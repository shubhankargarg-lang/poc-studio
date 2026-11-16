---
name: "design-system"
description: "Apply a client's brand to an approved wireframe. Takes exactly two inputs, the BRD and the clickable wireframe HTML. Researches the brand from official sources, harvests the real logo into every variant, identifies the real typeface and ships a legally usable one, and skins house Design Language v3.4 onto the brand while preserving luminance. It then finishes every component the wireframe contains as an implementation-ready product element, with its variants and states, correcting incomplete anatomy without changing content or behaviour, and draws three of the wireframe's screens at high fidelity. It audits everything composited in light and dark and ships one self-contained HTML design system with a machine-readable manifest for UnifyApps Headless (Nebula). It styles what exists and adds nothing. Use after the wireframes and before the build."
---

# Design system for a POC

**Input: the BRD and the wireframe HTML. Output: one measured, self-contained HTML design system.** Everything
between is a pipeline you run, not a method you interpret.

**A design system is not drawn, it is transformed.** We own a validated one, Design Language v3.4. The job is to move
it onto the client's colour without breaking a single measurement in it, then use it to style the application the
wireframe already defines.

**The design system styles what exists and finishes it. It does not invent what should exist.** The wireframe is
deliberately low fidelity. It fixes the journeys, screens, content, data, actions, states and component IDs, and draws
each component's basic structure. This skill turns each of those components into a complete product element a
frontend engineer could build from: the right anatomy for its kind, a clear hierarchy, its surface, spacing and
states, in the client's brand. It never changes what the wireframe owns. If a screen needs a structural, content or
behaviour change, that is a wireframe change: list it under **Wireframe gaps** and leave the screen as drawn.
Correcting a component's visual anatomy (a drawer's actions gathered into its footer, a Close word drawn as an icon
button) is this skill's job, within the rules in Step 9.

**Who owns what.** The wireframes skill carries the same table.

| Responsibility | Wireframe skill | Design system skill |
| --- | --- | --- |
| BRD interpretation | primary responsibility | consume and preserve |
| User journeys | define | preserve |
| Business rules | define and validate | preserve |
| Screen and state coverage | define | preserve |
| Content and data | define | preserve |
| Functional interactions | define and validate | preserve and style |
| Component identification | identify | catalogue and trace |
| Component anatomy | basic structural representation | refine and correct (Step 9) |
| Layout composition | functional and logical | visually optimise inside the wireframe's regions |
| Typography | minimal hierarchy | the complete type system |
| Colour and brand | minimal, greyscale | full brand treatment |
| Elevation and shadows | not used | applied where they separate surfaces |
| Visual states | functional representation | fully designed states |
| Final visual quality | not its objective | primary responsibility |

**Run it after the wireframes are approved and before the first build prompt.** Its output goes to UnifyApps
Headless (Nebula), which builds every page from its wireframe screen and styles it from this file.

---

# THE RUN

## Input contract

```
REQUIRED   the BRD                  the approved scoping document (02-scoping/scoping-document.docx, or a PDF)
           the wireframe HTML       02b-wireframes/<slug>-wireframes.html, made by the wireframes skill
DERIVED    client name, use case, website      from the BRD
           brand colour, logo, typeface, client design system, voice      researched (Steps 2–4)
USED IF GIVEN   anything the person or the caller supplies: a swatch, a logo file, a brand guide
```

**Nothing else is asked for.** Do not request PDFs, PNGs, screenshots or design references. Derive everything that
is derivable, record what you derived and where it came from, and keep going.

**Finding the inputs.** The wireframe HTML is the wireframes stage's only output; read it. (Its internal manifest in
`02b-wireframes/_working/` is generated from it; the HTML wins when they differ.) Two cases stop the run with one line
saying why:
- **No wireframe HTML**: "The design system styles the approved wireframe HTML; run the wireframes stage first."
- **A wireframe from before the HTML contract** (only `<slug>.wireframe.json` and PNGs, no HTML with `wf-meta`):
  "These wireframes predate the HTML contract; convert them with the wireframes skill ('Legacy wireframes') first."

**The tools are files in this skill, never typed by hand:** `scripts/ds_tool.py` (inventory, fidelity, audit, embed)
and `assets/ds-runtime.js`, which `ds_tool.py embed` puts into the page. Find the folder once:
```bash
D="$(ls -d ~/.claude/plugins/cache/*/poc-studio/*/skills/design-system 2>/dev/null | sort -V | tail -1)"; [ -n "$D" ] || D="$(dirname "$(dirname "$(find ~/.claude/plugins -path '*design-system/scripts/ds_tool.py' 2>/dev/null | head -1)")")"
T="$D/scripts/ds_tool.py"
```

## The only two stops

Do not ask anything else. Decide, record the decision in the QA report, move on. In an **unattended** run (the caller
says so, or nobody is there to answer), neither stop waits: take the unattended answer and record it.

1. **The brand hue is ambiguous**: two credible sources disagree by more than about 30° of hue. *Titan returned
   `#BD2426` (watch wordmark red) and `#00B0AB` (Tata parent teal), both real, 180° apart.* Attended: show both,
   transformed and measured, and wait. Unattended: take the higher source in the brand source order (Step 2) and
   record both candidates.
2. **The logo cannot be fetched as a real file.** Attended: ask for the asset. Unattended: use the stand-in the
   caller names, labelled as a stand-in, or else a text wordmark in the brand's type, visibly labelled a
   placeholder on the design-system page, and say so. **Never trace, redraw or approximate a client's mark**: not
   as SVG, not as CSS, not "close enough for a prototype".

---

## Step 0 · The system is in this file

**A brand skin is a transform of the existing system, never a re-derivation from prose.** The first attempt on a
client was built outward from a rules document. It obeyed every rule and was rejected in one line: *"NOT LIKE THIS …
USE EXACT THAT JUST REPLACE THE COLOURS."* Reading rules and building fresh produces something that follows the
rules and is not the system.

**So the system travels with this skill.** The first stylesheet below is Design Language v3.4, trimmed to the product
kit, with three deliberate changes. Every colour that rules used to hardcode is a token in `:root`, verified to render
pixel-identical to v3.4, so a brand transform touches `:root` alone. Its 20 font sizes are consolidated into five
type roles, and its font families and weights are tokens, so a declared token is the value that renders. Its dark
token block also applies to any element with the class `.ds-dark`, so the document can show light and dark side by
side. Six status text values were moved after measuring every status tag on every surface tier, the gradient
canvas and the wash included, composited, in both themes and both surface treatments, so each reaches 4.5:1
everywhere: light attention `#8A5A00` to `#825500` and positive `#1F6F5B` to `#1D6956`; dark neutral `#AAB7CB` to
`#C0CADA`, attention `#E3B45C` to `#EAC682`, negative `#EC9790` to `#F3BFBC` and positive `#86CDB4` to `#A2D9C5`. The two light elevations gained a contact edge (a 1px ring at 6–8% and a
short near shadow) because a white surface on a near-white page otherwise had no visible boundary where the large soft
shadow does not reach. The second stylesheet adds what the kit lacked:
spacing and size tokens, treatment switches, the app shell, overlays with header, body and footer regions, a document
component, banners, focus on every control, field and button edges that show on every surface, a true ground under
every gradient fill, and the classes the design-system page itself uses. This skill has no external dependency. Do not look for a reference file,
an artifact or a project document.

**How to use it:** paste both stylesheets verbatim, in order, as the page's only `<style>` block, then transform only
the colour values in the `:root` blocks (Step 6), and the two font tokens if Step 4 swaps a face. Structure, tiers,
radii, type roles, shadows, spacing and every component stay as written.

**Never rewrite a component from the prose in this file when a class for it exists below.** The prose says *why* a
component behaves as it does; the stylesheet says *what it is*. A second implementation is how one design system
quietly becomes two. It is the most common failure on this work, and it shows up as mixed radii and two kinds of
search field on one screen.

### The class inventory: use these, never write a second set

