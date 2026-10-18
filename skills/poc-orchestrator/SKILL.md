---
name: poc-orchestrator
description: Runs the UnifyApps POC Studio pipeline end to end for one client use case — Requirement Gathering → Scoping → Design System → Nebula build → Collaterals — with the General Reviewer checking every stage and answering every clarification question, an approval gate after each stage, and every file saved in the local client folder. Use when someone runs /poc-studio:start, says "start a POC for <client>", or asks to resume a POC Studio run.
---

# POC Studio orchestrator

You run one client's POC from requirement gathering to collaterals. You do not do the stages' work
yourself: each stage has its own skill, and you call it, check it with the reviewer, put it to the
person for approval, and hand the approved files to the next stage.

```
Start → 0 Setup → 1 Requirement Gathering → 2 Scoping → 3 Design System → 4 Nebula build → 5 Collaterals → Done
                         │                        │               │                 │                │
                     reviewer + gate         reviewer + gate  reviewer + gate   verify gate     reviewer + gate
                     (research skill available to every stage; reviewer answers every clarification question)
```

**Input — three values, all required:** the client name, the use case name and the **POC ID**, from
`/poc-studio:start <client> | <use case> | <POC ID>` (e.g. `/poc-studio:start Acme | Invoice matching | POC-acme-20261018`).
If a separator is missing, read the arguments sensibly; if any value is missing, ask once for the missing ones.
Everything else — website, personas, scope — comes from the documents the stages produce.

**The POC ID is mandatory: nothing starts without it.** Do not run Setup, check connectors, create folders or call any
stage until the person has given a POC ID. It looks like `POC-<client>-<YYYYMMDD>` (e.g. `POC-acme-20261018`): it
starts with `POC-` and ends with an 8-digit date. If what was given does not match that shape, show it back and ask
the person to confirm or correct it before starting. Use the POC ID exactly as given (same case) everywhere.

**The POC ID must exist in Orbit, and Orbit is kept in step with the run.** The `orbit-writeback` skill (load it
with the Skill tool, `poc-studio:orbit-writeback`) owns everything written to Orbit · POC Studio. The start command runs
its Setup (Nebula's tenant tools, POC ID check against `orbit_studio_poc`, the POC owner's name and email) before this skill;
if that has not happened in this session, run it first — not found → stop and ask the person to check the POC ID.
Then call it at every write-back moment listed under "Orbit write-back at each gate" below.

**The use case is the focus of the whole run.** A client often has several use cases in flight, and its Slack
channels, email threads and Drive folders mix them. Every stage works on **this** use case only:
- Requirement Gathering searches with the client name **and** the use-case terms, keeps material about this use case,
  and lists material about the client's other use cases as "other use case — not used" instead of mixing it in.
- Scoping, Design System, Nebula and Collaterals receive the use case name with every call, and the reviewer checks
  that each output stays on it.
- Each use case gets its own workspace, so two POCs for the same client never overwrite each other.

## The skills you call

Call each with the Skill tool. Use the plugin-qualified name the session lists (e.g. `poc-studio:scoping-l1-first`);
if a same-named skill exists from elsewhere, prefer the `poc-studio:` one.

| Stage | Skill | Owner (flowchart) |
|---|---|---|
| 1 Requirement Gathering | `requirement-gathering` | Aastha / Shubhankar |
| 2 Scoping | `scoping-l1-first` | Shubhankar |
| 3 Design System | `design-system` | Harshal |
| 4 Build | `/nebula:setup` (separate Nebula plugin) | Nebula |
| 5 Collaterals | `poc-collateral-studio` | Utkarsh Vasu |
| Any stage, outside facts | `research` | Lakshya / Gourav |
| Every gate, Orbit write-back | `orbit-writeback` | — |
| Every stage, review + questions | `general-reviewer`, run by the `poc-reviewer` agent | Gourav |

