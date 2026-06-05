# IC MS Specification

| **Document status** | **Value** |
| --- | --- |
| Status | Accepted baseline specification |
| Scope | IC MS runtime Intent and IntentReport API specification |
| Source of truth after commit | GitHub `baseline/intent/ic-ms/ic_ms_specification.md` |

## Table of contents:

- [1. API endpoints:](#1-api-endpoints)
  - [1.1. Intent resource APIs:](#11-intent-resource-apis)
  - [1.2. IntentReport APIs:](#12-intentreport-apis)
  - [1.3. Hub subscription APIs:](#13-hub-subscription-apis)
  - [1.4. TMF compliance and platform extension baseline:](#14-tmf-compliance-and-platform-extension-baseline)
- [2. Common conventions:](#2-common-conventions)
  - [2.1. Expression schema alignment:](#21-expression-schema-alignment)
  - [2.2. PATCH semantics:](#22-patch-semantics)
  - [2.3. Runtime IntentSpecification and expression IRI resolution rule:](#23-runtime-intentspecification-and-expression-iri-resolution-rule)
  - [2.4. Intent-level lifecycleStatus values:](#24-intent-level-lifecyclestatus-values)
  - [2.5. Intent-version lifecycleStatus values after admission:](#25-intent-version-lifecyclestatus-values-after-admission)
  - [2.6. LifecycleStatus purpose and projection rule:](#26-lifecyclestatus-purpose-and-projection-rule)
  - [2.7. Draft, submit, and external update rule:](#27-draft-submit-and-external-update-rule)
  - [2.8. Intent version transition rules:](#28-intent-version-transition-rules)
  - [2.9. Termination rule:](#29-termination-rule)
  - [2.10. Caching and ETag rules:](#210-caching-and-etag-rules)
  - [2.11. Typed placeholder rule:](#211-typed-placeholder-rule)
- [3. Common error body:](#3-common-error-body)
  - [3.1. Common errors:](#31-common-errors)
  - [3.2. Missing If-Match response:](#32-missing-if-match-response)
  - [3.3. ETag mismatch response:](#33-etag-mismatch-response)
- [4. Create Intent:](#4-create-intent)
  - [4.1. Request:](#41-request)
  - [4.2. Success response:](#42-success-response)
  - [4.3. Create as Draft example:](#43-create-as-draft-example)
  - [4.4. Create validation rule:](#44-create-validation-rule)
- [5. List Intents:](#5-list-intents)
  - [5.1. Request:](#51-request)
  - [5.2. Request with fresh-read override:](#52-request-with-fresh-read-override)
  - [5.3. Success response:](#53-success-response)
  - [5.4. Query parameters:](#54-query-parameters)
- [6. Retrieve Intent:](#6-retrieve-intent)
  - [6.1. Request:](#61-request)
  - [6.2. Request with fresh-read override:](#62-request-with-fresh-read-override)
  - [6.3. Success response:](#63-success-response)
  - [6.4. Not found response:](#64-not-found-response)
- [7. Full replace Intent:](#7-full-replace-intent)
  - [7.1. Request:](#71-request)
  - [7.2. Success response:](#72-success-response)
  - [7.3. Rule:](#73-rule)
- [8. Partial update Intent:](#8-partial-update-intent)
  - [8.1. Request:](#81-request)
  - [8.2. Success response:](#82-success-response)
  - [8.3. Rule:](#83-rule)
- [9. Terminate Intent:](#9-terminate-intent)
  - [9.1. Request:](#91-request)
  - [9.2. Success response:](#92-success-response)
  - [9.3. Rule:](#93-rule)
- [10. List IntentReports:](#10-list-intentreports)
  - [10.1. Request:](#101-request)
  - [10.2. Request with fresh-read override:](#102-request-with-fresh-read-override)
  - [10.3. Success response:](#103-success-response)
- [11. Retrieve IntentReport:](#11-retrieve-intentreport)
  - [11.1. Request:](#111-request)
  - [11.2. Request with fresh-read override:](#112-request-with-fresh-read-override)
  - [11.3. Success response:](#113-success-response)
  - [11.4. IntentReport delete posture:](#114-intentreport-delete-posture)
  - [11.5. TMF posture:](#115-tmf-posture)
  - [11.6. Event posture:](#116-event-posture)
- [12. Hub create subscription:](#12-hub-create-subscription)
  - [12.1. Strict TMF route request:](#121-strict-tmf-route-request)
  - [12.2. Strict TMF route success response:](#122-strict-tmf-route-success-response)
  - [12.3. Domain-scoped platform extension request:](#123-domain-scoped-platform-extension-request)
  - [12.4. Domain-scoped platform extension success response:](#124-domain-scoped-platform-extension-success-response)
  - [12.5. Supported event filters:](#125-supported-event-filters)
  - [12.6. Hub notification delivery rule:](#126-hub-notification-delivery-rule)
  - [12.7. Example subscriber listener callback:](#127-example-subscriber-listener-callback)
  - [12.8. Subscriber listener success response:](#128-subscriber-listener-success-response)
- [13. Hub retrieve subscription:](#13-hub-retrieve-subscription)
  - [13.1. Request:](#131-request)
  - [13.2. Request with fresh-read override:](#132-request-with-fresh-read-override)
  - [13.3. Success response:](#133-success-response)
- [14. Hub delete subscription:](#14-hub-delete-subscription)
  - [14.1. Request:](#141-request)
  - [14.2. Success response:](#142-success-response)
- [15. Validation and dependency error examples:](#15-validation-and-dependency-error-examples)
  - [15.1. Missing expression IRI:](#151-missing-expression-iri)
  - [15.2. Missing IntentSpecification ID:](#152-missing-intentspecification-id)
  - [15.3. Referenced specification not active:](#153-referenced-specification-not-active)
  - [15.4. IntentSpecification lookup unavailable:](#154-intentspecification-lookup-unavailable)
  - [15.5. ETag mismatch:](#155-etag-mismatch)
  - [15.6. Submitted Intent update not allowed:](#156-submitted-intent-update-not-allowed)
  - [15.7. External event timestamp rule:](#157-external-event-timestamp-rule)
- [16. External Intent event family:](#16-external-intent-event-family)
- [17. IntentCreateEvent:](#17-intentcreateevent)
- [18. IntentAttributeValueChangeEvent:](#18-intentattributevaluechangeevent)
- [19. IntentStatusChangeEvent:](#19-intentstatuschangeevent)
- [20. IntentDeleteEvent:](#20-intentdeleteevent)
- [21. External IntentReport event family:](#21-external-intentreport-event-family)
- [22. IntentReportCreateEvent:](#22-intentreportcreateevent)
- [23. IntentReportAttributeValueChangeEvent:](#23-intentreportattributevaluechangeevent)
- [24. IntentReportDeleteEvent:](#24-intentreportdeleteevent)
- [25. Internal Kafka event publication note:](#25-internal-kafka-event-publication-note)
- [26. Final specification notes:](#26-final-specification-notes)
- [27. Shared semantic bucket baseline:](#27-shared-semantic-bucket-baseline)
  - [27.1. Runtime Intent expression:](#271-runtime-intent-expression)
  - [27.2. Complete POST /intent request body example:](#272-complete-post-intent-request-body-example)
  - [27.3. Complete IntentValidatedEvent body example:](#273-complete-intentvalidatedevent-body-example)
  - [27.4. Baseline rules:](#274-baseline-rules)

**Service identity:**

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Controller MS |
| Short name | IC MS |
| Service name | `intent-controller-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `Intent` |
| Secondary resource | `IntentReport` |
| Primary responsibility | TMF-compliant runtime `Intent` controller, schema and request-shape admission, lifecycle and status projection, and external runtime intent events |

**TMF deployment path note:**

This specification uses `/intentManagement/v5` in examples as the platform base path. A strict TMF gateway exposure may publish the same API under `/tmf-api/intentManagement/v5`. The API gateway may map between the external TMF route prefix and the internal/platform route prefix without changing the resource contract.

**Boundary statement:**

IC MS owns the external runtime `Intent` and `IntentReport` resources.

IC MS validates runtime `Intent` request shape against the applicable `ACTIVE` `IntentSpecification` resolved from mandatory `intentSpecification.id`, with mandatory `expression.iri` used to confirm the semantic/expression contract. IC MS admits schema and request-shape valid runtime intents, emits `IntentValidatedEvent` as an internal state and progress event, projects external lifecycle and status based on downstream outcomes, and exposes curated `IntentReport` projections.

IC MS does not own:

- design-time `IntentSpecification` catalogue
- semantic validation
- policy validation
- optimisation
- network or platform change execution
- apply outcome interpretation
- runtime assurance truth
- real-time telemetry
- callback ingestion
- raw orchestrator callback interpretation

Network or platform change execution is owned by the downstream change execution layer, which may be a network orchestrator or another authorised fulfilment component depending on the Intent domain. IA MS interprets change outcomes and owns runtime assurance truth; IC MS only projects the resulting lifecycle and status changes.

---

## 1. API endpoints:

### 1.1. Intent resource APIs:

| **Purpose** | **Method** | **Endpoint** | **Position** |
|---|---:|---|---|
| Create runtime intent | `POST` | `/intentManagement/v5/intent` | TMF-aligned |
| List runtime intents | `GET` | `/intentManagement/v5/intent` | TMF-aligned |
| Retrieve runtime intent by ID | `GET` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Full replace runtime intent | `PUT` | `/intentManagement/v5/intent/{id}` | Platform extension |
| Partial update runtime intent | `PATCH` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Terminate runtime intent | `DELETE` | `/intentManagement/v5/intent/{id}` | TMF-aligned delete verb, platform behaviour is termination not physical deletion |

### 1.2. IntentReport APIs:

| **Purpose** | **Method** | **Endpoint** | **Position** |
|---|---:|---|---|
| List reports for intent | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport` | Platform/TMF-aligned nested report projection |
| Retrieve report by ID | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport/{id}` | Platform/TMF-aligned nested report projection |

### 1.3. Hub subscription APIs:

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

Hub subscriptions are REST webhook subscriptions. IC MS stores subscriber callback registrations and delivers subscribed external `Intent` and `IntentReport` event notifications by HTTP `POST` to the subscriber listener callback URL. Kafka is not used for external hub notification delivery. Delivery reliability is handled by an IC MS-owned local webhook delivery outbox and HTTP retry relay.

IC MS therefore has two separate event-delivery paths:

| Delivery path | Purpose | Transport | Durability model | Headers | Payload |
|---|---|---|---|---|---|
| Internal platform events | Publish internal state and progress events such as `IntentValidatedEvent` to independent internal consumers. | Kafka. | IC MS internal event outbox and Kafka relay. | CloudEvents-style Kafka/platform event headers. | Internal event JSON body. |
| External TMF/webhook notifications | Notify registered hub subscribers about consumer-safe `Intent` and `IntentReport` events. | HTTP `POST` to subscriber listener callback URL. | IC MS webhook delivery outbox and HTTP retry relay. | HTTP headers. | TMF-aligned event request body. |

---

### 1.4. TMF compliance and platform extension baseline:

IC MS exposes response classification header and maintains a documented set of strict TMF-compatible operations and approved platform extensions.

#### 1.4.1. Response classification headers:

IC MS returns a response classification header on external REST API responses so callers can distinguish strict TMF-aligned behaviour from documented platform-extension behaviour.

This is a response header only. Clients do not send this header in requests.

| **Response header** | **Meaning** |
|---|---|
| `X-Platform-Extension: true` | The route, method, response, or behaviour includes a documented platform extension. |
| `X-Platform-Extension: false` | No platform extension is used for the response. |

Header classification guidance:

| **IC MS response area** | **X-Platform-Extension** | **Reason** |
|---|---:|---|
| `POST /intent`, `GET /intent`, `GET /intent/{id}`, `PATCH /intent/{id}` using strict TMF-compatible behaviour | `false` | TMF-compatible Intent resource operations. |
| `POST /intent` or `PATCH /intent/{id}` using `submit` Draft/admission control | `true` | `submit` is an IC MS request-control extension. |
| `PUT /intent/{id}` | `true` | Deterministic full replacement is a platform extension. |
| `DELETE /intent/{id}` termination/retention response | `true` | The verb is TMF-compatible, but retained termination behaviour is platform-specific. |
| `GET /intent/{intentId}/intentReport`, `GET /intent/{intentId}/intentReport/{id}` | `false` | TMF-aligned read-only report projection. |
| Strict `/hub` create/delete responses | `false` | Strict TMF hub route family. |
| Domain-scoped `/intent/hub` responses | `true` | Domain-owned hub route family is a platform extension. |

Example strict TMF-aligned response classification header:

```http
X-Platform-Extension: false
```

Example platform-extension response classification header:

```http
X-Platform-Extension: true
```


IC MS keeps the external `Intent` and `IntentReport` contract TMF-aligned while documenting controlled platform extensions explicitly.

#### 1.4.2. Strict TMF-compatible operations:

| **Capability** | **Route family** | **Position** |
|---|---|---|
| Runtime Intent create/list/retrieve | `POST /intent`, `GET /intent`, `GET /intent/{id}` | TMF-compatible |
| Runtime Intent partial update | `PATCH /intent/{id}` | TMF-compatible |
| Runtime Intent delete verb | `DELETE /intent/{id}` | TMF-compatible verb; platform behaviour is termination and retention, not physical deletion |
| IntentReport list/retrieve | `GET /intent/{intentId}/intentReport`, `GET /intent/{intentId}/intentReport/{id}` | TMF-aligned nested report projection |
| Hub subscription create/delete | `POST /hub`, `DELETE /hub/{id}` | Strict TMF route family |

#### 1.4.3. Accepted platform extensions:

| **Extension** | **Reason** |
|---|---|
| `PUT /intent/{id}` | Deterministic full replacement for runtime Intent edits where `PATCH` is too ambiguous |
| `/intent/hub` domain-scoped hub routes | Domain-owned subscription surface for external Intent and IntentReport events |
| `GET /intent/hub/{id}` | Operational convenience for retrieving a domain-scoped subscription; not part of the strict TMF minimum hub route set |
| `_links` | Lifecycle-aware and authorisation-aware HATEOAS controls |
| Strong `ETag` / `If-Match` governance | Optimistic concurrency for unsafe operations |
| `428 Precondition Required` | Explicit response when required `If-Match` is missing |
| Termination-retention behaviour for `DELETE /intent/{id}` | Runtime Intent records remain available for audit, reporting, lifecycle history, and traceability |
| Ordinary external `IntentReport` delete not exposed | `IntentReport` is read-only curated projection/audit history for ordinary consumers; governed/admin removal remains internal or restricted |

Hub notification delivery is REST webhook delivery to subscriber listener callback URLs. IC MS does not create a Kafka topic or self-publish/self-consume Kafka events for external hub notifications.

---

## 2. Common conventions:

### 2.1. Expression schema alignment:

The long-term canonical expression-value schema pattern for the Intent domain should align with the TMF Intent Ontology direction and use a scalable JSON-LD-style structure.

For governed `targetEntitySchema` definitions, prefer this top-level shape:

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

Canonical schema direction:

- use `@context` for JSON-LD vocabulary and term mapping
- use `@type` for the expression-value type
- use `context.targets[]` for measurable goals or target outcomes
- use `context.constraints[]` for hard requirements
- use `context.preferences[]` for soft selection guidance
- allow the active `IntentSpecification.targetEntitySchema` to specialise permitted target, constraint, and preference entry types

Simplified object-map payloads may still appear in minimum-data explanation examples where readability matters, but they are not the preferred long-term canonical schema shape for governed `targetEntitySchema` definitions.



### 2.2. PATCH semantics:

`PATCH` uses JSON Merge Patch semantics.

All external `PATCH` request examples must use:

```http
Content-Type: application/merge-patch+json
```

`PATCH` is intended for small targeted updates. For deterministic full replacement of editable Draft resources, use `PUT` where the platform extension is available.



### 2.3. Runtime IntentSpecification and expression IRI resolution rule:

Submitted runtime `Intent` admission requests must carry both `intentSpecification.id` and `expression.iri`.

These fields serve different purposes:

| **Field** | **Purpose** |
|---|---|
| `intentSpecification.id` | Selects the exact active platform-managed `IntentSpecification` used for validation, governance, and audit. |
| `expression.iri` | Identifies the semantic/expression contract claimed by the runtime expression. |

For submitted admission, `intentSpecification.id` is mandatory. IC MS does not infer the governing runtime validation contract from `expression.iri` alone.

`expression.iri` is also mandatory because it identifies the expression language / ontology / expression contract used for runtime expression validation. IC MS must confirm that the runtime `expression.iri` is consistent with the selected specification's `expressionSpecification.iri`.

`intentSpecification.specKey` and `intentSpecification.name` are optional descriptive/discovery hints only. They are not mandatory and are not authoritative runtime validation keys. If supplied, IC MS may use them for consistency checking or narrowing where supported, but they must not replace `intentSpecification.id`.

Required submitted admission reference:

```json
{
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec"
  },
  "expression": {
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  }
}
```

Unsupported admission request because `intentSpecification.id` is missing:

```json
{
  "expression": {
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  }
}
```

IC MS must not resolve `IntentSpecification` by IRI alone, `specKey`, name, or inferred payload shape alone for submitted runtime admission.

The baseline surgical hospital slice is an illustrative runtime example used to make the IC MS contract concrete. It is not the only supported runtime Intent type, IntentSpecification, service class, schema, expression IRI, location, service type, or deployment profile. Other runtime Intents may use different targets, constraints, preferences, expression schemas, service types, priorities, and governance profiles while following the same IC MS contract rules.

Baseline:
- submitted admission requires `intentSpecification.id`
- submitted admission requires `expression.iri`
- IC MS resolves the exact `ACTIVE` `IntentSpecification` by `intentSpecification.id`
- IC MS rejects the admission request if `intentSpecification.id` is omitted
- IC MS confirms the request `expression.iri` matches the selected specification's `expressionSpecification.iri`
- `intentSpecification.specKey` and `intentSpecification.name` are optional hints only


### 2.4. Intent-level lifecycleStatus values:

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

### 2.5. Intent-version lifecycleStatus values after admission:

```text
Acknowledged
InProgress
Active
Degraded
Paused
Standby
Rejected
Failed
Terminated
Retired
```

### 2.6. LifecycleStatus purpose and projection rule:

`Intent.lifecycleStatus` is the externally visible lifecycle projection for the `Intent` resource. It keeps TMF-facing clients simple by exposing the current public state of the Intent rather than every historical or candidate version state.

Each internal Intent version also has its own version-level `lifecycleStatus`. Version-level lifecycle state is used for version history, restart/reuse decisions, audit, governance, and safe handling of previous versions while another version is the `activeVersion`.

`activeVersion` is the pointer to the Intent version currently driving the top-level `Intent.lifecycleStatus` projection. Do not use `effectiveVersion` or `currentVersion` for this pointer.

`GET /intent/{id}` returns the current projected `Intent` state for that Intent ID. It does not return the full internal version aggregate by default. The returned `version` is the projected runtime version.

Historical version state such as `Standby`, `Retired`, rollback candidates, and previous versions remains internal unless exposed through `IntentReport` or a documented platform extension.

### 2.7. Draft, submit, and external update rule:

External consumers must not set or patch `lifecycleStatus`. `lifecycleStatus` is assigned, transitioned, and projected by the intent management entity. IA MS determines assurance/runtime meaning and IC MS exposes the projected TMF-facing lifecycle state.

`submit` is an approved IC MS extension request-control field. It is not a lifecycle field. `submit: false` requests that the Intent be saved or kept as `Draft`. `submit: true` requests submission for admission.

If `submit` is omitted on initial create, IC MS treats the request as `submit: true`. If an Intent is persisted with `submit: false`, later omission of `submit` must preserve draft handling and must not automatically submit the Intent. A draft Intent is submitted only when a later request explicitly sets `submit: true`.

While `lifecycleStatus = Draft`, all attributes accepted by the `PUT` and `PATCH` request contract are mutable. The `PUT` and `PATCH` request contract must not expose `lifecycleStatus` as a writable attribute.

`id` is immutable. If `id` appears in a full-replacement `PUT` request, it must match the path `id` and is used only for consistency checking; it cannot be changed.

Response/projection fields such as `href`, `version`, `lifecycleStatus`, `statusReason`, `statusChangeDate`, `activeVersion`, and `_links` are not writable request fields unless explicitly documented otherwise.

`isBundle` is optional in create and update request bodies. If omitted on create, IC MS defaults `isBundle` to `false`. Persisted Intent responses include the server-resolved `isBundle` value.

Once an Intent leaves `Draft`, general attribute update on that submitted version is not allowed. Material changes after submission require creating a new Draft authoring record, editing that Draft authoring record, and explicitly submitting it with `submit: true`.

Draft Intents are authoring records only. They are not admitted, optimised, assured, sent to downstream change execution, or used to drive `activeVersion`.

### 2.8. Intent version transition rules:

IC MS must not create another newer version while there is already a newer candidate version in `Acknowledged` or `InProgress`. These states represent an admitted version change that has not yet resolved.

When a newer version becomes the `activeVersion`, previous versions transition as follows:

| Previous version lifecycleStatus | Transition when newer version becomes `activeVersion` |
|---|---|
| `Active` | `Standby` |
| `Degraded` | `Standby` |
| `Paused` | `Standby` |
| `Rejected` | `Terminated` |
| `Failed` | `Terminated` |

`Standby` is a non-active retained version state. It may later re-enter the Intent version change lifecycle only through `Acknowledged`, then `InProgress`, then `Active`. `Standby` may also be explicitly moved to `Terminated`.

`Retired` is an administrative/version-governance archival state. It is reachable only from `Terminated`; it is not a runtime/network operational state and is not exposed as an ordinary external API action.

### 2.9. Termination rule:

`DELETE /intent/{id}` is treated as termination, not physical deletion.

Runtime `Intent` records are retained for audit, reporting, lifecycle history, and traceability.

### 2.10. Caching and ETag rules:

Caching applies only to GET responses.

For cacheable GET operations, IC MS builds a deterministic cache key from the effective request shape, including:

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

Clients may bypass cached response serving using:

```http
Cache-Control: no-cache
```

When `Cache-Control: no-cache` is received, IC MS must bypass any existing cached response for that request, compile the response from the source-of-truth store, refresh the cache entry for the derived cache key where safe, and return the fresh response with normal cache-control headers.

IC MS may also invalidate or refresh affected cache entries on write paths or lifecycle and status transitions when it knows cached projections have become stale. Examples include Intent create, Draft update, admission, lifecycle and status projection update, IntentReport projection update, termination, and governed report purge.

ETag is used only for unsafe-operation concurrency through:

```http
If-Match
```

ETag is not used for GET revalidation in this baseline. `If-None-Match` and `304 Not Modified` are not baselined.

No caching strategy is baselined for non-GET operations.

### 2.11. Typed placeholder rule:

When examples abbreviate large repeated sections, keep the field’s real JSON type.

Use array placeholders for arrays and object placeholders for objects.

Example:

```json
{
  "resources": [
    {
      "resourceId": "SYD-PRI-01",
      "roles": [
        "primary"
      ],
      "resourceType": "networkPath",
      "resourceClass": "critical-gold-access",
      "metrics": {
        "benchmark": {
          "latencyMs": 7,
          "availabilityPercent": 99.996,
          "jitterMs": 1.1,
          "packetLossPercent": 0.004
        }
      }
    }
  ],
  "evaluationSummary": {
    "status": "COMPLETED",
    "statusReason": "Selected resource set satisfies the resolved targets and constraints."
  }
}
```

Do not use string placeholders for array/object fields.

---

## 3. Common error body:

```json
{
  "code": "...",
  "reason": "...",
  "message": "...",
  "status": 400,
  "referenceError": "https://mycsp.com.au/errors/...",
  "@type": "Error"
}
```

### 3.1. Common errors:

| **HTTP** | **Code** | **Scenario** |
|---:|---|---|
| `400` | `BAD_REQUEST` | Invalid JSON or invalid request structure |
| `404` | `RESOURCE_NOT_FOUND` | Intent, IntentReport, or subscription not found |
| `409` | `INVALID_STATE_TRANSITION` | Requested lifecycle/version transition is not allowed |
| `409` | `RESOURCE_CONFLICT` | Runtime update conflicts with current projection state |
| `412` | `PRECONDITION_FAILED` | Supplied `If-Match` does not match the current resource representation |
| `422` | `VALIDATION_FAILED` | Runtime Intent fails request-shape or specification validation, misses mandatory `intentSpecification.id`, misses mandatory `expression.iri`, or has an IRI/specification mismatch |
| `422` | `INTENT_SPECIFICATION_NOT_ACTIVE` | Referenced IntentSpecification is not active |
| `428` | `PRECONDITION_REQUIRED` | Required `If-Match` header is missing for an unsafe operation |
| `503` | `SERVICE_UNAVAILABLE` | IC MS DB unavailable or active spec cannot be confirmed |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

### 3.2. Missing If-Match response:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_REQUIRED",
  "reason": "IF_MATCH_REQUIRED",
  "message": "The If-Match header is required for this operation.",
  "status": 428,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_REQUIRED",
  "@type": "Error"
}
```

### 3.3. ETag mismatch response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied ETag does not match the current resource representation.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

## 4. Create Intent:

### 4.1. Request:

```http
POST /intentManagement/v5/intent?fields=id,href,name,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,expression,validFor,isBundle,priority,relatedParty,@type,@baseType
Content-Type: application/json
Accept: application/json
```

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "submit": true,
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec"
  },
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
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
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### 4.2. Success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intent/INT-HOSP-2026-001
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
ETag: "intent-INT-HOSP-2026-001-v1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "submit": true,
  "version": "v1",
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Intent request accepted for semantic validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec",
    "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
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
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH"
    }
  }
}
```

### 4.3. Create as Draft example:

A caller can create an Intent as a draft by setting `submit: false`. A Draft Intent is persisted for authoring only and is not admitted, optimised, assured, or sent to downstream change execution.

```http
POST /intentManagement/v5/intent?fields=id,href,name,humanExpression,submit,lifecycleStatus,statusReason,statusChangeDate,isBundle,@type,@baseType
Content-Type: application/json
Accept: application/json
```

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms.",
  "submit": false,
  "@type": "Intent",
  "@baseType": "Entity"
}
```

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intent/INT-HOSP-2026-001
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
ETag: "intent-INT-HOSP-2026-001-v1"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms.",
  "submit": false,
  "lifecycleStatus": "Draft",
  "statusReason": "Intent saved as draft and not submitted for admission.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "isBundle": false,
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### 4.4. Create validation rule:

If `submit` is omitted on create, IC MS treats the request as submitted for admission.

If `submit: false` is supplied, IC MS persists the Intent as `Draft` and does not emit `IntentValidatedEvent`, optimise, assure, or send the Intent to downstream change execution.

If `submit: true` is supplied, IC MS applies the runtime admission profile. IC MS emits `IntentValidatedEvent` after schema and request-shape validation succeeds and the external Intent projection is persisted.

If `isBundle` is omitted on create, IC MS defaults it to `false`. If supplied, it must be boolean. Persisted responses include the server-resolved value.

`IntentValidatedEvent` is a state and progress event, not a point-to-point command for a specific consumer.

---

## 5. List Intents:

### 5.1. Request:

```http
GET /intentManagement/v5/intent?offset=0&limit=10&lifecycleStatus=Active&fields=id,href,name,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,@type,@baseType
Accept: application/json
```

### 5.2. Request with fresh-read override:

```http
GET /intentManagement/v5/intent?offset=0&limit=10&lifecycleStatus=Active&fields=id,href,name,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### 5.3. Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
X-Total-Count: 1
X-Result-Count: 1
ETag: "intent-list-active-v21"
Cache-Control: private, max-age=60
```

```json
[
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
      "specKey": "hospital-surgical-slice-spec"
    },
    "@type": "Intent",
    "@baseType": "Entity"
  }
]
```

### 5.4. Query parameters:

| **Parameter** | **Meaning** |
|---|---|
| `offset` | Zero-based start position |
| `limit` | Maximum number of records |
| `fields` | Optional TMF-aligned field selection / projection parameter |
| `lifecycleStatus` | Filter by projected external lifecycle status |
| `version` | Filter by projected runtime version |
| `intentSpecification.id` | Filter by concrete IntentSpecification ID |

---

## 6. Retrieve Intent:

### 6.1. Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001?fields=id,href,name,description,humanExpression,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,expression,validFor,isBundle,priority,relatedParty,@type,@baseType
Accept: application/json
```

### 6.2. Request with fresh-read override:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001?fields=id,href,name,description,humanExpression,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,expression,validFor,isBundle,priority,relatedParty,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### 6.3. Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v3"
Last-Modified: Sat, 18 Apr 2026 02:20:00 GMT
Cache-Control: private, max-age=300
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "version": "v2",
  "lifecycleStatus": "Active",
  "statusReason": "Intent version v2 is active and assurance is healthy.",
  "statusChangeDate": "2026-04-18T12:20:00+10:00",
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec",
    "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 8,
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
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    }
  }
}
```

### 6.4. Not found response:

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "reason": "INTENT_NOT_FOUND",
  "message": "Intent INT-HOSP-2026-001 was not found.",
  "status": 404,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",
  "@type": "Error"
}
```

---

## 7. Full replace Intent:

### 7.1. Request:

```http
PUT /intentManagement/v5/intent/INT-HOSP-2026-001?fields=id,href,name,description,humanExpression,submit,intentSpecification,expression,validFor,isBundle,priority,relatedParty,@type,@baseType
Content-Type: application/json
Accept: application/json
If-Match: "intent-INT-HOSP-2026-001-v3"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Updated surgical connection request with lower latency target.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 8 ms and availability at least 99.99%.",
  "submit": false,
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec"
  },
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 8,
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
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### 7.2. Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v4"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Updated surgical connection request with lower latency target.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 8 ms and availability at least 99.99%.",
  "submit": false,
  "lifecycleStatus": "Draft",
  "statusReason": "Draft intent updated and not submitted for admission.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec",
    "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 8,
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
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH"
    }
  }
}
```

### 7.3. Rule:

`PUT` is a platform extension for deterministic full replacement.

`PUT` is allowed only while the current Intent/Draft projection is in `Draft`.

For a Draft Intent, all attributes accepted by the `PUT` request contract are mutable. The request contract does not expose `lifecycleStatus` as writable.

`id` is immutable. If `id` is supplied in the `PUT` body, it must match the path `id`; otherwise IC MS returns `409 Conflict` or `400 Bad Request` depending on validation policy.

If `submit: false` is supplied or `submit` is omitted on an existing Draft Intent, the Intent remains `Draft`.

If `submit: true` is supplied, IC MS validates the runtime admission profile and, if accepted, moves the projected lifecycle to `Acknowledged`.

Once an Intent leaves `Draft`, full replacement on that submitted version is not allowed. Material changes require creating a new Draft authoring record.

---

## 8. Partial update Intent:

### 8.1. Request:

```http
PATCH /intentManagement/v5/intent/INT-HOSP-2026-001?fields=id,href,name,submit,intentSpecification,expression,validFor,isBundle,priority,@type,@baseType
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "intent-INT-HOSP-2026-001-v4"
```

```json
{
  "submit": false,
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 7
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

### 8.2. Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v5"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Patched surgical connection request with lower latency target.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "submit": false,
  "lifecycleStatus": "Draft",
  "statusReason": "Draft intent patched and not submitted for admission.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec",
    "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 7,
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
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH"
    }
  }
}
```

### 8.3. Rule:

`PATCH` is supported for TMF compatibility but is not encouraged for ordinary edits where deterministic full replacement through `PUT` is available.

`PATCH` is allowed only while the current Intent/Draft projection is in `Draft`.

For a Draft Intent, all attributes accepted by the `PATCH` request contract are mutable. The request contract does not expose `id` or `lifecycleStatus` as writable patch attributes.

If `submit: false` is supplied or `submit` is omitted on an existing Draft Intent, the Intent remains `Draft`.

If `submit: true` is supplied, IC MS validates the runtime admission profile and, if accepted, moves the projected lifecycle to `Acknowledged`.

Once an Intent leaves `Draft`, partial update on that submitted version is not allowed. Material changes require creating a new Draft authoring record.

---

## 9. Terminate Intent:

### 9.1. Request:

```http
DELETE /intentManagement/v5/intent/INT-HOSP-2026-001
Accept: application/json
If-Match: "intent-INT-HOSP-2026-001-v5"
```

### 9.2. Success response:

```http
HTTP/1.1 202 Accepted
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v6"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "lifecycleStatus": "Terminated",
  "statusReason": "Intent termination requested and accepted.",
  "statusChangeDate": "2026-04-18T13:00:00+10:00",
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### 9.3. Rule:

`DELETE /intent/{id}` is treated as termination, not physical deletion.

The retained Intent record remains available for audit, reporting, lifecycle history, and traceability.

`202 Accepted` is used for TMF-aligned delete/termination acceptance. Callers can use `GET /intent/{id}` to retrieve the retained terminated projection after the termination request is accepted.

---

## 10. List IntentReports:

### 10.1. Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport?fields=id,href,creationDate,name,intent,expression,@type,@baseType
Accept: application/json
```

### 10.2. Request with fresh-read override:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport?fields=id,href,creationDate,name,intent,expression,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### 10.3. Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
X-Total-Count: 1
X-Result-Count: 1
ETag: "intent-report-list-INT-HOSP-2026-001-v3"
Cache-Control: private, max-age=60
```

```json
[
  {
    "id": "IR-INT-HOSP-2026-001-003",
    "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
    "creationDate": "2026-04-18T12:20:00+10:00",
    "name": "Sydney Hospital Surgical Connection Intent Report",
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "expression": {
      "@type": "JsonLdExpression",
      "@baseType": "Expression",
      "iri": "https://mycsp.com.au/tio/hospital-surgical-slice-report/v1.0",
      "expressionValue": {
        "version": "v2",
        "lifecycleStatus": "Active",
        "reportTime": "2026-04-18T12:20:00+10:00",
        "summary": "Intent is active and assurance is healthy.",
        "targetSummary": {
          "targets": [
            {
              "name": "maxLatencyMs",
              "target": 10,
              "observedValue": 8,
              "unit": "ms"
            }
          ]
        },
        "observationSummary": {
          "observedAt": "2026-04-18T12:20:00+10:00"
        }
      }
    },
    "@type": "IntentReport",
    "@baseType": "Entity",
    "_links": {
      "self": {
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003"
      },
      "intent": {
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      }
    }
  }
]
```

---

## 11. Retrieve IntentReport:

### 11.1. Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003?fields=id,href,creationDate,name,intent,expression,@type,@baseType
Accept: application/json
```

### 11.2. Request with fresh-read override:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003?fields=id,href,creationDate,name,intent,expression,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### 11.3. Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003
ETag: "intent-report-IR-INT-HOSP-2026-001-003-v1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "IR-INT-HOSP-2026-001-003",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
  "creationDate": "2026-04-18T12:20:00+10:00",
  "name": "Sydney Hospital Surgical Connection Intent Report",
  "intent": {
    "id": "INT-HOSP-2026-001",
    "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice-report/v1.0",
    "expressionValue": {
      "version": "v2",
      "lifecycleStatus": "Active",
      "reportTime": "2026-04-18T12:20:00+10:00",
      "summary": "Intent is active and assurance is healthy.",
      "serviceSummary": {
        "locationId": "AU-NSW-SYD-HOSP-001",
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold"
      },
      "targetSummary": {
        "targets": [
          { "name": "maxLatencyMs", "target": 10, "observedValue": 8, "unit": "ms" },
          { "name": "minAvailabilityPercent", "target": 99.99, "observedValue": 99.995, "unit": "percent" },
          { "name": "maxJitterMs", "target": 2, "observedValue": 1.5, "unit": "ms" },
          { "name": "maxPacketLossPercent", "target": 0.01, "observedValue": 0.005, "unit": "percent" }
        ]
      },
      "observationSummary": {
        "observedAt": "2026-04-18T12:20:00+10:00",
        "resources": [
          {
            "resourceId": "SYD-PRI-01",
            "role": "primary",
            "metrics": {
              "latencyMs": 8,
              "availabilityPercent": 99.995,
              "jitterMs": 1.5,
              "packetLossPercent": 0.005
            }
          },
          {
            "resourceId": "SYD-SEC-01",
            "role": "secondary",
            "metrics": {
              "latencyMs": 10,
              "availabilityPercent": 99.994,
              "jitterMs": 1.8,
              "packetLossPercent": 0.006
            }
          }
        ]
      }
    }
  },
  "@type": "IntentReport",
  "@baseType": "Entity",
  "_links": {
    "self": { "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003" },
    "intent": { "href": "/intentManagement/v5/intent/INT-HOSP-2026-001" },
    "list": { "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport" }
  }
}
```

---

### 11.4. IntentReport delete posture:

IC MS does not expose ordinary external `DELETE /intentManagement/v5/intent/{intentId}/intentReport/{id}` through NGW or public TMF-compliant consumer APIs by default.

External consumers can list and retrieve `IntentReport` records only. `IntentReport` is a read-only curated report/projection/audit resource for ordinary consumers. It represents externalised assurance and lifecycle reporting history derived from IA MS assurance truth, not a mutable business resource with an independent lifecycle.

IC MS may provide an internal-only governed delete/purge capability for `IntentReport` records. This internal capability is not routed through NGW, not advertised as a public consumer API, and not available to normal external consumers. It is restricted to retention purge, legal deletion, platform administration, approved data-correction workflows, or policy-governed cleanup.

### 11.5. TMF posture:

TMF921 includes an `IntentReport` delete operation and `IntentReportDeleteEvent` in the API/event model. IC MS intentionally does not expose the delete operation to ordinary external consumers because deleting reports as a normal consumer action would remove audit/projection history and would require introducing a separate report lifecycle such as `Archived` or `Deleted`.

No separate `IntentReport` lifecycle is baselined for ordinary consumer use. Delete/purge is treated as a governed administrative operation, not a normal report lifecycle transition.

If an implementation must expose the TMF report delete route for compatibility, it must be restricted/admin-only or return a policy error such as `403 Forbidden` or `405 Method Not Allowed` for ordinary consumers, depending on gateway/API policy.

### 11.6. Event posture:

`IntentReportDeleteEvent` remains part of the external TMF-aligned event vocabulary for `IntentReport` alignment.

IC MS emits `IntentReportDeleteEvent` only after successful governed internal/admin removal, where notification is allowed by policy. Valid trigger examples include retention purge, legal deletion, platform administration, approved data correction, or policy-governed cleanup.

`IntentReportDeleteEvent` is not emitted as the result of ordinary external consumer delete because ordinary external consumer delete is not exposed.

---


---

## 12. Hub create subscription:

### 12.1. Strict TMF route request:

```http
POST /intentManagement/v5/hub
Content-Type: application/json
Accept: application/json
```

```json
{
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription"
}
```

### 12.2. Strict TMF route success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/hub/sub-intent-001
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
ETag: "subscription-sub-intent-001-v1"
```

```json
{
  "id": "sub-intent-001",
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/hub/sub-intent-001"
    }
  }
}
```

### 12.3. Domain-scoped platform extension request:

```http
POST /intentManagement/v5/intent/hub
Content-Type: application/json
Accept: application/json
```

```json
{
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription"
}
```

### 12.4. Domain-scoped platform extension success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intent/hub/sub-intent-001
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
ETag: "subscription-sub-intent-001-v1"
```

```json
{
  "id": "sub-intent-001",
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/hub/sub-intent-001"
    }
  }
}
```

### 12.5. Supported event filters:

```text
IntentCreateEvent
IntentAttributeValueChangeEvent
IntentStatusChangeEvent
IntentDeleteEvent
IntentReportCreateEvent
IntentReportAttributeValueChangeEvent
IntentReportDeleteEvent
```

`IntentReportDeleteEvent` is included in the subscription vocabulary for TMF alignment, but is emitted only for governed internal/admin retention or deletion scenarios, not ordinary external consumer delete.

### 12.6. Hub notification delivery rule:

Subscribed notifications are delivered as REST webhook callbacks. IC MS sends an HTTP `POST` to the subscriber callback URL using the corresponding external TMF-aligned event payload as the request body. Kafka and CloudEvents headers are not used for this external hub delivery path. Webhook requests use HTTP headers such as `Content-Type`, `X-Correlation-Id`, and subscriber-specific authentication headers where configured.

IC MS records pending webhook deliveries in an IC MS-owned local delivery outbox and retries delivery according to platform retry policy. A subscriber listener should return `204 No Content` when the notification is accepted.

### 12.7. Example subscriber listener callback:

```http
POST https://consumer.example.com/listener/intent/events HTTP/1.1
Content-Type: application/json
X-Correlation-Id: corr-intent-status-001
```

```json
{
  "eventId": "evt-intent-status-001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "timeOccurred": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentStatusChangeEvent",
  "correlationId": "corr-intent-status-001",
  "description": "Intent lifecycle status changed.",
  "priority": "Normal",
  "title": "Intent status changed",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v2",
      "lifecycleStatus": "Active",
      "@type": "Intent",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentStatusChangeEvent"
}
```

### 12.8. Subscriber listener success response:

```http
HTTP/1.1 204 No Content
```

---

## 13. Hub retrieve subscription:

### 13.1. Request:

```http
GET /intentManagement/v5/intent/hub/sub-intent-001
Accept: application/json
```

### 13.2. Request with fresh-read override:

```http
GET /intentManagement/v5/intent/hub/sub-intent-001
Accept: application/json
Cache-Control: no-cache
```

### 13.3. Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
ETag: "subscription-sub-intent-001-v1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "sub-intent-001",
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/hub/sub-intent-001"
    }
  }
}
```

---

## 14. Hub delete subscription:

### 14.1. Request:

```http
DELETE /intentManagement/v5/intent/hub/sub-intent-001
If-Match: "subscription-sub-intent-001-v1"
```

### 14.2. Success response:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
X-Platform-Extension: true
```

---

## 15. Validation and dependency error examples:

### 15.1. Missing expression IRI:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "EXPRESSION_IRI_REQUIRED",
  "message": "Runtime Intent create/update requests must include expression.iri so IC MS can resolve the applicable expression contract for runtime validation.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### 15.2. Missing IntentSpecification ID:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "INTENT_SPECIFICATION_ID_REQUIRED",
  "message": "Submitted runtime Intent admission requires intentSpecification.id to identify the intended active runtime validation contract.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### 15.3. Referenced specification not active:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "INTENT_SPECIFICATION_NOT_ACTIVE",
  "message": "Referenced IntentSpecification ispec-hss-001 version 1.20 is not ACTIVE.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### 15.4. IntentSpecification lookup unavailable:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
Retry-After: 30
```

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "reason": "INTENT_SPECIFICATION_LOOKUP_UNAVAILABLE",
  "message": "Intent creation or update cannot be accepted because the applicable ACTIVE IntentSpecification could not be confirmed.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/SERVICE_UNAVAILABLE",
  "@type": "Error"
}
```

### 15.5. ETag mismatch:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied ETag does not match the current resource representation.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

### 15.6. Submitted Intent update not allowed:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "INVALID_STATE_TRANSITION",
  "reason": "INTENT_NOT_DRAFT",
  "message": "Intent attributes can be updated only while the Intent is in Draft. Create a new Draft authoring record for material changes after submission.",
  "status": 409,
  "referenceError": "https://mycsp.com.au/errors/INVALID_STATE_TRANSITION",
  "@type": "Error"
}
```

### 15.7. External event timestamp rule:

External TMF-aligned event examples populate both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp. `timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples. TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics.

---

## 16. External Intent event family:

IC MS emits external TMF-aligned resource events for `Intent` projection changes.

| **Event** | **Trigger** |
|---|---|
| `IntentCreateEvent` | Runtime Intent projection created |
| `IntentAttributeValueChangeEvent` | External Intent attributes changed |
| `IntentStatusChangeEvent` | External lifecycle and status projection changed |
| `IntentDeleteEvent` | Runtime Intent termination accepted; retained projection moves to `Terminated` |

These are external projection/resource events only.

They must not expose raw telemetry, raw optimiser decisions, raw `t7.knowledge plane` data, raw callback payloads, internal candidate scoring, or internal Kafka event payloads.

---

## 17. IntentCreateEvent:

```json
{
  "eventId": "evt-intent-create-001",
  "eventTime": "2026-04-18T12:00:00+10:00",
  "timeOccurred": "2026-04-18T12:00:00+10:00",
  "eventType": "IntentCreateEvent",
  "correlationId": "corr-intent-create-001",
  "description": "Intent created.",
  "priority": "Normal",
  "title": "Intent created",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v1",
      "lifecycleStatus": "Acknowledged",
      "intentSpecification": {
        "id": "ispec-hss-001",
        "specKey": "hospital-surgical-slice-spec"
      },
      "@type": "Intent",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentCreateEvent"
}
```

---

## 18. IntentAttributeValueChangeEvent:

```json
{
  "eventId": "evt-intent-attr-001",
  "eventTime": "2026-04-18T12:40:00+10:00",
  "timeOccurred": "2026-04-18T12:40:00+10:00",
  "eventType": "IntentAttributeValueChangeEvent",
  "correlationId": "corr-intent-attr-001",
  "description": "Intent projected attributes changed.",
  "priority": "Normal",
  "title": "Intent attributes changed",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v4",
      "lifecycleStatus": "Acknowledged",
      "@type": "Intent",
      "@baseType": "Entity"
    },
    "changedAttributes": [
      {
        "name": "expression.targets.maxLatencyMs",
        "oldValue": 8,
        "newValue": 7
      }
    ]
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentAttributeValueChangeEvent"
}
```

---

## 19. IntentStatusChangeEvent:

```json
{
  "eventId": "evt-intent-status-001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "timeOccurred": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentStatusChangeEvent",
  "correlationId": "corr-intent-status-001",
  "description": "Intent lifecycle status changed.",
  "priority": "Normal",
  "title": "Intent status changed",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v2",
      "lifecycleStatus": "Active",
      "@type": "Intent",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentStatusChangeEvent"
}
```

`IntentStatusChangeEvent` carries the current `event.intent.lifecycleStatus` snapshot. It does not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields in the external event payload. The event type plus the emitted resource snapshot provide the external lifecycle and status-change signal.

---

## 20. IntentDeleteEvent:

`IntentDeleteEvent` represents accepted termination, not physical deletion.

```json
{
  "eventId": "evt-intent-delete-001",
  "eventTime": "2026-04-18T13:00:00+10:00",
  "timeOccurred": "2026-04-18T13:00:00+10:00",
  "eventType": "IntentDeleteEvent",
  "correlationId": "corr-intent-delete-001",
  "description": "Intent termination accepted.",
  "priority": "Normal",
  "title": "Intent terminated",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v4",
      "lifecycleStatus": "Terminated",
      "@type": "Intent",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentDeleteEvent"
}
```

---

## 21. External IntentReport event family:

IC MS emits external TMF-aligned resource events for `IntentReport` projection changes.

| **Event** | **Trigger** |
|---|---|
| `IntentReportCreateEvent` | New `IntentReport` projection created |
| `IntentReportAttributeValueChangeEvent` | Existing `IntentReport` projection updated |
| `IntentReportDeleteEvent` | Governed platform/internal retention purge, administrative removal, legal deletion, or approved data-correction handling |

`IntentReportDeleteEvent` is part of the external TMF-aligned event vocabulary for `IntentReport` alignment. It is not emitted as the result of ordinary external consumer delete because ordinary external `IntentReport` delete is not exposed by default. Reports remain read-only curated projection/audit history for ordinary consumers and may be archived or purged only through governed internal retention or administrative policy where required.

---

## 22. IntentReportCreateEvent:

```json
{
  "eventId": "evt-intent-report-create-001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "timeOccurred": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentReportCreateEvent",
  "correlationId": "corr-intent-report-create-001",
  "description": "IntentReport created.",
  "priority": "Normal",
  "title": "IntentReport created",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-003",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
      "intent": {
        "id": "INT-HOSP-2026-001"
      },
      "version": "v2",
      "lifecycleStatus": "Active",
      "@type": "IntentReport",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentReportCreateEvent"
}
```

---

## 23. IntentReportAttributeValueChangeEvent:

```json
{
  "eventId": "evt-intent-report-attr-001",
  "eventTime": "2026-04-18T12:25:00+10:00",
  "timeOccurred": "2026-04-18T12:25:00+10:00",
  "eventType": "IntentReportAttributeValueChangeEvent",
  "correlationId": "corr-intent-report-attr-001",
  "description": "IntentReport attributes changed.",
  "priority": "Normal",
  "title": "IntentReport attributes changed",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-003",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
      "intent": {
        "id": "INT-HOSP-2026-001"
      },
      "version": "v2",
      "lifecycleStatus": "Degraded",
      "@type": "IntentReport",
      "@baseType": "Entity"
    },
    "changedAttributes": [
      {
        "name": "lifecycleStatus",
        "oldValue": "Active",
        "newValue": "Degraded"
      }
    ]
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentReportAttributeValueChangeEvent"
}
```

---

## 24. IntentReportDeleteEvent:

`IntentReportDeleteEvent` represents governed internal/admin removal, not ordinary external consumer delete.

```json
{
  "eventId": "evt-intent-report-delete-001",
  "eventTime": "2026-04-18T13:30:00+10:00",
  "timeOccurred": "2026-04-18T13:30:00+10:00",
  "eventType": "IntentReportDeleteEvent",
  "correlationId": "corr-intent-report-delete-001",
  "description": "IntentReport removed by governed retention policy.",
  "priority": "Normal",
  "title": "IntentReport removed",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-003",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
      "intent": {
        "id": "INT-HOSP-2026-001"
      },
      "@type": "IntentReport",
      "@baseType": "Entity"
    },
    "removalReason": "RETENTION_PURGE"
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentReportDeleteEvent"
}
```

---

## 25. Internal Kafka event publication note:

IC MS publishes `IntentValidatedEvent` internally after schema and request-shape validation and admission.

This is not a point-to-point command for a single consumer.

It is a platform state and progress event meaning the runtime Intent has passed IC MS schema and request-shape validation and has been admitted into the Intent lifecycle.

Current primary consumer is II MS / `intent-intelligence-ms`, but the event may be consumed by other authorised internal consumers where useful.

IC MS also consumes downstream internal events that drive projection updates. `IntentRejectedEvent` carries II MS semantic or policy rejection outcomes that IC MS projects as external `Rejected` state. `IntentAssuranceEvent` carries IA MS assurance and runtime outcome facts that IC MS uses to update external `Intent` and `IntentReport` projections. IC MS does not consume `IntentCallbackEvent` by default; callback interpretation belongs to IA MS.

Internal publication uses the IC MS internal event outbox and Kafka relay. Kafka records use the platform CloudEvents-style header model. This internal Kafka publication path is separate from external hub notification delivery.

Typical internal Kafka headers are:

| Header | Meaning |
|---|---|
| `ce-specversion` | CloudEvents specification version. |
| `ce-id` | Stable event identifier. |
| `ce-source` | Producing service, typically `intent-controller-ms`. |
| `ce-type` | Internal event type, for example `IntentValidatedEvent`. |
| `ce-time` | Event occurrence timestamp. |
| `ce-subject` | Runtime intent identifier where applicable. |
| `ce-correlationid` | Correlation identifier for tracing. |
| `content-type` | Event payload content type, usually `application/json`. |

External hub notifications do not use these Kafka headers. They are HTTP webhook calls and use HTTP headers.

---

## 26. Final specification notes:

- `GET /intent/{id}` returns current projected Intent state, not a full internal version aggregate.
- `GET /intent` lists current projected Intent states for retained Intent IDs.
- Submitted runtime create/update admission requires both mandatory `intentSpecification.id` and mandatory `expression.iri`.
- `intentSpecification.id` selects the exact active platform-managed specification.
- `expression.iri` identifies the semantic/expression contract and must match the selected specification's `expressionSpecification.iri`.
- IC MS does not admit by IRI-only resolution.
- `intentSpecification.specKey` and `intentSpecification.name` are optional hints only and are not authoritative runtime validation keys.
- IC MS must not resolve `IntentSpecification` by `specKey`, name, or inferred payload shape alone.

Baseline:
- `expression.iri` is mandatory.
- `intentSpecification.id` is mandatory for submitted admission.
- `intentSpecification.specKey` and `intentSpecification.name` are optional hints only.
- `expression.iri` is the semantic/expression contract identifier and must match the selected specification's `expressionSpecification.iri`.
- Runtime admission is governed by the explicit `intentSpecification.id` and the `expression.iri` consistency check. IC MS must not select the governing runtime contract by `expression.iri` alone.
- `DELETE /intent/{id}` is termination, not physical deletion.
- `submit` is an approved IC MS extension request-control field; `submit: false` saves or keeps an Intent as `Draft`, and `submit: true` submits it for admission.
- If `submit` is omitted on initial create, IC MS treats the request as submitted for admission.
- If an Intent is already persisted with `submit: false`, later omission of `submit` preserves Draft handling and must not automatically submit the Intent.
- External consumers must not set or patch `lifecycleStatus`; lifecycle is assigned, transitioned, and projected by the intent management entity.
- `isBundle` is optional in create/update requests; omitted create requests default to `false`, and persisted responses include the server-resolved value.
- `PUT /intent/{id}` is a platform extension for deterministic full replacement and is allowed only while the current Intent/Draft projection is in `Draft`.
- `PATCH /intent/{id}` is supported for TMF compatibility and is allowed only while the current Intent/Draft projection is in `Draft`.
- Once an Intent leaves `Draft`, material changes require creating a new Draft authoring record.
- ETag is used for unsafe-operation concurrency through `If-Match`.
- GET responses may use bounded private caching based on a deterministic cache key derived from the effective request shape.
- Clients may request a fresh GET using `Cache-Control: no-cache`; IC MS bypasses cached serving, reads from source of truth, and refreshes the cache entry where safe.
- `IntentDeleteEvent` represents termination acceptance, not physical deletion.
- External `Intent` events and `IntentReport` events are curated projection events and must not expose raw telemetry, raw callback payloads, raw optimiser details, raw knowledge-plane data, or internal candidate scoring.
- External event examples include both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp.
- IC MS does not expose ordinary external `DELETE /intent/{intentId}/intentReport/{id}` by default; IntentReport is read-only audit/projection history and is retained unless governed internal retention policy archives or purges it.

## 27. Shared semantic bucket baseline:

### 27.1. Runtime Intent expression:

IC MS accepts and projects runtime Intent resources using the external runtime expression shape baselined by ID MS:

```json
{
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {},
        "constraints": {},
        "preferences": {}
      }
    }
  }
}
```

`location`, `serviceType`, and `serviceClass` are not peer fields beside `targets`, `constraints`, and `preferences`. They are modelled under `expression.expressionValue.context.constraints` because they restrict what and where the intent must fulfil.

### 27.2. Complete POST /intent request body example:

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "submit": true,
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
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
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### 27.3. Complete IntentValidatedEvent body example:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "Acknowledged",
    "statusReason": "Intent request passed IC MS admission validation and was admitted for downstream processing.",
    "intentSpecification": {
      "id": "ispec-hss-001",
      "specKey": "hospital-surgical-slice-spec"
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
            "startDateTime": "2026-04-18T12:00:00+10:00"
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
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      }
    }
  }
}
```

### 27.4. Baseline rules:

- External runtime `Intent.expression.expressionValue` uses the `context` wrapper.
- `context` contains only `targets`, `constraints`, and `preferences`.
- `location`, `serviceType`, and `serviceClass` sit under `context.constraints`.
- `IntentValidatedEvent.body.expression` carries the same canonical semantic buckets internally without the external TMF expression wrapper.
- IC MS validates schema and request shape against the active ID MS `expressionSpecification` and `targetEntitySchema`.
- IC MS does not perform semantic/KP validation, optimisation, change execution, or assurance.
