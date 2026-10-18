#!/usr/bin/env bash
# POC collateral dependencies, installed into the user's own folders. No sudo, no Homebrew, no admin password.
# Safe to re-run: each step checks first. Ends with the doctor report.
set -uo pipefail
if [ "$(uname -s)" != Darwin ]; then
  echo "poc-collateral-setup is for macOS. On Linux, kit/setup.sh installs into the project folder (apt-get install -y ffmpeg poppler-utils libreoffice pandoc)."; exit 0
fi

HOME_DIR="$HOME/.local/poc-collateral"; BIN="$HOME/.local/bin"; SKILL="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$HOME_DIR/venv"; MODELS="$HOME_DIR/models"; FONTS="$HOME_DIR/fonts"; NODEDIR="$HOME_DIR/node"
PY_VERSION=3.12; NODE_VERSION=22.12.0; PLAYWRIGHT=1.56.1; LUCIDE=0.468.0
mkdir -p "$HOME_DIR" "$BIN" "$MODELS" "$FONTS" "$NODEDIR" "$HOME/Library/Fonts" "$HOME/Applications"
export PATH="$BIN:$HOME_DIR/node-runtime/bin:$PATH"
ARCH="$(uname -m)"   # arm64 or x86_64
step() { printf '\n== %s\n' "$*"; }
fail() { printf 'FAILED: %s\n' "$*"; FAILED=1; }
FAILED=0

# Corporate TLS interception: build a CA bundle from the macOS keychains (read-only, no admin) and use it everywhere.
CA="$HOME_DIR/ca.pem"
if [ ! -s "$CA" ]; then
  security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain > "$CA" 2>/dev/null || true
  security find-certificate -a -p /Library/Keychains/System.keychain >> "$CA" 2>/dev/null || true
  security find-certificate -a -p "$HOME/Library/Keychains/login.keychain-db" >> "$CA" 2>/dev/null || true
fi
export UV_SYSTEM_CERTS=1 SSL_CERT_FILE="$CA" NODE_EXTRA_CA_CERTS="$CA" PIP_CERT="$CA" REQUESTS_CA_BUNDLE="$CA" CURL_CA_BUNDLE="$CA"
dl() { # url out: curl with retries; falls back to the system trust store if the bundle is refused
  curl -fsSL --retry 3 --retry-all-errors --connect-timeout 30 -o "$2" "$1" || env -u CURL_CA_BUNDLE curl -fsSL --retry 3 --connect-timeout 30 -o "$2" "$1"; }

step "uv (Python installer)"
if ! command -v uv >/dev/null; then
  T=$(mktemp -d); A=$([ "$ARCH" = arm64 ] && echo aarch64-apple-darwin || echo x86_64-apple-darwin)
  dl "https://github.com/astral-sh/uv/releases/latest/download/uv-$A.tar.gz" "$T/uv.tgz" && tar -xzf "$T/uv.tgz" -C "$T" \
    && cp "$T"/uv-*/uv "$T"/uv-*/uvx "$BIN/" && chmod +x "$BIN/uv" "$BIN/uvx" || fail "uv download"
fi
uv --version || fail "uv"

step "Python $PY_VERSION + venv"
uv python install "$PY_VERSION" >/dev/null 2>&1 || fail "uv python install"
PY="$(uv python find "$PY_VERSION" 2>/dev/null)"; [ -n "$PY" ] && ln -sf "$PY" "$BIN/python$PY_VERSION"
[ -x "$VENV/bin/python" ] || uv venv -p "$PY_VERSION" "$VENV" >/dev/null || fail "venv"
uv pip install -q -p "$VENV/bin/python" pip kokoro-onnx soundfile python-pptx python-docx openpyxl numpy pillow resvg-py imageio-ffmpeg pypdf pypdfium2 \
  pypandoc_binary || fail "python packages"
ln -sfn "$VENV" "$HOME/.local/pocvenv"   # space-free path some earlier projects used

step "ffmpeg (imageio-ffmpeg) + ffprobe / pdftotext / pdftoppm stand-ins"
FF="$("$VENV/bin/python" -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null)"
[ -n "$FF" ] && ln -sf "$FF" "$BIN/ffmpeg" || fail "ffmpeg"
for t in ffprobe pdftotext pdftoppm; do
  if [ -e "$BIN/$t" ] && ! head -1 "$BIN/$t" | grep -q "poc-collateral\|pocvenv"; then echo "keep existing $t (not ours)"; continue; fi
  { echo "#!$VENV/bin/python"; tail -n +2 "$SKILL/scripts/standins/$t.py"; } > "$BIN/$t" && chmod +x "$BIN/$t"
done

