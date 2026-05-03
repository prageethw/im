# Context Dump

This file is the running baseline dump for this conversation. New baselines are appended to the end unless explicitly requested otherwise.

---

## Baseline: Reference books for Gurobi optimisation architecture exercise

The following uploaded books are accepted as the reference base for the Spring Boot + Kafka + Python/Gurobi optimisation exercise:

1. **REST in Practice** — use for REST API/resource design, HTTP methods, resource naming, status codes, representations, links, and web integration principles.
2. **Microservices Patterns** — use for Spring Boot/microservice structure, service boundaries, hexagonal architecture, inbound/outbound adapters, asynchronous messaging, transactional outbox, polling publisher / transaction-log tailing, duplicate handling, and microservice-owned persistence.
3. **Designing Data-Intensive Applications** — use for reliability, scalability, maintainability, transactions, fault tolerance, distributed systems, stream processing, dataflow, correctness, and persistence trade-offs.
4. **Building Event-Driven Microservices, 2nd Edition** — use for Kafka/event-stream design, event-driven microservices, event schemas/data contracts, eventification, request-response/event-driven integration, transactional outbox, durable event flow, and eventual consistency.

Reference usage rule:

```text
REST API shape:
  REST in Practice

Spring Boot microservice structure:
  Microservices Patterns

Outbox/inbox, asynchronous messaging, Kafka relay:
  Microservices Patterns + Building Event-Driven Microservices

Event schema, event contract, event stream design:
  Building Event-Driven Microservices

Database, transactions, reliability, consistency, scalability:
  Designing Data-Intensive Applications

Optimisation execution:
  Gurobi documentation / API reference
```

Current REST endpoint direction remains:

```http
POST /optimisation
GET  /optimisation/{optimisationId}
GET  /optimisation
POST /optimisation/{optimisationId}/cancel
POST /optimisation/{optimisationId}/retry
```

Design interpretation:

- `/optimisation` is the REST resource collection.
- `POST /optimisation` creates or accepts a new asynchronous optimisation job.
- `GET /optimisation/{optimisationId}` retrieves current status and final result when available.
- `202 Accepted` is the preferred response for creation because the Python/Gurobi optimisation work completes asynchronously.
- Spring Boot REST controller is treated as the inbound adapter into the optimisation request service.
- Spring Boot writes the optimisation request and outbox event in one local transaction.
- Outbox relay publishes the request event to Kafka.
- Python/Gurobi worker consumes through an inbox/idempotency boundary, processes with Gurobi, writes result state and a result outbox event, and publishes back to Kafka.
- Spring Boot consumes the result event through an inbox/idempotency boundary and updates the optimisation resource state exposed to the client.

---

---

## Baseline Update — REST HATEOAS, ETag Concurrency, and Cache-Control Position

For the Gurobi optimisation architecture exercise, the active REST interface baseline is:

- Follow full HATEOAS principles for REST interfaces.
- Resource representations must include hypermedia links/actions for valid next transitions.
- Clients should discover available state transitions from the representation instead of hardcoding workflow URLs.
- Available links/actions must vary by resource state.
- Aim for Richardson Maturity Model Level 3 where practical.
- Mutable optimisation resource responses must include an `ETag`.
- State-changing operations that depend on current resource state must require `If-Match` with the latest ETag.
- If `If-Match` is missing where required, return `428 Precondition Required`.
- If `If-Match` is stale, wrong, or does not match the current resource version, return `412 Precondition Failed`.
- Use ETags as the concurrency control mechanism for actions such as cancel, retry, update, or other resource-state transitions.
- Do not include `Cache-Control` headers in REST responses for now unless explicitly requested for a specific endpoint/response later.
- Client request-side `Cache-Control: no-cache` may be used by the caller when it wants to force revalidation or bypass cached reuse, but response-side `Cache-Control` is not part of the active baseline for now.

Example GET response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "opt-12345-v3"
```

Example state-changing request:

```http
POST /optimisation/opt-12345/cancel
If-Match: "opt-12345-v3"
```

Example missing precondition response:

```http
HTTP/1.1 428 Precondition Required
```

Example stale ETag response:

```http
HTTP/1.1 412 Precondition Failed
```

---

# Baselined OD MS / Optimisation-Definition-MS REST Specification

## 1. OD MS summary

Optimisation-Definition-MS (OD MS) owns the definition side of the optimisation platform. Its responsibility is to publish and govern the externally visible optimisation capability contract, called `OptimisationSpecification`.

OD MS does not expose the Gurobi model, objective logic, candidate-resource rules, solver configuration, model binding, or internal optimisation formulation. It only exposes what a caller needs to know to create a valid runtime optimisation through OC MS.

```text
OD MS owns:
  OptimisationSpecification

