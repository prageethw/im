# End-to-End Solution Brief — Optimisation Platform

**Document status:**

| **Field** | **Value** |
|---|---|
| **Status** | Baseline candidate |
| **Scope** | Optimisation platform end-to-end architecture |
| **Source path** | `baseline/optimiser/e2e/optimisation-e2e-solution-brief.md` |
| **Source of truth** | GitHub `main` |
| **Last aligned** | 2026-05-26 |
| **Last verified against OD/OC/OSB/OW specs** | 2026-05-26 |
| **Alignment scope** | Aligned with committed OD MS, OC MS, OSB MS, and OW MS specifications, including OD `specKey`, DRAFT `draftId`, official version, OC resolved contract-pointer rules, OC `creationContext.reason`, non-terminal `CANCELLATIONFAILED`, header-only ETag handling, circuit-breaker response signalling, OW MS execution ownership, OD and OC lifecycle diagrams, and platform resource model extension posture. |

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

- definition of optimisation capabilities
- runtime optimisation control
- worker and solver execution
- experience-layer presentation

## 2. Solution summary:

The solution provides a reusable, asynchronous optimisation platform backed by deterministic optimisation workers.

Core services:

| **Service** | **Responsibility** |
|---|---|
| **OD MS(Optimisation Definition MS)** | Owns the governed `OptimisationSpecification` catalogue, lifecycle, draft candidate identity, official versioning, and caller-facing request contracts. |
| **OC MS(Optimisation Controller MS)** | Owns runtime `Optimisation` resources, lifecycle, cancellation, retrial, persistence, event integration, result projection, and resolved specification contract pointers. |
| **OSB MS(Optimisation Screen Builder MS)** | Provides the OEX backend-for-frontend experience, shapes UI views and actions using user context, and calls backend optimisation APIs through NGW. |
| **OW MS (Optimisation Worker MS)** | Python worker service that consumes Kafka worker instructions, integrates with the Gurobi Python API, executes or cancels optimisation work, and emits outcome facts. |

OW MS means Optimisation Worker MS. OW MS emits outcome facts only; OC MS owns REST-visible lifecycle and result projection.

Operator access to the experience layer is governed by the ACG approval process and Microsoft Entra ID SSO. OGW invokes OSB MS using mTLS and User Context JWT. OSB MS invokes NGW using mTLS and OAuth2 system-to-system. User context stops before NGW; downstream OD MS and OC MS calls use service identity only.

OC MS validates the request structure and referenced ACTIVE OD MS request contract, persists the runtime `Optimisation` resource, returns `201 Created`, writes `OptimisationRequestedEvent` to its outbox, and drives execution asynchronously through Kafka. OC MS also owns external optimisation webhook subscriptions through `/optimisation/hub` and emits `OptimisationStatusChangeEvent` notifications after lifecycle or result projection is durably persisted.

Kafka carries worker instructions and outcomes, with a dedicated DLQ for unprocessable events. OW MS consumes `EXECUTE` or `CANCEL` instructions and emits execution outcomes and cancellation-command outcomes through `OptimisationCompletedEvent`.

NGW-exposed backend APIs use TMF-style API conventions where appropriate. `OptimisationSpecification` and `Optimisation` are optimiser-domain platform resources, not native TMF Open API resources. OC MS external webhook subscription and delivery payloads follow the Intent-style `/hub` callback pattern. OGW-exposed experience APIs, private MS-to-MS APIs, and internal Kafka events do not need to be TMF-compliant.

Platform resource model extensions are deliberate and documented in the owning service specifications. OD MS owns `specKey`, `draftId`, DRAFT candidate operations, and ACTIVE retirement semantics. OC MS owns runtime `creationContext`, cancellation and retrial commands, and the `CANCELLATIONFAILED` lifecycle value. OSB exposes experience-layer view models over these backend platform resources and must preserve their semantics.

## 3. Solution elaboration:

OD MS acts as the governed catalogue of optimisation capabilities. It exposes only what callers need to discover and submit a valid optimisation request through:

- `specCharacteristic[]`
- `expressionSpecification{}`
- `targetEntitySchema{}`
- `id`, `specKey`, `draftId`, `version`, `lifecycleStatus`, and HTTP `ETag` governance

OD MS does not expose Gurobi objectives, candidate resource rules, solver configuration, model bindings, or internal formulation details.

OD MS lifecycle baseline:

```text
DRAFT -> ACTIVE -> RETIRED
```

OD MS rules:

- DRAFT candidates are mutable and carry both `id` and `draftId`; DRAFT operations are addressed by `draftId`.
- DRAFT candidates have no official public version; draft revision uses `ETag`.
- Multiple DRAFT candidates may exist for the same `OptimisationSpecification.id`.
- `draftId` is retained as provenance after activation and retirement.
- Official version is assigned by OD MS only during activation.
- Only one ACTIVE official version is enforced per `OptimisationSpecification.id`.
- Many RETIRED official versions may exist for the same `OptimisationSpecification.id`.
- ACTIVE and RETIRED specifications are immutable.
- Activation of a DRAFT candidate assigns the official version and retires any previous ACTIVE version for the same `OptimisationSpecification.id` transactionally.
- `specKey` is the mandatory logical specification key used by OD MS to resolve the server-assigned specification `id` for a DRAFT candidate.

OD identity baseline:

- `id` is the stable OptimisationSpecification lineage identity.
- `draftId` is the DRAFT candidate identity and provenance identifier after activation or retirement.
- `version` is the official immutable version identity for ACTIVE and RETIRED records.
- `specKey` is the logical specification key used for discovery and active-lineage uniqueness; it is not used by OC MS for runtime contract selection.
- ACTIVE and RETIRED records are primarily selected by `id` and `version`.
- DRAFT candidates carry an `id` but DRAFT operations are addressed by `draftId`.
- Read-only provenance lookup by `id` and `draftId` is allowed because a `draftId` can produce at most one ACTIVE or RETIRED official version within an id lineage.

OC MS acts as the runtime controller. It accepts runtime requests, validates `expression.expressionValue` against the referenced ACTIVE `OptimisationSpecification.targetEntitySchema`, creates runtime optimisation resources, manages lifecycle state, publishes worker instructions, consumes worker outcomes, and projects final results.

OC MS runtime baseline:

- Runtime Optimisation has no business version.
- POST optimisation returns `201 Created` because the resource is created immediately.
- Execution is asynchronous.
- Runtime Optimisation includes `creationContext.reason = NEW` for normal requests and `creationContext.reason = RETRIAL` for retrial-created resources.
- Result is absent during active processing states and may be present according to OC MS lifecycle rules.
- `optimisationSpecification.id` is mandatory in the runtime create request.
- OC MS resolves the current ACTIVE `OptimisationSpecification` by id at acceptance time.
- OC MS persists the resolved `optimisationSpecification.id`, `version`, `draftId`, and `href` as the immutable contract pointer for the runtime record. OD MS ETags may be retained internally for cache validation, audit, and troubleshooting, but are not exposed inside the runtime payload.
- `expression.iri` is mandatory and identifies the submitted runtime expression semantics.
- OC MS verifies runtime `expression.iri` against the resolved `OptimisationSpecification.expressionSpecification.iri`.
- OC MS must not resolve or substitute the runtime contract by `specKey`, `draftId`, `version`, or `expression.iri`.
- OC MS must not substitute a newer ACTIVE specification for an already accepted runtime record.
- Retrial reuses the original persisted contract pointer and does not re-resolve the current ACTIVE specification.

OC runtime create request rule:

- Runtime create requests provide only `optimisationSpecification.id` as the OD contract reference.
- Clients must not provide resolved specification fields such as `optimisationSpecification.version`, `draftId`, or `href` in create requests.
- Clients must not provide `specKey` in runtime create requests because `specKey` is OD catalogue metadata, not an OC runtime selector.
- OC MS resolves `version`, `draftId`, and `href` from OD MS and persists them on the accepted runtime record. ETags and If-Match are HTTP headers only and are not JSON payload fields.

OSB MS acts as the OEX backend-for-frontend. It shapes experience models such as `HomeView`, `CapabilityCard`, `RequestFormModel`, `CreationResultView`, `OptimisationSummaryView`, and `OptimisationDetailView`. OSB response models are experience models, not source-of-truth domain resources. OSB may be owned by the experience team to simplify UI flows by aggregating and shaping payloads for UI components.

### 3.1. Use case view:

![Use case view](optimisation-use-case-view.svg)

The diagram is intentionally simplified and shows the main optimisation platform use cases. The table below provides the more detailed use-case breakdown used by the process views and implementation alignment.

| **No.** | **Use case** | **Actor** | **Summary** | **Outcome** |
|---:|---|---|---|---|
| **1** | Discover optimisation capability | User, OEX, or authorised platform service | Retrieve visible ACTIVE `OptimisationSpecification` capabilities from OD MS through OSB and NGW or system API access. | Caller understands which optimisation capability and request contract to use. |
| **2** | Create optimisation specification | Optimisation domain engineer | Create a governed `OptimisationSpecification` DRAFT in OD MS after agreement with E2E teams. | Mutable DRAFT specification is created without an official public version. |
| **3** | Activate optimisation specification | Optimisation domain engineer | Promote a reviewed DRAFT candidate to ACTIVE. | OD MS assigns official version and retires previous ACTIVE for the same `OptimisationSpecification.id`. |
| **4** | Create runtime optimisation | User, OEX, or authorised platform service | Submit a runtime `Optimisation` request to OC MS using a referenced ACTIVE specification and valid expression value. | OC MS returns `201 Created` and creates an `ACKNOWLEDGED` optimisation. Execution proceeds asynchronously. |
| **5** | Monitor optimisation | User, OEX, or authorised platform service | Read current lifecycle state and result when available. | Caller sees acknowledged, queued, processing, completed, infeasible, failed, cancelling, cancellation-failed, or cancelled state. |
| **6** | Cancel optimisation | User, OEX, or authorised platform service | Request cancellation for eligible non-terminal optimisation using `If-Match`. | OC MS accepts the asynchronous cancellation command, moves to `CANCELLING`, and sends a best-effort cancel instruction. |
| **7** | Retry failed optimisation | User, OEX, or authorised platform service | Retry a `FAILED` optimisation. | New `ACKNOWLEDGED` optimisation is created with `retrialOf` attribute; original failed record stays failed. |
| **8** | Execute optimisation | OW MS | Consume worker instruction and execute deterministic optimisation model through the Gurobi Python API, or process a cancellation command. | OW MS emits `OptimisationCompletedEvent` with execution outcomes `COMPLETED`, `INFEASIBLE`, or `FAILED`, and cancellation-command outcomes `CANCELLED` or `CANCELLATIONFAILED`. |
| **9** | Retrieve optimisation outcome | User, OEX, or authorised platform service | Retrieve completed result, infeasible explanation, failure details, or cancellation state. | Caller receives final projected runtime state/result from OC MS. |
| **10** | Subscribe to optimisation status changes | Authorised platform service or external subscriber | Register a callback through `/optimisation/hub` for `OptimisationStatusChangeEvent` delivery. | Subscriber receives webhook notifications after OC MS persists lifecycle or result projection, and can call `GET /optimisation/{id}` for the authoritative state. |

### 3.2. Logical view:

![Logical view](optimisation-logical-view.svg)

Logical integration model:

```text
User -> OEX UI -> Microsoft Entra ID SSO -> OGW -> OSB MS -> NGW -> OD MS and OC MS -> Kafka -> OW MS -> Gurobi Optimiser
OC MS -> /optimisation/hub subscription delivery -> subscriber callback URL
```

Key logical relationships:

```text
1. User -> Microsoft Entra ID: user authenticates using SSO after ACG approval.
2. UI -> OGW: OGW is the user-context-aware gateway.
3. OGW -> OSB MS: mTLS and User Context JWT.
4. OSB MS -> NGW: mTLS and OAuth2 system-to-system.
5. NGW -> OD MS: mTLS and service identity only.
6. NGW -> OC MS: mTLS and service identity only.
7. OC MS -> OD MS: direct internal service-to-service mTLS call for specification validation; this path does not route through NGW.
8. OC MS -> Kafka: emits OptimisationRequestedEvent with EXECUTE or CANCEL.
9. OW MS -> Kafka: consumes requested events and emits OptimisationCompletedEvent.
10. OC MS <- Kafka: consumes worker outcomes and projects result.
11. OC MS -> subscriber callback: emits OptimisationStatusChangeEvent after projected lifecycle or result changes are persisted.
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
7. OD MS reads visible ACTIVE `OptimisationSpecification` records by default. Default lookup by `id` resolves the current ACTIVE version where one exists.
8. OD MS returns capability and request-contract metadata.
9. OSB shapes CapabilityCard or RequestFormModel as needed.
10. Caller receives capabilities and the request contract needed to submit a runtime optimisation.
```

