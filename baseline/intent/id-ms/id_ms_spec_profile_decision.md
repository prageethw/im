# IntentSpecification mandatory profile decision

## 1. Decision summary

This decision defines a platform-specific mandatory profile for `IntentSpecification`, layered on top of TMF921.

TMF921 provides the generic `IntentSpecification` resource model, operation pattern, and event pattern. It does not prescribe the complete mandatory attribute profile required by every implementation. This platform therefore defines a stricter profile so that `IntentSpecification` resources are usable for catalogue governance, lifecycle management, runtime expression validation, and runtime intent resolution.

The key decision is:

- TMF921 alignment is the base model.
- Platform conformance defines the mandatory profile.
- `DRAFT` specifications may be incomplete within controlled limits.
- `ACTIVE` specifications must be complete enough to be safely discovered, governed, resolved, and used by runtime intent processing.
- `id` is mandatory on every persisted `IntentSpecification` resource.
- `expressionSpecification` is mandatory for an `ACTIVE` `IntentSpecification`.
- `expressionSpecification.iri` is mandatory inside `expressionSpecification` and is the authoritative semantic/expression contract identifier.
- `expressionSpecification.expressionLanguage` is mandatory inside `expressionSpecification` so consumers know how the expression is represented and interpreted.

This decision is a platform profile rule. It does not claim that TMF921 universally mandates the same fields for every implementation.

## 2. Context

TMF921 intentionally leaves implementation flexibility in the `IntentSpecification` model. That is useful for broad interoperability, because different organisations may need different levels of catalogue detail, lifecycle governance, schema discipline, and runtime coupling.

However, for this platform, an `IntentSpecification` is not only a descriptive catalogue record. Once active, it becomes a published runtime contract used by downstream consumers to understand, validate, and resolve submitted runtime intents.

If too many fields are treated as optional, downstream runtime behaviour becomes ambiguous.

The platform must be able to answer questions such as:

- Which specification defines the submitted runtime expression?
- Which semantic contract does the expression follow?
- Which schema validates the runtime expression body?
- Is the specification active and within its validity period?
- Which version family does this specification belong to?
- Can a runtime intent be resolved by expression IRI when an explicit specification reference is not supplied?
- Can event subscribers interpret specification events without an authoritative resource identity?

Therefore, the platform needs a mandatory profile that is stricter than the minimum generic TMF shape.

## 3. Decision drivers

The decision is driven by the following architecture needs:

| Driver | Need |
| --- | --- |
| TMF alignment | Use the TMF921 resource model and API/event patterns without inventing an incompatible resource shape. |
| Runtime safety | Prevent activation of specifications that cannot be used for runtime validation or resolution. |
| Governance | Ensure every persisted specification has stable identity, lifecycle status, version identity, and family grouping. |
| Discoverability | Ensure active specifications can be discovered and understood by users, portals, and integration consumers. |
| Validation | Ensure active specifications have a machine-readable validation contract. |
| Semantic clarity | Ensure active specifications identify the semantic/expression contract they support. |
| Evolvability | Allow incomplete drafts while preventing incomplete active contracts. |

## 4. Decision

### 4.1 TMF-aligned, not TMF-minimal

The platform remains TMF-aligned by using the TMF921 `IntentSpecification` resource model, including TMF-style identity, lifecycle status, specification characteristics, expression specification, target entity schema, related parties, relationships, and events.

However, the platform does not adopt a TMF-minimal interpretation where most fields are treated as operationally optional. Instead, the platform applies a mandatory profile appropriate for its runtime architecture.

The rule is:

> TMF-aligned does not mean TMF-minimal.

### 4.2 Persisted resource identity

`id` is mandatory on every persisted `IntentSpecification` resource.

The create operation may support either of the following patterns:

- the platform generates the `id`
- an authorised client supplies the `id`, subject to governance rules

After creation, `id` is immutable.

`id` must be present in:

- retrieve responses
- list responses
- update responses
- delete precondition evaluation
- external event payloads
- internal references from other services or components

`href` is also mandatory on persisted and returned resources because it provides the canonical resource URL for TMF-style navigation and event references.

### 4.3 DRAFT profile

A `DRAFT` specification may be incomplete because it is still being authored. However, it must contain enough information to be managed, versioned, and governed.

Mandatory fields for a persisted `DRAFT` `IntentSpecification`:

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

A `DRAFT` may omit fields that are required later for activation, such as `targetEntitySchema`, complete `specCharacteristic`, or complete `expressionSpecification`, provided the resource is not activated until the ACTIVE profile is satisfied.

### 4.4 ACTIVE profile

An `ACTIVE` specification is a published runtime contract. It must be complete enough for discovery, governance, validation, and runtime resolution.

Mandatory fields for an `ACTIVE` `IntentSpecification`:

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
| `expressionSpecification.iri` | Yes | Authoritative semantic/expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Yes | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Yes | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Yes | Catalogue/discovery/governance view of important supported characteristics. |
| `@type` | Yes | TMF polymorphic resource type. |
| `@baseType` | Yes | TMF base type alignment. |

Optional TMF fields may still be used when relevant, including:

- `description`
- `lastUpdate`
- `validFor.endDateTime`
- `relatedParty`
- `attachment`
- `constraint`
- `entitySpecRelationship`
- `intentSpecRelationship`
- `@schemaLocation`

These fields are not universally mandatory for every active specification unless a specific use case, product rule, governance rule, or integration rule requires them.

