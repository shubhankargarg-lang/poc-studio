---
description: Build one UnifyApps app with UnifyApps Headless from a BRD, on its own (no POC needed)
argument-hint: <Client> | <Use case> [| <POC ID>]
---

Make **the app (Orbit type `app`, saved as its preview link)** on its own, without a POC and without the other stages: **$ARGUMENTS**

The arguments are `<Client> | <Use case> [| <POC ID>]`. The POC ID is optional; without it the asset is made all the same.

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
  and run the same command again: `/poc-studio:app $ARGUMENTS`". On `"status": "error"`, stop and show them its `error` in one line.
- **`unreachable`** → stop. Tell the person in one line that POC Studio could not check for updates because GitHub
  could not be reached (show `error`), to check the internet connection or VPN, and to run the same command again.

If a tool call is ever refused with a reason that starts `POC_STUDIO_UPDATE:`, tell the person what it says and stop.
Never work around the version check.

## Step 1 — prerequisites (asked in the chat, before anything runs)

Load the `asset-run` skill (Skill tool: `poc-studio:asset-run`) and follow its **1 · Prerequisites** for the asset
**`app`**: take each prerequisite from the arguments, then from an existing workspace for this client and use case
(offer what you find in one line; in a chain from "Approve and make <next asset>", the asset just approved is used without an offer), then ask for everything still missing in **one** question. Never ask for a password.

- **Required:** Client name · Use case · a BRD or scoping document · the UnifyApps Headless plugin (`ua`) installed and this folder set up on `orbit.uat.unifyapps.com` (`/ua:setup`) · the collateral tools (Playwright, for the AI PM's browser check before publish) and a valid Orbit sign-in · not a folder whose UnifyApps Headless setup belongs to a pipeline run (if it is, ask once: a separate folder is recommended).
- **Optional** (asked once, in the same question; the run goes on without it): Approved wireframes (from this folder) · A design system HTML (without one, say the build uses UnifyApps Headless's default look, and offer `/poc-studio:design` first).
- **If something required is missing:** Plugin or setup missing: tell the person what to install or run, then check again.

If a POC ID was given, verify it as `asset-run` § 1 describes (found → the Orbit row carries it; not found → ask once to
correct it or drop it).

## Step 2 — make the asset

Only once every required prerequisite is in hand, continue with `asset-run` §§ 2–6 for **`app`**: the workspace and
run state, the stage run unattended (questions go to the AI PM), the AI PM review, the Orbit write as a one-off
document (a new version every time), the result in the chat, and the approval.
