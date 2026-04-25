# Baseline Release Summary

## Purpose

This release summary ties together the current baseline pack set and the latest major architecture decisions.

## Current baseline pack set

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

- `end-to-end-platform-flow-pack.md`
  - Happy path, rejection path, degraded/re-decision path, and ownership summary

- `baseline-pack-index-v6.md`
  - Current pack index for the baseline set

- `cross-pack-sweep-vnext.md`
  - Latest cross-pack terminology sweep

## Most recent running dump

- `new-context-working-v34.md`

## Major locked architecture points

### Intent versioning
- Once an Intent version becomes `Active`, it becomes the `effectiveVersion`.
- It remains the `effectiveVersion` even if its lifecycle later becomes `Degraded`, `Paused`, or `Failed`.
- `effectiveVersion` changes only when another version is confirmed `Active` in the network/service.

### IntentSpecification versioning
- Lifecycle states: `DRAFT`, `ACTIVE`, `RETIRED`
- Only `DRAFT` is editable
- New active versions must start as new `DRAFT` resources
- When a new version becomes `ACTIVE`, the previous `ACTIVE` version becomes `RETIRED`
- `RETIRED` specifications are not for new intent creation

### Internal event model
- `IntentAssuranceEvent` is the shared runtime truth event
- Same event name, with non-degraded and degraded forms
- `candidates` is conditional
- When present, `candidates` must include current active resources too
- IA MS emits `IntentAssuranceEvent` only on status/lifecycle change

### IC MS projection rule
- IC MS derives external lifecycle/reporting updates from `IntentAssuranceEvent`
- A status/lifecycle change updates both:
  - external `Intent`
  - external `IntentReport`
- Metric-only or candidate-only changes without status change do not create a separate external update path

### KP / Master Knowledge Config
- KP is internal II MS knowledge, not an external intent resource
- Global `resources` map
- `locations.applicableResourceIds` is the location-to-resource scoping link
- `resourceAttributes.surgicalCapable` is treated as a resource capability
- `orchestrator` remains resource-scoped

## Recommended reading order

1. `ontology-dictionary-baseline-v5.md`
2. `id-ms-baseline-specification-complete-samples-v2.md`
3. `ic-ms-baseline-specification-complete-samples-v4.md`
4. `internal-events-baseline-pack-complete-v3.md`
5. `kp-baseline-pack.md`
6. `ii-ms-baseline-pack.md`
7. `ia-ms-baseline-pack-v2.md`
8. `end-to-end-platform-flow-pack.md`

## Notes

- Markdown is the canonical working/export format.
- The running dump remains the most complete recovery source.
- Pack versions are milestone snapshots and may be refreshed again later.
