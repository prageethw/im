> Baseline pack: Intent Management / Intent Enabler only  
> Generated: 20260510_133900  
> Scope rule: Intent Management / Intent Enabler only. Do not import other domain context unless explicitly requested later.

# Intent Baseline Context Dump

## 1. Scope guard

This baseline pack is for Intent Management / Intent Enabler only.

Do not import other domain architecture context into this pack unless the scope is explicitly changed later.

The active domain terms are Intent, IntentSpecification, Intent lifecycle, Intent assurance, Intent callback, Intent validation, Intent resolution, and TMF921 Intent Management alignment.

## 2. Source compliance artifacts

The following attached artifacts are the compliance validation references for external TMF facing API, resource, schema, and event shapes:

| Artifact | Use |
|---|---|
| `TMF921_Intent_Management_v5.0.0_specification.pdf` | Primary TMF921 specification reference |
| `TMF921_Intent_Management_v5.0.0_conformance.pdf` | TMF921 conformance reference |
| `TMF921_Intent_Management_v5.0.0.oas.yaml` | OpenAPI schema and endpoint reference |
| `TR292_TMForum_Intent_Ontology_TIO_v3.6.0.pdf` | Intent ontology and semantic alignment reference |

Use these files preferentially over memory when validating compliance.

## 3. Service names and boundaries

| Short name | Service name | Boundary |
|---|---|---|
| ID MS | `intent-design-ms` | Owns IntentSpecification catalogue and governance |
| IC MS | `intent-controller-ms` | Owns canonical runtime Intent resource and external TMF Intent events |
| II MS | `intent-intelligence-ms` | Owns semantic interpretation and resolution decision input preparation |
| IA MS | `intent-assurance-ms` | Owns assurance correlation, runtime drift/degradation interpretation, and lifecycle input back to IC MS |
| ICB MS | `intent-callback-ms` | Owns inbound callback mediation and raw callback event publication |

Important naming rule: II MS means Intent Intelligence MS and uses service name `intent-intelligence-ms`. Do not use `intent-interpreter-ms`.

Important callback naming rule: ICB MS means Intent Callback MS / `intent-callback-ms`. Do not use CB MS to mean the callback service. CB means circuit breaker.

## 4. External runtime expression baseline

External TMF-facing runtime Intent expression shape:

```json
{
  "expression": {
    "@type": "IntentExpression",
    "expressionLanguage": "JSON",
    "expressionValue": {
      "context": {
        "targets": [],
        "constraints": [],
        "preferences": []
      }
    }
  }
}
```

Rules:

| Rule | Baseline |
|---|---|
| Canonical buckets | `targets`, `constraints`, `preferences` |
| Context shape | `expression.expressionValue.context` externally |
| Peer fields | No domain peer fields beside the three buckets inside `context` |
| Location | Model under `context.constraints` |
| Service type | Model under `context.constraints` |
| Service class | Model under `context.constraints` |
| Priority | Model under `context.constraints` |
| Internal events | Use native JSON context without TMF wrapper, e.g. `body.expression.context.targets` |
| Characteristic catalogue | IntentSpecification exposes one high-level `context` CharacteristicSpecification |
| Detailed validation | External expression-value schema referenced by `targetEntitySchema.@schemaLocation` |

## 5. Priority vocabulary baseline

Use `critical`, `high`, and `standard`.

Do not use `clinical-critical`.

Use field name `priority`, not `priority_level`.

## 6. IntentSpecification baseline principles

| Topic | Baseline |
|---|---|
| `@baseType` | `EntitySpecification` |
| Top-level characteristic catalogue | Use `specCharacteristic` |
| Runtime expression validation | Use `expressionSpecification` and `targetEntitySchema` |
| Detailed semantic inputs | Captured in `context.targets`, `context.constraints`, and `context.preferences` |
| CharacteristicValueSpecification | Use only for defaults, examples, or constrained discovery/governance values |
| Numeric SLA characteristics | Defaults/examples are governance and request-authoring guidance only; they are not semantic enforcement rules in ID MS |
| Semantic validation | II MS and Knowledge Plane |
| Runtime assurance | IA MS |


## 7. Intent lifecycle baseline

Runtime Intent lifecycle states include:

| State | Meaning |
|---|---|
| `InProgress` | Intent has been accepted and is being validated, resolved, orchestrated, or activated |
| `Active` | A specific Intent version is currently fulfilled/effective in the network |
| `Degraded` | Intent remains active but assurance indicates it is not meeting target quality or is at risk |
| `Failed` | The active version has failed and requires lifecycle handling or rollback |
| `Rejected` | The intent request failed validation or admission and will not proceed |
| `Terminated` | The version is no longer active/effective |

## 8. Version, lifecycle, and effectiveVersion baseline

Each Intent version has its own lifecycle.

Once a version becomes `Active`, it becomes the `effectiveVersion` even if it later becomes `Failed`.

Rollback is not automatic network magic. If version `1.1` becomes `Active` then fails, returning version `1.0` to active service requires another orchestration cycle.

