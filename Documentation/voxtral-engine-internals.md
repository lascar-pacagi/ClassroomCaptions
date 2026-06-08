# Embedded Voxtral Engine

This document explains the embedded Voxtral runtime used by Classroom Captions, the upstream code it derives from, and the changes made to integrate it safely into the application.

## 1. Provenance and Scope

The engine is derived from antirez's `voxtral.c` repository at commit:

```text
134d366c24d20c64b614a3dcc8bda2a6922d077d
```

The imported source is MIT licensed. The upstream license is preserved at:

```text
Vendor/VoxtralEngine/LICENSE
```

Import details and the exact included files are recorded in:

```text
Vendor/VoxtralEngine/UPSTREAM.md
```

Only the inference runtime was imported. The upstream command-line interface, microphone program, examples, and build system are intentionally excluded. Classroom Captions owns the public bridge, lifecycle, audio capture, threading, error reporting, and user interface.

## 2. Why This Runtime Was Selected

Three implementations were reviewed:

- `antirez/voxtral.c`: compact C/Metal implementation with direct access to streaming state and kernels.
- `awni/voxmlx`: clear MLX implementation that is useful as a behavioral reference.
- `T0mSIlver/voxmlx`: server-oriented fork with WebSocket integration.

The C runtime was selected as the primary engine because it can be embedded in the native macOS process, avoids a Python server in the normal classroom path, and exposes the streaming lifecycle needed for low-latency captions. The WebSocket backend remains available as an advanced fallback and as an independent comparison path.

This project does not use a 4-bit model. It downloads the official BF16 checkpoint and the Metal runtime converts tensors to FP16 for execution and caching. This keeps model quality close to the published checkpoint while using hardware-native half-precision operations.

## 3. Model Architecture

Voxtral Mini Realtime is an audio-conditioned autoregressive language model. The runtime can be understood as five stages.

### 3.1 Audio frontend

The application supplies mono, signed 16-bit PCM at 16 kHz. The project bridge converts it to normalized floating-point samples in the range `[-1, 1]`.

The audio frontend:

1. Accumulates samples required by the analysis window.
2. Computes log-Mel spectral features.
3. Preserves overlap between calls so arbitrary audio chunk sizes are accepted.
4. Sends complete feature frames into the audio encoder.

The bridge reuses its conversion buffer rather than allocating a new floating-point array for every microphone callback.

### 3.2 Audio encoder

The imported model parameters describe a 32-layer audio transformer with model width 1280 and a local attention window of 750 positions. Convolutional layers initially transform and subsample the Mel features.

Streaming inference retains the convolution tails and encoder key/value state required by the next audio chunk. It therefore does not recompute the full lecture audio on every call.

### 3.3 Adapter and downsampling

The audio encoder output is projected into the text decoder representation. This adapter also reduces the temporal rate. Its output is inserted into the decoder context as audio-conditioned representations.

### 3.4 Text decoder

The text side is a 26-layer autoregressive transformer with:

- model width 3072;
- 32 query heads;
- 8 key/value heads;
- an 8192-token attention window.

The decoder retains its key/value cache across streaming calls. New text tokens are generated from the accumulated audio and decoder context instead of restarting decoding.

### 3.5 Delayed streaming

The realtime model uses delay tokens to control how far transcription trails incoming speech. One delay unit represents approximately 80 ms. Classroom Captions exposes this as a delay setting in milliseconds and converts it to the model's delay-token count.

A shorter delay can make words appear sooner but gives the model less future acoustic context. A longer delay generally improves stability at the cost of visible latency. The default should be selected through measurements on real classroom speech rather than by minimizing the number alone.

Classroom Captions defaults to 320 ms, or four delay tokens. The previous
480 ms default remains a useful fallback when distant speech, room noise, or
frequent provisional revisions make stability more important than 160 ms of
additional responsiveness.

On June 8, 2026, replaying the same 29.376-second archived command recording
produced identical final text at 320 ms and 480 ms. Their real-time factors were
0.2385 and 0.2402 respectively; first-token processing times were 1.213 and
1.187 seconds, a difference small enough to treat as run-to-run noise. Live
provisional stability remains the deciding classroom metric.

## 4. Streaming State

`vox_stream` is stateful. Its important categories of state are:

- incomplete PCM and Mel-analysis windows;
- convolution history;
- audio-encoder key/value caches;
- adapter/downsampling state;
- decoder key/value caches;
- generated token queue;
- count of real audio samples supplied;
- flushing and completion state.

The normal lifecycle is:

```text
create model
create stream
feed PCM chunks
read zero or more text fragments after each feed
flush at a speech boundary
continue feeding, or finish at end of session
destroy stream
destroy model
```

`flush` supplies the padding required to process the current tail. It is appropriate at a meaningful silence boundary. It should not be called after every small audio callback because doing so changes the effective acoustic context and adds unnecessary work.

`finish` performs the final flush and drains generation at the end of the session.

## 5. Metal Execution

The runtime uses Metal, Metal Performance Shaders, MPSGraph, and Accelerate. The package compiles the imported C and Objective-C sources directly into the application.

Important implementation details include:

- BF16 checkpoint tensors are converted to FP16 for Metal execution.
- Converted weights and compiled graph/kernel state are cached by the runtime.
- Attention, normalization, projection, convolution, and sampling operations use a mixture of MPSGraph and custom Metal kernels.
- The generated `voxtral_shaders_source.h` embeds the Metal shader source in the executable.
- Model loading includes allocation, checkpoint mapping, conversion, and initial graph/kernel preparation, so startup time must be measured separately from steady-state transcription.

Some caches in the upstream implementation are process-global. Classroom Captions consequently supports one active embedded model/stream lifecycle at a time.

## 6. Source Map

The imported runtime lives under `Sources/CVoxtralEngine/Engine`.

- `voxtral.c`, `voxtral.h`: model loading, stream lifecycle, orchestration, and generation.
- `audio.c`, `audio.h`: PCM processing and Mel feature extraction.
- `encoder.c`: streaming audio transformer.
- `decoder.c`: autoregressive text decoder and cache management.
- `kernels.c`, `kernels.h`: CPU-side kernel interfaces and tensor operations.
- `metal.m`, `metal.h`: Metal/MPS integration and device resources.
- `safetensors.c`, `safetensors.h`: checkpoint parsing and tensor lookup.
- `tokenizer.c`, `tokenizer.h`: Tekken tokenizer loading and token decoding.
- `voxtral_shaders_source.h`: generated embedded Metal shader source.

Project-owned integration files are:

- `Sources/CVoxtralEngine/include/ClassroomVoxtral.h`
- `Sources/CVoxtralEngine/ClassroomVoxtral.c`
- `Sources/ClassroomCaptions/VoxtralEmbeddedService.swift`

## 7. Project-Owned C Bridge

The application does not expose upstream structs to Swift. `ClassroomVoxtral.h` defines opaque model and stream handles and a small stable API.

The bridge adds:

- validation that `consolidated.safetensors`, `tekken.json`, and `params.json` exist;
- explicit Metal initialization and shutdown, with CPU fallback disabled for live captions;
- structured status codes rather than interpreting console output;
- conversion from interleaved PCM16 to the runtime's float input;
- reusable conversion storage;
- bounded token copying with a `BUFFER_TOO_SMALL` result;
- preservation of an unread token when the caller's output buffer is too small;
- explicit model and stream ownership;
- finish, flush, cancellation, and sample-count functions;
- read-only visible-token and decoder-time counters for live diagnostics;
- a bounded live decoder-context threshold configurable per stream;
- a function identifying the pinned upstream revision.

The bridge never returns a pointer owned by the tokenizer or decoder to Swift. Text is copied into caller-owned storage before crossing the language boundary.

### Ownership

Every successful `ccv_model_create` must be paired with `ccv_model_destroy`. Every successful `ccv_stream_create` must be paired with `ccv_stream_destroy` before destroying its model.

### Threading

The bridge does not claim that an individual stream is thread-safe. All operations for one model and stream are serialized by `VoxtralEmbeddedService`.

### Errors

Positive statuses indicate a normal non-error condition such as no text currently available or an output buffer that must be enlarged. Negative statuses represent failures. Swift converts these statuses into descriptive service errors and UI state.

## 8. Swift Service

`VoxtralEmbeddedService` confines model loading and inference to a dedicated serial dispatch queue. This has three purposes:

1. Metal inference never blocks the SwiftUI main actor.
2. Audio chunks remain ordered.
3. C stream state is never accessed concurrently.

The service publishes an `AsyncStream` of connection, provisional-caption, finalized-caption, and error events. Generated fragments are accumulated as provisional text. A flush converts the current provisional text into a finalized caption.

Before opening the microphone, the service feeds 3.2 seconds of silence into a newly created stream and discards any resulting text. The model requires roughly 3.12 seconds of audio-conditioned adapter tokens to build its initial decoder prompt. Priming that prompt with silence prevents the beginning of the lecturer's first sentence from being used as startup context. The microphone is opened only after priming completes, so no real audio is dropped during this operation.

The microphone callback itself remains short: it updates the level meter, copies the PCM chunk already produced by the audio subsystem, and submits the work to the inference queue.

## 9. Application Backend Selection

The default backend is **Embedded Voxtral**. Its model directory defaults to:

```text
~/Library/Application Support/ClassroomCaptions/models/Voxtral-Mini-4B-Realtime-2602
```

The advanced **WebSocket Voxtral** backend is retained for experiments, server isolation, and behavioral comparisons. Backend choice is latched when a session begins so changing a picker cannot split one session across two engines.

## 10. Differences From Upstream

The integration deliberately changes the packaging and control surface, not the model mathematics.

