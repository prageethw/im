# Intent / Intent Management / Intent Enabler — Clean Context Dump

> Working baseline context file.
> This file replaces the previous reliance on `baseline/intent/contextdump.md`, which may be messy or stale.
> Going forward, this file should be amended whenever a new baseline decision is agreed.

## 1. Scope

This context is only for:

- Intent
- Intent Management
- Intent Enabler
- TMF921-facing Intent APIs and resources
- IntentSpecification / Intent lifecycle
- Intent Controller MS
- Intent Definition MS
- Intent Intelligence MS
- Intent Assurance MS
- Intent Callback MS
- Knowledge Plane configuration relevant to Intent

Do not bring Optimisation / OD / OC / OSB MS context into this thread unless explicitly requested.

## 2. Source-of-truth artifact set

The refreshed Intent baseline source folder is:

`https://github.com/prageethw/im/tree/main/baseline/intent`

Only Markdown files in that folder are baselined editable artifacts by default.

### Baselined Markdown files

- `ia_ms_design_brief.md`
- `ia_ms_specification.md`
- `ic_ms_design_brief.md`
- `ic_ms_specification.md`
- `icb_ms_design_brief.md`
- `icb_ms_specification.md`
- `id_ms_design_brief.md`
- `id_ms_specification.md`
- `ii_ms_design_brief.md`
- `ii_ms_specification.md`
- `intent_internal_events_specification.md`
- `kp_master_config.md`

### Special handling for context dump

- The existing GitHub `contextdump.md` is not treated as authoritative.
- A new clean context dump should be maintained from this point onward.
- New baseline decisions should be appended/amended into the clean context dump when the user says to baseline them.

### Excluded unless explicitly requested

- `.puml` files
- `.zip` files
- Any non-Markdown artifacts in the Intent folder

## 3. TMF/source reference files

Use these attached TMF files preferentially when validating TMF-facing API, resource, schema, and event shapes:

- `TMF921_Intent_Management_v5.0.0_specification.pdf`
- `TMF921_Intent_Management_v5.0.0_conformance.pdf`
- `TMF921_Intent_Management_v5.0.0.oas.yaml`
- `TR292_TMForum_Intent_Ontology_TIO_v3.6.0.pdf`

Use the uploaded architecture/reference books only as supporting design references where relevant.

## 4. Current high-level architectural baseline

### 4.1 Microservices

The Intent solution baseline includes:

- ID MS — Intent Definition MS
- IC MS — Intent Controller MS
- II MS — Intent Intelligence MS
- IA MS — Intent Assurance MS
- ICB MS — Intent Callback MS
- Knowledge Plane / KP configuration where relevant

### 4.2 Naming

- Use `intent-intelligence-ms`, not `intent-interpreter-ms`.
- Use `IntentCallbackEvent`, not `OrchestratorCallbackEvent` and not `IntentCallbackReceivedEvent`.
- `IntentDriftOccurredEvent` is retired from the active internal event baseline.

## 5. External TMF-facing baseline

### 5.1 ID MS / IntentSpecification

ID MS owns definition-time `IntentSpecification` lifecycle/governance.

ID MS owns:

- `/intentManagement/v5/intentSpecification`
- `/intentManagement/v5/intentSpecification/{id}`
- `/intentManagement/v5/intentSpecification/hub`
- `/intentManagement/v5/intentSpecification/hub/{id}`

ID MS does not own:

- Runtime `Intent`
- Runtime `IntentReport`
- Runtime assurance
- Runtime orchestration
- Callback ingestion
- Interpretation/resolution

For `IntentSpecification`:

- Use `@type: IntentSpecification`
- Use `@baseType: EntitySpecification`
- Use `specCharacteristic` as high-level catalogue/discovery metadata.
- Use `expressionSpecification` as the authoritative syntax/schema for request shape.
- Avoid duplicating nested object structure in `specCharacteristic`.
- Use `characteristicValueSpecification` only for defaults, examples, constrained allowed values, discovery, governance, or OEX/UI prefill guidance.

### 5.2 Runtime Intent expression shape

External runtime expression shape is:

`expression.expressionValue.context`

The top-level `context` contains only canonical semantic buckets:

- `targets`
- `constraints`
- `preferences`

Domain inputs such as `location`, `serviceType`, and `serviceClass` are modelled under `context.constraints`.

Internally, events use native JSON without the external TMF expression wrapper, for example:

- `body.expression.context.targets`
- `body.expression.context.constraints`
- `body.expression.context.preferences`

## 6. Canonical semantic buckets

Use these semantic meanings consistently end-to-end:

- `targets` — measurable SLA/outcome objectives, such as `maxLatencyMs`, `minAvailabilityPercent`, `maxJitterMs`, and `maxPacketLossPercent`.
- `constraints` — hard rules or required non-target inputs, such as `priority`, `redundancyRequired`, `timeWindow`, `location`, `serviceType`, and `serviceClass`.
- `preferences` — soft selection guidance, such as `preferredAccessTechnology`.

The same semantics must flow from:

`IntentSpecification -> Intent -> IntentValidatedEvent -> IntentResolvedEvent -> IntentOptimised/Network-ready flow -> IntentAssuranceEvent`

## 7. Internal event baseline

### 7.1 Event structure

Internal workflow events should use a common generic envelope but event-specific business bodies.

Shared envelope examples:

- CloudEvents headers
- `eventType`
- `eventVersion`
- `source`
- `eventTime`
- `correlationId`
- `references`

Do not force a fully generic business body across milestone-specific events.

### 7.2 Active internal events

Current active internal baseline includes milestone-specific events such as:

- `IntentValidatedEvent`
- `IntentResolvedEvent`
- `IntentNetworkReadyEvent`
- `IntentCallbackEvent`
- `IntentAssuranceEvent`

### 7.3 Retired event

`IntentDriftOccurredEvent` is retired.

Drift, degradation, failure, termination confirmation, and re-optimisation triggers are represented inside:

`IntentAssuranceEvent.assuranceOutcome`

Use fields such as:

- `assuranceStatus`
- `severity`
- `reason`
- `requiresReoptimisation`

## 8. IA MS baseline

IA MS owns runtime assurance interpretation and lifecycle/assurance meaning.

IA MS consumes `IntentCallbackEvent`, correlates intent, maps raw orchestrator state, updates assurance/projection state, and emits `IntentAssuranceEvent`.

IA MS owns:

- Correlation of callback intent context
- Mapping `orchestratorState` to assurance/lifecycle meaning
- Skip/reject decisions for unmapped or uncorrelatable callbacks
- Assurance outcome publication

IA MS does not rely on a separate `IntentDriftOccurredEvent`.

## 9. ICB MS baseline

ICB MS performs inbound callback ingestion and relay.

ICB MS:

- Accepts callbacks from external orchestrators
- Performs structural validation only
- Stores accepted callbacks in its outbox
- Publishes `IntentCallbackEvent` to Kafka
- Does not map or interpret `orchestratorState`
- Does not validate intent existence
- Does not derive orchestrator type
- Does not decide lifecycle impact

`IntentCallbackEvent` baseline:

- Emitted by `intent-callback-ms`
- Topic: `t7.intent.management.events.callbacks`
- Kafka key: `intentId`
- Consumer: `intent-assurance-ms`
- CloudEvents type: `au.com.mycsp.intent.callback.v1`

## 10. IC MS baseline

IC MS owns the runtime external TMF Intent resource and canonical runtime intent state.

IC MS owns external TMF-aligned events such as:

- `IntentStatusChangeEvent`
- `IntentDeleteEvent`
- `IntentAttributeValueChangeEvent`

IC MS projects external lifecycle/status from assurance and internal workflow outcomes.

IA MS provides operational lifecycle input; IC MS emits external TMF status events after updating the canonical Intent resource state.

## 11. II MS baseline

II MS owns interpretation/resolution after syntactic validation by IC MS.

Baseline flow:

- IC MS emits `IntentValidatedEvent`.
- II MS resolves the intent.
- II MS emits `IntentResolvedEvent` only when optimisation is required.
- If optimisation is not required, II MS emits `IntentNetworkReadyEvent` directly.
- II MS does not emit `IntentAppliedEvent`.

`IntentResolvedEvent` may include optional `applicablePathObservations` for re-optimisation after assurance drift/degradation, using:

- `pathId`
- `observedLatencyMs`
- `observedReliabilityPercent`
- `observedAt`

## 12. REST / persistence / reliability baseline

### 12.1 ETags and concurrency

Mutable resources expose ETags.

State-changing operations that depend on current state require `If-Match`.

- Missing required ETag: `428 Precondition Required`
- Stale/mismatched ETag: `412 Precondition Failed`

### 12.2 Cache policy

Successful GET responses use:

- `Cache-Control: private, max-age=300`
- `ETag`

