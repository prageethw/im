## IC MS Design Baseline:

### Purpose:

The Intent Controller MS, referred to as **IC MS**, owns the runtime `Intent` resource and the externally visible runtime intent lifecycle projection.

IC MS provides the main runtime Intent API surface under `/intentManagement/v5/intent`.

It accepts runtime intent creation requests, validates them syntactically against an `ACTIVE` `IntentSpecification`, persists the canonical `Intent`, emits internal workflow events, exposes retrieve/list/report APIs, and projects externally visible TMF-style lifecycle/status updates.

IC MS does **not** own design-time `IntentSpecification` governance. That is owned by ID MS.

## Service Identity:

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Controller MS |
| Service name | `intent-controller-ms` |
| Short name | IC MS |
| Primary runtime resource | `Intent` |
| Related runtime resource | `IntentReport` |
| Base path | `/intentManagement/v5/intent` |
| Hub path | `/intentManagement/v5/intent/hub` |
| API style | TMF-aligned REST |
| Source-of-truth database | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| Event style | External TMF-aligned events; internal CloudEvents where needed |
| Main responsibility | Runtime intent control and external lifecycle projection |

## Core Responsibilities:

| **Responsibility** | **Detail** |
|---|---|
| Runtime Intent source of truth | Owns persisted `Intent` resources |
| Intent creation | Supports `POST /intentManagement/v5/intent` |
| Intent retrieval | Supports `GET /intentManagement/v5/intent/{id}` |
| Intent listing | Supports `GET /intentManagement/v5/intent` where required |
| Intent versioning | Maintains runtime Intent versions and effective version metadata |
| External lifecycle projection | Projects lifecycle/status based on internal assurance/workflow events |
| IntentReport ownership | Owns externally visible reports/status projections where applicable |
| Event subscription management | Supports `/intent/hub` subscriptions |
| External event publication | Emits TMF-aligned `IntentCreateEvent`, `IntentAttributeValueChangeEvent`, and lifecycle/status events where required |
| Internal workflow publication | Emits internal `IntentValidatedEvent` after successful runtime intent validation |
| Concurrency control | Uses ETag and If-Match where applicable |
| Auditability | Maintains timestamps, lifecycle state, version metadata, and correlation context |

## IC MS Does Not Own:

| **Concern** | **Owner** |
|---|---|
| Design-time `IntentSpecification` lifecycle | ID MS |
| IntentSpecification CRUD APIs | ID MS |
| Intent semantic interpretation/resolution | II MS |
| Candidate path/resource resolution | II MS / Knowledge Plane |
| Optimisation decision | IO MS |
| Runtime assurance evaluation | IA MS |
| Raw orchestrator callback ingestion | ICB MS |
| Raw callback lifecycle mapping | IA MS |
| Network apply/orchestration execution | Orchestration layer / network orchestrator |
| Knowledge Plane config ownership | Knowledge Plane operating model |
| OEX user experience | OEX layer |

## API Contract Baseline:

### Resource Path:

```text
/intentManagement/v5/intent
```

### Supported Operations:

| **Operation** | **Method / Path** | **Purpose** | **Baseline Status** |
|---|---|---|---|
| Create Intent | `POST /intentManagement/v5/intent` | Create a new runtime `Intent` after syntactic validation against an active `IntentSpecification` | Baselined |
| List Intents | `GET /intentManagement/v5/intent` | Return runtime Intent resources | Candidate / expected |
| Retrieve Intent | `GET /intentManagement/v5/intent/{id}` | Retrieve one canonical runtime `Intent` resource | Baselined |
| Full update Intent | `PUT /intentManagement/v5/intent/{id}` | Future candidate; lifecycle-sensitive | Not fully baselined |
| Partial update Intent | `PATCH /intentManagement/v5/intent/{id}` | Future candidate; lifecycle-sensitive | Not fully baselined |
| Cancel / terminate Intent | `DELETE /intentManagement/v5/intent/{id}` or action endpoint | Needs lifecycle design | Pending |
| Create hub subscription | `POST /intentManagement/v5/intent/hub` | Subscribe to runtime Intent events | Baselined |
| Delete hub subscription | `DELETE /intentManagement/v5/intent/hub/{id}` | Remove runtime Intent event subscription | Baselined |

