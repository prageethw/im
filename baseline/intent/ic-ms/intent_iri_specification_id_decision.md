# TAF - Runtime Intent contract reference decision

| **Document status** | **Value** |
| --- | --- |
| Status | Accepted baseline decision |
| Scope | Runtime Intent admission contract reference rule |
| Primary focus | Whether runtime Intent admission should require `expression.iri`, `intentSpecification.id`, or both |
| Out of scope | Full runtime lifecycle design, Draft authoring details, internal version-history design, implementation routing details |
| Source of truth after commit | GitHub `baseline/intent/ic-ms/intent_iri_specification_id_decision.md` |

## Table of contents:

- [1. Decision summary:](#1-decision-summary)
- [2. Decision flow diagram:](#2-decision-flow-diagram)
- [3. Context:](#3-context)
- [4. Decision drivers:](#4-decision-drivers)
- [5. Options considered:](#5-options-considered)
  - [5.1. Rejected option: expression.iri-only admission:](#51-rejected-option-expressioniri-only-admission)
  - [5.2. Use intentSpecification.id only:](#52-use-intentspecificationid-only)
  - [5.3. Require both intentSpecification.id and expression.iri:](#53-require-both-intentspecificationid-and-expressioniri)
- [6. Decision:](#6-decision)
- [7. Validation rule:](#7-validation-rule)
- [8. Examples:](#8-examples)
  - [8.1. Valid admission request:](#81-valid-admission-request)
  - [8.2. Rejected request when intentSpecification.id is missing:](#82-rejected-request-when-intentspecificationid-is-missing)
  - [8.3. Rejected request when IRI does not match the specification:](#83-rejected-request-when-iri-does-not-match-the-specification)
- [9. Consequences:](#9-consequences)
  - [9.1. Positive consequences:](#91-positive-consequences)
  - [9.2. Trade-offs:](#92-trade-offs)
- [10. Decision outcome:](#10-decision-outcome)
- [11. References:](#11-references)
- [12. Follow-up work:](#12-follow-up-work)

## 1. Decision summary:

This decision records how a runtime `Intent` admission request identifies the governing runtime contract.

The decision is:

> Runtime Intent admission requires both `intentSpecification.id` and `expression.iri`.

The two fields serve different purposes:

| **Field** | **Purpose** |
| --- | --- |
| `intentSpecification.id` | Selects the exact platform-managed `IntentSpecification` resource used for validation, governance, lifecycle, and audit. |
| `expression.iri` | Identifies the semantic/expression contract that the runtime expression claims to follow. |

`expression.iri` alone is not sufficient for admission because the same IRI may be referenced by multiple `ACTIVE` `IntentSpecification` resources.

`intentSpecification.id` alone is not sufficient because the runtime expression still needs to declare the semantic/expression contract it follows, and the intent management entity must verify consistency between the runtime expression and the selected specification.

Draft creation remains lighter and does not require either field. This decision applies when a Draft is moved into admission or when a new runtime Intent is created directly for admission.

## 2. Decision flow diagram:

![Intent mandatory iri vs spec.id decision](intent_iri_specification_id_decision.svg)


## 3. Context:

A runtime `Intent` carries structured expression content in `expression.expressionValue`.

The interpretation of that content depends on the semantic/expression contract identified by `expression.iri`.

Separately, the intent management entity owns concrete `IntentSpecification` resources. These resources carry lifecycle state, version identity, governance metadata, validation schema, catalogue characteristics, and expression specification metadata.

Because these are different concepts, a runtime admission request needs both:

- the exact platform resource to use: `intentSpecification.id`
- the semantic contract identifier to check: `expression.iri`

The same `expression.iri` can be used by multiple `IntentSpecification` resources. For example, several active specifications may share the same semantic model but differ by product profile, validation schema, policy, lifecycle governance, target market, or implementation-specific constraints.

Therefore, allowing runtime admission by IRI alone can be ambiguous.

The baseline surgical hospital slice is an illustrative runtime example used to make the IC MS contract concrete. It is not the only supported runtime Intent type, IntentSpecification, service class, schema, expression IRI, location, service type, or deployment profile. Other runtime Intents may use different targets, constraints, preferences, expression schemas, service types, priorities, and governance profiles while following the same IC MS contract rules.

## 4. Decision drivers:

| **Driver** | **Need** |
| --- | --- |
| Deterministic admission | IC MS must know the exact `ACTIVE` `IntentSpecification` governing the request. |
| Semantic consistency | The runtime `expression.iri` must match the selected specification's `expressionSpecification.iri`. |
| Auditability | Persisted Intents must show which specification governed admission and which semantic contract was claimed. |
| Runtime safety | Avoid accidental admission against the wrong active specification when multiple specifications share the same IRI. |
| Operator clarity | Operators should not need to infer which specification was selected from IRI alone. |
| TMF alignment | Remain aligned with TMF-style resource references while applying a stricter intent management entity profile. |

## 5. Options considered:

### 5.1. Rejected option: expression.iri-only admission:

This option makes `expression.iri` the only mandatory contract reference in runtime admission.

It was rejected, as it is alone not sufficient.

Although `expression.iri` identifies the semantic/expression contract, it does not uniquely select a platform-managed `IntentSpecification` resource.

Problems:

- multiple active specifications may reference the same IRI
- product/profile/version selection becomes ambiguous
- IC MS may need hidden resolution logic
- audit trails become harder to explain
- adding a second active specification with the same IRI can change runtime admission behaviour

### 5.2. Use intentSpecification.id only:

This option makes `intentSpecification.id` mandatory but does not require `expression.iri`.

It was rejected, as it is alone not sufficient.

`intentSpecification.id` selects the platform-managed specification, but the runtime expression still needs to state which semantic/expression contract it claims to follow.

Problems:

- the request does not self-declare the expression contract
- downstream processors lose a direct semantic discriminator
- IC MS cannot check that the runtime expression IRI and selected specification IRI are consistent
- the expression body becomes less portable and less self-describing

### 5.3. Require both intentSpecification.id and expression.iri:

This option makes both fields mandatory for runtime admission.

It is the accepted option.

Benefits:

- `intentSpecification.id` selects the exact active platform specification
- `expression.iri` identifies the semantic/expression contract
- IC MS can validate that both are consistent
- audit records contain both the platform governance reference and the semantic contract reference
- no ambiguous active-specification resolution is needed during admission

## 6. Decision:

Runtime `Intent` admission requires:

- `intentSpecification.id`
- `expression.iri`

Both must be present.

Both must be consistent.

The admission request is rejected if:

- `intentSpecification.id` is missing
- `expression.iri` is missing
- the referenced `IntentSpecification` does not exist
- the referenced `IntentSpecification` is not active
- `expression.iri` does not match the referenced `IntentSpecification.expressionSpecification.iri`

Draft creation is not affected by this decision. Draft creation may omit both fields because Draft is not admitted into runtime processing.

## 7. Validation rule:

The validation rule is:

```text
1. Read intentSpecification.id from the admission request.
2. Retrieve the referenced IntentSpecification.
3. Verify lifecycleStatus = ACTIVE.
4. Read expression.iri from the admission request.
5. Compare expression.iri with IntentSpecification.expressionSpecification.iri.
6. Reject the request if either value is missing or the values do not match.
7. Continue admission validation only after the reference and IRI consistency check passes.
```

This means the intent management entity does not infer the governing runtime contract from `expression.iri` alone.

## 8. Examples:

### 8.1. Valid admission request:

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec"
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

This request is valid only if `ispec-hss-001` resolves to an active `IntentSpecification` version, for example version `1.20`, and its `expressionSpecification.iri` equals. The version is resolved from the selected specification and is not required in the request JSON because `intentSpecification.id` is the authoritative runtime contract selector.

```text
https://example.com/tio/hospital-surgical-slice/v1.0
```

### 8.2. Rejected request when intentSpecification.id is missing:

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "expression": {
    "@type": "JsonLdExpression",
    "iri": "https://example.com/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {}
    }
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

Rejected because `intentSpecification.id` is mandatory for admission.

Suggested error reason:

```text
MISSING_INTENT_SPECIFICATION_ID
```

### 8.3. Rejected request when IRI does not match the specification:

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "intentSpecification": {
    "id": "ispec-hss-001",
    "specKey": "hospital-surgical-slice-spec"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "iri": "https://example.com/tio/another-contract/v1.0",
    "expressionValue": {
      "context": {}
    }
  },
  "@type": "Intent",
  "@baseType": "Entity"
}
```

Rejected because the runtime `expression.iri` does not match the selected specification's `expressionSpecification.iri`.

Suggested error reason:

```text
INTENT_EXPRESSION_IRI_MISMATCH
```

## 9. Consequences:

### 9.1. Positive consequences:

- Admission is deterministic.
- IC MS does not need ambiguous active-specification resolution by IRI alone.
- Runtime requests remain self-describing through `expression.iri`.
- Persisted Intents have stronger traceability.
- Operators can see both the governing specification and semantic contract.
- Future introduction of multiple active specifications with the same IRI does not change admission behaviour.

### 9.2. Trade-offs:

- Requesters must know the active `IntentSpecification.id` before admission.
- OEX or catalogue discovery becomes more important.
- Clients cannot submit admission requests by semantic IRI alone.
- More validation is required at admission time.

These trade-offs are acceptable because they remove ambiguity from runtime admission and make audit/governance stronger.

## 10. Decision outcome:

This decision establishes the following baseline:

- Draft creation does not require `intentSpecification.id` or `expression.iri`.
- Runtime Intent admission requires `intentSpecification.id`.
- Runtime Intent admission requires `expression.iri`.
- IC MS retrieves the `ACTIVE` `IntentSpecification` by `intentSpecification.id`.
- IC MS rejects admission if `expression.iri` does not match `IntentSpecification.expressionSpecification.iri`.
- Persisted Intent responses after admission include both the selected `intentSpecification.id` and the runtime `expression.iri`.

## 11. References:

| **Reference** | **URL** | **Relevance to this decision** |
| --- | --- | --- |
| TMF921 Intent Management API v5.0.0 specification | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Defines the TMF921 Intent Management API and runtime `Intent` and `IntentSpecification` resource model used as the base for this profile decision. |
| TR292 TM Forum Intent Ontology (TIO) v3.6.0 | https://www.tmforum.org/resources/standard/tr292-intent-ontology-tio-v3-6-0/ | Provides the intent ontology and semantic-model background behind expression contract identifiers. |
| TR299 Intent Specification | https://www.tmforum.org/resources/standard/tr299-intent-specification/ | Provides the intent specification concept used to define rules for well-formed intent and allowed intent content. |
| Intent architecture baseline repository | https://github.com/prageethw/im/tree/main/baseline/intent | Holds the intent architecture baseline and project-specific profile artefacts. |

## 12. Follow-up work:

The follow-up work for this accepted baseline decision is resolved in the current IC MS baseline. The affected profile paper, IC MS specification, solution brief, and related diagrams have been aligned so runtime admission requires both `intentSpecification.id` and `expression.iri`, and IRI-only admission is not used as a governing contract-selection rule.
