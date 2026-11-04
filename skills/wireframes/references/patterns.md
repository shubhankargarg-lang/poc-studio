# Patterns — how each page should work, and how each app gets its own shape

Read this before writing the spec. It has seven parts: choosing a page's pattern and its shape, the app's signature,
how to carry the next step and split the work without a house layout, the rules that make a page easy to use, three
short thinking sketches, the tells, and how to use a reference. The rules come from review feedback on apps the loop
built. Nothing here is a layout to copy: two apps from this skill should not look alike.

## 1. Choose the pattern, then its shape

Answer these for each page, from its brief (SKILL.md rule 2), in order. The first "yes" is the pattern.

1. Is the main question *where* (stores, sites, warehouses, assets with coordinates)? → `map`
2. Does the job need several answers in a fixed order (plan, configure, apply, set up)? → `guided`
3. Is the person choosing one option among several? → `decision`
4. Do items move through stages the person pushes them along? → `board`
5. Does the person act on many records one by one? → `queue` (or `split` when they need the whole record beside the list)
6. Is it one record, document, picture or object worked on in depth? → `focus`
7. Is the history or a live stream the content? → `feed`
8. Does the person only watch numbers and act elsewhere (an executive)? → `dashboard`

Each pattern has several **shapes**. Pick the shape from the data and the signature (part 2), and do not give two
pages of one app the same shape unless they show the same kind of data.

| Pattern | Shapes to choose from | Design-system code |
|---|---|---|
| `queue` | inbox rows of two lines (name, then why) · table with a preview pane · cards grouped by due day · a sorted list with a "Done" fold at the bottom · the signature holding the items (page thumbnails, bars on a schedule, a picture grid) | P1 |
| `split` | list + record · list + document · three panes (list, object, notes) · list + map | P2 |
| `focus` | document with a margin of fields or comments · canvas or picture with an inspector · record with its timeline · a form wizard on one object | P3 |
| `decision` | 2–3 options side by side · one recommendation with "see others" · a compare matrix · a slider between two extremes | P3 |
| `guided` | agent column + filling canvas · numbered form steps · a checklist that unlocks in order | P8 (new) |
| `board` | stage columns · swim lanes by owner · a pipeline strip with counts above a list | P4 |
| `dashboard` | narrative brief (sentences with numbers) · mixed-width tiles and charts · one large chart with a ranked list | P5 |
| `map` | `map-component.md` (rings, dots, arcs, radius) · a floor or site plan · a schematic (gates, lines, zones) | P6 |
| `feed` | timeline by day · grouped by thread · calendar or Gantt (time across, things down) | P7 |

When two or more pages of an app are queues, give each a different shape (one inbox rows, one a table with a
preview pane, one cards grouped by day): three queues drawn the same way make three pages that look like one.

One pattern per page. A panel may hold a smaller pattern inside it (a map whose drawer holds a queue; a guided page
whose last step is a decision); never nest deeper.

## 2. The app's signature

Every app has one object or interaction that no other app has: the contract with its risky clauses outlined, the
ward floor plan, the lab plate of samples, the technician roster, the retail shelf photo. That
is what makes the app recognisable. Before drawing:

- Name it in the spec's `signature`: `name`, the `frame` where it is the hero, and `why` it is unique to this client.
- Draw it as itself with its real block (`document`, `media`, `graph`, `calendar`, `tree`, `board`, the map, `chat`,
  `compare`, `decomp`). It is never a `slot`, a `card` of text lines, a `table` or a `list`.
- Give it the most space on its page, and let it set the shape of the pages around it: an app built around a
  document puts the document beside every decision about it; an app built around pictures shows pictures on its home.
- **The home shows it too, holding the home's work.** Draw the home's items in the signature's own form where they
  fit it (a hospital's wards on the floor plan; a legal team's contracts as their first pages with the risky clauses
  counted). Give it the home's largest region. Place what it cannot show where the work needs it: below it, folded at
  the bottom, in a tab, in a drawer opened on demand, or in a side column. Choose by the work: a narrow side column on
  every home is a house layout too. A list of rows with the signature as a side panel beside it shows the same items
  twice. If the signature truly has no place on the home,
  say why in the home's brief.
