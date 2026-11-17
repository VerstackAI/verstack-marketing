#!/usr/bin/env bash
# Render a release template to PNG with headless Chrome.
# Usage: scripts/render.sh templates/release-1080x1350.html releases/2026-11-repeat-repairs/linkedin-1080x1350.png
# The size is read from the file name (WIDTHxHEIGHT).
set -euo pipefail
src="$1"; out="$2"
size=$(basename "$src" .html | grep -oE '[0-9]+x[0-9]+' | tail -1)
w=${size%x*}; h=${size#*x}
chrome=$(command -v google-chrome || command -v chromium || command -v chromium-browser || echo "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
mkdir -p "$(dirname "$out")"
"$chrome" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size="$w,$h" --virtual-time-budget=2000 --screenshot="$out" "file://$(cd "$(dirname "$src")" && pwd)/$(basename "$src")" 2>/dev/null
echo "Rendered $out ($w x $h)"
