# End-to-End Solution Brief — Optimisation Platform

## 1. Business context:

The optimisation platform provides a reusable capability for running deterministic optimisation problems using Gurobi-backed models.

The platform is not limited to the intent-management domain. It is designed as a generic optimisation capability that can be used by OEX, platform services, planning tools, assurance functions, intent-management flows, and other authorised entities that need to run optimisation.

The business need is to allow authorised consumers to discover available optimisation capabilities, understand the required request contract, submit optimisation requests asynchronously, monitor execution state, cancellation active requests where needed, retrial failed requests, and retrieve final outcomes without exposing internal solver details or Gurobi model implementation.

The solution separates the **definition of optimisation capabilities** from the **execution and lifecycle control of optimisation runs**.

---

## 2. Solution summary:

- The solution provides a reusable, asynchronous optimisation platform backed by deterministic Gurobi models.

- It uses two core microservices:
  - **OD MS** owns `OptimisationSpecification` and exposes the caller-facing request contract.
  - **OC MS** owns runtime `Optimisation` lifecycle, cancellation, retrial, event integration, and result projection.

- Consumers may include **OEX**, platform services, planning tools, assurance functions, intent-management flows, or other authorised entities that need to run optimisation.

- OEX layer:
  - **OEX UI** provides the user-facing optimisation experience.
  - **OGW** is the user-context-aware gateway that invokes OSB MS using mTLS and User Context JWT.
  - **OSB MS / Optimisation Screen Builder MS** is the context-aware OEX facade/backend-for-frontend for optimisation journeys. It shapes OEX screens and actions using the User Context JWT, initially proxies runtime optimisation journeys to OC MS through NGW, and later supports governed OD MS catalogue/specification journeys through NGW.


- Operator access to OEX is governed by the ACG approval process and Microsoft Entra ID SSO.

- OGW exposes OEX APIs for the OEX UI using user-context-aware OAuth2. OWG calls OSB MS using mTLS and User Context JWT. OSB MS reaches backend OD MS and OC MS APIs through NGW using mTLS and OAuth2 system-to-system.

- OC MS validates only request structure and the OD MS request contract, then returns `202 Accepted` and drives execution asynchronously through Kafka.

- Kafka carries worker instructions and outcomes, with a dedicated DLQ for unprocessable events.

- The Python/Gurobi worker consumes `EXECUTE` or `CANCEL` instructions, runs or cancels optimisation work, and returns `SUCCESS`, `INFEASIBLE`, or `FAILURE` outcomes.

- NGW-exposed backend APIs are TMF-compliant. OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.

---

## 3. Solution elaboration:

The solution is structured around a clean separation of responsibility.

OD MS acts as the governed catalogue of optimisation capabilities. It exposes only what callers need to know to submit valid optimisation requests. It does not expose Gurobi objectives, candidate resource rules, solver configuration, model bindings, or internal formulation details.

OC MS acts as the runtime controller. It accepts requests, validates the request shape and request contract, creates runtime optimisation resources, manages lifecycle state, publishes worker instructions, consumes worker outcomes, and projects final results.

The Python/Gurobi worker is responsible for executing the internal deterministic optimisation model. It consumes events from Kafka, executes or cancels work based on the instruction, and publishes outcome events back to Kafka.

### 3.1 Use case view:

| **Use case** | **Actor** | **Summary** | **Outcome** |
|---|---|---|---|
| Manage optimisation catalogue | Optimisation domain engineer | Create, update, activate, retire, and govern `OptimisationSpecification` records after agreement with broader E2E teams. This is an internal governed capability within the optimisation domain, not a general consumer capability. | Only approved optimisation domain engineers can define or change catalogue entries, and catalogue changes are governed before specifications become ACTIVE. |
| Discover optimisation capability | User / OEX / platform service | Retrieve available `OptimisationSpecification` records from OD MS and understand required constraints, targets, and context. | Caller knows which optimisation capability to use and the required request contract. |
| Create runtime optimisation | User / OEX / platform service | Submit a runtime `Optimisation` request to OC MS using an ACTIVE specification and valid constraints, targets, and context. | OC MS returns `202 Accepted` and creates an `ACKNOWLEDGED` optimisation. |
| Monitor optimisation | User / OEX / platform service | Read current lifecycle state and result when available. | Caller can see whether the optimisation is pending, processing, completed, infeasible, failed, cancelling, or cancelled. |
| Cancellation optimisation | User / OEX / platform service | Request cancellation for an eligible active optimisation. | OC MS moves the resource to `CANCELLING` and instructs the worker to cancellation where safely possible. |
| Retrial failed optimisation | User / OEX / platform service | Retrial a `FAILED` optimisation by creating a new linked optimisation. | A new `ACKNOWLEDGED` optimisation is created with `retrialOf` pointing to the failed one. |
| Execute optimisation | Python/Gurobi worker | Consume worker instruction and execute the deterministic optimisation model. | Worker emits `SUCCESS`, `INFEASIBLE`, or `FAILURE` outcome. |

