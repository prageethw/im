# Slice 03 IC MS

**Document status:** Initial SDD delivery slice baseline.

## 1. Purpose:

This slice builds IC MS, the Controller For Intents, to admit runtime intents, validate requests and publish admitted intent events for II MS decisioning.

## 2. Depends on:

- `sdd/slices/slice-01-foundation.md`
- `sdd/slices/slice-02-id-ms.md`
- `sdd/acceptance-criteria/ic-ms.md`
- `ic-ms/ic_ms_specification.md`
- Runtime API contract where available.

## 3. In scope:

- Runtime intent submission.
- Active specification validation through ID MS lookup.
- Runtime expression validation using `body.expression.context`.
- Runtime intent persistence.
- `IntentValidatedEvent` publication.
- Rejection behaviour.
- Runtime status retrieval.
- Lifecycle projection from downstream events where specified.

## 4. Out of scope:

- Optimiser submission.
- Optimiser callback interpretation.
- Network application.
- Assurance evaluation.
- External callback ingestion.

## 5. Build tasks:

| ID | Task |
|---|---|
| IC-SL-001 | Implement runtime intent data model and migrations. |
| IC-SL-002 | Implement runtime intent submission endpoint. |
| IC-SL-003 | Integrate active specification lookup with ID MS. |
| IC-SL-004 | Implement expression validation for canonical runtime context. |
| IC-SL-005 | Persist admitted runtime intent before event publication. |
| IC-SL-006 | Publish `IntentValidatedEvent` through outbox. |
| IC-SL-007 | Implement invalid request and rejection behaviour. |
| IC-SL-008 | Implement runtime status retrieval endpoint. |
| IC-SL-009 | Implement lifecycle projection from agreed events. |
| IC-SL-010 | Add API, event and lifecycle tests. |

## 6. Acceptance criteria:

- All criteria in `sdd/acceptance-criteria/ic-ms.md` pass.
- A valid runtime intent produces exactly one admitted runtime record and one logical `IntentValidatedEvent`.
- Invalid requests do not trigger downstream decisioning.
- Runtime lifecycle status is retrievable and consistent with consumed downstream state.

## 7. Test evidence:

- Runtime API contract test report.
- Event publication test report.
- ID MS lookup integration test report.
- Lifecycle projection test report.
- Idempotency test report.

## 8. Done when:

IC MS can admit valid runtime intents, reject invalid ones and publish decisioning-ready events without owning optimiser, network or assurance responsibilities.
