# OSB MS / Optimisation Screen Builder MS Design:

## Service purpose:

OSB MS means Optimisation Screen Builder MS.

OSB MS is the context-aware OEX facade / backend-for-frontend service for optimisation experiences.

OSB MS sits behind OGW and receives user context from the User Context JWT passed by OGW. It shapes the OEX optimisation experience and calls backend optimisation domain APIs through NGW.

OSB MS initially supports runtime optimisation journeys through OC MS. It later supports catalogue/specification journeys through OD MS.

## Access path:

The agreed access path is:

```text
User
-> OEX UI
-> OGW
-> OSB MS
-> NGW
-> OC MS
-> OD MS
```

Meaning:

```text
User:
  Uses OEX UI.

OEX UI -> OGW:
  OEX UI reaches the optimisation experience through OGW.

OGW -> OSB MS:
  OGW invokes OSB MS using mTLS and User Context JWT.

OSB MS -> NGW:
  OSB MS calls NGW using mTLS and OAuth2 system-to-system.

NGW -> OC MS / OD MS:
  NGW exposes the backend TMF-compliant optimisation APIs.
```

## Ownership boundary:

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
OD MS:
  owns OptimisationSpecification definitions.

OC MS:
  owns runtime Optimisation resources.

OSB MS:
  owns OEX experience/context-aware facade behaviour.
```

## API compliance:

OSB APIs are private/OEX experience APIs and do not need to be TMF-compliant.

NGW-exposed backend OD MS and OC MS APIs remain TMF-compliant.

OSB MS must not expose backend OD/OC resource contracts directly unless the UI journey explicitly needs that shape.

## Recommended namespace:

```http
/optimisationExperience/v1
```

Avoid using backend resource namespaces directly from OSB:

```http
/optimisation
/optimisationSpecification
```

Those belong to OC MS and OD MS behind NGW.

## Phase one endpoint set:

```http
GET  /optimisationExperience/v1/home
GET  /optimisationExperience/v1/capabilities
GET  /optimisationExperience/v1/capabilities/{capabilityId}/request-form

POST /optimisationExperience/v1/optimisations
GET  /optimisationExperience/v1/optimisations
GET  /optimisationExperience/v1/optimisations/{id}

POST /optimisationExperience/v1/optimisations/{id}/cancellation
POST /optimisationExperience/v1/optimisations/{id}/retrial
```

## Endpoint purpose:

| Endpoint | Purpose |
|---|---|
| `GET /optimisationExperience/v1/home` | Returns OEX optimisation landing-page model. |
| `GET /optimisationExperience/v1/capabilities` | Returns context-filtered optimisation capabilities visible to the user. |
| `GET /optimisationExperience/v1/capabilities/{capabilityId}/request-form` | Returns UI form model generated from the ACTIVE OptimisationSpecification. |
| `POST /optimisationExperience/v1/optimisations` | Creates runtime optimisation by calling NGW -> OC MS. |
| `GET /optimisationExperience/v1/optimisations` | Lists runtime optimisations visible to the user/context. |
| `GET /optimisationExperience/v1/optimisations/{id}` | Returns UI-friendly runtime optimisation detail. |
| `POST /optimisationExperience/v1/optimisations/{id}/cancellation` | Context-aware cancellation action mapped to OC MS cancellation. |
| `POST /optimisationExperience/v1/optimisations/{id}/retrial` | Context-aware retrial action mapped to OC MS retrial. |

## Phase two catalogue endpoint set:

Catalogue management is internal and governed.

```http
GET  /optimisationExperience/v1/catalogue
GET  /optimisationExperience/v1/catalogue/{specificationId}
GET  /optimisationExperience/v1/catalogue/{specificationId}/editor-form

POST /optimisationExperience/v1/catalogue
PUT  /optimisationExperience/v1/catalogue/{specificationId}

