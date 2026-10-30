# Connectors — what UnifyApps can connect to, and what each connector can do

`platform-master` uses this file to answer three questions. Can UnifyApps connect to X? What can it do with X: its
actions, triggers and agent tools? Is there already a connection for X on Orbit UAT? The plan review uses it whenever
the Zen plan relies on a connector, and the fallback uses it before building a step, tool or data source that calls
one. Two data files sit beside it: `connectors-index.tsv` (application connectors) and `platform-nodes.tsv` (built-in
platform nodes). Both were harvested from Orbit UAT. Endpoints and request shapes are also in `api-spec.md` §5, §7
and §31. Evidence markers: ✅ verified · 👁 observed · 📦 bundle-only · ⛔ does not work.

POC data is dummy seed data by policy. A POC usually **simulates** a source system as a Data Object shaped like that
system's output, so the connector question is mostly "is this real-world integration possible, and what would it
call", not "wire it now". Build a real connection only when the plan explicitly asks for one.

---

## 1. Three words that get confused

| Term | What it is | Where it lives | Identified by |
|---|---|---|---|
| **Connector** (also *node*, *app*, *application*) | The integration itself: Slack, Oracle DB, Snowflake. Ships with the platform, or is built with the Connectors SDK | `GET /api/workflow-builder/nodes` | `appName`, a lower_snake string (`slack`, `oracledb`, `microsoft_sharepoint`) |
| **Action / trigger / agent tool** (a *resource*) | One thing a connector can do: `slack_post_message_in_channel` | `GET /api/workflow-builder/node/{appName}/resources` | `resourceName` + `resourceVersion` |
| **Connection** | One authenticated instance of a connector (this Slack workspace, that Oracle server). Holds the secrets | `POST /api/aggregation?entityType=Connection&group=STANDARD` | 24-hex `id`, used as `context.connectionId` |

A workflow step, an agent tool, an app data source and a context-graph source all point at the same triple:
**`{appName, resourceName, resourceVersion}` plus a `connectionId`** when the connector needs one.

---

## 2. What the catalogue holds

| File | Rows | Columns | What it is |
|---|---|---|---|
| `connectors-index.tsv` | 983 | `appName` `displayName` | every built-in **application connector** (third-party systems) |
| `platform-nodes.tsv` | 91 | `appName` `displayName` | every built-in **platform node**: code, files, PDF, storage, AI, agents, control flow. None needs a connection |

Lines starting with `#` are headers. The harvest saw 1,214 nodes on Orbit UAT: 983 application connectors + 91
platform nodes + 140 **custom** connectors. Custom connectors are tenant-local (built with the Connectors SDK), so
they are left out of the index: their `appName` is a 24-hex id, not a readable slug.

What the catalogue is **not**:

- **Not a version record.** No `resourceVersion` is stored, on purpose. Resolve it from `/resources` at build time,
  every time. Versions drift daily (four HubSpot actions moved in 24 hours).
- **Not a list of connections.** A connector existing is not a connection existing. Only ~304 of the 983 had any
  connection on Orbit UAT, and most of those had fewer than five.
- **Not a list of actions.** One call to `/resources` gives the current actions for any connector.

---

## 3. "Can UnifyApps connect to X?"

Grep the index. No sign-in is needed:

```bash
grep -i "salesforce\|hubspot" references/connectors-index.tsv
grep -i "sql server\|sharepoint\|zoho crm" references/connectors-index.tsv   # find the appName for a product
grep -i "pdf\|excel\|ocr\|agent" references/platform-nodes.tsv              # platform capabilities
```

**`appName` is not always the product name.** Google Sheets is `gsheets`, Google Calendar is `gcalendar`, Zoho CRM is
`zoho`, SQL Server is `sqlserver`, Ontology/MDM is `mdm_by_unifyapps`. Grep the index; do not guess.

If X is in neither file:

1. Check for a **custom** connector on Orbit UAT (signed-in tab):
   ```js
   (await (await fetch('/api/workflow-builder/nodes?fields=name,displayName,custom',
     {credentials:'include'})).json()).objects.filter(o => o.custom)
   ```
2. Check the live catalogue: `GET /api/workflow-builder/nodes` (the platform adds connectors constantly). The
   `name` filter is ignored, so filter client-side.
3. If X genuinely has no connector, UnifyApps can still call it:
   - **`custom_http_endpoint`**: ad-hoc REST / GraphQL / SOAP / multipart / streaming, **no connection needed**
     (`custom_http_endpoint_execute`, `_execute_graphql`, `_execute_soap`, `_execute_multipart`,
     `_execute_streaming`);
   - **`custom_http_application`**: the same over a saved, authenticated base URL (a connection);
   - a purpose-built connector with the **Connectors SDK** (`api-spec.md` §25). It is real build work, so it is not
     a fallback job.

