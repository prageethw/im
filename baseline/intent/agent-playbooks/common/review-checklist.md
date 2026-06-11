# Agent-Assisted Pull Request Review Checklist

**Document status:** Draft review checklist.

## 1. Purpose:

This checklist is used for pull requests created or assisted by coding agents. It helps reviewers confirm that implementation work follows the Intent Platform architecture and SDD process.

## 2. Source alignment:

- [ ] Pull request identifies the source specification, design brief or SDD slice.
- [ ] Pull request identifies the OpenAPI and event contracts used.
- [ ] Pull request scope matches the requested task.
- [ ] No unrelated cleanup or opportunistic refactoring is included.

## 3. Architecture boundary check:

- [ ] Service ownership remains correct.
- [ ] No orchestration ownership has been introduced into Intent MS.
- [ ] ICB MS remains structural ingestion and relay only.
- [ ] II MS remains the optimiser outcome interpretation owner.
- [ ] IA MS remains the assurance evaluation owner.
- [ ] IC MS remains runtime admission and lifecycle projection owner.
- [ ] ID MS remains specification definition and version owner.

## 4. Contract check:

- [ ] Public API paths are unchanged unless explicitly approved.
- [ ] Request and response field names are unchanged unless explicitly approved.
- [ ] Event names are unchanged unless explicitly approved.
- [ ] Topic names are unchanged unless explicitly approved.
- [ ] Lifecycle states and transitions are unchanged unless explicitly approved.

## 5. Reliability check:

- [ ] Outbox pattern is used where reliable publication is required.
- [ ] Inbox or idempotent consumption is used where reliable consumption is required.
- [ ] Duplicate commands or callbacks are handled safely.
- [ ] Correlation identifiers are preserved.
- [ ] Retry behaviour does not create duplicate side effects.

## 6. Security check:

- [ ] Authentication and authorisation hooks are present where required.
- [ ] Callback source validation is implemented or stubbed according to the slice scope.
- [ ] Sensitive data is not logged.
- [ ] Validation failures return controlled errors.

## 7. Observability check:

- [ ] Structured logs are present for important state changes.
- [ ] Metrics are present for request, event and callback paths where in scope.
- [ ] Trace or correlation context is propagated.
- [ ] Failure paths are observable.

## 8. Test evidence:

- [ ] Unit tests pass.
- [ ] Component tests pass where applicable.
- [ ] Contract tests pass where applicable.
- [ ] Acceptance criteria are covered.
- [ ] Negative scenarios are tested.
- [ ] Test commands and results are included in the pull request.

## 9. Documentation check:

- [ ] Any changed behaviour is reflected in relevant documentation.
- [ ] ADR is updated if architecture decisions changed.
- [ ] Known limitations are documented.

## 10. Merge decision:

Merge only when:

- Scope is correct.
- Tests pass.
- No architecture drift is present.
- Reviewer is satisfied with contract compatibility and evidence.
