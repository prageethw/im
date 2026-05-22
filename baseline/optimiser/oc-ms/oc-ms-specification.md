# Optimisation Controller MS Specification

## 1. OC MS summary:

Optimisation-Controller-MS (OC MS) owns the runtime `Optimisation` resource. It is a generic optimisation controller, not an intent-only controller.

OC MS accepts runtime optimisation requests, validates the generic wrapper and the referenced OD MS request contract, persists the request, emits `OptimisationRequestedEvent`, and later projects `OptimisationCompletedEvent` outcomes back into the runtime resource.

OC MS validates runtime requests only against the currently referenced `ACTIVE` `OptimisationSpecification`. OD MS guarantees that `ACTIVE` and `RETIRED` specifications are immutable, so OC MS can treat the referenced `ACTIVE` specification contract as stable for the lifetime of the accepted runtime `Optimisation`.

OC MS does not use `familyId` or official specification `version` to select a runtime contract. Runtime validation is performed against the referenced `OptimisationSpecification.id`.

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
OptimisationSpecification lifecycle/version governance
Gurobi model formulation
Python/Gurobi solver execution
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

Runtime `Optimisation` is an execution/audit record, not an editable draft definition. Runtime changes occur only through internal event projection and explicit runtime commands such as cancellation and retrial. Clients must not use `PATCH` to edit runtime `Optimisation` resources.

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
optimisationSpecification
expression
result (terminal only)
optimisationRelationship[]
@type
@baseType
@schemaLocation
_links
```

Field notes:

| **Field** | **Rule** |
|---|---|
| `id` / `href` | Server-assigned runtime resource identity. |
| `priority` | Optional caller-supplied priority rank represented as a string. Baseline allowed values are `"1"` = highest, `"2"` = normal, and `"3"` = low. If omitted, OC MS applies the default priority policy. |
| `sourceContext` | Optional provenance context identifying the upstream domain and source resource that requested or caused the optimisation. It may be used for audit, traceability, and list filtering. |
| `optimisationSpecification` | Mandatory immutable reference to the `OptimisationSpecification.id` and `href` used as the exact contract pointer at creation time. |
| `expression` | Accepted runtime expression submitted by the caller. `expression.iri` is mandatory and must match the referenced ACTIVE specification's `expressionSpecification.iri`. |
| `result` | Terminal result projection only. Presence depends on lifecycle state. |
| `optimisationRelationship[]` | Used for relationships such as `retrialOf`. |
| `lifecycleStatus` / `statusChangeDate` | Runtime state and last lifecycle transition time. |
| `_links` | Lifecycle-aware HATEOAS action links. |

OC MS persists the referenced `OptimisationSpecification.id` and `href` as the immutable contract pointer for the life of the runtime `Optimisation`. Runtime creation requires both `optimisationSpecification.id` and `expression.iri`. OC MS MUST treat `optimisationSpecification.id` as the exact contract pointer and MUST verify that `expression.iri` matches the referenced ACTIVE specification's `expressionSpecification.iri`. OC MS MUST NOT substitute another current `ACTIVE` specification, even if the same `familyId` or `expressionSpecification.iri` later has another `ACTIVE` specification. If the referenced specification is later `RETIRED`, the runtime `Optimisation` remains valid as an audit record; OC MS does not revalidate or rewrite the specification reference.

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
```

Rules:

```text
ACKNOWLEDGED: OC MS accepted the request, persisted the Optimisation resource, and wrote the outbox event.
QUEUED: OptimisationRequestedEvent has been published or is waiting for worker processing.
PROCESSING: Python/Gurobi worker has started processing.
COMPLETED: Worker completed successfully and produced a usable result.
INFEASIBLE: Worker completed correctly, but no valid solution exists.
FAILED: Technical/runtime failure occurred.
CANCELLING: Cancellation command has been accepted and worker should stop or ignore where safely possible.
CANCELLED: Optimisation is confirmed cancelled.
```

