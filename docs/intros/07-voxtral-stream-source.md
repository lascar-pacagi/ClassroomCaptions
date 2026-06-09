## Model components

The local runtime loads several cooperating components:

- log-Mel audio front end;
- strided convolutional stem;
- audio transformer encoder;
- modality adapter projecting/grouping audio features;
- text decoder with autoregressive KV cache;
- tokenizer mapping token IDs to byte pieces;
- time/delay conditioning used by the realtime checkpoint.

Weights are immutable after load. Stream state is separate so one model context
could conceptually support multiple streams, although ClassroomCaptions uses
one serially owned stream.

## Stable incremental computation

Streaming cannot simply rerun the model on the entire lecture. Each stage keeps
the minimum state needed to extend prior computation:

- waveform tail for incomplete STFT windows;
- Mel-frame tail for causal convolution kernels;
- convolution/encoder position counters;
- encoder KV cache;
- unconsumed adapter features;
- decoder KV cache and current token;
- text pieces waiting for Swift to poll.

A position is exposed downstream only when future input cannot change it.
Stride alignment and causal receptive fields determine this stability.

## Delay conditioning

Realtime Voxtral conditions generation on a configured caption delay. The C
runtime builds a sinusoidal embedding from the delay value and feeds the
adapter/model tensors expected by the checkpoint. A smaller delay requests
earlier output but gives the model less future acoustic context; latency falls
while recognition stability may degrade.

## Continuous mode and recovery

The decoder has a finite text context. Continuous classroom use cannot allow
that context to grow for hours. At a boundary, the runtime can reset the
decoder's language and adapter counters (`gen_pos`, `total_adapter`,
`adapter_pos_offset`) while retaining the progressing audio timeline: the
fed-sample count, mel context, and encoder KV cache. A deeper recovery path
additionally rebuilds that audio front end after context exhaustion or unexpected
token behavior.

Resetting counters in the wrong domain would duplicate or skip audio. The code
therefore distinguishes full stream reset from decoder-only reset.

## Bridge semantics

The project-owned C bridge converts upstream conventions into:

- opaque handles;
- explicit status values;
- caller-provided error buffers;
- bounded text-buffer negotiation;
- monotonic sample/token/time counters;
- cancellation flag.

Swift never includes upstream private structs. This isolates the application
from layout changes and keeps all inference calls on one serial queue.
