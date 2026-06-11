@testable import ClassroomCaptions
import Network
import XCTest

final class LocalCaptionServerTests: XCTestCase {
    // The server now serves HTTPS with a self-signed identity, so the test
    // client must accept that certificate. It only ever talks to the local
    // listener, so trusting the presented server certificate is safe here.
    private let session = URLSession(
        configuration: .ephemeral,
        delegate: InsecureTrustDelegate(),
        delegateQueue: nil
    )

    func testPairingTokenHasExpectedEntropyAndEncoding() throws {
        let first = try CaptionSharingSecurity.makeToken()
        let second = try CaptionSharingSecurity.makeToken()

        XCTAssertEqual(
            first.count,
            CaptionSharingSecurity.tokenByteCount * 2
        )
        XCTAssertNotEqual(first, second)
        XCTAssertTrue(first.allSatisfy(\.isHexDigit))
    }

    func testPairingTokenComparisonRequiresExactValue() throws {
        let token = try CaptionSharingSecurity.makeToken()
        let replacement = token.last == "0" ? "1" : "0"
        let modified = String(token.dropLast()) + replacement

        XCTAssertTrue(CaptionSharingSecurity.tokensMatch(token, token))
        XCTAssertFalse(CaptionSharingSecurity.tokensMatch(token + "0", token))
        XCTAssertFalse(CaptionSharingSecurity.tokensMatch(modified, token))
    }

    func testRemoteSnapshotEncodingContainsNoControlCapability() throws {
        let snapshot = RemoteCaptionSnapshot(
            finalized: ["∀n ∈ ℕ, n ≥ 0"],
            provisional: "Nouvelle phrase",
            sessionActive: true,
            revision: 42
        )

        let data = try JSONEncoder().encode(snapshot)
        let decoded = try JSONDecoder().decode(
            RemoteCaptionSnapshot.self,
            from: data
        )

        XCTAssertEqual(decoded, snapshot)
        let object = try XCTUnwrap(
            JSONSerialization.jsonObject(with: data) as? [String: Any]
        )
        XCTAssertEqual(
            Set(object.keys),
            ["finalized", "provisional", "sessionActive", "revision"]
        )
    }

    func testServerRequiresTheGeneratedPairingToken() async throws {
        let updates = AsyncStream.makeStream(
            of: LocalCaptionServerStatus.self
        )
        let server = LocalCaptionServer(
            statusHandler: { status in
                updates.continuation.yield(status)
            },
            port: try XCTUnwrap(NWEndpoint.Port(rawValue: 18_765))
        )
        defer {
            server.stop()
            updates.continuation.finish()
        }

        server.start()
        guard let pairingURL = await readyURL(
            from: updates.stream,
            timeout: .seconds(4)
        ) else {
            throw XCTSkip("No active Wi-Fi listener is available.")
        }

        var invalidComponents = try XCTUnwrap(
            URLComponents(url: pairingURL, resolvingAgainstBaseURL: false)
        )
        invalidComponents.queryItems = [
            URLQueryItem(name: "token", value: "invalid"),
        ]
        let invalidURL = try XCTUnwrap(invalidComponents.url)
        let (_, invalidResponse) = try await session.data(
            from: invalidURL
        )
        XCTAssertEqual((invalidResponse as? HTTPURLResponse)?.statusCode, 404)

        let (page, validResponse) = try await session.data(
            from: pairingURL
        )
        XCTAssertEqual((validResponse as? HTTPURLResponse)?.statusCode, 200)
        XCTAssertTrue(
            String(decoding: page, as: UTF8.self)
                .contains("Classroom Captions")
        )
    }

