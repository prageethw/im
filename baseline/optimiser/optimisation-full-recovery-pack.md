# Optimisation Full Recovery Pack

Generated: 2026-05-02T05:44:46

This file combines the current optimisation architecture recovery material into one place.

It contains:
- The cumulative baseline/context dump
- The current OD MS / Optimisation-Definition-MS specification
- The current OC MS / Optimisation-Controller-MS specification

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

## Baseline appended 2026-05-02T04:32:51 - OC MS GET /optimisation/{id} runtime read contract

For the optimisation architecture exercise, baseline `GET /optimisation/{id}` as the main polling/read endpoint for runtime `Optimisation` state.

Purpose:

```text
GET /optimisation/{id}
  Returns the current runtime Optimisation resource.
  Shows lifecycleStatus.
  Shows accepted request metadata and inputs.
  Shows result only when a worker outcome exists.
  Exposes HATEOAS links based on lifecycleStatus.
  Returns ETag for unsafe transition concurrency.
```

Response/header rules:

```text
GET /optimisation/{id}
  Response:
    200 OK
    Content-Type: application/json
    ETag required
    No response Cache-Control for runtime Optimisation for now

Resource body:
  no version field
  result omitted until a worker outcome exists
  result included for COMPLETED, INFEASIBLE, or FAILED where outcome details are available
  HATEOAS links vary by lifecycleStatus

ETag:
  used for unsafe concurrency only
  client uses latest ETag with If-Match for cancel/retry
```

Active optimisation example:

```http
GET /optimisation/opt-12345
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "opt-12345-rev2"
```

```jsonc
{
  // Server-generated runtime optimisation identity.
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",

  // TMF-aligned REST resource typing.
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  // Optional upstream context, present only if supplied at creation.
  "sourceContext": {
    "domain": "intent-management",
    "resource": {
      "id": "intent-789",
      "href": "/intentManagement/v5/intent/intent-789",
      "@type": "IntentRef",
      "@referredType": "Intent"
    }
  },

  // Runtime metadata.
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice intent.",
  "priority": "1",

  // Runtime lifecycle owned by OC MS.
  // Runtime Optimisation does not expose a version field.
  "lifecycleStatus": "PROCESSING",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:01:00Z",
  "statusChangeDate": "2026-05-02T03:01:00Z",

  // Specification used to validate and trigger this optimisation.
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  // Accepted caller-fed inputs.
  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    },
    {
      "name": "topologySnapshot",
      "valueType": "object",
      "value": {
        "dataset": "topology-snapshot",
        "version": "2026-05-02T10:00:00Z"
      }
    }
  ],

  // No result field is included while lifecycleStatus is ACKNOWLEDGED, QUEUED, PROCESSING, or CANCELLING.

  // PROCESSING can still be cancelled.
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

Completed optimisation example:

```http
GET /optimisation/opt-12345
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "opt-12345-rev5"
```

```jsonc
{
  // Server-generated runtime optimisation identity.
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",

  // TMF-aligned REST resource typing.
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  // Runtime metadata.
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice intent.",
  "priority": "1",

  // Terminal successful lifecycle state.
  "lifecycleStatus": "COMPLETED",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:03:00Z",
  "statusChangeDate": "2026-05-02T03:03:00Z",

  // Specification used to validate and trigger this optimisation.
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  // Accepted caller-fed inputs.
  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    }
  ],

  // Result is included only when a worker outcome exists.
  // Public result uses a generic outputs[] structure because model-specific result semantics
  // are owned by the deterministic optimisation capability and worker output.
  "result": {
    "solutionStatus": "OPTIMAL",
    "completedAt": "2026-05-02T03:03:00Z",
    "summary": "Optimisation completed successfully.",
    "outputs": [
      {
        // Selected resource returned by the model.
        "name": "selectedResource",
        "valueType": "object",
        "value": {
          "resourceId": "path-001",
          "resourceType": "deliveryResource"
        }
      },
      {
        // Objective value returned by the model.
        "name": "objectiveValue",
        "valueType": "number",
        "value": 70,
        "unit": "costUnit"
      }
    ]
  },

  // COMPLETED is terminal.
  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    }
  }
}
```

HATEOAS by lifecycle:

```text
ACKNOWLEDGED / QUEUED / PROCESSING:
  self
  cancel

CANCELLING:
  self

FAILED:
  self
  retry

COMPLETED / INFEASIBLE / CANCELLED:
  self