Answer with the evidence: "Yes — `appName` `<x>` (`<displayName>`), N actions incl. `<a>`, `<b>`; connection on
Orbit UAT: yes/no", or "No built-in connector — reachable through `custom_http_endpoint` (public REST API)".

---

## 4. "What can it do?" — actions, triggers, agent tools

```http
GET /api/workflow-builder/node/{appName}/resources          ✅  every action, trigger and agent tool
GET /api/workflow-builder/node/{appName}/resource/{name}     ✅  one action's input/output contract
```

`/resources` returns `{objects:[{name, displayName, version, nodeName, resourceType, async, hidden, custom, description}]}`:

| Field | Use |
|---|---|
| `name` | the `resourceName` for `context.resourceName` |
| `version` | the value for `context.resourceVersion`. Read it at build time; never hard-code it |
| `resourceType` | `ACTION` (a step) · `TRIGGER` (starts a workflow) · `AGENT_TOOL` (a ready-made agent tool) |
| `async` | the step returns before the work finishes |
| `description` | one line of intent, usually enough to choose between two similar actions |

A short summary of the names, for the person or the plan review:

```js
const r = await (await fetch(`/api/workflow-builder/node/${app}/resources`, {credentials:'include'})).json();
r.objects.map(x => `${x.resourceType}\t${x.name}\t${x.displayName}`).join('\n');
```

