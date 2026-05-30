# Intent Controller MS Solution Brief

## Summary:

Intent Controller MS (IC MS) is the TMF-compliant runtime intent controller for the Intent Enabler. It owns the external `Intent` and `IntentReport` resource boundary, supports Draft runtime Intent authoring through the approved `submit` request-control extension, admits schema and request-shape valid submitted runtime intent requests, projects external lifecycle/status state, and publishes curated external runtime intent events.

IC MS is deliberately not the owner of semantic validation, optimisation, callback ingestion, change execution, or runtime assurance truth.

Its main purpose is to provide a stable external runtime API and event projection layer while delegating deeper decisioning, change handling, and assurance responsibilities to the appropriate downstream services. External consumers may author and edit Draft Intents, but they do not control lifecycle state. `lifecycleStatus`, `statusReason`, and `statusChangeDate` are owned by the intent management entity and projected externally by IC MS based on IC/IA outcomes.

## Logical View:

IC MS sits between external intent consumers, the definition-time specification catalogue, and the internal intent fulfilment pipeline.

It is the runtime API and projection boundary for `Intent` and `IntentReport`; it is not the owner of semantic interpretation, optimisation, callback ingestion, change execution, or runtime assurance truth.

![alt text](ic_ms_logical_view.svg)

```text
External consumer / OEX -> platform gateway -> IC MS -> ID MS
External consumer / OEX -> platform gateway -> IC MS -> Intent projection store
IC MS -> internal_event_outbox -> Kafka -> II MS
II MS / IA MS -> Kafka -> IC MS -> Intent / IntentReport projection store
IC MS -> webhook_delivery_outbox -> HTTP POST -> external subscriber listener callback
```

| Area | IC MS position |
|---|---|
| External API boundary | Owns `/intentManagement/v5/intent`, `/intentManagement/v5/intent/{id}`, nested `IntentReport` read APIs, and intent event hub subscription APIs. |
| Primary resource | `Intent`. |
| Secondary resource | `IntentReport`. |
| Upstream dependency | ID MS for `ACTIVE` `IntentSpecification` validation using mandatory `intentSpecification.id`, with mandatory `expression.iri` checked against the selected specification's `expressionSpecification.iri`. |
| Internal event path | Emits admitted runtime intent state through `IntentValidatedEvent` using the IC MS internal event outbox and Kafka relay. |
| Downstream event consumers | II MS consumes admitted runtime intent state through `IntentValidatedEvent`. |
| Downstream status inputs | II MS rejection outcomes and IA MS assurance outcomes drive IC MS external lifecycle/status projection. |
| External event subscribers | Receive TMF-aligned `Intent` and `IntentReport` events through REST webhook subscriber listener callbacks registered via the IC MS hub subscription model. |
| External notification path | Uses `webhook_delivery_outbox` and HTTP `POST`; Kafka is not used for external hub notification delivery. |

IC MS owns the externally visible runtime projection, not the full internal fulfilment state machine. The external `Intent` record is the current consumer-facing state of the runtime intent. Draft authoring records are pre-admission authoring records only and do not drive `activeVersion`. Draft Intents are not assigned a permanent runtime version; Draft authoring revision is represented by ETag, and a permanent runtime version is assigned only when the Draft is submitted and admitted. Historical versions, standby states, rollback candidates, internal resource candidates, optimiser scoring, and raw assurance detail remain internal unless projected through `IntentReport` or another documented platform extension.

## Process View:

![alt text](intent_creation_ms_sequence.svg)

### Runtime intent creation and Draft authoring:

1. A consumer sends `POST /intentManagement/v5/intent` with a runtime `Intent` request.
2. IC MS validates the basic TMF resource shape.
3. If `submit: false` is supplied, IC MS persists the Intent as `Draft`. If `isBundle` is omitted, IC MS defaults it to `false`.
4. A Draft Intent is an authoring record only; it is not admitted, optimised, assured, sent to downstream change execution, or used to drive `activeVersion`.
5. If `submit` is omitted on initial create, IC MS treats the request as `submit: true`.
6. If `submit: true` is supplied or defaulted, IC MS checks that the request carries both mandatory `intentSpecification.id` and mandatory `expression.iri`.
7. IC MS resolves the exact `ACTIVE` `IntentSpecification` using mandatory `intentSpecification.id`.
8. IC MS confirms the request `expression.iri` matches the selected specification's `expressionSpecification.iri`, then validates the runtime expression/request shape against the resolved `ACTIVE` definition owned by ID MS.
9. If validation fails, IC MS returns a structured error such as `422 VALIDATION_FAILED`.
10. If validation succeeds, IC MS persists the external `Intent` projection, includes the server-resolved `isBundle` value, and sets the initial projected lifecycle state to `Acknowledged`.
11. IC MS emits `IntentValidatedEvent` as an internal state/progress event.
12. Downstream services continue semantic interpretation, optimisation where applicable, change preparation, apply, callback interpretation, and assurance.
13. IC MS consumes downstream outcome/projection events and updates the external `Intent` and `IntentReport` views.

### Runtime intent Draft update and submitted-version change:

1. A consumer may update an existing Draft projection using `PUT` or `PATCH` only while the current Intent/Draft projection is in `Draft`.
2. Unsafe update operations require `If-Match`.
3. IC MS applies optimistic concurrency using the current ETag.
4. For a Draft Intent, all attributes accepted by the `PUT` / `PATCH` request contract are mutable.
5. The request contract does not expose `lifecycleStatus` as writable.
6. `id` is immutable. If `id` appears in a full-replacement `PUT`, it must match the path `id` and is used only for consistency checking.
7. If `submit` is omitted while the current Intent is already Draft, the Intent remains Draft.
8. If `submit: true` is supplied, IC MS validates the runtime admission profile and, if accepted, moves the projected lifecycle to `Acknowledged`.
9. Once an Intent leaves Draft, general attribute update on that submitted version is not allowed.
10. Material changes after submission require creating a new Draft authoring record, editing that Draft version, and explicitly submitting it.
11. IC MS projects the current runtime version externally while retaining internal version history for audit and traceability.

A new runtime version must not be created while there is already a newer candidate version in `Acknowledged` or `InProgress`. Draft authoring records are not admitted runtime candidates and do not drive `activeVersion`.

When a newer version becomes `activeVersion`, the previous version transition rule is:

| Previous version state | Transition when newer version becomes `activeVersion` |
|---|---|
| `Active` | `Standby` |
| `Degraded` | `Standby` |
| `Paused` | `Standby` |
| `Rejected` | `Terminated` |
| `Failed` | `Terminated` |

`Standby` versions must re-enter the Intent version change lifecycle through `Acknowledged`, then `InProgress`, before they can become `Active` again. `Retired` is reachable only from `Terminated`.

### Runtime intent termination:

1. A consumer requests termination using `DELETE /intentManagement/v5/intent/{id}`.
2. `DELETE` is treated as runtime termination, not physical deletion.
3. IC MS retains the runtime record for audit, reporting, lifecycle history, and traceability.
4. IC MS projects the lifecycle state as `Terminated`.
5. IC MS emits `IntentDeleteEvent` to represent accepted termination.

### IntentReport projection:

1. IA MS owns runtime assurance truth.
2. IC MS consumes curated assurance outcomes and creates/updates `IntentReport` projections.
3. External consumers can list and retrieve `IntentReport` records.
4. Ordinary external consumers do not delete `IntentReport` records.
5. Governed internal/admin purge may remove reports and emit `IntentReportDeleteEvent` when policy allows.

### Hub notification delivery:

1. A subscriber registers a callback URL through the strict TMF `/hub` route or the accepted domain-scoped `/intent/hub` platform extension.
2. IC MS stores the subscription, callback URL, optional filter/query, and delivery metadata.
3. When a subscribed `Intent` or `IntentReport` event occurs, IC MS creates the TMF-aligned event payload.
4. IC MS writes webhook delivery work to its own local delivery outbox.
5. The IC MS delivery relay posts the event payload to the subscriber listener callback URL using HTTP `POST`.
6. The subscriber listener acknowledges delivery with an HTTP success response, normally `204 No Content`, where aligned to TMF listener behaviour.
7. IC MS retries failed callback deliveries according to the delivery policy.

Kafka is not used for external hub notification delivery.

IC MS does not create a self-publish/self-consume Kafka loop for hub notifications, in which it is both the event originator and the delivery owner.

## Solution Elaboration:

IC MS is the runtime equivalent of a controlled authoring, admission, and projection layer. It can persist Draft Intents for authoring when `submit: false` is supplied. It accepts submitted runtime intent requests only when the incoming payload is structurally valid, carries mandatory `intentSpecification.id`, carries mandatory `expression.iri`, and passes the consistency check against the selected `ACTIVE` `IntentSpecification`.

It does not interpret whether the intent is semantically achievable, feasible, optimal, policy-compliant, or currently assured.

The design intentionally separates these concerns:

| Concern | Owner |
|---|---|
| Runtime API admission and external projection | IC MS |
| Intent definition/specification contract | ID MS |
| Semantic interpretation and network-ready preparation | II MS |
| Optimisation | Optimiser services |
| Network change execution | Change execution layer / network orchestrator |
| Callback ingestion | ICB MS |
| Callback interpretation and runtime assurance truth | IA MS |

IC MS therefore exposes a stable TMF-compliant resource API while avoiding leakage of internal fulfilment mechanics.

It is responsible for Draft authoring control, correct external lifecycle/status representation, consumer-safe reports, event subscription handling, ETag concurrency, and error consistency. External consumers request draft/save versus submission through `submit`; they do not assign lifecycle state.

## Responsibilities:

IC MS is responsible for:

| Responsibility | Description |
|---|---|
| Runtime `Intent` API | Create, list, retrieve, replace, patch, and terminate runtime intents. |
| Draft Intent authoring | Persist and update Draft Intents using the `submit` request-control extension without admitting them to downstream processing. |
| Runtime schema and request-shape validation | Validate submitted runtime intent request shape against the `ACTIVE` `IntentSpecification` selected by mandatory `intentSpecification.id`, with mandatory `expression.iri` checked against the selected specification's `expressionSpecification.iri`. |
| Initial admission | Persist schema and request-shape valid submitted requests and project `Acknowledged`. |
| Internal progress publication | Emit `IntentValidatedEvent` after schema and request-shape validation succeeds. |
| External lifecycle projection | Own consumer-facing `Intent.lifecycleStatus`, `statusReason`, and `statusChangeDate`; external consumers cannot set or patch these fields. |
| Runtime version projection | Return the current projected runtime version externally while retaining internal version history; Draft authoring records do not drive `activeVersion`. |
| `IntentReport` projection | Expose read-only curated report/projection history derived from assurance outcomes. |
| Event subscription | Support strict TMF `/hub` and domain-scoped `/intent/hub` subscription routes. |
| External event delivery | Deliver consumer-safe TMF-aligned `Intent` and `IntentReport` event notifications by REST webhook callback to subscriber listener URLs. |
| Concurrency control | Enforce ETag / `If-Match` on unsafe state-changing operations. |
| Common error shape | Return the shared platform REST error body. |

