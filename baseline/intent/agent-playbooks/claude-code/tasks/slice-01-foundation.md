# Claude Code Wrapper — Slice 01 Foundation

**Document status:** Claude Code wrapper for the agent-neutral Slice 01 Foundation task.

## 1. Purpose:

This file tells Claude Code how to execute the agent-neutral SDD task for Slice 01 Foundation.

The source of truth is the neutral task file. This wrapper must not override the SDD task, platform technology stack or architecture guardrails.

## 2. Execute this task:

Read and execute:

- `baseline/intent/sdd/tasks/slice-01-foundation-task.md`

Also read and follow:

- `baseline/intent/agent-playbooks/claude-code/CLAUDE.md`
- `baseline/intent/agent-playbooks/common/architecture-guardrails.md`
- `baseline/intent/sdd/platform-technology-stack.md`

## 3. Claude Code execution rules:

- Do not override the neutral SDD task.
- Do not infer a different technology stack.
- Use Java 21, Spring Boot 3.x and Maven.
- Inspect the repository structure before creating files.
- Keep all generated implementation files under `baseline/intent/`.
- Create independent service codebases under `baseline/intent/codebases/{ms}/`.
- Do not create shared implementation libraries.
- Do not create `baseline/intent/services/`.
- Do not create `baseline/intent/libs/`.
- Do not create root-level `intents/`, `services/`, `libs/`, `platform/` or `tests/`.
- Do not implement domain workflows.
- Provide changed files and test evidence.

## 4. Suggested Claude Code command:

From the repository root:

```bash
claude "Read baseline/intent/agent-playbooks/claude-code/tasks/slice-01-foundation.md and execute the referenced neutral SDD task."
```

## 5. Required evidence after run:

Provide:

```text
git status --short
git diff --stat
find baseline/intent/codebases -maxdepth 2 -type d -print
find baseline/intent -maxdepth 2 -type d \( -name codebases -o -name platform -o -name tests -o -name services -o -name libs \) -print
find . -maxdepth 2 -type d \( -name intents -o -name services -o -name libs -o -name platform -o -name tests \) -print
```