OD MS does not own:
  Runtime Optimisation execution
  Kafka outbox/inbox processing
  Gurobi solver execution
  Optimisation result projection
```

In one sentence:

```text
OD MS is the governed catalogue of optimisation capabilities; it tells callers what inputs they must provide, while the platform privately owns how those inputs are translated into deterministic Gurobi execution.
```

## 2. OD MS endpoint set

```http
# List/search OptimisationSpecification resources.
GET /optimisationSpecification

# Create a new OptimisationSpecification.
# ID is generated by OD MS.
POST /optimisationSpecification

# Retrieve one OptimisationSpecification.
GET /optimisationSpecification/{id}

# Full replacement/update.
# Allowed only while lifecycleStatus is DRAFT.
PUT /optimisationSpecification/{id}

# Delete a DRAFT OptimisationSpecification.
# ACTIVE and RETIRED specifications cannot be deleted.
DELETE /optimisationSpecification/{id}
```

## 3. OptimisationSpecification lifecycle

```text
DRAFT
ACTIVE
RETIRED
```

```text
DRAFT:
  Specification is being prepared.
  It can be updated or deleted with If-Match.

ACTIVE:
  Specification can be used by OC MS to create runtime Optimisation resources.
  ACTIVE specifications are immutable.
  PUT and DELETE are not allowed.

RETIRED:
  Specification is no longer usable for new runtime Optimisation resources.
  It remains available for audit/history and existing Optimisation references.
```

No normal lifecycle state called:

```text
DELETED
ARCHIVED
```

## 4. Version activation rule

```text
Only one ACTIVE OptimisationSpecification is allowed per specificationKey.

