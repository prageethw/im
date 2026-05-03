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
  // Validated syntactically against OD MS OptimisationSpecification constraintSpecifications, targetSpecifications, and contextSpecifications.
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
  runtime constraints[], targets[], and context[] against the referenced ACTIVE OptimisationSpecification contract definitions.constraints, targets, and context

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

## OD definition versus OC runtime model baseline:

OD MS defines the contract using:

```text
constraintSpecifications[]
targetSpecifications[]
contextSpecifications[]
```

OC MS runtime Optimisation resources carry actual accepted values using:

```text
constraints[]
targets[]
context[]
```

OC MS validation mapping:

```text
runtime constraints[] -> OD constraintSpecifications[]
runtime targets[] -> OD targetSpecifications[]
runtime context[] -> OD contextSpecifications[]
```

OC MS validates structure, required fields, enum/value type rules, and cardinality against the ACTIVE OptimisationSpecification. This includes candidateResources minItems = 2 for selection optimisation.

OC MS does not perform solver feasibility, candidate ranking, metric-vs-constraint evaluation, or objective trade-off evaluation.

---

## Runtime E2E access path baseline:

OC MS runtime access follows this path before backend asynchronous execution:

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

OC MS sits behind NGW. OC MS does not directly authenticate end users. User authentication and user-context-aware routing occur through Entra ID SSO, OEX UI/APIs, OGW, OEX Screen Builder MS, and NGW.

OC MS validates the runtime request against OD MS, persists the Optimisation, emits Kafka events, and consumes worker outcomes.

---

## OC MS infrastructure security controls:

OC MS integrations must explicitly capture service-to-infrastructure security controls.

### OC MS -> OC MS Database:

```text
Authentication:
  OC MS connects using an authenticated OC MS service identity.

Authorisation:
  OC MS is authorised only for the OC MS database/schema/tables required for runtime Optimisation, lifecycle state, result projection, outbox, and inbox records.
  No broad database admin/root access by default.

Encrypted connectivity:
  OC MS database connectivity uses encrypted transport.
  mTLS or platform-approved encrypted database connectivity is used where supported by the selected database platform.

Secrets and certificates:
  Database credentials, keys, and certificates are stored in approved secret management.
  Rotation must be supported without application code changes where possible.

Environment separation:
  OC MS database principals, roles, schemas, and credentials are environment-scoped.
  Non-production OC MS identities must not access production OC MS data.

Audit and monitoring:
  Authentication failures, authorisation denials, privileged operations, unusual access patterns, outbox/inbox processing failures, and schema changes are logged and monitored.

Ownership:
  OC MS owns application-level access to runtime Optimisation, outbox, and inbox data.
  Database/platform teams own database platform controls.
```

### OC MS -> OD MS:

```text
Authentication:
  OC MS calls OD MS using an authenticated service identity.

Authorisation:
  OC MS is authorised only to retrieve/validate referenced OptimisationSpecification resources needed for runtime request validation.

Encrypted connectivity:
  OC MS calls OD MS over mTLS to validate the referenced ACTIVE OptimisationSpecification.

Secrets and certificates:
  Service credentials/certificates are managed through approved secret/certificate management and rotated.

Audit and monitoring:
  Failed authentication, denied authorisation, validation failures, and downstream dependency failures are logged and monitored.
```

### OC MS -> Kafka:

```text
Authentication:
  OC MS Outbox Relay and OC MS Inbox use authenticated service identities.

Encrypted connectivity:
  OC MS connects to Kafka brokers using TLS/mTLS.

Authorisation:
  Kafka ACLs enforce least-privilege access by topic and consumer group.

OC MS Outbox Relay:
  Allowed to WRITE worker instruction events.
  Allowed to DESCRIBE required topics.
  Not allowed broad wildcard topic access.

OC MS Inbox:
  Allowed to READ worker outcome events using the approved OC MS inbox consumer group.
  Allowed to DESCRIBE required topics.
  Not allowed to use worker consumer groups or write arbitrary topics.

DLQ:
  DLQ produce/read/replay permissions are restricted to approved service or operations identities.

Secrets and certificates:
  Kafka credentials, keys, and certificates are stored in approved secret management and rotated.

Audit and monitoring:
  Produce failures, consume failures, ACL denials, authentication failures, consumer lag, DLQ growth, and replay attempts are logged and monitored.
```

### OC MS -> platform cache, if introduced later:

```text
OC MS does not require a cache in the current baseline.

If a cache is introduced later, the OC MS design brief must capture:
  authenticated service identity
  least-privilege cache namespace/keyspace access
  encrypted connectivity
  approved secret/certificate management
  environment-scoped cache roles
  audit/monitoring of denied access and privileged operations
```

---

## Observability and monitoring telemetry baseline:

Each service design brief and the E2E solution brief must capture observability as more than application logging.

Observability includes:

```text
application logs
metrics
distributed traces
audit/security events
dependency telemetry
alertable operational signals
```

Correlation and trace propagation:

```text
accept correlation id / request id from the upstream caller where provided
generate a correlation id when missing
propagate correlation id to downstream service, database, cache, Kafka, and platform calls where applicable
propagate trace context where platform standards support it
preserve useful downstream correlation identifiers in logs/telemetry where approved
```

Application log baseline:

```text
request id / correlation id
service name
operation or endpoint
safe subject/user/service reference where applicable
resource id where applicable
dependency called
dependency status code or outcome
latency
authorisation decision result where applicable
error code/reason
```

Monitoring telemetry baseline:

```text
request count by endpoint/operation and status
latency by endpoint/operation and dependency
error rate by endpoint/operation and dependency
dependency failure counts
timeout and retry counts where applicable
authorisation allow/deny counts where applicable
token or credential validation failure counts where applicable
database connection and query failure counts where applicable
Kafka produce/consume failure counts where applicable
Kafka lag and DLQ growth where applicable
outbox/inbox backlog where applicable
cache hit/miss/error counts where applicable
```

Distributed tracing baseline:

```text
trace inbound service requests
trace outbound dependency calls
include correlation id and safe business/resource identifiers as trace attributes where approved
do not include sensitive token claims, secrets, credentials, or full private payloads in traces
```

Security/audit baseline:

```text
authentication failures
authorisation failures
privileged operation attempts
catalogue write/activation/retirement attempts where applicable
unsafe runtime action attempts such as cancellation and retrial where applicable
Kafka replay/DLQ actions where applicable
database privileged access or schema-change actions where applicable
```

Sensitive claims, full tokens, secrets, credentials, private payload data, and personal data beyond approved identifiers must not be logged or emitted as telemetry attributes.

---

## OC MS observability focus:

OC MS observability must include runtime optimisation, outbox, inbox, and worker outcome monitoring.

Additional OC MS signals:

```text
runtime Optimisation create/list/detail counts
contract validation failures including OPTIMISATION_CONTRACT_VIOLATION
lifecycle transition counts
SUCCESS / INFEASIBLE / FAILURE outcome counts
cancellation and retrial action counts
ETag / If-Match precondition failures
OC MS database dependency latency and failures
OC MS Outbox backlog and publish failures
OC MS Inbox lag and consume/project failures
Kafka produce/consume failure counts
DLQ growth and replay attempts
late/stale worker outcome handling counts
```
