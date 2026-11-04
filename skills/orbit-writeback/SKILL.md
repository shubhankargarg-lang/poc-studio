---
name: orbit-writeback
description: Keeps Orbit · POC Studio (orbit.uat.unifyapps.com) in step with a POC Studio run, files feedback tickets in POC Build Loop and reads their status (/poc-studio:feedback), logs one Observability row per skill run (Moment 7), or runs one write-back moment by hand when the person asks to test it — uploads each gate's files and writes Document, Activity, Iteration and POC rows at the six write-back moments (gate posted, gate approved, changes asked, stage moved, new version ready, blocked). Called by the poc-orchestrator before and after every gate; also verifies the POC ID at start.
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

### 1. UnifyApps Headless's tenant tools (no separate folder)
All Orbit reads, writes and uploads go through **UnifyApps Headless's tenant tools, called directly as tools in this session**
(the same tools UnifyApps Headless uses while it builds), always with the host `orbit.uat.unifyapps.com`. There is no Orbit
folder and no command-line script.

Load them with **one** ToolSearch at the start of every write moment (they are deferred tools), by exact name first:

`select:mcp__plugin_ua_object__get_records,mcp__plugin_ua_object__apply_record_edits,mcp__plugin_ua_application-builder__upload_public_file`

If a name is not found, search for it (`+ua get_records`, `+ua apply_record_edits`,
`+ua upload_public_file`) and use the tool that comes back under that name.
- **UnifyApps Headless's tools are not in the session at all** → the `ua` plugin is not installed or not set up in this folder: ask the
  person to run `/ua:setup` here (tenant `orbit.uat.unifyapps.com`), then load them again.
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
  `poc_owner…`; use the record's own field names), and its **`client_name` and `use_case`** (every pipeline Document
  create sends them). Save all of them in the run state (`state.json` → `orbit`), so a resumed session has them. **The owner's name and email are used in
  every name and email field you write** (`created_by`, `actor_name`, `actor_email`), for AI and person actions
  alike; `actor_type` still says `ai` or `person`. If the record has no owner name or email, ask the person once.

### 3. Run state you keep
In the workspace `state.json`, under `orbit`:

```yaml
orbit:
  poc_id: POC-acme-20261018
  poc_record_id: <record id>
  owner: { name: <owner name>, email: <owner email> }
  client_name: <from the POC row>
  use_case: <from the POC row>
  documents:            # every document you wrote, by gate
    g1: [{ document_id: …, type: requirements, version: 1, status: in_review, file_link: … }]
  open_iterations:      # iteration rows waiting for a new version
    - { iteration_id: …, gate: g2, document_id: … }
  failed_writes: []     # anything that did not reach Orbit after 3 tries
```

and, beside `orbit`, `observability` (Moment 7's run group, last sequence and run ids).

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
  compressed. It goes by the route in **Video to Google Drive** below (copied through Drive for desktop into the
  company shared drive `POC Studio Video Library`, found and linked with the Drive connector). This is the only way the
  video is stored.
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

`slug` is the document type (`requirements`, `brd`, `wireframes`, `design-system`, `app`, `demo-script`, `deck`, `video`) or, for a
discovered input, `<source>-<short name>` (`slack-…`, `drive-…`, `gmail-…`, `calendar-…`).

## The rows

**Document** — object `orbit_studio_document` (create; afterwards update only `status`)

```json
{ "document_id": "<id>", "poc": "<poc_id>", "origin": "pipeline", "client_name": "<from the POC row>",
  "use_case": "<from the POC row>", "name": "BRD", "type": "brd", "stage": "3_scope", "gate_pack": "g2",
  "version": 1, "status": "in_review", "doc_role": "artifact",
  "file_link": "https://orbit.uat.unifyapps.com/api/file/download/…", "file_kind": "docx",
  "file_name": "Acme - BRD v1.docx", "summary": "One or two lines on what the document holds.",
  "created_by": "<POC owner name>", "saved_at": 1792280000000 }
```

- `type`: slack · requirements · brd · wireframes · design_system · app · demo_script · deck · video
- **Every Document create in the pipeline** sends `"origin": "pipeline"`, `"client_name"` and `"use_case"` (from the
  POC row read in Setup). One-off documents (`/poc-studio:<asset>` commands) are written by "One-off documents" below.
- **App documents** (`type app`) always carry the app's **preview link** as `file_link`, by the "Preview link rule"
  below, never the published matrix URL.
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
1. Read the POC row and this POC's documents (ignore rows with `origin` = `standalone`: one-off documents are never
   part of a gate) (`get_records`, filter `poc` = the POC ID, limit 100).
2. For every gate the run state shows **approved** but Orbit does not (`gN_status` not `approved` or
   `gN_owner_approved` not true): write the missing approval **only** — that gate's `in_review` documents →
   `approved`, an Activity `gate_decided` approve (actor_type person, the owner, message "Approval recorded late"),
   and on the POC row only `gN_status approved`, `gN_owner_approved true` and `last_activity`. For `g2a` or `g2w`
   approved in the run state whose BRD or wireframes document is not `approved` in Orbit: that document → `approved`
   and an Activity `gate_decided` approve only (no `g2_status`, no `g2_owner_approved`). **Never move `stage`,
   `current_gate` or `status` backwards**, and send no `slack_notification`.
3. For every document version in the run state that Orbit lacks (e.g. an app version): create it as in M5 (or as the
   approved app version above).
4. Retry everything in `failed_writes`.
5. Say in one line what was written (or "Orbit is in step").
Do not write G4 until G1–G3 show approved in Orbit.

## Video to Google Drive

The Drive connector cannot take a large file (it only accepts file bytes inside the tool call) and cannot set
company-wide link sharing. So the video goes through **Google Drive for desktop** on the person's computer: Claude
Code copies the file into a local Drive folder, the Drive app uploads it in the background, and the connector finds
it and gives its link.

**Where it goes — the company shared drive (primary route).** Every POC video goes to one shared drive that the whole
company already belongs to, so nobody has to create or share a folder of their own:

| | |
|---|---|
| Shared drive name | `POC Studio Video Library` |
| Shared drive id | `0AOY3pnWOezbhUk9PVA` (also the id of its root folder) |
| Members | `allemployees@unifyapps.com` as Contributor (everyone can add files and open every link) |
| Local folder (Drive for desktop, macOS) | `~/Library/CloudStorage/GoogleDrive-<email>/Shared drives/POC Studio Video Library/` |
| Where the video goes | the drive's **root**, as `<POC ID> - <Client> - Demo video v<N>.mp4` (no sub-folders) |

