import AppKit
import SwiftUI

private final class OverlayInteractionView: NSView {
    enum Interaction {
        case move
        case resize
    }

    var onDrag: ((Interaction, CGSize) -> Void)?
    var onDragEnded: (() -> Void)?

    private var interaction: Interaction?
    private var mouseDownLocation = NSPoint.zero

    override var isOpaque: Bool { false }

    override func hitTest(_ point: NSPoint) -> NSView? {
        let topHandle = NSRect(x: 0, y: bounds.maxY - 42, width: bounds.width, height: 42)
        let resizeHandle = NSRect(x: bounds.maxX - 48, y: 0, width: 48, height: 48)
        return topHandle.contains(point) || resizeHandle.contains(point) ? self : nil
    }

    override func acceptsFirstMouse(for event: NSEvent?) -> Bool {
        true
    }

    override func resetCursorRects() {
        super.resetCursorRects()
        addCursorRect(
            NSRect(x: 0, y: bounds.maxY - 42, width: bounds.width, height: 42),
            cursor: .openHand
        )
        addCursorRect(
            NSRect(x: bounds.maxX - 48, y: 0, width: 48, height: 48),
            cursor: .crosshair
        )
    }

    override func mouseDown(with event: NSEvent) {
        let point = convert(event.locationInWindow, from: nil)
        let resizeHandle = NSRect(x: bounds.maxX - 48, y: 0, width: 48, height: 48)
        interaction = resizeHandle.contains(point) ? .resize : .move
        mouseDownLocation = NSEvent.mouseLocation
        if interaction == .move {
            NSCursor.closedHand.set()
        }
    }

    override func mouseDragged(with event: NSEvent) {
        guard let interaction else { return }
        let current = NSEvent.mouseLocation
        onDrag?(
            interaction,
            CGSize(
                width: current.x - mouseDownLocation.x,
                height: current.y - mouseDownLocation.y
            )
        )
    }

    override func mouseUp(with event: NSEvent) {
        interaction = nil
        window?.invalidateCursorRects(for: self)
        onDragEnded?()
    }
}

@MainActor
final class CaptionOverlayController: NSObject, NSWindowDelegate {
    private static let minimumSize = NSSize(width: 420, height: 120)
    private static let screenMargin: CGFloat = 12
    private static let geometryDefaultsPrefix = "captionOverlay.frame."

    private let panel: NSPanel
    private let hostingView: NSHostingView<CaptionOverlayView>
    private let interactionView = OverlayInteractionView()
    private var selectedDisplayID: CGDirectDisplayID?
    private var interactionStartFrame: NSRect?
    private var isApplyingFrame = false

    var isVisible: Bool {
        panel.isVisible
    }

    override init() {
        panel = NSPanel(
            contentRect: NSRect(x: 0, y: 0, width: 900, height: 180),
            styleMask: [.borderless, .nonactivatingPanel],
            backing: .buffered,
            defer: true
        )
        hostingView = NSHostingView(
            rootView: CaptionOverlayView(
                lines: [],
                provisional: nil,
                question: nil,
                pendingQuestionCount: 0,
                fontSize: 32
            )
        )

        super.init()

        panel.delegate = self
        panel.isReleasedWhenClosed = false
        panel.backgroundColor = .clear
        panel.isOpaque = false
        panel.hasShadow = true
        panel.level = .floating
        panel.hidesOnDeactivate = false
        panel.ignoresMouseEvents = false
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .ignoresCycle]
        panel.minSize = Self.minimumSize

