# id_ms_specification.md

## ID MS Specification

### Service identity

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Definition MS |
| Short name | ID MS |
| Service name | `intent-definition-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `IntentSpecification` |
| Primary responsibility | Definition-time `IntentSpecification` catalogue, lifecycle/version governance, syntax contract, and external specification events |

### Boundary statement

ID MS owns definition-time `IntentSpecification` contracts and subscription management for specification events.

ID MS validates syntax/resource shape and enforces specification lifecycle/version governance. ID MS does not own runtime `Intent`, `IntentReport`, semantic validation, policy validation, network/resource feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

### TMF deployment path note

The examples in this specification use the platform base path `/intentManagement/v5`. A strict TMF deployment may expose the same API through `/tmf-api/intentManagement/v5`; the API gateway may map between the deployment prefix and the platform-owned service path without changing resource semantics.

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
POST /intentManagement/v5/intentSpecification?fields=id,href,familyId,name,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Content-Type: application/json
Accept: application/json
```

```json
{
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "Provider",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
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
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.19.expression.schema.json",
    "schemaVersion": "1.19",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  }
}
```

The client does not send `id`, `href`, `Location`, `ETag`, or `_links`. ID MS generates these values.

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
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "Provider",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
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
    "expressionLanguage": "JSON-LD",
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
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "fullUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but discouraged as a general update method. Prefer PUT for deterministic full replacement."
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
GET /intentManagement/v5/intentSpecification?offset=0&limit=10&lifecycleStatus=ACTIVE&fields=id,href,familyId,name,version,lifecycleStatus,isBundle,validFor,relatedParty,@type,@baseType
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
    "familyId": "hospital-surgical-slice-spec",
    "name": "Hospital Surgical Slice Intent Specification",
    "version": "1.19",
    "lifecycleStatus": "ACTIVE",
    "isBundle": false,
    "validFor": {
      "startDateTime": "2026-04-18T12:00:00+10:00"
    },
    "relatedParty": [
      {
        "@type": "RelatedPartyRefOrPartyRoleRef",
        "role": "Provider",
        "partyOrPartyRole": {
          "@type": "PartyRoleRef",
          "id": "mycsp",
          "name": "MyCSP",
          "@referredType": "Provider"
        }
      }
    ],
    "@type": "IntentSpecification",
    "@baseType": "EntitySpecification",
    "_links": {
      "self": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "partialUpdate": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "method": "PATCH",
        "warning": "PATCH is supported for compatibility but discouraged as a general update method. Prefer PUT for deterministic full replacement."
      }
    }
  }
]
```

The list operation returns a lightweight summary by default. It does not include full `specCharacteristic`, `expressionSpecification`, or `targetEntitySchema` unless explicitly requested through `fields`.

---
## 6. Retrieve IntentSpecification

### Request

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,familyId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Accept: application/json
```

### Request with cache override

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,familyId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
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
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.19",
  "lifecycleStatus": "ACTIVE",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "Provider",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19.schema.json",
  "specCharacteristic": "...bucket catalogue with example/default characteristicValueSpecification values...",
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
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
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "fullUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but discouraged as a general update method. Prefer PUT for deterministic full replacement."
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

`PUT` is the preferred platform extension for deterministic full replacement of an editable `DRAFT` specification.

### Request

