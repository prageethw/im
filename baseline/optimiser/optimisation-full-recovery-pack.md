# Optimisation Full Recovery Pack

Generated: 2026-05-03T22:42:08

This file combines the current optimisation architecture recovery material into one place.

It contains:
- The cumulative baseline/context dump
- The current OD MS / Optimisation-Definition-MS specification
- The current OC MS / Optimisation-Controller-MS specification
- The current E2E optimisation solution brief

---

# Part 1: Cumulative Context Dump

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

## Baseline appended 2026-05-03T10:59:36 - Process views updated

Updated process views to match the agreed OEX/OGW/Screen Builder/NGW sequence and OD/OC responsibility split.

Common access path:
```text
User -> Microsoft Entra ID SSO -> OEX UI -> OEX APIs -> OGW -> OEX Screen Builder MS -> NGW
```

OD MS process path:
```text
... -> NGW -> OD MS
```

OC MS runtime process path:
```text
... -> NGW -> OC MS -> Kafka -> Python/Gurobi Worker -> Gurobi Optimizer
```

Process views now cover:
- capability discovery
- OptimisationSpecification create/activate
- runtime Optimisation create
- 422 contract validation failure
- SUCCESS
- INFEASIBLE
- FAILURE
- cancellation
- retrial
- late worker outcome after cancellation

---

## Baseline appended 2026-05-03T11:06:58 - Runtime process flow updated with OC DB outbox inbox

Baselined the runtime process flow as:

```text
Consumer / OEX
-> OGW
-> OEX APIs
-> OEX GW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OD MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
-> Kafka
-> OC MS Inbox
-> OC MS DB
-> Consumer polls GET /optimisation/{id}
```

Key corrections:
- Runtime flow starts from `Consumer / OEX`, not just generic user.
- Runtime flow includes `OGW -> OEX APIs -> OEX GW -> OEX Screen Builder MS -> NGW`.
- OC MS validates against OD MS before persisting the accepted runtime Optimisation.
- Runtime persistence is explicit through `OC MS DB`.
- Outbox pattern is explicit through `OC MS Outbox -> Kafka`.
- Worker execution is explicit through `Python/Gurobi Worker -> Gurobi Optimizer`.
- Outcome path returns through `Kafka -> OC MS Inbox -> OC MS DB`.
- Consumer observes outcome by polling `GET /optimisation/{id}`.

---

## Baseline appended 2026-05-03T11:20:21 - Reverted E2E sequence to agreed OEX/OGW path

Reconfirmed the agreed logical E2E sequence:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Runtime process expansion now follows the same front-door path and removes the previously introduced extra `OEX GW` hop:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OD MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
-> Kafka
-> OC MS Inbox
-> OC MS DB
-> User polls GET /optimisation/{id}
```

Correction:
- Use `User`, not `Consumer / OEX`, as the starting actor in this baseline.
- Use `OEX UI -> OEX APIs -> OGW -> OEX Screen Builder MS`.
- Do not include a separate `OEX GW` hop.

---

## Baseline appended 2026-05-03T22:42:08 - Re-added visible Manage optimisation catalogue use case

Confirmed and re-added the visible use case row in the E2E use case view:

```text
Manage optimisation catalogue
```

Also added the `Optimisation catalogue governance use case` section to make the use case visible outside the security section.


---

# Part 2: Current OD MS Specification

# OD MS / Optimisation-Definition-MS Specification:

## Service purpose:

Optimisation-Definition-MS / OD MS owns the governed catalogue of optimisation capabilities.

OD MS defines what optimisation requests are allowed to look like. It does not execute optimisation, does not hold runtime request values, and does not store actual candidate resources from a request.

OD MS is the definition/specification service. OC MS is the runtime execution/controller service.

## Ownership:

OD MS owns:

```text
OptimisationSpecification resource
Optimisation capability metadata
Request contract definition
Constraint specification definitions
Target specification definitions
Context specification definitions
Candidate resource schema
Candidate resource cardinality rules
Specification lifecycle
Specification versioning
Specification list/retrieve/create/update operations
```

OD MS does not own:

```text
Runtime Optimisation resources
Runtime constraints[] values
Runtime targets[] values
Runtime context[] values
Actual candidate resource instances
Candidate-resource selection
Solver feasibility evaluation
Gurobi model execution
Runtime optimisation outcome
```

## Definition versus runtime model:

OD MS uses specification/definition sections:

```text
constraintSpecifications[]:
  Defines allowed hard-constraint fields.
  Does not contain caller-supplied runtime values.

targetSpecifications[]:
  Defines allowed optimisation goals and default/allowed priority ordering.
  Does not contain runtime optimisation results.

contextSpecifications[]:
  Defines required context objects and their schemas.
  Defines candidate resource shape, cardinality, resourceAttributes, and metrics.
  Does not contain actual runtime candidate IDs.
```

OC MS uses runtime instance sections:

```text
constraints[]:
  Actual caller-supplied constraint values.

targets[]:
  Actual caller-supplied or defaulted target goals/priorities.

context[]:
  Actual caller-supplied context values, including candidateResources when embedded.
```

Validation mapping:

```text
OC MS runtime constraints[] -> OD MS constraintSpecifications[]
OC MS runtime targets[] -> OD MS targetSpecifications[]
OC MS runtime context[] -> OD MS contextSpecifications[]
```

## Endpoint set:

OD MS exposes:

```http
GET    /optimisationSpecification
POST   /optimisationSpecification
GET    /optimisationSpecification/{id}
PUT    /optimisationSpecification/{id}
PATCH  /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

OD MS does not expose runtime optimisation operations. Runtime operations belong to OC MS.

## OptimisationSpecification resource shape:

Canonical fields:

```text
id
href
name
description
version
lifecycleStatus
creationDate
lastUpdate
validFor
constraintSpecifications[]
targetSpecifications[]
contextSpecifications[]
_links
@type
@baseType
@schemaLocation
```

## Lifecycle model:

```text
DRAFT
ACTIVE
DEPRECATED
RETIRED
```

Rules:

```text
DRAFT:
  Editable.

ACTIVE:
  Can be used by OC MS for runtime Optimisation creation.
  Should be immutable except lifecycle transition metadata.

DEPRECATED:
  Existing runtime use may continue where already accepted.
  New runtime use should be prevented unless explicitly allowed by policy.

RETIRED:
  Not available for new runtime Optimisation creation.
```

## Canonical OptimisationSpecification example:

```json
{
  "id": "os-7f3a9c21",
  "href": "/optimisationSpecification/os-7f3a9c21",
  "name": "Hospital surgical slice path optimisation",
  "description": "Defines the request contract for hospital surgical slice path selection optimisation.",
  "version": "1.0",
  "lifecycleStatus": "ACTIVE",
  "creationDate": "2026-05-02T01:00:00Z",
  "lastUpdate": "2026-05-02T02:00:00Z",
  "validFor": {
    "startDateTime": "2026-05-02T00:00:00Z"
  },
  "constraintSpecifications": [
    {
      "name": "maxLatency",
      "constraintType": "maximum",
      "ontologyPredicate": "icm:atMost",
      "valueType": "number",
      "required": true,
      "unit": "ms",
      "description": "Maximum allowed latency for a candidate resource."
    },
    {
      "name": "minReliability",
      "constraintType": "minimum",
      "ontologyPredicate": "icm:atLeast",
      "valueType": "number",
      "required": true,
      "unit": "percent",
      "description": "Minimum required reliability for a candidate resource."
    }
  ],
  "targetSpecifications": [
    {
      "name": "cost",
      "goal": "minimise",
      "required": true,
      "priority": 1,
      "description": "Primary optimisation target is to minimise cost among valid candidates."
    },
    {
      "name": "latency",
      "goal": "minimise",
      "required": false,
      "priority": 2,
      "description": "Secondary optimisation target is to minimise latency among valid candidates."
    },
    {
      "name": "reliability",
      "goal": "maximise",
      "required": false,
      "priority": 3,
      "description": "Tertiary optimisation target is to maximise reliability among valid candidates."
    }
  ],
  "contextSpecifications": [
    {
      "name": "topologySnapshot",
      "valueType": "object",
      "required": true,
      "description": "Topology snapshot containing or referencing the candidate resource set available for optimisation.",
      "schema": {
        "type": "object",
        "required": [
          "dataset",
          "version",
          "candidateResourceSetId",
          "candidateResources"
        ],
        "properties": {
          "dataset": {
            "type": "string"
          },
          "version": {
            "type": "string"
          },
          "candidateResourceSetId": {
            "type": "string"
          },
          "candidateResources": {
            "type": "array",
            "minItems": 2,
            "description": "Candidate resources available to the optimiser. At least two candidate options are required for resource/path/option-selection optimisation unless the capability is explicitly feasibility-validation-only.",
            "items": {
              "type": "object",
              "required": [
                "resourceId",
                "resourceType",
                "metrics"
              ],
              "properties": {
                "resourceId": {
                  "type": "string"
                },
                "resourceType": {
                  "type": "string"
                },
                "resourceClass": {
                  "type": "string"
                },
                "resourceAttributes": {
                  "type": "object",
                  "description": "Stable descriptive properties of the resource, such as locationId or pathClass."
                },
                "metrics": {
                  "type": "array",
                  "description": "Measured or computed values used for evaluation/optimisation, such as latency, reliability, cost, or utilisation.",
                  "items": {
                    "type": "object",
                    "required": [
                      "name",
                      "value"
                    ],
                    "properties": {
                      "name": {
                        "type": "string"
                      },
                      "value": {},
                      "unit": {
                        "type": "string"
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  ],
  "_links": {
    "self": {
      "href": "/optimisationSpecification/os-7f3a9c21",
      "method": "GET"
    },
    "createOptimisation": {
      "href": "/optimisation",
      "method": "POST"
    }
  },
  "@type": "OptimisationSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "/schema/OptimisationSpecification.schema.json"
}
```