## IC MS does not:

IC MS does not own:

| Not owned by IC MS | Owning component |
|---|---|
| `IntentSpecification` design-time catalogue | ID MS |
| Semantic validation | II MS |
| Policy validation | II MS and Knowledge Plane support |
| Knowledge resolution | II MS and Knowledge Plane support |
| Optimisation | Optimiser services |
| Network change execution | Change execution layer / network orchestrator |
| Apply outcome interpretation | IA MS |
| Runtime assurance truth | IA MS |
| Real-time telemetry | Telemetry platform consumed by IA MS |
| Callback ingestion | ICB MS |
| Raw orchestrator callback interpretation | IA MS |
| Raw candidate and resource scoring exposure | Internal optimiser/assurance pipeline only |

IC MS also does not resolve an `IntentSpecification` by `expression.iri` alone, `specKey`, name, key, or inferred expression shape alone. Submitted runtime create and update admission requests must include both `intentSpecification.id` and `expression.iri`. `intentSpecification.id` selects the exact ACTIVE platform-managed specification. `expression.iri` identifies the semantic/expression contract and must match the selected specification's `expressionSpecification.iri`. `intentSpecification.specKey` and `intentSpecification.name` are optional hints only.

IC MS does not allow external consumers to set or patch `lifecycleStatus`; lifecycle state is assigned and projected by the intent management entity.

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

When `submit` is omitted and the default create-admission behaviour is used without extension fields, a response may be classified as TMF-native where no platform-extension semantics are invoked. When `submit` is supplied, Draft behaviour is used, or admission control depends on the `submit` request-control extension, classify the response as a platform extension.


## Contracts:

### Intent resource APIs:

| Purpose | Method | Endpoint | Position |
|---|---:|---|---|
| Create runtime intent | `POST` | `/intentManagement/v5/intent` | TMF-compliant |
| List runtime intents | `GET` | `/intentManagement/v5/intent` | TMF-compliant |
| Retrieve runtime intent by ID | `GET` | `/intentManagement/v5/intent/{id}` | TMF-compliant |
| Full replace runtime intent | `PUT` | `/intentManagement/v5/intent/{id}` | Platform extension |
| Partial update runtime intent | `PATCH` | `/intentManagement/v5/intent/{id}` | TMF-compliant |
| Terminate runtime intent | `DELETE` | `/intentManagement/v5/intent/{id}` | TMF-compliant delete verb; platform behaviour is termination, not physical deletion |

### IntentReport APIs:

| Purpose | Method | Endpoint | Position |
|---|---:|---|---|
| List reports for intent | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport` | Platform/TMF-compliant nested report projection |
| Retrieve report by ID | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport/{id}` | Platform/TMF-compliant nested report projection |

Ordinary external consumers do not receive a public `DELETE /intentManagement/v5/intent/{intentId}/intentReport/{id}` capability. Governed internal/admin purge may exist, but is not exposed through NGW/public consumer APIs by default.

### Hub subscription APIs:

Strict TMF route form:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/hub` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/hub/{id}` |

Accepted domain-scoped platform extension:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create intent event subscription | `POST` | `/intentManagement/v5/intent/hub` |
| Retrieve intent event subscription | `GET` | `/intentManagement/v5/intent/hub/{id}` |
| Delete intent event subscription | `DELETE` | `/intentManagement/v5/intent/hub/{id}` |

The hub routes register REST webhook subscribers. They are not Kafka subscription APIs.

## PATCH semantics:

`PATCH` uses JSON Merge Patch semantics across the service's external REST API.

All `PATCH` requests must use:

```http
Content-Type: application/merge-patch+json
```

`PATCH` is intended for small targeted updates. For deterministic full replacement of editable Draft resources, use `PUT` where the platform extension is available.


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
- Use the canonical `targets`, `constraints`, and `preferences` semantic buckets consistently; concrete schemas may specialise whether each bucket uses object-map entries or array entries.
- Keep simplified object-map examples only where they are deliberately explanatory.


## Request shape:

A runtime intent create and update request uses the following baseline:

| Field | Requirement |
|---|---|
| `name` | Consumer-facing runtime intent name. |
| `description` | Optional descriptive text. |
| `humanExpression` | Human-readable expression of the requested outcome. |
| `submit` | Optional IC MS extension request-control field. `false` saves or keeps Draft; `true` submits for admission. If omitted on initial create, the request is treated as submitted. If omitted on an existing Draft, Draft handling is preserved. |
| `intentSpecification.id` | Mandatory for submitted admission; selects the exact ACTIVE platform-managed specification used for validation, governance, and audit. |
| `expression.iri` | Mandatory for submitted admission; identifies the semantic/expression contract and must match the selected specification's `expressionSpecification.iri`. |
| `intentSpecification.specKey` | Optional descriptive/discovery hint; not an authoritative validation key. |
| `intentSpecification.name` | Optional descriptive/discovery hint; not an authoritative validation key. |
| `expression` | Required TMF-compliant `JsonLdExpression`. |
| `expression.expressionValue.context.targets` | Required measurable outcome/SLA objectives where defined by the specification. |
| `expression.expressionValue.context.constraints` | Required or optional hard constraints as defined by the specification. |
| `expression.expressionValue.context.preferences` | Optional soft selection guidance as defined by the specification. |
| `isBundle` | Optional runtime bundle flag. Defaults to `false` when omitted on create; persisted responses include the server-resolved value. |
| `priority` | Runtime priority where applicable. |
| `relatedParty` | Requester/customer/operator party references where applicable. |
| `validFor` | Runtime validity window where applicable. |
| `@type` | `Intent`. |
| `@baseType` | `Entity`. |

Top-level `priority` is an API and platform processing priority used by IC MS and platform controls. `expression.expressionValue.context.constraints.priority` is a domain fulfilment constraint interpreted by downstream semantic validation, policy, optimisation, and assurance components. When both are present, they should normally be consistent, but they are not the same field.

Example explicit specification reference:

```json
{
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec",
    "version": "1.20"
  },
  "expression": {
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  }
}
```

IRI-only admission is not supported. This request is rejected because `intentSpecification.id` is missing:

```json
{
  "expression": {
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  }
}
```

`intentSpecification.specKey` and `intentSpecification.name` may be supplied as optional descriptive/discovery hints, but they are not mandatory and are not authoritative validation keys.

## Field specification:

### Runtime Intent projection fields:

| Field | Meaning |
|---|---|
| `id` | Server-generated runtime intent identifier. |
| `href` | Canonical resource URL. |
| `name` | Runtime intent name. |
| `description` | Consumer-facing description. |
| `humanExpression` | Human-readable request. |
| `submit` | Request-control extension indicating draft/save versus submission handling. |
| `version` | Current projected runtime version. |
| `lifecycleStatus` | Current projected external lifecycle status. |
| `statusReason` | Human-readable reason for current projected status. |
| `statusChangeDate` | Timestamp for the latest projected status change. |
| `intentSpecification` | Specification reference. `id` is mandatory for submitted admission; `specKey` and `name` are hints only. |
| `expression` | Runtime intent expression using `JsonLdExpression`. |
| `validFor` | Runtime validity period. |
| `isBundle` | Server-resolved bundle indicator. |
| `priority` | Consumer/platform priority. |
| `relatedParty` | Party references. |
| `_links` | Hypermedia controls for valid next actions. |
| `@type` | `Intent`. |
| `@baseType` | `Entity`. |

### Intent-level lifecycleStatus values:

The Intent-level `lifecycleStatus` is the externally visible lifecycle projection for the `Intent` resource. It normally reflects the current `activeVersion` and keeps TMF-compliant external consumers insulated from internal version history.

```text
Draft
Acknowledged
InProgress
Active
Degraded
Paused
Rejected
Failed
Terminated
```

![alt text](ic_ms_intent_lifecycle_state_diagram.svg)

### Intent-version lifecycleStatus values:

The Intent-version-level `lifecycleStatus` is the lifecycle truth for each individual runtime version. It supports version history, rollback/restart, audit, and governance.

```text
Draft
Acknowledged
InProgress
Active
Degraded
Paused
Standby
Rejected
Failed
Terminated
Retired
```

![alt text](ic_ms_intent_version_lifecycle_state_diagram.svg)

External `GET /intent/{id}` returns the current projected `Intent` state. It does not return the full internal version aggregate by default.

### Draft and update rules:

| Rule | Baseline |
|---|---|
| Draft authoring | `submit: false` saves or keeps an Intent as `Draft`. |
| Initial submit default | If `submit` is omitted on initial create, IC MS treats the request as submitted for admission. |
| Draft submit persistence | If an Intent is already persisted with `submit: false`, later omission of `submit` preserves Draft handling and does not automatically submit the Intent. |
| Submit Draft | `submit: true` requests admission. IC MS validates the runtime admission profile and, if accepted, projects `Acknowledged`. |
| Draft editability | While `lifecycleStatus = Draft`, all attributes accepted by the `PUT` / `PATCH` request contract are mutable. |
| Immutable identity | `id` is immutable; if included in `PUT`, it must match the path `id`. |
| Lifecycle ownership | `lifecycleStatus` is not writable through create and update contracts; it is assigned and projected by the intent management entity. |
| Bundle defaulting | `isBundle` is optional in request bodies and defaults to `false` when omitted on create; persisted responses include the server-resolved value. |
| Submitted-version update | Once an Intent leaves Draft, general attribute update on that submitted version is not allowed. Material changes require a new Draft authoring record. |

### Intent-version lifecycle rules:

| Rule | Baseline |
|---|---|
| New version gating | Do not create another newer version while there is already a newer candidate version in `Acknowledged` or `InProgress`. |
| Draft version behaviour | Draft authoring records are editable pre-admission authoring records and do not drive `activeVersion`. |
| New version becomes `activeVersion` after previous `Active` / `Degraded` / `Paused` | Previous version moves to `Standby`. |
| New version becomes `activeVersion` after previous `Rejected` / `Failed` | Previous version moves to `Terminated`. |
| Standby reactivation | `Standby -> Acknowledged -> InProgress -> Active`. |
| Retirement | Only `Terminated -> Retired`; no direct `Standby`, `Failed`, or `Rejected` to `Retired`. |
| Retired | Administrative/version-governance archival state, not a runtime/network operational state. |

### IntentReport projection fields:

| Field | Meaning |
|---|---|
| `id` | Report identifier. |
| `href` | Canonical report URL. |
| `creationDate` | Report creation timestamp. |
| `name` | Consumer-facing report name. |
| `intent` | Parent runtime intent reference. |
| `expression` | Curated report content using `JsonLdExpression`. |
| `_links` | Hypermedia links to self, parent intent, and list route. |
| `@type` | `IntentReport`. |
| `@baseType` | `Entity`. |

## Fields not accepted:

IC MS should reject or ignore unsupported external request fields according to the strictness of the endpoint contract.

| Field / pattern | Reason |
|---|---|
| `intentSpecification.specKey` as the authoritative validation key | IC MS does not resolve runtime requests by specKey alone; it is only an optional hint. |
| `intentSpecification.name` as the authoritative validation key | IC MS does not resolve runtime requests by display name alone; it is only an optional hint. |
| Missing `expression.iri` | Submitted admission must include `expression.iri` so IC MS can validate the semantic/expression contract against the selected specification. |
| Inferred specification from payload shape alone | IC MS must resolve the ACTIVE validation contract by mandatory `intentSpecification.id`, with mandatory `expression.iri` checked against the selected specification. |
| Internal optimiser candidate sets | Not part of the external runtime create and update contract. |
| Raw Knowledge Plane facts | Not accepted through IC MS runtime APIs. |
| Raw telemetry observations | IA MS consumes telemetry; IC MS exposes curated projections only. |
| Raw orchestrator callback payloads | ICB MS ingests callbacks; IA MS interprets them. |
| Consumer-supplied lifecycle/status projection authority | IC MS owns external lifecycle/status projection. |
| Consumer-supplied `lifecycleStatus` in create and update | Lifecycle state is assigned and projected by the intent management entity; external consumers use `submit`, not `lifecycleStatus`, to request draft/save versus admission. |
| Missing `isBundle` in create and update request | Not an error. IC MS defaults omitted `isBundle` to `false` on create and preserves the persisted/server-resolved value on Draft updates unless explicitly changed. |
| Consumer-supplied `IntentReport` mutation fields | Reports are curated projection/audit resources. |
| String placeholders for object/array fields in examples or payloads | Typed placeholder rule requires object placeholders for objects and array placeholders for arrays. |

## Authorisation:

IC MS is exposed through the platform gateway boundary and must enforce standard platform access controls before accepting runtime intent operations.

Authorisation responsibilities include:

| Area | Behaviour |
|---|---|
| Runtime intent create and update/delete | Only authorised external consumers or platform actors can create, update Draft Intents, submit Draft Intents, or terminate runtime intents. |
| Report read access | Consumers can only read reports they are authorised to access. |
| Hub subscription management | Only authorised subscribers can create or delete event subscriptions. |
| Internal event consumption | Internal consumers use service-to-service identity and platform trust controls. |
| Admin-only report purge | Governed internal/admin capability only, not ordinary external consumer capability. |

IC MS must not expose internal semantic, optimisation, assurance, or callback interpretation data simply because a caller can read an external `Intent` resource. Resource access and projection safety remain separate responsibilities.

## Persistence / state model:

IC MS persists external runtime intent projections, runtime version metadata, hub subscriptions, webhook delivery work, and curated `IntentReport` projections.

### Intent projection state:

| State item | Purpose |
|---|---|
| Runtime intent record | External canonical `Intent` projection, including Draft authoring records where `submit: false` is used. |
| Current projected version | Version returned by standard `GET /intent/{id}`; Draft authoring records do not drive `activeVersion`. |
| Lifecycle/status fields | `lifecycleStatus`, `statusReason`, `statusChangeDate`, assigned and projected by the intent management entity. |
| ETag/version token | Optimistic concurrency for unsafe operations. |
| Internal version history | Audit and traceability; not returned by default external GET. |
| Correlation identifiers | Trace lifecycle and downstream outcome handling. |

### IntentReport projection state:

| State item | Purpose |
|---|---|
| Report record | Read-only curated assurance/lifecycle report. |
| Parent intent reference | Associates report with runtime intent. |
| Report expression | Consumer-safe assurance and lifecycle summary. |
| ETag/version token | Supports GET caching and governed admin operations. |
| Retention metadata | Supports policy-governed purge/admin removal where required. |

### Hub subscription state:

| State item | Purpose |
|---|---|
| Subscription ID | Stable event subscription identifier. |
| Callback URL | Subscriber-owned listener endpoint. |
| Query/filter | Event filter expression such as `eventType=IntentStatusChangeEvent`. |
| ETag/version token | Required for unsafe delete where baselined. |
| Subscription metadata | Audit and operational support. |

### Webhook delivery outbox state:

| State item | Purpose |
|---|---|
| Delivery ID | Stable delivery work identifier. |
| Subscription ID | Links the notification to the subscriber registration. |
| Event payload | TMF-aligned event body to send to the subscriber listener. |
| Callback URL | Resolved subscriber listener URL. |
| Delivery status | Tracks pending, delivered, retrying, and failed delivery work. |
| Retry metadata | Retry count, next retry time, and last error information. |

## Event delivery paths:

IC MS has two distinct event-delivery paths. The two paths must not be collapsed into a single Kafka or webhook model.

| Delivery path | Purpose | Transport | Durability model | Headers | Payload |
|---|---|---|---|---|---|
| Internal platform event publication | Notify independent internal microservice consumers that runtime intent admission or another internal milestone has occurred. | Kafka. | IC MS internal event outbox and Kafka relay. | CloudEvents-style Kafka/platform event headers. | Internal event JSON body, for example `IntentValidatedEvent`. |
| External TMF/webhook notification delivery | Notify registered external subscribers about consumer-safe `Intent` and `IntentReport` events. | HTTP `POST` to subscriber listener callback URL. | IC MS webhook delivery outbox and HTTP retry relay. | HTTP headers. | TMF-aligned event request body, for example `IntentStatusChangeEvent`. |

## Internal Kafka event publication:

IC MS publishes internal state/progress events through the platform Kafka event backbone where an independent internal consumer exists.

| Event category | Purpose | Transport | Primary consumer |
|---|---|---|---|
| `IntentValidatedEvent` | Internal state/progress event emitted after schema and request-shape validation succeeds. | Kafka. | II MS / `intent-intelligence-ms`. |

`IntentValidatedEvent` is not a point-to-point command. It states that an `Intent` has passed IC MS schema and request-shape validation and has been admitted into the runtime lifecycle. IC MS writes the event to its internal event outbox, and the internal event relay publishes it to Kafka using the platform event header model.

## External hub notification delivery:

External `Intent` and `IntentReport` notifications are delivered to subscriber listener callback URLs through the hub subscription model. They are not delivered to external subscribers through Kafka.

| Delivery target | Event usage | Transport |
|---|---|---|
| Subscriber callback URL | External event delivery target configured through `/hub` or `/intent/hub`; the URL is subscriber-owned; notification payloads follow TMF-aligned event patterns so subscribers can use common TMF listener conventions. | HTTP `POST`. |

IC MS writes webhook delivery work to a local webhook delivery outbox and an HTTP delivery relay posts the TMF-aligned event body to the subscriber listener callback URL.

Kafka is not used for external hub notification delivery. External events must not expose raw telemetry, raw optimiser decisions, raw Knowledge Plane data, raw callback payloads, internal candidate scoring, or internal Kafka payloads.

## Event identity:

External IC MS events use a TMF-aligned event resource shape.

| Field | Meaning |
|---|---|
| `eventId` | Stable event identifier for idempotency/deduplication. |
| `eventTime` | Canonical event occurrence timestamp. |
| `timeOccurred` | Corrected spelling used consistently across the baseline; same timestamp semantics as TMF `timeOcurred`. |
| `eventType` | Event type name. |
| `correlationId` | Correlates event with request/workflow. |
| `description` | Human-readable event description. |
| `priority` | Event priority. |
| `title` | Human-readable event title. |
| `event` | Event payload wrapper containing `intent` or `intentReport`. |
| `changedAttributes` | Optional curated attribute-delta array used by attribute-value-change events only; must not expose raw telemetry, internal optimiser scoring, callback payloads, or implementation-only detail. |
| `reportingSystem` | IC MS reporting system identity. |
| `source` | IC MS source identity. |
| `@type` | Event type. |

External event names include:

```text
IntentCreateEvent
IntentAttributeValueChangeEvent
IntentStatusChangeEvent
IntentDeleteEvent
IntentReportCreateEvent
IntentReportAttributeValueChangeEvent
IntentReportDeleteEvent
```

`IntentReportDeleteEvent` is included for TMF vocabulary alignment but is emitted only after governed internal/admin removal where notification is allowed by policy.

`IntentAttributeValueChangeEvent` and `IntentReportAttributeValueChangeEvent` may include a curated `changedAttributes` array inside the event payload wrapper. This is an external projection aid for safe attribute deltas, not a channel for raw telemetry, internal optimiser scoring, callback payloads, or implementation-only detail.

Status-change events carry the current `intent.lifecycleStatus` snapshot in the `event.intent` payload. They do not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields in the external event payload. The event type, timestamp, and emitted resource snapshot provide the lifecycle-change signal.

## Internal Kafka CloudEvents headers:

For internal Kafka event backbone delivery, IC MS should use the common platform CloudEvents envelope where applicable.

These headers apply to internal Kafka events such as `IntentValidatedEvent`; they do not apply to external webhook notifications.

Typical CloudEvents headers include:

| Header | Meaning |
|---|---|
| `ce-specversion` | CloudEvents specification version. |
| `ce-id` | Stable event ID. |
| `ce-source` | Producing service, typically `intent-controller-ms`. |
| `ce-type` | Event type, such as `IntentValidatedEvent`. |
| `ce-time` | Event occurrence timestamp. |
| `ce-subject` | Runtime intent identifier where applicable. |
| `ce-correlationid` | Correlation identifier for tracing. |
| `content-type` | Event payload content type, usually `application/json`. |

