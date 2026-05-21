# Optimisation Screen Builder MS Specification

## 1. Service purpose:

OSB MS means Optimisation Screen Builder MS.

OSB MS is the context-aware OEX facade / backend-for-frontend service for optimisation experiences. OSB MS sits behind OGW and receives user context from the User Context JWT passed by OGW. It shapes the OEX optimisation experience and calls backend optimisation domain APIs through NGW.

OSB MS initially supports runtime optimisation journeys through OC MS, including capability discovery, request form construction, runtime optimisation creation, status/detail views, cancellation, and retrial. It may later support catalogue-management journeys through OD MS for approved optimisation domain engineers.

OSB MS is not the source of truth for `OptimisationSpecification` or runtime `Optimisation` resources.

## 2. Ownership boundary:

OSB MS owns:

- OEX-friendly optimisation experience APIs.
- Context-aware view shaping.
- Capability cards and landing-page models.
- Request-form models derived from OD MS specifications.
- Runtime optimisation list/detail view models.
- Context-aware action exposure such as cancellation and retrial.
- User-context-based filtering of visible capabilities and records.
- Catalogue-management screen support for approved optimisation domain engineers when enabled.

OSB MS does not own:

- `OptimisationSpecification` source of truth.
- Runtime `Optimisation` lifecycle source of truth.
- Kafka outbox/inbox processing.
- Solver execution.
- Gurobi model binding.
- Optimisation result projection.
- OD MS catalogue governance.
- OC MS runtime lifecycle governance.

Source-of-truth ownership:

```text
OD MS: owns OptimisationSpecification definitions and lifecycle/version governance.
OC MS: owns runtime Optimisation resources, lifecycle, event projection, and result projection.
OSB MS: owns OEX experience/context-aware facade behaviour only.
```

## 3. API compliance:

OSB APIs are private OEX experience APIs and do not need to be TMF-compliant.

NGW-exposed backend OD MS and OC MS APIs remain TMF-style optimiser-domain platform APIs. OSB MS must not expose backend OD/OC resource contracts directly unless the UI journey explicitly needs that shape.

OSB MS may transform backend OD/OC responses into UI-friendly models, but it must not change backend lifecycle semantics, result semantics, ETag semantics, or contract-validation decisions.

## 4. Recommended namespace:

```http
/optimisationExperience/v1
```

Avoid using backend resource namespaces directly from OSB:

```http
/optimisation
/optimisationSpecification
```

Those backend namespaces belong to OC MS and OD MS behind NGW.

OSB uses pluralised experience endpoint names intentionally. Backend OC MS and OD MS resource endpoint names remain unchanged behind NGW.

## 5. Phase one endpoint set:

```http
GET /optimisationExperience/v1/home
GET /optimisationExperience/v1/capabilities
GET /optimisationExperience/v1/capabilities/{capabilityId}/request-form
POST /optimisationExperience/v1/optimisations
GET /optimisationExperience/v1/optimisations
GET /optimisationExperience/v1/optimisations/{id}
POST /optimisationExperience/v1/optimisations/{id}/cancellation
POST /optimisationExperience/v1/optimisations/{id}/retrial
```

Path identity rules:

```text
capabilityId maps to OD MS OptimisationSpecification.id in phase one.
OSB aliases or slugs are not introduced in the baseline.
If OSB aliases are introduced later, their derivation, stability, and version-activation behaviour must be specified explicitly.
```



## 6. OSB response model baseline:

OSB response models are experience models, not source-of-truth domain resources. OD MS remains the source of truth for `OptimisationSpecification`, and OC MS remains the source of truth for runtime `Optimisation`.

Minimal OSB view model types:

| View model | Purpose |
|---|---|
| `HomeView` | OEX landing-page model containing visible capability summaries, recent/active runtime optimisation summaries, high-level counts, and available top-level actions. |
| `CapabilityCard` | OEX-friendly summary of an available optimisation capability derived from OD MS. |
| `RequestFormModel` | OEX-friendly form model generated from OD MS metadata and schema. |
| `CreationResultView` | OEX-friendly runtime creation result derived from OC MS `201 Created`. |
| `OptimisationSummaryView` | OEX-friendly list-row/summary representation of runtime optimisation state. |
| `OptimisationDetailView` | OEX-friendly detail representation of runtime optimisation state and terminal result where present. |
| `AvailableAction` | OEX action affordance derived from backend `_links` and further restricted by user context. |

OSB may rename, group, or format fields for OEX usability, but it must preserve backend lifecycle semantics, action semantics, status codes, ETags, and diagnostic correlation identifiers.


## 7. Security and identity boundary:

### 7.1. OGW -> OSB MS:

```text
mTLS
User Context JWT
```

OGW is the user-context-aware gateway for OEX/experience APIs. OSB MS receives user context from OGW and uses it to shape views, filter visible actions, and determine whether the user can access a journey.

### 7.2. OSB MS -> NGW:

```text
mTLS
OAuth2 system-to-system
```

User context stops before/at NGW. Downstream OD MS and OC MS calls use system/service identity only. OSB MS must not forward end-user identity, roles, claims, or scopes to OD MS or OC MS as backend authorisation context.

OSB MS is responsible for user-context-aware experience-layer authorisation before calling NGW. OD MS and OC MS authorise the calling system/service and enforce their own lifecycle, schema, ETag, and business rules.

OSB MS does not bypass NGW to call OD MS or OC MS directly unless explicitly approved by architecture/security governance.

OSB user-context filtering is not a security substitute for backend enforcement. If OSB shows an action but OD MS or OC MS rejects it, the backend decision wins. OSB must not assume visibility, freshness, or action eligibility from cached UI state alone.

## 8. Runtime optimisation flow:

```text
User -> OEX UI -> OGW -> OSB MS -> NGW -> OC MS
```

OSB MS must preserve the runtime expression shape expected by OC MS:

```text
expression.@type = JsonLdExpression
expression.@baseType = Expression
expression.iri = optimisation ontology/model IRI
expression.expressionValue.@context
expression.expressionValue.@type = opt:OptimisationProblem
expression.expressionValue.context.targets[]
expression.expressionValue.context.constraints[]
expression.expressionValue.context.preferences[]
```

OSB MS may construct an OEX-friendly request form from OD MS metadata, but the submitted backend runtime request must still conform to the OC MS `POST /optimisation` contract and the referenced ACTIVE OD MS `targetEntitySchema`.

Request-form generation rules:

```text
Request forms may be generated from OD MS specCharacteristic[], expressionSpecification, and targetEntitySchema.
specCharacteristic[] is UI guidance, discovery metadata, defaults, examples, and display guidance only.
targetEntitySchema remains the authoritative validation contract.
expressionSpecification provides expression type/language/ontology binding.
OSB form validation is pre-validation only.
OC MS remains the final runtime contract validator.
```

## 9. Catalogue/specification flow:

```text
User -> OEX UI -> OGW -> OSB MS -> NGW -> OD MS
```

Catalogue-management endpoints and view models are out of phase-one scope unless explicitly enabled.

When catalogue-management is disabled, OSB MS must not expose OD MS write, activation, or retirement journeys.

Only approved optimisation domain engineers can access catalogue write, activation, and retirement journeys when the feature is enabled.

When catalogue-management journeys are enabled, OSB MS must preserve OD MS governance:

```text
DRAFT specifications are mutable.
DRAFT specifications have no official public version.
Official version is assigned by OD MS during activation.
ACTIVE and RETIRED specifications are immutable.
Multiple DRAFT specifications may exist in the same familyId.
Only one ACTIVE specification is enforced per familyId.
PATCH requires application/merge-patch+json.
PUT requires application/json and is allowed only for mutable DRAFT replacement/finalisation.
```

OSB MS must not invent, override, or expose its own versioning semantics for `OptimisationSpecification`.

## 10. Backend mapping:

| OSB endpoint | Backend mapping | OSB responsibility |
|---|---|---|
| `GET /optimisationExperience/v1/home` | OSB aggregates/context-shapes from NGW -> OD MS and NGW -> OC MS as required. | Build landing-page model, cards, and available actions. |
| `GET /optimisationExperience/v1/capabilities` | NGW -> OD MS `GET /optimisationSpecification`. | Show visible optimisation capabilities. |
| `GET /optimisationExperience/v1/capabilities/{capabilityId}/request-form` | NGW -> OD MS `GET /optimisationSpecification/{id}`. | Transform specification metadata/schema into a request form model. |
| `POST /optimisationExperience/v1/optimisations` | NGW -> OC MS `POST /optimisation`. | Submit runtime request and return OEX-friendly `CreationResultView`. Backend success maps to OC `201 Created`. |
| `GET /optimisationExperience/v1/optimisations` | NGW -> OC MS `GET /optimisation`. | Return context-filtered list/detail summary. |
| `GET /optimisationExperience/v1/optimisations/{id}` | NGW -> OC MS `GET /optimisation/{id}`. | Transform backend state/result into UI-friendly detail. |
| `POST /optimisationExperience/v1/optimisations/{id}/cancellation` | NGW -> OC MS `POST /optimisation/{id}/cancellation`. | Expose cancellation only when user context and backend lifecycle/action model allow it. |
| `POST /optimisationExperience/v1/optimisations/{id}/retrial` | NGW -> OC MS `POST /optimisation/{id}/retrial`. | Expose retrial only when user context and backend lifecycle/action model allow it. |

## 11. Home aggregation behaviour:

`GET /optimisationExperience/v1/home` returns a `HomeView`.

The baseline `HomeView` is an experience model containing:

```text
visible optimisation capabilities
recent and/or active runtime Optimisation summaries
high-level counts or status buckets where useful
available top-level actions
support/diagnostic correlation metadata where applicable
```

OSB may aggregate from OD MS and OC MS through NGW to build this view. `HomeView` is not a source-of-truth resource and must not be used as the authoritative lifecycle, contract, or result record.

## 12. Capabilities filtering behaviour:

`GET /optimisationExperience/v1/capabilities` exposes an OEX-safe capability-browsing surface over OD MS `OptimisationSpecification` resources.

Baseline OSB capability filters:

| Query parameter | Behaviour |
|---|---|
| `familyId` | Maps to OD MS `familyId` filter where authorised. |
| `name` | Maps to OD MS `name` filter where authorised. |
| `lifecycleStatus` | Defaults to `ACTIVE` for normal OEX capability browsing. `DRAFT` and `RETIRED` are exposed only for authorised catalogue-management journeys when enabled. |
| `fields` | Optional top-level sparse field projection where supported by OSB view model. |

Normal OEX capability browsing must default to ACTIVE capabilities only.

## 13. Runtime creation behaviour:

When OSB MS calls OC MS through NGW to create a runtime optimisation, OC MS returns `201 Created` when the runtime `Optimisation` resource is created immediately.

OSB MS should return `201 Created` to OEX when OC MS returns `201 Created`, because OSB is acting as the direct experience facade for runtime creation. OSB may return an OEX-friendly `CreationResultView`, but it must preserve the backend creation semantics, backend `Location`, backend resource identifier, and backend correlation/trace identifiers where available.

OSB MS must preserve this semantic distinction:

```text
Resource creation is immediate.
Execution is asynchronous.
201 Created from OC MS does not mean the optimisation is feasible, started, solvable, or guaranteed to produce a valid result.
```

OSB MS may translate the response into an OEX-friendly message, but must not present creation as successful optimisation completion. OSB MS MUST NOT translate OC MS `201 Created` into a message implying optimisation completion.

## 14. Contract pointer and specification reference behaviour:

OSB MS must preserve the caller-selected or system-selected `optimisationSpecification.id` when submitting the backend runtime request to OC MS.

