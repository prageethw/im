# IC MS Specification:

**Service identity:**

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Controller MS |
| Short name | IC MS |
| Service name | `intent-controller-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `Intent` |
| Secondary resource | `IntentReport` |
| Primary responsibility | TMF-compliant runtime `Intent` controller, syntactic admission, lifecycle/status projection, and external runtime intent events |

**TMF deployment path note:**

This specification uses `/intentManagement/v5` in examples as the platform base path. A strict TMF gateway exposure may publish the same API under `/tmf-api/intentManagement/v5`. The API gateway may map between the external TMF route prefix and the internal/platform route prefix without changing the resource contract.

**Boundary statement:**

IC MS owns the external runtime `Intent` and `IntentReport` resources.

IC MS validates runtime `Intent` request shape against the applicable active `IntentSpecification` resolved from mandatory `intentSpecification.id`, with mandatory `expression.iri` used to confirm the semantic/expression contract. IC MS admits syntactically valid runtime intents, emits `IntentValidatedEvent` as an internal state/progress event, projects external lifecycle/status based on downstream outcomes, and exposes curated `IntentReport` projections.

IC MS does not own:

- design-time `IntentSpecification` catalogue
- semantic validation
- policy validation
- optimisation
- network or platform change execution
- apply outcome interpretation
- runtime assurance truth
- real-time telemetry
- callback ingestion
- raw orchestrator callback interpretation

Network or platform change execution is owned by the downstream change execution layer, which may be a network orchestrator or another authorised fulfilment component depending on the Intent domain. IA MS interprets change outcomes and owns runtime assurance truth; IC MS only projects the resulting lifecycle/status changes.

---

## 1. API endpoints:

### Intent resource APIs:

| **Purpose** | **Method** | **Endpoint** | **Position** |
|---|---:|---|---|
| Create runtime intent | `POST` | `/intentManagement/v5/intent` | TMF-aligned |
| List runtime intents | `GET` | `/intentManagement/v5/intent` | TMF-aligned |
| Retrieve runtime intent by ID | `GET` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Full replace runtime intent | `PUT` | `/intentManagement/v5/intent/{id}` | Platform extension |
| Partial update runtime intent | `PATCH` | `/intentManagement/v5/intent/{id}` | TMF-aligned |
| Terminate runtime intent | `DELETE` | `/intentManagement/v5/intent/{id}` | TMF-aligned delete verb, platform behaviour is termination not physical deletion |

### IntentReport APIs:

| **Purpose** | **Method** | **Endpoint** | **Position** |
|---|---:|---|---|
| List reports for intent | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport` | Platform/TMF-aligned nested report projection |
| Retrieve report by ID | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport/{id}` | Platform/TMF-aligned nested report projection |

### Hub subscription APIs:

Strict TMF route form:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/hub` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/hub/{id}` |

Accepted domain-scoped platform extension:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create intent event subscription | `POST` | `/intentManagement/v5/intent/hub` |
| Retrieve intent event subscription | `GET` | `/intentManagement/v5/intent/hub/{id}` |
| Delete intent event subscription | `DELETE` | `/intentManagement/v5/intent/hub/{id}` |

Hub subscriptions are REST webhook subscriptions. IC MS stores subscriber callback registrations and delivers subscribed external `Intent` and `IntentReport` event notifications by HTTP `POST` to the subscriber listener callback URL. Kafka is not used for external hub notification delivery. Delivery reliability is handled by an IC MS-owned local webhook delivery outbox and HTTP retry relay.

IC MS therefore has two separate event-delivery paths:

| Delivery path | Purpose | Transport | Durability model | Headers | Payload |
|---|---|---|---|---|---|
| Internal platform events | Publish internal state/progress events such as `IntentValidatedEvent` to independent internal consumers. | Kafka. | IC MS internal event outbox and Kafka relay. | CloudEvents-style Kafka/platform event headers. | Internal event JSON body. |
| External TMF/webhook notifications | Notify registered hub subscribers about consumer-safe `Intent` and `IntentReport` events. | HTTP `POST` to subscriber listener callback URL. | IC MS webhook delivery outbox and HTTP retry relay. | HTTP headers. | TMF-aligned event request body. |

---

### TMF compliance and platform extension baseline:


#### Response classification headers:

IC MS returns response classification headers on external REST API responses so callers can distinguish strict TMF-native behaviour from documented platform-extension behaviour.

These are response headers only. Clients do not send these headers in requests.

| **Response header** | **Meaning** |
|---|---|
| `X-TMF-Native: true` | The response is for a TMF-native operation/behaviour. |
| `X-TMF-Native: false` | The response is for an operation/behaviour that includes platform-specific semantics. |
| `X-Platform-Extension: true` | The route, method, response, or behaviour includes a documented platform extension. |
| `X-Platform-Extension: false` | No platform extension is used for the response. |

Header classification guidance:

| **IC MS response area** | **X-TMF-Native** | **X-Platform-Extension** | **Reason** |
|---|---:|---:|---|
| `POST /intent`, `GET /intent`, `GET /intent/{id}`, `PATCH /intent/{id}` using strict TMF-compatible behaviour | `true` | `false` | TMF-compatible Intent resource operations. |
| `POST /intent` or `PATCH /intent/{id}` using `submit` Draft/admission control | `false` | `true` | `submit` is an IC MS request-control extension. |
| `PUT /intent/{id}` | `false` | `true` | Deterministic full replacement is a platform extension. |
| `DELETE /intent/{id}` termination/retention response | `false` | `true` | The verb is TMF-compatible, but retained termination behaviour is platform-specific. |
| `GET /intent/{intentId}/intentReport`, `GET /intent/{intentId}/intentReport/{id}` | `true` | `false` | TMF-aligned read-only report projection. |
| Strict `/hub` create/delete responses | `true` | `false` | Strict TMF hub route family. |
| Domain-scoped `/intent/hub` responses | `false` | `true` | Domain-owned hub route family is a platform extension. |

Example TMF-native response headers:

```http
X-TMF-Native: true
X-Platform-Extension: false
```

Example platform-extension response headers:

```http
X-TMF-Native: false
X-Platform-Extension: true
```


IC MS keeps the external `Intent` and `IntentReport` contract TMF-aligned while documenting controlled platform extensions explicitly.

#### Strict TMF-compatible operations:

| **Capability** | **Route family** | **Position** |
|---|---|---|
| Runtime Intent create/list/retrieve | `POST /intent`, `GET /intent`, `GET /intent/{id}` | TMF-compatible |
| Runtime Intent partial update | `PATCH /intent/{id}` | TMF-compatible |
| Runtime Intent delete verb | `DELETE /intent/{id}` | TMF-compatible verb; platform behaviour is termination and retention, not physical deletion |
| IntentReport list/retrieve | `GET /intent/{intentId}/intentReport`, `GET /intent/{intentId}/intentReport/{id}` | TMF-aligned nested report projection |
| Hub subscription create/delete | `POST /hub`, `DELETE /hub/{id}` | Strict TMF route family |

#### Accepted platform extensions:

| **Extension** | **Reason** |
|---|---|
| `PUT /intent/{id}` | Deterministic full replacement for runtime Intent edits where `PATCH` is too ambiguous |
| `/intent/hub` domain-scoped hub routes | Domain-owned subscription surface for external Intent and IntentReport events |
| `GET /intent/hub/{id}` | Operational convenience for retrieving a domain-scoped subscription; not part of the strict TMF minimum hub route set |
| `_links` | Lifecycle-aware and authorisation-aware HATEOAS controls |
| Strong `ETag` / `If-Match` governance | Optimistic concurrency for unsafe operations |
| `428 Precondition Required` | Explicit response when required `If-Match` is missing |
| Termination-retention behaviour for `DELETE /intent/{id}` | Runtime Intent records remain available for audit, reporting, lifecycle history, and traceability |
| Ordinary external `IntentReport` delete not exposed | `IntentReport` is read-only curated projection/audit history for ordinary consumers; governed/admin removal remains internal or restricted |

Hub notification delivery is REST webhook delivery to subscriber listener callback URLs. IC MS does not create a Kafka topic or self-publish/self-consume Kafka events for external hub notifications.

---

## 2. Common conventions:

### Expression schema alignment:

The long-term canonical expression-value schema pattern for the Intent domain should align with the TMF Intent Ontology direction and use a scalable JSON-LD-style structure.

For governed `targetEntitySchema` definitions, prefer this top-level shape:

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

Canonical schema direction:

- use `@context` for JSON-LD vocabulary and term mapping
- use `@type` for the expression-value type
- use `context.targets[]` for measurable goals or target outcomes
- use `context.constraints[]` for hard requirements
- use `context.preferences[]` for soft selection guidance
- allow the active `IntentSpecification.targetEntitySchema` to specialise permitted target, constraint, and preference entry types

Simplified object-map payloads may still appear in minimum-data explanation examples where readability matters, but they are not the preferred long-term canonical schema shape for governed `targetEntitySchema` definitions.



### PATCH semantics:

`PATCH` uses JSON Merge Patch semantics.

All external `PATCH` request examples must use:

```http
Content-Type: application/merge-patch+json
```

`PATCH` is intended for small targeted updates. For deterministic full replacement of editable Draft resources, use `PUT` where the platform extension is available.



### Runtime IntentSpecification and expression IRI resolution rule:

Submitted runtime `Intent` admission requests must carry both `intentSpecification.id` and `expression.iri`.

These fields serve different purposes:

| **Field** | **Purpose** |
|---|---|
| `intentSpecification.id` | Selects the exact active platform-managed `IntentSpecification` used for validation, governance, and audit. |
| `expression.iri` | Identifies the semantic/expression contract claimed by the runtime expression. |

For submitted admission, `intentSpecification.id` is mandatory. IC MS does not infer the governing runtime validation contract from `expression.iri` alone.

`expression.iri` is also mandatory because it identifies the expression language / ontology / expression contract used for runtime expression validation. IC MS must confirm that the runtime `expression.iri` is consistent with the selected specification's `expressionSpecification.iri`.

`intentSpecification.specKey` and `intentSpecification.name` are optional descriptive/discovery hints only. They are not mandatory and are not authoritative runtime validation keys. If supplied, IC MS may use them for consistency checking or narrowing where supported, but they must not replace `intentSpecification.id`.

Required submitted admission reference:

```json
{
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20"
  },
  "expression": {
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  }
}
```

Unsupported admission request because `intentSpecification.id` is missing:

```json
{
  "expression": {
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  }
}
```

IC MS must not resolve `IntentSpecification` by IRI alone, family, key, name, or inferred payload shape alone for submitted runtime admission.

Baseline:
- submitted admission requires `intentSpecification.id`
- submitted admission requires `expression.iri`
- IC MS resolves the exact `ACTIVE` `IntentSpecification` by `intentSpecification.id`
- IC MS rejects the admission request if `intentSpecification.id` is omitted
- IC MS confirms the request `expression.iri` matches the selected specification's `expressionSpecification.iri`
- `intentSpecification.specKey` and `intentSpecification.name` are optional hints only


### Intent-level lifecycleStatus values:

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

### Intent-version lifecycleStatus values:

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

### LifecycleStatus purpose and projection rule:

`Intent.lifecycleStatus` is the externally visible lifecycle projection for the `Intent` resource. It keeps TMF-facing clients simple by exposing the current public state of the Intent rather than every historical or candidate version state.

Each internal Intent version also has its own version-level `lifecycleStatus`. Version-level lifecycle state is used for version history, restart/reuse decisions, audit, governance, and safe handling of previous versions while another version is the `activeVersion`.

`activeVersion` is the pointer to the Intent version currently driving the top-level `Intent.lifecycleStatus` projection. Do not use `effectiveVersion` or `currentVersion` for this pointer.

`GET /intent/{id}` returns the current projected `Intent` state for that Intent ID. It does not return the full internal version aggregate by default. The returned `version` is the projected runtime version.

Historical version state such as `Standby`, `Retired`, rollback candidates, and previous versions remains internal unless exposed through `IntentReport` or a documented platform extension.

### Draft, submit, and external update rule:

External consumers must not set or patch `lifecycleStatus`. `lifecycleStatus` is assigned, transitioned, and projected by the intent management entity. IA MS determines assurance/runtime meaning and IC MS exposes the projected TMF-facing lifecycle state.

`submit` is an approved IC MS extension request-control field. It is not a lifecycle field. `submit: false` requests that the Intent be saved or kept as `Draft`. `submit: true` requests submission for admission.

If `submit` is omitted on initial create, IC MS treats the request as `submit: true`. If an Intent is persisted with `submit: false`, later omission of `submit` must preserve draft handling and must not automatically submit the Intent. A draft Intent is submitted only when a later request explicitly sets `submit: true`.

While `lifecycleStatus = Draft`, all attributes accepted by the `PUT` / `PATCH` request contract are mutable. The `PUT` / `PATCH` request contract must not expose `lifecycleStatus` as a writable attribute.

`id` is immutable. If `id` appears in a full-replacement `PUT` request, it must match the path `id` and is used only for consistency checking; it cannot be changed.

Response/projection fields such as `href`, `version`, `lifecycleStatus`, `statusReason`, `statusChangeDate`, `activeVersion`, and `_links` are not writable request fields unless explicitly documented otherwise.

Once an Intent leaves `Draft`, general attribute update on that submitted version is not allowed. Material changes after submission require creating a new Draft version, editing that Draft version, and explicitly submitting it with `submit: true`.

Draft Intents are authoring records only. They are not admitted, optimised, assured, sent to downstream change execution, or used to drive `activeVersion`.

### Intent version transition rules:

IC MS must not create another newer version while there is already a newer candidate version in `Acknowledged` or `InProgress`. These states represent an admitted version change that has not yet resolved.

When a newer version becomes the `activeVersion`, previous versions transition as follows:

| Previous version lifecycleStatus | Transition when newer version becomes `activeVersion` |
|---|---|
| `Active` | `Standby` |
| `Degraded` | `Standby` |
| `Paused` | `Standby` |
| `Rejected` | `Terminated` |
| `Failed` | `Terminated` |

`Standby` is a non-active retained version state. It may later re-enter the Intent version change lifecycle only through `Acknowledged`, then `InProgress`, then `Active`. `Standby` may also be explicitly moved to `Terminated`.

`Retired` is an administrative/version-governance archival state. It is reachable only from `Terminated`; it is not a runtime/network operational state and is not exposed as an ordinary external API action.

### Termination rule:

`DELETE /intent/{id}` is treated as termination, not physical deletion.

Runtime `Intent` records are retained for audit, reporting, lifecycle history, and traceability.

### Caching and ETag rules:

- Caching applies only to GET responses.
- Clients may request a fresh GET response with `Cache-Control: no-cache`.
- ETag is used for unsafe-operation concurrency through `If-Match`.
- No caching strategy is baselined for non-GET operations.

### Typed placeholder rule:

When examples abbreviate large repeated sections, keep the field’s real JSON type.

Use array placeholders for arrays and object placeholders for objects.

Example:

```json
{
  "resources": [
    {
      "resourceId": "SYD-PRI-01",
      "roles": [
        "primary"
      ],
      "resourceType": "networkPath",
      "resourceClass": "critical-gold-access",
      "metrics": {
        "benchmark": {
          "latencyMs": 7,
          "availabilityPercent": 99.996,
          "jitterMs": 1.1,
          "packetLossPercent": 0.004
        }
      }
    }
  ],
  "evaluationSummary": {
    "status": "COMPLETED",
    "statusReason": "Selected resource set satisfies the resolved targets and constraints."
  }
}
```

Do not use string placeholders for array/object fields.

---

## 3. Common error body:

```json
{
  "code": "...",
  "reason": "...",
  "message": "...",
  "status": 400,
  "referenceError": "https://mycsp.com.au/errors/...",
  "@type": "Error"
}
```

### Common errors:

| **HTTP** | **Code** | **Scenario** |
|---:|---|---|
| `400` | `BAD_REQUEST` | Invalid JSON or invalid request structure |
| `404` | `RESOURCE_NOT_FOUND` | Intent, IntentReport, or subscription not found |
| `409` | `INVALID_STATE_TRANSITION` | Requested lifecycle/version transition is not allowed |
| `409` | `RESOURCE_CONFLICT` | Runtime update conflicts with current projection state |
| `412` | `PRECONDITION_FAILED` | Supplied `If-Match` does not match the current resource version |
| `422` | `VALIDATION_FAILED` | Runtime Intent fails request-shape/spec validation, misses mandatory `intentSpecification.id`, misses mandatory `expression.iri`, or has an IRI/specification mismatch |
| `422` | `INTENT_SPECIFICATION_NOT_ACTIVE` | Referenced IntentSpecification is not active |
| `428` | `PRECONDITION_REQUIRED` | Required `If-Match` header is missing for an unsafe operation |
| `503` | `SERVICE_UNAVAILABLE` | IC MS DB unavailable or active spec cannot be confirmed |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

### Missing If-Match response:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_REQUIRED",
  "reason": "IF_MATCH_REQUIRED",
  "message": "The If-Match header is required for this operation.",
  "status": 428,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_REQUIRED",
  "@type": "Error"
}
```

