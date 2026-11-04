---
name: connector-discovery
description: Finds, tests and designs every integration a UnifyApps POC needs with a client's own system (Salesforce, ServiceNow, SAP, HubSpot, Jira, a database or any other connector), and keeps the AI models the build uses working. In POC Studio it is called on every POC, after Requirement Gathering and before Scoping (stage 1c); its Part A (the client system) runs only when the requirements name a client system the app reads from or writes to, and its Part B (the AI models) runs every time. It asks the person for the connection, then uses UnifyApps Headless (the tenant's platform connectors) to validate the connection, read the real objects and fields, find the connector triggers and actions each need requires, test every read for real and every write without writing, and design the automations to build (trigger, steps, connector operations, field mapping, errors, limits). It returns an Integration Spec that Scoping copies into the BRD's integration, workflow and data sections, and that the build stage passes to UnifyApps Headless, so the build uses the same connection, operations and fields that were proved here. It also keeps the AI models the build depends on working: before the build it records, for each model slot the build uses (TEXT_GENERATION, Answer Generation, EMBEDDING / embeddingModel, ranking model and the others), a connected model card and a fallback on a different provider, each proved by one real test call (Call LLM model with options, or Fetch Embeddings), and writes them into the BRD, and whenever UnifyApps Headless runs an automation, an agent, a knowledge index or any other step whose model has run out of credits or quota, it finds models that are still working and lets the person choose the replacement, then hands the switch to UnifyApps Headless and re-runs only the failed step. Read-only on the client system; nothing is created on the tenant.
---

# Connector discovery

The client's system is only reachable through the client's **connection in UnifyApps**. This skill uses that
connection, through UnifyApps Headless's tenant tools, to answer three questions before anything is scoped:

1. **What is really there?** Objects, fields, types, picklist values, configuration records, counts, rights.
2. **What can the platform connector do with it?** The exact triggers and actions (operation names, inputs, outputs)
   that serve each thing the app must do, tested read-only.
3. **Which automations do we build?** One spec per automation: its trigger, its steps, the connector operation of
   each step, the field mapping between the client system and the app's objects, error handling and limits.

The result is the **Integration Spec**. Scoping writes it into the BRD; the build gives it to UnifyApps Headless. Nothing
about the client system is decided twice, and nothing in the BRD names an object, field or operation that was not
seen here.

The skill has two parts. **Part A** (steps 1–9) is the client system: it runs only when the approved requirements name
a client system the app reads from or writes to. **Part B** (AI models) runs on every POC: the model inventory before
Scoping, the model test again before the build, and model recovery whenever a model runs out of credits or quota.

```
Requirement Gathering approved → stage 1c: this skill, every POC
   │  Systems table has a read or write row?  ── no → integration_status: not_needed (Part A skipped)
   ▼ yes
Part A: 1 Connection message (person) → 2 Validate connection → 3 Needs list → 4 Read the schema
→ 5 Find connector operations → 6 Test them (read-only) → 7 Design the automations
→ 8 Write the Integration Spec → 9 Checkpoint (person)
   ▼ (both paths)
Part B: model inventory (scope: models) → Scoping (input) → … → Build (scope: verify, input)
Any time a model runs out of credits or quota → Part B, model recovery
```

## When it runs

