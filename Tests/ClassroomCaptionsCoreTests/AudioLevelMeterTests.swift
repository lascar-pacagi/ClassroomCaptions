import ClassroomCaptionsCore
import Foundation
import XCTest

final class AudioLevelMeterTests: XCTestCase {
    func testSilenceProducesZeroLevel() {
        let data = pcmData([0, 0, 0, 0])
        let reading = PCM16LevelMeter.measure(data)

        XCTAssertEqual(reading.rms, 0)
        XCTAssertEqual(reading.peak, 0)
        XCTAssertEqual(reading.normalizedLevel, 0)
    }

    func testPeakAndRMSUseNormalizedPCMValues() {
        let data = pcmData([Int16.max, 0, -Int16.max, 0])
        let reading = PCM16LevelMeter.measure(data)

        XCTAssertEqual(reading.peak, 1, accuracy: 0.0001)
        XCTAssertEqual(reading.rms, sqrt(0.5), accuracy: 0.0001)
        XCTAssertGreaterThan(reading.normalizedLevel, 0.9)
    }

    func testOddTrailingByteIsIgnored() {
        var data = pcmData([Int16.max])
        data.append(0x7f)

        XCTAssertEqual(PCM16LevelMeter.measure(data).peak, 1, accuracy: 0.0001)
    }

    private func pcmData(_ samples: [Int16]) -> Data {
        samples.withUnsafeBytes { Data($0) }
    }
}
