---
description: Make the demo collaterals for a built app — demo script, deck, video, or any of them — on their own (no POC needed)
argument-hint: <Client> | <Use case> | <App preview link> [| <POC ID>]
---

Make **the collaterals the person chooses (Orbit types `demo_script`, `deck`, `video`; one row each)** on its own, without a POC and without the other stages: **$ARGUMENTS**

The arguments are `<Client> | <Use case> | <App preview link> [| <POC ID>]`. The POC ID is optional; without it the asset is made all the same.

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
  and run the same command again: `/poc-studio:collaterals $ARGUMENTS`". On `"status": "error"`, stop and show them its `error` in one line.
- **`unreachable`** → stop. Tell the person in one line that POC Studio could not check for updates because GitHub
  could not be reached (show `error`), to check the internet connection or VPN, and to run the same command again.

If a tool call is ever refused with a reason that starts `POC_STUDIO_UPDATE:`, tell the person what it says and stop.
Never work around the version check.

## Step 1 — prerequisites (asked in the chat, before anything runs)

Load the `asset-run` skill (Skill tool: `poc-studio:asset-run`) and follow its **1 · Prerequisites** for the asset
**`collaterals`**: take each prerequisite from the arguments, then from an existing workspace for this client and use case
(offer what you find in one line; in a chain from "Approve and make <next asset>", the asset just approved is used without an offer), then ask for everything still missing in **one** question. Never ask for a password.

- **Required:** Client name · Use case · which collaterals (always asked — demo script, deck, video: any one, two or all three — unless the command already says which, e.g. `deck only` after the preview link) · the app's preview link (a published or builder link is turned into the preview link) · a valid Orbit sign-in · the collateral tools for the ones chosen.
- **Optional** (asked once, in the same question; the run goes on without it): A BRD or scoping document (strongly recommended: it drives the story and personas) · a Requirement Gathering document · the audience (business, technical or mixed).
- **If something required is missing:** Ask for what is missing; the person signs in to Orbit themselves in the window that opens.

If a POC ID was given, verify it as `asset-run` § 1 describes (found → the Orbit row carries it; not found → ask once to
correct it or drop it).

## Step 2 — make the asset

Only once every required prerequisite is in hand, continue with `asset-run` §§ 2–6 for **`collaterals`**: the workspace and
run state, the stage run unattended (questions go to the AI PM), the AI PM review, the Orbit write as a one-off
document (a new version every time), the result in the chat, and the approval.
