# Reference · design system v12.6

Read the parts SKILL.md points to. Without approved wireframes, the last part ("Without wireframes") also applies.

## The composition model — how the builder makes pages from the kit

Components are the words, **patterns** are the sentence shapes, and a **seeded chooser** decides which
sentence each page becomes, so two apps differ and one app stays coherent. **Order of authority: core
→ UX laws → fit → seed.** The seed only ever chooses between options that are already correct.

### Layer 1 · Components with labelled variants

Each family below carries **two or three variants** when the app uses it, each visibly different, each passing
every rule in this file. Every other hero, interactive or signature component carries two or three as well, under a
short code of its own; a static atom keeps one form (SKILL.md 0.6 and Step 2c; `check_ds.py` counts at least 25
distinct codes). A variant rearranges the same atoms; it never adds a colour, radius, elevation, type size
or spacing step. Each component page draws every variant with its code.

| Family | Code | What varies |
| --- | --- | --- |
| Page header / record header | `PH` / `RH` | ID eyebrow vs breadcrumb; actions inline vs in a menu |
| KPI tile | `KPI` | number over label vs label over number; sparkline; mini-bar |
| Chart frame | `CH` | legend inline vs below; with a view switch |
| Table row | `TB` | single line vs name over meta; status stripe |
| Card | `CD` | metric-led vs media-led vs text-led |
| Filter bar | `FB` | pill facets vs dropdowns |
| Empty state | `ES` | icon-led vs illustration-led |
| List item | `LI` | one line vs two lines vs thumbnail |
| Right-rail panel | `RP` | summary vs action list vs mixed |
| Agent drawer | `AG` | right drawer vs docked column vs bottom sheet; thread only vs thread with canvas |
| Signature components | `SG1…` | the two layouts 0.8 requires |

### Layer 2 · The layout patterns

A page is built on **one** pattern. Carrying seven means "a list plus a side rail" is one option, not
the only shape.

| # | Pattern | Built around | Fits |
| --- | --- | --- | --- |
| **P1** | List workspace | one list (table or cards), tabs, toolbar, optional rail | many records, flat |
| **P2** | Split master-detail | a list beside the **live full record** | records worked one at a time |
| **P3** | Focus / canvas | **one hero object**, little chrome, docked actions | one record, a document, a photo, a form-led task |
| **P4** | Board | **columns of cards** that move through stages | stages, a process |
| **P5** | Metric dashboard | a **mixed-width widget grid** (8/4, 6/6, 4/4/4) | aggregates |
| **P6** | Map | **the map is the page**, full bleed; top bar, insight cards, list panel and legend float over it (wireframes `map-component.md`) | locations |
| **P7** | Feed / timeline | **a chronological stream** as hero | activity, history, a schedule |

The agent drawer overlays any pattern; it is never a page body. In the kit, each pattern declares its
regions and grid split, which families fill each region, how it reflows per device, and its own
variants (rail left or right, detail inline or in a drawer). Patterns may nest once (a P2 record pane
holding a P7 feed); never two levels deep.

### Layer 3 · The chooser — run here, never by the builder

**All choosing happens in this run, by this skill.** The builder (UnifyApps Headless) works with no person in the
loop and is good at reproducing what it is given, not at judging which of three options is better; left
to choose, it falls back to the safest default, and every app turns into a list with a rail. So this
skill makes every choice, records it, and hands the builder answers, not options.

**How each choice is made — best fit first, the seed only breaks ties:**

1. **Build the candidate set**: the patterns or variants that fit the data shape and persona and pass
   the UX laws.
2. **Rank by fit to this client**: the data, the persona's job, and the design concept (Step 2c). The
   best fit is the **recommended** choice, and its one-line reason is recorded.
3. **Use the seed only when two candidates fit equally well.** One seed per build, from a hash of the
   client name. This is what makes two clients with similar data land on different, equally good
   answers, without any memory of past builds.

What gets chosen this way: the **pattern per page**; the **active variant per family** (once, for the
whole app); the **chart encoding per chart**. Shell, theme, surface, density, the agent-drawer variant
and the concept are set by the expression and the personas from evidence, not by the seed.

**Coherence overrides everything:** one shell, theme, density and surface per app; one variant per
family; the same data shape gets the same pattern wherever it recurs.

### Layer 4 · The build plan — answers the builder looks up

The choices are handed over as one machine-readable block, `#build-plan`, which the composition
contract quotes. The builder does not choose anything; it looks things up:

```html
<script type="application/json" id="build-plan">
{"seed":"asian-paints-7f3a","concept":"shade card: scores and status as paint chips",
 "app":{"shell":"rail","theme":"light","surface":"glass","density":"comfortable","agent":"AG-1"},
 "variants":"#style-sets active set",
 "pages":[
  {"route":"/today","pattern":"P7","regions":{"stream":"LI-2","rail":"RP-1"},"screen":"1 of 3",
   "why":"a rep's day is a timeline of visits"},
  {"route":"/visit/:id","pattern":"P3","regions":{"hero":"SG1 shade-card scorecard","dock":"action bar"},
   "screen":"2 of 3","why":"one visit, worked in depth"}],
 "rules":[
  {"when":{"shape":"many records, flat","persona":"desk"},"pattern":"P2"},
  {"when":{"shape":"many records, flat"},"pattern":"P1"},
  {"when":{"shape":"aggregates"},"pattern":"P5"},
  {"when":{"shape":"one record, deep"},"pattern":"P3"},
  {"when":{"shape":"stages"},"pattern":"P4"},
  {"when":{"shape":"locations"},"pattern":"P6"},
  {"when":{"shape":"activity or schedule"},"pattern":"P7"}]}
</script>
```

