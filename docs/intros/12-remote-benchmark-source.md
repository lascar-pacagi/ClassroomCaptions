## Remote backend state

The WebSocket service has two asynchronous authorities:

- caller tasks invoking start/send/commit/stop;
- URLSession delegate callbacks reporting open, message, close, and error.

A lock protects the small connection-state record. Continuations bridge
delegate completion back to `async` callers and must be resumed exactly once.
The event stream remains the public output contract.

JSON protocols vary in field naming and nesting. The parser searches supported
keys in priority order, but it does not accept arbitrary strings as final
captions. Event type determines provisional/final semantics.

## Benchmark methodology

The CLI removes AppKit, microphone permissions, display refresh, and network
variables. It still uses the project C bridge, so it measures the same model,
stream options, token draining, and finish behavior as the application.

Important measurements are:

- model load and stream creation time;
- audio duration;
- first text latency;
- wall-clock inference time;
- the real-time factor (inference time divided by audio duration; below 1.0
  means faster than real time);
- transcript and optional reference word-accuracy comparison.

The CLI does not report decoder token counts or tokens-per-second; those
diagnostics exist only on the embedded in-app path.

Chunk size affects scheduling and apparent latency. A benchmark intended to
predict classroom behavior should feed chunks comparable to microphone callback
delivery, not one complete WAV buffer.
