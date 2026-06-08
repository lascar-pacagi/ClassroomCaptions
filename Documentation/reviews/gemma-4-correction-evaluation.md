# Gemma 4 Caption Correction Evaluation

Evaluation dates: June 7-8, 2026.

## Decision

Both tested models are viable:

- **Gemma 4 26B-A4B** is the preferred high-quality desktop correction model on this machine.
- **Gemma 4 12B** remains the official-runtime fallback with the lower memory footprint.

Run either model through a persistent, loopback-only OpenAI-compatible server. Keep raw Voxtral captions visible immediately and replace a finalized segment only after Gemma returns a valid correction.

Do not put Gemma in the live audio critical path.

## Why Gemma 4 12B

Gemma 4 is Google's newest open-model family, released April 2, 2026. Gemma 4 12B was released June 3, 2026.

Relevant family members:

| Model | Architecture | Total parameters | Active parameters | Context |
| --- | --- | ---: | ---: | ---: |
| E4B | Dense with per-layer embeddings | 8B including embeddings | 4.5B effective | 128K |
| 12B | Dense unified | 11.95B | 11.95B | 256K |
| 26B-A4B | 128-expert MoE | 25.2B | 3.8B | 256K |
| 31B | Dense | 30.7B | 30.7B | 256K |

The 12B model is the best initial balance for this application:

- newest medium-size release;
- explicitly supported on Apple Silicon by Google;
- substantially stronger published multilingual and reasoning results than E4B;
- dense architecture with predictable behavior;
- official LiteRT-LM deployment artifact;
- less decode and memory cost than 31B;
- enough capacity for French/English technical vocabulary and conservative rewriting.

The 26B-A4B model has stronger published benchmark results and only 3.8B active parameters. It was tested through MLX after a recent PLE-aware mixed-precision artifact became available. Early uniform-quantized MoE builds had produced invalid output on some Apple GPUs, so every candidate artifact still requires direct output validation.

## Runtime Decision

Evaluated runtime: **LiteRT-LM 0.13.1**, released June 3, 2026.

Reasons:

- official Google runtime and optimized model package;
- macOS GPU support;
- Gemma 4 12B support added in 0.13;
- OpenAI-compatible `/v1/models` and `/v1/chat/completions` endpoints;
- Swift package now supports macOS, although its API remains early preview;
- compiled artifact caching;
- production separation between Voxtral's embedded C engine and Gemma.

MLX Python supports Gemma 4, but MLX Swift still had an open Gemma 4 architecture-support issue when reviewed. The first application integration should therefore use the local HTTP boundary. Native Swift embedding can be reconsidered after the relevant Swift APIs stabilize.

The server must bind to `127.0.0.1`, not `0.0.0.0`.

MLX-LM warns that its basic server is not recommended as a production server. For this application it should remain a loopback-only child process with no remote exposure. The application should supervise its lifecycle and communicate only through a narrowly scoped client.

## Installed Artifact

```text
Model ID: gemma-4-12b-correction
Source: litert-community/gemma-4-12B-it-litert-lm
Artifact: gemma-4-12B-it.litertlm
Disk size: 6.1 GB
Location: ~/.litert-lm/models/gemma-4-12b-correction/model.litertlm
```

The model is an optimized LiteRT package rather than the full BF16 checkpoint. This is appropriate for a secondary correction model: measured quality must decide whether a larger or less-quantized artifact is necessary.

### Gemma 4 26B-A4B

```text
Source: mlx-community/gemma-4-26B-A4B-it-OptiQ-4bit
Runtime: MLX-LM 0.31.3 / MLX 0.31.2
Artifact size: 17.7 GB
Resident/peak memory: approximately 17.8 GB
Precision: mixed 4-bit and 8-bit, PLE-aware
```

The model has 25.2B total and approximately 3.8B active parameters. The tested artifact uses higher precision for sensitive layers rather than uniform 4-bit quantization.

## Development Machine

```text
Apple M5 Max
40-core GPU
128 GB unified memory
macOS 26
```

Voxtral's official BF16 checkpoint remains loaded independently through the embedded Metal runtime.

## Measurements

### Synthetic GPU benchmark

Configuration:

```text
128 prefill tokens
64 decode tokens
512-token KV cache
GPU backend
disk compilation cache
```

Cold:

```text
Initialization:       6.392 s
Time to first token:  1.843 s
Prefill:             70.57 tokens/s
Decode:              34.59 tokens/s
```

Warm:

```text
Initialization:       6.302 s
Time to first token:  1.794 s
Prefill:             72.44 tokens/s
Decode:              37.53 tokens/s
```

The CLI creates a process and model instance for every invocation, so its initialization cost is unacceptable per caption. A persistent server is required.

### Actual correction prompts

Recorded French caption:

```text
Input:
Test du micro, test des sous-titres et test de l enregistrement pour pouvoir tester plus tard.

Output:
Test du micro, test des sous-titres et test de l'enregistrement pour pouvoir tester plus tard.

Wall time including standalone process startup: 3.30 s
```

Technical French:

```text
Input:
Aujourd hui nous allons regarder la complexité amortie des table de hachage et pourquoi une opération peut être en O de un en moyenne.

Output:
Aujourd'hui nous allons regarder la complexité amortie des tables de hachage et pourquoi une opération peut être en O(1) en moyenne.

Concurrent wall time: 4.30 s
```

Persistent server:

```text
First GPU request including engine initialization: 6.27 s
Next correction request:                         2.97 s
```

Warm output:

```text
Input:
On utilise un mutex pour protéger la section critiques entre les deux thread.

Output:
On utilise un mutex pour protéger la section critique entre les deux threads.
```

### Concurrent Voxtral impact

The 59.749-second Voxtral benchmark was run while Gemma corrected technical French.

