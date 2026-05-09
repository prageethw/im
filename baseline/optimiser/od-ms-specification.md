# OD MS / Optimisation Definition MS Specification:

## Service purpose:

Optimisation Definition MS (OD MS) owns the governed catalogue of `OptimisationSpecification` resources.

An `OptimisationSpecification` defines the allowed shape, semantics, and validation contract for runtime `Optimisation` requests. It describes what an optimisation request may contain, including supported `context.targets[]`, `context.constraints[]`, and `context.preferences[]` structures.

OD MS does not execute optimisation runs, evaluate solver feasibility, select candidates, invoke Gurobi, persist runtime `Optimisation` resources, or project runtime optimisation outcomes. Those runtime responsibilities belong to OSB MS, OC MS, workers, and the optimiser engine.

External OD MS APIs are TMF921/TIO-aligned in structure and semantics, but the domain concept is `OptimisationSpecification` rather than `IntentSpecification`.

## Ownership:

OD MS owns:

```text
OptimisationSpecification resource
Optimisation capability metadata
Request contract definition
Expression specification metadata
Target entity schema for runtime Optimisation expressions
Specification characteristic catalogue for discovery and OEX/UI guidance
Specification lifecycle
Specification versioning
Specification list/retrieve/create/update/delete operations
```

OD MS does not own:

```text
Runtime Optimisation resources
Runtime expression values
Runtime expression.expressionValue.context.targets[] values
Runtime expression.expressionValue.context.constraints[] values
Runtime expression.expressionValue.context.preferences[] values
Actual candidate resource instances submitted in a runtime request
Candidate-resource selection
Solver feasibility evaluation
Gurobi model execution
Runtime optimisation outcome
Runtime optimisation result projection
```

## Endpoint set:

OD MS exposes the TMF-aligned operation set for `OptimisationSpecification`:

```http
GET    /optimisationSpecification
POST   /optimisationSpecification
GET    /optimisationSpecification/{id}
PATCH  /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

OD MS also exposes the following approved platform extension:

```http
PUT    /optimisationSpecification/{id}
```

`PUT` is retained as an approved platform extension for full replacement of mutable `DRAFT` `OptimisationSpecification` resources.

`PATCH` is supported for TMF-style partial update compatibility. Use `PATCH` carefully. Do not use `PATCH` for material contract changes such as replacing `targetEntitySchema`, replacing `expressionSpecification`, changing the characteristic catalogue, changing version identity, or performing major lifecycle/version transitions unless the operation is explicitly designed and guarded. Prefer `PUT` for full replacement of a mutable `DRAFT` specification.

OD MS does not expose runtime optimisation operations. Runtime operations belong to OC MS and OSB MS.

## OptimisationSpecification resource shape:

`OptimisationSpecification` is the optimiser-domain equivalent of the TMF921 `IntentSpecification` resource.

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
isBundle
specCharacteristic[]
expressionSpecification
targetEntitySchema
relatedParty[]
attachment[]
constraint[]
entitySpecRelationship[]
@type
@baseType
@schemaLocation
```

The external `OptimisationSpecification` resource uses TMF-aligned structures only. Optimiser request-contract semantics are represented through `targetEntitySchema`, `expressionSpecification`, and `specCharacteristic[]`.

## Field semantics:

| Field | Meaning |
|---|---|
| `id` | Unique identifier for the specification resource. |
| `href` | Hyperlink reference to the specification resource. |
| `name` | Human-readable specification name. |
| `description` | Description of the optimisation capability and contract. |
| `version` | Specification version. |
| `lifecycleStatus` | Specification lifecycle value: `DRAFT`, `ACTIVE`, or `RETIRED`. |
| `creationDate` | Date/time the specification resource was created. |
| `lastUpdate` | Date/time the specification resource was last updated. |
| `validFor` | Optional validity window for the specification. |
| `isBundle` | TMF-style bundle indicator. Default should be `false` unless explicitly modelling a bundle. |
| `specCharacteristic[]` | Discovery/catalogue metadata for supported optimisation fields and UI/OEX guidance. |
| `expressionSpecification` | Defines the expression language and ontology IRI for runtime optimisation expressions. |
| `targetEntitySchema` | Authoritative schema contract for runtime `Optimisation.expression.expressionValue`. |
| `relatedParty[]` | Parties or roles associated with the specification. |
| `attachment[]` | Optional attachments relevant to the specification. |
| `constraint[]` | Optional TMF-style references to governing policy/rule constraints. Not runtime `context.constraints[]`. |
| `entitySpecRelationship[]` | Relationships to other specification resources. |
| `@type` | TMF-style discriminator. Use `OptimisationSpecification`. |
| `@baseType` | TMF-style base type. Use `EntitySpecification`. |
| `@schemaLocation` | Optional schema location for platform extension details. |


