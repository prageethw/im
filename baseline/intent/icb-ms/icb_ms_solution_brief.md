# Intent Callback MS Solution Brief
## Summary:

Intent Callback MS, referred to as ICB MS, is the thin callback ingestion service for the Intent Management Enabler platform. It accepts callback submissions from trusted external change-execution or application systems through the API Gateway, performs technical authorisation and structural validation, durably records the accepted callback fact, and publishes a raw internal `IntentCallbackEvent` to the dedicated callback Kafka topic for IA MS.

ICB MS does not interpret the callback meaning. It does not decide whether a callback means `Active`, `Failed`, `Terminated`, `Degraded`, or any other lifecycle or assurance outcome. IA MS is the normalisation and interpretation point. IA MS consumes `IntentCallbackEvent`, correlates the `intentId`, interprets raw `sourceState.state`, and emits lifecycle-driving `IntentAssuranceEvent` outcomes to the main internal event flow.

The current solution deliberately keeps ICB MS implementation-oriented and narrow:

- REST callback submission in.
- Durable callback submission and outbox record persisted in ICB-owned PostgreSQL-compatible storage.
- Asynchronous relay to Kafka.
- Raw callback event out.
- No lifecycle state, no assurance state, no optimiser interpretation, no KP internals, and no TMF expression wrappers.

## Logical View:

```text
External change-execution/apply system
        |
        | POST /intent-callback/v1/submissions
        v
API Gateway
        |
        | authenticated caller identity / trusted claims
        v
Intent Callback MS
        |
        | accepted callback submission + outbox record
        v
ICB PostgreSQL-compatible database
        |
        | outbox relay publishes raw callback fact
        v
Kafka topic: t7.intent.management.events.callbacks
        |
        | IntentCallbackEvent
        v
Intent Assurance MS
```

ICB MS sits behind the API Gateway. External systems do not call it directly. The API Gateway authenticates the external caller and forwards the trusted caller identity or claims to ICB MS. ICB MS uses that trusted context for technical authorisation and then validates the callback payload structure.

The callback Kafka topic is dedicated to raw callback facts. It is separate from the main internal intent event topic. IA MS is the intended consumer.

## Process View:

```text
1. External change-execution/apply system submits a callback.
2. API Gateway authenticates the caller and forwards the trusted caller context.
3. ICB MS authorises the callback submission for the caller/source context.
4. ICB MS validates only structure and syntax.
5. ICB MS writes the callback submission and callback outbox record in one DB transaction.
6. ICB MS returns 202 Accepted only after durable commit succeeds.
7. ICB outbox relay publishes an IntentCallbackEvent to t7.intent.management.events.callbacks.
8. IA MS consumes the event, validates/correlates intentId, maps raw sourceState.state, and emits IntentAssuranceEvent where appropriate.
9. IC MS consumes IntentAssuranceEvent and projects external TMF-compliant intent lifecycle/status.
```

If the ICB persistence path is unavailable, ICB MS fails fast and does not accept the callback. If Kafka is unavailable after the callback has been durably accepted, the API path can still succeed and the outbox relay retries publication later.

## Solution Elaboration:

### Responsibilities:

| Responsibility | Detail |
|---|---|
| Callback API exposure | Exposes `POST /intent-callback/v1/submissions` behind API Gateway. |
| Caller trust handling | Consumes trusted caller identity/claims forwarded by API Gateway. |
| Technical authorisation | Checks the authenticated caller is permitted to submit callback facts for the relevant source/integration context. |
| Structural validation | Validates required fields, non-empty strings, ISO 8601 timestamp shape, request size, and allowed structural shape. |
| Idempotent durable persistence | Persists accepted callback submission and outbox event record in one transaction. |
| Raw event publication | Publishes `IntentCallbackEvent` to `t7.intent.management.events.callbacks` through the outbox relay. |
| Duplicate protection | Uses `Idempotency-Key` and stable callback identifiers where available to prevent duplicate event facts. |
| Audit | Records accepted, rejected, duplicate, and failed callback ingestion decisions. |
| Observability | Emits structured logs, metrics, traces, relay lag, and publication health signals. |

### ICB MS does not:

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
| Optimisation decision | `optimiser-controller-ms` |
| Optimiser solver/backend execution | `t7-gurobi-optimiser`, where applicable |
| Network apply/change-execution execution | External change-execution/apply system |
| KP config/governance | Knowledge Plane operating model |

ICB MS must not validate that `intentId` exists in the platform. It validates only that the `intentId` field is structurally present and non-empty. IA MS owns correlation, unknown-intent handling, and downstream assurance outcome decisions.

## Contracts:

### Inbound callback contract:

#### Request shape:

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
  "@type": "IntentCallbackSubmission"
}
```

#### Success response:

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

#### Field specification:

| Field | Required | Validation | Notes |
|---|---:|---|---|
| `intentId` | Yes | Required, non-empty string | Syntax only. IA MS validates existence and correlation. |
| `callbackSource` | Yes | Required, non-empty string | Identifies the external source/change-execution instance. Gateway identity remains authoritative for trust. |
| `callbackTimestamp` | Yes | ISO 8601 date-time | Source-reported callback time. Distinct from ICB receive time and Kafka publish time. |
| `sourceState.state` | Yes | Required, non-empty string | Raw source-owned state. IA MS interprets it. ICB MS does not map it. |
| `sourceState.reason` | No | String when supplied | Human-readable source reason or explanatory detail. |
| `sourceReference` | No | Object when supplied | External source reference only. Must not be treated as a platform resource reference. |
| `details` | No | Structured JSON object subject to size and policy limits | Raw or structured callback detail where safe. Must not contain secrets or credentials. |
| `@type` | Yes | Normally `IntentCallbackSubmission` | Type marker for the submission payload. |
| `Idempotency-Key` header | Strongly recommended / may be required | Non-empty string | Protects external retry safety and duplicate callback handling. |
| `X-Correlation-ID` header | Recommended | Non-empty string | Propagated for tracing and operational correlation. |

#### Fields not accepted:

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

### Retrieve callback submission status:

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

## Authorisation:

| Layer | Responsibility |
|---|---|
| API Gateway | Authenticates external caller, validates token/client identity, applies platform edge controls, and forwards trusted identity/claims. |
| ICB MS | Trusts only gateway-forwarded identity/claims according to platform policy. |
| ICB MS | Authorises whether the authenticated caller/source may submit callbacks for the relevant integration context. |
| ICB MS | Rejects unauthorised, malformed, oversized, or structurally invalid callbacks. |
| ICB MS | Avoids exposing internal DB/Kafka details in errors. |
| ICB MS | Audits security-relevant decisions. |

The inbound `callbackSource` field is useful for callback provenance and downstream interpretation, but it is not by itself an authentication proof. The authenticated gateway context remains authoritative.

## Persistence / state / outbox model:

ICB MS follows the IME DB baseline: managed PostgreSQL or PostgreSQL-compatible RDBMS, owned by ICB MS only.

### Persistence tables:

| Table | Purpose |
|---|---|
| `callback_submission` | Accepted submission metadata, status, source, idempotency key, and timestamps. |
| `callback_submission_payload` | Optional payload body store where payload retention or separation is required. |
| `callback_idempotency` | Deduplication and external retry-safety records. |
| `callback_outbox` | Pending/published callback events for Kafka relay. |
| `callback_audit` | Audit of accepted, rejected, duplicate, and failed callback decisions. |
| `shedlock` | Optional clustered relay coordination table. |

### `callback_submission` baseline fields:

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

### `callback_outbox` baseline fields:

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Stable outbox/event identifier; may be used as `ce-id`. |
| `submission_id` | UUID | Links to `callback_submission`. |
| `intent_id` | VARCHAR | Kafka key and event subject. |
| `correlation_id` | VARCHAR | Propagated tracing/correlation value. |
| `event_type` | VARCHAR | `IntentCallbackEvent`. |
| `event_payload` | JSONB | JSON payload with top-level `body`. |
| `outbox_status` | VARCHAR / ENUM | Pending/published handling state, with failure represented by retry state or operational status according to implementation policy. |
| `retry_count` | INT | Relay retry attempts. |
| `next_attempt_at` | TIMESTAMPTZ | Optional retry scheduling field. |
| `created_at` | TIMESTAMPTZ | Outbox record creation time. |
| `published_at` | TIMESTAMPTZ | Set only after Kafka ACK. |

## Outbox relay:

### Outbox relay behaviour:

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

### Promotion rules ConfigMap (`icb-relay-promotion-rules`):

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

## Internal Kafka publication:

ICB MS has one event-delivery path: internal Kafka publication only. It does not expose REST hub subscriptions and does not deliver external HTTP webhook notifications.

### Internal Kafka topics:

| Topic | Purpose | Producer | Consumer |
|---|---|---|---|
| `t7.intent.management.events.callbacks` | Raw accepted callback facts | ICB MS | IA MS |

### Topic naming convention:

Internal topics use the intent management domain prefix. The callback topic is dedicated to raw callback facts and remains separate from the main internal event topic.

### IntentCallbackEvent contract:

#### Event identity:

| Attribute | Value |
|---|---|
| Event name | `IntentCallbackEvent` |
| Produced by | `intent-callback-ms` |
| Published to | `t7.intent.management.events.callbacks` |
| Intended consumer | `intent-assurance-ms` |
| Kafka key | `intentId` |
| Delivery model | At least once |
| Consumer requirement | Idempotent consumption required |

#### Internal Kafka CloudEvents headers:

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

#### Internal Kafka message body:

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

#### Example event body:

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

#### Body field specification:

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

#### Deviations from older draft shape:

| Older draft item | Current baseline treatment |
|---|---|
| Retired legacy callback state field | Replaced by `sourceState.state`. |
| `source` | Replaced by `callbackSource`. |
| `timestamp` | Replaced by `callbackTimestamp`. |
| `callbackType` in request/event | Not used as an ICB classification field in this solution brief. |
| Reverse-domain `ce-type` | Use event name `IntentCallbackEvent` in line with current internal event style. |
| Body fields `eventType`, `eventVersion`, `source`, `eventTime` | Not required in the payload body when CloudEvents metadata is carried in transport headers and JSON uses top-level `body`. |

#### Event-specific rules:

- `IntentCallbackEvent` carries raw callback facts only.
- Do not include `lifecycleStatus`.
- Do not include `assuranceStatus`.
- Do not include `targets`, `constraints`, `preferences`.
- Do not include optimiser scoring, solver internals, KP internals, or TMF expression wrappers.
- IA MS owns mapping from `sourceState.state` to lifecycle-driving `IntentAssuranceEvent` outcomes.

## Behaviour:

### Normal submit behaviour:

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

### Duplicate behaviour:

Duplicate submissions must not create duplicate internal callback facts. The service may either return the existing accepted status or a `409 DUPLICATE_CALLBACK` response depending on the platform idempotency policy for that integration.

### Failure behaviour:

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

## Configuration:

| Configuration area | Purpose |
|---|---|
| Gateway trusted header policy | Defines which identity/claim headers ICB MS may trust. |
| Source/integration authorisation policy | Defines which external callers may submit callbacks for each source/integration context. |
| Payload size and schema limits | Prevents oversized or structurally unsafe callback submissions. |
| Idempotency policy | Determines whether `Idempotency-Key` is mandatory for an integration and how duplicate responses are returned. |
| Relay promotion rules | Controls batch size, poll interval, retry settings, age threshold, and ordering. |
| Retention policy | Controls callback submission, payload, audit, and outbox retention. |
| Observability thresholds | Defines alerting for DB failure, outbox lag, publish failure, duplicate spikes, and validation failure spikes. |

## Consumer contract:

### Consumer contract model:

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

### IA MS lifecycle mapping steps:

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

### IA MS mapping config (illustrative only):

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

## Open items:

| # | Item | Status |
|---:|---|---|
| 1 | Throughput baseline | Parked for load testing. |
| 2 | Deployment sizing | Parked; HPA/min/max replicas and pod sizing to be confirmed after load testing. |
| 3 | Dead-letter implementation detail | IA-owned handling remains the decision point for unknown `intentId` and unmapped source state. Final physical pattern may be DLT table, topic, or operational alert workflow. |
| 4 | Maintenance window mechanism | Mechanism to be finalised if maintenance-window behaviour is retained, such as gateway route disablement, readiness change, or scale-down. |
| 5 | ICB spec/design callback field alignment | Current design direction removes `callbackType` as an ICB classification field. Ensure the implementation contract, OpenAPI/schema, and examples stay aligned on `sourceState.state`. |

## Closed items:

| # | Item | Decision |
|---:|---|---|
| 1 | Service role | ICB MS is a thin callback ingestion and raw event relay service. |
| 2 | Lifecycle interpretation | IA MS owns callback interpretation and lifecycle-driving assurance outcomes. |
| 3 | `intentId` existence validation | ICB MS checks syntax only; IA MS validates/correlates existence. |
| 4 | Callback topic | ICB publishes to dedicated `t7.intent.management.events.callbacks`. |
| 5 | Main event topic usage | ICB MS does not emit callback facts to the main internal events topic. |
| 6 | Outbox pattern | Accepted callback submission and callback outbox record are written transactionally. |
| 7 | Gateway protection | ICB MS sits behind API Gateway and trusts only gateway-forwarded identity/claims. |
| 8 | Event body style | Internal event value uses top-level `body`. |
| 9 | Internal event exposure | `IntentCallbackEvent` is internal and not directly exposed as a TMF listener event. |
| 10 | Sensitive data | Secrets, tokens, credentials, and raw stack traces are excluded from events and errors. |
| 11 | Optimiser/KP payloads | Optimiser scoring, solver internals, KP internals, and TMF expression wrappers are excluded from callback events. |
| 12 | Consumer responsibility | IA MS is the intended consumer and must consume idempotently. |

## MS identity:

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
| Primary output event | `IntentCallbackEvent` |
| Callback Kafka topic | `t7.intent.management.events.callbacks` |
| Source-of-truth persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| Deployment | Kubernetes service behind API Gateway |
| Relay model | Outbox relay with single-active coordination such as ShedLock |
| Consumes from Kafka | None |
| Publishes to Kafka | Yes, callback topic only |
| External TMF API owner | No. This is a platform callback ingestion API, not a TMF921 resource API. |
