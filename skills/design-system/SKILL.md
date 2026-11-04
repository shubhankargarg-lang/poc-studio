---
name: "design-system"
description: "Build a client design system from the scoping document (or BRD), a client name and a website, plus the approved wireframes when POC Studio has them, and ship it as ONE self-contained HTML file with the composition contract the builder follows. A creative director researches the client's world, drafts three directions from three different sources, checks them against the register of apps already made and picks one; the run then samples the real brand and logo, skins house Design Language v3.4 onto it preserving luminance, designs every component the app needs (with variants and drawn states), shows the client's hero object as HTML/CSS picture mockups, and opens with a showcase of three screens and two or three close-ups. A render scan and the creative director's judgement pass (at most two rounds) close the run, and the app's fingerprint goes into the shared register. Audited in light and dark. Use before any screen is drawn."
---

# Design system for a POC (v12.6)

**Input:** the approved wireframes (`wireframe-manifest.json`, the `png/` frames, the PDF), the scoping document, the
client name and the website. **Output:** one HTML file that makes this client's app look as if it was made only for
them, with every component the app needs, designed well enough that the builder never guesses.

**What decides quality, in this order:**
1. **An idea that belongs to this client.** Phase D finds it: a creative director researches, proposes three
   directions from three different sources, and picks the one with the strongest wow that still serves the work.
2. **The hero object shown the way users judge it.** The scoping document's 21.1 and the manifest's `hero_object`
   name the thing users care about most. When it has a picture, the picture leads wherever people meet it.
3. **Craft in every state.** The kit, the transform and the audit (Steps 0 to 6) keep every measurement honest.

Length is not quality. A file that documents everything at the same depth reads as generic, and the team rejected
exactly that. Depth goes to the direction, the showcase, the flows, the signature and up to five key components;
every other component page is compact (0.6). `check_ds.py` and `scan.py` hold the budgets.

**Who decides what.** The scoping document says what is true (data, rules, wording, the hero object). The wireframes
decide each page's layout, pattern and the journey. **This skill decides how every component looks and behaves.** It
designs each one to its brief in the manifest (`purpose`, `shows`, `does`, `volume`, `primary`, `media`) and may give
it a richer form than its grey frame when the brief is better served (a list of products becomes their pictures; a
timeline row leads with the item's image), marking the change with `data-form-change` and keeping the frame's layout.

**How a run goes** (pictures are drawn as HTML/CSS mockups, never fetched, so no time goes to finding images):

| # | Step | Time |
|---|---|---|
| 1 | Phase 0: read the wireframes and the scoping document, the build brief, the gap check | ~5 min |
| 2 | Steps 0 to 2b: the system, the brand sample, the logo, the typeface | ~6 min |
| 3 | **Phase D: the creative director's directions** (references/creative-director.md, Part 1) | ~8–10 min |
| 4 | Steps 2c to 5: the expression from the chosen direction, the transform, both themes; component pages, views and the showcase | ~18–20 min |
| 5 | Step 6: the audit and `$D/scripts/scan.py`; **Step 6b: the creative director's judgement**, at most two rounds | ~8–10 min |
| 6 | Step 7: ship; `check_ds.py` clean; the fingerprint added to the register | ~2 min |

If a run heads past 50 minutes, the usual cause is documentation (long tables, every part on every component) or a
third review round. Cut back to the budgets.

**Reference files, read when the step says:**

| File | Read it |
|---|---|
| `$D/references/creative-director.md` | Phase D and Step 6b; it is the director's whole brief |
| `$D/references/calibration.md` | Phase D and Step 6b; the team's taste: strong and weak past systems, the generic tells |
| `$R` (the shared register, below) | Phase D and Step 7; the apps already made. `$D/register/register.json` is only the seed that `$R` starts from |
| `$D/references/reference.md` | when you design components and write the build plan: the composition model, the view library, the component inventory and its states, the doctrine for forms, components, layout and overlays, the defect register and the hand-over checklist |
| `$D/references/history.md` | only when a rule seems odd; each version names the run that caused it |

> **How this file is layered.** The pipeline (sample, harvest, transform, audit, ship) is unchanged and
> authoritative. Phase 0 reads what the app needs. Phase D sets the idea. Step 2c turns the idea into the
> expression. Step 6b judges the result with fresh eyes. Step 7 hands it all over in one file.

## Locate this skill and the shared register — before the first script call

This skill's scripts, references and assets sit in its own folder inside the plugin, and every path in this file is
written from `$D`. Each shell starts fresh, so **start every command block with these two lines**, as they are:

```bash
source ~/.local/poc-collateral/env.sh 2>/dev/null; D="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/design-system 2>/dev/null | sort -V | tail -1)"; [ -n "$D" ] || D="$(dirname "$(find ~/.claude/plugins -path '*design-system/scripts/check_ds.py' 2>/dev/null | head -1)")/.."; [ -f "$D/scripts/check_ds.py" ] || echo "check: design-system skill folder not found"
R="$HOME/.local/poc-studio/design-register.json"; [ -f "$R" ] || { mkdir -p "$(dirname "$R")" && cp "$D/register/register.json" "$R"; }
```

- **`$D`** is this skill's folder. Read from it; never write into it, because the plugin cache is replaced on every
  update. Every script runs as `python3 -I "$D/scripts/<name>.py" …`, with paths as arguments.
- **`$R`** is the shared register of apps already made. It lives outside the plugin cache so it survives updates; on
  first use the line above seeds it from `$D/register/register.json`. When the orchestrator passes a register path,
  put that path in the `R` line of every block instead of the default. Every `register.py` call and `check_ds.py --register` takes `$R`; nothing writes to
  the seed.
- **The creative director is a separate agent with its own shell.** Run `echo "$D" "$R"` and hand it the absolute
  paths (its brief `$D/references/creative-director.md`, `$D/references/calibration.md`, the register `$R`, and the
  work folder), never `$D` or a relative path.

# GETTING OUTSIDE FACTS · call the `research` skill

**Any web search or outside research this skill needs goes through the `research` skill first.** Run
your own searches only when `research` fails (see "Calling `research`" below). `research` searches, rates the sources and returns an answer with sources, dates,
a strength rating and any gaps. It stays inside the question it was sent. This skill decides what to do
with the answer.

**Reading the client's own site comes first, and research confirms it.** Steps 1, 2 and 2b fetch the
swatch, the linked stylesheet, the font files and the logo directly from the client's site. Research
then confirms what was sampled against a second source, and fills in what the site could not give.
Research also covers facts from outside the conversation: the client's business, an industry process,
a regulation, comparable products, design references, and the client's brand guidelines and tone.

## The research plan — mandatory, before Step 1

Research is not optional and not "when needed". Every run writes a research plan at the end of Phase 0
and completes it before Step 3 (the transform). The plan has two parts.

**Part 1 · Questions every run asks**, whatever the BRD says:

| # | Question | Depth |
| --- | --- | --- |
| 1 | What are the client's brand colours? Confirm the hex values on an official source (the live site's CSS, a brand or press page) and a second independent source | Deep |
| 2 | Which typeface does the client use, who licenses it, and which open substitute matches it? | Deep |
| 3 | Where is the client's official logo file published (site, press kit, brand page, Wikimedia Commons)? | Deep |
| 4 | Does the client publish brand guidelines, and what do they say about tone, colour use and logo use? | Quick |
| 5 | What does the client do, for whom, and which words do they use for their own products, customers and processes? (with wireframes, skip: their copy and the scoping document's seed data already use the client's words) | Quick |
| 6 | **Components.** For this app's main components — the signature (0.8), the main table or list, the agent drawer (0.9), and one more the journey leans on — how do real products and component libraries build the same component? Look at real products in the client's domain first (help pages, product tours, app-store screenshots), then component and pattern libraries: Mobbin (mobbin.com), Page Flows, and the public design systems (Material, Carbon, Atlassian, Polaris). For each component: its states and what each looks like, what hover, selection and keyboard do, how it handles empty, long and many items, and the one idea worth taking. One request per component | At least 3 searches per component (Quick); stop at 5 |

**Part 2 · Questions the BRD raises** (only without approved wireframes; with them, skip Part 2). Read
the build brief and add a question only where the BRD leaves something the design depends on unsaid or thin. **At most three Part 2 questions, each Quick.** For
example:

- personas or jobs are vague → who does this work in this industry, and what do they read most
- the BRD names countries, regulated data or languages → which privacy, accessibility and language rules
  apply, and how dates, numbers and names are formatted there
- an archetype from 0.2 is in play → 3 to 5 polished references for that archetype and data shape
- the BRD names a third-party product the app mirrors or connects to → how that product presents the
  same data, so the terms and statuses match

**A question is done only when it meets its depth:**

| Depth | Minimum before the question is done |
| --- | --- |
| Quick | 3 searches, the pages behind the answer opened and read |
| Standard | 6 searches, at least one official or primary source |
| Deep | 12 searches, at least one official or primary source, and every key fact confirmed by a second independent source |

**Deep is only for questions 1 to 3** (colours, typeface, logo), because a wrong hue or a redrawn logo
is the most expensive mistake this skill can make. **When Steps 1, 2 and 2b already sampled the swatch,
the font files and the logo straight from the client's live site, each of these needs only Quick depth
to confirm on a second source**; Deep applies when the site sample failed or two sources disagree. Everything else is Quick or Standard. **Stop a
question as soon as its minimum is met and the answer is clear** — the minimum is a floor to reach,
and also the point to stop.

