import ClassroomCaptionsCore
import CVoxtralEngine
import Foundation
import Synchronization

enum VoxtralEmbeddedError: LocalizedError {
    case engine(status: ccv_status_t, message: String)

    var errorDescription: String? {
        switch self {
        case .engine(_, let message):
            return message
        }
    }
}

final class VoxtralEmbeddedService: @unchecked Sendable {
    private static let startupPrerollSamples = 16_000 * 32 / 10

    private struct State: @unchecked Sendable {
        var model: OpaquePointer?
        var stream: OpaquePointer?
        var continuation: AsyncStream<TranscriptionEvent>.Continuation?
        var provisionalText = ""
        var isRunning = false
    }

    private let state = Mutex(State())
    private let inferenceQueue = DispatchQueue(
        label: "ClassroomCaptions.voxtral.inference",
        qos: .userInitiated
    )

    func events() -> AsyncStream<TranscriptionEvent> {
        AsyncStream { continuation in
            state.withLock { $0.continuation = continuation }
            continuation.onTermination = { [weak self] _ in
                self?.state.withLock { $0.continuation = nil }
            }
        }
    }

    func start(
        modelDirectory: URL,
        delayMilliseconds: Int,
        processingIntervalSeconds: Float,
        maxDecodeContextTokens: Int
    ) async throws {
        _ = await stop()
        try await withCheckedThrowingContinuation {
            (continuation: CheckedContinuation<Void, Error>) in
            inferenceQueue.async { [weak self] in
                guard let self else {
                    continuation.resume(throwing: CancellationError())
                    return
                }

                var status = CCV_STATUS_OK
                var errorBuffer = [CChar](repeating: 0, count: 512)
                let model = ccv_model_load(
                    modelDirectory.path,
                    &status,
                    &errorBuffer,
                    errorBuffer.count
                )
                guard let model else {
                    continuation.resume(throwing: self.makeError(
                        status: status,
                        buffer: errorBuffer
                    ))
                    return
                }

                var options = ccv_stream_options_default()
                options.delay_ms = Int32(delayMilliseconds)
                options.processing_interval_seconds = processingIntervalSeconds
                options.continuous = 1
                options.max_decode_context_tokens = Int32(maxDecodeContextTokens)

                let stream = ccv_stream_create(
                    model,
                    options,
                    &status,
                    &errorBuffer,
                    errorBuffer.count
                )
                guard let stream else {
                    ccv_model_free(model)
                    continuation.resume(throwing: self.makeError(
                        status: status,
                        buffer: errorBuffer
                    ))
                    return
                }

                self.state.withLock { state in
                    state.model = model
                    state.stream = stream
                    state.provisionalText = ""
                    state.isRunning = true
                }
                do {
                    try self.primeDecoderWithSilence(stream)
                } catch {
                    self.state.withLock { state in
                        state.model = nil
                        state.stream = nil
                        state.isRunning = false
                    }
                    ccv_stream_free(stream)
                    ccv_model_free(model)
                    continuation.resume(throwing: error)
                    return
                }
                self.emit(.connected)
                continuation.resume()
            }
        }
    }

    func sendAudio(_ pcm16MonoData: Data) {
        guard !pcm16MonoData.isEmpty else { return }
        inferenceQueue.async { [weak self] in
            guard let self,
                  let stream = self.state.withLock({ $0.stream }) else {
                return
            }

            let status = pcm16MonoData.withUnsafeBytes { bytes -> ccv_status_t in
                let samples = bytes.bindMemory(to: Int16.self)
                guard let baseAddress = samples.baseAddress, !samples.isEmpty else {
                    return CCV_STATUS_INVALID_ARGUMENT
                }
                return ccv_stream_feed_pcm16(
                    stream,
                    baseAddress,
                    samples.count
                )
            }
            if status == CCV_STATUS_OK {
                self.drainText(from: stream)
            } else if status != CCV_STATUS_CANCELLED {
                self.emit(.failed(self.statusMessage(status)))
            }
        }
    }

    func flush(finalizeCaption: Bool) async {
        await withCheckedContinuation { continuation in
            inferenceQueue.async { [weak self] in
                guard let self,
                      let stream = self.state.withLock({ $0.stream }) else {
                    continuation.resume()
                    return
                }

                let status = ccv_stream_flush(stream)
                if status == CCV_STATUS_OK {
                    self.drainText(from: stream)
                    if finalizeCaption {
                        if let text = self.takeFinalizedProvisional() {
                            self.emit(.finalized(text))
                        }
                    }
                } else if status != CCV_STATUS_CANCELLED {
                    self.emit(.failed(self.statusMessage(status)))
                }
                continuation.resume()
            }
        }
    }

