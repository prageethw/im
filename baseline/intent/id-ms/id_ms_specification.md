# ID MS Specfication

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
ID MS validates syntax/resource shape and enforces specification lifecycle/version governance.
ID MS does not own runtime `Intent`, `IntentReport`, semantic validation, policy validation, network/resource feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

### TMF deployment path note

The examples in this specification use the platform base path `/intentManagement/v5`.
A strict TMF deployment may expose the same API through `/tmf-api/intentManagement/v5`; the API gateway may map between the deployment prefix and the platform-owned service path without changing resource semantics.

---

## 1. API endpoints

### IntentSpecification resource APIs

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create mutable DRAFT candidate | `POST` | `/intentManagement/v5/intentSpecification` |
| List specifications | `GET` | `/intentManagement/v5/intentSpecification` |
| Retrieve official ACTIVE/RETIRED specification by ID | `GET` | `/intentManagement/v5/intentSpecification/{id}` |
| Retire current ACTIVE specification | `DELETE` | `/intentManagement/v5/intentSpecification/{id}` |
| Retrieve DRAFT candidate | `GET` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Full replace DRAFT candidate | `PUT` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Partial update or activate DRAFT candidate | `PATCH` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Delete unused DRAFT candidate | `DELETE` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |

### Hub subscription APIs

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/intentSpecification/hub` |
| Retrieve subscription by ID | `GET` | `/intentManagement/v5/intentSpecification/hub/{id}` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/intentSpecification/hub/{id}` |

---

## 2. Common conventions

### Expression schema alignment:

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



### IntentSpecification draft, identity, and versioning clarification:

`IntentSpecification.version` is an official design-time contract version. It is assigned by ID MS only when a selected DRAFT candidate is activated. It is separate from runtime `Intent.version`.

Baseline rules:

- `POST /intentSpecification` always creates a mutable DRAFT candidate.
- The caller must provide `specKey` on create and must not provide `id`, `draftId`, `version`, `href`, `lifecycleStatus`, server timestamps, or `_links`.
- ID MS resolves the stable server-assigned `IntentSpecification.id` from `specKey` when the DRAFT candidate is created. If a current ACTIVE specification exists for the same `specKey`, the DRAFT candidate is assigned to that existing `id`; otherwise ID MS creates a new `id`. If only RETIRED versions exist for the same `specKey`, ID MS creates a new `id` unless governed lineage reuse is explicitly introduced later.
- ID MS assigns a new `draftId` for each mutable DRAFT candidate. DRAFT candidate retrieval, update, activation, and deletion use `/intentSpecification/draft/{draftId}`.
- DRAFT candidates do not expose an official public `version`; draft revision is represented by `ETag`.
- When a DRAFT candidate is activated, ID MS assigns the official `version`, carries the selected `draftId` forward as provenance, and transactionally retires the previous ACTIVE version for the same resolved `id`.
- `ACTIVE` and `RETIRED` `IntentSpecification` resources are immutable for material contract changes.
- Runtime `Intent.version` identifies the admitted runtime request/projection version and must not be confused with `IntentSpecification.version`.

### PATCH semantics:### PATCH semantics:

`PATCH` uses JSON Merge Patch semantics.

All external `PATCH` request examples must use:

```http
Content-Type: application/merge-patch+json
```

`PATCH` is intended for small targeted updates. For deterministic full replacement of editable Draft resources, use `PUT` where the platform extension is available.




### Response classification headers:

ID MS returns response classification headers on external REST API responses so callers can distinguish strict TMF-native behaviour from documented platform-extension behaviour.

These are response headers only. Clients do not send these headers in requests.

| **Response header** | **Meaning** |
|---|---|
| `X-TMF-Native: true` | The response is for a TMF-native operation/behaviour. |
| `X-TMF-Native: false` | The response is for an operation/behaviour that includes platform-specific semantics. |
| `X-Platform-Extension: true` | The route, method, response, or behaviour includes a documented platform extension. |
| `X-Platform-Extension: false` | No platform extension is used for the response. |

Header classification guidance:

| **ID MS response area** | **X-TMF-Native** | **X-Platform-Extension** | **Reason** |
|---|---:|---:|---|
| `POST /intentSpecification`, `GET /intentSpecification`, `GET /intentSpecification/{id}`, `GET /intentSpecification/draft/{draftId}`, `PATCH /intentSpecification/draft/{draftId}`, `DELETE /intentSpecification/{id}`, and `DELETE /intentSpecification/draft/{draftId}` using strict TMF-compatible behaviour | `true` | `false` | TMF-compatible IntentSpecification resource operations. |
| `PUT /intentSpecification/draft/{draftId}` | `false` | `true` | Deterministic full replacement of a mutable DRAFT candidate is a platform extension. |
| `PATCH /intentSpecification/draft/{draftId}` used for tightly controlled activation | `true` | `false` | Uses TMF-compatible partial update on the selected DRAFT candidate. |
| `PUT /intentSpecification/draft/{draftId}` used for full-resource finalisation/activation | `false` | `true` | Full-resource finalisation through PUT is a platform extension. |
| Strict `/hub` create/delete responses | `true` | `false` | Strict TMF hub route family. |
| Domain-scoped `/intentSpecification/hub` responses | `false` | `true` | Domain-owned hub route family is a platform extension. |
| `GET /intentSpecification/hub/{id}` | `false` | `true` | Subscription retrieval is an operational convenience extension. |

Example TMF-native response headers:

```http
X-TMF-Native: true
X-Platform-Extension: false
```

Example platform-extension response headers:

```http
X-TMF-Native: false
X-Platform-Extension: true
```


### Lifecycle values

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DELETED` lifecycle status. Delete is an operation/outcome, not a normal lifecycle state.


### Draft candidate identity model

ID MS follows the definition-candidate model used by the optimiser definition baseline:

```text
specKey -> resolves the stable server-assigned IntentSpecification.id
draftId -> selects the mutable DRAFT candidate
id -> selects the official ACTIVE/RETIRED lineage
version -> official version assigned only on activation
```

Runtime IC MS admission must still reference a concrete ACTIVE `intentSpecification.id`. Runtime admission must not use `specKey` or `draftId` as the contract-selection key.

### Versioning rules

- New specifications are normally created as `DRAFT`.
- `DRAFT` specifications are editable.
- `ACTIVE` and `RETIRED` specifications are immutable.
- Meaningful change after activation requires a new mutable DRAFT candidate.
- Only one ACTIVE official version is allowed for the same resolved `IntentSpecification.id`.
- At most one ACTIVE lineage may exist for a given `specKey`; duplicate ACTIVE lineages for the same `specKey` are a data-integrity breach.
- Activating a selected DRAFT candidate retires the previous ACTIVE version for the same resolved `id`.
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
| `fields` | Create, list, retrieve, update | Optional TMF-aligned field selection / projection parameter |
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
| `409` | `VERSION_CONFLICT` | Duplicate specification/version or specKey active-lineage conflict |
| `412` | `PRECONDITION_FAILED` | Supplied `If-Match` does not match the current resource version |
| `422` | `VALIDATION_FAILED` | Fails expression/spec schema constraints |
| `428` | `PRECONDITION_REQUIRED` | Required `If-Match` header is missing for an unsafe operation |
| `503` | `SERVICE_UNAVAILABLE` | Source-of-truth DB unavailable |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

### Missing If-Match response

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
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
X-TMF-Native: true
X-Platform-Extension: false
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

`POST /intentSpecification` creates a mutable DRAFT candidate only. The request must include `specKey`; ID MS resolves the stable server-assigned `IntentSpecification.id` from `specKey` and assigns a new `draftId`. The DRAFT candidate has no official public `version`; draft revision is represented by the returned `ETag`.

### Request

```http
POST /intentManagement/v5/intentSpecification?fields=id,href,specKey,draftId,name,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,intentBehaviour,intentLayer,@type,@baseType
Content-Type: application/json
Accept: application/json
```

```json
{
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "isBundle": false,
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
  "intentBehaviour": {
    "category": "REALTIME",
    "constraintMode": "STRICT",
    "objectiveType": "SLA",
    "fulfilmentMode": "CONTINUOUS"
  },
  "intentLayer": "SERVICE",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec.schema.json",
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "id": "context",
      "name": "context",
      "description": "Top-level semantic context supported by this IntentSpecification. The context contains canonical context.targets, context.constraints, and context.preferences. Detailed field rules are defined in the expression-value schema referenced by targetEntitySchema.@schemaLocation.",
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
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice.expression.schema.json",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  }
}
```

Client create requests must not provide `id`, `href`, `draftId`, official `version`, `lifecycleStatus`, `creationDate`, `lastUpdate`, `statusChangeDate`, `Location`, `ETag`, or `_links`. If `isBundle` is omitted, ID MS defaults it to `false`.

If a current ACTIVE specification exists for the same `specKey`, the DRAFT candidate is assigned to that existing `id`. If no current ACTIVE specification exists for the `specKey`, ID MS creates a new `id`. If only RETIRED versions exist for the `specKey`, ID MS creates a new `id` unless governed lineage reuse is introduced later.

### Success response

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
ETag: "id-draft-hospital-surgical-slice-a-r1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
```

