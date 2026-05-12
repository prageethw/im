# intent_internal_events_specification.md

## Intent internal events specification

### Purpose

This document defines the current baseline internal event contracts for the Intent Enabler workflow.

Internal events are platform events exchanged between Intent Enabler microservices and internal platform components. They are not external TMF listener events.

### Event style

Internal events use CloudEvents-style metadata in transport headers and a plain JSON body. The JSON payload uses a top-level `body` object.

Internal events are state/progress/outcome facts, not point-to-point commands for one specific consumer.

### Common internal event rules

| **Rule** | **Baseline** |
|---|---|
| Delivery model | At-least-once |
| Consumer behaviour | Idempotent consumption required |
| Deduplication key | `ce-id` / `eventId` |
| Correlation | `correlationId` must be propagated |
| Kafka key | Prefer `intentId` for intent-scoped events |
| Payload style | Plain JSON body with CloudEvents metadata in transport headers |
| Event naming | Use final baselined event names exactly |
| Schema evolution | Additive changes preferred; breaking changes require versioning |
| Sensitive data | Do not include secrets, tokens, credentials, or raw internal stack traces |
| External exposure | Internal payloads are not directly exposed as external TMF events |

### Stable event ontology rule

Internal events are not raw KP-schema projections.

Internal events use stable shared intent-domain terms. Domain-specific KP structures may vary, and II MS maps domain KP knowledge into the stable internal event contract.

Internal events may use a plain `body.context` object where they carry resolved runtime targets, constraints, and preferences. This is not the external TMF `Intent.expression` wrapper.

For IA, optimisation, and assurance flows where a resolved runtime context is being carried, use:

- `body.context.targets`
- `body.context.constraints`
- `body.context.preferences`

For simpler semantic rejection/admission events, direct fields may be used where already baselined. Do not use external TMF `IntentExpression` wrappers inside internal events.

### Service configuration structure rule

In `IntentNetworkReadyEvent.serviceConfiguration`, use:

- `orchestratorConfiguration.target`
- `orchestratorConfiguration.profile`
- `orchestratorConfiguration.resources`
- `observerConfiguration.target`
- `observerConfiguration.profile`
- `observerConfiguration.resourceIds`

Do not repeat `orchestrator` or `observer` prefixes inside their own configuration blocks.

### Service-ready configuration rule

`IntentNetworkReadyEvent` means the service configuration has been prepared for orchestration/apply. It does not mean the service has already been applied.

Use `serviceConfiguration` to carry the service apply and observation plan.

`serviceConfiguration.orchestratorConfiguration.resources` contains the selected resources ready for apply.

`serviceConfiguration.observerConfiguration.resourceIds` contains all KP resource IDs for the location/service that IA/observer should monitor.

Apply success/failure is confirmed later through callback and assurance processing, then projected through `IntentAssuranceEvent`.

---

## Common CloudEvents headers

