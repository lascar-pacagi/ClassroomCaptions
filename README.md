# ClassroomCaptions

ClassroomCaptions is a local-first macOS application for live classroom
subtitles. It captures a selected microphone, transcribes speech with Voxtral
on the Mac, optionally proofreads finalized captions with Gemma, and displays
the result in a movable overlay. Captions can also be sent live to other devices
on the same local Wi-Fi network — students read them in a browser on their own
phone, tablet, or laptop, with no app to install — and they can submit anonymous
questions back.

The application was designed for a hearing-impaired computer-science professor,
but its architecture is useful anywhere private, low-latency, offline
captioning is preferable to a cloud service.

## Main Features

- Embedded full-precision Voxtral Realtime inference using Metal.
- Fast provisional subtitles followed by optional Gemma correction.
- Standard, science, and assistant correction modes; science mode favors Unicode
  mathematics, logic, set, probability, and programming notation.
- Assistant mode: ask the model a spoken, keyword-framed question and read its
  answer — with syntax-highlighted code and compiled LaTeX — in a dedicated,
  locked-down overlay card (no network, no tools, displayed never executed).
- Raw Voxtral text is retained when correction fails or is rejected.
- Movable and resizable overlay, independently placed on any connected display.
- Spoken commands to show, hide, or clear the overlay.
- Local recording with WAV audio and text/JSON transcripts.
- Live captions sent to students' own devices (phone, tablet, laptop) through a
  browser over trusted Wi-Fi — nothing to install on their side.
- Anonymous student question page with a professor-controlled moderation queue.
- Spoken commands to show the next question and dismiss the current question.
- Live token speed, transformation percentage, and memory diagnostics.
- No cloud transcription and no model access from the student page.

## Platform Requirements

The current application targets:

- Apple Silicon Mac;
- macOS 15 or later;
- Xcode Command Line Tools with Swift 6.2 or later;
- a Metal-capable Apple GPU;
- Python 3 and `uv` for the optional Gemma correction server;
- approximately 9 GB of disk space for Voxtral;
- additional memory and disk space if Gemma correction is enabled.

The embedded runtime is macOS-specific. The caption and question clients are
ordinary web pages and work on iPhone, iPad, Android, Windows, Linux,
Chromebook, and other devices with a current browser.

## Models and Memory

### Voxtral: required

The application uses
[`mistralai/Voxtral-Mini-4B-Realtime-2602`](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602).
The official BF16 checkpoint occupies about **8.3 GB** on disk. The vendored C
runtime converts tensors to FP16 for Metal execution. Mistral recommends at
least 16 GB of accelerator memory for the official checkpoint.

ClassroomCaptions intentionally uses the official checkpoint rather than a
4-bit transcription model because live transcription quality is the primary
accessibility function. Voxtral is required even when Gemma is disabled.

### Gemma: optional

