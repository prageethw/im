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
II MS uses the lightweight internal KP for local semantic resolution, mappings, policy hints, and service-specific interpretation. II MS also uses external `t7-knowledge-plane` for network-related topology/resource context and broader network intelligence. Neither is exposed as external `Intent` or `IntentSpecification`.

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

## Baseline update — ID MS specification placeholder clarity:

Date: 2026-05-05T01:21:44.269813+00:00

### Updated file:
- `id_ms_specification.md`

### Baseline:
When request/response examples intentionally shorten large sections such as `specCharacteristic` or `expressionSpecification`, do not show empty arrays/objects unless the field is genuinely empty.

### Rule:
Use explicit explanatory placeholders such as:
- `"specCharacteristic": ["...similar payload to spec creation..."]`
- `"expressionSpecification": ...similar payload to spec creation...`

This makes clear that the content is abbreviated to save space, not missing from the real payload.

## Baseline update — IC MS design brief and IntentValidatedEvent production rule:

Date: 2026-05-05T02:22:05.009928+00:00

### New stable file:
- `ic_ms_design_brief.md`

### Baseline:
Created the initial IC MS design brief covering service identity, ownership, API surface, lifecycle/status projection, internal/external events, IntentReport responsibility, TMF/platform extension positioning, and ownership boundaries.

### IntentValidatedEvent rule:
IC MS does not emit `IntentValidatedEvent` as a point-to-point command for a specific consumer. IC MS emits it as an internal platform state/progress event meaning: the runtime Intent has passed IC MS syntactic validation and has been admitted into the intent lifecycle.

### Consumer positioning:
II MS is the current primary consumer because it performs semantic validation and resolution, but the event is not defined only for II MS. Other authorised internal consumers may consume it where useful.

### Boundary:
IC MS owns external `Intent` and `IntentReport` resources, syntactic validation against active `IntentSpecification`, and external lifecycle/status projection. IC MS does not own semantic validation, policy validation, optimisation, network apply, runtime assurance, telemetry ingestion, or callback mediation.

## Baseline update — IC MS lifecycle/status and versioning:

Date: 2026-05-05T02:29:41.944505+00:00

### Updated file:
- `ic_ms_design_brief.md`

### Lifecycle/status ownership:
IC MS owns the external lifecycle/status projection, not the runtime truth. Runtime truth comes from IC MS syntactic admission, II MS semantic/policy rejection outcomes, IA MS assurance outcomes, and accepted termination requests.

### Lifecycle values:
- `Acknowledged`
- `InProgress`
- `Active`
- `Degraded`
- `Paused`
- `Rejected`
- `Failed`
- `Terminated`

### Delete/terminate rule:
IC MS does not physically delete runtime `Intent` records by default. `DELETE /intentManagement/v5/intent/<built-in function id>` or equivalent terminate flow is treated as a termination request and transitions the retained `Intent` projection to `Terminated`.

### Versioning:
Each meaningful runtime `Intent` update creates a new Intent version. Each version has its own lifecycle/status. `effectiveVersion` tracks the version currently confirmed active in the network/service. Once a version becomes `Active`, it becomes `effectiveVersion` and remains so until another version is confirmed `Active`.

### Key rule:
IC MS must not invent runtime lifecycle truth. It projects external lifecycle/status from syntactic admission, II MS rejection outcomes, IA MS assurance outcomes, and accepted termination requests.

## Baseline update — IC MS activeVersion and version lifecycle refinement:

Date: 2026-05-05T04:43:42.158147+00:00

### Updated file:
- `ic_ms_design_brief.md`

### Baseline:
Use `activeVersion`, not `effectiveVersion` or `currentVersion`, for the Intent version currently confirmed active/effective in the network/service.

### Version lifecycle:
Individual Intent versions may use: `Acknowledged`, `InProgress`, `Active`, `Standby`, `Degraded`, `Paused`, `Rejected`, `Failed`, `Terminated`, and `Retired`.

### Standby:
When a newer Intent version becomes `Active`, IC MS moves `activeVersion` to the newer version and transitions the previously active version to `Standby`. `Standby` means the version is no longer currently active/effective, but is retained as a valid rollback or future reactivation candidate.

### Retired:
`Retired` is terminal and means the version is permanently removed from future active-candidate use. Once a version is `Retired`, its lifecycle state cannot change again.

### Termination:
IC MS does not physically delete runtime `Intent` records by default. Termination transitions the retained Intent projection to `Terminated` for audit, reporting, lifecycle history, and traceability.

### Examples:
The IC MS design brief now includes lifecycle/versioning tables and JSON examples for initial activation, update to v2, rollback to v1, retiring v2, and termination.