## TMF/TIO alignment:

Upper-bound constraints use platform-readable contract fields with TMF/TIO traceability:

```json
{
  "name": "maxLatency",
  "constraintType": "maximum",
  "ontologyPredicate": "icm:atMost",
  "valueType": "number",
  "required": true,
  "unit": "ms"
}
```

Lower-bound constraints use the same pattern:

```json
{
  "name": "minReliability",
  "constraintType": "minimum",
  "ontologyPredicate": "icm:atLeast",
  "valueType": "number",
  "required": true,
  "unit": "percent"
}
```

Do not use a platform contract field named `operator` for these upper/lower bound constraints.

## Contract validation rules:

OC MS validates runtime Optimisation requests against the ACTIVE OptimisationSpecification.

OC MS validates:

```text
required fields
value types
supported constraint names
supported target names
supported context names
constraintType values
target goal values
context object schema
cardinality rules such as candidateResources minItems = 2
```

OC MS does not validate:

```text
solver feasibility
candidate ranking
metric-vs-constraint fit
objective trade-off evaluation
best-candidate selection
```

## Contract violation response:

Use `422 Unprocessable Entity` when the JSON is structurally valid but violates the ACTIVE OptimisationSpecification request contract.

Example:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_CONTRACT_VIOLATION",
  "reason": "Optimisation request violates specification contract",
  "message": "topologySnapshot.candidateResources must contain at least 2 candidate resources for this optimisation capability.",
  "status": 422,
  "@type": "Error"
}
```

## Relationship to OC MS:

```text
OD MS:
  defines what is allowed.

OC MS:
  stores what was accepted at runtime.

Worker/model:
  decides feasibility and returns SUCCESS, INFEASIBLE, or FAILURE.
```

## Baseline validation note:

This OD MS specification intentionally does not include actual runtime candidate resources such as path identifiers, candidate metric values, selected resources, or runtime constraint values. Those belong in OC MS runtime Optimisation examples.

---

## Process view baseline:

OD MS participates in definition/specification processes only.

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OD MS
```

OD MS process responsibilities:
```text
create OptimisationSpecification
validate definition shape
store as DRAFT
activate as ACTIVE
serve ACTIVE definitions to OC MS and authorised consumers
```

OD MS does not participate in Kafka execution, Python/Gurobi Worker processing, Gurobi Optimizer execution, runtime cancellation, runtime retrial, or runtime outcome projection.

---

## Logical and process access baseline:

OD MS definition-management path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OD MS
```

OD MS also participates in OC MS runtime validation as the OptimisationSpecification definition source:

```text
OC MS -> OD MS
```

OD MS does not participate in Kafka, Python/Gurobi Worker, Gurobi Optimizer, OC MS Inbox, or runtime result projection.


---

# Part 3: Current OC MS Specification

# Optimisation-Controller-MS / OC MS Specification

## OC MS summary:

**Optimisation-Controller-MS (OC MS)** owns the runtime `Optimisation` resource. It is a generic optimisation controller, not an intent-only controller.

```text
OC MS owns:
  Runtime Optimisation resource
  Runtime lifecycle
  Syntactic and OD-MS-contract validation
  OC MS outbox write
  Publishing worker instruction events to t7.optimisation.events
  Inbox consumption of worker outcome events
  Runtime result projection

OC MS does not own:
  OptimisationSpecification definitions
  Gurobi model formulation
  Python/Gurobi solver execution
  Analytics platform datasets
```

OC MS accepts runtime optimisation requests, validates only the wrapper and OD MS request contract, persists the request, emits a worker instruction event, then later projects worker outcomes back into the runtime resource.

## OC MS endpoint set:

```http
# List/search runtime Optimisation resources.
GET /optimisation

# Create a runtime Optimisation.
POST /optimisation

# Retrieve runtime Optimisation state/result.
GET /optimisation/{id}

# Request cancellation of an active runtime Optimisation.
POST /optimisation/{id}/cancellation

# Retrial a failed runtime Optimisation by creating a new linked Optimisation.
POST /optimisation/{id}/retrial
```

Not supported:

```http
PUT /optimisation/{id}
DELETE /optimisation/{id}
```

Runtime `Optimisation` is an execution/audit record, not an editable draft definition.

## Runtime lifecycle:

```text
ACKNOWLEDGED
QUEUED
PROCESSING
COMPLETED
INFEASIBLE
FAILED
CANCELLING
CANCELLED
```

```text
ACKNOWLEDGED:
  OC MS accepted the request, persisted the Optimisation resource, and wrote the outbox event.

QUEUED:
  OptimisationRequestedEvent has been published or is waiting for worker processing.

PROCESSING:
  Python/Gurobi worker has started processing.

COMPLETED:
  Worker completed successfully and produced a usable result.

INFEASIBLE:
  Worker completed correctly, but no valid solution exists.

FAILED:
  Technical/runtime failure occurred.

CANCELLING:
  Cancellation command has been accepted and worker should stop/ignore where safely possible.

CANCELLED:
  Optimisation is confirmed cancelled.
```

Runtime `Optimisation` does **not** expose a `version` field. ETag is used in HTTP headers for unsafe concurrency.

## Lifecycle transitions:

```text
ACKNOWLEDGED -> QUEUED
QUEUED -> PROCESSING

PROCESSING -> COMPLETED
PROCESSING -> INFEASIBLE
PROCESSING -> FAILED

ACKNOWLEDGED -> CANCELLING -> CANCELLED
QUEUED -> CANCELLING -> CANCELLED
PROCESSING -> CANCELLING -> CANCELLED

FAILED -> retrial creates a new Optimisation

COMPLETED -> terminal
INFEASIBLE -> terminal by default
CANCELLED -> terminal
```

## HATEOAS by lifecycle:

```text
ACKNOWLEDGED / QUEUED / PROCESSING:
  self
  cancellation

CANCELLING:
  self

FAILED:
  self
  retrial

COMPLETED / INFEASIBLE / CANCELLED:
  self
```

## POST /optimisation:

```http
POST /optimisation
Content-Type: application/json
```

```jsonc
{
  // Optional source context.
  // Intent is only one possible source context.
  "sourceContext": {
    "domain": "intent-management",
    "resource": {
      "id": "intent-789",
      "href": "/intentManagement/v5/intent/intent-789",
      "@type": "IntentRef",
      "@referredType": "Intent"
    }
  },

  // Required ACTIVE OptimisationSpecification from OD MS.
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice intent.",
  "priority": "1",

  // Capability-specific caller-fed constraints, targets, and context.
  // Validated syntactically against OD MS OptimisationSpecification.constraints, targets, and context.
  "constraints": [
    {
      "name": "maxLatency",
      "constraintType": "maximum",
      "ontologyPredicate": "icm:atMost",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "minReliability",
      "constraintType": "minimum",
      "ontologyPredicate": "icm:atLeast",
      "valueType": "number",
      "value": 99.9,
      "unit": "percent"
    }
  ],
    "targets": [
      {
        "name": "cost",
        "goal": "minimise",
        "priority": 1
      },
      {
        "name": "latency",
        "goal": "minimise",
        "priority": 2
      },
      {
        "name": "reliability",
        "goal": "maximise",
        "priority": 3
      }
    ],
    "context": [
      {
        "name": "topologySnapshot",
        "valueType": "object",
        "value": {
          "dataset": "topology-snapshot",
          "version": "2026-05-02T10:00:00Z",
          "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z",
          "candidateResources": [
            {
              "resourceId": "path-001",
              "resourceType": "deliveryResource",
              "resourceClass": "low-latency-path",
              "resourceAttributes": {
                "locationId": "melbourne-hospital"
              },
              "metrics": [
                {
                  "name": "latency",
                  "value": 18,
                  "unit": "ms"
                },
                {
                  "name": "reliability",
                  "value": 99.95,
                  "unit": "percent"
                },
                {
                  "name": "cost",
                  "value": 70,
                  "unit": "costUnit"
                }
              ]
            },
            {
              "resourceId": "path-002",
              "resourceType": "deliveryResource",
              "resourceClass": "high-reliability-path",
              "resourceAttributes": {
                "locationId": "melbourne-hospital"
              },
              "metrics": [
                {
                  "name": "latency",
                  "value": 24,
                  "unit": "ms"
                },
                {
                  "name": "reliability",
                  "value": 99.995,
                  "unit": "percent"
                },
                {
                  "name": "cost",
                  "value": 90,
                  "unit": "costUnit"
                }
              ]
            }
          ]
        }
      }
    ]

  // TMF-aligned REST resource typing.
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json"
}
```

Successful response:

```http
HTTP/1.1 202 Accepted
Location: /optimisation/opt-12345
ETag: "opt-12345-rev1"
Content-Type: application/json
```

```jsonc
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",

  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  "sourceContext": {
    "domain": "intent-management",
    "resource": {
      "id": "intent-789",
      "href": "/intentManagement/v5/intent/intent-789",
      "@type": "IntentRef",
      "@referredType": "Intent"
    }
  },

  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice intent.",
  "priority": "1",

  "lifecycleStatus": "ACKNOWLEDGED",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:00:00Z",
  "statusChangeDate": "2026-05-02T03:00:00Z",

  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  "constraints": [
    {
      "name": "maxLatency",
      "constraintType": "maximum",
      "ontologyPredicate": "icm:atMost",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "minReliability",
      "constraintType": "minimum",
      "ontologyPredicate": "icm:atLeast",
      "valueType": "number",
      "value": 99.9,
      "unit": "percent"
    }
  ],
    "targets": [
      {
        "name": "cost",
        "goal": "minimise",
        "priority": 1
      },
      {
        "name": "latency",
        "goal": "minimise",
        "priority": 2
      },
      {
        "name": "reliability",
        "goal": "maximise",
        "priority": 3
      }
    ],
    "context": [
      {
        "name": "topologySnapshot",
        "valueType": "object",
        "value": {
          "dataset": "topology-snapshot",
          "version": "2026-05-02T10:00:00Z",
          "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z",
          "candidateResources": [
            {
              "resourceId": "path-001",
              "resourceType": "deliveryResource",
              "resourceClass": "low-latency-path",
              "resourceAttributes": {
                "locationId": "melbourne-hospital"
              },
              "metrics": [
                {
                  "name": "latency",
                  "value": 18,
                  "unit": "ms"
                },
                {
                  "name": "reliability",
                  "value": 99.95,
                  "unit": "percent"
                },
                {
                  "name": "cost",
                  "value": 70,
                  "unit": "costUnit"
                }
              ]
            },
            {
              "resourceId": "path-002",
              "resourceType": "deliveryResource",
              "resourceClass": "high-reliability-path",
              "resourceAttributes": {
                "locationId": "melbourne-hospital"
              },
              "metrics": [
                {
                  "name": "latency",
                  "value": 24,
                  "unit": "ms"
                },
                {
                  "name": "reliability",
                  "value": 99.995,
                  "unit": "percent"
                },
                {
                  "name": "cost",
                  "value": 90,
                  "unit": "costUnit"
                }
              ]
            }
          ]
        }
      }
    ]

  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    },
    "cancellation": {
      "href": "/optimisation/opt-12345/cancellation",
      "method": "POST"
    }
  }
}
```

`202 Accepted` means OC MS accepted the request for asynchronous execution. It does not mean the optimisation is feasible, started, solvable, or guaranteed to produce a valid result.

## OC MS validation boundary:

```text
OC MS validates:
  generic REST wrapper using its static API/OpenAPI contract
  referenced OptimisationSpecification exists in OD MS
  referenced OptimisationSpecification lifecycleStatus is ACTIVE
  constraints[], targets[], and context[] against the referenced ACTIVE OptimisationSpecification.constraints, targets, and context

