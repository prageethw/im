# IA MS Design Brief

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Document version | v1.0 |
| Last updated | 2026-06-01 |
| Scope | Intent Assurance MS design brief |
| Source of truth after commit | GitHub `baseline/intent/ia-ms/ia_ms_design_brief.md` |

Document authority: this design brief is authoritative for IA MS design decisions, responsibility boundaries, and ownership rules. Field-level contracts are defined in the IA MS specification; operational and configuration guidance is captured in the IA MS solution brief.

## Table of contents:

- [1. Purpose:](#1-purpose)
- [2. Service Identity:](#2-service-identity)
- [3. Core Responsibilities:](#3-core-responsibilities)
- [4. IA MS Does Not Own:](#4-ia-ms-does-not-own)
- [5. Main Inputs:](#5-main-inputs)
- [6. IntentNetworkReadyEvent source rule:](#6-intentnetworkreadyevent-source-rule)
- [7. Callback handling baseline:](#7-callback-handling-baseline)
- [8. Stale version and late-event handling:](#8-stale-version-and-late-event-handling)
- [9. IntentAssuranceEvent baseline:](#9-intentassuranceevent-baseline)
- [10. Observation endpoint baseline:](#10-observation-endpoint-baseline)
- [11. Observation gap and DLQ baseline:](#11-observation-gap-and-dlq-baseline)
- [12. Final baseline statement:](#12-final-baseline-statement)

## 1. Purpose:

Intent Assurance MS, referred to as IA MS, owns runtime assurance evaluation, callback state normalisation, assurance state updates, and assurance event publication for IME runtime intents. IA MS is the runtime assurance truth for IME. IC MS remains the owner of the externally visible runtime `Intent` lifecycle projection. IA MS consumes `IntentNetworkReadyEvent`, `IntentCallbackEvent`, and runtime metrics and observation facts only. For `IntentNetworkReadyEvent`, IA MS expects the final II MS shape using `body.intentVersion` and `body.expression.context`.


## 2. Service Identity:

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Assurance MS |
| Service name | `intent-assurance-ms` |
| Short name | IA MS |
| Main responsibility | Runtime assurance truth, callback state normalisation, observation evaluation, drift/degradation detection, assurance state updates, and `IntentAssuranceEvent` publication |
| Primary event inputs | `IntentNetworkReadyEvent`; `IntentCallbackEvent` from `t7.intent.management.events.callbacks` |
| Main event output | `IntentAssuranceEvent` |
| Event style | Internal CloudEvents headers with plain JSON `body` |
| External TMF API owner | No — IC MS owns external lifecycle projection |

## 3. Core Responsibilities:

| **Responsibility** | **Detail** |
|---|---|
| Runtime assurance truth | Owns current assurance and projection state used to determine whether an intent is healthy, degraded, failed, or terminated |
| Callback consumption | Consumes raw `IntentCallbackEvent` from the dedicated callback topic |
| Intent correlation | Validates/correlates `intentId` using IA state and platform context |
| Raw state mapping | Maps raw `sourceState.state` into platform lifecycle and assurance meaning |
| Assurance state update | Updates current assurance and projection state when actionable events are received |
| Degradation detection | Detects runtime degradation against resolved runtime targets and the IA stored applied assurance baseline |
| Assurance event publication | Publishes `IntentAssuranceEvent` to `t7.intent.management.events` |
| Runtime assurance trigger | Uses callback outcomes and observation metrics obtained through observability endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` |
| IA outbox ownership | Owns IA outbox and relay for reliable event publication |

`requiresReoptimisation` is not included by default in `IntentAssuranceEvent`.

II MS or another authorised decision component reads the assurance event state and decides whether re-interpretation, re-optimisation, or no action is required.

## 4. IA MS Does Not Own:

| **Concern** | **Owner** |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| Runtime `Intent` resource API | IC MS |
| External TMF-compliant lifecycle projection | IC MS |
| Raw callback ingestion API | ICB MS |
| Callback outbox persistence | ICB MS |
| Network change execution and apply execution | Change execution layer or network orchestrator |
| Intent interpretation/resolution | II MS |
| Optimisation decision | Optimiser and IO context |
| Knowledge Plane config CRUD and governance | Knowledge Plane operating model |
| OEX user experience | OEX layer |

## 5. Main Inputs:

| **Input** | **Source** | **Purpose** |
|---|---|---|
| `IntentCallbackEvent` | ICB MS via `t7.intent.management.events.callbacks` | Raw source callback state for IA-owned mapping |
| `IntentNetworkReadyEvent` | `intent-intelligence-ms` via main internal topic | Network-ready configuration and observability scope |
| Runtime metrics from observation endpoints | Observability platform endpoints informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` | Runtime metrics such as latency, availability, packet loss, and jitter for observer-scope resources |
| IA state | IA MS DB | Correlation, current assurance and projection state, idempotency |

## 6. IntentNetworkReadyEvent source rule:

`IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.

IA MS currently consumes it, but consumer identity is not part of the event ownership rule. IA MS must not show `ce-source: intent-assurance-ms` for `IntentNetworkReadyEvent`.

```http
ce-source: intent-intelligence-ms
```

`IntentNetworkReadyEvent.body.expression.context` carries the resolved runtime targets, constraints, and preferences. `IntentNetworkReadyEvent.serviceConfiguration.orchestratorConfiguration.resources[]` carries the selected apply configuration. `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[]` carries the full assurance observation scope that IA MS must observe.

Within `serviceConfiguration.observerConfiguration.resources[]`, `metrics` is a list of metric names to observe, not metric values. Example metric names are `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.

## 7. Callback handling baseline:

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

`sourceState.state` carries the raw source or change-execution state value. IA maps `sourceState.state` into lifecycle and assurance meaning.

Partial apply failure is treated as an IA mapping scenario: if the source or change-execution layer reports that some resources were applied and others failed, IA MS must preserve the factual callback and observation context, map the outcome to `Degraded` or `Failed` according to policy severity, and publish a curated `IntentAssuranceEvent` without exposing raw callback payloads.

## 8. Stale version and late-event handling:

IA MS must key assurance state by `intentId` and `intentVersion` where runtime versioning is supplied. A stale `IntentNetworkReadyEvent`, `IntentCallbackEvent`, or observation result for an older intent version must not overwrite newer IA state. Late callbacks or late observations for a superseded, terminated, or otherwise inactive version should be recorded for audit or dead-letter handling according to policy, but must not publish misleading `IntentAssuranceEvent` outcomes for the current version.

## 9. IntentAssuranceEvent baseline:

`IntentAssuranceEvent` is the single IA-owned runtime assurance event. It carries curated assurance facts using the internal event contract, not the external TMF expression wrapper.

The active generic body shape uses `intentVersion` for runtime intent versioning and `expression.context` for targets, constraints, and preferences:

| **Field or area** | **Purpose** |
|---|---|
| `lifecycleStatus` | Lifecycle-driving state that IC MS projects externally |
| `statusReason` | Human-readable reason for the current assurance outcome |
| `expression.context.targets` | Runtime targets used to interpret observations |
| `expression.context.constraints` | Location/service/priority/redundancy context where needed |
| `expression.context.preferences` | Preference context where useful for downstream decisions |
| `current.resources` | Full observed resource/path set in the IA assurance scope, mirroring `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[]` |
| `references` | Correlation and external resource references |

Reusable resource entries use `roles`, `resourceId`, `resourceType`, `resourceClass`, direct safe resource attributes such as `accessTechnology` where needed, `relationships`, and `metrics`.

Metric names are neutral and use names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`. Do not use metric origin wrappers or context-encoded field names such as `metrics.benchmark`, `metrics.telemetry`, `latencyBenchmarkMs`, `currentLatencyMs`, or `observedLatencyMs` in `IntentAssuranceEvent`.

Drift/degradation is represented through `IntentAssuranceEvent.lifecycleStatus`, `statusReason`, `expression.context`, and resource-level `metrics` in `current.resources`. IA MS does not include raw callback payloads, raw telemetry dumps, optimiser scoring, solver internals, `provider`, `current.evaluations`, `body.evaluations`, default `requiresReoptimisation`, `selectionStatus`, `assuranceStatus`, or a default `candidates` block in `IntentAssuranceEvent`.

For `Active`, `Degraded`, and `Failed`, `current.resources[]` should carry the full observer scope where applicable. `lifecycleStatus` and `statusReason` explain the interpreted outcome; each resource entry remains factual.

`IntentAssuranceEvent` is metrics-first by default. Do not include `current.evaluations` or `body.evaluations` unless a future policy explicitly requires derived evaluation objects. `lifecycleStatus` and `statusReason` explain the outcome; resource-level `metrics` provide the factual observed data needed by IC MS, II MS, and authorised decision components.

## 10. Observation endpoint baseline:

IA MS obtains runtime metrics from observability/observation endpoints. The observation endpoints are informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration`.

IA evaluates returned metric facts against resolved runtime targets and the IA stored applied assurance baseline. KP/rules may support mapping and evaluation policy but are not the source of truth for every assurance decision.

## 11. Observation gap and DLQ baseline:

IA MS must treat observation collection gaps as explicit operational facts. If the observability platform is unavailable, returns incomplete data, or returns stale observations beyond the configured freshness window, IA MS must not infer a healthy `Active` state from missing telemetry. IA MS should retry according to platform policy, retain the previous assurance state where safe, and publish or record an operational gap outcome where policy requires.

DLQ handling is a required minimum baseline for exhausted `IntentNetworkReadyEvent` and `IntentCallbackEvent` processing, unknown `intentId`, unknown or unmapped `sourceState.state`, invalid event shape, stale or superseded version handling that cannot be safely ignored, and repeated observation collection failures after retry policy is exhausted.

## 12. Final baseline statement:

IA MS is the runtime assurance truth service.

It consumes `IntentNetworkReadyEvent`, `IntentCallbackEvent`, and observation facts only; rejects stale or superseded event versions where needed; maps raw callback state; evaluates runtime observations against resolved runtime targets and the stored applied assurance baseline; and emits curated generic `IntentAssuranceEvent` outcomes. IC MS consumes `IntentAssuranceEvent` to project external TMF-compliant `Intent` lifecycle and `IntentReport` resources.

