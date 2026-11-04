# The wireframe spec — format and block library

One JSON file per run: `<workspace>/02b-wireframes/<slug>.wireframe.json`. `scripts/render.py` draws it. Every field
below is read by the renderer or written to the manifest; nothing else is.

```json
{
  "client": "Acme Retail", "use_case": "Inventory IQ", "slug": "acme-retail-inventory-iq",
  "app": { "name": "Inventory IQ", "logo": "ACME", "nav": ["Overview", "Sites", "Reorders"], "phone_tabs": ["Tasks", "Scan"],
           "search_label": "Search stores, SKUs, orders", "agent": "Copilot" },
  "today": "12 Aug",
  "signature": { "name": "the one object or interaction no other app has", "frame": "PG-02", "why": "why it is unique to this client" },
  "nav_options": [ { "name": "Labelled left rail", "shell": "left", "why": "…" },
                   { "name": "Dark band", "shell": "band", "why": "…", "chosen": true },
                   { "name": "Rail with saved views", "shell": "context", "why": "…" } ],
  "hero_object": { "name": "store", "picture": "the store's front photo, or false when it has none", "judged_by_eye": [ "what the person checks by looking" ] },
  "journey": [ { "step": "what the person does, in their words", "frame": "PG-01" } ],
  "brd_overrides": [ { "brd": "CMP-04 / §11.2 layout", "change": "what you did instead", "why": "the rule or brief line behind it" } ],
  "references": [ { "source": "…", "url": "…", "for": "the component it changed", "take": [ "…" ], "leave": [ "…" ] } ],
  "pages": [ { …page… } ]
}
```

`allow_words` (optional) lists real names that contain a banned word, e.g. `["Ewden Synthetic"]` for a product called that; the check skips text containing them. Give the reason in the hand-over.
`today` is the day the story is set on (SKILL.md rule 5): every date and day count on screen must agree with it. A
frame later in the story (after a lock, a week on) sets its own `today` on the page; extra frames inherit their page's.
`payoff_frame` (SKILL.md rule 16): the page ID of the frame where the signature's decision resolves.
`nav_options` (SKILL.md rule 13): three navigation shells drawn on the home, one from each family (rail, bar, command), one `chosen`; `app.shell` must match the
chosen one. Shells: `left`, `icons`, `context`, `topbar`, `band`, `command`. `app.context` gives the context panel's
items per nav area (`{"Style worklist": [["Ready to write", 8], ["Lock 22 Nov", 11]]}`), or a page's own `context`.
`hero_object` (SKILL.md rule 4) is the one thing these users care about most, from scoping §21 "Hero object": its
`name`, its `picture` (what the picture is, or `false`), and what the person `judged_by_eye`. When it has a picture,
the renderer warns if the signature, the home or most pages show none: put `thumb: true` on the table, list or
calendar that lists it, or draw the items as `media`.
`signature` is required in every new spec (SKILL.md rule 4, patterns.md part 2): when it is there, the renderer stops
on a missing signature field, brief or pattern, and warns when its frame draws it with generic blocks only. A spec
**without** a `signature` key is a legacy spec (written before v4): it renders exactly as before, and its missing
briefs, patterns and signature, and the other v4 checks (navigation options, references, hero object, payoff frame,
house layout), print as `warning:` lines instead of stopping (SKILL.md Update mode). `journey` is the demo storyline walked through the frames in order (SKILL.md rule 7). `brd_overrides` records every
place you changed the BRD's layout or did not use one of its components, with what replaced it and why; `coverage.py`
accepts a CMP ID listed here. `references` lists each reference you found by research or were given, the component it changed, what you took
and what you left (patterns.md part 7).

## Page