OC MS does not validate:
  optimisation semantics
  solver feasibility
  candidate selection
  objective interpretation
  Gurobi model validity
  resource-selection correctness
```

After acceptance, OC MS persists the runtime resource and writes `OptimisationRequestedEvent` with `instruction = EXECUTE` to its outbox in the same transaction.

## GET /optimisation/{id}:

```http
GET /optimisation/opt-12345
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "opt-12345-rev2"
```

Active-state example:

```jsonc
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",

  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice intent.",
  "priority": "1",

  "lifecycleStatus": "PROCESSING",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:01:00Z",
  "statusChangeDate": "2026-05-02T03:01:00Z",

  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  "constraints": [
    {
      "name": "maxLatency",
      "constraintType": "maximum",
      "ontologyPredicate": "icm:atMost",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "minReliability",
      "constraintType": "minimum",
      "ontologyPredicate": "icm:atLeast",
      "valueType": "number",
      "value": 99.9,
      "unit": "percent"
    }
  ],
    "targets": [
      {
        "name": "cost",
        "goal": "minimise",
        "priority": 1
      },
      {
        "name": "latency",
        "goal": "minimise",
        "priority": 2
      },
      {
        "name": "reliability",
        "goal": "maximise",
        "priority": 3
      }
    ],
    "context": [
      {
        "name": "topologySnapshot",
        "valueType": "object",
        "value": {
          "dataset": "topology-snapshot",
          "version": "2026-05-02T10:00:00Z",
          "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z",
          "candidateResources": [
            {
              "resourceId": "path-001",
              "resourceType": "deliveryResource",
              "resourceClass": "low-latency-path",
              "resourceAttributes": {
                "locationId": "melbourne-hospital"
              },
              "metrics": [
                {
                  "name": "latency",
                  "value": 18,
                  "unit": "ms"
                },
                {
                  "name": "reliability",
                  "value": 99.95,
                  "unit": "percent"
                },
                {
                  "name": "cost",
                  "value": 70,
                  "unit": "costUnit"
                }
              ]
            },
            {
              "resourceId": "path-002",
              "resourceType": "deliveryResource",
              "resourceClass": "high-reliability-path",
              "resourceAttributes": {
                "locationId": "melbourne-hospital"
              },
              "metrics": [
                {
                  "name": "latency",
                  "value": 24,
                  "unit": "ms"
                },
                {
                  "name": "reliability",
                  "value": 99.995,
                  "unit": "percent"
                },
                {
                  "name": "cost",
                  "value": 90,
                  "unit": "costUnit"
                }
              ]
            }
          ]
        }
      }
    ]

  // No result field while lifecycleStatus is ACKNOWLEDGED, QUEUED, PROCESSING, or CANCELLING.
  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    },
    "cancellation": {
      "href": "/optimisation/opt-12345/cancellation",
      "method": "POST"
    }
  }
}
```

Completed-state example:

```jsonc
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",

  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  "lifecycleStatus": "COMPLETED",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:03:00Z",
  "statusChangeDate": "2026-05-02T03:03:00Z",

  "result": {
    "outcome": "SUCCESS",
    "summary": "Optimisation completed successfully.",
    "outputs": [
      {
        "name": "selectedResource",
        "valueType": "object",
        "value": {
          "resourceId": "path-001",
          "resourceType": "deliveryResource"
        }
      },
      {
        "name": "objectiveValue",
        "valueType": "number",
        "value": 70,
        "unit": "costUnit"
      }
    ]
  },

  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    }
  }
}
```

Rules:

```text
GET /optimisation/{id}:
  ETag required
  no response Cache-Control for runtime Optimisation for now
  no version field
  result omitted until worker outcome exists
  generic result.outputs[] when outcome exists
```

## GET /optimisation:

```http
GET /optimisation?lifecycleStatus=PROCESSING&offset=0&limit=20
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Total-Count: 52
X-Result-Count: 20
```

```jsonc
[
  {
    // Summary only. Follow self for full constraints/targets/context/result.
    "id": "opt-12345",
    "href": "/optimisation/opt-12345",

    "@type": "Optimisation",
    "@baseType": "Entity",
    "@schemaLocation": "/schema/Optimisation.schema.json",

    "name": "Hospital surgical slice path optimisation request",
    "description": "Optimise path selection for hospital surgical slice intent.",
    "priority": "1",

    "lifecycleStatus": "PROCESSING",
    "creationDate": "2026-05-02T03:00:00Z",
    "lastUpdate": "2026-05-02T03:01:00Z",
    "statusChangeDate": "2026-05-02T03:01:00Z",

    "optimisationSpecification": {
      "id": "os-7f3a9c21",
      "href": "/optimisationSpecification/os-7f3a9c21",
      "@type": "OptimisationSpecificationRef",
      "@referredType": "OptimisationSpecification"
    },

    "_links": {
      "self": {
        "href": "/optimisation/opt-12345",
        "method": "GET"
      },
      "cancellation": {
        "href": "/optimisation/opt-12345/cancellation",
        "method": "POST"
      }
    }
  }
]
```

Rules:

```text
GET /optimisation:
  summary-only by default
  no full constraints/targets/context by default
  no result by default
  no per-item ETag by default
  no response Cache-Control for runtime Optimisation for now
  includes X-Total-Count and X-Result-Count
