import Foundation

public enum CaptionCorrectionValidationError: LocalizedError, Equatable, Sendable {
    case empty
    case containsControlMarkup
    case answerLikeResponse
    case excessiveLengthChange
    case excessiveRewrite
    case questionWasAnswered

    public var errorDescription: String? {
        switch self {
        case .empty:
            return "Gemma returned an empty correction."
        case .containsControlMarkup:
            return "Gemma returned reasoning or control markup."
        case .answerLikeResponse:
            return "Gemma returned an answer or explanation instead of a correction."
        case .excessiveLengthChange:
            return "Gemma changed the caption length too much."
        case .excessiveRewrite:
            return "Gemma rewrote too much of the caption."
        case .questionWasAnswered:
            return "Gemma appears to have answered a captioned question."
        }
    }
}

public enum CaptionCorrectionValidator {
    public static func validate(
        rawText: String,
        candidate: String,
        mode: CaptionCorrectionMode = .standard
    ) throws -> String {
        let raw = rawText.trimmingCharacters(in: .whitespacesAndNewlines)
        let corrected = candidate.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !corrected.isEmpty else {
            throw CaptionCorrectionValidationError.empty
        }

        let lowered = corrected.lowercased()
        let forbiddenMarkup = [
            "<think", "</think", "<|", "|>", "reasoning:", "analysis:",
            "```", "<tool", "</tool", "\\frac", "\\mathbb", "\\sum",
        ]
        guard !forbiddenMarkup.contains(where: lowered.contains) else {
            throw CaptionCorrectionValidationError.containsControlMarkup
        }

        let answerPrefixes = [
            "answer:", "the answer", "réponse :", "la réponse", "voici ",
            "bien sûr", "certainement", "yes,", "no,", "oui,", "non,",
            "to answer", "pour répondre", "explication :", "explanation:",
        ]
        guard !answerPrefixes.contains(where: lowered.hasPrefix) else {
            throw CaptionCorrectionValidationError.answerLikeResponse
        }

        let rawWords = comparisonWords(in: raw)
        let correctedWords = comparisonWords(in: corrected)
        guard !rawWords.isEmpty else { return corrected }
        let notationHeavy = mode == .science || isNotationHeavy(raw)

        if looksLikeQuestion(raw) {
            let questionUpperBound = max(rawWords.count + 3, Int(Double(rawWords.count) * 1.25))
            guard correctedWords.count <= questionUpperBound else {
                throw CaptionCorrectionValidationError.questionWasAnswered
            }
            guard looksLikeQuestion(corrected) else {
                throw CaptionCorrectionValidationError.questionWasAnswered
            }
        }

        let lowerBound = max(
            1,
            Int(Double(rawWords.count) * (notationHeavy ? 0.30 : 0.55))
        )
        let upperBound = max(rawWords.count + 5, Int(Double(rawWords.count) * 1.45))
        guard correctedWords.count >= lowerBound, correctedWords.count <= upperBound else {
            throw CaptionCorrectionValidationError.excessiveLengthChange
        }

        let distance = editDistance(rawWords, correctedWords)
        let allowedEdits = max(
            4,
            Int(
                Double(max(rawWords.count, correctedWords.count))
                    * (notationHeavy ? 0.80 : 0.48)
            )
        )
        guard distance <= allowedEdits else {
            throw CaptionCorrectionValidationError.excessiveRewrite
        }

        return corrected
    }

    private static func looksLikeQuestion(_ text: String) -> Bool {
        if text.contains("?") { return true }
        let first = words(in: text).first ?? ""
        let questionStarts: Set<String> = [
            "qui", "que", "quoi", "quel", "quelle", "quels", "quelles",
            "comment", "pourquoi", "quand", "où", "est-ce", "do", "does",
            "did", "what", "which", "who", "why", "how", "when", "where",
            "can", "could", "would", "should", "is", "are",
        ]
        return questionStarts.contains(first)
    }

    private static func words(in text: String) -> [String] {
        text.lowercased().split { character in
            !character.isLetter && !character.isNumber
        }
        .map(String.init)
    }

