# End-to-End Platform Flow Pack

This document consolidates the currently baselined **end-to-end platform flow** across IC MS, II MS, optimiser, IA MS, KP, and external projection.

## Scope

This pack includes:
- happy path
- rejection path
- degraded / re-decision path
- no-action degraded path
- event chain summaries
- ownership summary

## Notes

- IC MS owns the external intent/resource projection.
- II MS owns semantic interpretation, policy evaluation, candidate discovery, and optimisation trigger decisions.
- IA MS owns apply/orchestration handoff and runtime assurance truth.
- KP / Master Knowledge Config is internal II MS knowledge, not an external intent resource.

---

# 1. Happy path

## Steps

1. **Intent request enters IC MS**
   - client sends external `Intent`
   - IC MS validates syntax against active `IntentSpecification`

2. **IC MS emits validated handoff**
   - IC MS emits `IntentValidatedEvent`

3. **II MS interprets and evaluates**
   - resolves semantic meaning
   - resolves location/service context
   - applies policy rules
   - discovers applicable candidates from KP

4. **II MS decides optimisation path**
   - if optimisation is required -> emit `IntentResolvedEvent`
   - if optimisation is not required -> emit `IntentNetworkReadyEvent`

5. **Optimiser runs when needed**
   - optimiser consumes `IntentResolvedEvent`
   - optimiser emits `IntentOptimisedEvent`

6. **II MS produces apply-ready handoff**
   - II MS consumes optimiser outcome when relevant
   - II MS emits `IntentNetworkReadyEvent`

7. **IA MS applies to network**
   - IA MS consumes `IntentNetworkReadyEvent`
   - applies/orchestrates configuration
   - receives apply result

8. **IA MS starts assurance**
   - starts assurance/control loop
   - emits `IntentAssuranceEvent`

9. **IC MS updates external state/reporting**
   - consumes internal lifecycle/runtime truth
   - updates external `Intent`
   - updates external `IntentReport`
   - emits external TMF-style events as needed

## Happy-path event chain

```text
External Intent request
-> IC MS validates
-> IntentValidatedEvent
-> II MS semantic/policy/candidate processing
-> IntentResolvedEvent (if optimisation needed)
-> IntentOptimisedEvent
-> IntentNetworkReadyEvent
-> IA MS apply/orchestrate
-> IntentAssuranceEvent
-> IC MS external state/report projection
```

---

# 2. Rejection path

## Steps

1. **Intent request enters IC MS**
   - client sends external `Intent`
   - IC MS validates syntax against active `IntentSpecification`

2. **IC MS emits validated handoff**
   - IC MS emits `IntentValidatedEvent`

3. **II MS attempts semantic interpretation**
   - may fail at unresolved location
   - may fail at unsupported service meaning
   - may fail at contradictory request meaning
   - may fail at missing required context

4. **II MS evaluates policy**
   - may fail at location not allowed
   - may fail at priority not allowed
   - may fail at service class not allowed
   - may fail at policy restriction violation

5. **II MS checks candidates**
   - may fail at no valid applicable candidate set
   - may fail at unsatisfied optimisation preconditions

6. **II MS emits rejection**
   - II MS emits `IntentRejectedEvent`

7. **IC MS updates external lifecycle**
   - consumes internal rejection/lifecycle input
   - updates external `Intent.lifecycleStatus`
   - may emit external status-change event

## Rejection-path event chain

```text
External Intent request
-> IC MS validates
-> IntentValidatedEvent
-> II MS semantic / policy / candidate processing
-> IntentRejectedEvent
-> IC MS external lifecycle update
```

---

# 3. Degraded / re-decision path

## Steps

1. **IA MS is already monitoring**
   - configuration has been applied
   - assurance/control loop is running

2. **IA MS detects degraded runtime state**
   - lifecycle-relevant state is `Degraded`
   - determines current active resources
   - determines current evaluations
   - determines live metrics

3. **IA MS decides whether re-decision is needed**
   - degraded, but no re-decision needed yet
   - degraded, and re-decision needed

4. **IA MS emits assurance truth**
   - non-redecision degraded case:
     - emit `IntentAssuranceEvent` degraded form without `candidates`
   - re-decision degraded case:
     - emit `IntentAssuranceEvent` degraded form with `candidates`

   Locked rule:
   - when `candidates` is present, it includes the current active resources too

5. **II MS consumes degraded assurance truth**
   - decides no action, or
   - performs fresh semantic/policy/candidate pass leading to new `IntentResolvedEvent`

6. **Optimiser runs again when needed**
   - optimiser consumes new `IntentResolvedEvent`
   - emits `IntentOptimisedEvent`

7. **II MS emits new network-ready handoff**
   - emits new `IntentNetworkReadyEvent`

8. **IA MS applies updated configuration**
   - applies the new selected configuration
   - assurance loop continues

9. **IC MS updates external state/reporting**
   - updates external `Intent` / `IntentReport` as needed

## Degraded / re-decision event chain

```text
IA MS monitoring
-> degraded detected
-> IntentAssuranceEvent (degraded)
-> II MS evaluates re-decision need
-> IntentResolvedEvent
-> IntentOptimisedEvent
-> IntentNetworkReadyEvent
-> IA MS re-apply/orchestrate
-> continued assurance
```

---

# 4. No-action degraded path

## Steps

1. IA MS detects degraded runtime state
2. IA MS emits `IntentAssuranceEvent` degraded form without `candidates`
3. II MS decides no action
4. IA MS continues monitoring
5. IC MS may continue external reporting/lifecycle projection

## No-action degraded chain

```text
IA MS monitoring
-> degraded detected
-> IntentAssuranceEvent (degraded, no candidates)
-> II MS no action
-> continued assurance / reporting
```

---

# 5. Ownership summary

## IC MS
Owns:
- external `Intent`
- external `IntentReport`
- external TMF-style event projection
- syntactic validation handoff into internal flow

## II MS
Owns:
- semantic interpretation
- policy evaluation
- candidate discovery
- optimisation trigger decision
- internal outputs:
  - `IntentResolvedEvent`
  - `IntentRejectedEvent`
  - `IntentNetworkReadyEvent`

## Optimiser
Owns:
- optimisation execution
- output:
  - `IntentOptimisedEvent`

## IA MS
Owns:
- apply/orchestration handoff
- runtime assurance truth
- `IntentAssuranceEvent`
- internal lifecycle/status input toward IC MS

## KP
Provides:
- internal knowledge for II MS
- locations
- services
- policy rules
- resources
- optimisation profiles
- human expression mapping
- behaviour and resolution rules

---

# 6. Important locked behaviour

- non-degraded `IntentAssuranceEvent` does not require a new `IntentResolvedEvent`
- degraded `IntentAssuranceEvent` only drives re-decision when needed
- degraded `candidates`, when present, must include current active resources too
- KP is internal fulfilment knowledge, not an external intent resource
