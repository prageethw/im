# IC MS Baselined Contents

This document consolidates the currently baselined **IC MS** contents from the running context dump, including the agreed JSON payloads and event payloads.

## Scope
This pack includes:
- IC MS external `/intent` interfaces
- IC MS `/intent/hub` interfaces
- IC MS nested `IntentReport` interfaces
- IC MS external `Intent...Event` family
- IC MS external `IntentReport...Event` family
- related internal event baselines and refinements agreed during the IC MS exercise

## Notes
- This is a **baseline pack**, not a prose-only summary.
- JSON payloads are included in full where they were baselined.
- Historical/replaced terminology is not treated as active canonical content.


## IC MS baselines

### Responsibility
IC MS owns the external Intent domain and related external IntentReport projection.

### `/intent` interfaces baselined
- `POST /intentManagement/v5/intent`
- `GET /intentManagement/v5/intent`
- `GET /intentManagement/v5/intent/{id}`
- `PUT /intentManagement/v5/intent/{id}` — platform extension
- `PATCH /intentManagement/v5/intent/{id}` — supported but strongly discouraged
- `DELETE /intentManagement/v5/intent/{id}`

### `/intent/hub` baselined
- `POST /intentManagement/v5/intent/hub`
- `DELETE /intentManagement/v5/intent/hub/{id}`

Literal subscription style:
- one subscription per event type
- one callback URL per subscription

This same hub is used for both:
- `Intent...Event`
- `IntentReport...Event`

### `IntentReport` interfaces baselined
- `GET /intentManagement/v5/intent/{intentId}/intentReport`
- `GET /intentManagement/v5/intent/{intentId}/intentReport/{id}`

IntentReport is:
- IC-MS-owned
- external
- curated reporting/projection
- not raw runtime telemetry

### External `Intent` event family baselined
- `IntentCreateEvent`
- `IntentAttributeValueChangeEvent`
- `IntentStatusChangeEvent`
- `IntentDeleteEvent`

All are:
- TMF-aligned
- delivered via `/intent/hub`
- design-time only
- use `intent-controller-ms` in `reportingSystem.name` and `source.name`

### External `IntentReport` event family baselined
- `IntentReportCreateEvent`
- `IntentReportAttributeValueChangeEvent`
- `IntentReportDeleteEvent`

All are:
- TMF-aligned
- delivered via `/intent/hub`
- curated external projection/design-time reporting events
- use `intent-controller-ms` in `reportingSystem.name` and `source.name`

### Reusable-vs-specific checklist baselined
Reuse:
- transport/API conventions
- error model
- `ETag` / `If-Match`
- list behavior
- subscription scaffolding
- HATEOAS link conventions
- TMF-style external event envelope
- common internal event envelope
- reusable internal resource-entry shape

Keep explicit:
- `Intent`
- `IntentReport`
- `Intent...Event`
- `IntentReport...Event`
- `/intent`, `/intent/hub`, nested IntentReport routes
- external `/intentSpecification` validation semantics
- design-time interpretation rule for external IC MS events

---

## IC MS IntentReport terminology refinement

### Baseline terminology direction
For external `IntentReport`, prefer existing cross-platform names to minimise custom code and mapping:
- use `metrics`
- use `targets`
- use `evaluations`

Avoid introducing extra report-only terms such as:
- `observedOutcome`
- `expectations`

### Consistency rationale
This keeps `IntentReport` aligned with the existing internal naming direction:
- `evaluations` already exists in internal assurance and optimisation-related baselines
- `metrics` already exists in the reusable resource-entry shape
- target values can be represented cleanly as `targets`

### Preferred report pattern
```json
{
  "status": "Degraded",
  "statusReason": "Observed service quality no longer satisfies the expected operating target.",
  "evaluations": [
    {
      "name": "latencyCompliance",
      "result": "failed"
    },
    {
      "name": "availabilityCompliance",
      "result": "passed"
    }
  ],
  "metrics": [
    {
      "name": "latencyMs",
      "value": 12
    },
    {
      "name": "reliabilityPercent",
      "value": 99.992
    }
  ],
  "targets": [
    {
      "name": "latencyMs",
      "operator": "<=",
      "value": 10
    },
    {
      "name": "reliabilityPercent",
      "operator": ">=",
      "value": 99.99
    }
  ]
}
```

