## Metal object lifetime

The runtime initializes one `MTLDevice`, one command queue, one compiled shader
library, and a set of pipeline-state objects. Pipeline creation is expensive;
the code caches it by operation and shape-sensitive parameters.

A command buffer is a submission unit. Encoders append ordered operations.
`commit` makes work eligible for GPU execution. CPU code waits only when it
needs completed data or must safely reuse/free storage. Waiting after every
kernel would serialize CPU and GPU unnecessarily.

## Buffer ownership and storage modes

Weights are long-lived and frequently reused. Activations are short-lived and
benefit from pooling. Shared storage is visible to CPU and GPU on Apple silicon,
but visibility does not imply completion: command ordering still determines
when produced bytes are valid to read.

Caches in this file include:

- BF16-to-FP16 converted weights;
- merged/fused weight layouts;
- reusable activation buffers;
- cached `MPSMatrixMultiplication` objects;
- compiled custom shader pipelines.

Each cache needs a complete key and a shutdown path. A cache keyed only by a
pointer can become invalid if storage is freed and the address reused.

## Metal dispatch, concretely

If you have never written GPU code, the model is simpler than it looks. You write
one function — a **kernel** — that computes *one output element*, then ask the GPU
to run it across a **grid** of thousands of threads at once. Each thread is told
its own coordinate (`thread_position_in_grid`) and uses it to pick which element
it owns. Threads are organized into **threadgroups** that share a small, fast
scratch memory and can synchronize at a **barrier**; that is how cooperative
reductions (sums, maxes) are done.

Two kernels from this file make it concrete:

- **`silu` (elementwise).** Grid = one thread per array element. Thread `gid`
  computes `x[gid] = x[gid] / (1 + exp(-x[gid]))`, guarded by
  `if (gid >= n) return;` so an over-sized grid is harmless. A pure map.
- **`rms_norm` (one row per threadgroup).** Grid = one threadgroup per sequence
  position, 256 threads each. The 256 threads each sum part of the row's squares
  into shared memory; a tree reduction combines them; then each thread rescales
  its slice. The barrier is what lets the 256 threads agree on the row's norm
  before dividing.

Host and kernel must agree exactly on the layout — which buffer index holds which
tensor, the element type, the dimensions packed in the params struct, and the grid
size — because the GPU has no type checker across that boundary. That shared
contract is why the embedded shader source is documented as part of the ABI.

## Dispatch geometry

A Metal kernel receives a grid of threads grouped into threadgroups. Host code
and MSL must agree on:

- buffer index and element type;
- constant parameter layout/alignment;
- logical tensor dimensions;
- grid dimensions;
- bounds behavior for partial final groups.

The embedded shader header is therefore part of the C ABI between host and GPU,
even though both are compiled into one application.

## MPS and custom kernels

Metal Performance Shaders (`MPSMatrixMultiplication`) is appropriate for tuned
dense matrix products. Custom MSL is appropriate for project-specific fusion,
cache copies, rotary transforms, reductions, and layouts. The runtime chooses
between them based on operation shape and available optimized path. (It does not
use the higher-level MPSGraph framework.)

Objective-C is used because Metal's primary host API is Objective-C. Exported C
functions prevent Objective-C types from leaking into the rest of the C model
runtime.

## Why decode speed is memory bandwidth

A useful mental model for the whole file: generating one token requires
streaming essentially **every decoder weight** through the GPU's memory system
once. Per layer, the merged QKV projection reads about 38 MB of f16, the output
projection 25 MB, the merged gate/up FFN weights 113 MB, and the down projection
57 MB — roughly 233 MB per layer, about 6.1 GB across 26 layers, plus ~0.8 GB
for the final logits matmul against the tied token-embedding table. Call it
**~7 GB of weight reads per token**.

The arithmetic per token is tiny by GPU standards (one position, matvecs), so
the GPU's compute units are mostly waiting on memory. Tokens per second is
therefore approximately *memory bandwidth ÷ bytes per token*: at the ~12.5
tokens/s the realtime checkpoint targets, the runtime sustains on the order of
85 GB/s of weight traffic — comfortable for a Max-class Apple chip, tight for a
base one. This single fact explains most of the file's engineering: fusing a
whole token into one command buffer (no idle gaps between layers), keeping the
hidden state resident on the GPU, halving the KV cache with fp16, and merging
weight matrices so each is read in one contiguous pass. It also explains why
further speedups would come from weight quantization (fewer bytes per token),
not from faster arithmetic.

## How to read this chapter: one decode token on the GPU

The host counterpart of the decoder step in Chapter 9 is
`vox_metal_decoder_full_step`. It runs all 26 layers plus the final logits in a
**single command buffer** over a persistent on-GPU hidden-state buffer
(`g_dec_x`), so the 3072-vector never makes a CPU round trip between layers. Per
layer it encodes: the previous layer's output projection + FFN (fused), then
RMSNorm + a merged QKV matmul (`MPSMatrixMultiplication`), then one compute pass
doing RoPE on Q/K, the KV-cache write, and single-token attention
(`decoder_attention`, one threadgroup of 32 threads per head).
`memoryBarrierWithScope` orders those dependent passes. After the loop it appends
the final norm, the logits matmul, and `argmax_f32`, commits once, waits, and
returns the token id.

Read this against the CPU reference in Chapter 9: identical math, fused into far
fewer GPU submissions. The many `vox_metal_*` functions are specializations of
this one pattern — fused vs. separate, fp16 vs fp32 cache, encoder vs decoder.
