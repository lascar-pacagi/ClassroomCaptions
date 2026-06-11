// Renders the model's answer (Markdown) into rich HTML inside the locked-down
// overlay WebView: Markdown -> HTML (markdown-it with html:false, so any raw
// HTML the model emitted is escaped, never executed), syntax-highlighted code
// (highlight.js), and compiled LaTeX (KaTeX). Loaded as a same-origin asset so
// the page needs no inline script (strict CSP).
(function () {
  "use strict";

  function getMarkdown() {
    var node = document.getElementById("md");
    if (!node) return "";
    try {
      return JSON.parse(node.textContent);
    } catch (e) {
      return node.textContent || "";
    }
  }

  function makeRenderer() {
    var hasHljs = typeof window.hljs !== "undefined";
    return window.markdownit({
      html: false, // escape raw HTML from the model: nothing it writes executes
      linkify: false,
      breaks: false,
      highlight: function (code, lang) {
        if (hasHljs && lang && window.hljs.getLanguage(lang)) {
          try {
            return window.hljs.highlight(code, {
              language: lang,
              ignoreIllegals: true,
            }).value;
          } catch (e) {
            /* fall through to default escaping */
          }
        }
        return ""; // markdown-it escapes the code itself
      },
    });
  }

  function render() {
    var content = document.getElementById("content");
    if (!content) return;
    var md = getMarkdown();
    content.innerHTML = makeRenderer().render(md);

    if (typeof window.renderMathInElement === "function") {
      window.renderMathInElement(content, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\[", right: "\\]", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false },
        ],
        throwOnError: false,
        ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
      });
    }
    document.body.classList.add("ready");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
  } else {
    render();
  }
})();
