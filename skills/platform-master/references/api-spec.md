# UnifyApps Platform API — Specification (Orbit UAT)

The verified endpoint catalogue for `platform-master`: request and response shapes, workflow-step
contracts, the error catalogue, confirmed dead ends and lessons from earlier builds. Everything is
stated for **Orbit UAT** (`https://orbit.uat.unifyapps.com`) unless an entry says it was verified on
another tenant, in which case confirm it on Orbit UAT before relying on it. Calls run same-origin from
the person's signed-in browser tab (`fallback-by-api.md`). Ids in examples are placeholders: resolve
real ids on the tenant. Never copy an action's `resourceVersion` from here; resolve it at build time.

## 1. Evidence markers

| Mark | Meaning |
|---|---|
| ✅ | **Verified** — called directly and the result confirmed |
| 👁 | **Observed** — seen succeeding in live UI traffic, not called directly |
| 📦 | **Bundle-only** — path found in the front-end JavaScript; never exercised |
| ⚠️ | **Partial** — works, with a caveat that matters (stated inline) |
| ⛔ / ❌ | **Does not work** — tested; 404 / 405 / silent no-op. Kept so nobody retests it |

A ✅ on one tenant is not a ✅ on another — platform versions differ.

## Never call (deletes)

These exist on the platform. They are listed only so they are recognised and refused. Never call
them, never send HTTP `DELETE` to any path, never set `deleted: true` or `requestType: "DELETED"`,
and never build a delete node (`storage_by_unifyapps_delete_record(s)`, `_delete_record_by_id`,
any connector `*_delete_*` / `*_remove_*` action) into a workflow, data source or agent tool.

`POST /api/workflow-definition/delete/{id}` · `POST /api/entity/{entityType}/delete/{id}` ·
`POST /api/entity/action/delete` · `POST /api/context-graph/delete/{graphId}` ·
`POST /api/context-graph/nodes/delete/{nodeId}` · `POST /api/context-graph/edges/delete/{edgeId}` ·
`POST /api/context-graph/sources/delete/{id}` · `DELETE /agent-api/sessions/{s}/branches/{b}` ·
`DELETE /api/entity/{type}/{id}` · `POST /api/entity/create-update-or-delete/hierarchical` with `requestType:"DELETED"`

## Contents

- 2. Conventions
- 3. Authentication & session
- 4. Workflow definitions
- 5. Workflow builder — node catalog & schemas
- 6. Workflow execution & runs
- 7. Connections
- 8. Entities (generic CRUD)
- 9. AI agents, tasks, tools
- 10. Search: aggregation & lookup
- 11. Observability & traces
- 12. Enterprise Context Graph
- 13. Files
- 14. Other observed platform endpoints
- 15. Confirmed dead ends
- 16. Node action contracts
- 17. Error catalogue
- 18. Discrepancies and how they were settled (Orbit UAT)
- 19. Open questions
- 20. UI routes
- 22. Applications — data sources and publish
- 23. How app code calls the platform
- 24. Objects Manager
- 24b. AI Solutions — the platform's native prompt-to-solution builder
- 25. Connectors SDK (custom connectors)
- 26. Findings — AI-native app patterns (UAT)
- 27. Findings — scaling one app's data layer to 8,000 records (UAT)
- 28. Findings — cloning assets, objects, records (UAT)
- 29. Data sources in a config app (UAT)
- 30. Findings — Groovy validator, aggregation, stalling agents (UAT)
- 31. Connector catalogue — what exists and what it can do (UAT)
- 32. OCR / extraction node (UAT)
- 33. Findings — agents that stop early, publishing whole entities (UAT)
- 34. Findings — storage node shapes and the graph engine on Orbit UAT
- 35. Findings — an external HTTP service inside a workflow (UAT)
- 36. Findings — an app whose only source is the graph (verified on another tenant; confirm on Orbit UAT before relying on it)
- 37. Findings — running a real document corpus through a workflow (UAT)
- 38. Findings — entity updates and call nodes (UAT)
- 39. Findings — testing a finished graph-backed app (verified on another tenant; confirm on Orbit UAT before relying on it)
- 40. Findings — a 58,000-record build (UAT)
- 42. Findings — loading a large graph (verified on another tenant; confirm on Orbit UAT before relying on it)
- 41. Findings — generating 109 workflows from one design (UAT)
- 44. Findings — agent create and publish, entity tags (UAT)
- 45. Findings — an integration layer over simulated systems (verified on another tenant unless marked UAT; confirm on Orbit UAT before relying on it)
- 46. Findings — a read-only HubSpot read (UAT)
- 47. Findings — agents, tags, workflow updates, LLM and storage nodes (UAT)
- 48. Findings — data layer: three objects, 1,268 records (UAT)
- 49. Findings — six callable workflows and their data sources (UAT)
- 50. Findings — an agent built and tested over REST (UAT)
- 51. Findings — data-source scope in a config app (UAT)
- 52. Findings — governance: guardrails vs controls (UAT)
- 53. Findings — simulated source systems and scheduled sync (UAT)
- 54. Findings — live testing a supplier-risk build (UAT)
- 55. Findings — a property-performance build (UAT)
- 56. Findings — Code-node audit, native-node probe, insight latency (UAT)
- 58. Findings — SAP connectors (UAT)
- 57. Findings — native nodes instead of wrapper Groovy (UAT)
- 61. Findings — role-aware queries, skill drafts (UAT)
- 59. Findings — build-kit hardening (UAT)
- 60. Findings — a 115-workflow, 40-agent build with a context graph (verified on another tenant; confirm on Orbit UAT before relying on it)

---

## 2. Conventions

### Base URL and paths

All endpoints are relative to the tenant origin. Two prefixes exist:

- `/api/...` — everything except login
- `/auth/...` — the login executor only. **`/api/login`-style paths do not exist** (§15).

### Authentication

Session cookie, **httpOnly**, set when the person signs in. Every `/api/*` call requires it.
Call the API **same-origin from the person's signed-in browser tab**
(`fetch('/api/...', {credentials:'include'})`); the cookie rides along, page JavaScript cannot read
it, and no credential enters the conversation. ✅ UAT

When the session expires:
- `GET /api/user-context` returns **401**, and/or
- the call is **redirected to the HTML login page** — check `content-type` before parsing
  JSON, or you will parse HTML. Ask the person to sign in again; never retry in a loop.

### Headers

| Header | Value | Required |
|---|---|---|
| `Content-Type` | `application/json` | on bodies |
| `Accept` | `application/json` | recommended |
| `x-ua-timestamp`, `x-ua-timezone`, `x-ua-trace-id` | set by the web UI | no — calls succeed without them ✅ |

### Methods

The platform is **POST-heavy**. Updates are usually `POST .../update/...`, not `PUT`/`PATCH`.
Assume POST unless an entry says otherwise.

> 🚫 **Never delete.** Delete endpoints exist on the platform. This file does not document how to
> use them; they are listed once, by path, under "Never call (deletes)" so they can be recognised
> and refused. Never set a `deleted` flag to true, never send `requestType: "DELETED"`, and never
> build a `*_delete_*` node into a workflow, data source or agent tool. To switch something off,
> set a status / `archived` / `active:false` / `enabled:false` flag, or leave a workflow undeployed.

### Standard response envelopes

**Aggregation** (`/api/aggregation`):
```json
{ "objects": [ { "columns": { "id": "...", "name": "..." } } ],
  "totalHits": 123, "hasMore": false, "cursor": { "next": "<base64>" },
  "type": "AGGREGATION_RESPONSE" }
```
Read `o.columns`, not `o`. Column names are often abbreviated (see *Field abbreviations*).

**Entity** (`/api/entity/...`):
```json
{ "id": "<id>", "entityType": "ai_agent", "version": 1,
  "createdTime": 1789801645357, "modifiedTime": 1789801645357,
  "ownerUserId": <userId>, "lastModifiedBy": <userId>, "deleted": false, "standard": false,
  "deploymentState": { "deployedAt": 0, "deployedBy": 0, "entityVersion": 1, "version": 1 },
  "properties": { }, "grants": { "configs": [] }, "tags": [] }
```
Everything meaningful lives in `properties`.

**Entity list** (`POST /api/entity/{type}`):
```json
{ "objects": [ ...entities ], "hasMore": true, "cursor": { "next": "..." }, "type": "HITS" }
```

**Lookup** (`/api/lookup`):
```json
{ "response": { "objects": { "<key>": {...} }, "inaccessibleObjects": [], "type": "MAPPED_HITS" } }
{ "response": { "objects": [ ... ], "hasMore": false, "cursor": {...}, "type": "HITS" } }
```
`ByKeys` returns `MAPPED_HITS` (keyed map); `ByQuery` returns `HITS` (array).

### Error envelope

```json
// 404 / 405 — terse
{ "errorCode": -1, "errorId": "5b583ca8-6ca3-4ee1-84ed-cc273aad2851" }

// 500 — descriptive
{ "rootCauseMessage": "...", "message": "...", "errorCode": -1,
  "errorId": "<uuid>", "serviceName": "WorkflowDefinitionService" }

// 500 — asset not found
{ "rootCauseMessage": "CONNECTION with id oracledb not found",
  "assetClass": "CONNECTION", "assetId": "oracledb", "errorCode": 5002, ... }
```

Known `errorCode` values: `-1` generic · `5002` asset not found · `5004` invalid
group/type for aggregation. Full list in §17.

> ⚠️ **A 200 does not mean success.** Several endpoints return 200 while doing nothing
> (`objects/bulkUpdate` → `{"data":0}`), and `saveAndReturnViolations` returns 200 *and
> persists* a graph that has violations. Always check the body.

### Id formats

| Thing | Format | Example |
|---|---|---|
| Workflow | 24 hex | `<id>` |
| Deployed workflow snapshot | `s_{workflowId}/{version}/{hash}` | `s_<id>.../3/Khf8HC...=` |
| Entity (agent, task, tool, ...) | `e_` + 24 hex | `<id>` |
| Workflow node | author-chosen; UI uses `n_` + 5 chars | `n_sql`, `n_7M2BR` |
| Workflow edge | `{type}@{fromNodeId}@{toNodeId}` | `next@n_in@n_sql` |
| Run / execution | 24 hex | `<id>` |
| Node-output key | `{rootExecutionId}.{executionInstanceId}.{nodeId}` | `6aae26...026.6aae26...026.n_out` |
| User | integer | `<userId>` |
| ECG vertex | `{spaceId}::{unifiedEntityId}::{recordId}` | `90::6aae7f3c...::CON-001` |
| ECG record edge | `{fromVertex}::{toVertex}` | |

### Field abbreviations (aggregation)

| Abbrev | Field | Abbrev | Field |
|---|---|---|---|
| `cTm` | created time | `mTm` | modified time |
| `oUId` | owner user id | `lMBy` | last modified by |
| `d` | deleted | `pId` | project id |
| `v` | version | `lcName` | lower-cased name |
| `lPUBy` / `lPUOn` | last platform update by / on | | |

### Templating (inside workflow node inputs)

`{{ n_<nodeId>.outputs.<path> }}` — spaces inside the braces. A value starting with `=` is a
formula: `"=SUM({{ n_v.outputs.i }},1)"`, `"=LEN({{ n_x.outputs.items }})"`.
**An unresolved template silently drops the key** — no error, no violation.

---

## 3. Authentication & session

The person signs in to Orbit UAT themselves, in the browser. Every call then runs same-origin from
that signed-in tab (`fetch('/api/...', {credentials:'include'})`); the httpOnly session cookie rides
along and no credential ever enters the conversation. The platform also has a password login
executor (`POST /auth/workflow/execute/node?name=emailAndPassLoginRequest`, under `/auth/`, not
`/api/`); it is not used here, and nothing here ever handles a password.

### `GET /api/user-context?includeRoles=true` — Current user
✅ UAT

Session check and current-user details. Returns **401** when the session is invalid — the
cheapest liveness probe.

**Response** — 200, user object. `customer.id` is the tenant **`spaceId`** used in ECG
vertex ids (another tenant = `90`). Full field list not yet recorded.

### OAuth surface (UI routes, not REST)
📦 UAT

`/ui/auth/oauth/authorize`, `/oauth-consent`, `/complete/oauth/`, `/runtime-auth/new/`
exist in the login bundle — the platform can act as an OAuth authorization server. **No token
endpoint has been found**; see §19.

---

## 4. Workflow definitions

A workflow ("automation") is a `WorkflowDefinition`: `nodes[]` + `edges[]` + settings.
Node/edge model is in §16.

### `POST /api/workflow-definition` — Create
✅ UAT

**Request**

| Field | Type | Req | Notes |
|---|---|---|---|
| `name` | string | ✅ | not unique — track ids |
| `description` | string | | |
| `nodes` | array | ✅ | **must be non-null**, even for a stub (see Errors) |
| `edges` | array | | `[]` allowed |
| `tags` | string[] | | top-level; the supported ownership marker in shared tenants |
| `settings` | object | | defaults applied if omitted |

Minimal stub (then fill it via `saveAndReturnViolations`):
```json
{ "name": "My Automation", "description": "created via API",
  "nodes": [ { "id": "n_seed", "type": "START", "title": "seed",
               "trigger": { "type": "EVENT" }, "index": 0, "groupId": "n_seed-1",
               "fallbackMode": "STOP", "skip": false } ],
  "edges": [] }
```

**Response** — 200, the full `WorkflowDefinition`:
```json
{ "id": "<id>", "name": "My Automation", "lcName": "my automation",
  "description": "...", "version": 0, "standard": false, "deleted": false,
  "appsUsed": [], "ownerUserId": <userId>, "createdTime": 1789796832014, "modifiedTime": 1789796832014,
  "settings": { "enableNodeLevelLogging": true, "enableRunLogging": true,
                "enableVariableLogging": true, "route": { "default": false, "tierName": "global" } },
  "nodes": [ ... ], "edges": [ ... ] }
```
`lcName`, `appsUsed`, timestamps and ownership are server-assigned.

**Errors**

| Status | Message | Cause |
|---|---|---|
| 500 | `Cannot invoke "java.util.List.iterator()" because the return value of "...WorkflowDefinition.getNodes()" is null` | `nodes` omitted |

### `GET /api/workflow-definition/{id}` — Read
✅ UAT

Returns the full definition (same shape as create).

⚠️ **Does not return `tags`.** Read tags back only via aggregation projection
`[{"name":"tags"}]` (§10).

⚠️ **`groupId` on the stub START hides the rest of the graph in the builder canvas** (UAT): a
definition whose START had `groupId:"n_in-1"` while the other nodes had none rendered as trigger-only
("+" below it) although `GET` returned all 5 nodes and 4 edges. Either give every node no `groupId`
(what the UI does for a single lane) or the same one. Re-saving without `groupId` fixed it.

### `POST /api/workflow-definition/saveAndReturnViolations` — Save / update
✅ UAT

The real "save". Send the **complete** definition.

**Request** — full `WorkflowDefinition` including `id` and the **current** `version`,
`nodes`, `edges`, `settings`, `schemaReferences: []`, `standard: false`.

**Response** — 200:
```json
{ "workflowDefinition": { ...saved, "version": 1 },
  "violations": [ { "id": "n_brk", "type": "NODE",
                    "innerViolations": [ { "id": "Outgoing", "type": "next",
                      "message": "This automation has a trigger which expects response. Please add a step to send a response{{stepLabel}}." } ] } ] }
```
`violations` is `null` (or absent) when valid. `version` increments per save.
`appsUsed` is recomputed server-side from node `context.appName`.

**Notes**
- ⚠️ **HTTP 200 and persisted even with violations.** Always check `violations`.
- The UI calls this for Save; the UI never uses the bare `update/` endpoint.

### `POST /api/workflow-definition/{id}/deploy?version={n}` — Deploy
✅ UAT

**Request**

| Where | Field | Notes |
|---|---|---|
| query | `version` | the draft version to deploy (from the last save) |
| body | `deploymentNotes` | free text |
| body | `_type` | literally `"WORKFLOW_DEPLOY_OPTIONS"` |

```json
{ "deploymentNotes": "API-built callable workflow", "_type": "WORKFLOW_DEPLOY_OPTIONS" }
```

**Response** — 200:
```json
{ "workflowDefinition": { "id": "<id>",
    "deployedWorkflowVersion": 1, "deployedWorkflowNotes": "API-built callable workflow", ... } }
```
⚠️ The returned `id` is a **deployed snapshot id**, distinct from the draft id. The draft
and deployed copies version independently.

**Notes**
- Deploying a `SCHEDULED` workflow activates a live recurring job. `CALLABLE` workflows only
  run when invoked.
- ⛔ `/api/entity/action/saveAndDeploy` is **not** the workflow deploy — that is for entities (§8).

### `POST /api/workflow-definition/reachableFromNodeIds` — Graph reachability
👁 UAT

Builder helper, called while editing.

```json
{ "nodeId": "n_ahrd9",
  "workflowDefinition": { "name": "", "version": 0, "nodes": [ ... ], "edges": [ ... ] } }
```

### Other workflow-definition endpoints

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/api/workflow-definition/validate` | 👁 UAT | called by the UI before a test run; body not captured |
| POST | `/api/workflow-definition/executedWorkflowDefinition` | 👁 UAT | body `{"deployedWorkflowId":"s_{id}/{ver}/{hash}","test":true}` → the definition a run used |
| POST | `/api/workflow-definition/update/` | 📦 | partial update; unused by the UI |
| POST | `/api/workflow-definition/clone/` | 📦 | |
| GET | `/api/workflow-definition/deployed-workflow/` | 📦 | |
| GET | `/api/workflow-definition/node-dependency/` | 📦 | |
| GET | `/api/workflow-definition/global-settings` | 📦 | |
| GET | `/api/workflow-definition` | ⛔ 405 | there is **no list GET** — use aggregation (§10) |

---

## 5. Workflow builder — node catalog & schemas

How to discover which actions exist, their versions, and their input/output schemas.
**Resolve `resourceVersion` from here at runtime** — it drifts (e.g. `oracledb_execute_sql`
16522 → 16523, `if_else_condition` 11 → 204).

### `GET /api/workflow-builder/nodes` — Node catalog
✅ UAT

**Query params**

| Param | Notes |
|---|---|
| `fields` | comma list, e.g. `name,displayName,iconUrl,tags,type,needsAuthentication,custom,hidden` |
| `resourceType` | e.g. `ACTION` (👁) |
| `name` | ⛔ ignored — returns the full list |

**Response** — 200:
```json
{ "objects": [ { "id": "<id>", "name": "formbuilder_123",
                 "displayName": "123FormBuilder", "type": "ACTION", "tags": ["Applications"],
                 "needsAuthentication": true, "custom": false, "hidden": false,
                 "standard": false, "iconUrl": "https://...", "lcName": "...", "version": 0,
                 "hasOverriddenDetails": false, "deleted": false } ],
  "totalHits": 1210, "hasMore": false, "type": "HITS" }
```
**1,214 nodes on UAT**, up from 1,210 on 2026-09-19: **983 application connectors
+ 91 platform nodes (`tags: ["Internal"]`) + 140 custom**. 1,064 need a connection; 1 hidden;
0 `standard`. `type` values: `ACTION` (1,203), two `LOOP`, and one each of `IF_ELSE`, `BRANCH`,
`BRANCH_CONDITION`, `BREAK`, `CONTINUE`, `DELAY`, `SCOPE`, `STOP`, `CALL_WORKFLOW`.
Custom connectors have `custom: true` and a 24-hex id as `name`. The full catalogue ships in
§31 and `connectors.md`.

### `GET /api/workflow-builder/node/{nodeName}` — Node detail
✅ UAT

Node metadata plus a large `grants` block.

### `GET /api/workflow-builder/node/{nodeName}/resources` — A node's actions
✅ UAT

**Response** — 200:
```json
{ "objects": [ { "name": "oracledb_execute_sql", "displayName": "Execute a SQL statement",
                 "version": 16523, "nodeName": "oracledb", "resourceType": "ACTION",
                 "async": false, "hidden": false, "custom": false, "standard": false,
                 "passNodeSchema": false, "nodeTestDisabled": false, "description": "..." } ],
  "hasMore": false }
```
`version` here is the value to put in a node's `context.resourceVersion`.

**`resourceType` values ✅ UAT** — `ACTION`, `TRIGGER`, and **`AGENT_TOOL`**, a
ready-made agent tool. `AGENT_TOOL` is rare: on UAT only `github` shipped any
(`github_tools_get_file_modified_details`, `github_tools_list_collaborators`). Verified
mixes (ACTION/TRIGGER/AGENT_TOOL): `hubspot` 100/6/0 · `jira` 78/13/0 · `salesforce` 65/11/0 ·
`github` 44/12/2 · `slack` 44/2/0 · `gmail` 25/8/0 · `oracledb` 17/6/0 ·
`custom_http_endpoint` 7/0/0. Resource counts per connector run 1–170 (`workday`, `keka` 170;
`netsuite` 146; `snowflake` 145; `microsoft_teams` 136).

⚠️ A published **Connectors SDK** action can be attached to a *built-in* connector: `slack`'s
resource list contains six entries named `slack:{24-hex actionId}` alongside the standard
`slack_*` ones, flagged `custom: true`. A colon in a `resourceName` means "tenant-local" —
never put one in a portable artefact; resolve it with
`GET /api/connector-builder/definition/{defId}` (§25).

### `GET /api/workflow-builder/node/{nodeName}/resource/{resourceName}` — Action schema
✅ UAT

The input and output contract for one action. ~15 KB typical.

**Response** — 200:
```json
{ "name": "oracledb_execute_sql", "version": 16523, "resourceType": "ACTION",
  "input":  { "type": "SCHEMA_AND_LAYOUT", "dynamic": false,
              "schema": { "type": "object", "required": ["sql"], "properties": { ... }, "definitions": { } },
              "layout": { "ui:order": [...], "sql": { "ui:widget": "..." } } },
  "output": { "type": "SCHEMA_AND_LAYOUT",
              "schema": { "type": "object", "properties": { "rows": {...}, "rowsCount": {...}, "rowsAffected": {...} } } },
  "groupDetails": { } }
```
- Generate node `inputs` against `input.schema`. `input.layout` is UI-only.
- `input.dynamic: true` means the schema depends on runtime lookups — not yet exercised (§19).
- Some outputs are `SCHEMA_AND_LAYOUT` with no properties (e.g. callables) — they are
  dynamic, derived from the node's own config.

### `GET /api/workflow-builder/find-nodes-with-connections` — Nodes with a connection
✅ UAT

Same `fields` param as `/nodes`. Returns a **plain JSON array** (not the `objects` envelope)
of nodes that have at least one configured connection. 299 on 2026-09-19, **304 on
2026-09-23**.

⚠️ **It over-reports.** 25 of the 304 return `totalHits: 0` from
`POST /api/aggregation?entityType=Connection` for the same `appName` — deleted or
out-of-project connections still count here. Use this endpoint to narrow 1,214 nodes to ~300,
then trust the aggregation count for whether a connection is actually usable. (§18 D4)

### Other builder endpoints

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/api/workflow-builder/search-nodes-and-resources` | 👁 UAT | → `{nodeBuilders:{...}, nodeBuilderResources:{...}}` |
| GET | `/api/workflow-builder/env-variables` | 👁 UAT | |
| GET | `/api/workflow-builder/node/resource/entity-search-enabled` | 👁 UAT | |
| POST | `/api/workflow-builder/lookup/output-schema` | 👁 UAT | called before a test run |
| POST | `/api/workflow-builder/lookup/input-schema` | 📦 | |
| POST | `/api/workflow-builder/lookup/output-schema/with-errors` | 📦 | |
| POST | `/api/workflow-builder/lookup/nodes/output-schema/with-errors` | 📦 | |
| POST | `/api/workflow-builder/lookup/node/output-schema` | 📦 | |
| POST | `/api/workflow-builder/lookup/node/aggregation-metadata` | 📦 | |
| POST | `/api/workflow-builder/lookup/resources` | 📦 | |
| POST | `/api/workflow-builder/lookup/start-schema/` | 📦 | |
| POST | `/api/workflow-builder/lookup/runtime-connections-schema/` | 📦 | |
| POST | `/api/workflow-builder/lookup/{run,user,env,alert}-variables-schema` | 📦 | four variants |
| POST | `/api/workflow-builder/lookup/error-schema` | 📦 | |
| POST | `/api/workflow-builder/lookup/applications/` | 📦 | |
| POST | `/api/workflow-builder/collect-slot-schema` | 📦 | |
| POST | `/api/workflow-builder/node/automap` | 📦 | auto-map fields between steps |
| POST | `/api/workflow-builder/node/suggestions` | 📦 | next-node suggestions |
| GET | `/api/workflow-builder/node/resources` | 📦 | |
| GET | `/api/workflow-builder/webhook-url` | 📦 | |
| GET | `/api/workflow-builder/webhook-trigger-url` | 📦 | likely the URL for a `WEBHOOK` trigger — see §19 |

---

## 6. Workflow execution & runs

### `POST /api/test-workflow/initiate-test/{workflowId}` — Run a workflow
✅ UAT

Starts a run with an input payload. Despite the name, **it executes against real systems** —
the Oracle and HTTP calls in verified runs were genuine round trips.

**Request**

| Field | Type | Req | Notes |
|---|---|---|---|
| `payload` | object | ✅ | inputs matching the START node's `inputs.setup` schema |
| `type` | string | ✅ | `"MOCK"` |
| `workflowDefinition` | object | ✅ | the full definition **without `id`** — can be unsaved |

```json
{ "payload": { "customerId": "CUST-12345", "maxRows": 10 },
  "type": "MOCK",
  "workflowDefinition": { "name": "...", "version": 3, "nodes": [...], "edges": [...], "settings": {...} } }
```

**Response** — 200 `{ "runId": "<id>" }`. The run is asynchronous; poll
status next.

**Notes**
- Because the definition travels inline, you can test a graph you have not saved.
- Very large graphs (~60+ heavy nodes) can **time out the HTTP call** while the run still
  starts. Verify by reading results, not by the response. (another tenant)
- This is the **test** runner. How to invoke a *deployed* workflow from outside is open (§19).

### `POST /api/aggregation?entityType=WORKFLOW_EXECUTION&group=TEST_WORKFLOW_EXECUTION` — Run status
✅ UAT · ✅ another tenant

**Request**
```json
{ "entityType": "WORKFLOW_EXECUTION", "group": "TEST_WORKFLOW_EXECUTION",
  "projections": [ {"name":"ID"}, {"name":"STATUS"}, {"name":"EXECUTION_TIME"},
                   {"name":"START_TIME"}, {"name":"END_TIME"}, {"name":"FAILED_NODES"},
                   {"name":"START_NODE_OUTPUT"} ],
  "filter": { "op": "IN", "field": "ID", "values": ["<runId>"] },
  "page": { "limit": 5, "offset": 0 } }
```
To list runs of one workflow: filter `{"op":"IN","field":"WORKFLOW_ID","values":["<wfId>"]}`
and sort `[{"field":"START_TIME","order":"DESC"}]`. The UI also filters
`CONCURRENT_EXECUTION IN [false]`.

**Response**
```json
{ "objects": [ { "columns": {
    "ID": "<id>", "STATUS": "COMPLETED", "EXECUTION_TIME": 395,
    "START_TIME": 1789797991130, "END_TIME": 1789797991525,
    "START_NODE_OUTPUT": { "customerId": "CUST-12345", "maxRows": 10 },
    "DEPLOYED_WORKFLOW_ID": "s_<id>.../3/Khf8HC...=",
    "ROOT_EXECUTION_INSTANCE_ID": "...", "PARENT_EXECUTION_INSTANCE_ID": "...",
    "OTEL_TRACE_ID": "9e6bb8b5db1aa6d60f103176d3441eba", "RUN_TIME_TYPE": "TEST",
    "FAILED_NODES": ["n_code"], "DEBUGGED": false } } ],
  "type": "AGGREGATION_RESPONSE" }
```

| Projection | Meaning |
|---|---|
| `STATUS` | `COMPLETED`, `FAILED` observed. `CANCELLED` / `TIMED_OUT` **assumed**, not seen |
| `FAILED_NODES` | node ids that failed — present on `FAILED` |
| `START_NODE_OUTPUT` | echoes the input payload |
| `DEPLOYED_WORKFLOW_ID` | the snapshot actually run |
| `OTEL_TRACE_ID` | OpenTelemetry trace id |

**Notes**
- Projection names are **UPPERCASE**.
- ⚠️ The id filter differs by tenant — see §18: `field:"ID"` (UAT) vs `field:"fields.id"` (another tenant).
- A `COMPLETED` status only means no node threw. Assert on the output payload.

### `POST /api/lookup?ByKeys=TEST_WORKFLOW_VARIABLE` — Node inputs/outputs of a run
✅ UAT · ⚠️ see §18 for another tenant

Reads what a node actually received and produced. **This is how you verify a run.**

**Request**
```json
{ "type": "ByKeys", "lookupType": "TEST_WORKFLOW_VARIABLE",
  "keys": [ "<runId>.<runId>.n_out", "<runId>.<runId>.n_sql" ],
  "options": { "startTime": <START_TIME - 10000>, "endTime": <END_TIME + 10000>,
               "workflowId": "<workflowId>" } }
```
Key = `{rootExecutionId}.{executionInstanceId}.{nodeId}`; for a top-level run both ids
equal the `runId`. `startTime`/`endTime` are epoch ms bracketing the run.

**Response**
```json
{ "response": { "objects": {
    "<runId>.<runId>.n_sql": [
      { "type": "inputs",  "nodeId": "n_sql",
        "payload": { "sql": "SELECT 'CUST-12345' AS CUSTOMER_ID, SYSDATE AS AS_OF FROM DUAL" } },
      { "type": "outputs", "nodeId": "n_sql",
        "id": "<runId>/<runId>/n_sql/outputs",
        "payload": { "rows": [ { "CUSTOMER_ID": "CUST-12345", "AS_OF": "2026-09-19 06:54:34" } ],
                     "rowsCount": 1, "rowsAffected": 0 } } ] },
  "type": "MAPPED_HITS" } }
```

| Entry `type` | Contains |
|---|---|
| `inputs` | node inputs **with templates already resolved** — shows exactly what ran |
| `outputs` | node outputs, or an error object `{errorCode, cause:{...}, message}` on failure |
| `state` | runtime state, e.g. `{ "iteration": 3 }` on a `LOOP` |

### `POST /api/workflow-runs/node-executions` — Per-node timings
👁 UAT

Grouped per node: `STATUS`, `ENTRY_TIME`, `EXIT_TIME`, `EXECUTION_TIME`, `SKIPPED`,
`EXECUTION_INSTANCE_ID`, `ROOT_EXECUTION_INSTANCE_ID`, `PARENT_EXECUTION_INSTANCE_ID`.
Body wraps an aggregation query:
```json
{ "aggregationQuery": { "entityType": "WORKFLOW_NODE_EXECUTION", "group": "TEST_WORKFLOW_EXECUTION",
    "projections": [ { "name": "CURRENT_NODE_ID", "projections": [
        { "name": "CURRENT_NODE_ID", "aggregationFunction": "GROUP" },
        { "name": "ENTRY_TIME", "aggregationFunction": "MAX" },
        { "name": "STATUS", "aggregationFunction": "MAX_BY", "additional": { "AGGREGATE_BY": "ENTRY_TIME" } } ] } ] } }
```

### `POST /api/workflow/execute/node?name={registeredName}` — Named internal automation
⚠️ UAT · another tenant

Executes a **registered internal automation by name**. It is **not** a generic "run any
connector action" endpoint.

```json
{ "id": "getIndexRecommendationsForWorkflow",
  "context": { "appName": "standard_entities",
               "resourceName": "standard_entities_get_index_recommendations_for_workflow" },
  "inputs": { "includeOnlyMissingIndexes": true, "workflowId": "<id>" } }
```

Calling it with an arbitrary connector action returns **500 `forbidden datasource: not
found`**. Use a real workflow + `initiate-test` for connector actions.

Registered names observed in UI traffic:

| Name | Purpose | Status |
|---|---|---|
| `fetchUserPreferences` | UI preferences | 👁 |
| `fetch_records` | generic record fetch (saved views, etc.) | 👁 |
| `WorkflowScore` | best-practice score → `{score, totalChecks, passedChecks, success}` | 👁 |
| `getIndexRecommendationsForWorkflow` | index hints → `{result:{workflowIndexRecommendations:[]}}` | 👁 |
| `call_automation` | starts the prompt-to-automation copilot | 👁 |
| `fetch_ai_workflow_case_id`, `CopilotLookup`, `fetch_current_case`, `update_case_additional` | copilot internals | 👁 |
| `GetAllSessions`, `GetTraceTimeline`, `TraceTimelineDetails` | observability — see §11 | ✅ |

### Other execution endpoints

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/api/workflow/execute/node/sse` | 👁 UAT | server-sent-events stream used by the copilot. **Do not** clone/buffer the stream client-side — it stalls the session ("lost track of your active connection session") |
| POST | `/api/workflow/cancel/execution/` | 📦 | |
| POST | `/api/workflow/re-trigger-execution` | 📦 | |

---

## 7. Connections

### `GET /api/connection` — List all connections
✅ UAT

**Response** — 200 `{ "objects": [ ... ], "hasMore": false }`. **Every** connection in the
tenant (7,775–7,787 on UAT).

```json
{ "id": "<id>", "appName": "oracledb", "name": "OracleDB Server",
  "active": true, "projectId": "...", "options": {}, "userInput": { "<redacted>": "..." },
  "captureFailures": false, "standard": false, "version": 0,
  "ownerUserId": 0, "createdTime": 0, "modifiedTime": 0, "lcName": "..." }
```

**Notes**
- ⛔ **No server-side filter on this endpoint.** `?appName=`, `?app=`, `?appNames=`, `?filter=`,
  `?active=` are all ignored, and it is slow enough to exceed a 45 s client timeout.
  **Use `POST /api/aggregation?entityType=Connection&group=STANDARD` instead** (below) — it
  filters server-side in ~50 ms and does not return secrets.
- 🔴 **`userInput` contains secrets in clear** (`password`, `authToken`). Redact before
  logging or returning anywhere.
- **Names are not unique** (three different connections are all `RDQA-OracleDB-PRY`). Find a
  connection by the host/service in `userInput`, not by name.
- Match `appName` to the node name; prefer `active: true`.

### `GET /api/connection/{connectionId}` — One connection
✅ UAT

**Errors** — 500 `{"rootCauseMessage":"CONNECTION with id X not found","assetClass":"CONNECTION","errorCode":5002}`.

### `POST /api/lookup?ByQuery=CONNECTION` — Search connections by name
✅ another tenant

The fast alternative to pulling all connections.
```json
{ "type": "ByQuery", "lookupType": "CONNECTION", "query": "the author", "fields": ["name"],
  "options": { "appName": "mdm_by_unifyapps" }, "page": { "limit": 20, "offset": 0 } }
```

### `POST /api/aggregation?entityType=Connection&group=STANDARD` — Find connections (server-side)
✅ UAT

The Connections Manager list uses this. Filters on `appName`, `active`, `oUId`, `name`, `tags`.
```json
{ "entityType": "Connection", "group": "STANDARD", "includeTotalHits": true,
  "filter": { "op": "AND", "values": [
      { "field": "appName", "op": "EQUAL", "values": ["github"] },
      { "field": "active", "op": "EQUAL", "values": [true] } ] },
  "projections": [{"name":"id"},{"name":"name"},{"name":"appName"},{"name":"oUId"},{"name":"cTm"}],
  "sorts": [{"field":"cTm","order":"DESC"}], "page": { "limit": 30, "offset": 0 } }
```
**Response** — aggregation envelope; `totalHits` 56 for `github` on UAT; ~50 ms. No `userInput`.

### `GET /api/applications/{appName}?fields=authSpec,iconUrl,displayName,name,refreshable,includeOptions` — Connector auth form
✅ UAT

`authSpec.input` is a `SCHEMA_AND_LAYOUT` JSON Schema describing the connection `inputs`
(Custom HTTP: `name, requestType, authType, baseUrl, headersList, sslVerify,
requestTimeoutInSecs, connectionType, groupId, …`). Auth-type options come from
`POST /api/lookup?ByQuery=CUSTOMER_AUTH` `{options:{appName, auths:[{type,label}]}}` 👁.

**Also returns** `refreshable` (true ≈ OAuth with refresh → the user must click
*Authorize*; there is no API path around it) and `authSpec.externalDocUrl`, the public docs
page (`https://www.unifyapps.com/docs/unify-integrations/{slug}`; the slug is usually but not
always the `appName` — `openai` → `open-ai`). ✅ UAT.

⛔ **Empty body for internal nodes.** `custom_http_endpoint` returns **200 with a zero-length
body** — it is a platform node and has no connection form. Guard the JSON parse. Note the
pair: `custom_http_endpoint` = ad-hoc HTTP, no connection; `custom_http_application` = a
connector with a saved authenticated base URL (45 connections on UAT).

`authType` is usually **not** an inline enum — hence the `CUSTOMER_AUTH` lookup. A few
connectors do inline it: `openai` → `["TOKEN","COMPLIANCE"]`, `mcp_servers` →
`["TOKEN","NO_AUTH","BASIC","OAUTH","OAUTH_DCR","CREDENTIALS"]`. Verified required fields:
`snowflake` name/authType/domain/databaseName/schemaName/warehouseName · `sftp`
name/authType/host/port/username · `openai` domain/name/authType/authToken · `slack`,
`github`, `hubspot`, `gmail` name/authType only.

### `POST /api/connection/input/test?appName={appName}` — Test connection inputs
✅ UAT

Same body as create (below). **204** = success; the UI shows *Test connection successful*.

### `POST /api/connection/input?appName={appName}` — Create connection
✅ UAT

```json
{ "name": "<uc>_http_connection", "authType": "CUSTOM",
  "inputs": { "name": "<uc>_http_connection", "requestType": "HTTP",
              "authType": "CUSTOM", "baseUrl": "https://jsonplaceholder.typicode.com",
              "headersList": [], "sslVerify": true, "requestTimeoutInSecs": -1,
              "connectionType": "DIRECT", "tags": [],
              "rateLimitConfig": {"enabled": false}, "circuitBreakerConfig": {"enabled": false} },
  "options": { "rateLimitConfig": {"enabled": false}, "circuitBreakerConfig": {"enabled": false} },
  "tags": [] }
```
**Response** — 200, the connection (`id` 24 hex, `active: true`, `userInput` echoed). Created
`<id>` on UAT. `inputs` follow the app's `authSpec`. OAuth apps need the
user to click *Authorize* in the UI — do not attempt to script it.

