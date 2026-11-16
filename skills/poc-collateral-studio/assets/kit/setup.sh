#!/usr/bin/env bash
# kit/setup.sh: everything the pipeline needs. Safe to re-run.
# If poc-collateral-setup has installed the shared tools on this machine (~/.local/poc-collateral), reuse them:
# no downloads, done in seconds. Otherwise install into this project folder (Linux / cloud sandbox).
set -euo pipefail
SHARED="$HOME/.local/poc-collateral"
mkdir -p auth build out review
if [ -f "$SHARED/env.sh" ]; then
  printf 'source "%s"\n' "$SHARED/env.sh" > env.sh
  source env.sh
  [ -e models ] || ln -s "$SHARED/models" models
  [ -e fonts ] || ln -s "$SHARED/fonts" fonts
  [ -f package.json ] || npm init -y >/dev/null
  npm i --no-audit --no-fund --prefer-offline playwright@1.56.1 lucide-static@0.468.0 >/dev/null
  if [ -x "$SHARED/doctor.sh" ]; then bash "$SHARED/doctor.sh" || { echo "shared tools incomplete: run poc-collateral-setup again"; exit 1; }; fi
  echo "setup done (shared tools from $SHARED)"; exit 0
fi
: > env.sh   # every command starts with `source env.sh &&`; here there is nothing extra to load
[ -f package.json ] || npm init -y >/dev/null
npm i --no-audit --no-fund playwright@1.56.1 lucide-static@0.468.0 >/dev/null
# Use the machine's Chromium if Playwright already has one (cloud sandbox), else fetch it once.
if [ -z "${PLAYWRIGHT_BROWSERS_PATH:-}" ] && [ -z "${CHROME_PATH:-}" ]; then npx playwright install chromium >/dev/null; fi
PKGS="kokoro-onnx soundfile resvg-py python-pptx numpy pillow"
pip install -q --break-system-packages $PKGS 2>/dev/null || pip install -q $PKGS
command -v ffmpeg >/dev/null || { echo "ffmpeg is required (apt-get install -y ffmpeg; on a Mac run poc-collateral-setup)"; exit 1; }
command -v pdftotext >/dev/null || echo "WARN pdftotext missing (apt-get install -y poppler-utils; on a Mac run poc-collateral-setup): check.py cannot scan PDFs"
# Offline US-English narration model (Kokoro v1.0, ~350 MB, from GitHub releases).
mkdir -p models
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s models/$f ] || curl -sSfL -o models/$f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f
done
# Spectral, the template's typeface: for HTML renders, ffmpeg subtitles and LibreOffice previews.
mkdir -p fonts ~/.fonts
for w in Light Regular Italic Medium MediumItalic SemiBold; do
  [ -s fonts/Spectral-$w.ttf ] || curl -sSfL -o fonts/Spectral-$w.ttf https://raw.githubusercontent.com/google/fonts/main/ofl/spectral/Spectral-$w.ttf
  cp -n fonts/Spectral-$w.ttf ~/.fonts/ 2>/dev/null || true
done
fc-cache -f >/dev/null 2>&1 || true
echo "setup done"