Use request header `Cache-Control: no-cache` for explicit client cache bypass/revalidation.

### 12.3 Persistence

IME microservices use managed PostgreSQL / PostgreSQL-compatible RDBMS where applicable.

Baseline includes:

- JSONB for flexible resource bodies
- Per-MS database boundary
- Flyway/Liquibase migrations
- No manual production schema changes
- Transactional outbox/inbox where needed

Runtime telemetry history is not stored in the IME entity database by default. Runtime metrics/time-series observations are most likely handled by the organisation's Prometheus SaaS / managed metrics platform.

## 13. Maintenance rule

When the user says to baseline a new Intent decision:

1. Update memory/context.
2. Update this clean context dump.
3. Update relevant Markdown specification/design files where applicable.
4. Keep TMF-facing shapes validated against the uploaded TMF source/reference files.
5. Do not update Optimisation artifacts unless explicitly requested.

## Baseline repair — ID MS design brief rebuilt from GitHub base

Baselined on 2026-05-11.

`id_ms_design_brief.md` has been rebuilt using the current GitHub design brief as the structural base, preserving the detailed sections for API contract, lifecycle/versioning, caching, ETag, circuit breakers, deployment/persistence, security/access control, observability/audit, consistency sweep, and callback URL baseline. The file was then patched with the agreed baseline corrections: `intent-definition-ms` -> `intent-definition-ms`, Intent Definition MS naming, `familyId`, `isBundle`, `validFor`, `relatedParty`, `targetEntitySchema`, `fields`, `428` for missing `If-Match`, `412` for stale/mismatch, `PUT` preferred, `PATCH` supported but discouraged generally, activation as lifecycle update not `/activate`, delete only unused `DRAFT`, intentional `/intentSpecification/hub`, and external `IntentSpecification*Event` boundary.

## Baseline correction — ID MS service identity

Baselined on 2026-05-11.

The correct ID MS service identity is Intent Definition MS / ID MS / `intent-definition-ms`. Do not use Intent Design MS / `intent-design-ms` for the ID MS service name. Apply this correction across specifications, design briefs, source/reportingSystem event metadata, logs, and context summaries.

## Baseline update — ID MS `fields` query parameter

Baselined on 2026-05-11.

`fields` is the optional TMF-style field selection/projection query parameter for ID MS `IntentSpecification` operations. It is supported on create, list, retrieve, PUT platform-extension update, and PATCH TMF-compatible update examples. When `fields` is omitted, ID MS returns the default representation for the operation. List defaults to a lightweight summary representation. Retrieve defaults to a full single-resource representation.

## Baseline update — ID MS POST create request/response sync

Baselined on 2026-05-11.

Fix 2 from the TMF compliance pass is applied to `POST /intentManagement/v5/intentSpecification`. The create request includes `familyId`, `isBundle: false`, `validFor.startDateTime`, lightweight provider `relatedParty`, `specCharacteristic`, `expressionSpecification`, and `targetEntitySchema`. The client does not send `id`, `href`, `Location`, `ETag`, or `_links`. ID MS generates `id`, `href`, `Location`, `ETag`, `Last-Modified`, and server `_links` in the `201 Created` response. The response mirrors the stored `IntentSpecification` representation and keeps `targetEntitySchema.@schemaLocation` as the governed expression-value schema reference for validating `Intent.expression.expressionValue`.

## Baseline update — ID MS GET list/retrieve sync

Baselined on 2026-05-11.

Fix 3 from the TMF compliance pass is applied. `GET /intentManagement/v5/intentSpecification` returns a lightweight summary list by default, including `id`, `href`, `familyId`, `name`, `version`, `lifecycleStatus`, `isBundle`, `validFor`, `relatedParty`, `@type`, and `@baseType`. It omits full `specCharacteristic`, `expressionSpecification`, and `targetEntitySchema` unless requested via `fields`.

`GET /intentManagement/v5/intentSpecification/{id}` returns the full single-resource representation by default, including `id`, `href`, `familyId`, `name`, `description`, `version`, `lifecycleStatus`, `isBundle`, `validFor`, `relatedParty`, `@type`, `@baseType`, `@schemaLocation`, `specCharacteristic`, `expressionSpecification`, `targetEntitySchema`, and server-generated `_links`.

Both GET operations keep optional `fields`, `ETag`, GET-only private caching, and retrieve supports `Cache-Control: no-cache` as a fresh-read override.
