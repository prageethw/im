# intent_internal_events_specification.md

## Intent internal events specification:

### Purpose:

This document defines the current baseline internal event contracts for the Intent Enabler workflow.

Internal events are platform events exchanged between Intent Enabler microservices and internal platform components.

They are not external TMF listener events.

### Event style:

Internal events use CloudEvents-style metadata in transport headers and a plain JSON body.

The JSON payload uses a top-level `body` object.

Internal events are state/progress/outcome facts, not point-to-point commands for one specific consumer.

### Common internal event rules:

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


### Lean internal payload rule:

Internal events should carry milestone-specific fields directly and avoid embedding full external TMF resource objects unless the consumer genuinely needs that full resource snapshot.

Use top-level event-body fields for the event fact, such as `intentId`, `version`, `lifecycleStatus`, `statusReason`, and milestone-specific outcomes.

Use `references` for links/hrefs and related resource references instead of duplicating IDs, version, lifecycle, and resource metadata inside embedded external resource objects.

This keeps each internal event lean and avoids duplicate truth.

### Request ID reference rule:

Use `correlationId` as the standard cross-service trace/correlation reference in internal event examples.

Do not include `sourceRequestId` in internal event examples unless a request-ID propagation model is explicitly baselined later.

---

## Common CloudEvents headers:

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

## Internal event catalogue:

| **Event** | **Producer** | **Current primary consumer(s)** | **Purpose** |
|---|---|---|---|
| `IntentValidatedEvent` | `intent-controller-ms` | `intent-intelligence-ms` | Runtime Intent passed IC MS syntactic validation and was admitted into the lifecycle |
| `IntentRejectedEvent` | `intent-intelligence-ms` | `intent-controller-ms` | Semantic/policy validation rejected the admitted Intent |
| `IntentResolvedEvent` | `intent-intelligence-ms` | `intent-optimiser-ms` | Intent was semantically resolved into a canonical internal request for optimisation |
| `IntentOptimisedEvent` | `intent-optimiser-ms` | `intent-assurance-ms` / downstream orchestration path | Optimisation completed and selected resources/outcome are available |
| `IntentNetworkReadyEvent` | `intent-assurance-ms` / network apply path | `intent-controller-ms` / assurance projection path | Optimised intent has been successfully applied and the network/service is ready |
| `IntentAssuranceEvent` | `intent-assurance-ms` | `intent-controller-ms` | Assurance/apply/runtime outcome truth for external Intent and IntentReport projection |
| `IntentCallbackEvent` | `intent-callback-ms` | `intent-assurance-ms` | Accepted raw orchestrator callback relayed to the internal event backbone |

---

## IntentValidatedEvent:

### Producer:

```text
intent-controller-ms
```

### Current primary consumer:

```text
intent-intelligence-ms
```

### Meaning:

The runtime Intent has passed IC MS syntactic validation and has been admitted into the intent lifecycle.

This event is a state/progress event, not a point-to-point command.

### Example headers:

```http
ce-specversion: 1.0
ce-type: IntentValidatedEvent
ce-source: intent-controller-ms
ce-id: evt-intent-validated-001
ce-time: 2026-04-18T12:00:01+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Acknowledged",
    "statusReason": "Intent request passed IC MS syntactic validation and was admitted for downstream processing.",
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.20"
    },
    "expression": {
      "...similar payload to create intent request..."
    },
    "validation": {
      "result": "Passed",
      "validationType": "Syntactic",
      "validatedBy": "intent-controller-ms"
    },
    "references": {
      "intent": {
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      },
      "correlationId": "corr-intent-create-001"
    }
  }
}
```

### Notes:

- IC MS emits this only after the external Intent projection and outbox record are durably committed.
- The referenced `IntentSpecification.id` is concrete and must have been confirmed `ACTIVE` or validated from a valid fresh cached active spec.
- The payload is curated for downstream processing and does not expose DB/cache/internal implementation details.

---

