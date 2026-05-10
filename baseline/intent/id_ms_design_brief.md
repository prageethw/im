# ID MS Design Brief

## 1. Business context

Intent Design MS (ID MS) provides the design-time catalogue and governance capability for `IntentSpecification` resources in the Intent Management / Intent Enabler platform.

ID MS allows the platform to define, publish, govern, version, and retire the syntax contracts used by runtime intent creation. These specifications tell clients and OEX what types of intents can be requested, what expression shape is expected, what high-level characteristics are available, and what schema artefact governs the runtime `Intent.expression.expressionValue`.

ID MS is not the runtime intent owner. It does not own runtime `Intent`, semantic validation, policy validation, optimisation, assurance, telemetry, orchestration, or callback ingestion.

## 2. Solution summary

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Design MS |
| Short name | ID MS |
| Service name | `intent-design-ms` |
| Domain | Intent Domain |
| Base path | `/intentManagement/v5` |
| Primary resource | `IntentSpecification` |
| Primary role | Design-time `IntentSpecification` catalogue, syntax contract, lifecycle/version governance, and external specification events |

ID MS exposes TMF-aligned `IntentSpecification` APIs with controlled platform extensions for deterministic update, domain-scoped subscription routes, version-family governance, ETag/If-Match concurrency, server-generated affordances, and GET-only private caching.

## 3. Solution elaboration

### 3.1 Use case view

| **Use case** | **Description** |
|---|---|
| Create IntentSpecification | Create a new `DRAFT` design-time specification with governed expression metadata and schema reference |
| List IntentSpecifications | Discover active or draft specification summaries |
| Retrieve IntentSpecification | Retrieve the full specification including characteristics, expression metadata, and runtime expression schema reference |
| Update IntentSpecification | Replace or update editable `DRAFT` specifications |
| Activate IntentSpecification | Promote a `DRAFT` version to `ACTIVE` and retire the previous active version in the same family |
| Delete IntentSpecification | Delete only unused `DRAFT` specifications |
| Subscribe to specification events | Register external listeners for ID MS `IntentSpecification*Event` notifications |
| Publish specification events | Notify subscribers when specifications are created, changed, activated, retired, or deleted |

### 3.2 Logical view

ID MS owns the design-time `IntentSpecification` resource and its persistence boundary.

ID MS owns:

- `POST /intentManagement/v5/intentSpecification`
- `GET /intentManagement/v5/intentSpecification`
- `GET /intentManagement/v5/intentSpecification/{id}`
- `PUT /intentManagement/v5/intentSpecification/{id}`
- `PATCH /intentManagement/v5/intentSpecification/{id}`
- `DELETE /intentManagement/v5/intentSpecification/{id}`
- `POST /intentManagement/v5/intentSpecification/hub`
- `GET /intentManagement/v5/intentSpecification/hub/{id}`
- `DELETE /intentManagement/v5/intentSpecification/hub/{id}`
- `IntentSpecificationCreateEvent`
- `IntentSpecificationAttributeValueChangeEvent`
- `IntentSpecificationStatusChangeEvent`
- `IntentSpecificationDeleteEvent`

ID MS does not own:

- Runtime `Intent`
- Runtime `IntentReport`
- Semantic validation
- Policy validation
- Optimisation
- Runtime assurance
- Orchestration execution
- Callback ingestion
- Runtime telemetry storage

### 3.3 Process view

#### Create specification

1. Client or OEX submits `POST /intentManagement/v5/intentSpecification`.
2. API Gateway authenticates and authorises the request.
3. ID MS validates resource shape and syntax.
4. ID MS creates a new `DRAFT` `IntentSpecification`.
5. ID MS assigns server-controlled `id`, `href`, ETag, timestamps, and `_links`.
6. ID MS persists the resource.
7. ID MS emits `IntentSpecificationCreateEvent`.
8. ID MS returns `201 Created`.

Create request baseline includes:

- `familyId`
- `name`
- `description`
- `version`
- `lifecycleStatus: DRAFT`
- `isBundle`
- `validFor`
- `relatedParty`
- `specCharacteristic`
- `expressionSpecification`
- `targetEntitySchema`
- `@type: IntentSpecification`
- `@baseType: EntitySpecification`

Client create requests must not supply server-generated `_links`.

#### Retrieve/list specification

List returns a lightweight summary by default. Retrieve returns the full single-resource representation by default.

Both operations support optional TMF-style `fields`.

GET responses use private GET-only caching and ETags. Clients can request explicit fresh retrieval with `Cache-Control: no-cache`.

#### Update specification

Only `DRAFT` specifications are editable.

`PUT /intentManagement/v5/intentSpecification/{id}` is the preferred platform extension for deterministic full replacement of an editable `DRAFT` specification.

`PATCH /intentManagement/v5/intentSpecification/{id}` remains supported for TMF compatibility, but it is discouraged as a general update method. Use PATCH only where a TMF-compatible client cannot use PUT or where a tightly controlled, small compatibility update is required.

`ACTIVE` and `RETIRED` specifications are immutable for material update.

Missing `If-Match` returns `428 Precondition Required`.

Stale or mismatched `If-Match` returns `412 Precondition Failed`.

#### Activate specification

Activation is a lifecycle update, not a custom action endpoint.

Do not expose:

```http
POST /intentManagement/v5/intentSpecification/{id}/activate
```

Activation uses:

```http
PATCH /intentManagement/v5/intentSpecification/{id}
```

for strict TMF-compatible lifecycle update, or:

```http
PUT /intentManagement/v5/intentSpecification/{id}
```

as the preferred platform extension when the caller sends the full resource.

Only `DRAFT` specifications can be activated.

On activation:

- selected version becomes `ACTIVE`
- previous `ACTIVE` version in the same `familyId` becomes `RETIRED`
- new runtime intent creation must use the new active version
- existing runtime intents referencing retired specs may continue temporarily where safe
- ID MS emits two `IntentSpecificationStatusChangeEvent` events:
  - new version `DRAFT -> ACTIVE`
  - previous active version `ACTIVE -> RETIRED`

#### Delete specification

Delete is allowed only for unused `DRAFT` specifications.

Delete is blocked for:

- `ACTIVE`
- `RETIRED`
- any specification referenced by runtime `Intent`
- audit/history retention dependencies

A successful delete returns `204 No Content`, does not set `lifecycleStatus = DELETED`, and emits `IntentSpecificationDeleteEvent` only after successful delete.

#### Hub subscription

ID MS intentionally uses domain-scoped hub routes:

```http
POST /intentManagement/v5/intentSpecification/hub
GET /intentManagement/v5/intentSpecification/hub/{id}
DELETE /intentManagement/v5/intentSpecification/hub/{id}
```

Hub subscriptions target external listener callback URLs and use `query` to filter ID MS external `IntentSpecification*Event` notifications only.

The hub must not expose internal workflow events, KP details, runtime assurance state, telemetry, callback payloads, or internal fulfilment details.

## 4. Capability matrix

| **Capability** | **ID MS responsibility** |
|---|---|
| IntentSpecification catalogue | Owns design-time resource catalogue |
| Syntax contract | Owns `expressionSpecification` and `targetEntitySchema` references |
| Characteristic catalogue | Owns `specCharacteristic` discovery metadata |
| Version governance | Owns `familyId`, active version selection, and previous version retirement |
| Lifecycle governance | Owns `DRAFT`, `ACTIVE`, `RETIRED` transitions |
| Create/list/retrieve/update/delete | Owns external TMF-aligned APIs |
| Hub subscription | Owns ID MS domain-scoped subscription routes |
| External events | Emits external `IntentSpecification*Event` notifications |
| Runtime intent management | Not owned |
| Semantic validation | Not owned |
| Policy validation | Not owned |
| Runtime assurance | Not owned |
| Callback ingestion | Not owned |

