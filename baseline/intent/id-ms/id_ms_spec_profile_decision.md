# IntentSpecification consumer profile proposal

| **Document status** | **Value** |
| --- | --- |
| Status | Proposed decision paper |
| Scope | Consumer-submitted IntentSpecification profile proposal |
| Primary focus | Minimum mandatory, strongly recommended, and optional values consumers provide for DRAFT creation and ACTIVE publication |
| Out of scope | Operation routing, activation mechanics, retire behaviour, hub subscriptions, runtime Intent admission, draftId provenance lookup, and runtime fulfilment behaviour |
| Source of truth if accepted | ID MS Specification and ID MS Design Brief |

## Table of contents:

- [1. Proposal summary](#1-proposal-summary)
- [2. Scope and terminology](#2-scope-and-terminology)
- [3. Consumer identity submission model](#3-consumer-identity-submission-model)
- [4. Base and extended attribute classification](#4-base-and-extended-attribute-classification)
- [5. Consumer-submitted DRAFT creation profile](#5-consumer-submitted-draft-creation-profile)
- [6. Consumer-submitted ACTIVE publication profile](#6-consumer-submitted-active-publication-profile)
- [7. Server-managed and prohibited consumer fields](#7-server-managed-and-prohibited-consumer-fields)
- [8. Field classification summary](#8-field-classification-summary)
- [9. Minimal DRAFT create example](#9-minimal-draft-create-example)
- [10. Strongly recommended DRAFT create example](#10-strongly-recommended-draft-create-example)
- [11. ACTIVE publication example](#11-active-publication-example)
- [12. Consequences if accepted](#12-consequences-if-accepted)
- [13. References](#13-references)
- [14. Follow-up work if accepted](#14-follow-up-work-if-accepted)

## 1. Proposal summary:

This document proposes the consumer-submitted profile for `IntentSpecification` resources in ID MS.

The purpose is deliberately narrow: define which values consumers should provide when creating a DRAFT candidate and which values must be present before the candidate can be published as an ACTIVE `IntentSpecification` contract.

This proposal also calls out which consumer-visible attributes are TMF-aligned base attributes and which are ID MS extended attributes.

This proposal does not define API routing, activation mechanics, retire behaviour, hub subscription behaviour, runtime Intent admission, or `draftId` provenance lookup. Those details belong in the ID MS Specification and ID MS Design Brief.

The proposal separates consumer-provided fields into three classes:

| **Class** | **Meaning** |
| --- | --- |
| Minimum mandatory | Consumer must provide this for the relevant submission stage. |
| Strongly recommended | Consumer should provide this for a usable, governed, and discoverable specification, but it is not part of the absolute minimum. |
| Optional | Consumer may provide this where relevant, but ID MS must not depend on it for the minimum profile. |

## 2. Scope and terminology:

This proposal uses these terms:

| **Term** | **Meaning** |
| --- | --- |
| DRAFT creation | Consumer submission that creates an editable `IntentSpecification` DRAFT candidate. |
| ACTIVE publication | Consumer submission that completes the candidate sufficiently for ID MS to publish it as an ACTIVE contract. |
| Consumer-submitted field | A field the external consumer may send in the request body. |
| Server-managed field | A field generated or controlled by ID MS and not supplied by the consumer. |

This proposal is about `IntentSpecification` consumer submissions, not runtime `Intent` admission requests.

## 3. Consumer identity submission model:

For `POST /intentSpecification`, consumers submit `specKey`; they do not submit `id`, `draftId`, or official `version`.

The proposed model is:

| **Identifier** | **Owner** | **Purpose** |
| --- | --- | --- |
| `specKey` | Consumer-submitted | Logical specification key used by the consumer to create or evolve a specification family. |
| `id` | Server-assigned by ID MS | Stable official `IntentSpecification` lineage key. Consumers must not provide it in `POST /intentSpecification`. |
| `draftId` | Server-assigned by ID MS | Mutable DRAFT candidate key. Consumers must not provide it in `POST /intentSpecification`. |
| `version` | Server-assigned by ID MS on ACTIVE publication | Official public contract version. Consumers must not provide an official version in DRAFT creation. |

When a consumer creates a DRAFT candidate:

- if the submitted `specKey` has an existing ACTIVE lineage, ID MS assigns the new DRAFT candidate to that existing server-generated `id`;
- if the submitted `specKey` has no ACTIVE lineage, ID MS creates a new server-generated `id`;
- if only RETIRED versions exist for the submitted `specKey`, ID MS creates a new `id` by default unless explicit governance allows lineage reuse.

ID MS assigns a new `draftId` for the mutable candidate. ID MS assigns the official public `version` only when the DRAFT candidate is published as ACTIVE.

This keeps the consumer-submitted create profile simple while preserving server control of official identity, draft candidate identity, and published version identity.

## 4. Base and extended attribute classification:

This proposal separates TMF-aligned base attributes from ID MS platform extended attributes. Extended attributes are allowed only where they add ID MS governance, authoring, classification, or provenance value. They must not leak runtime fulfilment, optimisation, assurance, or callback behaviour into the definition contract.

| **Attribute** | **Classification** | **Consumer-submitted?** | **Purpose** |
| --- | --- | --- | --- |
| `name` | TMF-aligned base attribute | Yes | Human-readable specification name. |
| `description` | TMF-aligned base attribute | Yes | Human-readable purpose and scope. |
| `isBundle` | TMF-aligned base attribute | Yes | Indicates whether the specification is a bundle. |
| `validFor` | TMF-aligned base attribute | Yes | Defines intended validity period. |
| `relatedParty` | TMF-aligned base attribute | Yes | Captures owner, provider, or governance party context. |
| `specCharacteristic` | TMF-aligned base attribute | Yes | Catalogue and governance view of supported characteristics. |
| `expressionSpecification` | TMF-aligned base attribute | Yes | Expression contract metadata, including language and IRI. |
| `targetEntitySchema` | TMF-aligned base attribute | Yes | Machine-readable expression validation contract reference. |
| `@type` | TMF polymorphic metadata | Yes | Resource type marker, normally `IntentSpecification`. |
| `@baseType` | TMF polymorphic metadata | Yes | Base type marker, normally `EntitySpecification`. |
| `@schemaLocation` | TMF polymorphic metadata | Yes, optional | Resource representation schema location where published. |
| `specKey` | ID MS extended attribute | Yes | Consumer-submitted logical specification key used to create or evolve a specification family. |
| `intentBehaviour` | ID MS extended attribute | Yes, optional | Classification metadata for catalogue visibility, governance visibility, and external consumer understanding. |
| `intentLayer` | ID MS extended attribute | Yes, optional | Classification metadata identifying whether the specification is business, service, or resource level. |
| `schemaHash` inside `targetEntitySchema` | ID MS extended attribute | Yes, optional | Schema integrity metadata where schema governance supports it. |
| `id` | Server-managed ID MS attribute | No | Server-assigned official `IntentSpecification` lineage key. |
| `draftId` | Server-managed ID MS attribute | No | Server-assigned mutable DRAFT candidate key and later provenance key. |
| `version` | Server-managed ID MS attribute | No for DRAFT create | Official public contract version assigned by ID MS on ACTIVE publication. |
| `href`, `_links`, timestamps, `lifecycleStatus` | Server-managed attributes | No for DRAFT create | Generated or controlled by ID MS. |

The extended attributes in this proposal are intentionally small:

- `specKey` supports consumer-driven specification authoring and version evolution without allowing consumers to control the official `id`.
- `intentBehaviour` and `intentLayer` support catalogue classification and external understanding only.
- `schemaHash` supports optional schema integrity governance where available.

No additional behaviour fields are proposed at ID MS level.

## 5. Consumer-submitted DRAFT creation profile:

A DRAFT creation request should be lightweight. It only needs enough information for ID MS to create, identify, and govern the editable candidate.

### 5.1 Minimum mandatory fields for DRAFT creation:

| **Field** | **Requirement** | **Reason** |
| --- | --- | --- |
| `specKey` | Minimum mandatory | Consumer-submitted logical key used to create or evolve a specification family. |
| `name` | Minimum mandatory | Provides a human-readable catalogue name. |
| `@type` | Minimum mandatory | Identifies the TMF polymorphic resource type. |
| `@baseType` | Minimum mandatory | Preserves TMF base type alignment. |

### 5.2 Strongly recommended fields for DRAFT creation:

| **Field** | **Classification** | **Reason** |
| --- | --- | --- |
| `description` | Strongly recommended | Explains the purpose of the specification. |
| `isBundle` | Strongly recommended | Clarifies whether the specification is a bundle. If omitted, ID MS may default it to `false` where that policy is adopted. |
| `validFor.startDateTime` | Strongly recommended | Provides intended validity timing for later publication. |
| `relatedParty` | Strongly recommended | Captures owner or provider context. |
| `expressionSpecification` | Strongly recommended | Allows early review of the semantic and expression contract. |
| `targetEntitySchema` | Strongly recommended | Allows early review of the runtime expression validation contract. |
| `specCharacteristic` | Strongly recommended | Allows early catalogue and governance review. |

### 5.3 Optional fields for DRAFT creation:

| **Field** | **Classification** | **Reason** |
| --- | --- | --- |
| `intentBehaviour` | Optional | Classification metadata for catalogue visibility, governance visibility, and external consumer understanding. Not used by ID MS for runtime decisioning, runtime validation, admission control, or behavioural enforcement. |
| `intentLayer` | Optional | Classification metadata that identifies whether the specification is business, service, or resource level. Not used by ID MS for runtime decisioning, runtime validation, admission control, or behavioural enforcement. |
| `validFor.endDateTime` | Optional | Useful when the specification has a planned end of validity. |
| `@schemaLocation` | Optional | Useful where a concrete resource representation schema is published. |
| `schemaHash` inside `targetEntitySchema` | Optional | Useful for schema integrity checking where schema governance supports it. |

DRAFT candidates do not expose or guarantee any official version identifier. Any version indicator during authoring is non-authoritative. Draft revision is represented by the entity tag and draft governance model defined in the ID MS Specification.

## 6. Consumer-submitted ACTIVE publication profile:

Before an `IntentSpecification` can be published as ACTIVE, the consumer-submitted candidate must contain a complete contract profile.

### 6.1 Minimum mandatory fields for ACTIVE publication:

| **Field** | **Requirement** | **Reason** |
| --- | --- | --- |
| `specKey` | Minimum mandatory | Confirms the governed definition key for the candidate. |
| `name` | Minimum mandatory | Provides the published catalogue name. |
| `isBundle` | Minimum mandatory | Required for consistent resource interpretation. |
| `validFor.startDateTime` | Minimum mandatory | Defines when the published contract becomes valid. |
| `expressionSpecification` | Minimum mandatory | Defines the expression contract metadata. |
| `expressionSpecification.iri` | Minimum mandatory | Identifies the semantic and expression contract. |
| `expressionSpecification.expressionLanguage` | Minimum mandatory | Identifies the expression representation and interpretation model. |
| `targetEntitySchema` | Minimum mandatory | Provides the machine-readable runtime expression validation contract. |
| `targetEntitySchema.@schemaLocation` | Minimum mandatory | Identifies the governed expression schema artefact. |
| `specCharacteristic` | Minimum mandatory | Provides the catalogue and governance view of important supported characteristics. |
| `@type` | Minimum mandatory | Identifies the TMF polymorphic resource type. |
| `@baseType` | Minimum mandatory | Preserves TMF base type alignment. |

### 6.2 Strongly recommended fields for ACTIVE publication:

| **Field** | **Classification** | **Reason** |
| --- | --- | --- |
| `description` | Strongly recommended | Makes the published specification easier to understand and govern. |
| `relatedParty` | Strongly recommended | Captures provider, owner, or governance party context. |
| `intentBehaviour` | Strongly recommended | Supports catalogue classification and consumer understanding. |
| `intentLayer` | Strongly recommended | Clarifies whether the specification is business, service, or resource level. |
| `schemaHash` inside `targetEntitySchema` | Strongly recommended | Supports schema integrity checking where schema governance supports it. |
| `@schemaLocation` | Strongly recommended | Points to the resource representation schema where published. |

### 6.3 Optional fields for ACTIVE publication:

| **Field** | **Classification** | **Reason** |
| --- | --- | --- |
| `validFor.endDateTime` | Optional | Useful where expiry or retirement planning is known. |
| `attachment` | Optional | Useful for supporting documents where the implementation permits it. |
| `constraint` | Optional | Useful for additional TMF constraint metadata where required. |
| `entitySpecRelationship` | Optional | Useful for relationships to other entity specifications where required. |
| `intentSpecRelationship` | Optional | Useful for relationships to other intent specifications where required. |

## 7. Server-managed and prohibited consumer fields:

Consumers must not provide server-managed fields in DRAFT create requests.

| **Field** | **Rule** |
| --- | --- |
| `id` | Server-assigned official lineage key. Consumer must not provide it on create. ID MS resolves or creates it from the submitted `specKey` according to platform governance. |
| `href` | Server-generated canonical URL. Consumer must not provide it on create. |
| `draftId` | Server-assigned DRAFT candidate identifier. Consumer must not provide it on create. |
| `version` | Official public version is assigned by ID MS only on ACTIVE publication. Consumer must not provide an official version in DRAFT create. Any version indicator during authoring is non-authoritative. |
| `lifecycleStatus` | Server-managed lifecycle state. Consumer must not set it on create. |
| `creationDate` | Server-managed timestamp. |
| `lastUpdate` | Server-managed timestamp. |
| `statusChangeDate` | Server-managed timestamp. |
| `_links` | Server-generated navigation and operation affordances. |
| `ETag` | Response header, not a request body field. |
| `Location` | Response header, not a request body field. |

## 8. Field classification summary:

| **Field** | **DRAFT create** | **ACTIVE publication** |
| --- | --- | --- |
| `specKey` | Minimum mandatory | Minimum mandatory |
| `name` | Minimum mandatory | Minimum mandatory |
| `@type` | Minimum mandatory | Minimum mandatory |
| `@baseType` | Minimum mandatory | Minimum mandatory |
| `description` | Strongly recommended | Strongly recommended |
| `isBundle` | Strongly recommended | Minimum mandatory |
| `validFor.startDateTime` | Strongly recommended | Minimum mandatory |
| `relatedParty` | Strongly recommended | Strongly recommended |
| `expressionSpecification` | Strongly recommended | Minimum mandatory |
| `expressionSpecification.iri` | Strongly recommended | Minimum mandatory |
| `expressionSpecification.expressionLanguage` | Strongly recommended | Minimum mandatory |
| `targetEntitySchema` | Strongly recommended | Minimum mandatory |
| `targetEntitySchema.@schemaLocation` | Strongly recommended | Minimum mandatory |
| `specCharacteristic` | Strongly recommended | Minimum mandatory |
| `intentBehaviour` | Optional | Strongly recommended |
| `intentLayer` | Optional | Strongly recommended |
| `schemaHash` inside `targetEntitySchema` | Optional | Strongly recommended |
| `validFor.endDateTime` | Optional | Optional |
| `@schemaLocation` | Optional | Strongly recommended |

## 9. Minimal DRAFT create example:

```json
{
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

## 10. Strongly recommended DRAFT create example:

```json
{
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS performs syntax and structure validation only; II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "Provider",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice.expression.schema.json",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  },
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "id": "context",
      "name": "context",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

## 11. ACTIVE publication example:

```json
{
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents. This specification defines the allowed request shape for surgical connectivity intents. ID MS performs syntax and structure validation only; II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "Provider",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
  "intentBehaviour": {
    "category": "REALTIME",
    "constraintMode": "STRICT",
    "objectiveType": "SLA",
    "fulfilmentMode": "CONTINUOUS"
  },
  "intentLayer": "SERVICE",
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.20.expression.schema.json",
    "schemaVersion": "1.20",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  },
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "id": "context",
      "name": "context",
      "description": "Top-level semantic context supported by this IntentSpecification.",
      "valueType": "object",
      "configurable": true,
      "minCardinality": 1,
      "maxCardinality": 1
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/ispec-hss-001.schema.json"
}
```

## 12. Consequences if accepted:

Positive consequences:

- consumers know the minimum fields needed to create a DRAFT candidate
- consumers know the stronger profile needed before ACTIVE publication
- DRAFT authoring remains lightweight
- ACTIVE publication remains contract-safe
- server-managed fields are clearly separated from consumer-submitted fields
- optional classification metadata stays out of runtime enforcement

Trade-offs:

- the ACTIVE publication profile is stricter than the minimum generic TMF shape
- consumers may need to supply more complete metadata before publication
- the proposal requires lifecycle-aware validation in ID MS if accepted

## 13. References:

| **Reference** | **URL** | **Relevance** |
| --- | --- | --- |
| TMF921 Intent Management API v5.0.0 specification | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Defines the TMF Intent Management API and `IntentSpecification` resource model used as the base. |
| TMF921 Intent Management API v5.0.0 OpenAPI artefact | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the OpenAPI resource and event schemas used to validate TMF-facing shape. |
| TMF921 Intent Management API v5.0.0 conformance profile | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the TMF conformance context while allowing implementation-specific profile choices. |
| TR292 TM Forum Intent Ontology v3.6.0 | https://www.tmforum.org/resources/standard/tr292-intent-ontology-tio-v3-6-0/ | Provides intent ontology context behind semantic and expression contract identifiers. |
| Intent architecture baseline repository | https://github.com/prageethw/im/tree/main/baseline/intent | Holds the project baseline artifacts. |

## 14. Follow-up work if accepted:

If accepted, update or confirm the ID MS Specification and ID MS Design Brief so they:

- document the accepted consumer-submitted DRAFT and ACTIVE profiles
- enforce the accepted profile during DRAFT creation and ACTIVE publication
- keep server-managed fields separate from consumer-submitted fields
- keep operation routes and examples in specification artifacts rather than this proposal paper
- keep runtime Intent admission rules out of this proposal paper
