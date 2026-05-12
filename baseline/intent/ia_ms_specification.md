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

IA MS owns runtime assurance truth after network-ready configuration, apply callback, and observation metrics are available.

IA MS consumes only:

- `IntentNetworkReadyEvent`
- `IntentCallbackEvent`
- runtime metrics / observation facts from observability endpoints

IA MS does **not** consume `IntentOptimisedEvent` in the active baseline. Optimisation output may influence the service-ready configuration produced upstream, but IA receives its assurance/apply context through `IntentNetworkReadyEvent.serviceConfiguration` and IA stored/applied assurance state.

IC MS consumes `IntentAssuranceEvent` and projects the external TMF-facing `Intent.lifecycleStatus` and `IntentReport.expression.expressionValue`.

IA MS does not own external TMF APIs, runtime `Intent` resources, design-time `IntentSpecification`, semantic interpretation, optimisation decisions, callback ingestion, or network orchestration/apply execution.

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

---

## 4. Input event contracts

### 4.1 IntentNetworkReadyEvent input

IA MS consumes `IntentNetworkReadyEvent` to learn the apply plan and observer scope.

`IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`. IA MS must not emit `IntentNetworkReadyEvent`.

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
- Store selected apply resources from `serviceConfiguration.orchestratorConfiguration.resources`.
- Store monitored resource scope from `serviceConfiguration.observerConfiguration.resourceIds`.
- Store resolved runtime `body.context` as the assurance context.
- Do not emit `Active` solely because `IntentNetworkReadyEvent` was consumed.
- Active state requires apply/callback confirmation and/or runtime observations according to the workflow.

---

### 4.2 IntentCallbackEvent input

IA MS consumes raw callback relay events emitted by ICB MS.

The canonical callback fields are:

- `callbackSource`
- `callbackTimestamp`
- `sourceState`

`sourceState.state` carries the raw source/orchestrator state value such as `APPLIED`, `APPLY_FAILED`, or `TERMINATED`.

Do not use `orchestratorState`, `orchestratorSource`, or `orchestratorTimestamp` as the baseline callback field names.

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
    "callbackSource": "t7-network-orchestrator",
    "callbackTimestamp": "2026-04-18T12:14:58+10:00",
    "sourceState": {
      "state": "APPLIED",
      "reason": "Configuration applied successfully."
    }
  }
}
```

#### IA handling rules

- Validate/correlate `intentId` against IA state and platform context.
- Derive source/orchestrator type from IA/platform context where required, not from ICB MS.
- Map raw `sourceState.state` into IA lifecycle/assurance meaning.
- Do not expose raw callback payloads in `IntentAssuranceEvent`.
- ICB MS remains the owner of callback ingestion and callback outbox persistence.

---

### 4.3 Metrics collection through observation endpoints

IA MS does not consume a separately named observation snapshot event in the active baseline.

IA MS obtains runtime metrics from observability/observation endpoints that are selected or informed by `IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration`.

#### Logical metrics returned to IA MS

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
      "resourceId": "SYD-SEC-01",
      "roles": ["secondary"],
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

---

## 5. Callback state mapping

| **Raw `sourceState.state`** | **IA treatment** | **Typical `IntentAssuranceEvent.lifecycleStatus`** |
|---|---|---|
| `APPLY_ACCEPTED` | Apply request accepted by source/orchestration layer | `InProgress` |
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

### 6.2 Generic payload model

`IntentAssuranceEvent` uses the generic assurance model below.

| **Field / area** | **Purpose** |
|---|---|
| `body.context` | Resolved runtime context with targets, constraints, and preferences where relevant |
| `body.current.resources` | Currently selected/applied/observed resources for normal/active states |
| `body.candidates` | All applicable available resources for degraded/failed re-decision states, including the currently used resource and alternatives, each with metrics and status indicators |
| `body.references` | Correlation and resource references |

Reusable resource entries use:

- `roles`
- `resourceId`
- `resourceType`
- `resourceClass`
- `resourceAttributes`
- `relationships`
- `metrics`

Current runtime metric names use `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.

Benchmark context may use `latencyBenchmarkMs`, `availabilityBenchmarkPercent`, `jitterBenchmarkMs`, and `packetLossBenchmarkPercent`.

Do not duplicate `resourceId` into `resourceAttributes.pathId` when they are identical.

`requiresReoptimisation` is not included by default. II MS or another authorised decision component reads lifecycleStatus, statusReason, resource metrics, and candidates, then decides whether re-interpretation, re-optimisation, reselection, or no action is required.

