# Plan review checklist — reviewing the Zen build plan before the person sees it

This file is what `platform-master` reviews UnifyApps Headless's Zen build plan against. The plan is a spec (objects,
pages, workflows/automations, AI agents, data sources, seed data) plus a task graph (one task per entity, each owned
by one builder agent, with waits-on edges). Every item below is a platform lesson: something that, if the plan gets it
wrong, either fails loudly late or — far more often — answers HTTP 200 and quietly does nothing. Evidence markers are
kept where known: ✅ verified on the platform · 👁 observed, not re-run · ⚠️ partial · ⛔ does not work.

## How to use it

1. Read the plan's spec end to end, then the task graph. List every entity: objects, seed sets, workflows, agents
   (with their tasks and tools), data sources, connections, pages.
2. Walk sections 1–6 below in order. Each item is a **Check** (what to look for in the plan) and a **Fix** (what the
   plan should say instead). Skip items that do not apply to this plan's shape.
3. Write each finding as one line, in this exact form, and send the set back through Zen:

   ```
   <entity>: <change> — <why>
   ```

   Examples:
   - `ord_case (object): add custom index {status:1, due_at:1} — the queue page filters on status and sorts on due_at; only the key is indexed automatically`
   - `Case Assistant (agent): move the "end the turn with the answer" rule into every task's instructions — task instructions dominate; the agent prompt alone does not hold`
   - `task graph: make "tool: QueryCases" wait on "wf_query_cases" — a tool pointing at an undeployed workflow fails silently`

4. One finding per line, one change per finding. Name the entity exactly as the plan names it. Say why in platform
   terms (what breaks), not in terms of preference. If the plan is already right on an item, say nothing about it.
5. End with the "Top 15 checks" (section 7) as a final pass; any miss there is always worth a line.

---

## 1. Data objects and seed data

### Schema

- **Check:** every object declares a primary key field. **Fix:** name one field `primaryKey: true` (a business code
  such as `case_code`), or an auto-number field (`format: "auto-generate"` with a prefix and start). The record `id`
  is the primary-key value, so a duplicate key fails with a duplicate-key error rather than creating a second row ✅.
- **Check:** `required` lists the fields every write must carry, and nothing a later step fills in. **Fix:** keep
  `required` to the key and the fields present at creation; a field set later by an AI step or an approval must not
  be required, or the create fails with `Non Empty Validations … required <field>` ✅.
- **Check:** statuses and other fixed vocabularies are single-select fields with a static `oneOf` list (`const` +
  `title`), and the plan's workflows, seed and agent instructions use exactly those `const` values. **Fix:** align
  every writer to the `oneOf` consts; a value outside the list fails `property <field> invalid; oneOf fail` ✅.
  Changing an enum later is a four-part change (schema const, its title, every existing record, every writer) — get
  it right in the plan.
- **Check:** the schema has `additionalProperties: false` and the writers send only declared fields. **Fix:** remove
  undeclared keys from writers, or add them to the schema; an unknown key fails `add additionalProperties <key>` ✅.
- **Check:** links between objects are lookup fields (`foreignKey: {reference: "ENTITY_ID:<target>"}`). **Fix:** store
  the target record's id; foreign keys are checked only when enforced and **nothing cascades**, so the plan must not
  assume a cascade.
- **Check:** dates. **Fix:** use `integer` with `format: "date-time"`, `dateFormat: "epoch"` (epoch ms) consistently
  across objects, workflows and seed.
- **Check:** a count the screens or agent need is derivable without a join across two objects. **Fix:** denormalise
  the flag onto the row that gets counted (e.g. `is_material` on a link object). A count that needs a join is where
  an agent invents numbers.
- **Check:** soft retirement. **Fix:** any object whose rows can be withdrawn, superseded or reset carries an
  `active` / `archived` / status flag, and reads filter on it. Rows are never removed.
- **Check:** one current AI reading per record. **Fix:** an AI result object is keyed by the record it describes and
  written by upsert, so a re-run replaces the reading; history goes to an evidence-log object (section 2, "LLM and OCR steps"). A build
  that created a new row per run ended with 167 estimates for 121 requests and dashboards that did not reconcile.
- **Check:** an AI-usage / evidence-log object exists when the plan has any LLM or OCR step. **Fix:** add
  `<prefix>_evidence` with `workflow_id`, `workflow_name`, `step_name`, `source`, `unit_type`, `unit_ref`,
  `record_ref`, `model_id`, `tokens_in`, `tokens_out`, `cost_in`, `cost_out`, `cost`, `success`, `created_at`; its key
  auto-generated or `<wf>-<step>-<created_at>`.

### Record writes — read-merge-write, never partial

- 🔴 **Check:** any write that changes some fields of an existing record (a status change, an AI reading, an approval)
  goes through a create/update binding or storage node with `useRawPayload: true`. **Fix:** the writer must
  read the record, spread its properties, apply the change and write the whole record back. `useRawPayload` is a
  **replace**, not a merge: a partial payload returns 200 and deletes every field it left out ✅ (one build lost all
  but five fields on 415 records). The schema's `required` error on a partial write is the platform warning you it is
  a replace — adding the missing key to the payload is the wrong fix.
- **Check:** field-level partial updates. **Fix:** use `storage_by_unifyapps_update_records` (`updateFields:
  [{fieldName, actionType: "SET", setValue}]`, with an `id` EQUAL condition) or `bulk_upsert_records_by_id` with
  `updates: [{id, updateFields: [...]}]`. Those are genuine partial updates.
- ⛔ **Check:** a bulk upsert whose `updates` carry `{id, properties: {...}}`. **Fix:** use `updateFields`. The
  `properties` shape returns 200, the workflow reports the count it built, and **nothing is written** ✅.
- **Check:** `bulk_upsert_records_by_id` with an id that may be blank. **Fix:** it inserts a new row; use
  `update_records` with an `id` EQUAL condition instead.
