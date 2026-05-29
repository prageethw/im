# Intent Definition MS Solution Brief

## Summary:

Intent Definition MS (ID MS) is the definition-time microservice responsible for the `IntentSpecification` catalogue, version governance, lifecycle governance, syntax contract publication, and external `IntentSpecification` event subscription model. ID MS is the authoritative owner of `IntentSpecification` resources under `/intentManagement/v5/intentSpecification`.

It defines what runtime intent expressions are allowed to look like, which specification versions are available for new runtime intent creation, and which lifecycle/version rules protect active and retired specifications. ID MS is deliberately not the runtime intent owner. It does not own runtime `Intent`, `IntentReport`, semantic validation, policy validation, network feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

Those responsibilities remain with IC MS, II MS, IA MS, ICB MS, optimiser components, and knowledge/assurance services as applicable. The service follows the TMF921 `IntentSpecification` responsibility boundary while retaining documented platform extensions for deterministic full update, domain-scoped hub routes, spec-key version governance, HATEOAS links, optimistic concurrency, and explicit missing-precondition errors.

## Logical View:
![alt text](id_ms_logical_view.svg)
ID MS sits in the Intent Domain as the definition-time contract service.

```text
External client / OEX / authorised platform
  |
  | REST over NGW / API Gateway
  v
Intent Definition MS (ID MS)
  |
  | owns
  v
IntentSpecification catalogue
IntentSpecification lifecycle state
IntentSpecification spec-key version governance
IntentSpecification hub subscriptions
External IntentSpecification REST webhook notification delivery
```

ID MS exposes REST APIs for `IntentSpecification` resources and domain-scoped subscription resources. IC MS and other authorised consumers may retrieve active specifications from ID MS to validate runtime intent creation and to discover the governed expression contract.

Core logical resources are:

| Resource | Purpose |
|---|---|
| `IntentSpecification` | Definition-time contract describing allowed runtime intent expression structure and governance metadata. |
| `EventSubscription` | External listener subscription for ID MS `IntentSpecification` event notifications. |
| Specification key | Logical spec key grouped by `specKey`. |
| Specification version | Individual governed `IntentSpecification` version with its own lifecycle state. |

## Process View:
![alt text](intent_definition_ms_sequence.svg)
The primary ID MS process flows are:

1. Create a new draft `IntentSpecification`.
2. Retrieve or list specifications for discovery and runtime validation support.
3. Update an editable draft specification using preferred full replacement or tightly controlled partial update.
4. Activate a draft specification version through lifecycle update.
5. Retire the previous active specification in the same `specKey` during activation.
6. Delete an unused draft specification where retention and runtime-reference rules allow it.
7. Create, retrieve, and delete external event subscriptions.
8. Deliver external `IntentSpecification` event notifications by REST webhook callback after successful resource changes.

Activation is a lifecycle update on the resource, not a custom action endpoint. The service must not expose `POST /intentManagement/v5/intentSpecification/{id}/activate`. Strict TMF-compatible clients may use `PATCH`; the preferred platform extension is `PUT` when the caller submits the full resource representation.

## Solution Elaboration:

ID MS manages the definition-time contract used by the intent platform. A specification defines the governed expression shape, high-level characteristic catalogue, metadata, lifecycle status, version identity, related parties, and schema references used by downstream intent creation and validation flows.

The baseline surgical hospital slice specification uses:

- `@type: IntentSpecification`
- `@baseType: EntitySpecification`
- `specKey` for spec-key version governance
- `specCharacteristic` as a high-level characteristic catalogue
- `expressionSpecification` as the expression contract reference
- `targetEntitySchema` as the governed schema artefact reference for the expression-value shape
- `priority` values of `critical`, `high`, and `standard`
- canonical `context.targets`, `context.constraints`, and `context.preferences` semantics in the expression model

ID MS validates resource structure, required fields, lifecycle rules, and syntax/schema references. It does not decide whether a submitted runtime intent is semantically feasible or fulfillable in the network. Semantic and policy validation belongs to II MS and the knowledge plane. Runtime assurance belongs to IA MS.

## Responsibilities:

ID MS is responsible for:

| Area | Responsibility |
|---|---|
| Specification catalogue | Create, list, retrieve, update, activate, retire, and delete governed `IntentSpecification` resources. |
| Syntax contract | Publish the definition-time syntax and schema references used for runtime intent expression validation. |
| Version governance | Enforce `specKey`, unique versions, active-version selection, and previous-active retirement. |
| Lifecycle governance | Enforce `DRAFT`, `ACTIVE`, and `RETIRED` lifecycle states and allowed transitions. |
| Mutability control | Allow material update only while the specification is `DRAFT`. |
| Concurrency | Enforce strong `ETag` / `If-Match` behaviour on unsafe operations. |
| Subscription management | Manage external `IntentSpecification` event subscriptions through domain-scoped hub routes. |
| External events | Deliver TMF-aligned external resource-event notifications to registered hub subscriber callback URLs after successful specification changes. |
| Retrieval support | Allow IC MS and authorised consumers to retrieve active specifications for runtime validation and discovery. |

## ID MS does not:

ID MS does not:

- own runtime `Intent` resources;
- own `IntentReport` resources;
- validate runtime semantic feasibility;
- validate network topology or fulfilment feasibility;
- perform policy fulfilment decisions;
- perform optimisation;
- own runtime assurance or telemetry history;
- ingest change-execution callbacks;
- interpret callback state;
- expose internal II MS, IA MS, KP, optimiser, or callback implementation details through external `IntentSpecification` events;
- use `DELETED` as an `IntentSpecification.lifecycleStatus`;
- publish external hub notifications to Kafka topics.

## Response classification headers:

The service returns response classification headers on external REST API responses so callers can distinguish strict TMF-native behaviour from documented platform-extension behaviour.

These are response headers only. Clients do not send these headers in requests.

| **Response header** | **Meaning** |
|---|---|
| `X-TMF-Native: true` | The response is for a TMF-native operation/behaviour. |
| `X-TMF-Native: false` | The response is for an operation/behaviour that includes platform-specific semantics. |
| `X-Platform-Extension: true` | The route, method, response, or behaviour includes a documented platform extension. |
| `X-Platform-Extension: false` | No platform extension is used for the response. |

Use canonical header casing in examples:

```http
X-TMF-Native: true
X-Platform-Extension: false
```

or:

```http
X-TMF-Native: false
X-Platform-Extension: true
```


## Contracts:

ID MS exposes two contract families:

| Contract key | Contract |
|---|---|
| Resource API | REST API for `IntentSpecification` lifecycle and version management. |
| Hub API | Domain-scoped hub API for external `IntentSpecification` event subscriptions. |

The hub API is a REST webhook subscription model. Subscribers register callback URLs, and ID MS delivers matching `IntentSpecification` event notifications by HTTP `POST` to those callback URLs. Kafka is not used for hub notification delivery.

The platform base path is:

```http
/intentManagement/v5
```

Strict TMF-compatible gateway routing may map deployment-specific external prefixes to the platform-owned service path without changing resource semantics.

## Request shape / event shape:

### IntentSpecification resource API:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create specification | `POST` | `/intentManagement/v5/intentSpecification` |
| List specifications | `GET` | `/intentManagement/v5/intentSpecification` |
| Retrieve specification by ID | `GET` | `/intentManagement/v5/intentSpecification/{id}` |
| Full replace DRAFT candidate | `PUT` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Partial update or activate DRAFT candidate | `PATCH` | `/intentManagement/v5/intentSpecification/draft/{draftId}` |
| Retire current ACTIVE specification | `DELETE` | `/intentManagement/v5/intentSpecification/{id}` |

