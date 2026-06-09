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
