# intent_internal_events_specification.md

## Intent internal events specification

### Purpose

This document defines the current baseline internal event contracts for the Intent Enabler workflow.

Internal events are platform events exchanged between Intent Enabler microservices and internal platform components. They are not external TMF listener events.

### Event style

Internal events use CloudEvents-style metadata in transport headers and a plain JSON body.

The JSON payload uses a top-level `body` object.

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

### Lean internal payload rule

Internal events should carry milestone-specific fields directly and avoid embedding full external TMF resource objects unless the consumer genuinely needs that full resource snapshot.

Use top-level event-body fields for the event fact, such as `intentId`, `version`, `lifecycleStatus`, `statusReason`, and milestone-specific outcomes.

Use `references` for links/hrefs and related resource references instead of duplicating IDs, version, lifecycle, and resource metadata inside embedded external resource objects.

### Standard correlation rule

Use `correlationId` as the standard cross-service trace/correlation reference in internal event examples.

No additional request-id reference field is baselined by default.

### IntentValidatedEvent admission rule

Do not include a validation object in `IntentValidatedEvent`.

The event is emitted only after IC MS admission validation succeeds, so successful validation is implied by the event itself.

If validation fails, IC MS returns a synchronous API validation error and does not emit `IntentValidatedEvent`.

### Shared terminology rule

Use agreed intent-domain terminology consistently across internal events.

Use `location.locationId`, not a separate site block, unless a future event explicitly baselines a separate concept from `location`.

### Common references shape

Internal event `references` should use named resource reference objects with `id` and `href` where available.

Use `correlationId` as a common scalar reference.

Recommended shape:

```json
{
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
```

Where a reference is not useful to the consuming event, it may be omitted rather than included as an empty object.

### IntentResolvedEvent handoff content rule

For `IntentResolvedEvent`, use `context` for non-measurable contextual attributes such as `priority`, `redundancyRequired`, and `preferredAccessTechnology`.

Do not use a generic HTTP/request-shaped block for this context.

Do not include optimiser input-selection details or successful semantic/policy evaluation details in `IntentResolvedEvent` by default.

II MS emits `IntentResolvedEvent` only when semantic/policy resolution succeeds, so successful evaluation is implied by the event itself.

The optimiser owns its optimisation data-source, model, and method selection unless an explicit optimisation-profile handoff is baselined later.

Use `t7-knowledge-plane` as the standard service-style name where the Knowledge Plane must be referenced.

### Candidate resource example rule

`IntentResolvedEvent.candidates` should show the concrete reusable resource-entry shape in the main example.

Use `roles`, `resourceId`, `resourceType`, `resourceClass`, `resourceAttributes`, `relationships`, and `metrics`.

Use simple role names such as `primary` and `secondary`.

The main example should include at least two primary candidate paths and two secondary candidate paths so it is clear that the optimiser has a real candidate set to choose from.

Avoid placeholder-only candidates arrays in the main event example.

### Expression example rule

When `IntentValidatedEvent.expression` is shown in the main example, include a concrete expression sample rather than a placeholder-only object.

The expression sample should match the runtime Intent create request shape and preserve the same field names used by IC MS and the active `IntentSpecification`.

### Optimiser status and evaluation rule

Use optimiser statuses as the primary outcome for the optimisation run, target evaluations, and context evaluations.

Supported statuses:

```text
ACKNOWLEDGED
QUEUED
PROCESSING
COMPLETED
INFEASIBLE
FAILED
CANCELLING
CANCELLED
```

Do not add a separate `result` field by default.

`COMPLETED` means the item was successfully evaluated and satisfied.

`INFEASIBLE` means the item was evaluated but cannot be satisfied with the available candidates/constraints.

`FAILED` means technical/runtime/model/data failure.

