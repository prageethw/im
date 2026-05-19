# IntentSpecification mandatory profile proposal

## 1. Decision summary

This proposal defines the minimum mandatory attribute profile for `IntentSpecification` resources on this platform, layered on top of TMF921 Intent Management API v5.0.0.

TMF921 provides the generic `IntentSpecification` resource model together with the associated API and event patterns, but it does not prescribe a single universal mandatory attribute profile for every implementation. This platform therefore adopts a stricter profile so that `IntentSpecification` resources are usable for catalogue governance, lifecycle management, runtime expression validation, and runtime intent resolution.

The key proposals are:

- define the minimum mandatory attributes for a persisted `DRAFT` `IntentSpecification`
- define the minimum mandatory attributes for an `ACTIVE` `IntentSpecification`

This proposal defines a platform profile rule. It does not claim that TMF921 universally mandates the same fields for every implementation.

## 2. Proposal flow diagram

![IntentSpecification mandatory profile proposal](id_ms_spec_profile_decision.svg)

## 3. Context

TMF921 intentionally leaves implementation flexibility in the `IntentSpecification` model, which supports interoperability across different operating environments and implementation choices. That flexibility is useful because different organisations need different levels of catalogue detail, lifecycle governance, schema discipline, and runtime coupling.

For this platform, however, an `IntentSpecification` is not only a descriptive catalogue record. Once active, it becomes a published runtime contract used by downstream consumers to discover, validate, and resolve submitted runtime intents.

If too many fields are treated as optional, downstream runtime behaviour becomes ambiguous. The platform must be able to answer questions such as:

- Which specification defines the submitted runtime expression?
- Which semantic contract does the expression follow?
- Which schema validates the runtime expression body?
- Is the specification active and within its validity period?
- Which version family does this specification belong to?
- Can a runtime intent be resolved by expression IRI when an explicit specification reference is not supplied?
- Can event subscribers interpret specification events without an authoritative resource identity?

Therefore, the platform needs a mandatory profile that is stricter than the minimum generic TMF shape exposed by TMF921.

## 4. Decision drivers

The proposal is driven by the following architecture needs:

| Driver | Need |
| --- | --- |
| TMF alignment | Use the TMF921 resource model and API/event patterns without inventing an incompatible resource shape. |
| Runtime safety | Prevent activation of specifications that cannot be used for runtime validation or resolution. |
| Governance | Ensure every persisted specification has stable identity, lifecycle status, version identity, and family grouping. |
| Discoverability | Ensure active specifications can be discovered and understood by users, portals, and integration consumers. |
| Validation | Ensure active specifications have a machine-readable validation contract. |
| Semantic clarity | Ensure active specifications identify the semantic and expression contract they support. |
| Evolvability | Allow incomplete drafts while preventing incomplete active contracts. |

## 5. Proposal

### 5.1 TMF-aligned, not TMF-minimal

The platform remains TMF-aligned by using the TMF921 `IntentSpecification` resource model, including TMF-style identity, lifecycle status, specification characteristics, expression specification, target entity schema, relationships, and events.

However, the platform does not adopt a TMF-minimal interpretation where most fields are treated as operationally optional. Instead, it applies a mandatory profile that fits the runtime architecture and operating model of this platform.

The governing rule is:

> TMF-aligned does not mean TMF-minimal.

### 5.2 Minimum mandatory profile by lifecycle state

This proposal defines different minimum mandatory profiles for `DRAFT` and `ACTIVE` resources. A `DRAFT` specification must contain enough information to be identified, versioned, edited, governed, and safely transitioned later, while an `ACTIVE` specification must be complete enough to operate as a published runtime contract for discovery, validation, governance, and runtime resolution.

| Field | DRAFT | ACTIVE | Reason |
| --- | --- | --- | --- |
| `id` | Mandatory | Mandatory | Stable immutable resource identity. |
| `href` | Mandatory | Mandatory | Canonical resource URL for TMF-style navigation and references. |
| `name` | Mandatory | Mandatory | Human-readable catalogue name. |
| `familyId` | Mandatory | Mandatory | Groups versions of the same logical specification family. |
| `version` | Mandatory | Mandatory | Version identity within the family. |
| `lifecycleStatus` | Mandatory | Mandatory | Identifies whether the specification is draft, active, or retired. |
| `isBundle` | Mandatory | Mandatory | Clarifies whether the specification is a bundle. |
| `validFor.startDateTime` | Optional | Mandatory | Defines when the active contract becomes valid. |
| `expressionSpecification` | Optional | Mandatory | Defines the expression contract metadata. |
| `expressionSpecification.iri` | Optional | Mandatory | Authoritative semantic and expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Optional | Mandatory | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Optional | Mandatory | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Optional | Mandatory | Catalogue, discovery, and governance view of supported characteristics. |
| `@type` | Mandatory | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | Mandatory | TMF base type alignment. |

