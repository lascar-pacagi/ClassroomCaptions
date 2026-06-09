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

Encoder layers may use GELU depending on the component architecture. Exact
weight names and dimensions come from the checkpoint, not from generic
transformer convention.

## Rotary positions

RoPE rotates pairs of vector coordinates by position-dependent angles. It adds
relative-position structure without an additive embedding:

```text
(x_even, x_odd) -> rotation(theta(position, dimension))
```

Absolute positions must survive cache compaction. Reusing position zero after
moving cache bytes would make old and new tokens geometrically inconsistent.

## KV-cache economics

Without a cache, each generated token recomputes K and V for every previous
token. With a cache, one new row per layer is appended and attention reads
prior rows. Memory is approximately proportional to:

```text
layers * max_positions * kv_heads * head_dimension * 2(K,V) * bytes_per_value
```

FP16 cache storage halves bytes relative to FP32. The code includes capacity
growth, compaction, and fallback paths; every path must preserve row ordering.

## Numerical kernels

The scalar kernels are reference semantics and fallback. BLAS/Accelerate and
Metal provide throughput. Fused kernels reduce intermediate memory traffic, but
fusion must remain mathematically equivalent to the unfused residual,
normalization, projection, or activation sequence.