`/resource/{name}` returns `input.schema` (generate `inputs` against it), `input.layout` (UI only; but its
`ua:llm_description` entries are the platform's own instructions for filling a field) and `output.schema`.
`input.dynamic: true` means the visible fields depend on a runtime lookup (choose a Salesforce object and the field
list changes). For those, the reliable path is to configure the step once in the UI and read the saved workflow back.
⚠️ The declared output schema is not always the real output (an HTTP node also returns `headers`). Run the action
once and read what it returns.

**Verified resource mixes on Orbit UAT** (ACTION / TRIGGER / AGENT_TOOL): `hubspot` 100/6/– · `jira` 78/13/– ·
`salesforce` 65/11/– · `github` 44/12/2 · `slack` 44/2/– · `gmail` 25/8/– · `oracledb` 17/6/– ·
`custom_http_endpoint` 7/–/–. Large surfaces: `workday` 170, `keka` 170, `netsuite` 146, `snowflake` 145,
`microsoft_teams` 136, `genesys` 112, `hubspot` 106, `databricks_rest` 105, `jira` 91, `trello` 83.

**Execute one action without building anything** ✅: post an inline definition (START → the connector node → STOP,
with a `resourceVersion` you just resolved) to `POST /api/test-workflow/initiate-test/{id}` of a workflow the POC
owns. The inline graph runs and the saved definition is untouched (`fallback-by-api.md` §3.4). A test run writes for
real, so use read actions only. A record-level 404 from the SaaS fails the node and the run, so prefer batch reads.

---

## 5. "Do we already have a connection for X?" — on Orbit UAT

From the person's signed-in tab (`fallback-by-api.md` §2). This is the search the Connections Manager itself uses:
fast (~50 ms), server-side, and it returns **no secrets**.

```json
POST /api/aggregation?entityType=Connection&group=STANDARD
{ "entityType": "Connection", "group": "STANDARD", "includeTotalHits": true,
  "filter": { "op": "AND", "values": [
      { "field": "appName", "op": "EQUAL", "values": ["hubspot"] },
      { "field": "active",  "op": "EQUAL", "values": [true] } ] },
  "projections": [{"name":"id"},{"name":"name"},{"name":"appName"},{"name":"oUId"},{"name":"cTm"}],
  "sorts": [{"field":"cTm","order":"DESC"}], "page": { "limit": 30, "offset": 0 } }
```

- Rows come back as `{objects:[{columns:{id, name, appName, oUId, cTm}}], totalHits}`. For a yes/no answer, set
  `page.limit: 1` and read `totalHits`. Filters work on `appName`, `active`, `oUId`, `name`, `tags`.
- ✅ `POST /api/lookup?ByQuery=CONNECTION` `{type:"ByQuery", lookupType:"CONNECTION", query:"<name>", fields:["name"], options:{appName}, page:{limit:20, offset:0}}`
  searches by name text.
- 👁 `GET /api/workflow-builder/find-nodes-with-connections` (plain array) lists connectors that have at least one
  connection: a quick pre-filter. It over-reports: 25 of its 304 had `totalHits: 0` in the aggregation. **The
  aggregation is the answer.**
- ⛔ Never call `GET /api/connection` (no id). It returns every connection in the tenant (7,700+) **with secrets in
  clear**, ignores every filter, and times out. `GET /api/connection/{id}` returns one connection's `userInput`
  (secrets may be in clear or masked). Read it only to check a host or service name, and never print it.

**Choosing one**

1. Prefer a connection the signed-in person owns (`oUId` = their `user.id` from `GET /api/user-context`).
2. Names are not unique: three different connections on UAT were all called `RDQA-OracleDB-PRY`. Track ids.
3. Never use a connection whose name contains `DND` or `DONT TOUCH`, or one owned by someone else, without its
   owner's permission. Connection metadata is visible tenant-wide and any builder can pick any connection in a
   workflow. A test run on someone's personal Gmail connection really sends mail.
4. `active: false` connections exist and fail at run time with an auth error. Filter on `active`.
5. A model entity whose own connection is inactive fails every LLM call ("Connection … is not active"). Check
   `properties_connectionId` on `ai_agent_llm_model` before choosing a model.

**Snapshot of what Orbit UAT runs on** (connections per connector, at harvest): Ontology 3,296 · Gmail 965 ·
Slack 574 · Google Sheets 392 · Google Drive 285 · Salesforce 111 · Outlook 105 · OpenAI 92 · Snowflake 74 ·
GitHub 73.

**Creating one** is in `fallback-by-api.md` §3.3: the form (`GET /api/applications/{appName}?fields=authSpec,…`),
test (`POST /api/connection/input/test?appName=` → 204), create (`POST /api/connection/input?appName=`). Only
no-secret connections are created over the API. The person creates every connection that needs a secret, and every
OAuth connection (`refreshable: true`), in the Connections Manager (`/p/0/connections/create/{appName}` → Authorize).
Then find it by aggregation.

**Connection form facts** ✅ (`GET /api/applications/{appName}?fields=authSpec,iconUrl,displayName,name,refreshable,includeOptions`):

| `appName` | `refreshable` (≈ OAuth) | required |
|---|---|---|
| `slack`, `github`, `hubspot` | true | name, authType |
| `gmail` | false | name, authType |
| `openai` | false | domain, name, authType, authToken |
| `snowflake` | true | name, authType, domain, databaseName, schemaName, warehouseName |
| `sftp` | false | name, authType, host, port, username |
| `oracledb` | false | — (host, port, username, password, service name, `isCDBDatabase`…) |
| `custom_http_application` | false | name, baseUrl, authType, connectionType |
| `mcp_servers` | false | name, isSSESupported, authType |

`authType` options usually come from `POST /api/lookup?ByQuery=CUSTOMER_AUTH` 👁. `authSpec.externalDocUrl` links the
connector's public docs page (`https://www.unifyapps.com/docs/unify-integrations/{slug}`, where the slug is not always
the `appName`). `custom_http_endpoint` returns 200 with an **empty** body here: it is an internal node with no form.
Oracle EBS uses `oracledb` with `serviceName` = the PDB and `isCDBDatabase:false`. Pointing at the CDB gives
`ORA-01017`.

**Per-user runtime connections (agents)** ✅: an agent tool whose `context` has `{appName, resourceName}`, **no**
`connectionId`, and `runTimeConnectionEnabled: true` makes each signed-in user connect their **own** account. The chat
shows a "Connect" card once, and the platform reuses that user's connection afterwards. Use this for personal
connectors (Gmail, Drive, Calendar). Never bind those to a fixed connection. Caveats: custom SDK connectors render the
card blank (Connect still works). A turn waiting on a connection the user has not made sits in "Wait For Tool Calls".
The "runtime user connections" setting is not exposed for **workflows** on UAT, and a connector node in a workflow
without `connectionId` fails validation.

---

## 6. Capability patterns — reading a connector without reading 145 schemas

**Names do most of the work.** Almost every resource is `{appName}_{verb}_{object}`. Guess the name, then confirm it in
`/resources`.

| Verb family | Typical names | Notes |
|---|---|---|
| Read one | `get_*`, `fetch_*`, `retrieve_*`, `describe_*` | |
| Read many | `list_*`, `search_*`, `find_*`, `select_*` | `search_` takes a query; `list_` takes filters + paging |
| Write | `create_*`, `add_*`, `insert_*`, `upload_*`, `post_*` | |
| Change | `update_*`, `edit_*`, `replace_*`, `modify_*`, `rename_*`, `move_*` | |
| Write-or-change | `upsert_*`, `merge_*` | prefer for idempotent sync |
| Remove | `delete_*`, `remove_*`, `archive_*`, `clear_*` | **never used** by platform-master (no deletes) |
| Bulk | `*_batch`, `bulk_*`, `*_bulk`, `*_multiple_*` | prefer over a per-row action in a loop |
| Event | `on_*` | always `resourceType: TRIGGER` |

