# End-to-End Solution Brief — Optimisation Platform

## 1. Business context

The optimisation platform provides a reusable capability for running deterministic optimisation problems using Gurobi-backed models. The platform is not limited to the intent-management domain. It is designed as a generic optimisation capability that can be used by OEX, platform services, planning tools, assurance functions, intent-management flows, and other authorised entities that need to run optimisation.

The business need is to allow authorised consumers to discover available optimisation capabilities, understand the required request contract, submit optimisation requests asynchronously, monitor execution state, cancel active requests where needed, retry failed requests, and retrieve outcomes without exposing internal solver details or Gurobi model implementation.

The solution separates the definition of optimisation capabilities from the execution and lifecycle control of optimisation runs.

## 2. Solution summary

- The solution provides a reusable, asynchronous optimisation platform backed by deterministic Gurobi models.
- External-facing backend APIs are TMF921/TIO-aligned in resource style, expression pattern, event/subscription pattern where used, and extension semantics.
- The optimiser domain concept is **Optimisation**, not Intent.
- Optimisation runs are short-lived. They complete, fail, become infeasible, or are cancelled. They are not long-running desired-state control loops.
- OD MS owns `OptimisationSpecification` and exposes the caller-facing request contract.
- OC MS owns the runtime `Optimisation` lifecycle, cancellation, retrial, event integration, and result projection.
- OEX UI provides the user-facing optimisation experience.
- OGW is the user-context-aware gateway that invokes OSB MS using mTLS and User Context JWT.
- OSB MS / Optimisation Screen Builder MS is the context-aware OEX facade/backend-for-frontend for optimisation journeys.
- OSB MS reaches backend OD MS and OC MS APIs through NGW using mTLS and OAuth2 system-to-system.
- OC MS validates only the request structure and the OD MS request contract, then returns `202 Accepted` and drives execution asynchronously through Kafka.
- The Python/Gurobi worker consumes `EXECUTE` or `CANCEL` instructions, runs or cancels optimisation work, and returns `SUCCESS`, `INFEASIBLE`, or `FAILURE` outcomes.
- NGW-exposed backend APIs are TMF/TIO-aligned. OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.

## 3. Use case view

| Use case | Actor | Summary | Outcome |
|---|---|---|---|
| Discover optimisation capability | User / OEX / platform service | Retrieve available `OptimisationSpecification` records from OD MS and understand required targets, constraints, preferences, and context. | Caller knows which optimisation capability to use and the required request contract. |
| Create optimisation specification | Optimisation domain engineer | Create a new governed `OptimisationSpecification` in OD MS after agreement with broader E2E teams. | A new `OptimisationSpecification` is created in `DRAFT` state and is not usable for runtime optimisation until reviewed and activated. |
| Create runtime optimisation | User / OEX / platform service | Submit a runtime `Optimisation` request to OC MS using an ACTIVE specification and valid expression context. | OC MS returns `202 Accepted` and creates an `ACKNOWLEDGED` optimisation. |
| Monitor optimisation | User / OEX / platform service | Read current lifecycle state and result when available. | Caller can see whether the optimisation is pending, processing, completed, infeasible, failed, cancelling, or cancelled. |
| Cancellation optimisation | User / OEX / platform service | Request cancellation for an eligible active optimisation. | OC MS moves the resource to `CANCELLING` and instructs the worker to cancel where safely possible. |
| Retrial failed optimisation | User / OEX / platform service | Retrial a `FAILED` optimisation by creating a new linked optimisation. | A new `ACKNOWLEDGED` optimisation is created with `retrialOf` pointing to the failed one. |
| Execute optimisation | Python/Gurobi worker | Consume worker instruction and execute the deterministic optimisation model. | Worker emits `SUCCESS`, `INFEASIBLE`, or `FAILURE` outcome. |

## 4. Logical view

```text
User -> OEX UI -> Microsoft Entra ID SSO -> OGW -> OSB MS (OEX API) -> NGW -> OD MS / OC MS -> Kafka -> Python/Gurobi Worker -> Gurobi Optimiser
```

Key logical relationships:

```text
User -> Microsoft Entra ID: User authenticates using SSO after ACG approval.
UI -> OGW: OGW acts as the user-context-aware gateway for OEX APIs.
OGW -> OSB MS: Uses mTLS and User Context JWT.
OSB MS -> NGW: Uses mTLS and OAuth2 system-to-system.
NGW -> OD MS: Uses mTLS to expose OptimisationSpecification APIs.
NGW -> OC MS: Uses mTLS to expose runtime Optimisation APIs.
OC MS -> OD MS: Uses mTLS for internal service-to-service validation.
OC MS -> Kafka: Emits OptimisationRequestedEvent with instruction EXECUTE or CANCEL.
Python/Gurobi Worker -> Kafka: Consumes worker instructions and emits optimisation outcomes.
OC MS <- Kafka: Consumes worker outcomes and projects lifecycle/result.
```

## 5. Process view highlights

### 5.1 Create and execute optimisation

```text
User -> OEX UI -> OGW -> OSB MS(OEX API) -> NGW -> OC MS -> OD MS -> OC MS DB -> OC MS Outbox -> Kafka -> Python/Gurobi Worker -> Gurobi Optimiser -> Kafka -> OC MS Inbox -> OC MS DB -> User polls GET /optimisation/{id}
```

Detailed flow:

```text
1. User initiates the optimisation journey via UI.
2. User request reaches OGW.
3. OGW invokes OSB MS(OEX API) using mTLS and User Context JWT.
4. OSB MS validates the User Context JWT and shapes the request/action model.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the request to OC MS.
7. OC MS calls OD MS over mTLS to validate the referenced ACTIVE OptimisationSpecification and request contract.
8. OC MS validates expression.expressionValue.context.targets[], constraints[], and preferences[] against the OD MS request contract.
9. OC MS persists the accepted runtime Optimisation with lifecycleStatus = ACKNOWLEDGED in OC MS DB.
10. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE to OC MS Outbox in the same transaction.
11. OC MS Outbox relay publishes the event to Kafka.
12. Python/Gurobi Worker consumes the event from Kafka.
13. Python/Gurobi Worker resolves internal deterministic model binding.
14. Python/Gurobi Worker invokes Gurobi Optimiser.
15. Worker publishes OptimisationCompletedEvent or OptimisationFailedEvent back to Kafka.
16. OC MS Inbox consumes the worker outcome event.
17. OC MS Inbox updates OC MS DB with lifecycle and result projection.
18. User polls GET /optimisation/{id} through OGW -> OSB MS(OEX API) -> NGW -> OC MS to retrieve current status/result.
```

### 5.2 Retrial failed optimisation

```text
User -> OEX UI -> OGW -> OSB MS(OEX API) -> NGW -> OC MS -> OC MS DB -> OC MS Outbox -> Kafka -> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/retrial with If-Match.
2. OC MS validates original Optimisation lifecycleStatus = FAILED.
3. OC MS creates a new Optimisation resource in the OC MS DB.
4. New Optimisation links to the original through retrialOf.
5. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED.
6. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
7. Retrial does not move the failed Optimisation back to PROCESSING.
```

## 6. Canonical lifecycle and outcome mapping

Runtime Optimisation lifecycle states:

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

OD MS OptimisationSpecification lifecycle states:

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DEPRECATED` state for OptimisationSpecification.

## 7. Canonical runtime expression shape

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

## 8. Constraints

- NGW-exposed backend APIs are TMF/TIO-aligned.
- OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.
- Do not expose Gurobi model formulation, solver configuration, objective internals, candidate-resource rules, or model binding through public APIs.
- OD MS exposes only the caller-facing `OptimisationSpecification` request contract.
- OC MS performs syntactic and OD-MS-contract validation only.
- Runtime `Optimisation` does not expose a `version` field.
- Runtime `Optimisation` does not support client-side `PUT` or `DELETE`.
- Cancellation is represented through `lifecycleStatus = CANCELLING` and an `OptimisationRequestedEvent` with `instruction = CANCEL`.
- Only one `ACTIVE` `OptimisationSpecification` is allowed per `specificationKey`.
- ETag / If-Match is required for unsafe runtime operations such as cancellation and retrial.
- Internal Kafka events do not use TMF REST `@type`, `@baseType`, or `@schemaLocation`.
