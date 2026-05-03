# End-to-End Solution Brief — Optimisation Platform

## 1. Business context:

The optimisation platform provides a reusable capability for running deterministic optimisation problems using Gurobi-backed models.

The platform is not limited to the intent-management domain. It is designed as a generic optimisation capability that can be used by OEX, platform services, planning tools, assurance functions, intent-management flows, and other authorised entities that need to run optimisation.

The business need is to allow authorised consumers to discover available optimisation capabilities, understand the required input contract, submit optimisation requests asynchronously, monitor execution state, cancel active requests where needed, retry failed requests, and retrieve final outcomes without exposing internal solver details or Gurobi model implementation.

The solution separates the **definition of optimisation capabilities** from the **execution and lifecycle control of optimisation runs**.

---

## 2. Solution summary:

- The solution provides a reusable, asynchronous optimisation platform backed by deterministic Gurobi models.

- It uses two core microservices:
  - **OD MS** owns `OptimisationSpecification` and exposes the caller-facing input contract.
  - **OC MS** owns runtime `Optimisation` lifecycle, cancellation, retry, event integration, and result projection.

- Consumers may include **OEX**, platform services, planning tools, assurance functions, intent-management flows, or other authorised entities that need to run optimisation.

- Operator access to OEX is governed by the ACG approval process and Microsoft Entra ID SSO.

- OGW exposes OEX APIs for the OEX UI using user-context-aware OAuth2. OEX GW calls OEX Screen Builder MS using mTLS and User Context JWT. OEX Screen Builder MS reaches backend OD MS and OC MS APIs through NGW using mTLS and OAuth2 system-to-system.

- OC MS validates only request structure and the OD MS input contract, then returns `202 Accepted` and drives execution asynchronously through Kafka.

- Kafka carries worker instructions and outcomes, with a dedicated DLQ for unprocessable events.

- The Python/Gurobi worker consumes `EXECUTE` or `CANCEL` instructions, runs or cancels optimisation work, and returns `SUCCESS`, `INFEASIBLE`, or `FAILURE` outcomes.

- NGW-exposed backend APIs are TMF-compliant. OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.

---

## 3. Solution elaboration:

The solution is structured around a clean separation of responsibility.

OD MS acts as the governed catalogue of optimisation capabilities. It exposes only what callers need to know to submit valid optimisation requests. It does not expose Gurobi objectives, candidate resource rules, solver configuration, model bindings, or internal formulation details.

OC MS acts as the runtime controller. It accepts requests, validates the request shape and input contract, creates runtime optimisation resources, manages lifecycle state, publishes worker instructions, consumes worker outcomes, and projects final results.

The Python/Gurobi worker is responsible for executing the internal deterministic optimisation model. It consumes events from Kafka, executes or cancels work based on the instruction, and publishes outcome events back to Kafka.

### 3.1 Use case view:

| **Use case** | **Actor** | **Summary** | **Outcome** |
|---|---|---|---|
| Discover optimisation capability | User / OEX / platform service | Retrieve available `OptimisationSpecification` records from OD MS and understand required inputs. | Caller knows which optimisation capability to use and what inputs to provide. |
| Create runtime optimisation | User / OEX / platform service | Submit a runtime `Optimisation` request to OC MS using an ACTIVE specification and valid inputs. | OC MS returns `202 Accepted` and creates an `ACKNOWLEDGED` optimisation. |
| Monitor optimisation | User / OEX / platform service | Read current lifecycle state and result when available. | Caller can see whether the optimisation is pending, processing, completed, infeasible, failed, cancelling, or cancelled. |
| Cancel optimisation | User / OEX / platform service | Request cancellation for an eligible active optimisation. | OC MS moves the resource to `CANCELLING` and instructs the worker to cancel where safely possible. |
| Retry failed optimisation | User / OEX / platform service | Retry a `FAILED` optimisation by creating a new linked optimisation. | A new `ACKNOWLEDGED` optimisation is created with `retryOf` pointing to the failed one. |
| Execute optimisation | Python/Gurobi worker | Consume worker instruction and execute the deterministic optimisation model. | Worker emits `SUCCESS`, `INFEASIBLE`, or `FAILURE` outcome. |

### 3.2 Logical view:

The logical integration model is:

```text
User / Operator
-> Microsoft Entra ID SSO
-> OGW
-> OEX APIs / OEX UI
-> OEX GW
-> OEX Screen Builder MS
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Key logical relationships:

```text
User -> Microsoft Entra ID:
  User authenticates using SSO after ACG approval.

