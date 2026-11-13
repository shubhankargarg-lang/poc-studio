---
description: Update POC Studio to the latest version from GitHub (no git, no claude command needed), then restart
argument-hint: (no arguments)
---

Update POC Studio, say what happened in one or two lines, and tell the person how to restart. Ask no questions.
Show no file paths, JSON or tool names to the person.

Run with the Bash tool (it downloads with curl or Node, never Python's own HTTPS):

```bash
R="$(cat ~/.local/poc-studio/update/plugin_root 2>/dev/null)"
[ -f "$R/scripts/poc_update.py" ] || R="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/ 2>/dev/null | sort -V | tail -1)"
python3 "${R%/}/scripts/poc_update.py" install
```

Act on `status` in the JSON it prints:

- **`installed`** → "POC Studio <to> is installed (you were on <from>). Restart Claude Code to use it: type `/exit`,
  then open it again." If a POC run was in progress, add: "Then run the same command again; the run resumes where it
  stopped."
- **`current`** → "POC Studio is already on the latest version (<installed>)." If the person was blocked by the version
  check in this session, add: "Restart Claude Code (type `/exit`, then open it again) to load it."
- **`error`** → "POC Studio could not update: <error>." Then: if the error is about reaching GitHub, ask them to check the
  internet connection or VPN and try again; otherwise ask them to reinstall once with the two install commands in the
  README (`/plugin marketplace add shubhankargarg-lang/poc-studio`, then `/plugin install poc-studio@unifyapps-poc`).
  Do not retry in a loop.