```

Optional filters:

```text
lifecycleStatus
optimisationSpecificationId
sourceDomain
createdFrom
createdTo
offset
limit
```

## POST /optimisation/{id}/cancellation:

```http
POST /optimisation/opt-12345/cancellation
If-Match: "opt-12345-rev2"
Content-Type: application/json
```

```jsonc
{
  // Optional human-readable cancellation reason.
  "reason": "Caller no longer requires this optimisation."
}
```

Successful response:

```http
HTTP/1.1 202 Accepted
ETag: "opt-12345-rev3"
Content-Type: application/json
```

```jsonc
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",

  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  "lifecycleStatus": "CANCELLING",
  "statusReason": "Caller no longer requires this optimisation.",
  "lastUpdate": "2026-05-02T03:02:00Z",
  "statusChangeDate": "2026-05-02T03:02:00Z",

  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    }
  }
}
```

Allowed source states:

```text
ACKNOWLEDGED
QUEUED
PROCESSING
```

OC MS writes `OptimisationRequestedEvent` with `instruction = CANCEL` to its outbox in the same transaction.

## POST /optimisation/{id}/retrial:

```http
POST /optimisation/opt-12345/retrial
If-Match: "opt-12345-rev5"
Content-Type: application/json
```

```jsonc
{
  // Optional retrial reason for audit.
  "reason": "Retrial after temporary solver execution failure."
}
```

Successful response:

```http
HTTP/1.1 202 Accepted
Location: /optimisation/opt-67890
ETag: "opt-67890-rev1"
Content-Type: application/json
```

```jsonc
{
  "id": "opt-67890",
  "href": "/optimisation/opt-67890",

  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  "retrialOf": {
    "id": "opt-12345",
    "href": "/optimisation/opt-12345",
    "@type": "OptimisationRef",
    "@referredType": "Optimisation"
  },

  "statusReason": "Retrial after temporary solver execution failure.",

  "lifecycleStatus": "ACKNOWLEDGED",
  "creationDate": "2026-05-02T03:10:00Z",
  "lastUpdate": "2026-05-02T03:10:00Z",
  "statusChangeDate": "2026-05-02T03:10:00Z",

  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  "constraints": [
    {
      "name": "maxLatency",
      "constraintType": "maximum",
      "ontologyPredicate": "icm:atMost",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "minReliability",
      "constraintType": "minimum",
      "ontologyPredicate": "icm:atLeast",
      "valueType": "number",
      "value": 99.9,
      "unit": "percent"
    }
  ],
    "targets": [
      {
        "name": "cost",
        "goal": "minimise",
        "priority": 1
      },
      {
        "name": "latency",
        "goal": "minimise",
        "priority": 2
      },
      {
        "name": "reliability",
        "goal": "maximise",
        "priority": 3
      }
    ],
    "context": [
      {
        "name": "topologySnapshot",
        "valueType": "object",
        "value": {
          "dataset": "topology-snapshot",
          "version": "2026-05-02T10:00:00Z",
          "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z",
          "candidateResources": [
            {
              "resourceId": "path-001",
              "resourceType": "deliveryResource",
              "resourceClass": "low-latency-path",
              "resourceAttributes": {
                "locationId": "melbourne-hospital"
              },
              "metrics": [
                {
                  "name": "latency",
                  "value": 18,
                  "unit": "ms"
                },
                {
                  "name": "reliability",
                  "value": 99.95,
                  "unit": "percent"
                },
                {
                  "name": "cost",
                  "value": 70,
                  "unit": "costUnit"
                }
              ]
            },
            {
              "resourceId": "path-002",
              "resourceType": "deliveryResource",
              "resourceClass": "high-reliability-path",
              "resourceAttributes": {
                "locationId": "melbourne-hospital"
              },
              "metrics": [
                {
                  "name": "latency",
                  "value": 24,
                  "unit": "ms"
                },
                {
                  "name": "reliability",
                  "value": 99.995,
                  "unit": "percent"
                },
                {
                  "name": "cost",
                  "value": 90,
                  "unit": "costUnit"
                }
              ]
            }
          ]
        }
      }
    ]

  "_links": {
    "self": {
      "href": "/optimisation/opt-67890",
      "method": "GET"
    },
    "cancellation": {
      "href": "/optimisation/opt-67890/cancellation",
      "method": "POST"
    }
  }
}
```

Rules:

```text
Allowed source state:
  FAILED

Not allowed by default:
  COMPLETED
  INFEASIBLE
  CANCELLED
  CANCELLING
  ACKNOWLEDGED
  QUEUED
  PROCESSING
```

Retrial creates a **new** `Optimisation`; it does not mutate the failed one back into processing.

## Event model:

Use one topic:

```text
t7.optimisation.events
```

Worker request event:

```text
OptimisationRequestedEvent
```

Worker branches on:

```text
body.instruction
```

Initial instructions:

```text
EXECUTE
CANCEL
```

Do not use separate cancellation event types:

```text
OptimisationCancelRequestedEvent
OptimisationControlEvent
```

Outcome events:

```text
OptimisationCompletedEvent
OptimisationFailedEvent
```

## OptimisationRequestedEvent / EXECUTE:

Kafka headers:

```text
ce-specversion: 1.0
ce-id: evt-12345
ce-type: au.com.mycsp.optimisation.requested.v1
ce-source: optimisation-controller-ms
ce-time: 2026-05-02T03:00:00Z
ce-subject: optimisation/opt-12345
ce-datacontenttype: application/json
ce-correlationid: corr-12345
ce-eventversion: 1.0
content-type: application/json
```

Payload:

```jsonc
{
  "eventId": "evt-12345",
  "eventType": "OptimisationRequestedEvent",
  "eventVersion": "1.0",
  "source": "optimisation-controller-ms",
  "eventTime": "2026-05-02T03:00:00Z",
  "correlationId": "corr-12345",

  "body": {
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",
    "instruction": "EXECUTE",

    "optimisationSpecification": {
      "id": "os-7f3a9c21",
      "href": "/optimisationSpecification/os-7f3a9c21"
    },

    "constraints": [
    {
      "name": "maxLatency",
      "constraintType": "maximum",
      "ontologyPredicate": "icm:atMost",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "minReliability",
      "constraintType": "minimum",
      "ontologyPredicate": "icm:atLeast",
      "valueType": "number",
      "value": 99.9,
      "unit": "percent"
    }
  ],
      "targets": [
        {
          "name": "cost",
          "goal": "minimise",
          "priority": 1
        },
        {
          "name": "latency",
          "goal": "minimise",
          "priority": 2
        },
        {
          "name": "reliability",
          "goal": "maximise",
          "priority": 3
        }
      ],
      "context": [
        {
          "name": "topologySnapshot",
          "valueType": "object",
          "value": {
            "dataset": "topology-snapshot",
            "version": "2026-05-02T10:00:00Z",
            "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z"
          }
        }
      ]
  }
}
```

## OptimisationRequestedEvent / CANCEL:

Kafka headers:

```text
ce-specversion: 1.0
ce-id: evt-67890
ce-type: au.com.mycsp.optimisation.requested.v1
ce-source: optimisation-controller-ms
ce-time: 2026-05-02T03:02:00Z
ce-subject: optimisation/opt-12345
ce-datacontenttype: application/json
ce-correlationid: corr-12345
ce-eventversion: 1.0
content-type: application/json
```

Payload:

```jsonc
{
  "eventId": "evt-67890",
  "eventType": "OptimisationRequestedEvent",
  "eventVersion": "1.0",
  "source": "optimisation-controller-ms",
  "eventTime": "2026-05-02T03:02:00Z",
  "correlationId": "corr-12345",

  "body": {
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",
    "instruction": "CANCEL",
    "reason": "Caller no longer requires this optimisation."
  }
}
```

## Worker outcome events:

Outcome values:

```text
SUCCESS
INFEASIBLE
FAILURE
```

Mapping:

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```

No `solutionStatus` by default.

## OptimisationCompletedEvent / SUCCESS:

```jsonc
{
  "eventId": "evt-22345",
  "eventType": "OptimisationCompletedEvent",
  "eventVersion": "1.0",
  "source": "gurobi-worker",
  "eventTime": "2026-05-02T03:03:00Z",
  "correlationId": "corr-12345",

  "body": {
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",
    "outcome": "SUCCESS",
    "summary": "Optimisation completed successfully.",
    "completedAt": "2026-05-02T03:03:00Z",
    "outputs": [
      {
        "name": "selectedResource",
        "valueType": "object",
        "value": {
          "resourceId": "path-001",
          "resourceType": "deliveryResource"
        }
      }
    ]
  }
}
```

## OptimisationCompletedEvent / INFEASIBLE:

```jsonc
{
  "eventId": "evt-22346",
  "eventType": "OptimisationCompletedEvent",
  "eventVersion": "1.0",
  "source": "gurobi-worker",
  "eventTime": "2026-05-02T03:03:00Z",
  "correlationId": "corr-12345",

  "body": {
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",
    "outcome": "INFEASIBLE",
    "summary": "No feasible solution exists for the supplied constraints, targets, and context.",
    "completedAt": "2026-05-02T03:03:00Z"
  }
}
```

## OptimisationFailedEvent / FAILURE:

```jsonc
{
  "eventId": "evt-32345",
  "eventType": "OptimisationFailedEvent",
  "eventVersion": "1.0",
  "source": "gurobi-worker",
  "eventTime": "2026-05-02T03:03:00Z",
  "correlationId": "corr-12345",

  "body": {
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",
    "outcome": "FAILURE",
    "failureType": "SOLVER_EXECUTION_ERROR",
    "failureReason": "Gurobi solver execution failed before producing a result.",
    "failedAt": "2026-05-02T03:03:00Z"
  }
}
```

Late outcome rule:

```text
If OC MS has already moved the Optimisation to CANCELLING or CANCELLED:
  OC MS must not blindly apply a late SUCCESS, INFEASIBLE, or FAILURE outcome.
  It should handle the event idempotently as stale/late according to operational policy.
```

## Header/concurrency rules:

```text
POST /optimisation:
  returns Location and ETag

GET /optimisation/{id}:
  returns ETag
  no response Cache-Control for runtime resources for now

GET /optimisation:
  no per-item ETag by default
  includes X-Total-Count and X-Result-Count

POST /optimisation/{id}/cancellation:
  requires If-Match
  missing If-Match -> 428
  stale/wrong If-Match -> 412

POST /optimisation/{id}/retrial:
  requires If-Match
  missing If-Match -> 428
  stale/wrong If-Match -> 412
```

---

## TMF/TIO constraint representation baseline:

For upper-bound constraints in runtime Optimisation requests, responses, and worker instruction events, use:

```json
{
  "name": "maxLatency",
  "constraintType": "maximum",
  "ontologyPredicate": "icm:atMost",
  "valueType": "number",
  "value": 20,
  "unit": "ms"
}
```

Do not use a platform contract field named `operator` for this upper-bound constraint.

---

## OC MS happy and unhappy path validation/outcome baseline:

### Happy-path constraints:

The runtime Optimisation request should include both latency and reliability constraints in examples:

```json
"constraints": [
    {
      "name": "maxLatency",
      "constraintType": "maximum",
      "ontologyPredicate": "icm:atMost",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "minReliability",
      "constraintType": "minimum",
      "ontologyPredicate": "icm:atLeast",
      "valueType": "number",
      "value": 99.9,
      "unit": "percent"
    }
  ]
```

Happy-path rule:

```text
OC MS validates the request shape against the ACTIVE OptimisationSpecification.
This includes required fields, enum/value-type validation, and cardinality rules such as candidateResources minItems = 2.
OC MS does not evaluate which candidate wins.
```

### Unhappy-path contract violation example:

This request is structurally valid JSON, but violates the ACTIVE OptimisationSpecification request contract because `candidateResources` has only one candidate where `minItems = 2` is required for this selection optimisation.

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_CONTRACT_VIOLATION",
  "reason": "Optimisation request violates specification contract",
  "message": "topologySnapshot.candidateResources must contain at least 2 candidate resources for this optimisation capability.",
  "status": 422,
  "@type": "Error"
}
```

Rule:

```text
Cardinality failure is a request contract violation, not an optimisation outcome.

OC MS performs structural and request-contract validation, including cardinality checks such as candidateResources minItems = 2.

OC MS does not perform solver feasibility, candidate ranking, metric-vs-constraint evaluation, or objective trade-off evaluation.
```


### Unhappy-path optimiser outcome example:

This request satisfies the OD MS request contract shape and cardinality. It has at least two candidate resources, so OC MS accepts it and sends it to the worker/model. The worker/model may still return `INFEASIBLE` if no candidate satisfies the optimisation constraints.

```json
{
  "eventId": "evt-22346",
  "eventType": "OptimisationCompletedEvent",
  "eventVersion": "1.0",
  "source": "gurobi-worker",
  "eventTime": "2026-05-02T03:03:00Z",
  "correlationId": "corr-12345",
  "body": {
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",
    "outcome": "INFEASIBLE",
    "summary": "No feasible solution exists for the supplied constraints and context.",
    "completedAt": "2026-05-02T03:03:00Z"
  }
}
```

Rule:

```text
A valid request can still produce INFEASIBLE.

INFEASIBLE is an optimisation outcome produced by the worker/model.

It is not a request contract validation error.
```

---

## Runtime context versus specification contract clarification:

OD MS defines the allowed structure of `constraints[]`, `targets[]`, and `context[]`.

OC MS runtime requests and responses carry the actual accepted values for those sections.

Therefore:
```text
OD MS:
  defines the candidate resource schema, including candidateResources, resourceAttributes, and metrics.

OC MS:
  carries the actual candidateResources inside context.topologySnapshot.
  carries the actual constraints[] values supplied by the caller.
  validates structure/cardinality against OD MS.
  does not perform candidate ranking or metric-vs-constraint feasibility evaluation.
```

The presence of `constraints[]` in OC MS is expected. In OC MS it is not the definition; it is the runtime request instance.

---

## Logical and runtime process baseline:

OC MS runtime access path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OC MS
```

OC MS asynchronous execution path:

```text
OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
-> Kafka
-> OC MS Inbox
-> OC MS DB
```

User status/result retrieval:

```text
User polls GET /optimisation/{id}
```


---

## Corrected runtime process flow baseline:

The agreed runtime optimisation process flow is:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OD MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
-> Kafka
-> OC MS Inbox
-> OC MS DB
-> User polls GET /optimisation/{id}
```

Detailed interpretation:

```text
1. User authenticates through Microsoft Entra ID SSO and accesses OEX UI.
2. OEX UI calls OEX APIs.
3. OEX APIs route through OGW.
4. OGW routes to OEX Screen Builder MS.
5. OEX Screen Builder MS calls NGW.
6. NGW calls OC MS.
7. OC MS validates the runtime request against the ACTIVE OptimisationSpecification from OD MS.
8. OC MS persists the accepted runtime Optimisation in OC MS DB.
9. OC MS writes OptimisationRequestedEvent to OC MS Outbox in the same transaction.
10. OC MS Outbox relay publishes the event to Kafka.
11. Python/Gurobi Worker consumes the event from Kafka.
12. Python/Gurobi Worker invokes Gurobi Optimizer.
13. Worker publishes outcome event back to Kafka.
14. OC MS Inbox consumes the outcome event from Kafka.
15. OC MS Inbox updates OC MS DB with lifecycle/result projection.
16. User polls GET /optimisation/{id} through OEX UI -> OEX APIs -> OGW -> OEX Screen Builder MS -> NGW -> OC MS.
```

Outcome projection:

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```


---

# Part 4: Current E2E Optimisation Solution Brief

# End-to-End Solution Brief — Optimisation Platform

## 1. Business context:

The optimisation platform provides a reusable capability for running deterministic optimisation problems using Gurobi-backed models.

The platform is not limited to the intent-management domain. It is designed as a generic optimisation capability that can be used by OEX, platform services, planning tools, assurance functions, intent-management flows, and other authorised entities that need to run optimisation.

The business need is to allow authorised consumers to discover available optimisation capabilities, understand the required request contract, submit optimisation requests asynchronously, monitor execution state, cancellation active requests where needed, retrial failed requests, and retrieve final outcomes without exposing internal solver details or Gurobi model implementation.

The solution separates the **definition of optimisation capabilities** from the **execution and lifecycle control of optimisation runs**.

---

## 2. Solution summary:

- The solution provides a reusable, asynchronous optimisation platform backed by deterministic Gurobi models.

- It uses two core microservices:
  - **OD MS** owns `OptimisationSpecification` and exposes the caller-facing request contract.
  - **OC MS** owns runtime `Optimisation` lifecycle, cancellation, retrial, event integration, and result projection.

- Consumers may include **OEX**, platform services, planning tools, assurance functions, intent-management flows, or other authorised entities that need to run optimisation.

- Operator access to OEX is governed by the ACG approval process and Microsoft Entra ID SSO.

- OGW exposes OEX APIs for the OEX UI using user-context-aware OAuth2. OGW calls OEX Screen Builder MS using mTLS and User Context JWT. OEX Screen Builder MS reaches backend OD MS and OC MS APIs through NGW using mTLS and OAuth2 system-to-system.

- OC MS validates only request structure and the OD MS request contract, then returns `202 Accepted` and drives execution asynchronously through Kafka.

- Kafka carries worker instructions and outcomes, with a dedicated DLQ for unprocessable events.

- The Python/Gurobi worker consumes `EXECUTE` or `CANCEL` instructions, runs or cancels optimisation work, and returns `SUCCESS`, `INFEASIBLE`, or `FAILURE` outcomes.

- NGW-exposed backend APIs are TMF-compliant. OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.

---

## 3. Solution elaboration:

The solution is structured around a clean separation of responsibility.

OD MS acts as the governed catalogue of optimisation capabilities. It exposes only what callers need to know to submit valid optimisation requests. It does not expose Gurobi objectives, candidate resource rules, solver configuration, model bindings, or internal formulation details.

OC MS acts as the runtime controller. It accepts requests, validates the request shape and request contract, creates runtime optimisation resources, manages lifecycle state, publishes worker instructions, consumes worker outcomes, and projects final results.

The Python/Gurobi worker is responsible for executing the internal deterministic optimisation model. It consumes events from Kafka, executes or cancels work based on the instruction, and publishes outcome events back to Kafka.

### 3.1 Use case view:

| **Use case** | **Actor** | **Summary** | **Outcome** |
|---|---|---|---|
| Manage optimisation catalogue | Optimisation domain engineer | Create, update, activate, retire, and govern `OptimisationSpecification` records after agreement with broader E2E teams. This is an internal governed capability within the optimisation domain, not a general consumer capability. | Only approved optimisation domain engineers can define or change catalogue entries, and catalogue changes are governed before specifications become ACTIVE. |
| Discover optimisation capability | User / OEX / platform service | Retrieve available `OptimisationSpecification` records from OD MS and understand required constraints, targets, and context. | Caller knows which optimisation capability to use and the required request contract. |
| Create runtime optimisation | User / OEX / platform service | Submit a runtime `Optimisation` request to OC MS using an ACTIVE specification and valid constraints, targets, and context. | OC MS returns `202 Accepted` and creates an `ACKNOWLEDGED` optimisation. |
| Monitor optimisation | User / OEX / platform service | Read current lifecycle state and result when available. | Caller can see whether the optimisation is pending, processing, completed, infeasible, failed, cancelling, or cancelled. |
| Cancellation optimisation | User / OEX / platform service | Request cancellation for an eligible active optimisation. | OC MS moves the resource to `CANCELLING` and instructs the worker to cancellation where safely possible. |
| Retrial failed optimisation | User / OEX / platform service | Retrial a `FAILED` optimisation by creating a new linked optimisation. | A new `ACKNOWLEDGED` optimisation is created with `retrialOf` pointing to the failed one. |
| Execute optimisation | Python/Gurobi worker | Consume worker instruction and execute the deterministic optimisation model. | Worker emits `SUCCESS`, `INFEASIBLE`, or `FAILURE` outcome. |

### 3.2 Logical view:

The logical integration model is:

```text
User / Operator
-> Microsoft Entra ID SSO
-> OGW
-> OEX APIs / OEX UI
-> OEX Screen Builder MS
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Key logical relationships:

```text
User -> Microsoft Entra ID:
  User authenticates using SSO after ACG approval.

