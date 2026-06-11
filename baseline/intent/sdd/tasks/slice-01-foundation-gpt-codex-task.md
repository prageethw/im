# Slice 01 — Foundation GPT Codex Task

**Document status:** Execution instruction for GPT Codex assisted implementation.

## 1. Purpose:

This task instructs GPT Codex to implement the foundation skeleton for the Intent Management Platform.

Slice 01 creates the shared engineering baseline for all Intent microservices. It must not implement service-specific domain workflows yet.

## 2. Execution model:

GPT Codex is an implementation assistant, not the architecture owner.

Codex must implement against the existing repository specifications, contracts, acceptance criteria and guardrails. Codex must not change service ownership, event ownership, lifecycle semantics, topic names, public API names or architecture decisions unless an approved ADR already exists.

## 3. Branch:

Create and work on this branch:

```bash
git checkout -b feature/sdd-slice-01-foundation
```

## 4. Source of truth:

Use these documents as source of truth:

```text
baseline/intent/sdd/README.md
baseline/intent/sdd/platform-build-plan.md
baseline/intent/sdd/service-build-order.md
baseline/intent/sdd/slices/slice-01-foundation.md
baseline/intent/agent-playbooks/common/architecture-guardrails.md
baseline/intent/agent-playbooks/common/task-template.md
baseline/intent/agent-playbooks/common/review-checklist.md
baseline/intent/agent-playbooks/gpt-codex/AGENTS.md
```

Also review the existing service specifications and briefs under:

```text
baseline/intent/id-ms/
baseline/intent/ic-ms/
baseline/intent/icb-ms/
baseline/intent/ii-ms/
baseline/intent/ia-ms/
baseline/intent/e2e/
```

## 5. Required implementation:

Create the platform foundation skeleton for these services:

```text
services/id-ms/
services/ic-ms/
services/icb-ms/
services/ii-ms/
services/ia-ms/
```

Each service must include:

- application entry point
- `/health` endpoint
- `/ready` endpoint
- common error response model usage
- correlation ID handling
- structured logging scaffold
- configuration scaffold
- unit test scaffold
- component test scaffold
- contract test scaffold

Create shared foundation modules for:

- event envelope scaffold
- outbox scaffold
- inbox scaffold
- idempotency scaffold
- Kafka producer scaffold
- Kafka consumer scaffold
- correlation ID middleware or equivalent request context handling
- common error model
- health and readiness support

Create local runtime support for:

- Docker Compose
- Kafka or Redpanda local dependency
- local service startup
- smoke test command

Create test support for:

- unit tests
- component tests
- contract tests
- e2e smoke tests

## 6. Required behaviour:

The foundation must prove these behaviours:

1. Each service can start locally.
2. Each service exposes `/health`.
3. Each service exposes `/ready`.
4. Each service accepts a correlation ID header.
5. Each service returns a correlation ID header.
6. Each service uses the same error response shape.
7. Kafka producer and consumer scaffolds compile.
8. Outbox and inbox scaffolds compile.
9. Smoke test passes locally.
10. Test commands are documented.

## 7. Explicit constraints:

Do not implement domain workflows in this slice.

Do not implement:

- full TMF921 runtime APIs
- full Intent Definition APIs
- optimiser integration
- network apply integration
- assurance decisioning
- callback interpretation logic
- lifecycle transition logic beyond simple skeleton placeholders
- business validation rules
- production retry or compensation logic

Do not change:

- public API paths already defined in architecture documents
- event names
- Kafka topic names
- lifecycle state names
- service ownership boundaries
- optimiser callback ownership
- network callback ownership

Do not introduce:

- orchestration ownership into Intent MS
- synchronous coupling where an event boundary is specified
- direct service-to-service shortcuts that bypass the agreed architecture
- observability fields inside optimiser request or response payloads
- hidden business logic inside outbox or inbox scaffolds

## 8. Ownership guardrails:

Preserve these ownership boundaries:

| Area | Owner |
|---|---|
| Intent definition catalogue | ID MS |
| Runtime intent admission and lifecycle projection | IC MS |
| Optimisation decisioning and optimiser result consumption | II MS |
| Network apply, assurance evidence and assurance events | IA MS |
| Callback ingestion and structural relay | ICB MS |

Specific rules:

- ICB MS may ingest callback submissions and relay accepted callback events.
- ICB MS must not interpret optimisation meaning or assurance meaning.
- II MS consumes optimisation status callbacks, including optimiser outcomes.
- IA MS consumes execution and assurance callbacks.
- IA MS emits `IntentAssuranceEvent`.
- II MS evaluates degraded-state action after assurance feedback.

## 9. Expected repository shape:

Codex should propose a clean implementation structure. A suggested shape is:

```text
services/
  id-ms/
  ic-ms/
  icb-ms/
  ii-ms/
  ia-ms/
libs/
  common/
    correlation/
    errors/
    events/
    health/
    idempotency/
    inbox/
    logging/
    outbox/
    kafka/
platform/
  docker-compose.yml
  kafka/
  observability/
  helm/
tests/
  smoke/
  contract/
  component/
```

If the repository already has a different implementation structure, follow the existing style and explain any deviations in the PR.

## 10. Test evidence required:

The PR must include evidence for:

```text
unit tests pass
component tests pass
contract test scaffold present
smoke test passes
all services expose /health
all services expose /ready
correlation ID is returned
common error model is used
no domain workflows were implemented
```

## 11. PR output required:

Open a pull request with:

- summary of what was created
- changed file list
- how to run locally
- how to run tests
- test evidence
- known gaps
- confirmation that no domain workflow was implemented
- confirmation that service ownership boundaries were preserved

## 12. Review checklist:

The reviewer must confirm:

- Slice 01 scope was followed.
- No domain workflows were implemented.
- No architecture ownership boundary was moved.
- No event name, topic name or lifecycle state was renamed.
- Outbox and inbox are scaffolds only.
- Correlation ID handling is consistent.
- Health and readiness endpoints work across all services.
- Local runtime instructions are clear.
- Tests and smoke checks are included.
- The PR includes test evidence.

## 13. Completion rule:

Slice 01 is complete only when the foundation skeleton can be run locally, tested, reviewed and merged without introducing domain behaviour.