```

Public result shape rule:

```text
Use generic result.outputs[] publicly so OC MS does not have to expose model-specific result schema in OD MS.
```

---

## Baseline appended 2026-05-02T04:34:50 - OC MS GET /optimisation list/search contract

For the optimisation architecture exercise, baseline `GET /optimisation` as the OC MS list/search endpoint for runtime `Optimisation` resources.

Purpose:

```text
GET /optimisation
  Lists/searches runtime Optimisation resources.
  Returns summary items.
  Supports filtering by lifecycleStatus, sourceContext domain, specification, creation date, and pagination.
  Does not include full inputs or result by default.
```

Request:

```http
# List runtime Optimisation resources.
GET /optimisation?lifecycleStatus=PROCESSING&offset=0&limit=20
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

Successful response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Total-Count: 52
X-Result-Count: 20
```

Response body:

```jsonc
[
  {
    // Summary item only.
    // Follow self to retrieve full inputs/result.
    "id": "opt-12345",
    "href": "/optimisation/opt-12345",

    // TMF-aligned REST resource typing.
    "@type": "Optimisation",
    "@baseType": "Entity",
    "@schemaLocation": "/schema/Optimisation.schema.json",

    // Runtime metadata summary.
    "name": "Hospital surgical slice path optimisation request",
    "description": "Optimise path selection for hospital surgical slice intent.",
    "priority": "1",

    // Current lifecycle state.
    "lifecycleStatus": "PROCESSING",
    "creationDate": "2026-05-02T03:00:00Z",
    "lastUpdate": "2026-05-02T03:01:00Z",
    "statusChangeDate": "2026-05-02T03:01:00Z",

    // Optional source context summary, present only if supplied at creation.
    "sourceContext": {
      "domain": "intent-management",
      "resource": {
        "id": "intent-789",
        "href": "/intentManagement/v5/intent/intent-789",
        "@type": "IntentRef",
        "@referredType": "Intent"
      }
    },

    // Specification reference used by this runtime optimisation.
    "optimisationSpecification": {
      "id": "os-7f3a9c21",
      "href": "/optimisationSpecification/os-7f3a9c21",
      "@type": "OptimisationSpecificationRef",
      "@referredType": "OptimisationSpecification"
    },

    // Summary links only.
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
]
```

List rules:

```text
GET /optimisation:
  returns summary-only resources by default
  does not include full inputs by default
  does not include result by default
  does not include ETag by default for each item
  no response Cache-Control for runtime Optimisation for now
  includes X-Total-Count and X-Result-Count
  HATEOAS links still vary by lifecycleStatus
```

Rationale:

```text
Full inputs and result may be large or model-specific.
List/search should remain lightweight.
GET /optimisation/{id} is the detail endpoint.
```

---

## Baseline appended {timestamp} - OC MS execute/cancel API requests and OptimisationRequestedEvent instructions

For the optimisation architecture exercise, baseline the OC MS API and event model for both starting optimisation processing and requesting cancellation.

Use one Kafka topic:

```text
t7.optimisation.events
```

Use one worker request/instruction event type:

```text
OptimisationRequestedEvent
```

Use `body.instruction` to tell the Python/Gurobi worker what action is requested:

```text
EXECUTE:
  Worker should execute/start the optimisation.

CANCEL:
  Worker should cancel/stop/ignore the optimisation where safely possible.
```

Do not introduce separate cancel event types by default:

```text
Do not use:
  OptimisationCancelRequestedEvent
  OptimisationControlEvent
```

Outcome events remain separate:

```text
OptimisationCompletedEvent
OptimisationFailedEvent
```

---

### Processing API request: POST /optimisation

```http
POST /optimisation
Content-Type: application/json
```

```jsonc
{
  // Optional source context.
  // Used only when the caller wants to link this optimisation to an upstream domain/resource.
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

  // Required optimisation capability reference.
  // Must point to an ACTIVE OptimisationSpecification owned by OD MS.
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  // Human-readable runtime metadata.
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice intent.",

  // Runtime priority for scheduling/handling.
  // OC MS owns the allowed priority model.
  "priority": "1",

  // Capability-specific caller-fed inputs.
  // These are validated syntactically against the referenced OD MS OptimisationSpecification.inputs.
  // Feasibility/semantic checks are left to the Python/Gurobi worker.
  "inputs": [
    {
      // Required by the referenced OptimisationSpecification.
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      // Required by the referenced OptimisationSpecification.
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    },
    {
      // Optional input allowed by the referenced OptimisationSpecification.
      "name": "topologySnapshot",
      "valueType": "object",
      "value": {
        "dataset": "topology-snapshot",
        "version": "2026-05-02T10:00:00Z"
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
  // Server-generated runtime optimisation identity.
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",

  // TMF-aligned REST resource typing.
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  // Optional source context copied from request when supplied.
  "sourceContext": {
    "domain": "intent-management",
    "resource": {
      "id": "intent-789",
      "href": "/intentManagement/v5/intent/intent-789",
      "@type": "IntentRef",
      "@referredType": "Intent"
    }
  },

  // Accepted runtime metadata.
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice intent.",
  "priority": "1",

  // Runtime lifecycle owned by OC MS.
  // Runtime Optimisation does not expose a version field.
  "lifecycleStatus": "ACKNOWLEDGED",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:00:00Z",
  "statusChangeDate": "2026-05-02T03:00:00Z",

  // Specification used to validate and trigger this optimisation.
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  // Accepted caller-fed inputs.
  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    },
    {
      "name": "topologySnapshot",
      "valueType": "object",
      "value": {
        "dataset": "topology-snapshot",
        "version": "2026-05-02T10:00:00Z"
      }
    }
  ],

  // ACKNOWLEDGED can still be cancelled.
  // Unsafe transitions require If-Match using the latest ETag response header.
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

Acceptance rule:

```text
202 Accepted means OC MS accepted the request for asynchronous optimisation execution.

It does not mean:
  the optimisation is feasible
  Gurobi has started
  Gurobi can solve the model
  a valid result will definitely be produced
```

OC MS acceptance processing:

```text
1. Perform syntactic and OD-MS-contract validation only.
2. Persist runtime Optimisation with lifecycleStatus = ACKNOWLEDGED.
3. Write OptimisationRequestedEvent with instruction = EXECUTE to OC MS outbox in the same database transaction.
4. Return 202 Accepted.
5. Outbox relay later publishes the event to t7.optimisation.events.
```

---

### Processing event: OptimisationRequestedEvent / instruction EXECUTE

Kafka topic:

```text
t7.optimisation.events
```

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
  // Internal event identity.
  // Kafka events do not use TMF REST @type/@baseType/@schemaLocation.
  "eventId": "evt-12345",
  "eventType": "OptimisationRequestedEvent",
  "eventVersion": "1.0",

  // Producer service.
  "source": "optimisation-controller-ms",

  // Event creation time.
  "eventTime": "2026-05-02T03:00:00Z",

  // Correlation across request, worker execution, and result events.
  "correlationId": "corr-12345",

  // Minimal worker instruction payload.
  "body": {
    // Runtime Optimisation this instruction applies to.
    "optimisationId": "opt-12345",

    // REST location for traceability.
    "optimisationHref": "/optimisation/opt-12345",

    // Explicit worker instruction.
    "instruction": "EXECUTE",

    // ACTIVE OptimisationSpecification used to validate this request.
    // Worker resolves internal deterministic model binding from this reference.
    "optimisationSpecification": {
      "id": "os-7f3a9c21",
      "href": "/optimisationSpecification/os-7f3a9c21"
    },

    // Optional upstream context copied from runtime Optimisation if supplied.
    "sourceContext": {
      "domain": "intent-management",
      "resource": {
        "id": "intent-789",
        "href": "/intentManagement/v5/intent/intent-789",
        "resourceType": "Intent"
      }
    },

    // Caller-fed inputs accepted by OC MS.
    "inputs": [
      {
        "name": "latency",
        "valueType": "number",
        "value": 20,
        "unit": "ms"
      },
      {
        "name": "reliability",
        "valueType": "number",
        "value": 99.99,
        "unit": "percent"
      },
      {
        "name": "topologySnapshot",
        "valueType": "object",
        "value": {
          "dataset": "topology-snapshot",
          "version": "2026-05-02T10:00:00Z"
        }
      }
    ]
  }
}
```

EXECUTE event boundary:

```text
OptimisationRequestedEvent with instruction = EXECUTE includes:
  optimisationId
  optimisationHref
  instruction
  optimisationSpecification reference
  optional sourceContext
  inputs

It does not include:
  full Optimisation REST representation
  HATEOAS links
  ETag
  solver configuration
  objective internals
  candidate-resource rules
  model formulation
  result
```

---

### Cancellation API request: POST /optimisation/{id}/cancel

```http
POST /optimisation/opt-12345/cancel
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
  // Runtime optimisation identity.
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",

  // TMF-aligned REST resource typing.
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  // Cancellation has been accepted but may not be fully completed yet.
  "lifecycleStatus": "CANCELLING",

  // Optional caller-provided reason.
  "statusReason": "Caller no longer requires this optimisation.",

  "lastUpdate": "2026-05-02T03:02:00Z",
  "statusChangeDate": "2026-05-02T03:02:00Z",

  // CANCELLING exposes self only.
  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    }
  }
}
```

Cancellation state rules:

```text
Allowed source states:
  ACKNOWLEDGED
  QUEUED
  PROCESSING

