# Architecture

The repository is split into two targets.

## ClassroomCaptionsCore

Platform-neutral domain and service contracts:

- `CaptionTimeline` owns provisional and finalized caption state.
- `ClassroomSession` owns the long-running session lifecycle.
- `StreamingTranscriptionService` is the Voxtral boundary.
- `CaptionCorrectionService` is the Gemma 4 26B-A4B boundary.

Core does not import AppKit, SwiftUI, AVFoundation, or networking frameworks. This
keeps caption behavior deterministic and easy to test.

## ClassroomCaptions

Native macOS application:

- `ClassroomAppModel` coordinates UI state.
- `DashboardView` is the professor control surface.
- `CaptionOverlayController` owns a non-activating `NSPanel`.
- `CaptionOverlayView` renders finalized and provisional captions.
- `MicrophoneCaptureService` uses AUHAL to capture a selected input device without
  changing the system-wide default.
- `AudioDeviceCatalog` enumerates Core Audio input devices.

The development caption input drives the same domain path that Voxtral events will
use. It exists so overlay and timeline work can be tested before downloading models.

The overlay accepts mouse interaction without activating the application. Its
header moves the panel, its lower-right grip resizes it, and the resulting frame
is persisted independently for each display. Restored frames are clamped to the
current visible display area so monitor changes cannot strand the overlay
off-screen.

Spoken overlay commands are recognized in the application model before text
enters the caption timeline. Three independently configurable fixed phrases
default to `Bonjour soleil bleu` for show, `Bonjour soleil rouge` for hide, and
`Bonjour soleil blanc` to clear the currently displayed captions. The two-word
prefix gives Voxtral more acoustic context before the short color word and is
unlikely to occur in a computer-science lecture. Clearing creates a transcription
boundary and hides only existing overlay text; it does not remove segments from
Gemma correction, the timeline, or the session archive. This avoids
ordinary action words such as `affiche` and `masque`. Partial prefixes of the
command are suppressed from provisional
captions so a command does not flash in the overlay while Voxtral completes it.
Matching ignores case and accents and permits one transcription edit in long
words. Recognized command words are removed before Gemma correction and session
export. If Voxtral includes lecture text in the same finalized segment, only
the command span is removed. Cumulative provisional text may contain several
commands; they are executed once each in spoken order and all command spans are
removed before the segment reaches the timeline.

## Live Diagnostics

The optional diagnostics panel counts embedded Voxtral output at the token
boundary exposed by `ccv_stream_read_text`. It reports exact visible tokens
generated during the current session and average tokens per second.

Gemma reports prompt and completion token usage from the local MLX server
response. Completion speed and a character-level Levenshtein transformation
percentage are calculated after each validated correction. The percentage is
diagnostic only and does not influence caption acceptance.

When diagnostics are visible, the app samples resident memory once per second.
The app row includes embedded Voxtral because the model is loaded in the same
process. Gemma is measured separately from the loopback `mlx_lm.server`
process, and the panel also reports their combined resident size.

## Text Model Roles

The application uses one text model for subtitle correction:

- Gemma 4 26B-A4B runs behind a persistent loopback-only MLX-LM server.
- Only finalized Voxtral segments enter the correction queue.
- Thinking output is disabled.
- Requests are serialized, bounded, validated, and allowed to fail without
hiding the raw caption.

Gemma correction requests are stateless. The configurable context count selects
zero to eight previous finalized captions and quotes them as untrusted reference
data before the current target caption. The default remains zero, matching the
original behavior. Only the target caption may be returned.

Embedded Voxtral has two different rolling contexts. Its acoustic encoder keeps
the runtime's fixed 750-position window. Its decoder KV restart threshold is
configurable from 40 to 320 seconds, represented internally at 12.5 positions
per second. The default is 160 seconds, or 2,000 positions. This threshold is a
maximum: EOS and recovery safeguards may reset decoder context earlier.

DeepSeek V4 Flash is not an application backend. Its DS4 runtime and downloaded
weights are retained for a later, independent local coding-agent project. That
future agent will have a separate process, permission model, context store, and
tool-execution boundary. No coding-agent tools are reachable from caption
correction.

## Accessibility Invariant

Finalized raw text is immutable. Correction adds an optional `correctedText` value but
does not replace or destroy `rawText`. If correction fails, the raw caption remains
visible.

## Next Boundary

The next implementation increment adds the Gemma-backed
`CaptionCorrectionService`, including:

1. A persistent loopback-only MLX-LM process configuration.
2. Serialized correction of finalized captions.
3. Response validation, timeout, and raw-caption fallback.
4. Queue depth, latency, and model health indicators.
5. A backlog policy that prevents correction from trailing the lecture.