```http
PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,familyId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Content-Type: application/json
Accept: application/json
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "Provider",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19.schema.json",
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "id": "context",
      "name": "context",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1
    }
  ],
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.19.expression.schema.json",
    "schemaVersion": "1.19",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  }
}
```

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v2"
Last-Modified: Sat, 18 Apr 2026 03:00:00 GMT
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "Provider",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19.schema.json",
  "specCharacteristic": "...full replacement specCharacteristic...",
  "expressionSpecification": "...full replacement expressionSpecification...",
  "targetEntitySchema": "...full replacement targetEntitySchema...",
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
      "warning": "PATCH is supported for compatibility but discouraged as a general update method. Prefer PUT for deterministic full replacement."
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "DELETE"
    }
  }
}
```

### Immutable resource response

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
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

### Missing If-Match response

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

### ETag mismatch response

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

---
## 8. Partial update IntentSpecification

`PATCH` remains supported for TMF compatibility, but it is discouraged as a general update method. Prefer `PUT` for deterministic full replacement of editable `DRAFT` specifications. Use `PATCH` only where a TMF-compatible client cannot use `PUT` or where a tightly controlled, small targeted compatibility update is required.

`PATCH` must not normally be used for material contract replacement, including `familyId`, `version`, `specCharacteristic`, `expressionSpecification`, `targetEntitySchema`, or major lifecycle/version contract identity.

### Request

```http
PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19?fields=id,href,familyId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,@type,@baseType
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
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v2"
Last-Modified: Sat, 18 Apr 2026 03:00:00 GMT
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated draft description only.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "Provider",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
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
      "warning": "PATCH is supported for compatibility but discouraged as a general update method. Prefer PUT for deterministic full replacement."
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
Accept: application/json
```

### Success response

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
```

No response body is returned.

### Delete rules

| **Rule** | **Baseline** |
|---|---|
| Allowed lifecycle | `DRAFT` only |
| Blocked lifecycle | `ACTIVE`, `RETIRED` |
| Runtime references | Delete is blocked if the specification is referenced by runtime `Intent` resources |
| Audit/history dependency | Delete is blocked if retention is required for audit/history |
| ETag required | `If-Match` is required |
| Missing `If-Match` | `428 Precondition Required` |
| Stale/mismatched `If-Match` | `412 Precondition Failed` |
| Delete outcome | Physical or logical removal is an implementation detail |
| Resource lifecycle | Do not set `lifecycleStatus = DELETED` |
| Event emitted | `IntentSpecificationDeleteEvent` after successful delete only |

### Delete blocked response

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "RESOURCE_IMMUTABLE",
  "reason": "SPECIFICATION_DELETE_NOT_ALLOWED",
  "message": "IntentSpecification cannot be deleted because it is active, retired, referenced by runtime resources, or retained for audit/history.",
  "status": 409,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_IMMUTABLE",
  "@type": "Error"
}
```

### Missing If-Match response

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

### ETag mismatch response

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

---

## 10. Activate IntentSpecification through lifecycle update

Activation is not exposed through a custom action endpoint.

Do not use:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate
```

Use the existing resource update endpoint instead.

For strict TMF-compatible lifecycle update, use:

```http
PATCH /intentManagement/v5/intentSpecification/{id}
```

For the preferred platform extension where the caller sends the full resource representation, use:

```http
PUT /intentManagement/v5/intentSpecification/{id}
```

Although `PATCH` is discouraged as a general update method, this is an acceptable tightly controlled TMF-compatible case because activation is a small lifecycle-status transition.

### PATCH activation request

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

### PUT activation option

