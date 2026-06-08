# ClassroomCaptions

`ClassroomCaptions` is a local-first macOS application for accessible classroom
captioning. It is a separate product from the imported `localvoxtral` reference
project.

Current foundation:

- standalone Swift package and native SwiftUI application;
- explicit classroom session lifecycle;
- immutable raw caption segments with optional corrected text;
- movable, resizable per-display overlay with persisted geometry;
- configurable spoken commands to show or hide the overlay without adding the
  command to the transcript;
- backend protocols for streaming transcription and correction;
- unit-tested core domain model.
- embedded full-precision Voxtral transcription on Metal;
- serialized Gemma 4 26B-A4B correction with non-answering output validation;
- streamed WAV recording and timestamped text/JSON session archives.

Run during development:

```bash
swift run ClassroomCaptions
```

Package a local application bundle with the required microphone permission metadata:

```bash
./scripts/package_app.sh debug
open dist/ClassroomCaptions.app
```

Run tests:

```bash
swift test
```

Session archives default to `~/Documents/ClassroomCaptions`. See
`Documentation/session-archives.md` for the file formats and finalization lifecycle.
