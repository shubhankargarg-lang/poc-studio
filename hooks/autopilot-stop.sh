#!/usr/bin/env bash
# POC Studio: while <project>/.poc-studio/autopilot exists, a stage is running. If the turn is about to end
# (often a plain-text question from a stage or UnifyApps Headless), block it once with a reminder to route the question to
# the reviewer. stop_hook_active=true means we already reminded once in this stop sequence: let it end.
INPUT="$(cat 2>/dev/null)"
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
FLAG="$DIR/.poc-studio/autopilot"
[ -f "$FLAG" ] || exit 0
printf '%s' "$INPUT" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && exit 0
cat <<JSON
{"decision":"block","reason":"POC Studio autopilot is on (a stage is running). If you are about to end the turn with a question (from the stage or from UnifyApps Headless), do not ask the user: send it to the poc-reviewer agent in resolve mode, apply the answer, log it in context-log.md and continue the stage. If the stage is finished, go to its reviewer review and approval gate (run rm -f \"${FLAG}\" before asking for approval). If you genuinely need the user (an ASK_HUMAN answer or a sign-in), run rm -f \"${FLAG}\" first and then ask."}
JSON
exit 0
