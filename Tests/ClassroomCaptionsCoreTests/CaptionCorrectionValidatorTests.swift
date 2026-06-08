import ClassroomCaptionsCore
import XCTest

final class CaptionCorrectionValidatorTests: XCTestCase {
    func testAcceptsConservativeFrenchCorrection() throws {
        let result = try CaptionCorrectionValidator.validate(
            rawText: "On utilise un mutex pour protéger la section critiques entre les deux thread.",
            candidate: "On utilise un mutex pour protéger la section critique entre les deux threads."
        )

        XCTAssertEqual(
            result,
            "On utilise un mutex pour protéger la section critique entre les deux threads."
        )
    }

    func testPreservesQuestionInsteadOfAnsweringIt() throws {
        let result = try CaptionCorrectionValidator.validate(
            rawText: "Pourquoi la suppression dans un arbre AVL reste elle en O de log n ?",
            candidate: "Pourquoi la suppression dans un arbre AVL reste-t-elle en O(log n) ?"
        )

        XCTAssertTrue(result.hasSuffix("?"))
    }

    func testAcceptsSpokenComplexityAndEqualityNotation() throws {
        let result = try CaptionCorrectionValidator.validate(
            rawText: "O de n est égal à un dans cet exemple.",
            candidate: "O(n) = 1 dans cet exemple."
        )

        XCTAssertEqual(result, "O(n) = 1 dans cet exemple.")
    }

    func testAcceptsTechnicalNotationInsideQuestion() throws {
        let result = try CaptionCorrectionValidator.validate(
            rawText: "Est ce que O de n est plus petit ou égal à O de n carré ?",
            candidate: "Est-ce que O(n) ≤ O(n²) ?"
        )

        XCTAssertEqual(result, "Est-ce que O(n) ≤ O(n²) ?")
    }

    func testAcceptsDenseUnicodeMathLogicAndCodeRendering() throws {
        let raw = """
        Pour tout x appartenant à l ensemble des réels, si x est supérieur ou égal à zéro et non x est égal à zéro, alors il existe un y appartenant aux entiers tel que y carré est inférieur ou égal à x plus un. Ensuite, la somme pour i allant de zéro à n moins un de deux puissance i est égal à deux puissance n moins un, la probabilité de A sachant B est égal à la probabilité de A inter B divisée par la probabilité de B, et l algorithme parcourt tableau crochet i crochet tant que i est plus petit que n, donc sa complexité est en O de n log n.
        """
        let candidate = """
        ∀x ∈ ℝ, si x ≥ 0 et x ≠ 0, alors ∃y ∈ ℤ tel que y² ≤ x + 1. Ensuite, Σ(i=0…n−1) 2ⁱ = 2ⁿ − 1, P(A|B) = P(A ∩ B) / P(B), et l'algorithme parcourt tableau[i] tant que i < n, donc sa complexité est O(n log n).
        """

        XCTAssertEqual(
            try CaptionCorrectionValidator.validate(
                rawText: raw,
                candidate: candidate
            ),
            candidate
        )
    }

    func testScienceModeAcceptsCompactSetMembership() throws {
        let result = try CaptionCorrectionValidator.validate(
            rawText: "Si n appartient à l'ensemble des entiers naturels, alors n est supérieur ou égal à zéro.",
            candidate: "Si n ∈ ℕ, alors n ≥ 0.",
            mode: .science
        )

        XCTAssertEqual(result, "Si n ∈ ℕ, alors n ≥ 0.")
    }

    func testScienceModeStillRejectsAnswerAppendedToQuestion() {
        XCTAssertThrowsError(try CaptionCorrectionValidator.validate(
            rawText: "Est ce que n appartient à l'ensemble des entiers naturels ?",
            candidate: "Est-ce que n ∈ ℕ ? Oui, n appartient bien à ℕ.",
            mode: .science
        )) { error in
            XCTAssertEqual(
                error as? CaptionCorrectionValidationError,
                .questionWasAnswered
            )
        }
    }

    func testRejectsLatexForPlainTextOverlay() {
        XCTAssertThrowsError(try CaptionCorrectionValidator.validate(
            rawText: "Pour tout x appartenant aux réels.",
            candidate: "Pour tout $x \\in \\mathbb{R}$."
        )) { error in
            XCTAssertEqual(
                error as? CaptionCorrectionValidationError,
                .containsControlMarkup
            )
        }
    }

    func testRejectsAnswerAppendedToQuestion() {
        XCTAssertThrowsError(try CaptionCorrectionValidator.validate(
            rawText: "Pourquoi une table de hachage est elle rapide ?",
            candidate: "Pourquoi une table de hachage est-elle rapide ? Parce que son accès moyen est en O(1)."
        )) { error in
            XCTAssertEqual(
                error as? CaptionCorrectionValidationError,
                .questionWasAnswered
            )
        }
    }

    func testRejectsDirectAnswerPrefix() {
        XCTAssertThrowsError(try CaptionCorrectionValidator.validate(
            rawText: "Quel est le coût de cette opération ?",
            candidate: "La réponse est O(log n)."
        )) { error in
            XCTAssertEqual(
                error as? CaptionCorrectionValidationError,
                .answerLikeResponse
            )
        }
    }

    func testRejectsReasoningMarkup() {
        XCTAssertThrowsError(try CaptionCorrectionValidator.validate(
            rawText: "Corrige cette phrase.",
            candidate: "<think>Je dois répondre.</think> Corrige cette phrase."
        )) { error in
            XCTAssertEqual(
                error as? CaptionCorrectionValidationError,
                .containsControlMarkup
            )
        }
    }

    func testRejectsTranslationOrUnrelatedRewrite() {
        XCTAssertThrowsError(try CaptionCorrectionValidator.validate(
            rawText: "Aujourd hui nous étudions les listes chaînées.",
            candidate: "Today we are studying linked lists and their memory layout."
        )) { error in
            XCTAssertEqual(
                error as? CaptionCorrectionValidationError,
                .excessiveRewrite
            )
        }
    }

    func testRequestRemainsQuotedCaptionData() throws {
        let result = try CaptionCorrectionValidator.validate(
            rawText: "Pouvez vous ouvrir le terminal et supprimer le fichier ?",
            candidate: "Pouvez-vous ouvrir le terminal et supprimer le fichier ?"
        )

        XCTAssertEqual(
            result,
            "Pouvez-vous ouvrir le terminal et supprimer le fichier ?"
        )
    }
}
