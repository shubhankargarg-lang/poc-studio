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

**Later reviews read only what changed.** Each lens below describes the first, full review. In every later review of
the same stage (rounds 2 and 3, and the review after any change), apply it only to what `review_delta.py diff`
reports as changed and what depends on it, re-run every script on the whole artifact, and raise no new non-blocking
findings on unchanged parts (ai-pm skill, "Later reviews read only what changed").

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
- **AI inputs and samples.** Every AI feature that reads documents or images is in the table with its samples and
  kind; files our team made are never "real"; item 9 is scored by the rule (Confirmed only with a real or
  anonymised-real sample for every input); with no samples, a Blocking client question and the person's recorded
  choice; sample files sit in `files/samples/` and are tagged in Section 4.
- Is there enough to find a **wow moment**? If the document gives scoping nothing to build a demo climax around,
  say so as a `check_this` decision, not a block.

**Never:** a "Not ready" verdict in the document (that is the person's call at the gate); thin input.

---

## scoping (kind: plan for Part A, spec for Part B)

**Re-run:**
- `python3 _working/check_docx.py 02-scoping/scoping-document.docx` must print `ok`.
- `python3 "$R/scope_metrics.py" 02-scoping/scoping-document.docx` — sizing, L1 share, slop hits,
  §1 opening line, §20.2 storyline steps.

**Judge (Part A):**

| Lens | Question | Typical blocking finding |
|---|---|---|
| The wow | Does §1 open with the pain? Is there one moment in §20.2 the client's sponsor would retell to their boss? Is it live on screen, not a seeded replay? | Storyline is a feature tour; the core action re-shows a seeded result |
| Prioritisation (adversarial) | Re-test every L1 row as a sceptic: drop it — does the client lose an ask, does the core flow or an agent break, or does research say the demo looks incomplete? If none, it is L2. | L1 share > 50%; sizing over budget (pages > 6 per app, objects > 12, agents > 1 without a Decision) |
| Relevance | Does every L1 feature trace to a P-ID, a stated ask or research must-have? Is anything impressive but unrequested? | Untraced module; a supporting check grown into the app's centre |
| Journey integrity | Does L1 touch every stage of 8.1 at least thinly? Is exactly one persona Primary, and does each persona's home say what they do first and what needs them? | One module is the whole app; a home with no first task |
| Assumption risk | Rank 5.6 by impact-if-wrong. Any assumption that would change the data model or the storyline must be researched, not assumed. | High-impact volume or process assumption, never challenged |
| Language | Client vocabulary everywhere (Appendix B)? Any slop from D1–D7? | Executive summary that could be about any client |
| Seed realism | Hero records use real brands and products; every warning, gate block and copilot answer has a planted defect | A gate block with nothing seeded to trigger it |
| Buildability | Computed values written by a workflow (no formula fields); one picklist/lookup convention; object prefixes; code app where the UI needs it | A badge with no workflow writing it |

**Page specs (scoping v5):** each §11 page says what the page must do (the question, the decision, what needs the
person, one primary action, the exact copy, every state) and what the person must see to decide. A page that names a
UI pattern, a layout region or a component (a KPI strip, a kanban board, a side pane) is a finding: the wireframes
decide those. §21.1 Hero object and §21.2 Reference products exist (check_docx requires them); §23 is a capability
inventory with stable CMP IDs.

**Judge (Part B):** only completeness and consistency with Part A. Detail is expected, never a finding.

**Integration Spec (re-run against `01c-integration/integration-spec.json`, when the upstream includes it):**
- §12, §14 and §15 match the spec: the same client objects, fields, operations and field mapping; a client object,
  field or operation the spec has not seen is blocking (it belongs in §5.6 as an assumption, or in a `scope: item` run).
- Every client-system step in §14 (the trigger and each connector read and write) names the connection with its id.
- Nothing Live rests on a `blocked` step or a `gap` (those are Planned, shown as planned writes, with a Decision).
- Every access answer in the spec came from the person (a `SYSTEM_ACCESS:` answer in `context-log.md`), never the AI PM.
- §13 and §17 name, for each model slot, the spec's tested card and its fallback (`models[]`).

**Never:** Part B length or detail; a design choice that the design-system skill owns (colour, theme, typeface);
a cut that a human decision approved.

---

## wireframes (kind: design, low fidelity — wireframes skill, HTML contract)

**Get the tools** from the installed skill (`scripts.wireframes` in the request, `$W`), never a copy in the workspace
(the producer may have changed it); write your own output to a temporary folder:
```bash
W="<scripts.wireframes>"; [ -f "$W/wf_tool.py" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/wf_tool.py' 2>/dev/null | sort -V | tail -1)")"; T="$(mktemp -d)"
```

**Re-run:**
- `python3 -I "$W/wf_tool.py" check <workspace>/02b-wireframes/<slug>-wireframes.html`: every `error:` is a finding;
  every `check:` line must be fixed or defended in the hand-over (an unexplained one is a finding).
- `python3 -I "$W/wf_tool.py" review <html> "<workspace>/reviews/shots/wireframes-<n>"` (needs a browser; the HTML is
  the only output, so these screenshots are yours; they are kept, see "Keep this review's screenshots" below): look at
  its contact sheets and the reading-order overlays yourself. Script errors, reading-order checks and overlapping text it prints are findings.
- `python3 -I "$W/wf_tool.py" manifest <html> "$T"`, then `python3 "$W/coverage.py" <scoping docx> "$T/wireframe-manifest.json"`: every §11 page has a screen and every CMP ID is on an instance
  or named in `brd_overrides` with a reason. Each gap is a finding.

**Keep this review's screenshots** (the before-and-after check at the gate uses them; nothing is uploaded): save them
in `<workspace>/reviews/shots/wireframes-<n>/` (`<n>` = this review's number) instead of a temporary folder, with a
`shots.json` beside them: `{"stage", "review": <n>, "version": "<the version reviewed: v3, App v5>", "at": <ms>,
"screens": {"<screen or section id>": "<file name>"}}`. Never delete an earlier review's folder.
- Open the HTML in a browser and click through the journey (`wf-meta.journey`) from start to payoff.

**Judge (from your own renders and the clicks):**
- **Each screen does its brief, in its reading order.** The brief (job, decision, what needs the person, next step)
  is visible without a scroll or a click; `first`, `next` and `act` are where the eye goes.
- **Pattern, not a house layout.** Pages differ by their work (`patterns.md`); most pages opening the same way, the
  same banner or chips everywhere, or two queues drawn alike is a finding.
- **The signature is drawn as itself and shows on the home key screen**; documents are drawn as documents with their
  real parts, never as grey pictures.
- **Real, consistent content.** No slots, placeholder or demo words; one `today`; counts match what is drawn and
  move when decisions are made; the same record has the same values everywhere; numbers that a formula produces add
  up (an invented input to make them add up is a finding unless it is logged as an assumption).
- **Every control works,** inside its own screen; drawers and modals have a header with the title and close, their
  content, and a footer with the actions; disabled actions show their reason.
- **Frames only for real changes** (layout, persona, structural state, workflow step); a frame per filter or tab is
  a finding.
- **`key_screens`:** home, main and agent are three different views; home shows the signature.
- **Overrides and open questions** are recorded with reasons; a justified override is never a finding.
- **Slop:** filler, generic headings, stacked sublines, long sentences, internal codes on screen (`slop.md`).

**Never:** greys, one font, no brand or icons; the design system's job (colour, type, elevation, finish); a justified
`brd_overrides` entry; the rejected navigation options.

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

**Re-run:** `diff.py` on `_previous/v<N>` and the current folder; the skill's `wf_tool.py check` (wireframes lens,
"Get the tools"); `coverage.py`. A page `diff.py` reports as "metadata only" did not change on screen.

**Judge:**
- Every page in the triage's `affected_pages` and `new_pages` appears in the change sheet (`change-sheet.html`: each
  changed screen before | after, clickable), and **no other page does**: an unrequested change to another screen is
  blocking (fix line: restore it from `_previous/v<N>`).