### `POST /api/connection` — Create connection (bare)
⚠️ another tenant

Creating an `mdm_by_unifyapps` UDM connection by hand fails with
`No Value found in filter with field: sourceConnectionId` — a context graph creates its own
(§12). For ordinary connectors use `POST /api/connection/input?appName=` above.

**Connection config notes**
- Oracle **EBS**: `appName: "oracledb"`, `serviceName` = the **PDB**,
  `isCDBDatabase: false`. Pointing at the CDB gives `ORA-01017` (APPS is PDB-local).

---

## 8. Entities (generic CRUD)

Agents, tasks, tools, prompts, context-graph records and more are all **entities**, sharing
one CRUD surface keyed by `entityType`.

### `POST /api/entity` — Create
✅ UAT · another tenant

**Request**

| Field | Type | Req | Notes |
|---|---|---|---|
| `entityType` | string | ✅ | e.g. `ai_agent`, `e_action_ai_agent`, or an ECG `unifiedEntityId` |
| `properties` | object | ✅ | the entity's content |
| `tags` | string[] | | ⚠️ **top level only** — inside `properties` it 500s |

```json
{ "entityType": "e_topic_ai_agent", "tags": ["<TAG>"],
  "properties": { "name": "Customer Lookup", "aiAgentId": "e_...", "enabled": true } }
```

**Response** — 200, entity envelope with a new `e_...` id (ECG records use the primary-key
value as id). Server fills defaults (e.g. tools get `enabled: false` unless set).

**Errors**

| Status | Message | Cause |
|---|---|---|
| 500 | `Non Empty Validations ... add additionalProperties tags` | `tags` placed inside `properties` |

### `GET /api/entity/{entityType}/{id}` — Read
✅ UAT · another tenant

`GET /api/entity/{id}` without the type is ⛔ 405. Some types are singletons readable
without an id: `GET /api/entity/e_ai_agent_settings` ✅ returns the settings entity.

### `POST /api/entity/{entityType}` — List
✅ UAT

⚠️ **This lists — it does not create.** Posting a create body here returns a page of
existing entities and writes nothing.

**Request** — `{ "page": { "limit": 50, "offset": 0 } }`

**Response** — `{ objects, hasMore, cursor, type }`.

**Paging:** ⚠️ **offset-based.** Feeding `cursor` back silently re-returns page 1, so a
cursor loop yields duplicates. Increment `offset`; stop on `hasMore === false`.

### `POST /api/entity/update` — Update
✅ UAT

```json
{ "id": "<id>", "entityType": "e_action_ai_agent",
  "properties": { ...full properties, modified... }, "version": 0 }
```
Send the **full** `properties` and the **current** `version`. Response: entity, version +1.

### `POST /api/entity/action/saveAndDeploy` — Publish
✅ UAT

Publishes an entity (used for agents). Send the **whole entity object** as read, plus notes.

```json
{ ...entity from GET /api/entity/ai_agent/{id}..., "deploymentNotes": "V1 via API" }
```

**Response** — entity with `deploymentState: { deployedAt, deployedBy, entityVersion, version }`.

**Errors**

| Status | Message | Cause |
|---|---|---|
| 500 | `Non Empty Validations in Validating entity ai_agent with validationResult required name` | sent a partial body (e.g. `{id, entityType}`) or `properties.name` missing |

### Entity types reference

| entityType | What | Aggregation group |
|---|---|---|
| `ai_agent` | agent | ENTITY |
| `e_topic_ai_agent` | agent **Task** | ENTITY |
| `e_action_ai_agent` | agent **Tool** / capability | ENTITY |
| `e_prerequisite_task_ai_agent` | prerequisite action | ENTITY |
| `e_ai_agent_settings` | tenant agent settings (singleton) | ENTITY |
| `ai_agent_deployment` | channel deployment | ENTITY |
| `ai_agent_llm_model` | model registry | ENTITY |
| `e_ai_agent_team`, `e_ai_team_task` | multi-agent teams | ENTITY |
| `prompt` | reusable prompts (26 on UAT) | ENTITY |
| `knowledge_set`, `knowledge`, `knowledge_source` | RAG | ENTITY |
| `EntityType` | the type registry itself (17,791 on UAT) | STANDARD |
| `WorkflowDefinition` | workflows | STANDARD |
| `KNOWLEDGE_GRAPH_NODE` / `_EDGE` / `_SOURCE` | ECG schema | STANDARD |
| `<unifiedEntityId>` | an ECG node's records | — |
| `e_interface` | application (config or code) — id is a slug | ENTITY (§22) |
| `e_component` | app page / module / template component | ENTITY (§22) |
| `e_data_source` | app data source (authorises execute-node) | ENTITY (§22) |
| `e_theme`, `e_page_template`, `e_custom_component`, `e_i18n_namespace` | app theme / page templates / custom React components / translations | ENTITY |
| `EntityType` (`ENTITY_TYPE` in lookups) | Objects Manager objects | STANDARD (§24) |
| `Connection` | connections | STANDARD (§7) |
| `<objectId>` (e.g. `<uc>_scratch_task`, or `obj_<5 chars>` when generated) | an object's records | ENTITY (§24) |

Discover any type's fields with `POST /api/aggregation/metadata` (§10).

---

## 9. AI agents, tasks, tools

Built entirely on §8's entity CRUD. **A tool is a call into a workflow** — the same
`callables_call_automation` contract as a `CALL_WORKFLOW` node.

### Agent — `ai_agent`
✅ UAT

**Create** via `POST /api/entity`:
```json
{ "entityType": "ai_agent",
  "properties": { "name": "a sample agent", "agentType": "CONVERSATIONAL",
                  "instructions": "You help fleet operators ..." } }
```
`properties.name` is required for publish. Publish with `saveAndDeploy` (§8).

**Key properties**

| Property | Meaning |
|---|---|
| `name` | required |
| `instructions` | the system prompt (string) |
| `agentType` | `CONVERSATIONAL` |
| `role`, `goal` | shown in the UI Instructions tab; enrichers use `role: "Enricher"` |
| `responseGenerationSettings.answerGenerationModel` | answer model |
| `responseGenerationSettings.outputSchema` | structured output — the contract for enricher agents |
| `responseGenerationSettings.{tone,style,format}` | response shaping |
| `topicExecutionSettings.{topicSelectionModel,topicExecutionModel,topicAsTool}` | task routing |
| `preProcessingSettings`, `indexingSettings` | RAG behaviour |
| `longTermMemorySettings.enabled`, `contextManagement.*` | memory / context |
| `graphModelId` | links a context graph (does **not** by itself enable graph search — §12) |
| `defaultTools` | map of booleans; ⚠️ capabilities are really tool rows — see below |
| `mcpEnabled`, `visibility.type`, `evalSettings`, `loggingSettings` | misc |

### Task — `e_topic_ai_agent`
✅ UAT

```json
{ "entityType": "e_topic_ai_agent",
  "properties": {
    "name": "Vehicle Status",
    "description": "Use this task when the user asks about a vehicle's status or telemetry.",
    "instructions": [ "Confirm the vehicle id.", "Call VehicleLookup.", "Summarise in plain English." ],
    "aiAgentId": "<id>",
    "enabled": true, "isAppConnector": false, "runTimeConnectionEnabled": false,
    "governanceConfig": {} } }
```
- `description` = **when** (what the router matches on). `instructions` = **how** — an
  **array of strings**, rendered as numbered steps.
- Optional `modelSelectionConfig` overrides the model per task.
- At runtime `SetTopic` is a real tool call; the task's `instructions[]` arrive as its
  tool result (visible in traces, §11).

### Tool — `e_action_ai_agent` (workflow-backed)
✅ UAT

```json
{ "entityType": "e_action_ai_agent",
  "properties": {
    "name": "VehicleLookup",
    "description": "Look up a vehicle record by vehicle id.",
    "aiAgentId": "<id>",
    "topicId": "GLOBAL",
    "context": { "appName": "callables", "resourceName": "callables_call_automation" },
    "inputs": { "automationId": "<id>", "version": "-1",
                "synchronous": true, "runtimeConnections": {}, "parameters": {} },
    "enabled": true,
    "approvalConfig": { "enabled": true, "storeUserApprovalPreference": false } } }
```

| Field | Notes |
|---|---|
| `topicId` | `"GLOBAL"` = agent-wide (Tools tab); a task id = scoped to that task only |
| `inputs.automationId` | the workflow to call — must be **deployed** |
| `inputs.version` | `"-1"` = latest deployed |
| `inputs.parameters` | `{}` lets the model fill args from the workflow's `inputs.setup` schema |
| `enabled` | ⚠️ **defaults to `false`** — the tool silently never fires |
| `approvalConfig` | human-in-the-loop gate; shows real parameter values + Deny / Approve Once. **Deny genuinely blocks the write** ✅. Put it on every write tool; republish after changing |

Server-applied defaults also seen: `deferToolLoading`, `enableToolSearch`,
`excludeInputOutputFromTrace`, `isStandardAction`, `runTimeConnectionEnabled`.

#### Per-user OAuth — runtime user connections
✅ UAT — a connector tool with `context: {appName, resourceName}`, **no** `connectionId`
and `runTimeConnectionEnabled: true` makes each signed-in user connect their **own** account: the chat
shows a "Connectors that could help → Connect" card once, the platform keeps that user's connection
(`ownerUserId` = the user) and reuses/refreshes it on later chats. Nobody else's calls resolve to it.
- **Secrets are never readable**: `GET /api/connection/{id}` returns the connection with the secret masked
  (`"token": "__UNIFYAPPS_GARBAGE_CONSTANT__…"`); tokens live in the connection store, not in any data
  object, so object-level access to `<uc>_*` data never exposes them.
- ⛔ Never bind a personal connector (Gmail, Drive, Calendar, Fireflies) to a fixed `connectionId`, and
  never copy a token into an object or workflow variable: a fixed connection runs as its owner for every caller.
- ⚠️ **Connection metadata is tenant-visible and permissions come from platform roles.** `aggregation Connection`
  lists every user's connections (name, `appName`, `oUId`). `lookup ENTITY_PERMISSIONS {entityType:"Connection"}`
  on a connection owned by someone else returned `DECRYPT, EDIT, DELETE, SHARE…` for a broad (admin-level) role
  (UAT). Masking in `GET /api/connection/{id}` is not access control: restrict DECRYPT/EDIT on
  connections to admins via platform roles, grant OAuth scopes read-only, and let users revoke at the provider.
- Agent memory: `longTermMemorySettings: {enabled: true, userGlobalMemoryNotNeeded: false}` + `defaultTools.saveInstantMemoryTool: true`
  (per-user long-term memory; team agents have no `defaultTools`). ✅ UAT.

### Capability — `e_action_ai_agent` with `isStandardAction: true`
✅ UAT

Built-in capabilities are **tool rows**, not agent fields:
```json
{ "entityType": "e_action_ai_agent",
  "properties": { "name": "generateChartTool", "aiAgentId": "<agent>",
                  "isStandardAction": true, "enabled": true, "topicId": "GLOBAL" } }
```
Standard names seen: `generateChartTool`, `renderArtifact`, `loadSkill`, `webSearch`,
`createExcel`, `createDocx`, `createDocxOrPdf`, `createPDF`, `createPPTX`,
`createFlowDiagram`, `createFile`, `analyseFile`, `documentVision`, `deepResearch`,
`generateImageTool`, `executeCodeTool`, `ingestKnowledge`, `companyKnowledge`, `planTool`,
`todo_tool`, `summaryTool`, `requestClarification`, `clarifyFromUser`, `qa`,
`informationNotFoundTool`, `generatePublicFileUrl`, `allowKnowledgeControl`,
`CompleteDocumentContext`, `generateAndEditEmail`, `Build_App`.

⚠️ **`generateChartTool` needs `renderArtifact` too**, or the agent prints a table while
claiming it drew a chart. Charting is expensive (one request measured ~291 K tokens, ~$0.94).

### Recipe — agent with workflow-backed tools
✅ UAT

1. Build → save → check violations → **deploy** each workflow (§4). CALLABLE trigger with a
   clear `inputs.setup` — that schema becomes the tool's argument contract.
2. Smoke-test each with `initiate-test`; assert on the `n_out` payload (§6).
3. `POST /api/entity` → `ai_agent`.
4. `POST /api/entity` → one `e_topic_ai_agent` per journey.
5. `POST /api/entity` → one `e_action_ai_agent` per workflow, `enabled: true`, right `topicId`.
6. `POST /api/entity/action/saveAndDeploy` with the full agent entity; verify by snapshot (§47.1).

## 10. Search: aggregation & lookup

### `POST /api/aggregation?entityType={t}&group={g}` — Universal query
✅ UAT · another tenant

The platform's general search. `entityType` and `group` go in **both** the query string and
the body. Optional query param `name=table_block` (👁, used by list screens).

**Request** — send the **complete** body; partial bodies 500 with no useful message.
```json
{ "entityType": "WorkflowDefinition", "group": "STANDARD", "includeTotalHits": true,
  "filter": { "op": "AND", "values": [
      { "op": "EQUAL", "field": "d", "values": [false] },
      { "op": "ICONTAINS", "field": "lcName", "values": ["fleet"] } ] },
  "sorts": [ { "field": "cTm", "order": "DESC" } ],
  "projections": [ {"name":"id"}, {"name":"name"}, {"name":"trigger"}, {"name":"deployed"},
                   {"name":"appsUsed"}, {"name":"tags"}, {"name":"oUId"}, {"name":"cTm"} ],
  "page": { "limit": 30, "offset": 0 } }
```
A filter may also be a single flat condition: `{"field":"graphId","op":"EQUAL","values":["..."]}`.

**Groups**

| group | entityTypes |
|---|---|
| `STANDARD` | `WorkflowDefinition`, `EntityType`, `KNOWLEDGE_GRAPH_NODE/EDGE/SOURCE` |
| `ENTITY` | `e_*` entity types, `ai_agent_deployment`, `e_platform_asset_settings`, ... |
| `TEST_WORKFLOW_EXECUTION` | `WORKFLOW_EXECUTION`, `WORKFLOW_NODE_EXECUTION` |

**Operators seen:** `AND`, `OR`, `EQUAL`, `NOT_EQUAL`, `IN`, `ICONTAINS`, `EXISTS`,
`MISSING`, `GT`, `GTE`, `LT`, `LTE`.

**WorkflowDefinition projections:** `id`, `name`, `trigger` (`CALLABLE`, `SCHEDULED`,
`Application`, ...), `deployed`, `appsUsed`, `tags`, `standard`, `pId`, `oUId`, `cTm`,
`mTm`, `lMBy`. Filter fields: `d`, `standard`, `lcName`.

**Errors / gotchas**

| Symptom | Cause |
|---|---|
| 500, no message | body incomplete — send all of entityType, group, filter, sorts, projections, page |
| 500 `projections is null` | `projections` is **mandatory** for `group: ENTITY` |
| 500 `Invalid group: STANDARD and type: e_topic_ai_agent` (5004) | wrong group for the type |
| unrelated rows returned | ⚠️ `ICONTAINS` on `lcName` does **not** filter entity types — list and filter client-side |
| no `name` column | entity projections return only `id` / `tags` — read names via entity list |

Scale on UAT: 31,703 workflows · 28,994 tools · 2,872 tasks.

### `POST /api/aggregation/metadata` — Field list for any type
✅ another tenant · 👁 UAT

```json
{ "group": "ENTITY", "entityType": "ai_agent_deployment" }
```
Returns every field for the type. **The fastest way to learn an unknown schema.**

### `POST /api/lookup?ByKeys={TYPE}` / `?ByQuery={TYPE}` — Keyed / text lookup
✅ UAT · another tenant

```json
// by keys
{ "type": "ByKeys", "lookupType": "USER", "keys": ["<userId>"] }
// by query
{ "type": "ByQuery", "lookupType": "CONNECTION", "query": "the author", "fields": ["name"],
  "options": { "appName": "mdm_by_unifyapps" }, "page": { "limit": 20, "offset": 0 } }
```

| lookupType | Status | Use |
|---|---|---|
| `TEST_WORKFLOW_VARIABLE` | ✅ UAT | node inputs/outputs of a run (§6) |
| `CONNECTION` | ✅ another tenant | find a connection by name |
| `USER` | 👁 | user records (`email`, `name`, `userGroups`, `ssoLogin`, `state`, `userSessionType`) |
| `ENTITY_PERMISSIONS` | 👁 | `options: {entityType}`, `keys: [id]` |
| `ENTITY`, `UNIFIED_ENTITY`, `UNIFIED_ENTITY_MODEL` | 👁 another tenant | ECG and entity lookups |
| `TAG`, `NODE_BUILDER`, `TRIGGER_TYPE`, `s_project` | 👁 | UI list rendering |
| `WorkflowDefinition` | ⛔ | 500 — use aggregation instead |

`POST /api/lookup/bulk` is also used by the UI (👁).

### `POST /api/global-search` — Global search
⚠️ UAT

`{ "query": "user role matrix" }` → `{"hasMore":false}` with no results. Body shape not
understood yet. `/api/global-search/recent-searches` is 👁.

---

## 11. Observability & traces

Reads an agent's sessions and the **exact message array sent to the model**. Called through
the named-automation executor.

| Call | Returns | Status |
|---|---|---|
| `POST /api/workflow/execute/node?name=GetAllSessions` | sessions | ✅ UAT |
| `POST /api/workflow/execute/node?name=GetTraceTimeline&fetchTraceDetail={traceId}` | span tree | ✅ UAT |
| `POST /api/workflow/execute/node?name=TraceTimelineDetails&fetchTimelineDetails={spanId}` | span input/output incl. full `message[]` | ✅ UAT |

Request bodies are not yet recorded in full — the reliable method so far is to drive the UI
(`/p/0/ai-agents/{id}/observability`) and read the `TraceTimelineDetails` response from
network capture.

What traces reveal:
- Tool results verbatim — an empty `""` result is immediately visible.
- `SetTopic` is a real tool call carrying the task instructions.
- The platform appends a synthetic user turn `"Lets continue.."` after an assistant turn,
  causing an extra generation (the source of trailing "anything else?" filler).

---

## 12. Enterprise Context Graph

Verified on **another tenant** across three graph builds unless marked. Deep detail
is in `context-graph.md`.

### Critical ordering rules

1. **Publish the graph before loading records.** Records written to a `DRAFT` graph go to
   the entity store and are **never projected** into the Cypher layer — no error.
2. **Make every property `STRING`.** Typed properties store fine but the node projects
   **zero vertices**. Convert in Cypher (`toFloat(...)`).
3. **Records never link themselves.** Record edges are written only by the MDM connector
   inside a workflow (§16).

### Graph

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/api/context-graph` | ✅ | create — body `{name, description}` |
| GET | `/api/context-graph/{graphId}` | ✅ | header |
| POST | `/api/context-graph/update/{graphId}` | ✅ | |
| POST | `/api/context-graph/{graphId}/publish` | ✅ | `DRAFT` → `LIVE` |
| GET | `/api/context-graph/templates` | ✅ | prebuilt templates |

**Create response:** `{ id, status: "DRAFT", nodeCount: 1, unifiedEntityModelId: <same as id>, version: 1 }`.
Side effects: a default **`ecg_grant`** node (leave it), and an `mdm_by_unifyapps` **UDM
connection** named `<graph name> UDM Connection` with `userInput.unifiedEntityModelId =
<graphId>`. Use that connection for every MDM step; never hand-create one.

### Nodes (types)

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/api/context-graph/nodes` | ✅ | create |
| GET | `/api/context-graph/nodes/{nodeId}` | ✅ | incl. `properties[]`, `entityMetadata`, `recordTitleFormat` |
| POST | `/api/context-graph/nodes/update/{nodeId}?version={n}` | ✅ | ⚠️ version in the **query string**; body = full node |
| POST | `/api/context-graph/nodes/bulk-update-node-positions` | ✅ | canvas layout |
| GET | `/api/context-graph/nodes/templates` | ✅ | node templates |

**Create node request**
```json
{ "graphId": "<graphId>", "name": "Customer", "category": "core", "description": "...",
  "iconUrl": "account-executive", "nodePosition": { "x": 0, "y": 0 },
  "recordTitleFormat": "{{ mdm.field.customer_name }}",
  "properties": [
    { "id": "customer_id", "displayName": "Customer Id", "dataTypeInfo": { "type": "STRING" },
      "primaryKey": true, "required": true, "unique": false, "pii": false,
      "filterable": false, "sortable": false, "searchable": false,
      "graphQueryable": true, "standard": false } ] }
```
**Response:** node with server `id` **and** `unifiedEntityId` (the Cypher label and the
record `entityType`). `dataTypeInfo.type` values: `STRING`, `DOUBLE`, `BOOLEAN`, `DATE`,
`INTEGER`, `JSON`, `ARRAY` — **use STRING only** (rule 2).

**Errors:** `500 version is required for node update` → version belongs in the query string.
`500 Please delete data before updating entity schema` → type changes need zero records.

### Edges (types)

| Method | Path | Status |
|---|---|---|
| POST | `/api/context-graph/edges` | ✅ |
| GET | `/api/context-graph/edges/{edgeId}` | ✅ |
| POST | `/api/context-graph/edges/update/{edgeId}` | ✅ |

```json
{ "graphId": "<graphId>", "label": "WORKS_AT", "fromNodeId": "<nodeId>", "toNodeId": "<nodeId>" }
```
A type-level edge only **declares** a relationship may exist; it materialises nothing.

### Records

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/api/entity` | ✅ | create — `{entityType: <unifiedEntityId>, properties:{...}}`; id = primary-key value |
| POST | `/api/entity/update` | ✅ | |
| GET | `/api/entity/{unifiedEntityId}/{recordId}` | ✅ | raw record incl. `mdmRecordMetadata` |
| POST | `/api/context-graph/{graphId}/nodes/{unifiedEntityId}` | ✅ | list — `{includeTotalHits, page:{limit,offset}}`; flat props + `_ua_recordTitle`, `labels`, `modelId` |
| GET | `/api/context-graph/{graphId}/unifiedEntity/{ue}/records/{recordId}` | ✅ | record + `edges[]` |
| GET | `/api/context-graph/{graphId}/unifiedEntity/{ue}/records/{recordId}/graph?depth=1` | ✅ | neighbourhood |

Record edge shape (on read):
```json
{ "direction": "OUTGOING", "entityType": "<other ue>", "isDangling": true,
  "recordId": "TKT-002", "recordTitle": "AXN-256 - Duplicate Customer Profiles",
  "relationshipId": "HAS_TICKET", "relationshipLabel": "HAS_TICKET",
  "properties": { "edgeLabel": "HAS_TICKET", "id": "90::ueA::ACC-001::90::ueB::TKT-002" } }
```
`isDangling: true` = no matching type-level edge; still traverses normally.

`mdmRecordMetadata` carries field-level lineage: `sourceDetails[{fieldName, sourceAppName,
sourceId, stageRecordId, modifiedTime}]`, `contributingSources[]`,
`associatedStagingRecordIds[]`, `dataQualityResult`, `modelId`, `stagingMetadata`.

### Querying (OpenCypher)

Queried through the `mdm_by_unifyapps_execute_opencypher_query` workflow action (§16), not a
REST endpoint. Node label = `unifiedEntityId` (backticked); properties prefixed `_pr_`.
```cypher
MATCH (c:`<customer_ue>`)
WHERE toLower(coalesce(c.`_pr_name`, '')) CONTAINS 'presidential'
MATCH (c)-[:HAS_DEAL]->(d:`<deal_ue>`)
RETURN d.`_pr_deal_name` AS deal, labels(d) AS labels, d.modelId AS modelId LIMIT 50
```
Verify projection after the first record of each type: `MATCH (n) RETURN DISTINCT labels(n)`.

### Sources (connector ingestion)

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/api/context-graph/sources` | ✅ | `{graphId, appName, connectionId, name}`; auto-fills `destinationConnectionId`; starts Draft |
| GET | `/api/context-graph/sources/{sourceId}` | ✅ | incl. `objectDiscoveryConfigRefs[]` |
| POST | `/api/context-graph/sources/{sourceId}/publish` | 📦 | |
| GET | `/api/context-graph/sources/{sourceId}/objects/fetch-selected?limit=200&offset=0` | ✅ | per-object `objectSchema`, `enrichedObjectSchemas[]`, `schemaMappings[]` |
| POST | `/api/context-graph/sources/{sourceId}/objects/bulkUpdate` | ⛔ | 200 but `{"data":0}` — writes nothing |
| GET | `/api/context-graph/sources/{sourceId}/object-discoveries` | ✅ | |
| POST | `.../object-discoveries/scope-configs/bulk-save` | ✅ | scope (e.g. Slack `channelList`) |
| POST | `.../object-discoveries/discovery-configs/bulk-save` | ⚠️ | 200, but the **enricher binding does not persist** |
| GET | `/api/context-graph/sources/{sourceId}/schema-mappings` | ✅ | returns `{"objects":[]}` |
| POST · PUT · PATCH | `/api/context-graph/sources/{sourceId}/schema-mappings` | ⛔ 405 | **Map step is wizard-only** |
| POST | `/api/context-graph/sources/{sourceId}/schema-mapping/automap` | ⛔ 405 | |
| POST | `/api/context-graph/sources/{sourceId}/transformations/save` | 📦 | |
| GET | `/api/context-graph/sources/{sourceId}/transformations/group-by-source-field` | 📦 | |
| GET | `/api/context-graph/sources/applications/{appName}/objects` | ✅ | objects a connector exposes |
| POST | `/api/context-graph/sources/applications/{appName}/objects/{objectId}/details?connectionId=` | ✅ | body `{}`; object schema (nested for raw, flat for enriched) |
| GET | `/api/context-graph/sources/applications/{appName}/settings` · `/disabled-steps` | 📦 | |
| POST | `/api/context-graph/sources/objects/describe` | ✅ | `{connectionId, objectId, sourceConfigId}` → destination `fields[]` |
| GET | `/api/context-graph/sources/discoverers/{method}/{agentId}/{n}/schema` | ✅ | e.g. `AGENT/.../0` → `{outputSchema:{...}}` |
| GET | `/api/context-graph/sources/enrichers/{method}/{agentId}/{n}/schema` | ✅ | flattens `results[].items.properties` |
| GET | `/api/context-graph/sources/app/{appName}/resource/{resourceId}` | 📦 | |

**Scope config (Slack) request**
```json
{ "objectDiscoveryConfigEntries": [
    { "objectId": "Message", "displayName": "Message",
      "scopeConfig": { "scopeActionId": "slack_index_channels_and_chat",
                       "actionInputs": { "token_type": "user_token", "channelList": ["C0BD6AWDTLH"] } } } ] }
```
⚠️ An **empty `channelList` means every channel**. Always set it. HubSpot has no
record-level scope at all.

### ECG entity-type fields (from `/api/aggregation/metadata`)

- **`KNOWLEDGE_GRAPH_NODE`**: `id graphId name lcName category color iconUrl description
  properties propertiesCount edgeCount recordCount nodePosition unifiedEntityId standard tags
  spaceId v cTm mTm oUId pId lMBy lPUBy lPUOn`
- **`KNOWLEDGE_GRAPH_EDGE`**: `id graphId label lcName description fromNodeId toNodeId
  entityRelationshipIds[] standard tags spaceId v cTm mTm oUId pId lMBy lPUBy lPUOn`
- **`KNOWLEDGE_GRAPH_SOURCE`**: `id graphId name lcName appName connectionId status
  lastSyncTimeEpochMillis standard tags spaceId v cTm mTm oUId pId lMBy lPUBy lPUOn`

---

## 13. Files

### `POST /api/file/signed-url?preview=true&expiryTime=1` — Signed download URL
✅ another tenant

```json
{ "fileDetails": { "fileType": "application/pdf", "name": "AXN-MSA.pdf", "size": 54396,
    "source": "connector_streaming_uploads/90/6/<uuid>_AXN-MSA.pdf",
    "sourceType": "CLOUD_STORAGE", "ua:type": "FILE" } }
```
**Response:** `{ "url": "/api/file/download/__UNIFY_ENCR_AWS__V0__..." }`.

### `GET /api/file/download/{encryptedRef}&isPublic=false&preview=true` — Download
✅ another tenant

Returns the file bytes. Use the `url` from `signed-url` verbatim and append the flags.

---

## 14. Other observed platform endpoints

UI plumbing seen in live traffic. Not needed for building, recorded for completeness.

| Method | Path | Status | Notes |
|---|---|---|---|
| GET | `/api/mqtt/connectionDetails?resourceTypes=PLATFORM` | 👁 | realtime channel (MQTT over WebSocket) — needed by the copilot |
| GET | `/api/notification/unopenedCount` | 👁 | |
| POST | `/api/collaborators/connect` | 👁 | 204 — builder presence |
| POST | `/api/collaborators/active-users` | 👁 | → `{activeSessions:[{sessionId, userId}]}` |
| GET | `/api/entity/deployed/e_interface/{id}` | 👁 | deployed UI interface |
| POST | `/api/entity/deployed/embedded-entities/e_component` | 👁 | UI components |
| GET/POST | `/api/entity/deployed/...` (`bulk-fetch-snapshots`, `child-entities`, `snapshot/`, `entity-dependency`) | 📦 | deployed-entity family |
| POST | `/api/entity/restore/deployed/` | 📦 | |

---

## 15. Confirmed dead ends

Tested and **do not work**. Do not retest without a reason.

| Method | Path | Result | Use instead |
|---|---|---|---|
| any | `/api/login`, `/api/auth/login`, `/api/user/login`, `/api/v1/auth/login` | 404 | `/auth/workflow/execute/node?name=emailAndPassLoginRequest` |
| any | `/api/authenticate`, `/api/auth/token`, `/api/oauth/token`, `/api/session`, `/api/auth/me` | 404 | — |
| GET | `/api/workflow-definition` | 405 | aggregation, group `STANDARD` |
| GET | `/api/entity/{id}` (no type) | 405 | `/api/entity/{type}/{id}` |
| GET | `/api/entity/ai_agent` (no id) | 405 | `POST /api/entity/ai_agent` to list |
| POST | `/api/entity` with an existing `id` | 500 Mongo `E11000 duplicate key` | `POST /api/entity/update` |
| PUT · POST | `/api/entity/{type}/{id}` | 405 | `POST /api/entity/update` |
| PUT | `/api/entity/{type}` | 405 | |
| POST | `/api/entity/action/save`, `/api/entity/action/update` | 405 | `POST /api/entity/update` |
| POST | `/api/entity/save` | 500 `ENTITY_TYPE with id save not found` | |
| any | `/api/connections` | 404 | `/api/connection` |
| GET | `/api/connection?appName=` (and `app`, `appNames`, `filter`, `active`) | filter ignored | client-side filter / `lookup?ByQuery=CONNECTION` |
| any | `/api/tag`, `/api/tags`, `/api/entity-tag` | 404 | top-level `tags` on create; read via aggregation projection |
| GET | `/api/workflow-builder/nodes/{name}` | 404 | `/api/workflow-builder/node/{name}` |
| GET | `/api/workflow-builder/node/{n}/resource` | 404 | `/node/{n}/resources` |
| GET | `/api/workflow-builder/node/{n}/resources/{r}` | 404 | `/node/{n}/resource/{r}` |
| GET | `/api/workflow-builder/node/{n}/resource/{r}/schema` · `/input-schema` | 404 | `/node/{n}/resource/{r}` → `input.schema` |
| GET | `/api/workflow-builder/resource/{r}`, `/node-resource/{r}`, `/resources?nodeName=` | 404 | |
| GET | `/api/workflow-builder/node/resource?nodeName=` | 200 empty body | |
| POST | `/api/workflow/execute/node?name=<connector action>` | 500 `forbidden datasource: not found` | a real workflow + `initiate-test` |
| POST | `/api/lookup?ByQuery=WorkflowDefinition` | 500 | aggregation |
| POST | `/api/global-search/search` | 404 | |
| POST · PUT · PATCH | `/api/context-graph/sources/{id}/schema-mappings`, `.../schema-mapping/automap` | 405 | the UI wizard |
| POST | `/api/context-graph/sources/{id}/objects/bulkUpdate` | 200 `{"data":0}` — no-op | the UI wizard |
| POST | `/api/connection` for an `mdm_by_unifyapps` UDM connection | 500 `No Value found in filter with field: sourceConnectionId` | the graph creates it |
| GET | `/api/entity-type/{id}`, `/api/entity-type/find/{id}`, `/api/entity-type/by-id/{id}` | 404 | `GET /api/entity-type?entityType={id}` |
| GET | `/api/entity-type?id={id}` | 500 | same |
| POST | `/api/lookup?ByKeys=EntityType` | 500 5004 `Lookup type not supported` | `lookup?ByKeys=ENTITY_TYPE` |
| POST | `/api/aggregation/metadata?entityType=e_interface&group=ENTITY` with `{}` | 204 empty | read the entity itself |
| POST | `/api/workflow/execute/node` calling a CALLABLE with no `id` | 500 `forbidden datasource: not found` | register an `e_data_source` (§22) |
| fetch | `http://127.0.0.1` from a UnifyApps page | blocked by CSP `connect-src` | read data through the browser tool, not out of the page |

---

## 16. Node action contracts

✅ UAT — one callable workflow compiled from a step list ran first time:
`storage_by_unifyapps_fetch_records` (two EQUAL filters, one templated) → `storage_by_unifyapps_count_records`
`{object_type, triggerInputCondition}` → `{{ .count }}` → `utility_by_unifyapps_run_sql_query_on_list`
`SELECT properties.category_id AS category, COUNT(*) AS n FROM {{ n_req.outputs.objects }} GROUP BY properties.category_id`
→ `{{ .result }}` rows → `if_else_condition` (`{{ n_req.outputs.total }}` GT 0, true body in group `n_chk@g1@y`) →
`loop_for_each` (body group `n_each@g1@l`, `{{ n_each.outputs.item.id }}`) with `storage_by_unifyapps_update_records`
by id query inside → STOP. Versions resolved from `GET /api/workflow-builder/node/{app}/resources` at build time. An
auto-generate primary key (`prefix:'KTT', startFrom:1001`, not in `required`) was filled by a create-record node as
`KTT_1001`.

Workflow steps are not REST endpoints, but they are the API surface you actually program
against. Each is identified by `context.{appName, resourceName, resourceVersion}`, configured
by `inputs`, and read back as `{{ n_<id>.outputs.<field> }}`.

### Node / edge model
✅ UAT

```json
{ "id": "n_sql", "type": "ACTION", "title": "Execute a SQL statement", "subTitle": "Oracle DB",
  "context": { "appName": "oracledb", "resourceName": "oracledb_execute_sql",
               "resourceVersion": 16523, "connectionId": "<id>", "type": "APPLICATION" },
  "inputs": { ... }, "groupId": "g1", "index": 2, "fallbackMode": "STOP", "skip": false }
```

| Field | Notes |
|---|---|
| `type` | `START`, `ACTION`, `STOP`, `IF_ELSE`, `LOOP`, `BREAK`, `DELAY`, `CALL_WORKFLOW` |
| `context.connectionId` | **inside `context`**, never at node level |
| `context.type` | `"APPLICATION"` on non-trigger nodes |
| `groupId` | scope: `{ownerNodeId}@{parentGroupId}@{y\|n\|l\|error}`, concatenating as it nests |
| `fallbackMode` | `STOP` (fail run) · `MANUAL` (take the `error` edge) · `CONTINUE` (⚠️ see §18) |

Edges: `{ fromNodeId, toNodeId, type, id: "{type}@{from}@{to}", name? }`.

| Edge type | `name` | Meaning |
|---|---|---|
| `next` | — / `"no"` / `"loopback"` | normal flow / else / back to loop |
| `if` | `"yes"` | true branch of `IF_ELSE` |
| `loop` | — | into a `LOOP` body |
| `error` | `"error"` | failure path (needs `fallbackMode: MANUAL`) |

### Triggers (START nodes)

| resource | `trigger.type` | inputs | Status |
|---|---|---|---|
| `callables` / `callables_from_automation` | `CALLABLE` | `setup` = JSON Schema of the workflow's **input parameters** | ✅ UAT |
| `schedule` / `schedule_default` | `SCHEDULED` | `cron: "INTERVAL"\|"CRON"`, `interval`, `frequency: MINUTES\|HOURS\|DAYS`, `sequential` | ✅ UAT |
| (event) | `EVENT` | app event triggers, e.g. `oracledb_on_new_event` | 📦 |
| (webhook) | `WEBHOOK` | | 📦 |

CALLABLE outputs mirror `setup`: `{{ n_in.outputs.customerId }}`. Trigger `context` carries no
`type` field.

### Response — `callables_return_to_automation` (type `STOP`)
✅ UAT

`inputs.result` = any scalar or nested object, returned verbatim with templates resolved.
Every path of a CALLABLE workflow must end in one — the validator enforces it.

### Invoke an AI Agent from a workflow — `ai_agents_by_unifyapps_invoke_agent`
✅ VERIFIED UAT (an invoice-exception build, tenant orbit.uat.unifyapps.com) — ran end to end: START node context `{appName:'callables', resourceVersion:3109, resourceName:'callables_from_automation'}`, STOP node context `{appName:'callables', resourceVersion:3111, resourceName:'callables_return_to_automation', type:'APPLICATION'}`, edges as a top-level array (`fromNodeId`/`toNodeId`, not inline per-node). Invoke Agent node resourceVersion resolved via `GET /api/workflow-builder/node/ai_agents_by_unifyapps/resources` → 1783. String interpolation for `userQuery`/`messageId` must embed `{{ n_in.outputs.field }}` inside the JSON string literal — string concatenation with `+` sends the literal placeholder text, not the value. `ai_agent` entity create requires `tags` at the top level of the POST body, not inside `properties` (500 'additionalProperties tags' otherwise). Round trip ~15-22s for a class-D agent with one tool call; agent narrates tool selection in `agentResponses` (auditable) then returns the tool's JSON verbatim when instructed to.
Groovy Code-node gotchas found while building the tool workflow: `groovyx.net.http.HTTPBuilder` does not resolve (remove unused import); `new Date().format(pattern)` fails — use `new Date().toInstant().toString()` instead.
✅ VERIFIED UAT (a build tool, workflows `<id>` and the per-project agent probe) — **reading the agent's answer downstream**: `{{ n_x.outputs.agentResponses }}` is a list whose THOUGHT messages carry `additional.internalMessageType`; the answer is the LAST element without it, and it may arrive wrapped in a ```json fence. A Groovy node that takes `responses` (typed `array`), keeps `it.text && !it.additional?.internalMessageType`, takes the last, strips the fence and parses it with `new groovy.json.JsonSlurper().parseText(...)` (allowed in the sandbox) returns `[text, messageId, json]`; `{{ n_x_ans.outputs.result.json.priority }}` then feeds a create-record node. Data for the agent: `utility_by_unifyapps_to_json_string` `{object: "{{ n_f.outputs.objects }}"}` → `{{ n_j.outputs.result }}` embedded in `userQuery`. A **templated `aiAgentId`** (`"{{ n_in.outputs.agent_id }}"`) works — one probe workflow can ask any agent. A unique `messageId` per call: `"<wf>-<step>-{{ n_t.outputs.t }}"` with a create-variables node `t = "=ROUND((NOW()-DATE(1970,1,1))*86400000,0)"`. Turn times 7–12 s (Vertex Sonnet 5). initiate-test returned its runId normally for these runs. An agent with a guardrail denied topic answers the guardrail's blocked message through this node as well.
The synchronous (`async:false`) node that lets a workflow call a UnifyApps AI Agent and wait for its answer — how an
atomic agent  is invoked from its sub-workflow.

