> Baseline pack: Intent Management / Intent Enabler only  
> Generated: 20260510_133900  
> Scope rule: Intent Management / Intent Enabler only. Do not import other domain context unless explicitly requested later.

# ID MS Specification

Service: `intent-design-ms`  
Domain: IntentSpecification catalogue and governance

## 1. Responsibility

ID MS owns IntentSpecification resources. It provides governed creation, retrieval, listing, replacement, patching, deletion/retirement support, and event subscription support for IntentSpecification changes.

ID MS validates resource shape and syntax. It does not perform deep semantic feasibility validation, orchestration validation, or runtime assurance.

## 2. TMF alignment rules

| Item | Baseline |
|---|---|
| Resource | `IntentSpecification` |
| Base type | `@baseType: EntitySpecification` |
| Characteristic catalogue | `specCharacteristic` |
| Detailed runtime request syntax | `expressionSpecification` and schema references |
| Runtime context buckets | `targets`, `constraints`, `preferences` |
| Domain fields | Model under one of the three buckets |
| Numeric SLA defaults | Discovery/governance/UI defaults, not ID semantic enforcement |

## 3. Canonical surgical hospital slice IntentSpecification

Baseline ID: `hospital-surgical-slice-spec-v1.19`

### 3.1 Create route

```http
POST /intentManagement/v5/intentSpecification HTTP/1.1
Content-Type: application/json
Accept: application/json
```

