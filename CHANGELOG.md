# Changelog

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
