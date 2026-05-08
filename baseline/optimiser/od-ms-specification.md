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

## Shared versus candidate-specific context attributes:

Shared context attributes should be modelled at the `topologySnapshot` level.

Candidate-specific attributes should be modelled under `candidateResources[].resourceAttributes` only when they vary per candidate.

For this example, `location.locationId` belongs at `topologySnapshot` level because all candidate paths belong to the same optimisation scope/location.

Do not repeat the same `locationId` under every candidate resource.

Example runtime context shape:

```json
{
  "name": "topologySnapshot",
  "valueType": "object",
  "value": {
    "dataset": "topology-snapshot",
    "version": "2026-05-02T10:00:00Z",
    "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z",
    "location": {
      "locationId": "melbourne-hospital"
    },
    "candidateResources": [
      {
        "resourceId": "path-001",
        "resourceType": "deliveryResource",
        "resourceClass": "low-latency-path",
        "metrics": []
      }
    ]
  }
}
```

---

## Process view participation baseline:

OD MS participates in the runtime process as the OptimisationSpecification definition source.

In the runtime process view:

```text
... -> NGW -> OC MS -> OD MS -> OC MS DB ...
```

OD MS provides the ACTIVE OptimisationSpecification used by OC MS for request-contract validation.

OD MS does not persist runtime Optimisation resources, does not write OC MS outbox records, does not consume Kafka worker outcomes, and does not project runtime results.

---

## Logical view baseline:

OD MS definition logical path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OD MS
```

OD MS also participates in runtime validation as the specification source:

```text
OC MS -> OD MS
```

OD MS does not participate in Kafka, Python/Gurobi Worker, Gurobi Optimizer, OC MS Inbox, or runtime result projection.

---

## Process view baseline:

OD MS participates in the runtime process as the OptimisationSpecification definition source.

Full runtime process reference:

```text
Consumer
-> OEX
-> OGW
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
-> Consumer polls GET /optimisation/{id}
```

OD MS role in this process:

```text
OC MS -> OD MS:
  OC MS uses OD MS to retrieve/validate against the ACTIVE OptimisationSpecification.

OD MS -> OC MS DB:
  OD MS does not call OC MS DB. This arrow in the process view means control returns to OC MS after specification validation, and OC MS then persists the accepted runtime Optimisation in OC MS DB.
```

OD MS does not persist runtime Optimisation resources, does not write OC MS outbox records, does not consume Kafka worker outcomes, and does not project runtime results.
