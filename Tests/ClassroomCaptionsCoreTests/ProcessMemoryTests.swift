@testable import ClassroomCaptions
import Darwin
import XCTest

final class ProcessMemoryTests: XCTestCase {
    func testReadsCurrentProcessResidentMemory() {
        let footprint = ProcessMemory.physicalFootprintBytes(
            processID: getpid()
        )

        XCTAssertNotNil(footprint)
        XCTAssertGreaterThan(footprint ?? 0, 0)
    }
}