| Piece | Class |
| --- | --- |
| Glass tiers · padding · nested rung · solid | `.g1` `.g2` `.g3` `.pad` `.pad-s` `.inner` `.solid` |
| Ambient field (3 fixed layers) | `.amb.a` `.amb.b` `.amb.v` |
| Type | `.display` `.title` `h3.sub` `.micro` (mono eyebrow) |
| Layout | `.grid` `.g2c` `.g3c` `.g4c` `.stack` `.row` |
| Buttons · icon button · tags · pips | `.btn` `.btn-p` `.btn-s` `.btn-t` `.btn-i` (busy: `aria-busy="true"`) · `.tag` + `.neutral/.attention/.negative/.positive` · `.pip` |
| Table toolbar · search · facet · table | `.toolbar` `.field` `.chipsel` `.tblwrap` `.tbl` |
| Pagination | `.pg` `.pgb` `.rng` |
| AI Insight (scoped) | `.ai:not(.msg)` |
| Tiles · loop strip · empty | `.tile` `.loop` `.empty` |
| Fused tabs | `.tabs` `.tab` `.tabpanel` |
| Forms | `.fld` `.ctl` (+`.focus/.err/.warn/.off`) `.hint` `.seg` `.tog` `.opt` `.box` `.dot` `.drop` |
| Steppers · progress · reasoning stages | `.sth` `.stv` `.prog` `.stages` |
| Copilot | `.canvas` `.convo` `.msg.me` `.msg.ai` `.chips` |
| Kanban · calendar · agenda · slots | `.kb` `.cal` `.agenda` `.slot` |
| Person card · face stack · avatar | `.pc` `.faces` `.av` |
| Activity feed | `.feed` `.fi` `.fd` |
| Chart frame · sparkline · delta · legend | `.chart` `.spark` `.delta` `.legend` |
| Toast · menu · breadcrumb · note | `.toast` (`.toast.fixed` floats) `.menu` `.crumb` `.note` |
| **App shell** (additions) | `.app` (`.app.top` for a bar shell) `.app-rail` `.app-top` `.app-main` `.app-body` |
| **Overlays** (additions) | `.scrim` `.drawer` (`header` / `.body` / `footer`) `.modal` (`header`, content, `footer`) · anatomy regions on copied markup: `.pane` `.pane-head` `.pane-body` `.pane-foot` (Step 9) |
| **Gradients by role** (additions) | `data-canvas="glow"` (the app canvas and the top bar) · `.wash` (the signature component) |
| **Accessibility** (additions) | `.sr` (a control's word kept for screen readers when it is drawn as an icon) |
| **Feedback** (additions) | `.banner` + `.attention/.negative/.positive` (`.lead` for its first words) · `.skel` (static, never shimmering) |
| **Document** (additions) | `.doc` with the wireframe's document parts: `header`, `dl`, `.doc-parties`, `table`, `.num`, `.doc-totals` (`.grand`), `.doc-stamp`, `.doc-faint` |
| **Design-system page only** | `.ds-doc` `.ds-nav` `.ds-main` `.ds-sec` `.ds-facts` · catalogue `.ds-cat` `.ds-src` (the source line) `.ds-stage` · overlay stages `.ov` + `.drawer-s/.modal-s/.menu-s/.toast-s` · `.ds-states` (`.wide`) `.ds-parts` `.ds-scale` `.ds-icons` `.ds-compare` `.ds-dark` · `.ds-frame` (a styled screen) |

**Not in the kit, by choice:** the artefact studio, command palette, notification tray, diff view, bulk bar, slider
and file drop beyond `.drop`. Build one only when the wireframe contains it, from the tokens and the doctrine in the
REFERENCE section, never with new colour values. If one recurs across two builds, add it to the kit.

**`.ai` vs `.msg.ai`.** The AI Insight card is `.ai:not(.msg)` and agent chat bubbles are `.msg.ai`. An unscoped
`.ai` rule renders every conversation turn as an AI Insight card: invisible in light, obvious in dark. The kit is
already scoped; keep it that way.

### The foundations, as they really are

v3.4 promised "four type sizes, two weights" and shipped about 20 sizes. The kit now uses five roles and nothing
else, so a reader can learn the hierarchy at a glance and a builder can reproduce it. **Never add a size, weight,
spacing step, radius or shadow.**

| Foundation | Values (tokens) |
| --- | --- |
| Type roles | page heading 28 (`--fs-page`) · section heading 18 (`--fs-section`) · body 14 (`--fs-body`) · supporting text 12.5 (`--fs-support`) · compact metadata 11 (`--fs-meta`), set in the mono face for identifiers, table headers, eyebrows and timestamps · `--glyph-xs` 8 sizes two icon glyphs and is not a type role |
| Faces | `--font-ui` (Archivo, or Step 4's choice) and `--font-mono` (IBM Plex Mono) |
| Weights | 400 (`--fw-regular`) for reading, 600 (`--fw-strong`) for headings, labels and actions, 500 (`--fw-medium`) only for facet chips and nav links |
| Numerals | `tabular-nums` on every number |
| Spacing | 4 · 6 · 10 · 12 · 16 · 22 · 30 · 44 (`--sp-1` … `--sp-8`) between components and regions; the kit's own paddings stay as written |
| Sizes | rail 232 (`--rail-w`) · drawer 480 (`--drawer-w`) · modal 520 (`--modal-w`) · minimum target 40 (`--tap`) |
| Radius | 10 (`--r`) for cards, inputs, buttons' containers, panes, drawers, modals · 6 (`--r-sm`) for tags, chips, code · pill for search, facets, buttons, accent pills · circle for avatars · studio only 28/22/16/12 |
| Elevation | two levels, `--lift-1` resting and `--lift-2` raised, each with a contact edge (a faint 1px ring and a short near shadow) so a surface's boundary shows on every side, with the 1px inset top edge `--edge` |
| Motion | `--ease` (150 ms), on panes, drawers and tonal hover only; nothing else moves; reduced motion removes it all |
| Treatment switches | `data-surface="glass"` (as shipped) or `"solid"` · `data-fill="gradient"` (as shipped) or `"flat"` · `data-canvas="glow"` or `"plain"` · `data-labels="eyebrow"` (as shipped) or `"sentence"`, all on `<html>` (Step 5) |
| Edges | a field's outline is `--line-ctl` (3:1 on its surface, WCAG 1.4.11); a secondary button's edge is `--line-btn` |

### The stylesheets

**Paste both verbatim, in this order.** Inventory before transforming: the pair carries 50 distinct hexes, 20
distinct `rgb()` triples, and 15 bare-triple tokens. The bare-triple tokens are `--aur-a` `--aur-b` `--aur-c`
`--brand-rgb` `--fill-glow-rgb` `--accent-rgb` `--deep-rgb` `--warn-rgb` `--neg-rgb` `--shadow-rgb` `--shadow-dk-rgb`
`--tint-dk-rgb` `--edge-dk-rgb` `--deep-dk-rgb` `--accent-dk-rgb`. Count, transform, then diff the count.

**Bare triples are the trap.** Bare-triple tokens are declared as `0,113,206` and consumed as `rgba(var(--brand-rgb),a)`.
There is no `rgb(` to match, so a find-and-replace over hexes and `rgba(...)` skips them and leaves the ambient
field, focus rings, shadows and dark-mode tints on the previous brand. At 5% opacity that does not look broken. It
just casts the page in the wrong hue.

Design Language v3.4: colours tokenised, type consolidated, dark scope added:

```css
:root{--fill-1:#0071CE;--fill-2:#005DB4;--fill-3:#0035A6;--fill-3b:#0056B4;--fill-3c:#0059B6;--fill-deep:#0033A1;--fill-av:#0058B8;--ok-fill-1:#2C8A74;--ok-fill-2:#1F6F5B;--warn-fill-1:#A87213;--warn-fill-2:#8A5A00;--alt-fill-1:#B93CA5;--alt-fill-2:#8C1E79;--brand-rgb:0,113,206;--fill-glow-rgb:0,63,168;--accent-rgb:204,39,176;--deep-rgb:0,51,161;--warn-rgb:138,90,0;--neg-rgb:150,48,42;--shadow-rgb:6,22,54;--shadow-dk-rgb:2,6,14;--tint-dk-rgb:120,165,225;--edge-dk-rgb:214,232,255;--deep-dk-rgb:76,127,232;--accent-dk-rgb:232,132,214;--sp-deep:#0033A1;--sp-blue:#0071CE;--sp-cerise:#CC27B0;--sp-pink:#E17FD2;--base:#F1F5FB;--page-top:rgba(0,51,161,.022);--glass-1:rgba(255,255,255,.72);--glass-2:rgba(255,255,255,.82);--glass-3:rgba(255,255,255,.93);--glass-solid:rgba(255,255,255,.965);--inner:rgba(0,51,161,.045);--edge:inset 0 1px 0 rgba(255,255,255,.92);--blur-1:blur(22px) saturate(160%);--blur-2:blur(26px) saturate(170%);--ink:#0B1220;--ink-2:#47566B;--ink-3:#626D84;--ink-mute:#8E9AAE;--hair:rgba(11,18,32,.07);--hair-2:rgba(11,18,32,.12);--st-neutral:#47566B;--st-neutral-t:rgba(71,86,107,.10);--st-attention:#825500;--st-attention-t:rgba(138,90,0,.11);--st-negative:#96302A;--st-negative-t:rgba(150,48,42,.11);--st-positive:#1D6956;--st-positive-t:rgba(31,111,91,.11);--c1:#00325C;--c2:#005194;--c3:#0070CC;--c4:#0A90FF;--c5:#47ACFF;--c6:#85C8FF;--r:10px;--r-sm:6px;--r-pill:999px;--lift-1:0 0 0 1px rgba(6,22,54,.06),0 1px 3px rgba(6,22,54,.08),0 12px 32px -18px rgba(6,22,54,.28);--lift-2:0 0 0 1px rgba(6,22,54,.08),0 4px 12px rgba(6,22,54,.10),0 28px 60px -26px rgba(6,22,54,.40);--ease:150ms cubic-bezier(.22,.7,.28,1);--aur-a:0,51,161;--aur-b:0,113,206;--aur-c:204,39,176;--aur-1:.055;--aur-2:.045;--aur-3:.050;--vig:radial-gradient(120% 100% at 50% 40%,transparent 42%,rgba(6,18,46,.10) 100%)} @media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--base:#192030;--page-top:rgba(120,165,225,.055);--glass-1:rgba(120,165,225,.12);--glass-2:rgba(120,165,225,.17);--glass-3:rgba(120,165,225,.23);--glass-solid:#2F3D57;--inner:rgba(130,175,235,.085);--edge:inset 0 1px 0 rgba(214,232,255,.17);--ink:#D8E0EC;--ink-2:#AAB7CB;--ink-3:#9FADC3;--ink-mute:#78869F;--hair:rgba(206,224,255,.10);--hair-2:rgba(206,224,255,.17);--sp-blue:#6BB3EA;--sp-deep:#3A72DE;--sp-cerise:#E884D6;--sp-pink:#F2BCE9;--st-neutral:#C0CADA;--st-neutral-t:rgba(170,183,203,.12);--st-attention:#EAC682;--st-attention-t:rgba(227,180,92,.13);--st-negative:#F3BFBC;--st-negative-t:rgba(236,151,144,.13);--st-positive:#A2D9C5;--st-positive-t:rgba(134,205,180,.13);--c1:#E6F2FF;--c2:#B9DDFF;--c3:#8CC6F8;--c4:#62ADEC;--c5:#3F90D6;--c6:#3576B0;--lift-1:0 1px 2px rgba(2,6,14,.46),0 14px 34px -18px rgba(2,6,14,.68);--lift-2:0 2px 7px rgba(2,6,14,.52),0 32px 66px -26px rgba(2,6,14,.80);--aur-a:76,127,232;--aur-b:107,179,234;--aur-c:232,132,214;--aur-1:.26;--aur-2:.19;--aur-3:.22;--vig:radial-gradient(120% 100% at 55% 42%,transparent 50%,rgba(6,11,22,.30) 100%)} }:root[data-theme="dark"],.ds-dark{--base:#192030;--page-top:rgba(120,165,225,.055);--glass-1:rgba(120,165,225,.12);--glass-2:rgba(120,165,225,.17);--glass-3:rgba(120,165,225,.23);--glass-solid:#2F3D57;--inner:rgba(130,175,235,.085);--edge:inset 0 1px 0 rgba(214,232,255,.17);--ink:#D8E0EC;--ink-2:#AAB7CB;--ink-3:#9FADC3;--ink-mute:#78869F;--hair:rgba(206,224,255,.10);--hair-2:rgba(206,224,255,.17);--sp-blue:#6BB3EA;--sp-deep:#3A72DE;--sp-cerise:#E884D6;--sp-pink:#F2BCE9;--st-neutral:#C0CADA;--st-neutral-t:rgba(170,183,203,.12);--st-attention:#EAC682;--st-attention-t:rgba(227,180,92,.13);--st-negative:#F3BFBC;--st-negative-t:rgba(236,151,144,.13);--st-positive:#A2D9C5;--st-positive-t:rgba(134,205,180,.13);--c1:#E6F2FF;--c2:#B9DDFF;--c3:#8CC6F8;--c4:#62ADEC;--c5:#3F90D6;--c6:#3576B0;--lift-1:0 1px 2px rgba(2,6,14,.46),0 14px 34px -18px rgba(2,6,14,.68);--lift-2:0 2px 7px rgba(2,6,14,.52),0 32px 66px -26px rgba(2,6,14,.80);--aur-a:76,127,232;--aur-b:107,179,234;--aur-c:232,132,214;--aur-1:.26;--aur-2:.19;--aur-3:.22;--vig:radial-gradient(120% 100% at 55% 42%,transparent 50%,rgba(6,11,22,.30) 100%)} *{box-sizing:border-box} body{background:var(--base);background-image:linear-gradient(176deg,var(--page-top) 0%,transparent 46%);color:var(--ink);font-family:var(--font-ui);font-size:var(--fs-body);line-height:1.6;font-variant-numeric:tabular-nums;letter-spacing:-.003em;-webkit-font-smoothing:antialiased;position:relative} .amb{position:fixed;inset:-10%;pointer-events:none;z-index:0} .amb.a{filter:blur(84px);background:radial-gradient(62% 52% at 12% 4%,rgba(var(--aur-a),var(--aur-1)),transparent 72%),radial-gradient(56% 48% at 90% 20%,rgba(var(--aur-b),var(--aur-3)),transparent 72%),radial-gradient(64% 54% at 28% 82%,rgba(var(--aur-a),var(--aur-1)),transparent 74%)} .amb.b{filter:blur(70px);opacity:.9;background:radial-gradient(50% 42% at 78% 64%,rgba(var(--aur-c),var(--aur-2)),transparent 72%),radial-gradient(44% 38% at 6% 44%,rgba(var(--aur-c),var(--aur-2)),transparent 72%)} .amb.v{background:var(--vig)} .display{font-size:var(--fs-page);line-height:1.12;font-weight:var(--fw-strong);letter-spacing:-.028em;margin:0;text-wrap:balance} .title{font-size:var(--fs-section);line-height:1.3;font-weight:var(--fw-strong);letter-spacing:-.014em;margin:0} p,li,td,th{font-size:var(--fs-body);line-height:1.6;font-weight:var(--fw-regular);margin:0} .micro{font-family:var(--font-mono);font-size:var(--fs-meta);line-height:1.4;font-weight:var(--fw-strong);letter-spacing:.09em;text-transform:uppercase} header.mast{padding-block:76px 30px;display:flex;flex-direction:column;gap:16px} header.mast .micro{color:var(--sp-blue)} header.mast p{color:var(--ink-2);max-width:64ch;font-size:var(--fs-section);line-height:1.6} h3.sub{font-size:var(--fs-body);font-weight:var(--fw-strong);margin:0;letter-spacing:-.008em} .g1,.g2,.g3{border-radius:var(--r);position:relative} .g1{background:var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);box-shadow:var(--lift-1),var(--edge)} .g2{background:var(--glass-2);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);box-shadow:var(--lift-2),var(--edge)} .g3{background:var(--glass-3);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);box-shadow:var(--lift-1),var(--edge)} .pad{padding:22px} .pad-s{padding:16px 18px} .inner{background:var(--inner);border-radius:var(--r-sm);padding:14px 16px} .solid{background:var(--glass-solid);border-radius:var(--r);box-shadow:var(--lift-1),var(--edge)} .grid{display:grid;gap:16px} .g2c{grid-template-columns:repeat(auto-fit,minmax(272px,1fr))} .g3c{grid-template-columns:repeat(auto-fit,minmax(205px,1fr))} .g4c{grid-template-columns:repeat(auto-fit,minmax(158px,1fr))} .stack{display:flex;flex-direction:column;gap:12px} .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap} .sw{border-radius:var(--r);overflow:hidden;background:var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);box-shadow:var(--lift-1),var(--edge)} .btn{font-family:inherit;font-size:var(--fs-body);font-weight:var(--fw-strong);border:0;border-radius:var(--r-pill);padding:10px 20px;cursor:pointer;letter-spacing:-.006em;transition:transform var(--ease),box-shadow var(--ease),background var(--ease)} .btn-p{background:linear-gradient(180deg,var(--fill-1) 0%,var(--fill-2) 42%,var(--fill-3) 100%);color:#fff;box-shadow:0 1px 1px rgba(var(--shadow-rgb),.18),0 10px 22px -12px rgba(var(--fill-glow-rgb),.70),inset 0 1px 0 rgba(255,255,255,.28)} .btn-p:hover{transform:translateY(-1px);box-shadow:0 1px 1px rgba(var(--shadow-rgb),.20),0 16px 30px -14px rgba(var(--fill-glow-rgb),.80),inset 0 1px 0 rgba(255,255,255,.32)} .btn-s{background:var(--glass-2);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);color:var(--ink);box-shadow:var(--lift-1),var(--edge)} .btn-t{background:transparent;color:var(--ink-2);padding-inline:12px} .btn-t:hover{background:var(--inner)} .btn:disabled{background:var(--inner);color:var(--ink-mute);box-shadow:none;cursor:not-allowed;transform:none} .btn:focus-visible{outline:2px solid var(--sp-blue);outline-offset:3px} .tag{display:inline-flex;align-items:center;gap:5px;font-size:var(--fs-meta);font-weight:var(--fw-strong);line-height:1.3;padding:4px 11px;border-radius:var(--r-pill);background:var(--inner);color:var(--ink-2);letter-spacing:.01em} .tag.neutral{background:var(--st-neutral-t);color:var(--st-neutral)} .tag.attention{background:var(--st-attention-t);color:var(--st-attention)} .tag.negative{background:var(--st-negative-t);color:var(--st-negative)} .tag.positive{background:var(--st-positive-t);color:var(--st-positive)} .tag svg{width:12px;height:12px;flex:none} .pips{display:inline-flex;gap:6px;align-items:center} .pip{width:14px;height:14px;border-radius:50%;display:grid;place-items:center} .pip.done{background:linear-gradient(180deg,var(--ok-fill-1),var(--ok-fill-2));box-shadow:inset 0 1px 0 rgba(255,255,255,.3)} .pip.draft{background:linear-gradient(180deg,var(--warn-fill-1),var(--warn-fill-2));box-shadow:inset 0 1px 0 rgba(255,255,255,.28)} .pip.stale{background:var(--st-attention-t);box-shadow:inset 0 0 0 1.8px var(--st-attention)} .pip.missing{background:transparent;box-shadow:inset 0 0 0 1.5px var(--hair-2)} .pip i{font-style:normal;font-family:var(--font-mono);font-size:var(--glyph-xs);font-weight:var(--fw-strong);color:#fff;line-height:1} .pip.stale i{color:var(--st-attention)} .pip.missing i{color:var(--ink-mute)} .tblwrap{overflow-x:auto;border-radius:var(--r);background:var(--glass-solid);box-shadow:var(--lift-1),var(--edge)} .tbl{width:100%;border-collapse:collapse} .tbl thead th{text-align:left;padding:12px 16px;color:var(--ink-3);font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);letter-spacing:.09em;text-transform:uppercase;white-space:nowrap;border-bottom:1px solid var(--hair)} .tbl tbody td{padding:13px 16px;border-top:1px solid var(--hair);vertical-align:middle} .tbl tbody tr:first-child td{border-top:0} .tbl tbody tr{transition:background var(--ease)} .tbl tbody tr:hover{background:var(--inner)} .tbl .n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap} .toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding-bottom:14px} .field{flex:1;min-width:190px;display:flex;align-items:center;gap:9px;background:var(--glass-2);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);border-radius:var(--r-pill);padding:9px 15px;color:var(--ink-3);box-shadow:var(--edge),0 1px 2px rgba(var(--shadow-rgb),.04)} .field input{border:0;background:transparent;font-family:inherit;font-size:var(--fs-body);color:var(--ink);width:100%;outline:none} .chipsel{background:var(--glass-2);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);border-radius:var(--r-pill);padding:9px 14px;font-size:var(--fs-support);font-weight:var(--fw-medium);color:var(--ink-2);display:flex;gap:7px;align-items:center;box-shadow:var(--edge),0 1px 2px rgba(var(--shadow-rgb),.04)} .tabs{display:flex;gap:3px;padding:0 5px} .tab{font-family:inherit;font-size:var(--fs-body);font-weight:var(--fw-strong);border:0;background:transparent;color:var(--ink-3);padding:11px 16px;border-radius:var(--r) var(--r) 0 0;cursor:pointer;transition:color var(--ease),background var(--ease)} .tab[aria-selected="true"]{background:var(--glass-2);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);color:var(--ink);box-shadow:var(--edge)} .tabpanel{background:var(--glass-2);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);border-radius:0 var(--r) var(--r) var(--r);box-shadow:var(--lift-1),var(--edge);padding:20px} .ai:not(.msg){border-radius:var(--r);padding:18px 20px;display:flex;flex-direction:column;gap:10px;background:linear-gradient(135deg,rgba(var(--deep-rgb),.075) 0%,rgba(var(--brand-rgb),.045) 48%,rgba(var(--accent-rgb),.065) 100%),var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);box-shadow:var(--lift-1),var(--edge)} .ai .hd{display:flex;align-items:center;gap:8px} .ai .hd .micro{color:var(--sp-blue)} .ai p{color:var(--ink)} .ai .ground{font-size:var(--fs-support);color:var(--ink-3)} .ai .foot{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap} .chev{background:transparent;border:0;color:var(--ink-3);font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);letter-spacing:.07em;text-transform:uppercase;cursor:pointer;padding:0} .tile{border-radius:var(--r);padding:18px 20px;display:flex;flex-direction:column;gap:7px;background:linear-gradient(180deg,rgba(255,255,255,.28),rgba(255,255,255,0)),var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);box-shadow:var(--lift-1),var(--edge)} .tile .micro{color:var(--ink-3)} .tile .v{font-size:var(--fs-page);font-weight:var(--fw-strong);line-height:1.08;letter-spacing:-.03em} .tile .sub{font-size:var(--fs-support);color:var(--ink-3);line-height:1.45} .tile.flag{background:linear-gradient(180deg,rgba(var(--warn-rgb),.10),rgba(var(--warn-rgb),.04)),var(--glass-1)} .tile.flag .v{color:var(--st-attention)} .loop{display:flex;border-radius:var(--r);overflow:hidden;background:var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);box-shadow:var(--lift-1),var(--edge)} .loop div{flex:1;padding:14px 16px;display:flex;flex-direction:column;gap:4px} .loop div + div{border-left:1px solid var(--hair)} .loop .micro{color:var(--ink-3)} .loop b{font-size:var(--fs-section);font-weight:var(--fw-strong);letter-spacing:-.02em} .loop .on{background:linear-gradient(180deg,rgba(var(--brand-rgb),.10),rgba(var(--brand-rgb),.03))} .loop .on b{color:var(--sp-blue)} .rail-demo{border-radius:var(--r);overflow:hidden;box-shadow:var(--lift-2);display:flex;min-height:230px} .empty{border-radius:var(--r);padding:28px 22px;display:flex;flex-direction:column;gap:12px;align-items:flex-start;background:var(--inner)} .legend{display:flex;gap:16px;flex-wrap:wrap} .legend i{width:10px;height:10px;border-radius:3px;display:inline-block;margin-right:7px} .legend span{font-size:var(--fs-support);color:var(--ink-2);display:inline-flex;align-items:center} code.inl{font-family:var(--font-mono);font-size:var(--fs-support);background:var(--inner);padding:2px 6px;border-radius:var(--r-sm);color:var(--ink-2)} .note{border-radius:var(--r);padding:16px 18px;display:flex;flex-direction:column;gap:7px;background:linear-gradient(180deg,rgba(var(--warn-rgb),.09),rgba(var(--warn-rgb),.03)),var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);box-shadow:var(--lift-1),var(--edge)} .note .micro{color:var(--st-attention)} .note p{color:var(--ink)} @media (max-width:640px){.loop{flex-direction:column} .loop div + div{border-left:0;border-top:1px solid var(--hair)} .rail-demo{flex-direction:column} .rail-demo .nav{width:auto} } @media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}} .fld{display:flex;flex-direction:column;gap:6px} .fld > label{font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3)} .ctl{display:flex;align-items:center;gap:9px;background:var(--glass-2);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);border-radius:var(--r);padding:11px 14px;box-shadow:var(--edge),0 1px 2px rgba(var(--shadow-rgb),.04);transition:box-shadow var(--ease)} .ctl input,.ctl textarea,.ctl select{border:0;background:transparent;font-family:inherit;font-size:var(--fs-body);color:var(--ink);width:100%;outline:none;letter-spacing:-.003em} .ctl textarea{resize:vertical;min-height:76px;line-height:1.55} .ctl.focus{box-shadow:var(--edge),0 0 0 3px rgba(var(--brand-rgb),.18),0 1px 2px rgba(var(--shadow-rgb),.05)} .ctl.err{box-shadow:var(--edge),0 0 0 3px rgba(var(--neg-rgb),.16),0 1px 2px rgba(var(--shadow-rgb),.05);background:linear-gradient(0deg,var(--st-negative-t),var(--st-negative-t)),var(--glass-2)} .ctl.warn{box-shadow:var(--edge),0 0 0 3px rgba(var(--warn-rgb),.15),0 1px 2px rgba(var(--shadow-rgb),.05);background:linear-gradient(0deg,var(--st-attention-t),var(--st-attention-t)),var(--glass-2)} .ctl.off{background:var(--inner);box-shadow:none} .ctl.off input{color:var(--ink-mute)} .hint{font-size:var(--fs-support);color:var(--ink-3);line-height:1.45} .hint.e{color:var(--st-negative);display:flex;gap:6px;align-items:flex-start} .hint.w{color:var(--st-attention);display:flex;gap:6px;align-items:flex-start} .hint svg{width:13px;height:13px;flex:none;margin-top:2px} .req{color:var(--st-negative);font-weight:var(--fw-strong)} .seg{display:inline-flex;gap:2px;padding:3px;border-radius:var(--r-pill);background:var(--inner)} .seg button{font-family:inherit;font-size:var(--fs-support);font-weight:var(--fw-strong);border:0;background:transparent;color:var(--ink-3);padding:7px 16px;border-radius:var(--r-pill);cursor:pointer;letter-spacing:-.004em;transition:color var(--ease),background var(--ease)} .seg button[aria-pressed="true"]{background:var(--glass-3);color:var(--ink);box-shadow:var(--edge),0 1px 3px rgba(var(--shadow-rgb),.10)} .tog{display:inline-flex;align-items:center;gap:11px;cursor:pointer} .tog .track{width:44px;height:26px;border-radius:var(--r-pill);background:var(--inner);position:relative;transition:background var(--ease);box-shadow:inset 0 1px 2px rgba(var(--shadow-rgb),.08)} .tog .track .knob{position:absolute;top:3px;left:3px;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(var(--shadow-rgb),.28),inset 0 1px 0 rgba(255,255,255,.9);transition:transform var(--ease)} .tog.on .track{background:linear-gradient(180deg,var(--fill-1),var(--fill-2) 60%,var(--fill-3b))} .tog.on .track .knob{transform:translateX(18px)} .tog span{font-size:var(--fs-body);color:var(--ink-2)} .opt{display:inline-flex;align-items:flex-start;gap:10px;cursor:pointer;font-size:var(--fs-body);color:var(--ink-2)} .box,.dot{width:19px;height:19px;flex:none;border-radius:var(--r-sm);background:var(--glass-3);box-shadow:var(--edge),inset 0 0 0 1px var(--hair-2);display:grid;place-items:center;margin-top:1px} .dot{border-radius:50%} .opt.on .box,.opt.on .dot{background:linear-gradient(180deg,var(--fill-1),var(--fill-2) 60%,var(--fill-3b));box-shadow:inset 0 1px 0 rgba(255,255,255,.3),0 1px 3px rgba(var(--fill-glow-rgb),.35)} .box svg,.dot svg{width:12px;height:12px;color:#fff;opacity:0} .opt.on .box svg{opacity:1} .opt.on .dot::after{content:"";width:7px;height:7px;border-radius:50%;background:#fff} .sl{display:flex;flex-direction:column;gap:9px} .drop{border-radius:var(--r);padding:26px 20px;background:var(--inner);display:flex;flex-direction:column;align-items:center;gap:9px;text-align:center} .sth{display:flex;align-items:flex-start;gap:0} .sth .nd{flex:1;display:flex;flex-direction:column;gap:8px;position:relative;padding-top:2px} .sth .bar{display:flex;align-items:center;gap:0} .sth .cir{width:26px;height:26px;border-radius:50%;flex:none;display:grid;place-items:center;font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong)} .sth .cir.done{background:linear-gradient(180deg,var(--ok-fill-1),var(--ok-fill-2));color:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.3)} .sth .cir.now{background:linear-gradient(180deg,var(--fill-1),var(--fill-2) 60%,var(--fill-3));color:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.3),0 0 0 4px rgba(var(--brand-rgb),.14)} .sth .cir.todo{background:var(--glass-3);color:var(--ink-mute);box-shadow:var(--edge),inset 0 0 0 1px var(--hair-2)} .sth .cir.block{background:var(--st-negative-t);color:var(--st-negative);box-shadow:inset 0 0 0 1.5px var(--st-negative)} .sth .ln{flex:1;height:2px;background:var(--hair-2);border-radius:2px} .sth .ln.done{background:linear-gradient(90deg,var(--ok-fill-2),var(--ok-fill-1))} .sth .lbl{font-size:var(--fs-support);font-weight:var(--fw-strong);letter-spacing:-.006em;padding-right:12px} .sth .sub{font-size:var(--fs-support);color:var(--ink-3);padding-right:12px;line-height:1.45} .stv{display:flex;flex-direction:column} .stv .nd{display:grid;grid-template-columns:26px minmax(0,1fr);gap:0 14px;position:relative;padding-bottom:16px} .stv .nd:last-child{padding-bottom:0} .stv .nd::before{content:"";position:absolute;left:12.5px;top:26px;bottom:0;width:2px;background:var(--hair-2)} .stv .nd:last-child::before{display:none} .stv .cir{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);z-index:1} .stv .c{display:flex;flex-direction:column;gap:6px;padding-top:2px;min-width:0} .stv .hdr{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap} .stv .hdr b{font-size:var(--fs-body);font-weight:var(--fw-strong);letter-spacing:-.006em} .stv .hdr .when{font-family:var(--font-mono);font-size:var(--fs-meta);color:var(--ink-3);letter-spacing:.05em} .stv .ev{font-size:var(--fs-body);color:var(--ink-2);line-height:1.5} .pad ul,.stack ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:10px} .pad ul li,.stack ul li{position:relative;padding-left:17px;font-size:var(--fs-body);line-height:1.6;color:var(--ink-2)} .pad ul li::before{content:"";position:absolute;left:1px;top:8px;width:5px;height:5px;border-radius:50%;background:var(--sp-blue);opacity:.5} .stack ul li::before{content:"";position:absolute;left:1px;top:8px;width:5px;height:5px;border-radius:50%;background:var(--sp-blue);opacity:.5} .pad ul li b,.stack ul li b{color:var(--ink);font-weight:var(--fw-strong)} .prog{height:6px;border-radius:var(--r-pill);background:var(--inner);overflow:hidden;box-shadow:inset 0 1px 2px rgba(var(--shadow-rgb),.08)} .prog i{display:block;height:100%;border-radius:var(--r-pill);background:linear-gradient(90deg,var(--fill-deep),var(--fill-1))} .prog.mini{width:130px;height:4px;flex:none} .stages{display:flex;flex-direction:column;gap:9px} .stages div{display:flex;gap:10px;align-items:center;font-size:var(--fs-body)} .stages .tick{width:16px;height:16px;border-radius:50%;flex:none;display:grid;place-items:center} .stages .tick.ok{background:var(--st-positive-t);color:var(--st-positive)} .stages .tick.run{background:var(--inner);box-shadow:inset 0 0 0 1.5px var(--sp-blue)} .stages .tick.wait{background:var(--inner);box-shadow:inset 0 0 0 1.5px var(--hair-2)} .stages .ok + span{color:var(--ink-2)} .stages .run + span{color:var(--ink);font-weight:var(--fw-strong)} .stages .wait + span{color:var(--ink-mute)} .scene{position:relative;border-radius:var(--r);overflow:hidden;background:var(--glass-3);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);box-shadow:var(--lift-2),var(--edge);min-height:340px} .three{display:grid;grid-template-columns:132px minmax(0,1fr) 250px;gap:1px;border-radius:var(--r);overflow:hidden;background:var(--hair);box-shadow:var(--lift-1),var(--edge);min-height:270px} .toast{display:inline-flex;align-items:center;gap:13px;padding:13px 16px;border-radius:var(--r);background:var(--glass-2);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);box-shadow:var(--lift-2),var(--edge)} .toast .ic{width:22px;height:22px;border-radius:50%;flex:none;display:grid;place-items:center;background:var(--st-positive-t);color:var(--st-positive)} .toast b{font-size:var(--fs-body);font-weight:var(--fw-strong);letter-spacing:-.006em} .toast small{display:block;font-size:var(--fs-support);color:var(--ink-3)} .toast .undo{font-family:inherit;font-size:var(--fs-support);font-weight:var(--fw-strong);color:var(--sp-blue);background:transparent;border:0;cursor:pointer;padding:0 2px} .menu{width:236px;border-radius:var(--r);padding:6px;background:var(--glass-2);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);box-shadow:var(--lift-2),var(--edge);display:flex;flex-direction:column;gap:1px} .menu a{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:9px 12px;border-radius:var(--r-sm);font-size:var(--fs-body);color:var(--ink-2);text-decoration:none} .menu a:hover{background:var(--inner);color:var(--ink)} .menu a kbd{font-family:var(--font-mono);font-size:var(--fs-meta);color:var(--ink-3)} .menu hr{height:1px;background:var(--hair);border:0;margin:5px 0} .menu a.danger{color:var(--st-negative)} .crumb{display:flex;align-items:center;gap:8px;font-size:var(--fs-support);color:var(--ink-3);flex-wrap:wrap} .crumb a{color:var(--ink-2);text-decoration:none} .crumb a:hover{color:var(--ink)} .crumb b{color:var(--ink);font-weight:var(--fw-strong)} .av{width:30px;height:30px;border-radius:50%;flex:none;display:grid;place-items:center;font-size:var(--fs-meta);font-weight:var(--fw-strong);color:#fff;background:linear-gradient(150deg,var(--fill-av),var(--fill-deep));box-shadow:inset 0 1px 0 rgba(255,255,255,.22),0 1px 3px rgba(var(--shadow-rgb),.20)} .av.c2{background:linear-gradient(150deg,var(--alt-fill-1),var(--alt-fill-2))} .canvas{border-radius:var(--r);overflow:hidden;box-shadow:var(--lift-2),var(--edge);background:var(--glass-3);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);min-height:420px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:20px;padding:36px 24px;text-align:center;position:relative} .canvas .glowwrap{width:100%;max-width:520px;padding:26px} .canvas .composer{position:relative;display:flex;align-items:center;gap:11px;padding:15px 18px;border-radius:var(--r);background:var(--glass-2);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);box-shadow:var(--edge),0 2px 6px rgba(var(--shadow-rgb),.07),0 0 34px -6px rgba(var(--brand-rgb),.38),0 0 60px -10px rgba(var(--accent-rgb),.26)} .canvas .composer input{border:0;background:transparent;font-family:inherit;font-size:var(--fs-body);color:var(--ink);width:100%;outline:none;letter-spacing:-.006em} .canvas .composer input::placeholder{color:var(--ink-3)} .canvas h3{font-family:inherit;font-size:var(--fs-page);font-weight:var(--fw-strong);letter-spacing:-.024em;margin:0;line-height:1.2} .canvas .sublede{font-size:var(--fs-body);color:var(--ink-3);max-width:46ch;margin:0} .chips{display:flex;gap:9px;flex-wrap:wrap;justify-content:center} .chips button{font-family:inherit;font-size:var(--fs-support);font-weight:var(--fw-medium);color:var(--ink-2);background:var(--glass-2);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);border:0;border-radius:var(--r-pill);padding:8px 15px;cursor:pointer;box-shadow:var(--edge),0 1px 2px rgba(var(--shadow-rgb),.04)} .chips button:hover{color:var(--ink)} .proactive{width:100%;max-width:560px;display:flex;flex-direction:column;gap:10px;text-align:left} .convo{border-radius:var(--r);overflow:hidden;box-shadow:var(--lift-1),var(--edge);background:var(--glass-3);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);display:flex;flex-direction:column;min-height:420px} .convo .thread{flex:1;padding:18px;display:flex;flex-direction:column;gap:14px} .convo .dock{padding:14px 16px;display:flex;flex-direction:column;gap:10px;background:var(--glass-2);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);box-shadow:inset 0 1px 0 var(--hair)} .convo .dock .composer{display:flex;align-items:center;gap:11px;padding:12px 15px;border-radius:var(--r);background:var(--glass-3);box-shadow:var(--edge),0 1px 2px rgba(var(--shadow-rgb),.05)} .convo .dock .composer input{border:0;background:transparent;font-family:inherit;font-size:var(--fs-body);color:var(--ink);width:100%;outline:none} .msg{max-width:78%;display:flex;flex-direction:column;gap:5px} .msg.me{align-self:flex-end;align-items:flex-end} .msg.ai{align-self:flex-start} .msg .who{font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3)} .msg .bub{padding:12px 15px;border-radius:var(--r);font-size:var(--fs-body);line-height:1.55} .msg.me .bub{background:linear-gradient(180deg,var(--fill-1),var(--fill-2) 62%,var(--fill-3c));color:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.24),0 6px 16px -10px rgba(var(--fill-glow-rgb),.6)} .msg.ai .bub{background:var(--glass-2);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);color:var(--ink);box-shadow:var(--edge),0 1px 2px rgba(var(--shadow-rgb),.05)} .raildrw{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:1px;border-radius:var(--r);overflow:hidden;background:var(--hair);box-shadow:var(--lift-1),var(--edge);min-height:310px} @media (max-width:760px){.three{grid-template-columns:minmax(0,1fr)} .raildrw{grid-template-columns:minmax(0,1fr)} .sth{flex-direction:column;gap:14px} .sth .ln{display:none} } .scene{min-height:380px} .scope{display:inline-flex;align-items:center;gap:8px;align-self:flex-start;padding:5px 10px 5px 8px;border-radius:var(--r-pill);background:rgba(var(--brand-rgb),.10);color:var(--sp-blue);font-size:var(--fs-support);font-weight:var(--fw-strong)} .cmdk{width:min(520px,100%);border-radius:var(--r);overflow:hidden;background:var(--glass-2);backdrop-filter:var(--blur-2);-webkit-backdrop-filter:var(--blur-2);box-shadow:var(--lift-2),var(--edge)} @media (max-width:860px){.diff > div{grid-template-columns:minmax(0,1fr)} }:root{--r-shell:28px;--r-canvas:22px;--r-sheet:16px;--r-tile:12px} @media (max-width:900px){.bleed{margin-inline:0}} .studio2{position:relative;border-radius:var(--r-shell);display:grid;grid-template-columns:318px minmax(0,1fr);min-height:600px;overflow:hidden;background:linear-gradient(112deg,rgba(255,255,255,.74) 0%,rgba(255,255,255,.52) 26%,rgba(255,255,255,.28) 52%,rgba(255,255,255,.14) 100%),radial-gradient(60% 80% at 4% 0%,rgba(var(--deep-rgb),.10),transparent 70%),radial-gradient(52% 66% at 100% 100%,rgba(var(--accent-rgb),.09),transparent 72%);backdrop-filter:blur(30px) saturate(180%);-webkit-backdrop-filter:blur(30px) saturate(180%);box-shadow:var(--lift-2),inset 0 1px 0 rgba(255,255,255,.95)}:root[data-theme="dark"] .studio2,:root:not([data-theme="light"]) .studio2,.ds-dark .studio2{} @media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .studio2{background:linear-gradient(112deg,rgba(var(--tint-dk-rgb),.24) 0%,rgba(var(--tint-dk-rgb),.17) 30%,rgba(var(--tint-dk-rgb),.11) 60%,rgba(var(--tint-dk-rgb),.07) 100%),radial-gradient(60% 80% at 4% 0%,rgba(var(--deep-dk-rgb),.20),transparent 70%),radial-gradient(52% 66% at 100% 100%,rgba(var(--accent-dk-rgb),.14),transparent 72%);box-shadow:var(--lift-2),inset 0 1px 0 rgba(var(--edge-dk-rgb),.18)} }:root[data-theme="dark"] .studio2,.ds-dark .studio2{background:linear-gradient(112deg,rgba(var(--tint-dk-rgb),.24) 0%,rgba(var(--tint-dk-rgb),.17) 30%,rgba(var(--tint-dk-rgb),.11) 60%,rgba(var(--tint-dk-rgb),.07) 100%),radial-gradient(60% 80% at 4% 0%,rgba(var(--deep-dk-rgb),.20),transparent 70%),radial-gradient(52% 66% at 100% 100%,rgba(var(--accent-dk-rgb),.14),transparent 72%);box-shadow:var(--lift-2),inset 0 1px 0 rgba(var(--edge-dk-rgb),.18)} .chat2{display:flex;flex-direction:column;padding:22px 6px 18px 22px;min-width:0;position:relative} .t-ai{display:flex;flex-direction:column;gap:5px} @media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .chat2 .cmp{background:rgba(var(--tint-dk-rgb),.17);box-shadow:inset 0 1px 0 rgba(var(--edge-dk-rgb),.18),0 2px 9px -5px rgba(var(--shadow-dk-rgb),.52)}}:root[data-theme="dark"] .chat2 .cmp,.ds-dark .chat2 .cmp{background:rgba(var(--tint-dk-rgb),.17);box-shadow:inset 0 1px 0 rgba(var(--edge-dk-rgb),.18),0 2px 9px -5px rgba(var(--shadow-dk-rgb),.52)} .seam{position:absolute;top:0;bottom:0;right:-1px;width:56px;pointer-events:none;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.22))} @media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .seam{background:linear-gradient(90deg,rgba(var(--tint-dk-rgb),0),rgba(var(--tint-dk-rgb),.11))}}:root[data-theme="dark"] .seam,.ds-dark .seam{background:linear-gradient(90deg,rgba(var(--tint-dk-rgb),0),rgba(var(--tint-dk-rgb),.11))} .canv{margin:14px 14px 14px 0;border-radius:var(--r-canvas);display:flex;flex-direction:column;min-width:0;overflow:hidden;background:var(--glass-solid);box-shadow:var(--lift-2),inset 0 1px 0 rgba(255,255,255,.95)} @media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .canv{box-shadow:var(--lift-2),inset 0 1px 0 rgba(var(--edge-dk-rgb),.18)}}:root[data-theme="dark"] .canv,.ds-dark .canv{box-shadow:var(--lift-2),inset 0 1px 0 rgba(var(--edge-dk-rgb),.18)} .canv .bar2{padding:13px 18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;box-shadow:inset 0 -1px 0 var(--hair)} .canv .bar2 .ttl2{font-size:var(--fs-body);font-weight:var(--fw-strong);letter-spacing:-.008em;margin-right:auto} .canv .gen2{display:flex;align-items:center;gap:11px;padding:10px 18px;box-shadow:inset 0 -1px 0 var(--hair);background:linear-gradient(90deg,rgba(var(--deep-rgb),.07),rgba(var(--brand-rgb),.04) 55%,rgba(var(--accent-rgb),.05))} .canv .gen2 span{font-size:var(--fs-support);color:var(--ink-2)} .canv .gen2 .dot3{width:7px;height:7px;border-radius:50%;background:var(--sp-blue);flex:none} .canv .body3{flex:1;display:grid;grid-template-columns:66px minmax(0,1fr) 50px;min-height:0} .thumbs2{padding:16px 9px;display:flex;flex-direction:column;gap:9px;align-items:center;box-shadow:inset -1px 0 0 var(--hair)} .thumbs2 .th2{width:46px;height:32px;border-radius:8px;background:var(--inner);display:grid;place-items:center;cursor:pointer;font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);color:var(--ink-3)} .thumbs2 .th2.on{background:rgba(var(--brand-rgb),.12);box-shadow:0 0 0 2px var(--sp-blue);color:var(--sp-blue)} .vrail2{padding:16px 7px;display:flex;flex-direction:column;align-items:center;box-shadow:inset 1px 0 0 var(--hair)} .vrail2 .v2{width:30px;padding:7px 0;text-align:center;font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);color:var(--ink-3);border-radius:8px;cursor:pointer} .vrail2 .v2.on{background:rgba(var(--brand-rgb),.12);color:var(--sp-blue)} .vrail2 .tk{width:1px;height:13px;background:var(--hair-2)} .paper2{padding:26px 22px;display:flex;justify-content:center;align-items:flex-start;min-width:0;overflow:hidden} @media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .sheet2{background:linear-gradient(170deg,rgba(var(--deep-dk-rgb),.14),rgba(0,0,0,0) 44%),var(--glass-solid);box-shadow:0 1px 2px rgba(var(--shadow-dk-rgb),.34),0 20px 48px -24px rgba(var(--shadow-dk-rgb),.62),inset 0 1px 0 rgba(var(--edge-dk-rgb),.16)}}:root[data-theme="dark"] .sheet2,.ds-dark .sheet2{background:linear-gradient(170deg,rgba(var(--deep-dk-rgb),.14),rgba(0,0,0,0) 44%),var(--glass-solid);box-shadow:0 1px 2px rgba(var(--shadow-dk-rgb),.34),0 20px 48px -24px rgba(var(--shadow-dk-rgb),.62),inset 0 1px 0 rgba(var(--edge-dk-rgb),.16)} .kpi2.upd{box-shadow:0 0 0 2px rgba(var(--brand-rgb),.30);background:rgba(var(--brand-rgb),.07);position:relative} .kpi2.upd::after{content:"updated";position:absolute;top:-8px;right:9px;font-family:var(--font-mono);font-size:var(--glyph-xs);font-weight:var(--fw-strong);letter-spacing:.09em;text-transform:uppercase;color:#fff;background:var(--sp-blue);padding:2px 6px;border-radius:5px} .assump{border-radius:var(--r-tile);padding:13px 15px;background:var(--inner);font-size:var(--fs-support);color:var(--ink-3);line-height:1.55} .rscale{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px} .rscale div{background:var(--inner);padding:14px;display:flex;flex-direction:column;gap:5px} .rscale .s1{border-radius:28px} .rscale .s2{border-radius:22px} .rscale .s3{border-radius:16px} .rscale .s4{border-radius:12px} .rscale .s5{border-radius:10px} .rscale b{font-size:var(--fs-body);font-weight:var(--fw-strong)} .rscale code{font-family:var(--font-mono);font-size:var(--fs-meta);color:var(--sp-blue)} .rscale span{font-size:var(--fs-support);color:var(--ink-3);line-height:1.45} @media (max-width:860px){.studio2{grid-template-columns:minmax(0,1fr);min-height:0;border-radius:var(--r-canvas)} .chat2{padding:18px} .seam{display:none} .canv{margin:0 14px 14px} .canv .body3{grid-template-columns:minmax(0,1fr)} .thumbs2{flex-direction:row;box-shadow:inset 0 -1px 0 var(--hair);overflow-x:auto} .vrail2{flex-direction:row;box-shadow:inset 0 1px 0 var(--hair);overflow-x:auto} .paper2{padding:16px 12px} .sheet2{padding:20px} } @media (max-width:620px){.sheet2 .kpis2{grid-template-columns:minmax(0,1fr)} .kpi2.upd::after{right:auto;left:12px} } @media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .convo,:root:not([data-theme="light"]) .scene,:root:not([data-theme="light"]) .canvas,:root:not([data-theme="light"]) .tabpanel,:root:not([data-theme="light"]) .kb .kc{background:var(--glass-solid);backdrop-filter:none;-webkit-backdrop-filter:none} }:root[data-theme="dark"] .convo,:root[data-theme="dark"] .scene,:root[data-theme="dark"] .canvas,:root[data-theme="dark"] .tabpanel,:root[data-theme="dark"] .kb .kc,.ds-dark .convo,.ds-dark .scene,.ds-dark .canvas,.ds-dark .tabpanel,.ds-dark .kb .kc{background:var(--glass-solid);backdrop-filter:none;-webkit-backdrop-filter:none} .themesw{display:flex;align-items:center;gap:10px;flex-wrap:wrap} .kb{display:grid;grid-template-columns:repeat(auto-fit,minmax(218px,1fr));gap:12px} .kb .col{background:var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);border-radius:var(--r);box-shadow:var(--lift-1),var(--edge);padding:12px;display:flex;flex-direction:column;gap:9px} .kb .ch{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:0 2px} .kb .ch .micro{color:var(--ink-3)} .kb .ct{font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);color:var(--ink-3);background:var(--inner);border-radius:var(--r-sm);padding:2px 7px;font-variant-numeric:tabular-nums} .kb .kc{background:var(--glass-3);border-radius:var(--r-sm);padding:11px 12px;display:flex;flex-direction:column;gap:8px;box-shadow:var(--edge),0 1px 2px rgba(var(--shadow-rgb),.05)} .kb .kc b{font-size:var(--fs-body);font-weight:var(--fw-strong);letter-spacing:-.006em;line-height:1.4} .kb .kc .kid{font-family:var(--font-mono);font-size:var(--fs-meta);color:var(--ink-3);letter-spacing:.06em} .kb .kc .kf{display:flex;align-items:center;justify-content:space-between;gap:8px} .kb .dz{border-radius:var(--r-sm);min-height:54px;background:var(--inner);outline:1.5px dashed var(--hair-2);outline-offset:-2px;display:grid;place-items:center;font-size:var(--fs-support);color:var(--ink-3)} .kb .col.wip .ct{background:var(--st-attention-t);color:var(--st-attention)} .cal{background:var(--glass-solid);border-radius:var(--r);box-shadow:var(--lift-1),var(--edge);padding:16px;display:flex;flex-direction:column;gap:12px} .cal .chd{display:flex;align-items:center;justify-content:space-between;gap:10px} .cal .chd b{font-size:var(--fs-body);font-weight:var(--fw-strong)} .cal .grid7{display:grid;grid-template-columns:repeat(7,1fr);gap:3px} .cal .dow{font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);text-align:center;padding:4px 0} .cal .d{aspect-ratio:1;border-radius:var(--r-sm);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font-size:var(--fs-support);color:var(--ink-2);font-variant-numeric:tabular-nums;cursor:pointer;transition:background var(--ease)} .cal .d:hover{background:var(--inner)} .cal .d.out{color:var(--ink-mute);cursor:default} .cal .d.out:hover{background:transparent} .cal .d.today{box-shadow:inset 0 0 0 1.5px var(--sp-blue);color:var(--ink);font-weight:var(--fw-strong)} .cal .d.sel{background:linear-gradient(180deg,var(--fill-1),var(--fill-2) 60%,var(--fill-3));color:#fff;font-weight:var(--fw-strong);box-shadow:inset 0 1px 0 rgba(255,255,255,.26)} .cal .d.sel .evd{background:#fff} .cal .evd{width:4px;height:4px;border-radius:50%;background:var(--sp-blue)} .cal .d.busy .evd{background:var(--st-attention)} .agenda{display:flex;flex-direction:column;gap:1px;border-radius:var(--r);overflow:hidden;background:var(--hair)} .agenda .ar{display:grid;grid-template-columns:76px minmax(0,1fr) auto;gap:12px;align-items:center;background:var(--glass-solid);padding:12px 14px} .agenda .at{font-family:var(--font-mono);font-size:var(--fs-meta);color:var(--ink-3);letter-spacing:.05em;font-variant-numeric:tabular-nums} .agenda .an{display:flex;flex-direction:column;gap:2px;min-width:0} .agenda .an b{font-size:var(--fs-body);font-weight:var(--fw-strong);letter-spacing:-.006em} .agenda .an span{font-size:var(--fs-support);color:var(--ink-3)} .slots{display:grid;grid-template-columns:repeat(auto-fit,minmax(92px,1fr));gap:8px} .slot{font-family:inherit;font-size:var(--fs-support);font-weight:var(--fw-medium);border:0;border-radius:var(--r-pill);padding:9px 12px;cursor:pointer;background:var(--glass-2);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);color:var(--ink-2);box-shadow:var(--edge),0 1px 2px rgba(var(--shadow-rgb),.04);font-variant-numeric:tabular-nums} .slot[aria-pressed="true"]{background:linear-gradient(180deg,var(--fill-1),var(--fill-2) 60%,var(--fill-3));color:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.26)} .slot:disabled{background:var(--inner);color:var(--ink-mute);box-shadow:none;cursor:not-allowed;text-decoration:line-through} .pc{display:flex;gap:13px;align-items:flex-start;padding:15px 16px;border-radius:var(--r);background:var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);box-shadow:var(--lift-1),var(--edge)} .pc .av{width:40px;height:40px;font-size:var(--fs-body)} .pc .pb{display:flex;flex-direction:column;gap:5px;min-width:0;flex:1} .pc .pn{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap} .pc .pn b{font-size:var(--fs-body);font-weight:var(--fw-strong);letter-spacing:-.008em} .pc .pn span{font-size:var(--fs-support);color:var(--ink-3)} .pc .pm{display:flex;flex-direction:column;gap:3px} .pc .pm div{display:flex;gap:8px;align-items:center;font-size:var(--fs-support);color:var(--ink-2)} .pc .pm .k{font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);min-width:56px} .pc .pa{display:flex;gap:7px;flex-wrap:wrap;padding-top:2px} .faces{display:inline-flex;align-items:center} .faces .av{width:26px;height:26px;font-size:var(--fs-meta);box-shadow:inset 0 1px 0 rgba(255,255,255,.22),0 0 0 2px var(--glass-solid)} .faces .av + .av{margin-left:-6px} .faces .more{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;margin-left:-6px;background:var(--inner);color:var(--ink-2);font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);box-shadow:0 0 0 2px var(--glass-solid)} .feed{display:flex;flex-direction:column} .feed .fi{display:grid;grid-template-columns:22px minmax(0,1fr);gap:0 13px;position:relative;padding-bottom:15px} .feed .fi:last-child{padding-bottom:0} .feed .fi::before{content:"";position:absolute;left:10.5px;top:22px;bottom:0;width:2px;background:var(--hair-2)} .feed .fi:last-child::before{display:none} .feed .fd{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;z-index:1;background:var(--glass-3);box-shadow:var(--edge),inset 0 0 0 1px var(--hair-2);color:var(--ink-3)} .feed .fd svg{width:11px;height:11px} .feed .fd.pos{background:var(--st-positive-t);color:var(--st-positive);box-shadow:none} .feed .fd.att{background:var(--st-attention-t);color:var(--st-attention);box-shadow:none} .feed .fd.neg{background:var(--st-negative-t);color:var(--st-negative);box-shadow:none} .feed .fb{display:flex;flex-direction:column;gap:4px;padding-top:1px;min-width:0} .feed .fh{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap} .feed .fh b{font-size:var(--fs-body);font-weight:var(--fw-strong);letter-spacing:-.006em} .feed .fh span{font-size:var(--fs-body);color:var(--ink-2)} .feed .fw{font-family:var(--font-mono);font-size:var(--fs-meta);color:var(--ink-3);letter-spacing:.05em;margin-left:auto} .feed .fp{font-size:var(--fs-support);color:var(--ink-3);line-height:1.5} .pg{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding-top:13px} .pg .rng{font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);font-variant-numeric:tabular-nums} .pg .pgs{display:flex;gap:4px;align-items:center} .pgb{font-family:inherit;font-size:var(--fs-support);font-weight:var(--fw-strong);border:0;cursor:pointer;min-width:30px;height:30px;border-radius:var(--r-sm);background:transparent;color:var(--ink-2);font-variant-numeric:tabular-nums;transition:background var(--ease),color var(--ease)} .pgb:hover:not(:disabled){background:var(--inner);color:var(--ink)} .pgb[aria-current="page"]{background:var(--glass-3);color:var(--ink);box-shadow:var(--edge),0 1px 3px rgba(var(--shadow-rgb),.10)} .pgb:disabled{color:var(--ink-mute);cursor:not-allowed} .pg .gap{color:var(--ink-mute);padding:0 2px;font-size:var(--fs-support)} .chart{border-radius:var(--r);padding:18px 20px 16px;display:flex;flex-direction:column;gap:14px;background:var(--glass-1);backdrop-filter:var(--blur-1);-webkit-backdrop-filter:var(--blur-1);box-shadow:var(--lift-1),var(--edge)} .chart .chh{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap} .chart .cht{display:flex;flex-direction:column;gap:3px} .chart .cht b{font-size:var(--fs-body);font-weight:var(--fw-strong);letter-spacing:-.008em} .chart .cht .unit{font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3)} .chart .plot{position:relative} .chart svg{display:block;width:100%;height:auto;overflow:visible} .chart .ax{font-family:var(--font-mono);font-size:var(--fs-meta);fill:var(--ink-3);letter-spacing:.04em} .chart .gl{stroke:var(--hair);stroke-width:1} .chart .nodata{border-radius:var(--r-sm);background:var(--inner);padding:26px 18px;display:flex;flex-direction:column;gap:6px;align-items:center;text-align:center} .chart .nodata b{font-size:var(--fs-body);font-weight:var(--fw-strong)} .chart .nodata span{font-size:var(--fs-support);color:var(--ink-3)} .spark{display:inline-block;vertical-align:-2px;width:74px;height:18px} .delta{font-family:var(--font-mono);font-size:var(--fs-meta);font-weight:var(--fw-strong);font-variant-numeric:tabular-nums} .delta.up{color:var(--st-positive)} .delta.dn{color:var(--st-negative)} @media (max-width:640px){.agenda .ar{grid-template-columns:64px minmax(0,1fr)} .agenda .ar >:last-child{grid-column:1/-1} }
.ds-dark{;color:var(--ink);background-color:var(--base);color-scheme:dark}
```

v3.6 additions (after it):

```css
/* ── v3.5 additions: placed AFTER the verbatim kit. Tokens only; no new colour values. ── */
:root{--line-ctl:color-mix(in srgb,var(--ink-3) 80%,transparent);--line-btn:color-mix(in srgb,var(--ink-3) 45%,transparent);--font-ui:Archivo,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;--font-mono:"IBM Plex Mono",ui-monospace,monospace;--fs-page:28px;--fs-section:18px;--fs-body:14px;--fs-support:12.5px;--fs-meta:11px;--glyph-xs:8px;--fw-regular:400;--fw-medium:500;--fw-strong:600;--sp-1:4px;--sp-2:6px;--sp-3:10px;--sp-4:12px;--sp-5:16px;--sp-6:22px;--sp-7:30px;--sp-8:44px;--rail-w:232px;--drawer-w:480px;--modal-w:520px;--tap:40px}
[hidden]{display:none!important}
/* base text on the five roles: bare headings and controls never fall back to browser defaults (low specificity, kit classes win) */
:where(h1){margin:0;font:var(--fw-strong) var(--fs-page)/1.2 var(--font-ui)} :where(h2){margin:0;font:var(--fw-strong) var(--fs-section)/1.3 var(--font-ui)}
:where(h3,h4){margin:0;font:var(--fw-strong) var(--fs-body)/1.4 var(--font-ui)} :where(small){font-size:var(--fs-support)} :where(b,strong,th,dt){font-weight:var(--fw-strong)}
:where(button,input,select,textarea,option){font:inherit;color:inherit}
/* surface treatment: glass (as shipped) or solid (each glass tier replaced by its own colour composited over the page, so every measured ratio holds) */
:root[data-surface="solid"]{--blur-1:none;--blur-2:none}
@media (prefers-color-scheme:light){:root[data-surface="solid"]:not([data-theme="dark"]){--glass-1:color-mix(in srgb,#fff 72%,var(--base));--glass-2:color-mix(in srgb,#fff 82%,var(--base));--glass-3:color-mix(in srgb,#fff 93%,var(--base));--glass-solid:color-mix(in srgb,#fff 96.5%,var(--base))}}
:root[data-surface="solid"][data-theme="light"]{--glass-1:color-mix(in srgb,#fff 72%,var(--base));--glass-2:color-mix(in srgb,#fff 82%,var(--base));--glass-3:color-mix(in srgb,#fff 93%,var(--base));--glass-solid:color-mix(in srgb,#fff 96.5%,var(--base))}
@media (prefers-color-scheme:dark){:root[data-surface="solid"]:not([data-theme="light"]){--glass-1:color-mix(in srgb,rgb(var(--tint-dk-rgb)) 12%,var(--base));--glass-2:color-mix(in srgb,rgb(var(--tint-dk-rgb)) 17%,var(--base));--glass-3:color-mix(in srgb,rgb(var(--tint-dk-rgb)) 23%,var(--base))}}
:root[data-surface="solid"][data-theme="dark"],:root[data-surface="solid"] .ds-dark{--glass-1:color-mix(in srgb,rgb(var(--tint-dk-rgb)) 12%,var(--base));--glass-2:color-mix(in srgb,rgb(var(--tint-dk-rgb)) 17%,var(--base));--glass-3:color-mix(in srgb,rgb(var(--tint-dk-rgb)) 23%,var(--base))}
:root[data-surface="solid"] .amb{display:none}
/* fill treatment: gradient (as shipped) or flat (every brand, status and avatar fill collapses to its middle stop) */
:root[data-fill="flat"]{--fill-1:var(--fill-2);--fill-3:var(--fill-2);--fill-3b:var(--fill-2);--fill-3c:var(--fill-2);--fill-deep:var(--fill-2);--fill-av:var(--fill-2);--ok-fill-1:var(--ok-fill-2);--warn-fill-1:var(--warn-fill-2);--alt-fill-1:var(--alt-fill-2)}
/* an honest ground under every gradient fill, so the audit measures the colour under the text (audit trap 1) */
.btn-p,.tog.on .track,.opt.on .box,.opt.on .dot,.sth .cir.now,.msg.me .bub,.cal .d.sel,.slot[aria-pressed="true"],.prog i{background-color:var(--fill-3)}
.sth .cir.done,.pip.done{background-color:var(--ok-fill-2)} .pip.draft{background-color:var(--warn-fill-2)} .av{background-color:var(--fill-deep)} .av.c2{background-color:var(--alt-fill-2)}
/* links inside content read as text, not as brand (the brand colour has three uses only) */
:where(a[href]){color:inherit;text-decoration-color:var(--hair-2);text-underline-offset:2px}
/* focus is visible on every interactive element, not only buttons */
:where(a[href],button,input,select,textarea,summary,[role="tab"],[tabindex]:not([tabindex="-1"])):focus-visible{outline:2px solid var(--sp-blue);outline-offset:2px}
/* a field shows where it is: its outline reaches 3:1 against the surface it sits on (WCAG 1.4.11), in both themes */
.ctl{box-shadow:inset 0 0 0 1px var(--line-ctl),0 1px 2px rgba(var(--shadow-rgb),.04)}
.ctl.err{box-shadow:inset 0 0 0 1px var(--st-negative),0 0 0 3px rgba(var(--neg-rgb),.16)} .ctl.warn{box-shadow:inset 0 0 0 1px var(--st-attention),0 0 0 3px rgba(var(--warn-rgb),.15)}
.ctl:focus-within,.ctl.focus{box-shadow:inset 0 0 0 1px var(--sp-blue),0 0 0 3px rgba(var(--brand-rgb),.18)}
/* a button is a box whether it is a <button> or a link: an inline link with padding spills over the line above it */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:var(--sp-2);text-decoration:none;line-height:1.3}
/* a select draws its own chevron in the text colour, with room on the right, so the arrow never sits on the edge */
:is(select.ctl,.ctl select){appearance:none;-webkit-appearance:none;cursor:pointer;padding-right:calc(var(--sp-6) + 14px);background-image:linear-gradient(45deg,transparent 50%,currentColor 50%),linear-gradient(135deg,currentColor 50%,transparent 50%);background-position:calc(100% - 22px) 52%,calc(100% - 17px) 52%;background-size:5px 5px,5px 5px;background-repeat:no-repeat}
/* a button that follows a block of text keeps a gap from it (rows and headers space themselves) */
:is([data-ds-device],.ds-stage) :where(p,ul,ol,dl,h2,h3,h4,table) + :where(.btn):not(:is(.wf-inline,.wf-row,.row,.wf-header,.toolbar,.pane-foot) > .btn){margin-top:var(--sp-3)}
/* a secondary button has a visible edge on every surface, so it never reads as loose text */
.btn-s{box-shadow:inset 0 0 0 1px var(--line-btn),var(--lift-1)}
/* label style switch: eyebrow (as shipped: mono, uppercase) or sentence (the label as written, in the UI face) */
:root[data-labels="sentence"] :is(.fld>label,legend,.lbl){font-family:var(--font-ui);font-size:var(--fs-support);font-weight:var(--fw-strong);letter-spacing:0;text-transform:none;color:var(--ink-2)}
/* text kept for screen readers when a control is drawn as an icon (the name stays the wireframe's word) */
.sr{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.ctl :focus-visible{outline:none}
.ctl select{background-color:transparent;cursor:pointer}
.btn[aria-busy="true"]{cursor:progress} .btn[aria-busy="true"]::before{content:"";display:inline-block;width:11px;height:11px;margin-right:8px;vertical-align:-1px;border-radius:50%;border:2px solid currentColor;border-right-color:transparent}
.btn-i{display:inline-grid;place-items:center;min-width:var(--tap);min-height:var(--tap);padding:0;border:0;border-radius:var(--r-pill);background:transparent;color:var(--ink-2);cursor:pointer;transition:background var(--ease)} .btn-i:hover{background:var(--inner);color:var(--ink)} .btn-i svg{width:18px;height:18px}
/* numbers in a table column line up on the right, in tabular figures */
.tbl :is(th,td).num{text-align:right;font-variant-numeric:tabular-nums}
/* a data-bound bar shows the value it was drawn from */
.prog>i[style*="--v"]{width:var(--v)}
/* the metric tile's top sheen is a light-theme highlight; in dark it lifts the ground under the tile's text below 4.5:1 */
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tile:not(.flag){background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,0)),var(--glass-1)}}
:root[data-theme="dark"] .tile:not(.flag),.ds-dark .tile:not(.flag){background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,0)),var(--glass-1)}
/* gradients by role. Two colours only, always from the brand: light = a very light tint of the brand's primary fading to
   white (radial, from the top-left corner); dark = the brand deepened into the dark surface (linear, top to bottom or
   diagonal). They go on the app canvas and navigation (data-canvas="glow") and on the signature component (.wash),
   the same on every instance. Catalogue stages and the design-system page stay plain. data-canvas="plain" turns the
   canvas and navigation gradients off. */
:root[data-canvas="glow"] [data-ds-device]{background:radial-gradient(120% 90% at 0% 0%,color-mix(in srgb,rgb(var(--brand-rgb)) 9%,#fff),#fff 70%);background-color:#fff}
:root[data-canvas="glow"] .app-top{background:linear-gradient(90deg,color-mix(in srgb,rgb(var(--brand-rgb)) 7%,#fff),#fff 60%);background-color:#fff}
.wash{background:radial-gradient(130% 120% at 0% 0%,color-mix(in srgb,rgb(var(--brand-rgb)) 10%,#fff),#fff 65%);background-color:#fff}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"])[data-canvas="glow"] [data-ds-device]{background:linear-gradient(180deg,color-mix(in srgb,rgb(var(--brand-rgb)) 16%,var(--base)),var(--base) 60%);background-color:var(--base)}
  :root:not([data-theme="light"])[data-canvas="glow"] .app-top{background:linear-gradient(90deg,color-mix(in srgb,rgb(var(--brand-rgb)) 20%,var(--glass-solid)),var(--glass-solid) 70%);background-color:var(--glass-solid)}
  :root:not([data-theme="light"]) .wash{background:linear-gradient(140deg,color-mix(in srgb,rgb(var(--brand-rgb)) 24%,var(--glass-solid)),var(--glass-solid) 65%);background-color:var(--glass-solid)}}
:root[data-theme="dark"][data-canvas="glow"] [data-ds-device],:root[data-canvas="glow"] .ds-dark [data-ds-device]{background:linear-gradient(180deg,color-mix(in srgb,rgb(var(--brand-rgb)) 16%,var(--base)),var(--base) 60%);background-color:var(--base)}
:root[data-theme="dark"][data-canvas="glow"] .app-top,:root[data-canvas="glow"] .ds-dark .app-top{background:linear-gradient(90deg,color-mix(in srgb,rgb(var(--brand-rgb)) 20%,var(--glass-solid)),var(--glass-solid) 70%);background-color:var(--glass-solid)}
:root[data-theme="dark"] .wash,.ds-dark .wash{background:linear-gradient(140deg,color-mix(in srgb,rgb(var(--brand-rgb)) 24%,var(--glass-solid)),var(--glass-solid) 65%);background-color:var(--glass-solid)}
/* app shell */
.app{display:grid;grid-template-columns:auto minmax(0,1fr);min-height:100%;position:relative;z-index:1}
.app.top{grid-template-columns:minmax(0,1fr);grid-template-rows:auto 1fr}
.app-rail{position:sticky;top:0;align-self:start;min-height:100vh;width:var(--rail-w);display:flex;flex-direction:column;gap:var(--sp-1);padding:var(--sp-5) var(--sp-4);background:linear-gradient(180deg,var(--fill-deep),var(--fill-3));background-color:var(--fill-3);color:#fff}
.app-rail a{display:flex;align-items:center;gap:var(--sp-3);min-height:var(--tap);padding:0 var(--sp-4);border-radius:var(--r);color:#fff;opacity:.86;text-decoration:none;font-size:var(--fs-body);font-weight:var(--fw-medium);transition:background var(--ease)}
.app-rail a:hover{background:rgba(255,255,255,.10);opacity:1} .app-rail a[aria-current="page"]{background:rgba(255,255,255,.18);opacity:1;font-weight:var(--fw-strong)}
.app-rail a:focus-visible{outline-color:#fff}
.app-top{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:var(--sp-4);min-height:56px;padding:var(--sp-3) var(--sp-6);background:var(--glass-solid);box-shadow:inset 0 -1px 0 var(--hair)}
.app-top a{display:inline-flex;align-items:center;min-height:var(--tap);padding:0 var(--sp-3);border-radius:var(--r-sm);color:var(--ink-2);text-decoration:none;font-size:var(--fs-body)}
.app-top a:hover{background:var(--inner);color:var(--ink)} .app-top a[aria-current="page"]{color:var(--ink);font-weight:var(--fw-strong);background:var(--inner)}
.app-main{display:flex;flex-direction:column;min-width:0} .app-body{padding:var(--sp-6);display:flex;flex-direction:column;gap:var(--sp-5);min-width:0}
/* overlays (container doctrine: drawer for record-attached work, modal only for irreversible acts) */
.scrim{position:fixed;inset:0;z-index:40;background:rgba(var(--shadow-rgb),.32)}
.drawer{position:fixed;top:0;right:0;bottom:0;z-index:41;width:min(var(--drawer-w),100%);display:flex;flex-direction:column;background:var(--glass-solid);border-radius:var(--r) 0 0 var(--r);box-shadow:var(--lift-2),var(--edge);overflow:auto}
.drawer>header,.modal>header{display:flex;align-items:center;justify-content:space-between;gap:var(--sp-4)}
.drawer>header{padding:var(--sp-5) var(--sp-6);box-shadow:inset 0 -1px 0 var(--hair)} .drawer>.body{flex:1;padding:var(--sp-5) var(--sp-6);display:flex;flex-direction:column;gap:var(--sp-4)}
.drawer>footer{display:flex;justify-content:flex-end;gap:var(--sp-3);padding:var(--sp-4) var(--sp-6);box-shadow:inset 0 1px 0 var(--hair)}
/* overlay anatomy regions: put them on the wireframe's own header and footer, or on data-ds-wrap wrappers around its body */
:is(.drawer,.modal)>.pane{display:flex;flex-direction:column;flex:1;min-height:0}
:is(.drawer,.modal) .pane-head{display:flex;align-items:flex-start;justify-content:space-between;gap:var(--sp-4);padding:var(--sp-5) var(--sp-6) var(--sp-4);box-shadow:inset 0 -1px 0 var(--hair)}
:is(.drawer,.modal) .pane-head :is(h2,h3){font-size:var(--fs-section);line-height:1.3} :is(.drawer,.modal) .pane-head :is(small,p){color:var(--ink-2);font-size:var(--fs-support)}
:is(.drawer,.modal) .pane-head .btn-i{flex:none;margin:calc(var(--sp-2) * -1) calc(var(--sp-3) * -1) 0 0}
:is(.drawer,.modal) .pane-body{flex:1;min-height:0;overflow:auto;padding:var(--sp-5) var(--sp-6);display:flex;flex-direction:column;gap:var(--sp-5)}
:is(.drawer,.modal) .pane-foot{position:sticky;bottom:0;display:flex;align-items:center;justify-content:flex-end;flex-wrap:wrap;gap:var(--sp-3);padding:var(--sp-4) var(--sp-6);background:var(--glass-solid);box-shadow:inset 0 1px 0 var(--hair)}
.modal:has(.pane-head){padding:0;gap:0}
.modal{position:fixed;left:50%;top:50%;z-index:42;transform:translate(-50%,-50%);width:min(var(--modal-w),calc(100% - 32px));max-height:calc(100% - 64px);overflow:auto;display:flex;flex-direction:column;gap:var(--sp-4);padding:var(--sp-6);background:var(--glass-solid);border-radius:var(--r);box-shadow:var(--lift-2),var(--edge)}
.toast.fixed{position:fixed;left:50%;bottom:var(--sp-6);transform:translateX(-50%);z-index:43}
/* documents: an invoice, report or order drawn as the document, on paper, in the brand's type */
.doc{display:flex;flex-direction:column;gap:var(--sp-4);max-width:var(--doc-w,680px);padding:var(--sp-6) var(--sp-7);background:var(--glass-solid);border-radius:var(--r-sm);box-shadow:var(--lift-1),var(--edge);font-size:var(--fs-support);color:var(--ink)}
.doc header{display:flex;justify-content:space-between;align-items:flex-start;gap:var(--sp-5)} .doc h3{margin:0;font-size:var(--fs-section);font-weight:var(--fw-strong)}
.doc dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:2px var(--sp-3)} .doc dt{color:var(--ink-3)} .doc dd{margin:0}
.doc .doc-parties{display:grid;grid-template-columns:1fr 1fr;gap:var(--sp-5)}
.doc table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums} .doc th{text-align:left;font:var(--fw-strong) var(--fs-meta)/1.4 var(--font-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);padding:var(--sp-2) var(--sp-3);box-shadow:inset 0 -1px 0 var(--hair-2)} .doc td{padding:var(--sp-2) var(--sp-3);box-shadow:inset 0 -1px 0 var(--hair)}
.doc .num{text-align:right} .doc .doc-totals{align-self:flex-end;min-width:260px;display:flex;flex-direction:column;gap:var(--sp-1)} .doc .doc-totals div{display:flex;justify-content:space-between;gap:var(--sp-6)} .doc .doc-totals .grand{font-weight:var(--fw-strong);padding-top:var(--sp-2);box-shadow:inset 0 1px 0 var(--ink)}
.doc .doc-stamp{align-self:flex-start;padding:2px var(--sp-3);border-radius:var(--r-sm);box-shadow:inset 0 0 0 1.5px currentColor;font:var(--fw-strong) var(--fs-meta)/1.6 var(--font-mono);letter-spacing:.06em;text-transform:uppercase}
.doc .doc-faint{color:var(--ink-3)}
/* feedback */
.banner{display:flex;gap:var(--sp-3);align-items:flex-start;padding:var(--sp-4) var(--sp-5);border-radius:var(--r);background:var(--st-neutral-t);color:var(--ink);font-size:var(--fs-body)}
.banner.attention{background:var(--st-attention-t)} .banner.negative{background:var(--st-negative-t)} .banner.positive{background:var(--st-positive-t)}
.banner .lead{font-weight:var(--fw-strong);color:var(--ink)}
.skel{display:block;height:12px;border-radius:var(--r-sm);background:var(--inner)}
/* the layout bridge: a styled copy of a wireframe screen keeps the wireframe's structure (layout only, from tokens) */
[data-ds-device]{width:var(--w,1280px);min-height:var(--h,800px);margin-inline:auto;position:relative;transform:translateZ(0);overflow:hidden;container-type:inline-size;background:var(--base)}
:is([data-ds-device],.ds-stage) .wf-app{display:grid;grid-template-columns:auto minmax(0,1fr);min-height:inherit} :is([data-ds-device],.ds-stage) .wf-app.wf-top-shell{grid-template-columns:minmax(0,1fr);grid-template-rows:auto 1fr}
:is([data-ds-device],.ds-stage) .wf-main{display:flex;flex-direction:column;gap:var(--sp-5);min-width:0} :is([data-ds-device],.ds-stage) .wf-row{display:flex;gap:var(--sp-5);flex-wrap:wrap} :is([data-ds-device],.ds-stage) .wf-row>*{flex:1 1 260px;min-width:0}
:is([data-ds-device],.ds-stage) .wf-stack{display:flex;flex-direction:column;gap:var(--sp-3)} :is([data-ds-device],.ds-stage) .wf-inline{display:flex;gap:var(--sp-2);align-items:center;flex-wrap:wrap}
:is([data-ds-device],.ds-stage) .wf-split{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:var(--sp-5)} :is([data-ds-device],.ds-stage) .wf-header{display:flex;justify-content:space-between;align-items:flex-start;gap:var(--sp-4);flex-wrap:wrap}
:is([data-ds-device],.ds-stage) .wf-img{aspect-ratio:var(--ratio,4/3);display:flex;align-items:flex-end;padding:var(--sp-3);border-radius:var(--r-sm);background:var(--inner);font-size:var(--fs-support);color:var(--ink-2)}
@container (max-width:700px){:is([data-ds-device],.ds-stage) .wf-split,:is([data-ds-device],.ds-stage) .wf-app{grid-template-columns:minmax(0,1fr)}}
.ds-stage{container-type:inline-size}
/* a frame that holds a whole styled screen: fixed overlays stay inside it */
.ds-frame{position:relative;width:fit-content;max-width:100%;overflow:hidden;border-radius:var(--r);box-shadow:var(--lift-2);background:var(--base)}
@media (max-width:760px){.app{grid-template-columns:minmax(0,1fr)} .app-rail{position:static;min-height:0;width:auto;flex-direction:row;overflow-x:auto} .drawer{border-radius:0} .app-body{padding:var(--sp-5)}}
/* ── document only: the design-system page itself. Never used in the app ── */
.ds-doc{display:grid;grid-template-columns:232px minmax(0,1fr);gap:var(--sp-7);max-width:1480px;margin:0 auto;padding:var(--sp-6);position:relative;z-index:1}
.ds-nav{position:sticky;top:var(--sp-5);align-self:start;max-height:calc(100vh - 32px);overflow:auto;display:flex;flex-direction:column;gap:2px;font-size:var(--fs-support)}
.ds-nav a{display:block;padding:5px 10px;border-radius:var(--r-sm);color:var(--ink-2);text-decoration:none} .ds-nav a:hover{background:var(--inner);color:var(--ink)} .ds-nav .sub{padding-left:var(--sp-6)}
.ds-main{display:flex;flex-direction:column;gap:var(--sp-8);min-width:0}
.ds-sec{display:flex;flex-direction:column;gap:var(--sp-5);scroll-margin-top:var(--sp-5)} .ds-sec>h2{margin:0;font-size:var(--fs-page);font-weight:var(--fw-strong);line-height:1.2}
.ds-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:var(--sp-4)} .ds-facts>div{display:flex;flex-direction:column;gap:var(--sp-1);padding:var(--sp-4) var(--sp-5);border-radius:var(--r);background:var(--glass-solid);box-shadow:var(--lift-1),var(--edge)}
.ds-cat{display:flex;flex-direction:column;gap:var(--sp-5);padding:var(--sp-6);border-radius:var(--r);background:var(--glass-solid);box-shadow:var(--lift-1),var(--edge);scroll-margin-top:var(--sp-5)}
.ds-cat>header{display:flex;justify-content:space-between;align-items:baseline;gap:var(--sp-4);flex-wrap:wrap}
.ds-src{font-size:var(--fs-support);color:var(--ink-2)} .ds-src a{color:inherit}
.ds-stage{position:relative;width:100%;max-width:var(--spec-w,100%);padding:var(--sp-6);border-radius:var(--r);background:var(--base);box-shadow:inset 0 0 0 1px var(--hair);overflow-x:auto}
/* overlay stages: the overlay at its content height over a strip of dimmed page, never a page-sized empty box */
.ov{position:relative;transform:translateZ(0);overflow:hidden;height:var(--stage-h,auto)} .ov .scrim,.ov .wf-scrim{position:absolute}
.ov::before{content:"";position:absolute;inset:0;background:rgba(var(--shadow-rgb),.16)}
.ov.drawer-s{max-width:calc(var(--spec-w,var(--drawer-w)) + 150px);min-height:240px;padding:var(--sp-7) var(--sp-7) var(--sp-7) 120px;display:flex;justify-content:flex-end}
.ov.drawer-s .drawer{position:relative;inset:auto;z-index:1;width:var(--spec-w,var(--drawer-w));max-width:100%;max-height:var(--stage-max,960px);border-radius:var(--r)}
.ov.modal-s{max-width:calc(var(--spec-w,var(--modal-w)) + 120px);min-height:220px;padding:var(--sp-7);display:grid;place-items:center}
.ov.modal-s .modal{position:relative;left:auto;top:auto;transform:none;z-index:1;width:var(--spec-w,var(--modal-w));max-width:100%;max-height:none}
.ov.menu-s{--stage-h:240px;max-width:440px} .ov.toast-s{--stage-h:132px;max-width:640px} .ov.menu-s::before,.ov.toast-s::before{background:none}
.ov.menu-s::after{content:"";position:absolute;top:var(--sp-4);right:var(--sp-5);width:var(--tap);height:var(--tap);border-radius:var(--r-pill);background:var(--inner)}
.ov.menu-s [data-component-type="menu"]{position:absolute;top:calc(var(--tap) + var(--sp-5));right:var(--sp-5);width:auto;min-width:220px;max-width:320px}
.ds-states{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:var(--sp-5)} .ds-states.wide{grid-template-columns:minmax(0,1fr)}
.ds-parts{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:var(--sp-4) var(--sp-6);font-size:var(--fs-support)} .ds-parts h4{margin:0 0 var(--sp-1);font-size:var(--fs-support);font-weight:var(--fw-strong)}
.ds-scale{display:flex;align-items:flex-end;gap:var(--sp-6);flex-wrap:wrap} .ds-scale>div{display:flex;flex-direction:column;align-items:center;gap:var(--sp-2);font-size:var(--fs-support)} .ds-scale i{display:block;width:var(--v);height:var(--v);min-width:2px;background:var(--fill-2);border-radius:2px}
.ds-icons{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:var(--sp-4)} .ds-icons>div{display:grid;grid-template-columns:32px minmax(0,1fr);gap:2px var(--sp-3);align-items:center;padding:var(--sp-4);border-radius:var(--r);background:var(--glass-solid);box-shadow:var(--lift-1),var(--edge);font-size:var(--fs-support)} .ds-icons svg{grid-row:span 3;width:24px;height:24px}
.ds-compare{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:var(--sp-5);align-items:start} .ds-compare>div{border-radius:var(--r);padding:var(--sp-5);min-width:0;overflow:hidden}
@media (max-width:1100px){.ds-doc{grid-template-columns:minmax(0,1fr)} .ds-nav{position:static;flex-direction:row;flex-wrap:wrap;max-height:none} .ds-compare{grid-template-columns:minmax(0,1fr)}}
```

**Fonts as shipped:** Archivo 400/500/600 and IBM Plex Mono 400/500/600, both openly licensed Google Fonts, embedded
or linked in the page. Archivo is the default body face and Step 4 decides whether the client's replaces it. IBM
Plex Mono stays. If the mono is not actually loaded, table headers fall back silently and the whole grid loses its
register.

---

## Step 1 · Read the wireframe and the BRD

**The wireframe is the source of truth for structure and the component inventory. The BRD is the source of truth for
the client, the brand cues, the people and the conditions of use.**

1. Take the inventory (`T` as in "Finding the inputs"):
   ```bash
   source ~/.local/poc-collateral/env.sh 2>/dev/null
   python3 -I "$T" inventory "<workspace>/02b-wireframes/<slug>-wireframes.html" "<workspace>/03-design-system/_working/inventory.json"
   ```
   It lists every screen, frame, component (with its instances, variants and states), atom, the signature, the
   agent's one entry, the open questions and the requirements the wireframe could not place. It writes the component
   index (Step 11), the target widths, and the starting `#ds-manifest`, `#build-plan` and `#style-sets` blocks.
   **Automate what is deterministic, compose by eye.** The tools take inventories, IDs, tokens, manifests, audits and
   screenshots. They do not lay out a catalogue entry, size a specimen, set the hierarchy of a screen or choose the
   brand expression. You do that by hand, and you look at each result.
2. **Open the wireframe in a browser and click through it.** Look at every screen and frame, open the state picker
   in the review bar, and note how each component is used: its content density, its actions, what it sits next to.
3. **Read from the BRD only what this stage needs:** client, industry and website (§0–2); research findings and
   brand cues with their sources (§6); personas with their devices and conditions (§7), which set the target width:
   when the BRD says desktop only, design and check at its desktop width, test 1,024 px for robustness only, and say
   that smaller screens are unsupported. Draw no phone layout the BRD did not ask for; AI trust and labelling
   rules (§17); non-functional notes such as language, accessibility and devices (§18); the hand-off to the design
   system, with the hero object and reference products (§21); the glossary. Brand cues in the BRD are evidence with
   source types, not a chosen palette. Write what you take from the BRD once into `03-design-system/_working/notes.md`
   (messages and copy word for word) and work from the notes; reopen the BRD only for one missing fact.
4. **Decide nothing about structure.** Every component the inventory lists will be catalogued. No component outside
   it will be. Variants are the wireframe's variants, and states are the wireframe's states plus the interaction
   states each control needs (Step 9). When something the BRD needs is missing from the wireframe, or a component's
   anatomy cannot work as drawn, add an entry to **Wireframe gaps** (the gap, the BRD ref, the wireframe change it
   needs) and style the screen as drawn. Finishing a component's anatomy is not a structural decision; Step 9 says
   exactly what may change.

## Step 2 · Sample the brand

**Brand source order** (highest first): material the person or the caller supplied → the client's official brand
guidelines or design system → the client's live product → the client's website → the BRD's §6 cues. Research
through the `research` skill when it is installed; if it fails, use web search and fetch. Record each source. Read
`<workspace>/research/` once first, if it exists: a question it already answers is not asked again, and its brand
facts are leads you confirm on the live site. Fetch the client's page and its linked stylesheet once, and use them for
Steps 2, 3 and 4 together.

* **Read the CSS custom properties off `:root` on the live site**, not a screenshot and not the brand book. *On
  daikincomfort.com they are literally `--daikin_blue`, `--daikin_orange`, `--daikinGradient`.* Take the neutral ramp
  too. The type stack is its own step (Step 4).
* **A brand book's print primaries are not necessarily the hue the client means by "our colour".** Proofpoint's second
  attempt used H 196, the hue of their own 5415 Blue, and was still wrong. The answer came as a swatch: *"Its more of
  sea green and bluish…"*, sampled as `#102F2D` off their live site. **When a swatch is available, sample it. Do not
  reason toward it.**
* **Note the brand's chromatic role:** one hero colour, a pair, a gradient, or achromatic (black, white, grey) with a
  single accent. An achromatic brand's "brand colour" is its black, and its accent is a signal, never rotated into a
  hue it does not have.
* **Note the brand's surface habits:** does its own product use flat colour or gradients, translucent or solid
  panels, light or dark grounds? Step 5 uses this.
* **Voice:** from the website and the BRD's own copy, write two lines on how the product speaks (plain or formal,
  first or second person). This guides the catalogue's usage notes. It never rewrites wireframe copy.

## Step 3 · Harvest the logo

**Acquisition, in order. Stop at the first that yields a real file.** Fetch routes 1–4 together in one batch (the order
still picks the winner); go on to the later routes only when none of those is a real file.

1. **Inline `<svg>` in the site header**, or a linked `.svg` (`/logo.svg`, `/assets/logo*.svg`), always preferred; it
   scales and recolours cleanly.
2. `<link rel="apple-touch-icon">`, usually 180px, square, the mark alone.
3. `<meta property="og:image">`, usually the lockup, often with padding to crop.
4. `/favicon.svg` or `/favicon.ico`.
5. **The rendered page.** If a direct fetch is blocked, empty or built by JavaScript, open the site in the connected
   browser (Claude in Chrome or the built-in browser) and take the logo from the rendered page: the header `<svg>`
   markup, or the `src` of the header `<img>`, then fetch that URL (routes 7 and 8).
6. **The brand or media page, and the client's other official sources.** Many organisations publish their logo files
   on a brand site or press kit (`/brand`, `/media`, `/press`, `/newsroom`), often as SVG. When the client uses a
   parent's identity (a lab of a university, a subsidiary), look on the parent's brand site too. Also try the logo on
   the client's own docs or support site, and the client's app-store icon.
7. **The file's own address, downloaded directly.** Once any route has given you the logo's URL, download that file
   itself with the shell, separately from its page. A site that blocks the page may serve the file.
8. **Through the browser**, when downloads are blocked: in the connected browser (Claude in Chrome or the built-in
   browser), open the logo file's own URL, not the page, and read it with a page script (`fetch` the same address,
   convert to base64) to save the real bytes. If the page or file opens blank, try the other browser. This is
   retrieval of the real file, not drawing.
