# IA MS Baseline Pack

This document consolidates the currently baselined **IA MS** decision flow contents in Markdown.

## Scope

This pack includes:
- IA MS role and scope
- IA MS inputs and outputs
- IA MS decision stages
- stage-to-event mapping
- decision matrix
- rejection / assurance / no-action rules
- re-decision handoff behaviour

## Notes

- IA MS owns runtime assurance truth.
- IA MS consumes `IntentNetworkReadyEvent` and runtime feedback/telemetry.
- IA MS emits `IntentAssuranceEvent`.
- IA MS provides internal lifecycle/status input toward IC MS.
- IA MS does not perform optimisation decisioning.

---

# 1. IA MS role and scope

## Role
IA MS owns:
- apply/orchestration handoff to the network
- runtime assurance truth
- assurance/control-loop monitoring
- internal lifecycle input from network/application outcome
- `IntentAssuranceEvent`

## Inputs
- `IntentNetworkReadyEvent`
- orchestrator/apply result
- live telemetry / assurance data

## Outputs
- internal lifecycle/status input toward IC MS
- `IntentAssuranceEvent`

## Non-goals
IA MS does not own:
- external intent syntax validation
- semantic interpretation
- policy evaluation
- optimisation decision logic
- external TMF event publication

---

# 2. IA MS decision stages

## 1. Consume network-ready intent
- input: `IntentNetworkReadyEvent`
- IA MS reads target, configuration, observability, and references

## 2. Apply/orchestrate
- IA MS sends the apply-ready configuration to the orchestrator/network target

## 3. Receive apply result
- applied/accepted -> continue to assurance
- rejected/failed -> emit internal lifecycle/status input toward IC MS

## 4. Start assurance/control loop
- IA MS activates monitoring for the configured intent/service context

## 5. Evaluate runtime assurance state
IA MS determines:
- current lifecycle-relevant state
- current active resources
- evaluations
- live metrics
- whether degraded state exists

## 6. Emit assurance truth
- IA MS emits `IntentAssuranceEvent`

## 7. Continue or escalate
- non-degraded -> continue monitoring
- degraded without re-decision need -> continue monitoring, report truth
- degraded with re-decision need -> emit degraded assurance truth and let II MS decide next step

---

# 3. IA MS stage-to-event mapping table

| Stage | Input | Decision | Output |
|---|---|---|---|
| Consume network-ready intent | `IntentNetworkReadyEvent` | accept for IA MS processing | continue internal processing |
| Apply/orchestrate | target + configuration from `IntentNetworkReadyEvent` | can IA MS submit/apply the requested configuration? | continue or lifecycle/status input toward IC MS |
| Receive apply result | orchestrator/network response | was apply accepted / applied / failed / rejected? | continue to assurance or lifecycle/status input toward IC MS |
| Start assurance loop | observability context + telemetry sources | can assurance/control-loop start? | continue monitoring |
| Evaluate runtime assurance state | live telemetry + current applied state | is service non-degraded or degraded? | `IntentAssuranceEvent` |
| Non-degraded monitoring path | non-degraded assurance state | continue monitoring | `IntentAssuranceEvent` non-degraded form |
| Degraded monitoring path | degraded assurance state | is re-decision needed? | `IntentAssuranceEvent` degraded form |
| Re-decision trigger handoff | degraded assurance with re-decision need | include full applicable re-decision set? | degraded `IntentAssuranceEvent` with `candidates` |

---

# 4. IA MS decision matrix

| Checkpoint | Yes | No |
|---|---|---|
| Can IA MS accept the `IntentNetworkReadyEvent` for processing? | continue to apply/orchestrate | emit internal lifecycle/status input toward IC MS |
| Did apply/orchestration succeed or get accepted? | start assurance/control loop | emit internal lifecycle/status input toward IC MS |
| Can assurance/control loop start? | continue monitoring | emit internal lifecycle/status input toward IC MS |
| Is current runtime state degraded? | evaluate re-decision need | emit non-degraded `IntentAssuranceEvent` |
| Is re-decision needed? | emit degraded `IntentAssuranceEvent` with `candidates` | emit degraded `IntentAssuranceEvent` without `candidates` |

---

# 5. Output rules by stage

- apply/orchestration rejected or failed -> internal lifecycle/status input toward IC MS
- apply accepted/applied -> start assurance loop
- non-degraded runtime state -> `IntentAssuranceEvent` without `candidates`
- degraded runtime state without re-decision need -> `IntentAssuranceEvent` without `candidates`
- degraded runtime state with re-decision need -> `IntentAssuranceEvent` with `candidates`

---

# 6. Important locked behaviour

- IA MS is the source of runtime assurance truth
- IA MS does not decide optimisation; II MS does
- IA MS may include `candidates` only when re-decision is needed
- when `candidates` is present, it must include current active resources too

---

# 7. Completion status

This IA MS baseline pack currently covers:
- stage flow
- event outputs
- decision logic
- assurance/no-action behaviour
- re-decision trigger behaviour
