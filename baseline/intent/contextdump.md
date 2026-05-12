# contextdump.md

## Baseline update — IA MS generic assurance event and internal context alignment

Baselined on 2026-05-12.

`IntentNetworkReadyEvent` is produced by `intent-intelligence-ms`. IA MS currently consumes it, but consumer identity does not affect producer ownership. IA MS must not produce `IntentNetworkReadyEvent`.

Internal events may use a plain internal `body.context` object when carrying resolved runtime targets, constraints, and preferences. This internal `context` is not the external TMF `Intent.expression` wrapper. For IA, optimisation, and assurance flows, use `body.context.targets`, `body.context.constraints`, and `body.context.preferences` where the event carries resolved runtime context.

`requiresReoptimisation` is not included by default in `IntentAssuranceEvent`. II MS or another authorised decision component reads the assurance event state and decides whether re-interpretation, re-optimisation, or no action is required.

`IntentAssuranceEvent` now uses the more generic assurance model with `body.context`, `body.current.evaluations`, `body.current.resources`, `body.candidates`, and `body.references`. Reusable resource entries use `roles`, `resourceId`, `resourceType`, `resourceClass`, `resourceAttributes`, `relationships`, and `metrics`. `candidates` represents the complete valid candidate resource set known in the assurance/re-decision context at emission time, after applicable scope/policy filtering.