| Area | Classroom Captions change |
| --- | --- |
| Build | Swift Package target with explicit Metal, MPS, MPSGraph, Accelerate, and BLAS settings |
| Backend lifecycle | Bridge explicitly initializes Metal and rejects unintended CPU fallback |
| Source import | Runtime-only vendored subset pinned to an exact revision |
| Public API | Opaque project-owned C bridge instead of direct upstream structs |
| Input | Native PCM16 API with reusable conversion storage |
| Startup | 3.2-second silent decoder pre-roll before microphone capture |
| Output | Bounded copied UTF-8 fragments with recoverable buffer growth |
| Errors | Structured status values and Swift errors |
| Concurrency | One serial inference queue per service |
| Lifecycle | Explicit create/feed/flush/finish/cancel/destroy operations |
| Model storage | External application-support directory, never embedded in the app bundle |
| Traceability | Pinned revision and import manifest committed with the source |
| Fallback | Existing WebSocket implementation retained |

No quantization code has been added. No decoder, encoder, tokenizer, or sampling algorithm has been intentionally altered.

## 11. Model Download and Integrity

Run:

```bash
python3 scripts/download_voxtral_model.py
```

The downloader supports HTTP range resumption. It writes a manifest containing file sizes and SHA-256 hashes after the download completes. The files come from the official Mistral Hugging Face repository:

```text
mistralai/Voxtral-Mini-4B-Realtime-2602
```

The checkpoint is large. Keep it external to git and to the application bundle.

## 12. Benchmarking

The benchmark accepts a 16 kHz mono PCM16 WAV file:

```bash
scripts/benchmark_voxtral.sh speech.wav reference.txt
```

It reports:

- model load time;
- audio duration;
- inference wall-clock time;
- real-time factor, `inference time / audio duration`;
- first-token latency;
- complete transcript;
- word accuracy when a reference transcript is supplied.

A real-time factor below 1.0 means inference processes audio faster than it arrives. For live use, this is necessary but not sufficient. First-token latency, delay configuration, chunk size, thermal behavior, and caption stability also matter.

Quality measurements should include:

- quiet close-microphone speech;
- a lecturer at normal distance;
- student questions from different parts of the room;
- technical vocabulary, code identifiers, acronyms, and proper names;
- overlapping speech;
- projector or ventilation noise;
- French and English material if both are used.

Word accuracy is useful for repeatable comparison, but the practical classroom metric is whether the professor can follow the discussion with low effort. Save representative audio and references so engine revisions can be compared against the same corpus.

### 12.1 Baseline on the development machine

Measured on June 7, 2026, on an Apple M5 Max with a 40-core GPU and 128 GB unified memory, using the official checkpoint, 480 ms model delay, a 1.0-second processing interval, and 100 ms input chunks:

| Test | Model load | Inference | Real-time factor | First token | Word accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| 15.0 s clip, fed as fast as possible | 4.574 s | 3.864 s | 0.258 | 0.754 s computational | 69.4% |
| 59.749 s clip, fed as fast as possible | 4.249 s | 16.116 s | 0.270 | 0.339 s computational | 96.4% |
| 15.0 s clip, paced like a microphone | 4.404 s | 15.465 s wall clock | 1.031 including audio arrival | 2.725 s wall clock | 69.4% |

The short clip's reference and generated text differ near the end, which makes its word score unusually low despite an intelligible transcript. The longer clip is a more useful first quality indicator.

Before Metal was explicitly initialized by the project bridge, the runtime silently used CPU BLAS and took 78.803 seconds for the 15-second clip (`5.254x` real time). The untouched upstream CLI showed the same fallback behavior. This led to a project change: the bridge now owns Metal initialization and refuses an unintended CPU fallback.

## 13. Operational Sequence

At application startup no model is loaded. Starting a session performs:

1. Validate the model directory.
2. Load checkpoint and tokenizer on the inference queue.
3. Create a streaming decoder with the selected delay.
4. Start the selected microphone at 16 kHz mono PCM16.
5. Submit ordered audio chunks and publish available text.
6. Flush at speech boundaries.
7. Finish and drain the stream when the session stops.
8. Release stream and model resources.

Loading on demand avoids reserving several gigabytes of memory when captions are not being used.

## 14. Known Limitations and Hardening Work

The first embedded version has several explicit boundaries:

- An in-progress Metal operation cannot yet be interrupted midway; cancellation is observed between bridge calls.
- The upstream runtime still writes some diagnostics to standard error.
- Process-global Metal caches limit safe use to one active model instance.
- Generated text does not currently include word-level timestamps or speaker identity.
- Silence-boundary policy must be tuned against classroom recordings.
- Long-session memory and thermal behavior require an extended soak test.
- Address/undefined-behavior sanitizers should be run against the C bridge where compatible with Metal.
- The generated shader header should eventually have a documented regeneration command and reproducibility check.
- Compiler optimization choices, including any fast-math use, must be benchmarked for transcript equivalence before being changed.

These are integration risks to measure and improve; they are not reasons to move the primary path back to a Python server.

## 15. Verification Checklist

Before calling a runtime revision operational:

1. `swift test` passes.
2. A release build succeeds.
3. Missing or incomplete model directories return a structured error.
4. The official checkpoint loads.
5. Offline benchmark transcription is coherent.
6. Real-time factor and first-token latency are recorded.
7. At least one reference transcript is scored.
8. The packaged application starts and requests microphone permission.
9. Live microphone captions are tested for at least ten minutes.
10. Stop/start and microphone changes do not leak or crash.
