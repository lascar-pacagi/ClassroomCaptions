import ClassroomCaptionsCore
import XCTest

final class ModelQuestionScanTests: XCTestCase {
    private let start = "Bonjour modèle début"
    private let end = "Bonjour modèle fin"

    private func scan(_ text: String) -> ModelQuestionScan {
        SpokenOverlayCommandRecognizer.scanModelQuestion(
            in: text,
            startPhrase: start,
            endPhrase: end
        )
    }

    func testCompleteQuestionInOneSegment() {
        let result = scan(
            "Bonjour modèle début quelle est la complexité du tri rapide Bonjour modèle fin"
        )
        XCTAssertEqual(result.kind, .complete)
        XCTAssertEqual(result.question, "quelle est la complexité du tri rapide")
        XCTAssertEqual(result.before, "")
        XCTAssertEqual(result.after, "")
    }

    func testSurroundingTextStaysCaption() {
        let result = scan(
            "Donc Bonjour modèle début deux plus deux Bonjour modèle fin et voilà"
        )
        XCTAssertEqual(result.kind, .complete)
        XCTAssertEqual(result.before, "Donc")
        XCTAssertEqual(result.question, "deux plus deux")
        XCTAssertEqual(result.after, "et voilà")
    }

    func testOpensWithoutClosing() {
        let result = scan("Bonjour modèle début quelle est la limite")
        XCTAssertEqual(result.kind, .opens)
        XCTAssertEqual(result.question, "quelle est la limite")
        XCTAssertEqual(result.before, "")
    }

    func testClosesAnOpenCapture() {
        let result = scan("de cette suite Bonjour modèle fin merci")
        XCTAssertEqual(result.kind, .closes)
        XCTAssertEqual(result.question, "de cette suite")
        XCTAssertEqual(result.after, "merci")
    }

    func testPlainTextIsNotAQuestion() {
        let result = scan("Nous étudions maintenant les arbres binaires")
        XCTAssertEqual(result.kind, .none)
        XCTAssertEqual(result.before, "Nous étudions maintenant les arbres binaires")
        XCTAssertEqual(result.question, "")
    }

    func testToleratesMissingAccentsAndCase() {
        let result = scan(
            "bonjour modele debut intègre x de zéro à un bonjour modele fin"
        )
        XCTAssertEqual(result.kind, .complete)
        XCTAssertEqual(result.question, "intègre x de zéro à un")
    }

    func testEndBeforeStartDoesNotClose() {
        // An end phrase that precedes the start phrase must not pair with it.
        let result = scan(
            "Bonjour modèle fin perdu Bonjour modèle début ma vraie question"
        )
        XCTAssertEqual(result.kind, .opens)
        XCTAssertEqual(result.question, "ma vraie question")
    }

    func testEmptyPhrasesYieldNone() {
        let result = SpokenOverlayCommandRecognizer.scanModelQuestion(
            in: "Bonjour modèle début x Bonjour modèle fin",
            startPhrase: "",
            endPhrase: ""
        )
        XCTAssertEqual(result.kind, .none)
    }
}