Note: In this optimisation platform, the governed specification resource is `OptimisationSpecification`.

### 3.2 Logical view:

The logical integration model is:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
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

UI -> OGW:
  OGW acts as the user-context-aware gateway for OEX APIs.

OGW -> OEX APIs:
  Uses user SSO OAuth2 and propagates user context.

OGW -> OSB MS:
  Uses mTLS and User Context JWT.

OSB MS -> NGW:
  Uses mTLS and OAuth2 system-to-system.

NGW -> OD MS:
  Uses mTLS to expose OptimisationSpecification APIs.

NGW -> OC MS:
  Uses mTLS to expose runtime Optimisation APIs.

OC MS -> OD MS:
  Uses mTLS for internal service-to-service validation.

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
User
-> OGW
-> OEX APIs
-> OSB MS(OEX API)
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
-> User polls GET /optimisation/{id}
```

Detailed flow:

```text
1. Consumer submits an optimisation request through the OEX experience or another authorised integration path.
2. User-facing access is handled through OGW and OEX APIs.
3. OGW invokes OSB MS with mTLS and User Context JWT.
4. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
5. NGW routes the request to OC MS.
6. OC MS validates request structure.
7. OC MS calls OD MS over mTLS to validate the referenced ACTIVE OptimisationSpecification.
8. OC MS validates constraints[], targets[], and context[] against the OD MS request contract.
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

#### 3.3.2 Cancellation optimisation:

```text
User
-> OGW
-> OEX APIs
-> OSB MS(OEX API)
-> NGW
-> OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/cancellation with If-Match.
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

#### 3.3.3 Retrial failed optimisation:

```text
User
-> OGW
-> OEX APIs
-> OSB MS(OEX API)
-> NGW
-> OC MS
-> OC MS DB
-> OC MS Outbox
-> Kafka
-> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/retrial with If-Match.
2. Request reaches OC MS through the authorised gateway path.
3. OC MS validates original Optimisation lifecycleStatus = FAILED.
4. OC MS creates a new Optimisation resource.
5. New Optimisation links to the original through retrialOf.
6. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED.
7. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
8. Worker processes the new request.
```

---

## 4. Capability matrix:

| **Component** | **Responsibility** |
|---|---|
| **Microsoft Entra ID** | Provides SSO authentication for users before they access OEX. Supplies identity context used by the user-facing access path. |
| **ACG approval process** | Governs operator access to OEX. Users must be approved through the organisational access-control process before they can use the OEX optimisation experience. |
| **OGW** | User-context-aware gateway for OEX APIs and OEX UI integration. Uses user SSO OAuth2 from the UI/OEX API path and propagates user identity context into the OEX layer. |
| **OEX UI** | Provides the user/operator-facing experience for discovering optimisation capabilities, submitting requests, monitoring state, cancelling, retrying, and viewing results. |
| **OWG** | Secures internal OEX access to OSB MS using mTLS and User Context JWT. Preserves user context across the OEX backend interaction. |
| **OSB MS** | Builds and orchestrates the OEX screen/backend experience. Integrates with NGW using mTLS and OAuth2 system-to-system to call backend optimisation APIs. |
| **NGW** | NAAS Gateway exposing backend optimisation domain APIs for OD MS and OC MS. Provides the controlled backend API entry point for OSB MS and other authorised system consumers. NGW-exposed backend APIs are TMF-compliant. |
| **Optimisation-Definition-MS / OD MS** | Owns the definition side of the optimisation platform through `OptimisationSpecification`. Publishes caller-facing request contracts, manages `DRAFT`, `ACTIVE`, and `RETIRED` specification lifecycle, and ensures only one ACTIVE specification exists per `specificationKey`. Does not expose solver/model internals. |
| **OD MS Database** | Stores `OptimisationSpecification` records, version metadata, lifecycle state, request contracts, timestamps, ETag/revision data, and retained retired specifications for audit/history. |
| **Optimisation-Controller-MS / OC MS** | Owns runtime `Optimisation` resources. Accepts requests, validates the generic wrapper and OD MS request contract, manages lifecycle, cancellation, retrial, outbox/inbox integration, and result projection. Performs syntactic and contract validation only. |
| **OC MS Database** | Stores runtime `Optimisation` resources, accepted constraints, targets, and context, optional `sourceContext`, lifecycle state, status reasons, result projections, retrial links, timestamps, ETag/revision data, outbox records, and inbox records. |
| **OC MS Outbox Relay** | Publishes persisted OC MS outbox records to Kafka after DB commit. Publishes `OptimisationRequestedEvent` with `instruction = EXECUTE` or `instruction = CANCEL`. |
| **Kafka topic** | Main internal event stream for worker instructions and outcomes between OC MS and the Python/Gurobi worker. Uses CloudEvents-style Kafka headers. |
| **Kafka DLQ** | Holds events that cannot be safely processed after retrial handling. Preserves original event payload and failure metadata for operational investigation and replay decisions. |
| **Python / Gurobi Worker** | Consumes `OptimisationRequestedEvent`. For `EXECUTE`, resolves the internal deterministic model binding, resolves required data, executes optimisation, and emits an outcome. For `CANCEL`, cancels/stops/ignores processing where safely possible. |
| **Internal deterministic optimisation models** | Own solver-specific logic that is not exposed externally. Encapsulate objective formulation, constraints, candidate-resource rules, model binding, solver configuration, and Gurobi formulation. |
| **Gurobi Optimizer** | Executes the mathematical optimisation model prepared by the worker/model layer. Produces solve outcomes that the worker maps into `SUCCESS`, `INFEASIBLE`, or `FAILURE`. |
| **Analytics platform / data sources** | Provides authorised datasets required by the worker/model layer, such as topology snapshots, traffic forecasts, capacity information, inventory data, or other optimisation context datasets. |
| **OC MS Inbox Consumer** | Consumes worker outcome events, applies idempotency and stale/late-event handling, maps outcomes to lifecycle states, and projects result/failure details into the runtime `Optimisation` resource. |
| **Operational support / monitoring** | Monitors service health, Kafka lag, outbox/inbox processing, worker failures, solver failures, DLQ records, retrial counts, stale/late events, and optimisation lifecycle/result trends. |

---

## 5. Solution security:

### 5.1 User authentication and access governance:

Users access the OEX experience through the organisational ACG approval process and SSO using Microsoft Entra ID.

```text
User
-> ACG approval process
-> Microsoft Entra ID SSO
-> OGW
-> OEX UI
```

OGW is the user-context-aware gateway for the OEX channel. It uses user SSO OAuth2 from the UI/OEX API path and propagates user identity context into the OEX layer.

### 5.2 OEX internal access path:

OWG integrates with the OSB MS using:

```text
mTLS
User Context JWT
```

This preserves user context while securely invoking OEX backend experience services.

```text
OGW / OEX APIs
-> OSB MS(OEX API)
```

### 5.3 OEX to optimisation backend access:

OSB MS integrates with NGW using:

```text
mTLS
OAuth2 system-to-system
```

NGW exposes backend optimisation domain APIs for OD MS and OC MS.

```text
OSB MS
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

OC MS calls OD MS to validate referenced `OptimisationSpecification` resources. This internal service-to-service communication is secured using mTLS through service mesh.

```text
OC MS
-> mTLS
-> OD MS
```

OC MS uses this call to validate:

```text
OptimisationSpecification exists
OptimisationSpecification lifecycleStatus = ACTIVE
constraints[], targets[], and context[] match the OD MS request contract
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
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
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

OD MS exposes only the caller-facing request contract.

OC MS exposes runtime state and generic result outputs.

The worker and internal model layer own the solver-specific details.

---

## 6. Important quality attributes:

### 6.1 Availability:

OD MS and OC MS should be deployed as independently scalable and highly available services.

OD MS availability is important for capability discovery and request validation. OC MS availability is critical for runtime optimisation creation, lifecycle reads, cancellation, retrial, and event projection.

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
| Invalid or stale context datasets | Poor, infeasible, or failed optimisation outcomes. | Use request contract validation, dataset versioning, worker diagnostics, and operational monitoring. |
| DLQ growth | Indicates poison messages, schema drift, or repeated processing failures. | Monitor DLQ, preserve failure metadata, and define replay/remediation procedures. |
| Misconfigured internal model binding | OD MS may expose a valid request contract while worker execution fails. | Add deployment validation, contract tests between OD MS and worker model binding, and pre-production model checks. |
| Overexposure of solver details | Sensitive optimisation logic could leak externally. | Keep OD MS limited to caller-facing request contracts and keep solver details internal. |
| Incorrect specification activation | Wrong `ACTIVE` specification may affect all new requests for a `specificationKey`. | Use ETag/If-Match, lifecycle governance, review/approval, and only one ACTIVE version per key. |
| Complex access path through OEX gateways | Misconfiguration could break user context propagation or backend access. | Use clear contract testing across OGW, OWG, Screen Builder MS, NGW, OD MS, and OC MS. |

---

## 8. Assumptions:

- Operators access OEX only after ACG approval.

- User/operator authentication uses Microsoft Entra ID SSO.

- OGW is the user-context-aware gateway for OEX APIs and OEX UI integration.

- OWG integrates with OSB MS using mTLS and User Context JWT.

- OSB MS integrates with NGW using mTLS and OAuth2 system-to-system.

- NGW exposes OD MS and OC MS APIs to authorised backend consumers.

- NGW integrates with OD MS and OC MS using mTLS.

- OC MS calls OD MS using mTLS for internal service-to-service validation.

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

- OD MS exposes only the caller-facing `OptimisationSpecification` request contract.

- OC MS performs syntactic and OD-MS-contract validation only.

- Runtime `Optimisation` does not expose a `version` field.

- Runtime `Optimisation` does not support client-side `PUT` or `DELETE`.

- Cancellation is represented through `lifecycleStatus = CANCELLING` and an `OptimisationRequestedEvent` with `instruction = CANCEL`.

- Only one `ACTIVE` `OptimisationSpecification` is allowed per `specificationKey`.

- ETag / If-Match is required for unsafe runtime operations such as cancellation and retrial.

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
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
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

---


TMF/TIO alignment note:
Backend optimisation API examples use platform-readable constraint fields such as `constraintType: maximum` with `ontologyPredicate: icm:atMost` where semantic traceability to TMF/TIO upper-bound intent expressions is useful.

---

## Optimisation validation and outcome clarification:

The active design distinguishes request-contract validation from optimiser outcome.

```text
OC MS validates:
  required fields
  enum/value-type rules
  request contract shape
  cardinality rules such as candidateResources minItems = 2

OC MS does not evaluate:
  solver feasibility
  candidate ranking
  metric-vs-constraint fit
  objective trade-offs

Worker/model returns:
  SUCCESS
  INFEASIBLE
  FAILURE
