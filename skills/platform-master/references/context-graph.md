# Enterprise Context Graph — when a POC needs one, and how to build and query it over the API

`platform-master` uses this file when a use case needs a context graph: the plan review checks a plan that puts a
graph in, and the fallback builds a graph asset UnifyApps Headless could not. It covers what the Enterprise Context
Graph (ECG) is, when a POC needs one, how to create, populate and query it over the REST API from the person's
signed-in tab (`fallback-by-api.md` §2), and the gotchas. Everything is stated for **Orbit UAT**. Most of the graph
work was verified on another tenant; those facts are marked "verified on another tenant; confirm on Orbit UAT before
relying on it". Evidence markers: ✅ verified · 👁 observed · 📦 bundle-only · ⚠️ partial · ⛔ does not work.

---

## 1. What it is

A context graph is a model of the business: **node types** (Customer, Deal, Invoice), **edge types** (`HAS_DEAL`),
**records** of each node type, and **record-level edges** between records. It is queried with **OpenCypher** through
a workflow step. It also has a source pipeline (connector → discover → enrich → map) for continuous ingestion from
SaaS systems.

- A node type is backed by a Data Object whose id is its `unifiedEntityId` (`ue`). Records are entities of that type.
- The Cypher label of a node type is its `unifiedEntityId` (backticked). Properties appear as `_pr_<propertyId>`.
- Record ids are primary-key values (`CUST-001`). A vertex id is `{spaceId}::{unifiedEntityId}::{recordId}`.
- Each graph gets its own `mdm_by_unifyapps` connection, created automatically (named `<graph> UDM Connection`, or
  `<graph> Ontology Connection` on newer builds). Every MDM workflow step uses it.

## 2. When a POC needs one

Use a graph when the scoping document asks for a **"360", "brain", "one record", relationships or lineage across
systems**: questions whose answer is a traversal (customer → deals → stage; claimant → claims → shared bank
account), or an agent that must answer "who is connected to what". Do **not** add a graph for plain lists,
dashboards or CRUD. Data Objects and workflows are simpler, faster and fully verified on Orbit UAT.

When a plan includes a graph:

1. **Run the engine probe first (§3.1).** On Orbit UAT the ECG endpoints answer, but the graph engine behind them
   was found absent: every Cypher read failed. If the probe fails, the plan must fall back to Data Objects plus
   traversal workflows over objects, and say so.
2. Design the ontology (node types, keys, edge types) before any screen.
3. Decide the read path before the first object. Moving reads from objects to the graph later meant rewriting
   every data hook.

---

## 3. Create — the build order

```
0. Probe that the graph engine exists (§3.1)
1. POST /api/context-graph                    {name, description}      → graphId (+ auto UDM connection)
2. POST /api/context-graph/{graphId}/publish  DRAFT → LIVE   ← BEFORE loading any records
3. POST /api/context-graph/nodes              one per node type, every property STRING + graphQueryable
4. POST /api/context-graph/edges              {graphId, label, fromNodeId, toNodeId}
5. Records into each node type                (§4)
6. Verify projection: MATCH (n:`<ue>`) RETURN count(n) per type
7. Record-level edges with an MDM workflow    (§4.2)
8. A query workflow: mdm_by_unifyapps_execute_opencypher_query, deployed
9. Agent tool → that workflow (enabled:true); publish the agent; verify by snapshot
```

Node types can be created before or after publish; **records must come after**.

### 3.1 The engine probe (run before building)

```js
// after creating a throwaway node type in the POC's graph, publishing it and writing one record:
await call('POST', `/api/context-graph/${graphId}/nodes/${ue}`, { includeTotalHits: true, page: { limit: 1, offset: 0 } });
// 200 with a row → the engine is there.
// 500 "org.neo4j.driver.exceptions.ServiceUnavailableException: Unable to establish connection in 30000ms"
//   (from EntityRelationshipService) → it is not. The graph header, node counts and edge counts still read fine.
```

✅ On Orbit UAT, creating a graph, publishing it, creating node and edge types and writing records all returned 200,
but every projection-backed read failed with that error and did not recover. Verified on another tenant: the same
build ran end to end. Run the probe at the start of every graph task; do not assume either way.

### 3.2 Endpoints