Target state:
  CANCELLING

Final cancellation state:
  CANCELLED
```

OC MS cancellation processing:

```text
1. Validate If-Match.
2. Validate current lifecycleStatus is ACKNOWLEDGED, QUEUED, or PROCESSING.
3. Move lifecycleStatus to CANCELLING.
4. Store optional statusReason.
5. Write OptimisationRequestedEvent with instruction = CANCEL to OC MS outbox in the same transaction.
6. Return 202 Accepted.
7. Outbox relay later publishes the event to t7.optimisation.events.
```

No separate cancel event type is used:

```text
Do not use:
  OptimisationCancelRequestedEvent
  OptimisationControlEvent
```

---

### Cancellation event: OptimisationRequestedEvent / instruction CANCEL

Kafka topic:

```text
t7.optimisation.events
```

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
  // Internal event identity.
  // Kafka events do not use TMF REST @type/@baseType/@schemaLocation.
  "eventId": "evt-67890",
  "eventType": "OptimisationRequestedEvent",
  "eventVersion": "1.0",

  // Producer service.
  "source": "optimisation-controller-ms",

  // Event creation time.
  "eventTime": "2026-05-02T03:02:00Z",

  // Same correlation as the original optimisation request where possible.
  "correlationId": "corr-12345",

  // Minimal worker instruction payload.
  "body": {
    // Runtime Optimisation this instruction applies to.
    "optimisationId": "opt-12345",

    // REST location for traceability.
    "optimisationHref": "/optimisation/opt-12345",

    // Explicit worker instruction.
    "instruction": "CANCEL",

    // Optional caller-provided reason.
    "reason": "Caller no longer requires this optimisation."
  }
}
```

