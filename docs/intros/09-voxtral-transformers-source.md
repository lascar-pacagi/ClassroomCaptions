## A transformer layer, in plain terms

If transformers are not your daily work, here is the whole idea in code terms. A
layer maps a sequence of vectors (one per position) to another sequence of the
same shape, and the model stacks many such layers (32 in the encoder, 26 in the
decoder). Each layer does two things, each wrapped in a **residual** — the input
is added back to the output, so a layer only has to learn a *correction*:

1. **Attention — mixing across positions.** Each position emits a **query**, and
   every position a **key** and a **value** (three linear projections,
   `Q = X·Wq`, etc.). A position's new content is a weighted average of all
   positions' values, where the weight of position *j* for position *i* is how
   well *i*'s query matches *j*'s key: `softmax(Q·K^T / sqrt(head_dim))`. This is
   the *only* place information moves between positions. "Causal" masking forbids
   attending to the future; a "sliding window" also forbids attending too far
   into the past.
2. **Feed-forward (FFN) — mixing across features.** An independent two-layer MLP
   applied to each position on its own, here a gated **SwiGLU**:
   `SiLU(X·W_gate) * (X·W_up)`, then `· W_down`.

Around each, **RMSNorm** rescales a vector to unit root-mean-square so the numbers
stay in a stable range, and **RoPE** (above) injects position into the queries and
keys. That is the entire vocabulary of these two chapters: projections (matmuls),
normalization, an activation, attention, and a residual add — repeated, with the
exact dimensions taken from the checkpoint.

`Wq`, `Wk`, … are just matrices; multiplying by one is a **matmul**, the single
most expensive operation here. "BLAS" (Accelerate, on Apple) is the tuned library
for those matmuls; the scalar `vox_matmul` is the readable reference that the BLAS
and Metal paths must reproduce.

## Transformer equations mapped to the code

For input matrix \(X \in \mathbb{R}^{T \times d}\), RMS normalization is:

```text
rms(x) = sqrt(mean(x_i^2) + epsilon)
RMSNorm(x) = weight * x / rms(x)
```

Attention projects normalized input:

```text
Q = X Wq
K = X Wk
V = X Wv
Attention(Q,K,V) = softmax(Q K^T / sqrt(head_dim) + mask) V
```

The implementation reshapes projections into heads, applies RoPE to Q/K,
appends K/V rows to caches, computes attention, merges heads, applies output
projection, and adds the residual.

The feed-forward network uses a gated activation:

```text
hidden = SiLU(X W_gate) * (X W_up)
output = hidden W_down
```

Both the encoder and decoder feed-forward networks use this SwiGLU form (a SiLU
gate). GELU does not appear in the transformer blocks at all — only in the audio
conv stem and the modality adapter. The dimensions come from the checkpoint, not
from generic convention: the encoder is 1280-dimensional with 32 heads of size 64
(full multi-head attention) and a 5120-wide FFN; the decoder is 3072-dimensional
with 32 query heads but only 8 key/value heads (grouped-query attention — a 4:1
ratio that shrinks the KV cache fourfold) of size 128, and a 9216-wide FFN.

## Rotary position embeddings (RoPE)

Attention is **permutation-invariant**: `softmax(QK^T)V` returns the same result
if the tokens are shuffled, because it compares content, not order. Something must
inject position. Rather than *adding* a learned position vector, RoPE **rotates**
each query and key by an angle proportional to its position, so the geometry of
the dot product itself carries the order.

**The construction.** Split a head's vector into adjacent 2-D pairs
`(x0,x1), (x2,x3), ...`. Pair `d` is rotated by `angle = position * freq_d`, where
`freq_d = 1 / base^(2d / head_dim)` and `base = VOX_ROPE_THETA = 1,000,000`:

```text
x'[2d]   = x[2d]*cos(angle) - x[2d+1]*sin(angle)
x'[2d+1] = x[2d]*sin(angle) + x[2d+1]*cos(angle)
```

`vox_compute_rope_freqs` precomputes the `(cos, sin)` pair for every
(position, d); `vox_apply_rope` applies the 2x2 rotation in place. This is the
**interleaved (GPT-J) convention** — it pairs neighbouring coordinates `2d` and
`2d+1` — not the "rotate-half" GPT-NeoX layout that pairs coordinate `d` with
`d + head_dim/2`. Choosing the wrong pairing silently yields wrong logits.

**Why rotation encodes *relative* position.** If Q at position `m` and K at
position `n` are each rotated by their own angle, their dot product depends only
on the **difference** `m - n`: the rotations partially cancel, leaving `Q_m . K_n`
a function of distance rather than absolute index. The model learns "how far
apart" instead of "which slot," which is what lets it extend to lengths it never
saw during training.

**The frequency spectrum.** Because `freq_d` decays geometrically with `d`, the
first pairs spin quickly (sharp sensitivity to nearby tokens) while the last pairs
spin very slowly (coarse long-range position). The unusually large base, `1e6`,
slows every frequency, stretching the range over which positions stay unambiguous
to the long contexts a lecture needs. The encoder applies RoPE with
`head_dim = 64`, the decoder with `head_dim = 128`.

