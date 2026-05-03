# IC MS Baseline Pack

_Regenerated from latest running dump: `new-context-working-v24.md`._

This document consolidates the currently baselined **IC MS** contents in Markdown, including the agreed JSON payloads.

## Scope

This pack includes:
- IC MS external `/intent` interfaces
- IC MS external `/intent/hub` interfaces
- IC MS nested `IntentReport` interfaces
- IC MS external `Intent...Event` family
- IC MS external `IntentReport...Event` family
- IC MS internal touchpoints relevant to the external intent lifecycle

## Baseline rules

- Canonical active terms:
  - `location.locationId`
  - `service.serviceClass`
  - `resources`
  - `metrics`
  - `targets`
  - `evaluations`
  - `priority`
- Do **not** use as active attribute names unless discussing legacy/historical terms:
  - `primaryPathId`
  - `secondaryPathId`
  - `paths`
  - `observedOutcome`
  - `expectations`
  - `priority_level`
- `serviceType` is removed from active payloads.
- `geo_location` is acceptable where it belongs in the external contract.
- `PATCH` is supported but strongly discouraged in favour of `PUT`.
- `ETag` and `If-Match` concurrency rules apply to mutation operations.
- External IC MS events are design-time / curated projection events, not raw runtime telemetry.

---

# 1. IC MS responsibility

IC MS owns:
- the external `Intent` domain
- the external curated `IntentReport` projection
- the external `Intent...Event` family
- the external `IntentReport...Event` family
- the `/intent/hub` subscription surface for both event families

---

# 2. `/intent` interfaces

## POST /intentManagement/v5/intent

### Summary
Creates an `Intent` resource after syntactic validation against an ACTIVE `IntentSpecification`.

### Request
```http
POST /intentManagement/v5/intent HTTP/1.1
Host: mycsp.com.au
Content-Type: application/json
Accept: application/json
Accept-Language: en-AU
```

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
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
```

### Response
```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Language: en-AU
Location: https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001
ETag: W/"INT-HOSP-2026-001-v1"
Cache-Control: private, max-age=300
```

```json
{
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
  ],
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "GET"
    },
    "fullUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is allowed but strongly discouraged. Use PUT for deterministic intent updates."
    },
    "delete": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "DELETE"
    }
  }
}
```

---

## GET /intentManagement/v5/intent/{id}

### Summary
Retrieves the canonical external `Intent` resource by id.

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001 HTTP/1.1
Host: mycsp.com.au
Accept: application/json
Accept-Language: en-AU
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001
ETag: W/"INT-HOSP-2026-001-v1"
Cache-Control: private, max-age=300
```

```json
{
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
  ],
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "GET"
    },
    "fullUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is allowed but strongly discouraged. Use PUT for deterministic intent updates."
    },
    "delete": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "DELETE"
    }
  }
}
```

Not found:
```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "reason": "NOT_FOUND",
  "message": "No Intent exists for id 'INT-HOSP-2026-001'.",
  "status": 404,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",
  "@type": "Error"
}
```

---

## GET /intentManagement/v5/intent

### Summary
Lists `Intent` resources using offset/limit pagination.

```http
GET /intentManagement/v5/intent?offset=0&limit=10 HTTP/1.1
Host: mycsp.com.au
Accept: application/json
Accept-Language: en-AU
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
ETag: W/"intent-list-r1"
X-Total-Count: 1
X-Result-Count: 1
Cache-Control: private, max-age=300
```

```json
[
  {
    "id": "INT-HOSP-2026-001",
    "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
    "name": "Sydney Hospital Surgical Connection Intent",
    "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
    "lifecycleStatus": "Acknowledged",
    "priority": "CRITICAL",
    "@type": "Intent",
    "intentSpecification": {
      "id": "hospital-surgical-slice-spec-v1.19",
      "name": "Hospital-Surgical-Slice-Spec",
      "@type": "IntentSpecificationRef",
      "@referredType": "IntentSpecification",
      "@href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "validFor": {
      "startDateTime": "2026-04-17T10:00:00+10:00",
      "endDateTime": "2027-04-17T10:00:00+10:00"
    },
    "_links": {
      "self": {
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
        "method": "GET"
      },
      "fullUpdate": {
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
        "method": "PUT"
      },
      "partialUpdate": {
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
        "method": "PATCH",
        "warning": "PATCH is allowed but strongly discouraged. Use PUT for deterministic intent updates."
      },
      "delete": {
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
        "method": "DELETE"
      }
    }
  }
]
```

---

## PUT /intentManagement/v5/intent/{id}

### Summary
Full update of an `Intent` resource. Platform extension.

