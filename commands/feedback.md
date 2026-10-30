---
description: Record POC-level feedback in Orbit (how a POC run went, what the outputs got wrong, what should change in how POCs are run) for the next skill analysis
argument-hint: [skill or stage] <your feedback>
---

Record this POC-level feedback in Orbit: **$ARGUMENTS**

This is feedback on the POC run as a whole, not a change request on one document (a change request on a document stays
an Iteration, written by the orbit-writeback skill at that gate).

1. If no feedback text was given above, ask for it in one short question ("What feedback should I record?") and wait.
2. Load the `orbit-writeback` skill (Skill tool: `poc-studio:orbit-writeback`) and follow its **`/feedback`** section
   exactly. It uses the same UnifyApps Headless tenant tools and the same write rules as every other Orbit write.
3. Do not create an Activity row, do not update the POC row, do not send a Slack message: feedback does not move the POC.
4. The row carries a `skill` field: the skill or agent the feedback is about (named by the person, or decided from
   the text and this session), or `general` when it could be several or none fits — as the `/feedback` section says.
5. Reply with one line: `Recorded as FB-<…> for <client_name>, under <skill name or General>. It goes into the next
   skill analysis.` If the write fails, show the error in one line and what to do.