CANCEL event boundary:

```text
OptimisationRequestedEvent with instruction = CANCEL includes:
  optimisationId
  optimisationHref
  instruction
  optional reason

It does not include:
  full Optimisation REST representation
  HATEOAS links
  ETag
  optimisationSpecification
  inputs
  solver configuration
  objective internals
  candidate-resource rules
  model formulation
  result
```

Worker handling rule:

```text
Worker branches on body.instruction.

If instruction = EXECUTE:
  worker resolves internal deterministic model binding from the optimisationSpecification reference and starts execution.

If instruction = CANCEL:
  worker cancels/stops/ignores the optimisation where safely possible.
```

CloudEvents header mapping rule:

```text
ce-id:
  Same value as payload.eventId.

ce-type:
  Stable technical event type for the worker request event:
    au.com.mycsp.optimisation.requested.v1

ce-source:
  Producer component:
    optimisation-controller-ms

ce-subject:
  Business subject of the event:
    optimisation/{optimisationId}

ce-time:
  Same instant as payload.eventTime.

ce-correlationid:
  Same value as payload.correlationId.

ce-eventversion:
  Same value as payload.eventVersion.

ce-datacontenttype and content-type:
  application/json
```

---

## Baseline appended 2026-05-02T04:59:57 - Current OC MS processing and cancelling API/event baseline

For the optimisation architecture exercise, baseline the current OC MS processing and cancelling model.

Use one Kafka topic:

```text
t7.optimisation.events
```

Use one worker request event type:

```text
OptimisationRequestedEvent
```

The worker branches on:

```text
body.instruction
```

Allowed initial instructions:

```text
EXECUTE
CANCEL
```

Do not introduce separate cancel event types by default:

```text
Do not use:
  OptimisationCancelRequestedEvent
  OptimisationControlEvent
```

Outcome events remain separate:

```text
OptimisationCompletedEvent
OptimisationFailedEvent
```

---

### Processing API: POST /optimisation

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

  // Validated syntactically against OD MS OptimisationSpecification.inputs.
  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    },
    {
      "name": "topologySnapshot",
      "valueType": "object",
      "value": {
        "dataset": "topology-snapshot",
        "version": "2026-05-02T10:00:00Z"
      }
    }
  ],

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

  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    },
    {
      "name": "topologySnapshot",
      "valueType": "object",
      "value": {
        "dataset": "topology-snapshot",
        "version": "2026-05-02T10:00:00Z"
      }
    }
  ],

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

OC MS writes `OptimisationRequestedEvent` with `instruction = EXECUTE` to its outbox in the same DB transaction.

---

