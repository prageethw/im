Optimisation Screen Builder MS Specification

## Service purpose

OSB MS means Optimisation Screen Builder MS. OSB MS is the context-aware OEX facade / backend-for-frontend service for optimisation experiences. OSB MS sits behind OGW and receives user context from the User Context JWT passed by OGW. It shapes the OEX optimisation experience and calls backend optimisation domain APIs through NGW. OSB MS initially supports runtime optimisation journeys through OC MS.

It later supports catalogue/specification journeys through OD MS.

## Ownership boundary

OSB MS owns:

```text
OEX-friendly optimisation experience APIs
context-aware view shaping
capability cards and landing-page models
request-form models derived from OD MS specifications
runtime optimisation list/detail view models
context-aware action exposure such as cancellation and retrial
user-context based filtering of visible capabilities and records
catalogue-management screen support for approved optimisation domain engineers when enabled
```

OSB MS does not own:

```text
OptimisationSpecification source of truth
runtime Optimisation lifecycle source of truth
Kafka outbox/inbox processing
solver execution
Gurobi model binding
optimisation result projection
OD MS catalogue governance
OC MS runtime lifecycle governance
```

Source-of-truth ownership:

```text
OD MS: owns OptimisationSpecification definitions.
OC MS: owns runtime Optimisation resources.
OSB MS: owns OEX experience/context-aware facade behaviour.
```

## API compliance

OSB APIs are private/OEX experience APIs and do not need to be TMF-compliant. NGW-exposed backend OD MS and OC MS APIs remain TMF/TIO-aligned while using Optimisation as the domain concept. OSB MS must not expose backend OD/OC resource contracts directly unless the UI journey explicitly needs that shape.

## Recommended namespace

```http
/optimisationExperience/v1
```

Avoid using backend resource namespaces directly from OSB:

```http
/optimisation
/optimisationSpecification
```

Those belong to OC MS and OD MS behind NGW.

## Phase one endpoint set

```http
GET /optimisationExperience/v1/home
GET /optimisationExperience/v1/capabilities
GET /optimisationExperience/v1/capabilities/{capabilityId}/request-form
POST /optimisationExperience/v1/optimisations
GET /optimisationExperience/v1/optimisations
GET /optimisationExperience/v1/optimisations/{id}
POST /optimisationExperience/v1/optimisations/{id}/cancellation
POST /optimisationExperience/v1/optimisations/{id}/retrial
```

## Runtime optimisation flow

```text
User -> OEX UI -> OGW -> OSB MS -> NGW -> OC MS
```

OSB MS must preserve the runtime expression shape expected by OC MS:

```text
expression.expressionValue.context.targets[]
expression.expressionValue.context.constraints[]
expression.expressionValue.context.preferences[]
```

## Catalogue/specification flow

```text
User -> OEX UI -> OGW -> OSB MS -> NGW -> OD MS
```

Only approved optimisation domain engineers can access catalogue write, activation, and retirement journeys.

## Security baseline

### OGW -> OSB MS

```text
mTLS
User Context JWT
```

### OSB MS -> NGW

```text
mTLS
OAuth2 system-to-system
```

OSB MS does not bypass NGW to call OD MS or OC MS directly unless explicitly approved by architecture/security governance.

## Backend mapping

| OSB endpoint | Backend mapping |
|---|---|
| `GET /optimisationExperience/v1/home` | OSB aggregates/context-shapes from NGW -> OD MS and NGW -> OC MS as required. |
| `GET /optimisationExperience/v1/capabilities` | NGW -> OD MS `GET /optimisationSpecification`. |
| `GET /optimisationExperience/v1/capabilities/{capabilityId}/request-form` | NGW -> OD MS `GET /optimisationSpecification/{id}`, transformed into UI form model. |
| `POST /optimisationExperience/v1/optimisations` | NGW -> OC MS `POST /optimisation`. |
| `GET /optimisationExperience/v1/optimisations` | NGW -> OC MS `GET /optimisation`, context-filtered. |
| `GET /optimisationExperience/v1/optimisations/{id}` | NGW -> OC MS `GET /optimisation/{id}`, transformed into UI-friendly detail. |
| `POST /optimisationExperience/v1/optimisations/{id}/cancellation` | NGW -> OC MS `POST /optimisation/{id}/cancellation`. |
| `POST /optimisationExperience/v1/optimisations/{id}/retrial` | NGW -> OC MS `POST /optimisation/{id}/retrial`. |

## Concurrency handling

OSB MS must preserve backend ETag semantics for unsafe runtime operations.

```text
OSB MS receives or stores the current ETag from OC MS response.
For cancellation and retrial, OSB MS forwards If-Match to OC MS through NGW.
OC MS remains the concurrency source of truth.
```

Backend `412` and `428` must not be hidden as generic failures.
