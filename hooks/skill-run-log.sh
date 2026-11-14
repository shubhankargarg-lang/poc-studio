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
try:  # this chat's log file, for the orchestrator's own rows (session_log.py slice poc-orchestrator)
    if h.get("transcript_path"):
        os.makedirs(os.path.join(os.environ["OBS_DIR"], "session-logs"), exist_ok=True)
        open(os.path.join(os.environ["OBS_DIR"], "session-logs", "transcript"), "w").write(h["transcript_path"])
except Exception: pass
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
    open(f, "w").write(str(int(time.time() * 1000)))
    # Session log: note where this run starts in the session's log file (session_log.py slice cuts it out later).
    tp = h.get("transcript_path") or ""
    if tp:
        try:
            subprocess.run(["python3", os.path.join(os.path.dirname(os.environ["ROW_PY"]), "session_log.py"), "mark",
                            skill, tp, "--ledger", os.environ["OBS_DIR"]], capture_output=True, timeout=8)
        except Exception: pass
    raise SystemExit(0)
start = open(f).read().strip() if os.path.exists(f) else str(int(time.time() * 1000))
if tool == "Skill":
    msg = (f"POC Studio observability: `{skill}` is starting (started_at {start}, saved in .poc-studio/skill-starts/{skill}). "
           f"When this skill run returns, before the next step, write its one orbit_studio_skill_run row "
           f"(orbit-writeback Moment 7): cut its session log with `session_log.py slice {skill}`, upload it with "
           f"upload_public_file (session_log_link), build the row with skill_run_row.py --slice (real tokens), then "
           f"apply_record_edits. A log that fails to cut or upload never holds up the row or the run.")
    if skill == "platform-master":
        msg += (" Exception: if this is job 1b · Question review (a Zen planning question), do not write a row now: write one "
                "row for the whole planning window when the plan is approved, with started_at = state.json → zen_planning_started_at.")
    if skill == "unifyapps-headless":
        msg = (f"POC Studio observability: the UnifyApps Headless build is starting (started_at {start}). Write its one "
               f"`unifyapps-headless` row (Moment 7) when the app is published, not now, with its session log "
               f"(`session_log.py slice unifyapps-headless`, uploaded).")
else:
    msg = (f"POC Studio observability: an ai-pm review just returned (started_at {start}). If it was a review "
           f"(not a resolve answer, not INVALID_REQUEST), write its one orbit_studio_skill_run row now (orbit-writeback "
           f"Moment 7): verdict from its verdict file, reviews_run_id from observability.runs, round. Cut its session log "
           f"with `session_log.py slice ai-pm` (it also gives the real tokens), upload it (session_log_link), build the row "
           f"with skill_run_row.py --slice, then apply_record_edits. If it says REVISE (or the person asks for changes), run "
           f"`session_log.py mark-start <stage skill>` before applying the fixes inline, so the re-run gets its own log and tokens.")
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
