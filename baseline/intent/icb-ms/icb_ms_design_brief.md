# ICB MS Design Brief


| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Version | v3.0 |
| Last updated | 2026-06-02 |
| Scope | Intent Callback MS design brief |
| Source of truth after commit | GitHub `baseline/intent/icb-ms/icb_ms_design_brief.md` |

**Document authority:** This document owns ICB MS design decisions, service boundaries, and ownership rules. Field-level request and event contracts are owned by the ICB MS specification; operational flow and implementation guidance are owned by the solution brief.

## Table of contents:

- [1. Purpose:](#1-purpose)
- [2. Service identity:](#2-service-identity)
- [3. Callback ingestion sequence:](#3-callback-ingestion-sequence)
- [4. Boundary statement:](#4-boundary-statement)
- [5. Core responsibilities:](#5-core-responsibilities)
- [6. ICB MS does not own:](#6-icb-ms-does-not-own)
- [7. Callback submission model:](#7-callback-submission-model)
- [8. Idempotency baseline:](#8-idempotency-baseline)
- [9. Persistence baseline:](#9-persistence-baseline)
- [10. Outbox baseline:](#10-outbox-baseline)
- [11. Dependency behaviour:](#11-dependency-behaviour)
- [12. Security baseline:](#12-security-baseline)
- [13. Observability baseline:](#13-observability-baseline)
- [14. Design baseline statement:](#14-design-baseline-statement)

## 1. Purpose:

Intent Callback MS, referred to as ICB MS, owns thin callback ingestion for external change-execution/apply systems. ICB MS accepts callback submissions from trusted external systems through the API Gateway, performs technical authorisation and structural validation, durably records the callback fact through an outbox pattern, and publishes raw internal callback outcome events to Kafka. Change-execution/apply callbacks are relayed as `IntentCallbackEvent` to the dedicated callback topic for IA MS. Optimiser outcome callbacks are relayed as `OptimisationStatusChangeEvent` to the main intent-management event topic for II MS.

ICB MS does not interpret lifecycle, assurance, degradation, optimisation, or service meaning.

## 2. Service identity:

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Callback MS |
| Service name | `intent-callback-ms` |
| Short name | ICB MS |
| Main responsibility | Thin callback ingestion and raw callback event relay for change-execution/apply callbacks and optimiser outcome callbacks |
| Primary external input | Callback event submitted over REST from external change-execution/apply systems or approved optimiser platform or approved Optimiser platform |
| Primary internal outputs | `IntentCallbackEvent`; `OptimisationStatusChangeEvent` |
| Internal callback topics | `t7.intent.management.events.callbacks` for `IntentCallbackEvent`; `t7.intent.management.events` for `OptimisationStatusChangeEvent` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| External TMF API owner | No — this is a platform callback ingestion API, not a TMF921 resource API |

## 3. Callback ingestion sequence:

```text
External system / Optimiser -> API Gateway -> ICB MS -> Outbox DB -> Kafka -> IA MS / II MS
```

| **Step** | **Responsibility** |
|---|---|
| External system | Sends callback submission after change-execution/apply progress or outcome |
| API Gateway | Authenticates the caller and forwards trusted identity/claims |
| ICB MS | Authorises callback submission, validates structure, and writes a durable outbox record |
| Outbox DB | Stores callback submission and pending internal callback event durably |
| Kafka topics | Carry raw callback facts to IA MS and optimiser outcome events to II MS |
| IA MS / II MS | IA MS interprets change-execution callbacks; II MS consumes optimiser outcome events and packages selected configuration into `IntentNetworkReadyEvent` |

## 4. Boundary statement:

**ICB MS carries raw callback facts only. IA MS interprets callback state and owns lifecycle/assurance meaning.**

ICB MS must not decide whether a callback means `Active`, `Failed`, `Terminated`, `Degraded`, `Completed`, `Infeasible`, or any other intent or optimisation lifecycle state. ICB MS must not classify callback meaning through a field such as `callbackType`; raw callback meaning is carried by source-owned state such as `sourceState.state`, and IA MS owns interpretation, correlation, skip/dead-letter decisions, and lifecycle-driving assurance outcomes.

## 5. Core responsibilities:

| **Responsibility** | **Detail** |
|---|---|
| Callback API exposure | Exposes callback submission endpoint behind API Gateway |
| Caller trust handling | Consumes trusted identity/claims forwarded by API Gateway |
| Technical authorisation | Checks the authenticated caller is allowed to submit callback facts for the relevant change-execution/source context |
| Structural validation | Validates request syntax, required fields, timestamps, idempotency key, and allowed structural shape |
| Durable persistence | Writes callback submission and outbox event in one DB transaction |
| Raw event publication | Publishes `IntentCallbackEvent` to `t7.intent.management.events.callbacks` or `OptimisationStatusChangeEvent` to `t7.intent.management.events` through outbox relay according to the approved source integration profile |
| Idempotency | Handles external retry safety using idempotency key and/or callback identifiers |
| Audit | Records accepted, rejected, duplicate, and failed callback ingestion decisions |
| Observability | Emits logs, metrics, traces, and outbox relay health signals |

## 6. ICB MS does not own:

| **Concern** | **Owner** |
|---|---|
| Runtime `Intent` resource API | IC MS |
| External TMF-compliant lifecycle projection | IC MS |
| `IntentReport` projection | IC MS |
| Runtime assurance truth | IA MS |
| Callback state interpretation | IA MS |
| Semantic interpretation/resolution | II MS |
| Optimisation decision and selected-configuration meaning | Optimiser / II MS context; ICB MS only relays the approved optimiser outcome event |
| Optimiser solver/backend target | `t7-gurobi-optimiser`, where applicable |
| Network apply/change-execution execution | External change-execution/apply system |
| KP config/governance | Knowledge Plane operating model |

## 7. Callback submission model:

The external callback submission API carries event-like callback facts across the protected REST boundary. For change-execution/apply callbacks, the submitted payload uses `@type: IntentCallbackEvent`; ICB MS accepts, persists, and relays the fact internally as `ce-type: IntentCallbackEvent`. Approved optimiser outcome callbacks use `@type: OptimisationStatusChangeEvent` and are relayed internally as `ce-type: OptimisationStatusChangeEvent`.

Typical callback facts include:

- `intentId`
- `callbackSource`
- `callbackTimestamp`
- `sourceState.state`
- `sourceReference`
- raw or structured detail payload where safe

ICB MS validates that these fields are present and structurally valid. It does not validate that `intentId` is known to IA MS or decide what the raw state means.

Do not use `callbackType` as an ICB contract field. ICB MS does not classify callback meaning; IA MS interprets raw `sourceState.state` and source references in the context of the intent and assurance state.

Optimiser outcome callbacks use the same ICB-owned submission route but a different approved integration profile. II MS registers or supplies the ICB submission URL, `POST /intent-callback/v1/submissions`, to the Optimiser platform. When the Optimiser posts an approved `OptimisationStatusChangeEvent`, ICB MS performs technical authorisation, structural validation, durable persistence, and Kafka relay only. ICB MS publishes the event to `t7.intent.management.events` with `ce-source: intent-callback-ms`; II MS owns correlation and interpretation of the optimiser outcome.


## 8. Idempotency baseline:

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
- `callbackTimestamp`

Duplicate submissions should not create duplicate internal `IntentCallbackEvent` facts.

## 9. Persistence baseline:

ICB MS follows the IME DB baseline: managed PostgreSQL / PostgreSQL-compatible RDBMS, owned by ICB MS only.

Suggested tables:

| **Table** | **Purpose** |
|---|---|
| `callback_submission` | Stores accepted callback submission metadata and current submission publication state |
| `callback_submission_payload` | Optional separate table for raw/structured payload body where retention policy requires separation |
| `callback_idempotency` | Deduplication and external retry protection |
| `callback_outbox` | Durable internal `IntentCallbackEvent` and `OptimisationStatusChangeEvent` publication records |
| `callback_audit` | Audit of accept/reject/duplicate decisions |
| `shedlock` | Relay coordination if clustered outbox relay is used |

## 10. Outbox baseline:

ICB MS must write the accepted callback submission and callback outbox record in the same DB transaction.

The API returns success only after DB and outbox write succeed. Kafka publication is asynchronous through the outbox relay. The target topic and event type are determined by the approved source integration profile. If Kafka is unavailable, the API may still return success when DB/outbox commit succeeded, and the relay retries publication later.

## 11. Dependency behaviour:

| **Dependency** | **Baseline behaviour** |
|---|---|
| API Gateway unavailable | Request does not reach ICB MS |
| ICB MS DB unavailable | Hard fail-fast; return `503 Service Unavailable` |
| Kafka unavailable | API can still succeed after DB/outbox commit; outbox relay retries |
| Outbox relay unavailable | API can still write durable outbox; relay health alarms must fire |
| IA MS / II MS unavailable | ICB MS API unaffected; downstream consumers catch up later from Kafka topics |
| Unknown `intentId` | ICB MS does not reject solely for unknown intent; IA MS owns correlation/dead-letter decision |

## 12. Security baseline:

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

## 13. Observability baseline:

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

## 14. Design baseline statement:

**ICB MS is a thin callback ingestion service. It receives callback submissions from external systems through API Gateway, authorises and structurally validates them, stores them durably through an outbox pattern, and publishes raw `IntentCallbackEvent` facts to the callback Kafka topic for IA MS and approved `OptimisationStatusChangeEvent` facts to the main internal topic for II MS. ICB MS must not interpret lifecycle or assurance meaning; IA MS owns callback correlation and state interpretation.**
