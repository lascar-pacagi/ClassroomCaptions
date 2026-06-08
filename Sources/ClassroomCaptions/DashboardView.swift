import ClassroomCaptionsCore
import SwiftUI

struct DashboardView: View {
    @Bindable var model: ClassroomAppModel

    var body: some View {
        NavigationSplitView {
            List {
                Label("Live Session", systemImage: "captions.bubble")
                    .fontWeight(.semibold)
                Label("Transcript", systemImage: "doc.text")
                    .foregroundStyle(.secondary)
                Label("iPhone", systemImage: "iphone")
                    .foregroundStyle(.secondary)
                Label("Models", systemImage: "cpu")
                    .foregroundStyle(.secondary)
            }
            .navigationSplitViewColumnWidth(min: 180, ideal: 210)
        } detail: {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    header
                    controls
                    diagnostics
                    microphoneSettings
                    archiveSettings
                    voxtralSettings
                    correctionSettings
                    overlaySettings
                    manualInput
                    transcript
                }
                .padding(28)
            }
            .navigationTitle("Classroom Captions")
        }
        .onChange(of: model.selectedDisplayID) {
            model.refreshOverlay()
        }
        .onChange(of: model.captionFontSize) {
            model.refreshOverlay()
        }
        .onChange(of: model.correctionEnabled) {
            model.correctionSettingChanged()
        }
    }

    private var header: some View {
        HStack {
            VStack(alignment: .leading, spacing: 5) {
                Text("Classroom Session")
                    .font(.largeTitle.bold())
                Text(model.statusText)
                    .foregroundStyle(model.isListening ? .green : .secondary)
            }
            Spacer()
            Circle()
                .fill(model.isListening ? Color.green : Color.secondary.opacity(0.35))
                .frame(width: 12, height: 12)
                .accessibilityLabel(model.isListening ? "Listening" : "Not listening")
        }
    }

    private var controls: some View {
        GroupBox("Session") {
            HStack(spacing: 12) {
                Button(sessionButtonTitle) {
                    model.toggleSession()
                }
                .buttonStyle(.borderedProminent)
                .disabled(model.isStartingSession || model.isStoppingSession)

                Button(model.session?.phase == .paused ? "Resume" : "Pause") {
                    model.pauseOrResume()
                }
                .disabled(model.session?.phase != .listening && model.session?.phase != .paused)

                Button("Clear") {
                    model.clearSession()
                }
                .disabled(
                    model.session == nil
                        || model.hasActiveSession
                        || model.isStartingSession
                        || model.isStoppingSession
                )

                Spacer()

                Toggle("Correct finalized captions", isOn: $model.correctionEnabled)
                    .toggleStyle(.switch)
            }
            .padding(.vertical, 6)
        }
    }

    private var sessionButtonTitle: String {
        if model.isStoppingSession {
            return "Exporting..."
        }
        if model.isStartingSession {
            return "Starting..."
        }
        return model.hasActiveSession ? "Stop Session" : "Start Session"
    }

    @ViewBuilder
    private var diagnostics: some View {
        GroupBox("Live Diagnostics") {
            VStack(alignment: .leading, spacing: 12) {
                Toggle(
                    "Show live model and memory statistics",
                    isOn: $model.showLiveDiagnostics
                )
                .toggleStyle(.switch)

                if model.showLiveDiagnostics {
                    Grid(
                        alignment: .leading,
                        horizontalSpacing: 18,
                        verticalSpacing: 8
                    ) {
                        GridRow {
                            Text("Voxtral")
                            Text("\(model.voxtralGeneratedTokens) tokens")
                            Text(
                                "\(model.voxtralTokensPerSecond, format: .number.precision(.fractionLength(1))) tok/s"
                            )
                        }

                        GridRow {
                            Text("Gemma last")
                            Text(gemmaTokenSummary)
                            Text(gemmaSpeedSummary)
                        }

                        GridRow {
                            Text("Gemma session")
                            Text("\(model.gemmaTotalGeneratedTokens) generated tokens")
                            Text(gemmaTransformationSummary)
                        }

                        GridRow {
                            Text("App + Voxtral")
                            Text(appMemorySummary)
                            Text("same process")
                                .foregroundStyle(.secondary)
                        }

                        GridRow {
                            Text("Gemma memory")
                            Text(gemmaMemorySummary)
                            Text("MLX server process")
                                .foregroundStyle(.secondary)
                        }

                        GridRow {
                            Text("Total memory")
                            Text(totalMemorySummary)
                            Text("resident memory")
                                .foregroundStyle(.secondary)
                        }
                    }
                    .font(.caption.monospacedDigit())

                    Text(
                        "Voxtral updates per decoded token. Gemma statistics "
                            + "update after each validated correction."
                    )
                    .font(.caption)
                    .foregroundStyle(.secondary)
                }
            }
            .padding(.vertical, 6)
        }
    }

    private var gemmaTokenSummary: String {
        guard let generated = model.gemmaGeneratedTokens else {
            return "Waiting for finalized caption"
        }
        if let prompt = model.gemmaPromptTokens {
            return "\(generated) generated / \(prompt) prompt"
        }
        return "\(generated) generated"
    }

    private var gemmaSpeedSummary: String {
        guard let speed = model.gemmaTokensPerSecond else { return "—" }
        return speed.formatted(
            .number.precision(.fractionLength(1))
        ) + " tok/s"
    }

    private var gemmaTransformationSummary: String {
        guard let percentage = model.gemmaTransformationPercentage else {
            return "Transformation: —"
        }
        return "Transformation: "
            + percentage.formatted(.number.precision(.fractionLength(1)))
            + "%"
    }

    private var appMemorySummary: String {
        guard let bytes = model.appMemoryFootprintBytes else { return "—" }
        return formatMemory(bytes)
    }

    private var gemmaMemorySummary: String {
        guard let bytes = model.gemmaMemoryFootprintBytes else {
            return model.correctionServerReady ? "Detecting…" : "Not loaded"
        }
        return formatMemory(bytes)
    }

    private var totalMemorySummary: String {
        guard let app = model.appMemoryFootprintBytes else { return "—" }
        return formatMemory(app + (model.gemmaMemoryFootprintBytes ?? 0))
    }

    private func formatMemory(_ bytes: UInt64) -> String {
        return ByteCountFormatter.string(
            fromByteCount: Int64(bytes),
            countStyle: .memory
        )
    }

    private var overlaySettings: some View {
        GroupBox("Caption Overlay") {
            Grid(alignment: .leading, horizontalSpacing: 16, verticalSpacing: 12) {
                GridRow {
                    Text("Display")
                    Picker("Display", selection: $model.selectedDisplayID) {
                        ForEach(model.displays) { display in
                            Text(display.name).tag(Optional(display.id))
                        }
                    }
                    .labelsHidden()
                }

                GridRow {
                    Text("Text size")
                    HStack {
                        Slider(value: $model.captionFontSize, in: 24 ... 64, step: 1)
                        Text("\(Int(model.captionFontSize)) pt")
                            .monospacedDigit()
                            .frame(width: 52, alignment: .trailing)
                    }
                }

                GridRow {
                    Text("Voice command")
                    Toggle(
                        "Enable spoken overlay controls",
                        isOn: $model.overlayVoiceCommandsEnabled
                    )
                    .toggleStyle(.switch)
                }

                GridRow {
                    Text("Show phrase")
                    TextField(
                        "Bonjour soleil bleu",
                        text: $model.overlayShowVoiceCommand
                    )
                    .textFieldStyle(.roundedBorder)
                    .disabled(!model.overlayVoiceCommandsEnabled)
                }

                GridRow {
                    Text("Hide phrase")
                    TextField(
                        "Bonjour soleil rouge",
                        text: $model.overlayHideVoiceCommand
                    )
                    .textFieldStyle(.roundedBorder)
                    .disabled(!model.overlayVoiceCommandsEnabled)
                }

                GridRow {
                    Text("Clear phrase")
                    TextField(
                        "Bonjour soleil blanc",
                        text: $model.overlayClearVoiceCommand
                    )
                    .textFieldStyle(.roundedBorder)
                    .disabled(!model.overlayVoiceCommandsEnabled)
                }
            }

            Text(
                "Say “\(showVoiceCommand)”, “\(hideVoiceCommand)”, "
                    + "or “\(clearVoiceCommand)”. Clear blanks the overlay "
                    + "without deleting the archived transcript. Commands are "
                    + "removed before correction and export."
            )
            .font(.caption)
            .foregroundStyle(.secondary)
            .padding(.top, 8)

            HStack {
                Button(model.isOverlayVisible ? "Hide Overlay" : "Show Overlay") {
                    model.toggleOverlay()
                }
                Button("Refresh Displays") {
                    model.refreshDisplays()
                }
                Button("Reset Position & Size") {
                    model.resetOverlayFrame()
                }
                Spacer()
                Text("Drag the top handle to move; drag the lower-right grip to resize.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .padding(.top, 10)
        }
    }

    private var showVoiceCommand: String {
        let command = model.overlayShowVoiceCommand.trimmingCharacters(
            in: .whitespacesAndNewlines
        )
        return command.isEmpty ? "Bonjour soleil bleu" : command
    }

    private var hideVoiceCommand: String {
        let command = model.overlayHideVoiceCommand.trimmingCharacters(
            in: .whitespacesAndNewlines
        )
        return command.isEmpty ? "Bonjour soleil rouge" : command
    }

    private var clearVoiceCommand: String {
        let command = model.overlayClearVoiceCommand.trimmingCharacters(
            in: .whitespacesAndNewlines
        )
        return command.isEmpty ? "Bonjour soleil blanc" : command
    }

    private var correctionSettings: some View {
        GroupBox("Gemma 4 Subtitle Correction") {
            VStack(alignment: .leading, spacing: 12) {
                Picker("Correction mode", selection: $model.correctionMode) {
                    Text("Standard").tag(CaptionCorrectionMode.standard)
                    Text("Science").tag(CaptionCorrectionMode.science)
                }
                .pickerStyle(.segmented)

                Text(
                    model.correctionMode == .science
                        ? "Science favors compact Unicode math, logic, set, probability, and code notation."
                        : "Standard performs conservative proofreading with only common notation."
                )
                .font(.caption)
                .foregroundStyle(.secondary)

                Stepper(
                    "Previous captions: \(model.gemmaContextCaptionCount)",
                    value: $model.gemmaContextCaptionCount,
                    in: 0 ... 8
                )

                Text(
                    model.gemmaContextCaptionCount == 0
                        ? "Gemma receives only the current finalized caption."
                        : "Previous captions are quoted as reference; only the current caption may be returned."
                )
                .font(.caption)
                .foregroundStyle(.secondary)

                Grid(alignment: .leading, horizontalSpacing: 16, verticalSpacing: 10) {
                    GridRow {
                        Text("Server")
                        TextField(
                            "MLX-LM server executable",
                            text: $model.gemmaServerExecutable
                        )
                        .textFieldStyle(.roundedBorder)
                    }

                    GridRow {
                        Text("Model")
                        TextField(
                            "Local model path or Hugging Face ID",
                            text: $model.gemmaModelPath
                        )
                        .textFieldStyle(.roundedBorder)
                    }

                    GridRow {
                        Text("Endpoint")
                        TextField(
                            "Loopback endpoint",
                            text: $model.gemmaEndpoint
                        )
                        .textFieldStyle(.roundedBorder)
                    }
                }
                .disabled(model.hasActiveSession || model.isStartingSession)

                HStack(spacing: 14) {
                    Label(
                        model.correctionServerReady ? "Ready" : "Not ready",
                        systemImage: model.correctionServerReady
                            ? "checkmark.circle.fill" : "circle"
                    )
                    .foregroundStyle(
                        model.correctionServerReady ? .green : .secondary
                    )

                    Text("Queue: \(model.correctionQueueDepth)")
                        .monospacedDigit()

                    if let latency = model.lastCorrectionLatency {
                        Text(
                            "Last: \(latency, format: .number.precision(.fractionLength(2))) s"
                        )
                        .monospacedDigit()
                    }

                    Spacer()
                }
                .font(.caption)

                if let error = model.correctionError {
                    Text(error)
                        .font(.caption)
                        .foregroundStyle(.red)
                } else {
                    Text(
                        "Questions and requests are proofread as quoted caption data. "
                            + "Gemma is forbidden from answering or executing them, "
                            + "and answer-like output is rejected."
                    )
                    .font(.caption)
                    .foregroundStyle(.secondary)
                }
            }
            .padding(.vertical, 6)
        }
    }

    private var microphoneSettings: some View {
        GroupBox("Microphone") {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Picker("Input", selection: $model.selectedMicrophoneID) {
                        ForEach(model.microphones) { microphone in
                            Text(microphone.name).tag(Optional(microphone.id))
                        }
                    }
                    .disabled(model.isListening)

                    Button("Refresh") {
                        model.refreshMicrophones()
                    }
                    .disabled(model.isListening)
                }

                HStack(spacing: 12) {
                    Text("Level")
                    ProgressView(value: model.microphoneLevel)
                        .progressViewStyle(.linear)
                    Text(ByteCountFormatter.string(
                        fromByteCount: Int64(model.capturedAudioBytes),
                        countStyle: .memory
                    ))
                    .font(.caption.monospacedDigit())
                    .foregroundStyle(.secondary)
                }

                if let microphoneError = model.microphoneError {
                    Text(microphoneError)
                        .font(.callout)
                        .foregroundStyle(.red)
                } else {
                    Text("Audio is converted locally to 16 kHz mono PCM for Voxtral.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .padding(.vertical, 6)
        }
    }

    private var archiveSettings: some View {
        GroupBox("Session Recording") {
            VStack(alignment: .leading, spacing: 12) {
                Toggle(
                    "Record microphone audio and export transcripts",
                    isOn: $model.recordSessions
                )
                .toggleStyle(.switch)
                .disabled(model.hasActiveSession || model.isStartingSession)

                HStack {
                    Text("Folder")
                    TextField(
                        "Session archive directory",
                        text: $model.sessionArchiveDirectory
                    )
                    .textFieldStyle(.roundedBorder)
                    .disabled(
                        model.hasActiveSession
                            || model.isStartingSession
                            || !model.recordSessions
                    )
                }

                HStack {
                    if let archiveURL = model.lastSessionArchiveURL {
                        Text(archiveURL.path)
                            .font(.caption.monospaced())
                            .lineLimit(1)
                            .truncationMode(.middle)
                        Spacer()
                        Button("Show in Finder") {
                            model.revealLastSessionArchive()
                        }
                    } else {
                        Text("Each session exports audio.wav, transcript.txt, transcript.json, and session.json.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                if let archiveError = model.archiveError {
                    Text(archiveError)
                        .font(.callout)
                        .foregroundStyle(.red)
                }
            }
            .padding(.vertical, 6)
        }
    }

    private var voxtralSettings: some View {
        GroupBox("Voxtral Realtime") {
            Grid(alignment: .leading, horizontalSpacing: 16, verticalSpacing: 10) {
                GridRow {
                    Text("Backend")
                    Picker("Backend", selection: $model.transcriptionBackend) {
                        ForEach(TranscriptionBackend.allCases) { backend in
                            Text(backend.title).tag(backend)
                        }
                    }
                    .labelsHidden()
                    .disabled(model.isListening || model.isStartingSession)
                }

                if model.transcriptionBackend == .embedded {
                    GridRow {
                        Text("Model directory")
                        TextField("Official Voxtral model directory", text: $model.voxtralModelDirectory)
                            .textFieldStyle(.roundedBorder)
                            .disabled(model.isListening || model.isStartingSession)
                    }

                    GridRow {
                        Text("Max context")
                        HStack {
                            Slider(
                                value: $model.voxtralContextSeconds,
                                in: 40 ... 320,
                                step: 20
                            )
                            Text("\(Int(model.voxtralContextSeconds)) s")
                                .monospacedDigit()
                                .frame(width: 58, alignment: .trailing)
                        }
                        .disabled(model.hasActiveSession || model.isStartingSession)
                    }
                } else {
                    GridRow {
                        Text("Endpoint")
                        TextField("WebSocket endpoint", text: $model.voxtralEndpoint)
                            .textFieldStyle(.roundedBorder)
                            .disabled(model.isListening || model.voxtralConnected)
                    }
                    GridRow {
                        Text("Model")
                        TextField("Model identifier", text: $model.voxtralModel)
                            .textFieldStyle(.roundedBorder)
                            .disabled(model.isListening || model.voxtralConnected)
                    }
                }

                GridRow {
                    Text("Model delay")
                    HStack {
                        Slider(
                            value: $model.commitIntervalMilliseconds,
                            in: 240 ... 1_200,
                            step: 80
                        )
                        Text("\(Int(model.commitIntervalMilliseconds)) ms")
                            .monospacedDigit()
                            .frame(width: 72, alignment: .trailing)
                    }
                    .disabled(model.isListening || model.isStartingSession)
                }
            }

            if model.transcriptionBackend == .embedded {
                Text(
                    "The context setting limits decoder KV history; Voxtral may "
                        + "reset earlier at natural EOS boundaries. The acoustic "
                        + "encoder keeps its fixed rolling 750-position window."
                )
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .padding(.top, 8)
            } else {
                Text("Compatibility mode for comparison with voxmlx or vLLM servers.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .padding(.top, 8)
            }

            HStack {
                Label(
                    model.voxtralConnected ? "Connected" : "Disconnected",
                    systemImage: model.voxtralConnected
                        ? "checkmark.circle.fill" : "circle"
                )
                .foregroundStyle(model.voxtralConnected ? .green : .secondary)
                Spacer()
                if let latency = model.firstCaptionLatency {
                    Text("First caption: \(latency, format: .number.precision(.fractionLength(2))) s")
                        .font(.caption.monospacedDigit())
                } else {
                    Text("First-caption latency will appear during the test.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .padding(.top, 8)
        }
    }

    private var manualInput: some View {
        GroupBox("Development Caption Input") {
            VStack(alignment: .leading, spacing: 10) {
                TextField("Enter a caption to exercise the timeline and overlay", text: $model.manualCaptionText)
                    .textFieldStyle(.roundedBorder)
                    .onSubmit {
                        model.submitManualCaption()
                    }

                HStack {
                    Button("Preview as Provisional") {
                        model.previewProvisionalCaption()
                    }
                    Button("Finalize Caption") {
                        model.submitManualCaption()
                    }
                    .buttonStyle(.borderedProminent)
                    Spacer()
                    Text("This control will be replaced by Voxtral events.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .padding(.vertical, 6)
        }
    }

    private var transcript: some View {
        GroupBox("Recent Captions") {
            VStack(alignment: .leading, spacing: 10) {
                if model.recentSegments.isEmpty {
                    ContentUnavailableView(
                        "No Captions Yet",
                        systemImage: "captions.bubble",
                        description: Text("Start a session and finalize a development caption.")
                    )
                    .frame(maxWidth: .infinity)
                } else {
                    ForEach(model.recentSegments) { segment in
                        HStack(alignment: .firstTextBaseline, spacing: 12) {
                            Text("\(segment.sequence + 1)")
                                .font(.caption.monospacedDigit())
                                .foregroundStyle(.secondary)
                                .frame(width: 24, alignment: .trailing)
                            Text(segment.displayText)
                                .frame(maxWidth: .infinity, alignment: .leading)
                            correctionBadge(for: segment.correctionState)
                        }
                        Divider()
                    }
                }
            }
            .padding(.vertical, 6)
        }
    }

    private func correctionBadge(for state: CaptionCorrectionState) -> some View {
        Text(state.rawValue)
            .font(.caption2)
            .padding(.horizontal, 7)
            .padding(.vertical, 3)
            .background(.quaternary, in: Capsule())
    }
}
