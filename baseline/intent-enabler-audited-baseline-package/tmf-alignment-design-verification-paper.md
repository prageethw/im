# TMF Alignment Design Verification Paper

## Document purpose:

This paper provides a stakeholder-ready design verification point showing how the current Intent Enabler architecture aligns with the TM Forum Intent Ontology (TIO) and the TMF intent-management model.

It is intended to support architecture review, governance, and stakeholder alignment across product, engineering, assurance, and platform teams.

## Source reference:

Primary TMF source used for this verification:

- TM Forum Technical Report TR292, *TM Forum Intent Ontology (TIO)*, version 3.6.0, approved 04-Jul-2024.

## Executive summary:

The current Intent Enabler architecture is broadly aligned with the TMF intent model.

The architecture treats the Intent Enabler as the intent-handler-side platform that receives intent requirements from a client or OEX-side actor, validates them against an active IntentSpecification, interprets them through an internal intelligence and knowledge layer, applies the resulting network configuration, monitors runtime assurance, and reports back through external Intent and IntentReport projections.

The key alignment point is that the external model remains TMF-facing, while internal microservices, events, optimisation, telemetry, and knowledge-plane processing are implementation mechanisms used to fulfil the intent.

## 1. TMF concepts used as alignment anchors:

### 1.1 Intent:

In TMF TIO, intent is the information object used to tell an autonomous network or system what requirements it needs to meet.

Architecture alignment:

- The external `Intent` resource represents the requirement submitted by the client/OEX actor.
- The Intent Enabler fulfils that requirement through internal validation, interpretation, optimisation, apply, and assurance.
- The internal event chain does not replace the external Intent resource; it supports fulfilment.

### 1.2 Intent owner and intent handler:

TMF distinguishes between an intent owner and an intent handler.

Architecture alignment:

- Client / OEX maps to the intent-owner-side actor.
- Intent Enabler maps to the intent-handler-side domain.
- IC MS is the main TMF-facing interface point inside the Intent Enabler.
- The remaining services are internal fulfilment components of the handler domain.

Recommended stakeholder wording:

`Client / OEX -> Intent Enabler`

maps to:

`Intent Owner -> Intent Handler`

### 1.3 IntentReport:

TMF positions intent reports as the return communication from the handler to the owner, reporting achievement and compliance against the intent.

Architecture alignment:

- `IntentReport` is the external reporting projection.
- IA MS produces runtime assurance truth internally.
- IC MS projects that truth externally into `Intent` and `IntentReport`.
- This preserves the TMF control-loop pattern without exposing internal event complexity to external consumers.

### 1.4 IntentSpecification:

TMF describes IntentSpecification as the model for well-formed intent and allowed intent content.

Architecture alignment:

- ID MS owns IntentSpecification as a design-time contract.
- IntentSpecification lifecycle is separate from runtime Intent lifecycle.
- IntentSpecification versions use `DRAFT`, `ACTIVE`, and `RETIRED`.
- New active versions are created as new draft resources and promoted through governance.

### 1.5 Intent ontology and model federation:

TIO supports a modular ontology approach where common and extension models combine vocabulary and semantics.

Architecture alignment:

- II MS uses internal knowledge to interpret external intent content.
- The KP / knowledge plane supports fulfilment and resolution, but is not exposed as the external Intent.
- Domain-specific surgical-slice knowledge can be represented internally while keeping external contracts TMF-aligned.
- Intent-side concepts should be considered together with report-side concepts.

## 2. Architecture-to-TMF mapping:

| Architecture element | TMF alignment | Design interpretation |
|---|---|---|
| Client / OEX | Intent owner side | Expresses requirements to the Intent Enabler |
| Intent Enabler | Intent handler side | Receives and fulfils intent for the target autonomous domain |
| IC MS | TMF-facing Intent and IntentReport projection | Owns external Intent lifecycle, external reporting projection, and TMF-style events |
| ID MS | IntentSpecification owner | Owns allowed intent content, versioning, lifecycle, and governance of specifications |
| II MS | Intent interpretation and semantic handling | Resolves meaning, policy, candidates, and optimisation need using knowledge |
| IA MS | Runtime assurance truth source | Applies assurance monitoring and emits internal runtime truth |
| ICB MS | Intent callback support service | Mediates incoming network/orchestrator callbacks into the internal event path |
| t7.optimiser | Optimisation capability | Selects resources/paths when optimisation is required |
| t7.orchestrator | Network apply capability | Applies configuration and returns network state |
| t7.telemetry | Runtime observation source | Streams telemetry used by IA MS for assurance decisions |
| IntentReport | TMF reporting feedback | External projection of assurance/status back to owner-side consumers |

