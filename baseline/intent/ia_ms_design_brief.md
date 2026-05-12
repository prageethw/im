# IA MS Design Brief

## Purpose

Intent Assurance MS, referred to as IA MS, owns runtime assurance evaluation, callback state normalisation, assurance state updates, and assurance event publication for IME runtime intents.

IA MS is the runtime assurance truth for IME. IC MS remains the owner of the externally visible runtime `Intent` lifecycle projection. IA MS consumes optimisation, network-ready, callback, and observation/telemetry facts only.

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
| External TMF API owner | No — IC MS owns external lifecycle projection |

## Core Responsibilities

| **Responsibility** | **Detail** |
|---|---|
| Runtime assurance truth | Owns current assurance/projection state used to determine whether an intent is healthy, degraded, failed, or terminated |
| Callback consumption | Consumes raw `IntentCallbackEvent` from the dedicated callback topic |
| Intent correlation | Validates/correlates `intentId` using IA state and platform context |
| Raw state mapping | Maps raw `orchestratorState` into platform lifecycle/assurance meaning |
| Assurance state update | Updates current assurance/projection state when actionable events are received |
| Degradation detection | Detects runtime degradation against resolved runtime targets and the IA stored applied assurance baseline |
| Assurance event publication | Publishes `IntentAssuranceEvent` to `t7.intent.management.events` |
| Runtime assurance trigger | Uses callback outcomes and observation metrics obtained through observability endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` |
| IA outbox ownership | Owns IA outbox and relay for reliable event publication |

`requiresReoptimisation` is not included by default in `IntentAssuranceEvent`. II MS or another authorised decision component reads the assurance event state and decides whether re-interpretation, re-optimisation, or no action is required.

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
| Optimisation decision | Optimiser / IO context |
| Knowledge Plane config CRUD/governance | Knowledge Plane operating model |
| OEX user experience | OEX layer |

## Main Inputs

| **Input** | **Source** | **Purpose** |
|---|---|---|
| `IntentCallbackEvent` | ICB MS via `t7.intent.management.events.callbacks` | Raw orchestrator callback state for IA-owned mapping |
| `IntentNetworkReadyEvent` | `intent-intelligence-ms` via main internal topic | Network-ready configuration and observability scope |
| `IntentOptimisedEvent` | Optimiser via main internal topic | Selected resources, resolved targets, resolved constraints, preferences, and optimisation outcome |
| Runtime metrics from observation endpoints | Observability platform endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` | Runtime metrics such as latency, availability, packet loss, and jitter for observer-scope resources |
| IA state | IA MS DB | Correlation, current assurance/projection state, idempotency |

## Internal context structure alignment

Internal events may use a plain `body.context` object where they carry resolved runtime targets, constraints, and preferences.

For IA and optimisation assurance flows, use:

- `body.context.targets`
- `body.context.constraints`
- `body.context.preferences`

This keeps the end-to-end targets/constraints/preferences structure aligned across ID, IC, II, optimiser, and IA. This is an internal plain JSON event shape, not the external TMF `Intent.expression` wrapper.

## IntentNetworkReadyEvent source rule

`IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.

IA MS currently consumes it, but consumer identity is not part of the event ownership rule. IA MS must not show `ce-source: intent-assurance-ms` for `IntentNetworkReadyEvent`.

```http
ce-source: intent-intelligence-ms
```

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

The canonical `IntentCallbackEvent` fields consumed by IA are `orchestratorState`, `orchestratorSource`, and `orchestratorTimestamp`.

## IntentAssuranceEvent baseline

`IntentAssuranceEvent` is the single IA-owned runtime assurance event.

It carries curated assurance facts using the internal event contract, not the external TMF expression wrapper.

The active generic body shape uses:

| **Field / area** | **Purpose** |
|---|---|
| `lifecycleStatus` | Lifecycle-driving state that IC MS projects externally |
| `statusReason` | Human-readable reason for the current assurance outcome |
| `context.targets` | Runtime targets used to interpret observations |
| `context.constraints` | Location/service/priority/redundancy context where needed |
| `context.preferences` | Preference context where useful for downstream decisions |
| `current.evaluations` | Curated assurance evaluations for normal/active states |
| `current.resources` | Selected/applied/observed resources for normal/active states |
| `evaluations` | Curated violated/satisfied assurance checks for degraded/failed re-decision states |
| `candidates` | All applicable available resources for degraded/failed re-decision states, including the current resource and alternatives, with metrics and status indicators |
| `references` | Correlation and external resource references |

Reusable resource entries use `roles`, `resourceId`, `resourceType`, `resourceClass`, `resourceAttributes`, `relationships`, and `metrics`.

Current runtime metric names use `latencyMs` and `reliabilityPercent`. Benchmark contexts may use `latencyBenchmarkMs` and `reliabilityBenchmarkPercent`.

IA MS does not emit `IntentDriftOccurredEvent` in the active baseline. Drift/degradation is represented through `IntentAssuranceEvent.lifecycleStatus`, `statusReason`, `context`, `current.evaluations`, `current.resources`, and optionally `candidates`.

IA MS does not include raw callback payloads, raw telemetry dumps, optimiser scoring, solver internals, `provider`, or default `requiresReoptimisation` in `IntentAssuranceEvent`.

For `Active`, `current.resources` remains acceptable because there is no re-decision pressure. For `Degraded` and `Failed`, IA MS should not include a separate `current` block by default. Instead, it should put the current affected resource and all applicable alternatives together in `candidates`, using candidate-level `selectionStatus` and `assuranceStatus` to identify current, available, healthy, degraded, failed, or unavailable resources. Each candidate carries its own runtime metrics and benchmark metrics where available. For `Terminated`, candidates are normally not needed unless reporting final resources.

## Observation endpoint baseline

IA MS obtains runtime metrics from observability/observation endpoints. The observation endpoints are informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration`.

IA evaluates returned metric facts against resolved runtime targets and the IA stored applied assurance baseline. KP/rules may support mapping and evaluation policy but are not the source of truth for every assurance decision.

## Final baseline statement

IA MS is the runtime assurance truth service. It consumes callback, network-ready, optimisation, and observation facts; maps raw callback state; evaluates runtime observations against resolved runtime targets and the stored applied assurance baseline; and emits curated generic `IntentAssuranceEvent` outcomes.

IC MS consumes `IntentAssuranceEvent` to project external TMF-facing `Intent` lifecycle and `IntentReport` resources.
