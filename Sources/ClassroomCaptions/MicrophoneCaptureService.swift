@preconcurrency import AVFoundation
import AudioToolbox
import CoreAudio
import Foundation
import Synchronization

enum MicrophonePermission {
    case authorized
    case denied
    case restricted
    case notDetermined
}

enum MicrophoneCaptureError: LocalizedError {
    case deviceUnavailable
    case componentUnavailable
    case configuration(String, OSStatus)
    case invalidFormat

    var errorDescription: String? {
        switch self {
        case .deviceUnavailable:
            return "The selected microphone is unavailable."
        case .componentUnavailable:
            return "The macOS audio input component is unavailable."
        case .configuration(let step, let status):
            return "Microphone configuration failed at \(step) (OSStatus \(status))."
        case .invalidFormat:
            return "The microphone returned an invalid audio format."
        }
    }
}

private final class AudioRenderContext: @unchecked Sendable {
    let audioUnit: AudioUnit
    let inputFormat: AVAudioFormat
    let outputFormat: AVAudioFormat
    let converter: AVAudioConverter
    let handler: @Sendable (Data) -> Void
    let queue: DispatchQueue

    init(
        audioUnit: AudioUnit,
        inputFormat: AVAudioFormat,
        outputFormat: AVAudioFormat,
        converter: AVAudioConverter,
        handler: @escaping @Sendable (Data) -> Void,
        queue: DispatchQueue
    ) {
        self.audioUnit = audioUnit
        self.inputFormat = inputFormat
        self.outputFormat = outputFormat
        self.converter = converter
        self.handler = handler
        self.queue = queue
    }
}

private func microphoneInputCallback(
    _ reference: UnsafeMutableRawPointer,
    _ flags: UnsafeMutablePointer<AudioUnitRenderActionFlags>,
    _ timestamp: UnsafePointer<AudioTimeStamp>,
    _ busNumber: UInt32,
    _ frameCount: UInt32,
    _ data: UnsafeMutablePointer<AudioBufferList>?
) -> OSStatus {
    let context = Unmanaged<AudioRenderContext>.fromOpaque(reference)
        .takeUnretainedValue()
    guard let inputBuffer = AVAudioPCMBuffer(
        pcmFormat: context.inputFormat,
        frameCapacity: frameCount
    ) else {
        return noErr
    }
    inputBuffer.frameLength = frameCount

    let status = AudioUnitRender(
        context.audioUnit,
        flags,
        timestamp,
        busNumber,
        frameCount,
        inputBuffer.mutableAudioBufferList
    )
    guard status == noErr,
          let chunk = MicrophoneCaptureService.convert(
              inputBuffer,
              converter: context.converter,
              outputFormat: context.outputFormat
          ) else {
        return status
    }

    context.queue.async {
        context.handler(chunk)
    }
    return noErr
}

final class MicrophoneCaptureService: @unchecked Sendable {
    private struct State {
        var audioUnit: AudioUnit?
        var context: Unmanaged<AudioRenderContext>?
    }

    private let lock = NSLock()
    private var state = State()
    private let processingQueue = DispatchQueue(
        label: "ClassroomCaptions.microphone.processing",
        qos: .userInitiated
    )
    private let processingQueueKey = DispatchSpecificKey<Void>()
    private let outputFormat: AVAudioFormat

    init() {
        guard let format = AVAudioFormat(
            commonFormat: .pcmFormatInt16,
            sampleRate: 16_000,
            channels: 1,
            interleaved: true
        ) else {
            preconditionFailure("Unable to create the 16 kHz PCM output format.")
        }
        outputFormat = format
        processingQueue.setSpecific(key: processingQueueKey, value: ())
    }

    deinit {
        stop()
    }

    func permission() -> MicrophonePermission {
        switch AVCaptureDevice.authorizationStatus(for: .audio) {
        case .authorized: return .authorized
        case .denied: return .denied
        case .restricted: return .restricted
        case .notDetermined: return .notDetermined
        @unknown default: return .restricted
        }
    }

    func requestPermission() async -> Bool {
        switch permission() {
        case .authorized:
            return true
        case .notDetermined:
            return await AVCaptureDevice.requestAccess(for: .audio)
        case .denied, .restricted:
            return false
        }
    }

    func start(
        deviceUID: String?,
        handler: @escaping @Sendable (Data) -> Void
    ) throws {
        stop()
        guard let deviceID = AudioDeviceCatalog.resolveDeviceID(uid: deviceUID) else {
            throw MicrophoneCaptureError.deviceUnavailable
        }

        var description = AudioComponentDescription(
            componentType: kAudioUnitType_Output,
            componentSubType: kAudioUnitSubType_HALOutput,
            componentManufacturer: kAudioUnitManufacturer_Apple,
            componentFlags: 0,
            componentFlagsMask: 0
        )
        guard let component = AudioComponentFindNext(nil, &description) else {
            throw MicrophoneCaptureError.componentUnavailable
        }

        var optionalAudioUnit: AudioUnit?
        let creationStatus = AudioComponentInstanceNew(component, &optionalAudioUnit)
        guard creationStatus == noErr, let audioUnit = optionalAudioUnit else {
            throw MicrophoneCaptureError.configuration("create", creationStatus)
        }

        do {
            try configure(audioUnit, deviceID: deviceID, handler: handler)
        } catch {
            AudioComponentInstanceDispose(audioUnit)
            throw error
        }
    }

