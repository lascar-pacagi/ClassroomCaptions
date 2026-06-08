import AppKit
import ClassroomCaptionsCore
import Foundation
import Observation

struct DisplayChoice: Identifiable, Equatable {
    let id: CGDirectDisplayID
    let name: String
    let frame: CGRect
}

enum TranscriptionBackend: String, CaseIterable, Identifiable {
    case embedded
    case webSocket

    var id: Self { self }

    var title: String {
        switch self {
        case .embedded: return "Embedded Metal"
        case .webSocket: return "WebSocket (advanced)"
        }
    }
}

@MainActor
@Observable
final class ClassroomAppModel {
    private(set) var session: ClassroomSession?
    private(set) var statusText = "Ready"
    private(set) var displays: [DisplayChoice] = []
    private(set) var microphones: [MicrophoneDevice] = []
    private(set) var microphoneLevel = 0.0
    private(set) var capturedAudioBytes = 0
    private(set) var microphoneError: String?
    private(set) var voxtralConnected = false
    private(set) var firstCaptionLatency: TimeInterval?
    private(set) var isStartingSession = false
    private(set) var isStoppingSession = false
    private(set) var lastSessionArchiveURL: URL?
    private(set) var archiveError: String?
    private(set) var correctionServerReady = false
    private(set) var correctionQueueDepth = 0
    private(set) var lastCorrectionLatency: TimeInterval?
    private(set) var correctionError: String?
    private(set) var voxtralGeneratedTokens = 0
    private(set) var voxtralTokensPerSecond = 0.0
    private(set) var gemmaPromptTokens: Int?
    private(set) var gemmaGeneratedTokens: Int?
    private(set) var gemmaTotalGeneratedTokens = 0
    private(set) var gemmaTokensPerSecond: Double?
    private(set) var gemmaTransformationPercentage: Double?
    private(set) var appMemoryFootprintBytes: UInt64?
    private(set) var gemmaMemoryFootprintBytes: UInt64?
    var selectedDisplayID: CGDirectDisplayID?
    var selectedMicrophoneID: String?
    var transcriptionBackend = TranscriptionBackend.embedded
    var voxtralModelDirectory = NSString(
        string: "~/Library/Application Support/ClassroomCaptions/models/Voxtral-Mini-4B-Realtime-2602"
    ).expandingTildeInPath
    var voxtralEndpoint = "ws://127.0.0.1:8000/v1/realtime"
    var voxtralModel = "T0mSIlver/Voxtral-Mini-4B-Realtime-2602-MLX-4bit"
    var commitIntervalMilliseconds = UserDefaults.standard.object(
        forKey: "commitIntervalMilliseconds"
    ) as? Double ?? 320 {
        didSet {
            UserDefaults.standard.set(
                commitIntervalMilliseconds,
                forKey: "commitIntervalMilliseconds"
            )
        }
    }
    var voxtralContextSeconds = UserDefaults.standard.object(
        forKey: "voxtralContextSeconds"
    ) as? Double ?? 160 {
        didSet {
            UserDefaults.standard.set(
                voxtralContextSeconds,
                forKey: "voxtralContextSeconds"
            )
        }
    }
    var manualCaptionText = ""
    var correctionEnabled = true
    var correctionMode = CaptionCorrectionMode(
        rawValue: UserDefaults.standard.string(forKey: "correctionMode") ?? ""
    ) ?? .science {
        didSet {
            UserDefaults.standard.set(
                correctionMode.rawValue,
                forKey: "correctionMode"
            )
        }
    }
    var gemmaContextCaptionCount = UserDefaults.standard.object(
        forKey: "gemmaContextCaptionCount"
    ) as? Int ?? 0 {
        didSet {
            UserDefaults.standard.set(
                gemmaContextCaptionCount,
                forKey: "gemmaContextCaptionCount"
            )
        }
    }
    var gemmaServerExecutable = NSString(
        string: "~/.local/bin/mlx_lm.server"
    ).expandingTildeInPath
    var gemmaModelPath = "mlx-community/gemma-4-26B-A4B-it-OptiQ-4bit"
    var gemmaEndpoint = "http://127.0.0.1:8081"
    var captionFontSize = UserDefaults.standard.object(
        forKey: "captionFontSize"
    ) as? Double ?? 32 {
        didSet {
            UserDefaults.standard.set(
                captionFontSize,
                forKey: "captionFontSize"
            )
        }
    }
    var showLiveDiagnostics = UserDefaults.standard.bool(
        forKey: "showLiveDiagnostics"
    ) {
        didSet {
            UserDefaults.standard.set(
                showLiveDiagnostics,
                forKey: "showLiveDiagnostics"
            )
            diagnosticsSettingChanged()
        }
    }
    var overlayVoiceCommandsEnabled = UserDefaults.standard.object(
        forKey: "overlayVoiceCommandsEnabled"
    ) as? Bool ?? true {
        didSet {
            UserDefaults.standard.set(
                overlayVoiceCommandsEnabled,
                forKey: "overlayVoiceCommandsEnabled"
            )
        }
    }
    var overlayShowVoiceCommand = UserDefaults.standard.string(
        forKey: "overlayShowVoiceCommand"
    ) ?? "Bonjour soleil bleu" {
        didSet {
            UserDefaults.standard.set(
                overlayShowVoiceCommand,
                forKey: "overlayShowVoiceCommand"
            )
        }
    }
    var overlayHideVoiceCommand = UserDefaults.standard.string(
        forKey: "overlayHideVoiceCommand"
    ) ?? "Bonjour soleil rouge" {
        didSet {
            UserDefaults.standard.set(
                overlayHideVoiceCommand,
                forKey: "overlayHideVoiceCommand"
            )
        }
    }
    var overlayClearVoiceCommand = UserDefaults.standard.string(
        forKey: "overlayClearVoiceCommand"
    ) ?? "Bonjour soleil blanc" {
        didSet {
            UserDefaults.standard.set(
                overlayClearVoiceCommand,
                forKey: "overlayClearVoiceCommand"
            )
        }
    }
    var recordSessions = true
    var sessionArchiveDirectory = NSString(
        string: "~/Documents/ClassroomCaptions"
    ).expandingTildeInPath