### Processing event: OptimisationRequestedEvent / EXECUTE

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
  // Internal event identity.
  // Kafka events do not use TMF REST @type/@baseType/@schemaLocation.
  "eventId": "evt-12345",
  "eventType": "OptimisationRequestedEvent",
  "eventVersion": "1.0",
  "source": "optimisation-controller-ms",
  "eventTime": "2026-05-02T03:00:00Z",
  "correlationId": "corr-12345",

  "body": {
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",

    // Explicit worker instruction.
    "instruction": "EXECUTE",

    // Worker resolves internal deterministic model binding from this reference.
    "optimisationSpecification": {
      "id": "os-7f3a9c21",
      "href": "/optimisationSpecification/os-7f3a9c21"
    },

    "sourceContext": {
      "domain": "intent-management",
      "resource": {
        "id": "intent-789",
        "href": "/intentManagement/v5/intent/intent-789",
        "resourceType": "Intent"
      }
    },

    "inputs": [
      {
        "name": "latency",
        "valueType": "number",
        "value": 20,
        "unit": "ms"
      },
      {
        "name": "reliability",
        "valueType": "number",
        "value": 99.99,
        "unit": "percent"
      },
      {
        "name": "topologySnapshot",
        "valueType": "object",
        "value": {
          "dataset": "topology-snapshot",
          "version": "2026-05-02T10:00:00Z"
        }
      }
    ]
  }
}
```

---

### Cancellation API: POST /optimisation/{id}/cancel

```http
POST /optimisation/opt-12345/cancel
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

Target state:

```text
CANCELLING
```

Final cancellation state:

```text
CANCELLED
```

OC MS writes `OptimisationRequestedEvent` with `instruction = CANCEL` to its outbox in the same transaction.

---

### Cancellation event: OptimisationRequestedEvent / CANCEL

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
  // Internal event identity.
  // Kafka events do not use TMF REST @type/@baseType/@schemaLocation.
  "eventId": "evt-67890",
  "eventType": "OptimisationRequestedEvent",
  "eventVersion": "1.0",
  "source": "optimisation-controller-ms",
  "eventTime": "2026-05-02T03:02:00Z",
  "correlationId": "corr-12345",

  "body": {
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",

    // Explicit worker instruction.
    "instruction": "CANCEL",

    // Optional caller-provided reason.
    "reason": "Caller no longer requires this optimisation."
  }
}
```

Worker handling:

```text
If instruction = EXECUTE:
  worker resolves internal deterministic model binding from optimisationSpecification and starts execution.

If instruction = CANCEL:
  worker cancels/stops/ignores the optimisation where safely possible.
```

---

## Baseline appended 2026-05-02T05:29:42 - Worker outcome events for OptimisationCompletedEvent and OptimisationFailedEvent

For the optimisation architecture exercise, baseline the worker outcome events published by the Python/Gurobi worker to:

```text
t7.optimisation.events
```

Outcome event types:

```text
OptimisationCompletedEvent
OptimisationFailedEvent
```

High-level outcome values:

```text
SUCCESS
INFEASIBLE
FAILURE
```

Outcome-to-lifecycle mapping:

```text
outcome = SUCCESS
  OC MS lifecycleStatus -> COMPLETED

outcome = INFEASIBLE
  OC MS lifecycleStatus -> INFEASIBLE

outcome = FAILURE
  OC MS lifecycleStatus -> FAILED
```

Do not include `solutionStatus` by default.

```text
Use outcome as the public/contractual result classification.

