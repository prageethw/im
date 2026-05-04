# IC MS Specification:

## Purpose:

This specification defines the Intent Controller MS (IC MS) runtime API surface, interfaces, request/response examples, headers, and baseline event/subscription behaviour.

IC MS owns runtime `Intent` resources, runtime lifecycle projection, `IntentReport` where applicable, and `/intent/hub` subscriptions.

IC MS does not own design-time `IntentSpecification` governance. ID MS owns `IntentSpecification`.

## Service Identity:

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Controller MS |
| Service name | `intent-controller-ms` |
| Short name | IC MS |
| Primary resource | `Intent` |
| Related resource | `IntentReport` |
| Base path | `/intentManagement/v5/intent` |
| Hub path | `/intentManagement/v5/intent/hub` |
| API style | TMF-aligned REST |
| Source-of-truth database | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| Event style | External TMF-aligned events; internal CloudEvents where needed |

## Interface Summary:

| **Interface** | **Method / Path** | **Purpose** | **Baseline Status** |
|---|---|---|---|
| Create Intent | `POST /intentManagement/v5/intent` | Create a runtime `Intent` after syntactic validation against an ACTIVE `IntentSpecification` | Baselined |
| List Intents | `GET /intentManagement/v5/intent` | Return a top-level array of runtime `Intent` resources | Draft baseline |
| Retrieve Intent | `GET /intentManagement/v5/intent/{id}` | Retrieve one canonical runtime `Intent` resource | Baselined |
| Retrieve IntentReport | `GET /intentManagement/v5/intent/{id}/report` | Retrieve externally visible runtime report/projection for one intent | Draft baseline |
| Create hub subscription | `POST /intentManagement/v5/intent/hub` | Subscribe to runtime `Intent*Event` notifications | Baselined |
| Retrieve hub subscription | `GET /intentManagement/v5/intent/hub/{id}` | Retrieve one runtime intent hub subscription | Draft baseline |
| Delete hub subscription | `DELETE /intentManagement/v5/intent/hub/{id}` | Remove one runtime intent hub subscription | Baselined |

## Interface-Level Rules:

| **Area** | **Baseline** |
|---|---|
| Resource owner | IC MS / `intent-controller-ms` |
| Primary resource | `Intent` |
| Base path | `/intentManagement/v5/intent` |
| Hub path | `/intentManagement/v5/intent/hub` |
| API style | TMF-aligned REST |
| Response model | Full resource body for create/retrieve; top-level array for list; `204 No Content` for delete subscription success |
| ETag | Mandatory for create, retrieve, list, report retrieve, and subscription create/retrieve responses |
| If-Match | Required for `DELETE /intent/hub/{id}` and future unsafe update/delete operations |
| Runtime Intent ID | Server assigned |
| Runtime syntax validation | IC MS validates against an ACTIVE `IntentSpecification` |
| Semantic/policy validation | II MS and Knowledge Plane, not IC MS |
| Runtime assurance | IA MS, not IC MS |
| Priority field | `priority`, not `priority_level` |
| External event delivery | At-least-once; consumers deduplicate using stable `eventId` |

## Runtime Intent Resource Baseline:

Use:

```json
{
  "@type": "Intent",
  "@baseType": "Entity"
}
```

For surgical hospital slice examples:

| **Field / Rule** | **Baseline** |
|---|---|
| IntentSpecification reference | `hospital-surgical-slice-spec-v1.19` |
| Priority field | `priority`, not `priority_level` |
| Human expression | Include `humanExpression` |
| Latency expression | `maxLatencyMs: 10`, equivalent to latency <= 10 ms |
| Availability expression | `minAvailabilityPercent: 99.99`, equivalent to availability >= 99.99% |
| Validity | Include both `validFor.startDateTime` and `validFor.endDateTime` |
| Resource type | `@type: Intent` |
| Base type | `@baseType: Entity` |

## Create Intent:

### Request:

```http
POST /intentManagement/v5/intent HTTP/1.1
Host: api.mycsp.com.au
Content-Type: application/json
Accept: application/json
Content-Language: en-AU
correlationid: corr-icms-20260504-001
```

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
  "humanExpression": "Provide a critical surgical slice for Sydney Hospital with latency <= 10 ms and availability >= 99.99%.",
  "expression": {
    "location": {
      "locationId": "sydney-hospital",
      "locationType": "hospital"
    },
    "serviceClass": "surgical-slice",
    "priority": "critical",
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

### Successful Response:

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
  "humanExpression": "Provide a critical surgical slice for Sydney Hospital with latency <= 10 ms and availability >= 99.99%.",
  "expression": {
    "location": {
      "locationId": "sydney-hospital",
      "locationType": "hospital"
    },
    "serviceClass": "surgical-slice",
    "priority": "critical",
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

### Behaviour:

| **Concern** | **Baseline** |
|---|---|
| Owner | IC MS |
| Success response | `201 Created` |
| ID assignment | Server assigned |
| ETag | Mandatory |
| Validation | Syntactic validation against an ACTIVE IntentSpecification |
| Semantic validation | II MS / Knowledge Plane, not IC MS |
| Internal event | Emit `IntentValidatedEvent` after successful validation/persistence |
| External event | Emit `IntentCreateEvent` where subscription policy requires |

## List Intents:

### Request:

```http
GET /intentManagement/v5/intent?lifecycleStatus=Active&limit=20&offset=0 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
Accept-Language: en-AU
Cache-Control: no-cache
correlationid: corr-icms-20260504-002
```

### Successful Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intent?lifecycleStatus=Active&limit=20&offset=0
X-Total-Count: 1
X-Result-Count: 1
ETag: "icms-intent-list-active-rev-012"
Last-Modified: Mon, 04 May 2026 12:10:00 GMT
Cache-Control: private, max-age=60
correlationid: corr-icms-20260504-002
```

```json
[
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
    "humanExpression": "Provide a critical surgical slice for Sydney Hospital with latency <= 10 ms and availability >= 99.99%.",
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
]
```

### Behaviour:

| **Concern** | **Baseline** |
|---|---|
| Owner | IC MS |
| Success response | `200 OK` |
| Response body | Top-level array of Intent resources |
| Wrapper object | None |
| Headers | `X-Total-Count`, `X-Result-Count`, `ETag`, `Last-Modified`, `Content-Location` |
| Caching | Private cache by default |

## Retrieve Intent:

### Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
Accept-Language: en-AU
Cache-Control: no-cache
correlationid: corr-icms-20260504-003
```

### Successful Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "icms-intent-INT-HOSP-2026-001-rev-004"
Last-Modified: Mon, 04 May 2026 12:10:00 GMT
Cache-Control: private, max-age=60
correlationid: corr-icms-20260504-003
```

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
  "humanExpression": "Provide a critical surgical slice for Sydney Hospital with latency <= 10 ms and availability >= 99.99%.",
  "expression": {
    "location": {
      "locationId": "sydney-hospital",
      "locationType": "hospital"
    },
    "serviceClass": "surgical-slice",
    "priority": "critical",
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

### Behaviour:

| **Concern** | **Baseline** |
|---|---|
| Owner | IC MS |
| Success response | `200 OK` |
| Response body | Full canonical externally visible Intent resource |
| ETag | Mandatory |
| Content-Location | Required |
| Runtime state source | IC MS lifecycle projection state |

## Retrieve IntentReport:

### Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/report HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
Accept-Language: en-AU
Cache-Control: no-cache
correlationid: corr-icms-20260504-004
```

### Successful Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001/report
ETag: "icms-intent-report-INT-HOSP-2026-001-rev-003"
Last-Modified: Mon, 04 May 2026 12:10:30 GMT
Cache-Control: private, max-age=30
correlationid: corr-icms-20260504-004
```

```json
{
  "id": "IR-INT-HOSP-2026-001-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/report",
  "@type": "IntentReport",
  "@baseType": "Entity",
  "intent": {
    "id": "INT-HOSP-2026-001",
    "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
  },
  "lifecycleStatus": "Active",
  "effectiveVersion": "1.0",
  "reportTime": "2026-05-04T12:10:30+10:00",
  "summary": "Intent is active and currently meeting projected lifecycle status.",
  "assuranceSummary": {
    "status": "Healthy",
    "lastAssuranceEventTime": "2026-05-04T12:10:10+10:00",
    "observedMetrics": {
      "latencyMs": 7,
      "availabilityPercent": 99.995,
      "jitterMs": 3,
      "packetLossPercent": 0.005
    }
  },
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/report"
    },
    "intent": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    }
  }
}
```

### Behaviour:

| **Concern** | **Baseline** |
|---|---|
| Owner | IC MS |
| Success response | `200 OK` |
| Response body | Externally visible IntentReport projection |
| ETag | Mandatory |
| Cache-Control | Short private cache by default |
| Assurance truth | IA MS; IC MS exposes projection/report only |

## Create Intent Hub Subscription:

### Request:

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

### Successful Response:

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

### Supported Event Types:

| **Event Type** | **Purpose** |
|---|---|
| `IntentCreateEvent` | Runtime Intent created |
| `IntentAttributeValueChangeEvent` | Runtime Intent attribute changed |
| `IntentStatusChangeEvent` | Runtime Intent lifecycle/status changed |
| `IntentDeleteEvent` | Runtime Intent deleted/terminated where applicable |

## Retrieve Intent Hub Subscription:

### Request:

```http
GET /intentManagement/v5/intent/hub/sub-icms-001 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
Accept-Language: en-AU
correlationid: corr-icms-hub-002
```

### Successful Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intent/hub/sub-icms-001
ETag: "icms-intent-hub-sub-001-rev-001"
Last-Modified: Mon, 04 May 2026 12:05:00 GMT
correlationid: corr-icms-hub-002
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

## Delete Intent Hub Subscription:

### Request:

```http
DELETE /intentManagement/v5/intent/hub/sub-icms-001 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
If-Match: "icms-intent-hub-sub-001-rev-001"
correlationid: corr-icms-hub-003
```

### Successful Response:

```http
HTTP/1.1 204 No Content
Content-Language: en-AU
correlationid: corr-icms-hub-003
```

## Internal Event: IntentValidatedEvent:

IC MS emits `IntentValidatedEvent` after it successfully creates and syntactically validates a runtime `Intent`.

### Kafka Message:

```text
topic: t7.intent.management.events
key: INT-HOSP-2026-001

