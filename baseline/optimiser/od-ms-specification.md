# OD MS / Optimisation-Definition-MS Specification:

## Service purpose:

Optimisation-Definition-MS / OD MS owns the governed catalogue of optimisation capabilities.

OD MS defines what optimisation requests are allowed to look like. It does not execute optimisation, does not hold runtime request values, and does not store actual candidate resources from a request.

OD MS is the definition/specification service. OC MS is the runtime execution/controller service.

## Ownership:

OD MS owns:

```text
OptimisationSpecification resource
Optimisation capability metadata
Request contract definition
Constraint specification definitions
Target specification definitions
Context specification definitions
Candidate resource schema
Candidate resource cardinality rules
Specification lifecycle
Specification versioning
Specification list/retrieve/create/update operations
```

OD MS does not own:

```text
Runtime Optimisation resources
Runtime constraints[] values
Runtime targets[] values
Runtime context[] values
Actual candidate resource instances
Candidate-resource selection
Solver feasibility evaluation
Gurobi model execution
Runtime optimisation outcome
```

## Definition versus runtime model:

OD MS uses specification/definition sections:

```text
constraintSpecifications[]:
  Defines allowed hard-constraint fields.
  Does not contain caller-supplied runtime values.

targetSpecifications[]:
  Defines allowed optimisation goals and default/allowed priority ordering.
  Does not contain runtime optimisation results.

contextSpecifications[]:
  Defines required context objects and their schemas.
  Defines candidate resource shape, cardinality, resourceAttributes, and metrics.
  Does not contain actual runtime candidate IDs.
```

OC MS uses runtime instance sections:

```text
constraints[]:
  Actual caller-supplied constraint values.

targets[]:
  Actual caller-supplied or defaulted target goals/priorities.

context[]:
  Actual caller-supplied context values, including candidateResources when embedded.
```

Validation mapping:

```text
OC MS runtime constraints[] -> OD MS constraintSpecifications[]
OC MS runtime targets[] -> OD MS targetSpecifications[]
OC MS runtime context[] -> OD MS contextSpecifications[]
```

## Endpoint set:

OD MS exposes:

```http
GET    /optimisationSpecification
POST   /optimisationSpecification
GET    /optimisationSpecification/{id}
PUT    /optimisationSpecification/{id}
PATCH  /optimisationSpecification/{id}
DELETE /optimisationSpecification/{id}
```

OD MS does not expose runtime optimisation operations. Runtime operations belong to OC MS.

## OptimisationSpecification resource shape:

Canonical fields:

```text
id
href
name
description
version
lifecycleStatus
creationDate
lastUpdate
validFor
constraintSpecifications[]
targetSpecifications[]
contextSpecifications[]
_links
@type
@baseType
@schemaLocation
```

## Lifecycle model:

```text
DRAFT
ACTIVE
DEPRECATED
RETIRED
```

Rules:

```text
DRAFT:
  Editable.

ACTIVE:
  Can be used by OC MS for runtime Optimisation creation.
  Should be immutable except lifecycle transition metadata.

DEPRECATED:
  Existing runtime use may continue where already accepted.
  New runtime use should be prevented unless explicitly allowed by policy.

RETIRED:
  Not available for new runtime Optimisation creation.
```

## Canonical OptimisationSpecification example:

```json
{
  "id": "os-7f3a9c21",
  "href": "/optimisationSpecification/os-7f3a9c21",
  "name": "Hospital surgical slice path optimisation",
  "description": "Defines the request contract for hospital surgical slice path selection optimisation.",
  "version": "1.0",
  "lifecycleStatus": "ACTIVE",
  "creationDate": "2026-05-02T01:00:00Z",
  "lastUpdate": "2026-05-02T02:00:00Z",
  "validFor": {
    "startDateTime": "2026-05-02T00:00:00Z"
  },
  "constraintSpecifications": [
    {
      "name": "maxLatency",
      "constraintType": "maximum",
      "ontologyPredicate": "icm:atMost",
      "valueType": "number",
      "required": true,
      "unit": "ms",
      "description": "Maximum allowed latency for a candidate resource."
    },
    {
      "name": "minReliability",
      "constraintType": "minimum",
      "ontologyPredicate": "icm:atLeast",
      "valueType": "number",
      "required": true,
      "unit": "percent",
      "description": "Minimum required reliability for a candidate resource."
    }
  ],
  "targetSpecifications": [
    {
      "name": "cost",
      "goal": "minimise",
      "required": true,
      "priority": 1,
      "description": "Primary optimisation target is to minimise cost among valid candidates."
    },
    {
      "name": "latency",
      "goal": "minimise",
      "required": false,
      "priority": 2,
      "description": "Secondary optimisation target is to minimise latency among valid candidates."
    },
    {
      "name": "reliability",
      "goal": "maximise",
      "required": false,
      "priority": 3,
      "description": "Tertiary optimisation target is to maximise reliability among valid candidates."
    }
  ],
  "contextSpecifications": [
    {
      "name": "topologySnapshot",
      "valueType": "object",
      "required": true,
      "description": "Topology snapshot containing or referencing the candidate resource set available for optimisation.",
      "schema": {
        "type": "object",
        "required": [
          "dataset",
          "version",
          "candidateResourceSetId",
          "candidateResources"
        ],
        "properties": {
          "dataset": {
            "type": "string"
          },
          "version": {
            "type": "string"
          },
          "candidateResourceSetId": {
            "type": "string"
          },
          "candidateResources": {
            "type": "array",
            "minItems": 2,
            "description": "Candidate resources available to the optimiser. At least two candidate options are required for resource/path/option-selection optimisation unless the capability is explicitly feasibility-validation-only.",
            "items": {
              "type": "object",
              "required": [
                "resourceId",
                "resourceType",
                "metrics"
              ],
              "properties": {
                "resourceId": {
                  "type": "string"
                },
                "resourceType": {
                  "type": "string"
                },
                "resourceClass": {
                  "type": "string"
                },
                "resourceAttributes": {
                  "type": "object",
                  "description": "Stable descriptive properties of the resource, such as locationId or pathClass."
                },
                "metrics": {
                  "type": "array",
                  "description": "Measured or computed values used for evaluation/optimisation, such as latency, reliability, cost, or utilisation.",
                  "items": {
                    "type": "object",
                    "required": [
                      "name",
                      "value"
                    ],
                    "properties": {
                      "name": {
                        "type": "string"
                      },
                      "value": {},
                      "unit": {
                        "type": "string"
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  ],
  "_links": {
    "self": {
      "href": "/optimisationSpecification/os-7f3a9c21",
      "method": "GET"
    },
    "createOptimisation": {
      "href": "/optimisation",
      "method": "POST"
    }
  },
  "@type": "OptimisationSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "/schema/OptimisationSpecification.schema.json"
}
```

## TMF/TIO alignment:

Upper-bound constraints use platform-readable contract fields with TMF/TIO traceability:

```json
{
  "name": "maxLatency",
  "constraintType": "maximum",
  "ontologyPredicate": "icm:atMost",
  "valueType": "number",
  "required": true,
  "unit": "ms"
}
```

Lower-bound constraints use the same pattern:

```json
{
  "name": "minReliability",
  "constraintType": "minimum",
  "ontologyPredicate": "icm:atLeast",
  "valueType": "number",
  "required": true,
  "unit": "percent"
}
```

Do not use a platform contract field named `operator` for these upper/lower bound constraints.

## Contract validation rules:

OC MS validates runtime Optimisation requests against the ACTIVE OptimisationSpecification.

OC MS validates:

```text
required fields
value types
supported constraint names
supported target names
supported context names
constraintType values
target goal values
context object schema
cardinality rules such as candidateResources minItems = 2
```

OC MS does not validate:

```text
solver feasibility
candidate ranking
metric-vs-constraint fit
objective trade-off evaluation
best-candidate selection
```

## Contract violation response:

Use `422 Unprocessable Entity` when the JSON is structurally valid but violates the ACTIVE OptimisationSpecification request contract.

