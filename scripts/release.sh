#!/usr/bin/env bash
# Bump POC Studio to a new version everywhere the update check reads it, then commit and push.
# usage: scripts/release.sh 1.4.0 "what changed"
set -euo pipefail
NEW="$1"; MSG="${2:-Release $1}"
cd "$(dirname "$0")/.."
OLD="$(python3 -c 'import json;print(json.load(open(".claude-plugin/plugin.json"))["version"])')"
python3 - "$NEW" <<'PY'
import json, re, sys
new = sys.argv[1]
p = ".claude-plugin/plugin.json"; d = json.load(open(p)); d["version"] = new
open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
p = ".claude-plugin/marketplace.json"; d = json.load(open(p))
for pl in d["plugins"]:
    if pl["name"] == "poc-studio": pl["version"] = new
open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
p = "commands/start.md"; s = open(p).read()
s = re.sub(r'POC Studio v\d+\.\d+\.\d+', f'POC Studio v{new}', s)
s = re.sub(r'LOADED="\d+\.\d+\.\d+"', f'LOADED="{new}"', s)
s = re.sub(r'continuing on v\d+\.\d+\.\d+', f'continuing on v{new}', s)
open(p, "w").write(s)
PY
grep -c "$NEW" commands/start.md >/dev/null
echo "poc-studio $OLD -> $NEW"
git add -A && git commit -m "$MSG (v$NEW)" && git push origin HEAD:main
