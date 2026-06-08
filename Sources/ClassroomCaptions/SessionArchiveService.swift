import ClassroomCaptionsCore
import Foundation

struct SessionArchiveMetadata: Codable {
    let sessionID: UUID
    let startedAt: Date
    let endedAt: Date?
    let backend: String
    let microphone: String?
    let modelDelayMilliseconds: Int
    let audioFormat: String
    let audioBytes: UInt64
}

enum SessionArchiveError: LocalizedError {
    case audioTooLarge

    var errorDescription: String? {
        switch self {
        case .audioTooLarge:
            return "The WAV recording exceeded the 4 GB PCM file limit."
        }
    }
}

final class SessionArchiveService: @unchecked Sendable {
    private struct State {
        var directory: URL?
        var audioURL: URL?
        var audioHandle: FileHandle?
        var audioBytes: UInt64 = 0
        var writeFailure: String?
    }

    private let queue = DispatchQueue(
        label: "ClassroomCaptions.session.archive",
        qos: .utility
    )
    private var state = State()

    func start(session: ClassroomSession, rootDirectory: URL) async throws -> URL {
        try await perform {
            try self.closeAudioFile()
            let directory = rootDirectory.appendingPathComponent(
                Self.directoryName(for: session),
                isDirectory: true
            )
            try FileManager.default.createDirectory(
                at: directory,
                withIntermediateDirectories: true
            )

            let audioURL = directory.appendingPathComponent("audio.wav")
            FileManager.default.createFile(
                atPath: audioURL.path,
                contents: PCM16WAVHeader.make(dataByteCount: 0)
            )
            let handle = try FileHandle(forWritingTo: audioURL)
            try handle.seekToEnd()
            self.state = State(
                directory: directory,
                audioURL: audioURL,
                audioHandle: handle,
                audioBytes: 0
            )
            return directory
        }
    }

    func appendAudio(_ pcm16MonoData: Data) {
        guard !pcm16MonoData.isEmpty else { return }
        queue.async {
            guard let handle = self.state.audioHandle else { return }
            do {
                try handle.write(contentsOf: pcm16MonoData)
                self.state.audioBytes += UInt64(pcm16MonoData.count)
            } catch {
                self.state.writeFailure = error.localizedDescription
                try? handle.close()
                self.state.audioHandle = nil
            }
        }
    }

    func finalize(
        session: ClassroomSession,
        backend: String,
        microphone: String?,
        modelDelayMilliseconds: Int
    ) async throws -> URL? {
        try await perform {
            guard let directory = self.state.directory else { return nil }
            if let writeFailure = self.state.writeFailure {
                throw CocoaError(
                    .fileWriteUnknown,
                    userInfo: [NSLocalizedDescriptionKey: writeFailure]
                )
            }
            guard self.state.audioBytes <= UInt64(UInt32.max) else {
                throw SessionArchiveError.audioTooLarge
            }

            if let handle = self.state.audioHandle {
                try handle.seek(toOffset: 0)
                try handle.write(contentsOf: PCM16WAVHeader.make(
                    dataByteCount: UInt32(self.state.audioBytes)
                ))
                try handle.synchronize()
                try handle.close()
                self.state.audioHandle = nil
            }

            let transcript = SessionTranscriptDocument(session: session)
            try transcript.plainText().write(
                to: directory.appendingPathComponent("transcript.txt"),
                atomically: true,
                encoding: .utf8
            )
            try transcript.encodedJSON().write(
                to: directory.appendingPathComponent("transcript.json"),
                options: .atomic
            )

            let metadata = SessionArchiveMetadata(
                sessionID: session.id,
                startedAt: session.startedAt,
                endedAt: session.endedAt,
                backend: backend,
                microphone: microphone,
                modelDelayMilliseconds: modelDelayMilliseconds,
                audioFormat: "PCM signed 16-bit little-endian, 16000 Hz, mono",
                audioBytes: self.state.audioBytes
            )
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            try encoder.encode(metadata).write(
                to: directory.appendingPathComponent("session.json"),
                options: .atomic
            )

            self.state = State()
            return directory
        }
    }

    func cancel() {
        queue.sync {
            try? closeAudioFile()
            state = State()
        }
    }

    private func closeAudioFile() throws {
        if let handle = state.audioHandle {
            try handle.close()
        }
        state.audioHandle = nil
    }

    private func perform<T: Sendable>(
        _ operation: @escaping @Sendable () throws -> T
    ) async throws -> T {
        try await withCheckedThrowingContinuation { continuation in
            queue.async {
                do {
                    continuation.resume(returning: try operation())
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }

    private static func directoryName(for session: ClassroomSession) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = .current
        formatter.dateFormat = "yyyy-MM-dd_HH-mm-ss"
        return "\(formatter.string(from: session.startedAt))_"
            + session.id.uuidString.prefix(8)
    }
}