    @ObservationIgnored
    private let overlayController = CaptionOverlayController()
    @ObservationIgnored
    private let microphoneCapture = MicrophoneCaptureService()
    @ObservationIgnored
    private let voxtral = VoxtralRealtimeService()
    @ObservationIgnored
    private let embeddedVoxtral = VoxtralEmbeddedService()
    @ObservationIgnored
    private let sessionArchive = SessionArchiveService()
    @ObservationIgnored
    private let gemmaServer = GemmaServerController()
    @ObservationIgnored
    private var webSocketEventsTask: Task<Void, Never>?
    @ObservationIgnored
    private var embeddedEventsTask: Task<Void, Never>?
    @ObservationIgnored
    private var commitTask: Task<Void, Never>?
    @ObservationIgnored
    private var silenceFlushTask: Task<Void, Never>?
    @ObservationIgnored
    private var correctionWorkerTask: Task<Void, Never>?
    @ObservationIgnored
    private var correctionWarmupTask: Task<Void, Never>?
    @ObservationIgnored
    private var diagnosticsTask: Task<Void, Never>?
    private struct PendingCorrection {
        let segmentID: UUID
        let mode: CaptionCorrectionMode
    }
    @ObservationIgnored
    private var pendingCorrections: [PendingCorrection] = []
    @ObservationIgnored
    private var sessionListeningStartedAt: Date?
    @ObservationIgnored
    private var activeTranscriptionBackend: TranscriptionBackend?
    @ObservationIgnored
    private var activeRecordingEnabled = false
    @ObservationIgnored
    private var activeMicrophoneName: String?
    @ObservationIgnored
    private var processedOverlayVoiceCommandCount = 0
    @ObservationIgnored
    private var gemmaProcessID: pid_t?
    @ObservationIgnored
    private var overlayMinimumVisibleSequence: Int?
    @ObservationIgnored
    private var overlayClearFinalizationPending = false
    @ObservationIgnored
    private var overlayShouldResumeAfterClear = false

    var isListening: Bool {
        session?.phase == .listening
    }

    var hasActiveSession: Bool {
        guard let phase = session?.phase else { return false }
        return phase == .listening || phase == .paused || phase == .stopping
    }

    var isOverlayVisible: Bool {
        overlayController.isVisible
    }

    var recentSegments: [CaptionSegment] {
        session?.timeline.recentSegments(limit: 8) ?? []
    }

