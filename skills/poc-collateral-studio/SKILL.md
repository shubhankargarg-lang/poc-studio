---
name: poc-collateral-studio
description: Create the full collateral set for a UnifyApps POC (demo script, narrated demo video, PPT, walkthrough PDF, swimlanes) from one story, in the UnifyApps template theme.
---

# POC collateral studio

> ## HARD RULE: never delete a resource
> Do not delete anything that already exists: files, recordings, pages, records, platform
> objects, or anything another person made. Overwrite only artefacts this pipeline generated in
> the current run (the deck drops the template's sample slides from its own *output copy* only).
> If something has to go, say what and let the user remove it.

One POC → five collaterals, all generated from one story so they never disagree:

| # | Collateral | File |
|---|---|---|
| 1 | Demo script (time, screen, on-screen action, narration, features) | `out/<Slug>_Demo_Script.pdf` |
| 2 | Demo video, narrated in US English, with subtitles | `out/<Slug>_Demo.mp4` + `.srt` |
| 3 | PPT built from the UnifyApps template | `out/<Slug>_Deck.pptx` |
| 4 | Walkthrough PDF: real screenshots, numbered click markers, do / see / why | `out/<Slug>_Walkthrough.pdf` |
| 5 | Swimlanes: today vs. with UnifyApps | `out/<Slug>_Swimlanes.pdf` + PNGs (also a deck slide) |

This skill is **self-contained**. Its toolkit (Appendix) is written into the project folder and
run there. It needs Node 18+, Python 3.10+, ffmpeg, poppler (`pdftotext`), and network access to
npm, PyPI and GitHub (Playwright, the offline Kokoro voice model, the Spectral font). Nothing calls
a paid or external speech service.

Do the work yourself: discover, record, capture and write everything. Do not ask the user to
screen-record or send screenshots. **Never type a password**: `kit/auth.mjs` opens a visible
browser per persona and waits while the user signs in, then reuses the saved session.

**Decide, don't ask.** Keep the user out of the loop. Every judgement call (audience, scope,
subject, length, wording, which screen proves a feature, how to resolve a contradiction, which
review finding to fix first) is yours: make it from the build session, the project's documents and
the app, record it with a one-line reason in `brief.json` → `"decisions"`, mention it in your next
update, and keep going. The user can redirect at any time; never wait for them. Stop and ask only for
what you cannot obtain or infer: **(1)** a sign-in when no existing session or credential gets you in,
and **(2)** nothing else: the UnifyApps template is bundled with this skill. Ask once, and keep
building everything else while you wait. Anything that would delete or overwrite something you did not
create is not a question either: do not do it; route around it and note it in `internal.md`.

**Length: the video and the demo script run about 4–5 minutes.** That is the default for every
POC, whatever the persona. Go longer only when the app is genuinely too large to cover its
must-show features in 5 minutes (roughly more than 12–15 must-show features, or several personas
each with their own journey). Then set the length yourself (about 1 minute per extra 3 features,
up to ~8 minutes) and state it, with the reason, in the brief decisions. Never pad: if the story
runs short, stop.

---

## Phase 0: Decide the brief yourself (no intake questions)

