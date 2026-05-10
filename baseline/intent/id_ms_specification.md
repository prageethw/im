# id_ms_specification.md

## ID MS Specification

### Service identity

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Design MS |
| Short name | ID MS |
| Service name | `intent-design-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `IntentSpecification` |
| Primary responsibility | Design-time `IntentSpecification` catalogue, lifecycle/version governance, syntax contract, and external specification events |

### Boundary statement

ID MS owns design-time `IntentSpecification` contracts and subscription management for specification events.

ID MS validates syntax/resource shape and enforces specification lifecycle/version governance. ID MS does not own runtime `Intent`, `IntentReport`, semantic validation, policy validation, network/resource feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

---

## 1. API endpoints

### IntentSpecification resource APIs

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create specification | `POST` | `/intentManagement/v5/intentSpecification` |
| List specifications | `GET` | `/intentManagement/v5/intentSpecification` |
| Retrieve specification by ID | `GET` | `/intentManagement/v5/intentSpecification/{id}` |
| Full replace specification | `PUT` | `/intentManagement/v5/intentSpecification/{id}` |
| Partial update specification | `PATCH` | `/intentManagement/v5/intentSpecification/{id}` |
| Delete specification | `DELETE` | `/intentManagement/v5/intentSpecification/{id}` |
| Activate specification | `PUT` / `PATCH` | `/intentManagement/v5/intentSpecification/{id}` |

### Hub subscription APIs

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/intentSpecification/hub` |
| Retrieve subscription by ID | `GET` | `/intentManagement/v5/intentSpecification/hub/{id}` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/intentSpecification/hub/{id}` |

---

## 2. Common conventions

### Lifecycle values

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DELETED` lifecycle status. Delete is an operation/outcome, not a normal lifecycle state.

### Versioning rules

- New specifications are normally created as `DRAFT`.
- `DRAFT` specifications are editable.
- `ACTIVE` and `RETIRED` specifications are immutable.
- Meaningful change after activation requires a new versioned `IntentSpecification`.
- Only one version in the same specification family should be `ACTIVE` for new runtime intent creation.
- Activating a new version retires the previous active version.
- Retired specifications must not be used for new runtime `Intent` creation.
- Existing runtime intents that reference a retired specification may continue temporarily where safe.

### Caching and ETag rules

- Caching applies only to GET responses.
- Single-resource GET responses may use private cache with bounded TTL.
- List GET responses may use shorter private cache with bounded TTL.
- Clients may request a fresh GET response with `Cache-Control: no-cache`.
- ETag is not used for GET revalidation.
- `If-None-Match` and `304 Not Modified` are not baselined.
- ETag is used only for unsafe operation concurrency through `If-Match`.
- No caching strategy is baselined for non-GET operations.

### Query parameter conventions

The following query parameters are supported where applicable:

| **Parameter** | **Applies to** | **Purpose** |
|---|---|---|
| `offset` | List | Zero-based result offset for pagination |
| `limit` | List | Maximum number of results returned |
| `fields` | Create, list, retrieve, update | Optional TMF-style field selection / projection parameter |
| `lifecycleStatus` | List | Filter specifications by lifecycle state |
| `name` | List | Filter specifications by name |
| `version` | List | Filter specifications by version |

`fields` is supported for TMF compatibility. When omitted, ID MS returns the default representation for the operation.

---

## 3. Common error body

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

### Common errors

| **HTTP** | **Code** | **Scenario** |
|---:|---|---|
| `400` | `BAD_REQUEST` | Invalid JSON or invalid request structure |
| `404` | `RESOURCE_NOT_FOUND` | Specification or subscription not found |
| `409` | `RESOURCE_IMMUTABLE` | Attempt to update active/retired specification |
| `409` | `VERSION_CONFLICT` | Duplicate specification/version conflict |
| `412` | `PRECONDITION_FAILED` | Supplied `If-Match` does not match the current resource version |
| `422` | `VALIDATION_FAILED` | Fails expression/spec schema constraints |
| `428` | `PRECONDITION_REQUIRED` | Required `If-Match` header is missing for an unsafe operation |
| `503` | `SERVICE_UNAVAILABLE` | Source-of-truth DB unavailable |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

### Missing If-Match response

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

### ETag mismatch response

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

---

## 4. Create IntentSpecification

### Request

```http
POST /intentManagement/v5/intentSpecification?fields=id,href,name,version,lifecycleStatus,@type,@baseType
Content-Type: application/json
Accept: application/json
```