Runtime `Optimisation` does not expose a `version` field. ETag is used in HTTP headers for unsafe concurrency.

`statusChangeDate` records when `lifecycleStatus` last changed. It is distinct from `creationDate` and `lastUpdate`.

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
FAILED -> retrial creates a new Optimisation
COMPLETED -> terminal
INFEASIBLE -> terminal by default
CANCELLED -> terminal
```

`ACKNOWLEDGED -> QUEUED` is driven by OC MS after the OC MS Outbox Relay successfully publishes the `OptimisationRequestedEvent` to the Kafka topic. If publication is delayed, the resource may remain `ACKNOWLEDGED` while the outbox retry policy continues.

Retrial does not move the failed Optimisation back to `PROCESSING`. It creates a new linked Optimisation with `retrialOf`.

Retrial is available only from `FAILED` in the baseline. Retrial is not available from `INFEASIBLE` by default because `INFEASIBLE` is a valid optimisation/model outcome, not a technical execution failure. If a consumer wants another attempt after `INFEASIBLE`, it must submit a new `Optimisation` request with changed inputs.

## 7. Result presence rules:

Normative result field rules:

```text
result MUST be absent while lifecycleStatus is ACKNOWLEDGED, QUEUED, PROCESSING, or CANCELLING.
result MAY be present when lifecycleStatus is COMPLETED, INFEASIBLE, FAILED, or CANCELLED.
FAILED result details may include safe error codes, safe messages, retry guidance, and diagnostic references.
FAILED result details must not expose sensitive solver internals, Gurobi model formulation, credentials, infrastructure details, or raw stack traces.
```

## 8. HATEOAS by lifecycle:

```text
ACKNOWLEDGED / QUEUED / PROCESSING: self cancellation
CANCELLING: self
FAILED: self retrial
COMPLETED / INFEASIBLE / CANCELLED: self
```

## 9. External response header governance:

OC MS exposes optimiser-domain platform resources using TMF-style resource conventions. `Optimisation` is not a native TMF Open API resource.

All NGW-facing OC MS resource responses include:

```http
x-platform-extension: true
x-tmf-native: false
```

These headers are governance/documentation indicators only. Clients must not use them as runtime business-logic switches.

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
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
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
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
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

## 11. OD specification lookup and cache posture:

On `POST /optimisation`, OC MS validates the runtime request against the referenced `OptimisationSpecification.id` and the runtime `expression.iri`. Both are mandatory for runtime creation.

Rules:

```text
The runtime request must provide optimisationSpecification.id.
The runtime request must provide expression.iri.
The referenced OptimisationSpecification must exist.
The referenced OptimisationSpecification must be ACTIVE at request-acceptance time.
The runtime expression.iri must match the referenced OptimisationSpecification.expressionSpecification.iri.
OC MS must not infer the current active contract by stale familyId lookup.
OC MS must not resolve the runtime contract by expression.iri alone.
OC MS does not use familyId, official specification version, or expression.iri to choose a runtime contract.
OC MS persists the referenced OptimisationSpecification.id and href as the immutable contract pointer for the life of the runtime Optimisation.
OC MS MUST treat optimisationSpecification.id as the exact contract pointer and MUST NOT substitute another current ACTIVE specification, even if the same familyId or expressionSpecification.iri later has another ACTIVE specification.
If the specification is later RETIRED, the runtime Optimisation remains valid as an audit record; OC MS does not revalidate or rewrite the specification reference.
OC MS may cache immutable ACTIVE OptimisationSpecification contracts by id and ETag.
A cached ACTIVE contract for a specific id is safe because OD MS makes ACTIVE specifications immutable.
If the referenced specification is missing, not ACTIVE, cache-missing, or cache-stale beyond the local policy, OC MS refreshes from OD MS.
```

## 12. OC MS validation boundary:

OC MS validates:

```text
generic REST wrapper using its static API/OpenAPI contract
optimisationSpecification.id is present
expression.iri is present
referenced OptimisationSpecification exists in OD MS
referenced OptimisationSpecification lifecycleStatus is ACTIVE
referenced ACTIVE OptimisationSpecification contract is immutable by OD MS lifecycle governance
expression wrapper shape:
  expression.@type = JsonLdExpression
  expression.@baseType = Expression
  expression.iri matches the referenced OptimisationSpecification.expressionSpecification.iri