| Field | Meaning |
|---|---|
| `id` | the scoping document's page ID (`PG-03`). A second frame of the same page (a state, an open panel, an overlay) adds a letter: `PG-03b` |
| `title` | the page name from scoping §11 (and what the frame shows, for a second frame) |
| `pattern` | how the page works: `queue`, `split`, `focus`, `decision`, `guided`, `board`, `dashboard`, `map`, `feed` (patterns.md part 1). Required on a page's first frame |
| `shape` | which shape of the pattern this page uses, in words (patterns.md part 1 table), e.g. "inbox rows of two lines", "document with a margin" |
| `brief` | the thinking behind the page (SKILL.md rule 2): `arrives` (from where, when), `job`, `decision`, `sees` (what they need to see to decide, and how they trust it), `needs_you`, `done` (what the system or others already did), `next` (the one next step). `job`, `decision`, `needs_you` and `next` are required on a page's first frame; extra frames inherit it |
| `brd_ref` | the scoping section or route (`§11.3`, `/planner`) |
| `persona` | the page's primary persona (scoping §11 "Personas") |
| `width` | the persona's device width: 1280 desktop, 375 phone (scoping §7 / 0.4 of the design system) |
| `nav_active` | the nav item lit for this page |
| `today` | only for a frame set on a later day than the spec's `today` |
| `shell` | the page's own navigation shell when its persona's differs from `app.shell` (`left`, `icons`, `context`, `topbar`, `band`, `command`); a phone width gets the phone shell |
| `alt_view_of` | on a frame that draws another view of a page's items (rule 14): the page ID, with `view` naming the view shown |
| `context` | the context panel's items for this page, with the `context` shell |
| `topbar` | for `topbar` and map pages: `{"tabs": [...], "active": 0, "right": ["All states", "DAILY BRIEF"]}` (an UPPER-CASE item draws as a button with an icon). A count on a tab belongs to the page's persona: the director's tabs count the director's work |
| `rows` | the page body: a list of rows, each a list of blocks on a 12-column grid (`span` per block, `h` in px) |
| `layout` | `"map"` for a full-screen map page (see below); then `map`, `left`, `right` replace `rows` |
| `overlays` | a `drawer` or `modal` drawn over the page (one per frame) |

## Blocks — every block has `type`, `span`, `h`; every component block has `id` (scoping block ID) and `component`

Optional on any component block: `cmp` (the scoping §23 CMP ID it belongs to), `states` (from: loading, empty,
no-results, error, no-access, offline, thinking, …), `variants` (the forms the pages need, e.g. "compact",
"horizontal"; at most three per component across all pages), `note` (one line for the design system, about what it
must do, never how it looks).
For the design system, give every component block what it is for and what it carries: `purpose` (one line: the job
it does for the person), `shows` (the data fields it shows, in order of importance), `does` (the actions it offers),
and `hero: true` on the component that defines the page. A hero list, table, grid, board or calendar also gets `views`
(the 2 or 3 ways to look at its items, drawn as a switch on its title row) and `view` (the one shown). Each view other
than the one shown is an object with its `kind` (`table`, `board`, `wall`, `list`) and, for a board, `group_by`
(`status`, `meta` or `tags`), unless a frame draws it (`alt_view_of`); the renderer draws the rest in `png/VIEWS.png`.
`disabled: true` on a `button` or `next` block draws its action blocked. A hero component also gets `volume` (how many items it
holds at once in the seed, e.g. "12 styles", "about 60 invoices") and `primary` (its one main action). Where the hero
object's picture shows, `thumb: true` (table, list, calendar: a square picture leads each row) or a `media` block
(with `ratio`: width:height as `"1:1"`, `"4:5"`, `"16:9"` or a number such as `1.5`); `media: {"ratio": "4:5", "where": "…"}` on any other block records a picture slot the drawing cannot
show. These go into the manifest, and the design system designs to them.

`app.search_label` is the top bar's search placeholder (the document's own words); `app.agent` is the agent's short
name on its button and badges (default "AI"). Blocks without a `component` (`header`, `filters`, `tabs`, `label` and
the single controls) are page parts, not components: they go to the manifest's `page_parts`, never to `components`.

**The manifest** (`wireframe-manifest.json`), per component: `pages`, `blocks`, `cmp`, `variants` (only what the spec
lists), `features` (what the drawing shows it must do: `select`, `bulk`, `status_col`, `card`, `cluster`, `popup`,
`kind:<x>`), `states`, `notes`, `media`, `volume`, `primary`, `views`, and for a map `modes` plus the `data_contract` per mode and any `behaviour` lines.

