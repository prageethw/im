# Optimisation Full Recovery Pack

Generated: 2026-05-03T06:17:27

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

## Baseline appended 2026-05-03T05:50:56 - OC MS candidate resource set traceability

Updated the OC MS specification examples so resource-selection optimisation is self-contained and traceable.

Baseline rules:
- If an optimisation result selects a resource, route, path, placement, or option, the accepted inputs must provide or reference a candidate set with at least two candidate options.
- A single candidate option is not a meaningful optimisation problem unless the purpose is feasibility validation only.
- The `topologySnapshot` example now includes `candidateResourceSetId` and two candidate resources: `path-001` and `path-002`.
- The `selectedResource` result now includes `sourceInput: topologySnapshot` and the `candidateResourceSetId` so the selected `resourceId` can be traced back to the accepted inputs.

---

## Baseline appended 2026-05-03T05:54:55 - OD MS candidate resource contract and metrics naming

Baselined the required OD MS and OC MS consistency updates for resource/path/option-selection optimisation.

OD MS baseline:
- `OptimisationSpecification.inputs` must define the candidate-set input contract for optimisation capabilities that select a resource, route, path, placement, or option.
- The current example uses `topologySnapshot` to supply the candidate set.
- `topologySnapshot` must include `candidateResourceSetId`.
- Embedded `candidateResources` must have `minItems: 2`, unless the capability is explicitly feasibility-validation-only.
- Candidate resources use `resourceId`, `resourceType`, optional `resourceClass`, optional `resourceAttributes`, and `metrics`.
- Keep `metrics` as the reusable field name for measured/computed resource values used by the optimiser.
- Use `resourceAttributes` for stable descriptive candidate-resource properties.

OC MS consistency baseline:
- Runtime `inputs[]` examples include the full accepted `topologySnapshot` candidate set.
- Candidate examples include at least two candidate resources.
- Selected-resource results include `sourceInput` and `candidateResourceSetId` for traceability.
- `metrics` remains the agreed name for candidate values such as latency and reliability.

End-to-end rule:
```text
OD MS defines the candidate-set input contract.
OC MS validates runtime inputs against that contract.
Worker uses the candidate set during optimisation.
Result references the selected candidate back to sourceInput and candidateResourceSetId.
```

---

## Baseline appended 2026-05-03T06:09:08 - OC MS cancellation and retrial resource endpoints

Updated the OC MS design to use noun/resource-aligned command sub-resource endpoints.

Endpoint changes:
```text
Old:
  POST /optimisation/{id}/cancel
  POST /optimisation/{id}/retry

New:
  POST /optimisation/{id}/cancellation
  POST /optimisation/{id}/retrial
```

Meaning:
- `POST /optimisation/{id}/cancellation` creates a cancellation request/resource for the Optimisation.
- `POST /optimisation/{id}/retrial` creates a retrial request/resource for the failed Optimisation.

HATEOAS link names are updated to:
```text
cancellation
retrial
```

Lifecycle meaning remains unchanged:
- `ACKNOWLEDGED`, `QUEUED`, or `PROCESSING` can move to `CANCELLING` through cancellation.
- `FAILED` can create a new linked Optimisation through retrial.

---

## Baseline appended 2026-05-03T06:17:27 - Replace generic inputs with constraints, targets, and context

Baselined the optimisation request definition change across OD MS and OC MS.

New runtime request model:
```text
constraints[]:
  Hard pass/fail rules that must be satisfied.

targets[]:
  Optimisation goals/preferences applied among valid candidates.

context[]:
  Data used by the optimiser, including candidate resources and their metrics.
```

Current path-selection example:
```text
constraints:
  maxLatency lessThanOrEqualTo 20ms

targets:
  cost minimise, priority 1
  latency minimise, priority 2
  reliability maximise, priority 3

context:
  topologySnapshot with candidateResourceSetId and at least two candidateResources
```

Reasoning:
- The old `inputs[]` model mixed requirements and candidate data.
- `latency` and `reliability` at the top level are now replaced by clearer constraint/target definitions.
- Candidate resource measured values remain under `metrics`.
- `metrics` remains the agreed field for candidate measured/computed values.
- `resourceAttributes` remains the field for stable candidate-resource descriptive attributes.
- The example selectedResource `path-001` is consistent because `path-001` satisfies maxLatency 18ms <= 20ms while `path-002` fails maxLatency 24ms > 20ms.