OC MS persists the referenced `OptimisationSpecification.id` and `href` as the immutable contract pointer for the runtime `Optimisation`. OSB MS must not later substitute a different `OptimisationSpecification`, even a newer ACTIVE specification in the same family, for an already accepted runtime record.

If a specification is later `RETIRED`, existing runtime optimisation records remain valid audit records tied to the original `optimisationSpecification.id`.

## 15. Result display behaviour:

OSB MS must follow OC MS result presence rules:

```text
result MUST be absent in ACKNOWLEDGED, QUEUED, PROCESSING, and CANCELLING.
result MAY be present in COMPLETED, INFEASIBLE, FAILED, and CANCELLED.
FAILED result details may contain safe error codes/messages only.
OSB MS must not expose sensitive solver internals, Gurobi model formulation, credentials, infrastructure details, or raw stack traces.
```

OSB MS may present human-friendly labels, progress indicators, or guidance, but must not invent backend result values that are not present in the OC MS response.

## 16. Runtime action exposure:

OSB should use backend `_links` from OC MS as the authoritative runtime action affordance signal, then further restrict visible actions using the User Context JWT.

Action visibility rule:

```text
actionVisible = backend_link_present AND user_context_allows
```

OSB must not expose cancellation or retrial if the corresponding backend `_links` action is not present in the OC MS response. OSB may hide an available backend action when user context does not allow it, but it must not invent backend actions locally.

## 17. Cancellation and retrial behaviour:

### 17.1. Cancellation:

OSB MS exposes cancellation only when the user context and backend lifecycle state allow it.

Cancellation request body baseline:

```text
No request body is required.
If a body is supplied by OEX, it may contain optional reason/comment metadata only.
A supplied cancellation body must not change backend cancellation semantics.
```

Cancellation is best-effort. `CANCELLED` is set only after worker confirmation through OC MS event projection or an equivalent terminal confirmation path.

If OC MS returns `409 Conflict` because the runtime optimisation is already terminal, OSB MS must show an appropriate lifecycle-conflict message instead of hiding it as a generic failure.

### 17.2. Retrial:

Retrial is available only from `FAILED` in the baseline.

Retrial request body baseline:

```text
No request body is required.
Baseline retrial does not allow request overrides.
Retrial resubmits the original accepted expression and referenced OptimisationSpecification.id unchanged.
To change targets, constraints, preferences, source context, priority, or the referenced OptimisationSpecification, the caller must create a new Optimisation request rather than using retrial.
```

Retrial is not available from `INFEASIBLE` by default because `INFEASIBLE` is a valid optimisation/model outcome, not a technical execution failure.

## 18. Concurrency handling:

OSB MS must preserve backend ETag semantics for unsafe runtime operations.

```text
OSB MS receives or stores the current ETag from OC MS responses.
For cancellation and retrial, OSB MS forwards If-Match to OC MS through NGW.
OSB must forward the OC MS ETag and must not generate its own ETag for backend unsafe operations.
If OSB does not have a current ETag, it must refresh the runtime Optimisation before issuing cancellation/retrial, or return a refresh-required response to OEX.
OC MS remains the runtime concurrency source of truth.
```

Backend `412 Precondition Failed` and `428 Precondition Required` must not be hidden as generic failures.

## 19. Cache posture:

OSB may cache read-only capability, form, and view data only where backend cache headers and lifecycle rules allow.

OD MS capability/form data:

```text
ACTIVE OptimisationSpecification contracts are immutable.
OSB may cache OD-derived capability/form data only in line with OD/NGW cache policy.
OSB must not use cached OD data to bypass backend validation.
```

OC MS runtime data:

```text
Runtime Optimisation state changes over time.
OSB should avoid long-lived caching for runtime status/detail views.
OSB must not use cached runtime state alone to determine action eligibility.
```

## 20. Runtime status refresh:

Phase-one OEX/OSB status refresh is REST polling against OC MS through NGW.

Rules:

```text
OSB observes runtime progress through OC MS REST APIs.
OSB must not infer terminal status locally.
Terminal state must come from OC MS.
Polling cadence is owned by OSB MS in coordination with the OEX UI/platform UX. It is not owned by OD MS or OC MS.
```

## 21. Filtering, fields, and count handling:

OSB MS may expose OEX-friendly filters, but backend runtime filtering is performed by OC MS and backend capability filtering is performed by OD MS.

`GET /optimisationExperience/v1/optimisations` exposes an OEX-safe subset of OC MS runtime filters:

| Query parameter | Behaviour |
|---|---|
| `lifecycleStatus` | Maps to OC MS runtime lifecycle filter. |
| `sourceContext.domain` | Maps to OC MS source-context domain filter where authorised. |
| `sourceContext.resource.id` | Maps to OC MS source resource filter where authorised. |
| `optimisationSpecification.id` | Maps to OC MS referenced specification filter. |
| `creationDate.gt` / `creationDate.lt` | Maps to OC MS creation date range filter. |
| `lastUpdate.gt` / `lastUpdate.lt` | Maps to OC MS last-update range filter. |
| `statusChangeDate.gt` / `statusChangeDate.lt` | Maps to OC MS lifecycle-change date range filter. |
| `fields` | Optional top-level sparse field projection where supported by OSB view model. |

OSB may further restrict optimisation list results based on the User Context JWT. OSB must not expose backend records the user context is not allowed to view.

When proxying or translating `fields`:

```text
OD MS and OC MS baseline fields projection supports top-level fields only.
Nested field selection is not supported in the baseline.
Valid-but-absent lifecycle fields are omitted silently by OD MS/OC MS.
Unsupported field names return 400 from backend services.
```

When displaying backend list counts:

```text
X-Total-Count reflects total resources matching backend filters before paging and sparse projection.
X-Result-Count reflects resources returned in the current response page.
```

OSB MS may transform these into UI pagination metadata but must preserve their meaning.

## 22. Error handling:

OSB MS must preserve important backend error semantics:

| Backend condition | Backend status | OSB behaviour |
|---|---:|---|
| OD/OC contract validation failure | `422` | Show validation/contract error, not generic failure. |
| Lifecycle/action conflict | `409` | Show lifecycle/action conflict. |
| Missing `If-Match` | `428` | Refresh/retry guidance; do not hide as generic failure. |
| Stale/wrong `If-Match` | `412` | Show stale state and ask user to refresh. |
| Unsupported media type | `415` | Treat as OSB/client integration defect. |
| Backend resource not found or not visible | `404` | Show not found / no longer visible. |

OSB MS may map backend error bodies to OEX-friendly messages, but it must preserve the backend status and correlation information for support and troubleshooting.

OSB must preserve `correlationId` and `traceId` from backend headers and/or backend error bodies, and pass them through to OEX-layer error responses or logging following platform trace-header conventions. OSB may add its own correlation identifier, but it must not discard backend diagnostic identifiers.

## 23. Event posture:

OSB MS does not publish or consume the optimiser Kafka worker events.

Internal optimiser eventing remains owned by OC MS and the Python/Gurobi Worker:

```text
OptimisationRequestedEvent
OptimisationCompletedEvent
```

OSB MS observes runtime progress only through OC MS REST APIs exposed through NGW.

## 24. OSB MS non-goals:

OSB MS is not:

```text
source of truth for OptimisationSpecification
source of truth for runtime Optimisation
contract validator of record
runtime lifecycle owner
optimiser Kafka event publisher or consumer
solver/orchestration engine
replacement for OD MS or OC MS
```

## 25. Open design guardrails:

OSB MS must not:

```text
perform solver feasibility checks
evaluate optimisation candidate quality
modify runtime result projection
rewrite OptimisationSpecification references on existing runtime records
bypass NGW for OD/OC calls without explicit approval
forward end-user context to OD MS or OC MS
invent lifecycle transitions not present in OC MS
invent specification version semantics not present in OD MS
```
