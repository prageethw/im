# IA MS Acceptance Criteria

**Document status:** Initial SDD build-driving acceptance baseline. This document refines the architecture baseline into testable delivery criteria.


## 1. Purpose:

This document defines acceptance criteria for IA MS, the Guardian For Intents. IA MS owns network-ready application coordination, assurance evaluation, evidence capture and `IntentAssuranceEvent` publication.

## 2. Source artefacts:

| Artefact | Role |
|---|---|
| `ia-ms/ia_ms_specification.md` | Primary implementation specification |
| `ia-ms/ia_ms_design_brief.md` | Service design baseline |
| `ia-ms/ia_ms_solution_brief.md` | Behaviour and stakeholder summary |
| `e2e/intent_internal_events_specification.md` | Event contract baseline |

## 3. Ownership boundary:

IA MS owns assurance evaluation, evidence management, application status assessment and emission of assurance outcomes.

IA MS does not own runtime intent admission, optimiser decisioning, callback ingress or generic degraded-state decisioning.

## 4. Functional acceptance criteria:

| ID | Scenario | Acceptance criteria |
|---|---|---|
| IA-AC-001 | Consume network ready event | Given an `IntentNetworkReadyEvent`, when IA MS consumes it, then IA MS starts application and assurance processing idempotently. |
| IA-AC-002 | Apply selected configuration | Given selected configuration and observer configuration, when IA MS applies it to the network boundary, then the operation is recorded with correlation metadata. |
| IA-AC-003 | Consume network callback | Given a network execution callback relayed by ICB MS, when IA MS consumes it, then IA MS updates assurance evidence and application status. |
| IA-AC-004 | Emit active assurance | Given the network confirms the intent is active and benchmarks are met, when assurance evaluation completes, then IA MS emits `IntentAssuranceEvent` with active or assured state. |
| IA-AC-005 | Emit degraded assurance | Given telemetry or callback evidence shows benchmarks are not met, when evaluation completes, then IA MS emits `IntentAssuranceEvent` indicating degraded state. |
| IA-AC-006 | Emit failed assurance | Given application or evaluation fails, when terminal handling completes, then IA MS emits a failed assurance outcome with evidence. |
| IA-AC-007 | Emit terminated assurance | Given termination is confirmed, when evaluation completes, then IA MS emits a terminated assurance outcome with evidence. |
| IA-AC-008 | Preserve evidence | Given any assurance outcome, when stored, then supporting evidence, timestamps, correlation id and source references are persisted. |
| IA-AC-009 | Avoid degraded-state ownership | Given a degraded assurance event, when IA MS emits it, then II MS evaluates the governed degraded-state action path. |
| IA-AC-010 | Status query | Given an intent id, when assurance status is queried, then IA MS returns the latest assurance status and evidence summary. |

## 5. API and integration acceptance criteria:

- IA MS APIs must expose assurance status and evidence according to the specification.
- Network integration must use governed boundary contracts.
- IA MS must consume execution callbacks from the callbacks topic after ICB structural ingestion.
- IA MS must not consume optimiser status callbacks for decisioning.

## 6. Event acceptance criteria:

- IA MS must consume `IntentNetworkReadyEvent`.
- IA MS must consume network execution and assurance callbacks from `t7.intent.management.events.callbacks`.
- IA MS must emit `IntentAssuranceEvent` for active, degraded, failed and terminated outcomes where applicable.
- Event publication must use the outbox pattern.
- Event consumption must be idempotent.

## 7. Persistence acceptance criteria:

- Assurance records must preserve intent id, selected configuration reference, observer configuration reference, current assurance state, evidence links, correlation id and audit metadata.
- Terminal outcomes must be immutable unless an explicit correction flow exists.
- Evidence must be queryable for audit and lifecycle projection.

## 8. Negative acceptance criteria:

- IA MS must not call the optimiser.
- IA MS must not own optimiser callback interpretation.
- IA MS must not admit runtime intents.
- IA MS must not decide the degraded-state remediation path; it emits evidence and state for II MS evaluation.
- IA MS must not bypass ICB MS for external callback ingestion.

## 9. Test evidence:

The implementation is accepted only when network-ready consumption tests, callback consumption tests, assurance event tests, evidence persistence tests and idempotency tests pass.