The same status vocabulary may be applied at overall optimisation-run level, individual target-evaluation level, and context-evaluation level.


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
| `IntentResolvedEvent` | `intent-intelligence-ms` | `intent-optimiser-ms` | Intent was semantically resolved into a canonical internal handoff for optimisation |
| `IntentOptimisedEvent` | `intent-optimiser-ms` | `intent-assurance-ms` / downstream orchestration path | Optimisation completed and selected resources/outcome are available |
| `IntentNetworkReadyEvent` | `intent-assurance-ms` / network apply path | `intent-controller-ms` / assurance projection path | Optimised intent has been successfully applied and the network/service is ready |
| `IntentAssuranceEvent` | `intent-assurance-ms` | `intent-controller-ms` | Assurance/apply/runtime outcome truth for external Intent and IntentReport projection |
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

This event is a state/progress event, not a point-to-point command.

### Example headers

```http
ce-specversion: 1.0
ce-type: IntentValidatedEvent
ce-source: intent-controller-ms
ce-id: evt-intent-validated-001
ce-time: 2026-04-18T12:00:01+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Acknowledged",
    "statusReason": "Intent request passed IC MS admission validation and was admitted for downstream processing.",
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.20"
    },
    "expression": {
      "location": {
        "locationId": "sydney-hospital",
        "locationType": "hospital",
        "geographicScope": "campus"
      },
      "serviceClass": "critical-gold",
      "priority": "critical",
      "maxLatencyMs": 10,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01,
      "redundancyRequired": true,
      "preferredAccessTechnology": "5G",
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
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

### Notes

- IC MS emits this only after the external Intent projection and outbox record are durably committed.
- The referenced `IntentSpecification.id` is concrete and must have been confirmed `ACTIVE` or validated from a valid fresh cached active spec.
- The event itself implies admission validation success.
- The payload is curated for downstream processing and does not expose DB/cache/internal implementation details.

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

IC MS consumes this event and projects the external Intent lifecycle/status to `Rejected`.

### Example headers

```http
ce-specversion: 1.0
ce-type: IntentRejectedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-rejected-001
ce-time: 2026-04-18T12:01:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body

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

### Notes

- IC MS consumes this idempotently through inbox handling.
- IC MS emits external `IntentStatusChangeEvent` after the external projection changes to `Rejected`.
- IC MS may create or update an `IntentReport` projection where useful.

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

### Example headers

