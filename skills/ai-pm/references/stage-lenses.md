# Stage lenses — what the AI PM checks at each gate

Each lens has three parts, run in this order:

1. **Re-run (mechanical).** Re-run the stage's own checks yourself. Never trust a check result, score or
   screenshot the author pasted. A self-reported result that your re-run contradicts is a finding on its own (R9).
2. **Judge (PM).** The questions a script cannot answer, read from the artifact and screenshots.
3. **Never a finding.** Standing decisions and deliberate limits. Raising them burns a round for nothing.

Every finding carries a **fix line** a producer can apply without asking a question:
`<where: section / page / specimen / scene id> — <what is wrong, with evidence> — <exact change>`.
Bad: "Improve the executive summary." Good: "§1 para 1 — opens with the as-is process ('Today, merchandisers…') —
open with P1's cost: 'Range reviews slip two weeks every season because…' (E4)".

Before judging, read the lessons for this stage (`lessons.md`, filter `stage:`) and the owner's profile. Every lesson
is a check. A finding that a lesson caught cites it (`precedent: [L-012]`).

---

## requirement-gathering (kind: requirements)

**Re-run:** list `files/`; confirm every file named in the document exists and every file in `files/` is named.

**Judge:**
- Is the **pain** stated in the client's own words, with who suffers and what it costs? Or only the ask?
- Is the **use case** held to this one? Material from the client's other use cases is listed as "not used", not mixed in.
- Are the **stated asks verbatim** (quotes, with source)? A paraphrased ask is a finding: later stages trace to it.
- Does every gap carry the question that would close it, and a default the run will use meanwhile?
- Is there enough to find a **wow moment**? If the document gives scoping nothing to build a demo climax around,
  say so as a `check_this` decision, not a block.