User / UI -> OGW:
  OGW acts as the user-context-aware gateway for OEX APIs.

OGW -> OEX APIs:
  Uses user SSO OAuth2 and propagates user context.

OGW -> OEX Screen Builder MS:
  Uses mTLS and User Context JWT.

OEX Screen Builder MS -> NGW:
  Uses mTLS and OAuth2 system-to-system.

NGW -> OD MS:
  Uses mTLS to expose OptimisationSpecification APIs.

NGW -> OC MS:
  Uses mTLS to expose runtime Optimisation APIs.

OC MS -> OD MS:
  Uses Istio mTLS for internal service-to-service validation.

OC MS -> Kafka:
  Emits OptimisationRequestedEvent with instruction EXECUTE or CANCEL.

Python/Gurobi Worker -> Kafka:
  Consumes worker instructions and emits optimisation outcomes.

OC MS <- Kafka:
  Consumes worker outcomes and projects lifecycle/result.
```

Logical diagram artifact:

```text
optimisation-logical-view.drawio
```

### 3.3 Process view:

#### 3.3.1 Create and execute optimisation:

```text
User
-> OGW
-> OEX APIs
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OD MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
-> Kafka
-> OC MS Inbox
-> OC MS DB
-> User polls GET /optimisation/{id}
```

Detailed flow:

```text
1. Consumer submits an optimisation request through the OEX experience or another authorised integration path.
2. User-facing access is handled through OGW and OEX APIs.
3. OGW invokes OEX Screen Builder MS with mTLS and User Context JWT.
4. OEX Screen Builder MS calls NGW using mTLS and OAuth2 system-to-system.
5. NGW routes the request to OC MS.
6. OC MS validates request structure.
7. OC MS calls OD MS over Istio mTLS to validate the referenced ACTIVE OptimisationSpecification.
8. OC MS validates constraints[], targets[], and context[] against the OD MS request contract.
9. OC MS persists runtime Optimisation with lifecycleStatus = ACKNOWLEDGED.
10. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE to outbox.
11. Outbox relay publishes event to Kafka.
12. Python/Gurobi worker consumes event.
13. Worker resolves internal deterministic model binding.
14. Worker runs Gurobi.
15. Worker publishes OptimisationCompletedEvent or OptimisationFailedEvent.
16. OC MS inbox consumes worker outcome.
17. OC MS updates lifecycle and result.
18. Consumer retrieves result through GET /optimisation/{id}.
```

#### 3.3.2 Cancellation optimisation:

```text
User
-> OGW
-> OEX APIs
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/cancellation with If-Match.
2. Request reaches OC MS through the authorised gateway path.
3. OC MS validates ETag.
4. OC MS checks lifecycleStatus is ACKNOWLEDGED, QUEUED, or PROCESSING.
5. OC MS updates lifecycleStatus to CANCELLING.
6. OC MS writes OptimisationRequestedEvent with instruction = CANCEL to outbox.
7. Outbox relay publishes event to Kafka.
8. Worker consumes CANCEL instruction.
9. Worker stops, cancels, or ignores work where safely possible.
10. OC MS eventually projects CANCELLED when cancellation is confirmed or safely resolved.
```

#### 3.3.3 Retrial failed optimisation:

```text
User
-> OGW
-> OEX APIs
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/retrial with If-Match.
2. Request reaches OC MS through the authorised gateway path.
3. OC MS validates original Optimisation lifecycleStatus = FAILED.
4. OC MS creates a new Optimisation resource.
5. New Optimisation links to the original through retrialOf.
6. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED.
7. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
8. Worker processes the new request.
```

---

## 4. Capability matrix:

| **Component** | **Responsibility** |
|---|---|
| **Microsoft Entra ID** | Provides SSO authentication for users/operators before they access OEX. Supplies identity context used by the user-facing access path. |
| **ACG approval process** | Governs operator access to OEX. Users must be approved through the organisational access-control process before they can use the OEX optimisation experience. |
| **OGW** | User-context-aware gateway for OEX APIs and OEX UI integration. Uses user SSO OAuth2 from the UI/OEX API path and propagates user identity context into the OEX layer. |
| **OEX APIs / OEX UI** | Provides the user/operator-facing experience for discovering optimisation capabilities, submitting requests, monitoring state, cancelling, retrying, and viewing results. |
| **OGW** | Secures internal OEX access to OEX Screen Builder MS using mTLS and User Context JWT. Preserves user context across the OEX backend interaction. |
| **OEX Screen Builder MS** | Builds and orchestrates the OEX screen/backend experience. Integrates with NGW using mTLS and OAuth2 system-to-system to call backend optimisation APIs. |
| **NGW** | NAAS Gateway exposing backend optimisation domain APIs for OD MS and OC MS. Provides the controlled backend API entry point for OEX Screen Builder MS and other authorised system consumers. NGW-exposed backend APIs are TMF-compliant. |
| **Optimisation-Definition-MS / OD MS** | Owns the definition side of the optimisation platform through `OptimisationSpecification`. Publishes caller-facing request contracts, manages `DRAFT`, `ACTIVE`, and `RETIRED` specification lifecycle, and ensures only one ACTIVE specification exists per `specificationKey`. Does not expose solver/model internals. |
| **OD MS Database** | Stores `OptimisationSpecification` records, version metadata, lifecycle state, request contracts, timestamps, ETag/revision data, and retained retired specifications for audit/history. |
| **Optimisation-Controller-MS / OC MS** | Owns runtime `Optimisation` resources. Accepts requests, validates the generic wrapper and OD MS request contract, manages lifecycle, cancellation, retrial, outbox/inbox integration, and result projection. Performs syntactic and contract validation only. |
| **OC MS Database** | Stores runtime `Optimisation` resources, accepted constraints, targets, and context, optional `sourceContext`, lifecycle state, status reasons, result projections, retrial links, timestamps, ETag/revision data, outbox records, and inbox records. |
| **OC MS Outbox Relay** | Publishes persisted OC MS outbox records to Kafka after DB commit. Publishes `OptimisationRequestedEvent` with `instruction = EXECUTE` or `instruction = CANCEL`. |
| **Kafka topic** | Main internal event stream for worker instructions and outcomes between OC MS and the Python/Gurobi worker. Uses CloudEvents-style Kafka headers. |
| **Kafka DLQ** | Holds events that cannot be safely processed after retrial handling. Preserves original event payload and failure metadata for operational investigation and replay decisions. |
| **Python / Gurobi Worker** | Consumes `OptimisationRequestedEvent`. For `EXECUTE`, resolves the internal deterministic model binding, resolves required data, executes optimisation, and emits an outcome. For `CANCEL`, cancels/stops/ignores processing where safely possible. |
| **Internal deterministic optimisation models** | Own solver-specific logic that is not exposed externally. Encapsulate objective formulation, constraints, candidate-resource rules, model binding, solver configuration, and Gurobi formulation. |
| **Gurobi Optimizer** | Executes the mathematical optimisation model prepared by the worker/model layer. Produces solve outcomes that the worker maps into `SUCCESS`, `INFEASIBLE`, or `FAILURE`. |
| **Analytics platform / data sources** | Provides authorised datasets required by the worker/model layer, such as topology snapshots, traffic forecasts, capacity information, inventory data, or other optimisation context datasets. |
| **OC MS Inbox Consumer** | Consumes worker outcome events, applies idempotency and stale/late-event handling, maps outcomes to lifecycle states, and projects result/failure details into the runtime `Optimisation` resource. |
| **Operational support / monitoring** | Monitors service health, Kafka lag, outbox/inbox processing, worker failures, solver failures, DLQ records, retrial counts, stale/late events, and optimisation lifecycle/result trends. |

---

## 5. Solution security:

### 5.1 User authentication and access governance:

Users/operators access the OEX experience through the organisational ACG approval process and SSO using Microsoft Entra ID.

```text
User / Operator
-> ACG approval process
-> Microsoft Entra ID SSO
-> OGW
-> OEX APIs / OEX UI
```

OGW is the user-context-aware gateway for the OEX channel. It uses user SSO OAuth2 from the UI/OEX API path and propagates user identity context into the OEX layer.

### 5.2 OEX internal access path:

OGW integrates with the OEX Screen Builder MS using:

```text
mTLS
User Context JWT
```

This preserves user context while securely invoking OEX backend experience services.

```text
OGW / OEX APIs
-> OEX Screen Builder MS
```

### 5.3 OEX to optimisation backend access:

OEX Screen Builder MS integrates with NGW using:

```text
mTLS
OAuth2 system-to-system
```

NGW exposes backend optimisation domain APIs for OD MS and OC MS.

```text
OEX Screen Builder MS
-> NGW
-> OD MS / OC MS
```

OD MS and OC MS are not directly exposed to end users or the UI layer.

### 5.4 NGW to OD MS / OC MS security:

NGW integrates with OD MS and OC MS using:

```text
mTLS
```

This secures backend API access from the gateway to the optimisation domain services.

### 5.5 OC MS to OD MS service-to-service security:

OC MS calls OD MS to validate referenced `OptimisationSpecification` resources. This internal service-to-service communication is secured using mTLS through Istio.

```text
OC MS
-> Istio mTLS
-> OD MS
```

OC MS uses this call to validate:

```text
OptimisationSpecification exists
OptimisationSpecification lifecycleStatus = ACTIVE
constraints[], targets[], and context[] match the OD MS request contract
```

### 5.6 Kafka security:

OC MS and the Python/Gurobi worker integrate through Kafka.

Recommended controls:

```text
TLS for broker connectivity
service identity for producers and consumers
topic-level ACLs
separate consumer groups
DLQ access restricted to operational support
```

Producer/consumer permissions:

```text
OC MS:
  produce worker instruction events
  consume worker outcome events
  produce DLQ records when needed

