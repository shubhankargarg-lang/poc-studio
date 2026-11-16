---
name: poc-collateral-studio
description: Create the collateral set for a UnifyApps POC (demo script, narrated demo video, PPT) from one story, in the UnifyApps template theme.
---

# POC collateral studio

> ## HARD RULE: never delete a resource
> Do not delete anything that already exists: files, recordings, pages, records, platform
> objects, or anything another person made. Overwrite only artefacts this pipeline generated in
> the current run (the deck drops the template's sample slides from its own *output copy* only).
> If something has to go, say what and let the user remove it.

One POC → **three** collaterals, all generated from one story so they never disagree:

| # | Collateral | File |
|---|---|---|
| 1 | Demo script (time, screen, on-screen action, narration, features) | `out/<Slug>_Demo_Script.pdf` |
| 2 | Demo video, narrated in US English, with subtitles | `out/<Slug>_Demo.mp4` + `.srt` |
| 3 | PPT built from the UnifyApps template: the UnifyApps opening slide, the story, the technical blueprint (architecture + every automation and agent), the closing slide | `out/<Slug>_Deck.pptx` |

**Only these three are delivered.** No walkthrough PDF and no swimlanes document. The "today vs. with UnifyApps"
swimlane is drawn only as a **slide inside the deck** (Phase 6 below): its picture is a working file in `build/`,
never a separate deliverable. `out/` holds only the three collaterals. (The toolkit's walkthrough code stays in
`assets/kit/` unchanged but is never run.)

This skill is **self-contained**. Its toolkit (`assets/kit/`) is copied into the project folder and
run there. It needs Node 18+, Python 3.10+, ffmpeg, poppler (`pdftotext`), and network access to
npm, PyPI and GitHub. On a Mac these come from the `poc-collateral-setup` skill (installed once into the user's own
folders, no admin); `kit/setup.sh` reuses them (Playwright, the offline Kokoro voice model, the Spectral font). Nothing calls
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
   environment already uses, never typed by you), in this order: an existing `auth/<persona>.json`; then the Orbit
   session from Setup (`~/.local/poc-studio/auth/orbit.json`, copied to `auth/<persona>.json` after
   `orbit_signin.mjs --check` passes); only then `kit/auth.mjs`. Only when there is no way in does the run stop: then
   open `kit/auth.mjs` and ask the user to sign in, once, for every persona at the same time.
   **Orbit:** POC Studio apps are built by UnifyApps Headless on the Orbit environment
   (`https://orbit.uat.unifyapps.com/`). Use the app's **preview link** UnifyApps Headless reported (`<workspace>/04-build/
   build-summary.md`, `state.json` → `app.preview_url`) as each persona's `url` and `public_url`, for discovery,
   capture and the video recording. **Do not use the published Matrix app URL**: it asks for a user to
   be created before the app can be used. If no preview link is recorded, get it from UnifyApps Headless before recording. When the app needs a login, set the persona's `login` to
   `https://orbit.uat.unifyapps.com/login` (the preview answers 401 without a session instead of redirecting), open
   `kit/auth.mjs` and ask the user to sign in to Orbit there (Google sign-in is fine; it saves only once the preview
   opens); never type or store a password.
5. **Who receives the files.** Default **external** (the customer): no internal URLs, usernames,
   emails or build notes (`brief.share: "external"`). Use `"internal"` only when the request says the
   collaterals are for the team.
6. **Template.** Use the UnifyApps PPT template bundled with this skill:
   `assets/UnifyApps_template.pptx` in this skill's base directory (the path Claude Code prints as
   "Base directory for this skill" when the skill loads). If that path cannot be resolved, find it with
   `find ~/.claude/plugins -name UnifyApps_template.pptx`. Always use the bundled file, never another
   template. Never ask for it.

### What the persona decides (for all three collaterals)

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