**All research goes through the `research` skill.** When a stage (or you) needs outside facts, the stage's own
instructions already say to call `research`; make sure it does. Only if `research` is unavailable may a stage
fall back to its own web search, and it records that it did. Save each research answer to
`<workspace>/research/<stage>-<short-topic>.md` so later stages and the reviewer can reuse it.

## The workspace (everything lives in the local folder)

All files go inside the folder Claude Code is running in, under one folder per client, so every later step —
and any later session — can read them:

```
<cwd>/<client-slug>/<usecase-slug>/     ← <workspace>  (one folder per client, one sub-folder per use case)
  state.json                            stage status, approvals, paths (resume from here)
  context-log.md                        running record: asks, decisions, answers, approvals, feedback
  01-requirement-gathering/
    Requirement Gathering - <Client> - <Use case>.docx
    files/                              the client's own files, as pulled from Slack/Drive/Gmail
  02-scoping/
    scoping-document.docx               the build plan (Part A proposal, Part B build spec)
    _working/                           scoping's working notes, research, evidence log
  03-design-system/
    <slug>-design-system.html           the design system HTML Nebula reads (plus anything else the skill ships)
  04-build/
    build-summary.md                    Nebula's result: app name, preview link, published app URL, what was built
  05-collaterals/
    <slug>-collateral/out/              the 3 collaterals: demo script PDF, demo video (+ .srt), deck .pptx
  research/                             every research answer, by stage
  reviews/                              reviewer verdicts (*.yaml) and log.md
```

`<client-slug>` and `<usecase-slug>` are the names in lower case with hyphens (e.g. `acme-beverages` /
`shelf-compliance`); `<slug>` is `<client-slug>-<usecase-slug>` (e.g. `acme-beverages-shelf-compliance`). The
**POC ID** is the `work_id` in every reviewer request, and appears in `state.json`, the first line of
`context-log.md`, the title block of the Requirement Gathering and scoping documents, `04-build/build-summary.md`,
and the collateral brief (`brief.json` → `"poc_id"`, internal only). Create the tree at setup.

### state.json

```json
{ "poc_id": "POC-acme-20261018",
  "orbit": { "poc_id": "POC-acme-20261018", "poc_record_id": "<record id>", "owner": { "name": "…", "email": "…" },
             "documents": {}, "open_iterations": [], "failed_writes": [] },
  "client": "Acme Beverages", "use_case": "Shelf Compliance",
  "slug": "acme-beverages-shelf-compliance",
  "workspace": "<abs path>",
  "connectors": { "slack": true, "gmail": false, "drive": true, "calendar": true },
  "stages": {
    "requirement-gathering": { "status": "approved", "output": "01-requirement-gathering/Requirement Gathering - Acme Beverages - Shelf Compliance.docx", "review_rounds": 1 },
    "scoping":       { "status": "in_review" },
    "design-system": { "status": "pending" },
    "build":         { "status": "pending" },
    "collaterals":   { "status": "pending" } },
  "app": { "name": null, "preview_url": null, "published_url": null } }
```

Status values: `pending` → `running` → `in_review` → `awaiting_approval` → `approved` (or back to `running` on
requested changes). Update it at every transition.

### context-log.md

Append a dated line at every event: what the stage decided or assumed, every question and the answer it got (and
who answered: reviewer or person), every reviewer verdict, every gate result, and the person's feedback verbatim.
This file is the reviewer's memory of the use case; keep it factual and short.

## Resuming

If `<cwd>/<client-slug>/<usecase-slug>/state.json` exists (and has the same POC ID), read it and `context-log.md`, tell the person in one line where the
run stands, and continue from the first stage that is not `approved`. Never redo an approved stage unless the
person asks.

## Questions never go straight to the person

The stage skills are built not to ask questions. If any stage — or Nebula — still needs an answer:

1. Do not call AskUserQuestion and do not end your turn with a question. Send the question to the reviewer in
   **resolve** mode (see "Calling the reviewer").
2. Apply its answer, log it in `context-log.md`, and carry on.
3. Only an `ASK_HUMAN` disposition reaches the person, and then only as one question with the reviewer's
   recommended option first.

