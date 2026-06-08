import Foundation

public enum ClassroomSessionPhase: String, Codable, Equatable, Sendable {
    case idle
    case starting
    case listening
    case paused
    case stopping
    case failed
}

public struct ClassroomSession: Codable, Equatable, Sendable {
    public let id: UUID
    public let startedAt: Date
    public private(set) var endedAt: Date?
    public private(set) var phase: ClassroomSessionPhase
    public private(set) var timeline: CaptionTimeline
    public private(set) var failureMessage: String?

    public init(id: UUID = UUID(), startedAt: Date = Date()) {
        self.id = id
        self.startedAt = startedAt
        self.endedAt = nil
        self.phase = .starting
        self.timeline = CaptionTimeline()
        self.failureMessage = nil
    }

    @discardableResult
    public mutating func markListening() -> Bool {
        guard phase == .starting || phase == .paused else { return false }
        phase = .listening
        failureMessage = nil
        return true
    }

    @discardableResult
    public mutating func pause() -> Bool {
        guard phase == .listening else { return false }
        phase = .paused
        timeline.updateProvisional("")
        return true
    }

    @discardableResult
    public mutating func beginStopping() -> Bool {
        guard phase == .listening || phase == .paused || phase == .failed else {
            return false
        }
        phase = .stopping
        timeline.updateProvisional("")
        return true
    }

    @discardableResult
    public mutating func finish(at timestamp: Date = Date()) -> Bool {
        guard phase == .stopping else { return false }
        phase = .idle
        endedAt = timestamp
        return true
    }

    public mutating func fail(_ message: String) {
        phase = .failed
        failureMessage = message.trimmingCharacters(in: .whitespacesAndNewlines)
        timeline.updateProvisional("")
    }

    public mutating func updateProvisional(_ text: String, at timestamp: Date = Date()) {
        guard phase == .listening else { return }
        timeline.updateProvisional(text, at: timestamp)
    }

    @discardableResult
    public mutating func finalizeCaption(
        _ text: String,
        at timestamp: Date = Date(),
        correctionEnabled: Bool
    ) -> CaptionSegment? {
        guard phase == .listening || phase == .stopping else { return nil }
        return timeline.finalize(
            text,
            at: timestamp,
            correctionEnabled: correctionEnabled
        )
    }

    @discardableResult
    public mutating func beginCorrection(segmentID: UUID) -> Bool {
        timeline.beginCorrection(segmentID: segmentID)
    }

    @discardableResult
    public mutating func applyCorrection(segmentID: UUID, text: String) -> Bool {
        timeline.applyCorrection(segmentID: segmentID, text: text)
    }

    @discardableResult
    public mutating func failCorrection(segmentID: UUID, message: String) -> Bool {
        timeline.failCorrection(segmentID: segmentID, message: message)
    }
}
