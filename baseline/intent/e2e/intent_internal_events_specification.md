# Intent Event Specification

## 1. Document status:

| Field | Value |
|---|---|
| Document status | Intent Architecture 3.5 baseline-aligned internal event specification. |
| Source of truth | GitHub `main/baseline/intent`. |
| Baseline tag | `intent-3.5-baseline`. |
| Scope | Internal Intent Enabler event contracts, CloudEvents headers, topics, payload rules, and event-specific examples. |
| Change note | Adds numbered headings, numbered table of contents, and status table only. |

## 2. Table of contents:

- [1. Document status:](#1-document-status)
- [2. Table of contents:](#2-table-of-contents)
- [3. Intent internal events specification:](#3-intent-internal-events-specification)
  - [3.1. Purpose](#31-purpose)
  - [3.2. Event style](#32-event-style)
  - [3.3. Common internal event rules](#33-common-internal-event-rules)
  - [3.4. Stable event ontology rule](#34-stable-event-ontology-rule)
  - [3.5. Common references shape](#35-common-references-shape)
  - [3.6. Shared location vocabulary](#36-shared-location-vocabulary)
  - [3.7. Admission context carry-through rule](#37-admission-context-carry-through-rule)
  - [3.8. Optimiser status and evaluation rule](#38-optimiser-status-and-evaluation-rule)
  - [3.9. Service configuration structure rule](#39-service-configuration-structure-rule)
  - [3.10. Service-ready configuration rule](#310-service-ready-configuration-rule)
- [4. Common CloudEvents headers:](#4-common-cloudevents-headers)
  - [4.1. Header and topic deviations by event:](#41-header-and-topic-deviations-by-event)
- [5. Internal event catalogue:](#5-internal-event-catalogue)
- [6. IntentValidatedEvent:](#6-intentvalidatedevent)
  - [6.1. Producer](#61-producer)
  - [6.2. Current primary consumer](#62-current-primary-consumer)
  - [6.3. Meaning](#63-meaning)
  - [6.4. Example headers](#64-example-headers)
  - [6.5. Example body](#65-example-body)
  - [6.6. Event-specific rules](#66-event-specific-rules)
- [7. IntentRejectedEvent:](#7-intentrejectedevent)
  - [7.1. Producer](#71-producer)
  - [7.2. Current primary consumer](#72-current-primary-consumer)
  - [7.3. Meaning](#73-meaning)
  - [7.4. Example headers](#74-example-headers)
  - [7.5. Example body](#75-example-body)
  - [7.6. Event-specific rules](#76-event-specific-rules)
- [8. IntentResolvedEvent:](#8-intentresolvedevent)
  - [8.1. Producer](#81-producer)
  - [8.2. Current primary consumer](#82-current-primary-consumer)
  - [8.3. Meaning](#83-meaning)
  - [8.4. Example headers](#84-example-headers)
  - [8.5. Example body](#85-example-body)
  - [8.6. Event-specific rules](#86-event-specific-rules)
- [9. OptimisationStatusChangeEvent:](#9-optimisationstatuschangeevent)
  - [9.1. Producer](#91-producer)
  - [9.2. Current primary consumer](#92-current-primary-consumer)
  - [9.3. Meaning](#93-meaning)
  - [9.4. Topic](#94-topic)
  - [9.5. Example headers](#95-example-headers)
  - [9.6. Example payload](#96-example-payload)
  - [9.7. Event-specific rules](#97-event-specific-rules)
- [10. IntentNetworkReadyEvent:](#10-intentnetworkreadyevent)
  - [10.1. Producer](#101-producer)
  - [10.2. Current primary consumer](#102-current-primary-consumer)
  - [10.3. Meaning](#103-meaning)
  - [10.4. Example headers](#104-example-headers)
  - [10.5. Example body](#105-example-body)
  - [10.6. Event-specific rules](#106-event-specific-rules)
- [11. IntentAssuranceEvent:](#11-intentassuranceevent)
  - [11.1. Producer](#111-producer)
  - [11.2. Current primary consumer](#112-current-primary-consumer)
  - [11.3. Meaning](#113-meaning)
  - [11.4. Example body — active outcome](#114-example-body-active-outcome)
  - [11.5. Example body — degraded outcome](#115-example-body-degraded-outcome)
  - [11.6. Example body — failed outcome](#116-example-body-failed-outcome)
  - [11.7. Example body — terminated outcome](#117-example-body-terminated-outcome)
  - [11.8. Event-specific rules](#118-event-specific-rules)
- [12. IntentCallbackEvent:](#12-intentcallbackevent)
  - [12.1. Producer](#121-producer)
  - [12.2. Current primary consumer](#122-current-primary-consumer)
  - [12.3. Topic](#123-topic)
  - [12.4. Kafka key](#124-kafka-key)
  - [12.5. CloudEvents type](#125-cloudevents-type)
  - [12.6. Meaning](#126-meaning)
  - [12.7. Example headers](#127-example-headers)
  - [12.8. Example body](#128-example-body)
  - [12.9. Event-specific rules](#129-event-specific-rules)
  - [12.10. ICB MS ownership boundary](#1210-icb-ms-ownership-boundary)

## 3. Intent internal events specification:

### 3.1. Purpose:

This document defines the current baseline internal event contracts for the Intent Enabler workflow. Internal events are platform events exchanged between Intent Enabler microservices and internal platform components. They are not external TMF listener events.

### 3.2. Event style:

Internal events use CloudEvents-style metadata in transport headers and a plain JSON payload. Most Intent Enabler internal events use a top-level `body` object.

`OptimisationStatusChangeEvent` is the approved optimiser outcome payload relayed by ICB MS for II MS. It keeps the approved optimiser event payload shape at the payload root and is not converted into the ICB-owned `body` callback fact shape.

Internal events are state, progress, and outcome facts, not point-to-point commands for one specific consumer.

### 3.3. Common internal event rules:

| **Rule** | **Baseline** |
|---|---|
| Delivery model | At-least-once |
| Consumer behaviour | Idempotent consumption required |
| Deduplication key | `ce-id` or `eventId` |
| Correlation | `correlationId` must be propagated |
| Kafka key | Prefer `intentId` for intent-scoped events |
| Payload style | Plain JSON payload with CloudEvents metadata in transport headers. Most internal events use top-level `body`; `OptimisationStatusChangeEvent` uses the approved optimiser event payload shape at payload root. |
| Event naming | Use final baselined event names exactly |
| Schema evolution | Additive changes preferred; breaking changes require versioning |
| Sensitive data | Do not include secrets, tokens, credentials, or raw internal stack traces |
| External exposure | Internal payloads are not directly exposed as external TMF events |

### 3.4. Stable event ontology rule:

Internal events are not raw KP-schema projections. Internal events use stable shared intent-domain terms. Domain-specific KP structures may vary, and II MS maps domain KP knowledge into the stable internal event contract. Runtime intent semantics should preserve the canonical `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences` grouping unless a specific downstream event explicitly defines a different evaluated-output shape. Domain inputs such as `location`, `serviceType`, and `serviceClass` remain under `expression.context.constraints` for admitted and resolved runtime intent context.

Use shared resource vocabulary in internal events:

- `resourceType: "deliveryResource"`
- `resourceClass: "critical-gold"`
- `roles: ["primary"]` and `roles: ["secondary"]`
- neutral metric names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`

Do not encode source and context into event-facing metric wrappers or field names such as `metrics.benchmark`, `metrics.telemetry`, `latencyBenchmarkMs`, or `currentLatencyMs`. The event type and processing stage provide that meaning.

### 3.5. Common references shape:

Internal event `references` should use named resource reference objects with `id` and `href` where available. Use `correlationId` as a common scalar reference.

### 3.6. Shared location vocabulary:

Where a location is present inside `expression.context.constraints.location`, the stable baseline fields are `locationId`, optional `displayName`, optional `locationType`, and optional `geographicScope`. Service-specific events may carry the subset that is relevant to the stage; absence of optional fields must not change the location identity when `locationId` is present.

### 3.7. Admission context carry-through rule:

`IntentValidatedEvent` must carry both `intentSpecification.id` and `expression.iri` from IC MS admission. `intentSpecification.id` identifies the selected active specification. `expression.iri` identifies the admitted semantic and expression contract. II MS treats both as carried-forward admission facts and must not re-resolve the governing `IntentSpecification` by IRI alone.

### 3.8. Optimiser status and evaluation rule:

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

`COMPLETED` means the item was successfully evaluated and satisfied. `INFEASIBLE` means the item was evaluated but cannot be satisfied with the available resources and constraints. `FAILED` means technical/runtime/model/data failure.

### 3.9. Service configuration structure rule:

In `IntentNetworkReadyEvent.serviceConfiguration`, use:

- `orchestratorConfiguration.target`
- `orchestratorConfiguration.profile`
- `orchestratorConfiguration.resources`
- `observerConfiguration.target`
- `observerConfiguration.profile`
- `observerConfiguration.resources`

Do not repeat `orchestrator` or `observer` prefixes inside their own configuration blocks.

### 3.10. Service-ready configuration rule:

`IntentNetworkReadyEvent` means the service configuration has been prepared for change execution and apply. It does not mean the service has already been applied. Use `serviceConfiguration` to carry the service apply and observation plan.

`serviceConfiguration.orchestratorConfiguration.resources[]` contains only the optimiser-selected resources and configuration ready for apply.

`serviceConfiguration.observerConfiguration.resources[]` contains the full assurance observation scope that IA or observer should monitor, including selected and non-selected paths where they are part of the assurance scope. Each observer resource uses `metrics` as a list of metric names to observe, not metric values.

---

## 4. Common CloudEvents headers:

```http
ce-specversion: 1.0
ce-type: IntentValidatedEvent
ce-source: intent-controller-ms
ce-id: evt-intent-validated-001
ce-time: 2026-04-18T12:00:01+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 4.1. Header and topic deviations by event:

| Event | Topic and header note |
|---|---|
| `OptimisationStatusChangeEvent` | Published by `intent-callback-ms` to `t7.intent.management.events` after ICB relay. It may include `x-correlation-id` as an internal transport correlation header in addition to payload correlation fields. |
| `IntentCallbackEvent` | Published by `intent-callback-ms` to the dedicated callback topic `t7.intent.management.events.callbacks`, not the main internal topic. |
| Other internal events | Use the main internal intent event topic and the common CloudEvents-style header pattern shown above. |

---

## 5. Internal event catalogue:

| **Event** | **Producer** | **Current primary consumer(s)** | **Purpose** |
|---|---|---|---|
| `IntentValidatedEvent` | `intent-controller-ms` | `intent-intelligence-ms` | Runtime Intent passed IC MS admission validation and was admitted into the lifecycle |
| `IntentRejectedEvent` | `intent-intelligence-ms` | `intent-controller-ms` | Semantic and policy validation rejected the admitted Intent |
| `IntentResolvedEvent` | `intent-intelligence-ms` | `optimiser-controller-ms` or approved optimisation path | Intent was semantically resolved into a canonical internal handoff with applicable resources for optimisation. The optimiser may be an approved platform component reached through the optimiser integration path, not a public Intent Enabler API. |
| `OptimisationStatusChangeEvent` | `intent-callback-ms` | `intent-intelligence-ms` | Approved optimiser outcome callback relayed by ICB MS after durable callback ingestion. |
| `IntentNetworkReadyEvent` | `intent-intelligence-ms` | `intent-assurance-ms` | Optimised resource set has been projected into service configuration ready for change execution and apply; apply success is not yet confirmed |
| `IntentAssuranceEvent` | `intent-assurance-ms` | `intent-controller-ms` | Assurance, apply, and runtime outcome truth for external Intent and IntentReport projection |
| `IntentCallbackEvent` | `intent-callback-ms` | `intent-assurance-ms` | Accepted raw change execution and apply callback fact relayed to the dedicated callback topic for IA MS |

---

## 6. IntentValidatedEvent:

### 6.1. Producer:

```text
intent-controller-ms
```

### 6.2. Current primary consumer:

```text
intent-intelligence-ms
```

### 6.3. Meaning:

The runtime Intent has passed IC MS admission validation and has been admitted into the intent lifecycle.

### 6.4. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentValidatedEvent
ce-source: intent-controller-ms
ce-id: evt-intent-validated-001
ce-time: 2026-04-18T12:00:01+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 6.5. Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "Acknowledged",
    "statusReason": "Intent request passed IC MS admission validation and was admitted for downstream processing.",
    "intentSpecification": {
      "id": "ispec-hss-001",
      "specKey": "hospital-surgical-slice-spec",
      "version": "1.20"
    },
    "expression": {
      "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "hospital",
            "geographicScope": "campus"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    },
    "references": {
      "correlationId": "corr-intent-create-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      }
    }
  }
}
```

### 6.6. Event-specific rules:

- `IntentValidatedEvent` is the lean IC MS admission-focused event.
- It carries the admitted runtime `expression.iri` and `expression.context`.
- The admitted expression uses the shared semantic buckets: `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences`.
- It includes `serviceType` under `expression.context.constraints`.
- It keeps `redundancyRequired` under `expression.context.constraints` when it came from expression mapping/defaults.
- It does not include KP `benchmarks`, optimiser details, change-execution details, assurance details, or a `validation` object.
- It uses canonical `expression.context.constraints.location.locationId` in the baseline event example.

## 7. IntentRejectedEvent:

### 7.1. Producer:

```text
intent-intelligence-ms
```

### 7.2. Current primary consumer:

```text
intent-controller-ms
```

### 7.3. Meaning:

Semantic, policy, or downstream interpretation validation rejected the admitted Intent.

### 7.4. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentRejectedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-rejected-001
ce-time: 2026-04-18T12:01:00+10:00
ce-subject: INT-HOSP-2026-002
content-type: application/json
```

### 7.5. Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-002",
    "intentVersion": "v1",
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
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      },
      "knowledgePlane": {
        "configId": "hospital-surgical-slice-kp-v1",
        "version": "1.0"
      }
    }
  }
}
```

### 7.6. Event-specific rules:

- `IntentRejectedEvent` is the semantic, policy, or capability rejection event.
- For simple semantic or capability rejection, carry `lifecycleStatus`, `reasonCode`, `statusReason`, direct `location`, `serviceType`, `serviceClass`, and references. This is a deliberate compact rejection shape for failed admission or semantic resolution where a full resolved `body.expression.context` may not exist or may add no useful decision value.
- Use `reasonCode: SERVICE_NOT_AVAILABLE` when the requested service is not currently available for the resolved service/location.
- Do not include a `serviceContext` or generic `context` wrapper.
- Do not include an `evaluations` block unless multiple checks or detailed rejection evidence is genuinely useful.
- Do not include optimiser, change-execution, or assurance payloads.
- Include `references.knowledgePlane` when Knowledge Plane configuration or capability state materially contributed to the rejection decision. Do not include it for rejection outcomes that do not depend on KP context.

## 8. IntentResolvedEvent:

### 8.1. Producer:

```text
intent-intelligence-ms
```

### 8.2. Current primary consumer:

```text
optimiser-controller-ms
```

### 8.3. Meaning:

The admitted Intent has been semantically resolved into a canonical internal handoff that can be optimised.

### 8.4. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentResolvedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-resolved-001
ce-time: 2026-04-18T12:03:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 8.5. Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "InProgress",
    "statusReason": "Intent has been semantically resolved into candidate resources for optimisation.",
    "expression": {
      "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "displayName": "Sydney-Main-Hospital"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    },
    "references": {
      "correlationId": "corr-intent-create-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      },
      "knowledgePlane": {
        "configId": "hospital-surgical-slice-kp-v1",
        "version": "1.0"
      }
    },
    "resources": [
      {"resourceId": "SYD-PRI-01", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["primary"], "accessTechnology": "fibre", "metrics": {"latencyMs": 7, "availabilityPercent": 99.996, "jitterMs": 1.1, "packetLossPercent": 0.004}, "relationships": [{"type": "pairedSecondary", "resourceId": "SYD-SEC-01"}]},
      {"resourceId": "SYD-PRI-02", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["primary"], "accessTechnology": "5G", "metrics": {"latencyMs": 8, "availabilityPercent": 99.995, "jitterMs": 1.5, "packetLossPercent": 0.005}, "relationships": [{"type": "pairedSecondary", "resourceId": "SYD-SEC-02"}]},
      {"resourceId": "SYD-SEC-01", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["secondary"], "accessTechnology": "5G", "metrics": {"latencyMs": 10, "availabilityPercent": 99.994, "jitterMs": 1.8, "packetLossPercent": 0.006}, "relationships": [{"type": "protects", "resourceId": "SYD-PRI-01"}]},
      {"resourceId": "SYD-SEC-02", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["secondary"], "accessTechnology": "fibre", "metrics": {"latencyMs": 9, "availabilityPercent": 99.997, "jitterMs": 1.2, "packetLossPercent": 0.003}, "relationships": [{"type": "protects", "resourceId": "SYD-PRI-02"}]}
    ]
  }
}
```

### 8.6. Event-specific rules:

- `IntentResolvedEvent` is the lean optimiser handoff.
- Preserve resolved runtime semantics under `expression.context` when carrying the resolved intent context.
- Use `expression.context.targets` for measurable SLA-style objectives.
- Use `expression.context.constraints` for hard inputs such as location, service type, service class, priority, and redundancy.
- Use `expression.context.preferences` for soft selection guidance such as `preferredAccessTechnology`.
- Do not include direct top-level `priority`, `preferredAccessTechnology`, or `redundancyRequired`; place them under `expression.context.constraints` or `expression.context.preferences`.
- Do not include `capabilityStatus`; successful `IntentResolvedEvent` emission implies semantic/capability resolution succeeded.
- `IntentResolvedEvent.resources[]` contains all applicable and apply-capable resources for the resolved location and service that the optimiser may consider, not a shortened selected list.
- `IntentResolvedEvent.resources[].metrics` carries neutral metric values using names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.
- In `IntentResolvedEvent`, `resources[].metrics` carries candidate metric **values** from KP or resolution context. This is different from `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[].metrics`, where `metrics` is a list of metric **names** that IA or observer should collect.


## 9. OptimisationStatusChangeEvent:

### 9.1. Producer:

```text
intent-callback-ms
```

### 9.2. Current primary consumer:

```text
intent-intelligence-ms
```

### 9.3. Meaning:

`OptimisationStatusChangeEvent` is the approved optimiser outcome event relayed by ICB MS after the Optimiser platform submits `OptimisationStatusChangeEventRequest` to `POST /intent-callback/v1/submissions`. ICB MS validates the payload structurally, persists it through the callback outbox, and publishes the event to the main internal intent event topic. II MS owns optimiser outcome correlation, interpretation, and selected-configuration packaging.

### 9.4. Topic:

```text
t7.intent.management.events
```

### 9.5. Example headers:

```http
ce-specversion: 1.0
ce-type: OptimisationStatusChangeEvent
ce-source: intent-callback-ms
ce-id: evt-optimisation-status-001
ce-time: 2026-04-18T12:03:30+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
x-correlation-id: corr-intent-create-001
```

### 9.6. Example payload:

```json
{
  "eventType": "OptimisationStatusChangeEvent",
  "eventTime": "2026-04-18T12:03:30+10:00",
  "timeOccurred": "2026-04-18T12:03:30+10:00",
  "event": {
    "optimisation": {
      "id": "opt-hss-2026-001",
      "href": "/optimisation/opt-hss-2026-001",
      "previousLifecycleStatus": "PROCESSING",
      "newLifecycleStatus": "COMPLETED",
      "sourceContext": {
        "domain": "intent-management",
        "resource": {
          "id": "INT-HOSP-2026-001",
          "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
          "@type": "IntentRef",
          "@referredType": "Intent"
        },
        "correlationId": "corr-intent-create-001",
        "intentVersion": "v1"
      },
      "selectedConfiguration": {
        "orchestratorConfiguration": {
          "target": "t7-network-orchestrator",
          "profile": "hospital-surgical-slice-apply-v1",
          "resources": [
            {
              "resourceId": "SYD-PRI-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "accessTechnology": "fibre",
              "relationships": [
                {
                  "type": "pairedSecondary",
                  "resourceId": "SYD-SEC-01"
                }
              ]
            },
            {
              "resourceId": "SYD-SEC-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "accessTechnology": "5G",
              "relationships": [
                {
                  "type": "protects",
                  "resourceId": "SYD-PRI-01"
                }
              ]
            }
          ]
        },
        "observerConfiguration": {
          "target": "t7-observability-platform",
          "profile": "critical-gold-assurance-observation-v1",
          "resources": [
            {
              "resourceId": "SYD-PRI-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-PRI-02",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-SEC-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-SEC-02",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            }
          ]
        }
      }
    }
  },
  "@type": "OptimisationStatusChangeEvent"
}
```

### 9.7. Event-specific rules:

- `OptimisationStatusChangeEvent` is structurally relayed by ICB MS and consumed by II MS.
- ICB MS does not interpret optimiser status, selected configuration, feasibility, or service meaning.
- II MS owns correlation to the submitted `POST /optimisation` request and packaging of the selected configuration into `IntentNetworkReadyEvent`.
- This event is not converted into the ICB-owned `body` callback fact shape used by `IntentCallbackEvent`.


## 10. IntentNetworkReadyEvent:

### 10.1. Producer:

```text
intent-intelligence-ms
```

### 10.2. Current primary consumer:

```text
intent-assurance-ms
```

### 10.3. Meaning:

`IntentNetworkReadyEvent` is an internal milestone event indicating that the service configuration/resource set has been prepared for change execution and apply.

It does not mean the service has already been applied.

### 10.4. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-network-ready-001
ce-time: 2026-04-18T12:12:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 10.5. Example body:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "InProgress",
    "statusReason": "Service configuration has been prepared for change execution and apply.",
    "expression": {
      "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "constraints": {
          "location": {"locationId": "AU-NSW-SYD-HOSP-001", "displayName": "Sydney-Main-Hospital"},
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true
        },
        "preferences": {"preferredAccessTechnology": "5G"}
      }
    },
    "serviceConfiguration": {
      "orchestratorConfiguration": {
        "target": "t7-network-orchestrator",
        "profile": "hospital-surgical-slice-apply-v1",
        "resources": [
          {"resourceId": "SYD-PRI-01", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["primary"], "accessTechnology": "fibre", "relationships": [{"type": "pairedSecondary", "resourceId": "SYD-SEC-01"}]},
          {"resourceId": "SYD-SEC-01", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["secondary"], "accessTechnology": "5G", "relationships": [{"type": "protects", "resourceId": "SYD-PRI-01"}]}
        ]
      },
      "observerConfiguration": {
        "target": "t7-observability-platform",
        "profile": "critical-gold-assurance-observation-v1",
        "resources": [
          {"resourceId": "SYD-PRI-01", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["primary"], "metrics": ["latencyMs", "availabilityPercent", "jitterMs", "packetLossPercent"]},
          {"resourceId": "SYD-PRI-02", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["primary"], "metrics": ["latencyMs", "availabilityPercent", "jitterMs", "packetLossPercent"]},
          {"resourceId": "SYD-SEC-01", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["secondary"], "metrics": ["latencyMs", "availabilityPercent", "jitterMs", "packetLossPercent"]},
          {"resourceId": "SYD-SEC-02", "resourceType": "deliveryResource", "resourceClass": "critical-gold", "roles": ["secondary"], "metrics": ["latencyMs", "availabilityPercent", "jitterMs", "packetLossPercent"]}
        ]
      }
    },
    "references": {"correlationId": "corr-intent-create-001", "intent": {"id": "INT-HOSP-2026-001", "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"}, "intentSpecification": {"id": "ispec-hss-001", "specKey": "hospital-surgical-slice-spec", "version": "1.20", "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"}, "knowledgePlane": {"configId": "hospital-surgical-slice-kp-v1", "version": "1.0"}}
  }
}
```

### 10.6. Event-specific rules:

- `IntentNetworkReadyEvent` means service configuration is ready for change execution and apply, not that apply has succeeded.
- Preserve resolved context under `body.expression.context`; do not flatten `location`, `serviceType`, `serviceClass`, `targets`, `constraints`, or `preferences` as top-level fields.
- Use `serviceConfiguration` because the event carries the service apply and observation plan rather than low-level network configuration.
- Use `serviceConfiguration.orchestratorConfiguration` for apply and change-execution details.
- Use `serviceConfiguration.observerConfiguration` for assurance and monitoring details.
- Use `orchestratorConfiguration.target`, `orchestratorConfiguration.profile`, and `orchestratorConfiguration.resources`; do not repeat the `orchestrator` prefix inside the block.
- Use `observerConfiguration.target`, `observerConfiguration.profile`, and `observerConfiguration.resources`; do not repeat the `observer` prefix inside the block.
- `serviceConfiguration.orchestratorConfiguration.resources[]` contains only the optimiser-selected resources and configuration ready for apply.
- `serviceConfiguration.observerConfiguration.resources[]` contains the full assurance observation scope that IA or observer should monitor, including selected and non-selected resources.
- `serviceConfiguration.observerConfiguration.resources[].metrics` is a list of metric names to observe, not metric values.
- Do not include `applyOutcome`.
- Do not include service-apply QoS internals, bandwidth, routing policy, hops, or service attributes by default unless they are required by the change-execution contract.
- IA MS consumes this event; IA MS does not produce it.

## 11. IntentAssuranceEvent:

### 11.1. Producer:

```text
intent-assurance-ms
```

### 11.2. Current primary consumer:

```text
intent-controller-ms
```

### 11.3. Meaning:

IA MS reports curated assurance, apply, and runtime outcome truth. IC MS consumes this event and updates the external `Intent` and `IntentReport` projections.

### 11.4. Example body — active outcome:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "Active",
    "statusReason": "All observed resources in the assurance scope are operating within resolved runtime targets.",
    "expression": {
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "displayName": "Sydney-Main-Hospital"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    },
    "current": {
      "resources": [
        {
          "resourceId": "SYD-PRI-01",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": [
            "primary"
          ],
          "metrics": {
            "latencyMs": 8,
            "availabilityPercent": 99.995,
            "jitterMs": 1.5,
            "packetLossPercent": 0.005
          }
        },
        {
          "resourceId": "SYD-PRI-02",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": [
            "primary"
          ],
          "metrics": {
            "latencyMs": 9,
            "availabilityPercent": 99.996,
            "jitterMs": 1.4,
            "packetLossPercent": 0.004
          }
        },
        {
          "resourceId": "SYD-SEC-01",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": [
            "secondary"
          ],
          "metrics": {
            "latencyMs": 10,
            "availabilityPercent": 99.994,
            "jitterMs": 1.8,
            "packetLossPercent": 0.006
          }
        },
        {
          "resourceId": "SYD-SEC-02",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": [
            "secondary"
          ],
          "metrics": {
            "latencyMs": 9,
            "availabilityPercent": 99.997,
            "jitterMs": 1.2,
            "packetLossPercent": 0.003
          }
        }
      ]
    },
    "references": {
      "correlationId": "corr-intent-assurance-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      }
    }
  }
}
```

### 11.5. Example body — degraded outcome:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "Degraded",
    "statusReason": "Observed latency on one primary delivery resource is above the resolved target threshold.",
    "expression": {
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "displayName": "Sydney-Main-Hospital"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    },
    "current": {
      "resources": [
        {
          "resourceId": "SYD-PRI-01",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": [
            "primary"
          ],
          "metrics": {
            "latencyMs": 18,
            "availabilityPercent": 99.992,
            "jitterMs": 1.8,
            "packetLossPercent": 0.006
          }
        },
        {
          "resourceId": "SYD-PRI-02",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": [
            "primary"
          ],
          "metrics": {
            "latencyMs": 14,
            "availabilityPercent": 99.993,
            "jitterMs": 1.7,
            "packetLossPercent": 0.006
          }
        },
        {
          "resourceId": "SYD-SEC-01",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": [
            "secondary"
          ],
          "metrics": {
            "latencyMs": 12,
            "availabilityPercent": 99.994,
            "jitterMs": 1.8,
            "packetLossPercent": 0.006
          }
        },
        {
          "resourceId": "SYD-SEC-02",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": [
            "secondary"
          ],
          "metrics": {
            "latencyMs": 13,
            "availabilityPercent": 99.993,
            "jitterMs": 1.9,
            "packetLossPercent": 0.007
          }
        }
      ]
    },
    "references": {
      "correlationId": "corr-intent-assurance-002",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      }
    }
  }
}
```

### 11.6. Example body — failed outcome:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-003",
    "intentVersion": "v1",
    "lifecycleStatus": "Failed",
    "statusReason": "Apply failed and no safe active service state was confirmed.",
    "expression": {
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "displayName": "Sydney-Main-Hospital"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    },
    "current": {
      "resources": [
        {
          "resourceId": "SYD-PRI-01",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": ["primary"],
          "metrics": {}
        },
        {
          "resourceId": "SYD-PRI-02",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": ["primary"],
          "metrics": {}
        },
        {
          "resourceId": "SYD-SEC-01",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": ["secondary"],
          "metrics": {}
        },
        {
          "resourceId": "SYD-SEC-02",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "roles": ["secondary"],
          "metrics": {}
        }
      ]
    },
    "references": {
      "correlationId": "corr-intent-assurance-003",
      "intent": {
        "id": "INT-HOSP-2026-003",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-003"
      },
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      }
    }
  }
}
```

### 11.7. Example body — terminated outcome:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-004",
    "intentVersion": "v1",
    "lifecycleStatus": "Terminated",
    "statusReason": "Termination was confirmed by the change-execution system and no active observer scope remains.",
    "expression": {
      "context": {
        "targets": {},
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "displayName": "Sydney-Main-Hospital"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold"
        },
        "preferences": {}
      }
    },
    "current": {
      "resources": []
    },
    "references": {
      "correlationId": "corr-intent-assurance-004",
      "intent": {
        "id": "INT-HOSP-2026-004",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-004"
      },
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      }
    }
  }
}
```

### 11.8. Event-specific rules:

- Preserve resolved context under `body.expression.context`; do not flatten `location`, `serviceType`, `serviceClass`, `targets`, `constraints`, or `preferences` as top-level fields.
- Include resolved targets under `body.expression.context.targets` so control-loop consumers know which runtime objectives the observed metrics relate to.
- Preserve `constraints` and `preferences` under `body.expression.context` where useful for downstream decisions.
- Do not include `assuranceStatus` or `selectionStatus` by default; `lifecycleStatus` carries the assurance outcome.
- Use `current.resources[]` for the full observed resource and path set within assurance scope. For failed apply outcomes where no reliable telemetry was observed, resource entries may carry empty `metrics` objects to preserve the failed apply scope without inventing observed values. For confirmed termination, `current.resources[]` may be empty when no active observer scope remains.
- `current.resources[]` mirrors the observer scope received from `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[]`.
- Use `current.resources[].metrics` for neutral metric values for each observed resource.
- Do not include `evaluations` in `IntentAssuranceEvent` by default, including degraded state.
- IA MS reports lifecycle state, runtime targets, and observed metrics; II MS can use those metrics to trigger a new `IntentResolvedEvent`, and the optimiser evaluates feasibility/selection.
- Keep healthy and active assurance events scoped to the full observer scope, not only the selected apply resources.
- Do not include top-level `observedMetrics`; runtime values belong in `current.resources[].metrics`.
- Do not include `controlLoop` by default; downstream control-loop consumers derive the next action from the assurance event.
- Do not include a `knowledgePlane` reference by default; IA MS works from applied service configuration, observer scope, and resolved targets.

## 12. IntentCallbackEvent:

### 12.1. Producer:

```text
intent-callback-ms
```

### 12.2. Current primary consumer:

```text
intent-assurance-ms
```

### 12.3. Topic:

```text
t7.intent.management.events.callbacks
```

### 12.4. Kafka key:

```text
intentId
```

### 12.5. CloudEvents type:

```text
IntentCallbackEvent
```

### 12.6. Meaning:

ICB MS publishes accepted raw change execution and apply callbacks to the dedicated callback Kafka topic as `IntentCallbackEvent`.

IA MS consumes this event, validates and correlates intent state, maps raw source state into lifecycle and assurance meaning, and emits assurance outcomes where applicable.

### 12.7. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentCallbackEvent
ce-source: intent-callback-ms
ce-id: evt-intent-callback-001
ce-time: 2026-04-18T12:15:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 12.8. Example body:

```json
{
  "body": {
    "callbackId": "cb-sub-0001",
    "intentId": "INT-HOSP-2026-001",
    "callbackSource": "t7-network-orchestrator",
    "callbackTimestamp": "2026-04-18T12:14:58+10:00",
    "sourceState": {
      "state": "APPLIED",
      "reason": "Configuration applied successfully."
    },
    "sourceReference": {
      "id": "orch-job-9001",
      "href": "https://orchestrator.example.com/jobs/orch-job-9001"
    },
    "receivedAt": "2026-04-18T12:15:00+10:00",
    "details": {
      "message": "Raw callback payload retained by ICB MS according to retention policy."
    },
    "references": {
      "correlationId": "corr-intent-callback-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      }
    }
  }
}
```

### 12.9. Event-specific rules:

- `IntentCallbackEvent` is a raw callback relay event.
- ICB MS only accepts, persists, and publishes the callback.
- IA MS owns intent correlation, source-state mapping, skip or dead-letter decisions, and downstream assurance outcome publication.
- Use `callbackSource` for the external system or component that submitted the callback.
- Use `callbackTimestamp` for the timestamp supplied by that callback source.
- Use `receivedAt` for the ICB MS ingestion and acceptance timestamp. It is distinct from source-supplied `callbackTimestamp`.
- Use `sourceState` for the raw state and payload supplied by the callback source.
- Avoid retired source-specific callback state, source, and timestamp fields; use `callbackSource`, `callbackTimestamp`, and `sourceState`.
- Do not include lifecycle, service, optimisation, service-configuration, or assurance interpretation fields in this event.

### 12.10. ICB MS ownership boundary:

ICB MS does not validate intent existence, map source state, derive callback source type, decide actionability, or emit assurance and lifecycle events.

IA MS owns correlation, source-state mapping, skip or dead-letter decisions, and downstream assurance outcome publication.