This table is the core architectural proposal.

### 5.3 Persisted resource identity

`id` is mandatory on every persisted `IntentSpecification` resource. The create operation may either allow the platform to generate the `id` or allow an authorised client to supply the `id` subject to governance rules.

After creation, `id` is immutable. `id` must be present in retrieve responses, list responses, update responses, delete precondition evaluation, external event payloads, and internal references from other services or components.

`href` is also mandatory on persisted and returned resources because it provides the canonical resource URL for TMF-style navigation and event references.

### 5.4 DRAFT profile

A `DRAFT` specification may be incomplete because it is still being authored, but it must contain enough information to be managed, versioned, and governed.

Mandatory fields for a persisted `DRAFT` `IntentSpecification` are:

| Field | Mandatory | Reason |
| --- | --- | --- |
| `id` | Yes | Stable immutable resource identity. |
| `href` | Yes | Canonical resource URL. |
| `name` | Yes | Human-readable catalogue name. |
| `familyId` | Yes | Groups versions of the same logical specification family. |
| `version` | Yes | Version identity within the family. |
| `lifecycleStatus` | Yes | Must be `DRAFT` for draft specifications. |
| `isBundle` | Yes | Clarifies whether the specification is a bundle. |
| `@type` | Yes | TMF polymorphic resource type. |
| `@baseType` | Yes | TMF base type alignment. |

A `DRAFT` may omit fields that are required later for activation, such as `targetEntitySchema`, complete `specCharacteristic`, or complete `expressionSpecification`, provided the resource is not activated until the `ACTIVE` profile is satisfied.

### 5.5 ACTIVE profile

An `ACTIVE` specification is a published runtime contract. It must be complete enough for discovery, governance, validation, and runtime resolution.

Mandatory fields for an `ACTIVE` `IntentSpecification` are:

| Field | Mandatory | Reason |
| --- | --- | --- |
| `id` | Yes | Stable immutable specification identity. |
| `href` | Yes | Canonical resource URL. |
| `name` | Yes | Human-readable catalogue name. |
| `familyId` | Yes | Version family identity. |
| `version` | Yes | Version identity. |
| `lifecycleStatus` | Yes | Must be `ACTIVE`. |
| `isBundle` | Yes | Required for consistent specification interpretation. |
| `validFor.startDateTime` | Yes | Defines when the active contract becomes valid. |
| `expressionSpecification` | Yes | Defines the expression contract metadata. |
| `expressionSpecification.iri` | Yes | Authoritative semantic and expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Yes | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Yes | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Yes | Catalogue, discovery, and governance view of important supported characteristics. |
| `@type` | Yes | TMF polymorphic resource type. |
| `@baseType` | Yes | TMF base type alignment. |

Optional TMF fields may still be used when relevant, including `description`, `lastUpdate`, `validFor.endDateTime`, `relatedParty`, `attachment`, `constraint`, `entitySpecRelationship`, `intentSpecRelationship`, and `@schemaLocation`. These fields are not universally mandatory for every active specification unless a specific use case, product rule, governance rule, or integration rule requires them.

### 5.6 expressionSpecification rule

For an `ACTIVE` `IntentSpecification`, `expressionSpecification` is mandatory. Within `expressionSpecification`, both `iri` and `expressionLanguage` are mandatory.

The `iri` identifies the semantic and expression contract. TM Forum's Intent Common Model and Intent Expression ontology provides the basis for this expression-level contract, including the use of model IRIs such as `http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/`.

The `expressionLanguage` identifies how the expression is represented and interpreted, for example JSON-LD. If `expressionSpecification.iri` is mandatory, then `expressionSpecification` itself is necessarily mandatory; the parent object cannot remain optional when one of its child fields is required for platform behaviour.

### 5.7 targetEntitySchema rule

