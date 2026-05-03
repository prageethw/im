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
