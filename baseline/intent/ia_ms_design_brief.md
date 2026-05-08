## IA MS Design Brief:

### Purpose:

Intent Assurance MS, referred to as IA MS, owns runtime assurance evaluation, callback state normalisation, assurance state updates, and assurance event publication for IME runtime intents.

IA MS is the runtime assurance truth for IME. IC MS remains the owner of the externally visible runtime Intent lifecycle projection.

### Service Identity:

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Assurance MS |
| Service name | `intent-assurance-ms` |
| Short name | IA MS |
| Main responsibility | Runtime assurance, callback state normalisation, drift/degradation detection, assurance event publication |
| Primary event input | `IntentCallbackEvent` from `t7.intent.management.events.callbacks` |
| Other event input | `IntentNetworkReadyEvent`, `IntentResolvedEvent`, `IntentOptimisedEvent`, and related workflow events where required |
| Main event output | `IntentAssuranceEvent` |
| Retired event | `IntentDriftOccurredEvent` is not used in the active baseline |
| Event style | Internal CloudEvents headers with plain JSON `body` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| External TMF API owner | No — IC MS owns external lifecycle projection |

### Core Responsibilities:

| **Responsibility** | **Detail** |
|---|---|
| Runtime assurance truth | Owns current assurance/projection state used to determine whether an intent is healthy, degraded, failed, terminated, or requires re-optimisation |
| Callback consumption | Consumes raw `IntentCallbackEvent` from the dedicated callback topic |
| Intent correlation | Validates/correlates `intentId` using IA state and platform context |
| Unknown intent handling | Owns dead-letter/reject/operational handling decision for unknown or non-correlatable `intentId` |
| Orchestrator type derivation | Derives `orchestratorType` from IA/platform context, not from ICB MS |
| Raw state mapping | Maps raw `orchestratorState` into platform lifecycle/assurance meaning |
| Skip/unmapped handling | Handles unmapped/skip callback states with logging/audit as required |
| Assurance state update | Updates current assurance/projection state when actionable events are received |
| Drift/degradation detection | Detects runtime drift/degradation against KP-derived expectations |
| Assurance event publication | Publishes `IntentAssuranceEvent` to `t7.intent.management.events` |
| Runtime assurance trigger | Uses callback outcomes and observation metrics obtained through observability endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` |
| IA outbox ownership | Owns IA outbox and relay for reliable event publication |
| Idempotency tracking | Tracks consumed events and/or correlation keys where required |

### IA MS Does Not Own:

| **Concern** | **Owner** |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| Runtime `Intent` resource API | IC MS |
| External TMF-facing lifecycle projection | IC MS |
| Raw callback ingestion API | ICB MS |
| Callback outbox persistence | ICB MS |
| Network apply/orchestration execution | Orchestration layer / network orchestrator |
| Intent interpretation/resolution | II MS |
| Optimisation decision | IO MS |
| Knowledge Plane config CRUD/governance | Knowledge Plane operating model |
| OEX user experience | OEX layer |

### Main Inputs:

| **Input** | **Source** | **Purpose** |
|---|---|---|
| `IntentCallbackEvent` | ICB MS via `t7.intent.management.events.callbacks` | Raw orchestrator callback state for IA-owned mapping |
| `IntentNetworkReadyEvent` | II MS via main internal topic | Network-ready configuration and observability scope |
| Runtime metrics from observation endpoints | Observability platform endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` | Runtime metrics such as latency, availability, packet loss, and jitter for observer-scope resources |
| Knowledge Plane config | KP / governed config source | Thresholds, mapping rules, assurance rules, observability scope |
| IA state | IA MS DB | Correlation, current assurance/projection state, idempotency |

### Main Outputs:

| **Output** | **Target** | **Purpose** |
|---|---|---|
| `IntentAssuranceEvent` | Main internal topic `t7.intent.management.events` | Single IA-owned runtime assurance outcome event used for healthy, degraded, failed, terminated, drift, and re-optimisation outcomes |
| Dead-letter / reject outcome | IA DB / operational handling path | Records unknown/non-correlatable callback or failed processing decision |
| Skip/audit outcome | IA DB/logging | Records unmapped or intentionally ignored callback state |

### Callback Handling Baseline:

| **Concern** | **Owner** |
|---|---|
| Callback REST endpoint | ICB MS |
| Structural callback validation | ICB MS |
| Callback outbox persistence | ICB MS |
| Publication of raw callback event | ICB MS |
| `IntentCallbackEvent` consumption | IA MS |
| `intentId` existence/correlation validation | IA MS |
| Unknown `intentId` dead-letter decision | IA MS |
| `orchestratorType` derivation | IA MS |
| `orchestratorState` mapping | IA MS |
| Skip/unmapped callback handling | IA MS |
| Assurance/lifecycle event publication | IA MS |

### IntentCallbackEvent Consumption Flow:

| **Step** | **Action** |
|---|---|
| 1 | IA MS consumes `IntentCallbackEvent` from `t7.intent.management.events.callbacks` |
| 2 | IA MS checks idempotency/correlation where required |
| 3 | IA MS validates/correlates `intentId` using IA state/platform context |
| 4 | If unknown or not correlatable, IA MS records reject/dead-letter/operational handling outcome |
| 5 | If known, IA MS derives `orchestratorType` from IA/platform context |
| 6 | IA MS maps raw `orchestratorState` into lifecycle/assurance meaning |
| 7 | If unmapped/skip state, IA MS records skip outcome with audit/logging as required |
| 8 | If mapped/actionable, IA MS updates current assurance/projection state |
| 9 | IA MS writes IA outbox record for `IntentAssuranceEvent` |
| 10 | IA relay publishes `IntentAssuranceEvent` to `t7.intent.management.events` |

### IntentAssuranceEvent Baseline:

`IntentAssuranceEvent` is the single IA-owned runtime assurance event.

It carries curated assurance facts using the internal event contract, not the external TMF expression wrapper.

The active default body shape uses:

| **Field / area** | **Purpose** |
|---|---|
| `lifecycleStatus` | Lifecycle-driving state that IC MS projects externally |
| `statusReason` | Human-readable reason for the current assurance outcome |
| `location` | Canonical location context |
| `serviceType` / `serviceClass` | Canonical service context |
| `targets` | Runtime targets used to interpret observations |
| `resources` | Selected/applied resources where relevant |
| `observations` | Curated observed metrics for selected or observer-scope resources |
| `references` | Correlation and external resource references |

IA MS does not emit `IntentDriftOccurredEvent` in the active baseline. Drift/degradation is represented through `IntentAssuranceEvent.lifecycleStatus`, `statusReason`, `targets`, and `observations`.

IA MS does not include raw callback payloads, raw telemetry dumps, optimiser scoring, solver internals, or `provider` in `IntentAssuranceEvent`.

### Observation endpoint baseline:

IA MS obtains runtime metrics from observability/observation endpoints.

The observation target, profile, and resource scope are informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration`, especially:

- `observerConfiguration.target`
- `observerConfiguration.profile`
- `observerConfiguration.resourceIds`

No separately named observation snapshot event is baselined by default.

### Lifecycle Projection Relationship With IC MS:

IA MS does not own the external `Intent.lifecycleStatus` resource API.

IA MS emits lifecycle-driving assurance outcomes inside `IntentAssuranceEvent`.

IC MS consumes those events and updates/projects the external runtime `Intent` lifecycle.

| **IA Outcome** | **Typical IC Projection** |
|---|---|
| Apply completed / healthy | `Active` |
| Apply in progress | `InProgress` |
| Assurance degraded / drift detected | `Degraded` |
| Apply failed / unrecoverable failure | `Failed` |
| Termination confirmed | `Terminated` |
| Semantic/policy rejection from II MS | `Rejected` |

### Internal Event Envelope Baseline:

| **Envelope Area** | **Baseline** |
|---|---|
| Metadata | CloudEvents metadata in headers |
| Body wrapper | Top-level `body` |
| Payload format | Plain internal JSON |
| External TMF shape | Not used internally |
| Content type | `content-type: application/json` |
| Correlation header | `correlationid` |
| Event source | `intent-assurance-ms` |

### Persistence Baseline:

IA MS follows the active IME DB baseline.

| **Concern** | **Baseline** |
|---|---|
| DB type | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| DB ownership | Dedicated IA MS DB instance or logical managed DB boundary |
| Shared cross-MS DB | Not allowed |
| Schema migration | Flyway or Liquibase |
| Manual schema change | Not permitted |
| Future DR | Cross-region active-passive DR path required |

### Indicative Tables:

| **Table** | **Purpose** |
|---|---|
| `intent_assurance_state` | Current assurance/projection state per intent |
| `intent_assurance_observation` | Current or recent assurance observations where required |
| `intent_assurance_idempotency` | Deduplication/idempotency tracking for consumed events |
| `intent_assurance_mapping_audit` | Audit trail for callback mapping decisions |
| `intent_assurance_outbox` | Reliable publication of IA-owned events |
| `intent_assurance_dead_letter` | Optional dead-letter table if DLT model is selected |
| `shedlock` | Relay coordination if IA MS runs clustered outbox relay |

### Open Items:

| **Open Item** | **Status** |
|---|---|
| Dead-letter implementation model | Pending PLATFORM-021; DLT table/API vs Kafka DLQ topic |
| Exact orchestrator mapping config store | Pending KP operating model |
| Exact telemetry source integration | Pending observability/telemetry architecture |
| Exact assurance thresholds | Pending KP assurance rule definitions |
| Exact lifecycle projection mapping into IC MS | Needs final mapping table |
| IA outbox retry thresholds | Needs operational tuning |
| IA retention policy | Needs data retention decision |
| IA deployment sizing | Pending load testing |
| Kafka/event-streaming DR | Pending platform regional eventing decision |