External TMF-aligned subscriber callbacks are REST webhook notifications. They carry HTTP headers and a REST request body rather than Kafka-style CloudEvents headers.

## Internal Kafka message body:

### IntentValidatedEvent:

`IntentValidatedEvent` is emitted only after IC MS has persisted the admitted external `Intent` projection.

Canonical message intent:

```json
{
  "eventId": "evt-intent-validated-001",
  "eventType": "IntentValidatedEvent",
  "source": "intent-controller-ms",
  "correlationId": "corr-intent-create-001",
  "eventTime": "2026-04-18T12:00:00+10:00",
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "intentVersion": "v1",
    "lifecycleStatus": "Acknowledged",
    "intentSpecification": {
      "id": "ispec-hss-001",
      "specKey": "hospital-surgical-slice-spec",
      "version": "1.20"
    },
    "expression": {
      "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "hospital",
            "geographicScope": "campus"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true,
          "timeWindow": {
            "startDateTime": "2026-04-18T12:00:00+10:00"
          }
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    },
    "references": {
      "intent": {
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "href": "/intentManagement/v5/intentSpecification/ispec-hss-001?version=1.20"
      }
    }
  }
}
```

## Webhook HTTP request:

External hub notifications are sent as HTTP `POST` requests to the subscriber listener callback URL registered through `/hub` or `/intent/hub`.

```http
POST https://subscriber.example.com/tmf-callbacks/intent-events HTTP/1.1
Content-Type: application/json
X-Correlation-Id: corr-intent-status-001
```

## Webhook HTTP headers:

Webhook notifications use HTTP headers, not Kafka CloudEvents headers.

| Header | Purpose |
|---|---|
| `Content-Type: application/json` | Indicates the event body is JSON. |
| `X-Correlation-Id` | Carries the correlation identifier for tracing where configured. |
| `Authorization` or subscriber-specific credential | Used only where the subscriber callback contract requires callback authentication. |

## Webhook request body:

### External IntentStatusChangeEvent:

```json
{
  "eventId": "evt-intent-status-001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "timeOccurred": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentStatusChangeEvent",
  "correlationId": "corr-intent-status-001",
  "description": "Intent lifecycle status changed.",
  "priority": "Normal",
  "title": "Intent status changed",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v2",
      "lifecycleStatus": "Active",
      "@type": "Intent",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentStatusChangeEvent"
}
```

## Behaviour:

### Validation behaviour:

| Scenario | Behaviour |
|---|---|
| Invalid JSON or malformed request | Return `400 BAD_REQUEST`. |
| Missing `intentSpecification.id` on submitted admission | Return `422 VALIDATION_FAILED` with reason `INTENT_SPECIFICATION_ID_REQUIRED`. |
| Missing `expression.iri` | Return `422 VALIDATION_FAILED` with reason `EXPRESSION_IRI_REQUIRED`. |
| Runtime `expression.iri` does not match selected specification `expressionSpecification.iri` | Return `422 VALIDATION_FAILED` with reason `INTENT_EXPRESSION_IRI_MISMATCH`. |
| Referenced specification is not ACTIVE | Return `422 VALIDATION_FAILED` or `INTENT_SPECIFICATION_NOT_ACTIVE`. |
| Active specification cannot be confirmed | Return `503 SERVICE_UNAVAILABLE` with retry guidance where applicable. |
| `submit: false` supplied | Persist `Intent` as `Draft`; do not emit `IntentValidatedEvent`; do not optimise, assure, or send to downstream change execution. |
| `submit` omitted on initial create | Treat as submitted for admission. |
| Existing Draft updated with `submit` omitted | Preserve Draft handling; do not submit automatically. |
| `submit: true` supplied | Validate runtime admission profile; if accepted, persist/project `Acknowledged` and emit `IntentValidatedEvent`. |

### Update and concurrency behaviour:

| Scenario | Behaviour |
|---|---|
| Unsafe operation missing required `If-Match` | Return `428 PRECONDITION_REQUIRED` with reason `IF_MATCH_REQUIRED`. |
| Stale or mismatched ETag | Return `412 PRECONDITION_FAILED` with reason `ETAG_MISMATCH`. |
| Draft PUT/PATCH | Allowed while the current Intent/Draft projection is `Draft`; all request-contract attributes are mutable. |
| Submitted-version PUT/PATCH | Not allowed for general attribute update; material change requires a new Draft authoring record. |
| Newer candidate already exists | Reject/defer another newer version while the existing candidate is `Acknowledged` or `InProgress`. |
| `PATCH` usage | Supported for TMF compatibility while Draft, but `PUT` is preferred for deterministic full update. |

### Caching behaviour:

| Operation | Behaviour |
|---|---|
| GET list/retrieve | May use `Cache-Control: private, max-age=300` and `ETag` where applicable. |
| Fresh read | Client may send `Cache-Control: no-cache`. |
| Non-GET | No caching strategy baselined. |

### Delete/termination behaviour:

| Resource | Behaviour |
|---|---|
| `Intent` | `DELETE` means accepted termination, not physical deletion. |
| `IntentReport` | Ordinary external delete is not exposed by default. |
| Hub subscription | `DELETE` removes the subscription, requiring `If-Match` where baselined. |

