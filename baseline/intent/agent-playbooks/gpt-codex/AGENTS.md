# Codex Instructions for Intent Platform

**Document status:** Draft tool-specific agent wrapper.

## 1. Purpose:

This file provides Codex-specific instructions for working on the Intent Management Platform repository.

The SDD process is agent-neutral. These instructions adapt the common guardrails to Codex execution only.

## 2. Operating model:

Use the committed architecture documents, service specifications, OpenAPI contracts, event contracts and SDD artefacts as source of truth.

Before making changes:

1. Identify the requested SDD slice or service acceptance criteria.
2. Read the relevant service specification and design brief.
3. Read the relevant API and event contracts.
4. Read `agent-playbooks/common/architecture-guardrails.md`.
5. Limit changes to the requested scope.

## 3. Mandatory constraints:

- Do not change architecture decisions unless the task explicitly asks for an ADR update.
- Do not rename API paths, event names, topic names or lifecycle states.
- Do not introduce orchestration ownership into Intent MS.
- Do not move optimiser callback interpretation out of II MS.
- Do not move network execution callback interpretation out of IA MS.
- Do not make ICB MS perform semantic callback decisioning.
- Do not bypass outbox or inbox patterns where specified.
- Do not introduce synchronous coupling where an event boundary is specified.
- Do not add observability fields into optimiser request or response payloads.

## 4. Implementation rules:

- Prefer test-first implementation for new behaviour.
- Keep public contracts compatible unless explicitly asked to change them.
- Add or update unit, component and contract tests as appropriate.
- Keep changes small and scoped.
- Do not perform unrelated formatting or cleanup.
- Preserve existing filenames and directory structure unless the task explicitly asks for changes.

## 5. Required response from Codex:

Every Codex task result must include:

```text
Summary:
Changed files:
Tests added or updated:
Commands run:
Test results:
Contract impact:
Known limitations:
```

## 6. Pull request expectations:

A pull request created by Codex must be reviewable by engineers. It must include clear test evidence and must not hide architecture changes inside implementation changes.
