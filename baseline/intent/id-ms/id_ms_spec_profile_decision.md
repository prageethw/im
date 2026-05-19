# IntentSpecification mandatory profile proposal:

## 1. Decision summary:

This proposal defines the minimum mandatory attribute profile for `IntentSpecification` resources on this intent enabler entity, layered on top of TMF921.

TMF921 provides the generic `IntentSpecification` resource model, operation pattern, and event pattern. It does not prescribe the complete mandatory attribute profile required by every implementation.

This intent enabler entity therefore defines a stricter profile so that `IntentSpecification` resources are usable for catalogue governance, lifecycle management, runtime expression validation, and runtime intent resolution.

The key proposals are:

- define the minimum mandatory attributes for a persisted `DRAFT` `IntentSpecification`
- define the minimum mandatory attributes for an `ACTIVE` `IntentSpecification`

This proposal defines a candidate intent enabler entity profile rule. It does not claim that TMF921 universally mandates the same fields for every implementation.

## 2. Proposal flow diagram:

![IntentSpecification mandatory profile proposal](id_ms_spec_profile_decision.svg)

## 3. Context:

TMF921 intentionally leaves implementation flexibility in the `IntentSpecification` model. That is useful for broad interoperability, because different organisations may need different levels of catalogue detail, lifecycle governance, schema discipline, and runtime coupling.

However, for this intent enabler entity, an `IntentSpecification` is not only a descriptive catalogue record. Once active, it becomes a published runtime contract used by downstream consumers to understand, validate, and resolve submitted runtime intents.

If too many fields are treated as optional, downstream runtime behaviour becomes ambiguous.

The intent enabler entity must be able to answer questions such as:

- Which specification defines the submitted runtime expression?
- Which semantic contract does the expression follow?
- Which schema validates the runtime expression body?
- Is the specification active and within its validity period?
- Which version family does this specification belong to?
- Can a runtime intent be resolved by expression IRI when an explicit specification reference is not supplied?
- Can event subscribers interpret specification events without an authoritative resource identity?

Therefore, the intent enabler entity needs a mandatory profile that is stricter than the minimum generic TMF shape.

## 4. Decision drivers:

The proposal is driven by the following architecture needs:

| Driver | Need |
| --- | --- |
| TMF alignment | Use the TMF921 resource model and API/event patterns without inventing an incompatible resource shape. |
| Runtime safety | Prevent activation of specifications that cannot be used for runtime validation or resolution. |
| Governance | Ensure every persisted specification has stable identity, lifecycle status, version identity, and family grouping. |
| Discoverability | Ensure active specifications can be discovered and understood by users, portals, and integration consumers. |
| Validation | Ensure active specifications have a machine-readable validation contract. |
| Semantic clarity | Ensure active specifications identify the semantic/expression contract they support. |
| Evolvability | Allow incomplete drafts while preventing incomplete active contracts. |

## 5. Proposal:

### 5.1 TMF-aligned, not TMF-minimal:

The intent enabler entity remains TMF-aligned by using the TMF921 `IntentSpecification` resource model, including TMF-style identity, lifecycle status, specification characteristics, expression specification, target entity schema, related parties, relationships, and events.

However, the intent enabler entity does not adopt a TMF-minimal interpretation where most fields are treated as operationally optional. Instead, the intent enabler entity applies a mandatory profile appropriate for its runtime architecture.

The rule is:

> TMF-aligned does not mean TMF-minimal.

### 5.2 Minimum mandatory profile by lifecycle state:

This proposal defines different minimum mandatory profiles for `DRAFT` and `ACTIVE`.

A `DRAFT` specification must have enough information to be identified, versioned, edited, governed, and safely transitioned later.

An `ACTIVE` specification must have enough information to act as a published runtime contract for discovery, validation, governance, and runtime resolution.

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
| `expressionSpecification.iri` | Optional | Mandatory | Authoritative semantic/expression contract identifier. |
| `expressionSpecification.expressionLanguage` | Optional | Mandatory | Defines the expression representation and interpretation model. |
| `targetEntitySchema` | Optional | Mandatory | Authoritative validation contract for runtime expression values. |
| `specCharacteristic` | Optional | Mandatory | Catalogue/discovery/governance view of supported characteristics. |
| `@type` | Mandatory | Mandatory | TMF polymorphic resource type. |
| `@baseType` | Mandatory | Mandatory | TMF base type alignment. |