```json
{
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "lifecycleStatus": "DRAFT",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "creationDate": "2026-04-18T12:00:00+10:00",
  "lastUpdate": "2026-04-18T12:00:00+10:00",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice.expression.schema.json",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "GET"
    },
    "patch": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "PATCH"
    },
    "replace": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "PUT"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "DELETE"
    },
    "activate": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "PATCH"
    }
  }
}
```

## 5. List IntentSpecifications

### Request

```http
GET /intentManagement/v5/intentSpecification?offset=0&limit=10&lifecycleStatus=ACTIVE&fields=id,href,specKey,name,version,lifecycleStatus,isBundle,validFor,relatedParty,@type,@baseType
Accept: application/json
```

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
X-Total-Count: 1
X-Result-Count: 1
ETag: "intent-spec-list-active-v17"
Cache-Control: private, max-age=60
```

```json
[
  {
    "id": "hospital-surgical-slice-spec",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec",
    "specKey": "hospital-surgical-slice-spec",
    "draftId": "id-draft-hospital-surgical-slice-a",
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
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec"
      },
      "collection": {
        "href": "/intentManagement/v5/intentSpecification"
      },
      "retire": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec",
        "method": "DELETE"
      },
      "createNewVersion": {
        "href": "/intentManagement/v5/intentSpecification",
        "method": "POST"
      }
    }
  }
]
```

The list operation returns a lightweight summary by default. For `ACTIVE` and `RETIRED` official versions, `href` and `self` use `/intentSpecification/{id}`. `draftId` may be returned as immutable provenance, but DRAFT candidate mutation still uses `/intentSpecification/draft/{draftId}`. The list response does not include full `specCharacteristic`, `expressionSpecification`, or `targetEntitySchema` unless explicitly requested through `fields`.

---

## 6. Retrieve IntentSpecification

This operation retrieves the current official `ACTIVE` version by `id` by default. Historical `ACTIVE` or `RETIRED` versions are selected by `id` plus an explicit `version` query parameter. Mutable DRAFT candidates are retrieved through `GET /intentSpecification/draft/{draftId}`.

### Request

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?fields=id,href,specKey,draftId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Accept: application/json
```

