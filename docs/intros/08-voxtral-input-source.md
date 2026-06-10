## How to read this chapter

This chapter has three independent parts; read each beside the code it describes.

- **Audio front end** (`voxtral_audio.c`). Start at `vox_mel_feed`, the entry the
  streaming runtime calls with new samples: it appends them to a buffer and calls
  `mel_compute_available`, where the per-frame *window -> DFT (Discrete Fourier
  Transform) -> mel -> log* loop
  lives. `build_mel_filters` (called once at init) precomputes the 128 triangular
  filters; `vox_mel_finish` flushes the final padded frames. The math behind that
  loop is the next section.
- **Weights** (`voxtral_safetensors.c`). All load-time, nothing per audio frame:
  the model loader calls `safetensors_open` (validate + mmap), then
  `safetensors_find` per tensor name, then either `safetensors_get_bf16_direct`
  (a zero-copy pointer into the mapping) or `safetensors_get_f32` (an allocated,
  converted copy).
- **Tokenizer** (`voxtral_tokenizer.c`). `vox_tokenizer_load` parses `tekken.json`
  into two string tables; `vox_tokenizer_decode` maps one token id back to its
  byte piece, called once per generated token.

## From waveform to log-Mel features

The model never sees raw audio. Capture delivers 16 kHz mono PCM; this front end
turns that one-dimensional signal into a two-dimensional **log-Mel spectrogram**
— a picture of how much energy sits at each pitch, frame by frame — because that
is exactly the representation Voxtral was trained on. Four stages produce it, and
every constant must match training, or recognition collapses even when the math
is individually "reasonable."

**1. Framing.** Speech is not stationary, but over ~25 ms a vowel essentially is.
The signal is cut into overlapping frames of `WIN_LENGTH = 400` samples (25 ms at
16 kHz), advanced by `HOP_LENGTH = 160` samples (10 ms). The hop sets the frame
rate: `16000 / 160 = 100` frames per second. Consecutive frames overlap by 240
samples, so no instant of speech falls in a gap.

**2. Windowing.** Each frame is multiplied by a periodic **Hann window**, a raised
cosine that tapers smoothly to zero at both ends. The Fourier transform assumes
its input repeats forever, so an untapered frame's abrupt edges would leak energy
across every frequency ("spectral leakage"). The taper makes the finite frame
look periodic.

**3. The Fourier transform (per frame).** Each windowed frame is moved from the
time domain to the frequency domain — that is, rewritten as a sum of sinusoids,
recording how much energy each frequency contributes. A Discrete Fourier Transform of
`N_FFT = 400` real samples yields `N_FREQ = N_FFT/2 + 1 = 201` bins spanning 0 Hz
to the 8 kHz Nyquist limit (half the sample rate, the highest frequency a
sampled signal can represent), about 40 Hz apart. The code computes this as a
**direct** DFT against precomputed cosine/sine tables rather than calling an FFT
library: at this size it is cheap, dependency-free, and reproduces the training
pipeline bit-for-bit. What it keeps is **power**, `|FFT|^2 = real^2 + imag^2` —
phase is discarded, because only *how much* energy lives at each frequency
matters for recognition.

**4. The Mel filter bank.** Pitch perception is roughly logarithmic: 200 Hz versus
300 Hz is obvious, 5000 Hz versus 5100 Hz is not. The 201 linear power bins are
projected onto `N_MEL = 128` **triangular filters** whose centers are evenly
spaced on the perceptual **Mel scale** (`hertz_to_mel`, the Slaney convention)
between 0 and 8000 Hz. Each filter rises to its center frequency and falls after,
and is area-normalized so the wide high-frequency filters do not drown out the
narrow low-frequency ones. `mel[m] = sum_k filter[m,k] * power[k]` collapses 201
numbers to 128.

**5. Log compression and normalization.** Loudness spans many orders of
magnitude, so each Mel energy is passed through `log10` and then normalized
exactly as Voxtral's training did: clamp to `[LOG_MEL_MAX - 8, LOG_MEL_MAX]` =
`[-6.5, 1.5]`, then rescale by `(val + 4) / 4`. The clamp floors silence and
ceilings clipping; the affine step recenters the values onto the distribution the
weights expect. **A log-mel that is mathematically equivalent but uses a different
clamp or scale will still mis-recognize**, because it moves the input off that
distribution.

The output is one `[frames, 128]` matrix. One last detail matches the reference
implementation (vLLM, an open-source inference engine used as the reference):
the **final STFT frame is dropped** (`stft[..., :-1]`), so
one second of audio yields 100 frames, not 101.

### Doing it incrementally

A live lecture cannot wait for the whole recording. The streaming front end keeps
a growing sample buffer and emits a Mel frame the instant its full 400-sample
window has arrived, leaving the unfinished tail for the next chunk. Two absolute
counters survive buffer compaction — `sample_offset` (leading samples discarded)
and `mel_frame_offset` (leading frames compacted away) — so a frame's logical
position is always recoverable even after old audio is freed (roughly every
second, `MEL_SAMPLE_COMPACT_MIN`). At `finish`, right-edge reflection padding
(mirroring the last samples) supplies the final windows so the last words are
not truncated.

## Safetensors as a model ABI

A safetensors file has:

1. an eight-byte little-endian header length;
2. a JSON object describing dtype, shape, and byte offsets;
3. a contiguous raw-data region.

Memory mapping avoids copying multi-gigabyte weights. This parser validates the
header length and JSON and checks every tensor's byte range against the mapping,
rejecting offset overflow and ranges that fall past the file. It does not check
for overlapping tensors or negative shape dimensions; an unsupported dtype is
carried as `DTYPE_UNKNOWN` and rejected later, when an accessor is asked to read
it.

BF16 direct access borrows mapped bytes. F32 conversion allocates a new buffer.
Those two accessors intentionally have different ownership and memory cost.

## Token bytes

Tokenizer pieces are byte strings, not guaranteed standalone Unicode strings.
A multi-byte UTF-8 character may span tokens. The queue accumulates pieces in
order; display code should operate on validated assembled text rather than
assuming one token equals one character or word.
