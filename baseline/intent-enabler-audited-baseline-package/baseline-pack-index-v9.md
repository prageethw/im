# Baseline Pack Index

This index links the current baseline packs generated in Markdown.

## Current packs:

- `id-ms-baseline-specification-complete-samples-v2.md`
  - ID MS interfaces, hub operations, external events, and complete JSON samples

- `ic-ms-baseline-specification-complete-samples-v4.md`
  - IC MS interfaces, `/intent/hub`, `IntentReport`, external event families, complete JSON samples, and IC projection rule from `IntentAssuranceEvent`

- `internal-events-baseline-pack-complete-v3.md`
  - Internal event baselines including full JSON payloads and the latest `IntentAssuranceEvent` refinements

- `ontology-dictionary-baseline-v5.md`
  - Canonical terminology, meanings, usage guidance, legacy/replaced terms, and newer KP/flow terminology additions

- `kp-baseline-pack.md`
  - Master Knowledge Config / KP purpose, top-level structure, policy/resource/location model, and full hospital-slice KP example

- `ii-ms-baseline-pack.md`
  - II MS role, decision stages, stage-to-event mapping, decision matrix, and re-optimisation trigger rules

- `ia-ms-baseline-pack-v2.md`
  - IA MS role, apply/assurance flow, decision matrix, and IC projection interaction rule

- `icb-ms-baseline-pack-v2.md`
  - ICB MS incoming-only REST wrapper / callback access mediation role, interface boundary, and concrete API contract

- `end-to-end-platform-flow-pack.md`
  - Happy path, rejection path, degraded/re-decision path, and ownership summary

## Suggested reading order:

1. Ontology dictionary
2. ID MS baseline pack
3. IC MS baseline pack
4. Internal events baseline pack
5. KP baseline pack
6. II MS baseline pack
7. IA MS baseline pack
8. ICB MS baseline pack
9. End-to-end platform flow pack

## Notes:

- Markdown is the canonical working/export format going forward.
- External-contract exceptions such as `geo_location` remain allowed where required by the external contract.
- Historical/replaced terms are documented in the ontology dictionary and should not be used as active attribute names.
- Reference running dump: `new-context-working-v36.md`
