---
name: wireframes
description: Turns the approved scoping document (BRD) into low-fidelity wireframes — one grey-box PNG per page, drawn from a short JSON layout spec by a bundled script (no browser, no HTML) — plus a component manifest, the closed list of components the design system then designs and the build then uses. Map pages follow the bundled map-component reference (one network map, four modes). Runs in POC Studio's Plan phase between Scoping and the Design System, and for /poc-studio:wireframes.
---

# Wireframes (POC Studio, Plan phase)

**Input:** the approved scoping document (`02-scoping/scoping-document.docx`), the client and use case.
**Output** in `<workspace>/02b-wireframes/`:

| File | What it is |
|---|---|
| `<slug>.wireframe.json` | the layout spec you write (the only thing you write by hand) |
| `png/<page-id>.png` | one low-fidelity frame per page, at the persona's real width |
| `<slug>-wireframes.pdf` | all frames in nav order: what the person approves and what goes to Orbit |
| `wireframe-manifest.json` | generated from the spec: pages, and every component with its pages, blocks, CMP IDs, variants, states and, for maps, the data contract and behaviour |

**Why this stage exists.** The wireframes fix *what is on each page and where*. The design system then designs only
the components in the manifest (plus its baseline: sign-in, empty/error/loading/no-access, toast, confirm), and the
build composes pages to these layouts. Fixing the layout once, at low fidelity, is what lets the later stages stop
designing things nobody asked for.

## Rules

1. **The scoping document decides; the wireframe draws it.** Every page in §11 gets a frame, in nav order, with the
   page's own ID. Its regions come from §11 "Layout" and the blocks table; its words from "Screen UX" (the question,
   the one primary CTA, hero content, filters with their values, row/card anatomy, exact copy, context actions). The
   persona and width come from §11 "Personas" and §7. Nothing L2, nothing the document does not build.
   Set `app.search_label` and `app.agent` from the document's own words (spec-format.md).
2. **Low fidelity, on purpose.** Greys only, one font, no brand, no icons beyond what the script draws. Real labels
   and copy from the document, never lorem ipsum. Numbers from the seed data (§19) where the document gives them.
3. **Slots for the generic, detail for the defining.** Draw in detail only what makes this app this app: each page's
   hero, the work queue, the record's main card, the map, the agent's answer. Everything else is a `slot`: an empty
   dashed region named with its component, `count`, the `variants` it needs and its `states`. The design system fills
   the slot; you only fix where it goes and what it must cover.
4. **Name components the way §23 does.** Use one name per component across all pages (`approval-queue-table`, not
   three spellings), put the §23 CMP ID on its blocks as `cmp`, and reuse the same component wherever the same thing
   appears. Every CMP ID in §23 appears on at least one block. A new component that §23 does not have is allowed only
   when a §11 block needs it; say so in its `note`.
5. **Variety is bounded here.** `variants` lists only the forms the pages actually need (a compact card, a horizontal
   bar chart; at most three per component): the design system must design these. It may still show its own style-set
   alternatives within its rule-1 families (at most three per family counting these), never a new component. States:
   the ones §11 names for the block, always including loading and empty for data blocks.
6. **Extra frames only for what changes the layout.** A second frame of a page (`PG-03b`) is for an open panel, a
   drawer, a modal, a different mode of the same map, or a phone layout. Not for every state: states go in `states`.
   The agent opens as a drawer (one frame shows it); a confirm dialog for the one irreversible action is one modal.
7. **Maps.** A page whose main question is *where* (sites, stores, branches, assets, routes, a radius search) is a
   map page: read `references/map-component.md` and follow it exactly — the map is the page, panels float over it,
   one of four modes (`rings`, `dots`, `arcs`, `radius`), a legend in this screen's own words, and the map block's
   `data` contract (object, lat/lng fields, what colours a site, card fields, route ends or radius). If the records
   have no latitude/longitude in §12, the page is not a map page: raise it as a finding for the AI PM, do not invent
   fields. Never put a map in a card on a dashboard.
8. **One spec, rendered, never hand-drawn.** Write the spec (format: `references/spec-format.md`; a full example:
   `references/example-spec.json`), then render. Change a layout by changing the spec and re-rendering.

## Steps

1. Read the scoping document's §7 personas, §8 journeys, §9 conventions (navigation, global elements), §10.5 UI
   patterns, §11 page specs (all of each), §12 for lat/lng fields, §13 agents, §19 seed data, §20.2 demo storyline,
   §23 component inventory. Note the shell (left nav or top bar), the nav items per persona and the hero record.
