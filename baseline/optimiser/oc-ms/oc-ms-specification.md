# Optimisation Controller MS Specification

## 1. OC MS summary:

Optimisation-Controller-MS (OC MS) owns the runtime `Optimisation` resource. It is a generic optimisation controller, not an intent-only controller.

OC MS accepts runtime optimisation requests, validates the generic wrapper and the referenced OD MS request contract, persists the request, emits `OptimisationRequestedEvent`, and later projects `OptimisationCompletedEvent` outcomes back into the runtime resource.

OC MS validates runtime requests only against the currently referenced `ACTIVE` `OptimisationSpecification`. OD MS guarantees that `ACTIVE` and `RETIRED` specifications are immutable, so OC MS can treat the referenced `ACTIVE` specification contract as stable for the lifetime of the accepted runtime `Optimisation`.

OC MS does not use `familyId` or official specification `version` to select a runtime contract. Runtime validation is performed against the referenced `OptimisationSpecification.id`.

## 2. Ownership:

OC MS owns:

```text
Runtime Optimisation resource
Runtime lifecycle
Syntactic and OD-MS-contract validation
OC MS outbox write
Publishing worker instruction events to t7.optimisation.events
Inbox consumption of OptimisationCompletedEvent worker outcomes
Runtime result projection
Cancellation and retrial controls
```

OC MS does not own:

```text
OptimisationSpecification definitions
OptimisationSpecification lifecycle/version governance
Gurobi model formulation
Python/Gurobi solver execution
Analytics platform datasets
Long-running intent control-loop assurance
```

## 3. Endpoint set:

```http
GET /optimisation
POST /optimisation
GET /optimisation/{id}
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
```

Not supported:

```http
PUT /optimisation/{id}
PATCH /optimisation/{id}
DELETE /optimisation/{id}
```

Runtime `Optimisation` is an execution/audit record, not an editable draft definition.

## 4. Runtime lifecycle:

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

Rules:

```text
ACKNOWLEDGED: OC MS accepted the request, persisted the Optimisation resource, and wrote the outbox event.
QUEUED: OptimisationRequestedEvent has been published or is waiting for worker processing.
PROCESSING: Python/Gurobi worker has started processing.
COMPLETED: Worker completed successfully and produced a usable result.
INFEASIBLE: Worker completed correctly, but no valid solution exists.
FAILED: Technical/runtime failure occurred.
CANCELLING: Cancellation command has been accepted and worker should stop or ignore where safely possible.
CANCELLED: Optimisation is confirmed cancelled.
```

Runtime `Optimisation` does not expose a `version` field. ETag is used in HTTP headers for unsafe concurrency.

`statusChangeDate` records when `lifecycleStatus` last changed. It is distinct from `creationDate` and `lastUpdate`.

## 5. Lifecycle transitions:

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

Retrial does not move the failed Optimisation back to `PROCESSING`. It creates a new linked Optimisation with `retrialOf`.

## 6. HATEOAS by lifecycle:

```text
ACKNOWLEDGED / QUEUED / PROCESSING: self cancellation
CANCELLING: self
FAILED: self retrial
COMPLETED / INFEASIBLE / CANCELLED: self
```

## 7. External response header governance:

OC MS exposes optimiser-domain platform resources using TMF-style resource conventions. `Optimisation` is not a native TMF Open API resource.

All NGW-facing OC MS resource responses include:

```http
x-platform-extension: true
x-tmf-native: false
```

These headers are governance/documentation indicators only. Clients must not use them as runtime business-logic switches.

## 8. POST /optimisation:

```http
POST /optimisation
Content-Type: application/json
```