For `Active`, `body.current.resources` is acceptable because there is no re-decision pressure. For `Degraded` and `Failed`, do not include a separate `current` block by default; instead place the current resource and alternatives together in `body.candidates`, using candidate-level `selectionStatus`, `assuranceStatus`, and resource metrics to make the current/degraded resource explicit. For `Terminated`, candidates are normally not required unless reporting final resources.

### 6.3 Active outcome

For `Active`, IA MS may use `body.current.resources` because there is no re-decision pressure. The event remains fact-based: lifecycle/status reason plus resource metrics.

Do not include `current.evaluations` or `body.evaluations` by default.

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Active",
    "statusReason": "Selected resources are operating within resolved runtime targets.",
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
    "current": {
      "resources": [
        {
          "resourceId": "SYD-PRI-01",
          "roles": ["primary", "current"],
          "selectionStatus": "CURRENT",
          "assuranceStatus": "HEALTHY",
          "resourceType": "networkPath",
          "resourceClass": "critical-gold-access",
          "resourceAttributes": {
            "accessTechnology": "fibre",
            "locationId": "AU-NSW-SYD-HOSP-001"
          },
          "relationships": [
            {
              "type": "pairedSecondary",
              "targetResourceId": "SYD-SEC-01"
            }
          ],
          "metrics": {
            "latencyMs": 8,
            "availabilityPercent": 99.995,
            "jitterMs": 1.5,
            "packetLossPercent": 0.005,
            "latencyBenchmarkMs": 7,
            "availabilityBenchmarkPercent": 99.996,
            "jitterBenchmarkMs": 1.1,
            "packetLossBenchmarkPercent": 0.004
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
        "id": "hospital-surgical-slice-spec-v1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      }
    }
  }
}
```

### 6.4 Degraded outcome

For `Degraded`, IA MS does not include a separate `current` block by default.

The degraded/current resource and all applicable alternatives are represented together in `body.candidates`. This shape lets II MS or another authorised decision component inspect the current degraded resource, available alternatives, and their metrics without needing a separate `requiresReoptimisation` flag or a separate evaluations block.

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Degraded",
    "statusReason": "Current primary path latency is outside resolved runtime targets.",
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
    "candidates": [
      {
        "resourceId": "SYD-PRI-01",
        "roles": ["primary", "current"],
        "selectionStatus": "CURRENT",
        "assuranceStatus": "DEGRADED",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceAttributes": {
          "accessTechnology": "fibre",
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "targetResourceId": "SYD-SEC-01"
          }
        ],
        "metrics": {
          "latencyMs": 18,
          "availabilityPercent": 99.992,
          "jitterMs": 1.8,
          "packetLossPercent": 0.006,
          "latencyBenchmarkMs": 7,
          "availabilityBenchmarkPercent": 99.996,
          "jitterBenchmarkMs": 1.1,
          "packetLossBenchmarkPercent": 0.004
        }
      }
    ],
    "references": {
      "correlationId": "corr-intent-assurance-degraded-001",
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
| `current.resources` | `resourceSummary` |
| `context.targets` + `current.resources.metrics` + resource-level `selectionStatus` / `assuranceStatus` | fact-only `targetSummary` and `observationSummary` |
| `candidates` | Internal/authorised decision support where exposed by policy, not default public report detail |

IntentReport remains fact-only by default. It does not require separate `degradationSummary`, `reoptimisationSummary`, aggregate compliance `result`, or per-target `status` fields.

---

## 8. Output event rules

- `IntentAssuranceEvent` is the single IA-owned runtime assurance outcome event.
- `IntentDriftOccurredEvent` is retired and must not be used by default.
- Use `lifecycleStatus` and `statusReason` for state narrative.
- Use internal `context` where the event carries resolved runtime targets, constraints, and preferences.
- Use `current.resources` for normal/active-state resource facts where there is no immediate re-decision pressure.
- Do not include `current.evaluations` or `body.evaluations` by default.
- For `Degraded` and `Failed`, prefer no separate `current` block by default. Use `candidates`.
- In degraded/failed states, `candidates` includes all applicable available resources, including the current degraded/failed resource and alternatives, with candidate-level `selectionStatus`, `assuranceStatus`, runtime metrics, and benchmark metrics.
- Do not include raw callback payloads.
- Do not include raw telemetry dumps.
- Do not include optimiser scoring or solver internals.
- Do not include `provider`.
- Do not include external TMF `IntentExpression` wrappers in internal events.
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

## 11. Final baseline statement

IA MS is the internal runtime assurance truth service. It consumes `IntentNetworkReadyEvent`, `IntentCallbackEvent`, and runtime metrics/observation facts only; normalises callback and runtime state; updates IA-owned assurance state; and emits curated generic `IntentAssuranceEvent` outcomes. IC MS consumes these outcomes to project external TMF-facing `Intent` and `IntentReport` resources.