Normal OEX capability browsing defaults to ACTIVE capabilities only. `capabilityId` maps to OD MS `OptimisationSpecification.id` in phase one; OSB aliases or slugs are not introduced in the baseline.

#### 3.3.2. Create optimisation specification:

![Create optimisation specification](optimisation-specification-creation.svg)

```text
1. Approved optimisation domain engineer starts catalogue and specification creation journey.
2. Request reaches OGW.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB validates the user-context journey access.
5. OSB calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes create request to OD MS.
7. OD MS authenticates and authorises the service caller.
8. OD MS validates OptimisationSpecification request shape.
9. OD MS persists a mutable DRAFT candidate with `id`, `draftId`, `specKey`, and without official public version.
10. OD MS returns 201 Created with Location, ETag, `id`, and `draftId`.
11. OSB shapes catalogue-management response if catalogue management is enabled.
```

Catalogue-management journeys are feature-gated and out of phase-one scope unless explicitly enabled.

#### 3.3.3. Activate optimisation specification:

![Activate optimisation specification](optimisation-specification-activation.svg)

```text
1. Approved optimisation domain engineer requests activation of a reviewed DRAFT candidate.
2. OSB exposes this only when catalogue management is enabled and user context allows it.
3. OSB calls NGW using mTLS and OAuth2 system-to-system.
4. NGW routes activation PATCH or PUT to OD MS.
5. OD MS validates ETag, selected `draftId`, the DRAFT lifecycle, the draft’s resolved `id`, and the full specification contract.
6. OD MS assigns official version during activation.
7. OD MS moves the selected DRAFT candidate to ACTIVE.
8. OD MS transactionally retires any previous ACTIVE version for the same `OptimisationSpecification.id`.
9. ACTIVE and RETIRED specifications become immutable.
```

#### 3.3.4. Create and execute optimisation:

![Create and execute optimisation](optimisation-runtime-execution.svg)

```text
1. User initiates optimisation journey through OEX or another authorised caller submits a runtime request.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB validates user context and shapes the request and action model.
5. OSB calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes POST /optimisation to OC MS.
7. OC MS validates referenced `OptimisationSpecification.id` exists and resolves the current ACTIVE version at request-acceptance time.
8. OC MS validates runtime expression.iri is present and matches the referenced OptimisationSpecification.expressionSpecification.iri.
9. OC MS validates expression.expressionValue against the referenced ACTIVE targetEntitySchema.
10. OC MS persists runtime Optimisation with lifecycleStatus = ACKNOWLEDGED and creationContext.reason = NEW.
11. OC MS stores resolved `optimisationSpecification.id`, `version`, `draftId`, and `href` as the immutable contract pointer. OD MS ETags remain HTTP headers and may be retained internally for cache validation, audit, and troubleshooting only.
12. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE to outbox in same transaction.
13. OC MS returns 201 Created with Location, ETag, and runtime resource body after resource persistence and outbox write, before worker execution completes. The response always shows lifecycleStatus = ACKNOWLEDGED because ACKNOWLEDGED is the only initial lifecycle state after successful runtime resource creation.
14. OC MS Outbox Relay publishes OptimisationRequestedEvent to Kafka.
15. OC MS advances ACKNOWLEDGED -> QUEUED after successful Kafka publish. QUEUED is projected later and is not the initial creation response state.
16. OW MS consumes OptimisationRequestedEvent.
17. OW MS resolves deterministic model binding and invokes Gurobi Optimiser.
18. OW MS publishes OptimisationCompletedEvent with execution outcomes COMPLETED, INFEASIBLE, or FAILED, and cancellation-command outcomes CANCELLED or CANCELLATIONFAILED. COMPLETED, INFEASIBLE, and FAILED are terminal execution outcomes. CANCELLED is a terminal cancellation-command outcome. CANCELLATIONFAILED is a non-terminal cancellation-command outcome.
19. OC MS Inbox Consumer applies idempotency and stale and late event checks.
20. OC MS updates lifecycle and result projection.
21. If a matching `/optimisation/hub` subscription exists, OC MS emits an external `OptimisationStatusChangeEvent` after the projection is persisted.
22. Caller polls through User -> OEX -> OGW -> OSB MS -> NGW -> OC MS, or receives webhook notification and then calls `GET /optimisation/{id}`, to retrieve authoritative status and result.
```

#### 3.3.5. Monitor optimisation:

![Monitor optimisation](optimisation-status-retrieval.svg)

```text
1. User, OEX, or authorised platform service requests current status and result.
2. Request reaches OGW where user context is applicable.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB validates access to the requested optimisation view.
5. OSB calls NGW using mTLS and OAuth2 system-to-system.
6. NGW routes GET /optimisation/{id} to OC MS.
7. OC MS returns lifecycleStatus, status reason, terminal result where present, cancellation-command outcome details where present, failure details, and links and actions where applicable.
8. OSB shapes OptimisationDetailView or OptimisationSummaryView.
9. Caller receives current state.
```

Phase-one OEX and OSB status refresh is REST polling against OC MS through NGW. OC-owned webhook notifications through `/optimisation/hub` may also notify subscribed consumers of lifecycle and result changes. Polling remains the fallback and `GET /optimisation/{id}` remains the authoritative read model. OSB must not infer terminal status locally; terminal state and any later terminal outcome after CANCELLATIONFAILED must come from OC MS.

#### 3.3.6. Cancel optimisation:

![Cancel optimisation](optimisation-cancellation.svg)

```text
1. Consumer calls OSB cancellation endpoint with current ETag and If-Match context.
2. OSB uses backend _links as the authoritative action affordance signal.
3. actionVisible = backend_link_present AND user_context_allows.
4. OSB forwards If-Match from OC MS ETag and must not generate its own backend ETag.
5. NGW routes POST /optimisation/{id}/cancellation to OC MS.
6. OC MS validates ETag and eligible non-terminal lifecycle.
7. OC MS returns the status defined by the OC MS API contract for accepted cancellation. In the current baseline this is 202 Accepted, with lifecycleStatus = CANCELLING until a cancellation command outcome or terminal optimisation outcome is projected.
8. OC MS writes OptimisationRequestedEvent with instruction = CANCEL to outbox.
9. OC MS Outbox Relay publishes event to Kafka.
10. OW MS stops, cancels, or ignores work where safely possible.
11. Baseline cancellation confirmation is `OptimisationCompletedEvent.status = CANCELLED`; OC MS projects CANCELLED only after that worker confirmation. If OW MS reports `CANCELLATIONFAILED`, OC MS projects non-terminal CANCELLATIONFAILED and continues to accept a later valid terminal outcome of COMPLETED, INFEASIBLE, or FAILED.
```