## IntentRejectedEvent:

### Producer:

```text
intent-intelligence-ms
```

### Current primary consumer:

```text
intent-controller-ms
```

### Meaning:

Semantic, policy, or downstream interpretation validation rejected the admitted Intent.

IC MS consumes this event and projects the external Intent lifecycle/status to `Rejected`.

### Example headers:

```http
ce-specversion: 1.0
ce-type: IntentRejectedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-rejected-001
ce-time: 2026-04-18T12:01:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Rejected",
    "reasonCode": "SEMANTIC_LOCATION_UNSUPPORTED",
    "statusReason": "Requested hospital location is not currently supported for this service class.",
    "evaluations": [
      {
        "type": "Semantic",
        "result": "Failed",
        "reasonCode": "SEMANTIC_LOCATION_UNSUPPORTED",
        "message": "The requested location could not be resolved to a supported service location."
      }
    ],
    "references": {
      "correlationId": "corr-intent-create-001",
      "intentSpecificationId": "hospital-surgical-slice-spec-v1.20"
    }
  }
}
```

---

## IntentResolvedEvent:

### Producer:

```text
intent-intelligence-ms
```

### Current primary consumer:

```text
intent-optimiser-ms
```

### Meaning:

The admitted Intent has been semantically resolved into a canonical internal request that can be optimised.

### Example headers:

```http
ce-specversion: 1.0
ce-type: IntentResolvedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-resolved-001
ce-time: 2026-04-18T12:03:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "InProgress",
    "site": {
      "locationId": "sydney-hospital"
    },
    "service": {
      "serviceClass": "critical-gold"
    },
    "targets": {
      "maxLatencyMs": 10,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "request": {
      "priority": "critical",
      "redundancyRequired": true,
      "preferredAccessTechnology": "5G"
    },
    "inputs": {
      "knowledgeSource": "t7.knowledge plane",
      "resolutionProfile": "hospital-surgical-slice"
    },
    "candidates": [
      "...candidate resources resolved from knowledge plane..."
    ],
    "evaluations": [
      {
        "type": "Semantic",
        "result": "Passed"
      },
      {
        "type": "Policy",
        "result": "Passed"
      }
    ],
    "references": {
      "correlationId": "corr-intent-create-001",
      "intentSpecificationId": "hospital-surgical-slice-spec-v1.20",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      }
    }
  }
}
```

---

## IntentOptimisedEvent:

### Producer:

```text
intent-optimiser-ms
```

### Current primary consumer:

```text
intent-assurance-ms
```

### Meaning:

Optimisation completed and selected resources/outcome are available for downstream apply/assurance processing.

### Allowed optimisation outcome statuses:

```text
Optimised
NotOptimisable
Error
```

### Example headers:

```http
ce-specversion: 1.0
ce-type: IntentOptimisedEvent
ce-source: intent-optimiser-ms
ce-id: evt-intent-optimised-001
ce-time: 2026-04-18T12:05:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "site": {
      "locationId": "sydney-hospital"
    },
    "service": {
      "serviceClass": "critical-gold"
    },
    "resources": [
      {
        "roles": [
          "primary"
        ],
        "resourceId": "path-syd-hosp-5g-primary",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "5G"
        },
        "relationships": [
          {
            "type": "backup",
            "resourceId": "path-syd-hosp-fibre-backup"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 8,
          "expectedAvailabilityPercent": 99.995,
          "expectedJitterMs": 1.5,
          "expectedPacketLossPercent": 0.005
        }
      }
    ],
    "optimisationOutcome": {
      "status": "Optimised",
      "statusReason": "Optimisation completed and selected a compliant primary/backup resource set."
    },
    "evaluations": [
      {
        "name": "latency",
        "result": "Compliant",
        "target": 10,
        "expectedValue": 8
      }
    ],
    "references": {
      "correlationId": "corr-intent-create-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecificationId": "hospital-surgical-slice-spec-v1.20"
    }
  }
}
```

