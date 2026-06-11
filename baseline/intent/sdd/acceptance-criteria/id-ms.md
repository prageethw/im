# ID MS Acceptance Criteria

**Document status:** Initial SDD build-driving acceptance baseline. This document refines the architecture baseline into testable delivery criteria.


## 1. Purpose:

This document defines acceptance criteria for ID MS, the Librarian for Intents. ID MS owns intent specification definition, versioning, lifecycle governance, catalogue lookup and TMF921-aligned intent specification resources.

## 2. Source artefacts:

| Artefact | Role |
|---|---|
| `id-ms/id_ms_specification.md` | Primary implementation specification |
| `id-ms/id_ms_design_brief.md` | Service design baseline |
| `id-ms/id_ms_solution_brief.md` | Behaviour and stakeholder summary |
| `id-ms/*openapi*` or TMF921 contract | API contract source |
| `e2e/intent_internal_events_specification.md` | Shared event alignment where relevant |

## 3. Ownership boundary:

ID MS owns intent specification metadata, version lineage, draft lifecycle, active specification lookup and retired specification handling.

ID MS does not own runtime intent admission, network application, optimiser decisioning, callback ingestion or assurance evaluation.

## 4. Functional acceptance criteria:

| ID | Scenario | Acceptance criteria |
|---|---|---|
| ID-AC-001 | Create draft specification | Given a valid intent specification create request, when ID MS accepts it, then a draft specification is persisted with a stable identifier and lineage reference. |
| ID-AC-002 | Validate required fields | Given a create or update request missing mandatory fields, when ID MS validates it, then the request is rejected with a consistent validation error response. |
| ID-AC-003 | Activate specification | Given a valid draft specification, when activation is requested, then ID MS assigns the official version and marks the specification active. |
| ID-AC-004 | Enforce active version rule | Given a runtime lookup for new intent creation, when ID MS resolves a specification, then only an active specification version is returned as usable. |
| ID-AC-005 | Preserve version lineage | Given multiple versions of the same specification, when a new version is activated, then lineage is preserved and previous versions remain auditable. |
| ID-AC-006 | Retire specification | Given an active specification, when it is retired, then ID MS prevents it from being used for new runtime intents while preserving historical reference. |
| ID-AC-007 | Retrieve by id | Given an existing specification id, when a GET request is made, then the correct specification representation is returned. |
| ID-AC-008 | Retrieve by key and version | Given a specification key and version, when lookup is requested, then ID MS returns the matching version or a not found response. |
| ID-AC-009 | Idempotency | Given a repeated create request with the same idempotency key, when replayed, then ID MS returns the original outcome without duplicate persistence. |
| ID-AC-010 | Audit fields | Given any state-changing request, when completed, then created or updated audit metadata is persisted. |

## 5. API acceptance criteria:

- API paths, request fields and response fields must remain aligned with the agreed TMF921 intent specification contract.
- Error responses must use the platform error model.
- GET operations must support agreed cache headers where applicable.
- Non-GET operations must not be cached.
- Correlation identifiers must be accepted and propagated to logs and downstream events where applicable.

## 6. Persistence acceptance criteria:

- Specification records must preserve id, key, version, lifecycle status, lineage id and audit metadata.
- Historical versions must not be overwritten when new versions are activated.
- Active specification lookup must be deterministic.
- Concurrent activation attempts must not create duplicate active versions for the same specification key.

## 7. Event acceptance criteria:

- ID MS must publish only events explicitly defined in the architecture baseline.
- Events must include correlation id, causation id, event id, event type, event time and source service.
- Events must be published through the outbox pattern when emitted from a state-changing transaction.

## 8. Negative acceptance criteria:

- ID MS must not admit runtime intents.
- ID MS must not call the optimiser.
- ID MS must not process network callbacks.
- ID MS must not own assurance decisions.
- ID MS must not assign runtime intent lifecycle state.

## 9. Test evidence:

The implementation is accepted only when unit tests, component tests and API contract tests pass, and when version lifecycle scenarios have deterministic test evidence.