```http
ce-specversion: 1.0
ce-type: IntentResolvedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-resolved-001
ce-time: 2026-04-18T12:03:00+10:00
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
    "location": {
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
    "context": {
      "priority": "critical",
      "redundancyRequired": true,
      "preferredAccessTechnology": "5G"
    },
    "candidates": [
      {
        "roles": [
          "primary"
        ],
        "resourceId": "path-syd-hosp-5g-primary-a",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "5G",
          "provider": "mobile-access-a"
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "path-syd-hosp-fibre-secondary-a"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 8,
          "expectedAvailabilityPercent": 99.995,
          "expectedJitterMs": 1.5,
          "expectedPacketLossPercent": 0.005
        }
      },
      {
        "roles": [
          "primary"
        ],
        "resourceId": "path-syd-hosp-fibre-primary-b",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "fibre",
          "provider": "fixed-access-b"
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "path-syd-hosp-5g-secondary-b"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 7,
          "expectedAvailabilityPercent": 99.996,
          "expectedJitterMs": 1.1,
          "expectedPacketLossPercent": 0.004
        }
      },
      {
        "roles": [
          "secondary"
        ],
        "resourceId": "path-syd-hosp-fibre-secondary-a",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "fibre",
          "provider": "fixed-access-a"
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "path-syd-hosp-5g-primary-a"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 9,
          "expectedAvailabilityPercent": 99.997,
          "expectedJitterMs": 1.2,
          "expectedPacketLossPercent": 0.003
        }
      },
      {
        "roles": [
          "secondary"
        ],
        "resourceId": "path-syd-hosp-5g-secondary-b",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "5G",
          "provider": "mobile-access-b"
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "path-syd-hosp-fibre-primary-b"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 10,
          "expectedAvailabilityPercent": 99.994,
          "expectedJitterMs": 1.8,
          "expectedPacketLossPercent": 0.006
        }
      }
    ],
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

### Notes

- Successful semantic/policy resolution is implied by the event.
- The optimiser owns optimisation data-source/model/method selection unless an explicit optimisation-profile handoff is baselined later.
- `context` holds non-measurable contextual attributes.
- `targets` holds measurable desired outcomes/constraints.
- `candidates` carries the candidate resources resolved for optimisation where required.

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

### Allowed optimiser statuses

```text
ACKNOWLEDGED
QUEUED
PROCESSING
COMPLETED
INFEASIBLE
FAILED
CANCELLING
CANCELLED
```

### Example headers

```http
ce-specversion: 1.0
ce-type: IntentOptimisedEvent
ce-source: intent-optimiser-ms
ce-id: evt-intent-optimised-001
ce-time: 2026-04-18T12:05:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "location": {
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
        "resourceId": "path-syd-hosp-fibre-primary-b",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "fibre",
          "provider": "fixed-access-b"
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "path-syd-hosp-5g-secondary-b"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 7,
          "expectedAvailabilityPercent": 99.996,
          "expectedJitterMs": 1.1,
          "expectedPacketLossPercent": 0.004
        }
      },
      {
        "roles": [
          "secondary"
        ],
        "resourceId": "path-syd-hosp-5g-secondary-b",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "5G",
          "provider": "mobile-access-b"
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "path-syd-hosp-fibre-primary-b"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 10,
          "expectedAvailabilityPercent": 99.994,
          "expectedJitterMs": 1.8,
          "expectedPacketLossPercent": 0.006
        }
      }
    ],
    "optimisationRun": {
      "status": "COMPLETED",
      "statusReason": "Optimisation completed and selected a compliant primary/secondary resource set."
    },
    "targetEvaluations": [
      {
        "name": "latency",
        "status": "COMPLETED",
        "target": 10,
        "expectedValue": 7,
        "unit": "ms"
      },
      {
        "name": "availability",
        "status": "COMPLETED",
        "target": 99.99,
        "expectedValue": 99.996,
        "unit": "percent"
      },
      {
        "name": "jitter",
        "status": "COMPLETED",
        "target": 2,
        "expectedValue": 1.1,
        "unit": "ms"
      },
      {
        "name": "packetLoss",
        "status": "COMPLETED",
        "target": 0.01,
        "expectedValue": 0.004,
        "unit": "percent"
      }
    ],
    "contextEvaluations": [
      {
        "name": "redundancyRequired",
        "status": "COMPLETED",
        "target": true,
        "expectedValue": true
      },
      {
        "name": "preferredAccessTechnology",
        "status": "COMPLETED",
        "target": "5G",
        "expectedValue": "fibre",
        "statusReason": "Preferred technology was considered, but fibre primary with 5G secondary produced the best feasible resource set."
      }
    ],
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

### Infeasible optimisation example

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "location": {
      "locationId": "sydney-hospital"
    },
    "service": {
      "serviceClass": "critical-gold"
    },
    "optimisationRun": {
      "status": "INFEASIBLE",
      "statusReason": "No candidate resource set could satisfy all required targets."
    },
    "targetEvaluations": [
      {
        "name": "latency",
        "status": "INFEASIBLE",
        "target": 10,
        "bestExpectedValue": 18,
        "unit": "ms",
        "reasonCode": "OPTIMISATION_LATENCY_UNSATISFIABLE"
      },
      {
        "name": "availability",
        "status": "COMPLETED",
        "target": 99.99,
        "bestExpectedValue": 99.995,
        "unit": "percent"
      }
    ],
    "contextEvaluations": [
      {
        "name": "redundancyRequired",
        "status": "COMPLETED",
        "target": true,
        "expectedValue": true
      }
    ],
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

### Notes

- Use `resources`, not `selectedResources` or `selected`.
- If optimisation cannot produce a valid result, use `optimisationRun.status = INFEASIBLE` when no candidate set can satisfy required targets, or `FAILED` for technical/runtime/model/data failure.

---

## IntentNetworkReadyEvent

### Producer

```text
intent-assurance-ms / network apply path
```

### Current primary consumer

