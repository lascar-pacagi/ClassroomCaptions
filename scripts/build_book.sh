#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

python3 scripts/generate_source_book.py
python3 scripts/generate_domain_chapter.py
quarto render docs
