---
description: Start (or resume) a UnifyApps POC for a client use case — requirement gathering → connector discovery → scoping → wireframes → design system → UnifyApps Headless build → collaterals
argument-hint: <client name> | <use case name> | <POC ID>
---

Run the POC Studio pipeline for: **$ARGUMENTS**

The arguments are `<client name> | <use case name> | <POC ID>` (e.g. `Acme | Invoice matching | POC-acme-20261018`).
**All three are required. Do not start the run until a POC ID has been given** (format `POC-<client>-<YYYYMMDD>`).

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
  and run the same command again: `/poc-studio:start $ARGUMENTS`". On `"status": "error"`, stop and show them its `error` in one line.
- **`unreachable`** → stop. Tell the person in one line that POC Studio could not check for updates because GitHub
  could not be reached (show `error`), to check the internet connection or VPN, and to run the same command again.

If a tool call is ever refused with a reason that starts `POC_STUDIO_UPDATE:`, tell the person what it says and stop.
Never work around the version check.

## Step 1 — verify the POC ID in Orbit (after the update check, before anything else)

Only once Step 0 has finished and the POC ID has been given:

1. Load the `orbit-writeback` skill (Skill tool: `poc-studio:orbit-writeback`) and run its **Setup**: load UnifyApps Headless's
   tenant tools, then call `get_records` on the object **`orbit_studio_poc`** on Orbit UAT
   (`https://orbit.uat.unifyapps.com`), **filtered on `poc_id` EQUAL the POC ID given above**.
2. **Found** → keep the record id and the POC owner's name and email (they go in `state.json` → `orbit` once the
   workspace exists), and go on to Step 2.
3. **Not found** → **stop.** Tell the person: "POC ID `<POC ID>` was not found in Orbit (`orbit_studio_poc`). Please
   check the POC ID and send the correct one." Wait for their reply, then run this check again with the new ID.
   Do not start the pipeline until the check finds the record.
4. **The check cannot run** (UnifyApps Headless not installed, not set up in this folder, or Orbit needs a sign-in) → stop and
   tell the person what is needed (install UnifyApps Headless, or run `/ua:setup` here on `orbit.uat.unifyapps.com` and sign in
   themselves — never type a password), then run the check again. Never skip it.

## Step 2 — choose the run mode (once the POC ID is verified)

Ask with AskUserQuestion, one question, before anything runs: **"Which mode for this POC run?"**
- **Zen** — the AI PM reviews every stage, and you approve each gate (and Zen planning's build plan in Stage 4).
- **Sonic** — the AI PM reviews every stage and approves it; the run moves on by itself. You are asked only for what
  the run cannot pass without you (sign-ins, deletes and other `CONFIRM_REQUIRED` steps, credentials, a block the AI
  PM cannot clear, a Not ready requirement-gathering verdict, client-system connection and access questions, the
  replacement model when one runs out of credits).

Pass the answer to the orchestrator; it keeps it in `state.json` → `mode` (its "Run mode" section). **Resuming** a run
that already has a mode: do not ask again; say the mode in the resume line, and switch only if the person asks.

## Step 3 — run the pipeline

Load the `poc-orchestrator` skill from this plugin (Skill tool: `poc-studio:poc-orchestrator`) and follow it exactly,
starting with Setup. If the client name, the use case name or the POC ID is missing above, ask once for the missing
values and **wait**; nothing starts without the POC ID. If a workspace for this client and use case already exists in
the current folder with the same POC ID, resume from its `state.json`.