## TMF-aligned specification responsibility split:

OD MS must keep the three TMF-aligned specification structures separate. They are related, but they do not mean the same thing.

| Structure | Responsibility | Must not be used for |
|---|---|---|
| `specCharacteristic[]` | Catalogue/discovery metadata for OEX/UI and API consumers. It advertises supported optimisation capability characteristics, examples, defaults, and display guidance. | It must not be treated as the authoritative validation schema. |
| `expressionSpecification` | Expression-language and ontology binding. It defines that runtime optimisation expressions use `JsonLdExpression` and the optimisation ontology IRI. | It must not contain runtime request values or detailed JSON validation rules. |
| `targetEntitySchema` | Authoritative validation contract for `Optimisation.expression.expressionValue`, including `context.targets[]`, `context.constraints[]`, and `context.preferences[]`. | It must not be replaced by catalogue characteristics or prose-only rules. |

Baseline rule:

```text
specCharacteristic[]      = catalogue / discovery / UI guidance
expressionSpecification   = expression language + ontology IRI
targetEntitySchema        = authoritative runtime expressionValue validation schema
```

This separation is mandatory in OD MS examples and operation descriptions. Do not blend characteristic metadata with expression language metadata, and do not use either of them as a substitute for `targetEntitySchema`.

## Optimisation context contract:

The runtime optimisation problem is carried inside:

```text
Optimisation.expression.expressionValue.context
```

Canonical runtime shape:

```json
{
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://example.com/ontology/optimisation/v1",
    "expressionValue": {
      "@context": {
        "opt": "https://example.com/ontology/optimisation#"
      },
      "context": {
        "targets": [],
        "constraints": [],
        "preferences": []
      }
    }
  }
}
```

Meaning:

| Runtime bucket | Meaning |
|---|---|
| `context` | The whole optimisation scenario / big picture. |
| `context.targets[]` | Optimisation goals the optimiser tries to achieve. |
| `context.constraints[]` | Hard mandatory requirements that must be satisfied. |
| `context.preferences[]` | Soft ranking or selection preferences used to choose between otherwise valid outcomes. |

OD MS defines this runtime contract using `targetEntitySchema`. `specCharacteristic[]` may describe these fields for discovery, governance, examples, defaults, and OEX/UI prefill guidance, but it must not replace the authoritative schema.


## Embedded schema artifact: optimisation-expression-value.schema.json

To avoid ambiguity, the `targetEntitySchema.@schemaLocation` reference used by `OptimisationSpecification` must be backed by the governed schema content below. The schema is documented inside this OD MS specification baseline so readers do not have to locate a separate artifact to understand the contract.

Logical schema artifact name:

```text
optimisation-expression-value.schema.json
```

Schema purpose:

```text
Validates Optimisation.expression.expressionValue for runtime Optimisation requests.
The authoritative optimisation problem container is expressionValue.context.
context.targets[] contains optimisation goals.
context.constraints[] contains hard mandatory requirements.
context.preferences[] contains soft ranking or selection preferences.
```

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schema/optimisation/v1/optimisation-expression-value.schema.json",
  "title": "Optimisation Expression Value",
  "description": "Schema for Optimisation.expression.expressionValue. The context object is the canonical container for the runtime optimisation problem definition.",
  "type": "object",
  "additionalProperties": true,
  "required": [
    "@context",
    "context"
  ],
  "properties": {
    "@context": {
      "description": "JSON-LD context for optimisation vocabulary prefixes.",
      "type": "object",
      "additionalProperties": true
    },
    "context": {
      "description": "The full optimisation scenario / big picture. Contains optimisation goals, hard requirements, and soft preferences.",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "targets",
        "constraints",
        "preferences"
      ],
      "properties": {
        "targets": {
          "description": "Optimisation goals the optimiser tries to achieve.",
          "type": "array",
          "minItems": 1,
          "items": {
            "$ref": "#/$defs/target"
          }
        },
        "constraints": {
          "description": "Hard mandatory requirements that must be satisfied for a valid solution.",
          "type": "array",
          "minItems": 1,
          "items": {
            "$ref": "#/$defs/constraint"
          }
        },
        "preferences": {
          "description": "Soft ranking or selection preferences used to choose between otherwise valid outcomes.",
          "type": "array",
          "items": {
            "$ref": "#/$defs/preference"
          }
        }
      }
    }
  },
  "$defs": {
    "target": {
      "type": "object",
      "additionalProperties": true,
      "description": "A goal or threshold the optimiser should optimise toward.",
      "properties": {
        "maxLatencyMs": {
          "type": "number",
          "minimum": 0
        },
        "minAvailabilityPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100
        }
      }
    },
    "constraint": {
      "type": "object",
      "additionalProperties": true,
      "description": "A hard requirement that every valid optimisation outcome must satisfy.",
      "properties": {
        "locationId": {
          "type": "string",
          "minLength": 1
        },
        "serviceClass": {
          "type": "string",
          "minLength": 1
        },
        "redundancyRequired": {
          "type": "boolean"
        }
      }
    },
    "preference": {
      "type": "object",
      "additionalProperties": true,
      "description": "A soft preference that influences ranking or selection among feasible outcomes.",
      "properties": {
        "preferredAccessTechnology": {
          "type": "string",
          "minLength": 1
        },
        "optimiseFor": {
          "type": "string",
          "minLength": 1
        }
      }
    }
  }
}
```

## Lifecycle model:

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
  Specification can be used by OC MS to validate and create runtime Optimisation resources.
  ACTIVE specifications are immutable except controlled lifecycle/version transition metadata.

RETIRED:
  Specification is no longer usable for new runtime Optimisation creation.
  It remains available for audit/history and existing Optimisation references.
```

There is no `DEPRECATED` state in the optimiser baseline.



## Operation governance:

| Operation | Rule |
|---|---|
| `POST /optimisationSpecification` | Creates a new `DRAFT` specification by default unless an explicitly governed activation workflow is used. |
| `PUT /optimisationSpecification/{id}` | Approved platform extension; full replacement of mutable `DRAFT` specifications only. |
| `PATCH /optimisationSpecification/{id}` | Supported for TMF compatibility and acceptable for small governed lifecycle-only updates such as `ACTIVE -> RETIRED`. Do not use it for material contract replacement such as replacing `targetEntitySchema`, replacing `expressionSpecification`, changing the characteristic catalogue, or changing version identity. |
| `DELETE /optimisationSpecification/{id}` | Allowed for `DRAFT`; for `ACTIVE`, prefer lifecycle transition to `RETIRED` rather than physical delete. |
| `GET` | Available for all lifecycle states. |

When an `OptimisationSpecification` is `ACTIVE`, changing the runtime contract should normally require a new versioned `DRAFT` specification rather than mutation of the active one.

## POST create OptimisationSpecification baseline:

```http
POST /optimisationSpecification
```

Purpose:

Creates a new `OptimisationSpecification` resource in `DRAFT` state by default, unless an explicitly governed activation workflow is used.

Minimum TMF-aligned create fields:

```text
name
@type
```

Recommended create body fields:

```text
description
version
validFor
isBundle
specCharacteristic[]
expressionSpecification
targetEntitySchema
@baseType
@schemaLocation
```

Client create requests must not supply server-controlled fields:

```text
id
href
creationDate
lastUpdate
```

OD MS assigns server-controlled fields when the resource is created. The created resource returns the full `OptimisationSpecification` representation, including server-generated `id`, `href`, `creationDate`, `lastUpdate`, lifecycle state, and TMF-style polymorphism fields.
 This keeps runtime optimisation runs auditable, repeatable, and explainable.

## Version activation rule:

```text
Only one ACTIVE OptimisationSpecification is allowed per specificationKey.
When a DRAFT specification is promoted to ACTIVE, OD MS must transactionally retire the previous ACTIVE specification with the same specificationKey.
```

## Retirement governance baseline:

`ACTIVE -> RETIRED` is a governed lifecycle transition for an `OptimisationSpecification`.

Retirement may be performed with `PATCH /optimisationSpecification/{id}` when the only change is `lifecycleStatus: RETIRED`. This is an acceptable small controlled lifecycle update. PATCH remains discouraged for material runtime-contract replacement, including changes to `targetEntitySchema`, `expressionSpecification`, `specCharacteristic[]`, or version identity.