```text
Previous Voxtral real-time factor:   0.2697
Concurrent Voxtral real-time factor: 0.2674
Previous first token:                0.339 s
Concurrent first token:              0.371 s
Word accuracy:                       96.41% in both cases
```

No meaningful throughput regression was observed. First-token movement was 32 ms in this single test and requires more samples before attribution.

## Gemma 4 26B-A4B Results

Thinking/reasoning output must be disabled with:

```json
{"enable_thinking": false}
```

Without this setting, the first test consumed the complete 80-token budget in a visible reasoning channel and did not return the correction.

### Standalone correction

Recorded French caption:

```text
Output:
Test du micro, test des sous-titres et test de l'enregistrement pour pouvoir tester plus tard.

Wall time: 2.84 s
Prompt: 166.4 tokens/s
Decode: 102.3 tokens/s
Peak memory: 17.8 GB
```

Technical complexity caption:

```text
Output:
Aujourd'hui nous allons regarder la complexité amortie des tables de hachage et pourquoi une opération peut être en O(1) en moyenne.

Wall time: 2.77 s
Decode: 87.8 tokens/s
```

Mutex caption:

```text
Output:
On utilise un mutex pour protéger la section critique entre les deux threads.

Wall time: 2.70 s
Decode: 106.9 tokens/s
```

### Persistent server

```text
Short correction 1: 0.63 s
Short correction 2: 0.47 s
Long correction:    1.97 s for 116 output tokens
```

The long technical passage correctly fixed French agreement, punctuation, `nœud`, `liste chaînée`, AVL/red-black tree terminology, hash-table terminology, and `O(1)` without adding information.

### Concurrent Voxtral impact

The 59.749-second Voxtral benchmark ran concurrently with the 116-token correction:

```text
Voxtral baseline real-time factor: 0.2697
Concurrent real-time factor:       0.2725
Baseline first token:              0.339 s
Concurrent first token:            0.549 s
Word accuracy:                     96.41% in both cases
```

Throughput changed by about 1%. The first-token increase was 210 ms in this single stress test. Corrections should therefore be serialized and started only for finalized segments. A backlog policy remains necessary during dense continuous speech.

## Model Comparison

| Property | Gemma 4 12B LiteRT | Gemma 4 26B-A4B MLX |
| --- | ---: | ---: |
| Artifact size | 6.1 GB | 17.7 GB |
| Resident/peak memory | about 7.8 GB published | 17.8 GB measured |
| Warm short correction | 2.97 s | 0.47-0.63 s |
| Long technical correction | not identically tested | 1.97 s, 116 tokens |
| Concurrent Voxtral RTF | 0.2674 | 0.2725 |
| Runtime provenance | Official Google | Official MLX runtime, community quant |
| Integration maturity | Better | Newer artifact/server path |

The speed difference is mostly a runtime and architecture comparison, not a pure model-size comparison. Nevertheless, it reflects the actual deployment choices available today.

On the M5 Max, 26B-A4B is not merely viable; it is faster for this correction workload and has ample memory headroom. It is the selected default subtitle-correction backend. The 12B LiteRT model remains available as a fallback and comparison backend.

## Correction Policy

The correction prompt should:

- correct only evident transcription, punctuation, agreement, and casing errors;
- normalize unambiguous spoken mathematical and programming notation, such as
  `O de n` to `O(n)` and `est égal à` to `=`;
- preserve language, meaning, oral style, names, numbers, code identifiers, and technical terms;
- never summarize or add facts;
- return only corrected text;
- disable thinking/reasoning output;
- use low-variance generation;
- impose a short output limit based on input length.

The application must reject a response when:

- it is empty;
- it contains control or reasoning markup;
- it is implausibly longer or shorter than the raw caption;
- it changes too many words without explicit user permission;
- the request exceeds its timeout.

On rejection or timeout, the immutable raw Voxtral caption remains visible.

## Integration Plan

1. Add a `CaptionCorrectionService` implementation for a local OpenAI-compatible endpoint.
2. Use MLX-LM 26B-A4B by default and retain LiteRT-LM 12B as a fallback.
3. Keep DeepSeek V4 Flash outside the caption application for a future local coding-agent project.
4. Warm the model before microphone capture or in parallel with Voxtral startup.
5. Queue finalized captions serially.
6. Include limited neighboring raw captions for context, without requesting a rewrite of neighboring text.
7. Apply corrections through the existing `queued -> correcting -> corrected/failed` state machine.
8. Preserve both raw and corrected text in session archives.
9. Measure queue depth and correction latency in the UI.
10. Add a backlog policy so Gemma cannot trail a lecture indefinitely.

## Sources

- [Google: Gemma 4 12B developer guide](https://developers.googleblog.com/gemma-4-12b-the-developer-guide/)
- [Google: Gemma 4 launch](https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/)
- [Google Gemma 4 12B model card](https://huggingface.co/google/gemma-4-12B)
- [LiteRT-LM repository and release information](https://github.com/google-ai-edge/LiteRT-LM)
- [Official LiteRT Gemma 4 12B package](https://huggingface.co/litert-community/gemma-4-12B-it-litert-lm)
- [MLX Swift Gemma 4 support issue](https://github.com/ml-explore/mlx-swift/issues/389)
- [MLX Gemma 4 collection](https://huggingface.co/collections/mlx-community/gemma-4)
- [Gemma 4 26B-A4B OptiQ artifact](https://huggingface.co/mlx-community/gemma-4-26B-A4B-it-OptiQ-4bit)
- [MLX-LM releases](https://github.com/ml-explore/mlx-lm/releases)
- [Early quantized Gemma 4 MoE correctness report](https://github.com/ml-explore/mlx/issues/3393)
