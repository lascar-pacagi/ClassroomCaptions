import Foundation

public enum CaptionCorrectionState: String, Codable, Equatable, Sendable {
    case notRequested
    case queued
    case correcting
    case corrected
    case failed
}

public struct CaptionSegment: Identifiable, Codable, Equatable, Sendable {
    public let id: UUID
    public let sequence: Int
    public let startedAt: Date
    public let finalizedAt: Date
    public let rawText: String
    public private(set) var correctedText: String?
    public private(set) var correctionState: CaptionCorrectionState
    public private(set) var correctionFailure: String?

    public var displayText: String {
        correctedText ?? rawText
    }

    public init(
        id: UUID,
        sequence: Int,
        startedAt: Date,
        finalizedAt: Date,
        rawText: String,
        correctionState: CaptionCorrectionState
    ) {
        self.id = id
        self.sequence = sequence
        self.startedAt = startedAt
        self.finalizedAt = finalizedAt
        self.rawText = rawText
        self.correctedText = nil
        self.correctionState = correctionState
        self.correctionFailure = nil
    }

    mutating func beginCorrection() -> Bool {
        guard correctionState == .queued else { return false }
        correctionState = .correcting
        correctionFailure = nil
        return true
    }

    mutating func applyCorrection(_ text: String) -> Bool {
        guard correctionState == .correcting else { return false }
        let normalized = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalized.isEmpty else { return false }

        correctedText = normalized
        correctionState = .corrected
        correctionFailure = nil
        return true
    }

    mutating func failCorrection(_ message: String) -> Bool {
        guard correctionState == .queued || correctionState == .correcting else {
            return false
        }
        correctedText = nil
        correctionState = .failed
        correctionFailure = message.trimmingCharacters(in: .whitespacesAndNewlines)
        return true
    }
}

public struct ProvisionalCaption: Codable, Equatable, Sendable {
    public let startedAt: Date
    public private(set) var text: String

    public init(startedAt: Date, text: String) {
        self.startedAt = startedAt
        self.text = text
    }

    mutating func update(text: String) {
        self.text = text
    }
}

public struct CaptionTimeline: Codable, Equatable, Sendable {
    public private(set) var segments: [CaptionSegment] = []
    public private(set) var provisional: ProvisionalCaption?
    private var nextSequence = 0

    public init() {}

    public var isEmpty: Bool {
        segments.isEmpty && provisional == nil
    }

    public mutating func updateProvisional(_ text: String, at timestamp: Date = Date()) {
        let normalized = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalized.isEmpty else {
            provisional = nil
            return
        }

        if provisional == nil {
            provisional = ProvisionalCaption(startedAt: timestamp, text: normalized)
        } else {
            provisional?.update(text: normalized)
        }
    }

    @discardableResult
    public mutating func finalize(
        _ text: String,
        at timestamp: Date = Date(),
        correctionEnabled: Bool,
        id: UUID = UUID()
    ) -> CaptionSegment? {
        let normalized = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalized.isEmpty else {
            provisional = nil
            return nil
        }

        let segment = CaptionSegment(
            id: id,
            sequence: nextSequence,
            startedAt: provisional?.startedAt ?? timestamp,
            finalizedAt: timestamp,
            rawText: normalized,
            correctionState: correctionEnabled ? .queued : .notRequested
        )
        nextSequence += 1
        provisional = nil
        segments.append(segment)
        return segment
    }

    @discardableResult
    public mutating func beginCorrection(segmentID: UUID) -> Bool {
        guard let index = segments.firstIndex(where: { $0.id == segmentID }) else {
            return false
        }
        return segments[index].beginCorrection()
    }

    @discardableResult
    public mutating func applyCorrection(segmentID: UUID, text: String) -> Bool {
        guard let index = segments.firstIndex(where: { $0.id == segmentID }) else {
            return false
        }
        return segments[index].applyCorrection(text)
    }

    @discardableResult
    public mutating func failCorrection(segmentID: UUID, message: String) -> Bool {
        guard let index = segments.firstIndex(where: { $0.id == segmentID }) else {
            return false
        }
        return segments[index].failCorrection(message)
    }

    public func recentSegments(limit: Int) -> [CaptionSegment] {
        guard limit > 0 else { return [] }
        return Array(segments.suffix(limit))
    }

    public mutating func reset() {
        segments.removeAll(keepingCapacity: true)
        provisional = nil
        nextSequence = 0
    }
}
