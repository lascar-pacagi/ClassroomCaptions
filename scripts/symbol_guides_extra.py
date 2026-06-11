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
Appends an inbound `SubmittedClassroomQuestion` to the pending queue and
refreshes the overlay so the pending badge updates. The 500-entry cap is purely
a memory bound: the server admits at most 100 questions per hour, so the cap is
unreachable unless a multi-hour backlog is left entirely unmoderated. Runs on
the main actor via the server's question callback.
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
concurrent tickets (at most 4 per source) with a 4-hour life, the layered
rate-limit windows (10 s per ticket, 8 per source per 5 min, 30 global per
minute, 100 accepted per sliding hour), and the 10 s request-completion
timeout that defeats slowloris-style slot exhaustion.
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
Issues one rate-limit ticket per request: it first sweeps expired tickets,
refuses with 503 once maximumTickets live tickets exist, and refuses with 429
once one source already holds maximumTicketsPerSource live tickets — so a
single device looping the route cannot exhaust the table for the class. A
fresh makeToken value keys a StudentTicket recording the source ID, a
now+ticketLifetime expiry, and an empty submission history. A failed token
draw degrades to 503 rather than issuing a weak ticket.
""",
    ("LocalCaptionServer.swift", "submitQuestion"): """
Validates and rate-limits one question. The ticket must exist, be unexpired, and
bind to the same sourceID that obtained it (else 401), preventing ticket sharing
across peers. The body is JSON-decoded and run through normalizedQuestion (else
422). Four sliding windows are checked: a 10 s per-ticket gap, 8 per source per
5 min, 30 globally per minute, and 100 accepted per hour — a window rather than
a lifetime cap, so an active class recovers instead of losing questions for the
rest of the session; any breach yields 429. Only on success is the question
forwarded with a 202.
""",
    ("LocalCaptionServer.swift", "beginEventStream"): """
