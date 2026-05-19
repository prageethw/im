# ID MS IntentSpecification mandatory profile decision

## 1. Decision summary

ID MS defines a platform-specific mandatory profile for `IntentSpecification`, layered on top of TMF921.

TMF921 provides the generic `IntentSpecification` resource model, operation pattern, and event pattern, but it does not prescribe the complete mandatory attribute profile required by every implementation. This platform therefore defines a stricter ID MS profile so that `IntentSpecification` resources are usable for catalogue governance, lifecycle management, runtime expression validation, and IC MS resolution.

The key decision is:

- TMF921 alignment is the base model.
- ID MS platform conformance defines the mandatory profile.
- `DRAFT` specifications may be incomplete within controlled limits.
- `ACTIVE` specifications must be complete enough to be safely discovered, governed, resolved, and used by runtime Intent processing.
- `id` is mandatory on every persisted `IntentSpecification` resource.
- `expressionSpecification` is mandatory for an `ACTIVE` `IntentSpecification`.
- `expressionSpecification.iri` is mandatory inside `expressionSpecification` and is the authoritative semantic/expression contract identifier.
- `expressionSpecification.expressionLanguage` is mandatory inside `expressionSpecification` so consumers know how the expression is represented and interpreted.

This decision is an ID MS platform rule. It does not claim that TMF921 universally mandates the same fields for every implementation.

## 2. Problem

TMF921 intentionally leaves implementation flexibility in the `IntentSpecification` model. That is useful for broad interoperability, but it creates an architectural gap for this platform.

If ID MS treats too many `IntentSpecification` attributes as optional, downstream services cannot reliably answer basic runtime questions:

- Which specification defines the submitted runtime expression?
- Which semantic contract does the expression follow?
- Which schema validates the allowed runtime expression body?
- Is the specification active and within its validity period?
- Which version family does this specification belong to?
- Can IC MS resolve an `IntentSpecification` when a runtime request supplies only `expression.iri`?
- Can subscribers interpret ID MS events without an authoritative resource identity?

Therefore, the platform needs a mandatory profile that is stricter than the minimum generic TMF shape.

## 3. Decision

### 3.1 TMF-aligned, not TMF-minimal

ID MS remains TMF-aligned by using the TMF921 `IntentSpecification` resource model, including the TMF-style API, resource identity, lifecycle status, specification characteristics, expression specification, target entity schema, related party, relationships, and TMF-style events.

However, ID MS does not adopt a TMF-minimal interpretation where most fields are treated as operationally optional. Instead, ID MS applies a platform-specific mandatory profile.

The rule is:

> TMF-aligned does not mean TMF-minimal.

### 3.2 Persisted resource identity

`id` is mandatory on every persisted `IntentSpecification` resource.

The create operation may support either of the following patterns:

- ID MS generates the `id`.
- An authorised platform client supplies the `id`, subject to governance rules.

After creation, `id` is immutable.

`id` must be present in:

- retrieve responses
- list responses
- update responses
- delete precondition evaluation
- ID MS external event payloads
- internal references from other services

`href` is also mandatory on persisted and returned resources because it provides the canonical resource URL for TMF-style navigation and event references.

### 3.3 DRAFT profile

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

`DRAFT` may omit fields that are required later for activation, such as `targetEntitySchema`, complete `specCharacteristic`, or complete `expressionSpecification`, provided the resource is not activated until the ACTIVE profile is satisfied.

### 3.4 ACTIVE profile

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
| `validFor.startDateTime` | Yes | Defines when the ACTIVE contract becomes valid. |
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

These fields are not universally mandatory for every ACTIVE specification unless a specific use case or governance rule requires them.

### 3.5 expressionSpecification rule

For an `ACTIVE` `IntentSpecification`, `expressionSpecification` is mandatory.

Within `expressionSpecification`:

- `iri` is mandatory.
- `expressionLanguage` is mandatory.

The `iri` identifies the semantic/expression contract. It tells consumers which intent model or expression contract the runtime request follows.

The `expressionLanguage` identifies how the expression is represented and interpreted, for example JSON-LD.

If `expressionSpecification.iri` is mandatory, then `expressionSpecification` itself is necessarily mandatory. The parent object cannot be optional when one of its child fields is required for platform behaviour.

### 3.6 targetEntitySchema rule

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

### 3.7 specCharacteristic rule

For an `ACTIVE` `IntentSpecification`, `specCharacteristic` is mandatory.

`specCharacteristic` provides the catalogue-facing and governance-facing view of important supported characteristics. It helps users, OEX, governance processes, and integration consumers understand what the specification supports.

However, `specCharacteristic` is not the authoritative deep validation schema for the runtime expression body. That role belongs to `targetEntitySchema`.

The preferred pattern is:

- `specCharacteristic` gives discoverable high-level characteristics.
- `targetEntitySchema` gives detailed machine validation.
- `expressionSpecification.iri` identifies the semantic/expression contract.

### 3.8 Lifecycle-aware validation

ID MS applies lifecycle-aware validation.

Create and update operations may allow incomplete `DRAFT` resources. Activation to `ACTIVE` must validate the full ACTIVE mandatory profile.

