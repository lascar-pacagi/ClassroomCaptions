import AudioToolbox
import CoreAudio
import Foundation

struct MicrophoneDevice: Identifiable, Hashable, Sendable {
    let id: String
    let name: String
}

enum AudioDeviceCatalog {
    static func inputDevices() -> [MicrophoneDevice] {
        allDeviceIDs()
            .filter(deviceHasInput)
            .compactMap { deviceID in
                guard let uid = stringProperty(
                    kAudioDevicePropertyDeviceUID,
                    deviceID: deviceID
                ) else {
                    return nil
                }
                let name = stringProperty(kAudioObjectPropertyName, deviceID: deviceID)
                    ?? "Microphone"
                return MicrophoneDevice(id: uid, name: name)
            }
            .sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    static func defaultInputDeviceUID() -> String? {
        guard let deviceID = defaultInputDeviceID() else { return nil }
        return stringProperty(kAudioDevicePropertyDeviceUID, deviceID: deviceID)
    }

    static func resolveDeviceID(uid: String?) -> AudioObjectID? {
        guard let uid, !uid.isEmpty else {
            return defaultInputDeviceID()
        }
        return allDeviceIDs().first { deviceID in
            deviceHasInput(deviceID)
                && stringProperty(kAudioDevicePropertyDeviceUID, deviceID: deviceID) == uid
        }
    }

    static func setInputDevice(_ deviceID: AudioObjectID, on audioUnit: AudioUnit) -> OSStatus {
        var mutableDeviceID = deviceID
        return AudioUnitSetProperty(
            audioUnit,
            kAudioOutputUnitProperty_CurrentDevice,
            kAudioUnitScope_Global,
            0,
            &mutableDeviceID,
            UInt32(MemoryLayout<AudioObjectID>.size)
        )
    }

    private static func defaultInputDeviceID() -> AudioObjectID? {
        var address = AudioObjectPropertyAddress(
            mSelector: kAudioHardwarePropertyDefaultInputDevice,
            mScope: kAudioObjectPropertyScopeGlobal,
            mElement: kAudioObjectPropertyElementMain
        )
        var deviceID = AudioObjectID(0)
        var size = UInt32(MemoryLayout<AudioObjectID>.size)
        let status = AudioObjectGetPropertyData(
            AudioObjectID(kAudioObjectSystemObject),
            &address,
            0,
            nil,
            &size,
            &deviceID
        )
        return status == noErr && deviceID != 0 ? deviceID : nil
    }

    private static func allDeviceIDs() -> [AudioObjectID] {
        var address = AudioObjectPropertyAddress(
            mSelector: kAudioHardwarePropertyDevices,
            mScope: kAudioObjectPropertyScopeGlobal,
            mElement: kAudioObjectPropertyElementMain
        )
        var size: UInt32 = 0
        guard AudioObjectGetPropertyDataSize(
            AudioObjectID(kAudioObjectSystemObject),
            &address,
            0,
            nil,
            &size
        ) == noErr, size > 0 else {
            return []
        }

        var devices = [AudioObjectID](
            repeating: 0,
            count: Int(size) / MemoryLayout<AudioObjectID>.size
        )
        let status = devices.withUnsafeMutableBufferPointer { buffer in
            AudioObjectGetPropertyData(
                AudioObjectID(kAudioObjectSystemObject),
                &address,
                0,
                nil,
                &size,
                buffer.baseAddress!
            )
        }
        return status == noErr ? devices : []
    }

    private static func deviceHasInput(_ deviceID: AudioObjectID) -> Bool {
        var address = AudioObjectPropertyAddress(
            mSelector: kAudioDevicePropertyStreamConfiguration,
            mScope: kAudioDevicePropertyScopeInput,
            mElement: kAudioObjectPropertyElementMain
        )
        var size: UInt32 = 0
        guard AudioObjectGetPropertyDataSize(
            deviceID,
            &address,
            0,
            nil,
            &size
        ) == noErr, size > 0 else {
            return false
        }

        let pointer = UnsafeMutableRawPointer.allocate(
            byteCount: Int(size),
            alignment: MemoryLayout<AudioBufferList>.alignment
        )
        defer { pointer.deallocate() }
        guard AudioObjectGetPropertyData(
            deviceID,
            &address,
            0,
            nil,
            &size,
            pointer
        ) == noErr else {
            return false
        }

        let list = pointer.assumingMemoryBound(to: AudioBufferList.self)
        return UnsafeMutableAudioBufferListPointer(list).contains {
            $0.mNumberChannels > 0
        }
    }

    private static func stringProperty(
        _ selector: AudioObjectPropertySelector,
        deviceID: AudioObjectID
    ) -> String? {
        var address = AudioObjectPropertyAddress(
            mSelector: selector,
            mScope: kAudioObjectPropertyScopeGlobal,
            mElement: kAudioObjectPropertyElementMain
        )
        var value: Unmanaged<CFString>?
        var size = UInt32(MemoryLayout<Unmanaged<CFString>?>.size)
        guard AudioObjectGetPropertyData(
            deviceID,
            &address,
            0,
            nil,
            &size,
            &value
        ) == noErr, let value else {
            return nil
        }
        let string = value.takeUnretainedValue() as String
        return string.isEmpty ? nil : string
    }
}
