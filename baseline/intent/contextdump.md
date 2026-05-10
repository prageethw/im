# Intent / Intent Management / Intent Enabler — Context Dump

## Scope lock
This baseline pack is for **Intent / Intent Management / Intent Enabler only**. Do not bring in Optimisation / OD / OC / OSB MS context unless explicitly requested.

## Primary TMF/TIO compliance references
Use the uploaded TMF artifacts as compliance-validation sources before finalising external TMF-facing API, resource, schema, and event shapes:

- `TMF921_Intent_Management_v5.0.0_specification.pdf`
- `TMF921_Intent_Management_v5.0.0_conformance.pdf`
- `TMF921_Intent_Management_v5.0.0.oas.yaml`
- `TR292_TMForum_Intent_Ontology_TIO_v3.6.0.pdf`

## Active microservice names

| Short name | Service name | Role |
|---|---|---|
| ID MS | `intent-definition-ms` | Owns IntentSpecification resources and specification lifecycle/API. |
| IC MS | `intent-controller-ms` | Owns canonical Intent resources and external TMF921 Intent events. |
| II MS | `intent-intelligence-ms` | Owns semantic interpretation, policy/knowledge validation, and optimisation-required resolution handoff. |
| IA MS | `intent-assurance-ms` | Owns assurance, lifecycle interpretation from runtime/orchestrator feedback, drift/degradation detection, and lifecycle update input to IC MS. |
| ICB MS | `intent-callback-ms` | Incoming-only REST wrapper / callback access mediation service for orchestrator callbacks. |

## External runtime expression baseline
External runtime Intent expression shape is:

```json
{
  "expression": {
    "expressionValue": {
      "context": {
        "targets": [],
        "constraints": [],
        "preferences": []
      }
    }
  }
}
```

`context` contains only the canonical semantic buckets `targets`, `constraints`, and `preferences`.
Domain inputs such as `location`, `serviceType`, and `serviceClass` are modelled under `context.constraints` because they restrict where and what must be fulfilled.

## Internal event expression baseline
Internally, events use the same native context grouping without the external TMF expression wrapper, for example:

```json
{
  "body": {
    "expression": {
      "context": {
        "targets": [],
        "constraints": [],
        "preferences": []
      }
    }
  }
}
```

## IntentSpecification context characteristic baseline
`IntentSpecification.specCharacteristic` exposes a single high-level `context` CharacteristicSpecification with example/default values for:

- `context.targets`
- `context.constraints`
- `context.preferences`

Detailed validation remains in the external expression-value schema referenced by `targetEntitySchema.@schemaLocation`.

## Lifecycle/state baseline
Valid Intent lifecycle states include:

- `InProgress`
- `Active`
- `Degraded`
- `Failed`
- `Terminated`
- `Rejected`

## Effective version baseline
Once an Intent version becomes `Active`, it becomes the `effectiveVersion`, even if it later degrades or fails. Rolling back from a failed active version to an earlier version requires another orchestration/control cycle; the network will not automatically reactivate the old version by itself.

## Cross-service platform baselines

- Apply ETag / optimistic concurrency consistently.
- Require `If-Match` for protected update/delete operations where stale updates matter.
- Use `412 Precondition Failed` with standard error body on stale/mismatched ETag.
- Use GET caching consistently where safe.
- Use the common circuit-breaker response pattern:
  - `503 Service Unavailable` when no safe fallback can preserve contract meaning.
  - `200 OK` with a valid degraded response when a safe degraded fallback preserves contract meaning.
- Infrastructure access must explicitly capture security controls: authenticated service identity, least-privilege access, encrypted connectivity, no wildcard/admin access by default, approved secret/certificate management and rotation, environment-scoped roles, audit/monitoring of failures and privileged operations, and clear producer/consumer/read/write ownership.
