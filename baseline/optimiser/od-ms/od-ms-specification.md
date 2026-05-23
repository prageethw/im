# OD MS, Optimisation Definition MS Specification

## 1. Service purpose:

Optimisation Definition MS (OD MS) owns the governed catalogue of `OptimisationSpecification` resources. An `OptimisationSpecification` defines the allowed shape, semantics, lifecycle, and validation contract for runtime `Optimisation` requests.

It describes what a runtime optimisation request may contain, including the required `expression.expressionValue.context` container and its `targets[]`, `constraints[]`, and `preferences[]` buckets. External OD MS APIs are aligned to the TMF921 `IntentSpecification` resource and operation pattern, but the domain concept exposed by this optimiser architecture is `OptimisationSpecification`.

OD MS does **not** execute optimisation runs, evaluate solver feasibility, select candidates, invoke Gurobi, persist runtime `Optimisation` resources, or project runtime optimisation outcomes. Those runtime responsibilities belong to OSB MS, OC MS, workers, and the optimiser engine.

## 2. TMF alignment and platform extensions:

OD MS follows the TMF-style external resource model:

- `href` remains the standard resource hyperlink.
- `@type`, `@baseType`, `@schemaLocation`, and `@referredType` follow the TMF polymorphism and extension style.
- Standard external operations are `GET`, `POST`, `PATCH`, and `DELETE`.
- `PATCH` uses JSON Merge Patch semantics and requires `Content-Type: application/merge-patch+json`.
- `PUT` is an approved platform extension for full replacement and finalisation of mutable `DRAFT` specifications only.

Approved platform extensions:

| Extension | Purpose | Guardrail |
|---|---|---|
| `PUT /optimisationSpecification/{id}` | Full replacement and finalisation of mutable `DRAFT` specifications. | Requires `If-Match`; not allowed for `ACTIVE` or `RETIRED`. |
| `_links` | HATEOAS controls. | Does not replace `href`; lifecycle-aware and authorisation-aware. |
| `ETag` and `If-Match` governance | Optimistic concurrency for unsafe existing-resource operations. | Required for `PUT`, `PATCH`, and `DELETE`. |
| `x-platform-extension` and `x-tmf-native` response headers | Governance/documentation headers for NGW-facing optimiser-domain resources. | Used only on external NGW-facing OD/OC APIs; clients must not use these headers as business-logic switches. |

## 3. Ownership:

OD MS owns:

```text
OptimisationSpecification resource
Optimisation capability metadata
Request contract definition
Expression specification metadata
Target entity schema for runtime Optimisation expressions
Specification characteristic catalogue for discovery and OEX and UI guidance
Specification lifecycle
Specification activation and version assignment
Specification list, retrieve, create, update, and delete operations
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

## 4. Endpoint set:

TMF-aligned operation set:

```http
GET /optimisationSpecification
POST /optimisationSpecification
GET /optimisationSpecification/{id}
PATCH /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

Approved platform extension:

```http
PUT /optimisationSpecification/{id}
```

OD MS does not expose runtime optimisation operations. Runtime operations belong to OSB MS and OC MS.

## 5. OptimisationSpecification resource shape:

`OptimisationSpecification` is a platform optimiser-domain resource modelled using the TMF921 `IntentSpecification` and `EntitySpecification` pattern. It is not a native TMF921 resource name.

Canonical fields:

```text
id
href
name
description
familyId
draftId
version
lifecycleStatus
statusChangeDate
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
_links
```

Required create fields for `POST /optimisationSpecification`:

```text
name
familyId
expressionSpecification
targetEntitySchema
@type
```

Recommended create fields:

```text
description
validFor
isBundle
specCharacteristic[]
@baseType
@schemaLocation
```

Client create requests must not provide server-controlled fields:

```text
id
href
draftId
creationDate
lastUpdate
statusChangeDate
version
_links
```

`POST /optimisationSpecification` has two create modes. For a new specification lineage, the client omits `id` and `createFrom`; OD MS assigns `id` and `draftId`. For a new draft candidate under an existing lineage, the client provides `createFrom` with source `id` and `version`; OD MS reuses the existing `id` and assigns a new `draftId`.

For `createFrom` mode, `createFrom` is the only required client field. OD MS derives the initial draft candidate content from the referenced source version, including `name`, `familyId`, `expressionSpecification`, `targetEntitySchema`, `specCharacteristic[]`, and `@type`. Governance may allow selected fields to be overridden after the draft candidate is created while it remains `DRAFT`.

`version` is included in the canonical field set because it is present on `ACTIVE` and `RETIRED` specifications. Mutable `DRAFT` specifications do not expose an official public `version`. Each mutable draft candidate has a server-assigned `draftId`, and draft revision is represented by `ETag`. When a draft candidate is activated, the same `draftId` remains attached to the resulting `ACTIVE` and later `RETIRED` record as immutable provenance. `draftId` is therefore visible across the lifecycle. It selects a mutable candidate while the record is `DRAFT`, and may also support read-only provenance lookup after the record becomes `ACTIVE` or `RETIRED`.

`_links` is an approved HATEOAS platform extension. It does not replace the standard `href` field.

The external `OptimisationSpecification` resource must use only the TMF-aligned specification structures shown in the canonical field list. Optimiser request-contract semantics are represented through `targetEntitySchema`, `expressionSpecification`, and `specCharacteristic[]`.

## 6. Field semantics:

| Field | Meaning |
|---|---|
| `id` | Stable server-assigned `OptimisationSpecification` lineage identifier. It groups the current `ACTIVE` version, retained `RETIRED` versions, and mutable `DRAFT` candidates. A specific immutable `ACTIVE` or `RETIRED` specification version is selected by `id` and `version`. Because `draftId` is retained as provenance, OD MS may also support read-only lookup of `ACTIVE` and `RETIRED` records by `id` and `draftId`. A specific mutable draft candidate is selected by `id` and `draftId`. |
| `href` | Hyperlink reference to the specification resource. Server assigned. For DRAFT candidates, `href` must include or be accompanied by `draftId` when the link targets a specific mutable draft candidate. For `ACTIVE` and `RETIRED` versions, `href` resolves by `id` and optional `version`; read-only provenance lookup may additionally use `draftId` as a query filter. |
| `name` | Human-readable specification name. Required on create. |
| `description` | Description of the optimisation capability and contract. |
| `familyId` | Logical grouping metadata for related optimisation specifications. It supports discovery, reporting, and catalogue grouping, but OD MS must not use it as the lifecycle or versioning control key. |
| `draftId` | Server-assigned identifier for the draft candidate that produced the specification record. For `DRAFT` records, `draftId` is part of the mutable draft candidate identity and is required to select a specific draft. When the draft is activated, the same `draftId` is retained on the resulting `ACTIVE` and later `RETIRED` record as immutable provenance. It is not an official public version. It may be used for read-only provenance lookup of `ACTIVE` and `RETIRED` records, but must not be used for mutation, activation, deletion, or retirement. |
| `version` | Official specification version under the immutable `OptimisationSpecification.id`. Omitted for mutable `DRAFT`; assigned by OD MS only when a selected draft candidate is activated. Present and immutable for `ACTIVE` and `RETIRED` specifications. |
| `lifecycleStatus` | Specification lifecycle value: `DRAFT`, `ACTIVE`, or `RETIRED`. Created as `DRAFT` by default. |
| `statusChangeDate` | Date/time the `lifecycleStatus` last changed. Server assigned. |
| `creationDate` | Date/time the specification resource was created. Server assigned. |
| `lastUpdate` | Date/time the specification resource was last updated. Server assigned. |
| `validFor` | Optional validity window for the specification. |
| `isBundle` | TMF-style bundle indicator. Default should be `false` unless explicitly modelling a bundle. |
| `specCharacteristic[]` | Discovery/catalogue metadata for supported optimisation fields and OEX and UI guidance. |
| `expressionSpecification` | Defines the expression specification metadata for runtime optimisation expressions, including `@type`, `expressionType`, `expressionLanguage`, and ontology `iri`. |
| `targetEntitySchema` | Authoritative schema contract for runtime `Optimisation.expression.expressionValue`. |
| `relatedParty[]` | Parties or roles associated with the specification. |
| `attachment[]` | Optional attachments relevant to the specification. |
| `constraint[]` | Optional TMF-style references to governing policy/rule constraints. Not runtime `context.constraints[]`. |
| `entitySpecRelationship[]` | Relationships to other specification resources. |
| `@type` | TMF-style discriminator. Use `OptimisationSpecification`. |
| `@baseType` | TMF-style base type. Use `EntitySpecification`. |
| `@schemaLocation` | Optional schema location for platform extension details. |
| `_links` | Approved HATEOAS extension containing valid next actions for the current caller and lifecycle state. |

## 7. TMF-aligned specification responsibility split:

OD MS must keep the three TMF-aligned specification structures separate. They are related, but they do not mean the same thing.

| Structure | Responsibility | Must not be used for |
|---|---|---|
| `specCharacteristic[]` | Catalogue and discovery metadata for OEX and UI and API consumers. It advertises supported optimisation capability characteristics, examples, defaults, and display guidance. | It must not be treated as the authoritative validation schema. |
| `expressionSpecification` | Expression-language and ontology binding. It declares `@type = ExpressionSpecification`, `expressionType = JsonLdExpression`, `expressionLanguage = JSON-LD`, and the optimisation ontology `iri`. | It must not contain runtime request values or detailed JSON validation rules. |
| `targetEntitySchema` | Authoritative validation contract for `Optimisation.expression.expressionValue`, including `context.targets[]`, `context.constraints[]`, and `context.preferences[]`. | It must not be replaced by catalogue characteristics or prose-only rules. |

Baseline rule:

```text
specCharacteristic[] = catalogue, discovery, and UI guidance
expressionSpecification = expression type + expression language + ontology IRI
targetEntitySchema = authoritative runtime expressionValue validation schema
```

Runtime contract-selection rule:

```text
Runtime Optimisation creation requires both optimisationSpecification.id and expression.iri.
optimisationSpecification.id selects the exact governed OptimisationSpecification contract.
expression.iri identifies the submitted runtime expression semantics.
OC MS must verify that runtime expression.iri matches the referenced OptimisationSpecification.expressionSpecification.iri.
OC MS must validate expression.expressionValue against the referenced OptimisationSpecification.targetEntitySchema.
OC MS must not resolve or substitute the runtime contract by expression.iri alone.
```

The design-time `expressionSpecification` must not be confused with the runtime `expression` instance. `expressionSpecification` declares the expected expression type, expression language, and ontology for runtime requests. The runtime `Optimisation.expression` carries the actual `JsonLdExpression`, and `Optimisation.expression.expressionValue` carries the actual JSON-LD optimisation problem payload.

## 8. Runtime optimisation context contract:

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
        "opt": "https://example.com/ontology/optimisation#",
        "context": "opt:context",
        "targets": "opt:targets",
        "constraints": "opt:constraints",
        "preferences": "opt:preferences"
      },
      "@type": "opt:OptimisationProblem",
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
| `context` | The whole optimisation scenario, or big picture. |
| `context.targets[]` | Optimisation goals the optimiser tries to achieve. |
| `context.constraints[]` | Hard mandatory requirements that must be satisfied. |
| `context.preferences[]` | Soft ranking or selection preferences used to choose between otherwise valid outcomes. |

OD MS defines this runtime contract using `targetEntitySchema`. `specCharacteristic[]` may describe these fields for discovery, governance, examples, defaults, and OEX and UI prefill guidance, but it must not replace the authoritative schema.

## 9. Embedded schema artifact: optimisation-expression-value.schema.json:

To avoid ambiguity, the `targetEntitySchema.@schemaLocation` reference used by `OptimisationSpecification` is backed by the governed schema content below.

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
  "required": ["@context", "@type", "context"],
  "properties": {
    "@context": {
      "description": "JSON-LD context for optimisation vocabulary prefixes and canonical optimisation problem container terms.",
      "type": "object",
      "additionalProperties": true,
      "required": ["opt", "context", "targets", "constraints", "preferences"],
      "properties": {
        "opt": {
          "type": "string",
          "const": "https://example.com/ontology/optimisation#"
        },
        "context": {
          "type": "string",
          "const": "opt:context"
        },
        "targets": {
          "type": "string",
          "const": "opt:targets"
        },
        "constraints": {
          "type": "string",
          "const": "opt:constraints"
        },
        "preferences": {
          "type": "string",
          "const": "opt:preferences"
        }
      }
    },
    "@type": {
      "description": "JSON-LD type for the optimisation expression value.",
      "type": "string",
      "const": "opt:OptimisationProblem"
    },
    "context": {
      "description": "The full optimisation scenario, or big picture. Contains optimisation goals, hard requirements, and soft preferences.",
      "type": "object",
      "additionalProperties": false,
      "required": ["targets", "constraints", "preferences"],
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
          "description": "Hard mandatory requirements that must be satisfied for a valid solution. Concrete active OptimisationSpecification schemas decide whether this array may be empty for a given capability.",
          "type": "array",
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

## 10. Embedded schema governance baseline:

The embedded `optimisation-expression-value.schema.json` validates the runtime `Optimisation.expression.expressionValue` structure only. It does not perform solver feasibility checks, rank candidates, calculate objective trade-offs, select the best candidate, or decide runtime optimisation outcomes. Those responsibilities remain with OC MS, workers, and the optimiser engine.

| Schema element | Baseline rule |
|---|---|
| `expressionValue.@context` | Required JSON-LD context for optimiser ontology prefixes and canonical container terms: `context`, `targets`, `constraints`, and `preferences`. |
| `expressionValue.@type` | Required JSON-LD type. Baseline value is `opt:OptimisationProblem`. |
| `expressionValue.context` | Required object and canonical optimisation problem container. |
| `context.targets[]` | Required array containing optimisation goals. It should normally contain at least one target. |
| `context.constraints[]` | Required array containing hard mandatory requirements. Whether it may be empty is capability-specific and governed by the concrete active `OptimisationSpecification.targetEntitySchema`. |
| `context.preferences[]` | Required array containing soft ranking or selection preferences. It may be empty. |
| `$defs.target` | Reusable definition for target entries. |
| `$defs.constraint` | Reusable definition for hard-constraint entries. |
| `$defs.preference` | Reusable definition for soft-preference entries. |
| `additionalProperties` | Controlled container levels should be closed unless extension is explicitly intended; individual entry definitions may remain extensible where the capability schema allows domain-specific fields. |

## 11. Lifecycle model:

```text
DRAFT -> ACTIVE -> RETIRED
```

There is no `DEPRECATED` state in the optimiser baseline.

| Lifecycle state | Meaning | Edit/runtime rule |
|---|---|---|
| `DRAFT` | Specification is being prepared. | Editable. Not usable for new runtime `Optimisation` creation. No official public `version`; each draft candidate is identified by `draftId`, and revision is represented by `ETag`. |
| `ACTIVE` | Specification is approved for runtime use. | Immutable for contract and content changes. Used by OC MS to validate and create runtime `Optimisation` resources. May be moved to `RETIRED` only by governed lifecycle transition, normally when a replacement `DRAFT` for the same `OptimisationSpecification.id` is activated. |
| `RETIRED` | Specification is no longer available for new use. | Immutable retained history and audit record. Not editable and not usable for new runtime `Optimisation` creation. Existing runtime references may continue to resolve it for audit and explainability. |

Baseline immutability rule:

```text
Only DRAFT specifications are mutable.
ACTIVE specifications are contract and content immutable.
RETIRED specifications are fully immutable retained records.
To change an ACTIVE specification contract, create a new DRAFT candidate for the same `OptimisationSpecification.id` and activate one selected draft candidate.
OD MS assigns the official version during activation, not while the resource is still DRAFT.
`familyId` remains logical grouping metadata and must not drive activation, retirement, or official version uniqueness decisions.
```

## 12. Version activation and retirement governance:

Version governance baseline:

```text
DRAFT: no official public version; draftId identifies the mutable draft candidate and ETag represents draft revision and concurrency.
ACTIVE: official version is assigned at activation and is immutable; the source draftId is retained as provenance.
RETIRED: retains the assigned official version and source draftId and is immutable.
```

Version cardinality baseline for a given `OptimisationSpecification.id`:

```text
Zero or one ACTIVE version may exist.
Zero or many RETIRED versions may exist.
Zero or many mutable DRAFT candidates may exist.
Each DRAFT candidate has a server-assigned draftId and its own ETag.
When a DRAFT candidate is activated, its draftId is carried forward onto the resulting ACTIVE version and later RETIRED version as provenance.
Official version values must be unique across ACTIVE and RETIRED versions.
```

Multiple RETIRED versions are allowed and expected because existing runtime `Optimisation` records may reference older specification versions for audit, replay, explainability, and historical validation.

Multiple mutable DRAFT candidates are allowed for the same `OptimisationSpecification.id` so design alternatives can be prepared in parallel before one candidate is selected for activation. DRAFT candidates are not official versions. Each DRAFT candidate is selected by `draftId` and guarded by its own `ETag`. The selected draft candidate's `draftId` is carried forward after activation so the official version can be traced back to the draft that produced it.

DRAFT specifications do not expose an official public `version`; `draftId` identifies the candidate, while `ETag` represents revision and concurrency. ACTIVE and RETIRED specifications expose both `version` and source `draftId`: `version` is the official selector, while `draftId` is retained provenance that may also support read-only lookup. OD MS enforces only one ACTIVE version per `OptimisationSpecification.id`.

Identity and provenance sample:

| `id` | `draftId` | `version` | `lifecycleStatus` | Meaning |
|---|---|---:|---|---|
| `optimisation-spec-surgical-routing` | `od-draft-surgical-routing-a` | `1.0.0` | `RETIRED` | Old official version retained for audit. |
| `optimisation-spec-surgical-routing` | `od-draft-surgical-routing-b` | `1.1.0` | `ACTIVE` | Current official version used for new runtime creation. |
| `optimisation-spec-surgical-routing` | `od-draft-surgical-routing-c` | none | `DRAFT` | Mutable draft candidate being prepared. |

Selection rules:

```text
DRAFT candidate selection uses id and draftId.
ACTIVE and RETIRED official version selection uses id and version.
Default runtime selection by id resolves to the current ACTIVE version.
Read-only provenance lookup of ACTIVE and RETIRED records may use id and draftId.
draftId must not be used for mutation, activation, deletion, or retirement of ACTIVE or RETIRED records.
```

Version format baseline:

```text
Official version values use SemVer-compatible MAJOR.MINOR.PATCH format, for example 1.0.0.
The official version is assigned by OD MS during activation.
Client requests must not assign or change the official version.
Within an `OptimisationSpecification.id`, an official version value must be unique across ACTIVE and RETIRED versions as a server-side data-integrity invariant.
Because the official version is assigned by OD MS, clients cannot directly create a duplicate official version. If OD MS cannot safely assign a new official version because another activation is occurring for the same `OptimisationSpecification.id`, OD MS returns 409 Conflict for the concurrent activation conflict.
```

`POST /optimisationSpecification` supports two creation modes. A request without `createFrom` creates a new `OptimisationSpecification` lineage; OD MS assigns both `id` and `draftId`. A request with `createFrom` creates a new mutable `DRAFT` candidate under an existing `OptimisationSpecification.id`; OD MS reuses the existing `id`, assigns a new `draftId`, and does not assign an official public `version` until activation. In `createFrom` mode, `createFrom` is the only required client field; OD MS derives the starting draft contract from the referenced source version. In both modes OD MS assigns the draft candidate's initial `ETag`.

`DRAFT -> ACTIVE` is a governed activation transition on one selected `DRAFT` candidate. Activation may be performed by:

- `PATCH`, when the draft body is already final and only lifecycle activation is required.
- `PUT`, as an approved platform extension, when finalising/replacing the full mutable `DRAFT` contract as part of activation.

Activation rules:

```text
Only one ACTIVE version is allowed per `OptimisationSpecification.id`.
Activation is allowed only from a selected DRAFT candidate.
Activation validates the full OptimisationSpecification draft candidate before committing the lifecycle transition.
When a DRAFT candidate is promoted to ACTIVE, OD MS assigns the official version for that `OptimisationSpecification.id`, carries forward the selected candidate's `draftId` as provenance, and must transactionally retire any previous ACTIVE version for the same `OptimisationSpecification.id`.
The newly ACTIVE specification becomes contract and content immutable immediately after activation.
The previous ACTIVE specification becomes RETIRED and fully immutable as part of the same transaction.
Other DRAFT candidates for the same `OptimisationSpecification.id` remain DRAFT until explicitly deleted, superseded, or separately activated later.
```

`ACTIVE -> RETIRED` is a governed lifecycle transition, not a contract and content update. It is normally performed automatically when a replacement `DRAFT` candidate for the same `OptimisationSpecification.id` is activated. If a deployment allows explicit retirement, it must be lifecycle-only, require `If-Match`, update `statusChangeDate`, and must not change any contract fields.

`PUT` is not the mechanism for retiring an `ACTIVE` specification. `PUT` remains the approved platform extension for full replacement and finalisation of mutable `DRAFT` specifications only.

Physical `DELETE` is not used for `ACTIVE` or `RETIRED` specifications.

## 13. Operation governance summary:

| Operation | Rule |
|---|---|
| `GET /optimisationSpecification` | Lists visible specifications. Supports enumerated first-level filtering and `fields`. |
| `GET /optimisationSpecification/{id}` | Retrieves the current ACTIVE version by default. Historical versions require an explicit `version` query parameter. Draft candidates require explicit `lifecycleStatus=DRAFT` and `draftId` when retrieving one candidate. Supports first-level `fields`. |
| `POST /optimisationSpecification` | Creates a new mutable `DRAFT` candidate without an official public `version`. Without `createFrom`, OD MS creates a new lineage and assigns `id` and `draftId`; normal create fields are required. With `createFrom`, OD MS creates a new draft candidate under the referenced existing `id`, derives the starting contract from the source version, and assigns a new `draftId`; `createFrom` is the only required client field. Returns `draftId` and `ETag`. |
| `PUT /optimisationSpecification/{id}` | Approved platform extension. Full replacement and finalisation of a selected mutable `DRAFT` candidate only. For DRAFT candidate mutation, finalisation, and activation, `draftId` is required as a query parameter. Requires `If-Match` and `Content-Type: application/json`. Rejected for `ACTIVE` and `RETIRED`. |
| `PATCH /optimisationSpecification/{id}` | TMF-compatible partial update using JSON Merge Patch. Requires `If-Match` and `Content-Type: application/merge-patch+json`. Contract and content updates are allowed only for a selected `DRAFT` candidate. For DRAFT candidate mutation and activation, `draftId` is required as a query parameter. Retirement of `ACTIVE` is lifecycle-only, targets the current ACTIVE version for `id`, does not use `draftId`, and does not permit contract and content changes. Rejected for `RETIRED`. |
| `DELETE /optimisationSpecification/{id}` | Physical delete only for a selected mutable `DRAFT` candidate. Requires `draftId` as a query parameter and requires `If-Match`. Rejected for `ACTIVE` and `RETIRED`. |

## 14. Supported list filters:

`GET /optimisationSpecification` supports only the following first-level filters in the baseline:

| Query parameter | Meaning |
|---|---|
| `id` | Exact match on resource id. |
| `familyId` | Exact match on logical grouping metadata. |
| `draftId` | Exact match on a draft candidate identity. With `lifecycleStatus=DRAFT`, it selects a mutable draft candidate. With `ACTIVE` or `RETIRED`, it may be used for read-only provenance lookup. Official version selection remains by `id` and `version`. |
| `name` | Exact or implementation-defined case-insensitive name match. |
| `lifecycleStatus` | Exact match on `DRAFT`, `ACTIVE`, or `RETIRED`. |
| `version` | Exact match on official version. Meaningful only for `ACTIVE` and `RETIRED`. |
| `lastUpdate.gt`, `lastUpdate.lt` | Optional timestamp range filters for last update. |
| `statusChangeDate.gt`, `statusChangeDate.lt` | Optional timestamp range filters for lifecycle change date. |
| `fields` | Optional sparse fieldset projection. |

Unsupported or malformed query parameters return `400 Bad Request`. Requests combining `lifecycleStatus=DRAFT` with `version` are invalid and return `400 Bad Request`, because DRAFT candidates do not expose official public versions.

Default list resolution rule:

```text
When `id` is supplied without `version`, `lifecycleStatus`, or `draftId`, OD MS returns the current ACTIVE version for that `OptimisationSpecification.id` if one exists.
To retrieve historical records, callers must explicitly filter by `version`, `lifecycleStatus`, `draftId`, or an allowed combination.
To retrieve draft candidates, callers must explicitly filter by `lifecycleStatus=DRAFT`; to retrieve one draft candidate, callers must also provide `draftId`.
To retrieve an ACTIVE or RETIRED record by provenance, callers may provide `id`, `draftId`, and optionally `lifecycleStatus=ACTIVE` or `lifecycleStatus=RETIRED`.
If no ACTIVE version exists and no `version`, `lifecycleStatus`, or `draftId` filter is supplied, OD MS returns an empty list rather than silently returning DRAFT or RETIRED records.
```

Version and lifecycle filter examples:

```http
GET /optimisationSpecification?id=optimisation-spec-surgical-routing
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&lifecycleStatus=RETIRED
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&version=1.0.0
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&draftId=od-draft-surgical-routing-b
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&lifecycleStatus=RETIRED&draftId=od-draft-surgical-routing-a
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&lifecycleStatus=DRAFT
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&lifecycleStatus=DRAFT&draftId=od-draft-surgical-routing-a
```

Sparse field projection rule:

```text
If a requested field is valid but not present for the resource's current lifecycle state, OD MS omits that field silently rather than returning an error.
For example, fields=id,version on a DRAFT resource returns id and omits version because DRAFT specifications do not expose an official public version. Callers can request draftId for DRAFT records, and may also request draftId on ACTIVE or RETIRED records for provenance. A draftId filter on ACTIVE or RETIRED records is read-only provenance lookup and does not make draftId the official version selector.
Unsupported field names still return 400 Bad Request.
```

## 15. External response header governance:

OD MS external NGW-facing API responses include the following governance and documentation headers because `OptimisationSpecification` is an optimiser-domain platform resource that follows TMF-style conventions but is not a native TMF Open API resource:

```http
x-platform-extension: true
x-tmf-native: false
```

These headers apply to OD MS external API responses only. They are not used on internal Kafka events, database records, or private worker contracts.

Clients must not use these headers as runtime business-logic switches.

## 16. Concurrency and cache governance:

Unsafe existing-resource operations require optimistic concurrency:

```text
PUT /optimisationSpecification/{id}
PATCH /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

Required request header:

```http
If-Match: "<etag>"
```

Failure rules:

| Condition | Response |
|---|---|
| Missing `If-Match` on unsafe existing-resource operation | `428 Precondition Required` |
| Stale or mismatched `If-Match` | `412 Precondition Failed` |

For DRAFT candidate operations, `If-Match` must match the `ETag` of the selected `id` and `draftId` candidate. Missing `draftId` where it is required for DRAFT candidate retrieval, mutation, activation, or deletion returns `400 Bad Request`. An unknown `draftId` for the specified `id` returns `404 Not Found`. A stale or mismatched `If-Match` for the selected `id` and `draftId` candidate returns `412 Precondition Failed`. For ACTIVE retirement, `If-Match` must match the `ETag` of the current ACTIVE version for `id`; `draftId` is not used for ACTIVE retirement.

`POST /optimisationSpecification` creates a new server-assigned `DRAFT` candidate and does not normally require `If-Match`. It returns a `draftId` and an `ETag` for future updates to that candidate.

Successful GET responses include bounded private cache headers:

```http
Cache-Control: private, max-age=300
ETag: "<etag>"
```

The only explicit client cache override documented by OD MS is:

```http
Cache-Control: no-cache
```

The `private, max-age=300` posture is suitable for initial synchronous discovery/validation flows. OC MS may cache immutable `ACTIVE` specification contracts by `id` and `ETag`; because `ACTIVE` specifications are immutable, a cached contract for a specific `id` is safe. OC MS must not rely on a stale `familyId` lookup to infer the current active contract; runtime validation is against the referenced `OptimisationSpecification.id`.

## 17. HATEOAS baseline:

`_links` is an approved HATEOAS platform extension. It is lifecycle-aware and authorisation-aware. OD MS must expose only the links that are valid for the current caller and current lifecycle state.

`href` remains the standard TMF-style resource hyperlink and is not replaced by `_links`.

Lifecycle link visibility baseline:

| Lifecycle state | Links normally exposed |
|---|---|
| `DRAFT` | `self`, `collection`, `patch`, `replace`, `delete`, `activate` |
| `ACTIVE` | `self`, `collection`, `retire`, `createNewVersion` |
| `RETIRED` | `self`, `collection`, `createNewVersion` |

Link relation meaning:

| Link relation | Method | Meaning |
|---|---|---|
| `self` | `GET` | Retrieve this resource. |
| `collection` | `GET` | Return to collection/list. |
| `create` | `POST` | Create a new specification. Normally shown at collection level. |
| `patch` | `PATCH` | TMF-compatible partial update where authorised. |
| `replace` | `PUT` | Approved platform extension for full replacement of mutable `DRAFT`. |
| `delete` | `DELETE` | Delete mutable `DRAFT`. |
| `activate` | `PATCH` | Governed activation of a finalised `DRAFT`. |
| `retire` | `PATCH` | Governed retirement of an `ACTIVE` specification. |
| `createNewVersion` | `POST` | Create a new mutable `DRAFT` candidate for the same `OptimisationSpecification.id`. The POST body must include `createFrom` with source `id` and `version`, or the link-specific `href` must carry equivalent source context. The official `version` is assigned only when a draft candidate is activated. `familyId` may be retained as logical grouping metadata. |

The `activate` and `retire` link relations point to `PATCH` on the `OptimisationSpecification` resource itself. OD MS does not expose separate `/activate` or `/retire` action endpoints. DRAFT candidate action links must include `draftId` when the link targets a specific mutable draft candidate. `draftId` may be returned on ACTIVE and RETIRED records for provenance. ACTIVE and RETIRED links normally resolve official versions by `id` and optional `version`, or by `id` alone when resolving the current ACTIVE version. Read-only provenance lookup may additionally use `draftId`, but action links for ACTIVE and RETIRED must not use `draftId` for mutation. The `retire` link is lifecycle-only, targets the current ACTIVE version for `id`, does not use `draftId`, and must not be used to modify an `ACTIVE` specification contract and content.

## 18. Operation examples:

The examples below are internally consistent and should be used as the OD MS reference pattern.

### 18.1. POST /optimisationSpecification creates DRAFT:

Request:

```http
POST /optimisationManagement/v1/optimisationSpecification
Content-Type: application/json
```

```json
{
  "name": "Surgical Routing Optimisation Specification",
  "description": "Defines the allowed optimisation request contract for surgical routing optimisation.",
  "familyId": "optimisation-spec-surgical-routing",
  "validFor": {
    "startDateTime": "2026-05-09T00:00:00Z"
  },
  "isBundle": false,
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
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionType": "JsonLdExpression",
    "expressionLanguage": "JSON-LD",
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

Response:

```http
HTTP/1.1 201 Created
Location: /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?lifecycleStatus=DRAFT&draftId=od-draft-surgical-routing-a
ETag: "od-spec-surgical-routing-r1"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

```json
{
  "id": "optimisation-spec-surgical-routing",
  "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?lifecycleStatus=DRAFT&draftId=od-draft-surgical-routing-a",
  "draftId": "od-draft-surgical-routing-a",
  "name": "Surgical Routing Optimisation Specification",
  "description": "Defines the allowed optimisation request contract for surgical routing optimisation.",
  "familyId": "optimisation-spec-surgical-routing",
  "lifecycleStatus": "DRAFT",
  "statusChangeDate": "2026-05-09T04:10:00Z",
  "creationDate": "2026-05-09T04:10:00Z",
  "lastUpdate": "2026-05-09T04:10:00Z",
  "validFor": {
    "startDateTime": "2026-05-09T00:00:00Z"
  },
  "isBundle": false,
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
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionType": "JsonLdExpression",
    "expressionLanguage": "JSON-LD",
    "iri": "https://example.com/ontology/optimisation/v1"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://example.com/schema/optimisation/v1/optimisation-expression-value.schema.json"
  },
  "@type": "OptimisationSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://example.com/schema/optimisation/v1/OptimisationSpecification.schema.json",
  "_links": {
    "self": {
      "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?lifecycleStatus=DRAFT&draftId=od-draft-surgical-routing-a",
      "method": "GET"
    },
    "collection": {
      "href": "/optimisationManagement/v1/optimisationSpecification",
      "method": "GET"
    },
    "patch": {
      "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?draftId=od-draft-surgical-routing-a",
      "method": "PATCH"
    },
    "replace": {
      "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?draftId=od-draft-surgical-routing-a",
      "method": "PUT"
    },
    "delete": {
      "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?draftId=od-draft-surgical-routing-a",
      "method": "DELETE"
    },
    "activate": {
      "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?draftId=od-draft-surgical-routing-a",
      "method": "PATCH"
    }
  }
}
```

### 18.2. POST /optimisationSpecification creates draft candidate from existing version:

Request:

```http
POST /optimisationManagement/v1/optimisationSpecification
Content-Type: application/json
```

```json
{
  "createFrom": {
    "id": "optimisation-spec-surgical-routing",
    "version": "1.0.0"
  }
}
```

OD MS creates a new mutable DRAFT candidate for the same `OptimisationSpecification.id`, copies or derives the starting contract from the referenced immutable version according to platform governance, assigns a new `draftId`, and does not assign an official public `version` until activation. For `createFrom` mode, `createFrom` is the only required client field; fields such as `name`, `familyId`, `expressionSpecification`, `targetEntitySchema`, `specCharacteristic[]`, and `@type` are derived from the source version unless later changed under DRAFT governance.

Response body follows the same DRAFT response shape as section 18.1 and includes the new `draftId`, DRAFT `href`, and DRAFT action links that carry the selected `draftId`.

### 18.3. GET /optimisationSpecification list:

Request:

```http
GET /optimisationManagement/v1/optimisationSpecification?id=optimisation-spec-surgical-routing&fields=id,href,name,familyId,draftId,version,lifecycleStatus,statusChangeDate
Cache-Control: no-cache
```

Response:

```http
HTTP/1.1 200 OK
Cache-Control: private, max-age=300
ETag: "od-spec-list-r42"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

```json
[
  {
    "id": "optimisation-spec-surgical-routing",
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing",
    "name": "Surgical Routing Optimisation Specification",
    "familyId": "optimisation-spec-surgical-routing",
    "draftId": "od-draft-surgical-routing-a",
    "version": "1.0.0",
    "lifecycleStatus": "ACTIVE",
    "statusChangeDate": "2026-05-09T05:00:00Z",
    "@type": "OptimisationSpecification",
    "_links": {
      "self": {
        "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing",
        "method": "GET"
      },
      "collection": {
        "href": "/optimisationManagement/v1/optimisationSpecification",
        "method": "GET"
      },
      "retire": {
        "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing",
        "method": "PATCH"
      },
      "createNewVersion": {
        "href": "/optimisationManagement/v1/optimisationSpecification",
        "method": "POST"
      }
    }
  }
]
```

### 18.4. GET /optimisationSpecification/{id} retrieve ACTIVE by default:

Request:

```http
GET /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing
Cache-Control: no-cache
```

Response:

```http
HTTP/1.1 200 OK
Cache-Control: private, max-age=300
ETag: "od-spec-surgical-routing-r4"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

```json
{
  "id": "optimisation-spec-surgical-routing",
  "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing",
  "name": "Surgical Routing Optimisation Specification",
  "description": "Defines the allowed optimisation request contract for surgical routing optimisation.",
  "familyId": "optimisation-spec-surgical-routing",
  "draftId": "od-draft-surgical-routing-a",
  "version": "1.0.0",
  "lifecycleStatus": "ACTIVE",
  "statusChangeDate": "2026-05-09T05:00:00Z",
  "creationDate": "2026-05-09T04:10:00Z",
  "lastUpdate": "2026-05-09T05:00:00Z",
  "validFor": {
    "startDateTime": "2026-05-09T00:00:00Z"
  },
  "isBundle": false,
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
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionType": "JsonLdExpression",
    "expressionLanguage": "JSON-LD",
    "iri": "https://example.com/ontology/optimisation/v1"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://example.com/schema/optimisation/v1/optimisation-expression-value.schema.json"
  },
  "@type": "OptimisationSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://example.com/schema/optimisation/v1/OptimisationSpecification.schema.json",
  "_links": {
    "self": {
      "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing",
      "method": "GET"
    },
    "collection": {
      "href": "/optimisationManagement/v1/optimisationSpecification",
      "method": "GET"
    },
    "retire": {
      "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing",
      "method": "PATCH"
    },
    "createNewVersion": {
      "href": "/optimisationManagement/v1/optimisationSpecification",
      "method": "POST"
    }
  }
}
```

Historical version retrieval uses the same `id` with an explicit `version` filter:

```http
GET /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?version=1.0.0
Cache-Control: no-cache
```

OD MS returns the immutable `ACTIVE` or `RETIRED` version that matches the requested official version. It must not return a DRAFT resource for an official version lookup because DRAFT resources do not expose official public versions.

ACTIVE and RETIRED records may also be retrieved by source draft provenance:

```http
GET /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?draftId=od-draft-surgical-routing-a
Cache-Control: no-cache
```

OD MS returns the immutable `ACTIVE` or `RETIRED` official version produced from the supplied `draftId`, if the caller can see it. This is read-only provenance lookup. It does not make `draftId` the official version selector and must not be used for mutation, activation, deletion, or retirement.

### 18.5. GET /optimisationSpecification/{id} retrieve DRAFT candidate:

Request:

```http
GET /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?lifecycleStatus=DRAFT&draftId=od-draft-surgical-routing-a
Cache-Control: no-cache
```

OD MS returns the selected mutable DRAFT candidate. `GET /optimisationSpecification/{id}` without `version`, `lifecycleStatus`, or `draftId` returns the current ACTIVE version by default. `GET /optimisationSpecification/{id}?lifecycleStatus=DRAFT&draftId=...` returns a specific mutable draft candidate.

The returned DRAFT representation includes `draftId`, omits official public `version`, and exposes DRAFT action links containing the selected `draftId`.

### 18.6. PATCH activation of finalised DRAFT:

Request:

```http
PATCH /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?draftId=od-draft-surgical-routing-a
If-Match: "od-spec-surgical-routing-r3"
Content-Type: application/merge-patch+json
```

```json
{
  "lifecycleStatus": "ACTIVE"
}
```

The `draftId` query parameter selects the mutable DRAFT candidate being activated. OD MS assigns the official `version` as part of this activation transaction. Clients do not assign the official version while the specification is still `DRAFT`.

Response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-surgical-routing-r4"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

Response body returns the full activated resource, including the carried-forward `draftId` and the newly assigned official `version`. OD MS transactionally retires the previous `ACTIVE` version for the same `OptimisationSpecification.id`.

### 18.7. PUT finalise and activate mutable DRAFT:

Request:

```http
PUT /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?draftId=od-draft-surgical-routing-a
If-Match: "od-spec-surgical-routing-r3"
Content-Type: application/json
```

The `draftId` query parameter selects the mutable DRAFT candidate being replaced and optionally activated. The request body contains the full replacement mutable `DRAFT` `OptimisationSpecification` contract and may request activation. It must include all required client-controlled fields for the final contract. It must not include server-controlled fields such as `id`, `href`, `draftId`, `creationDate`, `lastUpdate`, `statusChangeDate`, `_links`, or official `version`.

```json
{
  "name": "Surgical Routing Optimisation Specification",
  "description": "Defines the allowed optimisation request contract for surgical routing optimisation.",
  "familyId": "optimisation-spec-surgical-routing",
  "lifecycleStatus": "ACTIVE",
  "validFor": {
    "startDateTime": "2026-05-09T00:00:00Z"
  },
  "isBundle": false,
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
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionType": "JsonLdExpression",
    "expressionLanguage": "JSON-LD",
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

OD MS assigns the official `version` as part of the activation transaction. Clients do not provide the official version while the specification is still `DRAFT`.

Response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-surgical-routing-r4"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

Response body returns the full activated resource, including the carried-forward `draftId` and the newly assigned official `version`. `PUT` is an approved platform extension and is allowed only for mutable `DRAFT` specifications.

### 18.8. PATCH retirement of ACTIVE:

Request:

```http
PATCH /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing
If-Match: "od-spec-surgical-routing-r4"
Content-Type: application/merge-patch+json
```

```json
{
  "lifecycleStatus": "RETIRED"
}
```

Response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-surgical-routing-r5"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

Response body returns the full retired `OptimisationSpecification`, including the original source `draftId` as provenance. This operation changes lifecycle metadata only; it must not alter any specification contract and content fields. `draftId` is not used for ACTIVE retirement because retirement targets the current ACTIVE version for `id`.

Retired specifications expose only lifecycle-authorised read/new-version links such as `self`, `collection`, and `createNewVersion`.

### 18.9. DELETE mutable DRAFT:

Request:

```http
DELETE /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?draftId=od-draft-surgical-routing-a
If-Match: "od-spec-surgical-routing-r1"
```

Response:

```http
HTTP/1.1 204 No Content
```

The `draftId` query parameter selects the mutable DRAFT candidate being deleted. Physical delete is allowed only for mutable `DRAFT` specifications. `ACTIVE` and `RETIRED` specifications are retained.

## 19. Error handling baseline:

OD MS uses TMF-style error responses with platform-specific error codes.

Core status codes:

| **Status** | **Use** |
|---|---|
| `200 OK` | Successful `GET`, `PATCH`, or approved platform-extension `PUT` with body. |
| `201 Created` | Successful `POST`. |
| `204 No Content` | Successful physical delete of a mutable `DRAFT` specification. |
| `400 Bad Request` | Invalid JSON, malformed request, invalid query parameter, or unsupported query parameter. |
| `401 Unauthorized` | Missing or invalid authentication. |
| `403 Forbidden` | Authenticated caller is not allowed. |
| `404 Not Found` | Resource not found or not visible to caller. |
| `405 Method Not Allowed` | HTTP method not supported for this resource. |
| `409 Conflict` | Lifecycle and version conflict, including ACTIVE or RETIRED mutation attempts or concurrent activation conflict for the same `OptimisationSpecification.id`. |
| `412 Precondition Failed` | `If-Match` is stale or mismatched. |
| `415 Unsupported Media Type` | Unsupported request content type. |
| `422 Unprocessable Entity` | Syntactically valid JSON violates OD MS `OptimisationSpecification` schema or targetEntitySchema contract rules. |
| `428 Precondition Required` | Missing required `If-Match` on unsafe existing-resource operation. |
| `500 Internal Server Error` | Unexpected OD MS failure. |
| `501 Not Implemented` | Operation or approved platform extension is not implemented or not enabled in this deployment. |
| `503 Service Unavailable` | OD MS temporarily unavailable. |

Boundary rules:

```text
ACTIVE or RETIRED contract or content mutation -> 409 Conflict
DRAFT contract and content update that fails OptimisationSpecification schema validation -> 422 Unprocessable Entity
targetEntitySchema or expressionSpecification contract-shape failure -> 422 Unprocessable Entity
concurrent activation conflict for the same `OptimisationSpecification.id` -> 409 Conflict
server-side official version uniqueness violation -> internal data-integrity failure; OD MS must roll back the activation transaction
unsupported PATCH Content-Type -> 415 Unsupported Media Type
unsupported query parameter -> 400 Bad Request
lifecycleStatus=DRAFT combined with version -> 400 Bad Request
missing draftId where required for DRAFT candidate retrieval, mutation, activation, or deletion -> 400 Bad Request
unknown draftId for the specified id -> 404 Not Found
stale or mismatched If-Match for selected (id, draftId) candidate -> 412 Precondition Failed
```

Immutable specification response:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_SPECIFICATION_IMMUTABLE",
  "reason": "OptimisationSpecification is immutable",
  "message": "Only DRAFT OptimisationSpecification resources can be changed. ACTIVE specifications are contract and content immutable and RETIRED specifications are fully immutable retained records.",
  "status": 409,
  "@type": "Error"
}
```

Concurrent activation conflict response:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_SPECIFICATION_ACTIVATION_CONFLICT",
  "reason": "Concurrent activation conflict",
  "message": "Another OptimisationSpecification activation is already in progress or has just completed for the same OptimisationSpecification id. Refresh the specification state and retry if still required.",
  "status": 409,
  "@type": "Error"
}
```

Unsupported media type response:

```http
HTTP/1.1 415 Unsupported Media Type
Content-Type: application/json
```

```json
{
  "code": "UNSUPPORTED_MEDIA_TYPE",
  "reason": "Unsupported media type",
  "message": "PATCH /optimisationSpecification/{id} requires Content-Type: application/merge-patch+json. PUT /optimisationSpecification/{id} requires Content-Type: application/json.",
  "status": 415,
  "@type": "Error"
}
```

Standard contract error body:

```json
{
  "code": "OPTIMISATION_SPEC_CONTRACT_VIOLATION",
  "reason": "OptimisationSpecification contract violation",
  "message": "targetEntitySchema must define expressionValue.context.targets, expressionValue.context.constraints, and expressionValue.context.preferences.",
  "status": 422,
  "@type": "Error"
}
```

## 20. Contract violation response:

Use `422 Unprocessable Entity` when the JSON is structurally valid but violates the OD MS `OptimisationSpecification` schema or the request-contract schema rules for `targetEntitySchema`, `expressionSpecification`, or `specCharacteristic[]`.

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_SPEC_CONTRACT_VIOLATION",
  "reason": "OptimisationSpecification contract violation",
  "message": "The submitted OptimisationSpecification does not satisfy the OD MS specification contract.",
  "status": 422,
  "@type": "Error"
}
```

## 21. Relationship to OC MS:

```text
OD MS: defines what is allowed.
OC MS: stores what was accepted at runtime.
Worker/model: decides feasibility/cancellation outcome and returns COMPLETED, INFEASIBLE, FAILED, or CANCELLED.
```

OC MS validates runtime `Optimisation` requests against the `targetEntitySchema` of the referenced `ACTIVE` `OptimisationSpecification`. Runtime creation requires both `optimisationSpecification.id` and `expression.iri`; OC MS uses the id as the exact contract pointer and verifies the runtime IRI against `OptimisationSpecification.expressionSpecification.iri`.

OC MS validates:

```text
required fields
value types
supported target names
supported constraint names
supported preference names
context object shape
allowed values where defined
cardinality rules such as candidateResources minItems = 2 where applicable
```

OC MS does not validate:

```text
solver feasibility
candidate ranking
metric and constraint fit
objective trade-off evaluation
best-candidate selection
```

OD MS does not persist runtime `Optimisation` resources, does not write OC MS outbox records, does not consume Kafka worker outcomes, and does not project runtime results.

---

## 22. Event and subscription posture:

OD MS is baselined as a synchronous REST API only for the initial optimiser architecture. TMF-style hub/listener subscription support is not included in the initial OD MS baseline. OD MS does not expose `/hub` endpoints and does not publish external `OptimisationSpecification` events by default. This is a deliberate scope decision.

Optimisation specifications support short-run optimisation models, and the initial runtime path can discover and validate against OD MS synchronously. OEX and OC MS may query OD MS directly for active `OptimisationSpecification` resources and their `targetEntitySchema` contracts.

A future TMF-style `/hub` subscription model may be introduced if concrete requirements emerge for external notification of specification creation, activation, retirement, or catalogue changes.

Until then, event support is deferred and must not be assumed by clients.
