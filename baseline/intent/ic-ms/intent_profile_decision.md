# Intent mandatory profile proposal:

## 1. Decision summary:

This proposal defines the minimum mandatory attribute profile for runtime `Intent` resources managed by an intent management entity, layered on top of TMF921.

TMF921 provides the generic runtime `Intent` resource model, operation pattern, and event pattern. It does not prescribe the complete mandatory attribute profile required by every implementation.

This proposal defines a stricter and lifecycle-aware profile so that runtime `Intent` resources can be admitted, validated, resolved against an active `IntentSpecification`, traced, versioned, audited, and projected through lifecycle states.

The key proposals are:

- define the minimum mandatory attributes for a runtime `Intent` create request
- define the minimum mandatory attributes for a persisted/admitted `Intent` response
- keep the minimum mandatory profile separate from optional intent-management-entity governed enrichment fields

This proposal defines a candidate intent management entity profile rule. It does not claim that TMF921 universally mandates the same fields for every implementation.
## 2. Proposal flow diagram:

![Intent mandatory profile proposal](intent_profile_decision.svg)

## 2. Context:

An `IntentSpecification` defines the reusable contract. A runtime `Intent` is a concrete request submitted against that contract, either by explicit reference to an `IntentSpecification` or by an expression IRI that can be resolved to one active specification.

The create request must contain enough machine-readable information to resolve and validate the runtime request. The persisted/admitted `Intent` must contain enough information to trace the request, audit the decision, project lifecycle state, and support later version or update handling.

The intent management entity must be able to answer questions such as:

- What did the requester ask for?
- Which expression contract does the runtime expression follow?
- Which active `IntentSpecification` governed admission and validation?
- What lifecycle state was projected externally?
- What version of the runtime `Intent` is currently represented?
- Can the request be traced back to a human-readable business statement?
- Can downstream consumers interpret the request without re-resolving ambiguous context?

## 3. Decision drivers:

| **Driver** | **Need** |
| --- | --- |
| Runtime admission safety | Ensure create requests contain enough machine-readable content to validate the runtime intent. |
| Specification resolution | Support explicit `intentSpecification.id` where supplied, or unambiguous resolution by `expression.iri` where omitted. |
| Traceability | Persist the resolved `intentSpecification.id` and lifecycle metadata after admission. |
| Human readability | Strongly encourage `humanExpression` so operators and auditors can quickly understand the business request. |
| Lifecycle projection | Ensure persisted intents expose lifecycle state, status reason, and status change time. |
| Version governance | Ensure persisted intents expose the projected runtime version. |
| TMF alignment | Stay aligned to the TMF921 resource model while applying a stricter implementation profile where needed. |

## 4. Proposal:

### 4.1 TMF-aligned, not TMF-minimal:

The intent management entity remains TMF-aligned by using the TMF921 runtime `Intent` resource model and operation pattern.

However, the intent management entity does not treat all optional-looking fields as operationally optional. A runtime intent must be complete enough to be admitted, validated, traced, and lifecycle-projected.

The rule is:

> TMF-aligned does not mean TMF-minimal.

### 4.2 Minimum mandatory profile by operation/state:

| **Field** | **Create request** | **Persisted/admitted response** | **Reason** |
| --- | --- | --- | --- |
| `id` | Not required | Mandatory | Generated or assigned persisted resource identity. |
| `href` | Not required | Mandatory | Canonical resource URL for TMF-style navigation and references. |
| `name` | Mandatory | Mandatory | Human-readable runtime intent name. |
| `version` | Not required | Mandatory | Projected runtime intent version. |
| `lifecycleStatus` | Not required | Mandatory | Externally visible lifecycle projection. |
| `statusReason` | Not required | Mandatory | Human-readable reason for the projected lifecycle status. |
| `statusChangeDate` | Not required | Mandatory | Timestamp of the latest lifecycle/status projection. |
| `intentSpecification.id` | Strongly recommended | Mandatory | Explicit or resolved active specification that governed admission. |
| `humanExpression` | Strongly recommended | Strongly recommended | Improves audit, triage, and human interpretation, but is not machine-authoritative. |
| `expression` | Mandatory | Mandatory | Runtime expression object. |
| `expression.@type` | Mandatory | Mandatory | Identifies the expression representation type. |
| `expression.iri` | Mandatory | Mandatory | Authoritative semantic/expression contract identifier. |
| `expression.expressionValue` | Mandatory | Mandatory | Machine-authoritative runtime intent content. |
| `@type` | Mandatory | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | Mandatory | TMF base type alignment. |

This table is the core architectural proposal.

### 4.3 Create request profile:

The minimum create request must include:

- `name`
- `expression`
- `expression.@type`
- `expression.iri`
- `expression.expressionValue`
- `@type`
- `@baseType`

The create request should strongly include:

- `humanExpression`
- `intentSpecification.id`

`humanExpression` is strongly recommended because it improves human traceability, auditability, triage, and business-level interpretation. It is not mandatory because the authoritative validation input is the structured expression.

`intentSpecification.id` is strongly recommended because it removes resolution ambiguity, improves traceability, and allows faster interpretation by operators and downstream systems. It is not mandatory because the intent management entity can resolve the applicable active `IntentSpecification` using `expression.iri` **when there is exactly one active match**.

### 4.4 IntentSpecification resolution rule:

`expression.iri` is **mandatory** in runtime create and update requests.

`intentSpecification.id` is optional in the create request.

If `intentSpecification.id` is supplied:

- it is authoritative
- the referenced `IntentSpecification` must exist
- the referenced `IntentSpecification` must be active
- the runtime `expression.iri` must be consistent with the specification's `expressionSpecification.iri`

If `intentSpecification.id` is omitted:

- the intent management entity resolves the applicable active `IntentSpecification` using `expression.iri`
- if exactly one active `IntentSpecification` matches, the request may be admitted
- if zero active specifications match, the request must be rejected
- if multiple active specifications match, the request must be **rejected** and the requester must supply `intentSpecification.id`

After successful admission, `intentSpecification.id` becomes mandatory on the persisted `Intent` representation because the intent management entity must record which active specification governed validation and admission.

### 4.5 Persisted/admitted response profile:

A persisted/admitted `Intent` response must include:

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

The persisted response may include strongly recommended or optional fields where supplied or derived, such as:

- `humanExpression`
- `description`
- `validFor`
- `relatedParty`
- `priority`
- `isBundle`
- `_links`

### 4.6 Lifecycle and version projection profile:

The top-level `Intent.lifecycleStatus` is the externally visible lifecycle projection for the runtime `Intent` resource.

The persisted `version` is the projected runtime version shown to external consumers.

Internal version history may be richer than the external projection. The intent management entity may retain version-level lifecycle state, standby versions, failed versions, rejected versions, and administrative archival state internally or expose them through a documented reporting or history mechanism.

The profile avoids using ambiguous pointer names such as `effectiveVersion` or `currentVersion`. Where a pointer is needed to identify the version driving the external projection, use `activeVersion`.

### 4.7 Recommended but not minimum mandatory fields:

| **Field** | **Proposed classification** | **Reason** |
| --- | --- | --- |
| `humanExpression` | **Strongly recommended** | Improves human traceability, auditability, triage, and business-level interpretation. |
| `intentSpecification.id` in create request | **Strongly recommended** | Removes ambiguity and speeds validation/interpretation where the requester knows the active specification. |
| `description` | Optional | Useful for extra human-readable context. |
| `validFor.startDateTime` | Optional / intent-management-entity governed | Useful when the runtime intent should be valid from a specific time. |
| `isBundle` | Optional / intent-management-entity governed | Useful where bundled intent behaviour is supported. |
| `priority` | Optional / intent-management-entity governed | Useful where priority is handled as policy or operational guidance. |
| `relatedParty` | Optional / intent-management-entity governed | Useful for requester, customer, or provider attribution. |
| `_links` | Optional / intent-management-entity governed | Useful for discoverable operation affordances. |

## 5. Examples:

The examples use a hospital surgical-connectivity scenario only to make the profile concrete. The minimal examples intentionally include only the fields needed to demonstrate the proposed create-request and persisted-response profiles, not complete API payloads. The fuller example then shows how strongly recommended and optional fields may be added for traceability, auditability, and richer implementation-specific governance.

### 5.1 Minimal create request and admitted response:

This example proves the minimum machine-readable create request. It omits `intentSpecification.id` to show that the intent management entity may resolve the active specification from `expression.iri`.

```http
POST /intentManagement/v5/intent
Content-Type: application/json
Accept: application/json
```

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
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

The response persists generated identity, projected lifecycle state, projected version, status metadata, and the resolved active specification reference.

```http
HTTP/1.1 201 Created
Location: /intentManagement/v5/intent/INT-HOSP-2026-001
Content-Type: application/json
ETag: "intent-INT-HOSP-2026-001-v1"
```

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "version": "v1",
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Intent request accepted for validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
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

### 5.2 Recommended create request with traceability fields:

This example shows the preferred create request shape where the requester supplies both strongly recommended fields: `humanExpression` and `intentSpecification.id`.

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

### 5.3 Fuller illustrative example with optional fields:

This example shows how an implementation can add optional fields for richer traceability, requester attribution, validity timing, prioritisation, and operation affordances. These fields are useful, but they are not all part of the generic minimum mandatory create-request profile.

