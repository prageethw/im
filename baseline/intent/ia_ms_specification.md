# IA MS Specification

## 1. Service identity

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Assurance MS |
| Short name | IA MS |
| Service name | `intent-assurance-ms` |
| Domain | Intent Domain |
| External API owner | No external TMF-facing API |
| Main responsibility | Runtime assurance truth, callback state normalisation, observation evaluation, and `IntentAssuranceEvent` publication |
| Main output event | `IntentAssuranceEvent` |
| Retired event | `IntentDriftOccurredEvent` is not used |

---

## 2. Boundary statement

IA MS owns runtime assurance truth after optimisation, network-ready configuration, apply callback, and observation metrics are available.

IA MS consumes internal events, uses `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` to identify the observability target/profile/resource scope, obtains metrics from observation endpoints, updates IA-owned assurance state, and publishes curated `IntentAssuranceEvent` outcomes to the main internal event topic.

IC MS consumes `IntentAssuranceEvent` and projects the external TMF-facing `Intent.lifecycleStatus` and `IntentReport.expression.expressionValue`.

IA MS does not own external TMF APIs, runtime `Intent` resources, design-time `IntentSpecification`, semantic interpretation, optimisation decisions, callback ingestion, or network orchestration/apply execution.
IA MS consumes optimisation, network-ready, callback, and observation/telemetry facts only.


---

## 3. Internal event style

IA MS uses the active internal event style:

| **Concern** | **Baseline** |
|---|---|
| Transport metadata | CloudEvents-style metadata in Kafka/message headers |
| Payload | Plain JSON body with top-level `body` |
| TMF wrapper | Not used internally |
| Delivery | At-least-once |
| Idempotency | Required for consumed events |
| Deduplication key | `ce-id` / event id |
| Correlation | `correlationId` propagated end-to-end |
| Kafka key | Prefer `intentId` for intent-scoped events |

Internal IA events must not use external TMF `IntentExpression` wrappers. Those wrappers are used only in external IC MS REST resources and external TMF-style events.

Internal events may still use a plain internal `context` object when carrying resolved targets, constraints, and preferences. This is an internal event convention, not the external TMF `Intent.expression` wrapper.

---

## 4. Input event contracts

### 4.1 IntentOptimisedEvent input

IA MS consumes `IntentOptimisedEvent` to understand the optimiser-selected resources, resolved targets, resolved constraints, preferences, and optimisation outcome.

For the active baseline, `IntentOptimisedEvent.body.context` follows the same logical grouping used end-to-end:

- `context.targets`
- `context.constraints`
- `context.preferences`

This keeps optimisation, assurance, and runtime reporting aligned with the ID/IC targets-constraints-preferences baseline while still using an internal plain JSON event body.

#### Example headers

```http
ce-specversion: 1.0
ce-type: IntentOptimisedEvent
ce-source: intent-optimiser-ms
ce-id: evt-intent-optimised-001
ce-time: 2026-04-18T12:05:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

#### Example body — completed optimisation

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
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
    },
    "resources": [
      {
        "resourceId": "SYD-PRI-01",
        "roles": ["primary"],
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "accessTechnology": "fibre",
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
        "roles": ["secondary"],
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "accessTechnology": "5G",
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
    "evaluations": {
      "targets": [
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
      "constraints": [
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
      "preferences": [
        {
          "name": "preferredAccessTechnology",
          "status": "COMPLETED",
          "statusReason": "Selected secondary resource uses preferred access technology."
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
      }
    }
  }
}
```

#### IA handling rules

- Store the selected resource set and resolved target baseline in IA state.
- Store `body.context.targets`, `body.context.constraints`, and `body.context.preferences` as the resolved optimisation context.
- Use resolved runtime targets and the IA stored applied assurance baseline for assurance evaluation.
- KP/rules may support mapping and evaluation policy, but IA must not query KP as the source of truth for every assurance decision by default.
- Do not expose optimiser scoring or solver internals.
- Do not add `provider` to IA state events or `IntentAssuranceEvent` outputs.
- If optimisation status is `INFEASIBLE` or `FAILED`, IA may publish a lifecycle-driving `IntentAssuranceEvent` with `lifecycleStatus: Failed` only when IA is the service responsible for projecting that outcome in the specific workflow. Otherwise, the optimiser failure remains an optimiser outcome consumed by the appropriate workflow owner.

---

### 4.2 IntentNetworkReadyEvent input

IA MS consumes `IntentNetworkReadyEvent` to learn the apply plan and the observer scope.

`IntentNetworkReadyEvent` is consumed by IA MS. It is not emitted by IA MS. In the active baseline the source is II MS unless a later workflow assigns this event to a different publisher.

