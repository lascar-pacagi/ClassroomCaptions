import Foundation

public enum PCM16WAVHeader {
    public static let byteCount = 44

    public static func make(
        dataByteCount: UInt32,
        sampleRate: UInt32 = 16_000,
        channelCount: UInt16 = 1
    ) -> Data {
        let bitsPerSample: UInt16 = 16
        let blockAlign = channelCount * bitsPerSample / 8
        let byteRate = sampleRate * UInt32(blockAlign)
        var data = Data()
        data.appendASCII("RIFF")
        data.appendLittleEndian(36 + dataByteCount)
        data.appendASCII("WAVE")
        data.appendASCII("fmt ")
        data.appendLittleEndian(UInt32(16))
        data.appendLittleEndian(UInt16(1))
        data.appendLittleEndian(channelCount)
        data.appendLittleEndian(sampleRate)
        data.appendLittleEndian(byteRate)
        data.appendLittleEndian(blockAlign)
        data.appendLittleEndian(bitsPerSample)
        data.appendASCII("data")
        data.appendLittleEndian(dataByteCount)
        return data
    }
}

public struct SessionTranscriptEntry: Codable, Equatable, Sendable {
    public let sequence: Int
    public let startSeconds: TimeInterval
    public let endSeconds: TimeInterval
    public let rawText: String
    public let correctedText: String?
    public let displayedText: String
    public let correctionState: CaptionCorrectionState
}

public struct SessionTranscriptDocument: Codable, Equatable, Sendable {
    public let sessionID: UUID
    public let startedAt: Date
    public let endedAt: Date?
    public let entries: [SessionTranscriptEntry]

    public init(session: ClassroomSession) {
        sessionID = session.id
        startedAt = session.startedAt
        endedAt = session.endedAt
        entries = session.timeline.segments.map { segment in
            SessionTranscriptEntry(
                sequence: segment.sequence,
                startSeconds: max(
                    0,
                    segment.startedAt.timeIntervalSince(session.startedAt)
                ),
                endSeconds: max(
                    0,
                    segment.finalizedAt.timeIntervalSince(session.startedAt)
                ),
                rawText: segment.rawText,
                correctedText: segment.correctedText,
                displayedText: segment.displayText,
                correctionState: segment.correctionState
            )
        }
    }

    public func plainText() -> String {
        entries.map { entry in
            "[\(Self.timestamp(entry.startSeconds)) - "
                + "\(Self.timestamp(entry.endSeconds))] \(entry.displayedText)"
        }
        .joined(separator: "\n")
        .appending(entries.isEmpty ? "" : "\n")
    }

    public func encodedJSON() throws -> Data {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return try encoder.encode(self)
    }

    private static func timestamp(_ interval: TimeInterval) -> String {
        let milliseconds = max(0, Int((interval * 1_000).rounded()))
        let hours = milliseconds / 3_600_000
        let minutes = milliseconds / 60_000 % 60
        let seconds = milliseconds / 1_000 % 60
        let remainder = milliseconds % 1_000
        if hours > 0 {
            return String(
                format: "%02d:%02d:%02d.%03d",
                hours,
                minutes,
                seconds,
                remainder
            )
        }
        return String(
            format: "%02d:%02d.%03d",
            minutes,
            seconds,
            remainder
        )
    }
}

private extension Data {
    mutating func appendASCII(_ string: String) {
        append(string.data(using: .ascii)!)
    }

    mutating func appendLittleEndian<T: FixedWidthInteger>(_ value: T) {
        var littleEndian = value.littleEndian
        Swift.withUnsafeBytes(of: &littleEndian) { append(contentsOf: $0) }
    }
}
