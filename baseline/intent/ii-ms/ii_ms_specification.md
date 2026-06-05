# II MS Specification

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Scope | Intent Intelligence MS internal event specification |
| Source of truth after commit | GitHub `baseline/intent/ii-ms/ii_ms_specification.md` |

## Table of contents:

- [1. Service identity:](#1-service-identity)
- [2. Boundary statement:](#2-boundary-statement)
  - [2.1. Required pre-resolution validation:](#21-required-pre-resolution-validation)
- [3. External API:](#3-external-api)
- [4. Event input: IntentValidatedEvent:](#4-event-input-intentvalidatedevent)
  - [4.1. Topic:](#41-topic)
  - [4.2. Producer:](#42-producer)
  - [4.3. Consumer:](#43-consumer)
  - [4.4. Meaning:](#44-meaning)
  - [4.5. Example headers:](#45-example-headers)
  - [4.6. Example body consumed by II MS:](#46-example-body-consumed-by-ii-ms)
  - [4.7. Input validation rules:](#47-input-validation-rules)
  - [4.8. Event input: OptimisationStatusChangeEvent:](#48-event-input-optimisationstatuschangeevent)
- [5. Semantic processing flow:](#5-semantic-processing-flow)
- [6. Target, constraint, and preference handling:](#6-target-constraint-and-preference-handling)
  - [6.1. Targets:](#61-targets)
  - [6.2. Constraints:](#62-constraints)
  - [6.3. Preferences:](#63-preferences)
- [7. Rejection reason codes:](#7-rejection-reason-codes)
- [8. Event output: IntentRejectedEvent:](#8-event-output-intentrejectedevent)
  - [8.1. Topic:](#81-topic)
  - [8.2. Producer:](#82-producer)
  - [8.3. Current primary consumer:](#83-current-primary-consumer)
  - [8.4. Meaning:](#84-meaning)
  - [8.5. Example headers:](#85-example-headers)
  - [8.6. Example body — service class unsupported:](#86-example-body-service-class-unsupported)
  - [8.7. Example body — redundancy capability unsupported:](#87-example-body-redundancy-capability-unsupported)
  - [8.8. Event-specific rules:](#88-event-specific-rules)
- [9. Event output: IntentResolvedEvent:](#9-event-output-intentresolvedevent)
  - [9.1. Topic:](#91-topic)
  - [9.2. Producer:](#92-producer)
  - [9.3. Current primary consumer:](#93-current-primary-consumer)
  - [9.4. Meaning:](#94-meaning)
  - [9.5. Example headers:](#95-example-headers)
  - [9.6. Example body — Sydney resolved:](#96-example-body-sydney-resolved)
  - [9.7. Example body — Melbourne resolved with open-ended time window:](#97-example-body-melbourne-resolved-with-open-ended-time-window)
  - [9.8. Event-specific rules:](#98-event-specific-rules)
- [10. Event output: IntentNetworkReadyEvent:](#10-event-output-intentnetworkreadyevent)
  - [10.1. Topic:](#101-topic)
  - [10.2. Producer:](#102-producer)
  - [10.3. Current primary consumer:](#103-current-primary-consumer)
  - [10.4. Meaning:](#104-meaning)
  - [10.5. Example headers:](#105-example-headers)
  - [10.6. Example body — network ready for change execution and assurance:](#106-example-body-network-ready-for-change-execution-and-assurance)
  - [10.7. Event-specific rules:](#107-event-specific-rules)
  - [10.8. Optimiser integration pattern for selected configuration:](#108-optimiser-integration-pattern-for-selected-configuration)
- [11. KP mapping rules:](#11-kp-mapping-rules)
- [12. Idempotency and ordering:](#12-idempotency-and-ordering)
- [13. Persistence:](#13-persistence)
- [14. Dependency behaviour:](#14-dependency-behaviour)
- [15. Observability:](#15-observability)
- [16. Security:](#16-security)
- [17. Contract summary:](#17-contract-summary)


## 1. Service identity:

| Item | Baseline |
|---|---|
| Full name | Intent Intelligence MS |
| Short name | II MS |
| Service name | `intent-intelligence-ms` |
| Domain | Intent Domain |
| Primary responsibility | Semantic interpretation, Knowledge Plane-backed validation, required pre-resolution validation, candidate-level semantic resolution, and service-ready preparation |
| External API | None |
| Primary input events | `IntentValidatedEvent`; `OptimisationStatusChangeEvent` after ICB MS callback ingestion |
| Output events | `IntentRejectedEvent`, `IntentResolvedEvent`, `IntentNetworkReadyEvent` |

## 2. Boundary statement:

II MS consumes syntactically admitted runtime intent facts from IC MS and performs semantic interpretation plus Knowledge Plane-backed resolution and required pre-resolution validation.

II MS emits:

- `IntentRejectedEvent` when the intent cannot be semantically, policy, or capability resolved
- `IntentResolvedEvent` when the intent can proceed to the next internal fulfilment stage as a candidate-level semantic-resolution handoff
- `IntentNetworkReadyEvent` when service-ready preparation has produced the concrete change-execution and observation configuration required by IA MS

II MS does not own runtime `Intent` REST APIs, external lifecycle projection, downstream selection and fulfilment decisions, assurance truth, callback ingestion, change execution, or KP governance.

The baseline surgical hospital slice is an illustrative runtime example used to make the II MS semantic interpretation and resolution contract concrete. It is not the only supported runtime Intent type, IntentSpecification, service class, schema, expression IRI, location, service type, Knowledge Plane profile, pre-resolution validation path, or deployment profile. Other runtime Intents may use different targets, constraints, preferences, expression schemas, service types, priorities, resources, governed validation sources, and governance profiles while following the same II MS contract rules.


### 2.1. Required pre-resolution validation:

Knowledge Plane is the primary governed knowledge source in the current hospital surgical slice baseline, but II MS resolution is not limited to Knowledge Plane and optimiser-related references. Depending on the intent domain, II MS may need to perform additional pre-resolution validation required to meet the intent accurately. This validation may consult approved T7 platform services, inventory systems, policy services, topology services, capacity systems, service catalogues, fulfilment systems, or other governed domain sources before II MS emits a semantic outcome.

These systems provide pre-resolution facts used by II MS during semantic interpretation, capability validation, policy validation, candidate discovery, or service-ready preparation. They do not own the external runtime `Intent` lifecycle and they do not change the II-owned event model.

II MS must curate and normalise facts returned by pre-resolution validation sources before carrying them forward. Raw source-system payloads, credentials, endpoint details, internal error details, and implementation-specific fields must not be exposed in `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent`.

---

## 3. External API:

II MS has no external TMF-compliant API and no consumer-facing REST contract in the active baseline. II MS is not exposed through NGW, OEX, public API gateways, or partner-facing API channels.

II MS registers or supplies the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, to the Optimiser platform for optimisation outcome delivery. Optimiser callback ingestion is owned by ICB MS. ICB MS places the received `OptimisationStatusChangeEvent` on Kafka for II MS consumption. The exact ICB optimiser-callback ingestion and relay contract must be confirmed during ICB MS refinement.

Operational probes such as health, readiness, and metrics are platform-internal only. They are for Kubernetes and platform operations and must not be treated as external product APIs or TMF921 resource APIs.

Example internal-only platform probes:

```http
GET /health
GET /ready
GET /metrics
```

These endpoints, if implemented, are restricted to the platform and runtime network plane and are not externally exposed.

---

## 4. Event input: IntentValidatedEvent:

### 4.1. Topic:

```text
t7.intent.management.events
```

The shared topic is the current baseline; event type and `ce-source` provide ownership boundaries. Future topic splitting may be introduced without changing II MS event payload contracts.

### 4.2. Producer:

```text
intent-controller-ms
```

### 4.3. Consumer:

```text
intent-intelligence-ms
```

### 4.4. Meaning:

`IntentValidatedEvent` means IC MS has admitted a runtime Intent after syntactic validation.

It does not mean semantic feasibility, policy acceptance, service availability, or downstream fulfilment success.

### 4.5. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentValidatedEvent
ce-source: intent-controller-ms
ce-id: evt-intent-validated-001
ce-time: 2026-04-18T12:00:01+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 4.6. Example body consumed by II MS:

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
          "redundancyRequired": true,
          "timeWindow": {
            "startDateTime": "2026-04-18T12:00:00+10:00",
            "endDateTime": "2026-04-18T14:00:00+10:00"
          }
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

### 4.7. Input validation rules:

II MS expects:

| Field | Rule |
|---|---|
| `body.intentId` | Required |
| `body.intentVersion` | Required where versioned runtime intent is used |
| `body.intentSpecification.id` | Required |
| `body.expression.iri` | Required |
| `body.expression.context` | Required |
| `body.expression.context.constraints.location.locationId` | Required |
| `body.expression.context.constraints.serviceType` | Required |
| `body.expression.context.constraints.serviceClass` | Required |
| `body.expression.context.targets` | Required for downstream-capable intents |
| `body.expression.context.constraints` | Required when hard constraints exist |
| `body.expression.context.preferences` | Optional |
| `body.references.correlationId` | Required |

II MS does not expect the external TMF `Intent.expression` wrapper in internal events. Internal events carry native JSON under `body.expression`, but that native expression must include the admitted `expression.iri` and preserve the canonical `context.targets`, `context.constraints`, and `context.preferences` grouping established by ID MS and IC MS. II MS must not re-resolve the governing `IntentSpecification` by IRI alone; `intentSpecification.id` remains the selected specification reference.

---

### 4.8. Event input: OptimisationStatusChangeEvent:

For optimisation-backed selection, II MS consumes `OptimisationStatusChangeEvent` from Kafka after ICB MS has ingested the external optimiser callback and relayed the event internally. This is an inbound internal Kafka event for II MS, not an external II MS endpoint.

#### Topic:

```text
t7.intent.management.events
```

#### Producer:

```text
intent-callback-ms
```

#### Consumer:

```text
intent-intelligence-ms
```

#### Meaning:

`OptimisationStatusChangeEvent` means the approved Optimiser platform has returned an optimisation outcome for a previously submitted `POST /optimisation` request. II MS consumes the event, correlates it to the original `intentId`, `intentVersion`, `correlationId`, and optimisation id, and packages the governed selected configuration into `IntentNetworkReadyEvent` when the outcome is complete and valid.

It does not mean network apply has succeeded, and it does not make II MS the owner of the optimiser lifecycle or optimisation algorithm.

#### Example Kafka headers:

```http
ce-specversion: 1.0
ce-type: OptimisationStatusChangeEvent
ce-source: intent-callback-ms
ce-id: evt-optimisation-status-001
ce-time: 2026-04-18T12:03:30+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

#### Example body consumed by II MS:

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
      "resultSummary": {
        "outcome": "COMPLETED",
        "summary": "Optimisation completed successfully. Selected primary and secondary resources for the Sydney hospital surgical slice."
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

#### Input validation rules:

II MS expects:

| Field | Rule |
|---|---|
| Kafka `ce-type` | Must be `OptimisationStatusChangeEvent` |
| Kafka `ce-source` | Must identify ICB MS, normally `intent-callback-ms` |
| Kafka `ce-subject` | Must carry the related runtime `intentId` |
| `event.optimisation.id` | Required optimisation id for correlation |
| `event.optimisation.newLifecycleStatus` | Required optimiser lifecycle state |
| `event.optimisation.sourceContext.resource.id` | Required runtime `intentId` |
| `event.optimisation.sourceContext.intentVersion` | Required where runtime intent versioning is used |
| `event.optimisation.sourceContext.correlationId` | Required correlation id |
| `event.optimisation.selectedConfiguration` | Required when `newLifecycleStatus` is `COMPLETED` |

II MS must process this event idempotently. Duplicate optimiser status events must not produce duplicate `IntentNetworkReadyEvent` publications.

## 5. Semantic processing flow:

| Step | Action |
|---|---|
| 1 | Consume `IntentValidatedEvent`; for optimisation-backed selection, also consume `OptimisationStatusChangeEvent` from Kafka after ICB MS callback ingestion |
| 2 | Check idempotency using CloudEvents `ce-id` and intent identity |
| 3 | Parse admitted internal `expression.context` |
| 4 | Resolve `context.constraints.location` from KP or another approved pre-resolution validation source where required |
| 5 | Resolve `context.constraints.serviceType` and `context.constraints.serviceClass` from KP, catalogue, policy, or another approved pre-resolution validation source where required |
| 6 | Validate service capability and status |
| 7 | Validate hard constraints, including priority, redundancy, and time window where present |
| 8 | Validate requested targets are supported for the service class |
| 9 | Preserve preferences for downstream selection guidance |
| 10 | Resolve valid resource set from KP, inventory, topology, capacity, or other approved pre-resolution validation sources after scope and policy filtering |
| 11 | Emit `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` through the II outbox, depending on the resolved milestone |

---

## 6. Target, constraint, and preference handling:

### 6.1. Targets:

Targets are measurable runtime objectives.

Supported baseline target fields:

```text
maxLatencyMs
minAvailabilityPercent
maxJitterMs
maxPacketLossPercent
```

II MS validates that target names and value types are supported for the requested service or service class. II MS preserves target names and values under `expression.context.targets`.

### 6.2. Constraints:

Constraints are hard runtime requirements.

Supported baseline constraint fields:

```text
location
serviceType
serviceClass
priority
redundancyRequired
timeWindow
```

`location`, `serviceType`, and `serviceClass` are part of `expression.context.constraints`, not sibling fields beside `targets`, `constraints`, and `preferences`.

When `constraints.timeWindow` is present:

- `startDateTime` is required
- `endDateTime` is optional
- `endDateTime` is included in the schema as an allowed optional property, not a mandatory property

### 6.3. Preferences:

Preferences are soft runtime selection guidance.

Supported baseline preference fields:

```text
preferredAccessTechnology
```

II MS preserves preferences for downstream selection guidance. II MS does not reject the intent only because a preference cannot be satisfied unless policy later promotes that preference into a hard constraint.

---

## 7. Rejection reason codes:

II MS reason codes must be expressed as intent-domain semantic, policy, capability, or processing issues. II MS must not expose downstream implementation vocabulary or use downstream-selection-specific reason codes.

| Reason code | Meaning |
|---|---|
| `SEMANTIC_LOCATION_UNSUPPORTED` | Requested location cannot be resolved or is unsupported for this intent domain |
| `SEMANTIC_LOCATION_TYPE_UNSUPPORTED` | Requested location type is not supported |
| `SEMANTIC_SERVICE_CLASS_UNSUPPORTED` | Requested service class is not supported |
| `SEMANTIC_REQUIRED_CONTEXT_MISSING` | Required `expression.context` information is missing |
| `SEMANTIC_EXPRESSION_UNSUPPORTED` | The admitted expression cannot be interpreted into canonical domain terms |
| `SEMANTIC_INTENT_CONTRADICTORY` | Requested targets and constraints are contradictory in the intent domain |
| `POLICY_LOCATION_NOT_ALLOWED` | Policy rejects the requested location |
| `POLICY_SERVICE_CLASS_NOT_ALLOWED` | Policy rejects the requested service class |
| `POLICY_PRIORITY_NOT_ALLOWED` | Policy rejects the requested priority |
| `POLICY_TIME_WINDOW_NOT_ALLOWED` | Policy rejects the requested time window |
| `KNOWLEDGE_LOOKUP_ERROR` | KP lookup failed or returned insufficient trusted information |
| `PROCESSING_ERROR` | II MS failed due to an internal processing error |

Capability and resource shortfall must be expressed as an intent-domain semantic or policy issue, not as a downstream-selection-specific issue.

---

## 8. Event output: IntentRejectedEvent:

### 8.1. Topic:

```text
t7.intent.management.events
```

### 8.2. Producer:

```text
intent-intelligence-ms
```

### 8.3. Current primary consumer:

```text
intent-controller-ms
```

### 8.4. Meaning:

II MS emits `IntentRejectedEvent` when the admitted intent is syntactically valid but cannot be semantically, policy, or capability resolved.

### 8.5. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentRejectedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-rejected-001
ce-time: 2026-04-18T12:01:00+10:00
ce-subject: INT-HOSP-2026-002
content-type: application/json
```

### 8.6. Example body — service class unsupported:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-002",
    "intentVersion": "v1",
    "lifecycleStatus": "Rejected",
    "reasonCode": "SEMANTIC_SERVICE_CLASS_UNSUPPORTED",
    "statusReason": "Surgical critical-gold connectivity is not supported for the requested location and service context.",
    "expression": {
      "context": {
        "constraints": {
          "location": {
            "locationId": "AU-QLD-BNE-HOSP-201",
            "displayName": "Brisbane-Main-Hospital"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold"
        }
      }
    },
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

### 8.7. Example body — redundancy capability unsupported:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-003",
    "intentVersion": "v1",
    "lifecycleStatus": "Rejected",
    "reasonCode": "SEMANTIC_INTENT_CONTRADICTORY",
    "statusReason": "Redundancy was required by the intent, but the resolved domain context cannot satisfy the requested redundant capability.",
    "expression": {
      "context": {
        "constraints": {
          "location": {
            "locationId": "AU-QLD-BNE-HOSP-201",
            "displayName": "Brisbane-Main-Hospital"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true
        }
      }
    },
    "references": {
      "correlationId": "corr-intent-create-003",
      "intent": {
        "id": "INT-HOSP-2026-003",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-003"
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

### 8.8. Event-specific rules:

- Use `lifecycleStatus: Rejected`.
- Include `reasonCode` and `statusReason`.
- Include resolved or partially resolved semantic context under `expression.context`.
- Include `expression.context.constraints` when needed to explain the rejection, such as redundancy failure.
- Do not include downstream selection details.
- Do not include assurance details.
- Do not include raw KP payloads.
- Preserve the canonical `context.targets`, `context.constraints`, and `context.preferences` grouping when expression details are included.

---

## 9. Event output: IntentResolvedEvent:

### 9.1. Topic:

```text
t7.intent.management.events
```

### 9.2. Producer:

```text
intent-intelligence-ms
```

### 9.3. Current primary consumer:

```text
optimiser-controller-ms
```

### 9.4. Meaning:

II MS emits `IntentResolvedEvent` when the admitted intent has been semantically resolved into a canonical handoff that can proceed to the next internal fulfilment stage.

### 9.5. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentResolvedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-resolved-001
ce-time: 2026-04-18T12:03:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 9.6. Example body — Sydney resolved:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "InProgress",
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
          "redundancyRequired": true,
          "timeWindow": {
            "startDateTime": "2026-04-18T12:00:00+10:00",
            "endDateTime": "2026-04-18T14:00:00+10:00"
          }
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
      {
        "resourceId": "SYD-PRI-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
        "accessTechnology": "fibre",
        "metrics": {
          "latencyMs": 7,
          "availabilityPercent": 99.996,
          "jitterMs": 1.1,
          "packetLossPercent": 0.004
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
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
        "accessTechnology": "5G",
        "metrics": {
          "latencyMs": 8,
          "availabilityPercent": 99.995,
          "jitterMs": 1.5,
          "packetLossPercent": 0.005
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
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "metrics": {
          "latencyMs": 10,
          "availabilityPercent": 99.994,
          "jitterMs": 1.8,
          "packetLossPercent": 0.006
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
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "fibre",
        "metrics": {
          "latencyMs": 9,
          "availabilityPercent": 99.997,
          "jitterMs": 1.2,
          "packetLossPercent": 0.003
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

### 9.7. Example body — Melbourne resolved with open-ended time window:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-004",
    "intentVersion": "v1",
    "lifecycleStatus": "InProgress",
    "expression": {
      "context": {
        "targets": {
          "maxLatencyMs": 12,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "constraints": {
          "location": {
            "locationId": "AU-VIC-MEL-HOSP-101",
            "displayName": "Melbourne-Main-Hospital"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true,
          "timeWindow": {
            "startDateTime": "2026-04-18T12:00:00+10:00"
          }
        },
        "preferences": {
          "preferredAccessTechnology": "fibre"
        }
      }
    },
    "references": {
      "correlationId": "corr-intent-create-004",
      "intent": {
        "id": "INT-HOSP-2026-004",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-004"
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
      {
        "resourceId": "MEL-PRI-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
        "accessTechnology": "fibre",
        "metrics": {
          "latencyMs": 9,
          "availabilityPercent": 99.995,
          "jitterMs": 1.4,
          "packetLossPercent": 0.005
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "MEL-SEC-01"
          },
          {
            "type": "pairedSecondary",
            "resourceId": "MEL-SEC-02"
          }
        ]
      },
      {
        "resourceId": "MEL-PRI-02",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
        "accessTechnology": "5G",
        "metrics": {
          "latencyMs": 10,
          "availabilityPercent": 99.994,
          "jitterMs": 1.6,
          "packetLossPercent": 0.006
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "MEL-SEC-02"
          }
        ]
      },
      {
        "resourceId": "MEL-SEC-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "metrics": {
          "latencyMs": 12,
          "availabilityPercent": 99.993,
          "jitterMs": 1.9,
          "packetLossPercent": 0.007
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "MEL-PRI-01"
          }
        ]
      },
      {
        "resourceId": "MEL-SEC-02",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "fibre",
        "metrics": {
          "latencyMs": 11,
          "availabilityPercent": 99.996,
          "jitterMs": 1.3,
          "packetLossPercent": 0.004
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "MEL-PRI-02"
          }
        ]
      }
    ]
  }
}
```

### 9.8. Event-specific rules:

- Preserve resolved semantic context under `expression.context`.
- Preserve `targets`, `constraints`, and `preferences` as first-class semantic buckets under `expression.context`.
- Do not flatten `location`, `serviceType`, or `serviceClass` into top-level event fields.
- Do not include direct top-level `priority`, `preferredAccessTechnology`, or `redundancyRequired` outside the buckets.
- Do not include `provider` by default.
- Do not include downstream-selected resources; all resources in `IntentResolvedEvent.resources` are applicable and apply-capable resources known for downstream consideration by `optimiser-controller-ms`, not final selected output.
- Include generic `metrics` values for applicable resources using neutral metric names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.
- Do not encode metric origin or lifecycle context into wrappers or field names such as `metrics.benchmark`, `metrics.telemetry`, `latencyBenchmarkMs`, or `currentLatencyMs`.

---

## 10. Event output: IntentNetworkReadyEvent:

### 10.1. Topic:

```text
t7.intent.management.events
```

### 10.2. Producer:

```text
intent-intelligence-ms
```

### 10.3. Current primary consumer:

```text
intent-assurance-ms
```

### 10.4. Meaning:

II MS emits `IntentNetworkReadyEvent` after semantic resolution and service-ready preparation have produced the concrete change-execution and observation configuration required by IA MS.

`IntentNetworkReadyEvent` does not mean network apply has succeeded. It means the service configuration and resource set has been prepared for change execution and apply and assurance observation.

IntentNetworkReadyEvent may be emitted only after II MS has received or derived a governed selected configuration from the authorised downstream selection or optimisation path. II MS does not own the optimisation algorithm or optimiser backend. II MS owns packaging the selected configuration into the service-ready event for IA MS.

For optimisation-backed selection, II MS uses the approved Optimiser platform integration pattern: a governed REST request to `POST /optimisation`, with the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, registered or supplied as the optimiser outcome target. The Optimiser platform sends `OptimisationStatusChangeEventRequest` to the ICB-owned callback submission URL. ICB MS ingests the callback request and publishes `OptimisationStatusChangeEvent` to Kafka for II MS consumption. The Optimiser platform owns optimisation execution, selection logic, solver models, and optimiser lifecycle. II MS owns submitting the governed request, correlating the Kafka-delivered optimiser outcome, and packaging that selected configuration into `IntentNetworkReadyEvent` for IA MS.

The governed `POST /optimisation` request must be submitted through the II MS optimisation API outbox pattern. II MS persists the semantic decision, `intent_optimisation_correlation` state, and pending optimisation API outbox entry before any outbound REST attempt. A dedicated optimisation API outbox worker submits the request, applies bounded retries and circuit-breaker behaviour, records the accepted optimisation id or failure state, and updates the correlation record used later when `OptimisationStatusChangeEvent` arrives from Kafka.

### 10.5. Example headers:

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-network-ready-001
ce-time: 2026-04-18T12:04:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 10.6. Example body — network ready for change execution and assurance:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "InProgress",
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
          "redundancyRequired": true,
          "timeWindow": {
            "startDateTime": "2026-04-18T12:00:00+10:00",
            "endDateTime": "2026-04-18T14:00:00+10:00"
          }
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    },
    "serviceConfiguration": {
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
    }
  }
}
```

### 10.7. Event-specific rules:

- `IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.
- `IntentNetworkReadyEvent` is consumed by `intent-assurance-ms`.
- Consumer identity does not change producer ownership.
- IA MS consumes this event; IA MS must not produce it.
- `IntentNetworkReadyEvent` means service configuration is ready for change execution and apply, not that apply has succeeded.
- Carry the resolved runtime `body.expression.context` with `targets`, `constraints`, and `preferences`; IA MS stores this as assurance context.
- Use `serviceConfiguration.orchestratorConfiguration` for apply and change-execution details.
- Use `serviceConfiguration.observerConfiguration` for assurance and monitoring details.
- `serviceConfiguration.orchestratorConfiguration.resources[]` carries only the optimiser-selected network-ready configuration and resources that must be applied by the change-execution layer; it includes resource details, topology, roles, and change-execution-relevant information, but not metric values.
- `serviceConfiguration.observerConfiguration.resources[]` carries the full assurance observation scope, including selected resources and any additional primary and secondary alternatives that IA must observe; it uses `metrics` as a list of metric names IA should observe, not a value object.
- When optimisation-backed selection is required, the selected configuration must come from the approved Optimiser path: `POST /optimisation`, followed by ICB-ingested `OptimisationStatusChangeEventRequest` and ICB-relayed `OptimisationStatusChangeEvent` on Kafka.
- Do not include `applyOutcome`.
- Do not use this event as a substitute for `IntentAssuranceEvent`; IA MS remains responsible for apply outcome interpretation and runtime assurance truth.


### 10.8. Optimiser integration pattern for selected configuration:

When an intent requires optimisation-backed resource selection, II MS records a pending optimisation request in the optimisation API outbox for submission to the Optimiser platform using `POST /optimisation`. The request carries the resolved `body.expression.context`, candidate resources, targets, constraints, preferences, and correlation metadata from the admitted and resolved intent. The outbound REST submission is performed by an API outbox worker using a stable idempotency key, not directly inside the inbound event consumer transaction.

The Optimiser platform performs optimisation execution and returns the selected configuration asynchronously by sending `OptimisationStatusChangeEventRequest` to the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, registered or supplied by II MS. ICB MS ingests the callback request and relays `OptimisationStatusChangeEvent` to Kafka for II MS consumption.

II MS does not own the optimisation algorithm, optimiser backend, solver model, or optimiser lifecycle. II MS owns submitting the governed optimisation request, correlating the Kafka-delivered optimiser outcome, and packaging the returned selected configuration into `IntentNetworkReadyEvent` for IA MS.

The optimisation expression may transform the canonical `body.expression.context` object into an optimiser-specific problem expression shape. Any such transformation must be explicit, traceable, and must not change the semantic meaning of targets, constraints, preferences, or resources.

Example `POST /optimisation` request body:

```json
{
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
  "optimisationSpecification": {
    "id": "ospec-hss-resource-selection-001",
    "specKey": "optimisation-spec-surgical-routing",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },
  "name": "Hospital surgical slice resource selection optimisation",
  "description": "Optimise candidate resource selection for the Sydney hospital surgical slice workload before II MS emits IntentNetworkReadyEvent.",
  "priority": "1",
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/ontology/optimisation/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "@context": {
        "opt": "https://mycsp.com.au/ontology/optimisation#",
        "context": "opt:context",
        "targets": "opt:targets",
        "constraints": "opt:constraints",
        "preferences": "opt:preferences",
        "resources": "opt:resources"
      },
      "@type": "opt:OptimisationProblem",
      "context": {
        "targets": [
          {
            "maxLatencyMs": 10,
            "minAvailabilityPercent": 99.99,
            "maxJitterMs": 2,
            "maxPacketLossPercent": 0.01
          }
        ],
        "constraints": [
          {
            "location": {
              "locationId": "AU-NSW-SYD-HOSP-001",
              "displayName": "Sydney-Main-Hospital"
            },
            "serviceType": "surgical-connectivity",
            "serviceClass": "critical-gold",
            "priority": "critical",
            "redundancyRequired": true,
            "timeWindow": {
              "startDateTime": "2026-04-18T12:00:00+10:00",
              "endDateTime": "2026-04-18T14:00:00+10:00"
            }
          }
        ],
        "preferences": [
          {
            "preferredAccessTechnology": "5G",
            "optimiseFor": "lowest-latency"
          }
        ],
        "resources": [
          {
            "resourceId": "SYD-PRI-01",
            "resourceType": "deliveryResource",
            "resourceClass": "critical-gold",
            "roles": [
              "primary"
            ],
            "accessTechnology": "fibre",
            "metrics": {
              "latencyMs": 7,
              "availabilityPercent": 99.996,
              "jitterMs": 1.1,
              "packetLossPercent": 0.004
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
            "resourceType": "deliveryResource",
            "resourceClass": "critical-gold",
            "roles": [
              "primary"
            ],
            "accessTechnology": "5G",
            "metrics": {
              "latencyMs": 8,
              "availabilityPercent": 99.995,
              "jitterMs": 1.5,
              "packetLossPercent": 0.005
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
            "resourceType": "deliveryResource",
            "resourceClass": "critical-gold",
            "roles": [
              "secondary"
            ],
            "accessTechnology": "5G",
            "metrics": {
              "latencyMs": 10,
              "availabilityPercent": 99.994,
              "jitterMs": 1.8,
              "packetLossPercent": 0.006
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
            "resourceType": "deliveryResource",
            "resourceClass": "critical-gold",
            "roles": [
              "secondary"
            ],
            "accessTechnology": "fibre",
            "metrics": {
              "latencyMs": 9,
              "availabilityPercent": 99.997,
              "jitterMs": 1.2,
              "packetLossPercent": 0.003
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
  },
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json"
}
```

Example Kafka headers for the optimiser outcome event consumed by II MS after ICB MS relay:

```http
ce-specversion: 1.0
ce-type: OptimisationStatusChangeEvent
ce-source: intent-callback-ms
ce-id: evt-optimisation-status-001
ce-time: 2026-04-18T12:03:30+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

Example optimiser outcome event body ingested by ICB MS and relayed to Kafka for II MS consumption:

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
      "resultSummary": {
        "outcome": "COMPLETED",
        "summary": "Optimisation completed successfully. Selected primary and secondary resources for the Sydney hospital surgical slice."
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

---

## 11. KP mapping rules:

II MS maps KP data into event-facing resource entries.

| KP field | Event-facing treatment |
|---|---|
| `resourceId` | Include as `resourceId` |
| `resourceType` | Include as `resourceType`, using controlled resource vocabulary such as `deliveryResource` |
| `resourceClass` | Include as `resourceClass`, using controlled class vocabulary such as `critical-gold` |
| `resourceRoles` | Map to `roles` |
| `accessTechnology` | Include if useful to preference handling |
| `metrics` | Map supported values into neutral event-facing metric fields such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent` in `IntentResolvedEvent.resources[]`; use metric names only in `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[].metrics` |
| `relationships` | Include only downstream-relevant relationships |
| `provider` | Do not include by default; KP inventory metadata only |

KP freshness rules:

- II MS must apply a configured KP freshness policy before using KP facts for safety-critical semantic resolution or service-ready packaging.
- If KP data is stale, missing, or cannot be refreshed within the configured freshness window, II MS must fail closed for the affected runtime version and use an intent-domain reason such as `KNOWLEDGE_LOOKUP_ERROR`.
- If optimisation or callback wait time exceeds the configured KP freshness threshold, II MS must re-check the current KP snapshot and version before packaging `IntentNetworkReadyEvent`.

---

## 12. Idempotency and ordering:

II MS must support at-least-once event delivery.

Rules:

- Deduplicate consumed `IntentValidatedEvent` by `ce-id` and event id.
- Deduplicate consumed `OptimisationStatusChangeEvent` by CloudEvents `ce-id`, optimisation id, event type, and intentId and intentVersion where available.
- Duplicate `OptimisationStatusChangeEvent` instances must not produce duplicate `IntentNetworkReadyEvent` publications.
- A stale optimiser outcome must not overwrite newer semantic or service-ready state for the same intentId and intentVersion.
- If IC MS supersedes, updates, or cancels a runtime intent while II MS or Optimiser processing is in flight, II MS must not publish a milestone event for the older or non-current runtime version. Late optimiser outcomes for that version are audit and correlation records only.
- Store semantic decision state per `intentId` and runtime version.
- Avoid emitting duplicate `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` for the same input event or milestone.
- If a newer runtime intent version exists, stale events must not overwrite newer resolution state.

---

## 13. Persistence:

Suggested tables:

| Table | Purpose |
|---|---|
| `intent_resolution_state` | Current semantic resolution state per intent and version |
| `intent_resolution_idempotency` | Consumed event deduplication |
| `intent_optimisation_correlation` | Tracks II-submitted optimisation requests, optimisation id, intentId, intentVersion, correlationId, ICB callback submission target reference where applicable, optimiser outcome state, and correlation of ICB-relayed `OptimisationStatusChangeEvent` outcomes back to the originating `POST /optimisation` request. |
| `intent_optimisation_api_outbox` | Durable API outbox for II-submitted `POST /optimisation` requests, including request body, idempotency key, callback submission URL, request status, retry count, next retry time, accepted optimisation id, and error/failure state. |
| `intent_resolution_audit` | KP lookup, policy, semantic, and rejection decision trail |
| `intent_resolution_outbox` | Reliable publication of II-owned events, including `IntentRejectedEvent`, `IntentResolvedEvent`, and `IntentNetworkReadyEvent` |
| `intent_resolution_dead_letter` | Required minimum failed and unprocessable event handling for exhausted `IntentValidatedEvent` and `OptimisationStatusChangeEvent` processing, including event id, event type, intentId, intentVersion where available, failure reason, retry count, payload hash, and replay and operational status. |
| `shedlock` | Relay coordination if clustered outbox relay is used |

---

## 14. Dependency behaviour:

| Dependency | Behaviour |
|---|---|
| II DB unavailable | Do not process or acknowledge event beyond retry and dead-letter policy |
| KP unavailable or stale | Fail closed for semantic resolution or service-ready packaging when fresh KP facts are required; refresh, retry, or dead-letter according to policy |
| Kafka unavailable | Use outbox relay retry; do not lose resolved or rejected outcome |
| Cache unavailable | Bypass cache and use KP or the relevant approved pre-resolution validation source where safe |
| Optimisation API outbox unavailable | Prevents outbound `POST /optimisation` submission for optimisation-backed selection. II MS keeps the optimisation request pending and must not emit `IntentNetworkReadyEvent` until the API outbox worker successfully submits the request and the correlated optimiser outcome is received through ICB MS and Kafka. |
| Optimiser / ICB optimiser callback path unavailable | Not a dependency for semantic resolution or `IntentResolvedEvent` emission. For optimisation-backed selection, `POST /optimisation` failure from the API outbox worker, missing optimiser callback through ICB MS, or missing `OptimisationStatusChangeEvent` from Kafka prevents `IntentNetworkReadyEvent` emission until configured retry, callback timeout, governed failure/rejection policy, or operational handling applies. |
| Downstream fulfilment stage unavailable | Not an II MS dependency for emitting `IntentResolvedEvent`; service-ready preparation must complete before emitting `IntentNetworkReadyEvent` |

---

## 15. Observability:

Recommended logs and metrics:

```text
ii_ms_intent_validated_consumed_count
ii_ms_intent_resolved_count
ii_ms_intent_network_ready_count
ii_ms_intent_rejected_count
ii_ms_kp_lookup_error_count
ii_ms_resolution_failure_count
ii_ms_outbox_pending_count
ii_ms_outbox_publish_failure_count
ii_ms_duplicate_event_count
ii_ms_optimisation_timeout_count
ii_ms_stale_event_ignored_count
ii_ms_kp_stale_or_refresh_failure_count
ii_ms_dead_letter_count
```

All logs and traces must include `correlationId` and `intentId` where available.

---

## 16. Security:

II MS is internal only.

Rules:

- consume only from trusted internal event backbone
- use workload identity for KP access
- expose no public, NGW, OEX, partner, or consumer-facing REST API
- restrict any platform probes to the internal runtime and network plane
- no external user and business authorisation in II MS
- do not include secrets, tokens, credentials, or raw stack traces in event payloads
- audit semantic and policy rejections where required

---

## 17. Contract summary:

II MS consumes `IntentValidatedEvent` and, for optimisation-backed selection, `OptimisationStatusChangeEvent` after ICB MS callback ingestion. It validates and resolves the admitted expression using Knowledge Plane data, domain knowledge, and any required use-case-specific pre-resolution validation sources, preserves `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences`, and emits `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` depending on the resolved milestone.

II MS must fail closed for stale KP facts, stale runtime versions, duplicate optimiser outcomes, missing optimiser callbacks, failed optimisation outcomes, and cancelled or superseded intents. These conditions must not produce unsafe or duplicate `IntentNetworkReadyEvent` publications.

`IntentRejectedEvent` is the semantic, policy, or capability rejection handoff. IC MS consumes it and projects the external runtime `Intent` lifecycle accordingly.

`IntentResolvedEvent` is the candidate-level semantic-resolution handoff. It carries canonical service context and the full valid, applicable, and apply-capable resource set for downstream consideration by `optimiser-controller-ms`. It includes generic metric values for applicable resources using neutral metric names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`. It is not the final service-ready/apply-ready handoff.

`IntentNetworkReadyEvent` is the service-ready preparation handoff to IA MS. It carries the optimiser-selected apply and change-execution configuration in `serviceConfiguration.orchestratorConfiguration` and the full assurance observation scope in `serviceConfiguration.observerConfiguration`, and it does not mean network apply has succeeded. It does not carry metric values in `serviceConfiguration.orchestratorConfiguration.resources[]`; `serviceConfiguration.observerConfiguration.resources[].metrics` names the metrics IA should observe.
