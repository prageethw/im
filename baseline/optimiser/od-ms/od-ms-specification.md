# OD MS / Optimisation Definition MS Specification

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
- `PUT` is an approved platform extension for full replacement/finalisation of mutable `DRAFT` specifications only.

Approved platform extensions:

| Extension | Purpose | Guardrail |
|---|---|---|
| `PUT /optimisationSpecification/{id}` | Full replacement/finalisation of mutable `DRAFT` specifications. | Requires `If-Match`; not allowed for `ACTIVE` or `RETIRED`. |
| `_links` | HATEOAS controls. | Does not replace `href`; lifecycle-aware and authorisation-aware. |
| `ETag` / `If-Match` governance | Optimistic concurrency for unsafe existing-resource operations. | Required for `PUT`, `PATCH`, and `DELETE`. |
| `x-platform-extension` / `x-tmf-native` response headers | Governance/documentation headers for NGW-facing optimiser-domain resources. | Used only on external NGW-facing OD/OC APIs; clients must not use these headers as business-logic switches. |

## 3. Ownership:

OD MS owns:

```text
OptimisationSpecification resource
Optimisation capability metadata
Request contract definition
Expression specification metadata
Target entity schema for runtime Optimisation expressions
Specification characteristic catalogue for discovery and OEX/UI guidance
Specification lifecycle
Specification activation/version assignment
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

`OptimisationSpecification` is a platform optimiser-domain resource modelled using the TMF921 `IntentSpecification` / `EntitySpecification` pattern. It is not a native TMF921 resource name.

Canonical fields:

```text
id
href
name
description
familyId
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
creationDate
lastUpdate
statusChangeDate
version
_links
```

`version` is included in the canonical field set because it is present on `ACTIVE` and `RETIRED` specifications. Mutable `DRAFT` specifications do not expose an official public `version`; draft revision is represented by `ETag` only.

`_links` is an approved HATEOAS platform extension. It does not replace the standard `href` field.

The external `OptimisationSpecification` resource must use only the TMF-aligned specification structures shown in the canonical field list. Optimiser request-contract semantics are represented through `targetEntitySchema`, `expressionSpecification`, and `specCharacteristic[]`.

## 6. Field semantics:

| Field | Meaning |
|---|---|
| `id` | Unique identifier for the specification resource. Server assigned. |
| `href` | Hyperlink reference to the specification resource. Server assigned. |
| `name` | Human-readable specification name. Required on create. |
| `description` | Description of the optimisation capability and contract. |
| `familyId` | Required stable specification-family identifier shared by all versions of the same `OptimisationSpecification`. OD MS uses it to enforce at most one `ACTIVE` version per family. |
| `version` | Official specification version within the specification family. Omitted for mutable `DRAFT`; assigned by OD MS only when the draft is activated. Present and immutable for `ACTIVE` and `RETIRED` specifications. |
| `lifecycleStatus` | Specification lifecycle value: `DRAFT`, `ACTIVE`, or `RETIRED`. Created as `DRAFT` by default. |
| `statusChangeDate` | Date/time the `lifecycleStatus` last changed. Server assigned. |
| `creationDate` | Date/time the specification resource was created. Server assigned. |
| `lastUpdate` | Date/time the specification resource was last updated. Server assigned. |
| `validFor` | Optional validity window for the specification. |
| `isBundle` | TMF-style bundle indicator. Default should be `false` unless explicitly modelling a bundle. |
| `specCharacteristic[]` | Discovery/catalogue metadata for supported optimisation fields and OEX/UI guidance. |
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
| `specCharacteristic[]` | Catalogue/discovery metadata for OEX/UI and API consumers. It advertises supported optimisation capability characteristics, examples, defaults, and display guidance. | It must not be treated as the authoritative validation schema. |
| `expressionSpecification` | Expression-language and ontology binding. It declares `@type = ExpressionSpecification`, `expressionType = JsonLdExpression`, `expressionLanguage = JSON-LD`, and the optimisation ontology `iri`. | It must not contain runtime request values or detailed JSON validation rules. |
| `targetEntitySchema` | Authoritative validation contract for `Optimisation.expression.expressionValue`, including `context.targets[]`, `context.constraints[]`, and `context.preferences[]`. | It must not be replaced by catalogue characteristics or prose-only rules. |

Baseline rule:

```text
specCharacteristic[] = catalogue / discovery / UI guidance
expressionSpecification = expression type + expression language + ontology IRI
targetEntitySchema = authoritative runtime expressionValue validation schema
```

The design-time `expressionSpecification` must not be confused with the runtime `expression` instance. `expressionSpecification` declares the expected expression type/language/ontology for runtime requests. The runtime `Optimisation.expression` carries the actual `JsonLdExpression`, and `Optimisation.expression.expressionValue` carries the actual JSON-LD optimisation problem payload.

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
| `context` | The whole optimisation scenario / big picture. |
| `context.targets[]` | Optimisation goals the optimiser tries to achieve. |
| `context.constraints[]` | Hard mandatory requirements that must be satisfied. |
| `context.preferences[]` | Soft ranking or selection preferences used to choose between otherwise valid outcomes. |

OD MS defines this runtime contract using `targetEntitySchema`. `specCharacteristic[]` may describe these fields for discovery, governance, examples, defaults, and OEX/UI prefill guidance, but it must not replace the authoritative schema.

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
      "description": "The full optimisation scenario / big picture. Contains optimisation goals, hard requirements, and soft preferences.",
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
| `DRAFT` | Specification is being prepared. | Editable. Not usable for new runtime `Optimisation` creation. No official public `version`; draft revision is represented by `ETag` only. |
| `ACTIVE` | Specification is approved for runtime use. | Immutable for contract/content changes. Used by OC MS to validate and create runtime `Optimisation` resources. May be moved to `RETIRED` only by governed lifecycle transition, normally when another `DRAFT` in the same `familyId` is activated. |
| `RETIRED` | Specification is no longer available for new use. | Immutable retained history/audit record. Not editable and not usable for new runtime `Optimisation` creation. Existing runtime references may continue to resolve it for audit/explainability. |

Baseline immutability rule:

```text
Only DRAFT specifications are mutable.
ACTIVE specifications are contract/content immutable.
RETIRED specifications are fully immutable retained records.
To change an ACTIVE specification contract, create a new DRAFT in the same familyId and activate it.
OD MS assigns the official version during activation, not while the resource is still DRAFT.
```

## 12. Version activation and retirement governance:

Version governance baseline:

```text
DRAFT: no official public version; ETag represents draft revision/concurrency.
ACTIVE: official version is assigned at activation and is immutable.
RETIRED: retains the assigned official version and is immutable.
```

Multiple DRAFT OptimisationSpecification resources may exist in the same familyId at the same time. Official version uniqueness applies only to ACTIVE and RETIRED specifications because DRAFT specifications do not expose an official public version. OD MS enforces only one ACTIVE OptimisationSpecification per familyId.

Version format baseline:

```text
Official version values use SemVer-compatible MAJOR.MINOR.PATCH format, for example 1.0.0.
The official version is assigned by OD MS during activation.
Client requests must not assign or change the official version.
Within a familyId, an official version value must be unique across ACTIVE and RETIRED specifications as a server-side data-integrity invariant.
Because the official version is assigned by OD MS, clients cannot directly create a duplicate official version. If OD MS cannot safely assign a new official version because another activation is occurring for the same familyId, OD MS returns 409 Conflict for the concurrent activation conflict.
```

`POST /optimisationSpecification` always creates a mutable `DRAFT` `OptimisationSpecification` without an official public `version`.

`DRAFT -> ACTIVE` is a governed activation transition on an existing `DRAFT` specification. Activation may be performed by:

- `PATCH`, when the draft body is already final and only lifecycle activation is required.
- `PUT`, as an approved platform extension, when finalising/replacing the full mutable `DRAFT` contract as part of activation.

Activation rules:

```text
Only one ACTIVE OptimisationSpecification is allowed per familyId.
Activation is allowed only from DRAFT.
Activation validates the full OptimisationSpecification before committing the lifecycle transition.
When a DRAFT specification is promoted to ACTIVE, OD MS assigns the official version for that specification family and must transactionally retire any previous ACTIVE specification with the same familyId.
The newly ACTIVE specification becomes contract/content immutable immediately after activation.
The previous ACTIVE specification becomes RETIRED and fully immutable as part of the same transaction.
```

`ACTIVE -> RETIRED` is a governed lifecycle transition, not a contract/content update. It is normally performed automatically when a replacement `DRAFT` in the same `familyId` is activated. If a deployment allows explicit retirement, it must be lifecycle-only, require `If-Match`, update `statusChangeDate`, and must not change any contract fields.

`PUT` is not the mechanism for retiring an `ACTIVE` specification. `PUT` remains the approved platform extension for full replacement/finalisation of mutable `DRAFT` specifications only.

Physical `DELETE` is not used for `ACTIVE` or `RETIRED` specifications.

## 13. Operation governance summary:

| Operation | Rule |
|---|---|
| `GET /optimisationSpecification` | Lists visible specifications. Supports enumerated first-level filtering and `fields`. |
| `GET /optimisationSpecification/{id}` | Retrieves one specification. Supports first-level `fields`. |
| `POST /optimisationSpecification` | Creates a new mutable `DRAFT` specification without an official public `version`. `familyId` is required. Returns an `ETag` for draft revision/concurrency. |
| `PUT /optimisationSpecification/{id}` | Approved platform extension. Full replacement/finalisation of mutable `DRAFT` only. Requires `If-Match` and `Content-Type: application/json`. Rejected for `ACTIVE` and `RETIRED`. |
| `PATCH /optimisationSpecification/{id}` | TMF-compatible partial update using JSON Merge Patch. Requires `If-Match` and `Content-Type: application/merge-patch+json`. Contract/content updates are allowed only for `DRAFT`. Activation from `DRAFT` is allowed. Retirement of `ACTIVE` is lifecycle-only and does not permit contract/content changes. Rejected for `RETIRED`. |
| `DELETE /optimisationSpecification/{id}` | Physical delete only for mutable `DRAFT`. Requires `If-Match`. Rejected for `ACTIVE` and `RETIRED`. |

## 14. Supported list filters:

`GET /optimisationSpecification` supports only the following first-level filters in the baseline:

| Query parameter | Meaning |
|---|---|
| `id` | Exact match on resource id. |
| `familyId` | Exact match on specification family. |
| `name` | Exact or implementation-defined case-insensitive name match. |
| `lifecycleStatus` | Exact match on `DRAFT`, `ACTIVE`, or `RETIRED`. |
| `version` | Exact match on official version. Meaningful only for `ACTIVE` and `RETIRED`. |
| `lastUpdate.gt` / `lastUpdate.lt` | Optional timestamp range filters for last update. |
| `statusChangeDate.gt` / `statusChangeDate.lt` | Optional timestamp range filters for lifecycle change date. |
| `fields` | Optional sparse fieldset projection. |

Unsupported or malformed query parameters return `400 Bad Request`.

Sparse field projection rule:

```text
If a requested field is valid but not present for the resource's current lifecycle state, OD MS omits that field silently rather than returning an error.
For example, fields=id,version on a DRAFT resource returns id and omits version because DRAFT specifications do not expose an official public version.
Unsupported field names still return 400 Bad Request.
```

## 15. External response header governance:

OD MS external NGW-facing API responses include the following governance/documentation headers because `OptimisationSpecification` is an optimiser-domain platform resource that follows TMF-style conventions but is not a native TMF Open API resource:

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

`POST /optimisationSpecification` creates a new server-assigned `DRAFT` resource and does not normally require `If-Match`. It returns an `ETag` for future updates.

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
| `createNewVersion` | `POST` | Create a new mutable `DRAFT` in the same `familyId` from an existing active/retired family. The official `version` is assigned only when the draft is activated. |

The `activate` and `retire` link relations point to `PATCH` on the `OptimisationSpecification` resource itself. OD MS does not expose separate `/activate` or `/retire` action endpoints. The `retire` link is lifecycle-only and must not be used to modify an `ACTIVE` specification contract/content.

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
Location: /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1
ETag: "od-spec-surgical-routing-v1-r1"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

```json
{
  "id": "optimisation-spec-surgical-routing-v1",
  "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
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
}
```

### 18.2. GET /optimisationSpecification list:

Request:

```http
GET /optimisationManagement/v1/optimisationSpecification?familyId=optimisation-spec-surgical-routing&lifecycleStatus=ACTIVE&fields=id,href,name,familyId,version,lifecycleStatus,statusChangeDate
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
    "id": "optimisation-spec-surgical-routing-v1",
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
    "name": "Surgical Routing Optimisation Specification",
    "familyId": "optimisation-spec-surgical-routing",
    "version": "1.0.0",
    "lifecycleStatus": "ACTIVE",
    "statusChangeDate": "2026-05-09T05:00:00Z",
    "@type": "OptimisationSpecification",
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
  }
]
```

### 18.3. GET /optimisationSpecification/{id} retrieve ACTIVE:

Request:

```http
GET /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1
Cache-Control: no-cache
```

Response:

```http
HTTP/1.1 200 OK
Cache-Control: private, max-age=300
ETag: "od-spec-surgical-routing-v1-r4"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