The plugin enforces this with two hooks: while the file `$CLAUDE_PROJECT_DIR/.poc-studio/autopilot` exists,
AskUserQuestion is blocked and redirected to the reviewer, and ending the turn is blocked once with a reminder (so a
plain-text question, e.g. from Nebula, is routed too). Create that file when a stage starts running; delete it right before
you put an approval gate or an `ASK_HUMAN` question to the person; recreate it when the stage work resumes.
Delete it when the run finishes or stops.

Always use the absolute path (stages `cd` into subfolders, and the shell keeps that directory):

```bash
F="${CLAUDE_PROJECT_DIR:-<cwd at setup>}/.poc-studio/autopilot"
mkdir -p "$(dirname "$F")" && echo "<workspace>" > "$F"     # stage running
rm -f "$F"                                                  # gate / ASK_HUMAN / sign-in / done
```

Record the absolute flag path in `state.json` (`"autopilot_flag"`) at setup and use it every time.

Sign-ins are the exception: the person always signs in themselves (Orbit, Slack, etc.); never type a password.

## Calling the reviewer

The reviewer must not be the session that wrote the work, so run it as a subagent: the Agent tool with
`subagent_type` `poc-studio:poc-reviewer` (or the name the session lists for the `poc-reviewer` agent). If that
agent type is unavailable, use a general-purpose subagent and tell it to load the `general-reviewer` skill first.

Write the request to `<workspace>/reviews/<stage>-<mode>-<n>.request.yaml` and pass its path in the prompt:

```yaml
request_id: <slug>-<stage>-<n>
workspace: <abs workspace path>
work_id: <POC ID>
mode: review | resolve
stage: requirement-gathering | research | scoping | design-system | build | collaterals
round: 1 | 2 | 3
owner: the person running POC Studio
audience: { who: <client audience from the context log, or "client stakeholders" before Stage 1 is approved>, stakes: low }
artifacts: [ <abs paths of the stage's outputs> ]          # review
upstream: { path: <approved upstream>, acceptance_criteria: [ ... ] }   # review; scoping 4.1 from stage 3 on
question: { text: <the question, verbatim>, options: [ ... ] }       # resolve
prior_verdict: <path>                                        # round 2+
```

The reviewer returns a verdict (and writes it to `<workspace>/reviews/`). Then:

| Verdict / disposition | What you do |
|---|---|
| `PASS` | Go to the approval gate. |
| `REVISE` | Re-run the stage skill on its own output with the fix lines (fix only what is listed), then review again. **At most 2 REVISE rounds**; after the second, go to the gate anyway and show the open findings. |
| `BLOCK` | Fix the blocking findings the same way, then review again. If it still blocks after round 2, go to the gate and show the blocking findings, so the person can override (quote the finding id and a reason; log it). |
| `ASK_HUMAN` | Put the one question to the person (autopilot file removed), log the answer as a human decision, continue. |
| `REQUEST_RESEARCH` / `research_request` | Call the `research` skill with it, save the answer, give it back to the reviewer or the stage. |
| `DECIDE` (resolve) | Apply the answer, log it, continue. |
| `SEND_BACK` (resolve) | The question was really a defect in the work: fix it in the stage, continue. |
| `INVALID_REQUEST` | Fix the request field it names and call again. |

## The approval gate (after every stage)

Remove the autopilot file, then:
1. Tell the person in a few lines: what the stage produced (with the saved paths), the reviewer's verdict and
   score, any assumptions marked `check_this`, and any open findings.
2. Ask with AskUserQuestion: **Approve and continue to <next stage>** / **Request changes** (they can type the
   changes in "Other").
3. **Approve** → mark the stage `approved` in `state.json`, log it, move on.
   **Changes** → log the feedback verbatim (it is now a human decision for every later review), re-run the stage
   skill to apply it, review again (round counter restarts for the new feedback), and gate again.

Never advance without an explicit approval.

## Orbit write-back at each gate

