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
