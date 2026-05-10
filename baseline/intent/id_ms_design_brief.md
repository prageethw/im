# id_ms_design_brief.md

## ID MS API contract — baseline:

ID MS owns the definition-time `IntentSpecification` resource and related hub subscriptions.

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Definition MS |
| Short name | ID MS |
| Service name | `intent-definition-ms` |
| Base path | `/intentManagement/v5` |
| Primary resource | `IntentSpecification` |

ID MS owns definition-time `IntentSpecification` contracts and subscription management for specification events. It validates syntax and resource shape, enforces specification lifecycle/version governance, and publishes external specification lifecycle events.

ID MS does not validate runtime semantic feasibility, policy fulfilment, network topology, optimisation, assurance, telemetry, orchestration callbacks, or runtime intent lifecycle truth.

## IntentSpecification resource APIs:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create specification | `POST` | `/intentSpecification` |
| List specifications | `GET` | `/intentSpecification` |
| Retrieve specification by ID | `GET` | `/intentSpecification/{id}` |
| Full replace specification | `PUT` | `/intentSpecification/{id}` |
| Partial update specification | `PATCH` | `/intentSpecification/{id}` |
| Delete / remove specification | `DELETE` | `/intentSpecification/{id}` |

`PUT /intentSpecification/{id}` is an intentional platform extension for deterministic full replacement.

`PATCH /intentSpecification/{id}` remains supported for TMF compatibility, but is discouraged as a general update method.

## Hub subscription APIs:

ID MS intentionally uses domain-scoped hub routes.

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentSpecification/hub` |
| Retrieve subscription by ID | `GET` | `/intentSpecification/hub/{id}` |
| Delete event subscription | `DELETE` | `/intentSpecification/hub/{id}` |

Hub subscriptions are for external `IntentSpecification*Event` notifications only.

They must not expose internal workflow events, KP details, runtime assurance state, telemetry, callback payloads, optimiser decisions, or candidate/resource scoring details.

## Query conventions:

List endpoint:

```http
GET /intentManagement/v5/intentSpecification?offset=0&limit=20&lifecycleStatus=ACTIVE&name=Hospital%20Surgical%20Slice&version=1.19&fields=id,href,familyId,name,version,lifecycleStatus,isBundle,validFor,relatedParty,@type,@baseType
```

Supported query params:

| **Param** | **Meaning** |
|---|---|
| `offset` | Zero-based start position |
| `limit` | Maximum number of records |
| `lifecycleStatus` | Filter by `DRAFT`, `ACTIVE`, or `RETIRED` |
| `name` | Filter by specification name |
| `version` | Filter by specification version |
| `fields` | Optional TMF-style field selection / projection |

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
| `DRAFT` | `PUT`, tightly controlled `PATCH`, `DELETE`, activation | Draft can be edited and governed |
| `ACTIVE` | No material `PUT`, `PATCH`, or `DELETE` | Active specs are immutable |
| `RETIRED` | No material `PUT`, `PATCH`, or `DELETE` | Retired specs are immutable |

Important:

- There is no `DELETED` lifecycle state.
- Delete is an operation/outcome, not a lifecycle status.
- Meaningful change after activation requires a new versioned `IntentSpecification`.
- `PATCH` is supported for TMF compatibility but discouraged as a general update method.
- `PUT` is preferred for deterministic full replacement of editable `DRAFT` specifications.
- Activation is a lifecycle update on `/intentSpecification/{id}`, not a custom `/activate` endpoint.
- When a new version becomes `ACTIVE`, the previous `ACTIVE` version in the same `familyId` becomes `RETIRED`.

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

Missing `If-Match` response:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
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

Stale/mismatched ETag response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
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
POST /intentManagement/v5/intentSpecification?fields=id,href,familyId,name,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Content-Type: application/json
Accept: application/json
```

Create request baseline includes:

- `familyId`
- `name`
- `description`
- `version`
- `lifecycleStatus: DRAFT`
- `isBundle`
- `validFor`
- `relatedParty`
- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`
- `@type: IntentSpecification`
- `@baseType: EntitySpecification`

Create clients must not supply server-generated `_links`.

Success:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/json
Content-Language: en-AU
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
```

