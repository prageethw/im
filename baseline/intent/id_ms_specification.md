# ID MS Specification:

## Purpose:

The Intent Design MS, referred to as **ID MS**, owns the design-time lifecycle and governance of `IntentSpecification` resources.

ID MS provides the authoritative source of truth for intent specifications used by the wider Intent Management Enabler platform.

ID MS does **not** own runtime `Intent`, `IntentReport`, runtime lifecycle projection, interpretation, optimisation, assurance, callback ingestion, or orchestration execution.

## Service Identity:

| **Attribute** | **Value** |
|---|---|
| Display name | Intent Design MS |
| Service name | `intent-design-ms` |
| Short name | ID MS |
| Primary resource | `IntentSpecification` |
| Base path | `/intentManagement/v5/intentSpecification` |
| Hub path | `/intentManagement/v5/intentSpecification/hub` |
| API style | TMF-aligned REST |
| Source-of-truth database | Managed PostgreSQL / PostgreSQL-compatible RDBMS + JSONB |
| Main responsibility | Govern design-time intent specifications |

## Interface Summary:

| **Interface** | **Method / Path** | **Purpose** |
|---|---|---|
| Create IntentSpecification | `POST /intentManagement/v5/intentSpecification` | Create a new design-time `IntentSpecification` resource |
| List IntentSpecifications | `GET /intentManagement/v5/intentSpecification` | Return a top-level array of `IntentSpecification` resources |
| Retrieve IntentSpecification | `GET /intentManagement/v5/intentSpecification/{id}` | Retrieve one `IntentSpecification` resource |
| Full update IntentSpecification | `PUT /intentManagement/v5/intentSpecification/{id}` | Replace/update the full specification resource with concurrency control |
| Partial update IntentSpecification | `PATCH /intentManagement/v5/intentSpecification/{id}` | Compatibility partial update; supported but discouraged |
| Delete / retire IntentSpecification | `DELETE /intentManagement/v5/intentSpecification/{id}` | Delete, retire, or tombstone according to lifecycle/reference policy |
| Create hub subscription | `POST /intentManagement/v5/intentSpecification/hub` | Subscribe to `IntentSpecification*Event` notifications |
| Retrieve hub subscription | `GET /intentManagement/v5/intentSpecification/hub/{id}` | Retrieve one subscription record |
| Delete hub subscription | `DELETE /intentManagement/v5/intentSpecification/hub/{id}` | Remove one subscription |

## Shared Resource Rules:

| **Area** | **Baseline** |
|---|---|
| `@type` | `IntentSpecification` |
| `@baseType` | `EntitySpecification` |
| `specCharacteristic` | High-level characteristic catalogue only |
| `expressionSpecification` | Authoritative request syntax/schema |
| Nested object structure | Defined in `expressionSpecification`, not duplicated in `specCharacteristic` |
| Numeric SLA values | Discovery/OEX/UI guidance only; not semantic enforcement |
| Semantic/policy validation | II MS and Knowledge Plane, not ID MS |
| Runtime assurance | IA MS, not ID MS |
| Priority field | `priority`, not `priority_level` |
| Surgical specification | `hospital-surgical-slice-spec-v1.19` |

## Create IntentSpecification:

### Request:

```http
POST /intentManagement/v5/intentSpecification HTTP/1.1
Host: api.mycsp.com.au
Content-Type: application/json
Accept: application/json
Content-Language: en-AU
correlationid: corr-idms-20260504-001
```