- **`pages`** covers every page in the inventory: its pattern, which variant or component fills each
  region, which of the three screens shows it (if any), and why.
- **`rules`** covers pages the builder creates that the inventory did not list: the builder takes the
  page's data shape and persona and uses the **first rule that matches**. The rules are ordered so
  the first match is the recommended fit for this client.
- **Every drawn specimen is tagged** so the builder copies the right one: `data-component="KPI"`
  `data-variant="KPI-2"` `data-active="true"`. Variants that are not active carry `data-active="false"`
  and a visible label "Reference — not in this app", so a builder that copies from the page never
  copies the wrong one. The three screens and the blueprints use active variants only.

**The reviewer can still change things.** Overriding one page's pattern, or making another variant
active, is an edit to `#build-plan` or `#style-sets`; the builder follows whatever the block says.

### The UX laws — every candidate passes these first

- **Jakob's law** — nav, search, primary action and record sit where users expect, in every pattern.
- **Hick's law** — no region offers more actions than it needs; the rest fold into a menu.
- **Fitts's law** — 24×24 targets at least; primary actions near the hand; destructive actions apart.
- **Miller's law** — chunks of 5–7; a stat row is 3–6 tiles.
- **Proximity / common region** — grouping by spacing and containers, not colour.
- **Consistency** — one look per app; the seed serves this law.
- **Von Restorff** — one thing per screen stands out.
- **Tesler's law** — complexity goes into the system, not onto the user.
- **Aesthetic–usability** — a cramped or mis-spaced candidate fails even if structurally valid.
- **Serial position** — the most useful column or action at the start or end, not buried.

A candidate that fails any law is removed before the seed sees it.

---

## The view library — the reserve the app draws from

**Held, not always built.** Phase 0 picks what a build uses; the rest stay dormant. A view the library
does not carry is a view the app can never produce, so it is wide on purpose. **Charts, graphs, flows
and maps are engines**: build each renderer once with the shared palette, then configure it to the
types listed. `[kit]` = a class already exists, reuse it; everything else is built from tokens and
doctrine when first needed, never with new colour values.

**Data and record** — table / data grid `[kit .tbl]` (always with the toolbar and filtered-empty ≠
empty) · editable grid · tree-table · card gallery `[kit .tile]` · list, one to three lines · key-value
list · grouped list · leaderboard · KPI tiles `[kit .tile .loop]` (colour a delta by good or bad, never
by sign) · detail / inspector · master-detail · compare / diff · pivot · heatmap grid (sequential
palette, never colour alone).

**Charts (chart engine, `.chart` owns frame, title, unit, legend, no-data)**, grouped by the question:
comparison (bar, column, grouped, stacked, bullet, lollipop, radar) · trend (line, area, stacked area,
step, slope, sparkline `[kit]`, candlestick) · part-to-whole (donut for at most three parts, treemap,
sunburst, waffle) · distribution (histogram, box, violin, dot, beeswarm) · relationship (scatter,
bubble, hexbin) · flow (funnel, waterfall, sankey) · single value (gauge, progress ring, big number with
delta) · analytics (cohort, retention, control chart, pareto) · geo (choropleth, bubble map, flow map; a site map is never a dashboard widget: it is a P6 page,
handed to the map engine). A chart without a unit is decoration; the ramp never cycles.

**Graph (graph engine, layouts force / hierarchy / radial)** — network · tree · org chart · mind map ·
ER / schema · dependency / lineage · adjacency matrix · taxonomy explorer. Nodes and edges have full
states.

**Process and flow (flow engine)** — workflow / DAG · flowchart · swimlane · sequence · state machine ·
decision tree · data-flow · journey map / blueprint · approval chain · stage board `[kit .loop]` ·
stepper `[kit .sth .stv]` · kanban `[kit .kb]` (always with a non-drag alternative) · agent run / trace
`[kit .stages]`. Nodes reuse the stepper's pip and status tones.

**Spatial (map engine: layers, markers, heat, routes, clustering, legend, zoom, drill-down)** — map ·
canvas / whiteboard · floorplan · network topology · slot / seat map `[kit .slot]` · mini-map.

**Temporal** — calendar month / week / day / agenda / slots `[kit .cal .agenda .slot]` (today takes a
ring, selection takes the fill, never both) · timeline · Gantt · resource schedule · roadmap · activity
feed `[kit .feed]` (a change carries its reason) · audit log.

**Agentic** — agent drawer `[kit .agent-drawer]`, the home of every agent (see "The agent component") ·
agent page `[kit .canvas]`, only when the agent is the page's whole purpose · agent workbench · AI
insight card `[kit .ai]` · reasoning trace · tool-call inspector · prompt console · suggested prompts
`[kit .chips]` · approval / action diff · citation panel.

**Document and artefact** — document reader · rich-text editor · form `[kit .fld .ctl]` · form builder ·
spreadsheet grid · code / log / JSON viewer · PDF / file preview · media gallery · slide view · redline
/ track changes · artefact studio `[kit .studio2]`.

---

## The component inventory — every atom, every state

The views are built from these atoms. **Reuse the stylesheet class whenever one exists**; a second
implementation is the most common failure on this work (mixed radii, two kinds of search field). A new
atom is built from tokens and the Form / Components doctrine, inside the chosen shape's radius scale.

- **Actions** — buttons `[kit .btn-p .btn-s .btn-t]`, icon button, button group, split button, link, menu button.
- **Inputs** — text and textarea `[kit .ctl]`, search `[kit .field]`, number stepper, tag input, OTP;
  select, combobox, multi-select, checkbox and radio `[kit .opt]`, switch `[kit .tog]`, segmented
  `[kit .seg]`, slider, rating; date, time and range pickers, file upload.