9. **Public logo libraries.** Wikimedia Commons and similar archives hold many organisations' official logos as SVG;
   use one only when its page names the organisation's own file as the source. Brandfetch and Simple Icons also hold
   official files. Use the file as published, record its page as the provenance, and check it matches the mark on
   the client's live site.
10. **Ask** (stop 2). Never trace, redraw or approximate.

**Work through every route before stop 2.** One blocked fetch is not a reason to stop: "could not be downloaded into
this workspace" after one try is not a result. Record each route tried with its result, so a reviewer can see the
search was complete.

**When no real file is obtained,** the deliverable is not brand-complete, and it says so. The overview at the top of
the page carries `data-brand-status="incomplete"` and a banner naming what is missing, why, and every source tried.
The placeholder (the client's name in the chosen type, marked `data-logo-status="placeholder"`, or the caller's
named stand-in marked `"stand-in"`) appears only where the wireframe marks `data-logo`. A placeholder is never
presented as the logo.

**The brand section always has its logo section,** whether or not the file was obtained:
`<div data-logo-kit>` in `#brand`, with one `<figure data-logo-variant="primary|horizontal|stacked|mark|reversed|one-colour|app">`
per variant from the table below, each drawn on its own ground at its minimum size, with its use, clear space and
misuse rules. With the real file, each slot shows that variant. Without it, each slot shows the placeholder wordmark
on the same ground and size, marked `data-logo-status="placeholder"` and labelled as a placeholder, and the section
names the official file's address if one was found, every route tried, and what is needed to finish: the file. Every
use of each variant on the page draws from one source (one data URI per variant), so adding the real file later is
one replacement per variant. `fidelity` fails a page without the seven slots.