| Situation | Runs? |
|---|---|
| Requirement Gathering is approved (POC Studio stage 1c: every POC) | Yes, before Scoping. Part A once per system whose Systems row says **read** or **write**; then Part B's model inventory |
| No such row (systems are reference only, or simulated in UnifyApps) | Part A does not run: record `integration_status: not_needed`. Part B's model inventory still runs |
| Scoping needs one fact or one operation the spec does not have | Yes, `scope: item` for that object, field or operation (no question to the person: the connection is already given) |
| The person fixed access, added objects, or the requirements changed | Yes, `scope: check` (re-tests from the saved spec) or `scope: item` |
| Build stage: before `/ua:plan`, to confirm the spec still holds | Yes, `scope: verify` (re-runs step 2, the read tests of step 6 and Part B's model test; resolves operation versions). No spec in the workspace → `scope: models`, and Part A `scope: full` only if the BRD names a client system the app reads from or writes to |
| Before the build, or whenever asked: which AI models can the build rely on | Yes, `scope: models` (Part B, Model inventory) |
| **Any time** UnifyApps Headless reports that a step failed because a model's credits, quota or billing ran out — an automation's LLM node, an agent's answer, a knowledge index (embedding), a reranker, a vision or speech step, a test run — in the build, a test, a fix or a demo | Yes, `mode: model-recovery` (Part B, Model recovery). It does not matter whether the POC has an external system |
| Run on its own ("test this Salesforce connection for this use case") | Yes, standalone: needs a connection, the system and a few sentences of what the app must do |

## Inputs

| Part | Meaning |
|---|---|
| **Workspace** | `<workspace>` with `state.json` and `context-log.md` (POC Studio), or any folder (standalone) |
| **Requirements** | The approved Requirement Gathering document: its **Systems** table (system · what the app does: read / write / none · objects or data named · environment · requirement · source), the current process steps and the asks |
| **Connection answers** | From the connection message (step 1) |
| **Tenant** | The run's UnifyApps tenant (POC Studio: Orbit UAT, `orbit.uat.unifyapps.com`). UnifyApps Headless must be set up and signed in there (`/ua:setup`) |
| **Run mode** | `zen` or `sonic` (POC Studio run mode). Access questions are the person's in both |
| **Scope** | `full` (default) · `item` · `check` · `verify` · `models` — or **`mode: model-recovery`** with the failed run, trace or index error |

## Rules (always)

1. **Ask before assuming.** Never assume a connection, a right, an object, a field, a value or an operation. Anything
   not confirmed is **[Assumed]** with its reason, and stays visible to Scoping, the AI PM and the build.
2. **Access questions belong to the person** — connection, write access, write test, missing rights, the checkpoint.
   Never answered by the AI PM or a reviewer, in Zen or Sonic. Start each with `SYSTEM_ACCESS:`.
3. **Read-only on the client system.** Run only read operations (list, describe, query, get, search, count, lookup).
   Write operations (create, update, upsert, delete, send, upload, merge, execute code) are **validated, never run**:
   their input schema is checked against the mapping and the connection user's rights are read. The only exception is
   one sandbox or dev **write test** after the person's explicit yes. Never on production.
4. **Nothing built on the tenant.** No workflow, object, data source or connection is created. Automations are
   designed here and built in the build stage. A model switch (Part B) is made by UnifyApps Headless after the person chooses, never by
   this skill.
5. **Secrets stay secret.** Never read a connection's stored inputs, never list connections unfiltered, never print
   credentials, cookies or tokens. Connections are created by the person.
6. **Business data is masked.** Configuration records (questions, picklists, templates, statuses) are kept in full;
   business records only as counts and at most 3 masked sample rows.
7. **Stay small.** At most 15 objects described per system on a full run; objects the needs list uses come first,
   related objects after. At most 200 configuration records per object. Say what was left out.
8. **Retry ceiling.** A failing call is retried at most twice, each time in a simpler form (split an OR or IN filter,
   drop a subquery, add a LIMIT, remove the field the error names). Then record the error and the limit, and move on.
9. **Operation versions are not frozen here.** Record operation names and input fields; the build resolves versions
   again (`scope: verify`). A version copied from this run is a hint, never a value to reuse blindly.
10. **A model switch is the person's choice.** Never switch a model silently, never pick for the person, never buy
    credits or raise a limit (spend). This skill finds and checks the alternatives and asks; UnifyApps Headless makes
    the switch. The person chooses in Zen and in Sonic.

## Tools (UnifyApps Headless)

Load with ToolSearch in one call (`select:` the names; the prefix is the session's, e.g.
`mcp__plugin_ua_automation-code__…`).

| Need | Tool |
|---|---|
| Find the connection | `list_connections` (filter by connector `appName` and name; read id, name, appName, active, owner, created) |
| A connector's connection settings (environment, instance URL) without secrets | `get_connection_schema` |
| Find triggers and actions | `search_operations` (by `appName` and a word: `query`, `describe`, `trigger`, `updated`, `create`, `update`, `upload`…) |
| An operation's inputs, outputs and whether inputs are dynamic | `get_operation_schema` |
| Fill a dynamic input (object list, field list) the way the builder does | `run_lookup` |
| Run a read operation on the client connection | `run_connector_operation` |
| Patterns of real automations using an operation | `find_workflow_examples` |
| How a workflow step is written (for the automation design) | `get_dsl_reference` |
| Model cards: provider, slots, tool calling, connection state | `list_models` (agent-builder server; `forSlot` with a tenant slot name; returns `connectionFound`, `connectionActive`, `canCallTools`, `provider`, `fills` — see Part B; `includeUnusable` only to explain why a card is missing) |
| Where a model is used | `get_agent` (its model slots), `get_knowledge_sets` (a set's embedding model), `open_workflow` / `get_workflow_dependencies` (an automation's LLM or AI nodes) |
| What failed and why | `inspect_workflow_run` / `list_workflow_runs` (automation run and node error), `read_trace` (agent run), `check_knowledge_status` (indexing errors) |
| Prove a model answers (the model test) | `run_connector_operation` on `conv_ai_by_unifyapps` with `conv_ai_by_unifyapps_call_llm_model_with_options` (chat cards) or `conv_ai_by_unifyapps_fetch_embeddings` (embedding cards): one direct run, nothing saved on the tenant, a fraction of a cent. Exact inputs in Part B, "The model test" |

If UnifyApps Headless is not set up or signed in, ask the person to run `/ua:setup` and sign in themselves, then
continue. If the tools cannot be used at all, say so and mark the system `assumed` (no browser workaround unless the
person offers their own sign-in to the client system, and then read only).

## Step 1 — The connection message (to the person, once, all systems together)

One plain line first, from the Systems table:

`SYSTEM_ACCESS: The approved requirements use <n> client system(s): <System> (<what the app does there>)[, …].
Before scoping I'll test <it/them> through the client's connection in UnifyApps, read-only: the objects and fields,
and the connector triggers and actions the app will need. Please give me the connection for each one.`

Then one AskUserQuestion round (up to four questions per call; more → a second round). Per system:

| # | Question | Options |
|---|---|---|
| 1 | `SYSTEM_ACCESS: Is there an existing <System> connection for this client in UnifyApps (<tenant>)? Type its name or ID in "Other".` | Yes, I'll give the name · Yes, name unknown (I'll search) · No connection yet |
| 2 (only when the app writes) | `SYSTEM_ACCESS: The app needs to <write action> in <System> (<environment>). Can the POC write there through the connection?` | Yes, it can write (I'll still check the rights, read-only) · Read only (the POC saves in UnifyApps; the write is planned) · Not sure, please check |
| 3 | `SYSTEM_ACCESS: How should changes in <System> reach the app?` (only when the requirements need the app to react to a change, e.g. "plan ready when the proposal is accepted") | Real time if available (recommended) · Every few minutes is fine · Only when the user acts in the app |
| 4 | `SYSTEM_ACCESS: Besides what the requirements name (<objects>), are there <System> objects or fields you want me to check?` | No, use the requirements · Yes, I'll list them (type in "Other") |

Answers: a name or ID → step 2 with it. "Name unknown" → one filtered search; several matches → ask which (name,
owner, created date; up to four). "No connection yet" → offer: add it now in <tenant> → Connections (the person signs
in to the client system themselves), or carry on with that system marked [Assumed]. Record every answer in
`state.json` → `integrations[]` and `context-log.md` as a human decision. A resumed run never asks again.

In POC Studio, remove the autopilot file before asking any `SYSTEM_ACCESS:` question (so the owner also gets the Slack
nudge) and recreate it after the answer; the `route-questions` hook letting these questions through is only a safety
net. The same holds for the model choice in Part B (model recovery step 4).

## Step 2 — Validate the connection

1. The connection exists, is **active**, and uses the expected connector (`appName`).
2. Its environment matches the Systems table (sandbox, dev, production) when the connection schema shows it. A
   production connection on a POC → tell the person in one line; continue read-only only if they confirm.
3. The cheapest read works (e.g. Salesforce `SELECT COUNT() FROM <main object>`, ServiceNow one `sys_user` row,
   SQL `SELECT 1`). An auth error → ask the person to re-authorise it in <tenant> → Connections, try once more,
   never loop.
4. **Who is the connection user?** Read it with a query, not from the connection's name (Salesforce: the user behind
   the session, e.g. `SELECT Id, Username, Profile.Name FROM User WHERE Id = '<id from a record the connection
   created>'` or the connector's "current user" operation if it has one; ServiceNow: `sys_user` for the integration
   account). Note when it is an admin: a real end user may have fewer rights.