```json
{
  "sourceContext": {
    "domain": "intent-management",
    "resource": {
      "id": "intent-789",
      "href": "/intentManagement/v5/intent/intent-789",
      "@type": "IntentRef",
      "@referredType": "Intent"
    }
  },
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice workload.",
  "priority": "1",
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://example.com/ontology/optimisation/v1",
    "expressionValue": {
      "@context": {
        "opt": "https://example.com/ontology/optimisation#",
        "context": "opt:context",
        "targets": "opt:targets",
        "constraints": "opt:constraints",
        "preferences": "opt:preferences"
      },
      "@type": "opt:OptimisationProblem",
      "context": {
        "targets": [
          {
            "maxLatencyMs": 20,
            "minAvailabilityPercent": 99.95
          }
        ],
        "constraints": [
          {
            "locationId": "melbourne-hospital-a",
            "serviceClass": "surgical-video",
            "redundancyRequired": true
          }
        ],
        "preferences": [
          {
            "preferredAccessTechnology": "5G",
            "optimiseFor": "lowest-latency"
          }
        ]
      }
    }
  },
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
x-platform-extension: true
x-tmf-native: false
```

```json
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
  "description": "Optimise path selection for hospital surgical slice workload.",
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
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://example.com/ontology/optimisation/v1",
    "expressionValue": {
      "@context": {
        "opt": "https://example.com/ontology/optimisation#",
        "context": "opt:context",
        "targets": "opt:targets",
        "constraints": "opt:constraints",
        "preferences": "opt:preferences"
      },
      "@type": "opt:OptimisationProblem",
      "context": {
        "targets": [
          {
            "maxLatencyMs": 20,
            "minAvailabilityPercent": 99.95
          }
        ],
        "constraints": [
          {
            "locationId": "melbourne-hospital-a",
            "serviceClass": "surgical-video",
            "redundancyRequired": true
          }
        ],
        "preferences": [
          {
            "preferredAccessTechnology": "5G",
            "optimiseFor": "lowest-latency"
          }
        ]
      }
    }
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
```

`202 Accepted` means OC MS accepted the request for asynchronous execution. It does not mean the optimisation is feasible, started, solvable, or guaranteed to produce a valid result.

## 9. OD specification lookup and cache posture:

On `POST /optimisation`, OC MS validates the runtime request against the referenced `OptimisationSpecification.id`.

Rules:

```text
The referenced OptimisationSpecification must exist.
The referenced OptimisationSpecification must be ACTIVE at request-acceptance time.
OC MS must not infer the current active contract by stale familyId lookup.
OC MS does not use familyId or official specification version to choose a runtime contract.
OC MS may cache immutable ACTIVE OptimisationSpecification contracts by id and ETag.
A cached ACTIVE contract for a specific id is safe because OD MS makes ACTIVE specifications immutable.
If the referenced specification is missing, not ACTIVE, cache-missing, or cache-stale beyond the local policy, OC MS refreshes from OD MS.
```

## 10. OC MS validation boundary:

OC MS validates:

```text
generic REST wrapper using its static API/OpenAPI contract
referenced OptimisationSpecification exists in OD MS
referenced OptimisationSpecification lifecycleStatus is ACTIVE
referenced ACTIVE OptimisationSpecification contract is immutable by OD MS lifecycle governance
expression wrapper shape:
  expression.@type = JsonLdExpression
  expression.@baseType = Expression
  expression.iri matches the specification ontology/model IRI where required
expression.expressionValue against the referenced ACTIVE OptimisationSpecification.targetEntitySchema
expression.expressionValue.@context contains the required optimiser ontology mappings
expression.expressionValue.@type = opt:OptimisationProblem
expression.expressionValue.context shape
expression.expressionValue.context.targets[] entries
expression.expressionValue.context.constraints[] entries
expression.expressionValue.context.preferences[] entries
cardinality and allowed values defined by targetEntitySchema
```

OC MS does not validate:

```text
optimisation semantics
solver feasibility
candidate selection
objective interpretation
Gurobi model validity
resource-selection correctness
```

After acceptance, OC MS persists the runtime resource and writes `OptimisationRequestedEvent` with `instruction = EXECUTE` to its outbox in the same transaction.