Do not ask the user intake questions. Work each answer out from what is already in front of you:
the build session (requirements, the customer's messages, what was built and for whom), the
project's documents, attached files, and the app itself. Write every answer to `brief.json`, add a
one-line reason for each under `"decisions"`, and state them in one short block at the top of your
first update, so the user can correct any of them while the work carries on.

1. **Persona / audience.** Infer who will watch from who asked for the POC and who will sign it off.
   Business stakeholders (CXO, brand or product leadership, operations heads, buyers) → **business**.
   IT, architecture or integration teams, or a brief that stresses APIs, security or systems →
   **technical**. A business sponsor plus a named technical evaluator → **mixed**. Name the role as
   specifically as the evidence allows ("Global Product Managers, Brand Directors"). No clear evidence →
   business.
2. **Narration voice.** Always **US English, female** (Kokoro `af_heart`). Do not ask.
3. **Scope.** Must-show features = what the app was built to prove: the requirements and success
   criteria from the build session, then every screen that carries one of them. The subject to follow
   = the record that touches the most must-show features (the one style, claim or store the seed data
   was built around). Length per the rule above.
4. **Sign-ins.** Reuse a session the build already has (saved `storageState`, or credentials the
   environment already uses, never typed by you). Only when there is no way in does the run stop: then
   open `kit/auth.mjs` and ask the user to sign in, once, for every persona at the same time.
   **Orbit:** POC Studio apps are built by Nebula on the Orbit environment
   (`https://orbit.uat.unifyapps.com/`). Use the app's **preview link** Nebula reported (`<workspace>/04-build/
   build-summary.md`, `state.json` → `app.preview_url`) as each persona's `url` and `public_url`, for discovery,
   capture, the video recording and the walkthrough. **Do not use the published Matrix app URL**: it asks for a user to
   be created before the app can be used. If no preview link is recorded, get it from Nebula before recording. When the app needs a login, open `kit/auth.mjs` on Orbit and ask the
   user to sign in to Orbit there; never type or store a password.
5. **Who receives the files.** Default **external** (the customer): no internal URLs, usernames,
   emails or build notes (`brief.share: "external"`). Use `"internal"` only when the request says the
   collaterals are for the team.
6. **Template.** Use the UnifyApps PPT template bundled with this skill:
   `assets/UnifyApps_template.pptx` in this skill's base directory (the path Claude Code prints as
   "Base directory for this skill" when the skill loads). If that path cannot be resolved, find it with
   `find ~/.claude/plugins -name UnifyApps_template.pptx`. Always use the bundled file, never another
   template. Never ask for it.

### What the persona decides (for all five collaterals)

| | Business | Technical | Mixed |
|---|---|---|---|
| Depth | Outcomes, before → after, value per scene | How it is built: workflow canvas, agent config, data objects, connectors, run history, APIs | Business acts + one technical act |
| Terminology | Plain words ("the assistant checks the shelf") | Platform terms ("the agent calls the scoring workflow; results write to the Visit object") | Plain, with terms only in the technical act |
| On screen | No code, JSON, IDs or internals | Builder screens, configs, payloads welcome | Internals only in the technical act |
| Pacing | 20–30 s per scene, 3–4 acts of 3–5 scenes | 30–40 s per scene, room to read configs | Business pacing; the technical act slower |
| Length | 4–5 min | 4–5 min (longer only for a large app, agreed) | 4–5 min |
| Opening | Problem today → outcome | Architecture: building blocks + systems | Problem → outcome; architecture before the technical act |
| Each scene ends on | What it is worth to the customer | What it shows about how it works and why that matters (reuse, governance, scale) | Per act |
| Voice speed | 1.0 | 0.95 | 1.0 |
| Deck emphasis | Challenges, outcome, proof, stats | Architecture, integration, swimlanes, governance | Both |

---

## Phase 0.5: Use the build session (when the app was built in this session)

This skill is usually invoked in the same session that built the app. That session already
holds the truth the collaterals must agree with, so use it **before writing a word of script**.
Everything below comes from what was built, not from looking at screens.

1. **Write `facts.json` from the build.** For every number, status and name the story will mention,
   record its true value and where it comes from: the seed data, the object records, the workflow
   that computes it. Example:
   ```json
   [{ "id": "samples_late", "value": 4, "phrases": ["samples are late", "samples late"],
      "source": "Sample object, status=late (seed)" },
    { "id": "jacket_sms_status", "value": "in transit", "phrases": [], "source": "SMP-BH-SS27-102-SMS1" }]
   ```
   `kit/check.py` then fails any screen, line or output that pairs a fact's phrase with a different
   number ("**Two** samples are late" in an AI brief when the record says 4).
2. **Walk the subject's records end to end.** For the one subject the story follows (one style, one
   claim), list its real state on every screen it appears on: stage, every sample round and its
   status, every date, cost lines, approvals. Contradictions between screens are the most damaging
   thing in a demo (Pentland: the summary said the *fit* sample was late, the record showed fit approved
   and the *SMS* sample in transit with a courier reference, and the chase email said "not shipped").
3. **Check every AI panel against the records it claims to summarise.** You know the prompts and the
   seed data. If an AI text disagrees with a record, or two AI panels disagree with each other (one says
   a swap closes two-thirds of a £14.52 gap, another says it saves £27.17), **fix it in the app**: fix
   the seed data, the prompt, or the cached output. Do not write narration around a wrong screen.
   **In POC Studio** the app was built by Nebula and approved by the person at the verify gate: route any fix to the
   app (seed data, prompts, cached outputs) through Nebula in the same session, and list every such fix at the
   collaterals approval gate.
   Change only demo data and prompts this build created; for records you did not create, leave them
   untouched and steer the story away from the contradiction instead (another record, another screen),
   noting it in `internal.md`. Never delete. No question is needed either way.
4. **Domain sense-check.** Would the customer's own experts accept each suggestion? (A 2-layer fabric
   "meeting the same brief" as a 3-layer GORE-TEX Pro shell would not.) Fix the data or drop the claim.
5. **Harvest what makes the story concrete:** the real navigation (routes, sidebar labels, tab
   names), stable selectors (add `data-testid` to the elements the story clicks if they lack one), the
   customer's own vocabulary from the requirements, the discovery pain points for the "today" swimlane,
   and the real architecture (apps, workflows, agents, objects, connections) for the "how it's built"
   slide and the technical act.
6. **Write `internal.md`** for everything the team should know but the customer must not see: known
   bugs, features left out and why (a copilot erroring), UAT links, test accounts, workarounds. This
   file never feeds a collateral; `check.py` fails any customer file that contains such notes.
7. **Know what the UI can actually do.** Only narrate actions the screen offers. If the app has
   "Copy draft", the narration says "copies the draft", not "sends it". If a claim needs a button
   that does not exist, build it or drop the claim.

When the app was *not* built in this session, do the same from discovery: read the app's pages,
records and AI panels during Phase 1 and write `facts.json` from what you verify.

---

## The pipeline

```bash
# POC Studio: work inside <workspace>/05-collaterals/ so every output lands in the client folder
mkdir <slug>-collateral && cd <slug>-collateral
# write every Appendix file into kit/ verbatim, then:
bash kit/setup.sh                                  # deps, Chromium, Kokoro voice, Spectral font
python3 kit/brand.py <skill-base-dir>/assets/UnifyApps_template.pptx  # tokens, logo, template copy -> brand/
```

| Phase | Command | Produces | Gate |
|---|---|---|---|
| 0 Brief | decide `brief.json` yourself from the session (persona, scope, length, share) | the brief + `decisions` | stated to the user, no questions |
| 0.5 Facts | write `facts.json`, `internal.md` from the build | ground truth | contradictions fixed in the app |
| 1 Plan | write `brief.json`, `coverage.json`, `story.json`; `node kit/lint.mjs` | the story | lint clean; 4–5 min |
| 1 Script | `python3 kit/narrate.py` then `node kit/docs.mjs script` | `out/<Slug>_Demo_Script.pdf` | sent to the user; work continues |
| 2 Sign in | `node kit/auth.mjs` | `auth/<persona>.json` | user signs in |
| 3 Capture | `node kit/run.mjs capture` | screenshots, step shots, `build/text/<scene>.txt` | **every scene green** |
| 3 Check | `python3 kit/check.py`, then read `review/check.md` as the viewer | consistency report | **0 must-fix** before recording |
| 4 Record | `node kit/run.mjs record` (`ACTS=B node …` re-records one act) | `build/raw/<act>.webm`, `build/timeline.json` | no FAIL / SLOW / OVERRUN; no LATE CUE ≥ 1.2 s |
| 4 Build | `node kit/cards.mjs && python3 kit/build.py` | `out/<Slug>_Demo.mp4`, `.srt` | acts "synced on the flash" |
| 5 Review | `python3 kit/review.py <n>`, then look at every frame | `review/v<n>/report.md`, contact sheet | all must-show items `shown`; no MUST FIX |
| 6 Swimlanes | write `swimlanes.json`; `node kit/swimlanes.mjs` | `out/<Slug>_Swimlanes.pdf`, PNGs | each step maps to a scene or discovery |
| 7 Walkthrough | `node kit/docs.mjs walkthrough` | `out/<Slug>_Walkthrough.pdf` | every page checked |
| 8 Deck | `python3 kit/deck.py --inspect`; write `deck.json`; `python3 kit/deck.py` | `out/<Slug>_Deck.pptx` | every slide rendered and checked |
| 9 Final | `python3 kit/check.py` again (it now scans all outputs) | | 0 must-fix |

Re-runs are surgical: `python3 kit/narrate.py a3 b1` re-voices two scenes; `ACTS=B` re-records one
act; `build.py` re-stitches in seconds. Each full run writes a fresh `build/<stage>.log`.

---

## Phase 1: Plan (coverage → story → script)

1. **Discover the app.** Walk every screen in scope and note the *real navigation path* to each
   (which menu, tab, row or button gets there). In the build session you mostly know this already.
2. **`coverage.json`**, one entry per must-show screen/feature. It is the checklist every version
   is audited against:
   ```json
   [{ "id": "F07", "screen": "Visit detail", "feature": "Failed check cites the brand clause",
      "nav_path": ["Sidebar › Visits", "Click visit row", "Tab › Findings"],
      "must_show_in": ["video", "walkthrough", "deck", "swimlane"] }]
   ```
3. **`brief.json`**:
   ```json
   { "customer": "Acme Beverages", "poc": "Shelf Compliance", "slug": "Acme_Shelf_Compliance",
     "persona": "business", "persona_role": "Head of Trade Marketing",
     "voice": { "gender": "female" }, "share": "external",
     "decisions": { "persona": "business: the POC was requested by brand leadership; sign-off is the Brand Director",
                    "length": "4:30, 11 must-show features", "share": "external: collaterals go to the customer" },
     "personas": { "brand": { "label": "Brand team", "url": "https://uat.example.com/app",
                              "public_url": "https://acme.example.com/app", "signin_note": "Your Acme SSO account",
                              "login": "/login", "username": "brand.lead@acme.com",
                              "localStorage": { "demoToolbar": "off" } } },
     "pronounce": { "KPIs": "K P Eyes" }, "subtitles": true, "internal_terms": ["Range Copilot error"],
     "reset": "How to reset demo data before a live run.",
     "limits": "Simulated in POC: … Connected at go-live: …" }
   ```
   `share: "external"` (default) keeps `url` and `username` out of the walkthrough (it shows
   `public_url` / `signin_note`); `"internal"` shows them. `internal_terms` are extra phrases
   `check.py` must never find in a customer file. `keepScrollOnNav: true` turns off the scroll reset.
4. **`story.json`**: acts → scenes, sized to **4–5 minutes** (about 10–13 scenes of 20–30 s). One
   idea per scene; follow one named subject throughout; write for the ear (short sentences, active
   voice, US spelling); explore rather than state (filter, open, switch, ask the assistant a real
   follow-up); say where the boundary is ("it flags the issue; the brand team decides"). Every
   number you say must be on that screen or in `facts.json`; every action you claim must be shown
   or be a button visible on that screen.
   ```json
   { "title": "Every shelf visit, *scored with proof*.",
     "opening": { "eyebrow": "Acme Beverages · Proof of concept", "subtitle": "…", "seconds": 4 },
     "closing": { "title": "From shelf photo to *scored visit*.", "subtitle": "…", "cta": "Next: pilot with 40 stores", "seconds": 5 },
     "acts": [{
       "id": "A", "title": "Find the visit", "card": "Find the visit, *not the spreadsheet*.",
       "goal": "…", "persona": "brand", "start": "/visits", "settle": 1000,
       "scenes": [{
         "id": "a1", "title": "Open the visit", "lane": "Brand team", "covers": ["F01"],
         "narration": "In Visits, Westgate scored lowest this morning. Opening it shows the clause behind each finding.",
         "actions": [
           { "do": "click", "target": { "text": "Visits", "within": "nav" }, "pre": true, "nav": true },
           { "do": "click", "target": { "testid": "visit-row-westgate" }, "say": "Click the Westgate visit", "at": "Opening it" },
           { "do": "highlight", "target": { "text": "Clause 4.2" }, "at": "the clause" } ],
         "walkthrough": { "do": ["Click **Visits** in the sidebar", "Click the *Westgate* row"],
                          "expect": "The finding and the clause it breaks.", "why": "Every finding comes with proof.",
                          "recover": "If the list is empty, clear the search box." } }] }] }
   ```
   `*text*` renders as the template's italic olive emphasis, `**text**` as bold. An act's `start`
   must be the screen its first scene talks about.
5. `node kit/lint.mjs`, then `python3 kit/narrate.py` (real timings) and
   `node kit/docs.mjs script`. Check the script's total length is 4–5 minutes. **Send the script
   and carry on recording; do not wait for approval.** If the user replies with changes, apply them,
   re-voice only the changed scenes (`python3 kit/narrate.py <ids>`) and re-record only the acts they touch.

### Actions (the only ones allowed)

| `do` | Fields | What the viewer sees |
|---|---|---|
| `click` | `target`, `nav`, `pre` | cursor travels to the element at human pace, ripple, click; `nav: true` waits for the new screen to finish loading |
| `hover` | `target` | cursor moves there (opens hover menus) |
| `type` | `target`, `text`, `delay` | click into the field, then text typed key by key |
| `press` | `key` | e.g. `Enter`, `Escape` |
| `select` | `target`, `option` | a native `<select>` choice |
| `scroll` | `to` or `by`, `pane` | mouse wheel on the pane under the cursor (most apps scroll an inner pane) |
| `highlight` | `target`, `ms`, `park` | olive glow around the element, then the cursor moves off it so it never covers the words |
| `waitFor` | `text` or `target` | waits for the app, not the clock |
| `settle` | `timeout` | waits until the network is quiet and no skeleton/spinner is visible |
| `wait` | `ms` | a pause (prefer `waitFor` / `settle`) |
| `goto` | `url`, **`reason`** | a URL jump; lint rejects it without a reason |
| `custom` | `fn` (+ any fields) | a function exported from `actions.mjs` `({page, engine, …})` |

**`pre: true`** runs the action *before the voice starts*: use it for the click that opens the
scene's screen. The recorder clicks, waits for the screen to finish loading, then starts the
narration, so the voice never talks about a screen that is not there yet. Lint rejects a scene whose
first click opens a screen under the voice (set `"under_voice": true` on the scene only if that is
intended). Every other action takes `"at": "<words from the narration>"` to land on that word (it
runs 0.25 s before it; tune with `"lead"`). `"say"` words the action for the script (needed for CSS
targets). Scenes take `"pad"` (ms after the line, default 700). `actions.mjs` may export
`prepare = { A: async ({page, base}) => … }` to stage data off camera before an act.

Targets: `{ "role": "button", "name": "Approve" }`, `{ "text": "…" }`, `{ "label": "…" }`,
`{ "placeholder": "…" }`, `{ "testid": "…" }`, `{ "css": "…" }`; add `"within": <target>` to scope
and `"nth": 1` to pick.

---

## Real navigation, not zooming (rule for the video)

The film must look like a person using the app. The toolkit enforces it:

- Each act opens **one** URL before the narration clock starts; after that every screen is
  reached by clicking the app's own sidebar, menus, tabs, rows and buttons. Each scene starts where
  the previous one ended.
- A visible cursor (injected, since recordings don't draw one) glides to each target and ripples
  on click; text is typed key by key; scrolling is real wheel scrolling of the pane.
- When the app changes route, every scrolled pane is reset to the top, so a new screen never opens
  half-way down and then jumps (the app remembering the last page's scroll).
- Navigation clicks are `pre`: the screen is open and loaded before the voice talks about it. No
  narration over a loading skeleton (`SLOW` in the log is a must-fix).
- **Forbidden:** zoom, crop-in, pan or Ken Burns effects on app footage, in the browser (CSS zoom,
  `transform: scale`, viewport changes) or in post (`zoompan`, animated scale/crop); films made
  from still screenshots; mid-act `goto` without a reason. `lint.mjs` rejects them, `build.py` uses
  cuts and cross-dissolves only (no dip to black), and `review.py` flags any `zoompan`.
- Highlights glow; they never magnify. Captions move to the top of the frame whenever the clicked or
  highlighted element is in the lower 30% of the screen, so they never cover what is being discussed.

---

## Narration voice

US English, female, offline: Kokoro `af_heart` for every POC (`brief.voice.id` exists only to
switch to `af_bella` or `af_nicole` if `af_heart` mispronounces something badly). Each scene is voiced in *beats* split at every `at` phrase, so cue times are exact.
`brief.pronounce` fixes how words sound without changing the written script. Listen to one
scene before voicing everything: `python3 kit/narrate.py a1`, then play `build/audio/a1.wav`.

---

## Theme: the UnifyApps template, everywhere

`kit/brand.py` reads the template every time (theme colours, layout logo) into
`brand/tokens.json` and copies it to `brand/template.pptx`. `kit/render.mjs` turns the tokens into
the CSS used by the cards, caption style, badge, both PDFs and the swimlanes. The deck is built
*from* the template itself. Reference values from the current template:

| Token | Value | Use |
|---|---|---|
| Canvas | radial `#FFFFFF` (0–41%) → `#F7F3ED` | slide, page, card and diagram background |
| Ink | `#0F2805` | headlines, card titles |
| Emphasis | `#847347`, Spectral Medium Italic | second half of headlines, eyebrows, icons, logo |
| Body | `#3D3829` | body text |
| Olive | `#4E582D` (accent `#828750`) | strong icon discs, AI / UnifyApps steps, CTA |
| Card | `#FCFAF5`, 1 px `#C3B9A8`, rounded | panels and cards |
| Icon disc | `#EDE6D7` + `#847347` line icon, or `#4E582D` + white | step and benefit icons |
| Sand | `#C5BAA9`, `#E3D8C2` | connectors, system lanes |
| Alert | `#F8ECE8` / `#DDB9B2` / `#AF4C44` | pain points, "The result" |

Type is Spectral throughout: headlines Light, as *"Plain lead: **italic olive phrase**."*;
eyebrows SemiBold caps in olive; body Regular. Footer on every page: UnifyApps wordmark +
"Intelligence that compounds" left, "Agentic Automation for the Enterprise · Strictly
Confidential" centre, page number right. Every film carries **"Powered and built by UnifyApps"**
bottom-right. The customer's own brand stays on their app only.

---

## Review in iterations (after every version of every collateral)

Work in phases and finish each before the next: **Facts → plan → script sent → capture green →
consistency gate → video act by act → review → swimlanes → walkthrough → deck → final check.**
Track them in the task list and send each collateral as soon as it passes.

After each version `v<n>`:

1. `python3 kit/review.py <n>`. It extracts frames (middle, every cue, end of each scene) into
   `review/v<n>/frames/`, builds `contact_sheet.jpg`, lists timing problems (OVERRUN, SLOW, FAIL, and
   LATE CUE ≥ 1.2 s as MUST FIX), runs `check.py`, and writes `review/v<n>/report.md` with the coverage
   matrix.
2. **Look at every frame** (Read the images). For each coverage item mark the Video column
   `shown` / `missing` / `wrong screen` / `unclear`, and list visual findings: navigation that
   teleports or jumps, the voice ahead of the screen, dead air, a highlight on the wrong thing, a
   caption covering the subject, the cursor on top of text, a loading screen under the voice.
3. **Read as the viewer** (`review/v<n>/check.md` puts each scene's narration beside its screen text).
   Be someone who runs this business watching for the first time: does any screen contradict the
   voice, an earlier screen, or another panel on the same screen? Is every number the same everywhere?
   Does every claimed action match a button that exists? Would their experts accept every suggestion?
   Fix the cause in the app (Phase 0.5) or in the story, never by talking around it.
4. **Check the documents against the same matrix.** Render them and look at every page:
   `pdftoppm -r 60 -png out/<file>.pdf review/v<n>/pages/<name>` for the PDFs, and
   `soffice --headless --convert-to pdf --outdir review/v<n> out/<Slug>_Deck.pptx` then
   `pdftoppm` for the deck. Look for overflow, overlap, tables running into the footer, empty slots,
   template sample text left behind, unreadable diagrams, font fallback, and stray `*` or `**`.
5. Fix (app data, story, actions, copy, deck.json), regenerate only what changed, and produce `v<n+1>`.
   Append what changed to `review/CHANGELOG.md`. **Ship only when every must-show item is `shown`
   in every collateral it is marked for and `check.py` reports 0 must-fix.**

---

## Swimlanes (`swimlanes.json`)

```json
{ "lanes": [ {"id":"merch","label":"Merchandiser","kind":"role"},
             {"id":"ua","label":"UnifyApps","kind":"unifyapps"},
             {"id":"crm","label":"Retail CRM","kind":"system","status":"simulated"} ],
  "views": [
    {"id":"today","title":"Today: *the manual shelf audit*.","steps":[
       {"id":"t1","lane":"merch","text":"Walks the shelf with a checklist","pain":"Results vary by person"} ]},
    {"id":"with","title":"With UnifyApps: *a scored visit in seconds*.","steps":[
       {"id":"w1","lane":"merch","text":"Uploads shelf photos","scene":"a1"},
       {"id":"w2","lane":"ua","text":"Agent scores six KPIs","kind":"ai","scene":"a2"},
       {"id":"w3","lane":"ua","text":"Visit record created","scene":"a2"},
       {"id":"w5","lane":"crm","text":"Score written back","kind":"system","parallel":true} ]} ] }
```

Steps flow left to right in order. Kinds: `manual` (card), `ai` (olive, "AI · UnifyApps"),
`auto` (light olive, "Automated · UnifyApps"; the default for steps in the UnifyApps lane), `system`
(sand), `decision` (dashed). `parallel` puts a step in the previous step's column, with the same input
and output: use it only for truly simultaneous steps. **A step that uses another step's output goes in
a later column** (the PACE agenda is built *from* submitted concepts, so it comes after the readiness
check, not beside it). `next: [ids]` overrides the flow. `pain` adds a red tag (today view). Lane
`status`: `live`, `simulated`, `golive`. Every "with" step names the `scene` that shows it; "today"
steps come from discovery, never invented. Keep a view to 4–5 lanes and 8 columns or fewer so the deck
slide stays readable. Technical persona: add a third view of system interactions.

## Walkthrough PDF

`node kit/docs.mjs walkthrough` builds: cover; at-a-glance (acts + the "with" swimlane); one page
per scene with the real final screenshot, **Why it matters**, and each **Do** line paired with its
numbered step shot (lint warns when `walkthrough.do` lines don't match click/type/select actions);
**You'll see**, **If it doesn't**, feature tags; an appendix with where to go and how to sign in (per
`brief.share`), reset steps, the screens shown live (from `coverage.json`), and what is simulated or
connected at go-live. Persona sets the wording depth.

## Deck (`deck.json`)

Every slide is a copy of one of the template's three slides, so master, background, footer and
fonts carry over. Run `python3 kit/deck.py --inspect` first: it lists each template slide's text
slots `T#` and pictures `P#` (the current template: slide 1 "Today's challenges" with 5 icon steps,
"Where it breaks down" 2×2 and "The result"; slide 2 "Reinvented" with 3 steps, a wide screenshot
`P3` and 3 big stats; slide 3 "What <role> gets" with screenshot `P0` and 4 icon benefits).

```json
{ "slides": [
  { "from": 1, "text": { "T0": "HOW SHELF AUDITS WORK TODAY", "T1": ["Today’s challenges: ", "the manual shelf audit", "."] },
    "images": { "P0": "lucide:store", "P1": "lucide:camera" }, "notes": "speaker notes" },
  { "from": 2, "images": { "P3": { "path": "build/shots/a2.png", "y": 0.2 } } },
  { "from": 3, "images": { "P0": "build/shots/a2.png" } },
  { "from": 1, "image": "build/swimlane_with_deck.png",
    "text": { "T0": "HOW IT WORKS WITH UNIFYAPPS", "T1": ["With UnifyApps: ", "a scored visit in seconds", "."] } } ] }
```

An `image` slide keeps the title, trims the picture's empty margins and fits it between the title
and the footer (`top_in`, `bottom_in`, `left_in`, `right_in` adjust the box); it warns when the
picture ends up under 80% of the slide width.

Default storyline (adjust by persona): 1 Today's challenges (slide 1) · 2 Reinvented (slide 2,
real screenshot) · 3 What each persona gets (slide 3, one per persona) · 4 Swimlane with UnifyApps
(image slide) · 5 How it's built (**technical: required**), an image slide of an architecture
diagram drawn in the theme from the real build (Apps, Agents, Workflows, Data; customer systems
marked live / simulated / go-live) · 6 Next steps / go-live path.

- **Big stats are outcomes**, not backlog: "seconds from photo to scored visit", "every finding
  linked to its clause", "3 brands on one record". Every figure is real (POC data or `facts.json`).
  A gap or a queue size ("£14.52 over target", "49 waiting") belongs in a proof slide's caption.
- **Fill every slot you keep**: any sample text left from the template is a review failure.
- **No internal notes** anywhere, speaker notes included. Next steps describe the customer's path
  (pilot, connect systems, roll out), never our fixes ("fix the agent's model connection").
- Icons: `lucide:<name>` (lucide-static), recoloured to match the icon they replace.

## Delivery

Send each collateral as it passes review (script first, so the user can redirect early). The final message lists the
five files, the persona, voice and length, coverage status, `check.py` result, and anything
simulated. Keep `story.json`, `coverage.json`, `facts.json`, `deck.json`, `swimlanes.json`,
`internal.md` and `review/` so the next iteration is surgical. `internal.md` goes to the team, never
to the customer.

## Gotchas

- Two personas on one origin share a cookie jar: one `auth/<persona>.json` each. Some portals bind
  the token to the browser context; then sign in inside the recording process instead
  (a `prepare` hook or `custom` action) and keep the sign-in before the clock.
- Most apps scroll an inner pane, not the window: give `scroll` a `pane` (or move the cursor there).
- Wait for the app (`waitFor`, `settle`, `nav: true`), not the clock.
- `LATE CUE` means the actions before it took longer than the words: shorten them or lengthen the
  line. `OVERRUN` means the scene's actions outlast its narration (silence on film). `SLOW` means a
  screen was still loading when the voice started: preload it in `prepare`, or add a `settle`.
- `no sync flash found` means that act's audio may drift ~0.2 s: re-record the act.
- If the app's own design uses "skeleton"/"spinner" classes on content that stays on screen,
  `settle` waits its full timeout and logs SLOW: use a `waitFor` on the real content instead of
  `nav: true` for that screen.
- Headless recording runs at 1920×1080. If the app needs a real (headed) browser, run under Xvfb.
- If Spectral is missing, renders silently fall back: `render.mjs` warns; re-run `kit/setup.sh`.
- Reuse existing sessions; ask for a sign-in only when there is no way in, all personas at once; never store or type passwords.

---

## Appendix: the toolkit

Write each block below to the named path **verbatim** (they are tested together), then run
`bash kit/setup.sh`. Do not "improve" them while writing; change behaviour through the JSON files,
`actions.mjs`, or a deliberate, reviewed edit after the first run.

### `kit/setup.sh`

```bash
#!/usr/bin/env bash
# kit/setup.sh: everything the pipeline needs, installed into this project folder. Safe to re-run.
set -euo pipefail
[ -f package.json ] || npm init -y >/dev/null
npm i --no-audit --no-fund playwright@1.56.1 lucide-static@0.468.0 >/dev/null
# Use the machine's Chromium if Playwright already has one (cloud sandbox), else fetch it once.
if [ -z "${PLAYWRIGHT_BROWSERS_PATH:-}" ] && [ -z "${CHROME_PATH:-}" ]; then npx playwright install chromium >/dev/null; fi
pip install -q --break-system-packages kokoro-onnx soundfile cairosvg python-pptx numpy pillow 2>/dev/null \
  || pip install -q kokoro-onnx soundfile cairosvg python-pptx numpy pillow
command -v ffmpeg >/dev/null || { echo "ffmpeg is required (apt-get install -y ffmpeg / brew install ffmpeg)"; exit 1; }
command -v pdftotext >/dev/null || echo "WARN pdftotext missing (apt-get install -y poppler-utils / brew install poppler): check.py cannot scan PDFs"
# Offline US-English narration model (Kokoro v1.0, ~350 MB, from GitHub releases).
mkdir -p models
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s models/$f ] || curl -sSfL -o models/$f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f
done
# Spectral, the template's typeface: for HTML renders, ffmpeg subtitles and LibreOffice previews.
mkdir -p fonts ~/.fonts
for w in Light Regular Italic Medium MediumItalic SemiBold; do
  [ -s fonts/Spectral-$w.ttf ] || curl -sSfL -o fonts/Spectral-$w.ttf https://raw.githubusercontent.com/google/fonts/main/ofl/spectral/Spectral-$w.ttf
  cp -n fonts/Spectral-$w.ttf ~/.fonts/ 2>/dev/null || true
done
fc-cache -f >/dev/null 2>&1 || true
mkdir -p auth build out review
echo "setup done"
```

### `kit/lib.mjs`

```js
// kit/lib.mjs: browser, visible cursor, human-paced actions. Shared by auth, run (capture/record).
import { chromium } from 'playwright';
import fs from 'node:fs';

export const W = 1920, H = 1080;
export const readJSON = (p, d) => (fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : d);
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function launch({ headless = true } = {}) {
  const opts = { headless, args: ['--hide-scrollbars', '--force-device-scale-factor=1'] };
  if (process.env.CHROME_PATH) opts.executablePath = process.env.CHROME_PATH;
  else if (process.env.CHROME_CHANNEL) opts.channel = process.env.CHROME_CHANNEL; // e.g. "chrome"
  return chromium.launch(opts);
}

// Drawn into every document: an arrow cursor that follows the real mouse, a ripple on click,
// a glow overlay for highlights, and the sync flash. None of it changes the page's scale.
// It also resets every scrolled pane to the top when the app changes route, so a new screen never
// opens half-way down because the app remembered the last page's scroll (set window.__keepScroll to opt out).
export const OVERLAY = `(() => {
  const css = \`#__cur{position:fixed;z-index:2147483647;pointer-events:none;width:26px;height:26px;left:0;top:0;
    transform:translate(-3px,-2px);filter:drop-shadow(0 2px 3px rgba(0,0,0,.35));transition:opacity .2s}
  .__rip{position:fixed;z-index:2147483646;pointer-events:none;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;
    border:3px solid rgba(78,88,45,.85);animation:__r .55s ease-out forwards}
  @keyframes __r{to{transform:scale(3.2);opacity:0}}
  .__glow{position:fixed;z-index:2147483645;pointer-events:none;border-radius:10px;
    box-shadow:0 0 0 3px #847347,0 0 0 9px rgba(132,115,71,.28),0 0 28px 8px rgba(132,115,71,.35);opacity:0;transition:opacity .35s}\`;
  const add = () => {
    if (document.getElementById('__cur') || !document.body) return;
    const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
    const c = document.createElement('div'); c.id = '__cur';
    c.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M3 2l7.5 19 2.6-7.6L21 10.8z" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.body.appendChild(c);
    let p = null; try { p = JSON.parse(sessionStorage.getItem('__curpos')); } catch (e) {}
    if (p) c.style.left = p[0] + 'px', c.style.top = p[1] + 'px';
  };
  document.addEventListener('DOMContentLoaded', add); setInterval(add, 300);
  addEventListener('mousemove', (e) => { const c = document.getElementById('__cur'); if (!c) return;
    c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px';
    try { sessionStorage.setItem('__curpos', JSON.stringify([e.clientX, e.clientY])); } catch (x) {} }, true);
  addEventListener('mousedown', (e) => { const r = document.createElement('div'); r.className = '__rip';
    r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px'; document.body.appendChild(r);
    setTimeout(() => r.remove(), 700); }, true);
  const top = () => { if (window.__keepScroll) return; scrollTo(0, 0);
    for (const e of document.querySelectorAll('*')) if (e.scrollTop > 0 && e.scrollHeight > e.clientHeight) e.scrollTop = 0; };
  const onNav = () => { [0, 60, 180, 400, 800].forEach((ms) => setTimeout(top, ms)); };
  for (const k of ['pushState', 'replaceState']) { const o = history[k];
    history[k] = function (...a) { const before = location.pathname + location.search; const r = o.apply(this, a);
      if (location.pathname + location.search !== before) onNav(); return r; }; }
  addEventListener('popstate', onNav); addEventListener('hashchange', onNav);
  window.__glow = (el, ms) => { const g = document.createElement('div'); g.className = '__glow'; document.body.appendChild(g);
    let on = true; const place = () => { if (!on) return; const b = el.getBoundingClientRect();
      Object.assign(g.style, { left: b.left - 6 + 'px', top: b.top - 6 + 'px', width: b.width + 12 + 'px', height: b.height + 12 + 'px' });
      requestAnimationFrame(place); };
    place(); requestAnimationFrame(() => (g.style.opacity = 1));
    setTimeout(() => { g.style.opacity = 0; setTimeout(() => { on = false; g.remove(); }, 400); }, ms); };
  window.__flash = (on) => { let f = document.getElementById('__flash');
    if (on) { f = document.createElement('div'); f.id = '__flash';
      f.style.cssText = 'position:fixed;inset:0;background:#FF00FF;z-index:2147483647'; document.documentElement.appendChild(f); }
    else if (f) f.remove(); };
})();`;

// target spec -> Locator. {role,name} | {text} | {label} | {placeholder} | {testid} | {css}; optional nth / within
export function loc(page, t) {
  if (typeof t === 'string') return page.locator(t).first();
  let root = t.within ? loc(page, t.within) : page;
  let l = t.role ? root.getByRole(t.role, { name: t.name, exact: t.exact ?? false })
    : t.text ? root.getByText(t.text, { exact: t.exact ?? false })
    : t.label ? root.getByLabel(t.label)
    : t.placeholder ? root.getByPlaceholder(t.placeholder)
    : t.testid ? root.getByTestId(t.testid)
    : root.locator(t.css);
  return t.nth != null ? l.nth(t.nth) : l.first();
}

// Wait until the screen has really painted: network quiet, and no loading skeleton / spinner left.
// Returns false (and the caller logs SLOW) if something still looks busy after `ms`.
export async function settled(page, ms = 6000) {
  await page.waitForLoadState('networkidle', { timeout: ms }).catch(() => {});
  const ok = await page.waitForFunction(() => {
    const vis = (e) => { const b = e.getBoundingClientRect(); return b.height > 0 && b.width > 0 && b.bottom > 0 && b.top < innerHeight; };
    return ![...document.querySelectorAll('[aria-busy="true"], [class*="skeleton" i], [class*="shimmer" i], [class*="spinner" i]')].some(vis);
  }, null, { timeout: ms }).then(() => true, () => false);
  await sleep(350);
  return ok;
}

export class Engine {
  constructor(page, log = console.log) { this.page = page; this.log = log; this.mx = W / 2; this.my = H / 2; this.marks = []; }

  mark(kind, b) { if (b) this.marks.push({ t: Date.now(), kind, y0: Math.round(b.y), y1: Math.round(b.y + b.height) }); }
  async moveTo(x, y) {
    const d = Math.hypot(x - this.mx, y - this.my);
    const steps = Math.max(12, Math.min(40, Math.round(d / 30)));
    await this.page.mouse.move(x, y, { steps });
    this.mx = x; this.my = y;
  }
  async centre(l) {
    // Bring the element to the middle with a real smooth scroll of whatever pane holds it.
    await l.waitFor({ state: 'visible', timeout: 15000 });
    const moved = await l.evaluate((el) => {
      const b = el.getBoundingClientRect();
      const off = b.top < 80 || b.bottom > innerHeight - 80;
      if (off) el.scrollIntoView({ block: 'center', behavior: 'smooth' });
      return off;
    });
    if (moved) await sleep(700);
    return l.boundingBox();
  }
  async point(l) { const b = await this.centre(l); await this.moveTo(b.x + b.width / 2, b.y + b.height / 2); return b; }
  // Move the cursor off the thing being read so it never sits on top of the words.
  async park(b) {
    const x = Math.min(W - 40, b.x + b.width + 36), y = Math.min(H - 60, b.y + b.height + 28);
    await this.moveTo(x, y);
  }

  async run(a) {
    try { await this.act(a); }
    catch (e) { throw new Error(`${a.do} ${JSON.stringify(a.target ?? a.to ?? a.text ?? a.url ?? '')}: ${e.message.split('\n')[0]}`); }
  }
  async act(a) {
    const p = this.page;
    switch (a.do) {
      case 'click': { const b = await this.point(loc(p, a.target)); this.mark('click', b); await sleep(220);
        await p.mouse.down(); await sleep(70); await p.mouse.up();
        if (a.nav && !(await settled(p))) this.log(`SLOW screen still loading after click ${JSON.stringify(a.target)}`); break; }
      case 'hover': { this.mark('hover', await this.point(loc(p, a.target))); break; }
      case 'type': { if (a.target) { await this.run({ do: 'click', target: a.target }); await sleep(250); }
        await p.keyboard.type(a.text, { delay: a.delay ?? 55 }); break; }
      case 'press': { await p.keyboard.press(a.key); break; }
      case 'select': { this.mark('select', await this.point(loc(p, a.target))); await sleep(200);
        await loc(p, a.target).selectOption(a.option); break; }
      case 'scroll': { // wheel the pane under the cursor; {to: target} or {by: px}
        if (a.pane) await this.point(loc(p, a.pane));
        let remaining = a.by ?? 0;
        if (a.to) { const l = loc(p, a.to); await l.waitFor({ state: 'attached' });
          const b = await l.boundingBox(); remaining = b ? b.y + b.height / 2 - H / 2 : 0; }
        const step = 110 * Math.sign(remaining);
        for (let n = Math.abs(Math.round(remaining / 110)); n > 0; n--) { await p.mouse.wheel(0, step); await sleep(45); }
        await sleep(350); break; }
      case 'highlight': { const l = loc(p, a.target); const b = await this.centre(l);
        if (a.point !== false) await this.point(l);
        this.mark('highlight', b);
        await l.evaluate((el, ms) => window.__glow(el, ms), a.ms ?? 2200);
        if (a.park !== false) { await sleep(250); await this.park(await l.boundingBox() ?? b); }
        await sleep(a.hold ?? 300); break; }
      case 'waitFor': { if (a.text) await p.getByText(a.text, { exact: false }).first().waitFor({ timeout: a.timeout ?? 30000 });
        else await loc(p, a.target).waitFor({ timeout: a.timeout ?? 30000 }); break; }
      case 'settle': { if (!(await settled(p, a.timeout ?? 6000))) this.log('SLOW screen still loading'); break; }
      case 'wait': { await sleep(a.ms); break; }
      case 'goto': { this.log(`GOTO ${a.url} (reason: ${a.reason})`); await p.goto(a.url, { waitUntil: 'networkidle' }); await settled(p); break; }
      case 'custom': { const mod = await import(new URL('../actions.mjs', import.meta.url)); await mod[a.fn]({ page: p, engine: this, ...a }); break; }
      default: throw new Error(`unknown action ${a.do}`);
    }
  }
}
```

### `kit/auth.mjs`

```js
// kit/auth.mjs: one visible browser per persona; the USER types the credentials. Saves auth/<persona>.json.
// usage: node kit/auth.mjs [persona ...]
import fs from 'node:fs';
import { launch, readJSON, W, H } from './lib.mjs';

const brief = readJSON('brief.json');
const want = process.argv.slice(2);
fs.mkdirSync('auth', { recursive: true });
for (const [name, p] of Object.entries(brief.personas)) {
  if (want.length && !want.includes(name)) continue;
  if (!p.login) continue; // public app, nothing to sign in to
  const browser = await launch({ headless: false });
  const ctx = await browser.newContext({ viewport: { width: W, height: H } });
  const page = await ctx.newPage();
  await page.goto(new URL(p.login, p.url).href);
  console.log(`>> Sign in as ${p.username} for persona "${name}" in the open window. Waiting...`);
  const loginPath = new URL(p.login, p.url).pathname;
  await page.waitForURL((u) => !u.pathname.startsWith(loginPath), { timeout: 0 });
  await page.waitForLoadState('networkidle').catch(() => {});
  await ctx.storageState({ path: `auth/${name}.json` });
  console.log(`saved auth/${name}.json`);
  await browser.close();
}
```

### `kit/lint.mjs`

```js
// kit/lint.mjs: refuse a story that breaks the rules before anything is captured or recorded.
// usage: node kit/lint.mjs   (exit 1 on errors)
import { readJSON } from './lib.mjs';

const NAV_WORDS = /^(on|in|under|open|opening|next|finally|back|stepping|switch|go|moving|the \w+ tab)/i;

export function lint() {
  const story = readJSON('story.json'), cov = readJSON('coverage.json', []), brief = readJSON('brief.json');
  const errs = [], warns = [];
  const allowed = new Set(['click', 'hover', 'type', 'press', 'select', 'scroll', 'highlight', 'waitFor', 'settle', 'wait', 'goto', 'custom']);
  const ids = new Set(cov.map((c) => c.id)), covered = new Set();
  for (const [name, p] of Object.entries(brief.personas))
    if (/uat|staging|preview|localhost|127\.0\.0\.1|sandbox|dev\./i.test(p.url) && !p.public_url && brief.share !== 'internal')
      warns.push(`persona ${name}: ${p.url} looks internal; set "public_url" for the walkthrough, or "share": "internal"`);
  for (const act of story.acts) {
    if (!brief.personas[act.persona]) errs.push(`${act.id}: unknown persona ${act.persona}`);
    for (const [i, s] of act.scenes.entries()) {
      if (!s.narration?.trim()) errs.push(`${s.id}: no narration`);
      if (!s.covers?.length) warns.push(`${s.id}: covers no feature`);
      for (const f of s.covers ?? []) { if (!ids.has(f)) errs.push(`${s.id}: covers unknown feature ${f}`); covered.add(f); }
      const acts = s.actions ?? [];
      for (const a of acts) {
        if (!allowed.has(a.do)) errs.push(`${s.id}: action "${a.do}" not allowed (no fill, zoom, scale or screenshots-as-video)`);
        if (a.do === 'goto' && !a.reason) errs.push(`${s.id}: mid-act goto needs a "reason"; navigate by clicking instead`);
        if (a.at && !s.narration.includes(a.at)) errs.push(`${s.id}: cue "${a.at}" not found in narration`);
        if (a.pre && a.at) errs.push(`${s.id}: a "pre" action runs before the voice, so it cannot have an "at" cue`);
        if (JSON.stringify(a).match(/zoom|scale\(|setViewportSize/i)) errs.push(`${s.id}: zoom/scale is forbidden`);
        const t = a.target ?? a.to;
        if (t && typeof t === 'object' && t.css && !t.text && !t.name && !t.label && !a.say)
          warns.push(`${s.id}: ${a.do} on a CSS selector has no "say"; the script would print an empty name`);
      }
      // The screen must change BEFORE the voice talks about it (Pentland: narration ran 2-4 s ahead of the screen).
      const firstMain = acts.find((a) => !a.pre);
      const opensScreen = (a) => a && a.do === 'click' && (a.nav || /tab|menu|sidebar|link/i.test(JSON.stringify(a.target)));
      if (opensScreen(firstMain) && !s.under_voice && (!firstMain.at || s.narration.indexOf(firstMain.at) < 40))
        errs.push(`${s.id}: the first click opens a screen while the voice is already talking about it; mark it "pre": true (or set "under_voice": true if that is intended)`);
      if (i === 0 && NAV_WORDS.test(s.narration) && !acts.some((a) => a.pre) && act.start)
        warns.push(`${s.id}: first scene of act ${act.id} talks about a screen; make sure act "start" opens that screen (it opens ${act.start})`);
      const steps = acts.filter((a) => ['click', 'type', 'select'].includes(a.do)).length;
      if (s.walkthrough?.do && s.walkthrough.do.length !== steps) warns.push(`${s.id}: walkthrough has ${s.walkthrough.do.length} "do" lines for ${steps} click/type/select actions; they are paired with numbered step shots`);
      const words = s.narration.split(/\s+/).length, secs = words / 2.6;
      if (secs > 45) warns.push(`${s.id}: ~${secs.toFixed(0)} s of narration; split the scene`);
    }
  }
  for (const c of cov) if ((c.must_show_in ?? []).includes('video') && !covered.has(c.id)) errs.push(`coverage ${c.id} (${c.feature}) is in no scene`);
  return { errs, warns };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { errs, warns } = lint();
  warns.forEach((w) => console.log('WARN ', w));
  errs.forEach((e) => console.log('ERROR', e));
  console.log(errs.length ? `lint failed: ${errs.length} error(s)` : 'lint clean');
  process.exit(errs.length ? 1 : 0);
}
```

### `kit/run.mjs`

```js
// kit/run.mjs: capture (fast dry-run + screenshots + screen text) or record (real-time, narrated timing, video).
// usage: node kit/run.mjs capture|record      ACTS=B,C node kit/run.mjs record   (re-record only those acts)
//
// Each scene runs in two parts:
//   1. "pre" actions (navigation that opens the scene's screen) run BEFORE the voice starts, then the
//      recorder waits for the screen to finish loading. The film shows the click; the voice starts on the new screen.
//   2. the rest run under the narration, each on its `at` word.
import fs from 'node:fs';
import { launch, Engine, OVERLAY, readJSON, sleep, settled, loc, W, H } from './lib.mjs';
import { lint } from './lint.mjs';

const mode = process.argv[2];
if (!['capture', 'record'].includes(mode)) throw new Error('mode must be capture or record');
const story = readJSON('story.json'), brief = readJSON('brief.json');
const narr = readJSON('build/narration.json', {});
const only = process.env.ACTS ? process.env.ACTS.split(',') : null;
for (const d of ['build/shots', 'build/raw', 'build/text']) fs.mkdirSync(d, { recursive: true });
const logf = fs.createWriteStream(`build/${mode}.log`, { flags: only ? 'a' : 'w' }); // a full run starts a fresh log
const log = (...m) => { const s = m.join(' '); console.log(s); logf.write(s + '\n'); };

const { errs } = lint();
if (errs.length) { errs.forEach((e) => log('LINT', e)); process.exit(1); }
if (mode === 'record') {
  const missing = story.acts.flatMap((a) => a.scenes).filter((s) => !narr[s.id]);
  if (missing.length) throw new Error(`no narration for ${missing.map((s) => s.id)}; run kit/narrate.py first`);
}
let actions = {}; try { actions = await import(new URL('../actions.mjs', import.meta.url)); } catch {}

const browser = await launch();
const timeline = readJSON('build/timeline.json', {}), report = readJSON('build/capture.json', {});

async function context(persona, video) {
  const p = brief.personas[persona];
  const opts = { viewport: { width: W, height: H }, deviceScaleFactor: 1 };
  if (fs.existsSync(`auth/${persona}.json`)) opts.storageState = `auth/${persona}.json`;
  if (video) opts.recordVideo = { dir: 'build/raw/_tmp', size: { width: W, height: H } };
  const ctx = await browser.newContext(opts);
  if (brief.keepScrollOnNav) await ctx.addInitScript(() => { window.__keepScroll = true; });
  await ctx.addInitScript(OVERLAY);
  if (p.localStorage) await ctx.addInitScript((kv) => { for (const [k, v] of Object.entries(kv)) localStorage.setItem(k, v); }, p.localStorage);
  return ctx;
}

// What is on screen, as text, for the consistency check (check.py): visible text only, overlays excluded.
const screenText = (page) => page.evaluate(() => {
  const out = []; const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walk.nextNode()) { const n = walk.currentNode, el = n.parentElement; const t = n.textContent.trim();
    if (!t || !el || el.closest('#__cur,.__glow,#__ring,script,style')) continue;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    out.push(t); }
  return out.join('\n');
});

for (const act of story.acts) {
  if (only && !only.includes(act.id)) continue;
  log(`\n== ${mode} act ${act.id}: ${act.title}`);
  const base = brief.personas[act.persona].url;
  if (actions.prepare?.[act.id]) { // stage demo data off camera
    const c = await context(act.persona, false); await actions.prepare[act.id]({ page: await c.newPage(), base }); await c.close();
  }
  const ctx = await context(act.persona, mode === 'record');
  const page = await ctx.newPage();
  const t0 = Date.now(), eng = new Engine(page, log);
  await page.goto(new URL(act.start, base).href, { waitUntil: 'networkidle' }); // the only URL jump: before the clock
  if (!(await settled(page))) log(`SLOW act ${act.id} start screen still loading`);
  await sleep(act.settle ?? 1000);
  await page.mouse.move(W / 2, H / 2);
  let clock = 0; const scenes = [];
  if (mode === 'record') { // sync flash: build.py finds it and starts the act on the frame after it
    await page.evaluate(() => window.__flash(true)); await sleep(400);
    await page.evaluate(() => window.__flash(false)); clock = (Date.now() - t0) / 1000;
  }
  let failed = false;
  for (const s of act.scenes) {
    if (failed) { report[s.id] = { ok: false, error: 'skipped after earlier failure' }; continue; }
    const start = Date.now(), n = narr[s.id] ?? { dur: 0, cues: {} }; let step = 0, voice = start;
    eng.marks = [];
    const pre = (s.actions ?? []).filter((a) => a.pre), main = (s.actions ?? []).filter((a) => !a.pre);
    async function stepShot(a) { // walkthrough step shot with a numbered ring
      if (mode !== 'capture' || !['click', 'type', 'select'].includes(a.do) || !a.target) return;
      step += 1;
      try {
        const box = await eng.centre(loc(page, a.target));
        await page.evaluate(([b, n]) => { const r = document.createElement('div'); r.id = '__ring';
          r.style.cssText = `position:fixed;z-index:2147483647;pointer-events:none;left:${b.x - 8}px;top:${b.y - 8}px;width:${b.width + 16}px;height:${b.height + 16}px;border:4px solid #847347;border-radius:12px`;
          r.innerHTML = `<b style="position:absolute;left:-22px;top:-22px;width:40px;height:40px;border-radius:50%;background:#4E582D;color:#fff;font:600 22px Georgia;display:grid;place-items:center">${n}</b>`;
          document.body.appendChild(r); }, [box, step]);
        await page.screenshot({ path: `build/shots/${s.id}_s${step}.png` });
        await page.evaluate(() => document.getElementById('__ring')?.remove());
      } catch {}
    }
    try {
      for (const a of pre) { await stepShot(a); await eng.run(a); }
      if (pre.length && !(await settled(page))) log(`SLOW ${s.id}: screen still loading when the voice starts`);
      voice = Date.now();
      for (const a of main) {
        if (mode === 'record' && a.at) {
          const due = voice + (n.cues[a.at] ?? 0) * 1000 + (a.lead ?? -250);
          const wait = due - Date.now();
          if (wait > 0) await sleep(wait); else if (wait < -700) log(`LATE CUE ${s.id} "${a.at}" by ${(-wait / 1000).toFixed(1)} s`);
        }
        await stepShot(a);
        await eng.run(a);
      }
      if (mode === 'record') {
        const target = n.dur * 1000 + (s.pad ?? 700), used = Date.now() - voice;
        if (used > target) log(`OVERRUN ${s.id}: actions ${(used / 1000).toFixed(1)} s > line ${(target / 1000).toFixed(1)} s`);
        else await sleep(target - used);
      } else await sleep(s.settle ?? 600);
      await page.screenshot({ path: `build/shots/${s.id}.png` });
      if (mode === 'capture') fs.writeFileSync(`build/text/${s.id}.txt`, await screenText(page));
      report[s.id] = { ok: true }; log(`ok   ${s.id}`);
    } catch (e) {
      failed = true; report[s.id] = { ok: false, error: e.message.split('\n')[0] };
      fs.mkdirSync('build/fail', { recursive: true }); await page.screenshot({ path: `build/fail/${s.id}.png` }).catch(() => {});
      log(`FAIL ${s.id}: ${report[s.id].error}`);
    }
    const rel = (t) => (t - t0) / 1000;
    scenes.push({ id: s.id, start: rel(start), voice: rel(voice), end: rel(Date.now()),
      marks: eng.marks.map((m) => ({ ...m, t: rel(m.t) })) });
  }
  await sleep(900);
  const end = (Date.now() - t0) / 1000, video = page.video();
  await ctx.close();
  if (mode === 'record') {
    const out = `build/raw/${act.id}.webm`;
    await video.saveAs(out); await video.delete();
    timeline[act.id] = { video: out, clock, end, scenes, failed };
  }
}
await browser.close();
fs.writeFileSync('build/capture.json', JSON.stringify(report, null, 2));
if (mode === 'record') fs.writeFileSync('build/timeline.json', JSON.stringify(timeline, null, 2));
const bad = Object.entries(report).filter(([, r]) => !r.ok);
log(bad.length ? `\n${bad.length} scene(s) failing: ${bad.map(([k]) => k)}` : '\nall scenes green');
process.exit(bad.length ? 1 : 0);
```

### `kit/narrate.py`

```python
# kit/narrate.py: US-English narration, offline (Kokoro). One WAV per scene, split into beats at each
# action's `at` phrase so every cue time is exact. Writes build/audio/<scene>.wav + build/narration.json.
# usage: python3 kit/narrate.py            python3 kit/narrate.py a3 b1   (re-voice only those scenes)
import json, os, sys, re
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

brief = json.load(open("brief.json")); story = json.load(open("story.json"))
v = brief.get("voice", {}); voice = v.get("id") or "af_heart"  # always US English, female (alternates: af_bella, af_nicole)
speed = v.get("speed") or (0.95 if brief.get("persona") == "technical" else 1.0)
MODEL = os.environ.get("KOKORO_DIR", "models")
k = Kokoro(f"{MODEL}/kokoro-v1.0.onnx", f"{MODEL}/voices-v1.0.bin")
os.makedirs("build/audio", exist_ok=True)
out = json.load(open("build/narration.json")) if os.path.exists("build/narration.json") else {}
only = set(sys.argv[1:])
GAP = 0.08  # seconds of silence between beats

def say(text):
    # Spell things the way they should sound; keep the written script clean.
    for a, b in brief.get("pronounce", {}).items(): text = re.sub(rf"\b{re.escape(a)}\b", b, text)
    s, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
    nz = np.where(np.abs(s) > 0.01)[0]                        # trim the model's leading/trailing silence
    if len(nz): s = s[max(0, nz[0] - int(.03 * sr)): nz[-1] + int(.06 * sr)]
    return s, sr

for act in story["acts"]:
    for sc in act["scenes"]:
        if only and sc["id"] not in only: continue
        text = sc["narration"].strip()
        cuts = sorted({text.index(a["at"]) for a in sc.get("actions", []) if a.get("at")} - {0})
        bounds = [0] + cuts + [len(text)]
        pieces, cues, t, sr = [], {}, 0.0, 24000
        for i in range(len(bounds) - 1):
            beat = text[bounds[i]:bounds[i + 1]].strip()
            if not beat: continue
            for a in sc.get("actions", []):
                if a.get("at") and bounds[i] <= text.index(a["at"]) < bounds[i + 1]: cues[a["at"]] = round(t, 3)
            s, sr = say(beat); pieces += [s, np.zeros(int(GAP * sr), dtype=s.dtype)]; t += len(s) / sr + GAP
        audio = np.concatenate(pieces)
        sf.write(f"build/audio/{sc['id']}.wav", audio, sr)
        out[sc["id"]] = {"dur": round(len(audio) / sr, 3), "cues": cues, "voice": voice}
        print(f"{sc['id']}: {out[sc['id']]['dur']:.1f}s  cues={cues}")
json.dump(out, open("build/narration.json", "w"), indent=2)
total = sum(v["dur"] for v in out.values()); print(f"total narration {total/60:.1f} min, voice {voice}")
```

### `kit/check.py`

```python
# kit/check.py: the consistency gate. Run after `capture` (before recording) and again in every review.
#   python3 kit/check.py            -> review/check.md, exit 1 if anything must be fixed
# It checks, mechanically:
#   1. every number the narration says is on that scene's screen (or in facts.json)
#   2. facts.json: wherever a fact's phrase appears with a number - in narration, on any screen, in any output -
#      the number matches the fact (catches "Two samples are late" on one screen vs "4 samples late" on another)
#   3. raw data on screen: [] {} null undefined NaN {{template}}
#   4. sentences that claim an action ("sends", "updates", "approving runs...") with nothing cued on screen
#   5. internal notes in customer-facing outputs (PDF/PPTX/SRT text and speaker notes)
# What it cannot judge - whether an AI panel contradicts a record, whether a claim matches the buttons on screen -
# is the reviewer's job: review/check.md lists each scene's narration next to its screen text for that read.
import json, os, re, glob, subprocess, sys

brief = json.load(open("brief.json")); story = json.load(open("story.json"))
facts = json.load(open("facts.json")) if os.path.exists("facts.json") else []
narr = json.load(open("build/narration.json")) if os.path.exists("build/narration.json") else {}
scenes = [(a, s) for a in story["acts"] for s in a["scenes"]]
screen = {s["id"]: open(f"build/text/{s['id']}.txt").read() for _, s in scenes if os.path.exists(f"build/text/{s['id']}.txt")}

UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9,
       "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15, "sixteenth": 16,
       "seventeenth": 17, "eighteenth": 18, "nineteenth": 19, "twentieth": 20, "thirtieth": 30}
NUMW = set(UNITS) | set(TENS) | set(ORD) | {"hundred", "thousand", "million", "and"}

def spoken_numbers(text):
    """Numbers in a sentence, whether written as digits or words: 'one hundred and eighteen' -> 118."""
    out = [float(x.replace(",", "")) for x in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", text)]
    words = re.findall(r"[a-z]+|[^a-z\s]", text.lower()); i = 0
    while i < len(words):
        if words[i] in NUMW and words[i] != "and":
            total, cur, j = 0, 0, i
            while j < len(words) and words[j] in NUMW:
                w = words[j]
                if w in UNITS: cur += UNITS[w]
                elif w in TENS: cur += TENS[w]
                elif w in ORD: cur += ORD[w]
                elif w == "hundred": cur = max(cur, 1) * 100
                elif w in ("thousand", "million"): total += max(cur, 1) * (1000 if w == "thousand" else 10**6); cur = 0
                j += 1
            if words[j - 1] == "and": j -= 1
            out.append(float(total + cur)); i = j
        else: i += 1
    return out

def screen_numbers(text):
    vals = set()
    for x in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        v = float(x.replace(",", "")); vals |= {v, float(round(v)), float(int(v))}
    return vals

IDIOM = {0.0, 1.0}  # "one place", "one click", "one inbox": too common to check
fact_vals = {float(f["value"]) for f in facts if isinstance(f.get("value"), (int, float))}
must, verify, info = [], [], []

# 1. numbers in the narration vs the screen it plays over
for a, s in scenes:
    if s["id"] not in screen: verify.append(f"{s['id']}: no screen text yet (run capture)"); continue
    on = screen_numbers(screen[s["id"]])
    for v in spoken_numbers(s["narration"]):
        if v in IDIOM or v in on or v in fact_vals: continue
        must.append(f"{s['id']}: the voice says **{v:g}**, which is not on this screen. Narration: \"{s['narration'][:140]}…\"")

# 2. facts: same thing, same number, everywhere
texts = {f"screen {k}": v for k, v in screen.items()}
texts.update({f"narration {s['id']}": s["narration"] for _, s in scenes})
outs = {}
for f in glob.glob("out/*.pdf"):
    try: outs[f] = subprocess.run(["pdftotext", "-layout", f, "-"], capture_output=True, text=True).stdout
    except FileNotFoundError: info.append("pdftotext not installed: PDFs not scanned")
for f in glob.glob("out/*.pptx"):
    from pptx import Presentation
    p = Presentation(f); chunks = []
    for i, sl in enumerate(p.slides, 1):
        for sh in sl.shapes:
            if sh.has_text_frame: chunks.append(sh.text_frame.text)
        if sl.has_notes_slide: chunks.append(f"[slide {i} speaker notes] " + sl.notes_slide.notes_text_frame.text)
    outs[f] = "\n".join(chunks)
for f in glob.glob("out/*.srt"): outs[f] = open(f).read()
texts.update(outs)
for fct in facts:
    for phrase in fct.get("phrases", []):
        pat = re.compile(r"((?:[\w.,£$€%-]+\s+){0,3})" + re.escape(phrase.lower()))
        for where, txt in texts.items():
            for m in pat.finditer(txt.lower()):
                nums = spoken_numbers(m.group(1))
                if nums and nums[-1] != float(fct["value"]):
                    must.append(f"{where}: \"…{m.group(0).strip()}…\" says {nums[-1]:g}, but fact `{fct['id']}` is {fct['value']} ({fct.get('source', 'facts.json')})")

# 3. raw data leaking onto screens
RAW = re.compile(r"(?:^|\s)(\[\]|\{\}|null|undefined|NaN|\[object Object\]|\{\{[^}]*\}\}|Invalid Date)(?=\s|$)")
for k, txt in screen.items():
    for m in RAW.finditer(txt): must.append(f"screen {k}: raw value `{m.group(1)}` is visible on screen")

# 4. told, not shown
CLAIM = re.compile(r"\b(moves?|updates?|sends?|sent|approv(?:e|es|ing)|exports?|logs?|runs?|syncs?|notif(?:y|ies)|creates?|generates?|books?|submits?)\b", re.I)
for a, s in scenes:
    sents = [x for x in re.split(r"(?<=[.!?])\s+", s["narration"]) if x]
    cued = [x["at"] for x in s.get("actions", []) if x.get("at")]
    for x in sents:
        if CLAIM.search(x) and not any(c in x for c in cued):
            verify.append(f"{s['id']}: told, not shown? \"{x}\" (nothing on screen is cued in this sentence; show it, or check the screen has the button/state that makes it true)")

# 5. internal notes in what the customer will receive
INTERNAL = re.compile(r"\b(error|bug|fix(?:ed|es)?|todo|tbd|fixme|uat|staging|preview|localhost|sandbox|model connection|not shown|workaround|hack|internal only|confirm (?:the wording|with)|placeholder|lorem|dummy)\b", re.I)
extra = [t.lower() for t in brief.get("internal_terms", [])]
mail = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
for f, txt in outs.items():
    for ln in txt.splitlines():
        hit = INTERNAL.search(ln) or any(t in ln.lower() for t in extra) or (mail.search(ln) and brief.get("share") != "internal")
        if hit: must.append(f"{os.path.basename(f)}: internal note in a customer file: \"{ln.strip()[:160]}\"")

os.makedirs("review", exist_ok=True)
with open("review/check.md", "w") as r:
    r.write(f"# Consistency check\n\n**{len(must)} must fix · {len(verify)} to verify**\n\n## Must fix\n\n")
    r.write("\n".join(f"- {x}" for x in must) or "- none"); r.write("\n\n## Verify\n\n")
    r.write("\n".join(f"- {x}" for x in verify) or "- none"); r.write("\n\n")
    if info: r.write("## Notes\n\n" + "\n".join(f"- {x}" for x in info) + "\n\n")
    r.write("## Read as the viewer (do this yourself, every version)\n\nFor each scene: does anything on this screen contradict the voice, "
            "an earlier screen, or another panel on the same screen (an AI summary vs the record it summarises; a status vs a date; "
            "a claim like \"sends it\" vs the buttons that exist)? Would someone who runs this business believe every sentence?\n\n")
    for a, s in scenes:
        r.write(f"### {s['id']} · {s.get('title', '')}\n\n**Voice:** {s['narration']}\n\n**Screen text:**\n\n~~~\n{screen.get(s['id'], '(not captured)')[:2500]}\n~~~\n\n")
print(f"review/check.md: {len(must)} must fix, {len(verify)} to verify")
sys.exit(1 if must else 0)
```

### `kit/brand.py`

```python
# kit/brand.py: pull the theme out of the UnifyApps template so every collateral matches it.
# usage: python3 kit/brand.py path/to/UnifyApps_template.pptx
# writes brand/tokens.json, brand/logo.png, brand/template.pptx (a copy; the original is never touched)
import sys, json, re, zipfile, shutil, os
src = sys.argv[1]; os.makedirs("brand", exist_ok=True)
shutil.copy(src, "brand/template.pptx")
z = zipfile.ZipFile(src)
theme = z.read("ppt/theme/theme1.xml").decode()
scheme = dict(re.findall(r'<a:(dk1|lt1|dk2|lt2|accent\d|hlink)><a:srgbClr val="(\w{6})"', theme))
# Defaults below are the values of the current template; the scheme read above overrides where it says so.
tok = {
  "canvas_from": "#FFFFFF", "canvas_to": "#" + scheme.get("lt2", "F7F3ED"),
  "ink": "#0F2805", "emphasis": "#" + scheme.get("dk1", "847347"), "body": "#3D3829",
  "olive": "#" + scheme.get("dk2", "4E582D"), "olive_2": "#" + scheme.get("accent4", "828750"),
  "card": "#FCFAF5", "card_line": "#C3B9A8", "disc": "#" + scheme.get("lt1", "EDE6D7"),
  "sand": "#" + scheme.get("accent5", "C5BAA9"), "sand_2": "#" + scheme.get("accent6", "E3D8C2"),
  "alert_fill": "#F8ECE8", "alert_line": "#DDB9B2", "alert_text": "#AF4C44",
  "font": "Spectral", "tagline": "Intelligence that compounds",
  "footer": "Agentic Automation for the Enterprise   ·   Strictly Confidential",
}
# The logo is the wide image on the slide layout (the footer wordmark).
from PIL import Image; import io
best = None
for n in z.namelist():
    if re.match(r"ppt/slideLayouts/_rels/.*\.rels", n):
        for t in re.findall(r'Target="\.\./media/([^"]+)"', z.read(n).decode()):
            im = Image.open(io.BytesIO(z.read("ppt/media/" + t)))
            if im.width > 2 * im.height and (best is None or im.width > best[1].width): best = (t, im)
if best: best[1].save("brand/logo.png"); print("logo:", best[0], best[1].size)
json.dump(tok, open("brand/tokens.json", "w"), indent=2); print(json.dumps(tok, indent=2))
```

### `kit/render.mjs`

```js
// kit/render.mjs: HTML in the template theme -> PNG or PDF. Used by cards, docs and swimlanes.
import fs from 'node:fs';
import path from 'node:path';
import { launch, readJSON } from './lib.mjs';

const T = readJSON('brand/tokens.json');
const F = path.resolve('fonts');
const face = (file, w, st = 'normal') => `@font-face{font-family:Spectral;src:url("file://${F}/${file}");font-weight:${w};font-style:${st}}`;
export const CSS = `
${face('Spectral-Light.ttf', 300)}${face('Spectral-Regular.ttf', 400)}${face('Spectral-Italic.ttf', 400, 'italic')}
${face('Spectral-Medium.ttf', 500)}${face('Spectral-MediumItalic.ttf', 500, 'italic')}${face('Spectral-SemiBold.ttf', 600)}
:root{--ink:${T.ink};--em:${T.emphasis};--body:${T.body};--olive:${T.olive};--olive2:${T.olive_2};--card:${T.card};
--line:${T.card_line};--disc:${T.disc};--sand:${T.sand};--sand2:${T.sand_2};--afill:${T.alert_fill};--aline:${T.alert_line};--atext:${T.alert_text}}
*{box-sizing:border-box;margin:0;padding:0}
html,body{font-family:Spectral,serif;color:var(--body);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.canvas{background:radial-gradient(circle at 0% 0%, ${T.canvas_from} 0%, ${T.canvas_from} 41%, ${T.canvas_to} 100%)}
.eyebrow{font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--em)}
h1,.h1{font-weight:300;color:var(--ink);line-height:1.08}
h1 em,.h1 em{font-weight:500;font-style:italic;color:var(--em)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px}
.disc{border-radius:50%;background:var(--disc);display:grid;place-items:center;color:var(--em)}
.alert{background:var(--afill);border:1px solid var(--aline);color:var(--atext);border-radius:12px}
.footer{position:absolute;left:0;right:0;bottom:0;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;color:var(--em)}
.footer span:last-child{text-align:right}
.footer img{height:1.2em;vertical-align:middle}
`;
export const logo = () => (fs.existsSync('brand/logo.png') ? `file://${path.resolve('brand/logo.png')}` : '');
export const footer = (page = '', scale = 1) => `<div class="footer" style="padding:0 ${40 * scale}px ${22 * scale}px;font-size:${11 * scale}px">
  <span><img src="${logo()}" style="height:${18 * scale}px"> &nbsp;·&nbsp; ${T.tagline}</span><span>${T.footer}</span><span>${page}</span></div>`;
// "Lead: *emphasis*." -> Lead: <em>emphasis</em>;  **bold** -> <b>bold</b>. Bold first, so ** never leaks as *.
export const md = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/\*([^*]+)\*/g, '<em>$1</em>');

let browser;
async function page(html, w, h) {
  browser ??= await launch();
  const p = await browser.newPage({ viewport: { width: w, height: h } });
  fs.mkdirSync('build/html', { recursive: true });
  const f = path.resolve(`build/html/${Date.now()}_${Math.random().toString(36).slice(2)}.html`);
  fs.writeFileSync(f, `<!doctype html><meta charset="utf-8"><style>${CSS}</style>${html}`);
  await p.goto(`file://${f}`); await p.evaluate(() => document.fonts.ready);
  const missing = await p.evaluate(() => !document.fonts.check('16px Spectral'));
  if (missing) console.warn('WARN Spectral not loaded: run the font install step');
  return p;
}
export async function png(html, out, w = 1920, h = 1080, transparent = false) {
  const p = await page(html, w, h); await p.screenshot({ path: out, omitBackground: transparent }); await p.close();
}
export async function pdf(html, out, opts = {}) {
  const p = await page(html, 1600, 1000);
  await p.pdf({ path: out, printBackground: true, preferCSSPageSize: true, ...opts }); await p.close();
}
export async function done() { await browser?.close(); browser = null; }
```

### `kit/cards.mjs`

```js
// kit/cards.mjs: opening, act and closing cards + the "Powered and built by UnifyApps" badge, in the theme.
// usage: node kit/cards.mjs   -> build/cards/*.png, build/cards/badge.png
import fs from 'node:fs';
import { png, done, footer, md } from './render.mjs';
import { readJSON as rj } from './lib.mjs';

const story = rj('story.json'), brief = rj('brief.json');
fs.mkdirSync('build/cards', { recursive: true });
const frame = (inner) => `<div class="canvas" style="width:1920px;height:1080px;position:relative;padding:150px 170px">${inner}${footer('', 2)}</div>`;

const o = story.opening ?? {};
await png(frame(`
  <div class="eyebrow" style="font-size:30px">${md(o.eyebrow ?? `${brief.customer} · Proof of concept`)}</div>
  <h1 style="font-size:104px;margin-top:34px;max-width:1500px">${md(o.title ?? story.title)}</h1>
  <p style="font-size:38px;margin-top:40px;max-width:1300px;line-height:1.4">${md(o.subtitle ?? '')}</p>`), 'build/cards/opening.png');

for (const [i, a] of story.acts.entries())
  await png(frame(`
    <div class="eyebrow" style="font-size:30px">Act ${i + 1} of ${story.acts.length}</div>
    <h1 style="font-size:96px;margin-top:34px;max-width:1500px">${md(a.card ?? a.title)}</h1>
    <p style="font-size:38px;margin-top:40px;max-width:1300px;line-height:1.4">${md(a.goal ?? '')}</p>`), `build/cards/act_${a.id}.png`);

const c = story.closing ?? {};
await png(frame(`
  <div class="eyebrow" style="font-size:30px">${md(c.eyebrow ?? 'What this means')}</div>
  <h1 style="font-size:96px;margin-top:34px;max-width:1500px">${md(c.title ?? 'Built on *UnifyApps*.')}</h1>
  <p style="font-size:38px;margin-top:40px;max-width:1300px;line-height:1.4">${md(c.subtitle ?? '')}</p>
  ${c.cta ? `<div style="display:inline-block;margin-top:56px;padding:22px 44px;border-radius:999px;background:var(--olive);color:#fff;font-size:34px;font-weight:600">${md(c.cta)}</div>` : ''}`), 'build/cards/closing.png');

await png(`<div style="display:inline-flex;align-items:center;gap:14px;padding:12px 24px;border-radius:999px;background:rgba(252,250,245,.94);
  border:1px solid var(--line);font-size:24px;color:var(--ink);font-weight:500">Powered and built by
  <span style="color:var(--em);font-weight:600;font-style:italic">UnifyApps</span></div>`, 'build/cards/badge.png', 420, 70, true);
await done();
console.log('cards written to build/cards/');
```

### `kit/build.py`

```python
# kit/build.py: acts + narration + cards + subtitles + badge -> out/<Slug>_Demo.mp4 and .srt
# Cuts and cross-dissolves only (no dip to black). No zoompan, no animated scale/crop: app footage is shown
# exactly as recorded. Subtitles move to the top of the frame whenever the thing being clicked or highlighted
# sits in the lower part of the screen, so a caption never covers what the voice is talking about.
# usage: python3 kit/build.py
import json, os, re, subprocess
import numpy as np

FPS, AR = 30, 48000
XF = 0.5             # cross-dissolve between segments (seconds)
LEAD = XF + 0.15     # still frames held before each act so the dissolve never eats footage or a word
LOW = 0.70           # a click/highlight below 70% of the frame height sends the caption to the top
brief = json.load(open("brief.json")); story = json.load(open("story.json"))
tl = json.load(open("build/timeline.json")); narr = json.load(open("build/narration.json"))
slug = brief["slug"]; os.makedirs("build/seg", exist_ok=True); os.makedirs("out", exist_ok=True)
log = open("build/build.log", "w")
def sh(*a):
    log.write(" ".join(map(str, a)) + "\n"); subprocess.run(["ffmpeg", "-y", "-v", "error", *map(str, a)], check=True)
def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", FPS,
       "-c:a", "aac", "-b:a", "192k", "-ar", AR, "-ac", 2]

def find_flash(video, est):
    """Return the time of the first frame after the magenta sync flash, or None."""
    start = max(0.0, est - 3)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", video, "-t", "6", "-vf", f"fps={FPS},scale=32:18",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 18, 32, 3).astype(int)
    hit = [(np.abs(f[..., 0] - 255) + f[..., 1] + np.abs(f[..., 2] - 255)).mean() < 60 for f in fr]
    return start + (max(i for i, h in enumerate(hit) if h) + 1) / FPS if any(hit) else None

def card(png, seconds, out):
    sh("-loop", 1, "-t", seconds, "-i", png, "-f", "lavfi", "-t", seconds, "-i", f"anullsrc=r={AR}:cl=stereo",
       "-vf", f"fps={FPS},format=yuv420p", *ENC, "-shortest", out)

def captions(text, d, start):
    """Split a scene's line into caption chunks (sentence, then clause if long), timed by length."""
    parts = []
    for s in [x for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x]:
        if len(s) <= 84: parts.append(s); continue
        chunk = ""
        for c in re.split(r"(?<=[,;:])\s+", s):
            if chunk and len(chunk) + len(c) > 84: parts.append(chunk); chunk = c
            else: chunk = f"{chunk} {c}".strip()
        if chunk: parts.append(chunk)
    total, pos, out = sum(len(x) for x in parts), 0, []
    for x in parts:
        a = start + d * pos / total; pos += len(x); out.append((a, start + d * pos / total, x))
    return out

segments, subs, placed, lows = [], [], {}, []
t = 0.0  # where the next segment starts in the final film (segments overlap by XF)
def add(f):
    global t
    start = t; segments.append((f, dur(f))); t = start + segments[-1][1] - XF; return start

card("build/cards/opening.png", story.get("opening", {}).get("seconds", 4), "build/seg/00_opening.mp4"); add("build/seg/00_opening.mp4")
for act in story["acts"]:
    a = tl[act["id"]]
    card(f"build/cards/act_{act['id']}.png", act.get("card_seconds", 3), f"build/seg/{act['id']}_0card.mp4")
    add(f"build/seg/{act['id']}_0card.mp4")
    flash = find_flash(a["video"], a["clock"])
    if flash is None: print(f"WARN act {act['id']}: no sync flash found; using recorded clock (audio may drift by ~0.2 s)")
    else: print(f"act {act['id']}: synced on the flash ({flash - a['clock']:+.2f} s)")
    v0 = flash if flash is not None else a["clock"]; length = a["end"] - a["clock"]
    act_start = t  # film time of this act segment's first frame
    inputs, chains = ["-ss", v0, "-t", length, "-i", a["video"]], []
    for i, s in enumerate(a["scenes"], start=1):
        voice = s.get("voice", s["start"])
        ms = int((max(0, voice - a["clock"]) + LEAD) * 1000)
        inputs += ["-i", f"build/audio/{s['id']}.wav"]
        chains.append(f"[{i}:a]aresample={AR},aformat=channel_layouts=stereo,adelay={ms}:all=1[a{i}]")
        sc = next(x for x in act["scenes"] if x["id"] == s["id"])
        f0 = act_start + ms / 1000; film = lambda x: act_start + LEAD + (x - a["clock"])
        placed[s["id"]] = {"act": act["id"], "start": round(film(s["start"]), 2), "voice": round(f0, 2),
                           "end": round(film(s["end"]), 2),
                           "cues": {k: round(f0 + v, 2) for k, v in narr[s["id"]]["cues"].items()}}
        lows += [(film(m["t"]), film(m["t"]) + 3.0) for m in s.get("marks", []) if m["y1"] > LOW * 1080]
        subs += captions(sc["narration"], narr[s["id"]]["dur"], f0)
    n = len(a["scenes"])
    mix = "".join(f"[a{i}]" for i in range(1, n + 1)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad[aout]"
    out = f"build/seg/{act['id']}_1act.mp4"
    sh(*inputs, "-filter_complex", ";".join(chains + [mix]), "-map", "0:v", "-map", "[aout]",
       "-vf", f"fps={FPS},scale=1920:1080,format=yuv420p,tpad=start_duration={LEAD}:start_mode=clone",
       *ENC, "-t", length + LEAD, out)
    add(out)
card("build/cards/closing.png", story.get("closing", {}).get("seconds", 5), "build/seg/99_closing.mp4"); add("build/seg/99_closing.mp4")

json.dump(placed, open("build/placed.json", "w"), indent=2)  # where each scene sits in the final film (for review)
def ts(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f"{int(h):02}:{int(m):02}:{s:06.3f}".replace(".", ",")
srt = f"out/{slug}_Demo.srt"
with open(srt, "w") as f:  # clean SRT for upload / players
    for i, (a, b, x) in enumerate(subs, 1): f.write(f"{i}\n{ts(a)} --> {ts(b - 0.05)}\n{x}\n\n")
burn = "build/burn.srt"; up = 0; AN8 = "{\\an8}"  # libass: anchor top-centre
with open(burn, "w") as f:  # the burned-in copy: top-anchored where the action is low on screen
    for i, (a, b, x) in enumerate(subs, 1):
        top = any(lo < b and hi > a for lo, hi in lows); up += top
        f.write(f"{i}\n{ts(a)} --> {ts(b - 0.05)}\n{AN8 if top else ''}{x}\n\n")
print(f"captions: {len(subs)}, {up} moved to the top to keep the action visible")

T = json.load(open("brand/tokens.json"))
def ass(hexc, alpha="00"): h = hexc.lstrip("#"); return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}"
style = (f"FontName=Spectral,FontSize=12,PrimaryColour={ass(T['ink'])},OutlineColour={ass(T['card'], '18')},"
         f"BackColour={ass(T['card'], '18')},BorderStyle=3,Outline=6,Shadow=0,MarginV=26,MarginL=40,MarginR=40")
ins, vch, ach = [], [], []
for k, (f, d) in enumerate(segments): ins += ["-i", f]
off, prev_v, prev_a = 0.0, "[0:v]", "[0:a]"
for k in range(1, len(segments)):
    off += segments[k - 1][1] - XF
    vch.append(f"{prev_v}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{k}]"); prev_v = f"[v{k}]"
    ach.append(f"{prev_a}[{k}:a]acrossfade=d={XF}[a{k}]"); prev_a = f"[a{k}]"
nb = len(segments)
sub = f"{prev_v}subtitles={burn}:fontsdir=fonts:force_style='{style}'[s]" if brief.get("subtitles", True) else f"{prev_v}null[s]"
final = f"out/{slug}_Demo.mp4"
sh(*ins, "-i", "build/cards/badge.png", "-filter_complex", ";".join(vch + ach + [sub, f"[s][{nb}:v]overlay=W-w-28:H-h-22[v]"]),
   "-map", "[v]", "-map", prev_a, *ENC, "-movflags", "+faststart", final)
spoken = sum(narr[s["id"]]["dur"] for a in story["acts"] for s in a["scenes"] if s["id"] in narr); film_len = dur(final)
print(f"{final}: {film_len/60:.1f} min film, {spoken/60:.1f} min narration ({film_len-spoken:.0f} s of cards + silence)")
```

### `kit/review.py`

```python
# kit/review.py: the review pass for version N. Pulls a frame at every scene's middle and at every cue,
# makes a contact sheet, runs the automatic checks (timing, loading screens, kit/check.py consistency gate),
# and writes review/v<N>/report.md with the coverage matrix for you to complete by LOOKING at every frame.
# usage: python3 kit/review.py 1
import json, os, sys, subprocess, re
from PIL import Image, ImageDraw, ImageFont

n = sys.argv[1]; d = f"review/v{n}"; os.makedirs(f"{d}/frames", exist_ok=True)
brief = json.load(open("brief.json")); story = json.load(open("story.json")); cov = json.load(open("coverage.json"))
placed = json.load(open("build/placed.json")); narr = json.load(open("build/narration.json"))
film = f"out/{brief['slug']}_Demo.mp4"
def grab(t, out):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", film, "-frames:v", "1", "-q:v", "3", out], check=True)

frames = []
for act in story["acts"]:
    for sc in act["scenes"]:
        p = placed.get(sc["id"])
        if not p: frames.append((sc["id"], "NOT RECORDED", None)); continue
        marks = [((p["start"] + p["end"]) / 2, "middle", "mid")] + [(t + 0.9, f'cue "{k}"', re.sub(r'[^a-z0-9]+', '_', k.lower())[:30])
                 for k, t in p["cues"].items()] + [(p["end"] - 0.3, "end", "end")]
        for t, what, tag in sorted(marks):  # in film order
            f = f"{d}/frames/{sc['id']}_{t:07.2f}_{tag}.jpg"; grab(t, f); frames.append((sc["id"], what, f))

# contact sheet, 4 across
shots = [x for x in frames if x[2]]; cols, tw, th = 4, 480, 270
sheet = Image.new("RGB", (cols * tw, ((len(shots) + cols - 1) // cols) * (th + 28)), "#F7F3ED"); dr = ImageDraw.Draw(sheet)
for i, (sid, what, f) in enumerate(shots):
    x, y = (i % cols) * tw, (i // cols) * (th + 28)
    sheet.paste(Image.open(f).resize((tw - 8, th - 8)), (x + 4, y + 4)); dr.text((x + 8, y + th), f"{sid} · {what}", fill="#0F2805")
sheet.save(f"{d}/contact_sheet.jpg", quality=85)

# automatic checks
issues = []
logs = "".join(open(f"build/{x}.log").read() for x in ("record", "build") if os.path.exists(f"build/{x}.log"))
for l in logs.splitlines():
    m = re.match(r"LATE CUE .* by ([\d.]+) s", l)
    if m and float(m.group(1)) >= 1.2: issues.append("MUST FIX (the glow lands after the words): " + l)
    elif re.match(r"(OVERRUN|FAIL|SLOW)", l): issues.append("MUST FIX: " + l)
    elif re.match(r"(LATE CUE|GOTO|WARN)", l): issues.append(l)
chk = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "check.py")], capture_output=True, text=True)
issues.append(("MUST FIX: " if chk.returncode else "") + "consistency gate: " + chk.stdout.strip() + " (details in review/check.md)")
if os.path.exists("review/check.md"): import shutil; shutil.copy("review/check.md", f"{d}/check.md")
if os.path.exists("build/build.log") and "zoompan" in open("build/build.log").read(): issues.append("zoompan found in the ffmpeg graph: forbidden")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", film], capture_output=True, text=True).stdout)
spoken = sum(narr[s["id"]]["dur"] for a in story["acts"] for s in a["scenes"] if s["id"] in narr)
cards = story.get("opening", {}).get("seconds", 4) + story.get("closing", {}).get("seconds", 5) + sum(a.get("card_seconds", 3) for a in story["acts"])
silence = dur - spoken - cards
if silence > 0.15 * spoken: issues.append(f"{silence:.0f} s of silence on app footage (>{0.15*spoken:.0f} s): tighten actions or pads")

scene_of = {s["id"]: s for a in story["acts"] for s in a["scenes"]}
with open(f"{d}/report.md", "w") as r:
    r.write(f"# Review v{n}: {brief['customer']} · {brief['poc']}\n\nFilm {dur/60:.1f} min · narration {spoken/60:.1f} min · persona {brief['persona']} · voice {brief['voice']}\n\n")
    r.write("## Coverage (fill Status after looking at each frame: shown / missing / wrong screen / unclear)\n\n")
    r.write("| Feature | Screen | Scenes | Frames | Video | Walkthrough | Deck | Swimlane |\n|---|---|---|---|---|---|---|---|\n")
    for c in cov:
        sc = [s for s, v in scene_of.items() if c["id"] in v.get("covers", [])]
        fr = ", ".join(os.path.basename(f) for s in sc for (sid, _, f) in frames if sid == s and f)
        r.write(f"| {c['id']} {c['feature']} | {c['screen']} | {', '.join(sc) or '**none**'} | {fr} | ? | ? | ? | ? |\n")
    r.write("\n## Automatic findings\n\n" + ("\n".join(f"- {i}" for i in issues) or "- none") + "\n")
    r.write("\n## Visual findings (navigation that teleports, dead air, wrong highlight, cut-off line, font fallback)\n\n- \n")
print(f"{d}/report.md, {len(shots)} frames, contact sheet {d}/contact_sheet.jpg, {len(issues)} automatic finding(s)")
```

### `kit/swimlanes.mjs`

```js
// kit/swimlanes.mjs: swimlanes.json -> out/swimlane_<view>.png (16:9, for the deck and walkthrough)
// and out/<Slug>_Swimlanes.pdf (one page per view), in the template theme.
// usage: node kit/swimlanes.mjs
import { png, pdf, done, footer, md } from './render.mjs';
import { readJSON } from './lib.mjs';

const brief = readJSON('brief.json'), sl = readJSON('swimlanes.json'), story = readJSON('story.json');
const scenes = new Set(story.acts.flatMap((a) => a.scenes.map((s) => s.id)));
const W = 1920, H = 1080, TOP = 210, BOT = 990, LH = 240, PADX = 50;
const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const STATUS = { live: 'Live', simulated: 'Simulated in POC', golive: 'Connected at go-live' };

function view(v, deck = false) {
  for (const s of v.steps) if (s.scene && !scenes.has(s.scene)) console.warn(`WARN ${v.id}/${s.id}: scene ${s.scene} not in story.json`);
  if (v.id !== 'today') for (const s of v.steps) if (!s.scene && s.kind !== 'system') console.warn(`WARN ${v.id}/${s.id}: no scene; every step must be shown in the demo or come from discovery`);
  const laneKind = Object.fromEntries(sl.lanes.map((l) => [l.id, l.kind]));
  for (const s of v.steps) s.kind ??= laneKind[s.lane] === 'unifyapps' ? 'auto' : laneKind[s.lane] === 'system' ? 'system' : 'manual';
  const lanes = sl.lanes.filter((l) => v.steps.some((s) => s.lane === l.id));
  const laneH = (BOT - TOP) / lanes.length, row = Object.fromEntries(lanes.map((l, i) => [l.id, i]));
  for (const [i, s] of v.steps.entries()) if (s.parallel && s.after) console.warn(`WARN ${v.id}/${s.id}: "parallel" with "after"; a step that needs another's output goes in a later column`);
  let c = -1; const col = {};
  for (const s of v.steps) col[s.id] = s.col ?? (s.parallel ? c : ++c);
  const ncol = Math.max(...Object.values(col)) + 1, colW = (W - PADX * 2 - LH) / ncol;
  const cw = Math.min(260, colW - 44), ch = Math.min(118, laneH - 54);
  const pos = {};
  for (const s of v.steps) pos[s.id] = { x: PADX + LH + col[s.id] * colW + (colW - cw) / 2, y: TOP + row[s.lane] * laneH + (laneH - ch) / 2 - (s.pain ? 14 : 0) };
  // Default flow: each main step -> the next main step. A "parallel" step shares the column of the main step
  // before it, takes the same input and feeds the same output. "next": [...] overrides any of this.
  const main = v.steps.filter((s) => !s.parallel), auto = {};
  main.forEach((s, i) => { auto[s.id] = main[i + 1] ? [main[i + 1].id] : []; });
  v.steps.forEach((s, i) => { if (!s.parallel) return;
    const q = [...v.steps.slice(0, i)].reverse().find((x) => !x.parallel); if (!q) return;
    const pred = main[main.indexOf(q) - 1]; if (pred) auto[pred.id].push(s.id);
    auto[s.id] = [...auto[q.id]]; });
  const edges = [], lanesUsed = {};
  v.steps.forEach((s) => {
    const nx = s.next ?? auto[s.id] ?? [];
    for (const t of nx) {
      const key = col[s.id]; lanesUsed[key] = (lanesUsed[key] ?? -1) + 1; const lane = lanesUsed[key];
      const a = pos[s.id], b = pos[t]; if (!b) continue;
      const handoff = s.lane !== v.steps.find((x) => x.id === t).lane;
      const auto = [s.kind, v.steps.find((x) => x.id === t).kind].some((k) => k === 'ai' || k === 'auto');
      const x1 = a.x + cw, y1 = a.y + ch / 2, x2 = b.x, y2 = b.y + ch / 2;
      const mx = Math.min(x2 - 16, x1 + 18 + lane * 12); // vertical run close to the source, offset per edge
      const d = Math.abs(y1 - y2) < 2 ? `M${x1},${y1} L${x2 - 10},${y2}` : `M${x1},${y1} L${mx},${y1} L${mx},${y2} L${x2 - 10},${y2}`;
      edges.push(`<path d="${d}" fill="none" stroke="${auto ? 'var(--olive)' : 'var(--sand)'}" stroke-width="${auto ? 3 : 2.5}"
        ${handoff && !auto ? 'stroke-dasharray="9 7"' : ''} marker-end="url(#${auto ? 'ah2' : 'ah'})"/>`);
    }
  });
  const card = (s) => {
    const p = pos[s.id], k = s.kind ?? 'manual';
    const st = k === 'ai' ? 'background:var(--olive);color:#fff;border-color:var(--olive)'
      : k === 'auto' ? 'background:#E9ECDD;color:var(--ink);border:1.5px solid var(--olive)'
      : k === 'system' ? 'background:var(--sand2);color:var(--ink);border-color:var(--sand)'
      : k === 'decision' ? 'border:2px dashed var(--em)' : '';
    return `<div class="card" style="position:absolute;left:${p.x}px;top:${p.y}px;width:${cw}px;height:${ch}px;padding:14px 16px;${st};
      display:flex;flex-direction:column;justify-content:center;font-size:${cw < 200 ? 17 : 19}px;line-height:1.25">
      ${k === 'ai' || k === 'auto' ? `<div style="font-size:13px;letter-spacing:.08em;font-weight:600;opacity:.8;margin-bottom:4px">${k === 'ai' ? 'AI' : 'AUTOMATED'} · UNIFYAPPS</div>` : ''}
      <div style="font-weight:${k === 'ai' ? 500 : 500};color:${k === 'ai' ? '#fff' : 'var(--ink)'}">${md(s.text)}</div>
      ${s.note ? `<div style="font-size:14px;margin-top:4px;opacity:.85">${md(s.note)}</div>` : ''}</div>
      ${s.pain ? `<div class="alert" style="position:absolute;left:${p.x}px;top:${p.y + ch + 8}px;width:${cw}px;padding:5px 10px;font-size:14px;line-height:1.2">● ${md(s.pain)}</div>` : ''}`;
  };
  const laneHtml = lanes.map((l, i) => `<div style="position:absolute;left:${PADX}px;top:${TOP + i * laneH}px;width:${W - PADX * 2}px;height:${laneH}px;
      border-top:1px solid var(--line);${i === lanes.length - 1 ? 'border-bottom:1px solid var(--line);' : ''}${l.kind === 'unifyapps' ? 'background:rgba(78,88,45,.05)' : ''}"></div>
    <div style="position:absolute;left:${PADX}px;top:${TOP + i * laneH + 8}px;width:${LH - 24}px;height:${laneH - 16}px;border-radius:12px;
      background:${l.kind === 'unifyapps' ? 'var(--olive)' : 'var(--disc)'};color:${l.kind === 'unifyapps' ? '#fff' : 'var(--ink)'};padding:0 18px;display:flex;flex-direction:column;justify-content:center">
      <div style="font-size:21px;font-weight:600">${esc(l.label)}</div>
      ${l.status ? `<div style="font-size:14px;margin-top:4px;color:${l.status === 'live' ? 'var(--olive)' : 'var(--em)'}">${STATUS[l.status] ?? esc(l.status)}</div>` : ''}</div>`).join('');
  return `<div class="${deck ? '' : 'canvas'}" style="width:${W}px;height:${H}px;position:relative">
    ${deck ? '' : `<div style="position:absolute;left:${PADX + 20}px;top:56px"><div class="eyebrow" style="font-size:20px">${esc(v.eyebrow ?? (v.id === 'today' ? 'How it works today' : 'How it works with UnifyApps'))}</div>
    <h1 style="font-size:54px;margin-top:10px">${md(v.title)}</h1></div>`}
    ${laneHtml}
    <svg width="${W}" height="${H}" style="position:absolute;left:0;top:0"><defs>
      <marker id="ah" markerWidth="10" markerHeight="10" refX="0" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--sand)"/></marker>
      <marker id="ah2" markerWidth="10" markerHeight="10" refX="0" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="var(--olive)"/></marker></defs>${edges.join('')}</svg>
    ${v.steps.map(card).join('')}
    ${deck ? '' : footer('', 1.6)}</div>`;
}

const pages = [];
for (const v of sl.views) {
  const h = view(v); pages.push(h); await png(h, `out/swimlane_${v.id}.png`); console.log(`out/swimlane_${v.id}.png`);
  await png(view(v, true), `build/swimlane_${v.id}_deck.png`, W, H, true); // transparent, no footer: the slide supplies both
}
await pdf(`<style>@page{size:1920px 1080px;margin:0}.pg{page-break-after:always}.pg:last-child{page-break-after:auto}</style>${pages.map((p) => `<div class="pg">${p}</div>`).join('')}`,
  `out/${brief.slug}_Swimlanes.pdf`);
console.log(`out/${brief.slug}_Swimlanes.pdf`);
await done();
```

### `kit/docs.mjs`

```js
// kit/docs.mjs: the demo script PDF and the walkthrough PDF, in the template theme (A4 landscape).
// usage: node kit/docs.mjs script | walkthrough | both
import fs from 'node:fs';
import path from 'node:path';
import { pdf, done, footer, md } from './render.mjs';
import { readJSON } from './lib.mjs';

const which = process.argv[2] ?? 'both';
const brief = readJSON('brief.json'), story = readJSON('story.json'), cov = readJSON('coverage.json', []);
const narr = readJSON('build/narration.json', {});
fs.mkdirSync('out', { recursive: true });
const img = (p) => (fs.existsSync(p) ? `file://${path.resolve(p)}` : null);
const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const secs = (s) => narr[s.id]?.dur ?? s.narration.split(/\s+/).length / 2.6;
const mmss = (x) => `${Math.floor(x / 60)}:${String(Math.round(x % 60)).padStart(2, '0')}`;
const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

const PAGE = `@page{size:297mm 210mm;margin:0}
.pg{width:297mm;height:210mm;position:relative;overflow:hidden;padding:16mm 18mm 20mm;page-break-after:always}
.pg:last-child{page-break-after:auto}
h1{font-size:34pt}h2{font-size:20pt;font-weight:400;color:var(--ink)}h2 em{font-style:italic;color:var(--em);font-weight:500}
.eyebrow{font-size:9pt;margin-bottom:3mm}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:8.6pt;line-height:1.35}
th{font-weight:600;color:var(--em);text-transform:uppercase;font-size:7.5pt;letter-spacing:.05em;text-align:left;padding:2mm;border-bottom:1px solid var(--line)}
td{padding:2.2mm 2mm;vertical-align:top;border-bottom:1px solid var(--sand2);color:var(--body)}
td.n{color:var(--em);font-weight:600;white-space:nowrap}
.tag{display:inline-block;padding:.3mm 1.6mm;border-radius:9px;background:var(--disc);color:var(--em);font-size:7pt;margin:0 1mm 1mm 0}
.k{font-size:8pt;color:var(--em);font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin:3mm 0 1mm}
.shot{width:100%;border-radius:8px;border:1px solid var(--line);display:block}`;

// Plain-English line for an action, used in the script's "On screen" column.
function says(a) {
  if (a.say) return a.say; // story can word any action for the script
  const t = a.target ?? a.to ?? {};
  const name = typeof t === 'string' ? '' : t.name ?? t.text ?? t.label ?? t.placeholder ?? '';
  const q = (n, fallback) => (n ? `“${n}”` : fallback);
  return { click: `Click ${q(name, 'the control')}`, hover: `Hover over ${q(name, 'the item')}`, type: `Type “${a.text}”`,
    press: `Press ${a.key}`, select: `Choose “${a.option}”`, scroll: a.to ? `Scroll to ${q(name, 'the section')}` : 'Scroll down',
    highlight: `Point out ${q(name, 'the section')}`, waitFor: '', settle: '', wait: '', goto: `Open ${a.url}`,
    custom: a.label ?? '' }[a.do] ?? '';
}

const cover = (title, sub) => `<div class="pg canvas" style="padding:34mm 26mm">
  <div class="eyebrow" style="font-size:11pt">${esc(brief.customer)} · ${esc(brief.poc)}</div>
  <h1 style="font-size:42pt;margin-top:6mm;max-width:220mm">${md(title)}</h1>
  <p style="font-size:14pt;margin-top:8mm;max-width:200mm;line-height:1.45">${md(sub)}</p>
  <p style="font-size:10pt;margin-top:14mm;color:var(--em)">Audience: ${esc(brief.persona_role ?? brief.persona)} (${esc(brief.persona)}) · Narration: US English, ${esc(brief.voice?.gender ?? 'female')} voice · ${date}</p>
  ${footer('', 1)}</div>`;

function covMatrix(firstPage) {
  const where = (id) => story.acts.flatMap((a) => a.scenes).filter((s) => (s.covers ?? []).includes(id)).map((s) => s.id);
  const PER = 9, pages = [];
  for (let i = 0; i < Math.max(cov.length, 1); i += PER) pages.push(cov.slice(i, i + PER));
  return pages.map((rows, k) => `<div class="pg canvas"><div class="eyebrow">Coverage${k ? ' (continued)' : ''}</div><h2>Every must-show feature, <em>and where it appears</em>.</h2>
  <table style="margin-top:6mm"><tr><th>ID</th><th>Screen</th><th>Feature</th><th>How to get there</th><th>Scenes</th><th>Shown in</th></tr>
  ${rows.map((c) => `<tr><td class="n">${c.id}</td><td>${esc(c.screen)}</td><td>${esc(c.feature)}</td><td>${esc((c.nav_path ?? []).join(' › '))}</td>
    <td>${where(c.id).join(', ') || '<b style="color:var(--atext)">none</b>'}</td><td>${(c.must_show_in ?? []).map((x) => `<span class="tag">${x}</span>`).join('')}</td></tr>`).join('')}
  </table>${footer(String(firstPage + k), 1)}</div>`).join('');
}

async function script() {
  let t = story.opening?.seconds ?? 4, pages = [], pg = 2;
  const rowH = (s) => Math.max(Math.ceil(s.narration.length / 95), (s.actions ?? []).map(says).filter(Boolean).length, 2) * 4.6 + 5; // mm
  for (const [i, a] of story.acts.entries()) {
    t += a.card_seconds ?? 3;
    const rows = a.scenes.map((s) => { const r = { h: rowH(s), html: `<tr><td class="n">${mmss(t)}</td><td><b style="color:var(--ink)">${esc(s.title)}</b><br><span style="color:var(--em)">${esc(s.lane ?? '')}</span></td>
      <td>${(s.actions ?? []).map(says).filter(Boolean).map(esc).join('<br>')}</td><td style="font-size:9.2pt">${esc(s.narration)}</td>
      <td>${(s.covers ?? []).map((c) => `<span class="tag">${c}</span>`).join('')}</td></tr>` }; t += secs(s) + 1.2; return r; });
    const chunks = [[]]; let used = 0;
    for (const r of rows) { if (used + r.h > 120 && chunks.at(-1).length) { chunks.push([]); used = 0; } chunks.at(-1).push(r); used += r.h; }
    chunks.forEach((c, k) => pages.push(`<div class="pg canvas"><div class="eyebrow">Act ${i + 1} of ${story.acts.length} · ${esc(brief.personas[a.persona]?.label ?? a.persona)}${k ? ' · continued' : ''}</div>
      <h2>${md(a.card ?? a.title)}</h2><p style="font-size:10pt;margin:2mm 0 5mm">${md(a.goal ?? '')}</p>
      <table><tr><th style="width:12mm">Time</th><th style="width:38mm">Scene</th><th style="width:58mm">On screen</th><th>Narration</th><th style="width:22mm">Covers</th></tr>${c.map((r) => r.html).join('')}</table>
      ${footer(String(pg++), 1)}</div>`));
  }
  const total = t + (story.closing?.seconds ?? 5);
  await pdf(`<style>${PAGE}</style>${cover(story.title, `Demo script for approval · ${story.acts.length} acts · about ${mmss(total)} minutes`)}${pages.join('')}${covMatrix(pg)}`,
    `out/${brief.slug}_Demo_Script.pdf`);
  console.log(`out/${brief.slug}_Demo_Script.pdf`);
}

async function walkthrough() {
  const lane = img('out/swimlane_with.png');
  const glance = `<div class="pg canvas"><div class="eyebrow">At a glance</div><h2>${md(story.title)}</h2>
    <div style="display:grid;grid-template-columns:${lane ? '1fr 1.25fr' : '1fr'};gap:8mm;margin-top:6mm">
    <div>${story.acts.map((a, i) => `<div class="card" style="padding:4mm 5mm;margin-bottom:3mm"><div class="k" style="margin:0">Act ${i + 1}</div>
      <div style="font-size:12pt;color:var(--ink);margin-top:1mm">${md(a.card ?? a.title)}</div><div style="font-size:9pt;margin-top:1mm">${md(a.goal ?? '')}</div></div>`).join('')}</div>
    ${lane ? `<div><img class="shot" src="${lane}"><div style="font-size:8pt;color:var(--em);margin-top:2mm">How the work flows with UnifyApps (full swimlanes in the companion PDF).</div></div>` : ''}
    </div>${footer('2', 1)}</div>`;
  let pg = 3; const pages = [];
  for (const [i, a] of story.acts.entries()) for (const s of a.scenes) {
    const w = s.walkthrough ?? {}, steps = (w.do ?? []);
    const stepHtml = steps.map((d, k) => { const sh = img(`build/shots/${s.id}_s${k + 1}.png`);
      return `<div style="display:grid;grid-template-columns:${sh ? '34mm 1fr' : '1fr'};gap:3mm;align-items:start;margin-bottom:2.5mm">
        ${sh ? `<img class="shot" src="${sh}">` : ''}<div style="font-size:9.2pt"><b style="color:var(--olive)">${k + 1}.</b> ${md(d)}</div></div>`; }).join('');
    const main = img(`build/shots/${s.id}.png`);
    pages.push(`<div class="pg canvas"><div class="eyebrow">Act ${i + 1} · ${esc(a.title)} · ${esc(s.lane ?? '')}</div><h2>${md(s.title)}</h2>
      <div style="display:grid;grid-template-columns:168mm 1fr;gap:7mm;margin-top:5mm">
        <div>${main ? `<img class="shot" src="${main}">` : '<div class="alert" style="padding:6mm">Screenshot missing: run capture</div>'}
          <div class="card" style="padding:3mm 4mm;margin-top:3mm;font-size:9pt"><span class="k">Why it matters</span><br>${md(w.why ?? '')}</div></div>
        <div><div class="k" style="margin-top:0">Do</div>${stepHtml}
          <div class="k">You'll see</div><div style="font-size:9.2pt">${md(w.expect ?? '')}</div>
          ${w.recover ? `<div class="k">If it doesn't</div><div style="font-size:9pt">${md(w.recover)}</div>` : ''}
          <div style="margin-top:3mm">${(s.covers ?? []).map((c) => `<span class="tag">${c} ${esc(cov.find((x) => x.id === c)?.feature ?? '')}</span>`).join('')}</div></div>
      </div>${footer(String(pg++), 1)}</div>`);
  }
  const internal = brief.share === 'internal';
  const live = [...new Set(cov.map((c) => c.screen.split(' · ')[0]))];
  const appx = `<div class="pg canvas"><div class="eyebrow">Appendix</div><h2>Running the demo <em>yourself</em>.</h2>
    <table style="margin-top:6mm"><tr><th>Role</th><th>Where</th><th>Sign in</th></tr>
    ${Object.values(brief.personas).map((p) => `<tr><td>${esc(p.label)}</td><td>${esc(internal ? p.url : p.public_url ?? 'Link provided with this guide')}</td>
      <td>${esc(internal ? p.username ?? 'no sign-in' : p.signin_note ?? 'Your account, provided separately')}</td></tr>`).join('')}</table>
    <div class="k" style="margin-top:6mm">Before you start</div><div style="font-size:9.5pt;line-height:1.5">${md(brief.reset ?? 'Use the demo data prepared for this POC.')}</div>
    <div class="k">Shown live in this guide</div><div style="font-size:9.5pt;line-height:1.5">${live.map(esc).join(' · ')}</div>
    <div class="k">Simulated in the POC, and connected at go-live</div><div style="font-size:9.5pt;line-height:1.5">${md(brief.limits ?? '')}</div>${footer(String(pg), 1)}</div>`;
  await pdf(`<style>${PAGE}</style>${cover(story.title, story.opening?.subtitle ?? 'Step-by-step walkthrough')}${glance}${pages.join('')}${appx}`,
    `out/${brief.slug}_Walkthrough.pdf`);
  console.log(`out/${brief.slug}_Walkthrough.pdf`);
}

if (which !== 'walkthrough') await script();
if (which !== 'script') await walkthrough();
await done();
```

### `kit/deck.py`

```python
# kit/deck.py: the PPT, built from the UnifyApps template. Every slide is a copy of one of the template's
# own slides (so master, background, footer, fonts and spacing carry over) with its text and pictures swapped.
#   python3 kit/deck.py --inspect      list every template slide's text slots (T#) and pictures (P#)
#   python3 kit/deck.py                build out/<Slug>_Deck.pptx from deck.json
# deck.json: {"slides": [
#   {"from": 1, "text": {"T0": "EYEBROW", "T1": ["Lead: ", "italic olive part", "."], "Merchandiser": "..."},
#    "images": {"P0": "lucide:camera", "P9": "build/shots/a2.png"}, "notes": "speaker notes"},
#   {"image": "build/swimlane_with_deck.png", "from": 1, "text": {"T0": "...", "T1": [...]}} ]}
# An image value can be {"path": "...", "y": 0.4} to choose which band of a tall screenshot fills a wide frame.
# Text keys are a slot id (T#) or a unique sample text. A list fills the runs in order (keeps the italic olive run).
# "lucide:<name>" renders that line icon in the colour of the icon it replaces. Screenshots are cropped to fill.
import sys, json, copy, io, os, re
from pptx import Presentation
from pptx.util import Emu
from PIL import Image

TPL = "brand/template.pptx"
def slots(slide):
    T, P = [], []
    for sh in sorted(slide.shapes, key=lambda s: (s.top or 0, s.left or 0)):
        if sh.shape_type == 13: P.append(sh)
        elif sh.has_text_frame and sh.text_frame.text.strip(): T.append(sh)
    return T, P

if "--inspect" in sys.argv:
    prs = Presentation(TPL)
    for i, s in enumerate(prs.slides, 1):
        T, P = slots(s); print(f"\n=== template slide {i}")
        for k, sh in enumerate(T):
            runs = [r.text for p in sh.text_frame.paragraphs for r in p.runs]
            print(f"  T{k:<3} {'|'.join(runs)[:90]!r}")
        for k, sh in enumerate(P):
            print(f"  P{k:<3} {Emu(sh.width).inches:.2f}x{Emu(sh.height).inches:.2f}in at ({Emu(sh.left).inches:.2f},{Emu(sh.top).inches:.2f})")
    sys.exit()

brief = json.load(open("brief.json")); spec = json.load(open("deck.json"))
prs = Presentation(TPL); originals = list(prs.slides)

def duplicate(src):
    dst = prs.slides.add_slide(src.slide_layout)
    for ph in list(dst.placeholders): ph._element.getparent().remove(ph._element)
    rid = {}
    for r in src.part.rels.values():
        if "image" in r.reltype: rid[r.rId] = dst.part.relate_to(r._target, r.reltype)
    for el in src.shapes._spTree.iterchildren():
        if el.tag.endswith(("}sp", "}pic", "}grpSp", "}cxnSp", "}graphicFrame")):
            x = copy.deepcopy(el); xml = None
            for b in x.iter():
                for k, v in list(b.attrib.items()):
                    if k.endswith("}embed") and v in rid: b.set(k, rid[v])
            dst.shapes._spTree.append(x)
    return dst

def set_text(sh, val):
    runs = [r for p in sh.text_frame.paragraphs for r in p.runs]
    vals = val if isinstance(val, list) else [val]
    for i, r in enumerate(runs): r.text = vals[i] if i < len(vals) else ""
    if len(vals) > len(runs): runs[-1].text += "".join(vals[len(runs):])

def colour_of(pic):
    import numpy as np
    a = np.asarray(Image.open(io.BytesIO(pic.image.blob)).convert("RGBA")).reshape(-1, 4)
    a = a[a[:, 3] > 200][:, :3]
    if not len(a): return "#847347"
    v, c = np.unique(a, axis=0, return_counts=True); return "#%02x%02x%02x" % tuple(v[c.argmax()])

def icon_png(name, colour, size=192):
    import cairosvg
    f = f"node_modules/lucide-static/icons/{name}.svg"
    if not os.path.exists(f):
        near = [x[:-4] for x in os.listdir(os.path.dirname(f)) if name.split("-")[0] in x][:12]
        raise SystemExit(f"no icon {name!r}; similar: {near}")
    svg = open(f).read()
    svg = svg.replace("currentColor", colour).replace('stroke-width="2"', 'stroke-width="1.75"')
    return io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size))

def fill_crop(path, w, h, y=0.0):
    im = Image.open(path).convert("RGB"); r = w / h
    if im.width / im.height > r: nw = int(im.height * r); im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:  # keep a band of the screenshot; y = where the band starts, as a fraction of the spare height
        nh = int(im.width / r); top = int((im.height - nh) * y); im = im.crop((0, top, im.width, top + nh))
    b = io.BytesIO(); im.save(b, "PNG"); b.seek(0); return b

def swap_picture(slide, pic, stream):
    part, rId = slide.part.get_or_add_image_part(stream)
    pic._element.blipFill.blip.rEmbed = rId

made = []
for n, sd in enumerate(spec["slides"], 1):
    src = originals[sd.get("from", 1) - 1]; s = duplicate(src); T, P = slots(s)
    sample = {}
    for k, sh in enumerate(T): sample.setdefault(sh.text_frame.text.strip(), []).append(k)
    for key, val in sd.get("text", {}).items():
        if re.fullmatch(r"T\d+", key): idx = int(key[1:])
        elif len(sample.get(key, [])) == 1: idx = sample[key][0]
        else: raise SystemExit(f"slide {n}: text key {key!r} is missing or not unique; use its T# from --inspect")
        set_text(T[idx], val)
    for key, val in sd.get("images", {}).items():
        pic = P[int(key[1:])]
        if isinstance(val, str) and val.startswith("lucide:"): swap_picture(s, pic, icon_png(val[7:], colour_of(pic)))
        else:
            v = val if isinstance(val, dict) else {"path": val}
            swap_picture(s, pic, fill_crop(v["path"], pic.width, pic.height, v.get("y", 0.0)))
    if sd.get("image"):  # a full slide picture (e.g. the swimlane) over this slide's title and footer
        keep = set(sd.get("keep", ["T0", "T1"]))
        for k, sh in enumerate(T):
            if f"T{k}" not in keep: sh._element.getparent().remove(sh._element)
        for sh in P: sh._element.getparent().remove(sh._element)
        for sh in list(s.shapes):
            if sh.shape_type == 1 or sh.shape_type == 9 or (sh.shape_type == 17 and not sh.text_frame.text.strip()):
                if sh not in T: sh._element.getparent().remove(sh._element)  # cards, connectors, empty boxes
        # Trim the picture's empty (transparent) margins, then fit it, aspect kept, into the content box
        # between the title and the footer, so nothing runs into the footer and the text stays readable.
        im = Image.open(sd["image"]).convert("RGBA"); bb = im.getchannel("A").getbbox() or (0, 0, im.width, im.height)
        im = im.crop(bb); buf = io.BytesIO(); im.save(buf, "PNG"); buf.seek(0)
        E = 914400; L, R = int(sd.get("left_in", 0.41) * E), int(sd.get("right_in", 0.41) * E)
        top, bottom = int(sd.get("top_in", 1.2) * E), prs.slide_height - int(sd.get("bottom_in", 0.6) * E)
        bw, bh = prs.slide_width - L - R, bottom - top
        w, h = (bw, int(bw * im.height / im.width)) if bw / bh < im.width / im.height else (int(bh * im.width / im.height), bh)
        s.shapes.add_picture(buf, L + (bw - w) // 2, top + (bh - h) // 2, width=w, height=h)
        if w < 0.8 * prs.slide_width: print(f"WARN slide {n}: picture only {w / prs.slide_width:.0%} of the slide width; text may be small. Use fewer lanes or steps.")
    if sd.get("notes"): s.notes_slide.notes_text_frame.text = sd["notes"]
    made.append(s)

# Drop the template's sample slides from this OUTPUT copy only (the template file itself is never changed).
lst = prs.slides._sldIdLst
for sl in originals:
    for sid in list(lst):
        if prs.slides.get(int(sid.get("id"))) is sl: prs.part.drop_rel(sid.rId); lst.remove(sid)
os.makedirs("out", exist_ok=True); out = f"out/{brief['slug']}_Deck.pptx"; prs.save(out); print(out, len(made), "slides")
```
