#!/usr/bin/env python3
"""Generate complete-source subsystem chapters.

The generator uses lexical structure only to avoid cutting declarations and
functions in arbitrary places. It does not pretend that regular expressions
understand program semantics. Technical explanations live in chapter and file
guides written by a human. A byte-for-byte reconstruction check prevents the
book from silently dropping or rewriting source.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/generated"
INTROS = ROOT / "docs/intros"
TARGET_BLOCK_LINES = 95
HARD_BLOCK_LINES = 180


@dataclass(frozen=True)
class Chapter:
    slug: str
    title: str
    purpose: str
    position: str
    files: tuple[str, ...]


DOMAIN_CHAPTER_FILES = (
    "Sources/ClassroomCaptionsCore/ModelProtocols.swift",
    "Sources/ClassroomCaptionsCore/CaptionTimeline.swift",
    "Sources/ClassroomCaptionsCore/ClassroomSession.swift",
    "Sources/ClassroomCaptionsCore/CaptionCorrectionValidator.swift",
    "Sources/ClassroomCaptionsCore/CaptionTransformation.swift",
    "Sources/ClassroomCaptionsCore/AudioLevelMeter.swift",
    "Sources/ClassroomCaptionsCore/SessionExport.swift",
    "Sources/ClassroomCaptionsCore/SpokenOverlayCommand.swift",
)
# The domain (Core) files are documented byte-for-byte in a dedicated, more
# richly annotated chapter produced by generate_domain_chapter.py
# (docs/generated/02-domain-professional.qmd). They are intentionally NOT
# re-emitted here; the completeness check at the end treats them as covered.


CHAPTERS = (
    Chapter(
        "03-orchestration-source",
        "Application Orchestration: Complete Source",
        "`ClassroomAppModel` is the main-actor coordinator. It latches settings, "
        "starts services in a safe order, translates callbacks into domain mutations, "
        "queues corrections, publishes remote snapshots, and refreshes the overlay.",
        "This is the hub of the executable. Read it after the domain model and before "
        "individual services, because it shows why each service API exists.",
        (
            "Sources/ClassroomCaptions/ClassroomCaptionsApp.swift",
            "Sources/ClassroomCaptions/ClassroomAppModel.swift",
            "Sources/ClassroomCaptions/ProcessMemory.swift",
        ),
    ),
    Chapter(
        "04-audio-source",
        "Audio Capture and Archives: Complete Source",
        "This chapter follows samples from the selected Core Audio device through "
        "AUHAL, format conversion, the capture gate, Voxtral delivery, level metering, "
        "and optional WAV/session persistence.",
        "The real-time callback is the strictest timing boundary in the program. "
        "Everything after it must own its bytes and must not make AppKit or model "
        "lifetime decisions from the audio thread.",
        (
            "Sources/ClassroomCaptions/AudioDeviceCatalog.swift",
            "Sources/ClassroomCaptions/MicrophoneCaptureService.swift",
            "Sources/ClassroomCaptions/SessionArchiveService.swift",
        ),
    ),
    Chapter(
        "05-ui-source",
        "Dashboard and Overlay: Complete Source",
        "The dashboard is declarative SwiftUI. The caption overlay is an AppKit "
        "`NSPanel` hosting a SwiftUI view, with a transparent interaction layer for "
        "moving and resizing without stealing focus.",
        "The app model owns state; these files render it and convert user gestures "
        "into coordinator calls. QR rendering also lives here because it is a view of "
        "a capability URL supplied by the network server.",
        (
            "Sources/ClassroomCaptions/DashboardView.swift",
            "Sources/ClassroomCaptions/CaptionOverlayController.swift",
        ),
    ),
    Chapter(
        "06-gemma-source",
        "Gemma Correction Pipeline: Complete Source",
        "Gemma is an optional post-processor. One component owns the local MLX-LM "
        "process; another constructs a non-instructional correction request, parses "
        "the response, and returns token metrics.",
        "The live subtitle never waits for this chapter's pipeline. The deterministic "
        "validator in the domain chapter decides whether candidate text may be "
        "attached to the immutable raw caption.",
        (
            "Sources/ClassroomCaptions/GemmaServerController.swift",
            "Sources/ClassroomCaptions/GemmaCorrectionService.swift",
        ),
    ),
    Chapter(
        "07-voxtral-stream-source",
        "Voxtral Streaming Runtime: Model and Complete Source",
        "`voxtral.c` owns the long-lived model context and incremental stream. It "
        "turns newly arrived PCM into mel frames, stable convolution outputs, encoder "
        "positions, adapter embeddings, and autoregressive text tokens.",
        "The project-owned C bridge narrows this runtime to opaque handles and status "
        "codes. Swift then serializes all handle use on one inference queue.",
        (
            "Sources/CVoxtralEngine/include/ClassroomVoxtral.h",
            "Sources/CVoxtralEngine/ClassroomVoxtral.c",
            "Sources/ClassroomCaptions/VoxtralEmbeddedService.swift",
            "Sources/CVoxtralEngine/Engine/voxtral.h",
            "Sources/CVoxtralEngine/Engine/voxtral.c",
        ),
    ),
    Chapter(
        "08-voxtral-input-source",
        "Voxtral Input, Tokenizer, and Weights: Complete Source",
        "These files transform waveform samples into log-Mel features, map Tekken "
        "token IDs to UTF-8 pieces, and expose safetensors mappings without copying "
        "large BF16 arrays unnecessarily.",
        "They feed and describe the state consumed by the streaming runtime. Errors "
        "here usually appear as load failures, dimension mismatches, malformed WAV "
        "input, or invalid token text.",
        (
            "Sources/CVoxtralEngine/Engine/voxtral_audio.h",
            "Sources/CVoxtralEngine/Engine/voxtral_audio.c",
            "Sources/CVoxtralEngine/Engine/voxtral_tokenizer.h",
            "Sources/CVoxtralEngine/Engine/voxtral_tokenizer.c",
            "Sources/CVoxtralEngine/Engine/voxtral_safetensors.h",
            "Sources/CVoxtralEngine/Engine/voxtral_safetensors.c",
        ),
    ),
    Chapter(
        "09-voxtral-transformers-source",
        "Voxtral Encoder, Decoder, and Kernels: Complete Source",
        "The transformer implementation is separated into audio encoder, text "
        "decoder, and reusable numerical kernels. This chapter traces tensor shapes, "
        "KV-cache ownership, normalization, attention, feed-forward layers, and "
        "greedy token selection.",
        "The streaming orchestrator calls these primitives; Metal accelerates the "
        "expensive operations while scalar C remains useful for setup and fallback.",
        (
            "Sources/CVoxtralEngine/Engine/voxtral_encoder.c",
            "Sources/CVoxtralEngine/Engine/voxtral_decoder.c",
            "Sources/CVoxtralEngine/Engine/voxtral_kernels.h",
            "Sources/CVoxtralEngine/Engine/voxtral_kernels.c",
        ),
    ),
    Chapter(
        "10-metal-source",
        "Metal Runtime and Shaders: Complete Source",
        "This chapter contains the Objective-C Metal host layer, its public C API, "
        "and the complete embedded shader source. It explains how buffers, command "
        "queues, pipelines, MPS matrix-multiplication operations, and "
        "synchronization connect CPU orchestration to Apple GPU execution.",
        "All higher Voxtral layers depend on this implementation for throughput. "
        "Nothing in Swift calls it directly; the C runtime owns the GPU boundary.",
        (
            "Sources/CVoxtralEngine/Engine/voxtral_metal.h",
            "Sources/CVoxtralEngine/Engine/voxtral_metal.m",
            "Sources/CVoxtralEngine/Engine/voxtral_shaders_source.h",
        ),
    ),
    Chapter(
        "11-network-source",
        "Apple Networking, HTTP, SSE, Questions, and QR: Complete Source",
        "The Mac acts as a local TCP server through Network.framework. It implements "
        "the deliberately small HTTP subset needed by two generated browser clients: "
        "a read-only SSE caption viewer and an anonymous question form.",
        "The server receives immutable snapshots from the app model. It cannot "
        "control the microphone, models, overlay, or filesystem. The dashboard turns "
        "its capability URLs into QR images.",
        ("Sources/ClassroomCaptions/LocalCaptionServer.swift",),
    ),
    Chapter(
        "12-remote-benchmark-source",
        "Remote Voxtral Backend and Benchmark: Complete Source",
        "The WebSocket service is an alternative transcription backend. The benchmark "
        "is a command-line harness used to measure the embedded C runtime without UI, "
        "microphone permissions, or AppKit.",
        "Both implement or exercise the same transcription contract used by the app "
        "model, which makes backend comparison possible.",
        (
            "Sources/ClassroomCaptions/VoxtralRealtimeService.swift",
            "Sources/VoxtralBenchmark/main.swift",
        ),
    ),
    Chapter(
        "13-tests-source",
        "Tests: Complete Source",
        "Tests are executable specifications for state transitions, validation, "
        "commands, bridge behavior, server security, geometry, export, and metrics.",
        "Read each test beside the production chapter it exercises. The complete "
        "listing is included so reconstruction includes expected behavior, not only "
        "implementation.",
        tuple(
            str(path.relative_to(ROOT))
            for path in sorted((ROOT / "Tests").rglob("*.swift"))
        ),
    ),
    Chapter(
        "14-build-source",
        "Build, Models, Packaging, and Documentation: Complete Source",
        "The manifest defines modules, compiler flags, frameworks, and products. "
        "The remaining files download the model, run the benchmark, package the "
        "macOS bundle, declare permissions, and rebuild this book.",
        "These files turn the source tree into reproducible executables and explain "
        "environment assumptions that ordinary Swift code does not express.",
        (
            "Package.swift",
            "Resources/Info.plist",
            "scripts/download_voxtral_model.py",
            "scripts/benchmark_voxtral.sh",
            "scripts/package_app.sh",
            "scripts/build_book.sh",
        ),
    ),
)

GUIDES = {
    "02-domain-source": """