### ETag mismatch response:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied ETag does not match the current resource version.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

## 4. Create Intent:

### Request:

```http
POST /intentManagement/v5/intent?fields=id,href,name,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,expression,validFor,isBundle,priority,relatedParty,@type,@baseType
Content-Type: application/json
Accept: application/json
```

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "submit": true,
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
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
          "redundancyRequired": true,
          "timeWindow": {
            "startDateTime": "2026-04-18T12:00:00+10:00"
          }
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    }
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intent/INT-HOSP-2026-001
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
ETag: "intent-INT-HOSP-2026-001-v1"
Last-Modified: Sat, 18 Apr 2026 02:00:00 GMT
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "submit": true,
  "version": "v1",
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Intent request accepted for semantic validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
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
          "redundancyRequired": true,
          "timeWindow": {
            "startDateTime": "2026-04-18T12:00:00+10:00"
          }
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    }
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but PUT is preferred for deterministic full updates."
    }
  }
}
```

### Create as Draft example:

A caller can create an Intent as a draft by setting `submit: false`. A Draft Intent is persisted for authoring only and is not admitted, optimised, assured, or sent to downstream change execution.

```http
POST /intentManagement/v5/intent?fields=id,href,name,humanExpression,submit,version,lifecycleStatus,statusReason,statusChangeDate,@type,@baseType
Content-Type: application/json
Accept: application/json
```

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms.",
  "submit": false,
  "@type": "Intent",
  "@baseType": "Entity"
}
```

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intent/INT-HOSP-2026-001
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
ETag: "intent-INT-HOSP-2026-001-v1"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms.",
  "submit": false,
  "version": "v1",
  "lifecycleStatus": "Draft",
  "statusReason": "Intent saved as draft and not submitted for admission.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Create validation rule:

If `submit` is omitted on create, IC MS treats the request as submitted for admission.

If `submit: false` is supplied, IC MS persists the Intent as `Draft` and does not emit `IntentValidatedEvent`, optimise, assure, or send the Intent to downstream change execution.

If `submit: true` is supplied, IC MS applies the runtime admission profile. IC MS emits `IntentValidatedEvent` after syntactic validation succeeds and the external Intent projection is persisted.

`IntentValidatedEvent` is a state/progress event, not a point-to-point command for a specific consumer.

---

## 5. List Intents:

### Request:

```http
GET /intentManagement/v5/intent?offset=0&limit=10&lifecycleStatus=Active&fields=id,href,name,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,@type,@baseType
Accept: application/json
```

### Request with fresh-read override:

```http
GET /intentManagement/v5/intent?offset=0&limit=10&lifecycleStatus=Active&fields=id,href,name,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
X-Total-Count: 1
X-Result-Count: 1
ETag: "intent-list-active-v21"
Cache-Control: private, max-age=60
```

```json
[
  {
    "id": "INT-HOSP-2026-001",
    "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
    "name": "Sydney Hospital Surgical Connection Intent",
    "version": "v2",
    "lifecycleStatus": "Active",
    "statusReason": "Intent version v2 is active and assurance is healthy.",
    "statusChangeDate": "2026-04-18T12:20:00+10:00",
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec",
      "version": "1.20"
    },
    "@type": "Intent",
    "@baseType": "Entity"
  }
]
```