- **Status and display** — badge, count dot, status tag `[kit .tag]`, chip `[kit .chipsel]`, avatar and
  group `[kit .av .faces]`, icon, progress bar `[kit .prog]` and ring, skeleton, spinner.
- **Containment** — glass cards `[kit .g1 .g2 .g3]`, panel, accordion, tabs `[kit .tabs]`, tile, inset `[kit .inner]`.
- **Overlays** — tooltip, popover, menu `[kit .menu]` (add trigger, dismiss and focus behaviour), context
  menu, modal, drawer, bottom sheet (phone only), toast `[kit .toast]`, banner (`.note` is the seed),
  command palette.
- **Navigation** — top bar, rail, breadcrumb `[kit .crumb]`, pagination `[kit .pg]`, tabs, stepper, tree nav.
- **States** — empty `[kit .empty]`, filtered-empty, error, loading, no-access, inline validation
  `[kit .ctl.err .hint.e]`, UNSET.

### The universal state + anatomy rule

```
STATES   default · hover · focus-visible · active/pressed · selected · disabled · loading · error · read-only
         and, where they apply: clickable vs static (a row or card that opens something shows it on hover;
         one that does not, never does) · expanded / collapsed · dragging / drop target · new or unread ·
         visited · success · warning · empty · AI-written / human-edited
DECLARES border width · border colour · radius · background · elevation · cursor · the token for each state
```