**Graph**

| Method | Path | |
|---|---|---|
| POST | `/api/context-graph` | **Create.** Body `{name, description}` → `{id, status:"DRAFT", nodeCount:1, unifiedEntityModelId:<same as id>, version:1}` |
| GET | `/api/context-graph/{graphId}` | Read the header |
| POST | `/api/context-graph/update/{graphId}` | Update |
| POST | `/api/context-graph/{graphId}/publish` | **DRAFT → LIVE** |
| GET | `/api/context-graph/templates` | Prebuilt graph templates |

Creating a graph also creates a default node **`ecg_grant`** ("default access-grant node", properties `uid`,
`mdmRecordMetadata`); leave it alone. The graph's `mdm_by_unifyapps` connection has
`userInput.unifiedEntityModelId = <graphId>`. Find its id with:

```json
POST /api/lookup?ByQuery=CONNECTION
{"type":"ByQuery","lookupType":"CONNECTION","query":"<graph name>","fields":["name"],
 "options":{"appName":"mdm_by_unifyapps"},"page":{"limit":20,"offset":0}}
```

Never hand-create it: `POST /api/connection` fails with `No Value found in filter with field: sourceConnectionId`.

**Node types**

| Method | Path | |
|---|---|---|
| POST | `/api/context-graph/nodes` | **Create node type** |
| GET | `/api/context-graph/nodes/{nodeId}` | Full node incl. `properties[]`, `entityMetadata`, `recordTitleFormat` |
| POST | `/api/context-graph/nodes/update/{nodeId}?version={n}` | **Update** — the version goes in the **query string**; body = the full node |
| POST | `/api/context-graph/nodes/bulk-update-node-positions` | Canvas layout |
| GET | `/api/context-graph/nodes/templates` | Node template catalogue |
| POST | `/api/aggregation?entityType=KNOWLEDGE_GRAPH_NODE&group=STANDARD` | **List a graph's node types** with name, id **and** `unifiedEntityId` |

There is no `GET /api/context-graph/{graphId}/nodes` (404). List node types like this:

```json
POST /api/aggregation?entityType=KNOWLEDGE_GRAPH_NODE&group=STANDARD
{ "entityType":"KNOWLEDGE_GRAPH_NODE", "group":"STANDARD",
  "filter":{"op":"AND","values":[{"field":"graphId","op":"EQUAL","values":["<graphId>"]}]},
  "projections":[{"name":"id"},{"name":"name"},{"name":"unifiedEntityId"},{"name":"cTm"}],
  "sorts":[{"field":"name","order":"ASC"}], "page":{"limit":200,"offset":0} }
```

Create a node type:

```json
POST /api/context-graph/nodes
{ "graphId": "<graphId>", "name": "Customer", "category": "core", "description": "...",
  "iconUrl": "account-executive", "nodePosition": {"x": 0, "y": 0},
  "recordTitleFormat": "{{ mdm.field.customer_name }}",
  "properties": [
    {"id":"customer_id","displayName":"Customer Id","dataTypeInfo":{"type":"STRING"},
     "primaryKey":true,"required":true,"unique":false,"pii":false,
     "filterable":false,"sortable":false,"searchable":false,"graphQueryable":true,"standard":false},
    {"id":"customer_name","displayName":"Customer Name","dataTypeInfo":{"type":"STRING"},
     "primaryKey":false,"required":false,"unique":false,"pii":false,
     "filterable":false,"sortable":false,"searchable":false,"graphQueryable":true,"standard":false} ] }
```

The response carries the server `id` **and** the `unifiedEntityId`. Property ids land in
`entityMetadata.graphQueryableFields`, which is what makes them addressable as `_pr_*`.

**Edge types**

| Method | Path |
|---|---|
| POST | `/api/context-graph/edges` — `{"graphId","label":"WORKS_AT","fromNodeId","toNodeId"}` |
| GET | `/api/context-graph/edges/{edgeId}` |
| POST | `/api/context-graph/edges/update/{edgeId}` |

A type-level edge only **declares** that a relationship may exist. It materialises nothing.

**Records and reads**

