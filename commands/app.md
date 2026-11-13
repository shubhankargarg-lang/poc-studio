---
description: Build one UnifyApps app with UnifyApps Headless from a BRD, on its own (no POC needed)
argument-hint: <Client> | <Use case> [| <POC ID>]
---

Make **the app (Orbit type `app`, saved as its preview link)** on its own, without a POC and without the other stages: **$ARGUMENTS**

The arguments are `<Client> | <Use case> [| <POC ID>]`. The POC ID is optional; without it the asset is made all the same.

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

- **`UP_TO_DATE`** → carry on with the run below.
- **`UPDATED <old> -> <new>`** → the new version is on disk, but this session is still running the old one, and only
  the person can switch it. **Stop here and do not start the run.** Tell the person, in two lines:
  "POC Studio was updated from <old> to <new>. Type `/reload-plugins`, then run the same command again:
  `/poc-studio:app $ARGUMENTS`".
- **`UPDATE_FAILED` or `UPDATE_CHECK_FAILED`** (the update could not run, or GitHub could not be reached, for example
  an SSL error) → **stop here; do not continue on this version.** Tell the person, in these words, then wait:
  "POC Studio could not update itself. Please reinstall it (2 minutes):
  1. Type `/plugin` and press Enter.
  2. Click the **+** (Add) button at the top right.
  3. Choose **Manage marketplaces**.
  4. Next to **unifyapps-poc**, click **Remove marketplace**.
  5. Click **Add marketplace** and enter `shubhankargarg-lang/poc-studio`.
  6. Find **POC Studio** and click **Add to computer**.
  7. Open a **new chat** and run: `/poc-studio:app $ARGUMENTS`"
  Only if the person says they have already done these steps and the check still fails, carry on, and say in one
  line which version you are continuing on.

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