    func testStudentQuestionSubmissionRequiresTicketAndIsRateLimited() async throws {
        let captionUpdates = AsyncStream.makeStream(
            of: LocalCaptionServerStatus.self
        )
        let questionUpdates = AsyncStream.makeStream(
            of: StudentQuestionServerStatus.self
        )
        let submissions = AsyncStream.makeStream(
            of: SubmittedClassroomQuestion.self
        )
        let server = LocalCaptionServer(
            statusHandler: { captionUpdates.continuation.yield($0) },
            questionStatusHandler: { questionUpdates.continuation.yield($0) },
            questionHandler: { submissions.continuation.yield($0) },
            port: try XCTUnwrap(NWEndpoint.Port(rawValue: 18_766))
        )
        defer {
            server.stop()
            captionUpdates.continuation.finish()
            questionUpdates.continuation.finish()
            submissions.continuation.finish()
        }

        server.start()
        guard await readyURL(
            from: captionUpdates.stream,
            timeout: .seconds(4)
        ) != nil else {
            throw XCTSkip("No active Wi-Fi listener is available.")
        }
        server.setQuestionSubmissionsEnabled(true)
        guard let studentURL = await studentURL(
            from: questionUpdates.stream,
            timeout: .seconds(4)
        ) else {
            return XCTFail("Student question URL was not published.")
        }

        let (page, pageResponse) = try await session.data(
            from: studentURL
        )
        XCTAssertEqual((pageResponse as? HTTPURLResponse)?.statusCode, 200)
        XCTAssertTrue(
            String(decoding: page, as: UTF8.self)
                .contains("Ask an anonymous question")
        )

        let ticketURL = try XCTUnwrap(URL(
            string: "/student-ticket?\(try XCTUnwrap(studentURL.query))",
            relativeTo: studentURL
        ))
        let (ticketData, ticketResponse) = try await post(
            ticketURL,
            body: Data()
        )
        XCTAssertEqual((ticketResponse as? HTTPURLResponse)?.statusCode, 200)
        let ticketPayload = try XCTUnwrap(
            JSONSerialization.jsonObject(with: ticketData) as? [String: Any]
        )
        let ticket = try XCTUnwrap(ticketPayload["ticket"] as? String)

        let questionURL = try XCTUnwrap(URL(
            string: "/questions?ticket=\(ticket)",
            relativeTo: studentURL
        ))
        let questionBody = try JSONSerialization.data(withJSONObject: [
            "text": "   Pourquoi la complexité est O(n log n) ?   ",
        ])
        let (_, acceptedResponse) = try await post(
            questionURL,
            body: questionBody
        )
        XCTAssertEqual(
            (acceptedResponse as? HTTPURLResponse)?.statusCode,
            202
        )
        guard let submitted = await nextSubmission(
            from: submissions.stream,
            timeout: .seconds(2)
        ) else {
            return XCTFail("Question was not delivered to the Mac callback.")
        }
        XCTAssertEqual(
            submitted.text,
            "Pourquoi la complexité est O(n log n) ?"
        )

        let (_, limitedResponse) = try await post(
            questionURL,
            body: questionBody
        )
        XCTAssertEqual(
            (limitedResponse as? HTTPURLResponse)?.statusCode,
            429
        )

        let invalidURL = try XCTUnwrap(URL(
            string: "/questions?ticket=invalid",
            relativeTo: studentURL
        ))
        let (_, invalidResponse) = try await post(
            invalidURL,
            body: questionBody
        )
        XCTAssertEqual(
            (invalidResponse as? HTTPURLResponse)?.statusCode,
            401
        )
    }

    func testSpokenQuestionRouteValidatesContentTypeAndTicket() async throws {
        let captionUpdates = AsyncStream.makeStream(
            of: LocalCaptionServerStatus.self
        )
        let questionUpdates = AsyncStream.makeStream(
            of: StudentQuestionServerStatus.self
        )
        let server = LocalCaptionServer(
            statusHandler: { captionUpdates.continuation.yield($0) },
            questionStatusHandler: { questionUpdates.continuation.yield($0) },
            port: try XCTUnwrap(NWEndpoint.Port(rawValue: 18_767))
        )
        defer {
            server.stop()
            captionUpdates.continuation.finish()
            questionUpdates.continuation.finish()
        }

        server.start()
        guard await readyURL(
            from: captionUpdates.stream,
            timeout: .seconds(4)
        ) != nil else {
            throw XCTSkip("No active Wi-Fi listener is available.")
        }
        server.setQuestionSubmissionsEnabled(true)
        guard let studentURL = await studentURL(
            from: questionUpdates.stream,
            timeout: .seconds(4)
        ) else {
            return XCTFail("Student question URL was not published.")
        }

        let ticketURL = try XCTUnwrap(URL(
            string: "/student-ticket?\(try XCTUnwrap(studentURL.query))",
            relativeTo: studentURL
        ))
        let (ticketData, _) = try await post(ticketURL, body: Data())
        let ticketPayload = try XCTUnwrap(
            JSONSerialization.jsonObject(with: ticketData) as? [String: Any]
        )
        let ticket = try XCTUnwrap(ticketPayload["ticket"] as? String)

        let audio = Data(count: 8_000) // 0.25 s of 16 kHz mono Int16 silence

        // Wrong content type is rejected before any audio is accepted.
        let jsonURL = try XCTUnwrap(URL(
            string: "/speak?ticket=\(ticket)", relativeTo: studentURL
        ))
        var jsonRequest = URLRequest(url: jsonURL)
        jsonRequest.httpMethod = "POST"
        jsonRequest.setValue(
            "application/json", forHTTPHeaderField: "Content-Type"
        )
        jsonRequest.httpBody = audio
        let (_, wrongType) = try await session.data(for: jsonRequest)
        XCTAssertEqual((wrongType as? HTTPURLResponse)?.statusCode, 415)

        // A valid octet-stream clip with a live ticket is accepted.
        var audioRequest = URLRequest(url: jsonURL)
        audioRequest.httpMethod = "POST"
        audioRequest.setValue(
            "application/octet-stream", forHTTPHeaderField: "Content-Type"
        )
        audioRequest.httpBody = audio
        let (_, accepted) = try await session.data(for: audioRequest)
        XCTAssertEqual((accepted as? HTTPURLResponse)?.statusCode, 202)

        // An unknown ticket is rejected.
        let badURL = try XCTUnwrap(URL(
            string: "/speak?ticket=invalid", relativeTo: studentURL
        ))
        var badRequest = URLRequest(url: badURL)
        badRequest.httpMethod = "POST"
        badRequest.setValue(
            "application/octet-stream", forHTTPHeaderField: "Content-Type"
        )
        badRequest.httpBody = audio
        let (_, badTicket) = try await session.data(for: badRequest)
        XCTAssertEqual((badTicket as? HTTPURLResponse)?.statusCode, 401)
    }

