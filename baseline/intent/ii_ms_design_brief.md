# II MS Design Brief

## Purpose

Intent Intelligence MS, referred to as II MS, owns semantic interpretation, Knowledge Plane-backed validation, and semantic/service-ready preparation for admitted runtime intents.

II MS receives syntactically admitted intent facts from IC MS, interprets and validates them against Knowledge Plane/domain knowledge, and emits one of the II-owned internal outcome events:

- `IntentRejectedEvent` for semantic, policy, or capability rejection
- `IntentResolvedEvent` for candidate-level semantic resolution
- `IntentNetworkReadyEvent` for service-ready preparation to IA MS

II MS is internal only. It does not expose a TMF-facing REST API and is not exposed through NGW, OEX, public API gateways, or partner-facing API channels.

## Service identity

| Attribute | Value |
|---|---|
| Display name | Intent Intelligence MS |
| Service name | `intent-intelligence-ms` |
| Short name | II MS |
| Domain | Intent Domain |
| Main responsibility | Semantic interpretation, Knowledge Plane-backed validation, canonical resolution, and service-ready preparation |
| Primary event input | `IntentValidatedEvent` |
| Main event outputs | `IntentRejectedEvent`, `IntentResolvedEvent`, `IntentNetworkReadyEvent` |
| Event style | Internal CloudEvents headers with plain JSON `body` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| External TMF API owner | No |

## Core responsibility

II MS answers this question:

```text
Can this admitted intent be semantically understood, resolved into a canonical candidate-level handoff, and, where applicable, prepared into a service-ready configuration for IA MS?
```

II MS does this after IC MS has already performed syntactic admission validation.

II MS owns:

| Responsibility | Detail |
|---|---|
| Semantic interpretation | Interprets the admitted expression from `IntentValidatedEvent` |
| KP-backed validation | Uses Knowledge Plane data to validate location, service, service class, capability, policy, and resource availability |
| Canonicalisation | Normalises admitted values into canonical internal location, service, target, constraint, preference, and resource terms |
| Rejection decision | Emits `IntentRejectedEvent` when semantic/policy/capability validation fails |
| Resolution decision | Emits `IntentResolvedEvent` when the intent can be handed to the next internal fulfilment stage as a candidate-level semantic-resolution handoff |
| Service-ready preparation | Emits `IntentNetworkReadyEvent` when orchestration and observation configuration has been prepared for IA MS |
| Candidate resource handoff | Provides the full valid resource set known for the resolved context after scope/policy filtering |
| Outbox publication | Publishes II-owned events reliably through the II outbox |
| Idempotency | Deduplicates consumed events and avoids duplicate semantic outcomes |
| Audit | Records semantic interpretation, KP lookup, rejection, resolution, and service-ready preparation decisions where required |

## II MS does not own

| Concern | Owner |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| Runtime `Intent` REST API | IC MS |
| Runtime `IntentReport` REST API | IC MS |
| External TMF lifecycle/status projection | IC MS |
| External event subscriptions | IC MS / ID MS depending on resource |
| Downstream optimisation selection | `optimiser-controller-ms` |
| Optimiser backend / solver target | `t7-gurobi-optimiser` where selected by KP or optimiser configuration |
| Assurance/apply/runtime truth | IA MS |
| Callback ingestion | ICB MS |
| Raw network apply/orchestration execution | Orchestration layer / network orchestrator |
| KP config CRUD/governance | Knowledge Plane operating model |
| OEX user experience | OEX layer |

## Main input

II MS consumes `IntentValidatedEvent` from the internal event backbone.

`IntentValidatedEvent` contains the admitted runtime expression in native internal JSON form. IC MS has already translated the external TMF-facing `Intent.expression.expressionValue` into internal event form.

II MS expects the admitted expression to preserve the canonical ID/IC semantic grouping:

```text
expression.context.targets
expression.context.constraints
expression.context.preferences
```

Domain inputs such as `location`, `serviceType`, and `serviceClass` are carried under `expression.context.constraints`.

## Main outputs

| Output | Condition | Purpose |
|---|---|---|
| `IntentRejectedEvent` | Semantic, policy, or capability validation fails | Tells IC MS the admitted intent must be externally projected as rejected |
| `IntentResolvedEvent` | Semantic/capability resolution succeeds and downstream fulfilment/selection is required | Provides candidate-level canonical context and the valid resource set for downstream consideration, including all applicable/applyable resources and neutral metric values |
| `IntentNetworkReadyEvent` | Service-ready preparation succeeds after resolution | Provides IA MS with prepared orchestration and observation configuration; it does not mean apply succeeded |

## Processing stages

