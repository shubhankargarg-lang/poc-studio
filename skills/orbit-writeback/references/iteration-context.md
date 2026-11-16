# Iteration context: how to decide each ask (orbit-writeback Moment 2c)

Adapted from the POC Studio feedback-capture skill's bucketing rules, for HTML wireframes and the v1.46 design
system. You are adding context to what the person asked at one gate. The person's words are evidence and are never
changed; your context is the layer that makes the skill change actionable.

## 1. Which iteration, or a new one, or not feedback

- **An existing iteration** when the turn is the change request itself, repeats it, explains it, narrows it, or
  complains it is still not done. Put every such turn in its `turn_ids` (that is how "asked N×" is counted).
- **A new ask from the chat** when the person asks for something (a change, a fix, a missing thing, a complaint
  about the output or the process) that never became a change request: said while a stage ran, in an approval
  ("Approve, but…"), in an "Other" answer. One new item per distinct ask; repeats go in the same item.
- **not_feedback**: questions about how things work, answers to the run's setup questions, thanks, status, sign-in,
  choices between offered options with nothing added, chatter about another POC or about POC Studio's own tooling.
- One ask = one item. Two different asks in one message become two items with the same turn id.

## 2. The context (the line people read in POC Build Loop)

At most 60 words, plain English, in this order: **what it is about** (screen, section or element, by what it does),
**what the person wants**, and **the general rule** a skill could follow so nobody has to ask again. Example:
"On the home screen, the summary stat cards go above the charts and lists, so the person reads the totals first.
Applies to any dashboard home." Never a client name, record id or amount in the rule part. Read the person's
screenshot if they pasted one, and the agent's line before the turn (`before`), to know what "this" means.

## 3. The skill to improve (`root_skill`): where the problem first appeared

The skill whose output first held the problem, so fixing that skill stops it coming back. Never the place it was
noticed. One of the 12 keys.

| The ask is about | root_skill |
|---|---|
| RG document, client files, samples, client questions, the Systems table | requirement-gathering |
| A client system's connection, objects, fields; the AI models used or failing | connector-discovery |
| BRD content: personas, L1/L2 scope, features, pages that exist, business rules, seed plan, statuses, exact copy, a fact stated in the BRD | scoping-l1-first |
| What a screen shows and in what order, navigation, views, what opens where, the component list, the journey (the wireframe HTML) | wireframes |
| How anything looks: colour, gradient, type, spacing, size, logo, shell styling, component look and states, light and dark | design-system |
| Zen planning questions or plan, platform route, the built app: a bug, a broken flow, an agent answering wrongly, missing seed data in the app, the build departing from a correct BRD, wireframe or design system | platform-master |
| Demo script, deck, video, narration, timing | poc-collateral-studio |
| Installing or checking the collateral tools | poc-collateral-setup |
| An outside fact or source from research | research |
| Process: stage order, too many or too few questions, gates, Zen or Sonic, skips, resume, time taken; a review that passed something the person then had to ask for | poc-orchestrator |
| How a one-off asset run behaved (its questions, its approval) | asset-run |
| What shows in Orbit or Slack, versions, links, tickets | orbit-writeback |

**Tie-breaks, in order:**
1. **Look** (colour, size, shape, font, icon style, spacing) → design-system at any gate. Only when the app ignored
   the design system it was given → platform-master.
2. **Arrangement** (where a region sits, its order, what opens where) → wireframes when the approved wireframe drew
   that screen; when the wireframe already had it right and the app departs → platform-master.
3. **Presence or name** (add, remove, rename a page, section, card, tab, control, label) → where it first appears:
   in the BRD's feature list or page specs → scoping-l1-first; only in the wireframe → wireframes; only in the build
   → platform-master. Size never decides it. A small addition at the build gate to a page that exists (a status
   chip, a line of copy) → platform-master.
4. **Facts**: wrong in the BRD → scoping-l1-first; copied from a research answer → research; misread from client
   files → requirement-gathering.
5. **Seed and demo data**: the BRD's seed plan left it out or set it wrong → scoping-l1-first; the plan had it and
   the app does not → platform-master.
6. **Brand chrome** (logo, app-name lockup, avatar, favicon) → design-system.
7. **Status colours** → design-system; status words → scoping-l1-first.
8. **A UnifyApps product defect** no skill could avoid → poc-orchestrator only if the run should have routed around
   it; otherwise give it `kind: app_fix` with context saying it is a platform defect.

## 4. Practice or app fix (`kind`)

- **practice**: a rule that would help other POCs (an order, a look, a missing kind of thing, a process habit).
- **app_fix**: touches this POC only and no skill could have known (a seed value, one record's name, a typo in one
  label, one client-specific wording). App fixes never become skill proposals.

## 5. Outcome and confidence

- **outcome**: for an ask about something you can see, compare the before and after screenshots the AI PM kept
  (Moment 2c, "Before-and-after check"); otherwise look at the version approved at this gate (the document, the wireframe HTML, the design system, the
  app version). `done` with `outcome_version` (`v3`, `App v5`) when it shows the change; `not_done` when it does not;
  `regressed` when an earlier version had it and this one lost it; `unclear` when you cannot tell.
- **confidence** (0–100): high (80+) when the ask is clear, you know which element it means and you checked the
  outcome (for a visible ask: on the before-and-after screenshots); medium (50–79) when one of those is uncertain; low (under 50) when you are guessing what "this" means.
