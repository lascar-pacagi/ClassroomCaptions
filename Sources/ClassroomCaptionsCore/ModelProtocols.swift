import Foundation

public enum TranscriptionEvent: Equatable, Sendable {
    case connected
    case provisional(String)
    case finalized(String)
    case tokenMetrics(GenerationTokenMetrics)
    case disconnected
    case failed(String)
}

public struct GenerationTokenMetrics: Equatable, Sendable {
    public let totalTokens: Int
    public let tokensPerSecond: Double

    public init(totalTokens: Int, tokensPerSecond: Double) {
        self.totalTokens = totalTokens
        self.tokensPerSecond = tokensPerSecond
    }
}

public struct TranscriptionConfiguration: Equatable, Sendable {
    public let endpoint: URL
    public let model: String
    public let delayMilliseconds: Int

    public init(endpoint: URL, model: String, delayMilliseconds: Int) {
        self.endpoint = endpoint
        self.model = model
        self.delayMilliseconds = delayMilliseconds
    }
}

public protocol StreamingTranscriptionService: Sendable {
    func events() -> AsyncStream<TranscriptionEvent>
    func start(configuration: TranscriptionConfiguration) async throws
    func sendAudio(_ pcm16MonoData: Data) async
    func stop() async
}

public enum CaptionCorrectionMode: String, CaseIterable, Codable, Equatable, Sendable {
    case standard
    case science
}

public struct CaptionCorrectionRequest: Equatable, Sendable {
    public let segment: CaptionSegment
    public let recentContext: [CaptionSegment]
    public let glossary: [String: String]
    public let mode: CaptionCorrectionMode

    public init(
        segment: CaptionSegment,
        recentContext: [CaptionSegment],
        glossary: [String: String],
        mode: CaptionCorrectionMode = .standard
    ) {
        self.segment = segment
        self.recentContext = recentContext
        self.glossary = glossary
        self.mode = mode
    }
}

public struct CaptionCorrectionResult: Equatable, Sendable {
    public let text: String
    public let promptTokens: Int?
    public let generatedTokens: Int?

    public init(
        text: String,
        promptTokens: Int? = nil,
        generatedTokens: Int? = nil
    ) {
        self.text = text
        self.promptTokens = promptTokens
        self.generatedTokens = generatedTokens
    }
}

public protocol CaptionCorrectionService: Sendable {
    func correct(
        _ request: CaptionCorrectionRequest
    ) async throws -> CaptionCorrectionResult
}
