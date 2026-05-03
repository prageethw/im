# Current Intent Enabler Baseline Summary:

## Architecture baseline:

The platform is called **Intent Enabler**.

| Domain / entity | Role |
|---|---|
| OEX & Other Entities | Intent-owner-side consumers that submit intent requirements |
| Intent Enabler | Intent-handler-side platform/domain |
| ID MS / `intent-definition-ms` | Owns `IntentSpecification` design-time contracts |
| IC MS / `intent-controller-ms` | Owns external `Intent`, `IntentReport`, lifecycle/status projection, and TMF-facing APIs/events |
| II MS / `intent-intelligence-ms` | Performs semantic validation, resolution, policy/candidate logic, and optimisation decision preparation |
| IA MS / `intent-assurance-ms` | Owns runtime assurance truth and emits `IntentAssuranceEvent` |
| ICB MS / `intent-callback-ms` | Incoming-only callback mediation service |
| `t7.optimiser` | Optimisation capability |
| `t7.orchestrator` | Applies / updates network configuration |
| `t7.telemetry` | Streams real-time telemetry to IA MS |
| `t7.knowledge plane` | External T7 network knowledge source used by II MS |

## Knowledge baseline:

II MS uses two knowledge sources:

| Knowledge source | Purpose |
|---|---|
| Lightweight II MS KP | Local semantic mappings, human-expression mapping, policy hints, service-specific interpretation |
| External `t7.knowledge plane` | Network-related topology/resource context, telemetry-related context, broader network intelligence for resolution and re-decision |

Neither knowledge source is exposed as the external `Intent` or `IntentSpecification`.

## Human expression baseline:

`humanExpression` may appear on the incoming `Intent`.

`humanExpressionMapping` is part of the lightweight II MS KP and stores interpretation rules, aliases, defaults, and conflict policy.

## Resource roles baseline:

`roles` is optional.

Use only:
- `primary`
- `secondary`

Omit `roles` when it has no meaningful role in the current intent context. Do not use `"roles": []`.

## Status/state baseline:

Expose externally:
- `lifecycleStatus`
- `statusReason`
- `statusChangeDate`

Treat internally:
- runtime state
- network state
- assurance state

## Current pending detailed-design items:

1. Finalise caching and circuit-breaker strategies for each MS.
2. Finalise EDA patterns for each MS.
3. Finalise deployment strategies for each MS.
4. Finalise Kubernetes cluster strategy.
5. Finalise SaaS / PaaS software choices for MS use.
