# Intent Intelligence MS Solution Brief

## Summary:

Intent Intelligence MS (II MS) is the internal semantic interpretation and resolution service for admitted runtime intents. It consumes syntactically admitted intent facts from Intent Controller MS (IC MS), interprets the admitted expression using governed Knowledge Plane data, validates semantic feasibility, policy, capability, and resource context, and emits the next internal milestone event.

II MS is not an external TMF-compliant API service. It does not expose runtime Intent REST APIs, design-time IntentSpecification APIs, customer-facing lifecycle projections, callback endpoints, orchestration execution, or assurance truth. Its responsibility is to convert a syntactically accepted runtime intent into one of the following internal outcomes:

- `IntentRejectedEvent` when the admitted intent cannot be semantically, policy, or capability resolved.
- `IntentResolvedEvent` when the admitted intent has been semantically resolved into a canonical intent context and a full, valid candidate resource set for downstream optimisation or fulfilment consideration.
- `IntentNetworkReadyEvent` when II MS has prepared the concrete service configuration needed for orchestration/apply, and assurance observation.

`IntentResolvedEvent` and `IntentNetworkReadyEvent` are intentionally different milestones. `IntentResolvedEvent` is the candidate-level semantic-resolution handoff. `IntentNetworkReadyEvent` is the service-ready preparation handoff to IA MS and means the service configuration/resource set has been prepared for orchestration/apply and assurance observation. It does not mean the network application has succeeded.

## Logical View:
![alt text](ii_ms_logical_view.svg)
II MS sits after IC MS in the runtime intent processing flow and before optimiser/orchestration/assurance execution stages.

```text
External Intent API
  -> IC MS syntactic admission and persistence
  -> IntentValidatedEvent
  -> II MS semantic interpretation and KP-backed resolution
  -> IntentRejectedEvent | IntentResolvedEvent | IntentNetworkReadyEvent
```

Logical responsibilities:

| Area | II MS responsibility |
|---|---|
| Runtime input | Consume `IntentValidatedEvent` from the internal event backbone. |
| Semantic interpretation | Interpret the admitted `expression.context` model. |
| Knowledge Plane validation | Resolve and validate location, service type, service class, targets, constraints, preferences, policy, and capability context. |
| Canonicalisation | Preserve and normalise canonical semantic buckets: `targets`, `constraints`, and `preferences`. |
| Candidate discovery | Resolve the full valid candidate resource set known for the resolved context after scope/policy filtering. |
| Rejection decision | Emit `IntentRejectedEvent` for semantic, policy, capability, or processing rejection. |
| Resolution handoff | Emit `IntentResolvedEvent` for candidate-level semantic resolution. |
| Service-ready handoff | Emit `IntentNetworkReadyEvent` when service configuration is prepared for orchestration and assurance observation. |
| Reliability | Use idempotent consumption and outbox-backed publication. |
| Audit | Persist the semantic decision trail where required. |

## Process View:
![alt text](ii_ms_sequence.svg)
1. II MS consumes `IntentValidatedEvent` from the internal Kafka event backbone.
2. It deduplicates the input event using CloudEvents identity and runtime intent identity.
3. It parses `body.expression.context.targets`, `body.expression.context.constraints`, and `body.expression.context.preferences`.
4. It resolves location, service type, service class, capability, policy, and resource context from the Knowledge Plane.
5. It validates hard constraints such as location, service class, priority, redundancy, and time window.
6. It validates measurable targets such as latency, availability, jitter, and packet loss against a known capability context.
7. It preserves preferences as soft selection guidance unless policy explicitly promotes a preference into a hard constraint.
8. It resolves the complete valid candidate resource set for the current semantic context after applicable scope and policy filtering.
9. It records the semantic decision and writes the output event to the II outbox.
10. The II outbox relay publishes the event to the internal event backbone.
11. Consumers continue the workflow according to the milestone event emitted.

## Solution Elaboration:

II MS exists because IC MS admission validation is intentionally syntactic and contract-focused. IC MS can confirm that an external runtime Intent request is structurally valid and references an active IntentSpecification, but it should not decide whether the requested outcome is semantically possible, policy-allowed, supported by the Knowledge Plane, or resolvable into a candidate resource set.