### Notes:

- Use `resources`, not `selectedResources` or `selected`.
- If optimisation cannot produce a valid result, use `optimisationOutcome.status = NotOptimisable` or `Error`.

---


## IntentNetworkReadyEvent:

### Producer:

```text
intent-assurance-ms / network apply path
```

### Current primary consumer:

```text
intent-controller-ms
```

### Meaning:

`IntentNetworkReadyEvent` is an internal milestone event indicating that the optimised intent has been successfully applied and the network/service is ready.

It represents a network-ready/apply-success milestone.

`IntentAssuranceEvent` remains the ongoing assurance/runtime outcome event used for active, degraded, failed, paused, and recovered projection updates.

### Example headers:

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-assurance-ms
ce-id: evt-intent-network-ready-001
ce-time: 2026-04-18T12:12:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Active",
    "statusReason": "Optimised intent has been applied and the network service is ready.",
    "site": {
      "locationId": "sydney-hospital"
    },
    "service": {
      "serviceClass": "critical-gold"
    },
    "resources": [
      {
        "roles": [
          "primary"
        ],
        "resourceId": "path-syd-hosp-5g-primary",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "5G"
        },
        "relationships": [
          {
            "type": "backup",
            "resourceId": "path-syd-hosp-fibre-backup"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 8,
          "expectedAvailabilityPercent": 99.995,
          "expectedJitterMs": 1.5,
          "expectedPacketLossPercent": 0.005
        }
      }
    ],
    "applyOutcome": {
      "status": "Applied",
      "statusReason": "Network orchestrator confirmed successful apply."
    },
    "references": {
      "correlationId": "corr-intent-create-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecificationId": "hospital-surgical-slice-spec-v1.20"
    }
  }
}
```

### Notes:

- `IntentNetworkReadyEvent` is a milestone event, not an ongoing telemetry event.
- IC MS may use this event to project the external Intent lifecycle to `Active` where that is the selected flow.
- IA MS may also use this milestone as part of its assurance state model.
- Ongoing assurance updates, degradation, recovery, pause, and failure signals should use `IntentAssuranceEvent`.

## IntentAssuranceEvent:

### Producer:

```text
intent-assurance-ms
```

### Current primary consumer:

```text
intent-controller-ms
```

### Meaning:

IA MS reports curated assurance/apply/runtime outcome truth.

IC MS consumes this event and updates the external `Intent` and `IntentReport` projections.

### Example body — active outcome:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v2",
    "lifecycleStatus": "Active",
    "statusReason": "Intent version v2 is active and assurance is healthy.",
    "assuranceStatus": "Healthy",
    "service": {
      "serviceClass": "critical-gold"
    },
    "location": {
      "locationId": "sydney-hospital"
    },
    "metrics": {
      "latencyMs": 8,
      "availabilityPercent": 99.995,
      "jitterMs": 1.5,
      "packetLossPercent": 0.005
    },
    "evaluations": [
      {
        "name": "latency",
        "result": "Compliant",
        "observedValue": 8,
        "threshold": 10
      }
    ],
    "references": {
      "correlationId": "corr-intent-assurance-001",
      "intentSpecificationId": "hospital-surgical-slice-spec-v1.20"
    }
  }
}
```