Establishes the single SSE caption stream. A newer authenticated viewer
pre-empts an existing stream (the old connection is cancelled before the slot
is reassigned), so a stuck or hijacked stream is reclaimed by simply reopening
the page rather than restarting sharing. The new stream gets the SSE headers
(nosniff, no-referrer, a 1 s retry hint), an immediate replay of the last
snapshot so a late joiner is not blank, the heartbeat timer, and a
clientConnected status report.
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
names the bad path, launchFailed wraps the spawn error or an early child exit (reported with its exit status, whatever it is), and
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
-sTCP:LISTEN` in a detached task, so a slow lsof can never stall the main actor
or the caption path. Any lsof failure, non-zero exit, or unparseable output
yields nil rather than a wrong PID.
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
persistent encoder/decoder scratch, ada_scale, the cached tokenizer, and finally
closes the safetensors mapping. Borrowed bf16 pointers are owned by the mapping
and not freed here. Null-safe and idempotent.
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
Allocates a zeroed stream and initializes the incremental mel context with 32
streaming-pad tokens of leading silence. The Tekken tokenizer is borrowed from
the context, parsed once on the first stream and reused by every later one so a
session restart does not re-parse the 14 MB tekken.json. Sets up the circular
token queue, the decoder scratch, single-best alternative mode, and the default
2-second processing interval. On any allocation failure it tears down partial
state and returns NULL.
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
context, adapter buffer, token queue, decoder scratch, and conv-stem boundary
buffers. The tokenizer and the shared vox_ctx_t are borrowed and not freed here;
the context owns the tokenizer, so queued token strings remain valid until
vox_free.
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
continuous mode, and the decode-context cap from options. It also preallocates
the decoder KV cache at the restart bound plus a margin rather than the full
8192-position window, saving roughly 740 MB at the default context; the cache
still grows on demand. On stream-init failure it sets status, frees the handle,
and returns NULL.
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
provisionalText. Tokens arrive in bursts (one decode pass yields about a
dozen), so the drain emits one token-rate metrics event and one provisional
caption event per burst rather than per token — each provisional event costs a
full main-actor caption-pipeline pass. Stops cleanly on NO_TEXT and surfaces any other status
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
Doubles kv_cache_max (starting from 256 if the cache was never allocated, so a
failed initial allocation cannot loop the doubling forever) until it covers the
requirement, allocates fresh K/V buffers
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
Public entry that feeds new positions to the encoder in batches of at most
VOX_ENC_INC_MAX_BATCH. The shared (Metal) KV cache is preallocated at
VOX_ENC_WINDOW plus that batch size and cannot grow, so a single oversized call
would fail and silently discard audio; batching keeps results identical to
separate smaller feeds while concatenating their outputs into one buffer.
""",
    ("voxtral_encoder.c", "encoder_forward_incremental_batch"): """
One bounded encoder step: compacts/grows the KV cache for the incoming frames,
runs RoPE at logical positions enc_kv_pos_offset+cache_len, projects Q/K/V only
for the new positions, appends K/V to the cache, and attends each new query over
the full window. After 32 layers and the final norm it returns the new positions'
[batch,1280] output; the GPU path runs all layers in one command buffer when
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
converting once and caching the result keyed by the source pointer under a
pthread mutex. The conversion runs through convert_bf16_to_f16 (NEON, eight
elements per iteration, parallelized across cores for large tensors) directly
into the shared buffer, with no intermediate malloc. The cache holds up to 512
entries; cleared by clear_f16_cache at shutdown.
""",
    ("voxtral_metal.m", "get_merged_f16_2"): """
Concatenates two bf16 weight matrices into one contiguous f16 buffer so a fused
matmul can produce both outputs in a single MPS call. Each component is converted
directly into its slice of the merged buffer — deliberately not through the f16
cache, which would permanently keep an individual copy of every component that
the default paths never read again (about 5.3 GB of duplicated weights across the
encoder and decoder stacks).
""",
    ("voxtral_metal.m", "get_merged_f16_3"): """
Like get_merged_f16_2 but concatenates three bf16 matrices (Wq, Wk, Wv) into one
f16 buffer for a single merged QKV matmul, converting each component directly
into its slice. The cache entry records all three source pointers, so distinct
triples can never alias.
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
Reports the total bytes held by the GPU weight caches by summing the f16 cache,
the f32 weight cache, and the merged-buffer cache. It deliberately ignores the
transient activation pool, so it reflects persistent weight residency rather
than peak usage.
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


# Pedagogical rewrites (2026-06-10): the reader is an experienced C programmer
# with no Swift, ML, networking, GPU, or signal-processing background. These
# entries override earlier notes of the same key; facts preserved, teaching added.
PEDAGOGY_REWRITES = {
    ('ClassroomCaptionsApp.swift', '@1'): """
A single `import SwiftUI` serves the whole file: a Swift import loads a
compiled module rather than textually including a header, and on macOS the
SwiftUI module also exposes the AppKit names (such as `NSApplication`) that
the Quit button below relies on.
""",
    ('ClassroomAppModel.swift', '@1'): """
Five imports map the coordinator's reach: `AppKit` for screens, Finder
reveal, and app-lifecycle notifications; `ClassroomCaptionsCore` for the pure
domain library (session, timeline, spoken-command recognizer); `Foundation`
for `URL`, `Date`, `UserDefaults`, and `NotificationCenter`; `Observation`
for the `@Observable` macro; and `Synchronization` for the `Mutex` that
guards the audio capture gate.
""",
    ('ClassroomAppModel.swift', 'class ClassroomAppModel'): """
Main-actor observable coordinator for all user-visible state and
cross-service workflows; everything the dashboard and overlay show is a
property here. `@Observable` drives SwiftUI invalidation, `@MainActor` is the
actual synchronization rule, and service internals stay on their own
queues/actors, crossing this boundary only as values or owned `Data`. In the
property list, `private(set)` means any code may read but only this class may
write, and a trailing `?` marks an optional (it holds a value or `nil`, and
must be checked before use), used for not-yet-known facts such as the
first-caption latency. The settings that follow pair `UserDefaults` (macOS's
per-app preference store, read at startup with `??` supplying a default) with
`didSet` — a property observer that runs after every assignment — so each
change is written straight back and survives relaunch without a save button.
""",
    ('ClassroomAppModel.swift', '@129'): """
This stretch finishes the persisted settings — live diagnostics and the five
spoken-command phrases ('Bonjour soleil bleu' and friends), each using the
same `UserDefaults`-plus-`didSet` pattern, with `showLiveDiagnostics` also
starting or stopping the diagnostics poller on each change — plus two plain
in-memory settings for recording and the archive folder. It then declares the
long-lived service objects (overlay controller, microphone capture, both
Voxtral backends, session archive, Gemma controller) and the stored `Task`
handles kept so running jobs can be cancelled later. These service and task
fields are `@ObservationIgnored`: excluded from `@Observable` change tracking
because they are machinery, not state any view draws.
""",
    ('ClassroomAppModel.swift', 'struct DisplayChoice'): """
A stable UI projection of one `NSScreen` (AppKit's object describing an
attached display): the Core Graphics display ID for persistence, the
localized name for the picker, and the global desktop frame (captured but currently unused by the UI).
A `struct` is a value type — assignment copies it, as in C — and `let` fields
are immutable once set. The names after the colon are protocol conformances
(interfaces): `Identifiable` gives SwiftUI a stable `id` for picker rows, and
`Equatable` synthesizes `==` so changes are detectable. Because it holds no
mutable `NSScreen` reference, a disconnected projector cannot leave a
dangling screen object inside UI state.
""",
    ('ClassroomAppModel.swift', 'enum TranscriptionBackend'): """
The user-selectable transcription implementation: in-process Metal inference
or an external WebSocket server. Unlike a C enum, a Swift enum is a full type
that can carry methods and properties. `: String` gives each case a readable
raw value that persists cleanly; `CaseIterable` synthesizes the `allCases`
list the settings picker displays; `Identifiable` lets the value itself serve
as its identity (`var id: Self { self }`). `title` is a computed property — a
getter re-run on every access — so presentation text lives beside the cases
while workflow code still branches exhaustively with `switch`.
""",
    ('ClassroomAppModel.swift', 'struct PendingCorrection'): """
Minimal FIFO work item: immutable segment identity plus the correction mode
latched when queued; the worker re-reads caption and context by UUID,
avoiding a second mutable copy of the segment. The fields that follow are
per-session bookkeeping: `audioInputEnabled = Mutex(false)` is a
lock-protected boolean — the capture gate the audio callback checks and every
start/pause/stop path flips — and `captionServer: LocalCaptionServer!` is an
implicitly unwrapped optional, its `!` promising assignment in `init` before
first use. The `var name: Type { ... }` declarations are computed properties,
recomputed on each read, so booleans such as `isListening` always reflect the
session's current phase; their `guard let` (unwrap an optional or exit early)
and `if case` (match a single enum case) are idioms this file uses throughout.
""",
    ('ClassroomAppModel.swift', 'init()'): """
Runs once at app launch, before any session: construction creates services
once and installs value-carrying callbacks, but starts no microphone or
model resources (the persisted settings were already loaded by the property
initializers above). The termination observer registers with
`NotificationCenter` (a process-wide broadcast registry) using a trailing
closure — a closure argument written after the call's closing parenthesis —
so quitting by any route still stops the spawned Gemma child;
`MainActor.assumeIsolated` asserts the code is already on the main thread,
permitting synchronous access to main-actor state. The caption server's
callbacks originate off the main actor and re-enter it with
`Task { @MainActor in }` before touching observable state; the final `if`
chains migrate voice phrases saved by older builds to the current
'Bonjour soleil' wording.
""",
    ('ClassroomAppModel.swift', 'func refreshDisplays('): """
Runs at construction and again when the dashboard's Refresh Displays button
is pressed: rebuilds the display list from current AppKit screens, repairs a
missing or stale selection, and reprojects the overlay, handling projector
connection and desktop rearrangement without retaining obsolete screen
objects. `map` builds a new array by applying its closure to every
`NSScreen`, yielding value-type `DisplayChoice` rows; in `contains(where:)`,
`$0` is shorthand for the closure's single argument. If the remembered
display ID no longer exists, selection falls back to the first screen so the
overlay always has a real target.
""",
    ('ClassroomAppModel.swift', 'func pauseOrResume'): """
Mid-session control, between start and stop: toggles the live session between
listening and paused. `guard var session` is this file's recurring edit
idiom — copy the optional value-type session into a local mutable variable
(exiting if there is none), mutate the copy, then publish it back with
`self.session = session`, so observers see one atomic change. Pausing gates
audio input off via the `audioInputEnabled` mutex and flushes buffered audio
so no half-utterance leaks across the pause; resuming re-enables input. Each
branch proceeds only if the session's own phase transition succeeds, then
refreshes the overlay; in any other phase neither branch acts, and the method merely republishes the unchanged session and refreshes the overlay.
""",
    ('ClassroomAppModel.swift', 'observeTranscriptionEvents'): """
Wired once in `init`, before any session exists: cancels any earlier
observers, then creates one long-lived task per backend. Each backend
publishes an `AsyncStream` (a typed asynchronous queue of values), and
`for await` iterates it, suspending until the next event arrives — the
asynchronous analogue of looping over reads from a pipe. Every delivery is
filtered against the backend latched for the active session, so a late event
from the inactive service cannot mutate the current transcript.
""",
    ('ClassroomAppModel.swift', 'handleVoxtralEvent'): """
Runs for every event a backend emits while a session is alive: this is the
reducer — one function that folds each incoming event into current state —
from backend events to domain transitions. The `switch` shows that Swift enum
cases carry payloads: `case .provisional(let text)` matches the case and
binds the text it carries, where C would switch on a tag and then read a
union field. `.connected` ends stage one of start and launches the microphone
handoff; provisional and finalized text pass through spoken-command
interception before timeline mutation; metrics update diagnostics
independently; disconnect and failure are interpreted in light of whether
stop was expected.
""",
    ('ClassroomAppModel.swift', 'startMicrophoneAfterVoxtralConnection'): """
Stage two of the start transaction, entered when Voxtral reports `connected`:
only now is microphone permission requested, the value-type
`ClassroomSession` created, the archive opened, and hardware capture
started — permission denial or capture failure unwinds everything back to
idle. The audio callback captures the backend and recording flags latched at
start, so it keeps serving the original start attempt's configuration. Each
chunk arrives as owned PCM data on the capture queue, where it is archived
and sent to Voxtral synchronously (per-chunk tasks would not preserve frame
order); meter and byte accounting hop to the main actor and publish at
roughly 15 Hz, and audio is forwarded only while the capture gate stays open.
""",
    ('ClassroomAppModel.swift', 'consumeOverlayVoiceCommand'): """
Every transcript, provisional or finalized, passes through this filter before
it can reach the timeline — via `handleVoxtralEvent` while live, and once
more for the text drained at stop. It recognizes completed command phrases,
applies them in spoken order, and returns the caption with those phrases
removed; a provisional fragment that could still grow into a command yields
an empty string, so a half-spoken control phrase never flashes on screen as
lecture content. Because hypotheses are revised as recognition refines,
executed actions are tracked element-wise per utterance — '...bleu' becoming
'...rouge' re-executes the corrected command instead of counting as already
handled — and the tracking list resets when text finalizes.
""",
    ('ClassroomAppModel.swift', 'visibleOverlayLines'): """
Presentation helper called on every overlay refresh and remote publish during
live captioning: it returns the last `limit` finalized caption lines,
honoring the spoken 'clear' boundary. It walks the timeline backwards,
stopping at `overlayMinimumVisibleSequence` — captions older than the
boundary stay hidden — or once `limit` lines are collected, then reverses the
result back into reading order. As the doc comment explains, sequence numbers
grow with position, so the visible lines always form a suffix of the timeline
and the scan costs O(limit) per caption event instead of filtering a whole
lecture's history. `limit: Int = 3` is a default argument (callers may omit
it), and `if let overlayMinimumVisibleSequence` is shorthand optional
binding: it unwraps the field into a same-named local constant.
""",
    ('ClassroomAppModel.swift', 'extension NSScreen'): """
An `extension` adds members to an existing type from outside its definition —
here a computed `displayID` property on AppKit's `NSScreen` — and `private`
keeps it visible to this file only. It bridges AppKit's loosely typed
device-description dictionary to the stable `CGDirectDisplayID` used for
selection and per-display geometry keys: `as?` attempts a cast and yields an
optional, and `?? 0` substitutes a default when the entry is missing or has
the wrong type.
""",
    ('ProcessMemory.swift', '@1'): """
`Darwin` exposes the raw C system interfaces this file wraps —
`proc_pidinfo`, `getpid`, and the `proc_taskinfo` struct — while `Foundation`
supplies the base Swift platform layer. Nothing executes here; imports only
make a module's declarations visible.
""",
    ('ProcessMemory.swift', 'enum ProcessMemory'): """
A stateless namespace for reading a process's resident memory via the Darwin
`proc_pidinfo` API; the diagnostics panel uses it to report both the app's
own footprint and the separate Gemma MLX server's. An enum with no cases is
Swift's idiom for a pure namespace: it can never be instantiated, so its
`static` functions are reachable only as `ProcessMemory.name(...)` — the
closest C analogue is a prefix-named group of free functions.
""",
    ('ProcessMemory.swift', 'residentSizeBytes'): """
Calls `proc_pidinfo(PROC_PIDTASKINFO)` into a `proc_taskinfo` struct and
returns its `pti_resident_size`, or `nil` if the call does not return the
exact expected struct size — which is how this API signals failure or a
denied/dead pid; the size-equality check is the standard `proc_pidinfo`
success test. `withUnsafeMutablePointer(to:)` is Swift's bridge to C
out-parameters: it hands the closure a real C pointer to `info` that is valid
only inside that closure, rather than letting an address escape as `&info`
would in C. `MemoryLayout<proc_taskinfo>.size` is Swift's `sizeof`.
""",
    ('AudioDeviceCatalog.swift', '@1'): """
`AudioToolbox` supplies the Audio Unit C API used to configure AUHAL,
`CoreAudio` supplies the C API for enumerating hardware devices and querying
their properties, and `Foundation` is Swift's base library (strings, sorting,
basic value types). Nothing executes here; the imports only make those APIs
visible to the declarations below.
""",
    ('MicrophoneCaptureService.swift', '@1'): """
`AVFoundation` provides the audio formats, the converter, and the
microphone-permission API; the `@preconcurrency` prefix imports it with Swift's
newer concurrency checks relaxed because the framework predates those
annotations. `AudioToolbox` and `CoreAudio` expose the AUHAL C interface,
`Foundation` is Swift's base library, and `Synchronization` supplies the
`Mutex` type used inside `convert`.
""",
    ('SessionArchiveService.swift', '@1'): """
`ClassroomCaptionsCore` is the app's own domain library, providing the session
model, the transcript document, and the `PCM16WAVHeader` helper used below;
`Foundation` supplies file I/O (`FileManager`, `FileHandle`), JSON encoding,
and date formatting.
""",
    ('AudioDeviceCatalog.swift', 'func inputDevices('): """
Enumerates every Core Audio device, keeps those exposing an input stream, and
maps each to a `MicrophoneDevice` keyed by its stable device UID, sorted
case-insensitively by name. The chained calls are Swift's pipeline style:
`filter` keeps matching elements, and `compactMap` (a map that silently drops
`nil` results) turns each numeric ID into a value — so a device whose UID query
fails simply disappears from the menu instead of aborting the whole listing,
and a missing name falls back to "Microphone". The UID, not the transient
`AudioObjectID`, is what the app stores and uses to re-resolve the device at capture start.
""",
    ('AudioDeviceCatalog.swift', 'defaultInputDeviceID'): """
Queries the system object (`kAudioObjectSystemObject`, the root Core Audio
object that represents the audio hardware system itself) for
`kAudioHardwarePropertyDefaultInputDevice`. Selector, global scope, and main
element identify the property, and Swift's `&` passes a variable's address
exactly like C's address-of operator, so `deviceID` and `size` act as in/out
parameters. Success still requires a nonzero device ID because zero is not
usable hardware.
""",
    ('AudioDeviceCatalog.swift', 'allDeviceIDs'): """
Implements Core Audio's two-call variable-size pattern, an idiom C programmers
will recognize: first ask only for the byte count, then allocate exactly that
much and ask again for the data. The Swift array lends its backing store
through `withUnsafeMutableBufferPointer`, which exposes the array's contiguous
storage as a raw C-style pointer valid only inside the closure — this is how a
safe Swift array is handed to a C out-parameter. Any status failure returns an
empty catalog rather than partially initialized identifiers.
""",
    ('AudioDeviceCatalog.swift', 'deviceHasInput'): """
Reads the device's input-scope stream configuration to decide whether it can
record at all — this is the test that keeps output-only hardware (speakers,
displays) out of the microphone menu. `AudioBufferList` is a variable-length C
struct whose true size is known only at runtime, so the code allocates raw
bytes with the struct's alignment and fills them via the property call; `defer`
(a Swift block that runs when the enclosing scope exits by any path) frees that
allocation on every early return. `UnsafeMutableAudioBufferListPointer` is the
Swift wrapper that makes the struct's trailing buffer array iterable, and the
device qualifies when at least one buffer reports channels.
""",
    ('AudioDeviceCatalog.swift', 'stringProperty'): """
Fetches a Core Foundation string property such as the UID or the display name.
The value arrives as `Unmanaged<CFString>` — a reference deliberately left
outside ARC's automatic retain/release so the programmer must state explicitly
who owns it. The API contract actually hands ownership to the caller; this code reads it
with `takeUnretainedValue` and never releases it, accepting a tiny one-off leak
per device query, and the `as String` bridge then yields an ordinary Swift
string. Empty strings are reported as `nil` so a
blank device name is treated like a missing one.
""",
    ('MicrophoneCaptureService.swift', 'microphoneInputCallback'): """
This function has a C callback ABI: AUHAL invokes it on the real-time audio
thread to announce that the hardware has produced `frameCount` new frames. For
an *input* callback the trailing buffer-list argument carries no samples — the
code must pull them itself, which is why it allocates an `AVAudioPCMBuffer` and
calls `AudioUnitRender` to copy the hardware frames into storage it owns.
`reference` is the opaque retained Swift context; `takeUnretainedValue`
recovers it without any atomic retain/release, so the audio thread never
contends on reference counts. The converted, owned `Data` chunk is handed to
the processing queue with `queue.async`, moving all further work off the
deadline thread. Returning `OSStatus` follows Audio Unit convention — Swift
errors cannot cross this C boundary — and a failed buffer allocation returns
`noErr` so one dropped chunk does not surface as a stream error.
""",
    ('MicrophoneCaptureService.swift', 'func start('): """
Start is transactional. `AudioComponentDescription` is a search key into
macOS's registry of audio plug-ins: type output, subtype HALOutput,
manufacturer Apple names AUHAL (the system's hardware-abstraction audio unit),
and `AudioComponentFindNext` returns the matching component so
`AudioComponentInstanceNew` can instantiate it. Any failure after that creation
disposes the partially constructed instance before rethrowing, so no
half-configured Audio Unit survives. A successful return means device
selection, format negotiation, callback installation, initialization, and
hardware start all completed.
""",
    ('MicrophoneCaptureService.swift', 'func stop()'): """
State is removed under the lock before any external teardown, so repeated
`stop` calls find nothing and are harmless. The teardown order matters:
stopping, uninitializing, and disposing the Audio Unit silences the real-time
callback first, and only then does `context?.release()` balance the single
retain taken by `passRetained` at setup — releasing earlier could free the
context while a callback still uses it. The final empty
`processingQueue.sync {}` is a drain barrier (it returns only after every chunk
already queued has been handled) and is skipped when the caller is already on
that queue — detected via the dispatch-specific key — to avoid waiting on
itself, a self-deadlock.
""",
    ('MicrophoneCaptureService.swift', 'func configure('): """
Completes AUHAL setup as a transaction. Each `AudioUnitSetProperty` call is the
property dance from the chapter intro — selector, scope, element, value
pointer, byte size, exactly as a C API: input is enabled on element 1 (the
hardware-input bus), output disabled on element 0, and the chosen device
attached. The code then *reads* the device's native format from the input
scope of element 1 and *installs the same format* on the output
(callback-facing) scope, so AUHAL performs no hidden conversion and the
callback receives raw hardware frames; the `AVAudioConverter` built here does
the real resampling to the fixed 16 kHz mono target. The context is retained
with `passRetained` for the C callback, released again if installation,
initialization, or start fails, and published under the lock only after every
fallible step succeeds.
""",
    ('MicrophoneCaptureService.swift', 'func convert('): """
`AVAudioConverter` performs the actual signal conversion — resampling from
whatever rate and sample layout the device produces down to 16 kHz mono
`Int16`. It works in pull style: the closure passed to `convert` is the
converter's input source and may be called more than once, so a `Mutex`-backed
flag (a lock that wraps the value it guards) supplies the source buffer exactly
once and answers `.noDataNow` afterwards. The output capacity is the input
frame count scaled by the sample-rate ratio plus a small margin, allowing for
resampling expansion. The final `Data(bytes:count:)` copies the PCM bytes out
of the temporary AVAudio buffer, producing the owned chunk that may safely
outlive the callback.
""",
    ('MicrophoneCaptureService.swift', 'class MicrophoneCaptureService'): """
Owns one AUHAL capture instance and one retained callback context. An `NSLock`
(a plain mutual-exclusion lock, the moral equivalent of `pthread_mutex_t`)
protects publication and removal of those two lifetime roots, while a serial
`DispatchQueue` (a first-in-first-out work queue whose closures run one at a
time on a system-managed thread) owns all ordinary delivery once the real-time
callback has copied the audio bytes.
""",
    ('MicrophoneCaptureService.swift', 'init()'): """
Constructs the model's fixed target format — interleaved signed 16-bit PCM,
mono, 16 kHz. Failure here would mean the platform cannot express a basic PCM
format: a broken invariant rather than a recoverable per-session error, hence
`preconditionFailure` (Swift's deliberate crash with a message, like an
`assert` that ships in release builds). `setSpecific` tags the processing queue
with a private key so that `stop` can later ask "is this code already running
on that queue?" and skip the synchronous wait that would otherwise deadlock on
itself.
""",
    ('SessionArchiveService.swift', 'struct SessionArchiveMetadata'): """
The stable JSON summary written beside the audio and transcripts. `Codable`
asks the compiler to derive serialization for the struct's fields
automatically, so the type converts to and from JSON without hand-written
encoding code. It records domain identity and times plus latched runtime
choices and the final audio byte count — and deliberately omits model weights,
mutable services, and the unstable provisional caption state.
""",
    ('SessionArchiveService.swift', 'func finalize('): """
On the archive queue, this propagates any earlier write failure, enforces the
4 GB PCM limit, and then repairs the WAV header: the 44-byte header written at
start carried sizes for an empty file because the two size fields (the overall
RIFF chunk size, stored as data bytes + 36, and the data chunk's byte count)
are unknowable while recording. The handle seeks back to offset 0, rewrites the
header with the true count, and `synchronize()` flushes it to disk
(Foundation's `fsync`) before closing. It then writes transcript.txt,
transcript.json, and a pretty-printed session.json, clears state, and returns
the directory — or `nil` if no session was ever started.
""",
    ('SessionArchiveService.swift', 'func perform<'): """
Bridges serial dispatch-queue work into Swift `async throws`. A continuation
is the suspended caller reified as a value: `withCheckedThrowingContinuation`
pauses the awaiting task, hands the closure a one-shot handle, and `resume`
restarts the task with either the operation's value or its error ("checked"
means the runtime traps if the handle is resumed twice, and logs a warning if it is discarded without ever being resumed). Exactly one
resume occurs per queued closure, and the generic result must be `Sendable`
because it crosses from the archive queue back to the caller's task.
""",
    ('DashboardView.swift', '@1'): """
The dashboard needs all four imports: `SwiftUI` for the declarative controls,
`AppKit` for the clipboard (`NSPasteboard`) and the `NSImage` QR bitmap,
`CoreImage.CIFilterBuiltins` for the typed QR-code generator filter, and
`ClassroomCaptionsCore` for the shared domain types (correction modes and
states) the controls tag and display.
""",
    ('DashboardView.swift', 'struct DashboardView'): """
One SwiftUI view renders the whole dashboard. `@Bindable` lets the `$model.x`
spelling used throughout the file produce a `Binding` (a get/set pair) into the
observable `ClassroomAppModel`, so every toggle and text field edits model
state directly rather than a view-local copy. Its `body` — the property SwiftUI
re-evaluates whenever observed model data changes — is a `NavigationSplitView`
(a sidebar-plus-detail layout) whose detail column stacks every settings group:
session, iPhone sharing, questions, diagnostics, microphone, archive, Voxtral,
correction, overlay, manual input, transcript. The `onChange` hooks forward
display and font-size edits to `refreshOverlay` and correction-toggle edits to
`correctionSettingChanged`, so all live state lives in the model.
""",
    ('DashboardView.swift', '@121'): """
This page renders the iPhone Live Captions group and the opening of the
Anonymous Student Questions group. The sharing group swaps which start/stop
button is prominent by state, copies the pairing URL to `NSPasteboard` (the
system clipboard), and picks among three explanatory captions with
`if case .failed(let message)` (pattern matching that extracts the error text
from the status enum); the pairing QR image appears on the right only while a
pairing URL exists.
""",
    ('DashboardView.swift', '@252'): """
Still inside the student-questions group: the student QR link and copy button,
the pending-queue row (Show Next / Dismiss Current / Clear Pending, each
disabled exactly when its model precondition fails), and two voice-phrase text
fields bound through `$model` that gray out while spoken overlay controls are
off. The currently presented question, when there is one, is echoed in a
selectable card so the professor sees what the classroom overlay is showing.
""",
    ('DashboardView.swift', 'var gemmaMemorySummary'): """
Two jobs share this block. `pairingQRCode` turns a URL into a QR image: Core
Image's built-in `qrCodeGenerator` filter encodes the URL's UTF-8 bytes at
error-correction level M, a 10x affine scale enlarges the tiny native output,
and an `NSCIImageRep` wraps the result as the `NSImage` the dashboard shows
(call sites add `.interpolation(.none)` so the modules stay crisp squares).
The rest is the Live Diagnostics grid behind the `showLiveDiagnostics` toggle:
token-rate and memory rows whose summary helpers degrade to a dash or a status
word when a value is nil — `gemmaMemorySummary` distinguishes "Detecting…"
(server ready, MLX process identity not yet resolved) from "Not loaded" via
`correctionServerReady`, so the Gemma memory row never falsely reads zero.
""",
    ('DashboardView.swift', 'var correctionSettings'): """
`formatMemory` wraps Foundation's `ByteCountFormatter` in its memory style so
every diagnostics row prints byte counts the same human-readable way. The rest
of this page is the Caption Overlay group — display picker, 24-64 pt text-size
slider, a master toggle for spoken overlay controls, and three phrase fields —
all bound straight into the model; the `showVoiceCommand` helper family below
substitutes the default French phrases when a field is left blank, so the hint
text never quotes an empty phrase (a blank field actually disables
spoken-command recognition until it is refilled). The Gemma 4 correction group
then opens with its Standard/Science segmented mode picker.
""",
    ('DashboardView.swift', '@614'): """
This page finishes the Caption Overlay group — the scroll-up and scroll-down
phrase fields, the help line that now also explains framing an Assistant-mode
question, and the Show/Refresh/Reset overlay buttons — then defines the small
helper properties that supply placeholder phrases and the per-mode description
text. The Gemma correction group then begins: the Standard/Science/Assistant
segmented picker, that description, the 0-8 previous-captions stepper, and the
start of the server/model/endpoint grid.
""",
    ('DashboardView.swift', '@739'): """
The Gemma group closes: model and endpoint fields disabled during an active or
starting session so the pipeline cannot be reconfigured mid-class, a status row
showing readiness, queue depth, and last latency, and a footer that is either
the current `correctionError` or the standing note that questions are proofread
as quoted data and answer-like output is rejected. The Microphone group follows
— an input picker and refresh locked while listening, a live level meter and a
captured-byte counter, and a local-PCM reminder — then the Session Recording
group begins with its record toggle and archive-folder field, both disabled
during a session (the folder also when recording is off).
""",
    ('DashboardView.swift', '@868'): """
The Session Recording group ends with the last archive path and a Show in Finder
button (or a note listing the exported files) plus any archive error. The
Voxtral Realtime group then fills the rest: a backend picker that swaps which
fields appear — model directory and a max-context slider for the embedded
backend, endpoint and model fields for the WebSocket one, all locked while
listening or starting — the shared 240-1200 ms model-delay slider, a caption
explaining the embedded context limit or the WebSocket compatibility mode, and a
connection row that reports first-caption latency.
""",
    ('DashboardView.swift', '@999'): """
The Development Caption Input group feeds the timeline by hand: a text field
whose `onSubmit` (Return in the field) finalizes, plus Preview-as-Provisional
and Finalize buttons. The Recent Captions group then lists each finalized
segment with its sequence number, display text, and correction badge, or an
empty-state placeholder when none exist yet.
""",
    ('CaptionOverlayController.swift', '@1'): """
Only two imports: `AppKit` for the panel, views, screens, cursors, and mouse
events this file drives directly, and `SwiftUI` for the caption content the
panel hosts. The file is precisely the bridge between those two UI systems.
""",
    ('CaptionOverlayController.swift', 'class OverlayInteractionView'): """
A transparent, borderless `NSView` (AppKit's basic rectangular view class —
the unit that draws content and receives mouse events) stretched over the whole
caption panel; it owns only the move and resize gestures. It declares itself
non-opaque and reports drag translations through the `onDrag` closure plus a
completion through `onDragEnded`, function values the controller installs at
startup. It sits in front of the SwiftUI hosting view but claims hits only in
its two handle rects (see `hitTest`), letting clicks elsewhere fall through.
""",
    ('CaptionOverlayController.swift', 'class CaptionOverlayController'): """
The main-actor controller owning the imperative side of the overlay: the
floating `NSPanel` (AppKit's auxiliary-window class — a window that can float
above others without becoming the application's main window), the
`NSHostingView` that renders SwiftUI content inside that AppKit window, the
`OverlayInteractionView`, the selected display, and per-display saved geometry.
It positions, clamps, persists, and restores the overlay frame, and acts as the
panel's `NSWindowDelegate` (the object AppKit notifies when the window moves or
resizes); `isApplyingFrame` suppresses persistence while the controller is
itself setting the frame, so only user-driven geometry is saved.
""",
    ('CaptionOverlayController.swift', 'override init'): """
Builds the panel; each flag buys something a captions window needs.
`.borderless` strips the title bar so only the rounded SwiftUI card is visible;
`.nonactivatingPanel` lets clicks on the overlay leave the professor's
frontmost app (slides, IDE) active; `isReleasedWhenClosed = false` keeps the
window's lifetime under Swift reference counting; the clear, non-opaque
background makes the window rectangle itself invisible; level `.floating`
stays above normal windows; `hidesOnDeactivate = false` keeps it on screen
when the app loses focus; the collection behavior joins all Spaces (virtual
desktops), may sit over full-screen apps, and is skipped by window cycling.
Auto Layout (AppKit's constraint solver) pins the hosting and interaction
views edge-to-edge in one container; the interaction view's closures route to
`movePanel`/`resizePanel`/`finishInteraction` with `[weak self]` (so they do
not retain the controller in a cycle), and `orderOut` starts the panel hidden.
""",
    ('CaptionOverlayController.swift', 'func resizePanel'): """
Applies a resize drag from the lower-right corner. macOS geometry places a
rectangle's origin at its bottom-left corner with y growing upward, so dragging
the grip downward makes `translation.height` negative; height is therefore
`start.height - translation.height`, and the origin's y is re-derived from the
anchored top edge (`start.maxY`) so the box grows downward and rightward while
the top stays put. The new width and height are clamped between the minimum
size and the room left before the screen margins, and the resulting rect still
passes through `clamped` against the visible frame.
""",
    ('CaptionOverlayController.swift', 'func persistFrame'): """
Writes the panel's current frame, serialized to a string, into `UserDefaults`
(the per-application key-value preference store macOS persists across launches)
under the selected display's geometry key — but only when not mid-`applyFrame`
and a display is selected. The `isApplyingFrame` guard is what prevents the
delegate's move/resize callbacks from re-saving frames the controller itself
just set programmatically.
""",
    ('CaptionOverlayController.swift', 'struct CaptionOverlayView'): """
Pure SwiftUI rendering of the caption card: finalized lines, italic provisional
text, the question card, the pending badge, and the two handle hints, layered
in a `ZStack` (children drawn back to front) over the dark rounded background
the audience sees. All inputs are immutable values supplied by the controller;
window ownership and geometry remain in AppKit. `contentVersion` joins the
lines and provisional text with control characters no caption can contain,
producing one change-detection string: `onChange` watches it and re-scrolls
through the `ScrollViewReader` proxy (a handle for commanding scroll position)
so the newest caption is always in view.
""",
    ('CaptionOverlayController.swift', 'captionText'): """
Renders one caption line as white text free to wrap onto any number of lines.
A `Text` whose container offers too little height may be truncated with an
ellipsis; `lineLimit(nil)` plus `fixedSize(horizontal: false, vertical: true)`
forces layout to grant the text its full required height while still wrapping
to the panel's width — the cure for the old ellipsis behavior.
""",
    ('GemmaServerController.swift', '@1'): """
The only import is `Foundation`, Apple's base library beyond the Swift language
itself; this file draws on it for `Process` (the child-program handle), `Pipe`,
`URLSession` (the HTTP client), and `URLRequest`. Nothing executes at import
time.
""",
    ('GemmaServerController.swift', 'enum GemmaServerError'): """
The typed failure set for the locally launched MLX-LM server (the separate
program that loads the Gemma model and answers requests over local HTTP).
Conforming to `LocalizedError` lets each case render a user-facing string:
`executableMissing` names the bad path, `launchFailed` wraps the spawn error or
a non-zero exit, and `unavailable` means the health endpoint never answered
successfully within the startup window. Distinct cases let the dashboard say
*which* part of this optional, fail-soft feature went wrong.
""",
    ('GemmaServerController.swift', 'class GemmaServerController'): """
Main-actor owner of the optional MLX-LM child and its health-check session.
`Process` is Foundation's handle for launching and controlling a child program
— roughly fork/exec, wait, and kill wrapped in one object — and `URLSession` is
Foundation's HTTP client, the object that opens connections, sends requests,
and hands back responses. Actor isolation serializes launch and termination
with UI workflows, while health probes suspend instead of blocking the event
loop. Only the child stored in `process` is considered owned and eligible for
termination.
""",
    ('GemmaServerController.swift', 'init('): """
Creates an ephemeral session (one that keeps no on-disk cache, cookies, or
credentials — useless baggage for loopback health checks) with deliberately
tight deadlines: one second for a request and two seconds for the whole
transfer. A probe against a server that is not listening yet therefore fails
almost immediately instead of hanging; `ensureReady` supplies the separate
45-second model-loading deadline by simply repeating these cheap probes.
""",
    ('GemmaServerController.swift', 'ensureReady'): """
Readiness is idempotent: if the endpoint already answers health checks —
no matter who started the server — the function returns at once, so a
professor-managed server is reused rather than duplicated. Otherwise the owned
child is launched once; because the only trustworthy ready signal is the server
answering HTTP after its multi-second model load, the loop probes every 250 ms,
and `Task.sleep` suspends between probes without occupying a thread. The
deadline uses `ContinuousClock`, which is monotonic and unaffected by
wall-clock changes, and an early child exit is reported immediately with its
exit status instead of waiting out the full 45 seconds.
""",
    ('GemmaServerController.swift', 'func launch('): """
Spawns the owned mlx_lm.server child once: it verifies the path is executable
(else `executableMissing`) and that the endpoint yields a host and port, then
starts the program with flags chosen for predictable proofreading. Temperature
0 removes sampling randomness (the model always picks its most probable next
token, so the same caption yields the same correction), disabled thinking stops
the model from emitting a self-reasoning preamble, max-tokens caps any reply at
384 tokens, and decode/prompt concurrency of one forbids overlapping
generations that would compete for memory. stdout and stderr go to /dev/null,
logging is WARNING-only, and a `run()` failure is rethrown as `launchFailed`.
""",
    ('GemmaServerController.swift', 'processIdentifier'): """
Resolves the server's PID, preferring the live owned `Process`'s identifier.
When the app did not spawn the server, it asks the operating system instead by
running `lsof -nP -tiTCP:port -sTCP:LISTEN` as a child process whose stdout is
captured through a `Pipe` (an in-memory channel — the same idea as a Unix pipe
— connecting the child's output to this app). `Task.detached` runs that lookup
on a background executor, so a slow lsof plus `waitUntilExit` can never stall
the main actor or the caption path. Any lsof failure, non-zero exit, or
unparseable output yields nil rather than a wrong PID.
""",
    ('GemmaServerController.swift', 'func isHealthy('): """
One complete HTTP request/response cycle used as a readiness probe. It builds
the standard `v1/models` URL, marks the request GET (a read-only fetch), and
`try await healthSession.data(for:)` sends it and suspends until the server
replies or the one-second timeout fires. An HTTP reply carries a three-digit
status code; only the 200–299 "success" range counts as healthy. Any thrown
error, non-HTTP response, or other status maps to false, so the poll loop
treats connection-refused during startup as simply not-yet-ready rather than as
a failure.
""",
    ('GemmaCorrectionService.swift', '@1'): """
`ClassroomCaptionsCore` is the app's own domain module: it provides the caption
segment types, the correction request/result values, and the deterministic
`CaptionCorrectionValidator` applied at the end of `correct`. `Foundation`
supplies the `URLSession` HTTP client and the JSON encoder/decoder pair.
""",
    ('GemmaCorrectionService.swift', 'enum GemmaCorrectionError'): """
Separates the three ways a correction round trip can fail before validation:
the endpoint URL cannot be built, the server's successful reply lacks the
expected JSON structure, or the server answers with a non-success HTTP status
(anything outside 200–299), in which case the numeric code and the reply body
text are kept for diagnosis. Typed errors let the coordinator preserve ordinary
control flow while `LocalizedError` supplies stable dashboard text.
""",
    ('GemmaCorrectionService.swift', 'struct Message'): """
The smallest chat-protocol unit: one labeled utterance. Chat-style LLM
endpoints take a list of these, where `role` says who is speaking — "system"
for the operator's standing instructions, "user" for the data to act on — and
models are trained to give system text higher authority, which is what makes
the injection defenses below meaningful. `role` stays a plain string rather
than a Swift enum because the OpenAI-compatible endpoint owns the role
vocabulary; `Codable` gives symmetric, compiler-checked JSON field names.
""",
    ('GemmaCorrectionService.swift', 'struct CompletionRequest'): """
The body of an OpenAI-style chat-completion request — the standard
"generate text from this conversation" message an LLM server accepts. Its
fields are the whole contract: `model` (pinned to default_model, the one model
MLX-LM loaded), the ordered `messages` conversation, `temperature` 0.0 (no
sampling randomness, so the same caption always yields the same correction),
`max_tokens` capping how much the model may generate, and `stream` false so
the reply arrives as one JSON document instead of incremental fragments.
Because the constant fields carry default values, call sites supply only
`messages` and the per-segment token budget, yet encoding still writes every
field into the JSON.
""",
    ('GemmaCorrectionService.swift', 'struct CompletionResponse'): """
The decoded reply envelope. Completion servers return an array of `choices`
(alternative generations — this app only ever reads the first) and an optional
`usage` block counting prompt and generated tokens, which feeds the dashboard's
correction metrics. Each choice's message exposes `reasoningContent` alongside
`content` so `correct()` can reject any reply where the model leaked
chain-of-thought (step-by-step self-talk) instead of returning a clean caption.
Nested `CodingKeys` remap the server's snake_case names to Swift camelCase, and
`Decodable` ignores any JSON fields this struct does not declare.
""",
    ('GemmaCorrectionService.swift', 'sharedPrompt'): """
The base system prompt (the standing instruction block sent with every request,
which chat models treat as outranking user text) and the core prompt-injection
defense: it frames the caption as untrusted quoted data that is never an
instruction, and forbids answering, obeying, continuing, explaining,
summarizing, or translating it. It scopes the model to formatting-only
corrections, bans LaTeX/Markdown/backtick output because the overlay renders
compact plain text, and states that notation normalization is not license to
solve an expression, so a captioned question comes back only proofread. The
wording assumes the model may still disobey — the deterministic validator, not
this text, has the final say.
""",
    ('GemmaCorrectionService.swift', 'init(endpoint:'): """
Stores the already validated loopback endpoint and builds an ephemeral session
(no on-disk cache or cookies) whose deadlines bound every correction round
trip: twelve seconds per request and fifteen for the whole transfer.
Corrections are serialized one at a time, so a hung generation must fail fast
and surrender the queue rather than stall later captions. The initializer does
not rewrite hosts or ports; endpoint policy remains the app model's
responsibility.
""",
    ('GemmaCorrectionService.swift', 'func correct('): """
One full request/response cycle with the model server. The function builds the
`v1/chat/completions` URL, computes a token budget that scales with caption
length but stays inside [48, 384], and assembles the two-message conversation:
the mode's system prompt, then a user message in which previous captions and
the target text sit inside distinct data markers so the model cannot mistake
either for instructions. `JSONEncoder().encode` turns the request struct into
JSON bytes, sent as a POST with a `Content-Type: application/json` header;
`try await session.data(for:)` suspends until the reply arrives. The reply is
then distrusted step by step — the status must be 2xx, `JSONDecoder` must
produce the expected shape, any nonempty reasoning channel causes rejection,
and the surviving text must still pass the deterministic validator before
becoming a result.
""",
    ('VoxtralRealtimeService.swift', '@1'): """
`ClassroomCaptionsCore` provides the shared transcription contract — the
`TranscriptionEvent` values and configuration types this backend must honor.
`Foundation` supplies `URLSession` with its WebSocket task plus
`JSONSerialization`; `Synchronization` supplies the `Mutex` that guards the
connection state.
""",
    ('VoxtralRealtimeService.swift', 'class VoxtralRealtimeService'): """
Bridges an external WebSocket protocol to the same
`StreamingTranscriptionService` contract as embedded Voxtral, so the app model
cannot tell the two backends apart. `URLSession` (Foundation's network client)
reports connection events through a *delegate* — an object it calls back when
the socket opens, closes, or fails — and that mechanism requires an
Objective-C-compatible object, hence the `NSObject` subclass. `@unchecked
Sendable` is this class's promise that it is safe to use from several threads
even though the compiler cannot verify it; the `Mutex<State>` below is what
actually makes the promise true.
""",
    ('VoxtralRealtimeService.swift', 'func start('): """
Start validates that the endpoint scheme is `ws` or `wss` (WebSocket, plain or
TLS-encrypted — the counterpart of http/https), stops any previous session, and
prepares the upgrade request: a WebSocket begins life as an ordinary HTTP
request whose headers ask the server to keep the connection open afterward as a
two-way message channel, and the `OpenAI-Beta: realtime=v1` header opts into
the realtime protocol. The session waits for connectivity, allows 30 seconds to
connect, and raises the whole-transfer limit to 24 hours because one lecture is
one long-lived connection. All connection state is installed under the mutex
*before* `task.resume()` starts network activity, so even the earliest delegate
callback finds a consistent owner.
""",
    ('VoxtralRealtimeService.swift', 'func commit('): """
The realtime protocol is append-then-commit: `sendAudio` only accumulates audio
in the server's input buffer, and the commit message asks the server to
transcribe what has accumulated. This method sends that commit only when
connected, with uncommitted audio actually present, and no generation already
in flight; it atomically clears `hasUncommittedAudio` and sets
`generationInProgress` inside the lock before sending, so racing commit calls
cannot start overlapping generations.
""",
    ('VoxtralRealtimeService.swift', 'didCloseWith'): """
Converts the WebSocket close handshake into the shared terminal path. Every
WebSocket close carries a numeric close code defined by the protocol;
`normalClosure` and `goingAway` are routine endings and produce no failure
message, while any other code keeps its numeric value plus the optional UTF-8
reason text so an abnormal disconnect can be diagnosed before the
`disconnected` event is emitted.
""",
    ('VoxtralRealtimeService.swift', 'private func handle(_ message:'): """
WebSocket messages arrive as either text or binary frames; this normalizes both
to `Data` bytes and parses them with `JSONSerialization`, Foundation's dynamic
JSON parser, which yields untyped dictionaries and arrays rather than the fixed
`Codable` structs the Gemma client uses — the right tool here because the
server's message shapes vary. Unknown future message kinds and malformed JSON
are silently ignored rather than crashing the stream or fabricating caption
events.
""",
    ('main.swift', '@1'): """
`CVoxtralEngine` exposes the project's C bridge — the `ccv_*` functions and
status codes the benchmark drives directly, bypassing the app. `Foundation`
supplies file loading, `Data`, and string formatting.
""",
    ('main.swift', 'enum BenchmarkError'): """
The three benchmark failure families, each carrying a human-readable message:
`usage` for bad command-line arguments, `invalidWAV` for unsupported audio
input, and `engine` for any non-OK status from the C bridge. `LocalizedError`
lets the top-level catch print whichever message applies, and the single switch
pattern binds all three associated strings to one name.
""",
    ('main.swift', 'struct PCMRecording'): """
Owned mono PCM16 samples plus the sample rate, guaranteeing the benchmark feeds
the bridge's required format. `duration` derives the recording length the
obvious way — sample count divided by samples per second — and the real-time
factor printed later divides inference time by exactly this value.
""",
    ('main.swift', 'drainText'): """
Empties the stream's pending text queue using the classic C sizing handshake:
call `ccv_stream_read_text` with a guess-sized buffer, and on
`BUFFER_TOO_SMALL` retry once with the exact byte count the bridge reported
through `required`. Each piece is decoded as UTF-8 up to the NUL terminator,
appended to the transcript, and echoed immediately so progress is visible. The
function returns whether any text appeared, which is how the caller records
first-token latency exactly once; `NO_TEXT` is the normal empty-queue answer,
and any other status is a real engine error.
""",
    ('main.swift', 'func wordAccuracy('): """
Scores the transcript against the reference in plain terms: the word-level
Levenshtein distance is the minimum number of single-word insertions,
deletions, and substitutions needed to turn the reference word list into the
transcript, and accuracy is one minus that distance divided by the reference
length. The classic dynamic-programming table is kept as a rolling pair of
rows, so memory stays linear instead of quadratic. An empty reference scores 1
only against an empty transcript, and the result is floored at zero so heavy
over-generation cannot yield a negative score.
""",
    ('main.swift', 'func seconds('): """
Converts a Swift `Duration` to floating-point seconds for printing. `Duration`
stores time as integer components — whole seconds plus attoseconds (10⁻¹⁸ s) —
so interval arithmetic never accumulates floating-point drift; this helper
performs the lossy conversion only at the reporting boundary.
""",
    ('main.swift', 'runRestartTest'): """
Measures what the app's stop/start cycle costs once the model weights are
already in memory. Each of two cycles repeats the application's session
sequence against the one loaded model: create a stream, prime it with the same
3.2 seconds of silence the app feeds before reporting "connected", feed the
recording in chunks of the configured size while draining text, then finish and
free the stream. Every phase is bracketed with `ContinuousClock` timestamps and
printed as per-cycle `stream_create`, `prime`, `feed`, and `stop` seconds, so
the cost of restarting captioning mid-lecture can be compared against the
one-time model load.
""",
    ('main.swift', 'func run()'): """
The whole benchmark, with every phase timed. It loads the model (the
multi-second weight read reported as `model_load_seconds`), optionally branches
into the restart test, then creates a stream with the same delay and
processing-interval options the app uses; an optional silent preroll warms the
pipeline without contributing transcript text. The feed loop pushes the WAV in
fixed-size chunks, drains text after each chunk, notes `first_token_seconds`
the first time any text appears, and with `--realtime` sleeps so audio arrives
no faster than a live microphone would deliver it. After `ccv_stream_finish`
and a final drain it prints the metrics — `inference_seconds` is wall-clock
processing time, `realtime_factor` divides that by audio duration (below 1.0
means faster than live speech), and `word_accuracy` compares against an
optional reference file — while `defer` blocks free the stream and model on
every exit path.
""",
    ('ClassroomVoxtral.h', '#endif'): """
A bare `#endif` closes the nearest open preprocessor conditional. This header
has three: the first two end the `#ifdef __cplusplus` regions that emit the
opening and the closing brace of the `extern "C"` linkage wrapper, and the
final one ends the include guard opened by `#ifndef CLASSROOM_VOXTRAL_H` — the
point through which the preprocessor skips on any repeated inclusion.
""",
    ('ClassroomVoxtral.h', 'ccv_stream_read_text'): """
