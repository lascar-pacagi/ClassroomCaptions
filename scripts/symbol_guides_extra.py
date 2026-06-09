"""Additional per-declaration commentary, merged into SYMBOL_GUIDES.

Each entry is keyed by (source_filename, declaration-token); the generator
attaches the note to a source block when the token appears as a whole identifier
in that block's top-level declaration line. Authored from the actual source.
"""

EXTRA_SYMBOL_GUIDES = {
    # --- Application composition and coordinator ----------------------------
    ("ClassroomCaptionsApp.swift", "struct ClassroomCaptionsApp"): """
The process composition root selected by `@main`. `@State` keeps one observable
model alive while SwiftUI reconstructs view values. The window and menu-bar
scenes share that same owner, so start/stop and overlay commands cannot diverge
between two model instances.
""",
    ("ClassroomAppModel.swift", "struct DisplayChoice"): """
A stable UI projection of one `NSScreen`: Core Graphics display ID for
persistence, localized name for selection, and global desktop frame for
diagnostics. It contains no mutable `NSScreen` reference.
""",
    ("ClassroomAppModel.swift", "enum TranscriptionBackend"): """
The user-selectable implementation choice. String raw values persist cleanly,
`CaseIterable` drives the picker, and `Identifiable` uses the enum value itself.
The title is presentation text; workflow branching remains exhaustive on cases.
""",
    ("ClassroomAppModel.swift", "struct ClassroomQuestion"): """
Main-actor representation of an accepted anonymous question. It preserves server
identity and timestamp for queue ordering but intentionally has no source
address, ticket, or student identity.
""",
    ("ClassroomAppModel.swift", "class ClassroomAppModel"): """
Main-actor observable coordinator for all user-visible state and cross-service
workflows. `@Observable` drives SwiftUI invalidation; `@MainActor` is the actual
synchronization rule. Service internals remain on their own queues/actors and
cross this boundary only as values or owned `Data`.
""",
    ("ClassroomAppModel.swift", "struct PendingCorrection"): """
Minimal FIFO work item: immutable segment identity plus the correction mode
latched when queued. The worker re-reads caption/context by UUID, avoiding a
second mutable copy of the segment.
""",
    ("ClassroomAppModel.swift", "func refreshDisplays("): """
Rebuilds display choices from current AppKit screens, repairs a missing/stale
selection, and reprojects the overlay. This handles projector connection and
desktop rearrangement without retaining obsolete screen objects.
""",
    ("ClassroomAppModel.swift", "func toggleSession("): """
UI convenience that selects start versus stop from derived lifecycle state.
The full methods still enforce transition guards, so duplicate button/menu
events remain harmless.
""",
    ("ClassroomAppModel.swift", "submitManualCaption"): """
Development/accessibility fallback that finalizes typed text through the same
domain and Gemma queue as speech. Empty/invalid input is rejected by the
timeline; accepted text clears the editor and refreshes presentation.
""",
    ("ClassroomAppModel.swift", "previewProvisionalCaption"): """
Projects typed text into the replaceable provisional slot without appending
history, allowing overlay behavior to be tested without microphone/model input.
""",
    ("ClassroomAppModel.swift", "revealLastSessionArchive"): """
Asks Finder to reveal the last completed archive URL. It has no filesystem
mutation and no effect before a successful finalize publishes a URL.
""",
    ("ClassroomAppModel.swift", "refreshMicrophones"): """
Re-enumerates current input devices, preserves a still-valid stable UID, and
otherwise falls back to the system default or first device. This repairs state
after USB/Bluetooth hardware changes.
""",
    ("ClassroomAppModel.swift", "observeTranscriptionEvents"): """
Cancels old observers, creates one task per backend stream, and filters events by
the backend latched for the active session. A late event from an inactive
service therefore cannot mutate the current transcript.
""",
    ("ClassroomAppModel.swift", "restartCommitTask"): """
Runs the remote backend's periodic commit loop with a 100 ms lower bound.
Cancellation is checked before and after sleeping so stop does not send a late
commit into a replacement session.
""",
    ("ClassroomAppModel.swift", "discardBufferedAudioAtPause"): """
Creates a caption boundary before pause: embedded Voxtral is flushed and
finalized asynchronously; the WebSocket buffer is committed. This prevents
pre-pause audio from merging with speech after resume.
""",
    ("ClassroomAppModel.swift", "recordFirstCaptionLatencyIfNeeded"): """
Records exactly the first visible-caption delay relative to microphone listening
start. Later provisional revisions leave the metric unchanged.
""",
    ("ClassroomAppModel.swift", "correctionSettingChanged"): """
Enabling correction clears prior error and begins warm-up. Disabling outside an
active session cancels warm-up and stops an owned Gemma process; active-session
work is not torn down midway through its latched workflow.
""",
    ("ClassroomAppModel.swift", "dismissPresentedStudentQuestion"): """
Clears only the question currently shown to the professor; pending questions
remain queued for later presentation.
""",
    ("ClassroomAppModel.swift", "clearPendingStudentQuestions"): """
Drops the not-yet-presented queue and refreshes the pending indicator without
altering the question currently open in the overlay.
""",
    ("ClassroomAppModel.swift", "func toggleOverlay("): """
Manual visibility control. Showing regenerates current content and display
selection rather than merely ordering a possibly stale panel forward.
""",
    ("ClassroomAppModel.swift", "resetLiveDiagnostics"): """
Clears per-session token, latency, transformation, and Gemma counters while
optionally resampling current app memory. It does not unload either model.
""",
    ("ClassroomAppModel.swift", "updateGemmaProcessIdentity"): """
Finds the owned or externally listening Gemma PID and samples its resident
memory. Failure remains `nil`, distinct from a false zero-byte footprint.
""",
    ("ClassroomAppModel.swift", "requestCaptionBoundaryForOverlayClear"): """
When clear is spoken during provisional text, forces the active backend to end
that caption. The pending-clear flag then prevents old provisional content from
immediately reappearing.
""",
    ("ClassroomAppModel.swift", "resumeOverlayAfterClearIfNeeded"): """
Waits for a genuinely new caption after the forced boundary, then restores
visibility only if the overlay was visible before clear. Until finalization
completes it refreshes in the hidden/filtered state.
""",
    ("ClassroomAppModel.swift", "resetOverlayClearState"): """
Atomically resets sequence filtering, boundary wait, remembered visibility, and
provisional command-count state at new/cleared session boundaries.
""",
    ("ClassroomAppModel.swift", "resetOverlayFrame"): """
Resolves the selected screen, removes its persisted geometry, applies the
controller's default frame, and makes the result visible for immediate feedback.
""",
    ("ClassroomAppModel.swift", "handleIPhoneSharingStatus"): """
Reduces server lifecycle values into dashboard URLs. Ready/connected states
publish the current snapshot; nonready states clear stale capability URLs, and
a full stop also resets question status.
""",
    ("ClassroomAppModel.swift", "handleStudentQuestionStatus"): """
Maintains the independently rotatable student URL: only `.ready` exposes it,
while stopped and failed states remove stale capabilities from the dashboard.
""",
    ("ClassroomAppModel.swift", "extension NSScreen"): """
Bridges AppKit's loosely typed device-description dictionary to the stable
`CGDirectDisplayID` used for selection and per-display geometry keys.
""",
    ("ClassroomAppModel.swift", "extension Duration"): """
Converts Swift's seconds/attoseconds representation to Foundation
`TimeInterval` seconds for latency metrics.
""",
    ("ProcessMemory.swift", "physicalFootprintBytes()"): """
Convenience overload sampling the current process ID through the same Darwin
implementation used for Gemma.
""",
    ("ProcessMemory.swift", "physicalFootprintBytes(processID:"): """
Public PID overload that delegates to resident-size measurement and preserves
failure as `nil`.
""",

    # --- Stable ClassroomVoxtral C ABI --------------------------------------
    ("ClassroomVoxtral.h", "#ifndef CLASSROOM_VOXTRAL_H"): """
This is the first half of the conventional C include guard. On the first
inclusion the macro is absent, so preprocessing continues; the next line
defines it. On later inclusions the preprocessor skips everything through the
matching final `#endif`. The guard prevents duplicate type and function
declarations when Swift's generated interoperability build includes this
header through more than one path.
""",
    ("ClassroomVoxtral.h", "#define CLASSROOM_VOXTRAL_H"): """
Defining the include-guard macro records that this header has been processed.
The two standard headers provide `size_t` and fixed-width integers. They are
included here because both types appear in the public ABI; relying on an
indirect include would make this header sensitive to unrelated include order.
""",
    ("ClassroomVoxtral.h", "#ifdef __cplusplus"): """
When a C++ compiler reads the header, `extern "C"` suppresses C++ name mangling
for the declarations that follow, preserving the exact linker symbols exported
by `ClassroomVoxtral.c`. A C or Objective-C compiler skips the linkage wrapper.
The matching conditional near the end closes the brace only in C++ mode.
""",
    ("ClassroomVoxtral.h", "typedef struct ccv_model"): """
Declares an opaque model handle. Callers may store and pass `ccv_model_t *`, but
cannot inspect its fields or allocate the object themselves because the
structure body exists only in `ClassroomVoxtral.c`. This keeps the Swift-facing
ABI stable when the upstream Voxtral context layout changes.
""",
    ("ClassroomVoxtral.h", "typedef struct ccv_stream"): """
Declares the second opaque handle, containing mutable state for one incremental
audio stream. A stream borrows its model for its entire lifetime, so the required
destruction order is stream first, model second. Opacity prevents Swift from
bypassing the bridge's serialization and status-code contract.
""",
    ("ClassroomVoxtral.h", "typedef enum"): """
Defines the complete status domain crossing the C/Swift boundary. Zero is
success; positive values are nonfatal polling outcomes (`NO_TEXT` and
`BUFFER_TOO_SMALL`); negative values are failures or terminal conditions.
Keeping these meanings distinct lets Swift retry a read with a larger buffer,
ignore an empty poll, or surface a real inference error without parsing stderr.
""",
    ("ClassroomVoxtral.h", "typedef struct"): """
Groups creation-time stream policy into one value passed by copy. `delay_ms`
controls model delay conditioning, `processing_interval_seconds` controls how
often accumulated audio advances inference, `continuous` enables long-running
caption recovery, and `max_decode_context_tokens` bounds retained decoder
history. These fields are latched when `ccv_stream_create` constructs the
upstream stream.
""",
    ("ClassroomVoxtral.h", "ccv_stream_options_default"): """
Returns a fully initialized policy value whose defaults are owned by the bridge.
Swift starts from this value and overrides only settings exposed by the UI,
which prevents newly added C fields from being left indeterminate by older
callers.
""",
    ("ClassroomVoxtral.h", "ccv_model_load"): """
Loads the immutable model context from a directory and returns an opaque owned
handle. `status` and `error_message` are optional out-parameters for structured
and human-readable diagnostics; `error_message_capacity` prevents the bridge
from writing past the caller's buffer. A null return means no model ownership
was transferred.
""",
    ("ClassroomVoxtral.h", "ccv_model_free"): """
Releases a model handle returned by `ccv_model_load`. It is null-tolerant, but
the caller must already have destroyed every stream borrowing this model. The
Swift service enforces that lifetime order on its serial inference queue.
""",
    ("ClassroomVoxtral.h", "ccv_stream_create"): """
Allocates mutable decoding state that borrows an already loaded model and
applies the supplied options. As with model loading, null indicates failure and
the two out-parameters explain why. The returned stream is single-owner and is
not made thread-safe by the opaque type.
""",
    ("ClassroomVoxtral.h", "ccv_stream_feed_pcm16"): """
Copies one buffer of mono signed 16-bit PCM into the incremental stream after
normalizing samples to floating point. `sample_count` counts samples, not bytes;
at the fixed 16 kHz model rate, 16,000 samples represent one second. Success
means the bytes were accepted and any newly stable inference work was run, not
that displayable text must already exist.
""",
    ("ClassroomVoxtral.h", "ccv_stream_flush"): """
Forces currently buffered, stable work through the live pipeline without ending
the stream. The application uses this at caption boundaries after silence or a
manual commit, then continues feeding later speech into the same context.
""",
    ("ClassroomVoxtral.h", "ccv_stream_finish"): """
Marks input complete, adds the front-end's required terminal padding, and drains
the final decoder work. After a successful finish no more audio may be fed; text
must still be read until `CCV_STATUS_NO_TEXT` before the stream is freed.
""",
    ("ClassroomVoxtral.h", "ccv_stream_cancel"): """
Requests early termination through the bridge's atomic cancellation flag. It is
the one operation designed to signal a stream independently; it does not make
feed, flush, read, finish, and free mutually thread-safe. Their serialization
remains the Swift service's responsibility.
""",
    ("ClassroomVoxtral.h", "ccv_stream_read_text"): """
Copies the next queued UTF-8 text fragment into caller-owned storage and reports
its required byte count through `bytes_written`. `NO_TEXT` means polling may
stop for now. `BUFFER_TOO_SMALL` lets the caller allocate the required capacity
and retry without losing the queued fragment.
""",
    ("ClassroomVoxtral.h", "ccv_stream_samples_fed"): """
Returns the cumulative number of PCM samples accepted by this stream. The app
uses this monotonic counter for diagnostics; it is not a timestamp and does not
subtract samples whose derived features were compacted from internal buffers.
""",
    ("ClassroomVoxtral.h", "ccv_stream_text_tokens_generated"): """
Returns the cumulative decoder-token count for live throughput diagnostics.
Tokens are model vocabulary units, not words or Unicode characters, so this
counter cannot be inferred reliably from the displayed caption length.
""",
    ("ClassroomVoxtral.h", "ccv_stream_decoder_milliseconds"): """
Returns accumulated wall time spent in decoder inference for this stream. Swift
combines it with the token count to report decoder tokens per second; model
loading, audio capture, Mel computation, and UI rendering are outside this
specific timer.
""",
    ("ClassroomVoxtral.h", "ccv_stream_free"): """
Destroys all mutable buffers and upstream state owned by one stream. The handle
must no longer be used afterward. It is freed before the borrowed model, on the
same serial queue that performed inference.
""",
    ("ClassroomVoxtral.h", "ccv_status_description"): """
Maps a status enum to a static human-readable string for logs and fallback error
messages. The returned pointer is borrowed program storage: callers neither free
nor modify it, and program logic should still branch on the enum value.
""",
    ("ClassroomVoxtral.h", "ccv_upstream_revision"): """
Returns the pinned upstream Voxtral revision compiled into the bridge. This
makes benchmark reports and bug investigations reproducible without exposing
the upstream implementation's internal structures through the ABI.
""",

    # --- Dashboard, overlay, app-model gaps, process memory -----------------
    ("DashboardView.swift", "struct DashboardView"): """
The single SwiftUI dashboard, driven by an `@Bindable` `ClassroomAppModel`.
Its `body` is a `NavigationSplitView` whose detail column stacks every settings
group (session, iPhone sharing, questions, diagnostics, microphone, archive,
Voxtral, correction, overlay, manual input, transcript). The `onChange` hooks
forward display and font-size edits to `refreshOverlay` and correction-toggle
edits to `correctionSettingChanged`, so all live state lives in the model.
""",
    ("DashboardView.swift", "func pairingQRCode"): """
Builds an `NSImage` QR code for a pairing/student URL using
`CIFilter.qrCodeGenerator` at correction level M, then scales the CoreImage
output 10x and wraps it in an `NSCIImageRep`. Returns nil if the filter
produces no output. The 10x affine scale plus `.interpolation(.none)` at the
call site keeps QR modules crisp instead of blurred.
""",
    ("DashboardView.swift", "var diagnostics"): """
The Live Diagnostics group, gated behind the `showLiveDiagnostics` toggle. When
enabled it lays out a monospaced grid of Voxtral token counts/rate, last and
session Gemma token stats, and per-process plus total memory footprints, each
value computed by a dedicated summary helper that degrades to a dash or status
string when its source is nil.
""",
    ("DashboardView.swift", "var gemmaMemorySummary"): """
Formats Gemma's resident footprint, but when the byte count is still nil it
distinguishes "Detecting..." (server ready, identity not yet resolved) from
"Not loaded" based on `correctionServerReady`, so the row never falsely reads
zero before the MLX process is found.
""",
    ("DashboardView.swift", "var voxtralSettings"): """
The Voxtral Realtime group: a backend picker (Embedded Metal vs WebSocket) that
swaps which fields appear -- model directory and a context slider for embedded,
or endpoint/model fields for WebSocket -- plus a shared model-delay slider.
Several controls lock while listening or connected so the backend cannot be
reconfigured mid-stream.
""",
    ("DashboardView.swift", "var correctionSettings"): """
The Gemma correction group: a Standard/Science mode picker, a previous-captions
context stepper, and server/model/endpoint fields (disabled during an active or
starting session). Shows readiness, queue depth, and last latency, and either
the current `correctionError` or the standing note that questions are proofread
as quoted data and answer-like output is rejected.
""",
    ("DashboardView.swift", "correctionBadge"): """
Renders the domain correction state as a compact capsule beside each recent
caption. It is intentionally presentation-only: tapping or displaying the badge
cannot mutate correction state.
""",
    ("CaptionOverlayController.swift", "class OverlayInteractionView"): """
A borderless `NSView` overlaid on the caption panel that owns only the move and
resize gestures. It is non-opaque and reports drag translations via `onDrag`
plus a completion via `onDragEnded`. It sits in front of the SwiftUI hosting
view but claims hits only in its two handle rects (see `hitTest`), letting
clicks elsewhere fall through.
""",
    ("CaptionOverlayController.swift", "func hitTest"): """
The click-through gate: returns self only when the point lands in the 42pt-tall
top move strip or the 48x48 lower-right resize corner, and nil everywhere else.
Returning nil lets the event pass to whatever is behind the overlay, so the
caption body never intercepts clicks. This is what makes the panel mostly
transparent to the mouse despite covering screen area.
""",
    ("CaptionOverlayController.swift", "func acceptsFirstMouse"): """
Returns true so a drag on a handle works even when the overlay window is not the
key/active window -- essential because the panel is a non-activating floater
that never takes focus from the presenter's foreground app.
""",
    ("CaptionOverlayController.swift", "enum Interaction"): """
Two gesture meanings share one transparent AppKit view. Capturing the choice at
mouse-down prevents a drag from switching between move and resize as the pointer
crosses handle boundaries.
""",
    ("CaptionOverlayController.swift", "resetCursorRects"): """
Registers an open-hand cursor over the top move strip and a crosshair over the
resize corner. AppKit calls this when geometry changes, so cursor hit regions
track the current panel size.
""",
    ("CaptionOverlayController.swift", "func mouseDown"): """
Classifies the gesture by testing whether the down point is inside the resize
corner (`.resize`) versus anywhere else in the handle area (`.move`), records
the absolute mouse location as the drag origin, and switches to the closed-hand
cursor for a move. The recorded `mouseDownLocation` is the anchor every
subsequent `mouseDragged` translation is measured from.
""",
    ("CaptionOverlayController.swift", "func mouseDragged"): """
Computes the cumulative translation from `mouseDownLocation` to the current
absolute mouse location and forwards it through `onDrag` with the active
interaction. The delta is absolute-from-origin, not incremental per event,
which is why the controller re-derives the frame from a cached start frame.
""",
    ("CaptionOverlayController.swift", "func mouseUp"): """
Ends the gesture, asks AppKit to recompute cursors, and notifies the controller
to discard its cached start frame and persist final geometry.
""",
    ("CaptionOverlayController.swift", "class CaptionOverlayController"): """
MainActor controller owning the floating caption `NSPanel`, the SwiftUI
`NSHostingView`, and the `OverlayInteractionView`, plus the selected display and
per-display saved geometry. It positions, clamps, persists, and restores the
overlay frame, acts as the panel's `NSWindowDelegate`, and keeps `isApplyingFrame`
to suppress persistence while it is itself setting the frame.
""",
    ("CaptionOverlayController.swift", "override init"): """
Builds the borderless non-activating panel (clear background, floating level,
joins all spaces, survives full-screen and deactivation) and composes a
container holding the hosting view full-bleed with the interaction view pinned
on top by Auto Layout. Wires the interaction view's `onDrag` to
`movePanel`/`resizePanel`, then orders the panel out so it starts hidden. The
`[weak self]` closures avoid a retain cycle between controller and view.
""",
    ("CaptionOverlayController.swift", "func show("): """
Updates the hosting view's root with the new lines, provisional text, question,
pending count, and font size, then decides placement: on a display change it
restores that display's saved frame, otherwise if the panel was hidden it
re-clamps the existing frame to the (possibly resized) screen, and finally
orders the panel front without activating.
""",
    ("CaptionOverlayController.swift", "func hide("): """
Persists the last frame before ordering the nonactivating panel out. Hiding does
not destroy the window or SwiftUI tree, so later show is fast and restores
geometry.
""",
    ("CaptionOverlayController.swift", "resetFrame"): """
Selects the target display, removes only that display's saved frame, and applies
the computed default. Other projector/laptop geometry remains remembered.
""",
    ("CaptionOverlayController.swift", "windowDidMove"): """
Window-delegate callback that persists user-driven movement. Programmatic frame
changes are filtered by `isApplyingFrame` inside `persistFrame`.
""",
    ("CaptionOverlayController.swift", "windowDidResize"): """
Persists user-driven size changes through the same guarded path as movement.
""",
    ("CaptionOverlayController.swift", "func movePanel"): """
Applies a move drag: caches the frame at gesture start (so the absolute
translation maps to a stable origin), offsets that origin by the translation,
then clamps the proposed rect to the screen's visible frame. Width and height
are preserved; only the origin moves.
""",
    ("CaptionOverlayController.swift", "func resizePanel"): """
Applies a resize drag from the lower-right corner: anchors the top edge
(`start.maxY`) so the box grows downward and rightward, clamps new width/height
between the minimum size and the room left to the screen margins, and re-derives
the origin's y from the anchored top. Height uses `start.height -
translation.height` because the corner is at the bottom.
""",
    ("CaptionOverlayController.swift", "finishInteraction"): """
Clears the gesture's cached origin so the next drag starts from the then-current
frame, and commits geometry to preferences once rather than on a stale origin.
""",
    ("CaptionOverlayController.swift", "restoredFrame"): """
Reads the selected display's serialized `NSRect`, falls back to first-run
geometry when absent, and always clamps old preferences to the display's current
visible bounds.
""",
    ("CaptionOverlayController.swift", "geometryKey"): """
Namespaces persisted rectangles by stable Core Graphics display ID, allowing
different laptop/projector layouts to retain independent overlay positions.
""",
    ("CaptionOverlayController.swift", "func applyFrame"): """
Sets the panel frame while holding `isApplyingFrame` true so the resulting
`windowDidMove`/`windowDidResize` delegate calls do not persist. It also clamps
the panel's `maxSize` to the visible frame minus margins on every apply, so the
user can never drag the box larger than the screen allows.
""",
    ("CaptionOverlayController.swift", "func defaultFrame"): """
Computes the first-run overlay rect: width clamped to 600-1200pt (or screen
width minus margins), a fixed 220pt height, horizontally centered and seated
48pt above the bottom of the visible frame. This is the layout `resetFrame`
returns to.
""",
    ("CaptionOverlayController.swift", "func clamped"): """
The universal frame constraint: shrinks width/height to fit the visible frame
minus margins (never below the minimum size, itself capped to available space),
then pins the origin so the whole box stays inside the margin-inset area. Every
placement path (restore, move, resize, show) funnels through this, so no code
can leave the panel partly off a display.
""",
    ("CaptionOverlayController.swift", "func persistFrame"): """
Writes the panel's current frame to UserDefaults under the selected display's
geometry key, but only when not mid-`applyFrame` and a display is selected. The
`isApplyingFrame` guard is what prevents the delegate's move/resize callbacks
from re-saving frames the controller just set programmatically.
""",
    ("CaptionOverlayController.swift", "func scrollToBottom"): """
Scrolls the caption list to the bottom anchor on the next main-queue tick. The
`DispatchQueue.main.async` defer lets SwiftUI finish applying the new lines
before scrolling, so the newest caption is reliably in view rather than
scrolling against stale layout. Called on appear and on every content change.
""",
    ("CaptionOverlayController.swift", "struct CaptionOverlayView"): """
Pure SwiftUI rendering of finalized lines, provisional text, question card,
pending badge, and handles. Inputs are immutable values supplied by the
controller; window ownership and geometry remain in AppKit.
""",
    ("CaptionOverlayController.swift", "captionText"): """
Creates unrestricted multiline caption text with vertical intrinsic sizing.
`fixedSize(horizontal:false, vertical:true)` prevents the old ellipsis behavior
while still wrapping to panel width.
""",
    ("CaptionOverlayController.swift", "questionCard"): """
Places the presented question in a visually distinct, independently scrollable
orange card capped at 130 points, so a long question cannot push live captions
out of the overlay.
""",
    ("CaptionOverlayController.swift", "extension NSScreen"): """
Extracts the stable numeric display ID from AppKit's device-description
dictionary for geometry persistence.
""",
    ("ClassroomAppModel.swift", "func pauseOrResume"): """
Toggles between listening and paused on the value-type session: pausing gates
audio input off via the `audioInputEnabled` mutex and flushes buffered audio so
no half-utterance leaks across the pause, while resuming re-enables input. Each
branch guards on the session's own transition succeeding before mutating, then
refreshes the overlay. No-ops in any other phase.
""",
    ("ClassroomAppModel.swift", "func clearSession"): """
Tears down a finished session: stops capture, gates audio off, cancels the
commit, silence-flush, and correction-worker tasks, drops pending corrections,
stops the active Voxtral backend, and resets every live counter, error, and
overlay-clear flag back to the Ready baseline. Guarded so it cannot run while a
session is active or transitioning.
""",
    ("ClassroomAppModel.swift", "func noteEmbeddedVoiceActivity"): """
Implements silence-based commit for the embedded backend: any audio frame above
the 0.06 level threshold (re)arms a 900ms timer, and if no louder frame arrives
before it fires, flushes Voxtral with `finalizeCaption: true`. Effectively each
trailing 900ms of silence after speech finalizes a caption. The task re-guards
on still-listening and still-embedded before flushing.
""",
    ("ClassroomAppModel.swift", "func warmCorrectionServer"): """
Pre-launches the Gemma MLX server in the background so the first correction is
not stalled by cold start. Guards on correction being enabled and no warmup
already running, ensures the server is ready, and on success marks it ready,
resolves its process identity, and clears errors; failures surface in
`correctionError`.
""",
    ("ClassroomAppModel.swift", "func enqueueCorrection"): """
Appends a segment to the pending-correction queue keyed by its UUID and current
mode, but only if the segment is `queued`, and rejects with `failCorrection`
when the queue already holds 8 entries (back-pressure so a slow Gemma cannot
grow an unbounded backlog). Updates the published queue depth and kicks the
worker.
""",
    ("ClassroomAppModel.swift", "func failCorrection"): """
Marks a segment's correction failed with a message on the value-type session,
writes it back, and refreshes the overlay. The session's own `failCorrection`
preserves the segment's `rawText`, so a failed correction falls back to the
uncorrected caption rather than losing it.
""",
    ("ClassroomAppModel.swift", "func waitForCorrections"): """
Blocks the stop sequence until the correction worker drains or a 60-second
deadline passes; on timeout it cancels the worker, fails every still-pending
segment with a timeout message, and zeroes the queue depth. This is what lets
`stopSession` guarantee the archive captures corrected text without hanging
forever on a stuck server.
""",
    ("ClassroomAppModel.swift", "func gemmaConfiguration"): """
Validates and returns the Gemma server triple (executable, model path,
endpoint), throwing `invalidEndpoint` unless the endpoint is http on
127.0.0.1/localhost with an explicit port. This is a hard loopback-only guard so
a correction request can never be aimed at a remote host.
""",
    ("ClassroomAppModel.swift", "func toggleIPhoneSharing"): """
Starts or stops the local caption web server. Stopping also disables question
submissions first; starting clears any stale pairing URL, sets status to
`.starting`, launches the server, and immediately publishes the current caption
snapshot so a phone that connects sees content right away.
""",
    ("ClassroomAppModel.swift", "func toggleStudentQuestions"): """
Enables or disables anonymous student question submissions on the caption
server, but refuses (setting a `.failed` status) unless iPhone sharing is
already active, since questions ride the same server.
""",
    ("ClassroomAppModel.swift", "func presentNextStudentQuestion"): """
Pops the oldest pending question into `presentedStudentQuestion` (or nil if the
queue is empty) and refreshes the overlay, forcing it visible only when a
question was actually presented. The popped question leaves the pending queue.
""",
    ("ClassroomAppModel.swift", "func receiveStudentQuestion"): """
Appends an inbound `SubmittedClassroomQuestion` to the pending queue (capped at
100 to bound memory against spam) and refreshes the overlay so the pending badge
updates. Runs on the main actor via the server's question callback.
""",
    ("ClassroomAppModel.swift", "func publishRemoteCaptions"): """
Builds and pushes a `RemoteCaptionSnapshot` to connected phones, bumping a
monotonic revision (wrapping add) each call so clients can detect staleness.
Without explicit lines it recomputes the same last-3 visible, sequence-filtered
lines and clear-aware provisional text the local overlay uses. No-ops entirely
when iPhone sharing is inactive.
""",
    ("ClassroomAppModel.swift", "func applyOverlayVoiceCommand"): """
Executes a recognized spoken overlay command. Show/hide directly drive the
overlay; clear records that the overlay should resume after the next caption,
sets a minimum-visible sequence so already-shown lines stay hidden, marks a
finalization pending, hides the overlay, and (on provisional text) forces a
caption boundary. NextQuestion and dismissQuestion delegate to the question
methods.
""",
    ("ClassroomAppModel.swift", "func diagnosticsSettingChanged"): """
Starts or stops the 1Hz diagnostics poller. When on it samples the app footprint
immediately, resolves the Gemma process identity, then loops every second
updating app and (if known) Gemma memory footprints via `ProcessMemory`. When
off it cancels the task.
""",
    ("ClassroomAppModel.swift", "func shutdown"): """
App-teardown hook that cancels the warmup, correction-worker, and diagnostics
tasks and stops both the caption (iPhone sharing) server and the Gemma server.
Releases the external processes and network listeners the model owns.
""",
    ("ProcessMemory.swift", "enum ProcessMemory"): """
A stateless namespace for reading a process's resident memory via the Darwin
`proc_pidinfo` API. The diagnostics panel uses it to report both the app's own
footprint and the separate Gemma MLX server's.
""",
    ("ProcessMemory.swift", "residentSizeBytes"): """
Calls `proc_pidinfo(PROC_PIDTASKINFO)` into a `proc_taskinfo` struct and returns
its `pti_resident_size`, or nil if the call does not return the exact expected
struct size (which is how this API signals failure or a denied/dead pid). The
size-equality check is the standard `proc_pidinfo` success test.
""",

    # --- Network server (security), Gemma controller and prompts ------------
    ("LocalCaptionServer.swift", "struct RemoteCaptionSnapshot"): """
The Codable wire payload sent over Server-Sent Events to each phone: the
finalized caption lines, an optional in-progress provisional line, a flag for
whether a capture session is live, and a monotonically rising revision.
Equatable lets the publisher skip redundant sends. It is a plain value type, so
encoding it with JSONEncoder is the entire serialization contract.
""",
    ("LocalCaptionServer.swift", "struct SubmittedClassroomQuestion"): """
The value handed to the app when a student question clears all validation and
rate limits: a fresh UUID, the normalized text, and the acceptance timestamp. It
carries no source identifier or ticket, so nothing that could deanonymize the
asker leaves the server boundary.
""",
    ("LocalCaptionServer.swift", "enum LocalCaptionServerStatus"): """
The dashboard-facing lifecycle of caption sharing. Associated `URL` values
exist only after listener readiness; `failed` carries presentation text rather
than a Network.framework object. Because this is a `Sendable` value, it can
leave the server queue without exposing mutable listener state.
""",
    ("LocalCaptionServer.swift", "enum StudentQuestionServerStatus"): """
Question intake has a separate lifecycle because it can be disabled while the
caption viewer remains active. The ready URL contains the independent student
capability, never the viewer token, so the type separation mirrors the security
separation.
""",
    ("LocalCaptionServer.swift", "enum CaptionSharingSecurity"): """
The caseless namespace holding every security constant and the three pure
crypto/sanitization helpers, so limits live in one auditable place: 32-byte
tokens, an 8 KiB request cap, a 2 KiB / 500-character question cap, 256
concurrent tickets, a 4-hour ticket life, and the layered rate-limit windows
(10 s per ticket, 8 per source per 5 min, 30 global per minute).
""",
    ("LocalCaptionServer.swift", "makeToken"): """
Mints a 256-bit secret by drawing tokenByteCount bytes from the system CSPRNG
via SecRandomCopyBytes and hex-encoding them, so the pairing/student tokens and
per-student tickets are unguessable. It throws rather than falling back to a weak
source if the draw fails, so a caller never proceeds with a predictable token.
""",
    ("LocalCaptionServer.swift", "tokensMatch"): """
Constant-time-ish token comparison: it UTF-8-encodes both strings, rejects
immediately on a length mismatch, then ORs the XOR of every byte pair into an
accumulator that is only zero when all bytes match. Avoiding an early return
inside the loop denies a timing oracle that could leak the token byte-by-byte.
""",
    ("LocalCaptionServer.swift", "normalizedQuestion"): """
Sanitizes untrusted student text before it is ever surfaced: it splits on
whitespace and newlines, drops empties, rejoins with single spaces, then rejects
the result if it is empty, exceeds maximumQuestionCharacters, or contains any
Unicode control character. Returning nil signals the caller to answer 422, so
control bytes and oversized input never reach the moderation queue or the model.
""",
    ("LocalCaptionServer.swift", "class LocalCaptionServer"): """
Owns the complete local-server state machine. `@unchecked Sendable` is a promise
the compiler cannot verify; safety comes from confining every mutable field and
Network.framework callback to the private serial queue. Public methods transfer
commands or immutable values onto that queue instead of touching state directly.
""",
    ("LocalCaptionServer.swift", "struct StudentTicket"): """
Queue-confined authorization state issued after the page capability is
presented. It records the source observed by the Mac, an absolute expiry, and
that ticket's accepted submission times. Tickets are neither persisted nor
forwarded to the application model.
""",
    ("LocalCaptionServer.swift", "init("): """
Injects three escaping `@Sendable` callbacks and the listening port. `@escaping`
means the server retains each closure after initialization; `@Sendable` makes
its captures part of Swift's concurrency checking. Default no-op question
callbacks keep caption-only construction free of optional closure branches.
""",
    ("LocalCaptionServer.swift", "func stop("): """
Schedules teardown on the owner queue. The call returns before cancellation
necessarily completes, but ordering with prior publishes and later starts is
deterministic because every operation enters the same serial queue.
""",
    ("LocalCaptionServer.swift", "func setQuestionSubmissionsEnabled("): """
Transfers one Boolean command to the queue-owned implementation. Credential
rotation and ticket clearing therefore cannot race an incoming question request
with a main-actor write to `questionsEnabled`.
""",
    ("LocalCaptionServer.swift", "func startOnQueue("): """
Performs restart as one queue transaction: discard old state, report starting,
mint a viewer capability, configure Wi-Fi TCP and Bonjour, install callbacks,
and start the listener. It does not publish a URL yet because neither listener
readiness nor an advertisable local address has been established.
""",
    ("LocalCaptionServer.swift", "func stopOnQueue("): """
Cancels heartbeat, stream, ordinary connections, and listener before clearing
their state. Both capabilities and every ticket/rate window are destroyed, so a
QR photographed before stop cannot authorize the next server run.
""",
    ("LocalCaptionServer.swift", "handleListenerState"): """
Turns Network.framework states into application states. On `.ready` it chooses
a Wi-Fi IPv4 address and constructs the capability URL; on `.failed` it reports
the error and tears down. Binding success and finding a browser-reachable
address are deliberately treated as separate conditions.
""",
    ("LocalCaptionServer.swift", "func accept("): """
Admits a new TCP connection, enforcing a hard ceiling of 64 concurrent
connections by cancelling anything beyond it to blunt connection-flood abuse. It
records the connection, derives a stable source ID from the peer endpoint for
per-source rate limiting, wires a state handler that prunes tracking on
failure/cancel, and starts the incremental request read.
""",
    ("LocalCaptionServer.swift", "handleStudentRequest"): """
The student-feature router, returning true once it owns a request so the caption
path is bypassed. It claims only /student, /student-ticket, and /questions; if
the feature is disabled it 404s to hide its existence. GET /student and POST
/student-ticket each require a tokensMatch against the student token; POST
/questions additionally demands a JSON content-type and a ticket query item.
""",
    ("LocalCaptionServer.swift", "setQuestionSubmissionsEnabledOnQueue"): """
Enabling questions mints a fresh student capability and clears every previous
ticket and rate window; disabling destroys the same state. The helper publishes
a URL only when the caption server has already discovered a host, so it cannot
advertise a half-constructed capability.
""",
    ("LocalCaptionServer.swift", "updateStudentQuestionURL"): """
Projects queue-owned host, enablement, and token state into a dashboard status.
Keeping URL construction here prevents callers from combining a current host
with a stale student token after restart or disablement.
""",
    ("LocalCaptionServer.swift", "issueStudentTicket"): """
Issues one rate-limit ticket per request: it first sweeps expired tickets, then
refuses with 503 once maximumTickets live tickets exist, capping memory and
enrollment. A fresh makeToken value keys a StudentTicket recording the source ID,
a now+ticketLifetime expiry, and an empty submission history. A failed token draw
degrades to 503 rather than issuing a weak ticket.
""",
    ("LocalCaptionServer.swift", "submitQuestion"): """
Validates and rate-limits one question. The ticket must exist, be unexpired, and
bind to the same sourceID that obtained it (else 401), preventing ticket sharing
across peers. The body is JSON-decoded and run through normalizedQuestion (else
422). Three sliding windows are checked: a 10 s per-ticket gap, 8 per source per
5 min, 30 globally per minute, plus a 100-question lifetime cap; any breach
yields 429. Only on success is the question forwarded with a 202.
""",
    ("LocalCaptionServer.swift", "beginEventStream"): """
Establishes the single SSE caption stream. If streamConnection is already set it
rejects with 409, enforcing exactly one connected phone at a time. Otherwise it
claims the connection, writes the SSE headers (nosniff, no-referrer, a 1 s retry
hint), immediately replays the last snapshot so a late joiner is not blank,
starts the heartbeat timer, and reports clientConnected.
""",
    ("LocalCaptionServer.swift", "startHeartbeat"): """
Creates a repeating dispatch timer on the server queue and sends SSE comment
frames during quiet periods. Comments carry no application event, but periodic
bytes keep the TCP path alive. Cancelling an existing timer first makes stream
replacement and teardown idempotent.
""",
    ("LocalCaptionServer.swift", "removeStreamConnection"): """
Clears the registered SSE stream only if the callback belongs to that exact
`NWConnection`. This identity check prevents a delayed cancellation from an old
phone from erasing a newer connection; the heartbeat stops when no stream
remains.
""",
    ("LocalCaptionServer.swift", "private func send("): """
JSON-encodes one immutable snapshot and frames it as an SSE `event:`/`data:`
record terminated by a blank line. A missing viewer is a no-op. Transport
failure cancels the connection, whose state callback performs queue-owned
cleanup.
""",
    ("LocalCaptionServer.swift", "func respond("): """
Writes a complete one-shot HTTP/1.1 response and closes: it frames the body with
Content-Length, Connection: close, and no-store caching, and stamps a strict
security header set on every reply, including a CSP that forbids remote
script/style/img/object and pins base-uri and frame-ancestors to none, plus
nosniff and X-Frame-Options DENY.
""",
    ("LocalCaptionServer.swift", "func contentLength("): """
Parses the Content-Length header into a non-negative Int, defaulting to 0 when
absent or unparseable. receiveRequest uses it to decide when a body is fully
buffered and to reject anything over maximumQuestionBytes, so a malformed or
hostile length never causes an over-read.
""",
    ("LocalCaptionServer.swift", "func headers("): """
Parses only the header grammar needed by the generated clients. Names are
trimmed and lowercased because HTTP field names are case-insensitive. Repeated
fields, folding, chunked coding, and general proxy behavior are intentionally
outside this small server's protocol.
""",
    ("LocalCaptionServer.swift", "func queryValue("): """
Delegates query parsing and percent-decoding to `URLComponents` instead of
splitting raw strings. The generated routes emit one value per capability or
ticket name, so returning the first matching item is a complete contract.
""",
    ("LocalCaptionServer.swift", "func sourceID("): """
Derives a coarse rate-limit key from the peer endpoint. It is not student
identity: NAT may merge users and address changes may split one user. The value
never leaves queue-owned abuse-control tables.
""",
    ("LocalCaptionServer.swift", "wifiIPv4Address"): """
Discovers the LAN IPv4 address to advertise by walking getifaddrs, skipping
interfaces that are down, loopback, or non-IPv4. It prefers en0 (the Wi-Fi
interface) and otherwise returns the first other candidate. `defer freeifaddrs`
guarantees the C allocation is released on every exit path.
""",
    ("LocalCaptionServer.swift", "studentQuestionPage"): """
Returns the complete HTML/CSS/JavaScript student client, embedding the student
capability through JSON encoding rather than string concatenation. JavaScript
exchanges it for a source-bound ticket and POSTs question JSON; no route exposes
caption, microphone, overlay, or model control.
""",
    ("LocalCaptionServer.swift", "browserPage"): """
Returns the read-only caption viewer. Its JavaScript opens an `EventSource`
carrying the viewer capability, replaces the rendered snapshot on each event,
and relies on browser reconnection. The embedded page and Swift routes therefore
form one protocol implementation that evolves together.
""",
    ("GemmaServerController.swift", "enum GemmaServerError"): """
The typed failure set for the locally launched MLX-LM server, conforming to
LocalizedError so each case renders a user-facing string: executableMissing
names the bad path, launchFailed wraps the spawn error or a non-zero exit, and
unavailable means the health endpoint never went green within the startup window.
""",
    ("GemmaServerController.swift", "class GemmaServerController"): """
Main-actor owner of the optional MLX-LM child and its health-check session.
Actor isolation serializes launch and termination with UI workflows, while
health probes suspend instead of blocking the event loop. Only the child stored
in `process` is considered owned and eligible for termination.
""",
    ("GemmaServerController.swift", "init("): """
Creates an ephemeral session with one-second request and two-second resource
timeouts. Individual failed probes therefore return quickly; `ensureReady`
supplies the separate 45-second model-loading deadline around repeated probes.
No cookies or persistent cache are useful for loopback health checks.
""",
    ("GemmaServerController.swift", "func launch("): """
Spawns the owned mlx_lm.server child once. It verifies the path is executable
(else executableMissing) and the endpoint yields host and port, then runs it with
deterministic flags: temp 0 and disabled thinking for reproducible proofreading,
max-tokens 384, single decode/prompt concurrency, and WARNING logging. stdout and
stderr go to /dev/null. A run failure is rethrown as launchFailed.
""",
    ("GemmaServerController.swift", "processIdentifier"): """
Resolves the server's PID, preferring the live owned Process's identifier. When
the app did not spawn the server it falls back to running `lsof -nP -tiTCP:port
-sTCP:LISTEN`, taking the first output line as the listener's PID. Any lsof
failure, non-zero exit, or unparseable output yields nil rather than a wrong PID.
""",
    ("GemmaServerController.swift", "func stop("): """
Terminates the owned server: if no process is tracked or it already exited it
just clears the reference, otherwise it sends SIGTERM via terminate and drops the
reference. It only ever kills a process this controller launched, never one
discovered through the lsof fallback.
""",
    ("GemmaServerController.swift", "func isHealthy("): """
Probes readiness with a GET to v1/models on the short-timeout ephemeral health
session, returning true only for a 2xx HTTPURLResponse. Any thrown error,
non-HTTP response, or non-2xx status maps to false, so polling treats
connection-refused during startup as simply not-yet-ready.
""",
    ("GemmaCorrectionService.swift", "struct CompletionRequest"): """
The OpenAI-style chat-completions request body. It hard-codes temperature 0 and
stream false for deterministic, single-shot proofreading and pins model to
default_model; only messages and the per-segment max_tokens vary. The constant
fields have defaults, so they are encoded without being passed at the call site.
""",
    ("GemmaCorrectionService.swift", "enum GemmaCorrectionError"): """
Separates malformed endpoint construction, structurally invalid success
payloads, and non-2xx server replies carrying status plus body. Typed errors let
the coordinator preserve control flow while `LocalizedError` supplies stable
dashboard text.
""",
    ("GemmaCorrectionService.swift", "actor GemmaCorrectionService"): """
An actor is a reference type whose mutable state is isolated by a Swift
executor. External calls require `await`, preventing concurrent corrections
through this instance. Even though its stored fields are immutable, actor
isolation documents the intended serialized workload for the large local model.
""",
    ("GemmaCorrectionService.swift", "struct Message"): """
The smallest chat-protocol unit: role and content. It remains a wire value rather
than a domain enum because the OpenAI-compatible endpoint owns role vocabulary.
`Codable` gives symmetric, compiler-checked JSON field names.
""",
    ("GemmaCorrectionService.swift", "struct CompletionResponse"): """
The decoded response envelope: an array of choices and optional usage. It
surfaces each choice's reasoningContent alongside content so correct() can reject
any reply where the model leaked chain-of-thought instead of returning a clean
caption. Nested CodingKeys remap the server's snake_case to camelCase.
""",
    ("GemmaCorrectionService.swift", "sharedPrompt"): """
The base system prompt and core prompt-injection defense: it frames the caption
as untrusted quoted data that is never an instruction, and forbids answering,
obeying, continuing, explaining, summarizing, or translating it. It scopes the
model to formatting-only corrections, bans LaTeX/Markdown/backtick output, and
states that notation normalization is not license to solve an expression, so a
captioned question is returned only proofread.
""",
    ("GemmaCorrectionService.swift", "standardPrompt"): """
The conservative mode appended to sharedPrompt: it permits normalizing only
common directly-spoken notation when the conversion is certain and aids
readability, and tells the model to prefer plain corrected prose when a symbolic
rendering would be ambiguous. Because it only narrows behavior, it cannot
reintroduce the answer-the-question capability the shared rules removed.
""",
    ("GemmaCorrectionService.swift", "sciencePrompt"): """
The aggressive mode appended to sharedPrompt: it directs broad conversion of
unambiguous spoken math/logic/probability/code into a fixed catalog of
established Unicode symbols, while still forbidding inventing, solving,
simplifying, or completing a formula. It bars fabricated placeholder set names,
so expanded symbol freedom never becomes permission to compute an answer.
""",
    ("GemmaCorrectionService.swift", "func systemPrompt("): """
Assembles the effective system prompt by concatenating sharedPrompt with either
sciencePrompt or standardPrompt based on the request mode. The shared safety
block always comes first, so the mode-specific notation rules extend rather than
override the injection defenses.
""",
    ("GemmaCorrectionService.swift", "init(endpoint:"): """
Stores the already validated loopback endpoint and configures an ephemeral
session with bounded request and resource deadlines. The initializer does not
rewrite hosts or ports; endpoint policy remains the app model's responsibility.
""",

    # --- Voxtral streaming runtime, audio front end, tokenizer, safetensors,
    #     C bridge, embedded service ----------------------------------------
    ("voxtral.h", "#define VOX_SAMPLE_RATE"): """
The audio ABI is fixed at 16 kHz; every upstream capture/file path must convert
to this rate before feeding the model.
""",
    ("voxtral.h", "#define VOX_MEL_BINS"): """
Each acoustic frame contains 128 Mel-band values, matching checkpoint training.
""",
    ("voxtral.h", "#define VOX_HOP_LENGTH"): """
Successive analysis windows advance 160 samples, giving a 10 ms/100 Hz Mel
frame clock at 16 kHz.
""",
    ("voxtral.h", "#define VOX_WINDOW_SIZE"): """
Each spectral window spans 400 samples, or 25 ms, so adjacent frames overlap.
""",
    ("voxtral.h", "#define VOX_FRAME_RATE"): """
The audio-language adapter/decoder receives 12.5 positions per second after all
front-end downsampling; this is distinct from the 100 Hz Mel clock.
""",
    ("voxtral.h", "#define VOX_LOG_MEL_MAX"): """
Checkpoint-specific upper clamp used before log-Mel normalization.
""",
    ("voxtral.h", "#define VOX_ENC_DIM"): """
Width of each encoder residual vector and normalization weight.
""",
    ("voxtral.h", "#define VOX_ENC_LAYERS"): """
Number of stacked audio-transformer layers and encoder KV-cache planes.
""",
    ("voxtral.h", "#define VOX_ENC_HEADS"): """
Number of encoder query heads.
""",
    ("voxtral.h", "#define VOX_ENC_KV_HEADS"): """
Encoder key/value head count; here it equals query heads, unlike grouped-query
attention in the decoder.
""",
    ("voxtral.h", "#define VOX_ENC_HEAD_DIM"): """
Per-head Q/K/V width. Projection width is heads multiplied by this dimension.
""",
    ("voxtral.h", "#define VOX_ENC_HIDDEN"): """
Intermediate width of the encoder's gated feed-forward network.
""",
    ("voxtral.h", "#define VOX_ENC_WINDOW"): """
Maximum retained encoder attention window before rolling-cache compaction.
""",
    ("voxtral.h", "#define VOX_ENC_NORM_EPS"): """
Numerical epsilon added inside encoder RMS normalization.
""",
    ("voxtral.h", "#define VOX_DOWNSAMPLE"): """
Number of encoder positions grouped by the modality adapter into one decoder
audio position.
""",
    ("voxtral.h", "#define VOX_DEC_DIM"): """
Decoder residual/token-embedding width.
""",
    ("voxtral.h", "#define VOX_DEC_LAYERS"): """
Number of language-transformer layers and decoder cache planes.
""",
    ("voxtral.h", "#define VOX_DEC_HEADS"): """
Number of decoder query heads.
""",
    ("voxtral.h", "#define VOX_DEC_KV_HEADS"): """
Eight K/V heads serve 32 query heads, implementing grouped-query attention and
reducing cache memory.
""",
    ("voxtral.h", "#define VOX_DEC_HEAD_DIM"): """
Per-head decoder attention width.
""",
    ("voxtral.h", "#define VOX_DEC_HIDDEN"): """
Intermediate width of the decoder SwiGLU feed-forward network.
""",
    ("voxtral.h", "#define VOX_DEC_WINDOW"): """
Architectural decoder context limit; the live stream may choose a smaller
restart threshold for latency.
""",
    ("voxtral.h", "#define VOX_DEC_NORM_EPS"): """
Decoder RMSNorm epsilon.
""",
    ("voxtral.h", "#define VOX_VOCAB_SIZE"): """
Number of decoder output/token-embedding rows, including control tokens.
""",
    ("voxtral.h", "#define VOX_ADA_NORM_DIM"): """
Bottleneck width of each layer's delay-conditioned adaptive norm MLP.
""",
    ("voxtral.h", "#define VOX_ROPE_THETA"): """
Base frequency scale for decoder rotary position embeddings.
""",
    ("voxtral.h", "vox_enc_layer_t"): """
All weights for one audio-transformer layer. Large matrices may be owned FP32
buffers or borrowed mapped BF16 pointers; comments record exact shapes and the
encoder's unusual bias pattern (Q/V/output biased, K not biased).
""",
    ("voxtral.h", "vox_encoder_t"): """
Owns the two convolutional stem layers, fixed array of transformer layers, and
final normalization for acoustic encoding.
""",
    ("voxtral.h", "vox_dec_layer_t"): """
One language layer's delay-conditioned normalization, grouped-query attention,
and gated feed-forward weights. Decoder projections have no biases.
""",
    ("voxtral.h", "vox_decoder_t"): """
Owns shared token embedding/output-projection weights, all decoder layers, and
the final norm.
""",
    ("voxtral.h", "vox_adapter_t"): """
Two learned projections mapping grouped encoder features into the decoder's
3,072-dimensional embedding space.
""",
    ("voxtral.h", "vox_ctx_t"): """
Long-lived model context: immutable weights/mapping, shared GPU resources,
decoder and encoder rolling caches, delay conditioning, and reusable scratch.
Streams borrow this object; it must outlive them.
""",
    ("voxtral.h", "#define VOX_MAX_ALT"): """
Compile-time ceiling for alternative-token diagnostics per decoded position.
""",
    ("voxtral.h", "vox_load"): """
Loads model mapping, tokenizer-independent weights, caches, and acceleration
resources from one model directory; returns owned context or null.
""",
    ("voxtral.h", "vox_free"): """
Releases every context-owned allocation after all borrowing streams are gone.
""",
    ("voxtral.h", "vox_set_delay"): """
Converts requested milliseconds to the model's 80 ms delay-token grid and
recomputes decoder time conditioning.
""",
    ("voxtral.h", "typedef struct vox_stream"): """
Opaque mutable state for one incremental transcription timeline.
""",
    ("voxtral.h", "vox_stream_init"): """
Allocates per-stream front-end, encoder/adapter, decoder, token queue, and
recovery state while borrowing the model context.
""",
    ("voxtral.h", "vox_stream_feed"): """
Accepts mono 16 kHz float samples, advances every newly stable stage, and queues
text pieces without finalizing input.
""",
    ("voxtral.h", "vox_stream_finish"): """
Adds terminal feature padding, processes all remaining stable positions, and
ends the stream.
""",
    ("voxtral.h", "vox_stream_get("): """
Dequeues best-token text pointers into caller storage. Piece memory remains
stream-owned until free.
""",
    ("voxtral.h", "vox_stream_text_token_count"): """
Returns cumulative generated decoder tokens for throughput diagnostics.
""",
    ("voxtral.h", "vox_stream_decoder_milliseconds"): """
Returns cumulative decoder execution time, excluding model load and front-end
work.
""",
    ("voxtral.h", "vox_stream_set_alt"): """
Configures how many near-best token alternatives to retain and their probability
distance cutoff.
""",
    ("voxtral.h", "vox_stream_get_alt"): """
Dequeues positions as fixed groups of best token plus optional alternatives.
""",
    ("voxtral.h", "vox_set_processing_interval"): """
Converts a seconds policy into the minimum new-Mel threshold between encoder
runs, trading responsiveness against GPU batching efficiency.
""",
    ("voxtral.h", "vox_stream_set_continuous"): """
Enables decoder recovery/restart behavior required for an unbounded lecture.
""",
    ("voxtral.h", "vox_stream_set_max_decode_context"): """
Sets the live restart threshold that bounds decoder attention cost.
""",
    ("voxtral.h", "vox_stream_flush"): """
Runs currently buffered stable work regardless of normal batching interval while
keeping the stream open.
""",
    ("voxtral.h", "vox_stream_free"): """
Destroys one stream's mutable buffers and token storage; the borrowed model
remains alive.
""",
    ("voxtral.h", "vox_transcribe("): """
Offline convenience wrapper loading WAV samples and driving the streaming API;
returns caller-owned text.
""",
    ("voxtral.h", "vox_transcribe_audio"): """
Offline wrapper for an already decoded float waveform.
""",
    ("voxtral.h", "vox_transcribe_stdin"): """
CLI wrapper that detects WAV versus raw PCM input and transcribes to EOF.
""",
    ("voxtral.h", "vox_encoder_forward("): """
Full nonincremental acoustic encoder path returning owned embeddings.
""",
    ("voxtral.h", "vox_encoder_forward_incremental"): """
Processes only new post-convolution positions using the rolling encoder cache.
""",
    ("voxtral.h", "vox_adapter_forward"): """
Groups/downsamples encoder rows and projects them into decoder embedding space.
""",
    ("voxtral.h", "vox_decoder_forward"): """
Runs one cached autoregressive step and returns the greedy next token ID.
""",
    ("voxtral.h", "vox_decoder_prefill"): """
Processes several prompt/audio embeddings in a batch and seeds decoder caches.
""",
    ("voxtral.h", "vox_decoder_kv_cache_preallocate"): """
Reserves decoder cache capacity before live generation.
""",
    ("voxtral.h", "vox_encoder_kv_cache_preallocate"): """
Reserves encoder cache capacity before live audio.
""",
    ("voxtral.c", "vox_adapter_load"): """
Resolves the two audio-language projection weight tensors by their safetensors
names and stores borrowed bf16 pointers into the mapped file (no copy). Returns
-1 if either tensor is missing, aborting the load. The pointers remain valid only
while the safetensors mapping is open.
""",
    ("voxtral.c", "vox_free"): """
Tears down a context: frees the f32 weight buffers converted out of safetensors
(conv stem, per-layer norms and biases, decoder ada/norm rows), releases KV
caches (Metal-shared free or plain free per build and the shared flag), the
persistent encoder/decoder scratch, ada_scale, and finally closes the safetensors
mapping. Borrowed bf16 pointers are owned by the mapping and not freed here.
Null-safe and idempotent.
""",
    ("voxtral.c", "stream_classify_token"): """
Classifies a sampled token into EOS, CONTROL (id below the 1000 text range),
INVALID (text-range id whose decode is NULL or empty), or TEXT. The empty-decode
case matters because Tekken token 1000 is byte 0x00, which as a C string is
empty; treating it as non-text prevents decode activity with no visible output
from masquerading as progress.
""",
    ("voxtral.c", "stream_conv_stem"): """
Runs new mel frames through the two-layer conv stem incrementally and returns a
newly-allocated [out_len, 1280] buffer of post-conv positions (caller frees; NULL
when nothing emerges). Conv1 has stride 2, so an odd conv0 count is saved as
conv0_residual and prepended next chunk to avoid corrupting alignment forever.
mel_tail and conv0_tail carry boundary context so causal convolutions match a
non-streaming pass.
""",
    ("voxtral.c", "stream_adapter_compact"): """
Drops adapter tokens the decoder has already consumed by memmove-ing the
surviving tail to the front of adapter_buf and advancing adapter_pos_offset by
the consumed count. Keeps physical buffer indices small while gen_pos and
total_adapter stay in an absolute logical coordinate; phys_pos is always the
logical position minus adapter_pos_offset.
""",
    ("voxtral.c", "stream_reset_decoder_state"): """
Hard-resets only the decoder side: zeroes the decoder KV cache length/offset,
drops the adapter backlog and its logical offset, rewinds gen_pos, and re-primes
prev_token to BOS with the streak/eos/prompt flags cleared. Used on EOS, KV
overflow, or a control-token loop so live transcription restarts without
rebuilding the mel/encoder front end.
""",
    ("voxtral.c", "vox_stream_init"): """
Allocates a zeroed stream, loads the Tekken tokenizer, and initializes the
incremental mel context with 32 streaming-pad tokens of leading silence. Sets up
the circular token queue, the decoder scratch, single-best alternative mode, and
the default 2-second processing interval. The returned stream borrows the context
but owns its own tokenizer, mel context, and buffers. On any allocation failure
it tears down partial state and returns NULL.
""",
    ("voxtral.c", "vox_stream_finish"): """
Finalizes a stream: flushes the delay-window padding (shared with
vox_stream_flush), marks finished, and closes the mel front end (right reflect
pad plus last-frame drop). It then forces one final encoder+decoder pass so
trailing tokens behind the delay are emitted. Returns -1 if already finished;
afterward feed/flush are rejected but tokens may still be drained.
""",
    ("voxtral.c", "vox_stream_get"): """
Pops up to max best-token strings from the head of the circular queue, returning
only alts[0] of each position and advancing queue_head. Returns the count
dequeued (0 when empty). The returned pointers are borrowed from the tokenizer
vocab and must not be freed by the caller.
""",
    ("voxtral.c", "vox_stream_free"): """
Optionally prints timing stats, then releases everything the stream owns: mel
context, tokenizer, adapter buffer, token queue, decoder scratch, and conv-stem
boundary buffers. The shared vox_ctx_t is borrowed and not freed here. Must be
called only after the caller has drained all wanted tokens, since the queued
string pointers die with the tokenizer.
""",
    ("voxtral.c", "vox_set_delay"): """
Sets the streaming look-ahead delay in milliseconds (clamped 80..2400), converted
to delay_tokens at 80 ms per token. Because the delay feeds the decoder time
conditioning, it recomputes t_cond and every layer's ada_scale via
vox_update_time_conditioning before returning.
""",
    ("voxtral.c", "vox_compute_time_embedding"): """
Builds the decoder timing embedding for a scalar t_value, matching the vLLM
Mistral time embedding: inverse frequencies decay geometrically over dim/2 bands,
emb = t * inv_freq, and the output is the concatenation [cos(emb), sin(emb)]
written into the caller-owned out of length VOX_DEC_DIM. out must already be sized
to the full decoder dim, since cos fills the low half and sin the high half.
""",
    ("voxtral.c", "vox_update_time_conditioning"): """
Recomputes t_cond from the current delay_tokens and precomputes, per decoder
layer, the ada_scale vector ada_up(GELU(ada_down(t_cond))). The ada_scale buffer
is lazily allocated once into context storage sized VOX_DEC_LAYERS * VOX_DEC_DIM
and reused thereafter; the per-layer matmuls read the borrowed mapped ada_norm
weights. Called at load and whenever the delay changes, so the decoder's per-layer
modulation always reflects the active delay.
""",
    ("voxtral.c", "load_bf16_direct"): """
Resolves an adapter weight tensor by name and returns a borrowed, zero-copy bf16
pointer into the safetensors mapping (via safetensors_get_bf16_direct), or NULL
after logging when the tensor is absent. The returned pointer is owned by the
mapping, not the caller.
""",
    ("voxtral.c", "trim_ascii_whitespace"): """
Strips leading and trailing ASCII whitespace from a C string in place, memmoving
the surviving span to the front and re-terminating with a NUL. Null-safe. Used to
clean the final transcribed text before it is returned to the caller.
""",
    ("voxtral.c", "tok_embed_bf16_to_f32"): """
Expands a single token's embedding row from bf16 to f32 by zero-extending each
16-bit value into the high half of a 32-bit float and copying into dst. Indexes
the borrowed mapped embedding table at token_id * dim; dst is caller scratch of
length dim. Used to add the previous token's embedding onto the adapter output
before each decoder step.
""",
    ("voxtral.c", "enum stream_tok_class"): """
The four-way classification a sampled token can take before the stream decides
what to do with it: TEXT (a non-empty decoded piece), CONTROL (id below the text
range), INVALID (text-range id that decodes to empty, e.g. Tekken token 1000 =
byte 0x00), and EOS. stream_classify_token assigns it; the streak watchdogs and
enqueue logic branch on it.
""",
    ("voxtral.c", "stream_enqueue_token"): """
Appends one position's alternatives array (VOX_MAX_ALT borrowed string pointers,
alts[0] best) to the circular token queue, doubling capacity and re-linearizing
head/tail when full. The stored char pointers are borrowed from the tokenizer's
owned vocab strings, not copied, so they stay valid for the tokenizer's lifetime.
On allocation failure it silently drops the token rather than corrupting the queue.
""",
    ("voxtral.c", "stream_reset_full_state"): """
Full live-stream recovery: tears down and rebuilds the mel context with the
standard 32-token silence left-pad, zeroes all conv-stem boundary buffers
(mel_tail, conv0_tail, conv0_residual, enc_residual) and the encoder KV cache,
then chains into the decoder reset. Returns -1 if the new mel context cannot be
allocated, in which case the caller falls back to a decoder-only reset to keep the
stream alive.
""",
    ("voxtral.c", "stream_fill_alts"): """
Fills the alternatives array for one emitted position: alts[0] is the best token's
decoded piece, and when n_alt > 1 it softmaxes the logits in place and repeatedly
scans the text-range vocabulary for the next-highest tokens, stopping once the
relative distance 1 - p/best_prob exceeds alt_cutoff or n_alt is reached. The
stored strings are borrowed from the tokenizer; the logits buffer is destructively
overwritten with probabilities, which is fine because it is re-filled every step.
""",
    ("voxtral.c", "vox_stream_text_token_count"): """
Returns the running count of emitted text tokens (0 for a NULL stream), a
diagnostic the app pairs with decoder time to compute the live token rate.
""",
    ("voxtral.c", "vox_stream_decoder_milliseconds"): """
Returns the accumulated decoder compute time in milliseconds (0 for a NULL
stream), paired with the text-token count to report tokens-per-decoder-second.
""",
    ("voxtral.c", "vox_stream_set_alt"): """
Configures alternative-token emission: n_alt (clamped to 1..VOX_MAX_ALT) is how
many ranked candidates each position keeps, and cutoff (clamped to 0..1) is the
relative-probability distance past which stream_fill_alts stops adding
alternatives. n_alt = 1 is the default single-best mode.
""",
    ("voxtral.c", "vox_stream_get_alt"): """
Like vox_stream_get but copies n_alt alternative pointers per position into a
row-major out_tokens grid (capped at VOX_MAX_ALT), advancing queue_head per
position consumed. Returns the number of positions dequeued. Each cell is a
borrowed tokenizer string or NULL when no qualifying alternative existed.
""",
    ("voxtral.c", "vox_transcribe_audio"): """
Offline convenience wrapper: spins up a stream, feeds the whole sample buffer,
finishes it, then drains the token queue into a single growing heap string that
the caller owns. The input samples are borrowed (not freed here), and trailing
ASCII whitespace is trimmed before return. Built entirely on the streaming API, so
it shares the same delay/padding behavior as live use.
""",
    ("voxtral.c", "vox_transcribe_stdin"): """
Reads stdin, peeking the first four bytes to choose a path: a RIFF header buffers
the whole file and transcribes it offline (parsing fmt/data chunks inline,
downmixing to mono and resampling to 16 kHz as needed), otherwise stdin is treated
as raw s16le 16 kHz mono and fed in 4096-sample blocks with tokens drained between
reads. Returns a caller-owned, whitespace-trimmed string; the two peeked samples
are fed before the read loop so no input is lost.
""",
    ("voxtral.c", "vox_transcribe"): """
File-path convenience entry: loads a WAV via vox_load_wav, delegates to
vox_transcribe_audio, frees the decoded samples, and returns the caller-owned text
(NULL if the file cannot be loaded). The thinnest offline wrapper over the
streaming core.
""",
    ("voxtral.c", "vox_set_processing_interval"): """
Sets how many new mel frames must accumulate before the encoder fires, derived
from seconds at the fixed 100 fps mel rate (sample_rate/hop = 16000/160), with a
floor of one frame. Larger intervals batch more audio per encoder call for
throughput; smaller intervals lower latency. Mutates only the stream's min_new_mel.
""",
    ("voxtral.c", "vox_stream_set_continuous"): """
Toggles continuous (live) mode, in which the decoder is periodically restarted
once its KV cache passes max_decode_context so per-step attention cost stays
bounded for an unbounded lecture. Off means a single bounded utterance.
""",
    ("voxtral.c", "vox_stream_set_max_decode_context"): """
Sets the decoder KV-cache ceiling (clamped to 250..8000 entries) that, on a
continuous stream, triggers a forced decoder restart to bound per-step attention
cost and keep decoding real-time. Only meaningful when continuous mode is on.
""",
    ("voxtral_audio.h", "vox_load_wav"): """
Loads a supported WAV and returns newly allocated normalized float samples;
`out_n_samples` receives the length. The caller frees the buffer. File I/O is
separate from the in-memory parser so binary parsing can be tested directly.
""",
    ("voxtral_audio.h", "vox_parse_wav_buffer"): """
Parses a bounded RIFF/WAVE byte range and returns owned 16 kHz mono float
samples. Unsupported channel, rate, encoding, or bit-depth combinations are
rejected rather than silently resampled.
""",
    ("voxtral_audio.h", "vox_read_pcm_stdin"): """
Reads raw little-endian signed PCM16 mono from standard input and returns an
owned float array. This supports command-line tools; the GUI uses Core Audio.
""",
    ("voxtral_audio.h", "vox_mel_spectrogram"): """
One-shot front end returning an owned row-major `[frames, 128]` log-Mel matrix.
Streaming callers use `vox_mel_ctx_t`; this function defines equivalent batch
semantics for files and diagnostics.
""",
    ("voxtral_audio.h", "typedef struct vox_mel_ctx"): """
Opaque incremental feature state. It hides retained waveform tails, Mel rows,
FFT/filter workspaces, absolute offsets, and finish state so callers cannot
violate compaction invariants.
""",
    ("voxtral_audio.h", "vox_mel_ctx_init"): """
Allocates incremental state and inserts the requested left padding before real
audio. That padding reproduces the model's trained boundary condition and is not
counted as classroom speech.
""",
    ("voxtral_audio.h", "vox_mel_feed"): """
Copies waveform samples into context storage and computes every newly complete
analysis window. Success means input was accepted; zero new stable frames is a
normal outcome for a short chunk.
""",
    ("voxtral_audio.h", "vox_mel_finish"): """
Adds terminal right padding exactly once and computes the final windows. It
establishes end-of-input, so feeding later samples would violate the context
lifecycle.
""",
    ("voxtral_audio.h", "vox_mel_data"): """
Returns a borrowed pointer to current contiguous Mel rows and writes their local
count. Feed, discard, or free may invalidate the pointer.
""",
    ("voxtral_audio.h", "vox_mel_frame_offset"): """
Returns the absolute frame represented by local row zero after compaction.
Downstream code adds this offset so array movement never resets model position.
""",
    ("voxtral_audio.h", "vox_mel_discard_before"): """
Discards rows older than an absolute boundary, moves the retained suffix, and
advances the frame offset. This bounds memory without changing retained rows'
temporal identity.
""",
    ("voxtral_audio.h", "vox_mel_free"): """
Releases all incremental waveform, feature, FFT, filter, and context storage.
Every borrowed Mel pointer becomes invalid.
""",
    ("voxtral_audio.c", "read_u16"): """
Decodes a little-endian 16-bit WAV field byte by byte, avoiding alignment and
host-endianness assumptions. The parser checks bounds before calling it.
""",
    ("voxtral_audio.c", "read_u32"): """
Decodes a little-endian 32-bit RIFF field without casting an unaligned pointer.
""",
    ("voxtral_audio.c", "vox_load_wav"): """
Reads the file into owned memory, delegates all chunk and format validation to
`vox_parse_wav_buffer`, then frees file bytes. Returned samples have independent
ownership.
""",
    ("voxtral_audio.c", "vox_read_pcm_stdin"): """
Grows a byte buffer while reading stdin, ignores an incomplete trailing byte,
and converts complete `int16_t` values to float. Its input format is the fixed
raw format documented by the CLI.
""",
    ("voxtral_audio.c", "hertz_to_mel"): """
Maps physical frequency to the Mel coordinate used for filter placement.
Changing this formula changes the checkpoint's expected feature distribution.
""",
    ("voxtral_audio.c", "mel_to_hertz"): """
Inverts the selected Mel mapping so evenly spaced Mel band edges can be mapped
back to FFT-bin frequencies.
""",
    ("voxtral_audio.c", "mel_compact_samples"): """
Drops waveform samples that can no longer contribute to any future window,
retains the unresolved tail, and advances its absolute sample origin. Compaction
waits for enough progress to amortize the memory move.
""",
    ("voxtral_audio.c", "vox_mel_ctx_init"): """
Constructs the filterbank, DFT tables, Hann window, dynamic buffers, and optional
left padding. Failure unwinds partial allocations so null never represents a
half-usable context.
""",
    ("voxtral_audio.c", "vox_mel_data"): """
Publishes the context's internal row-major feature storage without copying.
Callers consume it before the next mutation.
""",
    ("voxtral_audio.c", "vox_mel_discard_before"): """
Converts an absolute keep position to a local row, moves the suffix, reduces the
stored count, and advances `mel_frame_offset`. Boundaries already discarded are
harmless no-ops.
""",
    ("voxtral_audio.c", "vox_mel_free"): """
Null-safe destruction of every allocation and Accelerate setup owned by the
incremental front end.
""",
    ("voxtral_audio.c", "build_mel_filters"): """
Constructs the [128, 201] Slaney triangular mel filter bank as a caller-owned
array. FFT bin centers span 0..8000 Hz; band edges are placed uniformly in mel
space and mapped back to hertz, each triangle is the min of rising and falling
slopes clamped at zero, then area-normalized. A tiny epsilon guards zero band
widths against division by zero.
""",
    ("voxtral_audio.c", "vox_mel_spectrogram"): """
Computes a full [n_frames, 128] log-mel spectrogram in one shot, matching vLLM:
center reflect-pad by n_fft/2, periodic Hann window, a direct DFT per frame over
precomputed cos/sin tables, power, mel projection, then log10 clamped and
rescaled by (val+4)/4. Drops the final STFT frame to mirror stft[..., :-1].
Caller-owned result; all scratch is freed before return.
""",
    ("voxtral_audio.c", "struct vox_mel_ctx"): """
State for incremental mel: precomputed filter bank, DFT cos/sin tables, and Hann
window built once; a growing padded sample ring tracked by sample_offset; and a
growing mel buffer tracked by mel_frame_offset. The two global offsets let old
samples and emitted frames be compacted while callers keep addressing positions
in absolute coordinates.
""",
    ("voxtral_audio.c", "mel_compute_available"): """
Drains every mel frame whose full window currently fits in the buffered samples,
appending rows to the growing mel array and bumping n_mel_frames. Each frame
applies Hann window, direct DFT over the cos/sin tables, mel projection, and the
log10 clamp/rescale, identical math to the one-shot path. Returns how many new
frames were produced; stops at the first window past available data.
""",
    ("voxtral_audio.c", "vox_mel_finish"): """
Finalizes the incremental front end: appends optional trailing zeros, then 200
samples of right reflect padding from the last real sample (mirroring
center=True), computes all remaining frames, and drops the final frame per the
vLLM stft[..., :-1] convention. Idempotent via the finished flag.
""",
    ("voxtral_audio.c", "vox_mel_frame_offset"): """
Returns the global frame index of mel[0], i.e. how many frames have already been
discarded from the front. Callers add this to a local row index to recover an
absolute mel position that survives compaction.
""",
    ("voxtral_tokenizer.h", "typedef struct vox_tokenizer"): """
Opaque tokenizer ownership boundary. The JSON schema and byte-piece table stay
private while callers receive a small decode/query API.
""",
    ("voxtral_tokenizer.h", "vox_tokenizer_load"): """
Parses Tekken JSON into owned ID-to-byte-piece tables or returns null. The
tokenizer must outlive every borrowed piece returned by single-token decode.
""",
    ("voxtral_tokenizer.h", "vox_tokenizer_free"): """
Releases all decoded pieces, metadata arrays, and the tokenizer object.
""",
    ("voxtral_tokenizer.h", "vox_tokenizer_decode"): """
Returns a borrowed byte piece for one valid ID. A piece may split a UTF-8 scalar,
so consumers concatenate bytes before treating output as displayable Unicode.
""",
    ("voxtral_tokenizer.h", "vox_tokenizer_decode_seq"): """
Concatenates token pieces into one newly allocated NUL-terminated byte string.
The caller frees the result.
""",
    ("voxtral_tokenizer.h", "vox_tokenizer_vocab_size"): """
Returns the loaded ID-table extent for range checks, not a word count.
""",
    ("voxtral_tokenizer.c", "struct vox_tokenizer"): """
Holds two owned string tables: vocab (regular pieces, indexed by rank) and
special (control tokens), each a decoded UTF-8 byte string. bos_id and eos_id are
fixed at 1 and 2. This build decodes only; there is no encode-side trie.
""",
    ("voxtral_tokenizer.c", "skip_ws"): """
Advances the schema-specific JSON cursor over ASCII whitespace.
""",
    ("voxtral_tokenizer.c", "parse_str"): """
Parses a bounded JSON string with required escapes into caller storage and
rejects malformed or oversized values.
""",
    ("voxtral_tokenizer.c", "parse_long"): """
Consumes one signed decimal integer and advances the cursor; semantic token-ID
ranges are checked by the caller.
""",
    ("voxtral_tokenizer.c", "skip_value"): """
Skips unneeded JSON scalars or balanced arrays/objects, allowing new metadata
fields without allocating a complete JSON tree.
""",
    ("voxtral_tokenizer.c", "b64_decode"): """
Minimal base64 decoder over a 256-entry lookup table: accumulates 6-bit groups
and emits bytes into out, stopping at '=' padding and skipping any non-alphabet
character. Used to turn each vocab entry's token_bytes field into raw token
bytes, which may legitimately include embedded NULs.
""",
    ("voxtral_tokenizer.c", "vox_tokenizer_load"): """
Loads tekken.json fully into memory and walks the top-level object, populating
the vocab table (base64 token_bytes decoded per rank, mapped to id 1000+rank) and
the special table (token_str per rank, ids 0..999). Owns every decoded string;
bos/eos are hardcoded to 1/2. Returns a heap tokenizer the caller frees, or NULL
on open/parse failure.
""",
    ("voxtral_tokenizer.c", "vox_tokenizer_decode"): """
Maps a single token id to its borrowed UTF-8 byte string: ids >= 1000 index the
regular vocab at id-1000, ids 0..n_special index the special table, anything else
yields NULL. The returned pointer is owned by the tokenizer and must not be freed.
May legitimately return an empty string for byte-0x00 pieces.
""",
    ("voxtral_tokenizer.c", "vox_tokenizer_free"): """
Frees each owned regular/special piece, their tables, and the context. The same
path cleans partially populated objects after load failure.
""",
    ("voxtral_tokenizer.c", "vox_tokenizer_decode_seq"): """
Totals piece lengths, allocates once, copies in token order, and appends NUL.
Invalid IDs cannot index outside the tables.
""",
    ("voxtral_tokenizer.c", "vox_tokenizer_bos"): """
Returns the model protocol's beginning-of-sequence control ID.
""",
    ("voxtral_tokenizer.c", "vox_tokenizer_eos"): """
Returns the end-of-sequence ID used by decoder termination logic.
""",
    ("voxtral_tokenizer.c", "vox_tokenizer_vocab_size"): """
Returns the context's vocabulary-table size for decoder range validation.
""",
    ("voxtral_safetensors.h", "typedef enum safetensor_dtype_t"): """
The on-disk numeric formats understood by this loader. Unknown strings map to
`DTYPE_UNKNOWN` and are rejected by typed accessors rather than guessed.
""",
    ("voxtral_safetensors.h", "typedef struct safetensor_t"): """
Metadata for one tensor: bounded name, dtype, rank/shape, and byte interval
relative to the safetensors data region. It contains no owned weight buffer.
""",
    ("voxtral_safetensors.h", "typedef struct safetensors_file_t"): """
Owns the file descriptor/mapping and fixed tensor metadata table. Tensor data
pointers borrow the mapping and become invalid when this object closes.
""",
    ("voxtral_safetensors.h", "safetensors_open"): """
Maps a file read-only, parses and validates its JSON header and every tensor
range, then publishes a complete file object. Null means no mapping ownership
escaped.
""",
    ("voxtral_safetensors.h", "safetensors_close"): """
Unmaps bytes, closes the descriptor, and frees metadata ownership. It must
outlive all direct BF16 pointers handed to model components.
""",
    ("voxtral_safetensors.h", "safetensors_find"): """
Performs a name lookup in the parsed metadata table and returns a borrowed
descriptor or null. Weight loaders use exact checkpoint names as the model ABI.
""",
    ("voxtral_safetensors.h", "safetensors_data"): """
Returns a borrowed pointer to validated raw tensor bytes inside the mapping.
No conversion or allocation occurs.
""",
    ("voxtral_safetensors.h", "safetensors_get_f32"): """
Returns a newly allocated FP32 copy, converting supported on-disk formats.
Callers own and free it; this can double memory for large weights and is reserved
for tensors that need float storage.
""",
    ("voxtral_safetensors.h", "safetensors_get_bf16"): """
Returns a newly allocated BF16 representation, copying BF16 input or converting
supported source values. Ownership differs from the direct accessor.
""",
    ("voxtral_safetensors.h", "safetensors_get_bf16_direct"): """
Returns a borrowed zero-copy BF16 pointer only when dtype and byte size match.
It is read-only and tied to mapping lifetime.
""",
    ("voxtral_safetensors.h", "safetensor_is_bf16"): """
Small predicate used before selecting direct BF16 execution paths.
""",
    ("voxtral_safetensors.h", "safetensor_numel"): """
Multiplies shape dimensions to obtain logical element count, with invalid shape
metadata producing failure rather than a wrapped allocation size.
""",
    ("voxtral_safetensors.h", "safetensor_print"): """
Diagnostic printer for one tensor's name, dtype, shape, and byte interval; it
does not print multi-gigabyte data.
""",
    ("voxtral_safetensors.h", "safetensors_print_all"): """
Iterates metadata through `safetensor_print` for model-load diagnostics.
""",
    ("voxtral_safetensors.c", "skip_whitespace"): """
Advances the bounded header JSON cursor across whitespace.
""",
    ("voxtral_safetensors.c", "parse_string"): """
Parses one bounded JSON string into fixed storage with escape handling and
capacity checks, returning failure instead of truncating tensor names.
""",
    ("voxtral_safetensors.c", "parse_int"): """
Consumes a signed header integer used for shapes and offsets. Later validation
checks nonnegativity, multiplication overflow, and mapping bounds.
""",
    ("voxtral_safetensors.c", "parse_dtype"): """
Maps known safetensors dtype strings to the internal enum; unsupported values
remain explicit `UNKNOWN`.
""",
    ("voxtral_safetensors.c", "parse_tensor_entry"): """
Parses one tensor object's dtype, shape, and two data offsets into metadata.
Required fields and rank limits are validated before the descriptor is accepted.
""",
    ("voxtral_safetensors.c", "parse_header"): """
Walks the top-level header object, parsing each named tensor entry into the
file's fixed tensors array and skipping __metadata__. Sets num_tensors. Returns
-1 on any malformed structure, which aborts the open. Operates on the copied
header JSON string, not the mapped region, so it can NUL-terminate freely.
""",
    ("voxtral_safetensors.c", "safetensors_data"): """
Returns a borrowed pointer to a tensor's raw bytes inside the mmap by adding the
8-byte header-length prefix, the header size, and the tensor's data_offset to the
mapped base. No copy and no bounds re-check here; validity rests on the bounds
safetensors_open verified at load. Pointer is read-only and dies at close.
""",
    ("voxtral_safetensors.c", "safetensors_get_bf16_direct"): """
Zero-copy accessor returning a borrowed uint16 pointer straight into the mmap for
a BF16 tensor, after checking dtype and that numel*2 fits data_size. No
allocation; the pointer is read-only and invalid once the file is closed. This is
the fast path the engine uses to keep weights resident as bf16 without converting.
""",
    ("voxtral_safetensors.c", "safetensors_close"): """
Null-safe unmap/close/free teardown for the file object. The mapping is released
once; individual tensor descriptors and direct pointers own nothing separately.
""",
    ("voxtral_safetensors.c", "safetensors_find"): """
Linear exact-name search over at most the configured metadata limit. Model load
is infrequent, so simple lookup keeps ownership and failure behavior obvious.
""",
    ("voxtral_safetensors.c", "safetensor_numel"): """
Computes the product of dimensions with validity checks before the result is
used for byte-size calculations and allocations.
""",
    ("voxtral_safetensors.c", "bf16_to_f32"): """
Expands BF16 by placing its 16 bits in the high half of an IEEE-754 float word;
the exponent width is preserved and the missing mantissa bits become zero.
""",
    ("voxtral_safetensors.c", "f16_to_f32"): """
Converts IEEE half precision to float, handling zero, subnormal, finite,
infinite, and NaN exponent cases explicitly.
""",
    ("voxtral_safetensors.c", "safetensors_get_f32"): """
Allocates one float per element and converts from supported F32, BF16, or F16
storage. Every error frees partial output and returns null.
""",
    ("voxtral_safetensors.c", "safetensor_is_bf16"): """
Tests descriptor dtype without touching mapped tensor bytes.
""",
    ("voxtral_safetensors.c", "safetensors_get_bf16"): """
Allocates BF16 output, copying direct BF16 data or narrowing supported FP32
values. The caller owns this buffer independently of the mapping.
""",
    ("voxtral_safetensors.c", "safetensor_print"): """
Formats one metadata record for load debugging without dereferencing tensor
contents.
""",
    ("voxtral_safetensors.c", "safetensors_print_all"): """
Prints every parsed metadata record in source-table order.
""",
    ("ClassroomVoxtral.c", "ccv_model_load"): """
Validates the model directory (must hold consolidated.safetensors, tekken.json,
params.json), initializes Metal when built with it, then loads the engine via
vox_load behind an opaque ccv_model_t handle. Every failure path sets a specific
ccv_status_t and a human-readable error_message and frees partial state, so the
caller never receives a half-built handle.
""",
    ("ClassroomVoxtral.c", "struct ccv_model"): """
The concrete body hidden behind `ccv_model_t`: one owned upstream context.
Keeping this wrapper distinct leaves room for project metadata without exposing
`vox_ctx_t` through the stable ABI.
""",
    ("ClassroomVoxtral.c", "struct ccv_stream"): """
Bridge-owned mutable state: upstream stream, cancellation/finish flags, reusable
PCM conversion storage, and a pending text buffer retained across a too-small
read. Swift sees only the opaque pointer.
""",
    ("ClassroomVoxtral.c", "ccv_set_status"): """
Writes an optional status out-parameter. Null tolerance keeps callers free to
request only the handle/error string they need.
""",
    ("ClassroomVoxtral.c", "ccv_set_error"): """
Copies a diagnostic into caller-owned bounded storage with guaranteed
termination; null or zero-capacity output is a no-op.
""",
    ("ClassroomVoxtral.c", "ccv_model_file_exists"): """
Builds one required model path into a fixed local buffer and checks regular file
availability before invoking the heavier loader.
""",
    ("ClassroomVoxtral.c", "ccv_stream_options_default"): """
Returns the bridge's complete real-time policy baseline, ensuring future fields
are initialized for Swift callers that start from defaults.
""",
    ("ClassroomVoxtral.c", "ccv_stream_create"): """
Builds an opaque streaming handle over a loaded model: applies the delay to the
shared engine context, initializes a vox_stream, then sets processing interval,
continuous mode, and the decode-context cap from options. On stream-init failure
it sets status, frees the handle, and returns NULL.
""",
    ("ClassroomVoxtral.c", "ccv_model_free"): """
Null-safe wrapper destruction: frees the upstream model, then the small ABI
handle. Streams borrowing it must already be gone.
""",
    ("ClassroomVoxtral.c", "ccv_stream_feed_pcm16"): """
Converts an int16 PCM block to f32 in [-1,1) through a reused, lazily-grown
conversion_buffer owned by the stream, then feeds it to the engine.
Short-circuits to CANCELLED or STREAM_FINISHED when those flags are set,
INVALID_ARGUMENT on null/empty input, and INFERENCE_FAILED on alloc or engine
failure.
""",
    ("ClassroomVoxtral.c", "ccv_stream_flush"): """
Validates lifecycle/cancellation, calls the upstream nonterminal flush, and maps
its integer convention to the stable project status enum.
""",
    ("ClassroomVoxtral.c", "ccv_stream_finish"): """
Finishes exactly once, records terminal state only after upstream success, and
maps repeated or cancelled calls to explicit statuses.
""",
    ("ClassroomVoxtral.c", "ccv_stream_samples_fed"): """
Exposes the upstream cumulative sample counter without revealing stream layout.
Invalid handles return zero for diagnostics.
""",
    ("ClassroomVoxtral.c", "ccv_stream_text_tokens_generated"): """
Forwards the cumulative text-token counter used by the app's live rate display.
""",
    ("ClassroomVoxtral.c", "ccv_stream_decoder_milliseconds"): """
Forwards accumulated decoder timing as a double for rate calculation.
""",
    ("ClassroomVoxtral.c", "ccv_stream_free"): """
Releases pending text, conversion scratch, upstream stream, and finally the ABI
wrapper. No borrowed output pointer survives this call.
""",
    ("ClassroomVoxtral.c", "ccv_status_description"): """
Provides static fallback text for every bridge status without allocation.
""",
    ("ClassroomVoxtral.c", "ccv_upstream_revision"): """
Returns the compile-time pinned upstream revision string used in diagnostics and
tests.
""",
    ("VoxtralEmbeddedService.swift", "enum VoxtralEmbeddedError"): """
Swift-facing failures for invalid model path, C load/create failure, and stream
operation failure. Each carries enough bridge text to diagnose configuration
without exposing raw status handling to the app model.
""",
    ("VoxtralEmbeddedService.swift", "class VoxtralEmbeddedService"): """
Owns the embedded backend's C handles and serial inference queue. The class is
`@unchecked Sendable` because opaque pointers are not compiler-verifiable;
queue confinement guarantees that feed, drain, flush, finish, and destruction
never overlap.
""",
    ("VoxtralEmbeddedService.swift", "struct State"): """
Queue-confined lifecycle record for model/stream handles, continuation,
activation flags, pending provisional text, counters, and priming state. Keeping
them together lets startup and stop publish coherent transitions.
""",
    ("VoxtralEmbeddedService.swift", "func events("): """
Creates the ordered event stream and stores its continuation under queue
ownership. Termination removes the output sink without racing C-handle access.
""",
    ("VoxtralEmbeddedService.swift", "func flush("): """
Runs bridge flush on the inference queue, drains every available token, emits
updated metrics, and optionally converts the accumulated provisional caption
into a finalized event. It keeps the C stream alive for later audio.
""",
    ("VoxtralEmbeddedService.swift", "discardPendingText"): """
Drains and ignores text emitted by decoder priming so warm-up tokens cannot
appear as lecture captions.
""",
    ("VoxtralEmbeddedService.swift", "func emit("): """
Yields a value event through the current continuation; callers invoke it from
the inference queue so event order matches C-stream order.
""",
    ("VoxtralEmbeddedService.swift", "makeError"): """
Combines bridge status and bounded C error buffer into one localized Swift
failure, preferring the specific bridge message when present.
""",
    ("VoxtralEmbeddedService.swift", "statusMessage"): """
Converts the bridge's borrowed C status-description pointer to a Swift string
with a stable fallback for an unexpected null.
""",
    ("ClassroomVoxtral.c", "ccv_stream_cancel"): """
Sets the stream's atomic cancelled flag so concurrent or subsequent
feed/flush/finish calls short-circuit to CCV_STATUS_CANCELLED. The atomic makes
this safe to call from a different thread than the inference loop; it does not
free anything or interrupt an in-flight engine call.
""",
    ("ClassroomVoxtral.c", "ccv_stream_read_text"): """
Pops one pending token from the engine queue and copies its NUL-terminated UTF-8
into the caller's output buffer. A token already dequeued but not yet delivered is
cached in pending_text so a BUFFER_TOO_SMALL caller can retry with the reported
required_capacity without losing it. Returns NO_TEXT when the queue is empty.
""",
    ("VoxtralEmbeddedService.swift", "func primeDecoderWithSilence"): """
Warms the decoder before real audio by feeding startupPrerollSamples of int16
silence (about 3.2 s) through the engine, then discarding whatever provisional
tokens that silence produced so they never reach the UI. Throws on a non-OK feed
status, which start() treats as a fatal warm-up failure. Runs on the serial
inference queue.
""",
    ("VoxtralEmbeddedService.swift", "func drainText"): """
Pulls every available token from the engine via ccv_stream_read_text, growing the
buffer once on BUFFER_TOO_SMALL, and appends each non-empty token to the locked
provisionalText. After each token it emits updated token-rate metrics and a
provisional caption event. Stops cleanly on NO_TEXT and surfaces any other status
as a failure event.
""",
    ("VoxtralEmbeddedService.swift", "func takeFinalizedProvisional"): """
Atomically swaps out the accumulated provisionalText for the empty string under
the state lock, trims whitespace, and returns it or nil when empty. Used by
flush(finalizeCaption:) and stop() to convert the running provisional into a
single finalized caption without racing the drain path.
""",

    # --- Numerical kernels, encoder, decoder -------------------------------
    ("voxtral_kernels.h", "vox_add_inplace"): """
Elementwise residual primitive `a[i] += b[i]`, modifying only `a`. Equal length
and non-overlapping storage are caller obligations.
""",
    ("voxtral_kernels.h", "vox_mul_inplace"): """
Elementwise gate/product primitive `a[i] *= b[i]`.
""",
    ("voxtral_kernels.h", "vox_axpy"): """
BLAS-style operation `a += scale * b`, used for scaled residual accumulation.
""",
    ("voxtral_kernels.h", "vox_scale"): """
Multiplies one vector in place by a scalar.
""",
    ("voxtral_kernels.h", "vox_copy"): """
Copies `n` float elements from source to destination with the implementation's
defined overlap assumptions.
""",
    ("voxtral_kernels.h", "vox_matmul("): """
Computes row-major `C[M,N] = A[M,K] * B[K,N]`.
""",
    ("voxtral_kernels.h", "vox_matmul_t"): """
Computes with the stored right matrix interpreted as transposed, matching the
row-major checkpoint weight layout without materializing a transpose.
""",
    ("voxtral_kernels.h", "vox_linear("): """
Applies a dense projection and optional bias over one or more input rows.
""",
    ("voxtral_kernels.h", "vox_linear_nobias("): """
Dense projection variant for architecture layers whose checkpoint has no bias.
""",
    ("voxtral_kernels.h", "vox_linear_nobias_bf16"): """
Projects with BF16 stored weights while accumulating/outputting float.
""",
    ("voxtral_kernels.h", "vox_linear_bf16"): """
BF16-weight projection plus float bias.
""",
    ("voxtral_kernels.h", "vox_matmul_t_bf16"): """
Batched matrix product against transposed BF16 weights with float accumulation.
""",
    ("voxtral_kernels.h", "vox_conv1d("): """
General one-dimensional convolution over sequence/channel tensors.
""",
    ("voxtral_kernels.h", "vox_causal_conv1d"): """
Causal convolution whose output position never reads future input positions.
""",
    ("voxtral_kernels.h", "vox_rms_norm"): """
RMS normalization with learned weight and epsilon, without mean subtraction.
""",
    ("voxtral_kernels.h", "vox_silu"): """
In-place Sigmoid Linear Unit activation.
""",
    ("voxtral_kernels.h", "vox_gelu"): """
In-place Gaussian Error Linear Unit approximation used by encoder layers.
""",
    ("voxtral_kernels.h", "vox_softmax"): """
Normalizes each row with a max-subtracted exponential for numerical stability.
""",
    ("voxtral_kernels.h", "vox_causal_attention"): """
Reference causal attention over Q/K/V with head geometry and position limits
supplied explicitly by the caller.
""",
    ("voxtral_kernels.h", "vox_compute_rope_freqs"): """
Builds sine/cosine rotary frequencies from absolute positions and theta.
""",
    ("voxtral_kernels.h", "vox_apply_rope"): """
Applies interleaved GPT-J-style rotary pairs to every head in place.
""",
    ("voxtral_kernels.c", "vox_add_inplace"): """
Scalar elementwise residual addition; Accelerate may vectorize larger composite
paths, but this loop defines exact aliasing and arithmetic semantics.
""",
    ("voxtral_kernels.c", "vox_mul_inplace"): """
Scalar elementwise multiplication used by gated feed-forward activations.
""",
    ("voxtral_kernels.c", "vox_axpy"): """
Adds a scaled vector into another, matching the classic AXPY operation.
""",
    ("voxtral_kernels.c", "vox_scale"): """
Scales one float vector in place.
""",
    ("voxtral_kernels.c", "vox_copy"): """
Copies one float vector into distinct destination storage.
""",
    ("voxtral_kernels.c", "bf16_to_f32_buf"): """
Expands a BF16 array into caller-provided float storage for fallback kernels.
""",
    ("voxtral_kernels.c", "bf16_get_scratch"): """
Grows and reuses a process-global conversion scratch buffer. It reduces
allocation churn but assumes serialized kernel use by the inference runtime.
""",
    ("voxtral_kernels.c", "vox_linear_nobias"): """
Dispatches a no-bias dense layer through the float matrix multiplication path.
""",
    ("voxtral_kernels.c", "vox_matmul"): """
Dense row-major C[M,N] = A[M,K] @ B[K,N], dispatching to cblas_sgemm when
USE_BLAS is set and otherwise running the naive triple loop. B is laid out [K,N]
(not transposed), so the inner k-loop strides A contiguously but B by N. This is
the textbook GEMM that all the bf16 paths fall back to after weight conversion.
""",
    ("voxtral_kernels.c", "vox_matmul_t"): """
Computes C[M,N] = A[M,K] @ B[N,K]^T, i.e. B is stored row-major with each output
column as a contiguous K-length row, which matches PyTorch nn.Linear weight
layout. Both A and B rows are streamed contiguously in the inner loop, so this is
the cache-friendly variant used for logit and projection matmuls.
""",
    ("voxtral_kernels.c", "vox_linear"): """
Affine projection y[seq,out] = x[seq,in] @ W^T + b, where W is [out,in] row-major
(PyTorch convention) and bias is optional. BLAS path uses CblasTrans on W then
adds bias per row; the scalar path dots each x row against each weight row. This
is the f32 reference; bf16 weights go through the _bf16 wrappers instead.
""",
    ("voxtral_kernels.c", "bf16_matvec_fused"): """
Single-row (seq=1) matvec y[out] = W_bf16[out,in] @ x[in] + bias that reads bf16
weights and widens them to f32 in-register, avoiding the double memory pass of
convert-whole-matrix-then-GEMM. The NEON loop processes 8 weights per iteration
via two fp32 accumulators (left-shifting each u16 by 16 to form the bf16->f32
mantissa) with a scalar tail. This is the hot path for per-token decoder
generation.
""",
    ("voxtral_kernels.c", "vox_linear_nobias_bf16"): """
Bias-free linear with bf16 weights: dispatches to Metal if available, uses the
fused bf16 matvec for seq_len==1, and otherwise expands W into the shared
bf16_scratch f32 buffer before calling the f32 vox_linear_nobias. The scratch
buffer is reused across calls so multi-token prefill avoids per-call malloc.
""",
    ("voxtral_kernels.c", "vox_linear_bf16"): """
Same dispatch as the nobias variant but threads the optional bias through:
Metal/seq==1 paths add it inline, the multi-row path passes it to vox_linear
after converting W to f32. Used for the encoder's biased Q/V/out/w2 projections.
""",
    ("voxtral_kernels.c", "vox_matmul_t_bf16"): """
bf16-weight version of vox_matmul_t computing C[M,N] = A[M,K] @ B_bf16[N,K]^T.
For M==1 it uses the fused matvec directly; for M>1 it widens B into the shared
scratch and calls vox_matmul_t. This is how decoder logits are produced from the
tied bf16 token-embedding matrix.
""",
    ("voxtral_kernels.c", "vox_conv1d"): """
Direct 1D convolution with explicit symmetric padding: out length is
(length + 2*padding - kernel_size)/stride + 1, weights are [out_ch, in_ch, k] and
both in and out are channel-major [C, L]. Out-of-range taps are skipped rather
than read, so no input padding buffer is materialized.
""",
    ("voxtral_kernels.c", "vox_causal_conv1d"): """
Causal (left-padded) conv1d matching vLLM's WhisperCausalConv1d, with
padding_total = kernel_size - stride applied entirely on the left. It builds an
im2col matrix then runs a single cblas_sgemm against the [out_ch, in_ch*k]
weights, adding bias afterward. This is the conv front end of the audio encoder
stem.
""",
    ("voxtral_kernels.c", "vox_rms_norm"): """
Per-row RMSNorm over [seq,hidden]: divides each row by sqrt(mean(x^2)+eps) then
scales elementwise by the learned weight vector. eps is added inside the sqrt (to
the mean-square), not to the rms, and there is no mean-subtraction or bias since
this is RMS rather than LayerNorm.
""",
    ("voxtral_kernels.c", "vox_silu"): """
In-place SiLU/swish activation x = x * sigmoid(x) over n elements, computed as
x/(1+exp(-x)). Used as the gate nonlinearity in the SwiGLU FFNs of both encoder
and decoder.
""",
    ("voxtral_kernels.c", "vox_gelu"): """
In-place tanh-approximation GELU: 0.5*x*(1+tanh(sqrt(2/pi)*(x+0.044715*x^3))),
with the sqrt(2/pi) constant hardcoded. This is the activation for the conv-stem
GELUs and the projection adapter, not the FFNs (which use SiLU).
""",
    ("voxtral_kernels.c", "vox_softmax"): """
Numerically-stable row-wise softmax over an [rows,cols] matrix, done in place:
subtract the per-row max before exp, then divide by the row sum. The standalone
attention kernel instead fuses softmax online, so this is used where full score
rows are materialized.
""",
    ("voxtral_kernels.c", "vox_causal_attention"): """
Single-pass GQA attention producing out[seq_q, n_heads*head_dim] from Q and the
cached K/V laid out [seq_k, n_kv_heads*head_dim]. Each query head h maps to KV
head h/(n_heads/n_kv_heads); attendance runs from k_start (sliding-window lower
bound) to global_pos+1, where global_pos = q_offset+i gives the causal cutoff. It
uses online softmax with a running max and correction factor so V is accumulated
in one pass without storing the score row.
""",
    ("voxtral_kernels.c", "vox_compute_rope_freqs"): """
Precomputes interleaved cos/sin RoPE coefficients into freqs[seq, head_dim/2, 2]
for the given integer positions, with per-dimension frequency 1/theta^(2d/dim).
Storing both cos and sin once per position lets vox_apply_rope stay branch-free.
""",
    ("voxtral_kernels.c", "vox_apply_rope"): """
Applies rotary embedding in place to x[seq, heads*head_dim] using the cos/sin
pairs from vox_compute_rope_freqs. It rotates adjacent element pairs
(x0,x1) -> (x0*cos - x1*sin, x0*sin + x1*cos), the interleaved (GPT-J-style)
pairing of adjacent dimensions (not the rotate-half GPT-NeoX convention).
Called on Q and K before they enter attention and before K is written to cache.
""",
    ("voxtral_decoder.c", "load_f32"): """
Finds a named tensor and materializes an owned FP32 copy for decoder fields that
require float storage. Missing or incompatible weights fail model load.
""",
    ("voxtral_decoder.c", "load_bf16_direct"): """
Finds a named BF16 tensor and stores a zero-copy pointer into the safetensors
mapping. Mapping lifetime therefore dominates decoder lifetime.
""",
    ("voxtral_decoder.c", "kv_cache_is_allocated"): """
Checks that the decoder's selected cache representation and required layer
pointers exist before generation begins.
""",
    ("voxtral_decoder.c", "kv_cache_k_at"): """
Computes the FP32 key-cache row address for one layer and logical position.
""",
    ("voxtral_decoder.c", "kv_cache_v_at"): """
Computes the FP32 value-cache row address using the same capacity/stride layout.
""",
    ("voxtral_decoder.c", "kv_cache_k_f16_at"): """
Returns the FP16 key row when compact cache storage is active.
""",
    ("voxtral_decoder.c", "kv_cache_v_f16_at"): """
Returns the corresponding FP16 value row.
""",
    ("voxtral_decoder.c", "vox_decoder_load"): """
Loads all 26 decoder layers from the safetensors file: large matmul weights
(wq/wk/wv/wo, FFN w1/w2/w3, and the tied token embeddings) are kept as mmap'd
bf16 read directly, while the small norms and the ada_rms_norm MLP weights are
converted to f32. Returns -1 if any required attention weight or the final norm
is missing.
""",
    ("voxtral_decoder.c", "f16_to_f32"): """
Scalar IEEE half-to-single widening used when materializing an fp16 KV cache into
fp32, handling subnormals, inf/NaN (exp==0x1F), and the 127-15 exponent rebias.
This is true fp16, distinct from the bf16 widening (shift-left-16) used for
weights elsewhere.
""",
    ("voxtral_decoder.c", "kv_cache_init"): """
Allocates the per-layer K and V caches sized VOX_DEC_LAYERS * max_seq * (8*128)
elements, choosing fp16 vs fp32 storage and Metal-shared vs calloc memory based
on ctx->kv_cache_fp16 and Metal availability; CPU-only builds force fp32. Sets
kv_cache_len to 0 but leaves kv_pos_offset for the caller to manage.
""",
    ("voxtral_decoder.c", "vox_decoder_kv_cache_preallocate"): """
Idempotent wrapper that allocates the KV cache at max_seq only if not already
present, so the caller can reserve capacity up front and avoid mid-stream grow
copies. Returns 0 when the cache already exists.
""",
    ("voxtral_decoder.c", "kv_cache_grow"): """
Doubles kv_cache_max until it covers the requirement, allocates fresh K/V buffers
(fp16 or fp32, shared or heap to match the current mode), and copies the first
kv_cache_len valid rows of every layer across the changed per-layer stride. The
per-layer stride is max*kv_dim, so growth is a strided re-pack rather than a flat
realloc; old buffers are freed through the matching allocator.
""",
    ("voxtral_decoder.c", "kv_cache_compact"): """
Sliding-window eviction: when length exceeds VOX_DEC_WINDOW it memmoves the last
VOX_DEC_WINDOW K/V rows of each layer down to position 0 and advances
kv_pos_offset by the number discarded. Because RoPE is already baked into the
cached K vectors, the kept rows stay valid and only the logical-position offset
needs updating, with no re-encoding.
""",
    ("voxtral_decoder.c", "kv_cache_switch_to_fp32"): """
One-way conversion from an fp16 KV cache to fp32: allocates new f32 K/V buffers,
widens the first kv_cache_len rows of every layer via f16_to_f32, frees the fp16
buffers and clears kv_cache_fp16. The CPU forward/prefill paths call this because
they read the cache as float; the GPU path keeps fp16.
""",
    ("voxtral_decoder.c", "ensure_dec_buffers"): """
Lazily allocates the persistent single-token scratch (x, x_norm, q/k/v, attn_out,
proj_out, gate/up, ffn_out, rope_freqs) sized for one position and caches them on
ctx, so per-token generation reuses them instead of malloc/free each step.
""",
    ("voxtral_encoder.c", "load_f32"): """
Materializes a named encoder tensor as owned float storage when computation
cannot use the mapped BF16 bytes directly.
""",
    ("voxtral_encoder.c", "load_bf16_direct"): """
Returns a borrowed mapped BF16 weight pointer, avoiding a multi-gigabyte
conversion and tying encoder lifetime to the open safetensors file.
""",
    ("voxtral_encoder.c", "gelu_inplace"): """
Applies the encoder's GELU activation over a contiguous float vector.
""",
    ("voxtral_encoder.c", "causal_conv1d_out_len"): """
Computes the number of stable strided causal-convolution outputs available for a
given input length, kernel, and stride.
""",
    ("voxtral_encoder.c", "enc_kv_cache_k_at"): """
Addresses one encoder key-cache row from layer and local cache position.
""",
    ("voxtral_encoder.c", "enc_kv_cache_v_at"): """
Addresses the matching value-cache row.
""",
    ("voxtral_encoder.c", "vox_encoder_kv_cache_preallocate"): """
Allocates encoder caches to a known maximum before live audio, moving allocation
latency out of the first classroom utterance.
""",
    ("voxtral_encoder.c", "enc_realloc_float"): """
Overflow-aware helper for growing float scratch arrays while preserving existing
contents.
""",
    ("voxtral_encoder.c", "enc_realloc_int"): """
Equivalent growth helper for absolute-position arrays.
""",
    ("voxtral_encoder.c", "enc_inc_ensure_buffers"): """
Ensures every incremental encoder scratch/output/position buffer can hold the
next chunk as one transaction; failure prevents partial inference.
""",
    ("voxtral_encoder.c", "vox_encoder_load"): """
Loads the 32-layer audio encoder: the conv stem and all per-layer biases/norms
are f32, while the attention and FFN matmul weights are mmap'd bf16. Mirrors the
model's asymmetric biasing - wq/wv/wo and FFN w2 carry biases but wk does not -
so wk's bias is never requested.
""",
    ("voxtral_encoder.c", "vox_encoder_forward"): """
Full audio-encoder pass: transposes mel[frames,128] to channel-major, runs the
two causal conv1d+GELU stem layers (the second strided by 2), then 32
sliding-window causal MHA + SwiGLU transformer layers, and a final RMSNorm. RoPE
positions start at 0; encoder attention biases Q and V but not K (wk has no
bias), and uses VOX_ENC_WINDOW. Returns the [seq_len,1280] hidden state.
""",
    ("voxtral_encoder.c", "enc_kv_cache_grow"): """
Grows the encoder's incremental K/V cache by doubling enc_kv_cache_max and
re-packing existing rows across the new per-layer stride. Refuses to grow
Metal-shared buffers (which cannot be resized), so shared mode relies on
preallocation being large enough.
""",
    ("voxtral_encoder.c", "enc_kv_cache_compact"): """
Sliding-window eviction for the encoder cache: keeps the last VOX_ENC_WINDOW rows
per layer via memmove to position 0 and bumps enc_kv_pos_offset by the discarded
count, leaving baked-in RoPE valid. Mirrors the decoder's kv_cache_compact but
always operates on f32 rows.
""",
    ("voxtral_encoder.c", "vox_encoder_forward_incremental"): """
Streaming encoder step: compacts/grows the KV cache for new_len incoming frames,
runs RoPE at logical positions enc_kv_pos_offset+cache_len, projects Q/K/V only
for the new positions, appends K/V to the cache, and attends each new query over
the full window. After 32 layers and the final norm it returns the new positions'
[new_len,1280] output; the GPU path runs all layers in one command buffer when
the cache is shared.
""",
    ("voxtral_encoder.c", "vox_adapter_forward"): """
Bridges encoder to decoder: downsamples 4x by concatenating every group of 4
encoder frames into one 5120-d vector, then applies Linear(5120->3072) -> GELU ->
Linear(3072->3072) with bf16 weights to produce decoder-dimension embeddings.
Returns the [ds_len,3072] result.
""",

    # --- Metal host layer and decoded MSL shader kernels -------------------
    ("voxtral_metal.h", "vox_metal_init"): """
Creates the global device, command queue, shader library, pipelines, and caches.
Zero means callers must retain a CPU/fallback path.
""",
    ("voxtral_metal.h", "vox_metal_available"): """
Reports whether initialization completed; it performs no allocation or dispatch.
""",
    ("voxtral_metal.h", "vox_metal_shutdown"): """
Releases pipelines, MPS operation caches, converted/merged weights, activation
pool, persistent decoder storage, queue, and device.
""",
    ("voxtral_metal.h", "vox_metal_sgemm_bf16"): """
Multiplies float activations by transposed BF16 checkpoint weights. Weights are
converted and cached as FP16 GPU buffers; output remains float.
""",
    ("voxtral_metal.h", "vox_metal_sgemm("): """
Float dense product against row-major transposed weights through Metal/MPS.
""",
    ("voxtral_metal.h", "vox_metal_fused_qkv_bf16"): """
Encodes Q, K, and V projections in one command buffer with shared input.
""",
    ("voxtral_metal.h", "vox_metal_fused_norm_qkv_bf16"): """
Adds RMS normalization before fused Q/K/V projection while intermediates remain
on GPU.
""",
    ("voxtral_metal.h", "vox_metal_fused_ffn_bf16"): """
Runs gate/up projections, SiLU product, and down projection without CPU
round-trips for hidden activations.
""",
    ("voxtral_metal.h", "vox_metal_fused_wo_ffn_bf16"): """
Fuses attention output projection, residual, conditioned norm, SwiGLU, and the
second residual.
""",
    ("voxtral_metal.h", "vox_metal_batched_attention"): """
Computes all masked/windowed heads with strided matrix views, including mapping
many query heads onto fewer K/V heads.
""",
    ("voxtral_metal.h", "vox_metal_encoder_attention"): """
Encoder-specialized single-dispatch attention with the same tensor contract.
""",
    ("voxtral_metal.h", "vox_metal_fused_logits_bf16"): """
Applies final norm, vocabulary projection, and argmax on GPU; logits output is
optional.
""",
    ("voxtral_metal.h", "vox_metal_decoder_start"): """
Uploads one residual vector into persistent GPU storage before the layer loop.
""",
    ("voxtral_metal.h", "vox_metal_decoder_end"): """
Ends persistent-x mode after one token step.
""",
    ("voxtral_metal.h", "vox_metal_decoder_norm_qkv"): """
Runs first-layer normalization and Q/K/V projection from persistent x.
""",
    ("voxtral_metal.h", "vox_metal_decoder_wo_ffn_next_qkv"): """
Fuses one layer's output/feed-forward updates with the next layer's norm and
Q/K/V, removing an inter-layer command-buffer boundary.
""",
    ("voxtral_metal.h", "vox_metal_decoder_wo_ffn_logits"): """
Final-layer fusion ending with vocabulary projection and selected token.
""",
    ("voxtral_metal.h", "vox_metal_shared_alloc"): """
Allocates CPU/GPU-visible cache storage, falling back to zeroed heap memory when
Metal is unavailable.
""",
    ("voxtral_metal.h", "vox_metal_shared_free"): """
Frees a tracked shared Metal allocation or its fallback heap allocation.
""",
    ("voxtral_metal.h", "vox_metal_decoder_full_step"): """
Encodes all decoder layers, RoPE, cache writes, attention, logits, and argmax in
one command buffer.
""",
    ("voxtral_metal.h", "vox_metal_warmup_bf16"): """
Preconverts one BF16 weight to eliminate first-use latency.
""",
    ("voxtral_metal.h", "vox_metal_warmup_decoder_ops"): """
Preconstructs shape-specific MPS operations and decoder weight caches.
""",
    ("voxtral_metal.h", "vox_metal_warmup_merged_2"): """
Caches a two-matrix merged BF16 layout used by fused kernels.
""",
    ("voxtral_metal.h", "vox_metal_warmup_merged_3"): """
Caches a three-matrix merged BF16 layout.
""",
    ("voxtral_metal.h", "vox_metal_encoder_full_step"): """
Runs every encoder transformer layer plus final norm for one new chunk while
updating shared rolling caches.
""",
    ("voxtral_metal.h", "vox_metal_decoder_prefill_step"): """
Processes a multi-position prompt/audio prefix through all decoder layers and
updates cache length.
""",
    ("voxtral_metal.h", "vox_metal_memory_used"): """
Returns memory tracked by Metal caches/allocations for diagnostics, not total
process resident memory.
""",
    ("voxtral_metal.m", "f16_cache_entry_t"): """
One BF16-to-FP16 cache record keyed by the source CPU pointer and retaining the
converted `MTLBuffer`. Element count documents the cached extent.
""",
    ("voxtral_metal.m", "clear_f16_cache"): """
Under the cache mutex, releases every converted weight buffer, clears keys, and
resets the count during global shutdown.
""",
    ("voxtral_metal.m", "merged_cache_entry_t"): """
Caches one concatenated FP16 weight buffer by its source pointer tuple for fused
matrix operations.
""",
    ("voxtral_metal.m", "clear_merged_cache"): """
Drops all merged buffers and keys. Access is serialized by the runtime's
inference ownership around initialization/shutdown.
""",
    ("voxtral_metal.m", "weight_cache_entry_t"): """
Cache record for immutable FP32 norms/biases copied into shared Metal buffers;
size joins pointer identity in the key.
""",
    ("voxtral_metal.m", "clear_weight_cache"): """
Mutex-protected release of cached FP32 GPU buffers.
""",
    ("voxtral_metal.m", "pool_buffer_t"): """
One reusable activation allocation with capacity and checkout flag. Buffers are
rounded up to reduce repeated allocation for nearby tensor sizes.
""",
    ("voxtral_metal.m", "clear_activation_pool"): """
Releases pooled activations and resets capacity/use metadata at shutdown.
""",
    ("voxtral_metal.m", "clear_matmul_op_cache"): """
Drops the dictionary of shape/configuration-specific
`MPSMatrixMultiplication` objects under its mutex.
""",
    ("voxtral_metal.m", "vox_metal_available"): """
Returns the global initialization flag used by C fallback selection.
""",
    ("voxtral_metal.m", "vox_metal_sgemm("): """
Copies float activation input into pooled shared storage, reuses a cached float
weight buffer and shape-specific MPS operation, waits for completion, then
copies float output back and releases activations.
""",
    ("voxtral_metal.m", "vox_metal_fused_qkv_bf16"): """
Reuses three converted weight buffers and one uploaded input, encodes three MPS
products into one command buffer, then downloads Q/K/V and returns all scratch
buffers to the pool.
""",
    ("voxtral_metal.m", "vox_metal_fused_wo_ffn_bf16"): """
Allocates the complete residual/normalization/hidden scratch set, encodes output
projection through the second residual in one command buffer, copies updated x
back, and releases every pooled buffer.
""",
    ("voxtral_metal.m", "vox_metal_decoder_end"): """
Intentionally keeps persistent `g_dec_x` allocated for reuse across tokens; end
closes the logical step, while shutdown owns actual release.
""",
    ("voxtral_metal.m", "vox_metal_decoder_norm_qkv"): """
Allocates normalized/QKV scratch, encodes the shared helper from persistent x,
waits once, splits the contiguous QKV result into caller arrays, then returns
scratch to the pool.
""",
    ("voxtral_metal.m", "vox_metal_decoder_wo_ffn_logits"): """
Encodes the final persistent-x layer transition, final normalization,
vocabulary projection, and argmax; downloads four-byte token identity and
optionally the full logits.
""",
    ("voxtral_metal.m", "vox_metal_encoder_attention"): """
Uploads Q/K/V, dispatches one tiled compute grid across all encoder heads and
query blocks, downloads output after one completion wait, and releases scratch.
""",
    ("voxtral_metal.m", "vox_metal_shared_free"): """
Finds a tracked shared pointer, releases its Metal buffer, and fills the removed
slot from the final table entry; unknown pointers use ordinary `free` because
they came from fallback allocation.
""",
    ("voxtral_metal.m", "vox_metal_warmup_bf16"): """
Forces one conversion-cache lookup during model preparation, turning live
first-use work into startup work.
""",
    ("voxtral_metal.m", "vox_metal_warmup_merged_2"): """
Materializes one two-source merged FP16 buffer before decoding begins.
""",
    ("voxtral_metal.m", "vox_metal_warmup_merged_3"): """
Materializes one three-source merged FP16 buffer before live use.
""",
    ("voxtral_shaders.metal", "encoder_attention_kv_f16_qstrided"): """
Encoder attention variant reading strided Q projections and FP16 cached K/V.
The grid tiles query rows per head and converts half cache values during float
accumulation.
""",
    ("voxtral_shaders.metal", "batched_kv_cache_copy_f16"): """
Copies contiguous batched K/V float projections into FP16 cache rows at the
specified start position, one thread per scalar.
""",
    ("voxtral_shaders.metal", "batched_kv_cache_copy_strided_f16"): """
Same float-to-FP16 cache write when K and V occupy slices of a larger merged QKV
row; explicit source strides/offsets avoid deinterleaving on CPU.
""",
    ("voxtral_metal.m", "bf16_to_f16"): """
Converts one bfloat16 weight to IEEE half precision by rebiasing the exponent
from bias 127 to bias 15 and shifting the 7-bit mantissa left by 3 to fill f16's
10-bit field. Zero/subnormal bf16 exponents collapse to signed zero, 0xFF maps to
inf or a quiet NaN. It runs on the CPU during weight conversion because
MPSMatrixMultiplication accepts f32/f16, not bf16.
""",
    ("voxtral_metal.m", "get_cached_bf16_as_f16_buffer"): """
Returns a shared-storage MTLBuffer of f16 weights for a given bf16 CPU pointer,
converting once via bf16_to_f16 and caching the result keyed by the source
pointer under a pthread mutex. The conversion uploads with newBufferWithBytes
(StorageModeShared, zero-copy CPU/GPU). The cache holds up to 512 entries; cleared
by clear_f16_cache at shutdown.
""",
    ("voxtral_metal.m", "get_merged_f16_2"): """
Concatenates two bf16 weight matrices into one contiguous f16 buffer so a fused
matmul can produce both outputs in a single MPS call. It resolves each half
through the f16 cache, then memcpys the two f16 blocks into a fresh shared buffer
cached by the pair of source pointers. Note the lookup only compares key1/key2.
""",
    ("voxtral_metal.m", "get_merged_f16_3"): """
Like get_merged_f16_2 but concatenates three bf16 matrices (e.g. Wq, Wk, Wv) into
one f16 buffer for a single merged QKV matmul. The cache key only stores key1 and
key2 (not key3) and the lookup ignores the third pointer, so two triples sharing
the first two pointers will alias -- a real latent bug worth noting.
""",
    ("voxtral_metal.m", "get_cached_weight_buffer"): """
Caches f32 buffers (norm weights, biases, ada_scale) keyed by CPU pointer and
byte size, uploaded once in StorageModeShared. Cache hits require both pointer and
size to match. If the 512-entry table is full it allocates an uncached buffer and
returns it (leaked from the cache's perspective). clear_weight_cache nils all
entries at shutdown.
""",
    ("voxtral_metal.m", "pool_get_buffer"): """
Hands out a reusable shared activation buffer of at least the requested size,
scanning for a free pool slot whose capacity fits before allocating. New
allocations are rounded up to 64 KiB or 1 MiB granularity to maximize reuse,
marked in_use, and recorded in the 64-slot pool. If the pool is full it falls
back to a one-off buffer. Mutex-guarded.
""",
    ("voxtral_metal.m", "pool_release_buffer"): """
Marks a pooled activation buffer free again by finding it by identity and
clearing its in_use flag; the buffer stays allocated for later reuse. This is a
fixed-slot free-list: release does not deallocate, it just returns the slab to
the pool. clear_activation_pool nils every slot at shutdown.
""",
    ("voxtral_metal.m", "get_cached_matmul_op"): """
Returns a cached MPSMatrixMultiplication keyed by a string of (transposeLeft,
transposeRight, resultRows, resultColumns, interiorColumns, alpha, beta), creating
one on miss. Reusing the operator across tokens avoids repeated kernel setup for
identically shaped matmuls. This runtime uses MPSMatrixMultiplication, not
MPSGraph.
""",
    ("voxtral_metal.m", "init_shaders"): """
Compiles the embedded Metal source (decoded from the voxtral_shaders_metal byte
array via an NSUTF8 string) into one MTLLibrary with fast math enabled, then
builds a compute pipeline state for every kernel by name. Each pipeline is
optional: a missing function leaves its global nil and callers fall back.
""",
    ("voxtral_metal.m", "vox_metal_init"): """
Creates the system default MTLDevice and command queue, requiring at least Apple
GPU family 6 (rejecting older GPUs), then calls init_shaders. Sets g_initialized
only on success so vox_metal_available and every kernel entry can early-out when
Metal is unavailable. Idempotent.
""",
    ("voxtral_metal.m", "vox_metal_shutdown"): """
Tears down all GPU state: clears the f16, merged, f32-weight, activation-pool, and
matmul-op caches, nils every pipeline and the persistent decoder x buffer,
releases tracked shared allocations, then drops the library, queue, and device.
After this g_initialized is 0 so the engine can be re-initialized.
""",
    ("voxtral_metal.m", "vox_metal_sgemm_bf16"): """
Computes C[M,N] = A[M,K] @ B[N,K]^T with f32 A and bf16 B by fetching B's cached
f16 buffer, copying A into a pooled buffer, and running one cached
MPSMatrixMultiplication (transposeRight=YES). Encodes to a single command buffer,
commits, and waits for completion before copying C back from the shared result
buffer. Activation buffers are returned to the pool; weights stay cached.
""",
    ("voxtral_metal.m", "vox_metal_fused_norm_qkv_bf16"): """
Fuses RMSNorm and the three QKV projections into one command buffer: a rms_norm
compute dispatch (one threadgroup per row, 256 threads) writes x_norm, then three
cached MPSMatrixMultiplication encodes produce Q, K, V from the shared normalized
input against cached f16 weights. One commit/wait, then copies all three outputs
back. Only one CPU/GPU sync per layer.
""",
    ("voxtral_metal.m", "vox_metal_fused_ffn_bf16"): """
Runs the full SwiGLU FFN in one command buffer: gate = input @ w1^T and up =
input @ w3^T (two MPS matmuls), then silu(gate) and gate *= up as compute
dispatches, then output = gate @ w2^T. Intermediates stay in pooled GPU buffers;
only input is uploaded and only output read back after the single commit/wait.
""",
    ("voxtral_metal.m", "vox_metal_fused_logits_bf16"): """
Final-token head in one command buffer: rms_norm(x), then logits = x_norm @
tok_emb^T (vocab x dim f16 weights), then the argmax_f32 kernel writes the best
token id into a 4-byte buffer. Returns the argmax after commit/wait and only
copies the full logits array back if logits_out is non-NULL, avoiding a
vocab-sized transfer when only the token is needed.
""",
    ("voxtral_metal.m", "vox_metal_decoder_start"): """
Uploads the initial decoder hidden state x into the persistent g_dec_x shared
buffer, reallocating it only if too small so it survives across tokens. This
buffer is the heart of the persistent-x decoder path: subsequent per-layer
kernels read and update it in place on the GPU, avoiding per-layer CPU copies.
""",
    ("voxtral_metal.m", "encode_wo_ffn_steps"): """
Helper that appends the wo+FFN block for one layer onto an already-open command
buffer, reading attn_out and updating g_dec_x in place. It prefers fused custom
kernels when available (decoder_wo_residual, decoder_ffn_gate, decoder_w2_residual)
and otherwise falls back to MPS matmuls with separate silu/mul/add dispatches.
Uses memoryBarrierWithScope between dependent dispatches in the same encoder.
""",
    ("voxtral_metal.m", "encode_norm_qkv_steps"): """
Helper that appends rms_norm(g_dec_x) followed by a single merged QKV matmul onto
an open command buffer. The three weight matrices are concatenated via
get_merged_f16_3 so one MPSMatrixMultiplication yields Q, K, V contiguously; the
caller slices them with byte offsets. M is fixed at 1 (single decode token).
""",
    ("voxtral_metal.m", "vox_metal_decoder_wo_ffn_next_qkv"): """
Fuses one layer's wo+FFN with the next layer's norm+QKV into a single command
buffer, the key cross-layer fusion that halves command buffers per token. It calls
encode_wo_ffn_steps (updating g_dec_x) then encode_norm_qkv_steps for the next
layer, commits once, and copies the next layer's Q/K/V back.
""",
    ("voxtral_metal.m", "vox_metal_batched_attention"): """
Classic three-stage attention in one command buffer using MPS matmuls: per-head
strided QK^T into a scores buffer, one causal_softmax compute dispatch over all
(head, query) rows, then per-head scores@V. Q/K/V/out use strided MPSMatrix views
into packed buffers via per-head byte offsets, with GQA mapping kv_h = h/gqa_ratio.
""",
    ("voxtral_metal.m", "vox_metal_shared_alloc"): """
Allocates zeroed memory backed by a shared-storage MTLBuffer and records the
(ptr, buffer) pair so GPU kernels can later look up the buffer by its CPU pointer
via find_shared_buffer; this is how the KV cache becomes addressable from both
sides with zero copies. Falls back to plain calloc when Metal is down or the
8-slot tracking table is full.
""",
    ("voxtral_metal.m", "find_shared_buffer"): """
Linear-scans the shared-allocation table to recover the MTLBuffer that backs a
given CPU pointer, returning nil if untracked. Used by the monolithic
decoder/encoder steps to bind the KV cache (allocated via vox_metal_shared_alloc)
directly as a GPU buffer without re-uploading.
""",
    ("voxtral_metal.m", "vox_metal_decoder_full_step"): """
Runs an entire decode token, all 26 layers plus the logits head, in ONE command
buffer over the persistent g_dec_x buffer. Per layer it appends the previous
layer's wo+FFN (skipped on layer 0), the merged norm+QKV, then a single compute
encoder doing RoPE on Q and K, K/V writes into the shared KV cache at the
per-layer/per-position offset, and single-token decoder_attention (one threadgroup
of 32 threads per head); memoryBarrierWithScope separates RoPE, cache write, and
attention. After the loop it appends the last layer's wo+FFN, final rms_norm,
logits matmul, and argmax, commits once, and advances ctx->kv_cache_len.
""",
    ("voxtral_metal.m", "vox_metal_encoder_full_step"): """
Processes new_len positions through all 32 encoder layers in one command buffer,
operating on a pooled bufX uploaded once. Per layer: rms_norm, one merged QKV
matmul, then a compute encoder doing strided bias-add, batched strided RoPE,
strided KV-cache writes, and Q-tiled encoder_attention_qstrided over all heads;
then wo matmul, residual+ffn-norm, and the merged FFN. A final rms_norm writes
the result into bufXnorm, which is copied back.
""",
    ("voxtral_metal.m", "vox_metal_decoder_prefill_step"): """
Prefill path for M>1 decode tokens: like the encoder full step but with decoder
dims (head_dim=128, GQA 32/8) and 26 layers, reusing the
encoder_attention_qstrided kernel (or its kv-f16 variant) for batched causal
attention. Single commit/wait, copies x back, and advances kv_cache_len by
seq_len. Returns early if the required strided/f16 pipelines are missing.
""",
    ("voxtral_metal.m", "vox_metal_warmup_decoder_ops"): """
Comprehensive load-time warmup: pre-creates the cached MPSMatrixMultiplication
operators for the decode, encoder, and prefill shapes, pre-uploads all f32
norm/bias/ada_scale buffers, and pre-merges layer-0 weights. It then encodes and
waits on dummy matmuls so the GPU compiles each pipeline variant before real audio
arrives, eliminating first-token stalls.
""",
    ("voxtral_metal.m", "vox_metal_memory_used"): """
Reports the total bytes held by the GPU weight caches by summing num_elements*2
across the f16 cache and size across the f32 weight cache, each under its own
mutex. It deliberately ignores the activation pool and merged cache, so it
reflects persistent weight residency rather than peak usage.
""",
    ("voxtral_shaders.metal", "rms_norm"): """
Computes out = x * rsqrt(mean(x^2)+eps) * weight with one threadgroup per row.
Each thread strides over the hidden dimension accumulating a partial sum of
squares into shared memory, then a 256-wide tree reduction yields the row sum; the
row is rescaled by weight in a second strided pass. The two barriers bracket the
reduction, and the threadgroup width need not divide hidden.
""",
    ("voxtral_shaders.metal", "silu"): """
In-place SiLU activation x = x/(1+exp(-x)), one thread per element with a gid < n
bounds guard so an over-dispatched grid leaves the tail untouched. Plain
elementwise map over a flat buffer.
""",
    ("voxtral_shaders.metal", "gelu"): """
In-place tanh-approximation GELU, one thread per element with a gid < n guard.
Uses the standard 0.5*x*(1+tanh(sqrt(2/pi)*(x+0.044715*x^3))) form with the
sqrt(2/pi) constant baked in as 0.7978845608.
""",
    ("voxtral_shaders.metal", "add_inplace"): """
Elementwise a[i] += b[i] over n elements, one thread per index with a bounds
guard. Used between MPS matmuls to fold residual adds without a CPU round-trip.
""",
    ("voxtral_shaders.metal", "mul_inplace"): """
Elementwise a[i] *= b[i] over n elements, one thread per index with a bounds
guard. Used to apply the SwiGLU gate*up product on the GPU.
""",
    ("voxtral_shaders.metal", "ada_scale_mul"): """
Adaptive-RMSNorm conditioning: x[i] *= (1 + scale[i % stride]), so a per-channel
scale vector of length stride is broadcast across rows. One thread per element
with a bounds guard.
""",
    ("voxtral_shaders.metal", "argmax_f32"): """
Single-threadgroup argmax over a float array. Each lane scans a strided slice
tracking its local best value and index into parallel shared arrays, then a
256-wide tree reduction keeps the (value, index) pair with the larger value. Lane
0 writes the winning index to out[0].
""",
    ("voxtral_shaders.metal", "causal_softmax"): """
Numerically stable masked softmax over attention scores, one threadgroup per
(query, head) flattened as group_id = head*seq_q + qi. Phase 1 masks each key
outside [valid_start, valid_end] to -INFINITY (causal limit plus optional sliding
window) and reduces the row max; phase 2 exponentiates and reduces the sum; phase
3 normalizes by 1/(sum+1e-10). All three passes stride over seq_k.
""",
    ("voxtral_shaders.metal", "rope_apply"): """
Applies rotary position embedding in place to one position's [n_heads, head_dim]
vector, one thread per (head, half-dim) pair. Each thread rotates the adjacent
pair at indices 2i, 2i+1 by the (cos,sin) read from freqs. Threads beyond
n_heads*head_dim/2 return early.
""",
    ("voxtral_shaders.metal", "kv_cache_copy"): """
Writes kv_dim freshly projected f32 K (or V) values into the large cache buffer at
float_offset+gid, one thread per element with a gid < kv_dim guard. The host
computes float_offset from layer, position, and kv_dim so each token lands at its
slot.
""",
    ("voxtral_shaders.metal", "kv_cache_copy_f16"): """
Same as kv_cache_copy but narrows each f32 value to half on store into an f16
cache, halving KV memory bandwidth and footprint. Bounds-guarded by kv_dim.
""",
    ("voxtral_shaders.metal", "decoder_attention"): """
Single-token (seq_q=1) attention, one threadgroup of 32 threads (one SIMD group)
per query head, with head_dim=128 so each lane owns 4 dims. It walks keys in
[valid_start, valid_end] (causal plus sliding window) in one online-softmax pass:
each step computes a SIMD-reduced q.k dot, rescales the running max/sum/accumulators
by exp(old_max-new_max), and adds the weighted V. Keeping everything in one SIMD
group avoids any threadgroup barriers.
""",
    ("voxtral_shaders.metal", "decoder_attention_f16"): """
Identical online-softmax single-token attention to decoder_attention but reads the
K and V caches as half and converts to float in the dot product and V accumulation.
Q stays f32. Used when ctx->kv_cache_fp16 selects the f16 KV path.
""",
    ("voxtral_shaders.metal", "encoder_attention"): """
Q-tiled batched attention: one threadgroup per (head, query-block of ATTN_BQ=8
queries). Each thread holds one head_dim element of all 8 queries; per key it
computes 8 cooperative SIMD dot products, reduces across SIMD groups into 8 scaled
scores, then updates each query's online-softmax state and accumulates V. Per-query
causal/window masking is applied inside the loop. Supports head_dim 64 or 128.
""",
    ("voxtral_shaders.metal", "encoder_attention_kv_f16"): """
Same Q-tiled batched attention as encoder_attention but with half-precision K and
V (converted to float on load); Q and output stay f32. Used for the f16 KV-cache
encoder/prefill path.
""",
    ("voxtral_shaders.metal", "encoder_attention_qstrided"): """
Q-tiled batched attention variant that reads Q from a strided/offset layout, so Q
can be a column slice of a wider packed QKV buffer while output is written to its
own contiguous tensor. Otherwise identical online-softmax, GQA, and masking logic
to encoder_attention. This lets the monolithic encoder/prefill steps feed the
merged QKV buffer directly without deinterleaving Q.
""",
    ("voxtral_shaders.metal", "bias_add"): """
Adds a per-column bias to a row-major [seq_len, dim] tensor as data[gid] +=
bias[gid % dim], one thread per element with a bounds guard. The modulo broadcasts
the dim-length bias across all rows.
""",
    ("voxtral_shaders.metal", "bias_add_strided"): """
Bias-add restricted to a column slice of a wider row stride: thread gid maps to
(row, col) within chunk_cols and writes data[row*row_stride + col_offset + col] +=
bias[col]. Lets the host add wq/wv biases to just the Q or V slice of a packed QKV
buffer without touching the other slices.
""",
    ("voxtral_shaders.metal", "batched_rope_apply"): """
Applies RoPE to a whole [seq_len, n_heads, head_dim] batch, one thread per
(position, head, half-dim) triple decoded from a flat gid. Per-position (cos,sin)
pairs are indexed from freqs, and the adjacent pair is rotated. Over-dispatched
threads past total return early.
""",
    ("voxtral_shaders.metal", "batched_rope_apply_strided"): """
Batched RoPE that targets a column slice of a strided buffer: the element base
becomes pos*row_stride + col_offset + head*head_dim, so Q or K can be rotated in
place inside a packed QKV layout. Frequency indexing and the pairwise rotation
match batched_rope_apply.
""",
    ("voxtral_shaders.metal", "batched_kv_cache_copy"): """
Copies a contiguous [seq_len, kv_dim] block of new K or V into the cache at
cache_offset+gid, one thread per element over total with a guard. The host
computes cache_offset from layer and starting position.
""",
    ("voxtral_shaders.metal", "batched_kv_cache_copy_strided"): """
Gathers a column slice from a strided source (the K or V slice of a packed QKV
buffer) into a contiguous cache region: thread gid maps to (row, col) within
chunk_cols and reads from the strided source, writing cache[cache_offset+gid].
Lets the monolithic steps write K and V to cache directly from the merged QKV
buffer.
""",
    ("voxtral_shaders.metal", "deinterleave"): """
Extracts one contiguous column slice [M, chunk_cols] from a wider [M, src_stride]
source: thread gid maps to (row, col) and copies src[row*src_stride + col_offset +
col] into a packed dst[gid]. A generic strided-to-contiguous gather used to
separate a packed projection into its component matrices.
""",
    ("voxtral_shaders.metal", "silu_mul_merged"): """
Fused SwiGLU activation over a merged [M, hidden*2] row where columns [0:hidden)
are the gate and [hidden:2*hidden) the up projection. Each thread computes silu on
its gate element and multiplies by the matching up element, writing back into the
gate half in place. Avoids two separate silu and mul passes.
""",
    ("voxtral_shaders.metal", "decoder_ffn_gate"): """
M=1 fused FFN gate: one threadgroup per output channel row computes both
dot(x, w1[row]) and dot(x, w3[row]) from the merged w1/w3 buffer. Threads
cooperatively load x and half weights as float4/half4, SIMD-reduce each partial,
combine across SIMD groups, and lane 0 writes out[row] = silu(d1)*d3. Replaces a
matmul plus separate silu and mul for the single-token decode path.
""",
    ("voxtral_shaders.metal", "decoder_w2_residual"): """
M=1 fused down-projection with residual: one threadgroup per output dim row
computes dot(gate[0:hidden], w2[row]) via cooperative float4/half4 loads and a
SIMD-plus-threadgroup reduction, then lane 0 does x[row] += dot. Folds the w2
matmul and the residual add into a single dispatch over g_dec_x.
""",
    ("voxtral_shaders.metal", "decoder_wo_residual"): """
M=1 fused attention output projection with residual: one threadgroup per dim row
computes dot(attn[0:q_dim], wo[row]) using cooperative loads and a reduction, then
lane 0 adds it into x[row]. Folds the wo matmul and residual add into one dispatch,
the first step of the persistent-x decoder block.
""",

    # --- Tests as behavioural specifications, plus remaining services ------
    ("AudioLevelMeterTests.swift", "class AudioLevelMeterTests"): """
Specification for PCM16 level calculation, including normalization and malformed
odd-byte input behavior.
""",
    ("AudioLevelMeterTests.swift", "testSilenceProducesZeroLevel"): """
Pins that all-zero PCM produces exactly zero RMS and peak rather than a floor or
NaN.
""",
    ("AudioLevelMeterTests.swift", "testPeakAndRMSUseNormalizedPCMValues"): """
Pins conversion from signed 16-bit samples to unit-scale peak and RMS values.
""",
    ("AudioLevelMeterTests.swift", "testOddTrailingByteIsIgnored"): """
Pins safe handling of a final byte that cannot form a complete `Int16` sample.
""",
    ("AudioLevelMeterTests.swift", "func pcmData"): """
Test fixture helper encoding native `Int16` values into the same byte layout the
meter consumes.
""",
    ("CVoxtralBridgeTests.swift", "class CVoxtralBridgeTests"): """
Exercises the stable C ABI without loading a successful full model: defaults,
structured failure, and revision provenance.
""",
    ("CVoxtralBridgeTests.swift", "testPinnedRevisionIsExposed"): """
Pins that the compiled upstream revision is nonempty and available through the
bridge for reproducible diagnostics.
""",
    ("CaptionCorrectionValidatorTests.swift", "class CaptionCorrectionValidatorTests"): """
Executable policy for accepting notation-preserving proofreading while rejecting
answers, control markup, translation, and excessive rewrites.
""",
    ("CaptionCorrectionValidatorTests.swift", "testAcceptsConservativeFrenchCorrection"): """
Pins that ordinary French punctuation, capitalization, and agreement fixes pass
without changing meaning.
""",
    ("CaptionCorrectionValidatorTests.swift", "testAcceptsSpokenComplexityAndEqualityNotation"): """
Pins accepted conversion of spoken algorithmic complexity and equality into
compact notation.
""",
    ("CaptionCorrectionValidatorTests.swift", "testAcceptsTechnicalNotationInsideQuestion"): """
Pins that notation inside a question may be normalized while preserving the
question form.
""",
    ("CaptionCorrectionValidatorTests.swift", "testAcceptsDenseUnicodeMathLogicAndCodeRendering"): """
Pins science-mode acceptance of a dense but meaning-preserving mixture of
Unicode mathematics, logic, and code notation.
""",
    ("CaptionCorrectionValidatorTests.swift", "testScienceModeAcceptsCompactSetMembership"): """
Pins the intended “n belongs to natural numbers” transformation into `n ∈ ℕ`.
""",
    ("CaptionCorrectionValidatorTests.swift", "testRejectsAnswerAppendedToQuestion"): """
Pins rejection when a model preserves the question but appends an answer.
""",
    ("CaptionCorrectionValidatorTests.swift", "testRejectsTranslationOrUnrelatedRewrite"): """
Pins edit-distance/semantic-shape defenses against translation or unrelated
replacement text.
""",
    ("CaptionOverlayGeometryTests.swift", "class CaptionOverlayGeometryTests"): """
Pure geometry specification for minimum size and containment inside arbitrary
visible display rectangles.
""",
    ("CaptionOverlayGeometryTests.swift", "testClampShrinksFrameThatExceedsDisplay"): """
Pins that an oversized overlay is reduced to the available margin-inset display
instead of remaining partly off-screen.
""",
    ("CaptionTimelineTests.swift", "class CaptionTimelineTests"): """
Specification for provisional replacement, finalized sequence identity, and
correction-state preservation.
""",
    ("CaptionTimelineTests.swift", "testSequenceRemainsMonotonicAfterProvisionalUpdates"): """
Pins that any number of provisional revisions do not consume sequence numbers;
only finalized segments advance the dense order.
""",
    ("CaptionTransformationTests.swift", "class CaptionTransformationTests"): """
Specification for the character edit-distance percentage shown in diagnostics.
""",
    ("CaptionTransformationTests.swift", "testIdenticalCaptionHasZeroPercentTransformation"): """
Pins the identity case at exactly zero percent.
""",
    ("CaptionTransformationTests.swift", "testCompletelyDifferentSameLengthCaptionHasFullTransformation"): """
Pins equal-length complete substitution at one hundred percent.
""",
    ("ClassroomSessionTests.swift", "class ClassroomSessionTests"): """
Specification for legal session phases and the phases in which captions may
enter the timeline.
""",
    ("LocalCaptionServerTests.swift", "class LocalCaptionServerTests"): """
Loopback integration tests for capability entropy, read-only snapshots, viewer
authentication, student tickets, source binding, and rate limiting.
""",
    ("LocalCaptionServerTests.swift", "testPairingTokenHasExpectedEntropyAndEncoding"): """
Pins a 32-byte random token rendered as exactly 64 hexadecimal characters.
""",
    ("LocalCaptionServerTests.swift", "func readyURL"): """
Starts a test server and awaits a ready/client-connected callback with a bounded
continuation, skipping when the environment cannot expose Wi-Fi.
""",
    ("LocalCaptionServerTests.swift", "func studentURL"): """
Enables questions and awaits the independently generated student capability URL.
""",
    ("LocalCaptionServerTests.swift", "func nextSubmission"): """
Bridges the asynchronous accepted-question callback into one awaited test value.
""",
    ("LocalCaptionServerTests.swift", "func post"): """
Constructs and sends a loopback HTTP POST, returning status/body so authorization
and rate-limit behavior can be asserted.
""",
    ("ProcessMemoryTests.swift", "class ProcessMemoryTests"): """
Boundary test for Darwin resident-memory sampling.
""",
    ("ProcessMemoryTests.swift", "testReadsCurrentProcessResidentMemory"): """
Pins that the current process produces a nonzero measurement on supported macOS
instead of being reported as absent or zero.
""",
    ("SessionExportTests.swift", "class SessionExportTests"): """
Specification for WAV layout, stopping-phase final drain, transcript timing, and
archive file creation.
""",
    ("SessionExportTests.swift", "testFinalDrainCaptionIsAcceptedWhileStopping"): """
Pins the intentional exception that finalized model drain may append a caption
after the session has entered `stopping`.
""",
    ("SessionExportTests.swift", "func readUInt16"): """
Little-endian assertion helper for 16-bit WAV header fields.
""",
    ("SessionExportTests.swift", "func readUInt32"): """
Little-endian assertion helper for 32-bit WAV sizes and rates.
""",
    ("SessionExportTests.swift", "extension JSONDecoder"): """
Test-only decoder configured with the same ISO-8601 date strategy used by
archive JSON.
""",
    ("SpokenOverlayCommandTests.swift", "class SpokenOverlayCommandTests"): """
Dense specification for exact, tolerant, partial, multi-command, and
lecture-text-preserving voice recognition.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesFixedShowAndHidePhrases"): """
Pins the configured show/hide phrases and their actions.
""",
    ("SpokenOverlayCommandTests.swift", "testFixedPhraseDoesNotConfuseOrdinaryActionWords"): """
Pins that ordinary occurrences of action vocabulary without the trigger phrase
do not control the overlay.
""",
    ("SpokenOverlayCommandTests.swift", "testDetectsPartialFixedPhrase"): """
Pins provisional suppression when recognition contains only a prefix of the
configured trigger.
""",
    ("SpokenOverlayCommandTests.swift", "testDetectsPartialSecondWordWithoutDisplayingIt"): """
Pins suppression through a partially recognized second trigger word.
""",
    ("SpokenOverlayCommandTests.swift", "testDoesNotSuppressUnrelatedSecondWord"): """
Pins that a shared first word followed by unrelated speech remains lecture text.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesMultipleCommandsInSpokenOrder"): """
Pins ordered extraction when several control phrases occur in one transcript.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesShowHideAndClearCommandsInSpokenOrder"): """
Pins the full three-action ordering and complete removal of command text.
""",
    ("SpokenOverlayCommandTests.swift", "testClearCommandRetainsAdjacentLectureText"): """
Pins that clear is consumed while neighboring lecture words survive.
""",
    ("SpokenOverlayCommandTests.swift", "testDetectsPartialClearCommand"): """
Pins provisional holdback for an incomplete clear phrase.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesNextStudentQuestionCommand"): """
Pins the spoken action that pops and presents the next anonymous question.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesDismissStudentQuestionCommand"): """
Pins the separate action that clears the currently presented question.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesObservedCesAmesLumiereVariant"): """
Pins tolerance for an actual Voxtral homophone/transcription variant observed
during testing.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesHyphenatedShowCommand"): """
Pins normalization across hyphenated versus spaced trigger transcription.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesAccentsAndHideSynonym"): """
Pins accent normalization and the configured hide-action synonym.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesTolerantSingularAndAgreementVariant"): """
Pins bounded grammatical-number/agreement variation without opening arbitrary
fuzzy matching.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesOneCharacterTranscriptionError"): """
Pins the accepted edit-distance budget for one-character ASR error.
""",
    ("SpokenOverlayCommandTests.swift", "testRetainsLectureTextFromSameSegment"): """
Pins preservation of lecture text surrounding a recognized control phrase.
""",
    ("SpokenOverlayCommandTests.swift", "testRetainsTextAfterCommand"): """
Pins preservation specifically for words following a command.
""",
    ("SpokenOverlayCommandTests.swift", "testDoesNotRecognizeTriggerWithoutAction"): """
Pins that a trigger phrase alone is insufficient; a valid action word is
required before executing control.
""",
    ("VoxtralProtocolTests.swift", "class VoxtralProtocolTests"): """
Pure parser tests for tolerant extraction from remote WebSocket JSON shapes.
""",
    ("VoxtralProtocolTests.swift", "testFindStringUsesRequestedKeyPriority"): """
Pins deterministic key priority when several candidate transcript fields exist.
""",
    ("VoxtralProtocolTests.swift", "testNestedTranscriptIsFound"): """
Pins recursive discovery of transcript text inside nested dictionaries/arrays.
""",
    ("SessionExportTests.swift", "testWAVHeaderDescribesPCM16MonoAudio"): """
Pins the 44-byte canonical WAV header layout for the archive format: RIFF/WAVE
magic, a chunk size of data bytes plus 36, 16000 Hz, one channel, 16 bits per
sample, and a data-subchunk size equal to the PCM byte count. Locks the exact
little-endian offsets so the header stays byte-compatible with players and the
benchmark loader.
""",
    ("SessionExportTests.swift", "testTranscriptUsesRelativeTimestampsAndPreservesRawText"): """
Pins that exported transcripts timestamp each segment relative to session start
and that the raw recognized text is preserved verbatim even when correction is
disabled. Also pins that the JSON round-trips through an ISO-8601 decoder with
rawText and startSeconds intact.
""",
    ("SessionExportTests.swift", "testArchiveWritesAudioAndTranscriptFiles"): """
Pins the end-to-end archive contract: start creates the session directory,
appended PCM is written to audio.wav with its header rewritten to the true byte
count on finalize, and finalize emits transcript.txt, transcript.json, and
session.json into the same directory it returns.
""",
    ("CaptionCorrectionValidatorTests.swift", "testPreservesQuestionInsteadOfAnsweringIt"): """
Pins that a spoken question may be punctuated and normalized (elision, O(log n)
notation) but must remain a question, so the corrected caption still ends in a
question mark rather than being answered.
""",
    ("CaptionCorrectionValidatorTests.swift", "testScienceModeStillRejectsAnswerAppendedToQuestion"): """
Pins that science mode does not relax the question-integrity rule: appending an
answer after a question still throws questionWasAnswered, so the looser symbol
budget never permits answering.
""",
    ("CaptionCorrectionValidatorTests.swift", "testRejectsLatexForPlainTextOverlay"): """
Pins that LaTeX markup is rejected with containsControlMarkup, since the overlay
renders plain text and must not leak typesetting commands.
""",
    ("CaptionCorrectionValidatorTests.swift", "testRejectsDirectAnswerPrefix"): """
Pins that replacing a question with a direct answer is rejected with
answerLikeResponse, blocking the model from treating the caption as a prompt.
""",
    ("CaptionCorrectionValidatorTests.swift", "testRejectsReasoningMarkup"): """
Pins that chain-of-thought markup such as a think block is rejected with
containsControlMarkup, preventing model reasoning tokens from reaching the caption.
""",
    ("CaptionCorrectionValidatorTests.swift", "testRequestRemainsQuotedCaptionData"): """
Pins that an imperative request spoken by the lecturer is treated as caption text
to be punctuated, not as a command to act on, returning the cleaned question
unchanged.
""",
    ("CaptionTransformationTests.swift", "testReportsPartialCharacterTransformation"): """
Pins that a single-character insertion is scored as 20 percent, confirming the
metric is edit distance normalized by the longer length.
""",
    ("SpokenOverlayCommandTests.swift", "testFixedPhraseRetainsAdjacentLectureText"): """
Pins that text spoken in the same segment after a fixed command phrase is stripped
of the phrase and returned as remainingText, so the command is consumed but the
lecture sentence survives.
""",
    ("SpokenOverlayCommandTests.swift", "testRemovesAllCommandsButRetainsLectureText"): """
Pins that recognizeAll removes every command phrase from a multi-sentence
transcript while concatenating the surviving lecture text in the final command's
remainingText.
""",
    ("SpokenOverlayCommandTests.swift", "testRejectsDistantWordsDespiteValidAction"): """
Pins the fuzzy-match ceiling: a trigger word too far from the configured phrase is
rejected even when a valid action word follows, preventing false triggers.
""",
    ("SpokenOverlayCommandTests.swift", "testDetectsPartialTriggerForProvisionalSuppression"): """
Pins potential-command detection: leading fragments of the trigger are flagged for
provisional suppression, but a trigger embedded mid-sentence is not.
""",
    ("ClassroomSessionTests.swift", "testSessionLifecycle"): """
Pins the legal phase machine: starting to listening to paused back to listening to
stopping to idle, each transition returning true, with endedAt set once the
session reaches idle via finish.
""",
    ("ClassroomSessionTests.swift", "testCaptionsAreAcceptedOnlyWhileListening"): """
Pins that finalizeCaption returns nil and records nothing unless the session is
listening: captions before markListening and after pause are dropped, so the
timeline holds only the one accepted segment.
""",
    ("LocalCaptionServerTests.swift", "testPairingTokenComparisonRequiresExactValue"): """
Pins that token comparison requires exact equality: identical tokens match, but a
length change or any single-character mutation fails, the constant-time equality
guard against near-miss tokens.
""",
    ("LocalCaptionServerTests.swift", "testRemoteSnapshotEncodingContainsNoControlCapability"): """
Pins that the JSON pushed to viewers carries only finalized, provisional,
sessionActive, and revision keys and round-trips losslessly, ensuring remote
viewers receive read-only caption state with no control surface.
""",
    ("LocalCaptionServerTests.swift", "testServerRequiresTheGeneratedPairingToken"): """
Pins that the caption page is gated on the generated pairing token: a wrong token
gets 404 while the published pairing URL returns 200 with the captions page. Skips
when no Wi-Fi listener is available.
""",
    ("LocalCaptionServerTests.swift", "testStudentQuestionSubmissionRequiresTicketAndIsRateLimited"): """
Pins the full student-question security flow: submissions require enabling, a
per-session student URL, and a ticket minted from /student-ticket; a posted
question is delivered to the Mac callback with 202, a second post is rate-limited
with 429, and an invalid ticket is rejected with 401.
""",
    ("CaptionTimelineTests.swift", "testFinalizePreservesRawTextDuringCorrection"): """
Pins that applying a correction updates only displayText while rawText keeps the
original recognized string, preserving the unedited transcript for export and
audit.
""",
    ("CaptionTimelineTests.swift", "testFailedCorrectionLeavesRawCaptionVisible"): """
Pins that a failed correction leaves the raw caption as the visible displayText
and marks the segment correctionState .failed, so a correction error never blanks
or hides the original caption.
""",
    ("CaptionOverlayGeometryTests.swift", "testClampKeepsFrameInsideVisibleDisplay"): """
Pins that clamped keeps the overlay frame within a 12-point inset of the visible
display bounds on all sides, even for a frame starting far off-screen, so the
caption window is never lost off a display.
""",
    ("CaptionOverlayGeometryTests.swift", "testClampEnforcesMinimumSize"): """
Pins the minimum overlay size: a tiny frame is grown to 420 by 120 points,
guaranteeing the caption window stays legible.
""",
    ("CVoxtralBridgeTests.swift", "testDefaultOptionsAreSuitableForRealtimeCaptions"): """
Pins the default streaming options the app relies on: 320 ms delay, 1.0 s
processing interval, continuous mode on, and a 2000-token decode context cap, the
realtime captioning baseline.
""",
    ("CVoxtralBridgeTests.swift", "testMissingModelDirectoryReturnsStructuredError"): """
Pins that loading a missing model directory returns a null model with status
CCV_STATUS_MODEL_FILES_MISSING and a human-readable error naming the expected
consolidated.safetensors file, so the bridge reports structured load failures
rather than crashing.
""",
    ("AudioDeviceCatalog.swift", "func inputDevices("): """
Enumerates all CoreAudio devices, keeps those exposing an input stream, and maps
each to a MicrophoneDevice keyed by its stable device UID (falling back to the
name), sorted case-insensitively. The UID, not the transient AudioObjectID, is
what the app persists.
""",
    ("AudioDeviceCatalog.swift", "struct MicrophoneDevice"): """
A UI-facing pair of stable Core Audio device UID and human-readable name.
`Identifiable` lets SwiftUI use the UID as row identity; `Hashable` supports
selection collections; `Sendable` permits the value to cross concurrency
boundaries without exposing an `AudioObjectID`.
""",
    ("AudioDeviceCatalog.swift", "enum AudioDeviceCatalog"): """
A caseless enum used as a namespace for stateless Core Audio queries. Swift
cannot instantiate it because no cases exist, giving C-like module functions
while retaining access control and type-qualified names.
""",
    ("AudioDeviceCatalog.swift", "defaultInputDeviceUID"): """
Resolves the system's current default input object and immediately translates
its volatile numeric ID to the stable string UID persisted by the app. Failure
at either Core Audio query is represented as `nil`.
""",
    ("AudioDeviceCatalog.swift", "func resolveDeviceID("): """
Resolves a persisted UID back to a live AudioObjectID, falling back to the system
default input when the UID is nil or empty, and only matching devices that still
expose an input stream. Bridges saved preferences to the volatile device id the
audio unit needs.
""",
    ("AudioDeviceCatalog.swift", "setInputDevice"): """
Assigns the chosen hardware object to AUHAL's global current-device property.
Core Audio's C API requires a mutable pointer even though the input ID is a
value, hence the local copy. The raw `OSStatus` is returned so the capture
transaction can attach the failing setup step.
""",
    ("AudioDeviceCatalog.swift", "defaultInputDeviceID"): """
Queries the system object for `kAudioHardwarePropertyDefaultInputDevice`.
Selector, global scope, and main element identify the property; success still
requires a nonzero device ID because zero is not usable hardware.
""",
    ("AudioDeviceCatalog.swift", "allDeviceIDs"): """
Implements Core Audio's two-call variable-size pattern: ask for byte count,
allocate an exactly sized Swift array, then fill it through an unsafe mutable
buffer pointer. Any status failure returns an empty catalog rather than partially
initialized identifiers.
""",
    ("AudioDeviceCatalog.swift", "deviceHasInput"): """
Reads the input-scope `AudioBufferList` and accepts a device only when at least
one buffer reports channels. The raw allocation is aligned for the C structure
and released with `defer`, including every early return.
""",
    ("AudioDeviceCatalog.swift", "stringProperty"): """
Fetches a Core Foundation string property such as UID or name. Core Audio owns
the returned `CFString`, so `takeUnretainedValue` borrows it rather than
consuming a reference count; bridging then produces a Swift `String`.
""",
    ("MicrophoneCaptureService.swift", "enum MicrophonePermission"): """
Normalizes AVFoundation authorization into the four states the dashboard needs.
Keeping permission separate from capture errors prevents “not yet asked” from
being presented as a hardware failure.
""",
    ("MicrophoneCaptureService.swift", "enum MicrophoneCaptureError"): """
The setup transaction's typed failure surface: missing selected device, absent
AUHAL component, a named C configuration step plus `OSStatus`, or an unusable
stream format. `LocalizedError` converts those cases to actionable UI text.
""",
    ("MicrophoneCaptureService.swift", "class AudioRenderContext"): """
The retained object passed through AUHAL's opaque callback pointer. It groups
the Audio Unit, source/destination formats, converter, destination closure, and
processing queue so the C callback needs one stable lifetime token.
`@unchecked Sendable` relies on callback/teardown ordering, not compiler proof.
""",
    ("MicrophoneCaptureService.swift", "init("): """
Stores already constructed audio objects and the escaping handler in the
callback context. There is no setup logic here: all fallible construction stays
in `configure`, which can unwind before ownership is published.
""",
    ("MicrophoneCaptureService.swift", "class MicrophoneCaptureService"): """
Owns one AUHAL capture instance and one retained callback context. A lock
protects publication/removal of those two lifetime roots; the processing queue
owns ordinary delivery after the real-time callback has copied audio bytes.
""",
    ("MicrophoneCaptureService.swift", "struct State"): """
The minimal lock-protected lifetime record. Audio Unit and callback context are
removed together before teardown, so repeated `stop` calls observe an empty
state and cannot release either resource twice.
""",
    ("MicrophoneCaptureService.swift", "init()"): """
Constructs the model's fixed target format: interleaved signed PCM16, mono,
16 kHz. Failure is a programming/platform invariant violation and therefore a
precondition failure, not a recoverable per-session error. A dispatch-specific
key later prevents synchronously waiting on the processing queue from itself.
""",
    ("MicrophoneCaptureService.swift", "deinit"): """
Calls the idempotent stop path as a final ownership backstop. Correct application
shutdown stops explicitly; `deinit` ensures an unexpectedly released service
still removes callbacks before releasing their context.
""",
    ("MicrophoneCaptureService.swift", "func permission("): """
Maps AVFoundation's current authorization status without prompting. The
`@unknown default` branch treats future framework cases conservatively as
restricted, preserving exhaustive behavior across newer SDKs.
""",
    ("MicrophoneCaptureService.swift", "requestPermission"): """
Returns immediately for decided states and suspends only for the system prompt
when authorization is undetermined. `async` models that user interaction without
blocking the main thread.
""",
    ("MicrophoneCaptureService.swift", "func configure("): """
Completes AUHAL setup as a transaction: enable input bus 1, disable output bus
0, select hardware, read and install the callback-side format, create the
converter/context, install the C callback, initialize, and start. The retained
context is published only after every fallible step succeeds.
""",
    ("MicrophoneCaptureService.swift", "requireNoError"): """
Adapts Core Audio's integer `OSStatus` convention to Swift throwing control flow
while preserving the human-readable setup step. This keeps the configure
sequence linear and ensures one catch block performs rollback.
""",
    ("SessionArchiveService.swift", "struct SessionArchiveMetadata"): """
The stable JSON summary written beside audio and transcripts. It records domain
identity/times plus latched runtime choices and final byte count, without
embedding model weights, mutable services, or provisional caption state.
""",
    ("SessionArchiveService.swift", "enum SessionArchiveError"): """
Represents the WAV format's 32-bit data-size limit explicitly. The check occurs
before narrowing `UInt64` accounting to the `UInt32` header field, preventing
silent wraparound in long recordings.
""",
    ("SessionArchiveService.swift", "class SessionArchiveService"): """
Queue-confined owner of incremental archive I/O. `@unchecked Sendable` is valid
because callers never access `state`; synchronous and continuation-based methods
route every mutation through the private utility queue.
""",
    ("SessionArchiveService.swift", "struct State"): """
Tracks the in-progress directory, WAV path/handle, exact PCM byte count, and the
first asynchronous write failure. Capturing a failure in state lets `appendAudio`
remain nonthrowing while `finalize` still reports data loss.
""",
    ("SessionArchiveService.swift", "func cancel("): """
Synchronously closes the current file and clears all archive state. A synchronous
barrier is appropriate here because callers need cancellation complete before
starting another archive or releasing the service.
""",
    ("SessionArchiveService.swift", "closeAudioFile"): """
Closes the optional handle and clears it after success. Centralizing this
operation makes start, cancel, and error cleanup share the same ownership rule
instead of closing a stale copied handle independently.
""",
    ("SessionArchiveService.swift", "func perform<"): """
Bridges serial dispatch work into Swift `async throws` with a checked
continuation. Exactly one queue closure resumes the continuation with either the
operation value or error; the generic result must be `Sendable` because it
crosses back from the archive queue.
""",
    ("SessionArchiveService.swift", "directoryName"): """
Builds a filesystem-sortable local timestamp plus the first eight UUID
characters. The POSIX locale prevents user locale settings from changing
digits/separators, while the UUID suffix avoids collisions between sessions
started in the same second.
""",
    ("SessionArchiveService.swift", "func start("): """
Serializes archive setup onto its private utility queue: closes any open audio
file, creates the timestamped session directory, writes a zero-length WAV header
to audio.wav, and opens a seek-to-end write handle, returning the directory.
Resets all per-session state so a prior recording cannot leak in.
""",
    ("SessionArchiveService.swift", "func appendAudio("): """
Asynchronously appends PCM16 mono bytes to the open audio handle and accumulates
the byte count; on a write error it records the failure, closes the handle, and
nils it so later appends are no-ops and finalize can surface the error.
""",
    ("SessionArchiveService.swift", "func finalize("): """
On the archive queue, propagates any earlier write failure, enforces the 4 GB PCM
limit, rewrites the WAV header with the true data byte count, then writes
transcript.txt, transcript.json, and a pretty-printed session.json before clearing
state. Returns the directory, or nil if no session was started.
""",
    ("VoxtralRealtimeService.swift", "enum VoxtralRealtimeError"): """
The remote backend's two local failures: an endpoint with a non-WebSocket scheme
and a dictionary that cannot be serialized as JSON. Network closure and server
errors arrive later as `TranscriptionEvent.failed` values because they belong to
the asynchronous event stream rather than the synchronous start call.
""",
    ("VoxtralRealtimeService.swift", "class VoxtralRealtimeService"): """
Bridges an external WebSocket protocol to the same
`StreamingTranscriptionService` contract as embedded Voxtral. It subclasses
`NSObject` for URLSession delegation and promises `@unchecked Sendable`; a
`Mutex<State>` supplies the synchronization that the compiler cannot infer.
""",
    ("VoxtralRealtimeService.swift", "enum ConnectionState"): """
The lock-protected transport phase. Keeping `connecting` distinct from
`disconnected` prevents an early callback or repeated start from being treated
as an established session, while `connected` gates audio commit and sends.
""",
    ("VoxtralRealtimeService.swift", "struct State"): """
Collects every field that must change atomically under one mutex: transport
objects, event continuation, queued startup frames, commit/generation flags,
provisional text, and stop intent. A single aggregate avoids deadlocks and
inconsistent snapshots that several independently locked properties could
produce.
""",
    ("VoxtralRealtimeService.swift", "func events("): """
Creates the ordered `AsyncStream` consumed by the app model and stores its
continuation under the mutex. `onTermination` removes only that output handle;
transport shutdown remains explicit so a view task ending cannot silently
destroy an active backend.
""",
    ("VoxtralRealtimeService.swift", "func sendAudio("): """
Marks that a commit-worthy buffer exists, base64-encodes owned PCM bytes, and
sends the protocol's append event. Base64 is required because this backend uses
JSON text messages rather than binary WebSocket frames; it increases payload
size by roughly one third.
""",
    ("VoxtralRealtimeService.swift", "func stop("): """
Under the mutex, records user intent, detaches the current task/session, and
resets protocol state while preserving the event continuation. Cancellation and
URLSession invalidation occur after unlocking, avoiding delegate re-entry while
the mutex is held.
""",
    ("VoxtralRealtimeService.swift", "didOpenWithProtocol"): """
Accepts the open callback only when it belongs to the currently stored task,
then changes state to connected, emits the common lifecycle event, and starts
the recursive receive loop. Identity rejection makes callbacks from a replaced
session harmless.
""",
    ("VoxtralRealtimeService.swift", "didCloseWith"): """
Converts WebSocket close code and optional UTF-8 reason into the shared terminal
path. Normal closure and going-away are not reported as failures; abnormal codes
retain their numeric value for diagnosis before disconnection is emitted.
""",
    ("VoxtralRealtimeService.swift", "didCompleteWithError"): """
Handles URLSession task completion that may arrive in addition to a WebSocket
close callback. Cancellation is recognized by `NSURLErrorCancelled` and treated
as expected; task identity and disconnected-state checks in `handleTerminal`
deduplicate racing terminal callbacks.
""",
    ("VoxtralRealtimeService.swift", "func listen("): """
Arms one asynchronous receive. On success it parses the message and recursively
arms the next receive only if the task is still current and connected; on
failure it enters terminal handling. This explicit re-arming is how
`URLSessionWebSocketTask` forms a continuous message loop.
""",
    ("VoxtralRealtimeService.swift", "private func handle(_ message:"): """
Normalizes text and binary WebSocket messages to `Data`, then asks
`JSONSerialization` for a dictionary. Unknown future message cases and malformed
JSON are ignored rather than crashing the stream or fabricating caption events.
""",
    ("VoxtralRealtimeService.swift", "func handle(_ json:"): """
The realtime event dispatcher: on session.created it marks the session ready once
and flushes any queued frames; transcription delta events append to and emit
provisional text; done events clear generationInProgress and emit the final text;
error events emit a failure. Tolerates three vendor event-name spellings per phase.
""",
    ("VoxtralRealtimeService.swift", "func handleTerminal("): """
Single funnel for connection teardown: ignores stale or already-disconnected
tasks, resets state while preserving the event continuation, invalidates the
session, and emits a failure (suppressed for user-initiated stops) followed by
disconnected. Ensures terminal state is delivered at most once per task.
""",
    ("VoxtralRealtimeService.swift", "func commit("): """
Commits the audio buffer only when connected, with uncommitted audio present, and
no generation already in flight; it atomically clears hasUncommittedAudio and sets
generationInProgress before sending input_audio_buffer.commit, preventing
overlapping generations.
""",
    ("VoxtralRealtimeService.swift", "private func send(_ event:"): """
Validates and serializes a protocol dictionary before passing text to the
transport layer. Serialization failure becomes a typed transcription failure;
no partially encoded frame is sent.
""",
    ("VoxtralRealtimeService.swift", "func sendText("): """
Queues frames produced before the server's `session.created` event, otherwise
returns the current task and sends outside the mutex. Send completion reports
failure through the same terminal funnel, avoiding callback work while the lock
is held.
""",
    ("VoxtralRealtimeService.swift", "func emit("): """
Reads the current `AsyncStream` continuation under the mutex and yields after
the protected access. Events are values, so the consumer cannot mutate backend
state through the stream.
""",
    ("VoxtralRealtimeService.swift", "func reset("): """
Returns the aggregate to its disconnected defaults and optionally preserves the
event continuation across transport restarts. Centralizing reset prevents one
flag, queued frame, or provisional caption from leaking into the next session.
""",
    ("VoxtralRealtimeService.swift", "func findString("): """
Recursively searches a JSON value for the first non-empty string under any of the
priority keys, checking a dictionary's keys in order before descending into its
values and array elements. Lets the event handler extract transcript text across
differing vendor payload shapes.
""",
    ("download_voxtral_model.py", "def default_destination"): """
Builds the per-user Application Support location expected by the dashboard's
default model setting. Returning a `Path` keeps path joining platform-aware; no
directory is created until `main` has parsed any override.
""",
    ("download_voxtral_model.py", "def download"): """
Downloads one artifact through an adjacent `.partial` file. Existing bytes
produce an HTTP Range request; if the server does not confirm a content range,
the function restarts safely in write mode. Eight-MiB chunks bound memory, and
atomic `os.replace` publishes only a complete file.
""",
    ("download_voxtral_model.py", "def sha256"): """
Streams a file through SHA-256 in eight-MiB chunks, so hashing the checkpoint
does not duplicate gigabytes in memory. The digest records provenance; it proves
identity only when compared with a separately trusted expected value.
""",
    ("download_voxtral_model.py", "def main"): """
Parses the destination, creates it, downloads only missing or empty required
files, and writes a manifest of repository, time, byte sizes, and hashes. That
manifest identifies the concrete local model installation used by benchmarks
and classroom sessions.
""",
    ("main.swift", "struct Arguments"): """
Fully parsed benchmark configuration with explicit defaults. Separating this
value from execution keeps timed inference independent of command-line parsing.
""",
    ("main.swift", "struct PCMRecording"): """
Owned mono PCM16 bytes plus derived duration, guaranteeing the benchmark feeds
the bridge's required format.
""",
    ("main.swift", "enum BenchmarkError"): """
Typed usage and WAV-format failures rendered through `LocalizedError`.
""",
    ("main.swift", "func take("): """
Removes a named flag and its following value from mutable arguments, throwing
usage if the value is absent. Leftover tokens expose unknown options.
""",
    ("main.swift", "func parseArguments("): """
Parses the benchmark command line into Arguments: --model-dir and --audio are
required, the rest optional with defaults. Consumes each recognized flag and
throws usage if any unknown argument remains.
""",
    ("main.swift", "func loadPCMRecording("): """
Loads and validates a WAV file by walking its RIFF chunks: requires RIFF/WAVE
magic, reads the fmt chunk, locates the data chunk, and rejects anything that is
not uncompressed 16-bit 16 kHz mono PCM. Honors the chunk word-alignment padding
when advancing.
""",
    ("main.swift", "readUInt16"): """
Decodes a little-endian 16-bit WAV field from a previously bounds-checked offset.
""",
    ("main.swift", "readUInt32"): """
Decodes a little-endian 32-bit RIFF size/rate field.
""",
    ("main.swift", "drainText"): """
Polls bridge text until `NO_TEXT`, resizes on `BUFFER_TOO_SMALL`, concatenates
UTF-8 pieces, and records first-text latency exactly once.
""",
    ("main.swift", "func words("): """
Normalizes text into lowercase metric words for Levenshtein comparison. This is
not the model's tokenizer.
""",
    ("main.swift", "func wordAccuracy("): """
Computes word accuracy as one minus the word-level Levenshtein distance normalized
by the reference length, using a rolling two-row DP. An empty reference scores 1
only if the transcript is also empty, and the result is floored at zero.
""",
}