II MS performs that semantic decision step. It treats the admitted expression as an internal runtime intent fact model, not as a customer-facing API payload. The canonical semantic structure is preserved across the pipeline:

```text
expression.context.targets
expression.context.constraints
expression.context.preferences
```

`targets` are measurable runtime objectives such as maximum latency, minimum availability, maximum jitter, and maximum packet loss. `constraints` are hard requirements and required non-target inputs such as location, service type, service class, priority, redundancy requirement, and time window. `preferences` are soft selection guidance, such as preferred access technology.

II MS must not flatten these buckets into unrelated top-level fields. Keeping the same semantic buckets from ID MS to IC MS to II MS reduces mapping, prevents drift, and allows IA MS and later control-loop components to interpret assurance outcomes against the same intent context.

## Responsibilities:

II MS owns:

| Responsibility | Description |
|---|---|
| `IntentValidatedEvent` consumption | Consume admitted runtime intent events from IC MS. |
| Semantic interpretation | Interpret admitted intent expression context into canonical domain meaning. |
| KP-backed validation | Validate location, service type, service class, capability, policy, and resource availability. |
| Target validation | Validate supported measurable runtime objectives. |
| Constraint validation | Validate hard requirements such as location, priority, redundancy, and time window. |
| Preference preservation | Preserve soft selection guidance for downstream selection/optimisation. |
| Candidate resource resolution | Build the full, valid candidate resource set after applicable scope and policy filtering. |
| Semantic rejection | Emit `IntentRejectedEvent` with intent-domain reason codes. |
| Candidate-level resolution | Emit `IntentResolvedEvent` for downstream optimisation/fulfilment consideration. |
| Service-ready preparation | Emit `IntentNetworkReadyEvent` with prepared orchestration and observation configuration. |
| Idempotency | Deduplicate consumed events and avoid duplicate milestone outcomes. |
| Persistence | Store current semantic resolution state, decision audit, idempotency records, and outbox entries. |
| Event publication | Publish II-owned events reliably using the outbox relay pattern. |

## II MS does not:

| Concern | Owner |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| Runtime `Intent` REST API | IC MS |
| Runtime `IntentReport` REST API and projection | IC MS |
| External lifecycle/status projection | IC MS |
| External TMF subscription APIs | IC MS / ID MS depending on resource |
| External consumer authorisation | Gateway / OEX / domain-facing API layer before the internal event flow |
| Downstream optimisation algorithm ownership | Optimiser service |
| Network orchestration/apply execution | Orchestration layer / network orchestrator |
| Apply outcome truth | IA MS |
| Runtime assurance truth | IA MS |
| Callback ingestion | ICB MS |
| Raw callback interpretation and lifecycle mapping | IA MS |
| KP configuration CRUD/governance | Knowledge Plane operating model |
| Public, partner, OEX, or NGW-facing API exposure | Not applicable to II MS |

## Contracts:

II MS contracts are internal event contracts only.

| Contract | Direction | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `IntentValidatedEvent` | Inbound | `intent-controller-ms` | `intent-intelligence-ms` | Tells II MS that IC MS admitted a runtime Intent syntactically. |
| `IntentRejectedEvent` | Outbound | `intent-intelligence-ms` | `intent-controller-ms` | Tells IC MS that the admitted intent is semantically/policy/capability rejected. |
| `IntentResolvedEvent` | Outbound | `intent-intelligence-ms` | Optimiser / downstream fulfilment stage | Candidate-level semantic-resolution handoff. |
| `IntentNetworkReadyEvent` | Outbound | `intent-intelligence-ms` | `intent-assurance-ms` | Service-ready orchestration and observation configuration handoff. |

II MS has no external TMF-compliant REST contract in the active baseline. Any health, readiness, or metrics endpoints are internal platform probes only and must not be treated as product APIs.

II MS does not expose REST hub subscriptions and does not deliver external HTTP webhook notifications. All II-owned event contracts are internal Kafka event contracts only.

## Event delivery path:

II MS has one event-delivery model in the active baseline: internal Kafka event processing. It consumes `IntentValidatedEvent` from the internal intent-management event topic and publishes II-owned milestone events through the II internal outbox relay to Kafka. These events use CloudEvents-style Kafka/platform headers and JSON bodies. II MS does not use the external REST hub/webhook notification model because it has no external TMF-compliant API or subscriber callback contract.

## Inbound internal Kafka event shape: IntentValidatedEvent:

The inbound event is consumed from Kafka and uses CloudEvents-style Kafka/platform headers with a plain JSON body.

```http
ce-specversion: 1.0
ce-type: IntentValidatedEvent
ce-source: intent-controller-ms
ce-id: evt-intent-validated-001
ce-time: 2026-04-18T12:00:01+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

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

## Field specification:

| Field | Requirement | Notes |
|---|---|---|
| `body.intentId` | Required | Runtime Intent identity admitted by IC MS. |
| `body.version` | Required where runtime intent versioning is used | Used to prevent stale event decisions overriding newer versions. |
| `body.lifecycleStatus` | Required | Expected to reflect IC MS admission state, commonly `Acknowledged`. |
| `body.intentSpecification.id` | Required | Active specification used by IC MS admission validation. |
| `body.expression.context` | Required | Canonical runtime intent context. |
| `body.expression.context.targets` | Required for downstream-capable intents | Measurable outcome objectives. |
| `body.expression.context.constraints` | Required when hard requirements exist | Includes location, service type, service class, priority, redundancy, and time window where applicable. |
| `body.expression.context.constraints.location.locationId` | Required | Canonical location identifier or alias to be resolved by KP. |
| `body.expression.context.constraints.serviceType` | Required | Service domain requested by the runtime intent. |
| `body.expression.context.constraints.serviceClass` | Required | Service class such as `critical-gold`. |
| `body.expression.context.preferences` | Optional | Soft selection guidance. |
| `body.references.correlationId` | Required | Used for traceability across services and events. |
| `body.references.intent` | Required | Runtime Intent reference. |
| `body.references.intentSpecification` | Required | IntentSpecification reference. |

## Fields not accepted:

II MS should reject or ignore unexpected fields according to its schema and compatibility policy. The following fields are not part of the II MS baseline contract:

| Field or pattern | Reason |
|---|---|
| External TMF `Intent.expression.expressionValue` wrapper in II internal events | IC MS has already translated the external expression wrapper into internal JSON. |
| Top-level `location`, `serviceType`, `serviceClass`, `priority`, `redundancyRequired`, or `preferredAccessTechnology` outside `expression.context` | These belong under the canonical semantic buckets. |
| `provider` in resource entries by default | Provider is KP/resource-inventory metadata and is not event-facing unless explicitly needed. |
| Downstream-selected final resources in `IntentResolvedEvent` | `IntentResolvedEvent.resources` is the full valid candidate set, not final selection. |
| Apply outcome fields in `IntentNetworkReadyEvent` | Apply outcome is interpreted later by IA MS. |
| Assurance status or observed metric truth in II output events | Runtime assurance truth belongs to IA MS. |
| Raw KP payload dumps | II MS curates KP data into event-facing fields only. |
| Secrets, tokens, credentials, raw stack traces | Must never be emitted in event payloads. |

## Authorisation:

II MS is internal only. It is not exposed through NGW, OEX, public API gateways, partner channels, or external TMF APIs.

Security and authorisation rules:

- Consume only from trusted internal Kafka topics and trusted platform identities.
- Use workload identity for Knowledge Plane access.
- Use service-to-service identity and platform network policy for internal calls.
- Do not perform external end-user authorisation in II MS.
- Do not rely on downstream user context; II MS receives internal event facts, not external user claims.
- Restrict health, readiness, and metrics probes to the platform/runtime network plane.
- Audit semantic and policy rejections where required.
- Do not emit secrets, credentials, or sensitive internal implementation details in events.

## Persistence / state / outbox model:

II MS should use source-of-truth persistence for semantic resolution state and reliable event publication. A PostgreSQL-compatible relational store is suitable because II MS needs transactional state transitions, idempotency, auditability, and reliable outbox behaviour.

Suggested tables:

| Table | Purpose |
|---|---|
| `intent_resolution_state` | Current semantic resolution state per `intentId` and runtime version. |
| `intent_resolution_idempotency` | Consumed event deduplication keyed by CloudEvents id and/or intent/version identity. |
| `intent_resolution_audit` | Decision audit for KP lookup, policy validation, semantic rejection, and resolution outcomes. |
| `intent_resolution_outbox` | Reliable publication queue for `IntentRejectedEvent`, `IntentResolvedEvent`, and `IntentNetworkReadyEvent`. |
| `intent_resolution_dead_letter` | Optional failed/unprocessable event tracking. |
| `shedlock` | Optional clustered outbox relay coordination. |

The processing transaction should persist the semantic decision and enqueue the output event atomically. The relay publishes from the outbox and records publication state separately from decision ownership.

## Internal Kafka publication:

II MS publishes internal platform events through the internal outbox relay to Kafka. Event delivery is at-least-once. Consumers must be idempotent.

Publication rules:

- Publish only after the semantic decision is durably recorded.
- Use a stable event id for deduplication.
- Include `correlationId` and `intentId` in the body for traceability.
- Preserve CloudEvents headers consistently across event types.
- Do not publish partially constructed milestone events.
- Retry transient Kafka publication failures through the outbox relay.
- Treat exhausted publication retries as an operational failure requiring support handling.

## Internal Kafka topics:

| Topic | Event types | Direction for II MS |
|---|---|---|
| `t7.intent.management.events` | `IntentValidatedEvent`, `IntentRejectedEvent`, `IntentResolvedEvent`, `IntentNetworkReadyEvent` | Consume and publish internal intent workflow events. |

A future split into more granular topics can be introduced if throughput, retention, or ownership boundaries require it, but the baseline uses the shared internal intent-management events topic.

## Event identity:

CloudEvents identity must be stable and suitable for deduplication.

| Field | Rule |
|---|---|
| `ce-id` | Globally unique event id. Stable for the same event publication attempt. |
| `ce-source` | `intent-intelligence-ms` for II-owned outbound events. |
| `ce-type` | One of `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent`. |
| `ce-subject` | Runtime `intentId`. |
| `ce-time` | Event creation time. |
| `body.intentId` | Same runtime intent identity as `ce-subject`. |
| `body.version` | Runtime intent version when versioning is used. |
| `body.references.correlationId` | End-to-end trace/correlation id. |

## Internal Kafka CloudEvents headers:

Example outbound headers for `IntentResolvedEvent`:

```http
ce-specversion: 1.0
ce-type: IntentResolvedEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-resolved-001
ce-time: 2026-04-18T12:03:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

