import ClassroomCaptionsCore
import XCTest

final class CaptionTransformationTests: XCTestCase {
    func testIdenticalCaptionHasZeroPercentTransformation() {
        XCTAssertEqual(
            CaptionTransformation.percentage(from: "O(n)", to: "O(n)"),
            0
        )
    }

    func testCompletelyDifferentSameLengthCaptionHasFullTransformation() {
        XCTAssertEqual(
            CaptionTransformation.percentage(from: "abc", to: "xyz"),
            100
        )
    }

    func testReportsPartialCharacterTransformation() {
        XCTAssertEqual(
            CaptionTransformation.percentage(from: "chat", to: "chats"),
            20,
            accuracy: 0.001
        )
    }
}