User / UI -> OGW:
  OGW acts as the user-context-aware gateway for OEX APIs.

OGW -> OEX APIs:
  Uses user SSO OAuth2 and propagates user context.

OEX GW -> OEX Screen Builder MS:
  Uses mTLS and User Context JWT.

OEX Screen Builder MS -> NGW:
  Uses mTLS and OAuth2 system-to-system.

NGW -> OD MS:
  Uses mTLS to expose OptimisationSpecification APIs.

NGW -> OC MS:
  Uses mTLS to expose runtime Optimisation APIs.

OC MS -> OD MS:
  Uses Istio mTLS for internal service-to-service validation.

OC MS -> Kafka:
  Emits OptimisationRequestedEvent with instruction EXECUTE or CANCEL.

Python/Gurobi Worker -> Kafka:
  Consumes worker instructions and emits optimisation outcomes.

OC MS <- Kafka:
  Consumes worker outcomes and projects lifecycle/result.
```

Logical diagram artifact:

```text
optimisation-logical-view.drawio
```

### 3.3 Process view:

#### 3.3.1 Create and execute optimisation:

```text
Consumer / OEX
-> OGW
-> OEX APIs
-> OEX GW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OD MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
-> Kafka
-> OC MS Inbox
-> OC MS DB
-> Consumer polls GET /optimisation/{id}
```

Detailed flow:

```text
1. Consumer submits an optimisation request through the OEX experience or another authorised integration path.
2. User-facing access is handled through OGW and OEX APIs.
3. OEX GW invokes OEX Screen Builder MS with mTLS and User Context JWT.
4. OEX Screen Builder MS calls NGW using mTLS and OAuth2 system-to-system.
5. NGW routes the request to OC MS.
6. OC MS validates request structure.
7. OC MS calls OD MS over Istio mTLS to validate the referenced ACTIVE OptimisationSpecification.
8. OC MS validates inputs[] against the OD MS input contract.
9. OC MS persists runtime Optimisation with lifecycleStatus = ACKNOWLEDGED.
10. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE to outbox.
11. Outbox relay publishes event to Kafka.
12. Python/Gurobi worker consumes event.
13. Worker resolves internal deterministic model binding.
14. Worker runs Gurobi.
15. Worker publishes OptimisationCompletedEvent or OptimisationFailedEvent.
16. OC MS inbox consumes worker outcome.
17. OC MS updates lifecycle and result.
18. Consumer retrieves result through GET /optimisation/{id}.
```

#### 3.3.2 Cancel optimisation:

```text
Consumer / OEX
-> OGW
-> OEX APIs
-> OEX GW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/cancel with If-Match.
2. Request reaches OC MS through the authorised gateway path.
3. OC MS validates ETag.
4. OC MS checks lifecycleStatus is ACKNOWLEDGED, QUEUED, or PROCESSING.
5. OC MS updates lifecycleStatus to CANCELLING.
6. OC MS writes OptimisationRequestedEvent with instruction = CANCEL to outbox.
7. Outbox relay publishes event to Kafka.
8. Worker consumes CANCEL instruction.
9. Worker stops, cancels, or ignores work where safely possible.
10. OC MS eventually projects CANCELLED when cancellation is confirmed or safely resolved.
```

#### 3.3.3 Retry failed optimisation:

```text
Consumer / OEX
-> OGW
-> OEX APIs
-> OEX GW
-> OEX Screen Builder MS
-> NGW
-> OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/retry with If-Match.
2. Request reaches OC MS through the authorised gateway path.
3. OC MS validates original Optimisation lifecycleStatus = FAILED.
4. OC MS creates a new Optimisation resource.
5. New Optimisation links to the original through retryOf.
6. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED.
7. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
8. Worker processes the new request.
```

---

## 4. Capability matrix:

| **Component** | **Responsibility** |
|---|---|
| **Microsoft Entra ID** | Provides SSO authentication for users/operators before they access OEX. Supplies identity context used by the user-facing access path. |
| **ACG approval process** | Governs operator access to OEX. Users must be approved through the organisational access-control process before they can use the OEX optimisation experience. |
| **OGW** | User-context-aware gateway for OEX APIs and OEX UI integration. Uses user SSO OAuth2 from the UI/OEX API path and propagates user identity context into the OEX layer. |
| **OEX APIs / OEX UI** | Provides the user/operator-facing experience for discovering optimisation capabilities, submitting requests, monitoring state, cancelling, retrying, and viewing results. |
| **OEX GW** | Secures internal OEX access to OEX Screen Builder MS using mTLS and User Context JWT. Preserves user context across the OEX backend interaction. |
| **OEX Screen Builder MS** | Builds and orchestrates the OEX screen/backend experience. Integrates with NGW using mTLS and OAuth2 system-to-system to call backend optimisation APIs. |
| **NGW** | NAAS Gateway exposing backend optimisation domain APIs for OD MS and OC MS. Provides the controlled backend API entry point for OEX Screen Builder MS and other authorised system consumers. NGW-exposed backend APIs are TMF-compliant. |
| **Optimisation-Definition-MS / OD MS** | Owns the definition side of the optimisation platform through `OptimisationSpecification`. Publishes caller-facing input contracts, manages `DRAFT`, `ACTIVE`, and `RETIRED` specification lifecycle, and ensures only one ACTIVE specification exists per `specificationKey`. Does not expose solver/model internals. |
| **OD MS Database** | Stores `OptimisationSpecification` records, version metadata, lifecycle state, input contracts, timestamps, ETag/revision data, and retained retired specifications for audit/history. |
| **Optimisation-Controller-MS / OC MS** | Owns runtime `Optimisation` resources. Accepts requests, validates the generic wrapper and OD MS input contract, manages lifecycle, cancellation, retry, outbox/inbox integration, and result projection. Performs syntactic and contract validation only. |
| **OC MS Database** | Stores runtime `Optimisation` resources, accepted inputs, optional `sourceContext`, lifecycle state, status reasons, result projections, retry links, timestamps, ETag/revision data, outbox records, and inbox records. |
| **OC MS Outbox Relay** | Publishes persisted OC MS outbox records to Kafka after DB commit. Publishes `OptimisationRequestedEvent` with `instruction = EXECUTE` or `instruction = CANCEL`. |
| **Kafka topic** | Main internal event stream for worker instructions and outcomes between OC MS and the Python/Gurobi worker. Uses CloudEvents-style Kafka headers. |
| **Kafka DLQ** | Holds events that cannot be safely processed after retry handling. Preserves original event payload and failure metadata for operational investigation and replay decisions. |
| **Python / Gurobi Worker** | Consumes `OptimisationRequestedEvent`. For `EXECUTE`, resolves the internal deterministic model binding, resolves required data, executes optimisation, and emits an outcome. For `CANCEL`, cancels/stops/ignores processing where safely possible. |
| **Internal deterministic optimisation models** | Own solver-specific logic that is not exposed externally. Encapsulate objective formulation, constraints, candidate-resource rules, model binding, solver configuration, and Gurobi formulation. |
| **Gurobi Optimizer** | Executes the mathematical optimisation model prepared by the worker/model layer. Produces solve outcomes that the worker maps into `SUCCESS`, `INFEASIBLE`, or `FAILURE`. |
| **Analytics platform / data sources** | Provides authorised datasets required by the worker/model layer, such as topology snapshots, traffic forecasts, capacity information, inventory data, or other optimisation input datasets. |
| **OC MS Inbox Consumer** | Consumes worker outcome events, applies idempotency and stale/late-event handling, maps outcomes to lifecycle states, and projects result/failure details into the runtime `Optimisation` resource. |
| **Operational support / monitoring** | Monitors service health, Kafka lag, outbox/inbox processing, worker failures, solver failures, DLQ records, retry counts, stale/late events, and optimisation lifecycle/result trends. |

---

## 5. Solution security:

### 5.1 User authentication and access governance:

Users/operators access the OEX experience through the organisational ACG approval process and SSO using Microsoft Entra ID.

```text
User / Operator
-> ACG approval process
-> Microsoft Entra ID SSO
-> OGW
-> OEX APIs / OEX UI
```

OGW is the user-context-aware gateway for the OEX channel. It uses user SSO OAuth2 from the UI/OEX API path and propagates user identity context into the OEX layer.

### 5.2 OEX internal access path:

OEX GW integrates with the OEX Screen Builder MS using:

```text
mTLS
User Context JWT
```

This preserves user context while securely invoking OEX backend experience services.

```text
OGW / OEX APIs
-> OEX GW
-> OEX Screen Builder MS
```

### 5.3 OEX to optimisation backend access:

OEX Screen Builder MS integrates with NGW using:

```text
mTLS
OAuth2 system-to-system
```

NGW exposes backend optimisation domain APIs for OD MS and OC MS.

```text
OEX Screen Builder MS
-> NGW
-> OD MS / OC MS
```

OD MS and OC MS are not directly exposed to end users or the UI layer.

### 5.4 NGW to OD MS / OC MS security:

NGW integrates with OD MS and OC MS using:

```text
mTLS
```

This secures backend API access from the gateway to the optimisation domain services.

### 5.5 OC MS to OD MS service-to-service security:

OC MS calls OD MS to validate referenced `OptimisationSpecification` resources. This internal service-to-service communication is secured using mTLS through Istio.

```text
OC MS
-> Istio mTLS
-> OD MS
```

OC MS uses this call to validate:

```text
OptimisationSpecification exists
OptimisationSpecification lifecycleStatus = ACTIVE
inputs[] match the OD MS input contract
```

### 5.6 Kafka security:

OC MS and the Python/Gurobi worker integrate through Kafka.

Recommended controls:

```text
TLS for broker connectivity
service identity for producers and consumers
topic-level ACLs
separate consumer groups
DLQ access restricted to operational support
```

Producer/consumer permissions:

```text
OC MS:
  produce worker instruction events
  consume worker outcome events
  produce DLQ records when needed