| Method | Path | |
|---|---|---|
| POST | `/api/entity` | **Create a record** — `{entityType:<unifiedEntityId>, properties:{…}}`; `id` = the primary-key value |
| GET | `/api/entity/{unifiedEntityId}/{recordId}` | Raw record incl. `mdmRecordMetadata` (field-level lineage) |
| POST | `/api/entity/update` | Update — the **whole** entity as read |
| POST | `/api/context-graph/{graphId}/nodes/{unifiedEntityId}` | **List records** of a node type. Body `{includeTotalHits, page:{limit, offset}}` → flat props + `_ua_recordTitle`, `labels`, `modelId` |
| GET | `/api/context-graph/{graphId}/unifiedEntity/{ue}/records/{recordId}` | A record with its `edges[]` |
| GET | `/api/context-graph/{graphId}/unifiedEntity/{ue}/records/{recordId}/graph?depth=1` | Neighbourhood subgraph |
| GET | `/api/entity-type?entityType={ue}` | The node type's object schema (`name` = the node type's real name) |

A record read returns edges like
`{"direction":"OUTGOING","entityType":"<other ue>","isDangling":true,"recordId":"TKT-002","relationshipLabel":"HAS_TICKET", …}`.
`isDangling:true` means no matching type-level edge was declared; the edge still traverses.

UI routes: `/p/0/context-graphs` (list) · `/p/0/context-graphs/{graphId}?tab=nodes|edges|sources|records` ·
`…?tab=records&recordNodeId={nodeId}&recordId={recId}` (one record's view).

---

## 4. Populate

### 4.1 Records

- **Small sets (POC seed data):** `POST /api/entity` per record, ~8–10 in parallel, from the tab
  (`fallback-by-api.md` §3.2). Verified on another tenant: 28,848 records in ~9 min at concurrency 10, zero failures.
- **Large sets:** bulk-create **into the node type** with a callable workflow:
  START `{object_type, rows_json}` → Groovy `JsonSlurper` → `storage_by_unifyapps_bulk_create_records`
  (`object_type` = the `unifiedEntityId`, `useRawPayload:true`, `rawPayload` = the array, `skipUpdate:false`) → STOP
  with `insertedIds[]`. Run it synchronously through a data source. Verified on another tenant: 1,000 records in
  ~1.4 s; bulk create upserts by primary key, so a short slice can be reloaded. Confirm on Orbit UAT before relying
  on it.
- After the first record of **each** node type, check that it projects (§5). Catch a non-projecting type at record 1,
  not record 200.

### 4.2 Record-level edges

Records never link themselves. A matching `customer_id` property creates no relationship. Write edges from a workflow
with the graph's MDM connection in `context.connectionId`.

**A. `mdm_by_unifyapps_add_edge_to_graph`** (one edge per call):

```json
{"id":"n_e0","type":"ACTION","title":"CON-001 -[WORKS_AT]-> CUST-001",
 "context":{"appName":"mdm_by_unifyapps","resourceName":"mdm_by_unifyapps_add_edge_to_graph",
            "resourceVersion":"<resolve>","connectionId":"<graph MDM connection>","type":"APPLICATION"},
 "inputs":{"modelId":"<graphId>",
           "primaryEntityType":"<contact ue>","primaryEntityId":"CON-001",
           "associatedEntityType":"<customer ue>","associatedEntityId":"CUST-001",
           "label":"WORKS_AT","updateIfPresent":true},
 "fallbackMode":"STOP","skip":false,"index":2}
```

Required: `modelId, primaryEntityType, primaryEntityId, associatedEntityType, associatedEntityId, label`. The entity
types are `unifiedEntityId`s; the ids are primary-key values. Output `{success, fromNodeId, toNodeId}`. At scale, run it
inside `loop_for_each` over a JSON array input: `listSource` is a **plain template string**, the body sits in the
loop's child group, and the loop has a loopback edge. Verified on another tenant: 11,588 edges in 59 runs of 200 with
zero failures. On a later, larger build the same loop timed out every time through the test runner.

**B. `mdm_by_unifyapps_execute_opencypher_update` with `UNWIND … MERGE`** (verified on another tenant: 100 edges in
364 ms, 500 per call):

```cypher
UNWIND [{f:'<prefix>::<ue_a>::A-1', t:'<prefix>::<ue_b>::B-7'}] AS r
MATCH (a:`<ue_a>`) WHERE a.id = r.f
MATCH (b:`<ue_b>`) WHERE b.id = r.t
MERGE (a)-[:LABEL]->(b)
```

Match on the node's `id` (the first segment is the tenant prefix; read it from any node with
`MATCH (n:\`<ue>\`) RETURN n.id` and node `limit` 1). Matching on a `_pr_` property instead is a label scan (8.6 s
per 100). The action returns only `{success:true}`: count afterwards. Do not write edges to a type that has not
finished projecting. A `MERGE` after a failed `MATCH` writes nothing, silently.

