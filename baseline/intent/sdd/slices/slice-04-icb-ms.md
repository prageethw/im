# Slice 04 ICB MS

**Document status:** Initial SDD delivery slice baseline.

## 1. Purpose:

This slice builds ICB MS, the Dispatcher For Intents, to accept external callback submissions and relay them to the platform callbacks topic for IA MS and II MS consumption.

## 2. Depends on:

- `sdd/slices/slice-01-foundation.md`
- `sdd/acceptance-criteria/icb-ms.md`
- `icb-ms/icb_ms_specification.md`
- Callback event contracts.

## 3. In scope:

- `/intent-callback/v1/submissions` endpoint.
- Callback envelope validation.
- Source state preservation.
- Callback idempotency.
- Outbox relay to `t7.intent.management.events.callbacks`.
- Optimisation status callback relay for II MS.
- Network execution callback relay for IA MS.
- Security checks according to the baseline.

## 4. Out of scope:

- Optimiser outcome decisioning.
- Network assurance evaluation.
- Runtime lifecycle projection.
- Intent admission.

## 5. Build tasks:

| ID | Task |
|---|---|
| ICB-SL-001 | Implement callback submission data model and migrations. |
| ICB-SL-002 | Implement callback submission endpoint. |
| ICB-SL-003 | Implement structural validation for callback envelopes. |
| ICB-SL-004 | Implement duplicate detection. |
| ICB-SL-005 | Persist accepted callbacks and outbox records. |
| ICB-SL-006 | Publish callbacks to `t7.intent.management.events.callbacks`. |
| ICB-SL-007 | Add tests for optimiser status callback relay. |
| ICB-SL-008 | Add tests for network execution callback relay. |
| ICB-SL-009 | Add security validation hooks. |
| ICB-SL-010 | Add poison and retry handling tests. |

## 6. Acceptance criteria:

- All criteria in `sdd/acceptance-criteria/icb-ms.md` pass.
- Structurally valid callbacks are accepted and relayed.
- Duplicate callbacks are not relayed as duplicate logical events.
- II MS and IA MS can consume their relevant callback event types from the callbacks topic.
- ICB MS does not interpret business meaning of callback outcomes.

## 7. Test evidence:

- Callback API contract test report.
- Event relay test report.
- Duplicate callback test report.
- Security validation test report.
- Poison handling test report.

## 8. Done when:

ICB MS reliably accepts and relays callbacks while preserving the architecture boundary that interpretation belongs to II MS and IA MS.
