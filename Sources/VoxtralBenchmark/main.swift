import CVoxtralEngine
import Foundation

private struct Arguments {
    let modelDirectory: String
    let audioPath: String
    let referencePath: String?
    let delayMilliseconds: Int32
    let processingInterval: Float
    let chunkMilliseconds: Int
    let prerollMilliseconds: Int
    let simulateRealtime: Bool
}

private struct PCMRecording {
    let samples: [Int16]
    let sampleRate: Int

    var duration: TimeInterval {
        Double(samples.count) / Double(sampleRate)
    }
}

private enum BenchmarkError: LocalizedError {
    case usage(String)
    case invalidWAV(String)
    case engine(String)

    var errorDescription: String? {
        switch self {
        case .usage(let message), .invalidWAV(let message), .engine(let message):
            return message
        }
    }
}

private func parseArguments() throws -> Arguments {
    var values = Array(CommandLine.arguments.dropFirst())
    func take(_ flag: String) throws -> String {
        guard let index = values.firstIndex(of: flag), index + 1 < values.count else {
            throw BenchmarkError.usage("Missing \(flag).")
        }
        let value = values[index + 1]
        values.removeSubrange(index ... index + 1)
        return value
    }

    let modelDirectory = try take("--model-dir")
    let audioPath = try take("--audio")
    let referencePath: String?
    if values.contains("--reference") {
        referencePath = try take("--reference")
    } else {
        referencePath = nil
    }
    let delay = values.contains("--delay-ms")
        ? Int32(try take("--delay-ms")) ?? 320 : 320
    let interval = values.contains("--interval")
        ? Float(try take("--interval")) ?? 1.0 : 1.0
    let chunk = values.contains("--chunk-ms")
        ? Int(try take("--chunk-ms")) ?? 100 : 100
    let preroll = values.contains("--preroll-ms")
        ? Int(try take("--preroll-ms")) ?? 0 : 0
    let realtime = values.contains("--realtime")
    values.removeAll(where: { $0 == "--realtime" })
    guard values.isEmpty else {
        throw BenchmarkError.usage("Unknown arguments: \(values.joined(separator: " "))")
    }

    return Arguments(
        modelDirectory: modelDirectory,
        audioPath: audioPath,
        referencePath: referencePath,
        delayMilliseconds: delay,
        processingInterval: interval,
        chunkMilliseconds: chunk,
        prerollMilliseconds: max(0, preroll),
        simulateRealtime: realtime
    )
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

private func loadPCMRecording(path: String) throws -> PCMRecording {
    let data = try Data(contentsOf: URL(fileURLWithPath: path))
    guard data.count >= 44,
          String(data: data[0 ..< 4], encoding: .ascii) == "RIFF",
          String(data: data[8 ..< 12], encoding: .ascii) == "WAVE" else {
        throw BenchmarkError.invalidWAV("Audio must be a RIFF/WAVE file.")
    }

    var format: UInt16?
    var channels: UInt16?
    var sampleRate: UInt32?
    var bitsPerSample: UInt16?
    var pcmRange: Range<Int>?
    var offset = 12
    while offset + 8 <= data.count {
        let identifier = String(data: data[offset ..< offset + 4], encoding: .ascii) ?? ""
        let size = Int(readUInt32(data, at: offset + 4))
        let payloadStart = offset + 8
        let payloadEnd = payloadStart + size
        guard payloadEnd <= data.count else { break }

        if identifier == "fmt ", size >= 16 {
            format = readUInt16(data, at: payloadStart)
            channels = readUInt16(data, at: payloadStart + 2)
            sampleRate = readUInt32(data, at: payloadStart + 4)
            bitsPerSample = readUInt16(data, at: payloadStart + 14)
        } else if identifier == "data" {
            pcmRange = payloadStart ..< payloadEnd
        }
        offset = payloadEnd + (size % 2)
    }

    guard format == 1, channels == 1, sampleRate == 16_000,
          bitsPerSample == 16, let pcmRange else {
        throw BenchmarkError.invalidWAV(
            "Audio must be uncompressed 16-bit, 16 kHz, mono PCM WAV."
        )
    }

    let pcm = data[pcmRange]
    let samples = pcm.withUnsafeBytes { rawBuffer in
        Array(rawBuffer.bindMemory(to: Int16.self))
    }
    return PCMRecording(samples: samples, sampleRate: 16_000)
}

private func drainText(
    stream: OpaquePointer,
    transcript: inout String
) throws -> Bool {
    var emitted = false
    while true {
        var required = 0
        var buffer = [CChar](repeating: 0, count: 256)
        var status = ccv_stream_read_text(stream, &buffer, buffer.count, &required)
        if status == CCV_STATUS_BUFFER_TOO_SMALL {
            buffer = [CChar](repeating: 0, count: required)
            status = ccv_stream_read_text(stream, &buffer, buffer.count, &required)
        }
        if status == CCV_STATUS_NO_TEXT {
            return emitted
        }
        guard status == CCV_STATUS_OK else {
            throw BenchmarkError.engine(String(cString: ccv_status_description(status)))
        }

        let terminator = buffer.firstIndex(of: 0) ?? buffer.endIndex
        let token = String(decoding: buffer[..<terminator].map(UInt8.init), as: UTF8.self)
        transcript.append(token)
        print(token, terminator: "")
        fflush(stdout)
        emitted = true
    }
}

private func words(_ text: String) -> [String] {
    text.lowercased()
        .split { !$0.isLetter && !$0.isNumber }
        .map(String.init)
}

private func wordAccuracy(reference: String, transcript: String) -> Double {
    let lhs = words(reference)
    let rhs = words(transcript)
    guard !lhs.isEmpty else { return rhs.isEmpty ? 1 : 0 }

    var previous = Array(0 ... rhs.count)
    for (leftIndex, left) in lhs.enumerated() {
        var current = [Int](repeating: 0, count: rhs.count + 1)
        current[0] = leftIndex + 1
        for (rightIndex, right) in rhs.enumerated() {
            current[rightIndex + 1] = min(
                previous[rightIndex + 1] + 1,
                current[rightIndex] + 1,
                previous[rightIndex] + (left == right ? 0 : 1)
            )
        }
        previous = current
    }
    return max(0, 1 - Double(previous[rhs.count]) / Double(lhs.count))
}

private func run() throws {
    let arguments = try parseArguments()
    let recording = try loadPCMRecording(path: arguments.audioPath)

    var status = CCV_STATUS_OK
    var errorBuffer = [CChar](repeating: 0, count: 512)
    let loadStarted = ContinuousClock.now
    guard let model = ccv_model_load(
        arguments.modelDirectory,
        &status,
        &errorBuffer,
        errorBuffer.count
    ) else {
        let terminator = errorBuffer.firstIndex(of: 0) ?? errorBuffer.endIndex
        throw BenchmarkError.engine(
            String(decoding: errorBuffer[..<terminator].map(UInt8.init), as: UTF8.self)
        )
    }
    let loadDuration = ContinuousClock.now - loadStarted
    defer { ccv_model_free(model) }

    var options = ccv_stream_options_default()
    options.delay_ms = arguments.delayMilliseconds
    options.processing_interval_seconds = arguments.processingInterval
    guard let stream = ccv_stream_create(
        model,
        options,
        &status,
        &errorBuffer,
        errorBuffer.count
    ) else {
        throw BenchmarkError.engine("Unable to create benchmark stream.")
    }
    defer { ccv_stream_free(stream) }

    let chunkSamples = max(1, 16_000 * arguments.chunkMilliseconds / 1_000)
    if arguments.prerollMilliseconds > 0 {
        var remaining = 16_000 * arguments.prerollMilliseconds / 1_000
        let silence = [Int16](repeating: 0, count: chunkSamples)
        var discardedText = ""
        while remaining > 0 {
            let count = min(remaining, silence.count)
            let status = silence.withUnsafeBufferPointer {
                ccv_stream_feed_pcm16(stream, $0.baseAddress, count)
            }
            guard status == CCV_STATUS_OK else {
                throw BenchmarkError.engine(String(cString: ccv_status_description(status)))
            }
            _ = try drainText(stream: stream, transcript: &discardedText)
            remaining -= count
        }
    }

    let inferenceStarted = ContinuousClock.now
    let realtimeStarted = Date()
    var firstTokenDuration: Duration?
    var transcript = ""
    var offset = 0
    while offset < recording.samples.count {
        let end = min(offset + chunkSamples, recording.samples.count)
        let chunk = recording.samples[offset ..< end]
        let feedStatus = chunk.withUnsafeBufferPointer {
            ccv_stream_feed_pcm16(stream, $0.baseAddress, $0.count)
        }
        guard feedStatus == CCV_STATUS_OK else {
            throw BenchmarkError.engine(String(cString: ccv_status_description(feedStatus)))
        }
        if try drainText(stream: stream, transcript: &transcript),
           firstTokenDuration == nil {
            firstTokenDuration = ContinuousClock.now - inferenceStarted
        }
        if arguments.simulateRealtime {
            let targetElapsed = Double(end) / 16_000
            let remaining = targetElapsed - Date().timeIntervalSince(realtimeStarted)
            if remaining > 0 {
                Thread.sleep(forTimeInterval: remaining)
            }
        }
        offset = end
    }

    guard ccv_stream_finish(stream) == CCV_STATUS_OK else {
        throw BenchmarkError.engine("Unable to finish the benchmark stream.")
    }
    if try drainText(stream: stream, transcript: &transcript),
       firstTokenDuration == nil {
        firstTokenDuration = ContinuousClock.now - inferenceStarted
    }
    let inferenceDuration = ContinuousClock.now - inferenceStarted
    print()

    let loadSeconds = Double(loadDuration.components.seconds)
        + Double(loadDuration.components.attoseconds) / 1e18
    let inferenceSeconds = Double(inferenceDuration.components.seconds)
        + Double(inferenceDuration.components.attoseconds) / 1e18
    let firstTokenSeconds = firstTokenDuration.map {
        Double($0.components.seconds) + Double($0.components.attoseconds) / 1e18
    }

    print("model_load_seconds=\(String(format: "%.3f", loadSeconds))")
    print("audio_seconds=\(String(format: "%.3f", recording.duration))")
    print("inference_seconds=\(String(format: "%.3f", inferenceSeconds))")
    print("realtime_factor=\(String(format: "%.4f", inferenceSeconds / recording.duration))")
    if let firstTokenSeconds {
        print("first_token_seconds=\(String(format: "%.3f", firstTokenSeconds))")
    }
    print("transcript=\(transcript.trimmingCharacters(in: .whitespacesAndNewlines))")

    if let referencePath = arguments.referencePath {
        let reference = try String(
            contentsOfFile: referencePath,
            encoding: .utf8
        )
        let accuracy = wordAccuracy(
            reference: reference,
            transcript: transcript
        )
        print("word_accuracy=\(String(format: "%.4f", accuracy))")
    }
}

do {
    try run()
} catch {
    fputs("error: \(error.localizedDescription)\n", stderr)
    fputs(
        "usage: VoxtralBenchmark --model-dir DIR --audio FILE.wav "
            + "[--reference FILE.txt] [--delay-ms 320] [--interval 1.0] "
            + "[--chunk-ms 100] [--preroll-ms 0] [--realtime]\n",
        stderr
    )
    exit(1)
}
