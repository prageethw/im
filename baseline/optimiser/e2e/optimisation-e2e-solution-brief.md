# End-to-End Solution Brief — Optimisation Platform:

## Document status:

| **Field** | **Value** |
|---|---|
| **Status** | Baseline candidate |
| **Scope** | Optimisation platform end-to-end architecture |
| **Source path** | `baseline/optimiser/e2e/optimisation-e2e-solution-brief.md` |
| **Source of truth** | GitHub `main` |
| **Last enhanced** | 2026-05-21 |
| **Enhancement** | Added numbered headings, table of contents, status section, and colon-ended headings. |

## Table of contents:

- [1. Business context:](#1-business-context)
- [2. Solution summary:](#2-solution-summary)
- [3. Solution elaboration:](#3-solution-elaboration)
  - [3.1. Use case view:](#31-use-case-view)
  - [3.2. Logical view:](#32-logical-view)
  - [3.3. Process view:](#33-process-view)
    - [3.3.1. Discover optimisation capability:](#331-discover-optimisation-capability)
    - [3.3.2. Create optimisation specification:](#332-create-optimisation-specification)
    - [3.3.3. Create and execute optimisation:](#333-create-and-execute-optimisation)
    - [3.3.4. Monitor optimisation:](#334-monitor-optimisation)
    - [3.3.5. Cancel optimisation:](#335-cancel-optimisation)
    - [3.3.6. Retry failed optimisation:](#336-retry-failed-optimisation)
    - [3.3.7. Gurobi execute optimisation:](#337-gurobi-execute-optimisation)
- [4. Capability matrix:](#4-capability-matrix)
- [5. Solution security:](#5-solution-security)
  - [5.1. User authentication and access governance:](#51-user-authentication-and-access-governance)
  - [5.2. Experience layer internal access path:](#52-experience-layer-internal-access-path)
  - [5.3. Experience layer to optimisation backend access:](#53-experience-layer-to-optimisation-backend-access)
  - [5.4. NGW to OD MS / OC MS security:](#54-ngw-to-od-ms--oc-ms-security)
  - [5.5. OC MS to OD MS service-to-service security:](#55-oc-ms-to-od-ms-service-to-service-security)
  - [5.6. Kafka security:](#56-kafka-security)
  - [5.7. API concurrency control:](#57-api-concurrency-control)
  - [5.8. Event security and integrity:](#58-event-security-and-integrity)
  - [5.9. Sensitive information boundary:](#59-sensitive-information-boundary)
  - [5.10. Infrastructure security controls:](#510-infrastructure-security-controls)
- [6. Important quality attributes:](#6-important-quality-attributes)
  - [6.1. Availability:](#61-availability)
  - [6.2. Scalability:](#62-scalability)
  - [6.3. Performance:](#63-performance)
- [7. Risks:](#7-risks)
- [8. Assumptions:](#8-assumptions)
- [9. Constraints:](#9-constraints)
- [10. Appendix:](#10-appendix)
  - [10.1. OD MS endpoint summary:](#101-od-ms-endpoint-summary)
  - [10.2. OC MS endpoint summary:](#102-oc-ms-endpoint-summary)
  - [10.3. Runtime lifecycle states:](#103-runtime-lifecycle-states)
  - [10.4. Kafka topics:](#104-kafka-topics)
  - [10.5. Event types:](#105-event-types)
  - [10.6. Worker instructions:](#106-worker-instructions)
  - [10.7. Worker terminal status values:](#107-worker-terminal-status-values)
  - [10.8. Outcome mapping:](#108-outcome-mapping)
  - [10.9. Canonical runtime expression shape:](#109-canonical-runtime-expression-shape)
  - [10.10. Validation and outcome responsibility:](#1010-validation-and-outcome-responsibility)
  - [10.11. Key artifacts:](#1011-key-artifacts)

## 1. Business context:

The optimisation platform provides a reusable capability for running deterministic optimisation problems using Gurobi-backed models initially, but is extendable to run with different solver products. The platform is not limited to the intent-management domain.

It is designed as a generic optimisation capability that can be used by experience layer, platform services, planning tools, assurance functions, intent-management flows, and other authorised entities that need to run optimisation.

The business need is to allow authorised consumers to discover available optimisation capabilities, understand the required request contract, submit optimisation requests, monitor execution state, cancel active requests where needed, retry failed requests, and retrieve outcomes without exposing internal solver details or Gurobi model implementation.

The solution separates the definition of optimisation capabilities from the execution and lifecycle control of optimisation runs.

## 2. Solution summary:

The solution provides a reusable, asynchronous optimisation platform backed by deterministic Gurobi models.

The core optimisation services are:

| **Service** | **Responsibility** |
|---|---|
| **OD MS / Optimisation Definition MS** | Owns the governed `OptimisationSpecification` catalogue and exposes the caller-facing request contract. |
| **OC MS / Optimisation Controller MS** | Owns runtime `Optimisation` resources, lifecycle, cancellation, retrial, persistence, event integration, and result projection. |
| **OSB MS / Optimisation Screen Builder MS** | Provides the backend-for-frontend experience for optimisation journeys and calls backend optimisation APIs through NGW. |
| **Python/Gurobi Worker** | Executes or cancels internal deterministic optimisation work based on Kafka worker instructions. |

Consumers may include experience layer users, platform services, planning tools, assurance functions, intent-management flows, or other authorised entities that need to run optimisation. The experience layer provides the user optimisation experience.

OGW is the user-context-aware gateway for experience layer APIs and invokes OSB MS using mTLS and User Context JWT. OSB MS is the context-aware experience layer facade, or backend-for-frontend, for optimisation journeys.

OSB MS shapes experience layer screens and actions using the User Context JWT, proxies runtime optimisation journeys to OC MS through NGW, and supports governed OD MS catalogue specification journeys through NGW.

Operator access to the experience layer is governed by the ACG approval process and Microsoft Entra ID SSO. OSB MS reaches backend OD MS and OC MS APIs through NGW using mTLS and OAuth2 system-to-system.

OC MS validates the request structure and the referenced ACTIVE OD MS request contract, returns `202 Accepted`, and drives execution asynchronously through Kafka.

Kafka carries worker instructions and outcomes, with a dedicated DLQ for unprocessable events. The Python/Gurobi Worker consumes `EXECUTE` or `CANCEL` instructions, runs or cancels optimisation work, and returns `COMPLETED`, `INFEASIBLE`, or `FAILED` terminal outcomes through Kafka `OptimisationCompletedEvent`.

NGW-exposed backend APIs use TMF-style API conventions where appropriate. `OptimisationSpecification` and `Optimisation` are optimiser-domain platform resources modelled using TMF-style resource patterns; they are not native TMF921 resource names, though ontology can be adopted where useful.

OGW-exposed experience layer APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF compliant; they remain generic where useful.

## 3. Solution elaboration:

The solution is structured around a clean separation of responsibility and bounded context.

OD MS acts as the governed catalogue of optimisation capabilities. It exposes only what callers need to know to submit a valid optimisation request. OD MS exposes the caller-facing contract through `specCharacteristic[]`, `expressionSpecification`, and authoritative `targetEntitySchema`.

OD MS does not expose Gurobi objectives, candidate resource rules, solver configuration, model bindings, or internal formulation details. OD MS remains synchronous REST only for the initial baseline; no `/hub` subscription endpoint or outbound `OptimisationSpecification` events are exposed initially.

OC MS acts as the runtime controller. It accepts requests, validates the runtime `expression.expressionValue` shape against the referenced ACTIVE `OptimisationSpecification.targetEntitySchema`, creates runtime optimisation resources, manages lifecycle state, publishes worker instructions, consumes worker outcomes, and projects final results.

The Python/Gurobi Worker is responsible for executing the internal deterministic optimisation model. It consumes events from Kafka, executes or cancels work based on the instruction, and publishes `OptimisationCompletedEvent` back to Kafka with terminal status `COMPLETED`, `INFEASIBLE`, or `FAILED`.

A separate `OptimisationFailedEvent` is not used by default. External NGW API design is TMF ontology-aligned where useful, with controlled platform extensions clearly identified. OD MS owns the design-time optimisation contract. OC MS owns runtime optimisation resources. Internal APIs and Kafka events are intentionally not TMF REST resources.

Appendix sections in this brief define the canonical runtime expression shape and lifecycle baseline used across the optimiser architecture.

### 3.1. Use case view:

![Use case view](optimisation-use-case-view.svg)

| **No.** | **Use case** | **Actor** | **Summary** | **Outcome** |
|---:|---|---|---|---|
| **1** | Discover optimisation capability | User / experience layer / platform service | Retrieve available `OptimisationSpecification` records from OD MS and understand the required runtime expression contract. | Caller knows which optimisation capability to use and the required request contract. |
| **2** | Create optimisation specification | Optimisation domain engineer | Create a governed `OptimisationSpecification` in OD MS after agreement with broader E2E teams, including `specCharacteristic[]`, `expressionSpecification`, `targetEntitySchema`, and lifecycle/governance metadata. | A new `OptimisationSpecification` is created in `DRAFT` state and is not usable for runtime optimisation until reviewed and activated. |
| **3** | Activate optimisation specification | Optimisation domain engineer | Promote a reviewed `DRAFT` specification to `ACTIVE`, retiring the previous active version in the same specification family where applicable. | New runtime optimisation requests can reference the activated specification. |
| **4** | Create runtime optimisation | User / experience layer / platform service | Submit a runtime `Optimisation` request to OC MS using an ACTIVE specification and valid runtime `expression.expressionValue.context`. | OC MS returns `202 Accepted` and creates an `ACKNOWLEDGED` optimisation. |
| **5** | Monitor optimisation | User / experience layer / platform service | Read current lifecycle state and result when available. | Caller can see whether the optimisation is acknowledged, queued, processing, completed, infeasible, failed, cancelling, or cancelled. |
| **6** | Cancel optimisation | User / experience layer / platform service | Request cancellation for an eligible active optimisation. | OC MS moves the resource to `CANCELLING` and instructs the worker to cancel where safely possible. |
| **7** | Retry failed optimisation | User / experience layer / platform service | Retry a `FAILED` optimisation by creating a new linked optimisation. | A new `ACKNOWLEDGED` optimisation is created with `retrialOf` pointing to the failed one. |
| **8** | Execute optimisation | Python/Gurobi Worker | Consume worker instruction and execute the deterministic optimisation model. | Worker emits `OptimisationCompletedEvent` with terminal status `COMPLETED`, `INFEASIBLE`, or `FAILED`. |
| **9** | Retrieve optimisation outcome | User / experience layer / platform service | Retrieve completed result, infeasible explanation, or failure details. | Caller receives the final projected runtime optimisation state and result details. |

### 3.2. Logical view:

![Logical view](optimisation-logical-view.svg)

The logical integration model is:

```text
User -> experience layer UI -> Microsoft Entra ID SSO -> OGW -> OSB MS (experience layer API) -> NGW -> OD MS / OC MS -> Kafka -> Python/Gurobi Worker -> Gurobi Optimiser
```

Key logical relationships are:

```text
1. User -> Microsoft Entra ID: User authenticates using SSO after ACG approval.
2. UI -> OGW: OGW acts as the user-context-aware gateway for experience layer APIs.
3. OGW -> OSB MS: Uses mTLS and User Context JWT.
4. OSB MS -> NGW: Uses mTLS and OAuth2 system-to-system.
5. NGW -> OD MS: Uses mTLS to expose OptimisationSpecification APIs.
6. NGW -> OC MS: Uses mTLS to expose runtime Optimisation APIs.
7. OC MS -> OD MS: Uses mTLS for internal service-to-service validation.
8. OC MS -> Kafka: Emits OptimisationRequestedEvent with instruction EXECUTE or CANCEL.
9. Python/Gurobi Worker -> Kafka: Consumes worker instructions and emits OptimisationCompletedEvent with status COMPLETED, INFEASIBLE, or FAILED.
10. OC MS <- Kafka: Consumes worker outcomes and projects lifecycle/result.
```

Logical diagram artifact:

```text
optimisation-logical-view.drawio
```

### 3.3. Process view:

Each use case has a matching process flow. The process flows are intentionally more detailed than the logical view so that ownership, validation, persistence, eventing, and asynchronous execution responsibilities are clear.

#### 3.3.1. Discover optimisation capability:

![Discover optimisation capability](optimisation-capability-discovery.svg)

```text
1. User, experience layer, or another authorised platform service requests available optimisation capabilities.
2. Request reaches OGW.
3. OGW invokes OSB MS using mTLS and User Context JWT where user context is applicable.
4. OSB MS shapes the discovery request and applies user-context-aware filtering where applicable.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the discovery request to OD MS.
7. OD MS reads ACTIVE OptimisationSpecification records from OD MS DB.
8. OD MS returns caller-facing capability and request-contract metadata, including specCharacteristic[], expressionSpecification, and targetEntitySchema.
9. NGW returns the response to OSB MS.
10. OSB MS shapes the response for the experience layer/API consumer.
11. Caller receives available optimisation capabilities and understands which request contract to use.
```

#### 3.3.2. Create optimisation specification:

![Create optimisation specification](optimisation-specification-creation.svg)

```text
1. Approved optimisation domain engineer starts a catalogue/specification creation journey after agreement with broader E2E teams.
2. Request reaches OGW.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB MS validates the user context and confirms the user is allowed to access catalogue-management capabilities.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the create request to OD MS.
7. OD MS authenticates and authorises the catalogue operation.
8. OD MS validates the OptimisationSpecification request shape, including lifecycle metadata, specCharacteristic[], expressionSpecification, and targetEntitySchema.
9. OD MS persists the new OptimisationSpecification in OD MS DB with lifecycleStatus = DRAFT.
10. OD MS returns the created DRAFT OptimisationSpecification with Location and ETag where applicable.
11. NGW returns the response to OSB MS.
12. OSB MS shapes the catalogue-management response for the experience layer experience.
13. Optimisation domain engineer receives the DRAFT OptimisationSpecification result.
14. The DRAFT specification is not usable for runtime optimisation until reviewed and activated under OD MS governance.
```

#### 3.3.3. Create and execute optimisation:

![Create and execute optimisation](optimisation-runtime-execution.svg)

```text
1. User initiates the optimisation journey via UI or another authorised consumer submits a runtime request.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB MS validates the User Context JWT and shapes the request/action model.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the request to OC MS.
7. OC MS calls OD MS over mTLS to validate the referenced ACTIVE OptimisationSpecification.
8. OC MS validates expression.expressionValue against the ACTIVE OptimisationSpecification.targetEntitySchema, including context.targets[], context.constraints[], and context.preferences[].
9. OC MS persists the accepted runtime Optimisation with lifecycleStatus = ACKNOWLEDGED in OC MS DB.
10. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE to OC MS Outbox in the same transaction.
11. OC MS Outbox Relay publishes the event to Kafka.
12. Python/Gurobi Worker consumes OptimisationRequestedEvent from Kafka.
13. Python/Gurobi Worker resolves internal deterministic model binding.
14. Python/Gurobi Worker invokes Gurobi Optimiser.
15. Worker publishes OptimisationCompletedEvent with status COMPLETED, INFEASIBLE, or FAILED back to Kafka.
16. OC MS Inbox Consumer consumes the worker outcome event.
17. OC MS Inbox Consumer updates OC MS DB with lifecycle and result projection.
18. Caller polls GET /optimisation/{id} through OGW -> OSB MS -> NGW -> OC MS to retrieve current status/result.
```

#### 3.3.4. Monitor optimisation:

![Monitor optimisation](optimisation-status-retrieval.svg)

```text
1. User, experience layer, or another authorised platform service requests current optimisation status or result.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT where user context is applicable.
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

#### 3.3.5. Cancel optimisation:

![Cancel optimisation](optimisation-cancellation.svg)

```text
1. Consumer calls POST /optimisation/{id}/cancellation with If-Match.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB MS exposes or forwards the cancellation action only when the user context and runtime state allow it.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the cancellation request to OC MS.
7. OC MS validates ETag.
8. OC MS checks lifecycleStatus is ACKNOWLEDGED, QUEUED, or PROCESSING.
9. OC MS updates lifecycleStatus to CANCELLING in the OC MS DB.
10. OC MS writes OptimisationRequestedEvent with instruction = CANCEL to OC MS Outbox.
11. OC MS Outbox Relay publishes the event to Kafka.
12. Python/Gurobi Worker consumes the CANCEL instruction.
13. Worker stops, cancels, or ignores work where safely possible.
14. OC MS eventually projects CANCELLED when cancellation is confirmed or safely resolved.
```

#### 3.3.6. Retry failed optimisation:

![Retry failed optimisation](optimisation-retrial.svg)

```text
1. Consumer calls POST /optimisation/{id}/retrial with If-Match.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB MS exposes or forwards the retrial action only when the user context and runtime state allow it.
5. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes the retrial request to OC MS.
7. OC MS validates original Optimisation lifecycleStatus = FAILED.
8. OC MS creates a new Optimisation resource in the OC MS DB.
9. New Optimisation links to the original through retrialOf.
10. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED.
11. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
12. OC MS Outbox Relay publishes the event to Kafka.
13. Python/Gurobi Worker processes the new request.
14. Retrial does not move the failed Optimisation back to PROCESSING.
```

#### 3.3.7. Gurobi execute optimisation:

![Gurobi execute optimisation](optimisation-worker-execution.svg)

```text
1. Python/Gurobi Worker consumes OptimisationRequestedEvent with instruction = EXECUTE from Kafka.
2. Worker validates event idempotency and execution eligibility.
3. Worker resolves the required runtime context and internal deterministic model binding.
4. Worker invokes Gurobi Optimiser.
5. Gurobi Optimiser returns solver output, infeasibility information, or failure information.
6. Worker maps the outcome to COMPLETED, INFEASIBLE, or FAILED.
7. Worker publishes OptimisationCompletedEvent to Kafka with status COMPLETED, INFEASIBLE, or FAILED.
8. OC MS Inbox Consumer consumes the worker outcome event.
9. OC MS Inbox Consumer applies idempotency and stale/late-event checks.
10. OC MS Inbox Consumer updates OC MS DB with lifecycle/result projection.
11. User observes the outcome through GET /optimisation/{id}.
```

## 4. Capability matrix:

| **Component** | **Responsibility** |
|---|---|
| **Microsoft Entra ID** | Provides SSO authentication for users before they access experience layer. Supplies the identity context used by the user-facing access path. |
| **ACG approval process** | Governs operator access to experience layer. Users must be approved through the organisational access-control process before they can use the experience layer optimisation experience. |
| **OGW** | User-context-aware gateway for experience layer APIs and experience layer UI integration. Uses user SSO OAuth2 from the UI path and propagates user identity context into the experience layer. South-bound access to OSB MS is protected using mTLS and user context tokens. |
| **Experience layer UI** | Provides the user/operator-facing experience for discovering optimisation capabilities, submitting requests, monitoring state, cancelling, retrying, and viewing results. |
| **OSB MS** | Builds and orchestrates the experience layer screen/backend experience. Integrates with NGW using mTLS and OAuth2 system-to-system to call backend optimisation APIs. |
| **NGW** | Exposes backend optimisation domain APIs for OD MS and OC MS. Provides the controlled backend API entry point for OSB MS and other authorised system consumers. |
| **OD MS** | Owns the definition side of the optimisation platform through `OptimisationSpecification`. Defines what is allowed using `specCharacteristic[]`, `expressionSpecification`, and `targetEntitySchema`. Does not carry runtime values or decide solver outcomes. |
| **OD MS Database** | Stores `OptimisationSpecification` records, version metadata, lifecycle state, request contracts, timestamps, ETag/revision data, and retained retired specifications for audit/history. |
| **OC MS** | Owns runtime `Optimisation` resources. Carries accepted runtime `expression.expressionValue.context.targets[]`, `constraints[]`, and `preferences[]`; validates against the active OD `targetEntitySchema`; uses `422 OPTIMISATION_CONTRACT_VIOLATION` for contract/cardinality failures; manages lifecycle, cancellation, retrial, outbox/inbox integration, and result projection. |
| **OC MS Database** | Stores runtime `Optimisation` resources, accepted runtime expression values, optional source context, lifecycle state, status reasons, result projections, retrial links, timestamps, ETag/revision data, outbox records, and inbox records. |
| **OC MS Outbox Relay** | Publishes persisted OC MS outbox records to Kafka after DB commit. Publishes `OptimisationRequestedEvent` with `instruction = EXECUTE` or `instruction = CANCEL`. |
| **Kafka topic** | Main internal event stream for worker instructions and outcomes between OC MS and the Python/Gurobi Worker. Uses CloudEvents-style Kafka headers. |
| **Kafka DLQ** | Holds events that cannot be safely processed after retry/retrial handling. Preserves original event payload and failure metadata for operational investigation and replay decisions. |
| **Python/Gurobi Worker** | Consumes `OptimisationRequestedEvent`. For `EXECUTE`, resolves internal deterministic model binding, resolves required data, executes optimisation, and emits `OptimisationCompletedEvent`. For `CANCEL`, cancels/stops/ignores processing where safely possible. Determines `COMPLETED`, `INFEASIBLE`, or `FAILED` terminal outcome. |
| **Internal deterministic optimisation models** | Own solver-specific logic that is not exposed externally. Encapsulate objective formulation, constraints, candidate-resource rules, model binding, solver configuration, and Gurobi formulation. |
| **Gurobi Optimiser** | Executes the mathematical optimisation model prepared by the worker/model layer. Produces solve outcomes that the worker maps into `COMPLETED`, `INFEASIBLE`, or `FAILED`. |
| **Analytics platform/data sources** | Provides authorised datasets required by the worker/model layer, such as topology snapshots, traffic forecasts, capacity information, inventory data, or other optimisation context datasets. |
| **OC MS Inbox Consumer** | Consumes worker outcome events, applies idempotency and stale/late-event handling, maps outcomes to lifecycle states, and projects result/failure details into the runtime `Optimisation` resource. |
| **Operational support/monitoring** | Monitors service health, Kafka lag, outbox/inbox processing, worker failures, solver failures, DLQ records, retrial counts, stale/late events, and optimisation lifecycle/result trends. |

## 5. Solution security:

### 5.1. User authentication and access governance:

Users access the experience layer experience through the organisational ACG approval process and SSO using Microsoft Entra ID.

```text
User -> ACG approval process -> Microsoft Entra ID SSO -> OGW -> experience layer APIs / experience layer UI
```

OGW is the user-context-aware gateway for the experience layer channel. It uses user SSO OAuth2 from the UI/experience layer API path and propagates user identity context into the experience layer.

### 5.2. Experience layer internal access path:

OGW integrates with OSB MS using:

```text
mTLS
User Context JWT
```

This preserves user context while securely invoking experience layer backend experience services.

```text
OGW / experience layer APIs -> OSB MS
```

### 5.3. Experience layer to optimisation backend access:

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

### 5.4. NGW to OD MS / OC MS security:

NGW integrates with OD MS and OC MS using:

```text
mTLS
service/system identity only
```

This secures backend API access from the gateway to the optimisation domain services.

User context terminates before/at NGW. NGW-to-downstream OD MS / OC MS calls do not carry or expose end-user identity, claims, roles, or scopes. Downstream services authorise the calling system/service and enforce their own resource, lifecycle, schema, concurrency, and business rules.

### 5.5. OC MS to OD MS service-to-service security:

OC MS calls OD MS to validate referenced `OptimisationSpecification` resources. This internal service-to-service communication is secured using mTLS through a service mesh.

```text
OC MS -> mTLS -> OD MS
```

OC MS uses this call to validate:

```text
OptimisationSpecification exists
OptimisationSpecification lifecycleStatus = ACTIVE
expression.expressionValue matches the referenced OptimisationSpecification.targetEntitySchema
```

### 5.6. Kafka security:

OC MS and the Python/Gurobi Worker integrate through Kafka.

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

### 5.7. API concurrency control:

ETags are used for unsafe runtime actions.

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

Runtime `Optimisation` does not expose a business `version` field. ETag is used only as the HTTP concurrency mechanism.

### 5.8. Event security and integrity:

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

### 5.9. Sensitive information boundary:

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

### 5.10. Infrastructure security controls:

Every service-to-infrastructure integration must explicitly capture security controls. This applies to:

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

| **Control** | **Requirement** |
|---|---|
| **Authentication** | Every connecting workload uses an approved service identity. |
| **Authorisation** | Access is least privilege. Permissions are scoped to the required resource and operation. No broad wildcard, cluster-wide, schema-wide, or admin/root access by default. |
| **Encrypted connectivity** | Transport is encrypted. mTLS is used where supported and appropriate. Kafka broker connectivity uses TLS/mTLS where supported. |
| **Secret and certificate management** | Credentials, keys, tokens, and certificates are stored in approved secret management. Rotation is supported without application code changes where possible. |
| **Environment separation** | Principals, roles, credentials, topics, schemas, and namespaces are environment-scoped. |
| **Audit and monitoring** | Authentication failures, authorisation denials, privileged operations, replay/admin actions, Kafka lag, DLQ growth, and unusual infrastructure access are logged and monitored. |
| **Ownership** | Each design brief identifies the owning service, resource owner, allowed operations, and operational support path. |

## 6. Important quality attributes:

### 6.1. Availability:

OD MS and OC MS should be deployed as independently scalable and highly available services. OD MS availability is important for capability discovery and request validation. OC MS availability is critical for runtime optimisation creation, lifecycle reads, cancellation, retrial, and event projection.

Kafka availability is critical for asynchronous worker instruction and outcome exchange. The outbox/inbox patterns reduce data-loss risk during transient service or Kafka failures. Runtime optimisation records remain durable in OC MS DB even if worker execution is delayed. DLQ provides a controlled path for poison or unprocessable events.

### 6.2. Scalability:

OD MS scales primarily for read-heavy capability discovery. OC MS scales for runtime API traffic, outbox relay throughput, and inbox outcome processing. Python/Gurobi workers scale horizontally based on optimisation workload, queue depth, and solver runtime characteristics.

Kafka consumer groups allow worker scaling and OC MS inbox scaling. Large or long-running optimisation jobs are handled asynchronously and do not block REST API request threads.

### 6.3. Performance:

`POST /optimisation` returns `202 Accepted` after syntactic and OD-MS-contract validation only. Solver execution is asynchronous and decoupled from REST request latency.

`GET /optimisation/{id}` provides polling of lifecycle and result state. `GET /optimisation` returns summary-only records by default to avoid large list payloads. Runtime `result` is omitted until available. OD MS specification responses may use caching where appropriate. OC MS runtime responses do not use response `Cache-Control` for now.

## 7. Risks:

| **Risk** | **Impact** | **Mitigation** |
|---|---|---|
| **Long-running Gurobi executions** | Delayed optimisation outcomes and increased worker capacity pressure. | Use asynchronous execution, worker scaling, queue monitoring, timeout controls, and operational alerting. |
| **Best-effort cancellation** | A running optimisation may not stop immediately or may produce a late outcome. | Use `CANCELLING` state, worker cancellation handling, and late outcome idempotency rules. |
| **Kafka consumer lag** | Execution or result projection may be delayed. | Monitor consumer lag, scale workers/inbox consumers, and alert on thresholds. |
| **Invalid or stale context datasets** | Poor, infeasible, or failed optimisation outcomes. | Use request contract validation, dataset versioning, worker diagnostics, and operational monitoring. |
| **DLQ growth** | Indicates poison messages, schema drift, or repeated processing failures. | Monitor DLQ, preserve failure metadata, and define replay/remediation procedures. |
| **Misconfigured internal model binding** | OD MS may expose a valid request contract while worker execution fails. | Add deployment validation, contract tests between OD MS and worker model binding, and pre-production model checks. |
| **Overexposure of solver details** | Sensitive optimisation logic could leak externally. | Keep OD MS limited to caller-facing request contracts and keep solver details internal. |
| **Incorrect specification activation** | Wrong `ACTIVE` specification may affect all new requests for a specification family. | Use ETag/If-Match, lifecycle governance, review/approval, and only one ACTIVE version per family. |
| **Complex access path through experience layer gateways** | Misconfiguration could break user context propagation or backend access. | Use clear contract testing across OGW, OSB MS, NGW, OD MS, and OC MS. |

## 8. Assumptions:

- Operators access experience layer only after ACG approval.
- User/operator authentication uses Microsoft Entra ID SSO.
- OGW is the user-context-aware gateway for experience layer APIs and experience layer UI integration.
- OGW integrates with OSB MS using mTLS and User Context JWT.
- OSB MS integrates with NGW using mTLS and OAuth2 system-to-system.
- NGW exposes OD MS and OC MS APIs to authorised backend consumers.
- NGW integrates with OD MS and OC MS using mTLS.
- User context terminates before/at NGW; downstream OD MS / OC MS calls use system/service identity only.
- OC MS calls OD MS using mTLS for internal service-to-service validation.
- Kafka is available as the event backbone.
- Python/Gurobi Worker has authorised access to required analytics/data sources.
- The worker owns internal deterministic model binding and Gurobi execution details.
- Runtime `Optimisation` is asynchronous by design.
- `sourceContext` is optional and may be omitted for generic optimisation requests.
- Runtime `Optimisation` does not expose a business `version` field.

## 9. Constraints:

- NGW-exposed backend APIs use TMF-style API conventions where appropriate.
- `OptimisationSpecification` and `Optimisation` are optimiser-domain platform resources, not native TMF921 resource names.
- OGW-exposed experience layer APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF REST compliant.
- Do not expose Gurobi model formulation, solver configuration, objective internals, candidate-resource rules, or model binding through public APIs.
- OD MS exposes only the caller-facing `OptimisationSpecification` request contract.
- OC MS performs syntactic and OD-MS-contract validation only.
- Runtime `Optimisation` does not expose a `version` field.
- Runtime `Optimisation` does not support client-side `PUT` or `DELETE`.
- Cancellation is represented through `lifecycleStatus = CANCELLING` and an `OptimisationRequestedEvent` with `instruction = CANCEL`.
- Only one `ACTIVE` `OptimisationSpecification` is allowed per specification family.
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
DELETE /optimisationManagement/v1/optimisation/{id}
```

### 10.3. Runtime lifecycle states:

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
| **`ACKNOWLEDGED`** | OC MS accepted the runtime optimisation request and persisted it. |
| **`QUEUED`** | Request is waiting for worker processing. |
| **`PROCESSING`** | Python/Gurobi Worker is executing or preparing the optimisation. |
| **`COMPLETED`** | Worker returned successful completion and result is available. |
| **`INFEASIBLE`** | Worker/model determined no feasible solution exists. |
| **`FAILED`** | Technical/runtime failure occurred. |
| **`CANCELLING`** | Cancellation was requested and is being handled. |
| **`CANCELLED`** | Optimisation was cancelled or safely resolved as cancelled. |

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

### 10.4. Kafka topics:

```text
t7.optimisation.events
t7.optimisation.events.dlq
```

### 10.5. Event types:

```text
OptimisationRequestedEvent
OptimisationCompletedEvent
```

A separate `OptimisationFailedEvent` is not used by default. Failed and infeasible outcomes are represented inside `OptimisationCompletedEvent.status`.

### 10.6. Worker instructions:

```text
EXECUTE
CANCEL
```

### 10.7. Worker terminal status values:

```text
COMPLETED
INFEASIBLE
FAILED
```

### 10.8. Outcome mapping:

```text
COMPLETED -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILED -> FAILED
```

### 10.9. Canonical runtime expression shape:

Runtime optimisation requests carry actual runtime values under `expression.expressionValue.context`:

```json
{
  "expression": {
    "@type": "JsonLdExpression",
    "expressionLanguage": "JSON-LD",
    "expressionValue": {
      "@context": {
        "t7opt": "https://example.com/ontology/optimisation#"
      },
      "@type": "t7opt:OptimisationRequestExpression",
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

### 10.10. Validation and outcome responsibility:

The active design distinguishes request-contract validation from optimiser outcome.

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
```

Use `422 OPTIMISATION_CONTRACT_VIOLATION` for contract/cardinality failures, such as fewer than the required number of candidate resources for a selection optimisation.

Use `INFEASIBLE` only when the request is valid and the worker/model determines no feasible solution exists.

### 10.11. Key artifacts:

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