Python/Gurobi Worker:
  consume worker instruction events
  produce worker outcome events
  produce DLQ records when needed
```

### 5.7 API concurrency control:

ETags are used for unsafe runtime actions.

```text
POST /optimisation/{id}/cancel
POST /optimisation/{id}/retry
```

Both require:

```text
If-Match
```

Failure rules:

```text
Missing If-Match -> 428 Precondition Required
Stale/wrong If-Match -> 412 Precondition Failed
```

Runtime `Optimisation` does not expose a `version` field. ETag is used only as the HTTP concurrency mechanism.

### 5.8 Event security and integrity:

Internal Kafka events use CloudEvents-style headers:

```text
ce-specversion
ce-id
ce-type
ce-source
ce-time
ce-subject
ce-datacontenttype
ce-correlationid
ce-eventversion
content-type
```

Kafka events do not use TMF REST fields such as:

```text
@type
@baseType
@schemaLocation
```

Those fields are reserved for public REST resource representations.

### 5.9 Sensitive information boundary:

The public APIs and Kafka events do not expose:

```text
Gurobi model formulation
solver configuration
objective internals
candidate-resource rules
internal model bindings
resource-selection logic
```

OD MS exposes only the caller-facing input contract.

OC MS exposes runtime state and generic result outputs.

The worker and internal model layer own the solver-specific details.

---

## 6. Important quality attributes:

### 6.1 Availability:

OD MS and OC MS should be deployed as independently scalable and highly available services.

OD MS availability is important for capability discovery and request validation. OC MS availability is critical for runtime optimisation creation, lifecycle reads, cancellation, retry, and event projection.

Kafka availability is critical for asynchronous worker instruction and outcome exchange. The outbox/inbox patterns reduce data-loss risk during transient service or Kafka failures.

Runtime optimisation records remain durable in OC MS DB even if worker execution is delayed. DLQ provides a controlled path for poison or unprocessable events.

### 6.2 Scalability:

OD MS scales primarily for read-heavy capability discovery.

OC MS scales for runtime API traffic, outbox relay throughput, and inbox outcome processing.

Python/Gurobi workers scale horizontally based on optimisation workload, queue depth, and solver runtime characteristics.

Kafka consumer groups allow worker scaling and OC MS inbox scaling.

Large or long-running optimisation jobs are handled asynchronously and do not block REST API request threads.

### 6.3 Performance:

`POST /optimisation` returns `202 Accepted` after syntactic and OD-MS-contract validation only.

Solver execution is asynchronous and decoupled from REST request latency.

`GET /optimisation/{id}` provides polling of lifecycle and result state.

`GET /optimisation` returns summary-only records by default to avoid large list payloads.

Runtime `result` is omitted until available.

OD MS specification responses may use caching where appropriate. OC MS runtime responses do not use response `Cache-Control` for now.

---

## 7. Risks:

| **Risk** | **Impact** | **Mitigation** |
|---|---|---|
| Long-running Gurobi executions | Delayed optimisation outcomes and increased worker capacity pressure. | Use asynchronous execution, worker scaling, queue monitoring, timeout controls, and operational alerting. |
| Best-effort cancellation | A running optimisation may not stop immediately or may produce a late outcome. | Use `CANCELLING` state, worker cancellation handling, and late outcome idempotency rules. |
| Kafka consumer lag | Execution or result projection may be delayed. | Monitor consumer lag, scale workers/inbox consumers, and alert on thresholds. |
| Invalid or stale input datasets | Poor, infeasible, or failed optimisation outcomes. | Use input contract validation, dataset versioning, worker diagnostics, and operational monitoring. |
| DLQ growth | Indicates poison messages, schema drift, or repeated processing failures. | Monitor DLQ, preserve failure metadata, and define replay/remediation procedures. |
| Misconfigured internal model binding | OD MS may expose a valid input contract while worker execution fails. | Add deployment validation, contract tests between OD MS and worker model binding, and pre-production model checks. |
| Overexposure of solver details | Sensitive optimisation logic could leak externally. | Keep OD MS limited to caller-facing input contracts and keep solver details internal. |
| Incorrect specification activation | Wrong `ACTIVE` specification may affect all new requests for a `specificationKey`. | Use ETag/If-Match, lifecycle governance, review/approval, and only one ACTIVE version per key. |
| Complex access path through OEX gateways | Misconfiguration could break user context propagation or backend access. | Use clear contract testing across OGW, OEX GW, Screen Builder MS, NGW, OD MS, and OC MS. |

---

## 8. Assumptions:

- Operators access OEX only after ACG approval.

- User/operator authentication uses Microsoft Entra ID SSO.

- OGW is the user-context-aware gateway for OEX APIs and OEX UI integration.

- OEX GW integrates with OEX Screen Builder MS using mTLS and User Context JWT.

- OEX Screen Builder MS integrates with NGW using mTLS and OAuth2 system-to-system.

- NGW exposes OD MS and OC MS APIs to authorised backend consumers.

- NGW integrates with OD MS and OC MS using mTLS.

- OC MS calls OD MS using Istio mTLS for internal service-to-service validation.

- Kafka is available as the event backbone.

- Python/Gurobi worker has authorised access to required analytics/data sources.

- The worker owns internal deterministic model binding and Gurobi execution details.

- Runtime `Optimisation` is asynchronous by design.

- `sourceContext` is optional and may be omitted for generic optimisation requests.

- Runtime `Optimisation` does not expose a business `version` field.

---

## 9. Constraints:

- NGW-exposed backend APIs are TMF-compliant.

- OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.

- Do not expose Gurobi model formulation, solver configuration, objective internals, candidate-resource rules, or model binding through public APIs.

- OD MS exposes only the caller-facing `OptimisationSpecification` input contract.

- OC MS performs syntactic and OD-MS-contract validation only.

- Runtime `Optimisation` does not expose a `version` field.

- Runtime `Optimisation` does not support client-side `PUT` or `DELETE`.

- Cancellation is represented through `lifecycleStatus = CANCELLING` and an `OptimisationRequestedEvent` with `instruction = CANCEL`.

- Only one `ACTIVE` `OptimisationSpecification` is allowed per `specificationKey`.

- ETag / If-Match is required for unsafe runtime operations such as cancel and retry.

- Internal Kafka events do not use TMF REST `@type`, `@baseType`, or `@schemaLocation`.

---

## 10. Appendix:

### 10.1 OD MS endpoint summary:

```http
GET    /optimisationSpecification
POST   /optimisationSpecification
GET    /optimisationSpecification/{id}
PUT    /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

### 10.2 OC MS endpoint summary:

```http
GET  /optimisation
POST /optimisation
GET  /optimisation/{id}
POST /optimisation/{id}/cancel
POST /optimisation/{id}/retry
```

Unsupported:

```http
PUT    /optimisation/{id}
DELETE /optimisation/{id}
```

### 10.3 Runtime lifecycle states:

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

### 10.4 Kafka topics:

```text
t7.optimisation.events
t7.optimisation.events.dlq
```

### 10.5 Event types:

```text
OptimisationRequestedEvent
OptimisationCompletedEvent
OptimisationFailedEvent
```

### 10.6 Worker instructions:

```text
EXECUTE
CANCEL
```

### 10.7 Outcome values:

```text
SUCCESS
INFEASIBLE
FAILURE
```

### 10.8 Outcome mapping:

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```

### 10.9 Key artifacts:

```text
contextdump.md
od-ms-specification.md
oc-ms-specification.md
optimisation-full-recovery-pack.md
optimisation-logical-view.drawio
optimisation-e2e-solution-brief.md
```
