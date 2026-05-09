# OD MS / Optimisation-Definition-MS Specification

## Service purpose

Optimisation-Definition-MS / OD MS owns the governed catalogue of optimisation capabilities. OD MS defines what optimisation requests are allowed to look like.

OD MS does not execute optimisation, does not hold runtime request values, and does not store actual candidate resources from a request. OD MS is the definition/specification service. OC MS is the runtime execution/controller service.

## Ownership

OD MS owns:

```text
OptimisationSpecification resource
Optimisation capability metadata
Request contract definition
Constraint specification definitions
Target specification definitions
Preference specification definitions
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
Runtime expression values
Runtime context.targets[] values
Runtime context.constraints[] values
Runtime context.preferences[] values
Actual candidate resource instances
Candidate-resource selection
Solver feasibility evaluation
Gurobi model execution
Runtime optimisation outcome
```

## Endpoint set

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

## OptimisationSpecification resource shape

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
preferenceSpecifications[]
contextSpecifications[]
_links
@type
@baseType
@schemaLocation
```

## Lifecycle model

```text
DRAFT
ACTIVE
RETIRED
```

Rules:

```text
DRAFT:
  Specification is being prepared.
  Editable.
  Not usable for new runtime Optimisation creation.

ACTIVE:
  Specification can be used by OC MS to create runtime Optimisation resources.
  ACTIVE specifications are immutable except controlled lifecycle/version transition metadata.

RETIRED:
  Specification is no longer usable for new runtime Optimisation creation.
  It remains available for audit/history and existing Optimisation references.
```

There is no `DEPRECATED` state in the optimiser baseline.

## Version activation rule

```text
Only one ACTIVE OptimisationSpecification is allowed per specificationKey.
When a DRAFT specification is promoted to ACTIVE, OD MS must transactionally retire the previous ACTIVE specification with the same specificationKey.
```

## Definition versus runtime model

OD MS uses specification/definition sections:

```text
constraintSpecifications[]:
  Defines allowed hard-constraint fields.
  Does not contain caller-supplied runtime values.

targetSpecifications[]:
  Defines allowed optimisation targets and allowed/default values.
  Does not contain runtime optimisation results.

preferenceSpecifications[]:
  Defines allowed optimisation preferences.
  Does not contain runtime preference values.

contextSpecifications[]:
  Defines required context objects and their schemas.
  Defines candidate resource shape, cardinality, resourceAttributes, and metrics where applicable.
  Does not contain actual runtime candidate IDs.
```

OC MS uses runtime Optimisation expression values:

```text
expression.expressionValue.context.targets[]:
  Actual caller-supplied or defaulted target goals/thresholds.

expression.expressionValue.context.constraints[]:
  Actual caller-supplied constraint values.

expression.expressionValue.context.preferences[]:
  Actual caller-supplied preference values.
```

Validation mapping:

```text
runtime expression.expressionValue.context.targets[]     -> OD MS targetSpecifications[]
runtime expression.expressionValue.context.constraints[] -> OD MS constraintSpecifications[]
runtime expression.expressionValue.context.preferences[] -> OD MS preferenceSpecifications[]
runtime expression.expressionValue.context               -> OD MS contextSpecifications[]
```

## Contract validation rules

OC MS validates runtime Optimisation requests against the ACTIVE OptimisationSpecification.

OC MS validates:

```text
required fields
value types
supported constraint names
supported target names
supported preference names
supported context names
constraint/target/preference value types
context object schema
cardinality rules such as candidateResources minItems = 2 where applicable
```

OC MS does not validate:

```text
solver feasibility
candidate ranking
metric-vs-constraint fit
objective trade-off evaluation
best-candidate selection
```

## Canonical OptimisationSpecification example

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
      "name": "locationId",
      "valueType": "string",
      "required": true,
      "description": "Location scope for the optimisation."
    },
    {
      "name": "serviceClass",
      "valueType": "string",
      "required": true,
      "description": "Service class being optimised."
    },
    {
      "name": "redundancyRequired",
      "valueType": "boolean",
      "required": false,
      "description": "Whether redundant candidate handling is required."
    }
  ],
  "targetSpecifications": [
    {
      "name": "maxLatencyMs",
      "valueType": "number",
      "required": false,
      "unit": "ms",
      "description": "Maximum preferred latency target."
    },
    {
      "name": "minAvailabilityPercent",
      "valueType": "number",
      "required": false,
      "unit": "percent",
      "description": "Minimum preferred availability target."
    }
  ],
  "preferenceSpecifications": [
    {
      "name": "preferredAccessTechnology",
      "valueType": "string",
      "required": false
    },
    {
      "name": "optimiseFor",
      "valueType": "string",
      "required": false
    }
  ],
  "contextSpecifications": [
    {
      "name": "context",
      "valueType": "object",
      "required": true,
      "description": "Runtime optimisation context containing targets, constraints, and preferences arrays."
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

## Contract violation response

Use `422 Unprocessable Entity` when the JSON is structurally valid but violates the ACTIVE OptimisationSpecification request contract.

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_CONTRACT_VIOLATION",
  "reason": "Optimisation request violates specification contract",
  "message": "The optimisation expression.context does not satisfy the active OptimisationSpecification contract.",
  "status": 422,
  "@type": "Error"
}
```

## Relationship to OC MS

```text
OD MS: defines what is allowed.
OC MS: stores what was accepted at runtime.
Worker/model: decides feasibility and returns SUCCESS, INFEASIBLE, or FAILURE.
```

OD MS does not persist runtime Optimisation resources, does not write OC MS outbox records, does not consume Kafka worker outcomes, and does not project runtime results.