**Never:** a "Not ready" verdict in the document (that is the person's call at the gate); thin input.

---

## scoping (kind: plan for Part A, spec for Part B)

**Re-run:**
- `python3 _working/check_docx.py 02-scoping/scoping-document.docx` must print `ok`.
- `python3 <skill>/scripts/scope_metrics.py 02-scoping/scoping-document.docx` — sizing, L1 share, slop hits,
  §1 opening line, §20.2 storyline steps.

**Judge (Part A):**

| Lens | Question | Typical blocking finding |
|---|---|---|
| The wow | Does §1 open with the pain? Is there one moment in §20.2 the client's sponsor would retell to their boss? Is it live on screen, not a seeded replay? | Storyline is a feature tour; the core action re-shows a seeded result |
| Prioritisation (adversarial) | Re-test every L1 row as a sceptic: drop it — does the client lose an ask, does the core flow or an agent break, or does research say the demo looks incomplete? If none, it is L2. | L1 share > 50%; sizing over budget (pages > 6 per app, objects > 12, agents > 1 without a Decision) |
| Relevance | Does every L1 feature trace to a P-ID, a stated ask or research must-have? Is anything impressive but unrequested? | Untraced module; a supporting check grown into the app's centre |
| Journey integrity | Does L1 touch every stage of 8.1 at least thinly? Is exactly one persona Primary, with a task-led home? | One module is the whole app; a KPI-tile home |
| Assumption risk | Rank 5.6 by impact-if-wrong. Any assumption that would change the data model or the storyline must be researched, not assumed. | High-impact volume or process assumption, never challenged |
| Language | Client vocabulary everywhere (Appendix B)? Any slop from D1–D7? | Executive summary that could be about any client |
| Seed realism | Hero records use real brands and products; every warning, gate block and copilot answer has a planted defect | A gate block with nothing seeded to trigger it |
| Buildability | Computed values written by a workflow (no formula fields); one picklist/lookup convention; object prefixes; code app where the UI needs it | A badge with no workflow writing it |

**Judge (Part B):** only completeness and consistency with Part A. Detail is expected, never a finding.

**Never:** Part B length or detail; a design choice that the design-system skill owns (colour, theme, typeface);
a cut that a human decision approved.

---

## wireframes (kind: design, low fidelity)

**Re-run:**
- Render the spec yourself: `python3 "$W/render.py" <spec> <tmp>` (`W` = the request's `scripts.wireframes`) (a spec error is a finding with its
  line), then `python3 "$W/coverage.py" <scoping docx> <manifest>`: every §11 page has a frame and
  every §23 CMP ID is on a block. Each gap is a finding.
- Count: frames per page (extra frames only for an open panel, drawer, modal, map mode or phone layout), components in
  the manifest, components with more than three `variants` (a finding). `features` and `page_parts` are not variants.

**Judge (from the PNGs):**
- **Each frame answers its page's question.** The §11 Screen UX question, the one primary CTA, the hero content above
  the fold at 1280×800, the filters with their values, the exact copy. A frame whose hero is a KPI strip on a doer's
  home is a finding (scoping's home rule).
- **Slots vs detail.** The page's defining region is drawn in detail with real wording; generic regions are slots
  naming a component, a count, variants and states. A slot for the hero, or detail spent on a generic chart, is a
  finding.
- **One name per component.** The same thing has the same component name on every page; two names for one thing, or
  one name for two different things, is a finding.
- **Maps.** A page whose main question is *where* uses `layout: map` and follows `map-component.md` (map is the page,
  floating panels, legend in the screen's own words, mode fits the question, data contract with lat/lng fields that
  exist in §12). A map in a card, or a map without coordinates in the data model, is blocking.
- **Agent and irreversible action.** The agent appears as a drawer frame; the one irreversible action has its confirm
  modal frame.
- **Nothing L2.** A region or component that only an L2 feature needs is a finding: remove it.

**Never:** greys, one font, no brand or icons; empty slots; the design system's job (colour, type, variants beyond the
manifest's list); the render's own look.

---

## change-clarity (resolve, on every change request, any stage)

Runs before anything is reworked: at every approval gate (requirements, BRD/scoping, wireframes, design system, the
built app, collaterals), in Zen and Sonic, in a full run or a one-off. Read the person's words, everything they
attached, the current approved artifact and its upstream, and the human decisions in the context log. Decide
whether one sensible reading exists. Go by what each reading would redo, not by how long the request is.

**Vague — ASK_HUMAN** when any of these holds:
- The person supplies a **new artifact or reference** (a design system, a file, a screenshot, a website, a
  document) and does not say which parts to take or how it relates to the approved one.
- The request **conflicts** with an approved upstream document or a logged human decision.
- The scope is **open-ended or a matter of taste**: "make it better", "more modern", "cleaner", "like this one".
- It can be **read two ways**, and one reading would redo finished, approved work (a whole design system, many
  pages, the data model, the storyline).
- It **names something that does not exist** in the artifact (a page, a section, a component, a field).

**Clear — DECIDE** with a `reading` when all of these hold:
- It names the place and the change ("rename the 'Cases' tab to 'Claims'", "add the due date to the queue table").
- The change is small and easy to undo.
- There is one sensible reading, and it touches nothing the person did not name.

**How to ask.** 1–3 questions, each with 2–4 options. Each option is a complete reading in plain words. Put your
recommended option first. `why` says what makes the request vague, in one line, and `cost_if_wrong` says what would
be redone. Ask only what the words and attachments leave open.

**The default when in doubt.** A new artifact that would replace an approved one is never adopted in full without
asking. The recommended option keeps the approved one and takes only what the person named. When they named
nothing, recommend the smallest sensible part (for a design system: its colours and type, on the current styling).

**Worked example (a real incident).** After the app was built, the person shared a new design system that looked
very different from the approved one and asked to "use this". The build adopted all of it and dropped the existing
styling. The person only wanted part of it. The right answer was ASK_HUMAN:

```yaml
disposition: ASK_HUMAN
answer: { clear: false, attachments: [ { item: "new-ds.html", use: "to be confirmed" } ] }
why: "A new design system was supplied without saying which parts to use; using all of it would restyle every page."
ask_human:
  - { to: <owner>, question: "How should the new design system be used?",
      options: [ "Keep the current styling and take only its colours and type",
                 "Use it only for some components (name them)",
                 "Replace the current design system with it in full" ],
      recommended: "Keep the current styling and take only its colours and type",
      cost_if_wrong: "every page restyled, then restored", meanwhile: "nothing is reworked until answered" }
```

**In the next review.** The `reading`, or the person's answers, is the upstream for the change. In the review of the
reworked artifact:
- anything changed beyond the reading is a blocking R2 finding (fix line: restore it from the approved version);
- a stage or builder note that says it switched to the new input because it was very different, or that it chose a
  reading the person did not give, is a blocking R2 finding, even when the result looks good.

**Never:** asking about a change that is clear by the rules above; asking for approval of the reading of a clear
change (it is logged and shown in the next gate summary).

## change-triage (resolve, after the build — orchestrator 4c)

Classify the person's change request before anything touches the app. Read their words (with the `change-clarity`
reading or the person's answers to it), the approved spec and
manifest in `02b-wireframes/`, scoping §11 and `04-build/build-summary.md`. Go by what the change does to the
**layout**, not by how many words the request has.

| Tier | What the change does | Route |
|---|---|---|
| `small` | Copy or labels; a bug or broken control; seed or demo data; an agent's or automation's logic, prompt or output; a field or column added to an existing table, form or card; a status, filter value or sort; colour, spacing or type within the design system tokens; one state of one component | Direct fix through `ua-change` on the items named. No wireframes. |
| `big` | Adds or removes a page, drawer, modal or panel; changes a page's regions or their order; moves the hero or the primary CTA; changes the navigation or which persona sees a page; needs a component or variant that is not in the manifest; changes a step of the demo storyline (§20.2) | Wireframes first (only the affected frames), the person approves, then targeted `ua-change` fixes on those pages only. |
| `very-big` | A new persona or role shell; a new navigation structure; about half the pages or more change layout; a change to the data model (objects or fields) that several pages bind to | Wireframes first, the person approves, then a scoped re-plan (`/ua:plan`, Zen) limited to the affected pages and objects. |

- A request with several parts takes the tier of its largest part; the small parts ride along in the same fix.
- `affected_pages` lists every existing page whose frame will change, by page ID; `new_pages` lists pages to add.
  Pages that only show new data in an existing slot are `small`, not affected.
- When small or big could both fit, answer **big**.

## wireframes-update (review of the change sheet, after the build)

**Re-run:** `diff.py` on `_previous/v<N>` and the current folder; `render.py`; `coverage.py`.

**Judge:**
- Every page in the triage's `affected_pages` and `new_pages` appears in the change sheet, and **no other page does**:
  an unrequested change to another frame is blocking (fix line: restore it from `_previous/v<N>`).
- The after frame does what the person asked, in their words, and still answers the page's question (the
  `wireframes` lens applies to each changed frame).
- New components in the manifest delta are slots with a `note` saying they are new in this change.
- The change matches the `change-clarity` reading (or the person's answers); anything beyond it is blocking.

**Never:** that the design system was not updated (standing decision: the build styles new components from its kit
and tokens); that unchanged frames were not re-reviewed.

---

## design-system (kind: design)

**Re-run:**
- Render the HTML with Playwright in light and dark, at 1280×800, 1280×680 and 375×812.
- Run `scripts/render_check.js` (the design-system skill's own render check) in each. Any non-zero count is a finding
  with its `where` list.
- Count by script: component pages, `<template class="device">` screens (≤ 5), `#style-sets` with one active set,
  `data-active` on every specimen, every L1 feature ID and CMP ID from the scoping doc present in the page inventory.
  With approved wireframes: the `data-component` values equal the manifest's components plus the baseline (an extra
  or a missing one is a finding), every frame's page ID without its letter suffix is in `#build-plan`, and each drawn screen keeps its frame's
  regions in the same order.
- Exact wording: every quoted refusal/message in scoping §8.2 appears verbatim in the flow diagrams.

**Judge (from your own screenshots, not the skill's):**
- **Independent design score**, 1–5 on the skill's five dimensions (distinctiveness, hierarchy, rhythm, finish,
  concept). If yours is more than 1 point below the skill's self-score on any dimension, that is a finding with the
  screenshot as evidence. Distinctiveness or finish under 4 by your score is blocking.
- **Logo-off test, done by you.** Cover the logo on the main screen. Compare against the last design systems
  recorded in `lessons/recent-looks.md`. Same chrome + surface + layout as a recent client = finding.
- **Brand check.** Fetch the client's live site once; compare hue family, light-to-dark balance and chrome choice
  with the expression card. A black-led brand shipped on a colour rail is blocking.
- **Concept visible.** The design concept on the expression card shows in the signature components, not only the card.
- **Profile rules.** Owner's profile items (e.g. no coloured side stripes: reject a `TB` status-stripe variant in the
  active set).
- **Weakest part.** Read the skill's own "weakest part" answer. Fixable inside the run → finding. Not fixable → carry
  it to the gate summary.

**Fix lines** name the section and specimen, and the request says: "fix only what is listed; leave everything else
byte-for-byte". A full re-run of the design system for a few findings is a wasted hour.

**Never:** the five-screen limit; the skill's steps; a brand settled by its source order; the labelled UnifyApps
stand-in logo; the public Orbit upload.

---

## build — Stage 4b (kind: build)

Runs after UnifyApps Headless's own parallel testing (`04-build/test-report.md`) and before publish. Its test is the
first pass; this is the independent one. The app is opened from `app.preview_url` with the saved Orbit session.

**Re-run:**
- `node scripts/build_walk.mjs --url <preview_url> --storage <orbit session json> --routes 04-build/routes.json --out reviews/build-walk-<n>`
  walks every page in scoping §11 nav order at 1280×800, opens every tab, and writes per page: screenshot,
  render-check counts, visual-acceptance checks (horizontal scroll, row height ≤ 64 px, rows visible ≥ 8, wrapped
  pills), raw values on screen, disabled buttons without a reason, side stripes, console errors, failed requests,
  and every visible string (`copy.json`).
- Reconcile counts: every rail badge and KPI tile number equals its page's row count (from the walk's numbers).

