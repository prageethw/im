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