### Request Body:

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Syntax-first specification for requesting a low-latency, high-availability surgical hospital network slice. This specification defines request structure only. Semantic validation, policy validation, candidate resolution, optimisation and assurance are handled by downstream IME microservices and Knowledge Plane configuration.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "validFor": {
    "startDateTime": "2026-05-04T00:00:00+10:00"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": [
    {
      "id": "SC-LOCATION-001",
      "name": "location",
      "description": "Target clinical or hospital location for the requested surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1
    },
    {
      "id": "SC-SERVICE-CLASS-001",
      "name": "serviceClass",
      "description": "Requested service class. For this specification the expected service class is surgical-slice.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "surgical-slice"
        }
      ]
    },
    {
      "id": "SC-POLICY-PRIORITY-001",
      "name": "priority",
      "description": "Policy priority requested for the intent. The platform uses this as a policy input; policy interpretation is owned by II MS and Knowledge Plane rules.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "clinical-critical"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "high"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "standard"
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-LATENCY-001",
      "name": "maxLatencyMs",
      "description": "Requested maximum acceptable latency in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 10
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-AVAILABILITY-001",
      "name": "minAvailabilityPercent",
      "description": "Requested minimum service availability percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 99.99
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-JITTER-001",
      "name": "maxJitterMs",
      "description": "Requested maximum acceptable jitter in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 5
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-PACKET-LOSS-001",
      "name": "maxPacketLossPercent",
      "description": "Requested maximum acceptable packet loss percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 0.01
        }
      ]
    },
    {
      "id": "SC-RESILIENCE-REDUNDANCY-001",
      "name": "redundancyRequired",
      "description": "Indicates whether redundant candidate paths are requested.",
      "valueType": "boolean",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "boolean",
          "isDefault": true,
          "value": true
        }
      ]
    },
    {
      "id": "SC-ACCESS-TECHNOLOGY-001",
      "name": "preferredAccessTechnology",
      "description": "Preferred access technology if the requester supplies one. This is a preference only; eligibility and optimisation are handled outside ID MS.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": false,
          "value": "5G"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "fibre"
        }
      ]
    },
    {
      "id": "SC-DELIVERY-TIME-WINDOW-001",
      "name": "timeWindow",
      "description": "Optional requested time window for the surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1
    }
  ],
  "expressionSpecification": {
    "@type": "JsonExpressionSpecification",
    "description": "Syntax-first JSON expression shape for hospital surgical slice intent requests. This schema validates structure and basic value types only. It does not perform semantic validation, policy evaluation, candidate eligibility, optimisation, assurance, or orchestration decisions.",
    "expressionLanguage": "JSON",
    "schema": {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "Hospital Surgical Slice Intent Request",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "location",
        "serviceClass"
      ],
      "properties": {
        "location": {
          "type": "object",
          "additionalProperties": false,
          "description": "Top-level location object is closed. Only locationId, locationType, and geographicScope are permitted. geographicScope itself is intentionally open for platform-controlled extension.",
          "required": [
            "locationId"
          ],
          "properties": {
            "locationId": {
              "type": "string",
              "minLength": 1,
              "description": "Platform-controlled target location identifier."
            },
            "locationType": {
              "type": "string",
              "description": "Optional target location type, such as hospital or clinical-site."
            },
            "geographicScope": {
              "type": "object",
              "additionalProperties": true,
              "description": "Optional geographic scope. Semantic interpretation is handled by Knowledge Plane rules."
            }
          }
        },
        "serviceClass": {
          "type": "string",
          "const": "surgical-slice",
          "description": "Requested service class for this specification."
        },
        "priority": {
          "type": "string",
          "enum": [
            "clinical-critical",
            "high",
            "standard"
          ],
          "description": "Policy priority input. The field name is priority, not priority_level."
        },
        "maxLatencyMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable latency in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "minAvailabilityPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested minimum service availability percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxJitterMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable jitter in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxPacketLossPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested maximum acceptable packet loss percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "redundancyRequired": {
          "type": "boolean",
          "description": "Whether redundant path/resource treatment is requested."
        },
        "preferredAccessTechnology": {
          "type": "string",
          "enum": [
            "5G",
            "fibre"
          ],
          "description": "Optional access technology preference."
        },
        "timeWindow": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "startDateTime"
          ],
          "properties": {
            "startDateTime": {
              "type": "string",
              "format": "date-time"
            },
            "endDateTime": {
              "type": "string",
              "format": "date-time"
            }
          }
        }
      }
    }
  },
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

### Response:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Language: en-AU
Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "idms-intent-spec-hospital-surgical-slice-v1.19-rev-001"
Last-Modified: Mon, 04 May 2026 10:15:00 GMT
correlationid: corr-idms-20260504-001
```

### Response Body:

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Syntax-first specification for requesting a low-latency, high-availability surgical hospital network slice. This specification defines request structure only. Semantic validation, policy validation, candidate resolution, optimisation and assurance are handled by downstream IME microservices and Knowledge Plane configuration.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "validFor": {
    "startDateTime": "2026-05-04T00:00:00+10:00"
  },
  "lastUpdate": "2026-05-04T10:15:00+10:00",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": [
    {
      "id": "SC-LOCATION-001",
      "name": "location",
      "description": "Target clinical or hospital location for the requested surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1
    },
    {
      "id": "SC-SERVICE-CLASS-001",
      "name": "serviceClass",
      "description": "Requested service class. For this specification the expected service class is surgical-slice.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "surgical-slice"
        }
      ]
    },
    {
      "id": "SC-POLICY-PRIORITY-001",
      "name": "priority",
      "description": "Policy priority requested for the intent. The platform uses this as a policy input; policy interpretation is owned by II MS and Knowledge Plane rules.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "clinical-critical"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "high"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "standard"
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-LATENCY-001",
      "name": "maxLatencyMs",
      "description": "Requested maximum acceptable latency in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 10
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-AVAILABILITY-001",
      "name": "minAvailabilityPercent",
      "description": "Requested minimum service availability percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 99.99
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-JITTER-001",
      "name": "maxJitterMs",
      "description": "Requested maximum acceptable jitter in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 5
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-PACKET-LOSS-001",
      "name": "maxPacketLossPercent",
      "description": "Requested maximum acceptable packet loss percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 0.01
        }
      ]
    },
    {
      "id": "SC-RESILIENCE-REDUNDANCY-001",
      "name": "redundancyRequired",
      "description": "Indicates whether redundant candidate paths are requested.",
      "valueType": "boolean",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "boolean",
          "isDefault": true,
          "value": true
        }
      ]
    },
    {
      "id": "SC-ACCESS-TECHNOLOGY-001",
      "name": "preferredAccessTechnology",
      "description": "Preferred access technology if the requester supplies one. This is a preference only; eligibility and optimisation are handled outside ID MS.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": false,
          "value": "5G"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "fibre"
        }
      ]
    },
    {
      "id": "SC-DELIVERY-TIME-WINDOW-001",
      "name": "timeWindow",
      "description": "Optional requested time window for the surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1
    }
  ],
  "expressionSpecification": {
    "@type": "JsonExpressionSpecification",
    "description": "Syntax-first JSON expression shape for hospital surgical slice intent requests. This schema validates structure and basic value types only. It does not perform semantic validation, policy evaluation, candidate eligibility, optimisation, assurance, or orchestration decisions.",
    "expressionLanguage": "JSON",
    "schema": {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "Hospital Surgical Slice Intent Request",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "location",
        "serviceClass"
      ],
      "properties": {
        "location": {
          "type": "object",
          "additionalProperties": false,
          "description": "Top-level location object is closed. Only locationId, locationType, and geographicScope are permitted. geographicScope itself is intentionally open for platform-controlled extension.",
          "required": [
            "locationId"
          ],
          "properties": {
            "locationId": {
              "type": "string",
              "minLength": 1,
              "description": "Platform-controlled target location identifier."
            },
            "locationType": {
              "type": "string",
              "description": "Optional target location type, such as hospital or clinical-site."
            },
            "geographicScope": {
              "type": "object",
              "additionalProperties": true,
              "description": "Optional geographic scope. Semantic interpretation is handled by Knowledge Plane rules."
            }
          }
        },
        "serviceClass": {
          "type": "string",
          "const": "surgical-slice",
          "description": "Requested service class for this specification."
        },
        "priority": {
          "type": "string",
          "enum": [
            "clinical-critical",
            "high",
            "standard"
          ],
          "description": "Policy priority input. The field name is priority, not priority_level."
        },
        "maxLatencyMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable latency in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "minAvailabilityPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested minimum service availability percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxJitterMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable jitter in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxPacketLossPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested maximum acceptable packet loss percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "redundancyRequired": {
          "type": "boolean",
          "description": "Whether redundant path/resource treatment is requested."
        },
        "preferredAccessTechnology": {
          "type": "string",
          "enum": [
            "5G",
            "fibre"
          ],
          "description": "Optional access technology preference."
        },
        "timeWindow": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "startDateTime"
          ],
          "properties": {
            "startDateTime": {
              "type": "string",
              "format": "date-time"
            },
            "endDateTime": {
              "type": "string",
              "format": "date-time"
            }
          }
        }
      }
    }
  },
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "update": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "patch": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH"
    },
    "activate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19/activate",
      "method": "POST"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "DELETE"
    }
  }
}
```

