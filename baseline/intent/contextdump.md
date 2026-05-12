# Context dump update — IA MS alignment patch

Baselined on 2026-05-12.

IA MS alignment changes:
- `IntentOptimisedEvent` consumed by IA uses `body.context.targets`, `body.context.constraints`, and `body.context.preferences`.
- `IntentNetworkReadyEvent` is consumed by IA and must not show `ce-source: intent-assurance-ms`; active baseline uses `ce-source: intent-intelligence-ms`.
- `IntentCallbackEvent` consumed by IA uses ICB canonical fields: `orchestratorState`, `orchestratorSource`, and `orchestratorTimestamp`.
- IA maps raw `orchestratorState`, not older `sourceState.state`.
- Replaced vague KP-derived expectation wording with resolved runtime targets and IA stored applied assurance baseline.
- KP/rules may support mapping/evaluation policy, but IA does not query KP as source of truth for every assurance decision by default.
- `IntentAssuranceEvent` is still the single IA-owned runtime assurance output event; `IntentDriftOccurredEvent` remains retired.

# Context dump update — IA MS removes IntentResolvedEvent

Baselined on 2026-05-12.

`IntentResolvedEvent` is removed from IA MS entirely. IA MS does not list it as primary, optional, contextual, or supporting input. IA MS inputs remain focused on `IntentOptimisedEvent`, `IntentNetworkReadyEvent`, canonical `IntentCallbackEvent`, and observation/telemetry facts. `IntentResolvedEvent` remains part of the interpretation/resolution workflow, not IA assurance.