Every gate is mirrored to Orbit by the `orbit-writeback` skill (its table "The plugin's gates → Orbit moments" is the
reference). Do the write **before** putting the gate to the person (posting) and **right after** their answer
(decision) — **except G4**, which is written only after the collaterals are approved — so Orbit and the Slack thread always show the same state as the chat:

| In the run | Orbit moment (orbit-writeback) |
|---|---|
| Stage done + reviewed, before its gate | **M1** — G1 (RG + every discovered client file) · G2a (scoping doc) · G2b (design system) · G3 (published app) |
| Person approves | **M2** — G1 · G2a (scoping: BRD approved only) · G2 (design system: G2 approved) · G3 |
| Person asks for changes (their text, verbatim) | **M3** — Iteration row + activities; more text about the same change is added to that iteration |
| The reworked document is ready, before re-gating | **M5** — new version, old one superseded, iteration closed |
| Collaterals approved | **M1 · G4** — upload script PDF, deck, video; demo_ready |
| Nebula starts building | **M4** — stage `5_build` (if not already) |
| Run blocked (sign-in, tools, missing input) / stopped / resumed | **M6** |

`slack_notification: true` is sent only by M1 and M5 (when files are written or a new version is posted). If a write
fails three times, tell the person in one line and carry on; the run never stops because Orbit is unreachable,
except at the start (the POC ID must be verified).

---

## 0 · Setup

1. Get the client name, the use case name and the POC ID (all three required; stop and ask if the POC ID is missing).
   Make the slugs and the workspace tree. If it exists, resume (above) — but if its `state.json` has a **different**
   POC ID, stop and ask the person whether this is the same POC (resume) or a new one (then use a new folder
   `<client-slug>/<usecase-slug>-<POC ID>/`).
   If the client folder already holds **other** use cases, mention them in one line and keep them untouched.
2. **Connector check.** Look for each connector's tools with a tool search (`slack`, `gmail`, `drive`, `calendar`).
   - **Slack is required.** If no Slack tools are found, stop and ask the person to connect Slack (in Claude Code:
     `/mcp`, or connect it as a claude.ai connector), then check again. Do not start Stage 1 without it.
   - Gmail, Google Drive and Google Calendar are optional: list which are connected and carry on; the
     Requirement Gathering document records the missing ones as "Not connected".