### Hub subscription API:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/intentSpecification/hub` |
| Retrieve subscription by ID | `GET` | `/intentManagement/v5/intentSpecification/hub/{id}` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/intentSpecification/hub/{id}` |

Domain-scoped hub routes are intentional platform extensions. Strict TMF exposure may use a generic root `/hub` route at the gateway layer where required.

## PATCH semantics:

`PATCH` uses JSON Merge Patch semantics across the service's external REST API.

All `PATCH` requests must use:

```http
Content-Type: application/merge-patch+json
```

`PATCH` is intended for small targeted updates. For deterministic full replacement of editable Draft resources, use `PUT` where the platform extension is available.


## IntentSpecification versioning clarification:

`IntentSpecification.version` is a design-time contract version and is separate from runtime `Intent.version`.

A mutable DRAFT `IntentSpecification` candidate does not expose an official public `version`. Draft revision is represented by `ETag`. ID MS assigns the official design-time contract `version` only when the selected DRAFT candidate is activated.

Baseline:

- `POST /intentSpecification` creates a mutable DRAFT candidate.
- `specKey` is mandatory on create and is used by ID MS to resolve the stable server-assigned `IntentSpecification.id`.
- ID MS assigns a new `draftId` for each mutable DRAFT candidate.
- DRAFT candidate retrieval, update, activation, and deletion use `/intentSpecification/draft/{draftId}`.
- Material change after activation requires a new mutable DRAFT candidate.
- `ACTIVE` and `RETIRED` specifications are immutable for material contract changes.
- Runtime `Intent.version` and `IntentSpecification.version` are separate concepts.


## Expression schema alignment:

Intent domain expression schemas should align with the TMF Intent Ontology direction and use a scalable JSON-LD-style structure.

Preferred governed `expression.expressionValue` shape:

```json
{
  "@context": {
    "intent": "https://example.com/tio/hospital-surgical-slice/v1.0#",
    "context": "intent:context",
    "targets": "intent:targets",
    "constraints": "intent:constraints",
    "preferences": "intent:preferences"
  },
  "@type": "HospitalSurgicalSliceIntentExpressionValue",
  "context": {
    "targets": [],
    "constraints": [],
    "preferences": []
  }
}
```

Baseline:

- `targetEntitySchema` owns the detailed validation contract.
- `expressionSpecification.iri` identifies the semantic/expression contract.
- `specCharacteristic` gives catalogue/discovery summary only.
- Use array-based `targets`, `constraints`, and `preferences` for scalability.
- Keep simplified object-map examples only where they are deliberately explanatory.


## Field specification:

### IntentSpecification fields:

| Field | Baseline use |
|---|---|
| `id` | Server-generated unique specification identifier. |
| `href` | Server-generated resource URI. |
| `specKey` | Mandatory create-time key used to resolve the stable server-assigned `IntentSpecification.id` and group related official versions. |
| `name` | Human-readable specification name. |
| `description` | Definition-time description of the specification purpose. |
| `version` | Official public specification version, assigned only when a selected DRAFT candidate is activated. |
| `lifecycleStatus` | One of `DRAFT`, `ACTIVE`, or `RETIRED`. |
| `isBundle` | Indicates whether the specification is a bundle. |
| `validFor` | Validity period metadata. |
| `relatedParty` | Provider or other related-party metadata. |
| `specCharacteristic` | High-level characteristic catalogue for discovery/governance. |
| `expressionSpecification` | Authoritative expression contract reference. |
| `targetEntitySchema` | Governed expression-value schema reference. |
| `@type` | `IntentSpecification`. |
| `@baseType` | `EntitySpecification`. |
| `@schemaLocation` | Schema location for the specification resource, where supplied. |
| `_links` | Server-generated lifecycle-aware navigation/action affordances. |

### Lifecycle values:

```text
DRAFT
ACTIVE
RETIRED
```

There is no `DELETED` lifecycle state. Delete is an operation/outcome, not a lifecycle status.

### Query parameters:

| Parameter | Applies to | Purpose |
|---|---|---|
| `offset` | List | Zero-based result offset for pagination. |
| `limit` | List | Maximum number of results returned. |
| `fields` | Create, list, retrieve, update | Optional TMF-aligned field selection/projection. |
| `lifecycleStatus` | List | Filter specifications by lifecycle state. |
| `name` | List | Filter specifications by name. |
| `version` | List | Filter specifications by version. |

## Fields not accepted:

Clients must not provide server-generated or lifecycle/version values on create:

- `id`
- `href`
- `draftId`
- official `version`
- `lifecycleStatus`
- `creationDate`
- `lastUpdate`
- `statusChangeDate`
- `Location`
- `ETag`
- `_links`

Clients must not use or submit `DELETED` as a lifecycle status.

`PATCH` must not normally be used for material replacement of:

- `specKey`
- `version`
- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`
- major lifecycle/version contract identity

## Authorisation:

ID MS is externally reached through the platform gateway/security boundary. The gateway authenticates the caller and forwards trusted system context according to platform policy.