POST /optimisationExperience/v1/catalogue/{specificationId}/activation
POST /optimisationExperience/v1/catalogue/{specificationId}/retirement
```

## Catalogue security rule:

Only approved optimisation domain engineers can access catalogue write, activation, and retirement journeys.

OSB MS checks user context and role claims from the User Context JWT.

OD MS remains the source of truth and must enforce backend authorisation as well.

Catalogue changes are made only after agreement with the broader E2E teams that own, consume, or are impacted by the optimisation capability.

General users and runtime consumers cannot self-author new OptimisationSpecification records through OSB MS.

## Context awareness:

OSB MS uses the User Context JWT passed by OGW to shape the experience.

Examples:

```text
filter visible optimisation capabilities
filter visible runtime optimisation records
determine whether cancellation action is shown
determine whether retrial action is shown
hide catalogue-management journeys unless the user has approved optimisation domain engineer access
carry source/user context to backend calls where approved
shape UI labels, warnings, allowed actions, and screen sections
```

OSB MS must not trust UI-supplied role decisions. It must use trusted claims from the User Context JWT and backend authorisation decisions from OD MS / OC MS.

## Runtime optimisation flow:

```text
User
-> OEX UI
-> OGW
-> OSB MS
-> NGW
-> OC MS
```

Detailed flow:

```text
1. User opens the OEX optimisation experience.
2. OEX UI calls OGW.
3. OGW invokes OSB MS using mTLS and User Context JWT.
4. OSB MS reads authorised user/context claims.
5. OSB MS shapes the runtime request/view/action model.
6. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
7. NGW calls OC MS.
8. OC MS validates and manages runtime Optimisation as source of truth.
9. OSB MS returns a UI-friendly response to OEX UI through OGW.
```

## Catalogue/specification flow:

```text
User
-> OEX UI
-> OGW
-> OSB MS
-> NGW
-> OD MS
```

Detailed flow:

```text
1. User opens catalogue/specification journey in OEX UI.
2. OGW invokes OSB MS using mTLS and User Context JWT.
3. OSB MS checks whether the user has approved optimisation domain engineer access.
4. OSB MS calls NGW using mTLS and OAuth2 system-to-system.
5. NGW calls OD MS.
6. OD MS enforces OptimisationSpecification source-of-truth validation and authorisation.
7. OSB MS returns a UI-friendly catalogue or editor response.
```

## Security baseline:

### OGW -> OSB MS:

```text
mTLS
User Context JWT
```

Controls:

```text
OGW authenticates to OSB MS.
OSB MS validates User Context JWT signature, issuer, audience, expiry, and required claims.
OSB MS rejects missing, expired, malformed, or unauthorised context tokens.
OSB MS uses the User Context JWT only for authorised context-aware experience decisions.
```

### OSB MS -> NGW:

```text
mTLS
OAuth2 system-to-system
```

Controls:

```text
OSB MS authenticates to NGW as an approved service identity.
NGW authorises OSB MS to call only required backend optimisation APIs.
OSB MS does not bypass NGW to call OD MS or OC MS directly unless explicitly approved by architecture/security governance.
```

### Infrastructure access:

OSB MS should not require a database, cache, or Kafka integration in the initial baseline.

If OSB MS later integrates with any database, cache, Kafka topic, object storage, queue, search index, or other platform infrastructure, the OSB MS design brief must explicitly capture:

```text
authenticated service identity
least-privilege authorisation
encrypted connectivity, including mTLS where supported and appropriate
resource-level access scoping
no broad wildcard/admin/root access by default
approved secret/certificate management and rotation
environment-scoped principals/roles
audit and monitoring of access failures and privileged operations
clear ownership of producer/consumer/read/write permissions where relevant
```

## Backend mapping:

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

## Concurrency handling:

OSB MS must preserve backend ETag semantics for unsafe runtime operations.

```text
OSB MS receives or stores the current ETag from OC MS response.
For cancellation and retrial, OSB MS forwards If-Match to OC MS through NGW.
OC MS remains the concurrency source of truth.
```

Failure mapping:

```text
Missing If-Match from backend requirement -> surface as precondition-required UI/action error.
Stale ETag -> surface as stale-resource UI/action error.
Backend 412/428 must not be hidden as generic failure.
```

## Error handling:

OSB MS should convert backend errors into UI-friendly error models while preserving useful error code, reason, correlation id, and status.

OSB MS must not hide backend distinction between:

```text
400 malformed request
401 unauthenticated
403 unauthorised
404 not found
412 precondition failed
422 optimisation contract violation
500/502/503/504 platform failure
```

For runtime optimisation:

```text
422 OPTIMISATION_CONTRACT_VIOLATION is a request-contract validation failure from OC MS.
INFEASIBLE is an optimisation outcome from the worker/model projected by OC MS.
```


## Phase baseline:

Phase one:

```text
home
capability discovery
request-form generation
runtime optimisation create/list/detail
cancellation
retrial
```

Phase two:

```text
catalogue list/detail/editor-form
catalogue create/update
catalogue activation
catalogue retirement
approved optimisation domain engineer journeys
```

## Baseline timestamp:

```text
2026-05-03T23:43:48
```

---

## Observability and monitoring telemetry baseline:

Each service design brief and the E2E solution brief must capture observability as more than application logging.

Observability includes:

```text
application logs
metrics
distributed traces
audit/security events
dependency telemetry
alertable operational signals
```

Correlation and trace propagation:

```text
accept correlation id / request id from the upstream caller where provided
generate a correlation id when missing
propagate correlation id to downstream service, database, cache, Kafka, and platform calls where applicable
propagate trace context where platform standards support it
preserve useful downstream correlation identifiers in logs/telemetry where approved
```

Application log baseline:

```text
request id / correlation id
service name
operation or endpoint
safe subject/user/service reference where applicable
resource id where applicable
dependency called
dependency status code or outcome
latency
authorisation decision result where applicable
error code/reason
```

Monitoring telemetry baseline:

```text
request count by endpoint/operation and status
latency by endpoint/operation and dependency
error rate by endpoint/operation and dependency
dependency failure counts
timeout and retry counts where applicable
authorisation allow/deny counts where applicable
token or credential validation failure counts where applicable
database connection and query failure counts where applicable
Kafka produce/consume failure counts where applicable
Kafka lag and DLQ growth where applicable
outbox/inbox backlog where applicable
cache hit/miss/error counts where applicable
```

Distributed tracing baseline:

```text
trace inbound service requests
trace outbound dependency calls
include correlation id and safe business/resource identifiers as trace attributes where approved
do not include sensitive token claims, secrets, credentials, or full private payloads in traces
```

Security/audit baseline:

```text
authentication failures
authorisation failures
privileged operation attempts
catalogue write/activation/retirement attempts where applicable
unsafe runtime action attempts such as cancellation and retrial where applicable
Kafka replay/DLQ actions where applicable
database privileged access or schema-change actions where applicable
```

Sensitive claims, full tokens, secrets, credentials, private payload data, and personal data beyond approved identifiers must not be logged or emitted as telemetry attributes.

---

## OSB MS observability focus:

OSB MS observability must include OEX experience, context-awareness, and downstream dependency monitoring.

Additional OSB MS signals:

```text
home/capability/request-form/render endpoint counts
runtime action counts for create/cancellation/retrial
User Context JWT validation failures
context-based filtering decisions
catalogue-management access attempts
NGW dependency latency and failures
OC MS / OD MS backend error surfacing counts
```

---

## Logical view baseline:

The logical integration model is:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS / OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Definition-management logical path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OD MS
```

Runtime-optimisation logical path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OGW
-> OSB MS(OEX API)
-> NGW
-> OC MS
-> Kafka
-> Python/Gurobi Worker
-> Gurobi Optimizer
```

Logical responsibility split:

```text
OSB MS(OEX API):
  Provides the optimisation-specific OEX API/facade behind OGW.
  Uses User Context JWT to shape the OEX optimisation experience.
  Calls backend optimisation APIs through NGW.

OD MS:
  Owns OptimisationSpecification definitions using constraintSpecifications[], targetSpecifications[], and contextSpecifications[].

OC MS:
  Owns runtime Optimisation resources using constraints[], targets[], and context[].

Kafka / Python/Gurobi Worker / Gurobi Optimizer:
  Participate only in runtime execution flows after OC MS accepts the request.
```

API compliance rule:

```text
NGW-exposed OD MS and OC MS APIs are TMF-compliant.

OSB MS(OEX API) APIs exposed behind OGW are private/OEX experience APIs and do not need to be TMF-compliant.

Private MS-to-MS APIs and Kafka events are internal contracts unless separately exposed.
```
