# IntentSpecification mandatory profile proposal

| **Document status** | **Value** |
| --- | --- |
| Status | Proposed decision paper |
| Scope | IntentSpecification minimum mandatory profile proposal |
| Primary focus | DRAFT profile, ACTIVE profile, persisted identity, expressionSpecification, targetEntitySchema, specCharacteristic, and optional enrichment separation |
| Out of scope | Operation routing, activation mechanics, retire behaviour, hub subscriptions, runtime Intent admission, and draftId provenance lookup |
| Source of truth if accepted | ID MS Specification and ID MS Design Brief |

## Table of contents:

- [1. Proposal summary](#1-proposal-summary)
- [2. Context](#2-context)
- [3. Proposal drivers](#3-proposal-drivers)
- [4. Proposed minimum mandatory profile by lifecycle state](#4-proposed-minimum-mandatory-profile-by-lifecycle-state)
- [5. Proposed DRAFT profile](#5-proposed-draft-profile)
- [6. Proposed ACTIVE profile](#6-proposed-active-profile)
- [7. Proposed expressionSpecification rule](#7-proposed-expressionspecification-rule)
- [8. Proposed targetEntitySchema rule](#8-proposed-targetentityschema-rule)
- [9. Proposed specCharacteristic rule](#9-proposed-speccharacteristic-rule)
- [10. Optional enrichment fields](#10-optional-enrichment-fields)
- [11. Lifecycle-aware validation proposal](#11-lifecycle-aware-validation-proposal)
- [12. Examples](#12-examples)
- [13. Consequences if accepted](#13-consequences-if-accepted)
- [14. Alternatives considered](#14-alternatives-considered)
- [15. Proposal outcome](#15-proposal-outcome)
- [16. References](#16-references)
- [17. Follow-up work if accepted](#17-follow-up-work-if-accepted)

## 1. Proposal summary:

This document proposes a minimum mandatory attribute profile for `IntentSpecification` resources used by the intent management entity.

TMF921 provides the generic `IntentSpecification` resource model, operation pattern, and event pattern. It does not prescribe every implementation-specific mandatory field needed for a runtime-ready intent platform. This proposal therefore recommends a stricter implementation profile so that an `IntentSpecification` can be safely governed, activated, discovered, and used by downstream components as a runtime expression contract.

The proposal is intentionally limited to the mandatory profile question. It is not the source of truth for operation routes, draft candidate routing, activation mechanics, retire behaviour, hub subscription behaviour, runtime Intent admission, or `draftId` provenance lookup. Those details belong in the ID MS Specification and ID MS Design Brief.

The key proposal is:

- A persisted DRAFT `IntentSpecification` should contain enough information to be identified, managed, and governed.
- An ACTIVE `IntentSpecification` should contain enough information to act as a complete published runtime contract.
- Optional enrichment fields should remain separate from the minimum mandatory profile.
- Operation-level behaviour should be specified elsewhere, not repeated in this proposal paper.

## 2. Context:

For the intent management entity, an `IntentSpecification` is more than a descriptive catalogue record. Once active, it becomes a published runtime contract that downstream components use to validate and interpret submitted runtime intent expressions.

If the active resource is too sparse, downstream behaviour becomes ambiguous. The platform must be able to determine:

- which specification defines the submitted runtime expression
- which semantic and expression contract applies
- which schema validates the runtime expression body
- whether the specification is active and valid
- whether consumers can understand the supported characteristics

This proposal therefore recommends a lifecycle-aware mandatory profile that is stricter than a minimal interpretation of the generic TMF resource shape.

## 3. Proposal drivers:

| **Driver** | **Need** |
| --- | --- |
| TMF alignment | Use the TMF921 `IntentSpecification` resource model without inventing an incompatible shape. |
| Runtime safety | Prevent activation of incomplete specifications that cannot support runtime expression validation. |
| Governance | Ensure persisted specifications have stable identity, lifecycle status, and version identity where applicable. |
| Discoverability | Ensure active specifications can be understood by portals, operators, and integration consumers. |
| Validation | Ensure active specifications identify their machine-readable validation contract. |
| Semantic clarity | Ensure active specifications identify their semantic and expression contract. |
| Evolvability | Allow incomplete DRAFT resources while preventing incomplete ACTIVE contracts. |

## 4. Proposed minimum mandatory profile by lifecycle state:

The proposal separates the DRAFT and ACTIVE mandatory profiles.

A DRAFT specification may be incomplete because it is still being authored. It still needs enough information to be managed safely.

An ACTIVE specification is a published runtime contract. It should be complete enough for discovery, validation, governance, and runtime interpretation.

| **Field** | **DRAFT** | **ACTIVE** | **Reason** |
| --- | --- | --- | --- |
| `id` | Mandatory on persisted resource | Mandatory | Stable server-managed resource identity. |
| `href` | Mandatory on persisted resource | Mandatory | Canonical resource URL for TMF-style navigation and references. |
| `name` | Mandatory | Mandatory | Human-readable catalogue name. |
| `version` | Not exposed as official public version while DRAFT | Mandatory | Official activated contract version. |
| `lifecycleStatus` | Server-managed on create; mandatory on persisted resource | Mandatory | Identifies whether the specification is DRAFT, ACTIVE, or RETIRED. |
| `isBundle` | Optional on request; mandatory on persisted resource | Mandatory | Clarifies whether the specification is a bundle; defaults to `false` when omitted. |
| `validFor.startDateTime` | Optional | Mandatory | Defines when the active contract becomes valid. |
| `expressionSpecification` | Optional | Mandatory | Defines expression contract metadata. |
| `expressionSpecification.iri` | Optional | Mandatory | Authoritative semantic and expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Optional | Mandatory | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Optional | Mandatory | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Optional | Mandatory | Catalogue and governance view of supported characteristics. |
| `@type` | Mandatory | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | Mandatory | TMF base type alignment. |

## 5. Proposed DRAFT profile:

A DRAFT `IntentSpecification` may be incomplete because it is still being authored, reviewed, or governed.

Proposed mandatory fields for a persisted DRAFT resource:

| **Field** | **Proposed requirement** | **Reason** |
| --- | --- | --- |
| `id` | Mandatory on persisted resource | Stable server-managed identity. |
| `href` | Mandatory on persisted resource | Canonical resource URL. |
| `name` | Mandatory | Human-readable catalogue name. |
| `lifecycleStatus` | Mandatory on persisted resource | Must indicate DRAFT state. |
| `isBundle` | Mandatory on persisted resource | Defaults to `false` when omitted on create. |
| `@type` | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | TMF base type alignment. |

DRAFT candidates do not expose or guarantee an official public version identifier. Draft revision is represented by the entity tag and draft governance model defined in the ID MS Specification.

Fields such as `expressionSpecification`, `targetEntitySchema`, and `specCharacteristic` may be added while the DRAFT is being authored. They become mandatory before the specification can become ACTIVE.

## 6. Proposed ACTIVE profile:

An ACTIVE `IntentSpecification` is a published runtime contract. It should be complete enough for discovery, governance, validation, and downstream interpretation.

Proposed mandatory fields for an ACTIVE resource:

| **Field** | **Proposed requirement** | **Reason** |
| --- | --- | --- |
| `id` | Mandatory | Stable official specification identity. |
| `href` | Mandatory | Canonical resource URL. |
| `name` | Mandatory | Human-readable catalogue name. |
| `version` | Mandatory | Official activated contract version. |
| `lifecycleStatus` | Mandatory | Must indicate ACTIVE state. |
| `isBundle` | Mandatory | Required for consistent interpretation. |
| `validFor.startDateTime` | Mandatory | Defines when the active contract becomes valid. |
| `expressionSpecification` | Mandatory | Defines expression contract metadata. |
| `expressionSpecification.iri` | Mandatory | Authoritative semantic and expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Mandatory | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Mandatory | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Mandatory | Catalogue and governance view of important supported characteristics. |
| `@type` | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | TMF base type alignment. |

Optional TMF fields may still be used where relevant, including `description`, `lastUpdate`, `validFor.endDateTime`, `relatedParty`, relationships, attachments, constraints, and `@schemaLocation`.

## 7. Proposed expressionSpecification rule:

For an ACTIVE `IntentSpecification`, `expressionSpecification` should be mandatory.

Within `expressionSpecification`, the proposal makes these fields mandatory:

- `iri`
- `expressionLanguage`

The `iri` identifies the semantic and expression contract. The `expressionLanguage` identifies how the expression is represented and interpreted, such as JSON-LD.

If `expressionSpecification.iri` is required for active runtime behaviour, then the parent `expressionSpecification` object cannot be optional for ACTIVE resources.

## 8. Proposed targetEntitySchema rule:

For an ACTIVE `IntentSpecification`, `targetEntitySchema` should be mandatory.

`targetEntitySchema` is the authoritative machine-readable schema reference for validating runtime expression values. For the intent management entity, it should define the allowed shape of the submitted expression value, including the governed context structure used by the active specification.

`targetEntitySchema` should not be replaced by `specCharacteristic`. The two fields serve different purposes.

## 9. Proposed specCharacteristic rule:

For an ACTIVE `IntentSpecification`, `specCharacteristic` should be mandatory.

`specCharacteristic` provides the catalogue-facing and governance-facing view of important supported characteristics. It helps users, experience-layer applications, governance processes, and integration consumers understand what the specification supports.

However, `specCharacteristic` is not the authoritative deep validation schema for the runtime expression body. That role belongs to `targetEntitySchema`.

The proposed pattern is:

- `specCharacteristic` gives discoverable high-level characteristics
- `targetEntitySchema` gives detailed machine validation
- `expressionSpecification.iri` identifies the semantic and expression contract

## 10. Optional enrichment fields:

Some fields are useful but should not be part of the generic minimum mandatory profile.

| **Field** | **Proposed classification** | **Reason** |
| --- | --- | --- |
| `specKey` | Optional or implementation-governed | Useful for version grouping, but not part of the generic minimum mandatory profile proposed here. |
| `description` | Optional | Useful for catalogue readability and governance context. |
| `relatedParty` | Optional or implementation-governed | Useful for ownership and provider attribution. |
| `intentBehaviour` | Optional classification metadata | Useful for catalogue visibility, governance visibility, and external consumer understanding. It is not used by ID MS for runtime decisioning, runtime validation, admission control, or behavioural enforcement. |
| `intentLayer` | Optional classification metadata | Useful for identifying whether the specification is business, service, or resource level. It is not used by ID MS for runtime decisioning, runtime validation, admission control, or behavioural enforcement. |
| `@schemaLocation` | Optional or implementation-governed | Useful where a concrete schema for the resource representation is published. |
| `validFor.endDateTime` | Optional | Useful where the specification has a planned expiry. |
| `schemaVersion` or `schemaHash` inside `targetEntitySchema` | Optional or implementation-governed | Useful for stronger schema governance and integrity checking. |
| `_links` | Optional or implementation-governed | Useful for discoverable operation affordances. |

This proposal intentionally does not define the complete controlled value set for every optional enrichment field. The ID MS Specification is the source of truth for concrete field constraints if those fields are adopted.

## 11. Lifecycle-aware validation proposal:

This proposal recommends lifecycle-aware validation.

Create and update operations may allow incomplete DRAFT resources. Activation to ACTIVE should validate the full ACTIVE mandatory profile.

If a client attempts to activate a specification that does not satisfy the ACTIVE profile, the intent management entity should reject the request.

The preferred response is:

```text
422 Unprocessable Entity
```

This means the request is syntactically valid, but the resource cannot transition to the requested lifecycle state because it violates the proposed `IntentSpecification` profile.

## 12. Examples:

The examples below are intentionally minimal. They illustrate the proposed mandatory profile only. Operation-specific request and response examples belong in the ID MS Specification.

### 12.1 Minimal DRAFT representation:

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

### 12.2 Minimal ACTIVE representation:

```json
{
  "id": "ispec-hss-001",
  "href": "/intentManagement/v5/intentSpecification/ispec-hss-001",
  "name": "Hospital Surgical Slice Intent Specification",
  "version": "1.20",
  "lifecycleStatus": "ACTIVE",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.20.expression.schema.json"
  },
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "name": "context",
      "valueType": "object"
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

## 13. Consequences if accepted:

Positive consequences:

- clearer minimum DRAFT and ACTIVE profiles
- safer activation rules
- better runtime validation readiness
- cleaner separation between catalogue characteristics and validation schema
- stronger semantic and expression contract clarity
- less risk of activating incomplete specification contracts

Trade-offs:

- the implementation profile is stricter than a minimal TMF interpretation
- activation validation becomes more important
- clients must supply more information before a specification can become ACTIVE
- DRAFT and ACTIVE validation rules become intentionally different

## 14. Alternatives considered:

### 14.1 Treat generic TMF optionality as sufficient:

This was not recommended because it could allow ACTIVE specifications that are not usable for runtime validation or interpretation.

### 14.2 Make every useful field mandatory at create time:

This was not recommended because it would make DRAFT authoring too rigid. The platform should allow incomplete drafts while enforcing completeness before activation.

### 14.3 Make `expressionSpecification.iri` mandatory but keep `expressionSpecification` optional:

This was not recommended because the child field cannot be required while the parent object remains optional for ACTIVE resources.

## 15. Proposal outcome:

This proposal recommends adopting a lifecycle-aware `IntentSpecification` mandatory profile:

- DRAFT requires enough information to be identified, managed, and governed.
- ACTIVE requires the full runtime-contract profile.
- `expressionSpecification`, `expressionSpecification.iri`, and `expressionSpecification.expressionLanguage` are mandatory for ACTIVE resources.
- `targetEntitySchema` is mandatory for ACTIVE resources.
- `specCharacteristic` is mandatory for ACTIVE resources.
- Optional enrichment fields remain outside the generic minimum mandatory profile.

If accepted, the ID MS Specification and ID MS Design Brief should remain the source of truth for concrete operation behaviour and detailed constraints.

## 16. References:

| **Reference** | **URL** | **Relevance** |
| --- | --- | --- |
| TMF921 Intent Management API v5.0.0 specification | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Defines the TMF Intent Management API and `IntentSpecification` resource model used as the base. |
| TMF921 Intent Management API v5.0.0 OpenAPI artefact | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the OpenAPI resource and event schemas used to validate TMF-facing shape. |
| TMF921 Intent Management API v5.0.0 conformance profile | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the TMF conformance context while allowing implementation-specific profile choices. |
| TR292 TM Forum Intent Ontology v3.6.0 | https://www.tmforum.org/resources/standard/tr292-intent-ontology-tio-v3-6-0/ | Provides intent ontology context behind semantic and expression contract identifiers. |
| Intent architecture baseline repository | https://github.com/prageethw/im/tree/main/baseline/intent | Holds the project baseline artifacts. |

## 17. Follow-up work if accepted:

If accepted, update or confirm the ID MS Specification and ID MS Design Brief so they:

- document the accepted mandatory profile
- enforce lifecycle-aware validation
- keep DRAFT and ACTIVE validation distinct
- keep operation routes and examples in specification artifacts rather than this proposal paper
- keep runtime Intent admission rules out of this proposal paper except as references where needed
