# id_ms_design_brief.md

## Intent Design MS design brief:

### Service identity:

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Design MS |
| Short name | ID MS |
| Service name | `intent-design-ms` |
| Domain | Intent Domain |
| External resource owned | `IntentSpecification` |
| Primary role | Design-time `IntentSpecification` catalogue, syntax contract, version/lifecycle governance, and external `IntentSpecification*Event` publication |

### Boundary:

ID MS owns the design-time `IntentSpecification` resource contract. It defines and governs the syntax contract used by runtime `Intent` creation, including `specCharacteristic`, `expressionSpecification`, and `targetEntitySchema`.

ID MS does not own runtime `Intent`, runtime `IntentReport`, runtime assurance, callback ingestion, semantic/policy interpretation, optimisation, orchestration, telemetry, Knowledge Plane internals, or internal workflow events.

External ID MS APIs and events must not leak:

- runtime Intent state
- runtime assurance state
- callback payloads
- optimiser decisions
- Knowledge Plane internals
- telemetry
- internal candidate/resource scoring
- internal workflow events

### TMF posture:

ID MS is TMF-aligned for the external `IntentSpecification` resource contract with controlled platform extensions.

Strict TMF-compatible behaviours are:

```text
POST   /intentManagement/v5/intentSpecification
GET    /intentManagement/v5/intentSpecification
GET    /intentManagement/v5/intentSpecification/{id}
PATCH  /intentManagement/v5/intentSpecification/{id}
DELETE /intentManagement/v5/intentSpecification/{id}
```

Accepted platform extensions are:

```text
PUT    /intentManagement/v5/intentSpecification/{id}

POST   /intentManagement/v5/intentSpecification/hub
GET    /intentManagement/v5/intentSpecification/hub/{id}
DELETE /intentManagement/v5/intentSpecification/hub/{id}
```

`PATCH` is supported for TMF compatibility but discouraged as the general update method. `PUT` is preferred for deterministic full replacement of editable `DRAFT` specifications.

### Lifecycle model:

The `IntentSpecification.lifecycleStatus` values are:

```text
DRAFT
ACTIVE
RETIRED
```

Do not use `DELETED` as a lifecycle state.

Only `DRAFT` specifications are editable. `ACTIVE` and `RETIRED` specifications are immutable for material update. Material contract changes after activation require a new versioned `DRAFT` specification.

### Version-family governance:

`familyId` groups versioned specifications that represent versions of the same logical specification family.

Activation rules:

- Only `DRAFT` can be activated.
- Activation changes the selected version to `ACTIVE`.
- The previous `ACTIVE` version in the same `familyId` becomes `RETIRED`.
- New runtime `Intent` creation must use the new `ACTIVE` version.
- Existing runtime intents referencing retired specifications may continue temporarily where safe.
- Activation emits two `IntentSpecificationStatusChangeEvent` events:
  - new version `DRAFT -> ACTIVE`
  - previous active version `ACTIVE -> RETIRED`

### Create baseline:

`POST /intentManagement/v5/intentSpecification` creates a new design-time specification.

The create request includes:

- `familyId`
- `name`
- `description`
- `version`
- `lifecycleStatus: DRAFT`
- `isBundle: false`
- `validFor.startDateTime`
- lightweight provider `relatedParty`
- `@type: IntentSpecification`
- `@baseType: EntitySpecification`
- `@schemaLocation`
- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`

The client does not send:

- `id`
- `href`
- `Location`
- `ETag`
- `_links`

ID MS generates those values in the response.

### Expression contract:

Use:

```json
{
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JsonLdExpression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  }
}
```

JSON Schema is not used as the TMF expression language. JSON Schema is referenced through `targetEntitySchema`.

`targetEntitySchema.@schemaLocation` points to the governed external expression-value schema that validates:

```text
Intent.expression.expressionValue
```

The runtime expression value is expected to contain:

```json
{
  "context": {
    "targets": {},
    "constraints": {},
    "preferences": {}
  }
}
```

### Canonical context buckets:

The canonical semantic buckets are:

- `targets`
- `constraints`
- `preferences`

`targets` carry measurable objectives such as latency, availability, jitter, and packet loss.

`constraints` carry hard rules and required inputs such as location, service type, service class, priority, redundancy requirement, and time window.

`preferences` carry soft selection guidance such as preferred access technology.

### List and retrieve baseline:

`GET /intentManagement/v5/intentSpecification` returns a lightweight summary list by default. It includes:

- `id`
- `href`
- `familyId`
- `name`
- `version`
- `lifecycleStatus`
- `isBundle`
- `validFor`
- `relatedParty`
- `@type`
- `@baseType`

It omits full `specCharacteristic`, `expressionSpecification`, and `targetEntitySchema` unless requested through `fields`.

`GET /intentManagement/v5/intentSpecification/{id}` returns the full single-resource representation by default. It includes:

- `id`
- `href`
- `familyId`
- `name`
- `description`
- `version`
- `lifecycleStatus`
- `isBundle`
- `validFor`
- `relatedParty`
- `@type`
- `@baseType`
- `@schemaLocation`
- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`
- server-generated `_links`