        hostingView.sizingOptions = []
        let containerView = NSView()
        hostingView.translatesAutoresizingMaskIntoConstraints = false
        interactionView.translatesAutoresizingMaskIntoConstraints = false
        containerView.addSubview(hostingView)
        containerView.addSubview(interactionView)
        NSLayoutConstraint.activate([
            hostingView.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            hostingView.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            hostingView.topAnchor.constraint(equalTo: containerView.topAnchor),
            hostingView.bottomAnchor.constraint(equalTo: containerView.bottomAnchor),
            interactionView.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            interactionView.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            interactionView.topAnchor.constraint(equalTo: containerView.topAnchor),
            interactionView.bottomAnchor.constraint(equalTo: containerView.bottomAnchor),
        ])
        interactionView.onDrag = { [weak self] interaction, translation in
            switch interaction {
            case .move:
                self?.movePanel(by: translation)
            case .resize:
                self?.resizePanel(by: translation)
            }
        }
        interactionView.onDragEnded = { [weak self] in
            self?.finishInteraction()
        }
        panel.contentView = containerView
        panel.orderOut(nil)
    }

    func show(
        on screen: NSScreen,
        lines: [String],
        provisional: String?,
        question: String?,
        pendingQuestionCount: Int,
        fontSize: Double
    ) {
        hostingView.rootView = CaptionOverlayView(
            lines: lines,
            provisional: provisional,
            question: question,
            pendingQuestionCount: pendingQuestionCount,
            fontSize: fontSize
        )

        let displayID = screen.displayID
        if selectedDisplayID != displayID {
            selectedDisplayID = displayID
            applyFrame(restoredFrame(on: screen), on: screen)
        } else if !panel.isVisible {
            applyFrame(Self.clamped(panel.frame, to: screen.visibleFrame), on: screen)
        }

        panel.orderFrontRegardless()
    }

    func hide() {
        persistFrame()
        panel.orderOut(nil)
    }

    func resetFrame(on screen: NSScreen) {
        selectedDisplayID = screen.displayID
        UserDefaults.standard.removeObject(forKey: geometryKey(for: screen.displayID))
        applyFrame(Self.defaultFrame(on: screen), on: screen)
    }

    func windowDidMove(_ notification: Notification) {
        persistFrame()
    }

    func windowDidResize(_ notification: Notification) {
        persistFrame()
    }

    private func movePanel(by translation: CGSize) {
        guard let screen = selectedScreen else { return }
        let start = interactionStartFrame ?? panel.frame
        interactionStartFrame = start
        let proposed = NSRect(
            x: start.minX + translation.width,
            y: start.minY + translation.height,
            width: start.width,
            height: start.height
        )
        applyFrame(Self.clamped(proposed, to: screen.visibleFrame), on: screen)
    }

    private func resizePanel(by translation: CGSize) {
        guard let screen = selectedScreen else { return }
        let start = interactionStartFrame ?? panel.frame
        interactionStartFrame = start

        let maximumWidth = screen.visibleFrame.maxX - start.minX - Self.screenMargin
        let maximumHeight = start.maxY - screen.visibleFrame.minY - Self.screenMargin
        let width = min(
            max(Self.minimumSize.width, start.width + translation.width),
            max(Self.minimumSize.width, maximumWidth)
        )
        let height = min(
            max(Self.minimumSize.height, start.height - translation.height),
            max(Self.minimumSize.height, maximumHeight)
        )
        let proposed = NSRect(
            x: start.minX,
            y: start.maxY - height,
            width: width,
            height: height
        )
        applyFrame(Self.clamped(proposed, to: screen.visibleFrame), on: screen)
    }

    private func finishInteraction() {
        interactionStartFrame = nil
        persistFrame()
    }

    private var selectedScreen: NSScreen? {
        NSScreen.screens.first { $0.displayID == selectedDisplayID } ?? panel.screen
    }

    private func restoredFrame(on screen: NSScreen) -> NSRect {
        guard let value = UserDefaults.standard.string(
            forKey: geometryKey(for: screen.displayID)
        ) else {
            return Self.defaultFrame(on: screen)
        }
        return Self.clamped(NSRectFromString(value), to: screen.visibleFrame)
    }

    private func persistFrame() {
        guard !isApplyingFrame, let displayID = selectedDisplayID else { return }
        UserDefaults.standard.set(
            NSStringFromRect(panel.frame),
            forKey: geometryKey(for: displayID)
        )
    }

    private func geometryKey(for displayID: CGDirectDisplayID) -> String {
        Self.geometryDefaultsPrefix + String(displayID)
    }

    private func applyFrame(_ frame: NSRect, on screen: NSScreen) {
        isApplyingFrame = true
        panel.maxSize = NSSize(
            width: screen.visibleFrame.width - Self.screenMargin * 2,
            height: screen.visibleFrame.height - Self.screenMargin * 2
        )
        panel.setFrame(frame, display: true)
        isApplyingFrame = false
    }

    static func defaultFrame(on screen: NSScreen) -> NSRect {
        let horizontalMargin: CGFloat = 60
        let width = min(1_200, max(600, screen.visibleFrame.width - horizontalMargin * 2))
        let height: CGFloat = 220
        return NSRect(
            x: screen.visibleFrame.midX - width / 2,
            y: screen.visibleFrame.minY + 48,
            width: width,
            height: height
        )
    }

    static func clamped(_ frame: NSRect, to visibleFrame: NSRect) -> NSRect {
        let availableWidth = max(1, visibleFrame.width - screenMargin * 2)
        let availableHeight = max(1, visibleFrame.height - screenMargin * 2)
        let minimumWidth = min(minimumSize.width, availableWidth)
        let minimumHeight = min(minimumSize.height, availableHeight)
        let width = min(max(frame.width, minimumWidth), availableWidth)
        let height = min(max(frame.height, minimumHeight), availableHeight)
        let minX = visibleFrame.minX + screenMargin
        let minY = visibleFrame.minY + screenMargin
        let maxX = visibleFrame.maxX - screenMargin - width
        let maxY = visibleFrame.maxY - screenMargin - height
        return NSRect(
            x: min(max(frame.minX, minX), maxX),
            y: min(max(frame.minY, minY), maxY),
            width: width,
            height: height
        )
    }
}

