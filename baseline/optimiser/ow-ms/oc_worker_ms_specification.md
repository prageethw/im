# OC Worker MS Specification

**Document status:**

| **Field** | **Value** |
|---|---|
| **Status** | Baseline candidate |
| **Scope** | OC Worker MS Kafka worker, Gurobi execution, cancellation, and outcome publication specification |
| **Source path** | `baseline/optimiser/oc-worker-ms/oc_worker_ms_specification.md` |
| **Source of truth** | GitHub `main` |
| **Last aligned** | 2026-05-26 |
| **Alignment scope** | Aligned with OC MS `OptimisationRequestedEvent`, `OptimisationCompletedEvent`, `creationContext.reason`, `CANCELLATIONFAILED`, retrial, result projection, and ETag-header baseline. |

## Table of contents:

- [1. Service purpose](#1-service-purpose)
- [2. Ownership boundary](#2-ownership-boundary)
- [3. Runtime responsibility](#3-runtime-responsibility)
- [4. Kafka contract](#4-kafka-contract)
- [5. OptimisationRequestedEvent consumption](#5-optimisationrequestedevent-consumption)
- [6. EXECUTE handling](#6-execute-handling)
- [7. CANCEL handling](#7-cancel-handling)
- [8. Gurobi Python API integration](#8-gurobi-python-api-integration)
- [9. Model binding](#9-model-binding)
- [10. Result mapping](#10-result-mapping)
- [11. OptimisationCompletedEvent publication](#11-optimisationcompletedevent-publication)
- [12. Idempotency and duplicate handling](#12-idempotency-and-duplicate-handling)
- [13. Failure handling and DLQ posture](#13-failure-handling-and-dlq-posture)
- [14. Security and secrets](#14-security-and-secrets)
- [15. Observability](#15-observability)
- [16. Non-goals](#16-non-goals)
- [17. Open items](#17-open-items)

## 1. Service purpose:

OC Worker MS means Optimisation Controller Worker Microservice.

OC Worker MS is the Python runtime worker responsible for consuming optimisation worker instructions from Kafka, invoking the Gurobi Python API through internal model bindings, attempting safe cancellation where requested, and publishing worker outcome events back to Kafka.

OC Worker MS is part of the internal optimisation execution plane. It is not a public REST API, not a TMF-facing resource service, and not the source of truth for runtime `Optimisation` lifecycle state.

OC MS remains the runtime `Optimisation` lifecycle owner. OC Worker MS reports outcomes through `OptimisationCompletedEvent`; OC MS consumes those outcomes and projects lifecycle and result state onto the runtime `Optimisation` resource.

## 2. Ownership boundary:

OC Worker MS owns:

```text
Kafka consumption of OptimisationRequestedEvent
Instruction handling for EXECUTE and CANCEL
Internal Gurobi Python API invocation
Internal deterministic model binding execution
Safe cancellation attempts where supported
Mapping worker and solver outcomes to platform outcome statuses
Publication of OptimisationCompletedEvent
Worker-side idempotency checks
Worker-side execution telemetry and operational diagnostics
```

OC Worker MS does not own:

```text
OD MS OptimisationSpecification lifecycle
OC MS runtime Optimisation lifecycle source of truth
OC MS REST API
OSB MS experience views
External TMF-facing API contracts
Specification activation or retirement
Runtime Optimisation persistence in OC MS database
OC MS outbox or inbox persistence
External result presentation
Business approval of optimisation capabilities
```

OC Worker MS must not directly mutate OC MS runtime tables. Lifecycle and result projection must happen through OC MS consuming `OptimisationCompletedEvent`.

## 3. Runtime responsibility:

The baseline runtime interaction is:

```text
OC MS Outbox Relay -> Kafka -> OC Worker MS -> Gurobi Python API -> OC Worker MS -> Kafka -> OC MS Inbox Consumer
```

OC Worker MS consumes worker instruction events, executes or attempts cancellation, and emits outcome events. It does not expose a client-facing API in the baseline.

The worker handles two instructions:

```text
EXECUTE
CANCEL
```

The worker emits outcomes using `OptimisationCompletedEvent.status` values:

```text
COMPLETED
INFEASIBLE
FAILED
CANCELLED
CANCELLATIONFAILED
```

`CANCELLATIONFAILED` is a cancellation-command outcome. It is not necessarily a terminal optimisation outcome. OC MS may later project `COMPLETED`, `INFEASIBLE`, or `FAILED` if a normal terminal optimisation outcome is received.

## 4. Kafka contract:

Kafka topic baseline:

```text
t7.optimisation.events
t7.optimisation.events.dlq
```

OC Worker MS consumes `OptimisationRequestedEvent` from `t7.optimisation.events`.

OC Worker MS publishes `OptimisationCompletedEvent` to `t7.optimisation.events`.

The DLQ is used for events that cannot be safely processed after retry handling. DLQ behaviour is operationally governed and must preserve enough failure metadata for diagnosis and controlled replay decisions.

OC Worker MS must treat the Kafka event contract as the platform boundary. Internal Gurobi model formulation, solver parameters, model files, candidate scoring logic, and solver-specific diagnostics are implementation details and must not be exposed in platform event payloads unless explicitly governed later.

## 5. OptimisationRequestedEvent consumption:

OC Worker MS consumes `OptimisationRequestedEvent` values emitted by OC MS.

Required CloudEvents-style headers or equivalent metadata:

```text
ce-specversion
ce-type
ce-source
ce-id
ce-time
ce-subject
correlationid
traceid
content-type
```

Required event body fields:

| **Field** | **Rule** |
|---|---|
| `eventType` | Must be `OptimisationRequestedEvent`. |
| `eventVersion` | Required event contract version. |
| `eventTime` | Required event production timestamp. |
| `correlationId` | Required for cross-service traceability. |
| `traceId` | Required where platform tracing is enabled. |
| `optimisationId` | Required OC runtime Optimisation id. |
| `instruction` | Required. Allowed values are `EXECUTE` and `CANCEL`. |
| `creationContext` | Present for `EXECUTE`; includes `reason = NEW` or `RETRIAL` where provided by OC MS. |
| `optimisationSpecification` | Resolved immutable specification pointer with `id`, `version`, `draftId`, and `href`. |
| `expression` | Accepted runtime expression, including `expression.iri` and `expression.expressionValue`. |
| `sourceContext` | Optional accepted runtime source context. |
| `priority` | Optional accepted runtime priority. |

OC Worker MS must reject or dead-letter events that are structurally invalid, missing required fields, or use an unsupported `instruction` value after retry policy is exhausted.

OC Worker MS must not re-resolve OD MS specifications by `specKey`, `draftId`, `version`, or `expression.iri`. It must use the accepted runtime payload and resolved contract pointer supplied by OC MS.

## 6. EXECUTE handling:

For `instruction = EXECUTE`, OC Worker MS must:

```text
Validate event identity and idempotency.
Validate required event fields are present.
Resolve the internal model binding for the accepted optimisation request.
Construct the Gurobi execution from internal model binding and accepted runtime input.
Execute the optimisation through the Gurobi Python API.
Map the solver or worker result to a platform status.
Publish OptimisationCompletedEvent.
```

Allowed EXECUTE outcome status values:

```text
COMPLETED
INFEASIBLE
FAILED
```

`COMPLETED` means the worker produced a usable platform-safe result.

`INFEASIBLE` means the worker and model completed correctly, but no feasible solution exists for the accepted runtime problem.

`FAILED` means the worker could not complete execution because of technical failure, model binding failure, dependency failure, solver exception, unexpected worker exception, or another execution failure that is not a valid infeasibility outcome.

OC Worker MS must not expose raw Gurobi exceptions, model internals, solver stack traces, credentials, infrastructure details, or objective formulation details in the platform-safe result payload.

## 7. CANCEL handling:

For `instruction = CANCEL`, OC Worker MS must attempt to cancel or stop the corresponding in-flight optimisation where safely possible.

Allowed CANCEL outcome status values:

```text
CANCELLED
CANCELLATIONFAILED
```

`CANCELLED` means cancellation was honoured, applied, or confirmed safely by the worker.

`CANCELLATIONFAILED` means cancellation was requested but could not be honoured, applied, or confirmed safely. It is a cancellation-command outcome, not necessarily a terminal optimisation outcome.

Cancellation is best-effort. If the worker receives `CANCEL` but the optimisation has already completed or cannot be safely interrupted, the worker must report the safest accurate outcome available.

Baseline race rule:

```text
If CANCEL arrives but the worker completes first, OC Worker MS may emit the actual terminal optimisation outcome rather than CANCELLED.
```

If the worker reports `CANCELLATIONFAILED`, OC MS may keep observing for a later normal terminal optimisation outcome, depending on the worker execution state and OC MS idempotency rules.

## 8. Gurobi Python API integration:

OC Worker MS is implemented in Python and integrates with Gurobi through the Gurobi Python API.

The baseline permits OC Worker MS to:

```text
Create and configure Gurobi model execution using internal model bindings.
Invoke optimisation solving.
Monitor execution status.
Attempt safe cancellation or termination where supported by the Gurobi API and platform policy.
Capture platform-safe solver outcome metadata.
Map solver and worker outcomes to platform statuses.
```

The following remain internal implementation details and must not be exposed in platform event payloads or external API responses unless explicitly governed later:

```text
Objective formulation
Constraint implementation
Candidate scoring logic
Gurobi parameter values
Gurobi environment configuration
Model files or model code
Solver credentials or license details
Raw solver logs
Raw stack traces
Infrastructure internals
```

## 9. Model binding:

Model binding is the internal process that maps an accepted runtime `Optimisation` request to a concrete executable model implementation.

OC Worker MS may use internal configuration, deployment metadata, capability mapping, or model registry integration to resolve model binding.

The baseline model-binding input is the accepted runtime event payload from OC MS, including:

```text
optimisationId
optimisationSpecification.id
optimisationSpecification.version
optimisationSpecification.draftId
expression.iri
expression.expressionValue
sourceContext
priority
creationContext.reason
```

Model binding must not change the accepted runtime request semantics. If the worker cannot resolve a valid model binding for an accepted request, it must emit `OptimisationCompletedEvent.status = FAILED` with safe failure details.

Model binding errors are worker execution failures, not OD MS contract validation failures. OC MS has already accepted the runtime request before emitting `OptimisationRequestedEvent`.

## 10. Result mapping:

OC Worker MS maps worker and Gurobi outcomes to platform statuses as follows:

| **Worker or solver condition** | **OptimisationCompletedEvent.status** |
|---|---|
| Solver completed and worker produced a usable platform-safe result. | `COMPLETED` |
| Solver or model proved no feasible solution exists for the accepted runtime problem. | `INFEASIBLE` |
| Worker execution failed, model binding failed, solver raised an unrecoverable exception, dependency failed, or safe result could not be produced. | `FAILED` |
| Cancellation was honoured, applied, or confirmed safely. | `CANCELLED` |
| Cancellation was requested but could not be honoured, applied, or confirmed safely. | `CANCELLATIONFAILED` |

Result payloads must be platform-safe. They may include safe summaries, safe error codes, output values, diagnostic references, and retry guidance where appropriate. They must not include sensitive solver internals.

## 11. OptimisationCompletedEvent publication:

OC Worker MS publishes `OptimisationCompletedEvent` after completing an EXECUTE or CANCEL instruction outcome.

Required CloudEvents-style headers or equivalent metadata:

```text
ce-specversion
ce-type
ce-source
ce-id
ce-time
ce-subject
correlationid
traceid
content-type
```

Required event body fields:

| **Field** | **Rule** |
|---|---|
| `eventType` | Must be `OptimisationCompletedEvent`. |
| `eventVersion` | Required event contract version. |
| `eventTime` | Required event production timestamp. |
| `correlationId` | Required and should match the request event correlation where possible. |
| `traceId` | Required where platform tracing is enabled. |
| `optimisationId` | Required OC runtime Optimisation id. |
| `status` | Required. Allowed values are `COMPLETED`, `INFEASIBLE`, `FAILED`, `CANCELLED`, and `CANCELLATIONFAILED`. |
| `result` | Optional platform-safe result or command-outcome details. Required where a useful safe result can be produced. |
| `diagnostics` | Optional safe diagnostic references or operational hints. Must not expose sensitive internals. |

Example:

```json
{
  "eventType": "OptimisationCompletedEvent",
  "eventVersion": "1.0",
  "eventTime": "2026-05-26T04:00:00Z",
  "correlationId": "corr-12345",
  "traceId": "trace-12345",
  "optimisationId": "opt-12345",
  "status": "COMPLETED",
  "result": {
    "outcome": "COMPLETED",
    "summary": "Optimisation completed successfully.",
    "outputs": [
      {
        "name": "selectedResource",
        "valueType": "object",
        "value": {
          "resourceId": "path-001",
          "resourceType": "deliveryResource"
        }
      }
    ]
  }
}
```

The event must not include raw Gurobi model formulation, solver configuration, objective internals, credential material, infrastructure internals, or raw stack traces.

## 12. Idempotency and duplicate handling:

OC Worker MS must handle duplicate `OptimisationRequestedEvent` messages safely.

Baseline idempotency inputs:

```text
eventId or ce-id
optimisationId
instruction
correlationId
creationContext.reason where present
```

Worker idempotency rules:

```text
Duplicate EXECUTE events for the same event identity must not start duplicate unsafe solver executions.
Duplicate CANCEL events for the same event identity must not produce unsafe repeated cancellation side effects.
If a duplicate event arrives after the worker has already produced an outcome, the worker should avoid re-execution and may suppress duplicate outcome publication or republish the same outcome according to platform retry policy.
If the worker cannot determine whether a duplicate event has already been executed safely, it must prefer safe failure handling over duplicate unsafe execution.
```

OC MS remains the final projection idempotency owner. Even if OC Worker MS republishes an outcome, OC MS Inbox Consumer must apply inbox deduplication and lifecycle monotonicity rules.

## 13. Failure handling and DLQ posture:

OC Worker MS should use bounded retry for transient processing failures before DLQ routing.

Examples of retryable conditions:

```text
Transient Kafka publication failure
Transient dependency failure
Temporary Gurobi environment acquisition failure
Temporary model-binding metadata lookup failure where retry is safe
```

Examples of non-retryable or DLQ-eligible conditions:

```text
Malformed event payload
Missing required event fields
Unsupported instruction value
Unresolvable model binding after retry policy
Invalid event contract version where compatibility cannot be established
Poison event that repeatedly fails processing
```

DLQ entries must include safe failure metadata needed for diagnosis and controlled replay decisions. DLQ entries must not include secrets, raw stack traces, solver credentials, or sensitive Gurobi internals.

No automatic DLQ replay is performed by default. Replay requires operational approval and controlled procedure.

## 14. Security and secrets:

OC Worker MS must use platform-approved service identity for Kafka access and any required internal dependencies.

Security baseline:

```text
TLS for Kafka connectivity where supported by the platform.
Service identity for Kafka producer and consumer access.
Topic-level ACLs.
Secrets supplied through approved secret-management mechanism.
Gurobi credentials and license details must not be logged or published in events.
Sensitive solver internals must not be exposed outside the worker boundary.
```

OC Worker MS must not forward end-user identity to Gurobi or internal model execution unless explicitly approved by security governance. User context terminates at the experience and backend service layers; worker execution is service-owned.

## 15. Observability:

OC Worker MS must produce operational telemetry sufficient to operate the optimisation execution plane.

Recommended telemetry:

```text
Kafka consumer lag
Event processing latency
Optimisation execution duration
Cancellation attempt duration
Outcome counts by status
Retry counts
DLQ counts
Gurobi environment acquisition failures
Model binding failures
Worker exceptions
Safe diagnostic references by optimisationId and correlationId
```

Logs and metrics must include `optimisationId`, `correlationId`, and `traceId` where available.

Logs must not include sensitive solver internals, credentials, raw model files, raw stack traces in public channels, or personal data unless explicitly approved.

## 16. Non-goals:

OC Worker MS is not:

```text
A public API service
A TMF-facing API resource
The runtime Optimisation lifecycle source of truth
The OD MS specification owner
The OSB experience owner
A replacement for OC MS result projection
A catalogue management service
A general-purpose solver marketplace
```

OC Worker MS does not define the public `OptimisationSpecification` contract. It consumes already-accepted runtime work from OC MS.

## 17. Open items:

The following remain open unless decided by platform or product implementation teams:

```text
Exact Gurobi environment deployment model.
Exact Gurobi license and credential injection mechanism.
Detailed model registry or model-binding source.
Worker concurrency limits.
Job timeout policy.
Cancellation timeout policy.
Retry limits and backoff values.
DLQ replay procedure.
Safe result detail schema per optimisation capability.
Operational dashboards and alert thresholds.
```

These open items do not change the OC MS platform event boundary or OC MS ownership of runtime lifecycle projection.