**Read the inputs once.** Read the build summary, the scoping document's Part A/B, the test report and the seed data
once, and write what the collaterals need into `_working/notes.md` in one write (personas, the subject record, the
must-show features, routes, the architecture items for the blueprint). Later phases read the notes, and open a source
again only for something the notes do not cover.

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
   **In POC Studio** the app was built by UnifyApps Headless and approved by the person at the verify gate: route any fix to the
   app (seed data, prompts, cached outputs) through UnifyApps Headless in the same session, and list every such fix at the
   collaterals approval gate. Collect every app fix this phase finds and send them as **one batch**, then refresh the
   copilot or AI outputs once, then **freeze the data**: no more app changes after capture starts, except a fix for a
   must-fix finding from `check.py` or a review.
   Change only demo data and prompts this build created; for records you did not create, leave them
   untouched and steer the story away from the contradiction instead (another record, another screen),
   noting it in `internal.md`. Never delete. No question is needed either way.
4. **Real samples for document-reading flows.** When `01-requirement-gathering/files/samples/` has real samples (POC
   Studio), every scene where the flow uploads or reads a document or image uses one of them, so the customer sees the
   AI read real documents. Pick the sample the AI reads correctly (Stage 4's `test-report.md` says which). The
   "sample" label lives only in file names and the RG document; nothing on screen or in the narration says "demo",
   "sample" or "synthetic". Never upload a real sample anywhere outside the app (no Orbit link, no public storage).
5. **Domain sense-check.** Would the customer's own experts accept each suggestion? (A 2-layer fabric
   "meeting the same brief" as a 3-layer GORE-TEX Pro shell would not.) Fix the data or drop the claim.
6. **Harvest what makes the story concrete:** the real navigation (routes, sidebar labels, tab
   names), stable selectors (add `data-testid` to the elements the story clicks if they lack one), the
   customer's own vocabulary from the requirements, the discovery pain points for the "today" swimlane,
   and the real architecture (apps, workflows, agents, objects, connections) for the technical blueprint
   (`blueprint.json`) and the technical act.
6. **Write `internal.md`** for everything the team should know but the customer must not see: known
   bugs, features left out and why (a copilot erroring), UAT links, test accounts, workarounds. This
   file never feeds a collateral; `check.py` fails any customer file that contains such notes.
7. **Know what the UI can actually do.** Only narrate actions the screen offers. If the app has
   "Copy draft", the narration says "copies the draft", not "sends it". If a claim needs a button
   that does not exist, build it or drop the claim.

When the app was *not* built in this session, do the same from discovery: read the app's pages,
records and AI panels during Phase 1 and write `facts.json` from what you verify.

---

## Answering the AI PM (POC Studio, v1.0)

The orchestrator may call this skill again with the AI PM's findings (`<workspace>/reviews/collaterals-review-<n>.yaml`)
instead of a fresh task. Then:

1. **Fix only what is listed.** Edit the existing output in place: the story, actions, deck.json or app data the finding names; re-voice and re-record only the scenes and acts it touches; leave everything else exactly as it was. Do
   not re-run the whole pipeline for a handful of findings.
2. **Answer every finding** in `<workspace>/reviews/collaterals-response-<n>.yaml` (same `n` as the review):
   ```yaml
   responses:
     - { finding: F1, status: fixed,    where: "<section / page / specimen / scene>" }
     - { finding: F2, status: disputed, reason: "<the evidence: an E-, S-, A- or D-ID, a stated ask, a human decision>" }
     - { finding: F3, status: deferred, reason: "<non-blocking only>" }
   ```
   Dispute when the finding is wrong for this client, and say why with evidence; a dispute without evidence is
   treated as `fixed` and checked. Never dispute a finding that cites a human decision.
3. **Re-run your own checks** on what you changed (`lint.mjs`, `check.py`, and `review.py` for a new video version), and say what you ran in the response file
   (`checks: [ ... ]`). The AI PM re-runs them too.
4. Do not ask the person anything; questions still go to the reviewer in resolve mode.

---

## The pipeline