**How the connector finds files in it.** The connector's search does **not** return shared-drive files on a plain
title search; it finds them only when the query names the folder: always search
`parentId = '0AOY3pnWOezbhUk9PVA' and title = '<exact file name>'`. Never drop the `parentId` clause, and never look
for the file by date (Drive for desktop may keep a file's original timestamps).

**Fallback route (only if the shared drive route fails):** the person's own `My Drive/POC Studio/` folder, shared
with the company, exactly as before (see "Fallback: personal POC Studio folder" below). Last resort: the person drops
the file into the shared drive by hand.

### Video route check (in Setup, while the person is at the screen)

Run it once per run in the orchestrator's Setup, and again before the video upload if it did not pass. It never
blocks the run: if it fails, flag it and carry on.

1. **Drive connector**: its tools are in the session (Setup already requires this).
2. **Drive for desktop and the shared drive**: find the local folders and whether the app is running, with Bash:
   ```bash
   python3 - <<'PY'
   import glob, json, os, subprocess, sys
   DRIVE = "POC Studio Video Library"
   h = os.path.expanduser("~"); accounts = []
   for acct in sorted(glob.glob(f"{h}/Library/CloudStorage/GoogleDrive-*")):     # macOS (stream or mirror)
       email = os.path.basename(acct)[len("GoogleDrive-"):]
       # the shared drive sits one level down, in "Shared drives" (or its localised name): match it by its own name
       shared = [d for d in glob.glob(f"{acct}/*/{glob.escape(DRIVE)}") if os.path.isdir(d)]
       shared_parent = os.path.dirname(shared[0]) if shared else None             # "Shared drives", any language
       mydrive = [d for d in sorted(glob.glob(f"{acct}/*")) if os.path.isdir(d) and d != shared_parent
                  and not os.path.basename(d).startswith(("Shared", ".", "Other computers"))]
       accounts.append({"email": email, "shared_drive": shared[0] if shared else None,
                        "my_drive": mydrive[0] if mydrive else None})
   for d in [f"{h}/My Drive", f"{h}/Google Drive/My Drive"] + [f"{c}:/My Drive" for c in "DEFGHIJKLMNOPQRSTUVWXYZ"]:
       if os.path.isdir(d):                                                       # mirror mode / Windows drive letter
           base = os.path.dirname(d)
           shared = [s for s in glob.glob(f"{base}/*/{glob.escape(DRIVE)}") if os.path.isdir(s)]
           accounts.append({"email": None, "shared_drive": shared[0] if shared else None, "my_drive": d})
   if sys.platform == "win32":
       running = "GoogleDriveFS.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout
   else:
       running = subprocess.run(["pgrep", "-if", "Google Drive"], capture_output=True).returncode == 0
   print(json.dumps({"running": running, "accounts": accounts}))
   PY
   ```
   With several accounts, use the one whose email is on the POC owner's domain (`@unifyapps.com`). Its
   `shared_drive` is `<shared root>`; if it is `null`, the shared drive route fails for this account (see the table
   below) and the fallback route is checked instead.
3. **Same account and sync working (the real test):** write a small file
   `<shared root>/_poc-studio-sync-check (<email>).txt` containing the POC ID and a fresh random token (one file per
   person, overwritten each run, never deleted). Then, with the connector, search
   `parentId = '0AOY3pnWOezbhUk9PVA' and title = '_poc-studio-sync-check (<email>).txt'` every 15 s for up to 3
   minutes and read it (`read_file_content`): it passes when the token matches. Seeing the token through the
   connector proves the connector and Drive for desktop use the same Google account, that this account can write to
   the shared drive, and that sync works.
   The first write may bring up Claude Code's permission prompt (the folder is outside the workspace) and macOS's
   "access files on Google Drive" prompt: the person approves both once.
4. **Company-wide access:** read the sync-check file's permissions (`get_file_permissions`). It passes when there is
   a `group` permission for `allemployees@unifyapps.com` (any role from `reader` up). Members of a shared drive are
   inherited by every file in it, so no link-sharing setting is needed and Claude never changes sharing itself.
5. **If step 2, 3 or 4 fails, check the fallback route** ("Fallback: personal POC Studio folder" below). Save which
   route will be used.
6. Save the result in `state.json` → `video_route`:
   `{ "ok": true|false, "route": "shared_drive"|"personal_folder"|null, "root": "<local folder the video goes to>",
   "account": "<email>", "drive_id": "0AOY3pnWOezbhUk9PVA", "company_share": true|false,
   "folder_id": "<parent id the connector searches: the drive id, or the POC Studio folder id on the fallback>",
   "reason": "<why the shared drive route failed, if it did>", "checked_at": "<ISO time>" }`, and one line in
   `context-log.md`.
7. Tell the person in one line:
   - shared drive route passed → "The demo video will go to the `POC Studio Video Library` shared drive
     automatically (`<account>`), open to everyone at UnifyApps."
   - fallback route passed → "The demo video will go to your own `POC Studio` Drive folder: the shared drive route
     did not work because `<reason>`. Fix: `<fix>`."
   - neither → "**The demo video will not ship to Drive automatically:** `<reason>`. Fix: `<fix>`. Otherwise you will
     be asked to drop it into the shared drive at the end." Say it can be re-checked any time, re-check when they say
     it is fixed, and carry on either way.

| What failed (shared drive route) | `reason` | `fix` |
|---|---|---|
| No local Drive folder | Google Drive for desktop is not installed or not signed in | Install it and sign in with your UnifyApps Google account |
| Folder found, app not running | Google Drive for desktop is not running | Open Google Drive (it stays in the menu bar) |
| `shared_drive` is null | The `POC Studio Video Library` shared drive is not on this computer (not a member yet, or the Drive app has not listed it yet) | Open Finder → Google Drive → Shared drives and check it is there; if not, ask the drive's manager to check that `allemployees@unifyapps.com` (or you) is a member, then wait a minute and re-check |
| Could not write the folder | Claude Code or macOS did not allow access to the Drive folder, or this account is only a Viewer on the drive | Approve the access prompts; if it still fails, ask the drive's manager for Contributor access, then re-check |
| Token not seen in 3 minutes | Drive for desktop is signed in as `<email from the folder name>` but the Drive connector cannot see its files (a different Google account), or sync is paused/offline | Sign both in to the same UnifyApps account (connector: claude.ai → Settings → Connectors → Google Drive), check Drive is online and not paused |
| No `allemployees` permission | The shared drive is not open to the whole company, so the video would be visible only to its members | Ask the drive's manager to add `allemployees@unifyapps.com` as a member |

### Uploading the video (M1 · G4)

1. If `video_route.ok` is not true, **or `video_route.route` is missing** (a run started before POC Studio 1.22.0,
   whose check only knew the personal folder), run the check again first.
2. **Shared drive route** (`video_route.route = shared_drive`):
   1. Copy (never move) the final `.mp4` to `<shared root>/<POC ID> - <Client> - Demo video v<N>.mp4` (`cp`; no
      sub-folders). If a file with that name is already there from an earlier run of the same POC, use the next `v<N>`.
   2. With the connector, search `parentId = '0AOY3pnWOezbhUk9PVA' and title = '<POC ID> - <Client> - Demo video
      v<N>.mp4'` every 30 s for up to 15 minutes (large files take a while to upload). Take the newest match.
   3. Read its permissions: the `allemployees@unifyapps.com` group permission (inherited from the drive) means
      everyone in the company can open it. If it is missing, say at the gate that the video is open only to the
      drive's members and why.
3. **Fallback route** (`video_route.route = personal_folder`): the steps in "Fallback: personal POC Studio folder".
4. Get its link (`get_file_metadata` → `viewUrl` / `webViewLink`, else `https://drive.google.com/file/d/<id>/view`)
   and use it as the video document's `file_link`, with `file_kind video`, and "Video on Google Drive" in its
   `summary` (add "shared drive POC Studio Video Library" or "personal POC Studio folder").
5. **Last resort** (no route passed, or the file did not appear in 15 minutes): ask the person once to drop the file
   into the `POC Studio Video Library` shared drive (Finder → Google Drive → Shared drives), named
   `<POC ID> - <Client> - Demo video v<N>.mp4`; give the local path of the video. Wait until they say it is done,
   then do step 2.2–2.3 and step 4. Say which reason made it fall back.

### Fallback: personal POC Studio folder

Used only when the shared drive route fails and this route passes. It is the route POC Studio used before the shared
drive, unchanged:

- **Check:** the person's `My Drive` root is `my_drive` from step 2. Write `<my_drive>/POC Studio/_poc-studio-sync-check.txt`
  (`mkdir -p` the folder) with the POC ID and a fresh token; with the connector, search
  `title = '_poc-studio-sync-check.txt'` every 15 s for up to 3 minutes and read it: it passes when the token matches.
  Then find the `POC Studio` folder (`title = 'POC Studio'`, folder mime type, `owner = 'me'`) and read its
  permissions: company-wide when there is a `domain` permission for the owner's email domain with role `reader` or
  higher. If it is missing, ask the person once to set it themselves (give the folder link): **Share → General access
  → "<company>" (anyone in the organisation with the link) → Viewer → Done**. Claude never changes this setting itself.
- **Upload:** copy the `.mp4` to `<my_drive>/POC Studio/<POC ID> - <Client>/<Client> - Demo video v<N>.mp4`
  (`mkdir -p`, then `cp`); search `title = '<Client> - Demo video v<N>.mp4'` every 30 s for up to 15 minutes and take
  the newest match in that folder; read its permissions (a `domain` permission inherited from `POC Studio`); if it is
  missing, share it with the POC owner's email as `reader` and say at the gate that it is not shared company-wide and
  why. Then step 4 above.

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
| Wireframes done + reviewed, before their Claude gate | **M1w · G2 (Wireframes)** — see below |
| Wireframes approved in Claude | **M2w · G2 (Wireframes)** — see below |
| Design System done + reviewed, before its Claude gate | **M1b · G2 (Design system)** |
| Design System approved in Claude | **M2 · G2** (full) |
| Person approves the Zen plan (Stage 4, before any builder agent runs) | **M4a** — Activity "Zen plan approved"; stage stays `5_build` |
| platform-master builds an asset by the browser fallback (Stage 4) | **M4b** — Activity "Asset built by fallback"; stage stays `5_build` |
| UnifyApps Headless build published, before the verify gate | **M1 · G3** |
| App verified/approved in Claude | **M2 · G3** |
| Collaterals done + reviewed, approved in Claude | **M1 · G4** (Deliver complete) |
| Changes asked at any Claude gate | **M3** (phase of that gate) |
| Moving to another stage inside a phase | **M4** |
| The reworked document is ready (G1, G2, G3) | **M5** |
| The run is blocked / stopped / resumes | **M6** |

### Moment 1 — a gate is ready for review

**M1w · G2 (Wireframes)** is written exactly like the BRD column below, with these values: upload
`<slug>-wireframes.pdf` with `upload_public_file`; Document `type wireframes`, name "Wireframes", stage `3_scope`,
gate_pack `g2`, status `in_review`, `file_kind pdf`, `summary` = page and component counts and which pages are maps;
Activity `document_saved` and `gate_posted` g2; POC: **stage stays `3_scope`**, current_gate g2, g2_status waiting,
status waiting, g2_summary (BRD approved + wireframes), gate_summary, `slack_notification true`.

| | G1 Understand | G2 Plan — (a) BRD | G2 Plan — (b) Design system | G3 Build | G4 Deliver |
|---|---|---|---|---|---|
| Upload | RG .docx; **every client file found in discovery** (`01-requirement-gathering/files/`) | `scoping-document.docx` | design system .html | — | demo script .pdf; deck .pptx; demo video .mp4 → always Google Drive via "Video to Google Drive" (never `upload_public_file`) |
| Documents (create) | each discovered file: `doc_role input`, `type slack`, stage `1_signal_capture`, status `final`, `file_link` = uploaded URL (or the source's own link — Slack, Drive, Gmail, Calendar — with `file_kind link`), `summary` names its source (Slack / Drive / Gmail / Calendar) · RG: `type requirements`, stage `2_research_assess`, `file_kind docx` | BRD: `type brd`, stage `3_scope`, `file_kind docx` | Design system: `type design_system`, stage `4_design_system`, the `.html` uploaded with `upload_public_file` (`text/html`), `file_kind html` | App: `type app`, stage `6_finalize`, `file_link` = the app's **preview link** (Preview link rule), `file_kind link`, `name` = app name | Script `type demo_script` (`file_kind pdf`) · Deck `type deck` · Video `type video`; all stage `7_collaterals`, status `final` |
| gate_pack | g1 | g2 | g2 | g3 | g4 |
| status | in_review (inputs final) | in_review | in_review | in_review | final |
| Activity | `input_added` per input; `document_saved` for RG; `gate_posted` g1 | `document_saved`; `gate_posted` g2 | `document_saved`; `gate_posted` g2 | `document_saved`; `gate_posted` g3 | `document_saved` ×3; `stage_completed` g4, message "Deliver complete: demo-ready" (plus `gate_decided` g4 approve, actor_type person). If a deliver iteration is open: Iteration (update) status done, `resolved_document` = the deck's document_id, `resolved_at`; documents carry `from_iteration` |
| POC (update) | stage `2_research_assess`, current_gate g1, g1_status waiting, status waiting, g1_summary, gate_summary, `slack_notification true` | **stage stays `3_scope`**, current_gate g2, g2_status waiting, status waiting, g2_summary (the BRD), gate_summary, `slack_notification true` | stage `4_design_system`, current_gate g2, g2_status waiting, status waiting, g2_summary (BRD and wireframes approved + design system), gate_summary, `slack_notification true` | stage `6_finalize`, current_gate g3, g3_status waiting, status waiting, g3_summary, gate_summary, `solution_id` (the UnifyApps Headless solution `e_…`), `slack_notification true` | stage `8_demo_ready`, current_gate none, g4_status approved, status demo_ready, g4_summary, `slack_notification true` |

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
  status running, last_activity "BRD approved; wireframes in progress". **No** `g2_owner_approved`, no
  `g2_status approved`, no stage change, no slack_notification. `g2_status` deliberately stays `waiting` until the
  design system is posted (M1b) and approved (M2); `last_activity` tells readers the BRD is approved. (G2 is approved
  only with the design system.)
- **M2w (wireframes approved, design system not done yet):** the same as M2a, for the wireframes document: Document
  (update) → `approved`; Activity `gate_decided`, gate g2, decision approve, actor_type person, message "Wireframes
  approved"; POC: current_gate none, status running, last_activity "Wireframes approved; design system in progress".
  No `g2_owner_approved`, no `g2_status approved`, no stage change, no slack_notification.
- **Confirm every approval (M2, M2a and M2w) before the run moves on.** Right after the write, read the POC row back with
  `get_records` (and, for M2a or M2w, the BRD or wireframes document). M2 is confirmed when `gN_status` is `approved` and
  `gN_owner_approved` is true; M2a when the BRD document is `approved`; M2w when the wireframes document is `approved`. Not confirmed → send the missing keys again (up
  to 3 tries in total). Still not confirmed → **the next stage does not start**: tell the person in one line what did
  not reach Orbit and ask once whether to retry or carry on without Orbit for now (if they carry on, the gate goes to
  `failed_writes` and the reconcile check below writes it later). Record the confirmation in the run state
  (`orbit.confirmed: [g1, g2a, g2w, g2, g3]`).

### Sonic mode (the run's `state.json` → `mode` is `"sonic"`)

In Sonic run mode the AI PM approves each gate (poc-orchestrator: "The Sonic gate"). The moments, rows, order and checks
are the same as above, with these differences only:
- **No `slack_notification` at all** in moments 1 and 5 (gates are posted and approved silently). Never hold one back
  for later either.
- **M2 / M2a / M2w and M4a**: the Activity has `actor_type: "ai"` (names and emails stay the POC owner's, as Setup
  says) and the message says who approved it: "Approved by the AI PM (Sonic mode)" (M2a: "BRD approved by the AI PM
  (Sonic mode)"; M2w: "Wireframes approved by the AI PM (Sonic mode)"; M4a: "Zen plan approved by the AI PM (Sonic
  mode): <n> tasks; preview <preview path>"). The POC row gets the same keys as in Zen, `gN_owner_approved true`
  included, because the app and the Reconcile check read that key as "this gate is approved"; `last_activity` says
  "… approved by the AI PM (Sonic)".
- **G4** (collaterals): `gate_decided` g4 approve with `actor_type: "ai"`, same message.
- **Reconcile check** on a Sonic run: a late approval is written with `actor_type: "ai"` and the message "Approval
  recorded late (AI PM, Sonic mode)".
- **M3** (changes the person types during a Sonic run) is written exactly as in Zen, `actor_type: "person"`.

### Moment 3 — the owner asks for changes instead of approving
Iteration (create): status open, phase of the gate, **reason = their exact words**, related_document = the version
they rejected, skill = the stage skill. Add it to `open_iterations`. Activity: `iteration_logged` and `gate_decided`
(gate gN, decision request_changes, actor_type person). POC: `gN_status changes_requested`, current_gate none, status
running, last_activity (e.g. "Changes asked on the BRD"). No slack_notification.
Any further text the owner types about that change while it is being reworked is appended to the same iteration's
`reason` (update) rather than opening a new one.

### Moment 4 — moving to another stage inside a phase
POC (update): stage, status running, last_activity. No documents, no slack_notification. In this plugin: when UnifyApps Headless
starts building (`5_build`, if not already), and nothing else — the move to `4_design_system` happens only with M1b.

### Moment 4a — the person approves the Zen plan (Stage 4)
Written right after the person says yes ("start") to UnifyApps Headless's Zen plan, before the builder agents run.
Activity (create) only:

```json
{ "activity_id": "ACT-…", "poc": "<poc_id>", "type": "document_saved", "stage": "5_build", "gate": "g3",
  "actor_type": "person", "actor_name": "<POC owner name>", "actor_email": "<POC owner email>",
  "message": "Zen plan approved: <n> tasks; preview <preview path>", "created_at": 1792280000000 }
```

`type` is `document_saved` because the Activity object has no plan-approval type; the message carries the meaning.
POC (update): `last_activity` "Zen plan approved; building with <n> tasks", `last_activity_at`. The stage stays
`5_build`; no document, no gate status change, no slack_notification. If the person chooses "keep for later"
instead, write **M6** (blocked) and nothing here.

### Moment 4b — platform-master builds an asset by the browser fallback (Stage 4)
Written once per asset, right after platform-master has built and verified it and handed it back to UnifyApps
Headless. Activity (create) only:

```json
{ "activity_id": "ACT-…", "poc": "<poc_id>", "type": "document_saved", "stage": "5_build", "gate": "g3",
  "actor_type": "ai", "actor_name": "<POC owner name>", "actor_email": "<POC owner email>",
  "message": "Asset built by fallback: <type> <name> (<id>), task <n>", "created_at": 1792280000000 }
```

`type` is `document_saved` because the Activity object has no build-step type; the message carries the meaning. No POC
update, no document, no gate status change, no slack_notification.

### Moment 5 — the re-iterated document is ready (G1, G2, G3)
Upload the new file. Documents: update the rejected version → `superseded`; create the new version with version N+1,
`document_id …__v<N+1>`, status in_review, `from_iteration <iteration_id>`, summary saying what changed. Iteration
(update): status done, `resolved_document` = new document_id, `resolved_at` now; remove it from `open_iterations`.
Activity: `document_saved`, `gate_posted` gN. POC: current_gate gN, gN_status waiting, status waiting, gN_summary
(what changed), `slack_notification true`. Then wait for M2 or M3 again.
**G3 (the app):** there is no file to upload — the new version is an app document v(N+1) with the (same or new) app
preview link (Preview link rule) as `file_link`. **Every new app version is posted, whenever it happens:**
- while G3 is waiting or changes were asked → this M5 (new app document v(N+1), `in_review`, the old one
  `superseded`, gate re-posted with notification);
- after G3 was approved (e.g. UnifyApps Headless fixes made during collaterals) → create the app document v(N+1) with status
  `approved` and the preview link, set the previous version `superseded`, log `document_saved` (gate g3, message naming
  what changed) and update the POC `g3_summary` and `last_activity`; no notification, no gate change.
The run state's app version number and Orbit's latest app document must always match.

**Wireframes updated for a change after the build (orchestrator 4c, big or very big).** The change was logged as M3
at G3 (phase build). When the person approves the updated wireframes: upload the new wireframes PDF **and** the change
sheet (`changes/CR-<n>/change-sheet.pdf`); Documents: the wireframes document's current version → `superseded`; create
version N+1 with status `approved` (the person approved it), `from_iteration <iteration_id>`, summary = the pages
added, changed and removed. Activity: `document_saved` (gate g2, message "Wireframes v<N+1> for change: <one line>",
actor_type person). POC: `last_activity` only; no gate status change, no notification. **The iteration stays open**:
it is closed by the new app version's M5 above, which then names the wireframes version it was built from in its
summary. A dropped change (the person chose "Drop this change") closes the iteration with status done, no
`resolved_document`, and an Activity `document_saved` "Change dropped: <one line>". One-off runs write the wireframes
version as a one-off document ("One-off documents") instead.

**G4 changes:** collaterals are written only once approved, so a change asked at the collaterals gate is M3 (phase
deliver) **without** `related_document` and **without** `g4_status` (Orbit has not seen G4 yet): Iteration + activities
+ POC `status running` and `last_activity` only. When they are approved, M1 · G4 sends the documents with
`from_iteration` and closes the iteration then.

**A BRD version after a model switch** (connector-discovery "A model change in the BRD"). The person already chose
the model, so there is no gate and no iteration: upload the new BRD, create its document v(N+1) with status
`approved` and a summary "Model switch: <slot> <old card> → <new card>", set the previous version `superseded`, log
`document_saved` (gate g2, message naming the switch, `actor_type: person`), and update the POC's `last_activity`. No
notification, no gate change. A one-off run writes it as a one-off document version instead.

### Moment 6 — the run stops or is blocked
POC (update): status `blocked` with `blocked_on` (one line: what is needed — a sign-in, a tool install, a missing
file), or status `stopped`. When it resumes: status running and a new last_activity. No slack_notification.

### Moment 7 — a skill finished (`orbit_studio_skill_run`, the Observability view)

POC Build Loop's **Observability** view reads one row per skill run from `orbit_studio_skill_run`. Write **exactly one
row right after each logged skill run returns**, in a full run (poc-orchestrator) and in every one-off run
(asset-run), with the same `apply_record_edits` tool and the same write rules as every other moment (one call, leave
out every key that has no value, never `""` or `null`). **Create only:** never update or delete a skill-run row.

**Which runs get a row:**

| Run | `skill` | `label` (short, plain) |
|---|---|---|
| The orchestrator's Setup, once per session (full runs only) | `poc-orchestrator` | "POC started" (or "POC resumed") |
| Requirement Gathering | `requirement-gathering` | "RG doc v<N>" |
| Connector discovery (stage 1c, `scope: verify`, `scope: item`, model recovery) | `connector-discovery` | "Integration spec · <system>" or "Models only" (1c), "Verify before build", "Item: <object or operation>", "Model recovery: <slot>" (phase and gate of the stage it serves: a recovery during the build is `build`/`g3`) |
| Scoping | `scoping-l1-first` | "BRD v<N>" (a REVISE re-run: "BRD v<N> · <k> fixes") |
| Wireframes | `wireframes` | "<n> frames" |
| Design system | `design-system` | "Design system v<N>" |
| Each platform-master job | `platform-master` | "Pointers", "Question review · <n> questions, <k> options added" (one row for the whole Zen planning window, written when the plan is approved; `started_at` = `state.json` → `zen_planning_started_at`), "Plan review, round <r>", "Fallback: <asset>" |
| The Stage 4 build by UnifyApps Headless (from the plan's start to publish) | `unifyapps-headless` | "App build · <n> tasks" |
| Collaterals | `poc-collateral-studio` | what was made, e.g. "Script, deck, video" |
| Each `research` call | `research` | the question, cut to 60 characters |
| Each AI PM **review** (review mode, every round, the 4b build walk included) | `ai-pm` | "<what it reviewed> review, round <r>", e.g. "BRD review, round 1" |

Not logged: orbit-writeback's own moments, and the AI PM's resolve-mode answers (they are in `context-log.md`).

**Run state** (full run: `state.json` → `observability`; one-off: this run's entry → `observability`):

```yaml
observability:
  run_group: GRP-1793630000000     # "GRP-" + Date.now(), made once when the session's command starts; reused for every row
  sequence: 6                      # the last sequence written
  runs: { "scoping-l1-first|BRD v1": RUN-1793639000000-1190 }   # run_id by skill + label, so a review can point at it
```

- **`sequence`:** from 1, +1 per row. A full run continues from the highest `sequence` already logged for this `poc`:
  at Setup or resume, `get_records` on `orbit_studio_skill_run` with filter `poc` EQUAL the POC ID, sort
  `{field: "sequence", order: "DESC"}`, `limit` 1 (none → 0). A one-off run counts within its `run_group`, from 1.
- **Times:** note `started_at` (`node -e 'console.log(Date.now())'`) when the skill starts and `ended_at` when it
  returns.
- **Re-runs always get their own row.** A stage skill that runs again — to apply an AI PM REVISE, or the person's
  change request — is a new run: its own row, written as soon as it returns and **before** the review of it. Label
  "<doc> v<N> · <k> fixes" (a REVISE) or "<doc> v<N+1> · changes" (a change request), `round` +1, `triggered_by`
  `orchestrator` (REVISE) or `iteration` (changes, with the person's words in `input_ask`), `input_ask` = the fix lines
  for a REVISE. When the person asks for changes, first run `skill_run_row.py note-change <skill> --gate <gN>`; if they
  drop the change instead, `skill_run_row.py change-dropped <skill>`.

**The row** (field names exactly as stored; single-selects take the code):

```json
{ "host": "https://orbit.uat.unifyapps.com", "objectId": "orbit_studio_skill_run",
  "edits": [{ "op": "create", "properties": {
    "run_id": "RUN-<Date.now()>-<4 random digits>",
    "run_group": "<observability.run_group>",
    "poc": "<poc_id: full runs only; leave the key out for one-off runs>",
    "origin": "poc | one_off",
    "client_name": "<client>", "use_case": "<use case>",
    "primary_document_id": "<document_id of the main document this run saved, when it saved one>",
    "phase": "understand | plan | build | deliver",
    "gate": "g1 | g2 | g3 | g4 | none",
    "sequence": <n>,
    "skill": "<from the table>", "label": "<from the table>",
    "reviews_run_id": "<ai-pm only: run_id of the run it reviewed, from observability.runs>",
    "verdict": "<ai-pm only: pass | revise | block | ask_human>",
    "round": <1, 2, … when the same skill re-runs for the same gate>,
    "triggered_by": "orchestrator | person | command | iteration",
    "actor_name": "<the person running the session>", "actor_email": "<their email, if known>",
    "plugin_version": "<version in the plugin's .claude-plugin/plugin.json>",
    "model": "<the model id the skill ran on>",
    "started_at": <ms>, "ended_at": <ms>, "duration_ms": <ended_at - started_at>,
    "tokens_in": <n>, "tokens_out": <n>,
    "input_ask": "<the instruction the skill was given; on a re-run after changes, with the person's gate comment>",
    "input_documents": [{ "name": "BRD", "version": 1, "document_id": "<…>", "link": "<…>" }],
    "reasoning": ["<3–6 short plain sentences: what it checked, what it noticed, what it decided and why>"],
    "output_summary": "<one line, e.g. Sent 3 fixes back to scoping-l1-first>",
    "output_decisions": ["<the changes or decisions it made, one per line>"],
    "output_documents": [{ "name": "BRD", "version": 2, "document_id": "<…>", "link": "<…>" }],
    "created_at": <ms> } }] }
```

- **`phase` / `gate`:** requirement-gathering `understand`/`g1` · scoping-l1-first, wireframes, design-system
  `plan`/`g2` · platform-master, unifyapps-headless `build`/`g3` · poc-collateral-studio `deliver`/`g4` · an ai-pm
  review or a research call takes the phase and gate of the stage it serves · the orchestrator's row `understand`/
  `none`. In a one-off run, `phase` by the asset and `gate` `none`.
- **`origin` / `poc`:** `poc` for a full run (send `poc`); `one_off` for a one-off run (**never send `poc`**, even when
  the one-off was given a POC ID: a blank or foreign lookup is rejected).
- **`triggered_by`:** `orchestrator` for every run inside a full run, AI PM review rounds included; `command` for a
  one-off run's first pass; `iteration` for a re-run after the person asked for changes (`input_ask` then carries
  their words); `person` when the person runs a step by hand (e.g. testing a moment).
- **`round`:** 1 for the first run of that skill for the gate; +1 for each re-run (REVISE fixes, changes asked).
- **Documents:** `input_documents` and `output_documents` use the Orbit document rows this run already wrote or read
  (`document_id`, `version`, `file_link` as `link`). A run that saved no Orbit document (an AI PM review, a research
  call, platform-master's pointers) has no `output_documents` and no `primary_document_id`: its result is in
  `output_summary` and `output_decisions`.
- **AI PM rows:** `verdict` from the verdict file (`PASS` → `pass`, `REVISE` → `revise`, `BLOCK` → `block`,
  `ASK_HUMAN` → `ask_human`; an `INVALID_REQUEST` gets no row, only the corrected review does); `reasoning` from its findings and decision; `output_decisions` = its fix lines (or
  "No changes" on a pass); `reviews_run_id` = the `run_id` of the stage run it reviewed.
- **`model`:** the session's model id; for an AI PM review, the model its subagent ran on when the Agent result says.
- **Tokens:** use the measured counts when the run reports them (an AI PM subagent's usage). Otherwise **estimate**:
  `tokens_in` ≈ characters of the instruction plus every file the skill read, ÷ 4; `tokens_out` ≈ characters of
  everything it wrote (files and messages), ÷ 4. Round to the nearest 100.
- **The run flag and the hook.** At the start of a run (orchestrator Setup, or a one-off run's start) write
  `${CLAUDE_PROJECT_DIR:-<cwd>}/.poc-studio/observability` (holding the `run_group`); delete it when the run ends or
  stops. While it exists, the plugin's `skill-run-log.sh` hook saves each logged skill's start time in
  `.poc-studio/skill-starts/<skill>` and reminds the session, in the tool result, to write the row when the skill
  returns (for an AI PM review, right when its subagent returns). Use that start time as `started_at`. When an AI PM
  review returns, the hook also names any re-run that has no row yet and any rows still pending. The ledger
  (`.poc-studio/skill-runs/`) stays when the flag is deleted: it is the record the report and the checks read.
- **How to write it (always through the builder, never by hand).** The object validates every write against its
  schema, so one wrong type fails the row. Let `O` be this skill's `scripts/` folder
  (`find ~/.claude/plugins -path '*orbit-writeback/scripts/skill_run_row.py' -exec dirname {} \; | head -1`) and
  `LG` the run's `.poc-studio` folder (the one holding the `observability` flag; its absolute path is in `state.json`
  → `observability.ledger`, or the one-off run's entry). Pass `--ledger "$LG"` to every builder call: the builder keeps
  every row in a local ledger there (`skill-runs/`), so no row is ever lost.
  1. Write the fields you have, as one JSON object, to `$TMPDIR/skill-run-in.json` with a short script (never retype
     long text by hand). Loose values are fine: the builder turns "104k" into 104000, "v1" into 1, "REVISE" into
     `revise`, seconds into milliseconds, a command name (`brd`) into its skill, drops empty values and unknown keys,
     leaves `poc` off one-off rows, fills `phase`/`gate` from the skill, makes `run_id`, `duration_ms` and `created_at`.
     Tokens are never left empty: give measured counts when you have them; otherwise add `files_read` and
     `files_written` (paths) and the builder estimates both.
  2. `python3 "$O/skill_run_row.py" $TMPDIR/skill-run-in.json --out $TMPDIR/orbit-skill-run.json --ledger "$LG"`.
     - Exit 0 → send that file's JSON with `apply_record_edits` exactly as it is.
     - Exit 2 → the row lacks `skill` or `started_at`: add it (the hook's start file, or now) and build again.
     - Exit 3 → another row must come first: a review is never logged before the run it checked (`reviews_run_id`
       must be a logged run), and a re-run after a REVISE or a change request must have its own row before the
       review of it. Write the row the message names, then build this one again.
  3. Save the reply to a file and run `python3 "$O/skill_run_row.py" saved <run_id> <reply.json> --ledger "$LG"`: exit 0
     only when every item in `results` says `"ok": true`. Record the `run_id` in `observability.runs`.
- **If Orbit refuses the row**, read the error and fix it at once, changed only as needed: a duplicate `run_id` →
  build again without `run_id` (a new one is made); an error on `poc` (no such POC) → build again without `poc`;
  an error naming any other field → build again without that field.
- **Nothing is lost: the outbox.** A row whose `saved` check did not pass stays pending in the ledger. Before every
  write-back moment, at every gate decision and at the end of the run, run `python3 "$O/skill_run_row.py" pending
  --ledger "$LG"` and send each listed file again (then `saved`), until the list is empty. It never blocks or slows the
  run: no gate or skill waits for it, and it is not part of `failed_writes`.
- **Check against Orbit.** At every gate approval, on resume, and at the end of the run, read this POC's rows back
  (`get_records` on `orbit_studio_skill_run`, filter `poc` EQUAL the POC ID — one-off: `run_group` EQUAL the run's group —
  with enough `limit` for every row), save the reply, and run `skill_run_row.py reconcile <reply.json> --ledger "$LG"`:
  a row Orbit does not have goes back to pending and is sent again.
- **Report.** At the end of the run (and when the person asks), `skill_run_row.py report --ledger "$LG"` prints one line —
  "Observability: <n> runs logged, all saved in Orbit." — or names each row not saved and each re-run with no row.
  Put that line in the closing message as it is.
- It replaces nothing: the `gate_decided` Activity rows are still written at every gate (the view's approval lines
  come from them).

## When a write fails
- A reply with `"ok": false` or an error: read the message, fix the payload, and send **only the rows that failed**
  again (a create that succeeded must not be sent twice).
- `AUTH_EXPIRED` / signed out: ask the person to sign in again with `/ua:setup` in this folder, then resend.
- `CONFIRM_REQUIRED`: you sent something that deletes; you never should. Stop and tell the person.
- After three failures on one step, stop the write-back for this moment, tell the person in one line what did not
  reach Orbit, add it to `failed_writes` (with the gate and whether a notification was held back), and carry on with
  the run. They are retried at the start of the next moment (see "Before every moment"). **Never send slack_notification for a gate whose
  documents did not all save.**

## Never
- Create or delete POC rows, or delete any row.
- Write `manager_*` fields, `pinned`, `slack_channel_id`, `slack_thread_ts` (Orbit and its people own these).
- Send `slack_notification: true` outside moments 1 and 5, or at all in a Sonic run.
- Put a file's bytes or text in a row: upload it and save the link (no exceptions, the design system included).
- Write to any other object or tenant.
- Update or delete an `orbit_studio_skill_run` row (Moment 7 only creates them).
- Write assignee, due date, tags or analysis fields on a feedback ticket, or update or delete a ticket.

## Decisions (where this differs from `orbit-spec.md`)
1. G2 is pushed three times: the BRD as soon as scoping is done (with a notification), then the wireframes (with a
   notification), then the design system (with a notification); the stage stays `3_scope` until the design system
   moves it to `4_design_system`. G2 is approved with the design system. The wireframes are a `wireframes` document
   in the Plan phase (`orbit-spec.md` predates them).
2. G4 is written after the owner approves the collaterals in Claude.
3. The demo script is uploaded as a PDF (`file_kind pdf`); the "walkthrough video" is the demo video. The video is
   always put on Google Drive (any size) through Drive for desktop, in the company shared drive `POC Studio Video
   Library` (open to everyone through its `allemployees` membership; the person's own `POC Studio` folder is only the
   fallback), and its Drive link is its `file_link` (see "Video to Google Drive").
4. The POC ID is mandatory; there is no lookup by client slug.
5. No Orbit folder and no command-line script: reads, writes and uploads are UnifyApps Headless's tenant tools called directly in
   the session, and files are uploaded with `upload_public_file` (public links, owner-approved) instead of `upload_file`.
   One exception: files attached to a feedback ticket are uploaded with `orbit agent-builder upload_file` from the
   Orbit folder (signed-in links), as the `/feedback` section says.
6. Every client file found in discovery (Slack, Drive, Gmail, Calendar) is pushed as an input document at G1.
7. Every name/email field uses the POC owner's name and email from the POC record.
8. The design system is uploaded as a public `.html` file like every other document; no `content` or `format` is sent
   on any document row.
9. POC data policy: every file, client discovery files included, is uploaded as a public link without warning or asking
   (POCs use dummy data).

## Preview link rule (every app link POC Studio writes or records from)

An app is only ever recorded from, and saved to Orbit as, its **preview link**:
- a code app: `https://orbit.uat.unifyapps.com/agent-api/preview/b/<app id>/main`;
- a no-code app: `https://orbit.uat.unifyapps.com/p/0/interfaces/<app id>/preview`.

Given a published link (`*.matrix-uat.unifyapps.com`, `*.tensor-uat.unifyapps.com`) or a builder link, work out the
preview link from the app id in it. Without an id, ask for the preview link. Never save or record from a matrix link:
it needs a user to be created before it opens.

## One-off documents (`/poc-studio:<asset>` commands)

The standalone commands (`/poc-studio:requirements`, `brd`, `wireframes`, `design`, `app`, `collaterals`, run by
the `asset-run` skill) write **one-off documents**: rows in `orbit_studio_document` with `origin: "standalone"`, shown in
POC Build Loop under **Assets** (`https://poc-build-loop-orbit.tensor-uat.unifyapps.com/assets/<type-slug>`). This
section is the only place they are written from; `asset-run` calls it.

**A one-off run writes nothing else to Orbit** apart from its Observability rows (Moment 7, `origin: one_off`, no
`poc`). No Activity, no Iteration, no POC update, no `slack_notification`,
even when a POC ID was given: a one-off asset never moves a POC. The client files found by `requirements` are not
written as input rows either; only the Requirement Gathering document itself is written.

### The row (create only; afterwards update only `status`)

```json
{ "document_id": "SA-<client-slug>__<type-slug>__<usecase-slug>__v<N>",
  "origin": "standalone",
  "client_name": "<Client, as typed>",
  "use_case": "<Use case, as typed>",
  "poc": "<POC ID, only if one was given and verified; otherwise leave the key out>",
  "name": "<readable name, e.g. 'Acme — Invoice matching BRD'>",
  "type": "<requirements | brd | wireframes | design_system | app | demo_script | deck | video>",
  "stage": "<from the table below>",
  "gate_pack": "none",
  "version": <N>,
  "status": "in_review",
  "doc_role": "artifact",
  "file_link": "<public upload URL | Drive link | app preview link>",
  "file_kind": "<docx | pdf | pptx | html | video | link>",
  "file_name": "<e.g. 'Acme - BRD v2.docx'>",
  "summary": "<one or two lines on what it holds; for a new version, what changed>",
  "created_by": "<the person running the session>",
  "saved_at": <epoch ms from a one-line script> }
```

Slugs are lower case, with every run of non-letters/digits replaced by `-` and no `-` at the start or end (as
`client_slug` elsewhere): `[Test] Acme` → `test-acme`.

| type | type-slug (id and app URL) | stage | file_kind | file_link |
|---|---|---|---|---|
| requirements | `requirements` | `2_research_assess` | docx | `upload_public_file` URL |
| brd | `brd` | `3_scope` | docx | `upload_public_file` URL |
| wireframes | `wireframes` | `3_scope` | pdf | `upload_public_file` URL |
| design_system | `design-system` | `4_design_system` | html | `upload_public_file` URL (`text/html`; the same 20 MB rule as M1b) |
| app | `app` | `6_finalize` | link | the app's **preview link** (Preview link rule), never a matrix link |
| demo_script | `demo-script` | `7_collaterals` | pdf | `upload_public_file` URL |
| deck | `deck` | `7_collaterals` | pptx | `upload_public_file` URL |
| video | `video` | `7_collaterals` | video | Google Drive link via "Video to Google Drive" (shared drive `POC Studio Video Library`, file name `SA - <Client> - <Use case> - Demo video v<N>.mp4` in its root) |

Collaterals write one row per collateral delivered (up to three), in one `apply_record_edits` call.

**The one-off video** goes through "Video to Google Drive" with these differences: the file name is
`SA - <Client> - <Use case> - Demo video v<N>.mp4`, where N is the version from the lookup below (never a local
"next free v<N>"); it goes in the shared drive's **root**, with no `<POC ID> - <Client>` sub-folder (on the fallback
route, the root of the person's `POC Studio` folder); the connector finds it by that exact name in the drive root.

### How to write

The same tools and rules as every other write here: one ToolSearch for `get_records`, `apply_record_edits` and
`upload_public_file` (Setup § 1), host `orbit.uat.unifyapps.com`; never send `""` or `null` (leave the key out); check
every result is `"ok": true`. If the tenant tools are not in the session (UnifyApps Headless not installed, or this
folder not set up with `/ua:setup` on `orbit.uat.unifyapps.com`), treat it as a failed write (below) and say what to
run; the asset itself is still delivered.

**Version number (every write):**
1. Read the existing versions: `get_records` on `orbit_studio_document`, filter `document_id` `STARTS_WITH`
   `SA-<client-slug>__<type-slug>__<usecase-slug>__v`, fields `document_id, version, status`, limit 50 (keep each
   row's record id from the reply: the superseded updates need it). If
   `STARTS_WITH` is refused, filter `origin` EQUAL `standalone` and `type` EQUAL `<type>` (limit 200) and keep the ids
   with that prefix.
2. N = the highest `version` + 1, or 1 if there are none. Never trust only the local state: another person may have
   made a version from another laptop.
3. Upload the file (if the type has one).
4. One `apply_record_edits` call: `create` the new row with status `in_review`, and `update` (by record id, only
   `status`) every earlier version of the same id prefix whose status is not `superseded` to `superseded`.
5. Read the new row back by `document_id` and confirm it.

This covers a change asked at the chat gate and the same command run again later (another day, another person): both
make v(N+1), and the older version shows as superseded in the app's "older versions".

**The decision.** Approve → update the row's `status` to `approved` and read it back. Request changes → the next
version is written by the steps above when the reworked file is ready.

**Failures.** Three tries per write. Then tell the person in one line, keep the row (and file path) in `state.json` →
`standalone.failed_writes`, and retry it at the start of the next run of any `/poc-studio:<asset>` command in this
workspace. The local files are the deliverable either way: a failed Orbit write never stops the asset.

## /feedback — feedback tickets (`orbit_studio_feedback`, `orbit_studio_feedback_event`)

`/poc-studio:feedback <text>` files one piece of feedback as a **ticket** on POC Build Loop's Feedback page
(https://poc-build-loop-orbit.tensor-uat.unifyapps.com/feedback): how a POC or a one-off asset went, what the outputs
got wrong, what should change in POC Studio. It is **not** a change request on one document (that is an Iteration,
Moment 3, unchanged). Each ticket has its own ID (`FB-<Date.now()>`), a status, a priority and an activity history; people
triage it in the app (assignee, priority, status). Feedback does not feed the skill analysis: skill proposals are made
from iterations only. **A POC is optional.**

The plugin only **creates** tickets (and their `created` activity row) and **reads** them. It never updates or
deletes a ticket.

1. **Find the POC (optional).** Use the current workspace's POC ID: `state.json` → `orbit.poc_id` in the client
   workspace this session is working in (look for `*/*/state.json` under the current folder, or
   `./orbit-test/state.json`).
   - A one-off asset workspace (`state.json` → `standalone`) without a POC ID → file it with **no POC**, and do not
     ask (no `poc`, no `client_name`; the workspace slug goes in `channel_ref`).
   - No POC and no one-off runs in this session (or several POCs and it is not clear which) → ask once: "Which POC is
     this feedback for?", with the POCs found under this folder as options (show poc_id and client) and
     **"No POC (general)"**. A POC ID or client name typed in is accepted too.
   - A POC ID given or found → verify it and read `client_name` and `stage` with the `get_records` tool (Setup step 1
     loads it):
     `{"host":"https://orbit.uat.unifyapps.com","objectId":"orbit_studio_poc","filters":[{"field":"poc_id","op":"EQUAL","values":["<poc_id>"]}],"limit":1}`;
     if that filter shape is refused, use `"filter":{"poc_id":"<poc_id>"}`, and if that is refused too, fetch the row
     by its id (the record id equals the POC ID). By client name: filter `client_slug` EQUAL the client name
     lower-cased with every run of non-letters/digits replaced by `-`, `limit` 10; one row → use it, several → ask
     which.
   - Not found → ask once to correct it, or file without a POC.
2. **Attach files (optional).** The person can give files with their feedback: screenshots, logs, PDFs, files
   attached in the chat, or paths they mention. Take **at most 10**, each **at most 20 MB** (a larger one is skipped
   and named in the reply). For each file:
   1. Copy it into `$TMPDIR`, then upload it **from the Orbit folder** (`orbit-spec.md` § 1: the folder set up with
      `/ua:setup` on orbit.uat.unifyapps.com):
      `cp "<the file>" "$TMPDIR/"` then
      `orbit agent-builder upload_file '{"host":"orbit.uat.unifyapps.com","filePath":"'"$TMPDIR/<file name>"'","contentType":"<mime>"}'`
   2. The link is `https://orbit.uat.unifyapps.com` + the reply's `file.url`. It opens only for people signed in to
      orbit.uat.
   3. Keep one line per uploaded file, in the order given:
      - image (`png`, `jpg`, `jpeg`, `gif`, `webp`): `![<file name>](<link>)`
      - any other file: `[<file name>](<link>)`

   MIME types: png `image/png` · jpg/jpeg `image/jpeg` · gif `image/gif` · webp `image/webp` · pdf
   `application/pdf` · txt/log `text/plain` · csv `text/csv` · json `application/json` · docx, pptx, html, mp4 as in
   `orbit-spec.md`; anything else `application/octet-stream`.
   **If an upload fails**, still create the ticket without that file, and name the file in the reply. Never put a
   file's bytes or base64 in a row, and never put file lines in `quote`.
3. **Build the ticket and its `created` row with the builder, never by hand.** POC Build Loop finds and changes a
   ticket by `ticket_key`, so a ticket without it (or without `priority` and `updated_at`) cannot be moved or assigned
   in the app. Let `O` be this skill's `scripts/` folder
   (`find ~/.claude/plugins -path '*orbit-writeback/scripts/feedback_ticket.py' -exec dirname {} \; | head -1`).
   1. Write what you have, as one JSON object, to `$TMPDIR/fb/in.json` with a short script:
      `title` (the person's short title, or their first sentence), `feedback` (their words, unedited; several points
      in one message stay in one ticket), `given_by_name`, `given_by_email` (if known), `skill`, `quote` (their own
      exact short words worth keeping, if any), `channel_ref` (the workspace slug `<client-slug>/<usecase-slug>`, or
      the thread), `poc` and `client_name` **only when the ticket is about a verified POC**, `priority` only when the
      person clearly states one, and `attachments` (`[{"name", "link"}]` from step 2).
   2. `python3 "$O/feedback_ticket.py" build $TMPDIR/fb/in.json --out-dir $TMPDIR/fb` → prints `FB-<ms>` and writes
      `ticket.json` and `event.json`. Exit 2 → it names what is missing (title, feedback or given_by_name): ask for it
      once, then build again.
   The builder writes exactly this shape (and nothing else; it leaves out any field with no value, never `""` or `null`):

```json
{ "host": "https://orbit.uat.unifyapps.com", "objectId": "orbit_studio_feedback",
  "edits": [{ "op": "create", "properties": {
    "ticket_no": "FB-<ms>", "ticket_key": "FB-<ms>",
    "title": "<one line>", "feedback": "<full text, then a blank line and one line per attachment>",
    "status": "to_be_assigned", "priority": "none", "channel": "claude", "skill": "<skill key, or general>",
    "poc": "<poc_id: only for a POC>", "client_name": "<only with a POC>",
    "given_by_name": "<the person filing it>", "given_by_email": "<their email>",
    "quote": "<their own words>", "channel_ref": "<workspace slug or thread>",
    "created_at": <ms>, "updated_at": <the same ms> } }] }
```

   - `status` is always `to_be_assigned`. The field allows only `to_be_assigned`, `research`, `in_progress`,
     `blocked`, `in_qa`, `qa_rejected`, `done`; **never send** `open`, `incorporated`, `dismissed` or any other old
     value. Never send `source`, `poc_stage`, `gate`, `ticket_seq`, `assignee_*`, `due_date`, `tags`,
     `analysis_status`, `analysis_run_id`, `skill_proposal` or `incorporated_in_version`.
   - `given_by_name` / `given_by_email` are **the person giving the feedback**, not the POC owner: take them from the
     connected Slack profile of the session's user if there is one, else from `git config user.name` /
     `git config user.email`, else ask once.
   - `skill` is the POC Studio skill or agent the feedback is about, as its key. Choose it in this order:
     1. The person names a skill or stage in the feedback (or as an argument) → that key.
     2. Otherwise decide from the feedback text and this session:

        | Key | When |
        |---|---|
        | `requirement-gathering` | intake, the brief, client sources |
        | `scoping-l1-first` | the scoping / BRD document, L1 scope |
        | `wireframes` | the wireframes, page layouts, which components a page has |
        | `design-system` | palette, brand, components, the design system |
        | `poc-orchestrator` | how the run is driven, gates, the UnifyApps Headless build, app quality |
        | `asset-run` | the one-asset commands (`/poc-studio:requirements`, `brd`, `wireframes`, `design`, `app`, `collaterals`) |
        | `connector-discovery` | the client connection, the Integration Spec, the model tests and model recovery |
        | `platform-master` | Stage 4 pointers, the Zen question review, the Zen plan review, the browser fallback |
        | `poc-collateral-studio` | demo script, deck, video |
        | `orbit-writeback` | what shows in Orbit, statuses, links, Slack gate messages |
        | `ai-pm` | the AI PM's reviews, rulings, lessons |

     3. It could be several, or none fits clearly → `general`.
4. **Create the ticket:** send `ticket.json` as it is with `apply_record_edits`. Save the reply to
   `$TMPDIR/fb/reply.json` and run `python3 "$O/feedback_ticket.py" check $TMPDIR/fb/reply.json`: it passes only when
   every item in `results` says `"ok": true`.
   - **A `ticket_no` clash** (duplicate or unique-key error): `python3 "$O/feedback_ticket.py" retry $TMPDIR/fb`
     (now+1 for `ticket_no`, `ticket_key`, both times and the event) and send again, **at most 3 times**.
   - **Any other error, or still failing:** show the platform's error message in one line and what to do (e.g. run
     `/ua:setup` here on orbit.uat.unifyapps.com and sign in, then `/poc-studio:feedback` again). **Never say
     "Logged" for a write that failed.** A failed ticket is not retried later and not added to `failed_writes`.
5. **Create the activity row** right after, only once the ticket saved: send `event.json` as it is
   (`orbit_studio_feedback_event`, type `created`, the ticket's ms; its `ticket` field links to the ticket, so the
   ticket must exist first) and check the reply the same way. If only this row fails, keep the ticket and say so in
   one line ("Ticket saved; its activity row didn't: <error>").
6. **Read back** the ticket with `get_records` on `orbit_studio_feedback`, filter `ticket_key` EQUAL `FB-<ms>`, and
   confirm `ticket_key`, `priority` and `updated_at` are there.
7. **Reply in one line:**
   `Logged FB-<ms> (To be Assigned) → https://poc-build-loop-orbit.tensor-uat.unifyapps.com/feedback/FB-<ms>`
   Add ` · attached N files` when files were attached. Any file that could not be attached: one more short line
   naming it and why (too large, upload failed).
8. **Nothing else.** No Iteration row, no Activity row on the POC, no POC update, no `slack_notification`, no Slack
   message.

**This is the only place that creates a feedback ticket.** Any other step that files feedback on the person's behalf
follows these steps, with the builder.

### Ticket status

`/poc-studio:feedback status FB-<n>` (also `status <n>`, `fb <n>`, `FB-<n>` or just `<n>`, e.g. `FB-1793634938058`) is a **read only**; write nothing.
- Read the ticket: `get_records` on `orbit_studio_feedback`, filter `ticket_key` EQUAL `FB-<n>`, `limit` 1. Not found →
  say so in one line.
- Read its activity: `get_records` on `orbit_studio_feedback_event`, filter `ticket_key` EQUAL `FB-<n>`, sort
  `{field: "created_at", order: "DESC"}`, `limit` 5.
- Reply in 2–4 lines: the title; status (by its label); priority (by its label); the assignee (`assignee_name`, or
  "Unassigned"); the client or POC (or General); the newest activity line; and the link
  `https://poc-build-loop-orbit.tensor-uat.unifyapps.com/feedback/FB-<n>`.
- Status labels: `to_be_assigned` To be Assigned · `research` Research · `in_progress` In-Progress · `blocked`
  Blocked · `in_qa` In QA · `qa_rejected` QA Rejected · `done` Done. A missing status reads as To be Assigned.
- Priority labels: `urgent` Urgent · `high` High · `medium` Medium · `low` Low · `none` (or missing) No priority.

## Testing a moment by hand
When the person asks to test a write-back moment directly (e.g. "upload this file as the G2 BRD", "log this as a change
request on G1", "approve G3"), run just that moment as written above, with the file they attached or named and the
POC ID they give (verify it first with Setup step 2). Use the same ids, rows, order and checks as in a real run, keep
the run state in `./orbit-test/state.json` when there is no workspace, and after the moment read the rows back with
`get_records` (filter `poc` = the POC ID; for the POC row, `poc_id`) and show the person what Orbit now holds.