Notes:

- Create normally creates a `DRAFT` specification.
- Response returns the full created `IntentSpecification`.
- Response includes server-assigned `id`, `href`, `Location`, `ETag`, and `_links`.
- `Location` points to the new resource.
- `ETag` is mandatory.

## Retrieve IntentSpecification:

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,familyId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
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
- The returned resource includes full `familyId`, `isBundle`, `validFor`, `relatedParty`, `specCharacteristic`, `expressionSpecification`, `targetEntitySchema`, lifecycle status, and `_links`.

## List IntentSpecifications:

The list operation returns a lightweight summary by default.

Default list representation includes:

- `id`
- `href`
- `familyId`
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

## Full update IntentSpecification:

```http
PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,familyId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
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

## Partial update IntentSpecification:

```http
PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/json
Accept: application/json
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

Rules:

- Supported for TMF compatibility.
- Discouraged as a general update method from a platform perspective.
- Use only where a TMF-compatible client cannot use `PUT` or where a tightly controlled, small targeted compatibility update is required.
- Allowed only when `lifecycleStatus = DRAFT`.
- Requires `If-Match`.
- Prefer `PUT` for deterministic full replacement.
- Must not normally be used for material replacement of `familyId`, `version`, `specCharacteristic`, `expressionSpecification`, `targetEntitySchema`, or major lifecycle/version contract identity.

## Delete IntentSpecification:

```http
DELETE /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
Accept: application/json
```

Success:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
```

Rules:

- Allowed only for unused `DRAFT` specifications.
- Not allowed for `ACTIVE`.
- Not allowed for `RETIRED`.
- Delete is blocked if existing runtime intents reference the specification.
- Delete is blocked if audit/retention policy requires preservation.
- Delete does not create `lifecycleStatus = DELETED`.
- Delete emits `IntentSpecificationDeleteEvent` only after successful delete.
- Physical versus logical removal is an implementation detail.

## Activate IntentSpecification:

Activation is a lifecycle update, not a custom action endpoint.

Do not expose:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate
```

Use `PATCH /intentManagement/v5/intentSpecification/{id}` for strict TMF-compatible lifecycle update, or `PUT /intentManagement/v5/intentSpecification/{id}` as the preferred platform extension when the caller sends the full resource.

Although `PATCH` is discouraged as a general update method, it is acceptable for this tightly controlled TMF-compatible lifecycle transition.

Rules:

- Only `DRAFT` can be activated.
- Activated version becomes `ACTIVE`.
- Previous `ACTIVE` version in the same `familyId` becomes `RETIRED`.
- New runtime intent creation must use the new `ACTIVE` version.
- Existing runtime intents referencing retired specs may continue temporarily where safe.
- Missing `If-Match` returns `428`.
- Stale or mismatched `If-Match` returns `412`.
- Invalid lifecycle transition returns `409 Conflict`.
- Activation emits two `IntentSpecificationStatusChangeEvent` events:
  - new version `DRAFT -> ACTIVE`
  - previous active version `ACTIVE -> RETIRED`

## Hub create subscription:

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

## Hub retrieve subscription:

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

## Hub delete subscription:

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
| `412` | `PRECONDITION_FAILED` | Stale or mismatched `If-Match` |
| `422` | `VALIDATION_FAILED` | Fails expression/spec schema constraints |
| `428` | `PRECONDITION_REQUIRED` | Missing required `If-Match` |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

## ID MS API boundary statement:

**ID MS owns definition-time `IntentSpecification` contracts and subscription management for specification events. It validates syntax and resource shape, enforces specification lifecycle/version governance, and publishes external specification lifecycle events. It does not validate runtime semantic feasibility, policy fulfilment, network topology, optimisation, assurance, telemetry, orchestration callbacks, or callback ingestion.**

## Lifecycle and versioning rules:

### Lifecycle state model:

Allowed `IntentSpecification.lifecycleStatus` values:

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DELETED` lifecycle status.

Delete is an operation/outcome, not a normal lifecycle state.

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
- The `familyId` groups related versions of the same specification.
- Only one version in the same `familyId` should be `ACTIVE` for new runtime intent creation.
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
- `targetEntitySchema` references a valid governed expression-value schema artefact
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

## Caching, ETag, and dependency-specific circuit-breaker baseline:

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
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
```

ID MS may return:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
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
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
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
PUT /intentManagement/v5/intentSpecification/{id}
PATCH /intentManagement/v5/intentSpecification/{id}
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
2. ID MS retires the previous active version in the same specification family.
3. ID MS bypasses/refreshes its own cache for that specification family using an internal no-cache/refresh path.
4. ID MS stores the new active version as the current cached active copy.
5. ID MS ensures the previous active version is no longer returned as active.
6. ID MS emits status-change events for:
   - new version becoming `ACTIVE`
   - previous version becoming `RETIRED`

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

ID MS has multiple circuit-breaker trigger points. Different dependency failures have different behaviours.

| **Dependency path** | **CB style** | **Baseline behaviour** |
|---|---|---|
| ID MS -> DB | Hard fail-fast | Return `503`; consumer retries |
| ID MS -> cache | Graceful/silent | Bypass/ignore cache, use DB/source-of-truth, emit telemetry |
| ID MS -> Kafka/event broker | Graceful/silent with outbox | API succeeds after DB + outbox commit; relay retries Kafka later |
| ID MS -> external callback webhook | Async fail-fast per attempt | Delivery attempt fails fast, retries later; original API unaffected |
| IC MS -> ID MS | Cached fallback then fail-closed | IC MS may use fresh cached active spec fallback; otherwise fail closed |

### DB failure:

DB is a hard dependency.

If DB cannot be accessed:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
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

If cache read/write fails:

- trigger cache circuit breaker
- bypass cache where safe
- read from DB/source of truth where needed
- ignore failed cache writes
- continue request when DB/source-of-truth succeeds
- emit logs, metrics, and alerts

Rules:

- cache failure is silent/graceful from the client perspective
- do not return `503` only because cache is unavailable
- cache failure must not block create, update, or read when DB is available

### Kafka / event broker failure:

Kafka is not on the synchronous critical path when ID MS uses transactional outbox.

For create, update, delete, activation, and retirement:

- commit resource change and outbox record transactionally in DB
- return API success once DB + outbox transaction succeeds
- publish to Kafka asynchronously through outbox relay
- if Kafka is unavailable, relay fails fast for that publish attempt
- retry later using outbox retry policy
- do not fail original API call after successful DB/outbox commit

Rules:

- Kafka/event broker failure is graceful/silent for the original API consumer
- Kafka failure is operationally visible through retry metrics and alerts
- if DB/outbox commit fails, API operation fails because durable event publication cannot be guaranteed

### External callback webhook failure:

External subscriber callback delivery is asynchronous.

If callback endpoint is unavailable, times out, or returns failure:

- delivery worker fails fast for that delivery attempt
- mark attempt failed
- retry later using bounded retries and backoff
- do not impact original ID MS resource operation
- if retries are exhausted, mark delivery as failed and alert/operate

Rules:

- webhook failure is graceful/silent from the original API consumer’s point of view
- webhook failure must not roll back specification create, update, status-change, or delete operations
- webhook delivery is not a synchronous dependency for the API write path

### Final combined baseline statement:

**ID MS caching applies only to GET responses. GET responses may use bounded private caching, with longer TTL for single-resource GETs and shorter TTL for list GETs. Clients either use the cached response within TTL or request a fresh copy using `Cache-Control: no-cache`. ETag is not used for GET revalidation; `If-None-Match` and `304 Not Modified` are not baselined. ETag is used only for unsafe operation concurrency through `If-Match`.**

**On active-version promotion, ID MS refreshes its own active-specification cache using a no-cache/internal refresh path so the newly active version becomes the cached active copy and the previous active version is no longer returned as active.**