headers:
  ce-specversion: 1.0
  ce-type: au.com.mycsp.intent.validated.v1
  ce-source: intent-controller-ms
  ce-id: evt-icms-validated-001
  ce-time: 2026-05-04T12:00:01+10:00
  ce-subject: intent/INT-HOSP-2026-001
  correlationid: corr-icms-20260504-001
  content-type: application/json
```

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
        "priority": "critical"
      }
    },
    "references": {
      "intent": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

## External Event: IntentCreateEvent:

IC MS emits `IntentCreateEvent` to subscribed consumers where subscription policy requires it.

### Listener Delivery Request:

```http
POST /listener/intentCreateEvent HTTP/1.1
Host: consumer.example.com
Content-Type: application/json
Accept: application/json
correlationid: corr-icms-20260504-001
```

```json
{
  "eventId": "evt-external-intent-create-001",
  "eventTime": "2026-05-04T12:00:02+10:00",
  "eventType": "IntentCreateEvent",
  "correlationId": "corr-icms-20260504-001",
  "title": "Intent created",
  "description": "Runtime Intent INT-HOSP-2026-001 was created.",
  "priority": "normal",
  "timeOccurred": "2026-05-04T12:00:00+10:00",
  "reportingSystem": {
    "id": "intent-controller-ms",
    "name": "intent-controller-ms"
  },
  "source": {
    "id": "intent-controller-ms",
    "name": "intent-controller-ms"
  },
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "@type": "Intent",
      "@baseType": "Entity",
      "name": "Hospital surgical slice intent",
      "lifecycleStatus": "InProgress",
      "version": "1.0",
      "effectiveVersion": null
    }
  }
}
```

### Listener Success Response:

```http
HTTP/1.1 204 No Content
```

## Standard Error Responses:

### Invalid Request Shape:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
Content-Language: en-AU
correlationid: corr-icms-error-001
```

```json
{
  "code": "INVALID_REQUEST",
  "reason": "Bad Request",
  "message": "The request body is malformed or does not match the active IntentSpecification syntax.",
  "status": 400,
  "@type": "Error"
}
```

### Unknown Or Inactive IntentSpecification:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
Content-Language: en-AU
correlationid: corr-icms-error-002
```

```json
{
  "code": "INTENT_SPECIFICATION_NOT_ACTIVE",
  "reason": "Unprocessable Entity",
  "message": "The referenced IntentSpecification is unknown or not ACTIVE.",
  "status": 422,
  "@type": "Error"
}
```

### Missing If-Match:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
Content-Language: en-AU
correlationid: corr-icms-error-003
```

```json
{
  "code": "PRECONDITION_REQUIRED",
  "reason": "Precondition Required",
  "message": "If-Match header is required for this operation.",
  "status": 428,
  "@type": "Error"
}
```

### Stale If-Match:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
correlationid: corr-icms-error-004
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "Precondition Failed",
  "message": "The supplied ETag does not match the current resource version.",
  "status": 412,
  "@type": "Error"
}
```

## Lifecycle Baseline:

| **State** | **Meaning** |
|---|---|
| `InProgress` | Intent accepted and workflow is progressing |
| `Active` | Intent is active/effective in the network/service |
| `Degraded` | Intent is still effective but assurance indicates degraded conditions |
| `Failed` | Intent failed after being attempted or active |
| `Terminated` | Intent has been terminated |
| `Rejected` | Intent cannot be processed/resolved/accepted under validation or policy rules |

## Effective Version Rule:

Once an Intent version becomes `Active`, it becomes the `effectiveVersion`.

It remains the `effectiveVersion` even if its lifecycle later moves to `Degraded`, `Paused`, or `Failed`.

`effectiveVersion` changes only when another version is confirmed `Active` in the network/service.