```json
{
  "id": "INT-HOSP-2026-001",
  "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "version": "v1",
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Intent request accepted for validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20",
    "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.20"
  },
  "isBundle": false,
  "priority": "critical",
  "relatedParty": [
    {
      "@type": "RelatedPartyRefOrPartyRoleRef",
      "role": "requester",
      "partyOrPartyRole": {
        "@type": "PartyRoleRef",
        "id": "hospital-ops",
        "name": "Hospital Operations",
        "@referredType": "Customer"
      }
    }
  ],
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://example.com/tio/hospital-surgical-slice/v1.0",
    "expressionValue": {
      "context": {
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
  },
  "validFor": {
    "startDateTime": "2026-04-18T12:00:00+10:00"
  },
  "@type": "Intent",
  "@baseType": "Entity",
  "_links": {
    "self": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
    },
    "partialUpdate": {
      "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
      "method": "PATCH"
    }
  }
}
```

## 6. Consequences:

### 6.1 Positive consequences:

If accepted, this proposal gives the intent management entity:

- deterministic runtime admission inputs
- support for both explicit and IRI-based specification resolution
- stronger traceability after admission
- clearer distinction between machine-authoritative fields and human-readable helper fields
- lifecycle projection consistency
- improved audit and operational triage
- cleaner separation between minimum mandatory fields and optional enrichment

### 6.2 Trade-offs:

If accepted, this proposal also means:

- requesters can submit a minimal machine-readable intent without `humanExpression` or `intentSpecification.id`
- the intent management entity must handle unambiguous resolution by `expression.iri`
- persisted responses must include resolved specification identity after admission
- operators get better traceability when requesters provide strongly recommended fields, but cannot rely on those fields always being present in the create request

These trade-offs are acceptable because create requests should remain interoperable while persisted/admitted resources must be deterministic and traceable.

## 7. Alternatives considered:

### 7.1 Make `intentSpecification.id` mandatory in every create request:

This was rejected.

It would make validation deterministic, but it would remove the useful runtime pattern where a requester submits a valid expression identified by `expression.iri` and lets the intent management entity resolve the active specification when the match is unambiguous.

### 7.2 Make `humanExpression` mandatory:

This was rejected.

`humanExpression` is valuable for traceability and human interpretation, but it is not machine-authoritative. Making it mandatory would make the API harder to use without improving machine validation.

### 7.3 Allow create request without `expression.iri`:

This was rejected.

`expression.iri` is the runtime discriminator for the semantic/expression contract. Without it, the intent management entity cannot safely resolve the applicable active specification or validate the expression.

## 8. Proposal outcome:

This proposal recommends adopting a runtime `Intent` mandatory profile baseline.

If accepted, the intent management entity will document and enforce a lifecycle-aware runtime `Intent` profile:

- create requests require `name`, `expression`, `expression.@type`, `expression.iri`, `expression.expressionValue`, `@type`, and `@baseType`
- create requests strongly recommend `humanExpression` and `intentSpecification.id`
- persisted/admitted responses require generated identity, lifecycle projection metadata, resolved `intentSpecification.id`, expression fields, `@type`, and `@baseType`
- `intentSpecification.id` is optional in the create request but mandatory in the persisted/admitted response after resolution
- `expression.iri` is mandatory and is the default runtime validation discriminator where `intentSpecification.id` is omitted

## 9. References:

| **Reference** | **URL** | **Relevance to this proposal** |
| --- | --- | --- |
| TMF921 Intent Management API v5.0.0 specification | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Defines the TMF921 Intent Management API and runtime `Intent` resource model. |
| TMF921 Intent Management API v5.0.0 OpenAPI / Swagger artefact | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the OpenAPI resource and event schemas used to validate the TMF-facing API shape. |
| TMF921 Intent Management API v5.0.0 conformance profile | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the TMF conformance context while leaving implementation-specific mandatory profile choices to the intent management entity. |
| TR292 TM Forum Intent Ontology (TIO) v3.6.0 | https://www.tmforum.org/resources/standard/tr292-intent-ontology-tio-v3-6-0/ | Provides the intent ontology reference model and model-federation context behind semantic/expression contract identifiers. |
| TR299 Intent Specification | https://www.tmforum.org/resources/standard/tr299-intent-specification/ | Provides the intent specification concept used to describe rules for well-formed intent and allowed intent content. |
| Intent architecture baseline repository | https://github.com/prageethw/im/tree/main/baseline/intent | Holds the intent architecture baseline and project-specific profile artefacts. |

## 10. Follow-up work:

After this proposal is reviewed and baselined, update the affected architecture and specification artifacts surgically:

- document the runtime `Intent` mandatory profile
- clarify create request minimum mandatory fields
- clarify strongly recommended `humanExpression` and `intentSpecification.id`
- clarify persisted/admitted response mandatory fields
- clarify `intentSpecification.id` resolution and persistence behaviour
- keep runtime version/lifecycle profile wording aligned with the existing `activeVersion` baseline
