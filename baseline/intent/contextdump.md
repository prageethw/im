# Context Dump

## Baseline update — KP Master Config and context dump rule:

Date: 2026-05-04T15:06:45.814425Z

### Files:
- `kp_master_config.md`
- `contextdump.md`

### Baseline:
- The II MS lightweight Master Knowledge Config is now baselined in `kp_master_config.md`.
- `applicableResourceIds` is optional.
- Include `applicableResourceIds` only when the location has known applicable resources in the lightweight II MS KP.
- Omit `applicableResourceIds` when none are currently defined.
- Do not use empty arrays such as `"applicableResourceIds": []` by default.
- Going forward, append new baseline changes to the end of `contextdump.md` as the main context file.

### Knowledge-source rule:
II MS uses the lightweight internal KP for local semantic resolution, mappings, policy hints, and service-specific interpretation. II MS also uses external `t7.knowledge plane` for network-related topology/resource context and broader network intelligence. Neither is exposed as external `Intent` or `IntentSpecification`.

## Baseline update — ID MS Design Brief:

Date: 2026-05-04T15:29:35.255523+00:00

### File:
- `id_ms_design_brief.md`

### Baseline:
ID MS / `intent-definition-ms` owns the design-time `IntentSpecification` API contract and hub subscription APIs under `/intentManagement/v5`.

### API coverage:
- `POST /intentSpecification`
- `GET /intentSpecification`
- `GET /intentSpecification/{id}`
- `PUT /intentSpecification/{id}`
- `PATCH /intentSpecification/{id}`
- `DELETE /intentSpecification/{id}`
- `POST /intentSpecification/hub`
- `GET /intentSpecification/hub/{id}`
- `DELETE /intentSpecification/hub/{id}`

### Lifecycle baseline:
`IntentSpecification` lifecycle values are `DRAFT`, `ACTIVE`, and `RETIRED`. There is no `DELETED` lifecycle state. Delete is an operation/outcome, not a lifecycle status.

### Governance baseline:
- `DRAFT` specs can be edited.
- `ACTIVE` specs are immutable.
- `RETIRED` specs are immutable.
- Meaningful change after activation requires a new versioned `IntentSpecification`.
- `PUT` is preferred for deterministic full updates.
- `PATCH` is supported for compatibility but discouraged.

### Boundary:
ID MS validates syntax/resource shape and enforces specification lifecycle/version governance. It does not validate runtime semantic feasibility, policy fulfilment, network topology, optimisation, assurance, telemetry, or callbacks.

## Baseline update — ID MS lifecycle and versioning rules:

Date: 2026-05-04T15:35:23.666295+00:00

### Updated file:
- `id_ms_design_brief.md`

### Baseline:
The ID MS design brief now includes detailed lifecycle and versioning rules for `IntentSpecification`.

### Lifecycle:
Allowed `IntentSpecification.lifecycleStatus` values are `DRAFT`, `ACTIVE`, and `RETIRED`. `DELETED` is not a lifecycle status.

### Versioning:
Each meaningful change after activation requires a new versioned `IntentSpecification`. New versions start as `DRAFT`. Only one version in the same specification family should be `ACTIVE` for new runtime intent creation. Activating a new version retires the previous active version.

### Runtime compatibility:
IC MS validates new runtime `Intent` creation only against `ACTIVE` specifications. Existing intents referencing retired specifications may continue temporarily where safe, but should be migrated or recreated through controlled flow.

## Baseline update — ID MS caching and circuit-breaker strategy:

Date: 2026-05-04T22:32:03.043829+00:00

### Updated file:
- `id_ms_design_brief_v2.md`

### Baseline:
IC MS may use a cached `ACTIVE` `IntentSpecification` within a configured freshness window for runtime `Intent` syntactic validation.

### Fail-closed rule:
If ID MS is unavailable and IC MS has no valid fresh cached `ACTIVE` specification, IC MS must fail closed for new runtime intent creation with `503 Service Unavailable`.

### Active-version promotion cache invalidation:
When a new specification version is promoted to `ACTIVE`, ID MS must invalidate old active-specification caches and refresh consumers with the new active copy. Activation/write responses use `Cache-Control: no-store`. ID MS emits status-change events for the newly active version and the previously active version moving to `RETIRED`. IC MS treats those events as cache invalidation signals, evicts the old active version, and fetches the new active copy.

