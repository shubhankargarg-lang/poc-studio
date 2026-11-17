---
name: wireframes
description: Turns the approved scoping document (BRD) into complete, clickable, low-fidelity wireframes in one editable HTML file. Every screen, workflow path and state the BRD supports is drawn with real content, working controls and a stable data-* component-ID contract. The file is the structural and behavioural source of truth for the design system and the UnifyApps Headless (Nebula) build. That HTML is the only output: the person clicks through it at the gate, it goes to Orbit, and the design system and the build read it. Names the app's signature and draws it as itself, picks each page's pattern from its work, and keeps scope to what the BRD justifies, with no filler, invented features or AI slop. Runs in POC Studio's Plan phase between Scoping and the Design System, and for /poc-studio:wireframes.
---

# Wireframes (POC Studio, Plan phase)

**Input:** the approved scoping document (`02-scoping/scoping-document.docx`, or a PDF), the client and the use case.
**Output** in `<workspace>/02b-wireframes/`:

| File | What it is | Who reads it |
|---|---|---|
| `<slug>-wireframes.html` | **The only output.** One self-contained, editable, clickable HTML file: every screen, frame, state and interaction, with the metadata contract below | the person (at the gate and in Orbit), the AI PM, the design system, UnifyApps Headless (Nebula) |
| `_working/wireframe-manifest.json` | internal, generated from the HTML: pages, frames, signature, journey, components with their instances, variants and states | `coverage.py`, the build plan, the AI PM |
| `_working/<slug>.wireframe.json` | internal, generated from the HTML: the page index (a content hash per screen) | the orchestrator's review list |
| `_working/qa/` | internal, review screenshots of every screen and frame, contact sheets and a reading-order overlay per screen | the visual review (step 8) and the fresh-eyes reviewer |

There is no PDF and there are no PNG frames to hand over: the HTML is what everyone opens. The HTML is the only file
you write by hand; the internal files are generated from it by `scripts/wf_tool.py` and never uploaded or shown.
Change a wireframe by editing the HTML and regenerating, never by editing a generated file.

**The tools are files in this skill, never typed by hand.** `scripts/wf_tool.py` (embed, check, manifest, review),
`scripts/coverage.py`, `scripts/diff.py`, and the fixed parts of every wireframe, `assets/wf-base.css` and
`assets/wf-runtime.js`, which `wf_tool.py embed` puts into the HTML. Find the folder once:
```bash
W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/wf_tool.py' 2>/dev/null | head -1)")"
```

**Why this stage exists.** The BRD says what the app must do. The wireframes decide how each screen works: what the
person sees first, what needs them, how they decide, what they do next and what happens after. Getting this right
here is cheap; a screen that is hard to use stays hard to use after styling and building.

**What this skill owns, and what it hands on.** The wireframe owns the application structure, the screen hierarchy,
the component inventory, the content, the business meaning, the interactions, and the component and instance IDs.
The design system owns the brand, the visual language, the tokens, the finished look of each component and its
visual states. It styles and finishes what this file contains, and changes none of its content or behaviour. So
anything the app needs must be here: a component this file leaves out will either be missing or be invented later
without the BRD in view.

| Responsibility | Wireframe skill | Design system skill |
|---|---|---|
| BRD interpretation | primary responsibility | consume and preserve |
| User journeys | define | preserve |
| Business rules | define and validate | preserve |
| Screen and state coverage | define | preserve |
| Content and data | define | preserve |
| Functional interactions | define and validate | preserve and style |
| Component identification | identify | catalogue and trace |
| Component anatomy | basic structural representation | refine and correct |
| Layout composition | functional and logical | visually optimise |
| Typography | minimal hierarchy | the complete type system |
| Colour and brand | minimal, greyscale | full brand treatment |
| Elevation and shadows | not used | applied where they separate surfaces |
| Visual states | functional representation | fully designed states |
| Final visual quality | not its objective | primary responsibility |

So do not polish here. A problem of finish (flat cards, weak hierarchy, a drawer that blends into the page) is the
design system's to solve. A problem of structure is yours: a drawer with no header, its actions loose in the body, a
screen in the wrong reading order, a document drawn as a picture.

**Low fidelity means low visual styling.** Greys, one system font and no brand. It never means incomplete structure,
content or behaviour. Every component on every screen carries real content and every visible control works.

---

## Rules

Rules give their reason where it is not obvious. Where two rules pull in different directions, the order of priority is: the BRD's
scope and wording, then working behaviour, then restraint (rule 12), then everything else.

1. **The BRD sets what is built; you decide how each screen works.** Every page in §11 gets a screen, in nav order,
   with the page's own ID (`PG-03`). Nothing from L2 or future scope. Take the personas (§7), journeys (§8),
   data (§12), agents (§13), workflows and business rules (§14), roles (§16), seed data and demo day (§19), demo
   storyline (§20.2) and hero object (§21) as given. §23 lists capabilities or components with CMP IDs. Deliver each
   one with one or more components and put its CMP ID in their `data-brd-ref`. Where the BRD suggests a layout or a
   UI pattern, use it where it serves the person and change it where the brief (rule 3) and
   `references/patterns.md` show a better way. Record every change in `brd_overrides` (what the BRD had, what you
   did, why). A CMP ID you fold into another component goes there too, so nothing is dropped silently.
   **A page several personas use** is drawn for its primary persona. Each other persona whose view differs (other
   actions, another default tab, read-only) gets a frame with `persona`, and elements only some personas see carry
   `data-for` (rule 13).
   **When the app is a module inside a product the client already uses** (the BRD names a host app or a menu path),
   keep that product's shell and navigation as the BRD describes them and design only what is inside the page.

2. **Map the requirements before you draw.** Read the BRD through and write `requirements` in `wf-meta`: one entry
   per thing the app must show or do. That covers each page's question, decision and primary action, each
   information item, each action and its outcome, each business rule a person meets on screen (a prerequisite, a
   limit, a refusal), each workflow step a person starts or sees, each stated state, and each journey step. Each
   entry has the BRD `ref`, the `need` in plain words, and `covered_by`, the screen, frame or instance IDs that
   deliver it. An entry nothing can cover gets a `status`: `open question`, `out of scope` or `not shown on screen`
   (a background automation). This map is how the run proves complete coverage. It is also how it avoids invention:
   a component that serves no entry has no reason to exist (rule 12).

