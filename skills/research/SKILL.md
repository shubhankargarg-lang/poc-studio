---
name: research
description: Answers a specific research question with cited, source-rated evidence. Built to be called by other skills (for example Requirement Gathering, Scoping and DS in the POC package) and also usable directly. Use whenever a skill or the user needs outside facts looked up and checked, such as a client or company, an industry process, a regulation or standard, competitor or comparable products, benchmark figures, market data, or design and brand references. The caller supplies the question. This skill searches, checks the sources, and returns an answer with sources, confidence and gaps.
---

# Research

Research is a service that other skills call. The calling skill knows what it needs to find out.
Research finds it, checks it and returns it with sources. The caller owns the question and decides
what to do with the answer, so Research stays within the question it was given.

## What a caller sends

| Part | Meaning |
|---|---|
| **Question(s)** | Required. One or more specific questions to answer. |
| **Purpose** | The decision or deliverable the answer feeds, and where it will be used (an internal check, a working draft, or something the client will see). Research sets its depth from this. |
| **Context** | Known facts such as the client, industry, country, and any earlier findings. |
| **Format** | How the answer should come back. Default is below. A caller can ask for a table, a list, or a section that fits its own template. |

A request can arrive as plain text. Pull the parts out yourself and fill gaps from the context.

If a question is too broad to search ("research the client"), ask the caller one short question. When
nobody is available to answer, split it into the most likely specific questions, answer those, and
say that you did.

## How to work

1. **Restate each question in one line** and split broad ones into parts that can be searched.
   Then set the depth from the purpose:

   | Purpose looks like | Depth |
   |---|---|
   | Confirming a single fact or an internal yes/no check | Quick: about 5 to 10 searches |
   | Feeding a working draft, such as a scoping document section or a design direction | Standard: about 10 to 20 searches |
   | Figures or claims the client will see, or a decision that is hard to reverse | Deep: 20 or more searches, several angles, every key figure confirmed by a second source |

   When the purpose is unclear, use standard.
2. **Reuse what exists.** Check the context for earlier findings on the same point, and link to them
   instead of searching again.
3. **Search.** Use `references/source-guide.md` to pick where to look for this kind of question.
4. **Read and rate the sources** you rely on.
5. **Write the answer** in the format below.
6. **Check it** against the list at the end, then return it.

### Search practice

- Use short queries of 2 to 6 words. Start broad, then narrow, and change the wording after a miss.
- Search one topic per query: one competitor, one regulation, one reference site.
- Open the page of anything you rely on. A search snippet is a lead and never a source.
- With subagents available, give each one a question and run them in parallel, then merge the results
  and remove duplicates.
- Stop when every question has an answer, or two differently worded searches found nothing. Record
  that question as a gap.
- Put only public facts in queries. Deal values, internal contacts, pricing and anything marked
  confidential stay out, because queries leave the company.
- If a site refuses access, use another source or note the gap. Design gallery sites sometimes need a
  real browser session; use a connected browser for those.

### Rating sources

Give every finding a strength so the caller knows where to look hardest.

| Strength | Meaning |
|---|---|
| **Strong** | An official or primary source (regulator, standards body, the company's own site or filings, product documentation), or two independent reputable sources that agree |
| **Medium** | One reputable secondary source (established news, industry body, analyst, academic paper) |
| **Weak** | Vendor marketing, case-study outcomes, gallery posts, or anything unverified. Report these as what the source claims |

Forums, unattributed blogs and listicles are leads that point to better sources. Do not build a
finding on them.

## What you return

Use this layout unless the caller asked for another format. When the caller's format differs, keep
the source, date and strength attached to each fact.

```markdown
**Answer:** <2 to 4 sentences that answer the question directly>

**Findings**
| Finding | Source | Date | Strength |
|---|---|---|---|

**Gaps:** <what could not be found, and what could answer it>

**Notes for the caller:** <conflicts between sources, assumptions taken, anything that changes how
the answer should be used. Leave out when there is nothing to say.>
```

For several questions, repeat the layout under a short heading per question, in the order asked.
Lead with the answer and give the evidence after it. At most 8 findings per question, strongest first.

## Rules

Each rule comes with its reason, because the caller builds on what comes back.

1. **Never invent a fact, figure, name or source.** A wrong number in a client deliverable costs
   trust. A missing figure goes under gaps with a note on what would supply it.
2. **Every factual sentence has a link that supports it.** The caller and the reviewer can only check
   what they can open.
3. **Write in your own words.** Quote only when exact wording matters, such as a regulation, and keep
   a quote under 15 words, one per source at most. Never copy paragraphs, tables or lists.
4. **Date what changes.** Prices, leaders, rules, product versions and market figures carry the
   publication date and the date you read them.
5. **Report vendor and gallery claims as claims.** A product page tells you what the vendor says.
6. **Keep to the question.** Add background only when it changes how the answer is used.

## Check before returning

- Every factual sentence has a link, and the link supports it.
- Numbers, prices and dates match their sources exactly.
- Each question is answered or listed under gaps.
- The answer makes sense when read without the findings table.
- No confidential detail from the request went into a query or a source.

Then return the result to the caller in the reply and stop. Carrying on with the caller's own task is
the caller's job.

## Limits

- It does not contact the client, sales or anyone else, and sends nothing anywhere.
- It uses paid or login-only sources only when the user has connected them.
- It does not estimate figures it could not find.

## Improving this skill

When a review changes how research should be done, add one line here so the next run applies it.