## Baseline file handling rule:

Date: 2026-05-04T22:35:35.320776+00:00

### Rule:
Going forward, keep the main baseline dump file as `contextdump.md`.

Do not create numbered/versioned dump filenames such as `contextdump_v2.md` or `new-context-working-vXX.md` for normal baseline updates.

Append each new baseline update to the end of `contextdump.md`.

### Related rule:
For design briefs, keep the stable file name unless the user explicitly asks for a versioned copy.

## Baseline file handling rule — stable design files:

Date: 2026-05-04T22:36:58.456157+00:00

### Rule:
Going forward, design files must keep stable filenames and be fully overwritten with the corrected full version when revised.

### Applies to:
- `id_ms_design_brief.md`
- future MS design brief files
- other stable design/specification files unless the user explicitly requests a versioned copy

### Do not:
- create normal update files such as `_v2`, `_v3`, or numbered copies for design briefs
- leave the corrected version only in a temporary/versioned file

### Main context dump:
Keep one stable `contextdump.md` file and append every new baseline update to the end of that file.

## Baseline update — ID MS dependency-specific circuit-breaker refinement:

Date: 2026-05-04T22:50:08.727440+00:00

### Updated file:
- `id_ms_design_brief.md`

### Baseline:
ID MS has multiple circuit-breaker trigger points, and each dependency path has a different failure behaviour.

### Dependency-specific CB behaviour:
- DB failure is a hard fail-fast failure. ID MS returns `503 Service Unavailable` and the consumer retries later.
- Cache failure is graceful/silent. ID MS bypasses cache or ignores failed cache writes where safe, continues through DB/source-of-truth, and emits telemetry.
- Kafka/event-broker failure is graceful/silent when transactional outbox is used. API success depends on DB + outbox commit, not immediate broker availability. The outbox relay retries Kafka later.
- External callback webhook failure is asynchronous fail-fast per attempt. The delivery attempt fails fast, is retried later through bounded retry/backoff, and does not affect the original resource API response.

### Boundary:
Only DB/source-of-truth unavailability is catastrophic for synchronous ID MS resource operations. Cache, Kafka, and callback webhook failures are operational failures handled through cache bypass, outbox, retry, metrics, alerts, and operational follow-up.

## Baseline update — ID MS caching, ETag, and dependency-specific CB:

Date: 2026-05-04T23:35:42.796639+00:00

### Updated file:
- `id_ms_design_brief.md`

### Caching baseline:
ID MS caching applies only to GET responses. GET responses may use bounded private caching, with longer TTL for single-resource GETs and shorter TTL for list GETs. Clients either use the cached response within TTL or request a fresh copy using `Cache-Control: no-cache`.

### ETag baseline:
ETag is not used for GET revalidation. `If-None-Match` and `304 Not Modified` are not baselined. ETag is used only for unsafe operation concurrency through `If-Match`.

### Non-GET cache baseline:
No `Cache-Control: no-store` strategy is baselined for non-GET operations.

### Active-version promotion:
On active-version promotion, ID MS refreshes its own active-specification cache using a no-cache/internal refresh path so the newly active version becomes the cached active copy and the previous active version is no longer returned as active.

### Dependency-specific CB baseline:
DB failure is hard fail-fast and returns `503 Service Unavailable`. Cache failure is handled silently and gracefully by bypassing cache or ignoring cache writes where safe. Kafka/event-broker failure is handled through transactional outbox. External webhook callback failure is handled asynchronously and does not affect the original resource API response.

## Baseline update — ID MS deployment and persistence strategy:

Date: 2026-05-04T23:43:41.415139+00:00

### Updated file:
- `id_ms_design_brief.md`

### Baseline:
ID MS application instances are stateless and horizontally scalable. The source of truth for `IntentSpecification`, hub subscriptions, lifecycle/version state, and outbox records is a managed PostgreSQL-compatible RDBMS.

### Persistence:
Use relational columns for governance fields such as `id`, `family_id`, `name`, `version`, `lifecycle_status`, `etag`, and timestamps. Use JSONB for document-shaped resource body content such as `specCharacteristic`, `expressionSpecification`, `_links`, and event/resource snapshots.

