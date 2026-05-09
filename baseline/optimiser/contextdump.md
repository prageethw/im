
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