| | |
|---|---|
| node `type` | `CALL_INTERFACE_WORKFLOW` |
| `context` | `{appName:'ai_agents_by_unifyapps', resourceName:'ai_agents_by_unifyapps_invoke_agent', resourceVersion}` (1783 on UAT today — resolve at runtime: `GET /api/workflow-builder/node/ai_agents_by_unifyapps/resources`) |
| `inputs.callableInterfaceId` | `'__ua__invoke_ai_agent_by_unifyapps'` (the node's defaults also carry `defaultFallbackWorkflowId 68050ca67df58855654804a0`, `triggerWorkflowWithRuntimeType 'IN_MEMORY'`) |
| `inputs.parameters` | `aiAgentId` (required), `userQuery`, `sessionId` (same id = same conversation context), `messageId` (**a replay of the same id is answered from the original turn and not billed again** — use the idempotency key), `taskExecutionModel` (per-call `ai_agent_llm_model` id override), `skipApprovalBeforeToolExecution`, `userEmailAddress`, `attachments[]`, `ai_agent_default_tools {enableKnowledge, webSearch}`, `externalKnowledges[]`, `citations`, `routineId`, `spaceId` |
| output | `agentResponses[] {text, messageId, messageCreatedTime, choices[], coPilotBlocks[], additional}`, `publicResponse[] {text, choices[]}`, `citations[]`, `sessionId`, `usage {cost, inputTokens, outputTokens, llmCalls}` |

Interface definition: `POST /api/lookup?ByKeys=CALLABLE_INTERFACE {type:'ByKeys', lookupType:'CALLABLE_INTERFACE',
keys:['__ua__invoke_ai_agent_by_unifyapps']}`. The same app also has `…_cancel_stream`, `…_resume_agent_stream` and
chat-queue actions. Sibling node `workflow_agent_ask_ai_agent` ("create a new mini-agent on the fly") is a different
thing: an inline agent, not a registered one.

✅ VERIFIED UAT (a build engine, workflow `<uc>_gfd_triage` `<id>`, test run
`<id>`) — the same node built by the build engine's plan step `kind: "agent"`: a Groovy node builds `userQuery`
(one line of what to do + `INPUT (JSON):` + the input map as JSON), the Invoke Agent node carries only `aiAgentId`, `userQuery`
and `skipApprovalBeforeToolExecution: true` (no `messageId`, no `sessionId`), a Groovy node reads `agentResponses`. The run
completed in 7.6 s; the agent (one Task, no tools, Opus 4.8) answered `{status, value, confidence, confidence_basis,
abstain_reason}` as plain JSON, and `{{ n_x_p.outputs.result.json.category }}` fed the record update. A node-level
`async: false` sent on save is not kept on the stored node (read back `undefined`) and the call is synchronous all the same.
The platform fills `inputs.automationId` (`68050ca67df58855654804a0`, the node's default fallback workflow) by itself.

### Sub-workflow / agent tool — `callables_call_automation`
✅ UAT

| Input | Notes |
|---|---|
| `automationId` | target workflow id (deployed) |
| `version` | `"-1"` = latest deployed |
| `synchronous` | `true` waits for the result |
| `parameters` | must match the target's `inputs.setup` |
| `runtimeConnections` | `{}` |

Used by `CALL_WORKFLOW` nodes and by `e_action_ai_agent` tools alike.

### Oracle — `oracledb_execute_sql`
✅ UAT

| Input | Req | Notes |
|---|---|---|
| `sql` | ✅ | may contain templates and `:binds` |
| `params` | with binds | JSON Schema declaring each bind (name + type) |
| `record` | with binds | the bind **values**, as templates |
| `objectSourceResourceName` | | `"oracledb_execute_sql_metadata"` — enables typed `rows` |
| `response_schema` | | column schema matching the SELECT |
| `performAsync`, `record_loader` | | |

**Outputs:** `rows[]`, `rowsCount`, `rowsAffected`.

⚠️ Bind traps (the most expensive gotchas found):
- `params` **and** `record` are both required; missing either → `ORA-17041: Missing IN or OUT parameter`.
- `record` templates must reference **this** workflow's START node id — copied nodes carry
  a foreign id that silently resolves to nothing.
- A `record` **missing one key binds NULL silently** — diff SQL `:binds` against `record` keys.
- **OUT binds (`o_*`) must not be in `record`.**
- 🔴 **PL/SQL OUT binds are never returned** — an anonymous block returns
  `{"rows":[],"rowsCount":0,"rowsAffected":0}`. Follow every write with a verification
  `SELECT` node and return that.

23 `oracledb` actions exist, incl. `oracledb_select_rows_using_custom_sql`,
`oracledb_insert_record`, `oracledb_update_rows`, `oracledb_upsert_row`,
`oracledb_delete_rows_in_batch`, `oracledb_execute_stored_procedure`,
`oracledb_list_schemas`, `oracledb_list_tables_from_schema`, and CDC triggers
`oracledb_on_new_event` / `_on_update_event` / `_on_delete_event`.

### HTTP — `custom_http_endpoint_execute`
✅ UAT

Needs **no connection**.

| Input | Notes |
|---|---|
| `baseUrl`, `path`, `httpMethod` | required in practice |
| `headersList`, `queryParamsList`, `pathParamsList` | arrays |
| `bodySchema`, `body_loader` | request body |
| `authType`, `connectionType` | |
| `requestTimeoutInSecs`, `sslVerify`, `enableProxy`, `httpVersion` | |
| `responseSchema`, `errorResponseSchemas` | |

**Outputs:** `status` (int), `result` (parsed body).
Variants: `_execute_graphql`, `_execute_soap`, `_execute_multipart`, `_execute_streaming`.

### Code — `code_by_unifyapps_groovy`
✅ UAT

```json
{ "input":  { "type":"object", "required":["km"], "properties": { "km": {"type":"string","title":"km"} } },
  "output": { "type":"object", "required":["recommendation"], "properties": { "recommendation": {"type":"string","title":"recommendation"} } },
  "code": "return [\"recommendation\": \"Service now - odometer at \" + km + \" km\"];",
  "parameters": { "km": "{{ n_in.outputs.mileage }}" },
  "compile_static": false, "captureStdOutput": false }
```
- `input` declares names; `parameters` binds values; code reads them as bare variables.
- **Outputs nest under `result`**: `{{ n_code.outputs.result.recommendation }}`.

⚠️ `code_by_unifyapps_javascript`: a top-level `return` is rejected with *"Script rejected by
sandbox validation: Line 1, column 1: Invalid return statement"*. Correct JS form unknown
(§19). Other code actions: `_python`, `_java`, `_csharp`, `_execute_code_snippets`,
`_bubblewrap` (sandbox), `_playwright`.

### Auth — `auth_by_unifyapps_create_user_session` (the "run as the caller" executor)
✅ UAT — a run-as-caller workflow `<id>`, three workflows created end to end

```json
{ "context": { "appName": "auth_by_unifyapps", "resourceName": "auth_by_unifyapps_create_user_session", "resourceVersion": 2013 },
  "inputs": { "sessionDuration": 900000 } }
```
- Inputs: `sessionDuration` (ms), optional `userId` (a TEST user; leave empty = **the caller**).
  Output: `{{ n_session.outputs.sessionId }}`.
- A following Groovy node replays it as `Cookie: _at=<sessionId>` against the tenant's own
  `/api/*` and everything it creates is **owned by the calling user** (`oUId` = caller) — no
  service account, no stored password. Verified writes: `POST /api/workflow-definition` +
  `saveAndReturnViolations` + `deploy`, `POST /api/entity` (`ai_agent`) + `saveAndDeploy`,
  `POST /api/entity-type` + `/update`.
- Called from a code app through a `callables_call_automation` data source (`version: "-1"`,
  `synchronous: true`) the caller is the signed-in app user, so a plan step builds as the person
  who approved it. Ledger row + `Respond to automation` `{ok, platform_id, asset_type, name, detail, error}`.
- ⚠️ Claude's own permission gate refuses to *create or deploy* such a workflow and its data source
  (in auto **and** manual mode); the user runs the installer in their signed-in console. Reads,
  wiring, and calling it from the app are not gated.

### Control flow

| resource | type | inputs | Status |
|---|---|---|---|
| `if_else` / `if_else_condition` | `IF_ELSE` | `operator`, `filters: [{property, filter:{operator, value}}]` | ✅ |
| `loop` / `loop_while` | `LOOP` | `condition: {operator, filters}`, `captureIterations` | ✅ |
| `break` / `break` | `BREAK` | `loop: "<loop node id>"` | ✅ |

- `IF_ELSE` wiring: `if` edge (`yes`) into the body; `next` edge (`no`) to the rejoin node;
  the body's last node also points at the rejoin node.
- `LOOP` wiring: `loop` edge in; `next` (`loopback`) from the body's last node back; `next` out.
  Outputs `{result, index}`, state `{iteration}`.
- `BREAK` **still needs an outgoing `next` edge** to the enclosing condition's rejoin node,
  or validation fails.

### Variables

| resource | inputs |
|---|---|
| `variable_by_unifyapps_create_variables` | flat map `{ "counter": "0" }` → `{{ n_v.outputs.counter }}` |
| `variable_by_unifyapps_update_variables` | `{ "variables": [ { "source": "{{ n_v.outputs.counter }}", "value": "=SUM({{ n_v.outputs.counter }},1)" } ] }` |

### MDM — `mdm_by_unifyapps` (context graph write/read)
✅ another tenant

All steps use the graph's UDM connection as `context.connectionId`.

| Action | Inputs | Outputs |
|---|---|---|
| `add_edge_to_graph` | `modelId` (graphId), `primaryEntityType`, `primaryEntityId`, `associatedEntityType`, `associatedEntityId`, `label`, `updateIfPresent` | `{success, fromNodeId, toNodeId}` |
| `execute_opencypher_query` | `modelId`, `query`, `limit` (1–1000, default 100), `offset`, `skipRBAC`, `outputSchema` | query rows |
| `execute_opencypher_update` | Cypher write | 📦 |
| `create_staging_records`, `apply_data_matching_rules`, `apply_data_quality_rules`, `find_by_sql` | MDM golden-record pipeline | 📦 |

Entity types are `unifiedEntityId`s; entity ids are primary-key values. ~60–70 edge nodes per
workflow run reliably in 25–40 s.

### Storage — `storage_by_unifyapps`
✅ another tenant

| Action | Inputs |
|---|---|
| `create_record` | `object_type: <ue>`, `record: {...}` — ⚠️ fields under **`record`**, not top level |
| `fetch_records` | `object_type`, `page {paginateBy:"OFFSET", limit, offset}`, `numberOfRecordsToFetch:"MULTIPLE"`, `triggerInputCondition {operator:"AND", filters:[{property:"id", filter:{operator:"EQUAL", value}}]}` ✅ UAT (templated `object_type` works) |
| `create_record` (raw) | `useRawPayload:true`, `writeThroughSessionVariables:false`, `object_type`, `rawPayload: {{ node.outputs.result.payload }}` (a Map) ✅ UAT — output = the created entity (`id` = autonumber) |
| `update_record_by_id` (raw) | `useRawPayload:true`, `upsert:false`, `writeThroughSessionVariables:false`, `object_type`, `recordId`, `rawPayload` = **full** record (replaces it; merge the current `properties` first) ✅ UAT |

### ECG pipeline — `ecg_by_unifyapps`
📦 another tenant

`run_discovery`, `translate_raw_record`, `apply_enrichment`, `publish_record` — **all require a
published source config**, so they do not bypass the wizard.

### Connector specifics
✅ another tenant

- **HubSpot:** search operator `CONTAINS` is rejected → use `CONTAINS_TOKEN`. Always request
  `hs_object_id`. `hubspot_get_deal` supports `propertiesWithHistory: ["dealstage"]`. No
  "record updated" trigger — poll `hs_lastmodifieddate`.
- **Slack:** bot tokens read only joined channels; `token_type: "user_token"` reads what the
  user sees. `slack_list_conversation_history` = top-level only; replies need
  `slack_list_conversations_replies`. `slack_get_user_info_by_id` takes **`user`**;
  `slack_get_conversation` takes **`channelId`**; history takes **`channel`**.

---

### Caller identity inside workflows ✅ UAT
A CALLABLE workflow run from an app data source or an agent tool gets **no trusted caller identity**:
the Groovy binding holds only the node inputs, and the trigger outputs carry only
`__internals__ {m, s, c, p}` (mode, page slug, channel, platform). Templates may reference nodes only
(`{{ $user }}` etc. → *"Node referenced in input no longer exists"*). No workflow node looks up
platform users or roles (`auth_by_unifyapps` = sessions/MFA/IdP; `platform_by_unifyapps` = run
events). What IS trusted: storage writes run **as the caller** — records get `lastModifiedBy` = the
caller's platform user id — so platform object permissions (role → EDIT/VIEW per entity type) are the
hard enforcement, and `lastModifiedBy` is a trustworthy audit. App-side roles come from
`GET /api/user-context?includeRoles=true` (`user.roles[].name`).

## 17. Error catalogue

| Message (substring) | Where | Cause → fix |
|---|---|---|
| `Invalid username or password` (401) | login | bad creds, wrong IdP id, `firstLogin` set, or MFA |
| `app_not_configured_for_user` | Google SAML | account not in the SSO app → use a local account |
| `getNodes() is null` | create workflow | send `nodes` (a stub is fine) |
| `This automation has a trigger which expects response` | save violation | a path lacks a `STOP`; a `BREAK` lacks an outgoing edge |
| `forbidden datasource: not found` | `execute/node` | not a registered automation → use a workflow |
| `Script rejected by sandbox validation: Invalid return statement` | JS code node | use Groovy |
| `ORA-17041: Missing IN or OUT parameter at index` | Oracle node | `record` missing, or its templates reference a foreign START id |
| `ORA-17003: Invalid column index` | Oracle node | a `:word` inside a **string literal** (e.g. `'09:00'`) is parsed as a bind — build it with `CHR(58)` |
| `ORA-201xx: <sentence>` | Oracle node (PL/SQL) | a business rule raised with `RAISE_APPLICATION_ERROR`; surfaced verbatim deep in the failure payload |
| `ORA-01017` | Oracle connection | pointed at the CDB; EBS APPS is PDB-local |
| `Non Empty Validations ... required name` | saveAndDeploy | send the full entity; set `properties.name` |
| `Non Empty Validations ... add additionalProperties tags` | create entity | move `tags` to the top level |
| `E11000 duplicate key error` | `POST /api/entity` | you sent an existing id → use `/api/entity/update` |
| `ENTITY_TYPE with id save not found` | `/api/entity/save` | not an endpoint |
| `CONNECTION with id X not found` (5002) | connection | bad id |
| `Invalid group: STANDARD and type: e_topic_ai_agent` (5004) | aggregation | entities use `group: ENTITY` |
| `projections is null` | aggregation | `projections` mandatory for `ENTITY` |
| `version is required for node update` | ECG node update | version in the query string |
| `Please delete data before updating entity schema` | ECG node update | type changes need zero records |
| `No Value found in filter with field: sourceConnectionId` | create connection | don't hand-create the UDM connection |
| `The system lost track of your active connection session` | copilot | realtime channel broken — don't buffer the SSE stream; the in-app browser may block MQTT |
| `forbidden datasource : invalid input` | `execute/node` with an `id` | an input differs from the data source's stored value where it is not `{{templated}}`, or a stored input was omitted → send the full stored inputs, change only templated fields |
| `Non Empty Validations ... property X invalid; oneOf fail` | record create/update | value not in the field's `oneOf` |
| `Non Empty Validations ... required X` | record create/update | missing required field — updates replace the whole record, send all fields |
| `Non Empty Validations ... add additionalProperties X` | record create | field not in the object schema |
| `E11000 duplicate key ... CUSTOMER_ENTITY_<n>.<object>` | record create | primary-key value already used (record id = PK) |
| `Lookup type not supported: EntityType` (5004) | lookup | use `ENTITY_TYPE` |
| `e_component with id e_global_<app> not found` (5002) | embedded-entities | app has no global page yet — it is created with the first page |
| HTML instead of JSON | any | session expired → re-login |

---

## 18. Discrepancies and how they were settled (Orbit UAT)

### D1 — Reading node outputs
- `POST /api/lookup?ByKeys=TEST_WORKFLOW_VARIABLE` returns node inputs/outputs for many runs, but
  returns `inaccessibleObjects` (nothing) for runs of workflows **created over the API** (§35). Verify
  such a workflow through its data source, or re-run the definition inline with `initiate-test`, or
  write a small debug record from the workflow and read it back.

### D2 — `fallbackMode: CONTINUE`
- ✅ **Settled (§41.10):** `CONTINUE` does not continue after a failed connector action, and
  `MANUAL` + `error` edge did not route it either (run via an app data source). Design one unit of
  work per run. `MANUAL` + an `error` edge is verified for ordinary node failures in a test run.

### D3 — Run-status filter field
- `filter: {"op":"IN","field":"ID","values":[runId]}` ✅ on UAT. The form
  `{"op":"AND","values":[{"field":"fields.id","op":"EQUAL","values":[runId]}]}` with projection
  `RUN_ID` was verified on another tenant; confirm on Orbit UAT before relying on it.

### D4 — `find-nodes-with-connections` vs the Connection aggregation
✅ UAT

`GET /api/workflow-builder/find-nodes-with-connections` listed 304 connectors; querying
`POST /api/aggregation?entityType=Connection&group=STANDARD` per `appName` returned
`totalHits: 0` for 25 of them (`apitemplate_io`, `amazon_kms`, `base_ai`, `gchat`,
`microsoft_business_central`, `qualtrics`, `spotify`, `square`, `rootly`, `totango`,
`unicommerce`, …).

Most likely cause: the node list counts connections the aggregation filters out — deleted
ones, or ones in a project the caller cannot see. **Resolution rule:** the node list is a
cheap pre-filter, the aggregation is the answer. Not yet confirmed against a tenant admin
view.

### D5 — `initiate-test` and call-workflow nodes
- **§38:** "`initiate-test` cannot run a call-workflow node at all".
- **a build tool (2026-09-26, UAT):** master workflows made of `CALL_WORKFLOW` nodes COMPLETED through
  `initiate-test` — runs `<id>` (50 s) and `<id>` (53 s), each
  node's sub-workflow ran.
- **To resolve:** the §38 case used a stale `callables_call_automation` version (3124); a build tool runs
  resolved the version from the tenant. Re-test one master with a resolved version through both
  paths before relying on either statement. Until then: verify a master by the records its run
  writes (a records check), whichever way it was started.

---

## 19. Open questions

| # | Question | Notes |
|---|---|---|
| 1 | Invoke a deployed CALLABLE workflow from outside | ✅ register an `e_data_source` and call `execute/node` with its `id` (§22). API Manager endpoints are the external route — untested |
| 2 | **Dynamic-schema connectors** | `input.dynamic: true` actions (Salesforce objects, picklists) — what extra lookup runs? Configure once in the UI and read the saved definition back |
| 3 | Create a connection | ✅ `POST /api/connection/input?appName=` (§7). OAuth still needs the person to click Authorize |
| 4 | **Correct JavaScript code-node form** | top-level `return` rejected; use Groovy |
| 5 | **Webhook trigger** end to end | `/api/workflow-builder/webhook-trigger-url` |
| 6 | Observability **request bodies** | currently captured from UI traffic |
| 7 | ECG **Map step via API** | 405 everywhere; wizard only |
| 8 | ECG `associatedEdgeMappings` shape | every live source had it empty |
| 9 | What enables built-in `search_knowledge_graph` | `graphModelId` + `defaultTools` insufficient |
| 10 | Knowledge / RAG, multi-agent teams, channel deployments | entity types known, payloads not |
| 11 | `/api/global-search` request shape | returns empty |
| 12 | Change Sets (move/export between environments) API | not captured |

## 20. UI routes

Useful for eyeballing what the API built.

| Route | Screen |
|---|---|
| `/p/0/automations` | automation list |
| `/p/0/automations/ai-create` | prompt-to-automation |
| `/p/0/automations/{id}/builder` | builder canvas |
| `/p/0/automations/{id}/test` · `/test/{runId}` | test runs |
| `/p/0/ai-agents/custom` | agent list |
| `/p/0/ai-agents/{id}/configuration/instructions` | system prompt |
| `/p/0/ai-agents/{id}/configuration/topics` | **Tasks** (label ≠ path) |
| `/p/0/ai-agents/{id}/configuration/actions` | **Tools** |
| `/p/0/ai-agents/{id}/configuration/tasks` | **Prerequisite Actions** |
| `/p/0/ai-agents/{id}/configuration/capabilities` | capabilities |
| `/p/0/ai-agents/{id}/configuration/{knowledge,skills,memory,ai-models}` | |
| `/p/0/ai-agents/{id}/configuration/{sensitive-information,hallucinations,content-filter,word-filter,denied-topics,blocked-messaging}` | guardrails |
| `/p/0/ai-agents/{id}/deployments` · `/observability` | channels · traces |
| `/p/0/context-graphs` · `/{graphId}?tab=nodes\|edges\|sources\|records` | context graphs |
| `/p/0/objects/custom` · `/p/0/objects/{objectId}/records` · `/schema` · `/activity` · `/settings` | Objects Manager |
| `/p/0/connections/all` · `/p/0/connections/create/{appName}` | Connections Manager |
| `/p/0/interfaces` · `/p/0/interfaces/{appId}/overview` · `/builder/{pageSlug}` · `/settings/users` | Applications |
| `/p/0/interfaces/custom-components` · `/template-components` · `/p/0/design-system` | app assets |
| `/p/0/solutions` | AI Solutions (groups assets per use case) |
| `/p/0/agent-governance/*` | governance, model registry, monitoring |
| `/settings/users` · `/settings/users/create/details` | user admin |

---

## 22. Applications — data sources and publish

An app is an `e_interface` entity (id is a slug); its pages are `e_component` entities; every data
call an app makes is an `e_data_source` entity. Pages and app UI are built by the app builder and
are out of scope here; this section keeps only what a data source needs.

### `POST /api/entity/e_component` — List an app's pages
✅ UAT — filter `properties.interfaceId` EQUAL appId (required, or 5011). The global page
`e_global_<appId>` is returned as a `PAGE`.

### `POST /api/entity/embedded-entities/e_component` — A page with its data sources
✅ UAT — `{entityId, allowedEntityTypes:["e_component","e_data_source","e_interface"]}`.
Deployed variant: `/api/entity/deployed/embedded-entities/e_component` (+ `excludeFields`), types `e_component_deployed`.

### `e_data_source` — create with `POST /api/entity`, run with `execute/node`
✅ UAT

```json
{ "entityType": "e_data_source", "properties": {
  "name": "ds_vehicle_telemetry", "type": "APPLICATION",
  "interfaceId": "<appId>", "interfacePageId": "e_global_<appId>",
  "context": {"appName":"callables","resourceName":"callables_call_automation","resourceVersion":3124},
  "inputs": {"automationId":"<deployed CALLABLE id>","version":"-1","runtimeConnections":{},
             "parameters":{"vehicleId":"{{vehicleId}}"},"synchronous":true},
  "dP": [{"p":"inputs.parameters.vehicleId"}], "dpOn": [],
  "advancedOptions": {"runBehaviour":"automatic","refetchOnWindowFocus":true,
                      "timing":{"runQueryOnPageLoad":false,"runQueryPeriodically":false}} } }
```

```json
POST /api/workflow/execute/node?name=ds_vehicle_telemetry&requestId=<dsId>
{ "context": {...same...}, "id": "<dsId>",
  "inputs": {"automationId":"...","version":"-1","runtimeConnections":{},
             "parameters":{"__internals__":{"m":"PREVIEW","s":"global-page-of-<appId>","c":"PLATFORM","p":"browser"},"vehicleId":"V-100"},
             "synchronous":true},
  "options": {} }
→ 200 { "executionInstanceId", "id", "lookupReferences": {}, "response": <STOP result> }
```

**Governance (✅ verified):** no `id` → `forbidden datasource: not found`; a changed
non-templated input (e.g. `automationId`) or an omitted stored input →
`forbidden datasource : invalid input`. `context` may be any workflow action — storage
(`storage_by_unifyapps_fetch_records`, `_create_record`, `_update_record_by_id`) is common. Blocks bind with `{{ <dsId>['data'][...] }}`.

### `POST /api/entity/e_interface/{appId}/deploy` — Publish
✅ UAT (captured from the UI's Publish click) — `{deploymentNotes}` → the app with
`deploymentState {deployedAt, deployedBy, deploymentNotes, entityVersion, version}`. The UI
first calls `POST /api/entity/entity-dependency` and `/api/entity/deployed/entity-dependency`
`{entityType:"e_interface", entityId}` 👁. Versions: `aggregation` on `EntitySnapshot` (STANDARD)
with `additional:{entityType, entityId}` 👁.

## 23. How app code calls the platform

App code (code apps and config apps alike) calls `POST /api/workflow/execute/node` with an
`e_data_source` id, anchored `interfacePageId: "e_global_<appId>"`. Objects use five
object-agnostic storage bindings (FETCH, FETCH_ONE, CREATE, UPDATE, and a delete binding the
fallback never uses); each automation gets its own `callables_call_automation` data source. App
code must never call `/api/entity` or `/api/aggregation`.

## 24. Objects Manager

Module id `ENTITY_TYPE`. An object is an `EntityType` (STANDARD); its records are entities of
that type. ~18,300 custom objects on UAT.

### `POST /api/entity-type` — Create object
✅ UAT — `{id, name, pluralName, description, metadata:{storeDetails:{store:"MONGO"}}, tags}`
→ the EntityType with defaulted `metadata`. UI store options: JSON (MONGO), Blob, Key Value,
Event, Vector, Analytics.

### `GET /api/entity-type?entityType={id}` — Read object
✅ UAT. Bulk: `POST /api/lookup?ByKeys=ENTITY_TYPE {type:"ByKeys", lookupType:"ENTITY_TYPE", keys}` ✅.
⚠️ UAT: an object that does not exist returns **200 with an empty body** — `r.json()`
throws "Unexpected end of JSON input". Read as text; empty = not found (§28).

### `storage_by_unifyapps_create_object` (workflow node) — what worked ✅ UAT
Inputs `{uniqueId, singularName, pluralName, description, store:"MONGO", schemaPayload:<JSON schema object>,
layoutPayload:{"ui:order":[…]}, metadataPayload}` created four objects with 9–11 typed fields (auto-generate
primary key with `autoGeneratedFieldDefinition`, `single-select` with `oneOf`, `date-time`+`epoch`) from a
Groovy step's output mapped as `'{{ n.outputs.result.schema }}'` (an object template resolves to the object).
Output `{success:true}`. ⚠️ `metadataPayload: {tags: '{{ …array… }}'}` did **not** tag the object (string
rendering); tag afterwards with `POST /api/entity-type/update` (`tags:[…]`) or pass a whole object template —
`metadataPayload: '{{ n.outputs.result.metadata }}'` with `metadata:[tags:[…]]` from Groovy (unverified).
Runs as the workflow's caller: `ownerUserId` = the user who invoked the data source.

### App data sources refuse any input-shape drift ✅ UAT
`forbidden datasource : invalid input` when a call to a registered `e_data_source` changes a non-templated
stored input (e.g. `numberOfRecordsToFetch: SINGLE` on a source registered `MULTIPLE`) or omits one (`upsert`,
`page`, `sortBy`). Reuse the exact stored inputs + the templated ones; the same id cannot serve two shapes.
Also: `storage_by_unifyapps_update_record_by_id` with `useRawPayload` needs the **full** record and rejects
keys that are not in the object schema (`additionalProperties:false`).

### `POST /api/entity-type/update` — Update schema / settings
✅ UAT — send the **full** object as read, with
`input: {type:"SCHEMA_AND_LAYOUT", schema:<S>, layout:{"ui:order":[...]}}` and
`schema: {dynamic:false, type:"SCHEMA", schema:<S>}`. `<S>` is JSON Schema; per-field flags
`primaryKey, uniqueKey, nameField, searchable, sortable, filterable`; formats `text, email,
date-time (+dateFormat:"epoch"), single-select (+oneOf | foreignKey:{reference:"ENTITY_ID:<obj>"}),
auto-generate (+autoGeneratedFieldDefinition:{prefix,startFrom})` — the server joins prefix and
counter with `_` (`prefix:"SZ"` → `SZ_1004`; `"SZ-"` → `SZ-_1003`), so never end a prefix with a
separator; a prefix change applies to new records only ✅ UAT. The server derives
`metadata.primaryKeyField / nameField / filterableFields / searchableFields / dateFields /
referenceKeys / autoGeneratedFields` from the flags. `version` increments.

### Records
✅ UAT — create `POST /api/entity {entityType:<obj>, properties}` (record id = PK
value); read `GET /api/entity/{obj}/{id}`; list `POST /api/entity/{obj}` with
`{filter:{op,field:"properties.x",values}, sorts, page}` (EQUAL, GT, IN verified); aggregate
`POST /api/aggregation?entityType={obj}&group=ENTITY` (fields `properties_x`); update
`POST /api/entity/update` with the **full** properties (partial → `required` error). Schema
validation enforces `required`, `oneOf`, `additionalProperties:false`.

### Listing objects
✅ `POST /api/aggregation?entityType=EntityType&group=STANDARD` with projections
`name, id, columns, tags, oUId, cTm, mTm, description, packaged, standard`; custom objects:
filter `standard` EQUAL false OR MISSING. Fields of one object:
`POST /api/lookup?ByQuery=ENTITY_FIELD {options:{group:"ENTITY", entityType}}` ✅.
⛔ UAT: filtering that listing on `id` with op `CONTAINS`, `LIKE`, `STARTS_WITH`, `REGEX` or
`PREFIX` answers **500** `{"errorCode":-1}`. To find a project's objects, take the ids from its repo
(seed/bootstrap scripts) and read each one with `GET /api/entity-type`.

## 24b. AI Solutions — the platform's native prompt-to-solution builder
✅ UAT (read-only survey)

**UI:** sidebar *AI Solutions* → `/p/0/solutions` (975 on UAT). A solution = "one problem statement, one linked
set of assets". Detail page `/p/0/solutions/{id}` (Overview · Insights · Versions · Settings; *Preview*;
*Open in builder*). Builder = `/p/0/solutions/{id}?chatId=new`: chat on the left ("Describe what you want to
build. The agent will plan it, then build it."), right pane tabs **Plan · Preview · Code · Data sources ·
Objects · Trace**, model picker ("Auto"), *Publish*. Several chats per solution (`chatId`).

**Entity:** `POST /api/entity/e_solution` (list) — `properties: {name, description, status: building|built,
globalPlan (markdown "build plan — N items — …"), planId, approvedPlanId, chatId, model, modelEntityId,
provider, vertexProject, connectionId, memory, linkedEntities:[{id, type, state, version}]}`; linked types seen:
`ENTITY_TYPE` (objects, ids `obj_xxxxx`), `e_interface` (apps, `app-xxxxx`), `WORKFLOW_DEFINITION`,
`CONNECTION`; `state` = `COMPLETED`. Plans are a separate entity type (id `e_…`), type name not found yet
(`e_plan`, `e_solution_plan`, `plan`, `e_ai_plan`, `e_build_plan` → 500).

**Workflow nodes** (`solution_by_unifyapps`): `save_solution` (create/update, fields above), `deploy_solution`
(deploys every linked entity then the solution; returns `deployedEntityVersion`), `save_solution_versions`,
`restore_solution {id, deployedVersion}`. So version control of a whole solution is native.

**Other first-party nodes worth knowing (no session needed — they run with platform identity):**
`storage_by_unifyapps_create_object {uniqueId, singularName, pluralName, store, schemaPayload, layoutPayload,
metadataPayload}` / `update_schema`; `routines_by_unifyapps_create_routine` (managed agent
from `agentConfig`); `git_by_unifyapps_*` (clone/edit/commit/push/bash — code apps server-side);
`auth_by_unifyapps_create_user_session {userId?, sessionDuration}` → `sessionId` ("current user, or a TEST
user when userId is set"); `auth_by_unifyapps_mint_agent_identity` (SPIFFE token);
`platform_tools_by_unifyapps_*` (node/resource discovery); `platform_by_unifyapps_on_pipeline_*` triggers.


## 25. Connectors SDK (custom connectors)
✅ UAT — a 5-action GraphQL connector was built and published this way.
UI route: **`/connectors/custom`** (sidebar *Enterprise Systems → Connectors SDK*), connector at
`/connectors/{defId}/{authentications|triggers|actions|settings}`. Aggregation entity type: `ConnectorDefinition` (group `STANDARD`).
UI route: **`/connectors/custom`** (sidebar *Enterprise Systems → Connectors SDK*), connector at
`/connectors/{defId}/{authentications|triggers|actions|settings}`. Aggregation entity type: `ConnectorDefinition` (group `STANDARD`).

| Step | Call | |
|---|---|---|
| Create connector | `POST /api/connector-builder/definition/basic` `{name, description, baseUrl, logo, categories}` | 👁 (UI) |
| Read connector | `GET /api/connector-builder/definition/{defId}` → `{auths[], baseUrl, enabled, version, …}` (no tags field) | ✅ |
| Add auth | `POST /api/connector-builder/definition/{defId}/auth?type=TOKEN` (`TOKEN`, `JWT`, `OAUTH`, `OAUTH1`, `BASIC`, `CUSTOM`, `AWS`) | 👁 (UI) |
| Update auth input schema | `POST /api/connector-builder/definition/update/{defId}/auth?type=CUSTOM&version={v}` body `{type:"CUSTOM", input:{type:"SCHEMA_AND_LAYOUT", dynamic:false, layout:{}, schema:{…JSON schema…}}}` → `{definition:{auths[…]…}}`, bumps `version` | ✅ UAT |
| Auth request (headers) | read `GET /api/connector-builder/request/{defId}/{TYPE}/auth` · update `POST /api/connector-builder/request/update/{defId}/{TYPE}/auth?version={v}` with the full object | ✅ |
| CUSTOM auth request (login call) | the object the UI saves: `{type:"CUSTOM", authType:"CUSTOM", method, url, headers, queryParams, body:{type:"JSON", formEncode:false, payload:{…"{{ rawPayload.username }}"…}}, output:{type:"SCHEMA", dynamic:false, schema}, actionAuthHeaders:{}, refreshCredentials:{…}, refreshable, sslVerify, urlPath:false, version}`. Save the empty form once in the UI (creates the row, `version:0`), then `POST …/request/update/{defId}/CUSTOM/auth?version={v}` with the full object. **Output fields are body keys only** (Add field = Key/Label/Type/Default) — response headers such as `Set-Cookie` cannot be mapped there | ✅ UAT |
| Create action | `POST /api/connector-builder/definition/{defId}` `{name, description, type:"ACTION"}` → `{definition:{id…}, violations}` | ✅ |
| Action definition | read `GET /api/connector-builder/definition/{defId}/{actionId}` · update `POST /api/connector-builder/definition/{defId}/update/{actionId}?version={v}` (full object; set `enabled:true`, `input`/`output` `{type:"SCHEMA_AND_LAYOUT",dynamic:false,layout:{},schema}`) | ✅ |
| Action HTTP request | read `GET /api/connector-builder/request/{defId}/{actionId}/action` (`""` until first save) · **create** `POST` same path · **update** `POST /api/connector-builder/request/{defId}/update/{actionId}/action?version={v}` | ✅ |
| Publish | UI *Publish* button; then the connector's `enabled:true` and actions appear in `GET /api/workflow-builder/node/{defId}/resources` as `{defId}:{actionId}` | ✅ |
| Publish (API) | `POST /api/connector-builder/definition/{defId}/publish?version={v}` (what the UI button calls); publishing is what copies `logo` → `GET /api/applications/{defId}` `iconUrl` | ✅ |
| Edit name/description/logo | UI: Connectors list → row ⋯ → *Edit* (dialog fields `root.name`, `root.description`, `root.logo`). `POST …/definition/basic/update/{defId}?version=` with a hand-built body → 500 ConstraintViolation (shape unknown) — use the dialog, then Publish | ✅ |

- ⚠️ **UI "Use Code Snippet" on the auth Input tab expects an EXAMPLE PAYLOAD, not a JSON schema** — pasting a
  schema creates fields literally named `type`/`properties`/`required`. Paste `{"username":"","password":""}` and set
  formats in the field editor, or set the schema over the API (row above).
- **Templates:** connection inputs and action inputs are both `{{ rawPayload.<field> }}` (scan of 486
  connectors: TOKEN/CUSTOM/BASIC all use `rawPayload.*`; CUSTOM auth outputs use `{{ auth.<field> }}`).
  Auth header for a personal API key: auth input schema `{properties:{api_key:{type:"string",format:"password"}},required:["api_key"]}`
  + `actionAuthHeaders:{"Authorization":"Bearer {{ rawPayload.api_key }}"}`.
- **Action request shape:** `{type:"ACTION", method, url, headers, queryParams, body:{type:"JSON", formEncode:false, payload:{…}}, sslVerify, enableRetry}`.
  Templates may sit inside a larger string (e.g. a GraphQL query `transcripts(limit: {{rawPayload.limit}})`).
- ✅ **A Connectors-SDK action's run output is `{headers, status_code, body}`** (UAT, read via
  `TEST_WORKFLOW_VARIABLE`): `headers` is the full response-header map of arrays — so `set-cookie` from a login
  action is readable by the next node, same as `custom_http_endpoint_execute`. A non-2xx (401) marks the node
  FAILED but the payload is still recorded. Node shape in a workflow: `{type:"ACTION", context:{appName:"<defId>",
  resourceName:"<defId>:<actionId>", resourceVersion:1, connectionId}, inputs:{}}`; `initiate-test/probe` with the
  inline definition runs it without saving a workflow.
- ✅ **Template scope inside a Connectors-SDK action request** (UAT, echoed through httpbin):
  Groovy binding = `[systemInputs, cursor, input, rawPayload, user]`. `rawPayload` = the ACTION's own inputs;
  the connection lives at **`input.auth`** = `{username, password, credentials, name, connectionId, authType,
  tags, circuitBreakerConfig, rateLimitConfig}` (your auth-schema fields plus platform metadata). So a body-borne
  credential is `{{ input.auth.password }}` — NOT `rawPayload.*` (that contradicts the older note above for
  actions; `rawPayload.*` is what the AUTH request itself uses). `auth`, `connection`, `userInput` do not exist
  ("No such property … for class Script_…"). `systemInputs` = `[__ENV__, appName, VOICEBOT_URL, customerId,
  resourceName, user, systemAutomation, webhookUrl, isTestExecution]`.
- ⚠️ **Success output of an action = the parsed body only.** On a non-2xx the node FAILS and its output is the raw
  `{headers, status_code, body}`; on 2xx you get the body and nothing else — declaring `headers`/`status_code`
  in the output schema does not bring them back. So a login action cannot hand `Set-Cookie` to the next node.
- ⚠️ **The connection's own auth request does not seed a cookie jar**: after a successful CUSTOM auth login, a
  plain action to `/api/entity/<obj>` returned **401**. Session-cookie replay must be built explicitly.
- `GET /api/user/context` is **404** from a plain HTTP client (the SDK hook resolves it differently); use an
  entity read such as `POST /api/entity/<own object>` as an "is my session valid" probe.
- ⛔ `POST …/request/{defId}/{actionId}/action` on an action that already has a request → 500 Mongo `E11000 duplicate key`; use the `/update/` path.
  ⛔ `PUT`/`PATCH` on that path → 405. `/request/update/{defId}/{actionId}/action` → 404 (the `update` segment goes **after** `{defId}` for actions, **before** it for auth).
- UI gotcha: the Value field of the auth header editor is a template editor; synthetic typing leaves React state at `Bearer {{` — set it over the API instead.
- ⚠️ Runtime user connections with a **custom** connector: the chat's "Connectors that could help" card renders blank
  (no name, `<img alt="placeholder">` with no src) even though `GET /api/applications/{defId}` has `displayName`/`iconUrl`;
  **Connect still opens the auth popup** (UAT). Built-in connectors (Gmail, Calendar) render correctly.
- Google built-in connector scopes (OAUTH): Gmail and Calendar expose a `scopes` multi-select (defaults: Gmail
  `https://mail.google.com/`; Calendar edit + events + tasks + drive.readonly); **Drive has no scope field** and requests
  full `drive`. For enforced read-only, build a custom OAUTH connector with fixed `*.readonly` scopes.

### Agent skills — `e_skill_ai_agent`
✅ UAT — link lives on the skill: `properties.accessibleTo: ["ai_agent/<id>"]`. Attach = update
`accessibleTo` + `saveAndDeploy` the skill + republish the agent. Find an agent's skills with aggregation
`group=ENTITY`, filter `properties_accessibleTo IN ["ai_agent/<id>"]`. ⚠️ deploying a skill also publishes any
unpublished draft (`version` > `deploymentState.entityVersion`). 

### Agent conversation over REST
✅ UAT — send: `POST /api/workflow/execute/node/sse` (`callables_call_automation_streaming`,
automation `67dcfe388445037d9b0662c0`, params `{copilotType:"AI_AGENT_TEST", message, messageContentType:"MARKDOWN", aiAgentId, timezoneId}`);
read: `…?name=call_automation&fetchConversation=66ab98083d73300e63962287` (params `{copilotType, caseId, userId, aiAgentId, until}`);
traces: `GetTraceTimeline` (automation `680cdbcaa3741471fc7c22e9`, `{traceId}`) and `TraceTimelineDetails`
(automation `6943f1be474ba4398bf4201c`, `{id, type}`). 
⚠️ `loadSkill(generate-chart)` silently ends the turn on UAT (no further LLM span).

### HubSpot search notes
✅ UAT — `hubspot_search_records_batch` operators: EQ NEQ LT LTE GT GTE CONTAINS NOT_CONTAINS
HAS_PROPERTY NOT_HAS_PROPERTY BETWEEN IN NOT_IN (no CONTAINS_TOKEN); multi-owner field
`hs_all_collaborator_owner_ids` **IN [ownerId]** matches deals where the owner is one of several collaborators.
`hubspot_get_owners` returns `results[]` (schema says `owners`) incl. `teams[]`. `hubspot_get_pipelines`
returns `metadata.isClosed` as the **string** "true"/"false". `hubspot_get_association_batch` → `results[{from:{id}, to:[{toObjectId}]}]`.

### Browser → localhost from an Orbit page — blocked
✅ UAT — Orbit's CSP `connect-src` allows only `'self'` and listed cloud hosts, so `fetch('http://127.0.0.1:…')`
from an Orbit tab is refused; `window.open` without a user click is popup-blocked. To move data out of the tenant, call a
callable workflow (same-origin `/api/workflow/execute/node`) that writes through a connector, not the browser.

### `custom_http_endpoint_execute` returns ALL response headers — the declared output schema lies
✅ UAT — the action's advertised output schema has only `result` and `status`, but a real run's
`outputs` payload is `{status, status_code, rawParams, headers}` where **`headers` is every response header**
as a map of arrays. The `responseHeaders` **input** (array of header names) did **not** restrict the set.
Never infer a node's real output from `/api/workflow-builder/node/{n}/resource/{r}` — run it and read
the output.
- ⚠️ **`followRedirects` is an ENUM, not a boolean.** `false` fails at run time with
  `IllegalArgumentException: No enum constant java.net.http.HttpClient.Redirect.false`. Use `NEVER`
  (also `ALWAYS`, `NORMAL`). `authType` here is only `CUSTOM` | `BASIC_AUTH`; `connectionType` is
  `DIRECT` | `ON_PREM`.
- `custom_http_application` encrypts `pathsToEncrypt: ["password","headersList.value","soapHeadersList.value","clientSecret"]`
  — a secret may live in a connection's **header value**, but there is no built-in way to inject one into a
  request **body**; a body-borne credential needs a Connectors SDK connector (§25).

### AI Governance — Controls, and the `controls_schema` catalogue
✅ UAT — closes backlog item S4 for the Controls surface (Policies still open).
**Routes:** base `/p/0/agent-governance` **404s**; every screen is a child —
`/overview`, `/discovery`, `/registry`, `/model-registry`, `/monitoring`, `/incidents/chat`,
`/policies`, `/controls/chat`.
**Controls** are entities of type `controls` (574 on UAT). List with
`POST /api/aggregation?entityType=controls&group=ENTITY`, full rows with
`POST /api/entity/controls {page:{limit,offset}}` (offset paging), one with
`GET /api/entity/controls/{id}`.
`properties`: `name`, `description`, `checkType`, `appliedTo:"chat"|"knowledge"`,
`appliedOn:["user_input","agent_output","tool_input","tool_output"]`, `actionType:"flag"|"block"`,
`enabled`, `llmModel`, `confidenceThreshold`, `checkSeverity`, `severityModel`, `severityLevel`,
`accessibleTo`, and `additional.prompt` for custom LLM checks.
**`accessibleTo` is the attachment, exactly like `e_skill_ai_agent`**: `["global"]` (509 rows) or
`["ai_agent/<id>"]` (65 rows, all `ai_agent/enterprise_search_agent`).
**`checkType`** points at a `controls_schema` entity — `GET /api/entity/controls_schema/{id}` →
`{name, description, type, schema, layout, redact, mask}`. 15 exist, mirrored across
`type:"chat"` and `type:"knowledge"`: Prompt Injection (chat `e_6a500b3015d9546842783050`,
knowledge `e_6a55d234b6bf3639e4822464`), Blocked Tools `e_6a500b08d46d4e608bbe2f9b`,
Credentials & Secrets `e_6a500b3f15d9546842783059`, PII detection `e_6a500b1bd46d4e608bbe2f9f`,
Denied Topics `e_6a500b7c30b9186dd3773d30`, Content Filter `e_6a500b6ad46d4e608bbe2fdd`,
Regex pattern `e_6a500b4fd46d4e608bbe2fbe`, Custom terms `e_6a500b5b30b9186dd3773d18`, and the
literals `custom_chat` / `custom_knowledge`. The schema's `inputs` field is the entity's
`appliedOn`; default is `["user_input"]` only. `mask:true` on chat PII / Credentials / Regex.
⚠️ `POST /api/lookup?ByKeys=ENTITY` with a bare `lookupType:"ENTITY"` fails —
*"ENTITY_TYPE with id null not found"* (5002). Resolve ids with `GET /api/entity/{type}/{id}`.
⚠️ Registry/incident counts on UAT look seeded (10,832 registry agents vs ~2,400 real `ai_agent`).
✅ **Create verified:** `POST /api/entity {entityType:"controls", tags:[...], properties:{...}}`
created a prompt-injection control (`<id>`) attached to a throwaway agent
(`<id>`), enabled and blocking on all four surfaces; found again with an
aggregation filtered on `properties_accessibleTo IN ["ai_agent/<id>"]`. `breachOn` defaults to
`false`; no `deploymentState` is returned, so controls look live-on-create.
✅ (§52): **Policies** = `policies` entity (grouping only); attaching a control needs NO republish; `blockedTools`
takes tool NAMES (keyword CONTAINS / NOT_CONTAINS); and — the important part — a control scoped `ai_agent/<native agent id>`
**did not gate a single turn** on the tracking agent (14 probes), while the agent's own `gaurd_rail` guardrails blocked inline.
Treat Controls as the audit/incident layer and `gaurd_rail` as the enforcement layer. `confidenceThreshold` enum still
unconfirmed beyond `high`/`medium`. 

### Verified pieces ✅ UAT
- **`POST /api/connector-builder/definition/basic`** `{name, description, baseUrl, logo:"", categories:[]}` → 200
  `{definition:{id}, violations}`. `POST …/definition/{id}/auth?type=CUSTOM` → 200; the auth arrives with an EMPTY
  `input.schema` and `GET /api/connector-builder/request/{id}/CUSTOM/auth` returns `{}` until a request is written.
- **Caller identity inside an agent tool:** a workflow that creates a row and reads `outputs.ownerUserId` gets the
  chatting user. `storage_by_unifyapps_fetch_records` output shape is `{cursor, objects, hasMore}`.

- **`storage_by_unifyapps_update_record_by_id` as an app data source** ✅: stored inputs
  `{useRawPayload:true, upsert:false, writeThroughSessionVariables:false, object_type, recordId,
  rawPayload}`; `rawPayload` must be the FULL record properties (spread the read row, then override).
  DS `<id>`.
- **Publishing an agent from the API** ✅: `GET /api/entity/ai_agent/{id}` → mutate `properties`
  (`instructions`, `agentType:"ai-agent"`, `topicExecutionSettings.topicExecutionModel`,
  `responseGenerationSettings.answerGenerationModel(+ModelSettings.modelId)`, `defaultTools`,
  `conversationStarters:[{text}]`) → `POST /api/entity/action/saveAndDeploy` with the whole entity →
  `deploymentState {entityVersion:1, version:1}`. Attaching skills first via the skill's
  `accessibleTo` needed no skill deploy. (`conversationStarters` must be plain strings — §9.)
### More findings (UAT)

- **Runtime user connections stall agent turns.** When a tool needs a runtime connection the user has not made (or
  must pick with "Use"), the chat shows a Connectors card and the turn sits in "Executing Wait For Tool Calls" — the
  agent cannot skip it. Mitigate: tell the agent in the user message which sources are connected; disable tools of
  custom connectors (their card renders blank). Per-user data for app pages cannot come from a workflow: the
  "Runtime user connections" automation setting is not exposed on this tenant, and a connector node without
  `connectionId` fails validation ("Please select a connection").
- **Any user can pick any other user's connection** in their own workflow's connection list (e.g. a personal
  Gcalendar connection appears for every builder). Treat personal connections as tenant-readable unless sharing is removed.
  ✅ UAT — seen in the wild: another user's AI-generated workflow (`solution-builder-stub` tag) bound
  `gmail_send_email` to a personal `Gmail-1` connection and its **test runs really sent mail** (outputs
  `labelIds:["SENT"]`); another user's config-app data source ran `oracledb_create_snapshot` on a personal Oracle
  connection. **Who uses connection X (audit recipe):** there is no usage endpoint (`POST /api/entity/entity-dependency`
  `{entityType:"CONNECTION",entityId}` → `{}`). Instead: (1) agent tools / tasks / data sources —
  `POST /api/aggregation?entityType=e_action_ai_agent|e_topic_ai_agent|e_data_source&group=ENTITY` with
  `filter properties_context_connectionId IN [ids]` (projections `properties_name`, `properties_aiAgentId`,
  `properties_interfaceId`; `ownerUserId` is not projected — `GET /api/entity/{type}/{id}` for it); runtime-connection
  tools carry no `connectionId`. (2) workflows — `WorkflowDefinition` aggregation with `appsUsed IN [appName]`, then
  `GET /api/workflow-definition/{id}` and match the id in the body (3,901 definitions in ~20 s at 12 parallel).
  (3) whether it fired — `WORKFLOW_EXECUTION` in groups `PLATFORM` and `TEST_WORKFLOW_EXECUTION`, then
  `lookup TEST_WORKFLOW_VARIABLE` for the action node. Users by id: `POST /api/lookup?ByKeys=USER {keys:[...]}`.
- **HubSpot meetings** for a user: `hubspot_search_records_batch` object `meetings`, filter groups
  `hubspot_owner_id EQ <id>` OR `hs_attendee_owner_ids CONTAINS_TOKEN <id>`, plus `hs_meeting_start_time BETWEEN` epoch-ms
  strings; associations `meetings → deals`. `hs_meeting_external_url` is the Google Calendar event page, not the call link.
- **Agent memory (UAT, partly working):** `longTermMemorySettings.enabled` + `defaultTools.saveInstantMemoryTool`
  are not enough. Memory lives in entities `memoryprofile` (`scope:"userSpecific"`, `memoryTypes`, `accessibleTo:
  ["memory_profile_set/<id>" | "ai_agent/<id>"]`, not deployable — live on create), `memory_profile_set`
  (`accessibleTo:["ai_agent/<id>",…]`) and `memory_json_store` (records: `memoryText`, `memoryProfileId`,
  `memoryProfileSetId`, `createdFromAgentId`). Observed: the instant-save tool wrote to the tenant's
  "GlobalMemorySet" (not linked to the saving agent), so a new chat did not recall it; agents also claimed "saved"
  without calling the tool. Open: make saves land in a set linked to the agent.
  **Activation:** a `memory_profile_set` created by API shows "Undeployed Changes"
  and the UI Publish button does nothing — deploy it with `POST /api/entity/action/saveAndDeploy`
  (whole entity + `deploymentNotes`); every working set on UAT has a `deploymentState`.
  `memoryprofile` itself → 500 `Entity type is not deployable`. The background extractor stamps
  `state` (`inProgress`/`completed`) and `lastSyncTime` on the profile when it runs; a profile
  with neither has never been picked up. Schedule = `userDefinedGrabbingSchedule
  {duration, unit: MINUTES|DAYS}`; extracted records carry `createdFromAgentId` and the
  profile id. UI: agent → Configuration → Memory; set page `/p/0/memory-set/{id}/profiles`.
- **Solutions and platform internals (UAT):**
  - `internal_api_executor_execute_request` (server-side calls to platform APIs) → deploy fails
    `Internal HTTP Endpoint is not enabled` on UAT, so platform metadata can only be read from a
    signed-in browser tab.
  - Solutions (`e_solution`, `solution_by_unifyapps_*`: save / save versions / deploy / restore)
    link only `CONNECTION`, `ENTITY_TYPE`, `WORKFLOW_DEFINITION`, `e_interface` — no agents,
    records or data sources — and restore versions, not deletions.
  - A deleted workflow is gone for good: GET → 500, create with the same `id` → Mongo E11000
    duplicate key, no undelete endpoint. Never delete one.
  - `POST /api/workflow-definition` honours an explicit `id` when it is free.
  - Entity search guards: `e_component` requires a `properties.interfaceId` filter,
    `e_data_source` a `properties.interfacePageId` filter (5011). `properties.accessibleTo` IN
    `["ai_agent/<id>"]` works for skills, memory sets and profiles; `properties.aiAgentId` IN for
    topics and tools; `tags` IN works for `ai_agent` but not for apps.

- **Caller identity inside a workflow (UAT):** a CALLABLE run has no trusted "current user"
  variable — Groovy's binding holds only the declared parameters, `{{ context }}` is rejected ("Node referenced
  … no longer exists"), `variable_by_unifyapps_get_session_variables` returns `{}`, and `__internals__` in the
  START output is whatever the browser sent. Runs do record the caller (`WORKFLOW_EXECUTION.USER_ID`), and
  **storage writes are stamped with it**: `storage_by_unifyapps_create_record` returns `ownerUserId` /
  `lastModifiedBy` = the calling user. Pattern without any delete: the record the workflow writes anyway is the
  identity probe (§49.2). `System.getProperties(` is blacklisted in Groovy.

- **Groovy closure parameters must not shadow anything in the script (UAT).** A Code node's script
  is one scope: `{ String item, double price -> … }` deploys as 500 *"startup failed … already contains a
  parameter of the name price"* if `item`/`price` exist elsewhere, including in another closure's parameter
  list. `saveAndReturnViolations` passes; only `/deploy` compiles — so always read the deploy response.
- **`standard_entities_fetch_entities` — read platform entities from a workflow (UAT).**
  `context {appName:'standard_entities', resourceName:'standard_entities_fetch_entities',
  resourceVersion:22476}`, `inputs {entityType, group, projections, page}`. Three hard-won details:
  · `projections` entries need **`aggregationFunction:'NONE'`** — `[{name:'id'}]` fails with
  *"Aggregation function is null"*, and plain strings throw a ClassCastException. Without
  projections every row comes back with empty `columns`.
  · **`filter` is silently ignored.** `filter:{field,op,values}` and `triggerInputCondition` both
  return the whole tenant. Filter in a Code node instead.
  · `page.limit` is honoured generously: **20000 returned all 10,333 `e_interface` rows in one call**
  with `hasMore:false`. So a whole-tenant scan is one node, not a paging loop.
  · Entity projections still yield **only `id` and `tags`** — no name, no description (§10 note).
- **An object has TWO schemas and a write validates against the second (UAT).**
  `entity-type.input.schema` is the form/layout; `entity-type.schema.schema` is the validator and
  carries `additionalProperties:false`. Adding a field to `input.schema` alone lets the UI show it
  while every write fails with *"Non Empty Validations … add additionalProperties &lt;field&gt;"*.
  Update **both**, then `POST /api/entity-type/update`.
- **`storage_by_unifyapps_bulk_create_records`** (v16416) takes `rawPayload: [ …records ]` and
  returns `{inserted, insertedIds[], errors{}}`. An **empty list is accepted** (`inserted:0`), so a
  workflow that may have nothing to write needs no IF_ELSE branch.
- **The schedule trigger accepts `cron:'INTERVAL'` only (UAT).** `'CRON'`, `'CUSTOM'` and
  `'CRON_EXPRESSION'` are all rejected by `saveAndReturnViolations` with *"Please select a valid
  value"*, so a scheduled workflow runs on an interval from deployment — there is no fixed clock time.
- **Picking an agent's model — only ONE lever works (UAT).** Verified by measurement on
  an assistant agent: `topicExecutionSettings.topicExecutionModel` (+ `topicSelectionModel`) on the
  `ai_agent` entity, then `saveAndDeploy`. Two other routes look plausible and are **silently ignored**:
  the per-user preference `<agentId>-selectedModelId` (record `{applicationId:'ua-copilot', module:'INTERFACE',
  recordId:'ua-copilot'}` via `standard_entities_create_or_update_user_preferences`) and the per-turn
  `parameters.settings.taskExecutionModel` on the streaming send. Both returned a normal answer that still
  ran the old model.
- **A model entity can silently fall back to Sonnet (UAT).** `Claude Opus 4.8 [Anthropic]`
  (`<id>`) was deployed on the agent and the trace still read
  "Claude Sonnet 4.6 (BedRock)". `Vertex Opus 4.8` (`<id>`) genuinely runs.
  The tenant carries 425 `ai_agent_llm_model` rows, many broken test entries — **always verify after
  switching**, don't trust the name.
- **A model whose tenant connection is inactive fails every call (UAT).** `Claude Sonnet 4.6 [Anthropic]`
  (`<id>`) and `Claude Sonnet 5` (`<id>`) run on connection
  `AI Agent Anthropic` (`<id>`, `active:false`): the `__ua__call_ai_agent_llm_model` step fails in
  ~0.5 s with `Connection: AI Agent Anthropic is not active`, and a data-source call over it returns only
  `500 "Workflow execution failed"`. **Check before choosing a model**: aggregation on `ai_agent_llm_model` with
  projection `properties_connectionId` (also `properties_provider`, `properties_model` = the real model id), then
  `GET /api/connection/{id}` → `active`. Working on this tenant: `Vertex Opus 4.8` and `Sonnet 5 (Vertex AI)`
  (`<id>`, `properties_model: claude-sonnet-5`), both on `UnifyApps Vertex AI Connection for
  Gemini`. `Vertex Sonnet 5 AI FDE` (`<id>`) also says `claude-sonnet-5` but counts a
  different number of input tokens for the same prompt (32 vs 41) and calls itself an older model — treat it as a
  fallback, don't use it. `OpenAI GPT 5.6 Terra` (`<id>`) failed through the same step after 12 s.
- **Verify which model actually ran by its price signature** — `fetchConversation` →
  `additional.llmUsageDetails`: divide `inputCost` by (`inputTokens` - cacheWrite - cacheRead),
  `cacheWriteCost/cacheWriteInputTokens`, `outputCost/outputTokens`, x1e6 for $/M.
  Sonnet 4.6 = **3 / 3.75 / 15**; Opus 4.8 = **5 / 6.25 / 25**. The Observability trace also names the
  model per span, which is the other confirmation.
- **HubSpot search via the connector:** empty properties are omitted from results (you cannot tell "empty"
  from "no such property" except on records that have a value). `CONTAINS_TOKEN` accepts `*word*`
  wildcards; AND several of them to find a deal by name. `hs_object_id EQ` fetches one deal by id.
- **Findings from an invoice three-way-match build (UAT) ✅**
  - **Record list filters:** `POST /api/entity/{objectId}` accepts
    `filter {op:"AND", values:[{field:"properties.<f>", op:"GT"|"LT"|"GTE"|"IN", values:[…]}]}`, and GT/LT work
    on number fields. The `sort` in the same body did not apply: rows came back in id order.
  - **Agents on Vertex Opus** sometimes write prose before the JSON envelope, or a fenced block, or an envelope with
    one extra brace. A reader must take the answer as JSON when it starts with `{`; otherwise the last
    fenced block containing `"status"`; otherwise the last balanced `{"status"…}` object (a string-aware brace
    scan). For text fields, fall back to a regex over the raw answer.
  - **Guardrail denied topics blocked a drafting agent's own work:** topics "sending messages to suppliers" and
    "writing out a full IBAN" blocked every draft; the evidence rows carried the blocked message and the workflow
    run still COMPLETED. Fix: definitions that name what is NOT in the topic (drafting for a person to send;
    credit-note or corrected-invoice requests). Rule: after any guardrail change, re-run a real turn of that agent
    and read its newest evidence row.
  - **`incidents`:** for 40+ hours no control of any project wrote one on UAT, including controls probed live. So
    control firing is not provable by probe on UAT at present.

- **LLM steps are not repeatable on thinking models even at temperature 0** (Gemini 3.8 Flash [MEDIUM]): the same
  sizing scope gave 3–9 use cases. Flash [LOW] `<id>` + explicit granularity rules gave a stable
  structure in 3–5 s; exact repeatability needs caching the proposal per input.

## 26. Findings — AI-native app patterns (UAT)

### A data source is invisible to a published app until the app is published again ✅ UAT
Creating an `e_data_source` against `e_global_<appId>` is not enough for a **running** app.
Calling it returns `500 {"rootCauseMessage":"forbidden datasource: not found"}` even though the
entity exists, the ids match and the same call works from a signed-in platform tab.

`POST /agent-api/apps/{appId}/publish` fixes it immediately — the publish snapshots which data
sources the deployed app may execute.

Easy to misdiagnose: the five storage bindings were created **before** the first publish and
worked, so the failure looked specific to `callables_call_automation`. It is not. **Publish
after adding any data source.**

### LLM step inside a workflow — `conv_ai_by_unifyapps` ✅ UAT

| Field | Value |
|---|---|
| node `type` | **`CALL_INTERFACE_WORKFLOW`** (not `ACTION`) |
| `context` | `{appName:'conv_ai_by_unifyapps', resourceName:'conv_ai_by_unifyapps_call_llm_model_with_options', resourceVersion:2471}` |
| `inputs.callableInterfaceId` | `'__ua__call_ai_agent_llm_model'` |
| `inputs.parameters` | `{modelId, systemPrompt, message, temperature, maxTokens, responseFormat}` |
| `message` | chat array: `[{role:'user', content:[{type:'text', text:'…{{ n_in.outputs.x }}…'}]}]` |
| `responseFormat` | `{type:'json_object'}` |
| `modelId` | an `e_…` entity id — copy from an existing LLM workflow (`<id>` on Orbit UAT) |
| outputs | `{{ n.outputs.llmResponse }}` (string), `.success`, `.tokensUsed` |

Measured: ~19 s / ~2.5–3.8 K tokens for 25–35 records returning 4 structured insights.

### `initiate-test` cancels a slow run when its own HTTP call times out ⚠️ UAT
A workflow with an LLM step returned `500 "No Response received within specified timeout."`, and
the run then showed `STATUS: CANCELLED` at ~23 s — with the LLM node's `state` carrying a real
`childRunId`, i.e. the node had fired. The test runner, not the workflow, gave up.

Verify anything slow by calling the **deployed** workflow through its data source instead.

### Storage bulk writes ✅ UAT

| Action | Notes |
|---|---|
| `storage_by_unifyapps_bulk_upsert_records_by_id` | `updates:[{id, updateFields:[{fieldName, actionType:'SET'\|'UNSET'\|'INCREMENT'\|…, setValue}]}]`. `setValue` is declared `string` but **accepts a real number and stores it as one**. Output `{success, successCount, failedCount, errors}` |
| `storage_by_unifyapps_bulk_create_records` | `object_type`, `useRawPayload:true`, `rawPayload` = **array**. Output `{insertedIds, inserted, errors}` |

No bulk record endpoint exists on the entity API — `POST /api/entity/update-bulk` is
`500 "ENTITY_TYPE with id update-bulk not found"`. Loop `POST /api/entity/update` (concurrency 10
did 414 rows without a failure).

### Groovy sandbox — four traps ✅ UAT
1. **An optional parameter that resolved to nothing has no binding**, and reading it as a bare
   variable fails `No such property: x for class: Script_…`. Start every script with
   `def p = { String k -> binding.hasVariable(k) ? binding.getVariable(k) : null }`.
2. **`Date.format(String)` is not available** (it is a Groovy JDK extension the sandbox does not
   load) → `No signature of method: java.util.Date.format()`. **`java.time` appears to be blocked
   outright** — it failed with an error object carrying no message at all. *(Superseded: `java.time`
   runs verified on UAT, 09-26 (§47.29) and 09-27 (§47.50); the empty error matches trap 3 below.)* What works:
   `new java.sql.Date(System.currentTimeMillis()).toString()` → `yyyy-MM-dd`.
3. **Mutating a map while iterating it** throws `ConcurrentModificationException`, which also
   surfaces as an error object with **no message**. Build maps by adding, never by removing.
4. `groovy.json.JsonSlurper` **is** available.

Also: `storage_by_unifyapps_fetch_records` output inside a workflow is `{{ n.outputs.objects }}`
— not nested under `response` as it is through `execute/node`.

### Objects Manager — schema and seeding ✅ UAT
- Create with `POST /api/entity-type`, then **read it back and `POST /api/entity-type/update`
  with the whole object** plus `input` (`SCHEMA_AND_LAYOUT`) and `schema` (`SCHEMA`) carrying the
  same JSON Schema. The server derives `metadata.primaryKeyField` etc. from the per-field flags.
- A record's `id` **is** its primary-key value, which makes a seed loader idempotent: create,
  and on `E11000 duplicate key` read the row for its `version` and `POST /api/entity/update`.
- `POST /api/entity/{objectId}` with `page.limit` returns the rows; there is no `totalCount` on
  a `limit: 1` read, so count by fetching a page large enough to hold the object.

## 27. Findings — scaling one app's data layer to 8,000 records (UAT)

Found while taking one app's data layer from ~580 records to 7,997 across 14 objects. The theme is
that the storage node fails **silently and plausibly** at scale: it returns 200, it returns rows,
and the rows are wrong.

### `entity-type/update` ignores schema changes without the top-level `schema` block ⛔ UAT
Adding eight fields to an object by reading it, editing `input.schema.properties` and POSTing
the whole thing back returns **200**, and a re-read shows all eight new properties. It has not
worked. `columnCounts` stays at the old number, `metadata.filterableFields` reverts, and every
write that mentions a new field fails with `CREATE 500: Workflow execution failed` — no field
name, no hint. Setting `columnCounts` by hand in the payload does nothing.

The update needs **both** carriers of the JSON Schema, which §24 states but which is easy to
lose when round-tripping a read (the GET does **not** return `schema`, only `input.schema`):

```js
const et = await (await fetch(`/api/entity-type?entityType=${id}`)).json()
et.input.schema.properties.new_field = { title: 'New', type: 'string', filterable: true }
et.schema = { dynamic: false, type: 'SCHEMA', schema: et.input.schema }   // ← the missing half
await fetch('/api/entity-type/update', { method: 'POST', body: JSON.stringify(et) })
```

With it: `columnCounts` jumps to the real property count, `filterableFields` is derived from the
flags, and writes succeed. Verified on `<uc>_citizen_voice` (7 → 15 fields) and
`<uc>_story`. **Check `columnCounts` after every schema update** — it is the only cheap signal
that the change actually landed.

### Storage filters: one shape works, a near-identical one is ignored ⛔ UAT
`triggerInputCondition` must be `{ operator: 'AND', filters: [...] }`. The plausible variant
`{ operator: 'AND', operands: [...] }` is accepted and **silently ignored** — the read returns
the whole object with `total` unfiltered, which looks exactly like "the filter matched
everything". A single bare leaf (`{ property, filter }`) also works, which is what makes the
wrong shape so easy to ship: it behaves correctly until the day a second condition is added.

| Operator | Shape | UAT |
|---|---|---|
| `EQUAL` | `{ property, filter: { operator: 'EQUAL', value } }` | ✅ |
| `IN` | `filter: { operator: 'IN', value: [...] }` — on **`value`**, not `values` | ✅ (`values` is ignored) |
| `GREATER_THAN` / `GREATER_THAN_OR_EQUAL` on a string field | — | ⛔ `FETCH 500` |
| top-level `OR` in `triggerInputCondition` | — | ⛔ matches nothing (§26) |

A period window therefore cannot be expressed as `period > '2026-01'`; filter on the scope and
metric instead and slice in memory, or store an integer period alongside the string.

### Page limits are generous; the danger is not asking ✅ UAT
`page: { paginateBy: 'OFFSET', limit }` returned 500/1,000/2,000/3,000 rows in 235/152/175/209 ms
against a 5,016-row object — the limit is not the bottleneck and a `limit: 600` inherited from
when the object held 414 rows is. A truncated read renders a chart that looks right and is
missing half its entities, with no error anywhere. Two rules that follow:

- **Count with `total` from the response**, never `records.length`. On the one screen whose job
  is to state what the data layer holds, `length` reported 3,000 of 5,016 and looked plausible.

### The UPDATE binding refuses `upsert: true` ⛔ UAT
`storage_by_unifyapps_update_record_by_id` stores `upsert: false`, and overriding it at call
time is refused: `UPDATE 500: forbidden datasource : invalid input`. The stored input set is
matched by value, not merely by key (§26). A re-runnable seed therefore reads the existing
primary keys first and branches create-or-update per row — which is also faster, since the
create path skips the fetch-before-update.

**The better fix (✅ UAT, a sourcing build Sourcing Hub): mint a sixth binding.** `upsert` is a
stored input like any other, so a data source that bakes it in as `true` is accepted and behaves
exactly as wanted — clone the app's UPDATE `e_data_source`, set `properties.inputs.upsert = true`,
rename it, `POST /api/entity`, publish. One extra entity turns every seed writer into a plain
`upsert(object, id, payload)` with no read-before-write and no branching at all, which is what
makes the whole seed re-runnable. Remember the publish: a data source minted after the last
publish is invisible to the running app.

### A data source created after the last publish, again ⚠️ UAT
Cost an hour for the second time. The app called a new automation's data source, the call
failed, the calling code swallowed it into a shared error state, and the visible symptom was a
*stale risk card* — a card quoting "2.4x the national average" beside a map showing 1.3x.
Nothing said "forbidden datasource". **Publish immediately after registering a data source**,
before writing any UI against it, and give each automation call its own error surface rather
than a shared one.

### `saveAndDeploy` deploys the version BEFORE your edit ⛔ UAT
Editing an agent's instructions and calling `POST /api/entity/action/saveAndDeploy` once returns
**200** with a bumped `deploymentState.version`, and the change does **not** go live. The call
saves the draft and deploys in one step, but the snapshot it deploys is the entity as it was
*before* the save:

```
after one call:   version: 12   deploymentState.entityVersion: 7    ← deployed is stale
after a second:   version: 13   deploymentState.entityVersion: 13   ← now live
```

Nothing in either response says so, and the agent keeps answering from the old instructions —
which reads as "the model ignored my prompt" rather than as a deployment problem. **Always assert
`entity.version === entity.deploymentState.entityVersion` after deploying**, and call it again if
they differ. Verified on all three an executive-intelligence build agents. *(Superseded by §47.1: verify by comparing the deployed snapshot's `properties` with the agent's; `version` climbs on its own, so a version-equality loop may never end.)*

Related: an agent's answer format is often governed by its **Task** (`e_topic_ai_agent`,
`properties.instructions`, linked by `properties.aiAgentId`) rather than by the agent's own
instructions — the transcript names the task it picked ("Establishing our focus on: …"). Change
both, or the agent-level edit has no effect on that path. Tasks are not returned by
`POST /api/lookup?ByQuery=ENTITY` with `entityType: 'e_topic_ai_agent'` (500 `ENTITY_TYPE with id
null not found`); list them with `POST /api/entity/e_topic_ai_agent` and filter by `aiAgentId`.

## 28. Findings — cloning assets, objects, records (UAT)

### Cloning platform assets from a known-good app
✅ UAT

A fast correct way to build a new app's platform layer (6 objects, 3,397 records, 4 workflows,
9 data sources and 1 agent with 3 tasks + 2 tools in ~10 minutes). Clone only assets you own or
that sit in your own solution.

| Asset | Recipe |
|---|---|
| Workflow | `GET /api/workflow-definition/{id}` → strip ids/metadata, change name/prompt/`object_type` → `POST /api/workflow-definition` → `saveAndReturnViolations` → `deploy?version=<live version>` |
| Storage DS | `GET /api/entity/e_data_source/{id}` → change `name`, `interfaceId`, `interfacePageId` → `POST /api/entity` |
| Callable DS | same + `inputs.automationId` |
| Agent | copy `ai_agent.properties`, replace name/instructions/role/goal; create `e_topic_ai_agent` + `e_action_ai_agent`; `POST /api/entity/action/saveAndDeploy` with the full entity |

**One generic AI-writer workflow** ✅ — a clone of the insight engine taking `p_screen` (task
name), `p_context` (instructions incl. the exact JSON shape), `p_actions`, `p_data` served several
narrative jobs from one workflow and one data source. Cloning a workflow clones its prompt: rewrite it.

### `GET /api/entity-type?entityType={id}` — missing object
⚠️ UAT

**Response** — **200 with an empty body** for an object that does not exist, so `r.json()` throws
"Unexpected end of JSON input". Read `r.text()` and treat empty as not found.

### Records — parallel load
✅ UAT — 12 parallel `POST /api/entity` workers loaded 3,397 records (412
suppliers, 2,926 signals, 38 alerts, 14 treatments, 7 critical ops), zero failures, well under a
minute.

## 29. Data sources in a config app (UAT)

- **Transformer output**: the execute response is `response.result = <transformer return>`, but in expressions `{{ ds['data'] }}` **is** the return value ⛔ `['data']['result']` → ✅ `['data']`.
- **`advancedOptions.queryDisabled`** `{type:'filter', payload}` gates an automatic data source ✅. ⛔ `onPageLoad: runDs(A) → onSuccessActions runDs(B)` evaluated B's inputs before A's data was in the store (the LLM got empty arrays).
- HTTP (`custom_http_endpoint_execute`): `baseUrl` + `path` + `queryParamsList:[{key,value}]`; ⛔ a single `url` → *"Base URL must start with http(s)"*. Output `{status, result}` ✅.
- Storage filters `properties_<field>` / `id`; sort `properties.<field>` ✅. Callbacks `successEvents/failureEvents` run actions ✅.
- Connector data sources carry `context.connectionId` (Gmail, OpenAI… 👁 harvest).

## 30. Findings — Groovy validator, aggregation, stalling agents (UAT)

### The Groovy validator blacklists some plain identifiers ⛔ UAT
`saveAndReturnViolations` refused a node with
`Blacklisted commands found in code : owner = at position 1050`. The code was
`def owner = val('created_by') ?: '…'` — an ordinary local variable. The check is a substring
scan over the source, not a parse, so a variable **named** like a sensitive assignment is enough
to fail it. Rename (`raisedBy`) and it passes. Assume the same for any identifier that reads like
a platform field being assigned; the message does name the offending text and its offset, which
is the only reason this is quick to fix.

### Aggregation on `WorkflowDefinition`: `CONTAINS`, not `LIKE` ⚠️
`{field:'name', op:'LIKE', values:['<uc>_%']}` → **500** with a bare `errorCode: -1` and no
message. `op: 'CONTAINS'` with a plain substring works and is the way to find a tenant's
workflows by name prefix.

### A stalling agent is a tool-shape problem, not a model problem ⛔ → ✅ UAT
Driving the real dock with six questions, one of them — *"show me the group spend trend over the
last 24 months"* — made the agent call `QueryData` **five times** and end the turn with no answer.
Three defects in the cloned query workflow, all silent:

1. **One filter pair.** `object_type` + `filter_field`/`filter_value` cannot express a KPI series,
   which needs `scope` AND `scope_code` AND `metric`. The model can only guess one dimension at a
   time. Fix: three pairs, ANDed; a comma in the value becomes `IN`; `"true"`/`"false"` becomes a
   boolean; and strip a `properties.` prefix a caller added (otherwise `sort_field` silently
   becomes `properties.properties.x` and nothing sorts).
2. **Compaction by a whitelist of field names**, inherited from the app the workflow was cloned
   from. Over fifteen rows the post-processor kept only the fields on that list — none of which
   existed in the new domain — so an unfiltered read of a 5,424-row object returned **sixty empty
   objects**, `compacted: true`, no error. Compact by SHAPE instead: drop keys ending `_json` and
   string values longer than ~140 chars, keep every number, code, date and flag, and return a
   `note` naming what was dropped.
3. **No stopping rule in the instructions.** Added: *"two calls that returned the wrong rows means
   the filter was wrong, not the tool. Never make a third call that is another guess."*

After: the same six questions answered in **24–49 s each, every one with a chart, none stalled**.
Diagnose this class by calling the tool for every object the agent can reach and asserting the
returned rows have the number of keys you expect — sixty empty objects and sixty real ones are
indistinguishable in a latency measurement.


---

## 31. Connector catalogue — what exists and what it can do (UAT)

A full harvest of the tenant's connector surface (`connectors-index.tsv` and `platform-nodes.tsv`
beside this file hold the result; `connectors.md` explains how to use them). The endpoints are in
§5 and §7; this section records what the harvest established.