**Question 6 feeds the components, not just the record.** The creative director's research in Phase D is separate and
looks wider (the client's world, standout work); question 6 stays on how real products build this app's components. Keep two or three references per component.
Each goes on that component's page under **Reference** (the component page spec), at least two with
their links (`$D/scripts/check_ds.py` counts them): its link, what it does well, and what was taken — a state, an interaction, how a status or an AI value is shown, how
empty or overflow is handled. Take ideas, never colours, logos, artwork or copied markup. Nothing from
a reference adds a colour value, radius or new rule to the core. A reference that changed nothing in
the component is dropped. Mobbin and some galleries need a sign-in and may not load through a fetch:
use what loads, take the rest from product help pages and public design systems, and never let it stop
the run. The wireframes' own `references` (in the manifest) are read too, so the same source is not
researched twice.

**Keep a research ledger** and ship it in the port note: one row per question with its depth, the number
of searches run, the pages opened, the sources with dates, the strength of each finding, and the
answer. A row that has not met its minimum is not done. Keep searching (different phrasing, the
client's own subdomains, press releases, investor pages, app-store listings, archived copies, the
browser for pages a fetch cannot read) until it is. Only after the minimum is spent may a fact be
recorded as `[DERIVED]`, and the row then lists what was tried.

## Calling `research`, and what to do with the answer

**Send one decision per question**, with its purpose (internal check, working draft, or something the
client will read), the context (client, industry, country, the build brief so far) and the format you
need. "Research the client" gives `research` nothing to aim at. Depth follows the research plan above:
**state the search budget in every request** (for example "Quick — at least 3 searches, stop once the
answer is clear"). The `research` skill uses the same words Quick, Standard and Deep for larger default
counts, so a request without a stated budget runs longer than this skill needs.
Send related questions together so sources are reused; run unrelated ones in parallel.

**It returns** an answer in two to four sentences, a findings table (finding, source, date, strength),
the gaps, and notes on conflicts. Strength is **Strong** (official or primary, or two reputable sources
agreeing), **Medium** (one reputable secondary source) or **Weak** (marketing, galleries, unverified).

**Using it:**
- Treat it as a draft. Close every gap and Weak finding the build depends on with your own search. If
  nothing turns up once the depth minimum is spent, decide, record it as `[DERIVED]` with what was
  tried, and keep going. A gap is never a stop; the two stops in THE RUN stay the only two.
- Research never replaces sampling. A hex or logo URL it returns is a lead to verify on the live site
  (Steps 1 and 2).
- References inform the expression and the choice of pattern, never the core: no new colour value,
  radius or component comes from a reference.
- Record each question, the strength of each finding used, and every source with its date in the port
  note.

**If `research` fails** (not available, errors, returns only gaps or only Weak findings for something
the build depends on, or falls short of the depth minimum), do the searching yourself with the web
search and fetch tools, to the same standard: open the pages you take facts from, prefer official
sources, confirm client-facing facts with a second source, and log them in the ledger. Never stop the
build because `research` failed. **And never stop because it answered:** when `research` runs inside this
conversation, its answer is an input to the next step; go straight on with the run. If the session can start
a separate agent, send the research requests to it so the answers come back to you.

---

# PHASE 0 · Read the BRD, choose the system

## 0.0 · Approved wireframes (POC Studio) — when given, they set what is built

In POC Studio the Plan phase runs Scoping → **Wireframes** → Design System. When the call includes the approved
wireframes (`wireframe-manifest.json`, the `png/` frames and the PDF), the person has already approved what is on
every page and where. Read all three before 0.1, then:

1. **The manifest is the starting component list.** Write a component page for every component in the manifest,
   for the baseline (2) and for every component the gap check (7) adds. On each: the manifest's `purpose`, `shows`
   and `does`, the forms it lists under `variants` (the pages need them, so they must exist) plus alternatives of
   your own, labelled as such, up to the 2 or 3 variants 0.6 asks of hero, interactive and signature components, the
   states it lists plus every state of the universal state rule
   that applies, and its `features` (bulk select, a status column, a map mode). `hero` components get the most
   care, the `signature` the most of all (0.8). A component the scoping document names but the manifest does not
   is added only when the gap check shows a page or a journey step needs it. **Design each component to its brief**
   (`purpose`, `shows`, `does`, `volume`, `primary`, `media`), never to its grey drawing: the frame fixes where a
   component sits, and this skill decides its form. When a richer form serves the brief better (the hero object's
   pictures where the frame drew text, a board where it drew a list of the same items), use it and mark the
   section `data-form-change="<what changed and why>"`.
2. **The baseline is always built**, whether or not a frame shows it: the floor in 0.1 (the shell parts the frames
   use, sign-in with forgot and reset password, the four statuses in the domain's words, empty, no-results, loading,
   error and no-access states with wording, a toast with undo, the confirmation modal, every input state, light and
   dark), the agent drawer with its launcher for every agent (0.9), and the kit atoms of "The component inventory" in
   `$D/references/reference.md` (buttons, inputs, status tags, badges and the rest).
3. **The frames are the layouts.** Each page's pattern, region order and region fillers in `#build-plan` come from its
   frame (same page ID). Where a frame shows a slot, the region filler is that slot's component. A pattern blueprint
   is drawn only for a pattern no frame shows. Never re-decide a layout a frame fixes.
4. **The three full screens are frames at high fidelity, in the showcase (0.6):** the home with the signature, the
   main working page (the record or review page where the person does the work), and a page with the agent drawer
   open. Draw each with its frame's regions in the same order, in the chosen direction (Phase D) with real content
   and the hero object pictured. They show how the components sit together; they are a reference for the builder,
   who composes every other page itself.
5. **Maps.** A manifest component with a map `data_contract` gets one map component page that follows the wireframes
   skill's `references/map-component.md`: only the modes the manifest lists; ring, dot, label, site card and route or
   radius anatomy with every state; the legend pill; the floating controls; and the tile tint for light and dark as a
   token-driven filter.
6. **Check by script before hand-over:**
   ```bash
   source ~/.local/poc-collateral/env.sh 2>/dev/null; D="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/design-system 2>/dev/null | sort -V | tail -1)"; [ -n "$D" ] || D="$(dirname "$(find ~/.claude/plugins -path '*design-system/scripts/check_ds.py' 2>/dev/null | head -1)")/.."; [ -f "$D/scripts/check_ds.py" ] || echo "check: design-system skill folder not found"
   R="$HOME/.local/poc-studio/design-register.json"; [ -f "$R" ] || { mkdir -p "$(dirname "$R")" && cp "$D/register/register.json" "$R"; }
   python3 -I "$D/scripts/check_ds.py" <client>-design-system.html wireframe-manifest.json --register "$R"
   ```
   It checks every manifest `component` has a component page (`data-component`), every frame's page ID (without
   its letter suffix: `PG-03b` is page `PG-03`) is in `#build-plan`, every added component carries
   `data-added="true"` and a `data-reason`, each component page draws the manifest's states (`data-states`); the
   direction, thesis, showcase (three `data-screen`, two or three `data-moment`) and review are on the page; the
   signature has its anatomy and two reference links; every capability and journey step has its flow panel with three
   principle cards; the hero object's pictures (`data-media`) are in every screen
   and the signature; the fonts are not a default; the budgets and the richness floor hold (variants, hover and focus
   states, gradients, views); and the fingerprint does not repeat a past app in `$R`.
   Fix every `check:` line it prints. A `skipped (manifest has no <field>)` line is not a pass: do that check by hand
   from the source rule 8 names, and list it in the port note.
7. **The gap check: what the wireframes missed.** The wireframes should name every component, but if one is
   missed the builder will invent it, and an invented component rarely works well. Before designing, walk the
   app and list what the pages still need, from five places:
   - **Each journey step** (the manifest's `journey`): what the person sees and does at that step, and the
     component that shows it. A refusal needs an inline error or a blocked-action message; a hand-off needs
     a toast or a notification; an approval needs its confirm.
   - **Each component's `does`**: every action needs its control. "Filter" needs filter chips or a filter
     menu, "sort" a sort menu, "edit in place" an inline editor, "approve several" a bulk bar, "open" a
     drawer or a link, "chase the owner" a message composer or a confirm.
   - **The scoping document's words**: every status value (§12) needs its tag, every refusal (§14) its
     message, every role without access (§16) its no-access state, every AI value (§17) its marker.
   - **What every working app needs**, whether or not a frame shows it: pagination, tooltips, menus and
     context menus, date and time pickers, file upload, toasts with undo, the confirm modal, skeletons,
     notifications, the avatar and user menu. Most of these are already the baseline (2) and the kit atoms:
     design them there and do not list them as added.
   - **States**: a component the pages show in a state the manifest does not list (a selected row the
     frame shades, a disabled button a gate blocks) gets that state.
   Each addition gets a component page marked **Added by the design system**, with the page or journey step
   that needs it, and goes into the overview's "Added" list. **"Added" means a component the app needs that
   is in neither the manifest nor the baseline** (a reject-with-note popover, an ad-week picker, a plan card
   menu); a baseline atom drawn for this app (a status tag, a toast, a tooltip, a banner, the user menu) stays
   in the baseline. A typical run adds 3 to 8; more than 10 usually means baseline atoms were counted, or a
   feature the scoping document does not build crept in. Add what the pages need and a little more where
   it saves the builder a guess, never a feature the scoping document does not build. The "Added" list goes
   back to the wireframes as a note for their next change.
8. **An older manifest.** The plugin's wireframes skill writes every manifest field this skill reads, but an approved
   manifest from an older POC may lack some. A missing field never stops the run: take it from the scoping document,
   and say in the port note which fields came from where.
   - `hero_object` (top level) and each component's `media` → the scoping document's §21.1 hero object, or the §11
     page's "Hero content" / "What the person must see to decide". When it has a picture, pass its name to the check
     with `--hero-picture "<name>"` so the picture rules still run.
   - each component's `hero` and `signature` → §21.1 and the signature candidates of 0.8 (§21.1 hero object, the §23
     capability inventory, the WOW factor); the components that show the hero object or carry the main journey are the hero components.
   - `purpose`, `shows`, `does`, `volume`, `primary` → the §11 page specification where the component appears, the
     §12 volumes and the component's §23 CMP entry.
   - `cmp` → the §23 CMP list: every CMP ID gets its flow panel (0.6 part 6).
   - `journey` → the demo storyline §20.2 (then the §8 journeys), its steps numbered in order.
   - `payoff_frame` → the §20.2 storyline's turning point; the showcase shows it.
   - `views`, `alt_views`, `png/VIEWS.png` → two or more views per hero data set, chosen from the §11 "What the person must see to decide" lines, the §12 volumes and the view
     library in `$D/references/reference.md`.
   - `nav_options` → the chosen navigation in full and two alternatives of your own.
   - `references` → nothing to reuse; research question 6 finds them.
   `check_ds.py` prints `skipped (manifest has no <field>): <the check>` for every check a missing field turns off.

Without wireframes (a run that skipped them, or a design system made without any), 0.1–0.9 work from the scoping
document alone, exactly as written. **With wireframes, skip 0.2, 0.3 and 0.5** (now in `$D/references/reference.md`, "Without wireframes"; read them only for a run without wireframes): the frames already chose each page's
pattern and views.

**In the automated flow the BRD is a scoping document** — 80 to 130 pages, most of it data model,
workflows, business rules, agent prompts, seed data and sources. Read it as the BRD throughout this
file. Most of it is not visual, and that is exactly why it has to be read whole: the visual facts are
spread through it, and the journeys in it are the richest design input the system gets.

**This runs before THE RUN.** THE RUN (below) skins the system onto the client's brand. Phase 0 decides
*what gets skinned* — which views, which components, at what density — so the build matches the BRD
instead of defaulting to the same glass dashboard every time. If there is no BRD, only a client and a
website, skip to THE RUN and use the use-case dial defaults; Phase 0 is what a real requirement unlocks.

**The discipline is the same as Step 0's:** decide, record the decision, keep going. Phase 0 produces a
short **build brief** that every later step and the hand-over cite. It never asks the user more than the
two stops already allow.

## 0.1 · Parse the BRD into a build brief

**With approved wireframes, read only what the design system needs from the scoping document**, and fill
the build brief from it and the manifest:

| Scoping section | What the design system takes |
| --- | --- |
| Research findings and brand cues (§6), hand-off to the design system (§21) | brand inputs as evidence, light-to-dark balance, vibe |
| Hero object (§21.1), reference products (§21.2), each page's "What the person must see to decide" (§11) | the thing users judge and how (its picture, document or place), the evidence each screen must show, research leads for Phase D |
| Personas (§7) | density, device and default theme per persona (0.4) |
| Data model (§12) | every status value in its own words with its tone (positive, attention, negative, neutral), the picture, document and location fields, UNSET fields, volumes |
| Agents (§13), AI trust and governance (§17) | each agent's name and outputs, the AI marker, confidence, the human-in-the-loop moments |
| Workflows, rules and scoring (§14) | refusal messages and gate wording, word for word |
| Roles and permissions (§16) | read-only and no-access states and their wording |
| Seed data (§19) | the demo day, real content for specimens and screens, the worst real record. Where the seed does not give a number a specimen needs, derive it from the document's formulas; any value you invent is listed in the port note with what it stands for, so the build can replace it |
| Demo storyline (§20.2) | the moments the three screens and the agent drawer must show |

Everything else (pages, layouts, journeys, components) comes from the wireframes. The full read below is
for a run without wireframes.

**Without wireframes, read the whole BRD, end to end, before deciding anything.** Every section, table, appendix, data
model, automation, agent instruction and prompt, and every stakeholder note. Design facts hide in
unlikely places: a theme line in application settings, a chart tool in an agent's tool list, a status
value in a data model, a route list, an error message in a test case. Do not skim for the screens
alone. Record what you extract, mark anything you inferred `[DERIVED]`, and keep going.

```
DOMAIN          what the app is about (AP invoices, recruitment, churn, logistics…)
PERSONAS        who uses it, and their role (analyst, approver, exec, agent-operator, external user)
JOBS            the handful of things each persona comes to do
SURFACES        which surface archetypes the jobs imply (see 0.2)
SCREENS/ROUTES  every screen, route, overlay and modal the BRD names, including sign-in and recovery
VIEWS           which view-types the data and jobs require (see the view library in `$D/references/reference.md`)
DATA SHAPES     records · time series · relationships · stages/process · locations · documents · hierarchy
DATA VOLUMES    how many records, rows, items — decides paging, density and summaries
STATUSES        every status value and state word the BRD or its data model uses, in its own words
EDGE STATES     empty, no-results, loading, error, stale, locked, unset, no-access cases the BRD mentions
AGENT OUTPUTS   every agent and automation, its tools and what it can produce (see 0.3)
INTEGRATIONS    the systems the app reads from or writes to, and their terms
BRAND INPUTS    any colour, logo, typeface, theme, radius, tone or design system the BRD supplies
DEVICES         screen sizes, desktop or phone, light or dark
REGION/LOCALE   LTR/RTL, language, any compliance that touches the UI
CONTRADICTIONS  where the BRD disagrees with itself — each resolved and recorded as a derived decision
UNKNOWNS        what the design needs and the BRD does not say — each becomes a research question
OUT OF SCOPE    what the BRD does NOT ask for — stated explicitly
```

**When the BRD is a scoping document, read these sections for these fields** (section numbers follow
the usual template; find the equivalent if they differ):

| Scoping section | Feeds |
| --- | --- |
| Executive summary, context, pain points (§1–§3) | DOMAIN, the WOW factor, what the demo must prove |
| Scope, asked vs scoped, live vs simulated, decisions (§5) | OUT OF SCOPE, CONTRADICTIONS, what is real and what is staged |
| Research findings and brand cues (§6) | BRAND INPUTS, competitors for research question 6 |
| Personas (§7) | PERSONAS, DEVICES, density and shell per role (0.4) — every persona, not the first three |
| Journeys and workflows (§8) | JOBS and the flows in 0.7 — every journey, every step, every exception |
| Solution overview, global conventions (§9) | SURFACES, the app map, navigation, global elements |
| Feature catalogue (§10) | VIEWS; every must-have (L1) feature ID |
| Page specifications (§11) | SCREENS/ROUTES, what each page must do and show, key states |
| Data model, allowed transitions (§12) | STATUSES in their own words, state machines, UNSET fields |
| Agents (§13) | AGENT OUTPUTS, the agent drawers in 0.9 |
| Workflows, rules and scoring (§14) | refusal messages, gates, thresholds, what turns a status red |
| Roles and permissions (§16) | role shells, read-only states, no-access wording |
| AI trust and governance (§17) | the AI marker states, confidence display, human-in-the-loop moments |
| Non-functional notes, seed data (§18–§19) | DATA VOLUMES, sample content, hero records the specimens use |
| Demo storyline (§20) | which flows and screens carry the demo; the order the style guide follows |
| Hand-off to the design system (§21) | BRAND INPUTS, vibe, hero object and visual objects (§21.1), reference products (§21.2), key states, interactions |
| Capability inventory (§23) | signature-component candidates (0.8); every CMP ID gets a specimen (with wireframes: every manifest component; 0.0) |

**Every must-have (L1) feature ID and every CMP ID maps to at least one inventory row (0.6)** (with wireframes, the
manifest is the inventory and its coverage was checked at the wireframe stage: 0.0). Nothing
the document builds now is moved to "future scope" by this skill. Where the document itself marks a
feature future scope, it stays dormant.

**Go beyond the document, inside its fences** (only without wireframes; with them, the approved frames are the
scope and nothing is proposed: 0.0). The scoping document is the floor, not the ceiling.
After the read, ask: what would make each persona's main journey faster, clearer or more convincing
in a demo? Add those as **proposals** — a view, a variant, a state, an interaction — drawn and labelled
`Proposed` on the page, each with the persona and journey it serves. A proposal never contradicts the
out-of-scope list, never adds a live integration, and never replaces what the document specifies.

**Correct the document where it would hurt the app.** Scoping documents are written fast and
sometimes ask for something that breaks a doctrine here — an agent as a full-width card on a page, a
status shown by colour alone, a drag with no keyboard path, a chart that colours a delta by its sign.
Follow the doctrine, draw it correctly, and record the correction in the port note with the line it
replaces. The document's intent wins; its wording does not.

**Where each fact comes from, in order:**

1. **The BRD.** What it states is used as stated. Research never overrides a requirement.
2. **The `research` skill**, for every UNKNOWN and for the six questions every run asks (see the
   research plan).
3. **Your own web search and fetch**, when `research` fails or falls short, held to the same depth
   minimums and source standards.
4. **A derived decision**, only after 1 to 3 are exhausted, recorded with what was tried.

Brand inputs follow their own order — the brand source order in Step 1 — because a brand can be
current in two places at once (a deck and a website) without either being out of date. Where the BRD's
brand input is **demonstrably retired** (a rebrand dated after it, a logo the client no longer uses),
use the current brand, say so in the port note, and name the BRD line it replaces.

**The out-of-scope line is load-bearing.** It is how the build stays inside the requirement. A BRD for
an approval queue does not get a map, a chart wall or a chat just because the system can produce them.
Scope creep in a POC reads as "they didn't understand what we asked for."

⚠️ **A thin or messy BRD is the normal case, not an error.** Do not stop to interview the user; the two
stops in THE RUN are still the only two stops. Fill the gaps instead:

1. **Every empty field the design depends on becomes a research question** (Part 2 of the research plan:
   Quick, at most three; any further gap is decided and marked `[DERIVED]`). For example: no personas → who does this work in this industry and what do they
   read most; no statuses → which states this kind of record moves through in this industry; no
   volumes → typical record counts for a company of this size; no devices → where this kind of user
   works.
2. **Use what comes back to complete the brief**, marked `[DERIVED]` with its source, so the build
   brief has every field filled before Step 1.
3. **Sample content comes from research question 5** (the client's own business and terms), never from
   lorem ipsum or a generic company.
4. **Apply the floor below**, whatever the BRD leaves out.

**The floor — every build carries these, even from a one-paragraph BRD:**

- the app shell: left navigation with the logo, top bar, profile menu
- sign-in, with forgot-password and reset-password
- the main record list with its toolbar, search, filters and paging, and the record's detail view
- one primary form with validation, and every input state
- the four statuses (positive, attention, negative, neutral), named in the domain's own words
- empty, no-results, loading, error and no-access states, each with wording
- a toast with undo, and a confirmation modal for the one irreversible action
- light and dark, both reachable
- every component used, in every state of the universal state rule

The floor is the minimum, not a cap. Add what the brief and research call for; leave dormant what
neither does.

## 0.4 · Persona → density, device and shell

Set the information density from the primary persona, then let the use-case dial and the density tokens
(`$D/references/reference.md`) carry it:

- **Analyst / power user** → compact, keyboard-first, more on screen, fewer labels.
- **Occasional / external user** → spacious, guided, more labels and help.
- **Executive** → summary-first, few actions, headline numbers over raw rows.
- **Field / mobile user** → one column, thumb-reach actions at the bottom, large targets, glanceable
  status, camera and upload first, works in bright light.

**Then do it for every persona, not only the primary one.** Each persona gets a row in the build brief:
density, device and width (phone 375 px, tablet 768 px, laptop 1,280 px, wide 1,440 px), default theme,
and **its own shell** — which navigation it sees, what its first screen is, and how it reaches each
screen it uses. A persona who works on a phone or tablet gets real layouts at that width, with their
own navigation (bottom tabs on a phone, a collapsed rail on a tablet), not a desktop screen shrunk.
An external persona (customer, partner) gets its own lighter shell. **A persona whose screens are not
reachable from a shell has not been designed.**

**Shells are shown through the three screens (0.6), not drawn separately.** With wireframes, each
persona's shell is in its frames; a persona whose shell is not in the three screens is covered by its
frames and one line in the build plan. Without wireframes, such a persona gets a **shell blueprint**: its
navigation, first screen and regions as a labelled diagram, not a drawn screen.
Responsive behaviour is one line per shell (rail collapses to icons under 1,100 px; bottom tabs under
600 px). Device specimens use `<template class="device">` (Step 0's kit), never a narrowed `<div>`.

## 0.6 · The deliverable — the idea first, then a rich kit: draw more, write less

**Write a page inventory, not a page gallery.** One row per page, overlay and screen the brief names, recording what
the builder needs to compose it; every manifest component and every frame's page maps to a row. It goes in the Build
section at the end, never at the top.

**The file reads like a product site that happens to be a design system.** Its sections, in this order:

1. **Cover** — the logo, the app's name, the big idea in one line and one striking view of the hero object. Never a
   table of source files (that goes in the port note).
2. **Direction and thesis** (`#direction`, `#thesis`) — the chosen direction with its wow moment, the two not chosen
   in one line each (`data-option` on all three, `data-chosen` on one), and the thesis: 3 to 5 rules that only fit this
   client.
3. **Showcase** (`#showcase`) — the three full screens (`data-screen="1|2|3"`: the home with the signature, the main
   working page, a page with the agent drawer open), each the frame's layout at high fidelity in the chosen direction
   with real content and the hero object pictured; then **two or three close-ups** (`data-moment`) where the idea is
   strongest (a component in the state that tells the story, an interaction mid-way, the hero object at its best).
   This is what a sponsor scrolls first.
4. **Views and navigation** (`#views`) — the app's page types and the ways to look at its data, drawn with real
   content: every hero data set in each of the views the manifest lists (`views`, `alt_views`; the wireframes' `png/VIEWS.png`
   shows the ones not framed, and a `payoff_frame` shows the story's best moment, which the showcase should include), at least two views
   each, each marked `data-view="<component>:<view>"` (a wall, a table, a board by owner, a timeline by lock, a
   gallery, a compare); the navigation options the wireframes drew (`nav_options`), the chosen one in full and the
   others as smaller drawings, each marked `data-nav`, with what each is for; and the page types the app uses
   (queue, record, review, board, dashboard), each as a small composed thumbnail. This is where the builder sees the
   app's variety.
5. **Foundations, with the expressive layer** — colour with measured ratios, type, spacing, shape, material and
   elevation in both themes, motion (one table for the whole kit), icons, imagery rules; and **the expressive layer**
   (`#expressive`): the brand gradients (at least two, each `data-gradient`, built from the client's real colours,
   with where each is used: a hero band, a selected card, a chart fill, an empty state), depth (how cards lift on
   hover, what glows on focus), the selected and active treatments, one empty-state illustration in the brand's
   language, and the chart palette. A thesis may keep the accent rare; it never leaves the app without colour
   moments, depth or motion. Drawn, not described.
6. **Flows, at component level** (`#flows`) — **the heart of the file.** The wireframes show each page whole; this
   section shows **each job the person does**, at the scale of the components that do it: one flow panel per
   capability in the manifest (its `cmp`), grouped under 3 to 6 job headings in the client's words (for a product
   company: "Stage gates, samples and the critical path", "Readiness, assets and variants at scale"). Each flow panel:
   - **a title** in the person's words ("Product page preview and retailer validation", "Line plan board");
   - **a composed working unit**: the 2 to 5 components that do the job, put together the way they work together,
     live, with real seed data, the hero object pictured, and the controls the job needs (the switch between
     channels, a version toggle, the safe-area guide, the view switch), drawn in the state that tells the story (a
     check failing beside the thing it fails on, a moved tile ringed, a callout numbered on its drawing);
   - **three principle cards** under it: a short title that states the UX decision ("Preview the channel, not the
     record", "Every failure points at the page", "Fix where it fails") and two sentences on what it means and why.
     These are the thinking a reviewer used to bring.
   Mark each panel `data-flow="<CMP id>"`, `data-uses="<component>,<component>"` and `data-journey="<step numbers>"`,
   and each card `data-principle`. A panel is never a full page (the three screens are) and never one component
   alone (the component pages are): it is one job, end to end, at the size it is read. **Give each component in a
   panel its real width** (stack them, or let the panel run full width) so nothing is squeezed or cut off, and **say
   each thing once per panel**: a record shown in the panel is not shown again as a card beside it. `check_ds.py` checks that every
   capability and every journey step has its panel, that each panel uses two or more components and carries three
   principle cards, and that every hero component appears in a panel.
7. **Components** — the signature first, at full depth (0.8); then **up to five key components** (the manifest's
   `hero` components first; six full-depth pages in all, fewer only when the app has fewer hero components) at full
   depth too; then every other component on its page (below), grouped as
   the inventory groups them. The flows show components working together; the component pages stay compact and
   carry what a flow cannot show (every state, variants, rules).
8. **Journey** — the journey-to-component table (0.7).
9. **Build** — the page inventory, the composition contract, `#build-plan`, `#style-sets`, the token block, the logo
   kit, the port note and research ledger, the review (`#review`, Step 6b) and the hand-over.

**Draw more, write less.** The budgets limit writing, never drawing: at most **12,000 words** of visible text and at
most **24 tables** (`check_ds.py`), and at most **70,000 px** of page height at 1,440 wide (`scan.py`; the flow
panels take room, and they are worth it). A strong past
system did it in about 5,000 words and 13 tables, with dozens of drawn views. **The richness floor** (`check_ds.py`):
at least **25 distinct variants** (`data-variant`), every interactive component's state grid drawing hover and focus,
the expressive layer with two or more gradients, and the views section. A file under the floor reads as plain, and
the team rejected that as firmly as it rejected length.

**The component page.** Every component page has these parts, each marked with `data-part`; the full-depth pages add
anatomy and the eight points of 0.8:

1. **Header** — name and code, one line on what it is for, and its source: the manifest, the baseline, or **Added by
   the design system** with the step that needed it (`data-added="true" data-reason="…"`). A form that differs from
   its frame says so in one line (`data-form-change="…"`).
2. **Specimen** (`data-part="specimen"`) — the real component, large enough to read, with real seed data and the hero
   object's picture where it shows (`data-media` on each picture), live to hover, focus and press.
3. **States** (`data-part="states"`) — one grid at the component's real width, labelled, each state drawn once and
   drawn so it shows: default, **hover** (the lift, tint or glow the expressive layer gives it), **focus-visible**,
   **pressed**, **selected**, disabled, loading, empty, error, read-only, drag where it drags, and the domain's own.
   Every interactive component (one with `does` in the manifest) draws at least hover, focus-visible, pressed and
   selected where they apply. A state that differs only in one cell shows that cell, not the whole row again.
4. **Variants** (`data-part="variants"`) — **2 or 3 for every hero, interactive and signature component** (a static
   atom with nothing in `does`, such as a divider or a count dot, keeps one form): the forms the manifest lists plus
   your own, each visibly different in a way a reviewer sees in one second (dense row vs picture card; inline legend
   vs legend below; compact vs comfortable; light vs on the brand gradient), each with its code (`data-variant`, coded
   as Step 2c says) and one line on when to use it; the active one marked **Recommended — used in this app**
   (`data-active="true"`), the others **Reference — not in this app**.
5. **Rules** (`data-part="rules"`) — three to five lines: behaviour, content limits and truncation, the keyboard and
   screen-reader essentials, and the one mistake to avoid. Where it is used, in one line.
6. **Reference** (`data-part="reference"`), for the components researched under question 6: two links, what each
   does well, what was taken.

Anatomy with numbered callouts (`data-part="anatomy"`) is drawn for the signature and the up to five key full-depth
components (six in all). Micro-interaction timings, sizes and accessibility rules shared by the whole
kit are stated once in Foundations, never repeated per component. **The section carries
`data-component="<manifest name>"` and `data-states="<the states it draws>"`; the signature's section also carries
`data-signature`.** `$D/scripts/check_ds.py` reads them.

**Explore, then choose.** For each hero component, try more than one form before settling (the research references,
the direction, the manifest's views) and show the ones not chosen as labelled variants. A design system that shows
one answer per component hides the thinking the reviewer wants to see.

**Show components inside the work.** A specimen sits on its real surface with the client's real content, and where
the component lives beside others (a row in its table, a card on its board), show it there. A component drawn alone
on grey teaches the builder less than one drawn in context.

"Finished" means: the direction and thesis are on the page, the showcase is drawn, every needed component has its
page (the manifest's, the baseline and the added ones), every capability has its flow panel, the views and expressive
layer are drawn, the richness floor
is met, every journey step maps to its components, the budgets hold,
the review passed (Step 6b), and the contract is quoted.

## 0.7 · Journeys → the journey-to-component table

**The journeys are where the scoping document already describes the design.** A journey step that says
*"clicks Move stage → refused: 'No approved Fit or SMS sample'"* is an interaction specification. With
wireframes, the journey is the manifest's `journey` (each step and its frame); without them, the
scoping document's §8 journeys and §20.2 storyline.

**Walk every journey step and write one row per step** in a table on the overview:

| Step | Page (frame) | Component(s) | State it is in | What the person does | What they see next | Exact wording |
| --- | --- | --- | --- | --- | --- | --- |

**Rules:**

- **Every component is used, and every step has its components.** A manifest component no step or page
  uses is questioned in the port note; a step whose component is missing is a gap (0.0 rule 7), added
  before designing.
- **Exact wording is mandatory.** Every refusal, toast and message the document gives appears in the row
  word for word, and on the component page of the component that shows it.
- **Cross-persona hand-offs** name the component that carries the work across (a notification, a toast,
  an assignment chip).
- **Default interactions are not repeated per row.** Hover and focus on everything clickable, a loading
  state between action and response, an empty first run and an undo after a reversible action are stated
  once, in the composition contract.
- The table replaces the flow diagrams earlier versions drew: it carries the same information and checks
  the components at the same time.

## 0.8 · Signature components — depth where it matters

**Every domain has two or three components that carry the product.** Shelf compliance has the shelf
photo with evidence boxes. Product creation has the colour-checked image studio and the stage gate.
Recruitment has the ranked shortlist with explained scores. Delivery has the risk grid and the change
approval chain. Generic parts — tiles, tables, tabs — are carried by the kit; signature components are
where the client sees that we understood their work.

**Choose them** from the manifest's `signature`, the hero object (§21.1), the capability inventory
(§23), the WOW factor in the executive summary and the demo storyline. Name each in the build brief
with the reason.

**Specify each one in depth, on the page:**

1. **Anatomy** — every part named, with the token it uses and its measured contrast.
2. **Every state** of the universal state rule, plus its domain states (for a shelf photo: analysing,
   scored, retake needed, low confidence, override pending).
3. **Data variants** — empty, one item, typical, many (the document's real volumes), overflow, very
   long text, missing image, the worst real record in the seed data.
4. **Interactions** — what each click, hover, drag and key does, with the keyboard path and the
   non-drag alternative; what is selected, what is linked (tap a finding ↔ highlight its box).
5. **Responsive** — how it reflows at each persona's device width (0.4).
6. **Motion** — what moves, why, how long; nothing decorative.
7. **AI behaviour** — where the AI marker sits, how confidence shows, how a person accepts, edits or
   rejects, what an AI failure looks like.
8. **Variants** — at least two layouts for different contexts (a full view and a compact card; a
   desktop panel and a phone sheet), so the builder has the right one for each page (with wireframes,
   the forms the manifest lists for it come first; 0.0).

Document each signature component on its own full component page, drawn large, with real seed data, in its states and variants. **A signature
component drawn once, at one size, in its happy state, is a generic component with a new name.** The signature's
page is the deepest page in the file: anatomy (`data-part="anatomy"`), the eight points above, and a reference
part with at least two links; its section carries `data-signature`. It shows the hero object as users judge it
(pictured, when it has a picture) and takes its form from the chosen direction (Phase D).

**Signature components take their form from the design concept** (Step 2c): they are where the
concept is most visible. **They may introduce new composition** — a new layout of existing atoms, a new
overlay on an image, a new arrangement of a grid — but never a new colour value outside the transform,
a new radius, a third elevation or a new type size. That is where the expression of depth lives.

## 0.9 · Agents → the agent drawer

**Every agent the document names gets the agent drawer** (`$D/references/reference.md`, "The agent component"), with
that agent's name, scope, suggested prompts from the document, a real question from a journey, its
working stages and its answer rendered with its own output types (0.3) — chart, table, file, citation,
proposed action. **The main agent is shown open on the third screen**, over the page its wireframe drawer frame
shows, with the same messages. Every other agent is
documented on the agent-drawer component page as the drawer alone, with its own content, so no extra
screens are drawn.

- **The drawer is the default for every agent, on every page.** If the document puts an agent on a
  page as a card or a full-width block ("Copilot full width on Home"), draw it as the drawer, give
  it the app's one way in (below), and record the correction (0.1). A
  dashboard may keep an **AI insight card** that summarises; the conversation still opens in the
  drawer.
- **One way in to the agent, never two.** Choose exactly one visible entry for the whole app and record it as
  `app.agent_entry` in `#build-plan` and as `data-agent-entry` on `<html>`:
  - `topbar` (the default when the shell has a top bar or band): an "Ask Copilot" button in the bar, marked
    `data-agent-button`; no floating launcher anywhere;
  - `launcher`: the floating `.agent-launch` button only, for a shell with no room in a bar (an icon rail with no top
    bar) or a phone; no button in the bar;
  - `command`: the command field of a `command` shell asks the agent; neither a bar button nor a floating launcher.
  A keyboard shortcut may open the drawer in every case, because it is not a second button. Two visible ways in to
  the same agent read as two different things, and `check_ds.py` fails the file when both appear.
- **One drawer per agent family**, opened from the app's one entry on every internal page, with the current
  page's record as context.
- **Specify that it is built on the platform's live agent component** — streamed replies, real
  stages, tool outputs rendered in the thread. Never an automation that writes the answer to an
  object which the page shows after a refresh. The composition contract (Step 7) carries this line.
- **Agents that act** (approve, move, send) show the proposed action inside the drawer as a
  human-in-the-loop card, before and after, with approve and reject; nothing happens without it.

---
## Answering the AI PM (POC Studio, v1.0)

The orchestrator may call this skill again with the AI PM's findings (`<workspace>/reviews/design-system-review-<n>.yaml`)
instead of a fresh task. Then:

1. **Fix only what is listed.** Edit the existing output in place: the named sections and specimens of the one HTML file only, byte-for-byte elsewhere; leave everything else exactly as it was. Do
   not re-run the whole pipeline for a handful of findings.
2. **Answer every finding** in `<workspace>/reviews/design-system-response-<n>.yaml` (same `n` as the review):
   ```yaml
   responses:
     - { finding: F1, status: fixed,    where: "<section / page / specimen / scene>" }
     - { finding: F2, status: disputed, reason: "<the evidence: an E-, S-, A- or D-ID, a stated ask, a human decision>" }
     - { finding: F3, status: deferred, reason: "<non-blocking only>" }
   ```
   Dispute when the finding is wrong for this client, and say why with evidence; a dispute without evidence is
   treated as `fixed` and checked. Never dispute a finding that cites a human decision.
3. **Re-run your own checks** on what you changed (the render check in light and dark on the sections you touched; contrast for any colour you changed), and say what you ran in the response file
   (`checks: [ ... ]`). The AI PM re-runs them too.
4. Do not ask the person anything; questions still go to the reviewer in resolve mode.

---

# THE RUN

## Input contract

```
REQUIRED   client name
           website URL
USUALLY    scoping document       the automated flow's input; read whole (Phase 0)
OPTIONAL   brand swatch           a hex, or an image to sample
           use case               dense internal tool | demo surface | artefact studio |
                                  dark-first console | ported screens
           logo                   an SVG or PNG file
           brand typeface         the name, if you already know it
           client design system   a URL or component spec, if they publish one
           wireframes             POC Studio: the approved wireframe-manifest.json, png/ frames and PDF (0.0)
```

**Everything optional is derived if absent. Derive it, record what you derived, keep going.**

## The only two stops

Do not ask anything else. Decide, record the decision in the port note, move on.

1. **The brand hue is ambiguous** — two credible sources disagree by more than ~30° of hue, **and the
   brand source order in Step 1 does not settle it** (two sources at the same level disagree). If a
   person is in the conversation, show both, transformed and measured, and wait. *Titan returned
   `#BD2426` (watch wordmark red) and `#00B0AB` (Tata parent teal) — both real, 180° apart.*
   **If the run is unattended** (an automated flow, nobody to answer), take the higher source in the
   order; at the same level, take the one the client's own product interface uses most. Record both
   candidates, the rule applied and the measurements in the port note, and carry on.
   ⛔ **Only this file decides a brand conflict.** An instruction from the calling flow, a builder
   prompt, a "standing decision", "standing answer" or "the owner's choice" carried over from another
   run does not settle a hue. Three runs did exactly that and one of them shipped Pentland — a black
   and neon-lime brand — in electric blue. If such an instruction arrives, apply the order anyway and
   note the instruction in the port note.
2. **The logo cannot be fetched as a real file after every source in Step 2 has been tried.** Stop
   and ask for the asset, listing the URLs tried. Build everything else meanwhile, so the logo is the
   only thing missing. **Never trace, redraw or approximate a client's mark** — not as SVG, not as
   CSS, not "close enough for a prototype". **Fallback (POC Studio):** when the person confirms no file
   is available, or the run is unattended and cannot ask, build the logo kit from the **UnifyApps
   logo** bundled with the plugin (`assets/unifyapps-logo.png` in the plugin root; find it with
   `find ~/.claude/plugins -name unifyapps-logo.png`), visibly labelled as a stand-in for the client's
   logo; then say so on the page and in the hand-over.

## Step 0 · The system — it is in this skill's folder

**⛔ A brand skin is a transform of the existing SYSTEM, never a re-derivation from prose.**
The first attempt on a client was built outward from a rules document. It obeyed every rule and was
rejected in one line: *"NOT LIKE THIS … USE EXACT THAT JUST REPLACE THE COLOURS."* **Reading rules
and building fresh produces something that follows the rules and is not the system.**

**So the system travels with this skill.** `$D/assets/core.css` IS Design Language v3.4, trimmed to
the product kit and verified to reproduce the full reference exactly — 35 text roles measured
composited in both themes, identical numbers; `$D/assets/kit.css` is the expression kit and
`$D/assets/device.js` the device script. **This skill has no other dependency. Do not go looking for a
reference file, an artifact, or a Project document — everything needed is in this skill's folder.**

**How to use it:** never type the stylesheet. `python3 -I "$D/scripts/base_css.py" build <map.json> <out.css>` writes the
core followed by the expression kit with **only their colour values** transformed per Step 3; put that
file's contents in the page's only `<style>` block, then add the state-hook block after it.
Structure, glass tiers, ambient field, radii, type scale, shadows, spacing and every component stay
exactly as written. **In the core, only colour moves.** The expression kit is how the system varies
per client: it carries sanctioned variants (shell, chrome, surface, the agent drawer) switched by
attributes on `<html>`, chosen in Step 2c. **Choosing among the kit's variants is expression; writing
a new structure outside them is a second system** — the failure the next paragraph warns about.

⚠️ **Never rewrite a component from the prose in this file when a class for it exists in `$D/assets/core.css` or `$D/assets/kit.css`.** The
prose states *why* a component behaves as it does; the stylesheet states *what it is*. A second
implementation is how one design system quietly becomes two — it is the most common failure on this
work, and it shows up as mixed radii and two kinds of search field on one screen.

### The class inventory — call these, never write a second set

| Piece | Class |
| --- | --- |
| Glass tiers · padding · nested rung · solid | `.g1` `.g2` `.g3` `.pad` `.pad-s` `.inner` `.solid` |
| Ambient field (3 fixed layers) | `.amb.a` `.amb.b` `.amb.v` |
| Type | `.title` `.micro` (mono eyebrow) |
| Buttons · tags · pips | `.btn` `.btn-p` `.btn-s` `.btn-t` · `.tag` + `.neutral/.attention/.negative/.positive` · `.pip` |
| Table toolbar · search · facet · card · grid | `.toolbar` `.field` `.chipsel` `.tblwrap` `.tbl` |
| Pagination | `.pg` `.pgb` `.rng` |
| AI Insight (scoped, see below) | `.ai:not(.msg)` |
| Tiles · loop strip · empty | `.tile` `.loop` `.empty` |
| Fused tabs | `.tabs` `.tab` `.tabpanel` |
| Forms | `.fld` `.ctl` (+`.focus/.err/.warn/.off`) `.hint` `.seg` `.tog` `.opt` `.box` `.dot` |
| Steppers · progress · reasoning stages | `.sth` `.stv` `.prog` `.stages` |
| Copilot | `.canvas` `.convo` `.msg.me` `.msg.ai` `.chips` |
| Kanban · calendar · agenda · slots | `.kb` `.cal` `.agenda` `.slot` |
| Person card · face stack · avatar | `.pc` `.faces` `.av` |
| Activity feed | `.feed` `.fi` `.fd` |
| Chart frame · sparkline · delta · legend | `.chart` `.spark` `.delta` `.legend` |
| Toast · menu · breadcrumb · note | `.toast` `.menu` `.crumb` `.note` |
| **App shell** (kit) | `.app` (+`.with-agent`, `[data-shell="top"]`) `.app-rail` `.brand` `.nav-i` (+`[aria-current="page"]`) `.prof` `.app-main` `.app-top` (+`.scrolled`) `.app-body` `.app-tabs` |
| **Agent drawer** (kit) | `.agent-launch` `.agent-drawer` (+`[data-open]`, `.wide`, `.docked`) `.ad-hd` `.ad-name` `.ad-tools` `.ad-ctx` `.ad-thread` `.ad-dock` `.ad-composer` `.ad-out` `.ad-action` `.ad-diff` |
| **Expression switches** (kit, on `<html>`) | `data-chrome="brand / ink / light"` · `data-surface="glass / solid / paper"` · `data-density="compact / comfortable"` · `data-style-set="S1/S2/S3"` · `data-theme` · `--font-display` · `--signal` · `--paper` |
| **Overlays** (kit) | `.scrim` · `.modal` (+`.s`, `.l`) · `.drawer` (+`.s`, `.l`) · `.ov-hd` `.ov-t` `.ov-sub` `.ov-x` · `.ov-bd` · `.ov-ft` (+`.lead`) |
| **Spacing and density** (kit) | `--s-1…--s-12` · `--page-pad` `--section-gap` `--card-pad` · `--row-h` `--cell-px` `--cell-py` · `--ov-s/m/l` `--ov-pad` · `--content-max` |
| **Dense data** (kit) | `.cl` `.cl2` (`--col-w`) · `.cell-chips` `.more` · `.tblwrap.freeze` · `.row-x` `.xp` · `.dl` · `.cv` `.cv-tag` |
| **Specimens** (kit) | `<template class="device" data-device="desktop / wide / tablet / phone">` → `.device-wrap` · `.devices` · `.frame` (components only) |

**Not in the kit, by choice** — the artefact studio, command palette, notification tray, diff view,
bulk bar, slider and file drop. They are rare enough that carrying them costs every run. **Build them
from the tokens and the doctrine in `$D/references/reference.md`, never with new colour values**, and if one
recurs across two builds, add it to the kit.

⚠️ **`.ai` vs `.msg.ai`.** The AI Insight card is `.ai:not(.msg)` and agent chat bubbles are
`.msg.ai`. An unscoped `.ai` rule renders **every conversation turn as an AI Insight card** —
invisible in light, obvious in dark. The kit is already scoped; keep it that way.

### The stylesheet

**Run `python3 -I "$D/scripts/base_css.py" inventory` first** (with the two lines from "Locate this skill"). It lists
every colour in the core and the kit by family (blue, cerise, positive, attention, negative, neutral) with the counts:
the core carries 47 distinct hexes, 26 `rgb()`/`rgba()` triples and 9 bare `--aur` triple declarations; the expression
kit adds 12 hexes (one of them the `.media-well` ground) and 7 triples. Step 3 turns the inventory into a map and the script applies it, then prints the
counts before and after, every colour it moved with its luminance before and after, and the largest
change for the port note. The file is `$D/assets/core.css`; read it only to look up a class.

### The expression kit — written by the same script, after the stylesheet

`$D/assets/kit.css` (spacing and density tokens, the app shell, the agent drawer, overlays, dense data,
device frames and the expression switches). `base_css.py build` writes it after the core in the same
output, transformed with it.

**What the kit fixes, from the four runs:**

- **The rail runs the full height, always.** `.app-rail` is sticky at `height:100vh` inside a grid, so
  it never stops halfway down a long page (Pentland's rail ended at 750 px).
- **The top bar is opaque.** `.app-top` paints the solid rung over the page ground, so content never
  slides visibly under it and collides with the title (Pentland). Add `.scrolled` once the page has
  scrolled, for the shadow.
- **The agent is a drawer.** `.agent-drawer` slides in from the right over the page (the default),
  widens with `.wide` for charts and tables, or sits in the layout as a third column with `.docked`
  inside `.app.with-agent`. It is opaque, so text on it measures against one ground. On a phone it
  fills the screen.
- **Phone and tablet are part of the shell.** Under 1,100 px the rail collapses to icons (labels in
  `.lbl`, the wordmark in `.brand .word`); under 760 px it is replaced by `.app-tabs`, a bottom tab bar
  with 52 px targets.
- **In dark, the brand rail stays deep.** `--rail-deep` and `--rail-deep-2` are their own tokens in
  both themes (transformed like every other colour), so the rail does not turn pale when the dark theme
  lightens `--sp-deep`. No `color-mix()` anywhere: in a browser without it the rail rendered
  transparent.
- **Every screen that is drawn is drawn at its real width, in a device** (which screens are drawn
  at all is decided by 0.6 and its budget, not by this rule). Media queries answer the window, not a
  box, so a "1,280 px" screen drawn inside a 1,000 px guide column gets the desktop layout at the wrong
  width: the v5 runs squeezed state screens to one word per line and let a docked Copilot eat the page.
  **Every screen specimen** — desktop, wide, tablet, phone — goes in `<template class="device"
  data-device="desktop|wide|tablet|phone">`. The device script below renders it in an `<iframe>` at its
  true width (1,280, 1,440, 820, 390 px) with the page's own stylesheet, **scales it to fit the guide**,
  sizes desktop screens to their content height (`data-height="700"` fixes a height), and keeps the
  theme, chrome, surface, density and style set in sync. `.frame` remains only for a component shown
  without its screen.
- **Overlays share one system.** Modals (`.modal`, sizes `.s` 420 / default 560 / `.l` 760 px), side
  drawers (`.drawer`, same three sizes, always full height) and the agent drawer (420 px, `.wide` 760 px)
  use the same width tokens (`--ov-s/m/l`), the same anatomy (`.ov-hd` title and one line of support,
  `.ov-bd` scrolling body, `.ov-ft` footer with the primary action last on the right) and the same
  padding (`--ov-pad`, 24 px; 16 px on a phone). A modal never exceeds the screen height minus 64 px;
  its body scrolls. On a phone a modal becomes a bottom sheet and a drawer goes full width. `.scrim`
  dims the page under a modal, never under a drawer the person works beside.
- **The docked agent only docks when there is room.** `.app.with-agent` gives the drawer its own
  column at 1,440 px and wider; below that the same drawer becomes an overlay, so the page is never
  squeezed. When the entry is the launcher, it hides while any agent drawer is open (place `.agent-launch` after
  the drawer), and the page body gets bottom padding equal to the launcher's height plus its gap so it never sits on
  a card, row or button.
- **Spacing and density are tokens.** `--s-1…--s-12` (4–48 px) is the only spacing scale; page padding
  `--page-pad`, gaps between sections `--section-gap`, card padding `--card-pad`. `data-density=
  "compact|comfortable"` on `<html>` moves row height (36 / 44 / 52 px), cell padding and card padding
  together; nothing else changes.
- **Table helpers for dense data.** `.cl` (one line with ellipsis, width `--col-w`), `.cl2` (two lines),
  `.cell-chips` with `.more` ("+2"), `.tblwrap.freeze` (first column stays while the table scrolls),
  `.row-x .xp` (an expanded row that holds what does not fit a cell). `.dl` is a definition list with a
  label column of 120–160 px. `.cv` and `.cv-tag` frame a chart view and its code.
- **Chrome is a switch, not a rewrite.** `data-chrome="brand"` (the house gradient rail), `"ink"`
  (near-black chrome with the brand's signal colour as the active indicator — for black-led and
  achromatic brands), `"light"` (the rail on the solid rung, the brand only on the active indicator).
- **Surface is a switch.** `data-surface="glass"` (the house look), `"solid"` (opaque cards, no blur,
  a quieter aurora — for dense tools and clients whose own product is flat), `"paper"` (solid cards on
  the client's own page ground `--paper`, no aurora — for print-like, editorial or very calm brands).

**The device script:** `python3 -I "$D/scripts/base_css.py" device` prints it; paste it once, inline, at the end of `<body>`.

**Every colour in the kit is transformed with the core** in Step 3, and its ratios are measured in
Step 6 like everything else. The kit's literal blues follow the brand; the ink chrome's near-blacks are
near-neutral and barely move.

**Fonts as shipped:** Archivo 400/500/600 and IBM Plex Mono 400/500/600, both from Google Fonts and both openly licensed. **Archivo is the DEFAULT body face, not a fixed one — Step 2b decides whether it is replaced by the client's.** IBM Plex Mono stays. **If the mono is not
actually embedded, table headers fall back silently and the whole grid loses its register.**

⚠️ **Two token groups are declared as BARE triples** — `--aur-a` / `--aur-b` / `--aur-c`, consumed
as `rgba(var(--aur-a),a)`. **There is no `rgb(` to match, so a find-and-replace over hexes and
`rgba(...)` will skip them and leave the ambient field on the previous brand.** At 5% opacity that
does not look broken, it just casts the whole page in the wrong hue. Their hex equivalents are
`#0033A1` / `#0071CE` / `#CC27B0` in light and `#4C7FE8` / `#6BB3EA` / `#E884D6` in dark.

## Step 1 · Sample the brand

**The brand source order — highest first.** It decides every colour conflict; nothing else does.

1. **What the client supplied**: a swatch, the client's own deck or brand cues, a named brand system,
   the brand inputs and §21 hand-off of the scoping document when they come from client material.
2. **The client's published brand guidelines** or brand portal (colour pages, brand kit).
3. **The client's live product interface** — their own app or platform, when it is public.
4. **The client's live marketing site** — the CSS custom properties, the computed button and header
   colours.
5. **Third-party sources** (colour sites, logo libraries) — only ever as the confirming second source.

A source higher in the order wins even when a lower one is used more often. A retired source (a rebrand
dated after it) drops out of the order entirely. Record the order applied in the port note.

**Sample the identity, not only the hue.** A hue rotation alone produced four apps that looked the
same. Record each of these from the sources above; together they feed the expression (Step 2c):

- **Light-to-dark balance.** Is the brand light-led (white grounds, colour as accent), dark-led
  (black or near-black grounds, as on Pentland's deck) or colour-led (large fields of brand colour)?
- **The brand's chromatic role.** One hero colour, a pair, a gradient, or achromatic (black, white,
  grey) with a single accent? **An achromatic brand's "brand colour" is its black**, and its accent is
  the signal colour. Do not promote a link blue from the site into the brand.
- **The accent and where the client uses it** — buttons only, highlights, data, illustration.
- **The neutral ramp** — warm, cool or pure grey; the client's page background.
- **Shape and line** — square or rounded, hairlines or shadows, flat or layered, as their own product
  draws them (this chooses the Shape dial in Step 2c, `soft`, `square` or `round`; each shape's radius scale is
  fixed in the kit, and nothing between its steps is improvised).
- **Imagery** — product photography, people, illustration, data, none; and its treatment.
- **A motif** — a shape, line, angle or pattern in the logo or brand work that can become one quiet
  graphic element (a chevron, an oval, a stripe).
- **Type voice** — the display face and how loud headings are.

* **On the live site, read the CSS custom properties off `:root`** — not a screenshot. *On
  daikincomfort.com they are literally `--daikin_blue`, `--daikin_orange`, `--daikinGradient`.* Take
  the neutral ramp too. **From brand guidelines, take the digital (screen) palette**; a print primary
  (Pantone, CMYK) is not the screen colour the client means, as the next point shows. **The type stack is its own step — see Step 2b.**
* **🔴 A brand book's print primaries are not necessarily the hue the client means by "our colour".**
  Proofpoint's second attempt used H 196 — the hue of their own 5415 Blue — and was still wrong. The
  answer came as a swatch: *"Its more of sea green and bluish…"*, sampled as `#102F2D` off their live
  site. **When a swatch is available, sample it. Do not reason toward it.**
* **If the CSS cannot be fetched** (blocked, empty, or built by JavaScript), open the site in a browser
  (Claude in Chrome or the built-in browser) and read the values from the rendered page: the `:root`
  custom properties, and the computed colours of the primary button, links, header and nav. Do not
  fall back to a third-party colour site as the only source; use it as the second, confirming source
  in research question 1.
* **Inventory before transforming** — `base_css.py inventory` measures the core at **47 distinct hexes, 26
  `rgb()`/`rgba()` triples and 9 bare `--aur` triples**, and the kit at **12 hexes and 7 triples**. Count,
  transform, diff the count.

## Step 2 · Harvest the logo

**Acquisition, in order. Stop at the first that yields a real file:**

1. **Inline `<svg>` in the site header**, or a linked `.svg` (`/logo.svg`, `/assets/logo*.svg`) —
   always preferred; it scales and recolours cleanly.
2. `<link rel="apple-touch-icon">` — usually 180px, square, the mark alone.
3. `<meta property="og:image">` — usually the lockup, often with padding to crop.
4. `/favicon.svg` or `/favicon.ico`.
5. **The rendered page.** If a direct fetch is blocked, empty or JavaScript-rendered, open the site in
   a browser (Claude in Chrome or the built-in browser, whichever the session has) and take the logo
   from the rendered DOM: the header `<svg>` markup, or the `src` of the header `<img>`, then fetch
   that URL.
6. **The client's other official sources:** press, media or brand-kit page (`/press`, `/media`,
   `/brand`, `/newsroom`), the logo on the client's own docs or support site, and the client's
   app-store icon.
7. **Public logo libraries that hold the official file:** Wikimedia Commons (the file the client's
   Wikipedia article uses), Brandfetch, Simple Icons. Use the file as published; record its URL and
   check it matches the mark on the client's live site.
8. **Ask.** See stop 2 — never trace.

**Work through every step before stop 2.** "Could not be downloaded into this workspace" after one
blocked fetch is not a reason to stop. Record every URL tried and what each returned in the port note,
so a reviewer can see the search was complete.

**Then derive the kit. Seven variants, because a navbar and a favicon are not the same problem:**

| Variant | Where it goes | Min size | Ground |
| --- | --- | --- | --- |
| **Primary lockup** | Login, splash, cover slide, document header | 140px wide | Light page only |
| **Horizontal lockup** | Product header, email signature | 110px wide | Light page or tier-1 glass |
| **Stacked lockup** | Narrow columns, print, square crops | 96px wide | Light page only |
| **Mark only** | Collapsed rail, tab strip, compact header | 24px | Any |
| **Reversed mono** | **The nav rail** — the one branded surface | 24px | Brand gradient |
| **One-colour** | Watermark, single-ink print | 24px | Any |
| **App / favicon** | Tab, bookmark, PWA | 16 · 32 · 180 · 512 | Its own |

**Rules, and they are measured like anything else:**

* **Clear space is half the mark's height on all four sides.** Nothing crosses it, including the
  product name.
* **The mark is measured at ≥ 3:1 against its ground.** It is a graphical object, not text — 3:1 is
  the bar, and it still has to be met, in every variant and both themes.
* **Account and org logos are circles** (given on SailPoint: *"the logo used should be circular"*).
  Crop to a circle; never letterbox a rectangle inside one.
* **🔴 The rail is a gradient, so the logo on it is REVERSED MONO** — not the colour version with a
  white plate or glow behind it. A knocked-out mark on the brand gradient is the single most common
  place a prototype stops looking like the client owns it.
* **Never** recolour the mark outside the approved mono and reversed versions · place the
  full-colour logo on the brand fill · stretch, rotate, outline or shadow it · redraw it.
* **Record provenance** — which URL each file came from. Confirm anything uncertain by fetching it
  again or searching for it yourself; nothing ships with an unverified source.

## Step 2b · Type — research the real face, then decide what you may legally ship

**Two separate questions, and conflating them is the mistake.** *What typeface does the client
actually use?* is research. *May we put that file in our prototype?* is licensing, and the answer is
usually no.

### Identify it — in this order

⚠️ **Fetch the linked STYLESHEET, not the page.** A page fetch returns converted text with no
`@font-face` in it — tried on a live client site and it came back with zero font information while
the site plainly loads webfonts. Read the CSS file the page links to, or use the browser.

1. **`<link>` to `fonts.googleapis.com/css2?family=…`** — names the family outright, and tells you it
   is openly licensed. Best case; you are done.
2. **`@font-face` in the stylesheet** — `font-family` plus a `src: url(….woff2)`. The filename
   usually carries the family name.
3. **The loader domain names the foundry:** `use.typekit.net` / `p.typekit.net` → **Adobe Fonts** ·
   `fast.fonts.net` / `*.fontdeck` / Monotype paths → **Monotype** · `cloud.typography.com` →
   **Hoefler&Co**.
4. **Computed `font-family` on `body` and on a heading** — catches the case where the brand face is
   only used for display and the body is a system stack.
5. **Their brand or press page**, which often names the typeface in words.
6. **Ask.** Do not guess from a screenshot; a wrong guess propagates into every screen.

**Record what you found even when you cannot use it.** The style guide names the real face as what
production should license. That sentence is worth having in front of the client.

### 🔴 The licensing rule — identify the real face, ship an open one

**A webfont licence does not travel to us.** This is not caution, it is what the licences say:

* **Adobe Fonts cannot be self-hosted at all** and cannot be used by a third party — *"Adobe doesn't
  offer the ability to host fonts locally"*, and a client's site *"must load Adobe Fonts through
  their own Creative Cloud subscription"*. An agency cannot carry them into its own build.
* **Monotype webfonts are single-domain and metered** — a licence covers *"a single domain"*, runs on
  *"prepaid pageviews"*, and **agencies "may not share a single webfont license across multiple
  websites"**.
* **Google Fonts are open** (SIL OFL / Apache 2.0) — self-hosting, commercial use and redistribution
  are all permitted. This is why they are the fallback.

**So the rule, and it is not negotiable: never download and redistribute a client's licensed webfont
into our prototype.**

| What you found | What to ship |
| --- | --- |
| A Google Font | **Use it.** Link it or self-host it |
| Any other open face (OFL/Apache on GitHub or a foundry's free tier) | **Use it**, after checking the licence text itself |
| A licensed face — Adobe, Monotype, Hoefler, a bespoke foundry cut | **The closest open substitute**, with the real face named in the style guide |
| A display or script face used only in the logo | **Do not use it for UI at all.** It is a logo face; the body face is a separate question |
| Nothing identifiable | **Keep the system's own faces** and say so |

### Choosing the substitute — match the metrics, not the vibe

Two faces that "look similar" at 48px can wreck a 13px table. **Match, in this order:
x-height ratio · advance width · classification (grotesque / neo-grotesque / geometric / humanist) ·
stroke contrast · terminal style · whether it has tabular numerals**, which the system needs on
every number.

Starting points, **each to be verified by overlaying the two at the same size, never accepted from
this table alone**:

| Client's face | Open starting point |
| --- | --- |
| Helvetica / Helvetica Neue / Neue Haas Grotesk / Arial | **Inter** |
| Graphik, Founders Grotesk, Aktiv Grotesk | **Inter** or **Archivo** |
| Proxima Nova, Brandon, Sofia Pro | **Archivo** or **Figtree** |
| Gotham, Montserrat-adjacent geometrics | **Montserrat** |
| Avenir, Museo Sans, Nunito-adjacent humanists | **Nunito Sans** |
| Futura, Avant Garde | **Jost** |
| Circular, Poppins-adjacent geometrics | **Poppins** |
| DIN, Eurostile | **Barlow** or **Archivo Narrow** |
| Frutiger, Myriad, Univers | **Source Sans 3** |
| Tiempos, Georgia, a transitional serif | **Source Serif 4** |
| Garamond, an old-style serif | **EB Garamond** |

**When the closest match is a default face** (Inter, a system UI font), the body may keep it for tables and forms,
and the display face (`--font-display`, headings, the cover, big numbers) comes from the direction: a face with the
brand's character, checked against the brand's own headlines, never the same default. Record both in the fingerprint
with `fonts.reason`. `check_ds.py` flags a default face with no reason.

### ⚠️ A font swap invalidates the audit — re-measure

Changing the body face changes x-height and advance width, so it moves **apparent size, line length,
vertical rhythm and every fixed-width layout**. After the swap:

* **Re-run the contrast audit in both themes.** Contrast itself does not move, but perceived weight
  does — a lighter face at `--ink-3` can read thinner than the measured ratio suggests.
* **Re-measure fixed-width layouts.** A wider face is exactly what pushes a six-station rail back out
  of its container.
* **Check the numerals are tabular**, or every number in the system loses its alignment.
* **Check the four type sizes still hold their hierarchy** — a large x-height face makes 13px and
  15px look like the same size.

**🔴 Keep IBM Plex Mono regardless.** The mono is structural, not brand — it carries table headers,
eyebrows, KPI labels, timestamps and citation chips, and its 10.5px table header is a measured value.
Clients almost never have a brand mono, and swapping it changes the grid's register for no gain.
**Swap the body face; keep the mono.**

## Phase D · Creative direction — the idea, before anything is styled

**Run it after Step 2b, once the brand sample, the logo and the typeface are in hand, and before Step 2c.** The
direction decides the expression; doing it after the styling only produces a justification of what was already made.

**Why this exists.** People used to bring the idea in review rounds: "show the products", "this looks like the last
app", "make the runway feel like Pentland". The loop has no such rounds, so a creative director does that work here,
and judges the result again in Step 6b. Without it, runs converged: three of the apps in the register have a timeline
of text rows as their signature, and most share the same shell and surfaces.

**How to run it.** Start a separate agent when the session can (on the strongest model available) and give it
`$D/references/creative-director.md` as its brief, with the inputs listed in its Part 1: the scoping document's
sections it names, the manifest and the PNG frames, the brand sample, the register `$R` and
`$D/references/calibration.md`, **every one as an absolute path** (`echo "$D" "$R"`; the agent has its own shell). It does its own research (8 to 12 searches) and returns `direction.md`. When no separate
agent can be started, do Part 1 yourself as its own pass, following that file exactly, before going on.

**What comes back, and what you do with it:**
- **Three directions** from three different sources (the client's world, a standout product elsewhere, the users'
  own work), each with its wow moment, its signature re-imagined, its visual language and its risk; a scores table;
  the nearest past app for each.
- **The chosen direction**, the **thesis** (3 to 5 rules only this client fits), the **two showcase moments**, and
  the **parameters** as JSON. Step 2c applies the parameters; the cover, `#direction` and `#thesis` carry the words;
  the showcase draws the moments; the fingerprint records it all (Step 7).
- Run `python3 -I "$D/scripts/register.py" compare <client>-design-system.html "$R"` only after the fingerprint exists
  (Step 7; `check_ds.py --register "$R"` runs the same comparison). Here, the director has
  already checked the register; if it chose a direction that repeats a past app's idea, signature form or home layout,
  send it back once with the register line that matches.

**The direction includes an expressive layer.** Besides the idea and thesis it names the brand gradients, how depth
and hover feel, how selection shows, and one illustration style for empty states (references/creative-director.md).
A direction that is only black, white and one thin accent is not finished: the team judged that plain.

**The direction may change form, never the facts.** It decides the look and behaviour of components, the cover, the
showcase, the imagery and the motion. It never changes a page's layout or pattern (the wireframes'), the journey, the
data, the wording the scoping document gives, or the client's real colours and logo; it decides how those colours are
applied. Every measured rule in this file still holds: contrast floors, states, target sizes, both themes.

**The hero object leads.** When the manifest's `hero_object` has a picture, the chosen direction shows it wherever
people pick, check or approve one, at a size they can judge it by eye, on a neutral well (`.media-well`) so colour
stays honest in both themes. When the hero object has no picture, the director names what stands in for one (a
document page, a map position, a chart shape) and that leads instead.

**Pictures are HTML/CSS mockups.** The design system never fetches, downloads or embeds photos: no image search,
no client or retailer sites for pictures, no resizing, no data-URI photos. When the hero object has a picture
(`hero_object.picture`, or scoping 21.1), draw it as a mockup in HTML and CSS (inline SVG where a shape needs it) on
the neutral well (`.media-well`): the item's own silhouette or shape in the brand's style (a jacket, a boot, a can, a
document page, a site plan), its colourway as a swatch, its name and variant label, and the record's state. Mark every
such picture `data-media` (and `data-source="drawn"`). A seed record whose picture is missing in the app shows the
app's real fallback state on the same well, with one line ("Packshot due · DAM team"), never a hatched box. **The real
images belong to the app:** the build seeds them from the scoping document's §19 "Files and images" (client-supplied
files first, then the client's own public product pages); say in the hand-over which pictures the build must source.

## Step 2c · Choose the expression — so it looks like this client, and only this client

**Four runs, four clients, one look.** With the logo covered, Pentland, ClickUp, Vermont and Topcon
were the same product in a different hue: the same gradient rail, white bar, glass cards and aurora.
The core is right to stay fixed — its measurements are why the apps worked. What was missing is a
decision about **how this client's product should feel**, taken from evidence and recorded.

**The design concept is the chosen direction from Phase D.** Its big idea, thesis and parameters set what follows;
the paragraphs below say how a concept drives the system, and the dials record the parameters with their evidence.
Where the direction's parameters and a dial's default rule disagree, the direction wins unless it breaks a measured
rule (contrast, states, targets, both themes).

**The design concept — the one idea that makes this system belong to this client.** Find an object,
material or ritual from the client's own world and let it shape the system: Asian Paints' shade card
and paint chip; an airline's departure board and boarding pass; a fashion brand's lookbook and swatch
card; a lab's sample tray; a bank's statement. Choose it from what the scoping document, the client's
site and the research show the client's people actually handle every day, never from a generic
metaphor. Write it on the expression card in one line with its evidence, then let it drive:

- **the signature components (0.8)** — their form borrows from the concept (a dealer score shown as a
  paint chip whose shade fills to the score; a bag case header laid out like a boarding pass);
- **the variants** — each family's variants are designed from the concept, not taken from a house set;
- **the motif, empty states and imagery** — drawn from the concept, used quietly;
- **the chart voice** — how data is marked (chips, departure-board rows, swatches) where it reads
  better than a plain bar;
- **one signature interaction** — a single memorable moment tied to the concept (a score filling like
  paint; a status flipping like a departure-board tile; a card turning like a lookbook page), built
  within the motion rules, used once or twice in the app, never on every control.

**The concept changes form, never the core.** It can shape layout, composition, imagery and motion. It
never adds a colour value outside the transform, a radius outside the scale, a third elevation, a new
type size, or anything a UX law forbids. If the concept fights readability, the concept loses.

**Then set each dial from the concept, the identity sample (Step 1), the personas (0.4) and the
component references (research question 6) and the wireframes' references.** Every dial records its choice and the evidence that chose
it, in an **expression card** on the style guide.

| Dial | Options | Chosen by |
| --- | --- | --- |
| **Chrome** | `brand` gradient rail · `ink` near-black chrome · `light` rail on the solid rung | The brand's light-to-dark balance and chromatic role. Dark-led or achromatic → `ink`. Colour-led → `brand`. Light-led with a restrained accent → `light`. |
| **Shell** | left rail · top navigation (`data-shell="top"`) · rail plus docked agent (`.with-agent`) | Number of top-level destinations (≤ 5 and a wide content area → top navigation works), how the client's own product navigates, the persona's session length. |
| **Shape** | `soft` (house) · `square` · `round` (`data-shape` on `<html>`; kit.css holds the three measured scales) | The direction: the client's own product and print (sharp-cornered editorial, soft consumer, rounded friendly). Pick one; never mix. |
| **Surface** | `glass` · `solid` · `paper` | The client's own product (layered or flat), density (dense tools lean `solid`), the vibe line in §21. |
| **Default theme** | light · dark | Dark-led brands and dark-first personas (night shifts, control rooms) → dark; otherwise light. The product ships this default; the other theme stays one attribute away. |
| **Type voice** | display face = body face · a separate display face (`--font-display`) · display weight and size emphasis within the four-size scale | The client's display face (open or substituted, Step 2b) and how loud their headings are. |
| **Imagery** | product photography · people · illustration · data-led (no imagery) | What the client's own work shows and what the records have (styles with photos, shelves, people). Where records have images, every specimen shows them, with a real fallback. |
| **Motif** | none · one graphic element from the logo or brand work | Used once or twice, quietly: an empty-state illustration, the rail's top edge, a section divider, the AI marker. Never behind text, never a new colour. |
| **Chart voice** | bars and lines with gridlines · minimal with direct labels · dense small multiples | The personas (an executive reads big numbers and direct labels; an analyst reads grids) and the references. |
| **Signal** | the transformed accent (default) · the brand's literal accent as `--signal` | When the brand's own accent cannot be a fill under white text (neon lime, yellow, light cyan), keep it literal as `--signal` for indicators, focus glow on dark chrome, a key data series, selection marks — measured per use, never as body text on light. |

**Rules for the dials:**

- **The house default is a choice, not a fallback.** Picking `brand` chrome + left rail + `glass` +
  light needs evidence from the brand, the same as any other combination.
- **The logo-off test.** Cover the logo on the main screen and ask whether a person who knows the
  client would recognise it as theirs. If not, revisit chrome, surface, imagery and motif before going
  on. Record the answer in the expression card.
- **No app repeats a past app.** The director checked the register in Phase D; `register.py compare` checks the
  fingerprint again in Step 7. A run that matches a past app on its idea, signature form or home layout, or on more
  than 3 of the 8 visual lines, goes back to Phase D.
- **What the dials never move:** the steps within the chosen radius scale, the no-borders-on-cards rule, the two elevation
  levels, the four type sizes and two weights, spacing, component anatomy, every state, the status
  palette, the contrast floors. Variation lives in composition and colour application, never in
  breaking the measured core.

### Variants and the style set — options for the reviewer, one answer for the builder

Reviewers want choices ("show me another chart header"), and the builder needs one unambiguous answer.
Too many loose variants and the builder mixes them or picks the weakest. So variants are **coded,
capped and bundled**:

1. **Which components carry variants.** Every hero, interactive and signature component carries 2 or 3 (0.6); a
   static atom with nothing in `does` (a divider, a count dot) keeps one form. The shared families use their codes
   from the composition model (`$D/references/reference.md`, Layer 1): page header `PH`, record header `RH`, KPI tile
   `KPI`, chart frame and header `CH`, table row style `TB`, card `CD`, filter bar `FB`, empty state `ES`, list item
   `LI`, right-rail panel `RP`, agent drawer `AG`, and the signature components from 0.8 (`SG1`, `SG2`, …). Any other
   component takes a short code of its own (`QT` for a queue table). `check_ds.py` counts the distinct codes; the
   floor is 25.
2. **Two or three variants per family or component, never more**, coded `<code>-<n>` (`KPI-1`, `KPI-2`, `CH-3`). Each must
   differ in a way a reviewer can see in one second (number above label vs label above number; header
   with inline legend vs legend below), and each passes every rule in this file. No variant is a
   weaker copy kept for contrast.
3. **One style set by default: `S1`.** A style set names exactly **one** variant per family and per component that
   carries variants — never two. S1 is the set every drawn screen uses, and the only set the builder uses. The other variants
   still appear, labelled, on the component pages, so the reviewer can see the choices without whole
   screens being redrawn. **Draw `S2` (and at most `S3`) only when the user asks for options**, and
   then on **one** hero screen each, side by side.
4. **Every specimen is tagged.** Each component instance carries `data-variant="KPI-1"` (and the screen
   carries `data-style-set="S1"`), and the style guide prints the code beside each variant in the
   component section.
5. **Machine-readable for the builder.** The file carries one JSON block, which the composition contract
   quotes:

```html
<script type="application/json" id="style-sets">
{"active":"S1",
 "sets":{"S1":{"PH":"PH-1","RH":"RH-1","KPI":"KPI-1","CH":"CH-1","TB":"TB-1","CD":"CD-1","FB":"FB-1","ES":"ES-1"}},
 "variants":{"KPI-1":"number over label, delta below, no icon","KPI-2":"label over number, sparkline right"}}
</script>
```

   **The rule for the builder: use only the active set's variant for each family, everywhere, and never
   mix sets.** If the user asks for options and then picks S2, S2 is added to `"sets"` and only
   `"active"` changes.
6. **Variants are designed for this client.** Each family's variants come from the design concept,
   the brand and the references, so two clients' KPI tiles can look nothing alike. Each variant names
   its source (the concept, a component reference from research question 6, or brand evidence) in the `variants`
   text, and the **recommended** one (active in S1) says in one line why it fits this client best.

### Chart views — more than one way to see the same data

For every chart the document needs, start from the **question the chart answers** ("which stores
fail most?", "is the pass rate improving?") and draw **chart views**: the recommended view plus one or
two alternatives that answer the same question differently, each coded `CV-<chart>-<a|b|c>` and framed
in `.cv` with its code (`.cv-tag`).

- **Same frame, same data, same units, same status palette** across the views of one chart; only the
  encoding changes (bars ↔ dot plot ↔ line; stacked ↔ small multiples; donut never for more than three
  parts).
- **Mark one view Recommended** and say why in one line. The recommended view goes into the active
  style set's screens; the alternatives appear beside it in the chart section only.
- **Where the persona benefits, the view switch ships in the app**: a `.seg` in the chart header
  (Chart / Table at minimum, for accessibility and export), drawn in its states.
- **Every chart has a table view** available, even if it is not the recommended view.

**Black-led and achromatic brands** (Pentland: black grounds, white type, a neon yellow-green accent):
chrome `ink`, default theme usually dark, surface `solid` or `glass` over a near-black ground, the
accent kept literal as `--signal` for the active nav indicator, focus, selection and the one hero data
series. The primary button becomes a light fill with dark text, or the signal fill with dark text,
whichever measures ≥ 4.5:1 — never the signal under white. **An achromatic brand is never rotated
onto a hue taken from its website's link colour.**

**Brands whose hue is close to the house blue** (Topcon, H 208°): the transform barely moves anything,
so the expression has to carry the identity — chrome, surface, imagery, motif and type voice do the
work the hue cannot.

## Step 3 · Transform, preserving LUMINANCE

**The whole value of porting a validated system is that its measurements survive. They survive only
if you hold the right quantity fixed, and it is not the one in the colour picker.**

Contrast is a function of relative luminance alone. **HSL lightness is not luminance** — green at
L .40 is far brighter than blue at L .40. Measured on the Proofpoint port: holding HSL-L fixed while
rotating 207° → 176° took the primary from **4.54:1 to 3.12:1**, silently, on a token the document
prints a number for.

```python
import colorsys
def _lin(c): c/=255; return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def Y(rgb): r,g,b=rgb; return .2126*_lin(r)+.7152*_lin(g)+.0722*_lin(b)
def hsl_rgb(h,s,l): return tuple(round(v*255) for v in colorsys.hls_to_rgb(h,l,s))

def reskin(rgb, hue, sat):
    """Saturation is CHOSEN (that is the muting). Lightness is SEARCHED. hue/sat/l in 0..1."""
    target, lo, hi = Y(rgb), 0.0, 1.0
    for _ in range(60):
        mid = (lo+hi)/2
        if Y(hsl_rgb(hue, sat, mid)) < target: lo = mid
        else: hi = mid
    return hsl_rgb(hue, sat, (lo+hi)/2)
```

⚠️ **Do not add a "drop saturation if Y is unreachable" fallback.** In HLS, lightness 1.0 is white at
every saturation, so every `Y` in [0,1] is always reachable; that branch can only fire spuriously,
on a tolerance tighter than integer-RGB rounding, and when it fires it flattens a colour to grey
while keeping its hue. `#86CDB4` came back `#BFBFBF`. **Saturation is chosen; lightness is searched.**

**Apply it with the script.** Write a map with each family's new hue, saturation scale and cap, and pin
the sampled swatch under `"fixed"`:
`{"blue": {"hue": 176, "sat": 0.70, "cap": 0.62}, "cerise": {"hue": 152, "sat": 0.62, "cap": 0.44},
"fixed": {"#0033A1": "<the sampled swatch>"}}`, then run `python3 -I "$D/scripts/base_css.py" build map.json base.css`.
It moves every hex, `rgb()` triple and bare `--aur` triple (the ones a find-and-replace misses) and prints
each change. The function above is what it runs.

**Assign colour by job and keep the jobs separate:** brand/chrome · status · categorical ·
sequential.

* **The brand colour has exactly three uses** — the one primary action, the active nav item, the
  selected state. Not headings, icons, counts, or links in tables. Everything else greyscale.
* **Reserve the warm end for risk states** so a categorical colour never reads as an alarm. ⚠️ **If
  the brand itself is warm, Step 4 inverts this.**
* **Muting is a saturation cut, never a lightness cut** — a lightness cut moves the quantity you are
  holding. Worked example: blues → H176 at S × 0.70 (cap .62); the cerise family → H152 at S × 0.62
  (cap .44) for the gradient tail; positive → H138 against a green brand; amber → H28; red → H6;
  anything under S .06 left alone.
* **Four statuses, tonal only** — 8–10% tint, text at the 700 step, never a saturated fill.
  **Status always ships as icon + word + colour.**
* **Charts: one hue at several lightness steps.** Fixed hue order, never cycled.
* **🔴 Brand-as-accent and brand-as-fill are two different values.** White on the Proofpoint fill
  measured 4.15 against a claimed 4.94 — **the fill gradient runs one step darker than the accent
  token**, and it governs the primary button, user chat bubble, toggles, checked boxes, the current
  stepper node and the bulk-bar counter. **Check every gradient stop, not just the mid one.** In
  dark, brand-as-text lightens while brand-as-fill does not.

## Step 4 · The warm-brand checks (skip if the brand is cool)

Three things appear on a red or orange brand and on no cool one:

* **Negative status collides with the brand and no contrast figure will warn you.** A red brand and
  a red error measure 1.54 contrast — but contrast is a *lightness* metric and says nothing about
  categorical separation. **Measure ΔE.** At H 350 negative sits 26 ΔE from the brand against 90 ΔE
  in the blue original; **H 344 recovers 32 ΔE** and is about the ceiling before the error reads as a
  brand tint. Icon + word + colour becomes load-bearing rather than belt-and-braces.
* **The chart ramp must leave the brand hue entirely.** A six-step red ramp reads as six alarm
  levels. Send it cool — still one hue at several lightness steps, and it can never read as risk.
* **The accent needs more headroom.** A straight port put Titan's accent at 4.48 on the page, a fail
  where the blue measured 4.54.

## Step 5 · Both themes, and both reachable

**Light and dark are both deliverables. The mode you built in is not the only one that gets
checked.**

* **v3.3 shipped both themes and zero `<script>`**, so it silently followed the reader's OS and the
  reviewer only ever saw dark: *"do we not have light mode."* Two themes measured and argued over
  across a whole section, one of them invisible. **Shipping both is not enough — both must be
  *reachable*.**
* **A theme built by inversion fails on contact.** Light-mode brand hexes in a dark ambient field
  paint shadow instead of light; that is what blotched the first SailPoint dark mode.

**The style guide ships a theme switch** — built from `.seg` (D0), defaulting to the OS, remembered
in `localStorage`. **A screen built from the design system does not**, because a theme toggle in
product chrome is our scaffolding shipped to the client. On a product build, ship the **default theme chosen in
Step 2c, set explicitly as `data-theme` on `<html>`** — a product never follows the reader's OS (the
Topcon app opened dark on a dark-mode laptop while the design was light-first) — and **keep the other
theme's tokens live in the stylesheet**, so the second theme is one attribute away rather than a
rebuild. Users switch theme from the profile menu.

**Dark specifics — rebuilt in v5.** The v4 dark sat on a mid slate (`#192030`) under blue-grey glass at
12–23% and aurora at 19–26%. It read dull and muddy, and measured worse than it looked: composited on
its own tier-3 glass, `--ink-3` fell to 3.06:1 and the status tags to 2.98–3.43:1, which is why every
run lifted tokens by hand. The v5 dark, now in the stylesheet:

| Token | v4 | v5 | Why |
| --- | --- | --- | --- |
| `--base` | `#192030` | `#0B1018` | A deep, faintly brand-tinted ground: depth comes from a dark page, not from grey washes |
| `--glass-1/2/3` | `rgba(120,165,225,.12/.17/.23)` | `rgba(150,180,230,.05/.07/.095)` | Glass in dark is a whisper of light; heavy alpha is what turned it to slate |
| `--glass-solid` | `#2F3D57` | `#151B26` | The opaque rung sits one clear step above the page |
| `--inner` · `--edge` · `--hair` | `.085` · `.17` · `.10/.17` | `.06` · `.10` · `.08/.14` | Quieter separations on a darker ground |
| `--ink` / `-2` / `-3` / `-mute` | `#D8E0EC` `#AAB7CB` `#9FADC3` `#78869F` | `#E7ECF3` `#B6C0CF` `#9AA6B8` `#6F7B90` | Worst composited case now 9.61 / 6.21 / 4.63 (mute is disabled text, exempt) |
| `--sp-blue` (brand as text) | `#6BB3EA` | `#7DBDF0` | 5.65:1 at its worst ground, up from 3.06 |
| Status text | `#AAB7CB` `#E3B45C` `#EC9790` `#86CDB4` | `#B6C0CF` `#E8BC69` `#F2A49D` `#8FD3BA` | Every status tag ≥ 5.0:1 on its tint over the opaque rung (was 2.98–3.43) |
| `--aur-1/2/3` | `.26/.19/.22` | `.18/.12/.14` | The aurora becomes a glow at the edges, not a wash over everything |
| `--vig` | to `rgba(6,11,22,.30)` | to `rgba(2,5,11,.42)` | Corners fall away, which is what makes the glow read |
| `.tile` highlight | white at 28% | white at 4.5% (dark only) | The 28% highlight painted every tile grey |

**Rules for dark, whatever the brand:**

- **Depth is lightness steps, not washes**: page < glass tiers < opaque rung < inner wells < raised
  overlays, each a small, even step lighter.
- **The brand glows; it does not tint everything.** Allowed: the aurora at the page edges, a soft
  brand glow behind the hero area or the agent launcher, the focus ring, the active nav indicator, a
  brand gradient on the primary fill. Not allowed: brand colour behind body text, saturated panels.
- **No fluorescent text.** Brand-as-text in dark is a pastel step of the brand (HSL lightness ≥ 0.70,
  measured); a neon or saturated accent is used for marks, indicators and fills with dark text, never
  for words on dark.
- **Edges catch light upward in dark and downward in light.** One hue carries two categorical steps
  in dark, three in light.
- **A container that HOLDS other glass takes the opaque rung**, or nested glass composites two rungs
  above its intended one and drags every ink token after it.
- **After the transform, re-measure the dark set on the brand's own hue.** A warm or green brand moves
  luminance differently from blue; the v5 numbers are the floor the port must still meet.
- **Look at references first** (the component references of research question 6): well-regarded dark products use near-black
  grounds, low-alpha surfaces, a single accent and generous spacing. Take that discipline, not their
  colours.

**Light specifics — it is not dark with the tokens flipped:** near-white brand tint base · **aurora
alphas roughly halved** · tier 1 `rgba(255,255,255,.72)`, tier 2 `.82`, tier 3 brand at 5% · inset
highlight `rgba(255,255,255,.9)` · shadows to the brand's darkest tone at 8–12% · **the accent glow
drops, replaced by a soft focus ring**.
⚠️ **A tinted light background changes the surface a chart was validated against** — Daikin's palette
passes on `#F4F8FC` and a third slot drops below 3:1 by `#EEF4FA`. Cap the tint and re-run the
validator. **Re-measure fixed-width layouts after restyling** — larger radii and padding are what
push a six-station rail back out of its container.

## Step 6 · Audit, composited, both themes

**Walk every text role with alpha composited over its real parent chain, in light and in dark.** The
reference run on v3.4 covered 35 new roles and ended with 3 under AA in each theme, all three
deliberately dimmed states.

**Mechanical checks, all pass/fail:**

* **Rendered and screenshotted in light AND dark.** A theme nobody has looked at is broken.
* `grep -o 'stroke[A-Z]'` → **nothing.** 79 camelCase SVG attributes once shipped in our own design
  language with every icon at browser-default stroke. **JSX takes camelCase; plain HTML takes
  kebab-case — same defect, opposite fix, both silent.**
* `grep -E '\-\-[a-z-]+: ?[0-9]+,[0-9]+,[0-9]+'` → every **bare rgb triple** accounted for. v3.4
  declares its ambient field as `--aur-a:0,51,161`, consumed as `rgba(var(--aur-a),a)`. **There is no
  `rgb(` to match, so a hex-and-rgba replace leaves the ambient field on the previous client's
  brand** — at 5% opacity it does not look broken, it just casts the page in the wrong hue.
* Card `border-width` computes 0 · gradient cards carry no inset ring · `backdrop-filter` computes
  `blur(...) saturate(...)`, not `none` · 1px top edge on every glass surface.
* Radii only from the chosen shape's scale (`data-shape` on `<html>`, set in `$D/assets/kit.css`), never two shapes
  on one page: **soft** (the house default) 10 / 6 / pill / circle, **square** 3 / 2 / pill / circle, **round**
  16 / 10 / pill / circle. Studio surfaces (tile / sheet / canvas / shell) take soft 12 / 16 / 22 / 28, square
  4 / 6 / 6 / 8, round 20 / 24 / 28 / 32.
* Table header IBM Plex Mono 10.5px **and the face actually embedded** — if it silently falls back
  the whole grid loses its register.
* **If the body face was swapped (Step 2b): numerals are tabular, the four type sizes still hold
  their hierarchy, and no fixed-width layout has overflowed.**
* Tag font-size < button font-size · status tags ≥ 4.5 composited, both themes · **logo mark ≥ 3:1
  on its ground, every variant**.
* One `<style>`, one `</style>` · no horizontal page scroll · zero JS errors · **one output file**.
* **Theme switch correct under both OS schemes and across a reload.**
* **Narrow a filter until it returns nothing** and look at which empty state appears.
* **Shell, at the deepest scroll:** the rail's bottom equals the viewport's bottom, the top bar's
  computed background is opaque, no content is visible through or under it, and wide tables scroll
  inside their own container (no column clipped, no page-level horizontal scroll).
* **Every agent drawer opens, closes with Esc, returns focus to its launcher**, and is drawn over a
  real screen; no agent appears as a card or block in a page layout.
* **Images:** every record that has an image shows it; every missing image shows the designed
  fallback, never a broken-image icon or an empty card.
* **Status in charts** uses the status palette and a legend with words, never brand-colour steps.
* **Phone and tablet layouts that are drawn** (0.4: only a persona's primary device) render at their
  widths with their own navigation.

**Four traps, each of which produced a false result on a real run:**

1. **Gradient grounds read as transparent.** A walker reading `backgroundColor` finds nothing on a
   `linear-gradient` surface and falls through to the page — it reported **1.03:1** on rail text that
   measures **12.12:1**. Put an explicit `background-color` under every gradient: honest measurement
   plus a real fallback ground.
2. **Alpha ignored.** Composite the tint over its actual parent or every tonal status tag reports
   ~1.2 and you "fix" what was never broken. **Measuring the wrong thing is its own failure mode.**
3. **🔴 Inject CSS before the LAST `</style>`, not the first.** The first may be the host page's own
   skeleton — the rules land outside the stylesheet, are stripped on export, and every component
   renders with browser defaults while the file looks complete and the elements are all present in
   the DOM. **This is written down and it still happened while building v3.4.** Verify a *computed
   value* on a new component — not the source text, not the presence of the element.
4. **A handler audit false-clears if `[data-theme]` is on `<html>`** — `el.closest('[data-theme]')`
   then matches every element. Exclude `document.documentElement`. Same trap in Playwright:
   `page.click('[data-theme]')` clicks `<html>` and your dark screenshot comes back light — select
   `button[data-theme]`.

### Rendering safety — what broke in real output files, and the rule for each

Every one of these produced a file that looked finished in its source and rendered wrong.

| What broke | Rule |
| --- | --- |
| **Words looked run together** (Vermont, "Retakeneeded") | **Fonts are embedded as base64 WOFF2 taken unchanged from Google Fonts' own files** for the subsets the page needs (latin, latin-ext, plus any script the personas read). Never re-subset, rebuild or convert a font. Some faces simply have narrow spaces — Plus Jakarta Sans measures 0.17 em in its official file, Archivo 0.21, Inter 0.28 — so judge the space against the official file, not an absolute floor. For a face with a space under 0.2 em: no negative letter-spacing below 15 px, and `word-spacing:.04em` on text under 14 px. |
| **Fonts silently fell back** when a run's sandbox could not reach Google Fonts, so its own screenshots showed Arial and the audit measured the wrong face | Embedding (above) makes the file truly self-contained. A `<link>` to Google Fonts is allowed only as a backup *in addition* to the embedded faces. `document.fonts` must report every family loaded before screenshots are taken. |
| **Unstyled studio parts** — the v4 stylesheet had no light-theme base rule for `.sheet2`, `.kpis2`, `.kpi2` or the studio composer `.cmp` | Fixed in v5's stylesheet. Any class the page uses must have a base rule; the render check lists classes with no matching rule. |
| **Broken images and empty image tiles** (Pentland's AI views, its material swatches) | Every image is embedded (SVG inline, raster as a data URI of 200 KB or less) — never hot-linked, since client sites block hot-linking and the file must open offline. Every image box has a size or `aspect-ratio`, `alt` text and a designed fallback. Keep the file under 15 MB. |
| **One open drawer covered the whole guide; a 100vh rail ran past its screen** | Screen specimens go in `.frame > .frame-scroll` (the kit). |
| **A phone drawn in a narrow box showed the desktop layout** | Phone and tablet specimens go in `<template class="device">` and render as iframes (the device script). |
| **The launcher sat on the phone's tab bar** | Fixed in the kit: on a phone the launcher sits above `.app-tabs`. |
| **Tags broke onto two lines in narrow tables** ("Off / track") | Fixed in the core: tags, facet chips and slots do not wrap. |
| **Clipped inputs and spilling cards** (ClickUp's search placeholder cut off, a Topcon hover card 149 px outside its column) | Placeholders fit their field at the narrowest width shown. State specimens (hover, lifted, open) sit in a cell sized for that state. The render check flags spills and clips. |
| **A transparent rail in some browsers** (`color-mix()`) | No `color-mix()`, CSS nesting or container queries in the system CSS; layout must not depend on `:has()`. |
| **Icons at browser-default stroke** (camelCase SVG attributes in HTML) | The `stroke[A-Z]` grep above, before every hand-over. |
| **The guide's left navigation showed half-height, overlapping labels** (Fujairah: a fixed-height flex column, links with `overflow:hidden`, so the browser shrank each link to 15 px; worse on shorter screens) | Every child of a flex column that must keep its height gets `flex-shrink:0`; a long navigation scrolls inside itself (`overflow-y:auto`), it never squeezes its items. The render check's `vclipped` count catches it. |
| **State matrices squeezed wide components** (Fujairah: a 360 px pilot card forced into 190 px state columns — eyebrows one word per line, the last card cut at the edge) | A state cell is never narrower than the component's real width. Narrow atoms (buttons, chips, toggles) use the table matrix; a component wider than about 240 px shows its states as a wrapping grid, each tile at the component's real width (`grid-template-columns:repeat(auto-fill,minmax(<real width>,1fr))`). |
| **Wide diagrams looked cut off** (Fujairah's swimlanes ran 1,814 px in an 1,116 px column with no sign they scroll) | A diagram wider than its column either wraps (lanes stack, steps flow to a second row) or scrolls inside a frame with its first column (lane names) sticky and a visible edge fade and "Scroll →" hint. Nothing ends mid-card at the edge. |

**The render check — run it in the browser on the finished file, in light and in dark, at 1,280 px and
375 px, and paste the result into the hand-over.** It also walks every device iframe. Every count must be
zero and every face loaded; `where` names the first offenders. `overlaps` finds siblings that collide
(pills on top of each other, task names running into the next card); `squeezed` finds text wrapping at
one or two words per line (a column or card too narrow for its content); `vclipped` finds text cut off
vertically inside a box that hides overflow (a link or row shrunk below its line height). **Run it at
three viewports: 1,280 × 800, 1,280 × 680 (a short laptop screen, where squeezing shows first) and
375 × 812.**

```js
(() => {
  const res = { hScroll: 0, spills: 0, clipped: 0, vclipped: 0, overlaps: 0, squeezed: 0, brokenImages: 0, fonts: {}, unstyledClasses: [], where: [] };
  const note = (k, el, doc, win = window) => { res[k]++; if (res.where.length < 15) res.where.push(k + ': ' + (win.frameElement ? (win.frameElement.title || 'device') : 'page') + ' › ' + el.tagName.toLowerCase() + '.' + [...el.classList].join('.') + ' "' + (el.textContent || '').trim().slice(0, 40) + '"'); };
  const scan = (doc, win) => {
    const de = doc.documentElement; res.hScroll = Math.max(res.hScroll, de.scrollWidth - de.clientWidth);
    const texts = [];
    const layer = el => { for (let n = el; n && n !== doc.body; n = n.parentElement) { const p = win.getComputedStyle(n).position; if (p === 'fixed' || p === 'absolute' || p === 'sticky') return n; } return doc.body; };
    for (const el of doc.querySelectorAll('body *')) {
      const cs = win.getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
      if (['hidden', 'clip'].includes(cs.overflowX) && el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 40 && cs.textOverflow !== 'ellipsis' && !el.closest('.tblwrap')) note('clipped', el, doc, win);
      if (['hidden', 'clip'].includes(cs.overflowY) && el.clientHeight > 0 && el.scrollHeight > el.clientHeight + 2 && cs.webkitLineClamp === 'none' && !el.closest('.frame, .frame-scroll') && [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim())) note('vclipped', el, doc, win);
      const p = el.parentElement;
      if (p && cs.position !== 'fixed' && cs.position !== 'absolute' && win.getComputedStyle(p).overflowX === 'visible' && r.right > p.getBoundingClientRect().right + 4) note('spills', el, doc, win);
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim());
      if (own) {
        if (cs.display !== 'inline' && cs.display !== 'contents') texts.push([el, r, layer(el)]);
        const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.3, lines = Math.round(r.height / lh), words = el.textContent.trim().split(/\s+/).length;
        if (lines >= 3 && words / lines <= 1.6 && words >= 3) note('squeezed', el, doc, win);
      }
    }
    for (const parent of doc.querySelectorAll('body *')) {
      if (parent.matches('.faces')) continue;
      const kids = [...parent.children].filter(k => { const cs = win.getComputedStyle(k); return cs.display !== 'none' && cs.visibility !== 'hidden' && cs.position !== 'absolute' && cs.position !== 'fixed' && k.textContent.trim(); });
      for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) {
        const ra = kids[i].getBoundingClientRect(), rb = kids[j].getBoundingClientRect();
        const ix = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), iy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
        if (ra.width && rb.width && ix > 3 && iy > 3) note('overlaps', kids[j], doc, win);
      }
    }
    res.brokenImages += [...doc.images].filter(i => i.complete && !i.naturalWidth).length;
    const c = doc.createElement('canvas').getContext('2d');
    doc.fonts.forEach(f => { const fam = f.family.replace(/["']/g, ''); c.font = `16px "${fam}"`; res.fonts[fam] = { status: f.status, spaceEm: +((c.measureText('a b').width - c.measureText('ab').width) / 16).toFixed(2) }; });
    const css = [...doc.styleSheets].flatMap(s => { try { return [...s.cssRules].map(r => r.cssText) } catch (e) { return [] } }).join(' ');
    [...new Set([...doc.querySelectorAll('[class]')].flatMap(e => [...e.classList]))].filter(k => !css.includes('.' + k) && !res.unstyledClasses.includes(k)).forEach(k => res.unstyledClasses.push(k));
  };
  scan(document, window);
  for (const f of document.querySelectorAll('iframe')) { try { if (f.contentDocument) scan(f.contentDocument, f.contentWindow); } catch (e) {} }
  console.table(res); return res;
})()
```

**Every count is a defect in screens, specimens, state matrices, component pages and the guide's own
navigation.** The only allowed exception is a short label in the first column of a documentation table
wrapping onto two lines (for example "Hover a waypoint"); check each one by eye and list it in the
hand-over. Anything else flagged is fixed before hand-over. `unstyledClasses` should list only hooks used
by a script, never a visual component. The v5 runs measured 69–381 squeezed elements and up to 54
clipped ones per file; the reference test page measures zero on every count.

## Step 6b · The creative director's judgement — fresh eyes, at most two rounds

**After Step 6's audit is clean, before Step 7.** The audit proves the page is correct; this step decides whether it
is good, whether it is this client's, and whether it is unlike every app we made before.

1. **Scan and shoot.**
   ```bash
   source ~/.local/poc-collateral/env.sh 2>/dev/null; D="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/design-system 2>/dev/null | sort -V | tail -1)"; [ -n "$D" ] || D="$(dirname "$(find ~/.claude/plugins -path '*design-system/scripts/check_ds.py' 2>/dev/null | head -1)")/.."; [ -f "$D/scripts/check_ds.py" ] || echo "check: design-system skill folder not found"
   R="$HOME/.local/poc-studio/design-register.json"; [ -f "$R" ] || { mkdir -p "$(dirname "$R")" && cp "$D/register/register.json" "$R"; }
   python3 -I "$D/scripts/scan.py" <client>-design-system.html <work>/scan
   ```
   If `python3 -I -c "import playwright"` fails, install it first (on a Mac: run the `poc-collateral-setup` install,
   which puts it in the shared tools that the `source …/env.sh` line above loads; elsewhere `python3 -m pip install
   playwright`)
   and reuse the Chromium already present: never download a second browser when `PLAYWRIGHT_BROWSERS_PATH` or a
   Playwright Chromium exists (`scan.py` finds an installed Chromium by itself). The scan measures the page height
   (budget 70,000 px), finds overlapping and clipped text, contrast failures, small targets and repeated rows in light and dark,
   and saves the screenshots the director judges. Fix every `check:` line it prints before the judgement; a defect
   the script can find is not worth the director's time.
2. **Judge.** Give the separate agent (or, without one, your own separate pass) `$D/references/creative-director.md`
   Part 2 with only its inputs, as absolute paths: the screenshots, the scan's findings, `direction.md`,
   `$D/references/calibration.md`, the register `$R`, and the §11 "What the person must see to decide" lines for the three screens. Not your notes and not
   the HTML. It returns seven scores (distinctiveness, wow, richness, accuracy, UX, craft, journey) and up to eight ranked
   changes, each a push or a fix.
3. **Apply every change**, re-run `scan.py`, and send only the changed screenshots for round 2. A change you
   disagree with is still made unless it breaks a measured rule in this file; then say which rule in the review.
4. **Record the review on the page** in the Build section: `<section id="review" data-distinctiveness="4" data-wow="5" data-richness="4"
   data-accuracy="4" data-ux="4" data-craft="4" data-journey="5" data-rounds="2">` with the scores of each round, the
   changes made and any change not made with its reason. `check_ds.py` reads it.

**The pass bar is 4 or more on every score.** After round 2 the file ships with its honest scores, whatever they are,
and the lowest is named as the weakest part in the hand-over. There is no third round: the AI PM and the feedback
rounds take it from there. In POC Studio the AI PM rescores from its own screenshots; a score more than one point
above its score is a finding.

## Step 7 · Ship

**The output is one file: a single self-contained HTML file, and nothing else.** Not a published
artifact, not a separate token file, not a logo folder, not JSON or Markdown alongside it. Save it as
`<client>-design-system.html` in the outputs folder and hand over that path (a caller may give another name and
folder; then use those). Everything the deliverables
below describe lives inside that one file as sections of the page — the token block as a copyable code
block, the logo kit as inline SVG (raster variants as data URIs) with a copy button per variant, the
composition contract as a quotable block. If something cannot live inside the file, it is not delivered.

**The file is a design system, not a drawn copy of the app.** It documents every component in full,
shows the foundations, maps every journey step to its components, draws three screens, and hands over
the rules for the rest (0.6).

**Six deliverables, all inside the one file:**

1. **Living style guide** — the page itself, built like a real design-system site: self-contained,
   light and dark with a working switch, a **sticky left navigation** of its sections (full viewport
   height, scrolling inside itself when long; every item `flex-shrink:0`, one line, never squeezed), the client's
   expression applied to the guide itself (chrome, motif, type voice) so it reads as this client's
   system. **Its sections, in the order 0.6 gives:** cover, direction and thesis, showcase, views and
   navigation, foundations with the expressive layer, flows at component level (one panel per capability, with its
   three principle cards), components (signature and key components at full depth), journey, build. In more detail:
   - **Cover, direction, thesis and showcase** — as 0.6 describes; the expression card sits with the
     direction. The component list with each component's source (manifest, baseline or **Added by the design
     system** with its reason) and the build brief go to the Build section.
   - **Foundations** — colour (every token with its measured ratio), type scale, spacing and density,
     **material and elevation** (glass tiers layered over the ambient field, the solid rung, edge light,
     shadows, in both themes), motion (durations, easing, what moves and why), icons.
   - **Components** — one component page per component (0.6; the signature and up to five key components at full depth), grouped
     as the inventory groups them; signature components first, then the agent drawer, overlays,
     navigation, inputs, data display, feedback and states. Every component **rendered, not
     described**, with its live specimen and its state grid.
   - **Patterns** — chart views; a blueprint only for a pattern no frame shows (without wireframes, one per chosen pattern).
   - **Journey** — the journey-to-component table (0.7). The three screens are in the showcase, each labelled
     with its frame, persona and the storyline steps it shows.
   - **Build** — the page inventory, the composition contract, the token block, the logo kit, the port note
     and ledger, the review (Step 6b), the hand-over. Style sets S2/S3 only if the user asked for options.
2. **Token block** — one `:root`, tokens named by **job** never by colour, **a measured ratio printed
   beside each**, non-text ones marked. A token carrying a number nobody re-measured after a hue
   rotation is a defect.
3. **Logo kit** — the seven variants with the usage matrix, clear space, minimum sizes, misuse list
   and provenance. With `ink` or `light` chrome, the rail takes the variant that measures on it.
4. **Composition contract** — a block written for the builder (UnifyApps Headless), quoted verbatim in the build
   prompt. The builder reads this, not the skill, so every rule it must follow is here:
   - **Look up, don't choose.** Every design decision is already made in `#build-plan` and
     `#style-sets`. For each page: find its route in `build-plan.pages` and use that pattern and those
     region fillers. For a page not listed, take its data shape and persona and use the **first
     matching rule** in `build-plan.rules`. Use the `app` settings (shell, theme, surface, density,
     agent drawer) on every page. Never pick a different pattern or variant because it seems better.
   - **Copy only active specimens.** Build from components marked `data-active="true"`. Anything marked
     `data-active="false"` ("Reference — not in this app") is never used. Nothing exists outside the kit
     and the token block: no new component, colour, radius, elevation, type size or spacing step.
   - **Compose the page; don't clone a screen.** Follow the pattern's blueprint and match the drawn
     screens' look, spacing and finish, with the page's own content. Never copy one screen's content
     onto another page.
   - **Keep the concept.** Where `build-plan.concept` and a signature component apply to a page (the
     shade-card score, the boarding-pass header), use them as drawn; they are what make the app this
     client's.
   - **Journeys run as specified.** Build the pages so each journey step uses the components and states
     its row in the journey-to-component table names, with the document's exact wording for every refusal
     and message. Every page follows its wireframe frame's layout. Signature components are built as
     their component pages specify.
   - **Every component keeps every state from its component page and the kit's motion from Foundations:**
     hover, focus-visible, pressed, selected, disabled, loading, error and read-only. Every page also gets a loading state between action and response, the empty first
     run, undo after a reversible action, and its empty, filtered-empty, error, no-access and UNSET
     states, from the kit.
   - **Shell:** `.app`, `.app-rail`, `.app-top`, `.app-main`, `.app-body`; rail full height; top bar
     opaque, `.scrolled` on scroll; `data-chrome`, `data-surface`, `data-theme` on `<html>` as the
     expression card says.
   - **Agents:** the chosen `AG` drawer, opened from the app's one entry (`app.agent_entry`: the top-bar button,
     the floating launcher or the command field, never two of them), built on the
     platform's **live agent component** (streamed replies, real stages, tool outputs in the thread),
     never an automation that writes an answer for the page to show on refresh.
   - **Data and density:** tables scroll inside `.tblwrap`; one line per cell (two in the first column),
     two chips then "+n", about seven columns at 1,280 px; every image has a fallback; a count shown
     twice comes from one query.
   - **Overlays, spacing, colour:** modals and drawers only in the kit sizes and anatomy; the agent docks
     only at 1,440 px and wider; spacing only from the scale; no colour outside the token block; chart
     status series use the status palette; deltas coloured by good or bad, not by sign.
   - **The UX laws** in "The composition model" (`$D/references/reference.md`) bound everything the builder composes.
5. **The build plan** — `#build-plan` (composition model, Layer 4) and `#style-sets`, quoted with the
   contract: the seed, the concept, the app settings, the pattern and region fillers per page with the
   reason, the rules for unlisted pages, and the chart encoding per chart. A reviewer changes the app by
   editing these blocks; the builder follows them.

6. **The fingerprint** — `<script type="application/json" id="fingerprint">` with `client`, `app`, `idea`, `wow`,
   `signature_form`, `home_layout`, `nav`, `surface`, `shape`, `fonts` (`display`, `body`, and `reason` when either
   is a default face), `theme`, `density`, `imagery`, `colour_use`, `motion` and `accent_hue` (degrees), from the
   chosen direction as built. Once `check_ds.py … --register "$R"` is clean (it also compares the fingerprint with
   every app in the register), add it to the shared register:
   ```bash
   source ~/.local/poc-collateral/env.sh 2>/dev/null; D="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/design-system 2>/dev/null | sort -V | tail -1)"; [ -n "$D" ] || D="$(dirname "$(find ~/.claude/plugins -path '*design-system/scripts/check_ds.py' 2>/dev/null | head -1)")/.."; [ -f "$D/scripts/check_ds.py" ] || echo "check: design-system skill folder not found"
   R="$HOME/.local/poc-studio/design-register.json"; [ -f "$R" ] || { mkdir -p "$(dirname "$R")" && cp "$D/register/register.json" "$R"; }
   python3 -I "$D/scripts/register.py" add <client>-design-system.html "$R"
   ```
   and say in the hand-over that it was added. The next run reads it.

**And a type note:** the client's real typeface named, what was shipped instead, and why — *"Brand face
 is Gotham (Monotype, single-domain licence); shipped Montserrat as the closest open substitute.
 Production should license Gotham."* **A client reading that learns something; a silent substitution
 looks like we did not notice.**

**Plus a port note on the page itself**, stating the source version, max |ΔY| across all colours, and
every decision the port forced, **the brand source order applied, the expression card, the seed, and
every correction made to the scoping document (0.1)**. **Anchor the one branded surface to the client** —
with `brand` chrome the rail gradient starts at the sampled swatch; with `ink` chrome the signal colour
marks the active item; with `light` chrome the brand marks the active item and the primary action.

**Swap the sample domain, not the doctrine.** Proofpoint: Deal Gate → Quote Builder; gate artefacts
→ product configuration / pricing summary / legal review / order form; identities → seats; Okta IG →
Defender for O365; Stage 20/40 → awaiting approval / approved. **Every measurement stayed.**

⚠️ **Anonymise at extraction: the format travels, the client name does not.** The file is the
hand-over; do not publish it or share it as a link.
**If you fix something in the stylesheet, say so in the hand-over** — an unreported fix means
the next run reintroduces it and the skins quietly diverge.
**No demo or synthetic labels anywhere** — not "demo persona", not "synthetic data", not "used for demo
only". The app and its specimens read as the real product with real content.

---