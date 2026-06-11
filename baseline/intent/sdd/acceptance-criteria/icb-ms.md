# ICB MS Acceptance Criteria

**Document status:** Initial SDD build-driving acceptance baseline. This document refines the architecture baseline into testable delivery criteria.


## 1. Purpose:

This document defines acceptance criteria for ICB MS, the Dispatcher For Intents. ICB MS owns callback submission, structural validation, idempotent ingestion and outbox relay to the platform callbacks topic.

## 2. Source artefacts:

| Artefact | Role |
|---|---|
| `icb-ms/icb_ms_specification.md` | Primary implementation specification |
| `icb-ms/icb_ms_design_brief.md` | Service design baseline |
| `icb-ms/icb_ms_solution_brief.md` | Behaviour and stakeholder summary |
| `e2e/intent_internal_events_specification.md` | Callback event and topic baseline |

## 3. Ownership boundary:

ICB MS owns callback ingress, source envelope validation, duplicate detection and relay to Kafka.

ICB MS does not interpret business meaning of callbacks. II MS consumes optimisation status callbacks. IA MS consumes network execution and assurance callbacks.

## 4. Functional acceptance criteria:

| ID | Scenario | Acceptance criteria |
|---|---|---|
| ICB-AC-001 | Accept callback submission | Given a structurally valid callback submission, when received, then ICB MS accepts and persists the callback envelope. |
| ICB-AC-002 | Validate callback envelope | Given a callback missing required source state or identity fields, when submitted, then ICB MS rejects it with a validation error. |
| ICB-AC-003 | Preserve source state | Given a callback with `sourceState.state`, when accepted, then the source state is persisted unchanged. |
| ICB-AC-004 | Idempotent ingestion | Given a duplicate callback submission, when replayed, then ICB MS does not produce duplicate downstream callback events. |
| ICB-AC-005 | Relay to callbacks topic | Given an accepted callback, when the outbox relay runs, then an event is published to `t7.intent.management.events.callbacks`. |
| ICB-AC-006 | Optimisation callback relay | Given an optimiser `OptimisationStatusChangeEvent`, when accepted, then it is relayed for II MS consumption without business interpretation. |
| ICB-AC-007 | Network callback relay | Given a network execution callback, when accepted, then it is relayed for IA MS consumption without business interpretation. |
| ICB-AC-008 | Correlation preservation | Given a callback with correlation metadata, when relayed, then correlation id, causation id and source identifiers are preserved. |
| ICB-AC-009 | Poison handling | Given a callback that cannot be processed after configured retries, when retry is exhausted, then it is sent to the agreed error handling path with evidence. |
| ICB-AC-010 | Security validation | Given a callback request, when received, then authentication, authorisation and integrity checks are applied according to the security baseline. |

## 5. API acceptance criteria:

- Callback submission endpoint must remain `/intent-callback/v1/submissions` unless an ADR changes it.
- API responses must clearly distinguish accepted, rejected and duplicate callback submissions.
- Request validation must be structural only unless the specification explicitly defines additional checks.

## 6. Event acceptance criteria:

- ICB MS must publish accepted callbacks to `t7.intent.management.events.callbacks`.
- Consumers of the callbacks topic include IA MS and II MS.
- ICB MS must not route by hidden business logic that changes callback ownership.
- Event publication must use the outbox pattern.

## 7. Persistence acceptance criteria:

- Callback submissions must be persisted with event identity, source identity, callback type or event type where applicable, source state, received timestamp and processing status.
- Duplicate detection must be deterministic.
- Accepted callbacks must be replayable through the outbox relay without loss of correlation metadata.

## 8. Negative acceptance criteria:

- ICB MS must not decide optimiser outcomes.
- ICB MS must not emit `IntentNetworkReadyEvent`.
- ICB MS must not emit `IntentAssuranceEvent`.
- ICB MS must not update runtime intent lifecycle state directly.
- ICB MS must not call network systems to apply intent configuration.

## 9. Test evidence:

The implementation is accepted only when callback API tests, duplicate ingestion tests, outbox relay tests and topic contract tests pass.
