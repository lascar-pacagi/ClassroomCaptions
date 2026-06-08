import XCTest
@testable import ClassroomCaptions

final class VoxtralProtocolTests: XCTestCase {
    func testFindStringUsesRequestedKeyPriority() {
        let service = VoxtralRealtimeService()
        let value: [String: Any] = [
            "text": "fallback",
            "nested": ["delta": "preferred"],
        ]

        XCTAssertEqual(
            service.findString(in: value, keys: ["delta", "text"]),
            "fallback"
        )
    }

    func testNestedTranscriptIsFound() {
        let service = VoxtralRealtimeService()
        let value: [String: Any] = [
            "response": [
                "items": [
                    ["transcript": "nested transcript"]
                ]
            ]
        ]

        XCTAssertEqual(
            service.findString(in: value, keys: ["text", "transcript"]),
            "nested transcript"
        )
    }
}
