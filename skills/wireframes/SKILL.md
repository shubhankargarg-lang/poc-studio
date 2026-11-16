---
name: wireframes
description: Turns the approved scoping document (BRD) into complete, clickable, low-fidelity wireframes in one editable HTML file. Every screen, workflow path and state the BRD supports is drawn with real content, working controls and a stable data-* component-ID contract. The file is the structural and behavioural source of truth for the design system and the UnifyApps Headless (Nebula) build. The skill also writes the wireframe manifest, and PNG frames plus a PDF for the stages that still read them. Names the app's signature and draws it as itself, picks each page's pattern from its work, and keeps scope to what the BRD justifies, with no filler, invented features or AI slop. Runs in POC Studio's Plan phase between Scoping and the Design System, and for /poc-studio:wireframes.
---

# Wireframes (POC Studio, Plan phase)

**Input:** the approved scoping document (`02-scoping/scoping-document.docx`, or a PDF), the client and the use case.
**Output** in `<workspace>/02b-wireframes/`:

| File | What it is | Who reads it |
|---|---|---|
| `<slug>-wireframes.html` | **The deliverable.** One self-contained, editable, clickable HTML file: every screen, frame, state and interaction, with the metadata contract below | the person, the AI PM, the design system, UnifyApps Headless (Nebula) |
| `wireframe-manifest.json` | generated from the HTML: pages, frames, signature, journey, components with their instances, variants and states | the design system, the build, `coverage.py`, the AI PM |
| `<slug>.wireframe.json` | generated from the HTML: the page index (pages, frames, app-level keys, a content hash per page) | `diff.py` in Update mode, the orchestrator's review list |
| `png/<id>.png` | one image per screen and per frame, at the persona's width | the build's layout check, the AI PM, change sheets |
| `<slug>-wireframes.pdf` | all frames in nav order | the person at the gate, Orbit |
| `_qa/` | contact sheets of every screen and frame, and a reading-order overlay per screen | the visual review (step 8); nothing downstream reads it |

The HTML is the only file you write by hand. Everything else is generated from it by `wf_tool.py` (Appendix C).
Change a wireframe by editing the HTML and regenerating, never by editing a generated file.

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
   is there; never by adding cards, badges, numbers, labels or decoration. `export` checks the order on the rendered
   screen and draws it on `_qa/reading-order-<id>.png`.

4. **Pick the screen's pattern and shape from its work.** Use `references/patterns.md` part 1 for the pattern (`queue`,
   `split`, `focus`, `decision`, `guided`, `board`, `dashboard`, `map`, `feed`) and its shapes, part 3 for carrying
   the next step without a house layout, and part 4 for the rules every page keeps. Two screens of one app get the
   same shape only when they show the same kind of data. That reference was written for the earlier renderer. Its
   mentions of `slot`, spec fields and `render.py` `check:` lines are replaced by this skill. Its pattern, signature,
   usability and reference guidance all still apply.

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
   build ignore them, and they never appear as visible labels. Set `wf-meta.today` from the demo day, and make every
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
    toasts and the agent all do what they say, through `data-interaction` (Appendix B) or a link to a screen. A
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
    `wf-meta.references` with what you took and left. Research never stops the run.

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
| `data-interaction` | a control | what happens when it is used (Appendix B). An instance it names is resolved only inside the control's own screen, never on another screen; `~name` means `<this screen>.name`, so a shell or menu repeated on every screen can carry the same markup |
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
  <style id="wf-base">/* Appendix A, verbatim */</style>
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
  <script id="wf-runtime">/* Appendix B, verbatim */</script>
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

1. **Read.** `references/patterns.md`, then the whole BRD: §7 personas and devices, §8 journeys, §9 conventions,
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
   `wf-meta` complete. Write the tool from Appendix C to `<workspace>/02b-wireframes/_working/wf_tool.py`.
5. **Check and fix until clean:**
   ```bash
   source ~/.local/poc-collateral/env.sh 2>/dev/null; T="<workspace>/02b-wireframes/_working/wf_tool.py"; H="<workspace>/02b-wireframes/<slug>-wireframes.html"
   python3 -I "$T" check "$H"
   ```
   Fix every `error:` line. Fix each `check:` line, or say in the hand-over why it stays.
6. **Generate and check coverage:**
   ```bash
   source ~/.local/poc-collateral/env.sh 2>/dev/null; T="<workspace>/02b-wireframes/_working/wf_tool.py"; H="<workspace>/02b-wireframes/<slug>-wireframes.html"
   python3 -I "$T" manifest "$H" "<workspace>/02b-wireframes"
   W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/coverage.py' | head -1)")"
   python3 "$W/coverage.py" "<workspace>/02-scoping/scoping-document.docx" "<workspace>/02b-wireframes/wireframe-manifest.json"
   ```
   Every §11 page needs a screen, and every CMP ID needs an instance or a `brd_overrides` entry with its reason.
7. **Export the frames** (see Exports): `python3 -I "$T" export "$H" "<workspace>/02b-wireframes"`. Besides the PNGs and
   PDF it writes `_qa/`: labelled contact sheets of every screen and frame, and a reading-order overlay per screen.
   Fix every `check:` line about reading order, overflow or script errors.
8. **The visual acceptance gate.** Automated checks are necessary and not enough. Open the HTML in a browser if the
   session has one, click through the journey from the first step to the payoff, and try every control on the way.
   Then go through every contact sheet and every reading-order overlay, and open any screen or frame that looks wrong
   at full size. Review every screen, every meaningful frame, every component and its important states, the reading
   order, each document, layout consistency across screens, overflow and clipping, BRD coverage, and anything
   invented or unnecessary. For each screen, ask:
   - Can you tell within ten seconds what it is for, what needs you and what to do next?
   - Does every component say what it is, why it exists, what it shows, what you can do and what happens after?
   - Is there anything the BRD does not ask for, anything said twice, anything a person in this job would miss?
   - Cover test: cover the header and nav. Could this screen belong to any app? If so, rework it around the
     signature.
   - Lay all frames side by side: if most screens share the same top half, rework them.
   - Does the overlay's numbered order match where the eye actually goes? If not, move and group; do not decorate.
   - Is each document recognisable as that document?
   Never write that every screen was reviewed when only some were; the hand-over says what you looked at.
9. **Fresh-eyes review, one round.** Start a separate agent when the session can. Give it only the PNGs, the contact
   sheets, each screen's brief, the journey and the requirement map, never your notes, source or check output. If no
   independent agent can run, say so in the hand-over and mark the review outstanding; never write up a review that
   did not happen. It answers frame by frame: first ten seconds; is the signature the real
   thing; do every state, count and date agree; does the story read in order to the payoff; anything sloppy,
   generated-looking, invented or missing; could this app belong to another client with the logo swapped; does any
   title or sentence pass the swap test (Slop rules, rule 4); does every screen and block trace to a BRD need. Fix
   every finding in the HTML, re-run steps 5 to 7, and list the findings with what you did in the hand-over.
10. **Hand-over.** Return the paths, any "Optional next steps" (ideas beyond the BRD, not drawn), the screen, frame and component counts, the signature, the hero object, the
    chosen navigation with the two not chosen, each screen's pattern and shape in one line each, the
    `brd_overrides` and `open_questions` in one line each, the references with what each changed, the export
    method used, and any `check:` line kept with its reason.

---

## Exports and compatibility

The PNGs and the PDF are secondary exports kept for the stages that read them: the orchestrator's gate and Orbit
upload (the PDF), the build's layout check and the AI PM (the PNGs), and Update mode's change sheet (`diff.py`
compares PNGs). `export` needs a browser. Do not assume one is available. Check, in this order:

1. `python3 -I -c "import playwright"` succeeds. On a Mac, POC Studio's shared tools provide it after
   `source ~/.local/poc-collateral/env.sh`. `export` then uses Playwright's Chromium, or else any Chromium or Chrome
   already installed. Never download a second browser when one exists.
2. Without Python Playwright, `export` drives an installed Chrome or Chromium from the command line. Each frame is
   then cut at the window height, the `NAV-options` sheet is not drawn, and neither the reading order nor overlapping
   text is measured, so check both by eye; `export` prints these as `check:` lines.
3. With neither, `export` stops with `export: unavailable`. Then:
   - Do not skip the stage or hand over silently. The HTML, the manifest and the page index are complete and are
     what the design system needs.
   - On a Mac, run the `poc-collateral-setup` install (it installs Playwright and its Chromium), or
     `python3 -m pip install playwright` when Chrome is already installed, and run `export` again.
   - If that is not possible in the session, say so at the top of the hand-over: "No browser was available, so
     there are no PNG frames or PDF. The gate and Orbit upload, the build's frame comparison and Update mode's
     change sheet need them. Run `export` once a browser is installed." The person can still open the HTML.

The manifest keeps the field names the earlier JSON renderer used (`pages`, `components[].component`, `type`,
`pages`, `blocks`, `cmp`, `variants`, `features`, `states`, `purpose`, `shows`, `does`, `hero`, `media`, `views`,
`modes`, `data_contract`, `signature`, `journey`, `brd_overrides`, `nav_options`, `shell`, `payoff_frame`), so
`coverage.py`, `diff.py` and the stages that read the manifest keep working. It adds `format`, `frames`,
`components[].instances`, `variant_defs`, `atoms`, `agent_entry`, `open_questions` and `assumptions`. `blocks` now
holds `<screen-id>/<instance-id>`.

---

## Slop rules (the team's "Dos and don'ts to reduce AI slop")

Slop is output that looks finished but is generic, padded, invented or hard to read. These rules come from the team's
"Dos and don'ts to reduce AI slop" (14 Nov 2026), and most of them are already inside the rules above; this list is
the whole set as it applies to wireframes, so nothing is left to memory. Each has a number so it can be checked, and
`check` tests every one it can see; the word lists live in `check`, not here.

