import Foundation

enum GemmaServerError: LocalizedError {
    case executableMissing(String)
    case launchFailed(String)
    case unavailable

    var errorDescription: String? {
        switch self {
        case .executableMissing(let path):
            return "MLX-LM server executable not found at \(path)."
        case .launchFailed(let message):
            return "Could not launch the Gemma server: \(message)"
        case .unavailable:
            return "Gemma did not become ready before the startup timeout."
        }
    }
}

@MainActor
final class GemmaServerController {
    private var process: Process?
    private let healthSession: URLSession

    init() {
        let configuration = URLSessionConfiguration.ephemeral
        configuration.timeoutIntervalForRequest = 1
        configuration.timeoutIntervalForResource = 2
        healthSession = URLSession(configuration: configuration)
    }

    func ensureReady(
        executablePath: String,
        modelPath: String,
        endpoint: URL
    ) async throws {
        if await isHealthy(endpoint: endpoint) {
            return
        }
        if process?.isRunning != true {
            try launch(
                executablePath: executablePath,
                modelPath: modelPath,
                endpoint: endpoint
            )
        }

        let deadline = ContinuousClock.now + .seconds(45)
        while ContinuousClock.now < deadline {
            if await isHealthy(endpoint: endpoint) {
                return
            }
            if let process, !process.isRunning {
                throw GemmaServerError.launchFailed(
                    "process exited with status \(process.terminationStatus)"
                )
            }
            try await Task.sleep(for: .milliseconds(250))
        }
        throw GemmaServerError.unavailable
    }

    func stop() {
        guard let process, process.isRunning else {
            self.process = nil
            return
        }
        process.terminate()
        self.process = nil
    }

    func processIdentifier(endpoint: URL) -> pid_t? {
        if let process, process.isRunning {
            return process.processIdentifier
        }
        guard let port = endpoint.port else { return nil }

        let lookup = Process()
        let output = Pipe()
        lookup.executableURL = URL(fileURLWithPath: "/usr/sbin/lsof")
        lookup.arguments = [
            "-nP", "-tiTCP:\(port)", "-sTCP:LISTEN",
        ]
        lookup.standardOutput = output
        lookup.standardError = FileHandle.nullDevice
        do {
            try lookup.run()
            lookup.waitUntilExit()
            guard lookup.terminationStatus == 0 else { return nil }
            let data = output.fileHandleForReading.readDataToEndOfFile()
            let value = String(data: data, encoding: .utf8)?
                .split(whereSeparator: \.isNewline)
                .first
            return value.flatMap { pid_t($0) }
        } catch {
            return nil
        }
    }

    private func launch(
        executablePath: String,
        modelPath: String,
        endpoint: URL
    ) throws {
        guard FileManager.default.isExecutableFile(atPath: executablePath) else {
            throw GemmaServerError.executableMissing(executablePath)
        }
        guard let host = endpoint.host, let port = endpoint.port else {
            throw GemmaCorrectionError.invalidEndpoint
        }

        let process = Process()
        process.executableURL = URL(fileURLWithPath: executablePath)
        process.arguments = [
            "--model", modelPath,
            "--host", host,
            "--port", String(port),
            "--temp", "0",
            "--max-tokens", "384",
            "--chat-template-args", #"{"enable_thinking":false}"#,
            "--decode-concurrency", "1",
            "--prompt-concurrency", "1",
            "--prompt-cache-size", "4",
            "--log-level", "WARNING",
        ]
        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice
        process.terminationHandler = { _ in }
        do {
            try process.run()
        } catch {
            throw GemmaServerError.launchFailed(error.localizedDescription)
        }
        self.process = process
    }

    private func isHealthy(endpoint: URL) async -> Bool {
        let url = endpoint.appendingPathComponent("v1/models")
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        do {
            let (_, response) = try await healthSession.data(for: request)
            return (response as? HTTPURLResponse).map {
                (200 ..< 300).contains($0.statusCode)
            } ?? false
        } catch {
            return false
        }
    }
}
