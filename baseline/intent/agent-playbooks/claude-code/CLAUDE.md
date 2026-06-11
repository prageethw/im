# Claude Code Instructions for Intent Platform

**Document status:** Draft tool-specific agent wrapper.

## 1. Purpose:

This file provides Claude Code-specific instructions for working on the Intent Management Platform repository.

The SDD process is agent-neutral. These instructions adapt the common guardrails to Claude Code execution only.

## 2. Operating model:

Use the committed architecture documents, service specifications, OpenAPI contracts, event contracts and SDD artefacts as source of truth.

Before editing files or running commands, understand the requested slice and the relevant architecture boundaries.

Read these first when relevant:

- `agent-playbooks/common/architecture-guardrails.md`
- `agent-playbooks/common/task-template.md`
- Relevant `sdd/acceptance-criteria/*.md`
- Relevant `sdd/slices/*.md`
- Relevant service specification and design brief

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

## 4. Command and edit behaviour:

- Keep edits scoped to the requested task.
- Ask for confirmation before broad refactoring or destructive changes.
- Do not perform unrelated formatting changes.
- Prefer small, reviewable commits or patches.
- Run the narrowest useful tests first, then broader tests if needed.
- Report commands run and their outcomes.

## 5. Test expectations:

For implementation work, add or update tests that prove the requested behaviour.

Expected evidence may include:

- Unit tests.
- Component tests.
- Contract tests.
- Acceptance test updates.
- Local run or CI command output.

## 6. Required response from Claude Code:

Every task result must include:

```text
Summary:
Changed files:
Tests added or updated:
Commands run:
Test results:
Contract impact:
Known limitations:
```

## 7. Review expectation:

Do not present a change as complete unless the implementation matches the source specification and the relevant SDD acceptance criteria.
