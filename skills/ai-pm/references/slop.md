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
| U1 | The same four KPI tiles across the top of every home page | ≥ 3 pages open on a tile strip | "Lead <page> with the persona's next task (scoping §11 home rule)" |
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
| C5 | Refusal or error wording that differs from the scoping journey's exact wording | compare with scoping §8.2 / DS flow diagrams | "Use the exact wording: '<quote>'" |
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