## IC MS interface baseline — GET /intentManagement/v5/intent/{intentId}/intentReport/{id}

### Summary
Retrieves a single `IntentReport` resource for a given `Intent` from IC MS by report id. This is the baselined retrieve-one operation for the external curated `IntentReport` projection. It returns `200 OK`, includes `Content-Location` and mandatory `ETag`, uses private caching by default, and returns a richer curated `IntentReport` representation.

### Terminology note
`targets` is now baselined for the external `IntentReport` shape as the preferred report term for intended values, to stay consistent and avoid report-only wording such as `expectations`.

### Spec alignment note
From TMF921, this route:
- retrieves a single `IntentReport`
- is nested under the parent `intentId`
- supports `fields` selection for first-level attributes
- returns the TMF-defined `200IntentReport_Get` response shape

### IntentReport notes
- `IntentReport` is IC-MS-owned
- it is external
- it is a curated reporting/projection resource
- it is not raw runtime telemetry
- for terminology consistency, prefer:
  - `metrics`
  - `targets`
  - `evaluations`

### Request headers
```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001 HTTP/1.1
Host: mycsp.com.au
Accept: application/json
Accept-Language: en-AU
```

### Success response headers
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001
ETag: W/"IR-INT-HOSP-2026-001-001-r1"
Cache-Control: private, max-age=300
```

### Success response body
```json
{
  "id": "IR-INT-HOSP-2026-001-001",
  "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
  "name": "Sydney Hospital Surgical Connection Intent Report",
  "description": "Curated external report for the Sydney Hospital surgical connection intent.",
  "reportType": "IntentStatusReport",
  "category": "service-assurance",
  "creationDate": "2026-04-18T12:15:00+10:00",
  "lastUpdate": "2026-04-18T12:15:00+10:00",
  "validFor": {
    "startDateTime": "2026-04-18T12:15:00+10:00"
  },
  "status": "Degraded",
  "statusChangeDate": "2026-04-18T12:10:00+10:00",
  "statusReason": "Observed service quality no longer satisfies the expected operating target.",
  "summary": "The intent remains in service, but current observed performance is below the expected target.",
  "intent": {
    "id": "INT-HOSP-2026-001",
    "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
    "@type": "IntentRef",
    "@referredType": "Intent"
  },
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.19",
    "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
    "@type": "IntentSpecificationRef",
    "@referredType": "IntentSpecification"
  },
  "priority": "CRITICAL",
  "expression": {
    "@type": "JsonLdExpression",
    "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
    "expressionValue": {
      "@context": {
        "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
      },
      "@type": "icm:Constraint",
      "icm:and": [
        {
          "@type": "icm:LessOrEqual",
          "icm:leftOperand": "latency",
          "icm:rightOperand": 10
        },
        {
          "@type": "icm:GreaterOrEqual",
          "icm:leftOperand": "availability",
          "icm:rightOperand": 99.99
        }
      ]
    }
  },
  "targets": [
    {
      "name": "latencyMs",
      "operator": "<=",
      "value": 10
    },
    {
      "name": "reliabilityPercent",
      "operator": ">=",
      "value": 99.99
    }
  ],
  "metrics": [
    {
      "name": "latencyMs",
      "value": 12
    },
    {
      "name": "reliabilityPercent",
      "value": 99.992
    }
  ],
  "evaluations": [
    {
      "name": "latencyCompliance",
      "result": "failed"
    },
    {
      "name": "availabilityCompliance",
      "result": "passed"
    }
  ],
  "recommendedAction": "Review service quality and re-optimise if degradation persists.",
  "@type": "IntentReport",
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
      "method": "GET"
    }
  }
}
```

### Not found response headers
```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

### Not found response body
```json
{
  "code": "RESOURCE_NOT_FOUND",
  "reason": "NOT_FOUND",
  "message": "No IntentReport exists for intent 'INT-HOSP-2026-001' and id 'IR-INT-HOSP-2026-001-001'.",
  "status": 404,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",
  "@type": "Error"
}
```

## IC MS external event baseline — IntentCreateEvent