If solver-specific status is needed later, add it as optional diagnostic metadata, not as the primary status used by OC MS.
```

---

### OptimisationCompletedEvent / outcome = SUCCESS

Kafka headers:

```text
ce-specversion: 1.0
ce-id: evt-22345
ce-type: au.com.mycsp.optimisation.completed.v1
ce-source: gurobi-worker
ce-time: 2026-05-02T03:03:00Z
ce-subject: optimisation/opt-12345
ce-datacontenttype: application/json
ce-correlationid: corr-12345
ce-eventversion: 1.0
content-type: application/json
```

Payload:

```jsonc
{
  // Internal event identity.
  // Kafka events do not use TMF REST @type/@baseType/@schemaLocation.
  "eventId": "evt-22345",
  "eventType": "OptimisationCompletedEvent",
  "eventVersion": "1.0",

  // Producer component.
  "source": "gurobi-worker",

  // Event creation time.
  "eventTime": "2026-05-02T03:03:00Z",

  // Same correlation as the original OptimisationRequestedEvent where possible.
  "correlationId": "corr-12345",

  "body": {
    // Runtime Optimisation completed by the worker.
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",

    // High-level outcome used by OC MS for lifecycle mapping.
    "outcome": "SUCCESS",

    // Human-readable outcome summary.
    "summary": "Optimisation completed successfully.",

    // Worker completion timestamp.
    "completedAt": "2026-05-02T03:03:00Z",

    // Generic public outputs to project into Optimisation.result.outputs[].
    "outputs": [
      {
        // Selected resource returned by the deterministic model.
        "name": "selectedResource",
        "valueType": "object",
        "value": {
          "resourceId": "path-001",
          "resourceType": "deliveryResource"
        }
      },
      {
        // Objective value returned by the deterministic model.
        "name": "objectiveValue",
        "valueType": "number",
        "value": 70,
        "unit": "costUnit"
      }
    ]
  }
}
```

---

### OptimisationCompletedEvent / outcome = INFEASIBLE

Use `OptimisationCompletedEvent` because the solver completed correctly; it simply found no feasible solution.

Kafka headers:

```text
ce-specversion: 1.0
ce-id: evt-22346
ce-type: au.com.mycsp.optimisation.completed.v1
ce-source: gurobi-worker
ce-time: 2026-05-02T03:03:00Z
ce-subject: optimisation/opt-12345
ce-datacontenttype: application/json
ce-correlationid: corr-12345
ce-eventversion: 1.0
content-type: application/json
```

Payload:

```jsonc
{
  // Internal event identity.
  "eventId": "evt-22346",
  "eventType": "OptimisationCompletedEvent",
  "eventVersion": "1.0",

  // Producer component.
  "source": "gurobi-worker",

  // Event creation time.
  "eventTime": "2026-05-02T03:03:00Z",

  // Same correlation as the original OptimisationRequestedEvent where possible.
  "correlationId": "corr-12345",

  "body": {
    // Runtime Optimisation completed by the worker.
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",

    // High-level outcome used by OC MS for lifecycle mapping.
    "outcome": "INFEASIBLE",

    // Human-readable outcome summary.
    "summary": "No feasible solution exists for the supplied inputs.",

    // Worker completion timestamp.
    "completedAt": "2026-05-02T03:03:00Z"
  }
}
```

---

### OptimisationFailedEvent / outcome = FAILURE

Use `OptimisationFailedEvent` when the worker could not complete execution due to a technical/runtime failure.

Kafka headers:

```text
ce-specversion: 1.0
ce-id: evt-32345
ce-type: au.com.mycsp.optimisation.failed.v1
ce-source: gurobi-worker
ce-time: 2026-05-02T03:03:00Z
ce-subject: optimisation/opt-12345
ce-datacontenttype: application/json
ce-correlationid: corr-12345
ce-eventversion: 1.0
content-type: application/json
```

Payload:

```jsonc
{
  // Internal event identity.
  "eventId": "evt-32345",
  "eventType": "OptimisationFailedEvent",
  "eventVersion": "1.0",

  // Producer component.
  "source": "gurobi-worker",

  // Event creation time.
  "eventTime": "2026-05-02T03:03:00Z",

  // Same correlation as the original OptimisationRequestedEvent where possible.
  "correlationId": "corr-12345",

  "body": {
    // Runtime Optimisation that failed during worker execution.
    "optimisationId": "opt-12345",
    "optimisationHref": "/optimisation/opt-12345",

    // High-level outcome used by OC MS for lifecycle mapping.
    "outcome": "FAILURE",

    // Failure classification for operational handling.
    "failureType": "SOLVER_EXECUTION_ERROR",

    // Human-readable failure reason.
    "failureReason": "Gurobi solver execution failed before producing a result.",

    // Worker failure timestamp.
    "failedAt": "2026-05-02T03:03:00Z"
  }
}
```

---

### OC MS handling rule

```text
When OC MS consumes OptimisationCompletedEvent:
  If outcome = SUCCESS:
    lifecycleStatus -> COMPLETED
    result.outcome -> SUCCESS
    result.summary -> summary
    result.outputs[] -> outputs[]

  If outcome = INFEASIBLE:
    lifecycleStatus -> INFEASIBLE
    result.outcome -> INFEASIBLE
    result.summary -> summary

When OC MS consumes OptimisationFailedEvent:
  If outcome = FAILURE:
    lifecycleStatus -> FAILED
    result.outcome -> FAILURE
    result.failureType -> failureType
    result.failureReason -> failureReason
```

Late outcome rule:

```text
If OC MS has already moved the Optimisation to CANCELLING or CANCELLED:
  OC MS must not blindly apply a late SUCCESS, INFEASIBLE, or FAILURE outcome.
  It should handle the event idempotently as stale/late according to operational policy.
```

---

## Baseline appended 2026-05-02T05:31:55 - OC MS POST /optimisation/{id}/retry contract

For the optimisation architecture exercise, baseline `POST /optimisation/{id}/retry`.

Retry rule:

```text
POST /optimisation/{id}/retry creates a new Optimisation resource linked to the original one.

