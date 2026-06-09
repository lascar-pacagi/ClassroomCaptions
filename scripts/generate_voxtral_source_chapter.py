#!/usr/bin/env python3
"""Generate the complete, annotated voxtral.c chapter.

The generator deliberately copies source text without rewriting it. It then
reconstructs the source from the generated blocks and compares every byte so a
documentation build cannot silently omit or alter a line.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Sources/CVoxtralEngine/Engine/voxtral.c"
OUTPUT = ROOT / "docs/generated/voxtral-c-source.qmd"

REGIONS = [
    (1, 110, "Translation unit, delay conditioning, and adapter lookup",
     "Imports establish the runtime dependencies. The first helpers construct "
     "the sinusoidal delay embedding and load adapter tensors. Check dimensions "
     "here first when a model revision fails during loading."),
    (111, 261, "Model loading and Metal warm-up",
     "This region creates the long-lived model context, opens each component, "
     "binds tensors, and exercises Metal kernels before live audio arrives. "
     "Every successful allocation must have a matching path in `vox_free`."),
    (262, 412, "Destruction, constants, and scalar helpers",
     "Destruction is intentionally centralized. The remaining helpers normalize "
     "text and convert BF16 token embeddings to float values used by the decoder."),
    (413, 537, "Streaming state, token classes, and output queue",
     "`vox_stream` is the runtime state machine. Separate fields represent audio "
     "history, encoder output, decoder KV state, queued text, and recovery state. "
     "The queue decouples model progress from Swift polling."),
    (538, 718, "Incremental convolution stem",
     "The convolution code accepts only newly available mel frames while retaining "
     "the exact left context required by each kernel. Stride alignment determines "
     "which outputs are stable enough to expose downstream."),
    (719, 783, "Compaction and reset operations",
     "Compaction bounds retained adapter features. Decoder reset discards language "
     "state without rebuilding audio state; full reset reconstructs the complete "
     "stream after recovery or context exhaustion."),
    (784, 911, "Incremental encoder and adapter",
     "New convolution outputs pass through the audio transformer and modality "
     "adapter. Counters are absolute where possible so buffer compaction cannot "
     "change temporal meaning."),
    (912, 969, "Alternative-token support",
     "Alternative candidates are diagnostic output. They must not mutate the "
     "greedy path selected for the actual caption stream."),
    (970, 1190, "Prompt prefill, decoding, and continuous recovery",
     "This is the central autoregressive loop. It pre-fills the text decoder with "
     "the audio-conditioned prompt, advances one token at a time, classifies "
     "control tokens, and recovers when continuous mode reaches a boundary."),
    (1191, 1312, "Public stream lifecycle and text retrieval",
     "Construction validates model state and allocates stream buffers. Feed, finish, "
     "and get form the public streaming contract used by the project-owned bridge."),
    (1313, 1597, "Stream destruction and convenience transcription paths",
     "The destructor mirrors stream construction. Convenience entry points retain "
     "the upstream one-shot workflows even though ClassroomCaptions normally uses "
     "the incremental API."),
    (1598, 1652, "Flush and live configuration controls",
     "Flush forces pending stable work through the pipeline. Setters constrain "
     "processing cadence, continuous mode, decoder context, and caption delay."),
]


def fenced_source(lines: list[str], start: int) -> str:
    body = "".join(lines)
    if not body.endswith("\n"):
        body += "\n"
    return (
        f'```{{.c .numberLines startFrom="{start}"}}\n'
        f"{body}"
        "```\n"
    )


def main() -> None:
    raw = SOURCE.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    assert len(lines) == 1652, f"expected 1652 lines, found {len(lines)}"

    chunks: list[str] = []
    emitted_source: list[str] = []
    digest = hashlib.sha256(raw).hexdigest()
    chunks.append(
        "---\n"
        'title: "voxtral.c: Complete Annotated Source"\n'
        "---\n\n"
        "This chapter contains every line of the exact `voxtral.c` compiled by "
        "ClassroomCaptions. The code is divided only for pagination; no line is "
        "abbreviated. Original line numbers are preserved. The build generator "
        "reconstructs all code blocks and compares them byte-for-byte with the "
        "source before writing this chapter.\n\n"
        f"Source SHA-256: `{digest}`.\n\n"
        "Read the preceding implementation chapter first. Here, use the prose "
        "before each region as a checklist: identify ownership, mutable state, "
        "counter units, failure exits, and the invariant preserved by each loop.\n\n"
    )

    for begin, end, title, notes in REGIONS:
        chunks.append(
            f'## Lines {begin}-{end}: {title} {{.source-region}}\n\n'
            f"::: {{.source-notes}}\n{notes}\n:::\n\n"
        )
        # Smaller blocks paginate reliably and keep exact source line numbers.
        for block_start in range(begin, end + 1, 55):
            block_end = min(block_start + 54, end)
            block = lines[block_start - 1:block_end]
            emitted_source.append("".join(block))
            chunks.append(
                f"### Source lines {block_start}-{block_end}\n\n"
                f"{fenced_source(block, block_start)}\n"
            )

    reconstructed = "".join(emitted_source)
    if reconstructed != text:
        raise RuntimeError("generated source blocks do not reproduce voxtral.c")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(chunks), encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)}: {len(lines)} lines, sha256={digest}")


if __name__ == "__main__":
    main()
