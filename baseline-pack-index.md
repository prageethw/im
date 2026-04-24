# Baseline Pack Index

This index links the current baseline packs generated in Markdown.

## Packs

- `id-ms-baseline-specification-complete-samples-v2.md`
  - ID MS interfaces, hub operations, external events, and complete JSON samples

- `ic-ms-baseline-specification-complete-samples-v2.md`
  - IC MS interfaces, `/intent/hub`, `IntentReport`, external event families, and complete JSON samples

- `internal-events-baseline-pack-complete-v2.md`
  - Internal event baselines including full JSON payloads for:
    - `IntentValidatedEvent`
    - `IntentRejectedEvent`
    - `IntentResolvedEvent`
    - `IntentOptimisedEvent`
    - `IntentNetworkReadyEvent`
    - `IntentAssuranceEvent`

- `ontology-dictionary-baseline-v2.md`
  - Canonical terminology, meanings, usage guidance, and legacy/replaced terms

## Suggested reading order

1. Ontology dictionary
2. ID MS baseline pack
3. IC MS baseline pack
4. Internal events baseline pack

## Notes

- Markdown is the canonical working/export format going forward.
- External-contract exceptions such as `geo_location` remain allowed where required by the external contract.
- Historical/replaced terms are documented in the ontology dictionary and should not be used as active attribute names.
- Reference running dump: `new-context-working-v24.md`