| Scenario | Version 1.0 lifecycle | Version 1.1 lifecycle | `effectiveVersion` | Required behaviour |
|---|---|---|---|---|
| Initial active version | `Active` | Not created | `1.0` | Version 1.0 is fulfilled in network |
| New version submitted | `Active` or `Terminated` depending transition stage | `InProgress` | `1.0` until 1.1 activates | IC MS tracks each version lifecycle separately |
| New version activates | `Terminated` | `Active` | `1.1` | 1.1 becomes effective version |
| New version later fails | `Terminated` | `Failed` | `1.1` | Effective version remains 1.1 because it was the last active version |
| Rollback requested | `InProgress` or new recovery cycle | `Failed` | `1.1` until 1.0 reactivates | IC/II/orchestration must run another cycle |
| Rollback complete | `Active` | `Failed` or `Terminated` | `1.0` | 1.0 becomes effective again only after successful orchestration |

Persistence decision: keep versions in one logical table/collection by default, not a separate old-version table. Use version identifiers, lifecycle state, current/effective markers, audit fields, and optimistic concurrency rather than moving active/old versions to separate persistence models.

## 9. External and internal event ownership

| Event or event family | Owner | Baseline |
|---|---|---|
| External `IntentStatusChangeEvent` | IC MS | IC emits after updating canonical Intent resource state |
| External `IntentAttributeValueChangeEvent` | IC MS | Design-time/declarative Intent attribute change, not runtime telemetry |
| Internal lifecycle input from assurance | IA MS | IA emits internal lifecycle update to IC MS |
| Internal `IntentValidatedEvent` | IC MS | Syntactic validation success handoff to II MS |
| Internal `IntentResolvedEvent` | II MS | Emitted only when resolution work is required |
| Internal `IntentCallbackEvent` | ICB MS | Accepted raw callback event to Kafka for IA MS |
| Separate external `IntentDriftOccurredEvent` | Not used | Assurance event / lifecycle input covers drift and degradation |

## 10. Circuit breaker baseline

| Condition | HTTP behaviour |
|---|---|
| Circuit breaker triggered and no safe fallback can preserve contract meaning | `503 Service Unavailable` |
| Circuit breaker triggered but safe degraded fallback preserves contract meaning | `200 OK` with valid degraded response body and degradation signal |

Apply this pattern consistently across services unless specifically exempted.

## 11. ETag, optimistic concurrency, and caching baseline

Use strong ETags for mutable canonical resources.

Mutating operations that update or delete an existing resource require `If-Match` unless a specific endpoint is exempted.

Stale or mismatched `If-Match` returns:

```http
HTTP/1.1 412 Precondition Failed
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

```json
{
  "code": "PRECONDITION_FAILED",
  "reason": "ETAG_MISMATCH",
  "message": "The supplied If-Match value does not match the current resource version.",
  "status": "412",
  "referenceError": "https://mycsp.com.au/errors/PRECONDITION_FAILED",
  "@type": "Error"
}
```

GET operations may use private caching with ETag/conditional requests when it does not weaken correctness.

## 12. Database baseline

Managed PostgreSQL / PostgreSQL-compatible RDBMS is the default source-of-truth database for main Intent microservices and transactional entity persistence.

Use JSONB for flexible document-shaped resource bodies where appropriate.

NoSQL/document DB is not the default because lifecycle governance, versioning, ETag/If-Match, relationships, transactional outbox/inbox, auditability, query/list APIs, and operational simplicity favour an RDBMS default.

Specialised non-RDBMS stores remain secondary/future options only when access patterns justify them.

Initial deployment may be single-region or same-region multi-AZ, but selected service must support future cross-region active-passive DR. Active-active writes and distributed SQL remain future options only if explicitly required.

## 13. Security baseline for platform integrations

Any integration with database, cache, Kafka, object store, API gateway, secrets manager, or other platform infrastructure must capture:

| Control | Baseline |
|---|---|
| Authenticated identity | Every service uses authenticated workload identity |
| Authorisation | Least-privilege access per service and environment |
| Encryption | Encrypted connectivity in transit; encrypted storage at rest where supported |
| Secrets | Approved secret/certificate management and rotation |
| Environment scoping | Separate principals/roles per environment |
| No broad admin | No wildcard/admin access by default |
| Audit | Access failures, privileged operations, and policy denials are monitored |
| Ownership | Producer/consumer/read/write ownership is documented |
| Kafka | Topic-level producer/consumer ACLs and consumer group ownership |
| Database | Schema/table permissions are limited to the owning service role |

## 14. Closed-loop activity diagram baseline

The PlantUML activity diagram of the intent management pre-drift and post-drift loop is baselined under the title `Closed loop activity diagram`.

## 15. Baseline file policy

When future baseline updates are made, append silently to the running context dump and update the relevant service file unless the user asks to see the dump.

When generating downloadable artifacts, use unique filenames with timestamp/version suffixes to avoid stale download caching.
