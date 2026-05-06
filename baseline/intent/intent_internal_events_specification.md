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

### Stable event ontology rule

Internal events are not raw KP-schema projections.

Internal events use stable shared intent-domain terms. Domain-specific KP structures may vary, and II MS maps domain KP knowledge into the stable internal event contract.

Use direct `location`, `serviceType`, and `serviceClass` fields outside KP. Do not wrap them in `context`, `location`, `serviceType`, and `serviceClass`, or `locationBasedService` in internal event JSON examples.

### Common references shape

Internal event `references` should use named resource reference objects with `id` and `href` where available.

Use `correlationId` as a common scalar reference.

### Optimiser status and evaluation rule

Use optimiser statuses as the primary outcome for the optimisation run, target evaluations, and constraint evaluations.

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

`INFEASIBLE` means the item was evaluated but cannot be satisfied with the available resources/constraints.

`FAILED` means technical/runtime/model/data failure.

### Service-ready configuration rule

`IntentNetworkReadyEvent` means the service configuration has been prepared for orchestration/apply.

It does not mean the service has already been applied.

Use `serviceConfiguration` to carry the service apply plan derived from selected optimiser resources and KP logical target/profile references.

`serviceConfiguration.resources` contains the selected resources to apply.

`serviceConfiguration.observerResourceIds` contains all KP resource IDs for the location-based service that IA/observer should monitor.

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
| `IntentNetworkReadyEvent` | `intent-assurance-ms` / network preparation path | `intent-controller-ms` / assurance projection path | Optimised resource set is ready for orchestration/apply; apply success is not yet confirmed |
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
        "locationId": "AU-NSW-SYD-HOSP-001",
        "locationType": "hospital",
        "geographicScope": "campus"
      },
      "serviceType": "surgical-connectivity",
      "serviceClass": "critical-gold",
      "priority": "critical",
      "maxLatencyMs": 10,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01,
      "preferredAccessTechnology": "5G",
      "redundancyRequired": true
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

- `IntentValidatedEvent` is the lean IC MS admission-focused event.
- It carries the admitted runtime `expression`.
- It includes `serviceType`.
- It keeps `redundancyRequired` when it came from expression mapping/defaults.
- It does not include KP `benchmarks`, `resources`, `resources`, optimiser details, orchestrator details, or a `validation` object.
- It uses canonical `location.locationId` in the baseline event example.

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

### Example headers

```http
ce-specversion: 1.0
ce-type: IntentRejectedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-rejected-001
ce-time: 2026-04-18T12:01:00+10:00
ce-subject: INT-HOSP-2026-002
content-type: application/json
```

### Example body

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-002",
    "version": "v1",
    "lifecycleStatus": "Rejected",
    "reasonCode": "SERVICE_NOT_AVAILABLE",
    "statusReason": "Surgical critical-gold connectivity is not currently available at the requested location.",
    "location": {
      "locationId": "AU-QLD-BNE-HOSP-201",
      "displayName": "Brisbane-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "references": {
      "correlationId": "corr-intent-create-002",
      "intent": {
        "id": "INT-HOSP-2026-002",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-002"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      },
      "knowledgePlane": {
        "configId": "hospital-surgical-slice-kp-v1",
        "version": "1.0"
      }
    }
  }
}
```

### Event-specific rules

- `IntentRejectedEvent` is the semantic/policy/capability rejection event.
- For simple semantic/capability rejection, carry `lifecycleStatus`, `reasonCode`, `statusReason`, direct `location`, `serviceType`, `serviceClass`, and references.
- Use `reasonCode: SERVICE_NOT_AVAILABLE` when the requested service is not currently available for the resolved service/location.
- Do not include a `serviceContext` or generic `context` wrapper.
- Do not include an `evaluations` block unless multiple checks or detailed rejection evidence is genuinely useful.
- Do not include optimiser, orchestration, or assurance payloads.

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
      "locationId": "AU-NSW-SYD-HOSP-001",
      "displayName": "Sydney-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 10,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true
    },
    "preferences": {
      "preferredAccessTechnology": "5G"
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
      },
      "knowledgePlane": {
        "configId": "hospital-surgical-slice-kp-v1",
        "version": "1.0"
      }
    },
    "resources": [
      {
        "resourceId": "SYD-PRI-01",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "roles": [
          "primary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-b",
        "metrics": {
          "benchmark": {
            "latencyMs": 7,
            "availabilityPercent": 99.996,
            "jitterMs": 1.1,
            "packetLossPercent": 0.004
          }
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "SYD-SEC-01"
          }
        ]
      },
      {
        "resourceId": "SYD-PRI-02",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "roles": [
          "primary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-a",
        "metrics": {
          "benchmark": {
            "latencyMs": 8,
            "availabilityPercent": 99.995,
            "jitterMs": 1.5,
            "packetLossPercent": 0.005
          }
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "SYD-SEC-02"
          }
        ]
      },
      {
        "resourceId": "SYD-SEC-01",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-b",
        "metrics": {
          "benchmark": {
            "latencyMs": 10,
            "availabilityPercent": 99.994,
            "jitterMs": 1.8,
            "packetLossPercent": 0.006
          }
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "SYD-PRI-01"
          }
        ]
      },
      {
        "resourceId": "SYD-SEC-02",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-a",
        "metrics": {
          "benchmark": {
            "latencyMs": 9,
            "availabilityPercent": 99.997,
            "jitterMs": 1.2,
            "packetLossPercent": 0.003
          }
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "SYD-PRI-02"
          }
        ]
      }
    ]
  }
}
```

