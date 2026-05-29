# IntentSpecification profile decision

| **Document status** | **Value** |
| --- | --- |
| Status | Proposed decision paper |
| Scope | IntentSpecification minimum data requirements |
| Primary focus | `specKey`, `draftId`, DRAFT candidate creation, activation, official version assignment, ACTIVE/RETIRED immutability |
| Out of scope | Runtime Intent admission rules, full runtime lifecycle design, implementation routing details |
| Source of truth after commit | GitHub `baseline/intent/id-ms/id_ms_spec_profile_decision.md` |

## Table of contents:

- [1. Decision summary](#1-decision-summary)
- [2. Proposal flow diagram](#2-proposal-flow-diagram)
- [3. Context](#3-context)
- [4. Decision drivers](#4-decision-drivers)
- [5. Proposal](#5-proposal)
  - [5.1 TMF-aligned, not TMF-minimal](#51-tmf-aligned-not-tmf-minimal)
  - [5.2 Minimum mandatory profile by lifecycle state](#52-minimum-mandatory-profile-by-lifecycle-state)
  - [5.3 Recommended but not minimum mandatory fields](#53-recommended-but-not-minimum-mandatory-fields)
  - [5.4 Persisted resource identity](#54-persisted-resource-identity)
  - [5.5 DRAFT profile](#55-draft-profile)
  - [5.6 ACTIVE profile](#56-active-profile)
  - [5.7 expressionSpecification rule](#57-expressionspecification-rule)
  - [5.8 targetEntitySchema rule](#58-targetentityschema-rule)
  - [5.9 specCharacteristic rule](#59-speccharacteristic-rule)
  - [5.10 Lifecycle-aware validation](#510-lifecycle-aware-validation)
- [6. Examples](#6-examples)
  - [6.1 Minimal DRAFT create request and response](#61-minimal-draft-create-request-and-response)
  - [6.2 Minimal activation request and ACTIVE response](#62-minimal-activation-request-and-active-response)
  - [6.3 Fuller illustrative example with optional fields](#63-fuller-illustrative-example-with-optional-fields)
- [7. Consequences](#7-consequences)
  - [7.1 Positive consequences](#71-positive-consequences)
  - [7.2 Trade-offs](#72-trade-offs)
- [8. Alternatives considered](#8-alternatives-considered)
  - [8.1 Treat TMF optional fields as intent management entity optional](#81-treat-tmf-optional-fields-as-intent-management-entity-optional)
  - [8.2 Make every useful field mandatory at create time](#82-make-every-useful-field-mandatory-at-create-time)
  - [8.3 Make expressionSpecification.iri mandatory but not expressionSpecification](#83-make-expressionspecificationiri-mandatory-but-not-expressionspecification)
  - [8.4 Make runtime intentSpecification.id mandatory everywhere](#84-make-runtime-intentspecificationid-mandatory-everywhere)
- [9. Proposal outcome](#9-proposal-outcome)
- [10. References](#10-references)
- [11. Follow-up work](#11-follow-up-work)

## 1. Decision summary:

This proposal defines the minimum mandatory attribute profile for `IntentSpecification` resources on the intent management entity, layered on top of TMF921.

TMF921 provides the generic `IntentSpecification` resource model, operation pattern, and event pattern. It does not prescribe the complete mandatory attribute profile required by every implementation.

The intent management entity therefore defines a stricter profile so that `IntentSpecification` resources are usable for catalogue governance, lifecycle management, runtime expression validation, and runtime intent resolution.

The key proposals are:

- define the minimum mandatory attributes for a persisted `DRAFT` `IntentSpecification`
- define the minimum mandatory attributes for an `ACTIVE` `IntentSpecification`
- allow intent-management-entity-specific optional fields for richer version governance, catalogue discovery, and operational controls
- keep the minimum mandatory profile separate from optional intent-management-entity governed extensions

This proposal defines a candidate intent management entity profile rule. It does not claim that TMF921 universally mandates the same fields for every implementation.

## 2. Proposal flow diagram:

![IntentSpecification mandatory profile proposal](id_ms_spec_profile_decision.svg)

## 3. Context:

TMF921 intentionally leaves implementation flexibility in the `IntentSpecification` model. That is useful for broad interoperability, because different organisations may need different levels of catalogue detail, lifecycle governance, schema discipline, and runtime coupling.

However, for the intent management entity, an `IntentSpecification` is not only a descriptive catalogue record. Once active, it becomes a published runtime contract used by downstream consumers to understand, validate, and resolve submitted runtime intents. If too many fields are treated as optional, downstream runtime behaviour becomes ambiguous.

The intent management entity must be able to answer questions such as:

- Which specification defines the submitted runtime expression?
- Which semantic contract does the expression follow?
- Which schema validates the runtime expression body?
- Is the specification active and within its validity period?
- Can runtime admission safely validate the supplied `intentSpecification.id` and `expression.iri` against each other?
- Can event subscribers interpret specification events without an authoritative resource identity?

Therefore, the intent management entity needs a mandatory profile that is stricter than the minimum generic TMF shape.

## 4. Decision drivers:

The proposal is driven by the following architecture needs:

| **Driver** | **Need** |
| --- | --- |
| TMF alignment | Use the TMF921 resource model and API/event patterns without inventing an incompatible resource shape. |
| Runtime safety | Prevent activation of specifications that cannot be used for runtime validation, semantic contract consistency checks, or downstream resolution. |
| Governance | Ensure every persisted specification has stable identity, lifecycle status, and version identity. |
| Discoverability | Ensure active specifications can be discovered and understood by users, portals, and integration consumers. |
| Validation | Ensure active specifications have a machine-readable validation contract. |
| Semantic clarity | Ensure active specifications identify the semantic/expression contract they support. |
| Evolvability | Allow incomplete drafts while preventing incomplete active contracts. |

## 5. Proposal:

### 5.1 TMF-aligned, not TMF-minimal:

The intent management entity remains TMF-aligned by using the TMF921 `IntentSpecification` resource model, including TMF-style identity, lifecycle status, specification characteristics, expression specification, target entity schema, related parties, relationships, and events.

However, the intent management entity does not adopt a TMF-minimal interpretation where most fields are treated as operationally optional. Instead, the intent management entity applies a mandatory profile appropriate for its runtime architecture.

The rule is:

> TMF-aligned does not mean TMF-minimal.

### 5.2 Minimum mandatory profile by lifecycle state:

This proposal defines different profiles for the create request, persisted `DRAFT` candidate, and official `ACTIVE` contract.

A create request creates a mutable `DRAFT` candidate. It must have enough information for ID MS to resolve identity and create the candidate, but it must not contain server-assigned, lifecycle, or official-version fields.

A persisted `DRAFT` candidate must have enough information to be identified, edited, governed, and safely activated later.

An `ACTIVE` specification must have enough information to act as a published runtime contract for discovery, validation, governance, and runtime resolution.

| **Field** | **Create request** | **Persisted DRAFT candidate** | **ACTIVE official resource** | **Reason** |
| --- | --- | --- | --- | --- |
| `specKey` | Mandatory | Mandatory | Mandatory | Stable logical key used by ID MS to resolve the server-assigned `IntentSpecification.id`. |
| `id` | Not accepted | Mandatory, server-resolved | Mandatory | Stable official lineage identity resolved from `specKey`. |
| `draftId` | Not accepted | Mandatory, server-assigned | Optional provenance | Selects the mutable DRAFT candidate. |
| `href` | Not accepted | Mandatory | Mandatory | Canonical resource URL. DRAFT uses `/draft/{draftId}`; official records use `/{id}`. |
| `name` | Mandatory | Mandatory | Mandatory | Human-readable catalogue name. |
| `version` | Not accepted | Not exposed | Mandatory | Official public version assigned only on activation. |
| `lifecycleStatus` | Not accepted | Mandatory, server-managed as `DRAFT` | Mandatory | Identifies whether the specification is DRAFT, ACTIVE, or RETIRED. |
| `isBundle` | Optional, defaults `false` | Mandatory | Mandatory | Clarifies whether the specification is a bundle. |
| `validFor.startDateTime` | Optional | Optional until activation | Mandatory | Defines when the active contract becomes valid. |
| `expressionSpecification` | Mandatory | Mandatory | Mandatory | Defines the expression contract metadata. |
| `expressionSpecification.iri` | Mandatory where supplied by expression contract | Mandatory before activation | Mandatory | Authoritative semantic/expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Mandatory where supplied by expression contract | Mandatory before activation | Mandatory | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Mandatory | Mandatory | Mandatory | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Recommended | Optional until activation | Mandatory | Catalogue/discovery/governance view of supported characteristics. |
| `@type` | Mandatory | Mandatory | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Recommended | Mandatory on persisted resource | Mandatory | TMF base type alignment. |

This table is the core architectural proposal.

### 5.3 Recommended but not minimum mandatory fields:

Some fields are valuable and may be mandatory in a specific implementation, but they are not part of the generic minimum mandatory profile.

| **Field** | **Proposed classification** | **Reason** |
| --- | --- | --- |
| `description` | Optional | Useful for catalogue readability and governance context. |
| `relatedParty` | Optional / intent-management-entity governed | Useful for ownership and provider attribution. |
| `@schemaLocation` | Optional / intent-management-entity governed | Useful when an intent management entity publishes a concrete schema for the resource representation. |
| `validFor.endDateTime` | Optional | Useful when a specification has a planned expiry. |
| `schemaVersion` / `schemaHash` inside `targetEntitySchema` | Optional / governed | Useful for schema registry integrity and provenance. |

### 5.4 Persisted resource identity:

The persisted identity model follows the optimiser-definition candidate pattern:

```text
specKey -> stable logical key supplied by the caller
id -> stable server-assigned IntentSpecification lineage resolved from specKey
draftId -> server-assigned mutable DRAFT candidate selector
version -> official public version assigned only when a selected DRAFT is activated
```

`id` is not supplied by the caller on create. ID MS resolves it from `specKey`.
`draftId` is not supplied by the caller. ID MS assigns it for each mutable DRAFT candidate.
`version` is not supplied by the caller on create and is not exposed by DRAFT candidates. ID MS assigns the official public version during activation.

### 5.5 DRAFT profile:

A `DRAFT` candidate may be incomplete because it is still being authored. However, it must contain enough information to be managed, edited, governed, and selected for activation.

Mandatory fields for a persisted `DRAFT` `IntentSpecification` candidate:

| **Field** | **Mandatory** | **Reason** |
| --- | --- | --- |
| `id` | Yes, server-resolved from `specKey` | Stable official lineage identity. |
| `href` | Yes | Canonical DRAFT URL using `/intentSpecification/draft/{draftId}`. |
| `specKey` | Yes | Governs grouping and ID resolution. |
| `draftId` | Yes | Selects the mutable DRAFT candidate. |
| `name` | Yes | Human-readable catalogue name. |
| `lifecycleStatus` | Yes | Must be `DRAFT` for draft candidates. |
| `isBundle` | Yes | Server-resolved value; defaults to `false` if omitted on create. |
| `expressionSpecification` | Yes | Expression contract metadata required to author a meaningful candidate. |
| `targetEntitySchema` | Yes | Schema reference required to author a meaningful candidate. |
| `@type` | Yes | TMF polymorphic resource type. |
| `@baseType` | Yes | TMF base type alignment. |

A `DRAFT` candidate does not expose an official public `version`. Draft revision is represented by `ETag`. A `DRAFT` may omit fields that are required later for activation, such as complete `specCharacteristic`, provided the resource is not activated until the ACTIVE profile is satisfied.

### 5.6 ACTIVE profile:

An `ACTIVE` specification is a published runtime contract. It must be complete enough for discovery, governance, validation, and runtime resolution.

Mandatory fields for an `ACTIVE` `IntentSpecification`:

| **Field** | **Mandatory** | **Reason** |
| --- | --- | --- |
| `id` | Yes | Stable official specification identity. |
| `href` | Yes | Canonical official URL using `/intentSpecification/{id}`. |
| `specKey` | Yes | Governs related versions and active-lineage uniqueness. |
| `draftId` | Yes, as provenance where retained | Shows which DRAFT candidate was activated. |
| `name` | Yes | Human-readable catalogue name. |
| `version` | Yes | Official public version assigned on activation. |
| `lifecycleStatus` | Yes | Must be `ACTIVE`. |
| `isBundle` | Yes | Required for consistent specification interpretation. |
| `validFor.startDateTime` | Yes | Defines when the active contract becomes valid. |
| `expressionSpecification` | Yes | Defines the expression contract metadata. |
| `expressionSpecification.iri` | Yes | Authoritative semantic/expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Yes | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Yes | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Yes | Catalogue/discovery/governance view of important supported characteristics. |
| `@type` | Yes | TMF polymorphic resource type. |
| `@baseType` | Yes | TMF base type alignment. |

Optional TMF fields may still be used when relevant, including `description`, `lastUpdate`, `validFor.endDateTime`, `relatedParty`, `attachment`, `constraint`, `entitySpecRelationship`, `intentSpecRelationship`, and `@schemaLocation`.

These fields are not universally mandatory for every active specification unless a specific use case, product rule, governance rule, or integration rule requires them.

### 5.7 expressionSpecification rule:

For an `ACTIVE` `IntentSpecification`, `expressionSpecification` is mandatory.

Within `expressionSpecification`:

- `iri` is mandatory
- `expressionLanguage` is mandatory

The `iri` identifies the semantic/expression contract. It tells consumers which intent model or expression contract the runtime request follows.

The `expressionLanguage` identifies how the expression is represented and interpreted, for example JSON-LD.

If `expressionSpecification.iri` is mandatory, then `expressionSpecification` itself is necessarily mandatory. The parent object cannot be optional when one of its child fields is required for intent management entity behaviour.

### 5.8 targetEntitySchema rule:

For an `ACTIVE` `IntentSpecification`, `targetEntitySchema` is mandatory.

`targetEntitySchema` is the authoritative machine-readable schema reference for validating runtime expression values.

For the intent management entity, it defines the allowed shape of:

```text
expression.expressionValue.context
```

The canonical context shape contains:

```text
targets[]
constraints[]
preferences[]
```

`targetEntitySchema` should not be replaced by `specCharacteristic`. The two fields serve different purposes.

### 5.9 specCharacteristic rule:

For an `ACTIVE` `IntentSpecification`, `specCharacteristic` is mandatory.

`specCharacteristic` provides the catalogue-facing and governance-facing view of important supported characteristics. It helps users, experience-layer applications, governance processes, and integration consumers understand what the specification supports.

However, `specCharacteristic` is not the authoritative deep validation schema for the runtime expression body. That role belongs to `targetEntitySchema`.

The preferred pattern is:

- `specCharacteristic` gives discoverable high-level characteristics
- `targetEntitySchema` gives detailed machine validation
- `expressionSpecification.iri` identifies the semantic/expression contract

### 5.10 Lifecycle-aware validation:

The intent management entity applies lifecycle-aware validation.

Create and update operations may allow incomplete `DRAFT` resources. Activation to `ACTIVE` must validate the full ACTIVE mandatory profile.

If a client attempts to activate a specification that does not satisfy the ACTIVE profile, the intent management entity must reject the request.

The preferred response is:

```text
422 Unprocessable Entity
```

This means the request is syntactically valid, but the resource cannot transition to the requested lifecycle state because it violates the intent management entity `IntentSpecification` profile.

## 6. Examples:

The examples use a hospital surgical-connectivity scenario only to make the profile concrete. The minimal examples intentionally include only the fields needed to demonstrate the proposed DRAFT and ACTIVE mandatory profiles, not complete API payloads. The fuller example then shows how optional fields may be added for richer governance, discovery, and intent-management-entity-specific version management.

### 6.1 Minimal DRAFT create request and response:

This example proves the minimum draft-candidate profile. The request does not include `id`, `href`, `draftId`, official `version`, or `lifecycleStatus` because those fields are server-managed. `isBundle` is optional on create and defaults to `false` when omitted.

```http
POST /intentManagement/v5/intentSpecification
Content-Type: application/json
Accept: application/json
```

```json
{
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://example.com/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://example.com/schemas/intentExpression/hospital-surgical-slice.schema.json"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

The persisted response includes the resolved official lineage identity and the mutable DRAFT candidate selector.

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
Content-Type: application/json
ETag: "id-draft-hospital-surgical-slice-a-r1"
```

```json
{
  "id": "hospital-surgical-slice-spec",
  "href": "/intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://example.com/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://example.com/schemas/intentExpression/hospital-surgical-slice.schema.json"
  },
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

### 6.2 Minimal activation request and ACTIVE response:

This example proves the minimum active-runtime-contract profile.

It adds or finalises the mandatory fields required before the selected DRAFT candidate can be activated and used as a published runtime contract.

```http
PATCH /intentManagement/v5/intentSpecification/draft/id-draft-hospital-surgical-slice-a
Content-Type: application/merge-patch+json
Accept: application/json
If-Match: "id-draft-hospital-surgical-slice-a-r1"
```

```json
{
  "lifecycleStatus": "ACTIVE"
}
```

The response confirms the persisted official active contract and returns the official version assigned during activation.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-r1"
```

```json
{
  "id": "hospital-surgical-slice-spec",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec",
  "specKey": "hospital-surgical-slice-spec",
  "draftId": "id-draft-hospital-surgical-slice-a",
  "name": "Hospital Surgical Slice Intent Specification",
  "version": "1.19",
  "lifecycleStatus": "ACTIVE",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://example.com/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://example.com/schemas/intentExpression/hospital-surgical-slice-v1.19.schema.json"
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

### 6.3 Fuller illustrative example with optional fields:

This example shows how an implementation can add optional fields for richer governance, spec-key version management, catalogue discovery, ownership, schema integrity, and operation affordances.

These fields are useful, but they are not all part of the generic minimum mandatory profile.

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "specKey": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents.",
  "version": "1.19",
  "lifecycleStatus": "ACTIVE",
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
        "id": "provider",
        "name": "Example Provider",
        "@referredType": "Provider"
      }
    }
  ],
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://example.com/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://example.com/schemas/intentExpression/hospital-surgical-slice-v1.19.schema.json",
    "schemaVersion": "1.19",
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
      "maxCardinality": 1,
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "object",
          "isDefault": true,
          "value": {
            "targets": {
              "maxLatencyMs": 10,
              "minAvailabilityPercent": 99.99,
              "maxJitterMs": 2,
              "maxPacketLossPercent": 0.01
            },
            "constraints": {
              "location": {
                "locationId": "AU-NSW-SYD-HOSP-001",
                "locationType": "hospital",
                "geographicScope": "campus"
              },
              "serviceType": "surgical-connectivity",
              "serviceClass": "critical-gold",
              "priority": "critical",
              "redundancyRequired": true,
              "timeWindow": {
                "startDateTime": "2026-04-18T12:00:00+10:00"
              }
            },
            "preferences": {
              "preferredAccessTechnology": "5G"
            }
          }
        }
      ]
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://example.com/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19.schema.json",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    },
    "fullUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH"
    }
  }
}
```

## 7. Consequences:

### 7.1 Positive consequences:

If accepted, this proposal gives the intent management entity:

- deterministic specification identity
- stronger lifecycle governance
- safer activation rules
- reliable runtime expression validation
- clearer runtime resolution behaviour
- better event payload consistency
- clearer separation between TMF base optionality and intent management entity conformance
- better support for catalogue discovery

### 7.2 Trade-offs:

If accepted, this proposal also means:

- the intent management entity is stricter than a minimal TMF implementation
- clients must provide more information before a specification can become active
- activation validation becomes more important than simple create validation
- the intent management entity must maintain lifecycle-aware validation rules
- some clients may need to distinguish between creating a draft and publishing an active runtime contract

These trade-offs are acceptable because active specifications are not just catalogue records. They are runtime contract definitions used by intent-processing components.

## 8. Alternatives considered:

### 8.1 Treat TMF optional fields as intent management entity optional:

This was rejected.

It would make create/update easier, but it would allow active specifications that are not usable for runtime validation or runtime resolution.

### 8.2 Make every useful field mandatory at create time:

This was rejected.

It would make the create operation too rigid and would make it harder to incrementally author a specification. The intent management entity should allow controlled incomplete drafts.

### 8.3 Make expressionSpecification.iri mandatory but not expressionSpecification:

This was rejected as structurally inconsistent.

A child field cannot be mandatory for intent management entity behaviour while the parent object remains optional. Therefore, if `expressionSpecification.iri` is mandatory, `expressionSpecification` is mandatory too.

### 8.4 Make runtime intentSpecification.id mandatory everywhere:

This was previously deferred to the runtime intent API decision.

That runtime decision is now baselined: submitted runtime `Intent` admission requires both `intentSpecification.id` and `expression.iri`. Draft creation may remain lighter and may omit both fields until admission is requested.

This proposal still remains focused on the `IntentSpecification` mandatory profile. It mandates `id` on every persisted `IntentSpecification`, while the runtime intent API decision mandates `intentSpecification.id` and `expression.iri` for submitted runtime admission.

## 9. Proposal outcome:

This proposal recommends adopting the optimiser-style definition-candidate model for ID MS `IntentSpecification` governance.

If accepted, the intent management entity will document and enforce this lifecycle-aware profile:

- `POST /intentSpecification` creates a mutable DRAFT candidate.
- `specKey` is mandatory on create and resolves the stable server-assigned `IntentSpecification.id`.
- `draftId` is server-assigned and selects the mutable DRAFT candidate.
- DRAFT candidates do not expose an official public `version`; draft revision is represented by `ETag`.
- DRAFT retrieval, update, activation, and deletion use `/intentSpecification/draft/{draftId}`.
- The official public `version` is assigned only when the selected DRAFT candidate is activated.
- ACTIVE and RETIRED official records are selected by `/intentSpecification/{id}` and are immutable for material contract changes.
- `expressionSpecification` is mandatory for active resources.
- `expressionSpecification.iri` and `expressionSpecification.expressionLanguage` are mandatory for active resources.
- `targetEntitySchema` and `specCharacteristic` are mandatory for active resources.
- Activation fails if the ACTIVE profile is not satisfied.
- Runtime IC MS admission must reference a concrete ACTIVE `intentSpecification.id`, not `specKey` or `draftId`.

## 10. References:

| **Reference** | **URL** | **Relevance to this proposal** |
| --- | --- | --- |
| TMF921 Intent Management API v5.0.0 specification | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Defines the TMF921 Intent Management API and the `IntentSpecification` resource model used as the base for the intent management entity profile. |
| TMF921 Intent Management API v5.0.0 OpenAPI / Swagger artefact | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the OpenAPI resource and event schemas used to validate the TMF-facing API shape. |
| TMF921 Intent Management API v5.0.0 conformance profile | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the TMF conformance context while leaving implementation-specific mandatory profile choices to the intent management entity. |
| TR292 TM Forum Intent Ontology (TIO) v3.6.0 | https://www.tmforum.org/resources/standard/tr292-intent-ontology-tio-v3-6-0/ | Provides the intent ontology reference model and model-federation context behind semantic/expression contract identifiers. |
| TR299 Intent Specification | https://www.tmforum.org/resources/standard/tr299-intent-specification/ | Provides the intent specification concept used to describe rules for well-formed intent and allowed intent content. |
| Intent architecture baseline repository | https://github.com/prageethw/im/tree/main/baseline/intent | Holds the intent architecture baseline and project-specific profile artefacts. |

## 11. Follow-up work:

After this proposal is reviewed and baselined, update the affected architecture and specification artifacts surgically:

- document the platform mandatory profile
- clarify DRAFT versus ACTIVE validation
- clarify `id`, `expressionSpecification`, `expressionSpecification.iri`, and `expressionSpecification.expressionLanguage`
- clarify activation failure behaviour
- reference this decision where the mandatory profile is discussed
- keep runtime request admission rules aligned with the runtime intent API baseline: submitted runtime admission requires both `intentSpecification.id` and `expression.iri`, while Draft creation may remain lighter