**The cache invariant.** RoPE is applied to K *before* it is appended to the KV
cache, so every cached key already carries its absolute angle baked in. Sliding-
window compaction must therefore `memmove` rows **and** advance a position offset,
never rewind position to zero — otherwise old and new keys would be rotated as
though they shared a slot and the attention geometry would silently break (see
`kv_cache_compact`).

## The decoder generation loop

The text decoder is **autoregressive**: it emits one token at a time, each
conditioned on the audio embeddings from the adapter and on every token already
emitted. The runtime runs it in two phases.

**Prefill.** When a caption prompt is ready, `vox_decoder_prefill` processes all
of its positions in a single batched pass, writing K and V rows for every prompt
position into the cache at once. This amortizes setup over the whole prompt
instead of paying it token by token.

**Decode.** Each subsequent token comes from one call to `vox_decoder_forward`:
one new embedding in, the 3072-d hidden state advanced through all 26 layers, and
a vocabulary logit vector out. The function takes the **greedy argmax** itself and
returns the chosen token id, so captioning is deterministic — there is no sampling
temperature. The full logits remain available for diagnostics.

Not every token is caption text. `stream_classify_token` sorts each id into
**text**, **control** (below the text-id range), **end-of-sequence**, or
**invalid** (a text-range id that decodes to an empty piece, such as Tekken token
1000 = byte 0x00). Control and EOS tokens drive caption boundaries; two watchdogs
guard against pathologies — a long run of non-text/control tokens, or a context
that grows past `max_decode_context` — and force a decoder restart so live
captioning never stalls or runs away.

## KV-cache economics

The cache is what makes autoregressive decoding affordable. Without it, producing
token *N* would recompute K and V for all *N − 1* earlier tokens at every step —
quadratic work. The cache stores each position's K and V **once per layer**, so a
step computes them only for the single new token and *reads* the rest. Per-step
cost falls from O(N) recomputation to O(1) new work plus an O(N) attention read.

Its size is the dominant memory cost of long-context decode:

```text
bytes ~= layers * positions * kv_heads * head_dim * 2(K,V) * bytes_per_value
       = 26    * positions * 8        * 128      * 2       * bytes_per_value
```

Note the **8**, not 32. This is **grouped-query attention**: the decoder has 32
query heads but only 8 key/value heads, each shared by a group of four query
heads. GQA is exactly a cache-size trade — it cuts the K/V the model must store
and re-read by 4x at a small quality cost, which is why long-context decoders use
it.

Three mechanisms keep that cost bounded and correct:

- **Sliding window.** The decoder attends to at most `VOX_DEC_WINDOW = 8192`
  recent positions. `kv_cache_compact` keeps the most recent 8192 K/V rows,
  `memmove`s them to position 0, and advances a position offset so RoPE angles
  stay consistent (the cache invariant above).
- **Precision.** The GPU path stores the cache in **FP16**, halving bytes and
  memory bandwidth; the scalar CPU fallback first converts it to FP32
  (`kv_cache_switch_to_fp32`) because its kernels read `float`.
- **Growth.** When more capacity is needed the cache doubles and re-packs every
  layer's rows across the new per-layer stride. Every path — grow, compact,
  precision switch — must preserve row ordering, or positions and their baked-in
  RoPE angles would desynchronize.

## How to read this chapter: one decoder step

To see the kernels working together, trace a single generated token through
`vox_decoder_forward` (`voxtral_decoder.c`). For each of the 26 layers, on the one
new position's 3072-vector:

1. `vox_rms_norm` -> a normalized copy.
2. `vox_linear_bf16` for the projections -> `Q` (32 heads x 128), `K`, `V`
   (8 heads x 128). The query/KV head-count difference is GQA.
3. `vox_apply_rope` on `Q` and `K` -> position baked in.
4. Append this position's `K` and `V` rows to the layer's KV cache.
5. `vox_causal_attention` -> the new position attends over all cached positions in
   the 8192 window, giving a 32 x 128 result; the output projection `W_o` brings
   it back to 3072; add the residual.
6. `vox_rms_norm` again, then the SwiGLU FFN (`vox_silu` on the gate, times the up
   projection, then the down projection); add the residual.

After the last layer, one more RMSNorm and a matmul against the tied token
embedding produce the vocabulary logits, and the function takes the greedy argmax.
Read `voxtral_kernels.c` as the verbs of this sentence and `voxtral_decoder.c` as
the sentence. The encoder (`voxtral_encoder.c`) is the same shape with biased
projections, full 32/32 heads, and no autoregressive cache growth.

## Numerical kernels

The scalar kernels are reference semantics and fallback. BLAS/Accelerate and
Metal provide throughput. Fused kernels reduce intermediate memory traffic, but
fusion must remain mathematically equivalent to the unfused residual,
normalization, projection, or activation sequence.