3. **A brief for every screen before any markup.** In `wf-meta.screens.<id>.brief` write, in the user's words:
   `arrives` (from where, when), `job`, `decision`, `sees` (what they need to see to decide, and where the numbers
   come from), `needs_you`, `done` (what the system or others already did) and the one `next` step. If you cannot
   write `decision` and `next`, the screen has no clear purpose: merge it into another or raise it in
   `open_questions`.
   **Then declare its reading order** in `wf-meta.screens.<id>.reading_order`, as instance IDs: `first` (what the
   person must notice first), `next` (what they need to understand next), `act` (where they decide or act) and
   `support` (what they may need). The shell is not part of it. Compose the screen so placement, grouping, spacing
   and emphasis follow that order: `first` at the top of the content and the most prominent, `act` in the first view,
   `support` after or beside, never above, and never louder. Fix weak hierarchy by moving, grouping and spacing what
   is there; never by adding cards, badges, numbers, labels or decoration. `review` checks the order on the rendered
   screen and draws it on `_working/qa/reading-order-<id>.png`.
   A record's page opens on what the record is: its summary and key facts first (an AI summary where the BRD has an
   agent), then the checks, history or analysis done on it as support. A list opens on what needs the person soonest
   (the next meeting, the oldest overdue item), and a record with several past events shows their overview first.

4. **Pick the screen's pattern and shape from its work.** Use `references/patterns.md` part 1 for the pattern (`queue`,
   `split`, `focus`, `decision`, `guided`, `board`, `dashboard`, `map`, `feed`) and its shapes, part 3 for carrying
   the next step without a house layout, and part 4 for the rules every page keeps. Two screens of one app get the
   same shape only when they show the same kind of data. That reference was written for the earlier JSON spec. Its
   mentions of `slot` and spec fields are replaced by this skill's HTML; its `check:` lines come from `wf_tool.py check`. Its pattern, signature,
   usability and reference guidance all still apply.
   Controls that act on the same object sit together in one region beside or above it, never split between a side and
   the bottom. When settings exist both for all items and for one item, draw them as two separate controls: the
   all-items one applies to every item, the one-item one opens from that item, and its values override the defaults.

5. **The signature first, drawn as itself.** Every app has one object or interaction no other app has (patterns.md
   part 2). Name it in `wf-meta.signature` (`name`, `component`, `frame`, `why`), give it the most space on its
   screen and on the home, and draw it as the real thing its users know. For a known artefact (an invoice, a
   contract, a product page, a boarding pass, a lab report), look up how the real one is laid out and draw its parts
   in that order, with real text from the seed data. Take the hero object from §21 (`hero_object`: `name`,
   `picture`, `judged_by_eye`). When it has a photograph, show a picture area (`.wf-img` with a caption saying what
   the photo shows) wherever the person picks, checks or approves one.
   **A document is drawn as the document.** When the BRD names a known document (an invoice, a lab report, a purchase
   order, a receipt, a delivery note, a contract), draw a simplified but recognisable version of it as a
   `document` component in `.wf-doc`: title and reference, parties and dates (`dl`, `.doc-parties`), line items or
   measurements (`table`, numbers in `.num`), totals or key findings (`.doc-totals`, `.grand`), and status or approval
   (`.doc-stamp`). Use only the fields the BRD and seed data support. A scanned page takes `.wf-scan`; a value that
   is hard to read takes `.doc-faint`. A document is never a grey box with a caption: `check` rejects one.

6. **Every component is complete.** Each component shows realistic, relevant content that makes clear what it
   represents, why it exists, what information it presents, what the person can do with it, and what happens after
   they act. A table has its real columns and 4 to 8 real rows from the seed data. A form has its real fields,
   values, validation and submit result. A chart has its title stating the takeaway, axes with units and the real
   values. A queue shows its items in order. An AI answer shows the real answer, its sources and its stated
   confidence. An empty dashed box, a box naming a component, a count such as "×6", a list of variants or a
   technical note in place of content is never acceptable. A stakeholder must understand every screen without
   knowing any implementation term.

7. **Language the person would use.** Titles say what the block holds ("Rooms waiting for your check · 4"). Button
   labels are a verb and an object ("Release room"). Error messages say what happened and how to fix it. Use the
   BRD's exact copy wherever it gives one, and list those strings in `wf-meta.exact_copy`. Use one term per concept
   everywhere, in the client's words from the glossary. Keep sentences to 25 words at most. Use no internal codes,
   IDs, rule numbers, field names, tool names or file names on screen; a record's name comes before its own ID. Use
   no "demo", "synthetic", "sample", "dummy" or placeholder words on screen, in the journey or in a brief. When a
   real name contains one of those words, add it to `allow_words` and give the reason in the hand-over. When the
   BRD itself names a user-facing control with one of them (a "Demo tools" menu, say), keep its function, give it a
   neutral name, and record the rename in `brd_overrides`.

8. **Facts from the BRD, sample data marked.** Names, numbers, dates and statuses come from the seed plan (§19) where
   it gives them. Where you must illustrate beyond it (a fifth row, a time stamp, a second name), wrap the invented
   value in `<span data-sample>`. Reviewers can show these marks with the review bar; the design system and the
   build ignore them, and they never appear as visible labels. **Never copy a real client sample** (anything in
   `01-requirement-gathering/files/samples/`: real invoices, emails, names, account numbers) into the wireframe: the
   file is uploaded to Orbit as a public link. Draw the same kind of document with invented values in the same shape. Set `wf-meta.today` from the demo day, and make every
   date, day count and count agree with it and with each other: a tab that says 6 shows 6 items.

9. **Every path and state the BRD supports.** For each workflow the person meets, draw the main path, the
   alternate paths the BRD names (send back, reject with reason, re-shoot, edit then confirm), and the result of
   each action. For each data component, draw the states it needs as `data-states` with real wording, using the
   BRD's exact wording where §11 gives it: loading, empty (first use), filtered to nothing (a different fact from
   empty, with its own wording and action), error with how to recover, success, slow AI, and no permission. Add
   "unset" for a field from a journey the person has not done yet. A disabled action is drawn disabled with its
   reason visible beside it, in the BRD's helper text. Only draw a state the BRD, the workflow or the data actually
   produces.