struct CaptionOverlayView: View {
    private static let bottomAnchor = "caption-overlay-bottom"

    let lines: [String]
    let provisional: String?
    let question: String?
    let pendingQuestionCount: Int
    let fontSize: Double

    private var hasContent: Bool {
        !lines.isEmpty || provisional?.isEmpty == false
    }

    private var contentVersion: String {
        lines.joined(separator: "\u{0}")
            + "\u{1}"
            + (provisional ?? "")
    }

    var body: some View {
        ZStack {
            VStack(alignment: .leading, spacing: 10) {
                moveHandle

                if pendingQuestionCount > 0 {
                    pendingQuestionIndicator
                }

                if let question, !question.isEmpty {
                    questionCard(question)
                }

                ScrollViewReader { proxy in
                    ScrollView(.vertical) {
                        VStack(alignment: .leading, spacing: 10) {
                            Spacer(minLength: 4)

                            if hasContent {
                                ForEach(
                                    Array(lines.enumerated()),
                                    id: \.offset
                                ) { _, line in
                                    captionText(line)
                                }

                                if let provisional, !provisional.isEmpty {
                                    captionText(provisional)
                                        .foregroundStyle(.white.opacity(0.72))
                                        .italic()
                                }
                            } else {
                                Text("Caption overlay preview")
                                    .foregroundStyle(.white.opacity(0.72))
                            }

                            Color.clear
                                .frame(height: 1)
                                .id(Self.bottomAnchor)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .scrollIndicators(.hidden)
                    .defaultScrollAnchor(.bottom)
                    .onAppear {
                        scrollToBottom(proxy)
                    }
                    .onChange(of: contentVersion) {
                        scrollToBottom(proxy)
                    }
                }
            }
            .font(.system(size: fontSize, weight: .semibold, design: .rounded))
            .padding(.horizontal, 28)
            .padding(.bottom, 20)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .bottomLeading)

            resizeHandle
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .bottomTrailing)
        }
        .background(.black.opacity(0.82))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(.white.opacity(0.16), lineWidth: 1)
        }
    }

    private func captionText(_ text: String) -> some View {
        Text(text)
            .foregroundStyle(.white)
            .lineLimit(nil)
            .fixedSize(horizontal: false, vertical: true)
            .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func questionCard(_ question: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Label("Student question", systemImage: "questionmark.bubble.fill")
                .font(.system(size: 13, weight: .bold))
                .foregroundStyle(.orange)

            ScrollView(.vertical) {
                Text(question)
                    .font(.system(
                        size: max(18, fontSize * 0.72),
                        weight: .semibold,
                        design: .rounded
                    ))
                    .foregroundStyle(.white)
                    .fixedSize(horizontal: false, vertical: true)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .scrollIndicators(.visible)
            .frame(maxHeight: 130)
        }
        .padding(12)
        .background(.orange.opacity(0.18))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(.orange.opacity(0.55), lineWidth: 1)
        }
    }

    private var pendingQuestionIndicator: some View {
        Label(
            pendingQuestionCount == 1
                ? "1 student question pending"
                : "\(pendingQuestionCount) student questions pending",
            systemImage: "questionmark.bubble.fill"
        )
        .font(.system(size: 13, weight: .bold))
        .foregroundStyle(.orange)
        .padding(.horizontal, 10)
        .padding(.vertical, 7)
        .background(.orange.opacity(0.18))
        .clipShape(Capsule())
        .accessibilityLabel(
            "\(pendingQuestionCount) pending student questions"
        )
    }

    private func scrollToBottom(_ proxy: ScrollViewProxy) {
        DispatchQueue.main.async {
            proxy.scrollTo(Self.bottomAnchor, anchor: .bottom)
        }
    }

    private var moveHandle: some View {
        HStack(spacing: 8) {
            Image(systemName: "arrow.up.and.down.and.arrow.left.and.right")
            Text("Drag to move")
            Spacer()
        }
        .font(.system(size: 12, weight: .medium))
        .foregroundStyle(.white.opacity(0.58))
        .contentShape(Rectangle())
        .padding(.top, 10)
        .padding(.bottom, 4)
        .accessibilityLabel("Move caption overlay")
        .help("Drag to move the caption overlay")
    }

    private var resizeHandle: some View {
        Image(systemName: "arrow.down.right.and.arrow.up.left")
            .font(.system(size: 14, weight: .semibold))
            .foregroundStyle(.white.opacity(0.7))
            .frame(width: 38, height: 38)
            .contentShape(Rectangle())
            .accessibilityLabel("Resize caption overlay")
            .help("Drag to resize the caption overlay")
    }
}

private extension NSScreen {
    var displayID: CGDirectDisplayID {
        deviceDescription[NSDeviceDescriptionKey("NSScreenNumber")] as? CGDirectDisplayID ?? 0
    }
}
