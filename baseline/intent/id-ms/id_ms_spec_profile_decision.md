# IntentSpecification profile decision

| **Document status** | **Value** |
| --- | --- |
| Status | Proposed decision paper |
| Scope | Intent Definition MS `IntentSpecification` definition profile |
| Primary focus | `specKey`, `draftId`, DRAFT candidate creation, activation, official version assignment, ACTIVE and RETIRED immutability |
| Source of truth after commit | GitHub `baseline/intent/id-ms/id_ms_spec_profile_decision.md` |

## 1. Decision summary:

ID MS should follow the same definition-candidate logic used for optimiser definitions. `IntentSpecification` is a governed definition-time contract. Creation creates a mutable DRAFT candidate, not an official runtime-usable version.

Core identity model:

```text
specKey -> stable logical key supplied by the caller
id -> stable server-assigned IntentSpecification lineage resolved from specKey
draftId -> server-assigned mutable DRAFT candidate selector
version -> official public version assigned only when a selected DRAFT is activated
```

`id` is server-assigned and stable for the official specification lineage. It must not be assumed to equal `specKey`; examples use `id: ispec-hss-001` and `specKey: hospital-surgical-slice-spec` where the distinction matters.

## 2. Create request profile:

`POST /intentSpecification` creates a mutable DRAFT candidate only.

Required create fields:

```text
specKey
name
expressionSpecification
targetEntitySchema
@type
```

Recommended create fields:

```text
description
validFor
isBundle
specCharacteristic[]
relatedParty[]
@baseType
@schemaLocation
```

Client create requests must not provide:

```text
id
href
draftId
version
lifecycleStatus
creationDate
lastUpdate
statusChangeDate
Location
ETag
_links
```

If `isBundle` is omitted on create, ID MS defaults it to `false`.

## 3. DRAFT candidate response profile:

A successful create response must include the server-resolved identity and DRAFT candidate selector:

```text
id
href
specKey
draftId
name
lifecycleStatus = DRAFT
statusChangeDate
creationDate
lastUpdate
isBundle
expressionSpecification
targetEntitySchema
@type
@baseType
_links
```

DRAFT candidates do not expose an official public `version`. Draft revision is represented by `ETag`. Any version indicator during draft authoring is non-authoritative and must not be relied on.

## 4. specKey and id resolution rule:

`specKey` is mandatory when creating a DRAFT. ID MS uses it to resolve the server-assigned `IntentSpecification.id`.

Rules:

- If a current ACTIVE specification exists for the same `specKey`, the new DRAFT candidate is assigned to that existing `id`.
- If no current ACTIVE specification exists for the `specKey`, ID MS creates a new `id`.
- If only RETIRED versions exist for the `specKey`, ID MS creates a new `id` unless governed lineage reuse is explicitly introduced later.
- Lineage reuse across retired-only specifications is not assumed by default. Reintroduction or reuse of a prior lineage requires explicit governance.
- At most one ACTIVE lineage may exist for a given `specKey`; duplicate ACTIVE lineages are a data-integrity breach.

## 5. DRAFT candidate operations:

DRAFT candidate retrieval and mutation use `draftId`:

```http
GET /intentManagement/v5/intentSpecification/draft/{draftId}
PUT /intentManagement/v5/intentSpecification/draft/{draftId}
PATCH /intentManagement/v5/intentSpecification/draft/{draftId}
DELETE /intentManagement/v5/intentSpecification/draft/{draftId}
```

Unsafe DRAFT operations require `If-Match`. `PUT` performs deterministic full replacement of a mutable DRAFT candidate. `PATCH` performs TMF-compatible JSON Merge Patch and may activate the selected DRAFT candidate by setting `lifecycleStatus` to `ACTIVE`.

## 6. ACTIVE and RETIRED official profile:

ACTIVE and RETIRED official versions are selected by `id`, and a specific historical official version may also use `version`.

```http
GET /intentManagement/v5/intentSpecification/{id}
GET /intentManagement/v5/intentSpecification/{id}?version={version}
DELETE /intentManagement/v5/intentSpecification/{id}
```

The current ACTIVE version is selected by `id` alone. ACTIVE and RETIRED records are immutable for contract/content changes.

ACTIVE persisted resources must include:

```text
id
href
specKey
draftId
version
name
lifecycleStatus = ACTIVE
statusChangeDate
creationDate
lastUpdate
isBundle
validFor.startDateTime
expressionSpecification
expressionSpecification.iri
expressionSpecification.expressionLanguage
targetEntitySchema
specCharacteristic[]
@type
@baseType
```