step "pandoc (from the pypandoc_binary wheel)"
PD="$("$VENV/bin/python" -c 'import pypandoc;print(pypandoc.get_pandoc_path())' 2>/dev/null)"
if [ -n "$PD" ] && { [ ! -e "$BIN/pandoc" ] || [ -L "$BIN/pandoc" ]; }; then ln -sf "$PD" "$BIN/pandoc"; fi
command -v pandoc >/dev/null || fail "pandoc"

step "Node.js (user folder if none is on PATH)"
if ! command -v node >/dev/null || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]; then
  N=$([ "$ARCH" = arm64 ] && echo arm64 || echo x64); T=$(mktemp -d)
  dl "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-darwin-$N.tar.gz" "$T/node.tgz" \
    && mkdir -p "$HOME_DIR/node-runtime" && tar -xzf "$T/node.tgz" -C "$HOME_DIR/node-runtime" --strip-components 1 || fail "node download"
fi
node --version || fail "node"

step "Playwright $PLAYWRIGHT + lucide-static + Chromium"
( cd "$NODEDIR" && { [ -f package.json ] || npm init -y >/dev/null; } \
  && npm i --no-audit --no-fund "playwright@$PLAYWRIGHT" "lucide-static@$LUCIDE" >/dev/null \
  && npx playwright install chromium >/dev/null ) || fail "playwright"

step "Kokoro voice model (~350 MB)"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$MODELS/$f" ] || dl "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f" "$MODELS/$f" || fail "model $f"
done

step "Spectral fonts"
for w in Light Regular Italic Medium MediumItalic SemiBold; do
  [ -s "$FONTS/Spectral-$w.ttf" ] || dl "https://raw.githubusercontent.com/google/fonts/main/ofl/spectral/Spectral-$w.ttf" "$FONTS/Spectral-$w.ttf" || fail "font $w"
  cp -n "$FONTS/Spectral-$w.ttf" "$HOME/Library/Fonts/" 2>/dev/null || true
done

step "LibreOffice (user Applications, checksum verified)"
SOFFICE="$HOME/Applications/LibreOffice.app/Contents/MacOS/soffice"
[ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ] && SOFFICE=/Applications/LibreOffice.app/Contents/MacOS/soffice
if [ ! -x "$SOFFICE" ]; then
  BASE=https://download.documentfoundation.org/libreoffice/stable
  V=$(curl -fsSL --retry 3 --retry-all-errors "$BASE/" | grep -oE 'href="[0-9]+\.[0-9]+\.[0-9]+/"' | grep -oE '[0-9.]+[0-9]' | sort -V | tail -1)
  LA=$([ "$ARCH" = arm64 ] && echo aarch64 || echo x86_64); F="LibreOffice_${V}_MacOS_${LA}.dmg"; T=$(mktemp -d)
  WANT=$(curl -fsSL --retry 3 --retry-all-errors "$BASE/$V/mac/$LA/$F.sha256" | awk '{print $1}')
  OK=0
  for M in $(curl -fsSL --retry 3 --retry-all-errors "$BASE/$V/mac/$LA/$F.mirrorlist" | grep -oE 'https://[^"<]+\.dmg' | awk '!s[$0]++' | head -6); do
    curl -fsSL --retry 2 --connect-timeout 20 -o "$T/lo.dmg" "$M" && [ "$(shasum -a 256 "$T/lo.dmg" | awk '{print $1}')" = "$WANT" ] && { OK=1; break; }
  done
  if [ "$OK" = 1 ]; then
    MP=$(mktemp -d); hdiutil attach -nobrowse -readonly -mountpoint "$MP" "$T/lo.dmg" >/dev/null 2>&1 \
      && ditto "$MP/LibreOffice.app" "$HOME/Applications/LibreOffice.app"; hdiutil detach "$MP" >/dev/null 2>&1
    xattr -dr com.apple.quarantine "$HOME/Applications/LibreOffice.app" 2>/dev/null || true
  else fail "LibreOffice download (no mirror gave a file matching the published SHA-256)"; fi
  rm -rf "$T"
fi
[ -x "$SOFFICE" ] && ln -sf "$SOFFICE" "$BIN/soffice"

step "env.sh"
cat > "$HOME_DIR/env.sh" <<EOF
# source this in every shell that runs the collateral kit
export PATH="$BIN:$VENV/bin:$HOME_DIR/node-runtime/bin:\$PATH"
export KOKORO_DIR="$MODELS" UV_SYSTEM_CERTS=1
export PLAYWRIGHT_BROWSERS_PATH="\${PLAYWRIGHT_BROWSERS_PATH:-$HOME/Library/Caches/ms-playwright}"
EOF
echo "$HOME_DIR/env.sh"
cp "$SKILL/scripts/doctor.sh" "$HOME_DIR/doctor.sh" && chmod +x "$HOME_DIR/doctor.sh"   # kit/setup.sh runs it

bash "$SKILL/scripts/doctor.sh"
[ "$FAILED" = 0 ] && echo "setup finished" || { echo "setup finished with failures (see FAILED lines above)"; exit 1; }