Cancellation is best-effort. Cancellation has no required request body; optional reason or comment metadata does not change cancellation semantics. OSB must not send an empty JSON object solely to force `Content-Type`. If no body is supplied by OEX, OSB should call OC MS without a request body. Cancellation requested from a non-eligible lifecycle state, including `CANCELLING`, `CANCELLATIONFAILED`, or terminal states, returns `409 Conflict`.

OW MS cancellation handling is implementation-specific. The `CANCEL` instruction is best-effort; OW MS may complete a solve cycle before honouring cancellation where immediate interruption is not safe or supported. If `CANCEL` arrives but OW MS completes first, OC MS projects the actual terminal outcome; cancellation remains best-effort.

#### 3.3.7. Retry failed optimisation:

![Retry failed optimisation](optimisation-retrial.svg)

```text
1. Consumer calls OSB retrial endpoint with current ETag and If-Match context.
2. OSB exposes retrial only when backend _links includes retrial and user context allows it.
3. OSB forwards If-Match from OC MS ETag.
4. NGW routes POST /optimisation/{id}/retrial to OC MS.
5. OC MS validates original Optimisation lifecycleStatus = FAILED.
6. OC MS creates a new Optimisation resource.
7. New Optimisation links to original through retrialOf.
8. New Optimisation starts with lifecycleStatus = ACKNOWLEDGED and creationContext.reason = RETRIAL.
9. OC MS writes OptimisationRequestedEvent with instruction = EXECUTE for the new Optimisation.
10. OC MS returns 201 Created with Location, ETag, and the new runtime Optimisation body before worker execution completes.
11. OW MS processes the new request asynchronously.
```

Retrial is available only from `FAILED` in the baseline. Retrial is not available from `INFEASIBLE` by default because `INFEASIBLE` is a valid optimisation or model outcome, not a technical failure. Retrial is not available from `CANCELLATIONFAILED`. If the optimisation later reaches `FAILED`, retrial may then be requested from `FAILED`. Retrial has no required request body and does not allow overrides. OSB must not send an empty JSON object solely to force `Content-Type`. If no body is supplied by OEX, OSB should call OC MS without a request body. Retrial resubmits the original accepted expression and reuses the original persisted OC contract pointer, including `id`, `version`, `draftId`, and `href`. When OC MS creates the retrial resource, it returns `201 Created` with the new runtime Optimisation id, `Location`, `ETag`, and resource body.

#### 3.3.8. OW MS executes optimisation:

![OW MS executes optimisation](optimisation-worker-execution.svg)

```text
1. OW MS consumes OptimisationRequestedEvent with instruction = EXECUTE.
2. OW MS validates event idempotency and execution eligibility.
3. OW MS resolves runtime context and internal deterministic model binding.
4. OW MS invokes Gurobi Optimiser.
5. Gurobi Optimiser returns solver output, infeasibility information, failure information, or cancellation confirmation.
6. OW MS maps execution outcomes to COMPLETED, INFEASIBLE, or FAILED, and maps cancellation-command outcomes to CANCELLED or CANCELLATIONFAILED.
7. OW MS publishes OptimisationCompletedEvent.
8. OC MS Inbox Consumer applies idempotency and stale and late event checks.
9. OC MS updates runtime lifecycle and result projection.
10. User observes outcome through OC MS REST status and detail exposed through OSB and NGW.
```

OW MS does not set REST-visible `lifecycleStatus` directly; it emits outcome facts consumed and projected by OC MS.

OW MS idempotency in this E2E brief means duplicate event detection using `eventId` or `ce-id`, `optimisationId`, and instruction context before executing work. Detailed OW MS eligibility and deduplication rules belong in `ow-ms/ow_ms_specification.md`.
Detailed OW MS execution eligibility, cancellation handling, solver timeout, idempotency, and DLQ rules are owned by the OW MS specification.

## 4. Capability matrix:

| **Component** | **Responsibility** |
|---|---|
| **Microsoft Entra ID** | Provides SSO authentication for users before they access OEX/experience layer. |
| **ACG approval process** | Governs operator access to the OEX optimisation experience. |
| **OGW** | User-context-aware gateway for OEX APIs. Invokes OSB MS using mTLS and User Context JWT. |
| **OEX UI and experience layer** | Provides user/operator-facing experience for discovery, request submission, monitoring, cancellation, retrial, and result viewing. |
| **OSB MS** | Builds OEX view models, applies user-context filtering, uses backend `_links` plus user context for actions, forwards ETags, and calls backend APIs through NGW. |
| **NGW** | Backend API entry point for OD MS and OC MS using service identity and mTLS. |
| **OD MS** | Owns `OptimisationSpecification` catalogue, lifecycle and version governance, `id` lineage identity, `draftId` draft provenance, official `version`, `specKey` logical key, `specCharacteristic[]`, `expressionSpecification`, and `targetEntitySchema`. |
| **OD MS Database** | Stores specification lineage records, `draftId`, `specKey`, lifecycle, official version for ACTIVE and RETIRED, ETags, provenance, and immutable retained history. |
| **OC MS** | Owns runtime `Optimisation` resources, lifecycle, accepted expression values, immutable resolved specification pointer, outbox and inbox, cancellation, retrial, and result projection. |
| **OC MS Database** | Stores runtime records, lifecycle state, statusChangeDate, sourceContext, expression, resolved specification pointer, terminal result or cancellation-command outcome details where present, relationships, outbox, and inbox records. |
| **OC MS Outbox Relay** | Publishes `OptimisationRequestedEvent` to Kafka after DB commit; successful publish drives ACKNOWLEDGED -> QUEUED. |
| **OC MS external notification outbox or delivery component** | Delivers `OptimisationStatusChangeEvent` webhook notifications after OC MS persists lifecycle or result projection. Delivery retry or DLQ does not roll back the runtime projection. |
| **Kafka topic** | Internal event stream for worker instructions and outcomes. |
| **Kafka DLQ** | Holds events that cannot be safely processed after retry handling. |
| **OW MS** | Optimisation Worker MS. Python worker service that consumes requested events, executes or cancels work through the Gurobi Python API, and emits `OptimisationCompletedEvent` outcome facts. |
| **Internal deterministic optimisation models** | Own solver-specific objective formulation, constraints, candidate-resource rules, model binding, and solver configuration. |
| **Gurobi Optimiser** | Executes mathematical optimisation prepared by worker model layer. |
| **Analytics platform/data sources** | Provides authorised datasets required by the worker or model layer. |
| **OC MS Inbox Consumer** | Consumes worker outcomes, applies idempotency/stale and late checks, and projects lifecycle and result. |
| **Operational support and monitoring** | Monitors service health, Kafka lag, outbox and inbox processing, worker failures, solver failures, DLQ, and lifecycle and result trends. |