## 3. Verification points:

### 3.1 External intent contract is preserved:

The design preserves a TMF-facing external Intent resource. Internal events such as `IntentValidatedEvent`, `IntentResolvedEvent`, `IntentOptimisedEvent`, `IntentNetworkReadyEvent`, and `IntentAssuranceEvent` are implementation events, not replacements for the TMF-facing Intent resource.

Verification result:

**Aligned.**

### 3.2 IntentSpecification remains design-time:

IntentSpecification is treated as a governed design-time contract, with the active specification used to validate incoming Intent creation.

Verification result:

**Aligned.**

### 3.3 IntentReport closes the loop:

Runtime assurance is internally produced by IA MS, but the external reporting view is owned by IC MS through `IntentReport`.

Verification result:

**Aligned.**

### 3.4 Ontology and knowledge are used for interpretation:

II MS uses knowledge to interpret intent meaning, apply policy, discover candidates, and prepare optimisation decisions. This is consistent with the TIO model-federation direction, where vocabulary and semantics may be modular.

Verification result:

**Aligned, with one important boundary: KP remains internal fulfilment knowledge, not the external Intent model itself.**

### 3.5 Runtime telemetry supports assurance:

IA MS subscribes to `t7.telemetry` before applying configuration and uses real-time telemetry during runtime assurance. This supports the closed-loop assurance behaviour expected of an autonomous intent-handling domain.

Verification result:

**Aligned.**

### 3.6 Owner/handler separation is clear:

The architecture keeps the client/OEX actor outside the Intent Enabler and positions the Intent Enabler as the handler-side domain.

Verification result:

**Aligned.**

## 4. Design boundaries to preserve:

### 4.1 Do not expose internal fulfilment events as the external TMF contract:

Internal events are useful for service decoupling and observability, but external consumers should continue to see the TMF-facing Intent and IntentReport resources/events.

### 4.2 Keep KP internal:

The KP / knowledge plane is part of II MS fulfilment capability. It should not be treated as the external Intent or IntentSpecification payload.

### 4.3 Keep Intent and IntentReport vocabulary coordinated:

When new intent-side concepts are introduced, such as latency, reliability, priority, service class, surgical capability, or location, the corresponding report-side projection should be considered.

### 4.4 Keep lifecycle status as the external projection:

Use `lifecycleStatus`, `statusReason`, and `statusChangeDate` externally. Treat runtime state, network state, and assurance state as internal conditions that are projected externally as status.

### 4.5 Keep ICB MS incoming-only:

ICB MS is an incoming callback mediation service. It does not expose events to clients and does not act as an outbound event gateway.

## 5. Recommended stakeholder position:

The current Intent Enabler design is TMF-aligned because it preserves the external intent-owner / intent-handler interaction, keeps IntentSpecification as the governed design-time contract, uses Intent and IntentReport as the external control-loop interface, and confines implementation-specific processing to internal services, events, telemetry, optimisation, and knowledge-plane logic.

The design should therefore be positioned as:

- TMF-facing at the external contract boundary
- event-driven internally for fulfilment and assurance
- knowledge-driven internally for semantic resolution and policy/candidate selection
- telemetry-driven for runtime assurance
- externally projected through Intent lifecycle and IntentReport

## 6. Open follow-up items:

The following items remain pending for detailed design and do not block the TMF alignment baseline:

1. Finalise caching and circuit-breaker strategies for each MS.
2. Finalise EDA patterns for each MS.
3. Finalise deployment strategies for each MS.
4. Finalise Kubernetes cluster strategy.
5. Finalise SaaS / PaaS software choices for MS use.

## 7. Conclusion:

The architecture is aligned with TMF TIO principles when viewed as an intent-handler-side implementation of an intent-enabled domain.

The key governance rule is to keep the TMF-facing contract clean and stable while allowing the internal platform to use event-driven processing, knowledge-driven interpretation, optimisation, orchestration, callback mediation, and telemetry-driven assurance to fulfil the intent.
