---
description: File feedback as a ticket in POC Build Loop (FB-<n>) — about a POC, a one-off asset or POC Studio in general — or check a ticket's status
argument-hint: [status FB-<n>] | [skill or stage] <your feedback> [files]
---

Feedback for POC Studio: **$ARGUMENTS**

Every piece of feedback becomes a ticket (`FB-<n>`) on POC Build Loop's Feedback page
(https://poc-build-loop-orbit.tensor-uat.unifyapps.com/feedback), where people triage it (assignee, priority, status).
It is not a change request on one document (a change request on a document stays an Iteration, written by the
orbit-writeback skill at that gate). A POC is optional: feedback from a one-off asset run, or about POC Studio in
general, is filed too.

## Step 0 — make sure this is the latest POC Studio (always first)

POC Studio keeps itself current: a hook checks GitHub when the session starts and again before every stage, installs a
newer version on its own, and blocks a new stage until the person restarts on the latest version. Run this check once
now with the Bash tool (it uses curl or Node, never Python's own HTTPS):

```bash
R="$(cat ~/.local/poc-studio/update/plugin_root 2>/dev/null)"
[ -f "$R/scripts/poc_update.py" ] || R="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/ 2>/dev/null | sort -V | tail -1)"
python3 "${R%/}/scripts/poc_update.py" check
```

Act on `status` in the JSON it prints:

- **`current`** → carry on.
- **`outdated`** → run `python3 "${R%/}/scripts/poc_update.py" install`. On `"status": "installed"`, **stop here** and
  tell the person in two lines: "POC Studio <to> is installed. Restart Claude Code (type `/exit`, then open it again)
  and run the same command again: `/poc-studio:feedback $ARGUMENTS`". On `"status": "error"`, stop and show them its `error` in one line.
- **`unreachable`** → stop. Tell the person in one line that POC Studio could not check for updates because GitHub
  could not be reached (show `error`), to check the internet connection or VPN, and to run the same command again.

If a tool call is ever refused with a reason that starts `POC_STUDIO_UPDATE:`, tell the person what it says and stop.
Never work around the version check.

## Step 1 — file or read the ticket

1. **Status check.** If the text above is `status FB-<n>`, `status <n>`, `fb <n>`, `FB-<n>` or just a number, it is a
   read only: load the `orbit-writeback` skill (Skill tool: `poc-studio:orbit-writeback`), follow its
   **Ticket status** subsection under `/feedback`, and stop. Write nothing.
2. If no feedback text was given above, ask for it in one short question ("What feedback should I file?") and wait.
3. Load the `orbit-writeback` skill (Skill tool: `poc-studio:orbit-writeback`) and follow its **`/feedback`** section
   exactly. It uses the same UnifyApps Headless tenant tools and the same write rules as every other Orbit write: one
   ticket on `orbit_studio_feedback`, built with its `feedback_ticket.py` builder (full shape: `ticket_key` =
   `ticket_no`, status `to_be_assigned`, priority `none`, `updated_at` = `created_at`), then one `created` row on
   `orbit_studio_feedback_event`. Files the person gives with the feedback (screenshots, logs, PDFs; at most 10, each
   at most 20 MB) are uploaded and added as one link line each at the end of the feedback text, as that section says.
4. The ticket carries a `skill` field: the skill or agent the feedback is about (named by the person, or decided from
   the text and this session), or `general` when it could be several or none fits — as the `/feedback` section says.
5. **Reply in one line:**
   `Logged FB-<timestamp> (To be Assigned) → https://poc-build-loop-orbit.tensor-uat.unifyapps.com/feedback/FB-<timestamp>`
   Add ` · attached N files` when files were attached, and name any file that could not be attached. Only after
   every item of the write's reply says `"ok": true`: if the ticket write fails, show the platform's error in one
   line and what to do, and never say "Logged".
6. **Nothing else.** No Iteration row, no Activity row on the POC, no POC update, no `slack_notification`, no Slack
   message: feedback does not move a POC. Never set an assignee, due date, tags or analysis fields, and never update
   or delete a ticket; people do that in the app.
