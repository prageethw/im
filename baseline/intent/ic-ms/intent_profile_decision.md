# Intent mandatory profile proposal

| **Document status** | **Value** |
| --- | --- |
| Status | Proposed decision paper |
| Scope | Runtime Intent minimum data requirements |
| Primary focus | Admission request profile, persisted response profile, Draft request/response minimums, optional enrichment separation |
| Out of scope | Full lifecycle design, full version-history design, Draft lineage design, implementation routing details |
| Source of truth after commit | GitHub `baseline/intent/ic-ms/intent_profile_decision.md` |

## Table of contents:

- [Decision summary](#decision-summary)
- [Proposal flow diagram](#proposal-flow-diagram)
- [Context](#context)
- [Decision drivers](#decision-drivers)
- [Proposal](#proposal)
  - [TMF-aligned, not TMF-minimal](#tmf-aligned-not-tmf-minimal)
  - [Runtime Intent admission profile](#runtime-intent-admission-profile)
  - [Minimum attributes for Intent Draft creation](#minimum-attributes-for-intent-draft-creation)
  - [Minimum response attributes for Intent Draft creation](#minimum-response-attributes-for-intent-draft-creation)
  - [IntentSpecification resolution rule](#intentspecification-resolution-rule)
  - [Persisted response profile after admission](#persisted-response-profile-after-admission)
  - [Optional intent-management-entity governed enrichment fields](#optional-intent-management-entity-governed-enrichment-fields)
  - [Lifecycle ownership guardrail](#lifecycle-ownership-guardrail)
- [Examples](#examples)
  - [Minimal admission request](#minimal-admission-request)
  - [Minimal persisted response after admission](#minimal-persisted-response-after-admission)
- [Consequences](#consequences)
  - [Positive consequences](#positive-consequences)
  - [Trade-offs](#trade-offs)
- [Alternatives considered](#alternatives-considered)
  - [Make intentSpecification.id mandatory in every admission request](#make-intentspecificationid-mandatory-in-every-admission-request)
  - [Make humanExpression mandatory](#make-humanexpression-mandatory)
  - [Allow admission request without expression.iri](#allow-admission-request-without-expressioniri)
- [Proposal outcome](#proposal-outcome)
- [References](#references)
- [Follow-up work](#follow-up-work)

## Decision summary:

This proposal defines the minimum mandatory attribute profile for runtime `Intent` admission, layered on top of TMF921.

TMF921 provides the generic runtime `Intent` resource model, operation pattern, and event pattern. It does not prescribe the complete mandatory attribute profile required by every implementation.

The primary profile in this paper is the runtime `Intent` admission profile. This is the profile that must be satisfied before an Intent enters runtime processing.

Draft is treated only as a small pre-admission authoring context. Draft does not replace the runtime admission profile.

The key proposals are:

- define the minimum mandatory attributes for runtime `Intent` admission
- define the minimum mandatory attributes for a persisted Intent response after admission is accepted
- define the minimum attributes for `Intent` Draft creation
- define the minimum response attributes for `Intent` Draft creation
- keep the minimum mandatory profile separate from optional intent-management-entity governed enrichment fields

This proposal defines a candidate intent management entity profile rule. It does not claim that TMF921 universally mandates the same fields for every implementation.

## Proposal flow diagram:

![IntentSpecification mandatory profile proposal](intent_profile_decision.svg)

## Context:

An `IntentSpecification` defines the reusable contract. A runtime `Intent` is a concrete request made against that contract, either by explicit reference to an `IntentSpecification` or by an expression IRI that can be resolved to one active specification.

The admission request must contain enough machine-readable information to resolve and validate the runtime request. The persisted Intent must contain enough information to trace the request, audit the decision, project lifecycle state, and support later version or update handling.

Draft is a pre-admission authoring convenience. A Draft Intent may be incomplete because it is not admitted, not validated for runtime processing, and not sent downstream.

The intent management entity must be able to answer questions such as:

- What did the requester ask for?
- Which expression contract does the runtime expression follow?
- Which active `IntentSpecification` governed admission and validation?
- What lifecycle state was projected externally?
- What version of the runtime `Intent` is currently represented?
- Can the request be traced back to a human-readable business statement?
- Can downstream consumers interpret the request without re-resolving ambiguous context?

## Decision drivers:

| **Driver** | **Need** |
| --- | --- |
| Runtime admission safety | Ensure admission requests contain enough machine-readable content to validate the runtime intent. |
| Specification resolution | Support explicit `intentSpecification.id` where supplied, or unambiguous resolution by `expression.iri` where omitted. |
| Traceability | Persist the resolved `intentSpecification.id` and lifecycle metadata after admission. |
| Human readability | Strongly encourage `humanExpression` so operators and auditors can quickly understand the business request. |
| Lifecycle projection | Ensure persisted intents expose lifecycle state, status reason, and status change time. |
| Version governance | Ensure persisted intents expose the projected runtime version after admission is accepted. |
| TMF alignment | Stay aligned to the TMF921 resource model while applying a stricter implementation profile where needed. |

## Proposal:

### TMF-aligned, not TMF-minimal:

The intent management entity remains TMF-aligned by using the TMF921 runtime `Intent` resource model and operation pattern.

However, the intent management entity does not treat all optional-looking fields as operationally optional. A runtime intent must be complete enough to be admitted, validated, traced, and lifecycle-projected.

The rule is:

> TMF-aligned does not mean TMF-minimal.

### Runtime Intent admission profile:

The runtime admission profile is the main profile in this paper.

Admission is the point where the intent management entity accepts the Intent into runtime processing. At this point, the request must be complete enough to resolve the active `IntentSpecification` and validate the submitted expression.

The minimum admission request must include:

- `name`
- `expression`
- `expression.@type`
- `expression.iri`
- `expression.expressionValue`
- `@type`
- `@baseType`

The admission request is **strongly** encouraged to include:

- `humanExpression`
- `intentSpecification.id`

`humanExpression` is strongly recommended because it improves human traceability, auditability, triage, and business-level interpretation. It is not mandatory because the authoritative validation input is the structured expression.

`intentSpecification.id` is strongly recommended because it removes resolution ambiguity, improves traceability, and allows faster interpretation by operators and downstream systems. It is not mandatory because the intent management entity can resolve the applicable active `IntentSpecification` using `expression.iri` when there is exactly one active match.

### Minimum attributes for Intent Draft creation:

Draft is a pre-admission authoring convenience.

A draft can be created just by setting `submit: false`.

Draft is not the primary runtime profile. Draft is only a design time authoring profile used before admission.

Minimum Draft creation request attributes:

| **Attribute** | **Requirement** | **Reason** |
| --- | --- | --- |
| `name` | Mandatory | Gives the Draft a human-identifiable label. |
| `submit` | Mandatory with value `false` | Explicitly requests Draft authoring rather than admission. |
| `@type` | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | TMF base type alignment. |

**Strongly** recommended for Draft creation:

| **Attribute** | **Reason** |
| --- | --- |
| `humanExpression` | Helps reviewers and operators understand the intended request before the structured expression is complete. |

Draft creation does not require:

- `expression`
- `expression.iri`
- `expression.expressionValue`
- `intentSpecification.id`

Minimal Draft creation request payload:

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "submit": false,
  "@type": "Intent",
  "@baseType": "Entity"
}
```

Recommended Draft creation request payload with `humanExpression`:

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms.",
  "submit": false,
  "@type": "Intent",
  "@baseType": "Entity"
}
```

When a Draft is later moved into admission using `submit: true`, it must satisfy the normal runtime Intent admission profile defined in this paper.

### Minimum response attributes for Intent Draft creation:

A persisted Draft response should include enough information to identify, retrieve, edit, and understand the Draft state.

Draft Intents are not assigned a permanent runtime `version`. A permanent runtime `version` is assigned only after admission is accepted.

Minimum Draft creation response attributes:

| **Attribute** | **Requirement** | **Reason** |
| --- | --- | --- |
| `id` | Mandatory | Stable persisted Draft/Intent identity. |
| `href` | Mandatory | Canonical resource URL. |
| `name` | Mandatory | Human-readable Draft/Intent name. |
| `submit` | Mandatory with value `false` where exposed | Confirms the Draft has not been requested for admission. |
| `lifecycleStatus` | Mandatory with value `Draft` | Entity-assigned Draft state. |
| `statusReason` | Mandatory | Human-readable reason for Draft state. |
| `statusChangeDate` | Mandatory | Timestamp of Draft state assignment/update. |
| `@type` | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | TMF base type alignment. |

Minimum Draft creation response payload:

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "submit": false,
  "lifecycleStatus": "Draft",
  "statusReason": "Intent saved as draft and not submitted for admission.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "@type": "Intent",
  "@baseType": "Entity"
}
```

Recommended Draft creation response payload with `humanExpression` when supplied:

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms.",
  "submit": false,
  "lifecycleStatus": "Draft",
  "statusReason": "Intent saved as draft and not submitted for admission.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### IntentSpecification resolution rule:

`expression.iri` is mandatory for admission.

`intentSpecification.id` is optional in the admission request.

If `intentSpecification.id` is supplied:

- it is authoritative
- the referenced `IntentSpecification` must exist
- the referenced `IntentSpecification` must be active
- the runtime `expression.iri` must be consistent with the specification's `expressionSpecification.iri`

If `intentSpecification.id` is omitted:

- the intent management entity resolves the applicable active `IntentSpecification` using `expression.iri`
- if exactly one active `IntentSpecification` matches, the request may be admitted
- if zero active specifications match, the request must be rejected
- if multiple active specifications match, the request must be rejected and the requester must supply `intentSpecification.id`

After successful admission, `intentSpecification.id` becomes mandatory on the persisted `Intent` representation because the intent management entity must record which active specification governed validation and admission.

### Persisted response profile after admission:

A persisted `Intent` response after admission is accepted must include:

- `id`
- `href`
- `name`
- `version`
- `lifecycleStatus`
- `statusReason`
- `statusChangeDate`
- `intentSpecification.id`
- `expression`
- `expression.@type`
- `expression.iri`
- `expression.expressionValue`
- `@type`
- `@baseType`

The important distinction is:

> `intentSpecification.id` is optional in the admission request, but mandatory in the persisted response after admission is accepted.

### Optional intent-management-entity governed enrichment fields:

Optional enrichment fields are useful, but they are not part of the generic minimum mandatory profile.

| **Field** | **Proposed classification** | **Reason** |
| --- | --- | --- |
| `humanExpression` | **Strongly recommended** | Improves human traceability, auditability, triage, and business-level interpretation. |
| `intentSpecification.id` in admission request | **Strongly recommended** | Removes ambiguity and speeds validation/interpretation where the requester knows the active specification. |
| `description` | Optional | Useful for extra human-readable context. |
| `validFor.startDateTime` | Optional | Useful when the runtime intent should be valid from a specific time. |
| `isBundle` | Optional | Useful where bundled intent behaviour is supported. |
| `priority` | Optional | Useful where priority is handled as policy or operational guidance. |
| `relatedParty` | Optional | Useful for requester, customer, or provider attribution. |
| `_links` | Optional | Useful for discoverable operation affordances. |

Optional enrichment fields may be required by a specific implementation, product, channel, policy, onboarding profile, or security posture.

However, they are not part of the generic minimum mandatory profile defined by this proposal.

### Lifecycle ownership guardrail:

External consumers must not supply `lifecycleStatus` in any external write request.

`lifecycleStatus` is assigned, transitioned, and projected by the intent management entity.

## Examples:

The examples use a hospital surgical-connectivity scenario only to make the profile concrete. Draft request/response payloads are shown in the Draft sections above. This section focuses on admission and the persisted response after admission.

### Minimal admission request:

This example supplies `intentSpecification.id`, which is strongly recommended but not mandatory when `expression.iri` resolves unambiguously.

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "iri": "https://example.com/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99
        },
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold"
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    }
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

### Minimal persisted response after admission:

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "version": "v1",
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Intent accepted for admission processing.",
  "statusChangeDate": "2026-04-18T12:10:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "iri": "https://example.com/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
        "targets": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99
        },
        "constraints": {
          "location": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          },
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold"
        },
        "preferences": {
          "preferredAccessTechnology": "5G"
        }
      }
    }
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

## Consequences:

### Positive consequences:

If accepted, this proposal gives the intent management entity:

- a stable minimum profile for runtime Intent admission
- a small Draft add-on for pre-admission authoring
- support for both explicit and IRI-based specification resolution
- stronger traceability after admission
- clearer separation between minimum mandatory fields and optional enrichment

### Trade-offs:

If accepted, this proposal also means:

- requesters can submit a minimal machine-readable intent without `humanExpression` or `intentSpecification.id`
- the intent management entity must handle unambiguous resolution by `expression.iri`
- persisted responses must include resolved specification identity after admission
- operators get better traceability when requesters provide strongly recommended fields, but cannot rely on those fields always being present in the admission request

These trade-offs are acceptable because admission requests should remain interoperable while persisted resources must be deterministic and traceable.

## Alternatives considered:

### Make `intentSpecification.id` mandatory in every admission request:

This was rejected.

It would make validation deterministic, but it would remove the useful runtime pattern where a requester submits a valid expression identified by `expression.iri` and lets the intent management entity resolve the active specification when the match is unambiguous.

### Make `humanExpression` mandatory:

This was rejected.

`humanExpression` is valuable for traceability and human interpretation, but it is not machine-authoritative. Making it mandatory would make the API harder to use without improving machine validation.

### Allow admission request without `expression.iri`:

This was rejected.

`expression.iri` is the runtime discriminator for the semantic/expression contract. Without it, the intent management entity cannot safely resolve the applicable active specification or validate the expression.

## Proposal outcome:

This proposal recommends adopting a runtime `Intent` mandatory profile baseline.

If accepted, the intent management entity will document and enforce:

- runtime Intent admission requires `name`, `expression`, `expression.@type`, `expression.iri`, `expression.expressionValue`, `@type`, and `@baseType`
- persisted Intent response after admission requires identity, lifecycle projection, resolved `intentSpecification.id`, expression, `@type`, and `@baseType`
- Draft creation requires only `name`, `submit: false`, `@type`, and `@baseType`
- Draft creation response requires identity, Draft lifecycle projection, `submit: false`, `@type`, and `@baseType`; it does not require a permanent runtime `version`
- `humanExpression` and `intentSpecification.id` are strongly recommended for admission, but not generically mandatory
- `intentSpecification.id` is optional in the admission request but mandatory in the persisted response after admission is accepted
- optional enrichment fields remain separate from the generic minimum mandatory profile
- `lifecycleStatus` must not be supplied in any external write request

## References:

| **Reference** | **URL** | **Relevance to this proposal** |
| --- | --- | --- |
| TMF921 Intent Management API v5.0.0 specification | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Defines the TMF921 Intent Management API and runtime `Intent` resource model. |
| TMF921 Intent Management API v5.0.0 OpenAPI / Swagger artefact | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the OpenAPI resource and event schemas used to validate the TMF-facing API shape. |
| TMF921 Intent Management API v5.0.0 conformance profile | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the TMF conformance context while leaving implementation-specific mandatory profile choices to the intent management entity. |
| TR292 TM Forum Intent Ontology (TIO) v3.6.0 | https://www.tmforum.org/resources/standard/tr292-intent-ontology-tio-v3-6-0/ | Provides the intent ontology reference model and model-federation context behind semantic/expression contract identifiers. |
| TR299 Intent Specification | https://www.tmforum.org/resources/standard/tr299-intent-specification/ | Provides the intent specification concept used to describe rules for well-formed intent and allowed intent content. |
| Intent architecture baseline repository | https://github.com/prageethw/im/tree/main/baseline/intent | Holds the intent architecture baseline and project-specific profile artefacts. |

## Follow-up work:

After this proposal is reviewed and baselined, update the affected architecture and specification artifacts surgically:

- document the runtime `Intent` mandatory profile
- clarify admission request minimum mandatory fields
- clarify strongly recommended `humanExpression` and `intentSpecification.id`
- clarify persisted response mandatory fields
- clarify `intentSpecification.id` resolution and persistence behaviour
- keep runtime version/lifecycle profile wording aligned with the existing `activeVersion` baseline
