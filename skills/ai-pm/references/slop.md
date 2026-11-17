# Slop catalogue

Slop is output that looks finished and says nothing specific to this client. Every item below is detectable: by
script (`scripts/slop-phrases.json`, used by `scope_metrics.py` and `build_walk.mjs`) or by one look at a screenshot.
A hit is a finding under R4 (decoration) or R3 (filler) unless the line it sits on is justified by the client's own
material, quoted in the finding's evidence.

The test for every item: **could this sentence, screen or slide appear unchanged in a POC for a different client?**
If yes, it is slop.

## 1 · Documents (Requirement Gathering, scoping)

| # | Slop | Detect | Fix line |
|---|---|---|---|
| D1 | Executive summary opens with how the client works today, not with the pain | first sentence of §1 names a process step, no cost or failure | "Open §1 with who suffers, what goes wrong and what it costs" |
| D2 | Consultant filler: "seamless", "unlock", "leverage", "empower", "robust", "cutting-edge", "end-to-end visibility", "single pane of glass", "game-changer", "streamline" | phrase list | "Replace '<phrase>' with the specific record, number or step it stands for" |
| D3 | Overclaimed differentiator: "no other tool", "first-of-its-kind", "unlike any" | phrase list | "Name the products that cover part of it and say what we add" (scoping §6 rule) |
| D4 | Fake-precise numbers with no source: "reduces effort by 73%", "saves 4.2 hours" | a % or time-saved figure with no S-ID or A-ID on the same line | "Source it (S-ID), log it as an assumption (A-ID), or remove it" |
| D5 | Success metrics that measure the demo, not the business ("AI accuracy 95%") | §4 metric names an app behaviour | "Move to 4.1 acceptance; replace with the business outcome it serves" |
| D6 | A feature list that reads like any vendor's datasheet | L1 rows with no Client ask / journey-stage evidence | "Cut to L2 or cite the evidence" |
| D7 | Paragraphs that state no fact, finding or decision | sentence with no noun from the glossary, no ID, no number | "Delete, or replace with the fact it was gesturing at" |

## 2 · UI and design system

| # | Slop | Detect | Fix line |
|---|---|---|---|
| U1 | The same four KPI tiles across the top of every home page | ≥ 3 pages open on a tile strip | "Lead <page> with the persona's next task (wireframes patterns.md part 2; scoping §11 "Home pages")" |
| U2 | KPI strip as the whole home page, or a home with no task list | screenshot | same |
| U3 | Vanity numbers: totals that drive no action ("1,248 records") | tile with no filter or action behind it | "Show only counts that open a filtered list" |
| U4 | Sparkle / rainbow AI decoration on every AI element | screenshot; `✨` or gradient on > 2 elements per screen | "One AI marker style (scoping §9 AI signature), nothing else" |
| U5 | Gradient hero or banner with no brand reason | screenshot | "Remove, or cite the brand evidence for it" |
| U6 | Generic empty states ("No data yet", generic icon) | copy pull | "Use the exact empty-state copy and CTA from scoping §11" |
| U7 | Raw values on screen: `null`, `undefined`, `NaN`, `[object Object]`, `0.87` where a % is meant, `snake_case` field names, query syntax (`status = open`) | `build_walk.mjs` | "Format <value>; never show field names or raw fractions" |
| U8 | Lorem, placeholder, "Test 1", "John Doe", "Acme" in a non-Acme POC | copy pull | "Use the hero records from scoping §19" |
| U9 | Every card the same size in a uniform grid; every chart a default bar | screenshot | "Apply the build-plan pattern for this page" |
| U10 | Icons decorating labels that need none | screenshot | "Remove the icon" |
| U11 | Coloured side stripe on a card, row, bubble or field (owner preference) | DOM: `border-left` ≥ 2px with a non-neutral colour on a card-like box, or `TB` status-stripe variant active | "Show status with the tag; no side stripe" |
| U12 | Agent as a card or block on a page instead of the drawer | screenshot / DOM | "Agent opens in the drawer on the live agent component" |

## 3 · UI copy (every visible string)

| # | Slop | Detect | Fix line |
|---|---|---|---|
| C1 | Jargon or platform words the persona would not say ("entity", "record_id", "workflow run", "object") | phrase list + glossary | "Use the client's term: <glossary term>" |
| C2 | Two names for one thing across pages ("Visit" / "Audit") | copy pull, term clusters | "Pick the glossary term and use it everywhere" |
| C3 | Buttons that do not say what happens ("Submit", "OK", "Proceed", "Click here") | button text list | "Name the outcome: 'Send for approval'" |
| C4 | Copy that promises what the page lacks ("approve below" with no button) | read with the controls list | "Add the control or change the copy" |
| C5 | Refusal or error wording that differs from the scoping journey's exact wording | compare with scoping §8.2 / the DS journey-to-component table and flow panels | "Use the exact wording: '<quote>'" |
| C6 | Title Case Everywhere, ALL CAPS sentences, exclamation marks in system copy | regex | "Sentence case, no exclamation" |
| C7 | Helper text that repeats the label ("Name: enter the name") | copy pull | "Delete the helper or say what makes a valid value" |

