# Intent Enabler E2E Solution Brief

## 1. Document status:

| Field | Value |
|---|---|
| Document status | Intent Architecture 3.6 baseline-aligned E2E solution brief. |
| Source of truth | GitHub `intent-3.6-baseline/baseline/intent`. |
| Baseline tag | `intent-3.6-baseline`. |
| Scope | End-to-end Intent Enabler solution view, cross-service flow, security, quality attributes, appendices, and artefact index. |
| Change note | Aligns E2E metadata with the `intent-3.6-baseline` tag. |

## 2. Table of contents:

- [1. Document status:](#1-document-status)
- [2. Table of contents:](#2-table-of-contents)
- [3. Business context:](#3-business-context)
- [4. Solution summary:](#4-solution-summary)
- [5. Solution elaboration:](#5-solution-elaboration)
- [6. Use case view:](#6-use-case-view)
- [6.1. Define intent capability:](#61-define-intent-capability)
- [6.2. Activate intent capability:](#62-activate-intent-capability)
- [6.3. Create runtime intent:](#63-create-runtime-intent)
- [6.4. Interpret and resolve intent:](#64-interpret-and-resolve-intent)
- [6.5. Optimisation-backed selection:](#65-optimisation-backed-selection)
- [6.6. Prepare service-ready configuration:](#66-prepare-service-ready-configuration)
- [6.7. Ingest external apply callback:](#67-ingest-external-apply-callback)
- [6.8. Assure runtime intent:](#68-assure-runtime-intent)
- [6.9. Project external lifecycle and report:](#69-project-external-lifecycle-and-report)
- [6.10. Terminate runtime intent:](#610-terminate-runtime-intent)
- [6.11. Handle failed or degraded runtime state:](#611-handle-failed-or-degraded-runtime-state)
- [7. Logical view:](#7-logical-view)
- [8. Event delivery model:](#8-event-delivery-model)
- [9. Process view:](#9-process-view)
- [9.1. Definition-time process:](#91-definition-time-process)
- [9.2. Runtime intent process:](#92-runtime-intent-process)
- [10. Discover intent capability:](#10-discover-intent-capability)
- [11. Create intent specification:](#11-create-intent-specification)
- [12. Activate intent specification:](#12-activate-intent-specification)
- [13. Create and execute runtime intent:](#13-create-and-execute-runtime-intent)
- [14. Monitor runtime intent:](#14-monitor-runtime-intent)
- [15. Cancel and terminate runtime intent:](#15-cancel-and-terminate-runtime-intent)
- [16. Pause and resume runtime intent:](#16-pause-and-resume-runtime-intent)
- [17. Retry failed runtime intent:](#17-retry-failed-runtime-intent)
- [18. Callback ingestion:](#18-callback-ingestion)
- [19. Capability matrix:](#19-capability-matrix)
- [20. Solution security:](#20-solution-security)
- [21. User authentication and access governance:](#21-user-authentication-and-access-governance)
- [22. OEX internal access path:](#22-oex-internal-access-path)
- [23. OEX to intent backend access:](#23-oex-to-intent-backend-access)
- [24. NGW to ID MS, IC MS, and ICB MS security:](#24-ngw-to-id-ms-ic-ms-and-icb-ms-security)
- [25. Service-to-service security:](#25-service-to-service-security)
- [26. Kafka security:](#26-kafka-security)
- [27. API concurrency control:](#27-api-concurrency-control)
- [28. Event security and integrity:](#28-event-security-and-integrity)
- [29. Sensitive information boundary:](#29-sensitive-information-boundary)
- [30. Infrastructure security controls across solution briefs:](#30-infrastructure-security-controls-across-solution-briefs)
- [31. Important quality attributes:](#31-important-quality-attributes)
- [31.1. Availability:](#311-availability)
- [31.2. Scalability:](#312-scalability)
- [31.3. Performance:](#313-performance)
- [31.4. Reliability:](#314-reliability)
- [31.5. Maintainability:](#315-maintainability)
- [32. Risks:](#32-risks)
- [33. Assumptions:](#33-assumptions)
- [34. Constraints:](#34-constraints)
- [35. Appendix:](#35-appendix)
- [35.1. ID MS endpoint summary:](#351-id-ms-endpoint-summary)
- [35.2. IC MS endpoint summary:](#352-ic-ms-endpoint-summary)
- [35.3. ICB MS endpoint summary:](#353-icb-ms-endpoint-summary)
- [35.4. Runtime lifecycle states:](#354-runtime-lifecycle-states)
- [35.5. Kafka topics:](#355-kafka-topics)
- [35.6. External webhook notification delivery:](#356-external-webhook-notification-delivery)
- [35.7. Event types:](#357-event-types)
- [35.8. Worker instructions:](#358-worker-instructions)
- [35.9. IntentAssuranceEvent lifecycle mapping:](#359-intentassuranceevent-lifecycle-mapping)
- [35.10. Key artifacts:](#3510-key-artifacts)
- [35.11. Canonical runtime expression shape:](#3511-canonical-runtime-expression-shape)
- [35.12. IntentSpecification lifecycle baseline:](#3512-intentspecification-lifecycle-baseline)
- [35.13. Runtime Intent lifecycle baseline:](#3513-runtime-intent-lifecycle-baseline)
- [35.14. Internal event baseline:](#3514-internal-event-baseline)

## 3. Business context:

The Intent Enabler provides a governed, TMF-aligned way for authorised consumers to express desired service outcomes as runtime intents, rather than directly issuing low-level network configuration commands. The platform separates definition-time intent specification governance from runtime intent admission, semantic interpretation, service-ready preparation, callback ingestion, assurance, and external status projection.

The business objective is to support reliable outcome-driven service lifecycle management for high-value services such as hospital surgical connectivity. Consumers express intent goals, constraints, and preferences using governed `IntentSpecification` contracts. The platform validates the request, interprets it with Knowledge Plane context, prepares service configuration, ingests network and apply callbacks, evaluates runtime assurance, and projects a curated external lifecycle and report view.

The E2E design deliberately keeps service boundaries narrow:

- Intent Definition MS owns definition-time `IntentSpecification` resources.
- Intent Controller MS owns external runtime `Intent` and `IntentReport` resources.
- Intent Intelligence MS owns semantic interpretation and service-ready preparation.
- Intent Assurance MS owns runtime assurance truth and lifecycle-driving assurance outcomes.
- Intent Callback MS owns thin callback ingestion and raw callback event relay.

## 4. Solution summary:

The Intent Enabler is a multi-microservice solution built around external TMF-compliant APIs, internal event-driven workflow, durable persistence, outbox-backed publication, and clear responsibility boundaries. At a high level:

1. ID MS publishes and governs active `IntentSpecification` contracts.
2. IC MS admits runtime `Intent` requests that are syntactically valid and reference an active specification.
3. IC MS emits `IntentValidatedEvent` after admission.
4. II MS consumes the admitted intent, performs semantic and policy interpretation, and either rejects, resolves, or prepares network-ready service configuration.
5. II MS emits `IntentRejectedEvent`, `IntentResolvedEvent`, or `IntentNetworkReadyEvent` according to the workflow milestone.
6. Where optimisation-backed selection is required, II MS submits `POST /optimisation` using the optimisation API outbox and supplies the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, as the optimiser outcome callback target.
7. ICB MS receives external callback submissions from trusted change-execution and apply systems and approved Optimiser platforms, validates only structure, persists the callback, and publishes either raw `IntentCallbackEvent` or approved `OptimisationStatusChangeEvent` relay events.
8. IA MS consumes `IntentNetworkReadyEvent`, `IntentCallbackEvent`, and runtime observation facts, then emits `IntentAssuranceEvent`.
9. IC MS consumes curated downstream outcomes and updates the external `Intent` and `IntentReport` projection.

The design keeps external resources stable and controlled while allowing internal services to evolve independently through event contracts.

## 5. Solution elaboration:

The solution is split into definition-time and runtime concerns.

Definition-time concern:

- ID MS owns the `IntentSpecification` catalogue, lifecycle, version family, schema references, subscription model, and external specification events.
- An `IntentSpecification` defines the syntax contract that a runtime intent must follow.
- Only `ACTIVE` specifications may be used for new runtime intent creation.
- `DRAFT` specifications are editable; `ACTIVE` and `RETIRED` specifications are immutable for material contract changes.

Runtime concern:

- IC MS exposes runtime `Intent` and `IntentReport` APIs.
- Runtime intent creation is accepted only after basic TMF resource validation, active `IntentSpecification.id` reference validation, mandatory `expression.iri` validation, and expression-shape validation.
- II MS performs semantic interpretation and Knowledge Plane-backed capability validation.
- IA MS owns runtime assurance truth after service-ready configuration, callbacks, and observation metrics are available.
- ICB MS is a narrow ingestion adapter for external source callbacks.

The canonical runtime semantic model uses the same buckets through the pipeline:

```json
{
  "expression": {
    "context": {
      "targets": {},
      "constraints": {},
      "preferences": {}
    }
  }
}
```

`targets` are measurable goals, `constraints` are hard requirements, and `preferences` are soft selection guidance. This structure should remain consistent across ID MS, IC MS, II MS, IA MS, and future control-loop extensions.

## 6. Use case view:

![view](intent_platform_usecase.svg)

### 6.1. Define intent capability:

An authorised specification owner creates a new mutable `IntentSpecification` DRAFT candidate in ID MS. `specKey` resolves the stable server-assigned `IntentSpecification.id`; `draftId` selects the mutable DRAFT candidate; official `version` is assigned only on activation. The specification defines the governed expression contract, schema references, lifecycle metadata, related parties, and version identity.

### 6.2. Activate intent capability:

An authorised governance actor promotes a draft specification version to `ACTIVE` through a lifecycle update. Activation retires the previously active version with the same `specKey` and makes the new version available for creating new runtime intents.

### 6.3. Create runtime intent:

An external consumer or OEX submits a runtime `Intent` to IC MS. External consumers use `submit`, not `lifecycleStatus`, to request Draft save versus admission. IC MS validates syntax, confirms the submitted request carries both an active `IntentSpecification.id` and mandatory `expression.iri`, defaults omitted `isBundle` to `false`, persists the admitted intent, projects `Acknowledged`, and emits `IntentValidatedEvent`.

### 6.4. Interpret and resolve intent:

II MS consumes `IntentValidatedEvent`, interprets the admitted expression, resolves semantic context through Knowledge Plane data, validates policy, capability, and resource feasibility, and emits either `IntentRejectedEvent` or `IntentResolvedEvent`.

### 6.5. Optimisation-backed selection:

Where optimisation-backed selection is required, II MS submits `POST /optimisation` with the resolved candidate set and supplies the ICB-owned callback submission URL, `POST /intent-callback/v1/submissions`, to the Optimiser platform. The Optimiser submits `OptimisationStatusChangeEventRequest` to ICB MS. ICB MS structurally validates and relays the approved `OptimisationStatusChangeEvent` payload to `t7.intent.management.events` for II MS. II MS correlates the optimiser outcome and packages the selected configuration into `IntentNetworkReadyEvent`.

### 6.6. Prepare service-ready configuration:

II MS prepares service configuration for change-execution and apply and assurance observation. It emits `IntentNetworkReadyEvent` with `serviceConfiguration.orchestratorConfiguration` and `serviceConfiguration.observerConfiguration`. This event means configuration is ready for change execution and observation; it does not mean the network apply succeeded.

### 6.7. Ingest external apply callback:

An external change-execution and apply system submits a callback to ICB MS. ICB MS validates only technical and structural properties, stores the callback, and publishes a raw `IntentCallbackEvent` to the dedicated callback topic.

### 6.8. Assure runtime intent:

IA MS consumes service-ready configuration, callback facts, and runtime observation metrics. It maps raw `sourceState.state` values, evaluates metrics against the resolved targets and stored assurance baseline, and emits `IntentAssuranceEvent`.

### 6.9. Project external lifecycle and report:

IC MS consumes downstream outcome events and updates external `Intent.lifecycleStatus`, `statusReason`, and `IntentReport` projection. External consumers see a curated TMF-compliant view, not raw internal workflow detail.

### 6.10. Terminate runtime intent:

A consumer requests `DELETE /intentManagement/v5/intent/{id}`. IC MS treats this as runtime termination, not physical deletion. The runtime record is retained for audit, lifecycle history, and reporting.

### 6.11. Handle failed or degraded runtime state:

IA MS may emit `IntentAssuranceEvent` with lifecycle outcomes such as `Degraded` or `Failed`. IC MS projects the external status. Any re-interpretation, re-optimisation, rollback, or recovery decision remains a separate authorised workflow and is not hidden inside IA or ICB. `Paused` is handled through the separate IC MS-governed pause and resume lifecycle path and must be explicitly resumed or redirected before retry-style workflow continues.

## 7. Logical view:

![view](intent_enabler_logical_view.svg)

Optimisation-backed selection uses the same callback ingress boundary: II MS calls `POST /optimisation`, the Optimiser calls `POST /intent-callback/v1/submissions`, ICB MS publishes `OptimisationStatusChangeEvent` to the main internal event topic, and II MS consumes it before emitting `IntentNetworkReadyEvent`.

Logical resource ownership:

| Resource or concept | Owner |
|---|---|
| `IntentSpecification` | ID MS |
| Event subscriptions for `IntentSpecification` event notifications | ID MS |
| Runtime `Intent` | IC MS |
| Runtime `IntentReport` | IC MS |
| Semantic resolution state | II MS |
| Service-ready configuration | II MS |
| Raw callback submission | ICB MS |
| Runtime assurance truth | IA MS |
| External runtime lifecycle projection | IC MS |

## 8. Event delivery model:

The Intent Enabler uses three distinct delivery models. They must not be collapsed into a single Kafka-only model.

| Delivery path | Used for | Mechanism | Transport metadata |
|---|---|---|---|
| Internal platform events | Internal workflow facts such as `IntentValidatedEvent`, `IntentRejectedEvent`, `IntentResolvedEvent`, `OptimisationStatusChangeEvent`, `IntentNetworkReadyEvent`, `IntentCallbackEvent`, and `IntentAssuranceEvent` | Service-owned internal event outbox, relay, Kafka topic, idempotent internal consumers | CloudEvents-style Kafka and platform headers |
| External hub notifications | Subscriber notifications for `IntentSpecification`, `Intent`, and `IntentReport` resource events | Service-owned webhook delivery outbox, HTTP retry relay, HTTP `POST` to subscriber listener callback URL | HTTP headers such as `Content-Type`, `X-Correlation-Id`, and subscriber callback authentication where configured |
| Callback ingestion | Source, change-execution, and optimiser outcome callback submission into the platform | REST `POST` to ICB MS, callback persistence, callback outbox, internal Kafka publication to IA MS or II MS depending on callback profile | HTTP headers on inbound callback; CloudEvents-style Kafka and platform headers on `IntentCallbackEvent` or `OptimisationStatusChangeEvent` |

The callback ingestion path has two approved profiles. Change-execution and apply callbacks are relayed as `IntentCallbackEvent` on the dedicated callback topic `t7.intent.management.events.callbacks` for IA MS. Optimiser outcome callbacks are relayed as `OptimisationStatusChangeEvent` on the main internal event topic `t7.intent.management.events` for II MS. ID MS and IC MS hub notifications are REST webhook callbacks with TMF-aligned event payloads. Kafka is not used for external hub notification delivery.

Subscriber callback URLs are subscriber-owned; the platform defines the subscription API, delivery rules, retry behaviour, and TMF-aligned notification payload shape.

## 9. Process view:

### 9.1. Definition-time process:

```text
1. Authorised actor creates a mutable DRAFT IntentSpecification candidate in ID MS using `POST /intentSpecification` with mandatory `specKey`.
2. ID MS resolves the server-assigned `IntentSpecification.id` from `specKey`, assigns a new `draftId`, validates definition-time resource shape and schema references, and persists the DRAFT candidate.
3. ID MS emits `IntentSpecificationCreateEvent` for the created DRAFT candidate where external notification is enabled.
4. Authorised actor updates the selected DRAFT candidate using `PUT /intentSpecification/draft/{draftId}` or controlled `PATCH /intentSpecification/draft/{draftId}`.
5. Authorised actor promotes the selected DRAFT candidate to ACTIVE through `PATCH /intentSpecification/draft/{draftId}` or finalising `PUT /intentSpecification/draft/{draftId}`.
6. ID MS assigns the official version during activation, carries forward `draftId` as provenance, and retires the previous ACTIVE version for the same resolved `id`.
7. ID MS emits `IntentSpecificationStatusChangeEvent` for activation and retirement.
8. IC MS and other authorised consumers use only the ACTIVE official specification selected by concrete `intentSpecification.id` for runtime validation.
```

### 9.2. Runtime intent process:

```text
1. Consumer submits runtime Intent to IC MS.
2. IC MS validates TMF shape and active IntentSpecification reference.
3. IC MS persists the admitted Intent and projects Acknowledged.
4. IC MS emits IntentValidatedEvent.
5. II MS consumes IntentValidatedEvent.
6. II MS performs semantic, policy, capability, and resource-context validation.
7. II MS emits IntentRejectedEvent if rejected.
8. II MS emits IntentResolvedEvent when candidate-level resolution is complete.
9. Where optimisation-backed selection is required, II MS submits POST /optimisation and supplies POST /intent-callback/v1/submissions as the optimiser callback URL.
10. Optimiser submits OptimisationStatusChangeEventRequest to ICB MS.
11. ICB MS persists the optimiser callback and emits OptimisationStatusChangeEvent to the main internal event topic for II MS.
12. II MS consumes OptimisationStatusChangeEvent, correlates it to the submitted optimisation request, and emits IntentNetworkReadyEvent when service configuration is ready for application and observation.
13. External change-execution and apply system submits a callback to ICB MS.
14. ICB MS persists the apply callback and emits IntentCallbackEvent to the dedicated callback topic.
15. IA MS consumes IntentNetworkReadyEvent, IntentCallbackEvent, and observation metrics.
16. IA MS emits IntentAssuranceEvent.
17. IC MS updates external Intent and IntentReport projection.
18. At any point after admission, IC MS may place the runtime intent into Paused through an authorised lifecycle operation or platform policy action; resume, retry, recovery, or termination then follows the governed IC MS lifecycle rules.
```

## 10. Discover intent capability:

External consumers and OEX discover supported intent capabilities by reading `IntentSpecification` resources from ID MS. The default list response should remain lightweight. Full specification details, including `specCharacteristic`, `expressionSpecification`, and `targetEntitySchema`, are retrieved from the single-resource endpoint or requested through `fields` where supported. Only `ACTIVE` official specification versions are valid for creating new runtime intents.

`DRAFT` candidates are for governance and editing, selected by `draftId`, and have no official public version until activation. `RETIRED` official versions are retained for audit and history and existing references, but are not used for new runtime creation.

## 11. Create intent specification:

ID MS exposes:

```http
POST /intentManagement/v5/intentSpecification
```

Successful creation normally returns `201 Created`, a server-generated `id`, `href`, `Location`, `ETag`, and lifecycle-aware links. Created specifications normally start in `DRAFT`. ID MS does not accept caller-supplied server-generated fields such as `id`, `href`, `Location`, `ETag`, or `_links` on create.

## 12. Activate intent specification:

Activation is a lifecycle update on the selected DRAFT candidate addressed by `draftId`. The platform must not expose a custom activation action, such as:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate
```

Draft candidate updates use `PUT /intentManagement/v5/intentSpecification/draft/{draftId}` for deterministic full replacement, with controlled `PATCH /intentManagement/v5/intentSpecification/draft/{draftId}` retained for small targeted updates. Unsafe state-changing operations require `If-Match`.

`PATCH` uses JSON Merge Patch semantics and full PATCH request examples must use `Content-Type: application/merge-patch+json`.

Activation rules:

- Only `DRAFT` can become `ACTIVE`.
- The previous active version in the same `specKey` becomes `RETIRED`.
- New runtime intent creation uses the newly active version.
- Existing runtime intents referencing retired versions may continue where safe.
- Activation emits status-change events for both the activated version and the retired previous active version.

## 13. Create and execute runtime intent:

Runtime intent creation is owned by IC MS:

```http
POST /intentManagement/v5/intent
```

IC MS validates:

- request resource shape;
- required fields;
- that external consumers have not supplied `lifecycleStatus`;
- optional `isBundle`, defaulting it to `false` when omitted on create;
- reference to a concrete active `IntentSpecification.id`;
- mandatory `expression.iri` matching the selected specification's expression contract;
- runtime expression shape against the active specification contract;
- basic external authorisation context passed by the gateway/security layer.

IC MS does not validate semantic feasibility, network topology, resource suitability, or assurance success. After successful admission, IC MS persists the intent with the server-resolved `isBundle` value, sets the projected lifecycle to `Acknowledged`, and emits `IntentValidatedEvent`. II MS then performs semantic interpretation and service-ready preparation. Where an optimiser component is used, `IntentResolvedEvent` can hand off a full candidate set to the optimisation path.

II MS submits `POST /optimisation` through its optimisation API outbox, supplies the ICB callback URL, and consumes ICB-relayed `OptimisationStatusChangeEvent` before producing `IntentNetworkReadyEvent`.

## 14. Monitor runtime intent:

Monitoring is split across IA MS and IC MS.

IA MS owns the internal assurance truth:

- consumes `IntentNetworkReadyEvent`;
- stores selected apply resources and observer scope;
- consumes raw `IntentCallbackEvent` from ICB MS;
- obtains runtime metric facts from observability endpoints;
- evaluates resource metrics against targets and stored assurance baseline;
- emits `IntentAssuranceEvent`.

IC MS owns the external projection:

- updates runtime `Intent.lifecycleStatus`;
- updates `statusReason`;
- creates or updates `IntentReport` projection;
- emits external `Intent` events and `IntentReport` events where applicable.

IA MS must not expose raw telemetry dumps, raw callback payloads, or internal mapping details as the external customer-facing API.

## 15. Cancel and terminate runtime intent:

The runtime termination operation is represented externally as:

```http
DELETE /intentManagement/v5/intent/{id}
```

This is a termination request, not physical deletion of the runtime record. IC MS retains the intent for audit, traceability, reporting, and lifecycle history. Termination must follow the same security, authorisation, and concurrency expectations as other unsafe operations. If optimistic concurrency is required for the operation, a missing `If-Match` returns `428 Precondition Required`, and stale or mismatched `If-Match` returns `412 Precondition Failed`.

## 16. Pause and resume runtime intent:

`Paused` is a governed runtime state where the policy remains known but active downstream progression is intentionally suspended. Entry into `Paused` is owned by IC MS through an authorised runtime lifecycle operation or platform policy action; II MS, IA MS, and ICB MS must not independently place an intent into `Paused`. While paused, new semantic interpretation, optimisation, apply, or recovery work should not start unless an authorised resume or recovery workflow explicitly permits it.

Exit from `Paused` returns the runtime intent to an authorised workflow path such as re-evaluation, recovery, termination, or continued monitoring according to IC MS lifecycle rules.

## 17. Retry failed runtime intent:

A failed, degraded, or paused runtime intent does not automatically imply retry, rollback, reselection, or re-optimisation. IA MS reports assurance truth. IC MS projects it externally. `Paused` requires an authorised resume or recovery decision before retry-style workflow continues.

A retry or recovery action should be initiated by an authorised workflow that can evaluate:

- current lifecycle state;
- latest assurance metrics;
- original targets, constraints, and preferences;
- whether the referenced `IntentSpecification` version remains usable for the runtime context;
- whether a new runtime version is required;
- whether a new semantic interpretation or optimisation run is required.

Retry behaviour must remain explicit and auditable. It should not be hidden in ICB MS callback ingestion or IA MS raw-state mapping.

## 18. Callback ingestion:

ICB MS exposes:

```http
POST /intent-callback/v1/submissions
```

The same protected ingress endpoint accepts two approved request profiles: `IntentCallbackEventRequest` for change-execution and apply callbacks and `OptimisationStatusChangeEventRequest` for approved optimiser outcome callbacks. ICB MS sits behind the API Gateway. It accepts callback submissions from trusted external change-execution and apply systems and approved Optimiser platforms.

It validates only technical and structural properties, such as required fields, non-empty strings, ISO timestamp format, request size, trusted caller/source authorisation, and idempotency, where required. ICB MS does not validate that `intentId` exists. IA MS owns intent correlation and unknown-intent handling after consuming `IntentCallbackEvent`.

For change-execution and apply callbacks, the REST request uses `@type: IntentCallbackEventRequest` and the internal relay event is `IntentCallbackEvent`.

Canonical change-execution callback fields:

| Field | Purpose |
|---|---|
| `intentId` | Runtime intent identifier, syntax-only in ICB. |
| `callbackSource` | External source and change-execution identifier. |
| `callbackTimestamp` | Source-reported callback time. |
| `sourceState.state` | Raw source-owned state to be interpreted by IA MS. |
| `sourceState.reason` | Optional raw source reason. |
| `sourceReference` | Optional external source reference. |
| `details` | Safe structured callback detail, subject to policy and size limits. |

For optimiser outcome callbacks, the REST request uses `@type: OptimisationStatusChangeEventRequest` and the internal relay event is `OptimisationStatusChangeEvent`. ICB MS relays the approved optimiser payload shape to `t7.intent.management.events` for II MS and does not interpret optimiser status, selected configuration, feasibility, or service meaning.

Legacy callback state, source, and timestamp fields and `callbackType` must not be used as active ICB contract fields.

## 19. Capability matrix:

| Capability | ID MS | IC MS | II MS | IA MS | ICB MS |
|---|---:|---:|---:|---:|---:|
| Manage `IntentSpecification` | Yes | No | No | No | No |
| Manage specification lifecycle/version family | Yes | No | No | No | No |
| Expose runtime `Intent` API | No | Yes | No | No | No |
| Expose runtime `IntentReport` API | No | Yes | No | No | No |
| Admit syntactically valid runtime intents | No | Yes | No | No | No |
| Emit `IntentValidatedEvent` | No | Yes | No | No | No |
| Semantic interpretation | No | No | Yes | No | No |
| Knowledge Plane-backed validation | No | No | Yes | No | No |
| Candidate resource resolution | No | No | Yes | No | No |
| Service-ready configuration | No | No | Yes | No | No |
| Runtime assurance truth | No | No | No | Yes | No |
| Runtime callback ingestion | No | No | No | No | Yes |
| Raw callback interpretation | No | No | No | Yes | No |
| External lifecycle projection | No | Yes | No | No | No |
| Internal Kafka event publication | No | Yes | Yes | Yes | Yes |
| External webhook notification delivery | Yes | Yes | No | No | No |
| Callback ingestion and raw callback relay | No | No | No | No | Yes |
| Outbox-backed delivery and publication | Yes | Yes | Yes | Yes | Yes |

## 20. Solution security:

Security is enforced across the gateway, service, data, and event layers. External-facing services must not rely only on gateway authentication. Each owning service must enforce resource-level, lifecycle-level, and operation-level rules for the resources it owns.

## 21. User authentication and access governance:

External users and client systems authenticate through the OEX, gateway, and platform access layer. The external access layer is responsible for user authentication, tenant/customer context, consent and delegation controls where applicable, and coarse-grained access governance. Downstream services should receive only the trusted platform identity and context required for their responsibility. Internal services must not accept caller-supplied trust claims directly from the public internet.

## 22. OEX internal access path:

OEX or other authorised experience layers call the Intent Enabler through the platform gateway path. The gateway validates access, normalises trusted headers and context, applies edge controls, and routes requests to the appropriate domain service. OEX should not call internal event-driven services directly. II MS and IA MS have no public TMF-compliant REST API in the active baseline.

## 23. OEX to intent backend access:

External runtime and definition-time API access is limited to the services that own external resource boundaries:

- ID MS for `IntentSpecification` and specification hub subscriptions.
- IC MS for runtime `Intent`, `IntentReport`, and runtime intent hub subscriptions.
- ICB MS only for trusted external change-execution and apply callback submission and approved Optimiser outcome callback submission through its callback API.

II MS and IA MS remain internal-only microservices.

## 24. NGW to ID MS, IC MS, and ICB MS security:

The network gateway or API gateway authenticates callers, enforces coarse-grained access, and forwards trusted context. ID MS, IC MS, and ICB MS still enforce their own operation-specific rules:

- ID MS validates specification governance permissions and lifecycle constraints.
- IC MS validates runtime intent permissions, resource ownership, lifecycle rules, and concurrency.
- ICB MS validates source and integration authorisation for callback submission.

## 25. Service-to-service security:

Internal service-to-service calls and event producers and consumers should use service identity, mTLS where applicable, least-privilege credentials, and topic and API-level ACLs. Service-to-service authorisation is based on system/service identity and allowed operation, not arbitrary end-user claims. User-context-related authorisation should be resolved before crossing into internal service-to-service paths unless a specific audited delegation model is introduced.

## 26. Kafka security:

Kafka security expectations:

- authenticate producers and consumers;
- authorise topic-level produce and consume rights;
- restrict callback topic consumption to IA MS and operational support roles;
- encrypt traffic in transit;
- avoid secrets, tokens, credentials, and raw stack traces in payloads;
- use schema compatibility and additive evolution rules;
- enforce idempotent consumer behaviour for at-least-once delivery.

## 27. API concurrency control:

Unsafe operations that require optimistic concurrency must use `If-Match` with the current `ETag`.

Baseline error behaviour:

| Scenario | HTTP status | Reason |
|---|---:|---|
| Required `If-Match` missing | `428 Precondition Required` | `IF_MATCH_REQUIRED` |
| `If-Match` stale or mismatched | `412 Precondition Failed` | `ETAG_MISMATCH` |

This applies consistently to governed specification updates and deletes, runtime intent unsafe updates/termination where required, and hub subscription delete where the owning API requires concurrency protection.

## 28. Event security and integrity:

Internal events are facts, not commands. Producers emit events only after durable state changes or accepted raw facts. Consumers must deduplicate and process idempotently.

Event security rules:

- use stable event names exactly as baselined;
- use CloudEvents-style transport metadata for internal Kafka events;
- use a top-level JSON `body` payload for internal Kafka events unless a specific approved event shape defines otherwise, such as `OptimisationStatusChangeEvent`;
- propagate `correlationId`;
- prefer `intentId` as Kafka key for intent-scoped internal events;
- do not directly expose internal Kafka event payloads as external TMF-aligned webhook notification payloads;
- use HTTP headers and subscriber listener authentication where configured for external webhook notification delivery;
- do not include secrets, credentials, tokens, raw telemetry dumps, raw stack traces, or internal solver and KP details unless explicitly governed for an internal-only topic.

## 29. Sensitive information boundary:

External APIs and events must expose curated resource state only. They must not expose:

- internal KP configuration internals;
- optimiser scoring or solver internals;
- raw callback payloads;
- raw telemetry dumps;
- internal stack traces;
- secrets, credentials, tokens, or private infrastructure identifiers;
- source-system trust claims not intended for consumers.

IC MS and ID MS external events are resource events. They must not leak internal workflow, resource-candidate scoring, assurance internals, callback payloads, or telemetry detail.

## 30. Infrastructure security controls across solution briefs:

Expected platform controls include:

- API gateway authentication and route authorisation;
- mTLS or equivalent authenticated service-to-service transport;
- service account least privilege;
- secret management outside application payloads;
- database encryption at rest;
- Kafka TLS and ACLs;
- audit logging for state-changing operations;
- structured logs without sensitive payload leakage;
- operational alerting for outbox lag, dead-letter growth, DB failures, and event publication failures;
- environment separation and configuration promotion controls.

## 31. Important quality attributes:

### 31.1. Availability:

- External APIs must fail safely when their owned persistence path is unavailable.
- Outbox patterns decouple API acceptance from event publication where appropriate.
- ICB MS must not accept a callback unless the callback and outbox record are durably committed.
- Kafka unavailability after durable acceptance should be handled through retrying outbox relay.
- Webhook delivery failures after durable acceptance should be handled through retrying webhook delivery relay.
- Consumers must tolerate duplicate events and replay.

### 31.2. Scalability:

- IC MS, II MS, IA MS, and ICB MS should scale horizontally behind idempotent processing and partition-aware Kafka consumption.
- Kafka keys should prefer `intentId` for intent-scoped ordering.
- Outbox relays should process deterministic batches and support safe clustered coordination.
- Webhook delivery relays should support retry, backoff, and isolation of failing subscriber callbacks.
- List APIs should support pagination and lightweight default response shapes.

### 31.3. Performance:

- Runtime intent admission should perform only syntactic and active-specification validation, not deep semantic or assurance processing.
- Semantic interpretation and assurance are asynchronous through events.
- ID MS GET operations may use bounded private caching and support explicit fresh retrieval.
- IA MS metric evaluation should avoid exposing raw telemetry volume through external APIs.

### 31.4. Reliability:

- State changes and event publication must be retry-safe.
- Consumers must be idempotent under at-least-once delivery.
- Unknown callback intent correlation belongs to IA MS, not ICB MS.
- Event publication should be based on committed state, not in-memory side effects.

### 31.5. Maintainability:

- Specifications, design briefs, and solution briefs must remain aligned but distinct.
- External TMF resource boundaries should remain stable.
- Internal event contracts should evolve additively where possible.
- Stale terms such as `priority_level`, `trafficClass`, `callbackType`, and legacy callback source, timestamp, and state fields should not be reintroduced.

## 32. Risks:

| Risk | Impact | Mitigation |
|---|---|---|
| Boundary drift between IC, II, IA, and ICB | Services duplicate or contradict each other | Keep ownership matrix and event catalogue as baseline governance artefacts. |
| External events leaking internal details | Security and contract instability | Keep external events resource-scoped and curated. |
| Callback state misinterpreted at ingestion | Incorrect lifecycle projection | ICB remains raw ingestion only; IA owns mapping. |
| `IntentNetworkReadyEvent` misunderstood as apply success | Premature external `Active` projection | Document that apply success requires callback or observation evidence. |
| Specification lifecycle and version mistakes | Runtime intents created against wrong contract | Enforce one active version per `specKey` and active-only runtime creation. |
| Kafka duplicate delivery | Duplicate lifecycle and report updates | Idempotent consumers and stable deduplication keys. |
| Webhook delivery retry duplication | Duplicate subscriber notifications | Use event identifiers, idempotent subscriber listener handling, and delivery retry tracking. |
| Long-lived stale docs | Implementation drift | Use GitHub `intent-3.6-baseline/baseline/intent` as source of truth and update solution briefs after baseline changes. |

## 33. Assumptions:

- GitHub `intent-3.6-baseline/baseline/intent` is the source of truth for the Intent Architecture 3.6 baseline.
- ID MS and IC MS expose the external TMF-compliant resource APIs.
- ID MS and IC MS deliver external hub notifications by HTTP POST to subscriber listener callback URLs using TMF-aligned event payloads.
- II MS and IA MS are internal-only event-driven services.
- ICB MS is externally reachable only through the API Gateway for trusted callback sources.
- Managed PostgreSQL or PostgreSQL-compatible storage is suitable for owned service persistence and outbox tables.
- Kafka or equivalent event backbone is available for internal event distribution.
- Observability endpoints provide metric facts required by IA MS.
- Optimiser participation is allowed where configured, but the Intent Enabler boundary remains valid without exposing optimiser internals externally.

## 34. Constraints:

- TMF-compliant resource responsibility boundaries must remain intact.
- `IntentSpecification` lifecycle states are `DRAFT`, `ACTIVE`, and `RETIRED`.
- Runtime intent lifecycle states are `Acknowledged`, `InProgress`, `Active`, `Degraded`, `Paused`, `Rejected`, `Failed`, and `Terminated`.
- `IntentNetworkReadyEvent` must not be treated as network apply success.
- ICB MS must not validate `intentId` existence or map callback lifecycle meaning.
- External events must not expose internal KP, optimiser, telemetry, callback, or candidate-scoring details.
- External hub notifications must use subscriber-owned callback URLs and TMF-aligned event payloads; Kafka is not used for external hub notification delivery.

## 35. Appendix:

### 35.1. ID MS endpoint summary:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create specification | `POST` | `/intentManagement/v5/intentSpecification` |
| List specifications | `GET` | `/intentManagement/v5/intentSpecification` |
| Retrieve specification | `GET` | `/intentManagement/v5/intentSpecification/{id}` |
| Full replace draft specification candidate | `PUT` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Partial update draft specification candidate | `PATCH` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Delete draft specification candidate | `DELETE` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Create specification event subscription | `POST` | `/intentManagement/v5/intentSpecification/hub` |
| Retrieve specification subscription | `GET` | `/intentManagement/v5/intentSpecification/hub/{id}` |
| Delete specification subscription | `DELETE` | `/intentManagement/v5/intentSpecification/hub/{id}` |

### 35.2. IC MS endpoint summary:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create runtime intent | `POST` | `/intentManagement/v5/intent` |
| List runtime intents | `GET` | `/intentManagement/v5/intent` |
| Retrieve runtime intent | `GET` | `/intentManagement/v5/intent/{id}` |
| Full update runtime intent | `PUT` | `/intentManagement/v5/intent/{id}` |
| Partial update runtime intent | `PATCH` | `/intentManagement/v5/intent/{id}` |
| Terminate runtime intent | `DELETE` | `/intentManagement/v5/intent/{id}` |
| List intent reports | `GET` | `/intentManagement/v5/intent/{id}/intentReport` |
| Retrieve intent report | `GET` | `/intentManagement/v5/intent/{id}/intentReport/{reportId}` |
| Create runtime event subscription | `POST` | `/intentManagement/v5/hub` or domain-scoped runtime hub path where baselined |
| Delete runtime event subscription | `DELETE` | `/intentManagement/v5/hub/{id}` or domain-scoped runtime hub path where baselined |

### 35.3. ICB MS endpoint summary:

| Purpose | Method | Endpoint |
|---|---:|---|
| Submit callback | `POST` | `/intent-callback/v1/submissions` |
| Retrieve callback submission status | `GET` | `/intent-callback/v1/submissions/{id}` |

### 35.4. Runtime lifecycle states:

| State | Meaning |
|---|---|
| `Acknowledged` | IC MS admitted the request after syntactic validation. |
| `InProgress` | Downstream semantic, optimisation, service-ready, apply, or assurance workflow is underway. |
| `Active` | Service is applied, and assurance evidence supports the active state. |
| `Degraded` | Service is still present, but assurance evidence indicates degraded operation. |
| `Paused` | Policy exists but is intentionally paused; entry and exit are governed by IC MS lifecycle policy, not by IA or ICB interpretation. |
| `Rejected` | Request or later workflow outcome was rejected by semantic, policy, apply, or network decision. |
| `Failed` | Delivery or operation failed irrecoverably. |
| `Terminated` | Runtime intent has ended or been removed from active service state. |

### 35.5. Kafka topics:

| Topic | Purpose | Producer | Consumer |
|---|---|---|---|
| `t7.intent.management.events` | Core internal intent workflow events, including `OptimisationStatusChangeEvent` relay | IC MS, II MS, IA MS, ICB MS for optimiser outcome relay | IC MS, II MS, IA MS |
| `t7.intent.management.events.callbacks` | Raw accepted callback facts | ICB MS | IA MS |

Exact physical topic names other than the callback topic remain platform implementation details unless separately baselined. External hub notifications are not Kafka topics; they are delivered by HTTP POST to subscriber listener callback URLs through ID MS and IC MS webhook delivery outboxes.

### 35.6. External webhook notification delivery:

| Notification family | Owner | Delivery mechanism | Payload pattern |
|---|---|---|---|
| `IntentSpecification` event notifications | ID MS | HTTP POST to subscriber listener callback URL registered through `/intentSpecification/hub` | TMF-aligned event payload |
| `Intent` event notifications | IC MS | HTTP POST to subscriber listener callback URL registered through runtime hub subscription API | TMF-aligned event payload |
| `IntentReport` event notifications | IC MS | HTTP POST to subscriber listener callback URL registered through runtime hub subscription API | TMF-aligned event payload |

### 35.7. Event types:

External ID MS events:

```text
IntentSpecificationCreateEvent
IntentSpecificationAttributeValueChangeEvent
IntentSpecificationStatusChangeEvent
IntentSpecificationDeleteEvent
```

External IC MS events:

```text
IntentCreateEvent
IntentAttributeValueChangeEvent
IntentStatusChangeEvent
IntentDeleteEvent
IntentReportCreateEvent
IntentReportAttributeValueChangeEvent
IntentReportDeleteEvent
```

Internal events:

```text
IntentValidatedEvent
IntentRejectedEvent
IntentResolvedEvent
OptimisationStatusChangeEvent
IntentNetworkReadyEvent
IntentCallbackEvent
IntentAssuranceEvent
```

### 35.8. Worker instructions:

Outbox workers and event consumers should follow these rules:

- read committed outbox records only;
- publish in deterministic order where ordering matters;
- mark published only after broker acknowledgement for Kafka publication;
- leave failed publications retryable;
- use idempotent consumers;
- deduplicate by `ce-id`, callback id, event id, or another agreed stable identifier;
- propagate `correlationId`;
- do not perform semantic filtering in ICB relay workers;
- keep lifecycle mapping in IA MS, not ICB MS;
- keep external projection in IC MS, not IA MS;
- deliver external hub notifications by HTTP POST from the service-owned webhook delivery outbox, not by Kafka topic subscription.

### 35.9. IntentAssuranceEvent lifecycle mapping:

| IA outcome evidence | Typical projected lifecycle |
|---|---|
| Apply confirmed and metrics satisfy targets | `Active` |
| Apply confirmed but metrics breach target threshold | `Degraded` |
| Apply failed or unrecoverable assurance failure | `Failed` |
| Termination confirmed | `Terminated` |
| Source or observation indicates still progressing | `InProgress` |
| Rejection from semantic, policy, or apply workflow | `Rejected` |
| Authorised pause or resume governance decision | `Paused` is not normally projected from IA evidence; it is controlled by IC MS lifecycle policy. |

This table is conceptual. Concrete raw `sourceState.state` mapping belongs to IA MS configuration and audit.

### 35.10. Key artifacts:

| Artifact | Document heading | Purpose |
|---|---|---|
| `id_ms_solution_brief.md` | Intent Definition MS Solution Brief | ID MS implementation-oriented brief. |
| `ic_ms_solution_brief.md` | Intent Controller MS Solution Brief | IC MS implementation-oriented brief. |
| `ii_ms_solution_brief.md` | Intent Intelligence MS Solution Brief | II MS implementation-oriented brief. |
| `ia_ms_solution_brief.md` | Intent Assurance MS Solution Brief | IA MS implementation-oriented brief. |
| `icb_ms_solution_brief.md` | Intent Callback MS Solution Brief | ICB MS implementation-oriented brief. |
| `intent_internal_events_specification.md` | Intent Event Specification | Internal event contract baseline. |
| `id_ms_specification.md` | ID MS Specification | ID MS detailed external API specification. |
| `ic_ms_specification.md` | IC MS Specification | IC MS detailed external API specification. |
| `ii_ms_specification.md` | II MS internal specification | II MS internal specification. |
| `ia_ms_specification.md` | IA MS internal specification | IA MS internal specification. |
| `icb_ms_specification.md` | ICB MS Specification | ICB MS callback API and event specification. |

### 35.11. Canonical runtime expression shape:

External runtime intent expression:

```json
{
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://example.com/ontology/intent/v1",
    "expressionValue": {
      "@context": {
        "intent": "https://example.com/ontology/intent#"
      },
      "context": {
        "targets": {},
        "constraints": {},
        "preferences": {}
      }
    }
  }
}
```

Internal runtime event expression should preserve the same semantic grouping, normally without external TMF wrapper noise:

```json
{
  "body": {
    "expression": {
      "iri": "https://example.com/ontology/intent/v1",
      "context": {
        "targets": {},
        "constraints": {},
        "preferences": {}
      }
    }
  }
}
```

### 35.12. IntentSpecification lifecycle baseline:

```text
DRAFT -> ACTIVE -> RETIRED
```

Rules:

- `DRAFT` is editable and may be deleted if unused and policy allows.
- `ACTIVE` is immutable for material contract changes and usable for new runtime intent creation.
- `RETIRED` is retained for audit and history and existing references but not usable for new runtime intent creation.
- No `DELETED` lifecycle state exists.

### 35.13. Runtime Intent lifecycle baseline:

```text
Acknowledged
InProgress
Active
Degraded
Paused
Rejected
Failed
Terminated
```

### 35.14. Internal event baseline:

`IntentValidatedEvent` carries both `intentSpecification.id` and `expression.iri` as admitted facts from IC MS. II MS must not re-resolve the governing specification by IRI alone.

| Event | Producer | Primary consumer | Purpose |
|---|---|---|---|
| `IntentValidatedEvent` | `intent-controller-ms` | `intent-intelligence-ms` | Runtime intent passed IC MS admission validation. |
| `IntentRejectedEvent` | `intent-intelligence-ms` | `intent-controller-ms` | Semantic, policy, or capability rejection. |
| `IntentResolvedEvent` | `intent-intelligence-ms` | `optimiser-controller-ms` or approved optimisation path | Candidate-level semantic-resolution handoff. Optimiser may be an approved platform component reached through the optimiser integration path, not a public Intent Enabler API. |
| `OptimisationStatusChangeEvent` | `intent-callback-ms` | `intent-intelligence-ms` | Approved optimiser outcome callback relayed by ICB MS after durable callback ingestion. |
| `IntentNetworkReadyEvent` | `intent-intelligence-ms` | `intent-assurance-ms` | Service configuration ready for change execution and apply, and observation. |
| `IntentCallbackEvent` | `intent-callback-ms` | `intent-assurance-ms` | Raw accepted change-execution and apply callback fact for IA MS. |
| `IntentAssuranceEvent` | `intent-assurance-ms` | `intent-controller-ms` | Assurance, apply, and runtime outcome truth for external projection. |
