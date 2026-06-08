# Session Archives

Classroom Captions can record the microphone stream and export the corresponding caption timeline for later evaluation.

## Purpose

The archive provides a repeatable classroom corpus for:

- measuring Voxtral quality against human references;
- tuning model delay and silence segmentation;
- testing future Gemma correction;
- investigating words that were missed during a lecture;
- monitoring long-session behavior.

Recording is controlled by the **Session Recording** section in the application. The default destination is:

```text
~/Documents/ClassroomCaptions
```

Each session receives a directory named with its local start time and the first eight characters of its UUID.

## Files

### `audio.wav`

The microphone audio supplied to Voxtral:

- signed 16-bit PCM;
- little-endian;
- mono;
- 16 kHz;
- standard RIFF/WAVE header.

Audio is appended to disk on a dedicated serial queue. An hour requires approximately 115 MB, so the application does not retain the lecture in memory.

The WAV header is initially a placeholder. At session finalization, the writer seeks to the beginning and writes the final RIFF and data sizes.

### `transcript.txt`

A human-readable transcript:

```text
[00:01.250 - 00:03.500] Example caption text
```

Times are relative to the session start. Durations longer than one hour include an hour field.

### `transcript.json`

A structured transcript containing:

- sequence number;
- relative start and end times;
- immutable raw Voxtral text;
- optional corrected text;
- displayed text;
- correction state.

This is the preferred input for automated quality analysis.

### `session.json`

Session metadata:

- session UUID;
- absolute start and end times;
- selected transcription backend;
- microphone name;
- model delay;
- audio format;
- recorded byte count.

## Lifecycle and Ordering

The archive is created before microphone capture starts, preventing loss of the first audio callback.

When **Stop Session** is pressed:

1. Microphone capture stops.
2. The microphone processing queue drains, placing all captured audio before stop.
3. Pending audio writes finish on the archive queue.
4. Voxtral processes its queued audio and performs its final model flush.
5. Any delayed final text is added while the session is in the stopping phase.
6. The session receives its end timestamp.
7. The WAV header and transcript files are finalized.

The stop button displays **Exporting...** until this sequence completes. Starting another session during finalization is disabled.

## Privacy

The files remain local. Classroom Captions does not upload archives. Audio recording should still follow the institution's notice, consent, retention, and student-privacy requirements.

Delete archives through Finder according to the course retention policy. The application intentionally does not delete prior session directories when its current timeline is cleared.