When a DRAFT specification is promoted to ACTIVE, OD MS must transactionally retire the previous ACTIVE specification with the same specificationKey.
```

Example:

```jsonc
{
  // Stable family/key shared by all versions of the same optimisation capability.
  "specificationKey": "hospital-surgical-slice-path-optimisation",

  // Version of this specific specification.
  "version": "1.1",

  // Promoting this version to ACTIVE retires the previous ACTIVE version
  // with the same specificationKey.
  "lifecycleStatus": "ACTIVE"
}
```

Transactional activation logic:

```text
1. Validate If-Match for the target DRAFT specification.
2. Validate target specification is currently DRAFT.
3. Validate requested lifecycleStatus is ACTIVE.
4. Find current ACTIVE specification with the same specificationKey.
5. Move old ACTIVE specification to RETIRED.
6. Move target DRAFT specification to ACTIVE.
7. Update ETags and lastUpdate timestamps for changed resources.
8. Commit atomically.
```

## 5. Public OptimisationSpecification shape

The public OD MS resource exposes only the caller-facing input contract.

It exposes:

```text
id
href
specificationKey
type
baseType
schemaLocation
name
description
version
lifecycleStatus
creationDate
lastUpdate
inputs
_links
```

It does not expose by default:

```text
supportedInputModes
allowedObjectives
candidateResourceRules
solverConfiguration
modelBinding
resultSchema
inputType
sourceType
operator
inputTypeVocabulary
operatorVocabulary
full Gurobi formulation
internal objective logic
resource selection logic
```

Example resource:

```jsonc
{
  // Server-generated identity.
  "id": "os-7f3a9c21",
  "href": "/optimisationSpecification/os-7f3a9c21",

  // Stable capability family key.
  // Only one ACTIVE version is allowed per specificationKey.
  "specificationKey": "hospital-surgical-slice-path-optimisation",

  // TMF-aligned typing.
  "type": "OptimisationSpecification",
  "baseType": "EntitySpecification",
  "schemaLocation": "/schema/OptimisationSpecification.schema.json",

  // Public capability metadata.
  "name": "Hospital surgical slice path optimisation",
  "description": "Optimisation capability for hospital surgical slice path selection.",
  "version": "1.0",

  // Specification lifecycle.
  // DRAFT, ACTIVE, or RETIRED.
  "lifecycleStatus": "ACTIVE",

  // Server-owned timestamps.
  "creationDate": "2026-05-02T01:00:00Z",
  "lastUpdate": "2026-05-02T02:00:00Z",

  // Public caller-facing input contract only.
  // This exposes what external callers must or may feed into POST /optimisation.
  // It does not expose objective logic, candidate rules, solver config, model binding, or Gurobi formulation.
  "inputs": [
    {
      // Required latency threshold the caller must provide.
      // The deterministic optimisation model knows how to apply it.
      "name": "latency",
      "description": "Maximum acceptable latency threshold.",
      "valueType": "number",
      "unit": "ms",
      "required": true
    },
    {
      // Required reliability threshold the caller must provide.
      // The deterministic optimisation model knows how to apply it.
      "name": "reliability",
      "description": "Minimum acceptable reliability threshold.",
      "valueType": "number",
      "unit": "percent",
      "required": true
    },
    {
      // Optional caller-provided topology snapshot reference.
      // The platform/model knows how to resolve and use it if supplied.
      "name": "topologySnapshot",
      "description": "Optional reference to the topology snapshot to use for optimisation.",
      "valueType": "object",
      "required": false
    },
    {
      // Optional caller-provided traffic forecast reference.
      // The platform/model knows how to resolve and use it if supplied.
      "name": "trafficForecast",
      "description": "Optional reference to the traffic forecast to use for optimisation.",
      "valueType": "object",
      "required": false
    }
  ],

  // HATEOAS controls vary by lifecycleStatus.
  "_links": {
    "self": {
      "href": "/optimisationSpecification/os-7f3a9c21",
      "method": "GET"
    },
    "createOptimisation": {
      "href": "/optimisation",
      "method": "POST"
    }
  }
}
```

## 6. POST /optimisationSpecification

Creates a new `OptimisationSpecification`.

OD MS generates:

```text
id
href
creationDate
lastUpdate
ETag
```

### Request

```http
POST /optimisationSpecification
Content-Type: application/json
```

```jsonc
{
  // Stable family/key shared by all versions of this optimisation capability.
  // OD MS uses this to enforce one ACTIVE version per capability family.
  "specificationKey": "hospital-surgical-slice-path-optimisation",

  // Human-readable capability name.
  // Caller does not send id; OD MS generates id/href.
  "name": "Hospital surgical slice path optimisation",

  // External description of what this optimisation capability does.
  // Do not expose Gurobi model internals here.
  "description": "Optimisation capability for hospital surgical slice path selection.",

  // Version of this externally visible optimisation capability contract.
  "version": "1.0",

  // New specifications normally start as DRAFT.
  // DRAFT can be edited. ACTIVE is immutable.
  "lifecycleStatus": "DRAFT",

  // Public caller-facing input contract only.
  // This tells external callers what they need to feed into POST /optimisation.
  "inputs": [
    {
      // Required latency threshold the caller must provide.
      "name": "latency",
      "description": "Maximum acceptable latency threshold.",
      "valueType": "number",
      "unit": "ms",
      "required": true
    },
    {
      // Required reliability threshold the caller must provide.
      "name": "reliability",
      "description": "Minimum acceptable reliability threshold.",
      "valueType": "number",
      "unit": "percent",
      "required": true
    },
    {
      // Optional caller-provided topology snapshot reference.
      "name": "topologySnapshot",
      "description": "Optional reference to the topology snapshot to use for optimisation.",
      "valueType": "object",
      "required": false
    },
    {
      // Optional caller-provided traffic forecast reference.
      "name": "trafficForecast",
      "description": "Optional reference to the traffic forecast to use for optimisation.",
      "valueType": "object",
      "required": false
    }
  ],

  // TMF-aligned typing.
  "type": "OptimisationSpecification",
  "baseType": "EntitySpecification",
  "schemaLocation": "/schema/OptimisationSpecification.schema.json"
}
```

### Successful response

```http
HTTP/1.1 201 Created
Location: /optimisationSpecification/os-7f3a9c21
ETag: "os-7f3a9c21-v1"
Content-Type: application/json
```

```jsonc
{
  // Server-generated identity.
  "id": "os-7f3a9c21",
  "href": "/optimisationSpecification/os-7f3a9c21",

  "specificationKey": "hospital-surgical-slice-path-optimisation",

  "type": "OptimisationSpecification",
  "baseType": "EntitySpecification",
  "schemaLocation": "/schema/OptimisationSpecification.schema.json",

  "name": "Hospital surgical slice path optimisation",
  "description": "Optimisation capability for hospital surgical slice path selection.",
  "version": "1.0",
  "lifecycleStatus": "DRAFT",

  // Server-owned timestamps.
  "creationDate": "2026-05-02T01:00:00Z",
  "lastUpdate": "2026-05-02T01:00:00Z",

  // Accepted public input contract.
  "inputs": [
    {
      "name": "latency",
      "description": "Maximum acceptable latency threshold.",
      "valueType": "number",
      "unit": "ms",
      "required": true
    },
    {
      "name": "reliability",
      "description": "Minimum acceptable reliability threshold.",
      "valueType": "number",
      "unit": "percent",
      "required": true
    },
    {
      "name": "topologySnapshot",
      "description": "Optional reference to the topology snapshot to use for optimisation.",
      "valueType": "object",
      "required": false
    },
    {
      "name": "trafficForecast",
      "description": "Optional reference to the traffic forecast to use for optimisation.",
      "valueType": "object",
      "required": false
    }
  ],

  // DRAFT state exposes replace and delete.
  "_links": {
    "self": {
      "href": "/optimisationSpecification/os-7f3a9c21",
      "method": "GET"
    },
    "replace": {
      "href": "/optimisationSpecification/os-7f3a9c21",
      "method": "PUT"
    },
    "delete": {
      "href": "/optimisationSpecification/os-7f3a9c21",
      "method": "DELETE"
    }
  }
}
```

## 7. GET /optimisationSpecification/{id}

Retrieves one `OptimisationSpecification`.

### Request

```http
# Client may send Cache-Control: no-cache when it wants to bypass/revalidate cache.
# No If-None-Match in the active baseline.
GET /optimisationSpecification/os-7f3a9c21
Cache-Control: no-cache
```

### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "os-7f3a9c21-v3"
Cache-Control: max-age=3600
```