## List IntentSpecifications:

### Request:

```http
GET /intentManagement/v5/intentSpecification?lifecycleStatus=DRAFT&limit=20&offset=0 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
Accept-Language: en-AU
Cache-Control: no-cache
correlationid: corr-idms-20260504-002
```

### Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification?lifecycleStatus=DRAFT&limit=20&offset=0
X-Total-Count: 1
X-Result-Count: 1
ETag: "idms-intent-spec-list-draft-rev-001"
Last-Modified: Mon, 04 May 2026 10:15:00 GMT
Cache-Control: max-age=3600
correlationid: corr-idms-20260504-002
```

### Response Body:

```json
[
  {
    "id": "hospital-surgical-slice-spec-v1.19",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
    "name": "Hospital Surgical Slice Intent Specification",
    "description": "Syntax-first specification for requesting a low-latency, high-availability surgical hospital network slice. This specification defines request structure only. Semantic validation, policy validation, candidate resolution, optimisation and assurance are handled by downstream IME microservices and Knowledge Plane configuration.",
    "version": "1.19",
    "lifecycleStatus": "DRAFT",
    "validFor": {
      "startDateTime": "2026-05-04T00:00:00+10:00"
    },
    "lastUpdate": "2026-05-04T10:15:00+10:00",
    "@type": "IntentSpecification",
    "@baseType": "EntitySpecification",
    "specCharacteristic": [
      {
        "id": "SC-LOCATION-001",
        "name": "location",
        "description": "Target clinical or hospital location for the requested surgical slice service.",
        "valueType": "object",
        "configurable": true,
        "minCardinality": 1,
        "maxCardinality": 1
      },
      {
        "id": "SC-SERVICE-CLASS-001",
        "name": "serviceClass",
        "description": "Requested service class. For this specification the expected service class is surgical-slice.",
        "valueType": "string",
        "configurable": true,
        "minCardinality": 1,
        "maxCardinality": 1,
        "characteristicValueSpecification": [
          {
            "valueType": "string",
            "isDefault": true,
            "value": "surgical-slice"
          }
        ]
      },
      {
        "id": "SC-POLICY-PRIORITY-001",
        "name": "priority",
        "description": "Policy priority requested for the intent. The platform uses this as a policy input; policy interpretation is owned by II MS and Knowledge Plane rules.",
        "valueType": "string",
        "configurable": true,
        "minCardinality": 0,
        "maxCardinality": 1,
        "characteristicValueSpecification": [
          {
            "valueType": "string",
            "isDefault": true,
            "value": "clinical-critical"
          },
          {
            "valueType": "string",
            "isDefault": false,
            "value": "high"
          },
          {
            "valueType": "string",
            "isDefault": false,
            "value": "standard"
          }
        ]
      },
      {
        "id": "SC-ASSURANCE-LATENCY-001",
        "name": "maxLatencyMs",
        "description": "Requested maximum acceptable latency in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
        "valueType": "number",
        "configurable": true,
        "minCardinality": 0,
        "maxCardinality": 1,
        "characteristicValueSpecification": [
          {
            "valueType": "number",
            "isDefault": false,
            "value": 10
          }
        ]
      },
      {
        "id": "SC-ASSURANCE-AVAILABILITY-001",
        "name": "minAvailabilityPercent",
        "description": "Requested minimum service availability percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
        "valueType": "number",
        "configurable": true,
        "minCardinality": 0,
        "maxCardinality": 1,
        "characteristicValueSpecification": [
          {
            "valueType": "number",
            "isDefault": false,
            "value": 99.99
          }
        ]
      },
      {
        "id": "SC-ASSURANCE-JITTER-001",
        "name": "maxJitterMs",
        "description": "Requested maximum acceptable jitter in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
        "valueType": "number",
        "configurable": true,
        "minCardinality": 0,
        "maxCardinality": 1,
        "characteristicValueSpecification": [
          {
            "valueType": "number",
            "isDefault": false,
            "value": 5
          }
        ]
      },
      {
        "id": "SC-ASSURANCE-PACKET-LOSS-001",
        "name": "maxPacketLossPercent",
        "description": "Requested maximum acceptable packet loss percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
        "valueType": "number",
        "configurable": true,
        "minCardinality": 0,
        "maxCardinality": 1,
        "characteristicValueSpecification": [
          {
            "valueType": "number",
            "isDefault": false,
            "value": 0.01
          }
        ]
      },
      {
        "id": "SC-RESILIENCE-REDUNDANCY-001",
        "name": "redundancyRequired",
        "description": "Indicates whether redundant candidate paths are requested.",
        "valueType": "boolean",
        "configurable": true,
        "minCardinality": 0,
        "maxCardinality": 1,
        "characteristicValueSpecification": [
          {
            "valueType": "boolean",
            "isDefault": true,
            "value": true
          }
        ]
      },
      {
        "id": "SC-ACCESS-TECHNOLOGY-001",
        "name": "preferredAccessTechnology",
        "description": "Preferred access technology if the requester supplies one. This is a preference only; eligibility and optimisation are handled outside ID MS.",
        "valueType": "string",
        "configurable": true,
        "minCardinality": 0,
        "maxCardinality": 1,
        "characteristicValueSpecification": [
          {
            "valueType": "string",
            "isDefault": false,
            "value": "5G"
          },
          {
            "valueType": "string",
            "isDefault": false,
            "value": "fibre"
          }
        ]
      },
      {
        "id": "SC-DELIVERY-TIME-WINDOW-001",
        "name": "timeWindow",
        "description": "Optional requested time window for the surgical slice service.",
        "valueType": "object",
        "configurable": true,
        "minCardinality": 0,
        "maxCardinality": 1
      }
    ],
    "expressionSpecification": {
      "@type": "JsonExpressionSpecification",
      "description": "Syntax-first JSON expression shape for hospital surgical slice intent requests. This schema validates structure and basic value types only. It does not perform semantic validation, policy evaluation, candidate eligibility, optimisation, assurance, or orchestration decisions.",
      "expressionLanguage": "JSON",
      "schema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Hospital Surgical Slice Intent Request",
        "type": "object",
        "additionalProperties": false,
        "required": [
          "location",
          "serviceClass"
        ],
        "properties": {
          "location": {
            "type": "object",
            "additionalProperties": false,
            "description": "Top-level location object is closed. Only locationId, locationType, and geographicScope are permitted. geographicScope itself is intentionally open for platform-controlled extension.",
            "required": [
              "locationId"
            ],
            "properties": {
              "locationId": {
                "type": "string",
                "minLength": 1,
                "description": "Platform-controlled target location identifier."
              },
              "locationType": {
                "type": "string",
                "description": "Optional target location type, such as hospital or clinical-site."
              },
              "geographicScope": {
                "type": "object",
                "additionalProperties": true,
                "description": "Optional geographic scope. Semantic interpretation is handled by Knowledge Plane rules."
              }
            }
          },
          "serviceClass": {
            "type": "string",
            "const": "surgical-slice",
            "description": "Requested service class for this specification."
          },
          "priority": {
            "type": "string",
            "enum": [
              "clinical-critical",
              "high",
              "standard"
            ],
            "description": "Policy priority input. The field name is priority, not priority_level."
          },
          "maxLatencyMs": {
            "type": "number",
            "minimum": 0,
            "description": "Requested maximum acceptable latency in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
          },
          "minAvailabilityPercent": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Requested minimum service availability percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
          },
          "maxJitterMs": {
            "type": "number",
            "minimum": 0,
            "description": "Requested maximum acceptable jitter in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
          },
          "maxPacketLossPercent": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Requested maximum acceptable packet loss percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
          },
          "redundancyRequired": {
            "type": "boolean",
            "description": "Whether redundant path/resource treatment is requested."
          },
          "preferredAccessTechnology": {
            "type": "string",
            "enum": [
              "5G",
              "fibre"
            ],
            "description": "Optional access technology preference."
          },
          "timeWindow": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "startDateTime"
            ],
            "properties": {
              "startDateTime": {
                "type": "string",
                "format": "date-time"
              },
              "endDateTime": {
                "type": "string",
                "format": "date-time"
              }
            }
          }
        }
      }
    },
    "_links": {
      "self": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "update": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "method": "PUT"
      },
      "patch": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "method": "PATCH"
      },
      "activate": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19/activate",
        "method": "POST"
      },
      "delete": {
        "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "method": "DELETE"
      }
    }
  }
]
```

## Retrieve IntentSpecification:

### Request:

```http
GET /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
Accept-Language: en-AU
correlationid: corr-idms-20260504-003
```

### Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "idms-intent-spec-hospital-surgical-slice-v1.19-rev-001"
Last-Modified: Mon, 04 May 2026 10:15:00 GMT
Cache-Control: max-age=3600
correlationid: corr-idms-20260504-003
```

