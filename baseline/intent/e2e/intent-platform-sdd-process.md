# Spec-Driven Delivery Process for the Intent Management Platform

**Document status:** Draft baseline for engineering adoption  
**Audience:** Architecture, engineering, platform, QA, DevOps and delivery teams  
**Platform:** Intent Management Platform  
**Delivery model:** Architecture-led, contract-first, agent-assisted engineering  

---

## Table of Contents:

- [1. Purpose](#1-purpose)
- [2. Core Principles](#2-core-principles)
  - [2.1 Specification first](#21-specification-first)
  - [2.2 Contracts are executable specifications](#22-contracts-are-executable-specifications)
  - [2.3 Human-owned architecture, agent-assisted implementation](#23-human-owned-architecture-agent-assisted-implementation)
  - [2.4 Build in thin vertical slices](#24-build-in-thin-vertical-slices)
  - [2.5 Do not implement hidden orchestration](#25-do-not-implement-hidden-orchestration)
- [3. Current Artefacts as SDD Inputs](#3-current-artefacts-as-sdd-inputs)
- [4. Recommended Repository Structure](#4-recommended-repository-structure)
- [5. SDD Control Documents](#5-sdd-control-documents)
  - [5.1 Platform build plan](#51-platform-build-plan)
  - [5.2 Agent guardrails](#52-agent-guardrails)
  - [5.3 Definition of Ready](#53-definition-of-ready)
  - [5.4 Definition of Done](#54-definition-of-done)
- [6. Recommended Build Slices](#6-recommended-build-slices)
  - [Slice 1: Foundation skeleton](#slice-1-foundation-skeleton)
  - [Slice 2: ID MS, Librarian For Intents](#slice-2-id-ms-librarian-for-intents)
  - [Slice 3: IC MS, Controller For Intents](#slice-3-ic-ms-controller-for-intents)
  - [Slice 4: ICB MS, Dispatcher For Intents](#slice-4-icb-ms-dispatcher-for-intents)
  - [Slice 5: II MS, Brain For Intents](#slice-5-ii-ms-brain-for-intents)
  - [Slice 6: IA MS, Guardian For Intents](#slice-6-ia-ms-guardian-for-intents)
- [7. Agent Task Template](#7-agent-task-template)
- [8. Agent Adapter Layer](#8-agent-adapter-layer)
  - [8.1 Common agent rules](#81-common-agent-rules)
  - [8.2 Codex adapter](#82-codex-adapter)
  - [8.3 Claude Code adapter](#83-claude-code-adapter)
  - [8.4 Portability rule](#84-portability-rule)
- [9. Pull Request Review Checklist](#9-pull-request-review-checklist)
- [10. Acceptance Criteria Pattern](#10-acceptance-criteria-pattern)
- [11. Contract Testing Strategy](#11-contract-testing-strategy)
  - [11.1 API contracts](#111-api-contracts)
  - [11.2 Event contracts](#112-event-contracts)
  - [11.3 State-machine contracts](#113-state-machine-contracts)
- [12. SDD Workflow](#12-sdd-workflow)
- [13. Architecture Drift Controls](#13-architecture-drift-controls)
- [14. CI Gate Recommendations](#14-ci-gate-recommendations)
- [15. Engineering Operating Model](#15-engineering-operating-model)
- [16. Recommended First Actions](#16-recommended-first-actions)
- [17. Summary](#17-summary)

---

## 1. Purpose:

This paper defines a practical **Spec-Driven Delivery (SDD)** process for building the Intent Management Platform using existing architecture and service artefacts as the delivery source of truth.

The intent is to make engineering delivery faster without losing architectural control. The platform should be implemented from approved specifications, executable contracts, acceptance tests and review gates. Approved agentic coding tools such as Codex, Claude Code or equivalent engineering agents can be used to accelerate implementation, but they must not redefine platform ownership, lifecycle semantics, event routing, API contracts or integration responsibilities.

The recommended operating model is:

> Architecture defines what is correct.  
> SDD defines what to build next.  
> Approved engineering agents accelerate implementation.  
> Automated tests prove the implementation did not drift.

---

## 2. Core Principles:

### 2.1 Specification first:

No feature should be implemented until the relevant specification is clear enough to drive delivery.

A delivery item must identify:

- Service ownership
- API contract
- Event contracts
- State transitions
- Persistence responsibilities
- Error handling
- Security expectations
- Observability expectations
- Acceptance criteria
- Non-goals and prohibited behaviours

### 2.2 Contracts are executable specifications:

OpenAPI, AsyncAPI, JSON Schema, event examples and lifecycle tests are not supporting documents. They are executable contracts and must be treated as delivery gates.

A service implementation is not complete until it passes:

- API contract tests
- Event schema validation
- State transition tests
- Component tests
- Integration tests for the delivery slice
- Regression tests for previously delivered slices

### 2.3 Human-owned architecture, agent-assisted implementation:

Approved engineering agents may implement, refactor, generate tests, create adapters and propose pull requests. This process is tool-neutral. Codex, Claude Code or another approved coding agent may be used when it consumes the same specifications, contracts, acceptance criteria and guardrails.

Agents must not independently change:

- Service boundaries
- API paths
- Event names
- Topic names
- Lifecycle states
- Ownership of callbacks
- Ownership of optimisation decisioning
- Ownership of assurance decisioning
- Retry and compensation semantics
- Security model
- Persistence ownership
- Architecture decisions

Any change to those items requires an Architecture Decision Record (ADR) and human approval.

### 2.4 Build in thin vertical slices:

The platform should not be built as one large programme increment. It should be delivered as thin vertical slices that can be tested end to end.

Each slice should include:

- Contract updates if required
- Service implementation
- Persistence changes
- Event publication and consumption
- Tests
- Deployment configuration
- Operational checks
- Evidence of behaviour

### 2.5 Do not implement hidden orchestration:

The Intent Management Platform governs, validates, reasons, applies and assures intent lifecycle progression. It must not accidentally become a generic runtime orchestrator.

Where the network, optimiser, assurance system or external platform owns execution, the Intent Management Platform should integrate through governed APIs, events and callbacks rather than taking over the execution responsibility.

---

## 3. Current Artefacts as SDD Inputs:

The existing architecture artefacts become the SDD source material. They should be classified as follows.

| Artefact type | SDD role | Engineering use |
|---|---|---|
| Architecture overview | System specification | Defines platform context, boundaries and major flows |
| Solution brief | Behaviour specification | Defines platform responsibilities and end-to-end behaviour |
| Microservice design briefs | Service design specifications | Define each service role, ownership and integration boundaries |
| Microservice detailed specs | Implementation specifications | Drive service build tasks and acceptance criteria |
| OpenAPI files | Executable API contracts | Generate server stubs, clients, contract tests and API documentation |
| Event schemas and examples | Executable event contracts | Validate Kafka events and integration behaviour |
| Lifecycle tables | State-machine specifications | Validate legal and illegal transitions |
| PUML and draw.io diagrams | Visual specifications | Support engineering understanding and review |
| Executive deck | Stakeholder communication | Explains intent and direction, but should not be used as implementation source of truth |
| TMF921 and TMF references | External standards baseline | Validate alignment and terminology |

---

## 4. Recommended Repository Structure:

A practical SDD-enabled repository should separate architecture, contracts, implementation and delivery instructions.

```text
intent-platform/
  architecture/
    adr/
    diagrams/
    decisions/
    overview/

  specs/
    id-ms/
    ic-ms/
    ii-ms/
    ia-ms/
    icb-ms/

  contracts/
    openapi/
    events/
    schemas/
    examples/

  state-machines/
    intent-specification-lifecycle.md
    intent-runtime-lifecycle.md
    assurance-lifecycle.md

  services/
    id-ms/
    ic-ms/
    ii-ms/
    ia-ms/
    icb-ms/

  platform/
    kafka/
    helm/
    observability/
    security/
    local-dev/

  tests/
    contract/
    component/
    integration/
    e2e/
    fixtures/

  sdd/
    platform-build-plan.md
    service-build-order.md
    agent-guardrails.md
    definition-of-ready.md
    definition-of-done.md
    acceptance-criteria/
    slices/
    task-templates/
    review-checklists/

  agent-playbooks/
    common/
      guardrails.md
      pull-request-checklist.md
      test-evidence-template.md
    codex/
      AGENTS.md
      task-template.md
    claude-code/
      CLAUDE.md
      task-template.md
```

---

## 5. SDD Control Documents:

### 5.1 Platform build plan:

The platform build plan defines the intended delivery sequence and dependency order.

It should include:

- Build slices
- Service order
- Contract dependencies
- External integration dependencies
- Test strategy
- Release strategy
- Environments
- Operational readiness checkpoints

### 5.2 Agent guardrails:

The agent guardrails document tells any approved coding agent what it must not change. The same guardrails should be used for Codex, Claude Code and any other approved agent. Tool-specific instruction files should reference this common guardrail set rather than creating different rules for each tool.

Recommended baseline:

```md
# Agent Guardrails

- Do not change architecture decisions unless an ADR is updated.
- Do not rename API paths, event names, topic names or lifecycle states.
- Do not move service ownership boundaries.
- Do not introduce orchestration ownership into the Intent Management Platform.
- Do not move optimiser callback interpretation out of II MS.
- Do not move network execution callback interpretation out of IA MS.
- Do not bypass outbox or inbox patterns.
- Do not add synchronous coupling where an event boundary is specified.
- Do not add observability fields into optimiser request or response payloads unless the relevant spec is changed.
- Do not use old generated files as the source of truth.
- Do not alter public contracts without updating tests and contract versioning.
- Add or update tests for every behaviour change.
- Include changed files, test evidence and risk notes in every pull request.
```

### 5.3 Definition of Ready:

A work item is ready for agent-assisted implementation only when the following are true:

| Readiness item | Required |
|---|---:|
| Service owner is clear | Yes |
| API contract exists or is explicitly not required | Yes |
| Event contracts are identified | Yes |
| State transitions are defined | Yes |
| Acceptance criteria are written | Yes |
| Non-goals are stated | Yes |
| Test expectations are defined | Yes |
| Security expectations are known | Yes |
| Observability expectations are known | Yes |
| Required fixtures or examples are available | Yes |

### 5.4 Definition of Done:

A work item is done only when:

- Code is implemented according to the approved spec
- Public contracts are unchanged unless explicitly approved
- Unit tests pass
- Component tests pass
- API contract tests pass
- Event schema tests pass
- Relevant lifecycle tests pass
- Integration tests pass for the slice
- Observability hooks are present
- Security checks are applied
- Deployment manifests are updated where required
- Pull request includes implementation summary and test evidence
- Human review is complete

---

## 6. Recommended Build Slices:

### Slice 1: Foundation skeleton:

Purpose: establish the platform engineering foundation.

Deliverables:

- Service skeletons
- Common error model
- Health endpoints
- Correlation ID middleware
- Logging conventions
- OpenAPI generation pattern
- Kafka producer and consumer scaffolding
- Outbox pattern baseline
- Inbox pattern baseline
- Local development environment
- Helm chart baseline
- Contract test harness

Suggested agent task:

```text
Create the foundation skeleton for all Intent Management Platform microservices.
Use the approved repository structure and guardrails.
Do not implement domain behaviour yet.
Add health endpoints, correlation ID handling, standard error response handling, Kafka scaffolding, outbox and inbox placeholders, local development configuration and baseline tests.
```

---

### Slice 2: ID MS, Librarian For Intents:

Purpose: implement intent specification ownership.

Deliverables:

- Intent specification create and retrieve APIs
- Draft lifecycle
- Activation lifecycle
- Version assignment rules
- Lineage handling
- Validation against supported schema shape
- Persistence model
- API contract tests
- Lifecycle tests

Suggested agent task:

```text
Implement ID MS according to the ID MS specification and OpenAPI contract.
Do not change public paths, field names or lifecycle states.
Implement draft creation, activation, retrieval, version handling and validation.
Add unit, component and API contract tests.
```

---

### Slice 3: IC MS, Controller For Intents:

Purpose: implement runtime intent admission and lifecycle projection.

Deliverables:

- Runtime intent admission API
- Intent expression validation
- Specification lookup integration
- Runtime lifecycle persistence
- Idempotency handling
- IntentValidatedEvent publication
- IntentRejectedEvent publication where applicable
- Status retrieval API
- API, event and lifecycle tests

Suggested agent task:

```text
Implement IC MS admission according to the IC MS specification, OpenAPI contract and event contracts.
Persist the admitted runtime intent before publishing events.
Use the outbox pattern.
Do not introduce orchestration behaviour.
Do not rename lifecycle states, event names or topic names.
Add unit, component, API contract, event contract and lifecycle tests.
```

---

### Slice 4: ICB MS, Dispatcher For Intents:

Purpose: implement callback ingestion and relay.

Deliverables:

- Callback submission API
- Source state validation
- Structural callback validation
- Idempotent callback ingestion
- Callback persistence
- Outbox relay to callbacks topic
- Kafka publication tests
- Negative validation tests

Suggested agent task:

```text
Implement ICB MS callback submission and relay according to the ICB MS specification.
ICB MS must ingest and relay callback submissions, not interpret domain outcomes.
Publish accepted callbacks to the callbacks topic using the outbox pattern.
Do not move optimisation decisioning or assurance decisioning into ICB MS.
Add API, event and component tests.
```

---

### Slice 5: II MS, Brain For Intents:

Purpose: implement reasoning, optimisation interaction and selected configuration decisioning.

Deliverables:

- Consumption of IntentValidatedEvent
- Optimisation request submission
- Consumption of OptimisationStatusChangeEvent from callbacks topic
- Selected configuration handling
- IntentNetworkReadyEvent publication
- IntentRejectedEvent or governed hold outcome where applicable
- Timeout handling
- Idempotency handling
- Event and component tests

Suggested agent task:

```text
Implement II MS reasoning flow according to the II MS specification and event contracts.
Consume IntentValidatedEvent and OptimisationStatusChangeEvent.
Submit optimisation requests using the approved request contract.
Do not include observability details in optimisation request or response payloads unless explicitly specified.
Produce IntentNetworkReadyEvent when a valid selected configuration is available.
Add unit, component, event contract and integration tests.
```

---

### Slice 6: IA MS, Guardian For Intents:

Purpose: implement application, assurance and lifecycle evidence.

Deliverables:

- Consumption of IntentNetworkReadyEvent
- Network apply boundary integration
- Consumption of execution callbacks from callbacks topic
- Assurance evaluation
- IntentAssuranceEvent publication
- Failed and terminated outcome handling
- Audit and evidence persistence
- Component and integration tests

Suggested agent task:

```text
Implement IA MS application and assurance flow according to the IA MS specification and event contracts.
Consume IntentNetworkReadyEvent and relevant execution callbacks.
Emit IntentAssuranceEvent for assurance outcomes.
Do not move generic retry ownership into IA MS.
Do not consume optimisation callbacks as assurance decisions.
Add unit, component, event contract and integration tests.
```

---

## 7. Agent Task Template:

Every agent task should be constrained and testable. The same task template can be used with Codex, Claude Code or another approved coding agent.

```text
Task title:

Objective:

Source specifications:
- 

Contracts:
- 

Scope:
- 

Out of scope:
- 

Constraints:
- Do not change public API paths.
- Do not rename event fields.
- Do not change lifecycle states.
- Do not move ownership across services.
- Use outbox and inbox patterns where specified.

Required tests:
- Unit tests
- Component tests
- Contract tests
- Event schema tests
- Lifecycle tests
- Integration tests where applicable

Expected pull request evidence:
- Summary of behaviour implemented
- Changed files
- Test commands run
- Test results
- Known limitations
- Risks or assumptions
```

---

## 8. Agent Adapter Layer:

The SDD process is intentionally independent of any single AI coding tool. The repository should keep one common delivery process and a thin adapter layer for each approved agent.

Recommended structure:

```text
agent-playbooks/
  common/
    guardrails.md
    pull-request-checklist.md
    test-evidence-template.md
  codex/
    AGENTS.md
    task-template.md
  claude-code/
    CLAUDE.md
    task-template.md
```

The common folder contains the rules that must not vary by tool. The tool-specific folders only explain how to invoke the agent, where to place local instructions and how to format tasks for that agent.

### 8.1 Common agent rules:

All approved agents must follow the same architecture and delivery rules:

- Use approved architecture documents, service specifications, OpenAPI contracts and event schemas as source of truth.
- Do not change API paths, event names, lifecycle states, topic names or service boundaries unless an ADR explicitly allows it.
- Do not introduce orchestration ownership into the Intent Management Platform.
- Do not move optimiser callback interpretation out of II MS.
- Do not move network execution callback interpretation out of IA MS.
- Do not bypass outbox and inbox patterns.
- Do not add synchronous coupling where an event boundary is specified.
- Add or update tests for every behaviour change.
- Return changed files, test evidence, assumptions and risks.

### 8.2 Codex adapter:

The Codex adapter may include an `AGENTS.md` file and task templates that point back to the common SDD artefacts. Codex-specific instructions should describe how to create branches, prepare pull requests, run tests and report evidence. They should not create different architecture rules.

### 8.3 Claude Code adapter:

The Claude Code adapter may include a `CLAUDE.md` file and command templates that point back to the common SDD artefacts. Claude-specific instructions should describe how to work in the local repository, request permission for commands where required, run tests and report evidence. They should not create different architecture rules.

### 8.4 Portability rule:

A delivery slice is valid only when it can be handed to any approved agent with the same source specifications, contracts, acceptance criteria and guardrails. If a task only works for one tool, the task is too tool-specific and should be rewritten.

---

## 9. Pull Request Review Checklist:

Reviewers should validate both code quality and architecture conformance.

| Review area | Question |
|---|---|
| Scope | Does the PR implement only the requested slice? |
| Contracts | Were API and event contracts preserved? |
| Ownership | Did service boundaries remain intact? |
| Lifecycle | Are state transitions valid? |
| Events | Are consumed and published events correct? |
| Persistence | Is persistence owned by the correct service? |
| Idempotency | Are duplicate commands and events handled safely? |
| Outbox and inbox | Are event reliability patterns followed? |
| Security | Are authentication, authorization and validation expectations met? |
| Observability | Are logs, metrics and traces adequate? |
| Tests | Are the required tests present and passing? |
| Drift | Did Codex alter anything outside the approved scope? |

---

## 10. Acceptance Criteria Pattern:

Acceptance criteria should be written in a way that can become tests.

Example:

```gherkin
Feature: Runtime intent admission

Scenario: Valid runtime intent is admitted
  Given an active intent specification exists
  And the runtime intent expression is valid
  When the client submits the runtime intent
  Then IC MS persists the runtime intent
  And IC MS assigns the expected lifecycle state
  And IC MS publishes IntentValidatedEvent through the outbox
  And the response contains the runtime intent identifier

Scenario: Runtime intent references an inactive specification
  Given the referenced intent specification is retired
  When the client submits the runtime intent
  Then IC MS rejects the request
  And IC MS does not publish IntentValidatedEvent
  And the response contains a validation error
```

---

## 11. Contract Testing Strategy:

### 11.1 API contracts:

Each service API should be validated against its OpenAPI specification.

Validation should include:

- Required fields
- Optional fields
- Error responses
- Status codes
- Headers
- Idempotency behaviour where applicable
- Backward compatibility

### 11.2 Event contracts:

Each event producer should validate outbound events against schema.
Each event consumer should validate inbound event compatibility.

Validation should include:

- Event type
- Event version
- Source
- Correlation identifiers
- Required payload fields
- Lifecycle state fields
- Rejection of malformed events

### 11.3 State-machine contracts:

Lifecycle tests should verify:

- Legal transitions
- Illegal transitions
- Terminal states
- Reprocessing behaviour
- Duplicate event handling
- Recovery behaviour

---

## 12. SDD Workflow:

The recommended workflow for each slice is:

```text
1. Confirm source specifications
2. Confirm executable contracts
3. Write or update acceptance criteria
4. Ask the selected agent to generate failing tests first
5. Review tests against architecture intent
6. Ask the selected agent to implement until tests pass
7. Run contract and component tests
8. Run slice integration tests
9. Review PR for architecture drift
10. Merge only after evidence is attached
```

---

## 13. Architecture Drift Controls:

Architecture drift is the main risk when using agentic coding.

The following controls are recommended:

- Keep approved specs in the repository
- Require every agent task to reference source specs
- Use protected public contracts
- Run contract tests in CI
- Run event schema tests in CI
- Require ADRs for boundary changes
- Require human approval for lifecycle changes
- Reject PRs that change unrelated files
- Reject PRs that alter semantics without acceptance criteria
- Keep generated implementation separate from approved specifications

---

## 14. CI Gate Recommendations:

Minimum CI gates:

```text
- Format and lint
- Unit tests
- Component tests
- OpenAPI contract tests
- Event schema validation
- State-machine tests
- Integration tests for changed slice
- Security scan
- Container build
- Helm template validation
```

Recommended additional gates:

```text
- Backward compatibility check for contracts
- Architecture conformance tests
- Dependency vulnerability scan
- Test coverage threshold
- Consumer-driven contract tests
- Performance smoke tests
```

---

## 15. Engineering Operating Model:

| Role | Responsibility |
|---|---|
| Architect | Owns architecture decisions, service boundaries and lifecycle semantics |
| Product owner | Owns business priority and acceptance outcomes |
| Tech lead | Owns implementation approach and PR review quality |
| Engineer | Owns code, tests and operational quality |
| QA engineer | Owns acceptance test quality and regression confidence |
| Platform engineer | Owns CI, runtime platform, deployment and observability foundation |
| Approved coding agent | Assists with implementation, tests, refactoring and PR preparation |

An agent is a contributor, not an approver.

---

## 16. Recommended First Actions:

To operationalise this SDD process, the engineering team should start with these actions:

1. Create the `sdd/` folder structure.
2. Add `agent-guardrails.md`.
3. Add `definition-of-ready.md`.
4. Add `definition-of-done.md`.
5. Create one build slice file for foundation skeleton.
6. Create one build slice file for ID MS.
7. Convert IC MS admission behaviour into acceptance criteria.
8. Add initial API contract tests.
9. Add initial event schema tests.
10. Run the first agent task against a narrow, low-risk foundation slice.

---

## 17. Summary:

The Intent Management Platform is well suited to Spec-Driven Delivery because it already has a strong architecture baseline, service decomposition, lifecycle thinking, event boundaries and TMF-aligned API direction.

The next step is to convert the architecture artefacts into an explicit delivery system:

- Current documents become the source of truth.
- SDD files become the delivery instruction layer.
- Approved coding agents become implementation accelerators.
- Tests become the proof layer.
- Human review remains the control point.

The recommended delivery model is:

> Architecture-led.  
> Contract-first.  
> Slice-based.  
> Agent-assisted.  
> Test-proven.  
> Human-governed.
