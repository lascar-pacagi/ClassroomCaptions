#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MODEL_DIR="${VOXTRAL_MODEL_DIR:-$HOME/Library/Application Support/ClassroomCaptions/models/Voxtral-Mini-4B-Realtime-2602}"

if [ "$#" -lt 1 ]; then
    echo "usage: $0 AUDIO.wav [REFERENCE.txt]" >&2
    exit 1
fi

ARGS=(
    --model-dir "$MODEL_DIR"
    --audio "$1"
    --delay-ms "${VOXTRAL_DELAY_MS:-320}"
    --interval "${VOXTRAL_PROCESSING_INTERVAL:-1.0}"
    --chunk-ms "${VOXTRAL_CHUNK_MS:-100}"
)

if [ "$#" -ge 2 ]; then
    ARGS+=(--reference "$2")
fi

cd "$ROOT_DIR"
swift run -c release VoxtralBenchmark "${ARGS[@]}"