**Content**
1. Every screen, block and chart traces to a need in the BRD (`requirements`); cut what does not.
2. Build only what was asked. An extra idea goes in the hand-over under "Optional next steps", never on a screen.
3. Facts, names and numbers come from the BRD; an invented value is marked `data-sample` (rule 8 above).
4. The swap test: put another company's name in any title or sentence; if it still makes sense, rewrite it.
5. One term per concept, in the client's words, everywhere.
6. No trace of how the file was made on screen: no tool names, file names, paths, run IDs, scores or error codes.

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
13. Each screen has its own subtitle; no line repeats across screens.

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
23. One way into the assistant; AI output is marked once per panel, never with a sparkle on every block.
24. No emoji anywhere; every icon has its word beside it (Close and More may carry theirs as `aria-label`).

**Charts and numbers**
25. Pick the chart for the question: a line for a trend, a sorted bar to compare, a table for exact values; no pie
    with more than five slices, never two pies to compare.
26. At most six metrics per screen, each with its comparison (target or last period) and its time frame.
27. At most four series per chart; axes labelled with units, lines labelled directly, bars starting at zero.
28. Round to the precision the decision needs (two or three significant figures); one format per unit.
29. A short note under every chart and headline number says its source or time frame ("From the 11 Nov scan").

**When rules conflict:** the BRD's facts and exact copy first, then these rules, then completeness. Never add a
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
| HTML integrity | `check` reports no errors; the file opens with no script error (export reports any) |
| Metadata | unique screen and instance IDs; every instance's component is in the registry; every registry entry is used; variants declared; states consistent; `key_screens` set, with `home` and `main` different screens; the app's own classes named `l-…` |
| Overlay anatomy | every drawer and modal has a header with its title and close control, its content, and a footer with its actions |
| Rendered text | `export` reports no text overlapping other text (map labels on markers, labels under a floating panel) |
| Reading order | every screen declares `first`, `next` and `act`; `export` reports no reading-order check; the overlays match where the eye goes |
| Documents | every known document is a `.wf-doc` with its real parts; no document drawn as a picture |
| Frames | each frame changes layout, a persona's view, a structural state or a workflow step; no frame per filter or tab choice |
| Restraint | the rule 12 limits hold or the hand-over says why; the cover test and the side-by-side test pass |
| Visual review | you went through every contact sheet and overlay; fresh-eyes findings are fixed, or the review is reported outstanding |

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

1. **Keep the approved version.** Move the current HTML, page index, `png/`, PDF and manifest to
   `02b-wireframes/_previous/v<N>/` and copy the HTML back as the working file. Never delete a previous version.
2. **Edit only what the change needs.** Change the affected screens; add new screens (with briefs, frames and
   requirement entries) in nav order with new page IDs; remove a screen only if the person asked. Keep every
   unchanged screen's markup byte for byte. Keep existing component and instance IDs: a changed component keeps its
   ID, and a new one gets a new ID with a registry `notes` line saying it is new in this change. The design system
   is not re-run; the build styles a new component from the design system's kit and tokens.
   **A legacy wireframe** (a `<slug>.wireframe.json` spec with no HTML, made before this version) is updated with
   the skill version that made it. Do not convert it unless the person asks.
3. **Check, generate and export** (steps 5 to 7), and review only the changed and added screens (steps 8 and 9).
   List `check:` lines about other screens in the hand-over, without fixing them.
4. **Make the change sheet:**
   ```bash
   W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/diff.py' | head -1)")"
   source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 "$W/diff.py" "<workspace>/02b-wireframes/_previous/v<N>" "<workspace>/02b-wireframes" "<workspace>/02b-wireframes/changes/CR-<n>" --request "<the person's words>"
   ```
   Check its list against the triage: every affected page appears and nothing else does. Undo any unrequested
   change. `NO_CHANGES` means the edit did not land.
5. **Return** `changes/CR-<n>/change-sheet.pdf`, `change-summary.json`, the screens added, removed and changed, the
   components added in one line each, and the `check:` lines left unfixed because they sit outside the change.

## Answering the AI PM

Answer each finding as `fixed`, `disputed` (with the brief line, the requirement entry, the patterns.md rule, the §11
line or the CMP ID behind it) or `deferred`. A fix changes the HTML only where the finding points. Then re-run
`check`, `manifest` and `export`.

---

## Appendix A · `wf-base` stylesheet (paste verbatim)

```css
/* wf-base v1 — low fidelity: greys, one system font, no brand, no decoration. Structure and content only. */
*{box-sizing:border-box}
html{font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#1f1f1f;background:#e9e9e7}
body{margin:0}
[hidden]{display:none!important}
h1,h2,h3,h4,p{margin:0}
h1{font-size:22px;font-weight:600}h2{font-size:17px;font-weight:600}h3{font-size:15px;font-weight:600}
small,.wf-muted{color:#666;font-size:13px}
button,input,select,textarea{font:inherit;color:inherit}
:focus-visible{outline:2px solid #1f1f1f;outline-offset:2px}
/* review chrome (never part of the app) */
.wf-review{position:sticky;top:0;z-index:50;display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:8px 14px;background:#2b2b2b;color:#f2f2f2;font-size:13px}
.wf-review select,.wf-review button{background:#444;color:#f2f2f2;border:1px solid #666;border-radius:4px;padding:3px 8px}
.wf-notes{max-width:880px;margin:14px auto;padding:14px 18px;background:#fff;border:1px solid #bbb;font-size:13px}
.wf-stage{padding:24px;display:flex;justify-content:center}
html.wf-export .wf-stage{padding:0;display:block}
html.wf-export [data-wf-chrome]{display:none!important}
/* the device frame: one per screen, at the persona's width */
.wf-device{width:var(--w,1280px);min-height:var(--h,800px);background:#fff;position:relative;overflow:hidden;border:1px solid #c8c8c8;container-type:inline-size}
html.wf-export .wf-device{border:0}
/* layout primitives (names say what they do, not how they look) */
.wf-app{display:grid;grid-template-columns:auto 1fr;min-height:inherit}
.wf-app.wf-top-shell{grid-template-columns:1fr;grid-template-rows:auto 1fr}
.wf-nav{background:#f1f1f0;border-right:1px solid #d6d6d6;padding:14px 10px;display:flex;flex-direction:column;gap:4px;min-width:200px}
.wf-top-shell>.wf-nav{flex-direction:row;align-items:center;border-right:0;border-bottom:1px solid #d6d6d6;min-width:0;padding:10px 16px;gap:8px}
.wf-nav a{display:block;padding:7px 10px;border-radius:4px;color:#333;text-decoration:none}
.wf-nav a[aria-current="page"]{background:#d9d9d7;font-weight:600;color:#111}
.wf-main{padding:20px 24px;display:flex;flex-direction:column;gap:16px;min-width:0}
.wf-row{display:flex;gap:16px;flex-wrap:wrap}
.wf-row>*{flex:1 1 260px;min-width:0}
.wf-stack{display:flex;flex-direction:column;gap:10px}
.wf-inline{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.wf-split{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:16px}
.wf-card{border:1px solid #cfcfcf;border-radius:6px;padding:14px 16px;background:#fff;display:flex;flex-direction:column;gap:8px}
.wf-header{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
/* atoms */
.wf-btn{border:1px solid #8a8a8a;background:#fff;border-radius:4px;padding:7px 14px;cursor:pointer}
.wf-btn[data-variant="primary"]{background:#3a3a3a;border-color:#3a3a3a;color:#fff}
.wf-btn[data-variant="tertiary"]{border-color:transparent;text-decoration:underline}
.wf-btn:disabled,.wf-btn[aria-disabled="true"]{background:#eee;border-color:#ccc;color:#8c8c8c;cursor:not-allowed}
.wf-link{color:#1f1f1f;text-decoration:underline;cursor:pointer;background:none;border:0;padding:0}
.wf-tag{display:inline-block;border:1px solid #9a9a9a;border-radius:999px;padding:1px 9px;font-size:12px}
.wf-tag[data-variant="attention"],.wf-tag[data-variant="negative"]{border-width:2px;font-weight:600}
.wf-field{display:flex;flex-direction:column;gap:4px}
.wf-field label{font-size:13px;font-weight:600}
.wf-field input,.wf-field select,.wf-field textarea{border:1px solid #9a9a9a;border-radius:4px;padding:7px 9px;background:#fff}
.wf-field [aria-invalid="true"]{border-width:2px}
.wf-help{font-size:13px;color:#555}
.wf-error{font-size:13px;font-weight:600}
.wf-table{width:100%;border-collapse:collapse}
.wf-table th{text-align:left;font-size:12px;font-weight:600;color:#555;border-bottom:1px solid #bdbdbd;padding:7px 8px}
.wf-table td{border-bottom:1px solid #e1e1e1;padding:8px;vertical-align:top}
.wf-tabs{display:flex;gap:2px;border-bottom:1px solid #cfcfcf}
.wf-tabs button{border:0;background:none;padding:8px 12px;cursor:pointer;border-bottom:2px solid transparent}
.wf-tabs button[aria-selected="true"]{border-bottom-color:#1f1f1f;font-weight:600}
/* documents (invoice, lab report, purchase order…): drawn as the document, never as a picture */
.wf-doc{background:#fff;border:1px solid #9a9a9a;box-shadow:0 1px 3px rgba(0,0,0,.14);padding:20px 24px;display:flex;flex-direction:column;gap:12px;font-size:13px;max-width:var(--doc-w,640px)}
.wf-doc header{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.wf-doc h3{font-size:16px} .wf-doc dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:2px 10px} .wf-doc dt{color:#555} .wf-doc dd{margin:0}
.wf-doc .doc-parties{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.wf-doc table{width:100%;border-collapse:collapse} .wf-doc th{text-align:left;font-size:11px;color:#555;border-bottom:1px solid #9a9a9a;padding:4px 6px} .wf-doc td{border-bottom:1px solid #e1e1e1;padding:5px 6px}
.wf-doc .doc-totals{align-self:flex-end;min-width:240px} .wf-doc .doc-totals div{display:flex;justify-content:space-between;gap:24px} .wf-doc .doc-totals .grand{font-weight:600;border-top:2px solid #3a3a3a;padding-top:4px}
.wf-doc .doc-stamp{align-self:flex-start;border:2px solid #3a3a3a;padding:1px 8px;font-weight:600;font-size:12px;letter-spacing:.04em}
.wf-doc.wf-scan{background:#f7f6f1} .wf-doc .doc-faint{color:#9a9a9a}
.num{text-align:right;font-variant-numeric:tabular-nums}
/* pictures (photographs only): a grey box that says what the photo shows */
.wf-img{background:#dcdcdc;color:#4a4a4a;display:flex;align-items:flex-end;padding:8px;font-size:12px;aspect-ratio:var(--ratio,4/3);border-radius:4px}
/* overlays live inside the device so exports show them */
.wf-scrim{position:absolute;inset:0;background:rgba(0,0,0,.28);z-index:20}
.wf-drawer{position:absolute;top:0;right:0;bottom:0;width:min(420px,100%);background:#fff;border-left:1px solid #9a9a9a;z-index:21;display:flex;flex-direction:column;gap:12px;padding:16px;overflow:auto}
.wf-modal{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(480px,92%);background:#fff;border:1px solid #6f6f6f;z-index:22;padding:18px;display:flex;flex-direction:column;gap:12px}
.wf-toast{position:absolute;left:50%;bottom:20px;transform:translateX(-50%);background:#3a3a3a;color:#fff;padding:9px 14px;border-radius:6px;z-index:23;display:flex;gap:12px;align-items:center}
.wf-toast .wf-link{color:#fff}
/* review annotations, off by default */
html.wf-annot [data-sample]{text-decoration:underline dotted 2px}
html.wf-annot [data-instance-id]{outline:1px dashed #9c9c9c;outline-offset:2px}
@container (max-width:700px){.wf-split{grid-template-columns:1fr}.wf-app{grid-template-columns:1fr}.wf-nav{flex-direction:row;overflow-x:auto;min-width:0;border-right:0;border-bottom:1px solid #d6d6d6}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
```