### Event-specific rules

- `IntentResolvedEvent` is the lean optimiser handoff.
- Use direct `location`, `serviceType`, and `serviceClass` fields; do not wrap them in `context` or `serviceContext`.
- Do not include `capabilityStatus`; successful `IntentResolvedEvent` emission implies semantic/capability resolution succeeded.
- Use `targets` for measurable SLA-style objectives.
- Use `constraints` for hard non-target inputs such as `priority` and `redundancyRequired`.
- Use `preferences` for soft selection guidance such as `preferredAccessTechnology`.
- Do not include direct top-level `priority`, `preferredAccessTechnology`, or `redundancyRequired`; place them under `constraints` or `preferences`.
- Do not include a generic `context` wrapper by default.
- Do not include `resourceRoles` or `accessTechnologies`; resources already expose actual roles and access technologies.
- Do not include a separate top-level KP `benchmarks` block when it duplicates `targets`.
- Map KP/domain resource knowledge to runtime optimiser handoff `resources`.
- `IntentResolvedEvent.resources` contains all available resources for the resolved location/service that the optimiser may consider, not a shortened selected list.
- Resource entries use runtime `roles`, mapped from KP `resourceRoles`.
- For first-pass optimisation resources use `metrics.benchmark`; for degradation/control-loop re-optimisation resources use `metrics.telemetry` and omit `metrics.benchmark` by default.

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
      "locationId": "AU-NSW-SYD-HOSP-001",
      "displayName": "Sydney-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "resources": [
      {
        "resourceId": "SYD-PRI-01",
        "roles": [
          "primary"
        ],
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "accessTechnology": "fibre",
        "provider": "fixed-access-b",
        "metrics": {
          "benchmark": {
            "latencyMs": 7,
            "availabilityPercent": 99.996,
            "jitterMs": 1.1,
            "packetLossPercent": 0.004
          }
        }
      },
      {
        "resourceId": "SYD-SEC-01",
        "roles": [
          "secondary"
        ],
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "accessTechnology": "5G",
        "provider": "mobile-access-b",
        "metrics": {
          "benchmark": {
            "latencyMs": 10,
            "availabilityPercent": 99.994,
            "jitterMs": 1.8,
            "packetLossPercent": 0.006
          }
        }
      }
    ],
    "optimisationRun": {
      "status": "COMPLETED",
      "statusReason": "Optimisation completed and selected a feasible primary/secondary resource set."
    },
    "targetEvaluations": [
      {
        "name": "latency",
        "status": "COMPLETED",
        "target": 10,
        "benchmarkValue": 7,
        "unit": "ms"
      },
      {
        "name": "availability",
        "status": "COMPLETED",
        "target": 99.99,
        "benchmarkValue": 99.996,
        "unit": "percent"
      },
      {
        "name": "jitter",
        "status": "COMPLETED",
        "target": 2,
        "benchmarkValue": 1.1,
        "unit": "ms"
      },
      {
        "name": "packetLoss",
        "status": "COMPLETED",
        "target": 0.01,
        "benchmarkValue": 0.004,
        "unit": "percent"
      }
    ],
    "constraintEvaluations": [
      {
        "name": "priority",
        "status": "COMPLETED",
        "statusReason": "Critical priority was accepted as an optimisation constraint."
      },
      {
        "name": "redundancyRequired",
        "status": "COMPLETED",
        "statusReason": "Selected resources include primary and secondary roles."
      }
    ],
    "preferenceEvaluations": [
      {
        "name": "preferredAccessTechnology",
        "status": "COMPLETED",
        "statusReason": "Selected secondary resource uses preferred access technology."
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
      },
      "knowledgePlane": {
        "configId": "hospital-surgical-slice-kp-v1",
        "version": "1.0"
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
      "locationId": "AU-NSW-SYD-HOSP-001",
      "displayName": "Sydney-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "optimisationRun": {
      "status": "INFEASIBLE",
      "statusReason": "No resource resource set could satisfy all required targets and constraints."
    },
    "targetEvaluations": [
      {
        "name": "latency",
        "status": "INFEASIBLE",
        "target": 10,
        "bestBenchmarkValue": 18,
        "unit": "ms",
        "reasonCode": "OPTIMISATION_LATENCY_UNSATISFIABLE"
      },
      {
        "name": "availability",
        "status": "COMPLETED",
        "target": 99.99,
        "bestBenchmarkValue": 99.995,
        "unit": "percent"
      }
    ],
    "constraintEvaluations": [
      {
        "name": "priority",
        "status": "COMPLETED",
        "statusReason": "Critical priority was accepted as an optimisation constraint."
      },
      {
        "name": "redundancyRequired",
        "status": "INFEASIBLE",
        "statusReason": "No feasible primary/secondary resource set could satisfy the resolved targets."
      }
    ],
    "preferenceEvaluations": [
      {
        "name": "preferredAccessTechnology",
        "status": "COMPLETED",
        "statusReason": "Preferred access technology was considered during infeasibility analysis."
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
      },
      "knowledgePlane": {
        "configId": "hospital-surgical-slice-kp-v1",
        "version": "1.0"
      }
    }
  }
}
```

### Event-specific rules

- Use direct `location`, `serviceType`, and `serviceClass` fields; do not wrap them in `context` or `serviceContext`.
- Use `resources` for optimiser-selected resources.
- Use optimiser statuses such as `COMPLETED`, `INFEASIBLE`, and `FAILED`.
- Use `targetEvaluations` for measurable SLA-style target checks.
- Use `constraintEvaluations` for checks that correspond to `IntentResolvedEvent.constraints`.
- Use `preferenceEvaluations` for checks that correspond to `IntentResolvedEvent.preferences`.
- Use value comparison fields such as `target`, `benchmarkValue`, and `observedValue` for measurable target evaluations.
- For boolean/string constraints and preferences, use `name`, `status`, and `statusReason` unless the actual comparison value adds meaningful diagnostic value.
- Do not use `contextEvaluations`; this avoids reintroducing generic context terminology.
- Do not include optimiser objective/rule configuration in the event; optimiser owns that internally.

## IntentNetworkReadyEvent

### Producer

```text
intent-assurance-ms / network preparation path
```

### Current primary consumer

```text
intent-controller-ms
```

### Meaning

`IntentNetworkReadyEvent` is an internal milestone event indicating that the service configuration/resource set has been prepared for orchestration/apply.

It does not mean the service has already been applied.

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
    "lifecycleStatus": "InProgress",
    "statusReason": "Service configuration has been prepared for orchestration/apply.",
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "displayName": "Sydney-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "serviceConfiguration": {
      "orchestratorTarget": "t7-network-orchestrator",
      "orchestratorProfile": "hospital-surgical-slice-apply-v1",
      "observerTarget": "t7-observability-platform",
      "observerProfile": "critical-gold-assurance-observation-v1",
      "observerResourceIds": [
        "SYD-PRI-01",
        "SYD-PRI-02",
        "SYD-SEC-01",
        "SYD-SEC-02"
      ],
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
    "references": {
      "correlationId": "corr-intent-create-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      },
      "knowledgePlane": {
        "configId": "hospital-surgical-slice-kp-v1",
        "version": "1.0"
      }
    }
  }
}
```

