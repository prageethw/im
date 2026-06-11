# Agent Task Template

**Document status:** Draft agent-neutral task template.

## 1. Purpose:

Use this template when assigning implementation work to an approved coding agent such as Codex, Claude Code or another authorised tool.

## 2. Task header:

```text
Task title:
Service or slice:
Repository path:
Source branch:
Target branch:
```

## 3. Source artefacts:

List the exact artefacts the agent must use.

```text
Architecture documents:
Service specifications:
OpenAPI contracts:
Event contracts:
Acceptance criteria:
Existing tests:
```

## 4. Scope:

Describe only what the agent should change.

```text
Implement:
- 
- 

Do not implement:
- 
- 
```

## 5. Architecture constraints:

```text
- Do not change API paths.
- Do not rename event names or lifecycle states.
- Do not change service ownership boundaries.
- Do not introduce orchestration behaviour into Intent MS.
- Use outbox and inbox patterns where specified.
- Preserve correlation identifiers.
```

Add service-specific constraints as needed.

## 6. Expected implementation:

```text
Code changes:
Tests:
Configuration:
Documentation updates:
```

## 7. Acceptance criteria:

```text
The task is complete when:
- 
- 
- 
```

## 8. Required evidence:

The agent must return:

```text
Changed files:
Tests added or updated:
Commands run:
Test results:
Contract compatibility notes:
Known limitations:
```

## 9. Review checklist:

Before merge, a human reviewer must confirm:

- The implementation matches the source specification.
- The implementation does not drift from service ownership boundaries.
- Public contracts remain compatible or approved changes are documented.
- Tests cover success and failure paths.
- Observability and security baseline requirements are included.