Copies the next queued UTF-8 text fragment into caller-owned storage and always
reports the byte count it needs, NUL terminator included, through
`required_capacity`. `NO_TEXT` means polling may stop for now.
`BUFFER_TOO_SMALL` lets the caller allocate the reported capacity and retry
without losing the fragment — the bridge keeps holding it until a copy
succeeds.
""",
    ('ClassroomVoxtral.c', '@1'): """
The bridge includes its own public header, the upstream engine API, and — only
when compiled with Metal — the GPU backend header. `stdatomic.h` supplies the
atomic type for the cancellation flag, `unistd.h` the `access()` call used to
check model files, and `CCV_UPSTREAM_REVISION` pins the upstream commit hash
that `ccv_upstream_revision()` reports.
""",
    ('ClassroomVoxtral.c', 'ccv_stream_samples_fed'): """
Returns the bridge's own monotonic count of accepted samples — incremented in
`ccv_stream_feed_pcm16` only after the engine accepts a buffer, so rejected
audio is never counted. A null handle reads as zero, letting diagnostics code
call it unconditionally.
""",
    ('VoxtralEmbeddedService.swift', '@1'): """
An `import` makes a compiled module's public declarations visible — there is no
textual inclusion as with `#include`. `ClassroomCaptionsCore` supplies the
shared event and metrics value types, `CVoxtralEngine` is the C bridge target
whose `ccv_*` functions Swift calls directly, `Foundation` provides `Data` and
`URL`, and `Synchronization` provides the `Mutex` that guards shared state.
""",
    ('VoxtralEmbeddedService.swift', 'func releaseModel'): """
Frees the cached C model on app shutdown; ordinary stops keep it so the next
`start()` skips the multi-second weight reload. The locked closure returns the
model pointer only when no stream is active — a live session keeps its model —
and clears the cache fields so a later `start()` reloads; the actual
`ccv_model_free` runs after the lock is released, keeping the lock hold-time to
a pointer swap. Scheduling on the inference queue orders the free after any
inference work already queued.
""",
    ('VoxtralEmbeddedService.swift', 'enum VoxtralEmbeddedError'): """
The service's only error type. A Swift `enum` case can carry payload values
(roughly a tagged union in C); the single `engine` case packages the bridge's
status code with its human-readable message. Conforming to `LocalizedError`
lets Swift's error machinery display `errorDescription` directly, so whatever
the C side wrote into its error buffer — missing model files, failed load,
failed stream creation — reaches the UI without the app model handling raw
status codes.
""",
    ('VoxtralEmbeddedService.swift', 'class VoxtralEmbeddedService'): """
Owns the embedded backend's C handles and serial inference queue. A `final
class` is a reference type that cannot be subclassed; `Sendable` marks a type
safe to share across threads, and `@unchecked` means the programmer asserts
that instead of the compiler proving it — opaque C pointers are not
verifiable. The real guarantee is queue confinement: feed, drain, flush,
finish, and destruction never overlap. `startupPrerollSamples` is
16,000 × 3.2 = 51,200 samples — the 3.2 s of silence fed to prime the decoder
at startup.
""",
    ('VoxtralEmbeddedService.swift', 'struct State'): """
One record for everything mutable: the two C handles (`OpaquePointer` is
Swift's type for a pointer to an undeclared C struct), the event continuation,
the provisional caption accumulated so far, and the running flag. It lives
inside a `Mutex` (the Synchronization module's mutual-exclusion lock;
`withLock` runs a closure while holding it) because event-stream registration
and termination touch state off the inference queue. The `DispatchQueue` below
is the serial queue from the chapter introduction — the only place C functions
are called — and `.userInitiated` raises its priority because caption latency
is user-visible.
""",
    ('VoxtralEmbeddedService.swift', 'func events('): """
Builds the `AsyncStream` the app model consumes with `for await`: an
AsyncStream is a one-way channel whose producer pushes values through a
continuation handle. The builder closure stores that continuation in state so
`emit(_:)` can yield events in order; `onTermination` fires when the consumer
stops listening and clears the sink, so later events are dropped rather than
sent to nobody. `[weak self]` keeps this long-lived callback from holding the
service in memory.
""",
    ('VoxtralEmbeddedService.swift', 'func sendAudio'): """
The capture path hands over a `Data` (Foundation's owned byte buffer, a managed
counterpart of a malloc block) and returns immediately; the feed itself runs on
the inference queue, so no second feed can enter the mutable C stream
concurrently. `withUnsafeBytes` exposes the bytes as a raw pointer valid only
inside the closure, and `bindMemory(to: Int16.self)` reinterprets them as
PCM16 samples — the C call takes a sample count, not bytes. Success drains
newly decoded tokens; any failure except CANCELLED becomes a `.failed` event,
CANCELLED being the owner's own shutdown rather than an error.
""",
    ('VoxtralEmbeddedService.swift', 'statusMessage'): """
Wraps the C lookup for call sites that have a status but no bridge message.
`ccv_status_description` returns borrowed static storage and answers every
enum value (out-of-range ones map to a fixed "unknown status" string), and
`String(cString:)` copies the NUL-terminated UTF-8 into an owned Swift string,
so the result stays valid after any C state is freed.
""",
    ('voxtral.h', '@1'): """
Banner comment only: it identifies this header as the public API of the pure C
inference engine for Voxtral Realtime 4B (a four-billion-parameter
speech-to-text model); no declarations yet.
""",
    ('voxtral.h', '#ifndef VOXTRAL_H'): """
First half of the conventional include guard, same pattern as the bridge
header: the macro is undefined on first inclusion, so the body is processed
once, and every later inclusion skips ahead to the final `#endif`.
""",
    ('voxtral.h', '#define VOXTRAL_H'): """
Records that the header has been processed, then pulls in the three standard
headers the API depends on: `stddef.h` for `size_t`, `stdint.h` for the
fixed-width integer types (BF16 weights travel as `uint16_t`), and `stdio.h`
for standard I/O declarations. The constants that follow are the model's
datasheet — fixed by the trained checkpoint, not tunable.
""",
    ('voxtral.h', '#define VOX_MEL_BINS'): """
Each acoustic frame is a vector of 128 Mel-band energies: the spectrum of one
25 ms window summarized into 128 perceptually spaced frequency bands, matching
checkpoint training. This is also the conv stem's input channel count —
`conv0_weight` below is [1280, 128, 3].
""",
    ('voxtral.h', '#define VOX_LOG_MEL_MAX'): """
Fixed stand-in for the running maximum of the log-Mel values: the front end
clips anything more than 8 below it (to 1.5 − 8 = −6.5), limiting the dynamic
range to eight orders of magnitude before the final (val + 4) / 4
normalization. The value is checkpoint-specific — preprocessing must reproduce
exactly what the model saw during training.
""",
    ('voxtral.h', '#define VOX_ENC_DIM'): """
Width of the encoder's working vectors: every position is 1280 floats from the
conv stem onward, and each layer reads and writes that same width. All the
[.., 1280] and [1280] shapes in the structs below derive from this one number.
""",
    ('voxtral.h', '#define VOX_ENC_HEADS'): """
Attention runs as 32 parallel heads — independent attention units, each with
its own learned projections over a slice of the vector — whose outputs are
concatenated. 32 heads × 64 dims per head explains the 2048-row Q/K/V
projections in `vox_enc_layer_t`.
""",
    ('voxtral.h', '#define VOX_ENC_KV_HEADS'): """
Number of key/value heads. The encoder keeps one K/V head per query head
(32 = 32), the classic multi-head layout; the decoder instead uses
grouped-query attention, where several query heads share one K/V head to
shrink the KV cache (see `VOX_DEC_KV_HEADS`).
""",
    ('voxtral.h', '#define VOX_ENC_HEAD_DIM'): """
Each head attends within a 64-dimensional subspace; heads × head-dim
(32 × 64 = 2048) gives the full projection width, which is why the encoder's
attention weight matrices are [2048, 1280].
""",
    ('voxtral.h', '#define VOX_ENC_HIDDEN'): """