#### Example headers

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-network-ready-001
ce-time: 2026-04-18T12:12:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

#### Example body

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

#### IA handling rules

- Treat `IntentNetworkReadyEvent` as service configuration prepared for apply, not as apply success.
- Store selected apply resources from `orchestratorConfiguration.resources`.
- Store monitored resource scope from `observerConfiguration.resourceIds`.
- Do not emit `Active` solely because `IntentNetworkReadyEvent` was consumed.
- Active state requires apply/callback confirmation and/or runtime observations according to the workflow.

---

### 4.3 IntentCallbackEvent input

IA MS consumes raw callback relay events emitted by ICB MS.

The canonical callback fields are:

- `orchestratorState`
- `orchestratorSource`
- `orchestratorTimestamp`

Do not use older callback field names such as `callbackSource`, `callbackTimestamp`, or `sourceState.state`.

#### Example headers

```http
ce-specversion: 1.0
ce-type: au.com.mycsp.intent.callback.v1
ce-source: intent-callback-ms
ce-id: evt-intent-callback-001
ce-time: 2026-04-18T12:15:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

#### Example body — apply success callback

```json
{
  "body": {
    "eventType": "IntentCallbackEvent",
    "eventVersion": "1.0",
    "source": "intent-callback-ms",
    "eventTime": "2026-04-18T12:15:00+10:00",
    "correlationId": "corr-intent-callback-001",
    "intentId": "INT-HOSP-2026-001",
    "orchestratorState": "APPLIED",
    "orchestratorSource": "t7-network-orchestrator",
    "orchestratorTimestamp": "2026-04-18T12:14:58+10:00"
  }
}
```

#### Example body — apply failure callback

```json
{
  "body": {
    "eventType": "IntentCallbackEvent",
    "eventVersion": "1.0",
    "source": "intent-callback-ms",
    "eventTime": "2026-04-18T12:18:00+10:00",
    "correlationId": "corr-intent-callback-002",
    "intentId": "INT-HOSP-2026-003",
    "orchestratorState": "APPLY_FAILED",
    "orchestratorSource": "t7-network-orchestrator",
    "orchestratorTimestamp": "2026-04-18T12:17:55+10:00"
  }
}
```

#### IA handling rules

- Validate/correlate `intentId` against IA state and platform context.
- If `intentId` is unknown or not correlatable, record dead-letter/operational outcome according to IA policy.
- Derive orchestrator type from IA/platform context, not from ICB MS.
- Map raw `orchestratorState` into IA lifecycle/assurance meaning.
- Do not expose raw callback payloads in `IntentAssuranceEvent`.
- ICB MS remains the owner of callback ingestion and callback outbox persistence.

---

### 4.4 Metrics collection through observation endpoints

IA MS does not consume a separately named observation snapshot event in the active baseline. IA MS obtains runtime metrics from observability/observation endpoints that are selected or informed by the `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration` block.

`IntentNetworkReadyEvent` provides the observer scope, for example:

```json
{
  "serviceConfiguration": {
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
  }
}
```

IA MS uses this observer configuration to query or subscribe to platform observation endpoints for current metrics for the listed resources.

The exact observation endpoint API is owned by the observability platform and is not baselined in this IA MS specification.

#### Logical metrics returned to IA MS

```json
{
  "observedAt": "2026-04-18T12:29:55+10:00",
  "resourceMetrics": [
    {
      "resourceId": "SYD-PRI-01",
      "role": "primary",
      "metrics": {
        "latencyMs": 18,
        "availabilityPercent": 99.992,
        "jitterMs": 1.8,
        "packetLossPercent": 0.006
      }
    },
    {
      "resourceId": "SYD-SEC-01",
      "role": "secondary",
      "metrics": {
        "latencyMs": 12,
        "availabilityPercent": 99.994,
        "jitterMs": 1.8,
        "packetLossPercent": 0.006
      }
    }
  ]
}
```

#### IA handling rules

- Use `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.target` and `.profile` to identify the observation capability/profile to use.
- Use `observerConfiguration.resourceIds` as the monitoring scope for runtime assurance.
- Query or subscribe to observability platform endpoints according to platform integration design.
- Use returned metric facts to evaluate current runtime behaviour against resolved runtime targets and the IA stored applied assurance baseline.
- Do not publish raw telemetry dumps.
- Curate `observations` in `IntentAssuranceEvent` to what IC MS needs for external lifecycle/report projection.
- Healthy/active assurance events should normally include selected/applied resources only.
- Degraded/failed/recovery-supporting assurance events may include all monitored resources in observer scope.

---

## 5. Callback state mapping

| **Raw `orchestratorState`** | **IA treatment** | **Typical `IntentAssuranceEvent.lifecycleStatus`** |
|---|---|---|
| `APPLY_ACCEPTED` | Apply request accepted by orchestration layer | `InProgress` |
| `APPLY_IN_PROGRESS` | Apply still underway | `InProgress` |
| `APPLIED` | Apply completed; runtime observations may further confirm health | `Active` |
| `APPLY_REJECTED` | Apply request rejected before successful application | `Failed` |
| `APPLY_FAILED` | Apply failed after attempt | `Failed` |
| `TERMINATION_ACCEPTED` | Termination accepted | `InProgress` |
| `TERMINATED` | Termination confirmed | `Terminated` |
| Unknown/unmapped | Record skip/dead-letter/operational handling decision | No default lifecycle event unless policy requires one |

This mapping is intentionally IA-owned. ICB MS must not map source states into lifecycle states.

---

## 6. Output event contract — IntentAssuranceEvent

### 6.1 Common headers

```http
ce-specversion: 1.0
ce-type: IntentAssuranceEvent
ce-source: intent-assurance-ms
ce-id: evt-intent-assurance-001
ce-time: 2026-04-18T12:20:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 6.2 Active outcome

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Active",
    "statusReason": "Selected resources are operating within resolved runtime targets.",
    "context": {
      "constraints": {
        "location": {
          "locationId": "AU-NSW-SYD-HOSP-001",
          "displayName": "Sydney-Main-Hospital"
        },
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold"
      },
      "targets": {
        "maxLatencyMs": 10,
        "minAvailabilityPercent": 99.99,
        "maxJitterMs": 2,
        "maxPacketLossPercent": 0.01
      }
    },
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
        }
      },
      {
        "resourceId": "SYD-SEC-01",
        "role": "secondary",
        "metrics": {
          "latencyMs": 10,
          "availabilityPercent": 99.994,
          "jitterMs": 1.8,
          "packetLossPercent": 0.006
        }
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

### 6.3 Degraded outcome

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Degraded",
    "statusReason": "Selected resources are outside resolved runtime targets.",
    "context": {
      "constraints": {
        "location": {
          "locationId": "AU-NSW-SYD-HOSP-001",
          "displayName": "Sydney-Main-Hospital"
        },
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold"
      },
      "targets": {
        "maxLatencyMs": 10,
        "minAvailabilityPercent": 99.99,
        "maxJitterMs": 2,
        "maxPacketLossPercent": 0.01
      }
    },
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
        }
      },
      {
        "resourceId": "SYD-SEC-01",
        "role": "secondary",
        "metrics": {
          "latencyMs": 12,
          "availabilityPercent": 99.994,
          "jitterMs": 1.8,
          "packetLossPercent": 0.006
        }
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

### 6.4 Failed outcome from callback

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-003",
    "version": "v1",
    "lifecycleStatus": "Failed",
    "statusReason": "Network orchestrator reported apply failure for the selected resource configuration.",
    "context": {
      "constraints": {
        "location": {
          "locationId": "AU-NSW-SYD-HOSP-001",
          "displayName": "Sydney-Main-Hospital"
        },
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold"
      },
      "targets": {
        "maxLatencyMs": 10,
        "minAvailabilityPercent": 99.99,
        "maxJitterMs": 2,
        "maxPacketLossPercent": 0.01
      }
    },
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
    "observations": [],
    "references": {
      "correlationId": "corr-intent-callback-002",
      "intent": {
        "id": "INT-HOSP-2026-003",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-003"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      }
    }
  }
}
```

### 6.5 Terminated outcome

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Terminated",
    "statusReason": "Network orchestrator confirmed termination of the applied service configuration.",
    "context": {
      "constraints": {
        "location": {
          "locationId": "AU-NSW-SYD-HOSP-001",
          "displayName": "Sydney-Main-Hospital"
        },
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold"
      },
      "targets": {
        "maxLatencyMs": 10,
        "minAvailabilityPercent": 99.99,
        "maxJitterMs": 2,
        "maxPacketLossPercent": 0.01
      }
    },
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
    "observations": [],
    "references": {
      "correlationId": "corr-intent-terminate-001",
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

---

## 7. IntentReport projection support

IA MS does not create external `IntentReport` resources. IC MS owns external report projection.

IA MS emits enough curated facts for IC MS to build the external report expression:

| **IA fact** | **IC MS report projection** |
|---|---|
| `lifecycleStatus` | `IntentReport.expression.expressionValue.lifecycleStatus` |
| `statusReason` | `IntentReport.expression.expressionValue.statusReason` |
| `context.constraints.location`, `context.constraints.serviceType`, `context.constraints.serviceClass` | `serviceSummary` |
| `resources` | `resourceSummary` |
| `context.targets` + `observations` | fact-only `targetSummary` and `observationSummary` |

IntentReport remains fact-only by default. It does not require separate `degradationSummary`, `reoptimisationSummary`, aggregate compliance `result`, or per-target `status` fields.

---

## 8. Output event rules

- `IntentAssuranceEvent` is the single IA-owned runtime assurance outcome event.
- `IntentDriftOccurredEvent` is retired and must not be used by default.
- Use `lifecycleStatus` and `statusReason` for state narrative.
- Include `context.targets` so consumers can understand which runtime objectives observations relate to.
- Include selected/applied `resources`.
- Include `observations[].metrics` for observed telemetry.
- Do not include raw callback payloads.
- Do not include raw telemetry dumps.
- Do not include optimiser scoring or solver internals.
- Do not include `provider`.
- Do not include external TMF `IntentExpression` wrappers in internal events.
- Do not include `context.constraints` or `context.preferences` by default unless a future control-loop use case explicitly needs them.
- Do not include a default `requiresReoptimisation` flag; downstream consumers derive next action from lifecycle, reason, targets, and observations.

---

## 9. Persistence

IA MS owns its own PostgreSQL-compatible persistence boundary.

| **Table** | **Purpose** |
|---|---|
| `intent_assurance_state` | Current assurance/projection state per intent |
| `intent_assurance_observation` | Current/recent curated observations |
| `intent_assurance_idempotency` | Consumed event deduplication |
| `intent_assurance_mapping_audit` | Callback mapping and skip/dead-letter decisions |
| `intent_assurance_outbox` | Durable publication of `IntentAssuranceEvent` |
| `intent_assurance_dead_letter` | Optional dead-letter table if selected by platform policy |
| `shedlock` | Relay coordination if an embedded clustered relay is used |

---

## 10. Dependency behaviour

| **Dependency** | **Behaviour** |
|---|---|
| IA DB unavailable | Hard fail processing; do not acknowledge consumed event until retry/DLQ policy applies |
| Kafka unavailable | IA outbox retains unpublished events; relay retries later |
| Observability platform unavailable | Mark observation collection gap operationally; do not invent healthy state from missing telemetry |
| Callback topic unavailable | No new callbacks consumed; existing IA state remains unchanged |
| IC MS unavailable | IA still publishes to event backbone; IC catches up through its consumer/idempotency path |
| KP unavailable | IA uses stored applied configuration/resolved targets where available; do not query KP for every assurance decision by default |

---

## 11. Idempotency and ordering

- IA MS must process internal events idempotently.
- Deduplicate using `ce-id` / event id.
- Keep intent-scoped ordering where the event backbone supports keying by `intentId`.
- Ignore stale callbacks or observations when a newer IA state has already superseded them.
- Persist callback mapping decisions for auditability.
- Publish `IntentAssuranceEvent` through IA-owned transactional outbox.

---

## 12. Security

IA MS is internal only.

Baseline security rules:

- consume only from trusted internal event topics/integrations
- use workload identity for platform dependency access
- do not expose external user/business authorisation decisions
- do not store or emit secrets, credentials, or raw internal stack traces
- do not expose raw callback payloads in assurance events
- do not expose raw telemetry dumps in assurance events
- audit callback mapping, unknown intent handling, and lifecycle-driving assurance state changes

---

## 13. Observability

IA MS emits:

- structured logs with `correlationId`, `intentId`, `eventId`, and source event type
- callback mapping metrics
- observation evaluation metrics
- assurance lifecycle transition metrics
- outbox pending/publish-failure metrics
- duplicate event counters
- dead-letter/skip counters

Recommended metrics:

```text
ia_ms_callback_consumed_count
ia_ms_callback_unknown_intent_count
ia_ms_callback_unmapped_state_count
ia_ms_assurance_active_count
ia_ms_assurance_degraded_count
ia_ms_assurance_failed_count
ia_ms_assurance_terminated_count
ia_ms_observation_snapshot_count
ia_ms_observation_gap_count
ia_ms_outbox_pending_count
ia_ms_outbox_publish_failure_count
ia_ms_duplicate_event_count
```

---

## 14. Final baseline statement

IA MS is the internal runtime assurance truth service. It consumes optimisation, network-ready, callback, and telemetry/observation facts; normalises callback and runtime state; updates IA-owned assurance state; and emits curated `IntentAssuranceEvent` outcomes.

IC MS consumes these outcomes to project external TMF-facing `Intent` and `IntentReport` resources.

IA MS does not expose external TMF APIs, does not own callback ingestion, does not own semantic interpretation, does not own optimisation, and does not own external lifecycle resources.