## 5. Solution security:

### 5.1. User authentication and access governance:

Users access OEX through ACG approval and Microsoft Entra ID SSO.

```text
User -> ACG approval process -> Microsoft Entra ID SSO -> OGW -> OEX APIs and UI
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

User context stops before or at NGW. OSB performs user-context filtering and action shaping, but backend OD MS and OC MS decisions win. OD MS and OC MS authorise service identity and enforce lifecycle, schema, ETag, and business rules.

### 5.4. NGW to OD MS and OC MS security:

NGW integrates with OD MS and OC MS using:

```text
mTLS
service identity only
```

NGW-to-downstream OD MS and OC MS calls do not carry or expose end-user identity, claims, roles, or scopes.

### 5.5. OC MS to OD MS service-to-service security:

OC MS calls OD MS directly using service-to-service mTLS for specification validation. This is an internal service path and does not route through NGW.

OC MS resolves and validates the referenced specification contract:

```text
OptimisationSpecification.id exists
current ACTIVE version is resolved by OptimisationSpecification.id
resolved ACTIVE version has lifecycleStatus = ACTIVE
expression.expressionValue matches the resolved targetEntitySchema
resolved id, version, draftId, href are persisted on the runtime record
```

The persisted resolved specification reference is the immutable contract pointer for the accepted runtime Optimisation. OC MS must not re-resolve or replace that pointer later, including during retrial.

OC MS may cache immutable ACTIVE specification contracts by `id` and `version`, using OD MS ETag headers internally for cache validation, but must not infer the current active contract by stale `specKey` lookup. If OD MS is unavailable and OC MS has no valid cached immutable ACTIVE contract for the requested id, OC MS returns 503 Service Unavailable. If a valid cached immutable ACTIVE contract exists, OC MS may proceed according to cache policy. OC MS may separately maintain a request-result cache keyed by a deterministic hash of the canonical accepted runtime optimisation request body after the ACTIVE specification version is resolved. The request-result cache hash is internal metadata and does not replace runtime Optimisation identity, lifecycle, audit, or external representation. A request-result cache hit must still create or return a governed OC runtime resource according to the OC MS contract and must not bypass audit, lifecycle, or source-of-truth persistence. Request-result cache TTL and eviction policy are deployment-governed and outside this E2E baseline.

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
Replay and remediation must follow controlled operational procedures.
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
Stale or wrong If-Match -> 412 Precondition Failed
```

OSB forwards OC MS ETags and must not generate backend unsafe-operation ETags.

OD and OC ETags are conveyed through HTTP headers. Experience and view payloads must not embed ETag fields.

### 5.8. Event security and integrity:

Internal Kafka events use CloudEvents-style headers and must include:

```text
optimisationId
correlationId
traceId
eventId or ce-id
```

`OptimisationCompletedEvent` processing must be idempotent. OC MS projection must safely handle duplicate, stale, and late worker outcome events.

External `OptimisationStatusChangeEvent` webhook delivery is OC-owned and uses the Intent-style subscription model. Delivery must use platform-approved callback security such as mTLS, signed requests, shared secret, OAuth client credentials, or another governed mechanism. External event delivery is at-least-once; subscribers must deduplicate using `eventId` and must treat `GET /optimisation/{id}` as the source of truth.

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

Every service-to-infrastructure integration must explicitly capture authentication, authorisation, encrypted connectivity, secret and certificate management, environment separation, audit/monitoring, and ownership.

## 6. Important quality attributes:

### 6.1. Availability:

Availability SLA is yet to be determined.

OD MS and OC MS should be deployed as independently scalable and highly available services. Kafka availability is critical for asynchronous worker instruction and outcome exchange. Outbox and inbox patterns reduce data-loss risk during transient service or Kafka failures.

The database and Kafka cluster must meet the required availability targets for the platform. Kubernetes should run multiple pods where required and orchestrate pod placement and recovery to support the agreed availability posture.

### 6.2. Scalability:

The production environment is expected to scale dynamically based on demand.

OD MS scales primarily for capability discovery and specification retrieval. OC MS scales for runtime API traffic, outbox relay throughput, and inbox outcome processing. OW MS instances scale horizontally based on queue depth, solver runtime characteristics, and Gurobi licence or runtime capacity. OSB scales for OEX-API view traffic and can cache read-only OD-derived capability and form data only where backend cache headers allow.

Kubernetes provides the ability to scale pods based on demand.

### 6.3. Performance:

Synchronous API latency targets are to be confirmed through NFR baselining. Solver execution is excluded from REST latency because optimisation execution is asynchronous.

`POST /optimisation` returns `201 Created` after syntactic and OD-MS-contract validation, runtime resource persistence, and outbox write. Solver execution remains asynchronous and decoupled from REST request latency. 

`GET /optimisation/{id}` provides polling of lifecycle and result state. Runtime `result` is absent during active processing states, may be present for CANCELLATIONFAILED, and may be present for terminal states according to OC MS result rules. OSB and OEX status refresh is REST polling against OC MS through NGW in phase one. OC MS may also notify subscribed consumers through `/optimisation/hub` using `OptimisationStatusChangeEvent`. Webhook notification reduces polling pressure but does not replace the authoritative `GET /optimisation/{id}` read model. Polling cadence is owned by OSB MS in coordination with OEX UI/platform UX.

### 6.4. Circuit breaker and dependency fallback baseline:

Each optimiser microservice must apply circuit breakers, timeouts, bounded retries, and isolation to every remote dependency call. Remote dependencies include other microservices, databases, Kafka, Redis or cache stores, external data sources, model registries, Gurobi runtime or solver dependencies, and other external platform or system dependencies.

When a remote dependency is unavailable, timing out, unhealthy, or repeatedly failing, the circuit breaker opens and the service stops sending normal traffic to that dependency for the configured cool-down period. While the circuit breaker is open, the service monitors dependency recovery using bounded health probes or test calls according to the circuit-breaker policy. These probes are used to decide when the dependency path can move to half-open and then closed again. Probe behaviour must be rate-limited and must not overload a recovering dependency.

