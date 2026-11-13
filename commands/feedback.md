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

This command was loaded from **POC Studio v1.42.3**. Before anything else, run this check with the Bash tool:

```bash
LOADED="1.42.3"
python3 - "$LOADED" <<'PY'
import json, subprocess, sys, urllib.request
loaded = sys.argv[1]
url = "https://raw.githubusercontent.com/shubhankargarg-lang/poc-studio/main/.claude-plugin/plugin.json"
try:
    latest = json.load(urllib.request.urlopen(url, timeout=10))["version"]
except Exception as e:
    print(f"UPDATE_CHECK_FAILED {e}"); sys.exit(0)
v = lambda s: tuple(int(x) for x in s.split("."))
if v(latest) <= v(loaded):
    print(f"UP_TO_DATE {loaded}"); sys.exit(0)
def run(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("$", " ".join(cmd)); print((r.stdout + r.stderr).strip()); return r.returncode
ok = run("claude", "plugin", "marketplace", "update", "unifyapps-poc") == 0
for scope in ("user", "project", "local"):
    if ok and run("claude", "plugin", "update", "poc-studio@unifyapps-poc", "-s", scope) == 0:
        print(f"UPDATED {loaded} -> {latest}"); sys.exit(0)
print(f"UPDATE_FAILED {loaded} -> {latest}")
PY
```

Then act on the last line it printed:

- **`UP_TO_DATE`** → carry on below.
- **`UPDATED <old> -> <new>`** → the new version is on disk, but this session is still running the old one, and only
  the person can switch it. **Stop here and do not file the ticket.** Tell the person, in two lines:
  "POC Studio was updated from <old> to <new>. Type `/reload-plugins`, then run the same command again:
  `/poc-studio:feedback $ARGUMENTS`".
- **`UPDATE_FAILED` or `UPDATE_CHECK_FAILED`** (the update could not run, or GitHub could not be reached, for example
  an SSL error) → **stop here; do not continue on this version.** Tell the person, in these words, then wait:
  "POC Studio could not check for or install updates on this Mac. Please reinstall it once, in this order:
  1. `/plugin marketplace remove unifyapps-poc`
  2. `/plugin marketplace add shubhankargarg-lang/poc-studio`
  3. `/plugin install poc-studio@unifyapps-poc`
  4. `/reload-plugins`
  Then run the same command again: `/poc-studio:feedback $ARGUMENTS`.
  (If `/plugin` lists the POC Studio marketplace under another name, use that name in step 1.)"
  Only if the person says they have already done these steps and the check still fails, carry on, and say in one
  line which version you are continuing on.

An old version files tickets in a shape POC Build Loop cannot move or assign, so never file with an older
version than the latest published one. A status check (`status FB-<n>`) is a read and may go ahead.

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
