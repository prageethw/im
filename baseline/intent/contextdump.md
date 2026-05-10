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

## Baseline update — corrected ID MS spec patch actually applied

Baselined on 2026-05-11.

Corrected the generated `id_ms_specification.md` after discovering the previous replacement failed. The current generated file now actually contains the revised DELETE, activation/retirement, hub, and external event snapshot sections. Verification markers include runtime-reference delete blocking, `/intentSpecification/{id}/activate` rejection, `428`/`412` examples, hub retrieve private caching, event snapshot metadata rules, and event snapshots with `familyId`, `isBundle`, `validFor`, and `relatedParty`.


## Baseline update — ID MS fresh GitHub spec/design compliance patch

Baselined on 2026-05-11.

Fresh copies of `id_ms_specification.md` and `id_ms_design_brief.md` have been patched to use `Intent Definition MS` / `intent-definition-ms` consistently. The ID MS specification early resource examples were aligned with the existing design brief and TMF-facing baseline: POST create now includes `familyId`, `isBundle`, `validFor`, `relatedParty`, `specCharacteristic`, `expressionSpecification`, and `targetEntitySchema`, and excludes client-supplied `_links`; GET list returns the lightweight summary metadata; GET retrieve returns the full single-resource metadata including `targetEntitySchema`; PUT carries the full replacement representation; PATCH remains supported for TMF compatibility but is discouraged as a general update method. Later DELETE, activation, hub, and event snapshot baselines remain in place.
