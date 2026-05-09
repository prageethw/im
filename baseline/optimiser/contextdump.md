# Context Dump

This file is the running baseline dump for this conversation. New baselines are appended to the end unless explicitly requested otherwise.

---

## Baseline appended 2026-05-09 - Optimiser external API concept and TMF/TIO alignment

External-facing backend optimisation APIs remain TMF921/TIO-aligned in structure and semantics, but optimiser architecture documents use **Optimisation** as the external/domain concept instead of **Intent**.

The optimiser domain must not be forced into the long-running Intent control-loop model by default. A runtime Optimisation is a short-lived run that reaches a terminal outcome.

Runtime Optimisation lifecycle/status values:

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

Outcome mapping:

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```

Retrial rule:

```text
FAILED -> retrial creates a new Optimisation with retrialOf pointing to the failed one.
Retrial must not move the failed Optimisation back to PROCESSING.
```

OptimisationSpecification lifecycle values:

```text
DRAFT
ACTIVE
RETIRED
```

No `DEPRECATED` state is used for OptimisationSpecification.

Runtime Optimisation expression shape:

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
        "targets": [
          {
            "maxLatencyMs": 20,
            "minAvailabilityPercent": 99.95
          }
        ],
        "constraints": [
          {
            "locationId": "melbourne-hospital-a",
            "serviceClass": "surgical-video",
            "redundancyRequired": true
          }
        ],
        "preferences": [
          {
            "preferredAccessTechnology": "5G",
            "optimiseFor": "lowest-latency"
          }
        ]
      }
    }
  }
}
```

## OD MS OptimisationSpecification TMF-aligned resource shape baseline:

OD MS `OptimisationSpecification` must be modelled as the optimiser-domain equivalent of the TMF921 `IntentSpecification` resource.

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

`targetEntitySchema` is the authoritative validation contract for runtime `Optimisation.expression.expressionValue.context`, including `targets[]`, `constraints[]`, and `preferences[]`. `specCharacteristic[]` is for discovery/catalogue metadata, examples, defaults, and OEX/UI prefill guidance. It must not replace `targetEntitySchema` as the validation source.

## Baseline update - OD MS embedded targetEntitySchema artifact

- OD MS must not reference `optimisation-expression-value.schema.json` as a mysterious external file without also documenting the governed schema content in the OD MS specification baseline.
- `od-ms-specification.md` now includes an embedded schema artifact section named `optimisation-expression-value.schema.json`.
- The embedded schema validates `Optimisation.expression.expressionValue`, with `expressionValue.context` as the canonical container and `context.targets[]`, `context.constraints[]`, and `context.preferences[]` as the required semantic buckets.
- The schema section remains documentation inside the MD file unless a separate JSON artifact is explicitly requested later.



## Baseline update - OD MS specification responsibility split

OD MS / `OptimisationSpecification` must keep TMF-aligned structures clearly separated:

- `specCharacteristic[]` is catalogue/discovery metadata for OEX/UI and API consumers. It advertises supported optimisation capability characteristics, examples, defaults, and display guidance. It must not be treated as the authoritative validation schema.
- `expressionSpecification` defines expression language and ontology binding, such as `JsonLdExpression` and the optimisation ontology IRI. It must not contain runtime request values or detailed JSON validation rules.
- `targetEntitySchema` is the authoritative validation contract for `Optimisation.expression.expressionValue`, including `context.targets[]`, `context.constraints[]`, and `context.preferences[]`. It must not be replaced by catalogue characteristics or prose-only rules.

Baseline shorthand:

```text
specCharacteristic[]      = catalogue / discovery / UI guidance
expressionSpecification   = expression language + ontology IRI
targetEntitySchema        = authoritative runtime expressionValue validation schema
```

Future spec updates should proactively check this separation and cross-document consistency rather than waiting for review comments.

## Baseline update - OD MS OptimisationSpecification resource shape and field responsibilities

OD MS `OptimisationSpecification` canonical fields are:

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

Field responsibility baseline:

| Field / Section | Responsibility |
|---|---|
| `id`, `href` | Server-generated identity and address. |
| `name`, `description`, `version` | Human-readable catalogue identity/version. |
| `lifecycleStatus` | `DRAFT`, `ACTIVE`, `RETIRED` only. |
| `creationDate`, `lastUpdate`, `validFor` | Governance and validity metadata. |
| `isBundle` | TMF-aligned bundle flag; normally `false` for a single optimisation specification. |
| `specCharacteristic[]` | Catalogue/discovery metadata only. |
| `expressionSpecification` | Expression language and ontology IRI. |
| `targetEntitySchema` | Authoritative schema for runtime `Optimisation.expression.expressionValue.context`. |
| `relatedParty[]` | Owner/steward/supporting party references. |
| `attachment[]` | Optional supporting documentation or media. |
| `constraint[]` | Optional TMF-style policy/rule references applied to the specification; not runtime `context.constraints[]`. |
| `entitySpecRelationship[]` | Relationships to other specification resources. |
| `@type`, `@baseType`, `@schemaLocation` | TMF polymorphism and extension fields. |