`PUT` may also be used when the caller sends the full replacement representation with `lifecycleStatus: ACTIVE` as part of the complete `IntentSpecification` resource.

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20
ETag: "intent-spec-hospital-surgical-slice-spec-v1.20-v2"
Last-Modified: Sat, 18 Apr 2026 03:30:00 GMT
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
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
    "version": "1.19",
    "previousLifecycleStatus": "ACTIVE",
    "newLifecycleStatus": "RETIRED"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
    },
    "collection": {
      "href": "/intentManagement/v5/intentSpecification"
    },
    "createNewVersion": {
      "href": "/intentManagement/v5/intentSpecification",
      "method": "POST"
    }
  }
}
```

### Activation rules

| **Rule** | **Baseline** |
|---|---|
| Source state | Only `DRAFT` can be activated |
| Target state | Activated version becomes `ACTIVE` |
| Previous active | Previous `ACTIVE` version in the same `familyId` becomes `RETIRED` |
| New runtime creation | New runtime intents must use the new `ACTIVE` version |
| Existing runtime intents | Existing intents that reference retired specifications may continue temporarily where safe |
| Material update after activation | Not allowed; create a new versioned `DRAFT` |
| ETag required | `If-Match` is required |
| Missing `If-Match` | `428 Precondition Required` |
| Stale/mismatched `If-Match` | `412 Precondition Failed` |
| Invalid lifecycle transition | `409 Conflict` |

### Events emitted by activation

Activation emits two `IntentSpecificationStatusChangeEvent` events:

1. One event for the newly activated version:
   - `DRAFT -> ACTIVE`

2. One event for the previous active version in the same `familyId`:
   - `ACTIVE -> RETIRED`

### Invalid lifecycle transition response

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "INVALID_LIFECYCLE_TRANSITION",
  "reason": "INTENT_SPECIFICATION_ACTIVATION_NOT_ALLOWED",
  "message": "Only DRAFT IntentSpecification resources can be activated.",
  "status": 409,
  "referenceError": "https://mycsp.com.au/errors/INVALID_LIFECYCLE_TRANSITION",
  "@type": "Error"
}
```

### Missing If-Match response

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

### ETag mismatch response

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

---

## 11. Hub create subscription

ID MS intentionally uses the domain-scoped hub route for `IntentSpecification` event subscriptions. Strict TMF hub compatibility is based on the generic `/hub` subscription model; the `/intentSpecification/hub` route family is an approved platform extension that keeps subscription ownership explicit for the `IntentSpecification` domain.

The supported platform hub routes are:

```http
POST /intentManagement/v5/intentSpecification/hub
GET /intentManagement/v5/intentSpecification/hub/{id}
DELETE /intentManagement/v5/intentSpecification/hub/{id}
```

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

### Hub create rules

- The subscription callback is an external listener endpoint owned by the consuming system.
- The `query` field filters delivered events.
- ID MS hub subscriptions are for external `IntentSpecification*Event` notifications only.
- ID MS hub subscriptions must not expose internal workflow events, KP details, runtime assurance state, telemetry, callback payloads, or internal fulfilment details.

---

## 12. Hub retrieve subscription

`GET /intentManagement/v5/intentSpecification/hub/{id}` is a platform extension for operational convenience. It is not required by the strict TMF generic hub route shape, but is retained because it gives operators and consumers a safe way to inspect an ID MS-owned subscription without exposing internal workflow state.

### Request

```http
GET /intentManagement/v5/intentSpecification/hub/sub-001
Accept: application/json
```

### Success response

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

---

## 13. Hub delete subscription

### Request

```http
DELETE /intentManagement/v5/intentSpecification/hub/sub-001
If-Match: "subscription-sub-001-v1"
Accept: application/json
```

### Success response

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
```

No response body is returned.

### Missing If-Match response

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

### ETag mismatch response

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
  "message": "The supplied ETag does not match the current subscription resource version.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

### Hub route and event scope rules

| **Rule** | **Baseline** |
|---|---|
| Route style | Domain-scoped `/intentSpecification/hub` route is intentional |
| Subscription target | External listener callback URL |
| Filter | `query` filters event types |
| Event family | ID MS external `IntentSpecification*Event` notifications only |
| Retrieve | Supported intentionally |
| Delete | Requires `If-Match` |
| Missing `If-Match` | `428 Precondition Required` |
| Stale/mismatched `If-Match` | `412 Precondition Failed` |
| Create response | `201 Created` with `Location`, `ETag`, body, and `_links` |
| Retrieve response | `200 OK` with `ETag` and GET-only private caching |
| Delete response | `204 No Content` |
| Hub must not expose | Internal workflow events, KP details, runtime assurance state, telemetry, callback payloads, or internal fulfilment details |

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
| `IntentSpecificationDeleteEvent` | Unused draft specification deleted after delete succeeds |

These are external subscription events for the `IntentSpecification` resource.

They are not internal fulfilment events and must not expose II MS semantic validation details, lightweight II MS KP details, `t7.knowledge plane` data, optimiser decisions, runtime assurance state, telemetry, callback payloads, or internal candidate/resource scoring details.

Event resource snapshots should carry consistent resource metadata:

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

Status-change events include lifecycle transition fields such as `previousLifecycleStatus` and `newLifecycleStatus`.

Activation emits two `IntentSpecificationStatusChangeEvent` events:

- one for the new version `DRAFT -> ACTIVE`
- one for the previous active version `ACTIVE -> RETIRED`

Delete events are emitted only after successful delete and show the last known lifecycle state as `DRAFT`. Delete events must not use `DELETED`.

---

## 16. Event envelope pattern

External TMF-facing event examples populate both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp. `timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples. TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics.

