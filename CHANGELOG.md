# Changelog

## 1.38.0
Four stage skills updated together; they are one chain (the BRD feeds the wireframes, the wireframes feed the design system).
- **Scoping v5.** The BRD says what each page must do and what the person must see to decide; it no longer prescribes layout, UI patterns or components (the wireframes decide them). §23 is now a **capability inventory** (same CMP IDs). New required **21.1 Hero object** and **21.2 Reference products**. Tighter seed and copy rules: a tone per status, picture/file/location fields marked, every warning message word for word, every record a persona sees named, one demo day, totals computed by script, no "demo"/"dummy" labels, the brand is the client company. The Integration Spec input (v1.37) is kept.
- **Wireframes v4.11.** Each page gets a brief and a pattern (new `references/patterns.md`); the signature is drawn as itself; the journey ends on a payoff frame; three navigation shells with one chosen (`NAV-options.png`); 2–3 views per hero list (`VIEWS.png`); BRD changes recorded in `brd_overrides`; `check:` lines and a fresh-eyes review. Fixes on top: **older specs render exactly as before, with warnings** (so 4c changes on existing POCs keep working); a crash on `"1:1"` image ratios; Update mode leaves pages outside the change alone; `diff.py` reports app-level changes (navigation, demo day, journey), the NAV and VIEWS sheets, and "metadata only" pages.
- **Design system v12.6.** Creative direction by a separate pass, real product images, a showcase of three screens plus close-ups, flow panels per capability, the journey-to-component table, one way in to the agent, a judgement pass on seven scores, and size budgets checked by script (`check_ds.py`, `scan.py`, `base_css.py`, `register.py`). The wireframes' components are its starting list; it may add what the journey needs, marked Added with a reason. Fixes on top: its contradictions resolved (page height 70,000 px, one variant rule, radii per shape, measured colour counts, research depth), scripts located inside the plugin, the register of earlier apps kept at `~/.local/poc-studio/design-register.json` (seeded on first use), and a visible fallback when an older manifest lacks the new fields.
- **Research v2.** When another skill calls research mid-run, research writes its answer and hands control back to that skill instead of ending the turn. The connector-discovery rule (v1.37) is kept.
- **Plugin:** the AI PM's scoping, wireframes, wireframes-update, design-system and build lenses follow the new skills (overrides with a reason, Added components, three screens, seven scores, one agent entry, only the chosen navigation, views as a switch); the orchestrator's 2b and 3 stages, gate summaries and build request match; platform-master checks the chosen navigation and views; the shared tools install Python Playwright 1.56 (the design system's screenshots), and the doctor checks it.

## 1.37.0
- **New skill: connector-discovery (stage 1c, every POC, between Requirement Gathering and Scoping).**
  - **Part A — the client's own system, only when the use case reads from or writes to one** (Salesforce, ServiceNow, SAP, a database…): asks the person for the client's connection in UnifyApps, validates it, reads the real objects, fields, picklists and rights read-only, finds and tests the connector triggers and actions, designs the automations, and writes the Integration Spec (`01c-integration/`). Scoping copies it into the BRD (§12–§15, §5.4, §5.6, §18, Document Control) with the connection id on every client step; the build uses the same connection, operations and fields (`scope: verify` before `/ua:plan`).
  - **Part B — the AI models, always:** one real test call per chat and embedding model the build uses, with a fallback on another provider, so the BRD names tested models; tested again before the build; and **model recovery** whenever a model runs out of credits or quota: the step stops, models that pass a test are offered, the person chooses, UnifyApps Headless switches, only the failed step re-runs, and the BRD gets a new version with a note (no re-approval).
- Requirement Gathering adds a **Systems** table (read / write / none per client system), which decides whether Part A runs.
- Connection, access and replacement-model questions (`SYSTEM_ACCESS:`) are always the person's, in Zen and Sonic; the hooks let them through. The model test is pre-approved (a fraction of a cent, nothing created).
- The AI PM checks the BRD against the spec at the Scoping gate; platform-master's plan review checks client steps and model cards against it; a credits failure is never a browser-fallback case; research sends client-system questions to connector discovery first.
- Observability logs every connector-discovery run; new lesson L-019 (test models before the build).

## 1.36.1
- **Fix: the "Thank You" slide showed as the second slide.** `kit/deck.py` put the slides in the right order in the deck's list, but left the slide files inside the .pptx with their template names (opening = slide4.xml, Thank You = slide5.xml, content from slide6.xml). Viewers that order slides by file name showed Thank You second, while python-pptx and the AI PM saw it last. The slide files are now renamed in deck order, and `deck.py` re-reads the saved file and stops unless the file names follow the deck order, the opening slide is first and Thank You is last. The AI PM's deck check now looks at the file the same way.

## 1.36.0
- **Observability: every skill run is logged, including every re-run.** Re-runs after an AI PM REVISE or a change request were never logged (the hook only fires when a skill is first loaded), so the view jumped from "changes asked" to "approved". Now:
  - each re-run gets its own row before the review of it (label "<doc> v<N> · <k> fixes" or "· changes", round +1, `triggered_by` iteration for changes); the REVISE step, the gate's change step, 4c and asset-run say so where the re-run happens;
  - `skill_run_row.py` keeps a local ledger (`.poc-studio/skill-runs/`) and refuses (exit 3) a review row whose run is not logged, or that comes after a REVISE or change request whose re-run has no row; `note-change` / `change-dropped` record change requests;
  - the hook names any re-run with no row and any rows not yet saved when an AI PM review returns;
  - tokens are never empty: estimated from `files_read` / `files_written` when not measured;
  - outbox: a row that did not save stays pending and is sent again before every moment, at every gate and at the end (`pending`, `saved`); nothing is dropped after one retry any more;
  - check against Orbit at every gate approval, on resume and at the end (`reconcile`), and an end-of-run line from `report`: "Observability: <n> runs logged, all saved in Orbit."

## 1.35.0
- **Deck: UnifyApps opening and closing slides.** The bundled template now holds the UnifyApps cover ("Agentic automation for the enterprise") and the "Thank You" slide as template slides 4 and 5 (slides 1–3 unchanged, so existing `deck.json` files still work). `kit/deck.py` adds them first and last, exactly as they are; `"open": false` / `"close": false` leaves one out.
- **Deck: technical blueprint.** New `kit/blueprint.mjs` renders, from `blueprint.json`, an architecture slide (what it is, counts, and a four-layer diagram: users → front doors → automations and agents → data and connected systems, with live / simulated / go-live status) and a "what was built" list of every automation and AI agent (when it runs, what it does, objects and tools) on as many slides as it needs. Built from `04-build/build-summary.md`, never the plan; the script fails when the diagram and the list disagree. Big builds collapse the diagram's groups to "+N more" and keep every item in the list.
- AI PM collaterals lens checks the opening/closing slides and that the blueprint lists exactly what was built.
- **Vague change requests are clarified before rework.** Every change request (any gate, any stage, Zen and Sonic, full runs and one-off assets, and 4c after the build) first goes to the AI PM's new `change-clarity` check. Clear → it states its reading in one line and the change is limited to it. Vague (a new artifact with no word on which parts to take, a clash with an approved document, an open-ended ask, two readings where one would redo approved work) → 1–3 clarification questions go to the person, in Sonic too, before anything is reworked. A replacement artifact (for example a new design system after the build) is never adopted in full unless the person chooses that; work beyond the reading is a blocking finding in the next review. Hooks and README updated.
- **platform-master: knowledge sources from workflows** (tested on UAT): a workflow can add FILE or WEBSITE sources to an agent's knowledge set by creating a record on the system object `knowledge` and reading its indexing status (new pointer, plan-review check and api-spec entry).
- **platform-master job 1b · Question review**: each Zen planning question passes through platform-master first; it may add its own option ("Platform-master: …"), mark one of Zen's as agreed, or add nothing. Wired into the Zen planning window (Zen and Sonic); the plan review checks that a chosen platform-master route reaches the spec and tasks.

## 1.34.0
- **Changes after the build are triaged first; big ones go back to the wireframes before the app.** A change asked at the verify gate (or later) went straight to UnifyApps Headless, which could re-plan and rebuild the whole app. New orchestrator step **4c · Changes after the build**: the AI PM triages every change (`change-triage` lens) as **small** (direct `ua-change` fix, as before), **big** (wireframes first, then targeted fixes on the affected pages only) or **very big** (wireframes first, then a re-plan limited to the affected pages on the existing solution). The whole app is never re-planned for a change request.
- **Wireframes Update mode**: edits only the affected frames, keeps the approved version in `02b-wireframes/_previous/v<N>/`, and writes a before/after change sheet with the new `wireframes/scripts/diff.py` (`changes/CR-<n>/change-sheet.pdf`, `change-summary.json`: pages added/changed/removed, component delta, app-level changes). The AI PM reviews it with the new `wireframes-update` lens (only the triaged pages may change).
- **You approve the updated wireframes**, in Zen and in Sonic (Approve and update the app / Change the wireframes / Drop this change). Hooks and the AI PM let this through in Sonic.
- The design system is not updated for a change; new components are styled from its kit and tokens.
- Orbit: the approved wireframes become a new wireframes version (`from_iteration`, change sheet uploaded); the iteration stays open until the new app version's M5. A dropped change closes the iteration.
- One-off `/poc-studio:app` change requests use the same triage (wireframes first when the folder has approved wireframes).

## 1.33.0
- **Feedback tickets: full shape incl. ticket_key; status list updated.** Tickets filed by v1.27 and earlier had no `ticket_key`, `priority` or `updated_at` (and no `created` activity row), so POC Build Loop could not change their status or owner. Every ticket is now built by `orbit-writeback/scripts/feedback_ticket.py`: `ticket_key` = `ticket_no` = `FB-<ms>`, status `to_be_assigned`, priority `none`, `updated_at` = `created_at`, `poc` and `client_name` only for a POC; no `source`, `poc_stage` or other old fields. The `created` row in `orbit_studio_feedback_event` uses the same ms. A clash retries with now+1 (up to 3 times) for both keys.
- Status list now includes `research` (To be Assigned, Research, In-Progress, Blocked, In QA, QA Rejected, Done).
- Every write's reply is checked (`feedback_ticket.py check`): "Logged" is said only when every item is `"ok": true`; otherwise the platform's error is shown.
- **`/poc-studio:feedback` now checks for a newer POC Studio first**, as `/poc-studio:start` does, and stops until the person updates. Everyone on an older version must update.
- `feedback_ticket.py --self-test`: a dry run that builds sample tickets with and without a POC and checks the shape; nothing is sent.

## 1.32.1
- **Observability rows are built by a script, checked against the live `orbit_studio_skill_run` schema** (40 fields; `run_id`, `skill`, `started_at` required; schema validation on). `orbit-writeback/scripts/skill_run_row.py` turns loose values into the stored types and codes ("104k" → 104000, "v1" → 1, "REVISE" → `revise`, seconds → ms, `brd` → `scoping-l1-first`), drops empty values and unknown keys, never sends `poc` on a one-off row, and refuses a row it cannot make valid; the session sends its output as is.
- **New hook `skill-run-log.sh`** (PreToolUse and PostToolUse on Skill and Agent): while a run's `.poc-studio/observability` flag exists, it saves each logged skill's start time and reminds the session to write the row when the skill returns (an AI PM review, right when it returns). Notify only; never blocks.
- A refused row is retried once with only the failing part changed (new `run_id`, no `poc`, or without the named field), then noted in one line.

## 1.32.0
- **Observability log.** New orbit-writeback **Moment 7 — a skill finished**: right after each skill run returns, one create-only row in `orbit_studio_skill_run` for POC Build Loop's Observability view, in full runs and in every one-off command. Logged: each stage skill run and re-run, each AI PM review round (with `reviews_run_id`, `verdict`, `round`), each platform-master job, the Stage 4 build by UnifyApps Headless, each research call, and one `poc-orchestrator` "POC started" row per session. Not logged: orbit-writeback's own moments and the AI PM's resolve answers.
- Rows carry `run_group` (one per session) and `sequence` (continuing from the POC's highest), inputs, 3–6 lines of reasoning, the output summary and decisions, documents, timing, the plugin version, the model, and tokens (measured for AI PM subagents, estimated as characters ÷ 4 elsewhere). One-off rows are `origin: one_off` with no `poc`.
- Written with the same `apply_record_edits` tool as every other moment. A failed write is retried once, then noted in one line; it never blocks or slows a build. Gate `gate_decided` Activity rows are unchanged.

## 1.31.0
- **Run modes: Sonic or Zen**, asked once at the start of every run (`/poc-studio:start` and each one-asset command) and kept in `state.json` → `mode` (a run without one is Zen). **Zen** is the loop as before. **Sonic**: the AI PM's final verdict is each gate (PASS, or the third review's rulings with nothing blocking), so the run moves to the next stage by itself; in Stage 4 the AI PM answers Zen planning's questions and approves its plan after platform-master's review and the builder check.
- Still asked of the person in Sonic: sign-ins, every `CONFIRM_REQUIRED`, the AI PM's ASK_HUMAN items (credentials, real data, spend, sending or publishing outside Orbit UAT), a BLOCK after the third review, a Not ready requirements verdict, rebuilding pages already built, and a missing tool or connector.
- Hooks read a new `.poc-studio/sonic` flag and route approval gates to the AI PM too. Orbit: Sonic approvals are written with `actor_type: ai` ("Approved by the AI PM (Sonic mode)") and no `slack_notification`. `lessons.py record … auto` logs Sonic approvals apart from human first-try approvals. One-off runs in Sonic approve the asset without asking and do not chain.

## 1.30.0
- **Exact builder terms, so a POC app is never built as a no-code config app.** A build said "text-to-code" in its prose while Zen's task graph used no-code task kinds, so every page went to `app-agent` (`application-builder`). The plugin now names what actually decides the builder: the app, its pages and its publish use task kinds `code-app` / `code-publish`, owned by `code-app-agent` (`code-builder` tools); never `app`, `page-layout`, `page-bind`, `publish` or `app-agent`.
- **Orchestrator:** a Builder terms table; the build request carries those exact words; a builder check reads the task graph before the plan is shown and again before the first task starts; a no-code page task found during the run stops new page tasks and asks the person whether to rebuild. `app-agent` is removed from the builder list.
- **platform-master:** the plan review checks task kinds and owners first, every round; a no-code app task is never left as a "Check this" line.
- **AI PM:** standing answer names the task kinds; rebuilding pages already built the no-code way is the person's decision (ASK_HUMAN).
- **Scoping:** the app is always a text-to-code app (Code Builder); scoping no longer offers "no-code" for the app or a page.

## 1.29.0
- **Feedback ticket statuses follow POC Build Loop's six values:** new tickets are created as `to_be_assigned` (To be Assigned); `open` and the other old values are never sent (the platform now rejects them). `status FB-<n>` shows the new labels: To be Assigned, In-Progress, Blocked, In QA, QA Rejected, Done.
- **Attachments:** screenshots, logs, PDFs or paths given with `/poc-studio:feedback` (up to 10, 20 MB each) are uploaded with `orbit agent-builder upload_file` from the Orbit folder and appended to the feedback text as one line each (`![name](link)` for images, `[name](link)` for other files), which the app shows as thumbnails and chips. A failed upload still files the ticket and names the file.
- New reply: `Logged FB-<epoch> (To be Assigned) → <link>` (plus ` · attached N files`). A key clash retries with `now + 1`, up to 3 times.

## 1.28.1
- Feedback ticket IDs are timestamps again: `FB-<Date.now()>` (the same value as `created_at`, e.g. `FB-1793634938058`). No `ticket_seq`, no read of the last ticket to number it; a duplicate-key error retries with a new timestamp, at most 3 times. Everything else from 1.28.0 (tickets, optional POC, `created` activity row, link reply, `status`) is unchanged.

## 1.28.0
- **Feedback becomes tickets.** `/poc-studio:feedback <text>` files a ticket on POC Build Loop's Feedback page (https://poc-build-loop-orbit.tensor-uat.unifyapps.com/feedback) with a sequential ID `FB-<n>` (next number read from Orbit; a clash retries with the next number, at most 3 times), `status: open`, `priority: none` unless stated, and one `created` row on the new `orbit_studio_feedback_event` object. The reply gives the ticket ID and its link. Assignee, priority, status, due date and tags are set in the app; the plugin never updates or deletes a ticket.
- **A POC is optional.** Feedback from a one-off asset workspace is filed without a POC (and without asking); otherwise the person can pick **No POC (general)**. The old "feedback can only be filed against a POC" rule is gone.
- **`/poc-studio:feedback status FB-<n>`** (or `fb <n>`, `<n>`) reads a ticket's status, priority, assignee and latest activity from Orbit.
- Feedback no longer feeds the skill analysis (no `analysis_status`): skill proposals come from iterations only. Iterations (Moment 3) are unchanged.
- Skill keys: `asset-run` added, `research` removed.

## 1.27.0
- **One OK to the next asset.** A one-off asset's approval question now also offers **Approve and make <next asset>** (Requirements → BRD → Wireframes → Design system → App → Collaterals). It approves the asset and starts the next one-off at once, with the asset just approved as its input (no re-upload, no "use it?" offer); only what is still missing is asked. The question repeats at each approval, so a person can go asset by asset with one OK each, or stop with Approve.
- The chain stays one-off: each asset is its own Assets row (versioned as before) and never starts, joins or moves a POC run; the full loop is only `/poc-studio:start`.

## 1.26.0
- **New stage 2b · Wireframes** in the Plan phase, between the BRD and the design system (skill `wireframes`). From the approved scoping document it writes a short JSON layout spec; a bundled script (`render.py`, Pillow only, no browser, fonts included) draws one low-fidelity grey frame per page at the persona's width, a PDF of all frames, and `wireframe-manifest.json`: every component with its pages, CMP IDs, variants and states. Generic regions are **slots** that only name their component; the page's defining parts are drawn in detail with the BRD's real copy. `coverage.py` checks every §11 page and §23 CMP ID against the BRD. It has its own approval step inside G2 (Orbit: a `wireframes` document under Plan, M1w/M2w; no new gate).
- **Map component reference** (`wireframes/references/map-component.md`), taken from a working build: one shared map, four modes (rings, dots, arcs, radius), full-bleed with floating panels, whole-step fits padded for panels, screen-space health rings, collision-free labels, hover-to-card. Wireframes draw map pages with it, the design system styles it, platform-master adds a `Map:` pointer and checks Zen's plan against it, and the AI PM checks it at 4b. Scoping now gives location records latitude/longitude and seeds real coordinates.
- **Design system (v10.1):** with approved wireframes, the manifest is the component inventory (variants still capped at three per family), the frames are the layouts in `#build-plan`, the five screens are frames at high fidelity, nothing is proposed; the baseline (sign-in, statuses, empty/error/loading/no-access, toast, confirm, input states, both themes) is always built. Without wireframes it works as before.
- **Build:** the frames and manifest go in the build request; platform-master flags a page whose layout differs from its frame.
- **AI PM:** new `wireframes` lens and lesson stage; the design-system and 4b reviews check against the frames.
- **One asset:** `/poc-studio:wireframes <Client> | <Use case>`; `/poc-studio:design` takes approved wireframes when the folder has them.
- Runs started before 1.26 resume without wireframes when their design system has already started.

## 1.25.1
- Removed `/poc-studio:research-report`. Research is not a stage of the POC journey, so it is no longer made as a one-off asset: the command, its `asset-run` row and section, the one-off Orbit `research` document type and its README rows are gone. The one-asset commands are now `requirements`, `brd`, `design`, `app` and `collaterals`. The `research` skill stays: the stages and the AI PM still call it for outside facts. The full pipeline (`/poc-studio:start`) is unchanged.

## 1.25.0
- **Make one asset**: six new commands — `/poc-studio:requirements`, `research-report`, `brd`, `design`, `app`, `collaterals` — each makes one asset without a POC and without the other stages. Prerequisites are collected in the chat first (arguments → an existing client folder → one question); then the existing stage skill runs unattended, the AI PM reviews it, and the new `asset-run` skill writes it to Orbit as a one-off document (`origin: standalone`, shown in POC Build Loop under Assets), versioned from Orbit on every re-run or change, and asks for approval. Collaterals always ask which to make (demo script, deck, video — any of them). A one-off run never changes a pipeline run's files, state or Orbit rows.
- orbit-writeback: "One-off documents" section and a shared Preview link rule; pipeline Document rows now also send `origin: pipeline`, `client_name` and `use_case`, and app documents save the preview link (never the matrix URL). `/poc-studio:feedback` in a one-off workspace asks for a POC ID or writes nothing.
- `scripts/release.sh` bumps the version in every command file.

## 1.24.0
- The reviewer becomes the **AI PM** (`ai-pm` skill and agent, renamed from `general-reviewer` / `poc-reviewer` everywhere), v1.0: re-runs every stage's own checks instead of trusting them; stage lenses and a slop catalogue; a fixed/disputed/deferred response protocol where the third review is a ruling, not a question; a gate summary with rulings first; a lesson bank across POCs (`lessons.py`, ~/.local/poc-studio/lessons) seeded with 18 lessons, with owner profiles created at runtime (keyed by the owner's email; none shipped); `scope_metrics.py` for scoping. New **Stage 4b**: after UnifyApps Headless's own testing and before publish, the AI PM walks the app from its preview link (`build_walk.mjs`); fixes go back as direct `ua-change` changes in parallel, platform assets through platform-master's fallback. One Orbit sign-in at Setup (`orbit_signin.mjs`) serves the build walk and the video recording. Scoping, design-system and collaterals answer the AI PM's findings. Merged onto the current pipeline (Zen, parallel agents, shared drive, platform-master); no names in skills.

