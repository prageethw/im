# II MS Design Brief

## Purpose

Intent Intelligence MS, referred to as II MS, owns semantic interpretation and resolution for admitted runtime intents.

II MS receives syntactically admitted intent facts from IC MS, interprets and validates them against Knowledge Plane/domain knowledge, and emits either a semantic rejection event or an optimisation-ready resolution event.

II MS is internal only. It does not expose a TMF-facing REST API.

## Service identity

| Attribute | Value |
|---|---|
| Display name | Intent Intelligence MS |
| Service name | `intent-intelligence-ms` |
| Short name | II MS |
| Domain | Intent Domain |
| Main responsibility | Semantic interpretation, Knowledge Plane-backed validation, canonical resolution |
| Primary event input | `IntentValidatedEvent` |
| Main event outputs | `IntentRejectedEvent`, `IntentResolvedEvent` |
| Event style | Internal CloudEvents headers with plain JSON `body` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| External TMF API owner | No |

## Core responsibility

II MS answers this question:

```text
Can this admitted intent be semantically understood and resolved into a canonical optimisation-ready handoff?
```

II MS does this after IC MS has already performed syntactic admission validation.

II MS owns:

| Responsibility | Detail |
|---|---|
| Semantic interpretation | Interprets the admitted expression from `IntentValidatedEvent` |
| KP-backed validation | Uses Knowledge Plane data to validate location, service, service class, capability, policy, and resource availability |
| Canonicalisation | Normalises admitted values into canonical internal location, service, target, constraint, preference, and resource terms |
| Rejection decision | Emits `IntentRejectedEvent` when semantic/policy/capability validation fails |
| Resolution decision | Emits `IntentResolvedEvent` when the intent can be handed to optimisation |
| Candidate resource handoff | Provides the full valid resource set known for the resolved context after scope/policy filtering |
| Outbox publication | Publishes II-owned events reliably through the II outbox |
| Idempotency | Deduplicates consumed events and avoids duplicate semantic outcomes |
| Audit | Records semantic interpretation, KP lookup, rejection, and resolution decisions where required |

## II MS does not own

| Concern | Owner |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| Runtime `Intent` REST API | IC MS |
| Runtime `IntentReport` REST API | IC MS |
| External TMF lifecycle/status projection | IC MS |
| External event subscriptions | IC MS / ID MS depending on resource |
| Optimisation decision | IO MS / optimiser |
| Assurance/apply/runtime truth | IA MS |
| Callback ingestion | ICB MS |
| Raw network apply/orchestration execution | Orchestration layer / network orchestrator |
| KP config CRUD/governance | Knowledge Plane operating model |
| OEX user experience | OEX layer |

## Main input

II MS consumes `IntentValidatedEvent` from the internal event backbone.

`IntentValidatedEvent` contains the admitted runtime expression in native internal JSON form. IC MS has already translated the external TMF-facing `Intent.expression.expressionValue` into internal event form.

II MS expects the admitted expression to use the canonical semantic buckets:

```text
targets
constraints
preferences
```

## Main outputs

| Output | Condition | Purpose |
|---|---|---|
| `IntentRejectedEvent` | Semantic, policy, or capability validation fails | Tells IC MS the admitted intent must be externally projected as rejected |
| `IntentResolvedEvent` | Semantic/capability resolution succeeds and optimisation is required | Provides optimiser-ready canonical context and available resource set |

## Processing stages

| Stage | Description |
|---|---|
| Consume | Consume `IntentValidatedEvent` from the internal event backbone |
| Idempotency | Deduplicate by CloudEvents `ce-id` / event id and `intentId` |
| Semantic parse | Interpret `expression.location`, `serviceType`, `serviceClass`, `targets`, `constraints`, and `preferences` |
| KP lookup | Resolve location/service capability from Knowledge Plane |
| Capability validation | Confirm requested service/service class is available for the requested location |
| Policy validation | Validate hard constraints such as priority and redundancy against KP/domain policy |
| Canonicalisation | Normalise values into canonical internal terms |
| Resource discovery | Resolve available KP resources for the location/service |
| Outcome selection | Emit either `IntentRejectedEvent` or `IntentResolvedEvent` |
| Durable publication | Write event to II outbox and publish through relay |
| Audit | Record semantic/KP decision trail where required |