Example outbound headers for `IntentNetworkReadyEvent`:

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-network-ready-001
ce-time: 2026-04-18T12:04:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

## Internal Kafka message body: IntentRejectedEvent:

`IntentRejectedEvent` is emitted when semantic, policy, capability, or processing validation fails after IC MS syntactic admission.

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

Baseline reason-code families:

| Reason code | Meaning |
|---|---|
| `SEMANTIC_LOCATION_UNSUPPORTED` | Requested location cannot be resolved or is unsupported for this intent domain. |
| `SEMANTIC_LOCATION_TYPE_UNSUPPORTED` | Requested location type is not supported. |
| `SEMANTIC_SERVICE_CLASS_UNSUPPORTED` | Requested service class is not supported. |
| `SEMANTIC_REQUIRED_CONTEXT_MISSING` | Required `expression.context` information is missing. |
| `SEMANTIC_EXPRESSION_UNSUPPORTED` | The admitted expression cannot be interpreted into canonical domain terms. |
| `SEMANTIC_INTENT_CONTRADICTORY` | Requested targets/constraints are contradictory in the intent domain. |
| `POLICY_LOCATION_NOT_ALLOWED` | Policy rejects the requested location. |
| `POLICY_SERVICE_CLASS_NOT_ALLOWED` | Policy rejects the requested service class. |
| `POLICY_PRIORITY_NOT_ALLOWED` | Policy rejects the requested priority. |
| `POLICY_TIME_WINDOW_NOT_ALLOWED` | Policy rejects the requested time window. |
| `KNOWLEDGE_LOOKUP_ERROR` | KP lookup failed or returned insufficient trusted information. |
| `PROCESSING_ERROR` | II MS failed due to an internal processing error. |

