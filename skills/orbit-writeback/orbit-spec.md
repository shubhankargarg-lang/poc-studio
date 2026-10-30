Orbit write-back — instructions for the POC Studio orchestrator
Paste this whole section into the orchestration skill (or keep it as a reference file the skill loads before every gate). It tells the session exactly what to write to Orbit · POC Studio on the orbit.uat tenant, at which moment, in which object, with which keys.

Your job
While you run a POC build, you keep Orbit · POC Studio (tenant orbit.uat.unifyapps.com) in step with the build. Orbit is read by the POC owner, their team and a Slack bot. You write to it at exactly six moments, listed in When to write. You never write anything else, never delete a row, and never write to any other object or tenant.

All writes go through UnifyApps Headless's tenant tools, called by a terminal command (so file bytes never pass through this chat). If a write fails, see When a write fails; never skip a step silently.

Setup (once per run)
1. The Orbit folder
Every Orbit command runs from the Orbit folder: a folder set up with /ua:setup on orbit.uat.unifyapps.com, solution POC Studio. Its path is the plugin setting orbit_folder. If it is missing or not set up, stop and ask the person to run /ua:setup there once; do not write from the client's build folder (it may point at another tenant).

Define, for every command below:

ORBIT_DIR="<orbit_folder>"
UA="$(ls -d ~/.claude/plugins/cache/unifyapps-headless/ua/*/ | sort -V | tail -1)scripts"
orbit() { (cd "$ORBIT_DIR" && node "$UA/tool-calls.mjs" "$@"); }
2. The POC id
The build starts with /poc-studio:start <Client> | <Use case> | <poc_id>.

Third part present → that is poc_id.
Missing → find it:
orbit object get_records '{"host":"https://orbit.uat.unifyapps.com","objectId":"orbit_studio_poc","filters":[{"field":"client_slug","op":"EQUAL","values":["<client-slug>"]},{"field":"status","op":"NOT_IN","values":["stopped","demo_ready"]}],"fields":["poc_id","use_case","stage","current_gate"],"limit":10}'
client-slug = client name lower-cased, every run of non-letters/digits replaced by -. One row whose use_case matches → use its poc_id. Several → ask the person which. None → ask the person for the POC id (the row is created from Slack or the Orbit app; you do not create it).
Save poc_id in the run state (the workspace file) under orbit.poc_id. Every later write uses it.

3. Run state you keep
orbit:
  poc_id: POC-acme-20261018
  documents:            # every document you wrote, by gate
    g1: [{ document_id: …, type: requirements, version: 1, status: in_review }]
  open_iterations:      # iteration rows waiting for a new version
    - { iteration_id: …, gate: g2, document_id: … }
How to write
Create or update rows — apply_record_edits
Write the payload to a temp file with a script (never type base64 or long text into a command line), then:

orbit object apply_record_edits @"$TMPDIR/orbit-write.json"
Payload:

{
  "host": "https://orbit.uat.unifyapps.com",
  "objectId": "<object id>",
  "edits": [
    { "op": "create", "properties": { … } },
    { "op": "update", "recordId": "<record id>", "properties": { … only the keys that change … } }
  ]
}
Rules:

One call per object; put all rows of that object in one edits list.
update merges into the stored row: send only the keys you change. Never send a row back whole.
Never send "" or null: leave the key out.
Dates are epoch milliseconds (Date.now()).
Check the reply: every item in results must say "ok": true.
Upload a file — upload_file
cp "<the file>" "$TMPDIR/"     # the file must be in the Orbit folder or a temp folder
orbit agent-builder upload_file '{"host":"orbit.uat.unifyapps.com","filePath":"'"$TMPDIR/<file name>"'","contentType":"<mime>"}'
Save the link as https://orbit.uat.unifyapps.com + the reply's file.url. It opens only for people signed in to orbit.uat; it is never public.
At most 20 MB. A larger file (usually the walkthrough video): compress it under 20 MB; if that is not possible, ask the person for a link to it and save that instead.
MIME types: docx application/vnd.openxmlformats-officedocument.wordprocessingml.document · pptx application/vnd.openxmlformats-officedocument.presentationml.presentation · html text/html · pdf application/pdf · mp4 video/mp4.
Ids you make
Row	Id
Document	<poc_id>__<stage>__<slug>__v<N> e.g. POC-acme-20261018__3_scope__brd__v2
Activity	ACT-<Date.now()>-<4 random digits>
Iteration	IT-<poc_id>-<Date.now()>
slug is the document type (requirements, brd, design-system, app, demo-script, deck, video) or, for a Slack asset, slack-<short name>.

