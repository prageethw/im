# IC MS Design Brief

| **Document status** | **Value** |
| --- | --- |
| Status | Accepted baseline design brief |
| Scope | IC MS design brief |
| Source of truth after commit | GitHub `baseline/intent/ic-ms/ic_ms_design_brief.md` |

## Table of contents:

- [1. Service identity:](#1-service-identity)
- [2. IC MS core purpose:](#2-ic-ms-core-purpose)
- [3. IC MS does not own:](#3-ic-ms-does-not-own)
- [4. IC MS API surface:](#4-ic-ms-api-surface)
  - [4.1. Deployment path convention:](#41-deployment-path-convention)
  - [4.2. Intent resource APIs:](#42-intent-resource-apis)
  - [4.3. IntentReport APIs:](#43-intentreport-apis)
  - [4.4. Hub subscription APIs:](#44-hub-subscription-apis)
- [5. IC MS validation responsibility:](#5-ic-ms-validation-responsibility)
- [6. Event delivery paths:](#6-event-delivery-paths)
- [7. IntentValidatedEvent production rule:](#7-intentvalidatedevent-production-rule)
  - [7.1. Rule: `IntentValidatedEvent` is a state and progress event, not a point-to-point command:](#71-rule-intentvalidatedevent-is-a-state-and-progress-event-not-a-point-to-point-command)
- [8. Internal Kafka event publication:](#8-internal-kafka-event-publication)
  - [8.1. Internal Kafka CloudEvents-style headers:](#81-internal-kafka-cloudevents-style-headers)
- [9. External webhook notification delivery:](#9-external-webhook-notification-delivery)
  - [9.1. External webhook HTTP headers:](#91-external-webhook-http-headers)
  - [9.2. External webhook success response:](#92-external-webhook-success-response)
- [10. IC MS lifecycle and status projection:](#10-ic-ms-lifecyclestatus-projection)
  - [10.1. Lifecycle values:](#101-lifecycle-values)
  - [10.2. Lifecycle ownership rule:](#102-lifecycle-ownership-rule)
- [11. Internal event interactions:](#11-internal-event-interactions)
  - [11.1. Produces:](#111-produces)
  - [11.2. Current primary consumer:](#112-current-primary-consumer)
  - [11.3. Consumes:](#113-consumes)
  - [11.4. Does not consume by default:](#114-does-not-consume-by-default)
- [12. External event family:](#12-external-event-family)
  - [12.1. Intent events:](#121-intent-events)
  - [12.2. IntentReport events:](#122-intentreport-events)
  - [12.3. External event timestamp rule:](#123-external-event-timestamp-rule)
- [13. IntentReport responsibility:](#13-intentreport-responsibility)
  - [13.1. IntentReport delete posture:](#131-intentreport-delete-posture)
- [14. TMF compliance and platform extension baseline:](#14-tmf-compliance-and-platform-extension-baseline)
- [15. Response classification headers:](#15-response-classification-headers)
- [16. IC MS boundary statement:](#16-ic-ms-boundary-statement)
- [17. Lifecycle, status, and versioning baseline:](#17-lifecycle-status-and-versioning-baseline)
  - [17.1. Intent-level lifecycleStatus:](#171-intent-level-lifecyclestatus)
  - [17.2. Intent-version lifecycleStatus:](#172-intent-version-lifecyclestatus)
  - [17.3. Version state meanings:](#173-version-state-meanings)
  - [17.4. Version pointer:](#174-version-pointer)
  - [17.5. Why `activeVersion`:](#175-why-activeversion)
  - [17.6. Lifecycle/status ownership:](#176-lifecyclestatus-ownership)
  - [17.7. Lifecycle/versioning example:](#177-lifecycleversioning-example)
  - [17.8. Example JSON — while v2 is still being processed:](#178-example-json-while-v2-is-still-being-processed)
  - [17.9. Example JSON — after v2 becomes active:](#179-example-json-after-v2-becomes-active)
  - [17.10. Example JSON — after rollback or restart to v1 is acknowledged:](#1710-example-json-after-rollback-or-restart-to-v1-is-acknowledged)
  - [17.11. Example JSON — after rollback to v1 is confirmed:](#1711-example-json-after-rollback-to-v1-is-confirmed)
  - [17.12. Example JSON — after v2 is terminated and then retired from future use:](#1712-example-json-after-v2-is-terminated-and-then-retired-from-future-use)
  - [17.13. Example JSON — after termination:](#1713-example-json-after-termination)
  - [17.14. Delete or terminate rule:](#1714-delete-or-terminate-rule)
  - [17.15. Final baseline statements:](#1715-final-baseline-statements)
- [18. Intent lifecycle state diagrams:](#18-intent-lifecycle-state-diagrams)
  - [18.1. Purpose:](#181-purpose)
  - [18.2. Intent-level lifecycle states:](#182-intent-level-lifecycle-states)
  - [18.3. Intent-version lifecycle states:](#183-intent-version-lifecycle-states)
  - [18.4. Key lifecycle rules:](#184-key-lifecycle-rules)
  - [18.5. Intent-level lifecycle:](#185-intent-level-lifecycle)
  - [18.6. Intent-version lifecycle:](#186-intent-version-lifecycle)
  - [18.7. Example activeVersion transition:](#187-example-activeversion-transition)
  - [18.8. Baseline statement:](#188-baseline-statement)
- [19. External Intent projection and version visibility baseline:](#19-external-intent-projection-and-version-visibility-baseline)
  - [19.1. External projection rule:](#191-external-projection-rule)
  - [19.2. GET /intent/{id} example:](#192-get-intentid-example)
  - [19.3. Version-history exposure rule:](#193-version-history-exposure-rule)
  - [19.4. Baseline statement:](#194-baseline-statement)
- [20. Operation behaviour and IntentSpecification reference baseline:](#20-operation-behaviour-and-intentspecification-reference-baseline)
  - [20.1. IntentSpecification and expression IRI resolution rule:](#201-intentspecification-and-expression-iri-resolution-rule)
  - [20.2. Two separate version concepts:](#202-two-separate-version-concepts)
  - [20.3. Operation behaviour:](#203-operation-behaviour)
  - [20.4. Baseline statement:](#204-baseline-statement)
- [21. Caching, ETag, and dependency-specific circuit-breaker baseline:](#21-caching-etag-and-dependency-specific-circuit-breaker-baseline)
  - [21.1. Caching scope:](#211-caching-scope)
  - [21.2. GET caching behaviour:](#212-get-caching-behaviour)
  - [21.3. Client cache override:](#213-client-cache-override)
  - [21.4. ETag rule:](#214-etag-rule)
  - [21.5. Dependency-specific circuit-breaker behaviour:](#215-dependency-specific-circuit-breaker-behaviour)
  - [21.6. ID MS dependency rule:](#216-id-ms-dependency-rule)
  - [21.7. Failure responses:](#217-failure-responses)
  - [21.8. Baseline statements:](#218-baseline-statements)
- [22. Deployment and persistence strategy:](#22-deployment-and-persistence-strategy)
  - [22.1. Runtime and state model:](#221-runtime-and-state-model)
  - [22.2. Source of truth:](#222-source-of-truth)
  - [22.3. Recommended persistence model:](#223-recommended-persistence-model)
  - [22.4. JSONB usage:](#224-jsonb-usage)
  - [22.5. Suggested relational columns:](#225-suggested-relational-columns)
  - [22.6. Event publication and consumption:](#226-event-publication-and-consumption)
  - [22.7. High availability and scaling:](#227-high-availability-and-scaling)
  - [22.8. Disaster recovery:](#228-disaster-recovery)
  - [22.9. Health checks:](#229-health-checks)
  - [22.10. Configuration and secrets:](#2210-configuration-and-secrets)
  - [22.11. Deployment baseline statement:](#2211-deployment-baseline-statement)
- [23. Shared semantic bucket design baseline:](#23-shared-semantic-bucket-design-baseline)
- [24. Runtime expression context alignment with ID MS:](#24-runtime-expression-context-alignment-with-id-ms)
- [25. TMF fields and precondition response alignment:](#25-tmf-fields-and-precondition-response-alignment)
- [26. PATCH semantics:](#26-patch-semantics)
- [27. Expression schema alignment:](#27-expression-schema-alignment)

## 1. Service identity:

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Controller MS |
| Short name | IC MS |
| Service name | `intent-controller-ms` |
| Domain | Intent Domain |
| Primary resource | `Intent` |
| Secondary resource | `IntentReport` |
| Primary responsibility | TMF-compliant runtime Intent controller, schema and request-shape admission, lifecycle and status projection, and external runtime intent events |

## 2. IC MS core purpose:

IC MS owns the runtime intent API boundary for the Intent Enabler.

It is responsible for:

| **Area** | **IC MS responsibility** |
|---|---|
| External `Intent` API | Create, retrieve, list, update, patch, delete runtime intents |
| External `IntentReport` API | Expose read-only assurance/report projections for intents |
| Runtime lifecycle and status projection | Own external `Intent.lifecycleStatus`, `statusReason`, and `statusChangeDate` |
| Schema and request-shape validation | Validate incoming runtime `Intent` against `ACTIVE` `IntentSpecification` from ID MS |
| Initial admission | Accept schema and request-shape valid requests and project `Acknowledged` |
| Internal state and progress event publication | Emit `IntentValidatedEvent` to the internal Kafka event backbone after schema and request-shape validation succeeds |
| Rejection projection | Consume rejection outcome from II MS and project `Rejected` |
| Assurance projection | Consume `IntentAssuranceEvent` from IA MS and update external `Intent` / `IntentReport` |
| External webhook notifications | Deliver TMF-aligned `Intent` and `IntentReport` notifications by HTTP POST to subscriber listener callback URLs |

## 3. IC MS does not own:

| **Not owned by IC MS** | **Owner** |
|---|---|
| `IntentSpecification` design-time catalogue | ID MS |
| Semantic validation | II MS |
| Policy validation | II MS + lightweight II MS KP + `t7.knowledge plane` |
| Knowledge resolution | II MS + `t7.knowledge plane` |
| Optimisation | `optimiser-controller-ms` using optimiser backends such as `t7-gurobi-optimiser` where relevant |
| Network change execution | Change execution layer / network orchestrator |
| Apply outcome interpretation | IA MS |
| Runtime assurance truth | IA MS |
| Real-time telemetry | `t7.telemetry` consumed by IA MS |
| Callback ingestion | ICB MS |
| Raw orchestrator callback interpretation | IA MS |

## 4. IC MS API surface:

### 4.1. Deployment path convention:

Examples in this design brief use the platform route prefix:

```http
/intentManagement/v5
```

The API gateway may map external deployment routes to the internal platform route prefix without changing IC MS resource ownership or operation semantics.

### 4.2. Intent resource APIs:

| **Purpose** | **Method** | **Endpoint** | **Position** |
|---|---:|---|---|
| Create runtime intent | `POST` | `/intentManagement/v5/intent` | TMF-aligned |
| List runtime intents | `GET` | `/intentManagement/v5/intent` | TMF-aligned |
| Retrieve runtime intent by ID | `GET` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Full replace runtime intent | `PUT` | `/intentManagement/v5/intent/{id}` | Platform extension |
| Partial update runtime intent | `PATCH` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Delete / terminate runtime intent | `DELETE` | `/intentManagement/v5/intent/{id}` | TMF-aligned delete verb; platform behaviour is termination, not physical deletion |

### 4.3. IntentReport APIs:

| **Purpose** | **Method** | **Endpoint** | **Position** |
|---|---:|---|---|
| List reports for intent | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport` | Platform/TMF-aligned nested report projection |
| Retrieve report by ID | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport/{id}` | Platform/TMF-aligned nested report projection |

### 4.4. Hub subscription APIs:

Strict TMF route form:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/hub` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/hub/{id}` |

Accepted domain-scoped platform extension:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create intent event subscription | `POST` | `/intentManagement/v5/intent/hub` |
| Retrieve intent event subscription | `GET` | `/intentManagement/v5/intent/hub/{id}` |
| Delete intent event subscription | `DELETE` | `/intentManagement/v5/intent/hub/{id}` |

Strict TMF hub routes are rooted at `/intentManagement/v5/hub`.

IC MS also supports the domain-scoped `/intentManagement/v5/intent/hub` route family as an approved platform extension for Intent and IntentReport event subscriptions. `GET /intentManagement/v5/intent/hub/{id}` is an operational convenience extension and is not part of the strict minimum TMF hub operation set.

## 5. IC MS validation responsibility:

On `POST /intentManagement/v5/intent`, IC MS:

1. receives the external runtime intent request
2. validates basic TMF/resource shape
3. resolves the referenced `IntentSpecification`
4. validates the request against the `ACTIVE` `IntentSpecification`
5. rejects schema and request-shape invalid requests
6. accepts schema and request-shape valid requests
7. creates/persists the external `Intent` projection
8. sets initial `lifecycleStatus = Acknowledged` and persists the server-resolved `isBundle` value, defaulting to `false` when omitted on create
9. emits `IntentValidatedEvent` to the internal Kafka event backbone after schema and request-shape validation succeeds

IC MS validates syntax and contract shape only.

It does not decide semantic meaning, network feasibility, policy allowability, resource candidates, optimisation, apply result, or runtime assurance truth.

## 6. Event delivery paths:

IC MS has two separate event-delivery paths.

| **Path** | **Purpose** | **Durability model** | **Delivery mechanism** | **Headers** | **Consumers** |
|---|---|---|---|---|---|
| Internal platform events | Internal workflow/state-progress events such as `IntentValidatedEvent` | IC MS internal event outbox | Kafka relay publishes to the internal event topic | CloudEvents-style Kafka/platform headers | Authorised internal microservices such as II MS |
| External TMF/webhook notifications | Subscriber notifications for `Intent` and `IntentReport` projection changes | IC MS webhook delivery outbox | HTTP retry relay posts to subscriber listener callback URLs | HTTP request headers | External subscribers registered through `/hub` or `/intent/hub` |

Kafka is used for internal platform events where independent internal consumers exist. Kafka is not used for external hub notification delivery. External hub subscribers receive REST webhook callbacks, not Kafka messages.

## 7. IntentValidatedEvent production rule:

IC MS does not emit `IntentValidatedEvent` as a point-to-point command for one specific consumer. IC MS emits `IntentValidatedEvent` as a platform state and progress event that states:

```text
This Intent has passed IC MS schema and request-shape validation and has been admitted into the intent lifecycle.
```

Current primary consumer:

```text
II MS / intent-intelligence-ms
```

II MS is the current primary consumer because it performs semantic validation and resolution. However, the event is not defined only for II MS. It may be consumed by other authorised internal consumers where useful.

### 7.1. Rule: `IntentValidatedEvent` is a state and progress event, not a point-to-point command:

`IntentValidatedEvent` records that IC MS has admitted the runtime Intent after schema and request-shape validation. It is not an instruction addressed only to II MS.

## 8. Internal Kafka event publication:

IC MS publishes internal platform events through the internal event outbox and Kafka relay.

| **Internal event** | **Produced by** | **Primary consumer** | **Delivery** |
|---|---|---|---|
| `IntentValidatedEvent` | IC MS | II MS | Internal event outbox -> Kafka relay -> internal event topic |

Internal Kafka events use CloudEvents-style Kafka/platform headers.

### 8.1. Internal Kafka CloudEvents-style headers:

| **Header** | **Value pattern** | **Notes** |
|---|---|---|
| `ce-specversion` | `1.0` | CloudEvents spec version |
| `ce-type` | `IntentValidatedEvent` | Internal event type |
| `ce-source` | `intent-controller-ms` | Producing service identity |
| `ce-id` | `{event-id}` | Unique event identifier |
| `ce-time` | `{event-time}` | Event occurrence / publication timestamp |
| `ce-subject` | `{intentId}` | Runtime Intent the event relates to |
| `correlationid` | `{correlationId}` | End-to-end trace correlation |
| `content-type` | `application/json` | Payload content type |

## 9. External webhook notification delivery:

External `Intent` and `IntentReport` events are delivered through the REST hub subscription model. IC MS stores subscriber registrations and writes delivery work to a local webhook delivery outbox. A webhook delivery relay sends HTTP `POST` requests to subscriber listener callback URLs.

External webhook notifications use HTTP headers and a TMF-aligned event payload body. They do not use Kafka topics or CloudEvents-style Kafka headers.

### 9.1. External webhook HTTP headers:

| **HTTP header** | **Value pattern** | **Notes** |
|---|---|---|
| `Content-Type` | `application/json` | Event body is JSON |
| `X-Correlation-Id` | `{correlationId}` | Optional/required depending on gateway policy |
| `Authorization` | Subscriber callback credential | Used where callback authentication is configured |

### 9.2. External webhook success response:

```http
HTTP/1.1 204 No Content
```

## 10. IC MS lifecycle and status projection:

IC MS externally exposes lifecycle and status using:

```json
{
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Intent request accepted for semantic validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00"
}
```

### 10.1. Lifecycle values:

```text
Draft
Acknowledged
InProgress
Active
Degraded
Paused
Rejected
Failed
Terminated
```

### 10.2. Lifecycle ownership rule:

IC MS owns the external lifecycle and status projection, but not the runtime truth.

| **Lifecycle/status source** | **IC MS action** |
|---|---|
| Submitted IC MS schema and request-shape validation succeeds | Project `Acknowledged` |
| Draft creation with `submit:false` | Project `Draft`; no admitted Intent version is created and `activeVersion` is not driven |
| II MS semantic/policy rejection | Project `Rejected` |
| IA MS apply success / active assurance | Project `Active` |
| IA MS degraded assurance | Project `Degraded` |
| IA MS paused/failed/terminated outcome | Project `Paused`, `Failed`, or `Terminated` |
| Delete or terminate request accepted | Project termination path according to final delete or terminate rules |

## 11. Internal event interactions:

### 11.1. Produces:

```text
IntentValidatedEvent
```

Meaning:

```text
The runtime Intent has passed IC MS schema and request-shape validation and is admitted for downstream semantic validation, resolution, and fulfilment processing.
```

### 11.2. Current primary consumer:

```text
II MS / intent-intelligence-ms
```

### 11.3. Consumes:

```text
IntentRejectedEvent
IntentAssuranceEvent
```

### 11.4. Does not consume by default:

```text
IntentCallbackEvent
```

`IntentCallbackEvent` is consumed by IA MS. IA MS maps callback/orchestrator state into assurance/lifecycle truth and emits `IntentAssuranceEvent`.

## 12. External event family:

IC MS emits TMF-aligned external events for `Intent` and `IntentReport` projection changes.

### 12.1. Intent events:

```text
IntentCreateEvent
IntentAttributeValueChangeEvent
IntentStatusChangeEvent
IntentDeleteEvent
```

### 12.2. IntentReport events:

```text
IntentReportCreateEvent
IntentReportAttributeValueChangeEvent
IntentReportDeleteEvent
```

`IntentReportDeleteEvent` is retained in this vocabulary for TMF alignment and governed internal/admin deletion or retention purge scenarios only; it is not emitted for ordinary external consumer delete because that operation is not exposed by default.

### 12.3. External event timestamp rule:

External TMF-aligned event examples and emitted event envelopes populate both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp. `timeOccurred` is the corrected platform spelling used consistently across IC MS and ID MS external event examples.

These events are external projection/resource events only. They must not expose raw telemetry, raw optimiser decisions, raw `t7.knowledge plane` data, raw callback payloads, internal candidate scoring, internal Kafka event payloads, or full internal `IntentAssuranceEvent` body unless deliberately curated into `IntentReport`.

## 13. IntentReport responsibility:

`IntentReport` is a read-only external report projection owned by IC MS. It is based on assurance truth from IA MS, but it is not raw assurance telemetry and not the raw `IntentAssuranceEvent` body.

IntentReport uses the TMF expression wrapper. Curated report facts are carried inside `IntentReport.expression.expressionValue`.

The default report areas are:

- `version`
- `lifecycleStatus`
- `reportTime`
- `summary`
- `statusReason` where useful
- `serviceSummary`
- `resourceSummary` where useful
- `targetSummary`
- `observationSummary`

`targetSummary` is fact-only by default: target value, observed value, and unit. It does not include aggregate compliance-result labels or per-target `status` by default.

Consumers decide compliance from the facts. IntentReport should not expose raw telemetry dumps, raw callback payloads, raw optimiser details, raw KP data, internal candidate scoring, internal Kafka payloads, or implementation-only details unless deliberately curated and approved for external reporting.

### 13.1. IntentReport delete posture:

`IntentReport` is read-only from ordinary external API consumers.

IC MS does not expose ordinary external `DELETE /intentManagement/v5/intent/{intentId}/intentReport/{id}` through NGW or public TMF-compliant consumer APIs by default. External consumers can list and retrieve `IntentReport` records only.

Reason: `IntentReport` is a curated assurance/lifecycle report projection and audit/history record. Deleting it as a normal consumer operation would remove traceability and would require a separate report lifecycle such as `Archived` or `Deleted`, which is deliberately not baselined.

IC MS may provide an internal-only governed `IntentReport` delete/purge capability. This capability is not routed through NGW, not advertised as a public consumer API, and not available to normal external consumers. It is restricted to retention purge, legal deletion, platform administration, approved data-correction workflows, or policy-governed cleanup.

If a deployment must expose the TMF report delete route for compatibility, it must be restricted/admin-only or return a policy error such as `403 Forbidden` or `405 Method Not Allowed` for ordinary consumers.

`IntentReportDeleteEvent` remains part of the external TMF-aligned event vocabulary for `IntentReport` alignment. It may be emitted only after successful governed internal/admin removal where notification is allowed by policy. It is not emitted as the result of ordinary external consumer delete because ordinary report delete is not exposed.

No separate `IntentReport` lifecycle is baselined for ordinary consumer use because delete/purge is a governed administrative operation, not a normal report lifecycle transition.

## 14. TMF compliance and platform extension baseline:

IC MS keeps the external Intent and IntentReport contract TMF-aligned while documenting controlled platform extensions explicitly.

## 15. Response classification headers:

The service returns a response classification header on external REST API responses so callers can distinguish strict TMF-aligned behaviour from documented platform-extension behaviour.

This is a response header only. Clients do not send this header in requests.

| **Response header** | **Meaning** |
|---|---|
| `X-Platform-Extension: true` | The route, method, response, or behaviour includes a documented platform extension. |
| `X-Platform-Extension: false` | No platform extension is used for the response. |

Use canonical header casing in examples:

```http
X-Platform-Extension: false
```

or:

```http
X-Platform-Extension: true
```


IC MS remains TMF-aligned at the external contract level, while retaining documented, non-breaking platform extensions for deterministic update, domain-scoped subscription management, concurrency, and retained projection governance.

Strict TMF-compatible external operations:

| **Resource area** | **Strict TMF-compatible operations** |
|---|---|
| `Intent` | `POST /intentManagement/v5/intent`, `GET /intentManagement/v5/intent`, `GET /intentManagement/v5/intent/{id}`, `PATCH /intentManagement/v5/intent/{id}`, `DELETE /intentManagement/v5/intent/{id}` |
| `IntentReport` | `GET /intentManagement/v5/intent/{intentId}/intentReport`, `GET /intentManagement/v5/intent/{intentId}/intentReport/{id}` |
| Hub subscription | `POST /intentManagement/v5/hub`, `DELETE /intentManagement/v5/hub/{id}` |

Approved IC MS platform extensions:

| **Extension** | **Purpose and boundary** |
|---|---|
| `PUT /intentManagement/v5/intent/{id}` | Deterministic full replacement where supported; `PATCH` remains available for strict TMF-compatible clients. |
| `/intentManagement/v5/intent/hub` | Domain-scoped subscription route for IC-owned `Intent` and `IntentReport` notifications. |
| `GET /intentManagement/v5/intent/hub/{id}` | Operational convenience for retrieving a domain-scoped subscription. Not part of the strict minimum TMF hub operation set. |
| `ETag` and `If-Match` with `428 Precondition Required` and `412 Precondition Failed` | Platform optimistic-concurrency policy for unsafe operations. |
| Termination-retention behaviour for `DELETE /intent/{id}` | `DELETE` is treated as termination of the retained runtime `Intent` projection, not physical deletion by default. |
| Governed or admin-only `IntentReport` delete posture | Ordinary external consumers list and retrieve reports only; internal or admin purge may emit `IntentReportDeleteEvent` where policy allows. |

Platform preference:

- `PUT` is preferred for deterministic full replacement where supported.
- `PATCH` is supported for TMF compatibility but not encouraged for ordinary edits.
- Strict TMF clients can use `PATCH` and root `/hub` routes; platform-aware clients can use the documented IC domain-scoped routes and `PUT` extension where allowed.

## 16. IC MS boundary statement:

**IC MS is the TMF-compliant runtime intent controller. It owns external `Intent` and `IntentReport` resources, performs schema and request-shape validation against `ACTIVE` `IntentSpecification`, emits `IntentValidatedEvent` as an internal state and progress event, and projects external lifecycle and status from II MS rejection outcomes and IA MS assurance outcomes. IC MS does not perform semantic validation, policy validation, optimisation, network apply, runtime assurance, telemetry ingestion, or callback mediation.**

## 17. Lifecycle, status, and versioning baseline:

### 17.1. Intent-level lifecycleStatus:

The overall external Intent lifecycle remains:

```text
Draft
Acknowledged
InProgress
Active
Degraded
Paused
Rejected
Failed
Terminated
```

### 17.2. Intent-version lifecycleStatus:

Individual Intent versions can use:

```text
Acknowledged
InProgress
Active
Standby
Degraded
Paused
Rejected
Failed
Terminated
Retired
```

### 17.3. Version state meanings:

| **Version lifecycleStatus** | **Meaning** |
|---|---|
| `Acknowledged` | Version accepted after schema and request-shape validation |
| `InProgress` | Version change handling is in progress, including semantic resolution, optimisation where applicable, apply/change execution, or assurance confirmation |
| `Active` | Version is currently active in the network or service |
| `Standby` | Version is not currently active, but is retained as a valid rollback or future reactivation candidate |
| `Degraded` | Version is still active, but runtime assurance is degraded |
| `Paused` | Version is temporarily paused where applicable |
| `Rejected` | Version was rejected before successful fulfilment |
| `Failed` | Version failed during fulfilment, apply, or runtime processing |
| `Terminated` | Version was stopped because the Intent or service was terminated |
| `Retired` | Administrative/version-governance archival state; reachable only from `Terminated`; terminal |

### 17.4. Version pointer:

Use:

```json
{
  "activeVersion": "v1"
}
```

Do not use:

```json
{
  "effectiveVersion": "v1"
}
```

or:

```json
{
  "currentVersion": "v1"
}
```

### 17.5. Why `activeVersion`:

| **Term** | **Decision** | **Reason** |
|---|---|---|
| `activeVersion` | Use | Natural and clearly points to the version currently active in the network or service |
| `effectiveVersion` | Do not use | Accurate, but less natural |
| `currentVersion` | Do not use | Ambiguous; could mean latest submitted, latest edited, latest stored, or active |

### 17.6. Lifecycle/status ownership:

IC MS owns the external lifecycle and status projection, not the runtime truth.

Runtime truth comes from:

| **Source** | **Meaning** |
|---|---|
| IC MS | Schema and request-shape admission only |
| II MS | Semantic/policy rejection outcome |
| IA MS | Apply, active, degraded, failed, paused, and runtime assurance outcomes |
| External client/OEX | Termination request |

### 17.7. Lifecycle/versioning example:

| **Step** | **Trigger or event** | **Intent version** | **Version lifecycleStatus** | **Intent activeVersion** | **IC MS external projection** |
|---:|---|---|---|---|---|
| 1 | `POST /intent` with `submit:true` or omitted `submit` passes schema and request-shape validation | `v1` | `Acknowledged` | none | Intent admitted; `IntentValidatedEvent` emitted |
| 2 | Downstream fulfilment starts | `v1` | `InProgress` | none | Intent is being processed |
| 3 | IA MS confirms apply/assurance active | `v1` | `Active` | `v1` | Intent active; `v1` becomes active version |
| 4 | Runtime degradation reported by IA MS | `v1` | `Degraded` | `v1` | Intent degraded, but `v1` remains `activeVersion` |
| 5 | Meaningful update accepted, creates new version | `v2` | `Acknowledged` or `InProgress` | `v1` | New version being processed; service still running on `v1` |
| 6 | IA MS confirms updated apply active | `v2` | `Active` | `v2` | `v2` becomes `activeVersion` |
| 7 | `v2` becomes `activeVersion` | `v1` | `Standby` | `v2` | `v1` no longer active, but remains a rollback or restart candidate |
| 8 | Rollback/restart requested | `v1` | `Acknowledged` | `v2` | `v1` re-enters the Intent version change lifecycle; `v2` remains active until the restart is confirmed |
| 9 | Rollback/restart change execution begins | `v1` | `InProgress` | `v2` | `v1` is being applied; `v2` remains active until the restart is confirmed |
| 10 | Rollback/restart confirmed | `v1` | `Active` | `v1` | `v1` becomes `activeVersion` again; previous active version moves to `Standby` where applicable |
| 11 | Version explicitly terminated | `v2` | `Terminated` | `v1` | `v2` is no longer a restart candidate |
| 12 | Administrative retirement after termination | `v2` | `Retired` | `v1` | `v2` is archived for governance and audit and cannot become active again |

### 17.8. Example JSON — while v2 is still being processed:

```json
{
  "id": "INT-HOSP-2026-001",
  "lifecycleStatus": "InProgress",
  "activeVersion": "v1",
  "versions": [
    {
      "version": "v1",
      "lifecycleStatus": "Active"
    },
    {
      "version": "v2",
      "lifecycleStatus": "InProgress"
    }
  ]
}
```

### 17.9. Example JSON — after v2 becomes active:

```json
{
  "id": "INT-HOSP-2026-001",
  "lifecycleStatus": "Active",
  "activeVersion": "v2",
  "versions": [
    {
      "version": "v1",
      "lifecycleStatus": "Standby"
    },
    {
      "version": "v2",
      "lifecycleStatus": "Active"
    }
  ]
}
```

### 17.10. Example JSON — after rollback or restart to v1 is acknowledged:

```json
{
  "id": "INT-HOSP-2026-001",
  "lifecycleStatus": "InProgress",
  "activeVersion": "v2",
  "versions": [
    {
      "version": "v1",
      "lifecycleStatus": "Acknowledged"
    },
    {
      "version": "v2",
      "lifecycleStatus": "Active"
    }
  ]
}
```

### 17.11. Example JSON — after rollback to v1 is confirmed:

```json
{
  "id": "INT-HOSP-2026-001",
  "lifecycleStatus": "Active",
  "activeVersion": "v1",
  "versions": [
    {
      "version": "v1",
      "lifecycleStatus": "Active"
    },
    {
      "version": "v2",
      "lifecycleStatus": "Standby"
    }
  ]
}
```

### 17.12. Example JSON — after v2 is terminated and then retired from future use:

```json
{
  "id": "INT-HOSP-2026-001",
  "lifecycleStatus": "Active",
  "activeVersion": "v1",
  "versions": [
    {
      "version": "v1",
      "lifecycleStatus": "Active"
    },
    {
      "version": "v2",
      "lifecycleStatus": "Retired"
    }
  ]
}
```

### 17.13. Example JSON — after termination:

```json
{
  "id": "INT-HOSP-2026-001",
  "lifecycleStatus": "Terminated",
  "activeVersion": "v1",
  "versions": [
    {
      "version": "v1",
      "lifecycleStatus": "Terminated"
    },
    {
      "version": "v2",
      "lifecycleStatus": "Retired"
    }
  ]
}
```

### 17.14. Delete or terminate rule:

IC MS does not physically delete runtime `Intent` records by default.

`DELETE /intentManagement/v5/intent/{id}` or equivalent terminate flow is treated as a termination request.

The retained `Intent` record remains available for:

- audit
- reporting
- lifecycle history
- traceability
- existing `IntentReport` references

### 17.15. Final baseline statements:

**Use `activeVersion`, not `effectiveVersion` or `currentVersion`, for the Intent version currently confirmed active in the network or service.**

**When a newer Intent version becomes `Active`, IC MS moves `activeVersion` to the newer version and transitions the previously active version to `Standby`. `Standby` means the version is no longer currently active, but is retained as a valid rollback or future reactivation candidate.**

**`Retired` is an administrative/version-governance archival state. It is terminal and reachable only from `Terminated`; no operational version state moves directly to `Retired`.**

**IC MS does not physically delete runtime `Intent` records by default. Termination transitions the retained Intent projection to `Terminated` for audit, reporting, lifecycle history, and traceability.**

**IC MS must not invent runtime lifecycle truth. It projects external `Intent.lifecycleStatus`, `statusReason`, and `statusChangeDate` based on schema and request-shape admission, II MS rejection outcomes, IA MS assurance outcomes, and accepted termination requests.**

## 18. Intent lifecycle state diagrams:

### 18.1. Purpose:

IC MS lifecycle modelling is split into two related views:

1. Intent-level lifecycle — the external `Intent.lifecycleStatus` that IC MS projects.
2. Intent-version lifecycle — the lifecycle of each runtime Intent version, including `Standby` and `Retired`.

Important rule: `Standby` and `Retired` are version-level states, not overall Intent lifecycle states.

### 18.2. Intent-level lifecycle states:

```text
Draft
Acknowledged
InProgress
Active
Degraded
Paused
Rejected
Failed
Terminated
```

### 18.3. Intent-version lifecycle states:

```text
Acknowledged
InProgress
Active
Standby
Degraded
Paused
Rejected
Failed
Terminated
Retired
```

### 18.4. Key lifecycle rules:

| **Rule** | **Baseline** |
|---|---|
| Submitted schema and request-shape success | Intent or admitted version starts as `Acknowledged` |
| Draft creation with `submit:false` | Intent-level lifecycleStatus is `Draft`; no admitted Intent version is created and `activeVersion` is not driven |
| Semantic/policy rejection | Moves to `Rejected` |
| Fulfilment/apply starts | Moves to `InProgress` |
| Assurance confirms active | Moves to `Active` |
| Runtime degradation | Active version can move to `Degraded` while remaining `activeVersion` |
| Recovery from degradation | `Degraded -> Active` |
| New version becomes active | New version becomes `Active`; previous active version moves to `Standby` |
| Rollback/restart | `Standby -> Acknowledged -> InProgress -> Active`; previous active version moves to `Standby` only after the restarted version becomes active |
| Explicit retirement | Only `Terminated -> Retired`; `Retired` is administrative/version-governance archival state |
| Termination | Intent-level moves to `Terminated`; active version moves to `Terminated`; records retained |
| Physical delete | Not baselined for runtime `Intent` |

### 18.5. Intent-level lifecycle:
![view](ic_ms_intent_lifecycle_state_diagram.svg)

### 18.6. Intent-version lifecycle:
![view](ic_ms_intent_version_lifecycle_state_diagram.svg)

### 18.7. Example activeVersion transition:

```text
v1 Active, activeVersion = v1
-> v2 created, v2 InProgress, activeVersion still v1
-> v2 Active, activeVersion = v2, v1 moves to Standby
-> rollback or restart requested, v1 Acknowledged, activeVersion still v2
-> rollback or restart starts, v1 InProgress, activeVersion still v2
-> rollback or restart confirmed, v1 Active, activeVersion = v1, v2 moves to Standby
```

### 18.8. Baseline statement:

IC MS lifecycle diagrams must keep Intent-level lifecycle and Intent-version lifecycle separate. The external Intent lifecycle is what IC MS projects to callers. Version lifecycle tracks each runtime version and includes `Standby` for rollback/reactivation candidates and `Retired` as a terminal state for versions permanently removed from future active-candidate use.

## 19. External Intent projection and version visibility baseline:

### 19.1. External projection rule:

For the external `Intent` resource, IC MS projects the currently relevant version of that Intent ID.

This means:

- `GET /intent/{id}` returns the current projected version for that Intent ID.
- `GET /intent` lists current projected versions for retained Intent IDs.
- The returned `version` is the projected runtime version.
- IC MS does not return the full internal version aggregate by default.
- Internal version history, `Standby`, `Retired`, rollback candidates, and previous versions remain internal unless exposed through `IntentReport` or a documented platform extension.

### 19.2. GET /intent/{id} example:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001
Accept: application/json
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "version": "v2",
  "lifecycleStatus": "Active",
  "statusReason": "Intent version v2 is active and assurance is healthy.",
  "statusChangeDate": "2026-04-18T12:20:00+10:00",
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec",
    "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### 19.3. Version-history exposure rule:

Internal version history is retained for audit, rollback, assurance correlation, and traceability. Historical versions are not returned by default in the external `Intent` resource.

If needed, version history may be exposed through one of the following:

| **Mechanism** | **Purpose** |
|---|---|
| `IntentReport` | Curated external reporting/history projection |
| Documented platform extension | Explicit version inspection endpoint if required later |
| Internal operational tooling | Operator/debug use without changing external TMF-compliant resource shape |

### 19.4. Baseline statement:

**For the external `Intent` resource, IC MS simply projects the currently relevant version of that Intent ID. `GET /intent/{id}` and `GET /intent` return current projected Intent state, not the full internal version aggregate. The returned `version` is the projected runtime version. Internal version history, `Standby`, `Retired`, rollback candidates, and previous versions remain internal unless exposed through `IntentReport` or a documented platform extension.**

## 20. Operation behaviour and IntentSpecification reference baseline:

### 20.1. IntentSpecification and expression IRI resolution rule:

Submitted runtime `Intent` admission requests must carry both `intentSpecification.id` and `expression.iri`.

The fields serve different purposes:

| **Field** | **Purpose** |
|---|---|
| `intentSpecification.id` | Selects the exact active platform-managed `IntentSpecification` used for validation, governance, lifecycle, and audit. |
| `expression.iri` | Identifies the semantic expression contract claimed by the runtime expression. |

IC MS does not infer the governing runtime validation contract from `expression.iri` alone.

For submitted admission:
- `intentSpecification.id` is mandatory
- `expression.iri` is mandatory
- IC MS resolves the exact `IntentSpecification` by `intentSpecification.id`
- the resolved `IntentSpecification` must be `ACTIVE`
- IC MS validates that the supplied `expression.iri` is consistent with the resolved specification's `expressionSpecification.iri`
- IC MS validates the runtime expression against the resolved active specification
- if `intentSpecification.id` is omitted, IC MS rejects the request
- `intentSpecification.specKey` and `intentSpecification.name` are optional hints only

Draft creation remains light. A Draft Intent can be created with `submit: false` without `intentSpecification.id` or `expression.iri`; those fields become mandatory only when admission is requested. `isBundle` is optional and defaults to `false` when omitted on create.

The baseline surgical hospital slice is an illustrative runtime example used to make the IC MS contract concrete. It is not the only supported runtime Intent type, IntentSpecification, service class, schema, expression IRI, location, service type, or deployment profile. Other runtime Intents may use different targets, constraints, preferences, expression schemas, service types, priorities, and governance profiles while following the same IC MS contract rules.

### 20.2. Two separate version concepts:

| **Version concept** | **Applies to** | **Meaning** |
|---|---|---|
| `IntentSpecification` version | Design-time contract | Which schema or contract validates the runtime Intent |
| `Intent` version | Runtime intent | Which runtime request/config version is projected, active, standby, failed, terminated, or retained |

### 20.3. Operation behaviour:

| **Operation** | **Behaviour** |
|---|---|
| `POST /intent` with `submit: false` | Creates or saves a Draft authoring record. Does not require `intentSpecification.id` or `expression.iri` unless supplied as Draft content. |
| `POST /intent` with `submit: true` or omitted `submit` | Requires both `intentSpecification.id` and `expression.iri`; validates the runtime expression against the selected active specification; creates projected runtime version `v1`. |
| `GET /intent/{id}` | Returns current projected Intent state for that Intent ID, not the full internal version aggregate. |
| `GET /intent` | Lists current projected Intent states for retained Intent IDs. |
| `PUT /intent/{id}` | Platform extension for deterministic full replacement. Allowed only while Draft. If `submit: true` is supplied, requires both `intentSpecification.id` and `expression.iri` for admission. |
| `PATCH /intent/{id}` | TMF-compatible partial update using JSON Merge Patch. Allowed only while Draft. If `submit: true` is supplied, requires both `intentSpecification.id` and `expression.iri`. |
| `DELETE /intent/{id}` | Treated as termination, not physical delete; retained Intent projection moves to `Terminated`. |

### 20.4. Baseline statement:

**Submitted runtime `Intent` admission requires both `intentSpecification.id` and `expression.iri`. `intentSpecification.id` selects the exact active platform-managed specification. `expression.iri` identifies the semantic expression contract and must match the selected specification's `expressionSpecification.iri`. IC MS does not admit by IRI-only resolution.**

**Draft creation remains light. A Draft Intent can be created with `submit: false` without `intentSpecification.id` or `expression.iri`; those fields become mandatory only when admission is requested. `isBundle` is optional and defaults to `false` when omitted on create.**

**`GET` operations return current projected Intent state, not internal version aggregates, and do not resolve or mutate specification versions.**

**`DELETE /intent/{id}` is treated as termination, not physical deletion.**



## 21. Caching, ETag, and dependency-specific circuit-breaker baseline:

### 21.1. Caching scope:

IC MS caching applies only to GET responses.

Caching is baselined for:

```http
GET /intentManagement/v5/intent
GET /intentManagement/v5/intent/{id}
GET /intentManagement/v5/intent/{intentId}/intentReport
GET /intentManagement/v5/intent/{intentId}/intentReport/{reportId}
```

No caching strategy is baselined for non-GET operations.

### 21.2. GET caching behaviour:

For cacheable GET operations, IC MS builds a deterministic cache key from the effective request shape.

The cache key includes:

- request path
- query parameters
- selected `fields` projection
- relevant caller-safe projection context
- any other input that can change the returned representation

When a GET request is received:

1. IC MS builds the cache key for the request.
2. If the request does not include `Cache-Control: no-cache`, IC MS checks the cache for a valid unexpired response for that cache key.
3. If a valid cache entry exists, IC MS may return the cached response directly with the configured `Cache-Control` response header and remaining TTL according to the platform cache-header convention.
4. If no valid cache entry exists, IC MS compiles the response from the source-of-truth store, writes the response to cache with the configured TTL where safe, and returns the response with the configured cache-control headers.

Endpoint-level cache behaviour:

| **Endpoint** | **Cache behaviour** |
|---|---|
| `GET /intent/{id}` | Private bounded TTL; returns current projected Intent version |
| `GET /intent` | Private bounded TTL; shorter TTL for list |
| `GET /intent/{intentId}/intentReport` | Private bounded TTL; short TTL because reports can change with assurance |
| `GET /intent/{intentId}/intentReport/{reportId}` | Private bounded TTL; moderate TTL |

IC MS may refresh or invalidate affected cache entries on write paths or lifecycle and status transitions when it knows the current projection has changed. Examples include Intent create, Draft update, admission, lifecycle and status projection update, IntentReport projection update, termination, and governed report purge.

### 21.3. Client cache override:

Clients can request a fresh GET response using:

```http
Cache-Control: no-cache
```

When `Cache-Control: no-cache` is received, IC MS must bypass any existing cached response for that request, compile the response from the source-of-truth store, refresh the cache entry for the derived cache key where safe, and return the fresh response with normal cache-control headers.

### 21.4. ETag rule:

ETag is used for unsafe-operation concurrency through:

```http
If-Match
```

Applies to:

```http
PUT /intentManagement/v5/intent/{id}
PATCH /intentManagement/v5/intent/{id}
DELETE /intentManagement/v5/intent/{id}
```

`DELETE` is treated as termination, not physical deletion.

### 21.5. Dependency-specific circuit-breaker behaviour:

| **Dependency path** | **CB style** | **Baseline behaviour** |
|---|---|---|
| IC MS -> DB | Hard fail-fast | Return `503`; consumer retries |
| IC MS -> cache | Graceful/silent | Bypass cache or ignore failed cache writes; use DB/source-of-truth; emit telemetry |
| IC MS -> ID MS | Cached active-spec fallback then fail-closed for create/update | Use valid fresh cached active spec where available; otherwise fail closed for runtime-content admission |
| IC MS -> Kafka/event broker | Graceful/silent with internal event outbox | API succeeds after DB + internal event outbox commit; relay retries Kafka later |
| IC MS -> external webhook callback | Async fail-fast per delivery attempt | Delivery attempt fails fast, retries later; original API unaffected |

### 21.6. ID MS dependency rule:

For submitted `POST`, submitted `PUT`, and submitted/runtime-content-changing `PATCH`, IC MS must validate against the resolved `ACTIVE` `IntentSpecification` selected by mandatory `intentSpecification.id`, and must confirm the request `expression.iri` matches the selected specification's `expressionSpecification.iri`.

If ID MS cannot confirm that spec is `ACTIVE`:

| **Situation** | **IC MS behaviour** |
|---|---|
| Valid fresh cached active spec exists | Continue schema and request-shape validation using cache |
| No valid fresh cached active spec | Fail closed; do not admit/create new runtime version |

### 21.7. Failure responses:

DB unavailable:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Retry-After: 30
```

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "reason": "IC_MS_DATABASE_UNAVAILABLE",
  "message": "Intent service is temporarily unavailable because the persistence layer cannot be accessed.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/SERVICE_UNAVAILABLE",
  "@type": "Error"
}
```

Active IntentSpecification cannot be confirmed:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Retry-After: 30
```

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "reason": "INTENT_SPECIFICATION_LOOKUP_UNAVAILABLE",
  "message": "Intent creation or update cannot be accepted because the referenced ACTIVE IntentSpecification could not be confirmed.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/SERVICE_UNAVAILABLE",
  "@type": "Error"
}
```

### 21.8. Baseline statements:

**IC MS caching applies only to GET responses. For cacheable GET operations, IC MS derives a deterministic cache key from the effective request shape, returns a valid unexpired cached response where available, and otherwise compiles the response from the source-of-truth store and refreshes the cache where safe. Clients can bypass cached response serving with `Cache-Control: no-cache`; IC MS then reads from source of truth, refreshes the cache entry where safe, and returns the fresh response. ETag is used only for unsafe-operation concurrency through `If-Match`. No caching strategy is baselined for non-GET operations.**

**For runtime-content admission, IC MS must confirm the resolved `ACTIVE` `IntentSpecification` from ID MS or a valid fresh cached active specification. If it cannot confirm the active specification, IC MS fails closed and does not admit the runtime Intent or runtime version.**

**IC MS uses dependency-specific circuit-breaker behaviour. DB failure is hard fail-fast and returns `503 Service Unavailable`. Cache failure is graceful/silent. Kafka/event-broker failure is handled through internal event outbox. External webhook callback failure is asynchronous and does not affect the original API response.**

## 22. Deployment and persistence strategy:

### 22.1. Runtime and state model:

IC MS is a stateful MS, backed by a managed PostgreSQL-compatible RDBMS. IC MS application instances can still scale independently because durable state is externalised to the database rather than held in local memory.

### 22.2. Source of truth:

The IC MS database is the source of truth for:

- retained `Intent` projections
- internal `IntentVersion` history
- `IntentReport` projections
- hub/event subscriptions where IC MS owns the subscription route
- inbox records for idempotent event consumption
- internal event outbox records for durable Kafka publication
- webhook delivery outbox records for durable HTTP callback delivery
- ETag values
- lifecycle and status projection state
- audit-relevant runtime projection metadata

### 22.3. Recommended persistence model:

| **Table / store** | **Purpose** |
|---|---|
| `intent` | Stores retained external `Intent` projection, current projected version, lifecycle and status, ETag, timestamps, and resource body |
| `intent_version` | Stores internal runtime Intent versions, version lifecycle and status, concrete `IntentSpecification.id`, rollback/standby/retired history, and version payload |
| `intent_report` | Stores external `IntentReport` projections linked to retained `Intent` records |
| `event_subscription` | Stores external event subscriptions where IC MS owns the route |
| `inbox_event` | Stores consumed internal events such as `IntentRejectedEvent` and `IntentAssuranceEvent` for idempotent processing |
| `internal_event_outbox` | Stores internal platform events before Kafka publication, including `IntentValidatedEvent` |
| `webhook_delivery_outbox` | Stores external TMF/webhook notification delivery work before HTTP POST to subscriber callback URLs |
| audit table or audit log | Optional dedicated audit trail if not covered by platform audit capability |

### 22.4. JSONB usage:

Use JSONB where flexible document-shaped content is required.

Recommended JSONB fields:

- external `Intent` resource body snapshot
- internal `IntentVersion` payload
- `IntentReport` body snapshot
- internal event payload snapshot in `internal_event_outbox`
- webhook notification payload snapshot in `webhook_delivery_outbox`
- consumed event snapshot in `inbox_event`
- curated resource/service/evaluation summaries where structure may evolve

Relational columns should still be used for governance and query fields such as `id`, `version`, `lifecycleStatus`, `activeVersion` or projected version, `intentSpecificationId`, `etag`, and timestamps.

### 22.5. Suggested relational columns:

For `intent`:

| **Column** | **Purpose** |
|---|---|
| `id` | Stable Intent ID, for example `INT-HOSP-2026-001` |
| `projected_version` | Current externally projected runtime version |
| `lifecycle_status` | Current external `Intent.lifecycleStatus` |
| `is_bundle` | Server-resolved bundle flag; defaults to `false` when omitted on create |
| `status_reason` | Current external status reason |
| `status_change_date` | Last lifecycle and status projection change timestamp |
| `intent_specification_id` | Concrete `IntentSpecification.id` used by the projected version |
| `etag` | Current ETag for unsafe-operation concurrency |
| `resource_body` | Current external projected `Intent` JSONB representation |
| `created_at` | Creation timestamp |
| `updated_at` | Last update timestamp |
| `terminated_at` | Termination timestamp where applicable |

For `intent_version`:

| **Column** | **Purpose** |
|---|---|
| `intent_id` | Parent Intent ID |
| `version` | Runtime version, for example `v1`, `v2` |
| `version_lifecycle_status` | Version-level status such as `Active`, `Standby`, `Retired`, or `Terminated` |
| `intent_specification_id` | Concrete active `IntentSpecification.id` used for validation |
| `version_body` | Internal version JSONB payload |
| `created_at` | Version creation timestamp |
| `activated_at` | Timestamp when version became active, if applicable |
| `terminated_at` | Timestamp when version was terminated, if applicable |
| `retired_at` | Timestamp when version became retired, if applicable |

### 22.6. Event publication and consumption:

IC MS should use separate durable outbox models for internal Kafka publication and external webhook notification delivery.

Internal events published through the internal event outbox include:

- `IntentValidatedEvent`

External webhook notifications delivered through the webhook delivery outbox include:

- `IntentCreateEvent`
- `IntentAttributeValueChangeEvent`
- `IntentStatusChangeEvent`
- `IntentDeleteEvent`
- `IntentReportCreateEvent`
- `IntentReportAttributeValueChangeEvent`
- `IntentReportDeleteEvent` — governed internal/admin retention or deletion scenarios only

IC MS should use inbox/idempotency handling for consumed internal events, including:

- `IntentRejectedEvent`
- `IntentAssuranceEvent`

### 22.7. High availability and scaling:

IC MS should support:

- multiple application instances
- independent horizontal scaling of application instances
- safe restart behaviour
- no durable state held only in local memory
- rolling deployments
- same-region multi-AZ database configuration where available
- future cross-region active-passive DR support for the database

### 22.8. Disaster recovery:

Initial deployment may be single-region or same-region multi-AZ. The selected database service/deployment pattern must support future cross-region active-passive DR as use cases expand. Active-active multi-region writes are not baselined initially.

### 22.9. Health checks:

| **Health endpoint or check** | **Meaning** |
|---|---|
| Liveness | Process is running and can respond |
| Readiness | Service can access dependencies needed for serving traffic |
| DB readiness | Required for normal IC MS resource operations |
| ID MS readiness for admission | Required for new runtime-content admission unless valid fresh cached active spec exists |
| Kafka/internal outbox relay readiness | Should not block API readiness if DB/outbox commit path is healthy |
| Webhook delivery relay readiness | Should not block API readiness; delivery failures are retried asynchronously |
| Cache readiness | Should not block API readiness because cache failure is graceful/silent |

Readiness should fail when the DB/source-of-truth path is unavailable. Cache failure should not make IC MS unavailable. Kafka/event-broker unavailability should be surfaced through relay metrics/alerts rather than making the IC MS API unavailable when DB/internal outbox commit is healthy. Webhook delivery failures should be surfaced through webhook delivery metrics/alerts and retried asynchronously.

### 22.10. Configuration and secrets:

IC MS configuration should be externalised through platform configuration and secret management.

Examples:

- DB connection settings
- cache endpoint
- Kafka/event broker connection for internal events
- external webhook callback authentication settings
- ID MS lookup endpoint
- active-spec cache TTL values
- internal event outbox relay settings
- webhook delivery outbox relay settings
- inbox/idempotency settings
- retry/backoff settings
- service identity
- OAuth/JWT/security settings where applicable

Secrets must not be stored in application images or source files.

### 22.11. Deployment baseline statement:

**IC MS is a stateful MS, backed by a managed PostgreSQL-compatible RDBMS. IC MS application instances can still scale independently because durable state is externalised to the database rather than held in local memory. The database is the source of truth for retained `Intent` projections, internal `IntentVersion` history, `IntentReport` projections, subscriptions, inbox records, internal event outbox records, webhook delivery outbox records, ETag values, and lifecycle and status projection state.**

## 23. Shared semantic bucket design baseline:

IC MS accepts and projects runtime `Intent` resources using the shared semantic buckets defined by ID MS. External runtime `Intent.expression` uses the TMF expression wrapper.

The domain payload sits inside `expression.expressionValue.context`:

```json
{
  "expression": {
    "@type": "JsonLdExpression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
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
            "startDateTime": "2026-04-18T12:00:00+10:00"
          }
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    }
  }
}
```

Design rules:

- IC MS validates schema and request shape against the active ID MS `IntentSpecification.expressionSpecification` and `targetEntitySchema` contract.
- IC MS preserves the external TMF expression wrapper on TMF-compliant `Intent` resources.
- IC MS emits `IntentValidatedEvent` with the admitted expression as internal native JSON using the same canonical `targets`, `constraints`, and `preferences` buckets, without the external TMF expression wrapper.
- `location`, `serviceType`, and `serviceClass` sit under `context.constraints`; they are not peer fields beside `targets`, `constraints`, and `preferences`.
- IC MS does not perform semantic/KP validation.
- IC MS does not invent optimiser categories; it preserves the bucketed expression for II MS.

## 24. Runtime expression context alignment with ID MS:

IC MS must use the ID MS external runtime expression baseline for runtime Intent create/update/retrieve examples. External `Intent.expression.expressionValue` contains a single `context` object.

The `context` object contains only the canonical semantic buckets:

```text
targets
constraints
preferences
```

`location`, `serviceType`, and `serviceClass` are not peer fields beside those buckets. They sit under `context.constraints` because they restrict what and where the intent must fulfil.

Internal `IntentValidatedEvent.body.expression` carries the admitted expression as native JSON using the same canonical buckets, without the external TMF expression wrapper.

## 25. TMF fields and precondition response alignment:

IC MS supports the optional TMF-aligned `fields` query parameter on create/list/retrieve/update operations where applicable, including `IntentReport` list/retrieve projections.

Unsafe operations requiring optimistic concurrency use `If-Match`. Missing required `If-Match` returns `428 Precondition Required`. Stale or mismatched `If-Match` returns `412 Precondition Failed`.

`DELETE /intent/{id}` remains termination, not physical deletion. The preferred TMF-aligned response for accepted termination is `202 Accepted`; callers can retrieve the retained terminated projection using `GET /intent/{id}`.


## 26. PATCH semantics:

`PATCH` uses JSON Merge Patch semantics across the service's external REST API.

All `PATCH` requests must use:

```http
Content-Type: application/merge-patch+json
```

`PATCH` is intended for small targeted updates. For deterministic full replacement of editable Draft resources, use `PUT` where the platform extension is available.



## 27. Expression schema alignment:

Intent domain expression schemas should align with the TMF Intent Ontology direction and use a scalable JSON-LD-style structure.

Preferred governed `expression.expressionValue` shape:

```json
{
  "@context": {
    "intent": "https://example.com/tio/hospital-surgical-slice/v1.0#",
    "context": "intent:context",
    "targets": "intent:targets",
    "constraints": "intent:constraints",
    "preferences": "intent:preferences"
  },
  "@type": "HospitalSurgicalSliceIntentExpressionValue",
  "context": {
    "targets": [],
    "constraints": [],
    "preferences": []
  }
}
```

Baseline:

- `targetEntitySchema` owns the detailed validation contract.
- `expressionSpecification.iri` identifies the semantic expression contract.
- `specCharacteristic` gives catalogue/discovery summary only.
- Use array-based `targets`, `constraints`, and `preferences` for scalability.
- Keep simplified object-map examples only where they are deliberately explanatory.