### Example body — degraded outcome:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v2",
    "lifecycleStatus": "Degraded",
    "statusReason": "Latency assurance is degraded.",
    "assuranceStatus": "Degraded",
    "metrics": {
      "latencyMs": 18,
      "availabilityPercent": 99.99
    },
    "evaluations": [
      {
        "name": "latency",
        "result": "NonCompliant",
        "observedValue": 18,
        "threshold": 10
      }
    ],
    "references": {
      "correlationId": "corr-intent-assurance-002",
      "intentSpecificationId": "hospital-surgical-slice-spec-v1.20"
    }
  }
}
```

### Notes:

- IC MS processes `IntentAssuranceEvent` idempotently through inbox handling.
- IC MS updates the current projected external `Intent` resource.
- IC MS creates or updates the `IntentReport` projection.
- Raw telemetry remains outside IC MS; IC MS consumes curated assurance outcomes.

---

## IntentCallbackEvent:

### Producer:

```text
intent-callback-ms
```

### Current primary consumer:

```text
intent-assurance-ms
```

### Topic:

```text
t7.intent.management.events.callbacks
```

### Kafka key:

```text
intentId
```

### CloudEvents type:

```text
au.com.mycsp.intent.callback.v1
```

### Meaning:

ICB MS publishes accepted raw callbacks to Kafka as `IntentCallbackEvent`.

IA MS consumes this event, validates/correlates intent state, maps raw orchestrator state into lifecycle/assurance meaning, and emits assurance outcomes where applicable.

### Example headers:

```http
ce-specversion: 1.0
ce-type: au.com.mycsp.intent.callback.v1
ce-source: intent-callback-ms
ce-id: evt-intent-callback-001
ce-time: 2026-04-18T12:15:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body:

```json
{
  "body": {
    "eventType": "IntentCallbackEvent",
    "eventVersion": "1.0",
    "source": "intent-callback-ms",
    "eventTime": "2026-04-18T12:15:00+10:00",
    "correlationId": "corr-intent-callback-001",
    "intentId": "INT-HOSP-2026-001",
    "orchestratorState": {
      "state": "APPLIED",
      "details": {
        "...raw orchestrator callback payload..."
      }
    },
    "orchestratorSource": "t7.orchestrator",
    "orchestratorTimestamp": "2026-04-18T12:14:58+10:00"
  }
}
```

### ICB MS ownership boundary:

ICB MS does not validate intent existence, map orchestrator state, derive orchestrator type, decide actionability, or emit assurance/lifecycle events.

IA MS owns correlation, mapping, skip/dead-letter decisions, and downstream assurance outcome publication.

---

## Idempotency and replay:

| **Requirement** | **Producer baseline** |
|---|---|
| Stable event ID | Required |
| Correlation ID | Required |
| Intent ID | Required for intent-scoped events |
| Outbox publication | Required where event publication follows DB state change |
| At-least-once safe | Required |

| **Requirement** | **Consumer baseline** |
|---|---|
| Idempotent processing | Required |
| Inbox/dedup store | Recommended/required for state-changing consumers |
| Duplicate event handling | Safe no-op or idempotent update |
| Ordering assumption | Do not rely only on broker ordering for correctness |
| Stale event handling | Detect using version/state/timestamp where applicable |

---

## Topic/key baseline:

| **Event** | **Suggested topic** | **Kafka key** |
|---|---|---|
| `IntentValidatedEvent` | `t7.intent.management.events` | `intentId` |
| `IntentRejectedEvent` | `t7.intent.management.events` | `intentId` |
| `IntentResolvedEvent` | `t7.intent.management.events` | `intentId` |
| `IntentOptimisedEvent` | `t7.intent.management.events` | `intentId` |
| `IntentNetworkReadyEvent` | `t7.intent.management.events` | `intentId` |
| `IntentAssuranceEvent` | `t7.intent.management.events` | `intentId` |
| `IntentCallbackEvent` | `t7.intent.management.events.callbacks` | `intentId` |

---

## Final notes:

- Internal events are not external TMF events.
- External TMF events must be curated projection/resource events.
- Internal events must not leak secrets, credentials, tokens, or raw platform stack traces.
- Use `intent-intelligence-ms`, not `intent-interpreter-ms`.
- Use `intent-controller-ms`, not `intent-creation-ms`.
- Use `priority`, not `priority_level`.
- Use `critical`, not `clinical-critical`.
- Use `resources` for selected optimisation resources in `IntentOptimisedEvent`.
- Use typed placeholders in examples when abbreviating arrays or objects.
- Internal event payloads should be lean and avoid embedding full external TMF resource objects unless genuinely required by consumers.