Prefixes are not always the `appName` (`gsheet_on_new_row_polling` sits next to `gsheets_add_row`; `github_tools_*`
marks agent tools). Match on `name` from the API.

**Three resource types.** `ACTION` → a workflow node, an agent tool, an app data source. `TRIGGER` → the START node
only. `AGENT_TOOL` → a ready-made agent tool. It is rare (on UAT only `github` shipped any:
`github_tools_get_file_modified_details`, `github_tools_list_collaborators`). When one fits, prefer it to wrapping an
ACTION in a workflow.

**Trigger families.**

| Shape | Mechanism | Latency |
|---|---|---|
| `*_polling` (`gmail_on_new_email_polling`) | the platform polls on a schedule | the poll interval; works everywhere |
| `*_webhook` / `*_realtime` (`amazon_s3_on_new_file_realtime`) | the source pushes | near-instant; the source must be configured to call UnifyApps |
| plain `on_*` (`github_on_new_or_updated_pr`, `slack_on_new_message`) | connector-managed subscription | usually the one to use |

SQL connectors (`oracledb`, `postgres`, `snowflake`) share a CDC set: `on_new_event`, `on_update_event`,
`on_delete_event`, `on_new_or_update_event`, `on_event`, `on_scheduled_query_search`. Platform triggers:
`webhooks_default`, `schedule_default`, `callables_from_api`, `callables_from_automation`, `callables_from_interface`;
record triggers on Data Objects (`storage_by_unifyapps_on_any_change`, which needs the object's webhooks on). HubSpot
has no "record updated" trigger: poll `hs_lastmodifieddate` above a watermark.

**Single vs batch.** Most data connectors ship both (`oracledb_upsert_row` / `oracledb_upsert_rows_batch`,
`gsheets_add_row` / `gsheets_add_multiple_row`, `storage_by_unifyapps_create_record` /
`storage_by_unifyapps_bulk_create_records`). Inside a loop, a per-row action costs one step execution per row. Build the
array and call the batch action once. SQL connectors also pair `select_rows_in_batch` (structured filter),
`select_rows_using_custom_sql` (raw SQL) and `run_long_query_using_custom_sql` (async, for long queries).

**Superseded actions.** `gsheets_add_row` and `gsheets_add_row_v2` both exist. Prefer the highest `_vN`.

**Custom actions on built-in connectors.** A resource named `{defId}:{actionId}` (e.g. `slack:<24-hex>`) was added in
this tenant with the Connectors SDK. It works like any action but exists only on this tenant. Read it with
`GET /api/connector-builder/definition/{defId}` before assuming what it does.

**Nodes that need no connection** (`needsAuthentication: false`; full list in `platform-nodes.tsv`). Use these before
reaching for an HTTP call or a connector:

| Node | Use |
|---|---|
| `code_by_unifyapps` | Groovy (preferred), Python, JavaScript, Java, C#, Playwright |
| `custom_http_endpoint` | ad-hoc HTTP: REST, GraphQL, SOAP, multipart, streaming |
| `callables` | call another automation; return a response to a caller |
| `storage_by_unifyapps` | the tenant's own Data Objects: records, counts, schema |
| `utility_by_unifyapps` | SQL over a list, sort, JSON parse/stringify, dates, UUIDs |
| `mdm_by_unifyapps` / `unified_entity_by_unifyapps` / `ecg_by_unifyapps` | Ontology and Context Graph (`context-graph.md`) |
| `files_by_unifyapps`, `pdf_by_unifyapps`, `csv_by_unifyapps`, `excel_by_unifyapps`, `ppt_by_unifyapps`, `parquet_by_unifyapps` | file handling |
| `conv_ai_by_unifyapps` | call an LLM, OCR / document extraction, embeddings |
| `ai_agents_by_unifyapps` | invoke a platform agent from a workflow |
| `decision_table_by_unifyapps`, `template_by_unifyapps` | rule tables, text templates |
| `variable_by_unifyapps`, `if_else`, `loop`, `branch`, `delay`, `scope`, `stop` | state and control flow |
| `pii_by_unifyapps`, `encryption_tools_by_unifyapps`, `pgp_by_unifyapps` | redaction, encryption, signing |
| `on_prem_command_by_unifyapps`, `on_prem_files_by_unifyapps`, `on_prem_browser_by_unifyapps` | on-prem agent execution |

**Near-duplicates — pick deliberately.**

| Product | Options | Choose |
|---|---|---|
| Salesforce | `salesforce`, `salesforce_soap`, `salesforce_cpq`, `salesforce_marketing_cloud`, `salesforce_communications_cloud` | `salesforce` (REST) unless a SOAP-only or product-specific surface is needed |
| NetSuite | `netsuite` (146), `netsuite_soap` (13) | `netsuite` |
| Workday | `workday` (170), `workday_soap` | `workday` |
| SharePoint | `microsoft_sharepoint` (62), `microsoft_sharepoint_graph` (68) | Graph for modern tenants |
| Databricks | `databricks` (3, JDBC-style), `databricks_rest` (105) | `databricks_rest` beyond plain SQL |
| SAP | `sap_odata`, `sap_rfc`, `sap_hana`, `sap_successfactors`, `sap_concur`, `sap_ariba`, `sap_business_one`, … | by SAP product and protocol |
| Oracle | `oracledb` (the database) vs `oracle_fusion`, `oracle_fusion_cloud`, `oracle_ebusiness_suite`, `oracle_jde`, `oracle_siebel`, `oracle_epm` (application APIs) | by what is being reached |
| HTTP | `custom_http_endpoint` vs `custom_http_application` | endpoint = ad-hoc, no connection; application = saved authenticated base URL. Picking the wrong one is the most common HTTP mistake |
| Google | `google_workspace` (admin-wide) vs `gmail` / `gdrive` / `gsheets` / `gcalendar` / `gdocs` / `gslides` | the specific one for user data |

When in doubt, compare resource counts. The richer surface is nearly always the maintained one.

**Google scopes.** Gmail and Calendar expose a `scopes` multi-select at connection time. Drive has no scope field and
requests full `drive`. An enforced read-only Google connection needs a custom OAuth connector with fixed
`*.readonly` scopes.

**Connector specifics that bite** ✅:

- **HubSpot:** search operator `CONTAINS` is rejected; use `CONTAINS_TOKEN`. Always request `hs_object_id`. There is
  no list-properties action, and null-valued properties are dropped from results (absence ≠ nonexistence).
  `hubspot_get_deal` supports `propertiesWithHistory`. `closedate` carries a time of day. Stage labels can carry
  trailing spaces, and stage ids are recycled across pipelines: read the stage label and closed flag per pipeline.
- **Slack:** a bot token reads only channels the bot has joined (`token_type: "user_token"` reads what the user
  sees). `slack_list_conversation_history` returns top-level messages only (replies need
  `slack_list_conversations_replies`). `slack_get_user_info_by_id` takes `user`; `slack_get_conversation` takes
  `channelId`; history takes `channel`. Key on channel ids, not names.
- **SAP OData:** a connection's service list can be read with
  `POST /api/lookup?ByQuery=CONNECTOR_OBJECT_NAME` `{lookupType:"CONNECTOR_OBJECT_NAME", type:"ByQuery", options:{connectionId, source_resource_name:"sap_odata_list_services"}}`.
  An empty list is not proof that there are no services (stale credentials, or a v4 connection).
- **HTTP node:** `followRedirects` is an enum (`NEVER` | `ALWAYS` | `NORMAL`), not a boolean. A plain `body` input
  mapped from a Groovy step is sent as JSON. A single `url` input fails "Base URL must start with http(s)". Use
  `baseUrl` + `path`.

**The same catalogue from other surfaces.** The same `appName` drives app data sources (`e_data_source` with
`context.{appName, resourceName, connectionId}`), agent tools (`e_action_ai_agent`), and context-graph sources
(`GET /api/context-graph/sources/applications/{appName}/objects`: the objects a connector exposes for ingestion, its
*data model* rather than its verbs — `context-graph.md`).

---

## 7. Checklist for the plan review

When the Zen plan relies on a connector:

1. The `appName` exists in `connectors-index.tsv` (or as a custom connector on Orbit UAT). The plan names the right
   one of any near-duplicates.
2. The actions it needs exist in `/resources` (read actions for a read-only POC). It uses batch actions where it loops.
3. If the POC simulates the system (the default under the POC data policy), the simulating Data Object uses the
   **same field names** the connector would return, so switching to the real connector later changes only the reading
   node.
4. If a real connection is needed, it exists on Orbit UAT (`active`, owned by the person), or the plan says the
   person creates it in the Connections Manager. No step creates an OAuth connection over the API.
5. No personal connector is bound to a fixed connection in an agent tool.
6. No `*_delete_*` / `*_remove_*` action anywhere.