```http
PUT /intentManagement/v5/intent/INT-HOSP-2026-001 HTTP/1.1
Host: mycsp.com.au
Content-Type: application/json
Accept: application/json
Accept-Language: en-AU
If-Match: W/"INT-HOSP-2026-001-v1"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
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
```

Success:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001
ETag: W/"INT-HOSP-2026-001-v2"
Cache-Control: private, max-age=300
```

```json
{
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
  ],
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "GET"
    },
    "fullUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is allowed but strongly discouraged. Use PUT for deterministic intent updates."
    },
    "delete": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "DELETE"
    }
  }
}
```

ETag mismatch:
```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied If-Match value does not match the current resource version for 'INT-HOSP-2026-001'.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

## PATCH /intentManagement/v5/intent/{id}

### Summary
Compatibility partial update. Supported but strongly discouraged.

```http
PATCH /intentManagement/v5/intent/INT-HOSP-2026-001 HTTP/1.1
Host: mycsp.com.au
Content-Type: application/json
Accept: application/json
Accept-Language: en-AU
If-Match: W/"INT-HOSP-2026-001-v1"
```

```json
{
  "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
  "priority": "CRITICAL"
}
```

Success:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001
ETag: W/"INT-HOSP-2026-001-v2"
Cache-Control: private, max-age=300
```

```json
{
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
  ],
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "GET"
    },
    "fullUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH",
      "warning": "PATCH is allowed but strongly discouraged. Use PUT for deterministic intent updates."
    },
    "delete": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "DELETE"
    }
  }
}
```

ETag mismatch:
```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied If-Match value does not match the current resource version for 'INT-HOSP-2026-001'.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

## DELETE /intentManagement/v5/intent/{id}

### Summary
Deletes an existing `Intent` resource.

```http
DELETE /intentManagement/v5/intent/INT-HOSP-2026-001 HTTP/1.1
Host: mycsp.com.au
Accept: application/json
Accept-Language: en-AU
If-Match: W/"INT-HOSP-2026-001-v2"
```

Success:
```http
HTTP/1.1 204 No Content
```

ETag mismatch:
```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied If-Match value does not match the current resource version for 'INT-HOSP-2026-001'.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

# 3. `/intent/hub` interfaces

## POST /intentManagement/v5/intent/hub

### Summary
Creates a new `EventSubscription` in IC MS for external `Intent` and `IntentReport` events.

```http
POST /intentManagement/v5/intent/hub HTTP/1.1
Host: mycsp.com.au
Content-Type: application/json
Accept: application/json
Accept-Language: en-AU
```

```json
{
  "callback": "https://consumer.example.com/listener/intentCreateEvent",
  "query": "eventType=IntentCreateEvent"
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Language: en-AU
Location: https://mycsp.com.au/intentManagement/v5/intent/hub/ESUB-1001
ETag: W/"ESUB-1001-r1"
Cache-Control: private, max-age=300
```

```json
{
  "id": "ESUB-1001",
  "href": "https://mycsp.com.au/intentManagement/v5/intent/hub/ESUB-1001",
  "callback": "https://consumer.example.com/listener/intentCreateEvent",
  "query": "eventType=IntentCreateEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/hub/ESUB-1001",
      "method": "GET"
    },
    "delete": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/hub/ESUB-1001",
      "method": "DELETE"
    }
  }
}
```

Other request variants:
```json
{
  "callback": "https://consumer.example.com/listener/intentAttributeValueChangeEvent",
  "query": "eventType=IntentAttributeValueChangeEvent"
}
```

```json
{
  "callback": "https://consumer.example.com/listener/intentStatusChangeEvent",
  "query": "eventType=IntentStatusChangeEvent"
}
```

```json
{
  "callback": "https://consumer.example.com/listener/intentDeleteEvent",
  "query": "eventType=IntentDeleteEvent"
}
```

```json
{
  "callback": "https://consumer.example.com/listener/intentReportCreateEvent",
  "query": "eventType=IntentReportCreateEvent"
}
```

```json
{
  "callback": "https://consumer.example.com/listener/intentReportAttributeValueChangeEvent",
  "query": "eventType=IntentReportAttributeValueChangeEvent"
}
```

```json
{
  "callback": "https://consumer.example.com/listener/intentReportDeleteEvent",
  "query": "eventType=IntentReportDeleteEvent"
}
```

---

## DELETE /intentManagement/v5/intent/hub/{id}

### Summary
Deletes an existing `EventSubscription`.

```http
DELETE /intentManagement/v5/intent/hub/ESUB-1001 HTTP/1.1
Host: mycsp.com.au
Accept: application/json
Accept-Language: en-AU
If-Match: W/"ESUB-1001-r1"
```

Success:
```http
HTTP/1.1 204 No Content
```

ETag mismatch:
```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied If-Match value does not match the current resource version for EventSubscription 'ESUB-1001'.",
  "status": 412,
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

