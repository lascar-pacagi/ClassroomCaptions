import ClassroomCaptionsCore
import XCTest

final class CaptionTimelineTests: XCTestCase {
    func testFinalizePreservesRawTextDuringCorrection() {
        var timeline = CaptionTimeline()
        let id = UUID()
        timeline.updateProvisional("raw teknical text")
        timeline.finalize("raw teknical text", correctionEnabled: true, id: id)

        XCTAssertTrue(timeline.beginCorrection(segmentID: id))
        XCTAssertTrue(timeline.applyCorrection(segmentID: id, text: "raw technical text"))
        XCTAssertEqual(timeline.segments[0].rawText, "raw teknical text")
        XCTAssertEqual(timeline.segments[0].displayText, "raw technical text")
    }

    func testFailedCorrectionLeavesRawCaptionVisible() {
        var timeline = CaptionTimeline()
        let id = UUID()
        timeline.finalize("important raw caption", correctionEnabled: true, id: id)

        XCTAssertTrue(timeline.beginCorrection(segmentID: id))
        XCTAssertTrue(timeline.failCorrection(segmentID: id, message: "timeout"))
        XCTAssertEqual(timeline.segments[0].displayText, "important raw caption")
        XCTAssertEqual(timeline.segments[0].correctionState, .failed)
    }

    func testSequenceRemainsMonotonicAfterProvisionalUpdates() {
        var timeline = CaptionTimeline()
        timeline.updateProvisional("one")
        timeline.finalize("one", correctionEnabled: false)
        timeline.updateProvisional("two")
        timeline.updateProvisional("two revised")
        timeline.finalize("two revised", correctionEnabled: false)

        XCTAssertEqual(timeline.segments.map(\.sequence), [0, 1])
        XCTAssertEqual(timeline.segments.map(\.rawText), ["one", "two revised"])
    }
}
