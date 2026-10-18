#!/usr/bin/env bash
# Checks every collateral dependency by actually running it. Prints ok / MISSING per line; exit 1 if anything is missing.
H="$HOME/.local/poc-collateral"; [ -f "$H/env.sh" ] && source "$H/env.sh"
T=$(mktemp -d); bad=0
chk() { if eval "$2" >/dev/null 2>&1; then printf 'ok       %s\n' "$1"; else printf 'MISSING  %s\n' "$1"; bad=1; fi; }
echo "== collateral doctor"
chk "python3.12 venv"              "python3 -c 'import sys; assert sys.version_info >= (3,10)'"
chk "python packages"              "python3 -c 'import kokoro_onnx, soundfile, pptx, docx, openpyxl, numpy, PIL, resvg_py, imageio_ffmpeg, pypdf, pypdfium2'"
chk "node >= 18"                   "node -e 'process.exit(+process.versions.node.split(\".\")[0] >= 18 ? 0 : 1)'"
chk "playwright + chromium"        "cd '$H/node' && node -e \"require('playwright').chromium.launch().then(b=>b.close())\""
chk "lucide icons"                 "test -s '$H/node/node_modules/lucide-static/icons/camera.svg'"
chk "ffmpeg (encode + subtitles)"  "ffmpeg -v error -f lavfi -i testsrc=d=1:s=320x240 -y $T/t.mp4 && ffmpeg -hide_banner -filters | grep -q ' subtitles '"
chk "ffprobe (duration)"           "test \"\$(ffprobe -v error -show_entries format=duration -of csv=p=0 $T/t.mp4 | cut -c1)\" = 1"
chk "soffice (LibreOffice)"        "echo hi > $T/a.txt && soffice --headless --convert-to pdf --outdir $T $T/a.txt && test -s $T/a.pdf"
chk "pdftoppm"                     "pdftoppm -r 20 -png $T/a.pdf $T/p && ls $T/p-1.png"
chk "pandoc"                       "pandoc --version"
chk "pdftotext"                    "pdftotext -layout $T/a.pdf - | grep -q hi"
chk "Kokoro model"                 "test -s \"\$KOKORO_DIR/kokoro-v1.0.onnx\" && test -s \"\$KOKORO_DIR/voices-v1.0.bin\""
chk "Spectral fonts"               "ls ~/Library/Fonts/Spectral-MediumItalic.ttf"
chk "resvg icon render"            "python3 -c \"import resvg_py; resvg_py.svg_to_bytes(svg_string=open('$H/node/node_modules/lucide-static/icons/camera.svg').read(), width=64, height=64)\""
rm -rf "$T"
[ $bad = 0 ] && echo "all dependencies ok" || { echo "some dependencies missing: re-run poc-collateral-setup (setup.sh prints the failing step)"; exit 1; }