```json
{
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Design-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19.schema.json",
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "id": "context",
      "name": "context",
      "description": "Top-level semantic context supported by this IntentSpecification. The context contains canonical context.targets, context.constraints, and context.preferences. Detailed field rules are defined in the expression-value schema referenced by targetEntitySchema.@schemaLocation.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "object",
          "isDefault": true,
          "value": {
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
      ]
    }
  ],
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JsonLdExpression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.19.expression.schema.json",
    "schemaVersion": "1.19",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  },
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

### Success response

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/json
Content-Language: en-AU
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": "...same as request...",
  "expressionSpecification": "...same as request...",
  "targetEntitySchema": "...same as request...",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "fullUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but discouraged. Prefer PUT for deterministic full replacement."
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "DELETE"
    }
  }
}
```

---

## 5. List IntentSpecifications

### Request

```http
GET /intentManagement/v5/intentSpecification?offset=0&limit=10&lifecycleStatus=ACTIVE&fields=id,href,name,version,lifecycleStatus,@type,@baseType
Accept: application/json
```

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Total-Count: 1
X-Result-Count: 1
ETag: "intent-spec-list-active-v17"
Cache-Control: private, max-age=60
```

```json
[
  {
    "id": "hospital-surgical-slice-spec-v1.19",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
    "name": "Hospital Surgical Slice Intent Specification",
    "version": "1.19",
    "lifecycleStatus": "ACTIVE",
    "@type": "IntentSpecification",
    "@baseType": "EntitySpecification",
    "_links": {
      "self": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "partialUpdate": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "method": "PATCH",
        "warning": "PATCH is supported for compatibility but discouraged. Prefer PUT for deterministic full replacement."
      }
    }
  }
]
```

---

## 6. Retrieve IntentSpecification

### Request

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,name,description,version,lifecycleStatus,specCharacteristic,expressionSpecification,@type,@baseType
Accept: application/json
```

### Request with cache override

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,name,description,version,lifecycleStatus,specCharacteristic,expressionSpecification,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
Cache-Control: private, max-age=300
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Design-time specification for hospital surgical slice intents.",
  "version": "1.19",
  "lifecycleStatus": "ACTIVE",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": "...bucket catalogue with example/default characteristicValueSpecification values...",
  "expressionSpecification": "...full expression schema...",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but discouraged. Prefer PUT for deterministic full replacement."
    }
  }
}
```

### Not found response

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
```

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "reason": "INTENT_SPECIFICATION_NOT_FOUND",
  "message": "IntentSpecification hospital-surgical-slice-spec-v1.19 was not found.",
  "status": 404,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",
  "@type": "Error"
}
```

---

## 7. Full update IntentSpecification

### Request

```http
PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,name,description,version,lifecycleStatus,@type,@baseType
Content-Type: application/json
Accept: application/json
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated draft description.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": [],
  "expressionSpecification": {}
}
```

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v2"
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated draft description.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

### Immutable resource response

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
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

### Missing If-Match response

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

### ETag mismatch response

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

---

## 8. Partial update IntentSpecification

### Request

```http
PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,name,description,version,lifecycleStatus,@type,@baseType
Content-Type: application/json
Accept: application/json
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

```json
{
  "description": "Updated draft description only."
}
```

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v2"
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated draft description only.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but discouraged. Prefer PUT for deterministic full replacement."
    }
  }
}
```

---

## 9. Delete IntentSpecification

### Request

```http
DELETE /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

### Success response

```http
HTTP/1.1 204 No Content
```

### Rule

- Delete is allowed only for unused `DRAFT` specifications.
- Delete is blocked for `ACTIVE` and `RETIRED` specifications.
- Delete does not create `lifecycleStatus = DELETED`.

