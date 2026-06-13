# Intent SDD delivery change

## Slice identity

- Slice:
- Sub-slice: `01A`, `01B` or `01C`
- Neutral task version:
- Version baseline identifier:
- Prefixed wrapper used:
- Coding agent used:
- Source commit SHA before agent changes:
- Task-file SHA-256:

## Scope confirmation

- [ ] Only one coding agent worked on this slice and branch at a time.
- [ ] Changes are limited to the task-approved write scope.
- [ ] No source-of-truth architecture, SDD, API or event contract file was modified by the coding agent.
- [ ] No existing human changes were discarded.
- [ ] No destructive Git command was used.
- [ ] The coding agent did not commit, push, merge, rebase, tag or change branches.
- [ ] No future sub-slice was implemented early.
- [ ] No shared implementation library was introduced.
- [ ] No service ownership boundary was moved.

## Version and generated-output checks

- [ ] Exact versions match `baseline/intent/sdd/platform-version-baseline.md`.
- [ ] No snapshot, dynamic range or floating container tag is present.
- [ ] Generated implementation contains no agent names, prompts, generation timestamps or machine-specific paths.
- [ ] Old unprefixed wrapper filenames are absent.

## Test and validation evidence

| Check | Result | Evidence or reason |
|---|---|---|
| `./mvnw clean verify` |  |  |
| Line coverage |  |  |
| Branch coverage |  |  |
| Spotless |  |  |
| SpotBugs |  |  |
| CycloneDX SBOM |  |  |
| OWASP Dependency-Check |  |  |
| Gitleaks |  |  |
| Docker image build |  |  |
| Trivy image scan |  |  |
| Helm lint |  |  |
| Slice validator |  |  |

Use only `PASS`, `FAIL` or `NOT RUN`. Explain every `NOT RUN`.

## Architecture review

- [ ] API paths remain unchanged.
- [ ] Event names and topic names remain unchanged.
- [ ] Lifecycle states remain unchanged.
- [ ] Persistence and cache ownership remain service-local.
- [ ] Mocks and stubs are limited to test or local-development scaffolding.
- [ ] Comments explain only non-obvious architectural intent.
- [ ] Known gaps and deferred work are documented.

## Changed files

```text
Paste `git diff --name-only`.
```

## Known gaps and deferred work

Describe any incomplete check, decision or later-slice work.

## Human approval

- Reviewer:
- Review date:
- Decision:
