# Optimisation Screen Builder MS Specification

**Document status:**

| **Field** | **Value** |
|---|---|
| **Status** | Baseline candidate |
| **Scope** | Optimisation Screen Builder MS experience API and view-model specification |
| **Source path** | `baseline/optimiser/osb-ms/osb-ms-specification.md` |
| **Source of truth** | GitHub `main` |
| **Last aligned** | 2026-05-24 |
| **Alignment scope** | Aligned with OD `specKey`, OC `creationContext`, `CANCELLATIONFAILED`, retrial, and ETag-header baseline. |

## Table of contents:

- [1. Service purpose](#1-service-purpose)
- [2. Ownership boundary](#2-ownership-boundary)
- [3. API compliance](#3-api-compliance)
- [4. Recommended namespace](#4-recommended-namespace)
- [5. Phase one endpoint set](#5-phase-one-endpoint-set)
- [6. OSB response model baseline](#6-osb-response-model-baseline)
- [7. Security and identity boundary](#7-security-and-identity-boundary)
- [8. Runtime optimisation flow](#8-runtime-optimisation-flow)
- [9. Catalogue and specification flow](#9-catalogue-and-specification-flow)
- [10. Backend mapping](#10-backend-mapping)
- [11. Home aggregation behaviour](#11-home-aggregation-behaviour)
- [12. Capabilities filtering behaviour](#12-capabilities-filtering-behaviour)
- [13. Runtime creation behaviour](#13-runtime-creation-behaviour)
- [14. Contract pointer and specification reference behaviour](#14-contract-pointer-and-specification-reference-behaviour)
- [15. Result display behaviour](#15-result-display-behaviour)
- [16. Runtime action exposure](#16-runtime-action-exposure)
- [17. Cancellation and retrial behaviour](#17-cancellation-and-retrial-behaviour)
- [18. Concurrency handling](#18-concurrency-handling)
- [19. Cache posture](#19-cache-posture)
- [20. Runtime status refresh](#20-runtime-status-refresh)
- [21. Filtering, fields, and count handling](#21-filtering-fields-and-count-handling)
- [22. Error handling](#22-error-handling)
- [23. Event posture](#23-event-posture)
- [24. OSB MS non-goals](#24-osb-ms-non-goals)
- [25. Open design guardrails](#25-open-design-guardrails)

## 1. Service purpose:

OSB MS means Optimisation Screen Builder MS.

OSB MS is the context-aware OEX facade and backend-for-frontend service for optimisation experiences. OSB MS sits behind OGW and receives user context from the User Context JWT passed by OGW. It shapes the OEX optimisation experience and calls backend optimisation domain APIs through NGW.

OSB MS initially supports runtime optimisation journeys through OC MS, including capability discovery, request form construction, runtime optimisation creation, status and detail views, cancellation, and retrial. It may later support catalogue-management journeys through OD MS for approved optimisation domain engineers.

OSB MS is not the source of truth for `OptimisationSpecification` or runtime `Optimisation` resources.

## 2. Ownership boundary:

OSB MS owns:

- OEX-friendly optimisation experience APIs.
- Context-aware view shaping.
- Capability cards and landing-page models.
- Request-form models derived from OD MS specifications.
- Runtime optimisation list and detail view models.
- Context-aware action exposure such as cancellation and retrial.
- User-context-based filtering of visible capabilities and records.
- Catalogue-management screen support for approved optimisation domain engineers when enabled.

OSB MS does not own:

- `OptimisationSpecification` source of truth.
- Runtime `Optimisation` lifecycle source of truth.
- Kafka outbox and inbox processing.
- Solver execution.
- Gurobi model binding.
- Optimisation result projection.
- OD MS catalogue governance.
- OC MS runtime lifecycle governance.

Source-of-truth ownership:

```text
OD MS: owns OptimisationSpecification definitions, lifecycle governance, and version governance.
OC MS: owns runtime Optimisation resources, lifecycle, event projection, and result projection.
OSB MS: owns OEX experience facade behaviour and context-aware facade behaviour only.
```

## 3. API compliance:

OSB APIs are private OEX experience APIs and do not need to be TMF-compliant.

NGW-exposed backend OD MS and OC MS APIs remain TMF-style optimiser-domain platform APIs. OSB MS must not expose backend OD and OC resource contracts directly unless the UI journey explicitly needs that shape.

OSB MS may transform backend OD and OC responses into UI-friendly models, but it must not change backend lifecycle semantics, result semantics, ETag semantics, or contract-validation decisions.

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

Capability browsing normally resolves current ACTIVE specifications by `capabilityId`, which maps to `OptimisationSpecification.id`. OSB may display `specKey`, `version`, and `draftId` when returned by OD MS, but it must not use `specKey` or `draftId` to choose the runtime contract for OC MS creation.



## 6. OSB response model baseline:

OSB response models are experience models, not source-of-truth domain resources. OD MS remains the source of truth for `OptimisationSpecification`, and OC MS remains the source of truth for runtime `Optimisation`.

Minimal OSB view model types:

| View model | Purpose |
|---|---|
| `HomeView` | OEX landing-page model containing visible capability summaries, recent and active runtime optimisation summaries, high-level counts, and available top-level actions. |
| `CapabilityCard` | OEX-friendly summary of an available optimisation capability derived from OD MS. |
| `RequestFormModel` | OEX-friendly form model generated from OD MS metadata and schema. |
| `CreationResultView` | OEX-friendly runtime creation result derived from OC MS `201 Created`. |
| `OptimisationSummaryView` | OEX-friendly list-row and summary representation of runtime optimisation state. |
| `OptimisationDetailView` | OEX-friendly detail representation of runtime optimisation state and terminal result where present. |
| `AvailableAction` | OEX action affordance derived from backend `_links` and further restricted by user context. |

Minimal `CapabilityCard` fields:

```text
capabilityId: OD MS OptimisationSpecification.id used by OSB capability routes.
name: display name derived from the ACTIVE OptimisationSpecification.
description: short user-facing description where available.
specKey: stable logical specification key where useful for catalogue browsing.
version: current ACTIVE official version where visible to the user journey.
status: lifecycle summary, normally ACTIVE for runtime OEX browsing.
actions[]: available top-level actions such as requestForm.
```

Minimal `RequestFormModel` fields:

```text
capabilityId: OD MS OptimisationSpecification.id.
expressionIri: value expected for Optimisation.expression.iri.
schemaRef: targetEntitySchema reference or embedded schema metadata used to build the form.
fields[]: OEX field definitions derived from targetEntitySchema and supported by specCharacteristic guidance.
fields[].name: field name or path used in the generated expression payload.
fields[].valueType: UI-friendly value type.
fields[].required: whether the field is required by the resolved schema.
fields[].default: optional default or prefill value where allowed.
fields[].examples[]: optional examples derived from OD MS metadata.
actions[]: available form actions such as submit and refreshForm.
```

Minimal `CreationResultView` fields:

```text
id: new runtime Optimisation.id returned by OC MS.
href: new runtime Optimisation.href returned by OC MS.
lifecycleStatus: initial runtime lifecycleStatus, normally ACKNOWLEDGED.
creationContext: OC MS creation context, with reason NEW for normal creation and RETRIAL for retrial-created resources where returned. When OC MS returns creationContext, OSB must include it in CreationResultView and must not infer, default, or omit it.
location: backend Location header where returned.
backendETag: backend HTTP ETag header where returned.
summary: OEX-friendly creation message that does not imply optimisation completion.
actions[]: available backend-derived actions for the created runtime Optimisation.
```

Minimal `OptimisationSummaryView` fields:

```text
id: runtime Optimisation.id returned by OC MS.
href: runtime Optimisation.href returned by OC MS.
name: runtime Optimisation name where returned by OC MS.
lifecycleStatus: current OC MS lifecycleStatus, including CANCELLATIONFAILED where returned.
statusChangeDate: timestamp of the last lifecycle change.
creationContext: OC MS creation context, with reason NEW or RETRIAL where returned.
creationDate: runtime Optimisation creation timestamp where visible to the user journey.
lastUpdate: runtime Optimisation last-update timestamp where visible to the user journey.
optimisationSpecification: resolved specification reference summary containing id, version, draftId, and href where useful for support and audit.
summary: OEX-friendly lifecycle or result summary that preserves OC MS meaning.
actions[]: available backend-derived actions after user-context filtering.
```

Minimal `OptimisationDetailView` fields:

```text
id: runtime Optimisation.id returned by OC MS.
href: runtime Optimisation.href returned by OC MS.
name: runtime Optimisation name where returned by OC MS.
description: runtime Optimisation description where returned by OC MS.
lifecycleStatus: current OC MS lifecycleStatus, including CANCELLATIONFAILED where returned.
statusChangeDate: timestamp of the last lifecycle change.
creationContext: OC MS creation context, with reason NEW or RETRIAL where returned.
creationDate: runtime Optimisation creation timestamp.
lastUpdate: runtime Optimisation last-update timestamp.
sourceContext: source context where returned and authorised for display.
optimisationSpecification: resolved specification reference containing id, version, draftId, and href.
expression: accepted runtime expression where the journey is authorised to display it.
result: optional result or command-outcome details where returned by OC MS. CANCELLATIONFAILED result details must be replaced, not merged, if a later terminal outcome is projected.
optimisationRelationship[]: optional runtime relationships such as retrialOf.
actions[]: available backend-derived actions after user-context filtering.
```

Minimal `AvailableAction` fields:

```text
name: OEX action name.
label: user-facing action label.
method: backend or OSB method for the action.
href: OSB experience endpoint for the action.
enabled: whether the action is currently enabled for the user journey.
reason: optional reason when the action is hidden or disabled.
```

OSB may rename, group, or format fields for OEX usability, but it must preserve backend lifecycle semantics, action semantics, status codes, ETags, and diagnostic correlation identifiers.

When displaying runtime optimisation records, OSB should preserve the resolved backend specification pointer in the view model where useful for support and audit. The resolved pointer may include `optimisationSpecification.id`, `version`, `draftId`, and `href` where present in the OC MS response. OD MS and OC MS ETags remain HTTP headers and must not be represented as `etag` payload fields inside `optimisationSpecification`.


## 7. Security and identity boundary:

### 7.1. OGW -> OSB MS:

```text
mTLS
User Context JWT
```

OGW is the user-context-aware gateway for OEX experience APIs. OSB MS receives user context from OGW and uses it to shape views, filter visible actions, and determine whether the user can access a journey.

### 7.2. OSB MS -> NGW:

```text
mTLS
OAuth2 system-to-system
```

User context stops before NGW or at NGW. Downstream OD MS and OC MS calls use system identity only. OSB MS must not forward end-user identity, roles, claims, or scopes to OD MS or OC MS as backend authorisation context.

OSB MS is responsible for user-context-aware experience-layer authorisation before calling NGW. OD MS and OC MS authorise the calling system/service and enforce their own lifecycle, schema, ETag, and business rules.

OSB MS does not bypass NGW to call OD MS or OC MS directly unless explicitly approved by architecture and security governance.

OSB user-context filtering is not a security substitute for backend enforcement. If OSB shows an action but OD MS or OC MS rejects it, the backend decision wins. OSB must not assume visibility, freshness, or action eligibility from cached UI state alone.

## 8. Runtime optimisation flow:

```text
User -> OEX UI -> OGW -> OSB MS -> NGW -> OC MS
```

OSB MS must preserve the runtime expression shape expected by OC MS:

```text
expression.@type = JsonLdExpression
expression.@baseType = Expression
expression.iri = optimisation ontology and model IRI
expression.expressionValue as required by the selected ACTIVE OptimisationSpecification.targetEntitySchema
expression.expressionValue.context.targets[] where defined by the selected schema
expression.expressionValue.context.constraints[] where defined by the selected schema
expression.expressionValue.context.preferences[] where defined by the selected schema
```

Runtime creation requires both `optimisationSpecification.id` and `expression.iri`. OSB MS must preserve the selected `optimisationSpecification.id` as the exact governed contract pointer and must preserve the runtime `expression.iri` as the submitted expression semantic identifier. OSB MS must not drop, rewrite, infer, or substitute either value before calling OC MS. OSB MS must not send `optimisationSpecification.version`, `optimisationSpecification.draftId`, `optimisationSpecification.href`, `optimisationSpecification.specKey`, or an `etag` payload field in runtime creation requests. OC MS resolves and persists the resolved specification pointer and returns ETags only as HTTP headers.

OSB MS may construct an OEX-friendly request form from OD MS metadata, but the submitted backend runtime request must still conform to the OC MS `POST /optimisation` contract and the referenced ACTIVE OD MS `targetEntitySchema`.

Request-form generation rules:

```text
Request forms may be generated from OD MS specCharacteristic[], expressionSpecification, and targetEntitySchema.
specCharacteristic[] is UI guidance, discovery metadata, defaults, examples, and display guidance only.
targetEntitySchema remains the authoritative validation contract.
expressionSpecification provides expression type, language, and ontology binding.
OSB form validation is pre-validation only.
OC MS remains the final runtime contract validator.
```

Request-form staleness rules:

```text
OSB builds request forms from the current ACTIVE OptimisationSpecification at form-load time.
The user may submit the form after OD MS has activated a newer official version for the same OptimisationSpecification.id.
OSB must still submit only optimisationSpecification.id and expression.iri to OC MS.
OC MS resolves the current ACTIVE version again at acceptance time and remains the final validator.
If OC MS rejects the submission because the request no longer satisfies the current ACTIVE contract, OSB must preserve the backend status and show an OEX-friendly refresh-form message.
OSB should include a refresh-form action or equivalent OEX guidance when backend validation indicates the submitted form may be stale.
OSB must not force a stale request form through by sending version, draftId, href, specKey, or an etag payload field to OC MS.
```

## 9. Catalogue and specification flow:

```text
User -> OEX UI -> OGW -> OSB MS -> NGW -> OD MS
```

Catalogue-management endpoints and view models are out of phase-one scope unless explicitly enabled.

When catalogue-management mode is enabled, the OSB endpoint set must be extended explicitly for that journey. Possible catalogue-management endpoints, such as create capability, edit DRAFT candidate, activate DRAFT candidate, retire ACTIVE version, create from existing version, or delete DRAFT candidate, are not part of the phase-one runtime endpoint set until specified and approved.

Catalogue-management support for `draftId`, DRAFT candidate editing, activation, retirement, and `createFrom` is not part of the normal runtime OEX journey. These controls are exposed only in authorised catalogue-management journeys when enabled. OSB must not expose `createFrom`, draftId mutation, activation, retirement, or DRAFT deletion actions unless catalogue-management mode is enabled and user context authorises the journey.

When catalogue-management is disabled, OSB MS must not expose OD MS write, activation, or retirement journeys.

Only approved optimisation domain engineers can access catalogue write, activation, and retirement journeys when the feature is enabled.

When catalogue-management journeys are enabled, OSB MS must preserve OD MS governance:

```text
DRAFT specifications are mutable.
DRAFT specifications have no official public version.
Official version is assigned by OD MS during activation.
ACTIVE and RETIRED specifications are immutable.
Multiple DRAFT candidates may exist for the same OptimisationSpecification.id.
Each DRAFT candidate has a server-assigned draftId.
Only one ACTIVE version is enforced per OptimisationSpecification.id.
specKey is the OD MS logical specification key. OD MS uses it when creating DRAFT candidates to resolve the server-assigned OptimisationSpecification.id.
PATCH requires application/merge-patch+json.
PUT requires application/json and is allowed only for mutable DRAFT replacement and finalisation.
```

OSB MS must not invent, override, or expose its own versioning semantics for `OptimisationSpecification`.

## 10. Backend mapping:

| OSB endpoint | Backend mapping | OSB responsibility |
|---|---|---|
| `GET /optimisationExperience/v1/home` | OSB aggregates and context-shapes from NGW -> OD MS and NGW -> OC MS as required. | Build landing-page model, cards, and available actions. |
| `GET /optimisationExperience/v1/capabilities` | NGW -> OD MS `GET /optimisationSpecification`. | Show visible optimisation capabilities. |
| `GET /optimisationExperience/v1/capabilities/{capabilityId}/request-form` | NGW -> OD MS `GET /optimisationSpecification/{id}` for the current ACTIVE version by default. | Transform specification metadata and schema into a request form model. |
| `POST /optimisationExperience/v1/optimisations` | NGW -> OC MS `POST /optimisation`. | Submit runtime request and return OEX-friendly `CreationResultView`. Backend success maps to OC `201 Created`. |
| `GET /optimisationExperience/v1/optimisations` | NGW -> OC MS `GET /optimisation`. | Return context-filtered list and detail summary. |
| `GET /optimisationExperience/v1/optimisations/{id}` | NGW -> OC MS `GET /optimisation/{id}`. | Transform backend state and result into UI-friendly detail. |
| `POST /optimisationExperience/v1/optimisations/{id}/cancellation` | NGW -> OC MS `POST /optimisation/{id}/cancellation`. | Expose cancellation only when user context and backend lifecycle and action model allow it. |
| `POST /optimisationExperience/v1/optimisations/{id}/retrial` | NGW -> OC MS `POST /optimisation/{id}/retrial`. | Expose retrial only when user context and backend lifecycle and action model allow it. |

## 11. Home aggregation behaviour:

`GET /optimisationExperience/v1/home` returns a `HomeView`.

The baseline `HomeView` is an experience model containing:

```text
visible optimisation capabilities
recent and active runtime Optimisation summaries where useful
high-level counts or status buckets where useful
available top-level actions
support and diagnostic correlation metadata where applicable
```

OSB may aggregate from OD MS and OC MS through NGW to build this view. `HomeView` is not a source-of-truth resource and must not be used as the authoritative lifecycle, contract, or result record.

If one backend dependency is unavailable while another is healthy, OSB may return a partial `HomeView` rather than failing the whole request, provided degraded sections are clearly marked and no missing backend data is represented as authoritative. Degraded sections should be represented as empty or null with an explicit service-health indicator rather than omitted silently. If the unavailable dependency is required for the requested user journey, OSB should preserve the backend failure semantics and return an appropriate error response.

## 12. Capabilities filtering behaviour:

`GET /optimisationExperience/v1/capabilities` exposes an OEX-safe capability-browsing surface over OD MS `OptimisationSpecification` resources.

Baseline OSB capability filters:

| Query parameter | Behaviour |
|---|---|
| `specKey` | Maps to OD MS `specKey` filter where authorised. |
| `name` | Maps to OD MS `name` filter where authorised. |
| `version` | Maps to OD MS official version filter only for authorised catalogue-management journeys. |
| `draftId` | Maps to OD MS draft candidate or read-only provenance lookup only for authorised catalogue-management journeys. |
| `lifecycleStatus` | Defaults to `ACTIVE` for normal OEX capability browsing. `DRAFT` and `RETIRED` are exposed only for authorised catalogue-management journeys when enabled. |
| `fields` | Optional top-level sparse field projection where supported by OSB view model. |
| `offset` | Maps to backend paging offset where supported. |
| `limit` | Maps to backend paging limit where supported. |

Normal OEX capability browsing must default to ACTIVE capabilities only.

## 13. Runtime creation behaviour:

When OSB MS calls OC MS through NGW to create a runtime optimisation, OC MS returns `201 Created` when the runtime `Optimisation` resource is created immediately.

OSB MS should return `201 Created` to OEX when OC MS returns `201 Created`, because OSB is acting as the direct experience facade for runtime creation. OSB may return an OEX-friendly `CreationResultView`, but it must preserve the backend creation semantics, backend `Location`, backend resource identifier, and backend correlation and trace identifiers where available.

OSB MS must preserve this semantic distinction:

```text
Resource creation is immediate.
Execution is asynchronous.
201 Created from OC MS does not mean the optimisation is feasible, started, solvable, or guaranteed to produce a valid result.
```

OSB MS may translate the response into an OEX-friendly message, but must not present creation as successful optimisation completion. OSB MS MUST NOT translate OC MS `201 Created` into a message implying optimisation completion.

`CreationResultView` must include, at minimum, the new runtime `Optimisation.id`, `href`, initial `lifecycleStatus`, `creationContext` where returned by OC MS, backend `Location` header where returned, backend `ETag` header where returned, and available action links derived from the OC MS response.

Runtime creation request rule:

```text
OSB sends only the selected optimisationSpecification.id to OC MS.
OSB must not send optimisationSpecification.version, optimisationSpecification.draftId, optimisationSpecification.href, optimisationSpecification.specKey, or an etag payload field in the create request.
OC MS resolves version, draftId, and href from the current ACTIVE OD MS specification and returns the persisted resolved pointer. ETags remain HTTP headers.
```

Backend request shape sent from OSB to OC MS:

```json
{
  "optimisationSpecification": {
    "id": "optimisation-spec-surgical-routing",
    "@type": "OptimisationSpecificationRef",
    "@referredType": "OptimisationSpecification"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://example.com/ontology/optimisation/v1",
    "expressionValue": {
      "...expression payload shaped by the selected ACTIVE OptimisationSpecification.targetEntitySchema...": true
    }
  }
}
```

## 14. Contract pointer and specification reference behaviour:

OSB MS must preserve the caller-selected or system-selected `optimisationSpecification.id` when submitting the backend runtime request to OC MS.

OSB MS must also preserve the runtime `expression.iri`. Runtime creation requires both `optimisationSpecification.id` and `expression.iri`; OC MS uses the id as the exact contract pointer and verifies the runtime IRI against `OptimisationSpecification.expressionSpecification.iri`.

OC MS resolves the current `ACTIVE` version for the submitted `OptimisationSpecification.id` at acceptance time and persists the resolved contract pointer, including `id`, `version`, `draftId`, and `href`. OSB MS must not later substitute a different `OptimisationSpecification`, even a newer ACTIVE version for the same id, for an already accepted runtime record. ETags remain HTTP headers and are not part of the resolved specification pointer payload.

If a specification is later `RETIRED`, existing runtime optimisation records remain valid audit records tied to the original resolved `optimisationSpecification` pointer.

## 15. Result display behaviour:

OSB MS must follow OC MS result presence rules:

```text
result MUST be absent in ACKNOWLEDGED, QUEUED, PROCESSING, and CANCELLING.
result MAY be present in CANCELLATIONFAILED, COMPLETED, INFEASIBLE, FAILED, and CANCELLED.
CANCELLATIONFAILED represents a cancellation command outcome, not an optimisation execution outcome. It is non-terminal; any result details shown for it are cancellation-command details and may later be superseded by COMPLETED, INFEASIBLE, or FAILED.
When a subsequent terminal optimisation outcome is projected after CANCELLATIONFAILED, previously displayed CANCELLATIONFAILED result details must be fully replaced and must not be merged with the final outcome.
FAILED result details may contain safe error codes and safe messages only.
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

OSB must not expose retrial when `lifecycleStatus = CANCELLATIONFAILED`, even though that state is non-terminal. Retrial is exposed only when `lifecycleStatus = FAILED`.

## 17. Cancellation and retrial behaviour:

### 17.1. Cancellation:

OSB MS exposes cancellation only when the user context and backend lifecycle state allow it.

Cancellation request body baseline:

```text
No request body is required.
If a body is supplied by OEX, it may contain optional reason or comment metadata only.
A supplied cancellation body must not change backend cancellation semantics.
OSB must not send an empty JSON object solely to force Content-Type.
If no body is supplied by OEX, OSB should call OC MS without a request body.
If a cancellation body is supplied, OSB forwards only allowed reason or comment metadata.
```

Cancellation is best-effort. OSB preserves the OC MS cancellation response status. In the baseline, OC MS returns `202 Accepted` for an accepted asynchronous cancellation command and exposes `CANCELLING` until cancellation is confirmed or the cancellation command fails. OSB must return an OEX-friendly `CANCELLING` view rather than presenting cancellation as completed. `CANCELLED` is set only after worker confirmation through `OptimisationCompletedEvent.status = CANCELLED`. `CANCELLATIONFAILED` represents a cancellation command outcome, not an optimisation execution outcome. It is non-terminal; OSB should continue polling until OC MS projects `COMPLETED`, `INFEASIBLE`, or `FAILED`. Any alternative terminal confirmation path is outside the current baseline.

If OC MS returns `409 Conflict` because the runtime optimisation is already terminal, OSB MS must show an appropriate lifecycle-conflict message instead of hiding it as a generic failure.

### 17.2. Retrial:

Retrial is available only from `FAILED` in the baseline. OSB must not expose retrial when `lifecycleStatus = CANCELLATIONFAILED`, even though that state is non-terminal.

Retrial request body baseline:

```text
No request body is required.
Baseline retrial does not allow request overrides.
Retrial resubmits the original accepted expression and the original persisted OptimisationSpecification contract pointer unchanged, including id, version, draftId, and href. ETags remain HTTP headers and are not part of the contract pointer payload.
To change targets, constraints, preferences, source context, priority, or the referenced OptimisationSpecification, the caller must create a new Optimisation request rather than using retrial.
OSB must not send an empty JSON object solely to force Content-Type.
If no body is supplied by OEX, OSB should call OC MS without a request body.
Retrial request bodies with override fields must be rejected by OSB before calling OC MS.
```

When OC MS creates a retrial Optimisation, OSB preserves the OC MS creation semantics, `Location` header, `ETag` header where returned, and new runtime Optimisation id. If OC MS returns `201 Created` for the new retrial resource, OSB should return `201 Created` with an OEX-friendly `CreationResultView`. The retrial-created resource has `creationContext.reason = RETRIAL` and a `retrialOf` relationship to the original FAILED Optimisation.

Retrial is not available from `INFEASIBLE` by default because `INFEASIBLE` is a valid optimisation model outcome, not a technical execution failure. Retrial is also not exposed from `CANCELLATIONFAILED`; if the optimisation later reaches `FAILED`, retrial may then be exposed from `FAILED`.

## 18. Concurrency handling:

OSB MS must preserve backend ETag semantics for unsafe runtime operations.

```text
OSB MS receives or stores the current ETag from OC MS responses.
For cancellation and retrial, OSB MS forwards If-Match to OC MS through NGW.
OSB must forward the OC MS ETag and must not generate its own ETag for backend unsafe operations.
If OSB does not have a current ETag, the preferred path is to refresh the runtime Optimisation before issuing cancellation or retrial. A refresh-required response to OEX is permitted when latency, consistency, or user-interaction constraints make automatic refresh inappropriate.
OC MS remains the runtime concurrency source of truth.
```

Backend `412 Precondition Failed` and `428 Precondition Required` must not be hidden as generic failures.

## 19. Cache posture:

OSB may cache read-only capability, form, and view data only where backend cache headers and lifecycle rules allow.

OD MS capability and form data:

```text
ACTIVE OptimisationSpecification versions are immutable.
OSB may cache OD-derived capability and form data only in line with OD and NGW cache policy.
OSB must not use cached OD data to bypass backend validation.
```

OC MS runtime data:

```text
Runtime Optimisation state changes over time.
OSB should avoid long-lived caching for runtime status and detail views.
OSB must not use cached runtime state alone to determine action eligibility.
```

## 20. Runtime status refresh:

Phase-one OEX and OSB status refresh is REST polling against OC MS through NGW.

Rules:

```text
OSB observes runtime progress through OC MS REST APIs.
OSB must not infer terminal status locally.
Terminal state must come from OC MS.
Polling cadence is owned by OSB MS in coordination with the OEX UI and platform UX. It is not owned by OD MS or OC MS.
OSB must implement backoff, timeout handling, and a reasonable maximum poll rate to avoid runaway polling against OC MS. Specific cadence values are implementation-defined unless set by platform operational policy.
```

## 21. Filtering, fields, and count handling:

OSB MS may expose OEX-friendly filters, but backend runtime filtering is performed by OC MS and backend capability filtering is performed by OD MS.

`GET /optimisationExperience/v1/optimisations` exposes an OEX-safe subset of OC MS runtime filters:

| Query parameter | Behaviour |
|---|---|
| `lifecycleStatus` | Maps to OC MS runtime lifecycle filter, including `CANCELLATIONFAILED` where returned by OC MS. |
| `sourceContext.domain` | Maps to OC MS source-context domain filter where authorised. |
| `sourceContext.resource.id` | Maps to OC MS source resource filter where authorised. |
| `optimisationSpecification.id` | Maps to OC MS referenced specification filter. |
| `optimisationSpecification.version` | Maps to OC MS persisted resolved specification version filter where supported. |
| `optimisationSpecification.draftId` | Maps to OC MS persisted specification draft provenance filter where supported. |
| `creationDate.gt` / `creationDate.lt` | Maps to OC MS creation date range filter. |
| `lastUpdate.gt` / `lastUpdate.lt` | Maps to OC MS last-update range filter. |
| `statusChangeDate.gt` / `statusChangeDate.lt` | Maps to OC MS lifecycle-change date range filter. |
| `fields` | Optional top-level sparse field projection where supported by OSB view model. |
| `offset` | Maps to backend paging offset where supported. |
| `limit` | Maps to backend paging limit where supported. |

`priority` filtering is not supported in the phase-one OSB runtime optimisation list baseline because OC MS does not expose `priority` as a baseline list filter. If priority filtering is required later, it must be added to OC MS first or explicitly implemented as an OSB-only post-filter with clear result-count semantics.

`optimisationSpecification.version` and `optimisationSpecification.draftId` filters are for runtime history, support, audit, and traceability. They are not used by OSB to select a runtime contract for new optimisation creation.

OSB may further restrict optimisation list results based on the User Context JWT. OSB must not expose backend records the user context is not allowed to view. If a runtime Optimisation has no `sourceContext`, OSB must apply the configured experience-layer visibility policy and must not assume the record is visible to all users.

When proxying or translating `fields`:

```text
OD MS and OC MS baseline fields projection supports top-level fields only.
Nested field selection is not supported in the baseline.
Valid-but-absent lifecycle fields are omitted silently by OD MS and OC MS.
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
| OD or OC contract validation failure | `422` | Show validation and contract error, not generic failure. |
| Lifecycle and action conflict | `409` | Show lifecycle and action conflict. |
| Missing `If-Match` | `428` | Refresh and retry guidance; do not hide as generic failure. |
| Stale or wrong `If-Match` | `412` | Show stale state and ask user to refresh. |
| Unsupported media type | `415` | Treat as OSB or client integration defect. |
| Backend resource not found or not visible | `404` | Show not found or no longer visible. |
| Malformed request, unsupported filter, or forbidden server-controlled runtime field | `400` | Show request correction guidance. |
| OD MS or OC MS unavailable | `503` | Show temporary unavailability and retry guidance without implying validation failure. |

OSB integration defects, including sending forbidden OC create fields such as `optimisationSpecification.version`, `optimisationSpecification.draftId`, `optimisationSpecification.href`, `optimisationSpecification.specKey`, or an etag payload field, must be surfaced as request correction or integration-fix guidance and must not be hidden as generic optimisation failure.

OSB MS may map backend error bodies to OEX-friendly messages, but it must preserve the backend status and correlation information for support and troubleshooting.

OSB must preserve `correlationId` and `traceId` from backend headers and backend error bodies where present, and pass them through to OEX-layer error responses or logging following platform trace-header conventions. OSB may add its own correlation identifier, but it must not discard backend diagnostic identifiers.

## 23. Event posture:

OSB MS does not publish or consume the optimiser Kafka worker events.

Internal optimiser eventing remains owned by OC MS and OW MS:

```text
OptimisationRequestedEvent
OptimisationCompletedEvent
```

OSB MS observes runtime progress only through OC MS REST APIs exposed through NGW.

## 24. OSB MS non-goals:

OSB MS is not:

- Source of truth for `OptimisationSpecification`.
- Source of truth for runtime `Optimisation`.
- Contract validator of record.
- Runtime lifecycle owner.
- Optimiser Kafka event publisher or consumer.
- Solver or orchestration engine.
- Replacement for OD MS or OC MS.

## 25. Open design guardrails:

OSB MS must not:

- Perform solver feasibility checks.
- Evaluate optimisation candidate quality.
- Modify runtime result projection.
- Rewrite `OptimisationSpecification` references on existing runtime records.
- Bypass NGW for OD or OC calls without explicit approval.
- Forward end-user context to OD MS or OC MS.
- Invent lifecycle transitions not present in OC MS.
- Invent specification version semantics not present in OD MS.
- Force stale request-form submissions through OC MS validation.
