# POC Studio

A Claude Code plugin that runs a UnifyApps POC end to end for one client:

**Requirement Gathering → Scoping → Design System → Nebula build → Collaterals**

with a shared **Research** skill any stage can call, and a **General Reviewer** that checks every stage's output and
answers every clarification question, so the person is only asked to approve (or redirect) at the end of each stage.

## Install

In Claude Code:

```
/plugin marketplace add shubhankargarg-lang/poc-studio
/plugin install poc-studio@unifyapps-poc
```

On Claude Code 2.1.275 or later, one line also works:

```
/plugin install poc-studio --marketplace shubhankargarg-lang/poc-studio
```

Update later with `/plugin marketplace update unifyapps-poc`.

Requires the **Nebula** plugin for stage 4 (`/nebula:start`) and a **Slack** connector (Gmail, Google Drive and
Google Calendar are optional but improve requirement gathering).

## Use

Open Claude Code in the folder where the POC files should live, then:

```
/poc-studio:start <Client name> | <Use case name>
```

For example `/poc-studio:start Acme Beverages | Shelf Compliance`. The use case name keeps the whole run focused:
Requirement Gathering searches Slack, Gmail, Drive and Calendar for that use case and sets aside material about the
client's other use cases, and each use case gets its own folder. Run the same command again later to resume:
progress is kept in `<client-slug>/<usecase-slug>/state.json`.

## What happens

| # | Stage | Skill | Output (in `<client-slug>/<usecase-slug>/`) |
|---|---|---|---|
| 0 | Setup: connector check (Slack required), workspace | `poc-orchestrator` | `state.json`, `context-log.md` |
| 1 | Requirement Gathering | `requirement-gathering` | `01-requirement-gathering/Requirement Gathering - <Client> - <Use case>.docx`, `files/` |
| 2 | Scoping (build plan) | `scoping-l1-first` | `02-scoping/scoping-document.docx` |
| 3 | Design System | `design-system` | `03-design-system/<client-slug>-<usecase-slug>-design-system.html` |
| 4 | Build in Nebula (Sonic mode, Orbit) | `/nebula:start` | the app on https://orbit.uat.unifyapps.com/, `04-build/build-summary.md` |
| 5 | Collaterals (UnifyApps template) | `poc-collateral-studio` | `05-collaterals/<slug>-collateral/out/`: demo script, video, deck, walkthrough, swimlanes |

After each stage: the **reviewer** (an independent subagent, `poc-reviewer`) reviews the output, the stage fixes
what it flags (max 2 rounds), then you **approve or request changes**. Questions raised during a stage — including
Nebula's (e.g. which model to use) — go to the reviewer, not to you; a hook enforces this while a stage runs.
Research answers are saved in `research/`, reviewer verdicts in `reviews/`.

## Contents

```
.claude-plugin/plugin.json, marketplace.json
commands/start.md                  /poc-studio:start
agents/poc-reviewer.md             independent reviewer subagent
hooks/                             route questions to the reviewer while a stage runs
skills/poc-orchestrator/           the pipeline
skills/requirement-gathering/
skills/research/                   (+ references/calling-research.md, source-guide.md)
skills/scoping-l1-first/
skills/design-system/              unchanged, as tested
skills/general-reviewer/           POC Studio edition (no adapter needed)
skills/poc-collateral-studio/      (+ assets/UnifyApps_template.pptx)
assets/unifyapps-logo.png          fallback logo when a client logo cannot be found
```
