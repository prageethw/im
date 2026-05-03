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

## Corrected process view baseline:

The agreed runtime process view is:

```text
Consumer
-> OEX
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

Detailed interpretation:

```text
1. Consumer initiates the optimisation journey through OEX.
2. OEX routes the request to OGW.
3. OGW routes to OEX APIs.
4. OEX APIs route through OEX GW.
5. OEX GW routes to OEX Screen Builder MS.
6. OEX Screen Builder MS calls NGW.
7. NGW calls OC MS.
8. OC MS validates the runtime request against the ACTIVE OptimisationSpecification from OD MS.
9. OC MS persists the accepted runtime Optimisation in OC MS DB.
10. OC MS writes OptimisationRequestedEvent to OC MS Outbox in the same transaction.
11. OC MS Outbox relay publishes the event to Kafka.
12. Python/Gurobi Worker consumes the event from Kafka.
13. Python/Gurobi Worker invokes Gurobi Optimizer.
14. Worker publishes outcome event back to Kafka.
15. OC MS Inbox consumes the outcome event from Kafka.
16. OC MS Inbox updates OC MS DB with lifecycle/result projection.
17. Consumer polls GET /optimisation/{id} to retrieve current status/result.
```

Runtime request model:

```text
constraints[]
targets[]
context[]
```

Runtime contract validation:

```text
OC MS validates runtime constraints[], targets[], and context[] against the ACTIVE OD MS OptimisationSpecification.
OC MS validates structure, required fields, value types, supported names, supported enum values, and cardinality such as candidateResources minItems = 2.
OC MS does not perform solver feasibility, metric-vs-constraint evaluation, candidate ranking, or objective trade-off evaluation.
```

Outcome projection:

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```

Process view compliance rule:

```text
NGW-exposed OC MS and OD MS APIs are TMF-compliant.
OEX / OGW / OEX APIs / OEX GW / OEX Screen Builder MS are experience-layer/private integration components and do not need to be TMF-compliant.
Kafka events are internal contracts and do not need to be TMF-compliant unless separately required.
```

---

## Logical view baseline:

OC MS runtime logical path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

OC MS owns runtime Optimisation resources. It validates runtime requests against OD MS definitions, persists accepted executions, emits Kafka instructions, consumes worker outcomes, and projects lifecycle/result state.