```json
{
  "eventId": "evt-intent-spec-001",
  "eventTime": "2026-04-18T12:00:00+10:00",
  "timeOccurred": "2026-04-18T12:00:00+10:00",
  "eventType": "IntentSpecificationStatusChangeEvent",
  "correlationId": "corr-intent-spec-001",
  "description": "IntentSpecification lifecycle status changed.",
  "priority": "Normal",
  "title": "IntentSpecification status changed",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.20",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20",
      "familyId": "hospital-surgical-slice-spec",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.20",
      "lifecycleStatus": "ACTIVE",
      "isBundle": false,
      "validFor": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      },
      "relatedParty": [
        {
          "@type": "RelatedPartyRefOrPartyRoleRef",
          "role": "Provider",
          "partyOrPartyRole": {
            "@type": "PartyRoleRef",
            "id": "mycsp",
            "name": "MyCSP",
            "@referredType": "Provider"
          }
        }
      ],
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    },
    "previousLifecycleStatus": "DRAFT",
    "newLifecycleStatus": "ACTIVE"
  },
  "reportingSystem": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "source": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
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
  "timeOccurred": "2026-04-18T12:00:00+10:00",
  "eventType": "IntentSpecificationCreateEvent",
  "correlationId": "corr-intent-spec-create-001",
  "description": "IntentSpecification created.",
  "priority": "Normal",
  "title": "IntentSpecification created",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.19",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "familyId": "hospital-surgical-slice-spec",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.19",
      "lifecycleStatus": "DRAFT",
      "isBundle": false,
      "validFor": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      },
      "relatedParty": [
        {
          "@type": "RelatedPartyRefOrPartyRoleRef",
          "role": "Provider",
          "partyOrPartyRole": {
            "@type": "PartyRoleRef",
            "id": "mycsp",
            "name": "MyCSP",
            "@referredType": "Provider"
          }
        }
      ],
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    }
  },
  "reportingSystem": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "source": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
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
  "timeOccurred": "2026-04-18T12:05:00+10:00",
  "eventType": "IntentSpecificationAttributeValueChangeEvent",
  "correlationId": "corr-intent-spec-attr-001",
  "description": "IntentSpecification draft attributes changed.",
  "priority": "Normal",
  "title": "IntentSpecification attributes changed",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.19",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "familyId": "hospital-surgical-slice-spec",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.19",
      "lifecycleStatus": "DRAFT",
      "isBundle": false,
      "validFor": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      },
      "relatedParty": [
        {
          "@type": "RelatedPartyRefOrPartyRoleRef",
          "role": "Provider",
          "partyOrPartyRole": {
            "@type": "PartyRoleRef",
            "id": "mycsp",
            "name": "MyCSP",
            "@referredType": "Provider"
          }
        }
      ],
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    },
    "changedAttributes": [
      {
        "name": "description",
        "oldValue": "Definition-time specification for hospital surgical slice intents.",
        "newValue": "Updated draft description only."
      }
    ]
  },
  "reportingSystem": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "source": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
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
  "timeOccurred": "2026-04-18T12:10:00+10:00",
  "eventType": "IntentSpecificationStatusChangeEvent",
  "correlationId": "corr-intent-spec-status-001",
  "description": "IntentSpecification lifecycle status changed.",
  "priority": "Normal",
  "title": "IntentSpecification status changed",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.20",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20",
      "familyId": "hospital-surgical-slice-spec",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.20",
      "lifecycleStatus": "ACTIVE",
      "isBundle": false,
      "validFor": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      },
      "relatedParty": [
        {
          "@type": "RelatedPartyRefOrPartyRoleRef",
          "role": "Provider",
          "partyOrPartyRole": {
            "@type": "PartyRoleRef",
            "id": "mycsp",
            "name": "MyCSP",
            "@referredType": "Provider"
          }
        }
      ],
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    },
    "previousLifecycleStatus": "DRAFT",
    "newLifecycleStatus": "ACTIVE"
  },
  "reportingSystem": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "source": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
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
  "timeOccurred": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentSpecificationDeleteEvent",
  "correlationId": "corr-intent-spec-delete-001",
  "description": "Unused draft IntentSpecification deleted.",
  "priority": "Normal",
  "title": "IntentSpecification deleted",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.18-draft",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.18-draft",
      "familyId": "hospital-surgical-slice-spec",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.18-draft",
      "lifecycleStatus": "DRAFT",
      "isBundle": false,
      "validFor": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      },
      "relatedParty": [
        {
          "@type": "RelatedPartyRefOrPartyRoleRef",
          "role": "Provider",
          "partyOrPartyRole": {
            "@type": "PartyRoleRef",
            "id": "mycsp",
            "name": "MyCSP",
            "@referredType": "Provider"
          }
        }
      ],
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    }
  },
  "reportingSystem": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "source": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
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
- External TMF-facing events include both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp.
- `timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples. TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics.

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
| Event subscription | `POST /hub`, `DELETE /hub/{id}` | Strict TMF route form where required |