## Baseline update — GET caching wording cleanup across ID and IC:

Date: 2026-05-05T07:59:37.925379+00:00

### Checked files:
- `ic_ms_design_brief.md`
- `id_ms_design_brief.md`
- `id_ms_specification.md`
- `contextdump.md`

### Current wording rule:
Use only positive caching wording:
- GET responses may use bounded private caching.
- Clients may request a fresh GET using `Cache-Control: no-cache`.
- ETag is used for unsafe-operation concurrency through `If-Match`.
- No caching strategy is baselined for non-GET operations.

Avoid listing mechanisms that are not part of the baseline, because that creates reader confusion.

## Baseline update — IC MS caching, ETag, and dependency-specific CB:

Date: 2026-05-05T09:36:05.981308+00:00

### Updated file:
- `ic_ms_design_brief.md`

### Caching baseline:
IC MS caching applies only to GET responses. Clients either use cached GET responses within TTL or request a fresh copy using `Cache-Control: no-cache`. No caching strategy is baselined for non-GET operations.

### ETag baseline:
ETag is used only for unsafe-operation concurrency through `If-Match` on `PUT`, `PATCH`, and `DELETE`.

### ID MS dependency:
For `POST`, `PUT`, and runtime-content-changing `PATCH`, IC MS must confirm the exact referenced active `IntentSpecification.id` from ID MS or a valid fresh cached active specification. If it cannot confirm the active specification, IC MS fails closed and does not admit the runtime Intent or runtime version.

### Dependency-specific CB:
DB failure is hard fail-fast and returns `503 Service Unavailable`. Cache failure is graceful/silent. Kafka/event-broker failure is handled through transactional outbox. External webhook callback failure is asynchronous and does not affect the original API response.

## Baseline update — IC MS deployment and persistence strategy:

Date: 2026-05-05T09:47:24.292709+00:00

### Updated file:
- `ic_ms_design_brief.md`

### Baseline:
IC MS is a stateful MS, backed by a managed PostgreSQL-compatible RDBMS. IC MS application instances can still scale independently because durable state is externalised to the database rather than held in local memory.

### Source of truth:
The IC MS database is the source of truth for retained `Intent` projections, internal `IntentVersion` history, `IntentReport` projections, subscriptions, inbox/outbox records, ETag values, and lifecycle/status projection state.

### Persistence:
Recommended stores include `intent`, `intent_version`, `intent_report`, `event_subscription`, `inbox_event`, `outbox_event`, and optional audit table/audit log.

### Eventing:
IC MS uses transactional outbox for internal/external event publication and inbox/idempotency handling for consumed events such as `IntentRejectedEvent` and `IntentAssuranceEvent`.

### Scaling:
IC MS remains independently scalable at the application-instance level because durable state is not held in local memory.

## Baseline update — IC MS security and access-control boundary:

Date: 2026-05-05T09:50:32.634232+00:00

### Updated file:
- `ic_ms_design_brief.md`

### Authentication:
IC MS sits behind NGW. NGW performs system-to-system authentication using mTLS and OAuth2 token validation.

### Authorisation boundary:
Business/user-level authorisation is owned by OEX, not IC MS. IC MS does not implement business/user-level operation authorisation for runtime Intent or IntentReport operations.

### IC MS responsibility:
IC MS trusts authenticated platform/system callers and enforces technical resource integrity, syntactic validation, active-spec admission, lifecycle/status projection rules, version state-machine rules, ETag/If-Match concurrency, and delete-as-termination behaviour.

### Audit:
IC MS audits technical/governance-changing operations and technical integrity decisions. Business/user authorisation audit belongs to OEX where that decision is made.

## Baseline update — IC MS observability and audit:

Date: 2026-05-05T09:54:36.969843+00:00

### Updated file:
- `ic_ms_design_brief.md`

### Baseline:
IC MS must log and propagate correlation context, emit structured operational telemetry, participate in distributed tracing, and audit technical/governance-changing operations.

### Observability:
IC MS emits structured logs, metrics, traces, dependency health signals, active-spec lookup/cache fallback metrics, inbox/outbox metrics, event-delivery metrics, webhook delivery metrics, lifecycle projection metrics, version-state metrics, and IntentReport projection metrics.

### Audit:
Business/user-level authorisation audit remains with OEX. IC MS audit focuses on runtime Intent admission, version creation, lifecycle/status projection, active/projected-version changes, termination, IntentReport projection, technical validation failures, ETag/If-Match integrity decisions, dependency failure signals, and consumed-event idempotency decisions.