## 4 · Collaterals

| # | Slop | Detect | Fix line |
|---|---|---|---|
| K1 | The video opens on features, not the pain | first narration line | "Open on the client's pain in their words (RG pain points)" |
| K2 | No wow moment in the first 90 seconds | storyline vs `placed.json` | "Move the core action (scoping §20.2) before 1:30" |
| K3 | Narration that describes the screen ("here we see a table") instead of the outcome | phrase list | "Say what it is worth: '<outcome>'" |
| K4 | Deck big stats that are backlog sizes or vanity counts | deck text | "Outcome stats only (collateral skill rule)" |
| K5 | Template sample text, `*` or `**` left on a slide | `check.py` + render | "Fill or delete the slot" |
| K6 | "Next steps" that are our fixes, not the client's path | deck text | "Pilot → connect systems → roll out" |

## 5 · From the team's "Dos and don'ts to reduce AI slop" (14 Nov 2026)

Items the catalogue above did not yet name. The wireframes skill carries the same rules in its "Slop rules" section
and its `wf_tool.py check` tests them; a `check:` line the producer did not fix or defend is a finding here. The
design system styles exactly what the wireframe contains, so content slop is caught at the wireframes stage; the
visual items (U19, U20) are judged on the design system and the build by screenshot.

| # | Slop | Detect | Fix line |
|---|---|---|---|
| T1 | Sentences over 25 words, or averaging over 20 | `wf_tool.py check`; word count | "Split into sentences of 25 words at most" |
| T2 | Stock AI phrasing: "it's not just X, it's Y", slogans, "In conclusion", "Let me know if", hedges ("may potentially"), more than one dash aside in a paragraph | phrase list; `check` | "Say the fact once, plainly" |
| T3 | A list of three by habit ("fast, secure and scalable") | read | "List what is true: two, four or seven" |
| T4 | The swap test fails: the title or sentence still makes sense with another company's name | read | "Rewrite with this client's record, number or step" |
| T5 | Traces of how the output was made: tool names, file paths, run IDs, scores, error codes on screen or in a document | `check`; regex | "Remove; keep it in the QA notes" |
| T6 | Something built that nobody asked for | requirement map | "Cut it, or list it under Optional next steps" |
| U13 | More than four key facts on a card or record header; eight or more numbers on one card | `check` | "Keep four; put the rest behind Details" |
| U14 | More than six metrics on a screen, or a metric with no comparison and time frame | `check`; screenshot | "Six at most, each with its target or last period and its time frame" |
| U15 | A card inside a card | `check` | "Flatten into the parent's sections" |
| U16 | A tag on every row, or tags in three or more columns of a table | `check` | "Colour only the exceptions" |
| U17 | Emoji used as icons, or an icon with no word | `check` | "Use a labelled icon or words" |
| U18 | More than one primary button, or more than two other actions in a page header | `check` | "One primary; the rest in a menu" |
| U19 | Glass, glows or purple and indigo gradients by default; more than two typefaces | screenshot | "Solid by default; brand gradients only by role" |
| U20 | Chart junk: 3D, shadows, gradient fills, heavy gridlines, rainbow palettes, more than four series, a pie with more than five slices, bars not from zero, an untitled or "Chart 1" chart | screenshot | "Flat marks, one data colour and one highlight, a takeaway title, axes with units" |
| U21 | False precision ("$1,284,391.4762") or mixed formats ("$1.2M" beside "1,200,000 USD") | `check`; read | "Round to two or three significant figures; one format per unit" |
| U22 | A chart or headline number whose source or time frame is nowhere visible on the screen (one note per panel at most; no note needed when the screen already shows it) | screenshot | "Add the source or time frame under it" |

A clean word scan is not proof of quality: generic content in clean words is still slop (the test at the top).

## 6 · Writing, logic and clarity (the shared writing rules, 17 Nov 2026)

**Read this section in every review**, whatever the output: it carries the shared writing rules every skill follows
while it writes (`references/anti-slop.md` at the plugin root). Producers apply them as they write, so a hit here is a
miss. **Blocking:** U29, U30, U31 and U36 (claims the data does not support, contradicting states, options with the
same result, dead ends). Every other row here is non-blocking.