### Accepted platform extensions

Controlled platform extensions are acceptable when they are documented, non-breaking, and do not conflict with TMF semantics.

For ID MS, accepted platform extensions are:

| **Extension** | **Purpose** | **Rule** |
|---|---|---|
| `PUT /intentManagement/v5/intentSpecification/{id}` | Deterministic full replacement | Preferred platform update method where supported |
| `/intentManagement/v5/intentSpecification/hub` | Domain-scoped event subscription route | Allowed as a clearer domain-owned route when deliberately chosen |
| `GET /intentManagement/v5/intentSpecification/hub/{id}` | Subscription inspection | Platform convenience operation; not required by strict TMF generic hub shape |
| `DELETE /intentManagement/v5/intentSpecification/hub/{id}` | Domain-scoped subscription removal | Allowed as a clearer domain-owned route when deliberately chosen |
| `familyId` | Specification-family grouping across versions | Platform governance field; does not replace TMF `id` or `version` |
| `_links` | Lifecycle-aware navigation and operation hints | Platform HATEOAS extension; clients must not require it for strict TMF compatibility |
| `previousActiveSpecification` | Activation outcome trace | Platform governance projection showing the version retired during activation |
| Strong `ETag` / `If-Match` governance | Unsafe-operation concurrency control | Platform concurrency policy applied consistently to mutable operations |
| `428 Precondition Required` | Missing precondition response | Platform concurrency policy for unsafe operations that require `If-Match` |

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

The domain-scoped route is acceptable only as a documented platform extension and must preserve the same subscription semantics. `GET /intentManagement/v5/intentSpecification/hub/{id}` is also a platform extension for safe subscription inspection and is not part of the strict TMF generic hub route minimum.

### External event timestamp rule

For external TMF-facing resource events, ID MS populates both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp. `timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples. TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics. Internal events remain separate and continue to use the platform CloudEvents/header model plus the relevant internal body timestamp fields.

### Route prefix rule

The examples in this specification use `/intentManagement/v5` as the platform service base path. A strict TMF API gateway may expose the same operations under `/tmf-api/intentManagement/v5`; this is a deployment mapping concern and must not change resource ownership, payload semantics, or lifecycle governance.

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
