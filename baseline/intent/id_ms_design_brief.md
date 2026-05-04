## ID MS Design Brief:

### Purpose:

The Intent Design MS, referred to as **ID MS**, owns the design-time lifecycle and governance of `IntentSpecification` resources.

ID MS provides the authoritative source of truth for intent specifications used by the wider Intent Management Enabler platform.

It allows authorised platform users and systems to create, retrieve, list, update, version, activate, retire, delete where allowed, and subscribe to changes in `IntentSpecification` resources.

ID MS does **not** own runtime intent instances. Runtime `Intent` and `IntentReport` resources are owned by IC MS.

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
| Event style | TMF-aligned external events for subscriptions; internal CloudEvents where needed |
| Main responsibility | Govern design-time intent specifications |

## Core Responsibilities:

| **Responsibility** | **Detail** |
|---|---|
| IntentSpecification source of truth | Owns persisted specification resources and their design-time lifecycle |
| Specification creation | Supports creation of new draft specifications |
| Specification retrieval | Supports retrieve and list operations |
| Specification full update | Supports `PUT` with ETag-based concurrency |
| Specification partial update | Supports `PATCH` for compatibility, but discourages it in favour of `PUT` |
| Specification versioning | Maintains version-specific specification records |
| Lifecycle governance | Controls draft, active, retired, deleted/tombstoned states as applicable |
| Immutability enforcement | Prevents unsafe mutation of active specifications |
| Subscription management | Supports `/intentSpecification/hub` subscriptions |
| External event publication | Emits TMF-aligned `IntentSpecification*Event` notifications where required |
| Auditability | Maintains timestamps, version metadata, ETags, governance status, and actor/source metadata |

## ID MS Does Not Own:

| **Concern** | **Owner** |
|---|---|
| Runtime `Intent` resource lifecycle | IC MS |
| `IntentReport` resource lifecycle | IC MS |
| External Intent lifecycle/status projection | IC MS |
| Intent interpretation/resolution | II MS |
| Optimisation decision | IO MS |
| Runtime assurance | IA MS |
| Raw callback ingestion | ICB MS |
| Callback lifecycle mapping | IA MS |
| Network apply/orchestration execution | Orchestration layer / network orchestrator |
| OEX user experience | OEX layer |

## API Contract Baseline:

### Resource Path:

```text
/intentManagement/v5/intentSpecification
```

### Supported Operations:

| **Operation** | **Method / Path** | **Purpose** |
|---|---|---|
| Create IntentSpecification | `POST /intentManagement/v5/intentSpecification` | Create a new specification resource |
| List IntentSpecifications | `GET /intentManagement/v5/intentSpecification` | Return a top-level array of specification resources |
| Retrieve IntentSpecification | `GET /intentManagement/v5/intentSpecification/{id}` | Retrieve one specification resource |
| Full update IntentSpecification | `PUT /intentManagement/v5/intentSpecification/{id}` | Replace/update full resource with concurrency control |
| Partial update IntentSpecification | `PATCH /intentManagement/v5/intentSpecification/{id}` | Compatibility operation; discouraged in favour of `PUT` |
| Delete / retire IntentSpecification | `DELETE /intentManagement/v5/intentSpecification/{id}` | Delete, retire, or tombstone according to lifecycle policy |
| Create subscription | `POST /intentManagement/v5/intentSpecification/hub` | Subscribe to specification events |
| Retrieve subscription | `GET /intentManagement/v5/intentSpecification/hub/{id}` | Retrieve one subscription |
| Delete subscription | `DELETE /intentManagement/v5/intentSpecification/hub/{id}` | Remove subscription |

## IntentSpecification Resource Baseline:

### Resource Type:

Use:

```json
{
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

Do not use:

```json
{
  "@baseType": "ResourceSpecification"
}
```

Reason: `IntentSpecification` is a design-time specification for an intent entity/contract. It is not a network resource specification.

### Specification Model:

| **Area** | **Baseline** |
|---|---|
| `@type` | `IntentSpecification` |
| `@baseType` | `EntitySpecification` |
| Specification style | Syntax-first |
| Syntax owner | ID MS |
| Semantic validation owner | II MS and Knowledge Plane |
| Policy validation owner | II MS and Knowledge Plane |
| Runtime assurance owner | IA MS |
| Active surgical specification | `hospital-surgical-slice-spec-v1.19` |
| Priority field | `priority`, not `priority_level` |

### `specCharacteristic` vs `expressionSpecification`:

| **Field** | **Purpose** | **Baseline Rule** |
|---|---|---|
| `specCharacteristic` | High-level characteristic catalogue | Lists supported characteristics and governance metadata |
| `expressionSpecification` | Authoritative request syntax/schema | Defines exact JSON request shape, required fields, types, ranges, and allowed object structure |
| `characteristicValueSpecification` | Defaults/examples/allowed values | Use only where it adds discovery, governance, constrained allowed values, or OEX/UI prefill guidance |

Nested object structure should not be duplicated in `specCharacteristic`. Nested object structure belongs in `expressionSpecification`.

### Numeric SLA Characteristic Values:

For these fields:

- `maxLatencyMs`
- `minAvailabilityPercent`
- `maxJitterMs`
- `maxPacketLossPercent`

values shown in `characteristicValueSpecification` are illustrative/default guidance only.

They help discovery, documentation, governance, and OEX/UI prefill behaviour.

They are not semantic enforcement rules.

ID MS validates only resource shape and syntax. II MS and Knowledge Plane own semantic and policy validation. IA MS owns runtime assurance interpretation.

## Baselined Surgical Hospital Slice Characteristics:

| **Characteristic Name** | **Governance ID** | **Value Type** | **Notes** |
|---|---|---|---|
| `location` | `SC-LOCATION-001` | object | Required; nested object shape defined only in `expressionSpecification` |
| `serviceClass` | `SC-SERVICE-CLASS-001` | string | Required; expected value `surgical-slice` |
| `priority` | `SC-POLICY-PRIORITY-001` | string | Optional; allowed values may include `critical`, `high`, `standard` |
| `maxLatencyMs` | `SC-ASSURANCE-LATENCY-001` | number | Optional; listed values are guidance only |
| `minAvailabilityPercent` | `SC-ASSURANCE-AVAILABILITY-001` | number | Optional; listed values are guidance only |
| `maxJitterMs` | `SC-ASSURANCE-JITTER-001` | number | Optional; listed values are guidance only |
| `maxPacketLossPercent` | `SC-ASSURANCE-PACKET-LOSS-001` | number | Optional; listed values are guidance only |
| `redundancyRequired` | `SC-RESILIENCE-REDUNDANCY-001` | boolean | Optional |
| `preferredAccessTechnology` | `SC-ACCESS-TECHNOLOGY-001` | string | Optional preference only |
| `timeWindow` | `SC-DELIVERY-TIME-WINDOW-001` | object | Optional; requires `startDateTime` when present |

## Expression Specification Baseline:

### Location Object:

The `location` object is closed at the top level.

Only these fields are permitted:

- `locationId`
- `locationType`
- `geographicScope`

`location.locationId` is required and must be non-empty.

`geographicScope` is intentionally open for platform-controlled extension.

### Service Class:

`serviceClass` uses a constant value for the surgical slice specification: `surgical-slice`.

### Priority:

`priority` uses the agreed field name and may use the agreed enum values where the specification wants constrained values:

- `critical`
- `high`
- `standard`

### Time Window:

`timeWindow` is optional.

When `timeWindow` is present, `startDateTime` is required.

`endDateTime` is optional.

## Lifecycle Governance:

### Lifecycle States:

| **State** | **Meaning** |
|---|---|
| `DRAFT` | Specification is editable and not yet available for runtime use |
| `ACTIVE` | Specification is approved and available for runtime intent creation |
| `RETIRED` | Specification is no longer available for new runtime intents |

`DELETED` is not an `IntentSpecification.lifecycleStatus`. Deletion is an operation/outcome governed by delete, tombstone, retention, and reference-safety policy.

### Lifecycle Rules:

| **Rule** | **Baseline** |
|---|---|
| Draft mutation | `DRAFT` specifications may be edited with valid ETag |
| Active mutation | Once `ACTIVE`, specification must not allow `PUT`, `PATCH`, or `DELETE` |
| Meaningful change after activation | Create a new versioned specification resource |
| Runtime use | Runtime intents should reference a specific active specification/version |
| Retire behaviour | Retiring prevents new runtime use but should not break existing referenced intents |
| Delete behaviour | Delete requires lifecycle and reference checks |

## Concurrency and Caching:

### ETag Baseline:

`ETag` is mandatory for create, retrieve, list, update, and relevant delete/tombstone responses.

ETags support cache validation, optimistic concurrency control, and stale update protection.

### If-Match Baseline:

`If-Match` is required for state-changing operations against existing versioned resources.

| **Operation** | **If-Match Required?** |
|---|---|
| `POST /intentManagement/v5/intentSpecification` | No |
| `PUT /intentManagement/v5/intentSpecification/{id}` | Yes |
| `PATCH /intentManagement/v5/intentSpecification/{id}` | Yes |
| `DELETE /intentManagement/v5/intentSpecification/{id}` | Yes |

### Precondition Failures:

| **Scenario** | **Response** |
|---|---|
| `If-Match` missing where required | `428 Precondition Required` |
| `If-Match` does not match current ETag | `412 Precondition Failed` |
| Valid `If-Match` but lifecycle blocks operation | `409 Conflict` or policy-specific 4xx |
| Valid operation | Success response with updated ETag where applicable |

## Operation Baselines:

### Create:

| **Concern** | **Baseline** |
|---|---|
| Endpoint | `POST /intentManagement/v5/intentSpecification` |
| Success response | `201 Created` |
| Default lifecycle | `DRAFT` |
| `If-Match` | Not required for create |
| Response headers | `Location`, `Content-Location`, `ETag`, `Last-Modified`, `Content-Type`, `Content-Language` |

### Retrieve:

| **Concern** | **Baseline** |
|---|---|
| Endpoint | `GET /intentManagement/v5/intentSpecification/{id}` |
| Success response | `200 OK` |
| Response body | Full `IntentSpecification` resource |
| Response headers | `ETag`, `Last-Modified`, `Content-Type`, `Content-Location` |

### List:

| **Concern** | **Baseline** |
|---|---|
| Endpoint | `GET /intentManagement/v5/intentSpecification` |
| Response body | Top-level array of `IntentSpecification` resources |
| Wrapper | No custom `specs` wrapper |
| Response headers | `Content-Type`, `Content-Language`, `Content-Location`, `X-Total-Count`, `X-Result-Count`, `ETag`, `Last-Modified` |

### Full Update:

| **Concern** | **Baseline** |
|---|---|
| Endpoint | `PUT /intentManagement/v5/intentSpecification/{id}` |
| Preferred update method | Yes |
| `If-Match` | Required |
| Success response | `200 OK` with full returned resource body |

### Partial Update:

| **Concern** | **Baseline** |
|---|---|
| Endpoint | `PATCH /intentManagement/v5/intentSpecification/{id}` |
| Position | Supported for compatibility but discouraged in favour of `PUT` |
| `If-Match` | Required |
| Success response | `200 OK` with full returned resource body |

### Delete / Retire:

| **Concern** | **Baseline** |
|---|---|
| Endpoint | `DELETE /intentManagement/v5/intentSpecification/{id}` |
| `If-Match` | Required |
| Safety rule | Avoid unsafe physical deletion of active or referenced specifications |
| Success response | `204 No Content` where delete/retire succeeds |

## HATEOAS Baseline:

ID MS follows HATEOAS where practical.

Resource representations should include links/controls for valid next actions.

Available links/actions should vary by resource state.

| **Resource State** | **Likely Available Links** |
|---|---|
| `DRAFT` | `self`, `update`, `patch`, `activate`, `delete` |
| `ACTIVE` | `self`, `create-new-version`, `retire` |
| `RETIRED` | `self` |

## Subscription API Baseline:

### Hub Paths:

```text
/intentManagement/v5/intentSpecification/hub
/intentManagement/v5/intentSpecification/hub/{id}
```

### Supported Subscription Event Types:

| **Event Type** | **Purpose** |
|---|---|
| `IntentSpecificationCreateEvent` | New specification created |
| `IntentSpecificationAttributeValueChangeEvent` | Specification attribute changed |
| `IntentSpecificationStatusChangeEvent` | Specification lifecycle/status changed |
| `IntentSpecificationDeleteEvent` | Specification deleted/retired according to policy |

Each subscription uses an explicit `eventType` filter in `query`.

External ID MS events are delivered through the baselined hub subscription model using at-least-once delivery. Consumers must treat events as idempotent and deduplicate using a stable `eventId`.

## Persistence Design:

ID MS follows the active IME DB baseline.

| **Concern** | **Baseline** |
|---|---|
| DB type | Managed PostgreSQL / PostgreSQL-compatible RDBMS |
| Flexible resource body | JSONB |
| DB ownership | Dedicated ID MS DB instance or logical managed DB boundary |
| Shared cross-MS DB | Not allowed |
| Schema migration | Flyway or Liquibase |
| Manual schema change | Not permitted |
| Future DR | Cross-region active-passive DR path required |

### Indicative Tables:

| **Table** | **Purpose** |
|---|---|
| `intent_specification` | Current governed specification resources |
| `intent_specification_version` | Version history where physically separated |
| `intent_specification_audit` | Audit history if not platform-provided |
| `intent_specification_outbox` | Reliable event publication if ID MS owns event relay |
| `intent_specification_hub_subscription` | Hub subscription records |
| `shedlock` | Relay coordination if ID MS runs clustered outbox relay |

## Security Baseline:

| **Concern** | **Baseline** |
|---|---|
| External access | Through Gateway |
| Authentication | Gateway-managed |
| Authorisation | ID MS enforces resource/action-level authorisation where required |
| Direct exposure | ID MS should not be directly exposed externally |
| Correlation | ID MS must log and propagate correlation context |
| Input validation | Validate request shape and lifecycle rules |
| Audit | Record governed changes |

Any ID MS integration with database, cache, Kafka topic, or other platform infrastructure must explicitly capture authenticated service identity, least-privilege access, encrypted connectivity, approved secret/certificate management, environment-scoped roles, and audit/monitoring of access failures and privileged operations.

## Observability Baseline:

### Logs:

ID MS must produce structured logs for specification create/update/delete, validation failures, ETag failures, subscription changes, event publication, and event delivery failures.

### Metrics:

Indicative metrics include create/update/delete counts, validation failures, ETag/precondition failures, active subscription count, event publish counts/failures, and API latency.

## Error Handling:

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
| Unauthorised | `401 Unauthorized` |
| Forbidden | `403 Forbidden` |
| Resource not found | `404 Not Found` |
| Duplicate `id` | `409 Conflict` |
| Unsupported media type | `415 Unsupported Media Type` |
| Missing `If-Match` | `428 Precondition Required` |
| Stale `If-Match` | `412 Precondition Failed` |
| Lifecycle transition not allowed | `409 Conflict` or policy-specific 4xx |
| Internal failure | `500 Internal Server Error` |
| Dependency unavailable | `503 Service Unavailable` |

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

## Active Baseline Summary:

ID MS is the source-of-truth service for `IntentSpecification`.

It exposes TMF-aligned REST APIs under:

```text
/intentManagement/v5/intentSpecification
```

It uses:

- `@type: IntentSpecification`
- `@baseType: EntitySpecification`
- `specCharacteristic` as high-level catalogue
- `expressionSpecification` as authoritative request syntax/schema
- mandatory ETags
- `If-Match` for PUT, PATCH, and DELETE
- JSONB for flexible specification body
- per-MS managed PostgreSQL-compatible persistence
- Flyway/Liquibase schema migrations
- `/intentSpecification/hub` subscriptions with explicit `eventType` filters

The agreed active surgical hospital specification is:

```text
hospital-surgical-slice-spec-v1.19
```

with `priority`, not `priority_level`.

ID MS validates shape and syntax only. Semantic validation, policy validation, runtime assurance, optimisation, and orchestration execution are owned by other IME components.
