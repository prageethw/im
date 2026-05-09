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