Middle width of the encoder's gated feed-forward block: two projections widen
1280 to 5120 (`w1` acting as a multiplicative gate on `w3`'s output), and `w2`
projects the product back down to 1280.
""",
    ('voxtral.h', '#define VOX_ENC_WINDOW'): """
The encoder attends over at most the last 750 positions — roughly 15 seconds of
audio at about 50 positions per second. When the rolling encoder KV cache
reaches this window it is compacted and the oldest positions drop out; that
bound is what keeps memory and per-step cost constant over an unbounded
lecture.
""",
    ('voxtral.h', '#define VOX_ENC_INC_MAX_BATCH'): """
Upper bound on how many new positions one incremental encoder pass may append —
about five seconds of audio at roughly 50 positions per second. The bound
exists because the Metal-shared encoder KV cache is preallocated at
`VOX_ENC_WINDOW + 256` positions and cannot grow, so
`vox_encoder_forward_incremental` splits a larger backlog into batches of at
most this size, producing results identical to one oversized pass.
""",
    ('voxtral.h', '#define VOX_ENC_NORM_EPS'): """
Small constant added inside encoder RMS normalization (which rescales each
1280-vector by its root-mean-square so activation magnitudes stay stable layer
after layer); the epsilon keeps the division well-defined for a near-zero
vector.
""",
    ('voxtral.h', '#define VOX_DEC_DIM'): """
Width of the decoder's working vectors: token embeddings, adapter outputs, and
every layer's input and output are 3072 floats. The adapter exists precisely to
turn 5120-wide grouped audio features into this width, so audio and text can
share one decoder sequence.
""",
    ('voxtral.h', '#define VOX_DEC_HEAD_DIM'): """
Each decoder head spans 128 dimensions, so 32 query heads make the 4096-row
`wq` and 8 K/V heads make the 1024-row `wk`/`wv` in `vox_dec_layer_t`.
""",
    ('voxtral.h', '#define VOX_DEC_HIDDEN'): """
Middle width of the decoder's SwiGLU feed-forward block — the gated variant in
which one 3072-to-9216 projection passes through a smooth activation and
multiplies the other, before `w2` projects the product back to 3072.
""",
    ('voxtral.h', '#define VOX_DEC_NORM_EPS'): """
The decoder's RMS-normalization epsilon; same numerical-stability role as
`VOX_ENC_NORM_EPS`.
""",
    ('voxtral.h', '#define VOX_VOCAB_SIZE'): """
Number of token IDs the decoder can emit — 131,072 = 2^17 rows, including
control tokens. Each decode step produces a logits vector (one raw score per
vocabulary entry) of exactly this length, computed against the same
[131072, 3072] table that serves as the token-embedding matrix.
""",
    ('voxtral.h', '#define VOX_ADA_NORM_DIM'): """
Bottleneck width of the per-layer delay-conditioning network: each layer's tiny
MLP takes the 3072-wide time embedding of the configured caption delay,
squeezes it to 32 values, and expands it back into 3072 per-channel scale
factors (`ada_norm_down`/`ada_norm_up` below). This is how the chapter
introduction's delay conditioning physically enters every decoder layer.
""",
    ('voxtral.h', '#define VOX_ROPE_THETA'): """
Base of the rotary position embedding (RoPE), which encodes where a token sits
by rotating pairs of query/key channels through position-dependent angles. Each
channel pair turns at a different rate drawn from a geometric series with this
base; the large 10^6 base gives very slowly turning low-frequency channels, so
positions stay distinguishable across the 8192-token window.
""",
    ('voxtral.h', 'vox_load(const char *model_dir)'): """
Builds the long-lived `vox_ctx_t` from one model directory: maps
`consolidated.safetensors`, loads encoder/adapter/decoder weights, and sets up
caches and acceleration resources. Returns an owned context, or NULL on
failure. The tokenizer is deliberately not loaded here — the first stream
parses it and the context then lends it to later streams.
""",
    ('voxtral.h', 'vox_free(vox_ctx_t *ctx)'): """
Releases every context-owned allocation — weights and their file mapping,
caches, and scratch buffers. All borrowing streams must be freed first,
mirroring the stream-before-model order the Swift service enforces.
""",
    ('voxtral.h', 'vox_set_delay(vox_ctx_t *ctx, int delay_ms)'): """
Converts the requested delay in milliseconds to the model's 80 ms token grid
(valid range 80–2400, default 320 = 4 delay tokens) and recomputes the
decoder's time conditioning from it. The realtime checkpoint is trained to know
how far captions lag the audio: a smaller delay asks for earlier words with
less future acoustic context, as the chapter introduction describes.
""",
    ('voxtral.h', '#endif /* VOXTRAL_H */'): """
Closes the include guard opened on line 7; the trailing comment names the
matching macro — a courtesy in a 343-line header.
""",
    ('voxtral.c', '@1'): """
The header comment states this file's job: orchestrate the whole pipeline from
weight loading to text. The includes pull in the engine's own subsystems — the
math kernels, the safetensors weight-file reader, the audio front end, the
tokenizer, and (when built with `USE_METAL`) the GPU backend — plus the libc
headers for I/O, string handling, math, and the `gettimeofday` timers. Two
globals, `vox_verbose` and `vox_monitor`, gate diagnostic printing on stderr
for this file and the tokenizer; the audio module keeps its own independent
`vox_verbose_audio` flag.
""",
    ('voxtral.c', 'vox_compute_time_embedding'): """
Builds the timing embedding (a fixed-length vector of numbers encoding one
scalar) for `t_value`, the configured caption delay measured in decoder tokens.
Rather than handing the model a raw number, the scalar is spread across
`VOX_DEC_DIM` sinusoids: each of the dim/2 frequency bands gets a geometrically
decaying `inv_freq`, and the output is cos(t·inv_freq) in the low half and
sin(t·inv_freq) in the high half — a smooth encoding the network can
interpolate between delays it saw in training. The layout matches the vLLM
(reference GPU server) Mistral implementation exactly, so this C runtime
conditions the decoder the same way the published checkpoint expects. `out`
must already hold `VOX_DEC_DIM` floats.
""",
    ('voxtral.c', 'vox_update_time_conditioning'): """
Recomputes everything that depends on the configured delay. It first rebuilds
`t_cond` (the time-conditioning vector — the sinusoidal encoding of
`delay_tokens` from the previous function), then for each of the 26 decoder
layers precomputes `ada_scale = ada_up(GELU(ada_down(t_cond)))`: a tiny
two-matrix network (3072 -> 32 -> 3072, with GELU, a smooth nonlinear
activation, between them) that turns the delay encoding into a per-layer
scaling vector the decoder later applies to its activations. Doing the work
here — into a buffer lazily allocated to `VOX_DEC_LAYERS x VOX_DEC_DIM` and
reused — keeps it out of the per-token decode loop; it runs at load time and
again whenever `vox_set_delay` changes the delay. The `ada_norm` weight
matrices are small f32 copies converted out of the weight file at load time and
owned (and later freed) by the context.
""",
    ('voxtral.c', 'load_bf16_direct'): """
Looks up one weight tensor (a named array of model parameters) in the
safetensors file — the model's weight container, which the loader maps into
memory rather than copying onto the heap — and returns a pointer straight into
that mapping, in bf16 (bfloat16, the 16-bit float format the weights are stored
in). No copy is made, so the pointer is owned by the mapping, not the caller;
a missing name logs to stderr and returns NULL so the load can abort.
""",
    ('voxtral.c', 'vox_adapter_load'): """
Loads the modality adapter — the small projection network that turns grouped
encoder audio vectors into the decoder's 3072-wide embedding space, the last
narrowing step of the funnel. It resolves the two projection matrices by their
long checkpoint names and stores borrowed bf16 pointers into the mapped weight
file; nothing is copied, so the pointers stay valid only while the safetensors
mapping is open. Returns -1 if either tensor is missing, which aborts model
loading.
""",
    ('voxtral.c', 'vox_load'): """
Builds the immutable model context: allocate, record defaults (320 ms delay,
weights read in place as bf16), open the memory-mapped
`consolidated.safetensors`, then load encoder, adapter, and decoder in turn —
each failure path hands whatever exists so far to `vox_free` and returns NULL.
It then precomputes the delay conditioning and, when Metal (Apple's GPU API) is
available, pre-warms the GPU weight cache: every bf16 matrix is converted once
into the f16 form the GPU kernels read, and the q/k/v and w1/w3 matrices are
warmed only as merged buffers, because the per-token step reads them merged —
caching them individually too would duplicate about 3.9 GB of weights that are
never read again. Without this warm-up the first decoded token would pay the
whole conversion cost as a visible latency spike. Finally it preallocates the
encoder's KV cache (its stored attention history) and reports GPU memory used.
""",
    ('voxtral.c', 'tok_embed_bf16_to_f32'): """
Fetches one token's embedding (the learned `dim`-float vector that represents
that vocabulary entry inside the model) from the memory-mapped bf16 table at
row `token_id` and widens it to f32 in caller scratch. The conversion is a pure
bit trick: bf16 is exactly the top 16 bits of an IEEE-754 float, so shifting
each value left by 16 and reinterpreting the bits yields the correct float with
zeros in the low mantissa bits. The decoder calls this every step to add the
previous token's embedding onto the audio (adapter) embedding before the next
forward pass.
""",
    ('voxtral.c', 'struct vox_stream'): """
The complete mutable state of one live transcription, grouped by funnel stage:
the incremental mel front end with its absolute sample counter; tail buffers
(`mel_tail`, `conv0_tail`, `conv0_residual`) carrying convolution boundary
context between chunks; leftover encoder positions awaiting four-way grouping;
the growing adapter buffer; decoder progress (`gen_pos`, `prev_token`, watchdog
streaks, restart counters); the circular queue of decoded text pieces that
Swift polls; and timing totals. The recurring pattern is one buffer plus one
absolute counter per stage: buffers compact their already-consumed prefixes to
stay small, while counters such as `total_adapter` and `gen_pos` keep counting
in absolute stream coordinates, so compaction can never change which moment of
audio a stored vector represents. The struct is private to this file; the
project ABI sees only opaque pointers.
""",
    ('voxtral.c', 'enum stream_tok_class'): """
The four-way classification a sampled token receives before the stream decides
what to do with it: TEXT (the token decodes to a non-empty UTF-8 piece),
CONTROL (an ID below 1000, the model's reserved non-text range), INVALID (a
text-range ID whose decode is empty), and EOS (the end-of-sequence token, the
model's signal that the current caption is complete). INVALID exists because in
Tekken (Mistral's tokenizer — the table mapping token IDs to byte sequences)
token 1000 is the raw byte 0x00, which as a C string is empty; counting such
tokens as text would let "decode activity with no visible output" defeat the
stall watchdogs.
""",
    ('voxtral.c', 'stream_classify_token'): """
Applies that classification to one token ID: EOS (the end-of-sequence token)
and the sub-1000 control range are recognized by ID alone; anything else is
decoded through the tokenizer, and a NULL or empty piece counts as INVALID
rather than TEXT. The distinction feeds the recovery logic in
`stream_run_decoder`: only genuinely visible text resets the non-text streak,
so a decoder stuck emitting byte 0x00 or control tokens still triggers a
restart.
""",
    ('voxtral.c', 'stream_conv_stem'): """
Pushes newly arrived mel frames (each a 10 ms slice of audio described as 128
spectral numbers — step 2 of the funnel) through the two-layer convolutional
stem incrementally, returning a freshly allocated `[out_len, 1280]` buffer of
post-convolution positions (caller frees; NULL when nothing emerges). Both
layers are causal convolutions: each output mixes its input with the two before
it and never a future one, which is what makes chunked streaming possible — but
it also means a chunk's first outputs would see zero padding where the real
previous frames belong. The cure is tail buffers: `mel_tail` keeps the last two
mel frames and `conv0_tail` the last two conv0 outputs, each prepended to the
next chunk so its early outputs are computed from real history, with the
pad-contaminated overlap discarded. `conv1` additionally has stride 2 — it
emits one output per two inputs, halving the rate to ~50 per second — so it
must always be fed an even count; an odd leftover conv0 column is parked in
`conv0_residual` and prepended next time, because otherwise the stride phase
would shift and every later output would be wrong. The streamed result is
exactly what one whole-lecture pass would have produced.
""",
    ('voxtral.c', '@665'): """
This stretch is the second convolution layer plus the epilogue. The first chunk
feeds `conv1` directly (zero left-padding is genuinely correct at the start of
the audio), while every later chunk prepends the two saved `conv0_tail`
positions and discards the first output those positions contaminate; the tail
is then refreshed from the last two columns of `feed`. After the stride-2
convolution and GELU (a smooth nonlinearity applied after each layer), the
surviving columns are transposed from the channel-major `[1280, len]` scratch
into the row-per-position `[len, 1280]` layout the encoder expects.
""",
    ('voxtral.c', 'stream_adapter_compact'): """
Reclaims adapter-buffer space once the decoder has consumed a prefix. Each
adapter row is one 3072-float audio embedding the decoder reads exactly once
(one 80 ms step of the funnel's final stage); rows behind `gen_pos` are dead,
so the surviving tail is memmoved to the front and `adapter_pos_offset`
advances by the discarded count. The logical counters (`gen_pos`,
`total_adapter`) keep counting absolute stream positions forever; a physical
index is always the logical position minus `adapter_pos_offset`, so compaction
never changes which moment of audio a row represents.
""",
    ('voxtral.c', 'stream_reset_decoder_state'): """
Hard-resets only the language half of the stream: zeroing the decoder KV cache
length and offset (the KV cache is the per-layer key/value vectors attention
re-reads for every earlier token, so clearing it forgets all text context),
dropping the adapter backlog and its logical offset, rewinding `gen_pos`, and
re-priming `prev_token` to BOS (the beginning-of-sequence token that starts
every prompt) with the EOS/streak/prompt flags cleared. Used on a plain EOS restart (and as the final step of the full reset): the
next caption starts from a clean prompt while the mel/convolution/encoder front
end keeps its place in the audio timeline. KV-cache overflow and control-token
loops escalate to `stream_reset_full_state` instead, which also rebuilds that
front end.
""",
    ('voxtral.c', 'stream_reset_full_state'): """
The deeper recovery: it rebuilds the audio front end as well. A fresh mel
context is allocated first — with the standard 32 tokens of leading silence the
model expects before speech — so that failure leaves the old state intact and
returns -1, letting the caller fall back to a decoder-only reset instead of
killing the stream. On success it swaps in the new mel context, zeroes every
conv-stem boundary buffer (`mel_tail`, `conv0_tail`, `conv0_residual`,
`enc_residual`) and the encoder KV cache (the encoder's stored attention
history), then chains into the decoder reset, leaving the stream in the state
of a brand-new one.
""",
    ('voxtral.c', 'stream_run_encoder'): """
The front half of the pipeline, run after every feed: it decides whether enough
new audio has arrived, then advances mel frames all the way to adapter
embeddings. The gate works in absolute mel coordinates — `mel_cursor` minus the
context's own offset locates the unprocessed frames even after old ones were
discarded — and demands `min_new_mel` new frames (312 for the very first chunk,
sized so the first batch already covers the decoder's prompt) unless the stream
is finishing. Stable frames then pass through three stages: the incremental
conv stem; the encoder transformer, 32 layers refining each 1280-float position
using a KV cache (the stored key/value attention vectors that let new positions
attend to earlier ones without recomputing them); and the adapter, which only
consumes groups of exactly `VOX_DOWNSAMPLE = 4` encoder positions, so up to
three leftovers are parked in `enc_residual` and prepended next round. New
adapter rows land in the doubling `adapter_buf` at physical offsets that
account for past compaction, `total_adapter` advances in absolute coordinates,
and the consumed mel frames are finally discarded from the front-end buffer.
""",
    ('voxtral.c', 'stream_fill_alts'): """
Builds the per-position alternatives array: `alts[0]` is always the decoded
text of the chosen token, and when alternatives are enabled (`n_alt > 1`) the
raw logits (the decoder's score for every vocabulary entry) are converted in
place by softmax (exponentiate and normalize so the scores become probabilities
summing to 1), then the text-range vocabulary is rescanned for the next-best
tokens. Collection stops once the relative distance `1 - p/best_prob` exceeds
`alt_cutoff` — only tokens nearly as probable as the winner qualify — or when
`n_alt` slots are filled. The stored strings are borrowed from the tokenizer,
and destroying the logits is safe because the buffer is refilled on every
decode step.
""",
    ('voxtral.c', 'stream_run_decoder'): """
The language half, also run after every feed. The decoder cannot start until
the adapter holds `1 + 32 + delay_tokens` rows — enough to pair one audio
embedding with each prompt token of `[BOS] + [STREAMING_PAD]...`, since every
decoder input is the sum of an adapter row and a token embedding. Once ready it
performs the prefill: all prompt positions except the last run through the
decoder in one batch purely to populate the KV cache (the per-layer key/value
vectors that each later step's attention re-reads), then the final position
runs as a normal step to produce the first token. After that it decodes
greedily — each step adds the previous token's embedding to the next unconsumed
adapter row, runs one forward pass, and takes the single highest-scoring
vocabulary entry, never sampling — for as long as adapter rows remain,
classifying every token so that only real text reaches the queue Swift polls
and the non-text streak watchdog stays armed. Keeping that queue separate from
inference means a slow or absent reader never stalls decoding.
""",
    ('voxtral.c', '@1088'): """
This page closes the generation loop and decides whether the stream must
restart. The adapter cursor advances after every step, and an EOS token (the
model's end-of-sequence marker: this caption is finished) breaks out of the
loop; the timing block then accumulates decoder milliseconds and, in monitor
mode, prints one glyph per decode batch encoding what it produced and how slow
it was. The remainder is the watchdog ladder for continuous mode: an EOS, a KV
cache (the stored attention history whose length sets per-step cost) past
`max_decode_context`, a long run of non-text tokens, or twenty seconds of audio
with no decoded token forces a decoder reset — escalated to a full front-end
reset when the trigger was anything other than a plain EOS, or after two
consecutive restarts that produced no text.
""",
    ('voxtral.c', 'vox_stream_init'): """
Allocates a zeroed stream and prepares every per-stream resource. The tokenizer
(the parsed table mapping the model's integer token IDs to UTF-8 text pieces)
is borrowed from the context and parsed only for the first stream: re-parsing
the 14 MB `tekken.json` on every session restart used to cost hundreds of
milliseconds for identical data. The incremental mel context is created with 32
tokens' worth of leading silence — the left padding the model was trained to
expect before speech begins. Then come the circular token queue (256 positions),
the decoder scratch buffers (logits, step embedding, token-embedding temporary),
single-best alternative mode, a cleared encoder KV cache, and the default
2-second processing interval. Any allocation failure tears down the partial
stream and returns NULL.
""",
    ('voxtral.c', 'vox_stream_feed'): """
The single streaming entry point for audio: append the float samples to the
incremental mel front end, advance the absolute sample counter, then give both
halves of the pipeline a chance to run. Feeding never implies finalization — a
sample near the end of the buffer may still lack the future samples its
analysis window and convolutions need (its right context), so it simply waits
in the tail buffers until later audio arrives. NULL streams, finished streams,
and non-positive sample counts are rejected with -1.
""",
    ('voxtral.c', 'vox_stream_finish'): """
Finalizes a stream: it first reuses `vox_stream_flush` to push the delay-window
padding through, then marks the stream finished and closes the mel front end —
`vox_mel_finish` reflect-pads on the right (mirrors the final samples so the
last analysis windows are complete) and drops the fully computed final frame purely to match the vLLM frame-count
convention (`stft[..., :-1]`). One last encoder+decoder pass then forces out the trailing tokens that
were still hidden behind the configured delay. Returns -1 if already finished;
afterward feed and flush are rejected, but queued tokens may still be drained.
""",
    ('voxtral.c', '@1513'): """
The first half drains the finished WAV-path stream: token pieces are appended
into a doubling heap string, the stream is freed, and the trimmed text is
returned. The rest is the raw-PCM path: the four already-peeked header bytes
are re-fed as two samples so no input is lost, then a loop reads 4096-sample
blocks from stdin, scales each signed 16-bit sample into a float in [-1, 1),
feeds it, and drains newly decoded pieces into the same growing string until
end-of-file triggers `vox_stream_finish`.
""",
    ('voxtral.c', 'vox_transcribe_stdin'): """
Reads stdin, peeking the first four bytes to choose a path. If they spell RIFF
(the magic bytes of the WAV container format), the whole file is buffered and
transcribed offline: the fmt/data chunks are parsed inline, multi-channel audio
is averaged down to mono, and other sample rates are linearly resampled to the
model's 16 kHz. Anything else is treated as raw s16le audio (headerless signed
16-bit little-endian samples) at 16 kHz mono and fed in 4096-sample blocks with
tokens drained between reads; the two peeked samples are fed before the read
loop so no input is lost. Either way the result is one caller-owned,
whitespace-trimmed string.
""",
    ('voxtral.c', 'vox_stream_flush'): """
Flush exists because the model deliberately reports text `delay_tokens` behind
the audio: at a caption boundary the app wants those withheld words now,
without ending the stream. The trick is to synthesize the future the decoder is
waiting for — first an alignment pad up to the next 1280-sample (80 ms) token
boundary, then `(delay_tokens + 1) + 10` tokens' worth of zero samples, fed
through the normal mel path in 4096-sample chunks. With that silence in place,
the encoder threshold `min_new_mel` is temporarily dropped to 1 so everything
buffered is processed immediately, both pipeline halves run, and the threshold
is restored. Unlike finish, the stream stays live; the injected silence simply
becomes part of the audio timeline.
""",
    ('voxtral.c', 'vox_stream_set_continuous'): """
Toggles continuous (live) mode. When on, the decoder is allowed to restart
itself periodically — notably once its KV cache (the stored attention history
every new token must re-read, so its length sets per-step cost) exceeds
`max_decode_context` — keeping decode steps fast across an unbounded lecture.
When off, the stream is a single bounded utterance that stops decoding at its
first EOS.
""",
    ('voxtral.c', 'vox_stream_set_max_decode_context'): """
Sets the ceiling (clamped to 250..8000 entries) on the decoder KV cache — the
stored attention history each new decode step must scan, so this ceiling
directly bounds worst-case per-token latency. On a continuous stream, crossing
it triggers the forced decoder restart in `stream_run_decoder`; without
continuous mode the value is never consulted.
""",
    ('voxtral.c', 'vox_set_delay'): """
Sets the streaming look-ahead delay in milliseconds (clamped to 80..2400) and
converts it to whole tokens at 80 ms per token, the decoder's 12.5 Hz step. The
delay is how far behind live audio the model is allowed to report text; a
larger value gives it more future acoustic context and steadier words at the
cost of latency. Because the delay reaches the decoder as a learned
conditioning signal, the function immediately recomputes `t_cond` and every
layer's `ada_scale` via `vox_update_time_conditioning`.
""",
    ('voxtral_audio.h', '@1'): """
The opening comment names this header's two services: loading WAV audio into
model-ready samples, and computing the log-Mel spectrogram (the frame-by-frame
energy-per-pitch picture built up in the chapter introduction) that Voxtral
actually consumes.
""",
    ('voxtral_audio.h', '#ifndef VOXTRAL_AUDIO_H'): """
Standard include guard: the rest of the header is compiled only when
`VOXTRAL_AUDIO_H` is not yet defined, so a translation unit that reaches this
file twice — directly and through another header — sees each declaration once.
""",
    ('voxtral_audio.h', '#define VOXTRAL_AUDIO_H'): """
Defines the guard macro, then pulls in the only two dependencies the prototypes
need: `<stddef.h>` for `size_t` and `<stdint.h>` for `uint8_t`. A minimal
include list keeps every file that uses the audio API cheap to compile.
""",
    ('voxtral_audio.h', 'vox_verbose_audio'): """
Module-wide diagnostic switch: when nonzero, the audio code reports details
such as resampling decisions on stderr. `extern` declares the variable without
creating storage; the single definition lives in `voxtral_audio.c`, so every
file that includes this header reads and writes the same flag.
""",
    ('voxtral_audio.h', '#endif /* VOXTRAL_AUDIO_H */'): """
Closes the include guard opened at the top of the file.
""",
    ('voxtral_audio.h', 'vox_parse_wav_buffer'): """
Parses a WAV image already in memory — WAV is a RIFF container, a sequence of
tagged chunks each carrying a four-byte type, a byte length, and a payload —
and returns owned 16 kHz mono float samples in [-1, 1]. Non-PCM encodings and
bit depths other than 16 are rejected; stereo is averaged down to mono and any
other valid sample rate is resampled to 16 kHz. Splitting parsing from file
I/O lets tests feed crafted byte buffers directly.
""",
    ('voxtral_audio.c', '@1'): """
The header comment pins this file to the vLLM reference pipeline it must
reproduce, and the `#define`s freeze that contract in numbers: 16 kHz input,
128 mel bins, a 400-sample (25 ms) window advanced 160 samples (10 ms) per
frame, and the 1.5 log ceiling. `N_FREQ` is `N_FFT/2 + 1 = 201` because the
DFT of real-valued audio is mirror-symmetric: bins above half the sample rate
would repeat the ones below, so only 201 distinct frequencies exist. The
`M_PI` fallback covers strict C modes whose `<math.h>` omits the constant.
""",
    ('voxtral_audio.c', 'vox_parse_wav_buffer'): """
WAV is a RIFF container: after the 12-byte `RIFF`/`WAVE` prologue, the file is
a sequence of chunks, each a four-byte tag plus a little-endian length plus
payload. The parser walks those chunks rather than assuming a fixed layout,
taking format fields from `fmt ` and sample bytes from `data`; every chunk
length is bounds-checked, odd-byte padding is respected, and the bogus
0xFFFFFFFF data size that piped ffmpeg writes falls back to the rest of the
buffer. Only 16-bit PCM is accepted: samples are scaled by 1/32768 into
[-1, 1], multi-channel frames are averaged to mono, and any rate other than
16 kHz is linearly interpolated to the model's required rate.
""",
    ('voxtral_audio.c', 'hertz_to_mel'): """
Maps a frequency in hertz onto the Mel scale — the perceptual pitch axis from
the chapter walk-through on which the 128 filters are spaced evenly. The
Slaney convention implemented here is piecewise: below 1000 Hz the mapping is
linear (3 mels per 200 Hz), and above it becomes logarithmic
(`min_log_mel + log(f/1000) * 27/log(6.4)`), mirroring how human pitch
resolution stays roughly constant at low frequencies and coarsens at high
ones. Changing this formula moves every filter and therefore shifts the
feature distribution away from what the checkpoint was trained on.
""",
    ('voxtral_audio.c', 'vox_mel_free'): """
Null-safe destruction of everything the incremental front end owns: the mel
filter bank, the DFT cosine/sine tables, the sample buffer, the mel frame
buffer, and the context struct itself. Every pointer previously borrowed
through `vox_mel_data` becomes invalid here.
""",
    ('voxtral_tokenizer.h', '@1'): """
The comment scopes this API to decoding only. The model emits token IDs —
plain integers indexing a fixed vocabulary of pieces, where each piece is a
short byte sequence from a byte-pair vocabulary (frequent strings earn their
own piece; anything rare is spelled out from several smaller pieces) — and
captioning only needs to map integers back to bytes. Nothing in the app turns
text into tokens, so no encoder is built.
""",
    ('voxtral_tokenizer.h', '#ifndef VOXTRAL_TOKENIZER_H'): """
Include guard, the same compile-once idiom used by `voxtral_audio.h`.
""",
    ('voxtral_tokenizer.h', '#define VOXTRAL_TOKENIZER_H'): """
Marks the guard taken; `<stdint.h>` is the header's lone include, since the
API otherwise trades only in plain `int` IDs and `char` pointers.
""",
    ('voxtral_tokenizer.h', 'vox_tokenizer_vocab_size'): """
Returns the extent of the token-ID space — how many distinct integer IDs the
model may legally emit — for range-checking decoder output. It is not a word
count, and (as the implementation shows) not the number of entries actually
loaded: it reports the fixed Tekken ID space.
""",
    ('voxtral_tokenizer.h', '#endif /* VOXTRAL_TOKENIZER_H */'): """
Closes the include guard.
""",
    ('voxtral_tokenizer.c', '@1'): """
The format comment is the file's real specification. tekken.json stores the
regular vocabulary as base64-encoded byte strings, each carrying a `rank` that
becomes its table position, plus a separate special-token list; a token ID is
just an integer, with 0..999 selecting special (control) tokens and 1000+rank
selecting the regular piece at that rank. The constants size the fixed tables
(130072 regular pieces, 1000 specials, 256 bytes per piece), and
`extern int vox_verbose` borrows the engine-wide logging level defined in
`voxtral.c`.
""",
    ('voxtral_tokenizer.c', 'b64_decode'): """
Base64 is a text encoding that lets JSON carry arbitrary bytes: each character
contributes 6 bits drawn from a 64-symbol alphabet, so four characters
reconstruct three raw bytes. This minimal decoder looks each input character
up in the 256-entry table, accumulates 6-bit groups in `val`, and emits a byte
whenever 8 bits are available, stopping at `=` padding and skipping any
non-alphabet character. It turns each vocab entry's `token_bytes` field into
the token's raw bytes, which may legitimately include embedded NULs.
""",
    ('voxtral_tokenizer.c', 'vox_tokenizer_decode_seq'): """
Two passes: the first totals piece lengths so the result is allocated exactly
once, the second copies the pieces in token order and appends the final NUL.
Both passes skip IDs below 1000 — control tokens such as BOS, EOS, and the
streaming pads are model protocol and must never surface as caption text.
Invalid IDs decode to NULL and contribute nothing, so they cannot index
outside the tables.
""",
    ('voxtral_tokenizer.c', 'vox_tokenizer_vocab_size'): """
Reports the fixed Tekken ID space — 1000 specials plus 130072 regular ranks,
131072 in all, matching the `default_vocab_size` recorded in tekken.json —
rather than the count of entries actually loaded, so range checks always
cover every ID the model could emit. The `(void)tok` cast tells the compiler
the unused parameter is deliberate.
""",
    ('voxtral_safetensors.h', '@1'): """
The comment is the complete format map: an 8-byte little-endian count, then
that many bytes of JSON metadata, then nothing but raw tensor bytes. Because
all structure lives in the small JSON header and the bulk data is located
purely by byte offset, the reader stays small and tensors can be served
straight out of the memory-mapped file.
""",
    ('voxtral_safetensors.h', '#ifndef VOXTRAL_SAFETENSORS_H'): """
Include guard for the weights-reader API.
""",
    ('voxtral_safetensors.h', '#define VOXTRAL_SAFETENSORS_H'): """
Marks the guard taken and includes `<stddef.h>` and `<stdint.h>`: byte counts
(`size_t`), shape dimensions (`int64_t`), and 16-bit element views
(`uint16_t`) are the currency of this API.
""",
    ('voxtral_safetensors.h', '#define SAFETENSORS_MAX_TENSORS'): """
Fixed capacity of the per-file metadata table. The descriptors live inline
inside the file handle, so the table needs no per-tensor allocation and frees
with the handle; `parse_header` simply stops accepting entries at this limit.
""",
    ('voxtral_safetensors.h', 'safetensor_dtype_t'): """
A dtype tags how each stored element's bits are interpreted and how many bytes
it occupies. `F32` is the ordinary 32-bit float; `F16` is IEEE half precision;
`BF16` is bfloat16 — a 16-bit format that keeps float32's full 8-bit exponent
(same numeric range) but only 7 mantissa bits (less precision), the format
Voxtral's weights ship in. `DTYPE_UNKNOWN = -1` keeps an unrecognized header
string representable: the open still succeeds, and only the typed accessor
that later touches such a tensor rejects it.
""",
    ('voxtral_safetensors.h', 'safetensor_t'): """
The descriptor for one tensor: a bounded name, its dtype, `ndim` (how many
dimensions) with up to eight dimension lengths, and the byte interval that
locates its data. `data_offset` is measured from the start of the data region
— the bytes after the 8-byte length and the JSON header — not from the start
of the file; `safetensors_data` adds those bases back. The struct holds
metadata only, owns no weight bytes, and never needs freeing on its own.
""",
    ('voxtral_safetensors.h', '\nsafetensors_file_t'): """
The open-checkpoint handle: the `mmap` base pointer with the file size needed
to `munmap` it later, the parsed header geometry, a heap copy of the header
JSON, and the tensor descriptors inline in a fixed array. The direct accessors (`safetensors_data`, `safetensors_get_bf16_direct`)
hand out pointers that borrow `data`, so this object must outlive those; the
`get_f32`/`get_bf16` accessors instead return owned copies that survive it.
`safetensors_close` is the single point where the mapping dies.
""",
    ('voxtral_safetensors.h', 'safetensors_get_bf16'): """
Returns a newly allocated copy of a BF16 tensor's raw 16-bit words; any other
dtype returns NULL — no conversion is performed. Unlike the borrowed pointer
from `safetensors_get_bf16_direct`, the caller owns and frees this buffer, so
it remains valid even after the file is closed.
""",
    ('voxtral_safetensors.h', '#endif /* VOXTRAL_SAFETENSORS_H */'): """
Closes the include guard.
""",
    ('voxtral_safetensors.c', '@1'): """
Besides the standard library, the includes pull in the POSIX machinery the
reader stands on: `<fcntl.h>` and `<unistd.h>` for `open`/`close`,
`<sys/stat.h>` for `fstat` (the file size the mapping needs), and
`<sys/mman.h>` for `mmap`/`munmap`. The opening comment records that the
reader was adapted from an earlier model-loading project.
""",
    ('voxtral_safetensors.c', 'safetensor_numel'): """
Multiplies the shape dimensions into the tensor's logical element count — a
[128, 201] tensor holds 25728 elements. The function itself validates
nothing; callers such as `safetensors_get_f32` reject `n <= 0` and check that
`n` times the element size fits inside the recorded `data_size` before
allocating or copying.
""",
    ('voxtral_safetensors.c', 'safetensors_get_bf16'): """
Accepts only BF16 tensors — any other dtype prints an error and returns NULL,
with no conversion path — then allocates `numel * 2` bytes and copies the raw
16-bit words out of the mapping. The caller owns the buffer independently of
the mapping, unlike the borrowed pointer `safetensors_get_bf16_direct`
returns.
""",
    ('voxtral_encoder.c', '@1'): """
The banner comment is the file's contract: the exact architecture recipe — conv
stem, 32 causal transformer layers with a sliding window of 750, final norm, 4x
downsample, adapter — that the code below implements step by step. The includes
pull in the engine context (`voxtral.h`), the math kernels, the safetensors
weight loader, and optionally Metal; `ENC_PREFIX` is the long checkpoint-name
prefix shared by every encoder weight lookup.
""",
    ('voxtral_encoder.c', 'load_f32'): """
Looks up one tensor (a weights array identified by its checkpoint name) and
returns an owned f32 copy. The small encoder weights — conv kernels, biases,
norm scales — are loaded this way because the compute kernels read them as
plain `float`; the huge matmul weights instead stay in their mapped bf16 form
via `load_bf16_direct`. A missing name logs an error and returns NULL, which
`vox_encoder_load` turns into load failure.
""",
    ('voxtral_encoder.c', 'load_bf16_direct'): """
Returns a pointer straight into the mmap'd safetensors file for a bf16 tensor
(bfloat16: the top 16 bits of an IEEE-754 float, so half the bytes at reduced
precision). Nothing is copied or converted — gigabytes of weight data stay
backed by the file mapping — so the pointer is borrowed, valid only while the
safetensors file stays open; the encoder's lifetime is therefore tied to that
mapping.
""",
    ('voxtral_encoder.c', 'vox_encoder_load'): """
Loads the 32-layer audio encoder by checkpoint name: the conv stem and every
per-layer bias and norm scale are small and materialized as f32, while the
large attention and FFN matrices (attention being the position-mixing step,
the FFN the per-position network — see the layer primer) stay as mmap'd bf16
read in place. The loading mirrors the model's asymmetric biasing — wq, wv,
wo, and FFN w2 carry biases but wk has none — so a wk bias is never even
requested. A missing conv-stem kernel, per-layer attention matrix, or final
norm aborts the load with -1.
""",
    ('voxtral_encoder.c', 'gelu_inplace'): """
A one-line wrapper that applies GELU (the smooth activation glossed in the
chapter intro) to a flat float vector by delegating to the shared `vox_gelu`
kernel. It exists so the stem code below reads as architecture — conv, then
GELU — rather than as kernel plumbing.
""",
    ('voxtral_encoder.c', 'causal_conv1d_out_len'): """
Computes how many output frames the causal convolution (a sliding weighted
window that reads only current and earlier inputs) produces for a given input
length, kernel width, and stride: the ceiling of
(length - kernel + padding)/stride + 1, clamped at zero, the same formula
`vox_causal_conv1d` applies internally. The caller needs this number up front
because C has no growable tensors — every conv output buffer is malloc'd to
exactly this size before the convolution runs.
""",
    ('voxtral_encoder.c', 'vox_encoder_forward'): """
The full, non-incremental audio-encoder pass. It transposes mel[frames,128] to
channel-major for the conv stem, runs the two causal conv1d+GELU layers (the
second strided by 2, roughly halving the sequence), then 32 transformer layers
exactly as in the layer primer: self-attention — each position taking a
weighted average of other positions' content, here 32 heads (independent
attention subspaces) of 64 dims over a sliding window of the last
VOX_ENC_WINDOW positions — then a SwiGLU feed-forward, each half wrapped in
RMSNorm (rescale to unit root-mean-square) and a residual add. RoPE (the
rotation that bakes position into queries and keys) starts at position 0
because this pass always begins a fresh sequence, and the encoder's
projections bias Q and V but not K (wk has no bias). A final RMSNorm yields
the returned [seq_len,1280] hidden state.
""",
    ('voxtral_encoder.c', '@253'): """
The second half of every layer iteration: the attention result (the
per-position mix computed just above) is projected from 2048 back to 1280 by
wo — Metal and CPU twins, the GPU path adding the f32 bias on the CPU — and
added onto `x`, the residual add of the layer primer. The FFN half then
repeats the pattern: RMSNorm (rescale each row to unit root-mean-square),
SwiGLU (SiLU-gated product of the w1 and w3 projections, then w2), and a
second residual add. After the 32nd layer the epilogue applies the final
RMSNorm in place, frees the nine scratch buffers plus the RoPE tables, and
returns `x` as the [seq_len,1280] encoder output.
""",
    ('voxtral_encoder.c', 'enc_kv_cache_k_at'): """
Pointer arithmetic for one row of the encoder's key cache (the per-layer store
of key vectors that attention re-reads for every earlier audio position): the
layout is [layer][capacity][2048], so the row sits at
(layer * capacity + pos) * 2048. The stride uses capacity `enc_kv_cache_max`,
not the current length, so addresses stay stable as the cache fills.
""",
    ('voxtral_encoder.c', 'enc_kv_cache_v_at'): """
The same row arithmetic for the value cache — values being the stored content
vectors attention averages, where keys are what it scores against. Keeping K
and V in two parallel buffers rather than interleaved lets each be moved and
copied as contiguous per-layer blocks during compaction and growth.
""",
    ('voxtral_encoder.c', 'vox_encoder_kv_cache_preallocate'): """
Reserves the encoder KV cache (the per-layer key/value store attention
re-reads each step) at a known maximum before live audio arrives, moving the
multi-megabyte allocation out of the first classroom utterance. On a Metal
system the buffers come from `vox_metal_shared_alloc` — memory visible to both
CPU and GPU, which the monolithic GPU encoder step requires — otherwise from
zeroed calloc. Idempotent: an already-allocated cache returns 0 untouched.
""",
    ('voxtral_encoder.c', 'enc_kv_cache_grow'): """
Grows the encoder's incremental KV cache (the per-layer key/value rows
attention re-reads) by doubling `enc_kv_cache_max` until the requirement fits,
then re-packing: each layer's region is `capacity * 2048` floats, so a larger
capacity moves every layer's base address, and the valid rows of all 32 layers
are memcpy'd into their new strided homes rather than realloc'd flat.
Metal-shared buffers cannot be resized, so shared mode refuses with an error
and relies on preallocation having been large enough.
""",
    ('voxtral_encoder.c', 'enc_kv_cache_compact'): """
Sliding-window eviction — the encoder only ever attends to the most recent
VOX_ENC_WINDOW positions, so older rows are dead weight. It keeps the last
VOX_ENC_WINDOW key/value rows per layer via memmove to position 0 and bumps
`enc_kv_pos_offset` by the discarded count. The offset is the critical half:
RoPE (each key's position baked in as a rotation) is already applied to the
cached keys, so rows may move physically but their logical positions must keep
counting upward — the cache invariant from the chapter intro. Mirrors the
decoder's kv_cache_compact but always operates on f32 rows.
""",
    ('voxtral_encoder.c', 'enc_realloc_float'): """
realloc through a temporary so the original buffer survives allocation
failure: assigning `realloc`'s result directly to `*ptr` would lose (and leak)
the old block when it returns NULL. Returns 0 on success and -1 on failure,
with existing contents preserved as realloc guarantees.
""",
    ('voxtral_encoder.c', 'enc_realloc_int'): """
The same fail-safe realloc idiom for the int arrays holding absolute positions
— the ever-increasing indices that RoPE (position encoded as rotation) is
computed from as audio keeps streaming in.
""",
    ('voxtral_encoder.c', 'encoder_forward_incremental_batch'): """
One bounded encoder step over a chunk of new conv-stem frames, reusing all
earlier work through the KV cache (the per-layer store of key/value vectors
attention re-reads instead of recomputing). It compacts/grows the cache to
fit, computes RoPE (position baked in as rotation) at logical positions
`enc_kv_pos_offset + cache_len` onward — counting absolute audio position, not
cache slot — projects Q/K/V for the new positions only, appends the new K/V
rows, and lets each new query attend over the full retained window. After 32
layers and the final norm it returns just the new positions' [new_len,1280]
output; when the cache is Metal-shared, the GPU path runs all 32 layers in one
command buffer and skips the CPU loop entirely.
""",
    ('voxtral_encoder.c', '@582'): """
The same per-layer second half as the full pass, restricted to the `new_len`
fresh positions: wo projection plus residual add, RMSNorm (rescale to unit
root-mean-square), SwiGLU feed-forward, second residual. After all 32 layers
the final norm runs and — the incremental difference — `enc_kv_cache_len`
advances to `cache_len + new_len`, committing the key/value rows appended
earlier in the loop (the cached attention inputs) so the next chunk attends
over them; only the new positions' [new_len,1280] output is returned.
""",
    ('voxtral_encoder.c', 'vox_adapter_forward'): """
Bridges encoder to decoder: downsamples 4x by concatenating every group of 4
consecutive encoder frames into one 5120-wide vector — trading sequence length
for width, so the decoder runs far fewer, fatter positions — then applies
Linear(5120->3072) -> GELU -> Linear(3072->3072) with bf16 weights to reach
the decoder's 3072 dimension. The returned [ds_len,3072] rows enter the
decoder exactly like token embeddings (the vectors a token id would otherwise
look up).
""",
    ('voxtral_encoder.c', 'vox_encoder_forward_incremental'): """
Public entry that feeds new positions to the encoder in batches of at most
VOX_ENC_INC_MAX_BATCH. The shared (Metal) KV cache — the per-layer key/value
store attention re-reads, preallocated at VOX_ENC_WINDOW plus that batch size
— cannot grow, so a single oversized call would fail and silently discard that
audio. Batching keeps results identical to separate smaller feeds (each batch
compacts, appends, and attends exactly as a smaller call would) while
concatenating their outputs into one buffer.
""",
    ('voxtral_decoder.c', '@1'): """
The banner records the decoder recipe — 26 layers of grouped-query attention
plus SwiGLU feed-forward — and documents `ada_rms_norm_t_cond`, the small
time-conditioning MLP whose effect is precomputed once into `ctx->ada_scale`
at load time, so the forward paths only multiply by `1 + ada_scale`. The
includes are the same engine/kernels/safetensors/optional-Metal set as the
encoder.
""",
    ('voxtral_decoder.c', 'load_f32'): """
Decoder twin of the encoder's loader: finds a tensor (a named weights array)
in the checkpoint and materializes an owned f32 copy for the fields the CPU
kernels read as plain `float` — the norm scales and the small ada-MLP weights.
A missing name logs an error and returns NULL, failing model load.
""",
    ('voxtral_decoder.c', 'load_bf16_direct'): """
Returns a zero-copy pointer into the mmap'd safetensors file for a bf16 tensor
(bfloat16: the high 16 bits of an IEEE-754 float). Because the bytes are never
copied, the mapping must outlive the decoder — close the file and every large
weight pointer dangles.
""",
    ('voxtral_decoder.c', 'load_bf16_direct_checked'): """
Like `load_bf16_direct`, but also validates the tensor's element count against
what the architecture requires. It guards the one tensor indexed by runtime
values: the token-embedding table (one 3072-wide vector per vocabulary id),
which the runtime indexes by token id — with an undersized tensor from a
malformed checkpoint, a large id would silently read past the end of the
mapping instead of failing at load time. A mismatch logs both counts and
returns NULL.
""",
    ('voxtral_decoder.c', 'vox_decoder_load'): """
Loads all 26 decoder layers by name: the large matmul weights — attention's
wq/wk/wv/wo (the four projections of the layer primer), FFN w1/w2/w3, and the
token-embedding table (the vocabulary-sized matrix mapping each token id to
its 3072-vector, reused "tied" as the output scoring matrix) — stay as mmap'd
bf16, while the small per-layer norms and ada_rms_norm MLP weights are
materialized in f32. The embedding table goes through the element-count check
because token ids index it at runtime. Returns -1 if the embeddings, any
layer's attention weights, or the final norm are missing.
""",
    ('voxtral_decoder.c', 'f16_to_f32'): """
Scalar IEEE half-to-single widening, used when the fp16 KV cache (the stored
key/value vectors attention re-reads, kept at half width to save memory and
bandwidth) must be materialized as fp32 for the CPU kernels. It handles all
three regimes: subnormals (renormalized bit by bit), inf/NaN (exp==0x1F), and
normal numbers via the 127-15 exponent rebias. This is true IEEE fp16 —
distinct from bf16, whose widening is a mere shift-left-16, because the two
formats split their 16 bits differently between exponent and mantissa.
""",
    ('voxtral_decoder.c', 'kv_cache_is_allocated'): """
Reports whether the decoder KV cache (the per-layer store of key/value vectors
attention re-reads for every earlier token) exists in whichever representation
is selected: the fp16 pointer pair when `kv_cache_fp16` is set, the f32 pair
otherwise. Prefill and the preallocation entry consult it so the cache can be
allocated lazily instead of crashing on first use.
""",
    ('voxtral_decoder.c', 'kv_cache_k_at'): """
Address of one f32 key row in the decoder KV cache (the stored key vectors
each new query is scored against). The layout is [layer][capacity][1024],
where 1024 = 8 KV heads (the shared key/value subspaces of grouped-query
attention) x 128 dims; the stride uses capacity `kv_cache_max`, so addresses
stay valid as the cache fills toward it.
""",
    ('voxtral_decoder.c', 'kv_cache_v_at'): """
The matching f32 value-row address — values being the content vectors
attention averages once the key scores have set the weights. Same
[layer][capacity][1024] arithmetic as the key side.
""",
    ('voxtral_decoder.c', 'kv_cache_k_f16_at'): """
Key-row address when the cache is stored as fp16 (16-bit floats, halving the
bytes streamed per generated token on the GPU path); identical
layer/capacity arithmetic over a `uint16_t` base pointer.
""",
    ('voxtral_decoder.c', 'kv_cache_v_f16_at'): """
The fp16 counterpart for value rows, completing the four accessors so that
every cache touch in this file goes through one audited piece of pointer
arithmetic.
""",
    ('voxtral_decoder.c', 'kv_cache_init'): """
Allocates the decoder KV cache (per-layer key/value rows that attention
re-reads each generated token) sized VOX_DEC_LAYERS * max_seq * (8*128)
elements per side, choosing the representation by context: fp16 in
Metal-shared memory when the GPU is present and fp16 mode is on, f32 shared
when GPU without fp16, plain zeroed f32 heap otherwise — CPU-only builds force
fp32 because the scalar kernels read `float`. Sets kv_cache_len to 0 but
deliberately leaves kv_pos_offset alone: the caller manages logical positions
across cache rebuilds so RoPE angles (position baked into keys as rotation)
never rewind.
""",
    ('voxtral_decoder.c', 'vox_decoder_kv_cache_preallocate'): """
Idempotent public wrapper: allocates the KV cache (attention's stored
key/value rows) at max_seq only when none exists, letting the host reserve
full capacity up front and avoid mid-stream grow-and-copy pauses while
captions are live. Returns 0 immediately when a cache is already present.
""",
    ('voxtral_decoder.c', 'kv_cache_grow'): """
Capacity growth for the KV cache (the per-layer key/value rows attention
re-reads): doubles kv_cache_max — starting from 256 if the cache was never
allocated, so a failed initial allocation cannot loop the doubling forever —
until the requirement fits, allocates fresh K/V buffers matching the current
mode (fp16 or fp32, Metal-shared or heap), and copies the first kv_cache_len
valid rows of every layer. The copy is a strided re-pack, not a flat realloc,
because each layer's region is `capacity * kv_dim` wide: a new capacity moves
every layer's base. Old buffers are freed through the allocator that created
them.
""",
    ('voxtral_decoder.c', 'kv_cache_compact'): """
Sliding-window eviction: the decoder never attends further back than
VOX_DEC_WINDOW positions (the window that bounds both attention cost and cache
size — see the chapter intro), so when the length exceeds it, each layer's
last VOX_DEC_WINDOW key/value rows are memmove'd down to slot 0 and
kv_pos_offset advances by the number discarded. RoPE (each key's position
baked in as a rotation) is already applied to the cached keys, so the kept
rows stay valid as-is; only the logical-position offset needs updating, never
any re-encoding. The fp16 and f32 representations get the same row arithmetic.
""",
    ('voxtral_decoder.c', 'kv_cache_switch_to_fp32'): """
One-way escape hatch from the fp16 KV cache (half-width storage of attention's
key/value rows) to fp32: allocates f32 K/V buffers, widens the first
kv_cache_len rows of every layer through f16_to_f32, frees the fp16 buffers,
and clears kv_cache_fp16. The CPU prefill/forward paths call it because the
scalar kernels read the cache as `float`; the GPU path never does, keeping the
bandwidth savings. Row order is preserved exactly, so positions and their
baked-in RoPE rotations stay aligned.
""",
    ('voxtral_decoder.c', 'vox_decoder_prefill'): """
Prefill — the batched pass that pushes all prompt positions through the
decoder at once instead of token by token — writes every prompt position's
key/value rows into the KV cache (the per-layer store attention re-reads) in
one sweep, amortizing setup across the whole audio-conditioned prompt. Cache
allocation or growth and the RoPE table (rotation angles for the logical
positions, including the offset accumulated by compactions) are prepared
before any dispatch, because the GPU monolithic path consumes them immediately
and returns early. The CPU fallback first forces the cache to fp32, then runs
the 26 layers as in the layer primer, including the decoder-only ada_scale
multiplier applied to the normalized FFN input.
""",
    ('voxtral_decoder.c', 'vox_decoder_forward'): """
One autoregressive step — each new token conditioned on everything generated
so far. It takes the single new 3072-d embedding, advances it through all 26
layers against the existing KV cache (the stored key/value rows that make each
step cheap instead of recomputing the whole history), appends this position's
K/V rows, and multiplies the final hidden state against the tied
token-embedding matrix to produce logits (one raw score per vocabulary token).
It then takes the greedy argmax itself — the single highest-scoring id, no
sampling — and returns that token id, while the caller's logits buffer stays
filled for diagnostics. Compaction or growth runs first when the cache is
full, and on allocation failure it returns 2, the end-of-sequence id, so
generation degrades to a clean stop rather than a crash.
""",
    ('voxtral_kernels.h', '@1'): """
The banner states the header's three ground rules: these are the low-level
math kernels, everything operates on float32 tensors (flat arrays interpreted
through a shape convention) in row-major order, and the code was adapted from
the flux-2-4b project. The include guard opens in the next block.
""",
    ('voxtral_kernels.h', '#ifndef VOXTRAL_KERNELS_H'): """
Opens the classic include guard: once the macro is defined, the preprocessor
skips the entire header on any repeat `#include` in the same translation unit.
""",
    ('voxtral_kernels.h', '#define VOXTRAL_KERNELS_H'): """
Defines the guard macro and pulls in the header's only two dependencies,
`stddef.h` and `stdint.h` — the fixed-width `uint16_t` from the latter is how
raw bf16 weights travel through these prototypes.
""",
    ('voxtral_kernels.h', 'vox_copy'): """
Copies `n` floats; the implementation is a plain memcpy, so source and
destination must not overlap.
""",
    ('voxtral_kernels.h', 'vox_conv1d('): """
General 1-D convolution — each output sample a weighted sum over a small
sliding window of input samples, the same weights reused at every position —
over channel-major tensors, with explicit symmetric padding; the encoder stem
calls only the causal variant below.
""",
    ('voxtral_kernels.h', 'vox_causal_conv1d'): """
The convolution variant whose explicit padding (kernel_size - stride) sits on
the left, plus implicit right zero-padding to reach the ceil-derived output
length, so the output at time t reads only inputs at t and earlier — never the future — which is
what lets the encoder run on still-growing live audio.
""",
    ('voxtral_kernels.h', 'vox_rms_norm'): """
RMS normalization: rescales each row to unit root-mean-square and then applies
a learned per-element weight, keeping activations in a stable numeric range
without the mean subtraction of full LayerNorm.
""",
    ('voxtral_kernels.h', 'vox_softmax'): """
Turns each row into a probability distribution — non-negative weights summing
to 1 — using the max-subtracted exponential so large scores cannot overflow
`expf`.
""",
    ('voxtral_kernels.h', 'vox_causal_attention'): """
Reference attention: each query position takes a softmax-weighted average of
the visible positions' value vectors, weighted by how well its query matches
their keys (the layer primer's core equation). The head geometry — how many
independent attention subspaces, and how many shared key/value heads — and the
causal/sliding-window position limits are all supplied explicitly by the
caller.
""",
    ('voxtral_kernels.h', 'vox_compute_rope_freqs'): """
Precomputes the cos/sin tables for RoPE (the scheme that encodes a token's
position by rotating its query and key vectors) from absolute integer
positions and the base frequency theta.
""",
    ('voxtral_kernels.h', 'vox_apply_rope'): """
Applies those rotations in place to every head (each independent attention
subspace), pairing adjacent coordinates — the interleaved GPT-J convention.
This is the position-injection step run on Q and K before attention.
""",
    ('voxtral_kernels.h', 'vox_verbose'): """
Global verbosity level defined in voxtral.c and shared by every engine file;
levels >= 2 gate the per-layer progress logging seen throughout the encoder
and decoder.
""",
    ('voxtral_kernels.h', 'vox_monitor'): """
Global flag for the one-glyph progress monitor: when set, the streaming code
prints a single stderr marker per pipeline event (encoder chunk, prefill, and
so on).
""",
    ('voxtral_kernels.h', '#endif'): """
Closes the include guard opened at the top of the header.
""",
    ('voxtral_kernels.c', '@1'): """
Beyond the standard includes, the preamble selects acceleration at compile
time: USE_METAL pulls in the GPU host API, and USE_BLAS selects Apple's
Accelerate framework or generic cblas elsewhere. `MIN_GPU_ELEMENTS` (512*512)
is defined as a GPU-dispatch threshold, but nothing in this file currently
consults it.
""",
    ('voxtral_kernels.c', 'vox_matmul_t'): """
Computes C[M,N] = A[M,K] @ B[N,K]^T, i.e. B is stored row-major with each
output column as a contiguous K-length row — exactly PyTorch's nn.Linear
weight layout. Both A and B rows then stream contiguously in the inner loop,
making this the cache-friendly variant used for projections and for the logits
(the raw per-vocabulary-token scores a decoder step ends with).
""",
    ('voxtral_kernels.c', 'bf16_to_f32_buf'): """
Expands a bf16 array into caller-provided f32 storage. Because bf16 is
literally the top half of an IEEE-754 float, widening is a single 16-bit left
shift per element — no arithmetic, just bit placement — which the loop
performs by writing through a uint32_t view of the destination.
""",
    ('voxtral_kernels.c', 'vox_linear_nobias_bf16'): """
Bias-free linear with bf16 weights, dispatched three ways: Metal when
available, the fused bf16 matvec when seq_len == 1 (the per-token decode
case), and otherwise widening W into the shared bf16_scratch f32 buffer before
calling the f32 vox_linear_nobias. The scratch is reused across calls, so
multi-token prefill (the batched pass over all prompt positions) avoids a
malloc per projection.
""",
    ('voxtral_kernels.c', 'vox_linear_bf16'): """
Same three-way dispatch as the nobias variant but threading the optional bias
through: the Metal and seq==1 paths add it inline, the multi-row path hands it
to vox_linear after widening W to f32. The encoder is the customer — its
query, value, output, and FFN-w2 projections (the per-layer matmuls of the
layer primer) carry biases, where the decoder's projections carry none.
""",
    ('voxtral_kernels.c', 'vox_matmul_t_bf16'): """
bf16-weight version of vox_matmul_t computing C[M,N] = A[M,K] @ B_bf16[N,K]^T:
M == 1 goes straight to the fused matvec with no intermediate buffer, larger M
widens B into the shared scratch and calls vox_matmul_t. This is how the
decoder's logits — one raw score per vocabulary token — are produced from the
tied bf16 token-embedding matrix, the same table used to embed input tokens.
""",
    ('voxtral_kernels.c', 'vox_conv1d'): """
Direct 1-D convolution — each output a weighted sum over a sliding kernel_size
window of the input — with explicit symmetric padding: out length is
(length + 2*padding - kernel_size)/stride + 1, weights are [out_ch, in_ch, k],
and both in and out are channel-major [C, L]. Out-of-range taps are skipped
rather than read, so no padded copy of the input is ever materialized.
""",
    ('voxtral_kernels.c', 'vox_causal_conv1d'): """
Causal (left-padded) conv1d matching vLLM's WhisperCausalConv1d:
padding_total = kernel_size - stride sits entirely on the left, so outputs
never read future samples. For speed it builds an im2col matrix (unrolling
each input window into a column, which turns convolution into one big matrix
multiply) and runs a single cblas_sgemm against the [out_ch, in_ch*k] weights,
adding bias afterward. This is the conv front end of the audio encoder stem.
""",
    ('voxtral_kernels.c', 'vox_rms_norm'): """
Per-row RMSNorm: divide each row by its root-mean-square so values land in a
stable range, then scale elementwise by the learned weight (see the layer
primer). Two precision details are load-bearing: eps is added inside the sqrt
— to the mean-square, not to the rms — and there is no mean subtraction or
bias, which is exactly what distinguishes RMSNorm from LayerNorm.
""",
    ('voxtral_kernels.c', 'vox_softmax'): """
Numerically stable row-wise softmax — rewriting each row as positive weights
that sum to 1 — done in place: subtract the per-row max before exponentiating,
then divide by the row sum; without the max shift, scores near 90 would
already overflow expf. The attention kernel below fuses its own softmax
online, so this standalone version serves the places where full score rows are
materialized.
""",
    ('voxtral_kernels.c', 'vox_causal_attention'): """
The scalar reference for attention — each query scores every visible key, and
the softmax of those scores weights an average of the value vectors, the layer
primer's core equation — in a single pass over out[seq_q, n_heads*head_dim].
It supports GQA: query head h reads KV head h/(n_heads/n_kv_heads), so several
query heads share one cached K/V stream. Each query attends from k_start (the
sliding-window lower bound) to global_pos+1, where global_pos = q_offset + i
enforces causality — no reading later positions. The online softmax is the
subtle part: a running max and correction factor let V be accumulated in one
pass without ever storing the score row, so scratch memory stays O(head_dim)
regardless of sequence length.
""",
    ('voxtral_kernels.c', 'vox_compute_rope_freqs'): """
Precomputes the cos/sin coefficients for RoPE (position injected by rotating
query/key coordinate pairs — see the RoPE section of the intro) into
freqs[seq, head_dim/2, 2] for the given integer positions, with per-pair
frequency 1/theta^(2d/dim). Doing the trig once per position here lets
vox_apply_rope stay a branch-free multiply-add loop even though it runs once
per layer.
""",
    ('voxtral_kernels.c', 'vox_apply_rope'): """
Applies the RoPE rotation (the position encoding) in place to
x[seq, heads*head_dim] using the precomputed cos/sin pairs: adjacent elements
(x0,x1) become (x0*cos - x1*sin, x0*sin + x1*cos) — each pair is one 2-D
rotation by the position-dependent angle. This is the interleaved
(GPT-J-style) pairing of adjacent dimensions, not the rotate-half GPT-NeoX
layout; choosing the wrong pairing silently yields wrong output. It runs on Q
and K before attention, and crucially before K is written to the KV cache,
which is why cached keys carry their positions baked in.
""",
    ('voxtral_metal.h', 'vox_metal_sgemm('): """
The all-float32 sibling of `vox_metal_sgemm_bf16`: C[M,N] = A[M,K] @ B[N,K]^T
with no precision conversion. B is uploaded once into the float weight cache
and reused on every later call, so only the activations A travel to the GPU
each time; the product itself runs through the same cached
`MPSMatrixMultiplication` path.
""",
    ('voxtral_metal.h', 'vox_metal_fused_qkv_bf16'): """
Computes the three attention projections Q, K, and V from one shared input by
recording all three matmuls into a single command buffer (the unit of work the
CPU submits to the GPU). The input is uploaded once and the CPU blocks once
instead of three times — the comment above prices this at two saved
round-trips per call.
""",
    ('voxtral_metal.h', 'vox_metal_fused_norm_qkv_bf16'): """
Extends the fused QKV call by running RMS normalization first, inside the same
command buffer: the rms_norm kernel writes the normalized vector into a GPU
scratch buffer and the three projection matmuls read it from there. The
intermediate never returns to the CPU, so norm plus projections cost one
submission and one wait.
""",
    ('voxtral_metal.h', 'vox_metal_fused_wo_ffn_bf16'): """
One call covers the whole second half of a transformer layer: project the
attention result through wo, add it into the residual `x`, re-normalize,
optionally scale by the adaptive conditioning vector (1 + ada_scale), run the
SwiGLU feed-forward, and add its output into `x` again. `x` is updated in
place, and because every step is encoded into one command buffer the layer
tail costs a single CPU/GPU synchronization.
""",
    ('voxtral_metal.h', 'vox_metal_batched_attention'): """
Full attention — QK^T, causal/window-masked softmax, scores @ V — for every
head in one command buffer. Instead of copying each head's columns out of the
packed [seq, heads*head_dim] arrays, it builds strided matrix views (MPS
matrix descriptors whose row stride is the full packed row, so a head's slice
is addressed in place). When there are fewer K/V heads than query heads
(grouped-query attention), several query heads read the same K/V slice.
""",
    ('voxtral_metal.h', 'vox_metal_encoder_attention'): """
Same arguments and tensor layout as `vox_metal_batched_attention`, but the
whole computation is a single custom-kernel dispatch instead of dozens of
per-head MPS matmul encodes. For the encoder's 32 heads that removes most of
the CPU-side encoding cost; the masking and grouped-query rules are identical.
""",
    ('voxtral_metal.h', 'vox_metal_fused_logits_bf16'): """
The decoding head in one submission: final RMS norm, the logits matmul against
the token-embedding matrix, and an argmax kernel that leaves the winning token
id in a four-byte buffer. The function returns that id; `logits_out` may be
NULL, in which case the vocabulary-sized logits array is never copied back —
greedy decoding only needs the four bytes.
""",
    ('voxtral_metal.h', 'vox_metal_decoder_wo_ffn_logits'): """
Closes a persistent-x token step: encodes the last layer's wo+FFN update of
the GPU-resident `x`, then the final norm, the vocabulary matmul, and the GPU
argmax, all in one command buffer. Returns the chosen token id; as with
`vox_metal_fused_logits_bf16`, passing NULL for `logits_out` skips the large
logits download.
""",
    ('voxtral_metal.h', '@1'): """
The opening comment is the file's one-paragraph contract: MPS-accelerated
matrix multiplication with BF16-to-FP16 weight caching, plus compute shaders
for element-wise work, ported from the author's earlier flux-2-4b project.
""",
    ('voxtral_metal.h', '#ifndef VOXTRAL_METAL_H'): """
Standard include guard: together with the `#define` on the next line, the
header's declarations are compiled at most once per translation unit no matter
how many files include it.
""",
    ('voxtral_metal.h', '#define VOXTRAL_METAL_H'): """
Defines the guard macro and pulls in the header's only two dependencies:
`stddef.h` for `size_t` and `stdint.h` for the `uint16_t` in which raw BF16
weight words are passed across this API.
""",
    ('voxtral_metal.h', '#ifdef __cplusplus\nextern "C" {'): """
If a C++ (or Objective-C++) file ever includes this header, `extern "C"`
disables C++ name mangling so the declarations keep the plain C symbol names
that `voxtral_metal.m` exports; under plain C the preprocessor drops the
wrapper entirely.
""",
    ('voxtral_metal.h', 'Initialize Metal acceleration'): """
Ends the conditional section that opened the `extern "C"` block. From here to
the bottom of the file, every declaration is preceded by a comment stating its
contract — return values, ownership, required call order — and those comments
are the documentation the C engine code is written against.
""",
    ('voxtral_metal.h', '#ifdef __cplusplus'): """
The closing brace of the `extern "C" {` region opened near the top of the
header, again emitted only when a C++ compiler is reading the file.
""",
    ('voxtral_metal.h', '#endif'): """
Ends the C++-only conditional around that closing brace.
""",
    ('voxtral_metal.h', '#endif /* VOXTRAL_METAL_H */'): """
Terminates the include guard opened on line 9.
""",
    ('voxtral_metal.m', '@1'): """
The imports bring in the three Apple frameworks (Foundation, Metal, and Metal
Performance Shaders), this runtime's own headers — including the embedded
shader source array — and `pthread.h`/`mach_time.h` for cache mutexes and
timing. The rest of the preamble holds the first slice of the file's global state:
the device and command queue, one pipeline-state global per compiled kernel,
the persistent decoder hidden-state buffer `g_dec_x`, and the eight-slot table
that maps shared allocations' CPU pointers back to their `MTLBuffer`s (the
weight and activation caches add more globals further down the file).
""",
    ('voxtral_metal.m', 'convert_bf16_to_f16'): """
Bulk BF16-to-FP16 conversion behind every weight cache. The arm64 path
exploits the formats' kinship — a bfloat16 word is exactly the top half of a
float32 — so the loop widens eight values per iteration — two `vshll_n_u16` calls of
four lanes each shift them 16 bits left into f32 lanes, and `vcvt_f16_f32` rounds them to f16 in hardware
(round-to-nearest, slightly more accurate than the truncating scalar
`bf16_to_f16`). Because this conversion dominates model-load time, tensors of
two million elements or more are split into one-million-element chunks across
cores with `dispatch_apply`, Grand Central Dispatch's parallel for-loop; the
`^(size_t c){ ... }` argument is a C block (a function value that captures the
surrounding variables), and each chunk re-enters this function below the
threshold. Leftover elements and non-ARM builds use the scalar helper.
""",
    ('voxtral_metal.m', 'vox_metal_fused_wo_ffn_bf16'): """
The standalone (non-persistent-x) form of a layer's second half: ten encoded
steps in one command buffer. This page allocates the scratch set and encodes
steps 1-4: proj = attn_out @ wo^T (an MPS matmul), x += proj (the residual
add), x_norm = rms_norm(x, ffn_norm), and, when conditioning is present,
x_norm *= (1 + ada_scale). Both `x` and `attn_out` are uploaded on entry; the
continuation page carries the SwiGLU FFN, the second residual, the single
commit/wait, and the copy of the updated `x` back to the caller.
""",
    ('voxtral_metal.m', 'encode_wo_ffn_steps'): """
Helper that appends the wo+FFN block for one layer onto an already-open
command buffer, reading attn_out and updating the GPU-resident g_dec_x in
place. It prefers the fused custom kernels when their pipelines compiled —
decoder_wo_residual, decoder_ffn_gate, and decoder_w2_residual each perform a
matrix-vector product and its surrounding residual/activation work in a single
pass — and otherwise falls back to MPS matmuls with separate silu/mul/add
dispatches. Dependent dispatches inside one compute encoder are ordered with
`memoryBarrierWithScope`, a fence guaranteeing that earlier dispatches' buffer
writes are visible to later ones.
""",
    ('voxtral_metal.m', 'vox_metal_batched_attention'): """
Classic three-stage attention in one command buffer using MPS matmuls: a
per-head strided QK^T fills a scores buffer, one causal_softmax compute
dispatch normalizes all (head, query) rows, then per-head scores @ V produces
the output. Q/K/V/out are never deinterleaved: each head is addressed through
a strided MPSMatrix view (a descriptor whose row stride is the full packed
row, plus a per-head byte offset). Grouped-query attention — more query heads
than K/V heads — is handled by pointing head h at K/V head h / gqa_ratio.
""",
    ('voxtral_metal.m', 'vox_metal_encoder_attention'): """
Uploads Q/K/V and runs the entire attention as one compute dispatch instead of
the per-head MPS encodes of `vox_metal_batched_attention` — the section
comment prices the old path at 64 matmul encodes for the encoder's heads. The
grid is one 64-thread threadgroup per (head, block of 8 query rows), matching
the shader's ATTN_BQ tiling; after a single commit/wait the output is copied
back and the scratch buffers return to the pool.
""",
    ('voxtral_metal.m', '@1517'): """
Steps 5-10, the SwiGLU feed-forward on the normalized vector: two MPS matmuls
compute gate = x_norm @ w1^T and up = x_norm @ w3^T, two element-wise
dispatches apply silu(gate) and gate *= up, a third matmul produces
ffn_out = gate @ w2^T, and add_inplace folds it into x as the layer's second
residual. One commit/wait then copies the updated x back to the caller and
returns every scratch buffer to the pool.
""",
    ('voxtral_metal.m', '@1772'): """
The FFN half, with a fast and a fallback path at each end. If the fused
decoder_ffn_gate pipeline exists, one dispatch reads the merged [w1;w3]
weights and writes silu(x_norm @ w1^T) * (x_norm @ w3^T) straight into
bufGate; otherwise a single merged matmul fills [gate; up] and separate
silu/mul dispatches combine the buffer's two halves through byte offsets. The
down projection mirrors this: decoder_w2_residual folds gate @ w2^T into
g_dec_x in one pass, or an MPS matmul plus add_inplace does it in two.
""",
    ('voxtral_metal.m', '@2604'): """
Still inside each layer's compute encoder: the rotated K and V rows are copied
into the shared KV cache at this layer's slot for the current position (using
the f16 copy kernel when the half-precision cache is active), a second barrier
publishes those writes, and decoder_attention computes the whole single-token
attention with one 32-thread threadgroup per head reading the cache in place.
After the 26-layer loop the code appends the last layer's wo+FFN, the final
rms_norm of g_dec_x, the logits matmul against the cached f16 token-embedding
matrix, and argmax_f32, then commits once and waits; the CPU reads back the
4-byte token id (plus full logits only on request) and records the new cache
length pos + 1.
""",
    ('voxtral_metal.m', '@2877'): """
The interior of each encoder layer's combined Q/K/V pass — one compute encoder
with barriers between phases: strided bias adds put wq_bias on the Q columns
and wv_bias on the V columns of the packed QKV rows (the encoder, unlike the
decoder, carries bias vectors), batched RoPE rotates the Q then K slices with
one thread per (position, head, dimension-pair), strided copy kernels append
the M new K and V rows to this layer's region of the shared cache, and
encoder_attention_qstrided runs all heads with one 64-thread group per
(head, 8-query block). q_offset is the physical cache index, because window
masking must use the same coordinates the cache rows are stored under.
""",
    ('voxtral_metal.m', '@2996'): """
Per-layer steps 4 and 5, plus the start of the FFN: an MPS matmul applies the
output projection wo, then one encoder adds wo_bias, folds the projection into
the residual x, and re-normalizes into bufXnorm, with barriers because each
dispatch reads its predecessor's output. Step 6 opens with a single matmul
against the merged [w1;w3] buffer — each output row holds gate and up side by
side, hidden*2 wide — and silu_mul_merged collapses every pair to
silu(gate) * up in place.
""",
    ('voxtral_metal.m', '@3124'): """
The down projection reads bufGate through a strided matrix descriptor —
rowBytes is hidden*2 floats, so the matmul consumes only each row's combined
gate half without compacting the buffer first — and a final encoder adds
w2_bias plus the second residual into x. After the 32-layer loop one more
rms_norm writes the result into bufXnorm, and the single commit/wait runs,
timed with mach_absolute_time and reported at verbose level 2 as encode versus
commit+wait milliseconds. The output is copied back from bufXnorm because that
is where the final norm wrote.
""",
    ('voxtral_metal.m', '@3364'): """
Inside each layer's RoPE/cache/attention encoder: batched RoPE rotates the Q
and K slices of the packed QKV rows in place, a barrier publishes the
rotation, strided copy kernels append the M new K and V rows to this layer's
region of the decoder cache (f16 variants when the half-precision cache is
enabled), and after another barrier the attention dispatch reuses the
encoder's q-strided kernel with one 128-thread group per (head, 8-query
block). q_offset is kv_pos_offset + start_pos, so causal and sliding-window
masks see absolute token positions rather than buffer indices. The page ends
with the wo projection matmul and the opening of the residual/norm encoder.
""",
    ('voxtral_metal.m', '@3494'): """
The layer's tail: add_inplace folds the wo projection into the residual x,
rms_norm re-normalizes into bufXnorm, and when the model carries an ada_scale
conditioning table the normalized rows are multiplied by
(1 + ada_scale[layer]) — the same conditioned-norm sequence the single-token
path uses. The FFN then repeats the merged pattern ([gate;up] matmul,
silu_mul_merged, strided w2 read, residual add), the 26-layer loop closes, and
after the one commit/wait the updated hidden states are copied back and
ctx->kv_cache_len advances by seq_len, so the next decode step appends behind
the prefilled positions.
""",
    ('voxtral_metal.m', '@3799'): """
The decoder half of the dummy-matmul warmup: it materializes layer 0's merged
QKV, wo, merged [w1;w3], and w2 weight buffers, then encodes one matmul of
each shape at the prefill width M=38 and waits — actually executing a shape is
what triggers Metal's GPU pipeline compilation, so the cost lands here instead
of in the first real prefill. The closing loop pre-uploads every encoder
layer's attention and FFN norm vectors, plus the final encoder norm, into the
f32 weight cache.
""",
    ('voxtral_shaders.metal', '@1'): """
The header comment states the file's job: small GPU kernels for the element-wise
work between MPS matrix multiplications, so intermediate tensors never detour
through the CPU. `#include <metal_stdlib>` pulls in Metal's standard library
(math functions, the 16-bit `half` type, the SIMD reduction intrinsics), and
`using namespace metal` makes those names usable without a `metal::` prefix —
the only setup the whole shader file needs.
""",
    ('voxtral_shaders.metal', 'rms_norm'): """
Computes RMSNorm — out = x * rsqrt(mean(x²)+eps) * weight — with one threadgroup
(a block of threads sharing a small fast on-chip memory and able to synchronize)
per sequence row; `row` is `threadgroup_position_in_grid` (which group this is),
`tid` the thread's index inside the group, and the `[[buffer(n)]]` attributes
number the argument slots the host binds each tensor to. Each of the 256 threads
strides over the row accumulating a private sum of squares into the `shared_sum`
scratch array; the halving loop is a tree reduction — after each
`threadgroup_barrier` (a checkpoint no thread passes until all arrive, which
makes the scratch writes visible) the live half of the threads fold their
neighbor's slot into their own until slot 0 holds the whole row's sum. Every
thread then reads that total, forms the inverse root-mean-square, and rescales
its strided slice by it and the learned per-channel weight. The two barriers
bracket the reduction, and the strided loops mean the group width need not
divide `hidden`.
""",
    ('voxtral_shaders.metal', 'silu'): """
In-place SiLU activation x = x/(1+exp(-x)), the feed-forward gate nonlinearity.
The grid is one thread per array element: `gid` is `thread_position_in_grid` —
this thread's own index across the whole dispatch — and doubles as the element
index, while the `[[buffer(n)]]` numbers are the argument slots the host fills.
The `gid < n` guard is defensive: this host dispatches exactly n threads
(`dispatchThreads`, Metal's non-uniform threadgroups API), so no out-of-range
thread is ever launched; the guard only matters if a future host rounded the
grid up to whole threadgroups.
""",
    ('voxtral_shaders.metal', 'gelu'): """
In-place GELU (a smooth bell-curve gating nonlinearity used in transformer
feed-forward layers, similar in role to SiLU) in its standard tanh
approximation 0.5*x*(1+tanh(sqrt(2/pi)*(x+0.044715*x³))), with the sqrt(2/pi)
constant baked in as 0.7978845608. One thread per element: `gid`
(`thread_position_in_grid`, the thread's index across the dispatch) selects the
element, and the `gid < n` guard is defensive (this kernel's pipeline is
compiled but the current host never dispatches it — GELU runs on the CPU and
inside fused kernels instead).
""",
    ('voxtral_shaders.metal', 'add_inplace'): """
Elementwise a[i] += b[i] over n elements, one thread per index (`gid`, the
thread's position in the dispatch grid) with a bounds guard. Its reason to exist
is the residual add: transformer layers compute x = x + f(x), and running this
trivial kernel between MPS matmuls folds that add on the GPU instead of copying
both tensors back to the CPU just to sum two arrays.
""",
    ('voxtral_shaders.metal', 'mul_inplace'): """
Elementwise a[i] *= b[i], the same one-thread-per-element shape as add_inplace.
It applies the SwiGLU product (the feed-forward design where one projection
"gates" another by elementwise multiplication): a holds the silu-activated gate
and b the up projection, so after this kernel a is ready for the down
projection — all without leaving the GPU.
""",
    ('voxtral_shaders.metal', 'ada_scale_mul'): """
Adaptive-RMSNorm conditioning: x[i] *= (1 + scale[i % stride]). The scale
vector is one entry per channel (length `stride`) and the modulo replays it
across every row, so a whole [rows, stride] tensor is conditioned in one
dispatch with one thread per element (`gid`, the thread's grid position, with a
bounds guard). The "1 +" makes a zero scale the identity — the model learns a
correction around "leave it unchanged" rather than an absolute gain.
""",
    ('voxtral_shaders.metal', 'argmax_f32'): """
Finds the index of the largest float in an array — greedy token selection done
on the GPU so only the winning index, not the whole logits row, returns to the
CPU at the end of a decode step. A single threadgroup (a block of cooperating
threads with shared scratch memory) does the whole job: each thread scans a
strided slice keeping its private best (value, index) pair in the parallel
shared arrays, then a tree reduction — repeatedly halving the live thread count
with a `threadgroup_barrier` (an all-arrive checkpoint) between rounds — keeps
whichever pair holds the larger value. Thread 0 writes the surviving index to
out[0].
""",
    ('voxtral_shaders.metal', 'causal_softmax'): """
Turns rows of raw attention scores into probabilities for the path that
materializes the full score matrix (vox_metal_batched_attention). Softmax must
subtract the row maximum before exponentiating or exp() overflows, so each row
runs three phases with tree reductions in shared scratch between them: phase 1
overwrites every key outside [valid_start, valid_end] with -INFINITY — the
causal rule (a query may only attend to keys at or before its own position)
plus the optional sliding window (keys more than window_size-1 positions back
are also hidden) — while reducing the row max; phase 2 replaces each entry with
exp(x - max) while reducing the sum; phase 3 multiplies by 1/(sum+1e-10), the
epsilon protecting a fully masked row. One threadgroup (cooperating thread
block with barriers) per (query, head) pair, decoded from group_id =
head*seq_q + qi; every phase strides over seq_k so any row length works.
""",
    ('voxtral_shaders.metal', 'rope_apply'): """
Applies RoPE — rotary position embedding, which encodes "where in the sequence
this token sits" by rotating each adjacent pair of vector components through an
angle that grows with position — to one token's [n_heads, head_dim] block of Q
or K, in place. freqs supplies the precomputed (cos, sin) for each pair index
at this position; one thread per (head, pair) applies the standard 2-D rotation
to elements 2i and 2i+1. Threads past n_heads*head_dim/2 return immediately — a defensive guard, since
this host dispatches exactly that many threads via `dispatchThreads`.
""",
    ('voxtral_shaders.metal', 'kv_cache_copy'): """
Appends one token's freshly projected K (or V) vector to the KV cache — the
per-layer store of every earlier position's key/value vectors, which attention
re-reads on every later step. One thread per element copies data[gid] to
cache[float_offset+gid], with a defensive gid < kv_dim guard (the host dispatches exactly kv_dim
threads via `dispatchThreads`); the host computes float_offset from layer, position, and kv_dim so each token lands
in its own slot. Doing the copy as a kernel keeps the cache write inside the
same GPU command stream as the matmul that produced the data.
""",
    ('voxtral_shaders.metal', 'kv_cache_copy_f16'): """
The same single-token cache append, but the destination is `device half *` —
half is 16-bit floating point, two bytes instead of float's four — and
half(data[gid]) rounds each value on store. This halves both the cache's
footprint and the bytes attention must stream back per step; the precision loss
is confined to the cached K/V, since arithmetic elsewhere stays f32.
""",
    ('voxtral_shaders.metal', 'decoder_attention'): """
The hot kernel of decoding: attention for one new token (seq_q=1) against the
whole KV cache (the stored key/value vectors of every earlier position). Each
query head gets one threadgroup of exactly 32 threads — a single SIMD group,
the bundle the hardware runs in lockstep, whose lanes can combine values with
simd_sum without barriers or shared memory; that is why this kernel needs no
threadgroup_barrier at all. head_dim is 128, so lane `tid` owns dimensions tid,
tid+32, tid+64, tid+96 and preloads its four Q components; kv_head maps the
query head to its cache head, because grouped-query attention (GQA) lets
gqa_ratio query heads share one cached K/V head to shrink the cache.

The loop is a single pass over the valid keys — causal (j ≤ q_pos) plus the
optional sliding window. Per key j: each lane multiplies its four Q components
with the matching K components and simd_sum folds the 32 partials into the full
128-term dot product, scaled by the host-supplied scale (1/sqrt(head_dim)).
Softmax needs the row maximum before any exp, which a streaming pass cannot
know in advance, so the kernel keeps an *online softmax*: a running max, a
running sum of exp(score-max), and four output accumulators. Whenever a new
score raises the max, correction = exp(old_max-new_max) shrinks the sum and
accumulators so earlier work stays measured against the new reference; then
weight = exp(score-max) joins the sum and weight*V[j] joins the accumulators.
After the loop the accumulators hold exactly the weighted V sum, so dividing by
running_sum (+1e-10 against an all-masked row) yields the softmax average, and
each lane writes its four output dimensions.
""",
    ('voxtral_shaders.metal', 'decoder_attention_f16'): """
The identical algorithm to decoder_attention — one 32-thread SIMD group (the
hardware's lockstep bundle) per query head, four dimensions per lane, one
online-softmax pass (running max and sum, with exp(old_max-new_max) rescaling)
over the causally valid keys — except K_cache and V_cache are typed
`device const half *` (16-bit floats) and every load is widened with float()
before the dot product and the V accumulation, so all arithmetic still runs in
f32. Q and the output stay f32 throughout. The host dispatches this variant
when ctx->kv_cache_fp16 selected the half-precision KV cache; the benefit is
purely bandwidth — half the cache bytes streamed per generated token.
""",
    ('voxtral_shaders.metal', 'encoder_attention'): """
Batched attention for whole sequences (encoder layers and decoder prefill),
tiled so memory traffic is shared: one threadgroup (a thread block with common
scratch memory and barriers) per (head, block of ATTN_BQ=8 consecutive
queries), so every K and V vector fetched serves eight queries instead of one.
The group has one thread per head_dim element — 64 threads (2 SIMD groups) or
128 (4), a SIMD group being a 32-thread lockstep bundle with its own register
level reduction, simd_sum. Each thread preloads its single component of all
eight query vectors (q_vals) and keeps eight independent online-softmax states:
running max rmax, running sum rsum, and one output-component accumulator acc
per query. The loop bounds are the union of the eight queries' causal/window
key ranges.

Per key j, three sub-steps. Dot products: every thread multiplies its K
component by each of its eight Q components; simd_sum folds each product across
a SIMD group's 32 lanes, and lane 0 parks the per-group partial in the tg_simd
scratch array. After a threadgroup_barrier (the all-arrive checkpoint that
makes scratch writes visible), the first eight threads each finish one score by
summing across SIMD groups and applying scale (1/sqrt(head_dim)) into
tg_scores; a second barrier publishes them. Masking and accumulation: each
thread loads its V component once, then for each query — skipping keys outside
that query's own causal/window range — runs the online-softmax update: if the
score raises rmax, corr = exp(old_max-new_max) rescales rsum and acc so earlier
contributions stay consistent, then exp(score-max) joins the sum and, times the
V component, the accumulator. Finally each thread writes its component of all
eight output rows, dividing by rsum + 1e-10.
""",
    ('voxtral_shaders.metal', 'encoder_attention_kv_f16'): """
The same Q-tiled batched attention as encoder_attention — eight queries per
threadgroup, two-barrier cooperative score reduction, per-query online softmax
(running max/sum with exp-rescaling) — but K and V are `device const half *`
(16-bit floats), widened with float() as each component is loaded, so the
arithmetic and the output remain f32. Q stays f32 too. This serves the
half-precision KV-cache encoder/prefill path, where halving the cached bytes
halves the memory traffic the loop spends streaming K and V.
""",
    ('voxtral_shaders.metal', 'encoder_attention_qstrided'): """
The same Q-tiled attention as encoder_attention with two extra constants,
q_stride and q_col_offset, that change only where Q is read: query row qi
starts at qi*q_stride + q_col_offset instead of qi*(n_heads*head_dim). That
lets Q stay in place as a column slice of the merged QKV matmul output (one
wide row holding Q, K, and V side by side), so the monolithic encoder/prefill
steps skip the deinterleave copy that would otherwise extract Q into its own
tensor first. The output is still written contiguously, and the masking, GQA
head sharing, and online-softmax phases are unchanged.
""",
    ('voxtral_shaders.metal', 'encoder_attention_kv_f16_qstrided'): """
The fourth member of the encoder_attention family combines both variations: Q
is read through q_stride/q_col_offset directly out of the packed QKV buffer (no
deinterleave copy), and K/V are half (16-bit floats) widened with float() on
load, with all arithmetic and the output still f32. The eight-query tiling, the
two-barrier cooperative score reduction, and the per-query online-softmax
updates are byte-for-byte the same as encoder_attention; only the Q addressing
and the K/V element type differ. The host selects it when the KV cache is kept
in f16.
""",
    ('voxtral_shaders.metal', 'bias_add'): """
Adds a learned per-channel bias to every row of a [seq_len, dim] tensor: thread
gid (its index in the dispatch grid) owns one element and adds bias[gid % dim],
the modulo replaying the dim-length bias vector across all rows; the total
guard covers the rounded-up grid. The host uses it to finish a linear layer's
+b term right after the MPS matmul that computed x*W, keeping the whole layer
on the GPU.
""",
    ('voxtral_shaders.metal', 'bias_add_strided'): """
The slice-aware bias add for the packed QKV layout: gid maps to (row, col)
within a chunk_cols-wide window, and the write lands at
row*row_stride + col_offset + col. Because the merged QKV matmul leaves Q, K,
and V side by side in one wide row, the host points col_offset at just the Q or
V columns and adds wq's or wv's bias there without disturbing the neighboring
slices.
""",
    ('voxtral_shaders.metal', 'batched_rope_apply'): """
The whole-sequence version of rope_apply, for when many positions are processed
at once (encoder and prefill): one thread per (position, head, component-pair)
triple, all decoded by division and modulo from the flat grid index gid. Unlike
the single-token kernel, freqs holds a (cos, sin) pair per position per pair
index, so each row is rotated by its own position's angles — RoPE encodes
position by rotating adjacent component pairs through position-dependent
angles. Threads past the total return early.
""",
    ('voxtral_shaders.metal', 'batched_rope_apply_strided'): """
Batched RoPE re-addressed for the packed QKV buffer: the element base becomes
pos*row_stride + col_offset + head*head_dim, so the Q (or K) columns can be
rotated in place inside the wide merged row — Q, K, and V sitting side by side
after one matmul — instead of being copied out first. The frequency lookup and
the pairwise rotation are exactly batched_rope_apply's.
""",
    ('voxtral_shaders.metal', 'batched_kv_cache_copy'): """
Bulk version of kv_cache_copy: appends a whole [seq_len, kv_dim] block of new K
or V rows to the KV cache (the store of every earlier position's key/value
vectors that attention re-reads) in one dispatch, one thread per element with a
guard over total. The host computes cache_offset from layer and starting
position; prefill and the encoder use it whenever many positions arrive at
once.
""",
    ('voxtral_shaders.metal', 'batched_kv_cache_copy_f16'): """
The same bulk cache append with the destination typed half (16-bit floating
point, two bytes per value instead of four): half(data[gid]) rounds each f32 on
store. One thread per scalar; the rounding halves the cache's memory and the
bandwidth every later attention step spends streaming it back.
""",
    ('voxtral_shaders.metal', 'batched_kv_cache_copy_strided'): """
Bulk cache append that gathers its source from a column slice: gid maps to
(row, col) inside a chunk_cols window, reads
data[row*src_stride + src_col_offset + col], and writes the cache contiguously
at cache_offset+gid. This lets the monolithic steps copy the K and V slices
straight out of the merged QKV matmul output — where Q, K, and V share one wide
row — into the cache, the strided read doing the deinterleave for free during
the copy.
""",
    ('voxtral_shaders.metal', 'batched_kv_cache_copy_strided_f16'): """
Combines the slice gather and the precision narrowing in one kernel: each
thread reads its K or V element out of the wide merged QKV row
(row*src_stride + src_col_offset + col) and stores it rounded to half (16-bit
float) in the contiguous cache. The f16-cache path thus needs neither a
separate deinterleave pass nor a separate conversion pass — one dispatch does
both on the way into the cache.
""",
    ('voxtral_shaders.metal', 'deinterleave'): """
The general strided-to-contiguous gather that the _strided cache kernels
specialize: copies the chunk_cols-wide column slice starting at col_offset out
of an [M, src_stride] matrix into a packed [M, chunk_cols] destination, one
thread per output element with (row, col) decoded from the flat gid. The host
uses it to split a merged projection result — several matrices computed as one
wide matmul for efficiency — back into its component tensors when a consumer
needs them contiguous.
""",
    ('voxtral_shaders.metal', 'silu_mul_merged'): """
Fused SwiGLU activation (the feed-forward design where silu(gate) multiplies an
"up" projection elementwise) for the merged-weights layout: one matmul produced
rows of width hidden*2 holding [gate | up] side by side. Each thread owns one
gate element, applies silu, multiplies by the up element sitting hidden columns
to its right, and writes the product back into the gate half in place — one
dispatch instead of separate silu and mul_inplace passes, with no copy to
separate the halves first.
""",
    ('voxtral_shaders.metal', 'decoder_ffn_gate'): """
The single-token (M=1) feed-forward front half as one matrix-vector kernel:
threadgroup `row` (one cooperating thread block per output channel) produces
out[row] = silu(x·w1[row]) * (x·w3[row]), reading both weight rows from the
merged buffer where w3's rows sit hidden rows below w1's. The threads stride
the dim-long dot products in vectorized float4/half4 chunks — half is the
16-bit float the weights are stored in, widened to f32 inside the dot — then
simd_sum folds each thread's partial across its 32-thread SIMD group (the
hardware's lockstep bundle, which can reduce in registers), per-group results
land in threadgroup scratch, and after a barrier (the all-arrive checkpoint)
thread 0 sums the groups, applies silu to the w1 dot, multiplies by the w3 dot,
and writes the single output. For one token this replaces an MPS matmul plus
separate silu and mul dispatches.
""",
    ('voxtral_shaders.metal', 'decoder_w2_residual'): """
The matching single-token back half: threadgroup `row` computes the
down-projection dot(gate[0:hidden], w2[row]) with the same cooperative pattern
— strided float4/half4 loads (half being the 16-bit weight storage, widened in
the dot), simd_sum across each 32-thread SIMD group, per-group partials parked
in threadgroup scratch, one barrier, thread 0 summing the groups — but it
finishes with x[row] += dot: the residual add (transformers update the hidden
state as x = x + f(x)) is folded into the same dispatch. x is the persistent
on-GPU hidden state g_dec_x, so the FFN completes without the vector ever
visiting the CPU.
""",
    ('voxtral_shaders.metal', 'decoder_wo_residual'): """
The same fused matvec-plus-residual shape applied to attention output:
threadgroup `row` computes dot(attn[0:q_dim], wo[row]) — projecting the
concatenated per-head attention results back to the model dimension — via
cooperative float4/half4 loads, simd_sum within each 32-thread SIMD group (the
lockstep bundle that reduces in registers), threadgroup scratch plus one
barrier, and a final sum by thread 0 that performs x[row] += dot. It is the
first kernel of the persistent-x decoder block: attention's contribution joins
the resident hidden state in a single dispatch, with no separate matmul and
add_inplace.
""",
    ('LocalCaptionServer.swift', '@1'): """
The four imports are the file's complete dependency list: `Darwin` exposes the
C system library (later used for `getifaddrs` interface walking), `Foundation`
supplies the value types `Data`, `Date`, and `URL` plus the JSON coders,
`Network` provides the `NWListener` and `NWConnection` state machines the whole
server is built on, and `Security` contributes `SecRandomCopyBytes` for minting
random tokens.
""",
    ('LocalCaptionServer.swift', 'struct RemoteCaptionSnapshot'): """
The wire payload pushed to the phone over the Server-Sent Events stream (the
long-lived one-way HTTP response described in the chapter intro): the finalized
caption lines, an optional still-changing provisional line, whether a capture
session is live, and a revision number that only rises. The names after the
colon are compiler-generated abilities: `Codable` derives JSON encoding and
decoding from the field list, `Equatable` supplies `==` for value comparison (used by
the tests; the publisher itself sends every snapshot unconditionally), and `Sendable` marks the immutable value
safe to hand between threads. Encoding it with `JSONEncoder` is the entire
serialization contract — there is no separate schema.
""",
    ('LocalCaptionServer.swift', 'enum LocalCaptionServerStatus'): """
The dashboard-facing lifecycle of caption sharing. A Swift enum case can carry
a payload (like a C tagged union), and here the `URL` payloads exist only on
the states reached after the listener is ready — the type itself makes "show a
pairing QR before an address exists" unrepresentable. `failed` carries
presentation text rather than a Network.framework error object, and because the
whole value is immutable and `Sendable`, it can leave the server queue without
exposing mutable listener state.
""",
    ('LocalCaptionServer.swift', 'enum StudentQuestionServerStatus'): """
Question intake has its own lifecycle because the professor can disable it
while the caption viewer stays live. Its ready URL embeds the independent
student capability (a capability is a secret token whose mere possession grants
access — here, access to the question form only), never the viewer token, so
the type separation mirrors the security separation: leaking one URL never
grants the other URL's powers.
""",
    ('LocalCaptionServer.swift', 'enum CaptionSharingSecurity'): """
A Swift enum with no cases cannot be instantiated, which makes it a pure
namespace — a header of tunable security constants kept in one auditable place.
It holds the 32-byte token size, an 8 KiB request cap, a 2 KiB / 500-character
question cap, 256 concurrent tickets (at most 4 per source) with a 4-hour life,
the layered rate-limit windows (10 s between questions per ticket, 8 per source
per 5 minutes, 30 globally per minute, 100 accepted per sliding hour), and a
10 s request-completion timeout. That timeout defeats the slowloris attack, in
which a client opens connections and feeds bytes one at a time, never finishing
a request, until every one of the 64 connection slots is occupied.
""",
    ('LocalCaptionServer.swift', 'makeToken'): """
Mints a 256-bit secret: it draws `tokenByteCount` random bytes from the system
CSPRNG (a cryptographically secure random generator whose output cannot be
predicted from earlier output) via `SecRandomCopyBytes`, then hex-encodes them
with `%02x` formatting. The attack this defeats is guessing: an attacker on the
classroom Wi-Fi who knows the URL shape still faces 2^256 equally likely
tokens, so brute-forcing the viewer, student, or ticket credential is hopeless.
If the random draw fails the function throws (raises a Swift error) instead of
falling back to a weaker source, so a caller can never proceed with a
predictable token.
""",
    ('LocalCaptionServer.swift', 'tokensMatch'): """
Compares a presented token with the expected one without leaking timing
information. A naive `strcmp`-style comparison returns at the first differing
byte, so an attacker timing responses could learn how many leading characters
were correct and recover the token one byte at a time, like feeling a lock's
pins. This version UTF-8-encodes both strings, rejects immediately on a length
mismatch (lengths are public anyway), then XORs every byte pair and ORs the
results into one accumulator that is zero only when all bytes match — the loop
always runs to the end, so every wrong guess takes the same time.
""",
    ('LocalCaptionServer.swift', 'normalizedQuestion'): """
Sanitizes untrusted student text before anyone sees it: split on whitespace and
newlines, drop the empty pieces, and rejoin with single spaces, then reject the
result if it is empty, longer than `maximumQuestionCharacters`, or contains any
Unicode control character (invisible codes such as escape or backspace that can
corrupt terminal output or spoof what a reader sees). Returning `nil` tells the
caller to answer `422 Unprocessable Content` — HTTP's numeric verdict for
"well-formed request, unacceptable content" — so control bytes and oversized
input never reach the professor's moderation queue or the model.
""",
    ('LocalCaptionServer.swift', 'struct StudentTicket'): """
The queue-confined record behind one issued ticket: the source the Mac observed
when issuing it, an absolute expiry, and that ticket's own accepted-submission
times. Tickets are never persisted or forwarded to the application model, so
nothing here can deanonymize a student after class. The same block declares the
ledgers the `CaptionSharingSecurity` limits are enforced against — per-ticket
dates live inside each ticket, while per-source, global, and accepted-question
dates are separate queue-owned tables — plus one `JSONEncoder` reused across
snapshot publishes.
""",
    ('LocalCaptionServer.swift', 'func start('): """
The public entry point only hops onto the server's serial queue: `queue.async`
submits a closure (a function value capturing `self` weakly, so a destroyed
server is silently skipped) to run later on that queue, where `startOnQueue`
does the real work — generating a fresh viewer capability (the student capability is minted separately when questions are enabled), creating
Wi-Fi-constrained TCP parameters, installing listener callbacks on the server
queue, and publishing URLs only after listener readiness and local-address
selection. The hop is what makes the no-locks design sound: mutable state is
touched only from the queue.
""",
    ('LocalCaptionServer.swift', 'publish'): """
Called by the app model for every new caption snapshot. On the server queue it
first records the value in `lastSnapshot` — the stored copy `beginEventStream`
replays so a phone that connects late is not blank — and then sends it to the
single live SSE stream, if one exists. SSE framing JSON-encodes the immutable
snapshot, prefixes the protocol's `event:` and `data:` fields, and ends the
event with a blank line; slow or failed connections are removed by the queue
owner rather than blocking the app model.
""",
    ('LocalCaptionServer.swift', 'func setQuestionSubmissionsEnabled('): """
Transfers one Boolean command from whatever thread the app model calls on
(typically the main UI thread) to the queue-owned implementation. Because the
flag flip, credential rotation, and ticket clearing all execute on the serial
queue, they cannot race an incoming question request being handled on that same
queue.
""",
    ('LocalCaptionServer.swift', 'receiveRequest'): """
The framing loop that turns TCP's raw byte stream into one whole HTTP request.
TCP guarantees byte order but knows nothing about message boundaries, so a
single receive callback may deliver half a header, a header plus part of a
body, or several lines at once; the function therefore appends each chunk (at
most 2,048 bytes per callback) to the `accumulated` buffer and re-arms itself
until enough has arrived. "Enough" means the four-byte header terminator
`CR LF CR LF` has appeared and the buffer holds at least the header plus the
body length declared by `Content-Length`. Every exit is bounded — more than
8 KiB total earns `431`, a declared body over 2 KiB earns `413`, a peer that
closes early earns `400` — so a hostile client cannot grow the buffer without
limit, and only a complete request ever reaches the router.
""",
    ('LocalCaptionServer.swift', 'handleRequest'): """
The router. It splits the HTTP request line — the message's first line, such as
`GET /events?token=abc HTTP/1.1`, holding method, target, and protocol
version — into three parts, parses the target's path and query with
`URLComponents`, lowercases the header names, and slices off the body. Student
routes get first claim; everything else must be a `GET` whose `token` query
value passes `tokensMatch` against the viewer capability before the path is
even examined. Wrong credentials and unknown routes deliberately receive the
same `404 Not Found`, denying a probing attacker the oracle that would separate
"route exists but my token is wrong" from "no such route". The viewer token
unlocks only the caption page and `/events`; it can never submit questions,
just as student credentials can never read captions.
""",
    ('LocalCaptionServer.swift', 'respondNotFound'): """
Funnels the student router's refusals — a wrong capability token on `/student`
or `/student-ticket`, or an unsupported method — into the byte-identical
`404 Not Found` that unknown paths receive. The attack this blunts is
enumeration: if a bad token earned a distinctive `401` while a missing route
earned `404`, an attacker sweeping guessed URLs could map which routes exist
and whether questions are enabled; one shared response shape removes that
signal.
""",
    ('LocalCaptionServer.swift', 'func respond('): """
Writes one complete HTTP/1.1 response and closes the connection.
`Content-Length` tells the browser exactly where the body ends,
`Connection: close` declares the one-request-per-connection policy, and
`Cache-Control: no-store` keeps token-bearing pages out of caches. Every reply
also carries defensive browser instructions: the `Content-Security-Policy`
forbids the page from loading scripts, styles, or images from anywhere else, so
even if hostile text reached a page it could not pull in attacker code;
`X-Content-Type-Options: nosniff` stops the browser from reinterpreting a
response as a different type than declared; and `X-Frame-Options: DENY` (with
`frame-ancestors 'none'`) blocks embedding the page inside another site's frame
to trick taps. The send-completion callback then frees the connection's
tracking slots.
""",
    ('LocalCaptionServer.swift', 'studentQuestionPage'): r"""
Returns the entire student client — HTML structure, CSS styling, and JavaScript
behavior — as one Swift multiline string, with the student capability spliced
in by `\(token)` interpolation; that is safe only because `makeToken` emits
pure hex characters, which cannot break out of the JavaScript string literal.
For a non-web reader: `fetch` is the browser function a page's script uses to
issue its own HTTP requests. On load the script POSTs to `/student-ticket`,
exchanging the page capability for a short-lived ticket, and only then enables
the submit button; submitting POSTs the question as JSON to
`/questions?ticket=...` and maps the status code to a message — `202` clears
the box, `429` asks the student to wait. No route reachable from this page
exposes captions, microphone, overlay, or model control.
""",
    ('LocalCaptionServer.swift', 'browserPage'): """
Returns the read-only caption viewer page. Its script uses `EventSource`, the
browser object implementing the client half of Server-Sent Events: it opens one
long-lived HTTP request to `/events?token=...`, fires a callback for each
`event: captions` record the Mac pushes, and reconnects on its own (honoring
the server's one-second `retry` hint) when the connection drops. Each callback
parses the JSON snapshot and rebuilds the caption list from scratch — simpler
than diffing and harmless at caption sizes. Every line is inserted through
`textContent`, which treats the string as plain characters rather than HTML
markup, so caption text could not inject script even if it contained tags; a
final `scrollTop` assignment keeps the newest line visible. The embedded page
and the Swift routes form one protocol implementation that evolves together.
""",
    ('AudioLevelMeterTests.swift', '@1'): """
The imports bring in `ClassroomCaptionsCore` (the production module providing
`PCM16LevelMeter`), Foundation for the `Data` byte buffer, and XCTest, Apple's
unit-test framework.
""",
    ('AudioLevelMeterTests.swift', 'class AudioLevelMeterTests'): """
Specification for `PCM16LevelMeter`, the pure function that turns raw microphone
bytes into the level reading behind the app's microphone indicator. The three
tests pin the math at silence, at full scale, and on malformed input — if any of
them drifted, the professor could no longer trust the meter that tells him
whether the microphone is actually picking up his voice.
""",
    ('AudioLevelMeterTests.swift', 'testSilenceProducesZeroLevel'): """
Pins that all-zero PCM produces exactly zero RMS (root-mean-square, the standard
average-loudness measure), zero peak, and a zero normalized level — not a small
floor value or NaN (the floating-point "not a number" that invalid math such as
0/0 yields). A silent room must show a dead-flat meter; any residual reading
would falsely suggest the microphone is live. `XCTAssertEqual` records a failure
when its two arguments differ but lets the test continue, so all three fields
are checked in one run.
""",
    ('AudioLevelMeterTests.swift', 'testPeakAndRMSUseNormalizedPCMValues'): """
Feeds the most extreme samples — plus and minus `Int16.max` alternating with
zeros — and pins the normalized statistics: peak exactly 1 and RMS √0.5, the
analytic value for a full-scale signal active half the time. This proves the
meter divides by the 16-bit full-scale value before computing statistics, so its
readings live on a fixed 0-to-1 scale; the `accuracy:` parameter turns the
assertion into a tolerance comparison, the correct way to compare floating-point
results.
""",
    ('AudioLevelMeterTests.swift', 'testOddTrailingByteIsIgnored'): """
Appends a single stray byte after one complete sample and pins that measurement
still reports full peak. PCM16 audio arrives over byte pipes, so a chunk
boundary can split a 16-bit sample in half; the meter must treat the dangling
half-sample as data that has not arrived yet, because trapping or misreading it
would crash or corrupt the level display mid-lecture.
""",
    ('AudioLevelMeterTests.swift', 'func pcmData'): """
Fixture helper that reinterprets an `Int16` array as raw bytes — the Swift
equivalent of casting an `int16_t*` to `char*` — producing exactly the byte
layout the meter consumes. `withUnsafeBytes` briefly exposes the array's memory
as an untyped byte view, and `Data` copies it before that view becomes invalid.
""",
    ('CVoxtralBridgeTests.swift', '@1'): """
Imports `CVoxtralEngine`, the C target whose header declares the `ccv_*` engine
API, plus XCTest; Swift imports C headers directly, so the tests call the C
functions without any wrapper.
""",
    ('CVoxtralBridgeTests.swift', 'class CVoxtralBridgeTests'): """
Exercises the embedded recognizer's stable C ABI from Swift without ever loading
a real model: the option defaults, a structured load failure, and the pinned
upstream revision. These are the calls the app performs before any audio flows,
so they must behave deterministically even on a machine with no model files
installed — which is also what lets this suite run anywhere.
""",
    ('CVoxtralBridgeTests.swift', 'testDefaultOptionsAreSuitableForRealtimeCaptions'): """
Pins the defaults baked into `ccv_stream_options_default()`: a 320 ms delay, a
1.0 s processing interval, continuous mode on, and a 2000-token decode-context
cap — the realtime captioning baseline. The app builds its streaming session
from these defaults, so a silent change in the C layer would shift caption
latency or memory use without any Swift code changing; this test turns such a
drift into a visible failure.
""",
    ('CVoxtralBridgeTests.swift', 'testPinnedRevisionIsExposed'): """
Pins that `ccv_upstream_revision()` returns the exact git commit hash of the
upstream Voxtral sources the engine was built from; `String(cString:)` converts
the NUL-terminated C string into a Swift string for comparison. Recording the
precise revision keeps benchmarks and bug reports reproducible: changing the
vendored sources forces a deliberate update of this constant.
""",
    ('CaptionCorrectionValidatorTests.swift', '@1'): """
Imports `ClassroomCaptionsCore` for `CaptionCorrectionValidator` and its error
type, and XCTest for the test runner and assertions.
""",
    ('CaptionCorrectionValidatorTests.swift', 'class CaptionCorrectionValidatorTests'): """
Executable policy for the correction stage: conservative proofreading and
notation rendering are accepted; answers, control markup, translation, and
wholesale rewrites are rejected. The corrector is a language model, and a
language model will sometimes treat a caption as a prompt to be answered — this
validator and its tests are the wall that keeps such output off the classroom
screen.
""",
    ('CaptionCorrectionValidatorTests.swift', 'testAcceptsConservativeFrenchCorrection'): """
Pins the happy path: fixing the agreement and plural slips in "la section
critiques" and "les deux thread" passes validation, and the corrected sentence
comes back verbatim. An accepted baseline matters as much as the rejections
below — a validator that rejected everything would technically be safe and
completely useless, leaving the professor with raw recognizer text forever.
""",
    ('CaptionCorrectionValidatorTests.swift', 'testAcceptsSpokenComplexityAndEqualityNotation'): """
Pins that dictated mathematics — "O de n est égal à un" — may be rendered as the
compact notation "O(n) = 1". In an algorithms lecture formulas are spoken
constantly; if the validator scored this rewrite as excessive, every formula
would bounce back to its clumsy spoken transcription on the overlay.
""",
    ('CaptionCorrectionValidatorTests.swift', 'testAcceptsTechnicalNotationInsideQuestion'): """
Pins the point where two rules meet: notation may be normalized to "O(n) ≤
O(n²)" inside a sentence that is, and must remain, a question. Neither rule may
veto the other — rejecting the notation would degrade math captions, while
"completing" the question would put words in the professor's mouth.
""",
    ('CaptionCorrectionValidatorTests.swift', 'testAcceptsDenseUnicodeMathLogicAndCodeRendering'): """
Stress case for the rewrite budget: one long spoken paragraph of quantifiers,
set membership, a summation, conditional probability, and array-indexing code is
rendered as dense Unicode notation (∀, ℝ, Σ, P(A|B), tableau[i]) and must pass
unchanged, even under the default validation mode. Nearly every character
differs from the raw transcript here, so this pins that recognized notation
renderings are budgeted differently from arbitrary rewrites such as the
translation rejected further down.
""",
    ('CaptionCorrectionValidatorTests.swift', 'testScienceModeAcceptsCompactSetMembership'): """
Pins the canonical science-mode rendering: "n appartient à l'ensemble des
entiers naturels" becomes "n ∈ ℕ". The `mode: .science` argument selects the
validation profile with the looser symbol budget, and the test pins that under
it the compact candidate is returned exactly as proposed, so set-theory lectures
get real notation instead of spelled-out phrases.
""",
    ('CaptionCorrectionValidatorTests.swift', 'testRejectsAnswerAppendedToQuestion'): """
Pins the most dangerous corrector failure: keeping the professor's question but
helpfully appending the answer ("... ? Parce que son accès moyen est en O(1).").
Students must see what was asked, not the model's solution, so validation throws
`questionWasAnswered` and the raw caption stays. `XCTAssertThrowsError` asserts
that the call throws and passes the thrown error to a closure (a function value)
so the test can pin exactly which error occurred.
""",
    ('CaptionCorrectionValidatorTests.swift', 'testRejectsTranslationOrUnrelatedRewrite'): """
Pins the defense against the corrector replacing the French sentence with an
English translation — text whose meaning may be related but whose characters
share almost nothing with what was said. The validator's edit-distance check
(counting the whole-word insertions, deletions, and substitutions needed to
turn one sentence into the other) rejects it as `excessiveRewrite`, so captions can never silently switch language
or topic mid-lecture.
""",
    ('CaptionOverlayGeometryTests.swift', '@1'): """
Imports AppKit for `NSRect`, XCTest, and the app module via `@testable import`,
which compiles the test with access to the module's internal (non-public)
declarations such as `CaptionOverlayController`.
""",
    ('CaptionOverlayGeometryTests.swift', 'class CaptionOverlayGeometryTests'): """
Pure geometry specification for `CaptionOverlayController.clamped`, the function
that forces any proposed overlay frame back inside the visible display. The
`@MainActor` attribute runs the tests on the main thread because the controller
type is bound to it, but no window is ever created, so the suite stays fast and
headless. For a hard-of-hearing professor the overlay is the lecture: a frame
that escapes the screen means losing every caption until the window is hunted
down.
""",
    ('CaptionOverlayGeometryTests.swift', 'testClampShrinksFrameThatExceedsDisplay'): """
Pins that an overlay larger than the screen is shrunk to the visible area minus
the fixed 12-point margin: on an 800 by 576 visible rectangle starting at
y = 24, the result is 776 by 552 anchored at (12, 36). Without shrinking, the
edges of an oversized window — including the resize handles needed to fix it —
would sit beyond the screen where the mouse cannot reach.
""",
    ('CaptionTimelineTests.swift', '@1'): """
Imports `ClassroomCaptionsCore`, where `CaptionTimeline` lives, and XCTest.
""",
    ('CaptionTimelineTests.swift', 'class CaptionTimelineTests'): """
Specification for `CaptionTimeline`, the value type that owns the ordered
caption record: live provisional replacement, finalized segment identity, and
what happens to a segment when its correction succeeds or fails. Everything
students see and everything the archive stores flows through this structure, so
its invariants are pinned here in isolation, with no audio or UI involved.
""",
    ('CaptionTimelineTests.swift', 'testSequenceRemainsMonotonicAfterProvisionalUpdates'): """
Pins that provisional revisions — the live guesses the recognizer rewrites as a
sentence completes — consume no sequence numbers; only finalized captions
advance the count, so the two finalized segments here are numbered 0 and 1 with
no gap despite the extra drafts. A dense, monotonic sequence is what lets the
export and remote viewers order segments reliably no matter how many revisions
each one went through.
""",
    ('CaptionTransformationTests.swift', '@1'): """
Imports `ClassroomCaptionsCore` for `CaptionTransformation` and XCTest for the
assertions.
""",
    ('CaptionTransformationTests.swift', 'class CaptionTransformationTests'): """
Specification for `CaptionTransformation.percentage`, the diagnostic figure that
tells the professor how much the corrector changed a caption (0 means untouched,
100 means completely replaced). Three points — both extremes plus one interior
value — are enough to pin the formula: edit distance divided by the longer
string's length.
""",
    ('CaptionTransformationTests.swift', 'testIdenticalCaptionHasZeroPercentTransformation'): """
Pins the identity anchor: a caption the corrector did not touch scores exactly
0 percent, not a tiny floating-point residue. Any nonzero score on unchanged
text would destroy the metric's value as a quick "did the model alter my
words?" signal in the diagnostics.
""",
    ('CaptionTransformationTests.swift', 'testCompletelyDifferentSameLengthCaptionHasFullTransformation'): """
Pins the opposite anchor: substituting every character of an equal-length string
scores exactly 100 percent. Together with the zero case this fixes the metric's
scale, so a mid-range reading keeps a stable meaning from one session to the
next.
""",
    ('ClassroomSessionTests.swift', '@1'): """
Imports `ClassroomCaptionsCore` for the `ClassroomSession` value type and
XCTest.
""",
    ('ClassroomSessionTests.swift', 'class ClassroomSessionTests'): """
Specification for `ClassroomSession`: which transitions of its phase machine
(starting, listening, paused, stopping, idle) are legal, and in which phases a
caption may enter the timeline. The session is a plain value type, so each test
creates one with `var` and drives transitions directly — no audio hardware, no
clock, no UI.
""",
    ('ClassroomSessionTests.swift', 'testCaptionsAreAcceptedOnlyWhileListening'): """
Pins the gate on `finalizeCaption`: before `markListening` and after `pause` it
returns nil and records nothing, leaving only the caption spoken while listening
in the timeline. Pause must really mean pause — words spoken during a break or a
private aside must never reach the classroom screen or the archived transcript.
""",
    ('LocalCaptionServerTests.swift', '@1'): """
Uses `@testable import` to reach the app's internal server types
(`LocalCaptionServer`, `CaptionSharingSecurity`), Network for `NWEndpoint.Port`
when pinning test ports, and XCTest.
""",
    ('LocalCaptionServerTests.swift', 'class LocalCaptionServerTests'): """
Integration tests for the caption-sharing HTTP server, run against a real
listener that the test process talks to over the machine's own network
(loopback-style: the test is both server and client, so nothing leaves the Mac).
They pin token entropy, exact-match authentication, the read-only shape of
viewer data, student-question tickets, and per-source rate limits — the entire
security story for putting captions on classroom Wi-Fi.
""",
    ('LocalCaptionServerTests.swift', 'testPairingTokenHasExpectedEntropyAndEncoding'): """
Pins the pairing token's strength and shape: 32 random bytes — 256 bits of
entropy, far beyond guessing range — rendered as exactly 64 hexadecimal
characters, with two consecutive tokens never equal. This token is the only
secret protecting the caption stream on shared Wi-Fi, so its size and encoding
are pinned rather than assumed.
""",
    ('LocalCaptionServerTests.swift', 'testServerRequiresTheGeneratedPairingToken'): """
Starts the real server on a fixed test port and pins authentication at the HTTP
level: a URL carrying a wrong token receives 404 — the page simply does not
exist for unauthenticated callers, revealing nothing — while the published
pairing URL receives 200 and the caption page. The test is `async` (it can
`await` network replies); when the machine has no active Wi-Fi listener it
throws `XCTSkip`, which marks the test skipped rather than failed, and the
`defer` block stops the server even when an assertion fails early.
""",
    ('LocalCaptionServerTests.swift', 'testTicketIssuanceIsCappedPerSource'): """
Pins the per-source ticket cap: posting to `/student-ticket` succeeds with 200
exactly `CaptionSharingSecurity.maximumTicketsPerSource` times, and the next
request from the same source is refused with 429 ("too many requests"). Without
the cap, one student device looping the ticket route could exhaust the global
ticket table and lock the whole class out of asking questions — a one-phone
denial of service. Like the other server tests it is an `async` test against a
real listener and throws `XCTSkip` (skipped, not failed) when no Wi-Fi listener
is available.
""",
    ('LocalCaptionServerTests.swift', 'func readyURL'): """
Awaits the server's status stream until it reports `.ready` with the published
URL, racing that against a second task that just sleeps for the timeout:
whichever child of the task group finishes first wins, and `cancelAll()` stops
the loser. Returning nil on `.failed` or timeout is what lets callers skip
cleanly instead of hanging the whole suite on a server that never comes up.
""",
    ('LocalCaptionServerTests.swift', 'func studentURL'): """
The same race-against-timeout pattern for the student-question status stream: it
resolves to the independently generated student capability URL once the server
publishes it, ignores `.stopped`, and yields nil after the timeout. The student
URL is a separate secret from the viewer URL, so the tests must obtain it from
this second stream rather than derive it.
""",
    ('LocalCaptionServerTests.swift', 'func nextSubmission'): """
Bridges the server's accepted-question callback into one awaited value: a task
group races the first element of the submission stream against a sleeping
timeout task, so the test can assert on the exact text the Mac-side handler
received without ever risking an unbounded wait.
""",
    ('ProcessMemoryTests.swift', '@1'): """
Imports the app module with `@testable` for the internal `ProcessMemory` helper,
Darwin — the C/Unix layer of macOS — for `getpid`, and XCTest.
""",
    ('ProcessMemoryTests.swift', 'class ProcessMemoryTests'): """
Boundary test for `ProcessMemory`, the wrapper over Darwin that reports a
process's resident memory — the bytes it actually holds in RAM. The app polls
this number so the professor can see what the loaded models cost, which makes
"the query works on this machine" worth one executable check.
""",
    ('ProcessMemoryTests.swift', 'testReadsCurrentProcessResidentMemory'): """
Pins that sampling the test process itself — identified with the familiar Unix
`getpid()` — yields a value that is present and strictly positive, since a
running process cannot occupy zero bytes. If the underlying system query broke
or its result were misread, the memory figure would silently show blank or zero
and stop warning that the models are outgrowing the machine.
""",
    ('SessionExportTests.swift', '@1'): """
Imports both production modules — the app module via `@testable` for the archive
service, and `ClassroomCaptionsCore` for sessions and the WAV header — plus
XCTest.
""",
    ('SessionExportTests.swift', 'class SessionExportTests'): """
Specification for everything a session leaves on disk: the WAV header bytes,
transcripts with timestamps relative to session start, the final-drain exception
while stopping, and the archive directory contents. The archive is the
professor's durable record of what students were shown, so the formats are
pinned byte-for-byte rather than trusted to stay compatible.
""",
    ('SessionExportTests.swift', 'testFinalDrainCaptionIsAcceptedWhileStopping'): """
Pins the intentional exception to the listening-only rule: a caption finalized
while the session is already `stopping` is still appended to the timeline. The
recognizer always has a short tail of audio in flight, so the professor's last
sentence finishes decoding after he clicks stop — without this carve-out the
closing words of every lecture would vanish from both the screen and the
transcript.
""",
    ('SessionExportTests.swift', 'testWAVHeaderHandlesMaximumRIFFSize'): """
Pins the header builder at the format's hard ceiling: the RIFF chunk-size field
stores `dataByteCount + 36`, so the largest legal payload is `UInt32.max - 36`
bytes, and the test checks that the field then reads back exactly `UInt32.max`.
Unlike C, Swift traps (deliberately crashes) on unsigned overflow instead of
wrapping, so an unchecked addition one byte past this limit would abort the app
while it was saving a lecture; `loadUnaligned` reads the little-endian 32-bit
field straight from the raw bytes without requiring aligned storage.
""",
    ('SpokenOverlayCommandTests.swift', '@1'): """
Imports `ClassroomCaptionsCore`, home of `SpokenOverlayCommandRecognizer` and
`SpokenOverlayCommand`, and XCTest.
""",
    ('SpokenOverlayCommandTests.swift', 'class SpokenOverlayCommandTests'): """
Dense specification for `SpokenOverlayCommandRecognizer`, the matcher that lets
the professor drive the overlay by voice: exact phrases, tolerant variants,
partial-phrase suppression, several commands per transcript, and preservation of
the surrounding lecture text. Both failure directions are costly in class — a
missed command takes away hands-free control, and a false trigger hides the
captions students are reading.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesFixedShowAndHidePhrases'): """
Pins the basic contract: the configured show phrase yields a `.show` command and
the hide phrase a `.hide`, each with empty `remainingText` because the sentence
contained nothing but the command. The recognizer is a pure function — text in,
optional `SpokenOverlayCommand` out — which is why this whole suite runs without
audio or UI.
""",
    ('SpokenOverlayCommandTests.swift', 'testFixedPhraseDoesNotConfuseOrdinaryActionWords'): """
Pins that a sentence containing "affiche" and "masque" — words a CS professor
describing UI code says constantly — produces no command, asserted with
`XCTAssertNil` (fails if the value is non-nil). A false trigger on ordinary
action vocabulary would blank the captions in front of the class merely for
explaining what a function does.
""",
    ('SpokenOverlayCommandTests.swift', 'testDetectsPartialFixedPhrase'): """
Pins `isPotentialCommand` on a bare "Sésame": provisional captions are shown
live while the model is still finishing the sentence, so a visible prefix that
could still grow into a command phrase must be held back from display. Otherwise
students would watch half a magic phrase appear and vanish every time the
professor controls the overlay.
""",
    ('SpokenOverlayCommandTests.swift', 'testDetectsPartialSecondWordWithoutDisplayingIt'): """
Extends suppression into the middle of the second trigger word: "Sésame rou" and
"Sésame lum" could each still complete into a configured phrase, so both must
stay flagged as potential commands. This is the pin that keeps command fragments
from ever flashing on the classroom screen mid-recognition.
""",
    ('SpokenOverlayCommandTests.swift', 'testDoesNotSuppressUnrelatedSecondWord'): """
Pins the opposite edge: "Sésame logique" shares the first trigger word, but its
second word can no longer become either configured phrase, so it must flow
through as ordinary lecture text. Over-eager suppression would be its own bug,
holding real sentences off the screen on the mere suspicion of being commands.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesMultipleCommandsInSpokenOrder'): """
Pins that when one transcript contains several command phrases, `recognizeAll`
returns them in the order they were said — hide, show, hide — not in whatever
order the matchers happened to run. The overlay must replay the professor's
intent sequentially; reordering would leave it in the opposite visibility state
from the one he asked for.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesShowHideAndClearCommandsInSpokenOrder'): """
Repeats the ordering pin across the full action set by adding a configured clear
phrase: hide, clear, show come back exactly as spoken, and the final
`remainingText` is empty because the transcript held nothing but commands.
Spoken order must survive however many distinct actions are configured.
""",
    ('SpokenOverlayCommandTests.swift', 'testClearCommandRetainsAdjacentLectureText'): """
Pins that a clear command spoken at the end of a sentence is consumed while the
sentence before it — "La preuve est terminée." — returns as `remainingText`. It
is natural to chain a wrap-up sentence with the command that wipes the overlay,
and the wrap-up itself must still reach the captions.
""",
    ('SpokenOverlayCommandTests.swift', 'testDetectsPartialClearCommand'): """
Pins provisional holdback for the clear phrase as well: "Bonjour soleil bla"
could still become "Bonjour soleil blanc", so it is flagged as a potential
command and kept off the live caption line. Every configurable action phrase
needs its own suppression coverage, because each is matched independently.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesNextStudentQuestionCommand'): """
Pins the spoken command that pops the next anonymous student question onto the
overlay, configured as its own phrase and consumed entirely (empty
`remainingText`). Voice control matters doubly here: the professor is
mid-lecture and away from the keyboard, and the question queue is how a
hard-of-hearing lecturer keeps the class interactive.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesDismissStudentQuestionCommand'): """
Pins the companion command that dismisses the currently displayed question,
configured as a phrase distinct from "next question". Separate phrases for
separate queue operations mean a recognition near-miss can at worst do nothing —
it cannot perform the wrong operation on a student's question in front of
everyone.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesObservedCesAmesLumiereVariant'): """
Pins tolerance for a transcription Voxtral actually produced in testing: "Ces
âmes lumières", a near-homophone of the spoken "Sésame lumière", must still
recognize as `.show`. Field-observed variants get their own pins so a recognizer
refactor can never quietly reintroduce the failure where the professor says the
magic phrase and nothing happens.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesHyphenatedShowCommand'): """
Pins punctuation normalization in the trigger: the configured "Gloubi boulga"
matches the transcribed hyphenated "Gloubi-boulga,". This test also introduces
the recognizer's second form — a configurable trigger phrase followed by a
spoken action word ("affiche" for show) — instead of one fixed phrase per
action.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesAccentsAndHideSynonym'): """
Pins two tolerances at once: the configured phrase is unaccented ("Ecoute")
while the transcript carries the accent ("Écoute"), and "cache" is accepted as a
synonym action word for hiding. Accent and synonym drift are everyday behavior
for French speech recognition; without these allowances the professor would be
fighting the recognizer's spelling to control his own overlay.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesTolerantSingularAndAgreementVariant'): """
Pins bounded grammatical tolerance: "Oreille compensé" — singular, with
mismatched agreement — still matches the configured "Oreilles compensées". In
spoken French these endings are silent, so the recognizer cannot hear the
difference; the tolerance stays enumerated and narrow, though, never a license
for arbitrary fuzzy matching.
""",
    ('SpokenOverlayCommandTests.swift', 'testRecognizesOneCharacterTranscriptionError'): """
Pins the edit-distance budget on trigger words: "Oreiles", one letter short of
"Oreilles", still matches, and the action word "masque" yields `.hide`. A
routine one-character transcription slip must not cost the professor control of
the overlay; the rejection test below pins the ceiling, so together they bracket
exactly how much error is forgiven.
""",
    ('SpokenOverlayCommandTests.swift', 'testRetainsLectureTextFromSameSegment'): """
Pins that lecture text spoken before a trigger-plus-action command survives: the
command is excised and "La preuve est terminée." comes back as `remainingText`.
Losing neighboring words every time a command is spoken would punch silent holes
into the captions and the transcript students rely on.
""",
    ('SpokenOverlayCommandTests.swift', 'testRetainsTextAfterCommand'): """
Pins the mirror case: words spoken after the command survive as `remainingText`.
Together with the preceding test, the recognizer is pinned to remove exactly the
command and nothing else, whichever side of it the lecture content falls on.
""",
    ('SpokenOverlayCommandTests.swift', 'testOverlappingPhrasesPreferTheLongestWithoutCrashing'): """
Regression pin for a real crash: with one configured phrase a token-prefix of
another ("Bonjour soleil" versus "Bonjour soleil blanc"), the matchers used to
produce overlapping match ranges, and removing both trapped on invalidated
string indices — a Swift runtime trap aborts the process, so the captioning app
died mid-lecture. The test pins the fix: the longest match wins, and the spoken
clear phrase yields exactly one `.clear` command.
""",
    ('SpokenOverlayCommandTests.swift', 'testIdenticalConfiguredPhrasesYieldOneCommandWithoutCrashing'): """
Companion regression pin: the settings UI does not stop the professor from
assigning the same phrase to two different commands, and previously both
matchers claimed the same text range, whose double removal crashed. The test
pins the de-duplication — one spoken sentence yields exactly one command — so a
small configuration slip can no longer take down captioning in class.
""",
    ('VoxtralProtocolTests.swift', '@1'): """
Imports XCTest and the app module via `@testable` so the test can call
`VoxtralRealtimeService`'s internal `findString` helper directly.
""",
    ('VoxtralProtocolTests.swift', 'class VoxtralProtocolTests'): """
Pure parser tests for `VoxtralRealtimeService.findString`, the tolerant
extractor that digs transcript text out of whatever JSON shape a remote Voxtral
server emits. Different server builds wrap the text differently, and a parsing
miss does not raise an error — it silently produces no caption — so the search
rules are pinned here without any network involved.
""",
    ('VoxtralProtocolTests.swift', 'testFindStringUsesRequestedKeyPriority'): """
Pins the search order: at each dictionary level every requested key is tried
before the search descends into nested values. Here "delta" exists only one
level down while "text" sits at the top, so the top-level "fallback" wins over
the nested "preferred" — a shallow match beats a deeper one regardless of the
key list's order. Pinning this keeps extraction deterministic when a server
message happens to contain several plausible text fields.
""",
    ('VoxtralProtocolTests.swift', 'testNestedTranscriptIsFound'): """
Pins that the search recurses through both dictionaries and arrays, retrieving
"nested transcript" from `response.items[0].transcript`. Remote APIs tend to
nest their results deeper over time; if recursion broke, the connection would
look healthy while every caption silently vanished — the worst possible failure
for someone depending on the words.
""",
    ('Package.swift', '@1'): """
The whole file is one `Package(...)` call that Swift Package Manager compiles
and runs to learn the build graph; the `// swift-tools-version: 6.2` comment on
line 1 is mandatory and pins which manifest dialect SPM applies. Each entry in
`targets` is a compilation unit (one source directory built into one module):
`CVoxtralEngine` holds the C/Objective-C engine and so carries the C-only knobs
— `.define` adds `-D` preprocessor macros, `.unsafeFlags` passes `-O3
-march=native` to the C compiler verbatim, and each `.linkedFramework` plays
the role of a `-l` linker argument, naming the Apple system library to link
(Accelerate for BLAS, the Metal trio for the GPU). Each entry in `products` is
what a consumer can ask SPM to build or link against: the GUI executable, the
benchmark executable, and the importable core library. The `dependencies`
arrays replace hand-written Makefile rules — SPM derives compile order and
link lines from them — and the test target depends on all three modules so the
tests can exercise each layer directly.
""",
    ('Info.plist', '@1'): """
`Info.plist` is the bundle's identity card: macOS reads this XML dictionary,
not the executable, to learn what the application is and what it may request.
The `CFBundle*` keys supply the launcher's facts — executable name, the
reverse-DNS identifier `org.classroomcaptions.app` (the unique name macOS files
permissions and preferences under), display name, version strings, and package
type `APPL`, meaning "application". `LSMinimumSystemVersion` lets the system
refuse to launch on macOS older than 15, and `NSHighResolutionCapable` opts
into native Retina rendering instead of pixel-doubled scaling. The last three
keys are security declarations: macOS shows the microphone and local-network
strings verbatim in its permission dialogs and denies those capabilities
outright when the key is absent, and `NSBonjourServices` names the one Bonjour
(Apple's local-network service discovery) service type, `_classcaptions._tcp`,
the app uses to be found by the paired phone.
""",
    ('download_voxtral_model.py', '@1'): """
Every import is Python standard library — `urllib.request` for HTTP,
`hashlib` for SHA-256, and `argparse`/`json`/`os`/`time`/`pathlib` for
plumbing — so the downloader runs on stock Python 3 with nothing to install.
The two module constants pin what a valid installation means: `REPOSITORY`
names the Hugging Face repository (huggingface.co hosts model files in
git-like repositories), and `FILES` lists the three required artifacts — the
weights (`consolidated.safetensors`), the tokenizer data (`tekken.json`), and
the architecture parameters (`params.json`).
""",
    ('benchmark_voxtral.sh', '@1'): """
A thin launcher that turns environment variables into benchmark flags.
`set -euo pipefail` makes bash abort on any failed command, unset variable, or
failure inside a pipeline, and `ROOT_DIR` resolves the repository root from
the script's own location so the script works from any directory. The
`${VAR:-default}` expansions let `VOXTRAL_MODEL_DIR`, `VOXTRAL_DELAY_MS`,
`VOXTRAL_PROCESSING_INTERVAL`, and `VOXTRAL_CHUNK_MS` override the model path
and timing knobs without editing the file, while `ARGS=(...)` with
`"${ARGS[@]}"` is bash's array idiom for building an argument list that
survives embedded spaces (the default model path contains one); a second
positional argument adds an optional reference transcript. The closing
`swift run -c release VoxtralBenchmark` compiles the benchmark in release
mode if needed and runs it — SPM's equivalent of `make && ./bench`.
""",
    ('package_app.sh', '@1'): """
The bridge from SPM's bare executable to the `.app` directory bundle macOS
expects. It first builds the requested configuration (release by default),
then assembles the bundle by hand: `rm -rf` clears any stale previous bundle,
`Contents/MacOS/` receives the executable, `Contents/Info.plist` the property
list, and `Contents/Resources/` is created for the conventional layout. The
final `codesign --force --deep --sign -` applies an ad-hoc signature (`-`
means sign with no developer certificate, just checksums of the bundle's
contents) — enough for the machine that built it to launch the app and for
macOS to associate its permission grants with stable code, but not enough to
distribute to other Macs. Echoing the bundle path lets calling tooling pick
up the result.
""",
    ('build_book.sh', '@1'): """
The book's entire build in three commands, run from the repository root; the
`CDPATH=` prefix neutralizes the shell's `cd` search-path feature so the
`pwd` capture is clean wherever the script is invoked from.
`generate_source_book.py` regenerates every `docs/generated/*.qmd` chapter
from the real sources — including the byte-for-byte reconstruction check this
chapter's introduction describes — `generate_domain_chapter.py` rebuilds the
domain chapter, and only then does `quarto render docs` turn the Markdown
into the HTML and PDF book. Plain `/bin/sh` with `set -eu` suffices because
there are no pipelines: any failed step or unset variable stops the build
instead of publishing a stale book.
""",
    ('download_voxtral_model.py', 'def download'): """
Downloads one artifact through an adjacent `.partial` file so an interrupted
multi-gigabyte transfer resumes instead of starting over. Existing bytes
produce an HTTP Range request (a standard header asking the server to send
only the bytes from a given offset onward); the server confirms with a
`Content-Range` reply header, and if that confirmation is absent the function
restarts safely in write mode from byte zero rather than appending to a file
the server is resending from the start. Eight-MiB chunks bound memory while
feeding the live progress line, and the final `os.replace` is an atomic
rename: the real filename only ever names a complete file, which is exactly
the existing-and-non-empty test `main` relies on to skip finished downloads.
""",
    # === Assistant mode: spoken questions to the model + rich answer overlay ===
    ("ModelAnswerWebView.swift", "enum AnswerScrollDirection"): """
A two-value direction carried from the spoken scroll commands down to the answer
web view. Modeling it as an enum rather than a bool keeps call sites readable and
lets the view turn each case into a positive or negative pixel delta.
""",
    ("ModelAnswerWebView.swift", "class AnswerAssetSchemeHandler"): """
Serves the bundled rendering libraries (KaTeX, highlight.js, markdown-it, plus
our `render.js`/`overlay.css` and the math fonts) to the answer page over a
private `ccassets://` URL scheme. Because it only ever opens files inside the
bundled `RenderAssets` directory, the page can load our code while its
Content-Security-Policy still forbids every network origin: the answer can be
styled but can reach nothing on the machine or the network.
""",
    ("ModelAnswerWebView.swift", "override init"): """
Resolves the `RenderAssets` directory once from `Bundle.module` — the resource
bundle SwiftPM builds for this target. `resourceURL` is optional (a bundle need
not carry resources), so it is kept as `URL?` and every request re-checks it.
""",
    ("ModelAnswerWebView.swift", "start task"): """
WebKit calls this for every `ccassets://` sub-resource the page requests. It
resolves the path inside `RenderAssets` and refuses anything whose standardized
path escapes that directory (a `..` traversal), so the scheme cannot read
arbitrary files. On success it returns the bytes with a MIME type; any failure
fails the task.
""",
    ("ModelAnswerWebView.swift", "stop task"): """
WebKit calls this if a request is cancelled. The handler reads small local files
synchronously and has nothing to unwind, so the body is intentionally empty.
""",
    ("ModelAnswerWebView.swift", "func mimeType"): """
Maps a file extension to the MIME type WebKit needs to interpret each asset
(stylesheet, script, JSON, font). An unknown extension falls back to a generic
binary type rather than guessing.
""",
    ("ModelAnswerWebView.swift", "enum ModelAnswerRenderer"): """
A namespace — an enum with no cases is Swift's idiom for a bag of static helpers
— that builds the self-contained HTML page wrapping one Markdown answer.
""",
    ("ModelAnswerWebView.swift", "func html"): """
Assembles the page. The Markdown is embedded as JSON inside a non-executable
`<script type="application/json">` block, and `<`, `>`, `&` are escaped to
`\\uXXXX` so a literal `</script>` in the answer can never close that block
early — nothing the model wrote can become live markup. The strict CSP allows
only our `ccassets:` assets and forbids all network access; the injected
`font-size` rule applies the professor's chosen answer text size.
""",
    ("ModelAnswerWebView.swift", "struct ModelAnswerView"): """
A SwiftUI wrapper around an AppKit `WKWebView`; `NSViewRepresentable` is the
bridge between SwiftUI's value-type views and AppKit's reference-type views. It
holds no logic of its own — it builds the locked-down web view, reloads it when
the answer or font size changes, and forwards scroll commands.
""",
    ("ModelAnswerWebView.swift", "func makeCoordinator"): """
Creates the Coordinator, the long-lived reference object that survives SwiftUI's
repeated recreation of the value-type view and holds the web view plus the
last-rendered state.
""",
    ("ModelAnswerWebView.swift", "func makeNSView"): """
Builds the web view once: registers the asset scheme handler, enables JavaScript
(KaTeX and highlight.js need it), makes the background transparent so the card's
own backing shows through, and loads the initial HTML from memory with a
`ccassets://` base URL so relative asset references resolve through the handler.
""",
    ("ModelAnswerWebView.swift", "func updateNSView"): """
SwiftUI calls this when an input changes. It reloads the page only when the
Markdown or font size actually differs (avoiding needless reloads); when only the
scroll token advanced it runs a small `window.scrollBy`, so a spoken "scroll
up/down" pages through a long answer.
""",
    ("ModelAnswerWebView.swift", "class Coordinator"): """
Holds the mutable state the value-type view cannot: the web view, the last-loaded
Markdown and font size (to detect real changes), and the last scroll token. As
`WKNavigationDelegate` it also vetoes navigation — only the in-memory load and
our asset scheme are allowed, so a link in the answer cannot send the view
anywhere.
""",
    ("ClassroomAppModel.swift", "func scrollModelAnswer"): """
Handles the spoken scroll commands. It acts only when an answer is actually on
screen (not hidden, no student question in front), then bumps a counter and
records the direction; the overlay's web view watches that counter and performs
the scroll. The counter avoids passing a closure across the SwiftUI boundary.
""",
    ("ClassroomAppModel.swift", "func consumeModelQuestion"): """
The finalized-text half of Assistant mode. It scans one finalized caption for the
start/end keyword phrases and, accumulating across segments, decides: pass text
through unchanged, begin capturing a question, append to one in progress, or — on
the end phrase — send the assembled question to the model. It returns whatever
surrounding text should still become an ordinary subtitle, so the framed question
never leaks into the captions.
""",
    ("ClassroomAppModel.swift", "func armModelQuestionTimeout"): """
The safety net that stops a mis-heard end phrase from swallowing the captions
forever. Each time the capture grows it restarts a 30-second timer; if no end
phrase arrives, the capture is abandoned and the gathered text restored as a
normal subtitle. Cancelling the previous task first means only inactivity counts.
""",
    ("ClassroomAppModel.swift", "func cancelModelQuestionCapture"): """
Leaves capture mode. `restoringCaption` decides the gathered text's fate: the
timeout restores it as a subtitle (nothing the professor said is lost) while the
clear command discards it (he asked to wipe it). Either way it stops the timer
and refreshes the overlay so the capture banner disappears.
""",
    ("ClassroomAppModel.swift", "func previewModelQuestion"): """
The provisional-text half. Live hypotheses change constantly, so this never acts;
it only hides the part of the in-progress hypothesis that belongs to a question
being dictated, so the keyword phrases and the question do not flash as subtitles
before they are finalized.
""",
    ("ClassroomAppModel.swift", "func appendToQuestionCapture"): """
Appends a newly finalized segment to the question being assembled, trimming and
skipping empties so a multi-segment question joins with single spaces.
""",
    ("ClassroomAppModel.swift", "func joinedCaption"): """
Joins the text before a start phrase and after an end phrase into the single
subtitle they should form, dropping empties — used when a whole question arrives
inside one finalized segment.
""",
    ("ClassroomAppModel.swift", "func submitModelQuestion"): """
Sends a captured question to Gemma and surfaces the answer. It cancels any
in-flight request, shows the "generating" state, then on a background task warms
the server, calls the answer endpoint, and stores the Markdown (or an error
message) for the overlay. The model is handed only text and returns only text —
its reply is rendered, never executed, and never leaves the machine.
""",
    ("CaptionOverlayController.swift", "func captureBanner"): """
The mint banner shown while a question is being dictated. It names the exact end
phrase to say and echoes the text captured so far, so a mis-heard end phrase can
never leave the professor staring at vanished captions with no idea why.
""",
    ("CaptionOverlayController.swift", "func answerCard"): """
The model-answer card: a header above the locked-down `ModelAnswerView` web view,
given a solid dark backing so it stays readable regardless of the overlay's
background-opacity slider (that slider is for the captions). The neighbouring
loading card shows a spinner while the answer is still being generated.
""",
    ("DashboardView.swift", "func formatMemory"): """
Formats a raw byte count as a human-readable string for the diagnostics panel
using `ByteCountFormatter` with the memory count style, so a multi-gigabyte model
footprint reads naturally instead of as a long digit string.
""",
    ("GemmaCorrectionService.swift", "func answer"): """
Assistant mode's question path, deliberately separate from `correct`. It posts
the question with the answer-permitting system prompt, asks for more tokens than a
correction would, and returns the raw Markdown reply. No validator runs because
this is an answer, not a transcription — and the reply is rendered as text, never
executed.
""",
    ("SpokenOverlayCommandTests.swift", "testRecognizesScrollAndToggleAnswerCommands"): """
Confirms the three new overlay actions — scroll up, scroll down, and show/hide
answer — are each recognized from their configured phrase.
""",
    ("SpokenOverlayCommandTests.swift", "testEmptyScrollPhrasesAreIgnored"): """
Confirms an unconfigured (empty) scroll or toggle phrase matches nothing, so
leaving a command blank simply disables it.
""",
    ("ModelQuestionScanTests.swift", "class ModelQuestionScanTests"): """
Exercises the keyword-framed question detector used by Assistant mode, covering
every split of a transcript into surrounding caption text and the framed question.
""",
    ("ModelQuestionScanTests.swift", "func scan"): """
Test helper that runs the detector with the fixed default start/end phrases, so
each case reads as just its input and expected split.
""",
    ("ModelQuestionScanTests.swift", "testCompleteQuestionInOneSegment"): """
A whole question framed within one segment is reported as `.complete`, with the
question extracted and no surrounding caption.
""",
    ("ModelQuestionScanTests.swift", "testSurroundingTextStaysCaption"): """
Text before the start phrase and after the end phrase is preserved as caption,
while only the framed span becomes the question.
""",
    ("ModelQuestionScanTests.swift", "testOpensWithoutClosing"): """
A start phrase with no end phrase is `.opens`: capture begins and the text after
the phrase is the question so far.
""",
    ("ModelQuestionScanTests.swift", "testClosesAnOpenCapture"): """
An end phrase with no start phrase is `.closes`: it finishes a question opened in
an earlier segment, and the text after it returns to the captions.
""",
    ("ModelQuestionScanTests.swift", "testPlainTextIsNotAQuestion"): """
Ordinary speech with neither phrase is `.none` and stays entirely caption.
""",
    ("ModelQuestionScanTests.swift", "testToleratesMissingAccentsAndCase"): """
The phrases are matched after accent- and case-folding, so "bonjour modele
debut/fin" triggers exactly like the accented spelling Voxtral may or may not
produce.
""",
    ("ModelQuestionScanTests.swift", "testEndBeforeStartDoesNotClose"): """
An end phrase appearing before the start phrase must not pair with it: detection
only accepts an end that follows a start.
""",
    ("ModelQuestionScanTests.swift", "testEmptyPhrasesYieldNone"): """
With the feature unconfigured (empty phrases) nothing is detected, so disabling
Assistant mode cannot accidentally capture text.
""",
}

EXTRA_SYMBOL_GUIDES.update(PEDAGOGY_REWRITES)
