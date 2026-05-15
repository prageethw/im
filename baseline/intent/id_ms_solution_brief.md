# Intent Definition MS Solution Brief

## Summary:

Intent Definition MS (ID MS) is the definition-time microservice responsible for the `IntentSpecification` catalogue, version governance, lifecycle governance, syntax contract publication, and external `IntentSpecification` event subscription model. ID MS is the authoritative owner of `IntentSpecification` resources under `/intentManagement/v5/intentSpecification`.

It defines what runtime intent expressions are allowed to look like, which specification versions are available for new runtime intent creation, and which lifecycle/version rules protect active and retired specifications. ID MS is deliberately not the runtime intent owner. It does not own runtime `Intent`, `IntentReport`, semantic validation, policy validation, network feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

Those responsibilities remain with IC MS, II MS, IA MS, ICB MS, optimiser components, and knowledge/assurance services as applicable. The service follows the TMF921 `IntentSpecification` responsibility boundary while retaining documented platform extensions for deterministic full update, domain-scoped hub routes, version-family governance, HATEOAS links, optimistic concurrency, and explicit missing-precondition errors.

## Logical View:

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
IntentSpecification version-family governance
IntentSpecification hub subscriptions
External IntentSpecification REST webhook notification delivery
```

ID MS exposes REST APIs for `IntentSpecification` resources and domain-scoped subscription resources. IC MS and other authorised consumers may retrieve active specifications from ID MS to validate runtime intent creation and to discover the governed expression contract.

Core logical resources are:

| Resource | Purpose |
|---|---|
| `IntentSpecification` | Definition-time contract describing allowed runtime intent expression structure and governance metadata. |
| `EventSubscription` | External listener subscription for ID MS `IntentSpecification` event notifications. |
| Specification family | Logical version family grouped by `familyId`. |
| Specification version | Individual governed `IntentSpecification` version with its own lifecycle state. |

## Process View:
![alt text](https://img.plantuml.biz/plantuml/png/vHdPRkD6yfrVKQi0WOt8akEPyIPUU17RqZZ2ZWzOKX8WdeSMsPGQRXxRtTG1Zu4yvGCM-uNvagrgaZeeYfAoUbXWPLWogBhlAl-W3LCc2IHqGiD30otkYr0O4OLmruKJwF9_9ZnqENoKqSJvYndnW4CicGWT_IB2c2aMWCw0xhZMRCYlf1Y6u28vhfQW1inz6Qee2RsRI4OAllfeNqiG-6w4As8MckiYiCVuTxwx0JXI7bSPuBdx7H_u9T9TAHLDCg1tzhK454Q6hv3npWVd7ywB44MfVDy_SvUbyiHO895rm5FwAP7g5g7YTV3lwSTnZ32Ib_lcgDF2ZsFuuxT_mwCI0LCp_8nSzC6grxJZCDSWrLfxYXu9cOGRAP3WSzY4X_Olq8Ihn8pWKJBZHoge0TCPXBDaPAZTt_vCi8yTk6M6JzZCGjx-l0fL9knpc4bhCJgjkwxZHb9obxxNEKutvkvpUCCCaz4muQaSLpt7moS3fZdK7X8pYARGOmF9aMRhEYNuqEzTF_oo1DTD1jfL8YRop-4J7mfjq3npX6x_-gbzkoftHhibTCoCE-8A6In25YQHUk4gHMzrkezNlPiVsqzhbiqu3mYzEzE61pb3nxcyX6yRSACuMW_k-GHQYla65ieBNxZCckpoqaaz02T_Hml31Jm-T7lG51RsZeMOPW7-rHn_o9wju3-7hn2oWDTXp9N61tNmMI3ahEFLGGgVkpDNygvX9j4NKBDorEhGQ3JWpK5so9ISX6mn82PCUQ0eehHno1enN9ae42wqhi4e5cfc_UW0lYmQegFV43icxjf0YCfwcvHTmKjTYQWJ9Gml0q_jrnwJSJ2XuHLqfiTZ-xxLkRz55NZeEId5t7ndfzzcblSGeyHacU8aUchutN2-VFdYBC9XHOCO8vpiDvUBvp9h9mCYTalO5_1hjSAV2xpIE4Oy6KKlw1Uz5FSQ0efZ4GvJnhrPp9qCOPtlwmekXOdBfAJuxoi9RvyTv11RRJXpHobfDCioalNZcdn8_CTUxx6R1l3h4jKtYb8hsiKMFzSn_7IKA9UJO4O468aiYD7yn999Ord0sNHg7z2BEAzfUNPw2W__cCDiy1jMqfU5hw3L_jJvgVtKRbayBh6-M6uSsud2UaZYH8cfvln-EaNG3_QzYB11316wokOuAa_5oyKoX2NxY4_ZACJ70giDMV8aylqwU9nv9v8RB4E0UORl0PjQJC7rSIew9WNzKXqwQy2J_MxCKQ9FbACbBj0bTUYslKyP0a0RMHIiBSrNuMqfBwlb0v-Hudb3W2DFQ3SQqyCcA3G7MXB6J0hFiZjs2EraGRqicpwJH1gp0lkguYws_BLAGK622Oynbs1ebTM58WJD1a22PK3rJ84dyaeKofdjqc44KTfaqkYY4eVoMOUyOmtuc4XvyiHnkd9Jn_TZZrh5KQouZ-66-MQRVRztJ8vPPvgfVOCvXaynDmDXD0PE46Day7aIuHz8KIDAMd-BdQQ_kuUjIocFVPHzmM0GURF3TXALckLWNUJAOFGF4iD_OZBXDoCM3XSzfRH_P3xVjNLKWc_h6d_y_gzvrzWewLvDP2ELRIrbtaHMUajL8oaqZiDrXCq-UtEgwdrLdLzKTvk5WmOyqb28jJLFljxTnnES7eLhm5AfphsU68wCf6eT6aKZhWU-uDBJG6NWRw1H8GWIhBS3Zi6HZO0qmV2rF2Hk-sTYdCcViJre5h8uHjro3abg8HFz7sMbnwKWjs-M5Cr1mNYaSVwcqVyTExQnzHw-WGyDk4BRZibigUU9Piq-mttd6rh48cm1HYYEonmVYoZHbV6MaIC5ne8jPllK_RcBAFOQk91mDHPOHE_wc7Zt3psWMGBd6Pk8rA0tnLMJPLB_rxq2ZR--V-JwO_pIk6pZddQHIjX3nhNcw3UcXlXX4xJ0TiLB9UYuwNeGv-vAuL924u6BjOs4VF-oj8XVBNMpLzipHqYabO1RB41vR7dPP7mGefcOzRc2XDZnDcnPcnEiRF5STUQ1K_LitaABsbNiNqNGexbDZ-jhT8uosnp_hpRHei3LFjYzXnvKW3mFwY2yY_Ke-xETVH1XwbanTA7BdpUWnUr4t0yJZTbIUOVPN7gbZ2Q8RUVxoOY7j6xHOePuN-VhoOaTtUqjJYMIQpg9u5HUhACeOBlNtg-KxhD9PKiINveti59zJIi9IyjLlaxDvTKEBTOU6OeqIkN6FB2LPLjvBHlW0pJYnXbXltALkcyn6UJhxOBAeYAzX_i8RY9Bn0Aibver42el5Qlvseo-98_5ssSoNyBzN7v2sQMKP9U77Sl9OIyrozvuooMflBxiDf7RMyiYfvgmcaiuy4Ho4K65tHy7S5_Yq5uI4-zFloTlsw_j5i-qRIfbmR49DZ-a_9NH9ONkorWWvbVWr1RBL-ZoIZ9tRiPFPPGqiBdBeF_qYOPAnLrEYUed9i7fC3qXaAlqSqYZNxQZuBe2pL4oe3D7d5tqSSv38-goNN_ZLHb9aDTpAR1EZuo9zKMpgUSdxWQVChejD54puS-mWjkB3SBEBuwNECTj7TRon9-R8xyRLrubwpXtIJHMFH_APtVSCFedGDerybp8cD8rjqWF0QlEn9KdqItducLS1BQnCbYwkcs9bLslRkYcFPf1rRquluQjMsxboBjXu2kekt6SApEBE-_7-ncbgcd-IRjaNMetkr294IhWwrFmIaFPqc-S7x2M987y3m00)
The primary ID MS process flows are:

1. Create a new draft `IntentSpecification`.
2. Retrieve or list specifications for discovery and runtime validation support.
3. Update an editable draft specification using preferred full replacement or tightly controlled partial update.
4. Activate a draft specification version through lifecycle update.
5. Retire the previous active specification in the same `familyId` during activation.
6. Delete an unused draft specification where retention and runtime-reference rules allow it.
7. Create, retrieve, and delete external event subscriptions.
8. Deliver external `IntentSpecification` event notifications by REST webhook callback after successful resource changes.

Activation is a lifecycle update on the resource, not a custom action endpoint. The service must not expose `POST /intentManagement/v5/intentSpecification/{id}/activate`. Strict TMF-compatible clients may use `PATCH`; the preferred platform extension is `PUT` when the caller submits the full resource representation.

## Solution Elaboration:

ID MS manages the definition-time contract used by the intent platform. A specification defines the governed expression shape, high-level characteristic catalogue, metadata, lifecycle status, version identity, related parties, and schema references used by downstream intent creation and validation flows.

The baseline surgical hospital slice specification uses:

- `@type: IntentSpecification`
- `@baseType: EntitySpecification`
- `familyId` for version-family governance
- `specCharacteristic` as a high-level characteristic catalogue
- `expressionSpecification` as the expression contract reference
- `targetEntitySchema` as the governed schema artefact reference for the expression-value shape
- `priority` values of `critical`, `high`, and `standard`
- canonical `context.targets`, `context.constraints`, and `context.preferences` semantics in the expression model

ID MS validates resource structure, required fields, lifecycle rules, and syntax/schema references. It does not decide whether a submitted runtime intent is semantically feasible or fulfilable in the network. Semantic and policy validation belongs to II MS and the knowledge plane. Runtime assurance belongs to IA MS.

## Responsibilities:

ID MS is responsible for:

| Area | Responsibility |
|---|---|
| Specification catalogue | Create, list, retrieve, update, activate, retire, and delete governed `IntentSpecification` resources. |
| Syntax contract | Publish the definition-time syntax and schema references used for runtime intent expression validation. |
| Version governance | Enforce `familyId`, unique versions, active-version selection, and previous-active retirement. |
| Lifecycle governance | Enforce `DRAFT`, `ACTIVE`, and `RETIRED` lifecycle states and allowed transitions. |
| Mutability control | Allow material update only while the specification is `DRAFT`. |
| Concurrency | Enforce strong `ETag` / `If-Match` behaviour on unsafe operations. |
| Subscription management | Manage external `IntentSpecification` event subscriptions through domain-scoped hub routes. |
| External events | Deliver TMF-style external resource-event notifications to registered hub subscriber callback URLs after successful specification changes. |
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
- ingest orchestrator callbacks;
- interpret callback state;
- expose internal II MS, IA MS, KP, optimiser, or callback implementation details through external `IntentSpecification` events;
- use `DELETED` as an `IntentSpecification.lifecycleStatus`;
- publish external hub notifications to Kafka topics.

## Contracts:

ID MS exposes two contract families:

| Contract family | Contract |
|---|---|
| Resource API | REST API for `IntentSpecification` lifecycle and version management. |
| Hub API | Domain-scoped hub API for external `IntentSpecification` event subscriptions. |

The hub API is a REST webhook subscription model. Subscribers register callback URLs, and ID MS delivers matching `IntentSpecification` event notifications by HTTP `POST` to those callback URLs. Kafka is not used for hub notification delivery.

The platform base path is:

```http
/intentManagement/v5
```

A strict TMF deployment may expose the same API through:

```http
/tmf-api/intentManagement/v5
```

The gateway may map the strict deployment prefix to the platform-owned service path without changing resource semantics.

## Request shape / event shape:

### IntentSpecification resource API:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create specification | `POST` | `/intentManagement/v5/intentSpecification` |
| List specifications | `GET` | `/intentManagement/v5/intentSpecification` |
| Retrieve specification by ID | `GET` | `/intentManagement/v5/intentSpecification/{id}` |
| Full replace specification | `PUT` | `/intentManagement/v5/intentSpecification/{id}` |
| Partial update specification | `PATCH` | `/intentManagement/v5/intentSpecification/{id}` |
| Delete specification | `DELETE` | `/intentManagement/v5/intentSpecification/{id}` |

### Hub subscription API:

| Purpose | Method | Endpoint |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/intentSpecification/hub` |
| Retrieve subscription by ID | `GET` | `/intentManagement/v5/intentSpecification/hub/{id}` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/intentSpecification/hub/{id}` |

Domain-scoped hub routes are intentional platform extensions. Strict TMF exposure may use a generic root `/hub` route at the gateway layer where required.

## Field specification:

### IntentSpecification fields:

| Field | Baseline use |
|---|---|
| `id` | Server-generated unique specification identifier. |
| `href` | Server-generated resource URI. |
| `familyId` | Groups related versions of the same specification family. |
| `name` | Human-readable specification name. |
| `description` | Definition-time description of the specification purpose. |
| `version` | Specification version within the family. |
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
| `fields` | Create, list, retrieve, update | Optional TMF-style field selection/projection. |
| `lifecycleStatus` | List | Filter specifications by lifecycle state. |
| `name` | List | Filter specifications by name. |
| `version` | List | Filter specifications by version. |

## Fields not accepted:

Clients must not provide server-generated values on create:

- `id`
- `href`
- `Location`
- `ETag`
- `_links`

Clients must not use or submit `DELETED` as a lifecycle status.

`PATCH` must not normally be used for material replacement of:

- `familyId`
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
| Version-family index | Efficient lookup and enforcement of one active version per `familyId`. |
| Subscription store | Source of truth for domain-scoped hub subscriptions. |
| Audit/history store | Retention of lifecycle and governance evidence, especially for active/retired specifications. |
| Hub delivery outbox store | Durable ID MS-owned callback delivery work for external `IntentSpecification` event notifications after committed resource changes. |

The implementation should create hub delivery work from committed state. Resource mutation and notification delivery should be resilient to retry, duplicate delivery, and transient subscriber callback failures.

## Hub notification delivery:

ID MS uses `/intentSpecification/hub` as a REST webhook subscription mechanism. Subscribers register callback URLs and optional filters. After a committed `IntentSpecification` resource change, ID MS delivers matching `IntentSpecification` event notifications by HTTP `POST` to the registered subscriber callback URL.

The delivery model is a TMF-style subscriber listener callback. Kafka is not used for ID MS hub notification delivery. There is no ID MS self-publish/self-consume Kafka loop and no dedicated Kafka topic for these external hub notifications. ID MS is both the event originator and the delivery owner.

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

External ID MS events use TMF-style event identity fields:

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
      "id": "hospital-surgical-slice-spec-v1.20",
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20",
      "familyId": "hospital-surgical-slice-spec",
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

- Create normally produces a `DRAFT` specification.
- ID MS validates resource shape and required syntax/schema references.
- ID MS generates `id`, `href`, `Location`, `ETag`, and `_links`.
- Successful create returns `201 Created` with the full created resource.
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

- Activation is a lifecycle update on `/intentSpecification/{id}`.
- Only `DRAFT` can be activated.
- The activated version becomes `ACTIVE`.
- The previous `ACTIVE` version in the same `familyId` becomes `RETIRED`.
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
| Version-family rule | Only one active version per `familyId` for new runtime intent creation. |
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
| Version family | Closed. Use `familyId`; only one active version per family for new runtime creation. |
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
