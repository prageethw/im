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