**Each component page says which states apply and which do not, and why** ("no selected state: the list
only opens a record"). A state that applies and is missing is a defect; a state drawn that cannot happen
is noise. Tables state the row hover, the selected row, the focused cell, the sorted column, the row
being edited, a disabled row action and a loading row. A static item never gets a hover; a clickable one
always does, with the pointer cursor.

Every interactive atom ships and is audited across these states, including the engines' parts: a graph
node, an edge, a map marker, a flow step, a timeline event and a kanban card all have hover, selected
and disabled states, from tokens, the radius scale and the two elevations. An atom that looks unfinished
is usually missing its focus ring, its disabled tone or its selected treatment.

---

## The component page — how every component is documented

**In v12 the component page is compact; SKILL.md 0.6 gives its parts** (header, specimen, states, variants, rules,
reference, each marked with `data-part`), and 0.8 gives the signature's full-depth page. What still applies from the
older spec:

**How the state grid renders without a mouse.** After the expression kit, in the same `<style>` block, add a
**state-hook block**: for every `:hover`, `:focus-visible`, `:active` and selected rule in the stylesheet and kit,
repeat the same declarations under a state class (`.is-hover`, `.is-focus`, `.is-active`, `.is-selected`,
`.is-loading`; for example `.btn-p.is-hover{…}` copying `.btn-p:hover{…}`). The stylesheet stays verbatim; this block
only mirrors it. The builder uses the real pseudo-classes; the state classes are for the guide.

**A wide component (a table, a board, a record panel, anything over about 480 px) takes the full content width,** one
variant per row; narrow atoms may sit side by side. A component is never squeezed to fit a column.

**Show components on their real material** (the surface they live on, both themes through the switch) and, where they
live beside others, in that context.

**The finish bar:** parts aligned on one baseline, padding from the spacing scale, a visible focus ring, icons at their
optical size, no text squeezed or orphaned, and the client's real content.

---

## Foundation additions (so the new views render correctly)

These extend the foundations; they never move a measured value.

- **Semantic token tier.** Colour by job through a semantic alias layer, so the Step 3 reskin is
  near-mechanical and the hardcoded gradients and focus rings (`.btn-p`, `.msg.me`, `.tog.on`, the
  `rgba(0,113,206,…)` rings) stop slipping past the port.
- **Glass fallback.** Under `prefers-reduced-transparency`, Windows forced-colors, or a browser without
  `backdrop-filter`, glass falls back to the solid rung, so the page stays legible.
- **WCAG 2.2.** Targets at least 24×24 (buttons, pips, markers, slots, nodes); a visible, measured focus
  ring; a focused element never hidden by a sticky header, banner or the agent launcher; a non-drag
  alternative for every drag.
- **RTL and other scripts** (when the document names Arabic, Hebrew or CJK readers). CSS logical
  properties so the page mirrors; mirror directional icons only; allow for text growing 25–35%; add
  Arabic or CJK fallback fonts, since Archivo and IBM Plex Mono cover neither.
- **Stacking order.** base < sticky < dropdown < drawer < modal < toast < tooltip.
- **Motion.** Keep 120–160 ms and "nothing else moves"; feedback starts within 100 ms; each motion
  has a reason (orient, confirm, emphasise).
- **One visualization palette for all four engines.** Categorical, sequential, divergent and threshold
  palettes as separate jobs, colour-blind safe, never colour alone, and a table view for every chart.
- **Icons from one open, licensed set**, named in the style guide, plus the node, marker and edge
  glyphs the engines need.

**Parked:** design-token JSON export, multi-brand theming, locale formatting and pseudo-localisation,
product tours, a microcopy system, print and email rendering, executable audit tooling.

---

## Form — the parts people get wrong

* **No borders on cards.** Separation is elevation and tone, never a line. Hairlines *inside* a card
  — row separators, a divider between two regions — are fine; the rule is about the card's outline.
* **A card carrying colour gets exactly one treatment** — gradient wash alone, **or** solid tint plus
  one inset hairline. Never both. A gradient already says "selected"; a ring on top of it is the most
  common violation, and it shows up most on selected options inside a chat input. A solid tint
  without a ring reads as a flat slab, which is why the inverse holds.
* **Corner radius is a fixed five-step scale. Never improvise a value.** **10px** everywhere — cards,
  tiles, containers, inputs, selects, buttons, panes, drawers, modals, table containers · **6px**
  small inner elements — tags, chips, code · **pill** for toolbar search, facets and accent pills ·
  **circle** for avatars and account logos · **studio only** shell 28 / canvas 22 / sheet 16 /
  tile 12, because a 10px corner on an 1,100px object reads as a cut rather than a form. **Never
  8/12/14/16 outside that scale, and never a mix on one page** — mixed radii are the single most
  common reason a build reads as unfinished. These are the **soft** scale, the house default. The Shape dial
  (SKILL.md Step 2c, `data-shape` on `<html>`) swaps the whole scale at once: **square** 3 / 2 / pill / circle
  (studio 4 / 6 / 6 / 8), **round** 16 / 10 / pill / circle (studio 20 / 24 / 28 / 32). One shape per app. ⚠️ A blanket flatten to 10px was tried on the SailPoint
  wireframe 22 Sept 2026 and reverted within the hour. **Do not re-propose it.**
* **Ambient aurora in the brand theme, never flat grey.** Layered low-opacity radial blooms
  distributed down the page so a long document does not go flat below the fold. Percentage-sized
  radials on the body; avoid `background-attachment: fixed`, which bands in full-page captures.
  **Dense internal tool: 3–4% maximum, two or three blooms, page body only** — never behind a table
  or a side pane, which take a solid near-white ground so rows stay legible.
* **Glass in three tiers plus a nested rung**, with a **1px inset top highlight** — that detail is
  what sells it as light catching an edge. Nested `inner` surfaces instead of a second bordered box
  is what stops a UI looking cheap.
* **Two elevation levels, never a third.** Resting and raised. Rows do not lift on hover; they change
  tone.
* **Four type sizes, two weights** (400/600), `tabular-nums` on every number. **The mono face is
  structural, not decorative** — table headers, eyebrows, KPI labels, citation and version chips take
  it; body copy never does. If the mono is not actually embedded the headers fall back silently and
  the whole grid loses its register.
* **One icon weight, two sizes** — 16px in tables and chips, 18px in nav. Stroke 1.6.
* **Motion is 120–160ms ease-out on panes, drawers and tonal hover, and nothing else moves.** No
  count-ups, no card entrance animations, no skeleton shimmer.
* **Tags are quiet and smaller than the smallest button** — 11–11.5px against a 13–14px button,
  tonal, no border, no sentence inside. A tag states a fact; it must never read as pressable.

## Components — the doctrine, not just the class

* **Every table gets a toolbar**: search left, filters right, nothing in the middle, **above and
  outside** the card (the card is the table's **ground**, not its container). The search **reports
  its result beside itself — "4 of 7"**. Three or four facets (D8), drawn from the visible rows so a
  facet can never offer a value returning nothing. Applied filters are removable chips with one
  *Clear all*.
  **⚠️ A filtered-empty table is NOT an empty table and they must never share a state.** *"No rows
  match your search and filters"* with a clear action is a different fact from *"No opportunities at
  Stage 20 yet"* with a create action. **Showing the second when the first is true is the single most
  common table bug and it makes working software look broken.** A static reference matrix — a
  discount-authority table, a legend, a key-value spec block — is not a record list and takes no
  toolbar.
* **Pagination is built once and reused.** The range names the **total** ("1–10 of 47"), reflects the
  filter, disables rather than hides at the ends, and does not appear under ~25 rows.
* **Every AI or system-generated insight goes in a labelled AI Insight card** — subtle brand
  gradient, one CTA inside the same card, overflow behind a chevron, never by growing the card or
  truncating mid-sentence. The user must always be able to tell what the data *says* from what we
  *inferred*. **Reference: Topcon's approval-suggestion step** — a *"Suggestion only — you decide"*
  chip, a grounding line naming the source SOP and precedent set, per-row confidence, a reason per
  row, **and one row deliberately excluded with its reason shown.** Copy that shape.
* **Kanban** is for states a person changes and items that can move *backwards*. Fixed-order work is
  a **stepper**. WIP limits shown in the attention tone. The drop zone is **the one dashed edge we
  allow**, because the dash means something; every other dashed edge is decoration.
* **Calendar has three shapes** — month grid ("when is it free"), agenda ("what is happening"), slot
  picker ("commit to one"). Shipping a month grid when the user must choose a *time* is the common
  version of this mistake. Today takes a ring, selection takes the fill, **never both on one cell**.
  A taken slot is struck through and disabled, **never hidden** — hiding it makes a busy day look
  empty.
* **A person is a record, not a string.** Person card or face stack anywhere a human is named. Cap
  the stack at three faces plus a count; the overflow chip is a count, not an avatar; initials, never
  a generic silhouette.
* **An activity feed is not a stepper** — a stepper's shape is known in advance, a feed's is not.
  Newest first, mono timestamps, actor and object bold but not the verb, automated entries say
  "System", and a change carries its reason. A history that records *what* without *why* gets
  re-litigated in a meeting.
* **Chart frame:** the system owns the card, title, **unit**, legend placement and no-data state; the
  ramp and marks follow the palette rules and the `dataviz` skill. A chart without a stated unit is a
  decoration. **Never colour a delta by its arithmetic sign** — colour it by whether the movement is
  good, and name the comparison period beside it. **A series that encodes a status (pass / fail,
  on track / off track) takes the status palette and a worded legend**, never steps of the brand
  colour — Vermont's pass-rate chart showed Fail, Needs attention and Pass as three blues.
* **Container doctrine:** **modal** only for irreversible or legally significant acts (withdraw,
  reject with mandatory reason, e-signature, stop ship) — blocking is the point, never nested, never
  holding a scrolling table · **right drawer** (~480px, dismissible) for configuration attached to
  the current record · **third pane** (persistent, resizable, pushes rather than overlays) for the
  inspector, whose whole value is surviving a move to the next row · **stepper** where the *order* is
  part of the meaning · **full page** only for objects deserving a shareable URL · **inline expand**
  for hierarchies · **bottom sheet** never, on desktop.
* **A control sits inside the boundary of what it changes** — no divider between an active tab and
  the panel it governs. **Named exception: the table toolbar**, above and outside the card.
* **Header carries identity, navigation context, notifications, profile. Nothing else.** No role or
  persona switcher — a visible `Planner · CSR · Manager · Auditor` control tells the client instantly
  this is a mock, and real RBAC is an attribute of the signed-in user, so role switching lives in the
  profile menu. No theme toggle, no demo-path control. A quiet scope indicator is fine.
* **Left nav: logo → navigation → profile at the bottom**, on the chrome the expression chose
  (`brand` gradient, `ink` or `light`), full height at every scroll position. With a top-navigation
  shell, the same order runs left to right.
* **The top bar is opaque.** Content scrolls under it without showing through it.
* **One composer per surface. One right-hand rail, not two** — assistant and inspector share it as
  two modes; opening the assistant swaps the mode and remembers the inspector's state.
* **The agent component — always a drawer, never a card on the page.** Pentland's Range Copilot was
  built as a full-width block on Home, wired as an automation that wrote answers into an object the
  page showed after a refresh. That is not an agent. The rule:
  - **Where it lives.** A right-side **drawer** (`.agent-drawer`, ~440 px) that slides over the page
    without reflowing it — the default on every internal page. It opens from the app's **one** entry (a
    top-bar button, the floating launcher `.agent-launch`, or the command field; SKILL.md 0.9) plus a keyboard
    shortcut, and closes with Esc, returning focus. Variants, each for a reason: **wide** (720 px) while an answer carries a chart or table;
    **docked** as a third column (`.app.with-agent`) for personas who keep it open all session;
    **full screen** on a phone; **studio region** inside a two-pane artefact studio (interface left,
    conversation right, no card); **full page** only when the agent is the screen's whole purpose.
    One drawer at a time; it shares the right-hand side with the inspector as two modes.
  - **Anatomy, top to bottom.** Header: the agent's name, a scope chip (read-only, or what it can
    act on), expand / dock / close. Context chips: the record or page it is looking at. Thread: agent
    left, person right; the agent speaks first with three suggested prompts from the person's own data.
    Working stages while it thinks (`.stages`), named by what it is really doing. Answers rendered with
    their tool outputs — chart (chart engine, with unit), in-thread table, file card, citation chips
    with the evidence hover card, record links — each marked AI-written. Proposed actions as a
    **human-in-the-loop card** (`.ad-action` with `.ad-diff` before → after, approve and reject with a
    required reason). Dock: suggestion chips **outside** the composer, then the composer.
  - **Every state:** closed (launcher with an unread dot when the agent has something), opening, empty
    first run, thinking (stages), streaming, answered, partial answer with a gap named, refused (out of
    scope, with what to try instead), tool failed (which step, retry), offline, and read-only.
  - **How it is built.** On the platform's **live agent/chat component** — streamed replies, real
    stages from the agent run, tool outputs rendered as they arrive. Never an automation that stores
    the answer in an object for the page to pick up on refresh. The composition contract says so.
  - **AI on a page is not the agent.** A dashboard may carry an **AI insight card** (`.ai:not(.msg)`)
    that summarises and links "Ask about this" into the drawer, and a field may carry an AI-draft
    marker with an inline assist. The conversation itself always opens in the drawer.
  - **Loading is a sequence, not a spinner** — a copilot that shows its stages reads as reasoning, a
    spinner reads as latency. **The agent speaks first.**