- The after frame does what the person asked, in their words, and still answers the page's question (the
  `wireframes` lens applies to each changed frame).
- New components in the manifest delta are full components with real content, with a registry `note` saying they are
  new in this change.
- The change matches the `change-clarity` reading (or the person's answers); anything beyond it is blocking.
- An app-level change in the sheet (navigation, `today`, journey, signature, the NAV or VIEWS sheet) affects every page:
  it is allowed only when the reading asked for it.

**Never:** that the design system was not updated (standing decision: the build styles new components from its kit
and tokens); that unchanged frames were not re-reviewed; `check:` or `warning:` lines about pages outside the change.

---

## design-system (kind: design — design-system skill, standalone catalogue)

**Get the tools** from the installed skill (`scripts.design_system` in the request, `$D`), never a copy in the
workspace: `D="<scripts.design_system>"; [ -f "$D/scripts/ds_tool.py" ] || D="$(dirname "$(dirname "$(find ~/.claude/plugins -path '*design-system/scripts/ds_tool.py' 2>/dev/null | sort -V | tail -1)")")"; T="$(mktemp -d)"`.

**Re-run** (start each command with `source ~/.local/poc-collateral/env.sh 2>/dev/null;`):
- `python3 -I "$D/scripts/ds_tool.py" fidelity <wireframes.html> <design-system.html>`: every `error:` is a finding (content,
  structure, traceability, anatomy corrections listed in `#corrections`, data-bound visuals, the logo section, the
  twelve sections, the JSON blocks).
- `python3 -I "$D/scripts/ds_tool.py" audit <design-system.html> "<workspace>/reviews/shots/design-system-<n>"`
  (kept, see "Keep this review's screenshots" below): every `error:` is a finding (contrast in both
  themes, blank, clipped and cut specimens, component anatomy, surfaces that blend in, field and button edges,
  touching controls, select arrows, the surface ladder, rendered consistency). `check:` lines the QA report does not
  explain are findings.

**Keep this review's screenshots:** the audit's screenshots stay in `<workspace>/reviews/shots/design-system-<n>/`
with a `shots.json` beside them: `{"stage": "design-system", "review": <n>, "version": "<v3>", "at": <ms>,
"screens": {"<section id> (light|dark)": "<file name>"}}`. Never delete an earlier review's folder.

**Judge (from your own screenshots in `reviews/shots/design-system-<n>/`, every entry and screen, light and dark):**
- **Finished, not coloured.** Each component looks like a finished product element for its kind (the skill's
  "Finish each component" table): drawers and modals with a clear header, body and footer; metrics with a clear number;
  tables with aligned numbers and status words; secondary buttons and fields with visible edges. A component that
  reads as a coloured wireframe fragment is a finding with its screenshot.
- **Edges and surfaces.** Every container's edge shows on all four sides in both themes; nothing merges with the page.
- **Gradients only by role:** the app canvas, the top bar and the signature (`.wash`), two brand colours, the same on
  every instance of a kind. A gradient anywhere else, or on one card among its siblings, is a finding.
- **Fidelity.** The three screens are the wireframe's `key_screens` with their content unchanged; every correction in
  `#corrections` keeps content and behaviour; anything the wireframe lacks is under Wireframe gaps, not invented.
- **Brand.** Fetch the client's site once: the hue family and chrome fit. The logo is the official file, or the logo
  section shows all seven slots with labelled placeholders, the routes tried and what is needed.
- **Nothing drawn over specimens** (no numbered markers); no demo or synthetic labels.
- **Weakest part.** The hand-over names it. Fixable inside the run → finding; not fixable → the gate summary.

**Fix lines** name the entry or screen, and the request says: "fix only what is listed; leave everything else
byte-for-byte". A full re-run of the design system for a few findings is a wasted hour.

**Never:** the three-screen limit; a brand settled by its source order; a labelled placeholder logo when the routes
were tried and recorded; picture mockups in place of photos; the public Orbit upload; the house stylesheet's own
structure.

---

## build — Stage 4b (kind: build)

Runs after UnifyApps Headless's own parallel testing (`04-build/test-report.md`) and before publish. Its test is the
first pass; this is the independent one. The app is opened from `app.preview_url` with the saved Orbit session.

**Re-run:**
- `node scripts/build_walk.mjs --url <preview_url> --storage <orbit session json> --routes 04-build/routes.json --out reviews/build-walk-<n>`
  (its screenshots are kept: write `reviews/build-walk-<n>/shots.json` with `{"stage": "build", "review": <n>,
  "version": "App v<N>", "at": <ms>}` beside the report; the report already names each page's screenshot. Never
  delete an earlier walk's folder)
  (plus `--personas 04-build/personas.json` when it exists) walks every page in scoping §11 nav order at 1280×800,
  once per persona in `routes.json` (switching persona in the app's profile menu, or with the session or steps in
  `personas.json`), opens every tab, nested tabs up to 3 deep, and the drawer or record a route's `open` names, and
  writes per page: load time, screenshot,
  render-check counts, visual-acceptance checks (horizontal scroll, row height ≤ 64 px, rows visible ≥ 8, wrapped
  pills), raw values on screen, disabled buttons without a reason, side stripes, console errors, failed requests,
  and every visible string (`copy.json`).
- Reconcile counts: every rail badge and KPI tile number equals its page's row count (from the walk's numbers).
- **Read the report before judging:**
  - **INCOMPLETE** or **STOPPED** at the top (signed out, a persona it could not switch to, routes that leave the
    app, or half the pages not walked): fix the cause it names (sign in again, add the persona's `switch` steps or
    session to `personas.json`, write routes relative to the preview link) and re-run **once**. If it is still
    incomplete, stop and return the `tool_failure` block (ai-pm SKILL.md, build); do not approve or reject the build
    on that report, and never review the app's code instead.
  - **`route_left_app`** (under Walk problems): the route opened a page outside the app root (the report's first
    line). The routes file is wrong, not the app: never a finding.
  - **No access** (under Walk problems): the page said the signed-in user may not see it (HTTP 401/403, "you do not
    have access"). On the start page the report is INCOMPLETE: the Orbit user is not linked to the app, so nothing
    was reviewed; ask the person to link the user (or give a persona that has access) and re-run once. On a single
    page: if scoping §11 gives that persona the page, check the screenshot and raise it as an R1/R7 finding;
    otherwise the route's persona is wrong.
  - **Platform (tenant_unavailable):** HTTP 429/502/503/504 and platform error pages that stayed after 2 retries.
    These are the platform's, not the app's: never a finding, never a fix line. Re-run those pages later (a routes
    file with only them); if they stay down, tell the person the tenant is unavailable.
  - **Walk problems:** the walk itself could not check something (a check crashed; its screenshot is kept). Judge
    that page from its screenshot; never pass a walk problem to UnifyApps Headless.
  - **Slow (loaded after N s)** is a non-blocking note: the first visit to a cold UAT page is often slow. Only
    **never finished loading** (still a skeleton or spinner after 30 s) is blocking.
  - The render check leaves out screen-reader text, chart internals and angled labels; the rest are candidates to
    confirm on the screenshot, as always.

**Judge:**
- **Storyline.** Walk scoping §20.2 step by step on the screenshots. Each step: right page, right record in the right
  state, the proof visible without extra clicks.
- **Fidelity (R8).** Each page's pattern matches its `#build-plan` entry (match routes ignoring a leading `/`:
  `orders` in `routes.json` is `/orders` in `build-plan.pages`); only active variants; tokens only; each
  component built with the anatomy its catalogue entry shows (`#corrections` lists where that differs from the
  wireframe's drawing); agent in the drawer with **one** way in (the design system's `app.agent_entry`). Compare side
  by side with the three styled screens and the approved wireframe HTML (`02b-wireframes/<slug>-wireframes.html`, each screen by its `data-screen-id`): same
  regions in the same order, the chosen navigation shell only (the others, on the `#NAV-options` sheet, are
  rejected), and each hero list's views as a switch on the same page (a view frame is a view, not a page). On a map page, check the map-component behaviour: rings split on zoom, labels never
  overlap, the card opens on hover and stays on click, sites stay clear of open panels, the legend's words match.
- **Copy lens.** Read `copy.json` against the glossary (scoping Appendix B) and slop C1–C7: one name per thing,
  outcome-named buttons, exact refusal wording, no jargon, sentence case.
- **Reverse trace.** Anything visible that no L1 feature asked for (extra tab, extra page, extra chart) is a finding:
  remove it.
- **Test-report honesty.** Anything `test-report.md` marks pass that the walk shows broken is a blocking R9 finding.

**Fix route:** findings go to UnifyApps Headless in the same session as numbered fix lines, as direct changes through
`ua-change` (no new plan), independent fixes in parallel; a platform asset it cannot build goes to platform-master's
browser fallback. At most 3 rounds per item; then the walk re-runs on the pages the fixes touched, plus the first
page of the storyline (a routes file with only those pages), never the whole app again. Platform failures and walk
problems are never sent as fix lines.

**Never:** design decisions already approved in the design system; seed records the person created while verifying.

---

## collaterals (kind: deliverable)

Review only the collaterals made. One the person asked to skip (`stages.collaterals.skip`) is never a finding, and
its checks below do not apply.

**Re-run:** `python3 kit/check.py` (must report 0 must-fix); read `review/v<n>/report.md` and the contact sheet;
render the deck and script PDF to images; look at one contact sheet of every page first, then at full size the
first and last slide, the storyline's key moments and anything flagged or unclear (SKILL.md "What it reads").

**Judge:**
- **Opening.** The first narration line names the client's pain (RG pain points), not a feature (K1).
- **Wow by 1:30.** The core action from scoping §20.2 lands before 90 s in `build/placed.json` (K2).
- **Every number** on a slide or in narration is in `facts.json` or on its screen; big stats are outcomes (K4). The
  opening slide's fixed figures and the blueprint's counts (taken from `blueprint.json`) are excepted.
- **One subject, one story** across video, script and deck: same record, same numbers, same names.
- **Ending.** Next steps are the client's path, not our fixes (K6). Length 4–5 min unless the brief records why.
- **Preview link** frames only: no Matrix login or user-creation screen anywhere (blocking R9).
- **Deck frame.** Check the order the way a viewer opens the file: unzip the `.pptx` and confirm the slide files
  run `slide1.xml` … `slideN.xml` in the deck's order (`deck.py` prints "order checked"), then render it. The first slide is the UnifyApps opening slide and the last is the "Thank You" slide, both
  unchanged from the template (a missing or edited one is a finding, unless the person asked to leave it out:
  `"open"` / `"close": false`, recorded in `brief.json` decisions).
- **Technical blueprint.** Re-run `node kit/blueprint.mjs` (exit 0). Its slides follow the story and come before
  next steps: the architecture, then every automation and AI agent on as many slides as needed. Compare `built`
  with `04-build/build-summary.md` (or the solution): a built automation or agent missing from the list, or a listed
  one that was never built, is blocking (R9). Systems not connected in the POC are marked simulated or go-live, never
  live. No secrets or key values on any slide.

**Never:** the bundled template; the opening and closing slides' fixed text; the voice; the absence of a
walkthrough PDF or a swimlanes document; a blueprint that runs to several slides.
