---
description: Start (or resume) a UnifyApps POC for a client — requirement gathering → scoping → design system → Nebula build → collaterals
argument-hint: <client name>
---

Run the POC Studio pipeline for this client: **$ARGUMENTS**

Load the `poc-orchestrator` skill from this plugin (Skill tool: `poc-studio:poc-orchestrator`) and follow it exactly,
starting with Setup. If no client name was given above, ask for it once, then begin. If a workspace for this client
already exists in the current folder, resume from its `state.json`.