## 5. Solution security

ID MS is exposed through the API Gateway. Gateway handles authentication and primary request identity establishment.

ID MS must enforce:

- authenticated service identity for database and infrastructure access
- authorised least-privilege database access
- encrypted connectivity to persistence and platform dependencies
- no broad wildcard/admin access by default
- approved secret/certificate management and rotation
- environment-scoped principals and roles
- audit/monitoring of access failures and privileged operations
- explicit producer ownership for external specification events
- subscriber management controls for hub subscriptions
- ETag/If-Match protection for unsafe operations
- no leakage of internal workflow events, KP details, telemetry, callback payloads, or fulfilment internals through external APIs or events

## 6. Important quality attributes

| **Quality attribute** | **Baseline** |
|---|---|
| TMF compatibility | Maintain TMF-aligned resource shape, operations, event names, and `fields` support |
| Version governance | Enforce one active version per `familyId` |
| Consistency | Use ETag/If-Match on unsafe operations |
| Auditability | Preserve lifecycle, version, event, and update history as required |
| Discoverability | Expose summary list and full retrieve views |
| Extensibility | Use `targetEntitySchema` for governed expression-value schema reference |
| Encapsulation | Do not expose internal workflow or runtime fulfilment details |
| Operability | Support hub retrieve, ETag, caching, and clear error responses |

## 7. Risks

| **Risk** | **Mitigation** |
|---|---|
| Drift from TMF contract | Validate external shapes against TMF921 specification, conformance, and OAS source files |
| Confusion between design-time and runtime ownership | Keep ID MS scoped to `IntentSpecification`; runtime `Intent` remains IC MS |
| Patch misuse for material changes | Discourage PATCH generally and prefer PUT for deterministic DRAFT replacement |
| Multiple active versions | Enforce one active version per `familyId` |
| Accidental deletion of governed specs | Allow delete only for unused `DRAFT`; block active, retired, referenced, or audit-retained specs |
| Internal data leakage through events | Keep events external and resource-focused only |

## 8. Assumptions

- ID MS uses a managed PostgreSQL / PostgreSQL-compatible source-of-truth database.
- Schema migrations are versioned through Flyway or Liquibase.
- ID MS participates in platform observability and audit logging.
- Runtime `Intent` creation resolves active specifications through ID MS-facing APIs or cached read models.
- OEX may use ID MS APIs to discover available intent types and supported request shapes.

## 9. Constraints

- External API shape must remain TMF-aligned unless a platform extension is explicitly documented.
- No `DELETED` lifecycle state is used for `IntentSpecification`.
- `JsonLdExpression` remains the external TMF expression language.
- JSON Schema is referenced through `targetEntitySchema`, not used as `expressionLanguage`.
- `PATCH` is supported for TMF compatibility but discouraged as a general update method.
- `PUT` is the preferred platform extension for full replacement of editable `DRAFT` specifications.
- Domain-scoped `/intentSpecification/hub` routes are intentional.

## 10. Appendix

### Strict TMF-aligned elements

- `POST /intentManagement/v5/intentSpecification`
- `GET /intentManagement/v5/intentSpecification`
- `GET /intentManagement/v5/intentSpecification/{id}`
- `PATCH /intentManagement/v5/intentSpecification/{id}`
- `DELETE /intentManagement/v5/intentSpecification/{id}`
- TMF-style `fields`
- TMF-style `IntentSpecification*Event` names
- `@type: IntentSpecification`
- `@baseType: EntitySpecification`
- `expressionSpecification`
- `targetEntitySchema`
- `specCharacteristic`
- `validFor`
- `relatedParty`
- `isBundle`

### Intentional platform extensions

- `PUT /intentManagement/v5/intentSpecification/{id}`
- domain-scoped `/intentManagement/v5/intentSpecification/hub`
- `GET /intentManagement/v5/intentSpecification/hub/{id}`
- `familyId`
- server-generated `_links`
- ETag/If-Match concurrency
- private GET caching conventions