**Judge:**
- **Storyline.** Walk scoping §20.2 step by step on the screenshots. Each step: right page, right record in the right
  state, the proof visible without extra clicks.
- **Fidelity (R8).** Each page's pattern matches its `#build-plan` entry; only active variants; tokens only; agent in the
  drawer. Compare side by side with the drawn screens and the approved wireframe frames (`02b-wireframes/png/`): same
  regions in the same order. On a map page, check the map-component behaviour: rings split on zoom, labels never
  overlap, the card opens on hover and stays on click, sites stay clear of open panels, the legend's words match.
- **Copy lens.** Read `copy.json` against the glossary (scoping Appendix B) and slop C1–C7: one name per thing,
  outcome-named buttons, exact refusal wording, no jargon, sentence case.
- **Reverse trace.** Anything visible that no L1 feature asked for (extra tab, extra page, extra chart) is a finding:
  remove it.
- **Test-report honesty.** Anything `test-report.md` marks pass that the walk shows broken is a blocking R9 finding.

**Fix route:** findings go to UnifyApps Headless in the same session as numbered fix lines, as direct changes through
`ua-change` (no new plan), independent fixes in parallel; a platform asset it cannot build goes to platform-master's
browser fallback. At most 3 rounds per item; then the walk re-runs on the pages the fixes touched.

