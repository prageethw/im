# IA MS Design Brief

## Purpose

Intent Assurance MS, referred to as IA MS, owns runtime assurance evaluation, callback state normalisation, assurance state updates, and assurance event publication for IME runtime intents. IA MS is the runtime assurance truth for IME. IC MS remains the owner of the externally visible runtime `Intent` lifecycle projection. IA MS consumes `IntentNetworkReadyEvent`, `IntentCallbackEvent`, and runtime metrics/observation facts only.

IA MS does not consume `IntentOptimisedEvent` in the active baseline.

## Service Identity

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Assurance MS |
| Service name | `intent-assurance-ms` |
| Short name | IA MS |
| Main responsibility | Runtime assurance, callback state normalisation, drift/degradation detection, assurance event publication |
| Primary event input | `IntentCallbackEvent` from `t7.intent.management.events.callbacks` |
| Other event input | `IntentNetworkReadyEvent` |
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
| Raw state mapping | Maps raw `sourceState.state` into platform lifecycle/assurance meaning |
| Assurance state update | Updates current assurance/projection state when actionable events are received |
| Degradation detection | Detects runtime degradation against resolved runtime targets and the IA stored applied assurance baseline |
| Assurance event publication | Publishes `IntentAssuranceEvent` to `t7.intent.management.events` |
| Runtime assurance trigger | Uses callback outcomes and observation metrics obtained through observability endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` |
| IA outbox ownership | Owns IA outbox and relay for reliable event publication |

`requiresReoptimisation` is not included by default in `IntentAssuranceEvent`.

II MS or another authorised decision component reads the assurance event state and decides whether re-interpretation, re-optimisation, or no action is required.

## IA MS Does Not Own

| **Concern** | **Owner** |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| Runtime `Intent` resource API | IC MS |
| External TMF-compliant lifecycle projection | IC MS |
| Raw callback ingestion API | ICB MS |
| Callback outbox persistence | ICB MS |
| Network change execution / apply execution | Change execution layer / network orchestrator |
| Intent interpretation/resolution | II MS |
| Optimisation decision | Optimiser / IO context |
| Knowledge Plane config CRUD/governance | Knowledge Plane operating model |
| OEX user experience | OEX layer |

## Main Inputs

| **Input** | **Source** | **Purpose** |
|---|---|---|
| `IntentCallbackEvent` | ICB MS via `t7.intent.management.events.callbacks` | Raw source callback state for IA-owned mapping |
| `IntentNetworkReadyEvent` | `intent-intelligence-ms` via main internal topic | Network-ready configuration and observability scope |
| Runtime metrics from observation endpoints | Observability platform endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` | Runtime metrics such as latency, availability, packet loss, and jitter for observer-scope resources |
| IA state | IA MS DB | Correlation, current assurance/projection state, idempotency |

## IntentNetworkReadyEvent source rule

`IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.

IA MS currently consumes it, but consumer identity is not part of the event ownership rule. IA MS must not show `ce-source: intent-assurance-ms` for `IntentNetworkReadyEvent`.

```http
ce-source: intent-intelligence-ms
```

`IntentNetworkReadyEvent.serviceConfiguration.orchestratorConfiguration.resources[]` carries the selected apply configuration. `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[]` carries the full assurance observation scope that IA MS must observe.

Within `serviceConfiguration.observerConfiguration.resources[]`, `metrics` is a list of metric names to observe, not metric values. Example metric names are `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.

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
| Source/change-execution type derivation | IA MS |
| Raw `sourceState.state` mapping | IA MS |
| Skip/unmapped callback handling | IA MS |
| Assurance/lifecycle event publication | IA MS |

The canonical `IntentCallbackEvent` fields consumed by IA are `callbackSource`, `callbackTimestamp`, and `sourceState`.

`sourceState.state` carries the raw source/change-execution state value. IA maps `sourceState.state` into lifecycle/assurance meaning.

## IntentAssuranceEvent baseline

`IntentAssuranceEvent` is the single IA-owned runtime assurance event. It carries curated assurance facts using the internal event contract, not the external TMF expression wrapper.

The active generic body shape uses:

| **Field / area** | **Purpose** |
|---|---|
| `lifecycleStatus` | Lifecycle-driving state that IC MS projects externally |
| `statusReason` | Human-readable reason for the current assurance outcome |
| `context.targets` | Runtime targets used to interpret observations |
| `context.constraints` | Location/service/priority/redundancy context where needed |
| `context.preferences` | Preference context where useful for downstream decisions |
| `current.resources` | Full observed resource/path set in the IA assurance scope, mirroring `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[]` |
| `references` | Correlation and external resource references |

Reusable resource entries use `roles`, `resourceId`, `resourceType`, `resourceClass`, `resourceAttributes`, `relationships`, and `metrics`.

Metric names are neutral and use names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`. Do not use metric origin wrappers or context-encoded field names such as `metrics.benchmark`, `metrics.telemetry`, `latencyBenchmarkMs`, `currentLatencyMs`, or `observedLatencyMs` in `IntentAssuranceEvent`. IA MS does not emit `IntentDriftOccurredEvent` in the active baseline.

Drift/degradation is represented through `IntentAssuranceEvent.lifecycleStatus`, `statusReason`, `context`, and resource-level `metrics` in `current.resources`. IA MS does not include raw callback payloads, raw telemetry dumps, optimiser scoring, solver internals, `provider`, `current.evaluations`, `body.evaluations`, default `requiresReoptimisation`, `selectionStatus`, `assuranceStatus`, or a default `candidates` block in `IntentAssuranceEvent`.

For `Active`, `Degraded`, and `Failed`, `current.resources[]` should carry the full observer scope where applicable. `lifecycleStatus` and `statusReason` explain the interpreted outcome; each resource entry remains factual.

## Observation endpoint baseline

IA MS obtains runtime metrics from observability/observation endpoints. The observation endpoints are informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration`.

IA evaluates returned metric facts against resolved runtime targets and the IA stored applied assurance baseline. KP/rules may support mapping and evaluation policy but are not the source of truth for every assurance decision.

## Final baseline statement

IA MS is the runtime assurance truth service.

It consumes `IntentNetworkReadyEvent`, `IntentCallbackEvent`, and observation facts only; maps raw callback state; evaluates runtime observations against resolved runtime targets and the stored applied assurance baseline; and emits curated generic `IntentAssuranceEvent` outcomes. IC MS consumes `IntentAssuranceEvent` to project external TMF-compliant `Intent` lifecycle and `IntentReport` resources.

## Metrics-first IntentAssuranceEvent refinement

`IntentAssuranceEvent` is metrics-first by default.

Do not include `current.evaluations` or `body.evaluations` unless a future policy explicitly requires derived evaluation objects. `lifecycleStatus` and `statusReason` explain the outcome; resource-level `metrics` provide the factual observed data needed by IC MS, II MS, and authorised decision components.