```

Use `422 OPTIMISATION_CONTRACT_VIOLATION` for contract/cardinality failures, such as fewer than 2 candidate resources for a selection optimisation. Use `INFEASIBLE` only when the request is valid and the worker/model determines no feasible solution exists.

---

## Contract definition versus runtime values:

OD MS defines the optimisation request contract, including the allowed candidate resource structure under `context[]`.

OC MS carries the actual runtime `constraints[]`, `targets[]`, and `context[]` values accepted from the caller. For resource/path selection, the runtime context should include or reference candidate resources as defined by OD MS.

---

## Definition versus runtime contract naming:

OD MS defines the optimisation request contract using:

```text
constraintSpecifications[]
targetSpecifications[]
contextSpecifications[]
```

OC MS carries the runtime request instance using:

```text
constraints[]
targets[]
context[]
```

This keeps the design clear: OD MS defines what is allowed; OC MS stores and returns what was accepted at runtime.

---

## Corrected process view baseline:

The agreed runtime process view is:

```text
User
-> OEX
-> OGW
-> OEX APIs
-> OSB MS(OEX API)
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
-> User polls GET /optimisation/{id}
```

Detailed interpretation:

```text
1. Consumer initiates the optimisation journey through OEX.
2. OEX routes the request to OGW.
3. OGW routes to OEX APIs.
4. OEX APIs route through OWG.
5. OGW routes to OSB MS.
6. OSB MS calls NGW.
7. NGW calls OC MS.
8. OC MS validates the runtime request against the ACTIVE OptimisationSpecification from OD MS.
9. OC MS persists the accepted runtime Optimisation in OC MS DB.
10. OC MS writes OptimisationRequestedEvent to OC MS Outbox in the same transaction.
11. OC MS Outbox relay publishes the event to Kafka.
12. Python/Gurobi Worker consumes the event from Kafka.
13. Python/Gurobi Worker invokes Gurobi Optimizer.
14. Worker publishes outcome event back to Kafka.
15. OC MS Inbox consumes the outcome event from Kafka.
16. OC MS Inbox updates OC MS DB with lifecycle/result projection.
17. User polls GET /optimisation/{id} to retrieve current status/result.
```

Runtime request model:

```text
constraints[]
targets[]
context[]
```

Runtime contract validation:

```text
OC MS validates runtime constraints[], targets[], and context[] against the ACTIVE OD MS OptimisationSpecification.
OC MS validates structure, required fields, value types, supported names, supported enum values, and cardinality such as candidateResources minItems = 2.
OC MS does not perform solver feasibility, metric-vs-constraint evaluation, candidate ranking, or objective trade-off evaluation.
```

Outcome projection:

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
```

Process view compliance rule:

```text
NGW-exposed OC MS and OD MS APIs are TMF-compliant.
OEX / OGW / OEX APIs / OWG / OSB MS are experience-layer/private integration components and do not need to be TMF-compliant.
Kafka events are internal contracts and do not need to be TMF-compliant unless separately required.
```

---

## Infrastructure security controls across solution briefs:

The E2E solution brief and each individual service design brief must explicitly capture security controls for every service-to-infrastructure integration.

This applies to:

```text
service-to-database
service-to-cache
service-to-Kafka
service-to-object-storage
service-to-search-index
service-to-queue
service-to-platform-service
```

Required controls:

```text
Authentication:
  Every connecting workload uses an approved service identity.

Authorisation:
  Access is least privilege.
  Permissions are scoped to the required resource and operation.
  No broad wildcard, cluster-wide, schema-wide, or admin/root access by default.

Encrypted connectivity:
  Transport is encrypted.
  mTLS is used where supported and appropriate.
  Kafka broker connectivity uses TLS/mTLS where supported; Kafka ACLs enforce topic/consumer-group authorisation.

Secret and certificate management:
  Credentials, keys, tokens, and certificates are stored in approved secret management.
  Rotation is supported without application code changes where possible.

Environment separation:
  Principals, roles, credentials, topics, schemas, and namespaces are environment-scoped.

Audit and monitoring:
  Authentication failures, authorisation denials, privileged operations, replay/admin actions, Kafka lag, DLQ growth, and unusual infrastructure access are logged and monitored.

Ownership:
  Each design brief identifies the owning service, resource owner, allowed operations, and operational support path.
```

Current application:

```text
OD MS design brief:
  captures OD MS -> OD MS DB controls.
  states OD MS has no direct Kafka integration in the current baseline.

OC MS design brief:
  captures OC MS -> OC MS DB controls.
  captures OC MS -> OD MS mTLS controls.
  captures OC MS -> Kafka controls for outbox/inbox.

E2E solution brief:
  captures common cross-cutting infrastructure security controls.
  summarises database, Kafka, cache/future-infrastructure, identity, encryption, ACL, secret-management, and audit requirements.
```

---

## Logical view baseline:

The logical integration model is:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Definition-management logical path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS
```

Runtime-optimisation logical path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

---

## Runtime process view baseline:

For readability, the runtime process view is shown as:

```text
User
-> OEX UI
-> OGW
-> OSB MS (OEX APIs)
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
-> User polls GET /optimisation/{id}
```

Meaning:

```text
OSB MS (OEX APIs):
  OSB MS is the optimisation-specific OEX backend/API facade behind OGW.

OC MS DB:
  Runtime Optimisation persistence.

OC MS Outbox:
  Durable event publication pattern for worker instructions.

OC MS Inbox:
  Durable/idempotent worker outcome consumption and projection.
