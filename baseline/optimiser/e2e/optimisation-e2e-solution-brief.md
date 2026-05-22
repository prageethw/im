# End-to-End Solution Brief — Optimisation Platform

## Document status:

| **Field** | **Value** |
|---|---|
| **Status** | Baseline candidate |
| **Scope** | Optimisation platform end-to-end architecture |
| **Source path** | `baseline/optimiser/e2e/optimisation-e2e-solution-brief.md` |
| **Source of truth** | GitHub `main` |
| **Last aligned** | 2026-05-21 |
| **Alignment scope** | Aligned with committed OD MS, OC MS, and OSB MS specifications. |

## Table of contents:

- [1. Business context:](#1-business-context)
- [2. Solution summary:](#2-solution-summary)
- [3. Solution elaboration:](#3-solution-elaboration)
  - [3.1. Use case view:](#31-use-case-view)
  - [3.2. Logical view:](#32-logical-view)
  - [3.3. Process view:](#33-process-view)
- [4. Capability matrix:](#4-capability-matrix)
- [5. Solution security:](#5-solution-security)
- [6. Important quality attributes:](#6-important-quality-attributes)
- [7. Risks:](#7-risks)
- [8. Assumptions:](#8-assumptions)
- [9. Constraints:](#9-constraints)
- [10. Appendix:](#10-appendix)

## 1. Business context:

The optimisation platform provides a reusable capability for running deterministic optimisation problems using Gurobi-backed models initially, while remaining extendable to other solver products. The platform is not limited to the intent-management domain.

It can be used by experience layer users, platform services, planning tools, assurance functions, intent-management flows, and other authorised entities that need governed optimisation capability.

The business need is to allow authorised consumers to discover available optimisation capabilities, understand the required request contract, submit optimisation requests, monitor execution state, cancel active requests where needed, retry failed requests, and retrieve outcomes without exposing internal solver details or Gurobi model implementation.

The solution separates:

```text
definition of optimisation capabilities
runtime optimisation control
worker and solver execution
experience-layer presentation
```

## 2. Solution summary:

The solution provides a reusable, asynchronous optimisation platform backed by deterministic optimisation workers.

Core services:

| **Service** | **Responsibility** |
|---|---|
| **OD MS(Optimisation Definition MS)** | Owns the governed `OptimisationSpecification` catalogue and exposes caller-facing request contracts. |
| **OC MS(Optimisation Controller MS)** | Owns runtime `Optimisation` resources, lifecycle, cancellation, retrial, persistence, event integration, and result projection. |
| **OSB MS(Optimisation Screen Builder MS)** | Provides the OEX backend-for-frontend experience, shapes views/actions using user context, and calls backend optimisation APIs through NGW. |
| **Python Gurobi Worker** | Executes or cancels internal deterministic optimisation work based on Kafka worker instructions. |

Operator access to the experience layer is governed by the ACG approval process and Microsoft Entra ID SSO. OGW invokes OSB MS using mTLS and User Context JWT. OSB MS invokes NGW using mTLS and OAuth2 system-to-system. User context stops before NGW; downstream OD MS and OC MS calls use system service identity only.

OC MS validates the request structure and referenced ACTIVE OD MS request contract, persists the runtime `Optimisation` resource, returns `201 Created`, writes `OptimisationRequestedEvent` to its outbox, and drives execution asynchronously through Kafka.

Kafka carries worker instructions and outcomes, with a dedicated DLQ for unprocessable events. The Python & Gurobi Worker consumes `EXECUTE` or `CANCEL` instructions and returns terminal outcomes through `OptimisationCompletedEvent`.

NGW-exposed backend APIs use TMF-style API conventions where appropriate. `OptimisationSpecification` and `Optimisation` are optimiser-domain platform resources, not native TMF Open API resources. OGW-exposed experience APIs, private MS-to-MS APIs, and internal Kafka events do not need to be TMF-compliant.

## 3. Solution elaboration:

OD MS acts as the governed catalogue of optimisation capabilities. It exposes only what callers need to discover and submit a valid optimisation request through:

```text
specCharacteristic[]
expressionSpecification
targetEntitySchema
```

OD MS does not expose Gurobi objectives, candidate resource rules, solver configuration, model bindings, or internal formulation details.

OD MS lifecycle baseline:

```text
DRAFT -> ACTIVE -> RETIRED
```

OD MS rules:

```text
DRAFT is mutable.
DRAFT has no official public version; draft revision uses ETag.
Multiple DRAFT specifications may exist in the same familyId.
Official version is assigned by OD MS only during activation.
Only one ACTIVE specification is enforced per familyId.
ACTIVE and RETIRED specifications are immutable.
Activation retires any previous ACTIVE specification in the same familyId transactionally.
```

OC MS acts as the runtime controller. It accepts runtime requests, validates `expression.expressionValue` against the referenced ACTIVE `OptimisationSpecification.targetEntitySchema`, creates runtime optimisation resources, manages lifecycle state, publishes worker instructions, consumes worker outcomes, and projects final results.

OC MS runtime baseline:

```text
Runtime Optimisation has no business version.
POST optimisation returns 201 Created because the resource is created immediately.
Execution is asynchronous.
Result is terminal-only(not re-occuring).
optimisationSpecification.id is the immutable contract pointer for the runtime record.
OC MS must not substitute a newer ACTIVE specification from the same familyId.
```

OSB MS acts as the OEX backend-for-frontend. It shapes experience models such as `HomeView`, `CapabilityCard`, `RequestFormModel`, `CreationResultView`, `OptimisationSummaryView`, and `OptimisationDetailView`. OSB response models are experience models, not source-of-truth domain resources, OSB can be own by experience team to simplyfy their UI flows using common agregator to create payloads for UI components.

### 3.1. Use case view:

![Use case view](optimisation-use-case-view.svg)

The diagram is intentionally simplified and shows the main optimisation platform use cases. The table below provides the more detailed use-case breakdown used by the process views and implementation alignment.

| **No.** | **Use case** | **Actor** | **Summary** | **Outcome** |
|---:|---|---|---|---|
| **1** | Discover optimisation capability | User / OEX / authorised platform service | Retrieve visible ACTIVE `OptimisationSpecification` capabilities from OD MS through OSB/NGW or system API access. | Caller understands which optimisation capability and request contract to use. |
| **2** | Create optimisation specification | Optimisation domain engineer | Create a governed `OptimisationSpecification` DRAFT in OD MS after agreement with E2E teams. | Mutable DRAFT specification is created without an official public version. |
| **3** | Activate optimisation specification | Optimisation domain engineer | Promote a reviewed DRAFT to ACTIVE. | OD MS assigns official version and retires previous ACTIVE in the same `familyId`. |
| **4** | Create runtime optimisation | User / OEX / authorised platform service | Submit a runtime `Optimisation` request to OC MS using a referenced ACTIVE specification and valid expression value. | OC MS returns `201 Created` and creates an `ACKNOWLEDGED` optimisation. Execution proceeds asynchronously. |
| **5** | Monitor optimisation | User / OEX / authorised platform service | Read current lifecycle state and result when available. | Caller sees acknowledged, queued, processing, completed, infeasible, failed, cancelling, or cancelled state. |
| **6** | Cancel optimisation | User / OEX / authorised platform service | Request cancellation for eligible non-terminal(yet to be executed) optimisation using `If-Match`. | OC MS moves to `CANCELLING` and sends a best-effort(no guranteed cancellation) cancel instruction. |
| **7** | Retry failed optimisation | User / OEX / authorised platform service | Retry a `FAILED` optimisation. | New `ACKNOWLEDGED` optimisation is created with `retrialOf` attribute; original failed record stays failed. |
| **8** | Execute optimisation | Python Gurobi Worker | Consume worker instruction and execute deterministic optimisation model. | Worker emits `OptimisationCompletedEvent` with `COMPLETED`, `INFEASIBLE`, `FAILED`, or `CANCELLED`. |
| **9** | Retrieve optimisation outcome | User / OEX / authorised platform service | Retrieve completed result, infeasible explanation, failure details, or cancellation state. | Caller receives final projected runtime state/result from OC MS. |

### 3.2. Logical view:

![Logical view](optimisation-logical-view.svg)

Logical integration model:

```text
User -> OEX UI -> Microsoft Entra ID SSO -> OGW -> OSB MS -> NGW -> OD MS / OC MS -> Kafka -> Python/Gurobi Worker -> Gurobi Optimiser
```

Key logical relationships:

```text
1. User -> Microsoft Entra ID: user authenticates using SSO after ACG approval.
2. UI -> OGW: OGW is the user-context-aware gateway.
3. OGW -> OSB MS: mTLS and User Context JWT.
4. OSB MS -> NGW: mTLS and OAuth2 system-to-system.
5. NGW -> OD MS: mTLS and service/system identity only.
6. NGW -> OC MS: mTLS and service/system identity only.
7. OC MS -> OD MS: direct internal service-to-service mTLS call for specification validation; this path does not route through NGW.
8. OC MS -> Kafka: emits OptimisationRequestedEvent with EXECUTE or CANCEL.
9. Python/Gurobi Worker -> Kafka: consumes requested events and emits OptimisationCompletedEvent.
10. OC MS <- Kafka: consumes worker outcomes and projects result.
```

User context terminates before NGW. Downstream OD MS and OC MS calls do not carry or expose end-user identity, claims, roles, or scopes. OSB performs user-context filtering and view/action shaping, while OD MS and OC MS enforce backend service, lifecycle, schema, ETag, and business rules.

### 3.3. Process view:

The process flows are intentionally detailed so that ownership, validation, persistence, eventing, and asynchronous execution responsibilities are clear.

#### 3.3.1. Discover optimisation capability:

![Discover optimisation capability](optimisation-capability-discovery.svg)

```text
1. User, OEX, or authorised platform service requests available optimisation capabilities.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB shapes discovery and applies user-context filtering.
5. OSB calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes to OD MS using service identity.
7. OD MS reads visible ACTIVE OptimisationSpecification records by default.
8. OD MS returns capability and request-contract metadata.
9. OSB shapes CapabilityCard or RequestFormModel as needed.
10. Caller receives capabilities and the request contract needed to submit a runtime optimisation.
```

Normal OEX capability browsing defaults to ACTIVE capabilities only. `capabilityId` maps to OD MS `OptimisationSpecification.id` in phase one; OSB aliases/slugs are not introduced in the baseline.

#### 3.3.2. Create optimisation specification:

![Create optimisation specification](optimisation-specification-creation.svg)

```text
1. Approved optimisation domain engineer starts catalogue/specification creation journey.
2. Request reaches OGW.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB validates the user-context journey access.
5. OSB calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes create request to OD MS.
7. OD MS authenticates and authorises the service/system caller.
8. OD MS validates OptimisationSpecification request shape.
9. OD MS persists a mutable DRAFT with familyId and without official public version.
10. OD MS returns 201 Created with Location and ETag.
11. OSB shapes catalogue-management response if catalogue management is enabled.
```

Catalogue-management journeys are feature-gated and out of phase-one scope unless explicitly enabled.

#### 3.3.3. Activate optimisation specification:

![Activate optimisation specification](optimisation-specification-activation.svg)

```text
1. Approved optimisation domain engineer requests activation of a reviewed DRAFT.
2. OSB exposes this only when catalogue management is enabled and user context allows it.
3. OSB calls NGW using mTLS and OAuth2 system-to-system.
4. NGW routes activation PATCH/PUT to OD MS.
5. OD MS validates ETag, DRAFT lifecycle, and full specification contract.
6. OD MS assigns official version during activation.
7. OD MS moves the DRAFT to ACTIVE.
8. OD MS transactionally retires any previous ACTIVE specification in the same familyId.
9. ACTIVE and RETIRED specifications become immutable.
```

#### 3.3.4. Create and execute optimisation:

![Create and execute optimisation](optimisation-runtime-execution.svg)

```text
1. User initiates optimisation journey through OEX or another authorised caller submits a runtime request.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB validates user context and shapes the request/action model.
5. OSB calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes POST /optimisation to OC MS.
7. OC MS validates referenced OptimisationSpecification.id exists and is ACTIVE.
8. OC MS validates expression.expressionValue against the referenced ACTIVE targetEntitySchema.
9. OC MS persists runtime Optimisation with lifecycleStatus = ACKNOWLEDGED.
10. OC MS stores optimisationSpecification.id/href as immutable contract pointer.
11. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE to outbox in same transaction.
12. OC MS returns 201 Created with Location, ETag, and runtime resource body after resource persistence and outbox write, before worker execution completes.
13. OC MS Outbox Relay publishes OptimisationRequestedEvent to Kafka.
14. OC MS advances ACKNOWLEDGED -> QUEUED after successful Kafka publish.
15. Python/Gurobi Worker consumes OptimisationRequestedEvent.
16. Worker resolves deterministic model binding and invokes Gurobi Optimiser.
17. Worker publishes OptimisationCompletedEvent with COMPLETED, INFEASIBLE, FAILED, or CANCELLED.
18. OC MS Inbox Consumer applies idempotency and stale/late event checks.
19. OC MS updates lifecycle/result projection.
20. Caller polls through User -> OEX -> OGW -> OSB MS -> NGW -> OC MS to retrieve status/result.
```

#### 3.3.5. Monitor optimisation:

![Monitor optimisation](optimisation-status-retrieval.svg)

```text
1. User, OEX, or authorised platform service requests current status/result.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB validates access to the requested optimisation view.
5. OSB calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes GET /optimisation/{id} to OC MS.
7. OC MS returns lifecycleStatus, status reason, result when terminal, failure details, and links/actions where applicable.
8. OSB shapes OptimisationDetailView or OptimisationSummaryView.
9. Caller receives current state.
```

Phase-one OEX/OSB status refresh is REST polling against OC MS through NGW. OSB must not infer terminal status locally; terminal state must come from OC MS.

#### 3.3.6. Cancel optimisation:

![Cancel optimisation](optimisation-cancellation.svg)

```text
1. Consumer calls OSB cancellation endpoint with current ETag/If-Match context.
2. OSB uses backend _links as the authoritative action affordance signal.
3. actionVisible = backend_link_present AND user_context_allows.
4. OSB forwards If-Match from OC MS ETag and must not generate its own backend ETag.
5. NGW routes POST /optimisation/{id}/cancellation to OC MS.
6. OC MS validates ETag and eligible non-terminal lifecycle.
7. OC MS updates lifecycleStatus to CANCELLING.
8. OC MS writes OptimisationRequestedEvent with instruction = CANCEL to outbox.
9. OC MS Outbox Relay publishes event to Kafka.
10. Worker stops, cancels, or ignores work where safely possible.
11. OC MS projects CANCELLED only after worker confirmation or equivalent terminal confirmation that cancellation was honoured(safely).
```

Cancellation is best-effort. Cancellation has no required request body; optional reason/comment metadata does not change cancellation semantics. Cancellation requested for terminal `COMPLETED`, `FAILED`, `INFEASIBLE`, or `CANCELLED` state returns `409 Conflict`.

Worker cancellation handling is implementation-specific. The `CANCEL` instruction is best-effort; a worker may complete a solve cycle before honouring cancellation where immediate interruption is not safe or supported.

#### 3.3.7. Retry failed optimisation:

![Retry failed optimisation](optimisation-retrial.svg)

```text
1. Consumer calls OSB retrial endpoint with current ETag/If-Match context.
2. OSB exposes retrial only when backend _links includes retrial and user context allows it.
3. OSB forwards If-Match from OC MS ETag.
4. NGW routes POST /optimisation/{id}/retrial to OC MS.
5. OC MS validates original Optimisation lifecycleStatus = FAILED.
6. OC MS creates a new Optimisation resource.
7. New Optimisation links to original through retrialOf.
8. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED.
9. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
10. Worker processes the new request asynchronously.
```

Retrial is available only from `FAILED` in the baseline. Retrial is not available from `INFEASIBLE` by default because `INFEASIBLE` is a valid optimisation/model outcome, not a technical failure. Retrial has no required request body and does not allow overrides; it resubmits the original accepted expression and referenced `OptimisationSpecification.id` unchanged.

#### 3.3.8. Gurobi execute optimisation:

![Gurobi execute optimisation](optimisation-worker-execution.svg)

```text
1. Python/Gurobi Worker consumes OptimisationRequestedEvent with instruction = EXECUTE.
2. Worker validates event idempotency and execution eligibility.
3. Worker resolves runtime context and internal deterministic model binding.
4. Worker invokes Gurobi Optimiser.
5. Gurobi Optimiser returns solver output, infeasibility information, failure information, or cancellation confirmation.
6. Worker maps outcome to COMPLETED, INFEASIBLE, FAILED, or CANCELLED.
7. Worker publishes OptimisationCompletedEvent.
8. OC MS Inbox Consumer applies idempotency and stale/late event checks.
9. OC MS updates runtime lifecycle/result projection.
10. User observes outcome through OC MS REST status/detail exposed through OSB/NGW.
```

## 4. Capability matrix:

| **Component** | **Responsibility** |
|---|---|
| **Microsoft Entra ID** | Provides SSO authentication for users before they access OEX/experience layer. |
| **ACG approval process** | Governs operator access to the OEX optimisation experience. |
| **OGW** | User-context-aware gateway for OEX APIs. Invokes OSB MS using mTLS and User Context JWT. |
| **OEX UI / experience layer** | Provides user/operator-facing experience for discovery, request submission, monitoring, cancellation, retrial, and result viewing. |
| **OSB MS** | Builds OEX view models, applies user-context filtering, uses backend `_links` plus user context for actions, forwards ETags, and calls backend APIs through NGW. |
| **NGW** | Backend API entry point for OD MS and OC MS using service/system identity and mTLS. |
| **OD MS** | Owns `OptimisationSpecification` catalogue, lifecycle/version governance, `specCharacteristic[]`, `expressionSpecification`, and `targetEntitySchema`. |
| **OD MS Database** | Stores specification records, familyId, lifecycle, official version for ACTIVE/RETIRED, ETags, and immutable retained history. |
| **OC MS** | Owns runtime `Optimisation` resources, lifecycle, accepted expression values, immutable specification pointer, outbox/inbox, cancellation, retrial, and result projection. |
| **OC MS Database** | Stores runtime records, lifecycle state, statusChangeDate, sourceContext, expression, result when terminal, relationships, outbox, and inbox records. |
| **OC MS Outbox Relay** | Publishes `OptimisationRequestedEvent` to Kafka after DB commit; successful publish drives ACKNOWLEDGED -> QUEUED. |
| **Kafka topic** | Internal event stream for worker instructions and outcomes. |
| **Kafka DLQ** | Holds events that cannot be safely processed after retry handling. |
| **Python/Gurobi Worker** | Consumes requested events, executes/cancels work, and emits completed events. |
| **Internal deterministic optimisation models** | Own solver-specific objective formulation, constraints, candidate-resource rules, model binding, and solver configuration. |
| **Gurobi Optimiser** | Executes mathematical optimisation prepared by worker model layer. |
| **Analytics platform/data sources** | Provides authorised datasets required by the worker/model layer. |
| **OC MS Inbox Consumer** | Consumes worker outcomes, applies idempotency/stale/late checks, and projects lifecycle/result. |
| **Operational support/monitoring** | Monitors service health, Kafka lag, outbox/inbox processing, worker failures, solver failures, DLQ, and lifecycle/result trends. |

## 5. Solution security:

### 5.1. User authentication and access governance:

Users access OEX through ACG approval and Microsoft Entra ID SSO.

```text
User -> ACG approval process -> Microsoft Entra ID SSO -> OGW -> OEX APIs/UI
```

### 5.2. Experience layer internal access path:

OGW integrates with OSB MS using:

```text
mTLS
User Context JWT
```

### 5.3. Experience layer to optimisation backend access:

OSB MS integrates with NGW using:

```text
mTLS
OAuth2 system-to-system
```

User context stops before/at NGW. OSB performs user-context filtering and action shaping, but backend OD MS and OC MS decisions win. OD MS and OC MS authorise service/system identity and enforce lifecycle, schema, ETag, and business rules.

### 5.4. NGW to OD MS / OC MS security:

NGW integrates with OD MS and OC MS using:

```text
mTLS
service/system identity only
```

NGW-to-downstream OD MS / OC MS calls do not carry or expose end-user identity, claims, roles, or scopes.

### 5.5. OC MS to OD MS service-to-service security:

OC MS calls OD MS directly using service-to-service mTLS for specification validation. This is an internal service path and does not route through NGW.

OC MS validates:

```text
OptimisationSpecification exists
OptimisationSpecification lifecycleStatus = ACTIVE
expression.expressionValue matches targetEntitySchema
```

OC MS may cache immutable ACTIVE specification contracts by id and ETag, but must not infer current active contract by stale `familyId` lookup.

### 5.6. Kafka security:

Recommended controls:

```text
TLS for broker connectivity
service identity for producers and consumers
topic-level ACLs
separate consumer groups
DLQ access restricted to operational support
```

DLQ behaviour baseline:

```text
DLQ events require operational intervention.
No automatic replay is performed by default.
Replay/remediation must follow controlled operational procedures.
DLQ access is restricted to operational support.
DLQ entries should retain failure metadata needed for diagnosis and safe replay decisions.
```

### 5.7. API concurrency control:

ETags are used for unsafe runtime actions:

```http
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
```

Both require:

```http
If-Match
```

Failure rules:

```text
Missing If-Match -> 428 Precondition Required
Stale/wrong If-Match -> 412 Precondition Failed
```

OSB forwards OC MS ETags and must not generate backend unsafe-operation ETags.

### 5.8. Event security and integrity:

Internal Kafka events use CloudEvents-style headers and must include:

```text
optimisationId
correlationId
traceId
eventId / ce-id
```

`OptimisationCompletedEvent` processing must be idempotent. OC MS projection must safely handle duplicate, stale, and late worker outcome events.

### 5.9. Sensitive information boundary:

Public APIs, OSB views, and Kafka events must not expose:

```text
Gurobi model formulation
solver configuration
objective internals
candidate-resource rules
internal model bindings
resource-selection logic
credentials
infrastructure internals
raw stack traces
```

### 5.10. Infrastructure security controls:

Every service-to-infrastructure integration must explicitly capture authentication, authorisation, encrypted connectivity, secret/certificate management, environment separation, audit/monitoring, and ownership.

## 6. Important quality attributes:

### 6.1. Availability:
SLA of avalabilty yet to be determined.
OD MS and OC MS should be deployed as independently scalable and highly available services. Kafka availability is critical for asynchronous worker instruction/outcome exchange. Outbox/inbox patterns reduce data-loss risk during transient service or Kafka failures.
DB and kafka cluster will have enough redundency have high availablity requirements, and k8s will provide high availabilty by having multiple pods and having capabilty to orchestrate pods to meet defined avaialbilty.

### 6.2. Scalability:
Production enviorement expected to be able to dynamicaly scale based on demand.
OD MS scales primarily for capability discovery and specification retrieval. OC MS scales for runtime API traffic, outbox relay throughput, and inbox outcome processing. Python/Gurobi workers scale horizontally based on queue depth and solver runtime characteristics. OSB scales for OEX-API view traffic and can cache read-only OD-derived capability/form data only where backend cache headers allow.

K8s will provide ability scale based on demand.

### 6.3. Performance:

All sync api calls supposed to be provide below 30ms response time.

`POST /optimisation` returns `201 Created` after syntactic and OD-MS-contract validation, runtime resource persistence, and outbox write. Solver execution remains asynchronous and decoupled from REST request latency. 

`GET /optimisation/{id}` provides polling of lifecycle and result state. Runtime `result` is absent until terminal state. OSB/OEX status refresh is REST polling against OC MS through NGW in phase one. Polling cadence is owned by OSB MS in coordination with OEX UI/platform UX.

## 7. Risks:

| **Risk** | **Impact** | **Mitigation** |
|---|---|---|
| **Long-running Gurobi executions** | Delayed optimisation outcomes and worker capacity pressure. | Asynchronous execution, worker scaling, queue monitoring, timeout controls, and alerting. |
| **Best-effort cancellation** | Running optimisation may not stop immediately or may produce late outcome. | CANCELLING state, worker cancellation handling, and late outcome idempotency rules. |
| **Kafka consumer lag** | Execution/result projection delay. | Monitor lag, scale consumers/workers, alert on thresholds. |
| **Invalid or stale context datasets** | Poor, infeasible, or failed optimisation outcomes. | Request contract validation, dataset versioning, worker diagnostics, and monitoring. |
| **DLQ growth** | Poison messages, schema drift, or repeated processing failure. | DLQ monitoring, failure metadata retention, replay/remediation procedures. |
| **Misconfigured internal model binding** | Valid request contract but worker execution fails. | Deployment validation, contract tests, and pre-production model checks. |
| **Overexposure of solver details** | Sensitive optimisation logic leaks externally. | Keep solver/model details internal and return only safe generic outputs. |
| **Incorrect specification activation** | Wrong ACTIVE specification affects future requests. | OD lifecycle governance, ETag/If-Match, review/approval, and one ACTIVE per familyId. |
| **Complex access path through gateways** | User context or backend identity misconfiguration. | Contract tests across OGW, OSB, NGW, OD, and OC. |
| **Cached UI/action state misuse** | User sees stale or invalid actions. | Backend `_links` plus user-context rule; backend decision wins. |

## 8. Assumptions:

- Operators access OEX only after ACG approval.
- User/operator authentication uses Microsoft Entra ID SSO.
- OGW is the user-context-aware gateway for OEX APIs.
- OGW integrates with OSB MS using mTLS and User Context JWT.
- OSB MS integrates with NGW using mTLS and OAuth2 system-to-system.
- User context stops before/at NGW; downstream OD MS / OC MS calls use system/service identity only.
- NGW exposes OD MS and OC MS APIs to authorised backend consumers.
- OC MS calls OD MS using mTLS for specification validation.
- Kafka is available as the event backbone.
- Python Gurobi Worker has authorised access to required analytics data sources.
- Runtime `Optimisation` is asynchronous by design.
- `sourceContext` is optional and may be omitted for generic optimisation requests.
- Runtime `Optimisation` does not expose a business `version` field.
- OD MS is synchronous REST only for the initial baseline; specification events/hub support is deferred.
- OSB catalogue-management journeys are feature-gated and out of phase-one scope unless explicitly enabled.

## 9. Constraints:

- NGW-exposed backend APIs use TMF-style API conventions where appropriate.
- `OptimisationSpecification` and `Optimisation` are optimiser-domain platform resources, not native TMF Open API resources.
- OGW-exposed experience APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF REST compliant.
- `x-platform-extension: true` and `x-tmf-native: false` are governance documentation response headers on external NGW-facing optimiser resources.
- Do not expose Gurobi model formulation, solver configuration, objective internals, candidate-resource rules, or model binding through public APIs or OSB views.
- OD MS exposes only the caller-facing `OptimisationSpecification` request contract.
- OC MS performs syntactic and OD-MS-contract validation only.
- Runtime `Optimisation` does not expose a `version` field.
- Runtime `Optimisation` does not support client-side `PUT`, `PATCH`, or `DELETE`.
- Cancellation is represented through `lifecycleStatus = CANCELLING` and an `OptimisationRequestedEvent` with `instruction = CANCEL`.
- Only one `ACTIVE` `OptimisationSpecification` is allowed per `familyId`.
- ETag / If-Match is required for unsafe runtime operations such as cancellation and retrial.
- Internal Kafka events do not use TMF REST `@type`, `@baseType`, or `@schemaLocation`.

## 10. Appendix:

### 10.1. OD MS endpoint summary:

```http
GET /optimisationManagement/v1/optimisationSpecification
POST /optimisationManagement/v1/optimisationSpecification
GET /optimisationManagement/v1/optimisationSpecification/{id}
PATCH /optimisationManagement/v1/optimisationSpecification/{id}
PUT /optimisationManagement/v1/optimisationSpecification/{id}
DELETE /optimisationManagement/v1/optimisationSpecification/{id}
```

OD `PATCH` requires `Content-Type: application/merge-patch+json`. OD `PUT` requires `Content-Type: application/json` and is allowed only for mutable DRAFT replacement/finalisation.

### 10.2. OC MS endpoint summary:

```http
GET /optimisationManagement/v1/optimisation
POST /optimisationManagement/v1/optimisation
GET /optimisationManagement/v1/optimisation/{id}
POST /optimisationManagement/v1/optimisation/{id}/cancellation
POST /optimisationManagement/v1/optimisation/{id}/retrial
```

Unsupported:

```http
PUT /optimisationManagement/v1/optimisation/{id}
PATCH /optimisationManagement/v1/optimisation/{id}
DELETE /optimisationManagement/v1/optimisation/{id}
```

### 10.3. OSB MS endpoint summary:

```http
GET /optimisationExperience/v1/home
GET /optimisationExperience/v1/capabilities
GET /optimisationExperience/v1/capabilities/{capabilityId}/request-form
POST /optimisationExperience/v1/optimisations
GET /optimisationExperience/v1/optimisations
GET /optimisationExperience/v1/optimisations/{id}
POST /optimisationExperience/v1/optimisations/{id}/cancellation
POST /optimisationExperience/v1/optimisations/{id}/retrial
```

OSB uses pluralised experience endpoint names intentionally; backend OD and OC resource endpoint names remain unchanged behind NGW.

### 10.4. Runtime lifecycle states:

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

| **Status** | **Meaning** |
|---|---|
| `ACKNOWLEDGED` | OC MS accepted and persisted the request and wrote the outbox event. |
| `QUEUED` | Outbox Relay successfully published the requested event and worker processing is pending. |
| `PROCESSING` | Worker is executing or preparing the optimisation. |
| `COMPLETED` | Worker returned successful completion and result may be available. |
| `INFEASIBLE` | Worker/model determined no feasible solution exists. Not retriable by default. |
| `FAILED` | Technical/runtime failure occurred. Retriable by creating a new linked Optimisation. |
| `CANCELLING` | Cancellation was requested and is being handled. |
| `CANCELLED` | Optimisation was cancelled after worker confirmation, or equivalent terminal confirmation, that cancellation was honoured(safely). |

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

### 10.5. Kafka topics:

```text
t7.optimisation.events
t7.optimisation.events.dlq
```

### 10.6. Event types:

```text
OptimisationRequestedEvent
OptimisationCompletedEvent
```

A separate `OptimisationFailedEvent` is not used by default. Failed, infeasible, and cancelled outcomes are represented inside `OptimisationCompletedEvent.status`.

### 10.7. Worker instructions:

```text
EXECUTE
CANCEL
```

### 10.8. Worker terminal status values:

```text
COMPLETED
INFEASIBLE
FAILED
CANCELLED
```

### 10.9. Outcome mapping:

Worker emits `OptimisationCompletedEvent.status` using one of:

```text
COMPLETED
INFEASIBLE
FAILED
CANCELLED
```

OC MS maps worker status to runtime lifecycle status as follows:

```text
COMPLETED -> lifecycleStatus COMPLETED
INFEASIBLE -> lifecycleStatus INFEASIBLE
FAILED -> lifecycleStatus FAILED
CANCELLED -> lifecycleStatus CANCELLED
```

Do not introduce an alternate success status unless the worker contract is explicitly changed to emit one.

### 10.10. Canonical runtime expression shape:

Runtime optimisation requests carry actual runtime values under `expression.expressionValue.context`:

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

OD MS defines the allowed structure using `OptimisationSpecification.targetEntitySchema`. OC MS carries the accepted runtime values and validates them against the referenced ACTIVE schema.

### 10.11. Result presence rules:

```text
result MUST be absent while lifecycleStatus is ACKNOWLEDGED, QUEUED, PROCESSING, or CANCELLING.
result MAY be present when lifecycleStatus is COMPLETED, INFEASIBLE, FAILED, or CANCELLED.
FAILED result details may include safe error codes/messages only.
```

### 10.12. Validation and outcome responsibility:

```text
OC MS validates:
required fields
enum/value-type rules
request contract shape
cardinality rules defined by targetEntitySchema

OC MS does not evaluate:
solver feasibility
candidate ranking
metric-vs-constraint fit
objective trade-offs

Python/Gurobi Worker returns terminal status:
COMPLETED
INFEASIBLE
FAILED
CANCELLED
```

Use `422 OPTIMISATION_CONTRACT_VIOLATION` for contract/cardinality failures. Use `INFEASIBLE` only when the request is valid and the worker/model determines no feasible solution exists.

### 10.13. Key artifacts:

PUML and DrawIO files are editable source artifacts. Rendered SVG/PNG exports are the preferred review and consumption artifacts where available.

```text
od-ms/od-ms-specification.md
oc-ms/oc-ms-specification.md
osb-ms/osb-ms-specification.md
e2e/optimisation-e2e-solution-brief.md
e2e/optimisation-logical-view.drawio
e2e/optimisation-use-case-view.puml
e2e/optimisation-capability-discovery.puml
e2e/optimisation-specification-creation.puml
e2e/optimisation-specification-activation.puml
e2e/optimisation-runtime-execution.puml
e2e/optimisation-status-retrieval.puml
e2e/optimisation-cancellation.puml
e2e/optimisation-retrial.puml
e2e/optimisation-worker-execution.puml
```
