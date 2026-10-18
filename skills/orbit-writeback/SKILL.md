---
name: orbit-writeback
description: Keeps Orbit · POC Studio (orbit.uat.unifyapps.com) in step with a POC Studio run, records POC-level feedback (/poc-studio:feedback), or runs one write-back moment by hand when the person asks to test it — uploads each gate's files and writes Document, Activity, Iteration and POC rows at the six write-back moments (gate posted, gate approved, changes asked, stage moved, new version ready, blocked). Called by the poc-orchestrator before and after every gate; also verifies the POC ID at start.
---

# Orbit write-back (POC Studio)

You keep **Orbit · POC Studio** on the `orbit.uat.unifyapps.com` tenant in step with the run. Orbit is read by the POC
owner, their team and a Slack bot. The orchestrator calls this skill at the moments listed in **The plugin's gates →
Orbit moments**; you write exactly what that moment says and nothing else.

The owner's original specification is in `orbit-spec.md` beside this file; read it once per run. **This SKILL.md is
authoritative where the two differ** (the differences are the owner's decisions, listed under "Decisions").

**POC data policy (owner decision):** POC Studio builds proofs of concept with dummy data. The app's seed data,
the documents and the collaterals use made-up values, never real customer records, so public Orbit links are
approved for every document, including the client files found during discovery. Do not warn about or ask again
about public uploads.

## Setup (once per run, before Stage 1)

### 1. Nebula's tenant tools (no separate folder)
All Orbit reads, writes and uploads go through **Nebula's tenant tools, called directly as tools in this session**
(the same tools Nebula uses while it builds), always with the host `orbit.uat.unifyapps.com`. There is no Orbit
folder and no command-line script.

Load them with **one** ToolSearch at the start of every write moment (they are deferred tools), by exact name first:

`select:mcp__plugin_nebula_object__get_records,mcp__plugin_nebula_object__apply_record_edits,mcp__plugin_nebula_application-builder__upload_public_file`

If a name is not found, search for it (`+nebula get_records`, `+nebula apply_record_edits`,
`+nebula upload_public_file`) and use the tool that comes back under that name.
- **Nebula's tools are not in the session at all** → Nebula is not installed or not set up in this folder: ask the
  person to run `/nebula:setup` here (tenant `orbit.uat.unifyapps.com`), then load them again.
- **No record-write tool (`apply_record_edits`) can be found** → say in one line that Orbit write-back is not available
  in this session (reads and uploads may still work), record it in `failed_writes`, and carry on with the run.

### 2. Verify the POC ID and read the owner
The POC ID is mandatory (the start command will not run without it). Verify it exists with the **`get_records`** tool:

```json
{ "host": "https://orbit.uat.unifyapps.com", "objectId": "orbit_studio_poc",
  "filters": [{ "field": "poc_id", "op": "EQUAL", "values": ["<POC ID>"] }], "limit": 1 }
```

- No record → stop; tell the person "POC ID `<POC ID>` was not found in Orbit (`orbit_studio_poc`). Please check the
  POC ID and send the correct one." Wait, then check again with the new ID. Nothing starts until it is found.
- Record found → keep its record id (the POC row's `recordId` for every POC update) and read the **POC owner's name
  and email** from it (the owner fields of the record, e.g. a field named like `owner_name` / `owner_email` or
  `poc_owner…`; use the record's own field names). Save in the run state. **The owner's name and email are used in
  every name and email field you write** (`created_by`, `actor_name`, `actor_email`), for AI and person actions
  alike; `actor_type` still says `ai` or `person`. If the record has no owner name or email, ask the person once.

### 3. Run state you keep
In the workspace `state.json`, under `orbit`:

```yaml
orbit:
  poc_id: POC-acme-20261018
  poc_record_id: <record id>
  owner: { name: <owner name>, email: <owner email> }
  documents:            # every document you wrote, by gate
    g1: [{ document_id: …, type: requirements, version: 1, status: in_review, file_link: … }]
  open_iterations:      # iteration rows waiting for a new version
    - { iteration_id: …, gate: g2, document_id: … }
  failed_writes: []     # anything that did not reach Orbit after 3 tries
```

## How to write

### Create or update rows — the `apply_record_edits` tool
Call the tool with:

```json
{ "host": "https://orbit.uat.unifyapps.com", "objectId": "<object id>",
  "edits": [
    { "op": "create", "properties": { … } },
    { "op": "update", "recordId": "<record id>", "properties": { … only the keys that change … } } ] }
```

- One call per object; all rows of that object in one `edits` list.
- `update` merges into the stored row: send only the keys you change. Never send a row back whole.
- Never send `""` or `null`: leave the key out.
- Dates are epoch milliseconds (`Date.now()` / `int(time.time()*1000)`); get them with a one-line script, not by guessing.
- Build long values (summaries) with a script when they come from a file; never retype a file's contents by hand.
- Check the reply: every item in `results` must say `"ok": true`.

### Upload a file — the `upload_public_file` tool
Call it with:

```json
{ "host": "orbit.uat.unifyapps.com", "filePath": "<absolute path of the file>", "fileName": "<display name>",
  "mimeType": "<mime>" }
```

- The reply gives the file's **public URL**: save it as the document's `file_link` (and in the run state). Public
  links are owner-approved: anyone with the link can open the file, and Orbit's Slack thread can show it.
- `fileName` is the name readers see, e.g. `Acme - BRD v1.docx`, whatever the file is called on disk.
- At most **20 MB** per upload.
- **The demo video always goes to Google Drive, whatever its size**, never through `upload_public_file` and never
  compressed. It goes by the route in **Video to Google Drive** below (copied into the person's Drive for desktop
  folder, found and linked with the Drive connector). This is the only way the video is stored.
- Client files with no type below (or Google-native Docs/Sheets/Slides, mail and calendar items): save the
  source's own link (Slack permalink, Drive link, Gmail or Calendar link) with `file_kind link` instead of uploading.
- MIME: txt `text/plain` · md `text/markdown` · csv `text/csv` · eml `message/rfc822` · json `application/json` ·
  docx `application/vnd.openxmlformats-officedocument.wordprocessingml.document` · pptx
  `application/vnd.openxmlformats-officedocument.presentationml.presentation` · html `text/html` · pdf
  `application/pdf` · mp4 `video/mp4` · xlsx `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` ·
  png `image/png` · jpg `image/jpeg`.

### Ids you make

| Row | Id |
|---|---|
| Document | `<poc_id>__<stage>__<slug>__v<N>` e.g. `POC-acme-20261018__3_scope__brd__v2` |
| Activity | `ACT-<Date.now()>-<4 random digits>` |
| Iteration | `IT-<poc_id>-<Date.now()>` |

`slug` is the document type (`requirements`, `brd`, `design-system`, `app`, `demo-script`, `deck`, `video`) or, for a
discovered input, `<source>-<short name>` (`slack-…`, `drive-…`, `gmail-…`, `calendar-…`).

## The rows

**Document** — object `orbit_studio_document` (create; afterwards update only `status`)

```json
{ "document_id": "<id>", "poc": "<poc_id>", "name": "BRD", "type": "brd", "stage": "3_scope", "gate_pack": "g2",
  "version": 1, "status": "in_review", "doc_role": "artifact",
  "file_link": "https://orbit.uat.unifyapps.com/api/file/download/…", "file_kind": "docx",
  "file_name": "Acme - BRD v1.docx", "summary": "One or two lines on what the document holds.",
  "created_by": "<POC owner name>", "saved_at": 1792280000000 }
```

- `type`: slack · requirements · brd · design_system · app · demo_script · deck · video
- `status`: in_review (its gate is waiting) · approved (gate passed) · final (inputs and Deliver files) · superseded
- `doc_role`: artifact (the run made it) · input (found in discovery)
- `file_kind`: docx · pptx · html · pdf · video · image · link · other
- No `content` and no `format` on any document: every document, the design system included, is a file uploaded with
  `upload_public_file` and given by `file_link` + `file_kind` (the app renders it from the link). The design system is
  its `.html` file uploaded with mimeType `text/html`, `file_kind html`. It is one self-contained file with fonts and
  images embedded, so check its size first: if it is over 20 MB, re-compress the embedded raster images (e.g. to
  WebP/JPEG at lower quality) in a copy and upload that; if it still does not fit, upload nothing, say so in the
  document's `summary`, and raise it at the G2 gate (do not stop to ask during the write).
- A re-iterated version also sends `"from_iteration": "<iteration_id>"`.

**Activity** — object `orbit_studio_activity` (create only)

```json
{ "activity_id": "ACT-…", "poc": "<poc_id>", "type": "document_saved", "stage": "3_scope", "gate": "g2",
  "actor_type": "ai", "actor_name": "<POC owner name>", "actor_email": "<POC owner email>",
  "message": "BRD v1 saved", "related_document": "<document_id>", "created_at": 1792280000000 }
```

`type`: input_added · document_saved · gate_posted · gate_decided (with `decision`: approve · request_changes) ·
iteration_logged · stage_completed. `actor_type`: `ai` for what the run does, `person` for the owner's own decisions.

**Iteration** — object `orbit_studio_iteration` (create; then update to close)

```json
{ "iteration_id": "IT-…", "poc": "<poc_id>", "phase": "plan", "source": "person", "status": "open",
  "actor_name": "<POC owner name>", "actor_email": "<POC owner email>", "title": "BRD: add the approval matrix",
  "reason": "<the person's own words, exactly as they typed them>", "related_document": "<document_id they rejected>",
  "skill": "<the POC Studio skill that made the document>", "created_at": 1792280000000 }
```

`phase`: understand (G1) · plan (G2) · build (G3) · deliver (G4).

**POC** — object `orbit_studio_poc` (update only, `recordId` = the POC record's id from the check in Setup)
Every POC update also sends `last_activity` (one plain line people read) and `last_activity_at`.
`slack_notification: true` is sent **only in the last call of a gate push** (moments 1 and 5 — the moments a file is
written or a new version posted). It makes Orbit post to the POC's Slack thread; Orbit clears it itself.

## Reconcile check (on every resume, and before M1 · G4)

Before anything else when a run resumes, and again right before writing G4, compare Orbit with the run state:
1. Read the POC row and this POC's documents (`get_records`, filter `poc` = the POC ID, limit 100).
2. For every gate the run state shows **approved** but Orbit does not (`gN_status` not `approved` or
   `gN_owner_approved` not true): write the missing approval **only** — that gate's `in_review` documents →
   `approved`, an Activity `gate_decided` approve (actor_type person, the owner, message "Approval recorded late"),
   and on the POC row only `gN_status approved`, `gN_owner_approved true` and `last_activity`. **Never move `stage`,
   `current_gate` or `status` backwards**, and send no `slack_notification`.
3. For every document version in the run state that Orbit lacks (e.g. an app version): create it as in M5 (or as the
   approved app version above).
4. Retry everything in `failed_writes`.
5. Say in one line what was written (or "Orbit is in step").
Do not write G4 until G1–G3 show approved in Orbit.

## Video to Google Drive

The Drive connector cannot take a large file (it only accepts file bytes inside the tool call) and cannot set
company-wide link sharing (it shares with an email, a group or a Chat space only). So the video goes through
**Google Drive for desktop** on the person's computer: Claude Code copies the file into the local Drive folder, the
Drive app uploads it in the background, and the connector finds it and gives its link. Sharing to everyone in the
company comes from the `POC Studio` folder, which is set once to "anyone at <company> with the link", and every file
inside inherits it.

### Video route check (in Setup, while the person is at the screen)

Run it once per run in the orchestrator's Setup, and again before the video upload if it did not pass. It never
blocks the run: if it fails, flag it and carry on.

1. **Drive connector**: its tools are in the session (Setup already requires this).
2. **Drive for desktop**: find the local folder and whether the app is running, with Bash:
   ```bash
   python3 - <<'PY'
   import glob, json, os, subprocess, sys
   h = os.path.expanduser("~"); roots = []
   for acct in glob.glob(f"{h}/Library/CloudStorage/GoogleDrive-*"):          # macOS (stream or mirror)
       email = os.path.basename(acct)[len("GoogleDrive-"):]
       subs = [d for d in glob.glob(f"{acct}/*") if os.path.isdir(d) and not os.path.basename(d).startswith(("Shared", "."))]
       for d in subs: roots.append({"email": email, "root": d})
   for d in [f"{h}/My Drive", f"{h}/Google Drive/My Drive"] + [f"{c}:/My Drive" for c in "DEFGHIJKLMNOPQRSTUVWXYZ"]:
       if os.path.isdir(d): roots.append({"email": None, "root": d})        # mirror mode / Windows drive letter
   if sys.platform == "win32":
       running = "GoogleDriveFS.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout
   else:
       running = subprocess.run(["pgrep", "-if", "Google Drive"], capture_output=True).returncode == 0
   print(json.dumps({"running": running, "roots": roots}))
   PY
   ```
   With several roots, try first the one whose email is on the POC owner's domain (e.g. `@unifyapps.com`).
3. **Same account and sync working (the real test):** write a small file
   `<root>/POC Studio/_poc-studio-sync-check.txt` containing the POC ID and a fresh random token (`mkdir -p` the
   folder; the same file is overwritten each run and never deleted). Then, with the connector, search
   `title = '_poc-studio-sync-check.txt'` every 15 s for up to 3 minutes and read it (`read_file_content`): it passes
   when the token matches. Seeing the token through the connector proves the connector and Drive for desktop use the
   same Google account and that sync works.
   The first write may bring up Claude Code's permission prompt (the folder is outside the workspace) and macOS's
   "access files on Google Drive" prompt: the person approves both once.
4. **Company-wide sharing:** find the `POC Studio` folder with the connector (`title = 'POC Studio'`, folder mime type,
   `owner = 'me'`) and read its permissions (`get_file_permissions`). It passes when there is a `domain` permission
   for the owner's email domain with role `reader` or higher. If it is missing, ask the person once to set it
   themselves (give the folder link): **Share → General access → "<company>" (anyone in the organisation with the
   link) → Viewer → Done**, then read the permissions again. Claude never changes this setting itself.
5. Save the result in `state.json` → `video_route`:
   `{ "ok": true|false, "root": "<local folder>", "account": "<email>", "company_share": true|false,
   "folder_id": "<POC Studio folder id>", "reason": "<why not, if not ok>", "checked_at": "<ISO time>" }`, and one line
   in `context-log.md`.
6. Tell the person in one line:
   - all passed → "The demo video will go to Google Drive automatically (`<account>`), shared with everyone at
     `<company>`."
   - anything failed → "**The demo video will not ship to Drive automatically:** `<reason>`. Fix: `<fix>`. Otherwise
     you will be asked to drop it into the Drive folder at the end." Say it can be re-checked any time, re-check when
     they say it is fixed, and carry on either way.

| What failed | `reason` | `fix` |
|---|---|---|
| No local Drive folder | Google Drive for desktop is not installed or not signed in | Install it and sign in with your company Google account |
| Folder found, app not running | Google Drive for desktop is not running | Open Google Drive (it stays in the menu bar) |
| Could not write the folder | Claude Code or macOS did not allow access to the Drive folder | Approve the access prompts, then re-check |
| Token not seen in 3 minutes | Drive for desktop is signed in as `<email from the folder name>` but the Drive connector cannot see its files (a different Google account), or sync is paused/offline | Sign both in to the same company account (connector: claude.ai → Settings → Connectors → Google Drive), check Drive is online and not paused |
| No domain permission | The `POC Studio` folder is not shared with the company, so the video would be visible only to people it is shared with | Set the folder's General access as in step 4 |

### Uploading the video (M1 · G4)

1. If `video_route.ok` is not true, run the check again first.
2. Copy (never move) the final `.mp4` to `<root>/POC Studio/<POC ID> - <Client>/<Client> - Demo video v<N>.mp4`
   (`mkdir -p`, then `cp`).
3. With the connector, search `title = '<Client> - Demo video v<N>.mp4'` every 30 s for up to 15 minutes (large
   files take a while to upload). Take the newest match in that folder.
4. Read its permissions: a `domain` permission (inherited from `POC Studio`) means everyone in the company can open
   it. If it is missing, share it with the POC owner's email as `reader` and say at the gate that it is not shared
   company-wide and why.
5. Get its link (`get_file_metadata` → `webViewLink`, else `https://drive.google.com/file/d/<id>/view`) and use it as
   the video document's `file_link`, with `file_kind video`, and "Video on Google Drive" in its `summary`.
6. **Fallback** (the route failed, or the file did not appear in 15 minutes): ask the person once to drop the file
   into that Drive folder (give the local path of the video and the folder), wait until they say it is done, then do
   steps 3–5. Say which reason made it fall back.

## Order inside every moment
**upload files → Documents → Iteration → Activity → POC last.**

**Before every moment:**
1. **Retry `failed_writes` first.** If they all save now, send any `slack_notification` that was held back for their
   gate with this moment's POC update (only if this moment is itself M1 or M5; otherwise send a POC update with
   `slack_notification true` for that gate on its own).
2. **Never create twice.** Before any create in M1/M5, check `state.orbit.documents` (and, if the state is unsure,
   `get_records` on `orbit_studio_document` filtered on `document_id`). A row that already exists is not created
   again, and if every document of the gate already exists and its gate was already posted, skip the creates **and**
   the `slack_notification`: just re-gate in Claude. This covers resumes and retries after a timeout.

## The plugin's gates → Orbit moments

| When (in the run) | Orbit write |
|---|---|
| Requirement Gathering done + reviewed, before its Claude gate | **M1 · G1** |
| RG approved in Claude | **M2 · G1** |
| Scoping document done + reviewed, before its Claude gate | **M1a · G2 (BRD)** — see below |
| Scoping approved in Claude | **M2a · G2 (BRD)** — see below |
| Design System done + reviewed, before its Claude gate | **M1b · G2 (Design system)** |
| Design System approved in Claude | **M2 · G2** (full) |
| Nebula build published, before the verify gate | **M1 · G3** |
| App verified/approved in Claude | **M2 · G3** |
| Collaterals done + reviewed, approved in Claude | **M1 · G4** (Deliver complete) |
| Changes asked at any Claude gate | **M3** (phase of that gate) |
| Moving to another stage inside a phase | **M4** |
| The reworked document is ready (G1, G2, G3) | **M5** |
| The run is blocked / stopped / resumes | **M6** |

### Moment 1 — a gate is ready for review

| | G1 Understand | G2 Plan — (a) BRD | G2 Plan — (b) Design system | G3 Build | G4 Deliver |
|---|---|---|---|---|---|
| Upload | RG .docx; **every client file found in discovery** (`01-requirement-gathering/files/`) | `scoping-document.docx` | design system .html | — | demo script .pdf; deck .pptx; demo video .mp4 → always Google Drive via "Video to Google Drive" (never `upload_public_file`) |
| Documents (create) | each discovered file: `doc_role input`, `type slack`, stage `1_signal_capture`, status `final`, `file_link` = uploaded URL (or the source's own link — Slack, Drive, Gmail, Calendar — with `file_kind link`), `summary` names its source (Slack / Drive / Gmail / Calendar) · RG: `type requirements`, stage `2_research_assess`, `file_kind docx` | BRD: `type brd`, stage `3_scope`, `file_kind docx` | Design system: `type design_system`, stage `4_design_system`, the `.html` uploaded with `upload_public_file` (`text/html`), `file_kind html` | App: `type app`, stage `6_finalize`, `file_link` = the published app URL, `file_kind link`, `name` = app name | Script `type demo_script` (`file_kind pdf`) · Deck `type deck` · Video `type video`; all stage `7_collaterals`, status `final` |
| gate_pack | g1 | g2 | g2 | g3 | g4 |
| status | in_review (inputs final) | in_review | in_review | in_review | final |
| Activity | `input_added` per input; `document_saved` for RG; `gate_posted` g1 | `document_saved`; `gate_posted` g2 | `document_saved`; `gate_posted` g2 | `document_saved`; `gate_posted` g3 | `document_saved` ×3; `stage_completed` g4, message "Deliver complete: demo-ready" (plus `gate_decided` g4 approve, actor_type person). If a deliver iteration is open: Iteration (update) status done, `resolved_document` = the deck's document_id, `resolved_at`; documents carry `from_iteration` |
| POC (update) | stage `2_research_assess`, current_gate g1, g1_status waiting, status waiting, g1_summary, gate_summary, `slack_notification true` | **stage stays `3_scope`**, current_gate g2, g2_status waiting, status waiting, g2_summary (the BRD), gate_summary, `slack_notification true` | stage `4_design_system`, current_gate g2, g2_status waiting, status waiting, g2_summary (BRD approved + design system), gate_summary, `slack_notification true` | stage `6_finalize`, current_gate g3, g3_status waiting, status waiting, g3_summary, gate_summary, `solution_id` (the Nebula solution `e_…`), `slack_notification true` | stage `8_demo_ready`, current_gate none, g4_status approved, status demo_ready, g4_summary, `slack_notification true` |

`gN_summary` / `gate_summary`: 2–4 plain sentences on what the phase produced and what the person should check. For G3, include
the test results from `04-build/test-report.md` (passed / fixed / still failing).
Record every new `document_id` in the run state.

### Moment 2 — the owner approves a gate in Claude
- **M2 (G1, G2 full, G3):** Documents (update) each `in_review` document of that gate → `approved`. Activity
  `gate_decided`, gate gN, decision approve, actor_type person. POC: `gN_owner_approved true`, `gN_status approved`,
  current_gate none, stage = G1 → `3_scope` · G2 → `5_build` · G3 → `7_collaterals`, status running. No
  slack_notification.
- **M2a (scoping approved, design system not done yet):** Document (update) the BRD → `approved`. Activity
  `gate_decided`, gate g2, decision approve, actor_type person, message "BRD approved". POC: current_gate none,
  status running, last_activity "BRD approved; design system in progress". **No** `g2_owner_approved`, no
  `g2_status approved`, no stage change, no slack_notification. `g2_status` deliberately stays `waiting` until the
  design system is posted (M1b) and approved (M2); `last_activity` tells readers the BRD is approved. (G2 is approved
  only with the design system.)
- **Confirm every approval (M2 and M2a) before the run moves on.** Right after the write, read the POC row back with
  `get_records` (and, for M2a, the BRD document). M2 is confirmed when `gN_status` is `approved` and
  `gN_owner_approved` is true; M2a when the BRD document is `approved`. Not confirmed → send the missing keys again (up
  to 3 tries in total). Still not confirmed → **the next stage does not start**: tell the person in one line what did
  not reach Orbit and ask once whether to retry or carry on without Orbit for now (if they carry on, the gate goes to
  `failed_writes` and the reconcile check below writes it later). Record the confirmation in the run state
  (`orbit.confirmed: [g1, g2a, g2, g3]`).

### Moment 3 — the owner asks for changes instead of approving
Iteration (create): status open, phase of the gate, **reason = their exact words**, related_document = the version
they rejected, skill = the stage skill. Add it to `open_iterations`. Activity: `iteration_logged` and `gate_decided`
(gate gN, decision request_changes, actor_type person). POC: `gN_status changes_requested`, current_gate none, status
running, last_activity (e.g. "Changes asked on the BRD"). No slack_notification.
Any further text the owner types about that change while it is being reworked is appended to the same iteration's
`reason` (update) rather than opening a new one.

### Moment 4 — moving to another stage inside a phase
POC (update): stage, status running, last_activity. No documents, no slack_notification. In this plugin: when Nebula
starts building (`5_build`, if not already), and nothing else — the move to `4_design_system` happens only with M1b.

### Moment 5 — the re-iterated document is ready (G1, G2, G3)
Upload the new file. Documents: update the rejected version → `superseded`; create the new version with version N+1,
`document_id …__v<N+1>`, status in_review, `from_iteration <iteration_id>`, summary saying what changed. Iteration
(update): status done, `resolved_document` = new document_id, `resolved_at` now; remove it from `open_iterations`.
Activity: `document_saved`, `gate_posted` gN. POC: current_gate gN, gN_status waiting, status waiting, gN_summary
(what changed), `slack_notification true`. Then wait for M2 or M3 again.
**G3 (the app):** there is no file to upload — the new version is an app document v(N+1) with the (same or new) app
URL as `file_link`. **Every new app version is posted, whenever it happens:**
- while G3 is waiting or changes were asked → this M5 (new app document v(N+1), `in_review`, the old one
  `superseded`, gate re-posted with notification);
- after G3 was approved (e.g. Nebula fixes made during collaterals) → create the app document v(N+1) with status
  `approved` and the published URL, set the previous version `superseded`, log `document_saved` (gate g3, message naming
  what changed) and update the POC `g3_summary` and `last_activity`; no notification, no gate change.
The run state's app version number and Orbit's latest app document must always match.

**G4 changes:** collaterals are written only once approved, so a change asked at the collaterals gate is M3 (phase
deliver) **without** `related_document` and **without** `g4_status` (Orbit has not seen G4 yet): Iteration + activities
+ POC `status running` and `last_activity` only. When they are approved, M1 · G4 sends the documents with
`from_iteration` and closes the iteration then.

### Moment 6 — the run stops or is blocked
POC (update): status `blocked` with `blocked_on` (one line: what is needed — a sign-in, a tool install, a missing
file), or status `stopped`. When it resumes: status running and a new last_activity. No slack_notification.

## When a write fails
- A reply with `"ok": false` or an error: read the message, fix the payload, and send **only the rows that failed**
  again (a create that succeeded must not be sent twice).
- `AUTH_EXPIRED` / signed out: ask the person to sign in again with `/nebula:setup` in this folder, then resend.
- `CONFIRM_REQUIRED`: you sent something that deletes; you never should. Stop and tell the person.
- After three failures on one step, stop the write-back for this moment, tell the person in one line what did not
  reach Orbit, add it to `failed_writes` (with the gate and whether a notification was held back), and carry on with
  the run. They are retried at the start of the next moment (see "Before every moment"). **Never send slack_notification for a gate whose
  documents did not all save.**

## Never
- Create or delete POC rows, or delete any row.
- Write `manager_*` fields, `pinned`, `slack_channel_id`, `slack_thread_ts` (Orbit and its people own these).
- Send `slack_notification: true` outside moments 1 and 5.
- Put a file's bytes or text in a row: upload it and save the link (no exceptions, the design system included).
- Write to any other object or tenant.

## Decisions (where this differs from `orbit-spec.md`)
1. G2 is pushed twice: the BRD as soon as scoping is done (with a notification), then the design system (with a
   notification); the stage moves to `4_design_system` only with the design system. G2 is approved with the design
   system.
2. G4 is written after the owner approves the collaterals in Claude.
3. The demo script is uploaded as a PDF (`file_kind pdf`); the "walkthrough video" is the demo video. The video is
   always put on Google Drive (any size) through Drive for desktop, shared with the whole company through the
   `POC Studio` folder, and its Drive link is its `file_link` (see "Video to Google Drive").
4. The POC ID is mandatory; there is no lookup by client slug.
5. No Orbit folder and no command-line script: reads, writes and uploads are Nebula's tenant tools called directly in
   the session, and files are uploaded with `upload_public_file` (public links, owner-approved) instead of `upload_file`.
6. Every client file found in discovery (Slack, Drive, Gmail, Calendar) is pushed as an input document at G1.
7. Every name/email field uses the POC owner's name and email from the POC record.
8. The design system is uploaded as a public `.html` file like every other document; no `content` or `format` is sent
   on any document row.
9. POC data policy: every file, client discovery files included, is uploaded as a public link without warning or asking
   (POCs use dummy data).

## /feedback — POC-level feedback (`orbit_studio_feedback`)

`/poc-studio:feedback <text>` records one piece of **POC-level** feedback: how a POC run went, what the outputs got
wrong, what should change in how POCs are run. It is **not** a change request on one document (that is an Iteration,
Moment 3). Orbit's skill analysis reads these rows together with the iterations on its next "Run analysis", so each
one can become an edit to one of the plugin's SKILL.md files.

1. **Find the POC.** Use the current workspace's POC ID: `state.json` → `orbit.poc_id` in the client workspace this
   session is working in (look for `*/*/state.json` under the current folder, or `./orbit-test/state.json`). If the
   session has none, or several and it is not clear which, ask once: "Which POC is this feedback for?" and accept a POC
   ID or a client name.
2. **Read the POC row** with the `get_records` tool (Setup step 1 loads it) for `client_name` and `stage`:
   - by POC ID: `{"host":"https://orbit.uat.unifyapps.com","objectId":"orbit_studio_poc","filters":[{"field":"poc_id","op":"EQUAL","values":["<poc_id>"]}],"limit":1}`;
     if that filter shape is refused, use `"filter":{"poc_id":"<poc_id>"}`, and if that is refused too, fetch the row
     by its id (the record id equals the POC ID);
   - by client name: filter `client_slug` EQUAL the client name lower-cased with every run of non-letters/digits
     replaced by `-`, `limit` 10. One row → use it; several → ask which (show poc_id and use_case); none → ask for the
     POC ID.
   - No row at all → say the POC was not found and ask for the right POC ID; write nothing.
3. **Write one row** with the `apply_record_edits` tool, exactly as for every other object (How to write: one call,
   leave out any key that would be `""` or `null`):

```json
{ "host": "https://orbit.uat.unifyapps.com", "objectId": "orbit_studio_feedback",
  "edits": [{ "op": "create", "properties": {
    "ticket_no": "FB-<Date.now()>",
    "poc": "<poc_id>",
    "client_name": "<from the POC row>",
    "poc_stage": "<the POC row's stage>",
    "gate": "none",
    "title": "<the person's short title, or their first sentence cut to 90 characters>",
    "feedback": "<their words, unedited; several points in one message stay in one row>",
    "channel": "claude",
    "given_by_name": "<the person's name>",
    "given_by_email": "<their email, if known>",
    "source": "user",
    "status": "open",
    "analysis_status": "pending",
    "skill": "<skill key, or general>",
    "created_at": <Date.now()> } }] }
```

   - `ticket_no` and `created_at` use the same `Date.now()` value (get it with a one-line script).
   - `skill` is the POC Studio skill or agent the feedback is about, as its key: `requirement-gathering`, `research`,
     `scoping-l1-first`, `design-system`, `poc-orchestrator`, `poc-collateral-studio`, `orbit-writeback`,
     `general-reviewer`, `poc-reviewer` — or `general`. Choose it in this order:
     1. The person names a skill or stage in the feedback (or as an argument) → that key.
     2. Otherwise decide from the feedback text and this session, by what stage or output it is about:
        intake, the brief, client sources → `requirement-gathering`; outside facts → `research`; the scoping/BRD
        document, L1 scope → `scoping-l1-first`; palette, brand, components, the design system → `design-system`;
        how the run is driven, gates, the Nebula build, app build quality → `poc-orchestrator`; demo script, deck,
        video → `poc-collateral-studio`; what shows in Orbit, statuses or links, Slack gate messages →
        `orbit-writeback`; the reviewer's checks → `general-reviewer`; the independent reviewer agent → `poc-reviewer`.
     3. It could be several, or none fits clearly → `general` (Orbit's skill analysis places it).
   - Optional: `"quote"` (exact short words worth keeping verbatim) and `"channel_ref"` (e.g. the workspace path).
   - `given_by_name` / `given_by_email` are **the person giving the feedback**, not the POC owner: take them from the
     connected Slack profile of the session's user if there is one, else from `git config user.name` /
     `git config user.email`, else ask once. Leave `given_by_email` out if it is not known.
   - The reply must say `"ok": true` for the row; read it back with `get_records` on `orbit_studio_feedback` filtered on
     `ticket_no` to confirm.
4. **Nothing else.** No Activity row, no POC update, no `slack_notification`, no Slack message: feedback does not move
   the POC.
5. **Reply in one line:** `Recorded as FB-<…> for <client_name>, under <skill name or General>. It goes into the next skill analysis.` If the write
   fails, show the error in one line and what to do (e.g. run `/nebula:setup` here on orbit.uat.unifyapps.com and sign
   in, then run `/poc-studio:feedback` again). A failed feedback write is not retried later and is not added to
   `failed_writes`.

## Testing a moment by hand
When the person asks to test a write-back moment directly (e.g. "upload this file as the G2 BRD", "log this as a change
request on G1", "approve G3"), run just that moment as written above, with the file they attached or named and the
POC ID they give (verify it first with Setup step 2). Use the same ids, rows, order and checks as in a real run, keep
the run state in `./orbit-test/state.json` when there is no workspace, and after the moment read the rows back with
`get_records` (filter `poc` = the POC ID; for the POC row, `poc_id`) and show the person what Orbit now holds.