### Query parameters:

| **Parameter** | **Meaning** |
|---|---|
| `offset` | Zero-based start position |
| `limit` | Maximum number of records |
| `fields` | Optional TMF-aligned field selection / projection parameter |
| `lifecycleStatus` | Filter by projected external lifecycle status |
| `version` | Filter by projected runtime version |
| `intentSpecification.id` | Filter by concrete IntentSpecification ID |

---

## 6. Retrieve Intent:

### Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001?fields=id,href,name,description,humanExpression,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,expression,validFor,isBundle,priority,relatedParty,@type,@baseType
Accept: application/json
```

### Request with fresh-read override:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001?fields=id,href,name,description,humanExpression,version,lifecycleStatus,statusReason,statusChangeDate,intentSpecification,expression,validFor,isBundle,priority,relatedParty,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v3"
Last-Modified: Sat, 18 Apr 2026 02:20:00 GMT
Cache-Control: private, max-age=300
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "version": "v2",
  "lifecycleStatus": "Active",
  "statusReason": "Intent version v2 is active and assurance is healthy.",
  "statusChangeDate": "2026-04-18T12:20:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 8,
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
    }
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    }
  }
}
```

### Not found response:

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
```

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "reason": "INTENT_NOT_FOUND",
  "message": "Intent INT-HOSP-2026-001 was not found.",
  "status": 404,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",
  "@type": "Error"
}
```

---

## 7. Full replace Intent:

### Request:

```http
PUT /intentManagement/v5/intent/INT-HOSP-2026-001?fields=id,href,name,description,humanExpression,submit,intentSpecification,expression,validFor,isBundle,priority,relatedParty,@type,@baseType
Content-Type: application/json
Accept: application/json
If-Match: "intent-INT-HOSP-2026-001-v3"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Updated surgical connection request with lower latency target.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 8 ms and availability at least 99.99%.",
  "submit": false,
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 8,
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
    }
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v4"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Updated surgical connection request with lower latency target.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 8 ms and availability at least 99.99%.",
  "submit": false,
  "version": "v4",
  "lifecycleStatus": "Draft",
  "statusReason": "Draft intent updated and not submitted for admission.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 8,
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
    }
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but PUT is preferred for deterministic full updates."
    }
  }
}
```

### Rule:

`PUT` is a platform extension for deterministic full replacement.

`PUT` is allowed only while the current Intent version is in `Draft`.

For a Draft Intent, all attributes accepted by the `PUT` request contract are mutable. The request contract does not expose `lifecycleStatus` as writable.

`id` is immutable. If `id` is supplied in the `PUT` body, it must match the path `id`; otherwise IC MS returns `409 Conflict` or `400 Bad Request` depending on validation policy.

If `submit: false` is supplied or `submit` is omitted on an existing Draft Intent, the Intent remains `Draft`.

If `submit: true` is supplied, IC MS validates the runtime admission profile and, if accepted, moves the projected lifecycle to `Acknowledged`.

Once an Intent leaves `Draft`, full replacement on that submitted version is not allowed. Material changes require creating a new Draft version.

---

## 8. Partial update Intent:

### Request:

```http
PATCH /intentManagement/v5/intent/INT-HOSP-2026-001?fields=id,href,name,submit,intentSpecification,expression,validFor,isBundle,priority,@type,@baseType
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "intent-INT-HOSP-2026-001-v4"
```

