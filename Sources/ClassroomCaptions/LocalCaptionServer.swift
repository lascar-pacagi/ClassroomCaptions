import Darwin
import Foundation
import Network
import Security

struct RemoteCaptionSnapshot: Codable, Equatable, Sendable {
    let finalized: [String]
    let provisional: String?
    let sessionActive: Bool
    let revision: UInt64
}

struct SubmittedClassroomQuestion: Equatable, Sendable {
    let id: UUID
    let text: String
    let submittedAt: Date
}

enum LocalCaptionServerStatus: Equatable, Sendable {
    case stopped
    case starting
    case ready(url: URL)
    case clientConnected(url: URL)
    case failed(String)
}

enum StudentQuestionServerStatus: Equatable, Sendable {
    case stopped
    case ready(url: URL)
    case failed(String)
}

enum CaptionSharingSecurity {
    static let tokenByteCount = 32
    static let maximumRequestBytes = 8 * 1_024
    static let maximumQuestionBytes = 2 * 1_024
    // A spoken-question clip is 16 kHz mono Int16 (~32 KB/s); allow ~35 s of
    // audio plus header slack. This much larger budget is granted only when the
    // request line is POST /speak, so text requests stay tightly bounded.
    static let maximumSpokenAudioBytes = 32_000 * 35
    static let maximumSpokenRequestBytes = 32_000 * 35 + 4_096
    static let maximumQuestionCharacters = 500
    static let maximumTickets = 256
    static let maximumTicketsPerSource = 4
    static let ticketLifetime: TimeInterval = 4 * 60 * 60
    static let minimumQuestionInterval: TimeInterval = 10
    static let perSourceWindow: TimeInterval = 5 * 60
    static let perSourceQuestionLimit = 8
    static let globalWindow: TimeInterval = 60
    static let globalQuestionLimit = 30
    static let acceptedQuestionWindow: TimeInterval = 60 * 60
    static let acceptedQuestionLimit = 100
    static let requestTimeout: TimeInterval = 10

    static func makeToken() throws -> String {
        var bytes = [UInt8](repeating: 0, count: tokenByteCount)
        guard SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes)
                == errSecSuccess else {
            throw CocoaError(.fileWriteUnknown)
        }
        return bytes.map { String(format: "%02x", $0) }.joined()
    }

    static func tokensMatch(_ candidate: String, _ expected: String) -> Bool {
        let left = Array(candidate.utf8)
        let right = Array(expected.utf8)
        guard left.count == right.count else { return false }
        var difference: UInt8 = 0
        for index in left.indices {
            difference |= left[index] ^ right[index]
        }
        return difference == 0
    }

    static func normalizedQuestion(_ text: String) -> String? {
        let collapsed = text
            .components(separatedBy: .whitespacesAndNewlines)
            .filter { !$0.isEmpty }
            .joined(separator: " ")
        guard !collapsed.isEmpty,
              collapsed.count <= maximumQuestionCharacters,
              !collapsed.unicodeScalars.contains(where: {
                  CharacterSet.controlCharacters.contains($0)
              }) else {
            return nil
        }
        return collapsed
    }
}

final class LocalCaptionServer: @unchecked Sendable {
    private static let defaultPort: NWEndpoint.Port = 8_765
    private static let serviceType = "_classcaptions._tcp"

    private let queue = DispatchQueue(
        label: "ClassroomCaptions.local-caption-server",
        qos: .userInitiated
    )
    private let statusHandler: @Sendable (LocalCaptionServerStatus) -> Void
    private let questionStatusHandler:
        @Sendable (StudentQuestionServerStatus) -> Void
    private let questionHandler:
        @Sendable (SubmittedClassroomQuestion) -> Void
    // Raw 16 kHz mono little-endian Int16 PCM of a spoken question; the app
    // transcribes it locally and enqueues the text like a typed question.
    private let spokenQuestionHandler: @Sendable (Data) -> Void
    private let port: NWEndpoint.Port
    private var listener: NWListener?
    private var streamConnection: NWConnection?
    private var heartbeatTimer: DispatchSourceTimer?
    private var activeConnectionIDs: Set<ObjectIdentifier> = []
    private var connectionsAwaitingRequest: Set<ObjectIdentifier> = []
    private var token = ""
    private var studentToken = ""
    private var pairingURL: URL?
    private var studentURL: URL?
    private var lastSnapshot: RemoteCaptionSnapshot?
    private var questionsEnabled = false

    private struct StudentTicket {
        let sourceID: String
        let expiresAt: Date
        var submissionDates: [Date]
    }

    /// Reused across publishes; only touched on the server queue.
    private let snapshotEncoder = JSONEncoder()
    private var studentTickets: [String: StudentTicket] = [:]
    private var sourceSubmissionDates: [String: [Date]] = [:]
    private var globalSubmissionDates: [Date] = []
    private var acceptedQuestionDates: [Date] = []

    init(
        statusHandler: @escaping @Sendable (LocalCaptionServerStatus) -> Void,
        questionStatusHandler: @escaping @Sendable (
            StudentQuestionServerStatus
        ) -> Void = { _ in },
        questionHandler: @escaping @Sendable (
            SubmittedClassroomQuestion
        ) -> Void = { _ in },
        spokenQuestionHandler: @escaping @Sendable (Data) -> Void = { _ in },
        port: NWEndpoint.Port = defaultPort
    ) {
        self.statusHandler = statusHandler
        self.questionStatusHandler = questionStatusHandler
        self.questionHandler = questionHandler
        self.spokenQuestionHandler = spokenQuestionHandler
        self.port = port
    }

