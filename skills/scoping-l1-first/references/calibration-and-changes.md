# Scoping: calibration examples and version notes

Moved from SKILL.md unchanged; SKILL.md says when to read each part.

## 11. Calibration: how the Pentland example maps to this skill

- **Input**: an email asking for a POV on Product Enrichment and PLM in fashion, a 6-slide deck (future org, Demand vs GSP roles, new-product routes, range-to-release workflow), and a 6-page image-only PDF ("How we operate": strategy → concept → creation → activation, with NPD / Low touch / Zero touch lanes; planning calendar; bottom-up forecast).
- **Type**: A (POV in a known category), secondary C. **Framing**: POV/demo.
- **Research**: about 10 vendors per app, EU AI Act and C2PA, AI-UX guidance; 188 sources. Research also found the client's current stack (Centric PLM, Salsify, SAP, Shopify), which changed the positioning.
- **Catalogue**: PLM 161, Enrichment 159 and AI layer 18 sub-features, plus a 13-agent catalogue and a 36-component UI list.
- **Components**: e.g. Content Hub: content builder, tech pack reviewer, content generator, asset shot-list checker, channel readiness board, claims checker; PLM: line plan matrix, proposal studio, PACE decision room, style stage-gate stepper, critical-path calendar, forecast & sign-off grid.
- **Build plans**: PLM with 5 journey sections plus supporting pages, 19 objects, 3 workflows, one live Copilot and seeded ★ AI. Content app with 6 pages, 6 objects with typed fields, a 7-stage product record, 9 workflows (W1–W9), named seed records, an acceptance checklist and a demo path.
- **Sizing lesson** (from the Pentland scoping reviews): reviewers found 19 objects, many personas and many pages too heavy. They asked for about 10–12 objects, three personas, a handful of well-defined pages and three workflows (reset demo, change stage, generate the PACE pack PPT). They also rejected a draft that had drifted into a product-data and GTIN tool. The fix: keep the whole journey (strategies, concept, PACE, product record, line plan, critical path, materials, approvals) on fewer, richer pages, keep checks inside the product record, and seed every page.
- The client's process stages and meeting names (PACE, IBP, lanes) drove the page order, the stage picklists and the demo story.

A scoping document from this skill should contain everything the Excel and both build plans held, in one Word file, in the structure above.

**What the builds had to improvise** (both apps were built as code apps; the build plans missed these, and the rules above now require them): a generic read workflow as the copilot's tool, an activity-log object, a reset-demo workflow with seed snapshots and date shifting, an object prefix to avoid clashing with an older model on the tenant, one validated change-status workflow for all objects with per-object allowed values, gate conditions per stage, computed completeness/readiness/validation fields recalculated on every save, planted seed defects matching the copilot's expected answers, a deep-link route for agent answers, global brand/season filters, and a browser-side fallback when the agent could not generate a deck. Also note that the inputs spent much of their pages on demand and supply planning while the ask was PLM and Enrichment; the PLM build absorbed it as PACE meetings, forecasts and milestones rather than a third app.

**Don't reuse Pentland's page or component names** (content builder, line plan matrix and the rest above): they are Pentland's answers. **Don't copy these numbers either.** Pentland's counts (two apps, ~160 sub-features per app, 13 agents) fit Pentland. Size each new case from its own process and category.

---

## 12. Calibration: the brand compliance example

- **Input**: one page of meeting notes. The ask was to validate retail shelf compliance from photos using AI or computer vision; the KPIs listed were shelf space, visibility, logo placement, font and tagline; the targets were drinks brands (Diageo and Jim Beam named); field reps are offline, so on-device processing is needed; hundreds of thousands of stores; options weighed were classic vision models vs fine-tuned vision LLMs; the goal was the most frugal solution delivering 7–10 KPIs.
- **Type**: G (AI scoring). **Framing**: POV/demo; the agreed next step was a 3–4 slide proposal deck with a working prototype.
- **What was produced**: 6 KPIs (must-stock SKU presence, share of shelf, campaign and signage, eye-level visibility, brand placement and integrity, price and promo). The asked-for logo, font and tagline items were folded into brand integrity and campaign checks. Each KPI has an industry name, evidence with sources, a checks table, an inputs table with source type and source (manual input, web search or none), a formula, Pass / Needs attention / Fail / Not assessable bands, critical flags (missing hero SKU, counterfeit, price above MRP in India) and real-world example links. Weights per brand total 100, with reasons (price leads for Diageo because its strategy depends on prices reaching the shelf).
- **Components**: e.g. shelf photo capture (offline), KPI scorer, store scorecard, brand-team exception queue, rule & weight configurator.
- These names are this client's; name another client's capabilities from its own work.
- **Lesson**: for scoring apps, the rules spec is the heart of the scope, and the pages, objects and workflows are built around it.
- **Prioritisation lesson** (from the first run of this example): the first draft marked 126 of 175 rows L1 and specified 18 pages, which buried the core flow. Re-tested with the L1 rule (step 5), L1 is the capture → quality check → recognition → KPI scoring → review → follow-up loop, the agents (copilot, vision judge, action planner), the five asked items (shelf space, visibility, logo, font, tagline) plus the 7–10 KPI target, and the research must-haves (availability, price/MRP, critical flags); integrity checks, imports, coaching, model monitoring, digests, WhatsApp, native app and BI export are L2 future scope with no build spec.
- **Readability lesson** (from the VTInfo shelf-compliance run): the content was strong, but the document was hard to use. It ran to about 130 pages with 240 tables and only 3 diagrams, and four build sections held about 60% of the words. The catalogue had 21 columns, so every cell wrapped to a few characters even in landscape. Priority and a separate "Phase 1" column disagreed on 23 rows, and the Phase 1 count was 134 in one section and 131 in two others. Out-of-phase pages, workflows and agents were fully specified anyway, "Phase 2" appeared 53 times across the specs, and the acceptance criteria were printed twice. The fixes now in this skill: Part A / Part B with a reading guide, a lean 9-column catalogue with build and research details in Appendix E and F, no phase flags in specs, every count generated by script, each list stated once, and at least five diagrams.

---

## Changes in v5 (what the design system needs to look like this client)

Each page now says what the person must see to decide, including what they judge by eye and how many items they handle at once. Section 21 adds the hero object with its picture and the other visual objects (21.1), 3 to 5 reference products (21.2), and the typeface, photo style and tone as brand cues. A run that left these out gave the wireframes and the design system nothing visual to work with, and the app came out as rows of text for a business that judges its products by eye.

## Changes in this version (wireframes and design system split)

The wireframes skill now runs after this document and decides how each page works and looks: each page's layout and pattern, the home, the app's signature component and the UI components; the design system designs those components. So this document says what the app must do and leaves how it looks to them: pages keep their purpose, question, decision, data, actions, states and exact wording, with no layout regions, above-the-fold, hero, card anatomy or UI pattern names; section 10.5 and the §21 pattern and custom-component lists are gone; section 23 is the capability inventory, with stable CMP IDs; each status has its tone, picture, document and location fields are marked, every refusal and no-access message is given word for word, and section 19 names the demo day. Examples are from domains we are not scoping, and the Pentland and brand compliance names are marked as theirs.