```json
{
  "submit": false,
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 7
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
    }
  }
}
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v5"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Patched surgical connection request with lower latency target.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "submit": false,
  "version": "v5",
  "lifecycleStatus": "Draft",
  "statusReason": "Draft intent patched and not submitted for admission.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 7,
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
    }
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but PUT is preferred for deterministic full updates."
    }
  }
}
```

### Rule:

`PATCH` is supported for TMF compatibility but is not encouraged for ordinary edits where deterministic full replacement through `PUT` is available.

`PATCH` is allowed only while the current Intent version is in `Draft`.

For a Draft Intent, all attributes accepted by the `PATCH` request contract are mutable. The request contract does not expose `id` or `lifecycleStatus` as writable patch attributes.

If `submit: false` is supplied or `submit` is omitted on an existing Draft Intent, the Intent remains `Draft`.

If `submit: true` is supplied, IC MS validates the runtime admission profile and, if accepted, moves the projected lifecycle to `Acknowledged`.

Once an Intent leaves `Draft`, partial update on that submitted version is not allowed. Material changes require creating a new Draft version.

---

## 9. Terminate Intent:

### Request:

```http
DELETE /intentManagement/v5/intent/INT-HOSP-2026-001
Accept: application/json
If-Match: "intent-INT-HOSP-2026-001-v5"
```

### Success response:

```http
HTTP/1.1 202 Accepted
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v6"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "lifecycleStatus": "Terminated",
  "statusReason": "Intent termination requested and accepted.",
  "statusChangeDate": "2026-04-18T13:00:00+10:00",
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Rule:

`DELETE /intent/{id}` is treated as termination, not physical deletion.

The retained Intent record remains available for audit, reporting, lifecycle history, and traceability.

`202 Accepted` is used for TMF-aligned delete/termination acceptance. Callers can use `GET /intent/{id}` to retrieve the retained terminated projection after the termination request is accepted.

---

## 10. List IntentReports:

### Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport?fields=id,href,creationDate,name,intent,expression,@type,@baseType
Accept: application/json
```

### Request with fresh-read override:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport?fields=id,href,creationDate,name,intent,expression,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
X-Total-Count: 1
X-Result-Count: 1
ETag: "intent-report-list-INT-HOSP-2026-001-v3"
Cache-Control: private, max-age=60
```

```json
[
  {
    "id": "IR-INT-HOSP-2026-001-003",
    "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
    "creationDate": "2026-04-18T12:20:00+10:00",
    "name": "Sydney Hospital Surgical Connection Intent Report",
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "expression": {
      "@type": "JsonLdExpression",
      "@baseType": "Expression",
      "iri": "https://mycsp.com.au/tio/hospital-surgical-slice-report/v1.0",
      "expressionValue": {
        "version": "v2",
        "lifecycleStatus": "Active",
        "reportTime": "2026-04-18T12:20:00+10:00",
        "summary": "Intent is active and assurance is healthy.",
        "targetSummary": {
          "targets": [
            {
              "name": "maxLatencyMs",
              "target": 10,
              "observedValue": 8,
              "unit": "ms"
            }
          ]
        },
        "observationSummary": {
          "observedAt": "2026-04-18T12:20:00+10:00"
        }
      }
    },
    "@type": "IntentReport",
    "@baseType": "Entity",
    "_links": {
      "self": {
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003"
      },
      "intent": {
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      }
    }
  }
]
```

---

## 11. Retrieve IntentReport:

### Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003?fields=id,href,creationDate,name,intent,expression,@type,@baseType
Accept: application/json
```

### Request with fresh-read override:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003?fields=id,href,creationDate,name,intent,expression,@type,@baseType
Accept: application/json
Cache-Control: no-cache
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
X-TMF-Native: true
X-Platform-Extension: false
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003
ETag: "intent-report-IR-INT-HOSP-2026-001-003-v1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "IR-INT-HOSP-2026-001-003",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
  "creationDate": "2026-04-18T12:20:00+10:00",
  "name": "Sydney Hospital Surgical Connection Intent Report",
  "intent": {
    "id": "INT-HOSP-2026-001",
    "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice-report/v1.0",
    "expressionValue": {
      "version": "v2",
      "lifecycleStatus": "Active",
      "reportTime": "2026-04-18T12:20:00+10:00",
      "summary": "Intent is active and assurance is healthy.",
      "serviceSummary": {
        "locationId": "AU-NSW-SYD-HOSP-001",
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold"
      },
      "targetSummary": {
        "targets": [
          { "name": "maxLatencyMs", "target": 10, "observedValue": 8, "unit": "ms" },
          { "name": "minAvailabilityPercent", "target": 99.99, "observedValue": 99.995, "unit": "percent" },
          { "name": "maxJitterMs", "target": 2, "observedValue": 1.5, "unit": "ms" },
          { "name": "maxPacketLossPercent", "target": 0.01, "observedValue": 0.005, "unit": "percent" }
        ]
      },
      "observationSummary": {
        "observedAt": "2026-04-18T12:20:00+10:00",
        "resources": [
          {
            "resourceId": "SYD-PRI-01",
            "role": "primary",
            "metrics": {
              "latencyMs": 8,
              "availabilityPercent": 99.995,
              "jitterMs": 1.5,
              "packetLossPercent": 0.005
            }
          },
          {
            "resourceId": "SYD-SEC-01",
            "role": "secondary",
            "metrics": {
              "latencyMs": 10,
              "availabilityPercent": 99.994,
              "jitterMs": 1.8,
              "packetLossPercent": 0.006
            }
          }
        ]
      }
    }
  },
  "@type": "IntentReport",
  "@baseType": "Entity",
  "_links": {
    "self": { "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003" },
    "intent": { "href": "/intentManagement/v5/intent/INT-HOSP-2026-001" },
    "list": { "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport" }
  }
}
```

---

### IntentReport delete posture:

IC MS does not expose ordinary external `DELETE /intentManagement/v5/intent/{intentId}/intentReport/{id}` through NGW or public TMF-compliant consumer APIs by default.

External consumers can list and retrieve `IntentReport` records only. `IntentReport` is a read-only curated report/projection/audit resource for ordinary consumers. It represents externalised assurance and lifecycle reporting history derived from IA MS assurance truth, not a mutable business resource with an independent lifecycle.

IC MS may provide an internal-only governed delete/purge capability for `IntentReport` records. This internal capability is not routed through NGW, not advertised as a public consumer API, and not available to normal external consumers. It is restricted to retention purge, legal deletion, platform administration, approved data-correction workflows, or policy-governed cleanup.

### TMF posture:

TMF921 includes an `IntentReport` delete operation and `IntentReportDeleteEvent` in the API/event model. IC MS intentionally does not expose the delete operation to ordinary external consumers because deleting reports as a normal consumer action would remove audit/projection history and would require introducing a separate report lifecycle such as `Archived` or `Deleted`.

No separate `IntentReport` lifecycle is baselined for ordinary consumer use. Delete/purge is treated as a governed administrative operation, not a normal report lifecycle transition.

If an implementation must expose the TMF report delete route for compatibility, it must be restricted/admin-only or return a policy error such as `403 Forbidden` or `405 Method Not Allowed` for ordinary consumers, depending on gateway/API policy.

### Event posture:

`IntentReportDeleteEvent` remains part of the external TMF-aligned event vocabulary for `IntentReport` alignment.

IC MS emits `IntentReportDeleteEvent` only after successful governed internal/admin removal, where notification is allowed by policy. Valid trigger examples include retention purge, legal deletion, platform administration, approved data correction, or policy-governed cleanup.

`IntentReportDeleteEvent` is not emitted as the result of ordinary external consumer delete because ordinary external consumer delete is not exposed.

---


---

## 12. Hub create subscription:

### Strict TMF route request:

```http
POST /intentManagement/v5/hub
Content-Type: application/json
Accept: application/json
```

```json
{
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription"
}
```

### Domain-scoped platform extension request:

```http
POST /intentManagement/v5/intent/hub
Content-Type: application/json
Accept: application/json
```

```json
{
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription"
}
```

### Success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intent/hub/sub-intent-001
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
ETag: "subscription-sub-intent-001-v1"
```

