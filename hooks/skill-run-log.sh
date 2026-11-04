#!/usr/bin/env bash
# POC Studio observability (orbit-writeback Moment 7). While a run is active (<project>/.poc-studio/observability
# exists, made by the orchestrator's Setup or a one-off run's start), note when each logged skill starts and remind
# the session to write its one orbit_studio_skill_run row when it returns. Notify only: never blocks a tool, always
# exits 0, writes nothing to Orbit itself.
#   PreToolUse  Skill|Agent : save the start time in .poc-studio/skill-starts/<skill>
#   PostToolUse Skill       : a stage skill was loaded and is starting: say so, with its start time
#   PostToolUse Agent       : an ai-pm review returned: write its row now, with the measured usage
{
  INPUT="$(cat)" || exit 0
  DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
  [ -f "$DIR/.poc-studio/observability" ] || exit 0
  command -v python3 >/dev/null 2>&1 || exit 0
  ROW="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)/skills/orbit-writeback/scripts/skill_run_row.py"
  HOOK_INPUT="$INPUT" OBS_DIR="$DIR/.poc-studio" ROW_PY="$ROW" python3 - <<'PY'
import json, os, subprocess, time
try: h = json.loads(os.environ["HOOK_INPUT"])
except Exception: raise SystemExit(0)
ev, tool, ti = h.get("hook_event_name", ""), h.get("tool_name", ""), h.get("tool_input") or {}
LOGGED = {"requirement-gathering", "connector-discovery", "scoping-l1-first", "wireframes", "design-system", "platform-master",
          "poc-collateral-studio", "research"}
if tool == "Skill":
    name = str(ti.get("skill", "")).split(":")[-1]
    skill = "unifyapps-headless" if str(ti.get("skill", "")) in ("ua:plan", "plan") else name
    if skill not in LOGGED and skill != "unifyapps-headless": raise SystemExit(0)
elif tool == "Agent":
    sub = str(ti.get("subagent_type", "")) + " " + str(ti.get("prompt", ""))[:400]
    if "ai-pm" not in sub: raise SystemExit(0)
    skill = "ai-pm"
else: raise SystemExit(0)
d = os.path.join(os.environ["OBS_DIR"], "skill-starts"); os.makedirs(d, exist_ok=True)
f = os.path.join(d, skill)
if ev == "PreToolUse":
    open(f, "w").write(str(int(time.time() * 1000))); raise SystemExit(0)
start = open(f).read().strip() if os.path.exists(f) else str(int(time.time() * 1000))
if tool == "Skill":
    msg = (f"POC Studio observability: `{skill}` is starting (started_at {start}, saved in .poc-studio/skill-starts/{skill}). "
           f"When this skill run returns, before the next step, write its one orbit_studio_skill_run row "
           f"(orbit-writeback Moment 7): build it with skill_run_row.py, then apply_record_edits.")
    if skill == "platform-master":
        msg += (" Exception: if this is job 1b · Question review (a Zen planning question), do not write a row now: write one "
                "row for the whole planning window when the plan is approved, with started_at = state.json → zen_planning_started_at.")
    if skill == "unifyapps-headless":
        msg = (f"POC Studio observability: the UnifyApps Headless build is starting (started_at {start}). Write its one "
               f"`unifyapps-headless` row (Moment 7) when the app is published, not now.")
else:
    msg = (f"POC Studio observability: an ai-pm review just returned (started_at {start}). If it was a review "
           f"(not a resolve answer, not INVALID_REQUEST), write its one orbit_studio_skill_run row now (orbit-writeback "
           f"Moment 7): verdict from its verdict file, reviews_run_id from observability.runs, round, and tokens_in / "
           f"tokens_out from this result's usage if it reports them. Build it with skill_run_row.py, then apply_record_edits.")
# The local ledger (skill_run_row.py): a re-run with no row, and rows that did not reach Orbit yet.
def ledger(*cmd):
    try:
        r = subprocess.run(["python3", os.environ["ROW_PY"], *cmd, "--ledger", os.environ["OBS_DIR"]],
                           capture_output=True, text=True, timeout=8)
        return [l for l in r.stdout.splitlines() if l.strip()]
    except Exception: return []
due, pend = ledger("rework-check"), ledger("pending")
if due:
    msg += (" Before this review's row: " + "; ".join(due) + ". Write that re-run's row first (Moment 7: round +1, label "
            "'<doc> v<N> · <k> fixes' or '· changes'); the builder refuses the review's row until it exists.")
if pend:
    msg += (f" {len(pend)} Observability row(s) are not saved in Orbit yet: send each file from `skill_run_row.py pending` "
            f"with apply_record_edits, then `skill_run_row.py saved <run_id> <reply>`.")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
PY
} 2>/dev/null
exit 0