    init() {
        if UserDefaults.standard.object(forKey: "overlayShowVoiceCommand") == nil
            || overlayShowVoiceCommand == "Sésame lumière"
            || overlayShowVoiceCommand == "Rideau bleu" {
            overlayShowVoiceCommand = "Bonjour soleil bleu"
        }
        if UserDefaults.standard.object(forKey: "overlayHideVoiceCommand") == nil
            || overlayHideVoiceCommand == "Sésame rouge"
            || overlayHideVoiceCommand == "Sésame silence"
            || overlayHideVoiceCommand == "Rideau rouge" {
            overlayHideVoiceCommand = "Bonjour soleil rouge"
        }
        if UserDefaults.standard.object(forKey: "overlayClearVoiceCommand") == nil
            || overlayClearVoiceCommand == "Rideau blanc" {
            overlayClearVoiceCommand = "Bonjour soleil blanc"
        }
        refreshDisplays()
        refreshMicrophones()
        observeTranscriptionEvents()
        diagnosticsSettingChanged()
    }

    func refreshDisplays() {
        displays = NSScreen.screens.map { screen in
            DisplayChoice(
                id: screen.displayID,
                name: screen.localizedName,
                frame: screen.frame
            )
        }

        if selectedDisplayID == nil || !displays.contains(where: { $0.id == selectedDisplayID }) {
            selectedDisplayID = displays.first?.id
        }
        refreshOverlay()
    }

    func toggleSession() {
        hasActiveSession ? stopSession() : startSession()
    }

    func startSession() {
        guard !hasActiveSession, !isStartingSession, !isStoppingSession else {
            return
        }
        microphoneError = nil
        archiveError = nil
        correctionError = nil
        firstCaptionLatency = nil
        capturedAudioBytes = 0
        resetLiveDiagnostics()
        resetOverlayClearState()
        isStartingSession = true
        activeRecordingEnabled = recordSessions
        activeTranscriptionBackend = transcriptionBackend
        if correctionEnabled {
            warmCorrectionServer()
        }
        statusText = transcriptionBackend == .embedded
            ? "Loading and preparing Voxtral"
            : "Connecting to Voxtral"
        Task {
            do {
                switch transcriptionBackend {
                case .embedded:
                    try await embeddedVoxtral.start(
                        modelDirectory: URL(fileURLWithPath: voxtralModelDirectory),
                        delayMilliseconds: Int(commitIntervalMilliseconds),
                        processingIntervalSeconds: 1.0,
                        maxDecodeContextTokens: Int(
                            voxtralContextSeconds * 12.5
                        )
                    )
                case .webSocket:
                    guard let endpoint = URL(string: voxtralEndpoint) else {
                        throw VoxtralRealtimeError.invalidEndpoint
                    }
                    try await voxtral.start(configuration: TranscriptionConfiguration(
                        endpoint: endpoint,
                        model: voxtralModel,
                        delayMilliseconds: Int(commitIntervalMilliseconds)
                    ))
                }
            } catch {
                microphoneError = error.localizedDescription
                statusText = "Voxtral connection failed"
                isStartingSession = false
                activeRecordingEnabled = false
                activeTranscriptionBackend = nil
            }
        }
    }

    func pauseOrResume() {
        guard var session else { return }
        if session.phase == .listening {
            guard session.pause() else { return }
            statusText = "Paused"
        } else if session.phase == .paused {
            guard session.markListening() else { return }
            statusText = "Listening"
        }
        self.session = session
        refreshOverlay()
    }

    func stopSession() {
        guard !isStoppingSession, var currentSession = session else { return }
        guard currentSession.beginStopping() else { return }
        session = currentSession
        isStoppingSession = true
        commitTask?.cancel()
        commitTask = nil
        silenceFlushTask?.cancel()
        silenceFlushTask = nil
        microphoneCapture.stop()
        microphoneLevel = 0
        let backend = activeTranscriptionBackend
        let backendName = backend?.rawValue ?? "unknown"
        let microphoneName = activeMicrophoneName
        let delayMilliseconds = Int(commitIntervalMilliseconds)
        let shouldFinalizeArchive = activeRecordingEnabled
        Task {
            var drainedText: String?
            if backend == .embedded {
                drainedText = await embeddedVoxtral.stop()
            } else {
                await voxtral.stop()
            }
            guard var completedSession = self.session else {
                self.isStoppingSession = false
                return
            }
            if let drainedText {
                let remainingText = self.consumeOverlayVoiceCommand(
                    in: drainedText
                )
                if let segment = completedSession.finalizeCaption(
                    remainingText,
                    correctionEnabled: self.correctionEnabled
                ) {
                    self.enqueueCorrection(segment)
                }
                self.session = completedSession
            }
            await self.waitForCorrections()
            completedSession = self.session ?? completedSession
            _ = completedSession.finish()
            self.session = completedSession

            if shouldFinalizeArchive {
                do {
                    self.lastSessionArchiveURL = try await self.sessionArchive.finalize(
                        session: completedSession,
                        backend: backendName,
                        microphone: microphoneName,
                        modelDelayMilliseconds: delayMilliseconds
                    )
                } catch {
                    self.archiveError = error.localizedDescription
                }
            }

            self.voxtralConnected = false
            self.isStartingSession = false
            self.isStoppingSession = false
            self.activeTranscriptionBackend = nil
            self.activeRecordingEnabled = false
            self.activeMicrophoneName = nil
            if self.archiveError != nil {
                self.statusText = "Session stopped; export failed"
            } else if shouldFinalizeArchive {
                self.statusText = "Session stopped and exported"
            } else {
                self.statusText = "Session stopped"
            }
            self.refreshOverlay()
        }
        statusText = "Finishing Voxtral and exporting"
    }