- **The cover test:** cover the header and the nav of any frame. Could someone who knows the client tell which app
  it is? If every frame could belong to any app, the signature is missing.

## 3. The next step and the work split, without a house layout

Every page needs a visible next step and, where several groups of work exist, a split by who has to act. Neither
needs its own fixed block. Pick the way that fits the page; vary it across the app.

**Ways to carry the next step** (prefer the first that fits):
1. The hero's own action (the selected clause's "Accept / Redline", the ward card's "Open 4 discharges").
2. The first row or card marked as the one to do now, with its action on it.
3. A fixed decision bar at the foot of the page (`next` with `kind: "decision"`), when the page ends in one choice.
4. The agent's current question on a `guided` page.
5. The header's primary action, with the subtitle saying why.
6. A `next` banner: only when none of the above can carry it, and on at most two pages of an app.

**Ways to split the work by who has to act:** `chips` with counts · sections stacked on the page (Needs you first,
Done folded at the bottom) · board columns · tabs · a sorted list with a divider · a filter in the panel header. Use
`chips` only when two or more groups really hold work on that page.

## 4. Rules that make a page easy to use

1. **Lead with the work.** A page for someone who acts opens with what needs them. A row of number tiles may lead
   only a `dashboard` page.
2. **One next step you can see**, carried one of the ways in part 3. The header subtitle says what the page is for
   in one line.
3. **Split the work by who has to act**: *Needs you*, *In hand* (the agent or a team is on it), *Already done* (view
   only, no buttons). Filters work on these and on the reason, as well as on the record's status.
4. **Lead decisions with the recommendation**: the recommended option first, with its reason in one line, and one
   approve action. At most 3 options side by side; more than 3 means the top 3 and a compare view. An option that
   breaks a rule shows which rule and has no approve button.
5. **Use the user's words and units**, the way the client says them. A record's name comes first; its internal ID
   comes after, smaller. A source system's name goes in the source line, never in a label. Reason lines are short.
6. **Colour and status mean "needs action".** A good value never looks like a problem. Every status word and colour
   has a legend in this screen's own words.
7. **Show the working behind any number the person acts on**: one line per step with a plain explanation, and where
   each input comes from (`decomp`, `facts`).
8. **The system does the work; the person approves it.** Anything the system can read is read and shown with its
   source, never typed in by the person. The agent's work shows as done or in progress.
9. **One way in to each thing.** The same item opens the same panel from every entry point. No two cards for the
   same thing.
10. **Think through the cases the BRD skips**: no history, nothing to do today, partly done, numbers from two
    sources, an action blocked by a rule. Each gets a state in `states` or a line in the frame.
11. **Where the agent lives.** A drawer from the top bar, or the left column of a `guided` page. A nav page of its
    own only in a chat app. It opens when clicked.
12. **Pictures are drawn as pictures.** If the work is visual (shots, posters, products, photos, scans, floor
    plans), the frame shows the picture areas with `media` or `document`; a picture app without pictures is
    unreadable.

## 5. Three thinking sketches (other domains, on purpose — do not reuse their shapes)

**Contract review for a legal team.** The question is "which clauses in this contract put us at risk?" The signature
is the contract itself with risky clauses outlined. So the review page is `focus` with the `document` shape: the
contract fills the page, the margin lists each flagged clause with the playbook position, and the next step is the
first unresolved clause's own "Accept / Redline" action. The queue of contracts is an inbox of two-line rows (counter-
party, then the worst risk), sorted by deadline, with resolved ones folded at the bottom. No banner anywhere.

**Crew scheduling for field service.** The question is "who goes where tomorrow, and what is left uncovered?" The
signature is the schedule: technicians down, hours across. So the home is `feed` with the calendar shape; unassigned
jobs sit in a short list above it marked as the thing to do, and dragging a job onto a row is the action. A job opens
in a drawer with the customer's history. The dispatcher never sees a tile strip.

**Hospital bed flow for a site manager.** The question is "where will we run out of beds today?" The signature is the
ward plan. So the home is `map` with the floor-plan shape: wards coloured by beds free after expected discharges, a
ranked list of wards at risk below it, and the next step on the first ward's card ("Open 4 discharges"). The
discharge list per ward is a `board` (Ready to go / Waiting on pharmacy / Waiting on transport / Gone).