- **Check:** `skipIfBlank: true` on a field the flow may legitimately clear. **Fix:** set `skipIfBlank: false` and
  `unsetIfNull` deliberately, or the clear never lands.
- **Check:** entity-API updates (`POST /api/entity/update`, `/api/entity-type/update`). **Fix:** send the **full**
  record / full object; these replace `properties` / schema wholesale.
- **Check:** every bulk write is followed by a read-back. **Fix:** after the first record, read it back and compare
  its field count with the snapshot; a 2xx proves the call was accepted, never that the record is whole.

### Seed data (dummy by design)

- **Check:** seed rows carry every required field and only declared fields, with enum values from the `oneOf` lists.
  **Fix:** generate from the schema, not from memory.
- **Check:** dependent attributes are drawn from their parent. **Fix:** key each generated list by the parent's
  category (faults by equipment type, line items by product family). Independent draws produce rows like a lift fault
  on a pump, and the agent will quote them.
- **Check:** volume carries foreign keys. **Fix:** transactional rows filed against every dimension they name, so
  filters and drill-downs are real. Volume without keys is decoration.
- **Check:** time series. **Fix:** anchor history on the value the current record holds and extend backwards, so the
  last point of every chart equals the figure on the tile. Guard charts that need ≥ 3 periods.
- **Check:** derived numbers in seed (totals on a parent, counts in a KPI object). **Fix:** compute them from the base
  rows (or by a rollup workflow), never type them, so the two cannot disagree.
- **Check:** seed loads at the volume the scoping document's seed plan (§19) sets. **Fix:** large sets go through a
  bulk-create workflow (1,000–1,500 rows per call) rather than many single creates. Idempotent reload: create → on duplicate key, read the version →
  update with the full body.
- **Check:** seed text names the client business correctly and no incumbent product. **Fix:** neutral wording; no
  other vendor's product names in enum values, record codes, prose, prompts or instructions (a product name once
  reached eight places, including a primary key).

### Indexes

- **Check:** every object a page, data source or workflow filters or sorts on, beyond its key. **Fix:** add compound
  `metadata.customIndexDefinitions` from the real query shapes, fields in **equality → sort → range/IN** order (e.g.
  `{status:1, due_at:1}`). Only primary and unique keys are indexed automatically; `filterable` / `sortable` /
  `searchable` flags create **no** index ✅.
- **Check:** index count and names. **Fix:** at most 5 custom indexes per object, names without spaces
  (`index_1…5`); the array replaces the previous one, so the plan writes the full list each time. Each index must
  reach status `SUCCESS` (re-read until it does).
- **Check:** over-indexing. **Fix:** do not index what the key covers; small bounded reference tables need none; a
  foreign-key field that pages filter on always gets one.
- **Check:** code that depends on tie order. **Fix:** add a second sort field; rows with equal sort values may come
  back in a different order after indexing.

### What breaks (data layer)

| Check | Fix |
|---|---|
| Entity list filter written `{op:"AND", filters:[…]}` | `{op:"AND", values:[leaf, leaf]}` — the `filters` form is silently ignored and returns everything ✅ |
| Filter shapes copied between surfaces | Entity API: `{op, field:"properties.x", values}`; aggregation: field `properties_x`; storage node / data sources: `{operator, filters:[{property, filter:{operator, value}}]}`. The wrong shape is often accepted and ignored |
| A total over a set that can exceed a page computed by summing a read | compute it server-side (`count_records`, SQL-on-list) — one screen read 1,000 of 1,113 rows and showed a plausible wrong total |
| Record aggregation used for group-by | ⛔ aggregation on records returns one row per record; group in a workflow (fetch → SQL-on-list) |

---

## 2. Workflows / automations

### Shape

- 🔴 **Check:** native nodes first; a Code node only for a computation no native node covers. **Fix:** replace Code
  that does any of these with the native node ✅ (audited builds ran 46–48 % Code nodes in the worst cases):

  | Job | Native node |
  |---|---|
  | filter records | `storage_by_unifyapps_fetch_records` with `triggerInputCondition` on `properties.<field>`, `properties_<field>` or `id` ✅ |
  | count records | `storage_by_unifyapps_count_records` → `outputs.count` ✅ |
  | group / sum / avg / join / rank a list | `utility_by_unifyapps_run_sql_query_on_list` (`dataSources: ["{{ n_f.outputs.objects }}"]`, and the same pill is the table name in the SQL); output `outputs.result` ✅ |
  | sort a list | `utility_by_unifyapps_sort_list` → `outputs.sortedList` ✅ |
  | parse a JSON string (LLM reply, HTTP body) | `utility_by_unifyapps_to_json_object` → `outputs.result` ✅ |
  | object → text a model reads | `utility_by_unifyapps_to_json_string` (an object inside a template renders as `{a=1}`) |
  | build the response | the STOP node's `result` map of templates ✅ |
  | branch | `IF_ELSE` ✅ |
  | iterate | `LOOP` (`loop_for_each` / `loop_while`) ✅ |
  | counters, flags, small arithmetic | `variable_by_unifyapps_create_variables` / `update_variables` with `=SUM(…)`, `=LEN(…)`, `=IF(…)` ✅ |
  | call another workflow | `CALL_WORKFLOW` (`callables_call_automation`) — never inline its logic ✅ |
  | update every record matching a condition | `storage_by_unifyapps_update_records` (`numberOfRecordsToUpdate: "MULTIPLE"`) |
  | rule tables, template text, date maths, distinct values, ids | decision table, template compile/resolver, `date_diff` / `epoch_to_date`, `fetch_distinct_values`, `generate_uuid` 👁 |
  | call a service no connector covers | `custom_http_endpoint_execute` — needs no connection ✅ |

