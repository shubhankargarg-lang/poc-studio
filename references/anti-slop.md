# Writing rules for everything POC Studio produces

Every skill follows these rules **while it writes**: documents, screens, slides, narration, messages to the person and
Orbit text. Each skill adds its own rules in its "Quality rules" section, then checks its output against both lists
before it hands over. The AI PM reviews against the same rules, as a safety net.

Read this file once per skill run: `<skill-base-dir>/../../references/anti-slop.md` (the plugin root).

## How to settle conflicts

1. **The quality rules win** over any "make it impressive", "rich detail" or "the wow" instruction. The wow comes from
   the client-specific core action, never from extra panels, sections or decoration.
2. **Answer first per document and per section.** A paragraph may take any shape that helps its point; forcing every
   paragraph into one shape makes the rhythm robotic.
3. **A list for three or more parallel items** (features, fields, steps); **prose for reasoning** and trade-offs. A list
   is as long as the facts.

## Sentences

- Sentences average 15 to 20 words and stay under 25. Readers understand over 90% of a 14-word sentence and under 10%
  of a 43-word one.
- One idea per sentence. Do not chain clauses with semicolons, brackets, arrows or "·".
- Each document, section, screen and message opens with its main point.
- Everyday words, the active voice and direct verbs, with people as the subject: "the approver rejects it",
  "decided". Define a technical term the first time it appears.
- At most one or two em dashes in a whole document, and none in short copy (buttons, titles, empty states).
- Use complete sentences. Write headings and titles as plain statements, without a colon reveal ("The best part: …").

## Content

- Concrete numbers ("from 3 days to 4 hours") in place of praise words. Let the fact carry the weight; do not call a
  point "important", "key" or "critical".
- The swap test: a client brief, summary, title or slide stops making sense with another client's name in it.
- One term per concept, in the client's words, everywhere; and one concept per term.
- Every claim names its source: the client file, the person who said it, the system read, or the research source.
- State each uncertainty once, where it applies, specifically: "Not in the brief; assumed X".
- Quote the client exactly as written, and name who said it.
- Numbers are rounded to the precision the decision needs, with one format per unit across every output.
- Calm and factual: no exclamation marks, flattery, rhetorical questions, dramatic fragments or slogans.

## Endings

- End on the last concrete point, the decision being asked or the next step. Do not add a recap or a closing metaphor.

## Formatting

- Bold at most two points per section. No emoji.
- No heading over a section of two sentences or fewer; merge it into its parent.

## Before handing over

Read the output once against these rules and the skill's own Quality rules, as pass or fail. Fix every line that
fails, then check those lines again. Leave strong sections as they are: fix the minimum.
