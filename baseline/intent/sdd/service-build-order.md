# Intent Platform Service Build Order

**Document status:** Draft SDD planning artefact.

## 1. Purpose:

This document defines the recommended service build order for the Intent Management Platform. The order is designed to reduce integration risk, prove boundaries early and avoid building complex reasoning or assurance flows before the foundation contracts are stable.

## 2. Recommended order:

| Order | Service or layer | Reason |
|---:|---|---|
| 1 | Foundation | Establish common service scaffold, local runtime, event patterns, test harness, observability and security baseline. |
| 2 | ID MS | Provides the intent specification catalogue and active specification baseline needed by runtime intent admission. |
| 3 | IC MS | Provides runtime intent admission, validation and lifecycle projection. This becomes the main entry point for runtime intent flows. |
| 4 | ICB MS | Provides callback ingestion and reliable callback relay before II MS and IA MS depend on external callback outcomes. |
| 5 | II MS | Adds reasoning and optimiser interaction once IC and ICB boundaries exist. |
| 6 | IA MS | Adds assurance and network apply flow once selected configuration and callback paths are available. |

## 3. Rationale:

The order deliberately starts with stable contracts and low-semantic-risk services.

ID MS is built before IC MS because runtime intents should reference valid active intent specifications. IC MS is built before II MS because II MS consumes validated intent events. ICB MS is built before II MS and IA MS because both need callback outcomes to complete their control loops. IA MS comes after II MS because IA MS applies and assures selected configuration produced by the Brain For Intents.

## 4. Dependency view:

```text
Foundation
  -> ID MS
  -> IC MS
      -> ICB MS
          -> II MS
              -> IA MS
```

This is a build dependency view, not a runtime orchestration chain.

## 5. Parallelisation guidance:

Some work can proceed in parallel after the foundation slice is stable:

| Parallel work | Conditions |
|---|---|
| ID MS and IC MS API scaffolding | Shared API, error and persistence patterns are agreed. |
| ICB MS callback API and event schemas | Callback envelope and topic naming are stable. |
| II MS optimiser adapter spike | Optimiser request and callback contracts are stable. |
| IA MS assurance event model | IntentAssuranceEvent contract and lifecycle projection rules are stable. |

## 6. Build checkpoints:

| Checkpoint | Expected evidence |
|---|---|
| Foundation complete | Service templates, common middleware, local runtime and test harness work. |
| ID MS complete | Active intent specifications can be created, versioned and queried. |
| IC MS complete | Runtime intent can be admitted and `IntentValidatedEvent` can be emitted. |
| ICB MS complete | Callback submission is accepted, validated and relayed to Kafka. |
| II MS complete | Optimiser output can produce `IntentNetworkReadyEvent` or a governed rejection path. |
| IA MS complete | Network apply and assurance outcomes are reflected through `IntentAssuranceEvent`. |

## 7. Out-of-order exceptions:

A slice may be built out of order only when:

- It does not require unavailable contracts from a later slice.
- It is clearly marked as a spike or prototype.
- It does not change architecture ownership boundaries.
- It does not introduce production commitments before acceptance criteria exist.

## 8. Review rule:

Before starting each service slice, engineers must review:

- The service specification.
- The service design brief.
- Relevant OpenAPI contracts.
- Relevant event contracts.
- SDD acceptance criteria.
- Agent guardrails.