```http
ce-specversion: 1.0
ce-type: IntentValidatedEvent
ce-source: intent-controller-ms
ce-id: evt-intent-validated-001
ce-time: 2026-04-18T12:00:01+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

---

## Internal event catalogue

| **Event** | **Producer** | **Current primary consumer(s)** | **Purpose** |
|---|---|---|---|
| `IntentValidatedEvent` | `intent-controller-ms` | `intent-intelligence-ms` | Runtime Intent passed IC MS admission validation and was admitted into the lifecycle |
| `IntentRejectedEvent` | `intent-intelligence-ms` | `intent-controller-ms` | Semantic/policy validation rejected the admitted Intent |
| `IntentResolvedEvent` | `intent-intelligence-ms` | `intent-optimiser-ms` | Intent was semantically resolved into a canonical internal handoff with available resources for optimisation |
| `IntentOptimisedEvent` | `intent-optimiser-ms` | `intent-assurance-ms` / downstream orchestration path | Optimisation completed and selected resources/outcome are available |
| `IntentNetworkReadyEvent` | `intent-intelligence-ms` | `intent-assurance-ms` | Optimised/service-ready configuration is available for orchestration/apply observation; apply success is not yet confirmed |
| `IntentAssuranceEvent` | `intent-assurance-ms` | `intent-controller-ms` / authorised decision components | Assurance/apply/runtime outcome truth for external Intent and IntentReport projection |
| `IntentCallbackEvent` | `intent-callback-ms` | `intent-assurance-ms` | Accepted raw orchestrator callback relayed to the internal event backbone |

---

## IntentValidatedEvent

### Producer

```text
intent-controller-ms
```

### Current primary consumer

```text
intent-intelligence-ms
```

### Meaning

The runtime Intent has passed IC MS admission validation and has been admitted into the intent lifecycle.

### Event-specific rules

- `IntentValidatedEvent` is the lean IC MS admission-focused event.
- It carries the admitted runtime expression.
- The admitted expression uses the shared semantic buckets: `targets`, `constraints`, and `preferences`.
- It includes `serviceType`.
- It keeps `redundancyRequired` under `expression.constraints` when it came from expression mapping/defaults.
- It does not include KP `benchmarks`, optimiser details, orchestration details, assurance details, or a `validation` object.

---

## IntentRejectedEvent

### Producer

```text
intent-intelligence-ms
```

### Current primary consumer

```text
intent-controller-ms
```

### Meaning

Semantic, policy, or downstream interpretation validation rejected the admitted Intent.

### Event-specific rules

- `IntentRejectedEvent` is the semantic/policy/capability rejection event.
- For simple semantic/capability rejection, carry `lifecycleStatus`, `reasonCode`, `statusReason`, direct `location`, `serviceType`, `serviceClass`, and references.
- Do not include optimiser, orchestration, or assurance payloads.

---

## IntentResolvedEvent

### Producer

```text
intent-intelligence-ms
```

### Current primary consumer

```text
intent-optimiser-ms
```

### Meaning

The admitted Intent has been semantically resolved into a canonical internal handoff that can be optimised.

### Event-specific rules

- `IntentResolvedEvent` is the lean optimiser handoff.
- It may use direct `location`, `serviceType`, and `serviceClass` fields where already baselined for optimiser handoff.
- It uses `targets` for measurable SLA-style objectives.
- It uses `constraints` for hard non-target inputs such as `priority` and `redundancyRequired`.
- It uses `preferences` for soft selection guidance such as `preferredAccessTechnology`.
- It must not be listed as an IA MS input.

---

## IntentOptimisedEvent

### Producer

```text
intent-optimiser-ms
```

### Current primary consumer

```text
intent-assurance-ms
```

### Meaning

Optimisation completed and selected resources/outcome are available for downstream apply/assurance processing.

### Event-specific rules

- Use `body.context.targets`, `body.context.constraints`, and `body.context.preferences` for resolved runtime context.
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

`IntentNetworkReadyEvent` is an internal milestone event indicating that the service configuration/resource set has been prepared for orchestration/apply. It does not mean the service has already been applied.

### Example headers

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-network-ready-001
ce-time: 2026-04-18T12:12:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "InProgress",
    "statusReason": "Service configuration has been prepared for orchestration/apply.",
    "context": {
      "constraints": {
        "location": {
          "locationId": "AU-NSW-SYD-HOSP-001",
          "displayName": "Sydney-Main-Hospital"
        },
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold"
      }
    },
    "serviceConfiguration": {
      "orchestratorConfiguration": {
        "target": "t7-network-orchestrator",
        "profile": "hospital-surgical-slice-apply-v1",
        "resources": [
          {
            "role": "primary",
            "resourceId": "SYD-PRI-01"
          },
          {
            "role": "secondary",
            "resourceId": "SYD-SEC-01"
          }
        ]
      },
      "observerConfiguration": {
        "target": "t7-observability-platform",
        "profile": "critical-gold-assurance-observation-v1",
        "resourceIds": [
          "SYD-PRI-01",
          "SYD-PRI-02",
          "SYD-SEC-01",
          "SYD-SEC-02"
        ]
      }
    },
    "references": {
      "correlationId": "corr-intent-create-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      }
    }
  }
}
```

### Event-specific rules

- `IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.
- Current consumer is `intent-assurance-ms`.
- Consumer identity does not change producer ownership.
- IA MS consumes this event; IA MS must not produce it.
- `IntentNetworkReadyEvent` means service configuration is ready for orchestration/apply, not that apply has succeeded.
- Use `serviceConfiguration` because the event carries the service apply and observation plan rather than low-level network configuration.
- Use `serviceConfiguration.orchestratorConfiguration` for apply/orchestration details.
- Use `serviceConfiguration.observerConfiguration` for assurance/monitoring details.
- Do not include `applyOutcome`.

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

For `Degraded` and `Failed`, `candidates` represents all applicable available resources known in the assurance/re-decision context at emission time, after applicable scope/policy filtering. This includes the currently used/degraded resource and available alternatives. Candidate-level `selectionStatus` and `assuranceStatus` identify current, available, healthy, degraded, failed, or unavailable resources.

For `Active`, `current.resources` remains acceptable because there is no re-decision pressure. For `Terminated`, candidates are normally not needed unless reporting final resources.

`requiresReoptimisation` is not included by default. II MS or another authorised decision component derives the next action from lifecycleStatus, statusReason, resource metrics, and candidates.

### Event-specific rules

- `IntentAssuranceEvent` is the single IA-owned runtime assurance outcome event.
- `IntentDriftOccurredEvent` is retired and must not be used.
- Use `lifecycleStatus` and `statusReason` for lifecycle-driving state.
- Use `context.targets`, `context.constraints`, and `context.preferences` where useful for downstream projection and decision logic.
- Use `current.evaluations` and `current.resources` for current assurance facts.
- Use `candidates` for re-decision support where authorised.
- Do not include raw callback payloads, raw telemetry dumps, optimiser scoring, solver internals, or external TMF `IntentExpression` wrappers.

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

Accepted raw orchestrator callback relayed to the internal event backbone.

### Event-specific rules

- Use canonical callback fields:
  - `orchestratorState`
  - `orchestratorSource`
  - `orchestratorTimestamp`
- Do not use older callback fields such as `callbackSource`, `callbackTimestamp`, or `sourceState.state`.
- ICB MS owns callback ingestion and raw callback event publication.
- IA MS owns callback meaning/lifecycle mapping.


### Metrics-first assurance rule

`IntentAssuranceEvent` does not include `current.evaluations` or `body.evaluations` by default. Use `lifecycleStatus`, `statusReason`, resource-level `metrics`, `selectionStatus`, and `assuranceStatus` as the default fact model.
