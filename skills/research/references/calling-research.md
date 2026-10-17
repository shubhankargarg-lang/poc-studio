# Calling the research skill

A guide for anyone building a skill in the POC skill group (Requirement Gathering, Scoping, DS, or a
new one) that needs outside facts.

## Contents
- What the research skill does
- What to add to your skill
- Writing a good request
- Example requests
- What comes back
- Running several questions

## What the research skill does

`research` is a shared skill that answers a specific question with cited, checked evidence. Your
skill decides what it needs to know. Research searches, rates the sources, and returns an answer with
sources, dates, a strength rating and any gaps. It stays within the question you send and does not
carry on with your skill's work.

Use it whenever your skill needs facts from outside the conversation, for example about a client, an
industry process, a regulation, comparable products, benchmark figures or design references. This
keeps the searching rules in one place, so every skill gets evidence in the same shape.

## What to add to your skill

Copy this section into your skill's SKILL.md and adjust the wording to your stage. Claude reads your
skill when it runs, so this section is how your skill learns to call Research well.

```markdown
## Getting outside facts
When this stage needs facts it does not have, use the `research` skill. Send:
- **Question(s):** specific, one decision each
- **Purpose:** what this stage will decide with the answer, and whether it is an internal check, a
  working draft, or something the client will see
- **Context:** client, industry, country, earlier findings
- **Format:** the layout this stage needs, if different from the default

Treat what comes back as a draft. Check the gaps and the Weak findings before relying on them.
```

Add one or two example questions for your stage under it (see the examples below). Examples show
Claude what a good request from your stage looks like.

## Writing a good request

A request has four parts.

| Part | What to send |
|---|---|
| **Question(s)** | Required. One or more specific questions. |
| **Purpose** | The decision or deliverable the answer feeds, and where it will be used. Research sets how deep to search from this. |
| **Context** | Known facts: client, industry, country, and anything found earlier. |
| **Format** | Optional. The layout your stage needs, such as a table or a list for a template section. |

Tips:
- **Make the question specific.** "What KPIs do accounts payable teams use, and what ranges are
  reported?" works. "Research accounts payable" gives Research nothing to aim at.
- **Ask one decision per question.** Several questions in one request are fine. Each should map to
  something your stage will decide.
- **State the purpose clearly.** Research searches more deeply as the stakes rise:

  | Purpose | How Research works |
  |---|---|
  | Confirming one fact, or an internal yes/no check | Quick: about 5 to 10 searches |
  | Feeding a working draft, such as a scoping document section or a design direction | Standard: about 10 to 20 searches |
  | Figures the client will see, or a decision that is hard to reverse | Deep: 20 or more searches, with every key figure confirmed by a second source |

- **Include the context.** Client, industry and country change the answer, particularly for
  regulations and design conventions.
- **Ask for the format you will use.** Research keeps the source, date and strength attached to each
  fact whatever format you choose.

## Example requests

**Requirement Gathering**
- Question: Does `<named system>` support `<capability the requirement assumes>`? Which regulation
  governs `<process>` in `<country>`?
- Purpose: internal check on whether the requirement can go to scoping as written.
- Context: `<client>`, `<industry>`, `<country>`.

**Scoping (scoping document)**
- Question: Which KPIs do `<industry>` teams use for `<process>`, and what ranges do published sources
  report today and after automation? Which roles take part in `<process>`, and what does each one do?
- Purpose: feeds the success criteria and personas in the scoping document. The KPI figures will be shown to the
  client.
- Context: `<client>`, `<industry>`, `<country>`, findings from Requirement Gathering.
- Format: a table of KPI, range, context, source.

**DS**
- Question: Find 3 to 5 polished dashboard references for `<kind of data>` that combine a KPI header,
  filters and a detail table, and say what each does well. What do `<client>`'s public brand pages
  convey about tone and colour?
- Purpose: feeds the layout and the theme choice for the main feature in the working design.
- Context: `<client>`, `<industry>`, the features from the scoping document.
- Format: for each reference, a link and the idea worth borrowing.

## What comes back

Unless you ask for another format, each question returns:

```markdown
**Answer:** <2 to 4 sentences that answer the question directly>

**Findings**
| Finding | Source | Date | Strength |
|---|---|---|---|

**Gaps:** <what could not be found, and what could answer it>

**Notes for the caller:** <conflicts between sources, assumptions taken>
```

Strength is **Strong** (official or primary source, or two reputable sources that agree), **Medium**
(one reputable secondary source) or **Weak** (vendor marketing, gallery posts, unverified). Research
never invents a figure. Anything it could not find appears under gaps, so your skill should decide
what to do with each gap, such as raising it as a question for the PM.

The answer comes back in the reply. Saving it, or adding it to a document, is your skill's job.

## Running several questions

Send related questions in one request so Research can reuse sources. Send unrelated questions as
separate requests, or run them in parallel with subagents and merge the answers in your skill.
