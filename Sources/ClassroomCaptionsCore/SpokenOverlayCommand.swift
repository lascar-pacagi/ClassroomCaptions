import Foundation

public enum SpokenOverlayAction: Equatable, Sendable {
    case show
    case hide
    case clear
}

public struct SpokenOverlayCommand: Equatable, Sendable {
    public let action: SpokenOverlayAction
    public let remainingText: String

    public init(action: SpokenOverlayAction, remainingText: String) {
        self.action = action
        self.remainingText = remainingText
    }
}

public enum SpokenOverlayCommandRecognizer {
    private struct Match {
        let action: SpokenOverlayAction
        let range: Range<String.Index>
    }

    private struct Token {
        let normalized: String
        let range: Range<String.Index>
    }

    public static func recognize(
        in text: String,
        triggerPhrase: String
    ) -> SpokenOverlayCommand? {
        let triggerTokens = tokens(in: triggerPhrase).map(\.normalized)
        guard !triggerTokens.isEmpty else { return nil }

        let captionTokens = tokens(in: text)
        guard captionTokens.count > triggerTokens.count else { return nil }

        for startIndex in 0 ... captionTokens.count - triggerTokens.count - 1 {
            let endIndex = startIndex + triggerTokens.count
            let candidate = captionTokens[startIndex ..< endIndex].map(\.normalized)
            guard zip(candidate, triggerTokens).allSatisfy(matches),
                  let action = action(for: captionTokens[endIndex].normalized) else {
                continue
            }

            let commandRange = captionTokens[startIndex].range.lowerBound
                ..< captionTokens[endIndex].range.upperBound
            var remaining = text
            remaining.removeSubrange(commandRange)
            remaining = cleanRemainingText(remaining)
            return SpokenOverlayCommand(action: action, remainingText: remaining)
        }
        return nil
    }

    public static func recognize(
        in text: String,
        showPhrase: String,
        hidePhrase: String,
        clearPhrase: String = ""
    ) -> SpokenOverlayCommand? {
        recognizeAll(
            in: text,
            showPhrase: showPhrase,
            hidePhrase: hidePhrase,
            clearPhrase: clearPhrase
        ).first
    }

    public static func recognizeAll(
        in text: String,
        showPhrase: String,
        hidePhrase: String,
        clearPhrase: String = ""
    ) -> [SpokenOverlayCommand] {
        let matches = (
            matches(showPhrase, in: text, action: .show)
                + matches(hidePhrase, in: text, action: .hide)
                + matches(clearPhrase, in: text, action: .clear)
                + (
                    normalizedWords(showPhrase) == ["sesame", "lumiere"]
                        ? showAliases(in: text)
                        : []
                )
        ).sorted {
            $0.range.lowerBound < $1.range.lowerBound
        }
        guard !matches.isEmpty else { return [] }

        var remaining = text
        for match in matches.reversed() {
            remaining.removeSubrange(match.range)
        }
        let cleaned = cleanRemainingText(remaining)
        return matches.enumerated().map { index, match in
            SpokenOverlayCommand(
                action: match.action,
                remainingText: index == matches.count - 1 ? cleaned : ""
            )
        }
    }

    public static func isPotentialCommand(
        _ text: String,
        showPhrase: String,
        hidePhrase: String,
        clearPhrase: String = ""
    ) -> Bool {
        isPotentialPhrase(text, expectedPhrase: showPhrase)
            || isPotentialPhrase(text, expectedPhrase: hidePhrase)
            || isPotentialPhrase(text, expectedPhrase: clearPhrase)
    }

    public static func isPotentialCommand(
        _ text: String,
        triggerPhrase: String
    ) -> Bool {
        let triggerTokens = tokens(in: triggerPhrase).map(\.normalized)
        let captionTokens = tokens(in: text).map(\.normalized)
        guard !triggerTokens.isEmpty, !captionTokens.isEmpty else { return false }

        let comparedCount = min(triggerTokens.count, captionTokens.count)
        return zip(
            captionTokens.prefix(comparedCount),
            triggerTokens.prefix(comparedCount)
        ).allSatisfy(matches)
    }

    private static func matches(_ candidate: String, _ expected: String) -> Bool {
        if candidate == expected { return true }

        let candidateRoot = withoutPluralS(candidate)
        let expectedRoot = withoutPluralS(expected)
        if candidateRoot == expectedRoot { return true }

        guard min(candidateRoot.count, expectedRoot.count) >= 5 else {
            return false
        }
        return editDistance(candidateRoot, expectedRoot) <= 1
    }

    private static func withoutPluralS(_ word: String) -> String {
        guard word.count >= 5, word.hasSuffix("s") else { return word }
        return String(word.dropLast())
    }

