# ic_ms_specification.md

## IC MS Specification:

### Service identity:

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Controller MS |
| Short name | IC MS |
| Service name | `intent-controller-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `Intent` |
| Secondary resource | `IntentReport` |
| Primary responsibility | TMF-facing runtime `Intent` controller, syntactic admission, lifecycle/status projection, and external runtime intent events |

### Boundary statement:

IC MS owns the external runtime `Intent` and `IntentReport` resources.

IC MS validates runtime `Intent` request shape against a concrete active `IntentSpecification.id`, admits syntactically valid runtime intents, emits `IntentValidatedEvent` as an internal state/progress event, projects external lifecycle/status based on downstream outcomes, and exposes curated `IntentReport` projections.

IC MS does not own:

- design-time `IntentSpecification` catalogue
- semantic validation
- policy validation
- optimisation
- network apply
- runtime assurance truth
- real-time telemetry
- callback ingestion
- raw orchestrator callback interpretation

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
| List reports for intent | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport` | Platform/TMF-style nested report projection |
| Retrieve report by ID | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport/{id}` | Platform/TMF-style nested report projection |

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

---

## 2. Common conventions:

### Concrete IntentSpecification reference rule:

Runtime `Intent` create/update requests must reference a concrete `IntentSpecification.id`.

Supported:

```json
{
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  }
}
```

Not supported:

```json
{
  "intentSpecification": {
    "familyId": "hospital-surgical-slice-spec"
  }
}
```

Not supported:

```json
{
  "intentSpecification": {
    "name": "Hospital Surgical Slice Intent Specification"
  }
}
```

IC MS does not resolve `IntentSpecification` by family, key, name, or inferred payload shape.

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

### External projection rule:

`GET /intent/{id}` returns the current projected `Intent` state for that Intent ID.

It does not return the full internal version aggregate by default.

The returned `version` is the projected runtime version.

Historical version state such as `Standby`, `Retired`, rollback candidates, and previous versions remains internal unless exposed through `IntentReport` or a documented platform extension.

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
| `412` | `PRECONDITION_FAILED` | Missing/mismatched `If-Match` on unsafe operation |
| `422` | `VALIDATION_FAILED` | Runtime Intent fails request-shape/spec validation |
| `422` | `INTENT_SPECIFICATION_NOT_ACTIVE` | Referenced IntentSpecification is not active |
| `503` | `SERVICE_UNAVAILABLE` | IC MS DB unavailable or active spec cannot be confirmed |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

---

## 4. Create Intent:

### Request:

```http
POST /intentManagement/v5/intent
Content-Type: application/json
Accept: application/json
```

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "locationType": "hospital",
      "geographicScope": "campus"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 10,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      }
    },
    "preferences": {
      "preferredAccessTechnology": "5G"
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
  "version": "v1",
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Intent request accepted for semantic validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "locationType": "hospital",
      "geographicScope": "campus"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 10,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      }
    },
    "preferences": {
      "preferredAccessTechnology": "5G"
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

### Create validation rule:

IC MS emits `IntentValidatedEvent` after syntactic validation succeeds and the external Intent projection is persisted.

`IntentValidatedEvent` is a state/progress event, not a point-to-point command for a specific consumer.

---

## 5. List Intents:

### Request:

```http
GET /intentManagement/v5/intent?offset=0&limit=10&lifecycleStatus=Active
Accept: application/json
```

### Request with fresh-read override:

```http
GET /intentManagement/v5/intent?offset=0&limit=10&lifecycleStatus=Active
Accept: application/json
Cache-Control: no-cache
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
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
      "id": "hospital-surgical-slice-spec-v1.20"
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
| `lifecycleStatus` | Filter by projected external lifecycle status |
| `version` | Filter by projected runtime version |
| `intentSpecification.id` | Filter by concrete IntentSpecification ID |

---

## 6. Retrieve Intent:

### Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001
Accept: application/json
```

### Request with fresh-read override:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001
Accept: application/json
Cache-Control: no-cache
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
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
    "id": "hospital-surgical-slice-spec-v1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "locationType": "hospital",
      "geographicScope": "campus"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 8,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      }
    },
    "preferences": {
      "preferredAccessTechnology": "5G"
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
PUT /intentManagement/v5/intent/INT-HOSP-2026-001
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
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "locationType": "hospital",
      "geographicScope": "campus"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 8,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      }
    },
    "preferences": {
      "preferredAccessTechnology": "5G"
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
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v4"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Updated surgical connection request with lower latency target.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "version": "v4",
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Updated intent version accepted for semantic validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "locationType": "hospital",
      "geographicScope": "campus"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 8,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      }
    },
    "preferences": {
      "preferredAccessTechnology": "5G"
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

If meaningful runtime content changes, IC MS creates a new runtime Intent version.

---

## 8. Partial update Intent:

### Request:

```http
PATCH /intentManagement/v5/intent/INT-HOSP-2026-001
Content-Type: application/json
Accept: application/json
If-Match: "intent-INT-HOSP-2026-001-v4"
```

```json
{
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "locationType": "hospital",
      "geographicScope": "campus"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 7
    },
    "constraints": {
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
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
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
  "version": "v5",
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Patched intent version accepted for semantic validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "locationType": "hospital",
      "geographicScope": "campus"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 7,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      }
    },
    "preferences": {
      "preferredAccessTechnology": "5G"
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

If the patch changes meaningful runtime content, IC MS creates a new runtime Intent version.

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
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001
ETag: "intent-INT-HOSP-2026-001-v6"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "version": "v4",
  "lifecycleStatus": "Terminated",
  "statusReason": "Intent termination requested and accepted.",
  "statusChangeDate": "2026-04-18T13:00:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Rule:

`DELETE /intent/{id}` is treated as termination, not physical deletion.

The retained Intent record remains available for audit, reporting, lifecycle history, and traceability.

---

## 10. List IntentReports:

### Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport
Accept: application/json
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
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
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "version": "v2",
    "lifecycleStatus": "Active",
    "reportTime": "2026-04-18T12:20:00+10:00",
    "summary": "Intent is active and assurance is healthy.",
    "@type": "IntentReport",
    "@baseType": "Entity"
  }
]
```

---

## 11. Retrieve IntentReport:

### Request:

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003
Accept: application/json
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003
ETag: "intent-report-IR-INT-HOSP-2026-001-003-v1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "IR-INT-HOSP-2026-001-003",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
  "intent": {
    "id": "INT-HOSP-2026-001",
    "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
  },
  "version": "v2",
  "lifecycleStatus": "Active",
  "reportTime": "2026-04-18T12:20:00+10:00",
  "summary": "Intent is active and assurance is healthy.",
  "assuranceSummary": {
    "overallStatus": "Healthy",
    "latencyMs": 8,
    "availabilityPercent": 99.995,
    "jitterMs": 1.5,
    "packetLossPercent": 0.005
  },
  "serviceSummary": {
    "serviceClass": "critical-gold",
    "locationId": "sydney-hospital"
  },
  "evaluationSummary": {
    "result": "Compliant",
    "details": [
      "Latency target satisfied",
      "Availability target satisfied",
      "Jitter target satisfied",
      "Packet loss target satisfied"
    ]
  },
  "@type": "IntentReport",
  "@baseType": "Entity"
}
```

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
  "callback": "https://consumer.example.com/tmf/intent/events",
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
  "callback": "https://consumer.example.com/tmf/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription"
}
```

### Success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intent/hub/sub-intent-001
Content-Type: application/json
ETag: "subscription-sub-intent-001-v1"
```