**Never:** design decisions already approved in the design system; seed records the person created while verifying.

---

## collaterals (kind: deliverable)

**Re-run:** `python3 kit/check.py` (must report 0 must-fix); read `review/v<n>/report.md` and the contact sheet;
render the deck and script PDF to images and look at every page.

**Judge:**
- **Opening.** The first narration line names the client's pain (RG pain points), not a feature (K1).
- **Wow by 1:30.** The core action from scoping §20.2 lands before 90 s in `build/placed.json` (K2).
- **Every number** on a slide or in narration is in `facts.json` or on its screen; big stats are outcomes (K4). The
  opening slide's fixed figures and the blueprint's counts (taken from `blueprint.json`) are excepted.
- **One subject, one story** across video, script and deck: same record, same numbers, same names.
- **Ending.** Next steps are the client's path, not our fixes (K6). Length 4–5 min unless the brief records why.
- **Preview link** frames only: no Matrix login or user-creation screen anywhere (blocking R9).
- **Deck frame.** The first slide is the UnifyApps opening slide and the last is the "Thank You" slide, both
  unchanged from the template (a missing or edited one is a finding, unless the person asked to leave it out:
  `"open"` / `"close": false`, recorded in `brief.json` decisions).
- **Technical blueprint.** Re-run `node kit/blueprint.mjs` (exit 0). Its slides follow the story and come before
  next steps: the architecture, then every automation and AI agent on as many slides as needed. Compare `built`
  with `04-build/build-summary.md` (or the solution): a built automation or agent missing from the list, or a listed
  one that was never built, is blocking (R9). Systems not connected in the POC are marked simulated or go-live, never
  live. No secrets or key values on any slide.

**Never:** the bundled template; the opening and closing slides' fixed text; the voice; the absence of a
walkthrough PDF or a swimlanes document; a blueprint that runs to several slides.
