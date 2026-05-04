# id_ms_design_brief.md

## ID MS API contract — baseline:

ID MS owns the design-time `IntentSpecification` resource and related hub subscriptions.

Service:

```text
intent-definition-ms
```

Base path:

```http
/intentManagement/v5
```

## IntentSpecification resource APIs:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create specification | `POST` | `/intentSpecification` |
| List specifications | `GET` | `/intentSpecification` |
| Retrieve specification by ID | `GET` | `/intentSpecification/{id}` |
| Full replace specification | `PUT` | `/intentSpecification/{id}` |
| Partial update specification | `PATCH` | `/intentSpecification/{id}` |
| Delete / remove specification | `DELETE` | `/intentSpecification/{id}` |

## Hub subscription APIs:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentSpecification/hub` |
| Delete event subscription | `DELETE` | `/intentSpecification/hub/{id}` |
| Retrieve subscription by ID | `GET` | `/intentSpecification/hub/{id}` |

## Query conventions:

List endpoint:

```http
GET /intentManagement/v5/intentSpecification?offset=0&limit=20&lifecycleStatus=ACTIVE&name=Hospital%20Surgical%20Slice&version=1.19
```

Supported query params:

| **Param** | **Meaning** |
|---|---|
| `offset` | Zero-based start position |
| `limit` | Maximum number of records |
| `lifecycleStatus` | Filter by `DRAFT`, `ACTIVE`, or `RETIRED` |
| `name` | Filter by specification name |
| `version` | Filter by specification version |

Response headers:

```http
X-Total-Count: 1
X-Result-Count: 1
ETag: "list-etag-value"
Cache-Control: private, max-age=60
```

## Lifecycle rules:

Allowed lifecycle states:

```text
DRAFT
ACTIVE
RETIRED
```

Rules:

| **Current state** | **Allowed write operations** | **Rule** |
|---|---|---|
| `DRAFT` | `PUT`, `PATCH`, `DELETE`, activation | Draft can be edited |
| `ACTIVE` | No `PUT`, `PATCH`, or `DELETE` | Active specs are immutable |
| `RETIRED` | No `PUT`, `PATCH`, or `DELETE` | Retired specs are immutable |

Important:

- There is no `DELETED` lifecycle state.
- Delete is an operation/outcome, not a lifecycle status.
- Meaningful change after activation requires a new versioned `IntentSpecification`.
- `PATCH` is supported for compatibility but discouraged.
- `PUT` is preferred for deterministic full updates.

## ETag / If-Match rules:

| **Operation** | **ETag / If-Match rule** |
|---|---|
| `POST /intentSpecification` | Response must include `ETag` |
| `GET /intentSpecification/{id}` | Response must include `ETag` |
| `GET /intentSpecification` | Response should include list-level `ETag` |
| `PUT /intentSpecification/{id}` | Request must include `If-Match` |
| `PATCH /intentSpecification/{id}` | Request must include `If-Match` |
| `DELETE /intentSpecification/{id}` | Request must include `If-Match` |
| `POST /intentSpecification/hub` | Response must include `ETag` |
| `DELETE /intentSpecification/hub/{id}` | Request must include `If-Match` |

Stale/mismatched ETag response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
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

## Create IntentSpecification:

```http
POST /intentManagement/v5/intentSpecification
Content-Type: application/json
Accept: application/json
```

Success:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/json
Content-Language: en-AU
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
Cache-Control: no-store
```

Notes:

- Create normally creates a `DRAFT` specification.
- Response returns the full created `IntentSpecification`.
- `Location` points to the new resource.
- `ETag` is mandatory.

## Retrieve IntentSpecification:

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Accept: application/json
```

Success:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
Cache-Control: private, max-age=300
```

Notes:

- `GET` can be cached privately.
- IC MS may use this to validate incoming runtime `Intent` requests.
- The returned resource includes full `specCharacteristic`, `expressionSpecification`, lifecycle status, and `_links`.

## Full update IntentSpecification:

```http
PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/json
Accept: application/json
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

Success:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v2"
Cache-Control: no-store
```

Rules:

- Allowed only when `lifecycleStatus = DRAFT`.
- Requires `If-Match`.
- Returns full updated representation.
- Preferred over `PATCH`.

If resource is `ACTIVE`:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Cache-Control: no-store
```

```json
{
  "code": "RESOURCE_IMMUTABLE",
  "reason": "ACTIVE_SPECIFICATION_IMMUTABLE",
  "message": "ACTIVE IntentSpecification resources cannot be updated. Create a new versioned DRAFT specification instead.",
  "status": 409,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_IMMUTABLE",
  "@type": "Error"
}
```

## Partial update IntentSpecification:

```http
PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/json
Accept: application/json
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

Rules:

- Supported for compatibility.
- Discouraged from a platform perspective.
- Allowed only when `lifecycleStatus = DRAFT`.
- Requires `If-Match`.
- Should return full updated representation.
- Prefer `PUT` for deterministic full replacement.

## Delete IntentSpecification:

```http
DELETE /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

