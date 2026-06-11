#!/bin/sh
# Download the offline rendering libraries used by the Assistant-answer overlay
# card (rich HTML: syntax-highlighted code + compiled LaTeX). Pinned versions,
# fetched into Resources/RenderAssets/ so the packaged app renders answers with
# no network dependency at runtime. Re-run to refresh.
set -eu

KATEX_VERSION=0.16.11
HLJS_VERSION=11.9.0
MDIT_VERSION=14.1.0

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
out="$root/Sources/ClassroomCaptions/RenderAssets"
fonts="$out/fonts"
mkdir -p "$fonts"

katex="https://cdn.jsdelivr.net/npm/katex@$KATEX_VERSION/dist"
hljs="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/$HLJS_VERSION"
mdit="https://cdn.jsdelivr.net/npm/markdown-it@$MDIT_VERSION/dist"

fetch() { curl -fsSL --max-time 30 -o "$2" "$1" && echo "  $(basename "$2") ($(wc -c <"$2") bytes)"; }

echo "KaTeX $KATEX_VERSION"
fetch "$katex/katex.min.css" "$out/katex.min.css"
fetch "$katex/katex.min.js" "$out/katex.min.js"
fetch "$katex/contrib/auto-render.min.js" "$out/auto-render.min.js"

echo "KaTeX fonts (parsed from katex.min.css)"
# katex.min.css references each font as url(fonts/NAME.woff2); fetch exactly those.
grep -oE 'fonts/[A-Za-z0-9_-]+\.woff2' "$out/katex.min.css" | sort -u | while read -r rel; do
    fetch "$katex/$rel" "$out/$rel"
done

echo "highlight.js $HLJS_VERSION"
fetch "$hljs/highlight.min.js" "$out/highlight.min.js"
fetch "$hljs/styles/github-dark.min.css" "$out/highlight-theme.min.css"

echo "markdown-it $MDIT_VERSION"
fetch "$mdit/markdown-it.min.js" "$out/markdown-it.min.js"

echo "done -> $out"
ls -1 "$out" "$fonts" | wc -l | tr -d ' ' | sed 's/$/ files/'
