# ADR 0002: Embed a Locally Maintained Voxtral Engine

Status: Accepted

Date: 2026-06-07

## Decision

Use a reviewed, locally maintained derivative of `antirez/voxtral.c` as the primary
Voxtral Realtime inference engine on Apple Silicon.

The engine will:

- run in-process with the native macOS application;
- use the official Mistral BF16 checkpoint;
- convert/cache BF16 weights as FP16 for Metal execution;
- expose a narrow C API owned by this project;
- accept the application's existing 16 kHz mono PCM stream;
- return incremental token events directly to Swift;
- use one serial inference executor and one active transcription stream;
- require no Python runtime, local HTTP server, or WebSocket for normal operation.

`voxmlx` remains a reference and benchmark implementation. The T0mSIlver WebSocket
server fork remains an optional compatibility backend during development, not the
production accessibility path.

## Reviewed Revisions

- `antirez/voxtral.c`
  - revision: `134d366c24d20c64b614a3dcc8bda2a6922d077d`
  - latest commit date inspected: 2026-02-15
  - license: MIT
- `awni/voxmlx`
  - revision: `e6d193e85e84e30f26e370c66973ce287b8a9d57`
  - latest commit date inspected: 2026-02-08
  - license: MIT
- `T0mSIlver/voxmlx`
  - revision: `48bfdec9bc4f4f01390b25b0e098deae6dd3ae6c`
  - latest commit date inspected: 2026-02-27
  - license: MIT

Reviews used pinned local clones. Runtime installation from a moving Git branch is
rejected.

## Model Precision

The official `mistralai/Voxtral-Mini-4B-Realtime-2602` checkpoint stores BF16 weights.
It is not an FP16 checkpoint.

The chosen Metal path memory-maps the official BF16 safetensors and prepares FP16
weight buffers for GPU execution. This is a full 16-bit deployment, not 4-bit or
8-bit quantization. It meets the quality goal while fitting comfortably within the
M5 Max system's 128 GB unified memory.

The project will download only:

- `consolidated.safetensors`, approximately 8.9 GB;
- `tekken.json`, approximately 15 MB;
- `params.json`.

It will not download both duplicate weight files exposed by the Hugging Face model
repository.

## Why voxtral.c

### Native deployment

`voxtral.c` builds successfully on the target M5 Max with Apple Accelerate, Metal,
Metal Performance Shaders, Foundation, and system audio frameworks. The resulting
engine binary itself is small; model weights remain external application data.

No Python interpreter, package environment, FastAPI, Uvicorn, NumPy, MLX Python
bindings, `mistral-common`, or Hugging Face runtime library is required after model
download.

### Direct application integration

Its streaming API already exposes the needed conceptual operations:

- initialize a model and stream;
- feed float32 16 kHz audio;
- retrieve incremental decoded token strings;
- flush on silence without ending the stream;
- finish and release a stream;
- configure transcription delay and processing interval.

Direct C-to-Swift integration removes:

- Base64 audio expansion;
- JSON encoding and parsing;
- localhost network failure modes;
- WebSocket lifecycle coordination;
- a second microphone implementation;
- a separately managed server process.

### Full-precision model support

It reads the official BF16 safetensors directly and does not require an MLX-converted
or quantized model repository.

### Apple Silicon optimization

The inspected implementation contains:

- custom Metal kernels;
- fused decoder operations;
- FP16 KV cache support;
- rolling decoder KV cache;
- encoder sliding-window cache;
- chunked incremental encoder;
- cached BF16-to-FP16 GPU weight buffers;
- bounded mel and adapter buffers;
- continuous-stream recovery.

Published M3 Max measurements report faster-than-realtime operation. Those numbers
are not accepted as our benchmark results; they must be reproduced on the M5 Max.

### Auditability

The inference implementation is approximately 15,000 lines of C, Objective-C, and
Metal rather than a large transitive Python/runtime stack. This is still substantial,
but it is feasible to vendor, test, instrument, and maintain as part of this project.

## Why voxmlx Is Not Primary

Upstream `voxmlx` is compact and readable, and MLX is a strong Apple Silicon
framework. It is useful as an independent correctness oracle.