    func stop() async -> String? {
        await withCheckedContinuation { continuation in
            inferenceQueue.async { [weak self] in
                guard let self else {
                    continuation.resume(returning: nil)
                    return
                }

                let resources = self.state.withLock {
                    state -> (OpaquePointer?, OpaquePointer?, Bool) in
                    let resources = (state.stream, state.model)
                    state.stream = nil
                    state.model = nil
                    let wasRunning = state.isRunning
                    state.isRunning = false
                    return (resources.0, resources.1, wasRunning)
                }

                if let stream = resources.0 {
                    let status = ccv_stream_finish(stream)
                    if status == CCV_STATUS_OK {
                        self.drainText(from: stream)
                    } else if status != CCV_STATUS_STREAM_FINISHED,
                              status != CCV_STATUS_CANCELLED {
                        self.emit(.failed(self.statusMessage(status)))
                    }
                    ccv_stream_free(stream)
                }
                if let model = resources.1 {
                    ccv_model_free(model)
                }
                let finalizedText = self.takeFinalizedProvisional()
                if resources.2 {
                    self.emit(.disconnected)
                }
                continuation.resume(returning: finalizedText)
            }
        }
    }

    private func drainText(from stream: OpaquePointer) {
        while true {
            var requiredCapacity = 0
            var buffer = [CChar](repeating: 0, count: 256)
            var status = ccv_stream_read_text(
                stream,
                &buffer,
                buffer.count,
                &requiredCapacity
            )
            if status == CCV_STATUS_BUFFER_TOO_SMALL {
                buffer = [CChar](repeating: 0, count: requiredCapacity)
                status = ccv_stream_read_text(
                    stream,
                    &buffer,
                    buffer.count,
                    &requiredCapacity
                )
            }

            guard status == CCV_STATUS_OK else {
                if status != CCV_STATUS_NO_TEXT {
                    emit(.failed(statusMessage(status)))
                }
                return
            }

            let terminator = buffer.firstIndex(of: 0) ?? buffer.endIndex
            let token = String(
                decoding: buffer[..<terminator].map(UInt8.init),
                as: UTF8.self
            )
            guard !token.isEmpty else { continue }
            let provisional = state.withLock { state -> String in
                state.provisionalText.append(token)
                return state.provisionalText
            }
            let totalTokens = Int(ccv_stream_text_tokens_generated(stream))
            let decoderSeconds = ccv_stream_decoder_milliseconds(stream) / 1_000
            emit(.tokenMetrics(GenerationTokenMetrics(
                totalTokens: totalTokens,
                tokensPerSecond: decoderSeconds > 0
                    ? Double(totalTokens) / decoderSeconds
                    : 0
            )))
            emit(.provisional(provisional))
        }
    }

    private func primeDecoderWithSilence(_ stream: OpaquePointer) throws {
        let silence = [Int16](
            repeating: 0,
            count: Self.startupPrerollSamples
        )
        let status = silence.withUnsafeBufferPointer {
            ccv_stream_feed_pcm16(stream, $0.baseAddress, $0.count)
        }
        guard status == CCV_STATUS_OK else {
            throw VoxtralEmbeddedError.engine(
                status: status,
                message: "Voxtral decoder warm-up failed: \(statusMessage(status))"
            )
        }
        discardPendingText(from: stream)
    }

    private func discardPendingText(from stream: OpaquePointer) {
        var buffer = [CChar](repeating: 0, count: 256)
        var requiredCapacity = 0
        while true {
            var status = ccv_stream_read_text(
                stream,
                &buffer,
                buffer.count,
                &requiredCapacity
            )
            if status == CCV_STATUS_BUFFER_TOO_SMALL {
                buffer = [CChar](repeating: 0, count: requiredCapacity)
                status = ccv_stream_read_text(
                    stream,
                    &buffer,
                    buffer.count,
                    &requiredCapacity
                )
            }
            guard status == CCV_STATUS_OK else { return }
        }
    }

    private func takeFinalizedProvisional() -> String? {
        let text = state.withLock { state -> String in
            let text = state.provisionalText
            state.provisionalText = ""
            return text
        }.trimmingCharacters(in: .whitespacesAndNewlines)
        return text.isEmpty ? nil : text
    }

    private func emit(_ event: TranscriptionEvent) {
        state.withLock { $0.continuation }?.yield(event)
    }

    private func makeError(
        status: ccv_status_t,
        buffer: [CChar]
    ) -> VoxtralEmbeddedError {
        let terminator = buffer.firstIndex(of: 0) ?? buffer.endIndex
        let detail = String(
            decoding: buffer[..<terminator].map(UInt8.init),
            as: UTF8.self
        )
        return .engine(
            status: status,
            message: detail.isEmpty ? statusMessage(status) : detail
        )
    }

    private func statusMessage(_ status: ccv_status_t) -> String {
        String(cString: ccv_status_description(status))
    }
}
