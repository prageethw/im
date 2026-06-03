# ID MS Specification

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Scope | Intent Definition MS API and behaviour specification |
| Source of truth after commit | GitHub `baseline/intent/id-ms/id_ms_specification.md` |

## Table of contents:

- [1. Service identity:](#1-service-identity)
  - [1.1 Boundary statement:](#11-boundary-statement)
  - [1.2 TMF deployment path note:](#12-tmf-deployment-path-note)
- [2. API endpoints:](#2-api-endpoints)
  - [2.1 IntentSpecification resource APIs:](#21-intentspecification-resource-apis)
  - [2.2 Hub subscription APIs:](#22-hub-subscription-apis)
- [3. Common conventions:](#3-common-conventions)
  - [3.1 Expression schema alignment:](#31-expression-schema-alignment)
  - [3.2 IntentSpecification draft, identity, and versioning clarification:](#32-intentspecification-draft-identity-and-versioning-clarification)
  - [3.3 PATCH semantics:](#33-patch-semantics)
  - [3.4 Response locale:](#34-response-locale)
  - [3.5 Schema hash rule:](#35-schema-hash-rule)
  - [3.6 Response classification headers:](#36-response-classification-headers)
  - [3.7 Lifecycle values:](#37-lifecycle-values)
  - [3.8 Draft candidate identity model:](#38-draft-candidate-identity-model)
  - [3.9 Optional IntentSpecification behaviour metadata:](#39-optional-intentspecification-behaviour-metadata)
  - [3.10 Intent immutability clarification:](#310-intent-immutability-clarification)
  - [3.11 Versioning rules:](#311-versioning-rules)
  - [3.12 Caching and ETag rules:](#312-caching-and-etag-rules)
  - [3.13 Query parameter conventions:](#313-query-parameter-conventions)
- [4. Common error body:](#4-common-error-body)
  - [4.1 Common errors:](#41-common-errors)
  - [4.2 Missing If-Match response:](#42-missing-if-match-response)
  - [4.3 ETag mismatch response:](#43-etag-mismatch-response)
  - [4.4 Internal error response:](#44-internal-error-response)
- [5. Create IntentSpecification:](#5-create-intentspecification)
  - [5.1 Request:](#51-request)
  - [5.2 Success response:](#52-success-response)
- [6. List IntentSpecifications:](#6-list-intentspecifications)
  - [6.1 Request:](#61-request)
  - [6.2 Success response:](#62-success-response)
- [7. Retrieve IntentSpecification:](#7-retrieve-intentspecification)
  - [7.1 Request:](#71-request)
  - [7.2 Request with cache override:](#72-request-with-cache-override)
  - [7.3 Success response:](#73-success-response)
  - [7.4 DRAFT candidate retrieval:](#74-draft-candidate-retrieval)
  - [7.5 Produced version retrieval by draftId:](#75-produced-version-retrieval-by-draftid)
  - [7.6 Not found response:](#76-not-found-response)
- [8. Full replace DRAFT IntentSpecification candidate:](#8-full-replace-draft-intentspecification-candidate)
  - [8.1 Request:](#81-request)
  - [8.2 Success response:](#82-success-response)
  - [8.3 Immutable resource response:](#83-immutable-resource-response)
  - [8.4 Missing If-Match response:](#84-missing-if-match-response)
  - [8.5 ETag mismatch response:](#85-etag-mismatch-response)
- [9. Partial update DRAFT IntentSpecification candidate:](#9-partial-update-draft-intentspecification-candidate)
  - [9.1 Request:](#91-request)
  - [9.2 Success response:](#92-success-response)
- [10. Delete unused DRAFT IntentSpecification candidate:](#10-delete-unused-draft-intentspecification-candidate)
  - [10.1 Request:](#101-request)
  - [10.2 Success response:](#102-success-response)
  - [10.3 Delete rules:](#103-delete-rules)
  - [10.4 Delete blocked response:](#104-delete-blocked-response)
  - [10.5 Missing If-Match response:](#105-missing-if-match-response)
  - [10.6 ETag mismatch response:](#106-etag-mismatch-response)
  - [10.7 Retire current ACTIVE specification:](#107-retire-current-active-specification)
    - [10.7.1 Request:](#1071-request)
    - [10.7.2 Success response:](#1072-success-response)
    - [10.7.3 Retire rules:](#1073-retire-rules)
    - [10.7.4 Already retired response:](#1074-already-retired-response)
    - [10.7.5 Retire missing If-Match response:](#1075-retire-missing-if-match-response)
    - [10.7.6 Retire ETag mismatch response:](#1076-retire-etag-mismatch-response)
- [11. Activate IntentSpecification through lifecycle update:](#11-activate-intentspecification-through-lifecycle-update)
  - [11.1 PATCH activation request:](#111-patch-activation-request)
  - [11.2 PUT activation option:](#112-put-activation-option)
  - [11.3 Success response:](#113-success-response)
  - [11.4 Activation rules:](#114-activation-rules)
  - [11.5 Events emitted by activation:](#115-events-emitted-by-activation)
  - [11.6 Invalid lifecycle transition response:](#116-invalid-lifecycle-transition-response)
  - [11.7 Missing If-Match response:](#117-missing-if-match-response)
  - [11.8 ETag mismatch response:](#118-etag-mismatch-response)
- [12. Hub create subscription:](#12-hub-create-subscription)
  - [12.1 Request:](#121-request)
  - [12.2 Success response:](#122-success-response)
  - [12.3 Hub create rules:](#123-hub-create-rules)
- [13. Hub retrieve subscription:](#13-hub-retrieve-subscription)
  - [13.1 Request:](#131-request)
  - [13.2 Success response:](#132-success-response)
- [14. Hub delete subscription:](#14-hub-delete-subscription)
  - [14.1 Request:](#141-request)
  - [14.2 Success response:](#142-success-response)
  - [14.3 Missing If-Match response:](#143-missing-if-match-response)
  - [14.4 ETag mismatch response:](#144-etag-mismatch-response)
  - [14.5 Hub route and event scope rules:](#145-hub-route-and-event-scope-rules)
- [15. DB unavailable response:](#15-db-unavailable-response)
- [16. External event family:](#16-external-event-family)
- [17. Event envelope pattern:](#17-event-envelope-pattern)
- [18. IntentSpecificationCreateEvent:](#18-intentspecificationcreateevent)
- [19. IntentSpecificationAttributeValueChangeEvent:](#19-intentspecificationattributevaluechangeevent)
- [20. IntentSpecificationStatusChangeEvent:](#20-intentspecificationstatuschangeevent)
- [21. IntentSpecificationDeleteEvent:](#21-intentspecificationdeleteevent)
- [22. Final specification notes:](#22-final-specification-notes)
- [23. TMF compliance and platform extension baseline:](#23-tmf-compliance-and-platform-extension-baseline)
  - [23.1 Strict TMF-compliant baseline:](#231-strict-tmf-compliant-baseline)
  - [23.2 Accepted platform extensions:](#232-accepted-platform-extensions)
  - [23.3 Update method rule:](#233-update-method-rule)
  - [23.4 Lifecycle activation rule:](#234-lifecycle-activation-rule)
  - [23.5 Hub route rule:](#235-hub-route-rule)
  - [23.6 External event timestamp rule:](#236-external-event-timestamp-rule)
  - [23.7 Route prefix rule:](#237-route-prefix-rule)
  - [23.8 Baseline statement:](#238-baseline-statement)
- [24. Appendix A — External expression-value schema artefact:](#24-appendix-a-—-external-expression-value-schema-artefact)

## 1. Service identity:

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Definition MS |
| Short name | ID MS |
| Service name | `intent-definition-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `IntentSpecification` |
| Primary responsibility | Definition-time `IntentSpecification` catalogue, lifecycle and version governance, syntax contract, and external specification events |

### 1.1 Boundary statement:

ID MS owns definition-time `IntentSpecification` contracts and subscription management for specification events.
ID MS defines and governs the design-time `IntentSpecification` contract, including required fields, lifecycle rules, allowed expression shape, schema references, and validation constraints for runtime `Intent` payloads.
ID MS enforces specification lifecycle and version governance.
ID MS does not own runtime `Intent`, `IntentReport`, semantic validation, policy validation, network or resource feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

### 1.2 TMF deployment path note:

The examples in this specification use the platform base path `/intentManagement/v5`.
A strict TMF deployment may expose the same API through `/tmf-api/intentManagement/v5`; the API gateway may map between the deployment prefix and the platform-owned service path without changing resource semantics.

---

## 2. API endpoints:

### 2.1 IntentSpecification resource APIs:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create mutable DRAFT candidate | `POST` | `/intentManagement/v5/intentSpecification` |
| List specifications | `GET` | `/intentManagement/v5/intentSpecification` |
| Retrieve official ACTIVE and RETIRED specification by ID | `GET` | `/intentManagement/v5/intentSpecification/{id}` |
| Retire current ACTIVE specification | `DELETE` | `/intentManagement/v5/intentSpecification/{id}` |
| Retrieve DRAFT candidate or produced version by draftId | `GET` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Full replace DRAFT candidate | `PUT` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Partial update or activate DRAFT candidate | `PATCH` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Delete unused DRAFT candidate | `DELETE` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |

### 2.2 Hub subscription APIs:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/intentSpecification/hub` |
| Retrieve subscription by ID | `GET` | `/intentManagement/v5/intentSpecification/hub/{id}` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/intentSpecification/hub/{id}` |

---

## 3. Common conventions:

### 3.1 Expression schema alignment:

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



### 3.2 IntentSpecification draft, identity, and versioning clarification:

`IntentSpecification.version` is an official design-time contract version. It is assigned by ID MS only when a selected DRAFT candidate is activated. It is separate from runtime `Intent.version`.

Baseline rules:

- `POST /intentSpecification` always creates a mutable DRAFT candidate.
- The caller must provide `specKey` on create and must not provide `id`, `draftId`, `version`, `href`, `lifecycleStatus`, server timestamps, or `_links`.
- ID MS resolves the stable server-assigned `IntentSpecification.id` from `specKey` when the DRAFT candidate is created. The server-assigned `id` must not be assumed to equal `specKey`. If a current ACTIVE specification exists for the same `specKey`, the DRAFT candidate is assigned to that existing `id`; otherwise ID MS creates a new `id`. If only RETIRED versions exist for the same `specKey`, ID MS creates a new `id` unless governed lineage reuse is explicitly introduced later.
- ID MS assigns a new `draftId` for each mutable DRAFT candidate. Before activation, DRAFT candidate retrieval, update, activation, and deletion use `/intentSpecification/draft/{draftId}`. After activation, `GET /intentSpecification/draft/{draftId}` remains valid as a read-only provenance lookup for the official version produced from that DRAFT candidate.
- DRAFT candidates do not expose an official public `version`. ETag is used only as an optimistic concurrency token for unsafe DRAFT operations.
- DRAFT candidates do not expose or guarantee any version identifier. Any version indicator during authoring is non-authoritative.
- When a DRAFT candidate is activated, ID MS assigns the official `version`, carries the selected `draftId` forward as provenance, and transactionally retires the previous ACTIVE version for the same resolved `id`.
- `ACTIVE` and `RETIRED` `IntentSpecification` resources are immutable for material contract changes.
- Runtime `Intent.version` identifies the admitted runtime request/projection version and must not be confused with `IntentSpecification.version`.

### 3.3 PATCH semantics:

`PATCH` uses JSON Merge Patch semantics.

All external `PATCH` request examples must use:

```http
Content-Type: application/merge-patch+json
```

`PATCH` is intended for small targeted updates. For deterministic full replacement of editable Draft resources, use `PUT` where the platform extension is available.




### 3.4 Response locale:

`Content-Language: en-AU` is the platform default response locale used in examples. It does not change field names, enum values, identifiers, or JSON payload semantics.

### 3.5 Schema hash rule:

Where `targetEntitySchema.schemaHash` is supplied, real values must use the `sha256:<hex>` form. The placeholder `sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH` is illustrative only and must not be used in deployed resources. Verification against a schema registry is an implementation detail unless a stronger registry integration rule is introduced later.

The baseline surgical hospital slice is an illustrative example used to make the ID MS contract concrete. It is not the only supported IntentSpecification, intent type, service class, schema, expression IRI, or deployment profile. Other IntentSpecifications may use different targets, constraints, preferences, expression schemas, service types, and governance profiles while following the same ID MS contract rules.

### 3.6 Response classification headers:

ID MS returns a response classification header on external REST API responses so callers can distinguish strict TMF-compatible behaviour from documented platform-extension behaviour.

This is a response header only. Clients do not send this header in requests.

| **Response header** | **Meaning** |
|---|---|
| `X-Platform-Extension: true` | The route, method, response, or behaviour includes a documented platform extension. |
| `X-Platform-Extension: false` | No platform extension is used for the response. |

Header classification guidance:

| **ID MS response area** | **X-Platform-Extension** | **Reason** |
|---|---:|---|
| `POST /intentSpecification`, `GET /intentSpecification`, `GET /intentSpecification/{id}`, and `DELETE /intentSpecification/{id}` using strict TMF-compatible behaviour | `false` | TMF-compatible official IntentSpecification resource operations. |
| `GET /intentSpecification/draft/{draftId}`, `PUT /intentSpecification/draft/{draftId}`, `PATCH /intentSpecification/draft/{draftId}`, and `DELETE /intentSpecification/draft/{draftId}` | `true` | DRAFT-candidate route family is a platform extension used to retrieve, edit, activate, or delete mutable draft candidates before activation. |
| `PATCH /intentSpecification/draft/{draftId}` used for tightly controlled activation | `true` | Uses TMF-compatible partial-update semantics on the platform-extension DRAFT-candidate route. |
| `PUT /intentSpecification/draft/{draftId}` used for full-resource finalisation/activation | `true` | Full-resource finalisation through PUT on the DRAFT-candidate route is a platform extension. |
| Strict `/hub` create and delete responses | `false` | Strict TMF hub route family. |
| Domain-scoped `/intentSpecification/hub` responses | `true` | Domain-owned hub route family is a platform extension. |
| `GET /intentSpecification/hub/{id}` | `true` | Subscription retrieval is an operational convenience extension. |

Example strict TMF-compatible response classification header:

```http
X-Platform-Extension: false
```

Example platform-extension response classification header:

```http
X-Platform-Extension: true
```


### 3.7 Lifecycle values:

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DELETED` lifecycle status. Delete is an operation outcome, not a normal lifecycle state.


### 3.8 Draft candidate identity model:

ID MS follows the definition-candidate model used by the optimiser definition baseline:

```text
specKey -> resolves the stable server-assigned IntentSpecification.id
draftId -> selects the mutable DRAFT candidate before activation and acts as provenance lookup after activation
id -> selects the official ACTIVE and RETIRED lineage
version -> official version assigned only on activation
```

Runtime Intent admission must reference a concrete ACTIVE `IntentSpecification.id`. `specKey` and `draftId` must not be used for runtime contract selection. Runtime IC MS admission must still reject DRAFT candidates and RETIRED specifications for new runtime Intent creation. `draftId` provenance lookup is for definition governance and traceability only, not runtime admission.

Lineage reuse across retired-only specifications is not assumed by default. Reintroduction or reuse of a prior lineage requires explicit governance.

### 3.9 Optional IntentSpecification behaviour metadata:

`intentBehaviour` and `intentLayer` are optional classification metadata fields on `IntentSpecification`.

They support:

- catalogue visibility
- governance visibility
- external consumer understanding

They are not used by ID MS for:

- runtime decisioning
- runtime validation
- admission control
- behavioural enforcement

They are not required for DRAFT creation, activation, or runtime Intent admission in the current baseline. If omitted, ID MS does not infer or default these values unless an explicit platform policy is later introduced.

The only ID MS-level `intentBehaviour` fields defined in this baseline are:

- `category`
- `constraintMode`
- `objectiveType`
- `fulfilmentMode`

No additional behaviour fields are defined at ID MS level.

Example optional metadata for the hospital surgical slice specification:

```json
{
  "intentBehaviour": {
    "category": "REALTIME",
    "constraintMode": "STRICT",
    "objectiveType": "SLA",
    "fulfilmentMode": "CONTINUOUS"
  },
  "intentLayer": "SERVICE"
}
```

Controlled values:

| **Field** | **Allowed values** | **Meaning** |
|---|---|---|
| `intentBehaviour.category` | `REALTIME`, `BATCH`, `OPTIMISATION`, `ASSURANCE` | Broad behavioural type of intents created from the specification. |
| `intentBehaviour.constraintMode` | `STRICT`, `FLEXIBLE` | Whether constraints are normally mandatory or may be relaxed by governed policy or negotiation. |
| `intentBehaviour.objectiveType` | `SLA`, `COST`, `ENERGY`, `BALANCED` | Main decision or optimisation objective. |
| `intentBehaviour.fulfilmentMode` | `IMMEDIATE`, `LONGRUNNING`, `CONTINUOUS` | Fulfilment behaviour. |
| `intentLayer` | `BUSINESS`, `SERVICE`, `RESOURCE` | Abstraction layer of the intent. |

`fulfilmentMode` values mean:

| **Value** | **Meaning** |
|---|---|
| `IMMEDIATE` | Fulfilment is expected to complete in a short-lived operation. |
| `LONGRUNNING` | Fulfilment spans a longer-running workflow with delayed completion feedback. |
| `CONTINUOUS` | Downstream systems may operate in a closed-loop manner to maintain the intent objective over time. |

`IMMEDIATE` and `LONGRUNNING` describe fulfilment timing. `CONTINUOUS` indicates that downstream systems may operate in a closed-loop manner to maintain the intent objective over time. This does not imply mutation of the submitted runtime Intent instance.

These fields do not replace `expressionSpecification.iri`, `targetEntitySchema`, `specCharacteristic`, or request-specific `serviceType`, `serviceClass`, `priority`, targets, constraints, and preferences inside the governed expression schema.

### 3.10 Intent immutability clarification:

Runtime Intent instances created using an `ACTIVE` `IntentSpecification` remain tied to the specification identity and version used at admission.

- `IntentSpecification` lifecycle may evolve from `DRAFT` to `ACTIVE` to `RETIRED`.
- Existing runtime Intent instances referencing a `RETIRED` specification may continue under external platform governance policy.
- A change in intent requirements must result in submission of a new Intent instance. Runtime mutation of admitted Intent instances is not supported.
- ID MS does not mutate runtime Intent instances.
- `ACTIVE` and `RETIRED` `IntentSpecification` versions remain immutable for material contract changes.

### 3.11 Versioning rules:

- New specifications are normally created as `DRAFT`.
- `DRAFT` specifications are editable.
- `ACTIVE` and `RETIRED` specifications are immutable.
- Meaningful change after activation requires a new mutable DRAFT candidate.
- Only one ACTIVE official version is allowed for the same resolved `IntentSpecification.id`.
- At most one ACTIVE lineage may exist for a given `specKey`; duplicate ACTIVE lineages for the same `specKey` are a data-integrity breach.
- Activating a selected DRAFT candidate retires the previous ACTIVE version for the same resolved `id`.
- Retired specifications must not be used for new runtime `Intent` creation.
- Existing runtime Intent instances referencing a RETIRED specification may continue under external platform governance policy.

### 3.12 Caching and ETag rules:

Caching applies only to GET responses. No caching strategy is baselined for non-GET operations.

For cacheable GET operations, ID MS builds a deterministic cache key from the effective request shape. The cache key includes the request path, query parameters, selected `fields` projection, caller-safe response context where applicable, and any other input that can change the returned representation. The implementation may hash this key internally, but the externally documented behaviour is based on the deterministic cache key.

When a GET request is received:

1. ID MS builds the cache key for the effective request.
2. If the request does not include `Cache-Control: no-cache`, ID MS checks the cache for a valid unexpired response for that cache key.
3. If a valid cache entry exists, ID MS may return the cached response directly with the configured `Cache-Control` response header and the remaining cache lifetime represented according to the platform cache-header convention.
4. If no valid cache entry exists, ID MS compiles the response from the source-of-truth store, writes the response to cache with the configured TTL where safe, and returns the response with normal cache-control headers.

A consumer can bypass cached response serving by sending:

```http
Cache-Control: no-cache
```

When `Cache-Control: no-cache` is received, ID MS must bypass any existing cached response for that request, compile the response from the source-of-truth store, refresh the cache entry for the derived cache key where safe, and return the fresh response with normal cache-control headers.

ID MS may also invalidate or refresh affected cache entries on write paths or lifecycle transitions when it knows cached responses have become stale. IntentSpecification activation or retirement must invalidate or refresh affected active-version, retrieve-by-id, draft-provenance, and list cache entries so future GET requests do not return a previous active version as current.

Additional rules:

- Single-resource GET responses may use private cache with bounded TTL.
- List GET responses may use shorter private cache with bounded TTL.
- ETag is not used for GET revalidation.
- `If-None-Match` and `304 Not Modified` are not baselined.
- ETag is used only for unsafe operation concurrency through `If-Match`.


### 3.13 Query parameter conventions:

The following query parameters are supported where applicable:

| **Parameter** | **Applies to** | **Purpose** |
|---|---|---|
| `offset` | List | Zero-based result offset for pagination |
| `limit` | List | Maximum number of results returned |
| `fields` | Create, list, retrieve, update | Optional TMF-aligned field selection and projection parameter |
| `lifecycleStatus` | List | Filter specifications by lifecycle state |
| `name` | List | Filter specifications by name |
| `version` | List | Filter specifications by version |

`fields` is supported for TMF compatibility. When omitted, ID MS returns the default representation for the operation.

---

## 4. Common error body:

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

### 4.1 Common errors:

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

### 4.2 Missing If-Match response:

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

### 4.3 ETag mismatch response:

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
  "message": "The supplied ETag does not match the current resource version.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

### 4.4 Internal error response:

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "INTERNAL_ERROR",
  "reason": "UNEXPECTED_ERROR",
  "message": "An unexpected server error occurred while processing the request.",
  "status": 500,
  "referenceError": "https://mycsp.com.au/errors/INTERNAL_ERROR",
  "@type": "Error"
}
```

---

## 5. Create IntentSpecification:

`POST /intentSpecification` creates a mutable DRAFT candidate only. The request must include `specKey`; ID MS resolves the stable server-assigned `IntentSpecification.id` from `specKey` and assigns a new `draftId`. The DRAFT candidate has no official public `version`. ETag is used only as an optimistic concurrency token for unsafe DRAFT operations; it is not a business version and must not be treated as the official `IntentSpecification.version`. Any version indicator during draft authoring is non-authoritative and must not be relied on. DRAFT candidates do not expose or guarantee any version identifier.

### 5.1 Request:

```http
POST /intentManagement/v5/intentSpecification?fields=id,href,specKey,draftId,name,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,intentBehaviour,intentLayer,@type,@baseType
Content-Type: application/json
Accept: application/json
```

```json
{
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS defines and governs the allowed expression structure and schema references. IC MS performs runtime syntactic validation against the active specification. II MS and the Knowledge Plane validate semantic meaning, policy, and fulfilment feasibility.",
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
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/ispec-hss-001.schema.json",
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

### 5.2 Success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
ETag: "id-draft-hospital-surgical-slice-a-r1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
```

The response is classified with `X-Platform-Extension: false` because `POST /intentSpecification` is the TMF-aligned create operation. The `Location` points to the platform DRAFT candidate route because the created resource is a mutable DRAFT candidate addressed by `draftId` until activation.

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS defines and governs the allowed expression structure and schema references. IC MS performs runtime syntactic validation against the active specification. II MS and the Knowledge Plane validate semantic meaning, policy, and fulfilment feasibility.",
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

## 6. List IntentSpecifications:

### 6.1 Request:

```http
GET /intentManagement/v5/intentSpecification?offset=0&limit=10&lifecycleStatus=ACTIVE&fields=id,href,specKey,name,version,lifecycleStatus,isBundle,validFor,relatedParty,@type,@baseType
Accept: application/json
```

### 6.2 Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
X-Total-Count: 1
X-Result-Count: 1
ETag: "intent-spec-list-active-v17"
Cache-Control: private, max-age=60
```

```json
[
  {
    "id": "ispec-hss-001",
    "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec",
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
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001"
      },
      "collection": {
        "href": "/intentManagement/v5/intentSpecification"
      },
      "retire": {
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
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

The list operation returns a lightweight summary by default. For `ACTIVE` and `RETIRED` official versions, `href` and `self` use `/intentSpecification/{id}`. The default list response does not include `draftId`, full `specCharacteristic`, `expressionSpecification`, or `targetEntitySchema` unless explicitly requested through `fields`. Where returned, `draftId` is immutable provenance only; DRAFT candidate mutation still uses `/intentSpecification/draft/{draftId}`.

---

## 7. Retrieve IntentSpecification:

This operation retrieves the current official `ACTIVE` version by `id` by default. Historical `ACTIVE` or `RETIRED` versions are selected by `id` plus an explicit `version` query parameter. Mutable DRAFT candidates are retrieved through `GET /intentSpecification/draft/{draftId}`.

### 7.1 Request:

```http
GET /intentManagement/v5/intentSpecification/ispec-hss-001?fields=id,href,specKey,draftId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Accept: application/json
```

### 7.2 Request with cache override:

```http
GET /intentManagement/v5/intentSpecification/ispec-hss-001?fields=id,href,specKey,draftId,name,description,version,lifecycleStatus,isBundle,validFor,relatedParty,specCharacteristic,expressionSpecification,targetEntitySchema,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### 7.3 Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intentSpecification/ispec-hss-001
ETag: "intent-spec-ispec-hss-001-v1.19-r1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
Cache-Control: private, max-age=300
```

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS defines and governs the allowed expression structure and schema references. IC MS performs runtime syntactic validation against the active specification. II MS and the Knowledge Plane validate semantic meaning, policy, and fulfilment feasibility.",
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
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/ispec-hss-001.schema.json",
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
      "href": "/intentManagement/v5/intentSpecification/ispec-hss-001"
    },
    "collection": {
      "href": "/intentManagement/v5/intentSpecification"
    },
    "retire": {
      "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
      "method": "DELETE"
    },
    "createNewVersion": {
      "href": "/intentManagement/v5/intentSpecification",
      "method": "POST"
    }
  }
}
```

### 7.4 DRAFT candidate retrieval:

```http
GET /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
Accept: application/json
```

DRAFT candidate retrieval returns the mutable DRAFT candidate selected by `draftId`. DRAFT responses include `draftId`, omit official public `version`, and expose DRAFT action links such as `patch`, `replace`, `delete`, and `activate` using `/intentSpecification/draft/{draftId}`.

After activation, the same `GET /intentSpecification/draft/{draftId}` route may be used as a provenance lookup. In that case, ID MS returns the official read-only `IntentSpecification` version produced from the DRAFT candidate. The response shows the official `id`, official `version`, carried-forward `draftId`, and `lifecycleStatus` of `ACTIVE` or `RETIRED`. DRAFT mutation links such as `patch`, `replace`, `delete`, and `activate` must not be returned for the produced official version.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
Content-Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
ETag: "id-draft-hospital-surgical-slice-a-r1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS defines and governs the allowed expression structure and schema references. IC MS performs runtime syntactic validation against the active specification. II MS and the Knowledge Plane validate semantic meaning, policy, and fulfilment feasibility.",
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
  "intentBehaviour": {
    "category": "REALTIME",
    "constraintMode": "STRICT",
    "objectiveType": "SLA",
    "fulfilmentMode": "CONTINUOUS"
  },
  "intentLayer": "SERVICE",
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




### 7.5 Produced version retrieval by draftId:

After activation, `draftId` remains valid as a provenance lookup key. The lookup returns the official read-only version produced from the DRAFT candidate and removes DRAFT mutation links.

```http
GET /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-b
Accept: application/json
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
Content-Location: /intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20
ETag: "intent-spec-ispec-hss-001-v1.20-r1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-b",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS defines and governs the allowed expression structure and schema references. IC MS performs runtime syntactic validation against the active specification. II MS and the Knowledge Plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.20",
  "lifecycleStatus": "ACTIVE",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "intentBehaviour": {
    "category": "REALTIME",
    "constraintMode": "STRICT",
    "objectiveType": "SLA",
    "fulfilmentMode": "CONTINUOUS"
  },
  "intentLayer": "SERVICE",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20",
      "method": "GET"
    },
    "provenance": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-b",
      "method": "GET"
    },
    "collection": {
      "href": "/intentManagement/v5/intentSpecification"
    }
  }
}
```

### 7.6 Not found response:

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
```

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "reason": "INTENT_SPECIFICATION_NOT_FOUND",
  "message": "IntentSpecification ispec-hss-001 was not found.",
  "status": 404,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",
  "@type": "Error"
}
```

---

## 8. Full replace DRAFT IntentSpecification candidate:

`PUT` is the preferred platform extension for deterministic full replacement of an editable `DRAFT` specification.

### 8.1 Request:

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
  "description": "Updated definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS defines and governs the allowed expression structure and schema references. IC MS performs runtime syntactic validation against the active specification. II MS and the Knowledge Plane validate semantic meaning, policy, and fulfilment feasibility.",
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

### 8.2 Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
Content-Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
ETag: "id-draft-hospital-surgical-slice-a-r2"
Last-Modified: Sat, 18 Apr 2026 03:00:00 GMT
```

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS defines and governs the allowed expression structure and schema references. IC MS performs runtime syntactic validation against the active specification. II MS and the Knowledge Plane validate semantic meaning, policy, and fulfilment feasibility.",
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
      "method": "PATCH"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "method": "DELETE"
    }
  }
}
```

### 8.3 Immutable resource response:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 8.4 Missing If-Match response:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 8.5 ETag mismatch response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

## 9. Partial update DRAFT IntentSpecification candidate:

`PATCH` remains supported for TMF compatibility, but it is discouraged as a general update method.
Prefer `PUT` for deterministic full replacement of editable `DRAFT` specifications.
Use `PATCH` only where a TMF-compatible client cannot use `PUT` or where a tightly controlled, small targeted compatibility update is required.

`PATCH` must not normally be used for material contract replacement, including `specKey`, `version`, `specCharacteristic`, `expressionSpecification`, `targetEntitySchema`, or major lifecycle and version contract identity.

### 9.1 Request:

```http
PATCH /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a?fields=id,href,specKey,name,description,lifecycleStatus,isBundle,validFor,relatedParty,@type,@baseType
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "id-draft-hospital-surgical-slice-a-r1"
```

```json
{
  "description": "Updated draft description only."
}
```

### 9.2 Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
Content-Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
ETag: "id-draft-hospital-surgical-slice-a-r2"
Last-Modified: Sat, 18 Apr 2026 03:00:00 GMT
```

```json
{
  "id": "ispec-hss-001",
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
      "method": "PATCH"
    }
  }
}
```

---

## 10. Delete unused DRAFT IntentSpecification candidate:

### 10.1 Request:

```http
DELETE /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
If-Match: "id-draft-hospital-surgical-slice-a-r1"
Accept: application/json
```

### 10.2 Success response:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
X-Platform-Extension: true
```

No response body is returned.

### 10.3 Delete rules:

| **Rule** | **Baseline** |
|---|---|
| Allowed lifecycle | `DRAFT` only |
| Blocked lifecycle | `ACTIVE`, `RETIRED` |
| Runtime references | Delete is blocked if the specification is referenced by runtime `Intent` resources |
| Audit/history dependency | Delete is blocked if retention is required for audit/history |
| ETag required | `If-Match` is required |
| Missing `If-Match` | `428 Precondition Required` |
| Stale or mismatched `If-Match` | `412 Precondition Failed` |
| Delete outcome | Physical or logical removal is an implementation detail |
| Resource lifecycle | Do not set `lifecycleStatus = DELETED` |
| Event emitted | `IntentSpecificationDeleteEvent` after successful delete only |

### 10.4 Delete blocked response:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 10.5 Missing If-Match response:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 10.6 ETag mismatch response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 10.7 Retire current ACTIVE specification:

`DELETE /intentSpecification/{id}` retires the current ACTIVE official specification. It does not physically delete the official resource.

#### 10.7.1 Request:

```http
DELETE /intentManagement/v5/intentSpecification/ispec-hss-001
If-Match: "intent-spec-ispec-hss-001-v1.20-r1"
Accept: application/json
```

#### 10.7.2 Success response:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
X-Platform-Extension: false
```

No response body is returned.

#### 10.7.3 Retire rules:

| **Rule** | **Baseline** |
|---|---|
| Allowed lifecycle | `ACTIVE` only |
| Outcome | Current official version becomes `RETIRED` |
| Runtime references | Existing runtime Intent instances referencing a RETIRED specification may continue under external platform governance policy |
| ETag required | `If-Match` is required |
| Missing `If-Match` | `428 Precondition Required` |
| Stale or mismatched `If-Match` | `412 Precondition Failed` |
| Already retired | `409 Conflict` |
| Event emitted | `IntentSpecificationStatusChangeEvent` after successful retirement |

#### 10.7.4 Already retired response:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "INVALID_LIFECYCLE_TRANSITION",
  "reason": "INTENT_SPECIFICATION_RETIREMENT_NOT_ALLOWED",
  "message": "Only ACTIVE IntentSpecification resources can be retired.",
  "status": 409,
  "referenceError": "https://mycsp.com.au/errors/INVALID_LIFECYCLE_TRANSITION",
  "@type": "Error"
}
```


#### 10.7.5 Retire missing If-Match response:

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

#### 10.7.6 Retire ETag mismatch response:

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
  "message": "The supplied ETag does not match the current resource version.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

## 11. Activate IntentSpecification through lifecycle update:

A DRAFT `IntentSpecification` candidate is activated through the DRAFT-candidate resource route. Activation is a governed lifecycle update from `DRAFT` to `ACTIVE`.

Supported activation options:

| **Option** | **Route** | **Use** |
|---|---|---|
| TMF-compatible partial lifecycle update | `PATCH /intentManagement/v5/intentSpecification/draft/{draftId}` | Activate a DRAFT candidate with a small JSON Merge Patch body such as `{ "lifecycleStatus": "ACTIVE" }`. |
| Preferred platform full replacement | `PUT /intentManagement/v5/intentSpecification/draft/{draftId}` | Submit the complete DRAFT candidate representation and set `lifecycleStatus` to `ACTIVE` as a governed activation instruction. |

Both activation options require `If-Match`. `PATCH` remains discouraged for general editing, but is acceptable for this tightly controlled lifecycle update. `PUT` is preferred where the caller sends the complete DRAFT candidate representation.

ID MS does not expose a separate custom action endpoint such as `POST /intentManagement/v5/intentSpecification/{id}/activate`; activation remains part of the governed DRAFT-candidate resource update model.

### 11.1 PATCH activation request:

The following activation example assumes a second DRAFT candidate, `id-draft-hospital-surgical-slice-b`, was created for the next official version after earlier draft work on `id-draft-hospital-surgical-slice-a`.

```http
PATCH /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-b?fields=id,href,specKey,name,lifecycleStatus,previousActiveSpecification,@type,@baseType
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "id-draft-hospital-surgical-slice-b-r3"
```

```json
{
  "lifecycleStatus": "ACTIVE"
}
```

### 11.2 PUT activation option:

`PUT` may also be used when the caller sends the full replacement representation with `lifecycleStatus: ACTIVE` as part of the complete `IntentSpecification` resource. In this case, ID MS treats `lifecycleStatus: ACTIVE` as a governed activation instruction for the selected DRAFT candidate, not as a free-form mutation of a server-managed field. The activation request still requires `If-Match` and must satisfy the ACTIVE profile before ID MS promotes the candidate.

### 11.3 Success response:

Activation returns the full promoted ACTIVE `IntentSpecification` resource representation. `previousActiveSpecification` is included as an activation governance projection when a previous ACTIVE version was retired during the same transaction.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
Content-Location: /intentManagement/v5/intentSpecification/ispec-hss-001
ETag: "intent-spec-hospital-surgical-slice-r4"
Last-Modified: Sat, 18 Apr 2026 03:30:00 GMT
```

Activation full response body example:

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS defines and governs the allowed expression structure and schema references. IC MS performs runtime syntactic validation against the active specification. II MS and the Knowledge Plane validate semantic meaning, policy, and fulfilment feasibility.",
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
  "intentBehaviour": {
    "category": "REALTIME",
    "constraintMode": "STRICT",
    "objectiveType": "SLA",
    "fulfilmentMode": "CONTINUOUS"
  },
  "intentLayer": "SERVICE",
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
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.20.expression.schema.json",
    "schemaVersion": "1.20",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  },
  "previousActiveSpecification": {
    "id": "ispec-hss-001",
    "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.19",
    "version": "1.19",
    "lifecycleStatus": "RETIRED"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/ispec-hss-001"
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

### 11.4 Activation rules:

| **Rule** | **Baseline** |
|---|---|
| Source state | Only `DRAFT` can be activated |
| Target state | Activated version becomes `ACTIVE` |
| Previous active | Previous `ACTIVE` version for the same resolved `id` becomes `RETIRED` transactionally |
| New runtime creation | New runtime intents must use the new `ACTIVE` version |
| Existing runtime intents | Existing runtime Intent instances referencing a RETIRED specification may continue under external platform governance policy |
| Material update after activation | Not allowed; create a new mutable DRAFT candidate |
| ETag required | `If-Match` is required |
| Missing `If-Match` | `428 Precondition Required` |
| Stale or mismatched `If-Match` | `412 Precondition Failed` |
| Invalid lifecycle transition | `409 Conflict` |

### 11.5 Events emitted by activation:

Activation emits `IntentSpecificationStatusChangeEvent` for lifecycle transitions:

1. One event for the newly activated version, with the emitted `intentSpecification.lifecycleStatus` set to `ACTIVE`.
2. One event for the previous active version in the same `specKey`, with the emitted `intentSpecification.lifecycleStatus` set to `RETIRED`, when a previous active version exists.

Creating or editing a DRAFT candidate does not emit `IntentSpecificationStatusChangeEvent`. DRAFT creation may emit `IntentSpecificationCreateEvent`, and DRAFT attribute changes may emit `IntentSpecificationAttributeValueChangeEvent` where subscribed.

The status-change event type identifies that the lifecycle status changed. The event body carries the current `IntentSpecification` resource snapshot and does not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields.

### 11.6 Invalid lifecycle transition response:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 11.7 Missing If-Match response:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 11.8 ETag mismatch response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

## 12. Hub create subscription:

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

### 12.1 Request:

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

### 12.2 Success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hub/sub-001
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 12.3 Hub create rules:

- The subscription callback is an external listener endpoint owned by the consuming system.
- The `query` field filters delivered events.
- ID MS hub subscriptions are for external IntentSpecification events only: `IntentSpecificationCreateEvent`, `IntentSpecificationAttributeValueChangeEvent`, `IntentSpecificationStatusChangeEvent`, and `IntentSpecificationDeleteEvent`.
- ID MS delivers subscribed events by HTTP `POST` to the stored subscriber callback URL.
- ID MS does not publish hub notifications to Kafka and does not create a self-publish/self-consume Kafka loop for external subscription delivery.
- ID MS uses a local delivery outbox and retry relay to track pending, delivered, failed, and retryable webhook notification work.
- ID MS hub subscriptions must not expose internal workflow events, KP details, runtime assurance state, telemetry, callback payloads, or internal fulfilment details.

---

## 13. Hub retrieve subscription:

`GET /intentManagement/v5/intentSpecification/hub/{id}` is a platform extension for operational convenience.
It is not required by the strict TMF generic hub route shape, but is retained because it gives operators and consumers a safe way to inspect an ID MS-owned subscription without exposing internal workflow state.

### 13.1 Request:

```http
GET /intentManagement/v5/intentSpecification/hub/sub-001
Accept: application/json
```

### 13.2 Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

## 14. Hub delete subscription:

### 14.1 Request:

```http
DELETE /intentManagement/v5/intentSpecification/hub/sub-001
If-Match: "subscription-sub-001-v1"
Accept: application/json
```

### 14.2 Success response:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
X-Platform-Extension: true
```

No response body is returned.

### 14.3 Missing If-Match response:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 14.4 ETag mismatch response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-Platform-Extension: true
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

### 14.5 Hub route and event scope rules:

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
| Stale or mismatched `If-Match` | `412 Precondition Failed` |
| Create response | `201 Created` with `Location`, `ETag`, body, and `_links` |
| Retrieve response | `200 OK` with `ETag` and GET-only private caching |
| Delete response | `204 No Content` |
| Hub must not expose | Internal workflow events, KP details, runtime assurance state, telemetry, callback payloads, or internal fulfilment details |

---

## 15. DB unavailable response:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Content-Language: en-AU
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

## 16. External event family:

ID MS emits external TMF-aligned resource events for `IntentSpecification` changes.

| **Event** | **Trigger** |
|---|---|
| `IntentSpecificationCreateEvent` | New `IntentSpecification` created |
| `IntentSpecificationAttributeValueChangeEvent` | Editable draft attributes changed |
| `IntentSpecificationStatusChangeEvent` | Lifecycle status changes, such as activation to `ACTIVE` or retirement to `RETIRED` |
| `IntentSpecificationDeleteEvent` | Unused draft specification deleted after delete succeeds |

These are external subscription events for the `IntentSpecification` resource. They are not internal fulfilment events and must not expose II MS semantic validation details, lightweight II MS KP details, `t7.knowledge plane` data, optimiser decisions, runtime assurance state, telemetry, callback payloads, or internal candidate and resource scoring details.

Event resource snapshots should carry consistent resource metadata:

- `id`
- `href`
- `specKey`
- `draftId` where the event carries a DRAFT candidate snapshot
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

Activation emits `IntentSpecificationStatusChangeEvent` for lifecycle transitions:

- one for the newly activated version, with `intentSpecification.lifecycleStatus` set to `ACTIVE`
- one for the previous active version, with `intentSpecification.lifecycleStatus` set to `RETIRED`, when a previous active version exists

Creating or editing a DRAFT candidate does not emit `IntentSpecificationStatusChangeEvent`. DRAFT creation may emit `IntentSpecificationCreateEvent`, and DRAFT attribute changes may emit `IntentSpecificationAttributeValueChangeEvent` where subscribed.

Delete events are emitted only after successful delete and show the last known lifecycle state as `DRAFT`. Delete events must not use `DELETED`.

---

## 17. Event envelope pattern:

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
      "id": "ispec-hss-001",
      "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
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

## 18. IntentSpecificationCreateEvent:

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
      "id": "ispec-hss-001",
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "specKey": "hospital-surgical-slice-spec",
      "draftId": "id-draft-hospital-surgical-slice-a",
      "name": "Hospital Surgical Slice Intent Specification",
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

## 19. IntentSpecificationAttributeValueChangeEvent:

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
      "id": "ispec-hss-001",
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
      "specKey": "hospital-surgical-slice-spec",
      "draftId": "id-draft-hospital-surgical-slice-a",
      "name": "Hospital Surgical Slice Intent Specification",
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

## 20. IntentSpecificationStatusChangeEvent:

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
      "id": "ispec-hss-001",
      "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
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

## 21. IntentSpecificationDeleteEvent:

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
      "id": "ispec-hss-001",
      "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-old",
      "specKey": "hospital-surgical-slice-spec",
      "draftId": "id-draft-hospital-surgical-slice-old",
      "name": "Hospital Surgical Slice Intent Specification",
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

## 22. Final specification notes:

- `@baseType` is `EntitySpecification`, not `ResourceSpecification`.
- `specCharacteristic` is the high-level characteristic catalogue.
- `expressionSpecification` is the authoritative request-shape schema.
- `characteristicValueSpecification` is used only for defaults, examples, or constrained allowed values where useful.
- Numeric SLA values in `characteristicValueSpecification` are illustrative/default guidance only, not semantic enforcement.
- ID MS validates resource shape and syntax.
- II MS and knowledge sources own semantic and policy validation.
- IA MS owns runtime assurance.
- `timeWindow.startDateTime` is required when `timeWindow` is present.
- `priority` values are `critical`, `high`, and `standard`.
- `intentBehaviour` and `intentLayer` are optional definition-time metadata fields for catalogue classification, governance visibility, and external consumer understanding.
- `intentBehaviour` and `intentLayer` are not used by ID MS for behavioural enforcement, runtime decisioning, validation, or admission control.
- `intentBehaviour.fulfilmentMode` values are `IMMEDIATE`, `LONGRUNNING`, and `CONTINUOUS`. `CONTINUOUS` indicates that downstream systems may operate in a closed-loop manner to maintain the intent objective over time. This does not imply mutation of the submitted runtime Intent instance.
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

## 23. TMF compliance and platform extension baseline:

### 23.1 Strict TMF-compliant baseline:

For strict TMF alignment, ID MS supports the TMF-aligned `IntentSpecification` operations:

| **Operation** | **Endpoint** | **Position** |
|---|---|---|
| Create | `POST /intentManagement/v5/intentSpecification` | TMF-aligned |
| List | `GET /intentManagement/v5/intentSpecification` | TMF-aligned |
| Retrieve | `GET /intentManagement/v5/intentSpecification/{id}` | TMF-aligned |
| Partial update DRAFT candidate | `PATCH /intentManagement/v5/intentSpecification/draft/{draftId}` | TMF-compatible partial-update semantics on a platform-extension DRAFT-candidate route |
| Delete | `DELETE /intentManagement/v5/intentSpecification/{id}` | TMF-aligned |
| Event subscription | `POST /hub`, `DELETE /hub/{id}` | Strict TMF route form where required |

### 23.2 Accepted platform extensions:

Controlled platform extensions are acceptable when they are documented, non-breaking, and do not conflict with TMF semantics.

For ID MS, accepted platform extensions are:

| **Extension** | **Purpose** | **Rule** |
|---|---|---|
| `PUT /intentManagement/v5/intentSpecification/draft/{draftId}` | Deterministic full replacement of mutable draft candidates | Preferred platform update method where supported |
| `GET`, `PATCH`, and `DELETE /intentManagement/v5/intentSpecification/draft/{draftId}` | Draft-candidate route family | Platform route family for draft retrieval, editing, activation, and deletion before official activation |
| `/intentManagement/v5/intentSpecification/hub` | Domain-scoped event subscription route | Allowed as a clearer domain-owned route when deliberately chosen |
| `GET /intentManagement/v5/intentSpecification/hub/{id}` | Subscription inspection | Platform convenience operation; not required by strict TMF generic hub shape |
| `DELETE /intentManagement/v5/intentSpecification/hub/{id}` | Domain-scoped subscription removal | Allowed as a clearer domain-owned route when deliberately chosen |
| `specKey` | Specification-key grouping across versions | Platform governance field; does not replace TMF `id` or `version` |
| `_links` | Lifecycle-aware navigation and operation hints | Platform HATEOAS extension; clients must not require it for strict TMF compatibility |
| `previousActiveSpecification` | Activation outcome trace | Platform governance projection showing the version retired during activation |
| Strong `ETag` and `If-Match` governance | Unsafe-operation concurrency control | Platform concurrency policy applied consistently to mutable operations |
| `428 Precondition Required` | Missing precondition response | Platform concurrency policy for unsafe operations that require `If-Match` |

### 23.3 Update method rule:

`PATCH` is the strict TMF-compatible update operation.
`PUT` is the platform extension for deterministic full replacement and is preferred from the platform engineering perspective where clients support it.
`PATCH` remains supported for TMF compatibility but is not encouraged for ordinary edits when deterministic full replacement is available.

### 23.4 Lifecycle activation rule:

Activation and retirement are represented as resource updates to `IntentSpecification.lifecycleStatus`.

Use:

```http
PATCH /intentManagement/v5/intentSpecification/draft/{draftId}
```

for TMF-compatible partial-update semantics on the platform-extension DRAFT-candidate route.

Use:

```http
PUT /intentManagement/v5/intentSpecification/draft/{draftId}
```

as a platform extension when performing deterministic full replacement.

Activation is performed through the DRAFT-candidate update route. Do not add a separate custom lifecycle action endpoint such as:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate  (not exposed)
```

### 23.5 Hub route rule:

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

### 23.6 External event timestamp rule:

For external TMF-aligned resource events, ID MS populates both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp.
`timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples.
TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics.
Internal events remain separate and continue to use the platform CloudEvents/header model plus the relevant internal body timestamp fields.

### 23.7 Route prefix rule:

The examples in this specification use `/intentManagement/v5` as the platform service base path.
A strict TMF-compatible API gateway may map deployment-specific external prefixes to the platform-owned service path; this is a deployment concern and must not change resource ownership, payload semantics, or lifecycle governance.

### 23.8 Baseline statement:

ID MS and IC MS remain TMF-aligned at the external contract level.
Controlled platform extensions are allowed when documented, non-breaking, and semantically compatible with TMF.

For ID MS, `PATCH /intentSpecification/draft/{draftId}` uses TMF-compatible partial-update semantics on the platform-extension DRAFT-candidate route, while `PUT /intentSpecification/draft/{draftId}` is an accepted platform extension for deterministic full replacement of mutable DRAFT candidates.
TMF `/hub` routing is the strict subscription route form, while `/intentSpecification/hub` is an accepted domain-scoped platform extension when deliberately used.

---

## 24. Appendix A — External expression-value schema artefact:

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