## 1.23.0
- New skill `platform-master`, the UnifyApps platform expert for Stage 4, built from the platform knowledge of the UnifyApps helper (curated: no process, design or conflicting rules). Before `/ua:plan` it classifies the use case and adds best-practice pointers to the build request; in the Zen planning window it reviews and corrects Zen's plan (up to two rounds) before the person sees it, so the person approves an already-corrected plan; when UnifyApps Headless cannot build a platform asset, it builds it over the API from the person's signed-in browser tab on Orbit UAT and hands it back through `ua-change`. Orchestrator, reviewer standing answers, Orbit (M4b) and README updated.

## 1.22.0
- Demo video: saved to the company shared drive `POC Studio Video Library` (open to everyone through `allemployees@unifyapps.com`), in its root as `<POC ID> - <Client> - Demo video v<N>.mp4`, so nobody creates or shares a folder of their own. The Drive connector finds it with `parentId` = the drive id (its plain title search does not return shared-drive files). Video route check and upload updated; the person's own `POC Studio` folder stays as the fallback route, then a manual drop.

## 1.21.0
- Build: Zen plan with the user answering clarification questions and approving the plan; builder and test agents run in parallel; CONFIRM_REQUIRED always goes to the person; hooks let Zen-planning questions through.

## 1.20.0
- Renamed Nebula to UnifyApps Headless: /ua:setup, mcp__plugin_ua_* tools, new plugin cache path; build stage runs ua:setup then ua:plan (Sonic).
- Removed people's names from the skills: the owner column in the orchestrator's skill table, and the General Reviewer's owner (now UnifyApps Solutions).