ID MS must authorise callers for specification management operations and subscription management operations. It must enforce resource-level and lifecycle-level rules independently of gateway authentication.

| Operation type | Authorisation expectation |
|---|---|
| Read/list specifications | Caller must be authorised to discover/read definition-time contracts. |
| Create/update draft specifications | Caller must be authorised for specification governance/change. |
| Activate specifications | Caller must be authorised for governed lifecycle promotion. |
| Delete draft specifications | Caller must be authorised for controlled deletion and the resource must be unused. |
| Manage hub subscriptions | Caller must be authorised to register, inspect, or remove external listener subscriptions. |

## Persistence / state / outbox model:

ID MS requires durable persistence for:

| Store | Purpose |
|---|---|
| `IntentSpecification` store | Source of truth for specification resources, versions, lifecycle state, and schema references. |
| Spec-key version index | Efficient lookup and enforcement of one active version per `specKey`. |
| Subscription store | Source of truth for domain-scoped hub subscriptions. |
| Audit/history store | Retention of lifecycle and governance evidence, especially for active/retired specifications. |
| Hub delivery outbox store | Durable ID MS-owned callback delivery work for external `IntentSpecification` event notifications after committed resource changes. |

The implementation should create hub delivery work from committed state. Resource mutation and notification delivery should be resilient to retry, duplicate delivery, and transient subscriber callback failures.

## Hub notification delivery:

ID MS uses `/intentSpecification/hub` as a REST webhook subscription mechanism. Subscribers register callback URLs and optional filters. After a committed `IntentSpecification` resource change, ID MS delivers matching `IntentSpecification` event notifications by HTTP `POST` to the registered subscriber callback URL.

The delivery model is a TMF-aligned subscriber listener callback. Kafka is not used for ID MS hub notification delivery. There is no ID MS self-publish/self-consume Kafka loop and no dedicated Kafka topic for these external hub notifications. ID MS is both the event originator and the delivery owner.

Events are external subscription notifications for specification-resource changes. They must not expose internal fulfilment, KP, optimiser, assurance, telemetry, callback, or candidate/resource scoring details.

Supported external event types are:

```text
IntentSpecificationCreateEvent
IntentSpecificationAttributeValueChangeEvent
IntentSpecificationStatusChangeEvent
IntentSpecificationDeleteEvent
```

## Delivery reliability:

ID MS handles hub notification reliability through an ID MS-owned local delivery outbox and retry relay. Resource mutation and delivery work creation should be based on committed state so that subscriber callback delivery can be retried without changing the committed `IntentSpecification` outcome.

Registered subscribers receive notifications through REST webhook callback delivery only. They do not subscribe to Kafka topics and do not receive Kafka transport metadata.

## Event identity:

External ID MS events use TMF-aligned event identity fields:

| Field | Purpose |
|---|---|
| `eventId` | Unique event identifier. |
| `eventTime` | Canonical event occurrence timestamp. |
| `timeOccurred` | Platform-corrected spelling of event occurrence timestamp, aligned to `eventTime`. |
| `eventType` | Event type name. |
| `correlationId` | Correlation identifier for tracing the change flow. |
| `description` | Human-readable event description. |
| `priority` | Event priority, normally `Normal`. |
| `title` | Human-readable event title. |
| `event` | Event payload containing the `intentSpecification` snapshot. |
| `reportingSystem` | ID MS reporting system identity. |
| `source` | ID MS source identity. |
| `@type` | Event type. |

`eventTime` and `timeOccurred` should carry the same canonical occurrence timestamp.

## Webhook HTTP request:

ID MS hub notification delivery is an outbound HTTP callback to the subscriber listener URL registered through `/intentSpecification/hub`.

```http
POST https://subscriber.example.com/tmf-callbacks/intent-specification-status-change-event HTTP/1.1
Content-Type: application/json
X-Correlation-Id: corr-intent-spec-status-001
```

Subscriber callback authentication is deployment-specific and should use the configured subscriber credential or gateway-mediated callback authentication model. The webhook request is not a Kafka message and does not require Kafka transport metadata or CloudEvents headers.

## Webhook HTTP headers:

| Header | Purpose |
|---|---|
| `Content-Type: application/json` | Identifies the event notification payload format. |
| `X-Correlation-Id` | Carries the correlation identifier for tracing the change flow and callback delivery. |
| `Authorization` | Optional subscriber callback credential where configured by the platform/subscriber contract. |

## Webhook request body:

A typical `IntentSpecificationStatusChangeEvent` webhook body has this logical shape:

```json
{
  "eventId": "evt-intent-spec-status-001",
  "eventTime": "2026-04-18T12:10:00+10:00",
  "timeOccurred": "2026-04-18T12:10:00+10:00",
  "eventType": "IntentSpecificationStatusChangeEvent",
  "correlationId": "corr-intent-spec-status-001",
  "description": "IntentSpecification lifecycle status changed.",
  "priority": "Normal",
  "title": "IntentSpecification status changed",
  "event": {
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.20",
      "specKey": "hospital-surgical-slice-spec",
      "name": "Hospital Surgical Slice Intent Specification",
      "version": "1.20",
      "lifecycleStatus": "ACTIVE",
      "isBundle": false,
      "validFor": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      },
      "@type": "IntentSpecification",
      "@baseType": "EntitySpecification"
    }
  },
  "reportingSystem": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "source": {
    "id": "intent-definition-ms",
    "name": "Intent Definition MS"
  },
  "@type": "IntentSpecificationStatusChangeEvent"
}
```

Status-change events carry the current `intentSpecification.lifecycleStatus` snapshot. They do not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields; the event type and the emitted resource snapshot provide the lifecycle-change signal.

Delete events are emitted only after successful delete and show the last known lifecycle state as `DRAFT`. Delete events must not use `DELETED`.

## Behaviour:

### Create behaviour:

- Create produces a mutable `DRAFT` candidate and assigns a `draftId`.
- ID MS validates resource shape and required syntax/schema references.
- ID MS resolves `id` from `specKey` and generates `draftId`, DRAFT `href`, `Location`, `ETag`, and `_links`.
- Successful create returns `201 Created` with the full created DRAFT candidate resource.
- Successful create emits `IntentSpecificationCreateEvent`.

### List behaviour:

- List supports pagination, lifecycle filtering, name filtering, version filtering, and `fields` projection.
- The default list response is lightweight.
- Full `specCharacteristic`, `expressionSpecification`, and `targetEntitySchema` are omitted by default unless requested through `fields`.
- List GET may use short private caching.

### Retrieve behaviour:

- Retrieve returns the full single-resource representation by default.
- Retrieve includes full contract metadata, lifecycle state, schema references, and `_links`.
- Retrieve GET may use private caching.
- Clients may request a fresh response with `Cache-Control: no-cache`.

### Full update behaviour:

- `PUT` is the preferred platform extension for deterministic full replacement of an editable `DRAFT` specification.
- `PUT` requires `If-Match`.
- `ACTIVE` and `RETIRED` specifications cannot be materially updated.
- Missing `If-Match` returns `428 Precondition Required`.
- Stale or mismatched `If-Match` returns `412 Precondition Failed`.

### Partial update behaviour:

- `PATCH` remains available for TMF compatibility.
- `PATCH` is discouraged as a general update method.
- `PATCH` should be used only for tightly controlled small compatibility updates.
- `PATCH` must not normally replace material contract fields.

### Activation behaviour:

- Activation is a lifecycle update on `/intentSpecification/draft/{draftId}`.
- Only `DRAFT` can be activated.
- The activated version becomes `ACTIVE`.
- The previous `ACTIVE` version in the same `specKey` becomes `RETIRED`.
- New runtime intent creation must use the new active specification.
- Existing runtime intents referencing retired specifications may continue temporarily where safe.
- Activation emits two `IntentSpecificationStatusChangeEvent` events:
  - one for the newly activated specification version with `lifecycleStatus: ACTIVE`;
  - one for the previous active specification version with `lifecycleStatus: RETIRED`.

### Delete behaviour:

- Delete is allowed only for unused `DRAFT` specifications.
- Delete is blocked for `ACTIVE` and `RETIRED` specifications.
- Delete is blocked where runtime references or audit/history dependencies require retention.
- Delete requires `If-Match`.
- Successful delete returns `204 No Content`.
- Delete emits `IntentSpecificationDeleteEvent` only after successful delete.

