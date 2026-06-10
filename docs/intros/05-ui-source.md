## SwiftUI evaluation model

`DashboardView` is a struct. SwiftUI may create it frequently and call `body`
again whenever observed dependencies change. Local helper properties do not
cache widgets; they build new value descriptions. Persistent state therefore
belongs in the observable app model or a property wrapper designed for that
purpose.

Result-builder syntax allows `if`, `ForEach`, and multiple child expressions
inside containers. The compiler transforms those branches into nested generic
view types. `some View` hides the unwieldy concrete type while retaining static
dispatch.

## Why the overlay uses AppKit

The overlay requires behavior outside ordinary SwiftUI scene control:

- a borderless `NSPanel`;
- no application activation when clicked;
- explicit window level;
- placement on a chosen `NSScreen`;
- Spaces (macOS virtual desktops)/full-screen collection behavior;
- pointer-level move and resize;
- frame persistence per physical display.

`CaptionOverlayController` owns this imperative window lifecycle. It creates
one panel and replaces/updates hosted SwiftUI content as values change.

## Coordinate systems and clamping

macOS screen coordinates use a global desktop space and may contain negative
origins when displays are arranged left or below the primary display.
`visibleFrame` excludes menu bar and Dock reservations. Clamping therefore uses
the target screen's actual rectangle rather than assuming origin `(0, 0)`.

Resize computes the proposed frame from the dragged edge/corner, enforces
minimum dimensions, then intersects the result with visible bounds. Move keeps
size and changes origin. Persisted frames are keyed by display identifier so
projector and laptop arrangements can remember different geometry.

## Scrolling caption content

The overlay uses a scroll container rather than a line-limited text label.
After content changes, a scroll proxy moves to a stable bottom anchor. Dispatch
to the next main-loop turn lets SwiftUI finish layout before the scroll request;
otherwise the proxy may target the previous content height.