### The numbers

| | Count | Source |
|---|---|---|
| Nodes in the catalogue | **1,214** | `GET /api/workflow-builder/nodes` |
| — application connectors (built-in) | 983 | `tags: ["Applications"]`, `custom: false` |
| — platform nodes (built-in) | 91 | `tags: ["Internal"]`, `needsAuthentication: false` |
| — custom (Connectors SDK, tenant-local) | 140 | `custom: true`, 24-hex `name` |
| Need a connection | 1,064 | `needsAuthentication: true` |
| Have at least one connection | 304 → **279 real** | `find-nodes-with-connections`, minus 25 that aggregate to 0 (§18 D4) |
| Connections tenant-wide | 7,775+ | `GET /api/connection` (⛔ do not call — §7) |

Most-connected connectors: `mdm_by_unifyapps` 3,296 (every context graph creates one) · `gmail`
965 · `slack` 574 · `gsheets` 392 · `gdrive` 285 · `gcalendar` 247 · `salesforce` 111 ·
`microsoft_outlook` 105 · `openai` 92 · `snowflake` 74 · `github` 73.

**983 connectors ship; ~279 are actually connected, and most of those have fewer than five
connections.** "UnifyApps has a connector for X" and "this tenant can call X today" are different
claims — check the aggregation before promising the second.

