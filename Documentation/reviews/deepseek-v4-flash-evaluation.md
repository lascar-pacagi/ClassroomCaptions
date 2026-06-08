# DeepSeek V4 Flash Local Evaluation

Date: 2026-06-08

## Decision

A full DeepSeek V4 Flash quantized model is fast enough to run locally on this
Apple M5 Max with 128 GB of unified memory.

The viable artifact is antirez's imatrix-tuned asymmetric Q2 GGUF, run with
DwarfStar (DS4). It is not small in the ordinary sense: the file is 80.76 GiB
and its Metal mapping spans 81.75 GiB. It nevertheless fits beside the embedded
Voxtral BF16 model and remains interactive.

Do not replace Gemma 4 26B-A4B as the default caption corrector yet:

- Gemma's warm short corrections take 0.47-0.63 seconds, versus 1.14-1.92
  seconds for DeepSeek.
- Gemma uses 17.8 GB in the measured configuration, versus an 81.75 GiB model
  mapping for DeepSeek.
- DeepSeek translated the long French test into English under the existing
  generic correction prompt. A stricter French prompt prevented translation,
  but still failed to normalize every spoken complexity notation.
- DeepSeek's direct answer to a computer-science question was strong. This is
  the better reason to retain it as an optional professor Q&A backend.

Recommended role split:

1. Voxtral remains the latency-critical transcription engine.
2. Gemma 4 26B-A4B remains the default finalized-caption corrector.
3. DeepSeek V4 Flash Q2 is an optional, mutually exclusive text backend for
   professor-initiated questions or difficult corrections.
4. Use DeepSeek non-thinking mode for overlaid answers. Thinking mode can spend
   the entire output budget without reaching a final answer.

## Upstream Sources

- Official model:
  <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash>
- DS4 runtime:
  <https://github.com/antirez/ds4>
- DS4 quantized weights:
  <https://huggingface.co/antirez/deepseek-v4-gguf>

Pinned DS4 revision:

```text
c463029c205c2ec8d7ab6c0df4a3f52979091286
2026-06-06 Style ds4-agent system status messages
```

DS4 is MIT licensed. Its README describes the project as beta quality.

## Model

Downloaded artifact:

```text
DeepSeek-V4-Flash-IQ2XXS-w2Q2K-AProjQ8-SExpQ8-OutQ8-chat-v2-imatrix.gguf
86,720,111,488 bytes
80.76 GiB
```

Inspected model structure:

```text
Logical parameters: 284.33B
Active parameters:   approximately 13B, per the official model card
Layers:              43
Experts:             256 total, 6 active
Context:             compressed-attention architecture, up to 1M officially
```

Tensor storage reported by DS4:

| Type | Tensors | Size |
| --- | ---: | ---: |
| F16 | 359 | 2.04 GiB |
| Q8_0 | 345 | 6.15 GiB |
| Q2_K | 43 | 28.22 GiB |
| IQ2_XXS | 86 | 44.34 GiB |

This is not uniform two-bit quantization. The large routed-expert tensors use
IQ2_XXS/Q2_K while shared experts, projections, routing-sensitive tensors, and
the output path retain higher precision.

The 98 GB Q2/Q4 hybrid may improve quality but leaves less memory headroom. It
was not downloaded because the 81 GB model already exposed correction-quality
and concurrency tradeoffs, and the larger artifact would be a worse default
for simultaneous Voxtral use.

## Runtime Validation

The Metal binaries built successfully with the Apple toolchain.

Model-independent tests:

```text
Q4_K tests:                       4/4 passed
Answer extractor self-tests:     passed
```

The model loaded successfully on:

```text
Apple M5 Max
128 GB unified memory
Metal 4 tensor path enabled
```

With the model installed, the complete upstream `make test` run passed:

```text
30,474-token long-context prefill: passed
Tool-call quality:                 passed
Official/logprob vectors:          passed
Local golden vectors:              passed
Metal short prefill:               passed
Metal kernel tests:                passed
Metal tensor equivalence:          passed
Server tests:                      passed
```

The optional SSD-streaming correctness test was not enabled because this
128 GB machine runs the Q2 model through full Metal residency.

Cold one-shot startup:

```text
Metal residency request: 8.415 s
Total wall time:         12.52 s
Prefill:                 88.24 tokens/s
Generation:              31.35 tokens/s
Swaps:                   0
```

The cold cost makes a process-per-caption design unacceptable. DS4 must run as
a persistent loopback-only server.

After the model was warm in the operating-system cache, server residency took
0.394 seconds. That number should not be treated as a guaranteed application
startup time after reboot.

## Correction Corpus

The reproducible inputs and common prompt are stored in the ignored review
directory:

```text
vendor-review/ds4/classroom-benchmark/
```

All tests disabled thinking and used deterministic generation.

### Short Captions

| Case | Result | Wall time |
| --- | --- | ---: |
| Recording | Correct | 1.920 s |
| Complexity | Correct | 1.676 s |
| Mutex | Correct | 1.139 s |

Example:

```text
Input:
Aujourd hui nous allons regarder la complexité amortie des table de hachage et pourquoi une opération peut être en O de un en moyenne.

Output:
Aujourd'hui, nous allons regarder la complexité amortie des tables de hachage et pourquoi une opération peut être en O(1) en moyenne.
```

Warm server generation was about 38-39 tokens/s.

### Long Technical Caption

With the same generic correction prompt used for model comparison, DeepSeek
translated the entire French passage into English. This violates the explicit
instruction to preserve the original language.

Wall time:

```text
4.847 s
```

A stronger French-only prompt prevented translation and correctly fixed
agreement, accents, `nœud`, `chaînée`, and `rouge-noir`.

Wall time:

```text
6.308 s
```

However, it retained `O de n` and `O de un` in several places instead of
normalizing them to `O(n)` and `O(1)`. The short complexity caption had
normalized `O de un` correctly. This inconsistency requires a larger regression
corpus and stricter output validation before DeepSeek can correct captions by
default.

## Professor Question

Direct, non-thinking question:

```text
Pourquoi la suppression dans un arbre AVL reste-t-elle en O(log n), même si
plusieurs rotations peuvent être nécessaires ?
```

DeepSeek returned a correct concise explanation in French in 4.913 seconds.
It correctly related the number of constant-time rotations to the O(log n)
height of the tree.

Thinking mode with a 256-token limit took 7.421 seconds, consumed the complete
budget, exposed draft-like reasoning as content, and did not reach a final
answer. For an overlay, use non-thinking mode unless a separate long-running
question view can represent incomplete reasoning safely.

## Voxtral Concurrency

Reference Voxtral benchmark:

```text
Audio:         59.749 s
Word accuracy: 96.41%
Baseline RTF:  0.2697
Baseline TTFT: 0.339 s
```

### DeepSeek Resident, Idle

```text
Voxtral RTF:   0.2818
Voxtral TTFT:  1.289 s
Word accuracy: 96.41%
Swap:          none observed
```

Throughput changed by about 4.5%. The first-token result is a single sample and
was substantially worse; startup and residency pressure need repeated trials.

### One Realistic Overlapping Correction

```text
DeepSeek correction: 6.407 s
Voxtral RTF:         0.2705
Voxtral TTFT:        0.524 s
Word accuracy:       96.41%
```

Voxtral throughput was effectively unchanged. First-token latency increased by
185 ms, close to the previously observed 210 ms increase with Gemma 26B.

### Continuous Saturation Test

Six long DeepSeek corrections were submitted continuously:

```text
DeepSeek requests during overlap: 8.94, 8.57, 8.59 s
DeepSeek requests after overlap:  6.50, 5.91, 5.92 s
Voxtral RTF:                      0.4209
Voxtral TTFT:                     0.555 s
Word accuracy:                    96.41%
```

Voxtral remained faster than real time, but this load is unsuitable as a normal
policy. DeepSeek requests must be serialized, and caption corrections must not
form an unbounded queue.

## Integration Consequences

DS4 offers a loopback-only OpenAI-compatible server with
`/v1/chat/completions`, so it can implement the same future
`CaptionCorrectionService` boundary as MLX-LM.

Use:

```json
{
  "model": "deepseek-chat",
  "thinking": {"type": "disabled"},
  "temperature": 0
}
```

Operational requirements:

- keep DS4 persistent while selected;
- bind to `127.0.0.1`;
- never put it in Voxtral's live audio path;
- serialize requests;
- cap output based on input length;
- reject translation, excessive rewriting, reasoning markup, and truncated
  responses;
- retain immutable raw Voxtral text on every failure;
- avoid keeping Gemma, DeepSeek, and Voxtral all resident unless a separate
  memory-pressure test proves that configuration useful;
- keep DeepSeek outside the subtitle application.

## Conclusion

Yes, there is a quantized full DeepSeek V4 Flash that is fast enough on this
machine. The best current candidate is the 80.76 GiB DS4 Q2-imatrix model.

It is technically viable and strong enough for local professor Q&A. It is not
currently the best caption-correction backend: Gemma is much smaller, faster
for short corrections, and behaved more consistently on the long French
corpus. Retain DS4 and the downloaded model for a later, independent local
coding-agent project with its own sandbox, approvals, tool execution, context
storage, and security model.
