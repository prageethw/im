# End-to-End Solution Brief — Optimisation Platform

## 1. Business context:

The optimisation platform provides a reusable capability for running deterministic optimisation problems using Gurobi-backed models. The platform is not limited to the intent-management domain. It is designed as a generic optimisation capability that can be used by OEX, platform services, planning tools, assurance functions, intent-management flows, and other authorised entities that need to run optimisation.

The business need is to allow authorised consumers to discover available optimisation capabilities, understand the required request contract, submit optimisation requests asynchronously, monitor execution state, cancel active requests where needed, retry failed requests, and retrieve outcomes without exposing internal solver details or Gurobi model implementation.

The solution separates the **definition of optimisation capabilities** from the **execution and lifecycle control of optimisation runs**:

- **OD MS** owns governed `OptimisationSpecification` resources and the runtime request contract.
- **OC MS** owns runtime `Optimisation` resources and short-lived optimisation execution lifecycle.
- **OSB MS** provides the OEX-facing optimisation journey facade/backend-for-frontend.
- **OEX UI** provides the user-facing optimisation experience.
- **Python/Gurobi workers** execute deterministic optimisation models behind the internal event boundary.

---

## 2. Solution summary:

- The solution provides a reusable, asynchronous optimisation platform backed by deterministic Gurobi models.
- External-facing backend APIs are **TMF ontology-aligned** in style, resource structure, expression pattern, polymorphism fields, and extension semantics.
- The external optimiser domain concept is **Optimisation**, not Intent.
- A runtime `Optimisation` is a short-lived run. It completes, becomes infeasible, fails, or is cancelled. It is not a long-running desired-state intent control loop by default.
- The solution uses two core optimisation-domain microservices:
  - **OD MS** owns `OptimisationSpecification` and exposes the caller-facing request contract.
  - **OC MS** owns runtime `Optimisation` lifecycle, cancellation, retrial, event integration, and result projection.
- Consumers may include **OEX**, platform services, planning tools, assurance functions, intent-management flows, or other authorised entities that need to run optimisation.
- OEX layer:
  - **OEX UI** provides the user-facing optimisation experience.
  - **OGW** is the user-context-aware gateway that invokes OSB MS using mTLS and User Context JWT.
  - **OSB MS / Optimisation Screen Builder MS** is the context-aware OEX facade/backend-for-frontend for optimisation journeys.
  - OSB MS shapes OEX screens and actions using the User Context JWT, initially proxies runtime optimisation journeys to OC MS through NGW, and later supports governed OD MS catalogue/specification journeys through NGW.
- Operator access to OEX is governed by the ACG approval process and Microsoft Entra ID SSO.
- OGW exposes OEX APIs for the OEX UI using user-context-aware OAuth2.
- OGW calls OSB MS using mTLS and User Context JWT.
- OSB MS reaches backend OD MS and OC MS APIs through NGW using mTLS and OAuth2 system-to-system.
- OD MS exposes a synchronous REST API only in the initial baseline. `/hub` subscription and outbound `OptimisationSpecification` events are deferred until concrete requirements emerge.
- OD MS `OptimisationSpecification` is the optimiser-domain equivalent of TMF `IntentSpecification`.
- OD MS uses TMF-aligned structures: `specCharacteristic[]`, `expressionSpecification`, and `targetEntitySchema`.
- OC MS validates the runtime request wrapper and the active OD MS request contract, then creates and drives runtime execution asynchronously through Kafka.
- Kafka carries worker instructions and outcomes, with a dedicated DLQ for unprocessable events.
- The Python/Gurobi worker consumes `EXECUTE` or `CANCEL` instructions, runs or cancels optimisation work, and emits `OptimisationCompletedEvent` with status `COMPLETED`, `INFEASIBLE`, or `FAILED`.
- NGW-exposed backend APIs are TMF ontology-aligned. OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.
- Non-standard additions on external/backend APIs must be labelled as approved platform extensions. Current OD examples include `_links` for HATEOAS and `PUT /optimisationSpecification/{id}` for full replacement/finalisation of mutable `DRAFT` specifications.

---

## 3. Solution elaboration:

The solution is structured around a clean separation of responsibility.

OD MS acts as the governed catalogue of optimisation capabilities. It exposes only what callers need to know to submit valid optimisation requests. It does not expose Gurobi objectives, candidate resource rules, solver configuration, model bindings, or internal formulation details.

OC MS acts as the runtime controller. It accepts requests, validates the request shape and request contract, creates runtime optimisation resources, manages lifecycle state, publishes worker instructions, consumes worker outcomes, and projects final results.

The Python/Gurobi worker is responsible for executing the internal deterministic optimisation model. It consumes events from Kafka, executes or cancels work based on the instruction, and publishes outcome events back to Kafka.