Example:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "OPTIMISATION_CONTRACT_VIOLATION",
  "reason": "Optimisation request violates specification contract",
  "message": "topologySnapshot.candidateResources must contain at least 2 candidate resources for this optimisation capability.",
  "status": 422,
  "@type": "Error"
}
```

## Relationship to OC MS:

```text
OD MS:
  defines what is allowed.

OC MS:
  stores what was accepted at runtime.

Worker/model:
  decides feasibility and returns SUCCESS, INFEASIBLE, or FAILURE.
```

## Baseline validation note:

This OD MS specification intentionally does not include actual runtime candidate resources such as path identifiers, candidate metric values, selected resources, or runtime constraint values. Those belong in OC MS runtime Optimisation examples.

---

## Shared versus candidate-specific context attributes:

Shared context attributes should be modelled at the `topologySnapshot` level.

Candidate-specific attributes should be modelled under `candidateResources[].resourceAttributes` only when they vary per candidate.

For this example, `location.locationId` belongs at `topologySnapshot` level because all candidate paths belong to the same optimisation scope/location.

Do not repeat the same `locationId` under every candidate resource.

Example runtime context shape:

```json
{
  "name": "topologySnapshot",
  "valueType": "object",
  "value": {
    "dataset": "topology-snapshot",
    "version": "2026-05-02T10:00:00Z",
    "candidateResourceSetId": "candidate-paths-surgical-melbourne-20260502T100000Z",
    "location": {
      "locationId": "melbourne-hospital"
    },
    "candidateResources": [
      {
        "resourceId": "path-001",
        "resourceType": "deliveryResource",
        "resourceClass": "low-latency-path",
        "metrics": []
      }
    ]
  }
}
```

---

## Definition E2E access path baseline:

OD MS definition access follows this path:

```text
User
-> Microsoft Entra ID SSO
-> OEX UI
-> OEX APIs
-> OGW
-> OEX Screen Builder MS
-> NGW
-> OD MS
```

OD MS sits behind NGW. OD MS does not participate in Kafka, Python/Gurobi Worker, or Gurobi Optimizer runtime execution flows.

---

## OD MS infrastructure security controls:

OD MS integrations must explicitly capture service-to-infrastructure security controls.

### OD MS -> OD MS Database:

```text
Authentication:
  OD MS connects using an authenticated OD MS service identity.

Authorisation:
  OD MS is authorised only for the OD MS database/schema/tables required for OptimisationSpecification storage and retrieval.
  No broad database admin/root access by default.

Encrypted connectivity:
  OD MS database connectivity uses encrypted transport.
  mTLS or platform-approved encrypted database connectivity is used where supported by the selected database platform.

Secrets and certificates:
  Database credentials, keys, and certificates are stored in approved secret management.
  Rotation must be supported without application code changes where possible.

Environment separation:
  OD MS database principals, roles, schemas, and credentials are environment-scoped.
  Non-production OD MS identities must not access production OD MS data.

Audit and monitoring:
  Authentication failures, authorisation denials, privileged operations, schema changes, and unusual access patterns are logged and monitored.

Ownership:
  OD MS owns application-level access to OptimisationSpecification data.
  Database/platform teams own database platform controls.
```

### OD MS -> platform cache, if introduced later:

```text
OD MS does not require a cache in the current baseline.

If a cache is introduced later, the OD MS design brief must capture:
  authenticated service identity
  least-privilege cache namespace/keyspace access
  encrypted connectivity
  approved secret/certificate management
  environment-scoped cache roles
  audit/monitoring of denied access and privileged operations
```

### OD MS -> Kafka:

```text
OD MS does not integrate directly with Kafka in the current baseline.

If OD MS later becomes a Kafka producer or consumer, the OD MS design brief must capture:
  service identity
  TLS/mTLS broker connectivity
  topic-level ACLs
  consumer-group permissions where applicable
  DLQ permissions where applicable
  secret/certificate management
  monitoring and audit controls
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

## OD MS observability focus:

OD MS observability must include specification/catalogue lifecycle monitoring.

Additional OD MS signals:

```text
OptimisationSpecification create/update/activate/retire attempts
catalogue authorisation allow/deny counts
ACTIVE specification lookup counts
specification validation failures
ETag / If-Match precondition failures
OD MS database dependency latency and failures
```