3. Write `state.json` and the first lines of `context-log.md` (client, **use case**, date, connectors), then these **standing
   human decisions** (the owner set them for every run; the reviewer applies them):
   - Questions during stages are answered by the reviewer from context and assumptions, not the person.
   - Design system: if brand-colour sources disagree, pick the colour that fits the use case best; if no client logo
     file exists, build the logo kit from the UnifyApps logo; the style guide is a local HTML file.
   - Build: Nebula in Sonic mode on Orbit UAT; deploying/testing the POC app there is pre-approved; model IDs: Nebula's
     recommendation, else Nebula chooses, else any available model; no reviewer review of the build.
   - Collaterals: bundled UnifyApps template; no Doc deliverable; the person signs in to Orbit.
   - **POC data policy (owner decision):** POC Studio builds proofs of concept with dummy data. The app's seed data,
     the documents and the collaterals use made-up values, never real customer records, so public Orbit links are
     approved for every document, including the client files found during discovery. Do not warn about or ask again
     about public uploads.
   - The person's own Slack, Gmail, Drive and Calendar accounts are read-only: nothing is posted or sent from them.
     The one exception is Orbit: the `orbit-writeback` uploads to Orbit and its `slack_notification` (which makes
     Orbit post the gate to the POC's Slack thread) are owner-approved.
4. **Tools check, now, while the person is at the screen** (so the collateral stage is never blocked hours later).
   Check with `command -v` / `brew list`: `brew`, `ffmpeg`, `pdftotext` (poppler), `soffice` (LibreOffice),
   `pandoc`, `node`, `python3` (3.10+).
   - **System tools need the person's Mac password, which Claude never types.** If any are missing, give the person
     one block to paste into Terminal, with only the missing lines, and wait for them to say it is done:
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"   # only if brew is missing
     brew install ffmpeg poppler pandoc node python@3.12
     brew install --cask libreoffice
     ```
     (Linux: `sudo apt-get install -y ffmpeg poppler-utils pandoc nodejs libreoffice`.) Then re-check. If the person
     wants to skip, log it and carry on; the collateral stage will show the same block again.
   - **Everything that needs no password, Claude installs itself now:** `pip3 install python-docx python-pptx
     openpyxl kokoro-onnx soundfile cairosvg numpy pillow` (add `--break-system-packages` if pip refuses), and
     `npx playwright install chromium`.
   Log what was installed in `context-log.md`.
5. Tell the person in one or two lines what will happen, then start Stage 1.

## 1 · Requirement Gathering

- Create the autopilot file. Call `requirement-gathering` with the client name, **the use case name** and the stage folder
  `<workspace>/01-requirement-gathering/` (client files into `files/`, the document into the folder).
- The skill's own last step ("ask whether to proceed") is replaced by your reviewer + gate.
- Review: `stage: requirement-gathering`, artifacts = the .docx (and `files/` listing).
- **Orbit:** M1 · G1 before the gate (RG + every discovered client file); M2 on approve; M3 on changes; M5 before
  re-gating.
- Gate. The document's verdict (Ready / Ready with assumptions / Not ready) and its open questions are shown at
  the gate; proceeding on "Not ready" is the person's call.
- Log the client name, website, use case (as the document confirmed or refined it) and stated asks from the
  approved document in `context-log.md`.

## 2 · Scoping

- Create the autopilot file. Call `scoping-l1-first` with:
  - the use case name (the scope is this use case only; material about other use cases is out of the ask);
  - input 1: the approved `Requirement Gathering - <Client> - <Use case>.docx`;
  - input 2: everything in `01-requirement-gathering/files/`;
  - output path: `<workspace>/02-scoping/scoping-document.docx` (`_working/` beside it);
  - research through `research` (its section 4); it keeps its own `_working/research/`, and you also copy each
    answer to `<workspace>/research/scoping-<topic>.md`.
- It runs without asking the user; anything it cannot settle goes to the reviewer (resolve).
- Review: `stage: scoping`, upstream = the approved Requirement Gathering document. The reviewer reviews Part A
  as a plan and Part B as a build spec (detail in Part B is expected).
- **Orbit:** M1a · G2 (the scoping document, with notification) before the gate; M2a on approve (BRD approved only);
  M3 on changes; M5 before re-gating.
- Gate. Show the counts (L1 / L2 features, pages, objects, agents, workflows) and the top assumptions.

## 3 · Design System

The `design-system` skill is tested and its output is approved as is. **Call it exactly as it is; do not change,
extend or second-guess its steps.** Only these session facts are supplied by you:

- Create the autopilot file. Call `design-system` with:
  - **client name**, **use case** and **website**: from the approved Requirement Gathering / scoping documents (the website is in
    the client brief; if both are silent, the skill derives it);
  - **the BRD** = the approved `02-scoping/scoping-document.docx` (the skill's "BRD" means this document);
  - **where to save:** `<workspace>/03-design-system/`. The deliverable is the design system **HTML file** (the
    living style guide, with the token block and logo kit in it) saved there as
    `<slug>-design-system.html`, plus any other files the skill ships. Nebula reads the HTML from this
    folder. If an Artifact tool also exists in the session, publishing is optional; the local HTML is what counts.
- **The skill's two stops are answered without the person** (the reviewer's standing answers):
  - Brand hue ambiguous → pick the colour that fits the use case and audience best; record it in the port note.
  - No client logo file anywhere → build the logo kit from the UnifyApps logo bundled with this plugin
    (`assets/unifyapps-logo.png` in the plugin root; also `skills/poc-collateral-studio/assets/unifyapps-logo.png`;
    find it with `find ~/.claude/plugins -name unifyapps-logo.png` if the path is unclear); record it in the port note.
- The skill's hand-over questions are answered with the client in mind (read "Amogh" there as "the client").
- Review: `stage: design-system`, upstream = the approved scoping document.
- **Orbit:** M1b · G2 (the design system, with notification; stage moves to `4_design_system`) before the gate; M2 ·
  G2 on approve (G2 approved, stage `5_build`); M3 on changes; M5 before re-gating.
- Gate.

## 4 · Build with Nebula

- **Orbit:** M4 (stage `5_build`, if not already) when Nebula starts.
- Create the autopilot file. Invoke Nebula's start command, `/nebula:setup` (with the Skill tool as `nebula:setup`,
  or whatever name the session lists for it). Nebula updates itself when called; no update step is needed. If the Nebula plugin is not installed, stop and tell the person to
  install it, then continue.
- Give Nebula, in the invocation and again whenever it asks:
  - **Mode:** Sonic.
  - **Environment:** Orbit — `https://orbit.uat.unifyapps.com/`.
  - **Build plan:** `<workspace>/02-scoping/scoping-document.docx` (Part B is the build spec: objects §12, agents
    §13, workflows/automations §14, pages §11, seed data §19, build order §20).
  - **Use case / app name:** `<Client> — <Use case>` (so the app on Orbit is identifiable per use case).
  - **POC ID:** `<POC ID>` — give it to Nebula with the build so the build and the app can be traced to this POC.
  - **Design system:** `<workspace>/03-design-system/<slug>-design-system.html`.
  - **What to build:** a text-to-code app on UnifyApps with the agents, automations and objects listed in the
    build plan (L1 scope only).
  - **Questions:** tell Nebula that its questions will be answered by you (the session), not the person, so it
    should keep going; whenever it stops with a question — through AskUserQuestion or as plain text — answer it via
    the reviewer before doing anything else.
- **Every question Nebula asks is answered by the reviewer** (resolve mode, `stage: build`), not the person. Standing
  answers: Sonic mode; Orbit environment; for **model IDs** for agents and LLM tasks, pick the model Nebula
  recommends — if it recommends none, ask Nebula to select the most appropriate model for the task — if it cannot,
  pick any available model. Nebula's plan confirmation ("Start the Nebula build as planned?"): its recommended option
  ("Start it"). Seed-data file location (public or private): Nebula's recommended option, otherwise **private**.
  Sign-ins to Orbit are done by the person.
- **Test everything with Nebula, fix, then publish.** When Nebula reports the build complete, do **not** publish yet.
  Have Nebula test the whole app itself, in the same session, with its own testing tools (its app-verify / test skill
  or browser checks, whatever name the session lists for them; there is no reviewer review of the build):
  1. **Every page, one by one:** open each page in the app's preview (nav order from scoping §11), check it loads with
     seed data (no empty tables, charts or stage columns), click every button, tab, filter and link on it, and open
     every create/edit form and submit it once with test data.
  2. **Every automation / workflow** (scoping §14): run each one by its real trigger (the page button, the object event,
     a schedule run now, a manual trigger with test input) and check its result: the records it should write, the
     status it should change, the notification it should send. Failures, errors and empty results count as failed.
  3. **Every AI agent** (scoping §13): ask each of the spec's example prompts and check the answer matches the expected
     records from the seed data.
  4. **The demo storyline** (scoping §20.2): walk it end to end once, as the demo will run.
  5. **Fix and re-test:** every failure goes back to Nebula to fix (same session, Sonic mode), then that page,
     automation or agent is tested again, and anything the fix touched is re-tested too. Repeat until everything
     passes, **at most 3 fix rounds per failing item**; questions Nebula asks while fixing go to the reviewer as usual.
  6. **Report:** write `<workspace>/04-build/test-report.md`: one row per page, automation, agent and storyline step,
     with pass/fail, what was fixed and how many rounds, and anything still failing after 3 rounds (with the reason).
     Still-failing items are shown to the person at the verify gate; they never block publishing on their own.
- **Publish:** once testing is done, tell Nebula to publish the app on Orbit UAT (if its plan has not already
  published it) and to report **two links**: the published app URL, and the app's **preview link** (the
  link that opens the app directly with its seed data, without first creating a user in the Matrix app). If Nebula
  does not give the preview link, ask it for it explicitly.
