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
| `POST /optimisationSpecification` | Always creates a new `DRAFT` specification. It does not directly create an `ACTIVE` specification. |
| `PUT /optimisationSpecification/{id}` | Approved platform extension. May fully replace/finalise a mutable `DRAFT`; it may also activate that `DRAFT` as part of a governed full-replacement operation. |
| `PATCH /optimisationSpecification/{id}` | Supported for TMF compatibility and JSON Merge Patch. May perform lifecycle-only activation when the `DRAFT` body is already final and fully valid. Do not use it for material contract replacement. |
| `DELETE /optimisationSpecification/{id}` | Allowed for `DRAFT`; for `ACTIVE`, prefer lifecycle transition to `RETIRED` rather than physical delete. |
| `GET` | Available for all lifecycle states. |

When an `OptimisationSpecification` is `ACTIVE`, changing the runtime contract should normally require a new versioned `DRAFT` specification rather than mutation of the active one.

Activation is a governed transition from `DRAFT` to `ACTIVE`. Before committing activation, OD MS must validate the full `OptimisationSpecification`, including `specCharacteristic[]`, `expressionSpecification`, and `targetEntitySchema`. When a new version becomes `ACTIVE`, OD MS must atomically move the previously `ACTIVE` version in the same specification family to `RETIRED`. There must be at most one `ACTIVE` version per specification family.


## PUT full replacement baseline — approved platform extension:

```http
PUT /optimisationSpecification/{id}
```

`PUT` is an approved platform extension. TMF921 defines `GET`, `POST`, `PATCH`, and `DELETE` for `IntentSpecification`; OD MS keeps those TMF-aligned operations intact and adds `PUT` only for controlled full replacement of mutable `DRAFT` optimiser specifications.

Purpose:

```text
Fully replace a mutable DRAFT OptimisationSpecification resource.
```

Rules:

| Rule | Decision |
|---|---|
| TMF status | Approved platform extension. |
| Allowed lifecycle state | `DRAFT` only. |
| Required concurrency control | `If-Match` is required. |
| Successful response | `200 OK` with the full updated representation. |
| Not allowed for | `ACTIVE` or `RETIRED` specifications. |
| Preferred for | Material contract replacement on `DRAFT` specifications. |
| Server-controlled fields | `id`, `href`, `creationDate`, and `lastUpdate` remain OD MS controlled. |

Use `PUT` rather than `PATCH` for material `DRAFT` contract changes such as replacing `targetEntitySchema`, replacing `expressionSpecification`, materially changing `specCharacteristic[]`, changing `version`, changing `validFor`, or replacing the specification description and catalogue metadata as a coherent whole. `PUT` may also activate a `DRAFT` if the request is explicitly governed and the complete replacement body is valid for activation.

Example request:

```http
PUT /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1
If-Match: "od-spec-v1"
Content-Type: application/json
```

```json
{
  "name": "Surgical Routing Optimisation Specification",
  "description": "Defines the allowed optimisation request contract for surgical routing optimisation.",
  "version": "1.0.1",
  "lifecycleStatus": "DRAFT",
  "validFor": {
    "startDateTime": "2026-05-09T00:00:00Z"
  },
  "isBundle": false,
  "specCharacteristic": [],
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JsonLdExpression",
    "iri": "https://example.com/ontology/optimisation/v1"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://example.com/schema/optimisation/v1/optimisation-expression-value.schema.json"
  },
  "@type": "OptimisationSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://example.com/schema/optimisation/v1/OptimisationSpecification.schema.json"
}
```