### Delete blocked response

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "RESOURCE_IMMUTABLE",
  "reason": "SPECIFICATION_DELETE_NOT_ALLOWED",
  "message": "IntentSpecification cannot be deleted because it is active, retired, or referenced by runtime resources.",
  "status": 409,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_IMMUTABLE",
  "@type": "Error"
}
```

---

## 10. Activate IntentSpecification through lifecycle update

Activation is not exposed through a custom action endpoint.

Do not use:

```http
POST /intentManagement/v5/intentSpecification/{id}
```

Use the existing TMF-style resource update endpoint instead.

### PATCH request

```http
PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20?fields=id,href,familyId,name,version,lifecycleStatus,previousActiveSpecification,@type,@baseType
Content-Type: application/json
Accept: application/json
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.20-v1"
```

```json
{
  "lifecycleStatus": "ACTIVE"
}
```

### PUT request option

`PUT` may also be used when the caller sends the full replacement representation with:

```json
{
  "lifecycleStatus": "ACTIVE"
}
```

as part of the complete `IntentSpecification` resource.

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20
ETag: "intent-spec-hospital-surgical-slice-spec-v1.20-v2"
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.20",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20",
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "version": "1.20",
  "lifecycleStatus": "ACTIVE",
  "previousActiveSpecification": {
    "id": "hospital-surgical-slice-spec-v1.19",
    "lifecycleStatus": "RETIRED",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

### Rules

- Activation is represented as a lifecycle/status update on the `IntentSpecification` resource.
- Use `PUT` or `PATCH` against `/intentSpecification/{id}`.
- `PUT` is preferred for deterministic full replacement.
- `PATCH` is supported for TMF compatibility but is not encouraged for ordinary edits.
- The requested target version changes from `DRAFT` to `ACTIVE`.
- ID MS retires the previous active version in the same specification family.
- ID MS refreshes its own active-spec cache through an internal no-cache/refresh path.
- ID MS emits status-change events for the new active version and the previous retired version.

---

## 11. Hub create subscription

### Request

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

### Success response

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hub/sub-001
Content-Type: application/json
ETag: "subscription-sub-001-v1"
```

```json
{
  "id": "sub-001",
  "callback": "https://consumer.example.com/listener/intentSpecification/events",
  "query": "eventType=IntentSpecificationStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-001"
    }
  }
}
```

---

## 12. Hub retrieve subscription

### Request

