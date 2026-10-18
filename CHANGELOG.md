# Changelog

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
