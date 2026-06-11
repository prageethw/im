# Slice 05 II MS

**Document status:** Initial SDD delivery slice baseline.

## 1. Purpose:

This slice builds II MS, the Brain For Intents, to consume admitted intents, perform governed decisioning, interact with the optimiser and produce network-ready or rejected outcomes.

## 2. Depends on:

- `sdd/slices/slice-01-foundation.md`
- `sdd/slices/slice-03-ic-ms.md`
- `sdd/slices/slice-04-icb-ms.md`
- `sdd/acceptance-criteria/ii-ms.md`
- `ii-ms/ii_ms_specification.md`
- Optimiser API and callback contracts.

## 3. In scope:

- `IntentValidatedEvent` consumption.
- Optimiser request construction.
- `POST /optimisation` integration.
- ICB callback target usage.
- `OptimisationStatusChangeEvent` consumption from callbacks topic.
- Selected configuration handling.
- Knowledge provider lookup integration stub or governed contract.
- `IntentNetworkReadyEvent` publication.
- Infeasible, failed and timeout handling.
- Degraded-state evaluation from `IntentAssuranceEvent`.

## 4. Out of scope:

- Callback ingress endpoint ownership.
- Network application.
- Runtime admission.
- Generic retry orchestration.
- Direct assurance evaluation.

## 5. Build tasks:

| ID | Task |
|---|---|
| II-SL-001 | Implement decision record data model and migrations. |
| II-SL-002 | Implement `IntentValidatedEvent` consumer. |
| II-SL-003 | Implement optimiser request builder. |
| II-SL-004 | Implement optimiser client for `POST /optimisation`. |
| II-SL-005 | Configure ICB-owned callback URL usage. |
| II-SL-006 | Implement `OptimisationStatusChangeEvent` consumer. |
| II-SL-007 | Implement selected configuration decision handling. |
| II-SL-008 | Implement KP lookup contract or integration stub. |
| II-SL-009 | Publish `IntentNetworkReadyEvent` through outbox. |
| II-SL-010 | Implement infeasible, failed and timeout behaviours. |
| II-SL-011 | Implement degraded-state event consumption path. |
| II-SL-012 | Add decisioning, optimiser and event tests. |

## 6. Acceptance criteria:

- All criteria in `sdd/acceptance-criteria/ii-ms.md` pass.
- Observability configuration is not added to optimiser request or response payloads by default.
- Optimiser callbacks are consumed from the callbacks topic after ICB relay.
- Successful decisions produce `IntentNetworkReadyEvent`.
- Infeasible and failed decisions do not produce network-ready events.

## 7. Test evidence:

- Event consumer test report.
- Optimiser API contract test report.
- Optimisation callback test report.
- Decisioning test report.
- Timeout and infeasible outcome test report.
- Idempotency test report.

## 8. Done when:

II MS can transform admitted intents into governed network-ready decisions or explicit rejection outcomes without taking ownership of callback ingress or network application.