It is not selected as the primary runtime because:

- it introduces Python and several runtime dependencies;
- its repository contains no automated test suite;
- its upstream incremental encoder cache was configured far above the model's
  750-position sliding window;
- it requires either an MLX model conversion or loading through Python;
- process lifecycle and environment management would remain external to the app.

The official full-precision MLX conversion is a valid benchmark candidate. Memory is
not the reason for rejecting it.

## Why the T0mSIlver Server Fork Is Not Primary

The fork contains useful fixes:

- OpenAI Realtime-compatible WebSocket endpoint;
- Metal cache limit;
- explicit cache cleanup on disconnect;
- cached STFT matrices;
- materialization after concatenation;
- encoder cache corrected to the configured 750-position sliding window.

However, the server implementation has production-path weaknesses:

- no automated server tests;
- audio is Base64 encoded into JSON;
- inference runs synchronously inside the WebSocket receive handler;
- no explicit bounded input queue or backpressure contract;
- malformed Base64 and oversized messages are not rigorously constrained;
- non-final commit messages are intentionally ignored;
- model/session concurrency policy is not explicit;
- FastAPI/Uvicorn and Python environment health become accessibility dependencies.

Its protocol compatibility is convenient, but those costs are unnecessary when the
consumer is our own native application.

## voxtral.c Risks Requiring Local Work

The upstream README explicitly states that more testing is needed before production
use. We will not present upstream unchanged as classroom-ready.

Required changes before enabling it by default:

1. Replace public structs containing model internals with opaque handles.
2. Add structured error codes and caller-provided error messages.
3. Remove library writes to stdout/stderr; route diagnostics through callbacks.
4. Remove process-global verbosity flags.
5. Document and enforce single-threaded stream ownership.
6. Add cancellation checks between encoder and decoder work.
7. Add timestamps and token/event metadata.
8. Add deterministic reset and flush semantics for lecture pauses.
9. Audit all allocation failures and parser bounds.
10. Package Metal shaders reproducibly instead of relying on ad hoc generated headers.
11. Remove unused CLI and microphone code from the embedded library.
12. Decide whether `-ffast-math` is acceptable after numerical comparison.
13. Add long-session, multilingual, memory, and thermal tests.
14. Add AddressSanitizer and UndefinedBehaviorSanitizer test configurations.
15. Add model-file hashes and schema validation before loading.

The app will continue using its own Core Audio capture. The engine receives normalized
audio samples and never requests microphone permission itself.

## Local Source Ownership

The selected engine files will be copied into:

```text
Vendor/VoxtralEngine/
```

with:

- the original MIT license and attribution;
- `UPSTREAM.md` containing the reviewed revision;
- a patch/change log;
- no nested Git repository;
- no runtime download of source code;
- builds controlled by this project's Swift package and scripts.

Our stable wrapper will live in:

```text
Sources/CVoxtral/
Sources/ClassroomCaptions/VoxtralEmbeddedService.swift
```

Only the wrapper API is used by Swift application code. Internal upstream symbols are
not part of the application architecture.

## Validation Gate

The embedded engine becomes the default only after:

- official BF16 model download with recorded hashes;
- upstream sample regression tests pass;
- output is compared with official Transformers and MLX implementations;
- English and French classroom samples meet the agreed word-error threshold;
- first-token and steady-state latency are measured at several delay settings;
- a continuous two-hour stream completes without unbounded memory growth;
- pause/flush/restart behavior does not duplicate or lose transcript text;
- the app remains responsive while inference runs;
- sanitizers pass on parser, tokenizer, and streaming tests.

## Consequences

Benefits:

- smallest runtime and supply-chain surface;
- direct use of the official full 16-bit checkpoint;
- no local server to install or supervise;
- lower audio transport overhead;
- complete control over lifecycle, diagnostics, and recovery.

Costs:

- this project assumes responsibility for maintaining a nontrivial inference engine;
- Swift Package Manager integration with C, Objective-C, and Metal requires custom
  build work;
- correctness and long-session validation are mandatory;
- future Voxtral model revisions may require engine updates.