```json
{
  "id": "sub-intent-001",
  "callback": "https://consumer.example.com/tmf/intent/events",
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

---

## 13. Hub retrieve subscription:

### Request:

```http
GET /intentManagement/v5/intent/hub/sub-intent-001
Accept: application/json
```

### Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "subscription-sub-intent-001-v1"
```

```json
{
  "id": "sub-intent-001",
  "callback": "https://consumer.example.com/tmf/intent/events",
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
HTTP/1.1 204 No Content
```

---

## 15. Validation and dependency error examples:

### Missing concrete IntentSpecification ID:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "CONCRETE_INTENT_SPECIFICATION_ID_REQUIRED",
  "message": "Runtime Intent create/update requests must include a concrete intentSpecification.id.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### Referenced specification not active:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "INTENT_SPECIFICATION_NOT_ACTIVE",
  "message": "Referenced IntentSpecification hospital-surgical-slice-spec-v1.20 is not ACTIVE.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### IntentSpecification lookup unavailable:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Retry-After: 30
```

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "reason": "INTENT_SPECIFICATION_LOOKUP_UNAVAILABLE",
  "message": "Intent creation or update cannot be accepted because the referenced active IntentSpecification could not be confirmed.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/SERVICE_UNAVAILABLE",
  "@type": "Error"
}
```

### ETag mismatch:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
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

## 16. External Intent event family:

IC MS emits external TMF-style resource events for `Intent` projection changes.

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
        "id": "hospital-surgical-slice-spec-v1.20"
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
    },
    "previousLifecycleStatus": "InProgress",
    "newLifecycleStatus": "Active"
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

---

## 20. IntentDeleteEvent:

`IntentDeleteEvent` represents accepted termination, not physical deletion.