- Then write `04-build/build-summary.md`: app name, **preview link**, published app URL, the Nebula **solution id**
  (`e_…`, needed for Orbit G3), what was built (objects,
  agents, automations, pages) as Nebula reported it, the test results (counts passed / fixed / still failing, linking
  `test-report.md`), and anything it could not build. Save both in `state.json` →
  `app.preview_url` and `app.published_url`.
- **Orbit:** M1 · G3 (the app, `solution_id`) before the verify gate; M2 · G3 on approve; M3 on changes; M5 (new app
  version, no upload) before re-gating.
- **Gate — verify the published AI solution:** remove the autopilot file, show the test summary (and any item still
  failing), and ask the person to open the published app on Orbit, verify it and approve moving forward to collaterals. Approve → Stage 5. Changes → pass them to Nebula (same session), let it fix and re-test, gate again. Later fixes to the app (e.g.
  from the collateral stage) also go through Nebula, and are listed at the next gate.

## 5 · Collaterals

- **Only three collaterals:** the demo script (PDF), the demo video (with subtitles) and the PPT deck. No
  walkthrough PDF and no swimlanes document (the swimlane is only a slide inside the deck).
- Create the autopilot file. Call `poc-collateral-studio`. Work in `<workspace>/05-collaterals/` so every output
  lands there. Supply:
  - the app's **preview link** from `04-build/build-summary.md` / `state.json` → `app.preview_url` as every persona's
    `url` (and `public_url`) for discovery, capture and the video recording. **Never use the published
    Matrix app URL for these**: it requires creating a user before the app can be used. If no preview link was
    recorded, ask Nebula for it (same session) before recording;
  - the approved scoping document (problem statements, personas, journeys, demo storyline §20.2) and the
    Requirement Gathering document (the "today" pain points) as the build session's truth;
  - the template: the one bundled with the collateral skill (`assets/UnifyApps_template.pptx`) — always this one.
    The deck (problem statement → solution) is built from it.
