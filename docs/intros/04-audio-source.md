## Core Audio's element and scope model

AUHAL is an output Audio Unit used in an input configuration. Bus/element `1`
represents hardware input; element `0` represents output. Enabling input and
disabling output avoids opening an unnecessary playback path.

Audio Unit properties are addressed by:

- a selector identifying the property;
- a scope describing which side of the unit is observed;
- an element/bus number.

The same “stream format” property can therefore mean different formats at
different boundaries. The code reads the device-side input format and installs
that format on the callback-facing output scope before using
`AVAudioConverter` to produce the model's fixed format.

## The real-time render callback

`microphoneInputCallback` runs on Core Audio's **real-time thread** — a
high-priority thread with a hard deadline. The hardware hands over a buffer every
few milliseconds and expects the next one filled before it comes back around;
miss the deadline and the listener hears a click or a dropout. Real-time audio
programming therefore forbids, on this thread, anything that can block for an
unbounded or priority-inverted time: taking a lock another thread might hold,
waiting on I/O, or — ideally — even allocating memory. The rule is "do the
minimum, own your bytes, and get off the thread."

**Bridging a Swift object across a C function pointer.** The Audio Unit callback
is a plain C function pointer; it cannot capture Swift state the way a closure
can. The instance is smuggled through `Unmanaged`. At setup the service calls
`Unmanaged.passRetained(renderContext)` — handing ARC one extra owning reference —
and stores the resulting opaque pointer as the callback's `inputProcRefCon`. Each
invocation recovers it with `takeUnretainedValue()`, which performs **no** atomic
retain or release, so the audio thread never contends on ARC reference counts.
The single retain taken at setup is balanced by a release during teardown, after
callbacks have stopped.

**What the callback actually does.** It renders input with `AudioUnitRender`,
converts that buffer to the model's fixed 16 kHz mono format with
`AVAudioConverter`, and hands the resulting *owned* chunk to a serial
`DispatchQueue` with `queue.async`. Everything expensive — Voxtral inference, the
WAV write, level metering, SwiftUI updates — happens on that queue, off the
deadline. The callback never touches the model, sockets, files, the UI, or an
unbounded queue.

It is not perfectly real-time-safe — it allocates an `AVAudioPCMBuffer` and runs
the converter inline — but those costs are small and bounded. The next section
explains the trade and what a stricter design would cost.

## Why conversion leaves the callback

The current implementation performs render and format conversion in the
callback, then dispatches the resulting owned bytes. The callback still avoids
model inference, networking, files, UI, and unbounded queues. Conversion is a
bounded cost but remains the most timing-sensitive work in the application.

If profiling ever shows callback deadline misses, the next design would use a
preallocated lock-free/ring buffer and perform conversion on a dedicated
real-time-adjacent worker. That increases complexity: buffer overflow policy,
clock drift, and shutdown coordination become explicit.

## Sample representation

The model receives:

- one channel;
- 16,000 samples per second;
- signed 16-bit interleaved PCM;
- native-endian `Int16` inside the process.

The C bridge converts each integer to approximately `[-1, 1]` floating point.
An audio duration can be computed from byte count:

```text
seconds = bytes / (sample_rate * channels * bytes_per_sample)
        = bytes / (16000 * 1 * 2)
```

## Archive durability

WAV places sizes in its header, but those sizes are unknown while recording.
The archive writes a placeholder header, appends PCM incrementally, and seeks
back during finalization to write the actual byte count. A crash can therefore
leave a recoverable PCM payload with an incomplete header; orderly finalization
produces the standards-compatible file.

Transcript text and JSON are written only from finalized domain segments. The
archive does not serialize the unstable provisional hypothesis.