- **Check:** a Code node that remains. **Fix:** one job per node, titled with that job and why native cannot do it,
  ideally under 40 lines (over 60 needs a stated reason). Never a Code node that only flattens rows, renames fields,
  builds a filter, assembles the STOP payload or joins two branches. Code nodes ≥ native nodes in a workflow is a
  redesign.
- ⛔ **Check:** `storage_by_unifyapps_aggregate_records` or `utility_by_unifyapps_filter_list`. **Fix:** replace —
  the first returns one row per record with the raw value under every alias (plausible wrong totals); the second
  returned 0 of 20 matching rows. Group with fetch → SQL-on-list; filter in the fetch or the SQL `WHERE`.
- **Check:** one orchestration per human action. **Fix:** each button a person presses (submit, approve, reassign)
  maps to one callable workflow that does the whole action; a shared read or calculation is its own callable
  workflow called with `CALL_WORKFLOW`, not copied.
- **Check:** a deterministic verdict (a rule, a lookup, a calculation, a threshold) assigned to an LLM step. **Fix:**
  make it a workflow step or an HTTP call to the service that owns it; the model reads, compares and explains.

### Triggers

- **Check:** every START node has a `trigger`. **Fix:** `CALLABLE` for anything an agent tool, a data source or another
  workflow calls; `SCHEDULED` for timed jobs; `EVENT` for connector events; `WEBHOOK` for inbound calls. A START without
  a trigger makes the save fail (`Node.getTrigger() is null`) **after** the create has already succeeded — the fix is
  to repair that workflow, not to create a second one.
- **Check:** scheduled triggers. **Fix:** `inputs.cron: "INTERVAL"` with `interval` and `frequency` (`MINUTES` |
  `HOURS` | `DAYS`) — only `INTERVAL` saves ✅ (`CRON`, `CUSTOM` are rejected). For "weekdays at 07:00", run on an
  interval and let the first node skip runs outside the window.
- **Check:** callable input schema. **Fix:** a JSON Schema in the START node's `inputs.setup` with typed properties
  and a non-empty `required` list. It is the agent tool's argument contract and the data source's input set; an empty
  `required` lets the model omit parameters and the write lands NULL columns with no error.

### Templates and outputs

- **Check:** templates are `{{ n_<nodeId>.outputs.<path> }}` with spaces inside the braces, and every referenced node
  id exists **in this workflow**. **Fix:** rewrite templates copied from another workflow; an unresolved template
  silently drops the key — no error, no violation.
- **Check:** fetch output path. **Fix:** a fetch's collection is `{{ n.outputs.objects }}` and its count
  `{{ n.outputs.total }}`; `outputs.records` and `totalCount` resolve to nothing and the workflow returns zero of
  everything ✅.
- **Check:** a fetch without `triggerInputCondition`. **Fix:** send `triggerInputCondition: {}` to read everything;
  omitted, the node returns nothing ✅. Page with `{paginateBy: "OFFSET", limit: 2000, offset: 0}`.
- **Check:** Code node outputs. **Fix:** read as `{{ n_code.outputs.result.<field> }}`; null map values vanish from
  the output, so downstream treats absent keys as null.
- **Check:** SQL-on-list over a list that can be empty. **Fix:** guard it (an IF_ELSE on the count); it fails on an
  empty list.

### SQL nodes (database connectors)

- 🔴 **Check:** every `:bind` in `inputs.sql` has both a `params` schema entry and a `record` value. **Fix:** declare
  each bind in `params` (name + type) and supply it in `record` as a template. Missing `record` entirely →
  `ORA-17041 Missing IN or OUT parameter`; **missing one key in `record` binds NULL silently** and the run is green ✅.
  Diff the binds in the SQL against the keys in `record`.
- **Check:** `record` templates point at **this** workflow's START node. **Fix:** rewrite them after copying a node;
  a foreign node id resolves to nothing and gives ORA-17041 while SQL and `params` look perfect.
- **Check:** each SQL node's `params`/`record` contain only the binds its own SQL uses. **Fix:** no shared bind sets
  copied between nodes; use each bind name once (assign it to a PL/SQL local and reuse the local).
- 🔴 **Check:** PL/SQL OUT binds (`:o_*`). **Fix:** OUT binds stay **out** of `record` (feeding them an input corrupts
  the call), and they are **never returned** — an anonymous block returns `{"rows":[],"rowsCount":0}` whatever it
  assigns ✅. Every PL/SQL write is followed by a verification SELECT node, and STOP maps that node:
  `START → PL/SQL write → SELECT the resulting row → STOP`. For a create, order the SELECT by the new id descending.
- 🔴 **Check:** a colon inside a single-quoted SQL literal (`'HH24:MI'`, `'09:00'`). **Fix:** the connector treats
  any `:word` as a bind, even inside quotes → `ORA-17003 Invalid column index` ✅. Escape it (`'HH24":"MI'`) or build
  it (`'09'||CHR(58)||'00'`).
- **Check:** `objectSourceResourceName: "oracledb_execute_sql_metadata"` and a `response_schema` matching the
  SELECT's columns. **Fix:** add both; they are what make typed `rows` come back.
- **Check:** business-rule refusals. **Fix:** `RAISE_APPLICATION_ERROR(-20100..-20999, 'plain sentence')`; it
  surfaces inside the failure payload (`output.cause.cause.payload.message`), and the caller shows the first
  non-`ORA-06512` line. Catching `WHEN OTHERS` to return an `:o_error` does not work (OUT binds never return).
  Validate known rules before the call.
- **Check:** `connectionId` placement. **Fix:** inside `context`, never at node level or in `inputs`.

### Writes, verification and the response

- 🔴 **Check:** every write is verified by a read. **Fix:** a read-back node (fetch / SELECT) after the write, and the
  STOP returns what was read, not what was sent. `COMPLETED` only means no node threw ✅.
