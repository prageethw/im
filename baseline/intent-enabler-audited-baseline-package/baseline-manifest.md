# Intent Enabler Audited Baseline Manifest:

## Purpose:

This manifest identifies the current source-of-truth baseline files for the Intent Enabler architecture.

The rolling baseline dump is only a convenience file. The baseline source of truth is the set of files listed in this manifest together with the audit checklist.

## Trust rule:

If a topic is listed in this manifest and passes the audit checklist, treat it as baseline.

If a topic appears only in an old rolling dump and is not listed here, treat it as supporting notes only.

## Current source-of-truth files:

- `intent-enabler-closed-loop-activity-condensed-lifecycle-v3.puml` — Condensed closed-loop activity chart with lifecycle progression and explicit Rejected lifecycle path.
- `tmf-alignment-design-verification-paper.md` — Long-form TMF alignment design verification paper in Markdown.
- `tmf-alignment-design-verification-paper-v2.pdf` — Stakeholder-ready PDF version of the TMF alignment paper.
- `human-expression-mapping-baseline-addendum.md` — Explicit humanExpressionMapping baseline addendum.
- `resource-roles-field-baseline.md` — Resource roles optional-field rule and controlled vocabulary baseline.
- `id-ms-baseline-specification-complete-samples-v2.md` — ID MS baseline pack for IntentSpecification operations and samples.
- `ic-ms-baseline-specification-complete-samples-v4.md` — IC MS baseline pack for Intent, IntentReport, hub and external event behavior.
- `internal-events-baseline-pack-complete-v3.md` — Internal event baselines including IntentAssuranceEvent model.
- `ontology-dictionary-baseline-v5.md` — Ontology dictionary / terminology baseline.
- `kp-baseline-pack.md` — KP / Master Knowledge Config baseline pack.
- `ii-ms-baseline-pack.md` — II MS baseline pack.
- `ia-ms-baseline-pack-v2.md` — IA MS baseline pack.
- `end-to-end-platform-flow-pack.md` — End-to-end platform flow baseline pack.
- `intent-enabler-baseline-dump-with-human-expression.md` — Convenience rolling dump with explicit human expression addendum.

## Missing from workspace but expected from previous work:

- `intent-enabler-sequence-part1-baselined-v3-knowledge-plane.puml`
- `intent-enabler-sequence-part2-baselined-v3-knowledge-plane.puml`
- `tmf-alignment-design-verification-summary-baseline-v2.md`
- `tmf-alignment-confluence-page-v2.md`
- `icb-ms-baseline-pack-v2.md`
- `pending-architecture-closure-items.md`

## Current pending detailed-design items:

1. Finalise caching and circuit-breaker strategies for each MS.
2. Finalise EDA patterns for each MS.
3. Finalise deployment strategies for each MS.
4. Finalise Kubernetes cluster strategy.
5. Finalise SaaS / PaaS software choices for MS use.