```jsonc
{
  // Server-generated identity.
  "id": "os-7f3a9c21",
  "href": "/optimisationSpecification/os-7f3a9c21",

  "specificationKey": "hospital-surgical-slice-path-optimisation",

  "type": "OptimisationSpecification",
  "baseType": "EntitySpecification",
  "schemaLocation": "/schema/OptimisationSpecification.schema.json",

  "name": "Hospital surgical slice path optimisation",
  "description": "Optimisation capability for hospital surgical slice path selection.",
  "version": "1.0",

  // ACTIVE specs can be used by OC MS to create runtime Optimisation resources.
  "lifecycleStatus": "ACTIVE",

  "creationDate": "2026-05-02T01:00:00Z",
  "lastUpdate": "2026-05-02T02:00:00Z",

  "inputs": [
    {
      // Required latency threshold the caller must provide.
      "name": "latency",
      "description": "Maximum acceptable latency threshold.",
      "valueType": "number",
      "unit": "ms",
      "required": true
    },
    {
      // Required reliability threshold the caller must provide.
      "name": "reliability",
      "description": "Minimum acceptable reliability threshold.",
      "valueType": "number",
      "unit": "percent",
      "required": true
    },
    {
      // Optional caller-provided topology snapshot reference.
      "name": "topologySnapshot",
      "description": "Optional reference to the topology snapshot to use for optimisation.",
      "valueType": "object",
      "required": false
    },
    {
      // Optional caller-provided traffic forecast reference.
      "name": "trafficForecast",
      "description": "Optional reference to the traffic forecast to use for optimisation.",
      "valueType": "object",
      "required": false
    }
  ],

  // ACTIVE exposes createOptimisation.
  // ACTIVE does not expose replace/delete because ACTIVE specifications are immutable.
  "_links": {
    "self": {
      "href": "/optimisationSpecification/os-7f3a9c21",
      "method": "GET"
    },
    "createOptimisation": {
      "href": "/optimisation",
      "method": "POST"
    }
  }
}
```

## 8. GET /optimisationSpecification

Lists/searches `OptimisationSpecification` resources.

List response is summary-only by default. Caller follows `self` to get the full input contract.