### Three levels, not two

`appName` (connector) → `resourceName` + `resourceVersion` (action/trigger/agent-tool) →
`connectionId` (authenticated instance). A workflow step, an agent tool, an app data source and a
context-graph source all reference the same triple. `appName` is the key to every discovery
endpoint, and it is frequently **not** the product name: `gsheets`, `gcalendar`, `zoho` (Zoho CRM),
`sqlserver`, `mdm_by_unifyapps` (Ontology).

### Naming and shape conventions (useful for generating without a lookup)

- Resources are `{appName}_{verb}_{object}`; trigger prefixes occasionally differ from action
  prefixes (`gsheet_on_new_row_polling` vs `gsheets_add_row`).
- Verb families: `get_`/`fetch_` · `list_`/`search_`/`find_` · `create_`/`add_`/`insert_`/`upload_`
  · `update_`/`edit_`/`replace_` · `upsert_`/`merge_` · `delete_`/`remove_`/`archive_` ·
  `*_batch`/`bulk_*` · `on_*` (always TRIGGER).
- Superseded actions live alongside their replacements (`gsheets_add_row` / `_v2`,
  `openai_create_transcription` / `_v2`). Prefer the highest `_vN`.
- **Every SQL connector ships the same six triggers**: `on_new_event`, `on_update_event`,
  `on_delete_event`, `on_new_or_update_event`, `on_event`, `on_scheduled_query_search`. Verified
  identical on `oracledb`, `postgres`, `snowflake`.
- Trigger mechanism is in the name: `*_polling` (scheduled poll), `*_webhook` / `*_realtime`
  (push), bare `on_*` (connector-managed subscription).

### Near-duplicate connectors — pick deliberately

`salesforce` vs `salesforce_soap` vs `salesforce_cpq` vs `salesforce_marketing_cloud` ·
`netsuite` (146) vs `netsuite_soap` (13) · `workday` (170) vs `workday_soap` ·
`microsoft_sharepoint` (62) vs `microsoft_sharepoint_graph` (68) · `databricks` (3) vs
`databricks_rest` (105) · `custom_http_endpoint` (internal, ad-hoc) vs `custom_http_application`
(connector, saved base URL) · `google_workspace` (admin) vs `gmail`/`gdrive`/`gsheets` (user data)
· `oracledb` (the database) vs `oracle_fusion` / `oracle_ebusiness_suite` / `oracle_jde` /
`oracle_siebel` (the applications).

Comparing resource counts between two candidates reliably identifies the maintained one.

## 32. OCR / extraction node (UAT)

- **OCR/extraction node** ✅: `type:'CALL_INTERFACE_WORKFLOW'`, `context {appName:'conv_ai_by_unifyapps', resourceName:'conv_ai_by_unifyapps_ocr_document_details_extraction'}`, `inputs {callableInterfaceId:'__ua__call_ocr_extraction', parameters:{files:[{fileObject:{source, sourceType:'CLOUD_STORAGE', name, fileType}, mimeType}], modelId, prompt, systemPrompt, response_format:'json_object'}}` → outputs `{output (string), content[], status, errMsg}`. Interface definition: `POST /api/lookup?ByKeys=CALLABLE_INTERFACE`.
- `modelId` must be a **TEXT_EXTRACTION**-group model: `POST /api/lookup?ByQuery=ENTITY_ID:ai_agent_llm_model` with `properties.modelGroup IN [textExtraction, TEXT_EXTRACTION]` (Orbit UAT: `<id>`, Claude Sonnet 4.6) ✅.
- A one-page synthetic report PDF (3 KB): upload → record ANALYSED with summary, 5 key points, 3 risks, 13 metrics, 3 recommendations in ~39 s through an automation data source ✅.
## 33. Findings — agents that stop early, publishing whole entities (UAT)

### The other half of the stalling-agent fix ✅

§30 established that a stalling agent is usually a tool-shape problem, and the three-ANDed-filter-
pair `QueryData` stopped the *looping*. A second failure mode survived it, at roughly 1 turn in 9:

> `responseGenerationStatus: "completed"`, three tool calls made, and the last Bot message is
> *"…Let me look at the document detail for the highest-exposure names and pull the actual
> mandatory expired/expiring documents."* The turn ends there. The user sees a plan, not an answer.

There is **no max-iterations setting** on `ai_agent` to raise (`topicExecutionSettings` has only
the model choices, `thinkTool`, citations and voice). It is a prompting problem, and the fix is a
turn contract — now shipped in all three a sourcing build agents:

```
HOW A TURN ENDS — a contract with no exceptions
The last thing you write is the ANSWER to the question you were asked. Never a plan, never a
next step, never a note about a field.
- If your final sentence starts "Let me", "I'll now", "Next I will", "Let's look at" or "I need
  to", the turn is not finished. Either make that call, or delete the sentence and answer with
  what you already have.
- You get at most FIVE QueryData calls in a turn. On the fifth you stop reading and write the
  answer, naming what you could not check and what somebody would have to open to close it. A
  partial answer with its gap stated is the deliverable. A promise is not.
- A field that cannot give you what you wanted is a FINDING, not a reason to stop. Say what it
  can and cannot distinguish, give the best answer it does support, and move on.
- Open with the answer, not with how you got it. "I retrieved", "I now have", "I have the full
  list", "Let me separate" are working notes. The reader wants the finding in the first line.
```

The last bullet fixes a separate, purely cosmetic problem that showed up in **4 of 9** answers:
the final answer opened with the model's own working notes ("I retrieved all awarded events…",
"I now have both sides. Let me cross-reference…").

**Measuring it.** Send with `POST /api/workflow/execute/node/sse` and read the stream to the end
(that is your latency); then read the conversation and take the Bot message **without**
`additional.internalMessageType`. The list is **reverse chronological** — index 0 is the newest —
so the ANSWER is the first such message, not the longest. Taking the longest hides exactly this
bug, because in a stalled turn the longest non-thought message is a mid-turn narration.

Nine-question baseline before the contract: 9/9 `completed`, 20–54s, 2.2k–7.0k chars,
$0.07–$0.55 per turn.

### `saveAndDeploy` needs the whole entity ✅

`POST /api/entity/action/saveAndDeploy {entityType, id}` → **500**. It takes the **full entity
object** plus `deploymentNotes`
says. And still twice: re-READ the entity between the two calls, because the first publishes the
pre-edit snapshot. Confirm with `version === deploymentState.entityVersion`. *(Superseded by §47.1: verify by comparing the deployed snapshot's `properties` with the agent's; `version` climbs on its own, so a version-equality loop may never end.)*

## 34. Findings — storage node shapes and the graph engine on Orbit UAT

An app with 22 objects / 37,902 records, a context graph (16 node types, 47 edge types, 4,000
records, 11,588 edges), 8 workflows and 3 agents.

### 🔴 `updateFields` on a bulk upsert is a LIST OF OPERATIONS, not a map ✅

`storage_by_unifyapps_bulk_upsert_records_by_id` takes

```json
"updates": [ { "id": "<recordId>",
               "updateFields": [ {"fieldName": "days_in_stock", "actionType": "SET", "setValue": 418} ] } ]
```

Sending `updateFields: {days_in_stock: 418}` — the obvious shape — is accepted and the node
returns **`{success: true, failedCount: 0, successCount: 0, errors: {}}`**. No error anywhere:
the workflow is green, the summary says "125 records rewritten", and not one record changed.
`successCount: 0` with a non-empty input is the only signal. **Always assert on `successCount`,
never on the node's own `success` flag.**

### 🔴 Storage filter comparison operators are the SHORT forms ✅

In `triggerInputCondition`, `{operator: 'GREATER_THAN'}` (and `GREATER_THAN_OR_EQUAL`,
`LESS_THAN`) fails the whole run with

```
Cannot invoke "_UIFilter$SimpleOps.getOp()" because ... "_UIFilter$FilterBlock.getOperator()" is null
```

The working names are **`GT`, `GTE`, `LT`, `LTE`**, alongside `EQUAL`, `NOT_EQUAL`, `IN`.
`IN` takes `value` with an array (not `values`) and works on `id` as well as `properties.*`.
Note the error names the *block* operator, which sends you looking at the wrong level.

### ⚠️ Hardcoding `resourceVersion` from another app's workflow

Cloning a sourcing build's nodes carried `storage_by_unifyapps_bulk_upsert_records_by_id` v16331 when the
tenant now serves **16333** (fetch 16417 → 16419, groovy 2609 → 2611, callables 3109 → 3126 /
3111 → 3128). Reads still worked on the stale version, so this is not always fatal — but resolve
them at build time (`GET /api/workflow-builder/node/{app}/resources`) rather than copying.

### 🔴 `loop_for_each`: `listSource` takes a PLAIN TEMPLATE, and mappedArray silently no-ops ✅

```json
{"type":"LOOP","context":{"appName":"loop","resourceName":"loop_for_each","resourceVersion":<resolve>},
 "inputs":{"captureIterations":false, "listSource":"{{ n_prep.outputs.result.items }}"}}
```

Three things, and the third cost an hour:

1. The input key is **`listSource`** — not `items` or `list`. Omit it and the violation names it.
2. The loop node needs **two incoming edges** — the one in, plus a `next` edge (name `loopback`)
   from the last body node back to the loop, or deploy fails with
   `Please add atleast 2 incomingEdges edge`. The current item is `{{ n_loop.outputs.item }}`.
3. **`listSource` must be a plain template string.** Given the `{source, items, "ua:type":
   "mappedArray"}` shape — which is correct for a Groovy parameter bound to a whole list, and
   which *deploys and validates cleanly here* — **the loop body never executes**. There is no
   error: the STOP node still returns whatever the pre-loop nodes computed, so a run that wrote
   nothing reports `{"written": 11588}` and looks perfect.

   How to catch it: bind the body node's own output into the STOP result
   (`"edgeOut": "{{ n_edge.outputs }}"`). If the key is **absent** from the response, the body
   never ran. Then verify the side effect itself — for edges, read the record back
   (`GET /api/context-graph/{g}/unifiedEntity/{ue}/records/{id}` → `edges[]`) or run the Cypher.

With the plain template: 11,588 `add_edge_to_graph` calls in 59 runs of 200, **74 seconds, zero
failures** — instead of one literal node per edge.

### Listing a context graph's node types ✅

There is no `GET /api/context-graph/{graphId}/nodes` (404) and no `?graphId=` variant (405). The
UI uses

```
POST /api/aggregation?entityType=KNOWLEDGE_GRAPH_NODE&group=STANDARD
{ filter:{op:'AND', values:[{field:'graphId', op:'EQUAL', values:['<graphId>']}]},
  projections:[{name:'id'},{name:'name'},{name:'unifiedEntityId'},{name:'cTm'}], page:{limit:80,offset:0} }
```

### 🔴 The graph engine behind the ECG API was absent on Orbit UAT ✅

Every ECG **endpoint** answers on Orbit UAT — you can create a graph, publish it, create node and
edge types, and write records into the entity store, all returning 200 — but when this was
checked there was **no graph engine behind it**, so every projection-backed read failed (below).
The graph header, node counts and edge counts still read back fine, which makes it look healthy.
The same build ran end to end on another tenant. **Before building a graph on Orbit UAT, run the
one-record probe** (`context-graph.md`): create one node type, publish, write one record, list it
with `POST /api/context-graph/{graphId}/nodes/{ue}`. 200 with a row = the engine is there; 500
`ServiceUnavailableException` = it is not.

### Node creation is slow, and a timed-out `javascript_tool` keeps running ⚠️

`POST /api/context-graph/nodes` takes ~35 s each (the graph re-projects). A 16-node loop exceeds
the 45 s browser-tool timeout — and **the script keeps running in the tab after the tool
returns**. Starting a second loop created 14 duplicate node types. Run long loops detached with
a progress object and poll; never start a second pass over the same work.

Same failure mode wrote `<uc>_order` twice: the first (timed-out) `JD.write` call completed in the
background, so the retry hit 8,308 `E11000 duplicate key` errors. Check the object count before
re-running a load.

### `POST /api/entity/{objectId}` filter shape

Top-level `{op, field, values}`, or `{op:'AND', values:[{op, field, values}, …]}` — **not** the
storage node's `{operator, filters:[…]}`. Sending the storage shape here returns
`Cannot invoke "Filter$Op.isCompound()" because ... getOp() is null`. The two surfaces genuinely
differ; §22 already warns about the reverse direction.

### An empty entity-type read is an EMPTY BODY, not 404

`GET /api/entity-type?entityType=<missing>` → **200 with a zero-length body**, so `r.json()`
throws "Unexpected end of JSON input". Read `r.text()` and treat empty as not-found. (Restates
§28; hit again here.)

---

## 35. Findings — an external HTTP service inside a workflow (UAT)

A build with 16 objects, ~11,200 records, 7 workflows, 13 data sources and 3 agents. The new
ground here is calling a **third-party HTTP service** from a workflow and turning its answer into
records.

### `custom_http_endpoint_execute` — the POST body shape that works ✅ UAT

The node's input schema is `dynamic: true` and its `body` field is generated from `bodySchema`
through a `DynamicSchemaField`, which makes it look as though a request body must be declared
ahead of time. It does not. **A plain `body` input, mapped from a Groovy step's output, is
accepted and sent as JSON:**

```json
{ "baseUrl": "https://<host>", "path": "/forensic-check", "httpMethod": "POST",
  "body": "{{ n_body.outputs.result }}",
  "requestTimeoutInSecs": 120, "sslVerify": true, "authType": "CUSTOM",
  "connectionType": "DIRECT", "requestContentType": "application/json",
  "responseContentType": "HEADER_BASED", "httpVersion": "HTTP_2",
  "followRedirects": "NORMAL", "isAsync": false, "enableProxy": false,
  "ignoreTrailingSlashes": false }
```

Outputs are `{{ n.outputs.status }}` (int) and `{{ n.outputs.result }}` (the parsed body).
Verified end to end: a base64-encoded PDF built in Groovy → POST → a JSON report back → findings
and a document record written → STOP, **2.3 s wall clock** through the data source. No connection
is needed, and no `bodySchema` had to be declared.

**Probing a node contract without creating a workflow** ✅ — `POST /api/test-workflow/initiate-test/{anyId}`
accepts an arbitrary path id when the full definition travels inline. `initiate-test/probe` ran a
three-node graph and reported `COMPLETED` in 333 ms. Useful for establishing an input shape before
committing a workflow to the tenant.

### Resource versions drift within DAYS, not months ✅

Between a sourcing build (2026-09-23, morning) and this one (same day, afternoon) on the same tenant:

| Action | Then | Now |
|---|---|---|
| `storage_by_unifyapps_fetch_records` | 16417 | 16419 |
| `code_by_unifyapps_groovy` | 2609 | 2611 |
| `callables_from_automation` | 3109 | 3126 |
| `callables_return_to_automation` | 3111 | 3128 |
| `callables_call_automation` | 3130 | 3132 |

Four of five moved inside one day. Resolve every version from
`GET /api/workflow-builder/node/{app}/resources` at build time — a stored version is a workflow
that will not save, later.

### Adding a field to an object, and using it immediately ✅

`POST /api/entity-type/update` with the object as read, the new property added to **both**
`input.schema.properties` and `schema.schema.properties` (and appended to `input.layout['ui:order']`),
→ 200, and a read-back shows it. `storage_by_unifyapps_bulk_upsert_records_by_id` with
`skipSchemaValidation: false` could write the new field on the next run — no republish, no
migration of existing records (a row without the field simply does not have it).

### `skipIfBlank: true` makes an empty bulk write a no-op ✅

`storage_by_unifyapps_bulk_create_records` and `..._bulk_upsert_records_by_id` both take
`skipIfBlank`. With it set, a run where Groovy produced an empty array succeeds and writes
nothing. That removes the only reason these graphs would need branching.

### Reading a run's node outputs is still blocked on this tenant ⚠️

`POST /api/lookup?ByKeys=TEST_WORKFLOW_VARIABLE` returned
`{response: {inaccessibleObjects: [runId], objects: {}}}` for every run of a workflow created over
the API, with or without an `options.workflowExecutionId`, and
`POST /api/workflow-runs/node-executions` returned zero rows. Status and `EXECUTION_TIME` from the
`WORKFLOW_EXECUTION` aggregation work. (Consistent with §18 D1.)

**So verify a workflow through its `e_data_source`, not through the test runner.** `POST
/api/workflow/execute/node?name={dsName}&requestId={dsId}` from a signed-in platform tab returns
the STOP node's payload directly, which is both the real call path and the only one that shows you
the answer.

### Groovy blacklist, again: `owner` ⛔

`rec.owner = assignee` → `Blacklisted commands found in code : owner = at position 957`. It is a
substring scan over the source, not a parse. `rec['owner'] = assignee` passes and behaves
identically. (Restates §30; the trap is easy to re-create because `owner` is a natural field name.)

### `skipIfBlank: true` silently swallows a restore-to-EMPTY ⛔ UAT

`storage_by_unifyapps_bulk_upsert_records_by_id` with `skipIfBlank: true` does not only guard
against an empty `updates` LIST — it skips an individual `setValue` that is blank. A control-room
reset that restores `ring_code` from `'RING-01'` back to `''` therefore reports success, moves the
record count it expected, and leaves the field set. Two claimants stayed in a fraud ring after a
"byte-identical" reset, with nothing in any response to say so.

It was never needed for the case it looks like it covers: with `skipIfBlank: false` an **empty
updates array is still accepted** (200, zero writes, no error). Set it `false` on every node whose
job includes clearing a field.

## 36. Findings — an app whose only source is the graph (verified on another tenant; confirm on Orbit UAT before relying on it)

Making **every** figure of an app a Cypher query turned up a set of things that all share one
shape: **the platform answered 200 and did nothing.** Every item below was found by running the
app, not by reading the response.

### 36.1 `/api/entity/update` needs the WHOLE entity ✅ verified

```
POST /api/entity/update  {entityType, id, properties}   → 200, returns the id, writes NOTHING
POST /api/entity/update  {...the whole object from GET /api/entity/{ue}/{id}, modified}  → writes
```

The partial form is accepted and silently discarded. Read the entity, change the field on
`properties`, post the entity back. This is the same shape `entity-type/update` needs (§8) and
the same trap.

### 36.2 Graph node records reject both bulk writers ✅ verified

A context-graph node's records are addressable as an object (`object_type` = the
`unifiedEntityId`) and read fine through `storage_by_unifyapps_fetch_records`. Writing is another
matter:

| Node | Result |
|---|---|
| `storage_by_unifyapps_bulk_upsert_records_by_id` | `{failedCount:1, success:false, successCount:0, errors:{"CUS-00678":"Service EntityService remote call failure"}}` |
| `storage_by_unifyapps_bulk_update_record_by_id` | `{failedCount:0, updated:0, errors:{}}` — **no error at all**, and nothing written |
| `storage_by_unifyapps_update_record_by_id` with `useRawPayload` and a **partial** payload | 500 `Non Empty Validations … required customer_code` |
| `storage_by_unifyapps_update_record_by_id` with `useRawPayload` and the **whole** properties map | ✅ writes, returns the updated object |

So a workflow that changes many graph records is a `loop_for_each` over a planned list with one
whole-payload `update_record_by_id` in the body — not a bulk node. The record's `id` IS its
primary key (`CUS-00678`), not a separate platform id.

### 36.3 "forbidden datasource : invalid input" means **republish** ✅ verified

A deployed interface fixes the set of data sources it may call **at publish time**. A data source
created — or edited — after the last publish is rejected at runtime with
`forbidden datasource : invalid input`, which reads like a malformed request and is not one.
`POST /agent-api/apps/{appId}/publish` and it works, with nothing about the data source changed.

Corollary: `resourceVersion` in a data source's `context` must match what the app sends. The
generated `bindings.ts` sends `{appName, resourceName}` with **no** `resourceVersion` for the
storage bindings, so the stored context must omit it too.

### 36.4 The OpenCypher action caps at 1,000 rows ✅ verified

`mdm_by_unifyapps_execute_opencypher_query` returns at most **1,000** rows whatever `limit` you
pass. A 3,330-row match asked for 4,000 comes back as 1,000 rows and, unless you cap your own
limit at 1,000, your "did we truncate" check (`count >= limit`) says no. Cap at 1,000 and the
flag stays truthful.

`ORDER BY` **is** applied before the limit ✅ — `ORDER BY at DESC` with a limit of 6 returns the
six newest, not six arbitrary rows. A trailing `LIMIT n` inside the query text, however, is
ignored; the action's own limit wins.

**Consequence for an app:** every total, count and share must be `sum()` / `count()` in the query.
Reducing over the returned rows is wrong above 1,000 records and looks completely normal —
Receivables reported 229M against a true 229.6M for exactly this reason.

**Consequence for an agent:** give the tool a small default `row_limit` (100) and a description
that says aggregate. An agent that omits `row_limit` and gets 500 full records per call burned
**471,035 tokens in one turn** and then looped. Budget characters as well as rows in the shaper.

### 36.5 Agents: four things between "configured" and "working" ✅ all verified

| Symptom | Cause |
|---|---|
| app gets `204 No Content` on `GET /api/entity/ai_agent/{id}` | the agent was never **deployed** — `POST /api/entity/action/saveAndDeploy` with the whole entity |
| agent behaves like a platform builder, `multiAgentConfig` names `tensor_builder`/`tensor_planner` | `agentType` is `team`, inherited by cloning another agent. It must be `ai-agent` |
| agent answers "I do not have access to the tool … access to the following records would be required" | the tool entity lacks **`enabled: true`**. It is not offered to the model at all, and the answer reads like a permissions problem |
| agent calls the tool but never varies the arguments | the tool's `inputs.parameters` were pre-seeded (`{cypher:'', row_limit:'500'}`). Use `parameters: {}` and let the automation's START schema supply the shape |

`POST /api/entity/update` on `e_action_ai_agent` **rejects** an unknown property:
`Non Empty Validations … add additionalProperties excludeInputOutputFromTrace`. Copy only the
fields a real tool already has.

### 36.6 Read the node → unifiedEntityId map back; never transcribe it ✅

`POST /api/aggregation?entityType=KNOWLEDGE_GRAPH_NODE&group=STANDARD&name=context_graphs_nodes_table`
returns every node of a graph with `name`, `id` **and** `unifiedEntityId`. `GET
/api/entity-type?entityType={ue}` gives the same `name` one at a time.

This matters because a label that exists always matches something. A map transcribed in creation
order was wrong for **twelve of sixteen** node types — `Order` pointing at Invoice's entity,
`Employee` at Product's — and every query still returned plausible rows.

### 36.7 An ECG does not denormalise foreign keys

Node types built from `<uc>_order` / `<uc>_invoice` carried no `customer_code`: the counterparty is
reached by relationship, which is the point of mastering it once. Any per-customer read is a
traversal:

```cypher
MATCH (i:`<invoice_ue>`)-[:OWED_BY]->(c:`<customer_ue>`)
WHERE c.`_pr_customer_code` = 'CUS-00181'
```

A screen that filters on `customer_code` instead matches nothing and renders as an empty state,
not an error. When porting a screen from objects to the graph, check every filter field against
`GET /api/entity-type?entityType={ue}` first — two phantom fields (`customer_code`,
`since_year`) and one missing one (`freshness_hours`, which crashed a screen on `.toFixed()`)
were all found this way.

### 36.8 `resourceVersion` differs between tenants

Action versions on one tenant say nothing about another (`callables_call_automation` differed by
more than a thousand between two tenants). Always resolve from
`GET /api/workflow-builder/node/{app}/resources` on Orbit UAT. Carrying a number across tenants gives
`No config found for resource … in app …` from ConnectionService.

Also: the LLM node is `type: 'CALL_INTERFACE_WORKFLOW'`, not `ACTION`, whenever `inputs` carries
a `callableInterfaceId`. As an `ACTION` it fails with the same "No config found" error.

### 36.9 Cloning a workflow clones its prompt

A writer workflow cloned from another build kept that build's system prompt, so every line of
narrative in the new app was written by an engine told it worked for a different company in a
different country. Nothing failed. Read and rewrite the prompt of anything you clone.

### 36.11 The agent's model is `answerGenerationModelSettings.modelId`, not `answerGenerationModel` ✅

An agent cloned from a template carried `answerGenerationModel: <Sonnet 5>` **and**
`answerGenerationModelSettings.modelId: <Gemini 3.8 Flash>`. The settings block wins, so the
declared model was never used, and `topicSelectionModel` / `topicExecutionModel` were Flash too —
the whole tool-calling loop ran on a model nobody chose.

The failure signature is diagnostic: several fast tool calls, then **four model calls of
~190–300 ms each** and an error. That is the platform retrying an output it cannot parse — the model
fumbling the exact-JSON chart contract — and it surfaces to the user as "The AI response
contained corrupted internal data". It is not a data problem and not a permissions problem.

Also set `responseGenerationSettings.disableThought: true` for a tool-calling analyst: thinking on
every hop costs seconds and buys nothing when the instructions already prescribe the method.

**The graph is never the slow part.** Across every trace it is 1–3% of wall clock; measured
directly, a count is 396 ms cold / ~100 ms warm, a grouped aggregation 102 ms, 1,000 rows 114 ms,
and a 2-hop traversal aggregation 161 ms. If an agent feels slow, read the trace timeline before
touching the data layer.

### 36.12 An empty parameter is a caller priming, not a fault

`mdm_by_unifyapps_execute_opencypher_query` answers an empty `query` with a 500 `query is
required`. A hook that builds its query from a route parameter fires once before the parameter
exists, so Customer 360 logged **four red calls on every load** while rendering perfectly. Four
false failures per page hide the real ones.

Guard it in the workflow, not only in the caller: decide in Groovy (the template language has no
ternary) and bind the action to the result.

```groovy
def cy = p('cypher')?.toString()?.trim()
boolean blank = (cy == null || cy.length() == 0)
def query = blank ? 'MATCH (n) WHERE false RETURN n' : cy
return [limit: n, blank: blank, query: query]
```

…with the action bound to `{{ n_lim.outputs.result.query }}` and the shaper returning
`skipped: blank`, so the caller can tell "nothing asked" from "nothing found".

### 36.13 Read-after-write lag, and what it destroys

This tenant returns a stale read for a few seconds after a write. Two consequences, both found
the hard way:

1. **A verification that reads immediately reports false failures.** A scenario-battery run
   measured 7 of 13 levers as "did not restore"; with a 4-second settle before each read, all 13
   restore exactly and the dataset comes back byte-identical to baseline.
2. **A read-modify-write pipeline running close behind another write silently drops columns.**
   A source-rename job read 43 gold tables before an earlier backfill had settled and wrote them
   back without `freshness_hours`, which then crashed the screen on `.toFixed()`. Always settle,
   and prefer re-deriving from an untouched source (the `<uc>_*` objects, which graph writes never
   touch) over trusting what you just read.

### 36.16 Validate a model's output before you store it

Four Customer 360 insights generated, parsed and stored cleanly — and rendered as four cards with
a severity pill and nothing else, because the model had returned four objects under different key
names and `String(x.title || '')` wrote empty strings without complaint. The count looked right at
every step. Validate the fields you actually need before writing, and have the component skip a
record that is empty: an empty card is worse than no card.

---

## 37. Findings — running a real document corpus through a workflow (UAT)

165 real PDFs put through one intake workflow, 0 errors. Everything below was found by running
it, not by reading a response: the platform returned 200 for all of it.

### 37.1 `bulk_upsert_records_by_id` wants `updateFields`, not `properties` ✅ verified

The node's `updates` array is **field-level**, not record-level:

```jsonc
// storage_by_unifyapps_bulk_upsert_records_by_id
{ "object_type": "<uc>_claim", "skipIfBlank": false, "unsetIfNull": false,
  "updates": [
    { "id": "<record id>",
      "updateFields": [ { "fieldName": "risk_score", "actionType": "SET", "setValue": 74.6 } ] } ] }
```

An array of `{id, properties:{…}}` — the shape `POST /api/entity/update` takes, and the obvious
guess — is accepted with **HTTP 200 and writes nothing**. The workflow reports however many rows
it built; the records are untouched. The first run of a rescore said `rescored: 165` and changed
zero records. **Read one record back after the first batch**, not just the count the automation
returns.

Upside of the field-level shape: it is a genuine partial update, so it does not carry golden
rule 3's whole-record-replace hazard. `useRawPayload` on the *create* node still does.

### 37.2 A START node created over the API must carry its trigger ✅ verified

`POST /api/workflow-definition` accepts a START node without `trigger`; the follow-up
`saveAndReturnViolations` then 500s:

```
Cannot invoke "…triggers.Trigger.getType()" because the return value of "…nodes.Node.getTrigger()" is null
```

Add `trigger: { type: "CALLABLE" }` to the START node (alongside `context.resourceName =
callables_from_automation`). Note the create still **succeeded** and left a workflow behind, so
re-running the whole builder makes a second one — fetch the definition that exists, fix it, and
save that.

### 37.3 `fetch_records` output is `outputs.objects`, and `triggerInputCondition` must be present

- The collection a fetch node emits is `{{ n_x.outputs.objects }}`. `outputs.records` resolves to
  nothing and the downstream Groovy sees an empty list — again, 200 throughout.
- Omitting `triggerInputCondition` entirely returns nothing. To fetch everything, send
  `triggerInputCondition: {}`.
- `page.limit` of 1000–2000 returned all rows at these volumes (165 claims, 100 findings).

### 37.4 A data source sends **every** templated input, always ✅ verified

`<uc>_query` declares 15 templated parameters. Calling it with only `{object_type, limit}` came
back `count: 0` for an object holding 8 rows: the unset `{{filter_field}}` placeholders reach the
workflow as the literal template text and it filters on them. Send every templated parameter,
blank where unused. This is the read-side twin of `forbidden datasource : invalid input` on the
write side — there the platform tells you; here it just answers zero.

### 37.6 A record whose `id` you set is a record whose business key you cannot rename

`<uc>_check` records were created with `id` = the check id, so `id == properties.check_id`. When
the forensic engine turned out to emit `pdf_structure_forensics` / `font_resource_forensics`
while the catalogue called the same two checks `pdf_revision_recovery` / `retypeset_forensics`,
the catalogue **could not** be renamed to match — changing `check_id` would mean a new record and
abandoning the old one (never delete). The fix went the other way: the
**emitter** was changed to the catalogue's ids and the 23 findings already written were realigned
with `POST /api/entity/update`.

Worth knowing before you choose ids: an explicit `id` is a permanent primary key. Use it for
things whose identity is genuinely fixed, and let the platform mint ids for anything whose naming
might still move.

## 38. Findings — entity updates and call nodes (UAT)

### 🔴 `POST /api/entity/update` REPLACES `properties` wholesale ⛔ UAT

Sending one field does not merge it — every other property is dropped. A card updated with
`{properties:{screenshots:'…'}}` came back as a record whose *only* property was `screenshots`:
title, slug, description, categories, customer, videoUrl and sortOrder were gone, with a 200 and
nothing in the response to say so. There is **no version history** to roll back to
(`…/versions`, `…/history` both 404), and a record belonging to an app's own object is not
necessarily in a backup snapshot either.

- **To write one field**, use `storage_by_unifyapps_bulk_upsert_records_by_id` (v16331) with
  `updateFields:[{fieldName, actionType:'SET', setValue}]`, which is a true partial update.
- **To use `/api/entity/update` at all**, read the record first and send **every** property back.
- It also takes an optimistic lock: omit `version` and the second write fails with
  `ENTITY with id … and version 0 is stale, current version is 1`. The *first* write succeeds
  precisely because version 0 is current — so the destructive call is the one that goes through.

Recovering a wiped record without a backup: the sibling records reconstruct it. A seeded series
carries two independent sequences — `sortOrder` and a numeric slug suffix — and both had exactly
one gap (103 / `-3`), which fixes the lost values rather than guessing them.

### Reading entities and records over REST ✅ UAT

| Call | Returns |
|---|---|
| `POST /api/entity/{entityTypeId}` `{page:{limit,offset}}` | every record with **full `properties`** |
| `GET /api/entity/{entityTypeId}/{recordId}` | one record, incl. its `version` for the lock |

This works for app objects *and* for platform types. **`GET /api/entity/e_interface/{appId}`
returns `properties.name`** — the app's real name — which the `standard_entities_fetch_entities`
action cannot project (§ it yields only `id` and `tags`). So an app's name IS readable
server-side; the action is the limitation, not the platform.

`/api/entity/search` is a different thing entirely: it searches the `search` entity and silently
ignores an `entityType` in the body, answering 200 with unrelated rows.

### 🔴 `callables_call_automation` is a `CALL_WORKFLOW` node, not an `ACTION` ⛔ UAT

Built as `type:'ACTION'` it saves and **deploys** clean, then fails at run time with
`No config found for resource callables_call_automation in app callables` (ConnectionService).
Correct node: `type:'CALL_WORKFLOW'`, context `{appName:'callables',
resourceName:'callables_call_automation', resourceVersion:<resolve>}`, inputs
`{automationId, version:'-1', synchronous:true, parameters:{}}`.

Resolve the version, never copy it: `GET /api/workflow-builder/node/callables/resource/callables_call_automation`
→ `.version` (**3133** on Orbit; 3124 is stale and also fails). That response also
carries `nodeType`, which is how you learn the node type a resource wants.

⚠️ **Disputed — see §18 D5** (a build tool master runs `<id>` and `<id>` COMPLETED through initiate-test with a resolved call-node version; this case used a stale version 3124). **`initiate-test` cannot run a call-workflow node at all** — it fails there regardless of whether
the node is correct, so a green test run is not evidence and a red one is not a bug. Verify
through the app's `e_data_source` (the real call path), per §33. This is how a daily job that had
been deployed for a day was found never to have been able to run.

## 39. Findings — testing a finished graph-backed app (verified on another tenant; confirm on Orbit UAT before relying on it)

A finished-looking app rendered every screen with no console error and still had field defects,
one wrong agent answer and wrong figures on stored insight cards. The pattern: *the platform
succeeded at something other than what was meant.*

### 39.2 A transaction's counterparty is a traversal — use OPTIONAL MATCH ✅

Joining the customer onto a ledger with a plain `MATCH` silently **drops** every record whose
edge is missing, so the table loses rows while the count beside it does not. `OPTIONAL MATCH`
keeps the row set identical to the flat read and only fills the name in:

```cypher
MATCH (n:`<invoice ue>`) WHERE toFloat(n.`_pr_balance`) > 0
OPTIONAL MATCH (n)-[:OWED_BY]->(c:`<customer ue>`)
RETURN …, c.`_pr_customer_code` AS customer_code, c.`_pr_name` AS customer_name
```

Verified: 1,113 rows and 230M before and after, with names on every row.

### 39.3 Categorical values are an enum; `CONTAINS` silently conflates them ✅

Every ECG property is a string, so `CONTAINS` always compiles and always returns something
plausible. Asked for the 90+ ageing bucket, the credit agent wrote
``ageing_bucket CONTAINS '90'`` and answered **78.7M across 382 invoices**. The truth is
**60.3M across 295** — `'61-90'` also contains "90", and 295 + 87 = 382 exactly.

The fix is not a better instruction to "be careful". Put the **actual value lists** in the
agent's prompt (`RETURN DISTINCT n.\`_pr_<field>\``, once per categorical property) and require
`=` or `IN [...]`. The traps are the pairs: `61-90`/`90+`, `expiring`/`expired`,
`service`/`services`/`parts_service`, `in_stock`/`in_transit`. After the change the same
question returned 60,276,324 across 295, source line ``ageing_bucket = '90+'``.

