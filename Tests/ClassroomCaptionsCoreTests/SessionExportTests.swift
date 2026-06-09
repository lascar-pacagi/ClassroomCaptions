@testable import ClassroomCaptions
import ClassroomCaptionsCore
import XCTest

final class SessionExportTests: XCTestCase {
    func testWAVHeaderDescribesPCM16MonoAudio() {
        let header = PCM16WAVHeader.make(dataByteCount: 32_000)

        XCTAssertEqual(header.count, 44)
        XCTAssertEqual(String(data: header[0 ..< 4], encoding: .ascii), "RIFF")
        XCTAssertEqual(String(data: header[8 ..< 12], encoding: .ascii), "WAVE")
        XCTAssertEqual(readUInt32(header, at: 4), 32_036)
        XCTAssertEqual(readUInt32(header, at: 24), 16_000)
        XCTAssertEqual(readUInt16(header, at: 22), 1)
        XCTAssertEqual(readUInt16(header, at: 34), 16)
        XCTAssertEqual(readUInt32(header, at: 40), 32_000)
    }

    func testTranscriptUsesRelativeTimestampsAndPreservesRawText() throws {
        let startedAt = Date(timeIntervalSince1970: 1_000)
        var session = ClassroomSession(
            id: UUID(uuidString: "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE")!,
            startedAt: startedAt
        )
        XCTAssertTrue(session.markListening())
        session.updateProvisional(
            "raw teknical text",
            at: startedAt.addingTimeInterval(1.25)
        )
        _ = session.finalizeCaption(
            "raw teknical text",
            at: startedAt.addingTimeInterval(3.5),
            correctionEnabled: false
        )

        let document = SessionTranscriptDocument(session: session)
        XCTAssertEqual(
            document.plainText(),
            "[00:01.250 - 00:03.500] raw teknical text\n"
        )

        let decoded = try JSONDecoder.iso8601.decode(
            SessionTranscriptDocument.self,
            from: document.encodedJSON()
        )
        XCTAssertEqual(decoded.entries.first?.rawText, "raw teknical text")
        XCTAssertEqual(decoded.entries.first?.startSeconds, 1.25)
    }

    func testFinalDrainCaptionIsAcceptedWhileStopping() {
        var session = ClassroomSession()
        XCTAssertTrue(session.markListening())
        XCTAssertTrue(session.beginStopping())

        XCTAssertNotNil(session.finalizeCaption(
            "the final delayed words",
            correctionEnabled: false
        ))
        XCTAssertEqual(
            session.timeline.segments.last?.rawText,
            "the final delayed words"
        )
    }

    func testArchiveWritesAudioAndTranscriptFiles() async throws {
        let root = FileManager.default.temporaryDirectory.appendingPathComponent(
            UUID().uuidString,
            isDirectory: true
        )
        defer { try? FileManager.default.removeItem(at: root) }

        var session = ClassroomSession(
            id: UUID(uuidString: "11111111-2222-3333-4444-555555555555")!,
            startedAt: Date(timeIntervalSince1970: 2_000)
        )
        XCTAssertTrue(session.markListening())
        _ = session.finalizeCaption(
            "archive test",
            at: session.startedAt.addingTimeInterval(1),
            correctionEnabled: false
        )
        XCTAssertTrue(session.beginStopping())
        XCTAssertTrue(session.finish(at: session.startedAt.addingTimeInterval(2)))

        let service = SessionArchiveService()
        let directory = try await service.start(
            session: session,
            rootDirectory: root
        )
        service.appendAudio(Data([0, 0, 1, 0]))
        let finalizedDirectory = try await service.finalize(
            session: session,
            backend: "embedded",
            microphone: "Test Microphone",
            modelDelayMilliseconds: 480
        )

        XCTAssertEqual(finalizedDirectory, directory)
        let audio = try Data(
            contentsOf: directory.appendingPathComponent("audio.wav")
        )
        XCTAssertEqual(audio.count, 48)
        XCTAssertEqual(readUInt32(audio, at: 40), 4)
        XCTAssertTrue(FileManager.default.fileExists(
            atPath: directory.appendingPathComponent("transcript.txt").path
        ))
        XCTAssertTrue(FileManager.default.fileExists(
            atPath: directory.appendingPathComponent("transcript.json").path
        ))
        XCTAssertTrue(FileManager.default.fileExists(
            atPath: directory.appendingPathComponent("session.json").path
        ))
    }

    private func readUInt16(_ data: Data, at offset: Int) -> UInt16 {
        UInt16(data[offset]) | UInt16(data[offset + 1]) << 8
    }

    private func readUInt32(_ data: Data, at offset: Int) -> UInt32 {
        UInt32(data[offset])
            | UInt32(data[offset + 1]) << 8
            | UInt32(data[offset + 2]) << 16
            | UInt32(data[offset + 3]) << 24
    }

    func testWAVHeaderHandlesMaximumRIFFSize() {
        // The RIFF chunk-size field stores dataByteCount + 36; the largest
        // legal payload must not overflow UInt32 when the header is built.
        let header = PCM16WAVHeader.make(dataByteCount: UInt32.max - 36)
        XCTAssertEqual(header.count, PCM16WAVHeader.byteCount)
        let riffSize = header.subdata(in: 4..<8).withUnsafeBytes {
            $0.loadUnaligned(as: UInt32.self)
        }
        XCTAssertEqual(riffSize, UInt32.max)
    }
}


private extension JSONDecoder {
    static var iso8601: JSONDecoder {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }

}