## Appendix B · `wf-runtime` (paste verbatim)

`data-interaction` is a list of steps separated by `;`, run in order:

| Step | Does |
|---|---|
| `go:<screen or frame id>` | opens that screen or frame |
| `back` | goes back |
| `open:<instance>` / `close:<instance>` / `toggle:<instance>` | an overlay's state (`close` alone closes the overlay the control is in) |
| `state:<instance>=<state>` | sets any instance's state (tabs, filters, results, loading) |
| `wait:<ms>` | pauses, for a loading or checking state before its result |
| `toast:<instance>` | shows a toast for four seconds |
| `submit` | stops the steps if the surrounding form is invalid |

Example: `submit; state:~room-check=checking; wait:1200; state:~room-check=pass; toast:~status-toast`. Every instance a
step names is resolved only inside the control's own screen; there is no document-wide fallback, so an action on one
screen can never change another screen. If the target is not on that screen, the interaction stops at that step,
changes nothing, and reports `wf: missing target "<id>" on screen <screen>` in the console, in `window.wfErrors` and
on `<html data-wf-error>`; `check` reports the same as an error before the file is ever opened. `~name` lets a
component repeated on every screen (the shell, the user menu, the agent drawer) carry identical markup. Frames set
states only on their own screen, checked the same way.
Escape closes the open overlay, and opening a drawer or modal moves focus into it.

```js
/* wf-runtime v1 — screens, frames, states and interactions for a wireframe. Paste verbatim; do not edit per app. */
(() => {
  const d = document, root = d.documentElement;
  const meta = JSON.parse(d.getElementById('wf-meta').textContent);
  const $$ = (s, r = d) => [...r.querySelectorAll(s)];
  const OVERLAY = ['drawer', 'modal', 'toast', 'menu', 'popover'];
  // an instance resolves ONLY inside the control's own screen; '~name' means '<this screen>.name'. No document-wide fallback.
  const current = () => d.querySelector('.wf-screen:not([hidden])');
  const full = (id, scope) => id.startsWith('~') ? `${scope ? scope.dataset.screenId : ''}.${id.slice(1)}` : id;
  const inst = (id, scope) => scope ? scope.querySelector(`[data-instance-id="${CSS.escape(full(id, scope))}"]`) : null;
  function missing(id, scope, step) {   // fail safely: report, change nothing, stop the interaction
    const msg = `wf: missing target "${full(id, scope)}" on screen ${scope ? scope.dataset.screenId : '(none)'}${step ? ` in "${step}"` : ''}`;
    console.error(msg); (window.wfErrors = window.wfErrors || []).push(msg); root.dataset.wfError = msg;
  }
  const own = (el, c) => c.parentElement && c.parentElement.closest('[data-instance-id]') === el;
  function paint(el) {
    const st = el.dataset.state || 'default';
    if (OVERLAY.includes(el.dataset.componentType)) el.hidden = st === 'closed';
    $$('[data-when]', el).forEach(c => { if (own(el, c)) c.hidden = !c.dataset.when.split(/\s+/).includes(st); });
    $$('[role="tab"][data-tab]', el).forEach(t => { if (own(el, t)) t.setAttribute('aria-selected', String(t.dataset.tab === st)); });
  }
  function setState(id, st, scope) {
    const el = inst(id, scope);
    if (!el) { missing(id, scope); return false; }
    el.dataset.state = st; paint(el);
    if (OVERLAY.includes(el.dataset.componentType) && st === 'open' && el.dataset.componentType !== 'toast') {
      const f = el.querySelector('button,a[href],input,select,textarea,[tabindex]'); if (f) f.focus();
    }
  }
  $$('[data-instance-id]').forEach(el => { el.dataset.initial = el.dataset.state || 'default'; el.dataset.state = el.dataset.initial; });
  function show(id) {
    const fr = (meta.frames || []).find(f => f.id === id);
    const sid = fr ? fr.of : id;
    const screens = $$('.wf-screen');
    const sc = screens.find(s => s.dataset.screenId === sid) || screens[0];
    screens.forEach(s => { s.hidden = s !== sc; });
    $$('[data-instance-id]', sc).forEach(el => { el.dataset.state = el.dataset.initial; paint(el); });
    const dev = sc.querySelector('.wf-device'); if (dev) { if (!dev.dataset.w) dev.dataset.w = getComputedStyle(dev).getPropertyValue('--w'); dev.style.setProperty('--w', fr && fr.width ? fr.width + 'px' : dev.dataset.w); if (fr && fr.dir) dev.setAttribute('dir', fr.dir); else dev.removeAttribute('dir'); }
    if (fr) Object.entries(fr.set || {}).forEach(([k, v]) => setState(k, v, sc));
    const who = (fr && fr.persona) || sc.dataset.persona;
    $$('[data-for]', sc).forEach(e => { e.hidden = !e.dataset.for.split(/\s+/).includes(who); });
    root.dataset.persona = who;
    root.dataset.current = fr ? fr.id : sc.dataset.screenId;
    chrome(); scrollTo(0, 0); root.dataset.ready = '1';
  }
  async function run(spec, src) {
    const sc = src.closest('.wf-screen') || current(), S = (id, st) => setState(id, st, sc), I = id => inst(id, sc);
    for (const step of spec.split(';').map(s => s.trim()).filter(Boolean)) {
      const i = step.indexOf(':'), verb = i < 0 ? step : step.slice(0, i), arg = i < 0 ? '' : step.slice(i + 1).trim();
      const [k, v] = arg.split('=').map(s => s && s.trim());
      const target = verb === 'state' ? k : arg;
      if (['open', 'close', 'toggle', 'state', 'toast'].includes(verb) && target && !I(target)) { missing(target, sc, step); return; }
      if (verb === 'go') location.hash = arg;
      else if (verb === 'back') history.back();
      else if (verb === 'open') S(arg, 'open');
      else if (verb === 'close') S(arg || src.closest('[data-instance-id]').dataset.instanceId, 'closed');
      else if (verb === 'toggle') S(arg, I(arg) && I(arg).dataset.state === 'open' ? 'closed' : 'open');
      else if (verb === 'state') S(k, v);
      else if (verb === 'wait') await new Promise(r => setTimeout(r, +arg || 600));
      else if (verb === 'toast') { S(arg, 'open'); setTimeout(() => S(arg, 'closed'), 4000); }
      else if (verb === 'submit') { const f = src.closest('form'); if (f && !f.checkValidity()) { f.reportValidity(); return; } }
      else console.warn('wf: unknown step', step);
    }
  }
  d.addEventListener('click', e => {
    const t = e.target.closest('[data-interaction]');
    if (!t || t.disabled || t.getAttribute('aria-disabled') === 'true') return;
    e.preventDefault(); run(t.dataset.interaction, t);
  });
  d.addEventListener('submit', e => e.preventDefault());
  d.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    const open = $$('.wf-screen:not([hidden]) [data-instance-id][data-state="open"]').filter(el => OVERLAY.includes(el.dataset.componentType)).pop();
    if (open) setState(open.dataset.instanceId, 'closed', current());
  });
  function chrome() {
    const bar = d.querySelector('.wf-review'); if (!bar || root.classList.contains('wf-export')) return;
    const cur = root.dataset.current, sc = d.querySelector('.wf-screen:not([hidden])');
    const opts = $$('.wf-screen').map(s => [s.dataset.screenId, `${s.dataset.screenId} · ${s.dataset.screenTitle}`])
      .concat((meta.frames || []).map(f => [f.id, `${f.id} · ${f.title}`]));
    const states = $$('[data-instance-id][data-states]', sc).filter(el => el.dataset.states.trim().includes(' '));
    bar.innerHTML = `<strong>${meta.app.name} · wireframes</strong>
      <label>Screen <select id="wf-go">${opts.map(([v, t]) => `<option value="${v}"${v === cur ? ' selected' : ''}>${t}</option>`).join('')}</select></label>
      ${states.length ? `<label>State <select id="wf-st"><option value="">Component state…</option>${states.flatMap(el => el.dataset.states.split(/\s+/).map(s => `<option value="${el.dataset.instanceId}=${s}">${el.dataset.instanceId} → ${s}</option>`)).join('')}</select></label>` : ''}
      <button type="button" id="wf-an">${root.classList.contains('wf-annot') ? 'Hide' : 'Show'} annotations</button>
      <button type="button" id="wf-nt">Notes</button>`;
    bar.querySelector('#wf-go').onchange = e => { location.hash = e.target.value; };
    const st = bar.querySelector('#wf-st'); if (st) st.onchange = e => { const [k, v] = e.target.value.split('='); if (k) setState(k, v, current()); };
    bar.querySelector('#wf-an').onclick = () => { root.classList.toggle('wf-annot'); chrome(); };
    bar.querySelector('#wf-nt').onclick = () => { const n = d.querySelector('.wf-notes'); if (n) n.hidden = !n.hidden; };
  }
  const notes = d.querySelector('.wf-notes');
  if (notes) {
    const list = (t, xs, f) => xs && xs.length ? `<h3>${t}</h3><ul>${xs.map(f).join('')}</ul>` : '';
    notes.innerHTML = list('Open questions', meta.open_questions, q => `<li>${q.question} <small>(${q.brd_ref || ''}; assumed: ${q.assumption || 'nothing'})</small></li>`)
      + list('Changes to the BRD layout', meta.brd_overrides, o => `<li>${o.brd}: ${o.change} <small>(${o.why})</small></li>`)
      + list('Sample data used', $$('[data-sample]').map(e => e.textContent.trim()).filter((x, i, a) => x && a.indexOf(x) === i), x => `<li>${x}</li>`);
  }
  if (/export/.test(location.search)) root.classList.add('wf-export');
  addEventListener('hashchange', () => show(location.hash.slice(1)));
  show(location.hash.slice(1) || (meta.start || ''));
})();
```