It does not mutate the old Optimisation back into PROCESSING.
```

Purpose:

```text
POST /optimisation/{id}/retry
  Retries a failed runtime Optimisation by creating a new Optimisation resource.
  Requires If-Match on the original Optimisation.
  Allowed only when original lifecycleStatus = FAILED.
  Copies sourceContext, optimisationSpecification, priority, and inputs from the original unless explicitly overridden later.
  Writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
  Returns 202 Accepted with Location of the new Optimisation.
```

Request:

```http
POST /optimisation/opt-12345/retry
If-Match: "opt-12345-rev5"
Content-Type: application/json
```

```jsonc
{
  // Optional retry reason for audit.
  "reason": "Retry after temporary solver execution failure."
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
  // New runtime optimisation created by retry.
  "id": "opt-67890",
  "href": "/optimisation/opt-67890",

  // TMF-aligned REST resource typing.
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",

  // Link to the failed optimisation being retried.
  "retryOf": {
    "id": "opt-12345",
    "href": "/optimisation/opt-12345",
    "@type": "OptimisationRef",
    "@referredType": "Optimisation"
  },

  // Optional audit reason from retry request.
  "statusReason": "Retry after temporary solver execution failure.",

  // Copied from the original Optimisation when present.
  "sourceContext": {
    "domain": "intent-management",
    "resource": {
      "id": "intent-789",
      "href": "/intentManagement/v5/intent/intent-789",
      "@type": "IntentRef",
      "@referredType": "Intent"
    }
  },

  // Runtime metadata copied from original, or adjusted by OC MS if needed.
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice intent.",
  "priority": "1",

  // New resource starts from ACKNOWLEDGED.
  "lifecycleStatus": "ACKNOWLEDGED",
  "creationDate": "2026-05-02T03:10:00Z",
  "lastUpdate": "2026-05-02T03:10:00Z",
  "statusChangeDate": "2026-05-02T03:10:00Z",

  // Same OptimisationSpecification reference as original.
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },

  // Same accepted inputs as original.
  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    }
  ],

  // New retry run can be cancelled.
  "_links": {
    "self": {
      "href": "/optimisation/opt-67890",
      "method": "GET"
    },
    "cancel": {
      "href": "/optimisation/opt-67890/cancel",
      "method": "POST"
    }
  }
}
```

Retry state rules:

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

Reasoning:

```text
FAILED:
  retry is useful because the failure may be temporary/technical.

INFEASIBLE:
  retrying the same inputs is not useful because the solver completed correctly and found no feasible solution.
  Caller should create a new Optimisation with changed inputs.

COMPLETED:
  already succeeded.

CANCELLED:
  caller intentionally stopped it.
  Caller should create a new Optimisation if they want to run again.
```

Failure responses:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
```

```jsonc
{
  // If-Match is mandatory for unsafe transition operations.
  "code": "PRECONDITION_REQUIRED",
  "reason": "IF_MATCH_REQUIRED",
  "message": "If-Match header is required when retrying an Optimisation.",
  "status": "428",
  "@type": "Error"
}
```

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
```

```jsonc
{
  // Supplied ETag does not match the current resource revision.
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied ETag does not match the current Optimisation resource revision.",
  "status": "412",
  "@type": "Error"
}
```

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```jsonc
{
  // Only FAILED Optimisation resources can be retried by default.
  "code": "CONFLICT",
  "reason": "OPTIMISATION_NOT_RETRYABLE",
  "message": "Only FAILED Optimisation resources can be retried.",
  "status": "409",
  "@type": "Error"
}
```

Event rule:

```text
When retry is accepted, OC MS creates a new Optimisation and writes:

  OptimisationRequestedEvent
  instruction = EXECUTE
  optimisationId = opt-67890

to its outbox.

The old failed Optimisation remains unchanged except optional audit metadata such as lastRetryAt if explicitly added later.
```

---

## Baseline appended 2026-05-02T05:34:09 - OC MS endpoint set excludes PUT and DELETE

For the optimisation architecture exercise, baseline that OC MS / Optimisation-Controller-MS does not support direct client-side `PUT /optimisation/{id}` or `DELETE /optimisation/{id}`.

Runtime `Optimisation` is an execution/audit record, not an editable draft definition.

Do not support:

```http
PUT /optimisation/{id}
DELETE /optimisation/{id}
```

Reason for no PUT:

```text
Runtime Optimisation is not a draft/editable definition.
It is an immutable request record plus lifecycle/result updates owned by OC MS.
Client changes should be represented by creating a new Optimisation, cancelling, or retrying.
```

Reason for no DELETE:

```text
Runtime Optimisation records should remain available for audit/history.
Terminal records such as COMPLETED, FAILED, INFEASIBLE, and CANCELLED should not be deleted through the public API.
```

Final OC MS endpoint set:

```http
# List/search runtime Optimisation resources.
GET /optimisation

