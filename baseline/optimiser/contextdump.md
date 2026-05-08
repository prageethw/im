# Context Dump

> **Status:** Draft

## Table of contents:
- [Baseline: Reference books for Gurobi optimisation architecture exercise](#baseline-reference-books-for-gurobi-optimisation-architecture-exercise)
- [Baseline Update — REST HATEOAS, ETag Concurrency, and Cache-Control Position](#baseline-update-rest-hateoas-etag-concurrency-and-cache-control-position)
- [OD MS summary](#od-ms-summary)
- [OD MS endpoint set](#od-ms-endpoint-set)
- [OptimisationSpecification lifecycle](#optimisationspecification-lifecycle)
- [Version activation rule](#version-activation-rule)
- [Public OptimisationSpecification shape](#public-optimisationspecification-shape)
- [POST /optimisationSpecification](#post-optimisationspecification)
  - [Request](#request)
  - [Successful response](#successful-response)
- [GET /optimisationSpecification/{id}](#get-optimisationspecificationid)
  - [Request](#request-1)
  - [Response](#response)
- [GET /optimisationSpecification](#get-optimisationspecification)
  - [Request](#request-2)
  - [Response](#response-1)
- [PUT /optimisationSpecification/{id}](#put-optimisationspecificationid)
  - [Request](#request-3)
  - [Successful response](#successful-response-1)
  - [PUT failure responses](#put-failure-responses)
- [DELETE /optimisationSpecification/{id}](#delete-optimisationspecificationid)
  - [Request](#request-4)
  - [Successful response](#successful-response-2)
  - [DELETE rules](#delete-rules)
  - [DELETE failure responses](#delete-failure-responses)
- [HATEOAS by lifecycle state](#hateoas-by-lifecycle-state)
  - [DRAFT](#draft)
  - [ACTIVE](#active)
  - [RETIRED](#retired)
- [Header rules](#header-rules)
- [Key OD MS baseline summary](#key-od-ms-baseline-summary)
- [Baseline appended 2026-05-02T04:29:57 - Runtime Optimisation result visibility rule](#baseline-appended-2026-05-02t042957---runtime-optimisation-result-visibility-rule)
- [Baseline appended 2026-05-03T07:55:57 - Rebuilt OD MS specification as clean definition model](#baseline-appended-2026-05-03t075557---rebuilt-od-ms-specification-as-clean-definition-model)
- [Baseline appended 2026-05-03T08:08:22 - Shared location moved to topologySnapshot level](#baseline-appended-2026-05-03t080822---shared-location-moved-to-topologysnapshot-level)
- [Baseline appended 2026-05-03T10:53:26 - Corrected E2E logical integration sequence](#baseline-appended-2026-05-03t105326---corrected-e2e-logical-integration-sequence)
- [Baseline appended 2026-05-03T10:56:14 - E2E flows updated to corrected OEX/OGW/Screen Builder/NGW sequence](#baseline-appended-2026-05-03t105614---e2e-flows-updated-to-corrected-oexogwscreen-builderngw-sequence)
- [Baseline appended 2026-05-03T11:37:21 - Standardised User and UI wording](#baseline-appended-2026-05-03t113721---standardised-user-and-ui-wording)
- [Baseline appended 2026-05-03T21:47:00 - Infrastructure security controls captured in individual and E2E briefs](#baseline-appended-2026-05-03t214700---infrastructure-security-controls-captured-in-individual-and-e2e-briefs)
- [Baseline appended 2026-05-03T21:51:41 - Users wording and E2E summary security baseline](#baseline-appended-2026-05-03t215141---users-wording-and-e2e-summary-security-baseline)
- [Baseline appended 2026-05-03T23:57:53 - Applied global cleanup fixes](#baseline-appended-2026-05-03t235753---applied-global-cleanup-fixes)
- [Baseline appended 2026-05-04T00:02:50 - Added OSB MS under OEX layer in E2E solution summary](#baseline-appended-2026-05-04t000250---added-osb-ms-under-oex-layer-in-e2e-solution-summary)
- [Baseline appended 2026-05-08T05:59:04 - Logical view updated with OSB MS(OEX API)](#baseline-appended-2026-05-08t055904---logical-view-updated-with-osb-msoex-api)
- [Baseline appended 2026-05-08T06:02:45 - Re-applied visible logical and runtime process views](#baseline-appended-2026-05-08t060245---re-applied-visible-logical-and-runtime-process-views)
- [Baseline appended 2026-05-08T07:03:00 - Removed stale logical path with OWG](#baseline-appended-2026-05-08t070300---removed-stale-logical-path-with-owg)
- [Baseline appended 2026-05-08T07:05:13 - Removed stale process view with OEX APIs and OWG](#baseline-appended-2026-05-08t070513---removed-stale-process-view-with-oex-apis-and-owg)
- [Baseline appended 2026-05-08T08:12:37 - Re-added specification catalogue use case to E2E use case view](#baseline-appended-2026-05-08t081237---re-added-specification-catalogue-use-case-to-e2e-use-case-view)
- [Baseline appended 2026-05-08T08:21:59 - Added one-to-one use case sequence diagrams](#baseline-appended-2026-05-08t082159---added-one-to-one-use-case-sequence-diagrams)
- [Baseline appended 2026-05-08T08:37:48 - Added one-to-one process views for all use cases](#baseline-appended-2026-05-08t083748---added-one-to-one-process-views-for-all-use-cases)
- [Baseline appended 2026-05-08T09:50:50 - Moved seven process views under 3.3](#baseline-appended-2026-05-08t095050---moved-seven-process-views-under-33)
- [Baseline appended 2026-05-08T09:53:26 - Removed heading numbers from artefacts](#baseline-appended-2026-05-08t095326---removed-heading-numbers-from-artefacts)
- [Business context:](#business-context)
  - [Process view:](#process-view)
- [Business context:](#business-context-1)
  - [Process view:](#process-view-1)
- [Baseline appended 2026-05-08T09:59:06 - Restored logical view after heading cleanup](#baseline-appended-2026-05-08t095906---restored-logical-view-after-heading-cleanup)
- [Baseline appended 2026-05-08T11:00:04 - Draft status, table of contents, logical-before-process ordering](#baseline-appended-2026-05-08t110004---draft-status-table-of-contents-logical-before-process-ordering)
- [Baseline appended 2026-05-08T11:06:17 - Restored logical view diagram and logical view details](#baseline-appended-2026-05-08t110617---restored-logical-view-diagram-and-logical-view-details)
- [Baseline appended 2026-05-08T11:18:29 - Restored logical view as the section between use case and process view](#baseline-appended-2026-05-08t111829---restored-logical-view-as-the-section-between-use-case-and-process-view)
- [Baseline appended 2026-05-08T11:23:55 - Restored requested E2E runtime process view](#baseline-appended-2026-05-08t112355---restored-requested-e2e-runtime-process-view)

> **Status:** Draft

> **Status:** Draft

> **Status:** Draft

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
POST /optimisation/opt-12345/cancellation
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

## OD MS summary

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

## OD MS endpoint set

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

## OptimisationSpecification lifecycle

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

## Version activation rule

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

## Public OptimisationSpecification shape

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
  "context": [
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

## POST /optimisationSpecification

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
  "context": [
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
  "context": [
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

## GET /optimisationSpecification/{id}

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

  "context": [
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

## GET /optimisationSpecification

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

## PUT /optimisationSpecification/{id}

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

  "context": [
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

  "context": [
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

## DELETE /optimisationSpecification/{id}

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

## HATEOAS by lifecycle state

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

## Header rules

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
  POST /optimisation/{id}/cancellation
  POST /optimisation/{id}/retrial

Missing If-Match on unsafe operation:
  428 Precondition Required

Stale/wrong If-Match:
  412 Precondition Failed
```

## Key OD MS baseline summary

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
      "href": "/optimisation/opt-12345/cancellation",
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

## Baseline appended 2026-05-03T10:53:26 - Corrected E2E logical integration sequence

Baselined the E2E logical integration sequence as:

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

Rules:
- User authentication starts with Microsoft Entra ID SSO.
- OEX UI calls OEX APIs.
- OEX APIs are exposed through OGW.
- OGW routes to OEX Screen Builder MS.
- OEX Screen Builder MS integrates with NGW.
- NGW exposes TMF-compliant backend APIs for OD MS and OC MS.
- Runtime OC MS execution continues through Kafka, Python/Gurobi Worker, and Gurobi Optimizer.
- OD MS definition-management flows stop at OD MS and do not continue to Kafka/worker/optimizer unless a runtime optimisation is created through OC MS.

---

## Baseline appended 2026-05-03T10:56:14 - E2E flows updated to corrected OEX/OGW/Screen Builder/NGW sequence

Updated the active E2E process flows to follow the agreed sequence:

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

Key corrections:
- OEX UI appears before OEX APIs.
- OEX APIs are exposed through OGW.
- OGW routes to OEX Screen Builder MS.
- OEX Screen Builder MS calls NGW.
- NGW exposes TMF-compliant OD MS / OC MS backend APIs.
- Runtime OC MS flows continue to Kafka, Python/Gurobi Worker, and Gurobi Optimizer.
- OD MS definition flows stop at OD MS unless a runtime optimisation is created through OC MS.

---

## Baseline appended 2026-05-03T11:37:21 - Standardised User and UI wording

Updated active OD MS, OC MS, and E2E solution brief wording:
- Use `User` instead of `User`.
- Use `UI` instead of `UI`.

---

## Baseline appended 2026-05-03T21:47:00 - Infrastructure security controls captured in individual and E2E briefs

Confirmed that infrastructure access security controls must be captured in both:
- individual service design briefs
- the E2E solution brief

Updated:
- OD MS design brief with OD MS -> OD MS DB controls, plus cache/Kafka future-integration notes.
- OC MS design brief with OC MS -> OC MS DB, OC MS -> OD MS, and OC MS -> Kafka controls.
- E2E solution brief with cross-cutting infrastructure security requirements for service-to-database, service-to-cache, service-to-Kafka, and other platform infrastructure integrations.

---

## Baseline appended 2026-05-03T21:51:41 - Users wording and E2E summary security baseline

Updated wording:
- Replaced `Users` and common variants with `Users`.

Updated E2E solution summary to include the infrastructure security baseline:
- service-to-database, service-to-cache, service-to-Kafka, and other platform infrastructure integrations must explicitly capture security controls.
- required controls include authenticated service identity, least-privilege authorisation, encrypted connectivity, resource-level scoping, no broad wildcard/admin/root access, approved secret/certificate management and rotation, environment separation, audit/monitoring, and clear ownership of allowed operations.
- MS-to-Kafka controls include secured broker connectivity, service identity, Kafka ACLs, restricted DLQ permissions, CloudEvents-style headers, idempotent consumers, and monitoring/audit.
- MS-to-DB controls include authenticated, authorised, encrypted, least-privilege access with per-service database identities/roles.

---

## Baseline appended 2026-05-03T23:57:53 - Applied global cleanup fixes

Applied cleanup across all current optimisation artefacts.

Final active conventions:
```text
Runtime process:
  User -> OEX -> OGW -> OSB MS -> NGW -> OC MS -> OD MS -> OC DB -> Outbox -> Kafka -> Worker -> Gurobi -> Kafka

OSB access path:
User
-> OEX UI
-> OGW
-> OSB MS
-> NGW
-> OC MS
-> OD MS
```

Cleanup rules applied:
- No product-specific service mesh name for mTLS.
- No `OWG` wording; use `OWG` only where that separate gateway is still intentionally referenced.
- No stale `OEX APIs -> OWG -> OSB MS` hop in the OSB runtime process.
- No `User`; use `User` in the current baseline.
- No stale `/cancel` or `/retry` endpoint paths.
- No `cancellation` typo.
- Use `Gurobi Optimizer` consistently.

---

## Baseline appended 2026-05-04T00:02:50 - Added OSB MS under OEX layer in E2E solution summary

Updated the E2E solution summary to explicitly include the OEX layer:
- OEX UI provides the user-facing optimisation experience.
- OGW invokes OSB MS using mTLS and User Context JWT.
- OSB MS / Optimisation Screen Builder MS is the context-aware OEX facade/backend-for-frontend.
- OSB MS shapes screens/actions using User Context JWT, initially proxies runtime optimisation journeys to OC MS through NGW, and later supports governed OD MS catalogue/specification journeys through NGW.

---

## Baseline appended 2026-05-08T05:59:04 - Logical view updated with OSB MS(OEX API)

Updated logical view baseline to:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Definition logical path:
```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS
```

Runtime logical path:
```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Naming:
- Use `OSB MS(OEX API)` in logical views to show that OSB MS is the optimisation-specific OEX API/facade behind OGW.

---

## Baseline appended 2026-05-08T06:02:45 - Re-applied visible logical and runtime process views

Re-applied the visible logical view and runtime process view.

Logical view:
```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Runtime process view:
```text
User
-> OEX UI
-> OGW
-> OSB MS (OEX APIs)
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

---

## Baseline appended 2026-05-08T07:03:00 - Removed stale logical path with OWG

Removed stale E2E logical view:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Replaced with:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

---

## Baseline appended 2026-05-08T07:05:13 - Removed stale process view with OEX APIs and OWG

Removed stale process view:

```text
User
-> OEX UI
-> OGW
-> OSB MS (OEX APIs)
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

Replaced with:

```text
User
-> OEX UI
-> OGW
-> OSB MS (OEX APIs)
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

---

## Baseline appended 2026-05-08T08:12:37 - Re-added specification catalogue use case to E2E use case view

Re-added the governed specification/catalogue use case to the E2E use case view.

Use case:
```text
Manage optimisation catalogue
```

Clarification:
- In this optimisation platform, the governed specification resource is `OptimisationSpecification`.
- The use case covers create/update/activate/retire/govern `OptimisationSpecification` records.
- Access is restricted to approved optimisation domain engineers after agreement with broader E2E teams.

---

## Baseline appended 2026-05-08T08:21:59 - Added one-to-one use case sequence diagrams

Added a one-to-one sequence diagram section to the E2E solution brief.

Diagrams added for:
- Discover optimisation capability
- Manage optimisation catalogue
- Create runtime optimisation
- Monitor optimisation
- Cancellation optimisation
- Retrial failed optimisation
- Execute optimisation

Each diagram matches an E2E use case and uses the current OSB path: OEX UI -> OGW -> OSB MS (OEX APIs) -> NGW -> OD/OC.

---

## Baseline appended 2026-05-08T08:37:48 - Added one-to-one process views for all use cases

Added one-to-one process views for all seven E2E use cases:
- Discover optimisation capability
- Manage optimisation catalogue
- Create runtime optimisation
- Monitor optimisation
- Cancellation optimisation
- Retrial failed optimisation
- Execute optimisation

These are separate from the sequence diagrams and show ownership/process boundaries for each use case.

---

## Baseline appended 2026-05-08T09:50:50 - Moved seven process views under 3.3

Moved the seven one-to-one use-case process views into the E2E solution brief `### 3.3 Process view:` section and removed the separate duplicate process-view section.

3.3 now includes:
- 3.3.1 Discover optimisation capability
- 3.3.2 Manage optimisation catalogue
- 3.3.3 Create runtime optimisation
- 3.3.4 Monitor optimisation
- 3.3.5 Cancellation optimisation
- 3.3.6 Retrial failed optimisation
- 3.3.7 Execute optimisation

---

## Baseline appended 2026-05-08T09:53:26 - Removed heading numbers from artefacts

Removed numeric prefixes from Markdown headings across current artefacts.

Examples:
```text
## Business context:
### Process view:
#### Discover optimisation capability:
```

are now:
```text
## Business context:
### Process view:
#### Discover optimisation capability:
```

---

## Baseline appended 2026-05-08T09:59:06 - Restored logical view after heading cleanup

Restored the logical view sections after heading-number cleanup.

E2E/OSB logical view:
```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

OD MS has the definition logical path.
OC MS has the runtime logical path.

---

## Baseline appended 2026-05-08T11:00:04 - Draft status, table of contents, logical-before-process ordering

Updated artefacts to show `Status: Draft`, add a table of contents near the top, remove heading numbers, and keep the logical view before the process view where both sections exist.

---

## Baseline appended 2026-05-08T11:06:17 - Restored logical view diagram and logical view details

Restored logical view details and diagrams.

E2E and OSB now include:
- logical view diagram
- logical integration model
- definition-management logical path
- runtime-optimisation logical path
- logical responsibility table
- boundary rules
- API compliance rule

OD MS and OC MS now include service-focused logical diagrams and responsibility tables.

Logical view is placed before process view.

---

## Baseline appended 2026-05-08T11:18:29 - Restored logical view as the section between use case and process view

Restored the detailed logical view as `### Logical view:` between `### Use case view:` and `### Process view:` in the E2E solution brief.

Kept heading numbers removed while using the same placement that previously corresponded to section 3.2.

---

## Baseline appended 2026-05-08T11:23:55 - Restored requested E2E runtime process view

Rolled the E2E solution brief process view back to the version with the 18-step detailed runtime flow:
- User opens OEX UI
- OEX UI calls OGW
- OGW invokes OSB MS (OEX APIs) using mTLS and User Context JWT
- OSB MS calls NGW using mTLS and OAuth2 system-to-system
- NGW routes to OC MS
- OC MS validates against OD MS
- OC MS persists ACKNOWLEDGED state, writes OC MS Outbox, publishes to Kafka
- Python/Gurobi Worker invokes Gurobi Optimizer
- OC MS Inbox consumes outcome and updates OC MS DB
- User polls GET /optimisation/{id} through OEX UI -> OGW -> OSB MS (OEX APIs) -> NGW -> OC MS

---

## Baseline appended 2026-05-08T11:36:52 - E2E solution brief rolled back to GitHub commit

Rolled back `optimisation-e2e-solution-brief.md` to the GitHub commit version requested by the user:

```text
https://github.com/prageethw/im/blob/3f184867db74a6397ca3b67bc0ba062d9d0dd76e/baseline/optimiser/optimisation-e2e-solution-brief.md
```

A local backup of the immediately previous E2E file was created before replacing it.

---

## Baseline appended 2026-05-08T11:39:42 - Fixed E2E process view after GitHub rollback

Updated the E2E solution brief process view to:

```text
User
-> OGW
-> OSB MS(OEX API)
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

Also aligned the detailed interpretation to remove the OEX UI/OEX APIs/OWG hops from the runtime process view and use OGW -> OSB MS(OEX API) -> NGW.
