import ClassroomCaptionsCore
import XCTest

final class ClassroomSessionTests: XCTestCase {
    func testSessionLifecycle() {
        var session = ClassroomSession()

        XCTAssertEqual(session.phase, .starting)
        XCTAssertTrue(session.markListening())
        XCTAssertTrue(session.pause())
        XCTAssertTrue(session.markListening())
        XCTAssertTrue(session.beginStopping())
        XCTAssertTrue(session.finish())
        XCTAssertEqual(session.phase, .idle)
        XCTAssertNotNil(session.endedAt)
    }

    func testCaptionsAreAcceptedOnlyWhileListening() {
        var session = ClassroomSession()
        XCTAssertNil(session.finalizeCaption("ignored", correctionEnabled: false))

        XCTAssertTrue(session.markListening())
        XCTAssertNotNil(session.finalizeCaption("accepted", correctionEnabled: false))
        XCTAssertTrue(session.pause())
        XCTAssertNil(session.finalizeCaption("ignored again", correctionEnabled: false))
        XCTAssertEqual(session.timeline.segments.map(\.rawText), ["accepted"])
    }
}
