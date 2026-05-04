# IME Baseline Context Dump:

## Purpose:

This file is the maintained running baseline/context dump for the IME / Intent Management Enabler design work in this conversation context.

Going forward, when the user says "baseline", applicable baseline changes should be reflected in this file as well as in conversation memory/context, where file access is available.

## Current Documentation Style Baseline:

- Use one copyable writing block for long decision papers, design briefs, and baseline content when shown in chat.
- Do not create a document file unless explicitly requested.
- Use unnumbered headings.
- End headings with a colon.
- Make all table headings bold.
- Keep wording easy to copy into Confluence or documents.
- Use concise, executive-friendly wording where appropriate.
- Use "industry research", "data-systems literature", or "established data-systems practice" in decision papers rather than repeatedly anchoring body text to a book reference.
- Use Martin Kleppmann's *Designing Data-Intensive Applications* as a background/reference point for data architecture decisions.

## IME Entity Database Selection Baseline:

Managed PostgreSQL / PostgreSQL-compatible RDBMS is the preferred source-of-truth database for IME-owned transactional entities.

Use JSONB for flexible document-shaped resource bodies where appropriate.

NoSQL/document DB was considered but is not selected as the default because IME's lifecycle governance, versioning, ETag/If-Match, cross-resource references, query/list APIs, auditability, transactional outbox/inbox, and operational simplicity requirements favour RDBMS.

Distributed SQL remains a future option only if formal re-evaluation triggers arise:

- RTO under 2 minutes that promotion-based failover cannot meet.
- RPO of zero / no data-loss tolerance.
- Regulatory or contractual active-active regional independence.
- Measurable SLA impact from single-primary write latency.

Application-level active-active persistence remains a future option only if active-active regional ingestion becomes a hard requirement.

Each IME microservice owns its own dedicated managed PostgreSQL database instance or logical managed DB boundary. There is no shared cross-MS database instance, schema, or transactional database.

Schema changes must use versioned Flyway or Liquibase migrations. Manual production schema changes are not permitted.

Initial deployment may be single-region or same-region multi-AZ. The selected DB service must support future cross-region active-passive DR.

Initial DR planning target:

- RTO under 15 minutes.
- RPO under 5 minutes of committed writes for catastrophic regional failure.

Microservice-specific DB baseline:

| **Microservice** | **Database Baseline** |
|---|---|
| ID MS | RDBMS + JSONB for IntentSpecification lifecycle/versioning/governance, ETag, flexible spec body, and `/intentSpecification/hub` subscriptions. |
| IC MS | RDBMS for Intent records, versions, lifecycle projection, IntentReport, and `/intent/hub` subscriptions. |
| IA MS | RDBMS for current assurance/projection state, IA outbox, idempotency tracking, and ShedLock coordination where relay job is deployed. |
| ICB MS | RDBMS for callback outbox, retry state, relay status, durable ingestion, and ShedLock coordination. |
| II MS | No persistent DB required initially; future persistent state must be a scoped update to the DB decision paper. |
| IO MS | No persistent DB required initially; future persistent state must be a scoped update to the DB decision paper. |
| OEX | Out of MS source-of-truth scope; read models/search indexes/caches are derived or secondary stores. |

Any IME MS running an outbox relay job in a clustered deployment must use a distributed lock mechanism such as ShedLock backed by that MS's own RDBMS.

## ICB MS Design Baseline:

ICB MS is a thin inbound relay.

It receives orchestrator callbacks over REST via Gateway, performs syntactical validation only, persists accepted raw callbacks transactionally to `intent_callback_outbox`, and publishes them raw to Kafka as `IntentCallbackEvent` on `t7.intent.management.events.callbacks`.

ICB MS does not:

- Translate callback content.
- Interpret lifecycle.
- Map `orchestratorState`.
- Validate intent existence.
- Derive `orchestratorType`.
- Decide skip/unmapped-state handling.
- Make dead-letter decisions.
- Own lifecycle state.
- Consume Kafka.
- Emit assurance/lifecycle events.

Inbound request fields:

- `intentId`
- `correlationId`
- `orchestratorState`
- `source`
- `timestamp`

ICB validates only field presence/non-empty values and timestamp format.

Gateway handles authentication. ICB may perform minimal integration-level authorisation if required, but no semantic checks.

ICB outbox statuses are locked as:

- `PENDING`
- `PUBLISHED`
- `FAILED`

`SKIPPED` is not used by ICB.

Dedicated callback topic:

- `t7.intent.management.events.callbacks`

IA MS is the sole intended consumer.

## IntentCallbackEvent Baseline:

Kafka message:

- Topic: `t7.intent.management.events.callbacks`
- Key: `{intentId}`

CloudEvents headers:

- `ce-specversion: 1.0`
- `ce-type: au.com.mycsp.intent.callback.v1`
- `ce-source: intent-callback-ms`
- `ce-id: {event-id}`
- `ce-time: {relay-publish-timestamp}`
- `ce-subject: intent/{intentId}`
- `correlationid: {correlationId}`
- `content-type: application/json`

Kafka message value uses top-level `body` wrapper containing:

- `eventType: IntentCallbackEvent`
- `eventVersion: 1.0`
- `source: intent-callback-ms`
- `eventTime`
- `correlationId`
- `intentId`
- `orchestratorState`
- `orchestratorSource`
- `orchestratorTimestamp`

## IA MS Relationship to ICB Callback Flow:

IA MS owns:

- Intent existence/correlation validation.
- Orchestrator type derivation.
- Raw `orchestratorState` mapping.
- Skip/unmapped callback handling.
- Dead-letter decision for unknown intent.
- Assurance outcome/event publication.

IA MS consumes `IntentCallbackEvent`, maps raw callback state to lifecycle/assurance meaning, writes IA outbox, and emits `IntentAssuranceEvent` to `t7.intent.management.events`.

IC MS consumes `IntentAssuranceEvent` and projects external TMF-facing lifecycle/status.

## ICB MS Sequence Diagram Baselines:

### ICB MS sequence diagram 1:

Title: `ICB MS — Inbound Callback Ingestion and Relay`

The exact user-supplied PlantUML is the active baseline unless revised later.

Flow summary:

External Orchestrator posts `POST /intent-callback/v1/submissions` to API Gateway. Gateway forwards authenticated request with identity and claims to `intent-callback-ms`. ICB performs structural validation only for `intentId`, `correlationId`, `orchestratorState`, `source`, and ISO 8601 `timestamp`. Invalid shape returns `400 Bad Request`. Valid shape inserts raw callback into ICB RDBMS Callback Outbox with status `PENDING` and returns `202 Accepted`. ICB Outbox Relay acquires ShedLock, polls `PENDING` rows, publishes `IntentCallbackEvent` to Kafka topic `t7.intent.management.events.callbacks` with key `intentId`, receives Kafka ACK, marks row `PUBLISHED` and sets `published_at`, then releases ShedLock. IA MS consumes `IntentCallbackEvent`, validates/correlates `intentId`, handles unknown/not-correlatable outcomes, derives `orchestratorType`, maps raw `orchestratorState`, records skip outcome for unmapped/skip states, updates current assurance/projection state for mapped actionable states, writes IA outbox record `IntentAssuranceEvent`, publishes to `t7.intent.management.events`, and IC MS projects TMF-facing intent lifecycle/status.

### ICB MS sequence diagram 2:

Title: `ICB MS — Circuit Breaker and Failure Paths`

The exact user-supplied PlantUML is the active baseline unless revised later.

CB1 flow summary:

Outbox DB unavailable during inbound request. ICB attempts to insert raw callback into outbox with status `PENDING`; timeout/DB error occurs; CB1 opens and ICB fails fast. No insert/outbox record is written. ICB returns `503 Service Unavailable` via Gateway. Caller should retry with backoff. No `202 Accepted` is returned, no callback is accepted, and no Kafka event is emitted.

CB2 flow summary:

Kafka unavailable during relay. ICB Outbox Relay acquires ShedLock, polls PENDING outbox rows, attempts to publish `IntentCallbackEvent`, then timeout/Kafka error occurs. CB2 opens and relay pauses with no further publish attempts while open. Rows are left `PENDING` or marked `FAILED` after retry limit is exhausted. Rows are not deleted or marked `PUBLISHED` without confirmed Kafka ACK.

## II MS Knowledge Plane Config Baseline:

II MS Knowledge Plane config is the governed configuration used by Intent Interpreter MS to resolve validated intents into candidate resources and paths.

It includes:

- Service config.
- Location config.
- Resource config.
- Candidate path config.
- Policy rules.
- Observability rules.
- Rejection rules.
- Event shaping rules.

II MS uses platform-standard terms:

- `location.locationId`
- `service.serviceClass`
- `pathClass`
- `resourceClass`
- `networkConfiguration`
- `body`

Avoid legacy terms:

- `site.siteId`
- `trafficClass`
- `configuration.trafficClass`
- `payload`

II MS emits:

- `IntentResolvedEvent` when candidates are resolved.
- `IntentRejectedEvent` when the request cannot be resolved.
- `IntentNetworkReadyEvent` after optimisation result is ready for network apply/projection.

II MS does not own optimisation, assurance, lifecycle truth, callback mapping, or network orchestration execution.

## Knowledge Plane / Internal Event Baseline Highlights:

Internal events use CloudEvents metadata in headers and a top-level `body` wrapper.

Use `body`, not `payload`, for displayed internal event examples.

Canonical event names include:

- `IntentValidatedEvent`
- `IntentResolvedEvent`
- `IntentOptimisedEvent`
- `IntentNetworkReadyEvent`
- `IntentAssuranceEvent`
- `IntentDriftOccurredEvent`
- `IntentCallbackEvent`

`IntentDriftOccurredEvent` is emitted by IA MS, not II MS.

`IntentNetworkReadyEvent` must use `networkConfiguration`, not generic `configuration`, and `networkConfiguration.serviceClass`, not `configuration.trafficClass`.

`IntentNetworkReadyEvent` must include all location/service-applicable observing paths derived from Knowledge Plane, not only selected apply paths.

`IntentAssuranceEvent` should include the full relevant candidate context for assurance scope.

## Terms to Avoid Unless Discussing Legacy:

- `primaryPathId`
- `secondaryPathId`
- `paths` where the agreed model uses `resources` / `candidates`
- `observedOutcome`
- `expectations`
- `priority_level`
- `trafficClass`
- `site.siteId`
- `payload`

Canonical replacements/directions:

- `resources`
- `metrics`
- `targets`
- `priority`
- `serviceClass`
- `location.locationId`
- `body`

## Last Updated:

2026-05-01

## ID MS Design Brief File Baseline:

Created `id_ms_design_brief.md` as the baseline ID MS design brief file. Endpoint request/response examples will be amended into this file as the next step.
