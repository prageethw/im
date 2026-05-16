# Intent Controller MS Solution Brief

## Summary:

Intent Controller MS (IC MS) is the TMF-compliant runtime intent controller for the Intent Enabler. It owns the external `Intent` and `IntentReport` resource boundary, admits syntactically valid runtime intent requests, projects external lifecycle/status state, and publishes curated external runtime intent events. IC MS is deliberately not the semantic, optimisation, orchestration, callback, or runtime assurance owner.

Its main purpose is to provide a stable external runtime API and event projection layer while delegating deeper decisioning and assurance responsibilities to the appropriate downstream services. The current baseline source is GitHub `main/baseline/intent`. This solution brief is aligned to the validated `ic_ms_specification.md`, `ic_ms_design_brief.md`, and the baselined ID MS definition contract.

## Logical View:

IC MS sits between external intent consumers, the definition-time specification catalogue, and the internal intent fulfilment pipeline. It is the runtime API and projection boundary for `Intent` and `IntentReport`; it is not the owner of semantic interpretation, optimisation, orchestration, callback ingestion, or runtime assurance truth.

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
| Upstream dependency | ID MS for concrete active `IntentSpecification` validation. |
| Internal event path | Emits admitted runtime intent state through `IntentValidatedEvent` using the IC MS internal event outbox and Kafka relay. |
| Downstream event consumers | II MS consumes admitted runtime intent state through `IntentValidatedEvent`. |
| Downstream status inputs | II MS rejection outcomes and IA MS assurance outcomes drive IC MS external lifecycle/status projection. |
| External event subscribers | Receive TMF-style `Intent` and `IntentReport` events through REST webhook subscriber listener callbacks registered via the IC MS hub subscription model. |
| External notification path | Uses `webhook_delivery_outbox` and HTTP `POST`; Kafka is not used for external hub notification delivery. |

IC MS owns the externally visible runtime projection, not the full internal fulfilment state machine. The external `Intent` record is the current consumer-facing state of the runtime intent. Historical versions, standby states, rollback candidates, internal resource candidates, optimiser scoring, and raw assurance detail remain internal unless projected through `IntentReport` or another documented platform extension.