# Create a runtime Optimisation.
POST /optimisation

# Retrieve runtime Optimisation state/result.
GET /optimisation/{id}

# Request cancellation of an active runtime Optimisation.
POST /optimisation/{id}/cancel

# Retry a failed runtime Optimisation by creating a new linked Optimisation.
POST /optimisation/{id}/retry
```

Unsupported operation response:

```http
HTTP/1.1 405 Method Not Allowed
Allow: GET
Content-Type: application/json
```

```jsonc
{
  // Runtime Optimisation resources are not directly replaced or deleted by clients.
  "code": "METHOD_NOT_ALLOWED",
  "reason": "METHOD_NOT_ALLOWED",
  "message": "Runtime Optimisation resources cannot be replaced or deleted. Use cancel, retry, or create a new Optimisation.",
  "status": "405",
  "@type": "Error"
}
```

For collection route `/optimisation`, allowed methods are:

```text
GET
POST
```

For item route `/optimisation/{id}`, allowed method is:

```text
GET
```

Transition operations are exposed through HATEOAS action links:

```text
POST /optimisation/{id}/cancel
POST /optimisation/{id}/retry
```

---

## Baseline appended 2026-05-02T05:37:57 - OC MS specification file created

Baselined the current OC MS / Optimisation-Controller-MS specification as a separate artifact:

```text
oc-ms-specification.md
```

This artifact contains the current OC MS final specification, including:
- OC MS ownership and non-ownership
- endpoint set
- exclusion of PUT and DELETE for runtime Optimisation
- runtime lifecycle and transitions
- HATEOAS by lifecycle state
- POST /optimisation
- GET /optimisation/{id}
- GET /optimisation
- POST /optimisation/{id}/cancel
- POST /optimisation/{id}/retry
- event model on t7.optimisation.events
- OptimisationRequestedEvent with instruction EXECUTE and CANCEL
- worker outcome events OptimisationCompletedEvent and OptimisationFailedEvent
- outcome values SUCCESS, INFEASIBLE, FAILURE
- ETag/If-Match concurrency rules


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
POST /optimisation/{id}/cancel

# Retry a failed runtime Optimisation by creating a new linked Optimisation.
POST /optimisation/{id}/retry
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

FAILED -> retry creates a new Optimisation

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
  retry

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
  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    },
    {
      "name": "topologySnapshot",
      "valueType": "object",
      "value": {
        "dataset": "topology-snapshot",
        "version": "2026-05-02T10:00:00Z"
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

  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    },
    {
      "name": "reliability",
      "valueType": "number",
      "value": 99.99,
      "unit": "percent"
    }
  ],

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

`202 Accepted` means OC MS accepted the request for asynchronous execution. It does not mean the optimisation is feasible, started, solvable, or guaranteed to produce a valid result.

## OC MS validation boundary:

```text
OC MS validates:
  generic REST wrapper using its static API/OpenAPI contract
  referenced OptimisationSpecification exists in OD MS
  referenced OptimisationSpecification lifecycleStatus is ACTIVE
  inputs[] against the referenced ACTIVE OptimisationSpecification.inputs

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

  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    }
  ],

  // No result field while lifecycleStatus is ACKNOWLEDGED, QUEUED, PROCESSING, or CANCELLING.
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
      "cancel": {
        "href": "/optimisation/opt-12345/cancel",
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
  no full inputs by default
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

## POST /optimisation/{id}/cancel:

```http
POST /optimisation/opt-12345/cancel
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

## POST /optimisation/{id}/retry:

```http
POST /optimisation/opt-12345/retry
If-Match: "opt-12345-rev5"
Content-Type: application/json
```

```jsonc
{
  // Optional retry reason for audit.
  "reason": "Retry after temporary solver execution failure."
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

  "retryOf": {
    "id": "opt-12345",
    "href": "/optimisation/opt-12345",
    "@type": "OptimisationRef",
    "@referredType": "Optimisation"
  },

  "statusReason": "Retry after temporary solver execution failure.",

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

  "inputs": [
    {
      "name": "latency",
      "valueType": "number",
      "value": 20,
      "unit": "ms"
    }
  ],

  "_links": {
    "self": {
      "href": "/optimisation/opt-67890",
      "method": "GET"
    },
    "cancel": {
      "href": "/optimisation/opt-67890/cancel",
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

Retry creates a **new** `Optimisation`; it does not mutate the failed one back into processing.

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

POST /optimisation/{id}/cancel:
  requires If-Match
  missing If-Match -> 428
  stale/wrong If-Match -> 412

POST /optimisation/{id}/retry:
  requires If-Match
  missing If-Match -> 428
  stale/wrong If-Match -> 412
```