### 39.6 Audit stored LLM findings numerically, not just for citations ✅

28 stored insights, every one citing real record codes, every code real. **Ten still carried a
wrong number.** Each figure has to be re-run against the engine:

- a total that contradicts the sum of its own components (61.4M over six brands that sum to
  64,619,740 — the per-brand figures were all correct)
- a count taken from the four examples named rather than the population (4 certified-but-not-
  answerable measures; there are 10)
- a superlative that is simply not true ("the largest absolute breach in the book" — it is 4th;
  "the worst reading in twelve months" — July was worse)
- an inference contradicted by the data it cites ("1,254 missed SLA … dragging satisfaction",
  when unmet jobs carry *higher* CSAT — 3.72 against 3.67)
- a headline framing a 7-month low as a spike (overdue 5.07%, down from 12.72%, against a 12%
  target, titled "Overdue receivables spike")
- a figure the generator computed without the cancelled-order filter (§39.4)

A citation proves a record exists. It does not prove the arithmetic, the superlative or the
causal claim. Re-run every number.

### 39.7 The app origin's data-source path is not the console's ✅

From the app origin the data sources are called at
`POST /api-endpoint/external/workflow/execute/node?name=<ds>&requestId=<dsId>`, body
`{id, context, inputs}`, cookies only. The console's `/api/workflow/execute/node` returns **401**
from the app origin and `forbidden datasource: not found` from the console. This is the way to
read and write an app's objects from outside the React app — the storage bindings in
`bindings.ts` give the exact `context` and `storedInputs`.

⚠️ `triggerInputCondition` on `storage_by_unifyapps_fetch_records` was **ignored** in this shape:
a filter on `properties.scenario_code = 'SCN-04'` returned SCN-13. Fetch the page and filter in
the caller, or verify the filter actually bit before trusting a single-record read.

### HubSpot connector: property discovery, lever history, second pipeline ✅ UAT
- The `hubspot` node has **no list-properties action** (106 resources; none reads the property catalogue).
  Discover a custom property by requesting it on `hubspot_get_deal` (`properties: [names…]`): existing
  properties with a value come back, **null-valued properties are dropped by the connector**, unknown
  names are ignored. So absence ≠ nonexistence — probe a deal known to carry values.
- `hubspot_get_deal` `propertiesWithHistory` works for **custom** single-selects: `propertiesWithHistory:
  ["dealstage","buyer_zone","case_for_change",…]` → `{value, timestamp, sourceType, sourceId, updatedByUserId}[]`
  per property (sourceType CRM_UI / AUTOMATION_PLATFORM / PROPERTY_DEFAULT_VALUE).

### Workflow authoring gotchas ✅ UAT

- **Groovy `0G` is a `BigInteger`**, not BigDecimal: `def delta = 0G; delta.setScale(1, …)` fails with
  *No signature of method: java.math.BigInteger.setScale()*. Use `0.0G` for decimals (`2.0G`, `-2.0G`).
- A `CALL_WORKFLOW` node (`callables_call_automation` rv 3133) exposes the called workflow's STOP result
  **flat**: `{{ n_c1.outputs.deals }}`, `{{ n_c1.outputs.next_after }}` — there is no `.response` layer
  inside a workflow (the `.response` envelope exists only when an APP data source executes it).
- `storage_by_unifyapps_bulk_create_records` (rv 16416, `useRawPayload:true`, `rawPayload: <list of records>`)
  returns `{errors:{}, inserted:<n>, insertedIds:[…]}`; 300 rows in one node run in ~2 s. The Groovy
  that builds the rows must coerce numbers (`new BigDecimal(str(v))`) — values arriving from a called
  workflow are strings/doubles mixed.
- HubSpot search sorted by `amount DESCENDING` with `limit 100` pages fine with `after` (cursor is the
  offset as a string, e.g. `"100"`).

### Storage fetch filter on a string date; test-run limits ✅ UAT
- `triggerInputCondition` on a string field holding `YYYY-MM-DD`: `{operator:'GTE', value:'2026-08-10'}` ✅;
  `GREATER_THAN_OR_EQUAL` → *Workflow execution failed* (500). `IN` with an explicit list of dates also works.
- Orbit UAT can have short outages: `/api/user-context` 500 and `/agent-api/*` 503
  *"permission check is temporarily unavailable"* for every session; wait, do not retry writes blindly.
- `POST /api/test-workflow/initiate-test/{id}` returns 500 *No Response received within specified timeout*
  and the run ends CANCELLED when the workflow runs past roughly a minute (seen with 10 chained
  CALL_WORKFLOW nodes). Production scheduled runs are not listed under
  `group=TEST_WORKFLOW_EXECUTION`; PROD/LIVE/WORKFLOW_EXECUTION/STANDARD groups are all *Invalid group*.
- Storage fetch node / FETCH data source accepted `page.limit` 5000 and `sortBy:[{field:'properties.x', order:'DESC'}]`.

### More workflow facts ✅ UAT
- A workflow can **vanish** after a platform outage (404 afterwards, not listed). Recreate it and repoint every
  CALL_WORKFLOW node and every `callables_call_automation` data source that named it (the data source's
  `automationId` is a stored input: update the entity).
- `loop_for_each` does not collect per-iteration results. Write each iteration to a storage object
  (bulk upsert with `updateFields`) and read the object after the loop.
- A storage object's field with a `oneOf` enum (e.g. `kind`) rejects new values until the schema's `oneOf`
  is extended.
- An agent skill (`e_skill_ai_agent`) edited with `POST /api/entity/update` stays a draft until `saveAndDeploy`,
  which would also publish every other pending draft of that skill.

## 40. Findings — a 58,000-record build (UAT)

**40.1 The fetch node's count is `total`, not `totalCount`** ✅. `storage_by_unifyapps_fetch_records` with
`includeTotalCount: true` outputs `{objects, total, hasMore, cursor}`. `{{ n_fetch.outputs.totalCount }}` resolves to
nothing, silently — a claim-review build `<uc>_query` clone has reported an empty `object_total` since it was
built, and an aggregate that trusted it said "computed over all 0 matching records". Use `{{ n.outputs.total }}`.

**40.2 `[:] as Set` is immutable in the Groovy sandbox** ⛔→✅. It coerces an empty map to an unmodifiable set;
the first `.add()` throws `UnsupportedOperationException`, which the node reports as `{errorCode:-1}` with no
message. It only fires on the path that adds, so a one-record test passed and the 2,000-record run failed.
Use `new HashSet()`. **Debugging recipe that found it:** re-run the definition through `initiate-test` with the
Groovy wrapped in `try { … } catch (Throwable e) { return [err: e.toString(), at: e.getStackTrace()…] }` and
the STOP node returning `err` — the stack gives the script line.

**40.3 A search on `e_data_source` must filter on `properties.interfacePageId`** ✅.
`POST /api/entity/e_data_source` filtered by `properties.interfaceId` → `500 "Search on e_data_source requires a
properties.interfacePageId filter"`. Filter on `e_global_<appId>`.

**40.5 Tens of thousands of small `POST /api/entity` calls freeze the hidden browser pane** ⛔→✅. Three tabs in a
row stopped responding mid-load (even `1+1` timed out) after ~1 minute of 12–32 parallel workers. Load volume
through the platform instead: a four-node workflow (`<uc>_bulk_load`: START {object_type, rows_json} → Groovy
`JsonSlurper` → `storage_by_unifyapps_bulk_create_records` `skipUpdate:false` → STOP) run with
`initiate-test`, 1,000–1,500 rows per call: **1,000 records in < 8 s**, 25,389 touchpoints in 7 calls, no freeze.
Resume by reading existing ids with `POST /api/aggregation … projections:[{name:'id'}]` in 5,000-row pages.

**40.6 A generated dataset object that is never registered loads zero rows, silently.** The seed built
`students` in its own array and never put them in the output map; the loader reported `<uc>_student: 0 rows`
with 0 failures and the baselines for that object were never written. Print per-object counts before loading
and assert every schema object has rows.

**40.8 Bulk-create rejects duplicate primary keys inside one batch.** The withdrawal cascade minted
`TP-B-WD-<student>-ADVISING` twice (interventions closed + caseload updated); the whole bulk create failed
after the upserts before it had succeeded — a half-applied cascade returning HTTP 500. Suffix an index.

**40.9 Writers sum figures across processes unless told not to.** Given 9 people (adjunct pay) and "up to 30"
(donation-to-cash), the writer produced "39 staff", and an agent applied "up to 30" as a ceiling to every process.
Say it in every system prompt and agent instruction: never add people/systems/steps across divisions, and name
which process each figure belongs to.

**40.10 Tool-level timings on UAT (deployed, via data source):** retention watch over 2,000 students 1.0–1.4 s;
intelligent to-do list (with its writing step) 8–9 s; payroll three-way match 0.8 s; gift-to-cash over 2,411 gifts
1.4 s; driver merge 2.1 s; withdrawal cascade 0.6 s; curriculum review 13 s; content plan 24 s; screen insights 26 s;
docked agent answer with a chart ~35 s (Gemini 3.8 Flash settings cloned from a claim-review build analyst).

**40.12 Cheap exact counts: `POST /api/entity/{objectType}` with `includeTotalHits: true`.** Body
`{filter:{op:'AND',values:[{op:'EQUAL'|'IN',field:'properties.x',values:[…]}]}, page:{limit:1,offset:0},
includeTotalHits:true}` returns `totalHits` in ~100 ms — the right tool for verifying a load or a reset
fingerprint at 170k records (a workflow aggregate pages through every row).

**40.13 Scale that holds on UAT (a student-lifecycle build, 167,958 records, 22 objects):** `<uc>_bulk_load` (Groovy JsonSlurper →
`bulk_create_records`) at 1,500 rows per call ≈ 17 s per initiate call, 128 calls ≈ 35 min; one call returned
500 "No Response received within specified timeout" and was resent (upsert by primary key, so idempotent).
A fetch node with an `IN` filter of ~2,900 codes and `limit: 5000` works; a targeted retention sweep over
7,087 students (read active signals → read only students with one, on the watch list, or with a stale count)
runs in 2.5 s. A 20-page aggregate (100k rows) replaces the 6-page one.

## 42. Findings — loading a large graph (verified on another tenant; confirm on Orbit UAT before relying on it)

**42.1 `storage_by_unifyapps_bulk_create_records` INTO a graph node type works ✅ another tenant.** `object_type` =
the node's `unifiedEntityId`, `useRawPayload:true`, `rawPayload` = a JSON array of records (all values
strings), `skipUpdate:false`. 1,000 records per call in ~1.4 s when the workflow is run synchronously
through an app data source (`POST /api/workflow/execute/node?name=<ds>&requestId=<dsId>` with header
`x-ua-app`); the STOP result carries `insertedIds[]`. 199,300 records in 37 node types loaded in ~50 min.
Corrects §36.2's implication that every bulk writer fails on graph records: bulk **create** is fine; the
bulk **update/upsert** writers are the ones that do not touch graph records. About 1 initiate-test run in
50 fails at `n_bulk` with no message under load; a re-run of the same slice succeeds (upsert by primary key).

**42.2 Projection lags the load by minutes, per type.** After every bulk create returned, `MATCH (n)`
counts trailed the plan for ~10 minutes (Registration 0 → 5,531 → 14,174). Verify counts after a pause,
not after the write, and never write relationships to a type that has not finished projecting — a
`MATCH` on an unprojected node simply matches nothing and `MERGE` writes no edge, silently.

**42.3 Relationships: `mdm_by_unifyapps_execute_opencypher_update` (rv 336) with `UNWIND … MATCH … MERGE` ✅**
— the fast path. `MATCH (a:\`<ue>\`) WHERE a.id = r.f` on the node's `id` property (`<org>::<ue>::<pk>`,
e.g. `90::<id>::TP-000001`, indexed) writes 100 edges in **364 ms**; the same by the `_pr_` primary-key
property takes **8.6 s** (label scan). 500 per call stays under the 20 s synchronous limit. Returns only
`{success:true}` — count the edges with a Cypher read afterwards. `SHOW INDEXES` is rejected by the
Cypher-DSL rewriter.

**42.4 The `loop_for_each` + `add_edge_to_graph` writer (§36 a graph-only analytics build) was unusable here ⛔ another tenant.**
`POST /api/test-workflow/initiate-test/{wf}` on that workflow returned 500 `No Response received within
specified timeout` on every attempt (5 edges, 84 edges, captureIterations true or false) while the same
call on a bulk-create workflow succeeded throughout. A synchronous run through its data source is
**CANCELLED by the platform at 20 s** mid-loop (2 of 84 edges landed); `callables_call_automation_async`
(`synchronous:false`) returned `{result:true}` in 173 ms and wrote nothing. Use 42.3.

**42.5 A graph's auto-created MDM connection is now named `<graph name> Ontology Connection`** (was
`… UDM Connection`, §12). Find it with the lookup and match `/ontology connection|udm connection/i`.

**42.8 Writing graph records — what reaches the store and what does not ✅ another tenant.**
| Write | Store (`GET /api/entity/{ue}/{id}`) | Projection (Cypher) | Edges kept |
|---|---|---|---|
| `storage_by_unifyapps_update_record_by_id`, whole payload | ✅ | ✅ (seconds) | ✅ |
| `storage_by_unifyapps_bulk_create_records` on an EXISTING pk, `skipUpdate:false` | ✅ — it is an upsert that **REPLACES the whole record** (a payload of 2 fields leaves a record of 2 fields; verified 03:55 after an earlier "merge" reading that was only the read lag) | ✅ | ✅ |
| `execute_opencypher_update … SET n.\`_pr_x\` = …` | ⛔ unchanged | ✅ changed | — |
| `execute_opencypher_update … MERGE (a)-[:L]->(b)` | edges appear in the record API's `edges[]` ✅ | ✅ | — |
So: bulk create is the mass-update path for a sweep, and the payload must be the WHOLE record (read all
properties by Cypher, change fields, write everything back) — a partial payload deletes what it omits.
Never SET a property by Cypher — the store keeps the old value and the next re-projection will disagree
with the screen. **Read-after-write lag is 5–15 s on the store and minutes on the projection after a bulk
load**: a workflow that reads records the projection has not caught up with writes them back WITHOUT the
fields it could not see (this is how 41 drivers, 71 certificates and 10 gifts lost their `baseline_json`
after a 62k-record backfill was followed too soon by Brain runs). After any bulk load, wait until
`MATCH (n) WHERE n.\`_pr_<new field>\` IS NULL` is zero before running anything that writes.

**42.9 `callables_call_automation` with `synchronous:false` executes ✅.** A data source cloned with
`inputs.synchronous=false` returns `{result:true}` in ~110 ms and the run completes in the background
(a record created by it appeared 12 s later). The earlier "async wrote nothing" (42.4) was the loop
workflow's own failure, not the async path. Use it from an app for anything longer than the 20 s
synchronous limit, and read the outcome back from the graph.

**42.10 Porting storage workflows to the graph by TRANSFORMATION  ✅.**
19 workflows moved from Data Objects to the ECG without rewriting their Groovy. What had to change:
- a storage `fetch_records` node exposes `{{ n.outputs.objects }}`; a Groovy node that replaces it exposes
  `{{ n.outputs.result.objects }}` — every downstream reference must be rewritten;
- `mdm_by_unifyapps_execute_opencypher_query` answers `{stats, objects:[…], success}`; bind
  `{{ n_q.outputs.objects }}` to an array parameter — binding the whole Map to an array parameter arrives
  EMPTY with no error;
- graph properties are strings, so `active == true` / `receipted == false` in the original logic silently
  fail; the shaper hands 'true'/'false' back as booleans;
- a spec that paged its own reads (offset 5000) must keep the offset or the second page repeats the first
  (one student scored 66 from her 2 signals counted twice);
- generated Groovy nodes need their own `def g = { k -> binding.hasVariable(k) ? … }` — the original PRE is
  not inherited ("No signature of method: Script.g()");
- a Groovy map literal is `['k': 'v']`, never JSON `{"k":"v"}` ("Unexpected input: ':'") — the deploy step
  compiles every script, the save step does not;
- relationships written right after a bulk create can miss the not-yet-projected nodes: keep the link key
  on the record and run an idempotent `<uc>_link_orphans` (`MATCH (a) WHERE NOT (a)-[:L]->() … MERGE`) after
  every run — 933 ms over 200k nodes.

## 41. Findings — generating 109 workflows from one design (UAT)

**41.2 Generating 109 workflows.** One generator (`<script>` node helpers + a `wire()` that turns nested
`{if, then}` / `{each, body}` items into group ids and `if`/`loop`/`loopback` edges) built and deployed all 109 in
~13 s at 4–5 in parallel (`saveAndReturnViolations` → `deploy?version=`). Deploy is where Groovy compiles: the only
errors were a literal newline inside a single-quoted Groovy string (JS template escaping) and a helper defined only in
one prelude. Put shared helpers in ONE prelude; a second `def` of the same closure name in the same script is a
compile error.
- IF branch with nothing after it inside a loop body: add a no-op rejoin node, so the IF's `no` edge and the loopback
  are different edges (both would otherwise be `next@<if>@<loop>`).
- `loop_for_each` over a list that may be empty: pass `['__none__']` and guard the body with an IF on a flag the split
  node computes — otherwise the body runs once on the placeholder.
- The UnifyApps HTTP node cannot decompress: eCFR's `versioner/v1/full/...` returns **406 "requires response
  compression"**; the renderer `GET https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-21?chapter=I&subchapter=E&part=501`
  returns the official HTML uncompressed (132 KB) — use it.
**41.3 One data source per workflow — a generic dispatcher is refused.** A workflow whose CALL_WORKFLOW node takes
`automationId` from an input (run any workflow by id) was refused by Claude's permission classifier as a
remote-execution surface. Register one callable `e_data_source` per workflow the app runs (here 119), and keep the
map (name → data source id, automation id, parameters) in the repo as JSON read back from the tenant.

**41.5 Timings (deployed, via data source).** An abstaining agent with its ledger + resolution calls: ~0.4 s. An LLM
extraction or judgment agent: 4–10 s. The whole 20-step master workflow on an empty scope: 3.2 s (12 envelopes, 5
inbox items). SW-21 claims review of one product (1 classification + a rule match and a prohibited screen per claim,
13–19 claims): ~60 s.

**41.9 Deterministic codes make sub-workflow re-runs idempotent ✅.** Claim codes `CLM-<cycle>-<target>-<sha256(text)[0:8]>`,
gap codes `GAP-<asin>-<cls>-<sha256(cycle|cls|finding)[0:8]>` and opportunity codes derived from them: a re-run
FETCHes what exists, CREATE_MANYs only new codes, and UPSERTs pending claims in place (decided ones untouched).
Verified: SW-21 twice on one product → 13 claims, then the same 13 re-evaluated (rule matches refreshed), no
duplicates. The LLM classifier (AG-69) returned the same 13 claim texts both times.

**41.10 Connectors SDK — refreshable custom auth, templates, and failure handling (UAT).**
- *Refreshable CUSTOM auth*: the saved auth request carries `defaultExpiry`, `defaultExpiryUnit`, `expiryType`
  (`RELATIVE` | `ABSOLUTE`), `expiryTime` (string), `expiryUnit`, `refreshable`, and a `refreshCredentials` request
  object (method/url/headers/body/output — the UI shows no Body field for it, but a `body` set over the API persists).
  `POST /api/connector-builder/request/{defId}/CUSTOM/auth` answered **500 "ConnectorRequestService remote call
  failure" but had saved the request** (read back with GET) — always read back before retrying.
  A form-encoded token call: `body:{type:"JSON", formEncode:true, payload:{grant_type:"refresh_token", …}}`;
  `POST /api/connection/input/test` with fake credentials returns the provider's own 401 — egress and encoding
  proven, nothing saved.
- *Action templates*: `{{ input.auth.<field> }}` is a connection field in query/body; a whole-value template keeps
  its type (array → JSON array, number → number); Groovy runs (`{{ rawPayload.values.collect { [value: it] } }}` →
  array of objects); an **absent** action input drops its query parameter entirely, an **empty string** is sent as
  `key=`; an absent body value drops the key, inline it renders `null`. In `actionAuthHeaders`, `{{ auth.<output> }}`
  renders but a connection field via `{{ rawPayload.<field> }}` does **not** (header omitted) — put per-connection
  headers on each action.
- *`connectionId` must be a literal, existing connection* at save time: a template (`{{ n_in.outputs.connection_id }}`)
  is a violation "Connection is no longer available" and the workflow does not deploy.
- ⛔ *Failure handling, settling D2*: a Connectors-SDK action answering HTTP 500, run through an app data source,
  **failed the whole run with `fallbackMode: CONTINUE`**, and **also with `MANUAL` + an `error` edge** (edge
  `error@n_f@n_h`, name `error`, handler in group `n_f@g1@error`). Design for it: one unit of work per run, record the
  attempt before the external call, let the scheduler retry, and cap attempts.
- *Gzip in Groovy* ✅: `new java.net.URL(u).openConnection()` → `getInputStream().bytes` →
  `new java.util.zip.GZIPInputStream(new ByteArrayInputStream(raw)).bytes`. Pre-signed storage URLs are downloaded
  without the connector (which would add its own headers).

**43.4 Storage records of custom objects update through the entity API ✅ UAT.** `GET
/api/entity/<object>/<recordId>` then `POST /api/entity/update {id, entityType:<object>, properties,
version}` with the full properties (200, read back).

- **Concurrent decisions race**: four records decided in parallel each saw the others pending, so a gate
  that depended on all of them never flipped. Decide the gate where it is read.
- Long sub-workflows (≈3 min, one LLM call per item) outlive a 200 s client wait on the data-source call; the run
  continues and completes server-side — poll the records, don't retry.

## 44. Findings — agent create and publish, entity tags (UAT)

**44.1 `ai_agent` create rejects `sendSuggestedQueries` ✅ UAT.** `POST /api/entity {entityType:'ai_agent'}`
with `properties.sendSuggestedQueries` → 500 *Non Empty Validations … additionalProperties
sendSuggestedQueries*. Leave it out on create (agents.md §"An agent cloned…" suggests setting it; that
only applies to an update of an entity that already carries the key).

**44.2 Agent publish races its own tool/task writes ✅ UAT.** Creating `e_action_ai_agent` / `e_topic_ai_agent`
rows bumps the agent's version; a `saveAndDeploy` with the body read just before can fail *ENTITY … version
N is stale, current version is N+1* (5001). Re-read and retry; stop when
`deploymentState.entityVersion === version`. *(Superseded by §47.1: verify by comparing the deployed snapshot's `properties` with the agent's; `version` climbs on its own, so a version-equality loop may never end.)*

**44.3 Tag lookup for entities ✅ UAT.** `POST /api/aggregation?entityType=ai_agent&group=ENTITY` with
`filter:{op:'AND',values:[{field:'tags',op:'IN',values:['<tag>']}]}` returns the tagged agents
(`properties_tags` returns nothing). Tools/tasks of an agent: `e_action_ai_agent` / `e_topic_ai_agent`
with `properties_aiAgentId IN [id]`.

**44.6 A schema-2 workflow compiler in the browser ✅ UAT.** Workflows built node by node over REST
(START callable/SCHEDULED, groovy, fetch, create_record, bulk_create, bulk_upsert with updateFields,
call_llm_model_with_options with a Groovy-built `message` list, OCR extraction, CALL_WORKFLOW,
IF_ELSE with a no-op rejoin, STOP) saved without violations and ran through app data sources; a
`triggerInputCondition` may be a template resolving to a map a Groovy node built (`[:]` = everything).

## 45. Findings — an integration layer over simulated systems (verified on another tenant unless marked UAT; confirm on Orbit UAT before relying on it)

**45.1 ECG Sources cannot ingest data objects.** The Sources wizard catalogue (`/api/applications?module=ecg`)
lists 20 SaaS connectors (Confluence, GitHub, Gmail, Google Drive/Sheets, HubSpot, Jira, OneDrive, Outlook,
SharePoint, Teams, Salesforce, Slack, WhatsApp, Workday, …) and nothing for a database, a student system or
a UnifyApps object; `GET /api/context-graph/sources/applications/storage_by_unifyapps/objects` → empty.
`mdm_by_unifyapps_create_staging_records` / `apply_data_matching_rules` require a `sourceId` (a published
ECG source). ⇒ For systems outside the catalogue, integration = automations: record triggers + scheduled pull.

**45.2 Storage record triggers carry the before image ✅ (schema read).**
`storage_by_unifyapps_on_any_change {object_type, triggerInputCondition}` → `{change_type, object{id,
properties, version, modifiedTime, lastModifiedBy…}, before{…}}`; `on_create_record` and `on_update_record`
also exist. START node: `trigger:{type:'EVENT'}`, context `storage_by_unifyapps / storage_by_unifyapps_on_any_change`,
inputs `{object_type, triggerInputCondition:{}}`.

**45.2a A record trigger deploys only on an object with record events on.** ✅ UAT (an invoice three-way-match build, workflow `<id>`): `POST /api/workflow-definition/{id}/deploy` of a workflow whose START is `storage_by_unifyapps_on_any_change` on a freshly created object → HTTP 500, violation on `n_in.inputs.object_type`: "Webhooks are not enabled for object '<id>'. Please enable webhooks on the object to use this trigger." The switch is the object's `metadata.supportsWebhook` (false on every object the accepted builds exported; `true` in the entity-type read-back once set): `POST /api/entity-type/update` with the full metadata read from `GET /api/entity-type?entityType=` and `supportsWebhook: true`, then deploy. a build tool's `kit_objects` takes `events: true` for it.

**45.3 🔴 Inside a workflow, `fetch_records` filters on object fields need `properties.<field>`.**
`{property:'status', filter:{operator:'EQUAL', value:'PENDING'}}` returns **nothing** (200);
`{property:'properties.status', …}` works. `id` works bare (`GT`, `EQUAL`, `IN`). Sorting accepts both
`queued_ms` and `properties.queued_ms`. The system fields **`modifiedTime` / `createdTime` cannot be
filtered at all** (`GT`, `GTE`, `LT`, `EQUAL` all return nothing) but **can be sorted**. ⇒ incremental pulls:
full resync pages by `id GT <last id>` ascending; a safety-net pull reads the newest N by
`modifiedTime DESC` and keeps those newer than the watermark (flag a GAP when the page does not reach back).

**45.4 A graph node record written through the store is invisible to Cypher for seconds to minutes.**
`MERGE` against a node the projection cannot see yet does nothing (no error): 50 employees + 50 edges written in
one run → 0 edges; the same edges a minute later → 50. After a 15k-record load, edges to those nodes kept
failing for several minutes. ⇒ Queue relationships (`<uc>_ops_edge_queue`), write them once ≥ 60 s old, **read
each back** with a labelled `MATCH (a:L1)-[:R]->(b:L2) WHERE a.id=… AND b.id=…`, mark DONE only if returned,
retry with time-based backoff (attempt n waits n minutes), FAILED after 10 with the reason. 4,200 edges per run
in six UNWIND statements of ≤ 700 pairs + six verify reads ≈ 10 s.

**45.5 🔴 Never merge a golden record from the projection.** Reading the current golden record with Cypher and
writing the merge back with `bulk_create` (which REPLACES the record, §42.8) wiped fields whenever the projection
lagged: 853 enrolled students lost their Slate fields and lineage. The store is authoritative and readable by
business key: graph node records are storage records of object type `<unifiedEntityId>` whose **record id is
the primary-key value** (`GET /api/entity/<ue>/G-SL-682522` ✅; the `90::<ue>::<pk>` node id → 404). Use
`storage_by_unifyapps_get_records_by_ids {object_type: <ue>, ids:[pk…]}` for read-modify-write.

**45.6 Workflow-to-workflow calls are `CALL_WORKFLOW` nodes** (re-confirmed on another tenant): `type:'ACTION'` fails at run
time with *No config found for resource callables_call_automation*. Outputs are flat.

**45.7 Access identity for a governed read path ✅.** A query workflow that first writes its access-log row with
`storage_by_unifyapps_create_record` (raw payload from a Groovy node — templates cannot generate ids) gets
`outputs.ownerUserId` = the calling platform user (519612 for the author via an app data source); map it to a role
in a config object and check every backticked label in the Cypher against a governance matrix before running it.

**45.9 Throughput measured (another tenant, app data source, synchronous).** Generic apply of 1,000 simple records ≈ 1 s;
400 golden-record merges (crosswalk lookup, store read, survivorship, lineage) ≈ 1.1 s; 215k records across 41
sources synced in ~6 minutes with zero record errors.

