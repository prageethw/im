# II MS Specification

## Service identity

| Item | Baseline |
|---|---|
| Full name | Intent Intelligence MS |
| Short name | II MS |
| Service name | `intent-intelligence-ms` |
| Domain | Intent Domain |
| Primary responsibility | Semantic interpretation, KP-backed validation, and optimisation-ready resolution |
| External API | None by default |
| Primary input event | `IntentValidatedEvent` |
| Output events | `IntentRejectedEvent`, `IntentResolvedEvent` |

## Boundary statement

II MS consumes syntactically admitted runtime intent facts from IC MS and performs semantic interpretation and Knowledge Plane-backed resolution.

II MS emits either:

- `IntentRejectedEvent` when the intent cannot be semantically, policy, or capability resolved
- `IntentResolvedEvent` when the intent can proceed to optimisation

II MS does not own runtime `Intent` REST APIs, external lifecycle projection, optimisation decisions, assurance truth, callback ingestion, orchestration execution, or KP governance.

---

## 1. External API

II MS has no external TMF-facing API in the active baseline.

Platform/internal endpoints only:

```http
GET /health
GET /ready
GET /metrics
```

No consumer-facing REST contract is baselined for II MS.

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

It does not mean semantic feasibility, policy acceptance, service availability, or optimisation success.

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
      "location": {
        "locationId": "AU-NSW-SYD-HOSP-001",
        "locationType": "hospital",
        "geographicScope": "campus"
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
| `body.expression.location.locationId` | Required |
| `body.expression.serviceType` | Required |
| `body.expression.serviceClass` | Required |
| `body.expression.targets` | Required for optimisation-capable intents |
| `body.expression.constraints` | Required when hard constraints exist |
| `body.expression.preferences` | Optional |
| `body.references.correlationId` | Required |

II MS does not expect the external TMF `Intent.expression` wrapper in internal events. Internal events carry native JSON directly.

---

## 3. Semantic processing flow

| Step | Action |
|---|---|
| 1 | Consume `IntentValidatedEvent` |
| 2 | Check idempotency using CloudEvents `ce-id` and intent identity |
| 3 | Parse admitted internal expression |
| 4 | Resolve location from KP |
| 5 | Resolve service type and service class from KP |
| 6 | Validate service capability/status |
| 7 | Validate hard constraints, including priority, redundancy, and time window where present |
| 8 | Validate requested targets are supported for the service class |
| 9 | Preserve preferences for optimiser guidance |
| 10 | Resolve valid resource set from KP after scope/policy filtering |
| 11 | Emit `IntentRejectedEvent` or `IntentResolvedEvent` through II outbox |

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

II MS validates that target names and value types are supported for the requested service/service class.

II MS preserves target names and values in `IntentResolvedEvent.targets`.

### Constraints

Constraints are hard runtime requirements.

Supported baseline constraint fields:

```text
priority
redundancyRequired
timeWindow
```

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

II MS preserves preferences for optimiser use. II MS does not reject the intent only because a preference cannot be satisfied unless policy later promotes that preference into a hard constraint.

---

## 5. Rejection reason codes

| Reason code | Meaning |
|---|---|
| `LOCATION_NOT_FOUND` | Requested location cannot be resolved in KP |
| `SERVICE_NOT_AVAILABLE` | Requested service/service class is not available at the location |
| `UNSUPPORTED_SERVICE_CLASS` | Service class is not supported |
| `TARGET_NOT_SUPPORTED` | Requested target is not supported for this service |
| `CONSTRAINT_NOT_SATISFIABLE` | Hard constraint cannot be satisfied from KP/domain rules |
| `REDUNDANCY_NOT_AVAILABLE` | `redundancyRequired = true`, but KP does not show redundant capability |
| `POLICY_NOT_ALLOWED` | Policy rejects the request |
| `SEMANTIC_INTERPRETATION_FAILED` | II cannot interpret the admitted expression into canonical terms |

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

### Example body — service unavailable

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

### Example body — redundancy unavailable

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-003",
    "version": "v1",
    "lifecycleStatus": "Rejected",
    "reasonCode": "REDUNDANCY_NOT_AVAILABLE",
    "statusReason": "Redundancy was required by the intent, but redundant capability is not available for the resolved location and service class.",
    "location": {
      "locationId": "AU-QLD-BNE-HOSP-201",
      "displayName": "Brisbane-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true
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
- Include direct `location`, `serviceType`, and `serviceClass` when resolved or partially resolved.
- Include `constraints` only when needed to explain the rejection, such as redundancy failure.
- Do not include optimiser details.
- Do not include assurance details.
- Do not include raw KP payloads.
- Do not use a generic `context` wrapper.

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
intent-optimiser-ms
```

### Meaning

II MS emits `IntentResolvedEvent` when the admitted intent has been semantically resolved into a canonical handoff that can be optimised.

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
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00",
        "endDateTime": "2026-04-18T14:00:00+10:00"
      }
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

### Example body — Melbourne resolved with open-ended time window

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-004",
    "version": "v1",
    "lifecycleStatus": "InProgress",
    "location": {
      "locationId": "AU-VIC-MEL-HOSP-101",
      "displayName": "Melbourne-Main-Hospital"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 12,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      }
    },
    "preferences": {
      "preferredAccessTechnology": "fibre"
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "roles": [
          "primary"
        ],
        "accessTechnology": "fibre",
        "metrics": {
          "benchmark": {
            "latencyMs": 9,
            "availabilityPercent": 99.995,
            "jitterMs": 1.4,
            "packetLossPercent": 0.005
          }
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "MEL-SEC-01"
          }
        ]
      },
      {
        "resourceId": "MEL-PRI-02",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "roles": [
          "primary"
        ],
        "accessTechnology": "5G",
        "metrics": {
          "benchmark": {
            "latencyMs": 10,
            "availabilityPercent": 99.994,
            "jitterMs": 1.6,
            "packetLossPercent": 0.006
          }
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "metrics": {
          "benchmark": {
            "latencyMs": 12,
            "availabilityPercent": 99.993,
            "jitterMs": 1.9,
            "packetLossPercent": 0.007
          }
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "fibre",
        "metrics": {
          "benchmark": {
            "latencyMs": 11,
            "availabilityPercent": 99.996,
            "jitterMs": 1.3,
            "packetLossPercent": 0.004
          }
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

### Event-specific rules

- Use direct `location`, `serviceType`, and `serviceClass` fields.
- Preserve `targets`, `constraints`, and `preferences` as first-class semantic buckets.
- Do not include a generic `context` wrapper.
- Do not include direct top-level `priority`, `preferredAccessTechnology`, or `redundancyRequired` outside the buckets.
- Do not include `provider` by default.
- Do not include optimiser-selected resources; all resources in `IntentResolvedEvent.resources` are optimiser candidates, not optimiser output.
- For initial optimisation handoff, use `metrics.benchmark`.
- For future re-optimisation handoff based on live degradation, use `metrics.telemetry` and omit `metrics.benchmark` by default unless explicitly needed.

---

## 8. KP mapping rules

II MS maps KP data into event-facing resource entries.

| KP field | Event-facing treatment |
|---|---|
| `resourceId` | Include as `resourceId` |
| `resourceType` | Include as `resourceType` |
| `resourceClass` | Include as `resourceClass` |
| `resourceRoles` | Map to `roles` |
| `accessTechnology` | Include if useful to optimiser/preference handling |
| `metrics.benchmark` | Include under `metrics.benchmark` for first-pass optimisation |
| `relationships` | Include only optimiser-relevant relationships |
| `provider` | Do not include by default; KP inventory metadata only |

---

## 9. Idempotency and ordering

II MS must support at-least-once event delivery.

Rules:

- Deduplicate consumed `IntentValidatedEvent` by `ce-id` / event id.
- Store semantic decision state per `intentId` and runtime version.
- Avoid emitting duplicate `IntentRejectedEvent` or `IntentResolvedEvent` for the same input event.
- If a newer runtime intent version exists, stale events must not overwrite newer resolution state.

---

## 10. Persistence

Suggested tables:

| Table | Purpose |
|---|---|
| `intent_resolution_state` | Current semantic resolution state per intent/version |
| `intent_resolution_idempotency` | Consumed event deduplication |
| `intent_resolution_audit` | KP lookup, policy, semantic, and rejection decision trail |
| `intent_resolution_outbox` | Reliable publication of II-owned events |
| `intent_resolution_dead_letter` | Optional failed/unprocessable event handling |
| `shedlock` | Relay coordination if clustered outbox relay is used |

---

## 11. Dependency behaviour

| Dependency | Behaviour |
|---|---|
| II DB unavailable | Do not process/acknowledge event beyond retry/dead-letter policy |
| KP unavailable | Fail closed for semantic resolution and retry/dead-letter according to policy |
| Kafka unavailable | Use outbox relay retry; do not lose resolved/rejected outcome |
| Cache unavailable | Bypass cache and use KP/source where safe |
| Optimiser unavailable | Not an II MS dependency for emitting `IntentResolvedEvent` |

---

## 12. Observability

Recommended logs and metrics:

```text
ii_ms_intent_validated_consumed_count
ii_ms_intent_resolved_count
ii_ms_intent_rejected_count
ii_ms_kp_lookup_error_count
ii_ms_resolution_failure_count
ii_ms_outbox_pending_count
ii_ms_outbox_publish_failure_count
ii_ms_duplicate_event_count
```

All logs and traces must include `correlationId` and `intentId` where available.

---

## 13. Security

II MS is internal only.

Rules:

- consume only from trusted internal event backbone
- use workload identity for KP access
- no external user/business authorisation in II MS
- do not include secrets, tokens, credentials, or raw stack traces in event payloads
- audit semantic and policy rejections where required

---

## 14. Contract summary

II MS consumes `IntentValidatedEvent`, validates and resolves the admitted expression using Knowledge Plane/domain knowledge, preserves `targets`, `constraints`, and `preferences`, and emits either `IntentRejectedEvent` or `IntentResolvedEvent`.

The `IntentResolvedEvent` is the optimiser handoff. It carries canonical service context and the full valid resource set for optimiser consideration.

The `IntentRejectedEvent` is the semantic/policy/capability rejection handoff. IC MS consumes it and projects the external runtime `Intent` lifecycle accordingly.
