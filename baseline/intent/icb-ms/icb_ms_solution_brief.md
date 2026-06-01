# Intent Callback MS Solution Brief


| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Version | v3.0 |
| Last updated | 2026-06-02 |
| Scope | Intent Callback MS solution brief |
| Source of truth after commit | GitHub `baseline/intent/icb-ms/icb_ms_solution_brief.md` |

**Document authority:** This document owns ICB MS operational flow, implementation guidance, configuration, and process behaviour. Field-level contracts are owned by the ICB MS specification; high-level ownership decisions are owned by the design brief.

## Table of contents:

- [1. Summary:](#1-summary)
- [2. Logical View:](#2-logical-view)
- [3. Process View:](#3-process-view)
- [4. Solution Elaboration:](#4-solution-elaboration)
  - [4.1. Responsibilities:](#41-responsibilities)
  - [4.2. ICB MS does not:](#42-icb-ms-does-not)
- [5. Contracts:](#5-contracts)
  - [5.1. Inbound callback contract:](#51-inbound-callback-contract)
    - [5.1.1. Request shape:](#511-request-shape)
    - [5.1.2. Success response:](#512-success-response)
    - [5.1.3. Optimiser outcome callback request shape:](#513-optimiser-outcome-callback-request-shape)
    - [5.1.4. Field specification:](#514-field-specification)
    - [5.1.5. Fields not accepted:](#515-fields-not-accepted)
  - [5.2. Retrieve callback submission status:](#52-retrieve-callback-submission-status)
- [6. Authorisation:](#6-authorisation)
- [7. Persistence / state / outbox model:](#7-persistence-state-outbox-model)
  - [7.1. Persistence tables:](#71-persistence-tables)
  - [7.2. `callback_submission` baseline fields:](#72-callbacksubmission-baseline-fields)
  - [7.3. `callback_outbox` baseline fields:](#73-callbackoutbox-baseline-fields)
- [8. Outbox relay:](#8-outbox-relay)
  - [8.1. Outbox relay behaviour:](#81-outbox-relay-behaviour)
  - [8.2. Promotion rules ConfigMap (`icb-relay-promotion-rules`):](#82-promotion-rules-configmap-icb-relay-promotion-rules)
- [9. Internal Kafka publication:](#9-internal-kafka-publication)
  - [9.1. Internal Kafka topics:](#91-internal-kafka-topics)
  - [9.2. Topic naming convention:](#92-topic-naming-convention)
  - [9.3. IntentCallbackEvent contract:](#93-intentcallbackevent-contract)
    - [9.3.1. Event identity:](#931-event-identity)
    - [9.3.2. Internal Kafka CloudEvents headers:](#932-internal-kafka-cloudevents-headers)
    - [9.3.3. Internal Kafka message body:](#933-internal-kafka-message-body)
    - [9.3.4. Example event body:](#934-example-event-body)
    - [9.3.5. Body field specification:](#935-body-field-specification)
    - [9.3.6. Deviations from older draft shape:](#936-deviations-from-older-draft-shape)
    - [9.3.7. Event-specific rules:](#937-event-specific-rules)
  - [9.4. OptimisationStatusChangeEvent contract:](#94-optimisationstatuschangeevent-contract)
    - [9.4.1. Event identity:](#941-event-identity)
    - [9.4.2. Internal Kafka CloudEvents headers:](#942-internal-kafka-cloudevents-headers)
    - [9.4.3. Event-specific rules:](#943-event-specific-rules)
- [10. Behaviour:](#10-behaviour)
  - [10.1. Normal submit behaviour:](#101-normal-submit-behaviour)
  - [10.2. Duplicate behaviour:](#102-duplicate-behaviour)
  - [10.3. Failure behaviour:](#103-failure-behaviour)
- [11. Configuration:](#11-configuration)
- [12. Consumer contract:](#12-consumer-contract)
  - [12.1. IntentCallbackEvent consumer contract model:](#121-intentcallbackevent-consumer-contract-model)
  - [12.1.1. OptimisationStatusChangeEvent consumer contract model:](#1211-optimisationstatuschangeevent-consumer-contract-model)
  - [12.2. IA MS lifecycle mapping steps:](#122-ia-ms-lifecycle-mapping-steps)
  - [12.3. IA MS mapping config (illustrative only):](#123-ia-ms-mapping-config-illustrative-only)
- [13. Open items:](#13-open-items)
- [14. Closed items:](#14-closed-items)
- [15. MS identity:](#15-ms-identity)

## 1. Summary:

Intent Callback MS, referred to as ICB MS, is the thin callback ingestion service for the Intent Management Enabler platform. It accepts callback submissions from trusted external change-execution or application systems through the API Gateway, performs technical authorisation and structural validation, durably records the accepted callback fact, and publishes raw internal callback events to Kafka. Change-execution/apply callbacks are relayed as `IntentCallbackEvent` to the dedicated callback topic for IA MS. Optimiser outcome callbacks are relayed as `OptimisationStatusChangeEvent` to the main internal event topic for II MS.

ICB MS does not interpret the callback meaning. It does not decide whether a callback means `Active`, `Failed`, `Terminated`, `Degraded`, or any other lifecycle or assurance outcome. IA MS is the normalisation and interpretation point. IA MS consumes `IntentCallbackEvent`, correlates the `intentId`, interprets raw `sourceState.state`, and emits lifecycle-driving `IntentAssuranceEvent` outcomes to the main internal event flow.

The current solution deliberately keeps ICB MS implementation-oriented and narrow:

- REST callback submission in.
- Durable callback submission and outbox record persisted in ICB-owned PostgreSQL-compatible storage.
- Asynchronous relay to Kafka.
- Raw callback event out.
- No lifecycle state, no assurance state, no optimiser outcome interpretation, no KP internals, and no TMF expression wrappers.

## 2. Logical View:

![View](icb_ms_logical_view.svg)

ICB MS sits behind the API Gateway. External systems do not call it directly. The API Gateway authenticates the external caller and forwards the trusted caller identity or claims to ICB MS. ICB MS uses that trusted context for technical authorisation and then validates the callback payload structure.

The callback Kafka topic is dedicated to raw change-execution/apply callback facts. It is separate from the main internal intent event topic. IA MS consumes `IntentCallbackEvent` from the callback topic. For optimiser outcome callbacks, ICB MS publishes `OptimisationStatusChangeEvent` to the main internal intent event topic for II MS.

## 3. Process View:

```text
1. External change-execution/apply system or approved Optimiser platform submits a callback.
2. API Gateway authenticates the caller and forwards the trusted caller context.
3. ICB MS authorises the callback submission for the caller/source context.
4. ICB MS validates only structure and syntax.
5. ICB MS writes the callback submission and callback outbox record in one DB transaction.
6. ICB MS returns 202 Accepted only after durable commit succeeds.
7. ICB outbox relay publishes `IntentCallbackEvent` to `t7.intent.management.events.callbacks` for IA MS, or `OptimisationStatusChangeEvent` to `t7.intent.management.events` for II MS.
8. IA MS consumes `IntentCallbackEvent` and maps raw `sourceState.state`; II MS consumes `OptimisationStatusChangeEvent` and correlates optimiser selected configuration.
9. IC MS consumes IntentAssuranceEvent and projects external TMF-compliant intent lifecycle/status.
```

If the ICB persistence path is unavailable, ICB MS fails fast and does not accept the callback. If Kafka is unavailable after the callback has been durably accepted, the API path can still succeed and the outbox relay retries publication later.

## 4. Solution Elaboration:

### 4.1. Responsibilities:

| Responsibility | Detail |
|---|---|
| Callback API exposure | Exposes `POST /intent-callback/v1/submissions` behind API Gateway. |
| Caller trust handling | Consumes trusted caller identity/claims forwarded by API Gateway. |
| Technical authorisation | Checks the authenticated caller is permitted to submit callback facts for the relevant source/integration context. |
| Structural validation | Validates required fields, non-empty strings, ISO 8601 timestamp shape, request size, and allowed structural shape. |
| Idempotent durable persistence | Persists accepted callback submission and outbox event record in one transaction. |
| Raw event publication | Publishes `IntentCallbackEvent` to `t7.intent.management.events.callbacks` or `OptimisationStatusChangeEvent` to `t7.intent.management.events` through the outbox relay according to the approved source integration profile. |
| Duplicate protection | Uses `Idempotency-Key` and stable callback identifiers where available to prevent duplicate event facts. |
| Audit | Records accepted, rejected, duplicate, and failed callback ingestion decisions. |
| Observability | Emits structured logs, metrics, traces, relay lag, and publication health signals. |

### 4.2. ICB MS does not:

| Concern | Owning component |
|---|---|
| Runtime `Intent` resource API | IC MS |
| External TMF-compliant lifecycle projection | IC MS |
| `IntentReport` projection | IC MS |
| Runtime assurance truth | IA MS |
| Callback state interpretation | IA MS |
| Unknown `intentId` correlation/dead-letter decision | IA MS |
| Skip/unmapped callback decision | IA MS |
| Semantic interpretation/resolution | II MS |
| Optimisation decision and optimiser outcome interpretation | Optimiser / II MS context. ICB MS only relays the approved optimiser outcome event. |
| Optimiser solver/backend execution | `t7-gurobi-optimiser`, where applicable |
| Network apply/change-execution execution | External change-execution/apply system |
| KP config/governance | Knowledge Plane operating model |

ICB MS must not validate that `intentId` exists in the platform. It validates only that the `intentId` field is structurally present and non-empty. IA MS owns correlation, unknown-intent handling, and downstream assurance outcome decisions.

## 5. Contracts:

### 5.1. Inbound callback contract:

The same ICB-owned submission endpoint is used for approved callback profiles. The active profiles are:

| **Callback profile** | **External source** | **ICB output event** | **Kafka topic** | **Intended consumer** |
|---|---|---|---|---|
| Change-execution/apply callback | External orchestrator or apply system | `IntentCallbackEvent` | `t7.intent.management.events.callbacks` | IA MS |
| Optimiser outcome callback | Approved Optimiser platform | `OptimisationStatusChangeEvent` | `t7.intent.management.events` | II MS |

II MS registers or supplies the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, to the Optimiser platform. ICB MS validates and relays the optimiser event structurally; II MS owns correlation and interpretation of the optimiser outcome.

The submission API is a protected REST ingress for event-like callback facts. External callers do not publish directly to internal Kafka topics; ICB MS accepts, validates, persists, and relays the approved callback event internally through the outbox.


#### 5.1.1. Request shape:

```http
POST /intent-callback/v1/submissions
Content-Type: application/json
Accept: application/json
X-Correlation-ID: corr-callback-001
Idempotency-Key: cb-EXT-ORCH-001-INT-HOSP-2026-001-0001
```

```json
{
  "intentId": "INT-HOSP-2026-001",
  "callbackSource": "external-orchestrator-001",
  "callbackTimestamp": "2026-04-18T12:18:00+10:00",
  "sourceState": {
    "state": "APPLIED",
    "reason": "Network apply completed successfully."
  },
  "sourceReference": {
    "id": "orch-job-9001",
    "href": "https://orchestrator.example.com/jobs/orch-job-9001"
  },
  "details": {
    "message": "Network apply completed successfully.",
    "appliedResources": [
      {
        "resourceId": "SYD-PRI-01",
        "role": "primary"
      },
      {
        "resourceId": "SYD-SEC-01",
        "role": "secondary"
      }
    ]
  },
  "@type": "IntentCallbackEventRequest"
}
```

#### 5.1.2. Success response:

ICB MS returns success only after the callback submission and outbox event have been durably committed.

```http
HTTP/1.1 202 Accepted
Location: /intent-callback/v1/submissions/cb-sub-0001
Content-Type: application/json
ETag: "callback-submission-cb-sub-0001-v1"
```

```json
{
  "id": "cb-sub-0001",
  "href": "/intent-callback/v1/submissions/cb-sub-0001",
  "status": "Accepted",
  "statusReason": "Callback submission accepted and queued for internal publication.",
  "intentId": "INT-HOSP-2026-001",
  "receivedAt": "2026-04-18T12:18:03+10:00",
  "@type": "IntentCallbackSubmissionStatus",
  "_links": {
    "self": {
      "href": "/intent-callback/v1/submissions/cb-sub-0001"
    }
  }
}
```


#### 5.1.3. Optimiser outcome callback request shape:

```http
POST /intent-callback/v1/submissions
Content-Type: application/json
Accept: application/json
X-Correlation-ID: corr-intent-create-001
Idempotency-Key: cb-OPT-HSS-2026-001-0001
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
  "@type": "OptimisationStatusChangeEventRequest"
}
```

#### 5.1.4. Field specification:

| Field | Required | Validation | Notes |
|---|---:|---|---|
| `intentId` | Yes for `IntentCallbackEventRequest` | Required, non-empty string | Syntax only. IA MS validates existence and correlation. |
| `callbackSource` | Yes for `IntentCallbackEventRequest` | Required, non-empty string | Identifies the external source/change-execution instance. Gateway identity remains authoritative for trust. |
| `callbackTimestamp` | Yes for `IntentCallbackEventRequest` | ISO 8601 date-time | Source-reported callback time. Distinct from ICB receive time and Kafka publish time. |
| `sourceState.state` | Yes for `IntentCallbackEventRequest` | Required, non-empty string | Raw source-owned state. IA MS interprets it. ICB MS does not map it. |
| `eventType` | Yes for `OptimisationStatusChangeEventRequest` | Must be `OptimisationStatusChangeEvent` for the approved optimiser profile | Used to select the structural relay profile, not to interpret optimiser outcome meaning. |
| `event.optimisation.id` | Yes for `OptimisationStatusChangeEventRequest` | Required object field | Optimisation id for II MS correlation. |
| `event.optimisation.sourceContext.resource.id` | Yes for `OptimisationStatusChangeEventRequest` | Required non-empty string | Related runtime intentId used for Kafka subject/key and II MS correlation. |
| `event.optimisation.sourceContext.correlationId` | Yes for `OptimisationStatusChangeEventRequest` | Required non-empty string | Correlation id propagated to II MS. |
| `event.optimisation.sourceContext.intentVersion` | Required where runtime intent versioning is used | Non-empty string when supplied | Runtime intent version context. |
| `event.optimisation.selectedConfiguration` | Required when `newLifecycleStatus` is `COMPLETED` and outcome drives service-ready packaging | Object | ICB validates structure only; II MS interprets and packages selected configuration. |
| `sourceState.reason` | No | String when supplied | Human-readable source reason or explanatory detail. |
| `sourceReference` | No | Object when supplied | External source reference only. Must not be treated as a platform resource reference. |
| `details` | No | Structured JSON object subject to size and policy limits | Raw or structured callback detail where safe. Must not contain secrets or credentials. |
| `@type` | Yes | `IntentCallbackEventRequest` for change-execution/apply callbacks; `OptimisationStatusChangeEventRequest` for approved optimiser outcome callbacks. | Type marker for the submitted REST callback request payload. Internal Kafka event names remain `IntentCallbackEvent` and `OptimisationStatusChangeEvent`. |
| `Idempotency-Key` header | Strongly recommended / may be required | Non-empty string | Protects external retry safety and duplicate callback handling. |
| `X-Correlation-ID` header | Recommended | Non-empty string | Propagated for tracing and operational correlation. |

#### 5.1.5. Fields not accepted:

| Field | Reason |
|---|---|
| `callbackType` | Not an ICB contract field in the current design direction. ICB MS must not classify callback meaning through a platform callback vocabulary. Raw meaning is carried by `sourceState.state` and interpreted by IA MS. |
| `orchestratorState` | Retired legacy callback state field. Use `sourceState.state`. |
| `source` | Retired legacy shape. Use `callbackSource`. |
| `timestamp` | Retired legacy shape. Use `callbackTimestamp`. |
| `orchestratorType` | Retired legacy callback source-type field. IA MS derives source/change-execution type from its own state/configuration where required. |
| `lifecycleStatus` | ICB MS does not accept or emit lifecycle state. |
| `assuranceStatus` | ICB MS does not accept or emit assurance state. |
| `targets`, `constraints`, `preferences` | These are intent expression/optimisation concepts and must not be included in callback events. |
| KP internals / optimiser scoring / solver internals | Not part of callback ingestion. |
| Platform `references` supplied by external source | External sources must not supply platform URLs or internal resource references. ICB/IA may create safe internal references where needed. |

### 5.2. Retrieve callback submission status:

ICB MS may expose an operational status endpoint for callback submission handling.

```http
GET /intent-callback/v1/submissions/cb-sub-0001
Accept: application/json
```

A caller may request a fresh read using:

```http
GET /intent-callback/v1/submissions/cb-sub-0001
Accept: application/json
Cache-Control: no-cache
```

The status endpoint reports callback submission handling only. It does not expose IA assurance state and does not replace IC MS `Intent` or `IntentReport` resources.

| Status | Meaning |
|---|---|
| `Accepted` | Callback submission and outbox record were durably committed. |
| `Duplicate` | Callback was identified as a duplicate of an already accepted submission. |
| `Published` | Outbox relay published the callback event to Kafka. |
| `PublishFailed` | Outbox relay attempted publication and failed; retry policy applies. |
| `Rejected` | Submission was rejected before durable acceptance. |

These are callback submission handling statuses only. They are not external `Intent.lifecycleStatus` values.

## 6. Authorisation:

| Layer | Responsibility |
|---|---|
| API Gateway | Authenticates external caller, validates token/client identity, applies platform edge controls, and forwards trusted identity/claims. |
| ICB MS | Trusts only gateway-forwarded identity/claims according to platform policy. |
| ICB MS | Authorises whether the authenticated caller/source may submit callbacks for the relevant integration context. |
| ICB MS | Rejects unauthorised, malformed, oversized, or structurally invalid callbacks. |
| ICB MS | Avoids exposing internal DB/Kafka details in errors. |
| ICB MS | Audits security-relevant decisions. |

The inbound `callbackSource` field is useful for callback provenance and downstream interpretation, but it is not by itself an authentication proof. The authenticated gateway context remains authoritative.

## 7. Persistence / state / outbox model:

ICB MS follows the IME DB baseline: managed PostgreSQL or PostgreSQL-compatible RDBMS, owned by ICB MS only.

### 7.1. Persistence tables:

| Table | Purpose |
|---|---|
| `callback_submission` | Accepted submission metadata, status, source, idempotency key, and timestamps. |
| `callback_submission_payload` | Optional payload body store where payload retention or separation is required. |
| `callback_idempotency` | Deduplication and external retry-safety records. |
| `callback_outbox` | Pending/published callback events for Kafka relay, including `IntentCallbackEvent` and `OptimisationStatusChangeEvent`. |
| `callback_audit` | Audit of accepted, rejected, duplicate, and failed callback decisions. |
| `shedlock` | Optional clustered relay coordination table. |

### 7.2. `callback_submission` baseline fields:

| Column | Type | Notes |
|---|---|---|
| `id` | UUID / platform identifier | Primary callback submission identifier. |
| `intent_id` | VARCHAR | Copied from `intentId`; syntax only in ICB. |
| `callback_source` | VARCHAR | External source/change-execution identifier. |
| `callback_timestamp` | TIMESTAMPTZ | Source-reported callback time. |
| `source_state` | VARCHAR | Raw `sourceState.state`. |
| `source_reference_id` | VARCHAR | Optional external source reference identifier. |
| `idempotency_key` | VARCHAR | Optional/required depending on policy; used for retry safety. |
| `status` | VARCHAR / ENUM | `Accepted`, `Duplicate`, `Published`, `PublishFailed`, `Rejected`. |
| `received_at` | TIMESTAMPTZ | ICB MS receive/acceptance time. |
| `published_at` | TIMESTAMPTZ | Set when callback event is published. |
| `created_at` | TIMESTAMPTZ | Row creation time. |
| `updated_at` | TIMESTAMPTZ | Last status/update time. |

### 7.3. `callback_outbox` baseline fields:

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Stable outbox/event identifier; may be used as `ce-id`. |
| `submission_id` | UUID | Links to `callback_submission`. |
| `intent_id` | VARCHAR | Kafka key and event subject. |
| `correlation_id` | VARCHAR | Propagated tracing/correlation value. |
| `event_type` | VARCHAR | `IntentCallbackEvent` or `OptimisationStatusChangeEvent`. |
| `event_payload` | JSONB | JSON payload with top-level `body`. |
| `outbox_status` | VARCHAR / ENUM | Pending/published handling state, with failure represented by retry state or operational status according to implementation policy. |
| `retry_count` | INT | Relay retry attempts. |
| `next_attempt_at` | TIMESTAMPTZ | Optional retry scheduling field. |
| `created_at` | TIMESTAMPTZ | Outbox record creation time. |
| `published_at` | TIMESTAMPTZ | Set only after Kafka ACK. |

## 8. Outbox relay:

### 8.1. Outbox relay behaviour:

| Concern | Detail |
|---|---|
| Relay model | Asynchronous outbox relay. |
| Coordination | Single active relay cycle through ShedLock or equivalent distributed lock where multiple pods exist. |
| Ordering | Publish eligible pending rows in deterministic order, typically `created_at` ascending. |
| Kafka ACK rule | Mark published only after Kafka ACK succeeds. |
| Kafka unavailable | Leave record eligible for retry; API path remains decoupled after durable DB commit. |
| DB unavailable during API submit | Fail fast with `503 Service Unavailable`; no callback is accepted. |
| Idempotency | Relay and IA MS consumer must be idempotent because delivery is at least once. |
| Cleanup | Retention cleanup applies only after durable publication/retention rules allow it. |

### 8.2. Promotion rules ConfigMap (`icb-relay-promotion-rules`):

The ConfigMap governs relay operational behaviour only. It must not express semantic filtering, lifecycle mapping, or skip rules.

```yaml
relay:
  promotion:
    batchSize: 50
    pollIntervalMs: 5000
    maxRetries: 5
    minAgeSeconds: 5
    orderBy: CREATED_AT_ASC
```

## 9. Internal Kafka publication:

ICB MS has one event-delivery path: internal Kafka publication only. The output topic and event type are selected from the approved source integration profile. It does not expose REST hub subscriptions and does not deliver external HTTP webhook notifications.

### 9.1. Internal Kafka topics:

| Topic | Purpose | Producer | Consumer |
|---|---|---|---|
| `t7.intent.management.events.callbacks` | Raw accepted change-execution/apply callback facts as `IntentCallbackEvent` | ICB MS | IA MS |
| `t7.intent.management.events` | Approved optimiser outcome callback facts as `OptimisationStatusChangeEvent` | ICB MS | II MS |

### 9.2. Topic naming convention:

Internal topics use the intent management domain prefix. The callback topic is dedicated to raw callback facts and remains separate from the main internal event topic.

### 9.3. IntentCallbackEvent contract:

#### 9.3.1. Event identity:

| Attribute | Value |
|---|---|
| Event name | `IntentCallbackEvent` |
| Produced by | `intent-callback-ms` |
| Published to | `t7.intent.management.events.callbacks` |
| Intended consumer | `intent-assurance-ms` |
| Kafka key | `intentId` |
| Delivery model | At least once |
| Consumer requirement | Idempotent consumption required |

#### 9.3.2. Internal Kafka CloudEvents headers:

```http
ce-specversion: 1.0
ce-type: IntentCallbackEvent
ce-source: intent-callback-ms
ce-id: evt-intent-callback-0001
ce-time: 2026-04-18T12:18:04+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

Where correlation is available, it should be propagated through the common internal event correlation model, for example via a `correlationId` value inside `body.references` and/or an agreed transport correlation header.

#### 9.3.3. Internal Kafka message body:

```text
topic: t7.intent.management.events.callbacks
key:   {intentId}

headers:
  ce-specversion: 1.0
  ce-type:        IntentCallbackEvent
  ce-source:      intent-callback-ms
  ce-id:          {event-id}
  ce-time:        {relay-publish-timestamp}
  ce-subject:     {intentId}
  content-type:   application/json

value:
{
  "body": {
    ... raw callback fact ...
  }
}
```

#### 9.3.4. Example event body:

```json
{
  "body": {
    "callbackId": "cb-sub-0001",
    "intentId": "INT-HOSP-2026-001",
    "callbackSource": "external-orchestrator-001",
    "callbackTimestamp": "2026-04-18T12:18:00+10:00",
    "sourceState": {
      "state": "APPLIED",
      "reason": "Network apply completed successfully."
    },
    "sourceReference": {
      "id": "orch-job-9001",
      "href": "https://orchestrator.example.com/jobs/orch-job-9001"
    },
    "receivedAt": "2026-04-18T12:18:03+10:00",
    "details": {
      "message": "Network apply completed successfully.",
      "appliedResources": [
        {
          "resourceId": "SYD-PRI-01",
          "role": "primary"
        },
        {
          "resourceId": "SYD-SEC-01",
          "role": "secondary"
        }
      ]
    },
    "references": {
      "correlationId": "corr-callback-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      }
    }
  }
}
```

#### 9.3.5. Body field specification:

| Field | Required | Type | Notes |
|---|---:|---|---|
| `body.callbackId` | Yes | String | ICB callback submission/outbox identifier. |
| `body.intentId` | Yes | String | Present and non-empty; ICB checks syntax only. |
| `body.callbackSource` | Yes | String | External source/change-execution identifier. |
| `body.callbackTimestamp` | Yes | ISO 8601 date-time | Source-reported callback time. |
| `body.sourceState.state` | Yes | String | Raw source state; not interpreted by ICB MS. |
| `body.sourceState.reason` | No | String | Optional source-provided explanation. |
| `body.sourceReference` | No | Object | External source reference. |
| `body.receivedAt` | Yes | ISO 8601 date-time | ICB receive/accept time. |
| `body.details` | No | Object | Safe raw or structured details. |
| `body.references.correlationId` | Recommended | String | End-to-end correlation. |
| `body.references.intent` | Optional / platform-generated | Object | Safe platform intent reference, not caller-supplied. |

#### 9.3.6. Deviations from older draft shape:

| Older draft item | Current baseline treatment |
|---|---|
| Retired legacy callback state field | Replaced by `sourceState.state`. |
| `source` | Replaced by `callbackSource`. |
| `timestamp` | Replaced by `callbackTimestamp`. |
| `callbackType` in request/event | Not used as an ICB classification field in this solution brief. |
| Reverse-domain `ce-type` | Use event name `IntentCallbackEvent` in line with current internal event style. |
| Body fields `eventType`, `eventVersion`, `source`, `eventTime` | Not required in the payload body when CloudEvents metadata is carried in transport headers and JSON uses top-level `body`. |

#### 9.3.7. Event-specific rules:

- `IntentCallbackEvent` carries raw callback facts only.
- Do not include `lifecycleStatus`.
- Do not include `assuranceStatus`.
- Do not include `targets`, `constraints`, `preferences`.
- Do not include optimiser scoring, solver internals, KP internals, or TMF expression wrappers.
- IA MS owns mapping from `sourceState.state` to lifecycle-driving `IntentAssuranceEvent` outcomes.


### 9.4. OptimisationStatusChangeEvent contract:

#### 9.4.1. Event identity:

| Attribute | Value |
|---|---|
| Event name | `OptimisationStatusChangeEvent` |
| Produced by | `intent-callback-ms` |
| Published to | `t7.intent.management.events` |
| Intended consumer | `intent-intelligence-ms` |
| Kafka key | `intentId` where available |
| Delivery model | At least once |
| Consumer requirement | II MS must consume idempotently and correlate to the submitted optimisation request |

#### 9.4.2. Internal Kafka CloudEvents headers:

```http
ce-specversion: 1.0
ce-type: OptimisationStatusChangeEvent
ce-source: intent-callback-ms
ce-id: evt-optimisation-status-001
ce-time: 2026-04-18T12:03:30+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

#### 9.4.3. Event-specific rules:

- `OptimisationStatusChangeEvent` carries the approved optimiser outcome callback fact.
- ICB MS validates the callback structure and relays the event; it does not interpret optimisation status, selected configuration, feasibility, or lifecycle meaning.
- II MS owns optimiser outcome correlation and selected-configuration packaging into `IntentNetworkReadyEvent`.
- Do not include lifecycle or assurance projection fields produced by ICB MS.

## 10. Behaviour:

### 10.1. Normal submit behaviour:

| Step | Behaviour |
|---:|---|
| 1 | Receive callback request behind API Gateway. |
| 2 | Read trusted gateway caller identity/claims. |
| 3 | Authorise caller/source for callback submission. |
| 4 | Validate request structure and size. |
| 5 | Check idempotency key or stable duplicate identifiers where available. |
| 6 | Insert or update callback submission/idempotency records. |
| 7 | Insert callback outbox record in same DB transaction. |
| 8 | Return `202 Accepted` after durable commit. |
| 9 | Relay publishes `IntentCallbackEvent` asynchronously. |

### 10.2. Duplicate behaviour:

Duplicate submissions must not create duplicate internal callback facts. The service may either return the existing accepted status or a `409 DUPLICATE_CALLBACK` response depending on the platform idempotency policy for that integration.

### 10.3. Failure behaviour:

| Scenario | Behaviour |
|---|---|
| API Gateway unavailable | Request does not reach ICB MS. |
| Caller unauthenticated | Gateway rejects or ICB returns `401` if trusted identity is absent. |
| Caller unauthorised | ICB returns `403`. |
| Invalid JSON | ICB returns `400`. |
| Missing/invalid required fields | ICB returns `422`. |
| Payload too large | ICB returns `413`. |
| ICB DB unavailable | ICB returns `503`; no callback accepted and no Kafka event emitted. |
| Kafka unavailable after DB commit | API may still return success; outbox relay retries later. |
| Unknown `intentId` | ICB does not reject solely for unknown intent. IA MS owns correlation/dead-letter decision. |

## 11. Configuration:

| Configuration area | Purpose |
|---|---|
| Gateway trusted header policy | Defines which identity/claim headers ICB MS may trust. |
| Source/integration authorisation policy | Defines which external callers may submit callbacks for each source/integration context. |
| Payload size and schema limits | Prevents oversized or structurally unsafe callback submissions. |
| Idempotency policy | Determines whether `Idempotency-Key` is mandatory for an integration and how duplicate responses are returned. |
| Relay promotion rules | Controls batch size, poll interval, retry settings, age threshold, and ordering. |
| Retention policy | Controls callback submission, payload, audit, and outbox retention. |
| Observability thresholds | Defines alerting for DB failure, outbox lag, publish failure, duplicate spikes, and validation failure spikes. |

## 12. Consumer contract:

### 12.1. IntentCallbackEvent consumer contract model:

| Concern | Detail |
|---|---|
| Intended consumer | IA MS (`intent-assurance-ms`). |
| Producer | ICB MS (`intent-callback-ms`). |
| Topic | `t7.intent.management.events.callbacks`. |
| Contract style | Consumer-driven contract between IA MS and ICB MS. |
| Locked shape | Internal Kafka CloudEvents headers, Kafka key, top-level `body`, and callback fact field semantics. |
| Delivery | At least once. |
| Idempotency | IA MS must deduplicate using `ce-id`, callback id, or agreed stable event identifier. |
| Unknown `intentId` | IA MS owns dead-letter/alert handling. |
| Unmapped raw state | IA MS owns skip/ignore/dead-letter policy according to its mapping configuration. |

#### 12.1.1. OptimisationStatusChangeEvent consumer contract model:

| Concern | Detail |
|---|---|
| Intended consumer | II MS (`intent-intelligence-ms`). |
| Producer | ICB MS (`intent-callback-ms`). |
| Topic | `t7.intent.management.events`. |
| Contract style | Consumer-driven contract between II MS and ICB MS for approved optimiser outcome relay. |
| Locked shape | CloudEvents headers plus approved `OptimisationStatusChangeEvent` payload shape. |
| Delivery | At least once. |
| Idempotency | II MS must deduplicate and correlate using `ce-id`, optimisation id, intentId/intentVersion, and correlation id where available. |
| Interpretation | II MS owns optimiser outcome correlation and selected-configuration packaging. ICB MS validates and relays structure only. |

### 12.2. IA MS lifecycle mapping steps:

| Step | Actor | Action |
|---:|---|---|
| 1 | IA MS | Consumes `IntentCallbackEvent` from `t7.intent.management.events.callbacks`. |
| 2 | IA MS | Validates/correlates `intentId` against IA-owned state. |
| 3 | IA MS | Resolves source/change-execution context from IA-owned configuration/state where required. |
| 4 | IA MS | Maps raw `sourceState.state` into assurance/lifecycle-driving outcome. |
| 5 | IA MS | Handles unmapped/skip states according to IA policy with logging/audit. |
| 6 | IA MS | Writes assurance outcome and IA outbox record. |
| 7 | IA MS | Publishes `IntentAssuranceEvent` to the main internal event topic. |
| 8 | IC MS | Consumes `IntentAssuranceEvent` and projects TMF-compliant intent status/report state. |

### 12.3. IA MS mapping config (illustrative only):

```yaml
sourceStateMappings:
  external-orchestrator-001:
    APPLIED:
      assuranceOutcome: APPLY_COMPLETED
      lifecycleProjection: Active
    APPLY_FAILED:
      assuranceOutcome: APPLY_FAILED
      lifecycleProjection: Failed
    DECOMMISSIONED:
      assuranceOutcome: TERMINATION_CONFIRMED
      lifecycleProjection: Terminated
    PENDING_VALIDATION:
      assuranceOutcome: APPLY_IN_PROGRESS
      lifecycleProjection: InProgress
```

The mapping configuration belongs to IA MS. It is not an ICB MS configuration concern.

## 13. Open items:

| # | Item | Status |
|---:|---|---|
| 1 | Throughput baseline | Parked for load testing. |
| 2 | Deployment sizing | Parked; HPA/min/max replicas and pod sizing to be confirmed after load testing. |
| 3 | Dead-letter implementation detail | IA-owned handling remains the decision point for unknown `intentId` and unmapped source state. Final physical pattern may be DLT table, topic, or operational alert workflow. |
| 4 | Maintenance window mechanism | Mechanism to be finalised if maintenance-window behaviour is retained, such as gateway route disablement, readiness change, or scale-down. |
| 5 | ICB spec/design callback field alignment | Current design direction removes `callbackType` as an ICB classification field. Ensure the implementation contract, OpenAPI/schema, and examples stay aligned on `sourceState.state`. |

## 14. Closed items:

| # | Item | Decision |
|---:|---|---|
| 1 | Service role | ICB MS is a thin callback ingestion and raw event relay service. |
| 2 | Lifecycle interpretation | IA MS owns callback interpretation and lifecycle-driving assurance outcomes. |
| 3 | `intentId` existence validation | ICB MS checks syntax only; IA MS validates/correlates existence. |
| 4 | Callback topic | ICB publishes to dedicated `t7.intent.management.events.callbacks`. |
| 5 | Main event topic usage | ICB MS does not emit change-execution/apply `IntentCallbackEvent` facts to the main internal events topic. Change-execution/apply callbacks are published only to `t7.intent.management.events.callbacks`. Approved optimiser outcome callbacks are published as `OptimisationStatusChangeEvent` to `t7.intent.management.events` for II MS. |
| 6 | Outbox pattern | Accepted callback submission and callback outbox record are written transactionally. |
| 7 | Gateway protection | ICB MS sits behind API Gateway and trusts only gateway-forwarded identity/claims. |
| 8 | Event body style | Internal event value uses top-level `body`. |
| 9 | Internal event exposure | `IntentCallbackEvent` is internal and not directly exposed as a TMF listener event. |
| 10 | Sensitive data | Secrets, tokens, credentials, and raw stack traces are excluded from events and errors. |
| 11 | Optimiser/KP payloads | Optimiser scoring, solver internals, KP internals, and TMF expression wrappers are excluded from callback events. |
| 12 | Consumer responsibility | IA MS is the intended consumer for `IntentCallbackEvent`; II MS is the intended consumer for `OptimisationStatusChangeEvent`. Both consumers must consume idempotently. |

## 15. MS identity:

| Attribute | Value |
|---|---|
| Display name | Intent Callback MS |
| Service name | `intent-callback-ms` |
| Short name | ICB MS |
| Domain | Intent Domain |
| Base path | `/intent-callback/v1` |
| Main endpoint | `POST /intent-callback/v1/submissions` |
| Operational status endpoint | `GET /intent-callback/v1/submissions/{id}` |
| Primary responsibility | Callback submission ingestion and raw callback event relay |
| Primary output events | `IntentCallbackEvent`, `OptimisationStatusChangeEvent` |
| Kafka topics | `t7.intent.management.events.callbacks`, `t7.intent.management.events` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| Deployment | Kubernetes service behind API Gateway |
| Relay model | Outbox relay with single-active coordination such as ShedLock |
| Consumes from Kafka | None |
| Publishes to Kafka | Yes. Publishes `IntentCallbackEvent` to `t7.intent.management.events.callbacks` and `OptimisationStatusChangeEvent` to `t7.intent.management.events` |
| External TMF API owner | No. This is a platform callback ingestion API, not a TMF921 resource API. |
