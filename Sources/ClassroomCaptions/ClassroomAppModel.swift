import AppKit
import ClassroomCaptionsCore
import Foundation
import Observation
import Synchronization

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

struct ClassroomQuestion: Identifiable, Equatable {
    let id: UUID
    let text: String
    let submittedAt: Date
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
    private(set) var iphoneSharingStatus = LocalCaptionServerStatus.stopped
    private(set) var iphonePairingURL: URL?
    private(set) var studentQuestionStatus =
        StudentQuestionServerStatus.stopped
    private(set) var studentQuestionURL: URL?
    private(set) var pendingStudentQuestions: [ClassroomQuestion] = []
    private(set) var presentedStudentQuestion: ClassroomQuestion?
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
    var studentNextQuestionVoiceCommand = UserDefaults.standard.string(
        forKey: "studentNextQuestionVoiceCommand"
    ) ?? "Bonjour question suivante" {
        didSet {
            UserDefaults.standard.set(
                studentNextQuestionVoiceCommand,
                forKey: "studentNextQuestionVoiceCommand"
            )
        }
    }
    var studentDismissQuestionVoiceCommand = UserDefaults.standard.string(
        forKey: "studentDismissQuestionVoiceCommand"
    ) ?? "Bonjour question terminée" {
        didSet {
            UserDefaults.standard.set(
                studentDismissQuestionVoiceCommand,
                forKey: "studentDismissQuestionVoiceCommand"
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
    private var processedOverlayVoiceCommandActions: [SpokenOverlayAction] = []
    @ObservationIgnored
    private var gemmaProcessID: pid_t?
    @ObservationIgnored
    private var captionServer: LocalCaptionServer!
    @ObservationIgnored
    private var remoteCaptionRevision: UInt64 = 0
    @ObservationIgnored
    private var overlayMinimumVisibleSequence: Int?
    @ObservationIgnored
    private var overlayClearFinalizationPending = false
    @ObservationIgnored
    private var overlayShouldResumeAfterClear = false
    @ObservationIgnored
    private let audioInputEnabled = Mutex(false)

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

    var isIPhoneSharingActive: Bool {
        switch iphoneSharingStatus {
        case .starting, .ready, .clientConnected:
            return true
        case .stopped, .failed:
            return false
        }
    }

    var isIPhoneConnected: Bool {
        if case .clientConnected = iphoneSharingStatus {
            return true
        }
        return false
    }

    var areStudentQuestionsEnabled: Bool {
        if case .ready = studentQuestionStatus {
            return true
        }
        return false
    }

    var recentSegments: [CaptionSegment] {
        session?.timeline.recentSegments(limit: 8) ?? []
    }

    private var terminationObserver: NSObjectProtocol?
    @ObservationIgnored private var pendingAudioBytes = 0
    @ObservationIgnored private var lastMeterPublish = ContinuousClock.now

    init() {
        // Quitting via Cmd-Q, the Dock, or window close never runs the
        // menu-bar Quit button, and a spawned mlx_lm.server child outlives
        // its parent. Shut services down on every termination path.
        terminationObserver = NotificationCenter.default.addObserver(
            forName: NSApplication.willTerminateNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            MainActor.assumeIsolated {
                self?.shutdown()
            }
        }
        captionServer = LocalCaptionServer(
            statusHandler: { [weak self] status in
                Task { @MainActor [weak self] in
                    self?.handleIPhoneSharingStatus(status)
                }
            },
            questionStatusHandler: { [weak self] status in
                Task { @MainActor [weak self] in
                    self?.handleStudentQuestionStatus(status)
                }
            },
            questionHandler: { [weak self] question in
                Task { @MainActor [weak self] in
                    self?.receiveStudentQuestion(question)
                }
            }
        )
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
            audioInputEnabled.withLock { $0 = false }
            discardBufferedAudioAtPause()
            statusText = "Paused"
        } else if session.phase == .paused {
            guard session.markListening() else { return }
            audioInputEnabled.withLock { $0 = true }
            statusText = "Listening"
        }
        self.session = session
        refreshOverlay()
    }

    func stopSession() {
        guard !isStoppingSession, var currentSession = session else { return }
        guard currentSession.beginStopping() else { return }
        capturedAudioBytes += pendingAudioBytes
        pendingAudioBytes = 0
        session = currentSession
        isStoppingSession = true
        audioInputEnabled.withLock { $0 = false }
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
        audioInputEnabled.withLock { $0 = false }
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
            // isStartingSession stays true until markListening() or failure:
            // clearing it here re-enables Start while the microphone permission
            // prompt is up, allowing a second start to reload the model
            // mid-flight and double-start the archive.
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
            processedOverlayVoiceCommandActions = []
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
            isStartingSession = false
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
                guard let self,
                      self.audioInputEnabled.withLock({ $0 }) else {
                    return
                }
                if recordingEnabled {
                    archive.appendAudio(chunk)
                }
                let reading = PCM16LevelMeter.measure(chunk)
                if backend == .embedded {
                    self.embeddedVoxtral.sendAudio(chunk)
                } else if backend == .webSocket {
                    // Sent synchronously from the capture queue: per-chunk
                    // Tasks have no FIFO guarantee, so awaiting the send from
                    // them could deliver audio frames out of order.
                    self.voxtral.sendAudio(chunk)
                }
                Task {
                    await MainActor.run {
                        guard self.isListening else { return }
                        // Silence detection needs every chunk's level, but the
                        // observable meter/byte counters only need ~15 Hz:
                        // writing them at the 100 Hz capture rate invalidates
                        // SwiftUI views for changes no one can perceive.
                        self.pendingAudioBytes += chunk.count
                        if backend == .embedded {
                            self.noteEmbeddedVoiceActivity(
                                level: reading.normalizedLevel
                            )
                        }
                        let now = ContinuousClock.now
                        if self.lastMeterPublish.duration(to: now)
                            >= .milliseconds(66) {
                            self.lastMeterPublish = now
                            self.capturedAudioBytes += self.pendingAudioBytes
                            self.pendingAudioBytes = 0
                            self.microphoneLevel = reading.normalizedLevel
                        }
                    }
                }
            }
            _ = newSession.markListening()
            session = newSession
            audioInputEnabled.withLock { $0 = true }
            sessionListeningStartedAt = Date()
            statusText = "Listening with Voxtral"
            isStartingSession = false
            if activeTranscriptionBackend == .webSocket {
                restartCommitTask()
            }
            refreshOverlay()
        } catch {
            sessionArchive.cancel()
            audioInputEnabled.withLock { $0 = false }
            session = nil
            microphoneError = error.localizedDescription
            statusText = "Microphone failed"
            isStartingSession = false
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

    private func discardBufferedAudioAtPause() {
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
        captionServer.stop()
        gemmaServer.stop()
        embeddedVoxtral.releaseModel()
    }

    func toggleIPhoneSharing() {
        if isIPhoneSharingActive {
            captionServer.setQuestionSubmissionsEnabled(false)
            captionServer.stop()
        } else {
            iphonePairingURL = nil
            iphoneSharingStatus = .starting
            captionServer.start()
            publishRemoteCaptions()
        }
    }

    func toggleStudentQuestions() {
        guard isIPhoneSharingActive else {
            studentQuestionStatus = .failed(
                "Start iPhone sharing before enabling student questions."
            )
            return
        }
        captionServer.setQuestionSubmissionsEnabled(
            !areStudentQuestionsEnabled
        )
    }

    func presentNextStudentQuestion() {
        presentedStudentQuestion = pendingStudentQuestions.isEmpty
            ? nil
            : pendingStudentQuestions.removeFirst()
        refreshOverlay(forceVisible: presentedStudentQuestion != nil)
    }

    func dismissPresentedStudentQuestion() {
        presentedStudentQuestion = nil
        refreshOverlay()
    }

    func clearPendingStudentQuestions() {
        pendingStudentQuestions.removeAll()
        refreshOverlay()
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

    private var correctionWorkerGeneration = 0

    private func startCorrectionWorkerIfNeeded() {
        guard correctionWorkerTask == nil else { return }
        correctionWorkerGeneration += 1
        let generation = correctionWorkerGeneration
        correctionWorkerTask = Task { [weak self] in
            guard let self else { return }
            while !Task.isCancelled, !self.pendingCorrections.isEmpty {
                let pending = self.pendingCorrections.removeFirst()
                self.correctionQueueDepth = self.pendingCorrections.count + 1
                await self.correctSegment(pending.segmentID, mode: pending.mode)
                self.correctionQueueDepth = self.pendingCorrections.count
            }
            // A worker cancelled mid-await can resume after a newer worker was
            // spawned; only the current generation may release the handle,
            // otherwise the next enqueue starts a duplicate worker.
            if self.correctionWorkerGeneration == generation {
                self.correctionWorkerTask = nil
            }
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
        Task { [weak self] in
            guard let self else { return }
            let identifier = await self.gemmaServer.processIdentifier(
                endpoint: endpoint
            )
            self.gemmaProcessID = identifier
            if let identifier {
                self.gemmaMemoryFootprintBytes =
                    ProcessMemory.physicalFootprintBytes(
                        processID: identifier
                    )
            }
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
        let nextQuestionPhrase =
            studentNextQuestionVoiceCommand.trimmingCharacters(
                in: .whitespacesAndNewlines
            )
        let dismissQuestionPhrase =
            studentDismissQuestionVoiceCommand.trimmingCharacters(
                in: .whitespacesAndNewlines
            )
        guard !showPhrase.isEmpty, !hidePhrase.isEmpty,
              !clearPhrase.isEmpty, !nextQuestionPhrase.isEmpty,
              !dismissQuestionPhrase.isEmpty else {
            return text
        }

        let commands = SpokenOverlayCommandRecognizer.recognizeAll(
            in: text,
            showPhrase: showPhrase,
            hidePhrase: hidePhrase,
            clearPhrase: clearPhrase,
            nextQuestionPhrase: nextQuestionPhrase,
            dismissQuestionPhrase: dismissQuestionPhrase
        )
        if !commands.isEmpty {
            // Compare the recognized actions element-wise with what was
            // already executed for this utterance: a pure count would treat a
            // revised hypothesis ("...bleu" -> "...rouge") as already handled
            // and never execute the corrected command.
            let actions = commands.map(\.action)
            for (index, action) in actions.enumerated() {
                if index < processedOverlayVoiceCommandActions.count {
                    if processedOverlayVoiceCommandActions[index] != action {
                        applyOverlayVoiceCommand(action, provisional: provisional)
                        processedOverlayVoiceCommandActions[index] = action
                    }
                } else {
                    applyOverlayVoiceCommand(action, provisional: provisional)
                    processedOverlayVoiceCommandActions.append(action)
                }
            }
            if processedOverlayVoiceCommandActions.count > actions.count {
                processedOverlayVoiceCommandActions.removeLast(
                    processedOverlayVoiceCommandActions.count - actions.count
                )
            }
            if !provisional {
                processedOverlayVoiceCommandActions = []
            }
            return commands.last?.remainingText ?? ""
        }

        if provisional,
           SpokenOverlayCommandRecognizer.isPotentialCommand(
               text,
               showPhrase: showPhrase,
               hidePhrase: hidePhrase,
               clearPhrase: clearPhrase,
               nextQuestionPhrase: nextQuestionPhrase,
               dismissQuestionPhrase: dismissQuestionPhrase
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
        case .nextQuestion:
            if pendingStudentQuestions.isEmpty {
                statusText = "No pending student question"
            } else {
                presentNextStudentQuestion()
                statusText = "Next student question opened by voice command"
            }
        case .dismissQuestion:
            if presentedStudentQuestion == nil {
                statusText = "No student question is open"
            } else {
                dismissPresentedStudentQuestion()
                statusText = "Student question dismissed by voice command"
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
        processedOverlayVoiceCommandActions = []
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

    /// Last `limit` display lines at or past the clear boundary. Sequences
    /// are monotonic with position, so the visible segments form a suffix and
    /// this scan is O(limit), instead of filtering the whole timeline on
    /// every caption event of a long lecture.
    private func visibleOverlayLines(limit: Int = 3) -> [String] {
        guard let segments = session?.timeline.segments else { return [] }
        var lines: [String] = []
        for segment in segments.reversed() {
            if let overlayMinimumVisibleSequence,
               segment.sequence < overlayMinimumVisibleSequence {
                break
            }
            lines.append(segment.displayText)
            if lines.count == limit { break }
        }
        return lines.reversed()
    }

    func refreshOverlay(forceVisible: Bool = false) {
        let selectedScreen = NSScreen.screens.first { $0.displayID == selectedDisplayID }
            ?? NSScreen.main
        let lines = visibleOverlayLines()
        let provisional = overlayClearFinalizationPending
            ? nil
            : session?.timeline.provisional?.text
        publishRemoteCaptions(lines: lines, provisional: provisional)
        let shouldShow = forceVisible || overlayController.isVisible

        guard shouldShow, let selectedScreen else {
            overlayController.hide()
            return
        }

        overlayController.show(
            on: selectedScreen,
            lines: lines,
            provisional: provisional,
            question: presentedStudentQuestion?.text,
            pendingQuestionCount: pendingStudentQuestions.count,
            fontSize: captionFontSize
        )
    }

    private func handleIPhoneSharingStatus(_ status: LocalCaptionServerStatus) {
        iphoneSharingStatus = status
        switch status {
        case .ready(let url), .clientConnected(let url):
            iphonePairingURL = url
            publishRemoteCaptions()
        case .stopped, .starting, .failed:
            iphonePairingURL = nil
            studentQuestionURL = nil
            if case .stopped = status {
                studentQuestionStatus = .stopped
            }
        }
    }

    private func handleStudentQuestionStatus(
        _ status: StudentQuestionServerStatus
    ) {
        studentQuestionStatus = status
        switch status {
        case .ready(let url):
            studentQuestionURL = url
        case .stopped, .failed:
            studentQuestionURL = nil
        }
    }

    private func receiveStudentQuestion(
        _ submission: SubmittedClassroomQuestion
    ) {
        // The server has already answered "202 Accepted", so dropping here
        // is silent loss. The server admits at most 100 questions per hour;
        // this much larger cap is purely a memory bound and is unreachable
        // unless a multi-hour backlog is left entirely unmoderated.
        guard pendingStudentQuestions.count < 500 else { return }
        pendingStudentQuestions.append(ClassroomQuestion(
            id: submission.id,
            text: submission.text,
            submittedAt: submission.submittedAt
        ))
        refreshOverlay()
    }

    private func publishRemoteCaptions(
        lines: [String]? = nil,
        provisional: String? = nil
    ) {
        guard isIPhoneSharingActive else { return }
        remoteCaptionRevision &+= 1
        let visibleLines = lines ?? visibleOverlayLines()
        let visibleProvisional: String?
        if lines != nil {
            visibleProvisional = provisional
        } else {
            visibleProvisional = overlayClearFinalizationPending
                ? nil
                : session?.timeline.provisional?.text
        }
        captionServer.publish(RemoteCaptionSnapshot(
            finalized: visibleLines,
            provisional: visibleProvisional,
            sessionActive: hasActiveSession,
            revision: remoteCaptionRevision
        ))
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