## Process View:
![alt text](https://plantuml-server.kkeisuke.dev/svg/jLbjRnkv4Vw-lsBg0eM5o5RYIu9hW1IdM8eZr6-mv5oBSr1GkvJ4UiNLaLpRWc6Wd-u77FeBxvTqXkI-QNSb9tUr0SFI3cU6y_8yG-uFsZ1bqcKCesCu6yC1NANIY2M7aJHS6XZpdrCkGmuVu-HU1tyo2uuFLp4JCj2tGgwOOalGNkgCQytcl1-BkOGGrtDLafgoy7QkabH6nqcSAFZpH_jJai2_HeHYnQJvi2aSCVxzB6mHJbJ4bHTy6txFfxC6x_fA9VTUw3lxKnAIYU4LDT7RwTitRpSbDhsQpMP7OTchIDm9L58NV4c_3LwTeDIgBlvN-Wq28qoS9-DOSMP48YbJ-pPX7VZjF__TaRE0XGPLxWqVC1sInN2SI9qkkTe3flCFGIcSi7T-yYFqe7yvWXDc-3rRMzcJ7wjITRTkfFVBoe-EpyQDAmPy9gGehHaKQmQu9apYc8VqN6ThRkGOTy5XV_312Oud5rV386A6JPdci7UHccdo0BqREU2nkEDg3VwhVCd5zUJ3nJzAQyRfL8TAhCZIZRpYSw4DhYjiN7-u6fvKjv1hl-8nMwFpHLd3VQ9kkN9hhuQd_NzMTp98xYKQu6o9k-7gJeHSMzb1SvZwMgUAKIPTbFf5bFeO9PzNluafLpVo53V0fKyjUXy4xz_3gyFD2iapzlvza1K07FmD4mpluF9YF86Ui99dJ68_B_6_tjqR_zsDV0JtttZ5Gp4JeTLrAA8ky8ULGWp0Zpr5LQXD5muF3-4fGDLeW2e2JSmITSzK15uc22X-AnYlfS5DYH0-irX4Lcq0-6EN5Sllt5CEaxEFg4CdgS8OwGLRyQhum8gV3BVkfxABtgE8dZ3Mc64nMwFo6LVKIn5e50EXeOyEtl6ECqG63Wh7HdM5y0YncF5m7SPyR9X9zJlOSphskg13n5FMYuf-UDgwOUNpM8-ps_uDRW-X6JyoQwBHey9Qm6M4-12RKi1XnaIiIrvaTV7ww0YkvKeb8Q7y565fYCwODTL3c4Jy7Npkduu6_SdeulnV7_kZq-402m8nL-6MVy8g-E8tHwM0IlF2SwfhYmCUOu-M7DDf678UETzSnVHDiiHo6Nm0WusYMPYNJ3cA5YhGp8ehZGs2qVD8wDi1z_HlrwIsjh6ExqWoaU_WLRUUldvuAvFxc4TpB8kdcZM7CcZkNWcJPS1s71_UaJba8QmAxRLT3iy7e_CJhuWIKW_zqSjNhcVHODPyptEi7kicNIXSARi15HrV2kEzzqdWaTl0FgsY07Pkv6-__8fKjaJOmZpOxx4oZKiOFKiGN9T2CnTT-ut2eaSOT38eJNoOoxFLAbuxmP35CO5hargMGQFrcwWPb9Wl32Gpvts1jUYUWrhmjNiZSOh9TixqMeOBbSWarV7QXM5GQUeaDM6ovBsYIe1J653FFdutfqRimYoDPo8cPB6PvP2kA6Aw4pHLedkujH3tDzBRzK9NV9Ke0tU2ttUSkvPfAfMtGjR92wjMW7QHbwLzklNOepN9BrNzZWvHCawIM-o-9JFXGiWvTcR1ewuzlMX5_MEUqMiLmrDTEGfzcamknuw27alIJzIODkhlwllf-boEebfF-2uWX2FDSFJmaFSh6IpxT_JoDPmdr2ec2r9pT9TCtS9WU3hwFBn2cB9jIr15m9agtchWzGEE9_36_YKKnyBQOaN8K5ccGXAYeIJ42GDRByh63yon2DTsg3v8PhDE3XyMqv7sZsgqV-sg3adVDao2Ud9aw6RbVeqmEiE729RCpIt4C097hz7iu8mo3WlESCI5VT_RrFbX8iDK4LMkiJGP32TitccOBQwtKh5dNq2CWCl-vFZJCuG_MMSG_JBta5yVdI-6l7ZQsp5xRFRcZDCUlOOiT8g7U3Y05tPZWHCjOKG1oWXISu9JAZcI1GoGxHFOpsDaO9b4EHztchZsrH5SaaqPkR7W8zOMZzheiqNQLgLpWZpWkccsi80BBQd4HU5jYM-R9ZJOrmnh30VEq8-LdHed-aaidsCS_aMbEGPs3ow5resnwwxm1RMbiSbx8U_-Cyua8XMYT3v3XQxHSOzCpekkVSvWqGJfTlCS9B_FBVWf0lRpSKA-U8MSIKmcPFvuWN5FiAEnCe6bcC8UsWmvcueOnwkjHZTvfCHH9ibhs1jgrDGuhVIDmGD5QZXcEUN7Da2E-jlcblBiKfia53zW4KqJ59nirmP9Dvql82g8kiIXCpowviggV9pLJYil1pkYvLlwHPLG2pMwWFGp8J4fFHmmv45BlRGOmVokOimYxCkalEzEy7_AG5xkcwFZIxZuUmcWohNO9SyiGBHFYvNbsQ3OCdBGPEO9QkS-i3xfWFfxPe1svK_1Cnb-9xjdRFfTZKqdN2s5pC_HMoWLjGqdGpeyPiXWYhLTcbvXjLXhXBcOmiVjSPhk8opdq38B65ZpEKHqyJigMyIqqj2JGKaNoWXoMETXxz4kTjtEdCt4MINC_Hpo-GFwfk4lThiineQFrdaCUTHf9rKgkbselEcBvgOs2r9r5WPnmlOux5sbcpJirMecU7L-R-pLWHLixqvRGfjTUOIdjP2lt2ciTf8htFHN9vjTMLbUX6bBNrQF0oMVW_QZG4dgI_2rnu1d7G6-jVLBddLtX6y72kn40Eh-ruTLihWiEAVI-dGlbxUzlQy3ehUyx_DZAnPmQXROvExUFNIvrKJPrkr2qDES1YQZZAHqnPl3WCoM6dMLJcEX5tKbBeR51HwTc7AXx9YvnEE627LsSTSov_IgR5eZqQeH1rQDvYWks3FBLSbMOviv4-MBb4HL7hNImTQ-gFALtmSlKzItrcZTuHviewpVNQWrcDzny-aSzESjAuifxprcoVfA-CTlSOXjdQbgyFvJMVGBkQ0HH93471u7BNECc_1RO75Jff6LCuSlL8GWWJxduxDlGwLnAeNpYuddWEgcd7iQU_T2uibfJjg9cxDBiHxDkZZzfMgEqvyxfjlXKT6xWAY3QQEBvIMkytsX3tE2iqjxS98flMpHqitDDLymUVqDZcVAa8FfzT0p-CqjtyLoNpKMrbN-0UDWNUaVFmQ-OJW7slT4k9TFwHJAhv3Qni2SC8jNDPWCfqGNrvpNLwVsxaGJ_XhxSgEtIAStT0J1iuJ11bpQMfNs09KDQYZoDIznh4PtmxBZHOyJhL1srtLv3uzf583d8aIs_-m2_h4oAX0jL6muxTsiPjPdEAVHIpk7aTbGuOtIVVQclfnAcY_GjnXlmPMsrGGnL1LJgWfC6zPZOrKy7vanvbypUc-COXNVF8xMGrQMQeFPZLrk0TkcU8I7uFhmUT7OTXpvne1u07nUG11NPq8jUPrqAaZH58IAGF03uaIwZFy7.svg)
### Runtime intent creation:

1. A consumer submits `POST /intentManagement/v5/intent` with a runtime `Intent` request.
2. IC MS validates the basic TMF resource shape.
3. IC MS checks that the request references a concrete active `IntentSpecification.id`.
4. IC MS validates the runtime expression/request shape against the active definition owned by ID MS.
5. If validation fails, IC MS returns a structured error such as `422 VALIDATION_FAILED`.
6. If validation succeeds, IC MS persists the external `Intent` projection.
7. IC MS sets the initial projected lifecycle state to `Acknowledged`.
8. IC MS emits `IntentValidatedEvent` as an internal state/progress event.
9. Downstream services continue semantic interpretation, optimisation, orchestration preparation, apply, callback interpretation, and assurance.
10. IC MS consumes downstream outcome/projection events and updates the external `Intent` and `IntentReport` views.

### Runtime intent update:

1. A consumer updates an existing runtime intent using `PUT` or `PATCH`.
2. Unsafe update operations require `If-Match`.
3. IC MS applies optimistic concurrency using the current ETag.
4. Meaningful runtime content changes create a new runtime intent version.
5. The new version is admitted through the same syntactic validation and downstream fulfilment flow.
6. IC MS projects the current runtime version externally while retaining internal version history for audit and traceability.

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
3. When a subscribed `Intent` or `IntentReport` event occurs, IC MS creates the TMF-style event payload.
4. IC MS writes webhook delivery work to its own local delivery outbox.
5. The IC MS delivery relay posts the event payload to the subscriber listener callback URL using HTTP `POST`.
6. The subscriber listener acknowledges delivery with an HTTP success response, normally `204 No Content` where aligned to TMF listener behaviour.
7. IC MS retries failed callback deliveries according to delivery policy.

Kafka is not used for external hub notification delivery. IC MS does not create a self-publish/self-consume Kafka loop for hub notifications where it is both the event originator and the delivery owner.

## Solution Elaboration:

IC MS is the runtime equivalent of a controlled admission and projection layer. It accepts runtime intent requests only when the incoming payload is structurally valid and references a concrete active `IntentSpecification`. It does not interpret whether the intent is semantically achievable, feasible, optimal, policy-compliant, or currently assured.

The design intentionally separates these concerns:

| Concern | Owner |
|---|---|
| Runtime API admission and external projection | IC MS |
| Intent definition/specification contract | ID MS |
| Semantic interpretation and network-ready preparation | II MS |
| Optimisation | Optimiser services |
| Orchestration/network apply | Orchestration layer / network orchestrator |
| Callback ingestion | ICB MS |
| Callback interpretation and runtime assurance truth | IA MS |

IC MS therefore exposes a stable TMF-style resource API while avoiding leakage of internal fulfilment mechanics. It is responsible for correct external lifecycle/status representation, consumer-safe reports, event subscription handling, ETag concurrency, and error consistency.

## Responsibilities:

IC MS is responsible for:

| Responsibility | Description |
|---|---|
| Runtime `Intent` API | Create, list, retrieve, replace, patch, and terminate runtime intents. |
| Runtime syntactic validation | Validate incoming runtime intent request shape against a concrete active `IntentSpecification.id`. |
| Initial admission | Persist syntactically valid requests and project `Acknowledged`. |
| Internal progress publication | Emit `IntentValidatedEvent` after syntactic validation succeeds. |
| External lifecycle projection | Own consumer-facing `Intent.lifecycleStatus`, `statusReason`, and `statusChangeDate`. |
| Runtime version projection | Return the current projected runtime version externally while retaining internal version history. |
| `IntentReport` projection | Expose read-only curated report/projection history derived from assurance outcomes. |
| Event subscription | Support strict TMF `/hub` and domain-scoped `/intent/hub` subscription routes. |
| External event delivery | Deliver consumer-safe TMF-style `Intent` and `IntentReport` event notifications by REST webhook callback to subscriber listener URLs. |
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
| Network apply / orchestration execution | Orchestration layer / network orchestrator |
| Apply outcome interpretation | IA MS |
| Runtime assurance truth | IA MS |
| Real-time telemetry | Telemetry platform consumed by IA MS |
| Callback ingestion | ICB MS |
| Raw orchestrator callback interpretation | IA MS |
| Raw candidate/resource scoring exposure | Internal optimiser/assurance pipeline only |

IC MS also does not resolve an `IntentSpecification` by `familyId`, name, key, or inferred expression shape. Runtime create/update requests must reference a concrete active `IntentSpecification.id`.

## Contracts:

### Intent resource APIs:

| Purpose | Method | Endpoint | Position |
|---|---:|---|---|
| Create runtime intent | `POST` | `/intentManagement/v5/intent` | TMF-aligned |
| List runtime intents | `GET` | `/intentManagement/v5/intent` | TMF-aligned |
| Retrieve runtime intent by ID | `GET` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Full replace runtime intent | `PUT` | `/intentManagement/v5/intent/{id}` | Platform extension |
| Partial update runtime intent | `PATCH` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Terminate runtime intent | `DELETE` | `/intentManagement/v5/intent/{id}` | TMF-aligned delete verb; platform behaviour is termination, not physical deletion |

### IntentReport APIs:

| Purpose | Method | Endpoint | Position |
|---|---:|---|---|
| List reports for intent | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport` | Platform/TMF-style nested report projection |
| Retrieve report by ID | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport/{id}` | Platform/TMF-style nested report projection |

Ordinary external consumers do not receive a public `DELETE /intentManagement/v5/intent/{intentId}/intentReport/{id}` capability. Governed internal/admin purge may exist but is not exposed through NGW/public consumer APIs by default.

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

## Request shape:

A runtime intent create/update request must include:

| Field | Requirement |
|---|---|
| `name` | Consumer-facing runtime intent name. |
| `description` | Optional descriptive text. |
| `humanExpression` | Human-readable expression of the requested outcome. |
| `intentSpecification.id` | Required concrete active specification ID. |
| `expression` | Required TMF-style `JsonLdExpression`. |
| `expression.expressionValue.context.targets` | Required measurable outcome/SLA objectives where defined by the specification. |
| `expression.expressionValue.context.constraints` | Required or optional hard constraints as defined by the specification. |
| `expression.expressionValue.context.preferences` | Optional soft selection guidance as defined by the specification. |
| `isBundle` | Runtime bundle flag. |
| `priority` | Runtime priority where applicable. |
| `relatedParty` | Requester/customer/operator party references where applicable. |
| `validFor` | Runtime validity window where applicable. |
| `@type` | `Intent`. |
| `@baseType` | `Entity`. |

Example concrete specification reference:

```json
{
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  }
}
```

Unsupported specification references:

```json
{
  "intentSpecification": {
    "familyId": "hospital-surgical-slice-spec"
  }
}
```

```json
{
  "intentSpecification": {
    "name": "Hospital Surgical Slice Intent Specification"
  }
}
```

## Field specification:

### Runtime Intent projection fields:

| Field | Meaning |
|---|---|
| `id` | Server-generated runtime intent identifier. |
| `href` | Canonical resource URL. |
| `name` | Runtime intent name. |
| `description` | Consumer-facing description. |
| `humanExpression` | Human-readable request. |
| `version` | Current projected runtime version. |
| `lifecycleStatus` | Current projected external lifecycle status. |
| `statusReason` | Human-readable reason for current projected status. |
| `statusChangeDate` | Timestamp for latest projected status change. |
| `intentSpecification` | Concrete active specification reference. |
| `expression` | Runtime intent expression using `JsonLdExpression`. |
| `validFor` | Runtime validity period. |
| `isBundle` | Bundle indicator. |
| `priority` | Consumer/platform priority. |
| `relatedParty` | Party references. |
| `_links` | Hypermedia controls for valid next actions. |
| `@type` | `Intent`. |
| `@baseType` | `Entity`. |

### Intent-level lifecycleStatus values:

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

### Intent-version lifecycleStatus values:

```text
Acknowledged
InProgress
Active
Standby
Degraded
Paused
Rejected
Failed
Terminated
Retired
```

External `GET /intent/{id}` returns the current projected `Intent` state. It does not return the full internal version aggregate by default.

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
| `intentSpecification.familyId` as the only specification reference | IC MS does not resolve runtime requests by family. |
| `intentSpecification.name` as the only specification reference | IC MS does not resolve runtime requests by display name. |
| Inferred specification from expression shape | Runtime request must explicitly name the concrete active specification. |
| Internal optimiser candidate sets | Not part of the external runtime create/update contract. |
| Raw Knowledge Plane facts | Not accepted through IC MS runtime APIs. |
| Raw telemetry observations | IA MS consumes telemetry; IC MS exposes curated projections only. |
| Raw orchestrator callback payloads | ICB MS ingests callbacks; IA MS interprets them. |
| Consumer-supplied lifecycle/status projection authority | IC MS owns external lifecycle/status projection. |
| Consumer-supplied `IntentReport` mutation fields | Reports are curated projection/audit resources. |
| String placeholders for object/array fields in examples or payloads | Typed placeholder rule requires object placeholders for objects and array placeholders for arrays. |

## Authorisation:

IC MS is exposed through the platform gateway boundary and must enforce standard platform access controls before accepting runtime intent operations. Authorisation responsibilities include:

| Area | Behaviour |
|---|---|
| Runtime intent create/update/delete | Only authorised external consumers or platform actors can create, update, or terminate runtime intents. |
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
| Runtime intent record | External canonical `Intent` projection. |
| Current projected version | Version returned by standard `GET /intent/{id}`. |
| Lifecycle/status fields | `lifecycleStatus`, `statusReason`, `statusChangeDate`. |
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
| Event payload | TMF-style event body to send to the subscriber listener. |
| Callback URL | Resolved subscriber listener URL. |
| Delivery status | Tracks pending, delivered, retrying, and failed delivery work. |
| Retry metadata | Retry count, next retry time, and last error information. |

## Event delivery paths:

IC MS has two distinct event-delivery paths. The two paths must not be collapsed into a single Kafka or webhook model.

| Delivery path | Purpose | Transport | Durability model | Headers | Payload |
|---|---|---|---|---|---|
| Internal platform event publication | Notify independent internal microservice consumers that runtime intent admission or another internal milestone has occurred. | Kafka. | IC MS internal event outbox and Kafka relay. | CloudEvents-style Kafka/platform event headers. | Internal event JSON body, for example `IntentValidatedEvent`. |
| External TMF/webhook notification delivery | Notify registered external subscribers about consumer-safe `Intent` and `IntentReport` events. | HTTP `POST` to subscriber listener callback URL. | IC MS webhook delivery outbox and HTTP retry relay. | HTTP headers. | TMF-style event request body, for example `IntentStatusChangeEvent`. |

## Internal Kafka event publication:

IC MS publishes internal state/progress events through the platform Kafka event backbone where an independent internal consumer exists.

| Event category | Purpose | Transport | Primary consumer |
|---|---|---|---|
| `IntentValidatedEvent` | Internal state/progress event emitted after syntactic validation succeeds. | Kafka. | II MS / `intent-intelligence-ms`. |

`IntentValidatedEvent` is not a point-to-point command. It states that an `Intent` has passed IC MS syntactic validation and has been admitted into the runtime lifecycle. IC MS writes the event to its internal event outbox, and the internal event relay publishes it to Kafka using the platform event header model.

## External hub notification delivery:

External `Intent` and `IntentReport` notifications are delivered to subscriber listener callback URLs through the hub subscription model. They are not delivered to external subscribers through Kafka.

| Delivery target | Event usage | Transport |
|---|---|---|
| Subscriber callback URL | External event delivery target configured through `/hub` or `/intent/hub`; the URL is subscriber-owned, not TMF-owned. | HTTP `POST`. |

IC MS writes webhook delivery work to a local webhook delivery outbox and an HTTP delivery relay posts the TMF-style event body to the subscriber listener callback URL. Kafka is not used for external hub notification delivery.

External events must not expose raw telemetry, raw optimiser decisions, raw Knowledge Plane data, raw callback payloads, internal candidate scoring, or internal Kafka payloads.

## Event identity:

External IC MS events use a TMF-style event resource shape.

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

Status-change events carry the current `intent.lifecycleStatus` snapshot in the `event.intent` payload. They do not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields in the external event payload. The event type, timestamp, and emitted resource snapshot provide the lifecycle-change signal.

## Internal Kafka CloudEvents headers:

For internal Kafka event backbone delivery, IC MS should use the common platform CloudEvents envelope where applicable. These headers apply to internal Kafka events such as `IntentValidatedEvent`; they do not apply to external webhook notifications. Typical CloudEvents headers include:

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

External TMF-style subscriber callbacks are REST webhook notifications. They carry HTTP headers and a REST request body rather than Kafka-style CloudEvents headers.

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
      "id": "hospital-surgical-slice-spec-v1.20"
    },
    "expression": {
      "@type": "JsonLdExpression",
      "@baseType": "Expression",
      "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
      "expressionValue": {
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
            "redundancyRequired": true
          },
          "preferences": {
            "preferredAccessTechnology": "5G"
          }
        }
      }
    },
    "references": {
      "intent": {
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
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
| Missing concrete `intentSpecification.id` | Return `422 VALIDATION_FAILED` with reason `CONCRETE_INTENT_SPECIFICATION_ID_REQUIRED`. |
| Referenced specification is not active | Return `422 VALIDATION_FAILED` or `INTENT_SPECIFICATION_NOT_ACTIVE`. |
| Active specification cannot be confirmed | Return `503 SERVICE_UNAVAILABLE` with retry guidance where applicable. |
| Request passes syntactic validation | Persist `Intent`, set `Acknowledged`, emit `IntentValidatedEvent`. |

### Update and concurrency behaviour:

| Scenario | Behaviour |
|---|---|
| Unsafe operation missing required `If-Match` | Return `428 PRECONDITION_REQUIRED` with reason `IF_MATCH_REQUIRED`. |
| Stale or mismatched ETag | Return `412 PRECONDITION_FAILED` with reason `ETAG_MISMATCH`. |
| Valid material update | Create/project a new runtime version and re-enter admitted lifecycle. |
| `PATCH` usage | Supported for TMF compatibility, but `PUT` is preferred for deterministic full update. |

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
| ID MS lookup endpoint | Validate concrete active `IntentSpecification.id`. |
| Allowed lifecycle transitions | Control valid projected state movement. |
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
| Stable runtime `Intent` API | TMF-style create, list, retrieve, update, patch, and termination routes. |
| Concrete spec reference requirement | Runtime requests must reference `intentSpecification.id`. |
| External status projection | `lifecycleStatus`, `statusReason`, and `statusChangeDate` are IC MS-owned projections. |
| Report read model | `IntentReport` is a read-only curated projection/audit resource for ordinary consumers. |
| Hypermedia links | Responses include links for valid next actions where applicable. |
| Optimistic concurrency | Unsafe operations use `If-Match` and ETag. |
| External events | Subscribers receive consumer-safe TMF-style resource events through REST webhook callbacks. |
| No internal leakage | Raw telemetry, optimiser decisions, callback payloads, candidate scoring, and KP internals are not exposed in external events. |

Internal consumers can rely on `IntentValidatedEvent` as the admitted runtime intent handoff, not as a command targeted to a single service.

## Open items:

| Item | Status |
|---|---|
| Exact physical Kafka topic split for IC internal events | May be refined by deployment policy while preserving `IntentValidatedEvent` semantics. |
| Public exposure posture for TMF strict `/hub` versus domain-scoped `/intent/hub` | Both are baselined; gateway product exposure can choose supported route set. |
| Optional internal/admin `IntentReport` purge API details | Governed capability is allowed, but ordinary external consumer delete remains not exposed by default. |
| Full internal version-history retrieval API | Not exposed by default; can be defined later as a documented platform extension if needed. |

## Closed items:

| Item | Decision |
|---|---|
| IC MS service identity | Full name is `Intent Controller MS`; service name is `intent-controller-ms`. |
| Runtime create requires active concrete spec | Use `intentSpecification.id`; no family/name/inferred resolution. |
| IC MS validation scope | Syntactic/request-shape validation only; no semantic or optimisation ownership. |
| Initial admitted state | `Acknowledged`. |
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
| Primary responsibility | TMF-compliant runtime `Intent` controller, syntactic admission, lifecycle/status projection, and external runtime intent events |