```

---

## Use case sequence diagrams:

Each use case in the use case view has a matching sequence diagram below.

### Discover optimisation capability sequence:

```mermaid
sequenceDiagram
    actor User
    participant OEX as OEX UI
    participant OGW as OGW
    participant OSB as OSB MS (OEX APIs)
    participant NGW as NGW
    participant OD as OD MS

    User->>OEX: Open optimisation capability discovery
    OEX->>OGW: Request available capabilities
    OGW->>OSB: Invoke with User Context JWT
    OSB->>OSB: Validate context and shape request
    OSB->>NGW: GET backend capability data
    NGW->>OD: GET /optimisationSpecification
    OD-->>NGW: ACTIVE OptimisationSpecification records
    NGW-->>OSB: Specification response
    OSB-->>OGW: Context-filtered capability model
    OGW-->>OEX: Capability cards / discovery view
    OEX-->>User: Display available optimisation capabilities
```

### Manage optimisation catalogue sequence:

```mermaid
sequenceDiagram
    actor User
    participant OEX as OEX UI
    participant OGW as OGW
    participant OSB as OSB MS (OEX APIs)
    participant NGW as NGW
    participant OD as OD MS
    participant ODDB as OD MS DB

    User->>OEX: Open catalogue management journey
    OEX->>OGW: Submit catalogue create/update/activate/retire action
    OGW->>OSB: Invoke with User Context JWT
    OSB->>OSB: Validate approved optimisation domain engineer role
    OSB->>NGW: Forward governed catalogue request
    NGW->>OD: Call OptimisationSpecification API
    OD->>OD: Authorise catalogue operation
    OD->>ODDB: Persist specification change / lifecycle transition
    ODDB-->>OD: Commit success
    OD-->>NGW: Updated OptimisationSpecification
    NGW-->>OSB: Backend response
    OSB-->>OGW: UI-friendly catalogue response
    OGW-->>OEX: Catalogue screen update
    OEX-->>User: Show catalogue result / approval status
```

### Create runtime optimisation sequence:

```mermaid
sequenceDiagram
    actor User
    participant OEX as OEX UI
    participant OGW as OGW
    participant OSB as OSB MS (OEX APIs)
    participant NGW as NGW
    participant OC as OC MS
    participant OD as OD MS
    participant OCDB as OC MS DB
    participant Outbox as OC MS Outbox
    participant Kafka as Kafka
    participant Worker as Python/Gurobi Worker
    participant Gurobi as Gurobi Optimizer

    User->>OEX: Submit optimisation request
    OEX->>OGW: POST create optimisation
    OGW->>OSB: Invoke with User Context JWT
    OSB->>OSB: Validate context and shape request
    OSB->>NGW: POST backend optimisation request
    NGW->>OC: POST /optimisation
    OC->>OD: Validate ACTIVE OptimisationSpecification
    OD-->>OC: Specification contract valid
    OC->>OCDB: Persist ACKNOWLEDGED Optimisation
    OC->>Outbox: Write OptimisationRequestedEvent EXECUTE
    OCDB-->>OC: Commit success
    OC-->>NGW: 202 Accepted + Location + ETag
    NGW-->>OSB: Accepted response
    OSB-->>OGW: UI-friendly accepted response
    OGW-->>OEX: Accepted response
    OEX-->>User: Show submitted / pending status
    Outbox->>Kafka: Publish EXECUTE event
    Kafka->>Worker: Deliver EXECUTE event
    Worker->>Gurobi: Run optimisation model
```

### Monitor optimisation sequence:

```mermaid
sequenceDiagram
    actor User
    participant OEX as OEX UI
    participant OGW as OGW
    participant OSB as OSB MS (OEX APIs)
    participant NGW as NGW
    participant OC as OC MS
    participant OCDB as OC MS DB

    User->>OEX: Open optimisation status/result
    OEX->>OGW: GET optimisation status/detail
    OGW->>OSB: Invoke with User Context JWT
    OSB->>OSB: Validate context and access to optimisation
    OSB->>NGW: GET backend optimisation detail
    NGW->>OC: GET /optimisation/{id}
    OC->>OCDB: Read runtime Optimisation
    OCDB-->>OC: Lifecycle/result state
    OC-->>NGW: Runtime Optimisation resource
    NGW-->>OSB: Backend response
    OSB-->>OGW: UI-friendly status/result view
    OGW-->>OEX: Status/result response
    OEX-->>User: Display current lifecycle and result if available
