# ICB MS Design Brief:

## Purpose:

Intent Callback MS, referred to as ICB MS, owns thin callback ingestion for external orchestration/apply systems. ICB MS accepts callback submissions from trusted external systems through the API Gateway, performs technical authorisation and structural validation, durably records the callback fact through an outbox pattern, and publishes a raw internal `IntentCallbackEvent` to the callback Kafka topic for IA MS.

ICB MS does not interpret lifecycle, assurance, degradation, optimisation, or service meaning.

## Service identity:

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Callback MS |
| Service name | `intent-callback-ms` |
| Short name | ICB MS |
| Main responsibility | Thin callback ingestion and raw callback event relay |
| Primary external input | Callback submission from external orchestration/apply system |
| Primary internal output | `IntentCallbackEvent` |
| Internal callback topic | `t7.intent.management.events.callbacks` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| External TMF API owner | No — this is a platform callback ingestion API, not a TMF921 resource API |

## Callback ingestion sequence:

```text
External system -> API Gateway -> ICB MS -> Outbox DB -> Kafka callback topic -> IA MS
```

| **Step** | **Responsibility** |
|---|---|
| External system | Sends callback submission after orchestration/apply progress or outcome |
| API Gateway | Authenticates the caller and forwards trusted identity/claims |
| ICB MS | Authorises callback submission, validates structure, and writes a durable outbox record |
| Outbox DB | Stores callback submission and pending internal callback event durably |
| Kafka callback topic | Carries raw callback facts to IA MS |
| IA MS | Correlates `intentId`, maps raw `sourceState.state`, and emits `IntentAssuranceEvent` |

## Boundary statement:

**ICB MS carries raw callback facts only. IA MS interprets callback state and owns lifecycle/assurance meaning.**

ICB MS must not decide whether a callback means `Active`, `Failed`, `Terminated`, `Degraded`, or any other intent lifecycle state.

## Core responsibilities:

| **Responsibility** | **Detail** |
|---|---|
| Callback API exposure | Exposes callback submission endpoint behind API Gateway |
| Caller trust handling | Consumes trusted identity/claims forwarded by API Gateway |
| Technical authorisation | Checks the authenticated caller is allowed to submit callback facts for the relevant orchestrator/source context |
| Structural validation | Validates request syntax, required fields, timestamps, idempotency key, and allowed structural shape |
| Durable persistence | Writes callback submission and outbox event in one DB transaction |
| Raw event publication | Publishes `IntentCallbackEvent` to `t7.intent.management.events.callbacks` through outbox relay |
| Idempotency | Handles external retry safety using idempotency key and/or callback identifiers |
| Audit | Records accepted, rejected, duplicate, and failed callback ingestion decisions |
| Observability | Emits logs, metrics, traces, and outbox relay health signals |

## ICB MS does not own:

| **Concern** | **Owner** |
|---|---|
| Runtime `Intent` resource API | IC MS |
| External TMF-facing lifecycle projection | IC MS |
| `IntentReport` projection | IC MS |
| Runtime assurance truth | IA MS |
| Callback state interpretation | IA MS |
| Semantic interpretation/resolution | II MS |
| Optimisation decision | T7 optimiser entity/design |
| Network apply/orchestration execution | External orchestration/apply system |
| KP config/governance | Knowledge Plane operating model |

## Callback submission model:

The external callback submission contains raw orchestration/apply facts.

Typical callback facts include:

- `intentId`
- `callbackType`
- `callbackSource`
- `callbackTimestamp`
- `sourceState.state`
- `sourceReference`
- raw or structured detail payload where safe

ICB MS validates that these fields are present and structurally valid. It does not validate that `intentId` is known to IA MS or decide what the raw state means.

## Idempotency baseline:

External callback submissions should include an idempotency key.

Preferred header:

```http
Idempotency-Key: cb-EXT-ORCH-001-INT-HOSP-2026-001-0001
```

ICB MS should also use stable callback fields to protect against duplicates where available, such as:

- callback source
- source callback identifier
- `intentId`
- `sourceReference`
- `callbackType`
- `callbackTimestamp`

Duplicate submissions should not create duplicate internal `IntentCallbackEvent` facts.

## Persistence baseline:

ICB MS follows the IME DB baseline: managed PostgreSQL / PostgreSQL-compatible RDBMS, owned by ICB MS only.

Suggested tables:

| **Table** | **Purpose** |
|---|---|
| `callback_submission` | Stores accepted callback submission metadata and current submission publication state |
| `callback_submission_payload` | Optional separate table for raw/structured payload body where retention policy requires separation |
| `callback_idempotency` | Deduplication and external retry protection |
| `callback_outbox` | Durable internal `IntentCallbackEvent` publication records |
| `callback_audit` | Audit of accept/reject/duplicate decisions |
| `shedlock` | Relay coordination if clustered outbox relay is used |

## Outbox baseline:

ICB MS must write the accepted callback submission and callback outbox record in the same DB transaction.

The API returns success only after DB and outbox write succeed. Kafka publication is asynchronous through the outbox relay. If Kafka is unavailable, the API may still return success when DB/outbox commit succeeded, and the relay retries publication later.

## Dependency behaviour:

| **Dependency** | **Baseline behaviour** |
|---|---|
| API Gateway unavailable | Request does not reach ICB MS |
| ICB MS DB unavailable | Hard fail-fast; return `503 Service Unavailable` |
| Kafka unavailable | API can still succeed after DB/outbox commit; outbox relay retries |
| Outbox relay unavailable | API can still write durable outbox; relay health alarms must fire |
| IA MS unavailable | ICB MS API unaffected; IA consumes later from callback topic |
| Unknown `intentId` | ICB MS does not reject solely for unknown intent; IA MS owns correlation/dead-letter decision |

## Security baseline:

ICB MS is protected behind API Gateway.

API Gateway responsibilities:

- authenticate external caller
- validate token/client identity
- apply platform edge controls
- forward trusted identity/claims to ICB MS

ICB MS responsibilities:

- authorise callback submission based on trusted identity/claims
- validate request structure and size
- reject unauthorised or malformed callbacks
- avoid exposing internal DB/Kafka details in errors
- audit security-relevant decisions

No secrets, tokens, credentials, or raw internal stack traces are written into callback events.

## Observability baseline:

ICB MS must emit:

- structured logs with `correlationId`, `callbackId`, `intentId`, and callback source where available
- request metrics
- validation failure metrics
- duplicate callback metrics
- outbox pending/publish failure metrics
- relay lag metrics
- audit logs for accept/reject decisions
- distributed traces from API Gateway through DB/outbox relay where applicable

Suggested metrics:

```text
icb_ms_callback_submitted_count
icb_ms_callback_accepted_count
icb_ms_callback_rejected_count
icb_ms_callback_duplicate_count
icb_ms_callback_outbox_pending_count
icb_ms_callback_outbox_publish_failure_count
icb_ms_callback_db_error_count
icb_ms_callback_validation_error_count
```

## Design baseline statement:

**ICB MS is a thin callback ingestion service. It receives callback submissions from external systems through API Gateway, authorises and structurally validates them, stores them durably through an outbox pattern, and publishes raw `IntentCallbackEvent` facts to the callback Kafka topic for IA MS. ICB MS must not interpret lifecycle or assurance meaning; IA MS owns callback correlation and state interpretation.**