Record `connection: { id, name, app_name, environment, active, validated, user, user_profile }`.

## Step 3 — The needs list (from the requirements, before reading)

One row per thing the app must do in the client system. This list drives everything after it.

| Field | Meaning | Example |
|---|---|---|
| `need_id` | `N-01` … | N-03 |
| `kind` | **event** (the app reacts to a change), **read**, **find** (search by a field), **add**, **update**, **file** (attach or download), **delete** (rare; flag it) | event |
| `object` / `fields` | In the client's words first; resolved to API names in step 4 | Opportunity, StageName |
| `condition` | For events and finds: what must be true | StageName becomes "Proposal Accepted" |
| `purpose` | Why the app needs it | start drafting the plan |
| `requirement` | The ask it serves, with its source (Requirement Gathering line, email, doc) | "plan ready when the proposal is accepted" (client email) |
| `timing` | real time · polling every N min · on user action · scheduled | real time (answer to question 3) |
| `volume` | Expected records per run or per day, if known | a few per seller per month |

Add the person's extra objects (question 4). Keywords for matching come from this list and the use case nouns.

## Step 4 — Read the schema

**Schema strategy** — the first that works for this system:

| Strategy | When | How |
|---|---|---|
| **A. Metadata query** (preferred) | The schema is queryable | Salesforce: `EntityDefinition`, `FieldDefinition`, `PicklistValueInfo`, `EntityParticle` (create/update flags) by SOQL, one object per query. ServiceNow: `sys_db_object`, `sys_dictionary`, `sys_choice`. SQL: `information_schema.tables/columns`, constraints |
| **B. Describe operation** | A describe exists, A does not | One describe per object (outputs can be large or cut) |
| **C. Infer from records** | API-first systems (HubSpot, Jira, Zendesk, Workday, NetSuite REST, Sheets, generic REST) | The record-returning operations are the objects; fields and types from their output schemas and 1–3 sample records, marked `inferred`. Use any properties / fields / metadata operation the connector has for picklists and custom fields |

**Read in this order:**

