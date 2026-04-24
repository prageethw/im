# II MS Baseline Pack

This document consolidates the currently baselined **II MS** decision flow contents in Markdown.

## Scope

This pack includes:
- II MS role and scope
- II MS decision stages
- stage-to-event mapping
- decision matrix
- KP sections II MS reads
- rejection / optimisation / no-action rules
- re-optimisation trigger rules after `IntentAssuranceEvent`

## Notes

- II MS is the semantic and policy interpretation layer.
- II MS consumes validated intent input and internal assurance truth.
- II MS reads internal KP / Master Knowledge Config.
- II MS emits internal milestone events such as `IntentResolvedEvent`, `IntentRejectedEvent`, and `IntentNetworkReadyEvent`.

---

# 1. II MS role and scope

## Role
II MS is the semantic and policy interpretation layer using its internal knowledge plane.

## Inputs
- `IntentValidatedEvent`
- `IntentAssuranceEvent`
- KP / Master Knowledge Config

## Outputs
- `IntentResolvedEvent`
- `IntentRejectedEvent`
- `IntentNetworkReadyEvent`

## Non-goals
II MS does not own:
- external intent contract validation syntax
- runtime assurance truth generation
- optimiser execution itself
- direct external TMF event publication

---

# 2. II MS decision stages

## 1. Consume validated intent
- input: `IntentValidatedEvent`
- II MS reads validated request content, referenced `IntentSpecification`, and KP knowledge

## 2. Semantic interpretation
II MS resolves:
- `location`
- `sliceType`
- `priority`
- `semanticTag`
- service meaning from human/formal/characteristic input

KP used:
- `humanExpressionMapping`
- `locations`
- `services`
- `behaviour`

## 3. Policy evaluation
II MS checks whether the resolved request is allowed.

KP used:
- `policyRules`

Outcomes:
- fail -> `IntentRejectedEvent`
- pass -> continue

## 4. Candidate discovery
II MS determines the applicable resource set for the resolved location/service context.

KP used:
- `locations.applicableResourceIds`
- global `resources`

## 5. Optimisation decision
II MS decides whether optimisation is required.

KP used:
- `optimisationProfiles`
- `services`
- `resolutionOutput`

Outcomes:
- optimisation required -> emit `IntentResolvedEvent`
- optimisation not required -> emit `IntentNetworkReadyEvent`

## 6. Rejection path
- semantic, policy, or candidate-discovery failure -> emit `IntentRejectedEvent`

## 7. Re-optimisation trigger path
Later, after `IntentAssuranceEvent`:
- non-degraded -> no new `IntentResolvedEvent` required
- degraded without re-decision need -> no action
- degraded with re-decision need -> emit new `IntentResolvedEvent`

---

# 3. II MS stage-to-event mapping table

| Stage | Input | KP sections read | Decision | Output |
|---|---|---|---|---|
| Consume validated intent | `IntentValidatedEvent` | none yet beyond references carried in event | accept for II MS processing | continue internal processing |
| Semantic interpretation | validated request content from `IntentValidatedEvent` | `humanExpressionMapping`, `locations`, `services`, `behaviour` | can II MS resolve meaning, location, service context, and structured fields? | continue or reject |
| Policy evaluation | resolved semantic context | `policyRules` | is the resolved request allowed? | continue or `IntentRejectedEvent` |
| Candidate discovery | resolved and policy-valid request | `locations.applicableResourceIds`, `resources` | what is the applicable candidate set? | continue or reject if no valid candidate set |
| Optimisation decision | resolved request + applicable candidates | `optimisationProfiles`, `services`, `resolutionOutput` | is optimisation required? | `IntentResolvedEvent` or `IntentNetworkReadyEvent` |
| Rejection path | failure from semantic/policy/candidate stage | `resolutionOutput` as needed | rejection reason must be emitted | `IntentRejectedEvent` |
| Re-optimisation trigger path | `IntentAssuranceEvent` | `resources`, `locations`, `optimisationProfiles`, `policyRules` as needed | degraded and re-decision needed? | no action or new `IntentResolvedEvent` |

---

# 4. II MS decision matrix

| Checkpoint | Yes | No |
|---|---|---|
| Can II MS semantically resolve the request? | continue to policy evaluation | emit `IntentRejectedEvent` |
| Does policy allow the resolved request? | continue to candidate discovery | emit `IntentRejectedEvent` |
| Is there a valid applicable candidate set? | continue to optimisation decision | emit `IntentRejectedEvent` |
| Is optimisation required? | emit `IntentResolvedEvent` | emit `IntentNetworkReadyEvent` |
| Is `IntentAssuranceEvent.lifecycleStatus = Degraded`? | evaluate re-decision need | no action |
| Is re-decision needed? | emit new `IntentResolvedEvent` | no action |

---

# 5. Output rules by stage

- semantic interpretation fails -> `IntentRejectedEvent`
- policy evaluation fails -> `IntentRejectedEvent`
- candidate discovery finds no valid applicable set -> `IntentRejectedEvent`
- optimisation required -> `IntentResolvedEvent`
- optimisation not required -> `IntentNetworkReadyEvent`
- degraded assurance with re-decision needed -> new `IntentResolvedEvent`

---

# 6. Important locked behaviour

- non-degraded `IntentAssuranceEvent` does not require a new `IntentResolvedEvent`
- degraded `IntentAssuranceEvent` only drives re-decision when needed
- degraded `candidates`, when present, must include current active resources too

---

# 7. KP sections II MS reads

II MS reads the following KP sections:
- `locations`
- `services`
- `policyRules`
- `resources`
- `observabilityProfiles`
- `optimisationProfiles`
- `humanExpressionMapping`
- `behaviour`
- `resolutionOutput`

---

# 8. Completion status

This II MS baseline pack currently covers:
- stage flow
- event outputs
- decision logic
- re-optimisation trigger behaviour
- KP read surface
