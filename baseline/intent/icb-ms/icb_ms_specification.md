# ICB MS Specification


| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Version | v3.0 |
| Last updated | 2026-06-02 |
| Scope | Intent Callback MS REST and internal event specification |
| Source of truth after commit | GitHub `baseline/intent/icb-ms/icb_ms_specification.md` |

**Document authority:** This document owns ICB MS field-level request/response and internal event contracts. Operational guidance is owned by the solution brief; service boundary decisions are owned by the design brief.

## Table of contents:

- [1. Service identity:](#1-service-identity)
- [2. Boundary statement:](#2-boundary-statement)
- [3. API endpoints:](#3-api-endpoints)
- [4. Common headers:](#4-common-headers)
  - [4.1. Request headers:](#41-request-headers)
  - [4.2. Gateway-provided trusted context:](#42-gateway-provided-trusted-context)
- [5. Submit callback:](#5-submit-callback)
  - [5.1. Request:](#51-request)
  - [5.2. Success response:](#52-success-response)
- [6. Submit callback — apply failure example:](#6-submit-callback-apply-failure-example)
- [7. Submit callback — optimiser outcome example:](#7-submit-callback-optimiser-outcome-example)
- [8. Retrieve callback submission status:](#8-retrieve-callback-submission-status)
  - [8.1. Request:](#81-request)
  - [8.2. Fresh-read request:](#82-fresh-read-request)
  - [8.3. Success response:](#83-success-response)
  - [8.4. Submission status values:](#84-submission-status-values)
- [9. Internal Kafka publication:](#9-internal-kafka-publication)
- [10. IntentCallbackEvent publication:](#10-intentcallbackevent-publication)
  - [10.1. CloudEvents headers:](#101-cloudevents-headers)
  - [10.2. Event body — apply completed:](#102-event-body-apply-completed)
  - [10.3. Event body — apply failed:](#103-event-body-apply-failed)
- [11. OptimisationStatusChangeEvent publication:](#11-optimisationstatuschangeevent-publication)
  - [11.1. CloudEvents headers:](#111-cloudevents-headers)
  - [11.2. Event body — optimisation completed:](#112-event-body-optimisation-completed)
- [12. Event-specific rules:](#12-event-specific-rules)
- [13. Reference and correlation construction rules:](#13-reference-and-correlation-construction-rules)
- [14. Structural validation rules:](#14-structural-validation-rules)
  - [14.1. IntentCallbackEvent change-execution/apply callback profile:](#141-intentcallbackevent-change-executionapply-callback-profile)
  - [14.2. OptimisationStatusChangeEvent optimiser outcome callback profile:](#142-optimisationstatuschangeevent-optimiser-outcome-callback-profile)
- [15. Standard errors:](#15-standard-errors)
  - [15.1. Common errors:](#151-common-errors)
  - [15.2. Validation failure example:](#152-validation-failure-example)
  - [15.3. DB unavailable example:](#153-db-unavailable-example)
- [16. Persistence tables:](#16-persistence-tables)
- [17. Outbox relay rules:](#17-outbox-relay-rules)
- [18. Security rules:](#18-security-rules)
- [19. Observability rules:](#19-observability-rules)

## 1. Service identity:

| **Item** | **Baseline** |
|---|---|
| Full name | Intent Callback MS |
| Short name | ICB MS |
| Service name | `intent-callback-ms` |
| Domain | Intent Domain |
| Base path | `/intent-callback/v1` |
| Primary responsibility | Callback submission ingestion and raw callback event relay |
| Primary output events | `IntentCallbackEvent`, `OptimisationStatusChangeEvent` |
| Kafka topics | `t7.intent.management.events.callbacks` for `IntentCallbackEvent`; `t7.intent.management.events` for `OptimisationStatusChangeEvent` |

## 2. Boundary statement:

ICB MS owns callback submission ingestion only.

ICB MS performs technical authorisation, structural validation, idempotent durable persistence, and raw callback event publication for approved callback profiles. ICB MS does not interpret lifecycle, assurance, degradation, failure, termination, or optimisation meaning. IA MS owns change-execution callback state interpretation and emits lifecycle-driving `IntentAssuranceEvent` outcomes. II MS owns optimiser outcome correlation and selected-configuration packaging when ICB relays `OptimisationStatusChangeEvent`.

## 3. API endpoints:

| **Purpose** | **Method** | **Endpoint** |
|---|---:|---|
| Submit callback | `POST` | `/intent-callback/v1/submissions` |
| Retrieve callback submission status | `GET` | `/intent-callback/v1/submissions/{id}` |

The `POST` endpoint supports approved callback profiles, including change-execution/apply callback submissions and optimiser outcome callback submissions.

| **Callback profile** | **ICB output event** | **Kafka topic** | **Consumer** |
|---|---|---|---|
| Change-execution and apply callback | `IntentCallbackEvent` | `t7.intent.management.events.callbacks` | IA MS |
| Optimiser outcome callback | `OptimisationStatusChangeEvent` | `t7.intent.management.events` | II MS |

The `GET` endpoint is a callback-submission operational status endpoint. It does not expose internal IA assurance state and does not replace IC MS `Intent` or `IntentReport` resources.

## 4. Common headers:

### 4.1. Request headers:

```http
Content-Type: application/json
Accept: application/json
X-Correlation-ID: corr-callback-001
Idempotency-Key: cb-EXT-ORCH-001-INT-HOSP-2026-001-0001
```

### 4.2. Gateway-provided trusted context:

The exact header names may be platform-specific, but API Gateway must forward trusted caller identity/claims to ICB MS.

Indicative examples:

```http
X-Authenticated-Client-ID: external-orchestrator-001
X-Authenticated-Client-Name: External Network Orchestrator
X-Authenticated-Claims: 
```

ICB MS must not trust caller-supplied identity headers unless they are injected or signed by API Gateway according to platform security policy.

## 5. Submit callback:

### 5.1. Request:

```http
POST /intent-callback/v1/submissions
Content-Type: application/json
Accept: application/json
X-Correlation-ID: corr-callback-001
Idempotency-Key: cb-EXT-ORCH-001-INT-HOSP-2026-001-0001
```

```json
{
  "intentId": "INT-HOSP-2026-001",
  "callbackSource": "external-orchestrator-001",
  "callbackTimestamp": "2026-04-18T12:18:00+10:00",
  "sourceState": {
    "state": "APPLIED",
    "reason": "Network apply completed successfully."
  },
  "sourceReference": {
    "id": "orch-job-9001",
    "href": "https://orchestrator.example.com/jobs/orch-job-9001"
  },
  "details": {
    "message": "Network apply completed successfully.",
    "appliedResources": [
      {
        "resourceId": "SYD-PRI-01",
        "role": "primary"
      },
      {
        "resourceId": "SYD-SEC-01",
        "role": "secondary"
      }
    ]
  },
  "@type": "IntentCallbackEventRequest"
}
```

### 5.2. Success response:

ICB MS returns success only after callback submission and outbox event are durably committed.

```http
HTTP/1.1 202 Accepted
Location: /intent-callback/v1/submissions/cb-sub-0001
Content-Type: application/json
ETag: "callback-submission-cb-sub-0001-v1"
```

```json
{
  "id": "cb-sub-0001",
  "href": "/intent-callback/v1/submissions/cb-sub-0001",
  "status": "Accepted",
  "statusReason": "Callback submission accepted and queued for internal publication.",
  "intentId": "INT-HOSP-2026-001",
  "receivedAt": "2026-04-18T12:18:03+10:00",
  "@type": "IntentCallbackSubmissionStatus",
  "_links": {
    "self": {
      "href": "/intent-callback/v1/submissions/cb-sub-0001"
    }
  }
}
```

## 6. Submit callback — apply failure example:

```http
POST /intent-callback/v1/submissions
Content-Type: application/json
Accept: application/json
X-Correlation-ID: corr-callback-002
Idempotency-Key: cb-EXT-ORCH-001-INT-HOSP-2026-003-0001
```

```json
{
  "intentId": "INT-HOSP-2026-003",
  "callbackSource": "external-orchestrator-001",
  "callbackTimestamp": "2026-04-18T12:22:00+10:00",
  "sourceState": {
    "state": "APPLY_FAILED",
    "reason": "Network apply failed in change-execution layer."
  },
  "sourceReference": {
    "id": "orch-job-9003",
    "href": "https://orchestrator.example.com/jobs/orch-job-9003"
  },
  "details": {
    "message": "Network apply failed in change-execution layer.",
    "errorCode": "ORCH_APPLY_TIMEOUT"
  },
  "@type": "IntentCallbackEventRequest"
}
```

ICB MS does not convert this to `Failed`. IA MS maps the raw callback fact into lifecycle-driving assurance meaning.


## 7. Submit callback — optimiser outcome example:

```http
POST /intent-callback/v1/submissions
Content-Type: application/json
Accept: application/json
X-Correlation-ID: corr-intent-create-001
Idempotency-Key: cb-OPT-HSS-2026-001-0001
```

```json
{
  "eventType": "OptimisationStatusChangeEvent",
  "eventTime": "2026-04-18T12:03:30+10:00",
  "timeOccurred": "2026-04-18T12:03:30+10:00",
  "event": {
    "optimisation": {
      "id": "opt-hss-2026-001",
      "href": "/optimisation/opt-hss-2026-001",
      "previousLifecycleStatus": "PROCESSING",
      "newLifecycleStatus": "COMPLETED",
      "sourceContext": {
        "domain": "intent-management",
        "resource": {
          "id": "INT-HOSP-2026-001",
          "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
          "@type": "IntentRef",
          "@referredType": "Intent"
        },
        "correlationId": "corr-intent-create-001",
        "intentVersion": "v1"
      },
      "selectedConfiguration": {
        "orchestratorConfiguration": {
          "target": "t7-network-orchestrator",
          "profile": "hospital-surgical-slice-apply-v1",
          "resources": [
            {
              "resourceId": "SYD-PRI-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "accessTechnology": "fibre",
              "relationships": [
                {
                  "type": "pairedSecondary",
                  "resourceId": "SYD-SEC-01"
                }
              ]
            },
            {
              "resourceId": "SYD-SEC-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "accessTechnology": "5G",
              "relationships": [
                {
                  "type": "protects",
                  "resourceId": "SYD-PRI-01"
                }
              ]
            }
          ]
        },
        "observerConfiguration": {
          "target": "t7-observability-platform",
          "profile": "critical-gold-assurance-observation-v1",
          "resources": [
            {
              "resourceId": "SYD-PRI-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-PRI-02",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-SEC-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-SEC-02",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            }
          ]
        }
      }
    }
  },
  "@type": "OptimisationStatusChangeEventRequest"
}
```

ICB MS does not convert this to an optimisation lifecycle decision. II MS consumes the relayed `OptimisationStatusChangeEvent` and correlates it to the submitted `POST /optimisation` request.

## 8. Retrieve callback submission status:

### 8.1. Request:

```http
GET /intent-callback/v1/submissions/cb-sub-0001
Accept: application/json
```

### 8.2. Fresh-read request:

```http
GET /intent-callback/v1/submissions/cb-sub-0001
Accept: application/json
Cache-Control: no-cache
```

### 8.3. Success response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: "callback-submission-cb-sub-0001-v2"
Cache-Control: private, max-age=60
```

```json
{
  "id": "cb-sub-0001",
  "href": "/intent-callback/v1/submissions/cb-sub-0001",
  "status": "Published",
  "statusReason": "Callback submission was published to the internal callback topic.",
  "intentId": "INT-HOSP-2026-001",
  "receivedAt": "2026-04-18T12:18:03+10:00",
  "publishedAt": "2026-04-18T12:18:04+10:00",
  "@type": "IntentCallbackSubmissionStatus",
  "_links": {
    "self": {
      "href": "/intent-callback/v1/submissions/cb-sub-0001"
    }
  }
}
```

### 8.4. Submission status values:

| **Status** | **Meaning** |
|---|---|
| `Accepted` | Callback submission and outbox record were durably committed |
| `Duplicate` | Callback was identified as a duplicate of an already accepted submission |
| `Published` | Outbox relay published the callback event to Kafka |
| `PublishFailed` | Outbox relay attempted publication and failed; retry policy applies |
| `Rejected` | Submission was rejected before durable acceptance |

These statuses describe callback submission handling only. They are not external `Intent.lifecycleStatus` values.

## 9. Internal Kafka publication:

ICB MS publishes to Kafka through the outbox relay. The event type and topic are selected by the approved callback profile.

## 10. IntentCallbackEvent publication:

ICB MS publishes `IntentCallbackEvent` to:

```text
t7.intent.management.events.callbacks
```

### 10.1. CloudEvents headers:

```http
ce-specversion: 1.0
ce-type: IntentCallbackEvent
ce-source: intent-callback-ms
ce-id: evt-intent-callback-0001
ce-time: 2026-04-18T12:18:04+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 10.2. Event body — apply completed:

```json
{
  "body": {
    "callbackId": "cb-sub-0001",
    "intentId": "INT-HOSP-2026-001",
    "callbackSource": "external-orchestrator-001",
    "callbackTimestamp": "2026-04-18T12:18:00+10:00",
    "sourceState": {
      "state": "APPLIED",
      "reason": "Network apply completed successfully."
    },
    "sourceReference": {
      "id": "orch-job-9001",
      "href": "https://orchestrator.example.com/jobs/orch-job-9001"
    },
    "receivedAt": "2026-04-18T12:18:03+10:00",
    "details": {
      "message": "Network apply completed successfully.",
      "appliedResources": [
        {
          "resourceId": "SYD-PRI-01",
          "role": "primary"
        },
        {
          "resourceId": "SYD-SEC-01",
          "role": "secondary"
        }
      ]
    },
    "references": {
      "correlationId": "corr-callback-001",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-001"
      }
    }
  }
}
```

### 10.3. Event body — apply failed:

```json
{
  "body": {
    "callbackId": "cb-sub-0003",
    "intentId": "INT-HOSP-2026-003",
    "callbackSource": "external-orchestrator-001",
    "callbackTimestamp": "2026-04-18T12:22:00+10:00",
    "sourceState": {
      "state": "APPLY_FAILED",
      "reason": "Network apply failed in change-execution layer."
    },
    "sourceReference": {
      "id": "orch-job-9003",
      "href": "https://orchestrator.example.com/jobs/orch-job-9003"
    },
    "receivedAt": "2026-04-18T12:22:03+10:00",
    "details": {
      "message": "Network apply failed in change-execution layer.",
      "errorCode": "ORCH_APPLY_TIMEOUT"
    },
    "references": {
      "correlationId": "corr-callback-002",
      "intent": {
        "id": "INT-HOSP-2026-003",
        "href": "/intentManagement/v5/intent/INT-HOSP-2026-003"
      }
    }
  }
}
```


## 11. OptimisationStatusChangeEvent publication:

ICB MS publishes approved optimiser outcome callbacks to:

```text
t7.intent.management.events
```

OptimisationStatusChangeEvent is relayed using the approved optimiser event payload shape consumed by II MS. Unlike IntentCallbackEvent, it is not converted into an ICB-owned `body.callback` fact shape. ICB MS validates and relays the approved optimiser event structurally; II MS owns correlation and interpretation.


### 11.1. CloudEvents headers:

```http
ce-specversion: 1.0
ce-type: OptimisationStatusChangeEvent
ce-source: intent-callback-ms
ce-id: evt-optimisation-status-001
ce-time: 2026-04-18T12:03:30+10:00
ce-subject: INT-HOSP-2026-001
content-type: application/json
```

### 11.2. Event body — optimisation completed:

```json
{
  "eventType": "OptimisationStatusChangeEvent",
  "eventTime": "2026-04-18T12:03:30+10:00",
  "timeOccurred": "2026-04-18T12:03:30+10:00",
  "event": {
    "optimisation": {
      "id": "opt-hss-2026-001",
      "href": "/optimisation/opt-hss-2026-001",
      "previousLifecycleStatus": "PROCESSING",
      "newLifecycleStatus": "COMPLETED",
      "sourceContext": {
        "domain": "intent-management",
        "resource": {
          "id": "INT-HOSP-2026-001",
          "href": "/intentManagement/v5/intent/INT-HOSP-2026-001",
          "@type": "IntentRef",
          "@referredType": "Intent"
        },
        "correlationId": "corr-intent-create-001",
        "intentVersion": "v1"
      },
      "selectedConfiguration": {
        "orchestratorConfiguration": {
          "target": "t7-network-orchestrator",
          "profile": "hospital-surgical-slice-apply-v1",
          "resources": [
            {
              "resourceId": "SYD-PRI-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "accessTechnology": "fibre",
              "relationships": [
                {
                  "type": "pairedSecondary",
                  "resourceId": "SYD-SEC-01"
                }
              ]
            },
            {
              "resourceId": "SYD-SEC-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "accessTechnology": "5G",
              "relationships": [
                {
                  "type": "protects",
                  "resourceId": "SYD-PRI-01"
                }
              ]
            }
          ]
        },
        "observerConfiguration": {
          "target": "t7-observability-platform",
          "profile": "critical-gold-assurance-observation-v1",
          "resources": [
            {
              "resourceId": "SYD-PRI-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-PRI-02",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "primary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-SEC-01",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            },
            {
              "resourceId": "SYD-SEC-02",
              "resourceType": "deliveryResource",
              "resourceClass": "critical-gold",
              "roles": [
                "secondary"
              ],
              "metrics": [
                "latencyMs",
                "availabilityPercent",
                "jitterMs",
                "packetLossPercent"
              ]
            }
          ]
        }
      }
    }
  },
  "@type": "OptimisationStatusChangeEvent"
}
```

## 12. Event-specific rules:

- `IntentCallbackEvent` carries raw callback facts only.
- Do not include `lifecycleStatus` in `IntentCallbackEvent`.
- Do not include `assuranceStatus` in `IntentCallbackEvent`.
- Do not include `targets`, `constraints`, `preferences`, optimiser scoring, solver internals, or KP internals in `IntentCallbackEvent`.
- Approved `OptimisationStatusChangeEvent` payloads may include optimiser outcome and selected configuration fields required by II MS, but ICB MS must not interpret them.
- Do not use TMF expression wrappers inside internal callback events.
- IA MS owns mapping from `sourceState.state` to lifecycle-driving `IntentAssuranceEvent` outcomes.

## 13. Reference and correlation construction rules:

ICB MS must not trust caller-supplied platform `href` values. Where ICB MS creates safe platform references such as `body.references.intent.href`, it constructs them from configured platform route templates, for example `/intentManagement/v5/intent/{intentId}`.

`X-Correlation-ID` is copied into the internal relay contract where supplied. For `IntentCallbackEvent`, ICB MS stores it in `body.references.correlationId` and may also publish it as an internal Kafka/message header such as `x-correlation-id`. For `OptimisationStatusChangeEvent`, ICB MS preserves the approved optimiser event correlation fields, including `event.optimisation.sourceContext.correlationId`, and may also publish the same value as `x-correlation-id`. The payload correlation field remains the durable contract.

## 14. Structural validation rules:

Required request fields depend on the approved callback profile.

### 14.1. IntentCallbackEvent change-execution/apply callback profile:

| **Field** | **Rule** |
|---|---|
| `intentId` | Required, non-empty string |
| `callbackSource` | Required, non-empty string; gateway identity remains authoritative |
| `callbackTimestamp` | Required ISO-8601 date-time |
| `sourceState.state` | Required, non-empty string; interpreted by IA MS, not ICB MS |
| `@type` | Required, normally `IntentCallbackEventRequest` |
| `Idempotency-Key` | Strongly recommended for external retry safety; may be required by platform policy |

### 14.2. OptimisationStatusChangeEvent optimiser outcome callback profile:

| **Field** | **Rule** |
|---|---|
| `eventType` | Required; must be `OptimisationStatusChangeEvent` for the approved optimiser profile |
| `event.optimisation.id` | Required optimisation id |
| `event.optimisation.sourceContext.resource.id` | Required related runtime `intentId` |
| `event.optimisation.sourceContext.correlationId` | Required correlation id |
| `event.optimisation.sourceContext.intentVersion` | Required where runtime intent versioning is used |
| `event.optimisation.newLifecycleStatus` | Required optimiser lifecycle state |
| `event.optimisation.selectedConfiguration` | Required when `newLifecycleStatus` is `COMPLETED`; ICB MS validates structural presence only, and II MS determines whether the outcome drives service-ready packaging |
| `@type` | Required, normally `OptimisationStatusChangeEventRequest` |
| `Idempotency-Key` | Strongly recommended for external retry safety; may be required by platform policy |

ICB MS validates syntax and structure only. It does not validate service feasibility, lifecycle meaning, assurance meaning, selected-configuration meaning, or optimiser outcomes.

Do not use `callbackType` as an ICB contract field. Raw change-execution/apply callback meaning is carried by `sourceState.state` and interpreted by IA MS. Optimiser outcome meaning is carried by `OptimisationStatusChangeEvent` and interpreted by II MS.

## 15. Standard errors:

All ICB MS errors use the common cross-MS error body shape:

```json
{
  "code": "...",
  "reason": "...",
  "message": "...",
  "status": 400,
  "referenceError": "https://mycsp.com.au/errors/...",
  "@type": "Error"
}
```

### 15.1. Common errors:

| **HTTP** | **Code** | **Scenario** |
|---:|---|---|
| `400` | `BAD_REQUEST` | Invalid JSON or malformed request |
| `401` | `UNAUTHENTICATED` | Caller identity not authenticated by gateway |
| `403` | `FORBIDDEN` | Caller not authorised to submit callback |
| `409` | `DUPLICATE_CALLBACK` | Duplicate callback only when an integration-specific idempotency policy explicitly requires conflict-style duplicate signalling; default duplicate handling is idempotent `202 Accepted` where safe |
| `413` | `PAYLOAD_TOO_LARGE` | Callback payload exceeds configured size limit |
| `422` | `VALIDATION_FAILED` | Required callback fields are missing or structurally invalid |
| `503` | `SERVICE_UNAVAILABLE` | ICB MS persistence path is unavailable |
| `500` | `INTERNAL_ERROR` | Unexpected server error |

### 15.2. Validation failure example:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "code": "VALIDATION_FAILED",
  "reason": "CALLBACK_REQUEST_INVALID",
  "message": "Callback submission is missing required field sourceState.state.",
  "status": 422,
  "referenceError": "https://mycsp.com.au/errors/VALIDATION_FAILED",
  "@type": "Error"
}
```

### 15.3. DB unavailable example:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
Retry-After: 30
```

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "reason": "ICB_MS_DATABASE_UNAVAILABLE",
  "message": "Callback submission cannot be accepted because the persistence layer is unavailable.",
  "status": 503,
  "referenceError": "https://mycsp.com.au/errors/SERVICE_UNAVAILABLE",
  "@type": "Error"
}
```

## 16. Persistence tables:

| **Table** | **Purpose** |
|---|---|
| `callback_submission` | Accepted submission metadata, status, source, idempotency key, and timestamps |
| `callback_submission_payload` | Optional payload body store. Use when payload size, data classification, retention separation, or audit policy requires payload separation; otherwise the accepted payload may be stored inline in `callback_submission` or `callback_outbox` according to the implementation data model |
| `callback_idempotency` | Deduplication and retry-safety records |
| `callback_outbox` | Pending/published callback events for Kafka relay, including `IntentCallbackEvent` and `OptimisationStatusChangeEvent` |
| `callback_audit` | Audit of accepted/rejected/duplicate decisions |
| `shedlock` | Optional clustered relay coordination |

## 17. Outbox relay rules:

- Write callback submission and outbox record in one DB transaction.
- Return API success after DB/outbox commit succeeds.
- Publish to Kafka asynchronously through outbox relay.
- If Kafka is unavailable, retry publication later.
- If DB/outbox commit fails, return API failure because durable callback publication cannot be guaranteed.
- Outbox relay must be idempotent and safe to retry. The relay publishes `IntentCallbackEvent` to the callback topic and `OptimisationStatusChangeEvent` to the main internal event topic according to the outbox record event type.

## 18. Security rules:

- API Gateway authenticates external caller.
- ICB MS trusts only gateway-forwarded identity/claims according to platform policy.
- ICB MS authorises caller/source before accepting callback.
- Request body size limits must be enforced.
- Sensitive values, credentials, tokens, and raw internal stack traces must not be stored in events or returned in errors.
- Audit all accepted, rejected, and duplicate callback submissions.

## 19. Observability rules:

ICB MS emits structured logs, metrics, and traces for:

- callback request received
- validation failure
- authorisation failure
- duplicate callback detection
- outbox write success/failure
- outbox relay success/failure
- Kafka publish retry state

Recommended metrics:

```text
icb_ms_callback_submitted_count
icb_ms_callback_accepted_count
icb_ms_callback_rejected_count
icb_ms_callback_duplicate_count
icb_ms_callback_outbox_pending_count
icb_ms_callback_outbox_publish_failure_count
icb_ms_callback_db_error_count
icb_ms_callback_validation_error_count
```