**Then derive the kit. Seven variants, because a navbar and a favicon are not the same problem:**

| Variant | Where it goes | Min size | Ground |
| --- | --- | --- | --- |
| **Primary lockup** | Login, splash, cover slide, document header | 140px wide | Light page only |
| **Horizontal lockup** | Product header, email signature | 110px wide | Light page or tier-1 surface |
| **Stacked lockup** | Narrow columns, print, square crops | 96px wide | Light page only |
| **Mark only** | Collapsed rail, tab strip, compact header | 24px | Any |
| **Reversed mono** | The nav rail, when the rail carries the brand fill | 24px | Brand fill |
| **One-colour** | Watermark, single-ink print | 24px | Any |
| **App / favicon** | Tab, bookmark, PWA | 16 · 32 · 180 · 512 | Its own |

**Rules, and they are measured like anything else:**

* **Clear space is half the mark's height on all four sides.** Nothing crosses it, including the product name.
* **The mark is measured at ≥ 3:1 against its ground.** It is a graphical object, not text: 3:1 is the bar, and it
  must hold in every variant and both themes.
* **Account and org logos are circles.** Crop to a circle; never letterbox a rectangle inside one.
* **A rail on the brand fill takes the reversed mono logo**, never the colour version on a white plate or a glow. A
  knocked-out mark on the brand fill is the single most common place a prototype stops looking like the client owns
  it. With a light rail, use the colour lockup that measures on it.
