import Foundation

public enum SpokenOverlayAction: Equatable, Sendable {
    case show
    case hide
    case clear
    case nextQuestion
    case dismissQuestion
    case scrollUp
    case scrollDown
    case toggleAnswer
}

/// Result of scanning a transcript for the keyword-framed model question used by
/// the Assistant mode ("model question start ... model question end"). Detection
/// works on a single transcript; the app accumulates across segments.
public struct ModelQuestionScan: Equatable, Sendable {
    public enum Kind: Equatable, Sendable {
        /// No framing phrase present.
        case none
        /// A start phrase opened a question that this transcript does not close.
        case opens
        /// An end phrase closed a question opened in an earlier segment.
        case closes
        /// Both phrases present, start before end: a whole question in one go.
        case complete
    }

    public let kind: Kind
    /// Caption text before the start phrase (stays an ordinary subtitle).
    public let before: String
    /// The question itself, between the framing phrases.
    public let question: String
    /// Caption text after the end phrase (stays an ordinary subtitle).
    public let after: String

    public init(kind: Kind, before: String, question: String, after: String) {
        self.kind = kind
        self.before = before
        self.question = question
        self.after = after
    }
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
        clearPhrase: String = "",
        nextQuestionPhrase: String = "",
        dismissQuestionPhrase: String = "",
        scrollUpPhrase: String = "",
        scrollDownPhrase: String = "",
        toggleAnswerPhrase: String = ""
    ) -> SpokenOverlayCommand? {
        recognizeAll(
            in: text,
            showPhrase: showPhrase,
            hidePhrase: hidePhrase,
            clearPhrase: clearPhrase,
            nextQuestionPhrase: nextQuestionPhrase,
            dismissQuestionPhrase: dismissQuestionPhrase,
            scrollUpPhrase: scrollUpPhrase,
            scrollDownPhrase: scrollDownPhrase,
            toggleAnswerPhrase: toggleAnswerPhrase
        ).first
    }

    public static func recognizeAll(
        in text: String,
        showPhrase: String,
        hidePhrase: String,
        clearPhrase: String = "",
        nextQuestionPhrase: String = "",
        dismissQuestionPhrase: String = "",
        scrollUpPhrase: String = "",
        scrollDownPhrase: String = "",
        toggleAnswerPhrase: String = ""
    ) -> [SpokenOverlayCommand] {
        // Tokenizing is the expensive step (per-word allocation plus locale
        // diacritic folding over the whole provisional text); do it once and
        // share the tokens across every phrase matcher.
        let captionTokens = tokens(in: text)
        let matches = (
            matches(showPhrase, captionTokens: captionTokens, action: .show)
                + matches(hidePhrase, captionTokens: captionTokens, action: .hide)
                + matches(clearPhrase, captionTokens: captionTokens, action: .clear)
                + matches(
                    nextQuestionPhrase,
                    captionTokens: captionTokens,
                    action: .nextQuestion
                )
                + matches(
                    dismissQuestionPhrase,
                    captionTokens: captionTokens,
                    action: .dismissQuestion
                )
                + matches(
                    scrollUpPhrase,
                    captionTokens: captionTokens,
                    action: .scrollUp
                )
                + matches(
                    scrollDownPhrase,
                    captionTokens: captionTokens,
                    action: .scrollDown
                )
                + matches(
                    toggleAnswerPhrase,
                    captionTokens: captionTokens,
                    action: .toggleAnswer
                )
                + (
                    normalizedWords(showPhrase) == ["sesame", "lumiere"]
                        ? showAliases(in: captionTokens)
                        : []
                )
        ).sorted {
            if $0.range.lowerBound != $1.range.lowerBound {
                return $0.range.lowerBound < $1.range.lowerBound
            }
            return $0.range.upperBound > $1.range.upperBound
        }
        guard !matches.isEmpty else { return [] }

        // Distinct phrases may produce overlapping matches (one phrase a
        // prefix of another, or two commands configured with the same words).
        // Removing one range invalidates String indices inside any range that
        // overlaps it, so keep the longest match at each position and drop
        // whatever it overlaps before editing the text.
        var acceptedIndices: [Int] = []
        var lastUpperBound: String.Index?
        for (index, match) in matches.enumerated() {
            if let bound = lastUpperBound, match.range.lowerBound < bound {
                continue
            }
            acceptedIndices.append(index)
            lastUpperBound = match.range.upperBound
        }
        let accepted = acceptedIndices.map { matches[$0] }

        var remaining = text
        for match in accepted.reversed() {
            remaining.removeSubrange(match.range)
        }
        let cleaned = cleanRemainingText(remaining)
        return accepted.enumerated().map { index, match in
            SpokenOverlayCommand(
                action: match.action,
                remainingText: index == accepted.count - 1 ? cleaned : ""
            )
        }
    }

    public static func isPotentialCommand(
        _ text: String,
        showPhrase: String,
        hidePhrase: String,
        clearPhrase: String = "",
        nextQuestionPhrase: String = "",
        dismissQuestionPhrase: String = "",
        scrollUpPhrase: String = "",
        scrollDownPhrase: String = "",
        toggleAnswerPhrase: String = "",
        modelQuestionStartPhrase: String = "",
        modelQuestionEndPhrase: String = ""
    ) -> Bool {
        let captionTokens = tokens(in: text).map(\.normalized)
        guard !captionTokens.isEmpty else { return false }
        return isPotentialPhrase(captionTokens, expectedPhrase: showPhrase)
            || isPotentialPhrase(captionTokens, expectedPhrase: hidePhrase)
            || isPotentialPhrase(captionTokens, expectedPhrase: clearPhrase)
            || isPotentialPhrase(
                captionTokens,
                expectedPhrase: nextQuestionPhrase
            )
            || isPotentialPhrase(
                captionTokens,
                expectedPhrase: dismissQuestionPhrase
            )
            || isPotentialPhrase(captionTokens, expectedPhrase: scrollUpPhrase)
            || isPotentialPhrase(captionTokens, expectedPhrase: scrollDownPhrase)
            || isPotentialPhrase(
                captionTokens,
                expectedPhrase: toggleAnswerPhrase
            )
            || isPotentialPhrase(
                captionTokens,
                expectedPhrase: modelQuestionStartPhrase
            )
            || isPotentialPhrase(
                captionTokens,
                expectedPhrase: modelQuestionEndPhrase
            )
    }

    /// Scans one transcript for the Assistant-mode framing phrases and splits it
    /// into the caption text before the start phrase, the question between the
    /// phrases, and the caption text after the end phrase. The end phrase only
    /// counts when it follows the start phrase (or, for `.closes`, when no start
    /// phrase is present — the question was opened in an earlier segment).
    public static func scanModelQuestion(
        in text: String,
        startPhrase: String,
        endPhrase: String
    ) -> ModelQuestionScan {
        let captionTokens = tokens(in: text)
        let starts = matches(startPhrase, captionTokens: captionTokens, action: .show)
        let ends = matches(endPhrase, captionTokens: captionTokens, action: .hide)

        let start = starts.first
        let end: Match?
        if let start {
            end = ends.first { $0.range.lowerBound >= start.range.upperBound }
        } else {
            end = ends.first
        }

        func slice(_ range: Range<String.Index>) -> String {
            cleanRemainingText(String(text[range]))
        }
        func trimmed(_ range: Range<String.Index>) -> String {
            String(text[range]).trimmingCharacters(
                in: .whitespacesAndNewlines.union(
                    CharacterSet(charactersIn: ".,;:!?")
                )
            )
        }

        switch (start, end) {
        case let (start?, end?):
            return ModelQuestionScan(
                kind: .complete,
                before: slice(text.startIndex ..< start.range.lowerBound),
                question: trimmed(start.range.upperBound ..< end.range.lowerBound),
                after: slice(end.range.upperBound ..< text.endIndex)
            )
        case let (start?, nil):
            return ModelQuestionScan(
                kind: .opens,
                before: slice(text.startIndex ..< start.range.lowerBound),
                question: trimmed(start.range.upperBound ..< text.endIndex),
                after: ""
            )
        case let (nil, end?):
            return ModelQuestionScan(
                kind: .closes,
                before: "",
                question: trimmed(text.startIndex ..< end.range.lowerBound),
                after: slice(end.range.upperBound ..< text.endIndex)
            )
        case (nil, nil):
            return ModelQuestionScan(
                kind: .none,
                before: text,
                question: "",
                after: ""
            )
        }
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
        captionTokens: [Token],
        action: SpokenOverlayAction
    ) -> [Match] {
        let expectedTokens = tokens(in: phrase).map(\.normalized)
        guard !expectedTokens.isEmpty else { return [] }
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

    private static func showAliases(in captionTokens: [Token]) -> [Match] {
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
        _ captionTokens: [String],
        expectedPhrase: String
    ) -> Bool {
        let expectedTokens = tokens(in: expectedPhrase).map(\.normalized)
        guard !expectedTokens.isEmpty,
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