Where `schemaHash` is supplied in `targetEntitySchema`, real values use the `sha256:<hex>` format. Schema registry lookup and verification remain implementation details unless stricter policy is introduced.

## 7. Activation rule:

Activation is performed on one selected DRAFT candidate addressed by `draftId`.

Activation rules:

- Only `DRAFT` candidates can be activated.
- Activation validates the full resulting `IntentSpecification` candidate before committing.
- ID MS assigns the official `version` during activation.
- ID MS carries the selected `draftId` forward as immutable provenance.
- ID MS transactionally retires the previous ACTIVE version for the same resolved `id`.
- Activation must also enforce the `specKey` active-lineage uniqueness invariant.


## 8. Optional behaviour metadata:

`intentBehaviour` and `intentLayer` are optional classification metadata fields.

They support:

- catalogue visibility
- governance visibility
- external consumer understanding

They are not used by ID MS for:

- runtime decisioning
- runtime validation
- admission control
- behavioural enforcement

They are not part of the minimum mandatory profile and are not required for DRAFT creation, activation, or runtime Intent admission in the current baseline. If omitted, ID MS does not infer or default these values unless an explicit platform policy is later introduced.

The only ID MS-level `intentBehaviour` fields defined in this baseline are:

- `category`
- `constraintMode`
- `objectiveType`
- `fulfilmentMode`

No additional behaviour fields are defined at ID MS level.

Allowed values:

| **Field** | **Allowed values** | **Meaning** |
| --- | --- | --- |
| `intentBehaviour.category` | `REALTIME`, `BATCH`, `OPTIMISATION`, `ASSURANCE` | Broad behavioural type of intents created from the specification. |
| `intentBehaviour.constraintMode` | `STRICT`, `FLEXIBLE` | Whether constraints are normally mandatory or may be relaxed by governed policy or negotiation. |
| `intentBehaviour.objectiveType` | `SLA`, `COST`, `ENERGY`, `BALANCED` | Main decision or optimisation objective. |
| `intentBehaviour.fulfilmentMode` | `IMMEDIATE`, `LONGRUNNING`, `CONTINUOUS` | Fulfilment behaviour. |
| `intentLayer` | `BUSINESS`, `SERVICE`, `RESOURCE` | Abstraction layer of the intent. |

`fulfilmentMode` values mean:

| **Value** | **Meaning** |
| --- | --- |
| `IMMEDIATE` | Fulfilment is expected to complete in a short-lived operation. |
| `LONGRUNNING` | Fulfilment spans a longer-running workflow with delayed completion feedback. |
| `CONTINUOUS` | Downstream systems may operate in a closed-loop manner to maintain the intent objective over time. |

For the hospital surgical slice example, the recommended optional metadata is:

```json
{
  "intentBehaviour": {
    "category": "REALTIME",
    "constraintMode": "STRICT",
    "objectiveType": "SLA",
    "fulfilmentMode": "CONTINUOUS"
  },
  "intentLayer": "SERVICE"
}
```

`IMMEDIATE` and `LONGRUNNING` describe fulfilment timing. `CONTINUOUS` indicates that downstream systems may operate in a closed-loop manner to maintain the intent objective over time. This does not imply mutation of the submitted runtime Intent instance.

These fields do not replace `expressionSpecification.iri`, `targetEntitySchema`, `specCharacteristic`, or request-specific `serviceType`, `serviceClass`, `priority`, targets, constraints, and preferences inside the governed expression schema.

## 9. specKey lineage note:

`specKey` represents logical grouping across specification versions. If only `RETIRED` versions exist for a `specKey`, ID MS creates a new `id` by default. Lineage reuse of retired specifications is not assumed and requires explicit governance if introduced later.

## 10. Runtime admission guardrail:

IC MS runtime admission must reference a concrete ACTIVE `intentSpecification.id`. Runtime admission must not use `specKey` or `draftId` as the contract-selection key. DRAFT candidates are not valid for new runtime Intent admission.

## 11. Intent immutability clarification:

Runtime Intent instances created using an `ACTIVE` `IntentSpecification` remain tied to the specification identity and version used at admission.

- `IntentSpecification` lifecycle may evolve from `DRAFT` to `ACTIVE` to `RETIRED`.
- Existing runtime Intent instances referencing a RETIRED specification may continue under IC MS or platform governance policy.
- A change in intent requirements must result in submission of a new Intent instance. Runtime mutation of admitted Intent instances is not supported.
- ID MS does not mutate runtime Intent instances.
- `ACTIVE` and `RETIRED` `IntentSpecification` versions remain immutable for material contract changes.