## Appendix C · `wf_tool.py` (write to `02b-wireframes/_working/`, run with `python3 -I`)

`check` holds the word lists for placeholder, filler and generic-title tells, so this file does not repeat them.

```python
#!/usr/bin/env python3
"""wf_tool v1 — wireframe HTML → manifest, checks and exports. Standard library only, except `export` (Playwright).
usage: wf_tool.py manifest <wireframes.html> <out_dir>      writes wireframe-manifest.json and <slug>.wireframe.json
       wf_tool.py check    <wireframes.html>                prints error:/check: lines; exit 1 on any error
       wf_tool.py export   <wireframes.html> <out_dir>      writes png/<id>.png per screen and frame, <slug>-wireframes.pdf, and in _qa/
                                                            the reading-order overlays and contact sheets for the visual review
"""
import hashlib, json, os, re, sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
OVERLAY = {"drawer", "modal", "toast", "menu", "popover"}
TYPES = {"nav", "header", "tabs", "filter-bar", "table", "list", "card", "record-header", "form", "chart", "metric", "board", "calendar",
         "timeline", "stepper", "media", "document", "map", "chat", "ai-answer", "drawer", "modal", "toast", "banner", "menu", "popover",
         "empty-state", "diff", "tree", "graph", "compare", "upload", "rating"}

class Node:
    def __init__(s, tag, attrs, parent):
        s.tag, s.a, s.parent, s.kids = tag, dict(attrs), parent, []
    def walk(s):
        yield s
        for k in s.kids:
            if isinstance(k, Node): yield from k.walk()
    def text(s):
        if s.tag in ("script", "style", "template"): return ""
        return " ".join(" ".join((k if isinstance(k, str) else k.text()) for k in s.kids).split())
    def up(s, pred):
        p = s.parent
        while p is not None and not pred(p): p = p.parent
        return p

class Tree(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.root = Node("#doc", {}, None); s.cur = s.root
    def handle_starttag(s, tag, attrs):
        n = Node(tag, [(k, v if v is not None else "") for k, v in attrs], s.cur); s.cur.kids.append(n)
        if tag not in VOID: s.cur = n
    def handle_startendtag(s, tag, attrs):
        s.cur.kids.append(Node(tag, [(k, v if v is not None else "") for k, v in attrs], s.cur))
    def handle_endtag(s, tag):
        n = s.cur
        while n is not None and n.tag != tag: n = n.parent
        if n is not None and n.parent is not None: s.cur = n.parent
    def handle_data(s, data):
        s.cur.kids.append(data)

def load(path):
    t = Tree(); t.feed(open(path, encoding="utf-8").read()); nodes = list(t.root.walk())
    meta_n = next((n for n in nodes if n.a.get("id") == "wf-meta"), None)
    if meta_n is None: sys.exit("error: no <script type=\"application/json\" id=\"wf-meta\">")
    raw = "".join(k for k in meta_n.kids if isinstance(k, str))
    try: meta = json.loads(raw)
    except Exception as e: sys.exit(f"error: wf-meta is not valid JSON: {e}")
    html = next((n for n in nodes if n.tag == "html"), t.root)
    return nodes, meta, html

def in_chrome(n): return n.up(lambda p: "data-wf-chrome" in p.a) is not None or "data-wf-chrome" in n.a
def screen_of(n): return n.up(lambda p: "data-screen-id" in p.a)
def toks(v): return [x for x in re.split(r"[\s,]+", v or "") if x]

def collect(path):
    nodes, meta, html = load(path)
    screens = [n for n in nodes if "data-screen-id" in n.a]
    insts = [n for n in nodes if "data-instance-id" in n.a and not in_chrome(n)]
    atoms = [n for n in nodes if "data-atom" in n.a and not in_chrome(n)]
    return nodes, meta, html, screens, insts, atoms

def manifest(path, out):
    nodes, meta, html, screens, insts, atoms = collect(path)
    reg = meta.get("components", {})
    sinfo = meta.get("screens", {})
    comps = {}
    for n in insts:
        cid, sc = n.a.get("data-component-id", ""), screen_of(n)
        sid = sc.a["data-screen-id"] if sc else "?"
        r = reg.get(cid, {})
        e = comps.setdefault(cid, {"component": cid, "name": r.get("name", cid), "type": n.a.get("data-component-type") or r.get("type", ""),
                                   "pages": [], "blocks": [], "instances": [], "variants": [], "features": [], "states": [], "cmp": []})
        if sid not in e["pages"]: e["pages"].append(sid)
        e["blocks"].append(f"{sid}/{n.a['data-instance-id']}")
        refs = toks(n.a.get("data-brd-ref"))
        e["instances"].append({"id": n.a["data-instance-id"], "screen": sid, "variant": n.a.get("data-variant") or None,
                               "states": toks(n.a.get("data-states")) or ["default"], "initial": n.a.get("data-state", "default"),
                               "brd_ref": refs, "interactions": sorted({c.a["data-interaction"] for c in n.walk() if "data-interaction" in c.a})})
        v = n.a.get("data-variant")
        if v and v not in e["variants"]: e["variants"].append(v)
        for s in toks(n.a.get("data-states")) or ["default"]:
            if s not in e["states"]: e["states"].append(s)
        for c in refs:
            if c.startswith("CMP-") and c not in e["cmp"]: e["cmp"].append(c)
    for cid, e in comps.items():
        r = reg.get(cid, {})
        for k in ("purpose", "shows", "does", "volume", "primary", "hero", "signature", "media", "views", "modes", "data_contract", "behaviour", "notes"):
            if k in r: e[k] = r[k] if k != "purpose" else ([r[k]] if isinstance(r[k], str) else r[k])
        e["variant_defs"] = r.get("variants", {})
        e["features"] = sorted(set(r.get("features", [])))
    at = {}
    for n in atoms:
        k = n.a["data-atom"]; e = at.setdefault(k, {"atom": k, "variants": [], "states": [], "screens": []})
        v = n.a.get("data-variant") or "default"
        if v not in e["variants"]: e["variants"].append(v)
        st = ["disabled"] if ("disabled" in n.a or n.a.get("aria-disabled") == "true") else []
        st += ["invalid"] if n.a.get("aria-invalid") == "true" else []
        for s in st:
            if s not in e["states"]: e["states"].append(s)
        sc = screen_of(n); sid = sc.a["data-screen-id"] if sc else "?"
        if sid not in e["screens"]: e["screens"].append(sid)
    pages = []
    for s in screens:
        sid = s.a["data-screen-id"]; si = sinfo.get(sid, {})
        body = s.text() + "|" + "|".join(f"{n.a.get('data-instance-id')}:{n.a.get('data-state','')}" for n in s.walk() if "data-instance-id" in n.a)
        pages.append({"id": sid, "title": s.a.get("data-screen-title", ""), "persona": s.a.get("data-persona"),
                      "width": int(s.a.get("data-width", "1280") or 1280), "brd_ref": s.a.get("data-brd-ref"),
                      "pattern": s.a.get("data-pattern"), "layout": "map" if s.a.get("data-pattern") == "map" else None,
                      "shape": si.get("shape"), "brief": si.get("brief"),
                      "content_hash": hashlib.sha1(body.encode()).hexdigest()[:12]})
    slug = html.a.get("data-slug") or meta.get("slug") or "app"
    app = dict(meta.get("app", {})); app.setdefault("shell", html.a.get("data-shell", "left"))
    m = {"format": "wireframe-manifest/html-1", "source": os.path.basename(path),
         "app": app.get("name"), "client": meta.get("client"), "use_case": meta.get("use_case"), "today": meta.get("today"),
         "shells": sorted({"phone" if p["width"] < 600 else "desktop" for p in pages}), "pages": pages,
         "frames": meta.get("frames", []), "signature": meta.get("signature"), "journey": meta.get("journey", []),
         "brd_overrides": meta.get("brd_overrides", []), "references": meta.get("references", []),
         "hero_object": meta.get("hero_object"), "shell": app["shell"], "nav_options": meta.get("nav_options", []),
         "agent_entry": html.a.get("data-agent-entry") or meta.get("agent_entry"), "payoff_frame": meta.get("payoff_frame"),
         "key_screens": meta.get("key_screens"),
         "alt_views": meta.get("alt_views", []), "open_questions": meta.get("open_questions", []),
         "assumptions": meta.get("assumptions", []), "components": list(comps.values()), "atoms": list(at.values()), "page_parts": []}
    os.makedirs(out, exist_ok=True)
    json.dump(m, open(os.path.join(out, "wireframe-manifest.json"), "w"), indent=2, ensure_ascii=False)
    idx = {"format": "wireframe-index/html-1", "source": os.path.basename(path), "client": meta.get("client"),
           "use_case": meta.get("use_case"), "slug": slug, "app": app, "today": meta.get("today"), "signature": meta.get("signature"),
           "nav_options": meta.get("nav_options", []), "hero_object": meta.get("hero_object"), "journey": meta.get("journey", []),
           "brd_overrides": meta.get("brd_overrides", []), "payoff_frame": meta.get("payoff_frame"), "frames": meta.get("frames", []),
           "pages": pages + [{"id": f["id"], "title": f.get("title", ""), "frame_of": f["of"], "set": f.get("set", {})} for f in meta.get("frames", [])]}
    json.dump(idx, open(os.path.join(out, f"{slug}.wireframe.json"), "w"), indent=2, ensure_ascii=False)
    print(f"{len(pages)} screens · {len(meta.get('frames', []))} frames · {len(comps)} components · {len(insts)} instances · {len(at)} atom kinds → {out}")

BANNED = r"\b(lorem|ipsum|tbd|placeholder|dummy|synthetic|demo|simulated?|sample data|john doe|jane doe|foo|bar baz)\b"
FILLER = r"\b(delve|landscape|pivotal|seamless(ly)?|robust|leverage|unlock|transformative|testament|empower|streamline|cutting-edge)\b"
GENERIC = {"overview", "insights", "quick actions", "recent activity", "at a glance", "key metrics", "welcome back", "dashboard", "details", "summary", "chart 1", "chart", "untitled", "title"}
# the team's "Dos and don'ts to reduce AI slop" (Writing, Screens, Charts), kept here for the review pass and not in the instructions
PRAISE = r"\b(powerful|effortless(ly)?|world-class|best-in-class|game-?changer|revolutionary|next-gen(eration)?|state-of-the-art|supercharge|elevate|unparalleled|holistic)\b"
TELLS = r"(\bnot just\b.*\bit'?s\b|\bin today's\b|\bin conclusion\b|\blet me know\b|\boops\b|\bmay potentially\b|\bsomething went wrong\b)"
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF\U00002600-\U000026FF\U00002700-\U00002712\U00002718-\U000027BF]")   # ✓ ✔ ✕ ✖ ✗ stay: they are text marks
PATHS = r"(\b[\w-]+\.(py|json|js|md|yaml|yml|csv|html|docx?)\b|/Users/|~/|\brun[ _-]?id\b|\bstack trace\b|\bHTTP \d{3}\b)"
CODES = r"\b(PG|CMP|WF|AG|OB|AU)-\d+[a-z]?\b"
DOCS = r"\b(invoice|receipt|purchase order|certificate|statement|delivery note|lab(oratory)? (report|result)|contract|quotation|credit note|payslip|bill of lading)\b"

def check(path):
    nodes, meta, html, screens, insts, atoms = collect(path)
    err, chk = [], []
    E, C = err.append, chk.append
    reg = meta.get("components", {})
    for k in ("app", "client", "use_case", "today", "signature", "journey", "components", "screens"):
        if not meta.get(k): E(f"wf-meta has no '{k}'")
    allow = [w.lower() for w in meta.get("allow_words", [])]
    exact = {x.strip().lower() for x in meta.get("exact_copy", [])}
    sids = [s.a["data-screen-id"] for s in screens]
    for s in set(x for x in sids if sids.count(x) > 1): E(f"screen id {s} used twice")
    fids = [f["id"] for f in meta.get("frames", [])]
    targets = set(sids) | set(fids)
    for s in screens:
        sid = s.a["data-screen-id"]
        for k in ("data-screen-title", "data-persona", "data-width", "data-pattern"):
            if not s.a.get(k): E(f"{sid}: screen needs {k}")
        b = (meta.get("screens", {}).get(sid) or {}).get("brief") or {}
        for k in ("job", "decision", "next"):
            if not b.get(k): E(f"{sid}: brief has no '{k}' (wf-meta.screens)")
        def shown(n, who):
            p = n
            while p is not None and p is not s:
                if "data-for" in p.a and who not in toks(p.a["data-for"]): return False
                if "data-when" in p.a:
                    owner = p.up(lambda q: "data-instance-id" in q.a)
                    if owner is not None and owner.a.get("data-state", "default") not in toks(p.a["data-when"]): return False
                if p.a.get("data-component-type") in OVERLAY: return False
                p = p.parent
            return True
        for who in [s.a.get("data-persona")] + [f.get("persona") for f in meta.get("frames", []) if f.get("of") == sid and f.get("persona")]:
            prim = [n for n in s.walk() if n.a.get("data-atom") == "button" and n.a.get("data-variant") == "primary" and shown(n, who)]
            if len(prim) > 1: C(f"{sid} ({who}): {len(prim)} primary buttons visible at once; one per screen (the rest secondary)")
        personas = {s2.a.get("data-persona") for s2 in screens} | {f.get("persona") for f in meta.get("frames", []) if f.get("persona")}
        for n in s.walk():
            if "data-for" in n.a:
                if "data-when" in n.a: E(f"{sid}: an element has both data-for and data-when; nest one inside the other")
                for p in toks(n.a["data-for"]):
                    if p not in personas: E(f"{sid}: data-for '{p}' is not a persona of any screen or frame")
        nav = [n for n in s.walk() if n.a.get("data-component-type") == "nav"]
        for nv in nav:
            items = [n for n in nv.walk() if n.tag == "a"]
            if len(items) > 7: C(f"{sid}: navigation has {len(items)} items; seven or fewer")
        ro = (meta.get("screens", {}).get(sid) or {}).get("reading_order") or {}
        here = {n.a["data-instance-id"] for n in s.walk() if "data-instance-id" in n.a}
        for k in ("first", "next", "act"):
            if not ro.get(k): E(f"{sid}: reading_order has no '{k}' (wf-meta.screens.{sid}.reading_order)")
        for k, ids in ro.items():
            for x in ids if isinstance(ids, list) else [ids]:
                x = f"{sid}.{x[1:]}" if str(x).startswith("~") else x
                if x not in here: E(f"{sid}: reading_order.{k} names {x}, which is not an instance on this screen")
        for n in s.walk():
            if "wf-img" in n.a.get("class", "").split() and re.search(DOCS, n.text().lower()):
                E(f"{sid}: '{n.text()[:50]}' is a document drawn as a picture; draw the document (.wf-doc) with its real parts")
            if n.a.get("data-component-type") == "document" and not any(k.tag in ("table", "dl") for k in n.walk()):
                C(f"{n.a.get('data-instance-id')}: a document with no line items or fields; draw its anatomy (title and reference, parties, dates, lines, totals, status)")
    iids = [n.a["data-instance-id"] for n in insts]
    for i in set(x for x in iids if iids.count(x) > 1): E(f"instance id {i} used twice")
    used = set()
    states_of = {n.a["data-instance-id"]: (toks(n.a.get("data-states")) or ["default"]) for n in insts}
    on_screen = {}   # screen id -> {instance id: states}: interactions and frames resolve only inside their own screen
    for n in insts:
        sc_ = screen_of(n)
        if sc_ is not None: on_screen.setdefault(sc_.a["data-screen-id"], {})[n.a["data-instance-id"]] = states_of[n.a["data-instance-id"]]
    for n in insts:
        iid, cid = n.a["data-instance-id"], n.a.get("data-component-id", "")
        sc = screen_of(n)
        if not sc: E(f"{iid}: instance outside any screen")
        elif not iid.startswith(sc.a["data-screen-id"] + "."): E(f"{iid}: instance id must start with its screen id ({sc.a['data-screen-id']}.)")
        if cid not in reg: E(f"{iid}: component '{cid}' is not in wf-meta.components"); continue
        used.add(cid)
        if not n.a.get("data-component-type"): E(f"{iid}: no data-component-type")
        elif n.a["data-component-type"] not in TYPES: E(f"{iid}: type '{n.a['data-component-type']}' is not in the contract's list")
        elif reg[cid].get("type") and reg[cid]["type"] != n.a["data-component-type"]: E(f"{iid}: type {n.a['data-component-type']} but the registry says {reg[cid]['type']}")
        if not n.a.get("data-brd-ref"): E(f"{iid}: no data-brd-ref (trace it to the BRD, or to an override in brd_overrides)")
        v = n.a.get("data-variant")
        if v and v not in reg[cid].get("variants", {}): E(f"{iid}: variant '{v}' is not declared for {cid}")
        st = states_of[iid]
        if n.a.get("data-state", "default") not in st: E(f"{iid}: initial state '{n.a.get('data-state')}' not in data-states")
        for c in n.walk():
            if "data-when" in c.a and c.up(lambda p: "data-instance-id" in p.a) is n:
                for w in toks(c.a["data-when"]):
                    if w not in st: E(f"{iid}: data-when '{w}' is not one of its states {st}")
        if n.a.get("data-component-type") in OVERLAY and "closed" not in st: E(f"{iid}: an overlay needs a 'closed' state")
        if n.a.get("data-component-type") in ("drawer", "modal"):   # basic anatomy: header (title, close), body, footer (actions)
            kind = n.a["data-component-type"]
            mine = lambda k: k.up(lambda p: "data-instance-id" in p.a) is n
            heads = [k for k in n.walk() if k.tag == "header" and mine(k) and any(h.tag in ("h1", "h2", "h3", "h4") for h in k.walk())]
            if not heads: E(f"{iid}: the {kind} has no <header> holding its title")
            for k in n.walk():
                if k.tag != "button" or not mine(k): continue
                region = k.up(lambda p: p is n or (p.tag in ("header", "footer") and mine(p)))
                if (k.a.get("data-icon") == "close" or k.text().strip().lower() in ("close", "×", "✕")) and (region is None or region.tag != "header"):
                    C(f"{iid}: the close control sits outside the {kind}'s <header>")
                if k.a.get("data-variant") == "primary" and (region is None or region.tag != "footer"):
                    C(f"{iid}: '{k.text()[:30]}' sits in the {kind}'s body; put its actions in a <footer> after the content"); break
        txt = n.text()
        if len(re.sub(r"\W", "", txt)) < 3 and not any(k.tag in ("img", "svg", "input", "select", "textarea") or "wf-img" in k.a.get("class", "") for k in n.walk()):
            E(f"{iid}: the component shows no content")
        if n.a.get("data-component-type") == "card" and any(k is not n and k.a.get("data-component-type") == "card" for k in n.walk()):
            C(f"{iid}: a card inside a card; group with space and headings instead")
    for cid, r in reg.items():
        if cid not in used: E(f"component '{cid}' is in the registry but on no screen")
        for vname in r.get("variants", {}):
            if not any(n.a.get("data-component-id") == cid and n.a.get("data-variant") == vname for n in insts):
                C(f"{cid}: variant '{vname}' is declared but no instance uses it")
        for k in ("name", "type", "purpose"):
            if not r.get(k): E(f"component '{cid}' has no '{k}' in the registry")
    def target_ok(step, sid):
        """None when the step is valid on screen `sid`, else the reason. A target on another screen does not count."""
        verb, _, arg = step.partition(":"); arg = arg.strip()
        here = on_screen.get(sid, {})
        if verb in ("back", "wait", "submit") or (verb == "close" and not arg): return None
        if verb == "go": return None if arg in targets else f"'{arg}' is not a screen or frame"
        k, _, v = arg.partition("=") if verb == "state" else (arg, "", "")
        k, v = k.strip(), v.strip()
        if k.startswith("~"): k = f"{sid}.{k[1:]}"
        if verb not in ("open", "close", "toggle", "toast", "state"): return f"unknown step '{verb}'"
        if k not in here:
            where = [s for s, m in on_screen.items() if k in m]
            return f"missing target '{k}' on {sid}" + (f" (it exists only on {', '.join(where)}; interactions never reach another screen)" if where else "")
        if verb == "state": return None if v in here[k] else f"'{k}' has no state '{v}'"
        if verb != "close" and "open" not in here[k]: return f"'{k}' has no 'open' state"
        return None
    for n in nodes:
        if in_chrome(n): continue
        if "data-interaction" in n.a:
            sc_n = screen_of(n); sid_n = sc_n.a["data-screen-id"] if sc_n else ""
            for step in [x.strip() for x in n.a["data-interaction"].split(";") if x.strip()]:
                why = target_ok(step, sid_n)
                if why: E(f"{sid_n or '?'}: interaction '{step}' on <{n.tag}> '{(n.text() or n.a.get('aria-label', ''))[:30]}': {why}")
        if n.tag in ("button", "a") and screen_of(n):
            label = n.text() or n.a.get("aria-label", "")
            href = n.a.get("href", "")
            works = "data-interaction" in n.a or n.a.get("type") == "submit" or (href.startswith("#") and href[1:] in targets) or n.a.get("role") == "tab" and "data-interaction" in n.a
            off = "disabled" in n.a or n.a.get("aria-disabled") == "true"
            if off:
                rid = n.a.get("aria-describedby", "")
                if not rid or not any(m.a.get("id") == rid and m.text() for m in nodes): E(f"{screen_of(n).a['data-screen-id']}: disabled '{label}' has no visible reason (aria-describedby → the helper text)")
            elif not works: E(f"{screen_of(n).a['data-screen-id']}: '{label or n.tag}' does nothing (no data-interaction or #screen link)")
            if label.strip().lower() in ("submit", "ok", "click here", "go", "button", "yes", "no"): C(f"{screen_of(n).a['data-screen-id']}: vague label '{label}'; a verb and an object")
    for f in meta.get("frames", []):
        if f.get("of") not in sids: E(f"frame {f['id']}: 'of' {f.get('of')} is not a screen")
        if f.get("dir") not in (None, "rtl", "ltr"): E(f"frame {f['id']}: dir must be rtl or ltr")
        kinds = {(next((n for n in insts if n.a["data-instance-id"] == k), None) or Node("x", {}, None)).a.get("data-component-type") for k in (f.get("set") or {})}
        if kinds and kinds <= {"filter-bar", "tabs", "table", "list"} and kinds & {"filter-bar", "tabs"} and not f.get("persona") and not f.get("width"):
            C(f"frame {f['id']} only shows a filter or tab choice; that works in place on {f.get('of')}, so drop the frame")
        for k, v in (f.get("set") or {}).items():
            here = on_screen.get(f.get("of"), {})
            if k not in here: E(f"frame {f['id']}: sets {k}, which is not on its screen {f.get('of')}")
            elif v not in here[k]: E(f"frame {f['id']}: sets {k}={v}, a state it does not have")
    if len(fids) > 2 * len(sids) + 2: C(f"{len(fids)} frames for {len(sids)} screens; keep frames that change the layout, a persona's view or a workflow step")
    ids_all = targets | set(states_of)
    for r in meta.get("requirements", []):
        cov = r.get("covered_by") or []
        if not cov and r.get("status") not in ("open question", "out of scope", "not shown on screen"):
            E(f"requirement {r.get('ref')} ('{r.get('need', '')[:40]}') is covered by nothing and has no status")
        for x in cov:
            if x not in ids_all: E(f"requirement {r.get('ref')}: covered_by '{x}' is not a screen, frame or instance")
    if not meta.get("requirements"): E("wf-meta has no 'requirements' map (BRD requirement → screens, frames, instances)")
    for j in meta.get("journey", []):
        if j.get("frame") not in targets: E(f"journey step '{j.get('step', '')[:40]}' points at {j.get('frame')}, which is not a screen or frame")
    for k in ("payoff_frame",):
        if meta.get(k) and meta[k] not in targets: E(f"{k} {meta[k]} is not a screen or frame")
    ks = meta.get("key_screens") or {}
    for k in ("home", "main", "agent"):
        if not ks.get(k): E(f"wf-meta.key_screens has no '{k}' (the design system draws these three)")
        elif ks[k] not in targets: E(f"key_screens.{k} {ks[k]} is not a screen or frame")
    if len(screens) > 1 and ks.get("home") and ks.get("home") == ks.get("main"):
        E("key_screens.home and key_screens.main are the same screen; the design system draws three different views, so 'main' is the screen where the storyline's main work happens")
    fr_of = {f["id"]: f.get("of") for f in meta.get("frames", [])}
    if ks.get("agent") and ks.get("main") and fr_of.get(ks["agent"], ks["agent"]) != fr_of.get(ks["main"], ks["main"]):
        C(f"key_screens.agent {ks['agent']} is not a frame of the main screen {ks['main']}")
    sigc, home = (meta.get("signature") or {}).get("component"), ks.get("home")
    if sigc and home and len(screens) > 1:   # the home key screen shows the signature, as drawn in its frame's states
        hsid = fr_of.get(home, home); hset = next((f.get("set", {}) for f in meta.get("frames", []) if f["id"] == home), {})
        def seen(n):
            p = n
            while p is not None and p.a.get("data-screen-id") != hsid:
                if "hidden" in p.a and p.a.get("data-component-type") not in OVERLAY: return False
                if p.a.get("data-component-type") in OVERLAY and hset.get(p.a.get("data-instance-id"), p.a.get("data-state", "closed")) == "closed": return False
                if "data-when" in p.a:
                    o = p.up(lambda q: "data-instance-id" in q.a)
                    if o is not None and hset.get(o.a["data-instance-id"], o.a.get("data-state", "default")) not in toks(p.a["data-when"]): return False
                p = p.parent
            return True
        if not any(n.a.get("data-component-id") == sigc and (screen_of(n) or n).a.get("data-screen-id") == hsid and seen(n) for n in insts):
            C(f"the signature ({sigc}) is not visible on key_screens.home {home}; the home shows the signature, so point home at the screen or frame where it shows")
    own_cls = {}
    for s_ in screens:
        for n in s_.walk():
            for c in n.a.get("class", "").split():
                if not re.match(r"(wf-|l-|doc-)", c) and c not in ("num", "grand"): own_cls.setdefault(c, s_.a["data-screen-id"])
    if own_cls: C(f"classes outside the wf-, l- and doc- names: {', '.join(sorted(own_cls)[:10])}; name this app's own classes l-… so the design system's kit cannot restyle them")
    sig = meta.get("signature") or {}
    if sig and sig.get("frame") not in targets: E("signature.frame is not a screen or frame")
    if sig and sig.get("component") and sig["component"] not in reg: E("signature.component is not in the registry")
    comp_names = set(reg); sentences = {}
    for s in screens:
        sid = s.a["data-screen-id"]
        for n in s.walk():
            own = " ".join(k for k in n.kids if isinstance(k, str)).strip()
            if not own or n.tag in ("script", "style"): continue
            low = own.lower()
            if any(w in low for w in allow): continue
            if re.search(BANNED, low): E(f"{sid}: '{own[:50]}' uses a placeholder or demo word")
            if re.search(CODES, own): C(f"{sid}: '{own[:50]}' shows an internal BRD code; codes stay in metadata")
            if own.strip() in comp_names: E(f"{sid}: '{own}' is a component id shown as on-screen text")
            if re.search(FILLER, low): C(f"{sid}: filler word in '{own[:50]}'")
            if n.tag in ("h1", "h2", "h3", "h4") and low in GENERIC and low not in exact: C(f"{sid}: heading '{own}' says nothing; name what the block holds")
            if n.tag in ("p", "li", "span", "div", "td", "dd", "small"):
                for sen in re.split(r"(?<=[.!?])\s+", own):
                    w = len(sen.split())
                    if w > 25: C(f"{sid}: a {w}-word sentence ('{sen[:40]}…'); 25 words at most"); break
                if len(own.split()) >= 4: sentences.setdefault(sid, []).extend(len(x.split()) for x in re.split(r"(?<=[.!?])\s+", own) if x.strip())
            if own.count("·") >= 3: C(f"{sid}: '{own[:50]}' joins four or more facts with '·'; give them their own lines")
            if "!" in own and n.tag not in ("code", "pre"): C(f"{sid}: '{own[:50]}' has an exclamation mark; keep the tone calm and factual")
            if re.search(PRAISE, low): C(f"{sid}: praise word in '{own[:50]}'; use a concrete number or fact")
            if re.search(TELLS, low): C(f"{sid}: '{own[:50]}' uses a stock AI phrase (slogan, opener, closer, hedge or 'Oops')")
            if EMOJI.search(own): E(f"{sid}: emoji in '{own[:40]}'; use a labelled icon (data-icon) or words")
            if len(re.findall(r" [—–] ", own)) >= 2: C(f"{sid}: '{own[:50]}' has more than one dash aside; one per paragraph")
            if re.search(PATHS, own, re.I) and n.tag not in ("code", "pre"): C(f"{sid}: '{own[:50]}' shows how the output was made (a file name, path, run ID or error code)")
            if re.search(r"(?<![\d.])\d+\.\d{3,}(?![\d.])", own): C(f"{sid}: '{own[:50]}' shows false precision; round to what the decision needs")
    for sid, ws in sentences.items():
        if len(ws) >= 6 and sum(ws) / len(ws) > 20: C(f"{sid}: sentences average {sum(ws) / len(ws):.0f} words; aim for 15 to 20")
    # screens: the team's slop rules that a structure check can see
    taglines = {}
    for s in screens:
        sid = s.a["data-screen-id"]; ty = lambda n: n.a.get("data-component-type")
        metrics = [n for n in s.walk() if ty(n) == "metric"]
        if len(metrics) > 6: C(f"{sid}: {len(metrics)} metrics on one screen; six at most, each with a comparison and a time frame")
        for n in s.walk():
            if ty(n) in ("card", "record-header", "metric"):
                facts = [k for k in n.walk() if k.tag == "dt" and k.up(lambda q: "data-instance-id" in q.a) is n]
                if len(facts) > 4: C(f"{sid}: {n.a.get('data-instance-id')} shows {len(facts)} key facts; four at most, the rest behind Details")
                nums = re.findall(r"(?<![\w-])\d[\d,.]*%?(?![\w-])", n.text())
                if len(nums) > 8: C(f"{sid}: {n.a.get('data-instance-id')} packs {len(nums)} numbers onto one card; keep the few the decision needs")
            if ty(n) in ("card", "record-header", "metric") and n.up(lambda q: q.a.get("data-component-type") in ("card", "record-header", "metric") and q is not n) is not None:
                C(f"{sid}: {n.a.get('data-instance-id')} is a card inside a card; flatten it into its parent's sections")
            if ty(n) == "table":
                rows = [r for r in n.walk() if r.tag == "tr" and r.up(lambda q: q.tag == "tbody") is not None]
                tagged = [r for r in rows if any(k.a.get("data-atom") == "tag" for k in r.walk())]
                cols = {i for r in rows for i, c in enumerate([k for k in r.kids if not isinstance(k, str) and k.tag == "td"]) if any(x.a.get("data-atom") == "tag" for x in c.walk())}
                if len(cols) >= 3: C(f"{sid}: {n.a.get('data-instance-id')} has tags in {len(cols)} columns; colour only the exceptions")
                if len(rows) >= 4 and len(tagged) == len(rows) and len({" ".join(k.text() for k in r.walk() if k.a.get("data-atom") == "tag") for r in rows}) == 1:
                    C(f"{sid}: {n.a.get('data-instance-id')} puts the same tag on every row; colour only the exceptions")
                for i in range(12):
                    vals = [[k for k in r.kids if not isinstance(k, str) and k.tag == "td"] for r in rows]
                    vals = [v[i].text().strip() for v in vals if len(v) > i]
                    if len(vals) >= 4 and len(set(vals)) == 1 and vals[0] and not re.fullmatch(r"[-–—]|0|none|yes|no", vals[0], re.I):
                        C(f"{sid}: {n.a.get('data-instance-id')} repeats '{vals[0][:20]}' in every row of a column; use real, varied values"); break
            if n.a.get("data-icon") in ("sparkle", "sparkles", "ai", "magic"): taglines.setdefault(("ai", sid), []).append(n)
            if n.tag == "button" and n.a.get("data-icon") and not n.text().strip() and n.a.get("data-icon") not in ("close", "more"):
                C(f"{sid}: an icon button ({n.a['data-icon']}) has no text label; icons carry their word")
        if len(taglines.get(("ai", sid), [])) > 2: C(f"{sid}: {len(taglines[('ai', sid)])} AI sparkle marks; mark AI output once per panel")
        hdr = [n for n in s.walk() if ty(n) == "header" and any(k.tag == "h1" for k in n.walk())]   # the page header (the one with the title)
        sub = next((k.text().strip() for h in hdr for k in h.walk() if k.tag in ("p", "small") and k.text().strip()), "")
        if sub: taglines.setdefault(sub, []).append(sid)
        for h in hdr:
            acts = [k for k in h.walk() if k.a.get("data-atom") == "button" and k.a.get("data-variant") in ("primary", "secondary") and k.up(lambda q: "data-instance-id" in q.a) is h]
            if len(acts) > 3: C(f"{sid}: the page header holds {len(acts)} actions; one primary and at most two others, the rest in a menu")
    for k, v in taglines.items():
        if isinstance(k, str) and len(v) > 2: C(f"the same line '{k[:40]}' heads {len(v)} screens; give each screen its own")
    hs = fr_of.get(home, home) if home else None; inst_by = {n.a["data-instance-id"]: n for n in insts}
    first = ((meta.get("screens", {}).get(hs) or {}).get("reading_order") or {}).get("first") or []
    if first and all((inst_by.get(i) is not None and inst_by[i].a.get("data-component-type") == "metric") for i in first):
        C(f"key_screens.home {home} opens on number tiles; open on the person's next task")
    for x in err: print("error:", x)
    for x in chk: print("check:", x)
    print(f"{len(screens)} screens · {len(fids)} frames · {len(reg)} components · {len(insts)} instances · "
          f"{sum(1 for n in nodes if 'data-sample' in n.a)} sample-data marks · {len(err)} errors · {len(chk)} checks")
    sys.exit(1 if err else 0)

def browser(pw):
    import glob, shutil
    try: return pw.chromium.launch()
    except Exception as first:
        roots = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or "", os.path.expanduser("~/Library/Caches/ms-playwright"), os.path.expanduser("~/.cache/ms-playwright")]
        cands = [os.environ.get("WF_CHROMIUM") or ""]
        for r in roots:
            if r and os.path.isdir(r):
                cands += sorted(glob.glob(os.path.join(r, "chromium*", "chrome-*", "Chromium.app", "Contents", "MacOS", "Chromium")) +
                                glob.glob(os.path.join(r, "chromium*", "chrome-linux*", "chrome")), reverse=True)
        cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] + [shutil.which(n) or "" for n in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")]
        for exe in [c for c in cands if c and os.path.exists(c)]:
            try: return pw.chromium.launch(executable_path=exe)
            except Exception: continue
        raise RuntimeError(f"no Chromium could be started ({str(first).splitlines()[0]})")

def cli_shots(url, order, width, out):
    """No Python Playwright: drive an installed Chrome or Chromium from the command line (screenshots only)."""
    import shutil, subprocess
    exe = next((c for c in [os.environ.get("WF_CHROMIUM") or "", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"] + [shutil.which(n) or "" for n in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")]
                if c and os.path.exists(c)), None)
    if not exe: sys.exit("export: unavailable — no Python Playwright and no Chrome or Chromium on this machine (see SKILL.md, Exports)")
    shots = []
    for fid, sid, t, fw in order:
        w = fw or width[sid]; p = os.path.join(out, "png", f"{fid}.png")
        subprocess.run([exe, "--headless=new", "--hide-scrollbars", "--disable-gpu", f"--window-size={w},{812 if w < 600 else 900}",
                        "--virtual-time-budget=4000", f"--screenshot={os.path.abspath(p)}", f"{url}?export#{fid}"], capture_output=True, timeout=60)
        if not os.path.exists(p): sys.exit(f"export: Chrome did not write {p}")
        shots.append((fid, t, w, p))
    return shots, ["export used the Chrome command line: each frame is cut at the window height, and NAV-options/VIEWS sheets are not drawn"]

RO_JS = """({sid, ro}) => {
  const sc = document.querySelector(`.wf-screen[data-screen-id="${sid}"]`), dev = sc.querySelector('.wf-device').getBoundingClientRect(), out = {};
  for (const [k, ids] of Object.entries(ro)) {
    let r = null, font = 0;
    for (let id of [].concat(ids)) {
      if (id.startsWith('~')) id = sid + '.' + id.slice(1);
      const el = sc.querySelector(`[data-instance-id="${CSS.escape(id)}"]`); if (!el || el.closest('[hidden]')) continue;
      const b = el.getBoundingClientRect(); if (!b.width || !b.height) continue;
      r = r ? {l: Math.min(r.l, b.left), t: Math.min(r.t, b.top), r: Math.max(r.r, b.right), b: Math.max(r.b, b.bottom)} : {l: b.left, t: b.top, r: b.right, b: b.bottom};
      for (const x of [el, ...el.querySelectorAll('*')]) if (x.childNodes && [...x.childNodes].some(c => c.nodeType === 3 && c.nodeValue.trim())) font = Math.max(font, parseFloat(getComputedStyle(x).fontSize));
    }
    if (r) out[k] = {left: Math.round(r.l - dev.left), top: Math.round(r.t - dev.top), width: Math.round(r.r - r.l), height: Math.round(r.b - r.t), font};
  }
  return out;
}"""

OVERLAP_JS = r"""(sid) => {
  // text that overlaps other visible text on the rendered screen (map labels on markers, a label under a floating panel)
  const sc = document.querySelector(`.wf-screen[data-screen-id="${sid}"] .wf-device`), boxes = [], hits = [];
  const vis = el => { for (let n = el; n && n !== sc; n = n.parentElement) { if (n.hidden) return false; const cs = getComputedStyle(n); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false; } return true; };
  const tw = document.createTreeWalker(sc, NodeFilter.SHOW_TEXT);
  for (let t; (t = tw.nextNode());) {
    if (!t.nodeValue.trim() || !vis(t.parentElement)) continue;
    const r = document.createRange(); r.selectNodeContents(t);
    for (const b of r.getClientRects()) if (b.width > 2 && b.height > 2) boxes.push({el: t.parentElement, txt: t.nodeValue.trim().slice(0, 28), l: b.left, t: b.top + scrollY, r: b.right, b: b.bottom + scrollY});
  }
  // a collision is two texts whose glyphs show through each other: the top element at the overlap is one of the two, and
  // nothing opaque sits between it and their common container (a drawer or a filled button over a label covers it instead)
  const opaque = (e, stop) => { for (let n = e; n && n !== stop; n = n.parentElement) { const m = getComputedStyle(n).backgroundColor.match(/rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(',').map(Number); if (p.length < 4 || p[3] > .5) return true; } } return false; };
  const common = (x, y) => { let n = x; while (n && !n.contains(y)) n = n.parentElement; return n; };
  const top = (x, y, a, c) => { scrollTo(0, Math.max(0, y - innerHeight / 2)); const e = document.elementFromPoint(x, y - scrollY);
    if (!e || !(a.el.contains(e) || c.el.contains(e) || e.contains(a.el) || e.contains(c.el))) return false; return !opaque(e, common(a.el, c.el)); };
  for (let i = 0; i < boxes.length && hits.length < 6; i++) for (let j = i + 1; j < boxes.length && hits.length < 6; j++) {
    const a = boxes[i], c = boxes[j]; if (a.el === c.el || a.el.contains(c.el) || c.el.contains(a.el)) continue;
    const ox = Math.min(a.r, c.r) - Math.max(a.l, c.l), oy = Math.min(a.b, c.b) - Math.max(a.t, c.t);
    if (ox > 3 && oy > 3 && top((Math.max(a.l, c.l) + Math.min(a.r, c.r)) / 2, (Math.max(a.t, c.t) + Math.min(a.b, c.b)) / 2, a, c)) hits.push(`"${a.txt}" overlaps "${c.txt}"`);
  }
  scrollTo(0, 0); return hits;
}"""

def export(path, out):
    nodes, meta, html, screens, insts, atoms = collect(path)
    from PIL import Image, ImageDraw, ImageFont
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sync_playwright = None
    slug = html.a.get("data-slug") or meta.get("slug") or "app"
    os.makedirs(os.path.join(out, "png"), exist_ok=True)
    width = {s.a["data-screen-id"]: int(s.a.get("data-width", "1280")) for s in screens}
    title = {s.a["data-screen-id"]: s.a.get("data-screen-title", "") for s in screens}
    order = []
    for sid in width:
        order.append((sid, sid, title[sid], None))
        order += [(f["id"], f["of"], f.get("title", ""), f.get("width")) for f in meta.get("frames", []) if f["of"] == sid]
    url = "file://" + os.path.abspath(path)
    shots, problems, ro_boxes = [], [], {}
    if sync_playwright is None:
        shots, problems = cli_shots(url, order, width, out)
    else:
      with sync_playwright() as pw:
          b = browser(pw)
          for fid, sid, t, fw in order:
              w = fw or width[sid]; pg = b.new_page(viewport={"width": w, "height": 812 if w < 600 else 800}, device_scale_factor=1)
              msgs = []; pg.on("pageerror", lambda e: msgs.append(str(e)))
              pg.goto(f"{url}?export#{fid}"); pg.wait_for_function("document.documentElement.dataset.ready==='1'", timeout=10000)
              if pg.evaluate("document.documentElement.dataset.current") != fid: problems.append(f"{fid}: the page did not open on this frame")
              el = pg.locator(f'.wf-screen[data-screen-id="{sid}"] .wf-device').first
              p = os.path.join(out, "png", f"{fid}.png"); el.screenshot(path=p)
              if fid == sid:
                  ro = (meta.get("screens", {}).get(sid) or {}).get("reading_order") or {}
                  boxes = pg.evaluate(RO_JS, {"sid": sid, "ro": ro})
                  vh = 812 if w < 600 else 800; ro_boxes[sid] = (p, boxes)
                  inside = lambda a, b: a and b and a["left"] >= b["left"] - 2 and a["top"] >= b["top"] - 2 and a["left"] + a["width"] <= b["left"] + b["width"] + 2 and a["top"] + a["height"] <= b["top"] + b["height"] + 2
                  f_, n_, a_, s_ = (boxes.get(k) for k in ("first", "next", "act", "support"))
                  if inside(f_, n_) or inside(n_, f_): n_ = None
                  if inside(f_, s_) or inside(s_, f_): s_ = None
                  if f_ and n_ and n_["top"] < f_["top"] - 8 and n_["left"] >= f_["left"]: problems.append(f"{sid}: 'next' sits above 'first'; the eye meets it first")
                  if f_ and f_["top"] > vh * 0.6: problems.append(f"{sid}: 'first' starts {f_['top']}px down; it should be the first thing in view")
                  if a_ and a_["top"] > vh: problems.append(f"{sid}: the action starts {a_['top']}px down, below the first view at {w}px")
                  if f_ and s_ and s_["top"] < f_["top"] - 8: problems.append(f"{sid}: supporting content sits above 'first'")
                  if f_ and s_ and s_["font"] > f_["font"]: problems.append(f"{sid}: supporting content uses larger type ({s_['font']}px) than 'first' ({f_['font']}px)")
                  for k in ("first", "next", "act"):
                      if ro.get(k) and not boxes.get(k): problems.append(f"{sid}: reading_order.{k} is not visible on the rendered screen")
              for h in pg.evaluate(OVERLAP_JS, sid): problems.append(f"{fid}: text overlaps on the rendered screen: {h}")
              hs = pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
              if hs > 2: problems.append(f"{fid}: {hs}px of sideways scroll at {w}px")
              problems += [f"{fid}: script error {m}" for m in msgs]; shots.append((fid, t, w, p)); pg.close()
          for sheet in ("NAV-options", "VIEWS"):
              if any(n.a.get("id") == sheet for n in nodes):
                  pg = b.new_page(viewport={"width": 1280, "height": 800}); pg.goto(f"{url}?export#{sid}")
                  pg.wait_for_function("document.documentElement.dataset.ready==='1'")
                  pg.evaluate(f"(()=>{{const s=document.getElementById('{sheet}');s.hidden=false;s.removeAttribute('data-wf-chrome');s.scrollIntoView()}})()")
                  pg.locator(f"#{sheet}").screenshot(path=os.path.join(out, "png", f"{sheet}.png")); pg.close()
          b.close()
    pages = []
    try: font = ImageFont.truetype("DejaVuSans.ttf", 12)
    except Exception: font = ImageFont.load_default()
    for fid, t, w, p in shots:
        im = Image.open(p).convert("RGB"); full = Image.new("RGB", (im.width, im.height + 34), "white"); full.paste(im, (0, 34))
        ImageDraw.Draw(full).text((12, 11), f"{fid} · {t} · {w}px", fill="#333", font=font); pages.append(full)
    pdf = os.path.join(out, f"{slug}-wireframes.pdf")
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=110)
    qa = os.path.join(out, "_qa"); os.makedirs(qa, exist_ok=True)
    colours = {"first": "#d62728", "next": "#1f77b4", "act": "#2ca02c", "support": "#9467bd"}
    for sid, (p, boxes) in ro_boxes.items():
        im = Image.open(p).convert("RGB"); dr = ImageDraw.Draw(im)
        for i, k in enumerate(("first", "next", "act", "support"), 1):
            bx = boxes.get(k)
            if not bx: continue
            dr.rectangle([bx["left"], bx["top"], bx["left"] + bx["width"], bx["top"] + bx["height"]], outline=colours[k], width=3)
            dr.rectangle([bx["left"], bx["top"], bx["left"] + 74, bx["top"] + 18], fill=colours[k]); dr.text((bx["left"] + 4, bx["top"] + 3), f"{i} {k}", fill="white", font=font)
        im.save(os.path.join(qa, f"reading-order-{sid}.png"))
    thumbs = [(fid, t, Image.open(p).convert("RGB")) for fid, t, w, p in shots]
    for n in range(0, len(thumbs), 6):
        cells = []
        for fid, t, im in thumbs[n:n + 6]:
            s = 600 / max(im.width, 1); im2 = im.resize((600, max(1, int(im.height * s)))); im2 = im2.crop((0, 0, 600, min(520, im2.height)))
            cell = Image.new("RGB", (600, 548), "white"); cell.paste(im2, (0, 28)); ImageDraw.Draw(cell).text((8, 8), f"{fid} · {t}"[:90], fill="#222", font=font); cells.append(cell)
        sheet = Image.new("RGB", (3 * 610 + 10, ((len(cells) + 2) // 3) * 558 + 10), "#cfcfcf")
        for i, c in enumerate(cells): sheet.paste(c, (10 + (i % 3) * 610, 10 + (i // 3) * 558))
        sheet.save(os.path.join(qa, f"contact-sheet-{n // 6 + 1}.png"))
    if sync_playwright is None: problems.append("reading order and overlapping text were not measured (no Playwright); check both by eye on each screen")
    for x in problems: print("check:", x)
    print(f"{len(shots)} frames → {out}/png and {pdf}")

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    cmd, src = sys.argv[1], sys.argv[2]
    if cmd == "manifest" and len(sys.argv) == 4: manifest(src, sys.argv[3])
    elif cmd == "check": check(src)
    elif cmd == "export" and len(sys.argv) == 4: export(src, sys.argv[3])
    else: sys.exit(__doc__)
```