```bash
# POC Studio: work inside <workspace>/05-collaterals/ so every output lands in the client folder
mkdir <slug>-collateral && cd <slug>-collateral
mkdir -p kit _working && cp -R "<skill-base-dir>/assets/kit/." kit/   # the toolkit, copied in one command
bash kit/setup.sh                                  # reuses the shared tools if installed, else installs here
source env.sh && python3 kit/brand.py <skill-base-dir>/assets/UnifyApps_template.pptx  # tokens, logo, template copy -> brand/
```

**Every command in the collateral folder starts with `source env.sh && `** (each shell starts fresh; `env.sh` puts
the shared Python, ffmpeg, LibreOffice and voice model on the PATH; it is empty when nothing is shared). The commands
below omit it for brevity. On a Mac, if `~/.local/poc-collateral/env.sh` does not exist yet, run the
`poc-collateral-setup` skill first (no admin, once per Mac) instead of installing anything with Homebrew.

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
| 4 Trim | `python3 kit/trim.py` | the same film with every silent wait cut out; `build/trim.json` | every slow step shows click → short beat → result |
| 5 Review | `python3 kit/review.py <n>`, then look at every frame | `review/v<n>/report.md`, contact sheet | all must-show items `shown`; no MUST FIX |
| 6 Deck swimlane | write `swimlanes.json`; `node kit/swimlanes.mjs`; then `mkdir -p build/swimlanes && mv out/swimlane_*.png out/*_Swimlanes.pdf build/swimlanes/` | `build/swimlane_with_deck.png` for the deck slide (nothing left in `out/`) | each step maps to a scene or discovery |
| 7 Blueprint | write `blueprint.json` from the build (see "Blueprint"); `node kit/blueprint.mjs` | `build/blueprint/blueprint-1.png` (architecture), `blueprint-2…n.png` (what was built) | exit 0: diagram and list name the same things; every automation and agent built is listed |
| 8 Deck | `python3 kit/deck.py --inspect`; write `deck.json`; `python3 kit/deck.py` | `out/<Slug>_Deck.pptx` (opening slide first, closing slide last, added by the script) | every slide rendered and checked |
| 9 Final | `python3 kit/check.py` again (it now scans all outputs) | | 0 must-fix |

**Waiting and retries.** A long step (`kit/setup.sh` installing, a full `record`, `build.py`) runs in the foreground
with a long timeout; if it runs in the background, write `${CLAUDE_PROJECT_DIR:-$PWD}/.poc-studio/waiting` (beside the autopilot file), end the turn, and wait
for its finished notice instead of checking its status (delete the flag when it is done). When a command fails, fix
the cause and retry it once; when a capture or recording fails, re-run only the failing scene or act (`ACTS=B`), never
the whole run. If it fails a second time, record it in `internal.md` and carry on with what works.

**Limits per round.** At most **2 recordings** of any act and **2 video builds** per review round; at most **2 review
versions** (`v1`, `v2`) before shipping, unless a must-fix is still open. A `no sync flash found` drift of about 0.2 s
is accepted as it is when the cues land (no LATE CUE ≥ 1.2 s); re-record for it only when the voice is visibly off.

Re-runs are surgical: `python3 kit/narrate.py a3 b1` re-voices two scenes; `ACTS=B` re-records one
act; `build.py` re-stitches in seconds (always run `kit/trim.py` again after it). Each full run writes a fresh `build/<stage>.log`.

---

## Phase 1: Plan (coverage → story → script)

1. **Discover the app.** Walk every screen in scope and note the *real navigation path* to each
   (which menu, tab, row or button gets there). In the build session you mostly know this already.