    func start() {
        queue.async { [weak self] in
            self?.startOnQueue()
        }
    }

    func stop() {
        queue.async { [weak self] in
            self?.stopOnQueue(reportStatus: true)
        }
    }

    func publish(_ snapshot: RemoteCaptionSnapshot) {
        queue.async { [weak self] in
            guard let self else { return }
            self.lastSnapshot = snapshot
            self.send(snapshot, to: self.streamConnection)
        }
    }

    func setQuestionSubmissionsEnabled(_ enabled: Bool) {
        queue.async { [weak self] in
            self?.setQuestionSubmissionsEnabledOnQueue(enabled)
        }
    }

    private func startOnQueue() {
        stopOnQueue(reportStatus: false)
        statusHandler(.starting)

        do {
            guard let host = Self.wifiIPv4Address() else {
                statusHandler(.failed(
                    "No active Wi-Fi IPv4 address was found. Connect the Mac to Wi-Fi or an iPhone hotspot."
                ))
                return
            }
            token = try CaptionSharingSecurity.makeToken()

            // HTTPS: a browser only grants a page microphone access over a
            // secure (TLS) context, so the listener presents a self-signed
            // identity. See ServerTLSIdentity for what self-signed means here.
            let identity = try ServerTLSIdentity.makeIdentity(ipv4: host)
            let tlsOptions = NWProtocolTLS.Options()
            sec_protocol_options_set_local_identity(
                tlsOptions.securityProtocolOptions, identity
            )
            let parameters = NWParameters(tls: tlsOptions)
            parameters.requiredInterfaceType = .wifi
            parameters.includePeerToPeer = true
            parameters.allowLocalEndpointReuse = true

            let listener = try NWListener(using: parameters, on: port)
            listener.service = NWListener.Service(
                name: "Classroom Captions",
                type: Self.serviceType
            )
            listener.newConnectionHandler = { [weak self] connection in
                self?.accept(connection)
            }
            listener.stateUpdateHandler = { [weak self] state in
                self?.handleListenerState(state)
            }
            self.listener = listener
            listener.start(queue: queue)
        } catch {
            statusHandler(.failed(error.localizedDescription))
        }
    }

    private func stopOnQueue(reportStatus: Bool) {
        heartbeatTimer?.cancel()
        heartbeatTimer = nil
        streamConnection?.cancel()
        streamConnection = nil
        activeConnectionIDs.removeAll()
        connectionsAwaitingRequest.removeAll()
        listener?.cancel()
        listener = nil
        pairingURL = nil
        studentURL = nil
        token = ""
        studentToken = ""
        questionsEnabled = false
        studentTickets.removeAll()
        sourceSubmissionDates.removeAll()
        globalSubmissionDates.removeAll()
        acceptedQuestionDates.removeAll()
        questionStatusHandler(.stopped)
        if reportStatus {
            statusHandler(.stopped)
        }
    }

    private func handleListenerState(_ state: NWListener.State) {
        switch state {
        case .ready:
            guard let host = Self.wifiIPv4Address(),
                  let url = URL(
                      string: "https://\(host):\(port)/?token=\(token)"
                  ) else {
                statusHandler(.failed(
                    "No active Wi-Fi IPv4 address was found. Connect the Mac to Wi-Fi or an iPhone hotspot."
                ))
                stopOnQueue(reportStatus: false)
                return
            }
            pairingURL = url
            statusHandler(.ready(url: url))
            updateStudentQuestionURL(host: host)
        case .failed(let error):
            statusHandler(.failed(error.localizedDescription))
            stopOnQueue(reportStatus: false)
        case .cancelled:
            break
        default:
            break
        }
    }

    private func accept(_ connection: NWConnection) {
        guard activeConnectionIDs.count < 64 else {
            connection.cancel()
            return
        }
        let identifier = ObjectIdentifier(connection)
        activeConnectionIDs.insert(identifier)
        connectionsAwaitingRequest.insert(identifier)
        let sourceID = Self.sourceID(for: connection.endpoint)
        connection.stateUpdateHandler = { [weak self, weak connection] state in
            guard let self, let connection else { return }
            if case .failed = state {
                self.activeConnectionIDs.remove(ObjectIdentifier(connection))
                self.connectionsAwaitingRequest.remove(ObjectIdentifier(connection))
                self.removeStreamConnection(connection)
            } else if case .cancelled = state {
                self.activeConnectionIDs.remove(ObjectIdentifier(connection))
                self.connectionsAwaitingRequest.remove(ObjectIdentifier(connection))
                self.removeStreamConnection(connection)
            }
        }
        connection.start(queue: queue)
        // Authentication happens only after a complete request is parsed, so a
        // connection that never completes one must not hold a slot: cancel it
        // if no full request has arrived within the timeout (slowloris guard).
        queue.asyncAfter(
            deadline: .now() + CaptionSharingSecurity.requestTimeout
        ) { [weak self, weak connection] in
            guard let self, let connection else { return }
            if self.connectionsAwaitingRequest.contains(ObjectIdentifier(connection)) {
                connection.cancel()
            }
        }
        receiveRequest(
            on: connection,
            sourceID: sourceID,
            accumulated: Data()
        )
    }