2. Write `<workspace>/02b-wireframes/<slug>.wireframe.json`, one page per §11 page in nav order, then the extra frames
   (rule 6), then one drawer frame for the agent and one modal frame for the irreversible action if the document has
   them.
3. Render (on a Mac, the collateral tools' Python has Pillow; the fonts ship with this skill):
   ```bash
   W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/render.py' | head -1)")"
   source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 "$W/render.py" "<workspace>/02b-wireframes/<slug>.wireframe.json" "<workspace>/02b-wireframes"
   ```
   A spec error stops the render with one line per problem: fix the spec and run again. If Pillow is missing,
   `pip install pillow` (into the collateral venv on a Mac).
4. Check coverage against the scoping document, and fix every gap it lists (a missing page or CMP ID is a gap; a slot
   without `cmp` is fine for a shared component):
   ```bash
   W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/render.py' | head -1)")"
   source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 "$W/coverage.py" "<workspace>/02-scoping/scoping-document.docx" "<workspace>/02b-wireframes/wireframe-manifest.json"
   ```
   (Each shell starts fresh, so the first line is repeated. A BRD given as a PDF works too: pass the .pdf.)
5. Look at every PNG yourself (Read the image). Fix overlaps, cut-off text, a frame taller than it needs to be, or a
   region whose purpose is unclear. Re-render.
6. Return the PDF, the PNG folder and the manifest paths, the page and component counts, and in two lines what you
   drew in detail and why.

## What the next stages do with it

- **Design system:** reads the manifest as its component list (its section 0.0): a component page for every manifest
  component with the listed variants, features and states, plus its baseline (sign-in, statuses, empty/error/loading,
  toast, confirm, the agent drawer, the kit atoms); no proposals, no reserve views; its full screens are high-fidelity
  versions of wireframe frames, same layout.
- **Build:** the frames and manifest go in the build request; each page follows its frame's layout and the design
  system's styling. Map pages follow `map-component.md` (platform-master adds it as a pointer).
- **AI PM:** reviews this stage (lens `wireframes`) and, at Stage 4b, checks the built pages against the frames.

## Update mode (a change request after the app is built)

Called by the orchestrator's **4c · Changes after the build** (and `asset-run` § 6 for a one-off app) when the AI PM
has triaged a change as **big** or **very big**. Input: the person's words verbatim, the AI PM's triage (its
`affected_pages`, `new_pages`, `components`), and the approved `02b-wireframes/`. The app is not touched in this step.

1. **Keep the approved version.** Move the current spec, `png/`, PDF and manifest to
   `02b-wireframes/_previous/v<N>/` (`N` = the approved version; never delete it). Copy the spec back as the working
   spec.
2. **Edit only what the change needs.** Change the affected pages' entries in the spec, add new pages (and their
   extra frames, rule 6) in nav order with new page IDs, remove a page only if the person asked. Every rule above still
   holds (low fidelity, slots, one name per component, real copy from the person's words or the scoping document).
   Leave every other page's entry byte for byte as it was. The design system is not updated: a new component is
   added as a slot with a `note` saying it is new in this change, and the build styles it from the design system's
   kit and tokens.
3. **Render and check** as in Steps 3–5 (coverage still runs against the scoping document; a page the person added
   that the document does not have is expected, not a gap).
4. **Make the change sheet** (before | after for every page that differs, and the manifest delta):
   ```bash
   W="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/wireframes/scripts 2>/dev/null | sort -V | tail -1)"; [ -n "$W" ] || W="$(dirname "$(find ~/.claude/plugins -path '*wireframes/scripts/diff.py' | head -1)")"
   source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 "$W/diff.py" "<workspace>/02b-wireframes/_previous/v<N>" "<workspace>/02b-wireframes" "<workspace>/02b-wireframes/changes/CR-<n>" --request "<the person's words>"
   ```
   Check its list against the triage: every affected page appears, and nothing else does. A page that changed
   without being asked for is undone. `NO_CHANGES` means the edit did not land: fix the spec.
5. Return `changes/CR-<n>/change-sheet.pdf`, `change-summary.json`, the pages added, removed and changed, and the
   components added (not in the design system) in one line each.

## Answering the AI PM

Answer each finding in the response file as `fixed`, `disputed` (with the §11 line or CMP ID behind it) or `deferred`.
A fix changes the spec only where the finding points; re-render everything (it takes a second).
