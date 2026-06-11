import SwiftUI
import WebKit

/// Direction for the spoken scroll commands applied to the answer card.
enum AnswerScrollDirection: Equatable, Sendable {
    case up
    case down
}

/// Serves the bundled rendering assets (KaTeX, highlight.js, markdown-it, our
/// render.js / overlay.css and the KaTeX fonts) to the answer WebView over a
/// private `ccassets://` scheme. It exposes *only* files inside the bundled
/// RenderAssets directory, so the page can load our libraries but the CSP can
/// still forbid every network origin — the model cannot reach anything.
final class AnswerAssetSchemeHandler: NSObject, WKURLSchemeHandler {
    static let scheme = "ccassets"

    private let root: URL?

    override init() {
        root = Bundle.module.resourceURL?
            .appendingPathComponent("RenderAssets", isDirectory: true)
        super.init()
    }

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url, let root else {
            task.didFailWithError(URLError(.fileDoesNotExist))
            return
        }
        var relative = url.path
        if relative.hasPrefix("/") { relative.removeFirst() }
        let fileURL = root.appendingPathComponent(relative).standardizedFileURL
        // Refuse anything that escapes the assets directory.
        guard fileURL.path.hasPrefix(root.standardizedFileURL.path),
              let data = try? Data(contentsOf: fileURL) else {
            task.didFailWithError(URLError(.fileDoesNotExist))
            return
        }
        let response = URLResponse(
            url: url,
            mimeType: Self.mimeType(forExtension: fileURL.pathExtension),
            expectedContentLength: data.count,
            textEncodingName: nil
        )
        task.didReceive(response)
        task.didReceive(data)
        task.didFinish()
    }

    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}

    private static func mimeType(forExtension ext: String) -> String {
        switch ext.lowercased() {
        case "css": return "text/css"
        case "js": return "application/javascript"
        case "json": return "application/json"
        case "html": return "text/html"
        case "woff2": return "font/woff2"
        case "woff": return "font/woff"
        case "ttf": return "font/ttf"
        default: return "application/octet-stream"
        }
    }
}

/// Builds the self-contained HTML page that renders the model's Markdown answer.
enum ModelAnswerRenderer {
    static func html(markdown: String, fontSize: Double) -> String {
        // Inject the Markdown as JSON inside a non-executable <script> data block.
        // markdown-it (html:false) escapes any HTML the model emitted, and these
        // replacements stop a literal "</script>" in the answer from closing the
        // block early, so nothing the model wrote can become live markup.
        let data = (try? JSONSerialization.data(
            withJSONObject: markdown,
            options: [.fragmentsAllowed]
        )) ?? Data("\"\"".utf8)
        let safe = (String(data: data, encoding: .utf8) ?? "\"\"")
            .replacingOccurrences(of: "<", with: "\\u003c")
            .replacingOccurrences(of: ">", with: "\\u003e")
            .replacingOccurrences(of: "&", with: "\\u0026")

        let csp = [
            "default-src 'none'",
            "script-src ccassets:",
            "style-src ccassets: 'unsafe-inline'",
            "font-src ccassets:",
            "img-src ccassets: data:",
            "connect-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
        ].joined(separator: "; ")

        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="Content-Security-Policy" content="\(csp)">
        <link rel="stylesheet" href="ccassets://local/katex.min.css">
        <link rel="stylesheet" href="ccassets://local/highlight-theme.min.css">
        <link rel="stylesheet" href="ccassets://local/overlay.css">
        <style>body { font-size: \(max(10, min(40, Int(fontSize.rounded()))))px; }</style>
        </head>
        <body>
        <div id="content"></div>
        <script type="application/json" id="md">\(safe)</script>
        <script src="ccassets://local/markdown-it.min.js"></script>
        <script src="ccassets://local/highlight.min.js"></script>
        <script src="ccassets://local/katex.min.js"></script>
        <script src="ccassets://local/auto-render.min.js"></script>
        <script src="ccassets://local/render.js"></script>
        </body>
        </html>
        """
    }
}

/// A locked-down WebView that renders one model answer as rich HTML inside the
/// overlay. It can load only our bundled assets, runs no remote code, blocks all
/// navigation, and exposes nothing of the host machine; the spoken scroll
/// commands page through long answers via `scrollToken`.
struct ModelAnswerView: NSViewRepresentable {
    let markdown: String
    let fontSize: Double
    let scrollToken: Int
    let scrollDirection: AnswerScrollDirection

    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeNSView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.setURLSchemeHandler(
            AnswerAssetSchemeHandler(),
            forURLScheme: AnswerAssetSchemeHandler.scheme
        )
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.setValue(false, forKey: "drawsBackground")
        webView.underPageBackgroundColor = .clear

        context.coordinator.webView = webView
        context.coordinator.loadedMarkdown = markdown
        context.coordinator.loadedFontSize = fontSize
        context.coordinator.lastScrollToken = scrollToken
        webView.loadHTMLString(
            ModelAnswerRenderer.html(markdown: markdown, fontSize: fontSize),
            baseURL: URL(string: "ccassets://local/")
        )
        return webView
    }

    func updateNSView(_ webView: WKWebView, context: Context) {
        if context.coordinator.loadedMarkdown != markdown
            || context.coordinator.loadedFontSize != fontSize {
            context.coordinator.loadedMarkdown = markdown
            context.coordinator.loadedFontSize = fontSize
            webView.loadHTMLString(
                ModelAnswerRenderer.html(markdown: markdown, fontSize: fontSize),
                baseURL: URL(string: "ccassets://local/")
            )
        }
        if context.coordinator.lastScrollToken != scrollToken {
            context.coordinator.lastScrollToken = scrollToken
            let delta = scrollDirection == .down ? 260 : -260
            webView.evaluateJavaScript(
                "window.scrollBy({top: \(delta), left: 0, behavior: 'smooth'});",
                completionHandler: nil
            )
        }
    }

    final class Coordinator: NSObject, WKNavigationDelegate {
        weak var webView: WKWebView?
        var loadedMarkdown: String?
        var loadedFontSize: Double = 0
        var lastScrollToken = 0

        // Allow only the in-memory load and our asset scheme; refuse every
        // attempt to navigate elsewhere (e.g. a link in the answer). The async
        // form matches the delegate requirement exactly so it is actually used.
        @MainActor
        func webView(
            _ webView: WKWebView,
            decidePolicyFor navigationAction: WKNavigationAction
        ) async -> WKNavigationActionPolicy {
            let scheme = navigationAction.request.url?.scheme
            return scheme == AnswerAssetSchemeHandler.scheme || scheme == "about"
                ? .allow
                : .cancel
        }
    }
}