- **Login:** if the app needs a sign-in, the skill opens its sign-in browser (`kit/auth.mjs`) on Orbit; remove the
  autopilot file and ask the person to log in to Orbit there, then continue. Never type a password.
- Install whatever the toolkit needs (Node, Python packages, ffmpeg, poppler, Playwright Chromium, the voice model)
  when the stage needs it; its `kit/setup.sh` does most of this.
- Review: `stage: collaterals`, artifacts = everything in `out/`.
- **Orbit:** nothing before the gate. M3 (phase deliver) on changes; on approval, **M1 · G4** (upload script PDF, deck,
  video; demo_ready) — do it before marking the run done.
- Gate. On approval (after M1 · G4), mark the run done, delete the autopilot file, and give the person the list of files with
  their paths in the client folder.

## Rules for the whole run

- **Everything is saved in the workspace.** No stage output lives only in the chat.
- **Read only** in the person's accounts: nothing is posted, sent, uploaded or deleted in Slack, Gmail, Drive or
  Calendar from them. The only writes outside the local folder are the Orbit write-back (uploads and rows on
  Orbit · POC Studio, and Orbit's own Slack notification) done by `orbit-writeback`.
- **Never delete** anything you did not create in this run.
- **Tools and skills:** when a stage needs a tool or common skill (e.g. `docx`, `pptx`, `xlsx`, `pdf`, LibreOffice,
  pandoc, ffmpeg), install or load it then and continue. For Anthropic's document skills in Claude Code:
  `/plugin marketplace add anthropics/skills` then `/plugin install document-skills@anthropic-agent-skills`; if
  that is not possible, use the Python libraries (`python-docx`, `python-pptx`) directly.
- Keep the person informed with a task list (one item per stage) and a short line when each stage finishes; no
  running commentary.