Success:

```http
HTTP/1.1 204 No Content
Cache-Control: no-store
```

Rules:

- Allowed only for `DRAFT` specifications where no active/runtime references block deletion.
- Not allowed for `ACTIVE` or `RETIRED` unless a separately approved tombstone/retention policy permits it.
- Delete does not create `lifecycleStatus = DELETED`.

## Hub create subscription:

```http
POST /intentManagement/v5/intentSpecification/hub
Content-Type: application/json
Accept: application/json
```

```json
{
  "callback": "https://consumer.example.com/tmf/intentSpecification/events",
  "query": "eventType=IntentSpecificationStatusChangeEvent",
  "@type": "EventSubscription"
}
```

Success:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hub/sub-001
Content-Type: application/json
ETag: "subscription-sub-001-v1"
Cache-Control: no-store
```

```json
{
  "id": "sub-001",
  "callback": "https://consumer.example.com/tmf/intentSpecification/events",
  "query": "eventType=IntentSpecificationStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-001"
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

## Hub delete subscription:

```http
DELETE /intentManagement/v5/intentSpecification/hub/sub-001
If-Match: "subscription-sub-001-v1"
```

Success:

```http
HTTP/1.1 204 No Content
Cache-Control: no-store
```

## Standard error body:

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
| `412` | `PRECONDITION_FAILED` | Missing/mismatched `If-Match` |
| `422` | `VALIDATION_FAILED` | Fails expression/spec schema constraints |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

## ID MS API boundary statement:

**ID MS owns design-time `IntentSpecification` contracts and subscription management for specification events. It validates syntax and resource shape, enforces specification lifecycle/version governance, and publishes external specification lifecycle events. It does not validate runtime semantic feasibility, policy fulfilment, network topology, optimisation, assurance, telemetry, or callbacks.**

## Lifecycle and versioning rules:

### Lifecycle state model:

Allowed `IntentSpecification.lifecycleStatus` values:

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DELETED` lifecycle status. Delete is an operation/outcome, not a normal lifecycle state.

### Lifecycle transitions:

| **Transition** | **Allowed** | **Rule** |
|---|---:|---|
| Create -> `DRAFT` | Yes | New specifications are created as drafts by default |
| `DRAFT` -> `ACTIVE` | Yes | Activation makes this version available for new runtime `Intent` creation |
| `ACTIVE` -> `RETIRED` | Yes | Usually occurs when a newer version becomes active |
| `DRAFT` -> deleted | Yes, conditional | Allowed only if unused and not referenced |
| `ACTIVE` -> deleted | No by default | Active specifications are immutable and protected |
| `RETIRED` -> deleted | No by default | Retired specifications remain for audit/runtime compatibility unless tombstone policy is approved |
| Any state -> `DELETED` | No | `DELETED` is not a lifecycle status |

### Versioning rules:

- Each meaningful change after activation requires a new versioned `IntentSpecification`.
- A new version starts as `DRAFT`.
- Only one version in the same specification family should be `ACTIVE` for new runtime intent creation.
- When a new version becomes `ACTIVE`, the previous active version moves to `RETIRED`.
- Retired specifications must not be used for new `Intent` creation.
- Existing runtime intents that reference a retired specification may continue temporarily where safe.
- Preferred long-term treatment is to migrate existing intents to the new active specification version where safe, or terminate and recreate them.

### Specification family rule:

A specification family is the logical grouping of related versions of the same specification.

Example family:

```text
hospital-surgical-slice-spec
```

Example versions:

```text
hospital-surgical-slice-spec-v1.18
hospital-surgical-slice-spec-v1.19
hospital-surgical-slice-spec-v1.20
```

Only one version in that family should be `ACTIVE` for new runtime intent creation.

### Mutability rules:

| **Lifecycle status** | **Mutable?** | **Reason** |
|---|---:|---|
| `DRAFT` | Yes | Draft is still under design/governance |
| `ACTIVE` | No | Active contract must be stable for runtime clients and IC MS validation |
| `RETIRED` | No | Retired contract must remain stable for audit and existing runtime references |

### Runtime compatibility rules:

- IC MS must validate new runtime `Intent` creation only against an `ACTIVE` `IntentSpecification`.
- If a submitted intent references a `DRAFT` specification, IC MS rejects it.
- If a submitted intent references a `RETIRED` specification for new creation, IC MS rejects it.
- Existing intents that were created against a now-retired specification may continue temporarily if platform policy allows.
- Existing intents should be migrated to the new active specification version only through a controlled intent update/recreate flow.

### Activation governance rules:

Activation should only be allowed when:

- the specification is syntactically valid
- the `expressionSpecification` is valid
- required `specCharacteristic` entries are present
- the version identifier is unique
- there is no conflicting active version in the same family, or the activation operation also retires the previous active version
- governance approval has been completed where required

### Delete rules:

Delete is allowed only for unused `DRAFT` specifications.

Delete is blocked when:

- the specification is `ACTIVE`
- the specification is `RETIRED`
- existing runtime intents reference the specification
- audit/retention policy requires preservation

Delete success returns `204 No Content` and does not create `lifecycleStatus = DELETED`.

## Caching and circuit-breaker strategy:

### Caching purpose:

ID MS supports safe caching for read operations so IC MS and other consumers can reduce repeated `IntentSpecification` lookups.

Caching must not weaken specification governance or allow stale specifications to be used indefinitely.

### HTTP caching rules:

| **Operation** | **Caching rule** |
|---|---|
| `GET /intentSpecification/{id}` | Private cache allowed with `ETag` and bounded freshness |
| `GET /intentSpecification` | Private list cache allowed with short TTL |
| `POST /intentSpecification` | `Cache-Control: no-store` |
| `PUT /intentSpecification/{id}` | `Cache-Control: no-store` |
| `PATCH /intentSpecification/{id}` | `Cache-Control: no-store` |
| `DELETE /intentSpecification/{id}` | `Cache-Control: no-store` |
| Error responses | `Cache-Control: no-store` |
| Hub subscription writes | `Cache-Control: no-store` |

### Single-resource GET caching:

For `GET /intentManagement/v5/intentSpecification/{id}`, ID MS should return:

```http
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
Cache-Control: private, max-age=300
```

Rules:

- `ETag` is mandatory.
- `Cache-Control` should be private by default.
- Clients should revalidate when correctness matters.
- IC MS may cache active specifications for syntactic validation within a configured freshness window.

### IC MS cached active specification fallback:

IC MS may use a cached `ACTIVE` `IntentSpecification` for new runtime `Intent` syntactic validation only when all of the following are true:

- the cached specification is within the configured freshness window
- the cached specification lifecycle is `ACTIVE`
- the cached specification ID/version matches the runtime intent reference
- the cached specification includes the required `expressionSpecification`
- the cached specification has not been explicitly invalidated by an ID MS status-change event or cache refresh signal
- the degraded dependency path is logged and monitored

If any of these conditions are not true, IC MS must fail closed for new runtime intent creation when ID MS availability prevents confirmation.

### Fail-closed rule:

If ID MS is unavailable and IC MS has no valid fresh cached `ACTIVE` specification, IC MS must reject new runtime intent creation with:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Cache-Control: no-store
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

### Active-version promotion cache invalidation:

When a new version of an `IntentSpecification` is promoted to `ACTIVE`, ID MS must invalidate old active-specification caches and refresh consumers with the new active copy.

Baseline behaviour:

- the newly promoted active specification write/activation response must use `Cache-Control: no-store`
- ID MS emits `IntentSpecificationStatusChangeEvent` for the newly active version
- ID MS emits `IntentSpecificationStatusChangeEvent` for the previous active version moving to `RETIRED`
- IC MS must treat those status-change events as cache invalidation signals for the affected specification family
- IC MS must evict the previous active version from its active-spec validation cache
- IC MS should fetch and cache the new active version before accepting new runtime intents for that specification family where possible
- if IC MS cannot refresh the new active copy and no valid fresh cache exists, it must fail closed for new runtime intent creation

### Cache refresh after active promotion:

Recommended refresh flow:

```text
ID MS promotes v1.20 to ACTIVE
ID MS retires previous ACTIVE v1.19
ID MS emits status-change events for v1.20 and v1.19
IC MS receives event
IC MS invalidates cached active spec for the family
IC MS fetches v1.20 from ID MS
IC MS stores v1.20 as the current active validation copy
```

### Stale-cache protection:

IC MS must not use a cached specification when:

- the cache freshness window has expired
- the cached lifecycle is not `ACTIVE`
- the specification family has received a status-change invalidation event
- the runtime intent references a different version
- the expression schema is missing or invalid
- the cache entry cannot be tied to a valid `ETag`

### ID MS circuit-breaker strategy:

| **Dependency path** | **Circuit-breaker behaviour** |
|---|---|
| ID MS -> DB | Fail fast when open; return `503` for operations needing DB access |
| ID MS -> event publisher/outbox | Use outbox-first where possible; do not lose committed resource changes |
| ID MS -> external callback delivery | Delivery retry/failure handled by event delivery layer; resource operation should not depend on synchronous callback delivery |
| IC MS -> ID MS | IC MS may use fresh cached active spec fallback; otherwise fail closed |

### Observability requirements:

ID MS and IC MS should expose metrics/logs for:

- active specification cache hit count
- active specification cache miss count
- active specification cache invalidation count
- stale cache rejection count
- fail-closed due to ID MS unavailable
- ID MS DB circuit-breaker open count
- ID MS event publication failure count
- IC MS validation using cached active specification count

### Baseline statement:

IC MS may use a cached `ACTIVE` `IntentSpecification` within a configured freshness window for runtime intent creation. When a new specification version is promoted to `ACTIVE`, old active-spec caches must be invalidated through no-store write responses and status-change events, and IC MS must refresh its cache with the new active copy. If the active specification cannot be confirmed from ID MS or a valid fresh cache, IC MS fails closed for new runtime intent creation.