* **No stacked sublines under headers, no redundant preview data.** One header, one line of support
  at most, and only if it carries something the header does not. Show data by the priority of the
  flow the user is in on the screen they are on.
* **A fifth data state: UNSET.** Beyond empty / loading / error / populated — **a field belonging to
  a journey the user has not completed shows as visibly unset, never a seeded default dressed as
  their own answer.** On one build this produced a cost one-pager reading $26,250 against an actual
  $55,550 and a visit "booked" for March 2011, while the Next card told her to plan the visit the
  one-pager said was already booked.

## Layout, spacing, density and overlays — the rules the v5 screenshots broke

Every rule below comes from a screenshot of a v5 output. They apply to every screen that is drawn, and the builder applies them to every page it composes.

**Spacing.**
- Only the spacing scale (`--s-1` 4 px to `--s-12` 48 px). Page padding 24 px (16 px on a phone),
  24 px between sections, card padding 20 px (16 compact, 24 comfortable), 8 px between related
  controls, 4 px between a label and its value. No other values.
- **Equal rhythm inside a row of cards**: the same padding, the same order of parts (eyebrow → value →
  support line), top-aligned. A label that wraps to two lines must not push its value below its
  neighbours' (image 1: "Candidates in pools" pushed 77 down) — shorten the label or let the eyebrow
  row reserve two lines across the whole row.

**Filling the space — no dead areas.**
- **A row fills its width.** Tile rows use as many equal columns as tiles (3, 4, 5 or 6) across the
  full content width. Two-panel screens split 8/4 or 7/5 of a 12-column grid. A row that leaves a
  large empty area on the right, or a card with a large empty area below its content, is redesigned:
  move a related panel into the gap, or let the content take the width.