| Stage | Description |
|---|---|
| Consume | Consume `IntentValidatedEvent` from the internal event backbone |
| Idempotency | Deduplicate by CloudEvents `ce-id` / event id and `intentId` |
| Semantic parse | Interpret `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences` |
| KP lookup | Resolve location/service capability from Knowledge Plane |
| Capability validation | Confirm requested service/service class is available for the requested location |
| Policy validation | Validate hard constraints such as priority and redundancy against KP/domain policy |
| Canonicalisation | Normalise values into canonical internal terms |
| Resource discovery | Resolve available KP resources for the resolved domain context |
| Outcome selection | Emit `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` depending on the resolved milestone |
| Durable publication | Write event to II outbox and publish through relay |
| Audit | Record semantic/KP decision trail where required |

## Semantic bucket handling

II MS preserves the canonical semantic bucket model.

| Bucket | II MS treatment |
|---|---|
| `context.targets` | Validates supported measurable runtime objectives and carries them forward unchanged or canonically normalised |
| `context.constraints` | Validates hard requirements such as `location`, `serviceType`, `serviceClass`, `priority`, `redundancyRequired`, and `timeWindow` |
| `context.preferences` | Preserves soft selection guidance such as `preferredAccessTechnology` for downstream selection guidance |

II MS must not flatten the buckets into unrelated top-level fields in `IntentResolvedEvent` or `IntentNetworkReadyEvent`.

II MS may normalise values only where the semantic meaning is preserved and traceable.

## Knowledge Plane usage

II MS uses the Knowledge Plane as governed domain knowledge.

| KP area | II MS use |
|---|---|
| `locationBasedServices` | Resolve location/service availability and display labels |
| `capabilityStatus` | Decide available vs unknown/unavailable capability |
| `benchmarks` | Understand service capability baseline and service/location target thresholds |
| `resourceIds` | Discover candidate resources for downstream handoff |
| `resources` | Build valid resource entries for downstream consideration |
| `expressionMapping` | Resolve aliases/human expressions where applicable |
| `redundancyAvailable` | Validate redundancy requirements |
| logical target references | Resolve downstream target names where needed by downstream events |

II MS must not dump raw KP into events. It curates only the information required by the next stage.

`provider` remains KP/resource-inventory metadata only and is not included by default in event-facing resource entries.

KP remains a native knowledge/config source. KP may retain `metrics.benchmark.*` for resource reference/capability values, `benchmarks.*` for service/location target thresholds, and `t7-gurobi-optimiser` as the optimiser backend/solver target. II maps KP resource metric values into neutral event-facing `metrics` fields such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.

## Resource and metric vocabulary

II MS uses the shared event-facing resource vocabulary when emitting events:

| Concept | Event-facing baseline |
|---|---|
| Resource type | `deliveryResource` |
| Resource class | `critical-gold` |
| Resource roles | `roles`, using values such as `primary` and `secondary` |
| Resource metric values | `metrics.latencyMs`, `metrics.availabilityPercent`, `metrics.jitterMs`, `metrics.packetLossPercent` |

Event-facing metric fields must not encode origin or pipeline context into wrappers or field names. Do not use `metrics.benchmark`, `metrics.telemetry`, `latencyBenchmarkMs`, or `currentLatencyMs` in II event payloads. The event type and processing stage provide the meaning of the metric values.

## Resolution rule

II MS emits `IntentResolvedEvent` only when the admitted intent can be semantically understood and resolved into a candidate-level canonical context.

A successful resolution implies:

- the location can be resolved
- the requested service type and service class are understood
- the requested service is available or supported for the resolved location
- hard constraints are semantically valid
- the resource set is known and valid for downstream consideration after scope/policy filtering
- the intent can proceed to the next internal fulfilment/preparation stage

`IntentResolvedEvent.resources[]` contains the full valid/applicable/applyable resource set known in KP for the resolved context after applicable scope/policy filtering. It includes neutral event-facing metric values for those resources so `optimiser-controller-ms` can compare and select the best applicable configuration.

`IntentResolvedEvent.resources[]` is not the final selected/applied resource set and it is not the service-ready/apply-ready handoff.

## Service-ready preparation rule

II MS emits `IntentNetworkReadyEvent` when service-ready preparation has produced the concrete orchestration and observation configuration required by IA MS.

`IntentNetworkReadyEvent`:

- is produced by `intent-intelligence-ms`
- is consumed by `intent-assurance-ms`
- carries the resolved runtime `body.context`
- carries selected apply/orchestration details under `serviceConfiguration.orchestratorConfiguration`
- carries assurance/monitoring details under `serviceConfiguration.observerConfiguration`
- does not mean network apply has succeeded
- is not a substitute for `IntentAssuranceEvent`

IA MS consumes this event and must not produce it.

`IntentNetworkReadyEvent.serviceConfiguration.orchestratorConfiguration.resources[]` contains only the selected apply configuration chosen after optimisation/selection, not the full applicable candidate set.

`IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[]` contains the full assurance observation scope that IA MS must observe. Each observer resource uses `metrics` as a list of metric names to observe, not as metric values. Do not introduce a separate `observationPoints` attribute.

## Rejection rule