    func submitManualCaption() {
        guard var session, session.phase == .listening else { return }
        guard let segment = session.finalizeCaption(
            manualCaptionText,
            correctionEnabled: correctionEnabled
        ) else {
            return
        }

        self.session = session
        enqueueCorrection(segment)
        manualCaptionText = ""
        refreshOverlay()
    }

    func previewProvisionalCaption() {
        guard var session, session.phase == .listening else { return }
        session.updateProvisional(manualCaptionText)
        self.session = session
        refreshOverlay()
    }

    func clearSession() {
        guard !hasActiveSession, !isStartingSession, !isStoppingSession else {
            return
        }
        microphoneCapture.stop()
        commitTask?.cancel()
        commitTask = nil
        silenceFlushTask?.cancel()
        silenceFlushTask = nil
        correctionWorkerTask?.cancel()
        correctionWorkerTask = nil
        pendingCorrections.removeAll()
        correctionQueueDepth = 0
        let backend = activeTranscriptionBackend
        Task {
            if backend == .embedded {
                _ = await embeddedVoxtral.stop()
            } else {
                await voxtral.stop()
            }
        }
        session = nil
        sessionArchive.cancel()
        statusText = "Ready"
        manualCaptionText = ""
        microphoneLevel = 0
        capturedAudioBytes = 0
        microphoneError = nil
        voxtralConnected = false
        firstCaptionLatency = nil
        isStartingSession = false
        isStoppingSession = false
        activeRecordingEnabled = false
        activeMicrophoneName = nil
        activeTranscriptionBackend = nil
        resetLiveDiagnostics()
        resetOverlayClearState()
        refreshOverlay()
    }

    func revealLastSessionArchive() {
        guard let lastSessionArchiveURL else { return }
        NSWorkspace.shared.activateFileViewerSelecting([lastSessionArchiveURL])
    }

    func refreshMicrophones() {
        microphones = AudioDeviceCatalog.inputDevices()
        let availableIDs = Set(microphones.map(\.id))
        if let selectedMicrophoneID, availableIDs.contains(selectedMicrophoneID) {
            return
        }
        selectedMicrophoneID = AudioDeviceCatalog.defaultInputDeviceUID()
            ?? microphones.first?.id
    }

    private func observeTranscriptionEvents() {
        webSocketEventsTask?.cancel()
        embeddedEventsTask?.cancel()

        let webSocketEvents = voxtral.events()
        webSocketEventsTask = Task { [weak self] in
            for await event in webSocketEvents {
                guard !Task.isCancelled else { break }
                guard self?.activeTranscriptionBackend == .webSocket else { continue }
                self?.handleVoxtralEvent(event)
            }
        }

        let embeddedEvents = embeddedVoxtral.events()
        embeddedEventsTask = Task { [weak self] in
            for await event in embeddedEvents {
                guard !Task.isCancelled else { break }
                guard self?.activeTranscriptionBackend == .embedded else { continue }
                self?.handleVoxtralEvent(event)
            }
        }
    }

