#!/usr/bin/env bash
# POC Studio: while <project>/.poc-studio/autopilot exists, a stage (or UnifyApps Headless) is running and its
# clarification questions must go to the ai-pm agent, not the user. Otherwise do nothing.
# Two exceptions always reach the user: Zen planning in Stage 4 (while <project>/.poc-studio/zen-planning exists, Zen's
# clarification questions and its plan approval belong to the user) and any CONFIRM_REQUIRED (d_…) question.
# In Sonic run mode (<project>/.poc-studio/sonic exists) the zen-planning flag is never created, and approval gates are
# the AI PM's too, so the deny reason says so.
INPUT="$(cat 2>/dev/null)"   # the hook input (also drains it)
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
FLAG="$DIR/.poc-studio/autopilot"
[ -f "$DIR/.poc-studio/zen-planning" ] && exit 0
printf '%s' "$INPUT" | grep -Eq 'CONFIRM_REQUIRED|\(d_' && exit 0
printf '%s' "$INPUT" | grep -q 'SYSTEM_ACCESS:' && exit 0   # connector-discovery: access and model choices are the person's
[ -f "$FLAG" ] || exit 0
WS="$(head -n1 "$FLAG" 2>/dev/null | tr -d '"\\')"
if [ -f "$DIR/.poc-studio/sonic" ]; then
cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"POC Studio is in Sonic mode with autopilot on (workspace: ${WS}). Do not ask the user. Send this question to the ai-pm agent in resolve mode (write a request YAML in <workspace>/reviews/ and call the Agent tool with the ai-pm agent), apply its answer, log it in <workspace>/context-log.md and continue. In Sonic, approval gates and Zen planning's questions and plan approval are the AI PM's too: never ask the user to approve a stage. Only an ASK_HUMAN answer, a BLOCK still standing after the third review, a Not ready requirement-gathering verdict, a decision to rebuild pages built the no-code way, approving updated wireframes for a change after the build (4c), the AI PM's clarification questions on a vague change request the person typed, a missing tool or connector, a SYSTEM_ACCESS: question (client connection or a replacement model), or a sign-in reaches the user: for those, first run: rm -f \"${FLAG}\" and then ask."}}
EOF
exit 0
fi
cat <<EOF
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"POC Studio autopilot is on (workspace: ${WS}). Do not ask the user. Send this question to the ai-pm agent in resolve mode (write a request YAML in <workspace>/reviews/ and call the Agent tool with the ai-pm agent), apply its answer, log it in <workspace>/context-log.md and continue. Only if it returns ASK_HUMAN, or if this is a POC Studio approval gate or a sign-in, first run: rm -f \"${FLAG}\" and then ask the user."}}
EOF
exit 0
