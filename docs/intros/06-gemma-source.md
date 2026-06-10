## Process ownership and endpoint reuse

The controller distinguishes “the endpoint is healthy” from “this app owns a
child process.” A professor may start MLX-LM manually; in that case the app
reuses it and must not terminate it. When the app launches the process, it keeps
the `Process` reference and may stop that child during shutdown.

Health checks use a short-lived ephemeral URLSession and the OpenAI-compatible
`/v1/models` route. The 45-second deadline covers loading a large local model
without blocking the main thread; `await Task.sleep` suspends the task.

## Wire schema

`CompletionRequest` contains:

- model alias;
- ordered system/user messages;
- deterministic temperature (the sampling-randomness control; zero always
  picks the most likely token);
- bounded maximum output;
- non-streaming response choice.

The response decoder reads only fields used by the app. Unknown JSON fields are
ignored by `Decodable`, which makes the client tolerant of server metadata
additions without accepting a different semantic response shape.

## Prompt injection and capabilities

A prompt cannot make untrusted text cease to be adversarial. The design uses
three independent controls:

1. **No capability:** the model endpoint can return text but cannot call app
   methods, tools, shell, files, or network listener controls.
2. **Task framing:** system instructions and explicit data markers describe a
   correction-only transformation and prohibit answers/explanations.
3. **Deterministic validation:** Swift rejects reasoning markup, answer-shaped
   output, changed question form, excessive length change, and excessive word
   edits.

The third control is intentionally outside the model. A successful HTTP 200
means only that generation completed, not that the candidate is acceptable.

## Latency budgeting

Prompt context is bounded by the app model. Output budget scales with caption
character length and is clamped to `[48, 384]` tokens. Server prompt/decode
concurrency is one. These choices avoid competing 26B-model generations and
make the correction queue's latency easier to reason about.
