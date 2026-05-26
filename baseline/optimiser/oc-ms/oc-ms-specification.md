# Optimisation Controller MS Specification

**Document status:**

| **Field** | **Value** |
|---|---|
| **Status** | Baseline candidate |
| **Scope** | Optimisation Controller MS API, lifecycle, command, event, and runtime resource specification |
| **Source path** | `baseline/optimiser/oc-ms/oc-ms-specification.md` |
| **Source of truth** | GitHub `main` |
| **Last aligned** | 2026-05-26 |
| **Alignment scope** | Aligned with OD `specKey`, OC `creationContext`, `CANCELLATIONFAILED`, retrial, request-result cache, ETag-header baseline, OW MS ownership wording, and circuit-breaker response signalling. |

## Table of contents:

- [1. OC MS summary](#1-oc-ms-summary)
- [2. Ownership](#2-ownership)
- [3. Endpoint set](#3-endpoint-set)
- [4. Runtime Optimisation canonical fields](#4-runtime-optimisation-canonical-fields)
- [5. Runtime lifecycle](#5-runtime-lifecycle)
- [6. Lifecycle transitions](#6-lifecycle-transitions)
- [7. Result presence rules](#7-result-presence-rules)
- [8. HATEOAS by lifecycle](#8-hateoas-by-lifecycle)
- [9. External response header governance](#9-external-response-header-governance)
- [10. POST /optimisation](#10-post-optimisation)
- [11. OD specification lookup and cache posture](#11-od-specification-lookup-and-cache-posture)
- [12. OC MS validation boundary](#12-oc-ms-validation-boundary)
- [13. Internal event baseline](#13-internal-event-baseline)
- [14. GET /optimisation list](#14-get-optimisation-list)
- [15. GET /optimisation/{id}](#15-get-optimisation-id)
- [16. Cancellation and retrial](#16-cancellation-and-retrial)
- [17. Header/concurrency rules](#17-header-concurrency-rules)
- [18. Error handling boundary](#18-error-handling-boundary)
- [19. Outcome mapping](#19-outcome-mapping)

## 1. OC MS summary:

Optimisation-Controller-MS (OC MS) owns the runtime `Optimisation` resource. It is a generic optimisation controller, not an intent-only controller.

OC MS accepts runtime optimisation requests, validates the generic wrapper and the referenced OD MS request contract, persists the request, emits `OptimisationRequestedEvent`, and later projects `OptimisationCompletedEvent` outcomes back into the runtime resource.

OC MS validates runtime requests only against the current `ACTIVE` version of the referenced `OptimisationSpecification.id`. OD MS guarantees that `ACTIVE` and `RETIRED` specification versions are immutable, so OC MS can treat the resolved `ACTIVE` specification version as stable for the lifetime of the accepted runtime `Optimisation`.

OC MS does not use `specKey`, `draftId`, official specification `version`, or `expression.iri` to choose a runtime contract. Runtime validation is anchored on the referenced `OptimisationSpecification.id`; OC MS resolves the current `ACTIVE` version from OD MS at request-acceptance time and persists the resolved `version`, `draftId`, and `href` as contract traceability metadata. `expression.iri` is not a selector; it is a semantic compatibility check against the resolved `ACTIVE` specification.

## 2. Ownership:

OC MS owns:

```text
Runtime Optimisation resource
Runtime lifecycle
Syntactic and OD-MS-contract validation
OC MS outbox write
Publishing worker instruction events to t7.optimisation.events
Inbox consumption of OptimisationCompletedEvent worker outcomes
Runtime result projection
Cancellation and retrial controls
```

OC MS does not own:

```text
OptimisationSpecification definitions
OptimisationSpecification lifecycle and version governance
Gurobi model formulation
OW MS execution and Gurobi solver execution
Analytics platform datasets
Long-running intent control-loop assurance
```

## 3. Endpoint set:

Supported:

```http
GET /optimisation
POST /optimisation
GET /optimisation/{id}
POST /optimisation/{id}/cancellation
POST /optimisation/{id}/retrial
```

Not supported:

```http
PUT /optimisation/{id}
PATCH /optimisation/{id}
DELETE /optimisation/{id}
```

Runtime `Optimisation` is an execution and audit record, not an editable draft definition. Runtime changes occur only through internal event projection and explicit runtime commands such as cancellation and retrial. Clients must not use `PATCH` to edit runtime `Optimisation` resources.

## 4. Runtime Optimisation canonical fields:

Canonical runtime `Optimisation` fields:

```text
id
href
name
description
priority
lifecycleStatus
statusChangeDate
creationDate
lastUpdate
sourceContext
creationContext
optimisationSpecification
expression
result
optimisationRelationship[]
@type
@baseType
@schemaLocation
_links
```

Client create requests must not provide server-controlled runtime fields:

```text
id
href
lifecycleStatus
statusChangeDate
creationDate
lastUpdate
result
optimisationRelationship[]
creationContext
_links
optimisationSpecification.version
optimisationSpecification.draftId
optimisationSpecification.href
optimisationSpecification.specKey
optimisationSpecification.etag
etag or any ETag-like payload field
```

OC MS resolves and assigns those fields at creation time or during runtime projection. If a client supplies a forbidden server-controlled field, OC MS returns `400 Bad Request`.

Field notes:

| **Field** | **Rule** |
|---|---|
| `id` and `href` | Server-assigned runtime resource identity. |
| `priority` | Optional caller-supplied priority rank represented as a string. Baseline allowed values are `"1"` = highest, `"2"` = normal, and `"3"` = low. If omitted, OC MS applies the default priority policy. Unsupported priority values return `400 Bad Request`. |
| `sourceContext` | Optional provenance context identifying the upstream domain and source resource that requested or caused the optimisation. It may be used for audit, traceability, and list filtering. |
| `creationContext` | Server-assigned creation context for the runtime Optimisation. Baseline `creationContext.reason` values are `NEW` for a normal runtime optimisation request and `RETRIAL` for a new Optimisation created from a retrial request. |
| `optimisationSpecification` | Mandatory immutable reference to the resolved `ACTIVE` `OptimisationSpecification` version used as the exact contract pointer at creation time. Includes `id`, `version`, `draftId`, and `href`. OD MS ETags are HTTP headers and are not exposed as fields inside the runtime payload. |
| `expression` | Accepted runtime expression submitted by the caller. `expression.iri` is mandatory and must match the referenced ACTIVE specification's `expressionSpecification.iri`. |
| `result` | Result, terminal outcome, or command-outcome detail projection where available. Presence depends on lifecycle state. |
| `optimisationRelationship[]` | Used for relationships between runtime Optimisation resources. The baseline relationship type is `retrialOf`; other relationship types are out of scope for the current baseline. |
| `lifecycleStatus` and `statusChangeDate` | Runtime state and last lifecycle transition time. |
| `_links` | Lifecycle-aware HATEOAS action links. |

OC MS persists the resolved `OptimisationSpecification.id`, `version`, `draftId`, and `href` as the immutable contract pointer for the life of the runtime `Optimisation`. Runtime creation requires both `optimisationSpecification.id` and `expression.iri`. OC MS MUST use `optimisationSpecification.id` to resolve the current `ACTIVE` specification version from OD MS at acceptance time and MUST verify that `expression.iri` matches that resolved version's `expressionSpecification.iri`. OC MS MUST NOT substitute a different specification because of `specKey` or `expressionSpecification.iri`. If the resolved specification version is later `RETIRED`, the runtime `Optimisation` remains valid as an audit record; OC MS does not revalidate or rewrite the persisted specification reference.

Specification reference identity model:

```text
optimisationSpecification.id = stable OD MS specification lineage identity
optimisationSpecification.version = official immutable version resolved at acceptance time
optimisationSpecification.draftId = provenance identifier of the draft candidate that produced the resolved version
optimisationSpecification.href = OD MS hyperlink for the resolved version
```

OD MS ETags remain HTTP header values. OC MS may store the OD MS ETag internally for cache validation, audit, and troubleshooting, but it must not expose that OD MS ETag as a field inside the runtime `Optimisation` payload.

OC MS stores the resolved `version` even when the request supplies only `optimisationSpecification.id`. This preserves the exact contract used by the runtime `Optimisation` after OD MS later activates a newer version for the same `id`.

Creation context model:

```text
creationContext.reason = NEW for a normal runtime optimisation request.
creationContext.reason = RETRIAL for a new Optimisation created by retrying a previous FAILED Optimisation.
creationContext is assigned by OC MS and must not be supplied by clients.
Retrial is represented by creationContext plus optimisationRelationship, not by a lifecycleStatus value.
```

## 5. Runtime lifecycle:

```text
ACKNOWLEDGED
QUEUED
PROCESSING
COMPLETED
INFEASIBLE
FAILED
CANCELLING
CANCELLED
CANCELLATIONFAILED
```

Rules:

```text
ACKNOWLEDGED: OC MS accepted the request, persisted the Optimisation resource, and wrote the outbox event.
QUEUED: OptimisationRequestedEvent has been published or is waiting for worker processing.
PROCESSING: OW MS has started processing the optimisation work.
COMPLETED: Worker completed successfully and produced a usable result.
INFEASIBLE: Worker completed correctly, but no valid solution exists.
FAILED: Technical or runtime failure occurred.
CANCELLING: Cancellation command has been accepted and worker should stop or ignore where safely possible.
CANCELLED: Optimisation is confirmed cancelled.
CANCELLATIONFAILED: Non-terminal state. Represents failure of the cancellation command only. Cancellation was accepted and attempted, but the worker later reported that cancellation could not be honoured, applied, or confirmed. The optimisation execution may still continue and may later move to COMPLETED, INFEASIBLE, or FAILED.
```

Runtime `Optimisation` does not expose a `version` field. ETag is used in HTTP headers for unsafe concurrency.

`statusChangeDate` records when `lifecycleStatus` last changed. It is distinct from `creationDate` and `lastUpdate`. `statusChangeDate` MUST be updated on every lifecycleStatus transition, including `ACKNOWLEDGED -> QUEUED`, `QUEUED -> PROCESSING`, `CANCELLING -> CANCELLED`, `CANCELLING -> CANCELLATIONFAILED`, `CANCELLATIONFAILED -> COMPLETED`, `CANCELLATIONFAILED -> INFEASIBLE`, `CANCELLATIONFAILED -> FAILED`, and other terminal outcomes.

## 6. Lifecycle transitions:

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
FAILED -> retrial creates a new Optimisation
COMPLETED -> terminal
INFEASIBLE -> terminal by default
CANCELLED -> terminal
```
![State chart](oc-ms-lifecycle-state.svg)

`ACKNOWLEDGED -> QUEUED` is driven by OC MS after the OC MS Outbox Relay successfully publishes the `OptimisationRequestedEvent` to the Kafka topic. If publication is delayed, the resource may remain `ACKNOWLEDGED` while the outbox retry policy continues.

`QUEUED -> PROCESSING` may be driven by an internal worker-start acknowledgement or equivalent worker-start notification accepted by OC MS. The exact worker-start signal is platform-internal and does not change the external OC MS API contract. The current Kafka event baseline remains limited to `OptimisationRequestedEvent` and `OptimisationCompletedEvent`; introducing a separate progress event is outside the current baseline and would require an explicit event-baseline change.

Retrial does not move the failed Optimisation back to `PROCESSING`. It creates a new linked Optimisation with `retrialOf`.

Retrial is available only from `FAILED` in the baseline. Retrial is not allowed from `ACKNOWLEDGED`, `QUEUED`, `PROCESSING`, `CANCELLING`, `CANCELLATIONFAILED`, `COMPLETED`, `INFEASIBLE`, or `CANCELLED`. `CANCELLATIONFAILED` is not retriable in the baseline; if the optimisation later reaches `FAILED`, retrial may then be requested from `FAILED`. Retrial is not available from `INFEASIBLE` by default because `INFEASIBLE` is a valid optimisation or model outcome, not a technical execution failure. If a consumer wants another attempt after `INFEASIBLE`, it must submit a new `Optimisation` request with changed inputs.

## 7. Result presence rules:

Normative result field rules:

```text
result MUST be absent while lifecycleStatus is ACKNOWLEDGED, QUEUED, PROCESSING, or CANCELLING.
result MAY be present when lifecycleStatus is COMPLETED, INFEASIBLE, FAILED, CANCELLED, or CANCELLATIONFAILED.
For CANCELLATIONFAILED, result may include safe cancellation-attempt outcome details, but the optimisation may still later move to COMPLETED, INFEASIBLE, or FAILED when a normal worker outcome is received. If a later normal terminal outcome is projected, the CANCELLATIONFAILED result details should be superseded by the final outcome details.
FAILED result details may include safe error codes, safe messages, retry guidance, and diagnostic references.
FAILED and CANCELLATIONFAILED result details must not expose sensitive solver internals, Gurobi model formulation, credentials, infrastructure details, or raw stack traces.
```

Minimal result shape:

| **Field** | **Rule** |
|---|---|
| `outcome` | Required when `result` is present. Must match the projected outcome: `COMPLETED`, `INFEASIBLE`, `FAILED`, `CANCELLED`, or `CANCELLATIONFAILED`. |
| `summary` | Required when `result` is present. Safe human-readable summary suitable for external consumers. |
| `code` | Optional safe machine-readable outcome or diagnostic code. Required for `FAILED` and recommended for `INFEASIBLE`, `CANCELLED`, and `CANCELLATIONFAILED`. |
| `outputs[]` | Optional successful output values. Normally used only for `COMPLETED`. |
| `diagnostics[]` | Optional safe diagnostic references or messages. Must not expose solver internals, raw stack traces, credentials, infrastructure details, or Gurobi model formulation. |
| `retryGuidance` | Optional safe retry guidance. Normally used for `FAILED`; not used to imply retrial is available unless the lifecycle action link is present. |

Outcome-specific result rules:

```text
COMPLETED: result.outcome = COMPLETED and result.outputs[] may contain safe optimisation outputs.
INFEASIBLE: result.outcome = INFEASIBLE and result.summary or diagnostics explain why no feasible solution exists at a safe level.
FAILED: result.outcome = FAILED and result.code, summary, diagnostics, or retryGuidance may describe the technical or runtime failure safely.
CANCELLED: result.outcome = CANCELLED and result.summary may confirm cancellation was honoured safely.
CANCELLATIONFAILED: result.outcome = CANCELLATIONFAILED and result.summary or diagnostics may describe the failed cancellation command. This result is non-terminal and must be replaced, not merged, if a later terminal optimisation outcome is projected.
```

## 8. HATEOAS by lifecycle:

```text
ACKNOWLEDGED, QUEUED, and PROCESSING: self and cancellation
CANCELLING: self
CANCELLATIONFAILED: self
FAILED: self retrial
COMPLETED, INFEASIBLE, and CANCELLED: self
```

While `lifecycleStatus = CANCELLATIONFAILED`, the optimisation remains observable but no further cancellation or retrial action is exposed in the baseline. Callers should continue polling until a normal terminal outcome is projected.

## 9. External response header governance:

OC MS exposes optimiser-domain platform resources using TMF-style resource conventions. `Optimisation` is not a native TMF Open API resource.

All NGW-facing OC MS resource responses include:

```http
x-platform-extension: true
x-tmf-native: false
```

These headers are governance and documentation indicators only. Clients must not use them as runtime business-logic switches.

`x-cb-triggered: true` may also be returned when a remote dependency circuit breaker changes the externally meaningful response path. It is diagnostic only and must not be used as a business-logic switch or lifecycle/outcome indicator.

## 10. POST /optimisation:

```http
POST /optimisation
Content-Type: application/json
```

```json
{
  "sourceContext": {
    "domain": "intent-management",
    "resource": {
      "id": "intent-789",
      "href": "/intentManagement/v5/intent/intent-789",
      "@type": "IntentRef",
      "@referredType": "Intent"
    }
  },
  "optimisationSpecification": {
    "id": "optimisation-spec-surgical-routing",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice workload.",
  "priority": "1",
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
  },
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json"
}
```

Successful response:

```http
HTTP/1.1 201 Created
Location: /optimisation/opt-12345
ETag: "opt-12345-rev1"
Content-Type: application/json
x-platform-extension: true
x-tmf-native: false
```

```json
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",
  "sourceContext": {
    "domain": "intent-management",
    "resource": {
      "id": "intent-789",
      "href": "/intentManagement/v5/intent/intent-789",
      "@type": "IntentRef",
      "@referredType": "Intent"
    }
  },
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice workload.",
  "priority": "1",
  "lifecycleStatus": "ACKNOWLEDGED",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:00:00Z",
  "statusChangeDate": "2026-05-02T03:00:00Z",
  "creationContext": {
    "reason": "NEW"
  },
  "optimisationSpecification": {
    "id": "optimisation-spec-surgical-routing",
    "version": "1.1.0",
    "draftId": "od-draft-surgical-routing-b",
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?version=1.1.0",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },
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
  },
  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    },
    "cancellation": {
      "href": "/optimisation/opt-12345/cancellation",
      "method": "POST"
    }
  }
}
```

`201 Created` means OC MS created and persisted the runtime `Optimisation` resource immediately. Execution is asynchronous; resource creation is immediate. `201 Created` does not mean the optimisation is feasible, started, solvable, or guaranteed to produce a valid result.

The response `optimisationSpecification` reference shows the resolved ACTIVE contract version persisted by OC MS. The request may provide only `optimisationSpecification.id`; `version`, `draftId`, and `href` in the response are resolved from OD MS at acceptance time.

## 11. OD specification lookup and cache posture:

On `POST /optimisation`, OC MS validates the runtime request against the current `ACTIVE` version of the referenced `OptimisationSpecification.id` and the runtime `expression.iri`. Both are mandatory for runtime creation.

Rules:

```text
The runtime request must provide optimisationSpecification.id.
The runtime request must provide expression.iri.
The referenced OptimisationSpecification.id must exist in OD MS.
OD MS must return a current ACTIVE version for the referenced OptimisationSpecification.id at request-acceptance time.
The runtime expression.iri must match the resolved ACTIVE version's expressionSpecification.iri.
OC MS must not infer the current active contract by stale `specKey` lookup.
OC MS must not resolve the runtime contract by expression.iri alone.
OC MS treats `specKey` as OD MS catalogue governance metadata and does not accept or require it in runtime creation requests.
OC MS does not use `specKey`, `draftId`, official specification `version`, or `expression.iri` to choose a runtime contract.
OC MS resolves the current ACTIVE version by OptimisationSpecification.id at acceptance time.
OC MS persists the resolved OptimisationSpecification.id, version, draftId, and href as the immutable contract pointer for the life of the runtime Optimisation.
OC MS MUST NOT substitute a different specification because of `specKey` or `expressionSpecification.iri`.
If the resolved specification version is later RETIRED, the runtime Optimisation remains valid as an audit record; OC MS does not revalidate or rewrite the specification reference.
OC MS may maintain an internal OD contract cache for immutable ACTIVE OptimisationSpecification contracts. The cache is keyed by the resolved specification id and version, and may use the OD MS ETag HTTP header internally for cache validation. The OD MS ETag remains a header value and must not be exposed inside the runtime Optimisation payload.
A cached ACTIVE contract for a specific id and version is safe because OD MS makes ACTIVE and RETIRED versions immutable.
If the referenced specification is missing, no ACTIVE version exists, the OD contract cache is missing, or the OD contract cache is stale beyond the local policy, OC MS refreshes from OD MS.
```

Runtime requests must supply only `optimisationSpecification.id` for contract selection. Clients must not supply `optimisationSpecification.version`, `optimisationSpecification.draftId`, `optimisationSpecification.href`, or `optimisationSpecification.specKey` on creation. OC MS resolves `version`, `draftId`, and `href` from OD MS and persists them in the accepted runtime resource. OD MS ETags remain HTTP headers and may be used internally for cache validation, but they are not exposed in the runtime payload. If a client supplies any of those forbidden fields, OC MS returns `400 Bad Request`. If a client supplies ETag-like metadata in the JSON payload, OC MS also returns `400 Bad Request` because ETag is not a valid runtime payload field.

If OD MS is unavailable and OC MS has no valid cached immutable `ACTIVE` contract for the requested `OptimisationSpecification.id`, OC MS returns `503 Service Unavailable`. If OC MS has a valid cached immutable `ACTIVE` contract for the requested id and resolved version, it may proceed according to the configured OD contract cache policy.

OC MS may maintain a request-result cache for optimisation outcomes. The cache key is a deterministic hash of the canonical accepted runtime optimisation request body after OC MS has resolved the referenced ACTIVE `OptimisationSpecification` version. Each distinct canonical accepted request has its own cache entry. The cache stores the reusable optimisation response or outcome reference according to cache policy. The canonical request hash must be based only on fields that are part of the accepted optimisation problem and must not include transport headers or operational trace metadata. Cache TTL and eviction policy are deployment-governed and outside the current baseline specification. The cache hash is internal metadata and must not replace the runtime `Optimisation.id`, lifecycle, persisted audit record, or external resource representation. A request-result cache hit must still create or return a governed OC runtime `Optimisation` resource according to the OC MS contract and must not bypass lifecycle, audit, source-of-truth persistence, ETag handling, or external resource identity.

## 12. OC MS validation boundary:

OC MS validates:

```text
generic REST wrapper using its static API and OpenAPI contract
optimisationSpecification.id is present
expression.iri is present
referenced OptimisationSpecification.id exists in OD MS
referenced OptimisationSpecification.id has a current ACTIVE version
resolved ACTIVE OptimisationSpecification version is immutable by OD MS lifecycle governance
resolved version, draftId, and href are persisted as contract traceability metadata
expression wrapper shape:
  expression.@type = JsonLdExpression
  expression.@baseType = Expression
  expression.iri matches the resolved ACTIVE OptimisationSpecification version's expressionSpecification.iri
expression.expressionValue against the resolved ACTIVE OptimisationSpecification version's targetEntitySchema
expression.expressionValue JSON-LD context, type, container shape, target entries, constraint entries, preference entries, cardinality, and allowed values as defined by the resolved targetEntitySchema
```

OC MS must not hardcode a universal `expressionValue.@context` alias set or `expressionValue.@type` value outside the resolved `targetEntitySchema`. Concrete `OptimisationSpecification` contracts may use different ontology IRIs or JSON-LD aliases when OD MS governs them through the target entity schema.

OC MS does not validate:

```text
optimisation semantics
solver feasibility
candidate selection
objective interpretation
Gurobi model validity
resource-selection correctness
```

After acceptance, OC MS persists the runtime resource and writes `OptimisationRequestedEvent` with `instruction = EXECUTE` to its outbox in the same transaction.

Cancellation uses the same event type with `instruction = CANCEL`. OW MS execution outcomes and cancellation-command outcomes are returned through `OptimisationCompletedEvent`. Execution outcomes are `COMPLETED`, `INFEASIBLE`, or `FAILED`. Cancellation-command outcomes are `CANCELLED` or `CANCELLATIONFAILED`. `COMPLETED`, `INFEASIBLE`, and `FAILED` are terminal execution outcomes. `CANCELLED` is a terminal cancellation-command outcome. `CANCELLATIONFAILED` is a non-terminal cancellation-command outcome and may later be followed by a normal terminal execution outcome.

## 13. Internal event baseline:

OC MS uses exactly two internal Kafka event types with OW MS in the current baseline. These are platform-internal events, not TMF external notification events.

| **Event** | **Emitter** | **Consumer** | **Purpose** | **Key values** |
|---|---|---|---|---|
| `OptimisationRequestedEvent` | OC MS, OC MS Outbox Relay | OW MS | OW MS instruction event for execution or cancellation. | `instruction = EXECUTE` or `instruction = CANCEL` |
| `OptimisationCompletedEvent` | OW MS | OC MS, OC MS Inbox Consumer | OW MS outcome and cancellation-command outcome event for lifecycle and result projection. | `status = COMPLETED`, `FAILED`, `INFEASIBLE`, `CANCELLED`, or `CANCELLATIONFAILED` |

`OptimisationFailedEvent` is not used in the current baseline. Failed, infeasible, cancelled, and cancellation-failed outcomes are carried by `OptimisationCompletedEvent.status`. The event name remains `OptimisationCompletedEvent` in the current baseline even when it carries `CANCELLATIONFAILED` as a cancellation-command outcome. No separate cancellation-failed or progress event type is introduced. `CANCELLATIONFAILED` is not necessarily terminal; OC MS may later project `COMPLETED`, `INFEASIBLE`, or `FAILED` for the same Optimisation when a normal worker outcome is received.

Event identity and idempotency requirements:

```text
OptimisationRequestedEvent and OptimisationCompletedEvent MUST include optimisationId.
OptimisationRequestedEvent and OptimisationCompletedEvent MUST include correlationId and traceId.
OptimisationRequestedEvent and OptimisationCompletedEvent MUST include a unique eventId or CloudEvents ce-id.
OptimisationCompletedEvent processing MUST be idempotent.
OC MS projection MUST safely handle duplicate OptimisationCompletedEvent messages.
OC MS may use eventId or ce-id, inbox deduplication state, and monotonic lifecycle and statusChangeDate rules to suppress duplicate, stale, or late event projection.
CANCELLATIONFAILED must not suppress or block projection of subsequent valid terminal outcomes.
```

CloudEvents header baseline:

| **Header** | **Rule** |
|---|---|
| `ce-specversion` | Required. Use the platform-supported CloudEvents version. |
| `ce-id` | Required unique event id for idempotency. May also be carried as `eventId` in the event body where required by platform convention. |
| `ce-type` | Required. `OptimisationRequestedEvent` or `OptimisationCompletedEvent`. |
| `ce-source` | Required. Emitting component, such as `optimisation-controller-ms` or `optimisation-worker-ms`. |
| `ce-time` | Required event creation timestamp. |
| `ce-subject` | Recommended. Runtime `Optimisation.id`. |
| `correlationId` | Required platform correlation id. |
| `traceId` | Required platform trace id. |

`OptimisationRequestedEvent` body baseline:

| **Field** | **Rule** |
|---|---|
| `eventId` | Unique event id when body-level event identity is used in addition to `ce-id`. |
| `optimisationId` | Runtime `Optimisation.id` created by OC MS. |
| `instruction` | `EXECUTE` or `CANCEL`. |
| `creationContext` | Present for `EXECUTE`; includes `reason = NEW` or `RETRIAL`. |
| `optimisationSpecification` | Resolved immutable contract pointer with `id`, `version`, `draftId`, and `href`. ETags are headers or internal cache metadata only, not event payload fields. |
| `expression` | Accepted runtime expression for `EXECUTE`. |
| `cancellation` | Optional safe cancellation reason or comment metadata for `CANCEL` only. |
| `correlationId` and `traceId` | Required diagnostic context. |

`OptimisationCompletedEvent` body baseline:

| **Field** | **Rule** |
|---|---|
| `eventId` | Unique event id when body-level event identity is used in addition to `ce-id`. |
| `optimisationId` | Runtime `Optimisation.id` whose lifecycle or result is being projected. |
| `status` | `COMPLETED`, `INFEASIBLE`, `FAILED`, `CANCELLED`, or `CANCELLATIONFAILED`. |
| `result` | Optional safe outcome detail using the OC MS result shape. Required where the worker has safe useful output or diagnostics to project. |
| `correlationId` and `traceId` | Required diagnostic context. |

DLQ posture:

```text
Events that cannot be deserialised, validated, correlated to a known optimisationId, or safely projected after configured retry handling go to the optimiser DLQ.
DLQ entries must retain enough metadata for diagnosis and controlled replay decisions.
Automatic replay from DLQ is outside the current baseline.
DLQ handling must not expose solver internals or sensitive infrastructure details through external OC MS payloads.
```

## 14. GET /optimisation list:

Request:

```http
GET /optimisation?lifecycleStatus=PROCESSING&offset=0&limit=50&fields=id,href,lifecycleStatus,statusChangeDate
```

Supported first-level filters:

| Query parameter | Meaning |
|---|---|
| `id` | Exact match on runtime Optimisation id. |
| `lifecycleStatus` | Exact match on runtime lifecycle state. Supported values are `ACKNOWLEDGED`, `QUEUED`, `PROCESSING`, `COMPLETED`, `INFEASIBLE`, `FAILED`, `CANCELLING`, `CANCELLED`, and `CANCELLATIONFAILED`. |
| `sourceContext.domain` | Exact match on source context domain where present. |
| `sourceContext.resource.id` | Exact match on source resource id where present. |
| `optimisationSpecification.id` | Exact match on referenced OptimisationSpecification id. |
| `optimisationSpecification.version` | Exact match on resolved official OptimisationSpecification version persisted at acceptance time. |
| `optimisationSpecification.draftId` | Exact match on the draft candidate provenance identifier persisted from the resolved OptimisationSpecification version. |
| `creationDate.gt`, `creationDate.lt` | Optional creation timestamp range filters. |
| `lastUpdate.gt`, `lastUpdate.lt` | Optional last-update timestamp range filters. |
| `statusChangeDate.gt`, `statusChangeDate.lt` | Optional lifecycle-state-change date range filters. |
| `offset` | Zero-based starting position for paging. Default is `0`. |
| `limit` | Maximum number of resources returned in the current page. Default and maximum are deployment-governed. |
| `fields` | Optional sparse fieldset projection. |

Unsupported or malformed query parameters return `400 Bad Request`. Invalid `offset` or `limit` values also return `400 Bad Request`.

Paging rule:

```text
offset is the zero-based starting position.
limit is the maximum number of resources returned in the current page.
X-Total-Count reflects the number of resources matching filters before paging.
X-Result-Count reflects the number of resources returned in the current page after paging.
```

Sparse field projection rule:

```text
fields supports top-level fields only in the baseline. Nested field selection is not supported.
If a requested field is valid but not present for the resource's current lifecycle state, OC MS omits that field silently rather than returning an error.
For example, fields=id,result on a PROCESSING resource returns id and omits result because result is not present before terminal outcome projection. For `CANCELLATIONFAILED`, `result` may be present with cancellation-command outcome details, but it may later be superseded when a valid terminal outcome is projected.
Unsupported field names still return 400 Bad Request.
```

Response headers:

```http
HTTP/1.1 200 OK
X-Total-Count: 1
X-Result-Count: 1
Content-Type: application/json
x-platform-extension: true
x-tmf-native: false
```

```json
[
  {
    "id": "opt-12345",
    "href": "/optimisation/opt-12345",
    "lifecycleStatus": "PROCESSING",
    "statusChangeDate": "2026-05-02T03:01:00Z",
    "creationContext": {
      "reason": "NEW"
    },
    "@type": "Optimisation",
    "_links": {
      "self": {
        "href": "/optimisation/opt-12345",
        "method": "GET"
      },
      "cancellation": {
        "href": "/optimisation/opt-12345/cancellation",
        "method": "POST"
      }
    }
  }
]
```

`X-Total-Count` reflects the total number of resources matching the applied filters before paging and sparse field projection. `X-Result-Count` reflects the number of resources returned in the current response page.

## 15. GET /optimisation/{id}:

Full `GET /optimisation/{id}` representations include the accepted `expression` unless sparse field projection or a configured representation policy omits it. Examples may omit unchanged fields for brevity when the omitted fields are not material to the rule being illustrated.

```http
GET /optimisation/opt-12345
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "opt-12345-rev2"
x-platform-extension: true
x-tmf-native: false
```

Active-state example:

```json
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",
  "name": "Hospital surgical slice path optimisation request",
  "lifecycleStatus": "PROCESSING",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:01:00Z",
  "statusChangeDate": "2026-05-02T03:01:00Z",
  "creationContext": {
    "reason": "NEW"
  },
  "optimisationSpecification": {
    "id": "optimisation-spec-surgical-routing",
    "version": "1.1.0",
    "draftId": "od-draft-surgical-routing-b",
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?version=1.1.0",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },
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
  },
  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    },
    "cancellation": {
      "href": "/optimisation/opt-12345/cancellation",
      "method": "POST"
    }
  }
}
```

Completed-state example:


```json
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",
  "lifecycleStatus": "COMPLETED",
  "creationDate": "2026-05-02T03:00:00Z",
  "lastUpdate": "2026-05-02T03:03:00Z",
  "statusChangeDate": "2026-05-02T03:03:00Z",
  "creationContext": {
    "reason": "NEW"
  },
  "optimisationSpecification": {
    "id": "optimisation-spec-surgical-routing",
    "version": "1.1.0",
    "draftId": "od-draft-surgical-routing-b",
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?version=1.1.0",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },
  "result": {
    "outcome": "COMPLETED",
    "summary": "Optimisation completed successfully.",
    "outputs": [
      {
        "name": "selectedResource",
        "valueType": "object",
        "value": {
          "resourceId": "path-001",
          "resourceType": "deliveryResource"
        }
      }
    ]
  },
  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    }
  }
}
```

## 16. Cancellation and retrial:

Cancellation:

```http
POST /optimisation/opt-12345/cancellation
If-Match: "opt-12345-rev2"
Content-Type: application/json
```

Retrial:

```http
POST /optimisation/opt-12345/retrial
If-Match: "opt-12345-rev3"
Content-Type: application/json
```

Cancellation and retrial responses include the OC external response governance headers:

```http
x-platform-extension: true
x-tmf-native: false
```

Cancellation request body:

```text
No request body is required.
If a request body is supplied, it may contain optional reason or comment metadata only.
A supplied cancellation body does not change cancellation semantics, worker instruction meaning, or lifecycle eligibility.
```

Cancellation semantics:

```text
Cancellation is best-effort.
OC MS accepts cancellation only from eligible active lifecycle states: `ACKNOWLEDGED`, `QUEUED`, and `PROCESSING`.
Baseline cancellation confirmation is `OptimisationCompletedEvent.status = CANCELLED`. OC MS sets `CANCELLED` only from that event in the current baseline. If the worker reports that cancellation could not be honoured, applied, or confirmed, OC MS may project `CANCELLATIONFAILED`. Any alternative terminal confirmation path is outside the current baseline.
If cancellation is requested when lifecycleStatus is not cancellation-eligible, including `CANCELLING`, `CANCELLATIONFAILED`, `COMPLETED`, `FAILED`, `INFEASIBLE`, or `CANCELLED`, OC MS returns 409 Conflict.
```

Successful cancellation response:

```http
HTTP/1.1 202 Accepted
ETag: "opt-12345-rev3"
Content-Type: application/json
x-platform-extension: true
x-tmf-native: false
```

```json
{
  "id": "opt-12345",
  "href": "/optimisation/opt-12345",
  "lifecycleStatus": "CANCELLING",
  "statusChangeDate": "2026-05-02T03:02:00Z",
  "@type": "Optimisation",
  "_links": {
    "self": {
      "href": "/optimisation/opt-12345",
      "method": "GET"
    }
  }
}
```

`202 Accepted` means OC MS has validated `If-Match` and lifecycle eligibility, moved the runtime resource to `CANCELLING`, and written the `CANCEL` instruction to the outbox. It does not mean the worker has confirmed cancellation. The cancellation response body is a compact representation; full resource retrieval through `GET /optimisation/{id}` returns all fields, including `creationContext`. Final cancellation is projected only when OC MS receives `OptimisationCompletedEvent.status = CANCELLED`. If OC MS receives `OptimisationCompletedEvent.status = CANCELLATIONFAILED`, the resource moves to `CANCELLATIONFAILED` and may later move to `COMPLETED`, `INFEASIBLE`, or `FAILED` if a normal terminal optimisation outcome is received.

Retrial request body:

```text
No request body is required.
OC MS accepts retrial only when the original Optimisation lifecycleStatus is FAILED.
Retrial from any other lifecycleStatus returns 409 Conflict.
Baseline retrial does not allow request overrides.
Retrial resubmits the original accepted expression and the persisted resolved OptimisationSpecification reference unchanged, including `id`, `version`, `draftId`, and `href`.
Retrial does not re-resolve the current `ACTIVE` specification from OD MS. It reuses the original persisted specification `id`, `version`, and `draftId` contract pointer.
To change targets, constraints, preferences, source context, priority, or the referenced OptimisationSpecification contract, the caller must create a new Optimisation request rather than using retrial.
```

Retrial response creates a new Optimisation and links it to the failed optimisation. The new Optimisation has `creationContext.reason = RETRIAL`; normal runtime creation has `creationContext.reason = NEW`. Retrial is creation context, not a lifecycle state:

```http
HTTP/1.1 201 Created
Location: /optimisation/opt-67890
ETag: "opt-67890-rev1"
Content-Type: application/json
x-platform-extension: true
x-tmf-native: false
```

```json
{
  "id": "opt-67890",
  "href": "/optimisation/opt-67890",
  "@type": "Optimisation",
  "@baseType": "Entity",
  "@schemaLocation": "/schema/Optimisation.schema.json",
  "name": "Hospital surgical slice path optimisation request",
  "description": "Optimise path selection for hospital surgical slice workload.",
  "priority": "1",
  "lifecycleStatus": "ACKNOWLEDGED",
  "creationDate": "2026-05-02T04:00:00Z",
  "lastUpdate": "2026-05-02T04:00:00Z",
  "statusChangeDate": "2026-05-02T04:00:00Z",
  "creationContext": {
    "reason": "RETRIAL"
  },
  "optimisationSpecification": {
    "id": "optimisation-spec-surgical-routing",
    "version": "1.1.0",
    "draftId": "od-draft-surgical-routing-b",
    "href": "/optimisationManagement/v1/optimisationSpecification/optimisation-spec-surgical-routing?version=1.1.0",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },
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
  },
  "optimisationRelationship": [
    {
      "@type": "EntityRelationship",
      "relationshipType": "retrialOf",
      "id": "opt-12345",
      "@referredType": "Optimisation"
    }
  ],
  "_links": {
    "self": {
      "href": "/optimisation/opt-67890",
      "method": "GET"
    },
    "cancellation": {
      "href": "/optimisation/opt-67890/cancellation",
      "method": "POST"
    }
  }
}
```

## 17. Header/concurrency rules:

```text
POST /optimisation: returns Location and ETag
GET /optimisation/{id}: returns ETag
GET /optimisation: no per-item ETag by default; includes X-Total-Count and X-Result-Count
POST /optimisation/{id}/cancellation: requires If-Match
POST /optimisation/{id}/retrial: requires If-Match
missing If-Match -> 428
stale or wrong If-Match -> 412
```

NGW-facing OC MS resource responses include:

```http
x-platform-extension: true
x-tmf-native: false
```

Strict content type rules:

```text
POST /optimisation requires Content-Type: application/json.
POST /optimisation/{id}/cancellation has no required body; if a body is sent it requires Content-Type: application/json.
POST /optimisation/{id}/retrial has no required body; if a body is sent it requires Content-Type: application/json.
A body sent without Content-Type, or with an unsupported Content-Type, on cancellation or retrial returns 415 Unsupported Media Type.
Unsupported request content type returns 415 Unsupported Media Type.
```

### 17.1. Circuit breaker and remote dependency behaviour:

OC MS must apply circuit breakers, timeouts, bounded retries, and isolation to remote dependencies such as OD MS, its database, Kafka, cache stores where used, and other approved platform dependencies.

If a non-critical cache dependency is unavailable but OC MS can still serve the source-of-truth response from its database or required upstream dependency, OC MS should bypass the cache and return the normal response. The circuit-breaker header is N/A for that response.

If a remote dependency circuit breaker affects the externally meaningful response path, OC MS must include:

```http
x-cb-triggered: true
```

This header may appear on successful fallback responses or hard-failure responses. HTTP status and response body remain authoritative for success or failure. `x-cb-triggered: true` only indicates that a remote dependency circuit breaker affected the externally meaningful response path.

OC MS may proceed with runtime creation using a valid cached immutable ACTIVE OD contract only where the cache policy allows it and the cached contract is semantically safe for the requested `OptimisationSpecification.id` and resolved version. If OD MS is unavailable and OC MS has no valid cached immutable ACTIVE contract, OC MS must fail fast with `503 Service Unavailable` and include `x-cb-triggered: true`.

OC MS must not use cached or default fallback to fake runtime creation, contract validation, lifecycle projection, cancellation acceptance, retrial creation, ETag validation, result projection, security visibility, or audit state. For command and state-changing operations, OC MS may return a normal success status only when the operation has genuinely completed its required validation, persistence, concurrency, and durability obligations.

For OC MS runtime creation and cancellation, Kafka broker unavailability does not necessarily fail the REST command if OC MS can durably persist the runtime state and outbox record; the outbox relay handles later Kafka publication according to retry and DLQ policy.

While a circuit breaker is open, OC MS must monitor recovery through bounded health probes or test calls according to platform circuit-breaker policy. Probe behaviour must be rate-limited and must not overload a recovering dependency.

## 18. Error handling boundary:

| **Condition** | **Response** |
|---|---|
| Missing `optimisationSpecification.id`, missing `expression`, missing `expression.iri`, malformed wrapper, malformed JSON, malformed query parameter, unsupported query parameter, invalid paging parameter, unsupported priority value, or client-supplied forbidden server-controlled field | `400 Bad Request` |
| Referenced `OptimisationSpecification.id` is missing or not visible | `404 Not Found` |
| Referenced `OptimisationSpecification.id` has no current `ACTIVE` version | `422 Unprocessable Entity` |
| `expression.iri` does not match the resolved specification version's `expressionSpecification.iri` | `422 Unprocessable Entity` |
| `expression.expressionValue` fails the resolved `targetEntitySchema` | `422 Unprocessable Entity` |
| OD MS unavailable and OC MS has no valid cached immutable `ACTIVE` contract for the requested id | `503 Service Unavailable` |
| Cancellation requested from a non-eligible lifecycle state, including `CANCELLING`, `CANCELLATIONFAILED`, or terminal states, or retrial requested from `ACKNOWLEDGED`, `QUEUED`, `PROCESSING`, `CANCELLING`, `CANCELLATIONFAILED`, `COMPLETED`, `INFEASIBLE`, or `CANCELLED` | `409 Conflict` |
| Missing `If-Match` on cancellation or retrial | `428 Precondition Required` |
| Stale or wrong `If-Match` on cancellation or retrial | `412 Precondition Failed` |
| Unsupported `Content-Type` | `415 Unsupported Media Type` |

Boundary rules:

```text
400 = malformed request, missing required top-level wrapper fields such as `optimisationSpecification.id`, missing `expression`, missing `expression.iri`, unsupported query or filter parameter, invalid paging parameter, unsupported priority value, client-supplied forbidden server-controlled runtime field, or client-supplied `optimisationSpecification.specKey`.
422 = request content is syntactically valid but violates the resolved OD contract, including no current ACTIVE version for the referenced specification id, mismatch between `expression.iri` and the resolved specification version's `expressionSpecification.iri`, or `expression.expressionValue` failing `targetEntitySchema`.
409 = runtime lifecycle or action conflict.
428 = required If-Match missing.
412 = supplied If-Match does not match current ETag.
415 = unsupported request media type.
503 = OD MS is unavailable and OC MS has no valid cached immutable ACTIVE contract for the requested id.
```

Contract violation example:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_CONTRACT_VIOLATION",
  "reason": "Optimisation contract violation",
  "message": "The submitted Optimisation request does not satisfy the resolved ACTIVE OptimisationSpecification contract, including expressionSpecification.iri matching and targetEntitySchema validation.",
  "status": 422,
  "@type": "Error"
}
```

Lifecycle conflict example:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_LIFECYCLE_CONFLICT",
  "reason": "Optimisation lifecycle conflict",
  "message": "Cancellation is not allowed when lifecycleStatus is COMPLETED.",
  "status": 409,
  "@type": "Error"
}
```

Retrial lifecycle conflict example:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_LIFECYCLE_CONFLICT",
  "reason": "Optimisation lifecycle conflict",
  "message": "Retrial is not allowed when lifecycleStatus is INFEASIBLE. INFEASIBLE is a valid optimisation outcome, not a technical execution failure.",
  "status": 409,
  "@type": "Error"
}
```

Unsupported media type example:

```http
HTTP/1.1 415 Unsupported Media Type
Content-Type: application/json
```

```json
{
  "code": "UNSUPPORTED_MEDIA_TYPE",
  "reason": "Unsupported media type",
  "message": "POST /optimisation requires Content-Type: application/json.",
  "status": 415,
  "@type": "Error"
}
```

## 19. Outcome mapping:

OW MS execution outcomes and cancellation-command outcomes are carried by `OptimisationCompletedEvent.status` using the same status names that OC MS projects to runtime lifecycle states.

The current baseline keeps this single outcome event type; no separate progress, cancellation-failed, or retrial event type is introduced.

```text
COMPLETED -> lifecycleStatus COMPLETED
INFEASIBLE -> lifecycleStatus INFEASIBLE
FAILED -> lifecycleStatus FAILED
CANCELLED -> lifecycleStatus CANCELLED
CANCELLATIONFAILED -> lifecycleStatus CANCELLATIONFAILED
```

`INFEASIBLE` is an optimisation outcome produced by the worker or model. It is not a request contract validation error. `CANCELLATIONFAILED` is a cancellation-command outcome, not necessarily a terminal optimisation outcome. It may be followed by a normal terminal optimisation outcome if the worker later reports `COMPLETED`, `INFEASIBLE`, or `FAILED`.