```text
intent-controller-ms
```

### Meaning

`IntentNetworkReadyEvent` is an internal milestone event indicating that the optimised intent has been successfully applied and the network/service is ready.

It represents a network-ready/apply-success milestone.

`IntentAssuranceEvent` remains the ongoing assurance/runtime outcome event used for active, degraded, failed, paused, and recovered projection updates.

### Example headers

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-assurance-ms
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
    "lifecycleStatus": "Active",
    "statusReason": "Optimised intent has been applied and the network service is ready.",
    "location": {
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
        "resourceId": "path-syd-hosp-fibre-primary-b",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "fibre",
          "provider": "fixed-access-b"
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "path-syd-hosp-5g-secondary-b"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 7,
          "expectedAvailabilityPercent": 99.996,
          "expectedJitterMs": 1.1,
          "expectedPacketLossPercent": 0.004
        }
      },
      {
        "roles": [
          "secondary"
        ],
        "resourceId": "path-syd-hosp-5g-secondary-b",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "5G",
          "provider": "mobile-access-b"
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "path-syd-hosp-fibre-primary-b"
          }
        ],
        "metrics": {
          "expectedLatencyMs": 10,
          "expectedAvailabilityPercent": 99.994,
          "expectedJitterMs": 1.8,
          "expectedPacketLossPercent": 0.006
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
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      }
    }
  }
}
```

### Notes

- `IntentNetworkReadyEvent` is a milestone event, not an ongoing telemetry event.
- IC MS may use this event to project the external Intent lifecycle to `Active` where that is the selected flow.
- IA MS may also use this milestone as part of its assurance state model.
- Ongoing assurance updates, degradation, recovery, pause, and failure signals should use `IntentAssuranceEvent`.

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

IA MS reports curated assurance/apply/runtime outcome truth.

IC MS consumes this event and updates the external `Intent` and `IntentReport` projections.

### Example body — active outcome

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

### Example body — degraded outcome

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

### Notes

- IC MS processes `IntentAssuranceEvent` idempotently through inbox handling.
- IC MS updates the current projected external `Intent` resource.
- IC MS creates or updates the `IntentReport` projection.
- Raw telemetry remains outside IC MS; IC MS consumes curated assurance outcomes.

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

### Topic

```text
t7.intent.management.events.callbacks
```

### Kafka key

```text
intentId
```

### CloudEvents type

```text
au.com.mycsp.intent.callback.v1
```

### Meaning

ICB MS publishes accepted raw callbacks to Kafka as `IntentCallbackEvent`.

IA MS consumes this event, validates/correlates intent state, maps raw orchestrator state into lifecycle/assurance meaning, and emits assurance outcomes where applicable.

### Example headers

```http
ce-specversion: 1.0
ce-type: au.com.mycsp.intent.callback.v1
ce-source: intent-callback-ms
ce-id: evt-intent-callback-001
ce-time: 2026-04-18T12:15:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body

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
        "message": "Raw orchestrator callback payload retained by ICB MS"
      }
    },
    "orchestratorSource": "t7.orchestrator",
    "orchestratorTimestamp": "2026-04-18T12:14:58+10:00"
  }
}
```

### ICB MS ownership boundary

ICB MS does not validate intent existence, map orchestrator state, derive orchestrator type, decide actionability, or emit assurance/lifecycle events.

IA MS owns correlation, mapping, skip/dead-letter decisions, and downstream assurance outcome publication.

---

## Idempotency and replay

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

## Topic/key baseline

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

## Final notes

- Internal events are not external TMF events.
- External TMF events must be curated projection/resource events.
- Internal events must not leak secrets, credentials, tokens, or raw platform stack traces.
- Use `intent-intelligence-ms`, not the old interpreter service name.
- Use `intent-controller-ms`, not any creation-service wording.
- Use `priority`, not legacy priority field names.
- Use `critical`, not old clinical-specific priority values.
- Use `resources` for selected optimisation resources in `IntentOptimisedEvent`.
- Use typed placeholders in examples when abbreviating arrays or objects.
