# ID MS Design Brief

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Scope | Intent Definition MS design brief |
| Source of truth after commit | GitHub `baseline/intent/id-ms/id_ms_design_brief.md` |

## Table of contents:

- [1. ID MS API contract](#1-id-ms-api-contract)
- [2. TMF compliance and platform extension](#2-tmf-compliance-and-platform-extension)
- [3. Response locale](#3-response-locale)
- [4. Response classification headers](#4-response-classification-headers)
- [5. IntentSpecification resource APIs](#5-intentspecification-resource-apis)
- [6. Hub subscription APIs](#6-hub-subscription-apis)
- [7. Query conventions](#7-query-conventions)
- [8. Lifecycle rules](#8-lifecycle-rules)
- [9. ETag / If-Match rules](#9-etag-if-match-rules)
- [10. Create IntentSpecification](#10-create-intentspecification)
- [11. Retrieve IntentSpecification](#11-retrieve-intentspecification)
- [12. List IntentSpecifications](#12-list-intentspecifications)
- [13. Full update IntentSpecification](#13-full-update-intentspecification)
- [14. Partial update IntentSpecification](#14-partial-update-intentspecification)
- [15. Delete unused DRAFT IntentSpecification candidate](#15-delete-unused-draft-intentspecification-candidate)
- [16. Activation response traceability](#16-activation-response-traceability)
- [17. Activate IntentSpecification](#17-activate-intentspecification)
- [18. Hub create subscription](#18-hub-create-subscription)
- [19. Hub retrieve subscription](#19-hub-retrieve-subscription)
- [20. Hub delete subscription](#20-hub-delete-subscription)
- [21. Standard error body](#21-standard-error-body)
- [22. ID MS API boundary statement](#22-id-ms-api-boundary-statement)
- [23. Lifecycle and versioning rules](#23-lifecycle-and-versioning-rules)
- [24. Caching, ETag, and dependency-specific circuit-breaker baseline](#24-caching-etag-and-dependency-specific-circuit-breaker-baseline)
- [25. Deployment and persistence strategy](#25-deployment-and-persistence-strategy)
- [26. Security and access-control baseline](#26-security-and-access-control-baseline)
- [27. Observability and audit baseline](#27-observability-and-audit-baseline)
- [28. ID MS consistency sweep](#28-id-ms-consistency-sweep)
- [29. Optional IntentSpecification behaviour metadata](#29-optional-intentspecification-behaviour-metadata)
- [30. specKey lineage note](#30-speckey-lineage-note)
- [31. draftId provenance lookup rule](#31-draftid-provenance-lookup-rule)
- [32. Runtime admission guardrail](#32-runtime-admission-guardrail)
- [33. Callback URL baseline](#33-callback-url-baseline)
- [34. PATCH semantics](#34-patch-semantics)
- [35. IntentSpecification versioning clarification](#35-intentspecification-versioning-clarification)
- [36. Expression schema alignment](#36-expression-schema-alignment)

## 1. ID MS API contract:

ID MS owns the definition-time `IntentSpecification` resource and related hub subscriptions.

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Definition MS |
| Short name | ID MS |
| Service name | `intent-definition-ms` |
| Base path | `/intentManagement/v5` |
| Primary resource | `IntentSpecification` |

ID MS owns definition-time `IntentSpecification` contracts and subscription management for specification events.
It validates syntax and resource shape, enforces specification lifecycle and version governance, and delivers external specification lifecycle notifications to subscribed REST webhook listener callbacks.
ID MS does not validate runtime semantic feasibility, policy fulfilment, network topology, optimisation, assurance, telemetry, change-execution callbacks, or runtime intent lifecycle truth.

## 2. TMF compliance and platform extension:


## 3. Response locale:

`Content-Language: en-AU` is the platform default response locale used in examples. It does not change field names, enum values, identifiers, or JSON payload semantics.

## 4. Response classification headers:

The service returns response classification headers on external REST API responses so callers can distinguish strict TMF-native behaviour from documented platform-extension behaviour.

These are response headers only. Clients do not send these headers in requests.

| **Response header** | **Meaning** |
|---|---|
| `X-TMF-Native: true` | The response is for a TMF-native operation or behaviour. |
| `X-TMF-Native: false` | The response is for an operation or behaviour that includes platform-specific semantics. |
| `X-Platform-Extension: true` | The route, method, response, or behaviour includes a documented platform extension. |
| `X-Platform-Extension: false` | No platform extension is used for the response. |

Use canonical header casing in examples:

```http
X-TMF-Native: true
X-Platform-Extension: false
```

or:

```http
X-TMF-Native: false
X-Platform-Extension: true
```


ID MS follows the TMF921 `IntentSpecification` resource responsibility boundary while retaining a small set of approved platform extensions.

Deployment path convention:

- examples in this design brief use `/intentManagement/v5`
- NGW and API gateway routing may map any deployment-specific external prefix to the internal service path
- do not use `/tmf-api` in baseline path examples

Strict TMF-compatible operations remain:

| **Area** | **Strict TMF-compatible operation** |
|---|---|
| Create specification | `POST /intentManagement/v5/intentSpecification` |
| List specifications | `GET /intentManagement/v5/intentSpecification` |
| Retrieve specification | `GET /intentManagement/v5/intentSpecification/{id}` |
| Partial update DRAFT candidate | `PATCH /intentManagement/v5/intentSpecification/draft/{draftId}` |
| Delete specification | `DELETE /intentManagement/v5/intentSpecification/{id}` |
| Generic hub create and delete | `/hub` exposure where strict TMF gateway routing is required |

Approved platform extensions are:

| **Extension** | **Reason** |
|---|---|
| `PUT /intentManagement/v5/intentSpecification/draft/{draftId}` | Deterministic full replacement of editable DRAFT candidates |
| Domain-scoped `/intentSpecification/hub` routes | Keeps ID MS subscriptions scoped to `IntentSpecification` event notifications |
| `GET /intentSpecification/hub/{id}` | Operational convenience for retrieving a domain-scoped subscription |
| `specKey` | Spec-key version governance across related specification versions |
| `_links` | Platform navigation affordance |
| `previousActiveSpecification` | Activation and retirement traceability during active-version promotion |
| Strong `ETag` / `If-Match` rules | Optimistic concurrency for unsafe operations |
| `428 Precondition Required` | Explicit stale-write prevention when `If-Match` is missing |

External `IntentSpecificationCreateEvent`, `IntentSpecificationAttributeValueChangeEvent`, `IntentSpecificationStatusChangeEvent`, and `IntentSpecificationDeleteEvent` envelopes should populate both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp.
`timeOccurred` is the platform-corrected spelling used consistently for external event examples.

`IntentSpecificationStatusChangeEvent` carries the current `intentSpecification.lifecycleStatus` snapshot. It does not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields in the external event payload.

## 5. IntentSpecification resource APIs:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create mutable DRAFT candidate | `POST` | `/intentSpecification` |
| List specifications | `GET` | `/intentSpecification` |
| Retrieve official ACTIVE and RETIRED specification by ID | `GET` | `/intentSpecification/{id}` |
| Retire current ACTIVE specification | `DELETE` | `/intentSpecification/{id}` |
| Retrieve DRAFT candidate or produced version by draftId | `GET` | `/intentSpecification/draft/{draftId}` |
| Full replace DRAFT candidate | `PUT` | `/intentSpecification/draft/{draftId}` |
| Partial update or activate DRAFT candidate | `PATCH` | `/intentSpecification/draft/{draftId}` |
| Delete unused DRAFT candidate | `DELETE` | `/intentSpecification/draft/{draftId}` |

`PUT /intentSpecification/draft/{draftId}` is an intentional platform extension for deterministic full replacement of editable DRAFT candidates.
`PATCH /intentSpecification/draft/{draftId}` remains supported for TMF-compatible partial-update semantics on the platform-extension DRAFT-candidate route, but is discouraged as a general update method.

## 6. Hub subscription APIs:

ID MS intentionally uses domain-scoped hub routes for `IntentSpecification` event subscriptions.
Strict TMF exposure may use the generic root `/hub` route at the gateway layer; `/intentSpecification/hub` and `GET /intentSpecification/hub/{id}` are approved platform extensions for domain-owned operational clarity.

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentSpecification/hub` |
| Retrieve subscription by ID | `GET` | `/intentSpecification/hub/{id}` |
| Delete event subscription | `DELETE` | `/intentSpecification/hub/{id}` |

Hub subscriptions are for external `IntentSpecification` event notifications only. ID MS delivers those notifications by HTTP `POST` to the subscriber-owned REST webhook listener callback URL. Kafka is not used for external hub notification delivery.
They must not expose internal workflow events, KP details, runtime assurance state, telemetry, callback payloads, optimiser decisions, or candidate and resource scoring details.

## 7. Query conventions:

List endpoint:

```http
GET /intentManagement/v5/intentSpecification?offset=0&limit=20&lifecycleStatus=ACTIVE&name=Hospital%20Surgical%20Slice&version=1.19&fields=id,href,specKey,name,version,lifecycleStatus,isBundle,validFor,relatedParty,@type,@baseType
```

Supported query params:

| **Param** | **Meaning** |
|---|---|
| `offset` | Zero-based start position |
| `limit` | Maximum number of records |
| `lifecycleStatus` | Filter by `DRAFT`, `ACTIVE`, or `RETIRED` |
| `name` | Filter by specification name |
| `version` | Filter by specification version |
| `fields` | Optional TMF-aligned field selection / projection |

Response headers:

```http
X-Total-Count: 1
X-Result-Count: 1
ETag: "list-etag-value"
Cache-Control: private, max-age=60
```

## 8. Lifecycle rules:

Allowed lifecycle states:

```text
DRAFT
ACTIVE
RETIRED
```

Rules:

| **Current state** | **Allowed write operations** | **Rule** |
|---|---|---|
| `DRAFT` | `PUT`, tightly controlled `PATCH`, `DELETE`, activation | Draft can be edited and governed |
| `ACTIVE` | No material `PUT`, `PATCH`, or `DELETE` | Active specs are immutable |
| `RETIRED` | No material `PUT`, `PATCH`, or `DELETE` | Retired specs are immutable |

Important:

- There is no `DELETED` lifecycle state.
- Delete is an operation outcome, not a lifecycle status.
- Meaningful change after activation requires a new versioned `IntentSpecification`.
- `PATCH` is supported for TMF compatibility but discouraged as a general update method.
- `PUT` is preferred for deterministic full replacement of editable `DRAFT` specifications.
- Activation is a lifecycle update on `/intentSpecification/draft/{draftId}`, not a custom `/activate` endpoint.
- When a new version becomes `ACTIVE`, the previous `ACTIVE` version in the same `specKey` becomes `RETIRED`.

## 9. ETag / If-Match rules:

| **Operation** | **ETag / If-Match rule** |
|---|---|
| `POST /intentSpecification` | Response must include `ETag` |
| `GET /intentSpecification/{id}` | Response must include `ETag` |
| `GET /intentSpecification` | Response should include list-level `ETag` |
| `PUT /intentSpecification/draft/{draftId}` | Request must include `If-Match` |
| `PATCH /intentSpecification/draft/{draftId}` | Request must include `If-Match` |
| `DELETE /intentSpecification/{id}` and `DELETE /intentSpecification/draft/{draftId}` | Official delete and retire and draft-candidate delete both require `If-Match` where applicable; `/draft/{draftId}` applies only to mutable draft candidates. |
| `POST /intentSpecification/hub` | Response must include `ETag` |
| `DELETE /intentSpecification/hub/{id}` | Request must include `If-Match` |

Missing `If-Match` response:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
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

Stale or mismatched ETag response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied ETag does not match the current resource version.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

## 10. Create IntentSpecification:

```http
POST /intentManagement/v5/intentSpecification?fields=id,href,specKey,draftId,name,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,intentBehaviour,intentLayer,@type,@baseType
Content-Type: application/json
Accept: application/json
```

Create request baseline includes:

- mandatory `specKey`, used by ID MS to resolve the stable server-assigned `IntentSpecification.id`
- `name`
- `description`
- `validFor`
- `relatedParty`
- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`

ID MS creates a mutable `DRAFT` candidate. `lifecycleStatus`, `id`, `href`, `draftId`, official `version`, server timestamps, `Location`, `ETag`, and `_links` are not accepted in the create request. `isBundle` is optional on create and defaults to `false` when omitted.
- `@type: IntentSpecification`
- `@baseType: EntitySpecification`

Success:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
Content-Type: application/json
Content-Language: en-AU
ETag: "id-draft-hospital-surgical-slice-a-r1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
```

Notes:

- Create creates a mutable `DRAFT` candidate, not an official public version.
- ID MS resolves server-assigned `id` from `specKey` and assigns `draftId`; `id` must not be assumed to equal `specKey`.
- Response returns the created DRAFT candidate representation.
- Response includes server-assigned `draftId`, DRAFT `href`, `Location`, `ETag`, and `_links`.
- `Location` points to `/intentSpecification/draft/{draftId}`.
- DRAFT candidate revision is represented by `ETag`.
- Official `version` is assigned only when the selected DRAFT candidate is activated.

## 11. Retrieve IntentSpecification:

```http
GET /intentManagement/v5/intentSpecification/ispec-hss-001?fields=id,href,specKey,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Accept: application/json
```

Success:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/ispec-hss-001
ETag: "intent-spec-ispec-hss-001-v1.19-r1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
Cache-Control: private, max-age=300
```

Notes:

- `GET` can be cached privately.
- IC MS may use this to validate incoming runtime `Intent` requests.
- The returned resource includes full `specKey`, `isBundle`, `validFor`, `relatedParty`, `specCharacteristic`, `expressionSpecification`, `targetEntitySchema`, lifecycle status, and `_links`.

## 12. List IntentSpecifications:

The list operation returns a lightweight summary by default.

Default list representation includes:

- `id`
- `href`
- `specKey`
- `name`
- `version`
- `lifecycleStatus`
- `isBundle`
- `validFor`
- `relatedParty`
- `@type`
- `@baseType`
- `_links`

The list operation does not include full `specCharacteristic`, `expressionSpecification`, or `targetEntitySchema` by default unless requested through `fields`.

## 13. Full update IntentSpecification:

```http
PUT /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a?fields=id,href,specKey,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Content-Type: application/json
Accept: application/json
If-Match: "id-draft-hospital-surgical-slice-a-r1"
```

Success:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
ETag: "id-draft-hospital-surgical-slice-a-r2"
```

Rules:

- Allowed only when `lifecycleStatus = DRAFT`.
- Requires `If-Match`.
- Returns full updated representation.
- Preferred over `PATCH`.
- Intended for deterministic full replacement of editable `DRAFT` specifications.

If resource is `ACTIVE` or `RETIRED`:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "RESOURCE_IMMUTABLE",
  "reason": "ACTIVE_OR_RETIRED_SPECIFICATION_IMMUTABLE",
  "message": "ACTIVE and RETIRED IntentSpecification resources cannot be materially updated. Create a new versioned DRAFT specification for material contract changes.",
  "status": 409,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_IMMUTABLE",
  "@type": "Error"
}
```

## 14. Partial update IntentSpecification:

```http
PATCH /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "id-draft-hospital-surgical-slice-a-r1"
```

Rules:

- Supported for TMF compatibility.
- Discouraged as a general update method from a platform perspective.
- Use only where a TMF-compatible client cannot use `PUT` or where a tightly controlled, small targeted compatibility update is required.
- Allowed only when `lifecycleStatus = DRAFT`.
- Requires `If-Match`.
- Prefer `PUT` for deterministic full replacement.
- Must not normally be used for material replacement of `specKey`, `version`, `specCharacteristic`, `expressionSpecification`, `targetEntitySchema`, or major lifecycle and version contract identity.

## 15. Delete unused DRAFT IntentSpecification candidate:

```http
DELETE /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
If-Match: "id-draft-hospital-surgical-slice-a-r1"
Accept: application/json
```

Success:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
```

Rules:

- Allowed only for unused mutable `DRAFT` candidates.
- `ACTIVE` and `RETIRED` official specifications are not deleted through this route.
- Retiring an official `ACTIVE` specification uses `DELETE /intentSpecification/{id}` where supported by governance.
- Delete is blocked if existing runtime intents reference the specification.
- Delete is blocked if audit or retention policy requires preservation.
- Delete does not create `lifecycleStatus = DELETED`.
- Delete emits `IntentSpecificationDeleteEvent` only after successful delete.
- Physical versus logical removal is an implementation detail.

## 16. Activation response traceability:

`previousActiveSpecification` is included when a previous ACTIVE version was retired during the activation transaction. Example:

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
  "specKey": "hospital-surgical-slice-spec",
  "version": "1.20",
  "lifecycleStatus": "ACTIVE",
  "previousActiveSpecification": {
    "id": "ispec-hss-001",
    "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.19",
    "version": "1.19",
    "lifecycleStatus": "RETIRED"
  }
}
```

## 17. Activate IntentSpecification:

Activation is a lifecycle update, not a custom action endpoint.

Do not expose:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate
```

Use `PATCH /intentManagement/v5/intentSpecification/draft/{draftId}` for TMF-compatible partial-update semantics on the platform-extension DRAFT-candidate route, or `PUT /intentManagement/v5/intentSpecification/draft/{draftId}` as the preferred platform extension when the caller sends the full DRAFT candidate representation. When a PUT body includes `lifecycleStatus: ACTIVE`, ID MS treats it as a governed activation instruction, not as free-form mutation of a server-managed field.
Although `PATCH` is discouraged as a general update method, it is acceptable for this tightly controlled TMF-compatible lifecycle transition.

Rules:

- Only `DRAFT` can be activated.
- Activated version becomes `ACTIVE`.
- Previous `ACTIVE` version in the same `specKey` becomes `RETIRED`.
- New runtime intent creation must use the new `ACTIVE` version.
- Existing runtime Intent instances referencing a RETIRED specification may continue under external platform governance policy.
- Missing `If-Match` returns `428`.
- Stale or mismatched `If-Match` returns `412`.
- Invalid lifecycle transition returns `409 Conflict`.
- Activation emits two `IntentSpecificationStatusChangeEvent` events:
  - one event carrying the new version snapshot with `lifecycleStatus: ACTIVE`
  - one event carrying the previous active version snapshot with `lifecycleStatus: RETIRED`



Retire current ACTIVE specification example:

```http
DELETE /intentManagement/v5/intentSpecification/ispec-hss-001
If-Match: "intent-spec-ispec-hss-001-v1.20-r1"
Accept: application/json
```

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
```

If the specification is already `RETIRED`, ID MS returns `409 Conflict` because only `ACTIVE` official specifications can be retired.

## 18. Hub create subscription:

```http
POST /intentManagement/v5/intentSpecification/hub
Content-Type: application/json
Accept: application/json
```

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecification/events",
  "query": "eventType=IntentSpecificationStatusChangeEvent",
  "@type": "EventSubscription"
}
```

Success:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hub/sub-001
Content-Type: application/json
Content-Language: en-AU
ETag: "subscription-sub-001-v1"
```

```json
{
  "id": "sub-001",
  "href": "/intentManagement/v5/intentSpecification/hub/sub-001",
  "callback": "https://consumer.example.com/listener/intentSpecification/events",
  "query": "eventType=IntentSpecificationStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-001"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-001",
      "method": "DELETE"
    }
  }
}
```

Supported event filters:

```text
IntentSpecificationCreateEvent
IntentSpecificationAttributeValueChangeEvent
IntentSpecificationStatusChangeEvent
IntentSpecificationDeleteEvent
```


Hub notification delivery baseline:

- `/intentSpecification/hub` is a REST webhook subscription mechanism.
- ID MS stores subscriber callback registrations.
- ID MS delivers matching `IntentSpecification` event notifications by HTTP `POST` to the subscriber listener callback URL.
- The HTTP request body is the TMF-aligned external event payload, such as `IntentSpecificationStatusChangeEvent`.
- The subscriber returns `204 No Content` when notified successfully.
- Kafka topics are not used for external hub notification delivery because ID MS is both the event originator and the delivery owner.
- Delivery reliability is handled by an ID MS-owned local webhook delivery outbox and retry relay.

## 19. Hub retrieve subscription:

```http
GET /intentManagement/v5/intentSpecification/hub/sub-001
Accept: application/json
```

Success:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
ETag: "subscription-sub-001-v1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "sub-001",
  "href": "/intentManagement/v5/intentSpecification/hub/sub-001",
  "callback": "https://consumer.example.com/listener/intentSpecification/events",
  "query": "eventType=IntentSpecificationStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-001"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-001",
      "method": "DELETE"
    }
  }
}
```

## 20. Hub delete subscription:

```http
DELETE /intentManagement/v5/intentSpecification/hub/sub-001
If-Match: "subscription-sub-001-v1"
Accept: application/json
```

Success:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
```

## 21. Standard error body:

All ID MS errors use the common cross-MS error shape:

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

Common errors:

| **HTTP** | **Code** | **Scenario** |
|---:|---|---|
| `400` | `BAD_REQUEST` | Invalid JSON or invalid request structure |
| `404` | `RESOURCE_NOT_FOUND` | Specification or subscription not found |
| `409` | `RESOURCE_IMMUTABLE` | Attempt to update active/retired specification |
| `409` | `VERSION_CONFLICT` | Duplicate specification/version conflict |
| `412` | `PRECONDITION_FAILED` | Stale or mismatched `If-Match` |
| `422` | `VALIDATION_FAILED` | Fails expression/spec schema constraints |
| `428` | `PRECONDITION_REQUIRED` | Missing required `If-Match` |
| `503` | `SERVICE_UNAVAILABLE` | Source-of-truth DB unavailable |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

## 22. ID MS API boundary statement:

**ID MS owns definition-time `IntentSpecification` contracts and subscription management for specification events.
It validates syntax and resource shape, enforces specification lifecycle and version governance, and delivers external specification lifecycle notifications to subscribed REST webhook listener callbacks.
It does not validate runtime semantic feasibility, policy fulfilment, network topology, optimisation, assurance, telemetry, change-execution callbacks, or callback ingestion.**

## 23. Lifecycle and versioning rules:

### Lifecycle state model:

Allowed `IntentSpecification.lifecycleStatus` values:

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DELETED` lifecycle status.
Delete is an operation outcome, not a normal lifecycle state.

### Lifecycle transitions:

| **Transition** | **Allowed** | **Rule** |
|---|---:|---|
| Create -> `DRAFT` | Yes | New specifications are created as drafts by default |
| `DRAFT` -> `ACTIVE` | Yes | Activation makes this version available for new runtime `Intent` creation |
| `ACTIVE` -> `RETIRED` | Yes | Usually occurs when a newer version becomes active |
| `DRAFT` -> deleted | Yes, conditional | Allowed only if unused and not referenced |
| `ACTIVE` -> deleted | No by default | Active specifications are immutable and protected |
| `RETIRED` -> deleted | No by default | Retired specifications remain for audit/runtime compatibility |
| Any state -> `DELETED` | No | `DELETED` is not a lifecycle status |

### Versioning rules:

- Each meaningful change after activation requires a new versioned `IntentSpecification`.
- A new version starts as `DRAFT`.
- The `specKey` groups related versions of the same specification.
- Only one ACTIVE version is allowed for a given `specKey`.
- When a new version becomes `ACTIVE`, the previous active version moves to `RETIRED`.
- Retired specifications must not be used for new `Intent` creation.
- Existing runtime Intent instances referencing a RETIRED specification may continue under external platform governance policy.
- 
### Specification key rule:

A specification key is the logical grouping of related versions of the same specification.

Example spec key:

```text
hospital-surgical-slice-spec
```

Example official versions for the same stable specification id:

```text
id: ispec-hss-001, specKey: hospital-surgical-slice-spec, version: 1.18
id: ispec-hss-001, specKey: hospital-surgical-slice-spec, version: 1.19
id: ispec-hss-001, specKey: hospital-surgical-slice-spec, version: 1.20
```

Only one ACTIVE version is allowed for a given specKey.

Lineage reuse across retired-only specifications is not assumed by default. Reintroduction or reuse of a prior lineage requires explicit governance.

### Mutability rules:

| **Lifecycle status** | **Mutable?** | **Reason** |
|---|---:|---|
| `DRAFT` | Yes | Draft is still under design/governance |
| `ACTIVE` | No | Active contract must be stable for runtime clients and IC MS validation |
| `RETIRED` | No | Retired contract must remain stable for audit and existing runtime references |

### Runtime compatibility and Intent immutability rules:

- IC MS must validate new runtime `Intent` creation only against an `ACTIVE` `IntentSpecification`.
- If a submitted intent references a `DRAFT` specification, IC MS rejects it.
- If a submitted intent references a `RETIRED` specification for new creation, IC MS rejects it.
- Runtime Intent instances created using an `ACTIVE` `IntentSpecification` remain tied to the specification identity and version used at admission.
- Existing runtime Intent instances referencing a `RETIRED` specification may continue where platform policy allows.
- A change in intent requirements must result in submission of a new Intent instance. Runtime mutation of admitted Intent instances is not supported.
- ID MS does not mutate runtime Intent instances.
- `ACTIVE` and `RETIRED` `IntentSpecification` versions remain immutable for material contract changes.

### Activation governance rules:

Activation should only be allowed when:

- the specification is syntactically valid
- the `expressionSpecification` is valid
- required `specCharacteristic` entries are present
- `targetEntitySchema` references a valid governed expression-value schema artefact
- the version identifier is unique
- there is no conflicting active version in the same specKey, or the activation operation also retires the previous active version
- governance approval has been completed where required

### Delete rules:

Delete is allowed only for unused `DRAFT` specifications.

Delete is blocked when:

- the specification is `ACTIVE`
- the specification is `RETIRED`
- existing runtime intents reference the specification
- audit or retention policy requires preservation

Delete success returns `204 No Content` and does not create `lifecycleStatus = DELETED`.

## 24. Caching, ETag, and dependency-specific circuit-breaker baseline:

### Caching scope:

ID MS caching applies only to GET responses.

Caching is baselined for:

```http
GET /intentManagement/v5/intentSpecification/{id}
GET /intentManagement/v5/intentSpecification
GET /intentManagement/v5/intentSpecification/hub/{id}
```

No caching strategy is baselined for non-GET operations.

### Single-resource GET caching:

For a single `IntentSpecification`:

```http
GET /intentManagement/v5/intentSpecification/ispec-hss-001
```

ID MS may return:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "id-draft-hospital-surgical-slice-a-r1"
Cache-Control: private, max-age=300
```

Meaning:

- private bounded TTL cache is allowed
- single-resource GET may have a longer TTL than list GET
- `ETag` is returned, but not for GET revalidation
- `ETag` is used only for unsafe operation concurrency through `If-Match`

### List GET caching:

For list reads:

```http
GET /intentManagement/v5/intentSpecification?offset=0&limit=20&lifecycleStatus=ACTIVE
```

ID MS may return:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Total-Count: 1
X-Result-Count: 1
ETag: "intent-spec-list-active-v17"
Cache-Control: private, max-age=60
```

Meaning:

- list GET may be cached with a shorter TTL
- list responses still include `X-Total-Count` and `X-Result-Count`
- list-level `ETag` may be returned, but not for GET revalidation in this baseline

### Client cache override:

Clients can request a fresh GET response using:

```http
Cache-Control: no-cache
```

Example:

```http
GET /intentManagement/v5/intentSpecification/ispec-hss-001
Cache-Control: no-cache
```

Meaning:

- client does not rely on its existing cached copy
- ID MS returns a fresh `200 OK` representation
- `If-None-Match` is not baselined
- `304 Not Modified` is not baselined

### ETag rule:

ETag is not used for GET revalidation in this baseline.

Not baselined:

```http
If-None-Match
```

Not baselined:

```http
304 Not Modified
```

ETag is used only for unsafe operation concurrency through:

```http
If-Match
```

Applies to:

```http
PUT /intentManagement/v5/intentSpecification/draft/{draftId}
PATCH /intentManagement/v5/intentSpecification/draft/{draftId}
DELETE /intentManagement/v5/intentSpecification/{id}
DELETE /intentManagement/v5/intentSpecification/hub/{id}
```

and any activation/state-changing operation where stale updates could overwrite newer resource state.

### No non-GET caching strategy:

No caching strategy is baselined for non-GET operations.

Current rule:

- caching strategy is only discussed for GET responses
- non-GET operations do not have a caching strategy baseline

### ID MS internal cache refresh on active-version promotion:

When a new `IntentSpecification` version is promoted to `ACTIVE`, ID MS must refresh its own active-specification cache.

Activation flow:

1. ID MS performs activation against the source-of-truth DB.
2. ID MS retires the previous active version in the same specification key.
3. ID MS bypasses/refreshes its own cache for that specification key using an internal no-cache/refresh path.
4. ID MS stores the new active version as the current cached active copy.
5. ID MS ensures the previous active version is no longer returned as active.
6. ID MS emits status-change events for:
   - the new version becoming `ACTIVE`
   - the previous version becoming `RETIRED`

Baseline statement:

**On active-version promotion, ID MS must refresh its own active-specification cache using a no-cache/internal refresh path so the newly active version becomes the cached active copy and the previous active version is no longer returned as active.**

### IC MS cache behaviour:

IC MS may use a cached `ACTIVE` `IntentSpecification` for runtime `Intent` syntactic validation only when:

- the cached specification is within the configured freshness window
- the cached specification lifecycle is `ACTIVE`
- the cached specification ID/version matches the runtime intent reference
- the cached specification includes a valid `expressionSpecification`
- the cached specification includes a valid `targetEntitySchema`
- the cached specification has not been made stale by active-version promotion or other invalidation logic
- the degraded dependency path is logged and monitored

If ID MS is unavailable and IC MS has no valid fresh cached `ACTIVE` specification, IC MS must fail closed for new runtime intent creation.

### IC MS fail-closed response:

If active specification cannot be confirmed from ID MS or a valid fresh cache:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Content-Language: en-AU
Retry-After: 30
```

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "reason": "INTENT_SPECIFICATION_LOOKUP_UNAVAILABLE",
  "message": "Intent creation cannot be accepted because the active IntentSpecification could not be confirmed.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/SERVICE_UNAVAILABLE",
  "@type": "Error"
}
```

### Dependency-specific circuit-breaker behaviour:

ID MS has multiple circuit-breaker trigger points.
Different dependency failures have different behaviours.

| **Dependency path** | **CB style** | **Baseline behaviour** |
|---|---|---|
| ID MS -> DB | Hard fail-fast | Return `503`; consumer retries |
| ID MS -> cache | Graceful/silent | Bypass/ignore cache, use DB and source-of-truth, emit telemetry |
| ID MS -> external callback webhook | Async fail-fast per attempt | Delivery attempt fails fast, retries later; original API unaffected |
| IC MS -> ID MS | Cached fallback then fail-closed | IC MS may use fresh cached active spec fallback; otherwise fail closed |

### DB failure:

DB is a hard dependency.

If DB cannot be accessed:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Content-Language: en-AU
Retry-After: 30
```

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "reason": "ID_MS_DATABASE_UNAVAILABLE",
  "message": "IntentSpecification service is temporarily unavailable because the persistence layer cannot be accessed.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/SERVICE_UNAVAILABLE",
  "@type": "Error"
}
```

Rules:

- DB failure is not silently swallowed.
- ID MS cannot safely create, update, retrieve, activate, retire, or delete specifications without DB access.
- Consumer must retry later.

### Cache failure:

Cache is not source of truth.

If cache read and write fails:

- trigger cache circuit breaker
- bypass cache where safe
- read from DB/source of truth where needed
- ignore failed cache writes
- continue request when DB and source-of-truth succeeds
- emit logs, metrics, and alerts

Rules:

- cache failure is silent and graceful from the client perspective
- do not return `503` only because cache is unavailable
- cache failure must not block create, update, or read when DB is available

### Webhook delivery outbox failure:

External hub notification delivery is not on the synchronous critical path after the ID MS resource transaction commits.

For create, update, delete, activation, and retirement:

- commit the resource change and webhook delivery outbox record transactionally in DB
- return API success once the DB transaction succeeds
- deliver subscribed notifications asynchronously by HTTP `POST` through the ID MS webhook delivery relay
- if the subscriber callback endpoint is unavailable, the delivery attempt fails fast
- retry later using bounded retry and backoff policy
- do not fail the original API call after successful DB and outbox commit

Rules:

- webhook delivery failure is graceful/silent for the original API consumer
- webhook delivery failure is operationally visible through retry metrics and alerts
- if DB and outbox commit fails, API operation fails because durable notification delivery cannot be guaranteed

### External callback webhook failure:

External subscriber callback delivery is asynchronous.

If callback endpoint is unavailable, times out, or returns failure:

- delivery worker fails fast for that delivery attempt
- mark attempt failed
- retry later using bounded retries and backoff
- do not impact original ID MS resource operation
- if retries are exhausted, mark delivery as failed and alert/operate

Rules:

- webhook failure is graceful/silent from the original API consumer's point of view
- webhook failure must not roll back specification create, update, status-change, or delete operations
- webhook delivery is not a synchronous dependency for the API write path

### Final combined baseline statement:

**ID MS caching applies only to GET responses.
GET responses may use bounded private caching, with longer TTL for single-resource GETs and shorter TTL for list GETs.
Clients either use the cached response within TTL or request a fresh copy using `Cache-Control: no-cache`.
ETag is not used for GET revalidation; `If-None-Match` and `304 Not Modified` are not baselined.
ETag is used only for unsafe operation concurrency through `If-Match`.**

**On active-version promotion, ID MS refreshes its own active-specification cache using a no-cache/internal refresh path so the newly active version becomes the cached active copy and the previous active version is no longer returned as active.**

**ID MS uses dependency-specific circuit-breaker behaviour.
Database failure is hard fail-fast and returns `503 Service Unavailable`.
Cache failure is handled silently and gracefully by bypassing cache or ignoring cache writes where safe.
Webhook delivery failure is handled through the ID MS local delivery outbox. Each failed delivery attempt fails fast, is retried later, and does not affect the original resource API response.**

## 25. Deployment and persistence strategy:

### Runtime model:

ID MS is deployed as a mostly stateless API service.
The service instances can be horizontally scaled behind the API gateway / ingress layer.
The application instances should not hold domain truth in local memory.

### Source of truth:

The source of truth for ID MS is a managed PostgreSQL / PostgreSQL-compatible relational database.

ID MS stores and governs:

- `IntentSpecification` resources
- specification versions
- lifecycle status
- hub subscriptions
- local webhook delivery webhook delivery outbox records for subscribed event notification delivery
- audit-relevant metadata

### Recommended persistence model:

| **Table / store** | **Purpose** |
|---|---|
| `intent_specification` | Stores `IntentSpecification` resource, version, lifecycle, ETag, timestamps, and resource body |
| `intent_specification_subscription` | Stores `/intentSpecification/hub` event subscriptions |
| `webhook_delivery_outbox` | Stores durable subscriber webhook notification delivery records before HTTP callback delivery |
| `inbox_event` | Optional; used only if ID MS later consumes internal events requiring idempotent processing |
| audit table / audit log | Optional dedicated audit trail if not covered by platform audit capability |

### JSONB usage:

Use JSONB where flexible document-shaped content is required.

Recommended JSONB fields:

- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`
- `relatedParty`
- `_links`
- full resource body snapshot where useful
- event payload snapshot in `webhook_delivery_outbox`

Rationale:

- `IntentSpecification` is naturally document-shaped.
- JSONB supports flexible schema evolution.
- Relational columns still support governance queries such as `id`, `specKey`, `name`, `version`, `lifecycleStatus`, `ETag`, and timestamps.

### Suggested relational columns:

For `intent_specification`:

| **Column** | **Purpose** |
|---|---|
| `id` | Stable specification ID, for example `hospital-surgical-slice-spec` |
| `spec_key` | Logical specification key, for example `hospital-surgical-slice-spec` |
| `name` | Human-readable name |
| `version` | Version string |
| `lifecycle_status` | `DRAFT`, `ACTIVE`, or `RETIRED` |
| `etag` | Current entity tag for unsafe-operation concurrency |
| `resource_body` | Full JSONB representation |
| `created_at` | Creation timestamp |
| `updated_at` | Last update timestamp |
| `activated_at` | Activation timestamp, if active/previously active |
| `retired_at` | Retirement timestamp, if retired |

### High availability:

ID MS should be deployed with:

- multiple replicas
- rolling deployment support
- health checks
- same-region multi-AZ database configuration where available
- no local state dependency
- safe restart behaviour

### Disaster recovery:

Initial deployment may be single-region or same-region multi-AZ.
The selected database service/deployment pattern must support future cross-region active-passive DR as use cases expand.
Active-active multi-region writes are not baselined initially.

### Rollout strategy:

ID MS supports rolling deployment.

Rules:

- no breaking API change without versioning
- no incompatible DB schema change without backward-compatible migration
- migrations should be additive first where possible
- deployment should support rollback to the previous application version while DB remains compatible

### Health checks:

| **Health endpoint / check** | **Meaning** |
|---|---|
| Liveness | Process is running and can respond |
| Readiness | Service can access critical dependencies needed for serving traffic |
| DB readiness | Required for normal ID MS resource operations |
| Webhook delivery relay readiness | Should not block API readiness if DB and outbox commit path is healthy |
| Cache readiness | Should not block API readiness because cache failure is graceful/silent |

Readiness should fail when the DB and source-of-truth path is unavailable.
Readiness should not fail only because cache is unavailable.
Webhook delivery failures should be surfaced through relay metrics and alerts rather than making the ID MS API unavailable when the DB and outbox path is healthy.

### Configuration and secrets:

ID MS configuration should be externalised through platform configuration and secret management.

Examples:

- DB connection settings
- cache endpoint
- outbox relay configuration
- retry and backoff settings
- cache TTL values
- service identity
- callback and event delivery settings
- OAuth2, JWT, and security settings where applicable

Secrets must not be stored in application images or source files.

### Observability:

ID MS should emit:

- structured application logs
- request metrics
- dependency metrics
- cache hit and miss metrics
- circuit-breaker metrics
- webhook delivery metrics
- subscription delivery metrics
- audit and security logs where required
- distributed traces with propagated correlation context

Recommended metrics include:

- `intent_specification_create_count`
- `intent_specification_update_count`
- `intent_specification_patch_count`
- `intent_specification_activation_count`
- `intent_specification_retirement_count`
- `intent_specification_delete_count`
- `intent_specification_get_count`
- `intent_specification_list_count`
- `id_ms_db_error_count`
- `id_ms_cache_bypass_count`
- `id_ms_cache_write_failure_count`
- `id_ms_webhook_delivery_pending_count`
- `id_ms_webhook_delivery_outbox_failure_count`
- `id_ms_webhook_delivery_failure_count`

### Security posture:

ID MS should sit behind the platform gateway / ingress security layer.

Security baseline:

- authenticate callers through gateway and platform identity
- authorise create, update, delete, and activation operations at the appropriate upstream governance layer
- protect hub subscription creation and deletion
- validate callback URLs according to platform security policy
- apply request-size limits
- log security-relevant administrative operations
- avoid exposing internal DB, cache, and broker details in error responses

### Deployment baseline statement:

ID MS application instances are stateless and horizontally scalable.
The source of truth for `IntentSpecification`, hub subscriptions, lifecycle and version state, and webhook delivery outbox records is a managed PostgreSQL-compatible RDBMS.
JSONB may be used for document-shaped resource bodies and event snapshots, while relational columns support governance queries, lifecycle and versioning, ETag handling, and operational reporting.
ID MS readiness depends on DB and source-of-truth availability, but cache and webhook delivery failures are handled gracefully through cache bypass and the local delivery outbox where possible.

## 26. Security and access-control baseline:

### Authentication:

ID MS sits behind NGW.
NGW performs system-to-system authentication using:

| **Mechanism** | **Purpose** |
|---|---|
| mTLS | Authenticates the calling system or client at transport layer |
| OAuth2 token validation | Validates the calling workload or system token |

### Authorisation boundary:

ID MS does not own business and user-level operation authorisation.
Business and user-level authorisation belongs in the OEX layer.

| **Layer** | **Responsibility** |
|---|---|
| OEX | User and business-level access control, entitlement, role checks, and governance workflow permission |
| NGW | System-to-system authentication using mTLS and OAuth2 token validation |
| ID MS | Trusts authenticated platform and system callers and enforces technical resource integrity and governance state-machine rules |

No OAuth2 scopes are assumed.
No context-aware authorisation is baselined at NGW.

### ID MS technical integrity responsibilities:

ID MS still enforces:

- valid request shape
- `IntentSpecification` lifecycle rules
- version uniqueness
- one active version per `specKey`
- immutable `ACTIVE` and `RETIRED` specifications
- `ETag` / `If-Match` for unsafe operations
- no `DELETED` lifecycle state
- delete only for unused `DRAFT`
- callback URL validation for hub subscriptions if hub endpoints are exposed to system callers

### Audit baseline:

ID MS must audit technical/governance-changing operations, including:

- create specification
- update draft specification
- patch draft specification
- activate specification
- retire previous active specification
- delete unused draft specification
- create and delete hub subscription
- technical integrity validation failures where audit is required

Business and user authorisation audit belongs to OEX where that decision is made.

### Baseline statement:

**ID MS is protected behind NGW.
NGW performs system-to-system authentication using mTLS and OAuth2 token validation.
Business and user-level authorisation is owned by the OEX layer and should not be implemented as operation-level authorisation inside ID MS.
ID MS trusts authenticated platform and system callers and enforces technical resource integrity, lifecycle and version governance, validation, ETag and If-Match concurrency rules, and state-machine constraints for `IntentSpecification` resources.**

## 27. Observability and audit baseline:

### Observability purpose:

ID MS must provide enough operational visibility to support production operations, troubleshooting, governance review, and platform audit.

Observability covers:

- structured logs
- metrics
- distributed tracing
- audit records
- dependency health signals
- event/outbox delivery visibility

### Correlation and trace context:

ID MS must log and propagate correlation context.

Rules:

- Accept correlation and trace context from NGW where provided.
- Generate a correlation ID if one is not provided.
- Include correlation ID in structured logs.
- Include correlation ID in emitted events.
- Include correlation ID in webhook delivery outbox records.
- Propagate correlation ID to downstream dependency calls where applicable.
- Do not expose internal trace details in external error bodies.

### Structured logging:

ID MS logs should be structured and machine-readable.

Recommended log fields:

| **Field** | **Purpose** |
|---|---|
| `timestamp` | Event and log time |
| `level` | Log level |
| `service` | `intent-definition-ms` |
| `correlationId` | End-to-end correlation |
| `traceId` | Distributed trace ID where available |
| `operation` | API or internal operation name |
| `resourceId` | IntentSpecification ID where applicable |
| `specKey` | Specification key where applicable |
| `version` | Specification version where applicable |
| `lifecycleStatus` | Current or target lifecycle status where applicable |
| `result` | Success, failure, or degraded |
| `reasonCode` | Stable failure or reason code where applicable |

### Sensitive-data logging rule:

ID MS must not log:

- OAuth2 tokens
- mTLS certificate private material
- secrets
- DB credentials
- cache credentials
- full internal connection strings
- sensitive platform headers
- raw internal dependency stack traces in external responses

Internal logs may include sanitized technical details needed for support.
External error responses must remain stable and must not expose DB, cache, or internal infrastructure details.

### Metrics baseline:

ID MS should emit metrics for API operations, lifecycle transitions, dependency behaviour, caching, webhook delivery, and technical integrity validation.

Recommended metrics include:

| **Metric** | **Meaning** |
|---|---|
| `intent_specification_create_count` | Count of create operations |
| `intent_specification_update_count` | Count of update operations |
| `intent_specification_patch_count` | Count of patch operations |
| `intent_specification_activation_count` | Count of activations |
| `intent_specification_retirement_count` | Count of retirements |
| `intent_specification_delete_count` | Count of delete operations |
| `intent_specification_get_count` | Count of retrieve-by-id operations |
| `intent_specification_list_count` | Count of list operations |
| `intent_specification_validation_failure_count` | Count of syntax and schema validation failures |
| `id_ms_db_error_count` | Count of DB and source-of-truth failures |
| `id_ms_db_circuit_breaker_open_count` | Count of DB CB-open events |
| `id_ms_cache_hit_count` | Count of cache hits |
| `id_ms_cache_miss_count` | Count of cache misses |
| `id_ms_cache_bypass_count` | Count of cache bypass events |
| `id_ms_cache_write_failure_count` | Count of ignored cache-write failures |
| `id_ms_webhook_delivery_pending_count` | Current pending outbox event count |
| `id_ms_webhook_delivery_outbox_failure_count` | Count of outbox publish failures |
| `id_ms_webhook_delivery_failure_count` | Count of callback and webhook delivery failures |
| `id_ms_webhook_delivery_retry_count` | Count of callback and webhook retry attempts |

### Audit baseline:

ID MS audit focuses on technical/governance-changing operations and technical integrity decisions.

ID MS must audit:

- create specification
- update draft specification
- patch draft specification
- activate specification
- retire previous active specification
- delete unused draft specification
- create hub subscription
- delete hub subscription
- rejected unsafe operation due to missing `If-Match`
- rejected unsafe operation due to ETag mismatch
- rejected mutation of immutable `ACTIVE` specification
- rejected mutation of immutable `RETIRED` specification
- rejected delete due to references or lifecycle restrictions
- technical validation failures where audit is required

Business and user-level authorisation audit belongs to OEX, because OEX owns business and user-level authorisation decisions.

### Audit record fields:

Recommended audit record fields:

| **Field** | **Purpose** |
|---|---|
| `auditId` | Stable audit record ID |
| `timestamp` | Audit event time |
| `service` | `intent-definition-ms` |
| `operation` | Operation performed |
| `resourceId` | Specification or subscription ID |
| `specKey` | Specification key where applicable |
| `version` | Specification version where applicable |
| `previousLifecycleStatus` | Previous status where applicable for audit only |
| `newLifecycleStatus` | New status where applicable for audit only |
| `correlationId` | End-to-end correlation |
| `callerIdentity` | Authenticated system identity from NGW where available |
| `result` | Success/failure |
| `reasonCode` | Stable reason code for failure or special decision |

### Alerting baseline:

Operational alerts should be raised for:

- DB unavailable / DB circuit breaker open
- repeated DB errors
- outbox backlog above threshold
- repeated webhook delivery failures
- repeated webhook delivery failures
- activation failures
- repeated ETag and If-Match conflicts above normal threshold
- high validation failure rate
- cache bypass/failure rate above threshold
- readiness failures
- unexpected error rate increase

### Tracing baseline:

ID MS should participate in distributed tracing.

Trace spans should cover:

- inbound API request
- DB and source-of-truth operation
- cache read and write where applicable
- webhook delivery outbox record creation
- webhook delivery relay attempt where applicable
- webhook delivery attempt where applicable

Trace data must not include secrets or sensitive token contents.

### Baseline statement:

**ID MS must log and propagate correlation context, emit structured operational telemetry, and audit technical/governance-changing operations.
Business and user authorisation audit remains with OEX, while ID MS audit focuses on specification creation, update, activation, retirement, deletion, hub subscription changes, technical validation failures, ETag and If-Match integrity decisions, immutable-resource enforcement, and dependency failure signals.**

## 28. ID MS consistency sweep:

### Sweep date:

2026-05-15

### Overall result:

**PASS WITH NOTES**

### Checks:

| **Area** | **Result** | **Notes** |
|---|---|---|
| Service naming | PASS | Uses Intent Definition MS / ID MS / `intent-definition-ms` |
| Lifecycle states | PASS | Uses `DRAFT`, `ACTIVE`, `RETIRED`; no `DELETED` lifecycle state |
| Status-change event payload | PASS | Uses current `intentSpecification.lifecycleStatus` snapshot; no separate previous and new lifecycle fields in external event payload |
| GET-only caching | PASS | Caching is scoped to GET responses only |
| No GET ETag revalidation | PASS | `If-None-Match` and `304 Not Modified` are not baselined |
| ETag unsafe concurrency | PASS | ETag is positioned for `If-Match` unsafe operation concurrency |
| Dependency-specific circuit breakers | PASS | DB, cache, and webhook behaviours are present |
| Security boundary | PASS | NGW authentication and OEX authorisation boundary preserved |
| Eventing boundary | PASS | External `IntentSpecification` event family and boundary are present |
| Persistence baseline | PASS | PostgreSQL-compatible RDBMS, JSONB, and outbox persistence are present |
| Boundary exclusions | PASS | ID MS does not own runtime fulfilment concerns |
| Platform extensions | PASS | `PUT`, domain-scoped hub, `specKey`, `_links`, ETag and If-Match, and caching are documented |

### Notes requiring attention:

- Examples use `/intentManagement/v5`.
- Domain-scoped `/intentSpecification/hub` route is intentional; strict TMF generic `/hub` exposure can be handled by NGW and API gateway routing when required.
- `GET /intentSpecification/hub/{id}` is an approved platform extension for subscription retrieval.
- `PUT` full replacement is an intentional platform extension.
- `PATCH` remains supported for TMF compatibility, but is discouraged generally.
- External `IntentSpecificationCreateEvent`, `IntentSpecificationAttributeValueChangeEvent`, `IntentSpecificationStatusChangeEvent`, and `IntentSpecificationDeleteEvent` envelopes should populate both `eventTime` and `timeOccurred` with the same canonical occurrence timestamp.
- `targetEntitySchema` is retained as the governed runtime expression-value schema reference.
- `specKey` is retained for spec-key version governance.

### Final consistency position:

The ID MS design brief is internally consistent for the current baseline.
The design keeps ID MS focused on definition-time `IntentSpecification` resource ownership, lifecycle and version governance, syntax and resource shape validation, ETag and If-Match concurrency, GET-only caching, external `IntentSpecification` webhook notification delivery, PostgreSQL-compatible persistence, and technical observability/audit.
ID MS does not own semantic validation, policy validation, candidate and resource feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.


## 29. Optional IntentSpecification behaviour metadata:

`intentBehaviour` and `intentLayer` are optional classification metadata fields on `IntentSpecification`. Refer to the ID MS specification for the full `intentBehaviour` and `intentLayer` definition, allowed values, and constraints.

They support catalogue visibility, governance visibility, and external consumer understanding. They are not used by ID MS for runtime decisioning, runtime validation, admission control, or behavioural enforcement.

If omitted, ID MS does not infer or default these values unless an explicit platform policy is later introduced.

These fields do not replace `expressionSpecification.iri`, `targetEntitySchema`, `specCharacteristic`, or request-specific `serviceType`, `serviceClass`, `priority`, targets, constraints, and preferences inside the governed expression schema.

## 30. specKey lineage note:

`specKey` represents logical grouping across specification versions. If only `RETIRED` versions exist for a `specKey`, ID MS creates a new `id` by default. Lineage reuse of retired specifications is not assumed and requires explicit governance if introduced later.


## 31. draftId provenance lookup rule:

Before activation, `GET /intentSpecification/draft/{draftId}` returns the mutable DRAFT candidate. After activation, the same GET route remains valid as a read-only provenance lookup for the official `IntentSpecification` version produced from that DRAFT candidate.

For produced official versions, the response must show the official `id`, official `version`, carried-forward `draftId`, and lifecycle status. DRAFT mutation links must not be returned after activation. Runtime Intent admission must still reference a concrete ACTIVE `IntentSpecification.id`; `draftId` must not be used for runtime contract selection.

## 32. Runtime admission guardrail:

Runtime Intent admission must reference a concrete ACTIVE `IntentSpecification.id`. `specKey` and `draftId` must not be used for runtime contract selection. DRAFT candidates and RETIRED specifications must not be used for new runtime Intent admission.

## 33. Callback URL baseline:

Callback URLs are subscriber-owned listener endpoints.
Do not imply TM Forum owns subscriber callback URLs. Callback URLs are subscriber-owned, while notification payloads follow TMF-aligned event patterns.
Use neutral listener paths such as:

```text
https://consumer.example.com/listener/intentSpecification/events
```


## 34. PATCH semantics:

`PATCH` uses JSON Merge Patch semantics across the service's external REST API.

All `PATCH` requests must use:

```http
Content-Type: application/merge-patch+json
```

`PATCH` is intended for small targeted updates. For deterministic full replacement of editable Draft resources, use `PUT` where the platform extension is available.



## 35. IntentSpecification versioning clarification:

`IntentSpecification.version` is a design-time contract version and is separate from runtime `Intent.version`.

DRAFT `IntentSpecification` candidates do not expose an official public `version`. Draft revision is represented by `ETag`. Any version indicator during draft authoring is non-authoritative and must not be relied on. DRAFT candidates do not expose or guarantee any version identifier.

Baseline:

- DRAFT candidates do not expose an official public `version`; draft revision is represented by `ETag`.
- Material change after activation requires a new Draft `IntentSpecification` version.
- `ACTIVE` and `RETIRED` specifications are immutable for material contract changes.
- `specKey` is mandatory on create and is used by ID MS to resolve the stable server-assigned `IntentSpecification.id`.
- Runtime `Intent.version` and `IntentSpecification.version` are separate concepts.



## 36. Expression schema alignment:

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
- `expressionSpecification.iri` identifies the semantic and expression contract.
- `specCharacteristic` gives catalogue/discovery summary only.
- Use array-based `targets`, `constraints`, and `preferences` for scalability.
- Keep simplified object-map examples only where they are deliberately explanatory.