### Request with cache override

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?fields=id,href,specKey,draftId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### Success response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-r1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
Cache-Control: private, max-age=300
```

```json
{
  "id": "hospital-surgical-slice-spec",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
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
  "intentBehaviour": {
    "category": "REALTIME",
    "constraintMode": "STRICT",
    "objectiveType": "SLA",
    "fulfilmentMode": "CONTINUOUS"
  },
  "intentLayer": "SERVICE",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec.schema.json",
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
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec"
    },
    "collection": {
      "href": "/intentManagement/v5/intentSpecification"
    },
    "retire": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec",
      "method": "DELETE"
    },
    "createNewVersion": {
      "href": "/intentManagement/v5/intentSpecification",
      "method": "POST"
    }
  }
}
```

### DRAFT candidate retrieval

```http
GET /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
Accept: application/json
```

DRAFT candidate retrieval returns the mutable DRAFT candidate selected by `draftId`. DRAFT responses include `draftId`, omit official public `version`, and expose DRAFT action links such as `patch`, `replace`, `delete`, and `activate` using `/intentSpecification/draft/{draftId}`.

### Not found response

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
```

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "reason": "INTENT_SPECIFICATION_NOT_FOUND",
  "message": "IntentSpecification hospital-surgical-slice-spec was not found.",
  "status": 404,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",
  "@type": "Error"
}
```

---

## 7. Full replace DRAFT IntentSpecification candidate

`PUT` is the preferred platform extension for deterministic full replacement of an editable `DRAFT` specification.

### Request

```http
PUT /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a?fields=id,href,specKey,draftId,name,description,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Content-Type: application/json
Accept: application/json
If-Match: "id-draft-hospital-surgical-slice-a-r1"
```

```json
{
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
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
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a.schema.json",
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
X-TMF-Native: true
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
ETag: "id-draft-hospital-surgical-slice-a-r2"
Last-Modified: Sat, 18 Apr 2026 03:00:00 GMT
```

```json
{
  "id": "hospital-surgical-slice-spec",
  "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. It is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
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
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a.schema.json",
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
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a"
    },
    "fullUpdate": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but discouraged as a general update method. Prefer PUT for deterministic full replacement."
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
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
X-TMF-Native: true
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "RESOURCE_IMMUTABLE",
  "reason": "ACTIVE_OR_RETIRED_SPECIFICATION_IMMUTABLE",
  "message": "ACTIVE and RETIRED IntentSpecification resources cannot be materially updated. Create a new mutable DRAFT candidate for material contract changes.",
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
X-TMF-Native: true
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

### ETag mismatch response

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
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

## 8. Partial update DRAFT IntentSpecification candidate

`PATCH` remains supported for TMF compatibility, but it is discouraged as a general update method.
Prefer `PUT` for deterministic full replacement of editable `DRAFT` specifications.
Use `PATCH` only where a TMF-compatible client cannot use `PUT` or where a tightly controlled, small targeted compatibility update is required.

`PATCH` must not normally be used for material contract replacement, including `specKey`, `version`, `specCharacteristic`, `expressionSpecification`, `targetEntitySchema`, or major lifecycle/version contract identity.

### Request

```http
PATCH /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a?fields=id,href,specKey,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,@type,@baseType
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "id-draft-hospital-surgical-slice-a-r1"
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
X-TMF-Native: true
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
ETag: "id-draft-hospital-surgical-slice-a-r2"
Last-Modified: Sat, 18 Apr 2026 03:00:00 GMT
```

```json
{
  "id": "hospital-surgical-slice-spec",
  "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated draft description only.",
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
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a"
    },
    "fullUpdate": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
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
DELETE /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
If-Match: "id-draft-hospital-surgical-slice-a-r1"
Accept: application/json
```

### Success response

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
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
X-TMF-Native: true
X-Platform-Extension: false
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
X-TMF-Native: true
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

### ETag mismatch response

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
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

Activation is not exposed through a custom action endpoint. Do not use:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate  (not exposed)
```

Use the existing resource update endpoint instead.

For strict TMF-compatible lifecycle update, use:

```http
PATCH /intentManagement/v5/intentSpecification/draft/{draftId}
```

For the preferred platform extension where the caller sends the full resource representation, use:

```http
PUT /intentManagement/v5/intentSpecification/draft/{draftId}
```

Although `PATCH` is discouraged as a general update method, this is an acceptable tightly controlled TMF-compatible case because activation is a small lifecycle-status update.

### PATCH activation request

```http
PATCH /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-b?fields=id,href,specKey,name,version,lifecycleStatus,previousActiveSpecification,@type,@baseType
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "id-draft-hospital-surgical-slice-b-r3"
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
X-TMF-Native: true
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec
ETag: "intent-spec-hospital-surgical-slice-r4"
Last-Modified: Sat, 18 Apr 2026 03:30:00 GMT
```

```json
{
  "id": "hospital-surgical-slice-spec",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-b",
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "version": "1.20",
  "lifecycleStatus": "ACTIVE",
  "previousActiveSpecification": {
    "id": "hospital-surgical-slice-spec",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.19",
    "version": "1.19",
    "lifecycleStatus": "RETIRED"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec"
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
| Previous active | Previous `ACTIVE` version for the same resolved `id` becomes `RETIRED` transactionally |
| New runtime creation | New runtime intents must use the new `ACTIVE` version |
| Existing runtime intents | Existing intents that reference retired specifications may continue temporarily where safe |
| Material update after activation | Not allowed; create a new mutable DRAFT candidate |
| ETag required | `If-Match` is required |
| Missing `If-Match` | `428 Precondition Required` |
| Stale/mismatched `If-Match` | `412 Precondition Failed` |
| Invalid lifecycle transition | `409 Conflict` |

### Events emitted by activation

Activation emits two `IntentSpecificationStatusChangeEvent` events:

1. One event for the newly activated version, with the emitted `intentSpecification.lifecycleStatus` set to `ACTIVE`.
2. One event for the previous active version in the same `specKey`, with the emitted `intentSpecification.lifecycleStatus` set to `RETIRED`.

The status-change event type identifies that the lifecycle status changed. The event body carries the current `IntentSpecification` resource snapshot and does not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields.

### Invalid lifecycle transition response

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
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
X-TMF-Native: true
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

### ETag mismatch response

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
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

ID MS intentionally uses the domain-scoped hub route for `IntentSpecification` event subscriptions.
Strict TMF hub compatibility is based on the generic `/hub` subscription model; the `/intentSpecification/hub` route family is an approved platform extension that keeps subscription ownership explicit for the `IntentSpecification` domain.

The supported platform hub routes are:

```http
POST /intentManagement/v5/intentSpecification/hub
GET /intentManagement/v5/intentSpecification/hub/{id}
DELETE /intentManagement/v5/intentSpecification/hub/{id}
```

Hub subscriptions are delivered as TMF-aligned REST webhook notifications.
ID MS stores the subscriber callback registration and, when a subscribed `IntentSpecification` event occurs, delivers the corresponding event payload by HTTP `POST` to the subscriber listener callback URL.
Kafka is not used for external hub notification delivery because ID MS is both the event originator and the delivery owner, and no independent internal consumer requires a topic for these external notifications.
Delivery reliability is handled by an ID MS-owned local delivery outbox and retry relay.

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
X-TMF-Native: true
X-Platform-Extension: false
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
- ID MS hub subscriptions are for external IntentSpecification events only: `IntentSpecificationCreateEvent`, `IntentSpecificationAttributeValueChangeEvent`, `IntentSpecificationStatusChangeEvent`, and `IntentSpecificationDeleteEvent`.
- ID MS delivers subscribed events by HTTP `POST` to the stored subscriber callback URL.
- ID MS does not publish hub notifications to Kafka and does not create a self-publish/self-consume Kafka loop for external subscription delivery.
- ID MS uses a local delivery outbox and retry relay to track pending, delivered, failed, and retryable webhook notification work.
- ID MS hub subscriptions must not expose internal workflow events, KP details, runtime assurance state, telemetry, callback payloads, or internal fulfilment details.

---

## 12. Hub retrieve subscription

`GET /intentManagement/v5/intentSpecification/hub/{id}` is a platform extension for operational convenience.
It is not required by the strict TMF generic hub route shape, but is retained because it gives operators and consumers a safe way to inspect an ID MS-owned subscription without exposing internal workflow state.

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
X-TMF-Native: true
X-Platform-Extension: false
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
X-TMF-Native: true
X-Platform-Extension: false
```

No response body is returned.

### Missing If-Match response

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
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

### ETag mismatch response

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
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
| Delivery mechanism | HTTP `POST` to subscriber listener callback URL |
| Delivery reliability | ID MS-owned local delivery outbox and retry relay |
| Kafka usage | Kafka is not used for external hub notification delivery |
| Filter | `query` filters event types |
| Event family | ID MS external IntentSpecification events only: `IntentSpecificationCreateEvent`, `IntentSpecificationAttributeValueChangeEvent`, `IntentSpecificationStatusChangeEvent`, and `IntentSpecificationDeleteEvent` |
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
X-TMF-Native: true
X-Platform-Extension: false
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

ID MS emits external TMF-aligned resource events for `IntentSpecification` changes.

| **Event** | **Trigger** |
|---|---|
| `IntentSpecificationCreateEvent` | New `IntentSpecification` created |
| `IntentSpecificationAttributeValueChangeEvent` | Editable draft attributes changed |
| `IntentSpecificationStatusChangeEvent` | Lifecycle status changes, such as activation to `ACTIVE` or retirement to `RETIRED` |
| `IntentSpecificationDeleteEvent` | Unused draft specification deleted after delete succeeds |

These are external subscription events for the `IntentSpecification` resource. They are not internal fulfilment events and must not expose II MS semantic validation details, lightweight II MS KP details, `t7.knowledge plane` data, optimiser decisions, runtime assurance state, telemetry, callback payloads, or internal candidate/resource scoring details.

Event resource snapshots should carry consistent resource metadata:

- `id`
- `href`
- `specKey`
- `name`
- `version`
- `lifecycleStatus`
- `isBundle`
- `validFor`
- `relatedParty`
- optional `intentBehaviour` and `intentLayer` where supplied on the resource
- `@type`
- `@baseType`

Status-change events carry the current `intentSpecification.lifecycleStatus` snapshot. They do not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields.

Activation emits two `IntentSpecificationStatusChangeEvent` events:

- one for the newly activated version, with `intentSpecification.lifecycleStatus` set to `ACTIVE`
- one for the previous active version, with `intentSpecification.lifecycleStatus` set to `RETIRED`

Delete events are emitted only after successful delete and show the last known lifecycle state as `DRAFT`. Delete events must not use `DELETED`.

---

## 16. Event envelope pattern

External TMF-aligned event examples populate both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp.
`timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples.
TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics.

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
      "id": "hospital-surgical-slice-spec",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec",
      "specKey": "hospital-surgical-slice-spec",
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
      "id": "hospital-surgical-slice-spec",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.19",
      "specKey": "hospital-surgical-slice-spec",
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
      "id": "hospital-surgical-slice-spec",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.19",
      "specKey": "hospital-surgical-slice-spec",
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
      "id": "hospital-surgical-slice-spec",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec",
      "specKey": "hospital-surgical-slice-spec",
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
      "specKey": "hospital-surgical-slice-spec",
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
- `intentBehaviour` and `intentLayer` are optional definition-time metadata fields and are not required for DRAFT creation, activation, or runtime Intent admission in the current baseline.
- `intentBehaviour.fulfilmentMode` values are `IMMEDIATE`, `LONGRUNNING`, and `CONTINUOUS`; `CONTINUOUS` means the system adopts a closed loop for the intent.
- Use `priority`, not `priority_level`.
- Do not use `DELETED` as an `IntentSpecification.lifecycleStatus`.
- ETag is used for unsafe-operation concurrency only.
- Caching is GET-only.
- `If-None-Match` and `304 Not Modified` are not baselined.
- Missing required `If-Match` returns `428 Precondition Required`.
- Stale or mismatched `If-Match` returns `412 Precondition Failed`.
- `fields` is supported as an optional TMF-aligned field selection parameter.
- Activation is represented through PUT/PATCH lifecycle update, not a custom action endpoint.
- External TMF-aligned events include both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp.
- `timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples. TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics.
- `IntentSpecificationStatusChangeEvent` carries the current `intentSpecification.lifecycleStatus` snapshot and does not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields.

---

## TMF compliance and platform extension baseline

### Strict TMF-compliant baseline

For strict TMF alignment, ID MS supports the TMF-aligned `IntentSpecification` operations:

| **Operation** | **Endpoint** | **Position** |
|---|---|---|
| Create | `POST /intentManagement/v5/intentSpecification` | TMF-aligned |
| List | `GET /intentManagement/v5/intentSpecification` | TMF-aligned |
| Retrieve | `GET /intentManagement/v5/intentSpecification/{id}` | TMF-aligned |
| Partial update | `PATCH /intentManagement/v5/intentSpecification/draft/{draftId}` | TMF-aligned |
| Delete | `DELETE /intentManagement/v5/intentSpecification/{id}` | TMF-aligned |
| Event subscription | `POST /hub`, `DELETE /hub/{id}` | Strict TMF route form where required |

### Accepted platform extensions

Controlled platform extensions are acceptable when they are documented, non-breaking, and do not conflict with TMF semantics.

For ID MS, accepted platform extensions are:

| **Extension** | **Purpose** | **Rule** |
|---|---|---|
| `PUT /intentManagement/v5/intentSpecification/draft/{draftId}` | Deterministic full replacement | Preferred platform update method where supported |
| `/intentManagement/v5/intentSpecification/hub` | Domain-scoped event subscription route | Allowed as a clearer domain-owned route when deliberately chosen |
| `GET /intentManagement/v5/intentSpecification/hub/{id}` | Subscription inspection | Platform convenience operation; not required by strict TMF generic hub shape |
| `DELETE /intentManagement/v5/intentSpecification/hub/{id}` | Domain-scoped subscription removal | Allowed as a clearer domain-owned route when deliberately chosen |
| `specKey` | Specification-key grouping across versions | Platform governance field; does not replace TMF `id` or `version` |
| `_links` | Lifecycle-aware navigation and operation hints | Platform HATEOAS extension; clients must not require it for strict TMF compatibility |
| `previousActiveSpecification` | Activation outcome trace | Platform governance projection showing the version retired during activation |
| Strong `ETag` / `If-Match` governance | Unsafe-operation concurrency control | Platform concurrency policy applied consistently to mutable operations |
| `428 Precondition Required` | Missing precondition response | Platform concurrency policy for unsafe operations that require `If-Match` |

### Update method rule

`PATCH` is the strict TMF-compatible update operation.
`PUT` is the platform extension for deterministic full replacement and is preferred from the platform engineering perspective where clients support it.
`PATCH` remains supported for TMF compatibility but is not encouraged for ordinary edits when deterministic full replacement is available.

### Lifecycle activation rule

Activation/retirement is represented as a resource update to `IntentSpecification.lifecycleStatus`.

Use:

```http
PATCH /intentManagement/v5/intentSpecification/draft/{draftId}
```

for strict TMF compatibility.

Use:

```http
PUT /intentManagement/v5/intentSpecification/draft/{draftId}
```

as a platform extension when performing deterministic full replacement.

Do not expose custom lifecycle action endpoints such as:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate  (not exposed)
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
Hub notification delivery remains REST webhook delivery to the subscriber listener callback URL; Kafka is not part of the external hub notification model.
ID MS may use a local delivery outbox and retry relay for reliable webhook delivery, but that outbox is an ID MS implementation detail and not a subscriber-facing contract.
`GET /intentManagement/v5/intentSpecification/hub/{id}` is also a platform extension for safe subscription inspection and is not part of the strict TMF generic hub route minimum.

### External event timestamp rule

For external TMF-aligned resource events, ID MS populates both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp.
`timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples.
TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics.
Internal events remain separate and continue to use the platform CloudEvents/header model plus the relevant internal body timestamp fields.

### Route prefix rule

The examples in this specification use `/intentManagement/v5` as the platform service base path.
A strict TMF-compatible API gateway may map deployment-specific external prefixes to the platform-owned service path; this is a deployment concern and must not change resource ownership, payload semantics, or lifecycle governance.

### Baseline statement

ID MS and IC MS remain TMF-aligned at the external contract level.
Controlled platform extensions are allowed when documented, non-breaking, and semantically compatible with TMF.

For ID MS, `PATCH /intentSpecification/draft/{draftId}` uses TMF-compatible partial-update semantics on the platform-extension DRAFT-candidate route, while `PUT /intentSpecification/draft/{draftId}` is an accepted platform extension for deterministic full replacement of mutable DRAFT candidates.
TMF `/hub` routing is the strict subscription route form, while `/intentSpecification/hub` is an accepted domain-scoped platform extension when deliberately used.

---

## Appendix A — External expression-value schema artefact

The following JSON Schema is the external validation artefact referenced by `targetEntitySchema.@schemaLocation`.
It is shown here as implementation guidance only. It is not embedded inside `IntentSpecification.expressionSpecification`, `Intent.expression`, or `IntentReport.expression`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.19.expression.schema.json",
  "title": "Hospital Surgical Slice Intent Expression Value",
  "description": "Schema for Intent.expression.expressionValue. The context object contains the intent targets, constraints, and preferences for the hospital surgical slice intent.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "@context",
    "context"
  ],
  "properties": {
    "@context": {
      "description": "JSON-LD context for intent and domain vocabulary prefixes.",
      "type": "object",
      "additionalProperties": true
    },
    "@type": {
      "description": "JSON-LD type for the expression value.",
      "type": "string",
      "const": "IntentExpressionValue"
    },
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