When a circuit breaker is triggered, the service chooses the safest valid behaviour for the operation. Depending on the endpoint and dependency, this may be fail fast, return a safe pre-cached object, return a safe instantly generated default payload, bypass a non-critical dependency, or defer through a durable asynchronous mechanism where applicable.

HTTP status and response body remain authoritative for success or failure. `x-cb-triggered: true` only indicates that a remote dependency circuit breaker affected the externally meaningful response path.

`x-cb-triggered` is diagnostic only and must not be used by clients to infer lifecycle, validation, authorisation, or optimisation outcome state.

Use `x-cb-triggered: true` only when a remote dependency circuit breaker changes the externally meaningful response path. Do not use `x-cb-triggered` for local validation errors, malformed requests, lifecycle conflicts, stale ETags, local application errors, or normal cache bypass where the service still returns a source-of-truth response.

| **Dependency / situation** | **Safe behaviour when CB is triggered** | **HTTP status / outcome** | **Header** |
|---|---|---|---|
| Non-critical cache or Redis unavailable, source of truth still available | Bypass cache and use source of truth. | Normal success status. | N/A |
| Safe cached or precomputed object available because source dependency is unavailable | Return approved cached or precomputed object. | Normal success status. | `x-cb-triggered: true` |
| Safe default payload available because dependency-backed content is unavailable | Return approved default payload instantly. | Normal success status. | `x-cb-triggered: true` |
| Required remote dependency unavailable and no safe fallback exists | Fail fast. | Usually `503 Service Unavailable`. | `x-cb-triggered: true` |
| OD MS unavailable during runtime creation and no valid cached ACTIVE contract exists | Fail fast; OC MS must not accept the runtime request without resolved contract validation. | `503 Service Unavailable`. | `x-cb-triggered: true` |
| Command or state-changing operation cannot reach required remote dependency and cannot safely complete | Do not fake acceptance. Fail fast. | Appropriate failure, usually `503`. | `x-cb-triggered: true` |
| Local validation failure, malformed request, lifecycle conflict, or stale ETag | Return normal domain/API error. | `400`, `409`, `412`, `428`, or equivalent. | N/A |
| Local application error not caused by remote dependency circuit breaker | Return normal internal error. | `500 Internal Server Error`. | N/A |
| OW MS solver/runtime dependency unavailable during asynchronous execution | Do not fake success. Retry, DLQ, backpressure, or emit safe `FAILED` as governed. | Event outcome, not REST. | N/A |

Circuit-breaker fallback must not silently alter source-of-truth semantics. Default or cached fallback must not be used to fake command acceptance, contract validation, lifecycle projection, cancellation confirmation, retrial creation, optimisation result, security visibility, or audit state.

For command and state-changing operations, the service may return a normal success status only when the operation has genuinely completed its required validation, persistence, concurrency, and durability obligations.

For OC MS runtime creation and cancellation, Kafka broker unavailability does not necessarily fail the REST command if OC MS can durably persist the runtime state and outbox record; the outbox relay handles later Kafka publication according to retry and DLQ policy.

## 7. Risks:

| **Risk** | **Impact** | **Mitigation** |
|---|---|---|
| **Long-running Gurobi executions** | Delayed optimisation outcomes and worker capacity pressure. | Asynchronous execution, worker scaling, queue monitoring, timeout controls, and alerting. |
| **OW MS solver/runtime dependency exhaustion** | Optimisation execution may be delayed or fail when Gurobi runtime, licence, model registry, or worker compute capacity is exhausted. | Worker autoscaling, queue-depth monitoring, licence/runtime capacity monitoring, backpressure, timeout controls, and DLQ or FAILED outcome handling. |
| **Best-effort cancellation** | Running optimisation may not stop immediately, may produce a late outcome, or may report that cancellation could not be honoured or confirmed. | CANCELLING state, CANCELLATIONFAILED state, worker cancellation handling, and late outcome idempotency rules. |
| **Kafka consumer lag** | Execution/result projection delay. | Monitor lag, scale consumers/workers, alert on thresholds. |
| **OD MS unavailable during runtime creation** | New runtime optimisation creation may fail when OC MS cannot resolve the current ACTIVE specification and has no valid cached immutable ACTIVE contract. | OC MS may use a valid cached immutable ACTIVE contract according to cache policy; otherwise return 503 Service Unavailable and alert on OD dependency health. |
| **Invalid or stale context datasets** | Poor, infeasible, or failed optimisation outcomes. | Request contract validation, dataset versioning, worker diagnostics, and monitoring. |
| **DLQ growth** | Poison messages, schema drift, or repeated processing failure. | DLQ monitoring, failure metadata retention, replay and remediation procedures. |
| **Misconfigured internal model binding** | Valid request contract but worker execution fails. | Deployment validation, contract tests, and pre-production model checks. |
| **Overexposure of solver details** | Sensitive optimisation logic leaks externally. | Keep solver or model details internal and return only safe generic outputs. |
| **Incorrect specification activation** | Wrong ACTIVE specification affects future requests. | OD lifecycle governance, ETag and If-Match, review, approval, and one ACTIVE official version per `OptimisationSpecification.id`. |
| **Complex access path through gateways** | User context or backend identity misconfiguration. | Contract tests across OGW, OSB, NGW, OD, and OC. |
| **Misconfigured circuit-breaker fallback** | Service may return stale/default data where source-of-truth semantics are required, or fail too aggressively. | Use endpoint-specific fallback policies, do not fake command acceptance, contract validation, lifecycle projection, cancellation confirmation, retrial creation, optimisation result, security visibility, or audit state. |
| **Cached UI/action state misuse** | User sees stale or invalid actions. | Backend `_links` plus user-context rule; backend decision wins. |

## 8. Assumptions:

- Operators access OEX only after ACG approval.
- User and operator authentication uses Microsoft Entra ID SSO.
- OGW is the user-context-aware gateway for OEX APIs.
- OGW integrates with OSB MS using mTLS and User Context JWT.
- OSB MS integrates with NGW using mTLS and OAuth2 system-to-system.
- User context stops before or at NGW; downstream OD MS and OC MS calls use service identity only.
- NGW exposes OD MS and OC MS APIs to authorised backend consumers.
- Kafka is available as the event backbone.
- OC MS external webhook notification delivery uses an Intent-style `/optimisation/hub` subscription model where enabled.
- OW MS has authorised access to required analytics data sources and required Gurobi runtime dependencies.
- Runtime `Optimisation` is asynchronous by design.
- `sourceContext` is optional and may be omitted for generic optimisation requests.
- Runtime `Optimisation` does not expose a business `version` field.
- OD MS is synchronous REST only for the initial baseline; specification events and hub support is deferred.
- OSB catalogue-management journeys are feature-gated and out of phase-one scope unless explicitly enabled.