2. **`coverage.json`**, one entry per must-show screen/feature. It is the checklist every version
   is audited against:
   ```json
   [{ "id": "F07", "screen": "Visit detail", "feature": "Failed check cites the brand clause",
      "nav_path": ["Sidebar › Visits", "Click visit row", "Tab › Findings"],
      "must_show_in": ["video", "deck"] }]
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
- **Slow steps are recorded as they happen, then the wait is cut out** (`kit/trim.py`, after `build.py`). When an
  automation, an agent or a button takes longer than expected, do not fake it and do not narrate over a spinner:
  record the real click and the real result, and let the wait be **silent** — end the narration line before the slow
  action, and start the next line on the result (a `pre` click, or the next scene). `trim.py` finds every stretch
  inside a scene where the screen is frozen and nobody speaks for 1.5 s or more, keeps 0.4 s on each side and cuts the
  rest, so the film goes click → short beat → result while the voice-over carries on in sync. The subtitles and
  `build/placed.json` are shifted to match; the untrimmed film is kept in `build/`. Cards (opening, act, closing) are
  never cut. A wait that has narration over it is not cut: rewrite the line so it is silent.
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

**Two slides are not re-themed:** the deck's opening slide (dark green UnifyApps cover: "Agentic automation for
the enterprise", the three proof points) and closing slide ("Thank You") are template slides 4 and 5, added by
`kit/deck.py` first and last exactly as they are. Never edit their text or use them as a `from` for another slide.

---

## Review in iterations (after every version of every collateral)

Work in phases and finish each before the next: **Facts → plan → script sent → capture green →
consistency gate → video act by act → review → deck swimlane → deck → final check.**
Track them in the task list and send each collateral as soon as it passes.

After each version `v<n>`:

1. `python3 kit/review.py <n>`. It extracts frames (middle, every cue, end of each scene) into
   `review/v<n>/frames/`, builds `contact_sheet.jpg`, lists timing problems (OVERRUN, SLOW, FAIL, and
   LATE CUE ≥ 1.2 s as MUST FIX), runs `check.py`, and writes `review/v<n>/report.md` with the coverage
   matrix.
2. **Look at the contact sheet first**, then at the frames it flags and at every cue frame of a must-show item
   (Read the images); open the other frames only where the contact sheet shows a problem. In `v2` and later, look only at
   the scenes that changed. For each coverage item mark the Video column
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
   template sample text left behind (the opening and closing slides' fixed text is not sample text), unreadable
   diagrams, font fallback, and stray `*` or `**`.
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

## Walkthrough PDF — not produced in POC Studio

Skip this section: the walkthrough PDF is not a deliverable. Do not run `node kit/docs.mjs walkthrough`; build the
script with `node kit/docs.mjs script` only. Scenes need no `walkthrough` block (ignore lint warnings about it).

For reference only:

`node kit/docs.mjs walkthrough` builds: cover; at-a-glance (acts + the "with" swimlane); one page
per scene with the real final screenshot, **Why it matters**, and each **Do** line paired with its
numbered step shot (lint warns when `walkthrough.do` lines don't match click/type/select actions);
**You'll see**, **If it doesn't**, feature tags; an appendix with where to go and how to sign in (per
`brief.share`), reset steps, the screens shown live (from `coverage.json`), and what is simulated or
connected at go-live. Persona sets the wording depth.

## Deck (`deck.json`)

Every content slide is a copy of one of the template's three content slides, so master, background, footer and
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

Default storyline (adjust by persona): **Opening slide** (added by the script) · 1 Today's challenges (slide 1) ·
2 Reinvented (slide 2, real screenshot) · 3 What each persona gets (slide 3, one per persona) · 4 Swimlane with
UnifyApps (image slide) · 5 **Technical blueprint (every persona, required)**: one image slide per
`build/blueprint/blueprint-<n>.png`, in order: the architecture, then the automations and agents on as many slides as
the list needs · 6 Next steps / go-live path · **Closing slide** (added by the script).

Blueprint slides are image slides on template slide 1 with `"top_in": 1.25, "bottom_in": 0.55`; the slide title
carries the message, so `blueprint.json` needs no `headline`:

```json
{ "from": 1, "image": "build/blueprint/blueprint-1.png", "top_in": 1.25, "bottom_in": 0.55,
  "text": { "T0": "TECHNICAL BLUEPRINT · <POC ID>", "T1": ["How it’s built: ", "<the architecture in a few words>", "."] } },
{ "from": 1, "image": "build/blueprint/blueprint-2.png", "top_in": 1.25, "bottom_in": 0.55,
  "text": { "T0": "TECHNICAL BLUEPRINT · WHAT WAS BUILT", "T1": ["What was built: ", "<n> automations, <n> AI agents", "."] } }