    func stop() {
        lock.lock()
        let audioUnit = state.audioUnit
        let context = state.context
        state = State()
        lock.unlock()

        if let audioUnit {
            AudioOutputUnitStop(audioUnit)
            AudioUnitUninitialize(audioUnit)
            AudioComponentInstanceDispose(audioUnit)
        }
        context?.release()
        if DispatchQueue.getSpecific(key: processingQueueKey) == nil {
            processingQueue.sync {}
        }
    }

    private func configure(
        _ audioUnit: AudioUnit,
        deviceID: AudioObjectID,
        handler: @escaping @Sendable (Data) -> Void
    ) throws {
        var enableInput: UInt32 = 1
        try requireNoError(
            AudioUnitSetProperty(
                audioUnit,
                kAudioOutputUnitProperty_EnableIO,
                kAudioUnitScope_Input,
                1,
                &enableInput,
                UInt32(MemoryLayout<UInt32>.size)
            ),
            step: "enable input"
        )

        var disableOutput: UInt32 = 0
        try requireNoError(
            AudioUnitSetProperty(
                audioUnit,
                kAudioOutputUnitProperty_EnableIO,
                kAudioUnitScope_Output,
                0,
                &disableOutput,
                UInt32(MemoryLayout<UInt32>.size)
            ),
            step: "disable output"
        )
        try requireNoError(
            AudioDeviceCatalog.setInputDevice(deviceID, on: audioUnit),
            step: "select device"
        )

        var streamDescription = AudioStreamBasicDescription()
        var streamDescriptionSize = UInt32(MemoryLayout<AudioStreamBasicDescription>.size)
        try requireNoError(
            AudioUnitGetProperty(
                audioUnit,
                kAudioUnitProperty_StreamFormat,
                kAudioUnitScope_Input,
                1,
                &streamDescription,
                &streamDescriptionSize
            ),
            step: "read device format"
        )
        guard streamDescription.mSampleRate > 0,
              let inputFormat = AVAudioFormat(streamDescription: &streamDescription),
              let converter = AVAudioConverter(from: inputFormat, to: outputFormat) else {
            throw MicrophoneCaptureError.invalidFormat
        }

        try requireNoError(
            AudioUnitSetProperty(
                audioUnit,
                kAudioUnitProperty_StreamFormat,
                kAudioUnitScope_Output,
                1,
                &streamDescription,
                streamDescriptionSize
            ),
            step: "set callback format"
        )

        let renderContext = AudioRenderContext(
            audioUnit: audioUnit,
            inputFormat: inputFormat,
            outputFormat: outputFormat,
            converter: converter,
            handler: handler,
            queue: processingQueue
        )
        let unmanagedContext = Unmanaged.passRetained(renderContext)
        var callback = AURenderCallbackStruct(
            inputProc: microphoneInputCallback,
            inputProcRefCon: unmanagedContext.toOpaque()
        )
        do {
            try requireNoError(
                AudioUnitSetProperty(
                    audioUnit,
                    kAudioOutputUnitProperty_SetInputCallback,
                    kAudioUnitScope_Global,
                    0,
                    &callback,
                    UInt32(MemoryLayout<AURenderCallbackStruct>.size)
                ),
                step: "install callback"
            )
            try requireNoError(AudioUnitInitialize(audioUnit), step: "initialize")
            try requireNoError(AudioOutputUnitStart(audioUnit), step: "start")
        } catch {
            unmanagedContext.release()
            throw error
        }

        lock.lock()
        state.audioUnit = audioUnit
        state.context = unmanagedContext
        lock.unlock()
    }

    private func requireNoError(_ status: OSStatus, step: String) throws {
        guard status == noErr else {
            throw MicrophoneCaptureError.configuration(step, status)
        }
    }

    fileprivate static func convert(
        _ inputBuffer: AVAudioPCMBuffer,
        converter: AVAudioConverter,
        outputFormat: AVAudioFormat
    ) -> Data? {
        let ratio = outputFormat.sampleRate / max(1, inputBuffer.format.sampleRate)
        let capacity = AVAudioFrameCount(
            max(1, Int(ceil(Double(inputBuffer.frameLength) * ratio)) + 32)
        )
        guard let outputBuffer = AVAudioPCMBuffer(
            pcmFormat: outputFormat,
            frameCapacity: capacity
        ) else {
            return nil
        }

        let suppliedInput = Mutex(false)
        var error: NSError?
        let status = converter.convert(to: outputBuffer, error: &error) { _, outputStatus in
            let alreadySupplied = suppliedInput.withLock { supplied in
                let previous = supplied
                supplied = true
                return previous
            }
            if alreadySupplied {
                outputStatus.pointee = .noDataNow
                return nil
            }
            outputStatus.pointee = .haveData
            return inputBuffer
        }
        guard error == nil,
              status == .haveData || status == .inputRanDry,
              outputBuffer.frameLength > 0,
              let samples = outputBuffer.int16ChannelData else {
            return nil
        }

        return Data(
            bytes: samples[0],
            count: Int(outputBuffer.frameLength) * MemoryLayout<Int16>.size
        )
    }
}