    private static func comparisonWords(in text: String) -> [String] {
        var normalized = text.lowercased()
        let replacements = [
            ("n'appartient pas à", " notmember "),
            ("n appartient pas à", " notmember "),
            ("appartient à l'ensemble des entiers naturels", " member naturals "),
            ("appartient a l ensemble des entiers naturels", " member naturals "),
            ("appartenant à l'ensemble des entiers naturels", " member naturals "),
            ("appartenant a l ensemble des entiers naturels", " member naturals "),
            ("ensemble des entiers naturels", " naturals "),
            ("entiers naturels", " naturals "),
            ("ensemble des entiers relatifs", " integers "),
            ("entiers relatifs", " integers "),
            ("ensemble des nombres rationnels", " rationals "),
            ("nombres rationnels", " rationals "),
            ("ensemble des nombres réels", " reals "),
            ("ensemble des réels", " reals "),
            ("nombres réels", " reals "),
            ("ensemble des nombres complexes", " complexes "),
            ("nombres complexes", " complexes "),
            ("appartenant à", " member "),
            ("appartenant a", " member "),
            ("appartient à", " member "),
            ("appartient a", " member "),
            ("pour tout", " forall "),
            ("il existe", " exists "),
            ("si et seulement si", " equivalent "),
            ("implique que", " implies "),
            ("intersection de", " intersection "),
            ("inter ", " intersection "),
            ("union de", " union "),
            ("ensemble vide", " emptyset "),
            ("plus petit ou égal à", " lessorequal "),
            ("plus petit ou égal", " lessorequal "),
            ("inférieur ou égal à", " lessorequal "),
            ("inférieur ou égal", " lessorequal "),
            ("supérieur ou égal à", " greaterorequal "),
            ("supérieur ou égal", " greaterorequal "),
            ("différent de", " notequal "),
            ("est égal à", " equals "),
            ("égal à", " equals "),
            ("o de ", " bigo "),
            ("o(", " bigo "),
            ("∉", " notmember "),
            ("∈", " member "),
            ("ℕ", " naturals "),
            ("ℤ", " integers "),
            ("ℚ", " rationals "),
            ("ℝ", " reals "),
            ("ℂ", " complexes "),
            ("∀", " forall "),
            ("∃", " exists "),
            ("⇔", " equivalent "),
            ("⇒", " implies "),
            ("∩", " intersection "),
            ("∪", " union "),
            ("∅", " emptyset "),
            ("≤", " lessorequal "),
            ("≥", " greaterorequal "),
            ("≠", " notequal "),
            ("=", " equals "),
            ("²", " squared "),
            (" carré", " squared"),
        ]
        for (source, replacement) in replacements {
            normalized = normalized.replacingOccurrences(
                of: source,
                with: replacement
            )
        }
        return words(in: normalized)
    }

    private static func isNotationHeavy(_ text: String) -> Bool {
        let lowered = text.lowercased()
        let cues = [
            "pour tout", "appartenant", "ensemble des", "il existe",
            "supérieur ou égal", "inférieur ou égal", "plus petit ou égal",
            "différent de", "non ", "alors", "si ", "somme", "puissance",
            "probabilité", "sachant", "inter ", "divisée par", "o de ",
            "crochet", "log n", "carré",
        ]
        return cues.reduce(into: 0) { count, cue in
            if lowered.contains(cue) {
                count += 1
            }
        } >= 4
    }

    private static func editDistance(_ lhs: [String], _ rhs: [String]) -> Int {
        guard !lhs.isEmpty else { return rhs.count }
        guard !rhs.isEmpty else { return lhs.count }
        var previous = Array(0 ... rhs.count)
        for (leftIndex, leftWord) in lhs.enumerated() {
            var current = [leftIndex + 1]
            current.reserveCapacity(rhs.count + 1)
            for (rightIndex, rightWord) in rhs.enumerated() {
                current.append(min(
                    current[rightIndex] + 1,
                    previous[rightIndex + 1] + 1,
                    previous[rightIndex] + (leftWord == rightWord ? 0 : 1)
                ))
            }
            previous = current
        }
        return previous[rhs.count]
    }
}