10. **Every visible control works.** Links, tabs, filters, row clicks, buttons, form submits, drawers, modals,
    toasts and the agent all do what they say, through `data-interaction` (`assets/wf-runtime.js`) or a link to a screen. A
    control whose real effect is outside the prototype (send an email, export a file) shows the result state the
    person would see ("Report sent to 3 attendees"). A control that does nothing is a defect.

11. **Navigation and the agent, chosen on purpose.** Decide the shell from the work: how many destinations, how
    long the sessions are, whether people move between areas or stay in one, and how much width the hero object
    needs. Consider three really different shells from three families: a rail (labelled left rail, icon rail, rail
    plus context panel), a bar (light tab bar, dark band), and a command bar. Draw each small on the review sheet
    `#NAV-options`, choose one with its reason (`nav_options`, one `chosen: true`), and build every screen in the
    chosen shell. Keep to seven destinations or fewer per persona. A persona whose work differs may get its own
    shell. Give the agent exactly one way in for the whole app, recorded as `data-agent-entry` on `<html>`:
    `topbar` (a button in the bar), `launcher` (one floating button, for a shell with no bar or a phone) or
    `command` (the command field asks it). The agent opens as a drawer, except on a `guided` screen it leads.

12. **Restraint: every element serves a stated need.** An element with no entry in `requirements` and no line in
    the screen's brief is removed. Quality does not come from the number of elements. These numbers are limits; go
    under them when the work allows:
    - one primary (filled) action per screen and at most two other visible actions beside it, with the rest in a
      menu (a drawer or modal has its own primary);
    - at most four key facts in a card or record header, with the rest behind "Details" or in a tab;
    - at most six headline numbers in a view, each with its comparison and time frame. A row of number tiles opens
      only a `dashboard` screen, never a screen where the person acts;
    - status colour only on exceptions, with one status word per row;
    - one AI marker per panel ("Checked by AI", "Suggested"), never an AI badge on every block;
    - no card inside a card; no section that repeats what another already shows; no chart where a sorted table or
      one sentence answers the question;
    - helper text only where it changes what the person does;
    - search and filters only on the screen whose list they narrow, never repeated on a record's own page;
    - extra screens only for what changes the layout (rule 13). States are not screens.
    Set the size budget before you write markup: screens (= §11 pages), frames (rule 13), components (one per
    distinct job). Say in the hand-over where the BRD forced you over a limit.