### Event-specific rules

- `IntentNetworkReadyEvent` means service configuration is ready for orchestration/apply, not that apply has succeeded.
- Use direct `location`, `serviceType`, and `serviceClass` fields; do not wrap them in `context` or `serviceContext`.
- Use `serviceConfiguration` because the event carries the service apply plan rather than low-level network configuration.
- `serviceConfiguration.resources` contains the selected resources ready for apply.
- `serviceConfiguration.observerResourceIds` contains all KP resource IDs for the location/service that IA/observer should monitor, including selected and non-selected paths.
- Include logical `orchestratorTarget`, `orchestratorProfile`, `observerTarget`, and `observerProfile` from KP.
- Do not include `applyOutcome`.
- Do not include QoS, bandwidth, routing policy, hops, or service attributes by default.

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
    "version": "v1",
    "lifecycleStatus": "Active",
    "statusReason": "Observed telemetry for selected resources is within resolved targets.",
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "displayName": "Sydney-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "resources": [
      {
        "role": "primary",
        "resourceId": "SYD-PRI-01"
      },
      {
        "role": "secondary",
        "resourceId": "SYD-SEC-01"
      }
    ],
    "observations": [
      {
        "resourceId": "SYD-PRI-01",
        "role": "primary",
        "metrics": {
          "latencyMs": 8,
          "availabilityPercent": 99.995,
          "jitterMs": 1.5,
          "packetLossPercent": 0.005
        },
        "evaluations": [
          {
            "name": "latency",
            "status": "COMPLETED",
            "target": 10,
            "observedValue": 8,
            "unit": "ms"
          },
          {
            "name": "availability",
            "status": "COMPLETED",
            "target": 99.99,
            "observedValue": 99.995,
            "unit": "percent"
          },
          {
            "name": "jitter",
            "status": "COMPLETED",
            "target": 2,
            "observedValue": 1.5,
            "unit": "ms"
          },
          {
            "name": "packetLoss",
            "status": "COMPLETED",
            "target": 0.01,
            "observedValue": 0.005,
            "unit": "percent"
          }
        ]
      },
      {
        "resourceId": "SYD-SEC-01",
        "role": "secondary",
        "metrics": {
          "latencyMs": 10,
          "availabilityPercent": 99.994,
          "jitterMs": 1.8,
          "packetLossPercent": 0.006
        },
        "evaluations": [
          {
            "name": "latency",
            "status": "COMPLETED",
            "target": 10,
            "observedValue": 10,
            "unit": "ms"
          },
          {
            "name": "availability",
            "status": "COMPLETED",
            "target": 99.99,
            "observedValue": 99.994,
            "unit": "percent"
          },
          {
            "name": "jitter",
            "status": "COMPLETED",
            "target": 2,
            "observedValue": 1.8,
            "unit": "ms"
          },
          {
            "name": "packetLoss",
            "status": "COMPLETED",
            "target": 0.01,
            "observedValue": 0.006,
            "unit": "percent"
          }
        ]
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
    "version": "v1",
    "lifecycleStatus": "Degraded",
    "statusReason": "Observed latency is outside the resolved target.",
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "displayName": "Sydney-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "resources": [
      {
        "role": "primary",
        "resourceId": "SYD-PRI-01"
      },
      {
        "role": "secondary",
        "resourceId": "SYD-SEC-01"
      }
    ],
    "observations": [
      {
        "resourceId": "SYD-PRI-01",
        "role": "primary",
        "metrics": {
          "latencyMs": 18,
          "availabilityPercent": 99.992,
          "jitterMs": 1.8,
          "packetLossPercent": 0.006
        },
        "evaluations": [
          {
            "name": "latency",
            "status": "INFEASIBLE",
            "target": 10,
            "observedValue": 18,
            "unit": "ms",
            "statusReason": "Observed latency is above the resolved maximum latency target."
          },
          {
            "name": "availability",
            "status": "COMPLETED",
            "target": 99.99,
            "observedValue": 99.992,
            "unit": "percent"
          }
        ]
      },
      {
        "resourceId": "SYD-PRI-02",
        "role": "observedAlternative",
        "metrics": {
          "latencyMs": 9,
          "availabilityPercent": 99.996,
          "jitterMs": 1.4,
          "packetLossPercent": 0.004
        },
        "evaluations": [
          {
            "name": "latency",
            "status": "COMPLETED",
            "target": 10,
            "observedValue": 9,
            "unit": "ms"
          }
        ]
      },
      {
        "resourceId": "SYD-SEC-01",
        "role": "secondary",
        "metrics": {
          "latencyMs": 12,
          "availabilityPercent": 99.994,
          "jitterMs": 1.8,
          "packetLossPercent": 0.006
        },
        "evaluations": [
          {
            "name": "latency",
            "status": "INFEASIBLE",
            "target": 10,
            "observedValue": 12,
            "unit": "ms",
            "statusReason": "Observed latency is above the resolved maximum latency target."
          }
        ]
      },
      {
        "resourceId": "SYD-SEC-02",
        "role": "observedAlternative",
        "metrics": {
          "latencyMs": 9,
          "availabilityPercent": 99.997,
          "jitterMs": 1.2,
          "packetLossPercent": 0.003
        },
        "evaluations": [
          {
            "name": "latency",
            "status": "COMPLETED",
            "target": 10,
            "observedValue": 9,
            "unit": "ms"
          }
        ]
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

### Event-specific rules

- Use direct `location`, `serviceType`, and `serviceClass` fields; do not wrap them in `context` or `serviceContext`.
- Do not include `assuranceStatus` by default; `lifecycleStatus` carries the assurance outcome.
- Use `resources` for selected/applied resources.
- Use `observations[].metrics` for telemetry observed for each monitored resource.
- Keep healthy/active assurance events lean and include observations for selected/applied resources only.
- When `lifecycleStatus` is `Degraded`, `Failed`, or the event supports re-optimisation, IA MS may include observations for all monitored paths from `observerResourceIds`.
- Do not include top-level `targets` and `observedMetrics` when the same values are already carried in `observations[].evaluations`.
- Do not include `controlLoop` by default; downstream control-loop consumers derive the next action from the assurance event.
- Do not include a `knowledgePlane` reference by default; IA MS works from applied service configuration, observer scope, and resolved targets.
- No separate `IntentDriftOccurredEvent` is needed by default; drift/degradation is represented by `IntentAssuranceEvent`.

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
    "intentId": "INT-HOSP-2026-001",
    "eventType": "IntentCallbackEvent",
    "eventVersion": "1.0",
    "source": "intent-callback-ms",
    "eventTime": "2026-04-18T12:15:00+10:00",
    "correlationId": "corr-intent-callback-001",
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
- Use `priority`, not legacy priority field names.
- Use `critical`, not old clinical-specific priority values.
- Use `resources` for selected optimisation resources in `IntentOptimisedEvent`.


### Resource field naming rule

Use `resources` consistently across internal event bodies.

The event type defines what those resources mean:

| **Event** | **`resources` meaning** |
|---|---|
| `IntentResolvedEvent` | Available resources for optimiser consideration |
| `IntentOptimisedEvent` | Optimiser-selected resources |
| `IntentNetworkReadyEvent` | Selected resources ready for apply |
| `IntentAssuranceEvent` | Applied/assured selected resources |

Avoid stage-specific field names such as `candidates` and `resourcePlan` unless a future event genuinely needs multiple resource sets in the same payload.

### Optimisation input/evaluation bucket rule

`IntentResolvedEvent` separates optimiser inputs into `targets`, `constraints`, and `preferences`.

`IntentOptimisedEvent` maps those input buckets to `targetEvaluations`, `constraintEvaluations`, and `preferenceEvaluations`.

Use measurable value comparison fields such as `target`, `benchmarkValue`, and `observedValue` for target evaluations.

For boolean/string constraints and preferences, use `name`, `status`, and `statusReason` unless the actual comparison value adds useful diagnostic value.