`targetEntitySchema` owns real structural validation for runtime `expression.expressionValue.context.targets[]`, `context.constraints[]`, and `context.preferences[]`. `specCharacteristic[]` can advertise that those sections exist and provide examples/defaults/UI guidance, but it must not duplicate or replace the full schema.

## Baseline update - OD MS OptimisationSpecification lifecycle and governance

OD MS `OptimisationSpecification` lifecycle is intentionally simple and run-support oriented:

```text
DRAFT -> ACTIVE -> RETIRED
```

There is no `DEPRECATED` lifecycle state in the optimiser baseline.

| Status | Meaning | Edit rule | Runtime use rule |
|---|---|---|---|
| `DRAFT` | Specification is being prepared. | Editable through approved update operations. | Not usable for new runtime Optimisation creation. |
| `ACTIVE` | Specification is approved for runtime use. | Immutable except controlled lifecycle/version transition metadata. | Usable for new runtime Optimisation creation. |
| `RETIRED` | Specification is no longer available for new runtime use. | Immutable except audit metadata if explicitly required. | Not usable for new runtime Optimisation creation; historical runtime references remain readable. |

Operation governance baseline:

| Operation | Rule |
|---|---|
| `POST /optimisationSpecification` | Creates a new `DRAFT` specification by default unless an explicitly governed activation workflow is used. |
| `PUT /optimisationSpecification/{id}` | Approved platform extension; full replacement of mutable `DRAFT` specifications only. |
| `PATCH /optimisationSpecification/{id}` | Supported for TMF compatibility, but must be used carefully. Do not use it for material contract replacement such as replacing `targetEntitySchema`, replacing `expressionSpecification`, changing the characteristic catalogue, changing version identity, or major lifecycle/version transitions unless explicitly guarded. |
| `DELETE /optimisationSpecification/{id}` | Allowed for `DRAFT`; for `ACTIVE`, prefer lifecycle transition to `RETIRED` rather than physical delete. |
| `GET` | Available for all lifecycle states. |

When an `OptimisationSpecification` is `ACTIVE`, changing the runtime contract should normally require a new versioned `DRAFT` specification rather than mutation of the active one. This keeps runtime optimisation runs auditable, repeatable, and explainable.

## Baseline update - OD MS OptimisationSpecification lifecycle and governance

OD MS `OptimisationSpecification` lifecycle is intentionally simple and run-support oriented:

```text
DRAFT -> ACTIVE -> RETIRED
```

There is no `DEPRECATED` lifecycle state in the optimiser baseline.

| Status | Meaning | Edit rule | Runtime use rule |
|---|---|---|---|
| `DRAFT` | Specification is being prepared. | Editable through approved update operations. | Not usable for new runtime Optimisation creation. |
| `ACTIVE` | Specification is approved for runtime use. | Immutable except controlled lifecycle/version transition metadata. | Usable for new runtime Optimisation creation. |
| `RETIRED` | Specification is no longer available for new runtime use. | Immutable except audit metadata if explicitly required. | Not usable for new runtime Optimisation creation; historical runtime references remain readable. |

Operation governance baseline:

| Operation | Rule |
|---|---|
| `POST /optimisationSpecification` | Creates a new `DRAFT` specification by default unless an explicitly governed activation workflow is used. |
| `PUT /optimisationSpecification/{id}` | Approved platform extension; full replacement of mutable `DRAFT` specifications only. |
| `PATCH /optimisationSpecification/{id}` | Supported for TMF compatibility, but must be used carefully. Do not use it for material contract replacement such as replacing `targetEntitySchema`, replacing `expressionSpecification`, changing the characteristic catalogue, changing version identity, or major lifecycle/version transitions unless explicitly guarded. |
| `DELETE /optimisationSpecification/{id}` | Allowed for `DRAFT`; for `ACTIVE`, prefer lifecycle transition to `RETIRED` rather than physical delete. |
| `GET` | Available for all lifecycle states. |

When an `OptimisationSpecification` is `ACTIVE`, changing the runtime contract should normally require a new versioned `DRAFT` specification rather than mutation of the active one. This keeps runtime optimisation runs auditable, repeatable, and explainable.