13. **Frames only for what changes the layout.** A frame is a named state of a screen, declared in `wf-meta.frames`
    and opened by URL hash (`#PG-02b`). Make one only for a real change in layout or composition (an open drawer or
    modal, a different map mode, the payoff), a persona's own view of a shared page (`persona`), a structurally
    different state, a workflow step that needs its own view (a later step of a guided screen), a phone layout for a
    persona who uses two devices (`width`), or an alternative view the BRD asks for. Filters, tabs, sorting and other
    controls that change content in place work in place: a frame per filter choice is noise, and `check` flags it.
    Draw the story's main record fully; another record the journey visits gets its own frame only when its decision
    looks different, not because its numbers do. Each journey step points at the
    screen or frame that shows it. `payoff_frame` is the frame where the signature's decision resolves: the blocked thing clears, the number moves, the work goes out.
    Name three key screens in `key_screens` for the design system to draw at high fidelity: `home` (the primary
    persona's start screen, with the signature), `main` (the screen where the primary persona does the job the demo
    storyline centres on) and `agent` (a frame of `main` with the agent drawer open; if the BRD has no agent, the
    frame of `main` that opens its main drawer or modal). `home` and `main` are two different screens unless the app
    has only one: when the start screen is also where the work happens, `main` is the screen the storyline's main
    decision moves to (often the signature's own page). `check` fails `home` equal to `main`, and flags a `home` where
    the signature is not visible: when the start screen opens empty (a chat before its first answer), point `home` at
    the frame where the signature shows.

14. **Views only when the BRD supports them.** A switch between views (table, board, calendar) is added only when
    the BRD names more than one way to see the data, or a persona's stated job needs two orderings of the same items.
    Record the reason in the component's registry entry (`views`). It never appears as decoration.

15. **Maps.** A screen whose main question is *where* (sites, stores, assets with coordinates) is a map screen: read
    `references/map-component.md` and follow it. The map fills the screen, panels float over it, it has one of four
    modes, and its legend is in this screen's own words. Draw it at low fidelity as a grey area with positioned
    markers and labels. Put the mode, data contract and any behaviour lines in the map component's registry entry
    (`modes`, `data_contract`, `behaviour`). If the records have no latitude and longitude in §12, it is not a map
    screen: raise it in `open_questions` and do not invent fields.

16. **Research the signature, briefly.** Before you settle the signature and one other component that carries the
    app, find out how leading products do the same job: real products first, then pattern libraries (Mobbin, Page
    Flows), then case studies. Use the `research` skill with a Quick budget (3 to 5 searches, stop at two or three
    good examples), as patterns.md part 7 describes, and save each answer to
    `<workspace>/research/wireframes-<topic>.md`. If `research` is missing or fails, use web search and fetch to the
    same budget. Take layout moves and interactions, never artwork or text. List two to four references in
    `wf-meta.references` with what you took and left. Research never stops the run. Before any search or site visit,
    check `<workspace>/research/` for an earlier answer to the same question and reuse it; search only for what it
    leaves open.

17. **Ask, do not invent.** When the BRD is silent, contradictory or ambiguous on something the screen needs (who
    approves, what happens on failure, which field is shown), write an `open_questions` entry with the BRD ref, the
    question and the assumption you drew, and mark the affected content `data-sample` where it is invented. Do not
    add a feature, a field or a rule to fill the gap. The orchestrator's reviewer resolves open questions in an
    unattended run.

---

## The metadata contract (shared with the design-system skill)

The wireframe HTML carries machine-readable metadata that never shows in the interface. The design system and the
build read it, so its names and meanings are fixed. Change them only with a version change to both skills.

### On elements

| Attribute | Where | Meaning |
|---|---|---|
| `data-screen-id` | each `<section class="wf-screen">` | the BRD page ID (`PG-03`); unique |
| `data-screen-title`, `data-persona`, `data-width`, `data-pattern`, `data-brd-ref` | the same section | page name, primary persona ID (`U2`), device width (1280 desktop, 375 phone), pattern, BRD section |
| `data-component-id` | each component instance's root element | the reusable component's ID, kebab-case, named by what it does (`inspection-queue-table`); the same ID wherever the same component appears |
| `data-instance-id` | the same element | `<screen-id>.<component-id>`, with `-2`, `-3` for repeats on one screen (`PG-01.room-card-3`); unique in the file |
| `data-component-type` | the same element | one of: `nav`, `header`, `tabs`, `filter-bar`, `table`, `list`, `card`, `record-header`, `form`, `chart`, `metric`, `board`, `calendar`, `timeline`, `stepper`, `media`, `document`, `map`, `chat`, `ai-answer`, `diff`, `tree`, `graph`, `compare`, `upload`, `rating`, `drawer`, `modal`, `toast`, `banner`, `menu`, `popover`, `empty-state` |
| `data-variant` | the same element, when the component has variants | the variant's name, declared in the registry |
| `data-state`, `data-states` | the same element | the initial state, and every state it can show (`default loading empty error`). Overlays use `closed open` |
| `data-when` | a child of an instance | the state(s) in which this child shows; children without it always show |
| `data-brd-ref` | every instance | BRD references it delivers, separated by spaces: page, CMP, feature, workflow, rule IDs (`PG-02 CMP-03 HK-005 WF-01`) |
| `data-interaction` | a control | what happens when it is used (`assets/wf-runtime.js`). An instance it names is resolved only inside the control's own screen, never on another screen; `~name` means `<this screen>.name`, so a shell or menu repeated on every screen can carry the same markup |
| `data-atom`, `data-variant` | buttons, links styled as buttons, inputs, selects, toggles, checkboxes, radios, tags, avatars | the atom kind and its variant (`button` + `primary`, `secondary`, `tertiary`; `tag` + `positive`, `attention`, `negative`, `neutral`). Atoms have no instance ID |
| `data-sample` | an inline element | an illustrative value the BRD did not give (rule 8) |
| `data-for` | any element inside a screen | the persona IDs who see it (`U2 U4`); others do not. Never on the same element as `data-when` |
| `data-icon` | an atom | the icon the control needs, by meaning (`search`, `close`, `camera`). Low fidelity draws no icon; the design system draws it here and nowhere else |
| `data-logo` | the element holding the client or app name in the shell | where the design system places the logo |
| `data-wf-chrome` | review bar, notes, review sheets | scaffolding, never part of the app |

**Components, instances and variants.** A component is a reusable thing with one job (a room card, the inspection
queue table, the report-issue drawer). Every place it appears is an instance with its own instance ID and the same
component ID. Different content never makes a new component or a new variant. A variant exists only when the
structure, behaviour or purpose differs (a compact card that drops the photo; a read-only table with no row actions).
Declare each variant in the registry with what differs. A table owns its rows; cards repeated in a list are
instances.

### `wf-meta` (one JSON block in `<head>`)

```json
{
  "app": {"name": "Room Ready", "shell": "topbar", "agent": "Ask Room Ready"},
  "client": "…", "use_case": "…", "slug": "client-app", "today": "14 Nov", "start": "PG-01",
  "signature": {"name": "…", "component": "room-photo-check", "frame": "PG-02", "why": "…"},
  "hero_object": {"name": "room", "picture": "the four photos of the finished room", "judged_by_eye": ["…"]},
  "nav_options": [{"name": "…", "shell": "left|icons|context|topbar|band|command", "why": "…", "chosen": true}],
  "journey": [{"step": "what the person does, in their words", "frame": "PG-01"}],
  "payoff_frame": "PG-02c", "key_screens": {"home": "PG-01", "main": "PG-02", "agent": "PG-02e"},
  "frames": [{"id": "PG-02b", "of": "PG-02", "title": "Room · report issue open", "set": {"PG-02.report-issue-drawer": "open"}},
             {"id": "PG-02s", "of": "PG-02", "title": "Room · supervisor view", "persona": "U2", "set": {"PG-02.room-tabs": "ai-check"}},
             {"id": "PG-04m", "of": "PG-04", "title": "Ready rooms · phone", "width": 375},
             {"id": "PG-02r", "of": "PG-02", "title": "Room · Arabic layout", "dir": "rtl"}],
  "screens": {"PG-01": {"shape": "…", "brief": {"arrives": "…", "job": "…", "decision": "…", "sees": "…", "needs_you": "…", "done": "…", "next": "…"},
              "reading_order": {"first": ["PG-01.queue-summary"], "next": ["PG-01.invoice-queue-table"], "act": ["PG-01.page-header"], "support": ["PG-01.activity-feed"]}}},
  "requirements": [{"ref": "PG-02 Actions", "need": "supervisor releases with a reason", "covered_by": ["PG-02.release-form", "PG-02d"]}],
  "components": {"room-photo-check": {"name": "Room photo check", "type": "media", "purpose": "…", "shows": ["…"],
      "does": ["…"], "volume": "4 photos", "primary": "Submit for check", "hero": true, "signature": true,
      "variants": {"compact": "drops the result line; used in the queue preview"}, "media": {"ratio": "4:3", "where": "grid"},
      "views": [], "modes": [], "data_contract": {}, "behaviour": []}},
  "brd_overrides": [{"brd": "…", "change": "…", "why": "…"}],
  "references": [{"source": "…", "url": "…", "for": "<component>", "take": ["…"], "leave": ["…"]}],
  "open_questions": [{"id": "Q1", "brd_ref": "…", "question": "…", "assumption": "…"}],
  "assumptions": ["…"], "exact_copy": ["…"], "allow_words": []
}
```

`screens.<id>.reading_order` is `{"first": [ids], "next": [ids], "act": [ids], "support": [ids]}` (support optional).
`frames[].set` gives each instance's state in the frame. Set `frames[].width` only for a phone or desktop layout of the
same screen, `frames[].dir` only for a right-to-left frame, and `frames[].persona` only for another persona's view.

---

## Building the file

One HTML file. Its parts, in order:

```html
<!DOCTYPE html>
<html lang="en" dir="ltr" data-wf-version="1" data-slug="<slug>" data-shell="<chosen shell>" data-agent-entry="topbar">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title><App> — wireframes</title>
  <style id="wf-base"></style>   <!-- filled by `wf_tool.py embed` from assets/wf-base.css; never typed -->
  <style id="wf-app">/* this app's own layout rules only: grids, widths, order. No colour, border, shadow or font */</style>
  <script type="application/json" id="wf-meta">{ … }</script>
</head>
<body>
  <nav class="wf-review" data-wf-chrome aria-label="Wireframe review"></nav>
  <main class="wf-stage">
    <section class="wf-screen" data-screen-id="PG-01" data-screen-title="My Rooms" data-persona="U1" data-width="375"
             data-pattern="queue" data-brd-ref="§11 PG-01" hidden>
      <div class="wf-device" style="--w:375px;--h:812px"> … the whole screen: shell, content, its overlays … </div>
    </section>
    …
  </main>
  <section id="NAV-options" data-wf-chrome hidden> … the three shells, small, with their reasons … </section>
  <aside class="wf-notes" data-wf-chrome hidden></aside>
  <script id="wf-runtime"></script>   <!-- filled by `wf_tool.py embed` from assets/wf-runtime.js; never typed -->
</body>
</html>
```

The runtime builds the review bar (screen and frame picker, a state picker for every instance with more than one
state, the annotation toggle and the notes) from the metadata, so you write none of it.

**Authoring patterns:**
- **Each screen is whole.** It carries its own shell instance (`PG-02.app-nav`), its content and its overlays, all
  inside its `.wf-device`, so it exports and copies on its own.
- **Tabs:** a `tabs` instance whose `data-state` is the open tab and whose `data-states` lists the tabs. Each tab
  button has `role="tab" data-tab="photos" data-interaction="state:PG-02.room-tabs=photos"`, and each panel has
  `data-when="photos"`. Filters and segmented switches work the same way.
- **Overlays** (`drawer`, `modal`, `toast`, `menu`): inside the device, `data-state="closed" data-states="closed
  open" hidden`. Give each drawer and modal its basic anatomy: a `<header>` (the title, its context line and the close
  button, `data-icon="close"`), its content, and a `<footer>` after the content holding its actions. When the
  overlay's content changes by state (`data-when` blocks), each block keeps that order. `check` fails a drawer or
  modal with no header and flags a close control or primary action outside its region. On a map screen the drawer
  opens below the top bar, so the bar stays visible (`map-component.md`).
  Draw each drawer's content for its own job: a create or edit drawer is a form (labelled inputs, toggles, tabs only
  where the BRD splits the fields, Save and Cancel in the footer); only the agent drawer is a chat. Never reuse one
  overlay's markup for another job.
  Use a modal only for an irreversible or legally significant act; use a drawer for work attached to the current
  record.
