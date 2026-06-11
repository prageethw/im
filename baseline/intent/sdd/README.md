# Intent Platform SDD

**Document status:** Baseline entry point for specification-driven delivery.

## 1. Purpose:

This folder defines the specification-driven delivery process for building the Intent Management Platform.

The SDD process uses the architecture documents, service specifications, OpenAPI contracts, event contracts and acceptance criteria as the source of truth for implementation.

Coding agents such as Codex or Claude Code may assist with implementation, but they must follow the same architecture guardrails, acceptance criteria, contract tests and human review gates.

## 2. Folder structure:

| Folder | Purpose |
|---|---|
| `acceptance-criteria/` | Service-level acceptance criteria used to prove each service behaves correctly. |
| `slices/` | Incremental delivery slices used to build the platform in a controlled order. |
| `platform-build-plan.md` | Overall build approach and delivery model. |
| `service-build-order.md` | Recommended order for implementing the services. |

## 3. Source of truth:

The implementation must be driven by:

| Source | Purpose |
|---|---|
| Architecture overview and solution briefs | Define platform behaviour and ownership boundaries. |
| Service specifications | Define service responsibilities, lifecycle rules and persistence expectations. |
| OpenAPI contracts | Define executable API contracts. |
| Event contracts and schemas | Define executable event boundaries. |
| Lifecycle tables | Define allowed state transitions. |
| Acceptance criteria | Define what must be proven before a slice is complete. |

## 4. Delivery workflow:

Each delivery item should follow this flow:

1. Select a delivery slice.
2. Confirm the relevant service specifications and contracts.
3. Confirm or update acceptance criteria.
4. Create failing tests from the acceptance criteria.
5. Implement the minimum change required to pass the tests.
6. Run unit, component, contract and slice-level tests.
7. Capture test evidence.
8. Complete human review.
9. Merge only when the architecture and contracts remain aligned.

## 5. Agent-assisted implementation:

Agentic coding tools may be used to accelerate implementation.

The agent must:

- follow `agent-playbooks/common/architecture-guardrails.md`
- use the relevant service specification as source of truth
- avoid changing public API paths, event names, lifecycle states or topic names without an ADR
- add or update tests for every behaviour change
- provide changed-file summary and test evidence

Tool-specific instructions are stored outside this folder:

| Tool | Instruction file |
|---|---|
| Codex | `../agent-playbooks/codex/AGENTS.md` |
| Claude Code | `../agent-playbooks/claude-code/CLAUDE.md` |

## 6. Completion rule:

A slice is complete only when:

- acceptance criteria pass
- API and event contracts pass
- lifecycle behaviour is validated
- ownership boundaries are preserved
- test evidence is captured
- human review is complete
