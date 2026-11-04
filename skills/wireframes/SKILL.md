---
name: wireframes
description: Turns the approved scoping document (BRD) into low-fidelity wireframes that decide how each page works — who arrives, what they decide, what needs them and their one next step — and draws them as grey-box PNGs from a short JSON layout spec by a bundled script (no browser, no HTML), plus a component manifest, the closed list of components the design system then designs and the build then uses. Names the app's signature (the one object or interaction no other app has) and draws it as itself, picks each page's pattern and shape from its work so no two apps share a house layout, follows the bundled patterns reference and, for map pages, the map-component reference. Runs in POC Studio's Plan phase between Scoping and the Design System, and for /poc-studio:wireframes.
---

# Wireframes (POC Studio, Plan phase)

**Input:** the approved scoping document (`02-scoping/scoping-document.docx`), the client and use case.
**Output** in `<workspace>/02b-wireframes/`:

| File | What it is |
|---|---|
| `<slug>.wireframe.json` | the layout spec you write (the only thing you write by hand) |
| `png/<page-id>.png` | one low-fidelity frame per page, at the persona's real width |
| `<slug>-wireframes.pdf` | all frames in nav order: what the person approves and what goes to Orbit |
| `wireframe-manifest.json` | generated from the spec: the app's signature, pages with their brief and pattern, the demo journey, every change to the BRD's layout with its reason, and every component with its purpose, the data it shows, its actions, pages, blocks, CMP IDs, variants, states and, for maps, the data contract and behaviour |

**Why this stage exists.** The BRD says what the app must do: its pages, personas, data, agents and demo story.
The wireframes decide *how each page works*: what the person sees first, what needs them, how they decide and what
they do next, and so what is on each page and where. The design system then designs the components in the
manifest (plus its baseline: sign-in, empty/error/loading/no-access, toast, confirm, and any the journey needs, marked
Added with a reason), and the build composes pages to
these layouts. A page that is hard to use at this stage stays hard to use after styling and building, and the fix
then costs rounds of human review; getting the flow right here, at low fidelity, is the cheapest place to do it.

## Rules

1. **The BRD sets what is built; you decide how each page works.** Every page in §11 gets a frame, in nav order,
   with the page's own ID; nothing L2, nothing the document does not build. Take its personas (§7), journeys (§8),
   data (§12), agents (§13), seed data (§19), its demo day (§19) and demo storyline (§20.2) as given. Each §11 page
   says what the page must do (the question, the decision, what needs the person, the primary action, filters, exact
   copy and states) and its information and actions table: build the page's brief from them. §23 lists capabilities
   with CMP IDs: decide the UI components that deliver each one (one, several, or one shared), and put its CMP ID on
   their blocks as `cmp`. An older document may still give a "Layout", a blocks table with UI patterns or a §23
   component list: treat those as a starting suggestion, use them where they serve the person, and change them where
   the brief (rule 2) and `references/patterns.md` show a better way. Record every change in the spec's
   `brd_overrides` (what the BRD had, what you did, why); a CMP ID you fold into another component goes there too,
   so nothing is dropped silently. Set `app.search_label` and `app.agent` from the document's own words
   (spec-format.md). **When the app is a module inside a product the client already uses** (the document
   names a host app, a menu path such as "PLM › In market", or a shell to match), keep that product's shell
   and navigation as the document describes them, and design only what is inside the page; changing the
   host's navigation is never an override this skill makes. Each persona's nav badges count that persona's
   own work.
2. **Think before you draw: a brief for every page.** Before any block, write the page's `brief` in the spec: who
   `arrives` and from where; their `job` on this page; the `decision` they make; what they need to see to make it
   (`sees`), including where the numbers come from; what `needs_you` (the person) and what is `done` already by the
   system or others; and the one `next` step. Write it in the user's words. If you cannot fill `decision` and `next`,
   the page has no clear purpose: merge it or raise it as a finding.
3. **Pick the page's pattern and its shape from the work** (`references/patterns.md` part 1): the pattern (`queue`,
   `split`, `focus`, `decision`, `guided`, `board`, `dashboard`, `map`, `feed`) from the brief, then one of its shapes
   from the data and the signature. Do not give two pages the same shape unless they show the same kind of data; when
   several pages are queues, each gets a different shape. The
   rules in patterns.md part 4 apply to every page, and they are checks on what the page does: they are not a layout.
   There is no standard page top. Carry the next step and the work split the way each page needs (patterns.md part
   3): a banner, chips, a decision bar or a step indicator on most pages is the house layout this rule forbids. Use a
   decision bar only where the page ends in one choice, and a step indicator only where the job has ordered steps.
4. **The signature first, drawn as itself; slot the generic.** Every app has one object or interaction no other app
   has (patterns.md part 2). Name it in the spec's `signature` (`name`, `frame`, `why`), draw it with its real block
   (`artefact`, `media`, `graph`, `calendar`, `tree`, `board`, the map, `chat`, `compare`, `decomp`), give it the most
   space on its page and let it shape the pages around it. **When the signature is a thing people already know (a
   product page on a channel, an invoice, a contract, a script page, a boarding pass, a lab report), draw it as that
   thing:** first look up how the real one is laid out and write its parts in order (for an Amazon product page: the
   picture gallery on the left; brand store link, title, price, "About this item" bullets and description on the
   right), then draw it as an `artefact` with its real text from the seed data and the marks on the actual words.
   Grey lines in boxes read as any document from any app; the renderer warns when the signature is drawn that way. On the home, the signature holds the home's own work
where it can (in other domains: a hospital's wards on its floor plan, a legal team's contracts as their first pages, a
lab's samples as wells on their plate; take the form from this app's own object): a list beside it showing the same items again is two ways in to one thing (patterns.md part 4 rule 9). Draw the other
defining parts in detail too: each page's
   hero, the work queue, the decision, the record's main object, the agent's answer; mark them `hero: true`.
   Everything else is a `slot`: an empty dashed region named with its component, `count`, the `variants` it needs, its
   `states` and a one-line `note` on what it must do. A slot never holds a hero and never holds a paragraph of
   content. Give every component
   block its `purpose`, the data it `shows` and what it `does` (spec-format.md), and a hero component its `volume` and
   `primary` action: this is the component's brief, and the design system designs to it.
   **The hero object.** Take the scoping document's §21 "Hero object" (or decide it: the one thing these users care
   about most, the thing they would point at on screen: a product, a store, an invoice, a script page, a permit, a
   site) and write it in the spec's `hero_object`. When it has a picture, people recognise it by eye, so the picture
   goes wherever they pick, check or approve one: `thumb: true` on the signature's rows and the lists that hold it,
   `media` where the pictures themselves are the work. The signature always shows the hero object as itself. If the
   work is visual (shots, posters, products, photos, scans), draw the pictures. The renderer warns when the hero
   object's picture is missing from the signature, the home or most pages.
5. **Low fidelity, on purpose.** Greys only, one font, no brand, no icons beyond what the script draws. Real labels
   and copy in the user's words, never lorem ipsum; numbers from the seed data (§19) where the document gives them.
   Set the spec's `today` from the document's demo day (§19) (and a page's own `today` for a frame later in the story), and make every date, day count
   and count on a frame agree with it and with each other: a tab that says 6 shows 6.
   No "demo", "synthetic", "dummy", "simulate" or placeholder words on screen, in the journey or in a brief (the build reads all three); a record's name comes before its code;
   no styling instructions in notes (looks are the design system's job).
6. **Name components by what they do, once.** Use one name per component across all pages (`approval-queue-table`,
   not three spellings), reuse it wherever the same thing appears, and put the §23 CMP ID of the capability it delivers on its blocks as `cmp` when
   it is that component. A new component is fine when the brief needs it; give it a `purpose`.
7. **The demo story walks through the frames.** Write the spec's `journey`: each step of the §20.2 storyline in the
   user's words and the frame that shows it. Each frame's `next` step leads to the next frame of the journey. When
   the next step belongs to another persona, say how the work reaches them (a message, an assignment, a shared
   link) in that page's `arrives`, or start them from their own page.
8. **Variety is bounded here.** `variants` lists only the forms the pages actually need (a compact card, a horizontal
   bar chart; at most three per component): the design system must design these. It may still show its own style-set
   alternatives within its rule-1 families (at most three per family counting these), never a new component. States:
   the ones §11 names for the block plus the cases from patterns.md part 4 rule 10, always including loading and empty for
   data blocks.
9. **Extra frames only for what changes the layout.** A second frame of a page (`PG-03b`) is for an open panel, a
   drawer, a modal, a later step of a guided page, a different mode of the same map, or a phone layout. Not for every
   state: states go in `states`. An extra frame shows the page after the change, so update every block the change
   touches (counts, statuses, answers), not only the titles. The agent opens as a drawer (one frame shows it) unless it leads a `guided` page; a
   confirm dialog for the one irreversible action is one modal. A window or drawer that holds real controls (a
   settings window, a picker, a dossier) draws them as `blocks` inside the overlay, over its page.
10. **Maps.** A page whose main question is *where* (sites, stores, branches, assets, routes, a radius search) is a
    map page: read `references/map-component.md` and follow it exactly — the map is the page, panels float over it,
    one of four modes (`rings`, `dots`, `arcs`, `radius`), a legend in this screen's own words, and the map block's
    `data` contract (object, lat/lng fields, what colours a site, card fields, route ends or radius). If the records
    have no latitude/longitude in §12, the page is not a map page: raise it as a finding for the AI PM, do not invent
    fields. Never put a map in a card on a dashboard.
11. **References and research.** Before you settle the signature and one other component that carries the app, find
    out how others do the same job: real products, case studies and pattern libraries, through the `research` skill
    (patterns.md part 7). In POC Studio, save each answer to `<workspace>/research/wireframes-<topic>.md`. Fall back to
    the built-in web search and fetch tools if it fails or comes back with no usable example. Then carry on: the research answer is an input to the spec, never the run's last message. Add any reference the person or the BRD gives. List each in the spec's `references` with
    the component it changed, what you take and what you leave, and take only that.
12. **UX rules every page keeps.** One main action per page (the rest secondary). Bulk selection where a list holds
    more than about 20 items at once (`volume`). A confirm frame for the irreversible action. Seven or fewer table
    columns in view; the rest belong in the record. Every action shows its result: the frame after it, or the state
    it leaves. **States tell the truth:** an action the text calls blocked is drawn blocked (`disabled: true`), and
    every count on a frame matches the items it shows. The renderer prints a `check:` line for each one it can see.
13. **Explore the navigation; never assume it.** Before drawing the pages, draw three really different navigation
    shells on the home and choose one with its reason (`nav_options`, spec-format.md). The renderer has six: `left`
    (a labelled left rail), `icons` (a narrow icon rail), `context` (an icon rail plus a panel for the current area:
    saved views, groups, locks, recent records), `topbar` (a light bar with tabs), `band` (a dark band holding the
    logo and destinations, as many brand sites do) and `command` (no rail: destinations as text and a command field
    to go or ask). Choose from the work: how many destinations, how long the sessions are, whether the person moves
    between areas or stays in one, how much width the hero object needs, and how the client's own product and site
    navigate. **The three options come from three families**: a rail (`left`, `icons` or `context`), a bar (`topbar` or
    `band`) and the `command` bar; the renderer warns otherwise. A persona whose work differs may get its own shell
    (page `shell`). The renderer draws the options side by side in `png/NAV-options.png` and the PDF, the chosen one
    framed. The left rail is a choice like any other, never the default.
14. **More than one way to look at the main data.** Each hero list, table, grid or board that holds many items gets
    2 or 3 views (`views`, e.g. wall · table · by lock, or queue · board by owner · timeline), drawn as a switch on its
    title row; `view` marks the one shown. Draw at least one alternative view as its own frame (`alt_view_of` the
    page, with the same items), so the design system and the build see the app's page types, not only its pages.
    **Give every other view a kind** (`{"name": "By lock", "kind": "board", "group_by": "meta"}`; kinds: `table`,
    `board`, `wall`, `list`): the renderer draws each one from the same items in `png/VIEWS.png`, so no listed view is
    left undrawn. A view earns its place by answering a different question (which to do next; which team holds most;
    what locks when), never as decoration.
15. **No filler, nothing generated-looking.** Every title says what the block holds in the person's words ("Ready to
    write · 8, nearest lock first"); never "Overview", "Insights", "Quick actions", "Recent activity", "At a glance",
    "Key metrics" or "Welcome back". No block bigger than its content; no text running out of its box or sitting on
    other text. The renderer checks all three on every frame (it records where every word landed) and prints a
    `check:` line for each.
16. **Draw the payoff.** The demo's best moment is when the signature's decision resolves: the blocked thing clears,
    the number moves, the work goes out. Draw that moment as its own frame and name it in the spec's `payoff_frame`,
    so the design system and the build see the end of the story, not only its problem.
17. **One spec, rendered, never hand-drawn.** Write the spec (format: `references/spec-format.md`; a full example:
    `references/example-spec.json`), then render. Change a layout by changing the spec and re-rendering.

## Steps

1. Read `references/patterns.md`. Then read the scoping document's §7 personas, §8 journeys, §9 conventions
   (navigation, global elements), §11 page specs (all of each), §12 for status tones and the picture, document and
   lat/lng fields, §13 agents, §14 refusal messages, §19 seed data and the demo day, §20.2 demo storyline, §23
   capabilities (or component inventory in an older document), and any glossary or client wording. Note the shell
   (left nav or top bar), the nav items per persona, the hero object and its picture (§21), and what the person must
   see to decide on each page (§11).
2. **Think first.** Name the app's `signature` (rule 4), then research how others handle it and one other defining
   component (rule 11) and settle both. Look at how the client's own product and site navigate, and settle the three
   navigation options (rule 13) and the views of each hero data set (rule 14). For each §11 page, write its `brief`, choose its `pattern`
   and shape (rules 2–3) and how it carries its next step and its work split (patterns.md part 3); write the `journey`
   (rule 7). Note where the BRD's layout or components do not serve the brief and decide what replaces them
   (`brd_overrides`). Only then draw.
3. Write `<workspace>/02b-wireframes/<slug>.wireframe.json`: one page per §11 page in nav order, built on its pattern
   and shape, with a header subtitle saying what the page is for; then the extra frames (rule 9), then one drawer
   frame for the agent and one modal frame for the irreversible action if the document has them.
4. Render (on a Mac, the collateral tools' Python has Pillow; the fonts ship with this skill):
   ```bash
   W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/render.py' | head -1)")"
   source ~/.local/poc-collateral/env.sh 2>/dev/null; R=~/.local/poc-studio/design-register.json; [ -f "$R" ] || R=""; python3 "$W/render.py" "<workspace>/02b-wireframes/<slug>.wireframe.json" "<workspace>/02b-wireframes" ${R:+--register "$R"}
   ```
   `--register` is passed only when the shared design-system register exists at
   `~/.local/poc-studio/design-register.json`; never search the disk for another register file.
   A spec error stops the render with one line per problem: fix the spec and run again. A spec without `signature` is
   a spec from before v4: it renders as it always did, and what it lacks (briefs, patterns, the signature, the
   navigation options, hero object, payoff frame, references, house-layout checks) prints as `warning:` lines instead
   of stopping. A new spec always has a `signature`, so every rule above applies to it. Every `check:` line it prints
   is a tell (patterns.md part 6): fix it, or say in the hand-over why it stays. If Pillow is missing,
   `pip install pillow` (into the collateral venv on a Mac).
5. Check coverage against the scoping document, and fix every gap it lists (a missing page is a gap; a missing CMP ID
   is a gap unless `brd_overrides` names it with its reason; a slot without `cmp` is fine for a shared component):
   ```bash
   W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/render.py' | head -1)")"
   source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 "$W/coverage.py" "<workspace>/02-scoping/scoping-document.docx" "<workspace>/02b-wireframes/wireframe-manifest.json"
   ```
   (Each shell starts fresh, so the first line is repeated. A BRD given as a PDF works too: pass the .pdf.)
6. **Look at every PNG yourself (Read the image) as a first-time user would.** In the first 10 seconds of each frame,
   can you tell what the page is for, what needs you, and what to do next? Is the hero drawn as itself? Does the
   journey read in order from frame to frame? Then the cover test (patterns.md part 2): cover the header and nav of
   each frame; if it could belong to any app, rework it around the signature. Lay all the PNGs side by side: if most
   pages share the same top half, rework them. Then fix overlaps, cut-off text, a frame taller than it needs to be, or
   a region whose purpose is unclear. Re-render until the renderer prints no `check:` line you cannot defend.
6b. **A fresh-eyes review, one round.** Start a separate agent when the session can (otherwise do it yourself as a
   separate pass, before rereading your spec). Give it only the PNGs (frames, `NAV-options.png`, `VIEWS.png`), each
   page's brief and the journey; never the spec or your notes. It answers, frame by frame:
   - **First ten seconds:** what is this page for, what needs the person, what do they do next? Anything it cannot
     answer is a finding.
   - **The signature:** does it look like the real thing its users know, with real text, or like a generic box?
   - **Truth:** does every state, count and date on screen agree with the others and with the brief?
   - **The story:** do the frames read in the journey's order, ending on the payoff?
   - **Craft:** anything sloppy (misaligned, cramped, empty, cut off, a title that says nothing), anything that looks
     generated, anything a person doing this job would miss?
   - **Uniqueness:** could this app's home or signature belong to another client with the logo swapped?

   Fix every finding in the spec, re-render, and list the findings with what you did in the hand-over. One round;
   the AI PM reviews after.
7. Return the PDF, the PNG folder and the manifest paths, the page and component counts, the signature, the hero
   object, the chosen navigation (and the two not chosen) and the alternative views in one line each,
   each page's pattern and shape in one line, the BRD changes from `brd_overrides` in one line each, each reference with what it changed, and any
   `check:` line you kept with its reason.

## What the next stages do with it

- **Design system:** reads the manifest as its component list (its section 0.0): a component page for every manifest
  component with the listed variants, features and states, designed for its `purpose`, `shows` and `does`, the
  `hero` components first; plus its baseline (sign-in, statuses, empty/error/loading, toast, confirm, the agent
  drawer, the next-step banner, steps and chips, the kit atoms), with the `signature` component given the most care. The
  wireframes decide each page's layout, pattern and the journey; the design system decides how each component looks
  and may give a component a richer form when its brief is better served (a list of products as an image grid, a
  timeline with pictures), recording the change. Its full screens keep each frame's layout and pattern.
- **Build:** the frames and manifest go in the build request; each page follows its frame's layout and pattern and
  the design system's styling. Map pages follow `map-component.md` (platform-master adds it as a pointer).
- **AI PM:** reviews this stage (lens `wireframes`) and, at Stage 4b, checks the built pages against the frames.

## Update mode (a change request after the app is built)

Called by the orchestrator's **4c · Changes after the build** (and `asset-run` § 6 for a one-off app) when the AI PM
has triaged a change as **big** or **very big**. Input: the person's words verbatim, the AI PM's change-clarity reading (or the person's answers), the AI PM's
triage (its
`affected_pages`, `new_pages`, `components`), and the approved `02b-wireframes/`. The app is not touched in this step.

1. **Keep the approved version.** Move the current spec, `png/`, PDF and manifest to
   `02b-wireframes/_previous/v<N>/` (`N` = the approved version; never delete it). Copy the spec back as the working
   spec.
2. **Edit only what the change needs.** Change the affected pages' entries in the spec, add new pages (and their
   extra frames, rule 9) in nav order with new page IDs, remove a page only if the person asked. Every rule above still
   holds (a brief and pattern for a new page, low fidelity, slots, one name per component, real copy from the person's
   words or the scoping document). Leave every other page's entry byte for byte as it was. The design system is not
   updated: a new component is added as a slot with a `note` saying it is new in this change, and the build styles it
   from the design system's kit and tokens.
   **A legacy spec** (one without `signature`, written before v4) is updated as a legacy spec: no migration is needed,
   since it renders as before with `warning:` lines. Do not add a signature, briefs or patterns to the whole spec. If
   the person's change itself needs v4 fields (a new page needs its `brief` and `pattern`; a changed page's work
   changed), add them only to the changed or added pages; every other page keeps its entry as it was.
3. **Render and check** as in Steps 4–6, on the changed and added pages only (coverage still runs against the scoping
   document; a page the person added that the document does not have is expected, not a gap). The rework in Steps
   4–6 (fixing `check:` lines, the cover test, the side-by-side sameness pass, the fresh-eyes review) applies only to
   the changed and added pages. `check:` and `warning:` lines about pages outside the change, and the global ones
   (`nav_options`, references, payoff frame, `hero_object`, house layout, the cover test, the fresh-eyes rework), are
   listed in the hand-over but **not fixed**: fixing them would change pages the person did not ask about.
4. **Make the change sheet** (before | after for every page that differs, and the manifest delta):
   ```bash
   W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/render.py' | head -1)")"
   source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 "$W/diff.py" "<workspace>/02b-wireframes/_previous/v<N>" "<workspace>/02b-wireframes" "<workspace>/02b-wireframes/changes/CR-<n>" --request "<the person's words>"
   ```
   Check its list against the triage: every affected page appears, and nothing else does. A page that changed
   without being asked for is undone. The sheet also reports app-level changes (the `app` block and spec-level keys
   such as `today`, `signature`, `nav_options`, `journey`, `payoff_frame`, `hero_object`, `brd_overrides`), the
   `NAV-options` and `VIEWS` sheets when they differ (labelled as sheets, not pages), and pages whose only change is
   their `brief`, `pattern` or `shape` with the same drawing as "metadata only" (no before | after page). An
   app-level change the triage did not ask for is undone like a page. `NO_CHANGES` means the edit did not land: fix
   the spec.
5. Return `changes/CR-<n>/change-sheet.pdf`, `change-summary.json`, the pages added, removed, changed and metadata
   only, the sheets and app-level keys that changed, the components added (not in the design system) in one line
   each, and the `check:` / `warning:` lines left unfixed because they sit outside the change.

## Answering the AI PM

Answer each finding in the response file as `fixed`, `disputed` (with the brief line, the patterns.md rule, the §11
line or the CMP ID behind it) or `deferred`. A fix changes the spec only where the finding points; re-render
everything (it takes a second).