    func testTicketIssuanceIsCappedPerSource() async throws {
        let captionUpdates = AsyncStream.makeStream(
            of: LocalCaptionServerStatus.self
        )
        let questionUpdates = AsyncStream.makeStream(
            of: StudentQuestionServerStatus.self
        )
        let server = LocalCaptionServer(
            statusHandler: { captionUpdates.continuation.yield($0) },
            questionStatusHandler: { questionUpdates.continuation.yield($0) },
            port: try XCTUnwrap(NWEndpoint.Port(rawValue: 18_767))
        )
        defer {
            server.stop()
            captionUpdates.continuation.finish()
            questionUpdates.continuation.finish()
        }

        server.start()
        guard await readyURL(
            from: captionUpdates.stream,
            timeout: .seconds(4)
        ) != nil else {
            throw XCTSkip("No active Wi-Fi listener is available.")
        }
        server.setQuestionSubmissionsEnabled(true)
        guard let studentURL = await studentURL(
            from: questionUpdates.stream,
            timeout: .seconds(4)
        ) else {
            return XCTFail("Student question URL was not published.")
        }

        let ticketURL = try XCTUnwrap(URL(
            string: "/student-ticket?\(try XCTUnwrap(studentURL.query))",
            relativeTo: studentURL
        ))
        for _ in 0..<CaptionSharingSecurity.maximumTicketsPerSource {
            let (_, response) = try await post(ticketURL, body: Data())
            XCTAssertEqual((response as? HTTPURLResponse)?.statusCode, 200)
        }
        // One device looping the ticket route must not exhaust the global
        // table: the next request from the same source is refused.
        let (_, cappedResponse) = try await post(ticketURL, body: Data())
        XCTAssertEqual(
            (cappedResponse as? HTTPURLResponse)?.statusCode,
            429
        )
    }

    private func readyURL(
        from stream: AsyncStream<LocalCaptionServerStatus>,
        timeout: Duration
    ) async -> URL? {
        await withTaskGroup(of: URL?.self) { group in
            group.addTask {
                for await status in stream {
                    switch status {
                    case .ready(let url):
                        return url
                    case .failed:
                        return nil
                    default:
                        continue
                    }
                }
                return nil
            }
            group.addTask {
                try? await Task.sleep(for: timeout)
                return nil
            }
            let result = await group.next() ?? nil
            group.cancelAll()
            return result
        }
    }

    private func studentURL(
        from stream: AsyncStream<StudentQuestionServerStatus>,
        timeout: Duration
    ) async -> URL? {
        await withTaskGroup(of: URL?.self) { group in
            group.addTask {
                for await status in stream {
                    switch status {
                    case .ready(let url):
                        return url
                    case .failed:
                        return nil
                    case .stopped:
                        continue
                    }
                }
                return nil
            }
            group.addTask {
                try? await Task.sleep(for: timeout)
                return nil
            }
            let result = await group.next() ?? nil
            group.cancelAll()
            return result
        }
    }

    private func nextSubmission(
        from stream: AsyncStream<SubmittedClassroomQuestion>,
        timeout: Duration
    ) async -> SubmittedClassroomQuestion? {
        await withTaskGroup(of: SubmittedClassroomQuestion?.self) { group in
            group.addTask {
                for await submission in stream {
                    return submission
                }
                return nil
            }
            group.addTask {
                try? await Task.sleep(for: timeout)
                return nil
            }
            let result = await group.next() ?? nil
            group.cancelAll()
            return result
        }
    }

    private func post(
        _ url: URL,
        body: Data
    ) async throws -> (Data, URLResponse) {
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = body
        return try await session.data(for: request)
    }
}

/// Accepts the local server's self-signed certificate during tests. It only
/// ever runs against the loopback test listener, never a real network peer.
private final class InsecureTrustDelegate: NSObject, URLSessionDelegate {
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (
            URLSession.AuthChallengeDisposition, URLCredential?
        ) -> Void
    ) {
        if challenge.protectionSpace.authenticationMethod
            == NSURLAuthenticationMethodServerTrust,
            let trust = challenge.protectionSpace.serverTrust {
            completionHandler(.useCredential, URLCredential(trust: trust))
        } else {
            completionHandler(.performDefaultHandling, nil)
        }
    }
}