### Response Body:

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Syntax-first specification for requesting a low-latency, high-availability surgical hospital network slice. This specification defines request structure only. Semantic validation, policy validation, candidate resolution, optimisation and assurance are handled by downstream IME microservices and Knowledge Plane configuration.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "validFor": {
    "startDateTime": "2026-05-04T00:00:00+10:00"
  },
  "lastUpdate": "2026-05-04T10:15:00+10:00",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": [
    {
      "id": "SC-LOCATION-001",
      "name": "location",
      "description": "Target clinical or hospital location for the requested surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1
    },
    {
      "id": "SC-SERVICE-CLASS-001",
      "name": "serviceClass",
      "description": "Requested service class. For this specification the expected service class is surgical-slice.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "surgical-slice"
        }
      ]
    },
    {
      "id": "SC-POLICY-PRIORITY-001",
      "name": "priority",
      "description": "Policy priority requested for the intent. The platform uses this as a policy input; policy interpretation is owned by II MS and Knowledge Plane rules.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "clinical-critical"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "high"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "standard"
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-LATENCY-001",
      "name": "maxLatencyMs",
      "description": "Requested maximum acceptable latency in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 10
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-AVAILABILITY-001",
      "name": "minAvailabilityPercent",
      "description": "Requested minimum service availability percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 99.99
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-JITTER-001",
      "name": "maxJitterMs",
      "description": "Requested maximum acceptable jitter in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 5
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-PACKET-LOSS-001",
      "name": "maxPacketLossPercent",
      "description": "Requested maximum acceptable packet loss percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 0.01
        }
      ]
    },
    {
      "id": "SC-RESILIENCE-REDUNDANCY-001",
      "name": "redundancyRequired",
      "description": "Indicates whether redundant candidate paths are requested.",
      "valueType": "boolean",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "boolean",
          "isDefault": true,
          "value": true
        }
      ]
    },
    {
      "id": "SC-ACCESS-TECHNOLOGY-001",
      "name": "preferredAccessTechnology",
      "description": "Preferred access technology if the requester supplies one. This is a preference only; eligibility and optimisation are handled outside ID MS.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": false,
          "value": "5G"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "fibre"
        }
      ]
    },
    {
      "id": "SC-DELIVERY-TIME-WINDOW-001",
      "name": "timeWindow",
      "description": "Optional requested time window for the surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1
    }
  ],
  "expressionSpecification": {
    "@type": "JsonExpressionSpecification",
    "description": "Syntax-first JSON expression shape for hospital surgical slice intent requests. This schema validates structure and basic value types only. It does not perform semantic validation, policy evaluation, candidate eligibility, optimisation, assurance, or orchestration decisions.",
    "expressionLanguage": "JSON",
    "schema": {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "Hospital Surgical Slice Intent Request",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "location",
        "serviceClass"
      ],
      "properties": {
        "location": {
          "type": "object",
          "additionalProperties": false,
          "description": "Top-level location object is closed. Only locationId, locationType, and geographicScope are permitted. geographicScope itself is intentionally open for platform-controlled extension.",
          "required": [
            "locationId"
          ],
          "properties": {
            "locationId": {
              "type": "string",
              "minLength": 1,
              "description": "Platform-controlled target location identifier."
            },
            "locationType": {
              "type": "string",
              "description": "Optional target location type, such as hospital or clinical-site."
            },
            "geographicScope": {
              "type": "object",
              "additionalProperties": true,
              "description": "Optional geographic scope. Semantic interpretation is handled by Knowledge Plane rules."
            }
          }
        },
        "serviceClass": {
          "type": "string",
          "const": "surgical-slice",
          "description": "Requested service class for this specification."
        },
        "priority": {
          "type": "string",
          "enum": [
            "clinical-critical",
            "high",
            "standard"
          ],
          "description": "Policy priority input. The field name is priority, not priority_level."
        },
        "maxLatencyMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable latency in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "minAvailabilityPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested minimum service availability percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxJitterMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable jitter in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxPacketLossPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested maximum acceptable packet loss percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "redundancyRequired": {
          "type": "boolean",
          "description": "Whether redundant path/resource treatment is requested."
        },
        "preferredAccessTechnology": {
          "type": "string",
          "enum": [
            "5G",
            "fibre"
          ],
          "description": "Optional access technology preference."
        },
        "timeWindow": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "startDateTime"
          ],
          "properties": {
            "startDateTime": {
              "type": "string",
              "format": "date-time"
            },
            "endDateTime": {
              "type": "string",
              "format": "date-time"
            }
          }
        }
      }
    }
  },
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "update": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "patch": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH"
    },
    "activate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19/activate",
      "method": "POST"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "DELETE"
    }
  }
}
```

## Full Update IntentSpecification:

### Request:

```http
PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1
Host: api.mycsp.com.au
Content-Type: application/json
Accept: application/json
Content-Language: en-AU
If-Match: "idms-intent-spec-hospital-surgical-slice-v1.19-rev-001"
correlationid: corr-idms-20260504-004
```

### Request Body:

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated syntax-first specification for requesting a low-latency, high-availability surgical hospital network slice. This specification defines request structure only. Semantic validation, policy validation, candidate resolution, optimisation and assurance are handled by downstream IME microservices and Knowledge Plane configuration.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "validFor": {
    "startDateTime": "2026-05-04T00:00:00+10:00"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": [
    {
      "id": "SC-LOCATION-001",
      "name": "location",
      "description": "Target clinical or hospital location for the requested surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1
    },
    {
      "id": "SC-SERVICE-CLASS-001",
      "name": "serviceClass",
      "description": "Requested service class. For this specification the expected service class is surgical-slice.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "surgical-slice"
        }
      ]
    },
    {
      "id": "SC-POLICY-PRIORITY-001",
      "name": "priority",
      "description": "Policy priority requested for the intent. The platform uses this as a policy input; policy interpretation is owned by II MS and Knowledge Plane rules.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "clinical-critical"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "high"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "standard"
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-LATENCY-001",
      "name": "maxLatencyMs",
      "description": "Requested maximum acceptable latency in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 10
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-AVAILABILITY-001",
      "name": "minAvailabilityPercent",
      "description": "Requested minimum service availability percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 99.99
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-JITTER-001",
      "name": "maxJitterMs",
      "description": "Requested maximum acceptable jitter in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 5
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-PACKET-LOSS-001",
      "name": "maxPacketLossPercent",
      "description": "Requested maximum acceptable packet loss percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 0.01
        }
      ]
    },
    {
      "id": "SC-RESILIENCE-REDUNDANCY-001",
      "name": "redundancyRequired",
      "description": "Indicates whether redundant candidate paths are requested.",
      "valueType": "boolean",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "boolean",
          "isDefault": true,
          "value": true
        }
      ]
    },
    {
      "id": "SC-ACCESS-TECHNOLOGY-001",
      "name": "preferredAccessTechnology",
      "description": "Preferred access technology if the requester supplies one. This is a preference only; eligibility and optimisation are handled outside ID MS.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": false,
          "value": "5G"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "fibre"
        }
      ]
    },
    {
      "id": "SC-DELIVERY-TIME-WINDOW-001",
      "name": "timeWindow",
      "description": "Optional requested time window for the surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1
    }
  ],
  "expressionSpecification": {
    "@type": "JsonExpressionSpecification",
    "description": "Syntax-first JSON expression shape for hospital surgical slice intent requests. This schema validates structure and basic value types only. It does not perform semantic validation, policy evaluation, candidate eligibility, optimisation, assurance, or orchestration decisions.",
    "expressionLanguage": "JSON",
    "schema": {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "Hospital Surgical Slice Intent Request",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "location",
        "serviceClass"
      ],
      "properties": {
        "location": {
          "type": "object",
          "additionalProperties": false,
          "description": "Top-level location object is closed. Only locationId, locationType, and geographicScope are permitted. geographicScope itself is intentionally open for platform-controlled extension.",
          "required": [
            "locationId"
          ],
          "properties": {
            "locationId": {
              "type": "string",
              "minLength": 1,
              "description": "Platform-controlled target location identifier."
            },
            "locationType": {
              "type": "string",
              "description": "Optional target location type, such as hospital or clinical-site."
            },
            "geographicScope": {
              "type": "object",
              "additionalProperties": true,
              "description": "Optional geographic scope. Semantic interpretation is handled by Knowledge Plane rules."
            }
          }
        },
        "serviceClass": {
          "type": "string",
          "const": "surgical-slice",
          "description": "Requested service class for this specification."
        },
        "priority": {
          "type": "string",
          "enum": [
            "clinical-critical",
            "high",
            "standard"
          ],
          "description": "Policy priority input. The field name is priority, not priority_level."
        },
        "maxLatencyMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable latency in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "minAvailabilityPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested minimum service availability percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxJitterMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable jitter in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxPacketLossPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested maximum acceptable packet loss percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "redundancyRequired": {
          "type": "boolean",
          "description": "Whether redundant path/resource treatment is requested."
        },
        "preferredAccessTechnology": {
          "type": "string",
          "enum": [
            "5G",
            "fibre"
          ],
          "description": "Optional access technology preference."
        },
        "timeWindow": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "startDateTime"
          ],
          "properties": {
            "startDateTime": {
              "type": "string",
              "format": "date-time"
            },
            "endDateTime": {
              "type": "string",
              "format": "date-time"
            }
          }
        }
      }
    }
  },
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "update": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "patch": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH"
    },
    "activate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19/activate",
      "method": "POST"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "DELETE"
    }
  }
}
```

### Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "idms-intent-spec-hospital-surgical-slice-v1.19-rev-002"
Last-Modified: Mon, 04 May 2026 10:22:00 GMT
correlationid: corr-idms-20260504-004
```

### Response Body:

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Updated syntax-first specification for requesting a low-latency, high-availability surgical hospital network slice. This specification defines request structure only. Semantic validation, policy validation, candidate resolution, optimisation and assurance are handled by downstream IME microservices and Knowledge Plane configuration.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "validFor": {
    "startDateTime": "2026-05-04T00:00:00+10:00"
  },
  "lastUpdate": "2026-05-04T10:22:00+10:00",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "specCharacteristic": [
    {
      "id": "SC-LOCATION-001",
      "name": "location",
      "description": "Target clinical or hospital location for the requested surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1
    },
    {
      "id": "SC-SERVICE-CLASS-001",
      "name": "serviceClass",
      "description": "Requested service class. For this specification the expected service class is surgical-slice.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "surgical-slice"
        }
      ]
    },
    {
      "id": "SC-POLICY-PRIORITY-001",
      "name": "priority",
      "description": "Policy priority requested for the intent. The platform uses this as a policy input; policy interpretation is owned by II MS and Knowledge Plane rules.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": true,
          "value": "clinical-critical"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "high"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "standard"
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-LATENCY-001",
      "name": "maxLatencyMs",
      "description": "Requested maximum acceptable latency in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 10
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-AVAILABILITY-001",
      "name": "minAvailabilityPercent",
      "description": "Requested minimum service availability percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 99.99
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-JITTER-001",
      "name": "maxJitterMs",
      "description": "Requested maximum acceptable jitter in milliseconds. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 5
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-PACKET-LOSS-001",
      "name": "maxPacketLossPercent",
      "description": "Requested maximum acceptable packet loss percentage. Listed values are illustrative/default guidance for discovery and OEX/UI prefill only; semantic validation is handled by II MS and Knowledge Plane rules.",
      "valueType": "number",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "number",
          "isDefault": false,
          "value": 0.01
        }
      ]
    },
    {
      "id": "SC-RESILIENCE-REDUNDANCY-001",
      "name": "redundancyRequired",
      "description": "Indicates whether redundant candidate paths are requested.",
      "valueType": "boolean",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "boolean",
          "isDefault": true,
          "value": true
        }
      ]
    },
    {
      "id": "SC-ACCESS-TECHNOLOGY-001",
      "name": "preferredAccessTechnology",
      "description": "Preferred access technology if the requester supplies one. This is a preference only; eligibility and optimisation are handled outside ID MS.",
      "valueType": "string",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "valueType": "string",
          "isDefault": false,
          "value": "5G"
        },
        {
          "valueType": "string",
          "isDefault": false,
          "value": "fibre"
        }
      ]
    },
    {
      "id": "SC-DELIVERY-TIME-WINDOW-001",
      "name": "timeWindow",
      "description": "Optional requested time window for the surgical slice service.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 0,
      "maxCardinality": 1
    }
  ],
  "expressionSpecification": {
    "@type": "JsonExpressionSpecification",
    "description": "Syntax-first JSON expression shape for hospital surgical slice intent requests. This schema validates structure and basic value types only. It does not perform semantic validation, policy evaluation, candidate eligibility, optimisation, assurance, or orchestration decisions.",
    "expressionLanguage": "JSON",
    "schema": {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "Hospital Surgical Slice Intent Request",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "location",
        "serviceClass"
      ],
      "properties": {
        "location": {
          "type": "object",
          "additionalProperties": false,
          "description": "Top-level location object is closed. Only locationId, locationType, and geographicScope are permitted. geographicScope itself is intentionally open for platform-controlled extension.",
          "required": [
            "locationId"
          ],
          "properties": {
            "locationId": {
              "type": "string",
              "minLength": 1,
              "description": "Platform-controlled target location identifier."
            },
            "locationType": {
              "type": "string",
              "description": "Optional target location type, such as hospital or clinical-site."
            },
            "geographicScope": {
              "type": "object",
              "additionalProperties": true,
              "description": "Optional geographic scope. Semantic interpretation is handled by Knowledge Plane rules."
            }
          }
        },
        "serviceClass": {
          "type": "string",
          "const": "surgical-slice",
          "description": "Requested service class for this specification."
        },
        "priority": {
          "type": "string",
          "enum": [
            "clinical-critical",
            "high",
            "standard"
          ],
          "description": "Policy priority input. The field name is priority, not priority_level."
        },
        "maxLatencyMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable latency in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "minAvailabilityPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested minimum service availability percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxJitterMs": {
          "type": "number",
          "minimum": 0,
          "description": "Requested maximum acceptable jitter in milliseconds. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "maxPacketLossPercent": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Requested maximum acceptable packet loss percentage. Basic numeric syntax is validated here; semantic threshold validation is handled by II MS and Knowledge Plane rules."
        },
        "redundancyRequired": {
          "type": "boolean",
          "description": "Whether redundant path/resource treatment is requested."
        },
        "preferredAccessTechnology": {
          "type": "string",
          "enum": [
            "5G",
            "fibre"
          ],
          "description": "Optional access technology preference."
        },
        "timeWindow": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "startDateTime"
          ],
          "properties": {
            "startDateTime": {
              "type": "string",
              "format": "date-time"
            },
            "endDateTime": {
              "type": "string",
              "format": "date-time"
            }
          }
        }
      }
    }
  },
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "update": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "patch": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH"
    },
    "activate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19/activate",
      "method": "POST"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "DELETE"
    }
  }
}
```

