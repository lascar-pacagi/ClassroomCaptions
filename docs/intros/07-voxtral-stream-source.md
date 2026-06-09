## Model components

The local runtime loads several cooperating components:

- log-Mel audio front end;
- strided convolutional stem;
- audio transformer encoder;
- modality adapter projecting/grouping audio features;
- text decoder with autoregressive KV cache;
- tokenizer mapping token IDs to byte pieces;
- time/delay conditioning used by the realtime checkpoint.

Weights are immutable after load. Stream state is separate so one model context
could conceptually support multiple streams, although ClassroomCaptions uses
one serially owned stream.

## From PCM to tokens: the encoding pipeline

One chunk of microphone audio passes through five representations on its way to
text, each at its own rate. Keeping those rates straight is the key to reading
this file:

1. **Waveform — 16,000 Hz.** Signed PCM samples enter `vox_stream_feed`.
2. **Log-Mel frames — 100 Hz.** The front end (Chapter 8) turns each 400-sample
   window into a 128-bin Mel vector, one per 10 ms hop.
3. **Convolution positions — ~50 Hz.** A two-layer causal **convolutional stem**
   consumes Mel frames: `conv0` (kernel 3, stride 1, 128 -> 1280 channels) then
   `conv1` (kernel 3, **stride 2**, 1280 -> 1280), each followed by GELU. The
   stride-2 layer halves the time axis, so 100 Mel frames become ~50 convolution
   positions of width 1280. Because the convolutions are causal (left-padded) and
   run on chunks, the runtime keeps a Mel-frame tail and a one-position
   `conv0_residual`, so a chunk boundary yields exactly the outputs a
   whole-lecture pass would, and it discards the positions nearest a boundary that
   the zero padding would otherwise contaminate.
4. **Encoder positions — ~50 Hz.** The 32-layer audio transformer (Chapter 9)
   refines those 1280-d vectors with sliding-window self-attention, consuming only
   positions that later audio can no longer change.
5. **Adapter / decoder positions — 12.5 Hz.** The modality adapter concatenates
   every `VOX_DOWNSAMPLE = 4` consecutive encoder frames (1280 x 4 = 5120) and
   projects them into the decoder's 3072-d space, dropping the rate to 12.5 Hz.
   The 26-layer text decoder then attends over those audio embeddings and its own
   previous tokens to emit caption pieces autoregressively.

Every arrow is a **downsample with memory**: tail buffers and absolute counters
(samples -> Mel -> conv -> encoder -> adapter) make the streamed result identical
to a one-shot pass. A position is published only once no future input can revise
it, and that single rule is why each stage carries its own counter and tail.

## The numbers: shapes, rates, and a worked example

Every index calculation in these four chapters makes sense once the dimensions
are in front of you. The whole engine is governed by a handful of constants
(`voxtral.h`):

| Stage | Rate | Width per position | Governing constants |
| --- | --- | --- | --- |
| PCM samples | 16,000 Hz | 1 (scalar) | `VOX_SAMPLE_RATE 16000` |
| log-Mel frames | 100 Hz | 128 | `N_MEL 128`, `HOP_LENGTH 160`, `N_FFT 400` |
| convolution positions | ~50 Hz | 1280 | conv1 stride 2 |
| encoder positions | ~50 Hz | 1280 | `VOX_ENC_LAYERS 32`, 32 heads x `VOX_ENC_HEAD_DIM 64`, window `VOX_ENC_WINDOW 750` |
| adapter / decoder input | 12.5 Hz | 3072 | `VOX_DOWNSAMPLE 4` (1280 x 4 = 5120 -> 3072) |
| decoder hidden -> logits | 12.5 Hz | 3072 -> vocab | `VOX_DEC_LAYERS 26`, 32 query / 8 KV heads x `VOX_DEC_HEAD_DIM 128`, window `VOX_DEC_WINDOW 8192` |

**A worked example — two seconds of speech.** Follow one short utterance all the
way through:

- **32,000 samples** — two seconds at 16 kHz.
- **~200 Mel frames**, each a 128-vector. Hop 160 gives `32000 / 160 = 200`
  frames; the front end drops the last (`stft[..., :-1]`).
- **~100 convolution positions**, each 1280 wide. The conv stem's stride-2 layer
  halves the time axis (200 -> ~100).
- **~100 encoder positions** of 1280. The 32-layer encoder refines but does not
  resample.
- **~25 adapter embeddings** of 3072. The adapter concatenates groups of
  `VOX_DOWNSAMPLE = 4` encoder frames (4 x 1280 = 5120) and projects to 3072.
- **Up to ~25 caption tokens.** The decoder attends over those ~25 audio
  embeddings (plus its own prior text) and emits caption pieces at 12.5 Hz.

So two seconds of audio is 32,000 numbers at the microphone but only about 25
positions by the time the language model sees it — a reduction of more than a
thousandfold, which is what makes realtime decoding affordable. Keep this funnel
in mind: every "position", "row", and "frame" in the code is one step of it.

## Stable incremental computation

Streaming cannot simply rerun the model on the entire lecture. Each stage keeps
the minimum state needed to extend prior computation:

- waveform tail for incomplete STFT windows;
- Mel-frame tail for causal convolution kernels;
- convolution/encoder position counters;
- encoder KV cache;
- unconsumed adapter features;
- decoder KV cache and current token;
- text pieces waiting for Swift to poll.

A position is exposed downstream only when future input cannot change it.
Stride alignment and causal receptive fields determine this stability.

## Delay conditioning

Realtime Voxtral conditions generation on a configured caption delay. The C
runtime builds a sinusoidal embedding from the delay value and feeds the
adapter/model tensors expected by the checkpoint. A smaller delay requests
earlier output but gives the model less future acoustic context; latency falls
while recognition stability may degrade.

## Continuous mode and recovery

The decoder has a finite text context. Continuous classroom use cannot allow
that context to grow for hours. At a boundary, the runtime can reset the
decoder's language and adapter counters (`gen_pos`, `total_adapter`,
`adapter_pos_offset`) while retaining the progressing audio timeline: the
fed-sample count, mel context, and encoder KV cache. A deeper recovery path
additionally rebuilds that audio front end after context exhaustion or unexpected
token behavior.

Resetting counters in the wrong domain would duplicate or skip audio. The code
therefore distinguishes full stream reset from decoder-only reset.

## Bridge semantics

The project-owned C bridge converts upstream conventions into:

- opaque handles;
- explicit status values;
- caller-provided error buffers;
- bounded text-buffer negotiation;
- monotonic sample/token/time counters;
- cancellation flag.

Swift never includes upstream private structs. This isolates the application
from layout changes and keeps all inference calls on one serial queue.