## Runtime Intent Resource Baseline:

### Resource Type:

Use:

```json
{
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Surgical Hospital Runtime Intent Baseline:

For the surgical hospital slice examples, use:

| **Field / Rule** | **Baseline** |
|---|---|
| Intent specification | References `hospital-surgical-slice-spec-v1.19` |
| Priority field | Use `priority`, not `priority_level` |
| Human expression | Include `humanExpression` |
| Latency | Use `latency <= 10` style intent expression |
| Availability | Use `availability >= 99.99` style intent expression |
| Validity | Include both `validFor.startDateTime` and `validFor.endDateTime` |
| Resource type | `@type: Intent` |
| Base type | `@baseType: Entity` |

## Create Intent Operation Baseline:

### Endpoint:

```http
POST /intentManagement/v5/intent HTTP/1.1
Host: api.mycsp.com.au
Content-Type: application/json
Accept: application/json
Content-Language: en-AU
correlationid: corr-icms-20260504-001
```

### Behaviour:

| **Concern** | **Baseline** |
|---|---|
| Owner | IC MS |
| Success response | `201 Created` |
| ID assignment | Server-assigned `id` |
| Location header | Required |
| ETag | Mandatory |
| Validation | Syntactic validation against an `ACTIVE` `IntentSpecification` |
| Semantic validation | Not owned by IC MS; II MS / Knowledge Plane owns semantic interpretation |
| Internal event | Emit `IntentValidatedEvent` after successful validation/persistence |
| External event | Emit `IntentCreateEvent` where subscription policy requires |
| Persistence | Managed PostgreSQL-compatible RDBMS |
| Response body | Full returned canonical `Intent` representation |

### Create Request Shape:

```json
{
  "@type": "Intent",
  "@baseType": "Entity",
  "name": "Hospital surgical slice intent",
  "description": "Request a low-latency and high-availability network slice for surgical hospital services.",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.19",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
    "version": "1.19"
  },
  "humanExpression": "Provide a clinical-critical surgical slice for Sydney Hospital with latency <= 10 ms and availability >= 99.99%.",
  "expression": {
    "location": {
      "locationId": "sydney-hospital",
      "locationType": "hospital"
    },
    "serviceClass": "surgical-slice",
    "priority": "clinical-critical",
    "maxLatencyMs": 10,
    "minAvailabilityPercent": 99.99,
    "redundancyRequired": true,
    "preferredAccessTechnology": "5G"
  },
  "validFor": {
    "startDateTime": "2026-05-04T12:00:00+10:00",
    "endDateTime": "2026-05-04T18:00:00+10:00"
  }
}
```

### Create Success Response Headers:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Language: en-AU
Location: /intentManagement/v5/intent/INT-HOSP-2026-001
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "icms-intent-INT-HOSP-2026-001-rev-001"
Last-Modified: Mon, 04 May 2026 12:00:00 GMT
correlationid: corr-icms-20260504-001
```

### Create Success Response Body:

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "@type": "Intent",
  "@baseType": "Entity",
  "name": "Hospital surgical slice intent",
  "description": "Request a low-latency and high-availability network slice for surgical hospital services.",
  "lifecycleStatus": "InProgress",
  "version": "1.0",
  "effectiveVersion": null,
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.19",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
    "version": "1.19"
  },
  "humanExpression": "Provide a clinical-critical surgical slice for Sydney Hospital with latency <= 10 ms and availability >= 99.99%.",
  "expression": {
    "location": {
      "locationId": "sydney-hospital",
      "locationType": "hospital"
    },
    "serviceClass": "surgical-slice",
    "priority": "clinical-critical",
    "maxLatencyMs": 10,
    "minAvailabilityPercent": 99.99,
    "redundancyRequired": true,
    "preferredAccessTechnology": "5G"
  },
  "validFor": {
    "startDateTime": "2026-05-04T12:00:00+10:00",
    "endDateTime": "2026-05-04T18:00:00+10:00"
  },
  "creationDate": "2026-05-04T12:00:00+10:00",
  "lastUpdate": "2026-05-04T12:00:00+10:00",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "report": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/report"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility, but lifecycle-sensitive changes should use governed full update or versioning patterns."
    }
  }
}
```

## Retrieve Intent Operation Baseline:

### Endpoint:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
Accept-Language: en-AU
Cache-Control: no-cache
correlationid: corr-icms-20260504-002
```

