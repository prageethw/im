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
- Intent Design MS
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

- ID MS — Intent Design MS
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

ID MS owns design-time `IntentSpecification` lifecycle/governance.

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


## Baseline update — IC MS TMF compliance and ID MS expression alignment

Baselined on 2026-05-11.

Applied IC MS compliance improvements from the current GitHub baseline rather than replacing the whole artifact. IC MS now aligns runtime `Intent.expression.expressionValue` with the ID MS baseline: external expression value uses `context.targets`, `context.constraints`, and `context.preferences`, with `location`, `serviceType`, and `serviceClass` under `context.constraints`. Internal `IntentValidatedEvent.body.expression` carries the same semantic buckets without the external TMF wrapper. IC MS supports optional TMF-style `fields` on Intent and IntentReport operations where applicable. Missing required `If-Match` returns `428`; stale or mismatched `If-Match` returns `412`. `DELETE /intent/{id}` remains termination, not physical deletion, and uses `202 Accepted` for accepted termination. `IntentReport` remains read-only for ordinary external API consumers; ordinary `DELETE /intent/{intentId}/intentReport/{id}` is not exposed by default because reports are retained audit/projection history. Report archive/purge is governed internal retention/admin policy, so no separate IntentReport lifecycle is baselined and `IntentReportDeleteEvent` is not part of the normal external event family.

## Baseline update — IC MS IntentReportDeleteEvent posture

Baselined on 2026-05-11.

IC MS does not expose ordinary external `DELETE /intentManagement/v5/intent/{intentId}/intentReport/{id}` for normal API consumers. `IntentReport` remains a read-only curated report/projection/audit resource and no separate `IntentReport` lifecycle is baselined for ordinary consumer use. However, `IntentReportDeleteEvent` remains part of the external TMF-style event vocabulary for `IntentReport` alignment. It is emitted only for governed platform/internal retention purge, administrative removal, legal deletion, or approved data-correction handling where such removal is permitted by retention policy; it is not emitted as the result of ordinary external consumer delete.

## Baseline update — IC MS internal-only IntentReport delete/purge

Baselined on 2026-05-11.

IC MS does not expose ordinary external `DELETE /intentManagement/v5/intent/{intentId}/intentReport/{id}` through NGW or public TMF-facing consumer APIs. External consumers can list and retrieve `IntentReport` records only.

IC MS may provide an internal-only governed `IntentReport` delete/purge capability. This capability is not routed through NGW, not advertised as a public consumer API, and not available to normal external consumers. It is restricted to retention purge, legal deletion, platform administration, approved data-correction workflows, or policy-governed cleanup.

No separate `IntentReport` lifecycle is baselined for ordinary consumer use because delete/purge is a governed administrative operation, not a normal report lifecycle transition.

`IntentReportDeleteEvent` remains part of the external TMF-style event vocabulary. IC MS emits `IntentReportDeleteEvent` only after successful governed internal/admin removal where notification is allowed by policy. It is not emitted from ordinary external consumer delete because ordinary external consumer delete is not exposed.

## Baseline update — IC MS design expression-shape cleanup

Baselined on 2026-05-11.

Cleaned up `ic_ms_design_brief.md` so the shared semantic bucket example no longer shows the older flat runtime expression shape. The design now consistently uses the ID MS external runtime expression baseline: `Intent.expression.expressionValue.context.targets`, `context.constraints`, and `context.preferences`. `location`, `serviceType`, and `serviceClass` are under `context.constraints`, not peers beside the semantic buckets. IC MS preserves the TMF expression wrapper externally and emits internal `IntentValidatedEvent` using native JSON buckets without the external wrapper.
