# II MS Specification

## Service identity

| Item | Baseline |
|---|---|
| Full name | Intent Intelligence MS |
| Short name | II MS |
| Service name | `intent-intelligence-ms` |
| Domain | Intent Domain |
| Primary responsibility | Semantic interpretation, Knowledge Plane-backed validation, candidate-level semantic resolution, and service-ready preparation |
| External API | None |
| Primary input event | `IntentValidatedEvent` |
| Output events | `IntentRejectedEvent`, `IntentResolvedEvent`, `IntentNetworkReadyEvent` |

## Boundary statement

II MS consumes syntactically admitted runtime intent facts from IC MS and performs semantic interpretation and Knowledge Plane-backed resolution.

II MS emits:

- `IntentRejectedEvent` when the intent cannot be semantically, policy, or capability resolved
- `IntentResolvedEvent` when the intent can proceed to the next internal fulfilment stage as a candidate-level semantic-resolution handoff
- `IntentNetworkReadyEvent` when service-ready preparation has produced the concrete change-execution and observation configuration required by IA MS

II MS does not own runtime `Intent` REST APIs, external lifecycle projection, downstream selection/fulfilment decisions, assurance truth, callback ingestion, change execution, or KP governance.

---

## 1. External API

II MS has no external TMF-compliant API and no consumer-facing REST contract in the active baseline. II MS is not exposed through NGW, OEX, public API gateways, or partner-facing API channels.

Operational probes such as health, readiness, and metrics are platform-internal only. They are for Kubernetes/platform operations and must not be treated as external product APIs or TMF921 resource APIs.

Example internal-only platform probes:

```http
GET /health
GET /ready
GET /metrics
```

These endpoints, if implemented, are restricted to the platform/runtime network plane and are not externally exposed.

---

## 2. Event input: IntentValidatedEvent

### Topic

```text
t7.intent.management.events
```

### Producer

```text
intent-controller-ms
```

### Consumer

```text
intent-intelligence-ms
```

### Meaning

`IntentValidatedEvent` means IC MS has admitted a runtime Intent after syntactic validation.

It does not mean semantic feasibility, policy acceptance, service availability, or downstream fulfilment success.

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