    private func receiveRequest(
        on connection: NWConnection,
        sourceID: String,
        accumulated: Data
    ) {
        connection.receive(
            minimumIncompleteLength: 1,
            maximumLength: 2_048
        ) { [weak self, weak connection] data, _, isComplete, error in
            guard let self, let connection else { return }
            if error != nil {
                connection.cancel()
                return
            }

            var request = accumulated
            if let data {
                request.append(data)
            }
            // /speak uploads binary audio and needs a much larger budget than a
            // text request; the budget is gated on the request line itself so an
            // ordinary request can never claim the audio allowance.
            let isSpeak = Self.isSpokenQuestionRequest(request)
            let requestBudget = isSpeak
                ? CaptionSharingSecurity.maximumSpokenRequestBytes
                : CaptionSharingSecurity.maximumRequestBytes
            guard request.count <= requestBudget else {
                self.respond(
                    status: "431 Request Header Fields Too Large",
                    body: "Request too large.",
                    contentType: "text/plain; charset=utf-8",
                    on: connection
                )
                return
            }

            if let headerRange = request.range(of: Data("\r\n\r\n".utf8)) {
                guard let headerText = String(
                    data: request[..<headerRange.lowerBound],
                    encoding: .utf8
                ) else {
                    self.respond(
                        status: "400 Bad Request",
                        body: "Invalid request.",
                        contentType: "text/plain; charset=utf-8",
                        on: connection
                    )
                    return
                }
                let contentLength = Self.contentLength(in: headerText)
                let bodyBudget = isSpeak
                    ? CaptionSharingSecurity.maximumSpokenAudioBytes
                    : CaptionSharingSecurity.maximumQuestionBytes
                guard contentLength <= bodyBudget else {
                    self.respond(
                        status: "413 Content Too Large",
                        body: "Question is too large.",
                        contentType: "text/plain; charset=utf-8",
                        on: connection
                    )
                    return
                }
                let expectedCount = headerRange.upperBound + contentLength
                if request.count >= expectedCount {
                    self.handleRequest(
                        Data(request.prefix(expectedCount)),
                        sourceID: sourceID,
                        on: connection
                    )
                } else if isComplete {
                    self.respond(
                        status: "400 Bad Request",
                        body: "Incomplete request.",
                        contentType: "text/plain; charset=utf-8",
                        on: connection
                    )
                } else {
                    self.receiveRequest(
                        on: connection,
                        sourceID: sourceID,
                        accumulated: request
                    )
                }
            } else if isComplete {
                self.respond(
                    status: "400 Bad Request",
                    body: "Incomplete request.",
                    contentType: "text/plain; charset=utf-8",
                    on: connection
                )
            } else {
                self.receiveRequest(
                    on: connection,
                    sourceID: sourceID,
                    accumulated: request
                )
            }
        }
    }

    /// Whether the request line (available before the headers finish) is a
    /// spoken-question upload, which is allowed a much larger size budget.
    private static func isSpokenQuestionRequest(_ request: Data) -> Bool {
        guard let lineEnd = request.range(of: Data("\r\n".utf8)),
              let line = String(
                  data: request[..<lineEnd.lowerBound], encoding: .utf8
              ) else {
            return false
        }
        return line.hasPrefix("POST /speak")
    }

    private func handleRequest(
        _ data: Data,
        sourceID: String,
        on connection: NWConnection
    ) {
        connectionsAwaitingRequest.remove(ObjectIdentifier(connection))
        guard let headerRange = data.range(of: Data("\r\n\r\n".utf8)),
              let headerText = String(
                  data: data[..<headerRange.lowerBound],
                  encoding: .utf8
              ),
              let firstLine = headerText.components(
                  separatedBy: "\r\n"
              ).first else {
            respond(
                status: "400 Bad Request",
                body: "Invalid request.",
                contentType: "text/plain; charset=utf-8",
                on: connection
            )
            return
        }

        let parts = firstLine.split(separator: " ", maxSplits: 2)
        guard parts.count == 3,
              let components = URLComponents(string: String(parts[1])) else {
            respond(
                status: "400 Bad Request",
                body: "Invalid request.",
                contentType: "text/plain; charset=utf-8",
                on: connection
            )
            return
        }
        let method = String(parts[0])
        let headers = Self.headers(in: headerText)
        let body = Data(data[headerRange.upperBound...])

        if handleStudentRequest(
            method: method,
            components: components,
            headers: headers,
            body: body,
            sourceID: sourceID,
            on: connection
        ) {
            return
        }

        guard method == "GET",
              let candidate = Self.queryValue("token", in: components),
              CaptionSharingSecurity.tokensMatch(candidate, token) else {
            respond(
                status: "404 Not Found",
                body: "Not found.",
                contentType: "text/plain; charset=utf-8",
                on: connection
            )
            return
        }

        switch components.path {
        case "", "/":
            respond(
                status: "200 OK",
                body: Self.browserPage(token: token),
                contentType: "text/html; charset=utf-8",
                on: connection
            )
        case "/events":
            beginEventStream(on: connection)
        default:
            respond(
                status: "404 Not Found",
                body: "Not found.",
                contentType: "text/plain; charset=utf-8",
                on: connection
            )
        }
    }

    private func setQuestionSubmissionsEnabledOnQueue(_ enabled: Bool) {
        guard listener != nil, let pairingURL else {
            questionsEnabled = false
            questionStatusHandler(.failed(
                "Start iPhone sharing before enabling student questions."
            ))
            return
        }

        questionsEnabled = enabled
        studentTickets.removeAll()
        sourceSubmissionDates.removeAll()
        globalSubmissionDates.removeAll()
        acceptedQuestionDates.removeAll()
        guard enabled else {
            studentToken = ""
            studentURL = nil
            questionStatusHandler(.stopped)
            return
        }

        do {
            studentToken = try CaptionSharingSecurity.makeToken()
            updateStudentQuestionURL(host: pairingURL.host)
        } catch {
            questionsEnabled = false
            questionStatusHandler(.failed(error.localizedDescription))
        }
    }

