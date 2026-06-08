import AppKit
@testable import ClassroomCaptions
import XCTest

@MainActor
final class CaptionOverlayGeometryTests: XCTestCase {
    func testClampKeepsFrameInsideVisibleDisplay() {
        let visible = NSRect(x: -1_920, y: 40, width: 1_920, height: 1_040)
        let frame = NSRect(x: -2_400, y: -200, width: 900, height: 220)

        let result = CaptionOverlayController.clamped(frame, to: visible)

        XCTAssertGreaterThanOrEqual(result.minX, visible.minX + 12)
        XCTAssertGreaterThanOrEqual(result.minY, visible.minY + 12)
        XCTAssertLessThanOrEqual(result.maxX, visible.maxX - 12)
        XCTAssertLessThanOrEqual(result.maxY, visible.maxY - 12)
    }

    func testClampEnforcesMinimumSize() {
        let visible = NSRect(x: 0, y: 24, width: 1_440, height: 876)
        let frame = NSRect(x: 300, y: 300, width: 40, height: 20)

        let result = CaptionOverlayController.clamped(frame, to: visible)

        XCTAssertEqual(result.width, 420)
        XCTAssertEqual(result.height, 120)
    }

    func testClampShrinksFrameThatExceedsDisplay() {
        let visible = NSRect(x: 0, y: 24, width: 800, height: 576)
        let frame = NSRect(x: -100, y: -100, width: 2_000, height: 1_000)

        let result = CaptionOverlayController.clamped(frame, to: visible)

        XCTAssertEqual(result.width, 776)
        XCTAssertEqual(result.height, 552)
        XCTAssertEqual(result.minX, 12)
        XCTAssertEqual(result.minY, 36)
    }
}
