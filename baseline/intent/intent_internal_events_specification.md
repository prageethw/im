# intent_internal_events_specification.md

## IA-related event alignment update

This file keeps the broader internal event catalogue, but the IA-related baseline is updated as follows.

## IntentOptimisedEvent

### Producer

```text
intent-optimiser-ms
```

### Current primary consumer

```text
downstream orchestration / service-ready preparation path
```

### Meaning

Optimisation completed and selected resources/outcome are available for downstream service-ready preparation.

### Event-specific rules

- `IntentOptimisedEvent` is not an IA MS input in the active IA baseline.
- IA MS must not list `IntentOptimisedEvent` as a consumed input.
- Where the event carries resolved runtime context, use `body.context.targets`, `body.context.constraints`, and `body.context.preferences`.
- Use `resources` for optimiser-selected resources.
- Use optimiser statuses such as `COMPLETED`, `INFEASIBLE`, and `FAILED`.
- Do not include optimiser objective/rule configuration in the event; optimiser owns that internally.

---

## IntentNetworkReadyEvent

### Producer

```text
intent-intelligence-ms
```

### Current primary consumer

```text
intent-assurance-ms
```

### Meaning

`IntentNetworkReadyEvent` is an internal milestone event indicating that the service configuration/resource set has been prepared for orchestration/apply.

It does not mean the service has already been applied.

### Event-specific rules

- `IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.
- Current consumer is `intent-assurance-ms`.
- Consumer identity does not change producer ownership.
- IA MS consumes this event; IA MS must not produce it.
- `IntentNetworkReadyEvent` means service configuration is ready for orchestration/apply, not that apply has succeeded.
- Use `serviceConfiguration.orchestratorConfiguration` for apply/orchestration details.
- Use `serviceConfiguration.observerConfiguration` for assurance/monitoring details.
- Do not include `applyOutcome`.

---

## IntentCallbackEvent

### Producer

```text
intent-callback-ms
```

### Current primary consumer

```text
intent-assurance-ms
```

### Meaning

Accepted raw callback relayed to the internal event backbone.

### Event-specific rules

Use canonical callback fields:

- `callbackSource`
- `callbackTimestamp`
- `sourceState`

`sourceState.state` carries the raw source/orchestrator state value.

Do not use `orchestratorState`, `orchestratorSource`, or `orchestratorTimestamp` as the baseline callback field names.

ICB MS owns callback ingestion and raw callback event publication. IA MS owns callback meaning/lifecycle mapping.

---

## IntentAssuranceEvent

### Producer

```text
intent-assurance-ms
```

### Current primary consumer

```text
intent-controller-ms
```

### Meaning

IA MS reports curated assurance/apply/runtime outcome truth. IC MS consumes this event and updates the external `Intent` and `IntentReport` projections.

### Generic payload model

`IntentAssuranceEvent` uses a top-level `body` object with:

- `context`
- `current.resources` for normal/active states
- `candidates` for degraded/failed re-decision states
- `references`

Reusable resource entries use:

- `roles`
- `resourceId`
- `resourceType`
- `resourceClass`
- `resourceAttributes`
- `relationships`
- `metrics`

Current runtime metric names use `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.

Benchmark context may use `latencyBenchmarkMs`, `availabilityBenchmarkPercent`, `jitterBenchmarkMs`, and `packetLossBenchmarkPercent`.

For `Degraded` and `Failed`, `candidates` represents all applicable available resources known in the assurance/re-decision context at emission time, after applicable scope/policy filtering.

This includes the currently used/degraded resource and available alternatives. Candidate-level `selectionStatus` and `assuranceStatus` identify current, available, healthy, degraded, failed, or unavailable resources.

For `Active`, `current.resources` remains acceptable because there is no re-decision pressure. For `Terminated`, candidates are normally not needed unless reporting final resources.

`requiresReoptimisation` is not included by default. II MS or another authorised decision component derives the next action from lifecycleStatus, statusReason, resource metrics, and candidates.

### Event-specific rules

- `IntentAssuranceEvent` is the single IA-owned runtime assurance outcome event.
- `IntentDriftOccurredEvent` is retired and must not be used.
- Use `lifecycleStatus` and `statusReason` for lifecycle-driving state.
- Use `context.targets`, `context.constraints`, and `context.preferences` where useful for downstream projection and decision logic.
- Use `current.resources` for current assurance facts in normal/active states.
- Use `candidates` for re-decision support where authorised.
- Do not include `current.evaluations` or `body.evaluations` by default.
- Do not include raw callback payloads, raw telemetry dumps, optimiser scoring, solver internals, or external TMF `IntentExpression` wrappers.
