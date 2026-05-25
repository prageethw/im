# Optimisation Definition MS Specification

**Document status:**

| **Field** | **Value** |
|---|---|
| **Status** | Baseline candidate |
| **Scope** | Optimisation Definition MS API and resource specification |
| **Source path** | `baseline/optimiser/od-ms/od-ms-specification.md` |
| **Source of truth** | GitHub `main` |
| **Last aligned** | 2026-05-24 |
| **Alignment scope** | Aligned with OD `specKey`, DRAFT `draftId`, ACTIVE retirement, and OC runtime contract-selection baseline. |

## Table of contents:

- [1. Service purpose](#1-service-purpose)
- [2. TMF alignment and platform extensions](#2-tmf-alignment-and-platform-extensions)
- [3. Ownership](#3-ownership)
- [4. Endpoint set](#4-endpoint-set)
- [5. OptimisationSpecification resource shape](#5-optimisationspecification-resource-shape)
- [6. Field semantics](#6-field-semantics)
- [7. TMF-aligned specification responsibility split](#7-tmf-aligned-specification-responsibility-split)
- [8. Runtime optimisation context contract](#8-runtime-optimisation-context-contract)
- [9. Embedded schema artifact: optimisation-expression-value.schema.json](#9-embedded-schema-artifact-optimisation-expression-valueschemajson)
- [10. Embedded schema governance baseline](#10-embedded-schema-governance-baseline)
- [11. Lifecycle model](#11-lifecycle-model)
- [12. Version activation and retirement governance](#12-version-activation-and-retirement-governance)
- [13. Operation governance summary](#13-operation-governance-summary)
- [14. Supported list filters](#14-supported-list-filters)
- [15. External response header governance](#15-external-response-header-governance)
- [16. Concurrency and cache governance](#16-concurrency-and-cache-governance)
- [17. HATEOAS baseline](#17-hateoas-baseline)
- [18. Operation examples](#18-operation-examples)
- [19. Error handling baseline](#19-error-handling-baseline)
- [20. Contract violation response](#20-contract-violation-response)
- [21. Relationship to OC MS](#21-relationship-to-oc-ms)
- [22. Event and subscription posture](#22-event-and-subscription-posture)

## 1. Service purpose:

Optimisation Definition MS (OD MS) owns the governed catalogue of `OptimisationSpecification` resources. An `OptimisationSpecification` defines the allowed shape, semantics, lifecycle, and validation contract for runtime `Optimisation` requests.

It describes what a runtime optimisation request may contain, including the required `expression.expressionValue.context` container and its `targets[]`, `constraints[]`, and `preferences[]` buckets. External OD MS APIs are aligned to the TMF921 `IntentSpecification` resource and operation pattern, but the domain concept exposed by this optimiser architecture is `OptimisationSpecification`.

OD MS does **not** execute optimisation runs, evaluate solver feasibility, select candidates, invoke Gurobi, persist runtime `Optimisation` resources, or project runtime optimisation outcomes. Those runtime responsibilities belong to OSB MS, OC MS, workers, and the optimiser engine.

## 2. TMF alignment and platform extensions:

OD MS follows the TMF-style external resource model. `OptimisationSpecification` is a platform resource model aligned to TMF resource conventions. It is not a native TMF Open API resource. Optimiser-specific fields, operations, headers, and link relations are allowed only when they are explicit, documented, and guarded as platform extensions.

- `href` remains the standard resource hyperlink.
- `@type`, `@baseType`, `@schemaLocation`, and `@referredType` follow the TMF polymorphism and extension style.
- Standard external operations are `GET`, `POST`, `PATCH`, and `DELETE`.
- `PATCH` uses JSON Merge Patch semantics and requires `Content-Type: application/merge-patch+json`.
- `PUT` is an approved platform extension for full replacement and finalisation of mutable `DRAFT` specifications only.

Approved platform extensions:

| Extension | Purpose | Guardrail |
|---|---|---|
| `specKey` | Stable logical specification key used by OD MS to resolve the server-assigned specification `id` for a DRAFT candidate. | Required on create; not used by OC MS for runtime contract selection. |
| `draftId` | Server-assigned mutable DRAFT candidate identifier and lifecycle provenance marker. | Selects DRAFT operations only; official runtime selection remains by `id` and `version` after activation. |
| `PUT /optimisationSpecification/draft/{draftId}` | Full replacement and finalisation of a mutable `DRAFT` candidate. | Requires `If-Match`; not allowed for `ACTIVE` or `RETIRED` official versions. |
| `DELETE /optimisationSpecification/{id}` | Logical retirement of the current `ACTIVE` version for a specification `id`. | Must not physically delete `ACTIVE` or `RETIRED` records. |
| `DELETE /optimisationSpecification/draft/{draftId}` | Physical deletion of an unused mutable `DRAFT` candidate. | Not allowed for `ACTIVE` or `RETIRED` official versions. |
| `_links` | HATEOAS controls. | Does not replace `href`; lifecycle-aware and authorisation-aware. |
| `ETag` and `If-Match` governance | HTTP header based optimistic concurrency for unsafe existing-resource operations. | Required for `PUT`, `PATCH`, and `DELETE`; ETags are headers, not JSON payload fields. |
| `x-platform-extension` and `x-tmf-native` response headers | Governance documentation headers for NGW-facing optimiser-domain resources. | Used only on external NGW-facing OD and OC APIs; clients must not use these headers as business-logic switches. |

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
DELETE /optimisationSpecification/{id}
GET /optimisationSpecification/draft/{draftId}
PATCH /optimisationSpecification/draft/{draftId}
DELETE /optimisationSpecification/draft/{draftId}
```

Approved platform extension:

```http
PUT /optimisationSpecification/draft/{draftId}
```

Endpoint responsibility:

| Operation | Target | Meaning |
|---|---|---|
| `GET /optimisationSpecification` | Collection | List visible DRAFT, ACTIVE, and RETIRED records according to filters and caller authorisation. |
| `POST /optimisationSpecification` | Collection | Create a mutable DRAFT candidate only. `specKey` is required; OD MS resolves `id` from `specKey` and assigns a new `draftId`. |
| `GET /optimisationSpecification/{id}` | Lineage current official version | Retrieve the current ACTIVE version by default, or an ACTIVE and RETIRED official version with `version`. Read-only provenance lookup may use `draftId`, but DRAFT candidate mutation and retrieval use `/optimisationSpecification/draft/{draftId}`. |
| `DELETE /optimisationSpecification/{id}` | Current ACTIVE official version | Retire the current ACTIVE version for the supplied `id`. This is a lifecycle retirement operation, not physical deletion. |
| `GET /optimisationSpecification/draft/{draftId}` | DRAFT candidate | Retrieve one mutable DRAFT candidate. |
| `PATCH /optimisationSpecification/draft/{draftId}` | DRAFT candidate | Partially update a mutable DRAFT candidate, or activate the selected DRAFT candidate. |
| `PUT /optimisationSpecification/draft/{draftId}` | DRAFT candidate | Fully replace and optionally activate a mutable DRAFT candidate. |
| `DELETE /optimisationSpecification/draft/{draftId}` | DRAFT candidate | Physically delete an unused mutable DRAFT candidate. |

OD MS does not expose runtime optimisation operations. Runtime operations belong to OSB MS and OC MS.

## 5. OptimisationSpecification resource shape:

`OptimisationSpecification` is a platform optimiser-domain resource modelled using the TMF921 `IntentSpecification` and `EntitySpecification` pattern. It is not a native TMF921 resource name.

Canonical fields:

```text
id
href
name
description
specKey
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
specKey
name
expressionSpecification
targetEntitySchema
@type
```

Additional recommended create fields:

```text
description
validFor
isBundle
specCharacteristic[]
@baseType
@schemaLocation
```

Client create requests must not provide these server-controlled fields:

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

`POST /optimisationSpecification` always creates a mutable `DRAFT` candidate. The client must provide `specKey`, but must not provide `id`, `draftId`, or `version`. OD MS assigns both the stable server-controlled `id` and the server-controlled `draftId` when the DRAFT candidate is created.

`specKey` is the mandatory stable logical specification key supplied when creating a DRAFT. OD MS uses `specKey` to resolve the server-assigned `OptimisationSpecification.id` for the draft candidate. If a current ACTIVE specification already exists for the same `specKey`, OD MS assigns the new DRAFT candidate to that existing `id`. If no current ACTIVE specification exists for the `specKey`, OD MS creates a new `id`. If only RETIRED versions exist for the `specKey` and no ACTIVE version exists, OD MS creates a new `id` unless a governed lineage-reuse capability is explicitly introduced later through governed platform change. Historical lineage continuity across retired-only `specKey` records is intentionally not automatic in the baseline; `specKey` can be used for discovery and reporting across such lineages.

`specKey` may be changed while the specification is still `DRAFT`, but only when OD MS validates the change against the current ACTIVE `OptimisationSpecification.id` for the new `specKey`. If an ACTIVE specification already exists for the new `specKey`, the DRAFT candidate's stored `id` must match that ACTIVE `id`. If it does not match, OD MS returns `409 Conflict`. OD MS must not use a `specKey` change to move a DRAFT candidate from one existing ACTIVE lineage to another.

`specKey` is also the active logical uniqueness key. At most one ACTIVE `OptimisationSpecification.id` may exist for a given `specKey`. If OD MS detects more than one ACTIVE lineage for the same `specKey`, that is a server-side data-integrity breach. OD MS must not guess which lineage to use; it must reject the operation, roll back any activation transaction, raise an operational alert, and require administrative remediation.

When `specKey` is changed on a DRAFT candidate, OD MS validates the changed value against the current ACTIVE `OptimisationSpecification.id` for that `specKey`. If an ACTIVE specification already exists for the changed `specKey`, the DRAFT candidate's stored `id` must match that ACTIVE `id`. If it does not match, OD MS returns `409 Conflict`. If no ACTIVE specification exists for the changed `specKey`, the change is allowed only when it does not move the DRAFT away from an existing ACTIVE lineage.

`id` identifies the specification lineage from DRAFT through ACTIVE and RETIRED states. DRAFT operations are addressed by `draftId`; official runtime contract selection after activation is by `id`.

`version` is included in the canonical field set because it is present on `ACTIVE` and `RETIRED` specifications. Mutable `DRAFT` specifications do not expose an official public `version`. Each mutable draft candidate has a server-assigned `draftId`, and draft revision is represented by `ETag`. When a draft candidate is activated, the same `draftId` remains attached to the resulting `ACTIVE` and later `RETIRED` record as immutable provenance. `draftId` is therefore visible across the lifecycle. It selects a mutable candidate while the record is `DRAFT`, and may also support read-only provenance lookup after the record becomes `ACTIVE` or `RETIRED`.

`_links` is an approved HATEOAS platform extension. It does not replace the standard `href` field.

The external `OptimisationSpecification` resource must use only the TMF-aligned specification structures shown in the canonical field list. Optimiser request-contract semantics are represented through `targetEntitySchema`, `expressionSpecification`, and `specCharacteristic[]`.

## 6. Field semantics:

| Field | Meaning |
|---|---|
| `id` | Stable server-assigned `OptimisationSpecification` lineage identifier resolved from `specKey` when a DRAFT candidate is created. It groups the current `ACTIVE` version, retained `RETIRED` versions, and mutable `DRAFT` candidates. A specific immutable `ACTIVE` or `RETIRED` version is selected by `id` and `version`. The current ACTIVE version is selected by `id` alone. A DRAFT candidate carries its `id`, but DRAFT operations are addressed by `draftId`. |
| `href` | Hyperlink reference to the specification record. Server assigned. The canonical DRAFT candidate `href` form is `/optimisationManagement/v1/optimisationSpecification/draft/{draftId}`. The canonical current ACTIVE `href` form is `/optimisationManagement/v1/optimisationSpecification/{id}`. A specific ACTIVE or RETIRED version may be retrieved with `/optimisationManagement/v1/optimisationSpecification/{id}?version={version}`. |
| `name` | Human-readable specification name. Required on create. |
| `description` | Description of the optimisation capability and contract. |
| `specKey` | Mandatory stable logical specification key supplied when creating a DRAFT. OD MS uses it to resolve the server-assigned `OptimisationSpecification.id` for the draft candidate. If a current ACTIVE specification already exists for the same `specKey`, the DRAFT is assigned to that existing `id`. If no ACTIVE version exists for the `specKey`, OD MS creates a new `id`. If only RETIRED versions exist for the `specKey`, OD MS also creates a new `id` unless governed lineage reuse is explicitly introduced later through governed platform change. `specKey` may be changed while the record remains DRAFT, but OD MS must validate the changed value against the current ACTIVE `OptimisationSpecification.id` for that `specKey`. At most one ACTIVE lineage may exist for a given `specKey`. |
| `draftId` | Server-assigned identifier for a mutable DRAFT candidate. For `DRAFT` records, `draftId` is the operation selector for retrieve, update, activation, and deletion. When the draft is activated, the same `draftId` is retained on the resulting `ACTIVE` and later `RETIRED` record as immutable provenance. It is not an official public version. |
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
| `expressionSpecification{}` | Expression-language and ontology binding. It declares `@type = ExpressionSpecification`, `expressionType = JsonLdExpression`, `expressionLanguage = JSON-LD`, and the optimisation ontology `iri`. | It must not contain runtime request values or detailed JSON validation rules. |
| `targetEntitySchema{}` | Authoritative validation contract for `Optimisation.expression.expressionValue`, including `context.targets[]`, `context.constraints[]`, and `context.preferences[]`. | It must not be replaced by catalogue characteristics or prose-only rules. |

Baseline rule:

```text
specCharacteristic[] = catalogue, discovery, and UI guidance
expressionSpecification{} = expression type + expression language + ontology IRI
targetEntitySchema{} = authoritative runtime expressionValue validation schema
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

The `example.com` IRIs and JSON-LD aliases in this embedded baseline are illustrative placeholders. The base schema validates the common optimisation expression container shape. Concrete `OptimisationSpecification.targetEntitySchema` artifacts may constrain the exact ontology IRI, JSON-LD aliases, and JSON-LD type values for a specific capability.

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
          "minLength": 1
        },
        "context": {
          "type": "string",
          "minLength": 1
        },
        "targets": {
          "type": "string",
          "minLength": 1
        },
        "constraints": {
          "type": "string",
          "minLength": 1
        },
        "preferences": {
          "type": "string",
          "minLength": 1
        }
      }
    },
    "@type": {
      "description": "JSON-LD type for the optimisation expression value.",
      "type": "string",
      "minLength": 1
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
| `expressionValue.@context` | Required JSON-LD context for optimiser ontology prefixes and canonical container terms: `context`, `targets`, `constraints`, and `preferences`. The base schema requires these bindings to be present but does not lock them to the illustrative `example.com` IRI or `opt:*` aliases. Concrete capability schemas may add exact `const` values where required. |
| `expressionValue.@type` | Required JSON-LD type. The base schema requires a non-empty type value. Concrete capability schemas may constrain the exact type, for example `opt:OptimisationProblem`, where that is part of the governed capability contract. |
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
![State chart](od-ms-lifecycle-state.svg)

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
`specKey` is used at DRAFT creation time to resolve the server-assigned `id`. While the record remains DRAFT, `specKey` may be changed only if OD MS validates the change against the current ACTIVE `OptimisationSpecification.id` for the new `specKey`. Activation, retirement, and official version uniqueness are governed by the resolved `OptimisationSpecification.id`. In addition, OD MS must enforce at most one current ACTIVE lineage per `specKey`; a duplicate ACTIVE lineage for the same `specKey` is a data-integrity breach.
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
Each DRAFT candidate has a server-assigned id, a server-assigned draftId, and its own ETag.
When a DRAFT candidate is activated, its draftId is carried forward onto the resulting ACTIVE version and later RETIRED version as provenance.
Official version values must be unique across ACTIVE and RETIRED versions.
```

Multiple RETIRED versions are allowed and expected because existing runtime `Optimisation` records may reference older specification versions for audit, replay, explainability, and historical validation.

Multiple mutable DRAFT candidates are allowed for the same `OptimisationSpecification.id` so design alternatives can be prepared in parallel before one candidate is selected for activation. DRAFT candidates are not official versions. Each DRAFT candidate is selected by `draftId` and guarded by its own `ETag`. The selected draft candidate's `draftId` is carried forward after activation so the official version can be traced back to the draft that produced it.

DRAFT specifications do not expose an official public `version`; `draftId` identifies the candidate, while `ETag` represents revision and concurrency. ACTIVE and RETIRED specifications expose both `version` and source `draftId`: `version` is the official selector, while `draftId` is retained provenance that may also support read-only lookup. OD MS enforces only one ACTIVE version per `OptimisationSpecification.id`.

`specKey` is the active logical uniqueness key. At most one ACTIVE `OptimisationSpecification.id` may exist for a given `specKey`. Activation must fail with `409 Conflict` if promoting a DRAFT would create more than one ACTIVE lineage for the same `specKey`, or if OD MS detects an existing duplicate ACTIVE-lineage state for that `specKey`. OD MS must roll back the activation transaction and raise an operational alert for remediation.

Identity and provenance sample:

| `id` | `draftId` | `version` | `lifecycleStatus` | Meaning |
|---|---|---:|---|---|
| `optimisation-spec-surgical-routing` | `od-draft-surgical-routing-a` | `1.0.0` | `RETIRED` | Old official version retained for audit. |
| `optimisation-spec-surgical-routing` | `od-draft-surgical-routing-b` | `1.1.0` | `ACTIVE` | Current official version used for new runtime creation. |
| `optimisation-spec-surgical-routing` | `od-draft-surgical-routing-c` | none | `DRAFT` | Mutable draft candidate being prepared. |

Selection rules:

```text
DRAFT candidate selection uses draftId.
Current ACTIVE selection uses id.
ACTIVE and RETIRED official version selection uses id and version.
Default runtime selection by id resolves to the current ACTIVE version.
draftId is retained as provenance on ACTIVE and RETIRED records.
Within a given OptimisationSpecification.id, a draftId can produce at most one ACTIVE or RETIRED official version.
```

Version format baseline:

```text
Official version values use SemVer-compatible MAJOR.MINOR.PATCH format, for example 1.0.0.
The official version is assigned by OD MS during activation.
Client requests must not assign or change the official version.
Within an `OptimisationSpecification.id`, an official version value must be unique across ACTIVE and RETIRED versions as a server-side data-integrity invariant.
Because the official version is assigned by OD MS, clients cannot directly create a duplicate official version. If OD MS cannot safely assign a new official version because another activation is occurring for the same `OptimisationSpecification.id`, OD MS returns 409 Conflict for the concurrent activation conflict.
```

`POST /optimisationSpecification` always creates a mutable `DRAFT` candidate without an official public `version`. The request must include `specKey` and must not include `id`, `draftId`, or `version`. OD MS resolves the server-assigned `id` from `specKey`, assigns a new `draftId`, and returns the draft candidate's initial `ETag`. If a current ACTIVE specification already exists for the same `specKey`, the DRAFT is assigned to that existing `id`. If no current ACTIVE specification exists for the `specKey`, OD MS creates a new `id`. If only RETIRED versions exist for the `specKey`, OD MS creates a new `id` unless governed lineage reuse is explicitly introduced later.

`DRAFT -> ACTIVE` is a governed activation transition on one selected `DRAFT` candidate addressed by `draftId`. Activation may be performed by:

- `PATCH`, when the draft body is already final and only lifecycle activation is required.
- `PUT`, as an approved platform extension, when finalising/replacing the full mutable `DRAFT` contract as part of activation.

Activation rules:

```text
Only one ACTIVE version is allowed per `OptimisationSpecification.id`.
Activation is allowed only from a selected DRAFT candidate.
Activation does not accept a target `id` override. The target lineage is the `id` already resolved and stored on the DRAFT candidate.
Activation validates the full OptimisationSpecification draft candidate before committing the lifecycle transition.
Activation must also validate the `specKey` active-uniqueness invariant. If activation would result in more than one ACTIVE `OptimisationSpecification.id` for the same `specKey`, or if OD MS detects an existing duplicate ACTIVE-lineage state for that `specKey`, OD MS must return `409 Conflict`, roll back the transaction, and raise an operational alert.
When a DRAFT candidate is promoted to ACTIVE, OD MS assigns the official version for that `OptimisationSpecification.id`, carries forward the selected candidate's `draftId` as provenance, and must transactionally retire any previous ACTIVE version for the same `OptimisationSpecification.id`.
The newly ACTIVE specification becomes contract and content immutable immediately after activation.
The previous ACTIVE specification becomes RETIRED and fully immutable as part of the same transaction.
Other DRAFT candidates for the same `OptimisationSpecification.id` remain DRAFT until explicitly deleted, superseded, or separately activated later.
```

`ACTIVE -> RETIRED` is a governed lifecycle transition, not a contract and content update. It is normally performed automatically when a replacement `DRAFT` candidate for the same `OptimisationSpecification.id` is activated. Explicit retirement of the current ACTIVE version is performed by `DELETE /optimisationSpecification/{id}`. It must be lifecycle-only, require `If-Match`, update `statusChangeDate`, and must not change any contract fields.

`PUT` is not the mechanism for retiring an `ACTIVE` specification. `PUT` remains the approved platform extension for full replacement and finalisation of mutable `DRAFT` specifications only.

`DELETE /optimisationSpecification/draft/{draftId}` physically removes a mutable DRAFT candidate. `DELETE /optimisationSpecification/{id}` is intentionally a logical lifecycle retirement operation in this platform API. It retires the current ACTIVE version for the supplied `id` and must not physically remove ACTIVE or RETIRED records.

## 13. Operation governance summary:

| Operation | Rule |
|---|---|
| `GET /optimisationSpecification` | Lists visible specifications. Supports enumerated first-level filtering, `fields`, `offset`, and `limit`. List responses include pagination count headers when supported by the deployment. |
| `GET /optimisationSpecification/{id}` | Retrieves the current ACTIVE version by default. Historical ACTIVE or RETIRED versions require an explicit `version` query parameter. If the requested `version` matches the current ACTIVE version, OD MS returns the ACTIVE record. Supports first-level `fields`. |
| `GET /optimisationSpecification/draft/{draftId}` | Retrieves one mutable DRAFT candidate. DRAFT records do not expose official public `version`. Supports first-level `fields`. |
| `POST /optimisationSpecification` | Creates a new mutable DRAFT candidate without an official public `version`. `specKey` is required. `POST` does not accept `id`, `draftId`, or `version`. OD MS resolves `id` from `specKey`, assigns a new `draftId`, and returns `draftId` and `ETag`. |
| `PUT /optimisationSpecification/draft/{draftId}` | Approved platform extension. Full replacement and finalisation of a mutable DRAFT candidate only. Requires `If-Match` and `Content-Type: application/json`. The body must not change `id`, `draftId`, or `version`. If the body changes `specKey`, OD MS must validate the new value against the current ACTIVE `OptimisationSpecification.id` for that `specKey`. Rejected for ACTIVE and RETIRED official versions. |
| `PATCH /optimisationSpecification/draft/{draftId}` | TMF-compatible partial update using JSON Merge Patch. Requires `If-Match` and `Content-Type: application/merge-patch+json`. Contract and content updates are allowed only for the selected DRAFT candidate. The patch must not change `id`, `draftId`, or `version`. If the patch changes `specKey`, OD MS must validate the new value against the current ACTIVE `OptimisationSpecification.id` for that `specKey`. Activation from DRAFT is allowed by setting `lifecycleStatus` to `ACTIVE`. |
| `DELETE /optimisationSpecification/draft/{draftId}` | Physical delete only for an unused mutable DRAFT candidate. Requires `If-Match`. Rejected if the draft is already activated or otherwise no longer mutable. |
| `DELETE /optimisationSpecification/{id}` | Lifecycle retirement of the current ACTIVE version for the supplied `id`. Requires `If-Match` for the current ACTIVE version. Returns `204 No Content` on success. It does not delete the lineage, retained RETIRED versions, or DRAFT candidates. Returns `404 Not Found` when no current ACTIVE version exists. Returns `409 Conflict` only when a current ACTIVE version exists but retirement is blocked by governance. |

## 14. Supported list filters:

`GET /optimisationSpecification` supports only the following first-level filters in the baseline:

| Query parameter | Meaning |
|---|---|
| `id` | Stable server-assigned `OptimisationSpecification` lineage identifier resolved from `specKey` when a DRAFT candidate is created. It groups the current `ACTIVE` version, retained `RETIRED` versions, and mutable `DRAFT` candidates. A specific immutable `ACTIVE` or `RETIRED` version is selected by `id` and `version`. The current ACTIVE version is selected by `id` alone. A DRAFT candidate carries its `id`, but DRAFT operations are addressed by `draftId`. |
| `specKey` | Mandatory stable logical specification key supplied when creating a DRAFT. OD MS uses it to resolve the server-assigned `OptimisationSpecification.id` for the draft candidate. If a current ACTIVE specification already exists for the same `specKey`, the DRAFT is assigned to that existing `id`. If no ACTIVE version exists for the `specKey`, OD MS creates a new `id`. If only RETIRED versions exist for the `specKey`, OD MS creates a new `id` unless governed lineage reuse is explicitly introduced later. `specKey` may be changed while the record remains DRAFT, but OD MS must validate the changed value against the current ACTIVE `OptimisationSpecification.id` for that `specKey`. At most one ACTIVE lineage may exist for a given `specKey`. |
| `draftId` | Server-assigned identifier for a mutable DRAFT candidate. For `DRAFT` records, `draftId` is the operation selector for retrieve, update, activation, and deletion. When the draft is activated, the same `draftId` is retained on the resulting `ACTIVE` and later `RETIRED` record as immutable provenance. It is not an official public version. |
| `name` | Exact or implementation-defined case-insensitive name match. |
| `lifecycleStatus` | Exact match on `DRAFT`, `ACTIVE`, or `RETIRED`. |
| `version` | Exact match on official version. Meaningful only for `ACTIVE` and `RETIRED`. |
| `lastUpdate.gt`, `lastUpdate.lt` | Optional timestamp range filters for last update. |
| `statusChangeDate.gt`, `statusChangeDate.lt` | Optional timestamp range filters for lifecycle change date. |
| `offset` | Optional zero-based start position for list pagination. |
| `limit` | Optional maximum number of list items returned. |
| `fields` | Optional sparse fieldset projection. |

Unsupported or malformed query parameters return `400 Bad Request`. Requests combining `lifecycleStatus=DRAFT` with `version` are invalid and return `400 Bad Request`, because DRAFT candidates do not expose official public versions.

Pagination rule:

```text
OD MS list responses support `offset` and `limit` where pagination is enabled. When result counts are available, list responses include `X-Total-Count` for the total number of matching records and `X-Result-Count` for the number of records returned in the current response. If a deployment does not support count calculation, it may omit these headers but must still honour `offset` and `limit` or reject unsupported parameters with 400 Bad Request.
```

Default list resolution rule:

```text
When id is supplied without version, lifecycleStatus, or draftId, OD MS returns the current ACTIVE version for that OptimisationSpecification.id if one exists.
To retrieve historical records, callers must explicitly filter by version, lifecycleStatus, draftId, or an allowed combination.
To retrieve draft candidates from the collection, callers must explicitly filter by lifecycleStatus=DRAFT; to retrieve one draft candidate through the collection, callers may also provide draftId.
The canonical single-resource DRAFT retrieval endpoint is GET /optimisationSpecification/draft/{draftId}.
To retrieve an ACTIVE or RETIRED record by provenance, callers may provide id, draftId, and optionally lifecycleStatus=ACTIVE or lifecycleStatus=RETIRED.
If no ACTIVE version exists and no version, lifecycleStatus, or draftId filter is supplied, OD MS returns an empty list rather than silently returning DRAFT or RETIRED records.
```

Version and lifecycle filter examples:

```http
GET /optimisationSpecification?id=optimisation-spec-surgical-routing
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&lifecycleStatus=RETIRED
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&version=1.0.0
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&draftId=od-draft-surgical-routing-b
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&lifecycleStatus=RETIRED&draftId=od-draft-surgical-routing-a
GET /optimisationSpecification?id=optimisation-spec-surgical-routing&lifecycleStatus=DRAFT
GET /optimisationSpecification?lifecycleStatus=DRAFT&draftId=od-draft-surgical-routing-a
```

Sparse field projection rule:

```text
If a requested field is valid but not present for the resource's current lifecycle state, OD MS omits that field silently rather than returning an error.
For example, `fields=id,version` on a DRAFT resource returns `id` and omits `version` because DRAFT specifications do not expose an official public version. Callers can request `draftId` for DRAFT records, and may also request `draftId` on ACTIVE or RETIRED records for provenance. A `draftId` filter on ACTIVE or RETIRED records is read-only provenance lookup and does not make `draftId` the official version selector.
When `fields` is supplied, OD MS returns only requested business fields plus mandatory metadata fields `id`, `href`, and `@type`. `_links` is returned in a sparse response only when `_links` is explicitly requested.
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
PUT /optimisationSpecification/draft/{draftId}
PATCH /optimisationSpecification/draft/{draftId}
DELETE /optimisationSpecification/draft/{draftId}
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

For DRAFT candidate operations, `If-Match` must match the `ETag` of the selected `draftId` candidate. Missing or unknown `draftId` in a DRAFT candidate path returns `404 Not Found`. A stale or mismatched `If-Match` for the selected DRAFT candidate returns `412 Precondition Failed`. For ACTIVE retirement through `DELETE /optimisationSpecification/{id}`, `If-Match` must match the `ETag` of the current ACTIVE version for `id`; `draftId` is not used for ACTIVE retirement.

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

The `private, max-age=300` posture is suitable for initial synchronous discovery/validation flows. OC MS may cache immutable `ACTIVE` specification contracts by `id` and `ETag`; because `ACTIVE` specifications are immutable, a cached contract for a specific `id` is safe. OC MS must not rely on a stale `specKey` lookup to infer the current active contract; runtime validation is against the referenced `OptimisationSpecification.id` resolved by OD MS.

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
| `retire` | `DELETE` | Governed retirement of the current `ACTIVE` version for an `id`. |
| `createNewVersion` | `POST` | Item-level affordance to create a replacement `DRAFT` candidate by submitting the same `specKey` as the current ACTIVE specification. OD MS resolves the existing `id` from `specKey`; the official `version` is assigned only when the draft candidate is activated. |

The `create` and `createNewVersion` link relations are intentionally different. `create` is a collection-level affordance for creating a new DRAFT candidate. `createNewVersion` is an item-level affordance shown on ACTIVE or RETIRED records to guide callers toward creating a replacement DRAFT candidate using the same `specKey`. Both use `POST /optimisationSpecification`; the submitted `specKey` determines whether OD MS resolves the new DRAFT to an existing active lineage or creates a new lineage.

The `activate` link relation points to `PATCH /optimisationSpecification/draft/{draftId}`. DRAFT action links use the DRAFT candidate endpoint and include `draftId` in the path. The `retire` link relation points to `DELETE /optimisationSpecification/{id}` and targets the current ACTIVE version for that `id`. `draftId` may be returned on ACTIVE and RETIRED records for provenance, but ACTIVE and RETIRED action links must not use `draftId` for mutation.

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
  "specKey": "surgical-routing-optimisation",
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

Client requests must include `specKey` and must not include `id`, `draftId`, or `version`. OD MS resolves the server-assigned `id` from `specKey`, creates a mutable DRAFT candidate, assigns a new `draftId`, and returns the initial `ETag`. If a current ACTIVE specification already exists for the same `specKey`, the DRAFT is assigned to that existing `id`; otherwise OD MS creates a new `id`.

Response:

```http
HTTP/1.1 201 Created
Location: /optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a
ETag: "od-draft-surgical-routing-a-r1"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

```json
{
  "id": "optimisation-spec-surgical-routing",
  "href": "/optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a",
  "draftId": "od-draft-surgical-routing-a",
  "name": "Surgical Routing Optimisation Specification",
  "description": "Defines the allowed optimisation request contract for surgical routing optimisation.",
  "specKey": "surgical-routing-optimisation",
  "lifecycleStatus": "DRAFT",
  "statusChangeDate": "2026-05-09T04:10:00Z",
  "creationDate": "2026-05-09T04:10:00Z",
  "lastUpdate": "2026-05-09T04:10:00Z",
  "validFor": {
    "startDateTime": "2026-05-09T00:00:00Z"
  },
  "isBundle": false,
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
      "href": "/optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a",
      "method": "GET"
    },
    "collection": {
      "href": "/optimisationManagement/v1/optimisationSpecification",
      "method": "GET"
    },
    "patch": {
      "href": "/optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a",
      "method": "PATCH"
    },
    "replace": {
      "href": "/optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a",
      "method": "PUT"
    },
    "delete": {
      "href": "/optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a",
      "method": "DELETE"
    },
    "activate": {
      "href": "/optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a",
      "method": "PATCH"
    }
  }
}
```

### 18.2. GET /optimisationSpecification list:

Request:

```http
GET /optimisationManagement/v1/optimisationSpecification?id=optimisation-spec-surgical-routing&fields=id,href,name,specKey,draftId,version,lifecycleStatus,statusChangeDate,@type,_links
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
    "specKey": "surgical-routing-optimisation",
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
        "method": "DELETE"
      },
      "createNewVersion": {
        "href": "/optimisationManagement/v1/optimisationSpecification",
        "method": "POST"
      }
    }
  }
]
```

### 18.3. GET /optimisationSpecification/{id} retrieve ACTIVE by default:

Request:

```http
GET /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing
Cache-Control: no-cache
```

Response body returns the current ACTIVE official version for the supplied `id`. Historical version retrieval uses the same `id` with an explicit `version` filter:

```http
GET /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?version=1.0.0
Cache-Control: no-cache
```

OD MS returns the immutable `ACTIVE` or `RETIRED` version that matches the requested official version. It must not return a DRAFT resource for an official version lookup because DRAFT resources do not expose official public versions.

### 18.4. GET /optimisationSpecification/draft/{draftId} retrieve DRAFT candidate:

Request:

```http
GET /optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a
Cache-Control: no-cache
```

OD MS returns the selected mutable DRAFT candidate. The returned DRAFT representation includes `draftId`, omits official public `version`, and exposes DRAFT action links using `/optimisationSpecification/draft/{draftId}`.

### 18.5. PATCH activation of finalised DRAFT:

Request:

```http
PATCH /optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a
If-Match: "od-draft-surgical-routing-a-r3"
Content-Type: application/merge-patch+json
```

```json
{
  "lifecycleStatus": "ACTIVE"
}
```

The `draftId` path parameter selects the mutable DRAFT candidate being activated. OD MS reads the draft candidate's intended `id`, assigns the official `version`, and promotes the selected draft. If an ACTIVE version already exists for the same `id`, OD MS transactionally retires the previous ACTIVE version.

Response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-surgical-routing-r4"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

Response body returns the full activated resource, including the carried-forward `draftId` and the newly assigned official `version`.

```json
{
  "id": "optimisation-spec-surgical-routing",
  "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing",
  "specKey": "surgical-routing-optimisation",
  "draftId": "od-draft-surgical-routing-a",
  "version": "1.0.0",
  "name": "Surgical Routing Optimisation Specification",
  "description": "Defines the allowed optimisation request contract for surgical routing optimisation.",
  "lifecycleStatus": "ACTIVE",
  "statusChangeDate": "2026-05-09T05:00:00Z",
  "creationDate": "2026-05-09T04:10:00Z",
  "lastUpdate": "2026-05-09T05:00:00Z",
  "@type": "OptimisationSpecification",
  "@baseType": "EntitySpecification",
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
      "method": "DELETE"
    },
    "createNewVersion": {
      "href": "/optimisationManagement/v1/optimisationSpecification",
      "method": "POST"
    }
  }
}
```

### 18.6. PUT finalise and activate mutable DRAFT:

Request:

```http
PUT /optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a
If-Match: "od-draft-surgical-routing-a-r3"
Content-Type: application/json
```

The request body contains the full replacement mutable `DRAFT` `OptimisationSpecification` contract and may request activation by setting `lifecycleStatus` to `ACTIVE`. It must include all required client-controlled fields for the final contract. It must not include server-controlled fields or immutable identity fields such as `href`, `id`, `draftId`, `creationDate`, `lastUpdate`, `statusChangeDate`, `_links`, or official `version`. If the body changes `specKey`, OD MS must validate the new value against the current ACTIVE `OptimisationSpecification.id` for that `specKey` before accepting the update or activation.

Response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-surgical-routing-r4"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

Response body returns the full DRAFT or activated resource depending on the submitted lifecycle status. `PUT` is an approved platform extension and is allowed only for mutable DRAFT candidates.

### 18.7. DELETE current ACTIVE by id retires the active version:

Request:

```http
DELETE /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing
If-Match: "od-spec-surgical-routing-r4"
```

Response:

```http
HTTP/1.1 204 No Content
```

This operation retires the current ACTIVE version for the supplied `id`. It does not delete the lineage, retained RETIRED versions, or DRAFT candidates. If no current ACTIVE version exists for the supplied `id`, OD MS returns `404 Not Found`. If a current ACTIVE version exists but retirement is blocked by governance, OD MS returns `409 Conflict`.

### 18.8. DELETE mutable DRAFT by draftId:

Request:

```http
DELETE /optimisationManagement/v1/optimisationSpecification/draft/od-draft-surgical-routing-a
If-Match: "od-draft-surgical-routing-a-r1"
```

Response:

```http
HTTP/1.1 204 No Content
```

Physical delete is allowed only for mutable DRAFT candidates. ACTIVE and RETIRED official versions are retained.

## 19. Error handling baseline:

OD MS uses TMF-style error responses with platform-specific error codes.

Core status codes:

| **Status** | **Use** |
|---|---|
| `200 OK` | Successful `GET`, `PATCH`, or approved platform-extension `PUT` with body. |
| `201 Created` | Successful `POST`. |
| `204 No Content` | Successful physical delete of a mutable `DRAFT` candidate or successful retirement of the current `ACTIVE` version through `DELETE /optimisationSpecification/{id}`. |
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

`501 Not Implemented` is returned when an approved platform extension, such as `PUT /optimisationSpecification/draft/{draftId}`, is not enabled in the deployment receiving the request.

Boundary rules:

```text
ACTIVE or RETIRED contract or content mutation -> 409 Conflict
DRAFT contract and content update that fails OptimisationSpecification schema validation -> 422 Unprocessable Entity
targetEntitySchema or expressionSpecification contract-shape failure -> 422 Unprocessable Entity
concurrent activation conflict for the same `OptimisationSpecification.id` -> 409 Conflict
activation would create more than one ACTIVE lineage for the same `specKey` -> 409 Conflict and rollback
existing duplicate ACTIVE-lineage state for the same `specKey` detected during POST, PUT, PATCH, GET, or DELETE -> 409 Conflict for client-visible lifecycle operations and operational alert
server-side official version uniqueness violation -> internal data-integrity failure; OD MS must roll back the activation transaction
unsupported PATCH Content-Type -> 415 Unsupported Media Type
unsupported query parameter -> 400 Bad Request
client-supplied id, draftId, or version on POST -> 400 Bad Request
PATCH or PUT attempts to change id, draftId, or version -> 400 Bad Request
PATCH or PUT changes specKey and the changed value resolves to a different current ACTIVE OptimisationSpecification id -> 409 Conflict
lifecycleStatus=DRAFT combined with version -> 400 Bad Request
unknown draftId in /optimisationSpecification/draft/{draftId} -> 404 Not Found
stale or mismatched If-Match for selected draftId candidate -> 412 Precondition Failed
DELETE /optimisationSpecification/{id} with no visible current ACTIVE version -> 404 Not Found
DELETE /optimisationSpecification/{id} when current ACTIVE exists but retirement is blocked by governance -> 409 Conflict
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

Spec key conflict response:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_SPECIFICATION_SPEC_KEY_CONFLICT",
  "reason": "Spec key activation conflict",
  "message": "Activation would result in more than one ACTIVE OptimisationSpecification lineage for the same specKey, or OD MS detected an existing duplicate ACTIVE-lineage state for that specKey.",
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
  "message": "PATCH /optimisationSpecification/draft/{draftId} requires Content-Type: application/merge-patch+json. PUT /optimisationSpecification/draft/{draftId} requires Content-Type: application/json.",
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

Section 19 summarises the error status codes. This section defines the canonical `422 Unprocessable Entity` response used when the JSON is structurally valid but violates the OD MS `OptimisationSpecification` schema or the request-contract schema rules for `targetEntitySchema`, `expressionSpecification`, or `specCharacteristic[]`.

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

OC MS validates runtime `Optimisation` requests against the `targetEntitySchema` of the referenced `ACTIVE` `OptimisationSpecification`. Runtime creation requires both `optimisationSpecification.id` and `expression.iri`; OC MS uses the id as the exact contract pointer and verifies the runtime IRI against `OptimisationSpecification.expressionSpecification.iri`. OC MS does not use `specKey` for runtime contract selection.

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

A future `createFrom` capability for governed lineage reuse across retired-only `specKey` records is deferred and must not be assumed by clients. The current baseline creates a new `id` when a DRAFT is created for a `specKey` that has no current ACTIVE lineage, even if RETIRED history exists for the same `specKey`.

Until then, event support and future lineage-reuse capabilities are deferred and must not be assumed by clients.