This table is the core architectural proposal.

### 5.3 Persisted resource identity:

`id` is mandatory on every persisted `IntentSpecification` resource.

The create operation may support either of the following patterns:

- the intent enabler entity generates the `id`
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

### 5.4 DRAFT profile:

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

### 5.5 ACTIVE profile:

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

### 5.6 expressionSpecification rule:

For an `ACTIVE` `IntentSpecification`, `expressionSpecification` is mandatory.

Within `expressionSpecification`:

- `iri` is mandatory
- `expressionLanguage` is mandatory

The `iri` identifies the semantic/expression contract. It tells consumers which intent model or expression contract the runtime request follows.

The `expressionLanguage` identifies how the expression is represented and interpreted, for example JSON-LD.

If `expressionSpecification.iri` is mandatory, then `expressionSpecification` itself is necessarily mandatory. The parent object cannot be optional when one of its child fields is required for intent enabler entity behaviour.

### 5.7 targetEntitySchema rule:

For an `ACTIVE` `IntentSpecification`, `targetEntitySchema` is mandatory.

`targetEntitySchema` is the authoritative machine-readable schema reference for validating runtime expression values. For this intent enabler entity, it defines the allowed shape of:

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

### 5.8 specCharacteristic rule:

For an `ACTIVE` `IntentSpecification`, `specCharacteristic` is mandatory.

`specCharacteristic` provides the catalogue-facing and governance-facing view of important supported characteristics. It helps users, experience-layer applications, governance processes, and integration consumers understand what the specification supports.

However, `specCharacteristic` is not the authoritative deep validation schema for the runtime expression body. That role belongs to `targetEntitySchema`.

The preferred pattern is:

- `specCharacteristic` gives discoverable high-level characteristics
- `targetEntitySchema` gives detailed machine validation
- `expressionSpecification.iri` identifies the semantic/expression contract

### 5.9 Lifecycle-aware validation:

The intent enabler entity applies lifecycle-aware validation.

Create and update operations may allow incomplete `DRAFT` resources. Activation to `ACTIVE` must validate the full ACTIVE mandatory profile.

If a client attempts to activate a specification that does not satisfy the ACTIVE profile, the intent enabler entity must reject the request.

The preferred response is:

```text
422 Unprocessable Entity
```

This means the request is syntactically valid, but the resource cannot transition to the requested lifecycle state because it violates the intent enabler entity `IntentSpecification` profile.

## 6. Examples:

The examples use the current hospital surgical-slice payload pattern from the intent enabler entity baseline. The use case represents a hospital requesting a surgical-connectivity service with strict latency, availability, jitter, packet-loss, location, service-class, redundancy, and timing requirements. The examples show why an active `IntentSpecification` needs stable identity, an expression contract IRI, `targetEntitySchema`, and `specCharacteristic` before it can safely govern runtime intent submissions.

### 6.1 DRAFT IntentSpecification create request from the intent enabler entity baseline:

This example uses the current `POST /intentManagement/v5/intentSpecification` request body pattern from the ID MS specification. It shows a draft specification that already carries the expression contract, target entity schema, and discoverable context characteristic, even though the proposal only requires the lighter DRAFT minimum profile.

```json
{
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents.\nThis specification defines the allowed request shape for surgical connectivity intents.\nIt is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
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
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19.schema.json",
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "id": "context",
      "name": "context",
      "description": "Top-level semantic context supported by this IntentSpecification.\nThe context contains canonical context.targets, context.constraints, and context.preferences.\nDetailed field rules are defined in the expression-value schema referenced by targetEntitySchema.@schemaLocation.",
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
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.19.expression.schema.json",
    "schemaVersion": "1.19",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  }
}
```

### 6.2 Persisted DRAFT IntentSpecification response from the intent enabler entity baseline:

This example uses the current `201 Created` response pattern from the ID MS specification. It shows that the client does not send `id` or `href`, but the persisted resource returned by the intent enabler entity has both, which supports the proposal that `id` and `href` are mandatory on persisted resources.

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents.\nThis specification defines the allowed request shape for surgical connectivity intents.\nIt is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
  "version": "1.19",
  "lifecycleStatus": "DRAFT",
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
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19.schema.json",
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "id": "context",
      "name": "context",
      "description": "Top-level semantic context supported by this IntentSpecification.\nThe context contains canonical context.targets, context.constraints, and context.preferences.\nDetailed field rules are defined in the expression-value schema referenced by targetEntitySchema.@schemaLocation.",
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
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.19.expression.schema.json",
    "schemaVersion": "1.19",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  },
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
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but discouraged as a general update method.\nPrefer PUT for deterministic full replacement."
    },
    "delete": {
      "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "DELETE"
    }
  }
}
```

### 6.3 ACTIVE IntentSpecification retrieve response from the intent enabler entity baseline:

This example uses the current `GET /intentSpecification/{id}` success response pattern from the ID MS specification. It shows the active profile fields that must be present for runtime discovery, validation, and resolution.

```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "familyId": "hospital-surgical-slice-spec",
  "name": "Hospital Surgical Slice Intent Specification",
  "description": "Definition-time specification for hospital surgical slice intents.\nThis specification defines the allowed request shape for surgical connectivity intents.\nIt is syntax-first: ID MS validates structure and allowed fields, while II MS and the knowledge plane validate semantic meaning, policy, and fulfilment feasibility.",
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
        "id": "mycsp",
        "name": "MyCSP",
        "@referredType": "Provider"
      }
    }
  ],
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19.schema.json",
  "specCharacteristic": [
    {
      "@type": "CharacteristicSpecification",
      "id": "context",
      "name": "context",
      "description": "Top-level semantic context supported by this IntentSpecification.\nThe context contains canonical context.targets, context.constraints, and context.preferences.\nDetailed field rules are defined in the expression-value schema referenced by targetEntitySchema.@schemaLocation.",
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
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0"
  },
  "targetEntitySchema": {
    "@type": "TargetEntitySchema",
    "@schemaLocation": "https://mycsp.com.au/schemas/intentManagement/v5/intentExpression/hospital-surgical-slice-spec-v1.19.expression.schema.json",
    "schemaVersion": "1.19",
    "schemaHash": "sha256:REPLACE_WITH_PUBLISHED_SCHEMA_HASH"
  },
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
      "method": "PATCH",
      "warning": "PATCH is supported for compatibility but discouraged as a general update method.\nPrefer PUT for deterministic full replacement."
    }
  }
}
```

### 6.4 Runtime Intent request body from the intent enabler entity baseline:

This example uses the current complete `POST /intent` request body pattern from the IC MS specification. It shows how the runtime intent refers to an active specification and uses the same expression IRI and canonical `context.targets`, `context.constraints`, and `context.preferences` shape governed by the active `IntentSpecification`.

```json
{
  "name": "Sydney Hospital Surgical Connection Intent",
  "description": "Request for a surgical connection in Sydney Hospital.",
  "humanExpression": "I need a surgical connection in Sydney Hospital with latency less than or equal to 10 ms and availability at least 99.99%.",
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.20"
  },
  "expression": {
    "@type": "JsonLdExpression",
    "@baseType": "Expression",
    "iri": "https://mycsp.com.au/tio/hospital-surgical-slice/v1.0",
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
  "@baseType": "Entity"
}
```

A runtime API may choose to make explicit `intentSpecification.id` mandatory, or may choose to resolve the active specification from runtime `expression.iri` when the match is unambiguous.

That runtime resolution rule is a separate API decision and is not decided by this specification-profile proposal.


## 7. Consequences:

### 7.1 Positive consequences:

If accepted, this proposal gives the intent enabler entity:

- deterministic specification identity
- stronger lifecycle governance
- safer activation rules
- reliable runtime expression validation
- clearer runtime resolution behaviour
- better event payload consistency
- clearer separation between TMF base optionality and intent enabler entity conformance
- better support for catalogue discovery

### 7.2 Trade-offs:

If accepted, this proposal also means:

- the intent enabler entity is stricter than a minimal TMF implementation
- clients must provide more information before a specification can become active
- activation validation becomes more important than simple create validation
- the intent enabler entity must maintain lifecycle-aware validation rules
- some clients may need to distinguish between creating a draft and publishing an active runtime contract

These trade-offs are acceptable because active specifications are not just catalogue records. They are runtime contract definitions used by intent-processing components.

## 8. Alternatives considered:

### 8.1 Treat TMF optional fields as intent enabler entity optional:

This was rejected.

It would make create/update easier, but it would allow active specifications that are not usable for runtime validation or runtime resolution.

### 8.2 Make every useful field mandatory at create time:

This was rejected.

It would make the create operation too rigid and would make it harder to incrementally author a specification. The intent enabler entity should allow controlled incomplete drafts.

### 8.3 Make expressionSpecification.iri mandatory but not expressionSpecification:

This was rejected as structurally inconsistent.

A child field cannot be mandatory for intent enabler entity behaviour while the parent object remains optional. Therefore, if `expressionSpecification.iri` is mandatory, `expressionSpecification` is mandatory too.

### 8.4 Make runtime intentSpecification.id mandatory everywhere:

This is deferred to a separate runtime intent API decision.

This proposal mandates `id` on every persisted `IntentSpecification`, but runtime submission rules belong to the runtime intent API. A runtime API may still support resolution by runtime `expression.iri` where it is unambiguous.

## 9. Proposal outcome:

This proposal recommends adopting a intent enabler entity `IntentSpecification` mandatory profile baseline.

If accepted, the intent enabler entity will document and enforce a lifecycle-aware `IntentSpecification` mandatory profile:

- `DRAFT` requires identity and lifecycle-management fields.
- `ACTIVE` requires the full intent enabler entity runtime contract profile.
- `id` is mandatory and immutable on persisted resources.
- `expressionSpecification` is mandatory for active resources.
- `expressionSpecification.iri` and `expressionSpecification.expressionLanguage` are mandatory for active resources.
- `targetEntitySchema` and `specCharacteristic` are mandatory for active resources.
- Activation fails if the ACTIVE profile is not satisfied.

## 10. References:

| Reference | URL | Relevance to this proposal |
| --- | --- | --- |
| TMF921 Intent Management API v5.0.0 specification | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Defines the TMF921 Intent Management API and the `IntentSpecification` resource model used as the base for this intent enabler entity profile. |
| TMF921 Intent Management API v5.0.0 OpenAPI / Swagger artefact | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the OpenAPI resource and event schemas used to validate the TMF-facing API shape. |
| TMF921 Intent Management API v5.0.0 conformance profile | https://www.tmforum.org/resources/specification/tmf921-intent-management-api-v5-0-0/ | Provides the TMF conformance context for the API while leaving implementation-specific mandatory profile choices to the intent enabler entity. |
| TR292 TM Forum Intent Ontology (TIO) v3.6.0 | https://www.tmforum.org/resources/standard/tr292-intent-ontology-tio-v3-6-0/ | Provides the intent ontology reference model and model-federation context behind semantic/expression contract identifiers. |
| TR299 Intent Specification | https://www.tmforum.org/resources/standard/tr299-intent-specification/ | Provides the intent specification concept used to describe rules for well-formed intent and allowed intent content. |
| intent enabler entity baseline repository | https://github.com/prageethw/im/tree/main/baseline/intent | Holds the intent enabler entity intent architecture baseline and project-specific specification/profile artefacts. |

## 11. Follow-up work:

After this proposal is reviewed and baselined, update the affected architecture and specification artifacts surgically:

- document the intent enabler entity mandatory profile
- clarify DRAFT versus ACTIVE validation
- clarify `id`, `expressionSpecification`, `expressionSpecification.iri`, and `expressionSpecification.expressionLanguage`
- clarify activation failure behaviour
- reference this proposal where the mandatory profile is discussed
- keep runtime request resolution rules separate from this proposal unless explicitly baselined in the runtime intent API
