#!/usr/bin/env bash
# POC Studio: while <project>/.poc-studio/autopilot exists, a stage (or UnifyApps Headless) is running and its
# clarification questions must go to the poc-reviewer agent, not the user. Otherwise do nothing.
cat >/dev/null 2>&1   # drain the hook input
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
FLAG="$DIR/.poc-studio/autopilot"
[ -f "$FLAG" ] || exit 0
WS="$(head -n1 "$FLAG" 2>/dev/null | tr -d '"\\')"
cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"POC Studio autopilot is on (workspace: ${WS}). Do not ask the user. Send this question to the poc-reviewer agent in resolve mode (write a request YAML in <workspace>/reviews/ and call the Agent tool with the poc-reviewer agent), apply its answer, log it in <workspace>/context-log.md and continue. Only if it returns ASK_HUMAN, or if this is a POC Studio approval gate or a sign-in, first run: rm -f \"${FLAG}\" and then ask the user."}}
EOF
exit 0
