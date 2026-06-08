# Voxtral Runtime Review

Date: 2026-06-07

## Summary

| Runtime | Precision | Integration | Dependencies | Maturity signal | Decision |
| --- | --- | --- | --- | --- | --- |
| Official vLLM | BF16 | Local server | NVIDIA/CUDA stack | Mistral production recommendation | Not usable on Apple GPU |
| Official Transformers | BF16 | Python process | PyTorch ecosystem | Official support | Correctness oracle |
| awni/voxmlx | BF16 or MLX conversion | Python API | Python, MLX, NumPy, tokenizer libs | Small, no tests found | Benchmark/reference |
| T0mSIlver/voxmlx | MLX formats | WebSocket server | voxmlx plus FastAPI/Uvicorn | Useful fixes, no tests found | Development fallback |
| antirez/voxtral.c | Official BF16, FP16 Metal execution | In-process C API | Apple system frameworks | Narrow tests, explicitly pre-production | Selected local base |

## Important Findings

### Official model

- Four-billion-parameter realtime speech-to-text model.
- Official checkpoint is BF16.
- Audio input is 16 kHz.
- Model delay is configurable in 80 ms token increments.
- Mistral officially recommends vLLM for production, but vLLM's practical deployment
  path is NVIDIA-oriented.
- Mistral lists both MLX and `voxtral.c` as community contributions and does not claim
  either is production-tested.

### voxmlx upstream

- Approximately 1,700 lines of Python.
- Clear model-layer decomposition and useful conversion tooling.
- Can load the original checkpoint or converted MLX weights.
- No automated tests were found in the reviewed repository.
- Latest inspected revision had only four commits by one primary author.
- Upstream incremental encoder cache used a very large fixed capacity instead of the
  model's configured 750-position sliding window.

### voxmlx server fork

- Approximately 500-line server addition.
- Adds a practical OpenAI-style protocol and several memory/performance corrections.
- Correctly changes encoder cache capacity to the configured sliding window.
- Server processes audio in the async WebSocket handler without an explicit bounded
  worker queue.
- No automated tests were found.
- Its non-final commit handling does not match the behavior our initial client assumed:
  non-final commits are no-ops because inference runs on every audio append.

### voxtral.c

- Approximately 15,500 lines including C, Objective-C, and Metal.
- Builds successfully with the MPS backend on the target M5 Max.
- Links only Apple/system frameworks in the resulting executable.
- Uses official BF16 safetensors and caches FP16 weights for GPU execution.
- Provides incremental encoder, rolling caches, silence flush, continuous recovery,
  and a C streaming API.
- Latest reviewed changes added stronger recovery for continuous stdin and bounded
  adapter state.
- Regression testing currently checks key phrases on one approximately 60-second
  Italian sample in batch and streaming modes.
- Upstream explicitly requests more long-stream and production testing.

## Current Project Impact

The existing `VoxtralRealtimeService` WebSocket client is retained temporarily for:

- comparison against voxmlx or vLLM;
- protocol integration tests;
- diagnosing embedded-engine output differences.

It will not be the default production backend. The dashboard will eventually offer:

- `Embedded Metal` as the default;
- `OpenAI-compatible WebSocket` as an advanced diagnostic backend.

## Next Implementation

1. Import the pinned `voxtral.c` source subset with license and attribution.
2. Create an opaque, project-owned C interface.
3. Compile the engine as a native target with Metal resources.
4. Add a serial Swift actor around model and stream ownership.
5. Download the official checkpoint and record hashes.
6. Run parity, accuracy, latency, memory, and sanitizer tests.