### HA / DR:
ID MS should support multiple replicas, rolling deployments, health checks, and same-region multi-AZ database deployment where available. The selected database pattern must support future cross-region active-passive DR. Active-active multi-region writes are not baselined initially.

### Health:
Readiness depends on DB/source-of-truth availability. Cache failure should not make ID MS unavailable. Kafka/event-broker failure should be handled through transactional outbox and surfaced through metrics/alerts rather than blocking the API when DB/outbox commit is healthy.

## Baseline update — ID MS security and access-control:

Date: 2026-05-04T23:56:47.973649+00:00

### Updated file:
- `id_ms_design_brief.md`

### Authentication:
ID MS sits behind NGW. NGW performs system-to-system authentication using mTLS and OAuth2 token validation.

### Authorisation:
Authorisation is based on the authenticated mTLS client certificate identity and validated OAuth2 token identity. No OAuth2 scopes are assumed. No context-aware authorisation is baselined at NGW.

### ID MS responsibility:
ID MS performs operation-level authorisation using the authenticated caller identity for `IntentSpecification` reads, writes, activation, retirement, deletion, and hub subscription management.

### Audit:
ID MS must audit create, draft update, activation, retirement, draft deletion, hub subscription create/delete, and failed authorisation attempts for privileged operations.

## Baseline update — ID MS security/access-control boundary refinement:

Date: 2026-05-05T00:03:09.411553+00:00

### Updated file:
- `id_ms_design_brief.md`

### Authentication:
ID MS sits behind NGW. NGW performs system-to-system authentication using mTLS and OAuth2 token validation.

### Authorisation boundary:
Business/user-level authorisation is owned by the OEX layer, not ID MS. ID MS does not implement business/user-level operation authorisation for `IntentSpecification` reads, writes, activation, retirement, deletion, or hub subscription management.

### ID MS responsibility:
ID MS trusts authenticated platform/system callers and enforces technical resource integrity, lifecycle/version governance, request validation, ETag/If-Match concurrency rules, and state-machine constraints.

### Audit:
ID MS audits technical/governance-changing operations and technical integrity validation failures where required. Business/user authorisation audit belongs to OEX where that decision is made.

## Baseline update — ID MS observability and audit:

Date: 2026-05-05T00:05:59.882973+00:00

### Updated file:
- `id_ms_design_brief.md`

### Baseline:
ID MS must log and propagate correlation context, emit structured operational telemetry, participate in distributed tracing, and audit technical/governance-changing operations.

### Observability:
ID MS emits structured logs, metrics, traces, dependency health signals, cache metrics, outbox/event-delivery metrics, and webhook delivery metrics.

### Audit:
Business/user-level authorisation audit remains with OEX. ID MS audit focuses on specification creation, draft update/patch, activation, retirement, deletion, hub subscription changes, technical validation failures, ETag/If-Match integrity decisions, immutable-resource enforcement, and dependency failure signals.

### Sensitive data:
ID MS must not log OAuth2 tokens, certificate private material, secrets, credentials, full internal connection strings, sensitive platform headers, or raw internal dependency details in external responses.

## Baseline update — ID MS consistency sweep:

Date: 2026-05-05T00:08:01.489012+00:00

### Updated file:
- `id_ms_design_brief.md`

### Result:
ID MS design brief consistency sweep completed with result: **PASS WITH NOTES**.

### Confirmed:
- naming is consistent around ID MS / `intent-definition-ms` / `IntentSpecification`
- lifecycle uses `DRAFT`, `ACTIVE`, and `RETIRED`; no `DELETED` lifecycle state
- caching is GET-only
- ETag is not used for GET revalidation; `If-None-Match` and `304 Not Modified` are not baselined
- ETag is used for unsafe operation concurrency through `If-Match`
- DB/cache/Kafka/webhook dependency-specific CB behaviour is captured
- NGW handles mTLS and OAuth2 token validation; OEX owns business/user-level authorisation
- ID MS emits external `IntentSpecification*Event` events only
- persistence baseline uses managed PostgreSQL-compatible RDBMS with JSONB and outbox
- ID MS boundaries exclude semantic validation, policy validation, optimisation, assurance, telemetry, and callback ingestion

### Final position:
ID MS is complete for the current baseline unless later revised.