Python/Gurobi Worker:
  consume worker instruction events
  produce worker outcome events
  produce DLQ records when needed
```

### 5.7 API concurrency control:

ETags are used for unsafe runtime actions.

```text
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
```

Both require:

```text
If-Match
```

Failure rules:

```text
Missing If-Match -> 428 Precondition Required
Stale/wrong If-Match -> 412 Precondition Failed
```

Runtime `Optimisation` does not expose a `version` field. ETag is used only as the HTTP concurrency mechanism.

### 5.8 Event security and integrity:

Internal Kafka events use CloudEvents-style headers:

```text
ce-specversion
ce-id
ce-type
ce-source
ce-time
ce-subject
ce-datacontenttype
ce-correlationid
ce-eventversion
content-type
```

Kafka events do not use TMF REST fields such as:

```text
@type
@baseType
@schemaLocation
```

Those fields are reserved for public REST resource representations.

### 5.9 Sensitive information boundary:

The public APIs and Kafka events do not expose:

```text
Gurobi model formulation
solver configuration
objective internals
candidate-resource rules
internal model bindings
resource-selection logic
```

OD MS exposes only the caller-facing request contract.

OC MS exposes runtime state and generic result outputs.

The worker and internal model layer own the solver-specific details.

---

## 6. Important quality attributes:

### 6.1 Availability:

OD MS and OC MS should be deployed as independently scalable and highly available services.

OD MS availability is important for capability discovery and request validation. OC MS availability is critical for runtime optimisation creation, lifecycle reads, cancellation, retrial, and event projection.

Kafka availability is critical for asynchronous worker instruction and outcome exchange. The outbox/inbox patterns reduce data-loss risk during transient service or Kafka failures.

Runtime optimisation records remain durable in OC MS DB even if worker execution is delayed. DLQ provides a controlled path for poison or unprocessable events.

### 6.2 Scalability:

OD MS scales primarily for read-heavy capability discovery.

OC MS scales for runtime API traffic, outbox relay throughput, and inbox outcome processing.

Python/Gurobi workers scale horizontally based on optimisation workload, queue depth, and solver runtime characteristics.

Kafka consumer groups allow worker scaling and OC MS inbox scaling.

Large or long-running optimisation jobs are handled asynchronously and do not block REST API request threads.

### 6.3 Performance:

`POST /optimisation` returns `202 Accepted` after syntactic and OD-MS-contract validation only.

Solver execution is asynchronous and decoupled from REST request latency.

`GET /optimisation/{id}` provides polling of lifecycle and result state.

`GET /optimisation` returns summary-only records by default to avoid large list payloads.

Runtime `result` is omitted until available.

OD MS specification responses may use caching where appropriate. OC MS runtime responses do not use response `Cache-Control` for now.

---

## 7. Risks:

| **Risk** | **Impact** | **Mitigation** |
|---|---|---|
| Long-running Gurobi executions | Delayed optimisation outcomes and increased worker capacity pressure. | Use asynchronous execution, worker scaling, queue monitoring, timeout controls, and operational alerting. |
| Best-effort cancellation | A running optimisation may not stop immediately or may produce a late outcome. | Use `CANCELLING` state, worker cancellation handling, and late outcome idempotency rules. |
| Kafka consumer lag | Execution or result projection may be delayed. | Monitor consumer lag, scale workers/inbox consumers, and alert on thresholds. |
| Invalid or stale context datasets | Poor, infeasible, or failed optimisation outcomes. | Use request contract validation, dataset versioning, worker diagnostics, and operational monitoring. |
| DLQ growth | Indicates poison messages, schema drift, or repeated processing failures. | Monitor DLQ, preserve failure metadata, and define replay/remediation procedures. |
| Misconfigured internal model binding | OD MS may expose a valid request contract while worker execution fails. | Add deployment validation, contract tests between OD MS and worker model binding, and pre-production model checks. |
| Overexposure of solver details | Sensitive optimisation logic could leak externally. | Keep OD MS limited to caller-facing request contracts and keep solver details internal. |
| Incorrect specification activation | Wrong `ACTIVE` specification may affect all new requests for a `specificationKey`. | Use ETag/If-Match, lifecycle governance, review/approval, and only one ACTIVE version per key. |
| Complex access path through OEX gateways | Misconfiguration could break user context propagation or backend access. | Use clear contract testing across OGW, OGW, Screen Builder MS, NGW, OD MS, and OC MS. |

---

## 8. Assumptions:

- Operators access OEX only after ACG approval.

- User/operator authentication uses Microsoft Entra ID SSO.

- OGW is the user-context-aware gateway for OEX APIs and OEX UI integration.

- OGW integrates with OEX Screen Builder MS using mTLS and User Context JWT.

- OEX Screen Builder MS integrates with NGW using mTLS and OAuth2 system-to-system.

- NGW exposes OD MS and OC MS APIs to authorised backend consumers.

- NGW integrates with OD MS and OC MS using mTLS.

- OC MS calls OD MS using Istio mTLS for internal service-to-service validation.

- Kafka is available as the event backbone.

- Python/Gurobi worker has authorised access to required analytics/data sources.

- The worker owns internal deterministic model binding and Gurobi execution details.

- Runtime `Optimisation` is asynchronous by design.

- `sourceContext` is optional and may be omitted for generic optimisation requests.

- Runtime `Optimisation` does not expose a business `version` field.

---

## 9. Constraints:

- NGW-exposed backend APIs are TMF-compliant.

- OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.

- Do not expose Gurobi model formulation, solver configuration, objective internals, candidate-resource rules, or model binding through public APIs.

- OD MS exposes only the caller-facing `OptimisationSpecification` request contract.

- OC MS performs syntactic and OD-MS-contract validation only.

- Runtime `Optimisation` does not expose a `version` field.

- Runtime `Optimisation` does not support client-side `PUT` or `DELETE`.

- Cancellation is represented through `lifecycleStatus = CANCELLING` and an `OptimisationRequestedEvent` with `instruction = CANCEL`.

- Only one `ACTIVE` `OptimisationSpecification` is allowed per `specificationKey`.

- ETag / If-Match is required for unsafe runtime operations such as cancellation and retrial.

- Internal Kafka events do not use TMF REST `@type`, `@baseType`, or `@schemaLocation`.

---

## 10. Appendix:

### 10.1 OD MS endpoint summary:

```http
GET    /optimisationSpecification
POST   /optimisationSpecification
GET    /optimisationSpecification/{id}
PUT    /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

### 10.2 OC MS endpoint summary:

```http
GET  /optimisation
POST /optimisation
GET  /optimisation/{id}
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
```

Unsupported:

```http
PUT    /optimisation/{id}
DELETE /optimisation/{id}
```

### 10.3 Runtime lifecycle states:

```text
ACKNOWLEDGED
QUEUED
PROCESSING
COMPLETED
INFEASIBLE
FAILED
CANCELLING
CANCELLED
```

### 10.4 Kafka topics:

```text
t7.optimisation.events
t7.optimisation.events.dlq
```

### 10.5 Event types:

```text
OptimisationRequestedEvent
OptimisationCompletedEvent
OptimisationFailedEvent
```

### 10.6 Worker instructions:

```text
EXECUTE
CANCEL
```

### 10.7 Outcome values:

```text
SUCCESS
INFEASIBLE
FAILURE
```

### 10.8 Outcome mapping:

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```

### 10.9 Key artifacts:

```text
contextdump.md
od-ms-specification.md
oc-ms-specification.md
optimisation-full-recovery-pack.md
optimisation-logical-view.drawio
optimisation-e2e-solution-brief.md
```

---


TMF/TIO alignment note:
Backend optimisation API examples use platform-readable constraint fields such as `constraintType: maximum` with `ontologyPredicate: icm:atMost` where semantic traceability to TMF/TIO upper-bound intent expressions is useful.

---

## Optimisation validation and outcome clarification:

The active design distinguishes request-contract validation from optimiser outcome.

```text
OC MS validates:
  required fields
  enum/value-type rules
  request contract shape
  cardinality rules such as candidateResources minItems = 2

OC MS does not evaluate:
  solver feasibility
  candidate ranking
  metric-vs-constraint fit
  objective trade-offs

Worker/model returns:
  SUCCESS
  INFEASIBLE
  FAILURE
```

Use `422 OPTIMISATION_CONTRACT_VIOLATION` for contract/cardinality failures, such as fewer than 2 candidate resources for a selection optimisation. Use `INFEASIBLE` only when the request is valid and the worker/model determines no feasible solution exists.

---

## Contract definition versus runtime values:

OD MS defines the optimisation request contract, including the allowed candidate resource structure under `context[]`.

OC MS carries the actual runtime `constraints[]`, `targets[]`, and `context[]` values accepted from the caller. For resource/path selection, the runtime context should include or reference candidate resources as defined by OD MS.

---

## Logical view baseline:

The logical integration model is:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Definition-management logical path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OD MS
```

Runtime-optimisation logical path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Logical responsibility split:

```text
OD MS:
  Owns OptimisationSpecification definitions using constraintSpecifications[], targetSpecifications[], and contextSpecifications[].

OC MS:
  Owns runtime Optimisation resources using constraints[], targets[], and context[].

Kafka / Python/Gurobi Worker / Gurobi Optimizer:
  Participate only in runtime execution flows after OC MS accepts the request.
```