II MS emits `IntentRejectedEvent` when the admitted intent is syntactically valid but cannot be semantically/policy/capability resolved.

II MS reason codes are intent-domain reason codes. They must not leak downstream implementation or selection vocabulary.

Typical rejection reasons include:

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

## Lifecycle projection relationship with IC MS

II MS does not own the external `Intent.lifecycleStatus` resource API.

II MS emits lifecycle-driving internal facts:

| II outcome | IC MS typical projection |
|---|---|
| `IntentRejectedEvent.lifecycleStatus = Rejected` | `Intent.lifecycleStatus = Rejected` |
| `IntentResolvedEvent.lifecycleStatus = InProgress` | `Intent.lifecycleStatus = InProgress` while downstream fulfilment/preparation continues |
| `IntentNetworkReadyEvent.lifecycleStatus = InProgress` | `Intent.lifecycleStatus = InProgress` while apply/assurance continues |

IC MS owns the external projection and external TMF event publication.

## Internal event style

II MS emits internal events using:

| Area | Baseline |
|---|---|
| Transport metadata | CloudEvents headers |
| Body wrapper | Top-level `body` |
| Payload style | Plain internal JSON |
| External TMF shape | Not used internally |
| Correlation | `correlationId` propagated in body references and logs |
| Kafka key | Prefer `intentId` |

Internal II events do not use the TMF external `Intent.expression` wrapper, but they do preserve the native `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences` grouping.

## API stance

II MS has no external TMF-facing API and no consumer-facing REST contract. It is not exposed through NGW, OEX, public API gateways, or partner-facing API channels.

Operational probes such as `/health`, `/ready`, and `/metrics`, if implemented, are platform-internal only. They are for Kubernetes/platform operations and must not be presented as TMF921 resource APIs or externally exposed service APIs.

Any future operational/admin endpoint must be platform-internal only and must not be presented as a TMF921 resource API.

## Persistence baseline

II MS follows the active IME DB baseline.

| Concern | Baseline |
|---|---|
| DB type | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| DB ownership | Dedicated II MS DB instance or logical managed DB boundary |
| Shared cross-MS DB | Not allowed |
| Schema migration | Flyway or Liquibase |
| Manual schema change | Not permitted |
| Future DR | Cross-region active-passive DR path required |

Indicative tables:

| Table | Purpose |
|---|---|
| `intent_resolution_state` | Current semantic resolution state per intent |
| `intent_resolution_idempotency` | Deduplication/idempotency tracking for consumed events |
| `intent_resolution_audit` | Semantic/KP lookup decisions and rejection reasons |
| `intent_resolution_outbox` | Reliable publication of II-owned events |
| `intent_resolution_dead_letter` | Optional failed/unprocessable event handling |
| `shedlock` | Relay coordination if II MS runs a clustered outbox relay |

## Dependency and circuit-breaker behaviour

| Dependency | Behaviour |
|---|---|
| II MS DB unavailable | Hard fail processing; do not acknowledge event until retry/dead-letter policy applies |
| KP unavailable | Fail closed for semantic resolution; retry or dead-letter according to operational policy |
| Kafka/event broker unavailable | Consumed event state must not be lost; II outbox relay retries publication |
| Cache unavailable | Bypass cache and use KP/source where safe |
| Downstream fulfilment/preparation stage unavailable | Not an external caller concern; II emits only the milestone it has actually reached |

## Security baseline

II MS is internal only.

Security baseline:

- consume only from trusted internal event topics
- use workload identity for KP access
- expose no public, NGW, OEX, partner, or consumer-facing REST API
- restrict operational probes to the internal runtime/network plane
- no external user/business authorisation in II MS
- no secrets, tokens, credentials, or raw internal stack traces in event payloads
- no raw KP credentials or endpoint details in logs/events
- audit semantic rejection and policy rejection decisions where required

## Observability baseline

II MS must emit:

- structured logs with `correlationId` and `intentId`
- semantic rejection counters
- KP lookup latency/error metrics
- idempotency duplicate counters
- outbox pending/publish failure metrics
- event consumption lag
- distributed traces

Recommended metrics:

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

## Design baseline statement

II MS is the internal semantic interpretation, resolution, and service-ready preparation service.

It consumes `IntentValidatedEvent`, validates and resolves the admitted expression using Knowledge Plane/domain knowledge, preserves the canonical `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences` buckets, and emits `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` depending on the resolved milestone.

II MS emits neutral event-facing resource and metric structures. `IntentResolvedEvent.resources[]` carries the full applicable/applyable resource set with metric values for downstream optimisation/selection. `IntentNetworkReadyEvent.orchestratorConfiguration.resources[]` carries only the selected apply configuration, while `observerConfiguration.resources[]` carries the full IA observation scope with metric names to observe.

II MS does not own external TMF APIs, runtime Intent lifecycle projection, downstream apply execution, assurance truth, callback ingestion, or KP governance.