## Partial Update IntentSpecification:

### Request:

```http
PATCH /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1
Host: api.mycsp.com.au
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "idms-intent-spec-hospital-surgical-slice-v1.19-rev-002"
correlationid: corr-idms-20260504-005
```

### Request Body:

```json
{
  "description": "Patched description for the surgical hospital slice specification. PATCH is supported for compatibility but PUT is preferred."
}
```

### Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "idms-intent-spec-hospital-surgical-slice-v1.19-rev-003"
Last-Modified: Mon, 04 May 2026 10:45:00 GMT
Cache-Control: no-cache
correlationid: corr-idms-20260504-005
```

### Response Body:

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Patched description for the surgical hospital slice specification. PATCH is supported for compatibility but PUT is preferred.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "validFor": {
    "startDateTime": "2026-05-04T00:00:00+10:00"
  },
  "lastUpdate": "2026-05-04T10:45:00+10:00",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility. PUT is preferred for deterministic full specification updates."
    },
    "update": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    }
  }
}
```

## Delete IntentSpecification:

### Request:

```http
DELETE /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19 HTTP/1.1
Host: api.mycsp.com.au
If-Match: "idms-intent-spec-hospital-surgical-slice-v1.19-rev-003"
correlationid: corr-idms-20260504-006
```

### Response:

```http
HTTP/1.1 204 No Content
correlationid: corr-idms-20260504-006
```

## Create Hub Subscription:

### Request:

```http
POST /intentManagement/v5/intentSpecification/hub HTTP/1.1
Host: api.mycsp.com.au
Content-Type: application/json
Accept: application/json
correlationid: corr-idms-20260504-007
```

### Request Body:

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",
  "query": "eventType=IntentSpecificationCreateEvent"
}
```

### Response:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001
ETag: "idms-hub-sub-create-001-rev-001"
correlationid: corr-idms-20260504-007
```

### Response Body:

```json
{
  "id": "sub-idms-spec-create-001",
  "href": "/intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001",
  "callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",
  "query": "eventType=IntentSpecificationCreateEvent",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001",
      "method": "DELETE"
    }
  }
}
```

## Retrieve Hub Subscription:

### Request:

```http
GET /intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001 HTTP/1.1
Host: api.mycsp.com.au
Accept: application/json
correlationid: corr-idms-20260504-008
```

### Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "idms-hub-sub-create-001-rev-001"
Last-Modified: Mon, 04 May 2026 10:55:00 GMT
correlationid: corr-idms-20260504-008
```

### Response Body:

```json
{
  "id": "sub-idms-spec-create-001",
  "href": "/intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001",
  "callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",
  "query": "eventType=IntentSpecificationCreateEvent",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001"
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001",
      "method": "DELETE"
    }
  }
}
```

## Delete Hub Subscription:

### Request:

```http
DELETE /intentManagement/v5/intentSpecification/hub/sub-idms-spec-create-001 HTTP/1.1
Host: api.mycsp.com.au
If-Match: "idms-hub-sub-create-001-rev-001"
correlationid: corr-idms-20260504-009
```

### Response:

```http
HTTP/1.1 204 No Content
correlationid: corr-idms-20260504-009
```

## Standard Error Response:

### Example — Missing If-Match:

```http
HTTP/1.1 428 Precondition Required
Content-Type: application/json
correlationid: corr-idms-20260504-010
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

