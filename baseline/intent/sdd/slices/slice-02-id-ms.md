# Slice 02 ID MS

**Document status:** Initial SDD delivery slice baseline.

## 1. Purpose:

This slice builds ID MS, the Librarian For Intents, using the ID MS acceptance criteria and the agreed TMF921-aligned specification model.

## 2. Depends on:

- `sdd/slices/slice-01-foundation.md`
- `sdd/acceptance-criteria/id-ms.md`
- `id-ms/id_ms_specification.md`
- ID MS OpenAPI contract where available.

## 3. In scope:

- Intent specification create, read and update flows.
- Draft lifecycle.
- Activation and official version assignment.
- Specification lineage.
- Active specification lookup.
- Retired specification handling.
- API and persistence tests.

## 4. Out of scope:

- Runtime intent admission.
- Optimiser integration.
- Callback ingestion.
- Network assurance.

## 5. Build tasks:

| ID | Task |
|---|---|
| ID-SL-001 | Implement ID MS data model and persistence migrations. |
| ID-SL-002 | Implement create draft specification endpoint. |
| ID-SL-003 | Implement retrieve specification by id. |
| ID-SL-004 | Implement retrieve specification by key and version. |
| ID-SL-005 | Implement update draft specification behaviour. |
| ID-SL-006 | Implement activation behaviour with official version assignment. |
| ID-SL-007 | Implement retire behaviour. |
| ID-SL-008 | Implement active specification lookup for runtime consumers. |
| ID-SL-009 | Add validation and error mapping. |
| ID-SL-010 | Add unit, component and API contract tests. |

## 6. Acceptance criteria:

- All criteria in `sdd/acceptance-criteria/id-ms.md` pass.
- The implementation preserves specification lineage across versions.
- Only active specifications can be used for new runtime intents.
- Draft and retired specifications remain auditable.
- Duplicate create requests are idempotent where the API contract requires idempotency.

## 7. Test evidence:

- API contract test report.
- Specification lifecycle test report.
- Persistence migration test report.
- Idempotency test report.

## 8. Done when:

ID MS can manage specification lifecycle from draft to active to retired, and IC MS can reliably resolve active specifications for runtime admission.
