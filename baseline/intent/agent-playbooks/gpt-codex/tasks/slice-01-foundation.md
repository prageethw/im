# GPT Codex Wrapper — Slice 01 Foundation

**Document status:** GPT Codex wrapper for the agent-neutral Slice 01 Foundation task.

## 1. Purpose:

This file tells GPT Codex how to execute the agent-neutral SDD task for Slice 01 Foundation in controlled sub-slices.

The source of truth is the neutral task file. This wrapper must not override the SDD task, platform technology stack or architecture guardrails.

For the first coding run, execute **Slice 01A only**. Do not execute Slice 01B or Slice 01C until the previous sub-slice has passed human review.

## 2. Execute this task:

Read and execute:

- `baseline/intent/sdd/tasks/slice-01-foundation-task.md`

Also read and follow:

- `baseline/intent/agent-playbooks/gpt-codex/AGENTS.md`
- `baseline/intent/agent-playbooks/common/architecture-guardrails.md`
- `baseline/intent/sdd/platform-technology-stack.md`

## 3. GPT Codex execution rules:

- Do not override the neutral SDD task.
- Execute only Slice 01A for the first coding run.
- Do not execute Slice 01B or Slice 01C without the required human approval.
- Do not infer a different technology stack.
- Use Java 21, Spring Boot 3.x and Maven.
- Keep all generated implementation files under `baseline/intent/`.
- Create independent service codebases under `baseline/intent/codebases/{ms}/`.
- Do not create shared implementation libraries.
- Do not create `baseline/intent/services/`.
- Do not create `baseline/intent/libs/`.
- Do not create root-level `intents/`, `services/`, `libs/`, `platform/` or `tests/`.
- Do not implement domain workflows.
- Provide changed files and test evidence.

## 4. Suggested GPT Codex command:

From the repository root:

```bash
codex "Read baseline/intent/agent-playbooks/gpt-codex/tasks/slice-01-foundation.md and execute Slice 01A only from the referenced neutral SDD task. Do not execute Slice 01B or Slice 01C."
```

## 5. Required evidence after run:

Provide the Slice 01A evidence pack:

```text
git status --short
git diff --stat
find baseline/intent/codebases -maxdepth 2 -type d -print
find baseline/intent -maxdepth 2 -type d \( -name codebases -o -name platform -o -name tests -o -name services -o -name libs \) -print
find . -maxdepth 2 -type d \( -name intents -o -name services -o -name libs -o -name platform -o -name tests \) -print
```