### 3.2 Create request body

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Specification for a hospital surgical service slice intent using a TMF-aligned context expression containing targets, constraints and preferences.",
  "version": "1.19",
  "lifecycleStatus": "Active",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-01-01T00:00:00Z"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": [
    {
      "id": "SC-CONTEXT-001",
      "name": "context",
      "description": "High-level runtime intent context. Detailed validation is defined by expressionSpecification and targetEntitySchema.",
      "valueType": "object",
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "valueType": "object",
          "isDefault": true,
          "value": {
            "targets": [
              {
                "targetType": "serviceExperience",
                "name": "surgical-robotics-connectivity"
              }
            ],
            "constraints": [
              {
                "constraintType": "location",
                "locationId": "hospital-campus-001",
                "locationType": "hospitalCampus"
              },
              {
                "constraintType": "serviceType",
                "serviceType": "networkSlice"
              },
              {
                "constraintType": "serviceClass",
                "serviceClass": "surgical"
              },
              {
                "constraintType": "priority",
                "priority": "critical"
              }
            ],
            "preferences": [
              {
                "preferenceType": "accessTechnology",
                "preferredAccessTechnology": "5G-SA"
              }
            ]
          },
          "@type": "CharacteristicValueSpecification"
        }
      ]
    },
    {
      "id": "SC-LOCATION-001",
      "name": "location",
      "description": "Discovery metadata for the location constraint contained in context.constraints.",
      "valueType": "object",
      "configurable": true,
      "@type": "CharacteristicSpecification"
    },
    {
      "id": "SC-SERVICE-CLASS-001",
      "name": "serviceClass",
      "description": "Discovery metadata for the service class constraint contained in context.constraints.",
      "valueType": "string",
      "configurable": true,
      "@type": "CharacteristicSpecification"
    },
    {
      "id": "SC-POLICY-PRIORITY-001",
      "name": "priority",
      "description": "Discovery metadata for priority constraint. Allowed values are critical, high and standard.",
      "valueType": "string",
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        { "valueType": "string", "value": "critical", "isDefault": true, "@type": "CharacteristicValueSpecification" },
        { "valueType": "string", "value": "high", "@type": "CharacteristicValueSpecification" },
        { "valueType": "string", "value": "standard", "@type": "CharacteristicValueSpecification" }
      ]
    },
    {
      "id": "SC-ASSURANCE-LATENCY-001",
      "name": "maxLatencyMs",
      "description": "Illustrative latency guidance for discovery and pre-fill only.",
      "valueType": "number",
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        { "valueType": "number", "value": 10, "isDefault": true, "@type": "CharacteristicValueSpecification" }
      ]
    },
    {
      "id": "SC-ASSURANCE-AVAILABILITY-001",
      "name": "minAvailabilityPercent",
      "description": "Illustrative availability guidance for discovery and pre-fill only.",
      "valueType": "number",
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        { "valueType": "number", "value": 99.99, "isDefault": true, "@type": "CharacteristicValueSpecification" }
      ]
    },
    {
      "id": "SC-ASSURANCE-JITTER-001",
      "name": "maxJitterMs",
      "description": "Illustrative jitter guidance for discovery and pre-fill only.",
      "valueType": "number",
      "configurable": true,
      "@type": "CharacteristicSpecification"
    },
    {
      "id": "SC-ASSURANCE-PACKET-LOSS-001",
      "name": "maxPacketLossPercent",
      "description": "Illustrative packet-loss guidance for discovery and pre-fill only.",
      "valueType": "number",
      "configurable": true,
      "@type": "CharacteristicSpecification"
    },
    {
      "id": "SC-RESILIENCE-REDUNDANCY-001",
      "name": "redundancyRequired",
      "description": "Discovery metadata for redundancy preference or constraint.",
      "valueType": "boolean",
      "configurable": true,
      "@type": "CharacteristicSpecification"
    },
    {
      "id": "SC-ACCESS-TECHNOLOGY-001",
      "name": "preferredAccessTechnology",
      "description": "Discovery metadata for access technology preference.",
      "valueType": "string",
      "configurable": true,
      "@type": "CharacteristicSpecification"
    },
    {
      "id": "SC-DELIVERY-TIME-WINDOW-001",
      "name": "timeWindow",
      "description": "Discovery metadata for delivery time window. When present, startDateTime is required by expressionSpecification.",
      "valueType": "object",
      "configurable": true,
      "@type": "CharacteristicSpecification"
    }
  ],
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON",
    "schema": {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "type": "object",
      "required": ["context"],
      "additionalProperties": false,
      "properties": {
        "context": {
          "type": "object",
          "required": ["targets", "constraints", "preferences"],
          "additionalProperties": false,
          "properties": {
            "targets": {
              "type": "array",
              "items": { "$ref": "#/$defs/target" },
              "minItems": 1
            },
            "constraints": {
              "type": "array",
              "items": { "$ref": "#/$defs/constraint" },
              "minItems": 1
            },
            "preferences": {
              "type": "array",
              "items": { "$ref": "#/$defs/preference" }
            }
          }
        }
      },
      "$defs": {
        "target": {
          "type": "object",
          "required": ["targetType", "name"],
          "additionalProperties": true,
          "properties": {
            "targetType": { "type": "string" },
            "name": { "type": "string" }
          }
        },
        "constraint": {
          "type": "object",
          "required": ["constraintType"],
          "additionalProperties": true,
          "properties": {
            "constraintType": { "type": "string" },
            "locationId": { "type": "string" },
            "locationType": { "type": "string" },
            "geographicScope": {
              "type": "object",
              "description": "Platform-controlled extension area for geographic scope. The location object itself remains closed to the permitted location fields."
            },
            "serviceType": { "type": "string" },
            "serviceClass": { "type": "string" },
            "priority": { "type": "string", "enum": ["critical", "high", "standard"] },
            "maxLatencyMs": { "type": "number" },
            "minAvailabilityPercent": { "type": "number" },
            "maxJitterMs": { "type": "number" },
            "maxPacketLossPercent": { "type": "number" },
            "timeWindow": {
              "type": "object",
              "required": ["startDateTime"],
              "additionalProperties": false,
              "properties": {
                "startDateTime": { "type": "string", "format": "date-time" },
                "endDateTime": { "type": "string", "format": "date-time" }
              }
            }
          }
        },
        "preference": {
          "type": "object",
          "required": ["preferenceType"],
          "additionalProperties": true,
          "properties": {
            "preferenceType": { "type": "string" },
            "preferredAccessTechnology": { "type": "string" },
            "redundancyRequired": { "type": "boolean" }
          }
        }
      }
    }
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intent/hospital-surgical-slice-expression-value-v1.19.schema.json"
  },
  "_links": {
    "self": { "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19" },
    "collection": { "href": "/intentManagement/v5/intentSpecification" }
  }
}
```

### 3.3 Create response

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "ispec-hospital-surgical-slice-spec-v1.19-v1"
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

Response body returns the created `IntentSpecification` representation.

## 4. Operations baseline

### 4.1 Create

Generic:

```http
POST /intentManagement/v5/intentSpecification
```

Concrete example:

```http
POST /intentManagement/v5/intentSpecification
```

Creates `hospital-surgical-slice-spec-v1.19` using the body in section 3.

### 4.2 Retrieve by id

Generic:

```http
GET /intentManagement/v5/intentSpecification/{id}
```

Concrete example:

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
```

Success:

```http
HTTP/1.1 200 OK
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "ispec-hospital-surgical-slice-spec-v1.19-v1"
Content-Type: application/json
Content-Language: en-AU
Cache-Control: private, max-age=60
```

### 4.3 List

```http
GET /intentManagement/v5/intentSpecification?lifecycleStatus=Active&name=Hospital%20Surgical%20Slice%20Intent%20Specification
```

List supports filtering and projection patterns consistent with TMF style where available in the implementation profile.

### 4.4 Full update

Generic:

```http
PUT /intentManagement/v5/intentSpecification/{id}
If-Match: "ispec-hospital-surgical-slice-spec-v1.19-v1"
```

Concrete example:

```http
PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
If-Match: "ispec-hospital-surgical-slice-spec-v1.19-v1"
```

PUT performs full replacement of mutable fields under governance. It requires `If-Match`.

### 4.5 Partial update

Generic:

```http
PATCH /intentManagement/v5/intentSpecification/{id}
Content-Type: application/merge-patch+json
If-Match: "ispec-hospital-surgical-slice-spec-v1.19-v1"
```

Concrete example:

```http
PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/merge-patch+json
If-Match: "ispec-hospital-surgical-slice-spec-v1.19-v1"
```

PATCH is for small non-material updates. Do not use PATCH for material runtime contract replacement unless a governed workflow explicitly allows it.

### 4.6 Delete

Generic:

```http
DELETE /intentManagement/v5/intentSpecification/{id}
If-Match: "ispec-hospital-surgical-slice-spec-v1.19-v1"
```

Concrete example:

```http
DELETE /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
If-Match: "ispec-hospital-surgical-slice-spec-v1.19-v1"
```

Success:

```http
HTTP/1.1 204 No Content
```

## 5. ETag failure examples

### 5.1 PUT stale ETag

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
  "message": "The supplied If-Match value does not match the current IntentSpecification resource version.",
  "status": "412",
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

### 5.2 PATCH stale ETag

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
  "message": "The supplied If-Match value does not match the current IntentSpecification resource version.",
  "status": "412",
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

## 6. Event subscription hub baseline

Use domain-owned hub path pattern:

```http
POST /intentManagement/v5/intentSpecification/hub
DELETE /intentManagement/v5/intentSpecification/hub/{id}
GET /intentManagement/v5/intentSpecification/hub/{id}
```

Create subscriptions using literal one-subscription-per-event-type style.

### 6.1 Create subscription examples

IntentSpecificationCreateEvent:

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",
  "query": "eventType=IntentSpecificationCreateEvent",
  "@type": "EventSubscription"
}
```

IntentSpecificationAttributeValueChangeEvent:

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationAttributeValueChangeEvent",
  "query": "eventType=IntentSpecificationAttributeValueChangeEvent",
  "@type": "EventSubscription"
}
```

IntentSpecificationStatusChangeEvent:

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationStatusChangeEvent",
  "query": "eventType=IntentSpecificationStatusChangeEvent",
  "@type": "EventSubscription"
}
```

IntentSpecificationDeleteEvent:

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationDeleteEvent",
  "query": "eventType=IntentSpecificationDeleteEvent",
  "@type": "EventSubscription"
}
```

Success response:

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hub/sub-12345
ETag: "sub-12345-v1"
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

### 6.2 Retrieve subscription by id

```http
GET /intentManagement/v5/intentSpecification/hub/sub-12345
```

```http
HTTP/1.1 200 OK
Content-Location: /intentManagement/v5/intentSpecification/hub/sub-12345
ETag: "sub-12345-v1"
Content-Type: application/json
Content-Language: en-AU
Cache-Control: private, max-age=60
```

```json
{
  "id": "sub-12345",
  "href": "/intentManagement/v5/intentSpecification/hub/sub-12345",
  "callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",
  "query": "eventType=IntentSpecificationCreateEvent",
  "@type": "EventSubscription",
  "_links": {
    "self": { "href": "/intentManagement/v5/intentSpecification/hub/sub-12345" },
    "delete": { "href": "/intentManagement/v5/intentSpecification/hub/sub-12345", "method": "DELETE" }
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
  "code": "NOT_FOUND",
  "reason": "RESOURCE_NOT_FOUND",
  "message": "EventSubscription sub-12345 was not found.",
  "status": "404",
  "referenceError": "https://mycsp.com.au/errors/NOT_FOUND",
  "@type": "Error"
}
```

### 6.3 Delete subscription

```http
DELETE /intentManagement/v5/intentSpecification/hub/sub-12345
If-Match: "sub-12345-v1"
```

Success:

```http
HTTP/1.1 204 No Content
```

Stale ETag returns `412 Precondition Failed` with the standard error body.

## 7. Security controls

| Integration | Control |
|---|---|
| ID MS to PostgreSQL | Service-specific DB role; schema/table permissions only for IntentSpecification data; encrypted connection; audit failed access |
| ID MS to event delivery mechanism | Authorised producer identity only for IntentSpecification events |
| ID MS to cache if used | Environment-scoped cache credentials; private resource caching only |
| Secrets | Managed secrets/certificates with rotation |
| API Gateway | Authenticated caller context propagated; ID MS applies authorisation for governance operations |
