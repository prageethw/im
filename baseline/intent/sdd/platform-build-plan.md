# Intent Platform Build Plan

**Document status:** Draft build-driving SDD artefact.

## 1. Purpose:

This document defines the staged build plan for the Intent Management Platform. It turns the architecture baseline, service specifications, API contracts, event contracts and lifecycle decisions into an implementation sequence that engineers and approved coding agents can follow.

The build plan is agent-neutral. Codex, Claude Code or another approved coding agent may be used, provided the same source artefacts, guardrails, tests and review gates are followed.

## 2. Source of truth:

Implementation must be driven from the committed architecture artefacts under `baseline/intent`.

The authoritative inputs are:

| Artefact type | Location | Purpose |
|---|---|---|
| Platform architecture | `baseline/intent/e2e/` | Cross-service architecture, integration flow and operating model. |
| Service specifications | `baseline/intent/*-ms/` | Service ownership, APIs, events, persistence and lifecycle rules. |
| OpenAPI contracts | Service folders or contract folders | Executable REST API contracts. |
| Event contracts | E2E and service specification artefacts | Event names, payload structures and topic routing. |
| SDD acceptance criteria | `baseline/intent/sdd/acceptance-criteria/` | Behaviour that must be proven before a slice is accepted. |
| SDD slices | `baseline/intent/sdd/slices/` | Build order and scope control. |
| Agent playbooks | `baseline/intent/agent-playbooks/` | Tool-specific execution instructions and common guardrails. |

## 3. Build principles:

The platform must be built contract-first and test-first.

Core principles:

- Architecture documents define what is correct.
- SDD slices define what is built next.
- OpenAPI and event contracts define executable boundaries.
- Tests prove the implementation has not drifted.
- Coding agents accelerate implementation but do not own architecture decisions.
- Humans retain ownership of lifecycle semantics, service boundaries, event routing and operational trade-offs.

## 4. Delivery sequence:

The recommended delivery sequence is:

| Order | Slice | Primary outcome |
|---:|---|---|
| 1 | Foundation | Common engineering baseline, service scaffolds, local runtime, shared patterns and test harness. |
| 2 | ID MS | Intent specification registry, versioning and lifecycle baseline. |
| 3 | IC MS | Runtime intent admission, validation, lifecycle projection and event publication. |
| 4 | ICB MS | Callback ingestion, structural validation and callback event relay. |
| 5 | II MS | Reasoning flow, optimiser request submission, optimiser status callback consumption and selected configuration output. |
| 6 | IA MS | Network apply, assurance evaluation, lifecycle evidence and assurance event publication. |

## 5. Engineering gates:

Each slice must pass these gates before merge:

1. The source specification is identified.
2. Public API and event contracts are not renamed without ADR approval.
3. Unit tests pass.
4. Component tests pass.
5. Contract tests pass.
6. Slice-level acceptance criteria are satisfied.
7. Security and observability requirements are implemented for the slice.
8. Pull request includes changed files, test evidence and known limitations.
9. Human review confirms no architecture drift.

## 6. Agent execution model:

Coding agents may implement code, tests, migrations, documentation updates and build scripts. They must not decide service ownership or architecture semantics.

The preferred flow is:

```text
1. Select SDD slice.
2. Select service acceptance criteria.
3. Confirm source specs and contracts.
4. Ask agent to create or update failing tests.
5. Ask agent to implement only the scoped behaviour.
6. Run tests locally or in CI.
7. Review changed files and test evidence.
8. Merge only after human approval.
```

## 7. Architecture constraints:

The following constraints apply to all slices:

- Intent MS must not become a runtime network orchestrator.
- IC MS owns runtime intent admission and lifecycle projection.
- ID MS owns intent specification definition and version lifecycle.
- ICB MS owns callback ingestion and relay, not semantic decisioning.
- II MS owns reasoning and optimisation outcome interpretation.
- IA MS owns assurance evaluation and assurance event publication.
- Optimiser callback outputs are consumed by II MS through the callback event path.
- Network execution and assurance callbacks are consumed by IA MS through the callback event path.
- Outbox and inbox patterns must be used where event publication or consumption needs reliability.
- No synchronous coupling should be introduced where the architecture specifies an event boundary.

## 8. Definition of done:

A slice is done when:

- Code implements the approved scope only.
- Tests prove expected behaviour and important failure paths.
- Public contracts remain compatible or approved changes are documented.
- Observability, correlation and audit requirements are present.
- The service can run locally or in the agreed development environment.
- The pull request includes test evidence and architecture-drift notes.

## 9. Non-goals:

This plan does not replace detailed service specifications, OpenAPI contracts, event schemas or ADRs. It provides the build control layer that connects those artefacts to implementation.