### 4.5 expressionSpecification rule

For an `ACTIVE` `IntentSpecification`, `expressionSpecification` is mandatory.

Within `expressionSpecification`:

- `iri` is mandatory
- `expressionLanguage` is mandatory

The `iri` identifies the semantic/expression contract. It tells consumers which intent model or expression contract the runtime request follows.

The `expressionLanguage` identifies how the expression is represented and interpreted, for example JSON-LD.

If `expressionSpecification.iri` is mandatory, then `expressionSpecification` itself is necessarily mandatory. The parent object cannot be optional when one of its child fields is required for platform behaviour.

### 4.6 targetEntitySchema rule

For an `ACTIVE` `IntentSpecification`, `targetEntitySchema` is mandatory.

`targetEntitySchema` is the authoritative machine-readable schema reference for validating runtime expression values. For this platform, it defines the allowed shape of:

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

### 4.7 specCharacteristic rule

For an `ACTIVE` `IntentSpecification`, `specCharacteristic` is mandatory.

`specCharacteristic` provides the catalogue-facing and governance-facing view of important supported characteristics. It helps users, experience-layer applications, governance processes, and integration consumers understand what the specification supports.

However, `specCharacteristic` is not the authoritative deep validation schema for the runtime expression body. That role belongs to `targetEntitySchema`.

The preferred pattern is:

- `specCharacteristic` gives discoverable high-level characteristics
- `targetEntitySchema` gives detailed machine validation
- `expressionSpecification.iri` identifies the semantic/expression contract

### 4.8 Lifecycle-aware validation

The platform applies lifecycle-aware validation.

Create and update operations may allow incomplete `DRAFT` resources. Activation to `ACTIVE` must validate the full ACTIVE mandatory profile.

If a client attempts to activate a specification that does not satisfy the ACTIVE profile, the platform must reject the request.

The preferred response is:

```text
422 Unprocessable Entity
```

This means the request is syntactically valid, but the resource cannot transition to the requested lifecycle state because it violates the platform `IntentSpecification` profile.

## 5. Examples

### 5.1 Minimal DRAFT example

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

### 5.2 ACTIVE example excerpt

This example shows the important fields required before activation.

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

### 5.3 Runtime expression relationship example

An active specification defines the semantic contract:

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

A runtime API may choose to make explicit `intentSpecification.id` mandatory, or may choose to resolve the active specification from runtime `expression.iri` when the match is unambiguous. That runtime resolution rule is a separate API decision and is not decided by this specification-profile decision.

## 6. Consequences

### 6.1 Positive consequences

This decision gives the platform:

- deterministic specification identity
- stronger lifecycle governance
- safer activation rules
- reliable runtime expression validation
- clearer runtime resolution behaviour
- better event payload consistency
- clearer separation between TMF base optionality and platform conformance
- better support for catalogue discovery

### 6.2 Trade-offs

This decision also means:

- the platform is stricter than a minimal TMF implementation
- clients must provide more information before a specification can become active
- activation validation becomes more important than simple create validation
- the platform must maintain lifecycle-aware validation rules
- some clients may need to distinguish between creating a draft and publishing an active runtime contract

These trade-offs are acceptable because active specifications are not just catalogue records. They are runtime contract definitions used by intent-processing components.

## 7. Alternatives considered

### 7.1 Treat TMF optional fields as platform optional

This was rejected.

It would make create/update easier, but it would allow active specifications that are not usable for runtime validation or runtime resolution.

### 7.2 Make every useful field mandatory at create time

This was rejected.

It would make the create operation too rigid and would make it harder to incrementally author a specification. The platform should allow controlled incomplete drafts.

### 7.3 Make expressionSpecification.iri mandatory but not expressionSpecification

This was rejected as structurally inconsistent.

A child field cannot be mandatory for platform behaviour while the parent object remains optional. Therefore, if `expressionSpecification.iri` is mandatory, `expressionSpecification` is mandatory too.

### 7.4 Make runtime intentSpecification.id mandatory everywhere

This is deferred to a separate runtime intent API decision.

This decision mandates `id` on every persisted `IntentSpecification`, but runtime submission rules belong to the runtime intent API. A runtime API may still support resolution by runtime `expression.iri` where it is unambiguous.

## 8. Decision outcome

The decision is accepted as the platform `IntentSpecification` mandatory profile baseline.

The platform will document and enforce a lifecycle-aware `IntentSpecification` mandatory profile:

- `DRAFT` requires identity and lifecycle-management fields.
- `ACTIVE` requires the full platform runtime contract profile.
- `id` is mandatory and immutable on persisted resources.
- `expressionSpecification` is mandatory for active resources.
- `expressionSpecification.iri` and `expressionSpecification.expressionLanguage` are mandatory for active resources.
- `targetEntitySchema` and `specCharacteristic` are mandatory for active resources.
- Activation fails if the ACTIVE profile is not satisfied.

## 9. Follow-up work

After this decision is baselined, update the affected architecture and specification artifacts surgically:

- document the platform mandatory profile
- clarify DRAFT versus ACTIVE validation
- clarify `id`, `expressionSpecification`, `expressionSpecification.iri`, and `expressionSpecification.expressionLanguage`
- clarify activation failure behaviour
- reference this decision where the mandatory profile is discussed
- keep runtime request resolution rules separate from this decision unless explicitly baselined in the runtime intent API
