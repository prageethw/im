# Slice 06 IA MS

**Document status:** Initial SDD delivery slice baseline.

## 1. Purpose:

This slice builds IA MS, the Guardian For Intents, to consume network-ready decisions, coordinate application to the network boundary, evaluate assurance evidence and publish assurance outcomes.

## 2. Depends on:

- `sdd/slices/slice-01-foundation.md`
- `sdd/slices/slice-04-icb-ms.md`
- `sdd/slices/slice-05-ii-ms.md`
- `sdd/acceptance-criteria/ia-ms.md`
- `ia-ms/ia_ms_specification.md`
- Network boundary and assurance callback contracts.

## 3. In scope:

- `IntentNetworkReadyEvent` consumption.
- Application coordination to the governed network boundary.
- Observer configuration handling.
- Network execution callback consumption from callbacks topic.
- Assurance evidence persistence.
- Active, degraded, failed and terminated assurance outcomes.
- `IntentAssuranceEvent` publication.
- Assurance status query.

## 4. Out of scope:

- Optimiser decisioning.
- Optimiser callback interpretation.
- Runtime admission.
- Callback ingress endpoint ownership.
- Generic degraded-state remediation ownership.

## 5. Build tasks:

| ID | Task |
|---|---|
| IA-SL-001 | Implement assurance data model and migrations. |
| IA-SL-002 | Implement `IntentNetworkReadyEvent` consumer. |
| IA-SL-003 | Implement network boundary application adapter or stub. |
| IA-SL-004 | Persist application attempt and correlation metadata. |
| IA-SL-005 | Implement network execution callback consumer. |
| IA-SL-006 | Implement assurance evidence persistence. |
| IA-SL-007 | Emit active assurance event. |
| IA-SL-008 | Emit degraded assurance event. |
| IA-SL-009 | Emit failed assurance event. |
| IA-SL-010 | Emit terminated assurance event. |
| IA-SL-011 | Implement assurance status query. |
| IA-SL-012 | Add network-ready, callback and assurance tests. |

## 6. Acceptance criteria:

- All criteria in `sdd/acceptance-criteria/ia-ms.md` pass.
- IA MS consumes network-ready decisions idempotently.
- IA MS emits `IntentAssuranceEvent` with evidence for active, degraded, failed and terminated outcomes.
- IA MS does not evaluate optimiser status callbacks.
- Degraded outcomes are emitted as evidence for II MS to evaluate the governed action path.

## 7. Test evidence:

- Network-ready consumer test report.
- Network adapter component test report.
- Callback consumer test report.
- Assurance event publication test report.
- Evidence persistence test report.
- Idempotency test report.

## 8. Done when:

IA MS can apply and assure selected configurations, publish assurance outcomes and provide evidence without taking over optimiser or runtime controller responsibilities.