## 9. Constraints:

- NGW-exposed backend APIs use TMF-style API conventions where appropriate.
- OC MS calls OD MS directly using service-to-service mTLS for runtime specification validation and resolved contract-pointer capture.
- `OptimisationSpecification` and `Optimisation` are optimiser-domain platform resources, not native TMF Open API resources.
- Optimiser resources are platform resource models aligned to TMF conventions; approved optimiser-specific fields, operations, headers, link relations, and lifecycle values are documented in the owning service specifications.
- OGW-exposed experience APIs, private MS-to-MS APIs, private MS-to-MS events, and internal Kafka events do not need to be TMF REST compliant.
- `x-platform-extension: true` and `x-tmf-native: false` are governance documentation response headers on external NGW-facing optimiser resources.
- `x-cb-triggered: true` is a diagnostic response header used only when a remote dependency circuit breaker changes the externally meaningful response path. It is not a business-logic switch and is not used on internal Kafka events.
- Do not expose Gurobi model formulation, solver configuration, objective internals, candidate-resource rules, or model binding through public APIs or OSB views.
- OD MS exposes only the caller-facing `OptimisationSpecification` request contract.
- OC MS performs syntactic and OD-MS-contract validation only.
- Runtime `Optimisation` does not expose a `version` field.
- Runtime `Optimisation` does not support client-side `PUT`, `PATCH`, or `DELETE`.
- Cancellation is represented through `lifecycleStatus = CANCELLING` and an `OptimisationRequestedEvent` with `instruction = CANCEL`.
- Only one `ACTIVE` official `OptimisationSpecification` version is allowed per `OptimisationSpecification.id`, and OD MS also enforces at most one current ACTIVE lineage per `specKey`.
- ETag and If-Match are required for unsafe runtime operations such as cancellation and retrial.
- Internal Kafka events do not use TMF REST `@type`, `@baseType`, or `@schemaLocation`.
- OW MS internal events must not be exposed directly to external subscribers; OC MS external webhook events are emitted only after OC MS projection is persisted.

## 10. Appendix:

### 10.1. OD MS endpoint summary:

```http
GET /optimisationManagement/v1/optimisationSpecification
POST /optimisationManagement/v1/optimisationSpecification
GET /optimisationManagement/v1/optimisationSpecification/{id}
DELETE /optimisationManagement/v1/optimisationSpecification/{id}
GET /optimisationManagement/v1/optimisationSpecification/draft/{draftId}
PATCH /optimisationManagement/v1/optimisationSpecification/draft/{draftId}
PUT /optimisationManagement/v1/optimisationSpecification/draft/{draftId}
DELETE /optimisationManagement/v1/optimisationSpecification/draft/{draftId}
```

OD `PATCH` requires `Content-Type: application/merge-patch+json`. OD `PUT` requires `Content-Type: application/json` and is allowed only for mutable DRAFT replacement/finalisation.

DRAFT candidate operations use `/optimisationSpecification/draft/{draftId}`. ACTIVE retirement uses `DELETE /optimisationSpecification/{id}` and retires the current ACTIVE version for that `id`. ACTIVE and RETIRED official versions are selected by `id` and `version`, or by `id` alone when resolving the current ACTIVE version.

### 10.2. OC MS endpoint summary:

OC MS endpoints are shown using the OC MS resource path defined by the OC MS specification. NGW may mount or route these paths according to platform gateway configuration, but the backend OC resource path remains `/optimisation` in the current baseline.

```http
GET /optimisation
POST /optimisation
GET /optimisation/{id}
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
POST /optimisation/hub
GET /optimisation/hub/{id}
DELETE /optimisation/hub/{id}
```

`/optimisation/hub` manages external webhook subscriptions for OC-owned optimisation status notifications. The unsupported runtime operation list below applies to runtime `Optimisation` resources only.

Unsupported:

```http
PUT /optimisation/{id}
PATCH /optimisation/{id}
DELETE /optimisation/{id}
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
CANCELLATIONFAILED
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
| `CANCELLATIONFAILED` | Non-terminal cancellation command outcome. Cancellation could not be honoured or confirmed, and optimisation execution may still later reach COMPLETED, INFEASIBLE, or FAILED. |
| `CANCELLED` | Optimisation was cancelled after `OptimisationCompletedEvent.status = CANCELLED` confirms cancellation was honoured safely. |

Lifecycle transition baseline:

```text
ACKNOWLEDGED -> QUEUED
QUEUED -> PROCESSING
PROCESSING -> COMPLETED
PROCESSING -> INFEASIBLE
PROCESSING -> FAILED
ACKNOWLEDGED -> CANCELLING -> CANCELLED
QUEUED -> CANCELLING -> CANCELLED
PROCESSING -> CANCELLING -> CANCELLED
CANCELLING -> CANCELLATIONFAILED
CANCELLATIONFAILED -> COMPLETED
CANCELLATIONFAILED -> INFEASIBLE
CANCELLATIONFAILED -> FAILED
FAILED -> retrial creates new ACKNOWLEDGED Optimisation with creationContext.reason = RETRIAL
```

`statusChangeDate` is updated on every lifecycle transition, including ACKNOWLEDGED -> QUEUED, QUEUED -> PROCESSING, terminal outcomes, CANCELLING -> CANCELLED, CANCELLING -> CANCELLATIONFAILED, and later CANCELLATIONFAILED -> terminal outcome transitions.

### 10.5. Kafka topics:

```text
t7.optimisation.events
t7.optimisation.events.dlq
```

### 10.6. Event types:

Internal Kafka event types:

```text
OptimisationRequestedEvent
OptimisationCompletedEvent
```

External webhook event type:

```text
OptimisationStatusChangeEvent
```

A separate `OptimisationFailedEvent` is not used by default. Failed, infeasible, cancelled, and cancellation-failed outcomes are represented inside `OptimisationCompletedEvent.status`.

### 10.7. External webhook subscription baseline:

OC MS supports an Intent-style webhook subscription model for external status notifications.

```http
POST /optimisation/hub
GET /optimisation/hub/{id}
DELETE /optimisation/hub/{id}
```

Subscription request baseline:

```json
{
  "callback": "https://consumer.example.com/optimisation/events",
  "query": "eventType=OptimisationStatusChangeEvent",
  "@type": "EventSubscription"
}
```

`OptimisationStatusChangeEvent` is emitted only after OC MS has durably persisted the corresponding lifecycle or result projection. The webhook event is a notification, not the source of truth. Callback delivery failure must not roll back OC MS lifecycle or result projection. Delivery is at-least-once; subscribers must handle duplicate and out-of-order notifications idempotently and use `GET /optimisation/{id}` when they need the authoritative current state. Baseline subscription filtering supports `eventType`; lifecycle, source-context, and specification filters may be added later where governed by OC MS.

Safe event payload shape:

```json
{
  "eventId": "evt-opt-12345-completed-001",
  "eventType": "OptimisationStatusChangeEvent",
  "eventTime": "2026-05-26T13:40:00Z",
  "correlationId": "corr-12345",
  "traceId": "trace-12345",
  "event": {
    "optimisation": {
      "id": "opt-12345",
      "href": "/optimisation/opt-12345",
      "previousLifecycleStatus": "PROCESSING",
      "newLifecycleStatus": "COMPLETED",
      "statusChangeDate": "2026-05-26T13:40:00Z",
      "resultSummary": {
        "outcome": "COMPLETED",
        "summary": "Optimisation completed successfully."
      },
      "@type": "Optimisation"
    }
  }
}
```

OW MS does not publish external webhook events. `OptimisationRequestedEvent` and `OptimisationCompletedEvent` remain internal OC-to-OW events.

### 10.8. Worker instructions:

```text
EXECUTE
CANCEL
```

### 10.9. Worker outcome and cancellation-command status values:

```text
COMPLETED
INFEASIBLE
FAILED
CANCELLED
CANCELLATIONFAILED
```

`COMPLETED`, `INFEASIBLE`, and `FAILED` are execution outcomes. `CANCELLED` and `CANCELLATIONFAILED` are cancellation-command outcomes.

### 10.10. Outcome mapping:

Worker emits `OptimisationCompletedEvent.status` using one of the following execution outcome or cancellation-command status values:

```text
COMPLETED
INFEASIBLE
FAILED
CANCELLED
CANCELLATIONFAILED
```

OC MS maps worker execution outcome and cancellation-command status values to runtime lifecycle status as follows:

```text
COMPLETED -> lifecycleStatus COMPLETED
INFEASIBLE -> lifecycleStatus INFEASIBLE
FAILED -> lifecycleStatus FAILED
CANCELLED -> lifecycleStatus CANCELLED
CANCELLATIONFAILED -> lifecycleStatus CANCELLATIONFAILED
```

`COMPLETED`, `INFEASIBLE`, and `FAILED` are terminal execution outcomes. `CANCELLED` is a terminal cancellation-command outcome. `CANCELLATIONFAILED` is a non-terminal cancellation-command outcome.

`CANCELLATIONFAILED` is not a terminal optimisation outcome. It represents cancellation-command failure and may later be followed by COMPLETED, INFEASIBLE, or FAILED. Do not introduce an alternate success status unless the OW MS contract is explicitly changed to emit one.

### 10.11. Canonical runtime expression shape:

Runtime optimisation requests carry actual runtime values under `expression.expressionValue.context`:

Runtime creation requires both `optimisationSpecification.id` and `expression.iri`. The id selects the exact governed `OptimisationSpecification` contract. The runtime `expression.iri` identifies the submitted expression semantics and must match the referenced `OptimisationSpecification.expressionSpecification.iri`.

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

OD MS defines the allowed structure using `OptimisationSpecification.targetEntitySchema`. The example ontology IRI and JSON-LD aliases are illustrative unless fixed by the concrete active schema. OC MS carries the accepted runtime values and validates them against the referenced ACTIVE schema.

### 10.12. Result presence rules:

```text
result MUST be absent while lifecycleStatus is ACKNOWLEDGED, QUEUED, PROCESSING, or CANCELLING.
result MAY be present when lifecycleStatus is COMPLETED, INFEASIBLE, FAILED, CANCELLED, or CANCELLATIONFAILED.
CANCELLED result details may include safe cancellation summary metadata but must not expose worker internals.
CANCELLATIONFAILED result details may include safe cancellation command outcome metadata, but must be fully replaced and not merged when a later COMPLETED, INFEASIBLE, or FAILED terminal outcome is projected.
FAILED result details may include safe error codes and messages only.
```

### 10.13. Validation and outcome responsibility:

OC MS validates:

- required fields
- enum and value-type rules
- request contract shape
- cardinality rules defined by `targetEntitySchema`

OC MS does not evaluate:

- solver feasibility
- candidate ranking
- metric-vs-constraint fit
- objective trade-offs

OW MS returns terminal execution outcomes and cancellation-command outcomes:

- `COMPLETED`
- `INFEASIBLE`
- `FAILED`
- `CANCELLED`
- `CANCELLATIONFAILED`

`CANCELLATIONFAILED` is not terminal and must not block later projection of COMPLETED, INFEASIBLE, or FAILED.

Use `400 Bad Request` for malformed requests, missing required top-level request fields, unsupported priority values, or forbidden server-controlled fields. Use `422 OPTIMISATION_CONTRACT_VIOLATION` for OD contract, expression IRI compatibility, targetEntitySchema, and cardinality failures. Use `INFEASIBLE` only when the request is valid and the worker or model determines no feasible solution exists.

### 10.14. Key artifacts:

PUML and DrawIO files are editable source artifacts. Rendered SVG and PNG exports are the preferred review and consumption artifacts where available.

OSB MS has no lifecycle state diagram in the baseline because OSB is an experience-layer facade and does not own resource lifecycle state. Runtime lifecycle is owned by OC MS.

```text
od-ms/od-ms-specification.md
od-ms/od-ms.oas.yaml (pending)
od-ms/od-ms-lifecycle-state.puml
od-ms/od-ms-lifecycle-state.svg
oc-ms/oc-ms-specification.md
oc-ms/oc-ms.oas.yaml (pending)
oc-ms/oc-ms-lifecycle-state.puml
oc-ms/oc-ms-lifecycle-state.svg
osb-ms/osb-ms-specification.md
osb-ms/osb-ms.oas.yaml (pending)
ow-ms/ow_ms_specification.md
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