- **Headers carry their actions on the title row.** Page header: title left, primary action right,
  same line. Record header: ID eyebrow, title with status tags, one meta line; actions right-aligned on
  the title row — never floating in their own row with empty space beside them (image 5).
- **Definition lists** (`.dl`) use a label column of 120–160 px, never wider (image 5's 250 px label
  column left a channel of white).
- **Specimen height fits the content.** Device specimens size to their content; a fixed height only
  when the screen scrolls by design.

**Density — what fits in a cell, a card, a column.**
- **Tables: one line per cell by default; at most two in the first column** (name over one muted line).
  Longer text is truncated with an ellipsis and the full value in a tooltip, or moves to an expanded row
  (`.row-x`) or the detail drawer. **No paragraphs in cells** — image 4's reasons paragraph and
  four-row sub-score breakdown belong in the expanded row.
- **At most two chips per cell, then "+n"** (`.cell-chips`, `.more`). One status tag per cell. Nothing
  in a cell overlaps or leaves its cell (image 4: a source pill sat on the "Approved" chip; the status
  tag was cut off at the table edge).
- **Column budget at 1,280 px: about seven columns.** More columns → a column picker, a frozen first
  column (`.tblwrap.freeze`) and horizontal scroll inside the table. Minimum widths: ID 96 px, name
  200 px, status 120 px, number 80 px, date 104 px. Numbers right-aligned in tabular figures.
- **Cards in narrow columns** (kanban, lists): a card is at least 240 px wide and holds at most four
  lines — title, one meta line, one status, one blocking or next-action line. No two-column layout
  inside a card narrower than 320 px. Long status text truncates (image 2: "Feedback 2 days overdue"
  left the card; "No feedback yet" wrapped to three lines).
- **Row heights follow density**: 36 / 44 / 52 px for compact / default / comfortable, set by the
  persona (0.4), never mixed on one screen.

**Copy inside specimens.**
- **Never show field names, query syntax or rule expressions as text** — image 1's tiles read
  "status = open" and "interview_count > 0". Write what the person needs: "of 11 jobs", "3 with
  feedback overdue".
- IDs in mono only where the person really uses them (a requisition number), never as decoration.

**States never move the layout.** Hover, selected, focus and active change colour, shadow or an inset
ring — never padding, size, alignment or border width (image 1: the selected "On hold" tile grew a
thick border and centred its text).

**States are drawn once, in the component pages, not per screen.** Empty, loading, error,
filtered-empty, no-access and UNSET are documented as components, and one of them may appear in context
on one of the three screens. The builder applies them to every
page it composes. **Never several full app shells side by side** (images 3 and 6: three shells in one
row left a 200 px content area and one word per line).

**Overlays — one system** (kit: `.modal`, `.drawer`, `.agent-drawer`, `.ov-hd/.ov-bd/.ov-ft`):

| Overlay | Width | Height | When |
| --- | --- | --- | --- |
| Modal S | 420 px | content, max screen − 64 px | confirm an irreversible act |
| Modal M | 560 px | content, max screen − 64 px | a short form |
| Modal L | 760 px | content, max screen − 64 px | review or compare before committing |
| Drawer S | 420 px | full height | the agent; a quick peek |
| Drawer M | 560 px | full height | record detail, inspector, filters |
| Drawer L | 760 px | full height | the agent with a chart or table; a long form beside the list |
| Agent docked | 420 px column | full height | only at 1,440 px and wider |

Same header (title, one line of support, close), same body padding, same footer (secondary actions
left of primary, primary last on the right, a destructive primary in the negative tone). One overlay
at a time; a drawer never opens a modal on top of itself except to confirm. Image 7's agent filled
most of the screen because it was a docked column at 1,280 px; the kit now forbids it.

## The use-case dial

Same system, same components, both themes. What moves is restraint, ground and radius scale. The radii below are
the soft shape's; with `data-shape="square"` or `"round"` the same steps take that shape's values (SKILL.md Step 6).

| Use case | Ambient | Ground | Radii | Colour |
| --- | --- | --- | --- | --- |
| **Dense internal tool** (PLM, config, ops console) | aurora 3–4%, 2–3 blooms, body only | solid near-white behind tables and side panes | 10 / 6 / pill | brand on primary action, active nav, selected — nothing else |
| **Client-facing demo surface** | full aurora, blur 58–70px, vignette | glass tiers 1–3 | 10 / 6 / pill / circle | brand gradient on the nav rail; one accent pill |
| **Artefact / document studio** | quiet — the canvas is the subject | sheet white on a tinted shell | 28 / 22 / 16 / 12 | greyscale plus one brand accent |
| **Dark-first ops console** | blooms *lighter* than the page | opaque rung for any container holding glass | 10 / 6 / pill | brand-as-text steps up; brand-as-fill holds |
| **Ported screens from another build** | inherit the host | — | **normalised, see below** | inherit |

**Ported code gets one card, imposed from outside.** Screens from a separate build each bring their
own idea of a card — on the Enroll · Belong canvases there were **six paddings, four radii and three
shadows** between them, invisible one screen at a time and obvious the moment a dozen stack in one
column. **Do not edit them one by one.** One normalising block at the end of the ported stylesheet:
one radius, one surface, one shadow · **three padding tokens only** — a card you read into, a row
inside a card, a compact cell · a card holding rows takes **no padding of its own** and its rows
carry the rhythm · **media cropped to one aspect ratio** (`height:auto` on an illustration is how two
cards in a row end up different heights) · **restate the selected and status rings after the
normaliser** or the reset eats them · check the containers too — the agent's note, the stepper and
the action bar must sit in the **same column** as the cards.