### Example body consumed by II MS

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
        "id": "hospital-surgical-slice-spec-v1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      }
    }
  }
}
```

### Input validation rules

II MS expects:

| Field | Rule |
|---|---|
| `body.intentId` | Required |
| `body.version` | Required where versioned runtime intent is used |
| `body.intentSpecification.id` | Required |
| `body.expression.context` | Required |
| `body.expression.context.constraints.location.locationId` | Required |
| `body.expression.context.constraints.serviceType` | Required |
| `body.expression.context.constraints.serviceClass` | Required |
| `body.expression.context.targets` | Required for downstream-capable intents |
| `body.expression.context.constraints` | Required when hard constraints exist |
| `body.expression.context.preferences` | Optional |
| `body.references.correlationId` | Required |

II MS does not expect the external TMF `Intent.expression` wrapper in internal events. Internal events carry native JSON under `body.expression`, but that native expression must preserve the canonical `context.targets`, `context.constraints`, and `context.preferences` grouping established by ID MS and IC MS.

---

## 3. Semantic processing flow

| Step | Action |
|---|---|
| 1 | Consume `IntentValidatedEvent` |
| 2 | Check idempotency using CloudEvents `ce-id` and intent identity |
| 3 | Parse admitted internal `expression.context` |
| 4 | Resolve `context.constraints.location` from KP |
| 5 | Resolve `context.constraints.serviceType` and `context.constraints.serviceClass` from KP |
| 6 | Validate service capability/status |
| 7 | Validate hard constraints, including priority, redundancy, and time window where present |
| 8 | Validate requested targets are supported for the service class |
| 9 | Preserve preferences for downstream selection guidance |
| 10 | Resolve valid resource set from KP after scope/policy filtering |
| 11 | Emit `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` through the II outbox, depending on the resolved milestone |

---

## 4. Target, constraint, and preference handling

### Targets

Targets are measurable runtime objectives.

Supported baseline target fields:

```text
maxLatencyMs
minAvailabilityPercent
maxJitterMs
maxPacketLossPercent
```

II MS validates that target names and value types are supported for the requested service/service class. II MS preserves target names and values under `expression.context.targets`.

### Constraints

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

### Preferences

Preferences are soft runtime selection guidance.

Supported baseline preference fields:

```text
preferredAccessTechnology
```

II MS preserves preferences for downstream selection guidance. II MS does not reject the intent only because a preference cannot be satisfied unless policy later promotes that preference into a hard constraint.

---

## 5. Rejection reason codes

II MS reason codes must be expressed as intent-domain semantic, policy, capability, or processing issues. II MS must not expose downstream implementation vocabulary or use downstream-selection-specific reason codes.

| Reason code | Meaning |
|---|---|
| `SEMANTIC_LOCATION_UNSUPPORTED` | Requested location cannot be resolved or is unsupported for this intent domain |
| `SEMANTIC_LOCATION_TYPE_UNSUPPORTED` | Requested location type is not supported |
| `SEMANTIC_SERVICE_CLASS_UNSUPPORTED` | Requested service class is not supported |
| `SEMANTIC_REQUIRED_CONTEXT_MISSING` | Required `expression.context` information is missing |
| `SEMANTIC_EXPRESSION_UNSUPPORTED` | The admitted expression cannot be interpreted into canonical domain terms |
| `SEMANTIC_INTENT_CONTRADICTORY` | Requested targets/constraints are contradictory in the intent domain |
| `POLICY_LOCATION_NOT_ALLOWED` | Policy rejects the requested location |
| `POLICY_SERVICE_CLASS_NOT_ALLOWED` | Policy rejects the requested service class |
| `POLICY_PRIORITY_NOT_ALLOWED` | Policy rejects the requested priority |
| `POLICY_TIME_WINDOW_NOT_ALLOWED` | Policy rejects the requested time window |
| `KNOWLEDGE_LOOKUP_ERROR` | KP lookup failed or returned insufficient trusted information |
| `PROCESSING_ERROR` | II MS failed due to an internal processing error |

Capability/resource shortfall must be expressed as an intent-domain semantic or policy issue, not as a downstream-selection-specific issue.

---

## 6. Event output: IntentRejectedEvent

### Topic

```text
t7.intent.management.events
```

### Producer

```text
intent-intelligence-ms
```

### Current primary consumer

```text
intent-controller-ms
```

### Meaning

II MS emits `IntentRejectedEvent` when the admitted intent is syntactically valid but cannot be semantically, policy, or capability resolved.

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

### Example body — service class unsupported

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-002",
    "version": "v1",
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

### Example body — redundancy capability unsupported

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-003",
    "version": "v1",
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

- Use `lifecycleStatus: Rejected`.
- Include `reasonCode` and `statusReason`.
- Include resolved or partially resolved semantic context under `expression.context`.
- Include `expression.context.constraints` when needed to explain the rejection, such as redundancy failure.
- Do not include downstream selection details.
- Do not include assurance details.
- Do not include raw KP payloads.
- Preserve the canonical `context.targets`, `context.constraints`, and `context.preferences` grouping when expression details are included.

---

## 7. Event output: IntentResolvedEvent

### Topic

```text
t7.intent.management.events
```

### Producer

```text
intent-intelligence-ms
```

### Current primary consumer

```text
optimiser-controller-ms
```

### Meaning

II MS emits `IntentResolvedEvent` when the admitted intent has been semantically resolved into a canonical handoff that can proceed to the next internal fulfilment stage.

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

### Example body — Sydney resolved

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
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
        "accessTechnology": "fibre",
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

### Example body — Melbourne resolved with open-ended time window

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-004",
    "version": "v1",
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
        "resourceId": "MEL-SEC-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "metrics": {
          "latencyMs": 11,
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
          "latencyMs": 10,
          "availabilityPercent": 99.994,
          "jitterMs": 1.6,
          "packetLossPercent": 0.006
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "MEL-PRI-01"
          }
        ]
      }
    ]
  }
}
```

### Event-specific rules

- Preserve resolved semantic context under `expression.context`.
- Preserve `targets`, `constraints`, and `preferences` as first-class semantic buckets under `expression.context`.
- Do not flatten `location`, `serviceType`, or `serviceClass` into top-level event fields.
- Do not include direct top-level `priority`, `preferredAccessTechnology`, or `redundancyRequired` outside the buckets.
- Do not include `provider` by default.
- Do not include downstream-selected resources; all resources in `IntentResolvedEvent.resources` are applicable/applyable resources known for downstream consideration by `optimiser-controller-ms`, not final selected output.
- Include generic `metrics` values for applicable resources using neutral metric names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.
- Do not encode metric origin or lifecycle context into wrappers or field names such as `metrics.benchmark`, `metrics.telemetry`, `latencyBenchmarkMs`, or `currentLatencyMs`.

---

## 8. Event output: IntentNetworkReadyEvent

### Topic

```text
t7.intent.management.events
```

### Producer

```text
intent-intelligence-ms
```

### Current primary consumer

```text
intent-assurance-ms
```

### Meaning

II MS emits `IntentNetworkReadyEvent` after semantic resolution and service-ready preparation have produced the concrete change-execution and observation configuration required by IA MS.

`IntentNetworkReadyEvent` does not mean network apply has succeeded. It means the service configuration/resource set has been prepared for change execution/apply and assurance observation.