### Request

```http
# Client may use Cache-Control: no-cache when it wants to bypass/revalidate cache.
GET /optimisationSpecification?lifecycleStatus=ACTIVE&offset=0&limit=20
Cache-Control: no-cache
```

### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=3600
X-Total-Count: 1
X-Result-Count: 1
```

```jsonc
[
  {
    // Summary item only.
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",

    "specificationKey": "hospital-surgical-slice-path-optimisation",

    "type": "OptimisationSpecification",
    "baseType": "EntitySpecification",
    "schemaLocation": "/schema/OptimisationSpecification.schema.json",

    "name": "Hospital surgical slice path optimisation",
    "description": "Optimisation capability for hospital surgical slice path selection.",
    "version": "1.0",
    "lifecycleStatus": "ACTIVE",

    "creationDate": "2026-05-02T01:00:00Z",
    "lastUpdate": "2026-05-02T02:00:00Z",

    // Client follows self to retrieve the full input contract.
    "_links": {
      "self": {
        "href": "/optimisationSpecification/os-7f3a9c21",
        "method": "GET"
      },
      "createOptimisation": {
        "href": "/optimisation",
        "method": "POST"
      }
    }
  }
]
```

## 9. PUT /optimisationSpecification/{id}

Full replacement only.

Allowed only when current lifecycle state is `DRAFT`.

Can also promote `DRAFT -> ACTIVE`.

### Request

```http
PUT /optimisationSpecification/os-7f3a9c21
If-Match: "os-7f3a9c21-v1"
Content-Type: application/json
```

```jsonc
{
  // Full replacement of the DRAFT specification.
  // No id/href in request body; id comes from the path.
  "specificationKey": "hospital-surgical-slice-path-optimisation",

  "name": "Hospital surgical slice path optimisation",
  "description": "Optimisation capability for hospital surgical slice path selection.",
  "version": "1.0",

  // PUT may promote DRAFT to ACTIVE.
  // Once ACTIVE, future PUT/DELETE is not allowed.
  // When promoted to ACTIVE, OD MS retires the previous ACTIVE version
  // with the same specificationKey in the same transaction.
  "lifecycleStatus": "ACTIVE",

  "inputs": [
    {
      "name": "latency",
      "description": "Maximum acceptable latency threshold.",
      "valueType": "number",
      "unit": "ms",
      "required": true
    },
    {
      "name": "reliability",
      "description": "Minimum acceptable reliability threshold.",
      "valueType": "number",
      "unit": "percent",
      "required": true
    },
    {
      "name": "topologySnapshot",
      "description": "Optional reference to the topology snapshot to use for optimisation.",
      "valueType": "object",
      "required": false
    },
    {
      "name": "trafficForecast",
      "description": "Optional reference to the traffic forecast to use for optimisation.",
      "valueType": "object",
      "required": false
    }
  ],

  "type": "OptimisationSpecification",
  "baseType": "EntitySpecification",
  "schemaLocation": "/schema/OptimisationSpecification.schema.json"
}
```

### Successful response

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "os-7f3a9c21-v2"
Cache-Control: max-age=3600
```

```jsonc
{
  "id": "os-7f3a9c21",
  "href": "/optimisationSpecification/os-7f3a9c21",

  "specificationKey": "hospital-surgical-slice-path-optimisation",

  "type": "OptimisationSpecification",
  "baseType": "EntitySpecification",
  "schemaLocation": "/schema/OptimisationSpecification.schema.json",

  "name": "Hospital surgical slice path optimisation",
  "description": "Optimisation capability for hospital surgical slice path selection.",
  "version": "1.0",
  "lifecycleStatus": "ACTIVE",

  "creationDate": "2026-05-02T01:00:00Z",
  "lastUpdate": "2026-05-02T02:30:00Z",

  "inputs": [
    {
      "name": "latency",
      "description": "Maximum acceptable latency threshold.",
      "valueType": "number",
      "unit": "ms",
      "required": true
    },
    {
      "name": "reliability",
      "description": "Minimum acceptable reliability threshold.",
      "valueType": "number",
      "unit": "percent",
      "required": true
    },
    {
      "name": "topologySnapshot",
      "description": "Optional reference to the topology snapshot to use for optimisation.",
      "valueType": "object",
      "required": false
    },
    {
      "name": "trafficForecast",
      "description": "Optional reference to the traffic forecast to use for optimisation.",
      "valueType": "object",
      "required": false
    }
  ],

  // ACTIVE exposes createOptimisation only.
  "_links": {
    "self": {
      "href": "/optimisationSpecification/os-7f3a9c21",
      "method": "GET"
    },
    "createOptimisation": {
      "href": "/optimisation",
      "method": "POST"
    }
  }
}
```