```json
{
  "id": "optimisation-spec-surgical-routing-v1",
  "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1",
  "name": "Surgical Routing Optimisation Specification",
  "description": "Defines the allowed optimisation request contract for surgical routing optimisation.",
  "familyId": "optimisation-spec-surgical-routing",
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
}
```

### 18.4. PATCH activation of finalised DRAFT:

Request:

```http
PATCH /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1
If-Match: "od-spec-surgical-routing-v1-r3"
Content-Type: application/merge-patch+json
```

```json
{
  "lifecycleStatus": "ACTIVE"
}
```

OD MS assigns the official `version` as part of this activation transaction. Clients do not assign the official version while the specification is still `DRAFT`.

Response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-surgical-routing-v1-r4"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

Response body returns the full activated resource. OD MS transactionally retires the previous `ACTIVE` version in the same `familyId` family.

### 18.5. PUT finalise and activate mutable DRAFT:

Request:

```http
PUT /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1
If-Match: "od-spec-surgical-routing-v1-r3"
Content-Type: application/json
```

The request body contains the full replacement mutable `DRAFT` `OptimisationSpecification` contract and may request activation. It must include all required client-controlled fields for the final contract. It must not include server-controlled fields such as `id`, `href`, `creationDate`, `lastUpdate`, `statusChangeDate`, `_links`, or official `version`.

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
ETag: "od-spec-surgical-routing-v1-r4"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

