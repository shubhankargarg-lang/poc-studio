# Changelog

## 1.18.0
- Design system skill replaced with v10: a component kit with full component pages (anatomy, coded variants, every state, micro-interactions), pattern blueprints, every journey as a flow diagram and at most five full screens; a per-client design concept; all design choices made in the run and handed to Nebula as `#build-plan` and `#style-sets`, with `data-active` tags on every specimen; a design review before a 10-item checklist; lighter research depths; Fujairah render fixes.
- POC Studio edits kept in v10: UnifyApps stand-in logo when no client logo exists; no named reviewers in the hand-over questions; every research request states its search budget.
- Orchestrator: the Nebula hand-off follows the Composition contract, `#build-plan` and active specimens only; the five-screen limit is not to be expanded.
- Reviewer: design system checked against v10's 10-item list; undrawn pages and shells are never a finding.
- Research: a search budget stated by the caller sets the depth.

## 1.17.2
- Questions that wait on you now nudge the POC owner in the POC's Slack thread (not while autopilot routes questions to the reviewer).

## 1.17.0
- New skill `poc-collateral-setup` (from a successful run): installs every collateral tool once per Mac into the user's own folders, no admin and no Homebrew (Python 3.12 venv, ffmpeg, ffprobe/pdftotext/pdftoppm stand-ins, pandoc, LibreOffice, Kokoro voice, Spectral fonts, Playwright Chromium, lucide icons), with a doctor that runs each tool. Setup starts it in the background; Stage 5 runs the doctor first.
- Collateral kit: `kit/setup.sh` reuses the shared install (seconds, no downloads) and writes `env.sh`; every command starts with `source env.sh && `; deck icons drawn with resvg-py (cairosvg fallback); `kit/lint.mjs` works when the path has spaces; `kit/auth.mjs` waits for Google SSO to finish and saves only once the app opens; Orbit login set to `https://orbit.uat.unifyapps.com/login`.

## 1.16.0
- Demo video: copied into the person's Google Drive for desktop folder (`POC Studio/<POC ID> - <Client>/`), found and linked with the Drive connector, shared with the whole company through the `POC Studio` folder's General access. Setup runs a Video route check (Drive app installed and running, same account as the connector via a test file read back, folder shared with the company) and flags why the video would not ship automatically; manual drop stays as the fallback.

## 1.15.0
- Orbit: every approval write is read back and confirmed before the next stage starts; every new app version is posted (also after G3 approval); a Reconcile check on every resume and before G4 writes any missing approval or document version without moving the stage backwards.

## 1.14.0
- Collaterals: slow steps are recorded as they happen and the silent wait is cut out (`kit/trim.py`, after `build.py`): click → short beat → result, voice-over stays in sync, subtitles and scene times shifted; app-caused OVERRUN/SLOW count as fixed once trimmed.

## 1.13.2
- Scoping: brand guidelines found by web research when the client gives none (guidelines → live product → website), recorded as evidence with source type, light/dark balance and chromatic role; never promote a link/accent blue for a black-led brand; never ask about colours or theme in open questions; the design-system skill decides the palette and theme.

## 1.13.1
- /poc-studio:feedback rows carry a `skill` field (the skill or agent the feedback is about, or `general`), and the reply names it.

## 1.13.0
- Requirement Gathering: required Personas and journeys table; Stage-1 UX decisions (primary persona, device per persona, reuse vs rebuild) with source or stated default; checklist re-weighted to 12 items (personas and journeys = 25 points); Slack file retries cut to 2.
- Scoping: primary-persona rule and Primary column; Screen UX fields on every page (kept with the data bindings); home pages by persona type; prerequisites shown before the click (disabled with reason); Visual acceptance block in 4.1 (1280×800); demo storyline order; demo data rules in section 19.
- Build test: visual acceptance, blockers-before-click and the demo data rules (by script) are checked in the built app.

## 1.12.2
- The demo video always goes to Google Drive (any size), shared by link; that link is saved in Orbit. No Orbit upload for the video.

## 1.12.1
- Demo video over 20 MB goes to Google Drive (shared by link) and that link is saved in Orbit; Google Drive is now a required connector at setup, with Slack.

## 1.12.0
- Design system skill replaced with v6 (journeys as flows, signature components, agent drawers, per-client expression, brand source order, build contract), with two edits: UnifyApps stand-in logo when no client logo exists, 'Amogh' removed.
- Orchestration unchanged in flow: the stage still reads the approved scoping document and writes one HTML to `03-design-system/`, uploaded to Orbit as a public link; Nebula is told to follow the HTML's build contract; reviewer checks v6's finished-piece list.

## 1.11.0
- Build stage: Nebula tests every page, automation, AI agent and the demo storyline, fixes what fails (max 3 rounds per item), then publishes; results in `04-build/test-report.md` and the G3 summary.

## 1.10.2
- /feedback records POC-level feedback in Orbit for skill analysis (`/poc-studio:feedback <text>`, row in `orbit_studio_feedback`).