```http
GET /intentManagement/v5/intentSpecification/hub/sub-001
Accept: application/json
```

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "subscription-sub-001-v1"
```

```json
{
  "id": "sub-001",
  "callback": "https://consumer.example.com/listener/intentSpecification/events",
  "query": "eventType=IntentSpecificationStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-001"
    }
  }
}
```

---

## 13. Hub delete subscription

### Request

```http
DELETE /intentManagement/v5/intentSpecification/hub/sub-001
If-Match: "subscription-sub-001-v1"
```

### Success response

```http
HTTP/1.1 204 No Content
```

---

## 14. DB unavailable response

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

---

## 15. External event family

ID MS emits external TMF-style resource events for `IntentSpecification` changes.

| **Event** | **Trigger** |
|---|---|
| `IntentSpecificationCreateEvent` | New `IntentSpecification` created |
| `IntentSpecificationAttributeValueChangeEvent` | Editable draft attributes changed |
| `IntentSpecificationStatusChangeEvent` | Lifecycle status changes, such as `DRAFT -> ACTIVE` or `ACTIVE -> RETIRED` |
| `IntentSpecificationDeleteEvent` | Draft specification deleted |

These are external subscription events for the `IntentSpecification` resource.

They are not internal fulfilment events and must not expose II MS semantic validation details, lightweight II MS KP details, `t7.knowledge plane` data, optimiser decisions, runtime assurance state, telemetry, callback payloads, or internal candidate/resource scoring details.

---

## 16. Event envelope pattern

```json
{
  "eventId": "evt-intent-spec-001",
  "eventTime": "2026-04-18T12:00:00+10:00",
  "eventType": "IntentSpecificationStatusChangeEvent",
  "correlationId": "corr-intent-spec-001",
  "description": "IntentSpecification lifecycle status changed.",
  "priority": "Normal",
  "title": "IntentSpecification status changed",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.19",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.19",
      "lifecycleStatus": "ACTIVE",
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    }
  },
  "reportingSystem": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "source": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "@type": "IntentSpecificationStatusChangeEvent"
}
```

---

## 17. IntentSpecificationCreateEvent

```json
{
  "eventId": "evt-intent-spec-create-001",
  "eventTime": "2026-04-18T12:00:00+10:00",
  "eventType": "IntentSpecificationCreateEvent",
  "correlationId": "corr-intent-spec-create-001",
  "description": "IntentSpecification created.",
  "priority": "Normal",
  "title": "IntentSpecification created",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.19",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.19",
      "lifecycleStatus": "DRAFT",
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    }
  },
  "reportingSystem": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "source": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "@type": "IntentSpecificationCreateEvent"
}
```

---

## 18. IntentSpecificationAttributeValueChangeEvent

```json
{
  "eventId": "evt-intent-spec-attr-001",
  "eventTime": "2026-04-18T12:05:00+10:00",
  "eventType": "IntentSpecificationAttributeValueChangeEvent",
  "correlationId": "corr-intent-spec-attr-001",
  "description": "IntentSpecification draft attributes changed.",
  "priority": "Normal",
  "title": "IntentSpecification attributes changed",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.19",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.19",
      "lifecycleStatus": "DRAFT",
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    },
    "changedAttributes": [
      {
        "name": "description",
        "oldValue": "Design-time specification for hospital surgical slice intents.",
        "newValue": "Updated draft description only."
      }
    ]
  },
  "reportingSystem": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "source": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "@type": "IntentSpecificationAttributeValueChangeEvent"
}
```

---

## 19. IntentSpecificationStatusChangeEvent

```json
{
  "eventId": "evt-intent-spec-status-001",
  "eventTime": "2026-04-18T12:10:00+10:00",
  "eventType": "IntentSpecificationStatusChangeEvent",
  "correlationId": "corr-intent-spec-status-001",
  "description": "IntentSpecification lifecycle status changed.",
  "priority": "Normal",
  "title": "IntentSpecification status changed",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.20",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.20",
      "lifecycleStatus": "ACTIVE",
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    },
    "previousLifecycleStatus": "DRAFT",
    "newLifecycleStatus": "ACTIVE"
  },
  "reportingSystem": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "source": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "@type": "IntentSpecificationStatusChangeEvent"
}
```

---

## 20. IntentSpecificationDeleteEvent

```json
{
  "eventId": "evt-intent-spec-delete-001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentSpecificationDeleteEvent",
  "correlationId": "corr-intent-spec-delete-001",
  "description": "Unused draft IntentSpecification deleted.",
  "priority": "Normal",
  "title": "IntentSpecification deleted",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.18-draft",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.18-draft",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.18-draft",
      "lifecycleStatus": "DRAFT",
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    }
  },
  "reportingSystem": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "source": {
    "id": "intent-design-ms",
    "name": "Intent Design MS"
  },
  "@type": "IntentSpecificationDeleteEvent"
}
```

---

## 21. Final specification notes

- `@baseType` is `EntitySpecification`, not `ResourceSpecification`.
- `specCharacteristic` is the high-level characteristic catalogue.
- `expressionSpecification` is the authoritative request-shape schema.
- `characteristicValueSpecification` is used only for defaults, examples, or constrained allowed values where useful.
- Numeric SLA values in `characteristicValueSpecification` are illustrative/default guidance only, not semantic enforcement.
- ID MS validates resource shape and syntax.
- II MS and knowledge sources own semantic/policy validation.
- IA MS owns runtime assurance.
- `timeWindow.startDateTime` is required when `timeWindow` is present.
- `priority` values are `critical`, `high`, and `standard`.
- Use `priority`, not `priority_level`.
- Do not use `clinical-critical`; use `critical`.
- Do not use `DELETED` as an `IntentSpecification.lifecycleStatus`.
- ETag is used for unsafe-operation concurrency only.
- Caching is GET-only.
- `If-None-Match` and `304 Not Modified` are not baselined.
- Missing required `If-Match` returns `428 Precondition Required`.
- Stale or mismatched `If-Match` returns `412 Precondition Failed`.
- `fields` is supported as an optional TMF-style field selection parameter.
- Activation is represented through PUT/PATCH lifecycle update, not a custom action endpoint.

---

## TMF compliance and platform extension baseline

### Strict TMF-facing baseline

For strict TMF alignment, ID MS supports the TMF-style `IntentSpecification` operations:

| **Operation** | **Endpoint** | **Position** |
|---|---|---|
| Create | `POST /intentManagement/v5/intentSpecification` | TMF-aligned |
| List | `GET /intentManagement/v5/intentSpecification` | TMF-aligned |
| Retrieve | `GET /intentManagement/v5/intentSpecification/{id}` | TMF-aligned |
| Partial update | `PATCH /intentManagement/v5/intentSpecification/{id}` | TMF-aligned |
| Delete | `DELETE /intentManagement/v5/intentSpecification/{id}` | TMF-aligned |
| Event subscription | `/hub` and `/hub/{id}` | Strict TMF route form where required |

### Accepted platform extensions

Controlled platform extensions are acceptable when they are documented, non-breaking, and do not conflict with TMF semantics.

For ID MS, accepted platform extensions are:

| **Extension** | **Purpose** | **Rule** |
|---|---|---|
| `PUT /intentManagement/v5/intentSpecification/{id}` | Deterministic full replacement | Preferred platform update method where supported |
| `/intentManagement/v5/intentSpecification/hub` | Domain-scoped event subscription route | Allowed as a clearer domain-owned route when deliberately chosen |
| `/intentManagement/v5/intentSpecification/hub/{id}` | Domain-scoped subscription delete/retrieve route | Allowed as a clearer domain-owned route when deliberately chosen |

### Update method rule

`PATCH` is the strict TMF-compatible update operation.

`PUT` is the platform extension for deterministic full replacement and is preferred from the platform engineering perspective where clients support it. `PATCH` remains supported for TMF compatibility but is not encouraged for ordinary edits when deterministic full replacement is available.

### Lifecycle activation rule

Activation/retirement is represented as a resource update to `IntentSpecification.lifecycleStatus`.

Use:

```http
PATCH /intentManagement/v5/intentSpecification/{id}
```

for strict TMF compatibility.

Use:

```http
PUT /intentManagement/v5/intentSpecification/{id}
```

as a platform extension when performing deterministic full replacement.

Do not expose custom lifecycle action endpoints such as:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate
```