* **Never** recolour the mark outside the approved mono and reversed versions, place the full-colour logo on the
  brand fill, stretch, rotate, outline or shadow it, or redraw it.
* **Record provenance**: which URL each file came from. Mark anything unverified `[UNVERIFIED]`.
* The logo goes only where the wireframe marks `data-logo`.

## Step 4 · Type: research the real face, then decide what you may legally ship

**Two separate questions, and conflating them is the mistake.** *What typeface does the client actually use?* is
research. *May we put that file in our prototype?* is licensing, and the answer is usually no.

### Identify it, in this order

At most two look-ups to identify the face: the stylesheet (or the rendered page) for routes 1–4 below, then one
`research` request for the rest.

**Fetch the linked stylesheet, not the page.** A page fetch returns converted text with no `@font-face` in it. That
was tried on a live client site and came back with no font information while the site plainly loads webfonts. Read
the CSS file the page links to, or use the browser.

1. **`<link>` to `fonts.googleapis.com/css2?family=…`** names the family outright, and tells you it is openly
   licensed. Best case; you are done.
2. **`@font-face` in the stylesheet**: `font-family` plus a `src: url(….woff2)`. The filename usually carries the
   family name.
3. **The loader domain names the foundry:** `use.typekit.net` / `p.typekit.net` → **Adobe Fonts** ·
   `fast.fonts.net` / Monotype paths → **Monotype** · `cloud.typography.com` → **Hoefler&Co**.
