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