### Hub route rule

For strict TMF route compatibility, use:

```http
POST /intentManagement/v5/hub
DELETE /intentManagement/v5/hub/{id}
```

For domain-scoped platform extension routing, ID MS may expose:

```http
POST /intentManagement/v5/intentSpecification/hub
GET /intentManagement/v5/intentSpecification/hub/{id}
DELETE /intentManagement/v5/intentSpecification/hub/{id}
```

The domain-scoped route is acceptable only as a documented platform extension and must preserve the same subscription semantics.

### Baseline statement

ID MS and IC MS remain TMF-aligned at the external contract level. Controlled platform extensions are allowed when documented, non-breaking, and semantically compatible with TMF. For ID MS, `PATCH /intentSpecification/{id}` is the strict TMF update operation, while `PUT /intentSpecification/{id}` is an accepted platform extension for deterministic full replacement.

TMF `/hub` routing is the strict subscription route form, while `/intentSpecification/hub` is an accepted domain-scoped platform extension when deliberately used.

---

## Appendix A — External expression-value schema artefact

The following JSON Schema is the external validation artefact referenced by `targetEntitySchema.@schemaLocation`. It is shown here as implementation guidance only.

It is not embedded inside `IntentSpecification.expressionSpecification`, `Intent.expression`, or `IntentReport.expression`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.19.expression.schema.json",
  "title": "Hospital Surgical Slice Intent Expression Value Context Wrapper",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "context"
  ],
  "properties": {
    "context": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "targets",
        "constraints"
      ],
      "properties": {
        "targets": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "maxLatencyMs": {
              "type": "number",
              "minimum": 0
            },
            "minAvailabilityPercent": {
              "type": "number",
              "minimum": 0,
              "maximum": 100
            },
            "maxJitterMs": {
              "type": "number",
              "minimum": 0
            },
            "maxPacketLossPercent": {
              "type": "number",
              "minimum": 0,
              "maximum": 100
            }
          }
        },
        "constraints": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "location",
            "serviceType",
            "serviceClass",
            "priority",
            "redundancyRequired"
          ],
          "properties": {
            "location": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "locationId"
              ],
              "properties": {
                "locationId": {
                  "type": "string",
                  "minLength": 1
                },
                "locationType": {
                  "type": "string",
                  "minLength": 1
                },
                "geographicScope": {
                  "type": "string",
                  "minLength": 1
                }
              }
            },
            "serviceType": {
              "type": "string",
              "enum": [
                "surgical-connectivity"
              ]
            },
            "serviceClass": {
              "type": "string",
              "enum": [
                "critical-gold",
                "critical-silver"
              ]
            },
            "priority": {
              "type": "string",
              "enum": [
                "critical",
                "high",
                "standard"
              ]
            },
            "redundancyRequired": {
              "type": "boolean"
            },
            "timeWindow": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "startDateTime"
              ],
              "properties": {
                "startDateTime": {
                  "type": "string",
                  "format": "date-time"
                },
                "endDateTime": {
                  "type": "string",
                  "format": "date-time"
                }
              }
            }
          }
        },
        "preferences": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "preferredAccessTechnology": {
              "type": "string",
              "enum": [
                "5G",
                "fibre",
                "private-wireless"
              ]
            }
          }
        }
      }
    }
  }
}
```
