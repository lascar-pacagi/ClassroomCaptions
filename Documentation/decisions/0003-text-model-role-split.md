# ADR 0003: Separate Subtitle Correction from the Future Coding Agent

Status: Accepted

Date: 2026-06-08

## Decision

Use Gemma 4 26B-A4B through MLX-LM as the production target for correcting
finalized subtitles.

Retain DeepSeek V4 Flash and DS4 as an isolated research stack for a future
fully local coding agent comparable in workflow to Codex CLI or Claude Code.
DeepSeek is not part of the subtitle correction path.

The two systems must have separate:

- processes and model lifecycles;
- configuration and user controls;
- prompts and context stores;
- permissions and security policies;
- logs, traces, and evaluation corpora.

The caption application must never expose shell, file-editing, network, MCP, or
other coding-agent tools to a subtitle correction request.

## Subtitle Model

The selected correction model is:

```text
Gemma 4 26B-A4B
MLX OptiQ 4-bit artifact
Persistent loopback-only MLX-LM server
Thinking disabled
```

Measured reasons:

- 0.47-0.63 seconds for warm short corrections;
- 1.97 seconds for the long 116-token technical correction;
- 17.8 GB measured peak memory;
- good French computer-science terminology and conservative rewriting;
- negligible Voxtral throughput impact in the measured single-request overlap.

The 12B LiteRT model remains a fallback and comparison backend, not the default.

## Future Agent Model

The retained research model is:

```text
DeepSeek V4 Flash
DS4 asymmetric Q2 imatrix GGUF
80.76 GiB artifact
Pinned DS4 revision c463029c205c2ec8d7ab6c0df4a3f52979091286
```

The local evaluation showed that this model is fast enough for interactive
computer-science questions and agent experiments on the M5 Max. DS4 also has
the relevant foundations for long coding sessions: tool calling, live KV
reuse, disk KV checkpoints, OpenAI/Anthropic-compatible server APIs, and an
integrated coding-agent executable.

The future agent is a separate project phase. It requires its own threat model,
workspace sandbox, approval mechanism, tool protocol, patch application,
command execution, session persistence, and regression suite before it may
modify source code.

## Consequences

The current implementation sequence is:

1. Implement and validate the Gemma-backed `CaptionCorrectionService`.
2. Add correction queueing, timeout, validation, backlog, and archive behavior.
3. Complete the iPhone subtitle and professor-question surfaces.
4. Design the DeepSeek coding agent independently after the accessibility path
   is reliable.

Do not keep DeepSeek resident during normal classroom use. Its large Metal
mapping provides no benefit when Gemma owns subtitle correction.

The downloaded DeepSeek model and pinned DS4 review tree are retained locally
under the ignored `vendor-review/ds4` directory for later work.

## Evidence

- `Documentation/reviews/gemma-4-correction-evaluation.md`
- `Documentation/reviews/deepseek-v4-flash-evaluation.md`
- DS4 agent goals: <https://github.com/antirez/ds4/blob/main/AGENT.md>
- MLX-LM server: <https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md>