### Sensitive data:
IC MS must not log OAuth2 tokens, certificate private material, secrets, credentials, full internal connection strings, sensitive platform headers, or raw internal dependency details in external responses.

## Baseline update — IC MS specification document:

Date: 2026-05-05T10:08:45.517155+00:00

### New stable file:
- `ic_ms_specification.md`

### Baseline:
Created the IC MS specification document containing API endpoints, request/response examples, common errors, runtime Intent create/list/retrieve/update/patch/terminate examples, IntentReport examples, hub subscription examples, external `Intent*Event` examples, external `IntentReport*Event` examples, and internal `IntentValidatedEvent` publication note.

### Key alignment:
- Runtime create/update supports only concrete `intentSpecification.id`.
- `GET /intent/{id}` returns current projected Intent state, not full internal version aggregate.
- `DELETE /intent/{id}` is termination, not physical deletion.
- `PUT /intent/{id}` is platform extension for deterministic full replacement.
- `PATCH /intent/{id}` is supported for TMF compatibility.
- ETag is used for unsafe-operation concurrency through `If-Match`.
- GET cache refresh uses `Cache-Control: no-cache`.
- Event examples are curated external projection events.

## Baseline update — IC MS specification internal event coverage:

Date: 2026-05-05T10:12:27.379012+00:00

### Updated file:
- `ic_ms_specification.md`

### Baseline:
Confirmed and expanded IC MS specification coverage so the specification includes external REST interfaces, request/response examples, external events, and internal event interfaces.

### Internal event coverage added:
- `IntentValidatedEvent` produced by IC MS
- `IntentRejectedEvent` consumed by IC MS
- `IntentAssuranceEvent` consumed by IC MS

### Coverage matrix:
The IC MS specification now includes an interface coverage matrix covering external Intent APIs, IntentReport APIs, hub subscription APIs, external Intent events, external IntentReport events, internal produced/consumed events, common errors, caching/ETag conventions, and termination behaviour.

## Baseline update — hub GET Cache-Control headers:

Date: 2026-05-05T11:23:26.807866+00:00

### Checked files:
- `id_ms_specification.md`
- `ic_ms_specification.md`

### Result:
Hub subscription GET response examples now include `Cache-Control: private, max-age=300`.

### Rule:
All successful GET responses include `Cache-Control`, including resource GETs, list GETs, report GETs, and hub subscription GETs. Non-GET operations do not have a caching strategy baseline.

## Baseline update — GET Cache-Control quick pass:

Date: 2026-05-05T11:25:44.215101+00:00

### Checked files:
- `id_ms_specification.md`
- `ic_ms_specification.md`
- `id_ms_design_brief.md`
- `ic_ms_design_brief.md`

### Result:
All documented successful GET response examples in the ID MS and IC MS specification documents include `Cache-Control`.

### Cache bypass documentation:
The cache bypass / fresh-read rule is now documented explicitly: clients may send `Cache-Control: no-cache` on any GET request to request a fresh response. This applies to resource GETs, list GETs, report GETs, and hub subscription GETs.

### Current rule:
All successful GET responses include `Cache-Control`. Non-GET operations do not have a caching strategy baseline. ETag is used for unsafe-operation concurrency through `If-Match`.

## Baseline update — stable terminology and JSON repair:

Date: 2026-05-06T01:11:47.933166+00:00

### Updated files:
- `intent_internal_events_specification.md`
- stable baseline files containing old terminology where applicable

### Repair:
Fixed terminology alignment and JSON validity in the internal events specification.

### Confirmed:
- All JSON code blocks in `intent_internal_events_specification.md` validate successfully.
- Current internal event examples use `location.locationId`.
- `IntentResolvedEvent` uses `context`, no generic request block, no optimiser input-selection block, and no successful semantic/policy evaluation block.
- `IntentValidatedEvent` has a concrete expression sample and no validation object.
- Resource references use named `references` objects with `id` and `href`.
- Knowledge Plane naming uses `t7-knowledge-plane`.

## Full rewrite — internal events spec repaired and normalised:

Date: 2026-05-06T11:56:11.910239+00:00

### Updated file:
- `intent_internal_events_specification.md`

### Reason:
The previous file had stale examples and invalid/non-object JSON snippets in the event specification. The file has been rewritten to the current baseline.

### Confirmed:
- All JSON code blocks validate.
- Event examples use `serviceContext` outside KP.
- No event JSON example uses `locationBasedService`.
- `IntentValidatedEvent` is admission-focused and uses runtime `expression`.
- `IntentResolvedEvent` uses `serviceContext`, `targets`, `context`, and `candidates`.
- `IntentOptimisedEvent` uses selected `resources`, `optimisationRun`, `targetEvaluations`, and `contextEvaluations`.
- `IntentNetworkReadyEvent` uses `serviceConfiguration`.
- `IntentAssuranceEvent` uses `resources` and `observations[].metrics`.

