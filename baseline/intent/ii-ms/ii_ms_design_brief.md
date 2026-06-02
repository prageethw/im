# II MS Design Brief

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Scope | Intent Intelligence MS design brief |
| Source of truth after commit | GitHub `baseline/intent/ii-ms/ii_ms_design_brief.md` |

## Table of contents:

- [1. Purpose](#1-purpose)
- [2. Service identity](#2-service-identity)
- [3. Core responsibility](#3-core-responsibility)
- [4. II MS does not own](#4-ii-ms-does-not-own)
- [5. Main input](#5-main-input)
- [6. Main outputs](#6-main-outputs)
- [7. Processing stages](#7-processing-stages)
- [8. Semantic bucket handling](#8-semantic-bucket-handling)
- [9. Knowledge Plane usage](#9-knowledge-plane-usage)
  - [9.1. Required pre-resolution validation](#91-required-pre-resolution-validation)
- [10. Resource and metric vocabulary](#10-resource-and-metric-vocabulary)
- [11. Resolution rule](#11-resolution-rule)
- [12. Service-ready preparation rule](#12-service-ready-preparation-rule)
- [13. Rejection rule](#13-rejection-rule)
- [14. Lifecycle projection relationship with IC MS](#14-lifecycle-projection-relationship-with-ic-ms)
- [15. Internal event style](#15-internal-event-style)
- [16. API stance](#16-api-stance)
- [17. Persistence baseline](#17-persistence-baseline)
- [18. Dependency and circuit-breaker behaviour](#18-dependency-and-circuit-breaker-behaviour)
- [19. Security baseline](#19-security-baseline)
- [20. Observability baseline](#20-observability-baseline)
- [21. Design baseline statement](#21-design-baseline-statement)


## 1. Purpose

Intent Intelligence MS, referred to as II MS, owns semantic interpretation, Knowledge Plane-backed validation and required pre-resolution validation, and semantic/service-ready preparation for admitted runtime intents.

II MS receives syntactically admitted intent facts from IC MS, interprets and validates them against Knowledge Plane data, domain knowledge, and any additional pre-resolution validation sources required by the use case, and emits one of the II-owned internal outcome events:

- `IntentRejectedEvent` for semantic, policy, or capability rejection
- `IntentResolvedEvent` for candidate-level semantic resolution
- `IntentNetworkReadyEvent` for service-ready preparation to IA MS

II MS is internal only.

It does not expose a TMF-compliant REST API and is not exposed through NGW, OEX, public API gateways, or partner-facing API channels.

## 2. Service identity

| Attribute | Value |
|---|---|
| Display name | Intent Intelligence MS |
| Service name | `intent-intelligence-ms` |
| Short name | II MS |
| Domain | Intent Domain |
| Main responsibility | Semantic interpretation, Knowledge Plane-backed validation and required pre-resolution validation, canonical resolution, and service-ready preparation |
| Primary event inputs | `IntentValidatedEvent`; `OptimisationStatusChangeEvent` after ICB MS callback ingestion |
| Main event outputs | `IntentRejectedEvent`, `IntentResolvedEvent`, `IntentNetworkReadyEvent` |
| Event style | Internal CloudEvents headers with plain JSON `body` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| External TMF API owner | No |

## 3. Core responsibility

II MS answers this question:

```text
Can this admitted intent be semantically understood, resolved into a canonical candidate-level handoff, and, where applicable, prepared into a service-ready configuration for IA MS?
```

II MS does this after IC MS has already performed syntactic admission validation.

II MS owns:

| Responsibility | Detail |
|---|---|
| Semantic interpretation | Interprets the admitted expression from `IntentValidatedEvent` |
| KP-backed and required pre-resolution validation | Uses Knowledge Plane data and, where required, approved T7 services or other governed sources to validate location, service, service class, capability, policy, resource availability, and other use-case-specific facts needed before resolution |
| Canonicalisation | Normalises admitted values into canonical internal location, service, target, constraint, preference, and resource terms |
| Rejection decision | Emits `IntentRejectedEvent` when semantic/policy/capability validation fails |
| Resolution observability milestone | May emit `IntentResolvedEvent` after candidate-level semantic resolution for observability, audit, replay, or future consumers. It is not the optimiser trigger and has no mandatory consumer in the active baseline. |
| Service-ready preparation | Emits `IntentNetworkReadyEvent` when change-execution and observation configuration has been prepared for IA MS |
| Candidate resource handoff | Provides the full valid resource set known for the resolved context after scope/policy filtering |
| Outbox publication | Publishes II-owned events reliably through the II outbox |
| Idempotency | Deduplicates consumed events and avoids duplicate semantic outcomes |
| Audit | Records semantic interpretation, KP lookup, rejection, resolution, and service-ready preparation decisions where required |

## 4. II MS does not own

| Concern | Owner |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| Runtime `Intent` REST API | IC MS |
| Runtime `IntentReport` REST API | IC MS |
| External TMF lifecycle/status projection | IC MS |
| External event subscriptions | IC MS / ID MS depending on resource |
| Downstream optimisation selection | Optimiser platform / optimiser domain |
| Optimiser backend / solver target | `t7-gurobi-optimiser` where selected by KP or optimiser configuration |
| Assurance/apply/runtime truth | IA MS |
| Callback ingestion | ICB MS |
| Raw network apply / change execution | Change execution layer / network orchestrator |
| KP config CRUD/governance | Knowledge Plane operating model |
| OEX user experience | OEX layer |

## 5. Main input

II MS consumes `IntentValidatedEvent` from the internal event backbone. For optimisation-backed selection, II MS also consumes `OptimisationStatusChangeEvent` from Kafka after ICB MS has ingested the external optimiser callback and relayed the event internally.

`IntentValidatedEvent` contains the admitted runtime expression in native internal JSON form. IC MS has already translated the external TMF-compliant `Intent.expression.expressionValue` into internal event form.

II MS expects the admitted event to carry the admission context selected by IC MS:

| Field | II MS usage |
|---|---|
| `intentSpecification.id` | Active specification selected by IC MS for syntactic admission, governance, and traceability. |
| `expression.iri` | Semantic/expression contract identifier admitted by IC MS and checked against the selected specification. |

II MS must treat these as carried-forward admission facts. It must not re-resolve the governing `IntentSpecification` by IRI alone.

II MS expects the admitted expression to preserve the canonical ID/IC semantic grouping:

```text
expression.context.targets
expression.context.constraints
expression.context.preferences
```

Domain inputs such as `location`, `serviceType`, and `serviceClass` are carried under `expression.context.constraints`.

For optimiser outcomes, II MS expects `OptimisationStatusChangeEvent` to be published to Kafka by ICB MS with CloudEvents-style Kafka headers, including `ce-type: OptimisationStatusChangeEvent`, `ce-source: intent-callback-ms`, `ce-subject` set to the related runtime `intentId`, and a plain JSON body containing the optimiser outcome and `selectedConfiguration`.

The baseline surgical hospital slice is an illustrative runtime example used to make the II MS semantic interpretation and Knowledge Plane-backed resolution contract concrete. It is not the only supported runtime Intent type, IntentSpecification, service class, schema, expression IRI, location, service type, Knowledge Plane profile, or deployment profile. Other runtime Intents may use different targets, constraints, preferences, expression schemas, service types, priorities, resources, and governance profiles while following the same II MS contract rules.

## 6. Main outputs

| Output | Condition | Purpose |
|---|---|---|
| `IntentRejectedEvent` | Semantic, policy, or capability validation fails | Tells IC MS the admitted intent must be externally projected as rejected |
| `IntentResolvedEvent` | Semantic/capability resolution succeeds | Optional observability/audit milestone carrying candidate-level canonical context and the valid candidate resource set. It is not the optimiser trigger and has no mandatory consumer in the active baseline. |
| `IntentNetworkReadyEvent` | Service-ready preparation succeeds after resolution | Provides IA MS with prepared change-execution and observation configuration; it does not mean apply succeeded |

## 7. Processing stages

| Stage | Description |
|---|---|
| Consume | Consume `IntentValidatedEvent` from the internal event backbone. For optimisation-backed selection, also consume `OptimisationStatusChangeEvent` from Kafka after ICB MS has ingested and relayed the optimiser callback. |
| Idempotency | Deduplicate by CloudEvents `ce-id` / event id and `intentId` |
| Admission context check | Confirm the event carries `intentSpecification.id` and `expression.iri` from IC MS admission context |
| Semantic parse | Interpret `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences` |
| KP and required pre-resolution validation lookup | Resolve location, service capability, policy, and other required domain facts from Knowledge Plane and approved use-case-specific pre-resolution validation sources |
| Suitability / proceedability validation | Decide whether the admitted intent has enough trusted semantic, policy, capability, availability, freshness, and pre-resolution facts to proceed safely. If KP or approved validation sources show the intent is unsupported, contradictory, unsafe, unavailable, stale, or insufficiently validated, emit `IntentRejectedEvent` or record a governed processing failure instead of proceeding to candidate discovery or optimisation. |
| Capability validation | Confirm requested service/service class is available for the requested location |
| Policy validation | Validate hard constraints such as priority and redundancy against KP/domain policy |
| Canonicalisation | Normalise values into canonical internal terms |
| Resource discovery | Resolve available KP resources for the resolved domain context |
| Outcome selection | Emit `IntentRejectedEvent`, optionally emit `IntentResolvedEvent` for observability/audit after safe candidate-level resolution, or emit `IntentNetworkReadyEvent` only after selected service-ready configuration has been derived. |
| Durable publication | Write event to II outbox and publish through relay |
| Audit | Record semantic/KP decision trail where required |

For optimisation-backed selection, II MS also deduplicates `OptimisationStatusChangeEvent` after ICB relay and must not publish duplicate `IntentNetworkReadyEvent` outcomes for duplicate optimiser status events.

For in-flight updates or cancellation, II MS must check the current runtime intent version/state before submitting optimisation, before consuming an optimiser outcome, and before publishing any milestone event. A stale `IntentValidatedEvent` or `OptimisationStatusChangeEvent` for a superseded or cancelled runtime version must be ignored or recorded for audit, and must not produce a new `IntentNetworkReadyEvent`.

## 8. Semantic bucket handling

II MS preserves the canonical semantic bucket model.

| Bucket | II MS treatment |
|---|---|
| `context.targets` | Validates supported measurable runtime objectives and carries them forward unchanged or canonically normalised |
| `context.constraints` | Validates hard requirements such as `location`, `serviceType`, `serviceClass`, `priority`, `redundancyRequired`, and `timeWindow` |
| `context.preferences` | Preserves soft selection guidance such as `preferredAccessTechnology` for downstream selection guidance |

II MS must not flatten the buckets into unrelated top-level fields in `IntentResolvedEvent` or `IntentNetworkReadyEvent`.

II MS may normalise values only where the semantic meaning is preserved and traceable.

## 9. Knowledge Plane usage

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

II MS must not dump raw KP into events.

It curates only the information required by the next stage. `provider` remains KP/resource-inventory metadata only and is not included by default in event-facing resource entries. KP remains a native knowledge/config source. KP may retain `metrics.benchmark.*` for resource reference/capability values, `benchmarks.*` for service/location target thresholds, and `t7-gurobi-optimiser` as the optimiser backend/solver target.

II maps KP resource metric values into neutral event-facing `metrics` fields such as `latencyMs`, `availabilityPercent`, `jitterMs`, and `packetLossPercent`.

II MS must apply a configured KP freshness policy before using KP facts for safety-critical resolution. Where KP data is stale, missing, or cannot be refreshed within the configured freshness window, II MS must fail closed for the affected runtime version and use an intent-domain reason such as `KNOWLEDGE_LOOKUP_ERROR` rather than emitting an unsafe `IntentResolvedEvent` or `IntentNetworkReadyEvent`. In-flight intents must re-check the current KP snapshot/version before service-ready packaging when optimisation or callback wait time has exceeded the configured freshness threshold.

### 9.1. Required pre-resolution validation

Knowledge Plane is the primary governed knowledge source for the current hospital surgical slice baseline, but II MS must not be designed as if intent resolution can only use KP and optimiser-related inputs. Depending on the intent domain, II MS may need to perform additional pre-resolution validation required to meet the intent accurately. This validation may consult approved T7 platform services, inventory systems, policy services, catalogue services, topology services, capacity sources, fulfilment systems, or other governed domain sources.

These sources provide pre-resolution facts only; they do not own the external runtime `Intent` lifecycle. II MS remains responsible for semantic resolution, curating the returned facts, applying the II MS contract rules, and emitting the correct II-owned internal outcome event. Raw source-system payloads must not be dumped into II events. Only the validated and consumer-safe facts required by the next internal stage should be carried forward.

The active hospital surgical slice example mostly resolves from KP and optimiser-related references. Other intent types may require a wider pre-resolution validation chain while still following the same II MS event and semantic bucket rules.

## 10. Resource and metric vocabulary

II MS uses the shared event-facing resource vocabulary when emitting events:

| Concept | Event-facing baseline |
|---|---|
| Resource type | `deliveryResource` |
| Resource class | `critical-gold` |
| Resource roles | `roles`, using values such as `primary` and `secondary` |
| Resource metric values | `metrics.latencyMs`, `metrics.availabilityPercent`, `metrics.jitterMs`, `metrics.packetLossPercent` |

Event-facing metric fields must not encode origin or pipeline context into wrappers or field names.

Do not use `metrics.benchmark`, `metrics.telemetry`, `latencyBenchmarkMs`, or `currentLatencyMs` in II event payloads. The event type and processing stage provide the meaning of the metric values.

## 11. Resolution rule

II MS emits `IntentResolvedEvent` only when the admitted intent can be semantically understood and resolved into a candidate-level canonical context.

A successful resolution implies:

- the location can be resolved
- the requested service type and service class are understood
- the requested service is available or supported for the resolved location
- hard constraints are semantically valid
- the resource set is known and valid for downstream consideration after scope/policy filtering
- the intent can proceed to the next internal fulfilment/preparation stage

`IntentResolvedEvent.resources[]` contains the full valid/applicable/apply-capable resource set known in KP for the resolved context after applicable scope/policy filtering.

It includes neutral event-facing metric values for those resources so the resolved candidate set can be audited, replayed, or used by future authorised consumers. The active optimiser invocation is the direct `POST /optimisation` request submitted by II MS through its API outbox; `IntentResolvedEvent` is not the optimiser trigger. `IntentResolvedEvent.resources[]` is not the final selected/applied resource set and it is not the service-ready/apply-ready handoff.

## 12. Service-ready preparation rule

II MS emits `IntentNetworkReadyEvent` when service-ready preparation has produced the concrete change-execution and observation configuration required by IA MS.

IntentNetworkReadyEvent may be emitted only after II MS has received or derived a governed selected configuration from the authorised downstream selection or optimisation path. II MS does not own the optimisation algorithm or optimiser backend. II MS owns packaging the selected configuration into the service-ready event for IA MS.

For optimisation-backed selection, II MS submits the resolved intent context and candidate resources to the Optimiser platform using `POST /optimisation`. II MS registers or supplies the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, as the optimiser outcome target. The Optimiser platform returns the governed selected configuration by sending `OptimisationStatusChangeEvent` to ICB MS. ICB MS ingests the callback and publishes `OptimisationStatusChangeEvent` to Kafka for II MS consumption. II MS then packages that selected configuration into `IntentNetworkReadyEvent` for IA MS.

The `POST /optimisation` submission must be driven by the II MS optimisation API outbox, not by an in-memory synchronous call tied only to the `IntentValidatedEvent` consumer transaction. II MS must first persist the semantic decision, `intent_optimisation_correlation` state, and pending optimisation API outbox entry atomically. A dedicated optimisation API outbox worker submits the request, applies bounded retries and circuit-breaker behaviour, records the accepted optimisation id or failure state, and updates the correlation record. II MS must not emit `IntentNetworkReadyEvent` until the correlated `OptimisationStatusChangeEvent` is received through ICB MS and Kafka.

`IntentNetworkReadyEvent`:

- is produced by `intent-intelligence-ms`
- is consumed by `intent-assurance-ms`
- carries the resolved runtime `body.expression.context`
- carries selected apply/change-execution details under `serviceConfiguration.orchestratorConfiguration`
- carries assurance/monitoring details under `serviceConfiguration.observerConfiguration`
- does not mean network apply has succeeded
- is not a substitute for `IntentAssuranceEvent`

IA MS consumes this event and must not produce it.

`IntentNetworkReadyEvent.serviceConfiguration.orchestratorConfiguration.resources[]` contains only the selected apply configuration chosen after optimisation/selection, not the full applicable candidate set.

`IntentNetworkReadyEvent.serviceConfiguration.observerConfiguration.resources[]` contains the full assurance observation scope that IA MS must observe. Each observer resource uses `metrics` as a list of metric names to observe, not as metric values.

Do not introduce a separate `observationPoints` attribute.

## 13. Rejection rule

II MS emits `IntentRejectedEvent` when the admitted intent is syntactically valid but cannot be semantically/policy/capability resolved. II MS reason codes are intent-domain reason codes. They must not leak downstream implementation or selection vocabulary.

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

## 14. Lifecycle projection relationship with IC MS

II MS does not own the external `Intent.lifecycleStatus` resource API.

II MS emits lifecycle-driving internal facts:

| II outcome | IC MS typical projection |
|---|---|
| `IntentRejectedEvent.lifecycleStatus = Rejected` | `Intent.lifecycleStatus = Rejected` |
| `IntentResolvedEvent.lifecycleStatus = InProgress` | `Intent.lifecycleStatus = InProgress` while downstream fulfilment/preparation continues |
| `IntentNetworkReadyEvent.lifecycleStatus = InProgress` | `Intent.lifecycleStatus = InProgress` while apply/assurance continues |

IC MS owns the external projection and external TMF event publication.

## 15. Internal event style

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

## 16. API stance

II MS has no external TMF-compliant API and no consumer-facing REST contract. It is not exposed through NGW, OEX, public API gateways, or partner-facing API channels.

For optimiser-backed selection, II MS uses the ICB-owned callback ingestion path for optimiser outcome events. II MS registers or supplies the ICB submission URL to the Optimiser platform, and ICB MS publishes the received `OptimisationStatusChangeEvent` to Kafka for II MS consumption. The exact ICB ingestion and relay contract must be confirmed during ICB MS refinement.

Operational probes such as `/health`, `/ready`, and `/metrics`, if implemented, are platform-internal only. They are for Kubernetes/platform operations and must not be presented as TMF921 resource APIs or externally exposed service APIs.

Any future operational/admin endpoint must be platform-internal only and must not be presented as a TMF921 resource API.

## 17. Persistence baseline

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
| `intent_optimisation_correlation` | Tracks II-submitted optimisation requests, optimisation id, intentId, intentVersion, correlationId, ICB callback submission target reference where applicable, optimiser outcome state, and correlation of ICB-relayed `OptimisationStatusChangeEvent` outcomes back to the originating `POST /optimisation` request. |
| `intent_optimisation_api_outbox` | Durable API outbox for II-submitted `POST /optimisation` requests, including request body, idempotency key, callback submission URL, request status, retry count, next retry time, accepted optimisation id, and error/failure state. |
| `intent_resolution_audit` | Semantic/KP lookup decisions and rejection reasons |
| `intent_resolution_outbox` | Reliable publication of II-owned events |
| `intent_resolution_dead_letter` | Required minimum failed/unprocessable event handling for exhausted `IntentValidatedEvent` and `OptimisationStatusChangeEvent` processing, including event id, event type, intentId, intentVersion where available, failure reason, retry count, payload hash, and replay/operational status. |
| `shedlock` | Relay coordination if II MS runs a clustered outbox relay |

## 18. Dependency and circuit-breaker behaviour

| Dependency | Behaviour |
|---|---|
| II MS DB unavailable | Hard fail processing; do not acknowledge event until retry/dead-letter policy applies |
| KP unavailable or stale | Fail closed for semantic resolution or service-ready packaging when fresh KP facts are required; retry, refresh, or dead-letter according to operational policy. |
| Kafka/event broker unavailable | Consumed event state must not be lost; II outbox relay retries publication |
| Cache unavailable | Bypass cache and use KP/source where safe |
| Optimisation API outbox unavailable | Prevents outbound `POST /optimisation` submission for optimisation-backed selection. II MS must keep the optimisation request pending and must not emit `IntentNetworkReadyEvent` until the API outbox worker successfully submits the request and the correlated optimiser outcome is received through ICB MS and Kafka. |
| Optimiser / ICB optimiser callback path unavailable | Not a dependency for semantic resolution or `IntentResolvedEvent` emission. For optimisation-backed selection, `POST /optimisation` failure from the API outbox worker, missing optimiser callback through ICB MS, or missing `OptimisationStatusChangeEvent` from Kafka prevents `IntentNetworkReadyEvent` emission until configured retry, callback timeout, governed failure/rejection policy, or operational handling applies. |
| Downstream fulfilment/preparation stage unavailable | Not an external caller concern; II emits only the milestone it has actually reached |

## 19. Security baseline

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

## 20. Observability baseline

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
ii_ms_optimisation_timeout_count
ii_ms_stale_event_ignored_count
ii_ms_kp_stale_or_refresh_failure_count
ii_ms_dead_letter_count
```

## 21. Design baseline statement

II MS is the internal semantic interpretation, resolution, and service-ready preparation service.

It consumes `IntentValidatedEvent` and, for optimisation-backed selection, `OptimisationStatusChangeEvent` after ICB MS callback ingestion. It validates and resolves the admitted expression using Knowledge Plane data, domain knowledge, and any required use-case-specific pre-resolution validation sources, preserves the canonical `expression.context.targets`, `expression.context.constraints`, and `expression.context.preferences` buckets, and emits `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` depending on the resolved milestone. II MS emits neutral event-facing resource and metric structures.

`IntentResolvedEvent.resources[]` carries the full applicable/apply-capable resource set with metric values for observability, audit, replay, and future authorised consumers. `IntentNetworkReadyEvent.serviceConfiguration.orchestratorConfiguration.resources[]` carries only the selected apply/change-execution configuration, while `serviceConfiguration.observerConfiguration.resources[]` carries the full IA observation scope with metric names to observe.

II MS does not own external TMF APIs, runtime Intent lifecycle projection, downstream apply execution, assurance truth, callback ingestion, or KP governance.