```json
{
  "id": "sub-intent-001",
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/hub/sub-intent-001"
    }
  }
}
```

### Supported event filters:

```text
IntentCreateEvent
IntentAttributeValueChangeEvent
IntentStatusChangeEvent
IntentDeleteEvent
IntentReportCreateEvent
IntentReportAttributeValueChangeEvent
IntentReportDeleteEvent
```

`IntentReportDeleteEvent` is included in the subscription vocabulary for TMF alignment, but is emitted only for governed internal/admin retention or deletion scenarios, not ordinary external consumer delete.

### Hub notification delivery rule:

Subscribed notifications are delivered as REST webhook callbacks. IC MS sends an HTTP `POST` to the subscriber callback URL using the corresponding external TMF-aligned event payload as the request body. Kafka and CloudEvents headers are not used for this external hub delivery path. Webhook requests use HTTP headers such as `Content-Type`, `X-Correlation-Id`, and subscriber-specific authentication headers where configured.

IC MS records pending webhook deliveries in an IC MS-owned local delivery outbox and retries delivery according to platform retry policy. A subscriber listener should return `204 No Content` when the notification is accepted.

### Example subscriber listener callback:

```http
POST https://consumer.example.com/listener/intent/events HTTP/1.1
Content-Type: application/json
X-Correlation-Id: corr-intent-status-001
```

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

### Subscriber listener success response:

```http
X-TMF-Native: true
X-Platform-Extension: false
HTTP/1.1 204 No Content
```

---

## 13. Hub retrieve subscription:

### Request:

```http
GET /intentManagement/v5/intent/hub/sub-intent-001
Accept: application/json
```

### Request with fresh-read override:

```http
GET /intentManagement/v5/intent/hub/sub-intent-001
Accept: application/json
Cache-Control: no-cache
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
ETag: "subscription-sub-intent-001-v1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "sub-intent-001",
  "callback": "https://consumer.example.com/listener/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/hub/sub-intent-001"
    }
  }
}
```

---

## 14. Hub delete subscription:

### Request:

```http
DELETE /intentManagement/v5/intent/hub/sub-intent-001
If-Match: "subscription-sub-intent-001-v1"
```

### Success response:

```http
X-TMF-Native: true
X-Platform-Extension: false
HTTP/1.1 204 No Content
```

---

## 15. Validation and dependency error examples:

### Missing expression IRI:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "EXPRESSION_IRI_REQUIRED",
  "message": "Runtime Intent create/update requests must include expression.iri so IC MS can resolve the applicable expression contract for runtime validation.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### Missing IntentSpecification ID:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "INTENT_SPECIFICATION_ID_REQUIRED",
  "message": "Submitted runtime Intent admission requires intentSpecification.id to identify the intended active runtime validation contract.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### Referenced specification not active:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "INTENT_SPECIFICATION_NOT_ACTIVE",
  "message": "Referenced IntentSpecification hospital-surgical-slice-spec version 1.20 is not ACTIVE.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### IntentSpecification lookup unavailable:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
Retry-After: 30
```

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "reason": "INTENT_SPECIFICATION_LOOKUP_UNAVAILABLE",
  "message": "Intent creation or update cannot be accepted because the applicable active IntentSpecification could not be confirmed.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/SERVICE_UNAVAILABLE",
  "@type": "Error"
}
```

### ETag mismatch:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied ETag does not match the current resource version.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

