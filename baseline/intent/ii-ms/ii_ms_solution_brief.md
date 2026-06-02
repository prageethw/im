# Intent Intelligence MS Solution Brief

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Scope | Intent Intelligence MS solution brief |
| Source of truth after commit | GitHub `baseline/intent/ii-ms/ii_ms_solution_brief.md` |

## Table of contents:

- [1. Summary:](#1-summary)
- [2. Logical View:](#2-logical-view)
- [3. Process View:](#3-process-view)
- [4. Solution Elaboration:](#4-solution-elaboration)
  - [4.1. Required pre-resolution validation:](#41-required-pre-resolution-validation)
- [5. Responsibilities:](#5-responsibilities)
- [6. II MS does not:](#6-ii-ms-does-not)
- [7. Contracts:](#7-contracts)
- [8. Event delivery path:](#8-event-delivery-path)
- [9. Inbound internal Kafka event shape:](#9-inbound-internal-kafka-event-shape)
  - [9.1. IntentValidatedEvent:](#91-intentvalidatedevent)
  - [9.2. OptimisationStatusChangeEvent:](#92-optimisationstatuschangeevent)
- [10. Field specification:](#10-field-specification)
- [11. Fields not accepted:](#11-fields-not-accepted)
- [12. Authorisation:](#12-authorisation)
- [13. Persistence / state / outbox model:](#13-persistence-state-outbox-model)
- [14. Internal Kafka publication:](#14-internal-kafka-publication)
- [15. Internal Kafka topics:](#15-internal-kafka-topics)
- [16. Event identity:](#16-event-identity)
- [17. Internal Kafka CloudEvents headers:](#17-internal-kafka-cloudevents-headers)
- [18. Internal Kafka message body: IntentRejectedEvent:](#18-internal-kafka-message-body-intentrejectedevent)
- [19. Internal Kafka message body: IntentResolvedEvent:](#19-internal-kafka-message-body-intentresolvedevent)
- [20. Internal Kafka message body: IntentNetworkReadyEvent:](#20-internal-kafka-message-body-intentnetworkreadyevent)
- [21. Behaviour:](#21-behaviour)
  - [21.1. Successful semantic resolution:](#211-successful-semantic-resolution)
  - [21.2. Semantic rejection:](#212-semantic-rejection)
  - [21.3. Service-ready preparation:](#213-service-ready-preparation)
  - [21.4. Idempotency:](#214-idempotency)
  - [21.5. Ordering:](#215-ordering)
  - [21.6. Dependency failure:](#216-dependency-failure)
- [22. Configuration:](#22-configuration)
- [23. Consumer contract:](#23-consumer-contract)
- [24. Open items:](#24-open-items)
- [25. Closed items:](#25-closed-items)
- [26. MS identity:](#26-ms-identity)


## 1. Summary:

Intent Intelligence MS (II MS) is the internal semantic interpretation and resolution service for admitted runtime intents. It consumes syntactically admitted intent facts from Intent Controller MS (IC MS), interprets the admitted expression using governed Knowledge Plane data and any additional pre-resolution validation sources required by the use case, validates semantic feasibility, policy, capability, resource context, and other use-case-specific facts, and emits the next internal milestone event.

II MS is not an external TMF-compliant API service. It does not expose runtime Intent REST APIs, design-time IntentSpecification APIs, customer-facing lifecycle projections, callback endpoints, network change execution, or assurance truth.

Its responsibility is to convert a syntactically accepted runtime intent into one of the following internal outcomes:

- `IntentRejectedEvent` when the admitted intent cannot be semantically, policy, or capability resolved.
- `IntentResolvedEvent` as an optional observability and audit milestone when the admitted intent has been semantically resolved into a canonical intent context and a full, valid candidate resource set. 
- `IntentNetworkReadyEvent` when II MS has prepared the concrete service configuration needed for change execution and assurance observation.

`IntentResolvedEvent` and `IntentNetworkReadyEvent` are intentionally different milestones. `IntentResolvedEvent` is the candidate-level semantic-resolution handoff. `IntentNetworkReadyEvent` is the service-ready preparation handoff to IA MS and means the service configuration/resource set has been prepared for change execution and assurance observation. It does not mean the network application has succeeded. IntentNetworkReadyEvent may be emitted only after II MS has received or derived a governed selected configuration from the authorised downstream selection or optimisation path. II MS does not own the optimisation algorithm or optimiser backend. II MS owns packaging the selected configuration into the service-ready event for IA MS.

For optimisation-backed selection, II MS uses the approved Optimiser platform integration pattern: `POST /optimisation` for the governed REST request, with the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, registered or supplied as the optimiser outcome target. The Optimiser platform sends `OptimisationStatusChangeEvent` to ICB MS. ICB MS ingests the callback and publishes `OptimisationStatusChangeEvent` to Kafka for II MS consumption. The Optimiser platform owns optimisation execution, selection logic, solver models, and optimiser lifecycle. II MS owns submitting the governed request, correlating the Kafka-delivered optimiser outcome, and packaging that selected configuration into `IntentNetworkReadyEvent` for IA MS.

## 2. Logical View:

![alt text](ii_ms_logical_view.svg)

II MS sits after IC MS in the runtime intent processing flow and before optimiser, change-execution, and assurance stages.

```text
External Intent API -> IC MS syntactic admission and persistence -> IntentValidatedEvent -> II MS semantic interpretation and KP-backed resolution -> IntentRejectedEvent | IntentResolvedEvent | IntentNetworkReadyEvent
```

Logical responsibilities:

| Area | II MS responsibility |
|---|---|
| Runtime input | Consume `IntentValidatedEvent` from the internal event backbone. |
| Semantic interpretation | Interpret the admitted `expression.context` model. |
| Knowledge Plane validation | Resolve and validate location, service type, service class, targets, constraints, preferences, policy, and capability context using KP and approved external pre-resolution validation sources where required. |
| Suitability and proceedability validation | Decide whether the admitted intent has enough trusted semantic, policy, capability, availability, freshness, and pre-resolution facts to proceed safely. If KP or approved validation sources show the intent is unsupported, contradictory, unsafe, unavailable, stale, or insufficiently validated, II MS emits `IntentRejectedEvent` or records a governed processing failure instead of proceeding to candidate discovery or optimisation. |
| Canonicalisation | Preserve and normalise canonical semantic buckets: `targets`, `constraints`, and `preferences`. |
| Candidate discovery | Resolve the full valid candidate resource set known for the resolved context after scope/policy filtering. |
| Rejection decision | Emit `IntentRejectedEvent` for semantic, policy, capability, or processing rejection. |
| Resolution observability milestone | Optionally emit `IntentResolvedEvent` after candidate-level semantic resolution for observability, audit, replay, or future consumers. |
| Service-ready handoff | Emit `IntentNetworkReadyEvent` when service configuration is prepared for change execution and assurance observation. |
| Reliability | Use idempotent consumption and outbox-backed publication. |
| Audit | Persist the semantic decision trail where required. |

## 3. Process View:

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
11. For optimisation-backed selection, II MS submits `POST /optimisation` and registers or supplies the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`.
12. ICB MS ingests the external optimiser callback and publishes `OptimisationStatusChangeEvent` to Kafka.
13. II MS consumes and correlates the Kafka-delivered `OptimisationStatusChangeEvent` before emitting `IntentNetworkReadyEvent`.
14. Consumers continue the workflow according to the milestone event emitted.

## 4. Solution Elaboration:

II MS exists because IC MS admission validation is intentionally syntactic and contract-focused.

IC MS can confirm that an external runtime Intent request is structurally valid and references an active IntentSpecification, but it should not decide whether the requested outcome is semantically possible, policy-allowed, supported by the Knowledge Plane, or resolvable into a candidate resource set. II MS performs that semantic decision step. It treats the admitted expression as an internal runtime intent fact model, not as a customer-facing API payload.

The canonical semantic structure is preserved across the pipeline:

```text
expression.context.targets
expression.context.constraints
expression.context.preferences
```

`targets` are measurable runtime objectives such as maximum latency, minimum availability, maximum jitter, and maximum packet loss. `constraints` are hard requirements and required non-target inputs such as location, service type, service class, priority, redundancy requirement, and time window. `preferences` are soft selection guidance, such as preferred access technology.

II MS must not flatten these buckets into unrelated top-level fields. Keeping the same semantic buckets from ID MS to IC MS to II MS reduces mapping, prevents drift, and allows IA MS and later control-loop components to interpret assurance outcomes against the same intent context.

### 4.1. Required pre-resolution validation:

The hospital surgical slice baseline mainly uses Knowledge Plane data and optimiser-related references, but II MS is not limited to Knowledge Plane and optimiser integration. Different intent domains may require II MS to perform additional pre-resolution validation before it can resolve an admitted intent accurately and meet the intent safely. This validation may consult approved T7 platform services, inventory systems, policy services, topology sources, catalogue services, capacity sources, fulfilment systems, or other governed domain sources.

Those systems provide facts for semantic interpretation, capability validation, policy validation, candidate discovery, or service-ready preparation. They do not own the external `Intent` lifecycle, and they do not change the II MS event ownership model. II MS still curates the resolved facts and emits `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` according to the same contract rules.

II MS must not dump raw source-system responses into events. Only validated, normalised, and next-stage-relevant facts should be carried forward in the canonical `targets`, `constraints`, `preferences`, `resources`, and `serviceConfiguration` structures.

The baseline surgical hospital slice is an illustrative runtime example used to make the II MS semantic interpretation and Knowledge Plane-backed resolution contract concrete. It is not the only supported runtime Intent type, IntentSpecification, service class, schema, expression IRI, location, service type, Knowledge Plane profile, or deployment profile. Other runtime Intents may use different targets, constraints, preferences, expression schemas, service types, priorities, resources, and governance profiles while following the same II MS contract rules.

## 5. Responsibilities:

II MS owns:

| Responsibility | Description |
|---|---|
| `IntentValidatedEvent` consumption | Consume admitted runtime intent events from IC MS. |
| Semantic interpretation | Interpret admitted intent expression context into canonical domain meaning. |
| KP-backed and required pre-resolution validation | Validate location, service type, service class, capability, policy, resource availability, and other use-case-specific facts using KP and approved pre-resolution validation sources where required. |
| Target validation | Validate supported measurable runtime objectives. |
| Constraint validation | Validate hard requirements such as location, priority, redundancy, and time window. |
| Preference preservation | Preserve soft selection guidance for downstream selection/optimisation. |
| Candidate resource resolution | Build the full, valid candidate resource set after applicable scope and policy filtering. |
| Semantic rejection | Emit `IntentRejectedEvent` with intent-domain reason codes. |
| Candidate-level resolution observability | Optionally emit `IntentResolvedEvent` for observability, audit, replay, or future consumers after safe semantic resolution. |
| Service-ready preparation | Emit `IntentNetworkReadyEvent` with prepared change-execution and observation configuration. |
| Idempotency | Deduplicate consumed events and avoid duplicate milestone outcomes. |
| Persistence | Store current semantic resolution state, decision audit, idempotency records, and outbox entries. |
| Event publication | Publish II-owned events reliably using the outbox relay pattern. |

## 6. II MS does not:

| Concern | Owner |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| Runtime `Intent` REST API | IC MS |
| Runtime `IntentReport` REST API and projection | IC MS |
| External lifecycle/status projection | IC MS |
| External TMF subscription APIs | IC MS / ID MS depending on resource |
| External consumer authorisation | Gateway / OEX / domain-facing API layer before the internal event flow |
| Downstream optimisation algorithm ownership | Optimiser service |
| Network change execution | Change execution layer / network orchestrator |
| Apply outcome truth | IA MS |
| Runtime assurance truth | IA MS |
| Callback ingestion | ICB MS |
| Raw callback interpretation and lifecycle mapping | IA MS |
| KP configuration CRUD/governance | Knowledge Plane operating model |
| Public, partner, OEX, or NGW-facing API exposure | Not applicable to II MS |

## 7. Contracts:

II MS contracts are internal event contracts only.

| Contract | Direction | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `IntentValidatedEvent` | Inbound | `intent-controller-ms` | `intent-intelligence-ms` | Tells II MS that IC MS admitted a runtime Intent syntactically. |
| `IntentRejectedEvent` | Outbound | `intent-intelligence-ms` | `intent-controller-ms` | Tells IC MS that the admitted intent is semantically/policy/capability rejected. |
| `IntentResolvedEvent` | Optional outbound | `intent-intelligence-ms` | Optional observability and audit consumers | Observability and audit milestone for candidate-level semantic resolution. |
| `IntentNetworkReadyEvent` | Outbound | `intent-intelligence-ms` | `intent-assurance-ms` | Service-ready change-execution and observation configuration handoff. |
| `OptimisationStatusChangeEvent` | Inbound internal Kafka event | ICB MS | `intent-intelligence-ms` | Optimiser outcome event ingested by ICB MS and relayed to Kafka for a previously submitted `POST /optimisation` request. |

II MS has no external TMF-compliant REST contract in the active baseline. Any health, readiness, or metrics endpoints are internal platform probes only and must not be treated as product APIs.

For optimiser-backed selection, II MS registers or supplies the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, to the Optimiser platform when submitting `POST /optimisation`. The Optimiser platform sends `OptimisationStatusChangeEvent` to ICB MS. ICB MS performs callback ingestion and places `OptimisationStatusChangeEvent` on Kafka for II MS to consume.

II MS workflow events remain internal Kafka event contracts. The exact ICB optimiser-callback ingestion and relay contract must be confirmed during ICB MS refinement.

## 8. Event delivery path:

II MS has one event-delivery model in the active baseline: internal Kafka event processing. It consumes `IntentValidatedEvent` from IC MS and, for optimisation-backed selection, consumes `OptimisationStatusChangeEvent` from Kafka after ICB MS callback ingestion. II MS publishes II-owned milestone events through the II internal outbox relay to Kafka.

These events use CloudEvents-style Kafka/platform headers and JSON bodies. External optimiser callback ingestion is handled by ICB MS and then relayed to Kafka for II MS consumption.

## 9. Inbound internal Kafka event shape:

### 9.1. IntentValidatedEvent:

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

### 9.2. OptimisationStatusChangeEvent:

For optimisation-backed selection, II MS consumes `OptimisationStatusChangeEvent` from Kafka after ICB MS has ingested the external optimiser callback. The event uses CloudEvents-style Kafka/platform headers and a plain JSON body.

```http
ce-specversion: 1.0
ce-type: OptimisationStatusChangeEvent
ce-source: intent-callback-ms
ce-id: evt-optimisation-status-001
ce-time: 2026-04-18T12:03:30+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

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

## 10. Field specification:

| Field | Requirement | Notes |
|---|---|---|
| `body.intentId` | Required | Runtime Intent identity admitted by IC MS. |
| `body.intentVersion` | Required where runtime intent versioning is used | Used to prevent stale event decisions overriding newer versions. |
| `body.lifecycleStatus` | Required | Expected to reflect IC MS admission state, commonly `Acknowledged`. |
| `body.intentSpecification.id` | Required | Active specification used by IC MS admission validation. |
| `body.expression.iri` | Required | Semantic/expression contract admitted by IC MS and checked against the selected specification. |
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

## 11. Fields not accepted:

II MS should reject or ignore unexpected fields according to its schema and compatibility policy. It must not re-resolve the governing `IntentSpecification` by IRI alone; `intentSpecification.id` and `expression.iri` are carried-forward admission facts from IC MS. The following fields are not part of the II MS baseline contract:

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

## 12. Authorisation:

II MS is internal only.

It is not exposed through NGW, OEX, public API gateways, partner channels, or external TMF APIs.

Security and authorisation rules:

- Consume only from trusted internal Kafka topics and trusted platform identities.
- Use workload identity for Knowledge Plane access.
- Use service-to-service identity and platform network policy for internal calls.
- Do not perform external end-user authorisation in II MS.
- Do not rely on downstream user context; II MS receives internal event facts, not external user claims.
- Restrict health, readiness, and metrics probes to the platform/runtime network plane.
- Audit semantic and policy rejections where required.
- Do not emit secrets, credentials, or sensitive internal implementation details in events.

## 13. Persistence / state / outbox model:

II MS should use source-of-truth persistence for semantic resolution state and reliable event publication.

A PostgreSQL-compatible relational store is suitable because II MS needs transactional state transitions, idempotency, auditability, and reliable outbox behaviour.

Suggested tables:

| Table | Purpose |
|---|---|
| `intent_resolution_state` | Current semantic resolution state per `intentId` and runtime version. |
| `intent_resolution_idempotency` | Consumed event deduplication keyed by CloudEvents id and/or intent/version identity. |
| `intent_optimisation_correlation` | Tracks II-submitted optimisation requests, optimisation id, intentId, intentVersion, correlationId, ICB callback submission target reference where applicable, optimiser outcome state, and correlation of ICB-relayed `OptimisationStatusChangeEvent` outcomes back to the originating `POST /optimisation` request. |
| `intent_optimisation_api_outbox` | Durable API outbox for II-submitted `POST /optimisation` requests, including request body, idempotency key, callback submission URL, request status, retry count, next retry time, accepted optimisation id, and error/failure state. |
| `intent_resolution_audit` | Decision audit for KP lookup, policy validation, semantic rejection, and resolution outcomes. |
| `intent_resolution_outbox` | Reliable publication queue for `IntentRejectedEvent`, `IntentResolvedEvent`, and `IntentNetworkReadyEvent`. |
| `intent_resolution_dead_letter` | Required minimum failed/unprocessable event handling for exhausted `IntentValidatedEvent` and `OptimisationStatusChangeEvent` processing, including event id, event type, intentId, intentVersion where available, failure reason, retry count, payload hash, and replay/operational status. |
| `shedlock` | Optional clustered outbox relay coordination. |

The processing transaction should persist the semantic decision and enqueue the output event atomically. The relay publishes from the event outbox and records publication state separately from decision ownership. For optimisation-backed selection, the same decision transaction must also create or update the optimisation correlation record and pending optimisation API outbox entry before any `POST /optimisation` attempt is made.

## 14. Internal Kafka publication:

II MS publishes internal platform events through the internal outbox relay to Kafka. Event delivery is at-least-once. Consumers must be idempotent.

Publication rules:

- Publish only after the semantic decision is durably recorded.
- Use a stable event id for deduplication.
- Include `correlationId` and `intentId` in the body for traceability.
- Preserve CloudEvents headers consistently across event types.
- Do not publish partially constructed milestone events.
- Retry transient Kafka publication failures through the outbox relay.
- Treat exhausted publication retries as an operational failure requiring support handling.

## 15. Internal Kafka topics:

| Topic | Event types | Direction for II MS |
|---|---|---|
| `t7.intent.management.events` | `IntentValidatedEvent`, `OptimisationStatusChangeEvent`, `IntentRejectedEvent`, `IntentResolvedEvent`, `IntentNetworkReadyEvent` | Consume admitted intent and optimiser outcome events; publish II-owned workflow events. |

The shared topic is the current baseline; event type and `ce-source` provide ownership boundaries. Future topic splitting may be introduced without changing II MS event payload contracts.

A future split into more granular topics can be introduced if throughput, retention, or ownership boundaries require it, but the baseline uses the shared internal intent-management events topic.

## 16. Event identity:

CloudEvents identity must be stable and suitable for deduplication.

| Field | Rule |
|---|---|
| `ce-id` | Globally unique event id. Stable for the same event publication attempt. |
| `ce-source` | `intent-intelligence-ms` for II-owned outbound events; `intent-callback-ms` for ICB-relayed `OptimisationStatusChangeEvent` consumed by II MS. |
| `ce-type` | One of `IntentValidatedEvent`, `OptimisationStatusChangeEvent`, `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent`, depending on direction and producer. |
| `ce-subject` | Runtime `intentId`. |
| `ce-time` | Event creation time. |
| `body.intentId` | Same runtime intent identity as `ce-subject`. |
| `body.intentVersion` | Runtime intent version when versioning is used. |
| `body.references.correlationId` | End-to-end trace/correlation id. |

## 17. Internal Kafka CloudEvents headers:

Example inbound headers for `OptimisationStatusChangeEvent` consumed by II MS after ICB MS relay:

```http
ce-specversion: 1.0
ce-type: OptimisationStatusChangeEvent
ce-source: intent-callback-ms
ce-id: evt-optimisation-status-001
ce-time: 2026-04-18T12:03:30+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

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

## 18. Internal Kafka message body: IntentRejectedEvent:

`IntentRejectedEvent` is emitted when semantic, policy, capability, or processing validation fails after IC MS syntactic admission.

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

## 19. Internal Kafka message body: IntentResolvedEvent:

`IntentResolvedEvent` is the candidate-level semantic-resolution handoff. It carries canonical context and all valid and applicable candidate resources known for the resolved context after scope and policy filtering. It is not the final selected or applied resource set.

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
        ],
        "metrics": {
          "latencyMs": 7,
          "availabilityPercent": 99.996,
          "jitterMs": 1.1,
          "packetLossPercent": 0.004
        }
      },
      {
        "resourceId": "SYD-PRI-02",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
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
        "accessTechnology": "fibre",
        "relationships": [
          {
            "type": "protects",
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
    ],
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

Rules:

- Preserve `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences`.
- Do not flatten location, service type, service class, priority, redundancy, or preference fields into unrelated top-level event fields.
- `resources[]` is the full valid candidate set for the resolved context, not the final selected or applied resource set.
- Resource metrics use neutral metric names such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.
- Do not use context-encoded metric wrappers such as `metrics.benchmark` or `metrics.telemetry` in the baseline message shape.
- Do not include `provider` by default.

## 20. Internal Kafka message body: IntentNetworkReadyEvent:

`IntentNetworkReadyEvent` is the service-ready preparation handoff to IA MS. It carries the service configuration required for change execution and assurance observation. It does not mean network apply succeeded.

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

Rules:

- `IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`.
- IA MS consumes `IntentNetworkReadyEvent`; IA MS must not produce it.
- Use `serviceConfiguration.orchestratorConfiguration` for selected apply and change-execution details.
- Use `serviceConfiguration.observerConfiguration` for assurance/monitoring details.
- `serviceConfiguration.orchestratorConfiguration.resources[]` carries the selected apply and change-execution resources, including resource details, topology, roles, and change-execution-relevant information.
- `serviceConfiguration.orchestratorConfiguration.resources[]` must not carry observed metric values.
- `serviceConfiguration.observerConfiguration.resources[]` carries the assurance observation scope and uses `metrics` as a list of metric names IA MS should observe, not a value object.
- Do not include `applyOutcome`.
- Do not treat this event as proof that network apply succeeded.

## 21. Behaviour:

### 21.1. Successful semantic resolution:

When an admitted intent can be semantically interpreted and candidate resources are known, II MS may emit `IntentResolvedEvent` as an optional observability and audit milestone. Optimisation is invoked separately through the direct `POST /optimisation` API outbox path.

### 21.2. Semantic rejection:

When an admitted intent is syntactically valid but cannot be semantically, policy, or capability resolved, II MS emits `IntentRejectedEvent`. Rejection reason codes must be intent-domain reason codes and must not leak downstream implementation vocabulary.

### 21.3. Service-ready preparation:

When the service configuration required for change execution and assurance observation is prepared, II MS emits `IntentNetworkReadyEvent`.

IntentNetworkReadyEvent may be emitted only after II MS has received or derived a governed selected configuration from the authorised downstream selection or optimisation path. II MS does not own the optimisation algorithm or optimiser backend. II MS owns packaging the selected configuration into the service-ready event for IA MS.

This event carries `serviceConfiguration.orchestratorConfiguration` and `serviceConfiguration.observerConfiguration`.

For optimisation-backed selection, II MS emits `IntentNetworkReadyEvent` only after the approved Optimiser path returns a complete, correlated, current selected configuration through ICB-relayed `OptimisationStatusChangeEvent`. If `POST /optimisation` fails, the optimiser outcome is `FAILED` or `INFEASIBLE`, the callback is missing beyond the configured deadline, or the outcome is stale for the current runtime version, II MS must not emit `IntentNetworkReadyEvent`; it records the outcome in correlation state and follows governed retry, timeout, failure, or rejection policy.

### 21.4. Idempotency:

II MS must support at-least-once delivery. It deduplicates consumed events by CloudEvents id and runtime intent identity, and avoids duplicate output milestone events for the same input event and semantic decision.

II MS also deduplicates consumed `OptimisationStatusChangeEvent` instances by CloudEvents id, optimisation id, event type, and intent/version identity where available, and must not publish duplicate `IntentNetworkReadyEvent` outcomes for duplicate optimiser status events. A stale optimiser outcome for a superseded, cancelled, or no-longer-current runtime version must be ignored or recorded for audit and must not overwrite current semantic or service-ready state.

### 21.5. Ordering:

II MS must not allow stale events for older runtime intent versions to overwrite newer semantic resolution state.

Where runtime versioning is active, state transitions are keyed by `intentId` and version.

### 21.6. Dependency failure:

| Dependency | Behaviour |
|---|---|
| II database unavailable | Do not acknowledge/process beyond retry and dead-letter policy. |
| Knowledge Plane unavailable or stale | Fail closed for semantic resolution or service-ready packaging when fresh KP facts are required; refresh, retry, or dead-letter according to policy. |
| Kafka unavailable | Persist to outbox and retry through relay. |
| Cache unavailable | Bypass cache and use KP or the relevant approved pre-resolution validation source where safe. |
| Optimisation API outbox unavailable | Prevents outbound `POST /optimisation` submission for optimisation-backed selection. II MS keeps the optimisation request pending and must not emit `IntentNetworkReadyEvent` until the API outbox worker successfully submits the request and the correlated optimiser outcome is received through ICB MS and Kafka. |
| Optimiser / ICB optimiser callback path unavailable | Not a dependency for semantic resolution or `IntentResolvedEvent` emission. For optimisation-backed selection, `POST /optimisation` failure from the API outbox worker, missing optimiser callback through ICB MS, or missing `OptimisationStatusChangeEvent` from Kafka prevents `IntentNetworkReadyEvent` emission until configured retry, callback timeout, governed failure/rejection policy, or operational handling applies. |
| IA MS unavailable | Not a synchronous dependency; `IntentNetworkReadyEvent` remains the handoff. |

## 22. Configuration:

II MS configuration should be environment-specific and externally supplied through platform configuration mechanisms.

Suggested configuration areas:

| Configuration area | Examples |
|---|---|
| Kafka topics | Internal intent-management event topic names and consumer group id. |
| Outbox relay | Batch size, retry backoff, maximum retry count, relay lock settings for internal event publication. |
| Optimisation API outbox | Request submission retry backoff, maximum retry count, idempotency-key policy, circuit-breaker settings, callback wait timeout, and accepted-response handling for `POST /optimisation`. |
| KP, optimiser, and pre-resolution validation access | KP endpoint, `POST /optimisation` endpoint, ICB-owned callback submission URL registered with the Optimiser platform, approved T7 or governed source endpoints where required, timeout, cache TTL, circuit-breaker settings. |
| Semantic rules | Supported service types, service classes, target names, constraint names, and policy rule versions. |
| Rejection mapping | Reason-code mapping and user/projectable `statusReason` templates. |
| Observability | Log levels, metrics enablement, trace sampling. |
| Dead-letter handling | DLQ topic/table settings and operational alert thresholds. |

Configuration must not introduce per-environment contract drift. Contract field names and event meaning remain stable across environments.

## 23. Consumer contract:

Consumers of II-owned events must treat the event stream as at-least-once.

Consumer rules:

- Deduplicate by `ce-id` and/or `body.intentId` plus version and milestone type.
- Treat `IntentResolvedEvent.resources[]` as the full valid candidate set for observability, audit, replay, or future consumers, not final selected or applied output.
- Treat `IntentNetworkReadyEvent` as service-ready preparation only, not apply success.
- Do not infer assurance status from II events.
- Use `body.references.correlationId` for traceability.
- Preserve the canonical `body.expression.context.targets`, `body.expression.context.constraints`, and `body.expression.context.preferences` grouping when forwarding or deriving downstream state.
- Ignore or safely discard stale outcomes for superseded or cancelled runtime intent versions; consumers must not infer current state from stale optimiser outcomes.

## 24. Open items:

| Item | Status |
|---|---|
| Finalise implementation-level details for the approved Optimiser integration path: II MS submits `POST /optimisation`, registers or supplies the ICB-owned callback submission URL, and consumes ICB-relayed `OptimisationStatusChangeEvent` from Kafka. | Open implementation detail. |
| Finalise exact KP lookup, freshness, cache, and invalidation policy values per environment. | Open implementation detail. |
| Finalise DLQ operational runbook, replay controls, and poison-event retention policy. | Open implementation detail. |
| Confirm whether future topic split is needed for `IntentResolvedEvent` and `IntentNetworkReadyEvent` as volume grows. | Open scalability decision. |

## 25. Closed items:

| Item | Decision |
|---|---|
| II MS is internal only. | Closed. No external TMF-compliant API. |
| II MS consumes `IntentValidatedEvent`. | Closed. |
| II MS emits `IntentRejectedEvent`. | Closed. |
| II MS may emit `IntentResolvedEvent` as an optional observability and audit milestone. | Closed. |
| II MS owns and emits `IntentNetworkReadyEvent`. | Closed. |
| IA MS consumes but does not produce `IntentNetworkReadyEvent`. | Closed. |
| `IntentResolvedEvent` resources are candidates, not selected or applied resources. | Closed. |
| `IntentNetworkReadyEvent` does not mean apply success. | Closed. |
| Canonical buckets are `targets`, `constraints`, and `preferences`. | Closed. |
| `availabilityPercent` is the standard availability metric name. | Closed. |

## 26. MS identity:

| Attribute | Value |
|---|---|
| Full name | Intent Intelligence MS |
| Short name | II MS |
| Service name | `intent-intelligence-ms` |
| Domain | Intent Domain |
| External API | None |
| Primary input events | `IntentValidatedEvent`; `OptimisationStatusChangeEvent` after ICB MS callback ingestion |
| Output events | `IntentRejectedEvent`, `IntentResolvedEvent`, `IntentNetworkReadyEvent` |
| Primary persistence | PostgreSQL / PostgreSQL-compatible RDBMS |
| Event style | Internal Kafka events with CloudEvents-style Kafka/platform headers and plain JSON `body` |
| Public exposure | None |
