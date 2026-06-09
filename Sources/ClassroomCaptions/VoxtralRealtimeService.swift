import ClassroomCaptionsCore
import Foundation
import Synchronization

enum VoxtralRealtimeError: LocalizedError {
    case invalidEndpoint
    case invalidPayload

    var errorDescription: String? {
        switch self {
        case .invalidEndpoint:
            return "The Voxtral endpoint must use ws:// or wss://."
        case .invalidPayload:
            return "Unable to encode a Voxtral realtime request."
        }
    }
}

final class VoxtralRealtimeService: NSObject, StreamingTranscriptionService,
    URLSessionWebSocketDelegate, URLSessionTaskDelegate, @unchecked Sendable
{
    private enum ConnectionState {
        case disconnected
        case connecting
        case connected
    }

    private struct State {
        var connectionState: ConnectionState = .disconnected
        var session: URLSession?
        var task: URLSessionWebSocketTask?
        var continuation: AsyncStream<TranscriptionEvent>.Continuation?
        var model = ""
        var pendingFrames: [String] = []
        var sessionReady = false
        var hasUncommittedAudio = false
        var generationInProgress = false
        var provisionalText = ""
        var userInitiatedStop = false
    }

    private let state = Mutex(State())

    func events() -> AsyncStream<TranscriptionEvent> {
        AsyncStream { continuation in
            state.withLock { $0.continuation = continuation }
            continuation.onTermination = { [weak self] _ in
                self?.state.withLock { $0.continuation = nil }
            }
        }
    }

    func start(configuration: TranscriptionConfiguration) async throws {
        guard let scheme = configuration.endpoint.scheme?.lowercased(),
              scheme == "ws" || scheme == "wss" else {
            throw VoxtralRealtimeError.invalidEndpoint
        }

        await stop()
        var request = URLRequest(url: configuration.endpoint)
        request.timeoutInterval = 30
        request.setValue("realtime=v1", forHTTPHeaderField: "OpenAI-Beta")

        let sessionConfiguration = URLSessionConfiguration.default
        sessionConfiguration.waitsForConnectivity = true
        sessionConfiguration.timeoutIntervalForRequest = 30
        sessionConfiguration.timeoutIntervalForResource = 24 * 60 * 60
        let session = URLSession(
            configuration: sessionConfiguration,
            delegate: self,
            delegateQueue: nil
        )
        let task = session.webSocketTask(with: request)

        state.withLock { state in
            state.connectionState = .connecting
            state.session = session
            state.task = task
            state.model = configuration.model
            state.pendingFrames.removeAll(keepingCapacity: true)
            state.sessionReady = false
            state.hasUncommittedAudio = false
            state.generationInProgress = false
            state.provisionalText = ""
            state.userInitiatedStop = false
        }
        task.resume()
    }

    // Synchronous on purpose: callers on the capture queue rely on call order
    // matching frame order, and URLSessionWebSocketTask.send enqueues frames
    // in call order. (A synchronous method still satisfies the protocol's
    // async requirement.)
    func sendAudio(_ pcm16MonoData: Data) {
        guard !pcm16MonoData.isEmpty else { return }
        state.withLock { $0.hasUncommittedAudio = true }
        send([
            "type": "input_audio_buffer.append",
            "audio": pcm16MonoData.base64EncodedString(),
        ])
    }

    func commit() {
        let shouldCommit = state.withLock { state -> Bool in
            guard state.connectionState == .connected,
                  state.hasUncommittedAudio,
                  !state.generationInProgress else {
                return false
            }
            state.hasUncommittedAudio = false
            state.generationInProgress = true
            return true
        }
        guard shouldCommit else { return }
        send(["type": "input_audio_buffer.commit"])
    }

    func stop() async {
        let resources = state.withLock { state -> (URLSessionWebSocketTask?, URLSession?) in
            state.userInitiatedStop = true
            let resources = (state.task, state.session)
            reset(&state, preserveContinuation: true)
            return resources
        }
        resources.0?.cancel(with: .normalClosure, reason: nil)
        resources.1?.invalidateAndCancel()
    }

    func urlSession(
        _: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didOpenWithProtocol _: String?
    ) {
        let isCurrent = state.withLock { state -> Bool in
            guard state.task === webSocketTask else { return false }
            state.connectionState = .connected
            return true
        }
        guard isCurrent else { return }
        emit(.connected)
        listen(on: webSocketTask)
    }

    func urlSession(
        _: URLSession,
        webSocketTask: URLSessionWebSocketTask,
        didCloseWith closeCode: URLSessionWebSocketTask.CloseCode,
        reason: Data?
    ) {
        let reasonText = reason.flatMap { String(data: $0, encoding: .utf8) }
        handleTerminal(
            task: webSocketTask,
            message: closeCode == .normalClosure || closeCode == .goingAway
                ? nil
                : "Voxtral connection closed (\(closeCode.rawValue)): \(reasonText ?? "no reason")"
        )
    }

    func urlSession(_: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        guard let webSocketTask = task as? URLSessionWebSocketTask else { return }
        let nsError = error as NSError?
        let isCancellation = nsError?.domain == NSURLErrorDomain
            && nsError?.code == NSURLErrorCancelled
        handleTerminal(
            task: webSocketTask,
            message: isCancellation ? nil : error?.localizedDescription
        )
    }

    private func listen(on task: URLSessionWebSocketTask) {
        task.receive { [weak self] result in
            guard let self else { return }
            switch result {
            case .success(let message):
                self.handle(message)
                let isCurrent = self.state.withLock {
                    $0.connectionState == .connected && $0.task === task
                }
                if isCurrent {
                    self.listen(on: task)
                }
            case .failure(let error):
                self.handleTerminal(task: task, message: error.localizedDescription)
            }
        }
    }

    private func handle(_ message: URLSessionWebSocketTask.Message) {
        let data: Data?
        switch message {
        case .string(let text):
            data = text.data(using: .utf8)
        case .data(let binary):
            data = binary
        @unknown default:
            data = nil
        }
        guard let data,
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return
        }
        handle(json)
    }

    func handle(_ json: [String: Any]) {
        let type = json["type"] as? String ?? ""
        switch type {
        case "session.created":
            let startup = state.withLock { state -> (String, [String])? in
                guard !state.sessionReady else { return nil }
                state.sessionReady = true
                let frames = state.pendingFrames
                state.pendingFrames.removeAll(keepingCapacity: true)
                return (state.model, frames)
            }
            guard let startup else { return }
            if !startup.0.isEmpty {
                send(["type": "session.update", "model": startup.0])
            }
            startup.1.forEach(sendText)

        case "transcription.delta",
            "response.audio_transcript.delta",
            "conversation.item.input_audio_transcription.delta":
            guard let delta = findString(in: json, keys: ["delta", "text", "transcript"])
            else {
                return
            }
            let provisional = state.withLock { state in
                state.provisionalText.append(delta)
                return state.provisionalText
            }
            emit(.provisional(provisional))

        case "transcription.done",
            "response.audio_transcript.done",
            "conversation.item.input_audio_transcription.completed":
            let text = findString(in: json, keys: ["text", "transcript", "delta"])
            let finalized = state.withLock { state -> String in
                state.generationInProgress = false
                defer { state.provisionalText = "" }
                return text?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false
                    ? text!
                    : state.provisionalText
            }
            if !finalized.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                emit(.finalized(finalized))
            }

        case "error":
            state.withLock { $0.generationInProgress = false }
            emit(.failed(
                findString(in: json, keys: ["message", "error", "detail"])
                    ?? "Unknown Voxtral realtime error."
            ))
        default:
            break
        }
    }

    private func send(_ event: [String: Any]) {
        guard JSONSerialization.isValidJSONObject(event),
              let data = try? JSONSerialization.data(withJSONObject: event),
              let text = String(data: data, encoding: .utf8) else {
            emit(.failed(VoxtralRealtimeError.invalidPayload.localizedDescription))
            return
        }
        sendText(text)
    }

    private func sendText(_ text: String) {
        let task = state.withLock { state -> URLSessionWebSocketTask? in
            guard state.connectionState == .connected else { return nil }
            guard state.sessionReady else {
                state.pendingFrames.append(text)
                return nil
            }
            return state.task
        }
        task?.send(.string(text)) { [weak self, weak task] error in
            guard let self, let task, let error else { return }
            self.handleTerminal(task: task, message: error.localizedDescription)
        }
    }

    private func handleTerminal(task: URLSessionWebSocketTask, message: String?) {
        let outcome = state.withLock { state -> (Bool, String?) in
            guard state.task === task, state.connectionState != .disconnected else {
                return (false, nil)
            }
            let userInitiated = state.userInitiatedStop
            let session = state.session
            reset(&state, preserveContinuation: true)
            session?.invalidateAndCancel()
            return (true, userInitiated ? nil : message)
        }
        guard outcome.0 else { return }
        if let message = outcome.1 {
            emit(.failed(message))
        }
        emit(.disconnected)
    }

    private func emit(_ event: TranscriptionEvent) {
        state.withLock { $0.continuation }?.yield(event)
    }

    private func reset(_ state: inout State, preserveContinuation: Bool) {
        let continuation = state.continuation
        state = State()
        if preserveContinuation {
            state.continuation = continuation
        }
    }

    func findString(in value: Any, keys: [String]) -> String? {
        if let dictionary = value as? [String: Any] {
            for key in keys {
                if let text = dictionary[key] as? String, !text.isEmpty {
                    return text
                }
            }
            for nested in dictionary.values {
                if let match = findString(in: nested, keys: keys) {
                    return match
                }
            }
        } else if let array = value as? [Any] {
            for nested in array {
                if let match = findString(in: nested, keys: keys) {
                    return match
                }
            }
        }
        return nil
    }
}