## The defect register — re-derived on the system itself

**⛔ A figure asserted about the system from a measurement taken on a PORT of it is not evidence.**
One "defect" was recorded that way — a claim that §14's chart ramp fails its own 2.60 figure — and
had to be **withdrawn**: measured across all twenty triples, the best is exactly 2.60, and the dark
pair is exactly 4.24, both as the document claims. A luminance-preserving port makes this trap
worse, not better, because the port's numbers genuinely are the source's, so a wrong number looks
doubly confirmed. **Check every "the file says" against the file.**

The standing lessons, all derived from defects on the record:

* **White on the brand fill** — check every gradient stop, not just the mid one.
* **`.ai` vs `.msg.ai`** — an unscoped insight-card selector captures every agent chat turn.
* **Nested glass in dark** — a container holding glass takes the opaque rung.
* **A theme with no switch** follows the reader's OS and half your work is invisible.
* **Bare rgb triples** survive any regex port.
* **A wrong number in a document is not a wrong colour.** Correct the number.

**Added in v5, from the Pentland, ClickUp, Vermont and Topcon runs:**

* **Same core, same look** — with the logo covered the four apps were one product. The core stays
  fixed; the expression (Step 2c) must differ, with evidence.
* **An agent on a page** — Pentland's Copilot as a full-width block, fed by an automation and a
  refresh. Agents live in the drawer, on the live agent component.
* **A brand decided outside the file** — three runs settled a hue conflict with a "standing decision"
  from the calling flow; Pentland's black-and-lime brand shipped electric blue. Only the brand source
  order decides.
* **Must-haves moved to future scope** — Pentland's material compare, detail pane and docked Copilot
  were L1 and were dropped. Every L1 ID maps to an inventory row.
* **Journeys never drawn** — refusals, approvals and counters were in the scoping document and nowhere
  on the page. Every journey is a flow (0.7).
* **Status as brand steps** — Vermont's chart showed fail and pass as shades of blue.
* **A rail that stops, a bar you can see through** — layout defects in the build that the kit and the
  composition contract now prevent.
* **Personas without screens** — Vermont's merchandiser had no phone or tablet layout reachable from
  any shell.
* **A dull dark** — mid-slate grounds and heavy glass; failing contrast on its own tiers. Rebuilt.

**Added in v5.1, from the first v5 runs and their review screenshots:**

* **Screens at the wrong width** — "1,280 px" screens drawn in a narrower column took the desktop
  layout at half width: state screens one word per line, a docked Copilot covering the page. Every
  screen is now a device at real width, scaled.
* **Overlays of every size** — modals and drawers improvised per run. One overlay system, three sizes.
* **Dense tables and cards** — paragraphs, four-row breakdowns and stacked pills in cells; two-column
  layouts in 240 px kanban cards. Density rules with hard limits.
* **Dead space** — half-empty rows, actions floating in their own row, a 250 px label column.
* **Implementation leaking into copy** — "status = open" as a tile's support line.
* **Unbounded variants** — options with no codes and no way for the builder to pick one coherently.
  Coded variants, at most three style sets, one active.

## The finished-piece rule — no rework after hand-over

**What this skill hands over is the final piece.** The person receiving it should be able to use it
as it is: open the style guide, take the token block, drop in the logo kit, give the composition
contract to the builder. Never hand over a partial build, a "first pass", or a list of things still to do.

**Build first, review, then check once.** Do not run the full checklist after every fix. Build the
page, then do the design review below, then run the render check (Step 6) and the checklist once, fix
what fails, and re-check only the items that failed.

### The design review — now Step 6b

The creative director's judgement in SKILL.md Step 6b replaces the self-review earlier versions ran here. It uses
`$D/scripts/scan.py`'s screenshots, `$D/references/creative-director.md` Part 2 and `$D/references/calibration.md`
(which holds the generic tells), and records its scores in `#review` (`data-distinctiveness`, `data-wow`,
`data-richness`, `data-accuracy`, `data-ux`, `data-craft`, `data-journey`, `data-rounds`).

**The checklist — ten items:**

1. **The idea and the components.** The direction, thesis and showcase are on the page (three screens, two or three
   close-ups); every component the inventory needs has its page (the signature at full depth, the rest compact, 0.6),
   each added one with its reason; every hover, focus and press rule has its state class; the views, navigation
   options and expressive layer are drawn; the richness floor and the budgets hold (25+ variants; 12,000 words, 24
   tables, 70,000 px). `check_ds.py` and `scan.py` both print no `check:` line, and every `skipped` line from
   `check_ds.py` was checked by hand (SKILL.md 0.0 rule 8).
2. **Scope and coverage.** Every L1 feature ID and component ID in the document appears in the
   inventory (checked by script; with wireframes, every manifest component and frame page instead). Nothing the document put out of scope appears; dormant views are listed
   as not built.
3. **Journeys and signature work.** Every journey step has a row in the journey-to-component table with
   the document's exact wording for refusals and messages; every manifest component is used by a step or a
   page, and no step lacks its component. Each signature component shows anatomy, every state, data
   variants, interactions, responsive behaviour and two layouts. The main agent's drawer is open on the
   third screen; every other agent is on the agent-drawer component page; no agent sits in a
   page layout.
4. **The builder has answers, not options.** The contract and `#build-plan` cover every inventory page
   (pattern, region fillers, reason) and give rules for unlisted pages; `#style-sets` has one active set;
   every specimen carries `data-component`, `data-variant` and `data-active`, and every non-active
   variant is labelled "Reference — not in this app". The contract quotes the default interactions, the
   live-agent rule and the UX laws, and matches the expression card and kit classes.