4. **Computed `font-family` on `body` and on a heading** catches the case where the brand face is only used for
   display and the body is a system stack.
5. **Their brand or press page**, which often names the typeface in words.
6. **Ask** in an attended run; unattended, ship the closest open substitute and mark the face `[DERIVED]` in the type
   note. Do not guess from a screenshot; a wrong guess propagates into every screen.

**Record what you found even when you cannot use it.** The type note names the real face as what production should
license. That sentence is worth having in front of the client.

### The licensing rule: identify the real face, ship an open one

**A webfont licence does not travel to us.** This is not caution, it is what the licences say:

* **Adobe Fonts cannot be self-hosted at all** and cannot be used by a third party: *"Adobe doesn't offer the ability
  to host fonts locally"*, and a client's site *"must load Adobe Fonts through their own Creative Cloud
  subscription"*. An agency cannot carry them into its own build.
* **Monotype webfonts are single-domain and metered.** A licence covers *"a single domain"*, runs on *"prepaid
  pageviews"*, and **agencies "may not share a single webfont license across multiple websites"**.
* **Google Fonts are open** (SIL OFL / Apache 2.0): self-hosting, commercial use and redistribution are all permitted.
  This is why they are the fallback.

**So the rule: never download and redistribute a client's licensed webfont into our prototype.**