**ID MS uses dependency-specific circuit-breaker behaviour. Database failure is hard fail-fast and returns `503 Service Unavailable`. Cache failure is handled silently and gracefully by bypassing cache or ignoring cache writes where safe. Kafka/event-broker failure is handled through transactional outbox. External webhook callback failure is handled asynchronously: each failed delivery attempt fails fast, is retried later, and does not affect the original resource API response.**

## Deployment and persistence strategy:

### Runtime model:

ID MS is deployed as a mostly stateless API service.

The service instances can be horizontally scaled behind the API gateway / ingress layer. The application instances should not hold domain truth in local memory.

### Source of truth:

The source of truth for ID MS is a managed PostgreSQL / PostgreSQL-compatible relational database.

ID MS stores and governs:

- `IntentSpecification` resources
- specification versions
- lifecycle status
- hub subscriptions
- outbox records for event publication
- audit-relevant metadata

### Recommended persistence model:

| **Table / store** | **Purpose** |
|---|---|
| `intent_specification` | Stores `IntentSpecification` resource, version, lifecycle, ETag, timestamps, and resource body |
| `intent_specification_subscription` | Stores `/intentSpecification/hub` event subscriptions |
| `outbox_event` | Stores durable events before publication to Kafka/event infrastructure |
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
- event payload snapshot in `outbox_event`

Rationale:

- `IntentSpecification` is naturally document-shaped.
- JSONB supports flexible schema evolution.
- Relational columns still support governance queries such as `id`, `familyId`, `name`, `version`, `lifecycleStatus`, `ETag`, and timestamps.

### Suggested relational columns:

For `intent_specification`:

| **Column** | **Purpose** |
|---|---|
| `id` | Stable specification ID, for example `hospital-surgical-slice-spec-v1.19` |
| `family_id` | Logical specification family, for example `hospital-surgical-slice-spec` |
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

The selected database service/deployment pattern must support future cross-region active-passive DR as use cases expand. Active-active multi-region writes are not baselined initially.

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
| Kafka/outbox relay readiness | Should not block API readiness if DB/outbox commit path is healthy |
| Cache readiness | Should not block API readiness because cache failure is graceful/silent |

Readiness should fail when the DB/source-of-truth path is unavailable.

Readiness should not fail only because cache is unavailable. Kafka/event-broker unavailability should be surfaced through relay metrics/alerts rather than making the ID MS API unavailable when the DB/outbox path is healthy.

### Configuration and secrets:

ID MS configuration should be externalised through platform configuration and secret management.

Examples:

- DB connection settings
- cache endpoint
- Kafka/event broker connection
- outbox relay configuration
- retry/backoff settings
- cache TTL values
- service identity
- callback/event delivery settings
- OAuth/JWT/security settings where applicable

Secrets must not be stored in application images or source files.

### Observability:

ID MS should emit:

- structured application logs
- request metrics
- dependency metrics
- cache hit/miss metrics
- circuit-breaker metrics
- outbox publish metrics
- subscription delivery metrics
- audit/security logs where required
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
- `id_ms_outbox_pending_count`
- `id_ms_outbox_publish_failure_count`
- `id_ms_webhook_delivery_failure_count`

### Security posture:

ID MS should sit behind the platform gateway / ingress security layer.

Security baseline:

- authenticate callers through gateway/platform identity
- authorise create/update/delete/activation operations at the appropriate upstream governance layer
- protect hub subscription creation/deletion
- validate callback URLs according to platform security policy
- apply request-size limits
- log security-relevant administrative operations
- avoid exposing internal DB/cache/broker details in error responses

### Deployment baseline statement:

ID MS application instances are stateless and horizontally scalable.

The source of truth for `IntentSpecification`, hub subscriptions, lifecycle/version state, and outbox records is a managed PostgreSQL-compatible RDBMS. JSONB may be used for document-shaped resource bodies and event snapshots, while relational columns support governance queries, lifecycle/versioning, ETag handling, and operational reporting.

ID MS readiness depends on DB/source-of-truth availability, but cache and Kafka failures are handled gracefully through cache bypass and transactional outbox where possible.

## Security and access-control baseline:

### Authentication:

ID MS sits behind NGW.

NGW performs system-to-system authentication using:

| **Mechanism** | **Purpose** |
|---|---|
| mTLS | Authenticates the calling system/client at transport layer |
| OAuth2 token validation | Validates the calling workload/system token |

### Authorisation boundary:

ID MS does not own business/user-level operation authorisation. Business/user-level authorisation belongs in the OEX layer.

| **Layer** | **Responsibility** |
|---|---|
| OEX | User/business-level access control, entitlement, role checks, and governance workflow permission |
| NGW | System-to-system authentication using mTLS and OAuth2 token validation |
| ID MS | Trusts authenticated platform/system callers and enforces technical resource integrity and governance state-machine rules |

No OAuth2 scopes are assumed. No context-aware authorisation is baselined at NGW.

### ID MS technical integrity responsibilities:

ID MS still enforces:

- valid request shape
- `IntentSpecification` lifecycle rules
- version uniqueness
- one active version per `familyId`
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
- create/delete hub subscription
- technical integrity validation failures where audit is required

Business/user authorisation audit belongs to OEX where that decision is made.

### Baseline statement:

**ID MS is protected behind NGW. NGW performs system-to-system authentication using mTLS and OAuth2 token validation. Business/user-level authorisation is owned by the OEX layer and should not be implemented as operation-level authorisation inside ID MS. ID MS trusts authenticated platform/system callers and enforces technical resource integrity, lifecycle/version governance, validation, ETag/If-Match concurrency rules, and state-machine constraints for `IntentSpecification` resources.**

## Observability and audit baseline:

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

- Accept correlation/trace context from NGW where provided.
- Generate a correlation ID if one is not provided.
- Include correlation ID in structured logs.
- Include correlation ID in emitted events.
- Include correlation ID in outbox records.
- Propagate correlation ID to downstream dependency calls where applicable.
- Do not expose internal trace details in external error bodies.

### Structured logging:

ID MS logs should be structured and machine-readable.

Recommended log fields:

| **Field** | **Purpose** |
|---|---|
| `timestamp` | Event/log time |
| `level` | Log level |
| `service` | `intent-definition-ms` |
| `correlationId` | End-to-end correlation |
| `traceId` | Distributed trace ID where available |
| `operation` | API or internal operation name |
| `resourceId` | IntentSpecification ID where applicable |
| `familyId` | Specification family where applicable |
| `version` | Specification version where applicable |
| `lifecycleStatus` | Current or target lifecycle status where applicable |
| `result` | Success/failure/degraded |
| `reasonCode` | Stable failure/reason code where applicable |

### Sensitive-data logging rule:

ID MS must not log:

- OAuth2 tokens
- mTLS certificate private material
- secrets
- DB credentials
- cache credentials
- Kafka credentials
- full internal connection strings
- sensitive platform headers
- raw internal dependency stack traces in external responses

Internal logs may include sanitized technical details needed for support.

External error responses must remain stable and must not expose DB/cache/Kafka/internal infrastructure details.

### Metrics baseline:

ID MS should emit metrics for API operations, lifecycle transitions, dependency behaviour, caching, outbox/event delivery, and technical integrity validation.

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
| `intent_specification_validation_failure_count` | Count of syntax/schema validation failures |
| `id_ms_db_error_count` | Count of DB/source-of-truth failures |
| `id_ms_db_circuit_breaker_open_count` | Count of DB CB-open events |
| `id_ms_cache_hit_count` | Count of cache hits |
| `id_ms_cache_miss_count` | Count of cache misses |
| `id_ms_cache_bypass_count` | Count of cache bypass events |
| `id_ms_cache_write_failure_count` | Count of ignored cache-write failures |
| `id_ms_outbox_pending_count` | Current pending outbox event count |
| `id_ms_outbox_publish_failure_count` | Count of outbox publish failures |
| `id_ms_webhook_delivery_failure_count` | Count of callback/webhook delivery failures |
| `id_ms_webhook_delivery_retry_count` | Count of callback/webhook retry attempts |

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

Business/user-level authorisation audit belongs to OEX, because OEX owns business/user-level authorisation decisions.

### Audit record fields:

Recommended audit record fields:

| **Field** | **Purpose** |
|---|---|
| `auditId` | Stable audit record ID |
| `timestamp` | Audit event time |
| `service` | `intent-definition-ms` |
| `operation` | Operation performed |
| `resourceId` | Specification or subscription ID |
| `familyId` | Specification family where applicable |
| `version` | Specification version where applicable |
| `previousLifecycleStatus` | Previous status where applicable |
| `newLifecycleStatus` | New status where applicable |
| `correlationId` | End-to-end correlation |
| `callerIdentity` | Authenticated system identity from NGW where available |
| `result` | Success/failure |
| `reasonCode` | Stable reason code for failure or special decision |

### Alerting baseline:

Operational alerts should be raised for:

- DB unavailable / DB circuit breaker open
- repeated DB errors
- outbox backlog above threshold
- repeated Kafka/event publish failures
- repeated webhook delivery failures
- activation failures
- repeated ETag/If-Match conflicts above normal threshold
- high validation failure rate
- cache bypass/failure rate above threshold
- readiness failures
- unexpected error rate increase

### Tracing baseline:

ID MS should participate in distributed tracing.

Trace spans should cover:

- inbound API request
- DB/source-of-truth operation
- cache read/write where applicable
- outbox record creation
- outbox relay publish attempt where applicable
- webhook delivery attempt where applicable

Trace data must not include secrets or sensitive token contents.

### Baseline statement:

**ID MS must log and propagate correlation context, emit structured operational telemetry, and audit technical/governance-changing operations. Business/user authorisation audit remains with OEX, while ID MS audit focuses on specification creation, update, activation, retirement, deletion, hub subscription changes, technical validation failures, ETag/If-Match integrity decisions, immutable-resource enforcement, and dependency failure signals.**

## ID MS consistency sweep:

### Sweep date:

2026-05-11

### Overall result:

**PASS WITH NOTES**

### Checks:

| **Area** | **Result** | **Notes** |
|---|---|---|
| Service naming | PASS | Uses Intent Definition MS / ID MS / `intent-definition-ms` |
| Lifecycle states | PASS | Uses `DRAFT`, `ACTIVE`, `RETIRED`; no `DELETED` lifecycle state |
| GET-only caching | PASS | Caching is scoped to GET responses only |
| No GET ETag revalidation | PASS | `If-None-Match` and `304 Not Modified` are not baselined |
| ETag unsafe concurrency | PASS | ETag is positioned for `If-Match` unsafe operation concurrency |
| Dependency-specific circuit breakers | PASS | DB/cache/Kafka/webhook behaviours are present |
| Security boundary | PASS | NGW authentication and OEX authorisation boundary preserved |
| Eventing boundary | PASS | External `IntentSpecification*Event` family and boundary are present |
| Persistence baseline | PASS | PostgreSQL-compatible RDBMS, JSONB, and outbox persistence are present |
| Boundary exclusions | PASS | ID MS does not own runtime fulfilment concerns |
| Platform extensions | PASS | `PUT`, domain-scoped hub, `familyId`, `_links`, ETag/If-Match, and caching are documented |

### Notes requiring attention:

- Domain-scoped `/intentSpecification/hub` route is intentional.
- `PUT` full replacement is intentional platform extension.
- `PATCH` remains supported for TMF compatibility, but is discouraged generally.
- `targetEntitySchema` is retained as the governed runtime expression-value schema reference.
- `familyId` is retained for version-family governance.

### Final consistency position:

The ID MS design brief is internally consistent for the current baseline.

The design keeps ID MS focused on definition-time `IntentSpecification` resource ownership, lifecycle/version governance, syntax/resource-shape validation, ETag/If-Match concurrency, GET-only caching, external `IntentSpecification*Event` publication, PostgreSQL-compatible persistence, and technical observability/audit. ID MS does not own semantic validation, policy validation, candidate/resource feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

## Callback URL baseline:

Callback URLs are subscriber-owned listener endpoints.

Do not use TMF-specific path prefixes or TMF-owned path wording in callback URL examples.

Use neutral listener paths such as:

```text
https://consumer.example.com/listener/intentSpecification/events
```