```

A continued list page keeps the same title with "(continued)" in the eyebrow. Keep each title to one line.

`kit/deck.py` checks the saved file before it finishes: the slides' file names inside the package follow the deck order,
the opening slide is first and "Thank You" is last. A failed check stops the build; never hand over a deck that failed it.
When you look at the deck, look at it as a viewer opens it: render the saved `.pptx` (`soffice --convert-to pdf`) and check
the first and last pages, not the deck.json order.

- **Big stats are outcomes**, not backlog: "seconds from photo to scored visit", "every finding
  linked to its clause", "3 brands on one record". Every figure is real (POC data or `facts.json`).
  A gap or a queue size ("£14.52 over target", "49 waiting") belongs in a proof slide's caption.
- **Fill every slot you keep**: any sample text left from the template is a review failure.
- **No internal notes** anywhere, speaker notes included. Next steps describe the customer's path
  (pilot, connect systems, roll out), never our fixes ("fix the agent's model connection").
- Icons: `lucide:<name>` (lucide-static), recoloured to match the icon they replace.

## Blueprint (`blueprint.json`)

The technical blueprint shows the client **what was built and how it fits together**: a high-level architecture and a
list of every automation and AI agent. It goes in the deck (Phase 7 → slides in Phase 8), never as a separate file.

**Source of truth:** the build, never the plan. In POC Studio read `04-build/build-summary.md` (what UnifyApps
Headless reported it built: objects, agents, automations, pages, the solution) and set `"source"` to its path,
relative to the collateral folder (`../../04-build/build-summary.md`; a one-off run: `../../04-build/one-off/build-summary.md`);
the script fails when that file is missing and warns about any name that does not appear in it. Use scoping §11–§14 only for what each item does and when it
runs. Without a build summary (a one-off run), list the solution's automations and agents from the app's builder or
ask UnifyApps Headless for the list, and record the source in `brief.json` → `decisions`. Never list something the
scoping document planned but the build does not have; never leave out something that was built.

```json
{ "source": "../../04-build/build-summary.md",
  "what": "Self-serve wire payments for BMO's corporate clients, with a back office for BMO. Built on UnifyApps.",
  "principles": ["**Rules decide every wire**, never a model.", "**Money waits for a person's Confirm.**"],
  "users":   [ {"id": "dev", "label": "Client developer", "to": ["portal", "copilot"]} ],
  "doors":   [ {"id": "portal", "label": "Client portal", "sub": "4 pages · code app", "kind": "app"},
               {"id": "copilot", "label": "Copilot agent", "sub": "own records only", "kind": "agent"} ],
  "groups":  [ {"label": "Core API", "items": ["Token", "Wire R1–R7"]}, {"label": "AI", "items": ["Copilot"]} ],
  "data":    [ {"label": "BPS Transaction", "sub": "every wire, mode"} ],
  "systems": [ {"label": "Salesforce", "sub": "accounts", "status": "simulated"} ],
  "env": "Env: BPS_TOKEN_SIGNING_SECRET (signs tokens)",
  "key": ["Wire R1–R7", "BPS Transaction"],
  "built": [
    {"name": "Copilot", "type": "agent", "trigger": "Chat drawer in the portal", "does": "Prepares a wire from plain English; submits only after Confirm.", "tools": ["Copilot Submit"]},
    {"name": "Token", "type": "automation", "trigger": "API call", "does": "Issues a signed token for the client's API calls.", "objects": ["BPS Client"]},
    {"name": "Wire R1–R7", "type": "automation", "trigger": "Console, API or Copilot", "does": "Runs rules R1–R7 in order; the first failure decides.", "objects": ["BPS Account", "BPS Transaction"]} ] }