### Example — Stale If-Match:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
correlationid: corr-idms-20260504-011
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

## Interface-Level Concurrency Rules:

| **Operation** | **ETag in Response** | **If-Match Required in Request** |
|---|---|---|
| `POST /intentManagement/v5/intentSpecification` | Yes | No |
| `GET /intentManagement/v5/intentSpecification` | Yes | No |
| `GET /intentManagement/v5/intentSpecification/{id}` | Yes | No |
| `PUT /intentManagement/v5/intentSpecification/{id}` | Yes | Yes |
| `PATCH /intentManagement/v5/intentSpecification/{id}` | Yes | Yes |
| `DELETE /intentManagement/v5/intentSpecification/{id}` | No body for `204`; `If-Match` required for precondition check | Yes |
| `POST /intentManagement/v5/intentSpecification/hub` | Yes | No |
| `GET /intentManagement/v5/intentSpecification/hub/{id}` | Yes | No |
| `DELETE /intentManagement/v5/intentSpecification/hub/{id}` | No body for `204`; `If-Match` required for precondition check | Yes |

## Open Items:

| **Open Item** | **Status** |
|---|---|
| Final concrete managed PostgreSQL service | Pending platform DB decision |
| Exact physical DB boundary | Pending platform provisioning decision |
| Final lifecycle state set | Needs confirmation against TMF/resource governance policy |
| Delete vs retire semantics | Needs final governance rule |
| Full event delivery implementation | Needs alignment with platform event delivery component |
| Audit table vs platform audit service | Needs platform audit decision |
| Exact authorisation rules | Needs security architecture decision |
| Rate limits and API quotas | Needs gateway/API platform decision |
