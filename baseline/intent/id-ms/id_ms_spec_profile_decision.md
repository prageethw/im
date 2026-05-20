# IntentSpecification mandatory profile proposal

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
- Can a runtime intent be resolved by expression IRI when an explicit specification reference is not supplied?
- Can event subscribers interpret specification events without an authoritative resource identity?

Therefore, the intent management entity needs a mandatory profile that is stricter than the minimum generic TMF shape.

## 4. Decision drivers:

The proposal is driven by the following architecture needs:

| **Driver** | **Need** |
| --- | --- |
| TMF alignment | Use the TMF921 resource model and API/event patterns without inventing an incompatible resource shape. |
| Runtime safety | Prevent activation of specifications that cannot be used for runtime validation or resolution. |
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

This proposal defines different minimum mandatory profiles for `DRAFT` and `ACTIVE`.

A `DRAFT` specification must have enough information to be identified, versioned, edited, governed, and safely transitioned later.

An `ACTIVE` specification must have enough information to act as a published runtime contract for discovery, validation, governance, and runtime resolution.

| **Field** | **DRAFT** | **ACTIVE** | **Reason** |
| --- | --- | --- | --- |
| `id` | Mandatory on persisted resource | Mandatory | Stable immutable resource identity. |
| `href` | Mandatory on persisted resource | Mandatory | Canonical resource URL for TMF-style navigation and references. |
| `name` | Mandatory | Mandatory | Human-readable catalogue name. |
| `version` | Mandatory | Mandatory | Version identity. |
| `lifecycleStatus` | Mandatory | Mandatory | Identifies whether the specification is draft, active, or retired. |
| `isBundle` | Mandatory | Mandatory | Clarifies whether the specification is a bundle. |
| `validFor.startDateTime` | Optional | Mandatory | Defines when the active contract becomes valid. |
| `expressionSpecification` | Optional | Mandatory | Defines the expression contract metadata. |
| `expressionSpecification.iri` | Optional | Mandatory | Authoritative semantic/expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Optional | Mandatory | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Optional | Mandatory | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Optional | Mandatory | Catalogue/discovery/governance view of supported characteristics. |
| `@type` | Mandatory | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | Mandatory | TMF base type alignment. |

This table is the core architectural proposal.

### 5.3 Recommended but not minimum mandatory fields:

Some fields are valuable and may be mandatory in a specific implementation, but they are not part of this generic minimum mandatory profile.

| **Field** | **Proposed classification** | **Reason** |
| --- | --- | --- |
| `familyId` | Optional / intent-management-entity governed | Useful for version-family governance, but not required as a generic minimum mandatory field. |
| `description` | Optional | Useful for catalogue readability and governance context. |
| `relatedParty` | Optional / intent-management-entity governed | Useful for ownership and provider attribution. |
| `@schemaLocation` | Optional / intent-management-entity governed | Useful when an intent management entity publishes a concrete schema for the resource representation. |
| `validFor.endDateTime` | Optional | Useful when a specification has a planned expiry. |
| `schemaVersion` / `schemaHash` inside `targetEntitySchema` | Optional / intent-management-entity governed | Useful for stronger schema governance and integrity verification. |
| `_links` | Optional / intent-management-entity governed | Useful for discoverable operation affordances. |

An intent management entity may make any of these fields mandatory in a concrete implementation profile, but that is a stronger implementation-specific rule rather than the generic minimum mandatory profile proposed here.

### 5.4 Persisted resource identity:

`id` is mandatory on every persisted `IntentSpecification` resource.

The create operation may support either of the following patterns:

- the intent management entity generates the `id`
- an authorised client supplies the `id`, subject to governance rules

After creation, `id` is immutable.

`id` must be present in retrieve responses, list responses, update responses, delete precondition evaluation, event payloads, and internal references from other services or components.

`href` is also mandatory on persisted and returned resources because it provides the canonical resource URL for TMF-style navigation and event references.

### 5.5 DRAFT profile:

A `DRAFT` specification may be incomplete because it is still being authored. However, it must contain enough information to be managed, versioned, and governed.

Mandatory fields for a persisted `DRAFT` `IntentSpecification`:

| **Field** | **Mandatory** | **Reason** |
| --- | --- | --- |
| `id` | Yes, on persisted resource | Stable immutable resource identity. |
| `href` | Yes, on persisted resource | Canonical resource URL. |
| `name` | Yes | Human-readable catalogue name. |
| `version` | Yes | Version identity. |
| `lifecycleStatus` | Yes | Must be `DRAFT` for draft specifications. |
| `isBundle` | Yes | Clarifies whether the specification is a bundle. |
| `@type` | Yes | TMF polymorphic resource type. |
| `@baseType` | Yes | TMF base type alignment. |

A `DRAFT` may omit fields that are required later for activation, such as `targetEntitySchema`, complete `specCharacteristic`, or complete `expressionSpecification`, provided the resource is not activated until the ACTIVE profile is satisfied.

### 5.6 ACTIVE profile:

An `ACTIVE` specification is a published runtime contract. It must be complete enough for discovery, governance, validation, and runtime resolution.

Mandatory fields for an `ACTIVE` `IntentSpecification`:

| **Field** | **Mandatory** | **Reason** |
| --- | --- | --- |
| `id` | Yes | Stable immutable specification identity. |
| `href` | Yes | Canonical resource URL. |
| `name` | Yes | Human-readable catalogue name. |
| `version` | Yes | Version identity. |
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

This example proves the minimum draft-manageability profile. The request does not include `id` or `href` because the intent management entity may generate them during create.

```http
POST /intentManagement/v5/intentSpecification
Content-Type: application/json
Accept: application/json
```

```json
{
  "name": "Hospital Surgical Slice Intent Specification",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

The persisted response includes the generated resource identity and canonical URL.

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/json
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital Surgical Slice Intent Specification",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

### 6.2 Minimal ACTIVE update request and response:

This example proves the minimum active-runtime-contract profile.

It adds the mandatory fields required before the specification can be used as a published runtime contract.

```http
PUT /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
Content-Type: application/json
Accept: application/json
If-Match: "intent-spec-hospital-surgical-slice-spec-v1.19-v1"
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
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

The response confirms the persisted active contract and returns the updated validator version.

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Location: /intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: "intent-spec-hospital-surgical-slice-spec-v1.19-v2"
```

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
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

This example shows how an implementation can add optional fields for richer governance, version-family management, catalogue discovery, ownership, schema integrity, and operation affordances.

These fields are useful, but they are not all part of the generic minimum mandatory profile.

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "familyId": "hospital-surgical-slice-spec",
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

This is deferred to a separate runtime intent API decision.

This proposal mandates `id` on every persisted `IntentSpecification`, but runtime submission rules belong to the runtime intent API. A runtime API may still support resolution by runtime `expression.iri` where it is unambiguous.

## 9. Proposal outcome:

This proposal recommends adopting an intent management entity `IntentSpecification` mandatory profile baseline.

If accepted, the intent management entity will document and enforce a lifecycle-aware `IntentSpecification` mandatory profile:

- `DRAFT` requires identity and lifecycle-management fields.
- `ACTIVE` requires the full intent management entity runtime contract profile.
- `id` is mandatory and immutable on persisted resources.
- `expressionSpecification` is mandatory for active resources.
- `expressionSpecification.iri` and `expressionSpecification.expressionLanguage` are mandatory for active resources.
- `targetEntitySchema` and `specCharacteristic` are mandatory for active resources.
- Activation fails if the ACTIVE profile is not satisfied.

## 10. References:

| **Reference** | **URL** | **Relevance to this proposal** |
| --- | --- | --- |
| TMF921 Intent Management API v5.0.0 specification | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Defines the TMF921 Intent Management API and the `IntentSpecification` resource model used as the base for the intent management entity profile. |

## 11. Follow-up work:

After this proposal is reviewed and baselined, update the affected architecture and specification artifacts surgically:

- document the platform mandatory profile
- clarify DRAFT versus ACTIVE validation
- clarify `id`, `expressionSpecification`, `expressionSpecification.iri`, and `expressionSpecification.expressionLanguage`
- clarify activation failure behaviour
- reference this decision where the mandatory profile is discussed
- keep runtime request resolution rules separate from this decision unless explicitly baselined in the runtime intent API