## Baseline update — ID MS no-store cleanup:

Date: 2026-05-05T00:12:35.705139+00:00

### Updated file:
- `id_ms_design_brief.md`

### Baseline cleanup:
All residual `Cache-Control: no-store` references were removed from the ID MS design brief.

### Current caching rule:
ID MS caching is baselined only for GET responses. No caching strategy is baselined for non-GET operations. ETag is not used for GET revalidation; ETag is used only for unsafe operation concurrency through `If-Match`.

### Consistency result:
ID MS consistency sweep now passes with no notes.

## Baseline update — ID MS specification document:

Date: 2026-05-05T00:55:43.244675+00:00

### New stable file:
- `id_ms_specification.md`

### Baseline:
Created the ID MS specification document containing API endpoints, request/response examples, error bodies, lifecycle/version behaviour, hub subscription operations, activation operation, and external `IntentSpecification*Event` examples.

### Coverage:
- Create/list/retrieve/update/patch/delete `IntentSpecification`
- Activate `IntentSpecification`
- Create/retrieve/delete hub subscription
- Common error bodies
- DB unavailable response
- External event family:
  - `IntentSpecificationCreateEvent`
  - `IntentSpecificationAttributeValueChangeEvent`
  - `IntentSpecificationStatusChangeEvent`
  - `IntentSpecificationDeleteEvent`

### Alignment:
The specification follows the ID MS design brief baseline: GET-only caching, ETag only for unsafe-operation concurrency, no `DELETED` lifecycle state, `DRAFT`/`ACTIVE`/`RETIRED` lifecycle, `priority` not `priority_level`, and `critical` not `clinical-critical`.

## Baseline update — ID MS TMF-aligned lifecycle activation:

Date: 2026-05-05T01:02:30.098178+00:00

### Updated files:
- `id_ms_design_brief.md`
- `id_ms_specification.md`

### Baseline:
ID MS and IC MS must remain fully TMF-compliant at the external API boundary.

### Correction:
Do not expose a custom lifecycle action endpoint such as `POST /intentManagement/v5/intentSpecification/{id}/activate`.

### Lifecycle activation approach:
Activation/retirement is represented as a resource update to `IntentSpecification.lifecycleStatus` using:

- `PUT /intentManagement/v5/intentSpecification/{id}`
- `PATCH /intentManagement/v5/intentSpecification/{id}`

### Update preference:
`PUT` is preferred for deterministic full replacement. `PATCH` is supported for TMF compatibility but is not encouraged for ordinary edits.

### Governance:
When lifecycleStatus is updated to `ACTIVE`, ID MS applies governance internally: target version becomes `ACTIVE`, previous active version in the same family becomes `RETIRED`, ID MS refreshes its own active-specification cache through an internal no-cache/refresh path, and ID MS emits `IntentSpecificationStatusChangeEvent` events for both lifecycle changes.

## Baseline update — TMF compliance and platform extensions for ID MS:

Date: 2026-05-05T01:19:32.207312+00:00

### Updated files:
- `id_ms_design_brief.md`
- `id_ms_specification.md`

### Baseline:
ID MS and IC MS remain TMF-aligned at the external contract level, but controlled platform extensions are acceptable when documented, non-breaking, and semantically compatible with TMF.

### Strict TMF baseline:
- `POST /intentManagement/v5/intentSpecification`
- `GET /intentManagement/v5/intentSpecification`
- `GET /intentManagement/v5/intentSpecification/{id}`
- `PATCH /intentManagement/v5/intentSpecification/{id}`
- `DELETE /intentManagement/v5/intentSpecification/{id}`
- `/hub` and `/hub/{id}` for strict TMF-style event subscriptions where required

### Accepted platform extensions:
- `PUT /intentManagement/v5/intentSpecification/{id}` for deterministic full replacement
- `/intentManagement/v5/intentSpecification/hub`
- `/intentManagement/v5/intentSpecification/hub/{id}`

### Update method rule:
`PATCH` is the strict TMF-compatible update operation. `PUT` is the accepted platform extension and preferred for deterministic full replacement where clients support it.

### Activation rule:
Activation/retirement is represented as a resource update to `IntentSpecification.lifecycleStatus`, not a custom `/activate` action endpoint.