### Example headers

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-network-ready-001
ce-time: 2026-04-18T12:04:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### Example body — network ready for change execution and assurance

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "InProgress",
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
    },
    "serviceConfiguration": {
      "orchestratorConfiguration": {
        "target": "t7-network-orchestrator",
        "profile": "surgical-critical-gold-apply",
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
        "profile": "surgical-critical-gold-observe",
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

- `IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.
- `IntentNetworkReadyEvent` is consumed by `intent-assurance-ms`.
- Consumer identity does not change producer ownership.
- IA MS consumes this event; IA MS must not produce it.
- `IntentNetworkReadyEvent` means service configuration is ready for change execution/apply, not that apply has succeeded.
- Carry the resolved runtime `body.context` with `targets`, `constraints`, and `preferences`; IA MS stores this as assurance context.
- Use `serviceConfiguration.orchestratorConfiguration` for apply/change-execution details.
- Use `serviceConfiguration.observerConfiguration` for assurance/monitoring details.
- `serviceConfiguration.orchestratorConfiguration.resources[]` carries only the optimiser-selected network-ready configuration/resources that must be applied by the change-execution layer; it includes resource details, topology, roles, and change-execution-relevant information, but not metric values.
- `serviceConfiguration.observerConfiguration.resources[]` carries the full assurance observation scope, including selected resources and any additional primary/secondary alternatives that IA must observe; it uses `metrics` as a list of metric names IA should observe, not a value object.
- Do not include `applyOutcome`.
- Do not use this event as a substitute for `IntentAssuranceEvent`; IA MS remains responsible for apply outcome interpretation and runtime assurance truth.

---

## 9. KP mapping rules

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

---

## 10. Idempotency and ordering

II MS must support at-least-once event delivery.

Rules:

- Deduplicate consumed `IntentValidatedEvent` by `ce-id` / event id.
- Store semantic decision state per `intentId` and runtime version.
- Avoid emitting duplicate `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` for the same input event or milestone.
- If a newer runtime intent version exists, stale events must not overwrite newer resolution state.

---

## 11. Persistence

Suggested tables:

| Table | Purpose |
|---|---|
| `intent_resolution_state` | Current semantic resolution state per intent/version |
| `intent_resolution_idempotency` | Consumed event deduplication |
| `intent_resolution_audit` | KP lookup, policy, semantic, and rejection decision trail |
| `intent_resolution_outbox` | Reliable publication of II-owned events, including `IntentRejectedEvent`, `IntentResolvedEvent`, and `IntentNetworkReadyEvent` |
| `intent_resolution_dead_letter` | Optional failed/unprocessable event handling |
| `shedlock` | Relay coordination if clustered outbox relay is used |

---

## 12. Dependency behaviour

| Dependency | Behaviour |
|---|---|
| II DB unavailable | Do not process/acknowledge event beyond retry/dead-letter policy |
| KP unavailable | Fail closed for semantic resolution and retry/dead-letter according to policy |
| Kafka unavailable | Use outbox relay retry; do not lose resolved/rejected outcome |
| Cache unavailable | Bypass cache and use KP/source where safe |
| Downstream fulfilment stage unavailable | Not an II MS dependency for emitting `IntentResolvedEvent`; service-ready preparation must complete before emitting `IntentNetworkReadyEvent` |

---

## 13. Observability

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
```

All logs and traces must include `correlationId` and `intentId` where available.

---

## 14. Security

II MS is internal only.

Rules:

- consume only from trusted internal event backbone
- use workload identity for KP access
- expose no public, NGW, OEX, partner, or consumer-facing REST API
- restrict any platform probes to the internal runtime/network plane
- no external user/business authorisation in II MS
- do not include secrets, tokens, credentials, or raw stack traces in event payloads
- audit semantic and policy rejections where required

---

## 15. Contract summary

II MS consumes `IntentValidatedEvent`, validates and resolves the admitted expression using Knowledge Plane/domain knowledge, preserves `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences`, and emits `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` depending on the resolved milestone.

`IntentRejectedEvent` is the semantic/policy/capability rejection handoff. IC MS consumes it and projects the external runtime `Intent` lifecycle accordingly.

`IntentResolvedEvent` is the candidate-level semantic-resolution handoff. It carries canonical service context and the full valid/applicable/applyable resource set for downstream consideration by `optimiser-controller-ms`. It includes generic metric values for applicable resources using neutral metric names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`. It is not the final service-ready/apply-ready handoff.

`IntentNetworkReadyEvent` is the service-ready preparation handoff to IA MS. It carries the optimiser-selected apply/change-execution configuration in `serviceConfiguration.orchestratorConfiguration` and the full assurance observation scope in `serviceConfiguration.observerConfiguration`, and it does not mean network apply has succeeded. It does not carry metric values in `serviceConfiguration.orchestratorConfiguration.resources[]`; `serviceConfiguration.observerConfiguration.resources[].metrics` names the metrics IA should observe.
