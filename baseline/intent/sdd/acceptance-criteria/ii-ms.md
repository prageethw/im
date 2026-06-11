# II MS Acceptance Criteria

**Document status:** Initial SDD build-driving acceptance baseline. This document refines the architecture baseline into testable delivery criteria.


## 1. Purpose:

This document defines acceptance criteria for II MS, the Brain For Intents. II MS owns intent intelligence, optimiser submission, optimiser outcome consumption, selected configuration decisioning and degraded-state decision evaluation.

## 2. Source artefacts:

| Artefact | Role |
|---|---|
| `ii-ms/ii_ms_specification.md` | Primary implementation specification |
| `ii-ms/ii_ms_design_brief.md` | Service design baseline |
| `ii-ms/ii_ms_solution_brief.md` | Behaviour and stakeholder summary |
| `ii-ms/kp_master_config.md` | Knowledge provider and governed lookup baseline where present |
| `e2e/intent_internal_events_specification.md` | Event contract baseline |

## 3. Ownership boundary:

II MS owns intent decisioning, knowledge lookup coordination, optimiser request submission, optimisation outcome handling and production of network-ready or rejected decisions.

II MS does not own callback ingress, runtime intent admission, direct network application or generic retry orchestration.

## 4. Functional acceptance criteria:

| ID | Scenario | Acceptance criteria |
|---|---|---|
| II-AC-001 | Consume validated intent | Given an `IntentValidatedEvent`, when II MS consumes it, then it starts decisioning idempotently using intent id, correlation id and event identity. |
| II-AC-002 | Build optimisation request | Given a valid intent decisioning context, when II MS submits optimisation, then the request includes source context, optimisation specification id and expression context. |
| II-AC-003 | Keep observability out of optimiser request | Given optimiser submission, when the payload is built, then observer configuration and observability fields are not added to the optimiser request by default. |
| II-AC-004 | Register or use callback target | Given optimiser integration, when II MS submits optimisation, then the optimiser callback target resolves to the ICB-owned callback submission URL. |
| II-AC-005 | Consume optimisation status | Given an `OptimisationStatusChangeEvent` from the callbacks topic, when II MS consumes it, then selected configuration, infeasible, failed or timeout outcomes are handled according to the specification. |
| II-AC-006 | Produce network ready event | Given a successful optimisation outcome and governed lookup completion, when decisioning completes, then II MS publishes `IntentNetworkReadyEvent`. |
| II-AC-007 | Include observer configuration from governed source | Given the selected network configuration, when II MS emits `IntentNetworkReadyEvent`, then observer details are populated from KP or governed configuration, not the optimiser response. |
| II-AC-008 | Produce rejection outcome | Given an infeasible or invalid decisioning outcome, when no acceptable configuration exists, then II MS publishes the agreed rejection or failure event. |
| II-AC-009 | Consume assurance degradation | Given an `IntentAssuranceEvent` indicating degraded state, when II MS consumes it, then II MS evaluates the governed degraded-state action path. |
| II-AC-010 | Avoid generic retry ownership | Given failed or terminated outcomes, when II MS evaluates response, then it does not own generic retries unless a specific governed retrial instruction applies. |

## 5. API and integration acceptance criteria:

- Optimiser integration must use the agreed `POST /optimisation` contract.
- Callback ingestion must be owned by ICB MS.
- II MS must consume optimiser outputs from the callbacks topic, not from a private callback endpoint.
- Knowledge provider lookup contracts must include source discovery, freshness checks, trust scoring and governed lookup semantics where required by delivery stakeholders.

## 6. Event acceptance criteria:

- II MS must consume `IntentValidatedEvent`.
- II MS must consume optimisation status callbacks from `t7.intent.management.events.callbacks`.
- II MS must publish `IntentNetworkReadyEvent` for successful selected configuration outcomes.
- II MS may publish optional observability milestone events only where the architecture baseline permits.
- Event handling must be idempotent.

## 7. Persistence acceptance criteria:

- Decision records must preserve intent id, correlation id, optimiser request reference, optimiser outcome reference, selected configuration summary and decision status.
- Duplicate validated events or optimisation callbacks must not duplicate downstream decisions.
- Timeout and infeasible states must be recoverable and auditable.

## 8. Negative acceptance criteria:

- II MS must not expose the optimiser callback ingestion endpoint directly.
- II MS must not apply configuration to the network.
- II MS must not own runtime intent admission.
- II MS must not move observability fields into optimiser request or response payloads by default.
- II MS must not consume network execution callbacks intended for IA MS except where explicitly defined in the event contract.

## 9. Test evidence:

The implementation is accepted only when event consumption tests, optimiser contract tests, decisioning tests, timeout tests and idempotency tests pass.
