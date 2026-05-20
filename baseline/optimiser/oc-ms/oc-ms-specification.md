# Optimisation-Controller-MS / OC MS Specification

## OC MS summary

Optimisation-Controller-MS (OC MS) owns the runtime `Optimisation` resource. It is a generic optimisation controller, not an intent-only controller. OC MS accepts runtime optimisation requests, validates only the wrapper and OD MS request contract, persists the request, emits `OptimisationRequestedEvent`, then later projects `OptimisationCompletedEvent` outcomes back into the runtime resource.

## Ownership

OC MS owns:

```text
Runtime Optimisation resource
Runtime lifecycle
Syntactic and OD-MS-contract validation
OC MS outbox write
Publishing worker instruction events to t7.optimisation.events
Inbox consumption of `OptimisationCompletedEvent` worker outcomes
Runtime result projection
Cancellation and retrial controls
```

OC MS does not own:

```text
OptimisationSpecification definitions
Gurobi model formulation
Python/Gurobi solver execution
Analytics platform datasets
Long-running intent control-loop assurance
```

## Endpoint set

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
DELETE /optimisation/{id}
```

Runtime `Optimisation` is an execution/audit record, not an editable draft definition.

## Runtime lifecycle

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
CANCELLING: Cancellation command has been accepted and worker should stop/ignore where safely possible.
CANCELLED: Optimisation is confirmed cancelled.
```

Runtime `Optimisation` does not expose a `version` field. ETag is used in HTTP headers for unsafe concurrency.

## Lifecycle transitions

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

## HATEOAS by lifecycle

```text
ACKNOWLEDGED / QUEUED / PROCESSING: self cancellation
CANCELLING: self
FAILED: self retrial
COMPLETED / INFEASIBLE / CANCELLED: self
```

## POST /optimisation

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
        "opt": "https://example.com/ontology/optimisation#"
      },
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
        "opt": "https://example.com/ontology/optimisation#"
      },
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

## OC MS validation boundary

OC MS validates:

```text
generic REST wrapper using its static API/OpenAPI contract
referenced OptimisationSpecification exists in OD MS
referenced OptimisationSpecification lifecycleStatus is ACTIVE
expression.expressionValue against the referenced ACTIVE OptimisationSpecification.targetEntitySchema
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

After acceptance, OC MS persists the runtime resource and writes `OptimisationRequestedEvent` with `instruction = EXECUTE` to its outbox in the same transaction. Cancellation uses the same event type with `instruction = CANCEL`. Worker terminal outcomes are returned through `OptimisationCompletedEvent` with `status = COMPLETED`, `FAILED`, or `INFEASIBLE`.

## Internal event baseline

OC MS uses exactly two internal Kafka event types with the Python/Gurobi worker in the current baseline. These are platform-internal events, not TMF external notification events.

| Event | Emitter | Consumer | Purpose | Key values |
|---|---|---|---|---|
| `OptimisationRequestedEvent` | OC MS / OC MS Outbox Relay | Python/Gurobi Worker | Worker instruction event for execution or cancellation. | `instruction = EXECUTE` or `instruction = CANCEL` |
| `OptimisationCompletedEvent` | Python/Gurobi Worker | OC MS / OC MS Inbox Consumer | Terminal worker outcome event for lifecycle/result projection. | `status = COMPLETED`, `FAILED`, or `INFEASIBLE` |

`OptimisationFailedEvent` is not used in the current baseline. Failed and infeasible outcomes are carried by `OptimisationCompletedEvent.status`.

## GET /optimisation/{id}

```http
GET /optimisation/opt-12345
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "opt-12345-rev2"
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
        "opt": "https://example.com/ontology/optimisation#"
      },
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

## Cancellation and retrial

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

Retrial response creates a new Optimisation and links it to the failed optimisation:

```json
{
  "id": "opt-67890",
  "href": "/optimisation/opt-67890",
  "lifecycleStatus": "ACKNOWLEDGED",
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

## Header/concurrency rules

```text
POST /optimisation: returns Location and ETag
GET /optimisation/{id}: returns ETag
GET /optimisation: no per-item ETag by default; includes X-Total-Count and X-Result-Count
POST /optimisation/{id}/cancellation: requires If-Match
POST /optimisation/{id}/retrial: requires If-Match
missing If-Match -> 428
stale/wrong If-Match -> 412
```

## Outcome mapping

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```

`INFEASIBLE` is an optimisation outcome produced by the worker/model. It is not a request contract validation error.
