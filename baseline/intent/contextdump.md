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