The rows
Document — object orbit_studio_document (create; update only status)
{
  "document_id": "<id>",
  "poc": "<poc_id>",
  "name": "BRD",
  "type": "brd",
  "stage": "3_scope",
  "gate_pack": "g2",
  "version": 1,
  "status": "in_review",
  "doc_role": "artifact",
  "format": "link",
  "file_link": "https://orbit.uat.unifyapps.com/api/file/download/…",
  "file_kind": "docx",
  "file_name": "Acme - BRD v1.docx",
  "summary": "One or two lines on what the document holds.",
  "created_by": "<person running the session>",
  "saved_at": 1792280000000
}
type: slack · requirements · brd · design_system · app · demo_script · deck · video
status: in_review (its gate is waiting) · approved (gate passed) · final (inputs and Deliver files) · superseded (an older version)
doc_role: artifact (you made it) · input (found, e.g. in Slack)
file_kind: docx · pptx · html · pdf · video · image · link · other
Design system only: also "format": "html" and "content": "<the whole HTML>", so it renders in the app.
A re-iterated version also sends "from_iteration": "<iteration_id>".
Activity — object orbit_studio_activity (create only)
{
  "activity_id": "ACT-…",
  "poc": "<poc_id>",
  "type": "document_saved",
  "stage": "3_scope",
  "gate": "g2",
  "actor_type": "ai",
  "actor_name": "Claude",
  "message": "BRD v1 saved",
  "related_document": "<document_id>",
  "created_at": 1792280000000
}
type: input_added · document_saved · gate_posted · gate_decided (with decision: approve · request_changes) · iteration_logged · stage_completed. For the person's own action use "actor_type": "person", their name and actor_email.

Iteration — object orbit_studio_iteration (create; then update to close)
{
  "iteration_id": "IT-…",
  "poc": "<poc_id>",
  "phase": "plan",
  "source": "person",
  "status": "open",
  "actor_name": "<person>",
  "actor_email": "<their email>",
  "title": "BRD: add the approval matrix",
  "reason": "<the person's own words, as they said them>",
  "related_document": "<document_id of the version they rejected>",
  "skill": "<the POC Studio skill that made the document>",
  "created_at": 1792280000000
}
phase: understand (G1) · plan (G2) · build (G3) · deliver (G4).

POC — object orbit_studio_poc (update only, recordId = poc_id)
Every POC update also sends last_activity (one plain line people read) and last_activity_at. slack_notification: true is sent only in the last call of a gate push (moments 1 and 5). It makes Orbit post the gate to the POC's Slack thread; Orbit clears it itself.

When to write
Order inside every moment: upload files → Documents → Iteration → Activity → POC last.