```

### Cancellation optimisation sequence:

```mermaid
sequenceDiagram
    actor User
    participant OEX as OEX UI
    participant OGW as OGW
    participant OSB as OSB MS (OEX APIs)
    participant NGW as NGW
    participant OC as OC MS
    participant OCDB as OC MS DB
    participant Outbox as OC MS Outbox
    participant Kafka as Kafka
    participant Worker as Python/Gurobi Worker

    User->>OEX: Request cancellation
    OEX->>OGW: POST cancellation with current ETag
    OGW->>OSB: Invoke with User Context JWT
    OSB->>OSB: Validate context and action visibility
    OSB->>NGW: Forward cancellation with If-Match
    NGW->>OC: POST /optimisation/{id}/cancellation
    OC->>OC: Validate ETag and lifecycleStatus
    OC->>OCDB: Update lifecycleStatus = CANCELLING
    OC->>Outbox: Write OptimisationRequestedEvent CANCEL
    OCDB-->>OC: Commit success
    OC-->>NGW: 202 Accepted CANCELLING
    NGW-->>OSB: Backend response
    OSB-->>OGW: UI-friendly cancellation response
    OGW-->>OEX: Cancellation accepted
    OEX-->>User: Show cancelling status
    Outbox->>Kafka: Publish CANCEL event
    Kafka->>Worker: Deliver CANCEL instruction
    Worker->>Worker: Stop/cancel/ignore where safely possible
```

### Retrial failed optimisation sequence:

```mermaid
sequenceDiagram
    actor User
    participant OEX as OEX UI
    participant OGW as OGW
    participant OSB as OSB MS (OEX APIs)
    participant NGW as NGW
    participant OC as OC MS
    participant OCDB as OC MS DB
    participant Outbox as OC MS Outbox
    participant Kafka as Kafka
    participant Worker as Python/Gurobi Worker

    User->>OEX: Request retrial of failed optimisation
    OEX->>OGW: POST retrial with current ETag
    OGW->>OSB: Invoke with User Context JWT
    OSB->>OSB: Validate context and action visibility
    OSB->>NGW: Forward retrial with If-Match
    NGW->>OC: POST /optimisation/{id}/retrial
    OC->>OC: Validate original lifecycleStatus = FAILED
    OC->>OCDB: Create new ACKNOWLEDGED Optimisation with retrialOf
    OC->>Outbox: Write OptimisationRequestedEvent EXECUTE for new Optimisation
    OCDB-->>OC: Commit success
    OC-->>NGW: 202 Accepted + new Location
    NGW-->>OSB: Backend response
    OSB-->>OGW: UI-friendly retrial response
    OGW-->>OEX: New optimisation accepted
    OEX-->>User: Show new optimisation status
    Outbox->>Kafka: Publish EXECUTE event
    Kafka->>Worker: Deliver EXECUTE event
```

### Execute optimisation sequence:

```mermaid
sequenceDiagram
    participant Kafka as Kafka
    participant Worker as Python/Gurobi Worker
    participant Gurobi as Gurobi Optimizer
    participant OutcomeKafka as Kafka
    participant Inbox as OC MS Inbox
    participant OCDB as OC MS DB

    Kafka->>Worker: Deliver OptimisationRequestedEvent EXECUTE
    Worker->>Worker: Resolve model binding and input context
    Worker->>Gurobi: Execute deterministic optimisation model
    Gurobi-->>Worker: Solver result
    alt Success
        Worker->>OutcomeKafka: Publish OptimisationCompletedEvent SUCCESS
        OutcomeKafka->>Inbox: Deliver outcome
        Inbox->>OCDB: Project lifecycleStatus = COMPLETED and result
    else Infeasible
        Worker->>OutcomeKafka: Publish OptimisationCompletedEvent INFEASIBLE
        OutcomeKafka->>Inbox: Deliver outcome
        Inbox->>OCDB: Project lifecycleStatus = INFEASIBLE
    else Failure
        Worker->>OutcomeKafka: Publish OptimisationFailedEvent FAILURE
        OutcomeKafka->>Inbox: Deliver outcome
        Inbox->>OCDB: Project lifecycleStatus = FAILED
    end
```
