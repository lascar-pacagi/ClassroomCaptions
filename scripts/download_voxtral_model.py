#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path


REPOSITORY = "mistralai/Voxtral-Mini-4B-Realtime-2602"
FILES = (
    "consolidated.safetensors",
    "tekken.json",
    "params.json",
)


def default_destination():
    return (
        Path.home()
        / "Library"
        / "Application Support"
        / "ClassroomCaptions"
        / "models"
        / "Voxtral-Mini-4B-Realtime-2602"
    )


def download(filename, destination):
    target = destination / filename
    partial = target.with_suffix(target.suffix + ".partial")
    existing = partial.stat().st_size if partial.exists() else 0
    url = f"https://huggingface.co/{REPOSITORY}/resolve/main/{filename}?download=true"
    request = urllib.request.Request(url)
    if existing:
        request.add_header("Range", f"bytes={existing}-")

    print(f"Downloading {filename} ({existing} bytes already present)")
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=120) as response:
        content_range = response.headers.get("Content-Range")
        mode = "ab" if existing and content_range else "wb"
        if mode == "wb":
            existing = 0
        total_header = response.headers.get("Content-Length")
        total = existing + int(total_header) if total_header else None
        received = existing

        with partial.open(mode) as output:
            while True:
                chunk = response.read(8 * 1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                received += len(chunk)
                elapsed = max(0.001, time.monotonic() - started)
                rate = (received - existing) / elapsed / (1024 * 1024)
                if total:
                    percent = 100 * received / total
                    print(
                        f"\r  {percent:6.2f}%  {received / 2**30:.2f}/"
                        f"{total / 2**30:.2f} GiB  {rate:.1f} MiB/s",
                        end="",
                        flush=True,
                    )
                else:
                    print(
                        f"\r  {received / 2**30:.2f} GiB  {rate:.1f} MiB/s",
                        end="",
                        flush=True,
                    )
    print()
    os.replace(partial, target)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description="Download the official full-precision Voxtral Realtime model."
    )
    parser.add_argument("--destination", type=Path, default=default_destination())
    args = parser.parse_args()
    destination = args.destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)

    for filename in FILES:
        target = destination / filename
        if target.exists() and target.stat().st_size > 0:
            print(f"Using existing {filename}")
        else:
            download(filename, destination)

    manifest = {
        "repository": REPOSITORY,
        "downloaded_at_unix": time.time(),
        "files": {
            filename: {
                "bytes": (destination / filename).stat().st_size,
                "sha256": sha256(destination / filename),
            }
            for filename in FILES
        },
    }
    manifest_path = destination / "model-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Model ready: {destination}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