---

# Part 2: Current OD MS Specification

# Optimisation-Definition-MS / OD MS Specification

## 1. OD MS summary

**Optimisation-Definition-MS (OD MS)** owns the **definition side** of the optimisation platform. Its responsibility is to publish and govern the externally visible optimisation capability contract, called `OptimisationSpecification`.

OD MS does **not** expose the Gurobi model, objective logic, candidate-resource rules, solver configuration, model binding, or internal optimisation formulation. It only exposes what a caller needs to know to create a valid runtime optimisation through OC MS.

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

---

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

---

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

---

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

---

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

It does **not** expose by default:

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

---

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

## Optimisation request definition contract baseline:

OD MS defines the caller-facing contract for the runtime optimisation request. For the current path/resource-selection capability, the contract is split into:

```text
constraints[]:
  Hard pass/fail rules that must be satisfied.
  Example: maxLatency lessThanOrEqualTo 20ms.

targets[]:
  Optimisation goals or preferences applied among valid candidates.
  Example: minimise cost first, minimise latency second, maximise reliability third.

context[]:
  Data used by the optimiser, including candidate resources and their metrics.
  Example: topologySnapshot with candidateResourceSetId and at least two candidateResources.
```

The previous generic `inputs[]` model is replaced by the clearer top-level model:

```text
constraints[]
targets[]
context[]
```

Example runtime contract values:

```json
{
  "constraints": [
    {
      "name": "maxLatency",
      "operator": "lessThanOrEqualTo",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
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
}
```

Candidate-set rule:

```text
For optimisation capabilities that select a resource, route, path, placement, or option, the context contract must provide or reference a candidate set with at least two candidate options.

A single candidate option is not a meaningful optimisation problem unless the capability is explicitly feasibility-validation-only.

Use metrics for measured or computed candidate values such as latency, reliability, cost, or utilisation.

Use resourceAttributes for stable descriptive candidate properties such as locationId or pathClass.
```

Selection consistency for the example:

```text
path-001 passes maxLatency because latency 18ms <= 20ms.
path-002 fails maxLatency because latency 24ms > 20ms.

Among valid candidates, targets are applied:
  cost minimise priority 1
  latency minimise priority 2
  reliability maximise priority 3

Therefore path-001 is the consistent selectedResource in the example result.
```


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

OC MS accepts runtime optimisation requests, validates only the wrapper and OD MS input contract, persists the request, emits a worker instruction event, then later projects worker outcomes back into the runtime resource.

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
  Cancel command has been accepted and worker should stop/ignore where safely possible.

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
  cancel

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

  // Capability-specific caller-fed inputs.
  // Validated syntactically against OD MS OptimisationSpecification.inputs.
  "constraints": [
    {
      "name": "maxLatency",
      "operator": "lessThanOrEqualTo",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
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
  ],

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
      "operator": "lessThanOrEqualTo",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
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
  ],

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


The returned Optimisation resource includes the full accepted `inputs[]` set provided by the caller, not a truncated subset.

`202 Accepted` means OC MS accepted the request for asynchronous execution. It does not mean the optimisation is feasible, started, solvable, or guaranteed to produce a valid result.

## OC MS validation boundary:

```text
OC MS validates:
  generic REST wrapper using its static API/OpenAPI contract
  referenced OptimisationSpecification exists in OD MS
  referenced OptimisationSpecification lifecycleStatus is ACTIVE
  constraints[], targets[], and context[] against the referenced ACTIVE OptimisationSpecification contract

OC MS does not validate:
  optimisation semantics
  solver feasibility
  candidate selection
  objective interpretation
  Gurobi model validity
  resource-selection correctness
```


### Runtime request definition model:

```text
constraints[]:
  Hard pass/fail rules that must be satisfied.
  Example: maxLatency lessThanOrEqualTo 20ms.

targets[]:
  Optimisation goals or preferences applied among valid candidates.
  Example: minimise cost first, minimise latency second, maximise reliability third.

context[]:
  Data used by the optimiser, including candidate resources and their metrics.
  Example: topologySnapshot with candidateResourceSetId and at least two candidateResources.
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
      "operator": "lessThanOrEqualTo",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
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
  ],

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
          "resourceType": "deliveryResource",
          "sourceInput": "topologySnapshot",
          "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z"
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
  accepted constraints[], targets[], and context[] returned in full on the Optimisation object
  result omitted until worker outcome exists
  generic result.outputs[] when outcome exists
```
Candidate-set rule:

```text
If an optimisation result selects a resource, route, path, placement, or option, the accepted context must provide or reference a candidate set with at least two candidate options.

A single candidate option is not a meaningful optimisation problem unless the purpose is feasibility validation only.

When the selected output references a resourceId, the result should include traceability back to the source input and candidateResourceSetId where applicable.
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
    // Summary only. Follow self for full inputs/result.
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
POST /optimisation/opt-12345/cancellationlation
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
      "operator": "lessThanOrEqualTo",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
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
  ],

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

Do not use separate cancel event types:

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

    "inputs": [
      {
        "name": "latency",
        "valueType": "number",
        "value": 20,
        "unit": "ms"
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
          "resourceType": "deliveryResource",
          "sourceInput": "topologySnapshot",
          "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z"
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
    "summary": "No feasible solution exists for the supplied inputs.",
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

# Part 4: Current E2E Optimisation Solution Brief

# End-to-End Solution Brief — Optimisation Platform

## 1. Business context:

The optimisation platform provides a reusable capability for running deterministic optimisation problems using Gurobi-backed models.

The platform is not limited to the intent-management domain. It is designed as a generic optimisation capability that can be used by OEX, platform services, planning tools, assurance functions, intent-management flows, and other authorised entities that need to run optimisation.

The business need is to allow authorised consumers to discover available optimisation capabilities, understand the required input contract, submit optimisation requests asynchronously, monitor execution state, request cancellation of active requests where needed, request retrial of failed requests, and retrieve final outcomes without exposing internal solver details or Gurobi model implementation.

The solution separates the definition of optimisation capabilities from the execution and lifecycle control of optimisation runs.

---

## 2. Solution summary:

The solution provides a reusable, asynchronous optimisation platform backed by deterministic Gurobi models.

It uses two core microservices:
- Optimisation-Definition-MS / OD MS owns OptimisationSpecification and exposes the caller-facing input contract.
- Optimisation-Controller-MS / OC MS owns runtime Optimisation lifecycle, cancellation, retrial, event integration, and result projection.

Consumers may include OEX, platform services, planning tools, assurance functions, intent-management flows, or other authorised entities that need to run optimisation.

Operator access to OEX is governed by the ACG approval process and Microsoft Entra ID SSO.

The OEX UI reaches OGW, which provides the user-context-aware gateway path into the OEX channel.

OGW routes user-context-aware OEX traffic to OEX Screen Builder MS.

OEX Screen Builder MS reaches backend OD MS and OC MS APIs through NGW using mTLS and OAuth2 system-to-system.

NGW exposes OD MS and OC MS endpoints as TMF-compliant backend APIs.

OC MS validates only request structure and the OD MS input contract, then returns 202 Accepted and drives execution asynchronously through Kafka.

Kafka carries worker instructions and outcomes, with a dedicated DLQ for unprocessable events.

The Python/Gurobi worker consumes EXECUTE or CANCEL instructions, runs or cancels optimisation work, and returns SUCCESS, INFEASIBLE, or FAILURE outcomes.

NGW-exposed backend APIs are TMF-compliant. OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.

---

## 3. Solution elaboration:

The solution is structured around a clean separation of responsibility.

OD MS acts as the governed catalogue of optimisation capabilities. It exposes only what callers need to know to submit valid optimisation requests. It does not expose Gurobi objectives, candidate resource rules, solver configuration, model bindings, or internal formulation details.

OC MS acts as the runtime controller. It accepts requests, validates the request shape and input contract, creates runtime optimisation resources, manages lifecycle state, publishes worker instructions, consumes worker outcomes, and projects final results.

The Python/Gurobi worker is responsible for executing the internal deterministic optimisation model. It consumes events from Kafka, executes or cancels work based on the instruction, and publishes outcome events back to Kafka.

### 3.1 Use case view:

| Use case | Actor | Summary | Outcome |
|---|---|---|---|
| Discover optimisation capability | User / OEX / platform service | Retrieve available OptimisationSpecification records from OD MS and understand required inputs. | Caller knows which optimisation capability to use and what inputs to provide. |
| Create runtime optimisation | User / OEX / platform service | Submit a runtime Optimisation request to OC MS using an ACTIVE specification and valid inputs. | OC MS returns 202 Accepted and creates an ACKNOWLEDGED optimisation. |
| Monitor optimisation | User / OEX / platform service | Read current lifecycle state and result when available. | Caller can see whether the optimisation is pending, processing, completed, infeasible, failed, cancelling, or cancelled. |
| Request optimisation cancellation | User / OEX / platform service | Request cancellation for an eligible active optimisation. | OC MS moves the resource to CANCELLING and instructs the worker to cancel where safely possible. |
| Request optimisation retrial | User / OEX / platform service | Retrial a FAILED optimisation by creating a new linked optimisation. | A new ACKNOWLEDGED optimisation is created with retrialOf pointing to the failed one. |
| Execute optimisation | Python/Gurobi worker | Consume worker instruction and execute the deterministic optimisation model. | Worker emits SUCCESS, INFEASIBLE, or FAILURE outcome. |

### 3.2 Logical view:

The logical integration model is:

User / Operator
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer

Key logical relationships:

User -> Microsoft Entra ID:
User authenticates using SSO after ACG approval.

User -> OEX UI:
User accesses the OEX UI after SSO authentication.

OEX UI -> OGW:
OEX UI reaches the OEX channel through OGW.

OGW -> OEX Screen Builder MS:
OGW provides the user-context-aware gateway path and propagates user context to the OEX backend experience capability.

OEX Screen Builder MS -> NGW:
Uses mTLS and OAuth2 system-to-system to call backend optimisation APIs.

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

Logical diagram artifact:
optimisation-logical-view.drawio

### 3.3 Process view:

#### 3.3.1 Create and activate OptimisationSpecification:

This process defines and activates an optimisation capability before runtime consumers can submit optimisation requests against it.

Authorised platform/admin consumer
-> NGW
-> OD MS
-> OD MS DB

Detailed flow:

1. Authorised platform/admin consumer creates a draft OptimisationSpecification.
2. Request reaches OD MS through NGW.
3. OD MS validates the specification wrapper and input contract structure.
4. OD MS persists the specification with lifecycleStatus = DRAFT.
5. The draft can be reviewed and updated while it remains in DRAFT.
6. When ready, the specification is activated.
7. OD MS enforces that only one ACTIVE OptimisationSpecification exists per specificationKey.
8. If another ACTIVE specification already exists for the same specificationKey, OD MS retires the previous active version transactionally.
9. OD MS persists the new specification as ACTIVE.
10. Runtime consumers can now reference this ACTIVE OptimisationSpecification in POST /optimisation.

#### 3.3.2 Create and execute optimisation:

Consumer / OEX
-> OEX UI
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
-> Consumer polls GET /optimisation/{id}

Detailed flow:

1. Consumer submits an optimisation request through the OEX experience or another authorised integration path.
2. User accesses the OEX UI after Microsoft Entra ID SSO.
3. OEX UI calls the OEX channel through OGW.
4. OGW propagates user context to the OEX backend experience path.
5. OGW routes the OEX request to OEX Screen Builder MS.
6. OEX Screen Builder MS calls NGW using mTLS and OAuth2 system-to-system.
7. NGW routes the request to OC MS.
8. OC MS validates request structure.
9. OC MS calls OD MS over Istio mTLS to validate the referenced ACTIVE OptimisationSpecification.
10. OC MS validates inputs[] against the OD MS input contract.
11. OC MS persists runtime Optimisation with lifecycleStatus = ACKNOWLEDGED.
12. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE to outbox.
13. Outbox relay publishes event to Kafka.
14. Python/Gurobi worker consumes event.
15. Worker resolves internal deterministic model binding.
16. Worker runs Gurobi.
17. Worker publishes OptimisationCompletedEvent or OptimisationFailedEvent.
18. OC MS inbox consumes worker outcome.
19. OC MS updates lifecycle and result.
20. Consumer retrieves result through GET /optimisation/{id}.

#### 3.3.3 Request optimisation cancellation:

Consumer / OEX
-> OEX UI
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker

Detailed flow:

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

#### 3.3.4 Request optimisation retrial:

Consumer / OEX
-> OEX UI
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker

Detailed flow:

1. Consumer calls POST /optimisation/{id}/retrial with If-Match.
2. Request reaches OC MS through the authorised gateway path.
3. OC MS validates original Optimisation lifecycleStatus = FAILED.
4. OC MS creates a new Optimisation resource.
5. New Optimisation links to the original through retrialOf.
6. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED.
7. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
8. Worker processes the new request.

---

## 4. Capability matrix:

| Component | Responsibility |
|---|---|
| Microsoft Entra ID | Provides SSO authentication for users/operators before they access OEX. Supplies identity context used by the user-facing access path. |
| ACG approval process | Governs operator access to OEX. Users must be approved through the organisational access-control process before they can use the OEX optimisation experience. |
| OEX UI | Provides the user/operator-facing interface for discovering optimisation capabilities, submitting requests, monitoring state, requesting cancellation, requesting retrial, and viewing results. The OEX UI reaches the OEX channel through OGW. |
| OGW | User-context-aware gateway for OEX UI integration. Uses user SSO OAuth2 from the UI path and propagates user identity context into the OEX channel. Routes OEX requests to OEX Screen Builder MS. |
| OEX Screen Builder MS | Builds and orchestrates the OEX screen/backend experience. Sits between OGW and NGW. Integrates with NGW using mTLS and OAuth2 system-to-system to call backend optimisation APIs. |
| NGW | NAAS Gateway exposing backend optimisation domain APIs for OD MS and OC MS. Provides the controlled backend API entry point for OEX Screen Builder MS and other authorised system consumers. NGW-exposed backend APIs are TMF-compliant. |
| Optimisation-Definition-MS / OD MS | Owns the definition side of the optimisation platform through OptimisationSpecification. Publishes caller-facing input contracts, manages DRAFT, ACTIVE, and RETIRED specification lifecycle, and ensures only one ACTIVE specification exists per specificationKey. Does not expose solver/model internals. |
| OD MS Database | Stores OptimisationSpecification records, version metadata, lifecycle state, input contracts, timestamps, ETag/revision data, and retained retired specifications for audit/history. |
| Optimisation-Controller-MS / OC MS | Owns runtime Optimisation resources. Accepts requests, validates the generic wrapper and OD MS input contract, manages lifecycle, cancellation, retrial, outbox/inbox integration, and result projection. Performs syntactic and contract validation only. |
| OC MS Database | Stores runtime Optimisation resources, accepted inputs, optional sourceContext, lifecycle state, status reasons, result projections, retrial links, timestamps, ETag/revision data, outbox records, and inbox records. |
| OC MS Outbox Relay | Publishes persisted OC MS outbox records to Kafka after DB commit. Publishes OptimisationRequestedEvent with instruction = EXECUTE or instruction = CANCEL. |
| Kafka topic | Main internal event stream for worker instructions and outcomes between OC MS and the Python/Gurobi worker. Uses CloudEvents-style Kafka headers. |
| Kafka DLQ | Holds events that cannot be safely processed after retrial handling. Preserves original event payload and failure metadata for operational investigation and replay decisions. |
| Python / Gurobi Worker | Consumes OptimisationRequestedEvent. For EXECUTE, resolves the internal deterministic model binding, resolves required data, executes optimisation, and emits an outcome. For CANCEL, cancels/stops/ignores processing where safely possible. |
| Internal deterministic optimisation models | Own solver-specific logic that is not exposed externally. Encapsulate objective formulation, constraints, candidate-resource rules, model binding, solver configuration, and Gurobi formulation. |
| Gurobi Optimizer | Executes the mathematical optimisation model prepared by the worker/model layer. Produces solve outcomes that the worker maps into SUCCESS, INFEASIBLE, or FAILURE. |
| Analytics platform / data sources | Provides authorised datasets required by the worker/model layer, such as topology snapshots, traffic forecasts, capacity information, inventory data, or other optimisation input datasets. |
| OC MS Inbox Consumer | Consumes worker outcome events, applies idempotency and stale/late-event handling, maps outcomes to lifecycle states, and projects result/failure details into the runtime Optimisation resource. |
| Operational support / monitoring | Monitors service health, Kafka lag, outbox/inbox processing, worker failures, solver failures, DLQ records, retrial counts, stale/late events, and optimisation lifecycle/result trends. |

---

## 5. Solution security:

### 5.1 User authentication and access governance:

Users/operators access the OEX experience through the organisational ACG approval process and SSO using Microsoft Entra ID.

User / Operator
-> ACG approval process
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OEX Screen Builder MS

OGW is the user-context-aware gateway for the OEX channel. The OEX UI reaches the OEX channel through OGW. OGW uses user SSO OAuth2 from the UI path and propagates user identity context into the OEX backend path.

### 5.2 OEX internal access path:

OEX Screen Builder MS sits between OGW and NGW.

OEX UI
-> OGW
-> OEX Screen Builder MS
-> NGW

User context is propagated through the OEX access path so optimisation actions can be traced to the initiating operator where required.

### 5.3 OEX to optimisation backend access:

OEX Screen Builder MS integrates with NGW using:
- mTLS
- OAuth2 system-to-system

NGW exposes backend optimisation domain APIs for OD MS and OC MS.

OEX Screen Builder MS
-> NGW
-> OD MS / OC MS

OD MS and OC MS are not directly exposed to end users or the UI layer.

### 5.4 NGW to OD MS / OC MS security:

NGW integrates with OD MS and OC MS using mTLS.

This secures backend API access from the gateway to the optimisation domain services.

NGW exposes OD MS and OC MS endpoints as TMF-compliant backend APIs.

### 5.5 OC MS to OD MS service-to-service security:

OC MS calls OD MS to validate referenced OptimisationSpecification resources. This internal service-to-service communication is secured using mTLS through Istio.

OC MS
-> Istio mTLS
-> OD MS

OC MS uses this call to validate:
- OptimisationSpecification exists
- OptimisationSpecification lifecycleStatus = ACTIVE
- inputs[] match the OD MS input contract

### 5.6 Kafka security:

OC MS and the Python/Gurobi worker integrate through Kafka.

Recommended controls:
- TLS for broker connectivity
- service identity for producers and consumers
- topic-level ACLs
- separate consumer groups
- DLQ access restricted to operational support

Producer/consumer permissions:

OC MS:
- produce worker instruction events
- consume worker outcome events
- produce DLQ records when needed

Python/Gurobi Worker:
- consume worker instruction events
- produce worker outcome events
- produce DLQ records when needed

### 5.7 API concurrency control:

ETags are used for unsafe runtime actions:
- POST /optimisation/{id}/cancellation
- POST /optimisation/{id}/retrial

Both require If-Match.

Failure rules:
- Missing If-Match -> 428 Precondition Required
- Stale/wrong If-Match -> 412 Precondition Failed

Runtime Optimisation does not expose a version field. ETag is used only as the HTTP concurrency mechanism.

### 5.8 Event security and integrity:

Internal Kafka events use CloudEvents-style headers:
- ce-specversion
- ce-id
- ce-type
- ce-source
- ce-time
- ce-subject
- ce-datacontenttype
- ce-correlationid
- ce-eventversion
- content-type

Kafka events do not use TMF REST fields such as:
- @type
- @baseType
- @schemaLocation

Those fields are reserved for public REST resource representations.

### 5.9 Sensitive information boundary:

The public APIs and Kafka events do not expose:
- Gurobi model formulation
- solver configuration
- objective internals
- candidate-resource rules
- internal model bindings
- resource-selection logic

OD MS exposes only the caller-facing input contract.

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

POST /optimisation returns 202 Accepted after syntactic and OD-MS-contract validation only.

Solver execution is asynchronous and decoupled from REST request latency.

GET /optimisation/{id} provides polling of lifecycle and result state.

GET /optimisation returns summary-only records by default to avoid large list payloads.

Runtime result is omitted until available.

OD MS specification responses may use caching where appropriate. OC MS runtime responses do not use response Cache-Control for now.

---

## 7. Risks:

| Risk | Impact | Mitigation |
|---|---|---|
| Long-running Gurobi executions | Delayed optimisation outcomes and increased worker capacity pressure. | Use asynchronous execution, worker scaling, queue monitoring, timeout controls, and operational alerting. |
| Best-effort cancellation | A running optimisation may not stop immediately or may produce a late outcome. | Use CANCELLING state, worker cancellation handling, and late outcome idempotency rules. |
| Kafka consumer lag | Execution or result projection may be delayed. | Monitor consumer lag, scale workers/inbox consumers, and alert on thresholds. |
| Invalid or stale input datasets | Poor, infeasible, or failed optimisation outcomes. | Use input contract validation, dataset versioning, worker diagnostics, and operational monitoring. |
| DLQ growth | Indicates poison messages, schema drift, or repeated processing failures. | Monitor DLQ, preserve failure metadata, and define replay/remediation procedures. |
| Misconfigured internal model binding | OD MS may expose a valid input contract while worker execution fails. | Add deployment validation, contract tests between OD MS and worker model binding, and pre-production model checks. |
| Overexposure of solver details | Sensitive optimisation logic could leak externally. | Keep OD MS limited to caller-facing input contracts and keep solver details internal. |
| Incorrect specification activation | Wrong ACTIVE specification may affect all new requests for a specificationKey. | Use ETag/If-Match, lifecycle governance, review/approval, and only one ACTIVE version per key. |
| Complex access path through OEX gateways | Misconfiguration could break user context propagation or backend access. | Use clear contract testing across OGW, OEX Screen Builder MS, NGW, OD MS, and OC MS. |

---

## 8. Assumptions:

- Operators access OEX only after ACG approval.
- User/operator authentication uses Microsoft Entra ID SSO.
- OGW is the user-context-aware gateway used by the OEX UI to reach the OEX backend channel.
- OEX Screen Builder MS sits between OGW and NGW.
- OEX Screen Builder MS integrates with NGW using mTLS and OAuth2 system-to-system.
- NGW exposes OD MS and OC MS endpoints to authorised backend consumers.
- NGW integrates with OD MS and OC MS using mTLS.
- OC MS calls OD MS using Istio mTLS for internal service-to-service validation.
- Kafka is available as the event backbone.
- Python/Gurobi worker has authorised access to required analytics/data sources.
- The worker owns internal deterministic model binding and Gurobi execution details.
- Runtime Optimisation is asynchronous by design.
- sourceContext is optional and may be omitted for generic optimisation requests.
- Runtime Optimisation does not expose a business version field.

---

## 9. Constraints:

- NGW-exposed backend APIs are TMF-compliant.
- OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.
- Do not expose Gurobi model formulation, solver configuration, objective internals, candidate-resource rules, or model binding through public APIs.
- OD MS exposes only the caller-facing OptimisationSpecification input contract.
- OC MS performs syntactic and OD-MS-contract validation only.
- Runtime Optimisation does not expose a version field.
- Runtime Optimisation does not support client-side PUT or DELETE.
- Cancellation is represented through lifecycleStatus = CANCELLING and an OptimisationRequestedEvent with instruction = CANCEL.
- Only one ACTIVE OptimisationSpecification is allowed per specificationKey.
- ETag / If-Match is required for unsafe runtime operations such as cancellation and retrial.
- Internal Kafka events do not use TMF REST @type, @baseType, or @schemaLocation.

---

## 10. Appendix:

### 10.1 OD MS endpoint summary:

GET    /optimisationSpecification  
POST   /optimisationSpecification  
GET    /optimisationSpecification/{id}  
PUT    /optimisationSpecification/{id}  
DELETE /optimisationSpecification/{id}

### 10.2 OC MS endpoint summary:

GET  /optimisation  
POST /optimisation  
GET  /optimisation/{id}  
POST /optimisation/{id}/cancellation  
POST /optimisation/{id}/retrial

Unsupported:

PUT    /optimisation/{id}  
DELETE /optimisation/{id}

### 10.3 Runtime lifecycle states:

ACKNOWLEDGED  
QUEUED  
PROCESSING  
COMPLETED  
INFEASIBLE  
FAILED  
CANCELLING  
CANCELLED

### 10.4 Kafka topics:

t7.optimisation.events  
t7.optimisation.events.dlq

### 10.5 Event types:

OptimisationRequestedEvent  
OptimisationCompletedEvent  
OptimisationFailedEvent

### 10.6 Worker instructions:

EXECUTE  
CANCEL

### 10.7 Outcome values:

SUCCESS  
INFEASIBLE  
FAILURE

### 10.8 Outcome mapping:

SUCCESS -> COMPLETED  
INFEASIBLE -> INFEASIBLE  
FAILURE -> FAILED

### 10.9 Key artifacts:

contextdump.md  
od-ms-specification.md  
oc-ms-specification.md  
optimisation-full-recovery-pack.md  
optimisation-logical-view.drawio  
optimisation-e2e-solution-brief.md

