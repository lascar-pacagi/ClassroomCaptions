import Foundation

public struct AudioLevelReading: Equatable, Sendable {
    public let rms: Double
    public let peak: Double

    public init(rms: Double, peak: Double) {
        self.rms = rms
        self.peak = peak
    }

    public var normalizedLevel: Double {
        guard rms > 0 else { return 0 }
        let decibels = 20 * log10(rms)
        return min(1, max(0, (decibels + 60) / 60))
    }
}

public enum PCM16LevelMeter {
    public static func measure(_ data: Data) -> AudioLevelReading {
        let sampleCount = data.count / MemoryLayout<Int16>.size
        guard sampleCount > 0 else {
            return AudioLevelReading(rms: 0, peak: 0)
        }

        var sumOfSquares = 0.0
        var peak = 0.0
        data.withUnsafeBytes { rawBuffer in
            let samples = rawBuffer.bindMemory(to: Int16.self)
            for sample in samples.prefix(sampleCount) {
                let normalized = Double(sample) / Double(Int16.max)
                sumOfSquares += normalized * normalized
                peak = max(peak, abs(normalized))
            }
        }

        return AudioLevelReading(
            rms: sqrt(sumOfSquares / Double(sampleCount)),
            peak: peak
        )
    }
}