    private func updateStudentQuestionURL(host: String?) {
        guard questionsEnabled, !studentToken.isEmpty,
              let host,
              let url = URL(
                  string: "https://\(host):\(port)/student?token=\(studentToken)"
              ) else {
            return
        }
        studentURL = url
        questionStatusHandler(.ready(url: url))
    }

    private func handleStudentRequest(
        method: String,
        components: URLComponents,
        headers: [String: String],
        body: Data,
        sourceID: String,
        on connection: NWConnection
    ) -> Bool {
        guard components.path == "/student"
                || components.path == "/student-ticket"
                || components.path == "/questions"
                || components.path == "/speak" else {
            return false
        }
        guard questionsEnabled else {
            respond(
                status: "404 Not Found",
                body: "Not found.",
                contentType: "text/plain; charset=utf-8",
                on: connection
            )
            return true
        }

        switch (method, components.path) {
        case ("GET", "/student"):
            guard let candidate = Self.queryValue("token", in: components),
                  CaptionSharingSecurity.tokensMatch(candidate, studentToken) else {
                respondNotFound(on: connection)
                return true
            }
            respond(
                status: "200 OK",
                body: Self.studentQuestionPage(token: studentToken),
                contentType: "text/html; charset=utf-8",
                on: connection
            )

        case ("POST", "/student-ticket"):
            guard let candidate = Self.queryValue("token", in: components),
                  CaptionSharingSecurity.tokensMatch(candidate, studentToken) else {
                respondNotFound(on: connection)
                return true
            }
            issueStudentTicket(sourceID: sourceID, on: connection)

        case ("POST", "/questions"):
            guard headers["content-type"]?
                .lowercased()
                .hasPrefix("application/json") == true,
                  let ticket = Self.queryValue("ticket", in: components) else {
                respond(
                    status: "415 Unsupported Media Type",
                    body: #"{"error":"invalid_request"}"#,
                    contentType: "application/json; charset=utf-8",
                    on: connection
                )
                return true
            }
            submitQuestion(
                body: body,
                ticket: ticket,
                sourceID: sourceID,
                on: connection
            )

        case ("POST", "/speak"):
            guard headers["content-type"]?
                .lowercased()
                .hasPrefix("application/octet-stream") == true,
                  let ticket = Self.queryValue("ticket", in: components) else {
                respond(
                    status: "415 Unsupported Media Type",
                    body: #"{"error":"invalid_request"}"#,
                    contentType: "application/json; charset=utf-8",
                    on: connection
                )
                return true
            }
            submitSpokenQuestion(
                body: body,
                ticket: ticket,
                sourceID: sourceID,
                on: connection
            )

        default:
            respondNotFound(on: connection)
        }
        return true
    }