The default corrector is
[`mlx-community/gemma-4-26B-A4B-it-OptiQ-4bit`](https://huggingface.co/mlx-community/gemma-4-26B-A4B-it-OptiQ-4bit).
It is a mixed-precision MLX quantization of Gemma 4 26B-A4B. On the development
machine it occupies about **16 GB** in the Hugging Face cache and approximately
**18 GB of resident memory** when serving corrections.

Gemma is outside the latency-critical audio path. Raw Voxtral captions appear
first; a finalized caption is replaced only after Gemma returns a validated
correction.

Suggested configurations:

| Unified memory | Configuration |
| --- | --- |
| 16 GB | Voxtral only; disable correction. This is the safest minimum. |
| 24-32 GB | Voxtral plus `mlx-community/gemma-4-e4b-it-4bit`; validate quality on your language and subject. |
| 32-48 GB | Voxtral plus `mlx-community/gemma-4-12B-it-4bit`; a stronger lower-memory alternative. |
| 64 GB or more | Default 26B-A4B OptiQ model. |

These are operational starting points, not hard guarantees. macOS unified
memory is shared by the application, models, display system, and other
programs. Test a full-length lecture before relying on a new model.

## Installation

### 1. Install developer tools

```bash
xcode-select --install
swift --version
```

### 2. Clone and enter the repository

```bash
git clone <repository-url>
cd ClassroomCaptions
```

### 3. Download Voxtral

```bash
python3 scripts/download_voxtral_model.py
```

The resumable downloader installs the three required model files under:

```text
~/Library/Application Support/ClassroomCaptions/models/Voxtral-Mini-4B-Realtime-2602
```

It also creates `model-manifest.json` with file sizes and SHA-256 hashes.

### 4. Install MLX-LM for Gemma

Skip this step if correction will remain disabled.

Install [`uv`](https://docs.astral.sh/uv/) and MLX-LM:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install mlx-lm
```

Confirm that the default executable exists:

```bash
~/.local/bin/mlx_lm.server --help
```

The model is downloaded automatically from Hugging Face the first time the
application starts the correction server. To pre-download and test it:

```bash
~/.local/bin/mlx_lm.chat \
  --model mlx-community/gemma-4-26B-A4B-it-OptiQ-4bit
```

Some gated model artifacts require accepting their license on Hugging Face and
running `huggingface-cli login`.

### 5. Build and test

```bash
swift test
./scripts/package_app.sh
```

The packaged application is written to:

```text
dist/ClassroomCaptions.app
```

## Launching

For normal use:

```bash
open dist/ClassroomCaptions.app
```

For development:

```bash
swift run ClassroomCaptions
```

The packaged app is preferred because its `Info.plist` contains the microphone
permission description expected by macOS.

On first launch, allow microphone access. If access was denied, open **System
Settings > Privacy & Security > Microphone** and enable ClassroomCaptions.

## Typical Classroom Scenario

1. Connect the projector or second display.
2. Launch ClassroomCaptions before students arrive.
3. Select the microphone and the display that should contain the overlay.
4. Leave the projector display selected only if students should see subtitles.
   Choose the private display if subtitles are for the professor only.
5. Keep **Embedded Metal** selected and verify the Voxtral model directory.
6. Enable Gemma correction and select **Science** mode for technical lectures.
7. Press **Start Session** and speak a short test sentence.
8. Move and resize the overlay, then check microphone level and model status.
9. Optionally press **Start iPhone Sharing** and scan the private caption QR.
10. Optionally enable anonymous questions and show the separate student QR.
11. During class, use the configured spoken commands:

| Default phrase | Action |
| --- | --- |
| `Bonjour soleil bleu` | Show the overlay |
| `Bonjour soleil rouge` | Hide the overlay |
| `Bonjour soleil blanc` | Clear visible captions without deleting the transcript |
| `Bonjour question suivante` | Show the oldest pending student question |
| `Bonjour question terminée` | Dismiss the current student question |
| `Bonjour modèle début` … `Bonjour modèle fin` | Frame a spoken question to the model (assistant mode) |
| `Bonjour réponse` | Show or hide the model answer |
| `Bonjour monter` / `Bonjour plonger` | Scroll the answer up / down |

12. Press **Stop Session** and wait for final correction and export to finish.
13. Open the session folder under `~/Documents/ClassroomCaptions`.

## Browser Sharing

The Mac acts as a small HTTP server on port `8765`. A QR code contains a URL
with a fresh 256-bit random token. The caption page uses Server-Sent Events to
receive updates. The student page uses a separate token and temporary,
source-bound tickets.

Any current browser on the same reachable Wi-Fi network can connect; it is not
limited to Apple devices. The current caption server intentionally allows one
simultaneous live caption stream. Many students may use the question page,
subject to rate and queue limits.

This transport is authenticated but **not encrypted**. Use a trusted classroom
network or a personal hotspot. Anyone who obtains a QR code or copied link can
use that capability until sharing is stopped. Stop sharing after class to
invalidate both links.

Student text is placed only in the moderation queue. It cannot invoke Gemma,
control the microphone, execute application commands, or modify captions.

## Recordings and Privacy

Recording is **disabled by default**: archiving a class is a consent decision.
Enable **Record sessions** in the Session Recording group before class if you
want an archive; the choice is remembered across launches. When recording is
enabled, each session contains:

- `audio.wav`: 16 kHz, signed 16-bit, mono PCM;
- `transcript.txt`: readable corrected transcript;
- `transcript.json`: raw and corrected segment data;
- `session.json`: session metadata.

The default directory is `~/Documents/ClassroomCaptions`. Spoken overlay
commands are removed from caption text before correction and export.

All speech recognition and correction are local. Browser sharing sends visible
caption text across the selected local network. Review institutional recording,
consent, accessibility, and data-retention requirements before recording a
class.

## Configuration Notes

- **Model delay** trades latency for acoustic context. The default 320 ms is a
  tested balance; noisy or distant rooms may benefit from a larger value.
- **Voxtral context** controls the decoder restart threshold, not the acoustic
  encoder window.
- **Gemma context** is the number of previous finalized captions quoted as
  untrusted reference data. More context can improve terminology but adds
  latency.
- **Science mode** performs aggressive notation formatting but is still
  forbidden from solving or answering captioned questions.
- **Assistant mode** corrects captions exactly like science mode and adds a
  separate path: a question you frame in speech between the start and end phrases
  is sent to the model, and its answer is rendered (code highlighting, LaTeX) in
  a dedicated overlay card. The model still only ever receives text and returns
  text — it is given no tools and no machine access, and its answer is displayed,
  never executed. The card has priority rules: a displayed student question hides
  it, and it returns once that question is dismissed.
- If Gemma fails, times out, or rewrites too much, the raw caption remains
  visible.

## Benchmarking

Use a 16 kHz mono PCM WAV file:

```bash
scripts/benchmark_voxtral.sh lecture.wav reference.txt
```

The benchmark reports load time, inference time, real-time factor, first-token
latency, transcript, and optional word accuracy.

## Development

```bash
swift test
swift build -c release
git diff --check
```

The principal source areas are:

```text
Sources/ClassroomCaptionsCore/       Domain model and validation
Sources/ClassroomCaptions/           SwiftUI/AppKit application
Sources/CVoxtralEngine/              Project C bridge and vendored engine
Tests/ClassroomCaptionsCoreTests/    Unit and integration tests
Documentation/                       Design notes and evaluations
docs/                                Quarto technical book
```

The detailed Quarto documentation explains the complete architecture, Swift
for C programmers, Voxtral internals, model correction, networking protocol,
security controls, QR encoding, testing, and reconstruction procedure.

## Known Boundaries

- The native application currently requires macOS and Apple Silicon.
- The browser transport is HTTP, not HTTPS.
- Only one browser caption stream is accepted at a time.
- There is no speaker diarization or word-level timestamp display.
- Model startup is substantial; start the app before the lecture.
- Long-duration classroom and adverse-network soak testing should be repeated
  after model, macOS, or compiler upgrades.

## License and Model Terms

The imported `voxtral.c` runtime is MIT licensed; its license and pinned
revision are preserved under `Vendor/VoxtralEngine`.

Model weights are not included in this repository. Voxtral, Gemma, and their
quantized artifacts have their own licenses and acceptable-use terms. Review
those terms before redistribution or institutional deployment.
