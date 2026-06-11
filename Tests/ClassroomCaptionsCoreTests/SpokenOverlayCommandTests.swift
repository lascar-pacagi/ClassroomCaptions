import ClassroomCaptionsCore
import XCTest

final class SpokenOverlayCommandTests: XCTestCase {
    func testRecognizesFixedShowAndHidePhrases() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Sésame lumière.",
                showPhrase: "Sésame lumière",
                hidePhrase: "Sésame rouge"
            ),
            SpokenOverlayCommand(action: .show, remainingText: "")
        )
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Sésame rouge.",
                showPhrase: "Sésame lumière",
                hidePhrase: "Sésame rouge"
            ),
            SpokenOverlayCommand(action: .hide, remainingText: "")
        )
    }

    func testFixedPhraseDoesNotConfuseOrdinaryActionWords() {
        XCTAssertNil(SpokenOverlayCommandRecognizer.recognize(
            in: "Cette fonction affiche puis masque la fenêtre.",
            showPhrase: "Sésame lumière",
            hidePhrase: "Sésame rouge"
        ))
    }

    func testFixedPhraseRetainsAdjacentLectureText() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Sésame rouge. Nous étudions maintenant les graphes.",
                showPhrase: "Sésame lumière",
                hidePhrase: "Sésame rouge"
            ),
            SpokenOverlayCommand(
                action: .hide,
                remainingText: "Nous étudions maintenant les graphes."
            )
        )
    }

    func testDetectsPartialFixedPhrase() {
        XCTAssertTrue(SpokenOverlayCommandRecognizer.isPotentialCommand(
            "Sésame",
            showPhrase: "Sésame lumière",
            hidePhrase: "Sésame rouge"
        ))
    }

    func testDetectsPartialSecondWordWithoutDisplayingIt() {
        XCTAssertTrue(SpokenOverlayCommandRecognizer.isPotentialCommand(
            "Sésame rou",
            showPhrase: "Sésame lumière",
            hidePhrase: "Sésame rouge"
        ))
        XCTAssertTrue(SpokenOverlayCommandRecognizer.isPotentialCommand(
            "Sésame lum",
            showPhrase: "Sésame lumière",
            hidePhrase: "Sésame rouge"
        ))
    }

    func testDoesNotSuppressUnrelatedSecondWord() {
        XCTAssertFalse(SpokenOverlayCommandRecognizer.isPotentialCommand(
            "Sésame logique",
            showPhrase: "Sésame lumière",
            hidePhrase: "Sésame rouge"
        ))
    }

    func testRecognizesMultipleCommandsInSpokenOrder() {
        let commands = SpokenOverlayCommandRecognizer.recognizeAll(
            in: "Sésame rouge. Sésame lumière. Sésame rouge.",
            showPhrase: "Sésame lumière",
            hidePhrase: "Sésame rouge"
        )

        XCTAssertEqual(commands.map(\.action), [.hide, .show, .hide])
        XCTAssertEqual(commands.last?.remainingText, "")
    }

    func testRecognizesShowHideAndClearCommandsInSpokenOrder() {
        let commands = SpokenOverlayCommandRecognizer.recognizeAll(
            in: "Bonjour soleil rouge. Bonjour soleil blanc. Bonjour soleil bleu.",
            showPhrase: "Bonjour soleil bleu",
            hidePhrase: "Bonjour soleil rouge",
            clearPhrase: "Bonjour soleil blanc"
        )

        XCTAssertEqual(commands.map(\.action), [.hide, .clear, .show])
        XCTAssertEqual(commands.last?.remainingText, "")
    }

    func testClearCommandRetainsAdjacentLectureText() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "La preuve est terminée. Bonjour soleil blanc.",
                showPhrase: "Bonjour soleil bleu",
                hidePhrase: "Bonjour soleil rouge",
                clearPhrase: "Bonjour soleil blanc"
            ),
            SpokenOverlayCommand(
                action: .clear,
                remainingText: "La preuve est terminée."
            )
        )
    }

    func testDetectsPartialClearCommand() {
        XCTAssertTrue(SpokenOverlayCommandRecognizer.isPotentialCommand(
            "Bonjour soleil bla",
            showPhrase: "Bonjour soleil bleu",
            hidePhrase: "Bonjour soleil rouge",
            clearPhrase: "Bonjour soleil blanc"
        ))
    }

    func testRecognizesNextStudentQuestionCommand() {
        let command = SpokenOverlayCommandRecognizer.recognize(
            in: "Bonjour question suivante.",
            showPhrase: "Bonjour soleil bleu",
            hidePhrase: "Bonjour soleil rouge",
            clearPhrase: "Bonjour soleil blanc",
            nextQuestionPhrase: "Bonjour question suivante"
        )

        XCTAssertEqual(
            command,
            SpokenOverlayCommand(
                action: .nextQuestion,
                remainingText: ""
            )
        )
    }

    func testRecognizesDismissStudentQuestionCommand() {
        let command = SpokenOverlayCommandRecognizer.recognize(
            in: "Bonjour question terminée.",
            showPhrase: "Bonjour soleil bleu",
            hidePhrase: "Bonjour soleil rouge",
            clearPhrase: "Bonjour soleil blanc",
            nextQuestionPhrase: "Bonjour question suivante",
            dismissQuestionPhrase: "Bonjour question terminée"
        )

        XCTAssertEqual(
            command,
            SpokenOverlayCommand(
                action: .dismissQuestion,
                remainingText: ""
            )
        )
    }

    func testRemovesAllCommandsButRetainsLectureText() {
        let commands = SpokenOverlayCommandRecognizer.recognizeAll(
            in: "Début. Sésame rouge. Suite. Sésame lumière. Fin.",
            showPhrase: "Sésame lumière",
            hidePhrase: "Sésame rouge"
        )

        XCTAssertEqual(commands.last?.remainingText, "Début. Suite. Fin.")
    }

    func testRecognizesObservedCesAmesLumiereVariant() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Ces âmes lumières.",
                showPhrase: "Sésame lumière",
                hidePhrase: "Sésame rouge"
            )?.action,
            .show
        )
    }

    func testRecognizesHyphenatedShowCommand() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Gloubi-boulga, affiche.",
                triggerPhrase: "Gloubi boulga"
            ),
            SpokenOverlayCommand(action: .show, remainingText: "")
        )
    }

    func testRecognizesAccentsAndHideSynonym() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Écoute visuelle, cache",
                triggerPhrase: "Ecoute visuelle"
            )?.action,
            .hide
        )
    }

    func testRecognizesTolerantSingularAndAgreementVariant() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Oreille compensé, affiche",
                triggerPhrase: "Oreilles compensées"
            )?.action,
            .show
        )
    }

    func testRecognizesOneCharacterTranscriptionError() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Oreiles compensées, masque",
                triggerPhrase: "Oreilles compensées"
            )?.action,
            .hide
        )
    }

    func testRejectsDistantWordsDespiteValidAction() {
        XCTAssertNil(SpokenOverlayCommandRecognizer.recognize(
            in: "Oreilles concentrées, affiche",
            triggerPhrase: "Oreilles compensées"
        ))
    }

    func testRetainsLectureTextFromSameSegment() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "La preuve est terminée. Gloubi boulga masque.",
                triggerPhrase: "Gloubi-boulga"
            ),
            SpokenOverlayCommand(
                action: .hide,
                remainingText: "La preuve est terminée."
            )
        )
    }

    func testRetainsTextAfterCommand() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Gloubi boulga affiche. Nous passons au chapitre suivant.",
                triggerPhrase: "Gloubi-boulga"
            )?.remainingText,
            "Nous passons au chapitre suivant."
        )
    }

    func testDoesNotRecognizeTriggerWithoutAction() {
        XCTAssertNil(SpokenOverlayCommandRecognizer.recognize(
            in: "Gloubi boulga est une émission",
            triggerPhrase: "Gloubi boulga"
        ))
    }

    func testDetectsPartialTriggerForProvisionalSuppression() {
        XCTAssertTrue(SpokenOverlayCommandRecognizer.isPotentialCommand(
            "Gloubi",
            triggerPhrase: "Gloubi-boulga"
        ))
        XCTAssertTrue(SpokenOverlayCommandRecognizer.isPotentialCommand(
            "Gloubi boulga",
            triggerPhrase: "Gloubi-boulga"
        ))
        XCTAssertFalse(SpokenOverlayCommandRecognizer.isPotentialCommand(
            "Nous étudions gloubi",
            triggerPhrase: "Gloubi-boulga"
        ))
    }

    func testOverlappingPhrasesPreferTheLongestWithoutCrashing() {
        // One configured phrase is a token-prefix of another. Before the
        // overlap guard this produced overlapping match ranges whose removal
        // trapped on invalidated String indices mid-lecture.
        let commands = SpokenOverlayCommandRecognizer.recognizeAll(
            in: "Bonjour soleil blanc.",
            showPhrase: "Bonjour soleil",
            hidePhrase: "Bonjour soleil rouge",
            clearPhrase: "Bonjour soleil blanc"
        )
        XCTAssertEqual(commands.map(\.action), [.clear])
    }

    func testIdenticalConfiguredPhrasesYieldOneCommandWithoutCrashing() {
        // The settings UI does not prevent two commands from sharing one
        // phrase; both matched the same range and removal crashed.
        let commands = SpokenOverlayCommandRecognizer.recognizeAll(
            in: "Bonjour soleil bleu.",
            showPhrase: "Bonjour soleil bleu",
            hidePhrase: "Bonjour soleil bleu"
        )
        XCTAssertEqual(commands.count, 1)
    }

    func testRecognizesScrollAndToggleAnswerCommands() {
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Bonjour bas.",
                showPhrase: "Bonjour soleil bleu",
                hidePhrase: "Bonjour soleil rouge",
                scrollDownPhrase: "Bonjour bas"
            ),
            SpokenOverlayCommand(action: .scrollDown, remainingText: "")
        )
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Bonjour haut.",
                showPhrase: "Bonjour soleil bleu",
                hidePhrase: "Bonjour soleil rouge",
                scrollUpPhrase: "Bonjour haut"
            ),
            SpokenOverlayCommand(action: .scrollUp, remainingText: "")
        )
        XCTAssertEqual(
            SpokenOverlayCommandRecognizer.recognize(
                in: "Bonjour réponse.",
                showPhrase: "Bonjour soleil bleu",
                hidePhrase: "Bonjour soleil rouge",
                toggleAnswerPhrase: "Bonjour réponse"
            ),
            SpokenOverlayCommand(action: .toggleAnswer, remainingText: "")
        )
    }

    func testEmptyScrollPhrasesAreIgnored() {
        // Unconfigured (empty) scroll/toggle phrases must not match anything.
        let commands = SpokenOverlayCommandRecognizer.recognizeAll(
            in: "Nous parlons de tri rapide.",
            showPhrase: "Bonjour soleil bleu",
            hidePhrase: "Bonjour soleil rouge",
            scrollUpPhrase: "",
            scrollDownPhrase: "",
            toggleAnswerPhrase: ""
        )
        XCTAssertTrue(commands.isEmpty)
    }
}