For an `ACTIVE` `IntentSpecification`, `targetEntitySchema` is mandatory. It is the authoritative machine-readable schema reference for validating runtime expression values, which aligns with the conformance-oriented discipline expected in the TMF921B Intent Management Conformance Profile.

For this platform, `targetEntitySchema` defines the allowed shape of:

```text
expression.expressionValue.context
```

The canonical context shape contains:

```text
targets[]
constraints[]
preferences[]
```

`targetEntitySchema` should not be replaced by `specCharacteristic` because the two fields serve different purposes.

### 5.8 specCharacteristic rule

For an `ACTIVE` `IntentSpecification`, `specCharacteristic` is mandatory.

`specCharacteristic` provides the catalogue-facing and governance-facing view of important supported characteristics. It helps users, experience-layer applications, governance processes, and integration consumers understand what the specification supports.

However, `specCharacteristic` is not the authoritative deep validation schema for the runtime expression body. That role belongs to `targetEntitySchema`.

The preferred pattern is:

- `specCharacteristic` gives discoverable high-level characteristics.
- `targetEntitySchema` gives detailed machine validation.
- `expressionSpecification.iri` identifies the semantic and expression contract.

### 5.9 Lifecycle-aware validation

The platform applies lifecycle-aware validation. Create and update operations may allow incomplete `DRAFT` resources, but transition to `ACTIVE` must validate the full active mandatory profile.

If a client attempts to activate a specification that does not satisfy the `ACTIVE` profile, the platform must reject the request. Using `422 Unprocessable Entity` is consistent with TM Forum Open API design conventions in which a request can be syntactically valid but still rejected because the resource state or content violates business rules.

The preferred response is:

```text
422 Unprocessable Entity
```

## 6. Examples

### 6.1 Minimal DRAFT example

This example shows a persisted draft with enough identity to be governed and edited, but not yet enough information to be activated.