```json
{
  "eventId": "evt-intent-delete-001",
  "eventTime": "2026-04-18T13:00:00+10:00",
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

IC MS emits external TMF-style resource events for `IntentReport` projection changes.

| **Event** | **Trigger** |
|---|---|
| `IntentReportCreateEvent` | New `IntentReport` projection created |
| `IntentReportAttributeValueChangeEvent` | Existing `IntentReport` projection updated |
| `IntentReportDeleteEvent` | `IntentReport` projection removed where retention policy allows |

---

## 22. IntentReportCreateEvent:

```json
{
  "eventId": "evt-intent-report-create-001",
  "eventTime": "2026-04-18T12:20:00+10:00",
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

```json
{
  "eventId": "evt-intent-report-delete-001",
  "eventTime": "2026-04-18T13:30:00+10:00",
  "eventType": "IntentReportDeleteEvent",
  "correlationId": "corr-intent-report-delete-001",
  "description": "IntentReport projection removed.",
  "priority": "Normal",
  "title": "IntentReport deleted",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-003",
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
      "intent": {
        "id": "INT-HOSP-2026-001"
      },
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
  "@type": "IntentReportDeleteEvent"
}
```

---

## 25. Internal event publication note:

IC MS publishes `IntentValidatedEvent` internally after syntactic validation and admission.

This is not a point-to-point command for a single consumer.

It is a platform state/progress event meaning the runtime Intent has passed IC MS syntactic validation and has been admitted into the intent lifecycle.

Current primary consumer is II MS / `intent-intelligence-ms`, but the event may be consumed by other authorised internal consumers where useful.

---



## HATEOAS link compliance baseline:

### Rule:

All successful IC MS resource representations must include a `_links` object so clients can discover the next valid actions from the returned representation.

This applies to:

- `Intent` create/retrieve/list-item/update/patch/terminate responses
- `IntentReport` retrieve/list-item responses
- `EventSubscription` create/retrieve responses for `/hub` and `/intent/hub`

`204 No Content` responses do not include a response body and therefore do not include `_links`.

### Common link relation rules:

| **Link relation** | **Meaning** | **When included** |
|---|---|---|
| `self` | Canonical URL of the returned resource | Always for resource representations |
| `list` | Collection/list endpoint for the resource type | Optional but recommended on single-resource representations |
| `intentReport` | Nested reports for an Intent | Included on `Intent` representations |
| `fullUpdate` | Deterministic full replacement through `PUT` | Included when the Intent can accept a runtime update |
| `partialUpdate` | TMF-compatible partial update through `PATCH` | Included when the Intent can accept a runtime update; include warning that `PATCH` is supported but discouraged for ordinary edits |
| `terminate` | Termination through `DELETE /intent/{id}` | Included when the Intent is not already terminal |
| `delete` | Delete/tombstone report operation | Included on `IntentReport` when report deletion/tombstoning is allowed |
| `subscribe` | Hub subscription creation endpoint | Recommended on collection/root examples where useful |
| `unsubscribe` | Hub subscription delete endpoint | Included on subscription representations |

### Intent lifecycle-specific links:

| **Intent lifecycle status** | **HATEOAS links** |
|---|---|
| `Acknowledged` | `self`, `list`, `intentReport`, `fullUpdate`, `partialUpdate`, `terminate` |
| `InProgress` | `self`, `list`, `intentReport`, `terminate`; update links only if platform policy allows concurrent version update |
| `Active` | `self`, `list`, `intentReport`, `fullUpdate`, `partialUpdate`, `terminate` |
| `Degraded` | `self`, `list`, `intentReport`, `fullUpdate`, `partialUpdate`, `terminate` |
| `Paused` | `self`, `list`, `intentReport`, `terminate`; resume is not exposed as a separate action by default |
| `Rejected` | `self`, `list`, `intentReport`; `terminate` only if retained rejected intents can be explicitly closed |
| `Failed` | `self`, `list`, `intentReport`, `terminate` |
| `Terminated` | `self`, `list`, `intentReport`; no update or terminate links |

### Active Intent example:

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "version": "v2",
  "lifecycleStatus": "Active",
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "list": {
      "href": "/intentManagement/v5/intent"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    },
    "fullUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is supported for TMF compatibility but PUT is preferred for deterministic full updates."
    },
    "terminate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "DELETE"
    }
  }
}
```

### Terminated Intent example:

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "version": "v2",
  "lifecycleStatus": "Terminated",
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "list": {
      "href": "/intentManagement/v5/intent"
    },
    "intentReport": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    }
  }
}
```

### IntentReport example:

```json
{
  "id": "IR-INT-HOSP-2026-001-003",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
  "name": "Sydney Hospital Surgical Connection Intent Report",
  "@type": "IntentReport",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003"
    },
    "list": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport"
    },
    "intent": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "delete": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-003",
      "method": "DELETE"
    }
  }
}
```

### EventSubscription example:

```json
{
  "id": "sub-intent-001",
  "callback": "https://consumer.example.com/tmf/intent/events",
  "query": "eventType=IntentStatusChangeEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/hub/sub-intent-001"
    },
    "unsubscribe": {
      "href": "/intentManagement/v5/intent/hub/sub-intent-001",
      "method": "DELETE"
    },
    "subscribe": {
      "href": "/intentManagement/v5/intent/hub",
      "method": "POST"
    }
  }
}
```

### IC MS HATEOAS baseline statement:

IC MS responses must expose only links for operations that are valid for the current resource state. HATEOAS links must not advertise update or terminate actions for terminal `Intent` projections. `PUT` may be exposed as the preferred deterministic full-update platform extension where supported, while `PATCH` remains available for TMF compatibility but discouraged for ordinary edits.


## 26. Final specification notes:

- `GET /intent/{id}` returns current projected Intent state, not a full internal version aggregate.
- `GET /intent` lists current projected Intent states for retained Intent IDs.
- Runtime create/update requires concrete `intentSpecification.id`.
- IC MS does not resolve `IntentSpecification` by family, key, name, or inferred payload shape.
- `DELETE /intent/{id}` is termination, not physical deletion.
- `PUT /intent/{id}` is a platform extension for deterministic full replacement.
- `PATCH /intent/{id}` is supported for TMF compatibility but not encouraged for ordinary edits.
- ETag is used for unsafe-operation concurrency through `If-Match`.
- GET responses may use bounded private caching.
- Clients may request a fresh GET using `Cache-Control: no-cache`.
- `IntentDeleteEvent` represents termination acceptance, not physical deletion.
- External `Intent*Event` and `IntentReport*Event` payloads are curated projection events and must not expose raw telemetry, raw callback payloads, raw optimiser details, raw knowledge-plane data, or internal candidate scoring.

## Shared semantic bucket baseline

### Runtime Intent expression

IC MS accepts and projects runtime Intent resources using the shared semantic buckets `targets`, `constraints`, and `preferences`.

### Complete POST /intent request body example

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "locationType": "hospital",
      "geographicScope": "campus"
    },
    "serviceType": "surgical-connectivity",
    "serviceClass": "critical-gold",
    "targets": {
      "maxLatencyMs": 10,
      "minAvailabilityPercent": 99.99,
      "maxJitterMs": 2,
      "maxPacketLossPercent": 0.01
    },
    "constraints": {
      "priority": "critical",
      "redundancyRequired": true,
      "timeWindow": {
        "startDateTime": "2026-04-18T12:00:00+10:00"
      }
    },
    "preferences": {
      "preferredAccessTechnology": "5G"
    }
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Complete IntentValidatedEvent body example

```json
{
  "body": {
    "intentId": "INT-HOSP-2026-001",
    "version": "v1",
    "lifecycleStatus": "Acknowledged",
    "statusReason": "Intent request passed IC MS admission validation and was admitted for downstream processing.",
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.20"
    },
    "expression": {
      "location": {
        "locationId": "AU-NSW-SYD-HOSP-001",
        "locationType": "hospital",
        "geographicScope": "campus"
      },
      "serviceType": "surgical-connectivity",
      "serviceClass": "critical-gold",
      "targets": {
        "maxLatencyMs": 10,
        "minAvailabilityPercent": 99.99,
        "maxJitterMs": 2,
        "maxPacketLossPercent": 0.01
      },
      "constraints": {
        "priority": "critical",
        "redundancyRequired": true,
        "timeWindow": {
          "startDateTime": "2026-04-18T12:00:00+10:00"
        }
      },
      "preferences": {
        "preferredAccessTechnology": "5G"
      }
    },
    "references": {
      "correlationId": "corr-intent-create-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.20",
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
      }
    }
  }
}
```

### Baseline rules

- `/intent.expression` uses `targets`, `constraints`, and `preferences`.
- `IntentValidatedEvent.expression` carries the same semantic buckets.
- IC MS validates syntactic shape against the active ID MS `expressionSpecification`.
- IC MS does not perform semantic/KP validation, optimisation, orchestration, or assurance.



## Expression schema consumption and drift-prevention baseline:

IC MS does not discover or choose validation schemas independently.

For `POST /intent`, `PUT /intent/{id}`, and runtime-content-changing `PATCH /intent/{id}`, IC MS resolves the concrete `intentSpecification.id`, confirms the referenced specification is `ACTIVE`, and validates `Intent.expression.expressionValue` only against the expression-value schema referenced by that exact specification version.

Rules:

- IC MS must not validate runtime intents against a schema URL inferred from family, name, service type, or latest version.
- IC MS must not use a newer schema just because one exists.
- The schema reference is part of the active `IntentSpecification` contract.
- If the referenced schema is unavailable and IC MS has no valid fresh cached copy tied to the same `IntentSpecification.id` and schema hash, IC MS fails closed for create/update admission.
- Runtime `Intent.expression.expressionValue` carries only request data; it does not embed the validation schema.

This prevents design-time/runtime drift while keeping the external TMF-facing `Intent.expression` clean.