Example response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-v2"
Last-Modified: 2026-05-09T05:20:00Z
Content-Type: application/json
Cache-Control: private, no-cache
```

The response body returns the full updated `OptimisationSpecification` representation.

HATEOAS rule:

`replace` maps to `PUT /optimisationSpecification/{id}` and must be shown only when the current caller is authorised to fully replace a mutable `DRAFT` specification. Do not expose `replace` for `ACTIVE` or `RETIRED` specifications.

## PATCH partial update baseline — TMF-compatible but warned:

```http
PATCH /optimisationSpecification/{id}
```

`PATCH` is retained for TMF-style partial update compatibility. TMF921 requires JSON Merge Patch support for partial update operations and identifies `href`, `id`, `lastUpdate`, `@baseType`, `@schemaLocation`, and `@type` as non-patchable for `IntentSpecification`. OD MS follows that intent in optimiser terms.

Purpose:

```text
Apply a small, safe partial update to an OptimisationSpecification.
```

PATCH warning:

```text
PATCH must not be used as the normal mechanism for material runtime-contract replacement. Use PUT on a mutable DRAFT specification for full contract replacement.
```

OD MS allows `PATCH` mainly for small, safe updates such as:

```text
description
validFor
relatedParty[]
attachment[]
minor catalogue metadata corrections
explicitly governed lifecycle transitions such as DRAFT -> ACTIVE or ACTIVE -> RETIRED
```

Avoid `PATCH` for:

```text
full targetEntitySchema replacement
full expressionSpecification replacement
major specCharacteristic[] catalogue changes
version identity changes
ACTIVE runtime-contract mutation
uncontrolled lifecycle/version transitions
```

Non-patchable fields:

```text
id
href
creationDate
lastUpdate
@baseType
@schemaLocation
@type
```

Conditionally patchable fields:

```text
description
validFor
relatedParty[]
attachment[]
constraint[]
entitySpecRelationship[]
isBundle
name
version
lifecycleStatus
specCharacteristic[]
expressionSpecification
targetEntitySchema
```

Although TMF permits `expressionSpecification`, `specCharacteristic`, `targetEntitySchema`, and `version` to be patchable, OD MS treats material changes to those fields as governed operations. For a mutable `DRAFT`, prefer `PUT` when replacing them materially. For an `ACTIVE` specification, create a new versioned `DRAFT` instead of mutating the active runtime contract.

Example safe PATCH request:

```http
PATCH /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1
If-Match: "od-spec-v2"
Content-Type: application/merge-patch+json
```

```json
{
  "description": "Updated description for the surgical routing optimisation specification.",
  "validFor": {
    "startDateTime": "2026-05-09T00:00:00Z",
    "endDateTime": "2027-05-09T00:00:00Z"
  }
}
```

Example response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-v3"
Last-Modified: 2026-05-09T05:35:00Z
Content-Type: application/json
Cache-Control: private, no-cache
```

The response body returns the full updated `OptimisationSpecification` representation.

HATEOAS rule:

Expose `patch` only when the caller is authorised and the current lifecycle state allows partial update. Normally:

```text
DRAFT   -> may expose patch
ACTIVE  -> do not expose normal patch; may expose guarded retire action
RETIRED -> do not expose patch
```

## HATEOAS link baseline:

`_links` is an approved platform HATEOAS extension. It does not replace the TMF-style `href` field. OD MS must keep `href` as the standard resource hyperlink and use `_links` only to advertise valid next actions.

`_links` must be lifecycle-aware and authorisation-aware. It must expose only actions valid for the current caller and current `lifecycleStatus`.

Recommended link relations:

```text
self
collection
create
patch
replace
delete
activate
retire
createNewVersion
```

State-aware link baseline:

| Lifecycle state | Links normally exposed |
|---|---|
| `DRAFT` | `self`, `collection`, `patch`, `replace`, `delete`, `activate` |
| `ACTIVE` | `self`, `collection`, `retire`, `createNewVersion` |
| `RETIRED` | `self`, `collection`, `createNewVersion` |

Example `DRAFT` links:

```json
"_links": {
  "self": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "GET"
  },
  "collection": {
    "href": "/optimisationManagement/v1/optimisationSpecification",
    "method": "GET"
  },
  "patch": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "PATCH"
  },
  "replace": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "PUT"
  },
  "delete": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "DELETE"
  },
  "activate": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "PATCH"
  }
}
```

Example `ACTIVE` links:

```json
"_links": {
  "self": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "GET"
  },
  "collection": {
    "href": "/optimisationManagement/v1/optimisationSpecification",
    "method": "GET"
  },
  "retire": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "PATCH"
  },
  "createNewVersion": {
    "href": "/optimisationManagement/v1/optimisationSpecification",
    "method": "POST"
  }
}
```

Example `RETIRED` links:

```json
"_links": {
  "self": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "GET"
  },
  "collection": {
    "href": "/optimisationManagement/v1/optimisationSpecification",
    "method": "GET"
  },
  "createNewVersion": {
    "href": "/optimisationManagement/v1/optimisationSpecification",
    "method": "POST"
  }
}
```

