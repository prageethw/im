# Intent Platform Architecture Guardrails

**Document status:** Baseline agent-neutral guardrail document.

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

## 10. Write scope and Git safety rules:

- The selected SDD task defines the only paths that may be created or modified.
- For Slice 01A, write access is limited to:
  - `baseline/intent/codebases/id-ms/`
  - `baseline/intent/platform/`
  - `baseline/intent/tests/`
- Treat all architecture documents, service specifications, OpenAPI contracts, event contracts, SDD files and agent playbooks as read-only unless the task explicitly requests a document change.
- Do not delete, move or rename existing files unless the task explicitly requires it and a human has approved the change.
- Inspect `git status --short` before making changes and preserve all pre-existing human changes.
- Do not run commands that discard work, including `git reset --hard`, `git clean`, broad `git checkout`, broad `git restore` or destructive file removal.
- Do not create, delete or switch branches.
- Do not commit, amend, push, merge, rebase, tag or open a pull request unless a human explicitly requests that action.
- Do not write outside the repository or outside the task's approved paths.
- Stop and report if the requested implementation cannot be completed within the approved write scope.

## 11. Dependency and build reproducibility rules:

- Follow `baseline/intent/sdd/platform-version-baseline.md`.
- Use the Maven Wrapper in every service codebase.
- Pin direct dependency, Maven plugin, container image and Helm chart versions.
- Do not use `SNAPSHOT`, `LATEST`, `RELEASE`, dynamic version ranges, floating tags or unpinned build plugins.
- Use Maven Enforcer to verify Java, Maven and dependency convergence requirements.
- Use only approved dependency repositories already established by the project.
- Do not add a dependency when the Java or Spring standard library provides a clear solution.
- Record selected framework, dependency, plugin and container image versions in the service README and evidence pack.
- Stop and report when a required version choice is not governed by the platform baseline or an existing ADR.

## 12. Validation and supply-chain rules:

- `./mvnw clean verify` is mandatory and must not be skipped.
- The Maven verification lifecycle must enforce formatting, static analysis, tests and coverage thresholds.
- Generate a CycloneDX SBOM for each service.
- Run dependency vulnerability, secret and container image scans before merge.
- Build the service container image and lint the service-owned Helm chart.
- No unresolved critical vulnerability is acceptable.
- High-severity findings require documented human review and approval before merge.
- If Docker, Helm or an external scanner is unavailable, report the check as `NOT RUN`, explain why and do not claim that it passed.
- Preserve the commands executed and concise results in the evidence pack.
- Run `baseline/intent/sdd/validation/validate-slice-01a.sh` for Slice 01A.

## 13. Agent concurrency and generated output hygiene:

- Only one coding agent may modify the same slice and Git branch at a time.
- Do not run GPT Codex and Claude Code concurrently against Slice 01A on the same branch or working tree.
- A human must explicitly hand over the branch before a different agent continues the slice.
- Generated implementation files must not contain agent names, model names, prompts, chat transcripts or generation timestamps.
- Generated implementation files must not contain machine-specific absolute paths such as `/Users/...`, `/home/...` or `C:\\Users\\...`.
- Generated comments must describe architectural intent, not the identity of the tool that created the code.
- Generated code must not include placeholder claims such as `AI generated`, `Generated by Codex` or `Generated by Claude`.
- Build output, temporary agent files, local caches and tool transcripts must not be committed.
- The task version, version-baseline identifier and source commit SHA belong in the evidence pack, not in production source comments.

## 14. Pull request rules:

Every pull request must state:

- Scope implemented.
- Source specs used.
- Changed files.
- Tests run.
- Contract compatibility impact.
- Known limitations.
- Confirmation that guardrails were followed.
