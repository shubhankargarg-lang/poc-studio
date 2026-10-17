---
description: Start (or resume) a UnifyApps POC for a client use case — requirement gathering → scoping → design system → Nebula build → collaterals
argument-hint: <client name> | <use case name>
---

Run the POC Studio pipeline for: **$ARGUMENTS**

The arguments are `<client name> | <use case name>` (e.g. `Acme Beverages | Shelf Compliance`).

Load the `poc-orchestrator` skill from this plugin (Skill tool: `poc-studio:poc-orchestrator`) and follow it exactly,
starting with Setup. If the client name or the use case name is missing above, ask once for both, then begin. If a
workspace for this client and use case already exists in the current folder, resume from its `state.json`.
