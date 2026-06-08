import Darwin
import Foundation

enum ProcessMemory {
    static func physicalFootprintBytes() -> UInt64? {
        residentSizeBytes(processID: getpid())
    }

    static func physicalFootprintBytes(processID: pid_t) -> UInt64? {
        residentSizeBytes(processID: processID)
    }

    private static func residentSizeBytes(processID: pid_t) -> UInt64? {
        var info = proc_taskinfo()
        let expectedSize = MemoryLayout<proc_taskinfo>.size
        let result = withUnsafeMutablePointer(to: &info) { pointer in
            proc_pidinfo(
                processID,
                PROC_PIDTASKINFO,
                0,
                pointer,
                Int32(expectedSize)
            )
        }
        guard result == expectedSize else { return nil }
        return info.pti_resident_size
    }
}
