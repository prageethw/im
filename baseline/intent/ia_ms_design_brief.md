# IA MS Design Brief

## Purpose

Intent Assurance MS, referred to as IA MS, owns runtime assurance evaluation, callback state normalisation, assurance state updates, and assurance event publication for IME runtime intents.

IA MS is the runtime assurance truth for IME. IC MS remains the owner of the externally visible runtime `Intent` lifecycle projection.

IA MS consumes optimisation, network-ready, callback, and observation/telemetry facts only.


## Service Identity

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Assurance MS |
| Service name | `intent-assurance-ms` |
| Short name | IA MS |
| Main responsibility | Runtime assurance, callback state normalisation, drift/degradation detection, assurance event publication |
| Primary event input | `IntentCallbackEvent` from `t7.intent.management.events.callbacks` |
| Other event input | `IntentNetworkReadyEvent` and `IntentOptimisedEvent` |
| Main event output | `IntentAssuranceEvent` |
| Retired event | `IntentDriftOccurredEvent` is not used in the active baseline |
| Event style | Internal CloudEvents headers with plain JSON `body` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| External TMF API owner | No — IC MS owns external lifecycle projection |

## Core Responsibilities

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
| Drift/degradation detection | Detects runtime drift/degradation against resolved runtime targets and the IA stored applied assurance baseline |
| Assurance event publication | Publishes `IntentAssuranceEvent` to `t7.intent.management.events` |
| Runtime assurance trigger | Uses callback outcomes and observation metrics obtained through observability endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` |
| IA outbox ownership | Owns IA outbox and relay for reliable event publication |
| Idempotency tracking | Tracks consumed events and/or correlation keys where required |

KP/rules may support mapping and evaluation policy, but IA does not treat KP as the per-decision source of truth for every assurance decision.

## IA MS Does Not Own

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

## Main Inputs

| **Input** | **Source** | **Purpose** |
|---|---|---|
| `IntentCallbackEvent` | ICB MS via `t7.intent.management.events.callbacks` | Raw orchestrator callback state for IA-owned mapping |
| `IntentNetworkReadyEvent` | II MS via main internal topic | Network-ready configuration and observability scope |
| `IntentOptimisedEvent` | Optimiser via main internal topic | Selected resources, resolved targets, resolved constraints, preferences, and optimisation outcome |
| Runtime metrics from observation endpoints | Observability platform endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` | Runtime metrics such as latency, availability, packet loss, and jitter for observer-scope resources |
| Knowledge Plane config | KP / governed config source | Mapping rules, evaluation policy, assurance rules, and observability policy where required |
| IA state | IA MS DB | Correlation, current assurance/projection state, idempotency |

## Internal context structure alignment

`IntentOptimisedEvent` consumed by IA uses:

- `body.context.targets`
- `body.context.constraints`
- `body.context.preferences`

This keeps the end-to-end targets/constraints/preferences structure aligned across ID, IC, II, optimiser, and IA.

This is an internal plain JSON event shape, not the external TMF `Intent.expression` wrapper.

## IntentNetworkReadyEvent source rule

`IntentNetworkReadyEvent` is consumed by IA MS. It must not show `ce-source: intent-assurance-ms`.

In the active baseline, use:

```http
ce-source: intent-intelligence-ms
```

unless a later baseline assigns this event to a different publisher.

## Callback handling baseline

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
| Raw `orchestratorState` mapping | IA MS |
| Skip/unmapped callback handling | IA MS |
| Assurance/lifecycle event publication | IA MS |

The canonical `IntentCallbackEvent` fields consumed by IA are `orchestratorState`, `orchestratorSource`, and `orchestratorTimestamp`. Older names such as `callbackSource`, `callbackTimestamp`, and `sourceState.state` are not the active baseline.

## IntentCallbackEvent Consumption Flow

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

## IntentAssuranceEvent Baseline

`IntentAssuranceEvent` is the single IA-owned runtime assurance event. It carries curated assurance facts using the internal event contract, not the external TMF expression wrapper.

The active default body shape uses:

| **Field / area** | **Purpose** |
|---|---|
| `lifecycleStatus` | Lifecycle-driving state that IC MS projects externally |
| `statusReason` | Human-readable reason for the current assurance outcome |
| `context.constraints.location` | Canonical location context |
| `context.constraints.serviceType` / `context.constraints.serviceClass` | Canonical service context |
| `context.targets` | Runtime targets used to interpret observations |
| `resources` | Selected/applied resources where relevant |
| `observations` | Curated observed metrics for selected or observer-scope resources |
| `references` | Correlation and external resource references |

IA MS does not emit `IntentDriftOccurredEvent` in the active baseline. Drift/degradation is represented through `IntentAssuranceEvent.lifecycleStatus`, `statusReason`, `context.targets`, and `observations`.

IA MS does not include raw callback payloads, raw telemetry dumps, optimiser scoring, solver internals, or `provider` in `IntentAssuranceEvent`.

## Observation endpoint baseline

IA MS obtains runtime metrics from observability/observation endpoints. The observation endpoints are informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration`.

IA evaluates returned metric facts against resolved runtime targets and the IA stored applied assurance baseline. KP/rules may support mapping and evaluation policy but are not the source of truth for every assurance decision.

## Final baseline statement

IA MS is the runtime assurance truth service. It consumes callback, network-ready, optimisation, and observation facts; maps raw callback state; evaluates runtime observations against resolved runtime targets and the stored applied assurance baseline; and emits curated `IntentAssuranceEvent` outcomes.

IC MS consumes `IntentAssuranceEvent` to project external TMF-facing `Intent` lifecycle and `IntentReport` resources.