## POST create OptimisationSpecification baseline:

```http
POST /optimisationSpecification
```

Purpose:

Creates a new `OptimisationSpecification` resource in `DRAFT` state. `POST` does not directly create an `ACTIVE` specification in the baseline OD MS governance model.

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

## Version activation rule:

```text
POST always creates DRAFT.
DRAFT -> ACTIVE is a governed transition.
Only one ACTIVE OptimisationSpecification is allowed per specification family.
When a DRAFT specification is promoted to ACTIVE, OD MS must transactionally retire the previous ACTIVE specification in the same specification family.
Activation must validate specCharacteristic[], expressionSpecification, and targetEntitySchema before committing the transition.
```

Activation can be performed in two ways:

```text
PATCH: use when the DRAFT body is already final and the request is lifecycle-only or small controlled metadata.
PUT: use when the caller is finalising/replacing the full mutable DRAFT body and requesting activation as part of that governed operation.
```

This keeps runtime optimisation runs auditable, repeatable, and explainable.

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

## HTTP concurrency and cache governance:

OD MS applies a platform HTTP governance layer on top of the TMF-aligned resource operations.

### Unsafe operation concurrency:

Unsafe operations are operations that can change server state. For OD MS this includes:

```http
POST   /optimisationSpecification
PUT    /optimisationSpecification/{id}
PATCH  /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

Concurrency rules:

| Operation | Request concurrency rule | Response rule |
|---|---|---|
| `POST /optimisationSpecification` | Does not require `If-Match` for normal server-assigned create because no existing resource representation is being mutated. | Returns `ETag` for the created `DRAFT` resource. |
| `PUT /optimisationSpecification/{id}` | Requires `If-Match` with the current resource `ETag`. | Returns updated `ETag`. |
| `PATCH /optimisationSpecification/{id}` | Requires `If-Match` with the current resource `ETag`, including governed activation and retire transitions. | Returns updated `ETag`. |
| `DELETE /optimisationSpecification/{id}` | Requires `If-Match` with the current resource `ETag`. | Returns `204 No Content` on success. |

OD MS must reject missing or stale preconditions for existing-resource mutations:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
```