## Internal Kafka message body: IntentResolvedEvent:

`IntentResolvedEvent` is the candidate-level semantic-resolution handoff. It carries canonical context and all valid/applicable candidate resources known for the resolved context after scope and policy filtering. It is not the final selected/applied resource set.

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
    "resources": [
      {
        "resourceId": "SYD-PRI-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": ["primary"],
        "resourceAttributes": {
          "accessTechnology": "fibre"
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "SYD-SEC-01"
          }
        ],
        "metrics": {
          "latencyMs": 7,
          "availabilityPercent": 99.996,
          "jitterMs": 1.1,
          "packetLossPercent": 0.004
        }
      },
      {
        "resourceId": "SYD-SEC-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": ["secondary"],
        "resourceAttributes": {
          "accessTechnology": "5G"
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "SYD-PRI-01"
          }
        ],
        "metrics": {
          "latencyMs": 10,
          "availabilityPercent": 99.994,
          "jitterMs": 1.8,
          "packetLossPercent": 0.006
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
      },
      "knowledgePlane": {
        "configId": "hospital-surgical-slice-kp-v1",
        "version": "1.0"
      }
    }
  }
}
```

Rules:

- Preserve `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences`.
- Do not flatten location, service type, service class, priority, redundancy, or preference fields into unrelated top-level event fields.
- `resources[]` is the full valid candidate set for the resolved context, not the final selected/applied resource set.
- Resource metrics use neutral metric names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.
- Do not use context-encoded metric wrappers such as `metrics.benchmark` or `metrics.telemetry` in the baseline message shape.
- Do not include `provider` by default.

## Internal Kafka message body: IntentNetworkReadyEvent:

`IntentNetworkReadyEvent` is the service-ready preparation handoff to IA MS. It carries the service configuration required for orchestration/apply and assurance observation. It does not mean network apply succeeded.

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
            "roles": ["primary"]
          },
          {
            "resourceId": "SYD-SEC-01",
            "resourceType": "deliveryResource",
            "resourceClass": "critical-gold",
            "roles": ["secondary"]
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
            "roles": ["primary"],
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
            "roles": ["secondary"],
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

Rules:

- `IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.
- IA MS consumes `IntentNetworkReadyEvent`; IA MS must not produce it.
- Use `serviceConfiguration.orchestratorConfiguration` for apply/orchestration details.
- Use `serviceConfiguration.observerConfiguration` for assurance/monitoring details.
- `serviceConfiguration.resources[]` carries network-ready resource details, topology, roles, and orchestrator/observer-relevant information.
- `serviceConfiguration.resources[]` must not carry observed metric values.
- In `observerConfiguration.resources[]`, `metrics` is a list of metric names IA MS should observe, not a value object.
- Do not include `applyOutcome`.
- Do not treat this event as proof that network apply succeeded.

## Behaviour:

### Successful semantic resolution:

When an admitted intent can be semantically interpreted and candidate resources are known, II MS emits `IntentResolvedEvent`.

### Semantic rejection:

When an admitted intent is syntactically valid but cannot be semantically, policy, or capability resolved, II MS emits `IntentRejectedEvent`. Rejection reason codes must be intent-domain reason codes and must not leak downstream implementation vocabulary.

### Service-ready preparation:

When the service configuration required for orchestration/apply and assurance observation is prepared, II MS emits `IntentNetworkReadyEvent`. This event carries `serviceConfiguration.orchestratorConfiguration` and `serviceConfiguration.observerConfiguration`.

### Idempotency:

II MS must support at-least-once delivery. It deduplicates consumed events by CloudEvents id and runtime intent identity, and avoids duplicate output milestone events for the same input event and semantic decision.

### Ordering:

II MS must not allow stale events for older runtime intent versions to overwrite newer semantic resolution state. Where runtime versioning is active, state transitions are keyed by `intentId` and version.

### Dependency failure:

| Dependency | Behaviour |
|---|---|
| II database unavailable | Do not acknowledge/process beyond retry/dead-letter policy. |
| Knowledge Plane unavailable | Fail closed for semantic resolution and retry/dead-letter according to policy. |
| Kafka unavailable | Persist to outbox and retry through relay. |
| Cache unavailable | Bypass cache and use KP/source where safe. |
| Optimiser unavailable | Not a dependency for semantic resolution; downstream consumption handles its own availability. |
| IA MS unavailable | Not a synchronous dependency; `IntentNetworkReadyEvent` remains the handoff. |

## Configuration:

II MS configuration should be environment-specific and externally supplied through platform configuration mechanisms.

Suggested configuration areas:

| Configuration area | Examples |
|---|---|
| Kafka topics | Internal intent-management event topic names and consumer group id. |
| Outbox relay | Batch size, retry backoff, maximum retry count, relay lock settings. |
| KP access | KP endpoint, timeout, cache TTL, circuit-breaker settings. |
| Semantic rules | Supported service types, service classes, target names, constraint names, and policy rule versions. |
| Rejection mapping | Reason-code mapping and user/projectable `statusReason` templates. |
| Observability | Log levels, metrics enablement, trace sampling. |
| Dead-letter handling | DLQ topic/table settings and operational alert thresholds. |

Configuration must not introduce per-environment contract drift. Contract field names and event meaning remain stable across environments.

## Consumer contract:

Consumers of II-owned events must treat the event stream as at-least-once.

Consumer rules:

- Deduplicate by `ce-id` and/or `body.intentId` plus version and milestone type.
- Treat `IntentResolvedEvent.resources[]` as the full valid candidate set, not final selected/applied output.
- Treat `IntentNetworkReadyEvent` as service-ready preparation only, not apply success.
- Do not infer assurance status from II events.
- Use `body.references.correlationId` for traceability.
- Preserve the canonical `targets`, `constraints`, and `preferences` grouping when forwarding or deriving downstream state.

## Open items:

| Item | Status |
|---|---|
| Finalise whether optimiser consumes `IntentResolvedEvent` directly or via an optimiser-specific inbox abstraction in implementation. | Open implementation detail. |
| Finalise exact KP lookup and cache policy values per environment. | Open implementation detail. |
| Finalise DLQ operational runbook and replay controls. | Open implementation detail. |
| Confirm whether future topic split is needed for `IntentResolvedEvent` and `IntentNetworkReadyEvent` as volume grows. | Open scalability decision. |

## Closed items:

| Item | Decision |
|---|---|
| II MS is internal only. | Closed. No external TMF-compliant API. |
| II MS consumes `IntentValidatedEvent`. | Closed. |
| II MS emits `IntentRejectedEvent`. | Closed. |
| II MS emits `IntentResolvedEvent`. | Closed. |
| II MS owns and emits `IntentNetworkReadyEvent`. | Closed. |
| IA MS consumes but does not produce `IntentNetworkReadyEvent`. | Closed. |
| `IntentResolvedEvent` resources are candidates, not selected/applied resources. | Closed. |
| `IntentNetworkReadyEvent` does not mean apply success. | Closed. |
| Canonical buckets are `targets`, `constraints`, and `preferences`. | Closed. |
| `availabilityPercent` is the standard availability metric name. | Closed. |

## MS identity:

| Attribute | Value |
|---|---|
| Full name | Intent Intelligence MS |
| Short name | II MS |
| Service name | `intent-intelligence-ms` |
| Domain | Intent Domain |
| External API | None |
| Primary input event | `IntentValidatedEvent` |
| Output events | `IntentRejectedEvent`, `IntentResolvedEvent`, `IntentNetworkReadyEvent` |
| Primary persistence | PostgreSQL / PostgreSQL-compatible RDBMS |
| Event style | Internal Kafka events with CloudEvents-style Kafka/platform headers and plain JSON `body` |
| Public exposure | None |