    private func handleVoxtralEvent(_ event: TranscriptionEvent) {
        switch event {
        case .connected:
            voxtralConnected = true
            isStartingSession = false
            statusText = "Voxtral connected; requesting microphone access"
            Task { await startMicrophoneAfterVoxtralConnection() }

        case .provisional(let text):
            guard var session else { return }
            let provisionalText = consumeOverlayVoiceCommand(
                in: text,
                provisional: true
            )
            session.updateProvisional(provisionalText)
            self.session = session
            recordFirstCaptionLatencyIfNeeded()
            resumeOverlayAfterClearIfNeeded(hasNewCaption: !provisionalText.isEmpty)

        case .finalized(let text):
            guard var session else { return }
            let wasClearingOverlay = overlayClearFinalizationPending
            let remainingText = consumeOverlayVoiceCommand(in: text)
            let segment = session.finalizeCaption(
                remainingText,
                correctionEnabled: correctionEnabled
            )
            self.session = session
            if let segment {
                enqueueCorrection(segment)
            }
            recordFirstCaptionLatencyIfNeeded()
            processedOverlayVoiceCommandCount = 0
            if wasClearingOverlay || overlayClearFinalizationPending {
                overlayMinimumVisibleSequence =
                    (session.timeline.segments.last?.sequence ?? -1) + 1
                overlayClearFinalizationPending = false
                refreshOverlay()
            } else {
                resumeOverlayAfterClearIfNeeded(hasNewCaption: segment != nil)
            }

        case .tokenMetrics(let metrics):
            voxtralGeneratedTokens = metrics.totalTokens
            voxtralTokensPerSecond = metrics.tokensPerSecond

        case .failed(let message):
            microphoneError = message
            statusText = "Voxtral error"
            isStartingSession = false

        case .disconnected:
            voxtralConnected = false
            isStartingSession = false
            if isListening {
                microphoneCapture.stop()
                microphoneLevel = 0
                statusText = "Voxtral disconnected"
            }
        }
    }

    private func startMicrophoneAfterVoxtralConnection() async {
        guard await microphoneCapture.requestPermission() else {
            microphoneError = "Microphone access is required. Enable it in System Settings > Privacy & Security > Microphone."
            statusText = "Microphone access denied"
            if activeTranscriptionBackend == .embedded {
                _ = await embeddedVoxtral.stop()
            } else {
                await voxtral.stop()
            }
            activeRecordingEnabled = false
            activeTranscriptionBackend = nil
            return
        }

        do {
            let backend = activeTranscriptionBackend
            let recordingEnabled = activeRecordingEnabled
            let archive = sessionArchive
            var newSession = ClassroomSession()
            session = newSession
            activeMicrophoneName = microphones.first {
                $0.id == selectedMicrophoneID
            }?.name

            if activeRecordingEnabled {
                lastSessionArchiveURL = try await sessionArchive.start(
                    session: newSession,
                    rootDirectory: URL(
                        fileURLWithPath: sessionArchiveDirectory,
                        isDirectory: true
                    )
                )
            }

            try microphoneCapture.start(
                deviceUID: selectedMicrophoneID
            ) { [weak self] chunk in
                guard let self else { return }
                if recordingEnabled {
                    archive.appendAudio(chunk)
                }
                let reading = PCM16LevelMeter.measure(chunk)
                if backend == .embedded {
                    self.embeddedVoxtral.sendAudio(chunk)
                }
                Task {
                    await MainActor.run {
                        guard self.isListening else { return }
                        self.capturedAudioBytes += chunk.count
                        self.microphoneLevel = reading.normalizedLevel
                        if backend == .embedded {
                            self.noteEmbeddedVoiceActivity(
                                level: reading.normalizedLevel
                            )
                        }
                    }
                    if backend == .webSocket {
                        await self.voxtral.sendAudio(chunk)
                    }
                }
            }
            _ = newSession.markListening()
            session = newSession
            sessionListeningStartedAt = Date()
            statusText = "Listening with Voxtral"
            if activeTranscriptionBackend == .webSocket {
                restartCommitTask()
            }
            refreshOverlay()
        } catch {
            sessionArchive.cancel()
            session = nil
            microphoneError = error.localizedDescription
            statusText = "Microphone failed"
            if activeTranscriptionBackend == .embedded {
                _ = await embeddedVoxtral.stop()
            } else {
                await voxtral.stop()
            }
            activeRecordingEnabled = false
            activeMicrophoneName = nil
            activeTranscriptionBackend = nil
        }
    }