```json
{
  "code": "PRECONDITION_REQUIRED",
  "reason": "IF_MATCH_REQUIRED",
  "message": "This operation requires If-Match with the current OptimisationSpecification ETag.",
  "status": 428,
  "@type": "Error"
}
```

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied If-Match value does not match the current OptimisationSpecification ETag.",
  "status": 412,
  "@type": "Error"
}
```

### GET cache policy:

All OD MS `GET` operations return simple bounded cache metadata. `GET` remains read-only and may be cached for a bounded period.

Default response headers for successful `GET` operations:

```http
Cache-Control: private, max-age=300
ETag: "<current-resource-version>"
```

For collection `GET /optimisationSpecification`, `ETag` represents the selected collection view, including filters, paging, fields selection, and caller visibility. For item `GET /optimisationSpecification/{id}`, `ETag` represents the current resource representation.

Clients may force cache revalidation / cache override by sending:

```http
Cache-Control: no-cache
```

### HATEOAS interaction:

HATEOAS links for unsafe operations must imply the same precondition rules. For example, `replace`, `patch`, `activate`, `retire`, and `delete` links are only actionable when the caller supplies the current `ETag` in `If-Match`.

Example DRAFT link metadata:

```json
"_links": {
  "self": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "GET"
  },
  "replace": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "PUT",
    "requires": ["If-Match"]
  },
  "patch": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "PATCH",
    "requires": ["If-Match"]
  },
  "delete": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "DELETE",
    "requires": ["If-Match"]
  }
}
```

## DELETE /optimisationSpecification/{id}:

`DELETE /optimisationSpecification/{id}` is supported for TMF alignment and is governed by OptimisationSpecification lifecycle state.

### Request:

```http
DELETE /optimisationManagement/v1/optimisationSpecification/{id}
If-Match: "<current-resource-etag>"
```

### Lifecycle rules:

| Lifecycle state | DELETE behaviour |
|---|---|
| `DRAFT` | Allowed. Removes the mutable draft specification. |
| `ACTIVE` | Physical delete is not allowed. Use a governed lifecycle transition to `RETIRED`. |
| `RETIRED` | Normally not physically deleted. Retain for audit and historical runtime traceability. |

### Concurrency rules:

DELETE is an unsafe operation against an existing resource and therefore requires `If-Match`.

| Condition | Response |
|---|---|
| Missing `If-Match` | `428 Precondition Required` |
| Stale or mismatched `If-Match` | `412 Precondition Failed` |
| DRAFT deleted successfully | `204 No Content` |
| ACTIVE physical delete requested | `409 Conflict` or governed rejection response; caller should retire instead |
| RETIRED physical delete requested | `409 Conflict` unless an explicit administrative purge policy exists |

### Successful response:

```http
HTTP/1.1 204 No Content
```

### HATEOAS interaction:

`delete` is exposed only when the current caller is authorised and the specification is a mutable `DRAFT`.

```json
"_links": {
  "delete": {
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "method": "DELETE",
    "requires": ["If-Match"]
  }
}
```

For `ACTIVE` and `RETIRED` specifications, `delete` is not normally exposed. For `ACTIVE`, expose `retire` when the caller is authorised to perform lifecycle retirement.

### Baseline rule:

`DELETE /optimisationSpecification/{id}` is supported for TMF alignment. OD MS allows physical delete only for mutable `DRAFT` specifications. `ACTIVE` specifications must be retired through a governed lifecycle transition rather than physically deleted. `RETIRED` specifications are normally retained for audit and historical runtime traceability. DELETE requires `If-Match` and returns `204 No Content` on success.


## Error handling and status-code baseline:

OD MS uses TMF-style error responses with platform-specific error codes. The TMF standard operation shape remains intact; platform governance adds explicit concurrency and contract-validation errors where required.

### Core status codes:

| Status | Use |
|---|---|
| `200 OK` | Successful `GET`, `PATCH`, or approved-extension `PUT` returning a resource body. |
| `201 Created` | Successful `POST /optimisationSpecification`. |
| `204 No Content` | Successful `DELETE /optimisationSpecification/{id}`. |
| `400 Bad Request` | Invalid JSON, malformed request, invalid query parameter, or invalid `fields` syntax. |
| `401 Unauthorized` | Missing or invalid authentication. |
| `403 Forbidden` | Authenticated caller is not authorised for the requested operation or resource. |
| `404 Not Found` | Resource does not exist or is not visible to the caller. |
| `405 Method Not Allowed` | HTTP method is not supported for the target resource. |
| `409 Conflict` | Lifecycle, version, or specification-family conflict, including invalid activation/retirement conflict. |
| `412 Precondition Failed` | Supplied `If-Match` is stale or does not match the current resource `ETag`. |
| `415 Unsupported Media Type` | Request content type is unsupported. |
| `422 Unprocessable Entity` | JSON is syntactically valid but violates the OptimisationSpecification contract or governance rules. |
| `428 Precondition Required` | Required `If-Match` is missing on unsafe existing-resource operations. |
| `500 Internal Server Error` | Unexpected OD MS failure. |
| `503 Service Unavailable` | OD MS is temporarily unavailable. |

### Standard error body:

```json
{
  "code": "OPTIMISATION_SPEC_CONTRACT_VIOLATION",
  "reason": "OptimisationSpecification contract violation",
  "message": "targetEntitySchema must define expressionValue.context.targets, expressionValue.context.constraints, and expressionValue.context.preferences.",
  "status": 422,
  "@type": "Error"
}
```

### Concurrency error examples:

Missing `If-Match` on `PUT`, `PATCH`, or `DELETE` against an existing specification:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
```

```json
{
  "code": "PRECONDITION_REQUIRED",
  "reason": "Missing If-Match header",
  "message": "This operation requires If-Match with the current OptimisationSpecification ETag.",
  "status": 428,
  "@type": "Error"
}
```

Stale or mismatched `If-Match`:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETag mismatch",
  "message": "The supplied If-Match value does not match the current OptimisationSpecification ETag.",
  "status": 412,
  "@type": "Error"
}
```

### Baseline rule:

OD MS uses TMF-style error responses with platform-specific error codes. Unsafe existing-resource operations require `If-Match`; missing `If-Match` returns `428 Precondition Required`; stale or mismatched `If-Match` returns `412 Precondition Failed`. Valid JSON that violates the OD MS OptimisationSpecification contract returns `422 Unprocessable Entity`.