| What you found | What to ship |
| --- | --- |
| A Google Font | **Use it.** Link it or self-host it |
| Any other open face (OFL/Apache on GitHub or a foundry's free tier) | **Use it**, after checking the licence text itself |
| A licensed face: Adobe, Monotype, Hoefler, a bespoke foundry cut | **The closest open substitute**, with the real face named in the type note |
| A display or script face used only in the logo | **Do not use it for UI at all.** It is a logo face; the body face is a separate question |
| Nothing identifiable | **Keep the system's own faces** and say so |

### Choosing the substitute: match the metrics, not the vibe

Two faces that look similar at 48px can wreck a 13px table. **Match, in this order: x-height ratio · advance width ·
classification (grotesque / neo-grotesque / geometric / humanist) · stroke contrast · terminal style · whether it has
tabular numerals**, which the system needs on every number.

Starting points, **each to be verified by overlaying the two at the same size, never accepted from this table
alone**:

| Client's face | Open starting point |
| --- | --- |
| Helvetica / Helvetica Neue / Neue Haas Grotesk / Arial | **Inter** |
| Graphik, Founders Grotesk, Aktiv Grotesk | **Inter** or **Archivo** |
| Proxima Nova, Brandon, Sofia Pro | **Archivo** or **Figtree** |
| Gotham, Montserrat-adjacent geometrics | **Montserrat** |
| Avenir, Museo Sans, Nunito-adjacent humanists | **Nunito Sans** |
| Futura, Avant Garde | **Jost** |
| Circular, Poppins-adjacent geometrics | **Poppins** |
| DIN, Eurostile | **Barlow** or **Archivo Narrow** |
| Frutiger, Myriad, Univers | **Source Sans 3** |
| Tiempos, Georgia, a transitional serif | **Source Serif 4** |
| Garamond, an old-style serif | **EB Garamond** |

When the brand has no identifiable face, keeping Archivo is a decision with a reason, recorded in the type note. A
generic default chosen by habit makes every app look alike.

**Scripts other than Latin.** When the BRD needs Arabic, Hebrew or another script, choose an open face that covers
it and pairs with the Latin face (Noto Sans Arabic, IBM Plex Sans Arabic, Noto Sans Hebrew), and check the
right-to-left frame the wireframe drew.

### A font swap invalidates the audit: re-measure

Changing the body face changes x-height and advance width, so it moves **apparent size, line length, vertical rhythm
and every fixed-width layout**. After the swap:

* **Re-run the contrast audit in both themes.** Contrast itself does not move, but perceived weight does: a lighter
  face at `--ink-3` can read thinner than the measured ratio suggests.
* **Re-measure fixed-width layouts.** A wider face is exactly what pushes a six-station rail back out of its
  container.
* **Check the numerals are tabular**, or every number in the system loses its alignment.
* **Check the type roles still hold their hierarchy.** A large x-height face makes 13px and 15px look like the same
  size.

**Keep IBM Plex Mono regardless.** The mono is structural, not brand: it carries table headers, eyebrows, KPI
labels, timestamps and citation chips, and its 10.5px table header is a measured value. Clients almost never have a
brand mono, and swapping it changes the grid's register for no gain. **Swap the body face; keep the mono.**

## Step 5 · Set the visual direction, render it, then apply it

The direction is decided before the catalogue, from evidence, and looked at before it spreads to 30 components.
**A flat, pale, border-heavy look is a failure mode, not a safe default.** It is what the HEINEKEN run produced: a
light rail, solid white cards on a near-white page, and a brand that showed only on buttons. Equally, gradients,
glows, glass and shadows are tools, never defaults. Dense tables and data-heavy regions stay calm and readable.

**Decide each of these, with a one-line reason from the brand or the BRD** (they go on the expression card):

| Decision | Options | Decide by |
| --- | --- | --- |
| **Navigation** | brand-fill rail (a restrained tonal transition from the brand's deep to mid tone) · light rail with the brand on the active item · near-black chrome with the brand as signal | how strong the brand colour is and how much it carries the company's identity; the wireframe's shell |
| **Background** (`data-canvas`) | `glow`: the app canvas and the top bar carry the brand's gradient · `plain`: flat | `glow` by default; `plain` when the brand's own product is flat and quiet |
| **Gradients by role** | Two colours only, both from the brand, never a third. Light: a very light tint of the brand's primary fading to white, radial from the top-left corner. Dark: the brand deepened into the dark surface, linear from the top (canvas, top bar) or diagonal (signature). They go on the app canvas, the top bar and `.wash` on the signature component (at most one more component kind, and only one of real significance to the storyline). Catalogue stages and the design-system page stay plain. Never by position | every instance of a chosen kind carries the wash and no other kind does: a gradient that marks only the third of three cards is the inconsistency this rule exists to prevent |
| **Surface hierarchy** | app background → navigation → content surfaces → nested `.inner` → drawers and modals, each visibly distinct | always; the audit measures it |
| **Surface** (`data-surface`) | `glass` · `solid` (each tier composited over the page, every ratio unchanged) | `solid` for dense tools and phones in poor light; `glass` where the brand itself uses depth |
| **Fill** (`data-fill`) | `gradient` · `flat` | the brand's own product |
| **Colour** | primary, secondary, neutral ramp, semantic status | Steps 2, 6 and 7 |
| **Type** | the face from Step 4 on the five roles | Step 4 |
| **Density** | comfortable · compact (`.pad-s`, supporting text in tables) | the personas: many rows at a desk takes compact |
| **Themes** | default light or dark, both designed (Step 8) | the personas' conditions |
| **Labels** (`data-labels`) | `eyebrow` (mono, uppercase, as shipped) · `sentence` (the label as written, in the UI face at the supporting size) | `sentence` for forms and record facts people read in full; `eyebrow` where labels are short codes. Table headers, identifiers and timestamps keep the mono face either way |
| **Icons** | one open family (Lucide by default), stroke 1.6 | only when the wireframe has `data-icon` |
| **Pictures** | HTML/CSS mockups on the wireframe's photo areas | the wireframe's `.wf-img` captions |

**Render it before you apply it.** Style the shell and the main working screen (key screen 2) in two candidate
directions that differ in navigation and surface treatment. Screenshot both in light and dark and look at them side
by side. Choose one, write why in one line, and record the one you rejected. The test: cover the logo. Would someone
who knows the client recognise the product as theirs, and can a person still scan the densest table on the screen? If
the answer to either is no, revise before any catalogue entry is written. For a strong brand colour, a brand-fill rail
with a restrained tonal transition is usually right; it is not right for every client, so make the case each time.

## Step 6 · Transform, preserving luminance

**The whole value of porting a validated system is that its measurements survive. They survive only if you hold the
right quantity fixed, and it is not the one in the colour picker.**

Contrast is a function of relative luminance alone. **HSL lightness is not luminance**: green at L .40 is far brighter
than blue at L .40. Measured on the Proofpoint port, holding HSL-L fixed while rotating 207° → 176° took the primary
from **4.54:1 to 3.12:1**, silently, on a token the document prints a number for.

```python
import colorsys
def _lin(c): c/=255; return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def Y(rgb): r,g,b=rgb; return .2126*_lin(r)+.7152*_lin(g)+.0722*_lin(b)
def hsl_rgb(h,s,l): return tuple(round(v*255) for v in colorsys.hls_to_rgb(h,l,s))

def reskin(rgb, hue, sat):
    """Saturation is CHOSEN (that is the muting). Lightness is SEARCHED. hue/sat/l in 0..1."""
    target, lo, hi = Y(rgb), 0.0, 1.0
    for _ in range(60):
        mid = (lo+hi)/2
        if Y(hsl_rgb(hue, sat, mid)) < target: lo = mid
        else: hi = mid
    return hsl_rgb(hue, sat, (lo+hi)/2)
```

**Do not add a "drop saturation if Y is unreachable" fallback.** In HLS, lightness 1.0 is white at every saturation,
so every `Y` in [0,1] is always reachable. That branch can only fire spuriously, on a tolerance tighter than
integer-RGB rounding, and when it fires it flattens a colour to grey while keeping its hue. `#86CDB4` came back
`#BFBFBF`. **Saturation is chosen; lightness is searched.**

**Transform the `:root` blocks only:** the light block, the dark blocks (in the media query and under
`[data-theme="dark"]`), and the bare triples. Rules carry no colour of their own any more. Then grep the rules for any
hex or `rgb(` other than white and black, which must find nothing.

**Assign colour by job and keep the jobs separate:** brand/chrome · status · categorical · sequential.

* **The brand colour has exactly three uses**: the one primary action, the active nav item and the selected state.
  Not headings, icons, counts or links in tables. Everything else is greyscale.
* **Reserve the warm end for risk states** so a categorical colour never reads as an alarm. If the brand itself is
  warm, Step 7 inverts this.
* **Muting is a saturation cut, never a lightness cut**: a lightness cut moves the quantity you are holding. Worked
  example: blues → H176 at S × 0.70 (cap .62); the cerise family → H152 at S × 0.62 (cap .44) for the gradient tail;
  positive → H138 against a green brand; amber → H28; red → H6; anything under S .06 left alone.
* **Four statuses, tonal only**: 8–10% tint, text at the 700 step, never a saturated fill. **Status always ships as
  icon or word plus colour**, never colour alone.
* **Charts: one hue at several lightness steps.** Fixed hue order, never cycled.
* **Brand-as-accent and brand-as-fill are two different values.** White on the Proofpoint fill measured 4.15 against
  a claimed 4.94, because the fill gradient runs one step darker than the accent token. The fill tokens
  (`--fill-1` … `--fill-3c`, `--fill-deep`) govern the primary button, user chat bubble, toggles, checked boxes, the
  current stepper node, selected calendar day and slot, and the progress bar. **Check every stop, not just the middle
  one.** In dark, brand-as-text lightens while brand-as-fill does not.

## Step 7 · The warm-brand checks (skip if the brand is cool)

Three things appear on a red or orange brand and on no cool one:

* **Negative status collides with the brand and no contrast figure will warn you.** A red brand and a red error
  measure 1.54 contrast, but contrast is a lightness metric and says nothing about categorical separation. **Measure
  ΔE.** At H 350 negative sits 26 ΔE from the brand against 90 ΔE in the blue original; **H 344 recovers 32 ΔE** and
  is about the ceiling before the error reads as a brand tint. Icon or word plus colour becomes load-bearing.
* **The chart ramp must leave the brand hue entirely.** A six-step red ramp reads as six alarm levels. Send it cool:
  still one hue at several lightness steps, and it can never read as risk.
* **The accent needs more headroom.** A straight port put Titan's accent at 4.48 on the page, a fail where the blue
  measured 4.54.

## Step 8 · Both themes, both measured

**Light and dark are both measured and both kept live in the token block**, so the second theme is one attribute
away rather than a rebuild. Whether the app itself offers people a theme switch is the BRD's decision, and the
wireframe shows it if it does. When it does, every screen must re-theme, with no screen stuck light or dark. When it
does not, the app ships the default theme from Step 5.

* **v3.3 shipped both themes and no `<script>`**, so it silently followed the reader's OS and the reviewer only ever
  saw dark: *"do we not have light mode."* **The design-system page ships a theme switch** (document chrome, `assets/ds-runtime.js`
  A) so both themes are reachable. A theme toggle in product chrome that the BRD did not ask for is our scaffolding
  shipped to the client.
* **A theme built by inversion fails on contact.** Light-mode brand hexes in a dark ambient field paint shadow instead
  of light; that is what blotched the first SailPoint dark mode.

**Dark is designed, not inverted.** Set its hierarchy on purpose: app background darkest, then navigation, then
content surfaces, then nested surfaces, with drawers and modals the lightest, because raised surfaces catch more light
in dark. Separators are faint hairlines and are rarely needed. Text has three levels (`--ink`, `--ink-2`, `--ink-3`).
Status colours step up in lightness so they read on the dark surfaces without glowing. A passing contrast audit does
not prove the dark theme is comfortable or coherent: look at a dense table, a form, an open drawer and the status
treatments in dark before you accept it. The audit measures the surface ladder; your eye judges the balance.

**Dark specifics:** ambient washes go *lighter* than the page · edges catch light upward in dark and downward in light
· one hue carries two categorical steps in dark, three in light · **a container that holds other glass takes the
opaque rung**, or nested glass composites two rungs above its intended one and drags every ink token after it.

**Light specifics, which are not dark with the tokens flipped:** near-white brand tint base · **aurora alphas roughly
halved** · tier 1 `rgba(255,255,255,.72)`, tier 2 `.82`, tier 3 `.93` · inset highlight `rgba(255,255,255,.9)` ·
shadows to the brand's darkest tone at 8–12% · **the accent glow drops, replaced by a soft focus ring**.
**A tinted light background changes the surface a chart was validated against.** Daikin's palette passes on `#F4F8FC`
and a third slot drops below 3:1 by `#EEF4FA`. Cap the tint and re-run the audit. **Re-measure fixed-width layouts
after restyling**: larger radii and padding are what push a six-station rail back out of its container.

## Step 9 · Style the wireframe

This is the step the rest of the file serves. Three parts: the component catalogue, the atoms, and three styled
screens. **The rule for all three: copy the wireframe's markup, add classes, finish each component's anatomy, and
change no content or behaviour.**

**What you may change** in copied wireframe markup:
- `class` values: add kit classes (`btn btn-p`, `tblwrap`, `drawer`, `pad`, `stack`) beside the wireframe's own,
  including the anatomy regions `.pane-head`, `.pane-body` and `.pane-foot` on the wireframe's own `header` and `footer`;
- **region wrappers:** a `<div data-ds-wrap="header|body|footer|group|label">` (or `header`, `footer`, `section`)
  around consecutive elements of one component, to give it the regions its kind needs (the table below). A wrapper
  holds no text of its own and no `data-*` metadata, and it never reorders anything;
- **icon presentation:** a control the wireframe marks `data-icon` (Close, More) may be drawn as an icon button
  (`.btn-i`) with its word kept in `<span data-ds-wrap="sr" class="sr">Close</span>`, so its accessible name stays
  the wireframe's word;
- **a data-bound visual:** `<div class="prog" data-ds-viz data-ds-from="6 of 7" aria-hidden="true"><i
  style="--v:85.7%"></i></div>` beside a number the component already shows (a share, a count against a total it
  states, a position in a band it states), drawn from that number and nothing else. `fidelity` checks the value against
  the text. No trend line unless the component shows the series, no comparison it does not state, no invented target;
- `data-state`: set to the state the wireframe frame gives that instance;
- `style`: only `--w`, `--h`, `--ratio`, and layout properties that use tokens (`gap:var(--sp-5)`, grid columns);
- inside an element marked `data-icon`: one icon `<svg data-ds-decor aria-hidden="true">`;
- inside an element marked `data-logo`: the logo image, with the wireframe's text as its `alt`;
- on a picture area (`.wf-img`): a CSS picture mockup behind its caption and `data-media` on the element.

**What you never change:** any wireframe element, its order, or its nesting beyond the wrappers above; any text; any
`data-*` attribute other than `data-state` as above and adding `data-media`; `href`, `disabled`, `aria-*`, `role`. So
no added label, badge, icon (outside `data-icon`), metadata line, description, action, nested card, extra field or
extra section. If a wireframe card has a heading and two lines, the styled card has that heading and those two lines,
finished. What these rules cannot reach goes under **Wireframe gaps**: a missing part, an action in a place wrapping
cannot fix, a layout that does not work.

**Record every correction.** List each component whose anatomy you corrected, or that carries a data-bound visual, in
the QA report's `#corrections` list (`<li data-component="exception-detail">`: what changed, why, and that its content
and behaviour are unchanged), and say it in one sentence of its anatomy part. A correction applies everywhere the
component appears, in its catalogue entry and on the styled screens alike. `fidelity` fails a correction that is not
listed.

### Finish each component

**The wireframe draws what a component holds. The catalogue draws it finished.** A stat card in the wireframe is a
title, a number and a line of text. Styled, it keeps exactly those, with a clear hierarchy, considered padding, its
surface and elevation, and a supporting visual when its own numbers support one. Judge every component against the
conventions for its kind and correct what the wireframe left incomplete, within the rules above. These are
conventions, never templates: the use case decides the final form, and a floating header or footer, an overlay
drawer or a compact rail is right when the composition calls for it.

| Kind | Finished anatomy | Typical correction |
| --- | --- | --- |
| Drawer | header: title, its context line, close as an icon button at the top end · body: scrolls, holds the content · footer: pinned to the bottom, holding the actions · a clear edge from the page (raised elevation over a scrim) | actions at the end of the body wrapped as the footer · a Close word under the title drawn as an icon button · one undivided column wrapped into header, body and footer |
| Modal | header with its title (and close when it may be dismissed) · body · footer with its actions · scrim | as for the drawer |
| Navigation | brand area (logo, app name) · items in groups, icons and labels aligned · the active item clearly marked · account and utility controls at the end | items of mixed weight, size or alignment |
| Page | the app shell · a page header (title, its one-line purpose, its primary action) · the main region · supporting regions | a title and its action floating without a header region |
| Card | a header line · content with one focal point · its action · even padding · resting elevation on the canvas | a flat card that blends into the page |
| Metric | its label at the supporting size · the number at the page size in 600 with tabular figures · the comparison or time frame it states · a `.prog` bar when it is a share or a count against a total it states | the number at body size; the comparison without its direction |
| Table | header row in the mono role · numbers right-aligned in tabular figures · rows separated by a hairline · hover and selected tones · status as tag and word · the density from Step 5 | wide gaps between short columns; status as bare text |
| Form | labels above fields (`data-labels`) · fields with a 3:1 edge · help and error text under the field · actions together at the end | label and field out of line; actions scattered |
| Buttons | primary filled · secondary with a visible edge · tertiary as text with a hover tone · one primary per region | a secondary that reads as loose text |
| Record header | identity (name first, ID after and smaller) · status tag · key facts in a grid, labels and values aligned | facts strung on one line |

**Surface separation.** Every container separates from what is behind it: the canvas (`--base`), then content
surfaces with resting elevation, nested `.inner` regions inside them, then drawers, modals and menus raised over a
scrim. Every edge of a container must show: where it starts and where it ends is visible on all four sides, in both
themes. A container in its parent's colour with no elevation and no edge reads as a coloured wireframe fragment, and
`audit` fails it, as it fails a specimen that touches the edge of its stage. Use the surface treatment the direction chose, gradients only where the direction put them, and
shadows only on the two levels. Add nothing to make a specimen look fuller.

**When a correction would change function, stop.** Moving an action where it would mean something else, adding a
control, or merging two steps changes the product. Leave it as drawn and record it under Wireframe gaps with the
correction you propose.

### 9a · The component catalogue

**Every entry is a usable reference on its own.** A reader finds the component from the index, sees it finished and
branded at its real size, learns its parts and states, knows which wireframe screen and instances it comes from, and
could rebuild it. The low-fidelity wireframe component is not drawn again: the entry traces it through its metadata
and one link. Write the entries one by one in the order screens first use them, and look at each group of five as you
go (Step 10). One entry per wireframe component, and nothing else:

```html
<section class="ds-cat" data-catalogue data-component="exception-panel" id="cmp-exception-panel"
         data-component-type="card" data-source-screens="PG-02" data-source-instances="PG-02.exception-panel"
         data-variants="" data-states="default resolved">
  <header><div><p class="micro">card · 1 instance · PG-02 Invoice record</p><h3 class="title">Exception panel</h3></div><code>exception-panel</code></header>
  <p class="ds-src">From <a href="../02b-wireframes/<slug>-wireframes.html#PG-02">PG-02 Invoice record</a> · PG-02.exception-panel · opened from a queue row</p>
  <div class="ds-stage" style="--spec-w:360px" data-persona="U1">
    the instance, copied and finished: kit classes, regions, data-specimen-of="PG-02.exception-panel" data-active="true"
  </div>
  <div data-part="states"> … </div>
  <div class="ds-parts"> anatomy · tokens · behaviour · a11y · responsive </div>
</section>
```

- **Traceability without a copy.** `data-component-type`, `data-source-screens`, `data-source-instances`,
  `data-variants` and `data-states` list exactly what the wireframe has (`inventory.json` gives them; `fidelity`
  compares them). The one source line names the screen with its link, the instance IDs and what opens the component.
  Add no other caption, tag or explanation.
- **The specimen is the real component at its real size, finished.** Copy the instance's markup and content; add kit
  classes and complete its anatomy (Step 9). Set `--spec-w` on the stage to the width the instance has in the
  wireframe at the target width (a side panel 360, a table the content width), so nothing is stretched across a giant
  canvas and nothing is squeezed. Set `data-persona` on the stage to the source screen's persona, so parts only
  another persona sees (`data-for`) stay hidden; styled screens carry it on their `<section>`. A specimen with no kit
  class renders unstyled and fails the check. The stage is the app canvas, so the component's own surface and
  elevation show against it.
- **Overlays sit in an overlay stage at their content height:** `.ds-stage.ov` plus `.drawer-s` (the drawer at its
  own width over dimmed page), `.modal-s`, `.menu-s` (the menu anchored under a trigger at the top right)
  or `.toast-s`. Copy the overlay with `data-state` set to its open state and without `hidden`. The stage takes the
  overlay's height, so a drawer never shows a tall empty panel, and leaves dimmed page on every side, so the
  overlay's edge and shadow show all round. `audit` fails a tall empty panel and any card, metric, record header,
  document or overlay that runs to the edge of its stage, where it would merge with the entry around it.
- **Name the parts in words, never with numbers on the specimen.** The specimen shows the component as it will be
  built, with nothing drawn over it. The anatomy part names each part that exists (title, supporting content,
  primary action, secondary action, close control; columns, header, status treatment for a table) with its kit class
  and tokens. Numbered markers read as content to a builder, so `fidelity` fails `data-ds-part`.
- **States and variants:** render each variant the wireframe uses. Render a state only when it looks or behaves
  differently: a different message, structure or treatment. A state that only changes which record is shown is the
  same visual state; list it in the states part with the states that look the same, and do not draw it again. Wide
  components use `.ds-states.wide` (one per row) so nothing is cut; small ones use the grid. Interaction states
  (`.is-hover`, `.is-focus`, `.is-pressed`, `disabled`, `aria-busy`, `aria-invalid`, `aria-selected`) are drawn on
  the component's own control, once, and must be visibly different from each other.
- **The parts are specific to this component** in its context: the anatomy (its parts named), component and instance
  IDs, source screens, variants, states, type and colour tokens, dimensions and spacing, surface treatment, what each
  interaction does, its accessibility (role, name, keyboard, focus, contrast as measured) and its responsive or
  desktop-only behaviour. Notes copied across entries fail the check. Say nothing a reader could not use.
- **A table** shows its real columns, headers, four to six representative rows and its status treatments. **A form**
  shows its fields, labels, actions and its validation state. **A toast** shows its message, status treatment and how
  it is dismissed. **A document** looks like the document (the `.doc` component), not a grey box.
- Fill no empty space with decoration or invented content. If an entry looks empty, the specimen is wrong.
- Where the doctrine in REFERENCE expects a part the wireframe lacks (a table without its toolbar), style what exists
  and add the part to **Wireframe gaps**.

### 9b · The atoms

One `<section class="ds-cat" data-catalogue data-catalogue-atom="<atom>" id="atom-<atom>">` per atom kind the
wireframe uses (`data-atom`: button, input, select, toggle, checkbox, radio, tag, avatar), in a `.ds-stage`. Show each
variant the wireframe uses in each interaction state that applies, plus busy for buttons and the icon button if
`data-icon` appears. Tags stay smaller than the smallest button and are never pressable.

### 9c · Three styled screens

Draw exactly three, the wireframe's `key_screens`, each a copy of that screen or frame at high fidelity:

1. **`home`:** the primary persona's start screen, with the signature.
2. **`main`:** the main working screen, where the primary persona does the job the BRD's demo storyline centres on.
3. **`agent`:** the main working screen with the agent drawer open. If the BRD has no agent, the wireframe names the
   frame that opens that screen's main drawer or modal instead; say so in the QA report.

The wireframe chose them, so do not choose others. If one looks wrong for the job, record it under Wireframe gaps.
Each is `<section data-screen="1|2|3" data-ds-screen="<screen-id>" [data-ds-frame="<frame-id>"]>` holding a
`.ds-frame` with the copied `.wf-device` contents marked `data-ds-device`. A screen keeps its wireframe width (`--w`)
and the runtime scales it to fit, here and in the light and dark comparison; never narrow a screen to fit, because a
narrowed screen reflows and cuts its top bar. Paste the wireframe's `wf-app` style block
(layout only) into the stylesheet. The layout bridge in the additions gives the wireframe's layout classes their
structure in styled screens and specimens, and keeps every overlay inside its device. A frame with `persona` shows
that persona's view: keep its `data-for` elements as they are. The screens carry the same anatomy corrections as the
catalogue entries. Screens 2 and 3 copy the same screen, so their
instance IDs repeat; the runtime resolves every interaction inside its own screen.

### 9d · The manifest and the build blocks

From `inventory.json`, fill and include:
- `<script type="application/json" id="ds-manifest">`: per component, its instances, screens, variants, states and
  the tokens it uses; per atom the same; the screens and frames; and the token list with each token's measured ratio.
  It must match what the page renders (Step 10 checks it).
- `<script type="application/json" id="build-plan">`: the app settings (`shell`, `agent_entry`, `theme`, `surface`,
  `fill`, `canvas`, `density`, and `wash`: the component kinds that carry it), the `concept` (the signature), and every page with its pattern, its regions (top-level
  components in order) and its wireframe screen.
- `<script type="application/json" id="style-sets">`: one active set, `S1`, naming each component's variant(s) as the
  wireframe uses them.
Do not claim that UnifyApps Headless compiles or imports any token format. It reads this HTML and these blocks.

## Step 10 · The visual acceptance gate

Automated checks are necessary and not enough. **A technically passing page that looks unfinished or confuses its
reader is a failed page.** Run this full pass once, at the end, in both themes; after a later fix, re-check and look
only at the sections that changed. On any failed command or fetch, read the error, fix the cause and retry once; then
take another route or record the gap (`check:` lines still get fixed). Run the checks, look at everything, pass the polish gate, then have it looked at by fresh
eyes.

**Walk every text role with alpha composited over its real parent chain, in light and in dark.** The reference run on
v3.4 covered 35 roles and ended with 3 under AA in each theme, all three deliberately dimmed states (exempt as
disabled).

Run both checks and fix every `error:` line:

```bash
source ~/.local/poc-collateral/env.sh 2>/dev/null; python3 -I "$T" embed "<workspace>/03-design-system/<slug>-design-system.html"
python3 -I "$T" fidelity "<workspace>/02b-wireframes/<slug>-wireframes.html" "<workspace>/03-design-system/<slug>-design-system.html"
python3 -I "$T" audit "<workspace>/03-design-system/<slug>-design-system.html" "<workspace>/03-design-system/_working/qa"
```

`fidelity` (no browser) proves the styling changed nothing the wireframe owns: three styled screens with the same
instances in the same order, the same element tree and the same text; the frame's states; a catalogue entry for
every wireframe component and atom and for nothing else; specimens copied from real instances, active, and with the
instance's element tree apart from region wrappers and data-bound visuals; wrappers with no text or metadata; every
visual drawn from a number its component shows; every corrected component listed in `#corrections`; each entry's
traceability attributes matching the wireframe, and no low-fidelity copy in the catalogue; and
`#ds-manifest`, `#build-plan`, `#style-sets` and the agent entry consistent with the wireframe and the stylesheet. It
also checks the page: the twelve sections in order with a link to each in the navigation, the overview's brand status
(incomplete whenever a logo is a placeholder), an index row for every component, an `id="cmp-…"` on every entry, every
specimen inside a stage and using kit classes, and notes not copied across entries.

`audit` (Playwright, or an installed Chrome) renders the page in light and dark at 1,440 px, with each styled screen
and specimen at its own wireframe width, plus a 1,024 px robustness pass whose findings are checks only. It checks:
contrast of every text element against every colour it may sit on (each gradient stop, composited down to an opaque
ground; 4.5:1, or 3:1 for large text; disabled controls exempt); blank specimens (a stage mostly empty); clipped or
overflowing specimens and anything cut inside them; any part escaping its catalogue entry; the surface hierarchy
(app, navigation, content and overlay lightness, including overlays lighter than content in dark); component anatomy
(a drawer or modal with no header holding its title, a close control outside the header, a primary action outside
the footer, a tall empty panel below the content); cards, metrics, record headers, documents and overlays that blend
into the surface behind them or run to the edge of their stage; fields whose edge is under 3:1 and secondary buttons with no visible edge; content cut at an edge that hides
overflow (a styled screen wider than its frame, the light and dark comparison included, or a control past the edge of
its top bar or card); a button touching or overlapping the text or control beside it; a select whose arrow sits on its
edge; sideways scroll;
script errors; names, visible focus and targets; fonts not loaded; and rendered consistency (below). It saves a
screenshot of every catalogue entry and styled screen in both themes, the whole page, labelled contact sheets, and
`consistency.json`.

**Look at every screenshot yourself: every catalogue entry and every styled screen, in both themes.** Go through the
labelled contact sheets, then open each entry and screen at full resolution. A zero-error `audit` does not mean the
page is visually successful. For each component, answer:

1. Does it look complete and professionally designed, a finished product element?
2. Are its anatomy and internal layout right for its kind (Step 9, Finish each component)?
3. Are its header, body and footer clearly distinguished where it has them?
4. Does it separate from the surface behind it?
5. Are its type and spacing consistent with every other component?
6. Do its variants and states look meaningfully different from each other?
7. Does it keep the wireframe's content and functional meaning?
8. Can you trace it to its wireframe screen and instances from the entry alone?
9. Could a frontend engineer build it from this entry?
10. Does the whole document read as one coherent design system?

Hold it to the standard of a well-made component library: consistent specimen sizes, clear component boundaries,
deliberate surfaces and states you can tell apart at a glance. Then the page as a whole: the overview answers what
this is and whether it is complete, the index finds any component in seconds, and the brand reads as the client's.
Reject and fix anything that fails. Never write that all components were reviewed when only some were: the QA report
lists what you looked at.

**The visual consistency and polish gate.** Before the design system is complete, review the rendered output as one
product. Judge what renders, not what is declared: a defined token does not prove it is used, and a consistent
stylesheet does not prove a consistent interface. `audit` measures the computed styles of every styled screen and
specimen and fails on font sizes off the five roles, faces other than the two font tokens, weights other than 400,
500 and 600, colours that are no token, and one component rendered with different type, padding, radius, surface or
elevation in different places. It reports radii off the scale, gaps off the spacing scale, bordered cards, mixed icon
sizes or strokes, and large gradient surfaces. Then look, area by area, across the contact sheets and the three
screens:

| Area | Look for |
| --- | --- |
| Completeness | every component finished for its kind: anatomy, one focal point, surface and elevation, states (Step 9) |
| Spacing | padding, margins and gaps on the scale; no button touching the text above or beside it; a select's arrow inside its padding; the same rhythm between the same kinds of things; edges aligned; no awkward or excessive blank space |
| Typography | one face per role, the five sizes, weights used for hierarchy only, line heights even, the hierarchy readable at a glance |
| Colour | the palette's relationships hold; brand colour only on its three uses; status colours only for status, always with a word |
| Gradients and brand | only the canvas, the top bar and the signature carry a gradient: two brand colours, light tint to white in light, brand into the dark surface in dark; every instance of a kind looks the same; nothing else carries one; the product reads as the client's |
| Themes | light and dark have the same hierarchy and weight; neither looks unfinished |
| Surfaces | app background, navigation, content, nested and overlay surfaces distinct; no border where tone or elevation already separates; shadows only on the two levels |
| Proportions | components sized for their content and use; nothing stretched, squeezed, clipped or floating |
| Icons | one family, one stroke, two sizes, placed the same way beside their labels |
| Hierarchy and density | the most important thing reads first on every screen; dense regions calm and scannable |
| Reuse | the same component looks and behaves the same on every screen and in its catalogue entry |

Correct what you find in the stylesheet or the classes you added, never in the wireframe's content or structure:
awkward spacing, unnecessary borders, arbitrary font variations, weak colour choices, excess blank space, clipping,
misalignment and inconsistent treatments. Re-run `audit` and look again. Approve only when the page reads as one
coherent, professionally designed product rather than a set of separately generated parts. Record each area's
result, and what you changed, in the QA report.

**Fresh-eyes review, one round.** Start a separate agent when the session can, and give it only the screenshots and
contact sheets: no notes, no source, no audit output. While it works, end the turn and wait for Claude Code's finished
notice, with no status checks; if `$CLAUDE_PROJECT_DIR/.poc-studio/autopilot` exists, create `.poc-studio/waiting`
beside it and remove it when the reply arrives. It must be able to say what the application is, navigate the
document, find three components named from the wireframe, explain one component's anatomy and behaviour, compare its
light and dark appearance, and judge whether it could rebuild it. Record its findings and what you changed in the QA
report. If no independent review could run, say so in the QA report and leave it marked outstanding; never write a
review that did not happen.

**Mechanical checks the scripts do not cover, all pass/fail:**

* `grep -o 'stroke[A-Z]'` finds nothing. 79 camelCase SVG attributes once shipped in our own design language with
  every icon at browser-default stroke. **JSX takes camelCase; plain HTML takes kebab-case: same defect, opposite
  fix, both silent.**
* Every bare-triple token transformed (the list in Step 0).
* No hex or `rgb(` in any rule outside `:root`, other than white and black.
* With `glass`: card `border-width` computes 0, gradient cards carry no inset ring, `backdrop-filter` computes
  `blur(...) saturate(...)`, a 1px top edge on every glass surface. With `solid`: `backdrop-filter` computes `none`
  and the ambient field is off.
* Radii only {10, 6, pill, circle} outside the studio.
* Table headers use `--font-mono` at `--fs-meta` and the face is actually loaded; no `font-size` or `font-family`
  literal in any rule you wrote.
* If the body face was swapped (Step 4): numerals are tabular, the type roles hold their hierarchy, and no fixed-width
  layout overflows.
* Tag font size < button font size · status tags ≥ 4.5 composited in both themes · **logo mark ≥ 3:1 on its ground,
  every variant**.
* One `<style>`, one `</style>` · the theme switch is correct under both OS schemes and across a reload.
* On a styled screen with a filter, narrow it until it returns nothing and check that the filtered-empty state
  appears, not the empty state.

**Four traps, each of which produced a false result on a real run:**

1. **Gradient grounds read as transparent.** A walker reading `backgroundColor` finds nothing on a `linear-gradient`
   surface and falls through to the page. It reported **1.03:1** on rail text that measures **12.12:1**. The additions
   put a real `background-color` under every gradient fill, and `audit` measures every stop. Keep both.
2. **Alpha ignored.** Composite the tint over its actual parent or every tonal status tag reports about 1.2 and you
   "fix" what was never broken. **Measuring the wrong thing is its own failure mode.**
3. **Inject CSS before the LAST `</style>`, not the first.** The first may be a host page's own skeleton: the rules
   land outside the stylesheet, are stripped on export, and every component renders with browser defaults while the
   file looks complete. **This is written down and it still happened while building v3.4.** Verify a *computed
   value* on a new component, not the source text or the presence of the element.
4. **A handler audit false-clears if `[data-theme]` is on `<html>`**: `el.closest('[data-theme]')` then matches every
   element. Exclude `document.documentElement`. Same trap in Playwright: `page.click('[data-theme]')` clicks `<html>`
   and your dark screenshot comes back light. Select `button[data-theme-set]`.

A fifth, found while building the additions: **a theme-scoped override can lose to a later unscoped one.** The `solid` surface
first overrode the dark opaque rung with the light one. That gave 1.2:1 text in dark, which only the composited audit
caught. Every override of a themed token is scoped to its theme.

## Step 11 · Ship

**One self-contained HTML file**, `<workspace>/03-design-system/<slug>-design-system.html` (or the name and folder the
caller gives), built on the skeleton in Appendix A: a sticky navigation (`.ds-nav`) with a link to every section, and
these twelve sections in this order.

1. **Overview** (`#overview`): the application, the BRD and wireframe used (also as `data-source-brd` and
   `data-source-wireframe` on `<html>`), the brand status (`data-brand-status="complete"` or `"incomplete"`, with a
   banner naming anything unresolved), the number of components documented, and the sections available. A reader
   knows what this is and whether it is finished without scrolling.
2. **Component index** (`#index`): from `inventory.json`, one row per wireframe component: name, component ID, type,
   source screens (ID and name), instance IDs, variants and states counted, and a link to `#cmp-<id>`.
3. **Brand identity and visual direction** (`#brand`): the swatch with its provenance and the brand source order
   applied; the expression card (`#expression`: navigation · background · gradients by role · surface · fill · shell · density · default
   theme · concept, each with its reason, and the direction you rejected); the logo kit (seven variants, usage, clear
   space, minimum sizes, misuse, provenance, or the unresolved status); the type note; the two-line voice.
4. **Design foundations** (`#foundations`): the surface hierarchy from app background to overlay, radii, the two
   elevations and motion, each rendered.
5. **Colour and semantic tokens** (`#color`): the transformed `:root` blocks as swatches, every token named by job,
   **a measured ratio printed beside each**, non-text ones marked. A token carrying a number nobody re-measured after a
   hue rotation is a defect.
6. **Typography** (`#type`): the five roles rendered with token, size, weight and line height, and the mono face.
7. **Spacing, layout and surfaces** (`#space`): the spacing scale in one horizontal row (`.ds-scale`: token name,
   value and a proportional sample), the shell, content widths and the target width (desktop only when the BRD says
   so, with smaller screens stated as unsupported).
8. **Icon system** (`#icons`): a grid (`.ds-icons`) with each icon's preview, name, intended use and size, in one family
   and stroke; icons present in the wireframe first, any optional ones marked optional. If the wireframe uses no icon,
   say so in one line.
9. **Component catalogue** (`#components`): Step 9a, then the atoms (Step 9b).
10. **Screen-level compositions** (`#screens`): the three styled screens (Step 9c).
11. **Light and dark comparison** (`#themes`): key screen 2 and the densest component side by side, the page's theme
    on the left and a `.ds-dark` copy on the right (`.ds-compare`). Read it with the page in light.
12. **Traceability and QA report** (`#qa`): the audit results by theme, the surface lightness measured, the polish gate
    result for each area, what you looked at and what you changed, the anatomy corrections (`#corrections`), the fresh-eyes findings or "outstanding", **Wireframe gaps**, the port note (source
    version, max |ΔY| across all colours, every decision the port forced), and the three hand-over answers.

After section 12, keep the **Composition contract** (`#contract`, Appendix D, filled in), which the build prompt quotes
verbatim. Plus the three JSON blocks (Step 9d), the theme switch in the navigation (`data-doc-chrome`), and the
runtime (Appendix B).

**The type note:** the client's real typeface named, what was shipped instead and why. *"Brand face is Gotham
(Monotype, single-domain licence); shipped Montserrat as the closest open substitute. Production should license
Gotham."* **A client reading that learns something; a silent substitution looks like we did not notice.**

**Anchor the one branded surface to the client.** With the brand-fill rail, its fill starts at the sampled swatch;
with a light rail, the brand marks the active item and the primary action.

**Swap the sample domain, not the doctrine.** Proofpoint: Deal Gate → Quote Builder; gate artefacts → product
configuration / pricing summary / legal review / order form; identities → seats; Stage 20/40 → awaiting approval /
approved. **Every measurement stayed.**

**Anonymise at extraction: the format travels, the client name does not.** Check the share setting before handing over
a link. **If you fix something in the stylesheet, say so in the hand-over**: an unreported fix means the next run
reintroduces it and the skins quietly diverge. **No demo or synthetic labels anywhere** on the page or in specimens.

---

# REFERENCE

## Form: the parts people get wrong

* **No borders on cards.** Separation is elevation and tone, never a line. Hairlines *inside* a card (row separators,
  a divider between two regions) are fine; the rule is about the card's outline.
* **A card carrying colour gets exactly one treatment**: gradient wash alone, **or** solid tint plus one inset
  hairline. Never both. A gradient already says "selected"; a ring on top of it is the most common violation, and it
  shows up most on selected options inside a chat input. A solid tint without a ring reads as a flat slab, which is
  why the inverse holds.
* **Corner radius is a fixed scale. Never improvise a value.** **10px** everywhere: cards, tiles, containers, inputs,
  selects, panes, drawers, modals, table containers · **6px** for small inner elements: tags, chips, code · **pill**
  for buttons, toolbar search, facets and accent pills · **circle** for avatars and account logos · **studio only**
  shell 28 / canvas 22 / sheet 16 / tile 12, because a 10px corner on an 1,100px object reads as a cut rather than a
  form. **Never 8/12/14/16 outside that scale, and never a mix on one page**: mixed radii are the single most common
  reason a build reads as unfinished. A blanket flatten to 10px was tried and reverted within the hour. **Do not
  re-propose it.**
* **With glass: ambient aurora in the brand theme, never flat grey.** Layered low-opacity radial blooms distributed
  down the page. Percentage-sized radials on the body; avoid `background-attachment: fixed`, which bands in full-page
  captures. Dense tool: 3–4% at most, two or three blooms, page body only, never behind a table or a side pane, which
  take a solid ground so rows stay legible. With solid: no ambient field; the canvas glow (`data-canvas="glow"`) gives
  the app canvas its depth instead, in both themes. Text on any gradient is measured against every stop (`audit`);
  the tint strengths in the additions are deliberately light, so change them only after re-running the audit.
* **Glass in three tiers plus a nested rung**, with a **1px inset top highlight**: that detail sells it as light
  catching an edge. **Nested `inner` surfaces instead of a second bordered box** is what stops a UI looking cheap, in
  either treatment.
* **Two elevation levels, never a third.** Resting and raised. Rows do not lift on hover; they change tone.
* **The type roles and two weights** (400/600; 500 only on facets and nav), `tabular-nums` on every number. **The mono
  face is structural, not decorative**: table headers, eyebrows, KPI labels, citation and version chips take it; body
  copy never does.
* **One icon weight, two sizes**: 16px in tables and chips, 18px in nav, stroke 1.6, always beside a text label or
  with an accessible name. No emoji as icons.
* **Motion is 120–160ms ease-out on panes, drawers and tonal hover, and nothing else moves.** No count-ups, no card
  entrance animations, no skeleton shimmer. Loading is a sequence of real stages, not a spinner.
* **Tags are quiet and smaller than the smallest button**: 11–11.5px against a 13–14px button, tonal, no border, no
  sentence inside. A tag states a fact; it must never read as pressable.

## Components: the doctrine for styling them

The doctrine says how to style each kind of component **the wireframe contains**. It never adds one. Where the
doctrine expects a part the wireframe does not have, style what exists and record the gap.

* **Tables:** the toolbar (search left, filters right, nothing in the middle) sits **above and outside** the card;
  the card is the table's ground, not its container. The search reports its result beside itself ("4 of 7"). Applied
  filters are removable chips with one *Clear all*. **A filtered-empty table is not an empty table and they must
  never share a state.** *"No rows match your search and filters"* with a clear action is a different fact from *"No
  opportunities at Stage 20 yet"* with a create action. Showing the second when the first is true is the single most
  common table bug and it makes working software look broken. A static reference matrix (a legend, a key-value spec
  block) takes no toolbar. About seven columns at 1,280px; one line per cell, two in the first column.
* **Pagination** is built once and reused. The range names the **total** ("1–10 of 47"), reflects the filter,
  disables rather than hides at the ends, and does not appear under about 25 rows.
* **AI or system-generated insight** is styled as the AI Insight card: subtle brand wash, one CTA inside the same
  card, overflow behind a chevron, never growing the card or truncating mid-sentence. People must always be able to
  tell what the data *says* from what we *inferred*. One AI marker per panel, in the BRD's wording (§17). **Reference:
  Topcon's approval-suggestion step**: a *"Suggestion only — you decide"* chip, a grounding line naming the source,
  per-row confidence, a reason per row, **and one row deliberately excluded with its reason shown.**
* **Kanban** is for states a person changes and items that can move *backwards*; fixed-order work is a **stepper**.
  WIP limits in the attention tone. The drop zone is **the one dashed edge we allow**, because the dash means
  something.
* **Calendar has three shapes**: month grid ("when is it free"), agenda ("what is happening"), slot picker ("commit to
  one"). Today takes a ring, selection takes the fill, **never both on one cell**. A taken slot is struck through and
  disabled, **never hidden**: hiding it makes a busy day look empty.
* **A person is a record, not a string.** Person card or face stack where the wireframe names a human; cap the stack
  at three faces plus a count; initials, never a generic silhouette.
* **An activity feed is not a stepper**: a stepper's shape is known in advance, a feed's is not. Newest first, mono
  timestamps, actor and object bold but not the verb, automated entries say "System", and a change carries its
  reason.
* **Chart frame:** the system owns the card, title, **unit**, legend placement and no-data state; the ramp and marks
  follow the palette rules and the `dataviz` skill. A chart without a stated unit is a decoration. **Never colour a
  delta by its arithmetic sign**: colour it by whether the movement is good, and name the comparison period beside
  it.
* **Containers:** **modal** only for irreversible or legally significant acts, never nested, never holding a scrolling
  table · **right drawer** (480px, dismissible) for work attached to the current record · **third pane**
  (persistent, pushes rather than overlays) for an inspector · **stepper** where the order is part of the meaning ·
  **bottom sheet** never on desktop. The wireframe chose the container; style it to this doctrine.
* **A control sits inside the boundary of what it changes**: no divider between an active tab and its panel. Named
  exception: the table toolbar.
* **The header carries identity, navigation context, notifications and profile.** A role switcher, theme toggle or
  demo-path control in product chrome tells the client it is a mock. If the wireframe has one, style it quietly and
  record it as a wireframe gap.
* **Left rail: logo, then navigation, then profile at the bottom.**
* **One agent entry, one drawer.** The agent opens from the one entry the wireframe chose (`data-agent-entry`) into
  its drawer. Two visible ways in to the same agent read as two different things. Inside the drawer: user messages
  right, agent left, suggested prompts outside the input, **loading as a sequence of real stages, not a spinner**,
  and the agent speaks first. In the build it is the platform's live agent component, never an automation that
  writes an answer for the page to show on refresh.
* **No stacked sublines under headers and no redundant preview data.** That is a wireframe rule; the styling must not
  reintroduce it with captions or badges.
* **A fifth data state: UNSET.** A field from a journey the person has not completed shows as visibly unset, never a
  seeded default dressed as their own answer. On one build this produced a cost one-pager reading $26,250 against an
  actual $55,550, and a visit "booked" for March 2011.

## The use-case dial

Same system, same components, both themes. What moves is restraint, ground, treatment and radius scale. In every
row, content surfaces separate visibly from the page, and dense tables stay calm.

| Use case | Surface · fill | Ambient | Ground | Radii | Colour |
| --- | --- | --- | --- | --- | --- |
| **Dense internal tool** (PLM, config, ops console) | solid; fill from the brand's product | canvas glow; no ambient field | a tinted page, content surfaces clearly lighter, solid behind tables | 10 / 6 / pill | a brand-fill rail when the brand is strong; in content, brand only on primary action and selected |
| **Client-facing demo surface** | glass · the brand's own fill style | full aurora, blur 58–70px, vignette | tiers 1–3 | 10 / 6 / pill / circle | brand fill on the rail; one accent pill |
| **Artefact / document studio** | quiet; the canvas is the subject | off or minimal | sheet white on a tinted shell | 28 / 22 / 16 / 12 | greyscale plus one brand accent |
| **Dark-first ops console** | solid or glass | blooms *lighter* than the page | opaque rung for any container holding glass | 10 / 6 / pill | brand-as-text steps up; brand-as-fill holds |
| **Phone, on the move** | solid · flat | canvas glow | solid | 10 / 6 / pill | as dense tool; targets ≥ 40px |

**Ported code gets one card, imposed from outside.** Screens from a separate build each bring their own idea of a
card. On one set of canvases there were **six paddings, four radii and three shadows** between them, invisible one
screen at a time and obvious the moment a dozen stack in one column. **Do not edit them one by one.** One normalising
block at the end: one radius, one surface, one shadow, **three padding tokens only**, media cropped to one aspect
ratio, and **restate the selected and status rings after the normaliser** or the reset eats them.

## The defect register, re-derived on the system itself

**A figure asserted about the system from a measurement taken on a port of it is not evidence.** One "defect" was
recorded that way, a claim that the chart ramp fails its own 2.60 figure, and had to be **withdrawn**: measured across
all twenty triples, the best is exactly 2.60, and the dark pair is exactly 4.24, both as the document claims. A
luminance-preserving port makes this trap worse, because the port's numbers genuinely are the source's, so a wrong
number looks doubly confirmed. **Check every "the file says" against the file.**

The standing lessons, all derived from defects on the record:

* **White on the brand fill**: check every gradient stop, not just the middle one.
* **`.ai` vs `.msg.ai`**: an unscoped insight-card selector captures every agent chat turn.
* **Nested glass in dark**: a container holding glass takes the opaque rung.
* **A theme with no switch** follows the reader's OS and half your work is invisible.
* **Bare rgb triples** survive any regex port.
* **A themed override must be scoped to its theme** (the solid-surface defect).
* **A wrong number in a document is not a wrong colour.** Correct the number.

## Hand it over with these three answers

> **What is the wow factor here? Name it in one sentence.**
> **What would the reviewer or the client push back on first?**
> **What is the weakest part, and do you know it?**

**Answering the third honestly is not a confession, it is the deliverable.** A hand-over that names its own weakest
part gets fixed; one that hides it gets found.

---

## Appendix A · The page skeleton

```html
<!DOCTYPE html>
<html lang="en" data-ds-version="3" data-theme="light" data-surface="solid" data-fill="gradient" data-canvas="glow" data-labels="sentence" data-agent-entry="topbar"
      data-source-brd="scoping-document.docx" data-source-wireframe="<slug>-wireframes.html">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title><Client> · <App> — design system</title>
<style>/* fonts embedded · Step 0 stylesheet, transformed · v3.6 additions · the wireframe's wf-app block */</style>
</head>
<body>
<div class="amb a"></div><div class="amb b"></div><div class="amb v"></div>   <!-- glass only -->
<div class="ds-doc">
  <nav class="ds-nav" data-doc-chrome aria-label="Design system">
    <a href="#overview">Overview</a> <a href="#index">Component index</a> <a href="#brand">Brand and direction</a>
    <a href="#foundations">Foundations</a> <a href="#color">Colour and tokens</a> <a href="#type">Typography</a>
    <a href="#space">Spacing and layout</a> <a href="#icons">Icons</a> <a href="#components">Components</a>
    <a class="sub" href="#cmp-…">…one per entry…</a> <a href="#screens">Screens</a> <a href="#themes">Light and dark</a>
    <a href="#qa">Traceability and QA</a> <a href="#contract">Composition contract</a>
    <div class="seg" role="group" aria-label="Theme"><button data-theme-set="light">Light</button><button data-theme-set="dark">Dark</button></div>
  </nav>
  <main class="ds-main">
    <section class="ds-sec" id="overview" data-brand-status="complete|incomplete"> … </section>
    <section class="ds-sec" id="index"> … </section>   … #brand #foundations #color #type #space #icons #components #screens #themes #qa …
    <section class="ds-sec" id="contract"> … </section>
  </main>
</div>
<script type="application/json" id="ds-manifest">{…}</script>
<script type="application/json" id="build-plan">{…}</script>
<script type="application/json" id="style-sets">{…}</script>
<script id="ds-runtime"></script>   <!-- filled by `ds_tool.py embed` from assets/ds-runtime.js; never typed -->
</body></html>
```

The page's own layout uses the `ds-` classes and tokens only.

## Appendix B · `ds-runtime` (file: `assets/ds-runtime.js`)

It paints each instance's and specimen's state, lets the styled screens' own tabs and overlays work, mirrors the
kit's `:hover`, `:focus-visible` and `:active` rules as `.is-hover`, `.is-focus` and `.is-pressed` for state
specimens, scales each styled screen down to fit where it is shown (it keeps its wireframe width and layout), and runs
the theme switch. `ds_tool.py embed <design-system.html>` puts it into `<script id="ds-runtime">`; never edit it per
client.

## Appendix C · `ds_tool.py` (file: `scripts/ds_tool.py`)

`inventory <wireframes.html> <out.json>`, `fidelity <wireframes.html> <design-system.html>`,
`audit <design-system.html> [out_dir]` and `embed <design-system.html>`; run with `python3 -I`. Its header says what
each checks.

## Appendix D · The composition contract (fill in; ship verbatim in `#contract`)

> **Composition contract for UnifyApps Headless.** Quote and follow this section verbatim.
>
> 1. **Every page is its wireframe screen.** Build each page from `02b-wireframes/<slug>-wireframes.html#<page-id>`:
>    the same regions in the same order, the same components, the same content and copy, the same states and the same
>    interactions. Do not add, remove, rename or reorder anything on a page. `#build-plan` lists each page's pattern
>    and regions. Build each component with the anatomy its catalogue entry shows (header, body and footer regions, icon
>    controls); `#corrections` lists where that differs from the wireframe's drawing, and the content stays as drawn.
> 2. **Style from this file only.** Every component uses its catalogue entry in `#components` (only specimens marked
>    `data-active="true"`) and the variant `#style-sets` names. Every value comes from the token block: no new
>    colour, radius, elevation, type size, weight or spacing step, and no component outside the catalogue.
> 3. **Match the three drawn screens** (`#screens`) for look, spacing and finish. Never copy one screen's content onto
>    another page.
> 4. **States and behaviour.** Every component keeps every state in its catalogue entry: hover, focus-visible,
>    pressed, selected, disabled, loading, error and read-only where they apply, plus the data states its wireframe
>    instance has (empty, filtered-empty, loading, error, no permission, unset), with the wireframe's wording.
> 5. **Shell and settings:** `<shell>` shell (`.app`, `.app-rail` or `.app-top`, `.app-main`, `.app-body`),
>    `data-theme="<theme>"`, `data-surface="<surface>"`, `data-fill="<fill>"`, `data-canvas="<canvas>"`, density
>    `<density>` on `<html>`. Gradients go exactly where the expression card places them (canvas, top bar, the
>    `.wash` signature), the same on every instance, in the two brand colours only.
>    Both themes' tokens stay in the stylesheet.
> 6. **The agent:** one entry only (`<agent_entry>`), opening its drawer, built on the platform's live agent component
>    (streamed replies, real stages, tool outputs in the thread).
> 7. **Data and density:** tables scroll inside `.tblwrap`; about seven columns at 1,280px; one line per cell (two in
>    the first column); every image has a fallback; a count shown twice comes from one query.
> 8. **Overlays, spacing, colour:** drawers and modals only in the kit's sizes and anatomy (header, scrolling body,
>    pinned footer); spacing only from the
>    scale; chart status series use the status palette; deltas coloured by good or bad, not by sign.
> 9. **Pictures:** the drawn pictures are mockups. Seed the app with the real images the BRD names, shown where the
>    mockups show them.
> 10. **No labels for demo, sample or synthetic data** anywhere in the app.