### Mental model

The core module is a deterministic state machine wrapped around an append-only
caption history. A provisional string is replaceable because Voxtral revises it
while decoding. A finalized segment is stable: its raw text never changes.
Gemma may later attach a correction, but it does not overwrite evidence.

```text
TranscriptionEvent
       |
       v
ClassroomSession ----phase----> starting/listening/paused/stopping
       |
       v
CaptionTimeline ----append----> CaptionSegment(rawText, correctedText?)
```

The chapter therefore proceeds from service contracts to timeline storage,
session transitions, candidate validation, metrics, export, and spoken command
recognition. This order mirrors dependency direction.
""",
    "03-orchestration-source": """
### Execution story

The coordinator is read as a set of workflows rather than as one 1,300-line
object: initialization wires callbacks; start waits for Voxtral before opening
the microphone; transcription events mutate the current value-type session;
finalized segments enter one serialized correction worker; every visible state
change refreshes overlay and remote snapshots; stop drains model output before
closing the archive.

The critical ownership rule is: UI state belongs to `@MainActor`, C inference
belongs to the Voxtral queue, Core Audio owns its callback deadline, and the
network server owns its own serial queue. The coordinator transfers values
between owners; it does not make those owners share mutable internals.

![Execution domains coordinated by the main-actor app model. Every arrow carries a value; mutable service internals stay with their owner.](../figures/orchestration-ownership.svg){#fig-orchestration-ownership width=96%}

### Swift concepts introduced here

`@main` identifies the program entry type. `@MainActor` isolates declarations
to Swift's main executor. `@Observable` asks the Observation framework to track
property reads and writes used by SwiftUI. `@State` gives a view persistent
framework-managed storage across repeated value reconstruction.

`Task { ... }` creates asynchronous work. `await` permits suspension; it does
not mean “run on a worker thread.” `[weak self]` captures an optional non-owning
reference in a closure to avoid a retain cycle. `some View` is an opaque return
type: the compiler knows one concrete view type while callers depend only on
its protocol conformance.
""",
    "04-audio-source": """
### Sample path and timing

The callback cannot await. Pointers supplied by Core Audio are valid only for
the callback, so bytes crossing the boundary must become owned storage.
Stopping reverses construction order and prevents callbacks from observing
partially destroyed resources.

![The real-time callback creates owned PCM data before dispatching ordinary work, and teardown stops callbacks before releasing context.](../figures/audio-callback-boundary.svg){#fig-audio-callback-boundary width=96%}

### Swift and C-interoperability concepts introduced here

`@preconcurrency import` imports an older framework while suppressing
concurrency assumptions its declarations cannot yet express.
`@unchecked Sendable` is a promise made by this project: the compiler cannot
verify safety, so documented lock and queue ownership must enforce it.

`@escaping` means a closure may outlive the function call. `@Sendable` requires
captures suitable for transfer across concurrency domains. `Unmanaged<T>`
exposes explicit retain/release operations needed when a C callback stores an
opaque Swift object pointer. `deinit` is Swift's finalizer under Automatic
Reference Counting (ARC).
""",
    "05-ui-source": """
### Two UI systems, one state owner

SwiftUI is used where ordinary controls and observation are sufficient. AppKit
is used where the application needs a borderless non-activating panel, explicit
screen placement, window levels, Spaces behavior, and low-level dragging.
`NSHostingView` is the bridge: AppKit owns the window; SwiftUI describes its
caption content.

### SwiftUI concepts introduced here

A `View` is a value description with a `body`, not a persistent widget.
`@ViewBuilder` is a result builder that transforms declarative child
expressions and control flow into one composite view type. A `Binding<T>` is a
pair of get/set operations presented as mutable state to a control.

Property wrappers use `@Name` syntax to let a framework synthesize storage or
access behavior. View modifiers return new values; a chain such as
`.font(...).padding(...)` does not mutate an existing view object.
""",
    "06-gemma-source": """
### Safety and latency contract

The correction model receives quoted caption data and has no tool interface.
Requests are serialized because parallel 26B-model generations would increase
latency and memory pressure. Failure, timeout, malformed JSON, or rejected text
leaves the raw caption visible. This is a refinement path, never an
accessibility dependency.

![Gemma can produce only a candidate string. Capability absence and deterministic validation decide whether that string affects display.](../figures/gemma-security-pipeline.svg){#fig-gemma-security-pipeline width=96%}

### Swift concepts introduced here

An `actor` is a reference type whose mutable state is isolated; calls from
outside may require `await`. `Codable` combines `Encodable` and `Decodable`.
Nested `CodingKeys` map Swift property names to wire-format JSON keys.

`if let` and `guard let` perform optional binding: they unwrap an `Optional`
only on the branch where a value exists. `do`/`catch` handles thrown errors,
and `try`/`await` mark calls that may fail or suspend.
""",
    "07-voxtral-stream-source": """
### Five clocks inside one stream

Keep these units separate while reading: 16 kHz PCM samples, 100 Hz mel frames,
roughly 50 Hz post-convolution positions, grouped encoder positions, and 12.5 Hz
adapter/decoder positions. Tail buffers and absolute counters make chunked
execution equivalent to one continuous input.

The source order follows lifetime: context load, stream state, incremental
front end, encoder/adapter, decoder, public feed/get/flush operations, and
destruction. The Swift service appears beside the C code because queue ownership
is part of the runtime's correctness.

![The streaming runtime keeps separate counters for samples, Mel frames, convolution positions, encoder positions, and decoder positions.](../figures/voxtral-time-domains.svg){#fig-voxtral-time-domains width=97%}

PCM means Pulse-Code Modulation. A Mel spectrogram is a short-time spectral
representation whose frequency bins follow a perceptual Mel scale. KV means
key-value attention cache. BF16 means bfloat16, a 16-bit format retaining the
8-bit exponent width of IEEE-754 float. FP16 is IEEE half precision; the two
formats are not interchangeable.
""",
    "08-voxtral-input-source": """
### Boundary formats

Audio code establishes the exact numerical representation entering the model.
Safetensors code establishes tensor names, shapes, dtypes, mapped ownership, and
bounds. Tokenizer code establishes the mapping between decoder IDs and bytes.
These are not peripheral parsers: they define the model ABI on disk.

ABI means Application Binary Interface. FFT means Fast Fourier Transform.
STFT means Short-Time Fourier Transform. `mmap` maps file-backed virtual memory
into the process. UTF-8 means Unicode Transformation Format, 8-bit form.

For every returned pointer, determine ownership: borrowed mapped bytes, newly
allocated converted values, or internal context storage. C's type system does
not encode those lifetime distinctions.

![The input subsystem deliberately distinguishes copied stream storage, borrowed mapped bytes, and caller-owned converted buffers.](../figures/voxtral-input-ownership.svg){#fig-voxtral-input-ownership width=96%}
""",
    "09-voxtral-transformers-source": """
### Tensor computation hierarchy

Kernels implement matrix operations, normalization, activations, convolution,
and attention primitives. Encoder and decoder layers compose them while owning
their distinct KV caches and dimensions. Read every allocation together with
its shape and every cache position together with its unit.

BLAS means Basic Linear Algebra Subprograms. GELU means Gaussian Error Linear
Unit. SiLU means Sigmoid Linear Unit. RoPE means Rotary Position Embedding.
RMSNorm means Root Mean Square Layer Normalization.

Shape errors compile successfully in C and usually become memory corruption or
plausible but incorrect logits rather than a useful type error.

![A transformer layer appends only the new K/V rows, then attention reuses the complete retained cache before the residual feed-forward path.](../figures/transformer-cache-flow.svg){#fig-transformer-cache-flow width=96%}
""",
    "10-metal-source": """
### CPU/GPU division

The CPU validates dimensions, chooses a cached pipeline, fills small parameter
structures, encodes work, and decides when completion is required. Metal
buffers contain large tensors; command buffers order GPU operations; pipeline
state objects are compiled shader entry points. Metal Performance Shaders (MPS)
provide a tuned dense matrix multiply (`MPSMatrixMultiplication`) where a custom
kernel is unnecessary.

![The C transformer calls an Objective-C host runtime, which owns Metal pipelines, MPS operations, command ordering, and GPU buffers.](../figures/metal-runtime-stack.svg){#fig-metal-runtime-stack width=93%}

Metal Shading Language (MSL) defines GPU kernels. Metal Performance Shaders
(MPS) provide Apple-tuned primitives; this runtime uses `MPSMatrixMultiplication`
for dense matrix products and its own MSL kernels for everything else. (It does
not use the higher-level MPSGraph framework.)
`MTLBuffer` is a GPU-visible byte allocation; `MTLCommandBuffer` orders encoded
work. Objective-C Automatic Reference Counting manages Objective-C objects,
while raw C allocations still require explicit ownership.
""",
    "11-network-source": """
### Source reading order

The file starts with wire-visible value types and security constants. It then
defines queue-owned server state, listener lifecycle, incremental request
framing, routing, student tickets, rate limiting, SSE, HTTP response
construction, interface discovery, and finally the two complete browser pages.
The embedded HTML, CSS, and JavaScript are part of the protocol and are
therefore included, not summarized.

![Pairing transfers a capability URL visually; ordinary TCP, HTTP, SSE, and POST requests carry captions and questions.](../figures/network-request-flow.svg){#fig-network-request-flow width=96%}

TCP means Transmission Control Protocol. HTTP means Hypertext Transfer
Protocol. SSE means Server-Sent Events. URL means Uniform Resource Locator. QR
means Quick Response. `NWListener` and `NWConnection` are Network.framework
state machines; TCP itself does not preserve HTTP message boundaries.
""",
    "12-remote-benchmark-source": """
### Two consumers of one contract

The WebSocket implementation translates a remote JSON protocol into the same
`TranscriptionEvent` values emitted by the embedded service. The benchmark
calls the C ABI directly and reports model-load time, audio duration, inference
time, real-time factor, first-token latency, the transcript, and optional word
accuracy, isolating inference from UI and microphone variables.

WebSocket upgrades one HTTP connection to a bidirectional framed transport.
Base64 converts arbitrary bytes to printable ASCII at a 4/3 size expansion.
Word Error Rate (WER) is based on word insertions, deletions, and substitutions;
the benchmark reports a related normalized accuracy for practical comparison.
""",
    "13-tests-source": """
### Tests as behavioral documentation

Each test arranges an explicit state, performs one transition or boundary
operation, and checks the externally observable result. They reveal intended
semantics where implementation details alone could be ambiguous, especially
for voice-command tolerance, correction rejection, overlay geometry, HTTP
security, and pause behavior.

XCTest is Apple's unit-test framework. A test method is ordinary Swift code
whose assertions record failures without changing production behavior.
`async throws` tests can await asynchronous APIs and propagate unexpected
errors. Loopback sockets exercise the actual HTTP framing and authorization
logic without exposing the server beyond the local test process.
""",
    "14-build-source": """
### Build graph

Swift Package Manager compiles the C/Objective-C target with Accelerate and
Metal frameworks, then links it into the GUI executable and benchmark. The
packaging script creates a conventional `.app` directory and copies the
executable and `Info.plist`. Model weights remain external because they are
large and independently replaceable.

Swift Package Manager (SPM) evaluates `Package.swift` as Swift code. A target is
a compilation unit; a product is what clients build or link. `Info.plist` is
the bundle property list consumed by macOS. The shell scripts use `set -eu` so
an error or unset variable terminates packaging instead of silently producing
a partial application.
""",
}


OVERVIEWS = {
    "LocalCaptionServer.swift": (
        "One serial queue owns listener, connections, credentials, tickets, rate "
        "windows, snapshot, and heartbeat. Public methods enqueue work; every "
        "Network.framework callback is delivered back onto the same queue."
    ),
    "ClassroomAppModel.swift": (
        "This large coordinator is intentionally read by workflow: initialization, "
        "session lifecycle, transcription events, correction worker, overlay commands, "
        "sharing, questions, and diagnostics."
    ),
    "voxtral.c": (
        "Track five counter domains separately: PCM samples, mel frames, convolution "
        "positions, encoder positions, and adapter/decoder positions. Most subtle "
        "streaming bugs are unit or compaction mistakes between these domains."
    ),
    "voxtral_metal.m": (
        "The host layer caches Metal objects and pipeline state, allocates shared "
        "buffers, dispatches kernels, and waits only where CPU code needs completed "
        "results. Objective-C ownership and C-visible handles coexist in this file."
    ),
    "DashboardView.swift": (
        "View properties are descriptions, not persistent widgets. Side effects are "
        "delegated to the app model. The QR helper is pure rendering from URL bytes."
    ),
}

FILE_GUIDES = {
    "ClassroomCaptionsApp.swift": """
SwiftUI's `App` protocol is the process-level composition root. The
`@State` wrapper gives the scene one persistent `ClassroomAppModel`; `WindowGroup`
creates the dashboard scene; lifecycle hooks forward termination to the model.
For a C programmer, treat this file as the small `main` that constructs the
long-lived owner graph rather than as an ordinary view.
""",
    "ClassroomAppModel.swift": """
This type is isolated to Swift's main actor and is the application coordinator,
not a general-purpose data model. Read it as workflows: stored settings and
latched session configuration; construction and callback wiring; start,
pause/resume, and drain/stop; transcription-event reduction; serialized Gemma
correction; spoken-command interception; overlay projection; local-network
publication; diagnostics and shutdown.

The central invariant is ownership by execution domain. UI-visible state is
mutated only on the main actor. Core Audio owns its callback deadline. Embedded
Voxtral owns one serial inference queue. The network server owns a different
serial queue. Gemma requests are serialized by an actor/task. Methods in this
file transfer immutable values or owned `Data` between those domains.

Several methods intentionally accept final output while the session is
`stopping`: model drain happens after microphone capture closes. Conversely,
provisional output is ignored outside `listening`. Correction failure never
removes raw evidence. Voice commands are consumed before transcript insertion
so control phrases do not become lecture captions.
""",
    "ProcessMemory.swift": """
Darwin exposes process memory through Mach task APIs and `proc_pidinfo`. The
helper returns an optional byte count because permission, process lifetime, or
API failure can make a measurement unavailable. A missing value is not reported
as zero: zero would falsely mean the process consumes no memory.
""",
    "AudioDeviceCatalog.swift": """
Core Audio identifies devices with numeric `AudioObjectID` values but user
preferences need stable string UIDs. This file enumerates devices, filters for
input capability, resolves a saved UID back to the current object ID, and
configures AUHAL. Property queries follow Core Audio's two-step pattern:
request byte size, allocate storage, then request data.

OSStatus is a signed integer status convention inherited from C APIs. Every
property address combines selector, scope, and element; confusing input scope
with output scope is a common source of silent device-selection bugs.
""",
    "MicrophoneCaptureService.swift": """
This file crosses the strictest real-time boundary in the app. The C-compatible
AUHAL callback receives pointers valid only during the callback. It renders into
an `AVAudioPCMBuffer`, converts to mono signed PCM16 at 16 kHz, creates owned
`Data`, and dispatches that value to a non-real-time processing queue.

`Unmanaged.passRetained` explicitly transfers one Swift reference count into
the C callback context. `takeUnretainedValue` borrows it during callbacks;
`release` occurs only after the Audio Unit is stopped and the processing queue
is drained. The lock protects publication/removal of the Audio Unit and context,
not sample processing. Teardown reverses construction order so no callback can
observe a released context.
""",
    "SessionArchiveService.swift": """
The archive service serializes filesystem work on one queue. Start creates a
session directory and reserves a 44-byte WAV header. Audio appends extend the
file without blocking the main actor. Finalization rewrites the header with the
actual data size, closes the handle, then writes transcript text, JSON, and
metadata. Cancellation closes resources and removes partial state.

The generic `perform` bridge converts callback/queue work into Swift
continuations. Its ownership contract matters: exactly one continuation resume
must occur, and mutable file state remains queue-confined despite the class's
`@unchecked Sendable` declaration.
""",
    "DashboardView.swift": """
SwiftUI views are transient value descriptions. `body` is re-evaluated from
observable model state; it is not a retained widget tree that application code
mutates directly. Bindings write settings back to `ClassroomAppModel`; buttons
invoke workflows; helper properties split a large dashboard into readable view
fragments.

The QR helper supplies UTF-8 URL bytes to Core Image, requests correction level
M, then applies an integer scale without interpolation. The result transfers a
bearer URL visually; it does not add encryption or authentication.
""",
    "CaptionOverlayController.swift": """
The overlay combines AppKit and SwiftUI because neither alone expresses the
whole requirement cleanly. AppKit owns a borderless non-activating `NSPanel`,
screen selection, window level, Spaces behavior, persistence, and pointer
gestures. `NSHostingView` embeds the declarative caption content.

The interaction view distinguishes move from edge/corner resize and reports
translations to the controller. Geometry is clamped to the selected screen's
visible frame with minimum dimensions. The SwiftUI overlay uses a scroll view
and explicit bottom scrolling so new captions remain visible instead of being
truncated with an ellipsis.
""",
    "GemmaServerController.swift": """
This main-actor controller owns only a server process that it launched. It first
probes the loopback endpoint, launches MLX-LM only when necessary, polls health
with a monotonic deadline, and detects early process exit. Reusing an already
healthy endpoint allows an independently started server.

The command line fixes temperature to zero, disables model reasoning, limits
generation, and sets prompt/decode concurrency to one. Those are latency and
behavior controls, not the primary safety boundary. The primary boundary is
that the model receives text and returns text without application tools.
""",
    "GemmaCorrectionService.swift": """
The actor serializes access to its URLSession-facing correction state. Nested
`Codable` structures describe exactly the OpenAI-compatible JSON subset used by
MLX-LM. Coding keys translate snake_case wire names without leaking that naming
style into Swift properties.

The system prompt treats captions and context as untrusted quoted data.
Delimiters provide structure but are not trusted as a security mechanism.
Security comes from capability absence, output-shape checks, and the
deterministic `CaptionCorrectionValidator`. A response containing separate
reasoning is rejected. HTTP failure, malformed JSON, timeout, or excessive
rewrite leaves the raw caption visible.
""",
    "ClassroomVoxtral.h": """
This is the project-owned stable C ABI between Swift and the imported Voxtral
runtime. Opaque model/stream handles hide upstream layouts. Status codes replace
process termination and textual stderr with values Swift can classify. Stream
options collect the latency/context controls that must be fixed at creation.
""",
    "ClassroomVoxtral.c": """
The bridge validates model files, translates signed PCM16 to normalized float,
forwards feed/flush/finish calls, buffers text when the caller's destination is
too small, and maps upstream return conventions to stable project status codes.
It also exposes counters without giving Swift direct access to `vox_stream`.

Cancellation uses an atomic flag because it may be requested independently of
the inference queue. Destruction remains serialized by the Swift owner; the
atomic does not make arbitrary concurrent stream entry safe.
""",
    "VoxtralEmbeddedService.swift": """
This service owns one C model handle and one C stream handle and confines all
operations to a serial inference queue. Startup loads the full FP16/BF16 model,
creates configured streaming state, primes the decoder with silence, and only
then emits `connected`. Priming moves one-time allocation and kernel warm-up
before live speech so the first words are not lost.

PCM feed, flush, text draining, counters, and destruction never overlap.
`AsyncStream` transfers value events to the app model. Stop drains stable text
before releasing the stream; cancellation remains available for shutdown.
""",
    "voxtral_audio.c": """
The first half implements bounded WAV parsing and a one-shot log-Mel
spectrogram. The second half is the incremental front end. It retains enough
left waveform context for future windows, emits only complete frames, tracks an
absolute frame offset across compaction, and adds right padding exactly once at
finish.

Keep units explicit: waveform samples at 16 kHz, FFT windows, hop positions,
Mel bins, and emitted frame indices. Most streaming errors in this layer are
off-by-one mistakes between retained sample indices and absolute frame indices.
""",
    "voxtral_tokenizer.c": """
The tokenizer loader parses the Tekken vocabulary representation used by the
model and builds an ID-to-byte-piece table. Decoder output may split a UTF-8
character across tokens, so consumers must concatenate bytes before assuming a
complete displayed character. Control token IDs are model protocol, not text.
""",
    "voxtral_safetensors.c": """
Safetensors begins with a little-endian JSON-header length followed by metadata
and raw tensor bytes. This implementation memory-maps the file, parses only the
required JSON grammar, validates every offset against the mapping, and exposes
zero-copy BF16 pointers when the requested tensor is BF16 and its bytes fit the
mapping (there is no alignment requirement).

Converted F32 buffers have different ownership from direct mapped pointers.
Read every accessor together with its allocation rule; freeing mapped model
storage as if it were heap memory would be invalid.
""",
    "voxtral_encoder.c": """
The audio encoder loads convolution and transformer weights, applies the
strided convolutional stem, then runs self-attention and feed-forward layers.
The incremental path maintains encoder KV caches and compacts them while
preserving absolute position meaning.

Tensor comments and loop bounds are part of the contract. Track shapes as
`[sequence, model_dimension]`, per-head dimensions, and cache capacity. The
Metal path accelerates matrix-heavy operations; scalar code remains responsible
for allocation, shape validation, and fallback.
""",
    "voxtral_decoder.c": """
The decoder owns autoregressive text state. Prefill consumes the
audio-conditioned prompt in batches; forward consumes one new embedding and
produces logits for the next token. Per-layer KV caches avoid recomputing all
previous positions and may use FP16 storage before switching to FP32 fallback.

Cache growth, compaction, and position counters must agree. A copied cache row
represents a specific absolute token position; moving bytes without updating
the corresponding logical base would silently corrupt attention.
""",
    "voxtral_kernels.c": """
These are numerical building blocks: vector operations, matrix multiplication,
normalization, activations, softmax, rotary position embeddings, convolution,
and attention helpers. Accelerate/BLAS or Metal handles expensive paths where
available; scalar loops define the reference semantics.

For each kernel, identify input/output shape, aliasing permission, numeric
format, and whether the operation is in-place. BF16 conversion preserves the
upper 16 bits of IEEE-754 float representation; it is not IEEE half precision.
""",
    "voxtral.c": """
This is the streaming orchestration state machine. Read it with five clocks:
16 kHz PCM samples, Mel frames, post-convolution positions, encoder positions,
and adapter/decoder positions. Absolute counters retain temporal meaning while
bounded buffers compact their stored prefixes.

The model context owns immutable weights and GPU resources. Each `vox_stream`
owns mutable audio history, incremental front-end state, encoder/adapter
features, decoder KV state, queued text tokens, and recovery counters.
Continuous mode periodically resets language state without discarding the
audio timeline. Flush forces currently stable work through the pipeline; finish
adds terminal padding and drains the final caption.
""",
    "voxtral_metal.m": """
This Objective-C translation unit is the host runtime for Apple Metal. Global
state owns the device, command queue, shader library, pipeline states, reusable
activation buffers, converted-weight caches, merged-weight caches, and cached
`MPSMatrixMultiplication` objects. Initialization and shutdown must be paired.

CPU code validates dimensions and encodes commands; GPU kernels operate on
buffers. Shared-storage buffers permit CPU/GPU visibility but do not remove the
need for command-buffer ordering and completion waits. Cache keys must include
every shape/dtype property that changes compiled behavior.

Objective-C automatic reference counting manages Objective-C objects, while
the exported C API still has explicit ownership for raw allocations and opaque
context pointers.
""",
    "voxtral_shaders_source.h": """
This generated header embeds complete Metal Shading Language source in the C
binary. Each kernel's thread/grid mapping is part of its API: host dispatch
dimensions, buffer element type, parameter struct, and bounds checks must agree
exactly. The source includes normalization, activation, cache-copy, attention,
rotary embedding, fused feed-forward, residual, and reduction kernels.
""",
    "LocalCaptionServer.swift": """
One serial queue owns listener, accepted connections, capability tokens,
student tickets, rate windows, current snapshot, and heartbeat scheduling.
Network.framework callbacks are delivered onto that queue, making the mutable
server state single-owner despite the class's `@unchecked Sendable` boundary.

TCP is a byte stream, so request framing accumulates arbitrary receive chunks
until the HTTP header terminator and declared body length are present. The
server implements only its generated clients' HTTP subset. Viewer and student
capabilities are independent; student POSTs additionally require short-lived,
source-bound tickets and pass several bounded rate limits.

SSE connections remain open and receive an immediate snapshot plus later
revisioned updates and heartbeat comments. Browser input never reaches Gemma or
application control APIs.
""",
    "VoxtralRealtimeService.swift": """
This optional backend translates a remote WebSocket JSON protocol into the same
`TranscriptionEvent` algebra used by embedded Voxtral. A lock protects
connection state shared between URLSession delegate callbacks and async caller
methods. Audio is base64-encoded because the selected protocol carries JSON
messages rather than binary WebSocket frames.

The parser searches several known response shapes to tolerate server variants,
but lifecycle remains strict: one continuation, one socket, explicit commit,
and deterministic disconnect/failure events.
""",
    "main.swift": """
The benchmark is intentionally outside AppKit and microphone capture. It parses
arguments, validates WAV/PCM input, feeds the project C ABI in timed chunks,
drains text exactly as the application does, and reports model-load time, audio
duration, inference time, real-time factor, first-token latency, the transcript,
and optional word accuracy. It does not emit decoder token counts or
tokens-per-second; those diagnostics exist only on the embedded in-app path.

Word accuracy uses word-level Levenshtein distance normalized by reference
length. It is a diagnostic metric, not a replacement for listening tests.
""",
    "Package.swift": """
The Swift Package manifest is executable Swift evaluated by Swift Package
Manager. It declares the core library, C/Objective-C/Metal target, GUI
executable, benchmark, and tests; links Apple frameworks; and sets C language
and compiler options. Dependency arrows here are compile-time ownership
boundaries reflected in Chapter 1.
""",
    "Info.plist": """
The property list supplies the macOS bundle identity, executable name,
microphone usage explanation, local-network explanation, Bonjour service type,
and application behavior flags. Permission descriptions are user-visible
security declarations, not comments.
""",
}

SYMBOL_GUIDES = {
    ("ClassroomAppModel.swift", "init()"): """
Construction creates services once and installs value-returning callbacks.
Callbacks that originate off the main actor re-enter it explicitly before
touching observable state. The initializer also loads persisted settings, but
does not start microphone or model resources.
""",
    ("ClassroomAppModel.swift", "func startSession()"): """
Start is deliberately staged. It validates and latches settings, starts optional
archive/correction preparation, and asks Voxtral to initialize. The domain
`ClassroomSession` is not created here: it is constructed only after the
transcription service emits `connected`, at the moment microphone capture opens
(in `startMicrophoneAfterVoxtralConnection`). This ordering prevents model
startup from consuming the first spoken audio without decoding it.
""",
    ("ClassroomAppModel.swift", "func stopSession()"): """
Stop first closes the capture gate, cancels the periodic commit and silence-flush
tasks, then stops microphone callbacks, flushes and drains Voxtral, accepts the
final drained caption while the session is `stopping`, waits for correction work
up to its deadline, and finalizes the archive. This reverse-lifetime order is why
the last words survive.
""",
    ("ClassroomAppModel.swift", "handleVoxtralEvent"): """
This method is the reducer from backend events to domain transitions.
Provisional and finalized text pass through spoken-command interception before
timeline mutation. Metrics update diagnostics independently. Disconnect and
failure events are interpreted in light of whether stop was expected.
""",
    ("ClassroomAppModel.swift", "startMicrophoneAfterVoxtralConnection"): """
This asynchronous handoff checks that the original start attempt is still
current before opening hardware. The callback creates owned PCM data, updates
meter/archive accounting outside the real-time callback, and forwards audio
only while the capture gate remains open.
""",
    ("ClassroomAppModel.swift", "startCorrectionWorkerIfNeeded"): """
At most one worker drains the FIFO. The explicit queue bounds memory and makes
Gemma latency predictable on a large local model. New segments can be appended
while the worker is active without launching parallel generations.
""",
    ("ClassroomAppModel.swift", "correctSegment"): """
Correction snapshots context and configuration, marks the segment as
`correcting`, measures latency and token usage, then applies only validator-
approved output to the matching UUID. Every thrown path delegates to
`failCorrection`, preserving `rawText`.
""",
    ("ClassroomAppModel.swift", "consumeOverlayVoiceCommand"): """
Potential command prefixes are held back while provisional recognition is
incomplete. Completed commands are removed from the caption text and applied
in source order. This prevents phrases such as the show/hide command from
appearing as lecture content.
""",
    ("ClassroomAppModel.swift", "refreshOverlay"): """
The overlay receives a projection: recent finalized display text, provisional
text, question state, visual settings, and diagnostics. The controller owns
window lifetime; the model supplies values and intent.
""",
    ("MicrophoneCaptureService.swift", "microphoneInputCallback"): """
This function has a C callback ABI. `reference` is the opaque retained Swift
context. The callback allocates/render-converts one chunk and immediately
dispatches owned bytes. Returning `OSStatus` follows Audio Unit convention;
Swift errors cannot cross this C function boundary.
""",
    ("MicrophoneCaptureService.swift", "func start("): """
Start is transactional. Any failure after Audio Unit creation disposes the
partially constructed instance. A successful return means device selection,
format negotiation, callback installation, initialization, and hardware start
all completed.
""",
    ("MicrophoneCaptureService.swift", "func stop()"): """
State is removed under the lock before external teardown. Repeated stop calls
are therefore harmless. Queue synchronization occurs only when the caller is
not already on that queue, avoiding self-deadlock.
""",
    ("MicrophoneCaptureService.swift", "func convert("): """
The converter input closure may be called more than once. The mutex-backed flag
supplies the source buffer exactly once and then reports `.noDataNow`.
Frame-capacity calculation allows resampling expansion plus a small margin.
The returned `Data` copies PCM bytes out of the temporary AVAudio buffer.
""",
    ("GemmaServerController.swift", "ensureReady"): """
Readiness is idempotent: a healthy existing endpoint returns immediately.
Otherwise the owned process is launched once and polled with `ContinuousClock`,
which is monotonic and unaffected by wall-clock changes. Early child exit is
reported without waiting for the full timeout.
""",
    ("GemmaCorrectionService.swift", "func correct("): """
The request budget scales with caption length but remains bounded. Context and
target are placed in separate data markers. After HTTP and JSON checks, any
nonempty reasoning channel causes rejection; content then passes through the
deterministic validator before becoming a result.
""",
    ("VoxtralEmbeddedService.swift", "func start("): """
All C construction occurs on the inference queue. Failure unwinds model and
stream handles before reporting an event. Startup options translate UI
milliseconds/context values into the bridge ABI, and decoder priming moves
first-use GPU allocation outside live capture.
""",
    ("VoxtralEmbeddedService.swift", "func sendAudio"): """
`Data` owns the callback bytes. The inference queue converts and feeds them
serially, drains complete token pieces, and emits metrics. No second feed can
enter the mutable C stream concurrently.
""",
    ("VoxtralEmbeddedService.swift", "func stop()"): """
Stop marks the service inactive, finishes the C stream, drains remaining text,
returns any finalized provisional caption, then destroys stream before model.
The returned string exists because final drain may produce text after the last
ordinary event.
""",
    ("voxtral.c", "vox_load"): """
Model loading opens each component, validates expected tensors, initializes
Metal, and preallocates caches. Follow every failure label to verify that it
releases exactly the resources constructed before that point.
""",
    ("voxtral.c", "struct vox_stream"): """
This structure is the complete mutable streaming state. Fields belong to
different time domains; prefixes may be compacted while absolute counters
continue increasing. It is intentionally not exposed through the project ABI.
""",
    ("voxtral.c", "stream_run_encoder"): """
Only newly stable convolution positions enter the encoder. Produced embeddings
are appended in absolute order, then grouped by the modality adapter. Buffer
compaction cannot change the position represented by an embedding.
""",
    ("voxtral.c", "stream_run_decoder"): """
The decoder first pre-fills an audio-conditioned prompt, then greedily advances
tokens. Control-token classification decides caption boundaries and recovery.
Text pieces are queued separately so Swift polling does not control inference
progress.
""",
    ("voxtral.c", "vox_stream_feed"): """
Feed appends waveform samples to the incremental Mel context and runs whichever
downstream stages now have stable work. It does not imply finalization; missing
right context remains buffered for later audio.
""",
    ("voxtral.c", "vox_stream_flush"): """
Flush asks the pipeline to expose work stable at the current boundary without
destroying the stream. Finish additionally supplies terminal padding and marks
the input complete. The app uses these operations for caption boundaries and
session shutdown respectively.
""",
    ("voxtral_audio.c", "vox_parse_wav_buffer"): """
The parser walks RIFF chunks rather than assuming a fixed header layout. Every
chunk length is bounds-checked, odd-byte padding is respected, and only the
supported PCM representation is converted.
""",
    ("voxtral_audio.c", "vox_mel_feed"): """
Feed appends samples, computes every newly complete analysis window, and keeps
the unresolved waveform tail. Absolute frame offset is separate from the
current compacted array index.
""",
    ("voxtral_safetensors.c", "safetensors_open"): """
Open validates file size, maps bytes read-only, parses the bounded JSON header,
and verifies every tensor data interval before publishing the file object.
Subsequent direct access relies on these checks.
""",
    ("voxtral_decoder.c", "vox_decoder_prefill"): """
Prefill processes multiple prompt positions and writes their per-layer KV
entries. It amortizes setup compared with token-by-token forward execution.
Position and cache capacity checks must precede GPU dispatch.
""",
    ("voxtral_decoder.c", "vox_decoder_forward"): """
Forward computes one autoregressive step from the new embedding and existing
cache, writes the new K/V rows, performs the greedy argmax internally, and
returns the selected token id while leaving the full logits buffer available for
diagnostics.
""",
    ("LocalCaptionServer.swift", "func start("): """
Start generates fresh independent capabilities, creates Wi-Fi-constrained TCP
parameters, installs listener callbacks on the server queue, and publishes
URLs only after listener readiness and local-address selection.
""",
    ("LocalCaptionServer.swift", "receiveRequest"): """
Each receive callback appends arbitrary TCP bytes to a bounded accumulator.
Routing starts only after a complete header and declared body are present.
Header and body limits are checked before allocation can grow without bound.
""",
    ("LocalCaptionServer.swift", "handleRequest"): """
Routing authenticates capabilities before exposing protected route behavior.
Unknown routes and wrong credentials deliberately share a response shape.
Viewer routes cannot submit questions; student routes cannot control captions.
""",
    ("LocalCaptionServer.swift", "publish"): """
SSE framing JSON-encodes one immutable snapshot, prefixes protocol fields, and
ends the event with a blank line. Slow or failed connections are removed by the
queue owner rather than blocking the app model.
""",
    ("VoxtralRealtimeService.swift", "func start("): """
Start creates one WebSocket task and installs state before resuming it so early
delegate callbacks have a consistent owner. Connection timeout and cancellation
must settle the same continuation at most once.
""",
    ("main.swift", "func run()"): """
The benchmark constructs the same bridge options used by the app, feeds timed
chunks, repeatedly drains text until `NO_TEXT`, finishes the stream, prints
metrics, and frees handles on every exit path.
""",
}

# Additional per-declaration commentary lives in a sibling module so this file
# stays focused on structure. It is merged in if present.
try:
    from symbol_guides_extra import EXTRA_SYMBOL_GUIDES
except ImportError:  # pragma: no cover - the extra notes are optional
    EXTRA_SYMBOL_GUIDES = {}
SYMBOL_GUIDES.update(EXTRA_SYMBOL_GUIDES)


DECL_RE = re.compile(
    r"^\s*(?:(?:public|private|internal|fileprivate|open|static|final|"
    r"mutating|nonisolated|override|class)\s+)*"
    r"(?:struct|class|actor|enum|protocol|extension|func|init|deinit|"
    r"typedef|#define|[A-Za-z_][\w\s*]+\s+[A-Za-z_]\w*\s*\()"
)
NON_DECLARATION_PREFIXES = (
    "case ", "guard ", "if ", "else ", "for ", "while ", "switch ",
    "return", "throw ", "break", "continue", "defer ", "do {", "catch",
)


def language(path: Path) -> str:
    return {
        ".swift": "swift",
        ".c": "c",
        ".h": "c",
        ".m": "objective-c",
        ".py": "python",
        ".sh": "bash",
        ".plist": "xml",
    }.get(path.suffix, "text")


def unique(values: list[str], limit: int = 10) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
        if len(result) == limit:
            break
    return result


def declaration_names(path: Path, lines: list[str]) -> list[str]:
    names = []
    depths = declaration_depths(path, lines)
    for line, depth in zip(lines, depths):
        stripped = line.strip()
        if not stripped or stripped.startswith(NON_DECLARATION_PREFIXES):
            continue
        is_declaration = False
        if path.suffix == ".swift":
            is_declaration = depth <= 1 and SWIFT_BOUNDARY_RE.match(line) is not None
        elif path.suffix in {".c", ".m", ".metal"}:
            is_declaration = depth == 0 and (
                C_FUNCTION_RE.match(line) is not None
                or C_FUNCTION_START_RE.match(line) is not None
                or stripped.startswith(C_TYPE_BOUNDARY)
            )
        elif path.suffix == ".h":
            is_declaration = is_header_declaration(path, line, stripped, depth)
        elif path.suffix == ".py":
            is_declaration = line.startswith(("def ", "class ", "@dataclass"))
        elif path.name == "Package.swift":
            is_declaration = depth <= 1 and SWIFT_BOUNDARY_RE.match(line) is not None
        if is_declaration:
            compact = " ".join(stripped.split())
            names.append(compact[:150])
    return unique(names, 8)


def declaration_map(path: Path, lines: list[str]) -> list[tuple[int, str]]:
    declarations: list[tuple[int, str]] = []
    depths = declaration_depths(path, lines)
    for number, (line, depth) in enumerate(zip(lines, depths), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*", "#include")):
            continue
        if stripped.startswith(NON_DECLARATION_PREFIXES):
            continue
        is_declaration = False
        if path.suffix == ".swift":
            is_declaration = depth <= 1 and SWIFT_BOUNDARY_RE.match(line) is not None
        elif path.suffix in {".c", ".m", ".metal"}:
            is_declaration = depth == 0 and (
                C_FUNCTION_RE.match(line) is not None
                or C_FUNCTION_START_RE.match(line) is not None
                or stripped.startswith(C_TYPE_BOUNDARY)
            )
        elif path.suffix == ".h":
            is_declaration = is_header_declaration(path, line, stripped, depth)
        elif path.suffix == ".py":
            is_declaration = line.startswith(("def ", "class ", "@dataclass"))
        elif path.name == "Package.swift":
            is_declaration = depth <= 1 and SWIFT_BOUNDARY_RE.match(line) is not None
        if is_declaration:
            compact = " ".join(stripped.split())
            declarations.append((number, compact[:180]))
    return declarations


SWIFT_BOUNDARY_RE = re.compile(
    r"^\s*(?:(?:public|private|internal|fileprivate|open|static|final|"
    r"mutating|nonisolated|override|class|convenience|required)\s+)*"
    r"(?:struct|class|actor|enum|protocol|extension|func|init|deinit|"
    r"var\s+[A-Za-z_]\w*[^=]*\{|subscript)\b"
)
C_FUNCTION_RE = re.compile(
    r"^\s*(?:(?:static|inline|extern|const|unsigned|signed|struct|enum)\s+)*"
    r"[A-Za-z_][\w\s*<>]*\s+[A-Za-z_]\w*\s*\([^;]*\)\s*\{"
)
# A definition whose signature wraps across lines: the first line carries a
# return type and `name(`, but the closing `)`/`{` arrive on a later line.
# Applied only at brace depth 0, where C/Objective-C has no statements that
# could be confused for it. The trailing `[^;]*$` keeps single-line prototypes
# (`void f(int);`) from matching while still catching multi-line definitions.
C_FUNCTION_START_RE = re.compile(
    r"^\s*(?:(?:static|inline|extern|const|unsigned|signed|struct|enum)\s+)*"
    r"[A-Za-z_][\w\s*<>]*?[\s*]+[A-Za-z_]\w*\s*\([^;]*$"
)
# Top-level type definitions also start a documentation block.
C_TYPE_BOUNDARY = ("struct ", "typedef ", "enum ", "union ")
SHADER_FUNCTION_RE = re.compile(r'^\s*".*\b(?:kernel|inline)\s+\w+.*\(')
HEADER_PREPROCESSOR_BOUNDARIES = (
    "#ifndef ",
    "#ifdef ",
    "#if ",
    "#elif ",
    "#else",
    "#endif",
    "#define ",
)


def is_header_declaration(path: Path, line: str, stripped: str, depth: int) -> bool:
    """Whether a `.h` line begins a documentable declaration.

    Handles wrapped multi-line prototypes: the start line (`void foo(int a,`)
    is the declaration, while its tail (`int b);`) must not start its own block.
    A tail is recognized because it closes more parentheses than it opens.
    """
    if path.name == "voxtral_shaders_source.h":
        return SHADER_FUNCTION_RE.match(line) is not None
    if depth != 0:
        return False
    if stripped.startswith(
        ("typedef ", "struct ", "enum ", "union ")
        + HEADER_PREPROCESSOR_BOUNDARIES
    ):
        return True
    if C_FUNCTION_RE.match(line) or C_FUNCTION_START_RE.match(line):
        return True
    if stripped.endswith(";") and stripped.count(")") <= stripped.count("("):
        return True
    return False


def brace_depths(lines: list[str]) -> list[int]:
    """Return approximate brace depth before each line.

    The result is intentionally used only for pagination boundaries, never for
    semantic claims. It handles line comments and quoted strings well enough
    for the project's Swift/C/Objective-C sources.
    """
    result: list[int] = []
    depth = 0
    in_block_comment = False
    for line in lines:
        result.append(depth)
        index = 0
        in_string = False
        escaped = False
        while index < len(line):
            pair = line[index:index + 2]
            if in_block_comment:
                if pair == "*/":
                    in_block_comment = False
                    index += 2
                    continue
                index += 1
                continue
            if not in_string and pair == "/*":
                in_block_comment = True
                index += 2
                continue
            if not in_string and pair == "//":
                break
            char = line[index]
            if char == '"' and not escaped:
                in_string = not in_string
            if not in_string:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth = max(0, depth - 1)
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
            index += 1
    return result


def declaration_depths(path: Path, lines: list[str]) -> list[int]:
    """Return brace depths suitable for declaration-boundary detection.

    C headers commonly wrap their public declarations in::

        #ifdef __cplusplus
        extern "C" {
        #endif

    That brace controls C++ linkage; it is not a semantic container like a
    struct or function body. Counting it made every prototype appear nested and
    collapsed an entire public API into the preceding include-guard block. Keep
    ordinary lexical depth for all other files, but subtract active extern-C
    wrappers while scanning a header.
    """
    depths = brace_depths(lines)
    if path.suffix != ".h":
        return depths

    adjusted: list[int] = []
    extern_c_wrappers = 0
    for line, depth in zip(lines, depths):
        stripped = line.strip()
        adjusted.append(max(0, depth - extern_c_wrappers))
        if re.match(r'^extern\s+"C"\s*\{\s*$', stripped):
            extern_c_wrappers += 1
        elif (
            extern_c_wrappers > 0
            and stripped == "}"
            and depth == extern_c_wrappers
        ):
            extern_c_wrappers -= 1
    return adjusted


def declaration_boundaries(path: Path, lines: list[str]) -> list[int]:
    depths = declaration_depths(path, lines)
    candidates = [1]
    for number, (line, depth) in enumerate(zip(lines, depths), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        if path.suffix == ".swift":
            if depth <= 1 and SWIFT_BOUNDARY_RE.match(line):
                start = number
                while start > 1 and lines[start - 2].lstrip().startswith("@"):
                    start -= 1
                candidates.append(start)
        elif path.suffix in {".c", ".m", ".metal"}:
            if depth == 0 and (
                C_FUNCTION_RE.match(line)
                or C_FUNCTION_START_RE.match(line)
                or stripped.startswith(C_TYPE_BOUNDARY)
            ):
                candidates.append(number)
        elif path.suffix == ".h":
            if is_header_declaration(path, line, stripped, depth):
                candidates.append(number)
        elif path.suffix == ".py":
            if line.startswith(("def ", "class ", "@dataclass")):
                candidates.append(number)
        elif path.suffix == ".sh":
            if re.match(r"^[A-Za-z_]\w*\(\)\s*\{", line):
                candidates.append(number)

    candidates = sorted(set(candidates))
    # A very large declaration may still need pagination. Split only at blank
    # lines, preserving contiguous source and clearly naming continuations.
    boundaries = [candidates[0]]
    for start, end in zip(candidates, candidates[1:] + [len(lines) + 1]):
        cursor = start
        while end - cursor > HARD_BLOCK_LINES:
            ideal = cursor + TARGET_BLOCK_LINES
            lower = max(cursor + 40, ideal - 25)
            upper = min(end - 1, ideal + 35)
            blank = next(
                (
                    position
                    for position in range(upper, lower - 1, -1)
                    if not lines[position - 1].strip()
                ),
                ideal,
            )
            if blank <= cursor:
                break
            boundaries.append(blank + 1)
            cursor = blank + 1
        if end <= len(lines):
            boundaries.append(end)
    return sorted(set(boundaries))


def block_title(path: Path, block: list[str], start: int, end: int) -> str:
    declarations = declaration_names(path, block)
    if declarations:
        readable = declarations[0].rstrip("{").strip()
        if readable in {"typedef struct", "typedef enum", "typedef union"}:
            body = "".join(block)
            alias = re.search(r"}\s*([A-Za-z_]\w*)\s*;", body)
            if alias:
                readable += f" {alias.group(1)}"
        # A wrapped multi-line signature has an unbalanced '(' on its first
        # line; show the name and an opener rather than a truncated fragment.
        if readable.count("(") > readable.count(")"):
            readable = readable[: readable.index("(") + 1] + "…)"
        return f"`{readable}`"
    return f"Continuation of the surrounding declaration (lines {start}-{end})"


def preamble_title(path: Path) -> str:
    if path.suffix == ".swift" or path.name == "Package.swift":
        return "Imports and file preamble"
    if path.suffix == ".h":
        return "Header preamble"
    if path.suffix in {".c", ".m", ".metal"}:
        return "Translation-unit preamble"
    if path.suffix == ".py":
        return "Module preamble"
    if path.suffix == ".sh":
        return "Script preamble"
    return "File preamble"


def preamble_guide(path: Path, block: list[str]) -> str:
    text = "".join(block)
    if path.suffix == ".swift":
        modules = re.findall(r"^\s*(?:@preconcurrency\s+)?import\s+(\w+)", text, re.MULTILINE)
        if modules:
            rendered = ", ".join(f"`{module}`" for module in modules)
            return (
                f"The file begins by importing {rendered}. These imports establish "
                "the APIs visible to the declarations below; they execute no "
                "application workflow by themselves."
            )
    if path.suffix == ".h":
        return (
            "This preamble contains comments and preprocessing setup that apply to "
            "the complete public header. It introduces no runtime state."
        )
    if path.suffix in {".c", ".m", ".metal"}:
        return (
            "This translation-unit preamble selects dependencies, compile-time "
            "features, and file-local constants used by the definitions that follow."
        )
    if path.suffix == ".py":
        return (
            "The module preamble imports standard-library dependencies and defines "
            "configuration shared by the functions below."
        )
    if path.suffix == ".sh":
        return (
            "The script preamble selects the interpreter and failure behavior before "
            "any build operation runs."
        )
    return "This preamble establishes file-level context for the declarations below."


def symbol_present(symbol: str, text: str) -> bool:
    # Containment that respects identifier boundaries, so a short symbol such as
    # `vox_load` does not match inside `vox_adapter_load`. Boundaries are applied
    # only on the sides where the symbol itself ends in an identifier character
    # (keys like `func start(` must still match `func start(executablePath:`).
    left = r"(?<![A-Za-z0-9_])" if (symbol[:1].isalnum() or symbol[:1] == "_") else ""
    right = r"(?![A-Za-z0-9_])" if (symbol[-1:].isalnum() or symbol[-1:] == "_") else ""
    return re.search(left + re.escape(symbol) + right, text) is not None


def symbol_guide(path: Path, block: list[str]) -> str | None:
    # A pagination continuation of a large declaration begins no declaration of
    # its own, so it must never borrow a note: its body can name other functions
    # it merely calls. Only blocks that actually start a declaration qualify.
    if not declaration_names(path, block):
        return None
    # Match a note's symbol only against the block's own top-level declaration
    # lines, never the deeper body. Matching the whole block text let a function
    # that *calls* a longer-named helper borrow that helper's note (the longest
    # match wins), which produced duplicated/misattached commentary.
    depths = brace_depths(block)
    base = min(depths) if depths else 0
    header = "".join(
        line for line, depth in zip(block, depths) if depth <= base
    )
    # Anonymous C typedefs put their useful declaration name after the closing
    # brace (`} vox_ctx_t;`). That line is lexically inside the brace depth, so
    # append the alias explicitly for precise per-type commentary matching.
    if block and block[0].lstrip().startswith(("typedef struct", "typedef enum", "typedef union")):
        alias = re.search(r"}\s*([A-Za-z_]\w*)\s*;", "".join(block))
        if alias:
            header += "\n" + alias.group(1)
    matches = [
        (len(symbol), guide)
        for (filename, symbol), guide in SYMBOL_GUIDES.items()
        if filename == path.name and symbol_present(symbol, header)
    ]
    if not matches:
        return None
    # Prefer the most specific configured spelling.
    return max(matches, key=lambda item: item[0])[1].strip()


def parse_embedded_bytes(text: str) -> bytes:
    return bytes(int(token, 16) for token in re.findall(r"0x([0-9a-fA-F]{2})", text))


# A throwaway `.metal` path so the shader's decoded source reuses the C-style
# declaration splitting, titling, and note matching above.
SHADER_MSL_PATH = Path("voxtral_shaders.metal")


def write_shader_section(
    path_text: str, raw: bytes, text: str, digest: str
) -> str:
    """Render the embedded shader header as readable, decoded Metal source.

    The repository stores the shader library as a C byte array compiled into the
    runtime. Listing the hexadecimal bytes is useless to a reader, so the array
    is decoded back to the exact Metal Shading Language the compiler embedded and
    listed in full, split per kernel. Byte-for-byte fidelity is still verified:
    the decoded blocks must reproduce the embedded array exactly.
    """
    data = parse_embedded_bytes(text)
    declared = re.search(r"voxtral_shaders_metal_len\s*=\s*(\d+)", text)
    expected = int(declared.group(1)) if declared else len(data)
    if len(data) != expected:
        raise RuntimeError(
            f"shader byte array length {len(data)} != declared {expected}"
        )
    msl = data.decode("utf-8")
    msl_lines = msl.splitlines(keepends=True)
    msl_digest = hashlib.sha256(data).hexdigest()
    output = [
        f"## `{path_text}`\n\n",
        "**Role.** This header embeds the GPU shader library as a C byte array "
        "(`voxtral_shaders_metal[]`) compiled directly into the runtime, so no "
        "separate `.metallib` ships with the application.\n\n",
        FILE_GUIDES.get("voxtral_shaders_source.h", "").strip() + "\n\n",
        f"Length: {len(text.splitlines())} lines of byte array. "
        f"Header SHA-256: `{digest}`.\n\n",
        "### How this file is stored, and what is shown below\n\n",
        "The repository checks the shader library in as the array "
        f"`voxtral_shaders_metal[]` ({expected} bytes). Those bytes are valid "
        "UTF-8 Metal Shading Language. Printing the hexadecimal array would be "
        "unreadable, so this chapter decodes it back to the exact source the "
        "compiler embedded and lists it in full below, split per kernel. The "
        "decoded text is byte-for-byte identical to the embedded array (decoded "
        f"SHA-256: `{msl_digest}`); the generator reconstructs the array from the "
        "listed blocks and checks every byte.\n\n",
    ]
    declarations = declaration_map(SHADER_MSL_PATH, msl_lines)
    if declarations:
        output.extend([
            "### Kernel and function map {.unnumbered .unlisted}\n\n",
            "Line numbers refer to the decoded Metal source listed below.\n\n",
            "| Line | Kernel or function |\n",
            "| ---: | --- |\n",
        ])
        for number, declaration in declarations:
            escaped = declaration.replace("|", "\\|")
            output.append(f"| {number} | `{escaped}` |\n")
        output.append("\n")
    reconstructed: list[str] = []
    boundaries = declaration_boundaries(SHADER_MSL_PATH, msl_lines)
    active_declaration: str | None = None
    for index, start in enumerate(boundaries):
        end = (
            boundaries[index + 1] - 1
            if index + 1 < len(boundaries)
            else len(msl_lines)
        )
        block = msl_lines[start - 1:end]
        reconstructed.extend(block)
        names = declaration_names(SHADER_MSL_PATH, block)
        if names:
            title = block_title(SHADER_MSL_PATH, block, start, end)
            active_declaration = title
            output.append(f"### {title}\n\n")
        elif start == 1:
            output.append(
                f"### {preamble_title(SHADER_MSL_PATH)} "
                "{.unnumbered .unlisted}\n\n"
            )
            output.append(preamble_guide(SHADER_MSL_PATH, block) + "\n\n")
        else:
            subject = active_declaration or "the preceding declaration"
            output.append(
                f"### Continuation of {subject} "
                "{.unnumbered .unlisted}\n\n"
            )
        guide = symbol_guide(SHADER_MSL_PATH, block)
        if guide:
            output.append(guide + "\n\n")
        body = "".join(block)
        if not body.endswith("\n"):
            body += "\n"
        output.append(
            f'```{{.cpp .numberLines startFrom="{start}"}}\n{body}```\n\n'
        )
    if "".join(reconstructed).encode("utf-8") != data:
        raise RuntimeError(
            "decoded shader blocks do not reproduce the embedded MSL bytes"
        )
    return "".join(output)


def write_file_section(path_text: str) -> tuple[str, bytes]:
    path = ROOT / path_text
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    digest = hashlib.sha256(raw).hexdigest()
    if path.name == "voxtral_shaders_source.h":
        return write_shader_section(path_text, raw, text, digest), raw
    output = [
        f"## `{path_text}`\n\n",
        f"**Role.** {OVERVIEWS.get(path.name, 'This file is reproduced completely below. Read declarations in source order because later helpers rely on ownership and invariants established earlier.')}\n\n",
        FILE_GUIDES.get(
            path.name,
            "Read this file as one ownership unit. The source is divided at "
            "declaration boundaries for navigation; commentary does not infer "
            "behavior from identifier spelling."
        ).strip() + "\n\n",
        f"Length: {len(lines)} lines. SHA-256: `{digest}`.\n\n",
    ]
    declarations = declaration_map(path, lines)
    if declarations:
        output.extend([
            "### Declaration map {.unnumbered .unlisted}\n\n",
            "This map gives the reading spine of the file. Line numbers refer to the "
            "original source and to the numbered listings below.\n\n",
            "| Line | Declaration or entry point |\n",
            "| ---: | --- |\n",
        ])
        for number, declaration in declarations:
            escaped = declaration.replace("|", "\\|")
            output.append(f"| {number} | `{escaped}` |\n")
        output.append("\n")
    reconstructed: list[str] = []
    boundaries = declaration_boundaries(path, lines)
    active_declaration: str | None = None
    for index, start in enumerate(boundaries):
        end = (
            boundaries[index + 1] - 1
            if index + 1 < len(boundaries)
            else len(lines)
        )
        block = lines[start - 1:end]
        reconstructed.extend(block)
        names = declaration_names(path, block)
        if names:
            title = block_title(path, block, start, end)
            active_declaration = title
            output.append(f"### {title}\n\n")
        elif start == 1:
            output.append(
                f"### {preamble_title(path)} {{.unnumbered .unlisted}}\n\n"
            )
            output.append(preamble_guide(path, block) + "\n\n")
        else:
            subject = active_declaration or "the preceding declaration"
            output.append(
                f"### Continuation of {subject} "
                "{.unnumbered .unlisted}\n\n"
            )
        guide = symbol_guide(path, block)
        if guide:
            output.append(guide + "\n\n")
        body = "".join(block)
        if not body.endswith("\n"):
            body += "\n"
        output.append(
            f'```{{.{language(path)} .numberLines startFrom="{start}"}}\n'
            f"{body}```\n\n"
        )

    if "".join(reconstructed).encode("utf-8") != raw:
        raise RuntimeError(f"generated blocks do not reproduce {path_text}")
    return "".join(output), raw


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    covered: set[str] = set()
    for chapter in CHAPTERS:
        pieces = [
            "---\n",
            f'title: "{chapter.title}"\n',
            "---\n\n",
            "## Purpose and place in the application\n\n",
            chapter.purpose + "\n\n",
            chapter.position + "\n\n",
            GUIDES.get(chapter.slug, "") + "\n\n",
            "## How to read this chapter\n\n",
            "For each file, first read its hand-written role, ownership, invariants, "
            "and failure model. Source blocks retain original line numbers and syntax "
            "highlighting. Boundaries follow declarations where practical; a very "
            "large declaration is split only for pagination and is labeled as a "
            "continuation. The generator reconstructs every file from emitted blocks "
            "and compares every byte with the repository source. No prose claim is "
            "generated by counting calls or assignments with regular expressions.\n\n",
        ]
        intro = INTROS / f"{chapter.slug}.md"
        if intro.exists():
            pieces.append(intro.read_text(encoding="utf-8") + "\n\n")
        chapter_hash = hashlib.sha256()
        for path_text in chapter.files:
            covered.add(path_text)
            section, raw = write_file_section(path_text)
            pieces.append(section)
            chapter_hash.update(raw)
        pieces.insert(
            8,
            f"Combined source SHA-256: `{chapter_hash.hexdigest()}`.\n\n",
        )
        target = OUT / f"{chapter.slug}.qmd"
        target.write_text("".join(pieces).rstrip() + "\n", encoding="utf-8")
        print(f"generated {target.relative_to(ROOT)} ({len(chapter.files)} files)")

    # The domain chapter (generate_domain_chapter.py) reproduces these files in
    # full; count them as covered so the completeness guarantee still holds.
    covered.update(DOMAIN_CHAPTER_FILES)
    production = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "Sources").rglob("*")
        if path.suffix in {".swift", ".c", ".h", ".m"}
    }
    missing = sorted(production - covered)
    if missing:
        raise RuntimeError("production files omitted from source book: " + ", ".join(missing))
    print(f"verified complete production coverage: {len(production)} files")


if __name__ == "__main__":
    main()
