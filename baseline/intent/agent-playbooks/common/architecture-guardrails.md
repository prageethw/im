# Intent Platform Architecture Guardrails

**Document status:** Draft agent-neutral guardrail document.

## 1. Purpose:

This document defines architecture guardrails for engineers and approved coding agents working on the Intent Management Platform.

These guardrails apply regardless of tool. Codex, Claude Code or another approved coding agent must follow the same constraints.

## 2. Source-of-truth rules:

- Use committed architecture documents, service specifications, OpenAPI contracts, event contracts and SDD acceptance criteria as source of truth.
- Do not use generated local artefacts as source of truth when committed files are available.
- Do not change architecture decisions without updating or creating an ADR.
- Do not rename public APIs, event names, topic names, lifecycle states or service ownership boundaries unless explicitly requested.

## 3. Service ownership rules:

- ID MS owns intent specification definition, lifecycle and version management.
- IC MS owns runtime intent admission, validation and lifecycle projection.
- II MS owns reasoning, optimiser request submission and optimisation status interpretation.
- IA MS owns assurance evaluation, apply evidence and assurance event publication.
- ICB MS owns callback submission, structural validation, idempotent ingestion and relay.

## 4. Boundary rules:

- Do not introduce orchestration ownership into Intent MS.
- Do not make IC MS own optimiser outcome interpretation.
- Do not move optimiser callback interpretation out of II MS.
- Do not move network execution callback interpretation out of IA MS.
- Do not make ICB MS semantically interpret callback outcomes.
- Do not introduce synchronous coupling where an event boundary is specified.

## 5. Eventing and reliability rules:

- Use outbox pattern for reliable event publication where required.
- Use inbox or idempotent consumption for reliable event handling where required.
- Preserve correlation identifiers across REST and event boundaries.
- Preserve event identity, source and timestamp fields where specified.
- Do not rename event types unless contracts and consumers are updated under review.

## 6. API rules:

- Do not change public API paths without explicit approval.
- Do not change request or response field names unless the contract is updated and reviewed.
- Validate request payloads against the agreed OpenAPI or schema contract.
- Return errors using the agreed platform error model.
- Implement idempotency where the spec requires it.

## 7. Security rules:

- Do not bypass authentication or authorisation stubs in implementation.
- Do not log secrets, credentials or full sensitive payloads.
- Validate callback source identity where specified.
- Preserve tenant, platform and correlation context where required.

## 8. Observability rules:

- Add structured logs for command receipt, validation, persistence, event publication and event consumption.
- Add metrics for request counts, validation failures, event publication failures and callback ingestion failures.
- Add tracing context propagation across REST and event boundaries where supported.
- Do not add observability fields into optimiser request or response payloads unless the architecture explicitly changes.

## 9. Test rules:

- Add or update tests for every behaviour change.
- Prefer failing tests before implementation for new behaviour.
- Include unit, component and contract tests where applicable.
- Include negative tests for invalid lifecycle transitions and invalid payloads.
- Pull requests must include test evidence.

## 10. Pull request rules:

Every pull request must state:

- Scope implemented.
- Source specs used.
- Changed files.
- Tests run.
- Contract compatibility impact.
- Known limitations.
- Confirmation that guardrails were followed.