### Behaviour:

| **Concern** | **Baseline** |
|---|---|
| Owner | IC MS |
| Success response | `200 OK` |
| Response body | Full canonical externally visible `Intent` resource |
| `Content-Location` | Required |
| `ETag` | Mandatory |
| Cache-Control | Default private caching |
| HATEOAS | Include state-appropriate `_links` |
| Runtime state source | IC MS lifecycle projection state |

### Retrieve Success Response Headers:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "icms-intent-INT-HOSP-2026-001-rev-004"
Last-Modified: Mon, 04 May 2026 12:10:00 GMT
Cache-Control: private, max-age=60
correlationid: corr-icms-20260504-002
```

### Retrieve Success Response Body:

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "@type": "Intent",
  "@baseType": "Entity",
  "name": "Hospital surgical slice intent",
  "description": "Request a low-latency and high-availability network slice for surgical hospital services.",
  "lifecycleStatus": "Active",
  "version": "1.0",
  "effectiveVersion": "1.0",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.19",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
    "version": "1.19"
  },
  "humanExpression": "Provide a clinical-critical surgical slice for Sydney Hospital with latency <= 10 ms and availability >= 99.99%.",
  "expression": {
    "location": {
      "locationId": "sydney-hospital",
      "locationType": "hospital"
    },
    "serviceClass": "surgical-slice",
    "priority": "clinical-critical",
    "maxLatencyMs": 10,
    "minAvailabilityPercent": 99.99,
    "redundancyRequired": true,
    "preferredAccessTechnology": "5G"
  },
  "validFor": {
    "startDateTime": "2026-05-04T12:00:00+10:00",
    "endDateTime": "2026-05-04T18:00:00+10:00"
  },
  "creationDate": "2026-05-04T12:00:00+10:00",
  "lastUpdate": "2026-05-04T12:10:00+10:00",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "report": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/report"
    }
  }
}
```

## Runtime Lifecycle Baseline:

### Lifecycle States:

| **State** | **Meaning** |
|---|---|
| `InProgress` | Intent accepted and workflow is progressing |
| `Active` | Intent is active/effective in the network/service |
| `Degraded` | Intent is still effective but assurance indicates degraded conditions |
| `Failed` | Intent failed after being attempted or active |
| `Terminated` | Intent has been terminated |
| `Rejected` | Intent cannot be processed/resolved/accepted under validation or policy rules |

### Effective Version Rule:

Once an Intent version becomes `Active`, it becomes the `effectiveVersion`.

It remains the `effectiveVersion` even if its lifecycle later moves to `Degraded`, `Paused`, or `Failed`.

`effectiveVersion` changes only when another version is confirmed `Active` in the network/service.

## Internal Event Baseline:

### IntentValidatedEvent:

IC MS emits `IntentValidatedEvent` after it successfully creates and syntactically validates a runtime `Intent`.

| **Area** | **Baseline** |
|---|---|
| Emitting MS | IC MS |
| Consuming MS | II MS |
| Purpose | Start interpretation/resolution workflow |
| Metadata | CloudEvents headers |
| Body wrapper | Top-level `body` |
| Topic | `t7.intent.management.events` |
| Payload style | Plain internal JSON |
| Correlation header | `correlationid` |
| Content type | `content-type: application/json` |

Indicative payload:

```json
{
  "body": {
    "eventType": "IntentValidatedEvent",
    "eventVersion": "1.0",
    "source": "intent-controller-ms",
    "eventTime": "2026-05-04T12:00:01+10:00",
    "correlationId": "corr-icms-20260504-001",
    "intentId": "INT-HOSP-2026-001",
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.19",
      "version": "1.19"
    },
    "request": {
      "location": {
        "locationId": "sydney-hospital",
        "locationType": "hospital"
      },
      "service": {
        "serviceClass": "surgical-slice"
      },
      "constraints": {
        "maxLatencyMs": 10,
        "minAvailabilityPercent": 99.99
      },
      "policyInputs": {
        "priority": "clinical-critical"
      }
    },
    "references": {
      "intent": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

## Assurance and Lifecycle Projection:

IC MS consumes or receives lifecycle-driving internal events, especially `IntentAssuranceEvent`, to update the external runtime `Intent` lifecycle/status.

| **Input Event** | **Emitted By** | **IC MS Responsibility** |
|---|---|---|
| `IntentAssuranceEvent` | IA MS | Project external lifecycle/status on the runtime `Intent` |
| `IntentDriftOccurredEvent` | IA MS | May influence projected status where required |
| `IntentRejectedEvent` | II MS | Project rejected state |
| `IntentNetworkReadyEvent` | II MS | May support workflow/status transition depending on implementation |

IC MS does not perform runtime assurance calculation. IA MS owns assurance truth.

## External Event Subscription Baseline:

### Hub Paths:

```text
/intentManagement/v5/intent/hub
/intentManagement/v5/intent/hub/{id}
```

### Create Subscription:

```http
POST /intentManagement/v5/intent/hub HTTP/1.1
Host: api.mycsp.com.au
Content-Type: application/json
Accept: application/json
Content-Language: en-AU
correlationid: corr-icms-hub-001
```

```json
{
  "callback": "https://consumer.example.com/listener/intentCreateEvent",
  "query": "eventType=IntentCreateEvent"
}
```

### Create Subscription Response:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Language: en-AU
Location: /intentManagement/v5/intent/hub/sub-icms-001
Content-Location: /intentManagement/v5/intent/hub/sub-icms-001
ETag: "icms-intent-hub-sub-001-rev-001"
Last-Modified: Mon, 04 May 2026 12:05:00 GMT
correlationid: corr-icms-hub-001
```

```json
{
  "id": "sub-icms-001",
  "callback": "https://consumer.example.com/listener/intentCreateEvent",
  "query": "eventType=IntentCreateEvent",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/hub/sub-icms-001"
    },
    "delete": {
      "href": "/intentManagement/v5/intent/hub/sub-icms-001",
      "method": "DELETE"
    }
  }
}
```

### Delete Subscription:

```http
DELETE /intentManagement/v5/intent/hub/sub-icms-001 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
If-Match: "icms-intent-hub-sub-001-rev-001"
correlationid: corr-icms-hub-002
```

### Delete Subscription Response:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
correlationid: corr-icms-hub-002
```

### Subscription Events:

| **Event Type** | **Purpose** |
|---|---|
| `IntentCreateEvent` | Runtime Intent created |
| `IntentAttributeValueChangeEvent` | Runtime Intent attribute changed |
| `IntentStatusChangeEvent` | Runtime Intent lifecycle/status changed |
| `IntentDeleteEvent` | Runtime Intent deleted/terminated where applicable |

## External Event Baseline:

### IntentCreateEvent:

IC MS external `IntentCreateEvent` is TMF-aligned and delivered to subscriber-owned listener endpoints through the `/intent/hub` model.

| **Area** | **Baseline** |
|---|---|
| Delivery model | At-least-once |
| Consumer behaviour | Deduplicate using stable event ID |
| Event body | TMF-style event envelope |
| Resource payload | Runtime `Intent` inside `event.intent` |
| Reporting system | `intent-controller-ms` |
| Source | `intent-controller-ms` |

### IntentAttributeValueChangeEvent:

IC MS external `IntentAttributeValueChangeEvent` is TMF-aligned and delivered through `/intent/hub`.

It is a **design/runtime declarative resource event** reflecting changes to externally visible Intent attributes.

It is not raw telemetry, not callback state, and not internal assurance state.

## Persistence Baseline:

IC MS follows the active IME DB baseline.

| **Concern** | **Baseline** |
|---|---|
| DB type | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| DB ownership | Dedicated IC MS DB instance or logical managed DB boundary |
| Shared cross-MS DB | Not allowed |
| Schema migration | Flyway or Liquibase |
| Manual schema change | Not permitted |
| Future DR | Cross-region active-passive DR path required |

### Indicative Tables:

| **Table** | **Purpose** |
|---|---|
| `intent` | Canonical runtime Intent records |
| `intent_version` | Runtime version history where separated |
| `intent_report` | Runtime reports / projections |
| `intent_hub_subscription` | `/intent/hub` subscription records |
| `intent_outbox` | Reliable event publication if IC MS owns event relay |
| `intent_audit` | Audit history if not platform-provided |
| `shedlock` | Relay coordination if IC MS runs clustered outbox relay |

## Security Baseline:

| **Concern** | **Baseline** |
|---|---|
| External access | Through Gateway |
| Authentication | Gateway-managed |
| Authorisation | IC MS enforces resource/action-level authorisation where required |
| Direct exposure | IC MS should not be directly exposed externally |
| Correlation | IC MS must log and propagate correlation context |
| Input validation | Validate request shape against active specification |
| Audit | Record governed runtime changes |

## Observability Baseline:

### Logs:

| **Log Event** | **Purpose** |
|---|---|
| `intent_create_requested` | Runtime create request received |
| `intent_created` | Runtime Intent persisted |
| `intent_validation_failed` | Syntactic validation failed |
| `intent_validated_event_published` | Internal validation event emitted |
| `intent_lifecycle_projected` | External lifecycle/status updated |
| `intent_retrieve_requested` | Retrieve request received |
| `intent_hub_subscription_created` | Hub subscription created |
| `intent_hub_subscription_deleted` | Hub subscription deleted |
| `intent_event_published` | External event published |
| `intent_event_publish_failed` | Event delivery/publish failed |

### Metrics:

| **Metric** | **Purpose** |
|---|---|
| `ic_intent_create_total` | Count runtime creates |
| `ic_intent_create_failure_total` | Count create failures |
| `ic_intent_validation_failure_total` | Count validation failures |
| `ic_intent_lifecycle_projection_total` | Count lifecycle projections |
| `ic_intent_retrieve_total` | Count retrieves |
| `ic_hub_subscription_total` | Active subscription count |
| `ic_event_publish_total` | Events published |
| `ic_event_publish_failure_total` | Event publish failures |
| `ic_api_latency_ms` | API latency |

## Error Handling Baseline:

### Standard Error Body:

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "Precondition Failed",
  "message": "The supplied ETag does not match the current resource version.",
  "status": 412,
  "@type": "Error"
}
```