**45.10 🔴 A `LOOP` body must sit in the loop's child group, or the run never ends and every call in the body
is replayed ✅ another tenant (proven both ways).** Body nodes need `groupId: "<loopId>@<parentGroup>@l"`
(e.g. `n_loop@g1@l`). Built with every node in the root group
(`g1`), the loopback edge re-enters the loop at its first item for ever: a scheduled job ran one
`CALL_WORKFLOW` body 2,163 times in 35 minutes (~100/min, stepping up with each schedule tick) and a
safety-net loop replayed ~200 pulls a minute, flooding the store and the projection. Inline test runs on the
same 3-item graph: flat body → `CANCELLED` at 20 s (the test runner's cap; production has no cap); nested body
→ `COMPLETED` in 847 ms with exactly three child calls. Also 42.4's "loop writer unusable" had the same flat
shape — re-test before relying on that finding.

**45.11 Stopping a runaway ✅.** Pause a deployed workflow: `POST /api/workflow-definition/{id}/pause` (resume:
`POST /api/workflow-definition/{id}/unpause`; `/resume` is 404; a redeploy also clears the pause). Cancel one
run: `POST /api/workflow/cancel/execution/{executionId}` → 204. Production runs are listed by
`POST /api/aggregation?entityType=WORKFLOW_EXECUTION&group=PLATFORM` with filter `WORKFLOW_ID IN [<id>]`
(statuses `COMPLETED`, `FAILED`, `CANCELLED`, `WAIT`); every `CALL_WORKFLOW` child shows as its own root
execution. A run may stay listed as `WAIT` after its work finished (and after a cancel returned 204) — judge by
effects. Node inputs/outputs of production runs are not readable through `TEST_WORKFLOW_VARIABLE`
(`inaccessibleObjects`); re-run the saved definition through `initiate-test` (inline graph) to read each node.

**45.12 The storage fetch step ignores a sort on `createdTime` / `modifiedTime` ✅.** Through an app data source
(`storage_by_unifyapps_fetch_records`) `sortBy [{field:'createdTime',order:'DESC'}]` returns unsorted rows;
`properties.<field>` sorts work (a `YYYY-MM-DD HH:MM:SS` string sorts correctly). `POST /api/entity/{object}`
honours `createdTime` sorts. The entity list takes `includeTotalHits:true` → `totalHits` (exact count).

**45.13 Numbers read back from the store are Long or Double.** The same field came back as `1790310088242` on
one record and `1.790310088242E12` on another. Groovy that drops decimals before expanding the exponent turns
the second into `1` — expand `E` first (`new BigDecimal(v).toBigInteger()`), then strip decimals.

**45.14 Groovy inside a JavaScript template literal loses single backslashes.** `\(` and `\s` in a builder's
template string reach Groovy as `(` and `s`: a governance regex `/\(\s*…\s*\)/` deployed as `/(s*…s*)/`,
matched every query and refused every read for non-admin roles. Double every backslash in the JS source and
check the deployed code (`GET /api/workflow-definition/{id}` → node `inputs.code`).

**45.15 Projection lag under load.** After the runaway in 45.10 wrote millions of records, a store update took
~15 minutes to show in Cypher (normally seconds). Screens that must show an action at once should read the
action's audit row from the store, not the graph.

**45.18 A Cypher `collect()` reaches Groovy as a JSON list string, quotes included ✅ another tenant.**
`collect(g.gift_id) AS ids`, read back from `code_by_unifyapps_groovy`'s input, is the string `["RG-1","RG-2"]`.
Stripping only brackets and spaces leaves `"RG-2"`, which became part of a finding key and a relationship end that
never existed: 11 relationships failed after 10 attempts each. Parse it as JSON
(`new groovy.json.JsonSlurper().parseText(...)`), or strip `[`, `]`, whitespace **and** `"`. A key that ended up with
quotes shows in the edge queue as `…::"RG-002428"`.

**45.19 A refused bulk write does not fail the node ✅ another tenant.** `storage_by_unifyapps_bulk_create_records`
given a record the schema refuses (here an extra field on an `additionalProperties:false` object) completes
normally and returns `{inserted: 0, insertedIds: [], errors: {"<key>": "…Validating entity … additionalProperties
<field>"}}`; the workflow runs on. An upsert of an existing record reports `inserted: 1`. So "saved" must be decided
**after** the write, from `inserted`/`errors` — a student-lifecycle build's admin save reported *saved* and audited *Done* for a write
the store refused until a check step was added.

## 46. Findings — a read-only HubSpot read (UAT)

**46.1 Resource versions drift daily — four moved in 24 h.** ✅ UAT.
`hubspot_search_records_batch` 23234 → **23241**, `hubspot_get_owners` 23013 → **23020**,
`hubspot_get_association_batch` 23253 → **23260**, `hubspot_get_pipelines` 10731 → **10738**
(a deal-forecasting build build carried the old numbers). The saved probe workflow
`<uc>_hs_probe_search` `<id>` still holds 23234 and still runs, so an old version
is tolerated at run time — but a builder must still resolve from `/resources`.

**46.3 Owners: active only, and a per-id lookup fails the run.** ✅ `hubspot_get_owners` (75 rows) omits
deactivated owners; four `hubspot_owner_id` values on live deals (`29253802`, `75556300`, `75441557`,
`30028601`) resolve to nothing. `hubspot_get_owner_by_id {ownerId:<int>}` on one of them returns HubSpot
404 (`x-hubspot-notfound: true` in the node's `headers` output) and the node is `FAILED`, so the run is
`FAILED` (run `<id>`). Map through `get_owners` and keep the raw id as the fallback.

**46.4 `initiate-test/{id}` with a foreign inline graph.** ✅ Posting
`{payload, type:'MOCK', workflowDefinition:<base definition with different nodes/edges>}` to the id of an
existing, deployed workflow runs the inline graph (five different graphs run against
`<id>`), reads back through `TEST_WORKFLOW_VARIABLE` with that `workflowId`, and
leaves the saved definition untouched (`version` 1, `deploymentState.workflowVersion` 1 before and after).
This is the cleanest "execute a connector action once" path: no object is created. Runs land in that
workflow's test-run history.

**46.5 Node output carries the upstream HTTP headers.** 👁 A failed `hubspot_get_owner_by_id` node's
`outputs` payload is the raw HubSpot response envelope (`headers{…}`, status), which is where the
rate-limit headers can be read: `x-hubspot-ratelimit-max` 190, `-interval-milliseconds` 10000,
`-daily` 1000000, `-remaining`.

**46.6 Company batch read.** ✅ `hubspot_search_records_batch` `object:'companies'` with
`hs_object_id IN [<≤100 ids>]` returned `total` 100 then 4 for 104 ids in two runs (~1 s each).
`hubspot_get_association_batch` for 114 deal ids → 111 `results` (deals with no company are simply
absent from `results`, not returned with an empty `to`).

## 47. Findings — agents, tags, workflow updates, LLM and storage nodes (UAT)

**47.1 An agent's `version` is not "unpublished changes".** ✅ After `saveAndDeploy`, `ai_agent.version`
keeps climbing (+5 within seconds on agents with approval-gated tools; later also on a read-only agent,
v7 → v12) while `GET /api/entity/deployed/ai_agent/{id}` (the published snapshot: `properties`,
`entityVersion`, `deployedEntityVersion`, `snapshotAssets` = `{}`, `lastPlatformUpdateBy/On`) has
**identical `properties`** to `GET /api/entity/ai_agent/{id}`. Test publication by comparing the
snapshot's `properties` with the agent's, never `deploymentState.entityVersion === version` (a loop on
that re-publishes forever). `?version=`, `/versions`, `/history`, `/deployed` suffix → 404 or ignored.

**47.2 Tags are dropped in two places.** ✅ (a) `POST /api/entity/update` with `{id, entityType,
properties, version}` and no `tags` clears the entity's tags — always send `tags`. (b) A code app's
`e_interface` loses its tags after `POST /agent-api/apps/{appId}/publish` and after app builder turns
(its app-settings tools rewrite the entity). Re-apply with hierarchical `UPDATED` after every publish
and after each build; keep a second ownership marker in `properties.additional` (e.g. `buildRef`).

**47.6 Groovy helper names.** ✅ A code node whose prelude defines closure variables (`def p = {…}`)
fails to compile when the node's own code declares `def p` ("The current scope already contains a
variable of the name p", error 5008 on deploy). Define helpers as script methods (`def p(String k) {…}`).

**47.7 Workflow update in place.** ✅ `GET /api/workflow-definition/{id}` → replace `nodes`/`edges`
→ `saveAndReturnViolations` → `deploy?version=<new version>` keeps the id; every data source and agent
tool that calls it (`automationId`, `version:"-1"`) runs the new logic with no re-binding.

## 48. Findings — data layer: three objects, 1,268 records (UAT)

**48.1 Create → read → update with both schema carriers, in one pass ✅.** `POST /api/entity-type`
(`{id,name,pluralName,description,metadata:{storeDetails:{store:"MONGO"}},tags:["<TAG>"]}`) then
`GET` it back, set `input:{type:"SCHEMA_AND_LAYOUT",schema:S,layout:{"ui:order":[…]}}` **and**
`schema:{dynamic:false,type:"SCHEMA",schema:S}`, `POST /api/entity-type/update`. `columnCounts` matched
the property count on the first read-back for all three (24/11/8), `metadata.referenceKeys` was derived
from `foreignKey:{reference:"ENTITY_ID:<uc>_poc"}` as `{key:"properties.poc_id", referenceType:"<uc>_poc"}`,
`uniqueKeyFields` from two `uniqueKey:true` flags, `dateFields` from `format:"date-time"+dateFormat:"epoch"`.

**48.2 Renaming a field = replace the property in both carriers + rewrite every record ✅.**
`hubspot_poc` → `poc_value`: rebuilt `properties` without the old key and with the new one (order kept
via `ui:order`), `entity-type/update` → `columnCounts` 25 → 26 (with one more boolean added), then
`POST /api/entity/update` with the **full** new body for all 114 rows. Records that still carried the
old key were accepted by the update (the replace drops it); a read-back `distinctKeys` over the object
is the check that no row still has the phantom field.

**48.3 A replace-guard needs an explicit allow-list ✅.** A loader that refuses any write whose body
lacks a key the stored record has (the §27 rule) correctly blocked 53 + 28 writes where a field
*legitimately* disappears under a new mapping (`health_reason` cleared on green rows, `completed_at`
cleared when a milestone leaves `done`). Pass the keys that may vanish per batch
(`allowDrop:['health_reason']`) rather than loosening the guard — every other drop stays a hard error.

**48.4 Aggregation on records needs `projections`; group-by shapes return rows, not groups ⛔.**
`POST /api/aggregation?entityType=<uc>_poc&group=ENTITY` without `projections` → 500
`Cannot invoke "java.util.List.iterator()" because "projections" is null`. With projections, none of
`aggregations:[{type:'COUNT'}]+groupBy:[…]`, `projections:[{name,aggregation:'COUNT'}]`,
`groups:[{field}]`, `projections:[{name,type:'SUM'}]` grouped anything — each returned one row per
record (the `type:'SUM'` variant simply projected `properties_amount` and `id`). Until a grouping shape
is found, compute KPI totals in a workflow Groovy step over a full storage fetch (≤ 2,000 rows) — never by
reducing an app page. `POST /api/entity/{obj}` responses carry `objects, cursor, hasMore` and **no total**.

**48.5 Verified in the same session ✅.** Entity-list filters `EQUAL` on `properties.status` /
`properties.archived` / `properties.poc_id` (FK value), `IN` on `properties.<uc>_owner`, compound `AND`,
sorts on `properties.sequence`, `properties.target_end_date`, `cTm`. 1,252 creates with 8 parallel
workers in ~10 s, zero failures; an idempotent reload (create → `E11000` → read `version` → full
update) of the same 1,247 rows in ~15 s. Full-row equality against the generator output: 0 diffs.

## 49. Findings — six callable workflows and their data sources (UAT)

**49.1 Storage filters inside a workflow fetch node bite when the property is `properties_<field>` or `id` ✅.**
`triggerInputCondition:{operator:'AND',filters:[{property:'properties_archived',filter:{operator:'EQUAL',value:false}},
{property:'properties_kind',filter:{operator:'EQUAL',value:'blocker'}}]}` returned exactly the 80 blocker notes of 446 live
rows; `properties_poc_id` EQUAL returned the 6 milestones / 4 notes of one PoC; `id` EQUAL returned one row. Counts matched
`POST /api/entity/{obj}` reads (114 / 687 / 80). `includeTotalCount:true` → `outputs.total` (114). This settles the §39.7
doubt: the dot form (`properties.x`) is the entity API's; the underscore form is the storage node's.

**49.2 Caller identity without a scratch row or a delete ✅.** The record the workflow is about to create IS the identity
probe: create the note with `author:''`, read `{{ n_c.outputs.ownerUserId }}` (the caller's user id — through `initiate-test`
and through the app data source alike), match `<uc>_user_profile.properties.platform_user_id`, then `update_record_by_id`
with the full row and the resolved name ("<display name>"). 434 ms end to end, 9/9 fields read back, `lastModifiedBy` =
the caller. Fallback when no profile matches: `'Platform user <id>'` (factual, not invented). No delete is ever needed for caller identity.

**49.3 `loop_while` + `variable_by_unifyapps` is a working paging loop ✅.** `create_variables {after:'', more:'yes',
rows_json:'[]', total:'0', pages:'0'}` → `loop_while` on `{{ n_v.outputs.more }} EQUAL 'yes'` → HubSpot search with
`after:'{{ n_v.outputs.after }}'` → Groovy appends `results` to a JSON string and reads `{{ n_s.outputs.paging.next.after }}`
(absent on the last page → parameter unbound → `''`) → `update_variables` `[{source:'{{ n_v.outputs.after }}', value:…}]`
→ loopback edge (`type:'next', name:'loopback'`), body nodes in group `n_loop@g1@l`. 2 pages, 114/114 in ~2 s. A second
loop of the same shape feeds `hubspot_search_records_batch` on companies with `filterGroups[0].filters[0].values:
'{{ n_cp.outputs.result.ids }}'` (a template resolving to a String array inside a nested input works; 124 ids in 2 chunks
of ≤ 100) and `hubspot_get_association_batch` `inputs:'{{ n_ids.outputs.result.deal_ids }}'` (114 ids → 111 results).
`saveAndReturnViolations` accepted both loops first time. Whole refresh: 7–10 s, fits `initiate-test`.

**49.4 Vertex Opus 4.8 through the LLM node, verified by price ✅.** `conv_ai_by_unifyapps_call_llm_model_with_options`
(`CALL_INTERFACE_WORKFLOW`, rv 2480) with `modelId:'<id>'`, `temperature 0.2`, `maxTokens 2000`,
`responseFormat {type:'json_object'}`: 1,722 in / 117 out, `inputTokenCost` 0.00861 and `outputTokenCost` 0.002925 →
**5.00 / 25.00 USD per M = Opus 4.8** (Sonnet 4.6 would read 3 / 15); `finish_reason: end_turn`; child run on the platform
workflow `685127a68611a7196adb4415` (4,977 ms). Whole workflow 3.1–5.4 s, so `initiate-test` did not hit its ~26 s limit
at this prompt size (3 KB). The model quoted only facts from the prompt (milestone titles, HubSpot `use_case` text).
`topicExecutionModel` is an agent-entity setting; a workflow LLM node takes `modelId` directly.

**49.5 A null value in a Groovy result map is dropped from the node output ✅.** `[next_milestone_due: null,
insight_age_days: null]` → neither key exists in `n_g.outputs.result` nor in the STOP payload. Consumers must treat a
missing key as null; do not `required` such keys in the output schema.

**49.6 HubSpot `closedate` carries a time of day ⚠️.** The search returned `2024-12-12T19:18:18Z`-style values for deals
the data layer had stored at UTC midnight (the integration read had truncated to `yyyy-MM-dd`). A refresh that stores the
raw value flips `close_date`/`target_end_date` on every row; normalising to the date (first 10 chars) made the third run
report `changed_rows: 0` with only `synced_at` moving. `hubspot_get_pipelines` stage labels are trimmed (`"Closed Lost "`).

**49.7 Field-level upsert at scale, idempotent ✅.** `storage_by_unifyapps_bulk_upsert_records_by_id` (rv 16334) with 114
`{id, updateFields:[{fieldName, actionType:'SET', setValue}]}` entries → `{success:true, successCount:114, failedCount:0}`
in ~1 s; a full-row diff of all 114 records before/after showed only the SET fields changed and zero protected fields
(`status`, `health*`, `success_criteria`, `next_action`, `last_insight_at`) touched. `bulk_create_records` with
`rawPayload: []` and `skipUpdate:true` → `{inserted:0, insertedIds:[], errors:{}}` (empty list accepted again).
`actionType:'UNSET'` is emitted for blanked values but no row exercised it yet (👁).

**49.8 Repo copy == live definition, provably ✅.** `sha256(JSON.stringify({nodes, edges}, sortedKeys))` with the
server-added edge fields `priority`/`skip` stripped is identical between the definition rebuilt from the repo specs and
`GET /api/workflow-definition/{id}` for all six workflows (`local-hashes.json` vs the tab). The server only reorders keys
and adds `priority:0, skip:false` on edges. A single comment line that was in the repo but not in the tab paste was the
one mismatch found — a cheap check worth running after every deploy.

**49.10 Groovy notes.** Script methods (`def sv(Object v) {…}`) as the prelude avoid the closure-parameter clash (§47.6)
entirely; closure parameters in the script body must still be unique per script (`s1/h1/h2/s2`, `ra/rb` + `na/nb`).
`payload['owner'] = x` passes the `owner =` blacklist; `payload.owner = x` would not. `String.isLong()` and
`java.sql.Date(ms).toString()` are available; a civil-days function replaces `java.time` for ISO → epoch.
`IllegalArgumentException` / `IllegalStateException` messages surface verbatim as `rootCauseMessage` to the app data
source (verified: `kind must be update, blocker or decision`).


## 50. Findings — an agent built and tested over REST (UAT)

An agent with 3 tasks and 6 GLOBAL tools (`enabled:true`, `version "-1"`, `parameters {}`), two of
them approval-gated, plus a generic query workflow and an identity lookup workflow.

**50.1 The agent test API turn is asynchronous ✅.** `POST /api/workflow/execute/node/sse` (`callables_call_automation_streaming`,
`copilotType AI_AGENT_TEST`) returned 3 events and closed after ~2 s with `responseGenerationStatus: pending`; the turn kept running
server-side (7–20 s). Poll the conversation reader (`fetchConversation=66ab98083d73300e63962287`, `until` in the future) until
`response.additional.responseGenerationStatus === 'completed'` — and then check the newest Bot message is the settled answer: on the first
turn the reader reported `completed` while the only Bot message was the model's interim narration ("I'll start by identifying your owner
name…"); the real answer arrived a few seconds later as a second Bot message (list is reverse-chronological, take index 0 without
`internalMessageType`). `additional` also carries `firstFanMessageId` (= the trace id), `lastBrandMessageId`, `sessionDuration`,
`toolIndex` and `llmUsageDetails`. The browser `javascript_tool` has a 45 s ceiling, so run a battery as a background promise on
`window` and poll it from later calls.

**50.2 Which model actually ran — two independent proofs ✅.** (a) `TraceTimelineDetails` with `type: "LLM"` returns
`inputOutputContent.input.content` whose first keys are `isMultipleToolCallEnabled, modelId, …` — `modelId <id>`
(Vertex Opus 4.8) on every LLM span of the battery. (b) `llmUsageDetails`: `inputCost/inputTokens` (non-cached) = 5.00 USD/M,
`cacheWriteCost/cacheWriteInputTokens` = 6.25 USD/M, `outputCost/outputTokens` = 25.00 USD/M — the Opus 4.8 signature (Sonnet 4.6 = 3 /
3.75 / 15). Setting the same id in `topicExecutionSettings.{topicExecutionModel,topicSelectionModel}` and
`responseGenerationSettings.{answerGenerationModel,answerGenerationModelSettings.modelId}` left no other model in any slot.

**50.3 Cost shape ✅.** Every new conversation cache-writes ~35,700 tokens (platform prompt + 9 KB instructions + six tool schemas); a
turn with two LLM calls wrote it twice (68 K). Battery cost per turn: refusal $0.013, unknown-name $0.07, one-tool answers $0.23–0.34,
three-query answer $0.54. Same-chat follow-ups would read the cache instead (not measured here).

**50.4 The hidden user-context message carries the username only 👁.** The first user turn is prefixed by a hidden message:
`{"userName":"<username>","alias":"<username>"}` plus the date and timezone — no display name, email or platform user id. An identity
tool for "my …" questions must therefore accept `username`; `<uc>_poc_whoami` matches `<uc>_user_profile.username` (verified: the model
passed `{name:"<username>", username:"<username>"}` and got `<uc>_owner "<display name>"`). A bare display name ("the author") is ambiguous
across profiles and is refused rather than guessed.

**50.5 `tags` on tasks and tools ✅.** `POST /api/entity {entityType:'e_topic_ai_agent'|'e_action_ai_agent', tags:['<TAG>'], properties}`
keeps the tags on read-back (`POST /api/entity/<type>` list rows carry `tags`). `POST /api/entity/update` on either must resend `tags`
(§47.2 applies).

**50.6 Publish state ✅.** `saveAndDeploy` with the full entity + `tags` → `deploymentState.entityVersion === version` immediately
(1/1 → v1, 8/8 → v2, 15/15 → v3) and `GET /api/entity/deployed/ai_agent/{id}.properties` deep-equal to the agent's — both checks agree
here; the snapshot comparison remains the reliable one (§47.1).

**50.7 No `SetTopic` span appeared in any of the 12 traces 👁.** Traces show `LLM → Tool → LLM` under "Agent Execution" only, with
`topicAsTool:false` and three enabled tasks. Tool choice followed the agent-level instructions; whether task `instructions[]` were
injected could not be confirmed from the timeline (an earlier observation showed `SetTopic` as a tool call on a
different agent). Behaviour rules were therefore kept in BOTH the agent instructions and every task.

**50.8 Exact counts need a server-side group, not a list the model counts ✅.** Asked "there are 15 PoCs with blocker notes, right?",
the agent first equated `kpis.blocker_notes` (80 notes) with PoCs; after a counting rule it counted the 114 list rows by hand and
answered 58 (engine: 65). Adding `group_by`/`sum_field` to the generic query (`groups[{value,count,sum}]`, `groups_total` = distinct
values; `limit` defaults to 0 rows when grouping) gives `groups_total 65` for notes `kind=blocker` grouped by `poc_id`, and status
sums that add to the engine's 18,132,453.80. Never let the model count.

**50.9 A single-PoC question stopped at the first row 👁→✅.** With both a generic query and a detail tool available, "what is the health of
Najm and why" was answered from the query row (health + health_reason) without the detail (missed milestones, blocker note). The fix
was in the tool descriptions, not the prompt alone: the detail tool now says it is the ONLY read with milestones and notes and MUST be
called for any one-PoC answer, and the query tool says it does not return them.

## 51. Findings — data-source scope in a config app (UAT)

**51.1 A GLOBAL data source cannot read page variables or blocks ⛔ → ✅ page-level.** The six data sources the automation layer
created on `e_global_<app>` (`target: app`) were rebound to `{{ var_f_status['value'] || '' }}` etc.; every run from the page sent the parameters EMPTY (114 of 114 rows with `search = <city>` typed; `var_f_q` and the URL had the value). The `{{ }}` of a
global data source are evaluated in the global page's scope, where the page's `var_*` / `b_*` do not exist. Creating the same six on
the page that triggers them (`cfg.ensureDs(cfg.dsAutomation, {pageId, …})`, same workflow ids, `version "-1"`) fixed it first time
(`5 shown of 114` for `?q=<city>`). Keep global data sources for parameter-less or `userContext`-only calls.

**51.2 Automation data source without a transformer: `data` IS the STOP payload ✅.** `POST /api/workflow/execute/node` answers
`{executionInstanceId, id, lookupReferences, response: <STOP payload>}` and in the page `{{ e_ds['data']['kpis'] }}` reads it directly —
no `['result']` (that wrapper exists only with a JS transformer, §29).

## 52. Findings — governance: guardrails vs controls (UAT)

An agent with a `gaurd_rail` guardrail, nine `controls`, one `policies` row and an `agent_profile`
registry row, probed over the agent test API.

**52.1 Two enforcement layers; only `gaurd_rail` blocks inline ✅.** The agent console's Configuration → Guardrails group (PII Masking
`/configuration/sensitive-information`, Hallucinations `/hallucinations`, Content Filters `/content-filter`, Custom Word Filter
`/word-filter`, Denied Topics `/denied-topics`, Blocked Messaging `/blocked-messaging`) is ONE entity per agent, type **`gaurd_rail`**
(sic), found with `POST /api/aggregation?entityType=gaurd_rail&group=ENTITY` or `POST /api/entity/gaurd_rail {filter:{op:AND,
values:[{op:EQUAL, field:"properties.aiAgentId", values:[<agent>]}]}}`. It runs inline: the trace shows `Input Guardrails › {PII Mask,
Content Filters, LLM×n}` before the agent loop and `Response Guardrails › {Content Filters, PII Mask}` after it. A blocked prompt
produces: Fan message `additional.guardrailHit: true`, a Bot message whose text is `BlockedMessaging.blockedMessagingForPrompts.
blockedMessage`, `Input Guardrails › Content Filters` output `{withinThreshold:false, guardrailViolationDetected:true, contentFilters:
{…strengths…}}`, NO `Agent Execution` span, cost ≈ $0.013. AI Governance `controls` (§"AI Governance — Controls") attached via
`accessibleTo` to the native agent id, to a registry profile id under `ai_agent/`, and to `agent_profile/<profile id>` did not change
any of 14 read-only probes (injection, credential strings, denied topic, identity PII, profanity, a false-positive check; re-run 12
minutes later and again after registration) — every Fan `guardrailHit:false`, and the agent even passed an AWS key and a password into
a tool call. The tenant's `incidents` rows reference `agent_profile/<registry id>` (or a registry id under `ai_agent/`) and arrive in
bursts (2026-09-24 04:02–04:03 for one agent); registry profiles carry `evalSettings {runFrequency {5 MINUTES}, sessionCloseTime {24
HOURS}}` — consistent with a post-hoc evaluation of traces. No incident for the tracking agent appeared within 20 minutes.

**52.2 `gaurd_rail` create shape ✅** (`POST /api/entity {entityType:"gaurd_rail", tags:["<TAG>"], properties:{…}}`, tags kept):
```json
{ "aiAgentId": "<agent id>", "name": "<uc>_poc_copilot_guardrails", "runInAsync": false,
  "contentFilters": { "llmModel": "e_66b280e945f17a17c0e7c27a",
    "filterStrengthForPrompts":   { "hate":"high","insult":"medium","violence":"high","sexual":"high","misconduct":"high","promptAttack":"high" },
    "filterStrengthForResponses": { "hate":"high","insult":"medium","violence":"high","sexual":"high","misconduct":"high" } },
  "DeniedTopics": { "llmModel": "e_66b280e945f17a17c0e7c27a",
    "DeniedTopics": [ { "topicName": "...", "definitionOfYourTopic": "...", "addSamplePhrases": ["...", "..."] } ] },
  "customWorldFilter": { "filterProfanity": true, "wordsOrPhrases": [ { "name": "<word or phrase>" } ] },
  "RedactSensitiveInformation": { "piiByUA": { "enabled": true },
    "regex": { "enabled": true, "patterns": [ { "name": "AWS access key", "pattern": "AKIA[0-9A-Z]{16}" } ] },
    "automations": { "enabled": false, "ids": [] } },
  "BlockedMessaging": { "blockedMessagingForPrompts": { "blockedMessage": "..." }, "blockedMessagingForResponses": { "blockedMessage": "..." } },
  "Hallucinations": { "llmModel": "e_66b280e945f17a17c0e7c27a",
    "groundingConfig": { "enableGrounding": false, "groundingScore": 0.5 }, "relevanceConfig": { "enableRelevance": false, "relevanceScore": 0.5 } } }
```
Server adds `enabled` (**defaults `false`** — send/PATCH `true`) and `runInNewFlow:false`; `version` starts at 0; update with
`POST /api/entity/update {id, entityType:"gaurd_rail", tags, properties, version}`. `regex.patterns[]` items are exactly `{name,
pattern}` — any extra key is a 500 *"property patterns invalid; add additionalProperties regexPattern"*. Older rows carry a legacy
`RedactSensitiveInformation.Pattern[{Name, RegexPattern, guardrailBehaviour: mask|block}]`; the current UI writes the `regex` form.
Strength values `none|low|medium|high`; observed semantics: **higher = stricter** (`high` blocked a category the classifier rated
`Low`; `medium` blocked `insult: Medium`). The UI keys are `promptAttack` (entity) vs `prompt_attack` (span output).

**52.3 Guardrail classifier model ⚠️.** `llmModel: "sonnet_4_6_bedrock_no_thought"` (the alias that works in `controls`) makes EVERY
turn fail after ~127 s: Fan `additional.executionError` = `CONNECTION with id <id> not found`, Bot "The system
couldn't find the required connection…", `responseGenerationStatus` stuck at `pending`. The platform default `e_66b280e945f17a17c0e7c27a`
(924 of 1,0xx live `gaurd_rail` rows; `GET /api/entity/ai_agent_llm_model/<it>` 404s; the console picker shows the raw id) runs and
its classifier spans carry `modelId <id>` = **"Vertex Sonnet 4.6"** (`claude-sonnet-4-6`, provider `vertex_ai`).
Per turn the guardrail adds ~7 short classifier calls (one per content category + one per denied-topic pass) ≈ $0.01.

**52.4 A blocked turn never completes ✅.** For a guardrail-blocked prompt the conversation reader keeps `responseGenerationStatus:
"pending"` (observed 72 s+); the settled signal is the Fan message's `additional.guardrailHit === true` plus the Bot blocked message.
Poll for that, not for `completed` (amends §50.1).

**52.5 No republish after attaching ✅.** The guardrail was created 05:58:27Z, after the agent's v4 publish at 05:56:33Z; the deployed
snapshot (`GET /api/entity/deployed/ai_agent/{id}`) stayed deep-equal to the agent and mentions neither the `gaurd_rail` nor any
control; the blocks fired at 06:03–06:07Z. Same for `controls` (not in the snapshot). Closes the §"AI Governance — Controls" question.

**52.6 Agent Registry = `agent_profile` ✅.** 176 rows on UAT; the Registry page is `POST /api/aggregation?entityType=agent_profile&
group=ENTITY` (projections `properties_name, properties_applicationId, properties_awaitingTraces, oUId, mTm`) plus
`POST /api/workflow/execute/node?name=AgentRegistryListing` (per-agent `{lastActivity, telemetryCount, cost, incidents, policies}`;
"forbidden datasource" when called from a script). A native agent is listed only when a profile links to it:
`{applicationId:"unifyapps", assetType:"agent", external_agent_id:"<ai_agent id>", connectionType:"observe"|"control", enabled,
registered, agentProfileGroupIds:["unifyapps"], ownerId}`; the tenant's 61 linked native profiles came through a `unifyapps` connector
connection (Discovery: `agent_profile_group` rows = platform connections, `GetDiscoveredAssetCount` per group; "qa new" = 4,246 agents).
Creating one directly works: `POST /api/entity {entityType:"agent_profile", tags:["<TAG>"], properties:{name, description,
applicationId:"unifyapps", assetType:"agent", connectionType:"control", external_agent_id, enabled:true, registered:true,
agentProfileGroupIds:["unifyapps"], ownerId:"<userId>"}}` → `<id>`, shown as "the tracking agent · UnifyApps · Active ·
15 traces · $3.98 · policies 0" (the policies column ignored the nine attached controls under every scope string — unconfirmed how it
counts). The "Register Agent" drawer lists 14 platforms incl. a "UnifyApps" button (needs a connection the user authorises).