- **Disabled with a reason:** `<button … disabled aria-describedby="why-release">Release room</button>
  <p id="why-release" class="wf-help">Room is blocked by ticket 0412</p>`.
- **Forms** validate with `required` and show their `invalid` state with the error text in the BRD's words. The
  submit button runs `submit; …` so an invalid form stops there.
- **Pictures (photographs only):** `<div class="wf-img" style="--ratio:4/3">Shower and bath · taken 09:12</div>`. The
  caption says what the photo shows.
- **Documents:** `<article class="wf-doc" data-component-type="document" …><header><div><h3>Invoice</h3><p>MBG-26-04471
  · 13 Nov 2026</p></div><p class="doc-stamp">Blocked</p></header><div class="doc-parties"><dl>…supplier…</dl><dl>…buyer,
  PO…</dl></div><table>…lines, with <td class="num">…</table><div class="doc-totals"><div><span>Net</span><span>EUR
  31,350.00</span></div><div class="grand">…</div></div></article>`. The part class names are shared with the design
  system, which styles the same parts.
- **Right to left:** when the BRD needs Arabic, Hebrew or Urdu, add one frame of the main screen with `"dir": "rtl"`
  to show the mirrored layout. Use translated text where the BRD gives it; list the rest for translation in
  `open_questions`.
- **Phone screens:** at 375 px, in one column, with the shell's phone form and the primary action within thumb reach.

`wf-app` holds layout only because the design system carries it into its styled screens unchanged. Name the classes
it defines `l-…` (`l-queue-col`, `l-band`): the design system's kit has its own short names (`opt`, `legend`, `tile`,
`band`), and an unprefixed class of yours would pick up the kit's styling. `check` lists any class outside the `wf-`,
`l-` and `doc-` names. Keep the HTML
maintainable: semantic elements (`header`, `nav`, `main`, `section`, `table`, `form`, `label`,
`button`), no external files, fonts or scripts, and no inline styles beyond `--w`, `--h` and `--ratio`.

---

## Steps

1. **Read.** `references/patterns.md`. If `<workspace>/02b-wireframes/_working/notes.md` is missing or older than the
   scoping document, turn the document into text once and write into that notes file what this step lists (exact copy,
   field names and numbers word for word); then take the document's facts only from the notes, reopening the document
   only to check one missing fact. Read, from the notes, the whole BRD: §7 personas and devices, §8 journeys, §9 conventions,
   §10 features (L1 only), §11 page specs (each in full: question, decision, primary action, filters, exact copy,
   states, prerequisites and helper text, actions and what happens), §12 data and statuses, §13 agents, §14
   workflows and business rules, §16 roles, §17 AI trust rules, §19 seed data and demo day, §20.2 demo storyline,
   §21 hero object and reference products, §23 capabilities, and the glossary. Also read a map page's
   `references/map-component.md`.
2. **Map the requirements** (rule 2) and write the open questions (rule 17).
3. **Think before markup.** Name the signature and research it (rules 5, 16). Settle the navigation options and the
   agent's one entry (rule 11). Write each screen's brief, pattern and shape (rules 3, 4) and the journey and payoff
   (rule 13). Set the size budget (rule 12). Write the component registry: one entry per distinct job, with its
   purpose, what it shows and does, its states and any genuine variants.
4. **Write the HTML** (Building the file): the screens in nav order, then their frames, the `#NAV-options` sheet, and
   `wf-meta` complete, with empty `wf-base` and `wf-runtime` tags. Then put the fixed parts in (find `W` as above):
   ```bash
   H="<workspace>/02b-wireframes/<slug>-wireframes.html"; python3 -I "$W/wf_tool.py" embed "$H"
   ```