API compliance rule:

```text
NGW-exposed OD MS and OC MS APIs are TMF-compliant.

OEX APIs exposed through OGW are private/OEX experience APIs and do not need to be TMF-compliant.

Private MS-to-MS APIs and Kafka events are internal contracts unless separately exposed.
```


---

## Process view baseline:

The process view uses the agreed front-door sequence and then branches by process type.

Common access path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
```

### Process 1: Discover optimisation capabilities:

```text
1. User authenticates through Microsoft Entra ID SSO.
2. User accesses OEX UI.
3. OEX UI calls OEX APIs.
4. OEX APIs route through OGW.
5. OGW routes to OEX Screen Builder MS.
6. OEX Screen Builder MS calls NGW.
7. NGW calls OD MS.
8. OD MS returns available ACTIVE OptimisationSpecification definitions.
9. OEX Screen Builder MS shapes the response for the OEX UI.
10. OEX UI displays available optimisation capabilities.
```

This process stops at OD MS. No runtime Optimisation is created and no Kafka/worker/optimizer execution occurs.

### Process 2: Create or activate OptimisationSpecification:

```text
1. User authenticates through Microsoft Entra ID SSO.
2. User accesses OEX UI.
3. OEX UI calls OEX APIs.
4. OEX APIs route through OGW.
5. OGW routes to OEX Screen Builder MS.
6. OEX Screen Builder MS calls NGW.
7. NGW calls OD MS.
8. OD MS validates the OptimisationSpecification definition.
9. OD MS stores the definition as DRAFT.
10. When approved/ready, OD MS transitions the definition to ACTIVE.
```

OD MS definition model:

```text
constraintSpecifications[]
targetSpecifications[]
contextSpecifications[]
```

### Process 3: Create runtime Optimisation:

```text
1. User authenticates through Microsoft Entra ID SSO.
2. User accesses OEX UI.
3. OEX UI calls OEX APIs.
4. OEX APIs route through OGW.
5. OGW routes to OEX Screen Builder MS.
6. OEX Screen Builder MS calls NGW.
7. NGW calls OC MS.
8. OC MS validates the runtime request against the ACTIVE OptimisationSpecification from OD MS.
9. OC MS persists the accepted runtime Optimisation in OC MS DB.
10. OC MS writes OptimisationRequestedEvent to OC MS Outbox in the same transaction.
11. OC MS returns 202 Accepted with Location and ETag.
12. OC MS Outbox relay publishes the event to Kafka.
13. Python/Gurobi Worker consumes the event from Kafka.
14. Python/Gurobi Worker invokes Gurobi Optimizer.
```

Runtime process expansion:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OD MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
-> Kafka
-> OC MS Inbox
-> OC MS DB
-> User polls GET /optimisation/{id}
```

OC MS runtime model:

```text
constraints[]
targets[]
context[]
```

### Process 4: Runtime request contract violation:

```text
1. Request follows the common access path to OC MS.
2. OC MS validates runtime constraints[], targets[], and context[] against the ACTIVE OptimisationSpecification.
3. Request violates the OD MS-defined request contract.
4. Example: topologySnapshot.candidateResources has fewer than 2 candidates when minItems = 2 is required.
5. OC MS rejects the request before worker execution.
6. OC MS returns 422 Unprocessable Entity with OPTIMISATION_CONTRACT_VIOLATION.
7. Error response returns through NGW -> OEX Screen Builder MS -> OGW -> OEX APIs -> OEX UI.
```

This is a request-contract validation failure, not an optimisation outcome.

### Process 5: Successful optimisation execution:

```text
1. Kafka receives OptimisationRequestedEvent with instruction EXECUTE.
2. Python/Gurobi Worker consumes the event.
3. Python/Gurobi Worker invokes Gurobi Optimizer.
4. Worker/model evaluates constraints[], targets[], and context[].
5. Worker/model performs solver feasibility, metric-vs-constraint evaluation, candidate ranking, and objective trade-off evaluation.
6. Worker/model identifies a valid selected outcome.
7. Worker emits OptimisationCompletedEvent with outcome SUCCESS to Kafka.
8. OC MS Inbox consumes the outcome event.
9. OC MS updates OC MS DB and lifecycleStatus becomes COMPLETED.
10. User polls GET /optimisation/{id} through OEX UI -> OEX APIs -> OGW -> OEX Screen Builder MS -> NGW -> OC MS.
```

### Process 6: Infeasible optimisation execution:

```text
1. Runtime request passes OC MS request-contract validation.
2. OC MS accepts the request and emits OptimisationRequestedEvent to Kafka.
3. Python/Gurobi Worker consumes the event and invokes Gurobi Optimizer.
4. Worker/model evaluates accepted constraints[], targets[], and context[].
5. Worker/model determines no feasible solution exists.
6. Worker emits OptimisationCompletedEvent with outcome INFEASIBLE to Kafka.
7. OC MS Inbox consumes the outcome event.
8. OC MS updates OC MS DB and lifecycleStatus becomes INFEASIBLE.
9. User polls GET /optimisation/{id} to view the infeasible status.
```

INFEASIBLE is an optimisation outcome, not a request-contract validation error.

### Process 7: Worker/runtime failure:

```text
1. Runtime request passes OC MS request-contract validation.
2. OC MS accepts the request and emits OptimisationRequestedEvent to Kafka.
3. Python/Gurobi Worker consumes the event and invokes Gurobi Optimizer.
4. Worker/model fails due to a technical/runtime issue.
5. Worker emits OptimisationFailedEvent with outcome FAILURE to Kafka.
6. OC MS Inbox consumes the failure event.
7. OC MS updates OC MS DB and lifecycleStatus becomes FAILED.
8. Failed Optimisation exposes retrial HATEOAS control where allowed.
```

### Process 8: Cancellation:

```text
1. User initiates cancellation from OEX UI.
2. Request follows OEX UI -> OEX APIs -> OGW -> OEX Screen Builder MS -> NGW -> OC MS.
3. Consumer action maps to POST /optimisation/<built-in function id>/cancellation with If-Match.
4. OC MS validates ETag and lifecycle state.
5. Cancellation is allowed only from ACKNOWLEDGED, QUEUED, or PROCESSING.
6. OC MS updates runtime Optimisation to CANCELLING in OC MS DB.
7. OC MS writes OptimisationRequestedEvent with instruction CANCEL to OC MS Outbox.
8. OC MS returns 202 Accepted with the updated CANCELLING resource.
9. OC MS Outbox relay publishes the cancellation instruction to Kafka.
10. Python/Gurobi Worker consumes or observes the cancellation instruction.
11. Worker/model stops or ignores work where safely possible.
12. OC MS later marks the runtime Optimisation CANCELLED according to worker/operational handling.
```

### Process 9: Retrial:

```text
1. User initiates retrial from OEX UI.
2. Request follows OEX UI -> OEX APIs -> OGW -> OEX Screen Builder MS -> NGW -> OC MS.
3. Consumer action maps to POST /optimisation/<built-in function id>/retrial with If-Match.
4. OC MS validates ETag and lifecycle state.
5. Retrial is allowed only from FAILED by default.
6. OC MS creates a new runtime Optimisation resource in OC MS DB.
7. New runtime Optimisation references the failed one using retrialOf.
8. New runtime Optimisation starts at ACKNOWLEDGED.
9. OC MS writes OptimisationRequestedEvent with instruction EXECUTE to OC MS Outbox.
10. OC MS returns 202 Accepted with Location pointing to the new Optimisation.
11. OC MS Outbox relay publishes the execute instruction to Kafka.
12. Python/Gurobi Worker consumes the event and invokes Gurobi Optimizer.
```

Retrial creates a new Optimisation. It does not mutate the failed Optimisation back into PROCESSING.

### Process 10: Late worker outcome after cancellation:

```text
1. OC MS has already moved the runtime Optimisation to CANCELLING or CANCELLED.
2. A late SUCCESS, INFEASIBLE, or FAILURE outcome arrives through Kafka from the worker.
3. OC MS must not blindly overwrite the cancellation state.
4. OC MS handles the late event idempotently as stale/late according to operational policy.
```

Process view compliance rules:

```text
NGW-exposed OD MS and OC MS APIs are TMF-compliant.

OEX APIs exposed through OGW are private/OEX experience APIs and do not need to be TMF-compliant.

Private MS-to-MS APIs and Kafka events are internal contracts unless separately exposed.
```

---

## Optimisation catalogue governance use case:

Managing the optimisation catalogue means creating, updating, activating, and retiring `OptimisationSpecification` records in OD MS.

This is an internal governed optimisation-domain capability, not a general user or consumer self-service capability.

Access rule:

```text
Only approved optimisation domain engineers can create, update, activate, or retire OptimisationSpecification records.
```

Governance rule:

```text
Catalogue changes are made only after agreement with the broader E2E teams that own, consume, or are impacted by the optimisation capability.
```

Scope:

```text
create OptimisationSpecification
update OptimisationSpecification while DRAFT
activate OptimisationSpecification after approval/readiness
retire OptimisationSpecification when no longer available for new runtime requests
manage request-contract shape through constraintSpecifications[], targetSpecifications[], and contextSpecifications[]
```

Non-scope:

```text
general user or consumer self-service specification creation
runtime optimisation execution
solver/model formulation exposure
bypassing OD MS governance to create runtime capabilities
```