**52.7 `incidents` entity ✅.** `POST /api/aggregation?entityType=incidents&group=ENTITY` (sorts `cTm`; `IN` on `properties_accessibleTo`
works; `ICONTAINS` on it too) and `POST /api/entity/incidents`. Properties: `checkType` ("Denied Topics" | "PII detection" | "Regex
pattern" | "Custom terms" | "Custom LLM" …), `severity`, `confidence`, `traceId`, `chatTypeIncident {userQuery, source:"User Input",
userId, conversationId}`, `incidentType:"CHAT"`, `action:"FLAG"|"BLOCK"`, `control`, `policy`, `accessibleTo` (`["global",
"agent_profile/<id>"]` for a global control; `["ai_agent/<registry id>"]` for a scoped one), `assetType:"agent"`, `status:"OPEN"`.
`GET /api/entity/controls/<control referenced by an incident>` can 404 — controls get removed while incidents keep the id.

**52.8 `blockedTools` shape ✅.** `additional.blockedTools = {operator:"OR", filters:[{property:"NAME", filter:{operator:"CONTAINS"|
"NOT_CONTAINS", value:"<keyword>"}}]}` — tool NAMES by keyword, not ids (35 live rows: 33 CONTAINS, 5 NOT_CONTAINS, `operator` always
OR; some rows put a comma list in one `value`, semantics unknown — use one filter per keyword). Layout hint: *"Match tool names by
keyword — the agent may never invoke a matching tool."* Inline gating unobserved (see 52.1).

**52.9 Roles / visibility facts ✅.** `RoleDefinition` aggregation with `lcName ICONTAINS` business role names → 0 rows: none of a use case's business roles exists as a platform role on Orbit; Agent sharing shape:
`visibility {type:"PRIVATE", visibleTo:[{principalId:"<user id>", principalType:"u"}]}` (27 of 100 recent agents PRIVATE, 73 unset).
`GET /api/user-context?includeRoles=true` returns `{assumeContextAllowed, customer, environment, isImpersonatedSession, modules,
notificationMqttTopics, user}` with the role names under `user.roles`.

**52.10 Agent-level facts seen on the way.** `ai_agent.properties` carries `copilotAttachmentGuardrails`, `enableToolsGuardrailWrapper`,
`secureRuns`, `indexingSettings.piiMasking {automations, piiByUA, regex}` — indexing-time masking, separate from `gaurd_rail`. The
default (no `gaurd_rail` row) still runs `Input Guardrails › PII Mask ×2 + Content Filters` on `e_66b280e945f17a17c0e7c27a`, with
every category reported `none` and `withinThreshold:true` even for a prompt-injection string — the default blocks nothing.

**47.8 Agent turn usage lives under `additional`.** ✅ The conversation reader
(`fetchConversation=66ab98083d73300e63962287`) returns the turn's usage at
`response.additional.llmUsageDetails` (also on the Fan message's `additional`), not at
`response.llmUsageDetails`. `inputTokens` already INCLUDES `cacheReadInputTokens` and
`cacheWriteInputTokens` (38,994 = 1,530 + 12,488 + 24,976; `inputCost` prices only the 1,530) —
sum `inputTokens` only. One Opus 4.8 turn with three tools: $0.18.

**47.9 A full-record update evaluates `{{ … }}` inside every string.** ⚠️ `storage_by_unifyapps_update_record_by_id`
through an app data source (`rawPayload` = the whole record, required because a partial payload is
rejected 500) replaced every `{{ input.x }}` inside a stored JSON text (`plan_json`) with `""`.
Write JSON-text fields with `{{` as the JSON escape `\u007b\u007b` (backslash-u007b, twice) — the storage node sees no template
and `JSON.parse` restores the braces. The original text was recovered from the agent's tool span:
`TraceTimelineDetails` `{id:<record_plan span>, type:"Tool"}` → `inputOutputContent.input.content.plan_json`.

**47.10 A Custom Connector with a static API key needs no auth request.** ✅ `definition/basic` →
`definition/{D}/auth?type=CUSTOM` `{}` → `definition/update/{D}/auth?type=CUSTOM&version=1` with only the
connection form (`input` = `{api_key: {type:'string', format:'password'}}`) → per action: create, update
(`input`/`output` SCHEMA_AND_LAYOUT), `request/{D}/{A}/action` with the header `X-API-Key: {{ input.auth.api_key }}`
and path parameters as `{{ rawPayload.<name> }}` → `definition/{D}/publish`. `POST /api/connection/input/test?appName={D}`
`{name, authType:'CUSTOM', inputs:{name, authType:'CUSTOM', api_key}}` → 204; create the same body on
`/api/connection/input` → 200. All 10 actions list at `GET /api/workflow-builder/node/{D}/resources` (v2).
A workflow node `{type:'ACTION', context:{appName:D, resourceName:'D:A', resourceVersion, type:'APPLICATION',
connectionId}, inputs:{…}}` called `GET https://httpbin.org/anything/cafm/work-orders/WO-5001` with the
connection's key in `X-Api-Key` (probe connector `<id>`, connection `<id>`).

**47.11 Catalogue search.** ✅ `GET /api/workflow-builder/nodes` → 1,220 connectors
(`name` = appName, `displayName`, `description`, `iconUrl`, `custom`) in ~2 s; match on whole words
with a stop list (work, order, asset, system, data…) or "work orders" matches every "Work*" connector.
Existing connections per connector: aggregation `Connection` with `appName IN [...]`, `active: true`,
projections `id, name, appName, oUId` (no secrets).

**47.12 A fetch filter with no value is rejected.** ✅ UAT — `storage_by_unifyapps_fetch_records`
with `{property:'properties.ward_code', filter:{operator:'EQUAL'}}` (the template resolved to nothing because
the optional input was blank) fails the run: errorCode 5004 "Validation failed with 1 violations",
violation `No Value found in filter with field: properties.ward_code, operator: EQUAL`. Blank optional
filters must be removed before the node: build `triggerInputCondition` in a Groovy node that skips blank
values and pass it as `{{ n_x_w.outputs.result.cond }}` (an empty map `[:]` means no filter).

**47.13 `create_record` on an existing key.** ✅ UAT — a second `storage_by_unifyapps_create_record`
with the same primary-key value fails: errorCode 5010 "Duplicate key exception while inserting entity"
(Mongo write error). An append-only record (event, audit, history) needs a key unique per write.

**47.14 Groovy node code is a script body.** ✅ UAT — a trailing unmatched `}` fails the deploy
(5008 "Unexpected input: '}'"), not the save: `saveAndReturnViolations` accepts it and `deploy` returns 500.

**47.15 Agent approval card shape.** ✅ UAT — a tool behind `approvalConfig` stops the turn with a Bot
message that has NO `message` text: `interfaceDetails.slug = "mcp-request"`, `pageInputs = {toolId, request, caseId,
canApproveAlways}` (`request` lists the tool inputs as `name: value` lines); `responseGenerationStatus` stays
`pending`. Detect the card by the slug, not by searching message text for "approve".

**47.19 AI document extraction reads USER-scope uploads, not PUBLIC ones.** ✅ UAT — the same transfer
letter, uploaded from a code app with `useUppy({ accessScope: 'PUBLIC' })` and passed as the upload's `key`, made
the workflow with `ocr_document_details_extraction` fail ("Workflow execution failed", no detail); uploaded with
`accessScope: 'USER'` it was read and the record created. Pass the upload's `key` (not its url) and upload
documents a workflow reads with USER (or ALL_USERS) scope.

**47.21 An agent tool argument is written by the model in one generation, so a large JSON argument does not fit.** ⚠️ UAT (a planner agent `<id>`, Vertex Opus 4.8). The planner assembled a 230 KB plan (37 steps)
in its sandbox and could not pass it to `record_plan` (`plan_json` string): trimmed to 75-98 KB it still could not emit it,
and an `@file` reference is not resolved (the workflow received the literal text and the JSON parse failed). There is no
file or sandbox-to-tool hand-off; the model has to write every byte of the argument. Design for it: a tool that takes a
large document takes it in parts of about 20 KB (a draft record plus an append tool that merges the next part and
finishes on the last one). ✅ The build engine's `record_plan` (`draft`) + `append_plan_steps` (`finish`) pair ran through
`initiate-test`: 2 + 2 + 1 steps, then `awaiting_approval` with steps 1-5, and the earlier drafts were marked `superseded`.

**47.22 Calling the tenant's LLMs from outside the platform: a callable workflow behind an app data source.** ✅ UAT (an LLM bridge: workflow an LLM bridge workflow `<id>`, app `<appId>`,
data source one data source `<id>`). `POST /api/workflow/execute/node?name=call_automation` with
`callables_call_automation` and our own `automationId` answers 500 "forbidden datasource: not found" (as §15): an external
caller needs a data source. Recipe: START (`callables_from_automation`, inputs `model_id`, `system_prompt`, `prompt`,
`max_tokens` as strings) → `CALL_INTERFACE_WORKFLOW` `conv_ai_by_unifyapps_call_llm_model_with_options` (resourceVersion 2481 on
the day; `modelId`/`systemPrompt`/message text/`maxTokens` templated from START) → STOP (`callables_return_to_automation`,
`text` = `llmResponse`, tokens, `finish_reason`); a minimal config app (`e_interface` + `e_global_<app>` page) with one
`callables_call_automation` data source (every parameter templated, one `dP` each), published; then
`POST /api/workflow/execute/node?name=<dsName>&requestId=<dsId>` with header `x-ua-app: <appId>` and the parameters filled
in `inputs.parameters` → `response: {text, input_tokens, output_tokens, finish_reason, success}`. Gemini 3.8 Flash
[MEDIUM] `<id>`: ~2 s for a one-line reply. `{{ … }}` inside the prompt and the system prompt is
passed through literally both ways (not re-templated). The tenant's text models: `POST
/api/aggregation?entityType=ai_agent_llm_model&group=ENTITY` with projections `id`, `properties_name`,
`properties_modelGroup` and a client-side filter on `TEXT_GENERATION` (the `lookup?ByQuery=ENTITY_ID:ai_agent_llm_model`
body shape tried returned 200 with no objects). No native tool calling through this step: an agent loop needs a
JSON tool protocol on top.

**47.26 A data-source call must carry the same `context` the data source stores, `resourceVersion` included.** ✅ UAT. `POST /api/workflow/execute/node?name=<ds>&requestId=<id>` for a storage `fetch_records` data source created
with `context.resourceVersion: 16421`: without `resourceVersion` in the call's context → 500 "forbidden datasource :
invalid input"; with it → 200 and the records. A data source created without a version (the app builder's own) accepts
calls without one.

**47.28 The OCR extraction node writes at most the model entity's `settings.maxOutputTokens`, and that setting is shared.** ✅ UAT — `__ua__call_ocr_extraction` has no token-limit input (its schema: `files, modelId, prompt, systemPrompt,
response_format, templateId, enhanceImage, includePageText, processAsPdf, methodForReadingPDF`). The tenant's
"OpenAI GPT 4.1 mini" `e_ai_agent_openai_gpt_4.1_mini` carries `maxOutputTokens: 436`, so a six-line invoice's JSON
stopped after 436 tokens on every run (images, `processAsPdf`, `includePageText`, `response_format` text or none: same
cut; with `json_object` the service appends a lone `}` to the cut text). Read the cap with
`POST /api/lookup?ByKeys=ENTITY_ID:ai_agent_llm_model {type:'ByKeys', lookupType:'ENTITY_ID:ai_agent_llm_model', keys:[…]}`
→ `properties.settings.maxOutputTokens`, `properties.inputModality`. "OpenAI GPT 4.1" `<id>`
(8,192, text/image/pdf) read all six lines in 8 s (746 tokens out). Gemini 2.5 Flash and OpenAI GPT 5.2
`<id>` failed the node on the same file. These entities belong to the tenant, not to us: choose a
model whose cap fits at build time, and make the parse step fail the run when the answer does not parse (a silent `{}`
saved a document with no lines).

**47.29 Groovy `Date.format(String, TimeZone)` is not available in the Code node.** ✅ UAT — use `java.time`:
`java.time.Instant.ofEpochMilli(ms).atZone(java.time.ZoneId.of('<zone>')).format(java.time.format.DateTimeFormatter.ofPattern('yyyy-MM-dd HH:mm'))`.

**47.34 The LLM interface does multi-turn conversations, native tool calls and images.** ✅ UAT (build engine
Coder bridge `<uc>_llm_bridge_llm` `<id>`, data sources `ds_llm_bridge_llm` (sync) and
`ds_llm_bridge_llm_async` on `<appId>`). The `__ua__call_ai_agent_llm_model` interface's input schema
(`POST /api/lookup?ByKeys=CALLABLE_INTERFACE`, key `__ua__call_ai_agent_llm_model`) is `{modelId, systemPrompt,
message: [{role, content: [object]}], tools: [{type:'function', function:{name, description, parameters}}], maxTokens,
temperature, responseFormat:{type}, top_p, topK, stream, aiAgentId, caseId, messageId, retry_count, step, logProbs,
frequencyPenalty, presencePenalty}`. Build `message` and `tools` in a Groovy step from JSON strings and template them
into the LLM node as whole values. With Vertex Opus 4.8 `<id>`:
- **tools**: a turn that wants a tool answers `finish_reason: "tool_use"`, `llmResponse` = its short text, and
  `outputs.tools = [{name, arguments: "<JSON string>"}]` (no call id). The next turn works with the call echoed as
  assistant text and the result sent as a user text part: the model answered from it (`end_turn`), ~3 s a turn.
- **images**: a content part `{type:'image_url', image_url:{url:'data:image/png;base64,…'}}` is seen (it read
  "ZEBRA 47" and a red square, 115 input tokens, 2 s); the Anthropic shape `{type:'image', source:{type:'base64',…}}`
  fails the run ("Workflow execution failed").
- `{{ … }}` in message text (JSX `style={{ padding: 8 }}`) passes through literally.
- **speed**: a 450-line TSX file came back whole, 10,379 output tokens in 88 s through the synchronous data source
  (~118 tokens/s; Opus 4.8 and Vertex Sonnet 4.6 both allow 64,000 output tokens on UAT). Near the ~128 s sync limit
  for larger answers, so the Coder uses the async data source (`synchronous:false`, §42.9) and the workflow writes the
  answer to a record (`<uc>_llm_bridge_turn`, keyed by `turn_key`) that the page polls.
Production runs of the bridge are not readable per node (§45.11); debug the definition with `initiate-test` (short
turns finish inside its ~20 s window).

**47.35 A compiled return step's id is `n_out`: a step you call `out` collides with it.** ✅ UAT — the
engine's `{kind:'return'}` becomes node `n_out`; a spec step `{id:'out'}` produced two nodes with the same id, the
save succeeded and the run stopped after the LLM node with no output. Never name a step `out`.

**47.37 The Playwright node, the one-time schedule node, and identity across scheduled runs.** ✅ UAT.
- `code_by_unifyapps_playwright` (resourceVersion 2608): inputs `{input: <JSON schema>, output: <JSON schema>,
  parameters: {…}, script: <Node JS>, async, useTypescript, usePlaywrightTestFramework, testTimeout}`. Node v22;
  `require('playwright')` → `chromium.launch()` works headless; parameters arrive as script globals; the node returns
  `outputs.output` (everything the script printed) and `outputs.result`. Runs of 180 s, 360 s, 721 s and
  1,500 s (25 minutes, a headless page kept open) completed. `initiate-test` answers 500 "No Response received within specified timeout"
  after ~20 s while the run continues; read it from `WORKFLOW_EXECUTION` / `TEST_WORKFLOW_EXECUTION` (projections
  `ID, STATUS, EXECUTION_TIME, START_TIME, END_TIME`).
- `callables_schedule_a_callable` (v3130): `{automation_id, version:'-1', schedule_name, schedule_method:{schedule_type:
  'ONE_TIME', setup_config:{start_time: ISO, timezone}}, cancel_existing, infinite_retries, runtimeType:'DEFAULT',
  parameters:{…}, runtimeConnections:{}}`. A workflow that schedules itself keeps the caller as the owner of every
  scheduled run (three hops a minute apart, owner <userId> each time).
- `auth_by_unifyapps_create_user_session` (v2013) `{sessionDuration}` → `{sessionId}` (the `_at` cookie value).

**47.39 Conversation parts for tools: the Anthropic shape works, the OpenAI shape fails.** ✅ UAT (Opus 4.8
through `<uc>_llm_bridge_llm`). Assistant turn `content: [{type:'text'}, {type:'tool_use', id:'toolu_…', name, input}]`
and the next user turn `content: [{type:'tool_result', tool_use_id, content:'…'}]` (then any `image_url` parts) are
understood: the model answered from the tool result. An assistant message with `tool_calls` plus a `role:'tool'`
message fails the run. Do not echo tool calls as text ("(I called read_file {…})"): the model imitated it as plain text
and stopped calling tools after 7 turns.

**47.44 Listing an object's newest records.** ⛔→✅ corrected UAT (same day). `POST /api/entity/<object>`
with `{filter:{op:'AND',values:[]}, page:{limit, offset}}` returns records **ordered by `id` (the record key),
descending**; `sort:{field:'createdTime', order}` (either order), `sort:{field:'createdTime', order:'ASC'}` and no sort
all return the same order. The first reading ("newest first") was wrong: those keys happened to be sequential. A
`createdTime` `GTE` filter returns nothing, and `/api/aggregation` does not project or filter `createdTime`
(`properties_created_at`, the object's own field, works; §45.12 had already seen the storage fetch step ignore this sort). To find records created since a time: page through all
of them (`limit` 200) and check `createdTime` (ms) and `ownerUserId` in code; each record has `id`, `createdTime`,
`modifiedTime`, `ownerUserId`, `version`, `properties`. `GET /api/user-context?includeRoles=true` → `user.id` matches
`ownerUserId`. To find labelled records, filter on the label field instead
(`/api/aggregation?entityType=<object>&group=ENTITY`, `properties_<field> IN [...]`).

**47.46 Dates written from ISO text: convert with more than `Instant.parse`.** ✅ UAT . Date(-time) fields are stored as epoch ms. The build engine converted text with
`java.time.Instant.parse`, which accepts only a full instant with a zone (`2026-09-14T00:00:00Z`); a workflow input
`"2026-09-14"` became null and the field was left out of the record, with no error (the claim lost its
`loss_date`, so every loss-date rule read 0). Our converter's fault, not the platform's: convert date-only
(`LocalDate…atStartOfDay(zone)`), `yyyy-MM-dd HH:mm`, `yyyy-MM-ddTHH:mm[:ss]` (`LocalDateTime…atZone`) and offset
forms in the business zone . Fixed in the engine's create/update compile (1.6.44).

**47.47 Groovy `("" as BigDecimal)` fails with "Index 0 out of bounds for length 0".** ✅ UAT. The
message does not say "number": an AI extraction that returned `vat_aed: ""` for one estimate line failed the code
node (`FAILED_NODES: ["n_build"]`) and the whole document read. Cast through a converter (blank → 0, currency text
cleaned, anything else rethrown). Run history with the failed node: `/api/aggregation?entityType=WORKFLOW_EXECUTION
&group=PLATFORM`, projections UPPERCASE (`ID`, `STATUS`, `FAILED_NODES`, `START_TIME`) — lowercase `id` is
"Invalid Projection : id" (500).

**47.49 An early return inside an IF_ELSE branch: a second STOP node in the branch group.** ✅ UAT
(`<uc>_library_join_waitlist`, test run `<id>`). A `callables_return_to_automation` STOP node with
`groupId: "<ifId>@<parentGroup>@y"`, reached by the IF_ELSE's `if`/`yes` edge and with no outgoing edge, saves with no
violations next to the main `n_out` STOP; the run ended there with that node's `result` and no later node ran.
Without it, an IF_ELSE whose yes-branch is empty fails the save: "Total 2 outgoingEdges expected, but found 1."
The no-branch group is `@n` (§ groupId convention).

**47.50 Groovy has no `Date.parse(format, text)`.** ✅ UAT (inline test run `<id>`): `Date.parse('yyyy-MM-dd', '2026-09-28')` throws MissingMethodException (the groovy-dateutil extension is not on the platform); `java.time.LocalDate.parse('2026-09-28').atStartOfDay(java.time.ZoneOffset.UTC).toInstant().toEpochMilli()` works. Same family as §47.29 (`Date.format`).

**47.51 The tenant has a daily AI cost hard limit; a data source only says "Workflow execution failed".** ✅ UAT. Every LLM call on Orbit UAT (`call_llm_model` nodes, agents, the an LLM bridge) failed with `rootCauseMessage: "[COSTFLAG]Overall daily cost hard limit reached: input alone (1733.61125624) exceeds limit of 500.0"`: a tenant-wide daily budget (USD), shared by all users; not ours to change. The data source that ran the workflow answers only `{rootCauseMessage: "Workflow execution failed", executionInstanceId}`; the real cause is read from the run: `POST /api/aggregation?entityType=WORKFLOW_EXECUTION&group=PLATFORM` filtered `ID EQUAL <executionInstanceId>` (projections `ID, FAILED_NODES, START_TIME`), then `POST /api/lookup?ByKeys=WORKFLOW_VARIABLE` with keys `<id>.<id>.<node>` and a time window, no `workflowId` needed; the failed node's `outputs.payload.rootCauseMessage`. Non-AI workflows keep working.

👁 UAT (workflows `<id>` and `<id>`): under the same limit an **Invoke Agent node does not fail — the run stays in `WAIT`**. Every test run that called an agent after the limit was hit (seven runs over ~30 min) stayed `WAIT`, with node variables recorded only up to the node before the agent call; runs that called the same agent an hour earlier completed in 11–16 s; a `call_llm_model` workflow run at the same time failed in 2 s with `[COSTFLAG]`, and workflows without AI steps completed. So: a run parked in `WAIT` at an agent node is not evidence against the workflow — run any workflow with an LLM step: an immediate `[COSTFLAG]` confirms the limit. a build tool names both cases instead of reporting a failure (`kit/run.ts` `tenantCause`) and marks the item blocked, not failed.

**47.52 Identity in a use case: the platform user id in apps, the username in agents; a blank lookup must match nothing.** ✅ UAT (a lost-and-found build, workflow `<id>`, inline test runs). `GET /api/user-context` gives `user.id` (`"<userId>"`), `name` and `username` (`<username>`), no email; an agent sees only the username (§50.4). A workflow that acts for "the signed-in person" therefore takes `actor_user_id` or `actor_username` and looks the person up by each. A record-search filter on a blank value must not be sent (the platform refuses a filter without a value), and dropping it turns a one-record lookup into "the first record": with a blank id it returned the first person on file, a receptionist. A filter `{property: 'id', filter: {operator: 'EQUAL', value: '__no_match__'}}` is accepted and returns 0 records (`found: false`), which is what a blank lookup should answer. Verified: blank → refused, unknown username → refused, username `<username>` → the right person and their claims, id `<userId>` → the same.

**47.53 No OpenAI-compatible LLM endpoint on the tenant; the options are the LLM interface or an API Manager façade.**
✅ UAT (probe for a build tool). With a signed-in session, every OpenAI-style path answered 404: `/v1/models`,
`/v1/chat/completions`, `/openai/v1/…`, `/llm/v1/…`, `/llm-gateway/v1/…`, `/ai-gateway/v1/…`, `/gateway/v1/…`, the same
under `/api/…`, and `/agent-api/{v1/models, chat/completions, openapi.json, docs}` (FastAPI, no docs exposed). No
"gateway / chat/completions / virtual key" string exists in the console bundles. **AI Governance is not a model
gateway:** Model Registry "Add model" imports models from a connection (AWS Bedrock, Anthropic, Core42 Compass, OpenAI,
Snowflake, UnifyApps) into the inventory; Discovery connections are `Observe · Advisory` (sweeps + OTLP traces, copy
"This platform can't route calls through the gateway yet, so it can only be observed") except UnifyApps-native ones,
`Control · Enforced`. So external callers reach tenant models only through `__ua__call_ai_agent_llm_model` (§47.22
bridge, §47.34 native `tools` + multi-turn `message` + `responseFormat` + `stream`; output `tools:[{name, arguments}]`,
no call id). **API Manager** (`/p/0/api-platform`: API Groups = `APIEndpointCollection`, Policies — ACL, rate limit,
usage quota, cache, CORS, IP allow list, header injection, request transformer/validator, timeout — and Clients)
serves published groups under `/api-endpoint/<group path>/…`; it is the only way to put an OpenAI-shaped URL
(`…/v1/chat/completions` → workflow → the LLM interface → an OpenAI-shaped reply) in front of tenant models. 👁 Not
built or verified: path freedom, raw-JSON response shape, client API-key auth and streaming are still open. Every call
still counts against the tenant's daily AI cost limit (§47.51).

**47.18 A test run of a callable workflow writes for real.** ✅ UAT — `initiate-test` with
`type: "MOCK"` still executes `create_record` (a run record was created by a self-test); test with inputs that
cannot touch live data (a throwaway key) or be ready to close the record.

## 53. Findings — simulated source systems and scheduled sync (UAT)

### `storage_by_unifyapps_bulk_create_records` — array of raw payloads
✅ UAT — resourceVersion 16419. Inputs `{object_type, useRawPayload: true, skipIfBlank: false,
skipUpdate: false, rawPayload: "{{ n_build.outputs.result.signals }}"}` where the Groovy node returns a list of
maps. 60 records in one call. **An empty list is accepted** (run SUCCESS, nothing written) — no IF needed.

### Sync graph that writes back to the source
✅ UAT — fetch (status NEW) → fetch mapping → Groovy → bulk_create (product) →
`bulk_upsert_records_by_id` (v16335, `updates: [{id, updateFields:[{fieldName, actionType:'SET', setValue}]}]`)
on the source object → `create_record` run log → bulk upsert on the registry row. The record `id` for
upserts is the primary-key value (`CYB-ALR-000123`, `SRC-CYBLE`). Verified by row counts after each run.

### Scheduled twin of a callable workflow
✅ UAT — same nodes, START swapped for `schedule/schedule_default` v202 with
`{cron:'INTERVAL', interval: 15, frequency:'MINUTES', sequential: true}`. First unattended run fired on the
quarter hour after deploy. A scheduled workflow can still be smoke-tested with
`POST /api/test-workflow/initiate-test/{id}` `{payload:{}, type:'MOCK', workflowDefinition:<full def>}`;
node payloads via `lookup?ByKeys=TEST_WORKFLOW_VARIABLE` key `{runId}.{runId}.{nodeId}`.

### Groovy in these workflows
✅ ISO timestamp without java.time: `new java.sql.Timestamp(System.currentTimeMillis()).toString().replace(' ', 'T').substring(0, 19) + 'Z'`.
`new Random()` and `String.format` work in the sandbox.

### 12,700 entity writes from a signed-in tab
✅ 16 parallel workers (`POST /api/entity` create, `POST /api/entity/update` with the version from the list
read) — 12,752 writes, zero failures, a few minutes. 17 object schemas created/updated in one pass.

## 54. Findings — live testing a supplier-risk build (UAT)

### App UPDATE binding with a partial payload: a REPLACE, again
❌ UAT — an in-app writer passed partial changes to `storage_by_unifyapps_update_record_by_id`
(`useRawPayload: true`). On an object whose primary key is required the call 500s with
`Non Empty Validations in Validating entity <uc>_review with validationResult required review_code`
(`rootCauseMessage` in the execute-node response). Adding the key "fixed" the error and stripped the record
to three fields. ✅ Fix: the writer reads the row first through the FETCH binding
(`triggerInputCondition {operator:'AND', filters:[{property:'id', filter:{operator:'EQUAL', value:id}}]}`,
`page {limit:1}`, full stored input set), spreads `response.objects[0].properties`, applies the change and
writes the whole record. Verified: all 11 fields kept, new pack saved. Damaged record restored with
`POST /api/entity/update {id, entityType, version, properties}`.

### Patching deployed workflows in place
✅ UAT — `GET /api/workflow-definition/{id}`, edit `nodes[].inputs.code` (Groovy) in the returned
object, `POST /api/workflow-definition/saveAndReturnViolations` with the whole object (response
`{workflowDefinition}`, no `violations` key when clean), then `POST /api/workflow-definition/{id}/deploy?version=<new>`.
A save alone creates a new draft version; deploy it too so live and draft match. Four sync workflows moved
v1 → v2 this way, and the next scheduled runs used the new code.

### Bulk data correction
✅ UAT — 3,559 records across five objects rewritten (full properties + version,
`POST /api/entity/update`, 16 workers): zero failures, re-scan showed no field loss.

### Agent latency (observed)
⚠️ UAT — Supplier Risk Analyst (Gemini Flash, QueryData tool) took ~70 s from question to full
answer on "Which material service providers need attention this week, and why?". The answer was correct
and cited record codes. Worth measuring before any live demo.


## 55. Findings — a property-performance build (UAT)

**55.1 Acknowledge source rows with one `update_records` call.** ✅ — `storage_by_unifyapps_update_records`
(update type MULTIPLE, filter `id IN [<ids from the fetch>]`, `updateFields` SET `sync_status: ACKNOWLEDGED`)
marks ~1,000 rows in one node. The first version acknowledged row by row with upserts and the run was
cancelled at 165 s; with `update_records` the whole sync (8 sources → 8 product objects) takes ~9 s.

**55.2 The aggregate node does not group records of custom objects.** ❌ — with `properties.x` the columns
come back empty; with `properties_x` every record comes back as its own row (the REST aggregation API
behaves the same, §48). Compute KPIs in Groovy over a paged fetch (3 × 5,000 rows here) and assert
completeness (`rows_read == total`) before writing anything derived.

**55.3 LLM node numbers must be numbers.** ✅ — `max_tokens` / `temperature` resolved from a Groovy map as
strings fail the run: "max_tokens: Input should be a valid integer". Return `(int)` / `double` from Groovy.

**55.4 The test runner cancels LLM runs at ~26 s.** ⚠️ — `initiate-test` on a workflow with an LLM node
reports CANCELLED around 26 s. Test those workflows through their `e_data_source`
(`POST /api/workflow/execute/node`), which ran the same explain workflow to completion in 24 s.

**55.5 Groovy identifiers.** ❌ — `owner` is blacklisted (save fails); rename (`docOwner`). Avoid `next`,
`main` and other names that shadow script bindings.
❌ UAT (an invoice three-way-match build, `<uc>_threew_sw_08_match_basis`): a closure parameter named **`g`**
(`list.each { g -> … }`, `inject(0.0G) { a, g -> … }`) passes `saveAndReturnViolations` but the **deploy** fails 500
*"startup failed … The current parameter list already contains a parameter of the name g"* — the Code node wraps the
script in a scope that already binds `g`. Rename it (`gx`). The same script compiled and ran under stock Groovy 4.

**55.9 Generated data must be internally consistent.** ❌ found in review — the work-order generator drew
the fault ("Lift door fault") independently of the equipment ("Chilled-water pump 1"), and the explain
workflow cites work-order titles in the executive answer. Draw faults from the equipment's own category.
Repaired 250 work orders in the source and product objects with full-record `POST /api/entity/update`
(dry run on one record, field count read back, then 8 workers, 498 writes, 0 errors). The seed stayed
deterministic because `pick()` consumes one PRNG draw whatever the list length — diff old vs new
generator output first and assert that only the intended fields changed.

### Agent latency fix (measured)
✅ UAT — Supplier Risk Analyst: `responseGenerationSettings.disableThought: true`,
`topicExecutionSettings.topicSelectionModel` moved from Vertex Opus 4.8 (`<id>`) to the same Gemini Flash
as execution (`<id>`), plus a length rule in the instructions. Warm answers 60–70 s → **34–38 s**, first
answer of a fresh chat ~60 s (session start). Accuracy unchanged: Sydney concentration 61 of 85, Cyble 27 alerts /
26 vendors / 9-7-9-2 by severity, all matching a direct count of the records.

## 56. Findings — Code-node audit, native-node probe, insight latency (UAT)

All reads were `GET /api/workflow-definition/{id}`; the only write was a scratch probe workflow.

**56.1 How much Code earlier builds contained ✅.** 357 workflows on UAT across ten builds, every
node classified (START/STOP excluded). Hand-built apps ran 15–20 % Code nodes; a multi-agent
storefront-optimization build was **46 % Code (416 of 909 nodes, 15,733 Groovy lines, 99 nodes over 60
lines)** and engine-generated workflows were **48 %**.

What the Code nodes did, by title: "Lookups" (hand-built joins), "Act" (branching logic), "Envelope"
(assembling the return object), "This item"/"Next item" (loop bookkeeping), "(rows)" (flatten after every
fetch), "(record)" + "(changes)" (coerce before every write), "(prompt)" + "(parse)" + "(usage)" around LLM
calls, "(filter)", "Continue" (a Groovy `return [ok: true]` to rejoin an `if`). Largest single node: 283 lines.
An aggregate workflow summed in Groovy over one 5,000-row page and returned a note that the total may be short.

**56.2 Native replacements, run in probe `<uc>_native_node_probe` (`<id>`, saved
v1, 0 violations) against `<uc>_claim` (167 rows) ✅.**

- `storage_by_unifyapps_count_records` v16419 `{object_type, triggerInputCondition}` → `{count}`;
  167 unfiltered, 0 with a non-matching filter.
- `utility_by_unifyapps_run_sql_query_on_list` v6779 `{dataSources:["{{ n_f.outputs.objects }}"],
  sqlQuery}` — the pill is also the table name in `FROM`. Verified: `GROUP BY properties.scheme`,
  `COUNT(*)`, `SUM(CAST(properties.claimed_amount AS DOUBLE))` = 3,480,482, `ROUND(AVG(…),2)` =
  20,841.21, `WHERE … IS NOT NULL`, `ORDER BY`, `LIMIT`, and `JOIN` of two pills (`FROM {{a}} a JOIN
  {{b}} b ON a.id = b.id`). Output `outputs.result` (array of row maps). Whole run incl. two 167-row
  fetches: 1,028 ms.
- `utility_by_unifyapps_sort_list` v6676 `{listSource, sortBy:[{field:"id", order:"ASC"}]}` →
  `outputs.sortedList` ✅.
- `utility_by_unifyapps_to_json_object` v6834 `{jsonString}` → `outputs.result` (parsed, nested) ✅.
- STOP `callables_return_to_automation` `result` as a map of templates ✅ (no "envelope" node needed).
- Fetch/count filters inside a workflow: **both** `properties.country` and `properties_country`
  honoured (a non-matching value → 0 rows for fetch and count), `id` EQUAL → 1 row. Refines §49.1:
  the dot form is not ignored in these nodes on UAT today.

**56.3 Traps ⛔.**
- `storage_by_unifyapps_aggregate_records` v2734 (description "Runs an aggregation query (GROUP, SUM,
  COUNT, AVG …)") **does not aggregate**. Projections `{name, aggregationFunction, alias}` with bare
  names or `properties.x` → rows with empty `columns`; with `properties_x` → one row per record, the
  record's own value under every alias (`total` = `n` = `avg` = 18000 / 38150 / …), `hasMore:true`.
  A filtered variant behaves the same. No error — same wall as §48.4. Use fetch → SQL on list.
- `utility_by_unifyapps_filter_list` v6805 returned `filteredList: []` for a filter every row
  matches, with the property as the documented pill (`{{ n_f.outputs.objects[0].properties.country }}`)
  and as `properties.country`. Shape unresolved; filter in the fetch or the SQL `WHERE`.

**56.4 Schema read, not yet run 👁.** `decision_table_by_unifyapps_execute_table` v2290 `{entityId,
input_loader, entity, enableDynamicOutput, responseType}`; `template_by_unifyapps_compile_template`
v1826 `{template_id, template_loader, template_content, nested_eval}` → `{output}`;
`utility_by_unifyapps_template_resolver` v6763 `{payload, additionalContext}` → `{output}`;
`utility_by_unifyapps_date_diff` v6796 `{date1, date2, outputUnit: years|days|hours|minutes|seconds|milliseconds}`
→ `{difference}`; `storage_by_unifyapps_fetch_distinct_values` v16325 `{object_type, field,
triggerInputCondition}` → `{objects}`; `storage_by_unifyapps_update_records` v16422 `{object_type,
numberOfRecordsToUpdate, triggerInputCondition, updateFields:[{fieldName, actionType, setValue}]}` →
`{result, count, failedCount}` (used by a property-performance build); `duckdb_by_unifyapps_execute_sql_query`
v1680 `{instanceId, sqlQuery, exportFileType}` → `{resultFile}`. Resource counts: utility 63,
variable 17, decision table 6, storage 43. Many input fields carry a `ua:llm_description` in
`input.layout` — the platform's own filling instructions for a model.

**56.7 Models miscount rows ⛔ → the NUMBERS rule ✅.** On a student-lifecycle build's exact captured payload
(30 `at_risk` rows, 12,099 chars) a model said 26 critical (actual 30), 26 withdrawal (24),
20 missed classes (17), 15 aid verification (12) and charted those counts. Another model had 30 ✓ but listed
13 names under "12". Appended to every insight prompt: *"NUMBERS (hard rule): quote only figures that
appear in the data exactly as given. Never count rows, add, average or derive a new figure yourself,
in the text or in a chart. If a count matters and the data does not state it, name the records
instead of counting them. A chart may only plot values present in the data."* Replaying the same
payload twice: 3 findings, every figure a value from the data (scores, office counts, the
signals-by-office series), 5.2 s / 6.1 s.

**56.8 Found in passing ⚠️.**
- An insight workflow carried another build's system prompt verbatim — a clone never re-prompted.
- An app's insight panel never rendered: `response.insights` was a JSON **string**, and the parser parsed the outer
  object, found a string and returned `[]`. The call succeeded (4.7 s), the panel stayed empty.
- An insight payload was `rows.slice(0, 200)` cut at 60,000 chars, i.e. the OLDEST months: the model cited old figures
  as current and spent 20,113 tokens. Send the newest rows, capped.

## 58. Findings — SAP connectors (UAT)

Read-only, from a signed-in tab (`GET /api/applications/{app}?fields=authSpec`,
`GET /api/workflow-builder/node/{app}/resources`). Nothing created.

**58.1 `sap_odata` connection form.** `name`*, `authType`* (default `BASIC`: username + password),
`odataVersion` (default `2.0`), `hostUrl`* (host only, e.g. `www.S4System.com`, port if needed; the service
path goes in the action), `sslVerify` (default true; a PEM server certificate can be supplied for self-signed
hosts), `connectionType`* `DIRECT` | `ON_PREM` (`ON_PREM` requires `groupId` = an On-Prem group).
Resources: `sap_odata_search_objects`, `sap_odata_create_object` (v3193), `sap_odata_on_new_object` (TRIGGER),
`sap_odata_list_purchase_order` (v3343), `sap_odata_get_purchase_order_by_id` (v3344),
`sap_odata_list_purchase_requisition` (v3297), `sap_odata_list_attachments` (v3299),
`sap_odata_download_attachment` (v3300); search/list/download are v3296–3300. Versions drift; re-read before use.

**58.2 `sap_rfc` connection form.** `name`*, `authType`* choosing either direct application server
(`network_connection.gateway_host`*, `system_number`*) or load-balanced (`message_server_host`*,
`logon_group`); both take optional `quality_of_protection` (SNC, with `snc_partner_name`) and `program_id`.
`user_logon`: `client`* (integer), `user`*, `password`*, `language`. ⚠️ **No `connectionType`/ON_PREM
option.** The platform must reach the SAP gateway directly (port 33<sysnr>, e.g. 3300), so a cloud-hosted
SAP needs that port opened to the platform's egress. Resources: `sap_rfc_call_rfm` (v4181),
`sap_rfc_export_call_rfm` (v1939), `sap_rfc_send_idoc` (v4227), `sap_rfc_check_idoc_status` (v4228),
`sap_rfc_list_all_idoc_types` (v4094), `sap_rfc_on_new_idoc` (TRIGGER, v4120; needs an SM59 HTTP destination +
WE21 XML-HTTP port in SAP pointing at the platform webhook, per the connector's own instructions).

**58.3 Tenant state.** UAT had 7 `sap_odata` connections, all active, all owned by others: never use one
without its owner's permission.

**58.6 Listing a system's OData services from an existing connection (read-only).** The `serviceName`
dropdown of `sap_odata_search_objects` is a lookup: `POST /api/lookup?ByQuery=CONNECTOR_OBJECT_NAME`
`{lookupType:"CONNECTOR_OBJECT_NAME", type:"ByQuery", options:{connectionId, source_resource_name:"sap_odata_list_services"}}`
→ `{response:{objects:[{value|label…}], type:"HITS"}}`. It reads the gateway's registered services, with no
workflow and no write. (`objectId` uses `source_resource_name:"sap_odata_fetch_objects"` + `inputs.serviceName`.)
One connection returned 3,177 services; others to the same host returned 200 with an **empty** list: an empty
lookup is not a proof of "no services" (likely stale credentials or a v4 connection).

## 57. Findings — native nodes instead of wrapper Groovy (UAT)

**57.1 Verified ✅**
- `SELECT id, properties.* FROM {{ n_f.outputs.objects }}` flattens fetched records; `to_json(...)` must be
  `CAST(... AS VARCHAR)` (a JSON-typed column comes back as Jackson node metadata `{array:true,…}`); `list(struct)`
  does not convert, a single struct does; `list(id)` gives a string array.
- Templates: `{{ n.outputs.result[0] }}` (object) and `[0].field` work; an object embedded in a longer string
  renders as a **Java map** (`{a=1, b=2}`), not JSON; `[*]` wildcards are **not** supported (null payload).
- `utility_by_unifyapps_to_json_string {object}` → JSON text, `[]` for an empty list; throws on an unresolved input.
- `utility_by_unifyapps_to_json_object` parses clean JSON; a ```json fence fails (fastjson2).
- Variable node formulas are **Excel** (POI): each `{{ }}` becomes a cell (`0{{x}}` → `0A1`, invalid), so use
  templates as bare cells. Working: `=IF({{t}}>0,TRUE,FALSE)`, `=MIN({{t}},500)`,
  `=ROUND((NOW()-DATE(1970,1,1))*86400000,0)` (epoch ms), `=DEC2HEX(RANDBETWEEN(0,65535),4)&…` (RANDBETWEEN clamps
  at 2^31-1), `=LEFT(IF(LEN({{u}})>0,{{u}},"run"),120)`, `=IFERROR(VALUE({{a}}),0)+…` (SUM ignores numbers held as
  text); `GT()` and `UUID()` do not exist.
- A Groovy parameter typed string receives a template object as a **HashMap**.
- IF_ELSE: both branches may join the next node (or STOP) with two incoming edges; saves with no violations.
- `create_record` raw payload of templates: `"12.5"`→12.5, `"7"`→7, `"true"`→true, a list into a text field is
  stored as JSON text, unresolved keys dropped; `skipIfBlank:true` drops `""` values.
- `update_records` by query on `id`: blank id → `{result:false}`, nothing written; `skipIfBlank:false` lets `""`
  clear a text field, `true` skips it. Output is only `{result}` (no count).

**57.2 Traps ⛔**
- `run_sql_query_on_list` on an **empty list** fails ("json_read expected records"), and `dataSources` must be a
  list (an object pill → "Invalid data source"). No native node flattens a list that may be empty.
- `bulk_upsert_records_by_id` with a blank id **inserted a new record** (auto id) and reported success.
- `""` into a number field: create fails the run (select: oneOf); upsert fails that record silently (`failedCount`).
- A literal `"now"` in a date field is rejected by the platform (the build engine's old Groovy coercion dropped it silently).

---

## 61. Findings — role-aware queries, skill drafts (UAT)

### 🔴 A role filter with no owner id returned the WHOLE dataset ⛔ UAT

A query workflow built its role filter as `if (oid && r == 'sc') f << [...]`. With a role
and no `owner_id`, the guard failed, **no filter was added at all**, and the search came back
with every record. The agent's answer to a "which of my …" question was therefore about everyone —
a wrong answer that looks exactly like a right one, because nothing in the response says the scope
was dropped.

Fixed by refusing: a `role` other than `all` with no `owner_id` now throws. **A filter that silently
no-ops is worse than one that errors**; prefer an exception to a default whenever the default changes
who the answer is about.

### A platform skill's edits are drafts, and the gap can be months of content ⚠️

`e_skill_ai_agent` `<id>` was at `version` 20 with
`deploymentState.entityVersion` 16 — and the *deployed* text the agent actually reads was
42,521 chars against a 48,432-char draft. A whole section (§14, the second / map
contract) had never reached the agent. **Diff the deployed snapshot against the draft before
assuming an agent knows what its skill says**:

```
GET /api/entity/e_skill_ai_agent/{id}            → the draft
GET /api/entity/deployed/e_skill_ai_agent/{id}   → what the agent reads
```

`POST /api/entity/action/saveAndDeploy` with the full entity publishes it (and every other
pending draft, so check what else is pending first — here it was only our own §14).

## 59. Findings — build-kit hardening (UAT)

**59.1 `if_else_condition` refuses an empty comparison value.** ✅ A condition `{property: "{{ x }}", filter: {operator: "NOT_EQUAL", value: ""}}` saves with a violation on the node (`n_save_key: inputs`) and nothing deploys. Test "is this set?" another way (59.2).

**59.2 Emptiness is tested in Groovy, not in a Variables formula.** ⚠️ A Variables node `=IF(LEN(TRIM("{{ n_in.outputs.key }}"))>0,"yes","no")` returned `"yes"` for an empty `key` (run `<id>`). ✅ A Groovy node returning `[has: (k && !k.startsWith('{{')) ? 'yes' : 'no']` (bind `k` with `binding.hasVariable` first, §24c) and an IF_ELSE on `{{ n.outputs.result.has }} EQUAL "yes"` skips the write on a blank key (workflow `<id>`, three runs: NET created, NET replaced, blank skipped — `count` 1 / 1 / 0).

**59.3 An upsert with a blank primary key fails, it does not insert.** ✅ `storage_by_unifyapps_update_record_by_id` `{upsert: true, recordId: "", rawPayload: {<pk>: "", …}}` on an object whose primary key is required fails the node with **5008 "Primary key field is required"**. The §57 note ("upsert with a blank id inserts a record") holds for objects without a required key; guard the write either way (59.2) so the run does not fail.

**59.4 What an agent turn contains.** ✅ In `ai_agents_by_unifyapps_invoke_agent` → `agentResponses`, messages with `additional.internalMessageType` precede the answer (observed `THOUGHT`); the answer has none. A Groovy trail `rs.collect { it.additional?.internalMessageType ?: 'ANSWER' }` gives `THOUGHT,ANSWER` or `ANSWER`.

**59.5 An idempotent agent call.** ✅ `messageId` = `{{ n_k.outputs.result.key }}` where `n_k` is Groovy `java.security.MessageDigest.getInstance('SHA-256')` over `agentId|agentVersion|question` ran first time (workflow `<id>`, 8 nodes). Include the agent's version in the key, or a republished agent answers from the old turn (§16: a replayed id is answered from the first turn).

**59.6 The `additional` shapes of the remaining control checks** (read from live `controls` on UAT):

| Check | `checkType` | `additional` |
|---|---|---|
| Denied Topics | `e_6a500b7c30b9186dd3773d30` | `{deniedTopics: [{name, description, examples: [..]}]}` + `llmModel`, `confidenceThreshold` |
| Content Filter | `e_6a500b6ad46d4e608bbe2fdd` | `{filterCategories: {hate|insult|violence|sexual|misconduct: {severity: low|medium|high}}}` + `llmModel`; `inputs` only `user_input`, `agent_output` |
| Regex pattern | `e_6a500b4fd46d4e608bbe2fbe` | `{regexes: [{name, pattern}]}` (RE2) |
| Custom terms | `e_6a500b5b30b9186dd3773d18` | `{terms: [{primary, related: "comma, separated"}]}` |

A denied-topics control created by the kit (`<id>`) read back with `accessibleTo` = `["ai_agent/<native id>", "agent_profile/<profile id>", "ai_agent/<profile id>"]` after `POST /api/entity {entityType: "agent_profile", properties: {applicationId: "unifyapps", assetType: "agent", external_agent_id, connectionType: "control", enabled, registered, agentProfileGroupIds: ["unifyapps"], ownerId, name, description}}` ✅. Blocking still comes from the agent's `gaurd_rail` (§52): a salary question answered with the guardrail's blocked message, an ordinary ticket answered normally.

**59.7 Sorted and windowed run history.** ✅ `POST /api/aggregation?entityType=WORKFLOW_EXECUTION&group=PLATFORM` accepts `sorts: [{field: "START_TIME", order: "DESC"}]` and `filter: {op: "AND", values: [{op: "IN", field: "WORKFLOW_ID", values: [id]}, {op: "GTE", field: "START_TIME", values: [epochMs]}]}` — without the sort, a workflow with more than a page of runs hid its newest ones.

**59.8 The schema of an existing object.** ✅ `GET /api/entity-type?entityType=<id>` returns the schema at `schema.schema.properties` (and `required`); writing a spec back without a field removes it, so merge the current properties first (the kit keeps a field a later spec leaves out, `kept 1 existing field(s) … sla_hours`).


## 60. Findings — a 115-workflow, 40-agent build with a context graph (verified on another tenant; confirm on Orbit UAT before relying on it)

**60.1 The graph engine is shared by every graph of the tenant.** 🔴 ✅ `mdm_by_unifyapps_execute_opencypher_query` with `modelId` = our graph and the statement `MATCH ()-[r]->() RETURN type(r), count(*)` returned the relationship types and counts of OTHER graphs of the tenant (about a hundred types, some with hundreds of thousands of records). `MATCH (n) RETURN labels(n)[0], count(*)` returned only the node types of our own model, so a node scan is scoped and a relationship scan is not. Rules the build follows: every statement names its node types (a label is the `unifiedEntityId`); counts are one `MATCH (n:<label>) RETURN '<name>', count(n)` per node type joined with `UNION ALL` (accepted by the engine); a statement written by a model is refused when a node pattern carries no label and its variable was not given one earlier in the statement (`(?<![A-Za-z0-9_])\(\s*([a-z][a-z0-9_]*)?\s*\)`), and when it holds any of `CREATE MERGE SET DELETE DETACH REMOVE DROP CALL LOAD FOREACH` outside a quoted value.

**60.2 Friendly names in, engine names out.** ✅ A statement is written with the names of the model (`(f:Finding)`, `f.verdict`) and translated before it runs: outside quoted values, `:<NodeType>` becomes ``:`<unifiedEntityId>` `` and `<var>.<property>` becomes `<var>._pr_<property>` (not `.id`). A fast model then writes correct statements from a schema it can read (3.1 s for the model, the check and the query together).

**60.3 Projection lag and the id prefix.** ✅ 626 node records written by ten `bulk_create_records` nodes in one workflow were all in the graph about two minutes later. The `LIMIT` of a statement did not cap the rows (`LIMIT 1` returned 3); the node's own `limit` input does. The first segment of a node `id` is read from the graph itself (`MATCH (n:<label>) RETURN n.id AS id`, node `limit` 1) instead of being configured.

**60.4 The outputs of every node of a background run, by execution id.** ✅ Run history was empty for the whole day: `WORKFLOW_EXECUTION` in groups `PLATFORM` and `TEST_WORKFLOW_EXECUTION` returned no row for workflows that were running or had run in the background (started by a data source with `synchronous: false`, or by a `call_automation` node with `synchronous: false`), and the Runs tab of the workflow showed "No data in the selected period". The variables were there all the same: `POST /api/lookup?ByKeys=WORKFLOW_VARIABLE` `{type: "ByKeys", lookupType: "WORKFLOW_VARIABLE", keys: ["<executionId>.<executionId>.<nodeId>", …], options: {startTime, endTime}}` with the `executionInstanceId` the data source call returned gave `inputs` and `outputs` of every node that ran, and `outputs.rootCauseMessage` on the node that failed. Ask for every node id of the definition at once; the nodes that did not run are simply absent.

**60.5 A Groovy parameter named `binding` hides the binding of the script.** ✅ With a parameter `binding` on a Code node, `binding.hasVariable(k)` fails with `No signature of method: java.lang.String.hasVariable() is applicable for argument types: (String)`. A parameter named `out` is harmless.

**60.6 `policies` refuses `controlSettings`.** ✅ `POST /api/entity {entityType: "policies", properties: {…, controlSettings: {}}}` → 500 `Non Empty Validations in Validating entity policies with validationResult add additionalProperties controlSettings`. Without the property the policy is created. (UAT rows carry an empty `controlSettings`.)

**60.8 One agent answer cannot carry 48 items.** ✅ A judgment agent asked for one entry per obligation of a section returned 31 of 48 (an answer of 7,854 characters) and the next agent abstained on the gap. Work is cut by the unit the text gives (one clause at a time): every answer then came back whole.

**60.9 A synchronous run is cancelled at about 20 to 27 seconds.** ✅ (extends §42.4) Through the test runner a sub-workflow with three agent calls ended `CANCELLED` at 26.9 s. A quick workflow that starts the long one in the background (`call_automation`, `synchronous: false`) answers in under two seconds; background runs with nested synchronous calls ran for ten minutes without trouble.

**60.11 An upsert key without a reference.** ✅ (kit) A record key written as a plain text in a spec (`actions|AG-35`) was wrapped as a reference and refused at compile time; a key always carries a reference.

**60.12 A property is readable in the graph only when the node type marks it `graphQueryable: true`.** ✅ Node types created with properties that carry no `graphQueryable` load their records without an error, the vertices appear with their id, their primary key and `_ua_recordTitle` — and nothing else: a `WHERE` on any other property matches nothing and a `RETURN` of it is null. Marking the properties afterwards works: `GET /api/context-graph/nodes/{nodeId}`, then `POST /api/context-graph/nodes/update/{nodeId}?version={n}` with the node and ONLY the properties of the model (the platform's own `_ua_*` / `standard: true` properties sent back give 500 `Duplicate property key(s) not allowed for a node: _ua_version`), publish the graph, write the node records again. `entityMetadata.graphQueryableFields` then lists them and the same queries answer.

**60.13 What the daily AI cost limit stops, and what it does not.** ✅ `[COSTFLAG]User daily cost hard limit reached: input alone (30.0008…) exceeds limit of 30.0` came back from every `call_llm_model` node run for the user (test runner and data source) from about 13:00 UTC. Agent invocations (`invoke_agent`) started by background runs went on answering for at least another quarter of an hour (378 agent runs in the 20 minutes around it), including agents whose tool holds an LLM node. Five background runs of the same period stopped without an error and without reporting. The limit is a guard of the tenant: the build stopped launching work and waits for the reset.

**60.14 `keep_blank` in the kit means "keep the field when the value is blank".** ✅ (kit) `storage_by_unifyapps_update_records` with `skipIfBlank: true` leaves a field alone when its value is blank; clearing a text field needs `skipIfBlank: false`.

**60.16 The public app's AI runs as its visitor, not as the builder's user.** ✅ another tenant — with the builder's user at its daily cost limit (`[COSTFLAG]` on every LLM node run for that user), the insight workflow called by the PUBLIC published app answered (two readings produced within a minute). The builder preview runs under the signed-in user and its LLM calls stop at that user's limit. So: browsing the public app spends AI budget; walk screens for layout checks on the builder preview.