expression.expressionValue against the referenced ACTIVE OptimisationSpecification.targetEntitySchema
expression.expressionValue.@context contains the required optimiser ontology mappings
expression.expressionValue.@type = opt:OptimisationProblem
expression.expressionValue.context shape
expression.expressionValue.context.targets[] entries
expression.expressionValue.context.constraints[] entries
expression.expressionValue.context.preferences[] entries
cardinality and allowed values defined by targetEntitySchema
```

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

Cancellation uses the same event type with `instruction = CANCEL`. Worker terminal outcomes are returned through `OptimisationCompletedEvent` with `status = COMPLETED`, `FAILED`, `INFEASIBLE`, or `CANCELLED`.

## 13. Internal event baseline:

OC MS uses exactly two internal Kafka event types with the Python/Gurobi worker in the current baseline. These are platform-internal events, not TMF external notification events.

| **Event** | **Emitter** | **Consumer** | **Purpose** | **Key values** |
|---|---|---|---|---|
| `OptimisationRequestedEvent` | OC MS / OC MS Outbox Relay | Python/Gurobi Worker | Worker instruction event for execution or cancellation. | `instruction = EXECUTE` or `instruction = CANCEL` |
| `OptimisationCompletedEvent` | Python/Gurobi Worker | OC MS / OC MS Inbox Consumer | Terminal worker outcome event for lifecycle/result projection. | `status = COMPLETED`, `FAILED`, `INFEASIBLE`, or `CANCELLED` |

`OptimisationFailedEvent` is not used in the current baseline. Failed, infeasible, and cancelled outcomes are carried by `OptimisationCompletedEvent.status`.

Event identity and idempotency requirements:

```text
OptimisationRequestedEvent and OptimisationCompletedEvent MUST include optimisationId.
OptimisationRequestedEvent and OptimisationCompletedEvent MUST include correlationId and traceId.
OptimisationRequestedEvent and OptimisationCompletedEvent MUST include a unique eventId or CloudEvents ce-id.
OptimisationCompletedEvent processing MUST be idempotent.
OC MS projection MUST safely handle duplicate OptimisationCompletedEvent messages.
OC MS may use eventId/ce-id, inbox deduplication state, and monotonic lifecycle/statusChangeDate rules to suppress duplicate, stale, or late event projection.
```

## 14. GET /optimisation list:

Request:

```http
GET /optimisation?lifecycleStatus=PROCESSING&fields=id,href,lifecycleStatus,statusChangeDate
```

Supported first-level filters:

| Query parameter | Meaning |
|---|---|
| `id` | Exact match on runtime Optimisation id. |
| `lifecycleStatus` | Exact match on runtime lifecycle state. |
| `sourceContext.domain` | Exact match on source context domain where present. |
| `sourceContext.resource.id` | Exact match on source resource id where present. |
| `optimisationSpecification.id` | Exact match on referenced OptimisationSpecification id. |
| `creationDate.gt` / `creationDate.lt` | Optional creation timestamp range filters. |
| `lastUpdate.gt` / `lastUpdate.lt` | Optional last-update timestamp range filters. |
| `statusChangeDate.gt` / `statusChangeDate.lt` | Optional lifecycle-state-change timestamp range filters. |
| `fields` | Optional sparse fieldset projection. |

Unsupported or malformed query parameters return `400 Bad Request`.

Sparse field projection rule:

```text
fields supports top-level fields only in the baseline. Nested field selection is not supported.
If a requested field is valid but not present for the resource's current lifecycle state, OC MS omits that field silently rather than returning an error.
For example, fields=id,result on a PROCESSING resource returns id and omits result because result is not present before terminal outcome projection.
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

