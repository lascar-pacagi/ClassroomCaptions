import Foundation
import Network
import Security

/// Builds the TLS server identity (a certificate plus its private key) the local
/// HTTPS listener presents to browsers. Browsers only grant a page access to the
/// microphone over a *secure context* (HTTPS), so capturing a student's voice in
/// the browser requires this even on a private Wi-Fi network.
///
/// The identity is **self-signed**: there is no certificate authority, so the
/// Mac signs its own certificate. Browsers therefore show a one-time "not
/// trusted" warning that the student accepts; afterwards the connection is
/// encrypted and the microphone becomes available. The identity is generated
/// once with the system `openssl`, persisted, and reused so the warning is not
/// repeated every launch (it reappears only if the Mac's Wi-Fi address changes,
/// because the address is embedded in the certificate).
enum ServerTLSIdentity {
    enum Failure: LocalizedError {
        case opensslFailed(String)
        case importFailed(OSStatus)
        case noIdentity

        var errorDescription: String? {
            switch self {
            case .opensslFailed(let message):
                return "Could not generate the HTTPS certificate: \(message)"
            case .importFailed(let status):
                return "Could not load the HTTPS certificate (status \(status))."
            case .noIdentity:
                return "The generated PKCS#12 contained no identity."
            }
        }
    }

    // The PKCS#12 file is local to this user and only proves "same server as
    // before"; its passphrase is not a meaningful secret, so it is a constant.
    private static let passphrase = "classroomcaptions"
    private static let label = "ClassroomCaptions HTTPS"
    // The system LibreSSL produces a PKCS#12 that SecPKCS12Import accepts;
    // OpenSSL 3's modern default encryption would be rejected by Apple.
    private static let opensslPath = "/usr/bin/openssl"

    /// Returns a TLS identity whose certificate is valid for `ipv4`, generating
    /// and persisting it on first use (or when the address changed).
    static func makeIdentity(ipv4: String) throws -> sec_identity_t {
        let directory = try storageDirectory()
        let p12URL = directory.appendingPathComponent("identity.p12")
        let stampURL = directory.appendingPathComponent("address.txt")

        let storedAddress = try? String(contentsOf: stampURL, encoding: .utf8)
        if !FileManager.default.fileExists(atPath: p12URL.path)
            || storedAddress != ipv4 {
            try generate(p12URL: p12URL, ipv4: ipv4)
            try ipv4.write(to: stampURL, atomically: true, encoding: .utf8)
        }

        let data = try Data(contentsOf: p12URL)
        let secIdentity = try importIdentity(from: data)
        guard let identity = sec_identity_create(secIdentity) else {
            throw Failure.noIdentity
        }
        return identity
    }

    private static func storageDirectory() throws -> URL {
        let base = try FileManager.default.url(
            for: .applicationSupportDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )
        let directory = base
            .appendingPathComponent("ClassroomCaptions", isDirectory: true)
            .appendingPathComponent("tls", isDirectory: true)
        try FileManager.default.createDirectory(
            at: directory,
            withIntermediateDirectories: true,
            attributes: [.posixPermissions: 0o700]
        )
        return directory
    }

    private static func generate(p12URL: URL, ipv4: String) throws {
        let temporary = p12URL.deletingLastPathComponent()
            .appendingPathComponent("gen-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(
            at: temporary,
            withIntermediateDirectories: true,
            attributes: [.posixPermissions: 0o700]
        )
        defer { try? FileManager.default.removeItem(at: temporary) }

        let keyURL = temporary.appendingPathComponent("key.pem")
        let certURL = temporary.appendingPathComponent("cert.pem")

        // Self-signed certificate + key. The Wi-Fi IP goes in the Subject
        // Alternative Name so browsers match it to the address being visited.
        try runOpenSSL([
            "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", keyURL.path,
            "-out", certURL.path,
            "-days", "825",
            "-subj", "/CN=ClassroomCaptions",
            "-addext", "subjectAltName=IP:\(ipv4),DNS:classroomcaptions.local",
        ])
        // Bundle them into one PKCS#12 file, the format SecPKCS12Import reads.
        try runOpenSSL([
            "pkcs12", "-export",
            "-inkey", keyURL.path,
            "-in", certURL.path,
            "-out", p12URL.path,
            "-passout", "pass:\(passphrase)",
            "-name", label,
        ])
        try? FileManager.default.setAttributes(
            [.posixPermissions: 0o600], ofItemAtPath: p12URL.path
        )
    }

    private static func runOpenSSL(_ arguments: [String]) throws {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: opensslPath)
        process.arguments = arguments
        let errorPipe = Pipe()
        process.standardOutput = FileHandle.nullDevice
        process.standardError = errorPipe
        try process.run()
        let errorData = errorPipe.fileHandleForReading.readDataToEndOfFile()
        process.waitUntilExit()
        guard process.terminationStatus == 0 else {
            let message = String(data: errorData, encoding: .utf8) ?? "unknown error"
            throw Failure.opensslFailed(
                message.trimmingCharacters(in: .whitespacesAndNewlines)
            )
        }
    }

    private static func importIdentity(from data: Data) throws -> SecIdentity {
        let options = [kSecImportExportPassphrase as String: passphrase] as CFDictionary
        var items: CFArray?
        let status = SecPKCS12Import(data as CFData, options, &items)
        guard status == errSecSuccess else { throw Failure.importFailed(status) }
        guard let array = items as? [[String: Any]],
              let identity = array.first?[kSecImportItemIdentity as String] else {
            throw Failure.noIdentity
        }
        // SecPKCS12Import returns the identity as a SecIdentity (a cert + key
        // pair); the cast is to the concrete Security type.
        return identity as! SecIdentity
    }
}