If a client attempts to activate a specification that does not satisfy the ACTIVE profile, ID MS must reject the request.

The preferred response is:

```text
422 Unprocessable Entity
```

This means the request is syntactically valid, but the resource cannot transition to the requested lifecycle state because it violates the platform `IntentSpecification` profile.

### 3.9 Runtime relationship to IC MS

This decision applies to ID MS and the `IntentSpecification` catalogue.

It does not by itself decide whether runtime `Intent.intentSpecification.id` is mandatory on every IC MS request. That is an IC MS runtime request decision and should be covered in a separate IC MS decision paper.

The current intended relationship is:

- Every ACTIVE `IntentSpecification` in ID MS has a mandatory `id`.
- Every ACTIVE `IntentSpecification` in ID MS has a mandatory `expressionSpecification.iri`.
- Runtime `Intent.intentSpecification.id` may be optional if IC MS supports resolution by `Intent.expression.iri`.
- If runtime `intentSpecification.id` is supplied, it is authoritative.
- If runtime `intentSpecification.id` is omitted, IC MS resolves the ACTIVE specification using runtime `expression.iri`.
- If zero or multiple ACTIVE specifications match the runtime `expression.iri`, IC MS rejects the request and requires explicit `intentSpecification.id`.

This keeps the ID MS catalogue strong while allowing controlled runtime flexibility.

## 4. Examples

### 4.1 Minimal DRAFT example

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

### 4.2 ACTIVE example excerpt

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

### 4.3 Runtime expression relationship example

An ACTIVE specification defines the semantic contract:

```json
{
  "expressionSpecification": {
    "expressionLanguage": "JSON-LD",
    "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
  }
}
```

A runtime Intent can then use the corresponding expression IRI:

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

If the runtime request omits `intentSpecification.id`, IC MS may use this runtime `expression.iri` to resolve the ACTIVE `IntentSpecification`, subject to the separate IC MS resolution decision.

## 5. Consequences

### 5.1 Positive consequences

This decision gives the platform:

- deterministic specification identity
- stronger lifecycle governance
- safer activation rules
- reliable runtime expression validation
- clearer IC MS resolution behaviour
- better event payload consistency
- clearer separation between TMF base optionality and platform conformance
- better support for OEX and catalogue discovery

### 5.2 Trade-offs

This decision also means:

- ID MS is stricter than a minimal TMF implementation.
- Clients must provide more information before a specification can become ACTIVE.
- Activation validation becomes more important than simple create validation.
- ID MS must maintain lifecycle-aware validation rules.
- Some clients may need to distinguish between creating a draft and publishing an active runtime contract.

These trade-offs are acceptable because ACTIVE specifications are not just catalogue records. They are runtime contract definitions used by IC MS and downstream intent-processing services.

## 6. Alternatives considered

### 6.1 Treat TMF optional fields as platform optional

This was rejected.

It would make create/update easier, but it would allow ACTIVE specifications that are not usable for runtime validation or IC MS resolution.

### 6.2 Make every useful field mandatory at create time

This was rejected.

It would make the create operation too rigid and would make it harder to incrementally author a specification. The platform should allow controlled incomplete drafts.

### 6.3 Make expressionSpecification.iri mandatory but not expressionSpecification

This was rejected as structurally inconsistent.

A child field cannot be mandatory for platform behaviour while the parent object remains optional. Therefore, if `expressionSpecification.iri` is mandatory, `expressionSpecification` is mandatory too.

### 6.4 Make runtime intentSpecification.id mandatory everywhere

This is deferred to the IC MS decision paper.

ID MS mandates `id` on every persisted specification, but runtime submission rules belong to IC MS. IC MS may still support resolution by runtime `expression.iri` where it is unambiguous.

## 7. Decision outcome

The decision is accepted as the ID MS platform profile baseline.

ID MS will document and enforce a lifecycle-aware `IntentSpecification` mandatory profile:

- `DRAFT` requires identity and lifecycle-management fields.
- `ACTIVE` requires the full platform runtime contract profile.
- `id` is mandatory and immutable on persisted resources.
- `expressionSpecification` is mandatory for ACTIVE resources.
- `expressionSpecification.iri` and `expressionSpecification.expressionLanguage` are mandatory for ACTIVE resources.
- `targetEntitySchema` and `specCharacteristic` are mandatory for ACTIVE resources.
- Activation fails if the ACTIVE profile is not satisfied.

## 8. Follow-up work

After this decision is baselined, update the ID MS artifacts surgically:

- `id_ms_specification.md`
  - Add or refine the platform mandatory profile section.
  - Clarify DRAFT versus ACTIVE validation.
  - Clarify `id`, `expressionSpecification`, `expressionSpecification.iri`, and `expressionSpecification.expressionLanguage`.
  - Clarify activation failure behaviour.

- `id_ms_solution_brief.md`
  - Reference the decision at a high level.
  - Explain why ID MS applies a stronger platform profile than base TMF optionality.

- `id_ms_design_brief.md`
  - Reference the lifecycle-aware validation model.
  - Clarify activation gate responsibilities.

A separate IC MS decision paper should cover runtime request resolution rules, including whether runtime `intentSpecification.id` is optional or mandatory, and when resolution by `expression.iri` is allowed.