Moment 1 — a gate is ready for review (G1, G2, G3) or Deliver is finished (G4)
G1 Understand	G2 Plan	G3 Build	G4 Deliver
Upload	RG .docx; Slack files you downloaded	BRD .docx; Design system .html	—	Demo script .docx; Deck .pptx; Walkthrough video
Documents (create)	each Slack asset: type slack, doc_role input, stage 1_signal_capture, status final, file_link = uploaded URL or Slack permalink, file_kind link for a permalink · RG: type requirements, stage 2_research_assess, file_kind docx	BRD: type brd, stage 3_scope, file_kind docx · Design system: type design_system, stage 4_design_system, format html, content, file_kind html	App: type app, stage 6_finalize, file_link = the app's live URL, file_kind link, name = app name	Script type demo_script · Deck type deck · Video type video; all stage 7_collaterals, status final
gate_pack	g1	g2	g3	g4
status	in_review (Slack inputs final)	in_review	in_review	final
Activity (create)	input_added per Slack asset; document_saved per doc; gate_posted gate g1	document_saved ×2; gate_posted gate g2	document_saved; gate_posted gate g3	document_saved ×3; stage_completed gate g4, message Deliver complete: demo-ready
POC (update)	stage 2_research_assess, current_gate g1, g1_status waiting, status waiting, g1_summary, gate_summary, slack_notification true	stage 4_design_system, current_gate g2, g2_status waiting, status waiting, g2_summary, gate_summary, slack_notification true	stage 6_finalize, current_gate g3, g3_status waiting, status waiting, g3_summary, gate_summary, solution_id (the UnifyApps Headless solution e_… the build made), slack_notification true	stage 8_demo_ready, current_gate none, g4_status approved, status demo_ready, g4_summary, slack_notification true
gN_summary / gate_summary: 2–4 plain sentences on what the phase produced and what the person should check. Record every new document_id in the run state.

Moment 2 — the owner approves a gate in Claude (G1, G2, G3)
Documents (update): each in_review document of that gate → "status": "approved".
Activity (create): gate_decided, gate gN, decision approve, actor_type person, the owner's name and email.
POC (update): gN_owner_approved true, gN_status approved, current_gate none, stage = G1 → 3_scope · G2 → 5_build · G3 → 7_collaterals, status running. No slack_notification.
Moment 3 — the owner asks for changes instead of approving
Iteration (create): as above, status open, phase of the gate, reason = their exact words, related_document = the version they rejected. Add it to open_iterations in the run state.
Activity (create): iteration_logged · gate_decided, gate gN, decision request_changes, actor_type person.
POC (update): gN_status changes_requested, current_gate none, status running, last_activity (e.g. "Changes asked on the BRD"). No slack_notification.
Moment 4 — while reworking (optional)
When you move to another stage inside a phase, POC (update): stage, status running, last_activity. No documents, no slack_notification.

Moment 5 — the re-iterated document is ready
Upload the new file.
Documents: update the rejected version → "status": "superseded"; create the new version with version N+1, document_id …__v<N+1>, status in_review, from_iteration <iteration_id>, summary saying what changed.
Iteration (update <iteration_id>): status done, resolved_document = the new document_id, resolved_at now. Remove it from open_iterations.
Activity (create): document_saved · gate_posted, gate gN.
POC (update): current_gate gN, gN_status waiting, status waiting, gN_summary (what changed), slack_notification true.
Then wait for Moment 2 or Moment 3 again.

Moment 6 — the build stops or is blocked
POC (update): status blocked with blocked_on (one line: what is needed), or status stopped. When it resumes: status running and a new last_activity. No slack_notification.

When a write fails
A reply with "ok": false or an error: read the message, fix the payload, and send only the rows that failed again (a create that succeeded must not be sent twice).
AUTH_EXPIRED / signed out: ask the person to sign in again with /ua:setup in the Orbit folder, then resend.
CONFIRM_REQUIRED: you sent something that deletes; you never should. Stop and tell the person.
After three failures on one step, stop the write-back for this moment, tell the person in one line what did not reach Orbit, and carry on with the build. Never send slack_notification for a gate whose documents did not all save.
Never
Create or delete POC rows, or delete any row.
Write manager_* fields, pinned, slack_channel_id, slack_thread_ts (Orbit and its people own these).
Send slack_notification: true outside Moments 1 and 5.
Put a file's bytes in a row; upload it and save the link.