## Baseline update - OD MS POST create OptimisationSpecification

`POST /optimisationSpecification` creates a new `OptimisationSpecification` in `DRAFT` state by default, unless an explicitly governed activation workflow is used.

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

OD MS assigns server-controlled identity and timestamp fields on creation and returns the full created `OptimisationSpecification` representation.

## Baseline update - OD MS retirement governance

`ACTIVE -> RETIRED` is a governed lifecycle transition. It may be performed by `PATCH /optimisationSpecification/{id}` when the only change is `lifecycleStatus: RETIRED`; this is an acceptable small controlled lifecycle update. PATCH remains discouraged for material runtime-contract replacement.

`PUT /optimisationSpecification/{id}` remains an approved platform extension for full replacement/finalisation of mutable `DRAFT` specifications and is not the normal retirement mechanism for an `ACTIVE` specification.

Physical `DELETE` is not used for `ACTIVE` or `RETIRED` specifications. Retired specifications remain available for audit/history and existing runtime `Optimisation` references, but cannot be used for new runtime `Optimisation` creation.


## Baseline update - OD MS embedded optimisation expression schema

`targetEntitySchema` validates only the runtime `Optimisation.expression.expressionValue` structure. It does not perform solver feasibility checks, candidate ranking, objective trade-off evaluation, best-candidate selection, or runtime outcome decisions; those remain OC MS / worker / optimiser responsibilities.

`expressionValue.context` is the required canonical optimisation problem container and contains:

```json
{
  "context": {
    "targets": [],
    "constraints": [],
    "preferences": []
  }
}
```

Schema rules:

| Element | Rule |
|---|---|
| `context.targets[]` | Required array for optimisation goals; normally at least one target. |
| `context.constraints[]` | Required array for hard mandatory requirements; whether it may be empty is governed by the concrete active `OptimisationSpecification.targetEntitySchema`. |
| `context.preferences[]` | Required array for soft ranking/selection preferences; may be empty. |
| `$defs` | Keep JSON Schema `$defs` and short reusable names `target`, `constraint`, and `preference`. |

---

## OD MS baseline update — operation examples consistency cleanup

The OD MS specification has been cleaned so all operation examples consistently apply the baselined governance rules:

- `POST /optimisationSpecification` always creates `DRAFT` and returns `201 Created`, `Location`, `ETag`, and the full resource body.
- `GET /optimisationSpecification` and `GET /optimisationSpecification/{id}` return `Cache-Control: private, max-age=300` and `ETag`; the only documented cache override is `Cache-Control: no-cache`.
- Unsafe existing-resource operations (`PUT`, `PATCH`, `DELETE`) require `If-Match`.
- Missing `If-Match` returns `428 Precondition Required`; stale/mismatched `If-Match` returns `412 Precondition Failed`.
- `PUT /optimisationSpecification/{id}` is an approved platform extension for full replacement/finalisation of mutable `DRAFT` specifications only.
- `PATCH /optimisationSpecification/{id}` remains TMF-compatible but discouraged for material runtime-contract replacement.
- `PATCH` is acceptable for small controlled lifecycle-only transitions, including `DRAFT -> ACTIVE` activation when the draft body is already final and `ACTIVE -> RETIRED` retirement.
- Activation validates the full `OptimisationSpecification` and atomically retires the previously `ACTIVE` version in the same `specificationKey` family.
- Physical `DELETE` is allowed only for mutable `DRAFT`; `ACTIVE` and `RETIRED` specifications are retained.
- `_links` is a lifecycle-aware and authorisation-aware HATEOAS platform extension. `href` remains the standard TMF-style resource hyperlink.
- HATEOAS link visibility remains: `DRAFT -> self, collection, patch, replace, delete, activate`; `ACTIVE -> self, collection, retire, createNewVersion`; `RETIRED -> self, collection, createNewVersion`.
- The embedded `optimisation-expression-value.schema.json` remains in the OD MS specification file and keeps `$defs` with short names `target`, `constraint`, and `preference`.

---

## Baseline update - OD MS streamlined status-code set

The OD MS status-code baseline is streamlined and TMF-aligned, with platform governance additions where needed. The retained status codes are:

```text
200, 201, 204,
400, 401, 403, 404, 405, 409, 412, 415, 422, 428,
500, 501, 503
```

`501 Not Implemented` is retained because TMF921 OAS includes it and it is useful when an optional capability or approved platform extension, such as `PUT /optimisationSpecification/{id}`, is not implemented or enabled in a deployment.

`422 Unprocessable Entity` is used when the request JSON is syntactically valid but violates OD MS `OptimisationSpecification` schema, lifecycle, activation, or governance rules.