5. **Brand and research settled.** Research questions 1 to 3 met their depth (Quick on a second source when Steps 1,
   2 and 2b sampled the live site; Deep when the sample failed or two sources disagreed); the rest met their depth or are
   recorded as `[DERIVED]` with what was tried; the ledger and every source with its date are in the port
   note. The expression card records the design concept with its evidence, every dial with its evidence, and
   the logo-off answer; the concept is visible in the signature components, the variants and the one
   signature interaction.
6. **Both themes measured.** The contrast audit ran in light and dark; every failure is fixed; the ratios
   in the token block match the rendered page.
7. **Renders clean.** One self-contained HTML file, fonts and images embedded. The render check returns
   zero page scroll, spills, clips, vertical clips, overlaps and squeezed text anywhere on the page —
   screens, component pages, state matrices, diagrams and the guide's navigation — zero broken images,
   every font loaded, no unstyled component class, in light and dark, at 1,280 × 800, 1,280 × 680 and
   375 × 812. The only allowed flags are two-line labels in documentation tables, each checked by eye.
   Also look at a screenshot of the navigation and of one state matrix at 1,280 × 680.
8. **Layout and density hold.** No large dead areas; actions on the header's title row; one line per
   table cell (two in the first column); at most two chips per cell; cards within four lines; no field
   names or query syntax in copy; states do not move the layout; overlays use the kit sizes and anatomy.
9. **No leftovers, no generic tells.** No `TODO`, `TBD`, `lorem`, `placeholder`, empty links or empty
   sections, and no "demo" or "synthetic" labels anywhere. The creative director's review (Step 6b) is recorded in
   `#review` with every score, every generic tell it named is fixed, and the fingerprint is in the register. The
   theme switch, tabs, links and copy buttons work with no console errors. The one allowed exception is the labelled
   UnifyApps stand-in logo, and only under the conditions in stop 2.
10. **Consistent and handed over.** Token names, port note, build brief and style guide agree on every
    number. The three hand-over answers are written in the page's last section.

**Show the result.** The hand-over reply lists the ten items with pass and one line of evidence each
(for example "1 · pass · direction C, 3 screens, 2 close-ups, 34 component pages, 7,800 words"). An item that cannot show
evidence has not passed.

**A failure found here is fixed here, not reported as a known issue.** Only something that genuinely
cannot be fixed inside this run (the client's logo file does not exist anywhere) goes into the
hand-over, with the reason.

## Hand it over with these three answers

Write them in the style guide's last section and repeat them in the reply.

> **What is the WOW factor here? Name it in one sentence.**
> **What would the client push back on first?**
> **What is the weakest part, and do you know it?**

**Answering the third honestly is not a confession, it is the deliverable.** A hand-over that names
its own weakest part gets fixed; one that hides it gets found.
---


---

# Without wireframes — 0.2, 0.3 and 0.5

These run only when the design system is made from the scoping document alone (no approved wireframes). With wireframes the frames already chose each page's pattern and views.

## 0.2 · Map to surfaces

The build brief resolves to one or two **surface archetypes**; each sets the use-case dial row
(above) and the layout patterns its pages usually take ("The composition model", above):

- **Dashboard / overview** → P5 metric dashboard · demo-surface row
- **Dense ops console** or **record workspace** → P1 list workspace, P2 split master-detail, P3 focus · dense-internal row
- **Process / workflow** → P4 board, plus flow views · dense-internal row
- **Map / geospatial** → P6 map · demo-surface row
- **Activity / history** → P7 feed · either row
- **Wizard**, **conversational**, **artefact studio**, **portal**, **mobile-first** → the stepper, the
  agent drawer, the studio shell, a lighter shell, a one-column phone shell, inside whichever pattern
  the page's data needs

Everything the brief does not name stays dormant.

## 0.3 · The data-shape → view rule

Read the dominant data shape of each page and reach for the matching view, so a flow is drawn as a
flow and not a table. The pattern-fit table in the composition model turns the same reading into a
page layout.

- **Many records, flat** → table or card list. **One record, deep** → detail / focus view.
- **A value over time** → trend chart or timeline. **Values compared** → comparison chart.
  **Parts of a whole** → part-to-whole chart. **Spread** → distribution chart.
- **Entities and relationships** → graph, tree, ER or dependency view.
- **Steps, branches or stages** → flow diagram, swimlane, board or stepper.
- **Locations** → map. **Durations over time** → Gantt or timeline. On any time axis the today and
  deadline markers replace their own column's heading (never sit on top of the neighbouring days), and a bar's
  label sits inside the bar when it fits, otherwise after it, never under the today line.
- **An agent's work** → run / trace + approval. **A long text or file** → document, code or preview view.
  **Two things side by side** → compare / diff.

**Read what the agents and automations can output, not only the screens.** Each output type is a view
the system must style, even when no screen in the BRD shows it: a **chart** tool → the chart engine,
drawn inside that agent's drawer; a **file** output → document card and file viewer; a **table** →
the in-chat table; a **proposed action** → the approval card; a **citation** → citation chips and the
evidence hover card. "There is no trend data" is not a reason to leave charts dormant when an agent can
draw one.

## 0.5 · Record the build brief on the page

The build brief ships in the port note (Step 7), alongside the colour decisions: the surfaces chosen,
the views drawn from the reserve, the density, and the out-of-scope line. A reviewer should be able to
see *why these views and not others* without opening the BRD. **The views you did not build, because
the BRD did not ask for them, are part of the record** — they show the scope was a decision, not a
limit.