**Verify edges by counting in Cypher before and after** (`MATCH (:\`<ue_a>\`)-[r:LABEL]->(:\`<ue_b>\`) RETURN count(r)`).
A loop's STOP cannot see its own body's output, so a batch that wrote nothing still reports success.

### 4.3 Updating graph records

| Method | Result |
|---|---|
| `POST /api/entity/update` `{entityType, id, properties}` (partial) | **200, writes nothing** |
| `POST /api/entity/update` with the **whole** entity from `GET /api/entity/{ue}/{id}` | ✅ |
| `storage_by_unifyapps_bulk_upsert_records_by_id` | `success:false`, "Service EntityService remote call failure" |
| `storage_by_unifyapps_bulk_update_record_by_id` | `{failedCount:0, updated:0}`: no error, nothing written |
| `storage_by_unifyapps_update_record_by_id`, `useRawPayload`, **whole** properties map | ✅ |

(Verified on another tenant; confirm on Orbit UAT before relying on it.) A record written through the store is
invisible to Cypher for seconds to minutes. Never read a record back through Cypher to merge into it: read it with
`GET /api/entity/{ue}/{id}`.

### 4.4 Ingestion from connectors (sources)

Two mechanisms; pick per source:

| | Source pipeline (wizard) | Connector actions in a workflow |
|---|---|---|
| Configured via | Sources → Discover & Enrich → Map → Publish | the workflow definition API |
| Good for | continuous broad sync, unstructured content | scoped, per-record sync |
| Scoping | per connector: Slack yes (`channelList`); HubSpot no (all companies/deals/contacts) | exactly the records named |
| Blocker | the **Map** step cannot be written over the API (405) | none |

For a POC (dummy seed data), records come from seed loads (§4.1), not live sources. Use the source APIs only to
inspect what a connector would expose:

| Method | Path | |
|---|---|---|
| GET | `/api/context-graph/sources/applications/{appName}/objects` | the objects a connector exposes (its data model) ✅ |
| POST | `/api/context-graph/sources/applications/{appName}/objects/{objectId}/details?connectionId=` | an object's schema, body `{}` ✅ |
| POST | `/api/context-graph/sources` | register `{graphId, appName, connectionId, name}`; starts as Draft ✅ |
| GET | `/api/context-graph/sources/{sourceId}` | incl. `objectDiscoveryConfigRefs[]` ✅ |
| POST | `/api/context-graph/sources/update/{id}` | update ✅ |
| POST | `/api/context-graph/sources/{sourceId}/object-discoveries/scope-configs/bulk-save` | scope (Slack `channelList`) ✅ |
| POST | `…/object-discoveries/discovery-configs/bulk-save` | ⚠️ 200, but the enricher binding does not persist |
| GET | `/api/context-graph/sources/{sourceId}/objects/fetch-selected?limit=200&offset=0` | per-object `objectSchema`, `enrichedObjectSchemas`, `schemaMappings` ✅ |
| POST · PUT · PATCH | `/api/context-graph/sources/{sourceId}/schema-mappings`, `…/schema-mapping/automap` | ⛔ 405: the Map step is wizard-only |
| POST | `/api/context-graph/sources/{sourceId}/objects/bulkUpdate` | ⛔ 200 `{"data":0}`: writes nothing |
| POST | `/api/context-graph/sources/objects/describe` | `{connectionId:<graph MDM connection>, objectId:<ue>, sourceConfigId}` → destination fields ✅ |
| GET | `/api/context-graph/sources/enrichers/{method}/{agentId}/{n}/schema` | an enricher agent's output schema ✅ |
| POST | `/api/context-graph/sources/{sourceId}/publish` | 📦 |