5. **Check and fix until clean:**
   ```bash
   source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 -I "$W/wf_tool.py" check "$H"
   ```
   Fix every `error:` line. Fix each `check:` line, or say in the hand-over why it stays.
6. **Generate the internal manifest and check coverage:**
   ```bash
   python3 -I "$W/wf_tool.py" manifest "$H" "<workspace>/02b-wireframes/_working"
   python3 "$W/coverage.py" "<workspace>/02-scoping/scoping-document.docx" "<workspace>/02b-wireframes/_working/wireframe-manifest.json"
   ```
   Every §11 page needs a screen, and every CMP ID needs an instance or a `brd_overrides` entry with its reason.
7. **Review screenshots** (see "Review screenshots"): `python3 -I "$W/wf_tool.py" review "$H" "<workspace>/02b-wireframes/_working/qa"`.
   It captures every screen and frame, a contact sheet and a reading-order overlay per screen, for your review only.
   Fix every `check:` line about reading order, overlapping text, overflow or script errors.
8. **The visual acceptance gate.** Automated checks are necessary and not enough. Do this full pass once, at the end;
   after a later fix, look only at the screens and frames that changed. Open the HTML in a browser if the
   session has one, click through the journey from the first step to the payoff, and try every control on the way.
   Then go through every contact sheet and every reading-order overlay in `_working/qa/`, and open any screen or
   frame that looks wrong at full size. Review every screen, every meaningful frame, every component and its
   important states, the reading order, each document, layout consistency across screens, overflow and clipping, BRD
   coverage, and anything invented or unnecessary. For each screen, ask:
   - Can you tell within ten seconds what it is for, what needs you and what to do next?
   - Does every component say what it is, why it exists, what it shows, what you can do and what happens after?
   - Is there anything the BRD does not ask for, anything said twice, anything a person in this job would miss?
   - Cover test: cover the header and nav. Could this screen belong to any app? If so, rework it around the
     signature.
   - Lay all frames side by side: if most screens share the same top half, rework them.
   - Does the overlay's numbered order match where the eye actually goes? If not, move and group; do not decorate.
   - Is each document recognisable as that document?
   Never write that every screen was reviewed when only some were; the hand-over says what you looked at.
9. **Fresh-eyes review, one round.** Start a separate agent when the session can. While it works, end the turn and
   wait for Claude Code's finished notice, with no status checks; if `$CLAUDE_PROJECT_DIR/.poc-studio/autopilot`
   exists, create `waiting` beside it when you hand the job over and remove it when the reply arrives. Give it only the HTML, the review
   screenshots and contact sheets, each screen's brief, the journey and the requirement map, never your notes or
   check output. If no independent agent can run, say so in the hand-over and mark the review outstanding; never
   write up a review that did not happen. It answers screen by screen: first ten seconds; is the signature the real
   thing; do every state, count and date agree; does the story read in order to the payoff; does every line pass the two-second test (rule 36); does every headline
   number follow from the hero records (rule 30); anything sloppy,
   generated-looking, invented or missing; could this app belong to another client with the logo swapped; does any
   title or sentence pass the swap test (Slop rules, rule 4); does every screen and block trace to a BRD need. Fix
   every finding in the HTML, re-run steps 5 to 7 (looking only at the screens that changed), and list the findings
   with what you did in the hand-over.
10. **Hand-over.** Return the HTML's path (the only output), any "Optional next steps" (ideas beyond the BRD, not
    drawn), the screen, frame and component counts, the signature, the hero object, the chosen navigation with the
    two not chosen, each screen's pattern and shape in one line each, the `brd_overrides` and `open_questions` in one
    line each, the references with what each changed, how the review screenshots were taken, and any `check:` line
    kept with its reason.

---

## Review screenshots

The screenshots in `_working/qa/` exist only for the visual review; nothing downstream reads them, and the HTML is
complete without them. `review` needs a browser. Check, in this order:

1. `python3 -I -c "import playwright"` succeeds. On a Mac, POC Studio's shared tools provide it after
   `source ~/.local/poc-collateral/env.sh`. `review` then uses Playwright's Chromium, or else any Chromium or Chrome
   already installed. Never download a second browser when one exists.
2. Without Python Playwright, `review` drives an installed Chrome or Chromium from the command line. Each frame is
   then cut at the window height, the `NAV-options` sheet is not drawn, and neither the reading order nor overlapping
   text is measured, so check both by eye; `review` prints these as `check:` lines.
