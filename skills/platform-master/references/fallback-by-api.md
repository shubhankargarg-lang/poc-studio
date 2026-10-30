# Fallback by API — creating one asset from the signed-in browser tab

This file is what `platform-master` follows in **job 3 (fallback)**. UnifyApps Headless has reported that it cannot
build one asset. The person has signed in to Orbit UAT themselves, in the session's browser. The fallback then
creates **only that asset**, inside the POC's solution, over the UnifyApps REST API. Every call runs same-origin from
the person's signed-in tab. The fallback reads every write back, runs the asset's test, and hands the new ids back
to UnifyApps Headless. It never builds pages or app UI, never deletes anything, and never touches another solution or
tenant. Evidence markers: ✅ verified on the platform · 👁 observed in UI traffic · ⚠️ partial or unverified ·
⛔ does not work. The full endpoint catalogue, error catalogue and dead ends are in `api-spec.md`.

Tenant: **Orbit UAT**, `https://orbit.uat.unifyapps.com`, always.

---

## 1. When the fallback runs, and what it may touch

| | |
|---|---|
| Trigger | UnifyApps Headless reported that a task cannot be built: it failed after its own retries, or it says the platform capability is not available to it |
| Precondition | The person has signed in to Orbit UAT in the browser tab. Sign-in is always the person's own action |
| Scope | Exactly the one asset of the failed task (and the parts it cannot exist without, e.g. a tool's workflow when the task is "agent tool"). Types: Data Object (schema), seed records, Connection, Workflow/automation, AI Agent (+ tasks, tools, capabilities), Data source |
| Out of scope | Pages, app UI, themes, navigation, app publishing, code-app files. These stay with UnifyApps Headless and are listed at the verify gate |
| Never | Delete anything; touch an asset of another solution, another user or another tenant; type a password; read cookies or browser storage |
| Output | The new ids, a read-back of each, and a test result, handed back to UnifyApps Headless |

Order of work for one asset: **search (§4) → create (§3) → read back (§2.4) → test (§3) → tag/link (§5) → hand back.**
At most two attempts per asset. If the second attempt fails, record why and stop.

---

## 2. The same-origin call helper

### 2.1 Why same-origin

The person signs in themselves (SSO or username + password). The session cookie is **httpOnly**: the browser attaches
it to every request from the tenant origin, so page JavaScript can call `/api/...` with `credentials:'include'` and no
credential ever enters the conversation. Run every call with the browser's JavaScript tool, with the active tab on
`https://orbit.uat.unifyapps.com`.

- Never read or print `document.cookie`, `localStorage`, `sessionStorage` or request headers. You do not need them.
- Never type a password, complete an SSO prompt or click an OAuth consent on the person's behalf.
- A **401**, or an **HTML** response where JSON was expected, means the session has expired. Stop and have the
  orchestrator ask the person to sign in again. Do not retry in a loop.

### 2.2 The helper

Paste this as the first lines of every JavaScript-tool call. It returns parsed JSON. It treats an empty body as
`null` (several reads answer 200 with an empty body, e.g. a missing object). It throws a short message on errors.

```js
// mcp javascript tool — the active tab must be on https://orbit.uat.unifyapps.com
await (async () => {
  const ua = async (method, path, body, extraHeaders = {}) => {
    const r = await fetch(path, {
      method, credentials: 'include',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json', ...extraHeaders },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const ct = r.headers.get('content-type') || '';
    const text = await r.text();
    if (r.status === 401 || ct.includes('text/html'))
      throw new Error(`SESSION: HTTP ${r.status} — ask the person to sign in again`);
    if (!text) { if (!r.ok) throw new Error(`HTTP ${r.status} (empty body)`); return null; }
    let data; try { data = JSON.parse(text); } catch { throw new Error(`HTTP ${r.status} non-JSON: ${text.slice(0, 200)}`); }
    if (!r.ok) throw new Error(`HTTP ${r.status} ${JSON.stringify(data).slice(0, 600)}`);
    return data;
  };
  // never let this helper send a delete — refuse it outright
  const guard = (method, path, body) => {
    const s = `${method} ${path} ${JSON.stringify(body ?? '')}`;
    if (/^DELETE /i.test(s) || /\/delete(\/|\b)/i.test(path) || /"deleted"\s*:\s*true|"requestType"\s*:\s*"DELETED"|_delete_|_remove_/i.test(s))
      throw new Error('REFUSED: delete');
  };
  const call = async (m, p, b, h) => { guard(m, p, b); return ua(m, p, b, h); };

  const me = await call('GET', '/api/user-context?includeRoles=true');   // who am I? 401 = not signed in
  return { userId: me?.user?.id, name: me?.user?.name };
})()
```

✅ `GET /api/user-context?includeRoles=true` → 200 with the signed-in user (`user.id`, `user.name`, `user.username`,
`user.roles[].name`, `customer.id`); 401 when the session is invalid. Keep `user.id`. It is the owner id that appears
as `oUId` in aggregation rows and `ownerUserId` in entities, and it is how you recognise assets this session created.

### 2.3 Conventions

| Convention | Detail |
|---|---|
| Base | `/api/...` relative to the tenant origin |
| Format | JSON in and out (`Content-Type` / `Accept: application/json`). `x-ua-*` headers are optional |
| Methods | POST-heavy: create, update, list and search are POSTs. `PUT`/`PATCH` on entities → 405 |
| Search | `POST /api/aggregation?entityType=<Type>&group=STANDARD` (workflows, connections, objects) or `group=ENTITY` (agents, tasks, tools, data sources, records). Send the **full** body (`entityType`, `group`, `filter`, `sorts`, `projections`, `page`) or it answers 500 |
| Aggregation rows | `{objects:[{columns:{…}}], totalHits}` — read `o.columns`. Abbreviations: `cTm` created, `mTm` modified, `oUId` owner, `d` deleted, `lcName` lower-cased name |
| Entities | create `POST /api/entity` · read `GET /api/entity/{type}/{id}` · update `POST /api/entity/update` (the **whole** entity) · list `POST /api/entity/{type}` · publish `POST /api/entity/action/saveAndDeploy` |
| Paging | offset: `page:{limit, offset}`. On entity lists, `cursor` re-returns page 1 — increment `offset`, stop on `hasMore === false` |
| Versions | resolve every `resourceVersion` at build time: `GET /api/workflow-builder/node/{app}/resources` → `objects[].version`. Never copy one; they drift daily |
| Long work | the JavaScript tool gives up at ~45 s while the script keeps running. Run long work as a background promise on `window` (e.g. `window.__fb = run()`) and poll it in later calls; never start a second pass over the same work |

### 2.4 Read back after every write

A 2xx proves the call was accepted. It does not prove the asset is right. Several writes answer 200 and do nothing.
After **every** write:

1. Read the asset back with its own read call (table below).
2. Compare what matters: name, tags (§5), field count, `version`, deployment state.
3. Record the id and the read-back result in `04-build/fallback-<n>.md`.

| Asset | Read-back call | What to assert |
|---|---|---|
| Object | ✅ `GET /api/entity-type?entityType={id}` (empty body = not found) | `columnCounts` = the number of properties you sent; `metadata.primaryKeyField` set |
| Record | ✅ `GET /api/entity/{objectId}/{recordId}` | every field present (count them) |
| Connection | ✅ aggregation `entityType=Connection` filtered by `id` (projections only — never print `userInput`) | `active: true`, name |
| Workflow | ✅ `GET /api/workflow-definition/{id}` | nodes/edges as built, `deploymentState.workflowVersion === version`. Tags only via aggregation (§5) |
| Agent / task / tool | ✅ `GET /api/entity/{type}/{id}` and ✅ `GET /api/entity/deployed/ai_agent/{id}` | tool `enabled:true`; deployed `properties` deep-equal the agent's `properties` |
| Data source | ✅ `GET /api/entity/e_data_source/{id}` | `context`, stored `inputs`, `interfacePageId` |

A stale read can follow a write by a few seconds. If a read-back differs, wait ~4 s and read again before deciding
it failed.

---

## 3. One section per asset type

### 3.1 Data Object (schema)

An object is an `EntityType` (aggregation group `STANDARD`). Its records are entities whose `entityType` is the object
id.

**Endpoints**

| Step | Call | |
|---|---|---|
| Create | `POST /api/entity-type` `{id, name, pluralName, description, metadata:{storeDetails:{store:"MONGO"}}, tags:[]}` | ✅ |
| Read one | `GET /api/entity-type?entityType={id}` | ✅ |
| Read many | `POST /api/lookup?ByKeys=ENTITY_TYPE` `{type:"ByKeys", lookupType:"ENTITY_TYPE", keys:[ids]}` | ✅ |
| Set schema / settings | `POST /api/entity-type/update` — the **full** object as read, with `input` **and** `schema` set | ✅ |
| Field metadata | `POST /api/lookup?ByQuery=ENTITY_FIELD` `{options:{group:"ENTITY", entityType}}` | ✅ |
| Custom indexes | same update, `metadata.customIndexDefinitions` | ✅ |

Dead ends: `GET /api/entity-type/{id}` 404 · `/api/entity-type/find/{id}` 404 · `/api/entity-type?id=` 500 ·
`lookup?ByKeys=EntityType` 5004.

**Minimal request — two calls**

```js
// 1. create the object (id = the plan's object name, with the POC's prefix)
await call('POST', '/api/entity-type', { id: 'pc_claim', name: 'Claim', pluralName: 'Claims',
  description: 'POC claims', metadata: { storeDetails: { store: 'MONGO' } }, tags: ['<POC-TAG>'] });

// 2. read it back, set BOTH schema carriers, update
const S = { type: 'object', additionalProperties: false, required: ['claim_code', 'title'], properties: {
  claim_code: { type: 'string', title: 'Claim Code', primaryKey: true, nameField: true, searchable: true, sortable: true, filterable: true },
  title:      { type: 'string', format: 'text', title: 'Title' },
  status:     { type: 'string', format: 'single-select', default: 'open',
                oneOf: [{ const: 'open', title: 'Open' }, { const: 'closed', title: 'Closed' }] },
  amount:     { type: 'number', title: 'Amount' },
  is_flagged: { type: 'boolean', title: 'Flagged?' },
  due_at:     { type: 'integer', format: 'date-time', dateFormat: 'epoch', title: 'Due At' },
  vendor:     { type: 'string', format: 'single-select', foreignKey: { reference: 'ENTITY_ID:pc_vendor' } } } };
const et = await call('GET', '/api/entity-type?entityType=pc_claim');
et.input  = { type: 'SCHEMA_AND_LAYOUT', schema: S, layout: { 'ui:order': Object.keys(S.properties) } };
et.schema = { dynamic: false, type: 'SCHEMA', schema: S };
await call('POST', '/api/entity-type/update', et);
const back = await call('GET', '/api/entity-type?entityType=pc_claim');
return { columns: back.columnCounts, pk: back.metadata?.primaryKeyField };
```

Field types: string, number, integer, boolean, date-time (`integer` + `format:'date-time'` + `dateFormat:'epoch'`),
single/multi select (`oneOf`, or a lookup `foreignKey:{reference:'ENTITY_ID:<obj>'}`), email, auto-generate
(`format:'auto-generate'` + `autoGeneratedFieldDefinition:{prefix, startFrom}`), object, array, file. You set per-field
flags; the server derives `metadata` (`primaryKeyField`, `nameField`, `uniqueKeyFields`, `searchableFields`,
`filterableFields`, `dateFields`, `autoGeneratedFields`, `referenceKeys`).

**Gotchas**

- ⛔ **Both carriers or nothing.** `input.schema` is the form; `schema.schema` is the validator (it carries
  `additionalProperties:false`). An update that sets only `input.schema` returns 200, shows the fields, and every
  write that uses them fails with `Non Empty Validations … add additionalProperties <field>` or a bare "Workflow
  execution failed". The GET does not always return `schema`, so set it yourself. **Check `columnCounts` after every
  schema update**: it is the only cheap signal that the change landed.
- ⚠️ A missing object reads as **200 with an empty body**, not 404 (the helper returns `null`).
- Auto-generate prefixes are joined with `_` (`prefix:"SZ"` → `SZ_1004`; `"SZ-"` → `SZ-_1003`). Never end a prefix
  with a separator.
- A lookup field stores the target record's `id` (array of ids for multi-select). Nothing cascades.
- Field names that collide with system columns (e.g. `version`) cause trouble. Use a different name.
- `filterable`/`sortable`/`searchable` flags do **not** create indexes. Only the primary and unique keys are indexed.
  Add at most 5 custom indexes (`metadata.customIndexDefinitions:[{name:'index_1', indexFieldMetadataList:[{field:'properties.<f>', type:1}]}]`,
  fields in equality → sort → range order). Re-read until each index shows `status:"SUCCESS"`. Send the whole list
  every time: it replaces the previous one. A POC-sized object does not need them. Add one only when the plan
  filters a large object on that field.
- A record trigger (`storage_by_unifyapps_on_any_change`) deploys only on an object whose `metadata.supportsWebhook`
  is true. Otherwise deploy fails with "Webhooks are not enabled for object".
- To change a field type or rename a field, replace the property in **both** carriers and rewrite every record with
  its full body.

**Verify it exists and works:** `columnCounts` equals the property count. `metadata.primaryKeyField` is the planned
key. Then create one seed record (§3.2) and read it back with every field present.

---

### 3.2 Records (seed data)

POC data is dummy seed data from the scoping document's seed-data section. Generate it deterministically, so a
reload produces the same rows.

**Endpoints**

| Step | Call | |
|---|---|---|
| Create one | `POST /api/entity` `{entityType:<objectId>, properties:{…}}` — the record `id` = the primary-key value | ✅ |
| Read | `GET /api/entity/{objectId}/{recordId}` | ✅ |
| List / filter | `POST /api/entity/{objectId}` `{filter:{op:"AND", values:[{op:"EQUAL", field:"properties.status", values:["open"]}]}, page:{limit, offset}}` | ✅ |
| Exact count | same body + `includeTotalHits:true`, `page.limit:1` → `totalHits` | ✅ |
| Update | `POST /api/entity/update` `{id, entityType, version, properties:<FULL record>}` | ✅ |
| Aggregate | `POST /api/aggregation?entityType={objectId}&group=ENTITY` — `projections` mandatory; field names `properties_<field>` | ✅ (no grouping — see gotchas) |

**Minimal request**

```js
const rows = [/* generated seed rows, every required field present */];
const out = { ok: 0, fail: [] };
for (const p of rows) {
  try { await call('POST', '/api/entity', { entityType: 'pc_claim', properties: p }); out.ok++; }
  catch (e) { out.fail.push([p.claim_code, String(e).slice(0, 160)]); }
}
const first = await call('GET', `/api/entity/pc_claim/${rows[0].claim_code}`);
out.firstFields = Object.keys(first.properties).length;
return out;
```

Run more than ~200 rows as a background promise with ~8–12 parallel workers (✅ 12 workers loaded 3,397 records with
zero failures, well under a minute). For tens of thousands of rows, do not loop `POST /api/entity` from the tab: it
freezes the browser pane. Load through a small callable workflow instead (START `{object_type, rows_json}` → Groovy
`JsonSlurper` → `storage_by_unifyapps_bulk_create_records` with `useRawPayload:true`, `skipUpdate:false` → STOP;
✅ ~1,000 rows in under 8 s per call).

**Gotchas**

- Validation errors are 500 with `rootCauseMessage` `Non Empty Validations in Validating entity <obj> …`:
  `property status invalid; oneOf fail` (value not in `oneOf`) · `required title` · `add additionalProperties x`
  (field not in the schema).
- ⛔ **`POST /api/entity/update` replaces `properties` wholesale.** Send one field and every other field is gone,
  with a 200. Always read the record, spread its `properties`, change, write the whole thing back, with its
  `version`, and with `tags` (an update without `tags` clears them).
- A duplicate primary key → Mongo `E11000 duplicate key`. For an idempotent reload, on E11000 read the row's
  `version` and `POST /api/entity/update` with the full body.
- `POST /api/entity` with an existing `id` → E11000; `POST /api/entity/{objectId}` lists, it does not create.
- A record's `id` is its business key. You cannot rename the key later without creating a new record.
- The list combinator is `{op:"AND", values:[…]}`. `{op:"AND", filters:[…]}` is accepted and **ignored** (all rows
  come back). The list is ordered by `id` descending, and a `sort` in the body is ignored.
- ⛔ The aggregation API and `storage_by_unifyapps_aggregate_records` do not group: they return one row per
  record. Compute totals in a workflow (fetch → `utility_by_unifyapps_run_sql_query_on_list`) or count with
  `totalHits`.
- Keep seed data internally consistent (a child's category drawn from its parent's, dates in order). Agents and
  insight workflows quote it.
- Before any bulk change to existing records, snapshot them (`POST /api/entity/{obj}` pages) so they can be restored.
  Dry-run the first record, read it back, count its fields, then run the batch.

**Verify it exists and works:** `totalHits` per object equals the planned row count. A sample of records reads back
with the full field count. Every lookup field points at a record that exists.

---

### 3.3 Connection

A connection is one authenticated instance of a connector. Workflow steps, agent tools and data sources reference it
by id in `context.connectionId`. POC data is dummy by policy, so most POCs need **no** connection: the plan's
"system" is a Data Object shaped like that system's output. Build a connection only when the failed task is one.

**Endpoints**

| Step | Call | |
|---|---|---|
| Find (fast, no secrets) | `POST /api/aggregation?entityType=Connection&group=STANDARD` | ✅ |
| Find by name | `POST /api/lookup?ByQuery=CONNECTION` `{type:"ByQuery", lookupType:"CONNECTION", query:"<name>", fields:["name"], options:{appName}, page:{limit:20, offset:0}}` | ✅ |
| Connection form | `GET /api/applications/{appName}?fields=authSpec,iconUrl,displayName,name,refreshable,includeOptions` → `authSpec.input` | ✅ |
| Auth types | `POST /api/lookup?ByQuery=CUSTOMER_AUTH` `{options:{appName, auths:[{type:"", label:""}]}}` | 👁 |
| Test before saving | `POST /api/connection/input/test?appName={appName}` → **204** on success | ✅ |
| Create | `POST /api/connection/input?appName={appName}` → connection with `id` | ✅ |
| Read one | `GET /api/connection/{id}` — ⚠️ returns `userInput` (secrets may be in clear). Do not call it unless you must check a host, and never print it | ✅ |

⛔ `GET /api/connection` (no id) returns every connection in the tenant, with secrets, ignores every filter and times
out. Never call it. ⛔ `/api/connections` is 404.

**Minimal request — a no-secret Custom HTTP connection**

```js
const body = { name: 'pc_public_api', authType: 'CUSTOM',
  inputs: { name: 'pc_public_api', requestType: 'HTTP', authType: 'CUSTOM',
            baseUrl: 'https://api.example.com', headersList: [], sslVerify: true,
            requestTimeoutInSecs: -1, connectionType: 'DIRECT', tags: [],
            rateLimitConfig: { enabled: false }, circuitBreakerConfig: { enabled: false } },
  options: { rateLimitConfig: { enabled: false }, circuitBreakerConfig: { enabled: false } },
  tags: ['<POC-TAG>'] };
await call('POST', '/api/connection/input/test?appName=custom_http_application', body);   // expect 204 (null)
const c = await call('POST', '/api/connection/input?appName=custom_http_application', body);
return { id: c.id, active: c.active };
```

`inputs` must follow that connector's `authSpec` (`schema.required` is the minimum). `authSpec.externalDocUrl` links
the connector's public docs.

**Find body**

```json
{ "entityType": "Connection", "group": "STANDARD", "includeTotalHits": true,
  "filter": { "op": "AND", "values": [
      { "field": "appName", "op": "EQUAL", "values": ["<appName>"] },
      { "field": "active",  "op": "EQUAL", "values": [true] } ] },
  "projections": [{"name":"id"},{"name":"name"},{"name":"appName"},{"name":"oUId"},{"name":"cTm"}],
  "sorts": [{"field":"cTm","order":"DESC"}], "page": { "limit": 50, "offset": 0 } }
```

**Gotchas**

- **Secrets are the person's.** A connection that needs a password, token or API key, and every OAuth connector
  (`refreshable: true`: Slack, GitHub, HubSpot, Google, Microsoft, most SaaS), is created by the person in the
  Connections Manager (`/p/0/connections/create/{appName}` → name → Authorize). That works like a sign-in: the
  orchestrator asks the person, as it does for sign-in. Then find the connection by aggregation and use its id. Never
  put a secret in a request body, a file or the chat.
- Always **test before create**. A failed create leaves a broken connection in a shared tenant.
- `custom_http_endpoint` (the internal HTTP node, no connection) is not `custom_http_application` (a saved,
  authenticated base URL). Public HTTP APIs need no connection at all.
- `GET /api/applications/custom_http_endpoint` answers 200 with an **empty** body (it has no form).
- Names are not unique. Track ids. Prefer connections owned by the signed-in user (`oUId`). Never use a connection
  whose name contains `DND` / `DONT TOUCH`, or one owned by someone else.
- Do not hand-create an `mdm_by_unifyapps` (graph) connection: `POST /api/connection` fails with
  `No Value found in filter with field: sourceConnectionId`. A context graph creates its own (`context-graph.md`).
- A personal connector (Gmail, Drive, Calendar) must never be bound to a fixed `connectionId` in an agent tool:
  every user would act as its owner. Use a per-user runtime connection (`connectors.md`).
- In a workflow node, `context.connectionId` must be a literal, existing id. A template there is a violation
  ("Connection is no longer available").

**Verify it exists and works:** the test call answered 204. The aggregation finds the id with `active: true`. One
read-only action of that connector runs once through an inline `initiate-test` (§3.4) and returns data.

---

### 3.4 Workflow / automation — create, save, deploy, run a test

A workflow is a `WorkflowDefinition`: `nodes[]` + `edges[]` + settings. A **callable** workflow (START trigger
`CALLABLE`) is what agent tools and data sources call.

**Endpoints**

| Step | Call | |
|---|---|---|
| Create | `POST /api/workflow-definition` — `nodes` must be non-null | ✅ |
| Read | `GET /api/workflow-definition/{id}` (does **not** return `tags`) | ✅ |
| Save (the real update) | `POST /api/workflow-definition/saveAndReturnViolations` — the complete definition with the current `version` | ✅ |
| Deploy | `POST /api/workflow-definition/{id}/deploy?version={n}` body `{deploymentNotes, _type:"WORKFLOW_DEPLOY_OPTIONS"}` | ✅ |
| Test run | `POST /api/test-workflow/initiate-test/{id}` `{payload, type:"MOCK", workflowDefinition:<full definition>}` → `{runId}` | ✅ |
| Run status | `POST /api/aggregation?entityType=WORKFLOW_EXECUTION&group=TEST_WORKFLOW_EXECUTION` | ✅ |
| Node outputs | `POST /api/lookup?ByKeys=TEST_WORKFLOW_VARIABLE` key `{runId}.{runId}.{nodeId}` | ⚠️ empty for API-created workflows |
| Node catalogue | `GET /api/workflow-builder/nodes` | ✅ |
| A node's actions + versions | `GET /api/workflow-builder/node/{app}/resources` | ✅ |
| An action's input/output schema | `GET /api/workflow-builder/node/{app}/resource/{resource}` → `input.schema` | ✅ |
| Find workflows | `POST /api/aggregation?entityType=WorkflowDefinition&group=STANDARD` | ✅ |
| Pause a deployed workflow | `POST /api/workflow-definition/{id}/pause` · resume `…/unpause` | ✅ |

`GET /api/workflow-definition` (no id) is 405. `/api/entity/action/saveAndDeploy` is **not** the workflow deploy.

**Minimal request — create a stub, then save the real graph**

```js
const ver = async (app, res) => (await call('GET', `/api/workflow-builder/node/${app}/resources`))
  .objects.find(o => o.name === res).version;

// 1. stub — START must carry its trigger, or the save later 500s with "Node.getTrigger() is null"
const wf = await call('POST', '/api/workflow-definition', { name: 'pc_get_claim', description: 'POC: read one claim',
  tags: ['<POC-TAG>'],
  nodes: [{ id: 'n_in', type: 'START', title: 'Trigger via automation', trigger: { type: 'CALLABLE' },
            context: { appName: 'callables', resourceName: 'callables_from_automation',
                       resourceVersion: await ver('callables', 'callables_from_automation') },
            inputs: { setup: { type: 'object', additionalProperties: false, required: ['claim_code'],
                       properties: { claim_code: { type: 'string', title: 'claim_code' } } } },
            index: 0, fallbackMode: 'STOP', skip: false }],
  edges: [] });

// 2. the real graph: START → fetch → STOP
wf.nodes.push(
  { id: 'n_f', type: 'ACTION', title: 'Fetch the claim', subTitle: 'Storage',
    context: { appName: 'storage_by_unifyapps', resourceName: 'storage_by_unifyapps_fetch_records',
               resourceVersion: await ver('storage_by_unifyapps', 'storage_by_unifyapps_fetch_records'), type: 'APPLICATION' },
    inputs: { object_type: 'pc_claim', numberOfRecordsToFetch: 'MULTIPLE',
              page: { paginateBy: 'OFFSET', limit: 1, offset: 0 }, includeTotalCount: true,
              triggerInputCondition: { operator: 'AND', filters: [
                { property: 'id', filter: { operator: 'EQUAL', value: '{{ n_in.outputs.claim_code }}' } }] } },
    index: 1, fallbackMode: 'STOP', skip: false },
  { id: 'n_out', type: 'STOP', title: 'Respond to automation',
    context: { appName: 'callables', resourceName: 'callables_return_to_automation',
               resourceVersion: await ver('callables', 'callables_return_to_automation'), type: 'APPLICATION' },
    inputs: { result: { found: '{{ n_f.outputs.total }}', claim: '{{ n_f.outputs.objects }}' } },
    index: 2, fallbackMode: 'STOP', skip: false });
wf.edges = [
  { fromNodeId: 'n_in', toNodeId: 'n_f',  type: 'next', id: 'next@n_in@n_f' },
  { fromNodeId: 'n_f',  toNodeId: 'n_out', type: 'next', id: 'next@n_f@n_out' }];
wf.schemaReferences = []; wf.standard = false;
const saved = await call('POST', '/api/workflow-definition/saveAndReturnViolations', wf);
if (saved.violations) return { violations: saved.violations };           // 200 and persisted even when broken

// 3. deploy the live version, then assert deployed == live
const live = await call('GET', `/api/workflow-definition/${wf.id}`);
await call('POST', `/api/workflow-definition/${wf.id}/deploy?version=${live.version}`,
  { deploymentNotes: 'POC fallback', _type: 'WORKFLOW_DEPLOY_OPTIONS' });
const after = await call('GET', `/api/workflow-definition/${wf.id}`);
return { id: wf.id, version: after.version, deployed: after.deploymentState?.workflowVersion };
```

**The object model in one screen**

- Node: `{id, type, title, context:{appName, resourceName, resourceVersion, connectionId?, type:"APPLICATION"}, inputs, index, fallbackMode, skip}`.
  `connectionId` goes **inside `context`**. Trigger nodes carry no `context.type`.
- Node types: `START`, `ACTION`, `STOP`, `IF_ELSE`, `LOOP`, `BREAK`, `DELAY`, `CALL_WORKFLOW`, `CALL_INTERFACE_WORKFLOW`.
- Edges: `{fromNodeId, toNodeId, type, id:"{type}@{from}@{to}", name?}`. Types: `next` (also `name:"no"` /
  `"loopback"`), `if` (`name:"yes"`), `loop`, `error` (needs `fallbackMode:"MANUAL"`).
- Nesting is the `groupId`: `{ownerNodeId}@{parentGroupId}@{y|n|l|error}`. Give every root node the same `groupId`,
  or none. A mixed set hides the graph in the builder canvas.
- Templating: `{{ n_<nodeId>.outputs.<path> }}` with spaces inside the braces. A value starting with `=` is a formula
  (`"=SUM({{ n_v.outputs.i }},1)"`).
- Inputs: the CALLABLE START's `inputs.setup` is a JSON Schema. It becomes the agent tool's argument contract and the
  data source's parameters. Put every required input in `required`.
- Output: a `STOP` (`callables_return_to_automation`) whose `inputs.result` is an object (a JSON array fails at run
  time). Every path of a callable must end in a STOP.
- Triggers: `CALLABLE` (`callables_from_automation`), `SCHEDULED` (`schedule_default`, inputs
  `{cron:'INTERVAL', interval, frequency:'MINUTES'|'HOURS'|'DAYS', sequential}` — only `INTERVAL` saves), `EVENT`
  (app/record triggers). Deploying a SCHEDULED workflow starts a live recurring job.

**Native nodes first; Code is the last resort**

| Need | Use |
|---|---|
| filter records | `storage_by_unifyapps_fetch_records` `triggerInputCondition` on `properties_<field>` or `id` |
| count | `storage_by_unifyapps_count_records` `{object_type, triggerInputCondition}` → `outputs.count` |
| group / sum / join / rank | `utility_by_unifyapps_run_sql_query_on_list` (`dataSources:["{{ n_f.outputs.objects }}"]`, the same pill is the table name) — guard against an empty list |
| sort | `utility_by_unifyapps_sort_list` |
| parse JSON text | `utility_by_unifyapps_to_json_object` |
| JSON text for a model | `utility_by_unifyapps_to_json_string` |
| branch / iterate | `IF_ELSE` (`if_else_condition`) / `LOOP` (`loop_for_each`, `loop_while`) |
| call another workflow | `CALL_WORKFLOW` with `callables_call_automation` (`{automationId, version:"-1", synchronous:true, parameters}`) |
| update matching records | `storage_by_unifyapps_update_records` `{numberOfRecordsToUpdate:"MULTIPLE", triggerInputCondition, updateFields:[{fieldName, actionType:"SET", setValue}]}` |
| create one / many | `storage_by_unifyapps_create_record` / `storage_by_unifyapps_bulk_create_records` |
| call an LLM | `CALL_INTERFACE_WORKFLOW` `conv_ai_by_unifyapps_call_llm_model_with_options` |
| ask a platform agent | `CALL_INTERFACE_WORKFLOW` `ai_agents_by_unifyapps_invoke_agent` |
| HTTP to a public API | `custom_http_endpoint_execute` (`baseUrl` + `path` + `httpMethod`, no connection) |

Use Code (`code_by_unifyapps_groovy`) only for a real computation no node covers: one job per node, titled with why,
under ~40 lines. ⛔ `storage_by_unifyapps_aggregate_records` and `utility_by_unifyapps_filter_list` do not work on
UAT (plausible wrong totals / empty lists, no error).

**Gotchas that answer 200 and do nothing**

- `saveAndReturnViolations` returns **200 and persists** a graph with violations. Always check `violations`.
- A **save is not a deploy**. After any edit to a deployed workflow, re-read `version`, deploy that version, and
  assert `deploymentState.workflowVersion === version`. `deployedVersion` is a counter, not the workflow version.
- A fetch node's collection is `{{ n.outputs.objects }}` (not `.records`), and its count is `{{ n.outputs.total }}`
  (with `includeTotalCount:true`). A fetch with no `triggerInputCondition` returns nothing. Send `{}` for "all".
- Inside a workflow, storage filters use `properties_<field>` (underscore) or `id`. The dot form belongs to the entity
  API. Comparison operators are the short forms (`GTE`, not `GREATER_THAN_OR_EQUAL`). A filter with no value is
  rejected.
- `storage_by_unifyapps_bulk_upsert_records_by_id` takes `updates:[{id, updateFields:[{fieldName, actionType:'SET', setValue}]}]`.
  `{id, properties}` succeeds and writes nothing. `skipIfBlank:true` skips blank `setValue`s. An upsert with a blank
  id inserts a new record.
- A raw-payload write (`useRawPayload:true` on create/update by id) **replaces** the record. Hand it the whole
  record, never a partial one.
- An unresolved template silently drops its key from the output. A template that names a node id not in this
  workflow (copied from another) resolves to nothing.
- A `LOOP` body must sit in the loop's child group (`<loopId>@<parentGroup>@l`). Otherwise the run never ends and
  replays every call in the body. `loop_for_each` takes `listSource` as a **plain template string**. Add the
  `loopback` edge. A `BREAK` still needs an outgoing `next` edge.
- `callables_call_automation` is a **`CALL_WORKFLOW`** node, and LLM/OCR/invoke-agent steps are
  **`CALL_INTERFACE_WORKFLOW`** nodes. As `ACTION` they deploy clean and fail at run time with "No config found".
- `fallbackMode:"CONTINUE"` does **not** continue after a failed connector action, and `MANUAL` + `error` edge did not
  route a connector failure either. Design one unit of work per run.
- Groovy compiles only at **deploy** (always read the deploy response): `owner =` is blacklisted (use
  `payload['owner']`); closure parameters must be unique in the whole script; return Java Strings (`.toString()` on
  interpolated GStrings); `1.0G` not `1G` for decimals; no `Date.format`/`Date.parse` (use `java.time`); null map
  values vanish from the output; JavaScript code nodes reject a top-level `return` — use Groovy.
- LLM node: numbers (`maxTokens`, `temperature`) must be numbers, not strings. Thinking models spend `maxTokens` on
  reasoning (give 3–4× the visible output). Check `finish_reason`.
  Never let the model do arithmetic: pass it computed figures.
- The tenant has a daily AI cost limit. When it is reached, LLM nodes fail with `[COSTFLAG]…` and data sources only
  say "Workflow execution failed". Invoke-agent runs park in `WAIT`.

**Run a test**

```js
const def = await call('GET', `/api/workflow-definition/${id}`);
const { runId } = await call('POST', `/api/test-workflow/initiate-test/${id}`,
  { payload: { claim_code: 'CLM-0001' }, type: 'MOCK', workflowDefinition: def });
// poll status
const st = await call('POST', '/api/aggregation?entityType=WORKFLOW_EXECUTION&group=TEST_WORKFLOW_EXECUTION',
  { entityType: 'WORKFLOW_EXECUTION', group: 'TEST_WORKFLOW_EXECUTION',
    projections: [{name:'STATUS'},{name:'EXECUTION_TIME'},{name:'FAILED_NODES'},{name:'ID'}],
    filter: { op: 'IN', field: 'ID', values: [runId] }, page: { limit: 1, offset: 0 } });
return st.objects?.[0]?.columns;   // STATUS → COMPLETED | FAILED | CANCELLED
```

- `initiate-test` runs the **inline** definition you send, not the deployed one. A green test proves the graph, not
  what an agent tool or data source will run (they call `version:"-1"` = latest **deployed**).
- A test run **writes for real**. Test a write workflow with seed rows made for it.
- `initiate-test` gives up at ~20–60 s (`500 No Response received within specified timeout`, run `CANCELLED`). Test
  slow (LLM) workflows through a data source (§3.6) instead.
- Node outputs (`TEST_WORKFLOW_VARIABLE`) come back `inaccessibleObjects` for workflows created over the API. Verify
  through the STOP payload of a data-source call (§3.6), or through the records the run wrote.
- **A green run does not mean a correct result.** `COMPLETED` only means no node threw. Assert on the real payload,
  and for writes read the records back.

**Verify it exists and works:** zero violations. `deploymentState.workflowVersion === version`. The test run is
`COMPLETED`. The STOP payload or the written records carry the expected values. Tags are visible in the aggregation
projection (§5).

---

### 3.5 AI Agent (+ task, tool → workflow)

| Concept | Entity type | Key fields |
|---|---|---|
| Agent | `ai_agent` | `properties.name`, `instructions` (the system prompt), `agentType` |
| Task | `e_topic_ai_agent` | `description` = **when** to use it (the router matches on it); `instructions[]` = **how** (an array) |
| Tool | `e_action_ai_agent` | a call into a deployed workflow; `topicId` scopes it |
| Capability | `e_action_ai_agent` with `isStandardAction:true` | built-ins: charts, files, web search |

**Endpoints**

| Step | Call | |
|---|---|---|
| Create agent / task / tool | `POST /api/entity` `{entityType, tags:[…], properties:{…}}` | ✅ |
| Read | `GET /api/entity/{entityType}/{id}` (`GET /api/entity/{id}` without the type is 405) | ✅ |
| List (find by name client-side) | `POST /api/entity/{entityType}` `{page:{limit, offset}}`; filter `properties.aiAgentId` for tasks/tools | ✅ |
| Update | `POST /api/entity/update` `{id, entityType, version, tags, properties:<full>}` | ✅ |
| Publish | `POST /api/entity/action/saveAndDeploy` `{...whole entity..., deploymentNotes}` | ✅ |
| Deployed snapshot | `GET /api/entity/deployed/ai_agent/{id}` | ✅ |
| Test turn (send) | `POST /api/workflow/execute/node/sse` (Accept `text/event-stream`) | ✅ |
| Test turn (read) | `POST /api/workflow/execute/node?name=call_automation&fetchConversation=66ab98083d73300e63962287&copilotType=AI_AGENT_TEST` | ✅ |
| Traces | `POST /api/workflow/execute/node?name=GetTraceTimeline&fetchTraceDetail=680cdbcaa3741471fc7c22e9` · `…name=TraceTimelineDetails&fetchTimelineDetails=6943f1be474ba4398bf4201c` | ✅ |

The three automation ids above are platform-shipped automations that the agent test and trace calls name. They are
the same for every agent.

**Minimal request — the build order**

```js
// 0. the tool's workflow is built, deployed and tested first (§3.4)
// 1. agent — tags at the TOP level; agentType MUST be set (the API does not default it)
const agent = await call('POST', '/api/entity', { entityType: 'ai_agent', tags: ['<POC-TAG>'],
  properties: { name: 'Claims Analyst', agentType: 'ai-agent',
                instructions: 'You help claims handlers … (see instruction rules below)' } });
// 2. one task per journey
const task = await call('POST', '/api/entity', { entityType: 'e_topic_ai_agent', tags: ['<POC-TAG>'],
  properties: { name: 'Claim lookup', aiAgentId: agent.id, enabled: true, isAppConnector: false,
                runTimeConnectionEnabled: false, governanceConfig: {},
                description: 'Use this task when the user asks about one claim by its code.',
                instructions: ['Call GetClaim with the claim code.', 'Answer from the returned record only.'] } });
// 3. one tool per workflow — enabled MUST be true (default is false)
const tool = await call('POST', '/api/entity', { entityType: 'e_action_ai_agent', tags: ['<POC-TAG>'],
  properties: { name: 'GetClaim', description: 'Look up one claim by its claim code. Returns the full record.',
                aiAgentId: agent.id, topicId: 'GLOBAL',            // or task.id to scope it to that task
                context: { appName: 'callables', resourceName: 'callables_call_automation' },
                inputs: { automationId: '<workflow id>', version: '-1', synchronous: true,
                          runtimeConnections: {}, parameters: {} },
                enabled: true } });
// 4. publish from the FULL entity, then verify by snapshot
const full = await call('GET', `/api/entity/ai_agent/${agent.id}`);
await call('POST', '/api/entity/action/saveAndDeploy', { ...full, deploymentNotes: 'POC fallback' });
for (let i = 0; i < 3; i++) {
  const a = await call('GET', `/api/entity/ai_agent/${agent.id}`);
  const d = await call('GET', `/api/entity/deployed/ai_agent/${agent.id}`);
  if (JSON.stringify(a.properties) === JSON.stringify(d.properties)) return { agent: agent.id, task: task.id, tool: tool.id, published: true };
  await call('POST', '/api/entity/action/saveAndDeploy', { ...a, deploymentNotes: 'POC fallback (re-deploy)' });
}
return { published: false };
```

**Agent settings that must exist.** After the first publish, check that `properties` carries `instructions`,
`agentType`, `topicExecutionSettings`, `responseGenerationSettings`, `preProcessingSettings` and `indexingSettings`. An
agent missing them answers once and then hangs in an endless continuation. If they are missing, copy those four blocks
from a known-good agent in the POC's own solution. The model that runs the tool loop is
`topicExecutionSettings.topicExecutionModel` (and `topicSelectionModel`). The answer model is
`responseGenerationSettings.answerGenerationModelSettings.modelId`, which wins over `answerGenerationModel`. Put one
model id in all four slots. Do not send `sendSuggestedQueries` on create (500).

**Capabilities.** Add a capability as a tool row: `{entityType:'e_action_ai_agent', properties:{name:'<capability>',
aiAgentId, isStandardAction:true, enabled:true, topicId:'GLOBAL'}}`. Names include `generateChartTool`,
`renderArtifact`, `executeCodeTool`, `webSearch`, `createDocx`, `createPDF`, `createExcel`, `loadSkill`. Charts need
**all three** of `generateChartTool` + `renderArtifact` + `executeCodeTool`. With fewer, the agent claims a chart and
none renders, or the turn ends silently. Charts are costly (one request measured ~291 K tokens). Add them only when
the plan asks.

**Human approval.** Every tool that writes gets `properties.approvalConfig = {enabled:true,
storeUserApprovalPreference:false}`. Instructions alone do not stop a write. Republish after changing it.

**Gotchas**

- `POST /api/entity/{type}` **lists**, it does not create. Update is `POST /api/entity/update` with the whole entity
  (partial → validation error or silent field loss). An update without `tags` clears the tags.
- `saveAndDeploy` validates the whole entity (`required name` if `properties.name` is missing). The first
  `saveAndDeploy` after an edit can deploy the pre-edit snapshot. Verify by comparing the deployed snapshot's
  `properties` with the agent's (at most 3 re-deploys). Never loop on `version === deploymentState.entityVersion`:
  `version` keeps climbing by itself.
- Creating tasks/tools bumps the agent's `version`. A publish with a body read before them can fail "version N is
  stale" (5001). Re-read and retry.
- Agent tools default to `enabled:false`. Disabling a tool does not remove it from the schema.
- ⛔ **Never set `deleted:true` on a task or tool.** It makes the entity unupdatable and breaks the whole agent ("The
  agent hit an unexpected error" on every question), with no way back over the API. To retire a task, move its tools
  to another topic and set `properties.enabled=false`. Never leave a topic with zero tools.
- `conversationStarters` is an array of plain strings.
- `ICONTAINS` on `lcName` does not filter entities, and entity aggregation projections return only `id`/`tags`. Find
  an agent by name with `POST /api/entity/ai_agent` and filter `properties.name` client-side. Skip rows named
  `… (Deep Clone) for optimizationRun-…`.

**Instruction rules that make the agent work**

- Tool and task `name` + `description` are what the model routes on. Write them as instructions to a model. A
  detail tool must say why it is required ("the ONLY read that returns X — MUST be called for …").
- Put behaviour rules in **every Task's instructions**, not only the agent prompt. A Task's instructions arrive later
  in the context and dominate.
- Add a turn-ending contract: the last thing written is the answer, never a plan; at most five calls of a query
  tool per turn; a partial answer with its gap stated is the deliverable. Write rules positively, and never quote
  the phrase you want to forbid.
- A generic query tool needs **three** filter pairs (ANDed, comma = IN list), `object_total` beside `returned`, and
  a `group_by` (+ `sum_field`) option so the model never counts rows by hand.
- Identity: the model only knows the signed-in **username**. An identity tool matches on username and resolves
  role from data. Never hard-code a user id in instructions.
- After a Deny on an approval card, the agent must not retry and must not blame the session.

**Run a test question**

```js
// send — read the stream until it closes; caseId arrives in the first event
const r = await fetch('/api/workflow/execute/node/sse', { method: 'POST', credentials: 'include',
  headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
  body: JSON.stringify({ context: { appName: 'callables', resourceName: 'callables_call_automation_streaming' },
    inputs: { automationId: '67dcfe388445037d9b0662c0', synchronous: true,
              debugParams: { createCase: '67dcfe388445037d9b0662c0' },
              parameters: { copilotType: 'AI_AGENT_TEST', message: 'What is the status of CLM-0001?',
                            messageContentType: 'MARKDOWN', aiAgentId: '<agent id>', timezoneId: 'UTC' } } }) });
// …read r.body.getReader() to the end, take caseId from the first data: line…
// read the conversation (poll until additional.responseGenerationStatus === 'completed')
await call('POST', '/api/workflow/execute/node?name=call_automation&fetchConversation=66ab98083d73300e63962287&copilotType=AI_AGENT_TEST',
  { context: { appName: 'callables', resourceName: 'callables_call_automation' },
    inputs: { automationId: '66ab98083d73300e63962287', synchronous: true,
              parameters: { copilotType: 'AI_AGENT_TEST', caseId: '<caseId>', userId: '<user id>',
                            aiAgentId: '<agent id>', until: Date.now() } } });
```

- The stream can close after ~2 s with `responseGenerationStatus: pending`, while the turn keeps running. Poll the
  reader. Run the whole test as a background promise on `window` (the JavaScript tool's 45 s ceiling).
- `response.messages[]` is **reverse chronological**. The answer is the **first** Bot message without
  `additional.internalMessageType` (that marks THOUGHT lines). Do not take the longest one: in a stalled turn it is a
  narration. `completed` can arrive while the newest Bot message is still interim narration, so wait a few seconds
  and re-read.
- A guardrail-blocked turn never reaches `completed`. The signal is `guardrailHit:true` and the blocked message
  (`governance.md`).
- Cost and tokens are in `llmUsageDetails`. A turn with one tool call took 15–60 s on UAT.

**Verify it exists and works:** the deployed snapshot equals the agent's properties. Every tool has `enabled:true` and
an `automationId` that is deployed. No two tools share a name. One test question per task gets an answer that comes
from a tool result (the trace shows the tool span), with no trailing plan.

---

### 3.6 Data source (on an object, automation or connector)

Every read or write an app makes is an `e_data_source` entity that names **one** connector action (`context`) plus its
stored `inputs`. Building the app's pages is not part of the fallback. The fallback creates a data source only when
the failed task is the data source itself, attached to the app UnifyApps Headless already created.

**Endpoints**

| Step | Call | |
|---|---|---|
| Create | `POST /api/entity` `{entityType:"e_data_source", tags, properties}` | ✅ |
| Read | `GET /api/entity/e_data_source/{id}` | ✅ |
| List | `POST /api/entity/e_data_source` — **must** filter `properties.interfacePageId` (else 5011) | ✅ |
| Execute (test) | `POST /api/workflow/execute/node?name=<dsName>&requestId=<dsId>` `{id:<dsId>, context:<same as stored>, inputs:<stored + templated values>, options:{}}` | ✅ |
| Update | `POST /api/entity/update` (whole entity) | ✅ |

**Minimal request — an automation data source on the app's global page**

```js
const v = (await call('GET', '/api/workflow-builder/node/callables/resource/callables_call_automation')).version;
const ds = await call('POST', '/api/entity', { entityType: 'e_data_source', tags: ['<POC-TAG>'],
  properties: { name: 'ds_get_claim', type: 'APPLICATION',
    interfaceId: '<appId>', interfacePageId: 'e_global_<appId>', target: 'app',
    context: { appName: 'callables', resourceName: 'callables_call_automation', resourceVersion: v },
    inputs: { automationId: '<deployed workflow id>', version: '-1', runtimeConnections: {}, synchronous: true,
              parameters: { claim_code: "{{ var_claim['value'] }}" } },
    dP: [{ p: 'inputs.parameters.claim_code' }], dpOn: [],
    advancedOptions: { runBehaviour: 'manual', refetchOnWindowFocus: false,
                       timing: { runQueryOnPageLoad: false, runQueryPeriodically: false } },
    options: { cacheConfig: {} } } });

// test from the tab: same context (resourceVersion included), every stored input, templated ones filled in
const res = await call('POST', `/api/workflow/execute/node?name=ds_get_claim&requestId=${ds.id}`,
  { id: ds.id, context: { appName: 'callables', resourceName: 'callables_call_automation', resourceVersion: v },
    inputs: { automationId: '<deployed workflow id>', version: '-1', runtimeConnections: {}, synchronous: true,
              parameters: { claim_code: 'CLM-0001' } }, options: {} });
return res.response;   // = the workflow's STOP payload
```

**Storage data sources.** `context` `storage_by_unifyapps_fetch_records` (or `_get_record_by_id`, `_count_records`,
`_create_record`, `_update_records`, `_update_record_by_id`). Inputs follow the node contract:
`{object_type, triggerInputCondition:{operator:'AND', filters:[{property:'properties_<field>', filter:{operator:'EQUAL', value}}]}, numberOfRecordsToFetch:'MULTIPLE', page:{paginateBy:'OFFSET', limit}, sortBy:[{field:'properties.<field>', order:'DESC'}]}`.
Never a `*_delete_*` action.

**Connector data sources.** Put the connection in `context.connectionId` (the person's own connection, §3.3).
HTTP: `custom_http_endpoint_execute` with `baseUrl` + `path` + `queryParamsList:[{key, value}]` + `httpMethod` +
`authType:'NO_AUTH'`. A single `url` input fails "Base URL must start with http(s)".

**Gotchas**

- **Input-shape drift is refused.** A call whose non-templated inputs differ from the stored ones, or that omits a
  stored input, answers `500 forbidden datasource : invalid input`. A call without `id`, or for an unregistered
  action, answers `forbidden datasource: not found`. The call's `context` must carry the stored `resourceVersion`.
- On a read, a data source called without one of its templated inputs does not error. The placeholder reaches the
  workflow as literal text and the read returns zero rows. Send every templated input, blank where unused.
- A data source on `e_global_<appId>` evaluates `{{ }}` in the **global** page's scope: page variables are undefined
  there. Bind page state only on a page-level data source (`interfacePageId` = that page). The same workflow id can
  back one data source per page.
- Without a transformer, an automation data source's data **is** the workflow's STOP payload. With a transformer
  (`options.transformerConfig`, server-side JavaScript), the page sees the transformer's return value.
- A **running** (published) app cannot see a data source created after its last publish (`forbidden datasource: not
  found` from the app, while the same call works from the console tab). The app must be republished. That is
  UnifyApps Headless's job: say so in the hand-back.
- `refetchOnWindowFocus` defaults to true in the builder. Set it false for LLM-backed sources.
- One data source per workflow. A generic dispatcher that takes the workflow id as a parameter is refused.

**Verify it exists and works:** the read-back shows the stored `context` and `inputs`. The execute call from the tab
returns the expected payload (records, or the STOP result) with every templated input filled.

---

## 4. Search before create — reuse inside the POC's solution

Before creating, look for the asset in the POC's solution (by its tag, its name prefix, or the solution's linked
assets, §5). If it exists and is the POC's own, reuse it: go to read-back and test, and hand its id back. Never build
a duplicate next to it. An asset that is not the POC's (another owner, another solution, no POC tag) is read-only.
Never edit it, and never reuse it as if it were the POC's.

| Asset | Search call (read-only) | Notes |
|---|---|---|
| Object | `POST /api/aggregation?entityType=EntityType&group=STANDARD`, filter `standard` EQUAL false OR MISSING, projections `id,name,tags,oUId,columns,cTm` | or `GET /api/entity-type?entityType=<planned id>` — empty body = free. Filtering on `id` with `CONTAINS`/`LIKE` → 500 |
| Records | `POST /api/entity/{objectId}` `{includeTotalHits:true, page:{limit:1, offset:0}}` | load only what is missing; creates are idempotent by key (E11000 = already there) |
| Connection | aggregation `entityType=Connection` by `appName` + `active`, prefer `oUId` = the signed-in user | never `GET /api/connection` |
| Workflow | `POST /api/aggregation?entityType=WorkflowDefinition&group=STANDARD`, filter `d` EQUAL false + `lcName` ICONTAINS `<name>`, projections `id,name,tags,deployed,cTm,oUId` | `name`/`CONTAINS` → 500; names are not unique, so check the `tags` column and the owner in the rows |
| Agent | `POST /api/entity/ai_agent {page:{limit, offset}}`, filter `properties.name` client-side; or aggregation `entityType=ai_agent&group=ENTITY` with `tags` IN `[<POC-TAG>]` | skip `(Deep Clone)` rows |
| Task / tool | `POST /api/entity/e_topic_ai_agent` / `e_action_ai_agent` with filter `properties.aiAgentId` | de-duplicate by `name` |
| Data source | `POST /api/entity/e_data_source` with filter `properties.interfacePageId IN ["e_global_<appId>", …]` | match `name` |
| Connector / action | `connectors-index.tsv`, then `GET /api/workflow-builder/node/{app}/resources` | `connectors.md` |

Full aggregation body for workflows:

```json
{ "entityType": "WorkflowDefinition", "group": "STANDARD", "includeTotalHits": true,
  "filter": { "op": "AND", "values": [
      { "op": "EQUAL", "field": "d", "values": [false] },
      { "op": "ICONTAINS", "field": "lcName", "values": ["pc_get_claim"] } ] },
  "sorts": [{ "field": "cTm", "order": "DESC" }],
  "projections": [{"name":"id"},{"name":"name"},{"name":"tags"},{"name":"deployed"},{"name":"oUId"},{"name":"cTm"}],
  "page": { "limit": 30, "offset": 0 } }
```

If a half-built copy from the first attempt exists (e.g. the stub workflow was created and the save failed), fix
**that** one. Never create a second.

---

## 5. Tagging and ownership — keeping the asset in the POC's solution

Every asset the fallback creates carries three markers:

1. **The POC's name prefix** from the plan (e.g. `pc_` on objects and workflows). This is the same prefix UnifyApps
   Headless uses, so the asset reads as part of the build.
2. **A tag**: the POC's tag (the POC ID). `tags` is a plain array of strings at the **top level** of the create body,
   never inside `properties` (inside → 500 `add additionalProperties tags`).
3. **The solution link**: the asset is handed back to UnifyApps Headless with its id, so it is linked into the POC's
   solution (`<Client> — <Use case>`, id recorded in `04-build/`).

Facts that matter:

- ✅ There is no tag API (`/api/tag`, `/api/tags`, `/api/entity-tag` → 404). Tags go in the create/update body.
- ✅ `GET /api/workflow-definition/{id}` does not return `tags`. Read them back with an aggregation projection
  (`projections:[{name:"id"},{name:"tags"}]`). Entity tags read back with `GET /api/entity/{type}/{id}`.
- ✅ `POST /api/entity/update` without `tags` clears them. Resend them on every update. Tasks and tools keep tags
  set at create.
- ✅ An agent can be found by tag: aggregation `entityType=ai_agent&group=ENTITY`, filter `tags IN [<tag>]`.
- ✅ Records, objects, connections and workflows are owned by the signed-in user (`ownerUserId` / `oUId` = the
  person). Records are also stamped with `lastModifiedBy`.
- **The solution entity** (`e_solution`, listed with `POST /api/entity/e_solution`) carries `linkedEntities:[{id, type, state, version}]`. Linked types are only
  `CONNECTION`, `ENTITY_TYPE`, `WORKFLOW_DEFINITION` and `e_interface`; agents, records and data sources are not
  linked there and rely on the prefix and tag. ✅ Reading it is safe. ⚠️ Writing `linkedEntities` over REST has
  not been verified. Prefer the hand-back: UnifyApps Headless links the id into its solution. Do not edit the
  solution entity yourself. If a hand-back reply says the asset could not be linked, record that in
  `fallback-<n>.md` and list it at the verify gate.

Hand-back text, as SKILL.md step 5 gives it: "Task <n> (<entity>) was built outside the builder: <type> `<name>`,
id `<id>`. Mark the task done, do not rebuild it, and wire every task that waits on it to this id." For a data
source, add: "The app must be republished before it can call this data source."

---

## 6. Never

- **No delete endpoints.** Never call `POST /api/workflow-definition/delete/{id}`, `POST /api/entity/{type}/delete/{id}`,
  `POST /api/entity/action/delete`, any `/api/context-graph/**/delete/{id}`, or anything else listed under "Never
  call (deletes)" in `api-spec.md`.
- **No HTTP `DELETE`** on any URL.
- **No delete flags.** Never set `deleted: true` or send `requestType: "DELETED"`, on anything.
- **No delete steps.** Never build `storage_by_unifyapps_delete_record(s)`, `_delete_record_by_id`, a connector
  `*_delete_*` / `*_remove_*` action, or SQL `DELETE` / `DROP` / `TRUNCATE` into a workflow, data source or agent tool.
  To switch something off: `enabled:false`, a status / `archived` / `active:false` flag, or leave a workflow
  undeployed (or pause it). A scratch asset from a failed attempt stays; name it in `fallback-<n>.md`.
- **No pages, app UI, themes, navigation or app publishing.** They belong to UnifyApps Headless.
- **No other solution, user or tenant.** Write only to assets this POC created. Read others to learn, never change
  them. Orbit UAT only. Never reuse an id from another tenant.
- **No passwords or secrets.** Never type a password, complete a sign-in or OAuth consent, read cookies or browser
  storage, print `connection.userInput`, or put a credential in a request body, file or the chat.
- **No retry loops on 401.** A 401 or an HTML response means the person must sign in again.
- **No third attempt.** Two attempts per asset, then record why and stop.
