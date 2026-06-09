## From waveform to log-Mel features

For windowed sample vector \(x[n]\), the front end applies a window function
and computes a discrete Fourier transform. Power is accumulated into
frequency-domain magnitudes, then projected through triangular Mel filters:

```text
mel_energy[m, t] = sum_k filter[m, k] * |FFT(windowed_frame[t])[k]|^2
```

The logarithm compresses dynamic range. Model-specific clipping/normalization
must match training exactly; a mathematically reasonable alternative can still
produce unusable recognition because it changes the checkpoint's input
distribution.

Incremental extraction retains samples that do not yet form a complete window.
At finish, right padding supplies the final windows. Frame offset records how
many earlier frames were compacted away.

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