Cancellation uses the same event type with `instruction = CANCEL`. Worker terminal outcomes are returned through `OptimisationCompletedEvent` with `status = COMPLETED`, `FAILED`, or `INFEASIBLE`.

## 11. Internal event baseline:

OC MS uses exactly two internal Kafka event types with the Python/Gurobi worker in the current baseline. These are platform-internal events, not TMF external notification events.

| **Event** | **Emitter** | **Consumer** | **Purpose** | **Key values** |
|---|---|---|---|---|
| `OptimisationRequestedEvent` | OC MS / OC MS Outbox Relay | Python/Gurobi Worker | Worker instruction event for execution or cancellation. | `instruction = EXECUTE` or `instruction = CANCEL` |
| `OptimisationCompletedEvent` | Python/Gurobi Worker | OC MS / OC MS Inbox Consumer | Terminal worker outcome event for lifecycle/result projection. | `status = COMPLETED`, `FAILED`, or `INFEASIBLE` |

`OptimisationFailedEvent` is not used in the current baseline. Failed and infeasible outcomes are carried by `OptimisationCompletedEvent.status`.

## 12. GET /optimisation list:

Request:

```http
GET /optimisation?lifecycleStatus=PROCESSING&fields=id,href,lifecycleStatus,statusChangeDate
```

Supported first-level filters:

| Query parameter | Meaning |
|---|---|
| `id` | Exact match on runtime Optimisation id. |
| `lifecycleStatus` | Exact match on runtime lifecycle state. |
| `sourceContext.domain` | Exact match on source context domain where present. |
| `sourceContext.resource.id` | Exact match on source resource id where present. |
| `optimisationSpecification.id` | Exact match on referenced OptimisationSpecification id. |
| `creationDate.gt` / `creationDate.lt` | Optional creation timestamp range filters. |
| `lastUpdate.gt` / `lastUpdate.lt` | Optional last-update timestamp range filters. |
| `statusChangeDate.gt` / `statusChangeDate.lt` | Optional lifecycle-state-change timestamp range filters. |
| `fields` | Optional sparse fieldset projection. |

Unsupported or malformed query parameters return `400 Bad Request`.

Sparse field projection rule:

```text
If a requested field is valid but not present for the resource's current lifecycle state, OC MS omits that field silently rather than returning an error.
For example, fields=id,result on a PROCESSING resource returns id and omits result because result is not present before terminal outcome projection.
Unsupported field names still return 400 Bad Request.
```

Response headers:

```http
HTTP/1.1 200 OK
X-Total-Count: 1
X-Result-Count: 1
Content-Type: application/json
x-platform-extension: true
x-tmf-native: false
```

## 13. GET /optimisation/{id}:

```http
GET /optimisation/opt-12345
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "opt-12345-rev2"
x-platform-extension: true
x-tmf-native: false
```

Active-state example:

```json
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",
  "name": "Hospital surgical slice path optimisation request",
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
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://example.com/ontology/optimisation/v1",
    "expressionValue": {
      "@context": {
        "opt": "https://example.com/ontology/optimisation#",
        "context": "opt:context",
        "targets": "opt:targets",
        "constraints": "opt:constraints",
        "preferences": "opt:preferences"
      },
      "@type": "opt:OptimisationProblem",
      "context": {
        "targets": [
          {
            "maxLatencyMs": 20,
            "minAvailabilityPercent": 99.95
          }
        ],
        "constraints": [
          {
            "locationId": "melbourne-hospital-a",
            "serviceClass": "surgical-video",
            "redundancyRequired": true
          }
        ],
        "preferences": [
          {
            "preferredAccessTechnology": "5G",
            "optimiseFor": "lowest-latency"
          }
        ]
      }
    }
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
```

No `result` field is included while `lifecycleStatus` is `ACKNOWLEDGED`, `QUEUED`, `PROCESSING`, or `CANCELLING`.

Completed-state example:

```json
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

## 14. Cancellation and retrial:

Cancellation:

```http
POST /optimisation/opt-12345/cancellation
If-Match: "opt-12345-rev2"
Content-Type: application/json
```

Retrial:

```http
POST /optimisation/opt-12345/retrial
If-Match: "opt-12345-rev3"
Content-Type: application/json
```

Cancellation and retrial responses include the OC external response governance headers:

```http
x-platform-extension: true
x-tmf-native: false
```

Retrial response creates a new Optimisation and links it to the failed optimisation:

```json
{
  "id": "opt-67890",
  "href": "/optimisation/opt-67890",
  "lifecycleStatus": "ACKNOWLEDGED",
  "statusChangeDate": "2026-05-02T04:00:00Z",
  "optimisationRelationship": [
    {
      "@type": "EntityRelationship",
      "relationshipType": "retrialOf",
      "id": "opt-12345",
      "@referredType": "Optimisation"
    }
  ]
}
```

## 15. Header/concurrency rules:

```text
POST /optimisation: returns Location and ETag
GET /optimisation/{id}: returns ETag
GET /optimisation: no per-item ETag by default; includes X-Total-Count and X-Result-Count
POST /optimisation/{id}/cancellation: requires If-Match
POST /optimisation/{id}/retrial: requires If-Match
missing If-Match -> 428
stale/wrong If-Match -> 412
```

NGW-facing OC MS resource responses include:

```http
x-platform-extension: true
x-tmf-native: false
```

Strict content type rules:

```text
POST /optimisation requires Content-Type: application/json.
POST /optimisation/{id}/cancellation requires Content-Type: application/json when a request body is sent.
POST /optimisation/{id}/retrial requires Content-Type: application/json when a request body is sent.
Unsupported request content type returns 415 Unsupported Media Type.
```

## 16. Error handling boundary:

| **Condition** | **Response** |
|---|---|
| Runtime expression or referenced `targetEntitySchema` contract failure | `422 Unprocessable Entity` |
| Referenced `OptimisationSpecification` is missing or not visible | `404 Not Found` |
| Referenced `OptimisationSpecification` is not `ACTIVE` | `422 Unprocessable Entity` |
| Cancellation/retrial requested in an invalid lifecycle state | `409 Conflict` |
| Missing `If-Match` on cancellation/retrial | `428 Precondition Required` |
| Stale or wrong `If-Match` on cancellation/retrial | `412 Precondition Failed` |
| Unsupported `Content-Type` | `415 Unsupported Media Type` |
| Malformed JSON, malformed query parameter, or unsupported query parameter | `400 Bad Request` |

Boundary rules:

```text
422 = request/expression/OD targetEntitySchema contract violation.
409 = runtime lifecycle/action conflict.
428 = required If-Match missing.
412 = supplied If-Match does not match current ETag.
415 = unsupported request media type.
400 = malformed request or unsupported query/filter parameter.
```

Contract violation example:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_CONTRACT_VIOLATION",
  "reason": "Optimisation contract violation",
  "message": "The submitted expression.expressionValue does not satisfy the referenced ACTIVE OptimisationSpecification targetEntitySchema.",
  "status": 422,
  "@type": "Error"
}
```

Lifecycle conflict example:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_LIFECYCLE_CONFLICT",
  "reason": "Optimisation lifecycle conflict",
  "message": "Cancellation is not allowed when lifecycleStatus is COMPLETED.",
  "status": 409,
  "@type": "Error"
}
```

Unsupported media type example:

```http
HTTP/1.1 415 Unsupported Media Type
Content-Type: application/json
```

```json
{
  "code": "UNSUPPORTED_MEDIA_TYPE",
  "reason": "Unsupported media type",
  "message": "POST /optimisation requires Content-Type: application/json.",
  "status": 415,
  "@type": "Error"
}
```

## 17. Outcome mapping:

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```

`INFEASIBLE` is an optimisation outcome produced by the worker/model. It is not a request contract validation error.
