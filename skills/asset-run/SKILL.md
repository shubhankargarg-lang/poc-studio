---
name: asset-run
description: Makes ONE POC Studio asset on its own — a Requirement Gathering document, a research report, a BRD (scoping document), a design system, an app, or the collaterals (demo script, deck, video; any of them) — without a POC and without running the other stages. Collects that asset's prerequisites in the chat first, then runs the existing stage skill unchanged and unattended, has the AI PM review it, writes it to Orbit as a one-off document (a new version every time), shows it in the chat and asks for approval. Loaded by the /poc-studio:requirements, research-report, brd, design, app and collaterals commands; not for the full pipeline (/poc-studio:start).
---

# One asset, end to end (`asset-run`)

A command (`/poc-studio:<asset>`) has already run its update check and names the asset. You make that one asset with
the plugin's existing parts — the stage skill, the AI PM, the autopilot hooks and orbit-writeback — and nothing else.
The full pipeline (`/poc-studio:start`, `poc-orchestrator`) is not involved and is never changed by a one-off run.

| Asset | Command | Stage skill | AI PM `stage` | Orbit `type` (one row each) | Output folder |
|---|---|---|---|---|---|
| `requirements` | `/poc-studio:requirements` | `requirement-gathering` | `requirement-gathering` | `requirements` | `01-requirement-gathering/` |
| `research-report` | `/poc-studio:research-report` | `research` | `research` | `research` | `research/` |
| `brd` | `/poc-studio:brd` | `scoping-l1-first` | `scoping` | `brd` | `02-scoping/` |
| `design` | `/poc-studio:design` | `design-system` | `design-system` | `design_system` | `03-design-system/` |
| `app` | `/poc-studio:app` | `ua:setup`, `platform-master`, `ua:plan` (Zen) — Stage 4 | `build` (Stage 4b) | `app` | `04-build/` |
| `collaterals` | `/poc-studio:collaterals` | `poc-collateral-studio` | `collaterals` | `demo_script`, `deck`, `video` (the ones chosen) | `05-collaterals/` |

Load every skill with the Skill tool by its plugin name (`poc-studio:<skill>`). `R` below is the AI PM's scripts folder:
`R=$(dirname "$(find ~/.claude/plugins -path '*ai-pm/scripts/lessons.py' | head -1)")`. On a Mac, every Bash command
that runs `python3`, `node`, `ffmpeg`, `soffice` or `pandoc` starts with `source ~/.local/poc-collateral/env.sh && `
once that file exists.

## 1 · Prerequisites (in the chat, before anything runs)

Unlike the pipeline, a one-off run **asks for what it is missing before the stage starts.** Only once every required
prerequisite is in hand does the autopilot flag go on and the stage run unattended.

**Parse the arguments** (`<a> | <b> | …`, as the command shows). Quotes around a value are dropped. A trailing value
that looks like `POC-<…>-<8 digits>` is the POC ID. A missing separator is read sensibly; anything still unclear is
asked for in the one question below.

**Collect each prerequisite in this order, and stop at the first source that has it:**
1. The command arguments.
2. An existing workspace for this client and use case (`<cwd>/<client-slug>/<usecase-slug>/`): an approved
   Requirement Gathering document, `02-scoping/scoping-document.docx`, `03-design-system/*-design-system.html`,
   `state.json` → `app.preview_url`, earlier one-off outputs in `state.json` → `standalone.runs`. Offer what you find
   in one line ("Found `02-scoping/scoping-document.docx` from 28 Oct — use it?"); the newest file first.
3. Otherwise ask the person: **one** AskUserQuestion (or one plain question for free text) that lists everything
   still missing at once. Accept a local file path, a file dropped into the chat, a Slack or Drive link (read through
   that connector; download the file into the workspace), or pasted text (save it as a `.md` file in the stage's
   `files/` or `_inputs/` folder, so the stage can read it).

Never ask for a password or a token. Sign-ins are done by the person, in the window the step opens.

**Per asset** (Required must be in hand before step 2; Optional is asked once, in the same question, and the run goes
on without it):