### Hub notification behaviour:

- `/intentSpecification/hub` creates, retrieves, and deletes REST webhook subscriptions.
- ID MS stores subscriber callback URLs and subscription filters in its own subscription store.
- After a committed specification change, ID MS creates local delivery outbox work for matching subscriptions.
- An ID MS-owned retry relay delivers the event by HTTP `POST` to each subscriber listener callback URL.
- Kafka is not used for hub delivery. There is no ID MS self-publish/self-consume Kafka loop for external notifications.

## Configuration:

ID MS configuration should include:

| Configuration area | Purpose |
|---|---|
| Allowed lifecycle states | `DRAFT`, `ACTIVE`, `RETIRED`. |
| Mutability policy | Material update allowed only for `DRAFT`. |
| Spec-key version rule | Only one active version per `specKey` for new runtime intent creation. |
| Cache policy | GET-only private caching, with bounded TTLs. |
| Concurrency policy | Unsafe operations require `If-Match`. |
| Hub route policy | Domain-scoped `/intentSpecification/hub` routes retained as platform extension for REST webhook subscription delivery. |
| Event filter policy | Supported `IntentSpecification` event types and subscription filters for REST webhook delivery. |
| Schema registry / governed artefact references | Validation of `expressionSpecification` and `targetEntitySchema` references. |

## Consumer contract:

Consumers of ID MS should rely on these behaviours:

- IC MS retrieves active `IntentSpecification` resources to validate new runtime intent creation.
- New runtime intents must reference an `ACTIVE` specification.
- `DRAFT` and `RETIRED` specifications must not be used for new runtime intent creation.
- Consumers must treat `ACTIVE` and `RETIRED` specification contracts as immutable.
- Consumers should use `fields` where a lightweight response is sufficient.
- Consumers must use `If-Match` for unsafe updates and deletes.
- Event subscribers receive only external `IntentSpecification` event notifications through REST webhook callbacks and not internal workflow details.

## Open items:

| Item | Status |
|---|---|
| Exact schema registry implementation for `targetEntitySchema.@schemaLocation` and `schemaHash` | Implementation detail to be finalised. |
| Physical versus logical delete for unused drafts | Implementation detail; external outcome remains `204 No Content` and no `DELETED` lifecycle state. |
| Exact governance approval workflow before activation | Business/process implementation detail; activation rules require governance completion where applicable. |

## Closed items:

| Decision | Baseline |
|---|---|
| ID MS owns `IntentSpecification` only | Closed. Runtime `Intent` and `IntentReport` are IC MS concerns. |
| Lifecycle values | Closed: `DRAFT`, `ACTIVE`, `RETIRED`. |
| No `DELETED` lifecycle state | Closed. Delete is operation/outcome only. |
| `PUT` support | Closed. `PUT` is an approved platform extension for deterministic full replacement of editable drafts. |
| `PATCH` position | Closed. Supported for TMF compatibility but discouraged generally. |
| Activation endpoint | Closed. No custom `/activate`; use lifecycle update through `PUT` or `PATCH`. |
| Spec key | Closed. Use `specKey`; only one active version per specKey for new runtime creation. |
| Hub delivery model | Closed. `/intentSpecification/hub` uses REST webhook subscriber listener callback delivery backed by an ID MS-owned local delivery outbox; Kafka is not used for external hub notification delivery. |
| Event family | Closed. `IntentSpecificationCreateEvent`, `IntentSpecificationAttributeValueChangeEvent`, `IntentSpecificationStatusChangeEvent`, and `IntentSpecificationDeleteEvent`. |
| Event timestamp spelling | Closed. Use both `eventTime` and corrected `timeOccurred` with the same canonical occurrence timestamp. |
| Priority vocabulary | Closed. Use `critical`, `high`, `standard`; do not use `clinical-critical`. |
| Base type | Closed. Use `@baseType: EntitySpecification`. |

## MS identity:

| Item | Baseline |
|---|---|
| Full name | Intent Definition MS |
| Short name | ID MS |
| Service name | `intent-definition-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `IntentSpecification` |
| Primary responsibility | Definition-time `IntentSpecification` catalogue, lifecycle/version governance, syntax contract, and external REST webhook specification-event notifications. |