### Webhook delivery behaviour:

| Scenario | Behaviour |
|---|---|
| Subscriber listener returns success | Mark delivery as delivered. |
| Subscriber listener is temporarily unavailable | Retry according to callback delivery policy. |
| Subscriber listener permanently fails or exceeds retry limit | Mark delivery failed and raise operational alert according to platform policy. |
| Subscriber callback URL is invalid or unauthorised | Reject subscription or disable delivery according to subscription policy. |

## Configuration:

IC MS configuration should include:

| Configuration area | Purpose |
|---|---|
| ID MS lookup endpoint | Resolve and validate the `ACTIVE` `IntentSpecification` by mandatory `intentSpecification.id`, then confirm `expression.iri` matches the selected specification's `expressionSpecification.iri`. |
| Allowed lifecycle transitions | Control valid projected state movement. |
| Draft and submit policy | Control `submit` defaulting, Draft persistence, Draft submission, and Draft-only editability. |
| Internal event topic binding | Publish `IntentValidatedEvent`. |
| Hub subscription policy | Control callback URL validation, event filters, and subscription lifecycle. |
| Webhook delivery policy | Control retry intervals, retry limit, timeout, and failed-delivery handling. |
| ETag/concurrency policy | Enforce `If-Match` on unsafe operations. |
| Report retention policy | Govern `IntentReport` retention and internal/admin purge. |
| Cache policy | Apply GET-only cache headers and fresh-read override. |
| Error catalogue | Maintain shared platform REST error body consistency. |

## Consumer contract:

External consumers can rely on IC MS to provide:

| Contract item | Guarantee |
|---|---|
| Stable runtime `Intent` API | TMF-compliant create, list, retrieve, update, patch, and termination routes. |
| Runtime validation discriminator | Submitted runtime requests must include both `intentSpecification.id` and `expression.iri`. |
| Draft authoring | Consumers can save and edit Draft Intents with `submit: false`; Drafts are not admitted or sent downstream. |
| External status projection | `lifecycleStatus`, `statusReason`, and `statusChangeDate` are IC MS-owned projections and are not externally writable. |
| Report read model | `IntentReport` is a read-only curated projection/audit resource for ordinary consumers. |
| Hypermedia links | Responses include links for valid next actions where applicable. |
| Optimistic concurrency | Unsafe operations use `If-Match` and ETag. |
| Submitted-version immutability | Once an Intent leaves Draft, consumers cannot patch arbitrary attributes on that submitted version; material change requires a new Draft authoring record. |
| External events | Subscribers receive consumer-safe TMF-aligned resource events through REST webhook callbacks. |
| No internal leakage | Raw telemetry, optimiser decisions, callback payloads, candidate scoring, and KP internals are not exposed in external events. |

Internal consumers can rely on `IntentValidatedEvent` as the admitted runtime intent handoff, not as a command targeted to a single service.

## Open items:

| Item | Status |
|---|---|
| Exact physical Kafka topic split for IC internal events | May be refined by deployment policy while preserving `IntentValidatedEvent` semantics. |
| Public exposure posture for TMF strict `/hub` versus domain-scoped `/intent/hub` | Both are baselined; gateway product exposure can choose supported route set. |
| Optional internal/admin `IntentReport` purge API details | Governed capability is allowed, but ordinary external consumer delete remains not exposed by default. |
| Full internal version-history retrieval API | Not exposed by default; can be defined later as a documented platform extension if needed. |
| Draft authoring record creation route/detail | New submitted-version changes are represented by a new Draft authoring record using a documented platform extension route or operation to be finalised. `PUT` and `PATCH` must not mutate an admitted runtime version. |

## Closed items:

| Item | Decision |
|---|---|
| IC MS service identity | Full name is `Intent Controller MS`; service name is `intent-controller-ms`. |
| Runtime create and update ACTIVE spec resolution | Submitted admission requires both `intentSpecification.id` and `expression.iri`; specKey and name are optional hints only. |
| IC MS validation scope | Schema and request-shape validation only for submitted requests; no semantic or optimisation ownership. |
| Initial admitted state | `Acknowledged` after submitted request admission; `Draft` when `submit: false` is used. |
| Internal handoff event | `IntentValidatedEvent`. |
| Hub notification delivery | REST webhook delivery to subscriber listener callback URLs; Kafka is not used for external hub delivery. |
| `DELETE /intent/{id}` behaviour | Termination, not physical deletion. |
| External event timestamp spelling | Use both `eventTime` and corrected `timeOccurred`. |
| `IntentReportDeleteEvent` posture | Event vocabulary retained for TMF alignment; emitted only after governed internal/admin removal. |
| Ordinary external `IntentReport` delete | Not exposed by default. |
| Missing `If-Match` | `428 PRECONDITION_REQUIRED`. |
| Stale/mismatched ETag | `412 PRECONDITION_FAILED`. |

## MS identity:

| Item | Baseline |
|---|---|
| Full name | Intent Controller MS |
| Short name | IC MS |
| Service name | `intent-controller-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `Intent` |
| Secondary resource | `IntentReport` |
| Primary responsibility | TMF-compliant runtime `Intent` controller, schema and request-shape admission, lifecycle/status projection, and external runtime intent events |
