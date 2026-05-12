# contextdump.md

## Baseline update — IA MS input and callback field cleanup

Baselined on 2026-05-12 from fresh GitHub IA specification/design/internal event reads.

IA MS input events are `IntentNetworkReadyEvent` and `IntentCallbackEvent` only, plus runtime metrics/observation facts from observability endpoints. Remove `IntentOptimisedEvent` from IA MS design/spec input lists and IA handling examples. IA obtains selected/apply resource context from `IntentNetworkReadyEvent.serviceConfiguration` and IA stored/applied assurance baseline, not by directly consuming `IntentOptimisedEvent`.

Callback field names are now generic: `callbackSource`, `callbackTimestamp`, and `sourceState`. `sourceState.state` carries the raw source/orchestrator state such as `APPLIED`, `APPLY_FAILED`, or `TERMINATED`. Do not use `orchestratorState`, `orchestratorSource`, or `orchestratorTimestamp` as baseline callback fields.

Keep `IntentNetworkReadyEvent` produced by `intent-intelligence-ms`.

Keep metrics-first `IntentAssuranceEvent`: do not include `current.evaluations` or `body.evaluations` by default. Use `lifecycleStatus`, `statusReason`, `context`, resource-level `metrics`, `selectionStatus`, `assuranceStatus`, `current.resources` for Active, and `candidates` for Degraded/Failed.

Standardise runtime metric names on `availabilityPercent` and benchmark names on `availabilityBenchmarkPercent`, not `reliabilityPercent`.