### PUT failure responses

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
```

```jsonc
{
  // If-Match is mandatory for unsafe updates.
  "code": "PRECONDITION_REQUIRED",
  "reason": "IF_MATCH_REQUIRED",
  "message": "If-Match header is required when updating an OptimisationSpecification.",
  "status": "428",
  "type": "Error"
}
```

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
```

```jsonc
{
  // Supplied ETag does not match the current resource version.
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied ETag does not match the current OptimisationSpecification version.",
  "status": "412",
  "type": "Error"
}
```

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```jsonc
{
  // ACTIVE and RETIRED specifications are immutable.
  "code": "CONFLICT",
  "reason": "SPECIFICATION_IMMUTABLE",
  "message": "Only DRAFT OptimisationSpecification resources can be updated.",
  "status": "409",
  "type": "Error"
}
```

## 10. DELETE /optimisationSpecification/{id}

Delete is only for DRAFT cleanup.

### Request

```http
DELETE /optimisationSpecification/os-7f3a9c21
If-Match: "os-7f3a9c21-v1"
```

### Successful response

```http
HTTP/1.1 204 No Content
```

### DELETE rules

```text
DELETE /optimisationSpecification/{id}
  Requires If-Match.
  Allowed only when lifecycleStatus is DRAFT.
  Removes a draft specification that has not become ACTIVE.
  Not allowed for ACTIVE.
  Not allowed for RETIRED.
```

### DELETE failure responses

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
```

```jsonc
{
  // If-Match is mandatory for unsafe delete operations.
  "code": "PRECONDITION_REQUIRED",
  "reason": "IF_MATCH_REQUIRED",
  "message": "If-Match header is required when deleting an OptimisationSpecification.",
  "status": "428",
  "type": "Error"
}
```

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
```

```jsonc
{
  // Supplied ETag does not match the current resource version.
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied ETag does not match the current OptimisationSpecification version.",
  "status": "412",
  "type": "Error"
}
```

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```jsonc
{
  // ACTIVE and RETIRED specifications are retained for governance and audit.
  "code": "CONFLICT",
  "reason": "SPECIFICATION_IMMUTABLE",
  "message": "Only DRAFT OptimisationSpecification resources can be deleted.",
  "status": "409",
  "type": "Error"
}
```

## 11. HATEOAS by lifecycle state

### DRAFT

```jsonc
"_links": {
  "self": {
    "href": "/optimisationSpecification/os-7f3a9c21",
    "method": "GET"
  },
  "replace": {
    "href": "/optimisationSpecification/os-7f3a9c21",
    "method": "PUT"
  },
  "delete": {
    "href": "/optimisationSpecification/os-7f3a9c21",
    "method": "DELETE"
  }
}
```

### ACTIVE

```jsonc
"_links": {
  "self": {
    "href": "/optimisationSpecification/os-7f3a9c21",
    "method": "GET"
  },
  "createOptimisation": {
    "href": "/optimisation",
    "method": "POST"
  }
}
```

### RETIRED

```jsonc
"_links": {
  "self": {
    "href": "/optimisationSpecification/os-7f3a9c21",
    "method": "GET"
  }
}
```

## 12. Header rules

```text
GET /optimisationSpecification/{id}
  Response:
    ETag required
    Cache-Control: max-age=3600

GET /optimisationSpecification
  Response:
    Cache-Control: max-age=3600
    X-Total-Count and X-Result-Count for pagination

GET request cache bypass:
  Client may send Cache-Control: no-cache

No If-None-Match in the active baseline.

ETag is used for unsafe concurrency only:
  PUT /optimisationSpecification/{id}
  DELETE /optimisationSpecification/{id}
  POST /optimisation/{id}/cancel
  POST /optimisation/{id}/retry

Missing If-Match on unsafe operation:
  428 Precondition Required

Stale/wrong If-Match:
  412 Precondition Failed
```