`PUT /optimisationSpecification/{id}` remains an approved platform extension for full replacement or finalisation of mutable `DRAFT` specifications. It is not the normal mechanism for retiring an `ACTIVE` specification.

Physical `DELETE` is not used for `ACTIVE` or `RETIRED` specifications. Retired specifications remain available for audit, historical traceability, and existing runtime `Optimisation` references, but cannot be used for new runtime `Optimisation` creation.

### Retirement example:

```http
PATCH /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1
If-Match: "od-spec-surgical-routing-v1-r4"
Content-Type: application/merge-patch+json
```

```json
{
  "lifecycleStatus": "RETIRED"
}
```

```http
HTTP/1.1 200 OK
ETag: "od-spec-surgical-routing-v1-r5"
Content-Type: application/json
```

The response returns the full retired `OptimisationSpecification` representation. Its `_links` should expose only lifecycle-authorised read/new-version actions, such as `self`, `collection`, and `createNewVersion`.

## Definition versus runtime model:

OD MS uses TMF-aligned specification structures:

```text
expressionSpecification:
  Defines the supported expression language and ontology IRI.
  Does not contain runtime optimisation values.

targetEntitySchema:
  Defines the authoritative JSON/schema contract for runtime expression.expressionValue.
  Covers expression.expressionValue.context.targets[], constraints[], and preferences[].
  May define required fields, types, cardinality, allowed values, nested candidate resource shape, and object schemas.

specCharacteristic[]:
  Provides catalogue/discovery metadata and optional examples/defaults for supported fields.
  Helps OEX/UI consumers understand supported optimisation targets, constraints, and preferences.
  Does not replace targetEntitySchema as the validation source.
```

OC MS uses runtime `Optimisation` expression values:

```text
expression.expressionValue.context.targets[]:
  Actual caller-supplied or defaulted target goals/thresholds.

expression.expressionValue.context.constraints[]:
  Actual caller-supplied hard constraint values.

expression.expressionValue.context.preferences[]:
  Actual caller-supplied soft preference values.
```

Validation mapping:

```text
runtime expression.expressionValue.context -> OD MS targetEntitySchema
runtime context.targets[]                  -> targetEntitySchema properties for targets[]
runtime context.constraints[]              -> targetEntitySchema properties for constraints[]
runtime context.preferences[]              -> targetEntitySchema properties for preferences[]
```

## Contract validation rules:

OC MS validates runtime `Optimisation` requests against the `targetEntitySchema` of the `ACTIVE` `OptimisationSpecification`.

OC MS validates:

```text
required fields
value types
supported target names
supported constraint names
supported preference names
supported context object shape
allowed values where defined
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
  "isBundle": false,
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://example.com/ontology/optimisation/v1"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://example.com/schema/optimisation/v1/optimisation-expression-value.schema.json"
  },
  "specCharacteristic": [
    {
      "id": "SC-OPT-TARGETS-001",
      "name": "targets",
      "description": "Optimisation goals the optimiser tries to achieve.",
      "valueType": "array",
      "@type": "CharacteristicSpecification"
    },
    {
      "id": "SC-OPT-CONSTRAINTS-001",
      "name": "constraints",
      "description": "Hard mandatory requirements that must be satisfied.",
      "valueType": "array",
      "@type": "CharacteristicSpecification"
    },
    {
      "id": "SC-OPT-PREFERENCES-001",
      "name": "preferences",
      "description": "Soft ranking or selection preferences used to choose between valid outcomes.",
      "valueType": "array",
      "@type": "CharacteristicSpecification"
    }
  ],
  "@type": "OptimisationSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "/schema/OptimisationSpecification.schema.json"
}
```

## Contract violation response:

Use `422 Unprocessable Entity` when the JSON is structurally valid but violates the `ACTIVE` `OptimisationSpecification` request contract.

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_CONTRACT_VIOLATION",
  "reason": "Optimisation request violates specification contract",
  "message": "The optimisation expression.expressionValue.context does not satisfy the active OptimisationSpecification targetEntitySchema contract.",
  "status": 422,
  "@type": "Error"
}
```

## Relationship to OC MS:

```text
OD MS: defines what is allowed.
OC MS: stores what was accepted at runtime.
Worker/model: decides feasibility and returns SUCCESS, INFEASIBLE, or FAILURE.
```

OD MS does not persist runtime `Optimisation` resources, does not write OC MS outbox records, does not consume Kafka worker outcomes, and does not project runtime results.