Three apps, three different first screens, each built from its own signature. That is the aim.

## 6. The tells (check every frame before you hand over)

- Most pages open the same way (the same three blocks in the same order). `render.py` prints this.
- A next-step banner, the same chips, a decision bar or a step indicator on most pages. `render.py` prints this.
- A home that does not show the signature, shows it as a side panel beside a list, or puts a narrow side column
  beside it without saying why; a narrow side column on most pages; two queue pages drawn the
  same way; an extra frame whose titles changed but whose rows did not. `render.py` prints these.
- The signature drawn as a slot, a text card, a table or a list; a picture-led app drawn without pictures.
- A row of number tiles opening a page where the person acts.
- Dates that disagree on what day it is ("lock in 23 days" beside "2 days overdue, due 8 Aug"); a tab or heading whose
  count differs from what is drawn under it; a hero table of grey bars. `render.py` prints these.
- The journey passing from one persona to another through a page only the first one uses. `render.py` prints this.
- An internal code or ID as the main text; a source system's name as a label.
- "Demo", "synthetic", "dummy", "simulate", "placeholder", "TBD" on screen, in the journey or in a brief; a component's name used as on-screen text.
- Styling words in a note (hover, shadow, blur, colour): looks are the design system's job.
- Options that all look the same with no recommendation; Approve on a blocked option.
- A field asking the person for something the system can read.
- Search drawn twice; a large empty welcome banner; the agent as a page in a non-chat app.
- A window or drawer that needs real controls drawn as a paragraph: put its blocks inside the overlay.

`render.py` prints the ones it can find as `check:` lines; fix each, or say in the hand-over why it stays.

## 7. References: the ones you are given and the ones you find

**Find out how others do the same job before you settle the signature.** The signature and one other component that
carries the app (the record the person works on, the decision) are where outside ideas pay off. Research only those
two; a queue, a form or a confirm dialog needs none.

- **Look for how it works, then how it looks.** Ask how the best tools let this kind of person do this job: what
  leads the screen, how the work is split, how a status, a blocked step or an AI suggestion is shown, what happens
  after the click. The best sources, in order: real products (help pages, product tours, vendor pages, app-store
  screenshots), pattern libraries (Mobbin, Page Flows), UX case studies (Behance case studies show whole flows).
  Dribbble shots are an extra for visual ideas only; looks are the design system's job.
- **Ask the `research` skill**, one request for both components, with the question in the client's terms ("How do
  leading PIM and content tools let an editor review AI-written product copy against claims rules?"), the purpose
  ("ideas for the wireframe of the signature component; internal"), the context (client, industry, persona, job) and
  the budget: **Quick, 3 to 5 searches, stop once two or three good examples are found.** In POC Studio, save each
  answer to `<workspace>/research/wireframes-<topic>.md` (e.g. `wireframes-signature.md`), so the design system, the
  AI PM and a later change request can read what it found. Only when the `research` skill is unavailable (not
  installed, or it returns an error) run the search yourself with the built-in web search tool and open the best
  results with the web fetch tool, to the same budget and the same order of sources, and save that answer the same
  way. When `research` runs but finds no usable example, do not search again on your own: say so in the hand-over.
  A page that will not load that way (Dribbble and Behance often need a browser) is skipped. Research never stops
  the run, and its answer is never the end of it: when `research` hands back, continue at step 2 (settle the
  signature) and go on through every step to the hand-over. If the session can start a separate agent, give it
  the research request so the answer comes back to you. If neither route finds anything usable, say so in the
  hand-over.
- **Take ideas, never artwork.** A layout move, an interaction, a way to show a status or an AI suggestion. No
  colours, logos, illustrations or copied text.
- **Keep two to four references**, each in the spec's `references`: `{"source": "...", "url": "...", "for": "<component>",
  "take": [...], "leave": [...]}`. A reference that changed nothing in the component is dropped.

**A reference the person or the BRD gives** goes in `references` the same way. Take only the listed things. A layout
the person supplies for a page replaces your arrangement for that page; the rules above still hold for everything
else on it.
