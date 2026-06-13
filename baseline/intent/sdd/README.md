# Intent Platform SDD

**Document status:** Baseline entry point for specification-driven delivery.

## 1. Purpose:

This folder defines the specification-driven delivery process for building the Intent Management Platform.

The SDD process uses the architecture documents, service specifications, OpenAPI contracts, event contracts, platform technology stack and acceptance criteria as the source of truth for implementation.

Approved coding agents may assist with implementation, but they must follow the same architecture guardrails, acceptance criteria, contract tests and human review gates.

## 2. Folder structure:

| Folder or file | Purpose |
|---|---|
| `README.md` | Entry point for the SDD process. |
| `platform-build-plan.md` | Overall build approach and delivery model. |
| `service-build-order.md` | Recommended service implementation order. |
| `platform-technology-stack.md` | Mandatory implementation stack and repository structure baseline. |
| `platform-version-baseline.md` | Exact approved versions for runtimes, frameworks, containers and validation tools. |
| `acceptance-criteria/` | Service-level acceptance criteria used to prove each service behaves correctly. |
| `slices/` | Incremental delivery slices used to build the platform in a controlled order. |
| `tasks/` | Agent-neutral execution tasks for delivery slices. |
| `validation/` | Automated SDD validation scripts. |
| `templates/` | Review and delivery templates. |

## 3. Source of truth:

The implementation must be driven by:

| Source | Purpose |
|---|---|
| Architecture overview and solution briefs | Define platform behaviour and ownership boundaries. |
| Service specifications | Define service responsibilities, lifecycle rules and persistence expectations. |
| OpenAPI contracts | Define executable API contracts. |
| Event contracts and schemas | Define executable event boundaries. |
| Lifecycle tables | Define allowed state transitions. |
| Platform technology stack | Defines implementation stack, runtime platform and repository structure. |
| Platform version baseline | Defines exact approved versions and image tags. |
| Acceptance criteria | Define what must be proven before a slice is complete. |
| Agent-neutral tasks | Define what an approved coding agent may implement for a slice. |

## 4. Delivery workflow:

Each delivery item should follow this flow:

1. Select a delivery slice.
2. Confirm the relevant service specifications and contracts.
3. Confirm the platform technology stack, exact version baseline and repository structure.
4. Confirm or update acceptance criteria.
5. Create failing tests from the acceptance criteria.
6. Implement the minimum change required to pass the tests.
7. Run unit, component, contract and slice-level tests.
8. Capture test evidence.
9. Complete human review.
10. Merge only when the architecture and contracts remain aligned.

## 5. Agent-assisted implementation:

Approved coding agents may be used to accelerate implementation.

The agent must:

- follow `../agent-playbooks/common/architecture-guardrails.md`
- follow `platform-technology-stack.md`
- follow `platform-version-baseline.md`
- run the relevant script under `validation/`
- use the relevant service specification as source of truth
- use the relevant agent-neutral task under `tasks/`
- avoid changing public API paths, event names, lifecycle states or topic names without an ADR
- add or update tests for every behaviour change
- provide changed-file summary and test evidence

Tool-specific wrappers are stored outside this folder:

| Tool | Instruction file |
|---|---|
| GPT Codex | `../agent-playbooks/gpt-codex/AGENTS.md` |
| Claude Code | `../agent-playbooks/claude-code/CLAUDE.md` |

Tool-specific task wrappers are stored under:

| Tool | Wrapper folder |
|---|---|
| GPT Codex | `../agent-playbooks/gpt-codex/tasks/` |
| Claude Code | `../agent-playbooks/claude-code/tasks/` |

## 6. Completion rule:

A slice is complete only when:

- acceptance criteria pass
- API and event contracts pass
- lifecycle behaviour is validated
- ownership boundaries are preserved
- implementation follows the platform technology stack
- generated code remains under approved repository paths
- test evidence is captured
- human review is complete
