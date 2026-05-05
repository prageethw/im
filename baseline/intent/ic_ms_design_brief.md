# ic_ms_design_brief.md

## Service identity:

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Controller MS |
| Short name | IC MS |
| Service name | `intent-controller-ms` |
| Domain | Intent Domain |
| Primary resource | `Intent` |
| Secondary resource | `IntentReport` |
| Primary responsibility | TMF-facing runtime intent controller and lifecycle/status projection |

## IC MS core purpose:

IC MS owns the runtime intent API boundary for the Intent Enabler.

It is responsible for:

| **Area** | **IC MS responsibility** |
|---|---|
| External `Intent` API | Create, retrieve, list, update, patch, delete runtime intents |
| External `IntentReport` API | Expose read-only assurance/report projections for intents |
| Runtime lifecycle/status projection | Own external `Intent.lifecycleStatus`, `statusReason`, and `statusChangeDate` |
| Syntactic validation | Validate incoming runtime `Intent` against active `IntentSpecification` from ID MS |
| Initial admission | Accept syntactically valid requests and project `Acknowledged` |
| State/progress event publication | Emit `IntentValidatedEvent` to the internal event backbone after syntactic validation succeeds |
| Rejection projection | Consume rejection outcome from II MS and project `Rejected` |
| Assurance projection | Consume `IntentAssuranceEvent` from IA MS and update external `Intent` / `IntentReport` |
| External events | Emit TMF-style `Intent*Event` and `IntentReport*Event` events |

## IC MS does not own:

| **Not owned by IC MS** | **Owner** |
|---|---|
| `IntentSpecification` design-time catalogue | ID MS |
| Semantic validation | II MS |
| Policy validation | II MS + lightweight II MS KP + `t7.knowledge plane` |
| Knowledge resolution | II MS + `t7.knowledge plane` |
| Optimisation | `t7.optimiser` |
| Network apply | IA MS + `t7.orchestrator` |
| Runtime assurance truth | IA MS |
| Real-time telemetry | `t7.telemetry` consumed by IA MS |
| Callback ingestion | ICB MS |
| Raw orchestrator callback interpretation | IA MS |

## IC MS API surface:

### Intent resource APIs:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create runtime intent | `POST` | `/intentManagement/v5/intent` |
| List runtime intents | `GET` | `/intentManagement/v5/intent` |
| Retrieve runtime intent by ID | `GET` | `/intentManagement/v5/intent/{id}` |
| Full replace runtime intent | `PUT` | `/intentManagement/v5/intent/{id}` |
| Partial update runtime intent | `PATCH` | `/intentManagement/v5/intent/{id}` |
| Delete / terminate runtime intent | `DELETE` | `/intentManagement/v5/intent/{id}` |

### IntentReport APIs:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| List reports for intent | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport` |
| Retrieve report by ID | `GET` | `/intentManagement/v5/intent/{intentId}/intentReport/{id}` |

### Hub subscription APIs:

Strict TMF route form:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create event subscription | `POST` | `/intentManagement/v5/hub` |
| Delete event subscription | `DELETE` | `/intentManagement/v5/hub/{id}` |

Accepted domain-scoped platform extension:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Create intent event subscription | `POST` | `/intentManagement/v5/intent/hub` |
| Retrieve intent event subscription | `GET` | `/intentManagement/v5/intent/hub/{id}` |
| Delete intent event subscription | `DELETE` | `/intentManagement/v5/intent/hub/{id}` |

## IC MS validation responsibility:

On `POST /intentManagement/v5/intent`, IC MS:

1. receives the external runtime intent request
2. validates basic TMF/resource shape
3. resolves the referenced `IntentSpecification`
4. validates the request against the active `IntentSpecification`
5. rejects syntactically invalid requests
6. accepts syntactically valid requests
7. creates/persists the external `Intent` projection
8. sets initial `lifecycleStatus = Acknowledged`
9. emits `IntentValidatedEvent` to the internal event backbone after syntactic validation succeeds

IC MS validates syntax and contract shape only.

It does not decide semantic meaning, network feasibility, policy allowability, resource candidates, optimisation, apply result, or runtime assurance truth.

## IntentValidatedEvent production rule:

IC MS does not emit `IntentValidatedEvent` as a point-to-point command for one specific consumer.

IC MS emits `IntentValidatedEvent` as a platform state/progress event that states:

```text
This Intent has passed IC MS syntactic validation and has been admitted into the intent lifecycle.
```

Current primary consumer:

```text
II MS / intent-intelligence-ms
```

II MS is the current primary consumer because it performs semantic validation and resolution. However, the event is not defined only for II MS. It may be consumed by other authorised internal consumers where useful.

### Rule:

`IntentValidatedEvent` is a state/progress event, not a point-to-point command.

## IC MS lifecycle/status projection:

IC MS externally exposes lifecycle/status using:

```json
{
  "lifecycleStatus": "Acknowledged",
  "statusReason": "Intent request accepted for semantic validation and fulfilment.",
  "statusChangeDate": "2026-04-18T12:00:00+10:00"
}
```

### Lifecycle values:

```text
Acknowledged
InProgress
Active
Degraded
Paused
Rejected
Failed
Terminated
```

### Lifecycle ownership rule:

IC MS owns the external lifecycle/status projection, but not the runtime truth.

| **Lifecycle/status source** | **IC MS action** |
|---|---|
| IC MS syntactic validation succeeds | Project `Acknowledged` |
| II MS semantic/policy rejection | Project `Rejected` |
| IA MS apply success / active assurance | Project `Active` |
| IA MS degraded assurance | Project `Degraded` |
| IA MS paused/failed/terminated outcome | Project `Paused`, `Failed`, or `Terminated` |
| Delete/terminate request accepted | Project termination path according to final delete/terminate rules |

## Internal event interactions:

### Produces:

```text
IntentValidatedEvent
```

Meaning:

```text
The runtime Intent has passed IC MS syntactic validation and is admitted for downstream semantic validation, resolution, and fulfilment processing.
```

### Current primary consumer:

```text
II MS / intent-intelligence-ms
```

### Consumes:

```text
IntentRejectedEvent
IntentAssuranceEvent
```

### Does not consume by default:

```text
IntentCallbackEvent
```

`IntentCallbackEvent` is consumed by IA MS. IA MS maps callback/orchestrator state into assurance/lifecycle truth and emits `IntentAssuranceEvent`.

## External event family:

IC MS emits TMF-style external events for `Intent` and `IntentReport` projection changes.

### Intent events:

```text
IntentCreateEvent
IntentAttributeValueChangeEvent
IntentStatusChangeEvent
IntentDeleteEvent
```

### IntentReport events:

```text
IntentReportCreateEvent
IntentReportAttributeValueChangeEvent
IntentReportDeleteEvent
```

These events are external projection/resource events only.

They must not expose raw telemetry, raw optimiser decisions, raw `t7.knowledge plane` data, raw callback payloads, internal candidate scoring, internal Kafka event payloads, or full internal `IntentAssuranceEvent` body unless deliberately curated into `IntentReport`.

## IntentReport responsibility:

`IntentReport` is a read-only external report projection owned by IC MS.

It is based on assurance truth from IA MS, but it is not raw assurance telemetry.

IntentReport may contain curated information such as current lifecycle/status, status reason, assurance summary, current service/resource summary, evaluation summary, violation/degradation summary, last assurance update time, and references to the related `Intent`.

IntentReport should not expose implementation-only details unless they are explicitly approved for external reporting.

## TMF compliance and platform extension rule:

IC MS remains TMF-aligned at the external contract level, but controlled platform extensions are acceptable when documented, non-breaking, and semantically compatible with TMF.

Strict TMF-compatible update operation:

```http
PATCH /intentManagement/v5/intent/{id}
```

Accepted platform extension:

```http
PUT /intentManagement/v5/intent/{id}
```

Platform preference:

- `PUT` is preferred for deterministic full replacement where supported.
- `PATCH` is supported for TMF compatibility but not encouraged for ordinary edits.

## IC MS boundary statement:

**IC MS is the TMF-facing runtime intent controller. It owns external `Intent` and `IntentReport` resources, performs syntactic validation against active `IntentSpecification`, emits `IntentValidatedEvent` as an internal state/progress event, and projects external lifecycle/status from II MS rejection outcomes and IA MS assurance outcomes. IC MS does not perform semantic validation, policy validation, optimisation, network apply, runtime assurance, telemetry ingestion, or callback mediation.**