### Summary
External TMF-aligned event emitted by IC MS when a new `Intent` resource is created. This is the baselined create event for the surgical hospital slice example. It carries `event.intent`, is delivered via `/intent/hub`, is treated as a design-time external event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### TMF alignment note
This event is treated as TMF-aligned with platform-owned concrete content:
- TMF-style external event envelope is preserved
- event payload carries `event.intent`
- concrete field content and example values are platform-owned

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentCreateEvent for creation of the Sydney Hospital surgical connection intent.",
  "eventId": "EVT-INT-HOSP-2026-001-CREATE-0001",
  "eventTime": "2026-04-17T10:00:01+10:00",
  "eventType": "IntentCreateEvent",
  "priority": "3",
  "title": "IntentCreateEvent",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "lifecycleStatus": "Acknowledged",
      "priority": "CRITICAL",
      "isBundle": false,
      "@type": "Intent",
      "@baseType": "Entity",
      "validFor": {
        "startDateTime": "2026-04-17T10:00:00+10:00",
        "endDateTime": "2027-04-17T10:00:00+10:00"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "name": "Hospital-Surgical-Slice-Spec",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification",
        "@href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "humanExpression": "I need a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "characteristic": [
        {
          "@type": "Characteristic",
          "name": "slice_type",
          "value": "URLLC"
        },
        {
          "@type": "Characteristic",
          "name": "latency",
          "value": 10
        },
        {
          "@type": "Characteristic",
          "name": "availability",
          "value": 99.99
        },
        {
          "@type": "Characteristic",
          "name": "priority",
          "value": "CRITICAL"
        },
        {
          "@type": "Characteristic",
          "name": "semantic_tag",
          "value": "medical_urllc_critical"
        },
        {
          "@type": "Characteristic",
          "name": "geo_location",
          "value": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "HOSPITAL",
            "geographicScope": "AU-NSW-SYD"
          }
        }
      ]
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentCreateEvent"
}
```

## IC MS external event baseline — IntentAttributeValueChangeEvent

### Summary
External TMF-aligned event emitted by IC MS when an existing `Intent` resource has attribute values updated. This is the baselined attribute-value-change event for the surgical hospital slice example. It carries `event.intent`, is delivered via `/intent/hub`, is treated as a design-time external event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### TMF alignment note
This event is treated as TMF-aligned with platform-owned concrete content:
- TMF-style external event envelope is preserved
- event payload carries `event.intent`
- concrete field content and example values are platform-owned

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentAttributeValueChangeEvent for update of the Sydney Hospital surgical connection intent.",
  "eventId": "EVT-INT-HOSP-2026-001-ATTR-0001",
  "eventTime": "2026-04-17T10:05:00+10:00",
  "eventType": "IntentAttributeValueChangeEvent",
  "priority": "3",
  "title": "IntentAttributeValueChangeEvent",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "lifecycleStatus": "Acknowledged",
      "priority": "CRITICAL",
      "isBundle": false,
      "@type": "Intent",
      "@baseType": "Entity",
      "validFor": {
        "startDateTime": "2026-04-17T10:00:00+10:00",
        "endDateTime": "2027-04-17T10:00:00+10:00"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "name": "Hospital-Surgical-Slice-Spec",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification",
        "@href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "humanExpression": "I need a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "characteristic": [
        {
          "@type": "Characteristic",
          "name": "slice_type",
          "value": "URLLC"
        },
        {
          "@type": "Characteristic",
          "name": "latency",
          "value": 10
        },
        {
          "@type": "Characteristic",
          "name": "availability",
          "value": 99.99
        },
        {
          "@type": "Characteristic",
          "name": "priority",
          "value": "CRITICAL"
        },
        {
          "@type": "Characteristic",
          "name": "semantic_tag",
          "value": "medical_urllc_critical"
        },
        {
          "@type": "Characteristic",
          "name": "geo_location",
          "value": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "HOSPITAL",
            "geographicScope": "AU-NSW-SYD"
          }
        }
      ]
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentAttributeValueChangeEvent"
}
```

## IC MS external event baseline — IntentStatusChangeEvent