    private static func editDistance(_ lhs: String, _ rhs: String) -> Int {
        let left = Array(lhs)
        let right = Array(rhs)
        var previous = Array(0 ... right.count)

        for (leftIndex, leftCharacter) in left.enumerated() {
            var current = [leftIndex + 1]
            current.reserveCapacity(right.count + 1)
            for (rightIndex, rightCharacter) in right.enumerated() {
                current.append(min(
                    current[rightIndex] + 1,
                    previous[rightIndex + 1] + 1,
                    previous[rightIndex]
                        + (leftCharacter == rightCharacter ? 0 : 1)
                ))
            }
            previous = current
        }
        return previous[right.count]
    }

    private static func action(for token: String) -> SpokenOverlayAction? {
        if ["affiche", "afficher", "montre", "montrer"].contains(token) {
            return .show
        }
        if ["masque", "masquer", "cache", "cacher"].contains(token) {
            return .hide
        }
        return nil
    }

    private static func matches(
        _ phrase: String,
        in text: String,
        action: SpokenOverlayAction
    ) -> [Match] {
        let expectedTokens = tokens(in: phrase).map(\.normalized)
        guard !expectedTokens.isEmpty else { return [] }
        let captionTokens = tokens(in: text)
        guard captionTokens.count >= expectedTokens.count else { return [] }

        var result: [Match] = []
        for startIndex in 0 ... captionTokens.count - expectedTokens.count {
            let endIndex = startIndex + expectedTokens.count
            let candidate = captionTokens[startIndex ..< endIndex].map(\.normalized)
            guard zip(candidate, expectedTokens).allSatisfy(matches) else {
                continue
            }

            let commandRange = captionTokens[startIndex].range.lowerBound
                ..< captionTokens[endIndex - 1].range.upperBound
            result.append(Match(action: action, range: commandRange))
        }
        return result
    }

    private static func showAliases(in text: String) -> [Match] {
        let captionTokens = tokens(in: text)
        guard captionTokens.count >= 3 else { return [] }
        let expected = ["ces", "ames", "lumieres"]
        var result: [Match] = []
        for startIndex in 0 ... captionTokens.count - expected.count {
            let endIndex = startIndex + expected.count
            let candidate = captionTokens[startIndex ..< endIndex].map(\.normalized)
            guard zip(candidate, expected).allSatisfy(matches) else { continue }
            result.append(Match(
                action: .show,
                range: captionTokens[startIndex].range.lowerBound
                    ..< captionTokens[endIndex - 1].range.upperBound
            ))
        }
        return result
    }

    private static func isPotentialPhrase(
        _ text: String,
        expectedPhrase: String
    ) -> Bool {
        let expectedTokens = tokens(in: expectedPhrase).map(\.normalized)
        let captionTokens = tokens(in: text).map(\.normalized)
        guard !expectedTokens.isEmpty, !captionTokens.isEmpty,
              captionTokens.count <= expectedTokens.count else {
            return false
        }
        for (index, pair) in zip(captionTokens, expectedTokens).enumerated() {
            let (candidate, expected) = pair
            if matches(candidate, expected) {
                continue
            }
            let isLastProvisionalToken = index == captionTokens.count - 1
            if isLastProvisionalToken,
               candidate.count >= 2,
               expected.hasPrefix(candidate) {
                continue
            }
            return false
        }
        return true
    }

    private static func tokens(in text: String) -> [Token] {
        var result: [Token] = []
        var tokenStart: String.Index?

        func appendToken(endingAt end: String.Index) {
            guard let start = tokenStart else { return }
            let value = String(text[start ..< end])
                .folding(options: [.caseInsensitive, .diacriticInsensitive], locale: .current)
                .lowercased()
            result.append(Token(normalized: value, range: start ..< end))
            tokenStart = nil
        }

        var index = text.startIndex
        while index < text.endIndex {
            let character = text[index]
            if character.isLetter || character.isNumber {
                tokenStart = tokenStart ?? index
            } else {
                appendToken(endingAt: index)
            }
            index = text.index(after: index)
        }
        appendToken(endingAt: text.endIndex)
        return result
    }

    private static func normalizedWords(_ text: String) -> [String] {
        tokens(in: text).map(\.normalized)
    }

    private static func cleanRemainingText(_ text: String) -> String {
        guard !tokens(in: text).isEmpty else { return "" }
        var cleaned = text.trimmingCharacters(in: .whitespacesAndNewlines)
        cleaned = cleaned.replacingOccurrences(
            of: #"^\s*[,;:!?.–—]+\s*"#,
            with: "",
            options: .regularExpression
        )
        cleaned = cleaned.replacingOccurrences(
            of: #"\s+[,;:!?.–—]+\s*$"#,
            with: "",
            options: .regularExpression
        )
        cleaned = cleaned.replacingOccurrences(
            of: #"\.\s*\.\s*"#,
            with: ". ",
            options: .regularExpression
        )
        return cleaned.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