```

- **`built`** is the list: one entry per automation and per AI agent, **named exactly as in the build**, with when it
  runs and one plain sentence on what it does (outcome first), the objects it reads or writes, and an agent's tools.
- **The diagram** has four layers: `users` (personas and outside callers; `to` = the doors they use), `doors` (apps,
  API groups, agents in drawers; `kind` app / api / agent), the UnifyApps layer (`groups` of `built` names, grouped
  by job), and the bottom row (`data` objects, then `systems` with `status` live / simulated / golive). Every `built`
  name is in a group (a user-facing agent may be a door instead), and every group item is in `built`: the script
  exits 1 otherwise. `key` outlines the hero path (at most 3). `principles` (optional, at most 4) are the design
  rules a technical reader should trust; `env` (optional) names the environment variables.
- **Big builds:** when the groups do not fit as chips, the architecture draws each group's first three items and
  "+N more" (the list pages name them all), and the list runs to as many pages as it needs. Nothing is cut.
- No secrets, keys or tokens anywhere; environment variables by name only. The client's systems keep their real
  names; anything not connected in the POC is `simulated` or `golive`, never shown as live.

## Delivery

**Before hand-over**, check once: `out/` holds exactly the three files (+ the `.srt`); `python3 kit/check.py` reports 0
must-fix; the deck opens with the opening slide and ends with the closing slide; `internal.md` is not in `out/`.

Send each collateral as it passes review (script first, so the user can redirect early). The final message lists the
three files (script PDF, video with its .srt subtitles, deck), the persona, voice and length, coverage status, `check.py` result, and anything
simulated. Keep `story.json`, `coverage.json`, `facts.json`, `deck.json`, `swimlanes.json`, `blueprint.json`,
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
- An `OVERRUN` or `SLOW` caused by the app itself being slow (an automation or agent still running) is fixed by
  making that wait silent and letting `kit/trim.py` cut it: it counts as fixed when `build/trim.json` lists a cut
  over that stretch and the reviewed frames show click → result with no loading screen under the voice.
- `no sync flash found` means that act's audio may drift ~0.2 s: accept it when the cues land; re-record the act
  (within the 2-recording limit) only when the voice is visibly off the screen.
- If the app's own design uses "skeleton"/"spinner" classes on content that stays on screen,
  `settle` waits its full timeout and logs SLOW: use a `waitFor` on the real content instead of
  `nav: true` for that screen.
- Headless recording runs at 1920×1080. If the app needs a real (headed) browser, run under Xvfb.
- If Spectral is missing, renders silently fall back: `render.mjs` warns; re-run `kit/setup.sh`.
- `command not found` (ffmpeg, ffprobe, soffice, pdftoppm) or `No module named kokoro_onnx`: the command was run
  without `source env.sh && `. On a Mac, if the shared doctor reports MISSING, re-run `poc-collateral-setup`.
- On a Mac without Homebrew, `ffprobe`, `pdftotext` and `pdftoppm` are small Python stand-ins that answer the
  calls this kit makes; if a new call needs more, extend the stand-in in `~/.local/bin` rather than the kit.
- Reuse existing sessions; ask for a sign-in only when there is no way in, all personas at once; never store or type passwords.

---

## The toolkit (`assets/kit/`)

The toolkit lives in this skill's `assets/kit/` folder, one file per tool, tested together: `setup.sh`, `lib.mjs`,
`auth.mjs`, `lint.mjs`, `run.mjs`, `narrate.py`, `check.py`, `brand.py`, `render.mjs`, `cards.mjs`, `build.py`,
`trim.py`, `review.py`, `swimlanes.mjs`, `docs.mjs`, `blueprint.mjs`, `deck.py`. Copy the folder into the project with
one command (`cp -R "<skill-base-dir>/assets/kit/." kit/`), never write the files out by hand, and do not "improve"
them; change behaviour through the JSON files, `actions.mjs`, or a deliberate, reviewed edit after the first run.
Read a kit file only when a step needs to know how it works (an error, a flag): the commands above are all a run needs.