```json
{
  "id": "hospital-surgical-slice-spec-v1.20",
  "href": "https://mycsp.com.au/tmf-api/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20",
  "name": "Hospital Surgical Slice Specification",
  "familyId": "hospital-surgical-slice-spec",
  "version": "1.20",
  "lifecycleStatus": "DRAFT",
  "isBundle": false,
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

### 6.2 ACTIVE example excerpt

This example shows the important fields required before activation. The `expressionSpecification.iri` value is a TM Forum Intent Ontology (TIO) identifier that binds the specification to a semantic expression model defined in TR290A.

```json
{
  "id": "hospital-surgical-slice-spec-v1.20",
  "href": "https://mycsp.com.au/tmf-api/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20",
  "name": "Hospital Surgical Slice Specification",
  "familyId": "hospital-surgical-slice-spec",
  "version": "1.20",
  "lifecycleStatus": "ACTIVE",
  "isBundle": false,
  "validFor": {
    "startDateTime": "2026-04-17T10:00:00+10:00"
  },
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schema/intent/hospital-surgical-slice-expression-value.schema.json"
  },
  "specCharacteristic": [
    {
      "name": "context",
      "description": "Canonical runtime intent context containing targets, constraints, and preferences.",
      "valueType": "object",
      "configurable": true,
      "@type": "CharacteristicSpecification"
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification"
}
```

### 6.3 Runtime expression relationship example

An active specification defines the semantic contract through `expressionSpecification`, and a runtime intent can then use the corresponding expression `iri`.

```json
{
  "expressionSpecification": {
    "expressionLanguage": "JSON-LD",
    "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
  }
}
```

A runtime intent can then use the corresponding expression IRI:

```json
{
  "expression": {
    "@type": "JsonLdExpression",
    "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
    "expressionValue": {
      "context": {
        "targets": [
          {
            "name": "low-latency-surgical-connectivity",
            "targetType": "latency",
            "operator": "lessThanOrEqualTo",
            "value": 10,
            "unit": "ms"
          }
        ],
        "constraints": [
          {
            "name": "location",
            "constraintType": "site",
            "operator": "equals",
            "value": "hospital-a-surgery-wing"
          },
          {
            "name": "serviceClass",
            "constraintType": "serviceClass",
            "operator": "equals",
            "value": "surgical"
          }
        ],
        "preferences": [
          {
            "name": "prefer-resilient-path",
            "preferenceType": "resilience",
            "weight": 80
          }
        ]
      }
    }
  }
}
```

A runtime API may choose to make explicit `intentSpecification.id` mandatory, or it may resolve the active specification from runtime `expression.iri` when the match is unambiguous. That runtime resolution rule is a separate API decision and is not decided by this specification-profile proposal.

## 7. Consequences

### 7.1 Positive consequences

If accepted, this proposal gives the platform deterministic specification identity, stronger lifecycle governance, safer activation rules, reliable runtime expression validation, clearer runtime resolution behaviour, better event payload consistency, and clearer separation between TMF base optionality and platform conformance.

It also improves support for catalogue discovery and published runtime contract management.

### 7.2 Trade-offs

If accepted, this proposal also means the platform is stricter than a minimal TMF implementation, clients must provide more information before a specification can become active, activation validation becomes more important than simple create validation, and the platform must maintain lifecycle-aware validation rules.

Some clients may therefore need to distinguish between creating a draft and publishing an active runtime contract.

These trade-offs are acceptable because active specifications are not just catalogue records; they are runtime contract definitions used by intent-processing components.

## 8. Alternatives considered

### 8.1 Treat TMF optional fields as platform optional

This option was rejected because it would make create and update easier while still allowing active specifications that are not usable for runtime validation or runtime resolution.

### 8.2 Make every useful field mandatory at create time

This option was rejected because it would make the create operation too rigid and would make incremental specification authoring harder. The platform should allow controlled incomplete drafts.

### 8.3 Make `expressionSpecification.iri` mandatory but not `expressionSpecification`

This option was rejected as structurally inconsistent because a child field cannot be mandatory for platform behaviour while the parent object remains optional.

### 8.4 Make runtime `intentSpecification.id` mandatory everywhere

This is deferred to a separate runtime intent API decision. This proposal mandates `id` on every persisted `IntentSpecification`, but runtime submission rules belong to the runtime intent API and may still support resolution by runtime `expression.iri` where that is unambiguous.

## 9. Proposal outcome

This proposal recommends adopting a platform `IntentSpecification` mandatory profile baseline.

If accepted, the platform will document and enforce a lifecycle-aware `IntentSpecification` mandatory profile in which:

- `DRAFT` requires identity and lifecycle-management fields.
- `ACTIVE` requires the full platform runtime contract profile.
- `id` is mandatory and immutable on persisted resources.
- `expressionSpecification` is mandatory for active resources.
- `expressionSpecification.iri` and `expressionSpecification.expressionLanguage` are mandatory for active resources.
- `targetEntitySchema` and `specCharacteristic` are mandatory for active resources.
- Activation fails if the active profile is not satisfied.

## 10. Follow-up work

After this proposal is reviewed and baselined, update the affected architecture and specification artefacts surgically:

- document the platform mandatory profile
- clarify `DRAFT` versus `ACTIVE` validation
- clarify `id`, `expressionSpecification`, `expressionSpecification.iri`, and `expressionSpecification.expressionLanguage`
- clarify activation failure behaviour
- reference this decision wherever the mandatory profile is discussed
- keep runtime request resolution rules separate from this decision unless they are explicitly baselined in the runtime intent API

## References

| Ref | Document | Version | URL |
| --- | --- | --- | --- |
| [TMF921] | TMF921 Intent Management API User Guide | v5.0.0 | https://www.tmforum.org/resources/specifications/tmf921-intent-management-api-user-guide-v5-0-0/ |
| [TMF921B] | TMF921B Intent Management Conformance Profile | v5.0.0 | https://www.tmforum.org/resources/specifications/tmf921b-intent-management-conformance-profile-v5-0-0/ |
| [TR290A] | TR290A Intent Common Model – Intent Expression | v3.4.0 | https://www.tmforum.org/resources/introductory-guide/intent-common-model-intent-expression-v3-4-0-tr290a/ |
| [TR299] | TR299 Intent Specification | v3.6.0 | https://www.tmforum.org/resources/introductory-guide/tr299-intent-specification-v3-6-0/ |
| [IG1358] | IG1358 Intent Based Operation User Guide | v1.1.0 | https://www.tmforum.org/resources/introductory-guide/ig1358-intent-based-operation-user-guide-v1-1-0/ |
| [TMF-APIs] | TM Forum Open API Design Guidelines | — | https://www.tmforum.org/oda/open-apis/ |