## Semantic bucket handling

II MS preserves the canonical semantic bucket model.

| Bucket | II MS treatment |
|---|---|
| `targets` | Validates supported measurable runtime objectives and carries them forward unchanged or canonically normalised |
| `constraints` | Validates hard requirements such as `priority`, `redundancyRequired`, and `timeWindow` |
| `preferences` | Preserves soft selection guidance such as `preferredAccessTechnology` for optimisation |

II MS must not flatten the buckets into unrelated top-level fields in `IntentResolvedEvent`.

II MS may normalise values only where the semantic meaning is preserved and traceable.

## Knowledge Plane usage

II MS uses the Knowledge Plane as governed domain knowledge.

| KP area | II MS use |
|---|---|
| `locationBasedServices` | Resolve location/service availability and display labels |
| `capabilityStatus` | Decide available vs unknown/unavailable capability |
| `benchmarks` | Understand service capability baseline |
| `resourceIds` | Discover candidate resources for optimiser handoff |
| `resources` | Build valid resource entries for optimisation |
| `expressionMapping` | Resolve aliases/human expressions where applicable |
| `redundancyAvailable` | Validate redundancy requirements |
| logical target references | Resolve optimiser/orchestrator/observer names where needed by downstream events |

II MS must not dump raw KP into events. It curates only the information required by the next stage.

`provider` remains KP/resource-inventory metadata only and is not included by default in event-facing resource entries.

## Resolution rule

II MS emits `IntentResolvedEvent` only when the admitted intent can be semantically understood and resolved into an optimisation-ready context.

A successful resolution implies:

- the location can be resolved
- the requested service type and service class are understood
- the requested service is available or supported for the resolved location
- hard constraints are semantically valid
- the resource set is known and valid for optimisation after scope/policy filtering
- the intent can proceed to optimisation

`IntentResolvedEvent.resources` contains the full valid resource set known in KP for the resolved context after applicable scope/policy filtering. It is not the optimiser-selected set.

## Rejection rule

II MS emits `IntentRejectedEvent` when the admitted intent is syntactically valid but cannot be semantically/policy/capability resolved.

Typical rejection reasons include:

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

## Lifecycle projection relationship with IC MS

II MS does not own the external `Intent.lifecycleStatus` resource API.

II MS emits lifecycle-driving internal facts:

| II outcome | IC MS typical projection |
|---|---|
| `IntentRejectedEvent.lifecycleStatus = Rejected` | `Intent.lifecycleStatus = Rejected` |
| `IntentResolvedEvent.lifecycleStatus = InProgress` | `Intent.lifecycleStatus = InProgress` while optimisation/orchestration continues |

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

Internal II events do not use the TMF external `Intent.expression` wrapper.

## API stance

II MS has no external TMF-facing API.

Only internal/platform endpoints are expected:

```text
/health
/ready
/metrics
```

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
| Optimiser unavailable | Not II MS concern; II only emits `IntentResolvedEvent` |

## Security baseline

II MS is internal only.

Security baseline:

- consume only from trusted internal event topics
- use workload identity for KP access
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
ii_ms_intent_rejected_count
ii_ms_kp_lookup_error_count
ii_ms_resolution_failure_count
ii_ms_outbox_pending_count
ii_ms_outbox_publish_failure_count
ii_ms_duplicate_event_count
```

## Design baseline statement

II MS is the internal semantic interpretation and resolution service. It consumes `IntentValidatedEvent`, validates and resolves the admitted expression using Knowledge Plane/domain knowledge, preserves the canonical `targets`, `constraints`, and `preferences` buckets, and emits either `IntentRejectedEvent` or `IntentResolvedEvent`. II MS does not own external TMF APIs, runtime Intent lifecycle projection, optimisation, assurance truth, callback ingestion, or KP governance.
