## ID MS Design Baseline:

### Purpose:

ID MS (`intent-design-ms`) owns the design-time lifecycle and governance of `IntentSpecification` resources for the Intent Management Enabler platform.

ID MS is the source of truth for `IntentSpecification` resources and their versioning, lifecycle state, subscription model, and external design-time events where required.

ID MS does not own runtime `Intent`, `IntentReport`, lifecycle projection, interpretation/resolution, optimisation, assurance, callback ingestion, or orchestration execution.

## Service Identity:

| **Attribute** | **Baseline** |
|---|---|
| Display name | Intent Design MS |
| Service name | `intent-design-ms` |
| Short name | ID MS |
| Primary resource | `IntentSpecification` |
| Base path | `/intentManagement/v5/intentSpecification` |
| API style | TMF-aligned REST |
| Persistence | Managed PostgreSQL / PostgreSQL-compatible RDBMS + JSONB |
| Main responsibility | Design-time intent specification lifecycle and governance |

## Responsibilities:

| **Responsibility** | **Baseline** |
|---|---|
| `IntentSpecification` source of truth | ID MS owns persisted specification resources |
| Specification lifecycle | ID MS owns create, retrieve, list, update, version, activate, retire/delete governance |
| Specification versioning | Meaningful changes to active specifications require new versions |
| Concurrency | ETag on resource responses; `If-Match` required for PUT/PATCH/DELETE |
| HATEOAS | Responses include state-appropriate `_links` |
| Hub subscriptions | ID MS owns `/intentSpecification/hub` subscriptions |
| External events | ID MS publishes `IntentSpecification*Event` where required |
| Syntax/resource shape validation | ID MS validates resource shape and syntax |

## ID MS Does Not Own:

| **Concern** | **Owner** |
|---|---|
| Runtime `Intent` lifecycle | IC MS |
| `IntentReport` | IC MS |
| External lifecycle projection | IC MS, based on IA-driven lifecycle/assurance outcomes |
| Intent interpretation/resolution | II MS |
| Semantic/policy validation | II MS and Knowledge Plane |
| Optimisation | IO MS |
| Runtime assurance | IA MS |
| Callback ingestion | ICB MS |
| Orchestration execution | Orchestration layer / network orchestrator |
| OEX user experience | OEX layer |

## API Baseline:

| **Operation** | **Method / Path** | **Baseline** |
|---|---|---|
| Create specification | `POST /intentManagement/v5/intentSpecification` | Creates a new `IntentSpecification`, usually in `DRAFT` |
| List specifications | `GET /intentManagement/v5/intentSpecification` | Returns top-level array of `IntentSpecification` resources |
| Retrieve specification | `GET /intentManagement/v5/intentSpecification/{id}` | Returns one full resource |
| Full update | `PUT /intentManagement/v5/intentSpecification/{id}` | Preferred deterministic full update; requires `If-Match` |
| Partial update | `PATCH /intentManagement/v5/intentSpecification/{id}` | Supported for compatibility but discouraged; requires `If-Match` |
| Delete / retire | `DELETE /intentManagement/v5/intentSpecification/{id}` | Requires `If-Match`; must respect lifecycle/reference safety |
| Create subscription | `POST /intentManagement/v5/intentSpecification/hub` | Creates event subscription |
| Retrieve subscription | `GET /intentManagement/v5/intentSpecification/hub/{id}` | Retrieves subscription by id |
| Delete subscription | `DELETE /intentManagement/v5/intentSpecification/hub/{id}` | Deletes subscription |

## Concurrency and Caching Baseline:

| **Concern** | **Baseline** |
|---|---|
| ETag | Mandatory for create/retrieve/list/update responses |
| `If-Match` | Required for PUT/PATCH/DELETE against existing versioned resources |
| Missing `If-Match` | `428 Precondition Required` |
| Stale `If-Match` | `412 Precondition Failed` |
| PUT | Preferred update method |
| PATCH | Supported for compatibility but discouraged |
| Response body on update | Full returned `IntentSpecification` representation |
| Cache-Control | Private/revalidation-oriented for mutable resources |

## IntentSpecification Resource Baseline:

| **Field / Area** | **Baseline** |
|---|---|
| `@type` | `IntentSpecification` |
| `@baseType` | `EntitySpecification` |
| `specCharacteristic` | High-level characteristic catalogue only |
| `expressionSpecification` | Authoritative syntax/schema for request shape |
| Nested object structure | Defined in `expressionSpecification`, not duplicated in `specCharacteristic` |
| `characteristicValueSpecification` | Used only for defaults, examples, constrained allowed values, discovery, governance, or OEX/UI prefill guidance |
| Numeric SLA values | Illustrative/default guidance only, not semantic enforcement |
| Semantic/policy validation | II MS and Knowledge Plane |
| Runtime assurance | IA MS |

## Active Surgical Specification Baseline:

| **Area** | **Baseline** |
|---|---|
| Specification id | `hospital-surgical-slice-spec-v1.19` |
| Specification type | Syntax-first |
| Priority field | `priority`, not `priority_level` |
| Semantic validation | Outside ID MS; owned by II MS / Knowledge Plane |
| Runtime assurance | IA MS |

## Characteristic Governance IDs:

| **Field name** | **specCharacteristic.id** |
|---|---|
| `location` | `SC-LOCATION-001` |
| `serviceClass` | `SC-SERVICE-CLASS-001` |
| `priority` | `SC-POLICY-PRIORITY-001` |
| `maxLatencyMs` | `SC-ASSURANCE-LATENCY-001` |
| `minAvailabilityPercent` | `SC-ASSURANCE-AVAILABILITY-001` |
| `maxJitterMs` | `SC-ASSURANCE-JITTER-001` |
| `maxPacketLossPercent` | `SC-ASSURANCE-PACKET-LOSS-001` |
| `redundancyRequired` | `SC-RESILIENCE-REDUNDANCY-001` |
| `preferredAccessTechnology` | `SC-ACCESS-TECHNOLOGY-001` |
| `timeWindow` | `SC-DELIVERY-TIME-WINDOW-001` |

`specCharacteristic.name` must remain equal to the expression schema field name.

## Expression Specification Rules:

| **Area** | **Baseline** |
|---|---|
| `location` | Closed top-level object with `additionalProperties: false` |
| Permitted `location` fields | `locationId`, `locationType`, `geographicScope` |
| `location.locationId` | Required and non-empty |
| `geographicScope` | Intentionally open with `additionalProperties: true` for platform-controlled extension |
| `serviceClass` | Uses `const: "surgical-slice"` |
| `priority` | May use enum values `clinical-critical`, `high`, `standard` where constrained values are required |
| `timeWindow` | Optional object |
| `timeWindow.startDateTime` | Required when `timeWindow` is present |
| `timeWindow.endDateTime` | Optional |

## POST /intentManagement/v5/intentSpecification Baseline:

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

### Successful Response Headers:

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

## Hub Subscription Baseline:

| **Path** | **Purpose** |
|---|---|
| `/intentManagement/v5/intentSpecification/hub` | Create/list/manage subscriptions where applicable |
| `/intentManagement/v5/intentSpecification/hub/{id}` | Retrieve/delete specific subscription |

| **Event Type** | **Purpose** |
|---|---|
| `IntentSpecificationCreateEvent` | Specification created |
| `IntentSpecificationAttributeValueChangeEvent` | Specification attribute changed |
| `IntentSpecificationStatusChangeEvent` | Specification lifecycle/status changed |
| `IntentSpecificationDeleteEvent` | Specification deleted/retired according to governance policy |

Subscriptions should use explicit `eventType` filters.

## Persistence Baseline:

| **Area** | **Baseline** |
|---|---|
| DB type | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| Flexible body storage | JSONB |
| DB ownership | Dedicated ID MS DB instance or logical managed DB boundary |
| Shared DB | Not allowed across MSs |
| Schema migration | Flyway or Liquibase |
| Manual production schema changes | Not permitted |
| Future DR | Cross-region active-passive DR path required |

## Security Baseline:

| **Concern** | **Baseline** |
|---|---|
| External access | Through Gateway |
| Authentication | Gateway-managed |
| Authorisation | ID MS enforces resource/action-level authorisation where required |
| Direct exposure | ID MS should not be directly exposed externally |
| Correlation | ID MS logs and propagates correlation context |
| Infrastructure access | Authenticated service identity, least privilege, encrypted connectivity, managed secrets/certs, environment-scoped roles, audit/monitoring |

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