| Asset | Required | Optional | When something required is missing |
|---|---|---|---|
| requirements | Client name · Use case · Slack and Google Drive connectors (their tools are in the session) | Client website · Gmail and Calendar connectors | Connectors: stop and ask the person to connect them (in Claude Code: `/mcp`, or as a claude.ai connector), then check again, as Setup does |
| research-report | Client name · Topic · The question(s) | Purpose: internal check, working draft or client-facing (sets the depth) · Files to read first | Ask |
| brd | Client name · Use case · **At least one input**: an RG document, meeting notes, an email, client files, or a Slack or Drive link | Client website | Offer two options: "Run `/poc-studio:requirements` first" or "Paste or attach what you have" |
| design | Client name · Use case · **BRD or scoping document** (.docx or PDF) · Client website (ask once; accept "derive it", then the skill derives it) | Client logo file · Brand guidelines | Offer "Run `/poc-studio:brd` first" or "Attach a BRD" |
| app | Client name · Use case · **BRD or scoping document** · The UnifyApps Headless plugin (`ua`) installed and this folder set up on `orbit.uat.unifyapps.com` (`/ua:setup`) | Design system HTML (without one, say the build uses UnifyApps Headless's default look, and offer `/poc-studio:design` first) | Plugin or setup missing: tell the person what to install or run, then check again |
| collaterals | Client name · Use case · **Which collaterals** (always asked, below) · **App preview link** (Preview link rule) · Orbit sign-in valid · The collateral tools for the ones chosen | BRD or scoping document (strongly recommended: it drives the story and personas) · RG document · Audience: business, technical or mixed (else the skill decides) | Ask |

**Collaterals — which ones (always asked).** Unless the command text already says which (e.g. "deck only"), ask one
multi-select AskUserQuestion: "Which collaterals should I create?" with the options **Demo script (PDF)**, **Deck
(PPT)** and **Demo video (with subtitles)**; the person ticks one, two or all three. Record the choice in the run
(`"collaterals": ["deck", …]`). Then:
- **Orbit sign-in:** `node "$R/orbit_signin.mjs" --check`; if it is not valid, run `node "$R/orbit_signin.mjs"` and ask
  the person to sign in to Orbit in the window that opens (never type a password), then check again.
- **Tools:** on a Mac, run the `poc-collateral-setup` doctor (load that skill). If it is not all `ok`, run its install
  and wait for it (about 1 GB the first time; no admin, no Homebrew). On Linux, check `ffmpeg`, `pdftotext`, `soffice`,
  `node`, `python3` and give the person the one line to paste for anything missing.
- **Video route** (only when the video is chosen): run orbit-writeback's **Video route check** now, as Setup does. It
  never blocks the run; if it fails, say in one line that the video will not ship to Drive automatically, and why.

**Preview link (collaterals).** Apply orbit-writeback's **Preview link rule**: a code app's
`https://orbit.uat.unifyapps.com/agent-api/preview/b/<app id>/main` or a no-code app's
`https://orbit.uat.unifyapps.com/p/0/interfaces/<app id>/preview`. A published (`*.matrix-uat.unifyapps.com`,
`*.tensor-uat.unifyapps.com`) or builder link is turned into the preview link from the app id in it; without an id, ask
for the preview link. Never record from, or save, a matrix link.

**POC ID (optional on every command).** If one is given, verify it as `commands/start.md` Step 1 does (orbit-writeback
Setup: `get_records` on `orbit_studio_poc`, `poc_id` EQUAL). Found → the one-off row's `poc` is set. Not found → ask
once to correct it or drop it. If the check cannot run (UnifyApps Headless not installed or this folder not set up),
say so in one line and ask once: set it up and check again, or go on without the POC ID. Without a POC ID the run goes
ahead normally.

**Who made it (`created_by`).** There is no POC owner on a one-off run: use the person running the session — their
connected Slack profile name (read their own profile with the Slack connector), else `git config user.name`, else ask
once. Keep their email if the profile gives it. Save both in `state.json` → `standalone.created_by` /
`standalone.created_by_email` and reuse them on later runs in this workspace.

**Retry earlier failed writes.** If `state.json` → `standalone.failed_writes` has entries, retry them now (orbit-writeback,
"One-off documents" → Failures) and say in one line what was written.

## 2 · Workspace and run state

1. Use the pipeline's tree: `<cwd>/<client-slug>/<usecase-slug>/` (slugs: lower case, every run of non-letters/digits
   → `-`, no `-` at the start or end: `[Test] Acme` → `test-acme`). A research report uses the topic as the use case (`<topic-slug>`). Create the folders the asset needs
   (`01-requirement-gathering/files/`, `02-scoping/`, `03-design-system/`, `04-build/`, `05-collaterals/`, `research/`,
   `reviews/`) and `context-log.md` if it does not exist (first line: client, use case, "one-off runs", date).