Response body returns the full activated resource. `PUT` is an approved platform extension and is allowed only for mutable `DRAFT` specifications.

### 18.6. PATCH retirement of ACTIVE:

Request:

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

Response:

```http
HTTP/1.1 200 OK
ETag: "od-spec-surgical-routing-v1-r5"
x-platform-extension: true
x-tmf-native: false
Content-Type: application/json
```

Response body returns the full retired `OptimisationSpecification`. This operation changes lifecycle metadata only; it must not alter any specification contract/content fields.

Retired specifications expose only lifecycle-authorised read/new-version links such as `self`, `collection`, and `createNewVersion`.

### 18.7. DELETE mutable DRAFT:

Request:

```http
DELETE /optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing-v1
If-Match: "od-spec-surgical-routing-v1-r1"
```

Response:

```http
HTTP/1.1 204 No Content
```

Physical delete is allowed only for mutable `DRAFT` specifications. `ACTIVE` and `RETIRED` specifications are retained.

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
| `409 Conflict` | Lifecycle/version conflict, including ACTIVE/RETIRED mutation attempts or concurrent activation conflict for the same familyId. |
| `412 Precondition Failed` | `If-Match` is stale or mismatched. |
| `415 Unsupported Media Type` | Unsupported request content type. |
| `422 Unprocessable Entity` | Syntactically valid JSON violates OD MS `OptimisationSpecification` schema or targetEntitySchema contract rules. |
| `428 Precondition Required` | Missing required `If-Match` on unsafe existing-resource operation. |
| `500 Internal Server Error` | Unexpected OD MS failure. |
| `501 Not Implemented` | Operation or approved platform extension is not implemented or not enabled in this deployment. |
| `503 Service Unavailable` | OD MS temporarily unavailable. |

Boundary rules:

```text
ACTIVE/RETIRED contract or content mutation -> 409 Conflict
DRAFT contract/content update that fails OptimisationSpecification schema validation -> 422 Unprocessable Entity
targetEntitySchema / expressionSpecification contract-shape failure -> 422 Unprocessable Entity
concurrent activation conflict for the same familyId -> 409 Conflict
server-side official version uniqueness violation -> internal data-integrity failure; OD MS must roll back the activation transaction
unsupported PATCH Content-Type -> 415 Unsupported Media Type
unsupported query parameter -> 400 Bad Request
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
  "message": "Only DRAFT OptimisationSpecification resources can be changed. ACTIVE specifications are contract/content immutable and RETIRED specifications are fully immutable retained records.",
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
  "message": "Another OptimisationSpecification activation is already in progress or has just completed for the same familyId. Refresh the family state and retry if still required.",
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
Worker model: decides feasibility cancellation outcome and returns COMPLETED, INFEASIBLE, FAILED, or CANCELLED.
```

OC MS validates runtime `Optimisation` requests against the `targetEntitySchema` of the referenced `ACTIVE` `OptimisationSpecification`.

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
metric-vs-constraint fit
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
