# Optimisation Worker MS Specification

**Document status:**

| **Field** | **Value** |
|---|---|
| **Status** | Baseline candidate |
| **Scope** | OW MS Kafka worker, Gurobi execution, cancellation, and outcome publication specification |
| **Source path** | `baseline/optimiser/ow-ms/ow_ms_specification.md` |
| **Source of truth** | GitHub `main` |
| **Last aligned** | 2026-05-26 |
| **Alignment scope** | Aligned with OC MS `OptimisationRequestedEvent`, `OptimisationCompletedEvent`, `creationContext.reason`, `CANCELLATIONFAILED`, retrial, result projection, ETag-header baseline, and circuit-breaker response signalling. |

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
- [10. Internal worker execution state model](#10-internal-worker-execution-state-model)
- [11. Worker job registry](#11-worker-job-registry)
- [12. Result mapping](#12-result-mapping)
- [13. OptimisationCompletedEvent publication](#13-optimisationcompletedevent-publication)
- [14. Safe result payload baseline](#14-safe-result-payload-baseline)
- [15. Idempotency, ordering, and duplicate handling](#15-idempotency-ordering-and-duplicate-handling)
- [16. Failure handling and DLQ posture](#16-failure-handling-and-dlq-posture)
- [17. Timeouts and execution limits](#17-timeouts-and-execution-limits)
- [18. Backpressure and capacity handling](#18-backpressure-and-capacity-handling)
- [19. Result size and artifact handling](#19-result-size-and-artifact-handling)
- [20. Model artifact integrity](#20-model-artifact-integrity)
- [21. Resource cleanup and graceful shutdown](#21-resource-cleanup-and-graceful-shutdown)
- [22. Security and secrets](#22-security-and-secrets)
- [23. Observability](#23-observability)
- [24. Non-goals](#24-non-goals)
- [25. Open items](#25-open-items)

## 1. Service purpose:

OW MS means Optimisation Worker MS.

OW MS is the Python runtime worker responsible for consuming optimisation worker instructions from Kafka, invoking the Gurobi Python API through internal model bindings, monitoring running optimisation jobs, attempting safe cancellation where requested, and publishing worker outcome events back to Kafka.

OW MS is part of the internal optimisation execution plane. It is not a public REST API, not a TMF-facing resource service, and not the source of truth for runtime `Optimisation` lifecycle state.

OC MS remains the runtime `Optimisation` lifecycle owner. OW MS reports outcomes through `OptimisationCompletedEvent`; OC MS consumes those outcomes and projects lifecycle and result state onto the runtime `Optimisation` resource. OW MS emits outcome facts only; it must not treat its internal execution state as REST-visible lifecycle state.

## 2. Ownership boundary:

OW MS owns:

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

OW MS does not own:

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

OW MS must not directly mutate OC MS runtime tables. Lifecycle and result projection must happen through OC MS consuming `OptimisationCompletedEvent`.

## 3. Runtime responsibility:

The baseline runtime interaction is:

```text
OC MS Outbox Relay -> Kafka -> OW MS -> Gurobi Python API -> OW MS -> Kafka -> OC MS Inbox Consumer
```

OW MS consumes worker instruction events, executes or attempts cancellation, and emits outcome events. It does not expose a client-facing API in the baseline.

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

OW MS consumes `OptimisationRequestedEvent` from `t7.optimisation.events` using a dedicated OW MS Kafka consumer group. This consumer group must not be shared with OC MS, OC MS inbox consumers, operational replay consumers, or other services.

Kafka delivery is treated as at-least-once. OW MS must be idempotent for duplicate `OptimisationRequestedEvent` messages and must not rely on exactly-once delivery for safe execution.

OW MS publishes `OptimisationCompletedEvent` to `t7.optimisation.events`.

The DLQ is used for events that cannot be safely processed after retry handling. DLQ behaviour is operationally governed and must preserve enough failure metadata for diagnosis and controlled replay decisions. OW MS may route unprocessable worker-side events to the DLQ according to retry policy, but DLQ replay is operationally controlled and must preserve idempotency.

OW MS must treat the Kafka event contract as the platform boundary. Internal Gurobi model formulation, solver parameters, model files, candidate scoring logic, and solver-specific diagnostics are implementation details and must not be exposed in platform event payloads unless explicitly governed later.

## 5. OptimisationRequestedEvent consumption:

OW MS consumes `OptimisationRequestedEvent` values emitted by OC MS.

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

OW MS must reject or dead-letter events that are structurally invalid, missing required fields, or use an unsupported `instruction` value after retry policy is exhausted.

OW MS must not re-resolve OD MS specifications by `specKey`, `draftId`, `version`, or `expression.iri`. It must use the accepted runtime payload and resolved contract pointer supplied by OC MS.

## 6. EXECUTE handling:

For `instruction = EXECUTE`, OW MS must:

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

OW MS must not expose raw Gurobi exceptions, model internals, solver stack traces, credentials, infrastructure details, or objective formulation details in the platform-safe result payload.

## 7. CANCEL handling:

For `instruction = CANCEL`, OW MS must attempt to cancel or stop the corresponding in-flight optimisation where safely possible.

Allowed CANCEL outcome status values:

```text
CANCELLED
CANCELLATIONFAILED
```

`CANCELLED` means cancellation was honoured, applied, or confirmed safely by the worker.

`CANCELLATIONFAILED` means cancellation was requested but could not be honoured, applied, or confirmed safely. It is a cancellation-command outcome, not necessarily a terminal optimisation outcome.

Cancellation is best-effort. If the worker receives `CANCEL` but the optimisation has already completed or cannot be safely interrupted, the worker must report the safest accurate outcome available.

Baseline race and cancellation rules:

```text
If CANCEL arrives before a matching EXECUTE is observed, OW MS may record cancellation intent in the job registry or route the event to retry according to ordering policy. If CANCEL arrives before execution starts and OW MS can suppress execution safely, OW MS emits CANCELLED.
If CANCEL arrives while execution is running and Gurobi can be stopped safely, OW MS emits CANCELLED.
If CANCEL arrives but cancellation cannot be honoured, applied, or confirmed safely, OW MS emits CANCELLATIONFAILED.
If CANCEL arrives but execution completes before cancellation is applied, OW MS emits the actual terminal optimisation outcome rather than `CANCELLED`.
If CANCEL arrives for unknown work and no safe local job record exists, OW MS emits CANCELLATIONFAILED or routes to retry or DLQ according to operational policy.
```

If the worker reports `CANCELLATIONFAILED`, OC MS may keep observing for a later normal terminal optimisation outcome, depending on the worker execution state and OC MS idempotency rules.

## 8. Gurobi Python API integration:

OW MS is implemented in Python and integrates with Gurobi through the Gurobi Python API.

The baseline permits OW MS to:

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

OW MS may use internal configuration, deployment metadata, capability mapping, or model registry integration to resolve model binding.

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

Model binding may maintain internal traceability metadata such as `modelBindingId`, `modelBindingVersion`, model artifact version, or configuration version. This metadata is internal unless OC MS result projection explicitly allows a safe reference.

Model binding must not change the accepted runtime request semantics. If the worker cannot resolve a valid model binding for an accepted request, it must emit `OptimisationCompletedEvent.status = FAILED` with safe failure details.

Model binding errors are worker execution failures, not OD MS contract validation failures. OC MS has already accepted the runtime request before emitting `OptimisationRequestedEvent`.

## 10. Internal worker execution state model:

OW MS may maintain an internal worker execution state model for safe processing, observability, cancellation lookup, and duplicate handling. This state model is internal to OW MS and must not be exposed as the OC MS runtime `lifecycleStatus`.

Internal worker state baseline:

```text
RECEIVED
CLAIMED
RUNNING
CANCELLING
OUTCOME_PUBLISHED
DLQ_PENDING
```

State meaning:

| **Internal state** | **Meaning** |
|---|---|
| `RECEIVED` | OW MS has consumed a Kafka instruction but has not yet claimed execution. |
| `CLAIMED` | OW MS has accepted responsibility for processing the instruction after idempotency checks. |
| `RUNNING` | OW MS is executing or monitoring Gurobi work for an `EXECUTE` instruction. |
| `CANCELLING` | OW MS is attempting to cancel, interrupt, or suppress execution where safely possible. |
| `OUTCOME_PUBLISHED` | OW MS has published an `OptimisationCompletedEvent` or equivalent outcome event. |
| `DLQ_PENDING` | OW MS cannot safely process the event and it is pending DLQ routing after retry policy. |

Internal worker state must not be confused with OC MS runtime lifecycle. OC MS remains the lifecycle source of truth after consuming worker outcome events.

## 11. Worker job registry:

OW MS should maintain a worker job registry so `CANCEL` instructions can locate in-flight work by `optimisationId`.

The job registry may be implemented using in-memory state, a persistent store, or another platform-approved coordination mechanism depending on deployment reliability requirements. Registry durability is deployment-governed. If cancellation must work across worker restarts or worker-instance failover, the registry or equivalent coordination state must survive worker restart.

Minimum job registry fields:

```text
optimisationId
eventId or ce-id
instruction
workerInstanceId
internalState
startedAt
lastHeartbeatAt
cancelRequestedAt where applicable
publishedOutcomeStatus where applicable
correlationId
traceId
```

Job registry rules:

```text
The registry is an internal worker coordination mechanism, not a public resource.
The registry must not replace OC MS runtime Optimisation persistence.
The registry must not expose Gurobi model internals, credentials, raw logs, or solver stack traces.
If the registry is persistent, access must use least-privilege service identity and encrypted connectivity.
```

For horizontally scaled workers, the registry or consumer-group strategy must prevent unsafe duplicate solver execution for the same `optimisationId` and instruction. Horizontal scaling must preserve per-`optimisationId` idempotency, cancellation lookup correctness, and job-registry ownership semantics.

## 12. Result mapping:

OW MS maps worker and Gurobi outcomes to platform statuses as follows:

| **Worker or solver condition** | **OptimisationCompletedEvent.status** |
|---|---|
| Solver completed and worker produced a usable platform-safe result. | `COMPLETED` |
| Solver or model proved no feasible solution exists for the accepted runtime problem. | `INFEASIBLE` |
| Worker execution failed, model binding failed, solver raised an unrecoverable exception, dependency failed, or safe result could not be produced. | `FAILED` |
| Cancellation was honoured, applied, or confirmed safely. | `CANCELLED` |
| Cancellation was requested but could not be honoured, applied, or confirmed safely. | `CANCELLATIONFAILED` |

Result payloads must be platform-safe. They may include safe summaries, safe error codes, output values, diagnostic references, and retry guidance where appropriate. They must not include sensitive solver internals.

## 13. OptimisationCompletedEvent publication:

OW MS publishes `OptimisationCompletedEvent` after completing an EXECUTE or CANCEL instruction outcome.

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

Worker event timestamps are informational. OC MS remains responsible for final lifecycle projection using inbox idempotency, lifecycle monotonicity, and status-change rules.

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

## 14. Safe result payload baseline:

OW MS emits platform-safe result payloads only. Result payloads are consumed by OC MS and projected into runtime `Optimisation.result` according to OC MS rules.

Minimal safe result shape:

```json
{
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
  ],
  "diagnostics": [
    {
      "code": "SAFE_DIAGNOSTIC_REFERENCE",
      "message": "Safe diagnostic reference for operational support."
    }
  ]
}
```

Outcome-specific guidance:

| **Status** | **Result guidance** |
|---|---|
| `COMPLETED` | May include safe output values and summary. |
| `INFEASIBLE` | May include safe infeasibility summary and safe diagnostic references. Must not expose solver formulation internals. |
| `FAILED` | May include safe error code, safe message, retry guidance, and diagnostic reference. Must not expose raw exception details. |
| `CANCELLED` | May include safe cancellation summary metadata. |
| `CANCELLATIONFAILED` | May include safe cancellation-attempt outcome details. It must be clear that this is a cancellation-command outcome, not a terminal optimisation outcome. |

The result payload must not include raw Gurobi model formulation, objective formulas, objective internals, constraint implementation details, constraint internals, candidate scoring logic, solver parameter values, model files, credentials, infrastructure internals, raw Gurobi exceptions, raw solver logs, or raw stack traces.

## 15. Idempotency, ordering, and duplicate handling:

OW MS must handle duplicate `OptimisationRequestedEvent` messages safely because Kafka delivery is treated as at-least-once in the platform baseline.

Baseline idempotency inputs:

```text
eventId or ce-id
optimisationId
instruction
correlationId
creationContext.reason where present
```

Worker idempotency and ordering rules:

```text
Duplicate EXECUTE events for the same event identity must not start duplicate unsafe solver executions.
Duplicate CANCEL events for the same event identity must not produce unsafe repeated cancellation side effects.
If a duplicate event arrives after the worker has already produced an outcome, the worker should avoid re-execution and may suppress duplicate outcome publication or republish the same outcome according to platform retry policy.
If the worker cannot determine whether a duplicate event has already been executed safely, it must prefer safe failure handling over duplicate unsafe execution.
If CANCEL arrives before EXECUTE has been claimed, OW MS may record the cancellation intent and suppress execution if the matching EXECUTE is later received, or route to retry and DLQ according to operational policy.
If CANCEL arrives while EXECUTE is running on another worker instance, OW MS must use the job registry or platform coordination mechanism to locate the owning execution where possible.
If EXECUTE is received after an outcome has already been published for the same optimisationId and instruction context, OW MS must not start a new solver execution unless the event identity and OC MS instruction context prove it is a distinct accepted request.
```

OC MS remains the final projection idempotency owner. Even if OW MS republishes an outcome, OC MS Inbox Consumer must apply inbox deduplication and lifecycle monotonicity rules.

## 16. Failure handling and DLQ posture:

OW MS should use bounded retry for transient processing failures before DLQ routing.

Examples of retryable conditions:

```text
Transient Kafka publication failure
Transient dependency failure
Temporary Gurobi environment acquisition failure
Temporary model-binding metadata lookup failure where retry is safe
Temporary artifact-store or model-registry access failure where retry is safe
Temporary capacity exhaustion where backpressure or retry is safer than failure
```

Retryable failures are infrastructure, dependency, or capacity failures where retry can safely produce the same intended execution without changing the accepted runtime problem.

Examples of non-retryable or DLQ-eligible conditions:

```text
Malformed event payload
Missing required event fields
Unsupported instruction value
Unresolvable model binding after retry policy
Model artifact integrity failure where platform policy requires verified artifacts
Invalid event contract version where compatibility cannot be established
Poison event that repeatedly fails processing
```

Non-retryable failures are contract, compatibility, integrity, or model-binding failures where retry is not expected to succeed without a governed correction.

Schema-invalid, unsupported, or non-processable poison events are routed to DLQ only after the configured retry policy is exhausted, unless the failure is classified as non-retryable by platform policy.

DLQ entries must include safe failure metadata needed for diagnosis and controlled replay decisions. DLQ entries must not include secrets, raw stack traces, solver credentials, or sensitive Gurobi internals.

No automatic DLQ replay is performed by default. Replay requires operational approval and controlled procedure. Replayed DLQ events must retain original identity where required for idempotency and must not create duplicate unsafe Gurobi execution.

## 17. Timeouts and execution limits:

OW MS timeout and limit values are deployment-governed unless explicitly baselined later.

Timeout and limit categories:

```text
execution timeout
solver runtime timeout
cancellation timeout
model-binding lookup timeout
Kafka publish retry timeout
stale job heartbeat timeout
worker concurrency limit
maximum in-flight Gurobi jobs per worker instance
```

Timeout rules:

```text
Timeouts must be observable and alertable.
A timeout that prevents safe completion maps to FAILED unless it is a cancellation-specific timeout that maps to CANCELLATIONFAILED.
Timeouts must not expose raw solver internals in result payloads.
Timeout and concurrency policies must be configurable per deployment or capability where required.
```

## 18. Backpressure and capacity handling:

OW MS must protect worker capacity, Gurobi license capacity, Kafka stability, and downstream dependencies.

Backpressure rules:

```text
OW MS should pause, slow, or limit Kafka consumption when worker capacity is exhausted.
OW MS should pause, slow, or limit Kafka consumption when Gurobi license capacity is exhausted or unavailable.
OW MS must not claim more work than it can safely execute, monitor, cancel, and publish outcomes for.
Backpressure decisions must be observable through metrics and alerts.
Backpressure must not cause unsafe duplicate execution for the same optimisationId.
```

Capacity controls are deployment-governed, but must align with worker concurrency limits, maximum in-flight Gurobi jobs per worker instance, retry policy, and job-registry ownership semantics.

### 18.1. Circuit breaker and remote dependency behaviour:

OW MS must apply circuit breakers, timeouts, bounded retries, and isolation to remote dependencies such as Kafka, model registries, external data sources, Gurobi runtime or solver dependencies, cache or job-registry stores where used, and other approved platform dependencies.

If a non-critical cache or registry acceleration path is unavailable but OW MS can still use a safe source-of-truth path, OW MS should bypass the non-critical dependency without changing the worker outcome semantics.

When a remote dependency circuit breaker is triggered during asynchronous execution, OW MS must choose the safest governed behaviour for the operation: backpressure, bounded retry, DLQ routing, use of an approved verified cached artifact, or emission of a safe `FAILED` or `CANCELLATIONFAILED` outcome where appropriate. OW MS must not fake `COMPLETED`, `CANCELLED`, or any other successful outcome when the required execution, cancellation, or verification did not actually complete safely.

`x-cb-triggered` is a REST response header and is not used on OW MS Kafka outcome events. OW MS circuit-breaker state must instead be observable through metrics, logs, traces, and safe outcome or DLQ metadata.

Circuit-breaker fallback must not silently alter optimisation result semantics, cancellation confirmation, model binding, artifact integrity, security visibility, or audit state.

While a circuit breaker is open, OW MS must monitor recovery through bounded health probes or test calls according to platform circuit-breaker policy. Probe behaviour must be rate-limited and must not overload a recovering dependency.

## 19. Result size and artifact handling:

OW MS must keep `OptimisationCompletedEvent.result` within Kafka and platform message-size policy.

Result size rules:

```text
Result payloads must be bounded and platform-safe.
Large solver artifacts, debug files, model exports, detailed logs, or bulky outputs must not be embedded in Kafka events.
If large artifacts are needed for operational support, they must be stored in an approved internal artifact store and referenced through safe diagnostic references only.
Artifact references must be access-controlled and must not expose solver internals to unauthorised consumers.
```

The platform-safe result payload should contain only summaries, safe output values, safe error codes, safe diagnostic references, and retry guidance where applicable.

## 20. Model artifact integrity:

OW MS must verify model artifact integrity before execution when model artifacts or model-binding configuration are loaded from an external registry, file store, container image, or configuration source.

Integrity rules:

```text
Model artifacts must come from approved sources.
Model artifact versions must be traceable through internal metadata such as modelBindingId, modelBindingVersion, artifact version, checksum, or signature reference.
OW MS should validate checksum, signature, or equivalent integrity metadata before execution where supported by the deployment.
If model artifact integrity cannot be verified when required, OW MS must fail safely and emit FAILED with safe failure details.
Integrity failure details must not expose model internals, credentials, or raw stack traces.
```

Model artifact integrity metadata is internal unless OC MS result projection explicitly allows a safe reference.

## 21. Resource cleanup and graceful shutdown:

OW MS must clean up worker-owned runtime resources after terminal outcome, cancellation outcome, failed execution, timeout, or DLQ routing.

Cleanup rules:

```text
Release Gurobi model handles, environments, and execution resources where applicable.
Remove or expire temporary files and scratch data.
Clear sensitive in-memory material where practical.
Update job registry state to OUTCOME_PUBLISHED or DLQ_PENDING as appropriate.
Avoid retaining raw solver logs, model files, credentials, or stack traces outside approved operational stores.
```

Graceful shutdown rules:

```text
OW MS should stop claiming new work when shutdown begins.
OW MS should preserve enough job-registry state to avoid unsafe duplicate execution after restart.
OW MS should publish a safe outcome, checkpoint safe internal state, or allow controlled retry according to deployment policy for in-flight jobs.
OW MS must avoid losing cancellation intent or in-flight job ownership where cross-restart cancellation is required.
OW MS must not acknowledge Kafka work as safely complete until outcome publication, durable handoff, or DLQ routing has reached the platform-defined safe point.
```

Shutdown and cleanup behaviour must be observable and covered by operational runbooks.

## 22. Security and secrets:

OW MS must use platform-approved service identity for Kafka access and any required internal dependencies.

Security baseline:

```text
TLS for Kafka connectivity where supported by the platform.
Service identity for Kafka producer and consumer access.
Topic-level ACLs.
Least-privilege access to any worker job registry or model-binding store.
Encrypted connectivity to internal dependencies.
Secrets supplied through approved secret-management mechanism.
Gurobi credentials and license details must be supplied through approved secret management, rotated according to platform policy, and must not be logged, written to job registry records, or published in events or result payloads.
Model artifacts and model-binding configuration must be access controlled.
Sensitive solver internals must not be exposed outside the worker boundary.
```

OW MS must not forward end-user identity to Gurobi or internal model execution unless explicitly approved by security governance. User context terminates at the experience and backend service layers; worker execution is service-owned.

## 23. Observability:

OW MS must produce operational telemetry sufficient to operate the optimisation execution plane.

Recommended telemetry:

```text
Kafka consumer lag
Event processing latency
Optimisation execution duration
Solver runtime duration
Cancellation attempt duration
Cancellation success and cancellation failed counts
Outcome counts by status
Retry counts
DLQ counts
Duplicate event detections
Job registry claim conflicts
Gurobi environment acquisition failures
Model binding failures
Worker exceptions
Safe diagnostic references by optimisationId and correlationId
```

Logs and metrics must include `optimisationId`, `correlationId`, and `traceId` where available.

Logs must not include sensitive solver internals, credentials, raw model files, raw stack traces in public channels, or personal data unless explicitly approved.

## 24. Non-goals:

OW MS is not:

```text
A public API service
A TMF-facing API resource
The runtime Optimisation lifecycle source of truth
The OD MS specification owner
The OSB experience owner
A replacement for OC MS result projection
A writer to OC MS runtime database tables
A catalogue management service
A general-purpose solver marketplace
The owner of OC MS lifecycle projection
```

OW MS does not define the public `OptimisationSpecification` contract. It consumes already-accepted runtime work from OC MS.

## 25. Open items:

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
Result size limits and large-artifact storage policy.
Model artifact checksum or signature validation mechanism.
Graceful shutdown policy for in-flight jobs.
Backpressure thresholds for worker and Gurobi license capacity.
```

These open items do not change the OC MS platform event boundary or OC MS ownership of runtime lifecycle projection.
