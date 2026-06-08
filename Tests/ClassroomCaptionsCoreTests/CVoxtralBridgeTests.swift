import CVoxtralEngine
import XCTest

final class CVoxtralBridgeTests: XCTestCase {
    func testDefaultOptionsAreSuitableForRealtimeCaptions() {
        let options = ccv_stream_options_default()

        XCTAssertEqual(options.delay_ms, 320)
        XCTAssertEqual(options.processing_interval_seconds, 1.0, accuracy: 0.001)
        XCTAssertEqual(options.continuous, 1)
        XCTAssertEqual(options.max_decode_context_tokens, 2_000)
    }

    func testMissingModelDirectoryReturnsStructuredError() {
        var status = CCV_STATUS_OK
        var error = [CChar](repeating: 0, count: 256)

        let model = ccv_model_load(
            "/definitely/missing/classroom-voxtral-model",
            &status,
            &error,
            error.count
        )

        XCTAssertNil(model)
        XCTAssertEqual(status, CCV_STATUS_MODEL_FILES_MISSING)
        let terminator = error.firstIndex(of: 0) ?? error.endIndex
        let message = String(decoding: error[..<terminator].map(UInt8.init), as: UTF8.self)
        XCTAssertTrue(message.contains("consolidated.safetensors"))
    }

    func testPinnedRevisionIsExposed() {
        XCTAssertEqual(
            String(cString: ccv_upstream_revision()),
            "134d366c24d20c64b614a3dcc8bda2a6922d077d"
        )
    }
}