    private func issueStudentTicket(
        sourceID: String,
        on connection: NWConnection
    ) {
        let now = Date()
        studentTickets = studentTickets.filter { $0.value.expiresAt > now }
        guard studentTickets.count < CaptionSharingSecurity.maximumTickets else {
            respond(
                status: "503 Service Unavailable",
                body: #"{"error":"classroom_full"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
            return
        }
        // One device looping the ticket route must not exhaust the global
        // table for everyone else: cap live tickets per source as well.
        let ticketsFromSource = studentTickets.values.filter {
            $0.sourceID == sourceID
        }.count
        guard ticketsFromSource < CaptionSharingSecurity.maximumTicketsPerSource
        else {
            respond(
                status: "429 Too Many Requests",
                body: #"{"error":"ticket_limit"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
            return
        }

        do {
            let ticket = try CaptionSharingSecurity.makeToken()
            studentTickets[ticket] = StudentTicket(
                sourceID: sourceID,
                expiresAt: now.addingTimeInterval(
                    CaptionSharingSecurity.ticketLifetime
                ),
                submissionDates: []
            )
            let body = #"{"ticket":"\#(ticket)","maxCharacters":\#(CaptionSharingSecurity.maximumQuestionCharacters)}"#
            respond(
                status: "200 OK",
                body: body,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
        } catch {
            respond(
                status: "503 Service Unavailable",
                body: #"{"error":"ticket_unavailable"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
        }
    }

    private func submitQuestion(
        body: Data,
        ticket: String,
        sourceID: String,
        on connection: NWConnection
    ) {
        struct Payload: Decodable {
            let text: String
        }

        let now = Date()
        guard let studentTicket = studentTickets[ticket],
              studentTicket.expiresAt > now,
              studentTicket.sourceID == sourceID else {
            respond(
                status: "401 Unauthorized",
                body: #"{"error":"invalid_ticket"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
            return
        }
        guard let payload = try? JSONDecoder().decode(Payload.self, from: body),
              let text = CaptionSharingSecurity.normalizedQuestion(
                  payload.text
              ) else {
            respond(
                status: "422 Unprocessable Content",
                body: #"{"error":"invalid_question"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
            return
        }

        guard registerAcceptedSubmission(
            ticket: ticket, sourceID: sourceID, now: now
        ) else {
            respond(
                status: "429 Too Many Requests",
                body: #"{"error":"rate_limited"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
            return
        }

        questionHandler(SubmittedClassroomQuestion(
            id: UUID(),
            text: text,
            submittedAt: now
        ))
        respond(
            status: "202 Accepted",
            body: #"{"accepted":true}"#,
            contentType: "application/json; charset=utf-8",
            on: connection
        )
    }

    /// Applies the shared sliding-window rate limits and records one accepted
    /// submission (typed or spoken). Returns false — recording nothing — when
    /// any limit is hit, so the caller can answer 429.
    private func registerAcceptedSubmission(
        ticket: String,
        sourceID: String,
        now: Date
    ) -> Bool {
        guard var studentTicket = studentTickets[ticket] else { return false }
        studentTicket.submissionDates.removeAll {
            now.timeIntervalSince($0) > CaptionSharingSecurity.perSourceWindow
        }
        var sourceDates = sourceSubmissionDates[sourceID, default: []]
        sourceDates.removeAll {
            now.timeIntervalSince($0) > CaptionSharingSecurity.perSourceWindow
        }
        globalSubmissionDates.removeAll {
            now.timeIntervalSince($0) > CaptionSharingSecurity.globalWindow
        }
        // Sliding window, not a lifetime counter: a session-long cap would
        // permanently disable questions for an active class once reached.
        acceptedQuestionDates.removeAll {
            now.timeIntervalSince($0)
                > CaptionSharingSecurity.acceptedQuestionWindow
        }

        let submittedTooRecently = studentTicket.submissionDates.last.map {
            now.timeIntervalSince($0)
                < CaptionSharingSecurity.minimumQuestionInterval
        } ?? false
        guard !submittedTooRecently,
              sourceDates.count < CaptionSharingSecurity.perSourceQuestionLimit,
              globalSubmissionDates.count
                  < CaptionSharingSecurity.globalQuestionLimit,
              acceptedQuestionDates.count
                  < CaptionSharingSecurity.acceptedQuestionLimit else {
            return false
        }

        studentTicket.submissionDates.append(now)
        sourceDates.append(now)
        globalSubmissionDates.append(now)
        studentTickets[ticket] = studentTicket
        sourceSubmissionDates[sourceID] = sourceDates
        acceptedQuestionDates.append(now)
        return true
    }

    /// Accepts a spoken-question audio clip (raw 16 kHz mono Int16 PCM). Same
    /// ticket and rate limits as a typed question; the clip is bounded and
    /// forwarded to the app, which transcribes it and enqueues the text.
    private func submitSpokenQuestion(
        body: Data,
        ticket: String,
        sourceID: String,
        on connection: NWConnection
    ) {
        let now = Date()
        guard let studentTicket = studentTickets[ticket],
              studentTicket.expiresAt > now,
              studentTicket.sourceID == sourceID else {
            respond(
                status: "401 Unauthorized",
                body: #"{"error":"invalid_ticket"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
            return
        }
        // 16 kHz mono Int16 is ~32 KB per second. Require at least ~0.1 s and
        // cap the clip near 35 s so one POST cannot upload an endless recording.
        guard body.count >= 3_200, body.count <= 32_000 * 35 else {
            respond(
                status: "422 Unprocessable Content",
                body: #"{"error":"invalid_audio"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
            return
        }
        guard registerAcceptedSubmission(
            ticket: ticket, sourceID: sourceID, now: now
        ) else {
            respond(
                status: "429 Too Many Requests",
                body: #"{"error":"rate_limited"}"#,
                contentType: "application/json; charset=utf-8",
                on: connection
            )
            return
        }
        spokenQuestionHandler(body)
        respond(
            status: "202 Accepted",
            body: #"{"accepted":true}"#,
            contentType: "application/json; charset=utf-8",
            on: connection
        )
    }

    private func respondNotFound(on connection: NWConnection) {
        respond(
            status: "404 Not Found",
            body: "Not found.",
            contentType: "text/plain; charset=utf-8",
            on: connection
        )
    }

    private func beginEventStream(on connection: NWConnection) {
        // A newer authenticated viewer pre-empts the existing stream: the slot
        // would otherwise be unrecoverable if the old stream is stuck or was
        // opened by someone else with a captured link, locking the professor's
        // own phone out until sharing restarts.
        if let existing = streamConnection, existing !== connection {
            streamConnection = nil
            existing.cancel()
        }

        streamConnection = connection
        let headers = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/event-stream; charset=utf-8",
            "Cache-Control: no-store, no-cache, must-revalidate",
            "Connection: keep-alive",
            "X-Content-Type-Options: nosniff",
            "Referrer-Policy: no-referrer",
            "",
            "retry: 1000",
            "",
            "",
        ].joined(separator: "\r\n")
        connection.send(
            content: Data(headers.utf8),
            completion: .contentProcessed { [weak connection] error in
                if error != nil {
                    connection?.cancel()
                }
            }
        )

        if let lastSnapshot {
            send(lastSnapshot, to: connection)
        }
        startHeartbeat()
        if let pairingURL {
            statusHandler(.clientConnected(url: pairingURL))
        }
    }

    private func startHeartbeat() {
        heartbeatTimer?.cancel()
        let timer = DispatchSource.makeTimerSource(queue: queue)
        timer.schedule(deadline: .now() + 10, repeating: 10)
        timer.setEventHandler { [weak self] in
            guard let self, let connection = self.streamConnection else { return }
            connection.send(
                content: Data(": heartbeat\n\n".utf8),
                completion: .contentProcessed { [weak connection] error in
                    if error != nil {
                        connection?.cancel()
                    }
                }
            )
        }
        heartbeatTimer = timer
        timer.resume()
    }

    private func removeStreamConnection(_ connection: NWConnection) {
        guard streamConnection === connection else { return }
        streamConnection = nil
        heartbeatTimer?.cancel()
        heartbeatTimer = nil
        if let pairingURL {
            statusHandler(.ready(url: pairingURL))
        }
    }

    private func send(
        _ snapshot: RemoteCaptionSnapshot,
        to connection: NWConnection?
    ) {
        guard let connection,
              let json = try? snapshotEncoder.encode(snapshot),
              let payload = String(data: json, encoding: .utf8) else {
            return
        }
        let event = "event: captions\ndata: \(payload)\n\n"
        connection.send(
            content: Data(event.utf8),
            completion: .contentProcessed { [weak connection] error in
                if error != nil {
                    connection?.cancel()
                }
            }
        )
    }

    private func respond(
        status: String,
        body: String,
        contentType: String,
        on connection: NWConnection
    ) {
        let bodyData = Data(body.utf8)
        let headers = [
            "HTTP/1.1 \(status)",
            "Content-Type: \(contentType)",
            "Content-Length: \(bodyData.count)",
            "Cache-Control: no-store",
            "Connection: close",
            "Content-Security-Policy: default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
            "Referrer-Policy: no-referrer",
            "X-Content-Type-Options: nosniff",
            "X-Frame-Options: DENY",
            "",
            "",
        ].joined(separator: "\r\n")
        var response = Data(headers.utf8)
        response.append(bodyData)
        connection.send(
            content: response,
            contentContext: .finalMessage,
            isComplete: true,
            completion: .contentProcessed { [weak self, weak connection] _ in
                guard let self, let connection else { return }
                self.activeConnectionIDs.remove(ObjectIdentifier(connection))
                self.connectionsAwaitingRequest.remove(
                    ObjectIdentifier(connection)
                )
            }
        )
    }

    private static func contentLength(in headerText: String) -> Int {
        let value = headers(in: headerText)["content-length"] ?? "0"
        return max(0, Int(value) ?? 0)
    }

    private static func headers(in headerText: String) -> [String: String] {
        var result: [String: String] = [:]
        for line in headerText.components(separatedBy: "\r\n").dropFirst() {
            guard let separator = line.firstIndex(of: ":") else { continue }
            let name = line[..<separator]
                .trimmingCharacters(in: .whitespacesAndNewlines)
                .lowercased()
            let value = line[line.index(after: separator)...]
                .trimmingCharacters(in: .whitespacesAndNewlines)
            guard !name.isEmpty else { continue }
            result[name] = value
        }
        return result
    }

    private static func queryValue(
        _ name: String,
        in components: URLComponents
    ) -> String? {
        components.queryItems?
            .first(where: { $0.name == name })?
            .value
    }

    private static func sourceID(for endpoint: NWEndpoint) -> String {
        if case .hostPort(let host, _) = endpoint {
            return String(describing: host)
        }
        return String(describing: endpoint)
    }

    private static func wifiIPv4Address() -> String? {
        var interfaces: UnsafeMutablePointer<ifaddrs>?
        guard getifaddrs(&interfaces) == 0, let first = interfaces else {
            return nil
        }
        defer { freeifaddrs(interfaces) }

        var fallback: String?
        var cursor: UnsafeMutablePointer<ifaddrs>? = first
        while let interface = cursor {
            defer { cursor = interface.pointee.ifa_next }
            let flags = Int32(interface.pointee.ifa_flags)
            guard flags & IFF_UP != 0,
                  flags & IFF_LOOPBACK == 0,
                  let address = interface.pointee.ifa_addr,
                  address.pointee.sa_family == UInt8(AF_INET) else {
                continue
            }

            var host = [CChar](repeating: 0, count: Int(NI_MAXHOST))
            let length = socklen_t(address.pointee.sa_len)
            guard getnameinfo(
                address,
                length,
                &host,
                socklen_t(host.count),
                nil,
                0,
                NI_NUMERICHOST
            ) == 0 else {
                continue
            }
            let terminator = host.firstIndex(of: 0) ?? host.endIndex
            let value = String(
                decoding: host[..<terminator].map(UInt8.init),
                as: UTF8.self
            )
            let name = String(cString: interface.pointee.ifa_name)
            if name == "en0" {
                return value
            }
            fallback = fallback ?? value
        }
        return fallback
    }

    private static func studentQuestionPage(token: String) -> String {
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
          <meta name="color-scheme" content="dark">
          <title>Ask a Question</title>
          <style>
            :root { font-family: -apple-system, BlinkMacSystemFont, sans-serif; color-scheme: dark; }
            * { box-sizing: border-box; }
            body { margin: 0; min-height: 100dvh; background: #080808; color: white; }
            main { max-width: 700px; min-height: 100dvh; margin: 0 auto; padding: max(24px, env(safe-area-inset-top)) 20px max(28px, env(safe-area-inset-bottom)); }
            h1 { margin: 0 0 8px; font-size: 30px; }
            p { color: #aaa; line-height: 1.4; }
            textarea { width: 100%; min-height: 150px; margin-top: 18px; padding: 16px; resize: vertical; border: 1px solid #444; border-radius: 14px; background: #171717; color: white; font: inherit; font-size: 20px; line-height: 1.35; }
            .row { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-top: 12px; }
            button { min-height: 48px; padding: 0 20px; border: 0; border-radius: 12px; background: #3278f6; color: white; font: inherit; font-weight: 650; }
            button:disabled { opacity: .45; }
            #count, #message { color: #999; font-size: 14px; }
            #message[data-kind="success"] { color: #62d982; }
            #message[data-kind="error"] { color: #ff7777; }
            .privacy { margin-top: 28px; font-size: 13px; color: #777; }
            .voice { margin-top: 26px; padding-top: 22px; border-top: 1px solid #222; }
            .voice-label { color: #aaa; margin: 0 0 10px; }
            #talk { width: 100%; min-height: 64px; font-size: 20px; background: #2b6b3f; touch-action: none; user-select: none; -webkit-user-select: none; }
            #talk[data-state="recording"] { background: #d23b3b; }
            #voice-message { margin: 10px 0 0; color: #999; font-size: 14px; min-height: 18px; }
            #voice-message[data-kind="success"] { color: #62d982; }
            #voice-message[data-kind="error"] { color: #ff7777; }
          </style>
        </head>
        <body>
          <main>
            <h1>Ask an anonymous question</h1>
            <p>Your question will appear in the professor's moderation queue. It is not sent directly to an AI model.</p>
            <form id="form">
              <label for="question">Question</label>
              <textarea id="question" maxlength="500" required autocomplete="off" placeholder="Write your question here…"></textarea>
              <div class="row">
                <span id="count">0 / 500</span>
                <button id="submit" type="submit" disabled>Submit question</button>
              </div>
              <p id="message" role="status" aria-live="polite"></p>
            </form>
            <div class="voice">
              <p class="voice-label">Or ask out loud (held only while you press):</p>
              <button id="talk" type="button" disabled>Tap to enable microphone</button>
              <p id="voice-message" role="status" aria-live="polite"></p>
            </div>
            <p class="privacy">No name is requested. A temporary in-memory ticket is used only for abuse prevention and disappears when classroom sharing stops. Your voice is sent only to the professor's Mac and transcribed there; the audio is then discarded.</p>
          </main>
          <script>
            const sessionToken = "\(token)";
            const form = document.getElementById("form");
            const question = document.getElementById("question");
            const submit = document.getElementById("submit");
            const count = document.getElementById("count");
            const message = document.getElementById("message");
            const talk = document.getElementById("talk");
            const voiceMessage = document.getElementById("voice-message");
            let ticket = null;

            function showMessage(text, kind) {
              message.textContent = text;
              message.dataset.kind = kind;
            }

            async function obtainTicket() {
              const response = await fetch("/student-ticket?token=" + encodeURIComponent(sessionToken), {
                method: "POST",
                cache: "no-store",
                credentials: "omit"
              });
              if (!response.ok) throw new Error("ticket");
              const payload = await response.json();
              ticket = payload.ticket;
              submit.disabled = question.value.trim().length === 0;
              if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                talk.disabled = false;
              }
            }

            question.addEventListener("input", () => {
              count.textContent = question.value.length + " / 500";
              submit.disabled = !ticket || question.value.trim().length === 0;
            });

            form.addEventListener("submit", async event => {
              event.preventDefault();
              if (!ticket) return;
              submit.disabled = true;
              showMessage("Submitting…", "");
              try {
                const response = await fetch("/questions?ticket=" + encodeURIComponent(ticket), {
                  method: "POST",
                  cache: "no-store",
                  credentials: "omit",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ text: question.value })
                });
                if (response.status === 202) {
                  question.value = "";
                  count.textContent = "0 / 500";
                  showMessage("Question submitted.", "success");
                } else if (response.status === 429) {
                  showMessage("Please wait before submitting another question.", "error");
                } else {
                  showMessage("The question could not be submitted.", "error");
                }
              } catch {
                showMessage("Connection lost. Check the classroom Wi-Fi.", "error");
              }
              submit.disabled = !ticket || question.value.trim().length === 0;
            });

            const MAX_SPEAK_MS = 30000;
            let micEnabled = false, recording = false, audioCtx = null,
                srcNode = null, processor = null, micStream = null,
                captured = [], maxTimer = null;

            function voiceStatus(text, kind) {
              voiceMessage.textContent = text;
              voiceMessage.dataset.kind = kind || "";
            }

            // First step: a single TAP requests microphone permission. Doing it
            // here, not during a press-and-hold, keeps the permission pop-up from
            // interrupting the recording gesture. The stream is then kept open so
            // every later hold records instantly with no further prompt.
            async function enableMic() {
              if (micEnabled) return;
              if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                voiceStatus("Voice needs a secure (https) connection.", "error");
                return;
              }
              voiceStatus("Allow microphone access…", "");
              try {
                micStream = await navigator.mediaDevices.getUserMedia({
                  audio: { channelCount: 1, echoCancellation: true,
                           noiseSuppression: true, autoGainControl: true }
                });
              } catch {
                voiceStatus("Microphone access was declined.", "error");
                return;
              }
              audioCtx = new (window.AudioContext || window.webkitAudioContext)();
              srcNode = audioCtx.createMediaStreamSource(micStream);
              processor = audioCtx.createScriptProcessor(4096, 1, 1);
              processor.onaudioprocess = e => {
                if (recording) {
                  captured.push(new Float32Array(e.inputBuffer.getChannelData(0)));
                }
              };
              srcNode.connect(processor);
              processor.connect(audioCtx.destination);
              micEnabled = true;
              talk.textContent = "Hold to speak";
              voiceStatus("Microphone ready — press and hold to speak.", "success");
            }

            function startSpeaking() {
              if (!micEnabled || recording || !ticket) return;
              if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
              captured = [];
              recording = true;
              talk.dataset.state = "recording";
              talk.textContent = "Recording… release to send";
              voiceStatus("Listening…", "");
              maxTimer = setTimeout(() => stopSpeaking(true), MAX_SPEAK_MS);
            }

            async function stopSpeaking(send) {
              if (!recording) return;
              recording = false;
              if (maxTimer) { clearTimeout(maxTimer); maxTimer = null; }
              talk.dataset.state = "";
              talk.textContent = "Hold to speak";
              const sampleRate = audioCtx ? audioCtx.sampleRate : 48000;
              const chunks = captured;
              captured = [];
              if (!send) {
                voiceStatus("Microphone ready — press and hold to speak.", "");
                return;
              }
              const pcm = encodePCM16(chunks, sampleRate);
              if (pcm.byteLength < 3200) {
                voiceStatus("Too short — hold, then speak.", "error");
                return;
              }
              voiceStatus("Sending…", "");
              talk.disabled = true;
              try {
                const response = await fetch(
                  "/speak?ticket=" + encodeURIComponent(ticket),
                  { method: "POST", cache: "no-store", credentials: "omit",
                    headers: { "Content-Type": "application/octet-stream" },
                    body: pcm }
                );
                if (response.status === 202) {
                  voiceStatus("Spoken question sent.", "success");
                } else if (response.status === 429) {
                  voiceStatus("Please wait before speaking again.", "error");
                } else {
                  voiceStatus("The question could not be sent.", "error");
                }
              } catch {
                voiceStatus("Connection lost. Check the classroom Wi-Fi.", "error");
              }
              talk.disabled = false;
            }

            // Average no resampling library: merge the captured blocks, linearly
            // resample from the device rate to 16 kHz, and pack as Int16 PCM.
            function encodePCM16(chunks, srcRate) {
              let total = 0;
              for (const c of chunks) total += c.length;
              const merged = new Float32Array(total);
              let offset = 0;
              for (const c of chunks) { merged.set(c, offset); offset += c.length; }
              const ratio = srcRate / 16000;
              const outLength = Math.max(0, Math.floor(merged.length / ratio));
              const out = new Int16Array(outLength);
              for (let i = 0; i < outLength; i++) {
                const pos = i * ratio;
                const i0 = Math.floor(pos);
                const i1 = Math.min(i0 + 1, merged.length - 1);
                let s = merged[i0] + (merged[i1] - merged[i0]) * (pos - i0);
                s = Math.max(-1, Math.min(1, s));
                out[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
              }
              return out.buffer;
            }

            talk.addEventListener("pointerdown", e => {
              e.preventDefault();
              if (micEnabled) { startSpeaking(); } else { enableMic(); }
            });
            talk.addEventListener("pointerup", e => {
              e.preventDefault();
              if (recording) stopSpeaking(true);
            });
            talk.addEventListener("pointerleave", () => { if (recording) stopSpeaking(true); });
            talk.addEventListener("pointercancel", () => { if (recording) stopSpeaking(false); });
            talk.addEventListener("contextmenu", e => e.preventDefault());

            obtainTicket().catch(() => {
              showMessage("Question submissions are unavailable.", "error");
            });
          </script>
        </body>
        </html>
        """
    }

    private static func browserPage(token: String) -> String {
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
          <meta name="color-scheme" content="dark">
          <title>Classroom Captions</title>
          <style>
            :root { font-family: -apple-system, BlinkMacSystemFont, sans-serif; color-scheme: dark; }
            * { box-sizing: border-box; }
            body { margin: 0; min-height: 100dvh; background: #050505; color: white; }
            main { min-height: 100dvh; display: flex; flex-direction: column; padding: max(18px, env(safe-area-inset-top)) 20px max(24px, env(safe-area-inset-bottom)); }
            header { display: flex; justify-content: space-between; gap: 16px; align-items: center; color: #aaa; font-size: 14px; }
            #status[data-state="live"] { color: #62d982; }
            #captions { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; gap: 14px; overflow-y: auto; padding-top: 24px; }
            .final { font-size: clamp(25px, 7vw, 44px); line-height: 1.22; font-weight: 650; }
            .provisional { font-size: clamp(23px, 6.5vw, 40px); line-height: 1.22; color: #b8b8b8; font-style: italic; }
            .empty { color: #888; font-size: 22px; }
          </style>
        </head>
        <body>
          <main>
            <header><strong>Classroom Captions</strong><span id="status">Connecting…</span></header>
            <section id="captions" aria-live="polite"><div class="empty">Waiting for captions…</div></section>
          </main>
          <script>
            const token = "\(token)";
            const status = document.getElementById("status");
            const captions = document.getElementById("captions");
            const source = new EventSource("/events?token=" + encodeURIComponent(token));
            source.addEventListener("open", () => {
              status.textContent = "Live";
              status.dataset.state = "live";
            });
            source.addEventListener("error", () => {
              status.textContent = "Reconnecting…";
              status.dataset.state = "waiting";
            });
            source.addEventListener("captions", event => {
              const snapshot = JSON.parse(event.data);
              captions.replaceChildren();
              for (const line of snapshot.finalized) {
                const element = document.createElement("div");
                element.className = "final";
                element.textContent = line;
                captions.appendChild(element);
              }
              if (snapshot.provisional) {
                const element = document.createElement("div");
                element.className = "provisional";
                element.textContent = snapshot.provisional;
                captions.appendChild(element);
              }
              if (!snapshot.finalized.length && !snapshot.provisional) {
                const element = document.createElement("div");
                element.className = "empty";
                element.textContent = snapshot.sessionActive
                  ? "Listening…"
                  : "Waiting for the session to start…";
                captions.appendChild(element);
              }
              captions.scrollTop = captions.scrollHeight;
            });
          </script>
        </body>
        </html>
        """
    }
}