## 1.19.0
- Requirement Gathering: a short summary under the title (use case, score and verdict, top 3 questions); a use-case type line; the problem stated before any solution; a "What this POC adds" table when earlier work exists; the current process as numbered steps; Visual requirements captured word for word and tagged for the design system; every figure cited to its primary source; a PM's written record of a client call counts as a client source; questions marked Blocking or Nice to have, with region-specific and AI-grounding questions; answered questions move into Section 1 and the score is re-run; internal working notes only in Section 4.
- Scoping: two or three app personas (notification recipients are not personas); L1 checked against the storyline and covering every journey stage; leaner POV sizing (3–6 pages, never more than 8; 8–12 objects; 3–8 workflows; one live copilot agent), reached by merging, with secondary records in drawers or modals; the executive summary opens with the business problem; success criteria measure business outcomes, with honest baselines; differentiators name the products that cover part of the ground; record key generation stated; workflow paths checked for overwrites, edge states and required fields; scoring ownership and weights for rules that do not apply; a live demo core with seed data matching each step (10–15 minutes); real product images, downloaded into the app's storage; Visual requirements from Requirement Gathering carried into the design-system hand-off (§21); Reset demo restores seed records only and never removes records the person made; four new consistency checks; the Pentland sizing lesson.
- Orchestrator (build): a new solution named `<Client> — <Use case>` for every POC, never a cached one; Nebula's text-to-code builder only; forms submitted twice to catch duplicate keys, with test records cleared after testing; agent follow-up questions tested; ratios shown as percentages; records the person creates while verifying are kept.
- Reviewer: standing answers for Nebula's cached-solution and builder questions (new solution, text-to-code), so the reviewer never picks a cached solution because Nebula recommends it.

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
