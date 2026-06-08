import Foundation

public enum CaptionTransformation {
    public static func percentage(from original: String, to corrected: String) -> Double {
        let source = Array(original)
        let destination = Array(corrected)
        let maximumLength = max(source.count, destination.count)
        guard maximumLength > 0 else { return 0 }
        return min(
            100,
            100 * Double(editDistance(source, destination)) / Double(maximumLength)
        )
    }

    private static func editDistance(
        _ lhs: [Character],
        _ rhs: [Character]
    ) -> Int {
        guard !lhs.isEmpty else { return rhs.count }
        guard !rhs.isEmpty else { return lhs.count }
        var previous = Array(0 ... rhs.count)
        for (leftIndex, leftCharacter) in lhs.enumerated() {
            var current = [leftIndex + 1]
            current.reserveCapacity(rhs.count + 1)
            for (rightIndex, rightCharacter) in rhs.enumerated() {
                current.append(min(
                    current[rightIndex] + 1,
                    previous[rightIndex + 1] + 1,
                    previous[rightIndex]
                        + (leftCharacter == rightCharacter ? 0 : 1)
                ))
            }
            previous = current
        }
        return previous[rhs.count]
    }
}