| type | Draws | Fields |
|---|---|---|
| **`slot`** | **an empty dashed region naming the component** — the default for anything generic | `component`, `count` (×N), `title`, `note`, `variants`, `states` |
| `header` | page title, subtitle, breadcrumb, actions (last = primary) | `title`, `subtitle`, `breadcrumb`, `actions` |
| `filters` | search box + filter chips with their values | `chips`, `search`, `search_label` |
| `tabs` | tab row | `items`, `active` |
| `label` | a small section label | `text` |
| `kpi` | metric tile with a trend line | `label`, `value`, `delta` |
| `stat` | big-number tile (label, info, value, unit, delta pill) | `label`, `value`, `unit`, `warn`, `delta` |
| `insight` | floating insight card (map pages): label, value, "/ total", progress, one line, ↗ | `label`, `value`, `of`, `sub`, `progress`, `warn`, `ai`, `badge`, `active` |
| `table` | table with header, rows, status pills | `title`, `columns`, `rows` (a list of cell lists in column order, the status cell's text drawn as its pill), `selected` (row index, e.g. the row a preview pane shows), `status_col`, `statuses`, `action_col`, `select`, `checked` (row indexes drawn ticked, or `"all"`), `bulk`, `thumb`. A hero table needs 4–8 real `rows`; rows past them are drawn as grey bars |
| `list` | one-to-two-line list with status pills | `title`, `items: [{title, meta, status}]`, `thumb` |
| `card` | text card with an optional button | `title`, `lines`, `action` |
| `chart` | chart placeholder | `title`, `kind` (line, bar, donut), `caption` |
| `form` | labelled fields and submit | `title`, `fields: [{label, kind (text, select, number, textarea, photo), value}]`, `submit`, `submit_full` |
| `select`, `stepper`, `slider`, `text`, `button` | single form controls and text inside panels | `label`, `value`, `kind`, `filled` / `text`, `bold`, `size` / `full`, `disabled` |
| `tiles` | a row of 2–4 count tiles at the top of a panel | `items: [[label, value], …]`, `active` |
| `move` | a from → to card with value and Reject / Approve | `from`, `to`, `miles`, `value`, `value_label`, `detail`, `kind` |
| `timeline` | a short event list | `title`, `items` |
| `next` | the page's one next step: a sentence and one primary action; `kind: "decision"` draws the fixed approve bar | `text`, `action`, `secondary`, `label`, `ai`, `kind`, `sub` |
| `steps` | where the person is in a job: numbered steps, done ones ticked | `items`, `active` |
| `chips` | the work split by who has to act, with counts (Needs you · In hand · Already done) and an optional reason filter | `items: [[label, count]]`, `active`, `right` |
| `work` | work items as cards: name, tags, the number to act on, a one-line reason, a progress bar, actions | `title`, `items: [{title, tags, value, value_label, why, ai, progress, progress_label, actions}]` |
| `options` | options side by side; one `state: "recommended"`; `state: "blocked"` shows why and has no button | `items: [{name, head, sub, badge, state, facts: [[label, value]], note}]`, `choose` |
| `compare` | options compared row by row; a string row is a section label; `best` shades the recommended column | `title`, `columns`, `rows`, `best` |
| `board` | columns of cards for stages; an empty column says so | `columns: [{title, count, empty, cards: [{tag, title, meta, action}]}]` |
| `graph` | a centre item with linked items on each side, each link with its weight; `weak: true` dashes it | `title`, `center`, `left_title`, `right_title`, `left`, `right: [{label, value, weak}]`, `caption` |
| `chat` | the agent leading a job on the page: progress, messages, quick-reply chips, input | `title`, `status`, `progress: {label, of, at}`, `messages: [{from, text, done, chips, pick}]`, `input` |
| `decomp` | the working behind a number, one line per step with a plain explanation; a 4th value `"total"` marks the result | `title`, `rows: [[label, help, value(, "total")]]` |
| `facts` | tiles of the inputs used: label, value, one line, source; no value draws "Waiting" | `title`, `cols`, `items: [{label, value, sub, source}]` |
| `stack` | several blocks one under the other inside one span (an agent column beside a canvas) | `blocks` (each with its own `h`) |
| `artefact` | **the real thing its users know, with its real text** (rule 4): `layout: "product"` draws a picture gallery (`gallery`, `missing` due slots) beside `store`, `title_text`, `price`, `bullets`, `description`, `foot`; `layout: "page"` draws a page with `heading`, `paragraphs` and `lines` (rows of cells). `marks: [{n, field, kind}]` outline a field: `field` is `title`, `bullet 1`…, `description`, `paragraph 1`…, `line 1`…; `kind` is `fail` (box and solid number), `limit` (dashed) or `ok` (underline) | `title`, `layout`, the fields above, `marks` |
| `document` | a page of a document (invoice, contract, scan) with the regions the system read outlined and numbered; optional page thumbnails | `title`, `pages`, `page`, `regions: [{label, at: [x, y, w, h] as fractions}]` |
| `media` | a grid of pictures (shots, posters, products, photos) with caption, meta, tags; one can be `selected` | `title`, `cols`, `ratio`, `items: [{title, meta, tags, badge, selected}]` |
| `calendar` | time across, things down (a schedule, a Gantt, a roster); bars span their time | `title`, `columns`, `label_width`, `today`, `thumb`, `rows: [{label, bars: [{from, to, label, style: solid / outline / dashed}]}]` |
| `tree` | a hierarchy (sites › areas › assets, folders) as indented rows with open markers, meta and status | `title`, `items: [{label, depth, open, meta, status, selected}]` |

**Detail vs slot.** Draw in detail (with real wording) only what makes this app this app: the hero of each page, the
work queue, the record's main card, the map, the agent's answer. Everything generic — a KPI row, a standard chart, a
settings form, a secondary table — is a `slot` with its component name, count, the variants it needs and its states.
The design system designs the component; the wireframe only fixes where it goes and what it must cover.

## Overlays

| type | Fields |
|---|---|
| `drawer` | `id`, `component`, `title`, `width`, `messages: [{from: user|agent, text, chips, card}]`, `input`, `states` — the agent drawer is always a drawer, never a card on the page |
| `modal` | `id`, `component`, `title`, `body`, `actions` (last = primary), `width`, `height` (optional; fits its content), `blocks` |

Both overlays take `blocks`: real controls drawn inside the window or drawer (a settings set, a picker, a dossier with
facts and a chart). A drawer with `blocks` and no `messages` shows its `actions` at the foot instead of a chat input.

## Map pages (`"layout": "map"`) — read `map-component.md` first

```json
{ "id": "PG-03", "layout": "map", "width": 1280, "height": 800, "topbar": {…},
  "map":   { "type": "map", "id": "B-31", "component": "network-map", "mode": "rings | dots | arcs | radius",
             "legend": [["dot0", "Critical"], ["dot1", "Watch"], ["dot2", "Healthy"], ["ai", "Assumption"]],
             "data": { "object": "…", "lat": "…", "lng": "…", "tone_by": "…", "card_fields": [ … ] },
             "behaviour": [ "…only lines that differ from map-component.md…" ],
             "card": { "title": "…", "status": "…", "lines": [ … ] }, "labels": [ "…" ], "states": [ … ] },
  "left":  { "width": 256, "blocks": [ scope select, label, insight cards… ] }  // or "card": true for one form panel
  "right": { "id": "B-36", "component": "detail-panel", "title": "…", "width": 380, "blocks": [ … ] } }
```

Legend marks: `dot0` (filled, most urgent), `dot1` (ring), `dot2` (grey dot), `dash` (dashed route), `ai`
(an AI estimate). No "demo" or "synthetic" mark. Mode extras: `rings` → `counts`; `dots` → `n`, `share0`, `share1`, `labels`;
`arcs` → `routes`, `hubs`, `counts`; `radius` → `radius_label`, `n`.

A map is never a block in a row: the renderer stops with an error if one is.

## What the renderer checks before drawing (it stops with one line per problem)

Duplicate page ids; a page without `id`, `title` or `persona`; a page's first frame without `pattern` or the required
`brief` fields; a row wider than 12 columns; an unknown block type; a component block without `component`; a map in
a row; a map page without `mode`, `data` or `legend`.

It then prints `check:` lines for the tells it can find (patterns.md part 6): demo or placeholder words on screen, in the journey or in a brief, a
title that leads with an internal code, styling in a note, a number-tile row leading a page that is not a dashboard,
a hero drawn as a slot, a slot note written as a paragraph, most pages opening with the same blocks, a next-step
banner, work-split chips, a decision bar or a step indicator on most pages, two queue pages that open the same way,
no reference recorded for the signature, dates or day counts that disagree on what day it is, a tab whose count is
smaller than what is drawn under it, a hero table without `rows`, a persona arriving from another persona's page
with no hand-over, a home that does not show the signature or shows it as a side panel beside a list, a narrow side column on the home
(unless its brief says why) or on most pages, an extra frame whose titles
changed but whose rows did not, and a signature drawn with generic blocks only. These do not stop the render;
fix each one or say in the hand-over why it stays.
