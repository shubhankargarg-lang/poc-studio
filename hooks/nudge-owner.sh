#!/usr/bin/env bash
# POC Studio: when a question waits on the person (AskUserQuestion), nudge the POC owner in the POC's Slack thread
# through an Orbit workflow. Notify only: never blocks or changes the question, prints nothing, always exits 0.
# Skipped while .poc-studio/autopilot exists (route-questions.sh sends those questions to the reviewer).
{
  NUDGE_URL="${ORBIT_NUDGE_URL:-https://orbit.uat.unifyapps.com/api-endpoint/trigger-workflow/6ad587d60b01177697d38daa}"
  NUDGE_KEY="${ORBIT_NUDGE_KEY:-onk_ca271da89e044c7a0b22a7954df44c90b30519444281c0fe}"
  [ -n "$NUDGE_URL" ] && [ -n "$NUDGE_KEY" ] || exit 0
  command -v curl >/dev/null 2>&1 || exit 0

  INPUT="$(cat)" || exit 0
  DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
  [ -e "$DIR/.poc-studio/autopilot" ] && exit 0

  # every candidate run state, newest first; the parser keeps the first one that has orbit.poc_id
  STATES="$(ls -t "$DIR"/*/*/state.json "$DIR"/orbit-test/state.json 2>/dev/null)"
  [ -n "$STATES" ] || exit 0
  SESSION="$(basename "$DIR") on $(hostname -s 2>/dev/null || hostname 2>/dev/null)"

  if command -v python3 >/dev/null 2>&1; then
    BODY="$(HOOK_INPUT="$INPUT" STATES="$STATES" SESSION="$SESSION" python3 -c '
import json, os, sys
poc = None
for p in os.environ["STATES"].splitlines():
    try:
        poc = (json.load(open(p)).get("orbit") or {}).get("poc_id")
    except Exception:
        poc = None
    if poc: break
if not poc: sys.exit(0)
qs = (json.loads(os.environ["HOOK_INPUT"]).get("tool_input") or {}).get("questions") or []
if not qs: sys.exit(0)
first = qs[0] or {}
print(json.dumps({
    "poc_id": poc,
    "question": "\n\n".join(str(q.get("question", "")) for q in qs if q),
    "options": [str(o.get("label", "")) for o in (first.get("options") or []) if isinstance(o, dict)],
    "header": str(first.get("header", "")),
    "session": os.environ["SESSION"],
}))
')"
  elif command -v node >/dev/null 2>&1; then
    BODY="$(HOOK_INPUT="$INPUT" STATES="$STATES" SESSION="$SESSION" node -e '
const fs = require("fs"); const env = process.env;
let poc = null;
for (const p of env.STATES.split("\n")) {
  try { poc = (JSON.parse(fs.readFileSync(p, "utf8")).orbit || {}).poc_id || null; } catch { poc = null; }
  if (poc) break;
}
if (!poc) process.exit(0);
const qs = ((JSON.parse(env.HOOK_INPUT).tool_input || {}).questions) || [];
if (!qs.length) process.exit(0);
const first = qs[0] || {};
console.log(JSON.stringify({
  poc_id: poc,
  question: qs.filter(Boolean).map((q) => String(q.question ?? "")).join("\n\n"),
  options: (first.options || []).filter((o) => o && typeof o === "object").map((o) => String(o.label ?? "")),
  header: String(first.header ?? ""),
  session: env.SESSION,
}));
')"
  else
    exit 0
  fi
  [ -n "$BODY" ] || exit 0

  ( curl -sS -m 5 -X POST "$NUDGE_URL" -H 'Content-Type: application/json' -H "X-Orbit-Nudge-Key: $NUDGE_KEY" \
      --data-binary @- >/dev/null 2>&1 <<<"$BODY" ) &
} >/dev/null 2>&1
exit 0