- **Check:** the verification step is simple. **Fix:** keep it boring. The write commits before the verify node runs;
  if verify fails the run is FAILED and the agent says "could not be created" while the row exists, and the retry
  makes a duplicate ✅.
- **Check:** the STOP `result`. **Fix:** an object (a JSON array fails only at run time), carrying the business
  outcome plus `successCount` (or equivalent) for writes, and `usage_logged` / the AI node's `success` when there is
  an AI step, so a test can assert them.
- **Check:** caller identity. **Fix:** never trust a "who am I" parameter the page or chat sends. Derive the caller
  server-side: create the record (or a scratch row) and read `outputs.ownerUserId`, then map it to a profile row.
  For agents, one `whoami` tool maps the signed-in username to the back-end ids.
- **Check:** guards before writes. **Fix:** `throw new IllegalArgumentException('…')` in a Code node fails the callable
  cleanly; the caller sees `rootCauseMessage` (errorCode 5005). Use it for ownership / whitelist checks before any
  storage write.

### Branching, loops and errors

- **Check:** IF_ELSE wiring. **Fix:** `if` edge (`name: "yes"`) into the true branch, `next` edge (`name: "no"`) to
  the rejoin node, and the true branch's last node also points at the rejoin node.
- 🔴 **Check:** loop bodies sit in the loop's child group (`<loopId>@<parentGroup>@l`). **Fix:** save and deploy
  accept a body left in the parent group, and then the run never ends: the loopback replays the first item forever ✅
  (one run replayed a child workflow 2,163 times in 35 minutes). Wiring: `loop` edge in, `next` edge with
  `name: "loopback"` back, `next` edge out.
- **Check:** a BREAK node. **Fix:** it still needs an outgoing `next` edge to the same rejoin node as the enclosing
  condition's `no` branch, or validation fails.
- **Check:** error handling. **Fix:** an `error` edge fires only with `fallbackMode: "MANUAL"` on the node; with `STOP`
  the run fails and the handler never runs. ⛔ Do not rely on `fallbackMode: "CONTINUE"` (or `IGNORE`, `SKIP`, …) to
  keep a run going — it does not.
- **Check:** root `groupId` is the same on every top-level node. **Fix:** mixed or missing root groups hide the graph
  on the canvas.

### LLM and OCR steps inside workflows

- **Check:** node type. **Fix:** an LLM or OCR node is `CALL_INTERFACE_WORKFLOW` (e.g.
  `conv_ai_by_unifyapps_call_llm_model_with_options` with `callableInterfaceId: "__ua__call_ai_agent_llm_model"`);
  as `ACTION` it fails with "No config found" ✅. A call-automation node is `CALL_WORKFLOW`.