`X-Total-Count` reflects the total number of resources matching the applied filters before paging and sparse field projection. `X-Result-Count` reflects the number of resources returned in the current response page.

## 15. GET /optimisation/{id}:

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
  "optimisationSpecification": {
    "id": "os-7f3a9c21",
    "href": "/optimisationSpecification/os-7f3a9c21",
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
  "result": {
    "outcome": "SUCCESS",
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
If a request body is supplied, it may contain optional reason/comment metadata only.
A supplied cancellation body does not change cancellation semantics, worker instruction meaning, or lifecycle eligibility.
```

Cancellation semantics:

```text
Cancellation is best-effort.
OC MS accepts cancellation only for eligible non-terminal lifecycle states.
CANCELLED is set only after worker confirmation through OptimisationCompletedEvent or an equivalent terminal confirmation path.
If cancellation is requested when lifecycleStatus is terminal (COMPLETED, FAILED, INFEASIBLE, or CANCELLED), OC MS returns 409 Conflict.
```

Retrial request body:

```text
No request body is required.
Baseline retrial does not allow request overrides.
Retrial resubmits the original accepted expression and referenced OptimisationSpecification.id unchanged.
To change targets, constraints, preferences, source context, priority, or the referenced OptimisationSpecification, the caller must create a new Optimisation request rather than using retrial.
```

Retrial response creates a new Optimisation and links it to the failed optimisation:

```json
{
  "id": "opt-67890",
  "href": "/optimisation/opt-67890",
  "lifecycleStatus": "ACKNOWLEDGED",
  "statusChangeDate": "2026-05-02T04:00:00Z",
  "optimisationRelationship": [
    {
      "@type": "EntityRelationship",
      "relationshipType": "retrialOf",
      "id": "opt-12345",
      "@referredType": "Optimisation"
    }
  ]
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
stale/wrong If-Match -> 412
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
Unsupported request content type returns 415 Unsupported Media Type.
```

## 18. Error handling boundary:

| **Condition** | **Response** |
|---|---|
| Missing or mismatched `optimisationSpecification.id`, `expression.iri`, or referenced `targetEntitySchema` contract failure | `422 Unprocessable Entity` |
| Referenced `OptimisationSpecification` is missing or not visible | `404 Not Found` |
| Referenced `OptimisationSpecification` is not `ACTIVE` | `422 Unprocessable Entity` |
| Cancellation/retrial requested in an invalid lifecycle state | `409 Conflict` |
| Cancellation requested for a terminal lifecycle state | `409 Conflict` |
| Missing `If-Match` on cancellation/retrial | `428 Precondition Required` |
| Stale or wrong `If-Match` on cancellation/retrial | `412 Precondition Failed` |
| Unsupported `Content-Type` | `415 Unsupported Media Type` |
| Malformed JSON, malformed query parameter, or unsupported query parameter | `400 Bad Request` |

Boundary rules:

```text
422 = request/expression/OD targetEntitySchema contract violation, including missing `optimisationSpecification.id`, missing `expression.iri`, or mismatch between `expression.iri` and the referenced specification's `expressionSpecification.iri`.
409 = runtime lifecycle/action conflict.
428 = required If-Match missing.
412 = supplied If-Match does not match current ETag.
415 = unsupported request media type.
400 = malformed request or unsupported query/filter parameter.
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
  "message": "The submitted Optimisation request does not satisfy the referenced ACTIVE OptimisationSpecification contract, including required optimisationSpecification.id, expression.iri, expressionSpecification.iri matching, and targetEntitySchema validation.",
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

```text
SUCCESS -> COMPLETED
INFEASIBLE -> INFEASIBLE
FAILURE -> FAILED
CANCELLED -> CANCELLED
```

`INFEASIBLE` is an optimisation outcome produced by the worker/model. It is not a request contract validation error.