(The source surface was verified on another tenant; confirm on Orbit UAT before relying on it.) An empty
`channelList` means **every** channel: always set it. Data Objects are not a source type; ingest object data with
the bulk-create workflow. The `ecg_by_unifyapps` pipeline actions (`run_discovery`, `translate_raw_record`,
`apply_enrichment`, `publish_record`) all require a published source config, so they do not bypass the wizard.

**Enricher agents** (when a source needs one): an `ai_agent` with `role: "Enricher"` whose
`responseGenerationSettings.outputSchema` (`{results:[{…fields…}]}`) is the contract. Name its output fields to match
the destination node's property ids, so mapping is one row. Prompt rules: one input yields one row per extracted
entity; never a Cartesian product of unrelated entities; ids derived from the source record, never invented; look up
existing records before assigning ids (or every run creates duplicates). Do not use an LLM for pure capture.

---

## 5. Query

Queries run through the workflow action **`mdm_by_unifyapps_execute_opencypher_query`**, not a REST endpoint:

```json
{"type":"ACTION","context":{"appName":"mdm_by_unifyapps","resourceName":"mdm_by_unifyapps_execute_opencypher_query",
            "resourceVersion":"<resolve>","connectionId":"<graph MDM connection>","type":"APPLICATION"},
 "inputs":{"modelId":"<graphId>","query":"{{ n_in.outputs.cypherQuery }}","limit":100,"offset":0,"skipRBAC":false}}
```

Required `query`, `modelId`; optional `limit` (1–1000, default 100), `offset`, `skipRBAC`, `outputSchema`. Output
`{stats, objects:[…], success}`: bind `{{ n_q.outputs.objects }}`.

**Conventions**

```cypher
MATCH (c:`<customer_ue>`)
WHERE toLower(coalesce(c.`_pr_name`, '')) CONTAINS 'northwind'
MATCH (c)-[:HAS_DEAL]->(d:`<deal_ue>`)-[:AT_STAGE]->(s:`<stage_ue>`)
RETURN d.`_pr_deal_name` AS deal, s.`_pr_label` AS stage, labels(d) AS labels, d.modelId AS modelId
LIMIT 50
```

- Every `RETURN` includes `labels(v) AS labels` and `v.modelId AS modelId`.
- Never bind with an inline `{prop: value}` map. Match the bare label, then filter with
  `WHERE toLower(coalesce(…)) CONTAINS`. For categorical fields use `=` against the exact values: `CONTAINS '90'`
  also matches `'61-90'`.
- **Every property is a string.** Use `toFloat()` / `toInteger()` on every comparison, `ORDER BY` and `sum()`. Store
  dates as `YYYY-MM-DD`.
- **Name a node type in every pattern.** The engine is shared by every graph of the tenant: an unlabelled
  `MATCH ()-[r]->()` returned **other graphs'** relationship types. Count with one labelled `MATCH` per type joined
  by `UNION ALL`. Refuse a model-written statement that has an unlabelled node or a write keyword (`CREATE MERGE SET
  DELETE DETACH REMOVE DROP CALL LOAD FOREACH`).
- **At most 1,000 rows** come back, whatever limit is asked. A statement's own `LIMIT` is ignored; the node's `limit`
  input wins. `ORDER BY` applies before the limit. So every total, count and share is a `sum()`/`count()` **in the
  query**. Never reduce a truncated read in the app.
- The graph does not denormalise foreign keys. A per-customer read is a **traversal**. Joining a counterparty onto a
  list is `OPTIONAL MATCH`: a plain `MATCH` silently drops rows whose edge is missing.
- An empty `query` answers 500 `query is required`. Guard it in the workflow (decide in Groovy, then bind).
- A Cypher `collect()` reaches Groovy as a JSON list **string**: parse it.
- Let a model write friendly names (`(f:Finding)`, `f.verdict`) and translate them to engine names
  (`` `<ue>` ``, `` `_pr_verdict` ``) before the query runs.

(The query rules above were verified on another tenant; confirm on Orbit UAT before relying on them.)

**Verify projection** after the first record of each type:

```cypher
MATCH (n:`<ue>`) RETURN '<NodeName>' AS type, count(n) AS n
UNION ALL MATCH (n:`<ue2>`) RETURN '<NodeName2>', count(n)
```

