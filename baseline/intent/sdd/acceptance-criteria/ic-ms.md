# IC MS Acceptance Criteria

**Document status:** Initial SDD build-driving acceptance baseline. This document refines the architecture baseline into testable delivery criteria.


## 1. Purpose:

This document defines acceptance criteria for IC MS, the Controller For Intents. IC MS owns runtime intent admission, request validation, runtime lifecycle projection and publication of accepted or rejected intent events.

## 2. Source artefacts:

| Artefact | Role |
|---|---|
| `ic-ms/ic_ms_specification.md` | Primary implementation specification |
| `ic-ms/ic_ms_design_brief.md` | Service design baseline |
| `ic-ms/ic_ms_solution_brief.md` | Behaviour and stakeholder summary |
| `ic-ms/*openapi*` or TMF921 contract | Runtime API contract source |
| `e2e/intent_internal_events_specification.md` | Event contract baseline |

## 3. Ownership boundary:

IC MS owns runtime intent capture, admission validation, runtime intent persistence, lifecycle projection and client-facing runtime status.

IC MS does not own intent specification authoring, optimiser reasoning, callback ingestion, network application or assurance evaluation.

## 4. Functional acceptance criteria:

| ID | Scenario | Acceptance criteria |
|---|---|---|
| IC-AC-001 | Submit runtime intent | Given a valid runtime intent request, when IC MS admits it, then a runtime intent resource is persisted and an accepted event is published. |
| IC-AC-002 | Validate active specification | Given a runtime intent request referencing a specification, when IC MS validates it, then the referenced specification must be active in ID MS. |
| IC-AC-003 | Validate expression | Given a runtime intent request, when expression validation runs, then `body.expression.context` is validated as the canonical runtime context path. |
| IC-AC-004 | Reject invalid request | Given an invalid runtime intent request, when validation fails, then IC MS persists or returns the rejected outcome according to the specification and publishes the agreed rejection event where required. |
| IC-AC-005 | Draft submit false | Given a draft style request with `submit=false`, when accepted, then IC MS stores it without progressing it to downstream decisioning. |
| IC-AC-006 | Admission idempotency | Given a repeated admission request with the same idempotency key, when replayed, then duplicate runtime intents are not created. |
| IC-AC-007 | Runtime status projection | Given downstream status events, when IC MS consumes them, then runtime lifecycle status is projected for API retrieval. |
| IC-AC-008 | Pause and resume projection | Given pause or resume requests supported by IC MS, when processed, then IC MS projects lifecycle state but does not independently resume network behaviour. |
| IC-AC-009 | Correlation | Given any runtime intent, when events are produced or consumed, then correlation id and intent id are preserved across the flow. |
| IC-AC-010 | Status retrieval | Given an existing runtime intent id, when a client retrieves it, then IC MS returns the latest projected status and relevant metadata. |

## 5. API acceptance criteria:

- Runtime API behaviour must remain aligned with the agreed TMF921 profile.
- Request and response fields must not be renamed without an ADR and contract update.
- API responses must use the platform error model.
- GET responses must support agreed cache behaviour where applicable.
- Non-GET endpoints must not be cached.

## 6. Event acceptance criteria:

- IC MS must publish `IntentValidatedEvent` when an intent is admitted and ready for II MS decisioning.
- IC MS must publish rejection events only where specified by the architecture baseline.
- IC MS must consume downstream lifecycle or assurance events only to project runtime status.
- Event publication must use the outbox pattern.
- Event consumption must be idempotent.

## 7. Persistence acceptance criteria:

- Runtime intent records must preserve intent id, specification reference, expression, lifecycle status, version, correlation id and audit metadata.
- Lifecycle projection must be recoverable from persisted state and consumed events.
- Duplicate admission must be prevented through idempotency keys or equivalent uniqueness controls.

## 8. Negative acceptance criteria:

- IC MS must not call the optimiser directly.
- IC MS must not own optimiser callback interpretation.
- IC MS must not own network execution callback ingestion.
- IC MS must not apply configuration to the network.
- IC MS must not infer assurance status independently of IA MS evidence.

## 9. Test evidence:

The implementation is accepted only when API contract tests, lifecycle projection tests, idempotency tests and event publication tests pass.