### Submitted Intent update not allowed:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
X-TMF-Native: true
X-Platform-Extension: false
```

```json
{
  "code": "INVALID_STATE_TRANSITION",
  "reason": "INTENT_NOT_DRAFT",
  "message": "Intent attributes can be updated only while the Intent is in Draft. Create a new Draft version for material changes after submission.",
  "status": 409,
  "referenceError": "https://mycsp.com.au/errors/INVALID_STATE_TRANSITION",
  "@type": "Error"
}
```

### External event timestamp rule:

External TMF-aligned event examples populate both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp. `timeOccurred` is the platform-corrected spelling used consistently across ID MS and IC MS external event examples. TMF921 examples contain the misspelled `timeOcurred`; this baseline intentionally uses the corrected spelling while preserving the same timestamp semantics.

---

## 16. External Intent event family:

IC MS emits external TMF-aligned resource events for `Intent` projection changes.

| **Event** | **Trigger** |
|---|---|
| `IntentCreateEvent` | Runtime Intent projection created |
| `IntentAttributeValueChangeEvent` | External Intent attributes changed |
| `IntentStatusChangeEvent` | External lifecycle/status projection changed |
| `IntentDeleteEvent` | Runtime Intent termination accepted; retained projection moves to `Terminated` |

These are external projection/resource events only.

They must not expose raw telemetry, raw optimiser decisions, raw `t7.knowledge plane` data, raw callback payloads, internal candidate scoring, or internal Kafka event payloads.

---

## 17. IntentCreateEvent:

```json
{
  "eventId": "evt-intent-create-001",
  "eventTime": "2026-04-18T12:00:00+10:00",
  "timeOccurred": "2026-04-18T12:00:00+10:00",
  "eventType": "IntentCreateEvent",
  "correlationId": "corr-intent-create-001",
  "description": "Intent created.",
  "priority": "Normal",
  "title": "Intent created",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v1",
      "lifecycleStatus": "Acknowledged",
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec",
        "version": "1.20"
      },
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
  "@type": "IntentCreateEvent"
}
```

---

## 18. IntentAttributeValueChangeEvent:

```json
{
  "eventId": "evt-intent-attr-001",
  "eventTime": "2026-04-18T12:40:00+10:00",
  "timeOccurred": "2026-04-18T12:40:00+10:00",
  "eventType": "IntentAttributeValueChangeEvent",
  "correlationId": "corr-intent-attr-001",
  "description": "Intent projected attributes changed.",
  "priority": "Normal",
  "title": "Intent attributes changed",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v4",
      "lifecycleStatus": "Acknowledged",
      "@type": "Intent",
      "@baseType": "Entity"
    },
    "changedAttributes": [
      {
        "name": "expression.targets.maxLatencyMs",
        "oldValue": 8,
        "newValue": 7
      }
    ]
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentAttributeValueChangeEvent"
}
```

---

## 19. IntentStatusChangeEvent:

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

`IntentStatusChangeEvent` carries the current `event.intent.lifecycleStatus` snapshot. It does not carry separate `previousLifecycleStatus` or `newLifecycleStatus` fields in the external event payload. The event type plus the emitted resource snapshot provide the external lifecycle/status-change signal.

---

## 20. IntentDeleteEvent:

`IntentDeleteEvent` represents accepted termination, not physical deletion.

```json
{
  "eventId": "evt-intent-delete-001",
  "eventTime": "2026-04-18T13:00:00+10:00",
  "timeOccurred": "2026-04-18T13:00:00+10:00",
  "eventType": "IntentDeleteEvent",
  "correlationId": "corr-intent-delete-001",
  "description": "Intent termination accepted.",
  "priority": "Normal",
  "title": "Intent terminated",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "version": "v4",
      "lifecycleStatus": "Terminated",
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
  "@type": "IntentDeleteEvent"
}
```

---

## 21. External IntentReport event family:

IC MS emits external TMF-aligned resource events for `IntentReport` projection changes.

| **Event** | **Trigger** |
|---|---|
| `IntentReportCreateEvent` | New `IntentReport` projection created |
| `IntentReportAttributeValueChangeEvent` | Existing `IntentReport` projection updated |
| `IntentReportDeleteEvent` | Governed platform/internal retention purge, administrative removal, legal deletion, or approved data-correction handling |

`IntentReportDeleteEvent` is part of the external TMF-aligned event vocabulary for `IntentReport` alignment. It is not emitted as the result of ordinary external consumer delete because ordinary external `IntentReport` delete is not exposed by default. Reports remain read-only curated projection/audit history for ordinary consumers and may be archived or purged only through governed internal retention or administrative policy where required.

---

## 22. IntentReportCreateEvent:

```json
{
  "eventId": "evt-intent-report-create-001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "timeOccurred": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentReportCreateEvent",
  "correlationId": "corr-intent-report-create-001",
  "description": "IntentReport created.",
  "priority": "Normal",
  "title": "IntentReport created",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-003",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
      "intent": {
        "id": "INT-HOSP-2026-001"
      },
      "version": "v2",
      "lifecycleStatus": "Active",
      "@type": "IntentReport",
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
  "@type": "IntentReportCreateEvent"
}
```

---

## 23. IntentReportAttributeValueChangeEvent:

```json
{
  "eventId": "evt-intent-report-attr-001",
  "eventTime": "2026-04-18T12:25:00+10:00",
  "timeOccurred": "2026-04-18T12:25:00+10:00",
  "eventType": "IntentReportAttributeValueChangeEvent",
  "correlationId": "corr-intent-report-attr-001",
  "description": "IntentReport attributes changed.",
  "priority": "Normal",
  "title": "IntentReport attributes changed",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-003",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
      "intent": {
        "id": "INT-HOSP-2026-001"
      },
      "version": "v2",
      "lifecycleStatus": "Degraded",
      "@type": "IntentReport",
      "@baseType": "Entity"
    },
    "changedAttributes": [
      {
        "name": "lifecycleStatus",
        "oldValue": "Active",
        "newValue": "Degraded"
      }
    ]
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentReportAttributeValueChangeEvent"
}
```

---

## 24. IntentReportDeleteEvent:

`IntentReportDeleteEvent` represents governed internal/admin removal, not ordinary external consumer delete.

```json
{
  "eventId": "evt-intent-report-delete-001",
  "eventTime": "2026-04-18T13:30:00+10:00",
  "timeOccurred": "2026-04-18T13:30:00+10:00",
  "eventType": "IntentReportDeleteEvent",
  "correlationId": "corr-intent-report-delete-001",
  "description": "IntentReport removed by governed retention policy.",
  "priority": "Normal",
  "title": "IntentReport removed",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-003",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
      "intent": {
        "id": "INT-HOSP-2026-001"
      },
      "@type": "IntentReport",
      "@baseType": "Entity"
    },
    "removalReason": "RETENTION_PURGE"
  },
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "Intent Controller MS"
  },
  "@type": "IntentReportDeleteEvent"
}
```

---

## 25. Internal Kafka event publication note:

IC MS publishes `IntentValidatedEvent` internally after syntactic validation and admission.

This is not a point-to-point command for a single consumer.

It is a platform state/progress event meaning the runtime Intent has passed IC MS syntactic validation and has been admitted into the Intent lifecycle.

Current primary consumer is II MS / `intent-intelligence-ms`, but the event may be consumed by other authorised internal consumers where useful.

Internal publication uses the IC MS internal event outbox and Kafka relay. Kafka records use the platform CloudEvents-style header model. This internal Kafka publication path is separate from external hub notification delivery.

Typical internal Kafka headers are:

| Header | Meaning |
|---|---|
| `ce-specversion` | CloudEvents specification version. |
| `ce-id` | Stable event identifier. |
| `ce-source` | Producing service, typically `intent-controller-ms`. |
| `ce-type` | Internal event type, for example `IntentValidatedEvent`. |
| `ce-time` | Event occurrence timestamp. |
| `ce-subject` | Runtime intent identifier where applicable. |
| `ce-correlationid` | Correlation identifier for tracing. |
| `content-type` | Event payload content type, usually `application/json`. |

External hub notifications do not use these Kafka headers. They are HTTP webhook calls and use HTTP headers.

---

## 26. Final specification notes:

- `GET /intent/{id}` returns current projected Intent state, not a full internal version aggregate.
- `GET /intent` lists current projected Intent states for retained Intent IDs.
- Submitted runtime create/update admission requires both mandatory `intentSpecification.id` and mandatory `expression.iri`.
- `intentSpecification.id` selects the exact active platform-managed specification.
- `expression.iri` identifies the semantic/expression contract and must match the selected specification's `expressionSpecification.iri`.
- IC MS does not admit by IRI-only resolution.
- `intentSpecification.specKey` and `intentSpecification.name` are optional hints only and are not authoritative runtime validation keys.
- IC MS must not resolve `IntentSpecification` by family, key, name, or inferred payload shape alone.

Baseline:
- `expression.iri` is mandatory.
- `intentSpecification.id` is mandatory for submitted admission.
- `intentSpecification.specKey` and `intentSpecification.name` are optional hints only.
- `expression.iri` is the semantic/expression contract identifier and must match the selected specification's `expressionSpecification.iri`.
- Normal governance expects one matching `ACTIVE` `IntentSpecification` per expression IRI; ambiguity or no match is rejected.
- `DELETE /intent/{id}` is termination, not physical deletion.
- `submit` is an approved IC MS extension request-control field; `submit: false` saves or keeps an Intent as `Draft`, and `submit: true` submits it for admission.
- If `submit` is omitted on initial create, IC MS treats the request as submitted for admission.
- If an Intent is already persisted with `submit: false`, later omission of `submit` preserves Draft handling and must not automatically submit the Intent.
- External consumers must not set or patch `lifecycleStatus`; lifecycle is assigned, transitioned, and projected by the intent management entity.
- `PUT /intent/{id}` is a platform extension for deterministic full replacement and is allowed only while the current Intent version is in `Draft`.
- `PATCH /intent/{id}` is supported for TMF compatibility and is allowed only while the current Intent version is in `Draft`.
- Once an Intent leaves `Draft`, material changes require creating a new Draft version.
- ETag is used for unsafe-operation concurrency through `If-Match`.
- GET responses may use bounded private caching.
- Clients may request a fresh GET using `Cache-Control: no-cache`.
- `IntentDeleteEvent` represents termination acceptance, not physical deletion.
- External `Intent` events and `IntentReport` events are curated projection events and must not expose raw telemetry, raw callback payloads, raw optimiser details, raw knowledge-plane data, or internal candidate scoring.
- External event examples include both `eventTime` and `timeOccurred` with the same canonical event occurrence timestamp.
- IC MS does not expose ordinary external `DELETE /intent/{intentId}/intentReport/{id}` by default; IntentReport is read-only audit/projection history and is retained unless governed internal retention policy archives or purges it.

## Shared semantic bucket baseline:

### Runtime Intent expression:

IC MS accepts and projects runtime Intent resources using the external runtime expression shape baselined by ID MS:

```json
{
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {},
        "constraints": {},
        "preferences": {}
      }
    }
  }
}
```

`location`, `serviceType`, and `serviceClass` are not peer fields beside `targets`, `constraints`, and `preferences`. They are modelled under `expression.expressionValue.context.constraints` because they restrict what and where the intent must fulfil.

### Complete POST /intent request body example:

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "submit": true,
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec",
    "version": "1.20"
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
          "redundancyRequired": true,
          "timeWindow": {
            "startDateTime": "2026-04-18T12:00:00+10:00"
          }
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    }
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Complete IntentValidatedEvent body example:

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Acknowledged",
    "statusReason": "Intent request passed IC MS admission validation and was admitted for downstream processing.",
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec",
      "version": "1.20"
    },
    "expression": {
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
      "correlationId": "corr-intent-create-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec",
        "version": "1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec?version=1.20"
      }
    }
  }
}
```

### Baseline rules:

- External runtime `Intent.expression.expressionValue` uses the `context` wrapper.
- `context` contains only `targets`, `constraints`, and `preferences`.
- `location`, `serviceType`, and `serviceClass` sit under `context.constraints`.
- `IntentValidatedEvent.body.expression` carries the same canonical semantic buckets internally without the external TMF expression wrapper.
- IC MS validates syntactic shape against the active ID MS `expressionSpecification` and `targetEntitySchema`.
- IC MS does not perform semantic/KP validation, optimisation, change execution, or assurance.
