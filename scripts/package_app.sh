#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIGURATION="${1:-release}"
APP_NAME="ClassroomCaptions"
BUILD_DIR="$ROOT_DIR/.build/arm64-apple-macosx/$CONFIGURATION"
APP_DIR="$ROOT_DIR/dist/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"

cd "$ROOT_DIR"
swift build -c "$CONFIGURATION" --product "$APP_NAME"

rm -rf "$APP_DIR"
mkdir -p "$CONTENTS_DIR/MacOS" "$CONTENTS_DIR/Resources"
cp "$BUILD_DIR/$APP_NAME" "$CONTENTS_DIR/MacOS/$APP_NAME"
cp "$ROOT_DIR/Resources/Info.plist" "$CONTENTS_DIR/Info.plist"

# SwiftPM emits target resources (RenderAssets: KaTeX, highlight.js, markdown-it)
# in a side bundle that Bundle.module locates via Bundle.main.resourceURL. The
# Assistant-mode answer renderer needs it, so copy it into the .app's Resources.
RESOURCE_BUNDLE="$BUILD_DIR/${APP_NAME}_${APP_NAME}.bundle"
if [ -d "$RESOURCE_BUNDLE" ]; then
    cp -R "$RESOURCE_BUNDLE" "$CONTENTS_DIR/Resources/"
else
    echo "warning: resource bundle not found at $RESOURCE_BUNDLE" >&2
fi

codesign --force --deep --sign - "$APP_DIR"
echo "$APP_DIR"