3. With neither, `review` says so and stops without error. Review every screen by eye in the browser instead (open
   the HTML and use the review bar's screen and frame picker), and say at the top of the hand-over that no
   screenshots could be taken. Never skip the stage for this.

The internal manifest keeps the field names the stages that read it use (`pages`, `components[].component`, `type`,
`blocks`, `cmp`, `variants`, `features`, `states`, `purpose`, `shows`, `does`, `hero`, `media`, `views`, `modes`,
`data_contract`, `signature`, `journey`, `brd_overrides`, `nav_options`, `shell`, `payoff_frame`), plus `format`,
`frames`, `components[].instances`, `variant_defs`, `atoms`, `agent_entry`, `open_questions` and `assumptions`.
`blocks` holds `<screen-id>/<instance-id>`.

---

## Slop rules (the team's "Dos and don'ts to reduce AI slop")

Slop is output that looks finished but is generic, padded, invented or hard to read. These rules come from the team's
"Dos and don'ts to reduce AI slop" (14 Nov 2026), and most of them are already inside the rules above; this list is
the whole set as it applies to wireframes, so nothing is left to memory. Apply them while you draw and write each screen; the shared writing rules (`<skill-base-dir>/../../references/anti-slop.md`) apply to every line too. Each has a number so it can be checked, and
`check` tests every one it can see; the word lists live in `check`, not here.

**Content**
1. Every screen, block and chart traces to a need in the BRD (`requirements`); cut what does not.
2. Build only what was asked. An extra idea goes in the hand-over under "Optional next steps", never on a screen.
3. Facts, names and numbers come from the BRD; an invented value is marked `data-sample` (rule 8 above).
4. The swap test: put another company's name in any title or sentence; if it still makes sense, rewrite it.
5. One term per concept, in the client's words, everywhere, and one concept per term: never one word for two things
   ("High" for volume and for urgency).
6. No trace of how the file was made on screen: no tool names, file names, paths, run IDs, scores or error codes; no
   internal agent names (the assistant keeps the one name set in `app.agent`), model names, confidence on rule-based
   checks or arithmetic, or system words such as "indexing", "knowledge set" and "last read".

**Writing** (the reader understands over 90% of a 14-word sentence and under 10% of a 43-word one)
7. Sentences average 15 to 20 words, 25 at most. One dash aside per paragraph at most; no chains of "·", ";" or arrows.
8. Each screen, block and message starts with its main point. Use everyday words, the active voice, and concrete
   numbers ("from 3 days to 4 hours") in place of praise words.
9. Codes and IDs go in tables and record headers, after the name, never in running text.
10. Calm and factual: no exclamation marks, slogans, "not just X, it's Y", openers that restate the question, closers
    like "Let me know", or hedges like "may potentially". State an uncertainty once, specifically.
11. A list is as long as the facts: two, four or seven items, never three by habit.

**Headings**
12. Every title names what its block holds or its outcome, in the reader's words; never "Overview" or "Chart 1".
13. A subtitle only when it says what the screen is for (never the sort order or the date); no line repeats across
    screens.

**Screens**
14. One job and one primary button per screen, and at most two other visible actions in its header; the rest go in a
    menu.
15. The home opens on the person's next task and shows the signature; never on a strip of number tiles.
16. At most four key facts on a card or record header; the rest behind "Details". At most eight numbers on one card.
17. Navigation has seven items or fewer; tabs only where there is enough content to split.
18. No card inside a card; sections of one card are its own headings and dividers.
19. Colour (tags) marks the exceptions: never the same tag on every row, never tags in three or more columns.
20. Real, varied data from the client's domain: no repeated dummy value down a column, no placeholder names.
21. Every view has its empty, loading and error states where the data can produce them (rule 9 above).
22. Buttons say a verb and an object; error messages say what happened and how to fix it; rules are explained in
    words ("within the 30% discount limit").
23. One way into the assistant; AI output shows as "AI" once per panel, with no sparkle on every block and no agent or
    model name under each answer. A decision the AI made on its own keeps its one-line reason.
24. No emoji anywhere; every icon has its word beside it (Close and More may carry theirs as `aria-label`).

**Charts and numbers**
25. Pick the chart for the question: a line for a trend, a sorted bar to compare, a table for exact values; no pie
    with more than five slices, never two pies to compare.
26. At most six metrics per screen, each with its comparison (target or last period) and its time frame.
27. At most four series per chart; axes labelled with units, lines labelled directly, bars starting at zero.
28. Round to the precision the decision needs (two or three significant figures); one format per unit.
29. A short note says the source or time frame of a chart or headline number only when neither is already visible on
    the screen, and at most once per panel.

**Story, states and clarity**
30. Every headline number and payoff claim agrees with the hero records' states, values and times. If the story needs
    a condition the data does not have, raise it in `open_questions`.
31. Times on a record run in order, and a state comes after the events that cause it. The same count means the same
    thing everywhere: a header that says 4 matches a filter that says 4.
32. Every action is allowed only in the states the BRD's lifecycle names; in any other state it is disabled with its
    reason.
33. Each option on a decision has a different visible result; two options with the same result are merged or dropped.
    A status never contradicts an open exception.
34. No dead ends: draw the path after a wrong AI answer, the edit and remove actions, and what happens next after a
    hand-off, or list each as an open question.
35. Each fact appears once per screen. A summary links to its list instead of repeating its figures; it may keep one
    headline number that links to the list.
36. The two-second test: every label, badge and count makes sense without the BRD. A badge says what it counts
    ("2 need attention"), every number has its unit, and each filter has its own title.
37. Detail goes only to the role that acts on it: check IDs and score maths go to the supervisor, never the
    housekeeper.
38. The presenter tools (persona switcher and reset) live only in the review bar (`data-wf-chrome`), never in the user
    menu or the app bar.
39. Dates, times and spelling follow the BRD's locale (§19); a time from another zone shows that zone.

**When rules conflict:** the BRD's facts and exact copy first, with one exception: a label must describe what is
counted. Keep the client's own name when it means what is counted; otherwise rename it, record it in `brd_overrides`
and raise it in `open_questions`. Then these rules, then completeness. Never add a
screen, block or word to look thorough. A clean `check` is not proof of quality: generic content in clean words is
still slop, which is why the fresh-eyes review asks the swap test (rule 4) and whether every screen traces to the BRD
(rule 1).

## Validation (all must pass before hand-over)

| Area | Pass when |
|---|---|
| Requirement coverage | every `requirements` entry is covered or has a status; `coverage.py` reports no missing page or CMP ID |
| Screens and workflows | every §11 page has a screen; every journey step has a screen or frame; every action shows its result; every alternate path the BRD names is drawn |
| Component completeness | no instance without content; no placeholder, component name or count shown in place of content; every hero table has real rows |
| Content quality | the BRD's exact copy where it gives one; one term per concept; no internal codes or placeholder words on screen; sample data marked |
| Slop rules | every rule in "Slop rules" holds; each `check:` line from them is fixed or defended in the hand-over |
| Interactions | `check` reports no control that does nothing and no interaction pointing at nothing; you clicked through the journey |
| States | every data component has the states its data produces, with real wording; disabled actions show their reason |
| Data consistency | one `today`; counts match the items shown; the same record has the same values on every screen |
| Responsive | each screen works at its persona's width with no sideways scroll; a persona with two devices has the second layout as a frame |
| HTML integrity | `check` reports no errors; the file opens with no script error (`review` reports any) |
| Metadata | unique screen and instance IDs; every instance's component is in the registry; every registry entry is used; variants declared; states consistent; `key_screens` set, with `home` and `main` different screens; the app's own classes named `l-…` |
| Overlay anatomy | every drawer and modal has a header with its title and close control, its content, and a footer with its actions |
| Rendered text | `review` reports no text overlapping other text (map labels on markers, labels under a floating panel) |
| Reading order | every screen declares `first`, `next` and `act`; `review` reports no reading-order check; the overlays match where the eye goes |
| Documents | every known document is a `.wf-doc` with its real parts; no document drawn as a picture |
| Frames | each frame changes layout, a persona's view, a structural state or a workflow step; no frame per filter or tab choice |
| Restraint | the rule 12 limits hold or the hand-over says why; the cover test and the side-by-side test pass |
| Visual review | you clicked through the journey and went through every contact sheet and overlay (or every screen by eye when no browser could take screenshots); fresh-eyes findings are fixed, or the review is reported outstanding |

---

## What the next stages do with it

- **Design system:** takes exactly two inputs, the BRD and this HTML. It catalogues every component and atom found
  here, keeps every component ID, instance ID, variant and state, finishes and styles them, and draws the three
  `key_screens` at high fidelity with their content unchanged. It may complete a component's visual anatomy (wrap a
  drawer's body and footer, draw Close as an icon button) and records each correction. It adds no content or
  behaviour. A gap it finds comes back as a wireframe change.
- **Build (UnifyApps Headless):** composes each page from its screen here (regions, order and content), styled by the
  design system. It builds the chosen navigation shell only, the agent from its one entry, maps per
  `map-component.md`, and every state and interaction drawn here.
- **AI PM:** reviews this stage and later checks the built pages against these screens.

---

## Update mode (a change request after the app is built)

Called by the orchestrator's **4c · Changes after the build** (and `asset-run` § 6) when the AI PM has triaged a
change as **big** or **very big**. Input: the person's words verbatim, the AI PM's change-clarity reading, its triage
(`affected_pages`, `new_pages`, `components`), and the approved `02b-wireframes/`. The app is not touched in this
step.

1. **Keep the approved version.** Copy the current HTML to `02b-wireframes/_previous/v<N>/` and keep working on the
   HTML in place. Never delete a previous version. If the approved wireframes have no HTML (made before wireframes
   were HTML), convert them first ("Legacy wireframes" below) and keep the converted copy as `_previous/v<N>/`.
2. **Edit only what the change needs.** Change the affected screens; add new screens (with briefs, frames and
   requirement entries) in nav order with new page IDs; remove a screen only if the person asked. Keep every
   unchanged screen's markup byte for byte. Keep existing component and instance IDs: a changed component keeps its
   ID, and a new one gets a new ID with a registry `notes` line saying it is new in this change. The design system
   is not re-run; the build styles a new component from the design system's kit and tokens.
3. **Embed, check, generate and review** (steps 4 to 7), and review only the changed and added screens (steps 8 and 9).
   List `check:` lines about other screens in the hand-over, without fixing them.
4. **Make the change sheet:**
   ```bash
   source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 -I "$W/diff.py" "<workspace>/02b-wireframes/_previous/v<N>" "<workspace>/02b-wireframes" "<workspace>/02b-wireframes/changes/CR-<n>" --request "<the person's words>"
   ```
   Check its list against the triage: every affected page appears and nothing else does. Undo any unrequested
   change. `NO_CHANGES` means the edit did not land.
   The change sheet is one clickable HTML page: each changed screen before and after, side by side.
5. **Return** `changes/CR-<n>/change-sheet.html`, `change-summary.json`, the screens added, removed and changed, the
   components added in one line each, and the `check:` lines left unfixed because they sit outside the change.

## Answering the AI PM

Answer each finding as `fixed`, `disputed` (with the brief line, the requirement entry, the patterns.md rule, the §11
line or the CMP ID behind it) or `deferred`. A fix changes the HTML only where the finding points. Then re-run
`check`, `manifest` and `review`, and look only at the screens that changed.

**On any failed command** (a tool, a download, a search), read the error, fix the cause and retry once; then take
another route or note it in the hand-over.

## Legacy wireframes (made before wireframes were HTML)

A POC whose wireframes were approved as PNG frames and a PDF (`02b-wireframes/<slug>.wireframe.json`, `png/`,
`<slug>-wireframes.pdf`, `wireframe-manifest.json`, no `*-wireframes.html`) is converted once, when the design system
is about to run or a change request needs Update mode:
1. Read the approved spec (its fields are explained in `references/legacy-spec-format.md`), every PNG frame, the
   manifest and the BRD.
2. Draw the **same** wireframes as HTML (Building the file): the same screens, page IDs, component IDs, frames,
   navigation, signature, journey and content. Fill what the old frames left as empty slots with real content from
   the BRD, mark invented values `data-sample`, and change nothing else: this is a format change, not a redesign.
3. Run steps 4 to 7. Keep the old files in `02b-wireframes/_legacy/` (never delete them).
4. Hand over as "the approved wireframes, now clickable; nothing changed". The orchestrator shows it at a short gate.

---

## The fixed parts (files in this skill)

- `assets/wf-base.css`: the low-fidelity stylesheet (greys, one system font, no brand). Put into every wireframe by
  `wf_tool.py embed`; never edited per app (the app's own layout rules go in `wf-app`).
- `assets/wf-runtime.js`: screens, frames, states, interactions and the review bar. Put in by `wf_tool.py embed`;
  never edited per app. `data-interaction` is a list of steps separated by `;`, run in order:

  | Step | Does |
  |---|---|
  | `go:<screen or frame id>` | opens that screen or frame |
  | `back` | goes back |
  | `open:<instance>` / `close:<instance>` / `toggle:<instance>` | an overlay's state (`close` alone closes the overlay the control is in) |
  | `state:<instance>=<state>` | sets any instance's state (tabs, filters, results, loading) |
  | `wait:<ms>` | pauses, for a loading or checking state before its result |
  | `toast:<instance>` | shows a toast for four seconds |
  | `submit` | stops the steps if the surrounding form is invalid |

  Example: `submit; state:~room-check=checking; wait:1200; state:~room-check=pass; toast:~status-toast`. Every
  instance a step names is resolved only inside the control's own screen; there is no document-wide fallback, so an
  action on one screen can never change another screen. If the target is not on that screen, the interaction stops
  at that step, changes nothing, and reports `wf: missing target "<id>" on screen <screen>` in the console, in
  `window.wfErrors` and on `<html data-wf-error>`; `check` reports the same as an error before the file is opened.
  `~name` lets a component repeated on every screen (the shell, the user menu, the agent drawer) carry identical
  markup. Frames set states only on their own screen, checked the same way. Escape closes the open overlay, and
  opening a drawer or modal moves focus into it.
- `scripts/wf_tool.py`: `embed`, `check`, `manifest`, `review`. `check` holds the word lists for placeholder,
  filler and generic-title tells and the slop checks, so this file does not repeat them.