## 13. Key OD MS baseline summary

```text
OD MS owns OptimisationSpecification.

OptimisationSpecification is a public capability/input contract, not a public Gurobi model definition.

Expose only:
  id
  href
  specificationKey
  type
  baseType
  schemaLocation
  name
  description
  version
  lifecycleStatus
  creationDate
  lastUpdate
  inputs
  _links

Do not expose by default:
  supportedInputModes
  allowedObjectives
  candidateResourceRules
  solverConfiguration
  modelBinding
  resultSchema
  inputType
  sourceType
  operator
  inputTypeVocabulary
  operatorVocabulary

POST uses server-generated IDs only.

Use lifecycleStatus:
  DRAFT
  ACTIVE
  RETIRED

Only DRAFT specifications are editable/deletable.

ACTIVE specifications are immutable.

When a DRAFT version is promoted to ACTIVE:
  previous ACTIVE version with the same specificationKey is moved to RETIRED.

Only one ACTIVE specification is allowed per specificationKey.

RETIRED specifications are retained for audit/history and existing Optimisation references.

No DELETED or ARCHIVED lifecycle status in the active baseline.
```

---

## Baseline appended 2026-05-02T04:29:57 - Runtime Optimisation result visibility rule

For the optimisation architecture exercise, runtime `Optimisation` resources do not expose `result: null` or `resultPending`.

Use `lifecycleStatus` to indicate progress.

Result visibility rule:

```text
If lifecycleStatus is ACKNOWLEDGED, QUEUED, PROCESSING, or CANCELLING:
  result is omitted.

If lifecycleStatus is COMPLETED, INFEASIBLE, or FAILED:
  result/outcome details may be included.

If lifecycleStatus is CANCELLED:
  result is omitted, but cancellation/status reason may be included if useful.
```

Rationale:

```text
The lifecycle state already tells the caller whether the optimisation is pending, running, completed, infeasible, failed, cancelling, or cancelled.

Do not duplicate that state with result:null or resultPending:true.
```

Example active state:

```jsonc
{
  // Runtime lifecycle tells the caller the optimisation is still in progress.
  "lifecycleStatus": "PROCESSING",

  // No result field is included until a worker outcome exists.
  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    },
    "cancel": {
      "href": "/optimisation/opt-12345/cancel",
      "method": "POST"
    }
  }
}
```

---

## Baseline appended 2026-05-03T07:55:57 - Rebuilt OD MS specification as clean definition model

Rebuilt OD MS specification to remove runtime request-instance drift.

Validation intent:
- OD MS contains `constraintSpecifications[]`, `targetSpecifications[]`, and `contextSpecifications[]`.
- OD MS does not contain runtime `constraints[]`, `targets[]`, or `context[]` instance sections.
- OD MS does not contain actual candidate IDs such as path-001/path-002.
- OD MS does not contain runtime request values such as `"value": 20` or `"value": 99.9`.
- OD MS defines candidate resource schema and minItems cardinality only.

---

## Baseline appended 2026-05-03T08:08:22 - Shared location moved to topologySnapshot level

Baselined the shared versus candidate-specific context rule.

Rule:
- Put shared context attributes at `context.topologySnapshot` level.
- Use `candidateResources[].resourceAttributes` only for attributes that vary per candidate.
- Do not repeat the same `locationId` under every candidate if all candidate paths belong to the same optimisation scope/location.

For the current examples:
- `location.locationId = melbourne-hospital` is placed at `topologySnapshot` level.
- Repeated candidate-level `resourceAttributes.locationId` blocks are removed from OC MS runtime examples.

---

## Baseline appended 2026-05-03T08:41:32 - Removed DEPRECATED from OD MS lifecycle

Confirmed the OD MS OptimisationSpecification lifecycle should not include `DEPRECATED` in the current baseline.

Active lifecycle model:
```text
DRAFT
ACTIVE
RETIRED
```

Meaning:
- `DRAFT`: editable.
- `ACTIVE`: usable by OC MS for runtime Optimisation creation and should be immutable except lifecycle metadata.
- `RETIRED`: not available for new runtime Optimisation creation.

Removed the previously shown `DEPRECATED` state and its wording:
```text
DEPRECATED:
  Existing runtime use may continue where already accepted.
  New runtime use should be prevented unless explicitly allowed by policy.
```