A type missing or at 0 has records that will never be queryable. Fix it (§6) and reload that type.

### 5.1 An agent that answers from the graph

The built-in `search_knowledge_graph` default tool did **not** activate from `graphModelId` + `defaultTools`. Build
the tool explicitly:

1. Callable workflow `START(cypherQuery) → mdm_by_unifyapps_execute_opencypher_query → STOP`; deploy it.
2. `e_action_ai_agent` with `callables_call_automation`, `inputs.automationId`, `topicId:"GLOBAL"`, **`enabled:true`**.
3. Put in the agent's instructions: the label ids, the `_pr_` property names, the edge list, the Cypher rules
   above, and the **distinct values** of every categorical property (`RETURN DISTINCT n.\`_pr_<field>\``) with
   "match with `=`, never CONTAINS".
4. `saveAndDeploy`; verify by snapshot (`fallback-by-api.md` §3.5).

One graph-query workflow can serve both screens (through a data source) and agents.

---

## 6. Gotchas

| Symptom | Cause → fix |
|---|---|
| Cypher returns `objects: []` but records exist | the graph was DRAFT when the records were written, or properties aren't STRING / `graphQueryable` → publish first; fix the node type; reload |
| A node type is missing from the counts | same; reload that type's records after publishing |
| Records load, vertices appear with their key only, every filter on another property matches nothing | a property lacks `graphQueryable: true, standard: false` → update the node type with its own properties only (never send back the platform's `_ua_*` properties), publish, write the records again |
| Typed properties (`DATE`, `DOUBLE`, `INTEGER`, `BOOLEAN`) | store fine, but the node projects **zero vertices** → STRING only |
| `500 Please delete data before updating entity schema` | a property **type** change needs zero records → choose STRING up front. Never delete records to get past it |
| `500 version is required for node update` | the version goes in the query string: `/nodes/update/{id}?version={n}` |
| `Validation failed … sourceConnectionId` | do not hand-create the graph's MDM connection |
| Record titles show raw ids | `recordTitleFormat` must be `{{ mdm.field.<prop> }}` |
| `storage_by_unifyapps_create_record` writes nothing | fields go under `record`, not at the top level of the inputs |
| A node → `unifiedEntityId` map built from creation order is wrong | **read it back** with the `KNOWLEDGE_GRAPH_NODE` aggregation (one build had 12 of 16 types mapped wrongly; every query still returned plausible rows) |
| `POST /api/context-graph/nodes` takes ~35 s each | the graph re-projects. Run node creation as a background promise and poll; a timed-out JavaScript call keeps running, and a second pass created duplicate node types |
| Projection lags the load | count after a pause; reload any short slice (bulk create upserts by key) |
| `fallbackMode: CONTINUE` | does not continue: one failed node fails the run |
| Action versions | differ completely between tenants; resolve from `GET /api/workflow-builder/node/{app}/resources` on Orbit UAT |
| A cross-tenant read | there is no UnifyApps-to-UnifyApps connector, MCP or API key. Keep the graph and everything that reads it on Orbit UAT |

**Stage and status trap.** Real source systems recycle ids and mis-set closed flags (a stage id `closedwon` labelled
"Business Win" was an open 70 % stage). Never judge state from an id. Key such nodes on `pipeline::id`, compute
terminal-ness per pipeline at load time, trim labels, and traverse to read `label`/`is_terminal`. For dummy POC data,
generate stages consistently and avoid the problem.

**Testing a graph-backed app** (verified on another tenant; confirm on Orbit UAT before relying on it): diff every
field a screen reads against `GET /api/entity-type?entityType={ue}` (phantom fields render as empty cells, not
errors); state how a KPI series reconciles to its transactions; audit stored LLM findings numerically; take
baselines from the engine, not from an agent's rounded answer.

## 7. Never

- Never delete a graph, node type, edge type, source or record, and never call the context-graph delete endpoints
  listed in `api-spec.md` "Never call (deletes)". To retire a record, set an `active:false` / `archived` property and
  filter on it in every Cypher pattern.
- Never write to a graph that is not the POC's own. Reference graphs built by others are read-only.
- Never put a write keyword in a model-written Cypher statement that the query tool runs.