    private func restartCommitTask() {
        commitTask?.cancel()
        let interval = max(100, commitIntervalMilliseconds)
        commitTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .milliseconds(interval))
                guard !Task.isCancelled, let self else { break }
                self.voxtral.commit()
            }
        }
    }

    private func noteEmbeddedVoiceActivity(level: Double) {
        guard level >= 0.06 else { return }
        silenceFlushTask?.cancel()
        silenceFlushTask = Task { [weak self] in
            try? await Task.sleep(for: .milliseconds(900))
            guard !Task.isCancelled, let self, self.isListening,
                  self.activeTranscriptionBackend == .embedded else {
                return
            }
            await self.embeddedVoxtral.flush(finalizeCaption: true)
        }
    }

    private func recordFirstCaptionLatencyIfNeeded() {
        guard firstCaptionLatency == nil, let sessionListeningStartedAt else { return }
        firstCaptionLatency = Date().timeIntervalSince(sessionListeningStartedAt)
    }

    func correctionSettingChanged() {
        if correctionEnabled {
            correctionError = nil
            warmCorrectionServer()
        } else if !hasActiveSession {
            correctionWarmupTask?.cancel()
            correctionWarmupTask = nil
            gemmaServer.stop()
            correctionServerReady = false
        }
    }

    func shutdown() {
        correctionWarmupTask?.cancel()
        correctionWorkerTask?.cancel()
        diagnosticsTask?.cancel()
        gemmaServer.stop()
    }

    func diagnosticsSettingChanged() {
        diagnosticsTask?.cancel()
        diagnosticsTask = nil
        guard showLiveDiagnostics else { return }
        appMemoryFootprintBytes = ProcessMemory.physicalFootprintBytes()
        if let endpoint = URL(string: gemmaEndpoint) {
            updateGemmaProcessIdentity(endpoint: endpoint)
        }
        diagnosticsTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(1))
                guard !Task.isCancelled, let self else { break }
                self.appMemoryFootprintBytes = ProcessMemory.physicalFootprintBytes()
                if let processID = self.gemmaProcessID {
                    self.gemmaMemoryFootprintBytes =
                        ProcessMemory.physicalFootprintBytes(
                            processID: processID
                        )
                }
            }
        }
    }

    private func warmCorrectionServer() {
        guard correctionEnabled, correctionWarmupTask == nil else { return }
        correctionWarmupTask = Task { [weak self] in
            guard let self else { return }
            do {
                let configuration = try self.gemmaConfiguration()
                try await self.gemmaServer.ensureReady(
                    executablePath: configuration.executablePath,
                    modelPath: configuration.modelPath,
                    endpoint: configuration.endpoint
                )
                guard !Task.isCancelled else { return }
                self.correctionServerReady = true
                self.updateGemmaProcessIdentity(endpoint: configuration.endpoint)
                self.correctionError = nil
            } catch {
                guard !Task.isCancelled else { return }
                self.correctionServerReady = false
                self.correctionError = error.localizedDescription
            }
            self.correctionWarmupTask = nil
        }
    }

    private func enqueueCorrection(_ segment: CaptionSegment) {
        guard segment.correctionState == .queued else { return }
        guard pendingCorrections.count < 8 else {
            failCorrection(
                segmentID: segment.id,
                message: "Correction skipped because the Gemma queue is full."
            )
            return
        }
        pendingCorrections.append(PendingCorrection(
            segmentID: segment.id,
            mode: correctionMode
        ))
        correctionQueueDepth = pendingCorrections.count
        startCorrectionWorkerIfNeeded()
    }

    private func startCorrectionWorkerIfNeeded() {
        guard correctionWorkerTask == nil else { return }
        correctionWorkerTask = Task { [weak self] in
            guard let self else { return }
            while !Task.isCancelled, !self.pendingCorrections.isEmpty {
                let pending = self.pendingCorrections.removeFirst()
                self.correctionQueueDepth = self.pendingCorrections.count + 1
                await self.correctSegment(pending.segmentID, mode: pending.mode)
                self.correctionQueueDepth = self.pendingCorrections.count
            }
            self.correctionWorkerTask = nil
        }
    }

    private func correctSegment(
        _ segmentID: UUID,
        mode: CaptionCorrectionMode
    ) async {
        guard var currentSession = session,
              let segment = currentSession.timeline.segments.first(where: {
                  $0.id == segmentID
              }),
              currentSession.beginCorrection(segmentID: segmentID) else {
            return
        }
        session = currentSession
        refreshOverlay()

        let startedAt = ContinuousClock.now
        do {
            let configuration = try gemmaConfiguration()
            try await gemmaServer.ensureReady(
                executablePath: configuration.executablePath,
                modelPath: configuration.modelPath,
                endpoint: configuration.endpoint
            )
            correctionServerReady = true
            updateGemmaProcessIdentity(endpoint: configuration.endpoint)
            let recentContext = currentSession.timeline.segments
                .filter { $0.sequence < segment.sequence }
                .suffix(max(0, gemmaContextCaptionCount))
            let service = GemmaCorrectionService(endpoint: configuration.endpoint)
            let result = try await service.correct(CaptionCorrectionRequest(
                segment: segment,
                recentContext: Array(recentContext),
                glossary: [:],
                mode: mode
            ))
            let latency = startedAt.duration(to: .now).timeInterval
            guard !Task.isCancelled, var updatedSession = session else { return }
            _ = updatedSession.applyCorrection(
                segmentID: segmentID,
                text: result.text
            )
            session = updatedSession
            lastCorrectionLatency = latency
            gemmaPromptTokens = result.promptTokens
            gemmaGeneratedTokens = result.generatedTokens
            if let generatedTokens = result.generatedTokens {
                gemmaTotalGeneratedTokens += generatedTokens
                gemmaTokensPerSecond = Double(generatedTokens) / max(0.001, latency)
            } else {
                gemmaTokensPerSecond = nil
            }
            gemmaTransformationPercentage = CaptionTransformation.percentage(
                from: segment.rawText,
                to: result.text
            )
            correctionError = nil
        } catch {
            guard !Task.isCancelled else { return }
            if !(error is CaptionCorrectionValidationError) {
                correctionServerReady = false
            }
            correctionError = error.localizedDescription
            failCorrection(segmentID: segmentID, message: error.localizedDescription)
        }
        refreshOverlay()
    }

    private func failCorrection(segmentID: UUID, message: String) {
        guard var currentSession = session else { return }
        _ = currentSession.failCorrection(segmentID: segmentID, message: message)
        session = currentSession
        refreshOverlay()
    }

    private func waitForCorrections() async {
        let deadline = ContinuousClock.now + .seconds(60)
        while correctionWorkerTask != nil || !pendingCorrections.isEmpty {
            if ContinuousClock.now >= deadline {
                correctionWorkerTask?.cancel()
                correctionWorkerTask = nil
                let remaining = pendingCorrections
                pendingCorrections.removeAll()
                for correction in remaining {
                    failCorrection(
                        segmentID: correction.segmentID,
                        message: "Correction timed out while stopping the session."
                    )
                }
                correctionQueueDepth = 0
                return
            }
            try? await Task.sleep(for: .milliseconds(100))
        }
    }

    private func gemmaConfiguration() throws -> (
        executablePath: String,
        modelPath: String,
        endpoint: URL
    ) {
        guard let endpoint = URL(string: gemmaEndpoint),
              endpoint.scheme == "http",
              endpoint.host == "127.0.0.1" || endpoint.host == "localhost",
              endpoint.port != nil else {
            throw GemmaCorrectionError.invalidEndpoint
        }
        return (gemmaServerExecutable, gemmaModelPath, endpoint)
    }

    func toggleOverlay() {
        if overlayController.isVisible {
            overlayController.hide()
        } else {
            refreshOverlay(forceVisible: true)
        }
    }

    private func resetLiveDiagnostics() {
        voxtralGeneratedTokens = 0
        voxtralTokensPerSecond = 0
        gemmaPromptTokens = nil
        gemmaGeneratedTokens = nil
        gemmaTotalGeneratedTokens = 0
        gemmaTokensPerSecond = nil
        gemmaTransformationPercentage = nil
        if showLiveDiagnostics {
            appMemoryFootprintBytes = ProcessMemory.physicalFootprintBytes()
        }
    }

    private func updateGemmaProcessIdentity(endpoint: URL) {
        gemmaProcessID = gemmaServer.processIdentifier(endpoint: endpoint)
        if let gemmaProcessID {
            gemmaMemoryFootprintBytes = ProcessMemory.physicalFootprintBytes(
                processID: gemmaProcessID
            )
        }
    }

    private func consumeOverlayVoiceCommand(
        in text: String,
        provisional: Bool = false
    ) -> String {
        guard overlayVoiceCommandsEnabled else { return text }
        let showPhrase = overlayShowVoiceCommand.trimmingCharacters(
            in: .whitespacesAndNewlines
        )
        let hidePhrase = overlayHideVoiceCommand.trimmingCharacters(
            in: .whitespacesAndNewlines
        )
        let clearPhrase = overlayClearVoiceCommand.trimmingCharacters(
            in: .whitespacesAndNewlines
        )
        guard !showPhrase.isEmpty, !hidePhrase.isEmpty,
              !clearPhrase.isEmpty else {
            return text
        }

        let commands = SpokenOverlayCommandRecognizer.recognizeAll(
            in: text,
            showPhrase: showPhrase,
            hidePhrase: hidePhrase,
            clearPhrase: clearPhrase
        )
        if !commands.isEmpty {
            let firstUnhandledIndex = min(
                processedOverlayVoiceCommandCount,
                commands.count
            )
            for command in commands.dropFirst(firstUnhandledIndex) {
                applyOverlayVoiceCommand(
                    command.action,
                    provisional: provisional
                )
            }
            if provisional {
                processedOverlayVoiceCommandCount = commands.count
            } else {
                processedOverlayVoiceCommandCount = 0
            }
            return commands.last?.remainingText ?? ""
        }

        if provisional,
           SpokenOverlayCommandRecognizer.isPotentialCommand(
               text,
               showPhrase: showPhrase,
               hidePhrase: hidePhrase,
               clearPhrase: clearPhrase
           ) {
            return ""
        }
        return text
    }

    private func applyOverlayVoiceCommand(
        _ action: SpokenOverlayAction,
        provisional: Bool
    ) {
        switch action {
        case .show:
            refreshOverlay(forceVisible: true)
            statusText = "Overlay shown by voice command"
        case .hide:
            overlayController.hide()
            statusText = "Overlay hidden by voice command"
        case .clear:
            overlayShouldResumeAfterClear =
                overlayShouldResumeAfterClear || overlayController.isVisible
            overlayMinimumVisibleSequence =
                (session?.timeline.segments.last?.sequence ?? -1) + 1
            overlayClearFinalizationPending = true
            overlayController.hide()
            statusText = "Captions cleared by voice command"
            if provisional {
                requestCaptionBoundaryForOverlayClear()
            }
        }
    }

    private func requestCaptionBoundaryForOverlayClear() {
        silenceFlushTask?.cancel()
        silenceFlushTask = nil
        if activeTranscriptionBackend == .embedded {
            Task { [weak self] in
                guard let self else { return }
                await self.embeddedVoxtral.flush(finalizeCaption: true)
            }
        } else {
            voxtral.commit()
        }
    }

    private func resumeOverlayAfterClearIfNeeded(hasNewCaption: Bool) {
        guard hasNewCaption, !overlayClearFinalizationPending else {
            refreshOverlay()
            return
        }
        let shouldResume = overlayShouldResumeAfterClear
        overlayShouldResumeAfterClear = false
        refreshOverlay(forceVisible: shouldResume)
    }

    private func resetOverlayClearState() {
        overlayMinimumVisibleSequence = nil
        overlayClearFinalizationPending = false
        overlayShouldResumeAfterClear = false
        processedOverlayVoiceCommandCount = 0
    }

    func resetOverlayFrame() {
        guard let selectedScreen = NSScreen.screens.first(where: {
            $0.displayID == selectedDisplayID
        }) ?? NSScreen.main else {
            return
        }
        overlayController.resetFrame(on: selectedScreen)
        refreshOverlay(forceVisible: true)
    }

    func refreshOverlay(forceVisible: Bool = false) {
        let selectedScreen = NSScreen.screens.first { $0.displayID == selectedDisplayID }
            ?? NSScreen.main
        let lines = session?.timeline.segments
            .filter { segment in
                guard let overlayMinimumVisibleSequence else { return true }
                return segment.sequence >= overlayMinimumVisibleSequence
            }
            .suffix(3)
            .map(\.displayText) ?? []
        let provisional = overlayClearFinalizationPending
            ? nil
            : session?.timeline.provisional?.text
        let shouldShow = forceVisible || overlayController.isVisible

        guard shouldShow, let selectedScreen else {
            overlayController.hide()
            return
        }

        overlayController.show(
            on: selectedScreen,
            lines: lines,
            provisional: provisional,
            fontSize: captionFontSize
        )
    }
}

private extension NSScreen {
    var displayID: CGDirectDisplayID {
        deviceDescription[NSDeviceDescriptionKey("NSScreenNumber")] as? CGDirectDisplayID ?? 0
    }
}

private extension Duration {
    var timeInterval: TimeInterval {
        let parts = components
        return Double(parts.seconds)
            + Double(parts.attoseconds) / 1_000_000_000_000_000_000
    }
}