## Baseline update — IntentRejectedEvent simplified rejection payload:

Date: 2026-05-06T12:15:43.379760+00:00

### Updated file:
- `intent_internal_events_specification.md`

### Baseline:
For simple semantic/capability rejection, `IntentRejectedEvent` carries `lifecycleStatus`, `reasonCode`, `statusReason`, `serviceContext`, and references.

### Applied:
- Removed `capabilityStatus` from `serviceContext`.
- Replaced `SERVICE_CAPABILITY_UNKNOWN` with `SERVICE_NOT_AVAILABLE`.
- Removed the simple `evaluations` block.
- Kept `knowledgePlane` reference because the rejection is based on semantic/KP lookup.

## Baseline update — common metrics container:

Date: 2026-05-06T12:34:03.490482+00:00

### Updated files:
- `intent_internal_events_specification.md`
- `kp_master_config.md`

### Baseline:
Use `metrics` as the common resource performance container.

### Rules:
- Use `metrics.benchmark` for KP/design-time expected values.
- Use `metrics.telemetry` for observed/runtime values.
- Avoid a separate resource-level `benchmarks` object in event resource entries.
- Evaluation entries may still use `benchmarkValue` or `observedValue` to identify which value is being compared.
- Location/service-level `benchmarks` in KP remain valid because they represent design-time service capability values, not per-resource performance samples.

### Applied:
- Converted event resource-entry `benchmarks` to `metrics.benchmark`.
- Converted KP resource `benchmarks` to `metrics.benchmark`.

## Baseline update — direct location/service fields applied across events:

Date: 2026-05-06T13:47:53.357187+00:00

### Updated file:
- `intent_internal_events_specification.md`

### Baseline:
Where applicable, internal events use direct `location`, `serviceType`, and `serviceClass` fields. Do not wrap them in `context`, `serviceContext`, or `locationBasedService`.

### Applied:
- Flattened `serviceContext` in `IntentRejectedEvent`, `IntentOptimisedEvent`, `IntentNetworkReadyEvent`, and `IntentAssuranceEvent`.
- Confirmed `IntentResolvedEvent` remains lean with direct fields and no generic `context` wrapper.
- Confirmed no event body uses `serviceContext` or a top-level generic `context` wrapper.

## Correction — IC specification JSON placeholders repaired:

Date: 2026-05-07T02:53:16.079859+00:00

### Updated file:
- `ic_ms_specification.md`

### Applied:
- Replaced invalid placeholder JSON snippets with complete valid JSON examples.
- Replaced abbreviated Intent response payloads with complete payloads using `expression.targets`, `expression.constraints`, and `expression.preferences`.
- Confirmed IC/ID spec and design Markdown JSON blocks validate.

---

## Baseline update — event alignment and external projection cleanup:

Applied event/projection alignment across IA MS, IC MS, ID MS, and internal event documentation.

Per-file active changes:

- `ia_ms_design_brief.md`: aligned `IntentAssuranceEvent` with the internal event specification. Removed the old default `assuranceOutcome`, `runtimeState`, and `candidates` pattern. IA MS now emits lifecycle-driving assurance truth using top-level `body.lifecycleStatus`, `body.statusReason`, `targets`, `resources`, and `observations`.
- `intent_internal_events_specification.md`: removed event-facing `provider` attributes from `IntentResolvedEvent.resources[]` and `IntentOptimisedEvent.resources[]`. `provider` remains KP/resource-inventory metadata only.
- `ic_ms_design_brief.md`: clarified `IntentReport` projection rules. IntentReport is based on IA truth but is not raw telemetry and not the raw `IntentAssuranceEvent` body. It uses TMF `expression.expressionValue` for curated facts and keeps `targetSummary` fact-only.
- `ic_ms_specification.md`: replaced old IntentReport examples that used direct fields and `evaluationSummary.result` with TMF-wrapped `IntentReport.expression.expressionValue`, containing fact-only `targetSummary` and curated `observationSummary`.
- `id_ms_specification.md`: corrected `specCharacteristic` to the high-level bucket catalogue (`targets`, `constraints`, `preferences`) with example/default `characteristicValueSpecification` only. Detailed validation remains in the external expression-value schema referenced through `targetEntitySchema.@schemaLocation`.

Active rule: internal events carry native JSON facts; external TMF resources carry TMF expression wrappers; external reports contain curated projection facts only and do not expose raw telemetry, raw callback payloads, raw optimiser details, raw KP data, or internal event bodies.
