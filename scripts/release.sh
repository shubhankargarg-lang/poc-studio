#!/usr/bin/env bash
# Bump POC Studio to a new version (plugin.json and marketplace.json), then commit and push.
# Every change that reaches main needs a new version: that is how users' copies notice it.
# (Skill changes approved in Orbit get their patch bump from the 'Orbit · Commit skill with version bump' automation.)
# usage: scripts/release.sh 1.4.0 "what changed"
set -euo pipefail
NEW="$1"; MSG="${2:-Release $1}"
cd "$(dirname "$0")/.."
OLD="$(python3 -c 'import json;print(json.load(open(".claude-plugin/plugin.json"))["version"])')"
python3 - "$NEW" <<'PY'
import glob, json, re, sys
new = sys.argv[1]
p = ".claude-plugin/plugin.json"; d = json.load(open(p)); d["version"] = new
open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
p = ".claude-plugin/marketplace.json"; d = json.load(open(p))
for pl in d["plugins"]:
    if pl["name"] == "poc-studio": pl["version"] = new
open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
PY
echo "poc-studio $OLD -> $NEW"
git add -A && git commit -m "$MSG (v$NEW)" && git push origin HEAD:main
