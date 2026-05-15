# Intent Definition MS Solution Brief

## Summary:

Intent Definition MS (ID MS) is the definition-time microservice responsible for the `IntentSpecification` catalogue, version governance, lifecycle governance, syntax contract publication, and external `IntentSpecification` event subscription model. ID MS is the authoritative owner of `IntentSpecification` resources under `/intentManagement/v5/intentSpecification`.

It defines what runtime intent expressions are allowed to look like, which specification versions are available for creating new runtime intents, and which lifecycle/version rules protect active and retired specifications. ID MS is deliberately not the runtime intent owner. It does not own runtime `Intent`, `IntentReport`, semantic validation, policy validation, network feasibility, optimisation, runtime assurance, telemetry, or callback ingestion.

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
External IntentSpecification event publication
```

ID MS exposes REST APIs for `IntentSpecification` resources and domain-scoped subscription resources.

IC MS and other authorised consumers may retrieve active specifications from ID MS to validate runtime intent creation and to discover the governed expression contract.

Core logical resources are:

| Resource | Purpose |
|---|---|
| `IntentSpecification` | Definition-time contract describing allowed runtime intent expression structure and governance metadata. |
| `EventSubscription` | External listener subscription for ID MS `IntentSpecification` event notifications. |
| Specification family | Logical version family grouped by `familyId`. |
| Specification version | Individual governed `IntentSpecification` version with its own lifecycle state. |

## Process View:

The primary ID MS process flows are:

1. Create a new draft `IntentSpecification`.
2. Retrieve or list specifications for discovery and runtime validation support.
3. Update an editable draft specification using preferred full replacement or tightly controlled partial update.
4. Activate a draft specification version through lifecycle update.
5. Retire the previous active specification in the same `familyId` during activation.
6. Delete an unused draft specification where retention and runtime-reference rules allow it.
7. Create, retrieve, and delete external event subscriptions.
8. Publish external `IntentSpecification` event notifications after successful resource changes.

Activation is a lifecycle update on the resource, not a custom action endpoint. The service must not expose `POST /intentManagement/v5/intentSpecification/{id}/activate`.

Strict TMF-compatible clients may use `PATCH`; the preferred platform extension is `PUT` when the caller submits the full resource representation.
![alt text](https://img.plantuml.biz/plantuml/png/xLZRJXn747sVhwWGoG9vsIKOi4r4v8K5Z68kOfVOKl13pqmFsw9tUjBTiu2GfJpb0w9yeRyaLTqpUvsz9SvR5i6YdkhggbEdBZtlZ6NQvZq9PwdbgOKMJqGgh50fdBTX4zhyjvod4OSJgHw2xsoNzpXaaeaqCFSYpPXcFJ25q3atXjtnfXHtAKIeZkiHgP15ztTQvMbyfAJIyFs9-un8u5yh8f6nr1vE2iUClqcY6S9AnrmNWdlH6nuc5TOrjLOFXT0hznaHIfNbOshYlN1lTszIOjAg94cser6hOj4Ng6HQS8j-AgmwHQbiMlmj_GI15LRowjYidxNmQmE-_luNN6dHO_e9lrM4CHYFcWa25bdKkdRyY159cOGZAL3XRTg0o-DFq81cRhjm9PbDbEwj0JE5H302CgnTd7vqpqu_ZgzNcNUR5lQv7MUjytOGAIbvHCzDkQUTyUWsFMAMINMNStzoinF4k18oms7jChUXUeGE2oL7dQr3h_3ofdDu-MdSZ4Aq9Kp6RDJb6kM7d8C7fU-vzjjRP-shPkVe_V5r41mSm0zrEDASMGuN_05QcYKMXWQAH4JCkNLm47XSOFCdH07suUgotO66SBBdB4Noz_2_Hd-tM1lRVvi-Gyfwl0PzhWqkr21XFI6Vpk8QI97mw2cIl6sPpSq-h3axrcfGhzVXIu37uQ4491wBONfWEWPDSJOsSClu6B73fnbfDnPIT2QUvSnWZuSIjpreONcLgCVck4-EOmeXh0QzWDOXMCrImrnCDm8wV7Deu_RM3mMgCJo3cECYUkUDAL6Ts5eH2Oy7UUpZiTmUH38OXdxC-Gp9IR02KeLBWG52FPnSDa4XHCUDxDw7N-TZzJcGIcLEAMTH5uDrXr5nYj_d8PWyD94McGi6u6VSie5ZZcBFXNI8zOb9IRJ-GdHo5kul25f98Jg4IGllEvqhs7vyT0lqAKazwU3srXPS_ZmGcm4TLfvxRmWCe7DxkCGCTeTnBBqQwumLFQvok_3WdST7bDvrVoVtpB12f95soOSuMoo54IOzLhXr_fYf59S5bZs2RLCboOOtBuq3-gKAi5s7Qzmcq0qyyWDbJmMcfg82d1wlKW3mM0J2xS6OD9v5l59cungvLjPBM8-5YLIV5XkWqM742lfCYfXLvcGLOp-JHRCBn30dYGkOMfgR74bKbO6J4eJiArQ7arpApMkEOqFaGtIJnLHjrpFD4-G6PeJhOZUT3KAOEYsGLuNkMca-KHzNCHTwmXeCSI-J76NnG9NhYFv1ZGQtU0ycY_NDyg5oeQ4CIz3suG6XYfzMAyRQk_rD2d7J8aN3tF9VcCpvKPUbTpx3box9HOHoXtzSKNWBWMLhxbpnHUNswnz_bXK3h89XYKE6-nfdO1sxDGkH31kUJM4ThgZfOpQN9EgSdsmQ12Qou8wQpw6EkEjQIVKXjPecaXWImMLiGANowKSmw0JqSYm08KU_Yca0nsJBf_X4fwtEgAomlpXs9JQnB4FRImq-Z8JT_-pw5kpQWPUmMuSc-jSdO7tiIT6QMyC1zINDoWgBcHMQuxpD-qBbPYxZ2dLajS3ZXcEGPq0PHQg05vST58YGVQe73LRQWLqgKuX2_JPjSzqNM4xERt0g877gRzXctPH0BMKMymRQlabLd1xbIe3mCVOJdneqTioLdKzz6jmpQ28M8feWdslWuwbXk0MypDxXbylXYMF7mbYn7UykCRnmMh8ogbxQg_CfKCxh6rwTfq4yhcznff55ema6woNbuer_hQgmoV6fz6J33JhBPsFLh3uUjFyeKKE55z59dyoi_7L9krV7cwSR0sxItA3ZS-zlixDKubKPTrCNW8SkJscEfBaHzxqePwjDDw-ucxNE9JTqrS9HP3AbMiSVZZl7gsNLAbsWcF3uI7D2jhw0L07pb2rdmO6z9g39FoQWo2Dljoq6zKM9DfqjE6eZY9KDPtB3OWxxyBbG3mRpeOOXNtVWGi6HSWgSm3GHfqI8V7Dk3LC47B5b9klSlMR8ZWQCim8mvUGGYuakYND78d5MgV1mP-ijsUuUkp6Q6PT0LQxEaYqlDAyPtMZyXHC6xtsyN-sHc-VyUTkVLbvSgNcLAC3DzGS2IFE84-6ItERO4Fqra9gHMVvLIJSFgQUKgh7MTAtDp7wZ4JaLTVx8QD9leA4YULgh-NiGohdZEayPFy0uB-mdKumiNvICNiN98wLZd7b6NQrXVv08GGq4bkYvRolYsX2aHQyfnWxszwNNuSXLT47WbhsA8i0hr9W1F5AfUwmB5UYClX8fj8szpfZHQIRSdTb7gc291cL-DL3crU9_Y4jH_9R3XV9Tw1wVRhzZjMf1AGlUOMBdFHdy3G00)
## Solution Elaboration:

ID MS manages the definition-time contract used by the intent platform.

A specification defines the governed expression shape, high-level characteristic catalogue, metadata, lifecycle status, version identity, related parties, and schema references used by downstream intent creation and validation flows.

The baseline surgical hospital slice specification uses:

- `@type: IntentSpecification`
- `@baseType: EntitySpecification`
- `familyId` for version-family governance
- `specCharacteristic` as a high-level characteristic catalogue
- `expressionSpecification` as the expression contract reference
- `targetEntitySchema` as the governed schema artefact reference for the expression-value shape
- `priority` values of `critical`, `high`, and `standard`
- canonical `context.targets`, `context.constraints`, and `context.preferences` semantics in the expression model

ID MS validates resource structure, required fields, lifecycle rules, and syntax/schema references.

It does not decide whether a submitted runtime intent is semantically feasible or fulfilable in the network. Semantic and policy validation belongs to II MS and the knowledge plane. Runtime assurance belongs to IA MS.

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
| External events | Publish TMF-style external resource events after successful specification changes. |
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
- use `DELETED` as an `IntentSpecification.lifecycleStatus`.

## Contracts:

ID MS exposes two contract families:

| Contract family | Contract |
|---|---|
| Resource API | REST API for `IntentSpecification` lifecycle and version management. |
| Hub API | Domain-scoped hub API for external `IntentSpecification` event subscriptions. |

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

ID MS is externally reached through the platform gateway/security boundary.

The gateway authenticates the caller and forwards trusted system context according to platform policy. ID MS must authorise callers for specification management operations and subscription management operations. It must enforce resource-level and lifecycle-level rules independently of gateway authentication.

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
| Outbox/event publication store | Durable publication of external `IntentSpecification` event notifications after committed resource changes. |

The implementation should publish external events from committed state. Resource mutation and event publication should be resilient to retry, duplicate delivery, and transient downstream publisher failures.

## Kafka publication:

ID MS may publish external specification events through the platform eventing mechanism used for TMF-style notifications. The solution brief does not require ID MS to expose internal workflow event topics.

Events are external subscription notifications for specification-resource changes. They must not expose internal fulfilment, KP, optimiser, assurance, telemetry, callback, or candidate/resource scoring details.

## Topics:

The baseline documents define the external event family but do not lock a dedicated Kafka topic name for ID MS in the same way the ICB callback topic is locked.

The implementation should use the platform’s external notification/event distribution convention for TMF-style `IntentSpecification` event delivery.

Supported external event types are:

```text
IntentSpecificationCreateEvent
IntentSpecificationAttributeValueChangeEvent
IntentSpecificationStatusChangeEvent
IntentSpecificationDeleteEvent
```

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
| `event` | Event payload containing the `intentSpecification` snapshot and transition data where applicable. |
| `reportingSystem` | ID MS reporting system identity. |
| `source` | ID MS source identity. |
| `@type` | Event type. |

`eventTime` and `timeOccurred` should carry the same canonical occurrence timestamp.

## CloudEvents headers:

The current ID MS baseline uses TMF-style external event envelopes for subscription notifications. It does not require CloudEvents headers for the ID MS external event examples.

If the platform event distribution layer wraps these events in CloudEvents for transport, the CloudEvents metadata must remain a transport envelope only and must not change the TMF-style resource-event payload semantics.

## Message shape:

A typical `IntentSpecificationStatusChangeEvent` has this logical shape:

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
- Activation emits two `IntentSpecificationStatusChangeEvent` events: one for `DRAFT -> ACTIVE` and one for previous active `ACTIVE -> RETIRED`.

### Delete behaviour:

- Delete is allowed only for unused `DRAFT` specifications.
- Delete is blocked for `ACTIVE` and `RETIRED` specifications.
- Delete is blocked where runtime references or audit/history dependencies require retention.
- Delete requires `If-Match`.
- Successful delete returns `204 No Content`.
- Delete emits `IntentSpecificationDeleteEvent` only after successful delete.

## Configuration:

ID MS configuration should include:

| Configuration area | Purpose |
|---|---|
| Allowed lifecycle states | `DRAFT`, `ACTIVE`, `RETIRED`. |
| Mutability policy | Material update allowed only for `DRAFT`. |
| Version-family rule | Only one active version per `familyId` for new runtime intent creation. |
| Cache policy | GET-only private caching, with bounded TTLs. |
| Concurrency policy | Unsafe operations require `If-Match`. |
| Hub route policy | Domain-scoped `/intentSpecification/hub` routes retained as platform extension. |
| Event filter policy | Supported `IntentSpecification` event types. |
| Schema registry / governed artefact references | Validation of `expressionSpecification` and `targetEntitySchema` references. |

## Consumer contract:

Consumers of ID MS should rely on these behaviours:

- IC MS retrieves active `IntentSpecification` resources to validate new runtime intent creation.
- New runtime intents must reference an `ACTIVE` specification.
- `DRAFT` and `RETIRED` specifications must not be used for new runtime intent creation.
- Consumers must treat `ACTIVE` and `RETIRED` specification contracts as immutable.
- Consumers should use `fields` where a lightweight response is sufficient.
- Consumers must use `If-Match` for unsafe updates and deletes.
- Event subscribers receive only external `IntentSpecification` event notifications and not internal workflow details.

## Open items:

| Item | Status |
|---|---|
| Dedicated physical Kafka topic name for ID MS external events | Not locked in the current baseline; use platform external notification convention unless later baselined. |
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
| Primary responsibility | Definition-time `IntentSpecification` catalogue, lifecycle/version governance, syntax contract, and external specification events. |