| # | Slop | Detect | Fix line |
|---|---|---|---|
| D8 | Clauses chained with semicolons, brackets, arrows or "·"; sentences over 25 words | read | "One idea per sentence" |
| D9 | Recap endings ("Ultimately", "Overall", or a last paragraph that restates the piece) | phrase list; read | "End on the last concrete point or next step" |
| D10 | Bold on more than two points per section, a heading on every paragraph, emoji bullets, headings over sections of two sentences or fewer | read | "Bold one or two points; merge tiny sections" |
| D11 | Em dash clusters, or em dashes in short copy | read | "Use a comma, period or parentheses" |
| D12 | Negative listing ("Not an X. Not a Y. A Z."), exclamation marks, flattery | phrase list; read | "State Z directly" |
| D13 | One thing under several names in a document (C2 covers screen copy) | glossary against the text | "Pick the glossary term and use it everywhere" |
| D14 | Weasel attribution ("experts agree", "studies show", "industry reports suggest", "widely regarded") | phrase list | "Name the source or cut the claim" |
| D15 | Importance puffery ("plays a vital role", "marks a pivotal moment", "stands as a testament") | phrase list | "State the fact" |
| D16 | Interpretive metadiscourse ("the key point is", "this distinction matters", "in other words") | phrase list | "Delete the aside" |
| D17 | Rhetorical or faux-insight setups and throat-clearing ("What if…", "Here's what nobody tells you", "Let me be clear") | phrase list | "Make the claim" |
| D18 | Dramatic fragments ("X. And Y. And Z.") and fake-profound kickers | read | "Use complete sentences; end on the concrete point" |
| D19 | Fake-strong verbs ("serves as", "acts as"), weak verb phrases ("made a decision"), objects doing human verbs | phrase list | "Use is, has, or the direct verb" |
| D20 | Robotic rhythm: every paragraph or page spec built the same way | read | "Vary the shape where it helps the point" |
| D21 | Bullets where two sentences of prose would read better | read | "Write it as prose" |
| D22 | One uncertainty restated many times | read | "State it once, where it applies" |
| D23 | A metric label that does not describe what is counted ("Average response time" for time to close) | label against the formula | "Name what is counted; record the rename" |
| D24 | One word for two concepts ("High" for volume and urgency), or two words for one | glossary against screen words | "One term per concept, one concept per term" |
| U23 | No error state, or "Oops! Something went wrong" | copy pull | "Say what happened and how to fix it" |
| U24 | Internal rule IDs, citation trails, or "demo" and "synthetic" words on screen | build walk; screenshot | "Remove from the screen" |
| U25 | More than about four text sizes, or more than one spacing scale | screenshot | "Four text sizes, one spacing scale" |
| U26 | A business rule not explained in words on screen | read with the spec | "Say the rule: 'within the 30% discount limit'" |
| U27 | AI marked more than once per panel, or more than one way into the assistant | screenshot | "One entry point; one marker per panel" |
| U28 | Em dashes or colon reveals in UI strings | copy pull | "Plain sentence, no dash" |
| U29 | A headline number or payoff claim the data does not support | re-derive from the hero records | "Work it out from the data, or drop the claim" |
| U30 | States that contradict each other, or an action allowed in the wrong state (Delivered with custody stopped) | walk each hero record | "Guard the action by state; make the status follow the exceptions" |
| U31 | Two options on a decision with the same visible result | read each action's outcome | "Merge them, or say what each changes" |
| U32 | AI internals on screen: internal agent names (other than the assistant's own), model names, confidence on rule-based checks, system words ("indexing", "last read") | copy pull | "Show 'AI' once per panel; use plain words" |
| U33 | The same fact twice or more on one screen | read | "Keep it once; link the summary to its list" |
| U34 | Presenter tools mixed into the product: in wireframes, outside the review bar; in the build, outside the profile menu's presenter group | DOM; screenshot | "Wireframes: the review bar. Build: the profile menu, apart from settings" |
| U35 | Dates, times or spelling outside the BRD's locale; a time with no zone | read | "Use the BRD's locale; show the zone" |
| U36 | A dead end: no path after a wrong AI answer, no edit or remove, no word on how the person hears back | walk the journey | "Draw the path, or raise it as an open question" |
| U37 | A label, badge or count that needs the BRD to understand ("75 t billed", badge "2") | the two-second test | "Say what it counts, with its unit" |
| H1 | The wrong chart for the question | read | "Line for a trend, sorted bar to compare, table for exact values" |
| K7 | Stock headline formulas ("Reinvented: …", "Every X comes with its Y") | phrase list | "Title it with the specific outcome" |
| K8 | The same tagline on several slides or act cards | deck text | "One use per deck" |
| K9 | A slide title that says nothing new | deck text | "Say what this slide adds" |

