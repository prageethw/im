---

## E2E solution brief restoration baseline — 2026-05-09:

The `optimisation-e2e-solution-brief.md` file has been restored against the fuller GitHub baseline from commit `49251df312adff0fefb26bc12bd71e0ca09fd82d`, preserving the earlier detailed section order and content breadth rather than the shortened compressed version.

Restored / preserved major sections include:

- Business context
- Solution summary
- Solution elaboration
- Use case view
- Logical view
- Detailed process view
- Capability matrix
- Solution security
- Infrastructure security controls
- Quality attributes
- Risks
- Assumptions
- Constraints
- Appendix
- TMF ontology alignment note
- Optimisation validation and outcome clarification
- Contract definition versus runtime values
- Canonical runtime expression shape
- Runtime Optimisation lifecycle baseline

Merged updates applied during restoration:

- General wording uses `TMF ontology-aligned` rather than `TMF921/TIO-aligned`, except where specific standards validation is intended.
- `OWG` wording has been removed/replaced with `OGW` and direct `OGW -> OSB MS` wording.
- OD MS remains synchronous REST only for the initial baseline; no `/hub` or outbound `OptimisationSpecification` events.
- OD MS `OptimisationSpecification` uses `specCharacteristic[]`, `expressionSpecification`, and `targetEntitySchema`; old `constraintSpecifications[]`, `targetSpecifications[]`, `preferenceSpecifications[]`, and `contextSpecifications[]` wording is not used as the external OD resource shape.
- Runtime optimisation expression uses `expression.expressionValue.context.targets[]`, `context.constraints[]`, and `context.preferences[]`.
- OD MS lifecycle remains `DRAFT`, `ACTIVE`, `RETIRED`; no `DEPRECATED`.
- Activation of a new specification version retires the previous active version in the same specification family.
- OD HATEOAS `_links`, ETag/If-Match, simple GET cache policy, and approved platform extension wording are preserved at E2E level.


## Baseline update — E2E solution brief 1–10 structure cleanup

- Active E2E source is GitHub main `baseline/optimiser/optimisation-e2e-solution-brief.md`.
- Preserve the existing detailed E2E content and 1–10 design structure.
- Move important trailing unnumbered sections into the numbered structure:
  - `TMF ontology alignment note` -> `3.4 Design rules and TMF ontology alignment`.
  - `Optimisation validation and outcome clarification` -> `3.5 Validation and outcome responsibility`.
  - `Contract definition versus runtime values` -> `3.6 Specification contract versus runtime values`.
  - `Canonical runtime expression shape` -> `10.10 Canonical runtime expression shape`.
  - `Runtime Optimisation lifecycle baseline` -> `10.11 Runtime Optimisation lifecycle baseline`.
- Keep all current detailed process flows and capability/security/quality/risk/assumption/constraint content.
- Apply wording cleanup only where it does not change meaning, such as `Cancel optimisation`, `Retry failed optimisation`, and `not limited to the intent-management domain`.

## Baseline update — E2E use case numbering

The `optimisation-e2e-solution-brief.md` use case view now includes a `No.` column with sequential numbers 1–9 for the E2E use cases. The use case names, actors, summaries, and outcomes were preserved; only numbering was added for easier cross-reference to process-view sections.


## Baseline update — E2E flow numbering

- Updated `optimisation-e2e-solution-brief.md` so logical flow and process-flow arrow summaries are numbered.
- The logical integration model now lists each hop as a numbered step.
- Key logical relationships are numbered 1 to 10.
- Process-view summary flows now show numbered hops before the existing detailed numbered flows.
- No service responsibility or API semantics were changed by this update.


## E2E solution brief summary cleanup — 2026-05-09

Removed low-level OD MS field-responsibility details from the Solution summary of `optimisation-e2e-solution-brief.md`. Detailed OD MS contract responsibilities remain in the elaboration/appendix sections and OD MS specification.

## E2E baseline update — embed validation/contract sections in capability matrix

- Current GitHub-main E2E baseline remains the source of truth for the E2E solution brief.
- Standalone sections `3.5 Validation and outcome responsibility` and `3.6 Specification contract versus runtime values` are removed from the E2E brief.
- Their content is embedded into section `4. Capability matrix` because validation responsibility, outcome ownership, and contract-vs-runtime-value separation are component responsibilities.
- OD MS row now states that OD defines what is allowed using `specCharacteristic[]`, `expressionSpecification`, and `targetEntitySchema`, but does not carry runtime values or decide solver outcomes.
- OC MS row now states that OC carries accepted runtime `expression.expressionValue.context.targets[]`, `constraints[]`, and `preferences[]`, validates against the active OD `targetEntitySchema`, and uses `422 OPTIMISATION_CONTRACT_VIOLATION` for contract/cardinality failures.
- Python/Gurobi Worker row now states that the worker/model determines `SUCCESS`, `INFEASIBLE`, or `FAILURE`.
- OC MS Inbox Consumer row now states the outcome mapping: `SUCCESS -> COMPLETED`, `INFEASIBLE -> INFEASIBLE`, and `FAILURE -> FAILED`.
