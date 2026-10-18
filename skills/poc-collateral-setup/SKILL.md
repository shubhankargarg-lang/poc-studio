---
name: poc-collateral-setup
description: Install once per Mac, without admin rights or Homebrew, everything POC Studio needs to make collaterals (and documents) — Python 3.12 with every package, ffmpeg/ffprobe, pdftotext/pdftoppm, pandoc, LibreOffice, the Kokoro voice model, Spectral fonts, Playwright Chromium, lucide icons — then prove it works with a doctor check. Use at POC Studio Setup (it runs in the background), before Stage 5 Collaterals, or when someone asks to set up or check the collateral tools.
---

# POC collateral setup (macOS, no admin)

One install per Mac, into the user's own folders. Every later POC reuses it: the collateral kit's `kit/setup.sh`
sees the shared install and finishes in seconds with no downloads. Safe to re-run: every step checks first and
skips what is already there. On Linux it does nothing (the kit installs into the project folder there).

## Where things go

| What | Where |
|---|---|
| Shared home (no spaces in the path) | `~/.local/poc-collateral/` |
| Python 3.12 venv (all Python packages) | `~/.local/poc-collateral/venv` |
| Kokoro voice model (~350 MB) | `~/.local/poc-collateral/models` |
| Spectral fonts | `~/.local/poc-collateral/fonts` + `~/Library/Fonts` |
| Node tools (Playwright 1.56.1, lucide-static 0.468.0) + Chromium | `~/.local/poc-collateral/node`, `~/Library/Caches/ms-playwright` |
| Commands: `ffmpeg`, `ffprobe`, `pdftotext`, `pdftoppm`, `pandoc`, `soffice`, `python3.12` | `~/.local/bin` |
| LibreOffice | `~/Applications/LibreOffice.app` (or the existing `/Applications` one) |
| Environment for every shell | `~/.local/poc-collateral/env.sh` |
| Doctor (also run by `kit/setup.sh`) | `~/.local/poc-collateral/doctor.sh` |

How each tool comes without Homebrew or admin:
- **uv** from its GitHub release into `~/.local/bin`; **Python 3.12** through uv (never macOS's built-in Python,
  which can ask for a developer-tools install that needs admin).
- **Node.js 22** from nodejs.org into `~/.local/poc-collateral/node-runtime`, only if no Node 18+ is on the PATH.
- **ffmpeg 7** from the `imageio-ffmpeg` wheel (with the subtitles, freeze- and silence-detect filters the kit uses);
  **ffprobe**, **pdftotext**, **pdftoppm** are small Python stand-ins that answer the calls the kit makes; an existing
  real tool of the same name is kept.
- **pandoc** from the `pypandoc_binary` wheel (the reviewer reads `.docx` with it).
- **LibreOffice** `.dmg` from The Document Foundation, SHA-256 checked against the published sum, copied into
  `~/Applications`.
- **resvg-py** draws the deck icons (cairosvg needs libcairo from Homebrew).
- Corporate networks: downloads retry with a CA bundle built read-only from the macOS keychains
  (`SSL_CERT_FILE`, `NODE_EXTRA_CA_CERTS`, `PIP_CERT`, `UV_SYSTEM_CERTS`).

Find the scripts at `${CLAUDE_PLUGIN_ROOT}/skills/poc-collateral-setup/scripts/`, i.e. this skill's base directory
(the path Claude Code prints as "Base directory for this skill") + `/scripts`. If neither resolves:
`find ~/.claude/plugins -path '*poc-collateral-setup/scripts/setup.sh'`.

## 1. Already installed? (seconds)

```bash
[ -f ~/.local/poc-collateral/env.sh ] && bash ~/.local/poc-collateral/doctor.sh
```

Every line `ok` → nothing to do; say "Collateral tools already set up on this Mac" in one line.

## 2. Install (first time, or the doctor showed MISSING)

Tell the person in one line: "Setting up the collateral tools once on this Mac (about 1 GB into your user folder, no
admin needed); this runs in the background." Then run it **in the background** (Bash `run_in_background`; it takes
several minutes) and carry on with other work:

```bash
bash "<skill base dir>/scripts/setup.sh"
```

It ends with the doctor report. When it finishes:
- `setup finished` and every doctor line `ok` → log it in `context-log.md`.
- `FAILED: <step>` lines → run setup once more (most failures are a dropped download). If the same step fails again,
  tell the person in one line which tool is missing and what it blocks (e.g. "LibreOffice did not install: deck
  previews cannot be rendered"), and carry on; Stage 5 runs the doctor again before it starts.

## 3. Using it

- **Every command that needs these tools starts with `source ~/.local/poc-collateral/env.sh && `** (each shell
  starts fresh). Inside a collateral folder, `kit/setup.sh` writes a local `env.sh` that does the same, so there the
  rule is `source env.sh && `.
- The collateral kit needs nothing else: its `kit/setup.sh` links the shared models and fonts, installs the two npm
  packages from the shared cache, and runs the doctor.
- Sign-in for recording is `kit/auth.mjs` (the person signs in; Google SSO is fine; it saves only once the app opens).

## Never

- Sign in for the person, type a password, use `sudo`, or change system settings.
- Install with Homebrew (it needs admin on most company Macs).
- Delete anything outside `~/.local/poc-collateral` (re-runs overwrite only what this skill wrote).