---

# 4. `IntentReport` interfaces

## Terminology refinement

Use in external `IntentReport`:
- `metrics`
- `targets`
- `evaluations`

Avoid:
- `observedOutcome`
- `expectations`

Preferred report pattern:
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

## GET /intentManagement/v5/intent/{intentId}/intentReport

### Summary
Lists `IntentReport` resources for a given `Intent`.

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport?offset=0&limit=10 HTTP/1.1
Host: mycsp.com.au
Accept: application/json
Accept-Language: en-AU
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
ETag: W/"intent-report-list-r1"
X-Total-Count: 1
X-Result-Count: 1
Cache-Control: private, max-age=300
```

```json
[
  {
    "id": "IR-INT-HOSP-2026-001-001",
    "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
    "name": "Sydney Hospital Surgical Connection Intent Report",
    "description": "Curated external report for the Sydney Hospital surgical connection intent.",
    "creationDate": "2026-04-18T12:15:00+10:00",
    "lastUpdate": "2026-04-18T12:15:00+10:00",
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "@type": "IntentRef",
      "@referredType": "Intent"
    },
    "@type": "IntentReport",
    "_links": {
      "self": {
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
        "method": "GET"
      }
    }
  }
]
```

---

## GET /intentManagement/v5/intent/{intentId}/intentReport/{id}

### Summary
Retrieves a single richer curated `IntentReport`.

```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001 HTTP/1.1
Host: mycsp.com.au
Accept: application/json
Accept-Language: en-AU
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001
ETag: W/"IR-INT-HOSP-2026-001-001-r1"
Cache-Control: private, max-age=300
```

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

Not found:
```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

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

---

# 5. External `Intent...Event` family

## IntentCreateEvent
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

## IntentAttributeValueChangeEvent
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

## IntentStatusChangeEvent
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

## IntentDeleteEvent
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

---

# 6. External `IntentReport...Event` family

## IntentReportCreateEvent
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

## IntentReportAttributeValueChangeEvent
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

## IntentReportDeleteEvent
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentReportDeleteEvent for deletion of the Sydney Hospital surgical connection intent report.",
  "eventId": "EVT-IR-INT-HOSP-2026-001-001-DELETE-0001",
  "eventTime": "2026-04-19T09:10:00+10:00",
  "eventType": "IntentReportDeleteEvent",
  "priority": "3",
  "title": "IntentReportDeleteEvent",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
      "name": "Sydney Hospital Surgical Connection Intent Report",
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
  "@type": "IntentReportDeleteEvent"
}
```

---

# 7. Internal touchpoints relevant to IC MS

## IntentValidatedEvent
IC MS emits `IntentValidatedEvent` after syntactic validation succeeds, handing off to II MS.

## IntentAssuranceEvent
IC MS consumes `IntentAssuranceEvent` as the shared internal assurance truth event to keep external lifecycle/reporting state aligned with actual network state.

## Internal event role summary

- `IntentValidatedEvent` → emitted by IC MS
- `IntentRejectedEvent` → consumed by IC MS indirectly for lifecycle projection
- `IntentResolvedEvent` → internal II MS positive handoff
- `IntentOptimisedEvent` → optimiser handoff back to II MS
- `IntentNetworkReadyEvent` → internal apply-ready handoff
- `IntentAssuranceEvent` → consumed by both II MS and IC MS as platform assurance truth

---

# 8. Completion status

The IC MS baseline pack now covers:
- `/intent`
- `/intent/hub`
- `IntentReport`
- external `Intent...Event`
- external `IntentReport...Event`
- relevant IC MS internal event touchpoints

## IC MS projection rule from IntentAssuranceEvent

### Rule
IC MS derives external lifecycle/reporting updates from `IntentAssuranceEvent`.

IA MS emits `IntentAssuranceEvent` only on status/lifecycle change.

IC MS updates both:
- external `Intent`
- external `IntentReport`

for the same emitted `IntentAssuranceEvent`.

### Effective projection table

| Event situation | Update `Intent` | Update `IntentReport` |
|---|---|---|
| `Active` status change | Yes | Yes |
| `Degraded` status change | Yes | Yes |
| `Paused` status change | Yes | Yes |
| `Failed` status change | Yes | Yes |
| `Terminated` status change | Yes | Yes |
| Metric-only change without status change | No event | No |
| Candidate-only change without status change | No event | No |

### Intent
Keep the runtime projection model simple:
- no separate lifecycle-only IA->IC event
- no metric-only or candidate-only external update trigger without a status/lifecycle change