### Summary
External TMF-aligned event emitted by IC MS when the lifecycle status of an existing `Intent` changes. This is the baselined status-change event for the surgical hospital slice example. It carries `event.intent`, is delivered via `/intent/hub`, is treated as a design-time external event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### TMF alignment note
This event is treated as TMF-aligned with platform-owned concrete content:
- TMF-style external event envelope is preserved
- event payload carries `event.intent`
- concrete field content and example values are platform-owned

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentStatusChangeEvent for lifecycle transition of the Sydney Hospital surgical connection intent.",
  "eventId": "EVT-INT-HOSP-2026-001-STATUS-0001",
  "eventTime": "2026-04-18T12:10:05+10:00",
  "eventType": "IntentStatusChangeEvent",
  "priority": "3",
  "title": "IntentStatusChangeEvent",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "lifecycleStatus": "Degraded",
      "priority": "CRITICAL",
      "isBundle": false,
      "@type": "Intent",
      "@baseType": "Entity",
      "validFor": {
        "startDateTime": "2026-04-17T10:00:00+10:00",
        "endDateTime": "2027-04-17T10:00:00+10:00"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "name": "Hospital-Surgical-Slice-Spec",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification",
        "@href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "humanExpression": "I need a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "characteristic": [
        {
          "@type": "Characteristic",
          "name": "slice_type",
          "value": "URLLC"
        },
        {
          "@type": "Characteristic",
          "name": "latency",
          "value": 10
        },
        {
          "@type": "Characteristic",
          "name": "availability",
          "value": 99.99
        },
        {
          "@type": "Characteristic",
          "name": "priority",
          "value": "CRITICAL"
        },
        {
          "@type": "Characteristic",
          "name": "semantic_tag",
          "value": "medical_urllc_critical"
        },
        {
          "@type": "Characteristic",
          "name": "geo_location",
          "value": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "HOSPITAL",
            "geographicScope": "AU-NSW-SYD"
          }
        }
      ]
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentStatusChangeEvent"
}
```

## IC MS external event baseline — IntentDeleteEvent

### Summary
External TMF-aligned event emitted by IC MS when an `Intent` resource is deleted. This is the baselined delete event for the surgical hospital slice example. It carries a lean `event.intent`, is delivered via `/intent/hub`, is treated as a design-time external event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### Baseline notes
- keep delete payload lean
- do not duplicate the richer status-projection shape from `IntentStatusChangeEvent`
- do not introduce a separate `Deleted` lifecycle state
- treat this as a lean tombstone-style event for deletion of the external `Intent` resource

### TMF alignment note
This event is treated as TMF-aligned with platform-owned concrete content:
- TMF-style external event envelope is preserved
- event payload carries `event.intent`
- concrete field content and example values are platform-owned

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentDeleteEvent for deletion of the Sydney Hospital surgical connection intent.",
  "eventId": "EVT-INT-HOSP-2026-001-DELETE-0001",
  "eventTime": "2026-04-19T09:00:00+10:00",
  "eventType": "IntentDeleteEvent",
  "priority": "3",
  "title": "IntentDeleteEvent",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "@type": "Intent",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentDeleteEvent"
}
```

## IC MS external event baseline — IntentReportCreateEvent

### Summary
External TMF-aligned event emitted by IC MS when a new `IntentReport` resource is created. This baselined create event for the surgical hospital slice example carries `event.intentReport`, is delivered via `/intent/hub`, is treated as a curated external reporting event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### Terminology check
No new terminology introduced here beyond already baselined terms:
- `IntentReport`
- `metrics`
- `targets`
- `evaluations`