Backend optimisation API examples use platform-readable optimisation fields while preserving TMF ontology-aligned structure, expression pattern, polymorphism fields, and extension semantics. Detailed standard validation should reference the relevant TMF921 / TR292 material when a specific external API/resource/event decision is being baselined.

Runtime Optimisation requests use the canonical expression shape described in Appendix 10.10. Runtime lifecycle states, terminal outcomes, and outcome mapping are described in Appendix 10.11.

Non-standard additions on external/backend APIs must be labelled as approved platform extensions and must not break standard resource and operation responsibilities. Internal Kafka events and private service-to-service APIs do not need to use TMF REST representation fields.

### 3.1 Use case view:

| **No.** | **Use case** | **Actor** | **Summary** | **Outcome** |
|---:|---|---|---|---|
| 1 | Discover optimisation capability | User / OEX / platform service | Retrieve available `OptimisationSpecification` records from OD MS and understand supported `context.targets[]`, `context.constraints[]`, and `context.preferences[]`. | Caller knows which optimisation capability to use and the required request contract. |
| 2 | Create optimisation specification | Optimisation domain engineer | Create a new governed `OptimisationSpecification` in OD MS after agreement with broader E2E teams, including request-contract metadata such as `specCharacteristic[]`, `expressionSpecification`, `targetEntitySchema`, and lifecycle/governance details. | A new `OptimisationSpecification` is created in `DRAFT` state and is not usable for runtime optimisation until it is reviewed and activated. |
| 3 | Activate optimisation specification | Optimisation domain engineer / authorised platform role | Activate a complete `DRAFT` specification after OD validation. | The selected version becomes `ACTIVE`; any previously active version in the same specification family becomes `RETIRED`. |
| 4 | Retire optimisation specification | Optimisation domain engineer / authorised platform role | Retire an `ACTIVE` specification when it must no longer be used for new runtime optimisations. | The specification becomes `RETIRED`; historical runtime references remain readable. |
| 5 | Create runtime optimisation | User / OEX / platform service | Submit a runtime `Optimisation` request to OC MS using an `ACTIVE` specification and valid expression context. | OC MS accepts/creates a short-lived optimisation run and begins asynchronous processing. |
| 6 | Monitor optimisation | User / OEX / platform service | Read current lifecycle state and result when available. | Caller can see whether the optimisation is acknowledged, queued, processing, completed, infeasible, failed, cancelling, or cancelled. |
| 7 | Cancel optimisation | User / OEX / platform service | Request cancellation for an eligible active optimisation. | OC MS moves the resource to `CANCELLING` and instructs the worker to cancel where safely possible. |
| 8 | Retry failed optimisation | User / OEX / platform service | Retry a `FAILED` optimisation by creating a new linked optimisation. | A new `ACKNOWLEDGED` optimisation is created with `retrialOf` pointing to the failed one. |
| 9 | Execute optimisation | Python/Gurobi worker | Consume worker instruction and execute the deterministic optimisation model. | Worker emits `OptimisationCompletedEvent` with status `COMPLETED`, `INFEASIBLE`, or `FAILED`. |

### 3.2 Logical view:

The logical integration model is:

```text
1. User -> OEX UI
2. OEX UI -> Microsoft Entra ID SSO
3. Microsoft Entra ID SSO -> OGW
4. OGW -> OSB MS (OEX API)
5. OSB MS (OEX API) -> NGW
6. NGW -> OD MS / OC MS
7. OC MS -> Kafka
8. Kafka -> Python/Gurobi Worker
9. Python/Gurobi Worker -> Gurobi Optimiser
```

Key logical relationships:

```text
1. User -> Microsoft Entra ID: User authenticates using SSO after ACG approval.
2. UI -> OGW: OGW acts as the user-context-aware gateway for OEX APIs.
3. OGW -> OSB MS: Uses mTLS and User Context JWT.
4. OSB MS -> NGW: Uses mTLS and OAuth2 system-to-system.
5. NGW -> OD MS: Uses mTLS to expose OptimisationSpecification APIs.
6. NGW -> OC MS: Uses mTLS to expose runtime Optimisation APIs.
7. OC MS -> OD MS: Uses mTLS for internal service-to-service validation against ACTIVE OptimisationSpecification contracts.
8. OC MS -> Kafka: Emits OptimisationRequestedEvent with instruction EXECUTE or CANCEL.
9. Python/Gurobi Worker -> Kafka: Consumes worker instructions and emits optimisation outcomes.
10. Kafka -> OC MS: OC MS consumes worker outcomes and projects lifecycle/result.
```

Logical diagram artifact:

```text
optimisation-logical-view.drawio
```

### 3.3 Process view:

Each use case has a matching process flow. The process flows are intentionally more detailed than the logical view so that ownership, validation, persistence, eventing, and asynchronous execution responsibilities are clear.

#### 3.3.1 Discover optimisation capability:

```text
1. User / OEX / platform service -> OGW
2. OGW -> OSB MS(OEX API)
3. OSB MS(OEX API) -> NGW
4. NGW -> OD MS
5. OD MS -> OD MS DB
6. OD MS DB -> OD MS
7. OD MS -> NGW
8. NGW -> OSB MS(OEX API)
9. OSB MS(OEX API) -> OGW
10. OGW -> User / OEX / platform service receives available optimisation capabilities
```

Detailed flow:

```text
1. User, OEX, or another authorised platform service requests available optimisation capabilities.
2. Request reaches OGW.
3. OGW invokes OSB MS(OEX API) using mTLS and User Context JWT where user context is applicable.
4. OSB MS shapes the discovery request and applies user-context-aware filtering where applicable.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the discovery request to OD MS.
7. OD MS reads ACTIVE OptimisationSpecification records from OD MS DB.
8. OD MS returns caller-facing capability and request-contract metadata, including specCharacteristic[], expressionSpecification, and targetEntitySchema.
9. NGW returns the response to OSB MS.
10. OSB MS shapes the response for the OEX/API consumer.
11. Caller receives available optimisation capabilities and understands which request contract to use.
```

#### 3.3.2 Create optimisation specification:

```text
1. Optimisation domain engineer -> OGW
2. OGW -> OSB MS(OEX API)
3. OSB MS(OEX API) -> NGW
4. NGW -> OD MS
5. OD MS -> OD MS DB
6. OD MS DB -> OD MS
7. OD MS -> NGW
8. NGW -> OSB MS(OEX API)
9. OSB MS(OEX API) -> OGW
10. OGW -> Optimisation domain engineer receives DRAFT OptimisationSpecification result
```

Detailed flow:

```text
1. Approved optimisation domain engineer starts a catalogue/specification creation journey after agreement with broader E2E teams.
2. Request reaches OGW.
3. OGW invokes OSB MS(OEX API) using mTLS and User Context JWT.
4. OSB MS validates the user context and confirms the user is allowed to access catalogue-management capabilities.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the create request to OD MS.
7. OD MS authenticates and authorises the catalogue operation.
8. OD MS validates the OptimisationSpecification request shape, including TMF-aligned resource fields, specCharacteristic[], expressionSpecification, and targetEntitySchema.
9. OD MS persists the new OptimisationSpecification in OD MS DB with lifecycleStatus = DRAFT.
10. OD MS returns the created DRAFT OptimisationSpecification with Location and ETag where applicable.
11. NGW returns the response to OSB MS.
12. OSB MS shapes the catalogue-management response for the OEX experience.
13. Optimisation domain engineer receives the DRAFT OptimisationSpecification result.
14. The DRAFT specification is not usable for runtime optimisation until reviewed and activated under OD MS governance.
```

#### 3.3.3 Activate optimisation specification:

```text
1. Optimisation domain engineer -> OGW
2. OGW -> OSB MS(OEX API)
3. OSB MS(OEX API) -> NGW
4. NGW -> OD MS
5. OD MS -> OD MS DB
6. OD MS DB -> OD MS
7. OD MS -> NGW
8. NGW -> OSB MS(OEX API)
9. OSB MS(OEX API) -> OGW
10. OGW -> Optimisation domain engineer receives ACTIVE OptimisationSpecification result
```

Detailed flow:

```text
1. Authorised optimisation domain engineer requests activation of a completed DRAFT OptimisationSpecification.
2. Request reaches OGW.
3. OGW invokes OSB MS(OEX API) using mTLS and User Context JWT.
4. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
5. NGW routes the governed activation request to OD MS.
6. OD MS validates If-Match for the DRAFT specification.
7. OD MS validates the full OptimisationSpecification, including specCharacteristic[], expressionSpecification, and targetEntitySchema.
8. OD MS changes the selected version from DRAFT to ACTIVE.
9. OD MS atomically moves any previously ACTIVE version in the same specification family to RETIRED.
10. OD MS ensures there is at most one ACTIVE version per specification family.
11. OD MS returns the activated OptimisationSpecification with updated ETag and lifecycle-aware _links.
```

#### 3.3.4 Create and execute optimisation:

```text
1. User -> OEX UI
2. OEX UI -> OGW
3. OGW -> OSB MS(OEX API)
4. OSB MS(OEX API) -> NGW
5. NGW -> OC MS
6. OC MS -> OD MS
7. OD MS -> OC MS DB
8. OC MS DB -> OC MS Outbox
9. OC MS Outbox -> Kafka
10. Kafka -> Python/Gurobi Worker
11. Python/Gurobi Worker -> Gurobi Optimiser
12. Gurobi Optimiser -> Kafka
13. Kafka -> OC MS Inbox
14. OC MS Inbox -> OC MS DB
15. OC MS DB -> User polls GET /optimisation/{id}
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
8. OC MS validates expression.expressionValue.context.targets[], constraints[], and preferences[] against the OD MS targetEntitySchema.
9. OC MS persists the accepted runtime Optimisation with lifecycleStatus = ACKNOWLEDGED in OC MS DB.
10. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE to OC MS Outbox in the same transaction.
11. OC MS Outbox relay publishes the event to Kafka.
12. Python/Gurobi Worker consumes the event from Kafka.
13. Python/Gurobi Worker resolves internal deterministic model binding.
14. Python/Gurobi Worker invokes Gurobi Optimiser.
15. Worker publishes OptimisationCompletedEvent back to Kafka with status `COMPLETED`, `INFEASIBLE`, or `FAILED`.
16. OC MS Inbox consumes the worker outcome event.
17. OC MS Inbox updates OC MS DB with lifecycle and result projection.
18. User polls GET /optimisation/{id} through OGW -> OSB MS(OEX API) -> NGW -> OC MS to retrieve current status/result.
```

#### 3.3.5 Monitor optimisation:

```text
1. User / OEX / platform service -> OGW
2. OGW -> OSB MS(OEX API)
3. OSB MS(OEX API) -> NGW
4. NGW -> OC MS
5. OC MS -> OC MS DB
6. OC MS DB -> OC MS
7. OC MS -> NGW
8. NGW -> OSB MS(OEX API)
9. OSB MS(OEX API) -> OGW
10. OGW -> User / OEX / platform service receives current lifecycle/result
```

Detailed flow:

```text
1. User, OEX, or another authorised platform service requests current optimisation status or result.
2. Request reaches OGW.
3. OGW invokes OSB MS(OEX API) using mTLS and User Context JWT where user context is applicable.
4. OSB MS validates access to the requested optimisation view.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes GET /optimisation/{id} to OC MS.
7. OC MS reads the runtime Optimisation from OC MS DB.
8. OC MS returns lifecycleStatus, status reason, result projection, failure details, or links/actions where applicable.
9. NGW returns the response to OSB MS.
10. OSB MS shapes a user-friendly status/result model.
11. Caller receives current lifecycle/result state.
12. No OC MS Outbox record is written and no worker instruction is emitted for read-only monitoring.
```

#### 3.3.6 Cancel optimisation:

```text
1. User -> OEX UI
2. OEX UI -> OGW
3. OGW -> OSB MS(OEX API)
4. OSB MS(OEX API) -> NGW
5. NGW -> OC MS
6. OC MS -> OC MS DB
7. OC MS DB -> OC MS Outbox
8. OC MS Outbox -> Kafka
9. Kafka -> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/cancellation with If-Match.
2. Request reaches OGW.
3. OGW invokes OSB MS(OEX API) using mTLS and User Context JWT.
4. OSB MS exposes or forwards the cancellation action only when the user context and runtime state allow it.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the cancellation request to OC MS.
7. OC MS validates ETag.
8. OC MS checks lifecycleStatus is ACKNOWLEDGED, QUEUED, or PROCESSING.
9. OC MS updates lifecycleStatus to CANCELLING in the OC MS DB.
10. OC MS writes OptimisationRequestedEvent with instruction = CANCEL to OC MS Outbox.
11. OC MS Outbox relay publishes event to Kafka.
12. Python/Gurobi Worker consumes CANCEL instruction.
13. Worker stops, cancels, or ignores work where safely possible.
14. OC MS eventually projects CANCELLED when cancellation is confirmed or safely resolved.
```

#### 3.3.7 Retry failed optimisation:

```text
1. User -> OEX UI
2. OEX UI -> OGW
3. OGW -> OSB MS(OEX API)
4. OSB MS(OEX API) -> NGW
5. NGW -> OC MS
6. OC MS -> OC MS DB
7. OC MS DB -> OC MS Outbox
8. OC MS Outbox -> Kafka
9. Kafka -> Python/Gurobi Worker
```

Detailed flow:

```text
1. Consumer calls POST /optimisation/{id}/retrial with If-Match.
2. Request reaches OGW.
3. OGW invokes OSB MS(OEX API) using mTLS and User Context JWT.
4. OSB MS exposes or forwards the retrial action only when the user context and runtime state allow it.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the retrial request to OC MS.
7. OC MS validates original Optimisation lifecycleStatus = FAILED.
8. OC MS creates a new Optimisation resource in the OC MS DB.
9. New Optimisation links to the original through retrialOf.
10. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED.
11. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
12. OC MS Outbox relay publishes the event to Kafka.
13. Python/Gurobi Worker processes the new request.
14. Retrial does not move the failed Optimisation back to PROCESSING.
```

#### 3.3.8 Gurobi execute optimisation:

```text
1. Kafka -> Python/Gurobi Worker
2. Python/Gurobi Worker -> Gurobi Optimiser
3. Gurobi Optimiser -> Kafka
4. Kafka -> OC MS Inbox
5. OC MS Inbox -> OC MS DB
6. OC MS DB -> User polls GET /optimisation/{id}
```

Detailed flow:

```text
1. Python/Gurobi Worker consumes OptimisationRequestedEvent with instruction = EXECUTE from Kafka.
2. Worker validates event idempotency and execution eligibility.
3. Worker resolves the required runtime context and internal deterministic model binding.
4. Worker invokes Gurobi Optimiser.
5. Gurobi Optimiser returns solver output or failure information.
6. Worker maps the solver outcome to OptimisationCompletedEvent status `COMPLETED`, `INFEASIBLE`, or `FAILED`.
7. Worker publishes OptimisationCompletedEvent to Kafka.
8. OC MS Inbox consumes the worker outcome event.
9. OC MS Inbox applies idempotency and stale/late-event checks.
10. OC MS Inbox updates OC MS DB with lifecycle/result projection.
11. User observes the outcome through GET /optimisation/{id}.
```

---
## 4. Capability matrix:

| **Component** | **Responsibility** |
|---|---|
| **Microsoft Entra ID** | Provides SSO authentication for users before they access OEX. Supplies the identity context used by the user-facing access path. |
| **ACG approval process** | Governs operator access to OEX. Users must be approved through the organisational access-control process before they can use the OEX optimisation experience. |
| **OGW** | User-context-aware gateway for OEX APIs and OEX UI integration. Uses user SSO OAuth2 from the UI path and propagates user identity context into the OEX layer, north-bound protected with user OAuth2 token and south-bound protected with mTLS plus user context tokens. |
| **OEX UI** | Provides the user/operator-facing experience for discovering optimisation capabilities, submitting requests, monitoring state, cancelling, retrying, and viewing results. |
| **OSB MS** | Builds and orchestrates the OEX screen/backend experience. Integrates with NGW using mTLS and OAuth2 system-to-system to call backend optimisation APIs, north-bound protected with mTLS and user context tokens. |
| **NGW** | NAAS Gateway exposing backend optimisation domain APIs for OD MS and OC MS. Provides the controlled backend API entry point for OSB MS and other authorised system consumers. NGW-exposed backend APIs are TMF ontology-aligned. |
| **OD MS** | Owns the definition side of the optimisation platform through `OptimisationSpecification`. Publishes caller-facing request contracts, manages `DRAFT`, `ACTIVE`, and `RETIRED` specification lifecycle, and ensures only one `ACTIVE` specification exists per specification family. Defines what is allowed through `specCharacteristic[]` for catalogue/discovery/UI guidance, `expressionSpecification` for expression language and ontology IRI, and `targetEntitySchema` as the authoritative runtime `expressionValue` validation schema. Does not carry runtime values, evaluate solver feasibility, rank candidates, assess objective trade-offs, or expose solver/model internals. |
| **OD MS Database** | Stores `OptimisationSpecification` records, version metadata, lifecycle state, request contracts, timestamps, ETag/revision data, and retained retired specifications for audit/history. |
| **OC MS** | Owns runtime `Optimisation` resources. Accepts requests, validates the generic wrapper and OD MS request contract, manages lifecycle, cancellation, retrial, outbox/inbox integration, and result projection. Carries the accepted runtime values in `expression.expressionValue.context.targets[]`, `constraints[]`, and `preferences[]`. Validates required fields, enum/value-type rules, request-contract shape, cardinality rules, and runtime context against the active OD MS `targetEntitySchema`. Performs syntactic and contract validation only; it does not evaluate solver feasibility, candidate ranking, metric-vs-constraint fit, or objective trade-offs. Contract/cardinality failures use `422 OPTIMISATION_CONTRACT_VIOLATION`; `INFEASIBLE` is used only after a valid request is assessed by the worker/model and no feasible solution exists. |
| **OC MS Database** | Stores runtime `Optimisation` resources, accepted expression context, optional `sourceContext`, lifecycle state, status reasons, result projections, retrial links, timestamps, ETag/revision data, outbox records, and inbox records. |
| **OC MS Outbox Relay** | Publishes persisted OC MS outbox records to Kafka after DB commit. Publishes `OptimisationRequestedEvent` with `instruction = EXECUTE` or `instruction = CANCEL`. |
| **Kafka topic** | Main internal event stream for worker instructions and outcomes between OC MS and the Python/Gurobi worker. Uses CloudEvents-style Kafka headers. |
| **Kafka DLQ** | Holds events that cannot be safely processed after retrial handling. Preserves original event payload and failure metadata for operational investigation and replay decisions. |
| **Python / Gurobi Worker** | Consumes `OptimisationRequestedEvent`. For `EXECUTE`, resolves the internal deterministic model binding, resolves required data, executes optimisation, determines runtime solver outcome, and emits `OptimisationCompletedEvent` with status `COMPLETED`, `INFEASIBLE`, or `FAILED`. For `CANCEL`, cancels/stops/ignores processing where safely possible. |
| **Internal deterministic optimisation models** | Own solver-specific logic that is not exposed externally. Encapsulate objective formulation, constraints, candidate-resource rules, model binding, solver configuration, and Gurobi formulation. |
| **Gurobi Optimiser** | Executes the mathematical optimisation model prepared by the worker/model layer. Produces raw solver output that the worker maps into `OptimisationCompletedEvent.status` values `COMPLETED`, `INFEASIBLE`, or `FAILED`. |
| **Analytics platform/data sources** | Provides authorised datasets required by the worker/model layer, such as topology snapshots, traffic forecasts, capacity information, inventory data, or other optimisation context datasets. |
| **OC MS Inbox Consumer** | Consumes worker outcome events, applies idempotency and stale/late-event handling, maps `OptimisationCompletedEvent.status` to lifecycle states (`COMPLETED -> COMPLETED`, `INFEASIBLE -> INFEASIBLE`, `FAILED -> FAILED`), and projects result/failure details into the runtime `Optimisation` resource. |
| **Operational support/monitoring** | Monitors service health, Kafka lag, outbox/inbox processing, worker failures, solver failures, DLQ records, retrial counts, stale/late events, and optimisation lifecycle/result trends. |

