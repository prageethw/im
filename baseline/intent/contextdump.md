# contextdump.md

## Baseline update — IA MS generic assurance event and internal context alignment

Baselined on 2026-05-12.

`IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`. IA MS currently consumes it, but consumer identity does not affect producer ownership. IA MS must not produce `IntentNetworkReadyEvent`.

Internal events may use a plain internal `body.context` object when carrying resolved runtime targets, constraints, and preferences. This internal `context` is not the external TMF `Intent.expression` wrapper. For IA, optimisation, and assurance flows, use `body.context.targets`, `body.context.constraints`, and `body.context.preferences` where the event carries resolved runtime context.

`requiresReoptimisation` is not included by default in `IntentAssuranceEvent`. II MS or another authorised decision component reads the assurance event state and decides whether re-interpretation, re-optimisation, or no action is required.

`IntentAssuranceEvent` now uses the more generic assurance model with `body.context`, `body.current.evaluations`, `body.current.resources`, `body.candidates`, and `body.references`. Reusable resource entries use `roles`, `resourceId`, `resourceType`, `resourceClass`, `resourceAttributes`, `relationships`, and `metrics`. `candidates` represents the complete valid candidate resource set known in the assurance/re-decision context at emission time, after applicable scope/policy filtering.

## Baseline update — IA MS degraded assurance candidates model

Baselined on 2026-05-12.

For `Degraded` and similar re-decision states in `IntentAssuranceEvent`, do not include a separate `current` block by default. Instead, include all applicable available resources in `body.candidates`, including the currently used/degraded resource. Candidate entries carry their own runtime metrics and benchmark metrics where available, and use fields such as `roles`, `selectionStatus`, and `assuranceStatus` to identify current, available, degraded, healthy, failed, or unavailable resources.

`body.evaluations` may carry violated/satisfied assurance checks and reference the affected `resourceId`. `requiresReoptimisation` remains omitted by default; II MS or another authorised decision component reads the event state, evaluations, and candidates to decide whether re-interpretation, re-optimisation, reselection, or no action is required.

For `Active`, `current.resources` remains acceptable because there is no re-decision pressure. For `Terminated`, candidates are normally not needed unless reporting final resources.

## Baseline update — IA MS metrics-first IntentAssuranceEvent

Baselined on 2026-05-12.

`IntentAssuranceEvent` is metrics-first by default. Do not include `current.evaluations` or `body.evaluations` by default. Use `lifecycleStatus` and `statusReason` to explain the outcome, and use resource-level `metrics`, `selectionStatus`, and `assuranceStatus` to show the current health/state of each resource.

For `Active`, `body.current.resources` is acceptable because there is no re-decision pressure. Each current resource carries runtime metrics and benchmark metrics where available.

For `Degraded` and `Failed`, do not include a separate `current` block by default. Use `body.candidates` to include the current degraded/failed resource and all applicable alternatives. Each candidate carries `roles`, `selectionStatus`, `assuranceStatus`, `resourceType`, `resourceClass`, `resourceAttributes`, `relationships`, and `metrics`.

`requiresReoptimisation` remains omitted by default. II MS or another authorised decision component reads `lifecycleStatus`, `statusReason`, metrics, and candidates to decide the next action.