### Baseline notes
- this is a curated external report event
- not raw runtime telemetry
- keep it aligned with the richer `IntentReport` retrieve-one shape
- use the same hub as `Intent...Event`

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentReportCreateEvent for creation of the Sydney Hospital surgical connection intent report.",
  "eventId": "EVT-IR-INT-HOSP-2026-001-001-CREATE-0001",
  "eventTime": "2026-04-18T12:15:05+10:00",
  "eventType": "IntentReportCreateEvent",
  "priority": "3",
  "title": "IntentReportCreateEvent",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
      "name": "Sydney Hospital Surgical Connection Intent Report",
      "description": "Curated external report for the Sydney Hospital surgical connection intent.",
      "reportType": "IntentStatusReport",
      "category": "service-assurance",
      "creationDate": "2026-04-18T12:15:00+10:00",
      "lastUpdate": "2026-04-18T12:15:00+10:00",
      "validFor": {
        "startDateTime": "2026-04-18T12:15:00+10:00"
      },
      "status": "Degraded",
      "statusChangeDate": "2026-04-18T12:10:00+10:00",
      "statusReason": "Observed service quality no longer satisfies the expected operating target.",
      "summary": "The intent remains in service, but current observed performance is below the expected target.",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
        "@type": "IntentRef",
        "@referredType": "Intent"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification"
      },
      "priority": "CRITICAL",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "targets": [
        {
          "name": "latencyMs",
          "operator": "<=",
          "value": 10
        },
        {
          "name": "reliabilityPercent",
          "operator": ">=",
          "value": 99.99
        }
      ],
      "metrics": [
        {
          "name": "latencyMs",
          "value": 12
        },
        {
          "name": "reliabilityPercent",
          "value": 99.992
        }
      ],
      "evaluations": [
        {
          "name": "latencyCompliance",
          "result": "failed"
        },
        {
          "name": "availabilityCompliance",
          "result": "passed"
        }
      ],
      "recommendedAction": "Review service quality and re-optimise if degradation persists.",
      "@type": "IntentReport"
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentReportCreateEvent"
}
```

## IC MS external event baseline — IntentReportAttributeValueChangeEvent

### Summary
External TMF-aligned event emitted by IC MS when an existing `IntentReport` resource has attribute values updated. This baselined attribute-value-change event for the surgical hospital slice example carries `event.intentReport`, is delivered via `/intent/hub`, is treated as a curated external reporting event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### Terminology check
No new terminology introduced here beyond already baselined terms:
- `IntentReport`
- `metrics`
- `targets`
- `evaluations`

### Baseline notes
- this is a curated external report event
- not raw runtime telemetry
- keep it aligned with the richer `IntentReport` retrieve-one shape
- use the same hub as `Intent...Event`
- suitable when report content changes without deleting the report resource

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentReportAttributeValueChangeEvent for update of the Sydney Hospital surgical connection intent report.",
  "eventId": "EVT-IR-INT-HOSP-2026-001-001-ATTR-0001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentReportAttributeValueChangeEvent",
  "priority": "3",
  "title": "IntentReportAttributeValueChangeEvent",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
      "name": "Sydney Hospital Surgical Connection Intent Report",
      "description": "Curated external report for the Sydney Hospital surgical connection intent.",
      "reportType": "IntentStatusReport",
      "category": "service-assurance",
      "creationDate": "2026-04-18T12:15:00+10:00",
      "lastUpdate": "2026-04-18T12:20:00+10:00",
      "validFor": {
        "startDateTime": "2026-04-18T12:15:00+10:00"
      },
      "status": "Degraded",
      "statusChangeDate": "2026-04-18T12:10:00+10:00",
      "statusReason": "Observed service quality no longer satisfies the expected operating target.",
      "summary": "The intent remains in service, but current observed performance is below the expected target.",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
        "@type": "IntentRef",
        "@referredType": "Intent"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification"
      },
      "priority": "CRITICAL",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "targets": [
        {
          "name": "latencyMs",
          "operator": "<=",
          "value": 10
        },
        {
          "name": "reliabilityPercent",
          "operator": ">=",
          "value": 99.99
        }
      ],
      "metrics": [
        {
          "name": "latencyMs",
          "value": 12
        },
        {
          "name": "reliabilityPercent",
          "value": 99.992
        }
      ],
      "evaluations": [
        {
          "name": "latencyCompliance",
          "result": "failed"
        },
        {
          "name": "availabilityCompliance",
          "result": "passed"
        }
      ],
      "recommendedAction": "Review service quality and re-optimise if degradation persists.",
      "@type": "IntentReport"
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentReportAttributeValueChangeEvent"
}
```

## Internal event baseline refinement — IntentAssuranceEvent shared consumer role

### Baseline interpretation
`IntentAssuranceEvent` is the shared internal assurance truth event consumed by both:
- II MS, to decide what happens next
- IC MS, to keep external state and reporting aligned with actual network state

### Design consequence
Keep `IntentAssuranceEvent`:
- generic
- clean
- state-focused
- not optimiser-specific
- not IC-specific
- not overloaded with duplicated derived views

### Preferred structure direction
Use:
- `lifecycleStatus`
- `statusChangeDate`
- `statusReason`
- `current`
- `candidates`
- `references`

This event is the platform assurance truth that both II MS and IC MS consume for different purposes.