Both operations support optional TMF-style `fields`.

### Update baseline:

`PUT /intentManagement/v5/intentSpecification/{id}` is the preferred platform extension for deterministic full replacement of an editable `DRAFT` specification.

`PATCH /intentManagement/v5/intentSpecification/{id}` remains available for TMF compatibility, but it is discouraged as a general update method. Use `PATCH` only where a TMF-compatible client cannot use `PUT`, or where a tightly controlled small compatibility update is required.

`PATCH` must not normally replace material contract fields such as:

- `familyId`
- `version`
- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`
- lifecycle/version identity

### Optimistic concurrency:

Unsafe state-changing operations that require optimistic concurrency must use `If-Match`.

Missing required `If-Match` returns:

```text
428 Precondition Required
code: PRECONDITION_REQUIRED
reason: IF_MATCH_REQUIRED
```

Stale or mismatched `If-Match` returns:

```text
412 Precondition Failed
code: PRECONDITION_FAILED
reason: ETAG_MISMATCH
```

This applies consistently to PUT, PATCH, DELETE, activation/lifecycle update, and hub subscription delete where `If-Match` is required.

### Delete baseline:

`DELETE /intentManagement/v5/intentSpecification/{id}` is allowed only for unused `DRAFT` specifications.

Delete is blocked for:

- `ACTIVE`
- `RETIRED`
- specifications referenced by runtime `Intent`
- specifications retained for audit/history

Successful delete returns `204 No Content`, does not set `lifecycleStatus = DELETED`, and emits `IntentSpecificationDeleteEvent` only after successful delete.

Physical versus logical removal is an implementation detail.

### Hub subscription baseline:

ID MS intentionally uses domain-scoped hub routes:

```text
POST   /intentManagement/v5/intentSpecification/hub
GET    /intentManagement/v5/intentSpecification/hub/{id}
DELETE /intentManagement/v5/intentSpecification/hub/{id}
```

These are deliberately retained even though strict TMF uses root `/hub`.

Hub subscriptions target external listener callback URLs and use `query` to filter ID MS external `IntentSpecification*Event` notifications only.

Hub create returns:

- `201 Created`
- `Location`
- `ETag`
- response body
- server-generated `_links`

Hub retrieve returns:

- `200 OK`
- response body
- `ETag`
- private GET caching

Hub delete requires `If-Match`:

- missing `If-Match` returns `428`
- stale or mismatched `If-Match` returns `412`
- success returns `204 No Content`

The ID MS hub must not expose internal workflow events, Knowledge Plane details, runtime assurance state, telemetry, callback payloads, or fulfilment internals.

### External event baseline:

The external ID MS event family is:

```text
IntentSpecificationCreateEvent
IntentSpecificationAttributeValueChangeEvent
IntentSpecificationStatusChangeEvent
IntentSpecificationDeleteEvent
```

These are external subscription events only.

Event resource snapshots should carry consistent resource metadata:

- `id`
- `href`
- `familyId`
- `name`
- `version`
- `lifecycleStatus`
- `isBundle`
- `validFor`
- `relatedParty`
- `@type`
- `@baseType`

Status-change events include lifecycle transition fields such as:

- `previousLifecycleStatus`
- `newLifecycleStatus`

Delete events are emitted only after successful delete, show the last known lifecycle state as `DRAFT`, and must not use `DELETED`.

### Compliance status:

ID MS is compliant with the intended TMF-aligned posture, with two documented platform extensions:

- `PUT /intentManagement/v5/intentSpecification/{id}`
- domain-scoped `/intentManagement/v5/intentSpecification/hub` route family