### Key Error Responses:

| **Scenario** | **HTTP Status** |
|---|---|
| Invalid request shape | `400 Bad Request` |
| Unknown or inactive IntentSpecification | `400 Bad Request` or `422 Unprocessable Entity` depending on final API policy |
| Unauthorised | `401 Unauthorized` |
| Forbidden | `403 Forbidden` |
| Resource not found | `404 Not Found` |
| Duplicate client-provided external reference | `409 Conflict` where applicable |
| Unsupported media type | `415 Unsupported Media Type` |
| Missing `If-Match` where required | `428 Precondition Required` |
| Stale `If-Match` | `412 Precondition Failed` |
| Lifecycle transition not allowed | `409 Conflict` |
| Internal failure | `500 Internal Server Error` |
| Dependency unavailable | `503 Service Unavailable` |

## Open Items:

| **Open Item** | **Status** |
|---|---|
| Full `GET /intent` list request/response baseline | Pending |
| Full `IntentReport` API baseline | Pending |
| Runtime update/versioning endpoint design | Pending |
| Intent cancellation/termination API design | Pending |
| Exact lifecycle projection mapping from IA events | Pending refinement |
| IC MS event relay implementation detail | Pending platform event delivery design |
| Exact authorisation rules | Pending security architecture decision |
| Rate limits and API quotas | Pending gateway/API platform decision |

## Active Baseline Summary:

IC MS is the source-of-truth service for runtime `Intent` and externally visible lifecycle projection.

It exposes runtime APIs under:

```text
/intentManagement/v5/intent
```

It uses:

- `@type: Intent`
- `@baseType: Entity`
- server-assigned `id`
- mandatory ETags
- `Content-Location`
- default private caching for retrieve
- `/intent/hub` subscriptions
- TMF-aligned external events
- internal CloudEvents with top-level `body`
- `priority`, not `priority_level`
- `humanExpression`
- `validFor.startDateTime` and `validFor.endDateTime`

IC MS validates runtime intent syntax against an active `IntentSpecification`.

II MS and Knowledge Plane own semantic interpretation and resolution.

IO MS owns optimisation.

IA MS owns runtime assurance.

ICB MS owns raw callback ingestion.
