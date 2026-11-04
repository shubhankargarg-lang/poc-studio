#!/usr/bin/env bash
# POC Studio: while <project>/.poc-studio/autopilot exists, a stage is running. If the turn is about to end
# (often a plain-text question from a stage or UnifyApps Headless), block it once with a reminder to route the question to
# the reviewer. stop_hook_active=true means we already reminded once in this stop sequence: let it end.
INPUT="$(cat 2>/dev/null)"
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
FLAG="$DIR/.poc-studio/autopilot"
[ -f "$DIR/.poc-studio/zen-planning" ] && exit 0   # Zen planning window: the user answers, let the turn end
[ -f "$FLAG" ] || exit 0
printf '%s' "$INPUT" | grep -q 'SYSTEM_ACCESS:' && exit 0   # connector-discovery: access and model choices are the person's
printf '%s' "$INPUT" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && exit 0
if [ -f "$DIR/.poc-studio/sonic" ]; then
cat <<JSON
{"decision":"block","reason":"POC Studio is in Sonic mode with autopilot on. If you are about to end the turn with a question (from the stage or from UnifyApps Headless), do not ask the user: send it to the ai-pm agent in resolve mode, apply the answer, log it in context-log.md and continue. If the stage is finished, run its AI PM review; the AI PM's verdict is the gate (the orchestrator's 'The Sonic gate'): record the approval, write it to Orbit and start the next stage without asking. Only an ASK_HUMAN answer, a BLOCK still standing after the third review, a Not ready requirement-gathering verdict, a no-code rebuild decision, approving updated wireframes for a change after the build (4c), the AI PM's clarification questions on a vague change request, a missing tool or connector, a SYSTEM_ACCESS: question (client connection or a replacement model), or a sign-in goes to the user: run rm -f \"${FLAG}\" first and then ask. If the whole run is finished, delete the autopilot and sonic flags and end."}
JSON
exit 0
fi
cat <<JSON
{"decision":"block","reason":"POC Studio autopilot is on (a stage is running). If you are about to end the turn with a question (from the stage or from UnifyApps Headless), do not ask the user: send it to the ai-pm agent in resolve mode, apply the answer, log it in context-log.md and continue the stage. If the stage is finished, go to its reviewer review and approval gate (run rm -f \"${FLAG}\" before asking for approval). If you genuinely need the user (an ASK_HUMAN answer or a sign-in), run rm -f \"${FLAG}\" first and then ask."}
JSON
exit 0