1. **List objects** (filter by the client's namespaces or prefixes when the list is large).
2. **Resolve the needs list**: map every object and field word to an API name. Unresolved → `not_found` with the
   closest candidates.
3. **Describe** the objects the needs list uses first, then objects they reference, up to 15: fields (API name,
   label, type, length, required), picklist values, references, record types, create and update flags.
4. **Configuration records** (questions and answer types, templates, statuses, reason codes…), up to 200 per object.
   Follow the chain to where an answer type is really defined.
5. **Counts** for each described object; for configuration under a parent, counts **per parent** and the parents
   that have **none**.
6. **Rights** of the connection user on every object and field the app writes: Salesforce `ObjectPermissions` and
   `FieldPermissions` through the user's permission set assignments; ServiceNow ACLs and roles; SQL privileges.
   Not readable → say so; flags alone are reported as "flags only".

## Step 5 — Find the connector operations

For every need, find the platform operation that will serve it in the build, and read its schema.

| Need kind | Look for (by `search_operations` on the connector) | Record |
|---|---|---|
| event | Triggers: real-time record updated / created (e.g. Change Data Capture or platform events), polling "new or updated record (batch)", webhook / inbound notification | trigger name, mode (real time / polling / webhook), its inputs (object, fields to watch, filter), its output (which fields arrive), and its prerequisites (e.g. CDC enabled for the object, an outbound message or Flow configured by the client) |
| read / find | Query (SOQL, SQL, encoded query), get by id, search, list with filter | operation name, the exact query or filter text that worked in step 6, paging |
| add / update | Create record, update record, upsert by external id, bulk variants | operation name, required inputs, how a record is chosen (id, external id), what it returns |
| file | Upload file / attach, download file | operation name, size limits, where the file is linked |
| delete | Delete record | operation name; flag it to the person, it is never tested |

For each operation: `get_operation_schema` → inputs (with `dynamic` ones filled by `run_lookup` for the target
object), outputs, and the name of every field the mapping will use. Check `find_workflow_examples` for a working
pattern on the same connector. Several candidates → prefer real time over polling (when the person wanted real time
and its prerequisites hold), a query over many gets, upsert over find-then-create when an external id exists.

**No operation fits** a need → `gap` with the reason, and the closest workaround (e.g. "no trigger for this object:
poll the query every 5 minutes", "no upload action: use the REST API action with a content body", "custom connector
needed"). A gap is never hidden: it becomes [Assumed] and a design decision for Scoping.

## Step 6 — Test them (read-only)

| Operation | Test | Result |
|---|---|---|
| Read / find / query | Run it on the client connection with the real filter, `LIMIT 1`–`5` | `proved` (ran; rows or zero rows) · `failed` (error) |
| Trigger | Do not fire it. Check: the trigger operation exists for the object; its inputs accept the object and fields (lookup); its prerequisites hold where readable (e.g. Salesforce: the object is enabled for Change Data Capture, `SELECT … FROM PlatformEventChannelMember` or the connector's lookup); the change it waits for exists in real data (e.g. records already at the target stage) | `ready` · `prerequisite missing: <what>` (with the fallback trigger) · `not_testable` |
| Create / update / upsert | Do not run it. Check: every mapped field exists, is createable / updateable, its type and allowed values match the source; the connection user has the right (step 4.6); required inputs are all mapped; locking or validation rules the system reports (when readable) | `ready` (permission) · `flags_only` · `blocked: <field or right>` |
| File | Check the operation's inputs and size limit; the user's create right on the file object | `ready` · `flags_only` · `blocked` |
| Write test (optional) | Only after the person's yes, only on sandbox or dev: one record named `POC-TEST <POC or run id> <date>`, through the real operation; give the person its id to remove (never delete it yourself) | `proved` · `failed` |

Never: run a write operation without the write test's yes; fire or register a trigger; change client configuration.
A `blocked` or `failed` result on something the core flow needs → ask the person (rights to fix, or the POC saves in
UnifyApps and shows the client write as a planned step).

## Step 7 — Design the automations

Group the needs into the automations the build will make. One spec per automation, `AU-01` … (Scoping renames
them to its `WF-` ids and keeps the `AU` id as a reference).

| Part | What to write |
|---|---|
| Name and purpose | e.g. AU-01 "Proposal accepted → prepare plan": what it does and which requirement it serves |
| Trigger | The trigger operation (or app event / schedule), mode, object, condition, the fields it delivers, its prerequisite and the fallback if the prerequisite is missing |
| Steps | Numbered. Each step: the connector operation **and the connection (name and id) on that step**, or an app step (app object write, agent call, rule), its inputs **mapped field by field** (client field ← app field or constant), and what it outputs to the next step. The trigger names the connection too |
| Field mapping | Table: client object.field · type · direction (in / out / both) · app object.field · transform (as is, picklist map, date format, HTML → text, id lookup) · allowed values |
| Idempotency | The key that makes a repeat run harmless (e.g. "one plan per opportunity id"), and how duplicates are detected |
| Conflict rule | For two-way data: which side wins and how a conflict is detected (e.g. "compare the current client value with the value read at draft time; a difference is a conflict for the user") |
| Errors and retries | Which errors are retried (lock, timeout, rate limit) and how often; which stop and notify; where the error is shown |
| Limits | API calls per run, query limits found in step 4 (e.g. "no parent-child subqueries"), payload or file size, rate limits |
| Human gate | Where a person must approve before a write (e.g. "nothing is written before Confirm & save") |
| Status | `Live` (every step `proved` or `ready` by permission) · `Live with assumption` (a `flags_only` or `not_testable` step) · `Planned` (a `blocked` step or a `gap`: built against app data, the client write shown as planned) |
| Test plan for the build | The read queries that proved it, the first test run to do after building (with the sandbox record to use), and what "working" looks like |

Also write the **app-side objects** the automations need (only the fields that hold client data or ids: e.g.
`op_opportunity.sf_opportunity_id`, `op_answer.sf_value_at_draft`), so Scoping's data model and the mapping agree.

## Step 8 — Write the Integration Spec

In `<workspace>/01c-integration/` (standalone: `<cwd>/connector-discovery/<system>/`), two files and a working folder:

- `Integration Spec - <Client> - <Use case>.md` — for people (layout below);
- `integration-spec.json` — the same, for Scoping and the build (format below);
- `_working/` — raw reads (unmasked, never uploaded), operation schemas, the queries that ran.

**Check before saving (both files come from one data structure, written by one script; never edit one by hand).**
Stop and fix, then save again, when any of these fails:

| # | Check |
|---|---|
| C1 | Every need in `needs[]` has an entry in `operations[]` whose `need_id` is that need (its trigger or action), or the need's result is `gap` with its workaround |
| C2 | Every connector step of every automation names an `op_id` that exists in `operations[]`, and every trigger names one |
| C3 | Every operation, step and trigger carries the connection id, and it is the validated connection of step 2 |
| C4 | Every client object and field named in `operations[]`, `automations[]` and `field_mapping[]` exists in `objects[]` (or is in `assumed[]`) |
| C5 | The counts in the summary (needs by result, automations by status, [Assumed]) equal the rows they count |
| C6 | Every operation named in the `.md` is in the `.json`, and the other way round |

Record the result as `checks: { "C1": "pass", … }` in the JSON and one line in the `.md` summary.

Layout of the `.md` (no section dropped; an empty one says "None"):

```
# Integration Spec — <Client> — <Use case>
Date · tenant · generated by connector-discovery

1. Summary — per system: connection, environment, connection user, objects read, needs (proved / ready / flags only /
   blocked / gap), automations (Live / Live with assumption / Planned), [Assumed] count
2. Connection — name, id, connector, environment, user and profile, how it was validated
3. Needs list — N-xx rows with the result of each
4. Objects and fields — per object: fields, types, picklists, references, counts, per-parent counts, rights
5. Configuration records — in full (e.g. every plan question with its answer type and options)
6. Connector operations — per need: trigger or action name, inputs used, outputs used, prerequisite, test result
7. Automations — AU-xx specs in full (step 7)
8. Field mapping — one table per object, both directions
9. Limits and rules — query limits, API budgets, rate limits, locking, conflict rule
10. Assumed — item · why · what would confirm it · impact
11. For the BRD — the exact rows Scoping copies (below)
12. For the build — the exact build-request block (below)
```

## Step 9 — Checkpoint (to the person)

One line: `SYSTEM_ACCESS: <System>: connection OK (<user>), <n> objects read, <a> of <b> needs proved or ready,
<k> automations (<l> Live, <m> planned). Spec: 01c-integration/Integration Spec - <Client> - <Use case>.md.`

Question: `SYSTEM_ACCESS: Go on to scoping with this?` — **Go to scoping** · **Add objects or needs** (type them;
run `scope: item`, then ask again) · **Fix access first** (wait for "done"; run `scope: check`, then ask again).
In Sonic, ask only when a core-flow need is `blocked` or a `gap`; otherwise log the line and continue.

## How Scoping uses it (the BRD)

Pass the Integration Spec to the scoping skill as an input, with this instruction:

> The Integration Spec is the source of truth for the client system and its integration. Copy, do not re-invent:
> - **§12 Data model:** client fields the app stores (ids, values at draft, external keys) exactly as its field mapping
>   names them; configuration records exactly as listed.
> - **§14 Workflows:** one WF per AU spec, keeping its trigger, steps, connector operations, idempotency, conflict
>   rule, errors and human gate; write "AU-xx" in each WF's spec. **Every client-system step names the connection
>   with its id** — the trigger and each connector read and write, e.g. "salesforce_update_record_batch on
>   <connection name> (<connection id>)" — not only the first step. A WF with a client step that
>   does not name it is incomplete.
> - **§15 Integrations:** the systems table from its summary (connection name and id, direction, mechanism = the
>   operation names, frequency = trigger mode, auth = the connection); §15's field-mapping table = its field mapping.
> - **§13 Agents and §17 AI trust:** each model slot's card id and its fallback, from `models[]`.
> - **Document Control:** a "Connector discovery" row with the date, the connection name and id (or "no client
>   system"), and the status.
> - **§5.4 Live vs simulated:** from each AU's status (Live, Live with assumption → Live plus an assumption, Planned →
>   **Mocked**, with the client write shown as planned, recorded as a Decision).
> - **§5.6 Assumptions:** every item in its Assumed section, with its reason and impact.
> - **§18 Non-functional:** its limits (API budget per run, query limits, rate limits, file size).
> - **Evidence log:** each fact used, with the source "Integration Spec §<n>".
> - A client fact or operation it does not have → run connector-discovery `scope: item`; only "not found" becomes an
>   assumption.

The AI PM checks at the Scoping gate that §12, §14 and §15 match the spec, that every client-system step in §14
names the connection id, that nothing Live depends on a `blocked`
step or a `gap`, and that every access answer came from the person.

## How the build uses it

Before `/ua:plan`:

1. Run `scope: verify`: the connection is still active, the read tests still pass, and each operation name resolves
   to its current version (`get_operation_schema`). Anything that changed is listed for the person.
2. Add this block to the build request, from section 12 of the spec:

```
Integration spec (from connector-discovery, verified <date>):
- Connection: <name> (<id>), connector <appName>, <environment>. Use this connection in every client-system step;
  never create another.
- Automations to build: AU-01 … AU-n — each with its trigger operation, steps and connector operations, field mapping,
  idempotency key, conflict rule, retries and human gate as in 01c-integration/integration-spec.json.
- Use only these client objects and fields: <list>. Query limits: <list>.
- Planned (not live) client writes: <list> — build them against app data and show the client write as planned.
- First test runs after building: <from each AU's test plan>.
- AI models (from the model inventory, checked <date>): <slot> → <model card> (fallback <model card>) for each slot
  the build uses. Before indexing knowledge, index one document and check its status, then the rest. If any step
  fails on credits or quota, stop that step and run connector-discovery `mode: model-recovery`; never switch the
  model yourself.
```

3. The build's plan review (POC Studio: platform-master job 2) checks every client-system task against the spec:
   same connection id, same operations, mapped fields only, Planned items not wired live.

## Part B — AI models: inventory and recovery

Part B runs on every POC, with or without a client system. Every POC build runs AI models: chat/LLM models in agents and automation LLM nodes, embedding models for knowledge
indexing, and sometimes rerankers, vision, speech or image models. A model whose provider account has run out of
credits or quota fails at run time, often for every item at once (e.g. all 7 knowledge documents failed to index). This
part keeps that from costing a ruling, a guess and a full re-run.

### What `list_models` really returns (read this first)

Checked on Orbit UAT, 3 Nov 2026. Use these names, not generic ones:

| Field | Meaning | How to use it |
|---|---|---|
| `id` | The model card id (e.g. `e_6acca2af70b66f5702c8b59f`) | The value an agent slot, knowledge set or LLM node takes, and the value the BRD names |
| `name` | Free text, often misleading (a card named "…Azure OpenAI…" can have `provider: deepinfra`) | Show it to the person; never decide on it |
| `model` | The provider's model id (`claude-sonnet-5`, `text-embedding-3-large`) | Some cards have none: treat them as last choice |
| `provider` | `anthropic`, `vertex_ai`, `amazon_bedrock`, `openai`, `azure_openai`, `openrouter`, `deepinfra`, `custom_http_…` | The only quota signal available: `list_models` does **not** show which provider connection a card uses, so "different account" can only be judged by a different `provider`. Some cards have no provider: they cannot be judged, so never pick one as the fallback for an exhausted provider |
| `fills` | The slots the card may fill | Filter with `forSlot`. Some cards have no `fills`: skip them |
| `canCallTools`, `canCallMultipleTools` | Whether the card can drive tool calls | **Required `true` for any agent that has tools** (most do); `canCallMultipleTools: true` when a turn calls several tools |
| `thinking` | Thinking settings, when the card has them | Note it; thinking cards need a larger output budget |
| `connectionFound`, `connectionActive` | Whether the card's connection exists and is switched on | Keep only cards with **both `true`**. `false` → the card fails every run. `null` → could not be read in time: unknown, not off. **`true` does not mean the model answers**: nothing in `list_models` calls the model, so credits and quota are never visible here |

**Slot names** (pass one as `forSlot`), as the tenant uses them:

| Use | Slot name(s) |
|---|---|
| An agent's main model / an automation LLM node | `TEXT_GENERATION` |
| Knowledge answers | `Answer Generation`, `Query Rephrasal` |
| Knowledge indexing | `chunking`, `metadata enrichment`; embedding: **`EMBEDDING` or `embeddingModel`** — both names exist on the tenant, so query **both** and merge |
| Reranking | `ranking model` |
| Guardrails | `hallucination`, `denied topics`, `content filter` |
| Images, documents, code, web, audio | `IMAGE_PROCESSING`, `TEXT_EXTRACTION`, `CODE_GENERATION`, `WEB_SEARCH`, `AUDIO_PROCESSING`, `REALTIME_AUDIO` |

Read the slot a step needs from the thing that uses it (the agent's slots in `get_agent`, the knowledge set's model
fields in `get_knowledge_sets`, the node's model input in the workflow); never assume one from a generic word.

### The model test (one real call per card)

`list_models` never calls the model, so a card can show `connectionActive: true` and still fail every run (checked on
Orbit UAT, 3 Nov 2026: an Anthropic Claude Sonnet 5 card listed as active failed every call, while a Vertex card for
the same model answered). The only proof is one real call. Two platform steps take a model card directly and can be
run on their own with `run_connector_operation` (no `connectionId`, nothing created on the tenant):

**Chat cards** (`TEXT_GENERATION`, `Answer Generation`, `Query Rephrasal`, `chunking`, guardrail slots, any card an
agent or LLM node uses):

```json
{ "appName": "conv_ai_by_unifyapps",
  "resourceName": "conv_ai_by_unifyapps_call_llm_model_with_options",
  "inputs": { "callableInterfaceId": "__ua__call_ai_agent_llm_model",
              "parameters": { "modelId": "<card id>",
                              "message": [ { "role": "user", "content": [ { "type": "text", "text": "Reply with the single word ok" } ] } ],
                              "maxTokens": 20 } } }
```

Pass: `ok: true`, `result.success: true`, a non-empty `result.llmResponse`. Record `tokensUsed` and the cost
(`inputTokenCost` + `outputTokenCost`, about $0.0001). Keep the input exactly this shape: extra options
(`temperature`, `systemPrompt`, a tiny `maxTokens`) are not needed for the test.

**Embedding cards** (`EMBEDDING`, `embeddingModel`):

```json
{ "appName": "conv_ai_by_unifyapps",
  "resourceName": "conv_ai_by_unifyapps_fetch_embeddings",
  "inputs": { "callableInterfaceId": "__ua__generic_fetch_embedding",
              "defaultFallbackWorkflowId": "<the operation schema's default>",
              "parameters": { "modelId": "<card id>", "text_batch": [ "ping" ] } } }
```

Read `defaultFallbackWorkflowId` from `get_operation_schema` each run (on Orbit UAT, 3 Nov 2026:
`69748b47f9421a440d992ec4`). Pass: `ok: true`, `result.embedding_batch[0].embeddings` is a non-empty list, and
**`result.usedModelId` equals the card tested** (a different id means the platform fell back to another model, so the
card itself was not proved). Record the vector length: a fallback for a knowledge set should give the same length.

**Results:**

| Outcome | Health | What it means |
|---|---|---|
| Pass | `healthy` (with the time) | The card answered just now |
| `ok: false` with a quota, credits or billing message | `exhausted` | Go to model recovery for any step that uses it |
| `ok: false` with any other error (often HTTP 500 "Workflow execution failed", which gives no reason) | `failing` | Do not use the card; the cause cannot be told from this error, so do not call it "out of credits" |
| A slot with no test step (`ranking model`, `IMAGE_PROCESSING`, `AUDIO_PROCESSING`, `REALTIME_AUDIO`, `WEB_SEARCH`) | `unknown` | Proved only by the build's first real run of that slot |

Rules: one test per card per run (the retry ceiling allows one retry with the same input only to rule out a blip);
the text sent is always the fixed test text, never client data; the test is a read (no records, no side effects), and
its cost is too small to need the person's yes, but write each test in `context-log.md`.

### Model inventory (`scope: models`; also part of `scope: verify` before the build)

1. **Slots the build needs**, from the BRD and the build plan when they exist; at stage 1c (before Scoping), from the
   approved requirements: each AI capability the use case needs (an agent or an LLM step → `TEXT_GENERATION`;
   documents to search → `EMBEDDING`/`embeddingModel` and `Answer Generation`; images or scans → `IMAGE_PROCESSING`
   or `TEXT_EXTRACTION`; …), each row marked `from requirements`. Then: each agent's slots, each automation LLM or AI node, each
   knowledge set (embedding, chunking, answer, reranker if used), any image, document, audio or web step. One row per
   slot: `slot_id`, the tenant slot name (table above), where it is used, the card the BRD names.
2. **Candidate cards:** `list_models` with `forSlot` (for embedding, both `EMBEDDING` and `embeddingModel`). Keep
   cards with `connectionFound` and `connectionActive` both `true`, a `provider`, and — for an agent with tools —
   `canCallTools: true`. Prefer cards whose `model` matches what the BRD names.
3. **Health: run the model test** on the primary and the fallback card of every chat and embedding slot (and on the
   next candidate when one fails). Only a passed test makes a card `healthy`; never from `list_models`. A card that
   is `failing` or `exhausted` is not chosen. Slots with no test step stay `unknown` until the build's first real run.
4. **Choose for each slot:** a primary card and a fallback with a **different `provider`** (the closest you can get to
   a different account; say so). Embedding: the fallback should produce the same kind of vectors where possible
   (same `model`, e.g. `text-embedding-3-large` on `azure_openai` for `openai`); either way a switch re-indexes the
   whole knowledge set.
5. **Write the result where it is used:**
   - the spec (`models[]`, the "AI models" line of the build block);
   - **the BRD**: if Scoping has not run yet, the spec's model rows are its input (§13 agents' model, §17 AI trust, the
     assumption list). If the BRD already exists and names a different card id, a missing card, or a card that fails
     step 2, list each difference (slot · BRD card · proposed card · reason) and ask the person to choose (the model
     recovery question, step 4 of "Model recovery"); then update the BRD before the build as described in "A model
     change in the BRD" below. A BRD never goes to the build with a card id
     that the inventory rejected.
   - Run the model test again in `scope: verify` just before the build (credits can run out between Scoping and the
     build). After the first real run of an untested slot, set its `health`; if the run failed, go to model recovery.

### Model recovery (`mode: model-recovery`, any time a model runs out)

**Recognise it.** The run, trace or index error says the model's provider refused for money or quota, for example:
`insufficient_quota`, `exceeded your current quota`, `credit balance is too low`, `billing`, `payment required`
(402), `RESOURCE_EXHAUSTED`, `quota exceeded`, `limit reached for this month`, or 429 with a quota or billing message.
A plain **rate limit** (429 "too many requests", "retry after") is not exhausted credits: wait and retry the step up to
twice first; only if it persists is it treated as exhausted. Auth errors (401, invalid key) are a connection problem:
tell the person to fix the provider connection; they are not a model switch.

**Then, in order:**

1. **Stop the failing step**, not the whole run: no more items go to the exhausted model (e.g. stop adding documents
   to the index). Note what already succeeded so it is not redone.
2. **Find every place the exhausted model is used** (Tools: agents' slots, knowledge sets, automation nodes), and
   every other card on the **same provider connection** — they are likely exhausted too.
3. **List the alternatives** for the same tenant slot (both embedding slot names for an embedding step):
   `list_models` `forSlot`, `connectionFound` and `connectionActive` both `true`, a **different `provider`** from the
   exhausted card (cards with no provider are left out), and `canCallTools: true` for an agent with tools. Put the
   inventory's fallback first. **Run the model test on each candidate** and offer only cards that pass (at most
   three); for a slot with no test step, say "unknown — the re-run checks it". If the re-run in step 6 still fails,
   come back here with that card removed. Nothing passes → say so.
4. **Ask the person** (one question; they choose, in Zen and Sonic):

   `SYSTEM_ACCESS: The <kind> model "<card>" (<provider>) ran out of credits or quota while <step, e.g. "indexing 7
   knowledge documents for AG-02">. These models still work for this step. Which should I switch to?`

   | Option | Description |
   |---|---|
   | `<card A name>` (Recommended) | `<provider> · <model> · id <card id> · health <healthy (model test <time>) / unknown — the re-run checks it> · <what changes: "re-indexes 7 documents, about N min" or "re-runs only the failed step">` |
   | `<card B>` | same shape |
   | `<card C>` | same shape (at most three cards) |
   | Add credits to `<provider>` and retry | The person tops up the account; I retry the failed step only (this is spend: their action, never mine) |

   No healthy alternative → only the last option, plus "Stop here and keep the step as failed".
5. **Hand the switch to UnifyApps Headless** (`ua-change`, a direct change): "Switch <slot(s)> from <old card> to
   <chosen card>: <agent ids / knowledge set ids / automation node>. Same model in every slot of the agent. Do not
   change anything else." Embedding: the knowledge set's embedding model changes and **all** its sources are
   re-indexed — index one document first, check its status, then the rest.
6. **Re-run only what failed** (the node, the agent test, the unindexed documents) and check it worked (run status,
   trace, `check_knowledge_status` = indexed for every source).
7. **Record it:** the spec's `models[]` (old → new, reason, time, who chose), `context-log.md` as a human decision,
   and, in POC Studio, `lessons.py capture <workspace> build "<provider> credits ran out during <step>; switched to
   <card>"`. **Update the BRD**
   wherever it names the old card id (§13, §17, assumptions), as described in "A model change in the BRD" below, so a
   rebuild does not bring the exhausted card back.

### A model change in the BRD

The person already chose the model, so this is not a change request: no clarity check, no review round and no gate.
Write the new card id wherever the BRD names the old one (§13, §17, assumptions), add one Document Control row
("Model switch: <slot> <old card> → <new card>, <reason>, chosen by the person, <date>"), and save it as a new BRD
version (POC Studio: orbit-writeback "A BRD version after a model switch"). Nothing else in the BRD changes.

**Never** in model recovery: buy credits or change a plan or limit; switch without the person's choice; switch an
embedding model on a set without re-indexing it; retry an exhausted model in a loop; change a model the failure did
not touch.

## Output format (`integration-spec.json`)

```json
{
  "schema_version": "1.0",
  "client": "Acme", "use_case": "Opportunity Plan", "generated_at": "2026-11-03T18:14:00+05:30",
  "tenant": "orbit.uat.unifyapps.com",
  "systems": [ {
    "system": "Salesforce", "app_name": "salesforce", "environment": "sandbox",
    "status": "done",
    "connection": { "id": "<connection id>", "name": "Salesforce Connection - Acme sandbox", "source": "user_given",
                    "active": true, "validated": true, "user": "integration.user@…", "user_profile": "System Administrator" },
    "schema_strategy": "metadata_query",
    "needs": [
      { "need_id": "N-01", "kind": "event", "object": "Opportunity", "fields": ["StageName"],
        "condition": "StageName = 'Proposal Accepted'", "purpose": "start the plan",
        "requirement": "plan ready when the proposal is accepted (client email)", "timing": "real time",
        "operation": "N-01-op", "result": "ready", "detail": "7 records already at this stage" }
    ],
    "objects": [ { "api_name": "Opportunity", "label": "Opportunity", "record_count": 22,
                   "fields": [ { "api_name": "StageName", "type": "picklist", "values": ["…"] } ],
                   "rights": { "create": "yes (permission)", "update": "yes (permission)" } } ],
    "configuration": [ { "item": "plan questions", "object": "Plan_Question__c", "count": 30,
                         "per_parent": { "parents_total": 10, "parents_with_records": 10 }, "records": [ ] } ],
    "operations": [
      { "op_id": "N-01-op", "need_id": "N-01", "type": "trigger", "name": "<trigger operation name>",
        "mode": "real time", "inputs": { "object": "Opportunity", "fields": ["StageName"] },
        "prerequisite": "Opportunity enabled for Change Data Capture", "prerequisite_status": "unknown",
        "fallback": "<polling trigger name>, every 5 minutes", "test": "ready",
        "connection_id": "<connection id>" },
      { "op_id": "N-14-op", "need_id": "N-14", "type": "action", "name": "salesforce_create_record_batch",
        "inputs": { "objectId": "Plan_Answer__c", "allOrNone": false }, "test": "ready (permission) — not run",
        "connection_id": "<connection id>" }
    ],
    "automations": [
      { "id": "AU-01", "name": "Proposal accepted → prepare plan", "requirement": "plan ready when the proposal is accepted",
        "trigger": "N-01-op", "steps": [ { "n": 1, "kind": "connector", "op_id": "N-03-op", "op": "<query operation>",
          "connection_id": "<connection id>",
          "inputs": { "query": "SELECT … FROM Opportunity WHERE Id = :trigger.Id" }, "outputs": ["Opportunity row"] } ],
        "idempotency": "one plan per Opportunity.Id", "conflict_rule": null,
        "errors": "UNABLE_TO_LOCK_ROW retried twice after 5 s; others stop and notify the owner",
        "human_gate": "none (draft only)", "status": "Live with assumption",
        "test_plan": "move a sandbox opportunity to Proposal Accepted; expect one plan within 3 minutes" }
    ],
    "field_mapping": [ { "client": "Opportunity.StageName", "type": "picklist", "direction": "in",
                         "app": "op_opportunity.stage", "transform": "as is" } ],
    "limits": { "query_limits": ["no parent-child subqueries"], "api_calls_per_run": 15 },
    "assumed": [ { "item": "Change Data Capture on Opportunity", "why": "not readable", "confirm": "Setup → Change Data Capture", "impact": "use polling" } ],
    "errors": [],
    "checks": { "C1": "pass", "C2": "pass", "C3": "pass", "C4": "pass", "C5": "pass", "C6": "pass" }
  } ],
  "models": [
    { "slot_id": "M-01", "slot": "EMBEDDING", "used_by": ["knowledge set KS-01 (AG-02)"], "brd_card": "e_…",
      "primary": { "card": "e_6a9ec98b0dfd8d53e7f58394", "name": "Text-Embedding-3-Large", "model": "text-embedding-3-large",
                   "provider": "openai", "connectionFound": true, "connectionActive": true, "health": "healthy",
                   "test": { "at": "2026-11-03T16:40:00Z", "operation": "conv_ai_by_unifyapps_fetch_embeddings", "usedModelId": "e_6a9ec98b0dfd8d53e7f58394", "vector_length": 3072 } },
      "fallback": { "card": "e_6918e83442f9146811ffef43", "name": "text-embedding-3-large - azure openai", "model": "text-embedding-3-large",
                    "provider": "azure_openai", "connectionFound": true, "connectionActive": true, "health": "unknown" },
      "brd_updated": "BRD v3 §13, §17 (model switch, no re-approval)",
      "switches": [ { "at": "2026-11-03T13:20:00Z", "from": "<card>", "to": "<card>", "reason": "insufficient_quota while indexing 7 documents",
                      "chosen_by": "person", "rerun": "re-indexed 7 documents; all indexed" } ] }
  ]
}
```

Statuses: need and operation results `proved` · `ready` · `flags_only` · `blocked` · `failed` · `not_testable` ·
`gap`; automation status `Live` · `Live with assumption` · `Planned`; system status `done` · `partial` · `assumed` ·
`failed` · `not_needed`.

## Failure handling

| What happens | Do this |
|---|---|
| UnifyApps Headless not set up or signed out | Ask the person to run `/ua:setup` and sign in; continue from the last step |
| Connection inactive or auth error | Ask the person to re-authorise it; try once more; still failing → system `failed` |
| A query is refused | Simplify it (Rule 8) at most twice; record the limit |
| No describe or query operation | Strategy C; the rest is [Assumed] |
| No operation fits a need | `gap` with the workaround; [Assumed]; a Decision for Scoping |
| A write operation appears in a test | Stop before running it and log it (Rule 3) |
| A step fails on credits or quota (any model) | Part B, Model recovery: stop the step, find healthy alternatives, the person chooses, UnifyApps Headless switches, re-run only the failed step |
| A model test fails (`failing` or `exhausted`) | Do not choose that card; test the next candidate; `exhausted` on a card already in use → model recovery |
| A rate limit, not exhausted credits | Wait and retry the step up to twice; persistent → treat as exhausted |
| The person does not answer (Sonic) | System `assumed`, reason "no connection answer"; the AI PM shows it at the Scoping gate |

## Never

- Write to the client system, except one approved sandbox write test; delete anything; fire or register a trigger.
- Create a workflow, object, data source or connection on the tenant.
- Read or print a connection's secrets, or list connections unfiltered.
- Answer an access question for the person, or let the AI PM answer it.
- Name an object, field, value or operation in the spec that was not read in this run (it goes to Assumed instead).
- Freeze an operation version for the build without `scope: verify`.
- Switch a model, buy credits or raise a quota for the person; call a model "healthy" without a real call.