2. **Protect what is already there.** Before a stage writes a file that already exists, copy the existing file to
   `<stage folder>/_previous/<file name> <YYYYMMDD-HHMM>` (never delete). If that file is an output of a pipeline run
   (`state.json` → `stages.<stage>.output`, or the pipeline's fixed output path while that stage is not `pending`),
   write the one-off into `<stage folder>/one-off/` instead, so the pipeline's own file never changes.
3. Run state goes in `state.json` under the key **`standalone`** (create `state.json` with only this key if there is
   none). A one-off run never changes `stages`, `orbit`, `poc_id`, `app` or any gate state of a pipeline run in the
   same workspace.
   ```json
   "standalone": { "runs": [ { "asset": "brd", "started_at": "<ISO>", "status": "running | in_review | done",
       "document_id": "SA-acme__brd__invoice-matching__v2", "version": 2, "file_link": "…",
       "inputs": ["01-requirement-gathering/Requirement Gathering - Acme - Invoice matching.docx"] } ],
     "created_by": "<name>", "created_by_email": "<email, if known>", "failed_writes": [] }
   ```
   Collaterals add one entry per collateral delivered (asset `demo_script`, `deck`, `video`).
4. **Standing decisions** — append to `context-log.md` once per workspace (the AI PM reads them like a pipeline's):
   questions during the stage are answered by the AI PM from context and assumptions, not the person (except, in
   `app`, Zen's planning questions, its plan approval and every `CONFIRM_REQUIRED`, which are the person's); the design
   system runs unattended, settles brand colour by its own source order and uses the UnifyApps logo as a labelled
   stand-in when no client logo exists; builds use UnifyApps Headless in Zen mode on Orbit UAT with a new solution
   `<Client> — <Use case>`, and model IDs follow its recommendation; collaterals use the bundled UnifyApps template;
   POC data policy — made-up seed and document values, so public Orbit links are approved; the person's Slack, Gmail,
   Drive and Calendar are read-only, and the only writes outside the folder are this one-off's Orbit row(s) and, for a
   video, the file copied into the `POC Studio Video Library` shared drive.
5. **AI PM setup** (once per machine; seconds after that): `python3 "$R/lessons.py" init`, and `pip install pyyaml`
   into the shared venv if `python3 -c "import yaml"` fails. `owner_profile` for review requests = `created_by_email`
   in lower case (leave it out if unknown).

## 3 · Run the stage (unattended)

Create the autopilot flag now (absolute path; record it in `state.json` → `standalone.autopilot_flag`), exactly as the
orchestrator's "Questions never go straight to the person" describes: questions go to the AI PM (`ai-pm` agent,
resolve mode), and the hooks enforce it. Then call the stage **exactly as the orchestrator's stage section does —
same arguments, same output path, same rules — with these differences only**, and **skip every Orbit moment those
sections name** (M1–M6, M4a, M4b, Reconcile, the G4 upload): a one-off writes only its own row, in § 5.

- **requirements** — orchestrator § 1: `requirement-gathering` with the client name, the use case and
  `<workspace>/01-requirement-gathering/`. The skill's own last step ("ask whether to proceed") is replaced by § 4–6
  here.
- **research-report** — call `research` with the question(s), the purpose, the topic and the context (the client name,
  files to read first). Save the answer as `research/<topic-slug>-report.md`, then render
  `research/Research - <Client> - <Topic>.docx` from it with the title "Research — <Client> — <Topic>": `pandoc
  "<md>" -o "<docx>" --metadata title="Research — <Client> — <Topic>"`, or python-docx if pandoc is missing. The `.docx`
  is what goes to Orbit.
- **brd** — orchestrator § 2: `scoping-l1-first` with the use case; **input 1** = what was collected (the RG
  document, or the notes, emails and files, saved under `01-requirement-gathering/files/`); **input 2** = every client
  file collected; output `<workspace>/02-scoping/scoping-document.docx` (`_working/` beside it).
- **design** — orchestrator § 3, unchanged and unattended: the BRD collected is "the approved scoping document"; the
  website and any logo file or brand guidelines collected are passed with it; output
  `<workspace>/03-design-system/<slug>-design-system.html`. When the stage is done and before the AI PM review, also
  open the file locally (`open <file>` on a Mac, `xdg-open` on Linux) so the person sees it straight away.
- **app** — orchestrator § 4 as written: `/ua:setup` with a **new** solution `<Client> — <Use case>`;
  `platform-master` pointers; `/ua:plan` in Zen inside the Zen planning window (the person answers Zen's questions and
  approves the plan, which platform-master reviewed first); the parallel build; UnifyApps Headless's own tests; the
  browser fallback for any platform asset it cannot build; the **4b AI PM build walk**; publish. Without a design
  system, leave the build request's design-system item out, tell UnifyApps Headless to use its default look, and give
  the 4b review the BRD alone as upstream. Finish with the app's **preview link** (Preview link rule) in
  `04-build/build-summary.md` and the run state. `CONFIRM_REQUIRED` stays the person's.
- **collaterals** — orchestrator § 5 with: the preview link from § 1 as every persona's `url` and `public_url`; the
  BRD and RG document if collected (else the skill builds its story from the app and says so in the brief); the
  bundled template; the audience if given. **Only the collaterals chosen in § 1 are delivered**, still built from
  one story; when only the video is chosen, the narration script is still written for the video but not delivered.
  The Orbit session from § 1 is copied to the collateral folder's `auth/<persona>.json` for each persona.

Update the run's `status` to `in_review` when the stage's output exists.

## 4 · AI PM review

As the orchestrator's "Calling the reviewer" does: the `ai-pm` agent (`subagent_type` `poc-studio:ai-pm`), a request
YAML in `<workspace>/reviews/<stage>-review-<n>.request.yaml` with `work_id` = the POC ID if given, else
`SA-<client-slug>__<usecase-slug>`; `stage` from the table above; `artifacts` = the asset's output(s); `upstream` = the
input the asset was made from (the RG document for a BRD, the BRD for a design system or app, the BRD and the app for
collaterals; none for requirements and research beyond the question); `owner_profile` as in § 2. Handle the verdict
exactly as the orchestrator's table does: REVISE with a response file (at most 2 REVISE rounds), BLOCK, the round-3
ruling, ASK_HUMAN, research requests. For the app, this is the Stage 4b walk inside § 3.

## 5 · Write to Orbit, then show it in the chat

1. **Write first**, with status `in_review`, so the asset is in POC Build Loop as soon as it exists: load
   `orbit-writeback` (Skill tool: `poc-studio:orbit-writeback`) and follow **"One-off documents"** — the version
   lookup in Orbit, the upload (public URL; for the video, "Video to Google Drive" with the file name
   `SA - <Client> - <Use case> - Demo video v<N>.mp4`), the row, earlier versions `superseded`, the read-back.
   Collaterals: one row per collateral delivered, in one `apply_record_edits` call. Record `document_id`, `version`
   and `file_link` in the run. A failed write never stops the asset (orbit-writeback, Failures).
2. **Remove the autopilot flag**, then show the person, in this order:
   - the local file path(s);
   - the Orbit file link(s) — the public upload URL, the Drive link or the app preview link — which open without the app;
   - the app row(s): `https://poc-build-loop-orbit.tensor-uat.unifyapps.com/assets/<type-slug>`;
   - the AI PM gate summary: `python3 "$R/lessons.py" gate <workspace> <stage>`;
   - any `check_this` assumptions and anything still open.
3. Ask with AskUserQuestion: **Approve** / **Request changes** (they type the changes in "Other").

## 6 · The decision

- **Approve** → orbit-writeback "One-off documents" → The decision: the row's (or rows') `status` → `approved`, read
  back. `python3 "$R/lessons.py" record <workspace> <stage> approved`. Run status `done`. Log it in `context-log.md`.
  Tell the person in one line that the asset is approved, with its Orbit link. The run ends here.
- **Request changes** → log their words verbatim in `context-log.md` (a human decision for every later review),
  `python3 "$R/lessons.py" capture <workspace> <stage> "<their words>"` and `… record <workspace> <stage> changes`.
  Recreate the autopilot flag, re-run the stage skill on its own output with those changes (fix only what they
  asked), review again (§ 4; the round counter restarts), then write the **new version** (§ 5, which makes v(N+1) and
  supersedes the older one) and ask again (§ 5.2–6).

## Never

- Change the full pipeline's state, files or Orbit rows: no Activity, Iteration or POC update, no `slack_notification`.
- Write a matrix link to Orbit or record from one.
- Delete a file or an Orbit row (earlier versions become `superseded`; earlier files go to `_previous/`).
- Type a password, or answer a `CONFIRM_REQUIRED` for the person.
- Start the stage before its required prerequisites are in hand.
