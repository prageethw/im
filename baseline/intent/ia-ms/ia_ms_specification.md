# IA MS Specification

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Scope | Intent Assurance MS internal event specification |
| Source of truth after commit | GitHub `baseline/intent/ia-ms/ia_ms_specification.md` |

## Table of contents:

- [1. Service identity](#1-service-identity)
- [2. Boundary statement](#2-boundary-statement)
- [3. Internal event style](#3-internal-event-style)
- [4. Input event contracts](#4-input-event-contracts)
  - [4.1. IntentNetworkReadyEvent input](#41-intentnetworkreadyevent-input)
    - [4.1.1. Example headers](#411-example-headers)
    - [4.1.2. Example body](#412-example-body)
    - [4.1.3. IA handling rules](#413-ia-handling-rules)
  - [4.2. IntentCallbackEvent input](#42-intentcallbackevent-input)
    - [4.2.1. Example headers](#421-example-headers)
    - [4.2.2. Example body — apply success callback](#422-example-body-apply-success-callback)
    - [4.2.3. IA handling rules](#423-ia-handling-rules)
  - [4.3. Metrics collection through observation endpoints](#43-metrics-collection-through-observation-endpoints)
    - [4.3.1. Logical metrics returned to IA MS](#431-logical-metrics-returned-to-ia-ms)
- [5. Callback state mapping](#5-callback-state-mapping)
- [6. Output event contract — IntentAssuranceEvent](#6-output-event-contract-intentassuranceevent)
  - [6.1. Common headers](#61-common-headers)
  - [6.2. Generic payload model](#62-generic-payload-model)
  - [6.3. Active outcome](#63-active-outcome)
  - [6.4. Degraded outcome](#64-degraded-outcome)
- [7. IntentReport projection support](#7-intentreport-projection-support)
- [8. Output event rules](#8-output-event-rules)
- [9. Persistence](#9-persistence)
- [10. Dependency behaviour](#10-dependency-behaviour)
- [11. Final baseline statement](#11-final-baseline-statement)

## 1. Service identity

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Assurance MS |
| Short name | IA MS |
| Service name | `intent-assurance-ms` |
| Domain | Intent Domain |
| External API owner | No external TMF-compliant API |
| Main responsibility | Runtime assurance truth, callback state normalisation, observation evaluation, and `IntentAssuranceEvent` publication |
| Main input events | `IntentNetworkReadyEvent`, `IntentCallbackEvent` |
| Main output event | `IntentAssuranceEvent` |
| Retired event | `IntentDriftOccurredEvent` is not used |

---

## 2. Boundary statement

IA MS owns runtime assurance truth after network-ready configuration, apply callback, and observation metrics are available.

IA MS consumes only:

- `IntentNetworkReadyEvent`
- `IntentCallbackEvent`
- runtime metrics / observation facts from observability endpoints

IA MS does **not** consume `IntentOptimisedEvent` in the active baseline.

Optimisation output may influence the service-ready configuration produced upstream, but IA receives its assurance/apply context through `IntentNetworkReadyEvent.serviceConfiguration` and IA stored/applied assurance state.

IC MS consumes `IntentAssuranceEvent` and projects the external TMF-compliant `Intent.lifecycleStatus` and `IntentReport.expression.expressionValue`.

IA MS does not own external TMF APIs, runtime `Intent` resources, design-time `IntentSpecification`, semantic interpretation, optimisation decisions, callback ingestion, or network change-execution/apply execution.

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

Internal IA events must not use external TMF `IntentExpression` wrappers. Those wrappers are used only in external IC MS REST resources and external TMF-aligned events.

---

## 4. Input event contracts

### 4.1. IntentNetworkReadyEvent input

IA MS consumes `IntentNetworkReadyEvent` to learn the apply plan and observer scope.

`IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`. IA MS must not emit `IntentNetworkReadyEvent`.

#### 4.1.1. Example headers

```http
ce-specversion: 1.0
ce-type: IntentNetworkReadyEvent
ce-source: intent-intelligence-ms
ce-id: evt-intent-network-ready-001
ce-time: 2026-04-18T12:12:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

#### 4.1.2. Example body

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "InProgress",
    "statusReason": "Service configuration has been prepared for change-execution/apply.",
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
    "serviceConfiguration": {
      "orchestratorConfiguration": {
        "target": "t7-network-orchestrator",
        "profile": "hospital-surgical-slice-apply-v1",
        "resources": [
          {
            "resourceId": "SYD-PRI-01",
            "resourceType": "deliveryResource",
            "resourceClass": "critical-gold",
            "roles": ["primary"],
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
            "roles": ["secondary"],
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
            "roles": ["primary"],
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
          },
          {
            "resourceId": "SYD-SEC-02",
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
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001"
      }
    }
  }
}
```

#### 4.1.3. IA handling rules

- Treat `IntentNetworkReadyEvent` as service configuration prepared for apply, not as apply success.
- Store selected apply resources from `serviceConfiguration.orchestratorConfiguration.resources`.
- Store monitored resource scope from `serviceConfiguration.observerConfiguration.resources`; later `IntentAssuranceEvent.body.current.resources[]` mirrors that observer scope when reporting observed resource metrics.
- Store resolved runtime `body.expression.context` as the assurance context.
- Do not emit `Active` solely because `IntentNetworkReadyEvent` was consumed.
- Active state requires apply/callback confirmation and/or runtime observations according to the workflow.
- Key state by `intentId` and `intentVersion` where supplied; stale `IntentNetworkReadyEvent` instances must not overwrite newer assurance state.

---

### 4.2. IntentCallbackEvent input

IA MS consumes raw callback relay events emitted by ICB MS.

The canonical callback fields are:

- `callbackSource`
- `callbackTimestamp`
- `sourceState`

`sourceState.state` carries the raw source/change-execution state value such as `APPLIED`, `APPLY_FAILED`, or `TERMINATED`.

Do not use retired source-specific callback state/source/timestamp field names as the baseline callback field names.

#### 4.2.1. Example headers

```http
ce-specversion: 1.0
ce-type: IntentCallbackEvent
ce-source: intent-callback-ms
ce-id: evt-intent-callback-001
ce-time: 2026-04-18T12:15:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

#### 4.2.2. Example body — apply success callback

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "callbackSource": "t7-network-orchestrator",
    "callbackTimestamp": "2026-04-18T12:14:58+10:00",
    "sourceState": {
      "state": "APPLIED",
      "reason": "Configuration applied successfully."
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

#### 4.2.3. IA handling rules

- Validate/correlate `intentId` against IA state and platform context.
- Derive source/change-execution type from IA/platform context where required, not from ICB MS.
- Map raw `sourceState.state` into IA lifecycle/assurance meaning.
- Do not expose raw callback payloads in `IntentAssuranceEvent`.
- ICB MS remains the owner of callback ingestion and callback outbox persistence.

---

### 4.3. Metrics collection through observation endpoints

IA MS does not consume a separately named observation snapshot event in the active baseline.

IA MS obtains runtime metrics from observability/observation endpoints that are selected or informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration`.

#### 4.3.1. Logical metrics returned to IA MS

```json
{
  "observedAt": "2026-04-18T12:29:55+10:00",
  "resourceMetrics": [
    {
      "resourceId": "SYD-PRI-01",
      "roles": ["primary"],
      "metrics": {
        "latencyMs": 18,
        "availabilityPercent": 99.992,
        "jitterMs": 1.8,
        "packetLossPercent": 0.006
      }
    },
    {
      "resourceId": "SYD-PRI-02",
      "roles": ["primary"],
      "metrics": {
        "latencyMs": 14,
        "availabilityPercent": 99.993,
        "jitterMs": 1.7,
        "packetLossPercent": 0.006
      }
    },
    {
      "resourceId": "SYD-SEC-01",
      "roles": ["secondary"],
      "metrics": {
        "latencyMs": 12,
        "availabilityPercent": 99.994,
        "jitterMs": 1.8,
        "packetLossPercent": 0.006
      }
    },
    {
      "resourceId": "SYD-SEC-02",
      "roles": ["secondary"],
      "metrics": {
        "latencyMs": 13,
        "availabilityPercent": 99.993,
        "jitterMs": 1.9,
        "packetLossPercent": 0.007
      }
    }
  ]
}
```


IA MS must apply configured observation freshness and retry policy to metrics collected from observability endpoints. Stale or incomplete observations must not produce a misleading healthy state. When observation collection fails after retry policy is exhausted, IA MS must record the operational gap and route to DLQ or operational handling according to policy.

---

## 5. Callback state mapping

| **Raw `sourceState.state`** | **IA treatment** | **Typical `IntentAssuranceEvent.lifecycleStatus`** |
|---|---|---|
| `APPLY_ACCEPTED` | Apply request accepted by source/change-execution layer | `InProgress` |
| `APPLY_IN_PROGRESS` | Apply still underway | `InProgress` |
| `APPLIED` | Apply completed; runtime observations may further confirm health | `Active` |
| `APPLY_REJECTED` | Apply request rejected before successful application | `Failed` |
| `APPLY_FAILED` | Apply failed after attempt | `Failed` |
| `TERMINATION_ACCEPTED` | Termination accepted | `InProgress` |
| `TERMINATED` | Termination confirmed | `Terminated` |
| Unknown/unmapped | Record skip/dead-letter/operational handling decision | No default lifecycle event unless policy requires one |

This mapping is intentionally IA-owned. ICB MS must not map source states into lifecycle states.

IA MS must also treat callback and observation inputs as version-aware where `intentVersion` is available. Late callbacks, stale observations, or events for a superseded or terminated intent version must be recorded for audit or dead-letter handling according to policy and must not overwrite current-version assurance state.

---

## 6. Output event contract — IntentAssuranceEvent

### 6.1. Common headers

```http
ce-specversion: 1.0
ce-type: IntentAssuranceEvent
ce-source: intent-assurance-ms
ce-id: evt-intent-assurance-001
ce-time: 2026-04-18T12:20:00+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 6.2. Generic payload model

`IntentAssuranceEvent` uses the generic assurance model below.

| **Field / area** | **Purpose** |
|---|---|
| `body.expression.context` | Resolved runtime context with targets, constraints, and preferences where relevant, derived from `IntentNetworkReadyEvent.body.expression.context` |
| `body.current.resources` | Full observed resource/path set within the assurance scope, including primary and all secondary/alternative resources supplied through `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources` |
| `body.references` | Correlation and resource references |

Reusable resource entries use:

- `roles`
- `resourceId`
- `resourceType`
- `resourceClass`
- direct safe resource attributes such as `accessTechnology` where needed
- `relationships`
- `metrics`

Controlled vocabulary baseline:

- `roles`: `primary`, `secondary`
- `resourceType`: `deliveryResource`, `computeResource`, `storageResource`, `securityResource`, `platformResource`
- `resourceClass`: `critical-gold`, `critical-silver`, `standard`, `best-effort`

Do not use resource-level `selectionStatus` or `assuranceStatus` by default. The interpreted assurance outcome is represented by `lifecycleStatus` and `statusReason`.

`body.current.resources` carries the full observed resource/path set for `Active`, `Degraded`, and `Failed` assurance outcomes. It is not limited to the currently active primary path. When IA receives multiple observing paths from `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[]`, IA reports metrics for the same observed set so downstream consumers can see the affected path and all monitored alternatives in the same event.

Metric names stay neutral and describe the measurement itself, such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.

Do not encode metric origin or evaluation context in field names or wrappers. Do not use wrappers or names such as `benchmark`, `telemetry`, `observed`, `current`, `latencyBenchmarkMs`, or `currentLatencyMs` by default. The event type and lifecycle stage provide the context for interpreting the metric values.


`requiresReoptimisation` is not included by default. II MS or another authorised decision component reads `lifecycleStatus`, `statusReason`, and the full observed resource metrics, then decides whether re-interpretation, re-optimisation, reselection, or no action is required.

For `Terminated`, `current.resources` is normally not required unless reporting final resource facts.

### 6.3. Active outcome

For `Active`, IA MS uses `body.current.resources` to report the full observed resource/path set within the assurance scope, not only the primary path. The event remains fact-based: lifecycle/status reason plus neutral resource metrics.

Do not include `current.evaluations` or `body.evaluations` by default.

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "Active",
    "statusReason": "All monitored delivery resources are operating within resolved runtime targets.",
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
          "roles": [
            "primary"
          ],
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "accessTechnology": "fibre",
          "relationships": [
            {
              "type": "pairedSecondary",
              "resourceId": "SYD-SEC-01"
            }
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
          "roles": [
            "primary"
          ],
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "accessTechnology": "5G",
          "relationships": [
            {
              "type": "pairedSecondary",
              "resourceId": "SYD-SEC-02"
            }
          ],
          "metrics": {
            "latencyMs": 8,
            "availabilityPercent": 99.995,
            "jitterMs": 1.5,
            "packetLossPercent": 0.005
          }
        },
        {
          "resourceId": "SYD-SEC-01",
          "roles": [
            "secondary"
          ],
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "accessTechnology": "5G",
          "relationships": [
            {
              "type": "alternativeTo",
              "resourceId": "SYD-PRI-01"
            }
          ],
          "metrics": {
            "latencyMs": 9,
            "availabilityPercent": 99.994,
            "jitterMs": 1.7,
            "packetLossPercent": 0.006
          }
        },
        {
          "resourceId": "SYD-SEC-02",
          "roles": [
            "secondary"
          ],
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "accessTechnology": "fibre",
          "relationships": [
            {
              "type": "alternativeTo",
              "resourceId": "SYD-PRI-02"
            }
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
      "correlationId": "corr-intent-assurance-active-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001"
      }
    }
  }
}
```

### 6.4. Degraded outcome

For `Degraded`, IA MS still uses `body.current.resources` to report the full observed resource/path set within the assurance scope. The set includes the degraded resource and all monitored alternatives supplied through `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources`.

This shape lets II MS or another authorised decision component inspect the affected primary path, all observed secondary paths, and their neutral metrics without needing a separate `requiresReoptimisation` flag, a separate evaluations block, a separate `candidates` block, or resource-level status fields.

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "Degraded",
    "statusReason": "Current primary path latency is outside resolved runtime targets.",
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
          "roles": [
            "primary"
          ],
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "accessTechnology": "fibre",
          "relationships": [
            {
              "type": "pairedSecondary",
              "resourceId": "SYD-SEC-01"
            }
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
          "roles": [
            "primary"
          ],
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "accessTechnology": "5G",
          "relationships": [
            {
              "type": "pairedSecondary",
              "resourceId": "SYD-SEC-02"
            }
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
          "roles": [
            "secondary"
          ],
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "accessTechnology": "5G",
          "relationships": [
            {
              "type": "alternativeTo",
              "resourceId": "SYD-PRI-01"
            }
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
          "roles": [
            "secondary"
          ],
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "accessTechnology": "fibre",
          "relationships": [
            {
              "type": "alternativeTo",
              "resourceId": "SYD-PRI-02"
            }
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
      "correlationId": "corr-intent-assurance-degraded-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001"
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
| `expression.context.constraints.location`, `expression.context.constraints.serviceType`, `expression.context.constraints.serviceClass` | `serviceSummary` |
| `current.resources` | `resourceSummary`, including the full observed resource/path set within the assurance scope |
| `expression.context.targets` + `current.resources.metrics` | fact-only `targetSummary` and `observationSummary` |

IntentReport remains fact-only by default. It does not require separate `degradationSummary`, `reoptimisationSummary`, aggregate compliance `result`, or per-target `status` fields.

---

## 8. Output event rules

- `IntentAssuranceEvent` is the single IA-owned runtime assurance outcome event.
- `IntentDriftOccurredEvent` is retired and must not be used by default.
- Use `lifecycleStatus` and `statusReason` for state narrative.
- Use internal `body.expression.context` where the event carries resolved runtime targets, constraints, and preferences.
- Use `current.resources` for the full observed resource/path set within the assurance scope, including primary and all observed secondary/alternative resources.
- Do not include `current.evaluations` or `body.evaluations` by default.
- For `Degraded` and `Failed`, keep the affected resource and all observed alternatives together in `current.resources` by default.
- Do not use a separate `candidates` block by default in `IntentAssuranceEvent`; IA reports observed assurance facts, while II MS or another authorised decision component decides whether re-interpretation, re-optimisation, or reselection is required.
- Do not include resource-level `selectionStatus` or `assuranceStatus` by default; derive interpreted state from `lifecycleStatus` and `statusReason`.
- Do not include raw callback payloads.
- Do not include raw telemetry dumps.
- Do not include optimiser scoring or solver internals.
- Do not include `provider`.
- Do not include external TMF `IntentExpression` wrappers in internal events; use the internal `body.expression.context` wrapper only.
- Do not include a default `requiresReoptimisation` flag. II MS or another authorised decision component reads the assurance event state and decides whether re-interpretation or re-optimisation is required.

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
| `intent_assurance_dead_letter` | Required minimum dead-letter handling for exhausted input processing, unknown or invalid callbacks, stale/superseded event handling that cannot be safely ignored, and repeated observation collection failures after retry policy is exhausted |
| `shedlock` | Relay coordination if an embedded clustered relay is used |

DLQ handling is a required minimum baseline for exhausted `IntentNetworkReadyEvent` and `IntentCallbackEvent` processing, unknown `intentId`, unknown or unmapped `sourceState.state`, invalid event shape, stale or superseded version handling that cannot be safely ignored, and repeated observation collection failures after retry policy is exhausted.

---

## 10. Dependency behaviour

| **Dependency** | **Behaviour** |
|---|---|
| IA DB unavailable | Hard fail processing; do not acknowledge consumed event until retry/DLQ policy applies |
| Kafka unavailable | IA outbox retains unpublished events; relay retries later |
| Observability platform unavailable, stale, or incomplete | Retry according to configured policy, mark the observation collection gap operationally, retain previous assurance state where safe, and do not invent healthy state from missing or stale telemetry |
| Callback topic unavailable | No new callbacks consumed; existing IA state remains unchanged |
| IC MS unavailable | IA still publishes to event backbone; IC catches up through its consumer/idempotency path |
| KP unavailable | IA uses stored applied configuration/resolved targets where available; do not query KP for every assurance decision by default |

---

## 11. Final baseline statement

IA MS is the internal runtime assurance truth service. It consumes `IntentNetworkReadyEvent`, `IntentCallbackEvent`, and runtime metrics/observation facts only; normalises callback and runtime state; updates IA-owned assurance state; and emits curated generic `IntentAssuranceEvent` outcomes. IC MS consumes these outcomes to project external TMF-compliant `Intent` and `IntentReport` resources.