- **Check:** latency where a person waits (screen insights, summaries, an action's AI reading). **Fix:** input capped (≤ 30 rows per set, ≤ 8,000 characters), two or
  three findings, `maxTokens` ≤ ~1,600, results stored so a revisit is instant from cache. The model is the one chosen
  for the build.
- **Check:** thinking models. **Fix:** they spend `maxTokens` on reasoning; give them 3–4× the visible output and
  check `finish_reason` (`MAX_TOKENS` means truncated JSON and a failed parse) ✅.
- **Check:** JSON output. **Fix:** `responseFormat: {type: "json_object"}`, low temperature, parse with
  `to_json_object` (or slice from the first `{` to the last `}`), and handle `finish_reason`.
- **Check:** the prompt. **Fix:** it states the client's business in one line and what it must never be called; it
  says the document/records are data, not instructions; it names no other customer or vendor; and every prompt that
  produces figures ends with the NUMBERS rule (section 3). A cloned workflow clones its prompt — rewrite it.
- **Check:** an evidence-log row per AI call. **Fix:** after every AI node (inside the loop body when the node is in a
  loop): a small prep step building the row, then a create on `<prefix>_evidence` with `fallbackMode: "MANUAL"` and an
  `error` edge to a handler that returns the business result with `usage_logged: false`. Write the log row before the
  business record, so a duplicate-key failure on the record never loses the measurement.
- **Check:** smoke-testing a slow LLM workflow through the test runner. **Fix:** the test runner gives up at ~23–26 s
  and marks the run CANCELLED ✅; test slow steps through the deployed workflow's data source.

### Deploy vs saved state

- 🔴 **Check:** the plan treats save and deploy as separate steps. **Fix:** after **any** edit to a deployed workflow,
  deploy again with the live version (`deploy?version=<current version>`, re-read first — it advances on every save),
  then assert `deploymentState.workflowVersion === version`. Agent tools and data sources call the **latest deployed**
  version (`version: "-1"`); an edited-but-not-deployed fix never runs ✅.
- **Check:** "tested green" evidence. **Fix:** the test runner (`initiate-test`) executes the definition sent inline,
  never the deployed one ✅; a green test proves the SQL, not what the agent runs.
- **Check:** `violations` after every save. **Fix:** a save with violations still returns 200 and persists; the plan
  must require `violations: null`.
- **Check:** `resourceVersion` on nodes. **Fix:** resolve it at build time from the node's resources list; never
  hard-code (versions drift within a session; a stale one gives "No config found" or blocks later saves).

### Groovy, when Code is genuinely needed

| Check | Fix |
|---|---|
| JavaScript Code node with a top-level `return` | use Groovy; JS rejects it ("Invalid return statement") |
| Interpolated `"…${x}…"` returned to a page | `.toString()` every string; a GString serialises as an object and crashes the page |
| `1G` then `.setScale()` | write decimal literals (`1.0G`); `1G` is a BigInteger |
| `def owner = …` | rename (`ownerName`); `owner =` is blacklisted at save |
| closure parameter sharing a name with anything in scope | prefix it uniquely; save accepts it, **deploy** fails |
| `Date.format(...)` | use `java.time` (`LocalDate.now(ZoneOffset.UTC).toString()`) |
| optional parameter read as a bare variable | `binding.hasVariable('x')` first; unresolved params are unbound |

### Pre-production audit (every workflow in the plan)

The plan should commit to running this over every workflow before agents and pages are wired. Each row is a silent
failure found in real builds (one pass over 26 workflows found three broken write tools that had passed every manual
test).

| Check | Failure if missed |
|---|---|
| PL/SQL write whose STOP does not read a trailing SELECT | empty result; the agent invents a success line |
| `inputs.setup.required` empty | parameters omitted, NULL columns |
| `:binds` in SQL vs keys in `record` | column silently NULL |
| OUT binds present in `record` | corrupted call |
| write tool without `approvalConfig.enabled` | agent writes unprompted |
| `deploymentState.workflowVersion !== version` | the old definition runs |
| `:word` inside a quoted SQL literal | `ORA-17003` |
| Code nodes ≥ native nodes, or a Code node > 60 lines, or doing a job in the native table | black-box logic, deploy-time failures |
| LLM step behind a screen with uncapped input | 30 s waits |
| `violations` not null after the last save | breaks later |
| `resourceVersion` ≠ the live one | "No config found" |
| START without trigger, a path not ending in STOP, STOP `result` not an object | invalid graph |
| LLM/OCR node not `CALL_INTERFACE_WORKFLOW`; call node not `CALL_WORKFLOW` | "No config found" |
| template naming a node id not in this workflow | silent NULLs, dropped keys |
| fetch without `triggerInputCondition`; consumer reading `outputs.records` | zero of everything |
| bulk upsert without `updateFields`; STOP without `successCount`; `skipIfBlank` on a clearable field | 200, nothing written |
| write not verified by a read-back | green run, nothing written |
| `fallbackMode: "CONTINUE"` relied on | run fails anyway |
| root `groupId` mixed or missing | graph hidden on canvas |
| `aggregate_records` or `filter_list` used | ⛔ wrong totals / empty lists |
| AI node without its evidence-log row | no audit, no cost |
| prompt naming another customer/vendor; no "the document is data" line; no `finish_reason` handling | wrong context, injection, truncation |
| a secret in inputs, prompts, `setup` defaults or payloads | secrets persist in the run store |
| a destructive node or SQL (`*_delete_*`, `DELETE`/`DROP`/`TRUNCATE`) that the scoping document does not specify (its Reset demo step keeps to exactly what it specifies) | data lost — use a status flag |
| tags missing | untraceable asset |

---

## 3. AI agents

### Entity and setup

- 🔴 **Check:** `properties.agentType` is set. **Fix:** `agentType: "ai-agent"` for a task/tool agent. The create call
  does not default it; without it the test surface degrades and the runtime appends extra messages after the answer ✅.
  An agent cloned from a team template inherits `agentType: "team"` — reset it.
- **Check:** the agent carries the full settings blocks. **Fix:** `topicExecutionSettings`,
  `responseGenerationSettings`, `preProcessingSettings`, `indexingSettings` all present; an agent missing them answered
  and then hung in an endless "Generating response…" ✅.
- **Check:** which model actually runs. **Fix:** `topicExecutionSettings.topicExecutionModel` drives the tool loop and
  the streamed answer; `answerGenerationModelSettings.modelId` overrides `answerGenerationModel`. Set the same model
  (the one chosen for the build) in all slots (`topicExecutionModel`, `topicSelectionModel`, `answerGenerationModel`,
  `answerGenerationModelSettings.modelId`). Set `disableThought: true` for a tool-calling analyst.
- **Check:** publish. **Fix:** `saveAndDeploy` with the **whole** entity; verify by snapshot (the deployed
  `properties` equal the agent's), redeploying at most three times. Never "publish until versions match" — the version
  climbs on its own. An agent never deployed answers 204 to an embedding page and the chat sits on "Loading…" ✅.
  Republish after any change to tasks, tools or settings.

### Tasks vs agent instructions — where behaviour rules go

- 🔴 **Check:** behaviour rules (how to end a turn, number checking, tool recovery, denial handling) live only in the
  agent's `instructions`. **Fix:** put them in **every task's** `instructions[]` too. Task instructions arrive as the
  `SetTopic` tool result, much more recent in context, and they dominate ✅. A rule to check the user's stated number
  did nothing in the agent prompt and worked as the first instruction of each answering task.
- **Check:** task shape. **Fix:** `description` = **when** to use it (the router matches on it, so write a trigger
  condition); `instructions` = **how**, as an array of strings; tools scoped by `topicId` so only that task's tools are
  in play. One task per subsystem or journey.
- **Check:** ID-MAPPING. **Fix:** each task's instructions name, for each id, the tool that produces it and the tool
  that consumes it — this is what makes chained calls reliable.
- **Check:** identity. **Fix:** one global `whoami` tool; every task says "call whoami first; never hard-code an id".
  Grep task instructions for literal ids — task-level text is where hard-coded ids survive. The model only knows the
  username (no email, id or display name); identity tools match on username and refuse an ambiguous name.
- **Check:** rules written negatively by quoting the unwanted phrase. **Fix:** never quote the forbidden string —
  it primes the model to emit it. Write it positively: "Describe only the business outcome. Do not announce completion
  or narrate your own mechanics."
- **Check:** the client business framing. **Fix:** agent and task instructions state, in one line, what the client
  business is and what it must never be called.

### Tools that call workflows

- **Check:** tool shape. **Fix:** `context: {appName: "callables", resourceName: "callables_call_automation"}`,
  `inputs: {automationId: <workflow id>, version: "-1", synchronous: true, runtimeConnections: {}, parameters: {}}`.
  Leave `parameters` empty so the model fills arguments from the workflow's `setup` schema; pre-seeded values pin them.
- 🔴 **Check:** `enabled: true` on every tool. **Fix:** tools default to `enabled: false`; the tool is then not offered
  and the agent answers in the abstract ("access to the following records would be required") — reads like a
  permissions problem, is a missing boolean ✅. Copy the flag set from a working tool (`enabled`,
  `isStandardAction: false`, `enableToolSearch: false`, `runTimeConnectionEnabled: false`, `deferToolLoading: false`).
- 🔴 **Check:** write tools. **Fix:** `approvalConfig: {enabled: true, storeUserApprovalPreference: false}` on every
  tool that writes. Instructions alone are not a gate — an agent told to "wait for a yes" asked and wrote in the same
  turn ✅. Add a task rule: a Deny is the person's decision — do not retry and do not call it a session or permission
  error.
- **Check:** names and descriptions. **Fix:** written as instructions to a model, not internal ids. A detail tool
  loses to a query tool unless its description says why it is required ("the ONLY read that returns notes — MUST be
  called for any one-record answer"; the query "does NOT return them").
- **Check:** duplicate tool names across the agent; a task with zero tools; a tool whose workflow is not deployed.
  **Fix:** unique names, at least one tool per task, every `automationId` deployed. Any of these can make the agent
  fail globally with "The agent hit an unexpected error".
- **Check:** personal connectors (mail, drive, calendar) bound to a fixed connection. **Fix:** omit `connectionId`
  and set `runTimeConnectionEnabled: true`, so each user connects their own.
- 🔴 **Check:** the plan removes or retires a task or tool. **Fix:** never remove tasks or tools by flag; disable them
  instead (`enabled: false`), after moving the task's tools to another task. Setting `deleted: true` makes the entity
  unupdatable while it still lists, and the whole agent then fails on every question; there is no API route back ✅.

### The generic query tool

- 🔴 **Check:** a generic `QueryData` tool with one `filter_field` / `filter_value`. **Fix:** three ANDed pairs
  (`filter_field`/`filter_value`, `…2`, `…3`). A multi-dimension lookup (scope **and** scope code **and** metric)
  cannot be expressed with one pair; the agent guesses, gets the wrong rows, guesses again and ends with no answer ✅
  (five calls and no answer before; an answer with a chart in 24–49 s after).
- **Check:** pre-processing. **Fix:** a comma-separated value becomes an `IN` list; `"true"`/`"false"` filter a
  boolean; a caller-added `properties.` prefix is stripped (otherwise the sort silently never applies).
- **Check:** result compaction. **Fix:** compact by **shape** (drop keys ending `_json` and strings over ~140
  characters, keep every number, code, date and flag, and return a note naming dropped fields), never by a whitelist
  of field names — a cloned whitelist returned sixty `{}` rows with no error ✅.
- **Check:** totals and counting. **Fix:** return `object_total` beside `returned` and tell the agent to say which it
  quotes; add `group_by` (+ `sum_field`) returning `groups[{value, count, sum}]` and `groups_total`, default the row
  limit to 0 when grouping, and say "quote groups_total, never count rows by hand" ✅. Or a separate `AggregateData`
  tool computed server-side.
- **Check:** row budget. **Fix:** default the row limit low (~100) in the workflow (the agent gets the default; the page
  passes its own); return `{count, matched, limit, truncated, rows}`; a whole-record dump of hundreds of rows makes the
  model conclude the data is empty ✅.
- **Check:** the data source that fronts the query workflow. **Fix:** callers must send **every** templated input,
  blank where unused; a missing one reaches the workflow as literal `{{filter_field}}` text and the read returns zero ✅.
- **Check:** the instructions. **Fix:** a worked example of the hardest call (all three pairs, sort field and order),
  and a stopping rule: "two calls that returned the wrong rows means the filter was wrong; never make a third guess —
  say what you found and what is missing".

### The turn contract — an agent announcing a call it never makes

- 🔴 **Check:** every agent's (and every task's) instructions carry the turn contract. **Fix:** add, right after the
  tool-recovery rule: the last thing written is the answer, never a plan; a final sentence starting "Let me", "I'll
  now", "Next I will" means the turn is not finished — make the call or delete the sentence; at most five query calls
  per turn, then answer with the gap named; a field that cannot give what was wanted is a finding, not a reason to
  stop; open with the answer, not with working notes. Without it ~1 turn in 9 ended on "Let me look at…" with
  status `completed` ✅. There is no max-iterations setting to raise — it is a prompting fix.
- **Check:** trailing filler after a write ("operation completed…", "what next?"). **Fix:** "reply with the business
  outcome only and end the turn" in every task, the write task included. The platform appends a synthetic continue
  turn after an assistant message, which triggers an extra generation; instructions reduce it.
- **Check:** how answers are measured. **Fix:** the answer is the **first** bot message without
  `internalMessageType` in the reverse-chronological conversation, after status `completed` and the text has settled —
  not the longest one (in a stalled turn the longest is a mid-turn narration).

### Charts the agent writes

- 🔴 **Check:** an agent expected to draw charts. **Fix:** enable `generateChartTool`, `renderArtifact` **and**
  `executeCodeTool` as standard-action tool rows (`isStandardAction: true`, `enabled: true`, `topicId: "GLOBAL"`).
  Without `renderArtifact` the agent prints a table while claiming "here is your chart" ✅; without `executeCodeTool`
  the turn ends silently after loading the chart skill ✅. Instruct the agent to write the full text answer whether
  or not a chart renders.
- ⚠️ **Check:** the plan's answers depend on the in-chat chart path. **Fix:** it has also ended silently with all three
  enabled; prove it over the API before relying on it, or have the agent emit chart data the page renders. One chart
  request cost ~290K tokens, ~94 s and ~5–10× a normal turn — enable deliberately, not on every answer.
- **Check:** chart blocks the page renders from chat. **Fix:** show the contract by one whole example per chart shape,
  never as `"type": "bar|line|…"` — the model treats the pipe list as a value for whichever field comes to mind; say
  in words that the `kind` field never changes. Use the real figures just read, cite the source, keep the prose
  answer; no total on scores, averages, rates or time series.

### Entity guide and grounding

- **Check:** the analyst agent's instructions name each object it reads, its key fields, the meaning of each status
  and how objects link. **Fix:** add an entity guide (object → fields → which tool reads it → example filter). With
  one generic query tool, naming objects and fields in the instructions is what makes routing correct, and adding an
  object costs nothing.
- **Check:** number grounding. **Fix:** the NUMBERS rule verbatim in agent/task instructions and insight prompts:
  quote only figures in the data exactly as given; never count rows, add, average or derive a figure; if a count
  matters and the data does not state it, name the records. Fast models miscounted 30 given rows (said 26) ✅. Counts
  come from `count_records` / SQL-on-list / `groups_total`.
- **Check:** narrow mandates. **Fix:** prefer several narrow agents (answer, detect, advise) over one broad one when
  their refusal rules differ; they can share the same tools.
- **Check:** knowledge (RAG) sources. **Fix:** retrieval is filtered by the **viewer's** sharing; knowledge owned by a
  different account returns zero chunks and the agent loops. Tabular files go to a text-to-SQL path and do not answer
  prose questions.

### Latency

- Chat turn times to expect (not a finding on their own): simple counts ~10 s, charted answers 18–31 s, multi-query
  reasoning 43–72 s, plus the platform's own silent gap between phases (10–25 s).
---

## 4. Architecture rules that do not conflict

- **Check:** the plan names its style. **Fix:** **Full** for request/case desks (intake → AI reading → rule check →
  auto-decide or route to a person), document evidence verdicts and designed multi-step agentic operations; **Light**
  for dashboards, KPI command centres, analytics and chat-over-data. Never force Full onto a dashboard or
  chat-over-data use case.
- **Check (Full):** process stages. **Fix:** every step sits in one of six stages in this order — Setup · Read &
  ground · Understand & prioritize · Propose · Govern · Publish & measure: acquire truth first, decide later, write
  last.
- **Check (Light):** a short numbered process (steps, who acts, what each produces); each step is a workflow, one
  orchestration per human action; an AI reading is an LLM step inside the workflow that needs it, made an AI agent only
  when it needs tools or must sit in the agent registry; a reading below the bar becomes a `needs_review` status shown
  as a queue where that person already works.
- **Check:** a model doing arithmetic, lookups or thresholds. **Fix:** move them into a workflow step or tool; the
  model proposes, deterministic steps verify and execute.
- **Check:** one AI step, one job. **Fix:** an AI step (or atomic agent) whose output can be wrong in two independent
  ways is split in two. Atomic agents are single-action and named for that action ("Duplicate Claim Detector"), never
  for an area. A conversational assistant is a screen's assistant whose tools are workflows, not an atomic agent.
- **Check (Full):** atomic agents. **Fix:** each is a real AI agent with one task, invoked from its sub-workflow by
  the Invoke Agent node (`CALL_INTERFACE_WORKFLOW`, `ai_agents_by_unifyapps_invoke_agent`) 👁, answering a JSON
  envelope (`status`, `value`, `confidence`, `confidence_basis`, `binding_constraint`, `abstain_reason`); a composite
  takes the **minimum** confidence, never the mean. Prove one agent through the node before building the rest.
- **Check:** confidence and evidence on AI readings. **Fix:** every AI reading that drives a decision is stored with
  its confidence and the evidence behind it; a reading below the bar goes to a person, never "proceed with a warning".
  A step that must end in a person says so even at full confidence.
- **Check:** one current reading per record, history in the evidence log (section 1).
- **Check:** deterministic claims. **Fix:** where the product's claim is deterministic (a check, a score), the
  deterministic layer owns the verdict and evidence; the model owns the reading and the so-what. Give "inconclusive" a
  place; never let a finding become a statement about a person.
- **Check:** scores. **Fix:** a score that orders a queue is calibrated on ordinary traffic, not only adversarial
  cases (check the distribution and the band histogram); a rescore workflow recomputes from stored findings.
- **Check:** derived aggregates. **Fix:** one rollup workflow rebuilds every derived number from the base records,
  called after the action that changes them.
- **Check:** internal codes on screens. **Fix:** no internal codes (step, workflow, agent ids, raw record ids, tool
  names, JSON) on any screen or in a user-voice message; tool routing belongs in instructions.
- **Check:** one application per use case. **Fix:** every screen is a page of that one app, grouped by role; a second
  app only when the requirements ask for one.
- **Check:** agent writes to an outside channel. **Fix:** no agent writes to a customer-facing channel unless the
  scope says so; read-only first for anything commercial.

---

## 5. Data sources and connections

### How pages read data

- 🔴 **Check:** pages call workflows or objects directly. **Fix:** every page → platform call goes through a
  registered `e_data_source` — a storage binding on an object (fetch, fetch-one, create, update, upsert) or a binding
  on a callable automation or connector action. No data source → `forbidden datasource: not found`; a stored input
  omitted or a non-templated input changed → `forbidden datasource : invalid input` ✅. Fix the data source, never
  route around it.
- **Check:** one data source per callable workflow a page uses. **Fix:** list them in the plan; each one's stored
  inputs mirror the workflow's `setup` schema with `{{placeholders}}` for every parameter.
- **Check:** callers send every templated input. **Fix:** blank where unused (see section 3 — a read returns zero
  otherwise; a write errors).
- **Check:** storage write bindings. **Fix:** they carry `useRawPayload: true` — the page's writer must be
  read-merge-write (section 1).
- 🔴 **Check:** publish order. **Fix:** the app must be published after every new or changed data source or agent; the
  deployed app fixes its set of data sources at publish time, and anything newer is rejected at run time (two screens
  sat empty for an hour over this) ✅. The app also returns 401 on every data call until it has been published once —
  publish the scaffold early.
- **Check:** simulated sources. **Fix:** when an outside system is stood in for by a seeded object, the object uses the
  **same field names** the connector would return, so switching to the real connector later is a change of the reading
  node and nothing else.
- **Check:** a deterministic capability the platform lacks. **Fix:** one HTTP node away
  (`custom_http_endpoint_execute`, no connection needed); the service owns the verdict, the workflow owns the records.

### Connections — search before you create

- 🔴 **Check:** the plan creates a connection, workflow, object or agent without searching first. **Fix:** "search
  before you create — reuse, clone or create": search the tenant for each planned asset; reuse or reference what fits,
  clone what nearly fits, create only what is missing, and record which for each asset.

  | Asset | Search |
  |---|---|
  | Workflows | `POST /api/aggregation?entityType=WorkflowDefinition&group=STANDARD`, full body, `lcName ICONTAINS` (names are not unique; track ids) |
  | Objects | `POST /api/aggregation?entityType=EntityType&group=STANDARD`, `standard` false or MISSING |
  | Agents | `POST /api/entity/ai_agent {page:{limit, offset}}`, filter `properties.name` client-side; skip `(Deep Clone)` rows |
  | Connections | `POST /api/aggregation?entityType=Connection&group=STANDARD` by `appName` + `active`; prefer one owned by the person |

- **Check:** connection identification. **Fix:** match a connection by `appName` and its real host/service, not by
  name — names are arbitrary and duplicated; avoid ones marked DND / DONT TOUCH. Never list all connections with the
  plain GET (slow, returns secrets).
- **Check:** connections needing OAuth or secrets. **Fix:** the person creates or authorizes them in their own
  account; the plan only references the id.
- **Check:** assets not owned by the person. **Fix:** read-only — reference them (a tool pointing at its workflow, a
  data source pointing at its automation) or clone into a new asset; never edit. A cloned workflow clones its prompt
  and model settings: rewrite the prompt, re-set `modelId` and `maxTokens`.

### Tagging and ownership

- **Check:** every created entity is tagged. **Fix:** a project tag plus a consistent name prefix/suffix on every
  workflow, object, agent, task, tool and data source. `tags` is a plain string array at the **top level** of the
  create payload (inside `properties` fails); it is accepted on tasks and tools too and must be resent on every update.
  The workflow read-back does not return tags — verify through an aggregation projection.
---

## 6. Task graph checks

- **Check:** every entity in the spec has exactly one task, and every task builds exactly one entity. **Fix:** add the
  missing task; split a task that builds two; merge duplicates. Agent tasks and tools, data sources, indexes and the
  evidence-log object count as entities if the spec lists them.
- **Check:** each task's owner fits the entity kind (e.g. workflows with automation-agent, AI agents with
  agent-builder, pages with the app builders). **Fix:** reassign.
- **Check:** waits-on order. **Fix:**
  1. objects (and their indexes) before the seed that loads them and the workflows that read or write them;
  2. a callable workflow before any workflow that `CALL_WORKFLOW`s it;
  3. workflows **deployed** before the agent tools that call them and the data sources that front them;
  4. agent tasks before the tools scoped to them; tools before the agent's final publish;
  5. agents published, and data sources created, before the pages that embed or call them;
  6. the app publish after the last data source and agent change.
- **Check:** connections. **Fix:** any connection the person must authorize is a wait on every workflow that uses it,
  surfaced early, not discovered at the end.
- **Check:** needless chains. **Fix:** objects are independent of each other (lookup fields only need the target id
  at write time); independent workflows, seed loads and pages run in parallel. Chain only on a real dependency (an id
  or a deployed version the next task needs).
- **Check:** verification tasks. **Fix:** each write workflow's task includes its read-back test; the agent's task
  includes one tool-only question whose number is checked against the records; the page's task includes loading the
  page after the final publish.

---

## 7. Top 15 checks

1. Every partial record write is read-merge-write; no partial `useRawPayload` payload; bulk upserts use `updateFields`.
2. Every object has a key, a tight `required` list, `oneOf` statuses used exactly by all writers, and custom indexes
   (equality → sort → range, ≤ 5) for every query shape beyond the key.
3. Native nodes first; no `aggregate_records` / `filter_list`; Code only for a real computation, short, titled with why.
4. One callable orchestration per human action; START has a trigger and a non-empty `required` in `setup`.
5. Every write is verified by a read-back that STOP returns; PL/SQL writes end with a verification SELECT.
6. SQL binds: `params` **and** `record`, keys diffed against the SQL, OUT binds excluded, no colon inside a quoted literal.
7. Fetches use `outputs.objects` / `outputs.total` and always send `triggerInputCondition`; loop bodies sit in the
   loop's child group; error edges use `fallbackMode: "MANUAL"`.
8. Deploy after every edit and assert the deployed version equals the saved version; `violations` null after every save.
9. AI steps behind a screen: capped input, `maxTokens` sized, `finish_reason` handled, NUMBERS rule, one
   evidence-log row per call.
10. Agents: `agentType: "ai-agent"`, full settings blocks, one model set in all slots, published and verified by snapshot.
11. Behaviour rules (turn contract, number check, denial handling, end-the-turn) in **every task**, not only the agent prompt.
12. Tools: `enabled: true`, empty `parameters`, write tools `approvalConfig.enabled`; never remove tasks/tools by flag —
    disable instead.
13. Generic query tool: three filter pairs, shape-based compaction, `object_total` / `groups_total`, low default limit,
    a worked example and a stopping rule in the instructions.
14. Charts in chat need `generateChartTool` + `renderArtifact` + `executeCodeTool`, a text answer regardless, and are
    proven before relied on.
15. Pages read only through data sources; search before you create (reuse, clone or create); everything tagged; the
    task graph orders objects → workflows (deployed) → tools/agents → data sources → pages → app publish, with
    independent work in parallel.