---

## 5. Solution security:

### 5.1 User authentication and access governance:

Users access the OEX experience through the organisational ACG approval process and SSO using Microsoft Entra ID.

```text
User -> ACG approval process -> Microsoft Entra ID SSO -> OGW -> OEX APIs / OEX UI
```

OGW is the user-context-aware gateway for the OEX channel. It uses user SSO OAuth2 from the UI/OEX API path and propagates user identity context into the OEX layer.

### 5.2 OEX internal access path:

OGW integrates with OSB MS using:

```text
mTLS
User Context JWT
```

This preserves user context while securely invoking OEX backend experience services.

```text
OGW / OEX APIs -> OSB MS
```

### 5.3 OEX to optimisation backend access:

OSB MS integrates with NGW using:

```text
mTLS
OAuth2 system-to-system
```

NGW exposes backend optimisation domain APIs for OD MS and OC MS.

```text
OSB MS -> NGW -> OD MS / OC MS
```

OD MS and OC MS are not directly exposed to end users or the UI layer.

### 5.4 NGW to OD MS / OC MS security:

NGW integrates with OD MS and OC MS using:

```text
mTLS
```

This secures backend API access from the gateway to the optimisation domain services.

### 5.5 OC MS to OD MS service-to-service security:

OC MS calls OD MS to validate referenced `OptimisationSpecification` resources. This internal service-to-service communication is secured using mTLS through a service mesh.

```text
OC MS -> mTLS -> OD MS
```

OC MS uses this call to validate:

```text
OptimisationSpecification exists
OptimisationSpecification lifecycleStatus = ACTIVE
expression.expressionValue.context.targets[] / constraints[] / preferences[] match the OD MS targetEntitySchema
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
OC MS: produce worker instruction events, consume worker outcome events, produce DLQ records when needed
Python/Gurobi Worker: consume worker instruction events, produce worker outcome events, produce DLQ records when needed
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

Runtime `Optimisation` does not expose a business `version` field. ETag is used only as the HTTP concurrency mechanism.

OD MS unsafe existing-resource operations also require `If-Match`:

```text
PUT /optimisationSpecification/{id}
PATCH /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

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

OD MS exposes only the caller-facing request contract. OC MS exposes runtime state and generic result outputs. The worker and internal model layer own the solver-specific details.

### 5.10 Infrastructure security controls across solution briefs:

The E2E solution brief and each individual service design brief must explicitly capture security controls for every service-to-infrastructure integration. This applies to:

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
Authentication: Every connecting workload uses an approved service identity.
Authorisation: Access is least privilege. Permissions are scoped to the required resource and operation. No broad wildcard, cluster-wide, schema-wide, or admin/root access by default.
Encrypted connectivity: Transport is encrypted. mTLS is used where supported and appropriate. Kafka broker connectivity uses TLS/mTLS where supported; Kafka ACLs enforce topic/consumer-group authorisation.
Secret and certificate management: Credentials, keys, tokens, and certificates are stored in approved secret management. Rotation is supported without application code changes where possible.
Environment separation: Principals, roles, credentials, topics, schemas, and namespaces are environment-scoped.
Audit and monitoring: Authentication failures, authorisation denials, privileged operations, replay/admin actions, Kafka lag, DLQ growth, and unusual infrastructure access are logged and monitored.
Ownership: Each design brief identifies the owning service, resource owner, allowed operations, and operational support path.
```

Current application:

```text
OD MS design brief: captures OD MS -> OD MS DB controls and states OD MS has no direct Kafka integration in the current baseline.
OC MS design brief: captures OC MS -> OC MS DB controls, OC MS -> OD MS mTLS controls, and OC MS -> Kafka controls for outbox/inbox.
E2E solution brief: captures common cross-cutting infrastructure security controls and summarises database, Kafka, cache/future-infrastructure, identity, encryption, ACL, secret-management, and audit requirements.
```

---

## 6. Important quality attributes:

### 6.1 Availability:

OD MS and OC MS should be deployed as independently scalable and highly available services. OD MS availability is important for capability discovery and request validation. OC MS availability is critical for runtime optimisation creation, lifecycle reads, cancellation, retrial, and event projection.

Kafka availability is critical for asynchronous worker instruction and outcome exchange. The outbox/inbox patterns reduce data-loss risk during transient service or Kafka failures. Runtime optimisation records remain durable in OC MS DB even if worker execution is delayed. DLQ provides a controlled path for poison or unprocessable events.

### 6.2 Scalability:

OD MS scales primarily for read-heavy capability discovery. OC MS scales for runtime API traffic, outbox relay throughput, and inbox outcome processing.

Python/Gurobi workers scale horizontally based on optimisation workload, queue depth, and solver runtime characteristics. Kafka consumer groups allow worker scaling and OC MS inbox scaling. Large or long-running optimisation jobs are handled asynchronously and do not block REST API request threads.

### 6.3 Performance:

`POST /optimisation` creates a runtime optimisation resource after syntactic and OD-MS-contract validation. Solver execution is asynchronous and decoupled from REST request latency.

`GET /optimisation/{id}` provides polling of lifecycle and result state. `GET /optimisation` returns summary-only records by default to avoid large list payloads. Runtime `result` is omitted until available.

OD MS GET responses use the simple cache policy:

```text
Cache-Control: private, max-age=300
ETag: <current-resource-version>
```

The only documented OD cache override is:

```text
Cache-Control: no-cache
```

OC MS runtime responses do not use response `Cache-Control` for now unless later agreed.

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
| Incorrect specification activation | Wrong `ACTIVE` specification may affect all new requests for a specification family. | Use ETag/If-Match, lifecycle governance, review/approval, and only one ACTIVE version per family. |
| Complex access path through OEX gateways | Misconfiguration could break user context propagation or backend access. | Use clear contract testing across OGW, OSB MS, NGW, OD MS, and OC MS. |

---

## 8. Assumptions:

- Operators access OEX only after ACG approval.
- User/operator authentication uses Microsoft Entra ID SSO.
- OGW is the user-context-aware gateway for OEX APIs and OEX UI integration.
- OGW integrates with OSB MS using mTLS and User Context JWT.
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

- NGW-exposed backend APIs are TMF ontology-aligned.
- OGW-exposed OEX APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF-compliant.
- External-facing APIs/resources/events/specifications must be validated against the relevant TMF standard material before baselining.
- Non-standard additions must be labelled as approved platform extensions and must not break TMF-standard resource/operation responsibilities.
- Do not expose Gurobi model formulation, solver configuration, objective internals, candidate-resource rules, or model binding through public APIs.
- OD MS exposes only the caller-facing `OptimisationSpecification` request contract.
- OD MS is synchronous REST only for the initial baseline; no `/hub` subscription endpoints or outbound `OptimisationSpecification` events are included initially.
- OC MS performs syntactic and OD-MS-contract validation only.
- Runtime `Optimisation` does not expose a `version` field.
- Runtime `Optimisation` does not support client-side `PUT` by default.
- Cancellation is represented through `lifecycleStatus = CANCELLING` and an `OptimisationRequestedEvent` with `instruction = CANCEL`.
- Only one `ACTIVE` `OptimisationSpecification` is allowed per specification family.
- ETag / If-Match is required for unsafe runtime operations such as cancellation and retrial.
- Internal Kafka events do not use TMF REST `@type`, `@baseType`, or `@schemaLocation`.

---

## 10. Appendix:

### 10.1 OD MS endpoint summary:

```http
GET /optimisationSpecification
POST /optimisationSpecification
GET /optimisationSpecification/{id}
PUT /optimisationSpecification/{id}
PATCH /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

OD MS endpoint notes:

```text
POST always creates DRAFT.
PUT is an approved platform extension for full replacement/finalisation of mutable DRAFT specifications.
PATCH is supported for TMF compatibility but discouraged for material runtime-contract replacement.
DELETE physically deletes mutable DRAFT only; ACTIVE and RETIRED are retained, with ACTIVE retired through governed lifecycle transition.
OD MS has no /hub endpoint in the initial baseline.
```

### 10.2 OC MS endpoint summary:

```http
GET /optimisation
POST /optimisation
GET /optimisation/{id}
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
```

Current E2E assumption pending OC MS specification shaping — unsupported or deferred until OC MS shaping confirms otherwise:

```http
PUT /optimisation/{id}
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
```

### 10.6 Worker instructions:

```text
EXECUTE
CANCEL
```

### 10.7 OptimisationCompletedEvent status values:

```text
COMPLETED
INFEASIBLE
FAILED
```

### 10.8 Event status to lifecycle mapping:

```text
COMPLETED -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILED -> FAILED
```

### 10.9 Key artifacts:

```text
contextdump.md
od-ms-specification.md
oc-ms-specification.md
osb-ms-specification.md
optimisation-full-recovery-pack.md
optimisation-logical-view.drawio
optimisation-e2e-solution-brief.md
```

### 10.10 Canonical runtime expression shape:

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

Semantic meaning:

```text
context = the full optimisation scenario / problem context
targets[] = optimisation goals the optimiser tries to achieve
constraints[] = hard mandatory requirements that must be satisfied
preferences[] = soft ranking or selection preferences used to choose between otherwise valid outcomes
```

---

### 10.11 Runtime Optimisation lifecycle baseline:

Runtime Optimisation status list:

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

Status meanings:

| Status | Meaning |
|---|---|
| `ACKNOWLEDGED` | OC MS accepted the runtime optimisation request and persisted it. |
| `QUEUED` | Request is waiting for worker processing. |
| `PROCESSING` | Python/Gurobi Worker is executing or preparing the optimisation. |
| `COMPLETED` | Worker emitted `OptimisationCompletedEvent` with status `COMPLETED`; result is available. |
| `INFEASIBLE` | Worker/model determined no feasible solution exists. |
| `FAILED` | Technical/runtime failure occurred. |
| `CANCELLING` | Cancellation was requested and is being handled. |
| `CANCELLED` | Optimisation was cancelled or safely resolved as cancelled. |

Outcome mapping:

```text
COMPLETED -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILED -> FAILED
```

Lifecycle transition baseline:

```text
ACKNOWLEDGED -> QUEUED -> PROCESSING -> COMPLETED
ACKNOWLEDGED -> QUEUED -> PROCESSING -> INFEASIBLE
ACKNOWLEDGED -> QUEUED -> PROCESSING -> FAILED
ACKNOWLEDGED -> CANCELLING -> CANCELLED
QUEUED -> CANCELLING -> CANCELLED
PROCESSING -> CANCELLING -> CANCELLED
FAILED -> retrial creates new ACKNOWLEDGED Optimisation
```

Transition rules:

| From | To | Trigger |
|---|---|---|
| `ACKNOWLEDGED` | `QUEUED` | OC MS outbox event is ready/published for worker execution. |
| `QUEUED` | `PROCESSING` | Worker starts or claims execution. |
| `PROCESSING` | `COMPLETED` | Worker emits `OptimisationCompletedEvent` with status `COMPLETED`. |
| `PROCESSING` | `INFEASIBLE` | Worker returns `INFEASIBLE`. |
| `PROCESSING` | `FAILED` | Worker emits `OptimisationCompletedEvent` with status `FAILED` or a technical failure is projected. |
| `ACKNOWLEDGED` / `QUEUED` / `PROCESSING` | `CANCELLING` | User requests cancellation through `POST /optimisation/{id}/cancellation`. |
| `CANCELLING` | `CANCELLED` | Cancellation is confirmed or safely resolved. |
| `FAILED` | new `ACKNOWLEDGED` | User requests retrial through `POST /optimisation/{id}/retrial`; creates a new Optimisation. |

Retrial rule:

```text
Retrial does not move FAILED back to PROCESSING.
Retrial creates a new runtime Optimisation resource with retrialOf pointing to the failed one.
```

### 10.12 Internal event baseline:

The optimiser platform uses exactly two internal Kafka event types between OC MS and the Python/Gurobi worker in the current baseline. These are platform-internal events and do not use TMF REST resource fields such as `@type`, `@baseType`, or `@schemaLocation`.

| Event | Emitter | Consumer | Purpose | Key values |
|---|---|---|---|---|
| `OptimisationRequestedEvent` | OC MS Outbox Relay | Python/Gurobi Worker | Instructs the worker to execute or cancel a runtime optimisation. | `instruction = EXECUTE` or `instruction = CANCEL` |
| `OptimisationCompletedEvent` | Python/Gurobi Worker | OC MS Inbox Consumer | Reports terminal worker outcome for lifecycle/result projection. | `status = COMPLETED`, `FAILED`, or `INFEASIBLE` |

`OptimisationFailedEvent` is not used in the current baseline. Failed and infeasible outcomes are carried by `OptimisationCompletedEvent.status`.

