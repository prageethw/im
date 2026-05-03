add things here.

# Intent Management Context Dump

This file is a running baseline/context dump for rebuilding the conversation quickly in a new thread.
It is intended to preserve agreed baselines, including concrete JSON payloads and interface direction.

---

## Working agreement

- Give an early warning if the conversation is getting close to context limits.
- Maintain a running context/baseline dump file quietly and only show/dump it when explicitly asked.

---

## Reference anchors

### 1) TMF921
Used as the external standards validation reference for the Intent Management API surface.

### 2) REST in Practice
Used as the web architecture / REST / resource / URI / representation / hypermedia reference.

### 3) Building Event-Driven Microservices
Used as the internal event-driven architecture / bounded context / event stream / orchestration / eventual consistency reference.

---

## Cross-platform baselines first

### Shared internal terminology
Use these common internal names wherever possible:
- `location.locationId`
- `service.serviceClass`
- `current.resources`
- `candidates`
- `request`
- `inputs`

Shared reusable resource-entry shape:
- `roles`
- `resourceId`
- `resourceType`
- `resourceClass`
- `resourceAttributes`
- `relationships`
- `metrics`

Keep milestone-specific sections explicit only where they carry real business meaning, such as:
- `resolvedIntent`
- `hardConstraints`
- `optimisationObjectives`
- `preferences`
- `evaluations`
- `statusReason`
- `lifecycleStatus`
- `references`

### Documentation style
Implementation-facing examples should:
- keep the actual JSON clean
- use comment/note lines outside JSON for allowed enum/status values and field semantics

### Lifecycle states
Baselined lifecycle set:
- `Acknowledged`
- `InProgress`
- `Active`
- `Degraded`
- `Paused`
- `Rejected`
- `Failed`
- `Terminated`

Meaning:
- `Acknowledged` = syntactic validation succeeded and request admitted
- `InProgress` = semantic / optimisation / apply workflow underway
- `Active` = network has confirmed the policy is active
- `Degraded` = active but not meeting expected service outcome
- `Paused` = network state; policy exists but is intentionally paused
- `Rejected` = can originate pre-orchestration or post-orchestration
- `Failed` = network state; delivery/operation failed irrecoverably
- `Terminated` = network state; ended/removed

### Versioning / effectiveVersion
- each Intent version has its own lifecycle
- once a version becomes `Active`, it becomes the `effectiveVersion`
- it remains the `effectiveVersion` even if it later becomes `Degraded`, `Paused`, or `Failed`
- `effectiveVersion` changes only when another version is confirmed `Active`
- a previously terminated version does not automatically become active again after a newer version fails
- restoring prior behaviour requires a new orchestration/apply cycle, typically as a new version
- keep all versions together in the same logical store family, not moved out to a separate “old versions” table/collection by default

---

## MS ownership

### ID MS
- owns `IntentSpecification`
- owns `/intentManagement/v5/intentSpecification`
- owns `/intentManagement/v5/intentSpecification/hub`
- owns external `IntentSpecification...Event` family

### IC MS
- owns external `Intent` domain
- owns external `IntentReport` curated projection domain
- owns `/intentManagement/v5/intent`
- owns `/intentManagement/v5/intent/hub`
- owns nested `IntentReport` routes
- owns external TMF lifecycle projection events

### II MS
- semantic/policy interpretation layer
- consumes `IntentValidatedEvent` from IC MS
- consumes `IntentDriftOccurredEvent` from IA MS
- consumes `IntentOptimisedEvent` from optimiser
- emits `IntentResolvedEvent`
- emits `IntentRejectedEvent`
- emits `IntentNetworkReadyEvent` when appropriate
- uses its own internal knowledge plane

### IA MS
- owns runtime assurance truth
- emits internal assurance outcome

---

## Internal event names baselined

- `IntentValidatedEvent` (IC MS → II MS)
- `IntentRejectedEvent` (II MS → IC MS)
- `IntentResolvedEvent` (II MS → optimiser)
- `IntentOptimisedEvent` (optimiser → II MS)
- `IntentNetworkReadyEvent` (II MS → IA MS)
- `IntentAssuranceEvent` (IA MS → IC MS / II MS as needed)
- `IntentDriftOccurredEvent` retained only if needed; otherwise drift handled via assurance (`current` + `candidates`)

---

## Internal event wrapper style (latest recovered JSON pattern)

```json
{
  "topic": "t7.intent.management.events",
  "key": "<intent-id>",
  "headers": {
    "content-type": "application/json",
    "ce_specversion": "1.0",
    "ce_type": "<EventName>",
    "ce_source": "<ms-name>",
    "ce_id": "<event-id>",
    "ce_time": "<timestamp>",
    "ce_subject": "<intent-id>",
    "ce_datacontenttype": "application/json",
    "ce_correlationid": "<correlation-id>"
  },
  "body": {
    "...": "event-specific business payload"
  }
}
```

Common rules:
- topic: `t7.intent.management.events`
- CloudEvents metadata in `headers`
- business payload in `body`
- clean JSON examples
- `references` at tail of `body` where applicable

---

## Internal event JSONs (latest recovered examples)

### IntentValidatedEvent

```json
{
  "topic": "t7.intent.management.events",
  "key": "INT-HOSP-2026-001",
  "headers": {
    "content-type": "application/json",
    "ce_specversion": "1.0",
    "ce_type": "IntentValidatedEvent",
    "ce_source": "intent-controller-ms",
    "ce_id": "EVT-INT-HOSP-2026-001-VAL-0001",
    "ce_time": "2026-04-17T10:00:05+10:00",
    "ce_subject": "INT-HOSP-2026-001",
    "ce_datacontenttype": "application/json",
    "ce_correlationid": "INT-HOSP-2026-001-INIT"
  },
  "body": {
    "eventType": "IntentValidatedEvent",
    "eventVersion": "1.0",
    "source": "intent-controller-ms",
    "eventTime": "2026-04-17T10:00:05+10:00",
    "correlationId": "INT-HOSP-2026-001-INIT",
    "status": "VALIDATED",
    "request": {
      "id": "INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "humanExpression": "I need a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "@type": "Intent",
      "@baseType": "Entity",
      "isBundle": false,
      "validFor": {
        "startDateTime": "2026-04-17T10:00:00+10:00",
        "endDateTime": "2027-04-17T10:00:00+10:00"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "name": "Hospital-Surgical-Slice-Spec",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification",
        "@href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "characteristic": [
        {
          "@type": "Characteristic",
          "name": "slice_type",
          "value": "URLLC"
        },
        {
          "@type": "Characteristic",
          "name": "latency",
          "value": 10
        },
        {
          "@type": "Characteristic",
          "name": "availability",
          "value": 99.99
        },
        {
          "@type": "Characteristic",
          "name": "priority",
          "value": "CRITICAL"
        },
        {
          "@type": "Characteristic",
          "name": "semantic_tag",
          "value": "medical_urllc_critical"
        },
        {
          "@type": "Characteristic",
          "name": "geo_location",
          "value": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "HOSPITAL",
            "geographicScope": "AU-NSW-SYD"
          }
        }
      ]
    },
    "inputs": {
      "validationScope": "SPEC_SYNTAX",
      "validationTimestamp": "2026-04-17T10:00:05+10:00",
      "validatedAgainst": {
        "intentSpecificationId": "hospital-surgical-slice-spec-v1.19",
        "intentSpecificationHref": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "version": "1.19"
      },
      "checkedElements": [
        "name",
        "@type",
        "expression.@type",
        "expression.iri",
        "expression.expressionValue",
        "characteristic[slice_type]",
        "characteristic[latency]",
        "characteristic[availability]",
        "characteristic[priority]",
        "characteristic[semantic_tag]",
        "characteristic[geo_location]"
      ],
      "checkedCharacteristics": [
        "slice_type",
        "latency",
        "availability",
        "geo_location",
        "priority",
        "semantic_tag"
      ],
      "message": "Intent payload is structurally valid against the active IntentSpecification."
    },
    "references": {
      "intent": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

### IntentRejectedEvent

Allowed `reasonCode` values:
- Semantic: `SEMANTIC_LOCATION_UNSUPPORTED`, `SEMANTIC_LOCATION_TYPE_UNSUPPORTED`, `SEMANTIC_SERVICE_CLASS_UNSUPPORTED`, `SEMANTIC_INTENT_CONTRADICTORY`, `SEMANTIC_REQUIRED_CONTEXT_MISSING`, `SEMANTIC_EXPRESSION_UNSUPPORTED`
- Policy: `POLICY_LOCATION_NOT_ALLOWED`, `POLICY_SERVICE_CLASS_NOT_ALLOWED`, `POLICY_PRIORITY_NOT_ALLOWED`, `POLICY_TIME_WINDOW_NOT_ALLOWED`, `POLICY_REQUEST_NOT_AUTHORISED`
- Optimisation: `OPTIMISATION_NOT_OPTIMISABLE`, `OPTIMISATION_NO_VALID_CANDIDATES`, `OPTIMISATION_DISJOINTNESS_UNSATISFIABLE`, `OPTIMISATION_LATENCY_UNSATISFIABLE`, `OPTIMISATION_RELIABILITY_UNSATISFIABLE`
- Processing: `PROCESSING_ERROR`, `KNOWLEDGE_LOOKUP_ERROR`, `OPTIMISER_ERROR`

```json
{
  "topic": "t7.intent.management.events",
  "key": "INT-HOSP-2026-001",
  "headers": {
    "content-type": "application/json",
    "ce_specversion": "1.0",
    "ce_type": "IntentRejectedEvent",
    "ce_source": "intent-intelligence-ms",
    "ce_id": "EVT-INT-HOSP-2026-001-REJ-0001",
    "ce_time": "2026-04-17T10:00:15+10:00",
    "ce_subject": "INT-HOSP-2026-001",
    "ce_datacontenttype": "application/json",
    "ce_correlationid": "INT-HOSP-2026-001-INIT"
  },
  "body": {
    "eventType": "IntentRejectedEvent",
    "eventVersion": "1.0",
    "source": "intent-intelligence-ms",
    "eventTime": "2026-04-17T10:00:15+10:00",
    "correlationId": "INT-HOSP-2026-001-INIT",
    "intentId": "INT-HOSP-2026-001",
    "lifecycleStatus": "Rejected",
    "reasonCode": "SEMANTIC_LOCATION_UNSUPPORTED",
    "statusReason": "The requested location is not supported for the specified intent class.",
    "evaluations": [
      {
        "name": "locationSupport",
        "result": "failed"
      },
      {
        "name": "policyCompatibility",
        "result": "notEvaluated"
      }
    ],
    "references": {
      "intent": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

### IntentResolvedEvent

```json
{
  "topic": "t7.intent.management.events",
  "key": "INT-HOSP-2026-001",
  "headers": {
    "content-type": "application/json",
    "ce_specversion": "1.0",
    "ce_type": "IntentResolvedEvent",
    "ce_source": "intent-intelligence-ms",
    "ce_id": "EVT-INT-HOSP-2026-001-RES-0001",
    "ce_time": "2026-04-17T10:00:20+10:00",
    "ce_subject": "INT-HOSP-2026-001",
    "ce_datacontenttype": "application/json",
    "ce_correlationid": "INT-HOSP-2026-001-INIT"
  },
  "body": {
    "eventType": "IntentResolvedEvent",
    "eventVersion": "1.0",
    "source": "intent-intelligence-ms",
    "eventTime": "2026-04-17T10:00:20+10:00",
    "correlationId": "INT-HOSP-2026-001-INIT",
    "intentId": "INT-HOSP-2026-001",
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001"
    },
    "service": {
      "serviceClass": "critical-gold",
      "intentName": "Sydney Hospital Surgical Connection Intent"
    },
    "resolvedIntent": {
      "targetOutcome": "Provide a surgical connection for Sydney Hospital",
      "hardConstraints": {
        "maximumLatencyMs": 10,
        "minimumAvailabilityPercent": 99.99,
        "requireDisjointPrimaryAndSecondary": true
      },
      "optimisationObjectives": [
        {
          "name": "minimiseLatency",
          "priority": 1
        },
        {
          "name": "maximiseAvailability",
          "priority": 2
        }
      ],
      "preferences": {
        "priority": "CRITICAL",
        "semanticTag": "medical_urllc_critical"
      }
    },
    "candidates": [
      {
        "roles": ["primary"],
        "resourceId": "PATH-SYD-HOSP-001-A",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [
          {
            "type": "disjointFrom",
            "targetResourceId": "PATH-SYD-HOSP-001-B"
          }
        ],
        "metrics": [
          {
            "name": "latencyBenchmarkMs",
            "value": 8
          },
          {
            "name": "reliabilityBenchmarkPercent",
            "value": 99.999
          }
        ]
      },
      {
        "roles": ["primary"],
        "resourceId": "PATH-SYD-HOSP-001-D",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [
          {
            "type": "disjointFrom",
            "targetResourceId": "PATH-SYD-HOSP-001-B"
          }
        ],
        "metrics": [
          {
            "name": "latencyBenchmarkMs",
            "value": 9
          },
          {
            "name": "reliabilityBenchmarkPercent",
            "value": 99.998
          }
        ]
      },
      {
        "roles": ["secondary"],
        "resourceId": "PATH-SYD-HOSP-001-B",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [
          {
            "type": "disjointFrom",
            "targetResourceId": "PATH-SYD-HOSP-001-A"
          },
          {
            "type": "disjointFrom",
            "targetResourceId": "PATH-SYD-HOSP-001-D"
          }
        ],
        "metrics": [
          {
            "name": "latencyBenchmarkMs",
            "value": 9
          },
          {
            "name": "reliabilityBenchmarkPercent",
            "value": 99.995
          }
        ]
      },
      {
        "roles": ["secondary"],
        "resourceId": "PATH-SYD-HOSP-001-C",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-silver",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [],
        "metrics": [
          {
            "name": "latencyBenchmarkMs",
            "value": 11
          },
          {
            "name": "reliabilityBenchmarkPercent",
            "value": 99.97
          }
        ]
      }
    ],
    "references": {
      "intent": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

### IntentOptimisedEvent

Allowed `optimisationOutcome.status` values:
- `Optimised`
- `NotOptimisable`
- `Error`

```json
{
  "topic": "t7.intent.management.events",
  "key": "INT-HOSP-2026-001",
  "headers": {
    "content-type": "application/json",
    "ce_specversion": "1.0",
    "ce_type": "IntentOptimisedEvent",
    "ce_source": "intent-optimiser-ms",
    "ce_id": "EVT-INT-HOSP-2026-001-OPT-0001",
    "ce_time": "2026-04-17T10:00:35+10:00",
    "ce_subject": "INT-HOSP-2026-001",
    "ce_datacontenttype": "application/json",
    "ce_correlationid": "INT-HOSP-2026-001-INIT"
  },
  "body": {
    "eventType": "IntentOptimisedEvent",
    "eventVersion": "1.0",
    "source": "intent-optimiser-ms",
    "eventTime": "2026-04-17T10:00:35+10:00",
    "correlationId": "INT-HOSP-2026-001-INIT",
    "intentId": "INT-HOSP-2026-001",
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001"
    },
    "service": {
      "serviceClass": "critical-gold"
    },
    "resources": [
      {
        "roles": ["primary"],
        "resourceId": "PATH-SYD-HOSP-001-A",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [
          {
            "type": "disjointFrom",
            "targetResourceId": "PATH-SYD-HOSP-001-B"
          }
        ],
        "metrics": [
          {
            "name": "latencyBenchmarkMs",
            "value": 8
          },
          {
            "name": "reliabilityBenchmarkPercent",
            "value": 99.999
          }
        ]
      },
      {
        "roles": ["secondary"],
        "resourceId": "PATH-SYD-HOSP-001-B",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [
          {
            "type": "disjointFrom",
            "targetResourceId": "PATH-SYD-HOSP-001-A"
          }
        ],
        "metrics": [
          {
            "name": "latencyBenchmarkMs",
            "value": 9
          },
          {
            "name": "reliabilityBenchmarkPercent",
            "value": 99.995
          }
        ]
      }
    ],
    "optimisationOutcome": {
      "status": "Optimised",
      "statusReason": "Selected the best valid primary and secondary resource combination that satisfies constraints and objectives."
    },
    "evaluations": [
      {
        "name": "latencyObjective",
        "result": "passed"
      },
      {
        "name": "availabilityObjective",
        "result": "passed"
      },
      {
        "name": "disjointnessConstraint",
        "result": "passed"
      }
    ],
    "references": {
      "intent": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

### IntentAssuranceEvent

```json
{
  "topic": "t7.intent.management.events",
  "key": "INT-HOSP-2026-001",
  "headers": {
    "content-type": "application/json",
    "ce_specversion": "1.0",
    "ce_type": "IntentAssuranceEvent",
    "ce_source": "intent-assurance-ms",
    "ce_id": "EVT-INT-HOSP-2026-001-ASR-0001",
    "ce_time": "2026-04-18T12:10:00+10:00",
    "ce_subject": "INT-HOSP-2026-001",
    "ce_datacontenttype": "application/json",
    "ce_correlationid": "INT-HOSP-2026-001-INIT"
  },
  "body": {
    "eventType": "IntentAssuranceEvent",
    "eventVersion": "1.0",
    "source": "intent-assurance-ms",
    "eventTime": "2026-04-18T12:10:00+10:00",
    "correlationId": "INT-HOSP-2026-001-INIT",
    "intentId": "INT-HOSP-2026-001",
    "lifecycleStatus": "Degraded",
    "statusChangeDate": "2026-04-18T12:10:00+10:00",
    "statusReason": "Observed service quality no longer satisfies the expected operating target.",
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001"
    },
    "current": {
      "serviceClass": "critical-gold",
      "evaluations": [
        {
          "name": "latencyCompliance",
          "result": "failed"
        },
        {
          "name": "availabilityCompliance",
          "result": "passed"
        }
      ],
      "resources": [
        {
          "roles": ["primary"],
          "resourceId": "PATH-SYD-HOSP-001-A",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          },
          "relationships": [
            {
              "type": "disjointFrom",
              "targetResourceId": "PATH-SYD-HOSP-001-B"
            }
          ],
          "metrics": [
            {
              "name": "latencyMs",
              "value": 12
            },
            {
              "name": "reliabilityPercent",
              "value": 99.992
            }
          ]
        },
        {
          "roles": ["secondary"],
          "resourceId": "PATH-SYD-HOSP-001-B",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          },
          "relationships": [
            {
              "type": "disjointFrom",
              "targetResourceId": "PATH-SYD-HOSP-001-A"
            }
          ],
          "metrics": [
            {
              "name": "latencyMs",
              "value": 9
            },
            {
              "name": "reliabilityPercent",
              "value": 99.995
            }
          ]
        }
      ]
    },
    "candidates": [
      {
        "roles": ["primary"],
        "resourceId": "PATH-SYD-HOSP-001-D",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [
          {
            "type": "disjointFrom",
            "targetResourceId": "PATH-SYD-HOSP-001-B"
          }
        ],
        "metrics": [
          {
            "name": "latencyMs",
            "value": 11
          },
          {
            "name": "reliabilityPercent",
            "value": 99.998
          }
        ]
      },
      {
        "roles": ["secondary"],
        "resourceId": "PATH-SYD-HOSP-001-C",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-silver",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [],
        "metrics": [
          {
            "name": "latencyMs",
            "value": 10
          },
          {
            "name": "reliabilityPercent",
            "value": 99.997
          }
        ]
      }
    ],
    "references": {
      "intent": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

---

## Shared platform baselines for externally facing MSs

### REST transport and error model
- `ETag` is mandatory on all resource responses (create, retrieve, list, full update, partial update)
- `If-Match` is required on `PUT`, `PATCH`, `DELETE` for existing versioned resources
- stale or mismatched `ETag` → `412 Precondition Failed`

Standard error body:

```json
{ "code": "...", "reason": "...", "message": "...", "status": 412, "referenceError": "...", "@type": "Error" }
```

### Caching
- `GET` responses are cached by default with private caching
- clients can bypass cache using `Cache-Control: no-cache`

### Circuit breaker response pattern
- breaker with no safe fallback → `503 Service Unavailable`
- breaker with safe degraded fallback preserving meaning → `200 OK` with a valid degraded representation and degradation signalled in body and/or warning/header

### External event delivery policy
- delivery model: at-least-once
- include stable `eventId` (or equivalent); consumers must be idempotent
- listener success acknowledgement: `204 No Content`
- retry on timeout/network failure/5xx with bounded retries and exponential backoff; exhausted retries are operational failure

---

## ID MS baselines

### Responsibility
ID MS owns `IntentSpecification`.

### External interfaces baselined
- `POST /intentManagement/v5/intentSpecification`
- `GET /intentManagement/v5/intentSpecification/{id}`
- `GET /intentManagement/v5/intentSpecification`
- `PUT /intentManagement/v5/intentSpecification/{id}` — platform-specific full update
- `PATCH /intentManagement/v5/intentSpecification/{id}` — supported but discouraged
- `DELETE /intentManagement/v5/intentSpecification/{id}`

### Subscription endpoints baselined
- `POST /intentManagement/v5/intentSpecification/hub`
- `DELETE /intentManagement/v5/intentSpecification/hub/{id}`
- `GET /intentManagement/v5/intentSpecification/hub/{id}`

### Lifecycle/versioning/governance baselined
- lifecycle states:
  - `DRAFT`
  - `ACTIVE`
  - `RETIRED`
- only `DRAFT` is editable
- `ACTIVE` is not mutable/deletable
- new active versions must start as new `DRAFT` resources

### External event family baselined
- `IntentSpecificationCreateEvent`
- `IntentSpecificationAttributeValueChangeEvent`
- `IntentSpecificationStatusChangeEvent`
- `IntentSpecificationDeleteEvent`

### Reusable-vs-specific checklist baselined
Reuse:
- error model
- `ETag` / `If-Match`
- `412`
- private caching
- list behavior: `offset`, `limit`, top-level array, `X-Total-Count`, `X-Result-Count`
- subscription scaffolding: `id`, `href`, `callback`, `query`, `@type: EventSubscription`
- HATEOAS link conventions
- TMF-style external event envelope

Keep explicit:
- `IntentSpecification`
- `expressionSpecification`
- characteristic definitions
- lifecycle/versioning/governance semantics
- the `IntentSpecification...Event` family
- `/intentSpecification/hub` ownership pattern

### Location naming direction
Where the platform controls the content, prefer:
- `locationId`
- `locationType`
- `geographicScope`

preserving TMF/resource-specific names only where standard-driven.

### Hub request bodies baselined

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationCreateEvent",
  "query": "eventType=IntentSpecificationCreateEvent"
}
```

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationAttributeValueChangeEvent",
  "query": "eventType=IntentSpecificationAttributeValueChangeEvent"
}
```

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationStatusChangeEvent",
  "query": "eventType=IntentSpecificationStatusChangeEvent"
}
```

```json
{
  "callback": "https://consumer.example.com/listener/intentSpecificationDeleteEvent",
  "query": "eventType=IntentSpecificationDeleteEvent"
}
```

### Retrieve subscription by id baseline
- `200 OK`
- `Content-Location`
- mandatory `ETag`
- private caching by default
- returned body includes `callback`, `query`, `@type`, `_links`
- matching `404 Not Found` example uses the standard error body

---

## IC MS baselines

### Responsibility
IC MS owns the external Intent domain and related external IntentReport projection.

### `/intent` interfaces baselined
- `POST /intentManagement/v5/intent`
- `GET /intentManagement/v5/intent`
- `GET /intentManagement/v5/intent/{id}`
- `PUT /intentManagement/v5/intent/{id}` — platform extension
- `PATCH /intentManagement/v5/intent/{id}` — supported but strongly discouraged
- `DELETE /intentManagement/v5/intent/{id}`

### `/intent/hub` baselined
- `POST /intentManagement/v5/intent/hub`
- `DELETE /intentManagement/v5/intent/hub/{id}`

Literal subscription style:
- one subscription per event type
- one callback URL per subscription

This same hub is used for both:
- `Intent...Event`
- `IntentReport...Event`

### `IntentReport` interfaces baselined
- `GET /intentManagement/v5/intent/{intentId}/intentReport`
- `GET /intentManagement/v5/intent/{intentId}/intentReport/{id}`

IntentReport is:
- IC-MS-owned
- external
- curated reporting/projection
- not raw runtime telemetry

### External `Intent` event family baselined
- `IntentCreateEvent`
- `IntentAttributeValueChangeEvent`
- `IntentStatusChangeEvent`
- `IntentDeleteEvent`

All are:
- TMF-aligned
- delivered via `/intent/hub`
- design-time only
- use `intent-controller-ms` in `reportingSystem.name` and `source.name`

### External `IntentReport` event family baselined
- `IntentReportCreateEvent`
- `IntentReportAttributeValueChangeEvent`
- `IntentReportDeleteEvent`

All are:
- TMF-aligned
- delivered via `/intent/hub`
- curated external projection/design-time reporting events
- use `intent-controller-ms` in `reportingSystem.name` and `source.name`

### Reusable-vs-specific checklist baselined
Reuse:
- transport/API conventions
- error model
- `ETag` / `If-Match`
- list behavior
- subscription scaffolding
- HATEOAS link conventions
- TMF-style external event envelope
- common internal event envelope
- reusable internal resource-entry shape

Keep explicit:
- `Intent`
- `IntentReport`
- `Intent...Event`
- `IntentReport...Event`
- `/intent`, `/intent/hub`, nested IntentReport routes
- external `/intentSpecification` validation semantics
- design-time interpretation rule for external IC MS events

---

## Current Master Knowledge Config naming direction

Draft direction baselined:
- top-level grouping uses `locations` rather than `sites`
- human-level expression mapping uses `location` rather than `geo_location`
- resolved structured location data uses:
  - `locationId`
  - `locationType`
  - `geographicScope`

Open working note:
- in external IntentSpecification / external request content, `geo_location` may still remain where that external contract is already baselined
- in human-level mapping and platform-controlled master config naming, prefer `location`

Additional draft direction:
- `constraints.priority` not `priority_level`
- `constraints.serviceClass` not `trafficClass`
- path benchmarks prefer machine-friendly numeric naming:
  - `latencyBenchmarkMs`
  - `reliabilityBenchmarkPercent`

---

## Notes for continuation

Natural starting stack when restarting from zero:
- external standard reference → TMF921
- web architecture reference → REST in Practice
- internal event-driven architecture reference → Building Event-Driven Microservices

Then walk in this order:
1. cross-platform foundations
2. MS ownership
3. lifecycle + versioning
4. ID MS external contracts
5. IC MS external contracts
6. internal event flow
7. master knowledge config

## ID MS interface baseline — POST /intentManagement/v5/intentSpecification

### Summary
Creates a new `IntentSpecification` resource in ID MS. This is the baselined create operation for the syntax-first surgical hospital slice specification example. It returns `201 Created`, includes mandatory `Location` and `ETag` headers, and returns the full created resource representation with `_links`. The example baseline uses `hospital-surgical-slice-spec-v1.19`.

### Request headers
```http
POST /intentManagement/v5/intentSpecification HTTP/1.1
Host: mycsp.com.au
Content-Type: application/json
Accept: application/json
Accept-Language: en-AU
```

### Request body
```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "name": "Hospital-Surgical-Slice-Spec",
  "description": "Syntax-first IntentSpecification for hospital surgical slice requests. Defines allowed intent content and structural constraints only. Intended business semantics for surgical URLLC use cases are described for guidance and are enforced outside this specification by II MS / knowledge-plane validation. This version acts as the base specification extended by v1.20.",
  "version": "1.19",
  "lifecycleStatus": "ACTIVE",
  "isBundle": false,
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/tmf-api/schema/Common/IntentSpecification.schema.json",
  "validFor": {
    "startDateTime": "2026-04-17T10:00:00+10:00"
  },
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
  },
  "specCharacteristic": [
    {
      "id": "SC-DELIVERY-001",
      "name": "slice_type",
      "description": "Declares the requested slice class. For hospital surgical scenarios, the intended usage is URLLC. This specification constrains the structural value only. Scenario suitability and business-policy enforcement are performed outside this specification by II MS / knowledge-plane validation.",
      "valueType": "string",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": false,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "isDefault": true,
          "value": "URLLC"
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-001",
      "name": "latency",
      "description": "Maximum target latency requested for the slice. For surgical URLLC scenarios, expected usage is low-latency operation, commonly around 10 ms or below. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",
      "valueType": "integer",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "integer",
          "unitOfMeasure": "ms",
          "valueFrom": 0,
          "valueTo": 20,
          "rangeInterval": "closed",
          "isDefault": true,
          "value": 10
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-002",
      "name": "availability",
      "description": "Requested availability target for the slice. For surgical URLLC scenarios, expected usage is very high availability, commonly 99.999 percent. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",
      "valueType": "number",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "number",
          "unitOfMeasure": "percent",
          "valueFrom": 0,
          "valueTo": 100,
          "rangeInterval": "closed",
          "isDefault": true,
          "value": 99.999
        }
      ]
    },
    {
      "id": "SC-CONTEXT-001",
      "name": "geo_location",
      "description": "Resolvable site reference identifying the target hospital or operating location. This specification defines the required object structure only. Site resolution, geographic interpretation, and domain-specific validation are performed outside this specification by II MS / knowledge-plane validation.",
      "valueType": "object",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "object",
          "semanticType": "tio:GeographicSiteRef",
          "referenceModel": "TMF673-Site",
          "requiredFields": [
            "locationId",
            "locationType",
            "geographicScope"
          ],
          "description": "CSP-independent resolvable location reference. Structural shape is enforced here; semantic resolution is performed externally."
        }
      ]
    },
    {
      "id": "SC-CONTEXT-002",
      "name": "priority",
      "description": "Priority classification for the requested slice intent. For surgical use cases, higher priority values are typically expected. This specification constrains the allowed enumeration only. Operational meaning and policy impact are determined outside this specification by II MS / knowledge-plane validation.",
      "valueType": "string",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "value": "CRITICAL",
          "isDefault": false
        },
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "value": "HIGH",
          "isDefault": false
        },
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "value": "NORMAL",
          "isDefault": true
        }
      ]
    },
    {
      "id": "SC-CONTEXT-003",
      "name": "semantic_tag",
      "description": "Semantic classification tag associated with the requested slice intent. This specification constrains the structural value only. The meaning of the tag and any semantic-policy consequences are validated outside this specification by II MS / knowledge-plane validation.",
      "valueType": "string",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "value": "medical_urllc_critical",
          "isDefault": true
        }
      ]
    }
  ]
}
```

### Response headers
```http
HTTP/1.1 201 Created
Content-Type: application/json
Content-Language: en-AU
Location: https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19
ETag: W/"hospital-surgical-slice-spec-v1.19-1.19"
Last-Modified: Fri, 17 Apr 2026 00:00:00 GMT
Cache-Control: private, max-age=300
```

### Response body
```json
{
  "id": "hospital-surgical-slice-spec-v1.19",
  "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
  "name": "Hospital-Surgical-Slice-Spec",
  "description": "Syntax-first IntentSpecification for hospital surgical slice requests. Defines allowed intent content and structural constraints only. Intended business semantics for surgical URLLC use cases are described for guidance and are enforced outside this specification by II MS / knowledge-plane validation. This version acts as the base specification extended by v1.20.",
  "version": "1.19",
  "lifecycleStatus": "ACTIVE",
  "isBundle": false,
  "@type": "IntentSpecification",
  "@baseType": "EntitySpecification",
  "@schemaLocation": "https://mycsp.com.au/tmf-api/schema/Common/IntentSpecification.schema.json",
  "validFor": {
    "startDateTime": "2026-04-17T10:00:00+10:00"
  },
  "expressionSpecification": {
    "@type": "ExpressionSpecification",
    "expressionLanguage": "JSON-LD",
    "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
  },
  "specCharacteristic": [
    {
      "id": "SC-DELIVERY-001",
      "name": "slice_type",
      "description": "Declares the requested slice class. For hospital surgical scenarios, the intended usage is URLLC. This specification constrains the structural value only. Scenario suitability and business-policy enforcement are performed outside this specification by II MS / knowledge-plane validation.",
      "valueType": "string",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": false,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "isDefault": true,
          "value": "URLLC"
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-001",
      "name": "latency",
      "description": "Maximum target latency requested for the slice. For surgical URLLC scenarios, expected usage is low-latency operation, commonly around 10 ms or below. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",
      "valueType": "integer",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "integer",
          "unitOfMeasure": "ms",
          "valueFrom": 0,
          "valueTo": 20,
          "rangeInterval": "closed",
          "isDefault": true,
          "value": 10
        }
      ]
    },
    {
      "id": "SC-ASSURANCE-002",
      "name": "availability",
      "description": "Requested availability target for the slice. For surgical URLLC scenarios, expected usage is very high availability, commonly 99.999 percent. This specification constrains only the allowed structural range. Semantic and policy validation are performed outside this specification by II MS / knowledge-plane validation.",
      "valueType": "number",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "number",
          "unitOfMeasure": "percent",
          "valueFrom": 0,
          "valueTo": 100,
          "rangeInterval": "closed",
          "isDefault": true,
          "value": 99.999
        }
      ]
    },
    {
      "id": "SC-CONTEXT-001",
      "name": "geo_location",
      "description": "Resolvable site reference identifying the target hospital or operating location. This specification defines the required object structure only. Site resolution, geographic interpretation, and domain-specific validation are performed outside this specification by II MS / knowledge-plane validation.",
      "valueType": "object",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "object",
          "semanticType": "tio:GeographicSiteRef",
          "referenceModel": "TMF673-Site",
          "requiredFields": [
            "locationId",
            "locationType",
            "geographicScope"
          ],
          "description": "CSP-independent resolvable location reference. Structural shape is enforced here; semantic resolution is performed externally."
        }
      ]
    },
    {
      "id": "SC-CONTEXT-002",
      "name": "priority",
      "description": "Priority classification for the requested slice intent. For surgical use cases, higher priority values are typically expected. This specification constrains the allowed enumeration only. Operational meaning and policy impact are determined outside this specification by II MS / knowledge-plane validation.",
      "valueType": "string",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "value": "CRITICAL",
          "isDefault": false
        },
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "value": "HIGH",
          "isDefault": false
        },
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "value": "NORMAL",
          "isDefault": true
        }
      ]
    },
    {
      "id": "SC-CONTEXT-003",
      "name": "semantic_tag",
      "description": "Semantic classification tag associated with the requested slice intent. This specification constrains the structural value only. The meaning of the tag and any semantic-policy consequences are validated outside this specification by II MS / knowledge-plane validation.",
      "valueType": "string",
      "minCardinality": 1,
      "maxCardinality": 1,
      "configurable": true,
      "@type": "CharacteristicSpecification",
      "characteristicValueSpecification": [
        {
          "@type": "CharacteristicValueSpecification",
          "valueType": "string",
          "value": "medical_urllc_critical",
          "isDefault": true
        }
      ]
    }
  ],
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "GET"
    },
    "fullUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PUT"
    },
    "partialUpdate": {
      "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "PATCH",
      "warning": "PATCH is allowed but discouraged. Use PUT for deterministic specification updates."
    },
    "delete": {
      "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
      "method": "DELETE"
    }
  }
}
```

## IC MS IntentReport terminology refinement

### Baseline terminology direction
For external `IntentReport`, prefer existing cross-platform names to minimise custom code and mapping:
- use `metrics`
- use `targets`
- use `evaluations`

Avoid introducing extra report-only terms such as:
- `observedOutcome`
- `expectations`

### Consistency rationale
This keeps `IntentReport` aligned with the existing internal naming direction:
- `evaluations` already exists in internal assurance and optimisation-related baselines
- `metrics` already exists in the reusable resource-entry shape
- target values can be represented cleanly as `targets`

### Preferred report pattern
```json
{
  "status": "Degraded",
  "statusReason": "Observed service quality no longer satisfies the expected operating target.",
  "evaluations": [
    {
      "name": "latencyCompliance",
      "result": "failed"
    },
    {
      "name": "availabilityCompliance",
      "result": "passed"
    }
  ],
  "metrics": [
    {
      "name": "latencyMs",
      "value": 12
    },
    {
      "name": "reliabilityPercent",
      "value": 99.992
    }
  ],
  "targets": [
    {
      "name": "latencyMs",
      "operator": "<=",
      "value": 10
    },
    {
      "name": "reliabilityPercent",
      "operator": ">=",
      "value": 99.99
    }
  ]
}
```

## IC MS interface baseline — GET /intentManagement/v5/intent/{intentId}/intentReport/{id}

### Summary
Retrieves a single `IntentReport` resource for a given `Intent` from IC MS by report id. This is the baselined retrieve-one operation for the external curated `IntentReport` projection. It returns `200 OK`, includes `Content-Location` and mandatory `ETag`, uses private caching by default, and returns a richer curated `IntentReport` representation.

### Terminology note
`targets` is now baselined for the external `IntentReport` shape as the preferred report term for intended values, to stay consistent and avoid report-only wording such as `expectations`.

### Spec alignment note
From TMF921, this route:
- retrieves a single `IntentReport`
- is nested under the parent `intentId`
- supports `fields` selection for first-level attributes
- returns the TMF-defined `200IntentReport_Get` response shape

### IntentReport notes
- `IntentReport` is IC-MS-owned
- it is external
- it is a curated reporting/projection resource
- it is not raw runtime telemetry
- for terminology consistency, prefer:
  - `metrics`
  - `targets`
  - `evaluations`

### Request headers
```http
GET /intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001 HTTP/1.1
Host: mycsp.com.au
Accept: application/json
Accept-Language: en-AU
```

### Success response headers
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Language: en-AU
Content-Location: https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001
ETag: W/"IR-INT-HOSP-2026-001-001-r1"
Cache-Control: private, max-age=300
```

### Success response body
```json
{
  "id": "IR-INT-HOSP-2026-001-001",
  "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
  "name": "Sydney Hospital Surgical Connection Intent Report",
  "description": "Curated external report for the Sydney Hospital surgical connection intent.",
  "reportType": "IntentStatusReport",
  "category": "service-assurance",
  "creationDate": "2026-04-18T12:15:00+10:00",
  "lastUpdate": "2026-04-18T12:15:00+10:00",
  "validFor": {
    "startDateTime": "2026-04-18T12:15:00+10:00"
  },
  "status": "Degraded",
  "statusChangeDate": "2026-04-18T12:10:00+10:00",
  "statusReason": "Observed service quality no longer satisfies the expected operating target.",
  "summary": "The intent remains in service, but current observed performance is below the expected target.",
  "intent": {
    "id": "INT-HOSP-2026-001",
    "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
    "@type": "IntentRef",
    "@referredType": "Intent"
  },
  "intentSpecification": {
    "id": "hospital-surgical-slice-spec-v1.19",
    "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
    "@type": "IntentSpecificationRef",
    "@referredType": "IntentSpecification"
  },
  "priority": "CRITICAL",
  "expression": {
    "@type": "JsonLdExpression",
    "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
    "expressionValue": {
      "@context": {
        "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
      },
      "@type": "icm:Constraint",
      "icm:and": [
        {
          "@type": "icm:LessOrEqual",
          "icm:leftOperand": "latency",
          "icm:rightOperand": 10
        },
        {
          "@type": "icm:GreaterOrEqual",
          "icm:leftOperand": "availability",
          "icm:rightOperand": 99.99
        }
      ]
    }
  },
  "targets": [
    {
      "name": "latencyMs",
      "operator": "<=",
      "value": 10
    },
    {
      "name": "reliabilityPercent",
      "operator": ">=",
      "value": 99.99
    }
  ],
  "metrics": [
    {
      "name": "latencyMs",
      "value": 12
    },
    {
      "name": "reliabilityPercent",
      "value": 99.992
    }
  ],
  "evaluations": [
    {
      "name": "latencyCompliance",
      "result": "failed"
    },
    {
      "name": "availabilityCompliance",
      "result": "passed"
    }
  ],
  "recommendedAction": "Review service quality and re-optimise if degradation persists.",
  "@type": "IntentReport",
  "_links": {
    "self": {
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
      "method": "GET"
    }
  }
}
```

### Not found response headers
```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Content-Language: en-AU
Cache-Control: no-store
```

### Not found response body
```json
{
  "code": "RESOURCE_NOT_FOUND",
  "reason": "NOT_FOUND",
  "message": "No IntentReport exists for intent 'INT-HOSP-2026-001' and id 'IR-INT-HOSP-2026-001-001'.",
  "status": 404,
  "referenceError": "https://mycsp.com.au/errors/RESOURCE_NOT_FOUND",
  "@type": "Error"
}
```

## IC MS external event baseline — IntentCreateEvent

### Summary
External TMF-aligned event emitted by IC MS when a new `Intent` resource is created. This is the baselined create event for the surgical hospital slice example. It carries `event.intent`, is delivered via `/intent/hub`, is treated as a design-time external event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### TMF alignment note
This event is treated as TMF-aligned with platform-owned concrete content:
- TMF-style external event envelope is preserved
- event payload carries `event.intent`
- concrete field content and example values are platform-owned

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentCreateEvent for creation of the Sydney Hospital surgical connection intent.",
  "eventId": "EVT-INT-HOSP-2026-001-CREATE-0001",
  "eventTime": "2026-04-17T10:00:01+10:00",
  "eventType": "IntentCreateEvent",
  "priority": "3",
  "title": "IntentCreateEvent",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "lifecycleStatus": "Acknowledged",
      "priority": "CRITICAL",
      "isBundle": false,
      "@type": "Intent",
      "@baseType": "Entity",
      "validFor": {
        "startDateTime": "2026-04-17T10:00:00+10:00",
        "endDateTime": "2027-04-17T10:00:00+10:00"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "name": "Hospital-Surgical-Slice-Spec",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification",
        "@href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "humanExpression": "I need a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "characteristic": [
        {
          "@type": "Characteristic",
          "name": "slice_type",
          "value": "URLLC"
        },
        {
          "@type": "Characteristic",
          "name": "latency",
          "value": 10
        },
        {
          "@type": "Characteristic",
          "name": "availability",
          "value": 99.99
        },
        {
          "@type": "Characteristic",
          "name": "priority",
          "value": "CRITICAL"
        },
        {
          "@type": "Characteristic",
          "name": "semantic_tag",
          "value": "medical_urllc_critical"
        },
        {
          "@type": "Characteristic",
          "name": "geo_location",
          "value": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "HOSPITAL",
            "geographicScope": "AU-NSW-SYD"
          }
        }
      ]
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentCreateEvent"
}
```

## IC MS external event baseline — IntentAttributeValueChangeEvent

### Summary
External TMF-aligned event emitted by IC MS when an existing `Intent` resource has attribute values updated. This is the baselined attribute-value-change event for the surgical hospital slice example. It carries `event.intent`, is delivered via `/intent/hub`, is treated as a design-time external event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### TMF alignment note
This event is treated as TMF-aligned with platform-owned concrete content:
- TMF-style external event envelope is preserved
- event payload carries `event.intent`
- concrete field content and example values are platform-owned

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentAttributeValueChangeEvent for update of the Sydney Hospital surgical connection intent.",
  "eventId": "EVT-INT-HOSP-2026-001-ATTR-0001",
  "eventTime": "2026-04-17T10:05:00+10:00",
  "eventType": "IntentAttributeValueChangeEvent",
  "priority": "3",
  "title": "IntentAttributeValueChangeEvent",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "lifecycleStatus": "Acknowledged",
      "priority": "CRITICAL",
      "isBundle": false,
      "@type": "Intent",
      "@baseType": "Entity",
      "validFor": {
        "startDateTime": "2026-04-17T10:00:00+10:00",
        "endDateTime": "2027-04-17T10:00:00+10:00"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "name": "Hospital-Surgical-Slice-Spec",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification",
        "@href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "humanExpression": "I need a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "characteristic": [
        {
          "@type": "Characteristic",
          "name": "slice_type",
          "value": "URLLC"
        },
        {
          "@type": "Characteristic",
          "name": "latency",
          "value": 10
        },
        {
          "@type": "Characteristic",
          "name": "availability",
          "value": 99.99
        },
        {
          "@type": "Characteristic",
          "name": "priority",
          "value": "CRITICAL"
        },
        {
          "@type": "Characteristic",
          "name": "semantic_tag",
          "value": "medical_urllc_critical"
        },
        {
          "@type": "Characteristic",
          "name": "geo_location",
          "value": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "HOSPITAL",
            "geographicScope": "AU-NSW-SYD"
          }
        }
      ]
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentAttributeValueChangeEvent"
}
```

## IC MS external event baseline — IntentStatusChangeEvent

### Summary
External TMF-aligned event emitted by IC MS when the lifecycle status of an existing `Intent` changes. This is the baselined status-change event for the surgical hospital slice example. It carries `event.intent`, is delivered via `/intent/hub`, is treated as a design-time external event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### TMF alignment note
This event is treated as TMF-aligned with platform-owned concrete content:
- TMF-style external event envelope is preserved
- event payload carries `event.intent`
- concrete field content and example values are platform-owned

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentStatusChangeEvent for lifecycle transition of the Sydney Hospital surgical connection intent.",
  "eventId": "EVT-INT-HOSP-2026-001-STATUS-0001",
  "eventTime": "2026-04-18T12:10:05+10:00",
  "eventType": "IntentStatusChangeEvent",
  "priority": "3",
  "title": "IntentStatusChangeEvent",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "description": "Request for a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "lifecycleStatus": "Degraded",
      "priority": "CRITICAL",
      "isBundle": false,
      "@type": "Intent",
      "@baseType": "Entity",
      "validFor": {
        "startDateTime": "2026-04-17T10:00:00+10:00",
        "endDateTime": "2027-04-17T10:00:00+10:00"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "name": "Hospital-Surgical-Slice-Spec",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification",
        "@href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
      },
      "humanExpression": "I need a surgical connection in Sydney Hospital with latency <= 10 ms and availability >= 99.99.",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "characteristic": [
        {
          "@type": "Characteristic",
          "name": "slice_type",
          "value": "URLLC"
        },
        {
          "@type": "Characteristic",
          "name": "latency",
          "value": 10
        },
        {
          "@type": "Characteristic",
          "name": "availability",
          "value": 99.99
        },
        {
          "@type": "Characteristic",
          "name": "priority",
          "value": "CRITICAL"
        },
        {
          "@type": "Characteristic",
          "name": "semantic_tag",
          "value": "medical_urllc_critical"
        },
        {
          "@type": "Characteristic",
          "name": "geo_location",
          "value": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "locationType": "HOSPITAL",
            "geographicScope": "AU-NSW-SYD"
          }
        }
      ]
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentStatusChangeEvent"
}
```

## IC MS external event baseline — IntentDeleteEvent

### Summary
External TMF-aligned event emitted by IC MS when an `Intent` resource is deleted. This is the baselined delete event for the surgical hospital slice example. It carries a lean `event.intent`, is delivered via `/intent/hub`, is treated as a design-time external event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### Baseline notes
- keep delete payload lean
- do not duplicate the richer status-projection shape from `IntentStatusChangeEvent`
- do not introduce a separate `Deleted` lifecycle state
- treat this as a lean tombstone-style event for deletion of the external `Intent` resource

### TMF alignment note
This event is treated as TMF-aligned with platform-owned concrete content:
- TMF-style external event envelope is preserved
- event payload carries `event.intent`
- concrete field content and example values are platform-owned

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentDeleteEvent for deletion of the Sydney Hospital surgical connection intent.",
  "eventId": "EVT-INT-HOSP-2026-001-DELETE-0001",
  "eventTime": "2026-04-19T09:00:00+10:00",
  "eventType": "IntentDeleteEvent",
  "priority": "3",
  "title": "IntentDeleteEvent",
  "event": {
    "intent": {
      "id": "INT-HOSP-2026-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "name": "Sydney Hospital Surgical Connection Intent",
      "@type": "Intent",
      "@baseType": "Entity"
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentDeleteEvent"
}
```

## IC MS external event baseline — IntentReportCreateEvent

### Summary
External TMF-aligned event emitted by IC MS when a new `IntentReport` resource is created. This baselined create event for the surgical hospital slice example carries `event.intentReport`, is delivered via `/intent/hub`, is treated as a curated external reporting event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### Terminology check
No new terminology introduced here beyond already baselined terms:
- `IntentReport`
- `metrics`
- `targets`
- `evaluations`

### Baseline notes
- this is a curated external report event
- not raw runtime telemetry
- keep it aligned with the richer `IntentReport` retrieve-one shape
- use the same hub as `Intent...Event`

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentReportCreateEvent for creation of the Sydney Hospital surgical connection intent report.",
  "eventId": "EVT-IR-INT-HOSP-2026-001-001-CREATE-0001",
  "eventTime": "2026-04-18T12:15:05+10:00",
  "eventType": "IntentReportCreateEvent",
  "priority": "3",
  "title": "IntentReportCreateEvent",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
      "name": "Sydney Hospital Surgical Connection Intent Report",
      "description": "Curated external report for the Sydney Hospital surgical connection intent.",
      "reportType": "IntentStatusReport",
      "category": "service-assurance",
      "creationDate": "2026-04-18T12:15:00+10:00",
      "lastUpdate": "2026-04-18T12:15:00+10:00",
      "validFor": {
        "startDateTime": "2026-04-18T12:15:00+10:00"
      },
      "status": "Degraded",
      "statusChangeDate": "2026-04-18T12:10:00+10:00",
      "statusReason": "Observed service quality no longer satisfies the expected operating target.",
      "summary": "The intent remains in service, but current observed performance is below the expected target.",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
        "@type": "IntentRef",
        "@referredType": "Intent"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification"
      },
      "priority": "CRITICAL",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "targets": [
        {
          "name": "latencyMs",
          "operator": "<=",
          "value": 10
        },
        {
          "name": "reliabilityPercent",
          "operator": ">=",
          "value": 99.99
        }
      ],
      "metrics": [
        {
          "name": "latencyMs",
          "value": 12
        },
        {
          "name": "reliabilityPercent",
          "value": 99.992
        }
      ],
      "evaluations": [
        {
          "name": "latencyCompliance",
          "result": "failed"
        },
        {
          "name": "availabilityCompliance",
          "result": "passed"
        }
      ],
      "recommendedAction": "Review service quality and re-optimise if degradation persists.",
      "@type": "IntentReport"
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentReportCreateEvent"
}
```

## IC MS external event baseline — IntentReportAttributeValueChangeEvent

### Summary
External TMF-aligned event emitted by IC MS when an existing `IntentReport` resource has attribute values updated. This baselined attribute-value-change event for the surgical hospital slice example carries `event.intentReport`, is delivered via `/intent/hub`, is treated as a curated external reporting event, and uses `intent-controller-ms` in both `reportingSystem.name` and `source.name`.

### Terminology check
No new terminology introduced here beyond already baselined terms:
- `IntentReport`
- `metrics`
- `targets`
- `evaluations`

### Baseline notes
- this is a curated external report event
- not raw runtime telemetry
- keep it aligned with the richer `IntentReport` retrieve-one shape
- use the same hub as `Intent...Event`
- suitable when report content changes without deleting the report resource

### Event JSON
```json
{
  "correlationId": "INT-HOSP-2026-001",
  "description": "IntentReportAttributeValueChangeEvent for update of the Sydney Hospital surgical connection intent report.",
  "eventId": "EVT-IR-INT-HOSP-2026-001-001-ATTR-0001",
  "eventTime": "2026-04-18T12:20:00+10:00",
  "eventType": "IntentReportAttributeValueChangeEvent",
  "priority": "3",
  "title": "IntentReportAttributeValueChangeEvent",
  "event": {
    "intentReport": {
      "id": "IR-INT-HOSP-2026-001-001",
      "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001/intentReport/IR-INT-HOSP-2026-001-001",
      "name": "Sydney Hospital Surgical Connection Intent Report",
      "description": "Curated external report for the Sydney Hospital surgical connection intent.",
      "reportType": "IntentStatusReport",
      "category": "service-assurance",
      "creationDate": "2026-04-18T12:15:00+10:00",
      "lastUpdate": "2026-04-18T12:20:00+10:00",
      "validFor": {
        "startDateTime": "2026-04-18T12:15:00+10:00"
      },
      "status": "Degraded",
      "statusChangeDate": "2026-04-18T12:10:00+10:00",
      "statusReason": "Observed service quality no longer satisfies the expected operating target.",
      "summary": "The intent remains in service, but current observed performance is below the expected target.",
      "intent": {
        "id": "INT-HOSP-2026-001",
        "href": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
        "@type": "IntentRef",
        "@referredType": "Intent"
      },
      "intentSpecification": {
        "id": "hospital-surgical-slice-spec-v1.19",
        "href": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19",
        "@type": "IntentSpecificationRef",
        "@referredType": "IntentSpecification"
      },
      "priority": "CRITICAL",
      "expression": {
        "@type": "JsonLdExpression",
        "iri": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/",
        "expressionValue": {
          "@context": {
            "icm": "http://tio.models.tmforum.org/tio/v2.0.0/IntentCommonModel/"
          },
          "@type": "icm:Constraint",
          "icm:and": [
            {
              "@type": "icm:LessOrEqual",
              "icm:leftOperand": "latency",
              "icm:rightOperand": 10
            },
            {
              "@type": "icm:GreaterOrEqual",
              "icm:leftOperand": "availability",
              "icm:rightOperand": 99.99
            }
          ]
        }
      },
      "targets": [
        {
          "name": "latencyMs",
          "operator": "<=",
          "value": 10
        },
        {
          "name": "reliabilityPercent",
          "operator": ">=",
          "value": 99.99
        }
      ],
      "metrics": [
        {
          "name": "latencyMs",
          "value": 12
        },
        {
          "name": "reliabilityPercent",
          "value": 99.992
        }
      ],
      "evaluations": [
        {
          "name": "latencyCompliance",
          "result": "failed"
        },
        {
          "name": "availabilityCompliance",
          "result": "passed"
        }
      ],
      "recommendedAction": "Review service quality and re-optimise if degradation persists.",
      "@type": "IntentReport"
    }
  },
  "reportingSystem": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "source": {
    "id": "IC-MS",
    "name": "intent-controller-ms",
    "@type": "ReportingResource",
    "@referredType": "LogicalResource"
  },
  "@type": "IntentReportAttributeValueChangeEvent"
}
```

## Internal event baseline refinement — IntentAssuranceEvent shared consumer role

### Baseline interpretation
`IntentAssuranceEvent` is the shared internal assurance truth event consumed by both:
- II MS, to decide what happens next
- IC MS, to keep external state and reporting aligned with actual network state

### Design consequence
Keep `IntentAssuranceEvent`:
- generic
- clean
- state-focused
- not optimiser-specific
- not IC-specific
- not overloaded with duplicated derived views

### Preferred structure direction
Use:
- `lifecycleStatus`
- `statusChangeDate`
- `statusReason`
- `current`
- `candidates`
- `references`

This event is the platform assurance truth that both II MS and IC MS consume for different purposes.

## Internal event baseline — IntentAssuranceEvent

### Summary
Shared internal assurance truth event consumed by both II MS and IC MS. II MS uses it to decide what happens next, while IC MS uses it to keep external state and reporting aligned with actual network state.

### Terminology check
New active field baselined here:
- `deviation` inside `evaluations[]`

Keep the already baselined names:
- `lifecycleStatus`
- `statusChangeDate`
- `statusReason`
- `location.locationId`
- `current`
- `candidates`
- `resources`
- `metrics`
- `evaluations`
- `references`

### Baseline notes
- emitted by `intent-assurance-ms`
- sent on internal topic `t7.intent.management.events`
- uses CloudEvents metadata in headers
- business content is in `body`
- `current.resources` is the current in-service set
- `candidates` is the optional re-decision set
- live values use `latencyMs` and `reliabilityPercent`
- `evaluations` stays inside `current`
- `deviation.value` uses signed numeric margin semantics

### Sign rule
- positive `deviation.value` = above target
- negative `deviation.value` = below target

### Event JSON
```json
{
  "topic": "t7.intent.management.events",
  "key": "INT-HOSP-2026-001",
  "headers": {
    "content-type": "application/json",
    "ce_specversion": "1.0",
    "ce_type": "IntentAssuranceEvent",
    "ce_source": "intent-assurance-ms",
    "ce_id": "EVT-INT-HOSP-2026-001-ASR-0001",
    "ce_time": "2026-04-18T12:10:00+10:00",
    "ce_subject": "INT-HOSP-2026-001",
    "ce_datacontenttype": "application/json",
    "ce_correlationid": "INT-HOSP-2026-001-INIT"
  },
  "body": {
    "eventType": "IntentAssuranceEvent",
    "eventVersion": "1.0",
    "source": "intent-assurance-ms",
    "eventTime": "2026-04-18T12:10:00+10:00",
    "correlationId": "INT-HOSP-2026-001-INIT",
    "intentId": "INT-HOSP-2026-001",
    "lifecycleStatus": "Degraded",
    "statusChangeDate": "2026-04-18T12:10:00+10:00",
    "statusReason": "Observed service quality no longer satisfies the expected operating target.",
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001"
    },
    "current": {
      "serviceClass": "critical-gold",
      "evaluations": [
        {
          "name": "latencyCompliance",
          "result": "failed",
          "deviation": {
            "value": 2,
            "unit": "ms"
          }
        },
        {
          "name": "availabilityCompliance",
          "result": "passed",
          "deviation": {
            "value": 0.002,
            "unit": "percent"
          }
        }
      ],
      "resources": [
        {
          "roles": ["primary"],
          "resourceId": "PATH-SYD-HOSP-001-A",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          },
          "relationships": [
            {
              "type": "disjointFrom",
              "targetResourceId": "PATH-SYD-HOSP-001-B"
            }
          ],
          "metrics": [
            {
              "name": "latencyMs",
              "value": 12
            },
            {
              "name": "reliabilityPercent",
              "value": 99.992
            }
          ]
        },
        {
          "roles": ["secondary"],
          "resourceId": "PATH-SYD-HOSP-001-B",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          },
          "relationships": [
            {
              "type": "disjointFrom",
              "targetResourceId": "PATH-SYD-HOSP-001-A"
            }
          ],
          "metrics": [
            {
              "name": "latencyMs",
              "value": 9
            },
            {
              "name": "reliabilityPercent",
              "value": 99.995
            }
          ]
        }
      ]
    },
    "candidates": [
      {
        "roles": ["primary"],
        "resourceId": "PATH-SYD-HOSP-001-D",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "relationships": [
          {
            "type": "disjointFrom",
            "targetResourceId": "PATH-SYD-HOSP-001-B"
          }
        ],
        "metrics": [
          {
            "name": "latencyMs",
            "value": 11
          },
          {
            "name": "reliabilityPercent",
            "value": 99.998
          }
        ]
      },
      {
        "roles": ["secondary"],
        "resourceId": "PATH-SYD-HOSP-001-C",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-silver",
        "resourceAttributes": {
          "locationId": "AU-NSW-SYD-HOSP-001"
        },
        "metrics": [
          {
            "name": "latencyMs",
            "value": 10
          },
          {
            "name": "reliabilityPercent",
            "value": 99.997
          }
        ]
      }
    ],
    "references": {
      "intent": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

## Terminology enforcement baseline refinement — remove serviceType from active payloads

### Rule
- remove `serviceType` from active payloads and events
- keep only `service.serviceClass`

### Rationale
`serviceClass` is the canonical active service classification term. `serviceType` is not required in the active payload set unless a real consumer need appears later.

## Post-assurance re-optimisation baseline

### Rule
`IntentAssuranceEvent` always includes the current active resources.

When `lifecycleStatus` is not `Degraded`:
- there is no requirement for II MS to trigger another `IntentResolvedEvent`
- II MS can treat the assurance event as state/reporting truth only

When `lifecycleStatus` is `Degraded`:
- `IntentAssuranceEvent` may also include the broader applicable monitored resource set with metrics
- II MS can use that broader set to decide whether re-resolution / re-optimisation is needed

### Preferred terminology
Prefer:
- `current active resources`
- `applicable monitored resources`

Avoid looser wording such as:
- `available resources`

### Design consequence
- non-degraded assurance flow does not automatically reopen optimisation
- degraded assurance flow is the trigger point where II MS may emit another `IntentResolvedEvent`

## IntentAssuranceEvent candidate optionality baseline

### Rule
Use `candidates` only when re-decision / rediscovery is actually needed.

- normal / `Active` / non-`Degraded`:
  - include only `current`
  - do not include `candidates`

- `Degraded`, but no re-decision needed yet:
  - `current` may still be sufficient
  - II MS may treat the event as state/reporting truth only

- `Degraded` and re-decision needed:
  - include `candidates`
  - include candidate `metrics`
  - II MS can use that input to decide the next `IntentResolvedEvent`

### Design consequence
- `current` is the always-relevant operational truth
- `candidates` is conditional
- candidate `metrics` appear only when `candidates` is present for re-decision

## IntentAssuranceEvent shape baseline — degraded and non-degraded forms

### Rule
Use the same event name: `IntentAssuranceEvent`.

Allow two payload forms based on state:

- non-degraded form:
  - no `candidates`
  - includes current assurance truth only

- degraded form:
  - may include `candidates` when re-decision is needed
  - still keeps the same event name and overall event structure

### Design consequence
Do not introduce a separate event type for degraded vs non-degraded assurance.
Keep one assurance truth event with conditional body shape by lifecycle state.

## IntentAssuranceEvent candidate set refinement baseline

### Rule
When `candidates` is present in the degraded re-decision form of `IntentAssuranceEvent`, it must contain the full applicable re-decision set, including the currently active resources.

### Interpretation
- `current.resources` = what is active now
- `candidates` = full applicable re-decision set, including active resources and other applicable monitored resources

### Design consequence
II MS must be able to decide among:
- keep the current selection
- partially change the current selection
- fully re-optimise the selection

So `candidates` must not exclude the current active resources.

## KP naming stability baseline — keep prior observability naming

### Rule
Keep the earlier observability-related naming as previously drafted for now.

- do not rename to `monitoringProfileId`
- do not introduce a broader `monitoring` rename across events/config at this stage

### Intent
Avoid unnecessary terminology churn and keep progressing with the current KP refinement using the already drafted observability naming.

## KP baseline — master knowledge config v1

### Summary
Baselined internal KP / master knowledge config for the hospital slice example. This is internal II MS knowledge, not an intent resource and not an external IntentSpecification contract.

### Full config
```json
{
  "version": "1.0",

  "locations": {
    "AU-NSW-SYD-HOSP-001": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "name": "Sydney Hospital",
      "locationType": "HOSPITAL",
      "geographicScope": "AU-NSW-SYD",
      "resourceAttributes": {
        "surgicalCapable": true
      },
      "applicableResourceIds": [
        "SYD-PRI-01",
        "SYD-PRI-02",
        "SYD-BAK-01",
        "SYD-BAK-02",
        "SYD-CMP-01",
        "SYD-SEC-01"
      ],
      "observabilityProfileId": "URLLC_SURGICAL_HIGH_FIDELITY",
      "optimisationProfileIds": [
        "SURGICAL_JOINT",
        "LOWEST_LATENCY"
      ]
    },
    "AU-VIC-MEL-HOSP-101": {
      "locationId": "AU-VIC-MEL-HOSP-101",
      "name": "Alpha Hospital",
      "locationType": "HOSPITAL",
      "geographicScope": "AU-VIC-MEL",
      "resourceAttributes": {
        "surgicalCapable": true
      },
      "applicableResourceIds": [],
      "observabilityProfileId": "URLLC_SURGICAL_HIGH_FIDELITY",
      "optimisationProfileIds": [
        "SURGICAL_JOINT",
        "LOWEST_LATENCY"
      ]
    },
    "AU-QLD-BNE-HOSP-201": {
      "locationId": "AU-QLD-BNE-HOSP-201",
      "name": "Gamma Hospital",
      "locationType": "HOSPITAL",
      "geographicScope": "AU-QLD-BNE",
      "resourceAttributes": {
        "surgicalCapable": true
      },
      "applicableResourceIds": [],
      "observabilityProfileId": "URLLC_SURGICAL_HIGH_FIDELITY",
      "optimisationProfileIds": [
        "SURGICAL_JOINT",
        "LOWEST_LATENCY"
      ]
    },
    "AU-NSW-NEW-HOSP-301": {
      "locationId": "AU-NSW-NEW-HOSP-301",
      "name": "Beta Hospital",
      "locationType": "HOSPITAL",
      "geographicScope": "AU-NSW-NEW",
      "resourceAttributes": {
        "surgicalCapable": false
      },
      "applicableResourceIds": []
    }
  },

  "services": {
    "surgical-connectivity": {
      "serviceId": "surgical-connectivity",
      "name": "Surgical Connectivity Service",
      "serviceClass": "critical-gold",
      "locationTypes": [
        "HOSPITAL"
      ],
      "constraints": {
        "sliceType": "URLLC",
        "trafficClass": "URLLC-Gold",
        "semanticTag": "medical_urllc_critical",
        "priority": [
          "CRITICAL",
          "HIGH"
        ]
      }
    }
  },

  "policyRules": {
    "surgical-urllc-location-policy": {
      "ruleId": "surgical-urllc-location-policy",
      "appliesTo": {
        "sliceType": "URLLC",
        "semanticTag": "medical_urllc_critical"
      },
      "conditions": [
        {
          "field": "locationType",
          "operator": "equals",
          "value": "HOSPITAL"
        },
        {
          "field": "surgicalCapable",
          "operator": "equals",
          "value": true
        }
      ],
      "onFailure": {
        "reasonCode": "POLICY_LOCATION_NOT_ALLOWED",
        "statusReason": "Requested location is not allowed for the surgical URLLC profile."
      }
    },
    "surgical-priority-policy": {
      "ruleId": "surgical-priority-policy",
      "appliesTo": {
        "sliceType": "URLLC",
        "semanticTag": "medical_urllc_critical"
      },
      "conditions": [
        {
          "field": "priority",
          "operator": "in",
          "value": ["CRITICAL", "HIGH"]
        }
      ],
      "onFailure": {
        "reasonCode": "POLICY_PRIORITY_NOT_ALLOWED",
        "statusReason": "Requested priority is not allowed for the surgical URLLC profile."
      }
    }
  },

  "resources": {
    "SYD-PRI-01": {
      "resourceId": "SYD-PRI-01",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["primary"],
      "locationId": "AU-NSW-SYD-HOSP-001",
      "resourceAttributes": {
        "hops": ["fc00:2:2:101", "fc00:2:2:210"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_SYDNEY_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "SYD-BAK-01"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 6.1
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.995
        }
      ]
    },
    "SYD-PRI-02": {
      "resourceId": "SYD-PRI-02",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["primary"],
      "locationId": "AU-NSW-SYD-HOSP-001",
      "resourceAttributes": {
        "hops": ["fc00:2:2:105", "fc00:2:2:220"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_SYDNEY_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "SYD-BAK-02"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 8.9
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.992
        }
      ]
    },
    "SYD-BAK-01": {
      "resourceId": "SYD-BAK-01",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["secondary"],
      "locationId": "AU-NSW-SYD-HOSP-001",
      "resourceAttributes": {
        "hops": ["fc00:2:2:102", "fc00:2:2:211"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_SYDNEY_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "SYD-PRI-01"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 7.0
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.994
        }
      ]
    },
    "SYD-BAK-02": {
      "resourceId": "SYD-BAK-02",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["secondary"],
      "locationId": "AU-NSW-SYD-HOSP-001",
      "resourceAttributes": {
        "hops": ["fc00:2:2:106", "fc00:2:2:221"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_SYDNEY_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "SYD-PRI-02"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 9.5
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.991
        }
      ]
    },
    "SYD-CMP-01": {
      "resourceId": "SYD-CMP-01",
      "resourceType": "computeResource",
      "resourceClass": "critical-gold",
      "roles": [],
      "locationId": "AU-NSW-SYD-HOSP-001",
      "resourceAttributes": {
        "surgicalCapable": true,
        "status": "Baseline",
        "zone": "SYD-COMPUTE-A"
      },
      "metrics": [
        {
          "name": "capacityBenchmarkUnits",
          "value": 120
        }
      ]
    },
    "SYD-SEC-01": {
      "resourceId": "SYD-SEC-01",
      "resourceType": "securityResource",
      "resourceClass": "critical-silver",
      "roles": [],
      "locationId": "AU-NSW-SYD-HOSP-001",
      "resourceAttributes": {
        "surgicalCapable": true,
        "status": "Baseline",
        "inspectionMode": "deep-packet"
      },
      "metrics": [
        {
          "name": "inspectionCapacityBenchmarkGbps",
          "value": 40
        }
      ]
    }
  },

  "observabilityProfiles": {
    "URLLC_SURGICAL_HIGH_FIDELITY": {
      "profileId": "URLLC_SURGICAL_HIGH_FIDELITY",
      "telemetrySink": "PROMETHEUS_SYDNEY_CLUSTER",
      "samplingPolicy": "high-fidelity"
    }
  },

  "optimisationProfiles": {
    "SURGICAL_JOINT": {
      "profileId": "SURGICAL_JOINT",
      "engine": "gurobi",
      "model": "GUROBI_LATENCY_RELIABILITY_JOINT",
      "objective": "minimise_latency_maximise_reliability",
      "selectionPolicy": {
        "requireDisjointPrimaryAndSecondary": true
      }
    },
    "LOWEST_LATENCY": {
      "profileId": "LOWEST_LATENCY",
      "engine": "gurobi",
      "model": "GUROBI_LOWEST_LATENCY_FEASIBLE",
      "objective": "minimise_latency",
      "selectionPolicy": {
        "requireDisjointPrimaryAndSecondary": true
      }
    }
  },

  "humanExpressionMapping": {
    "enabled": true,
    "entityAliases": {
      "Sydney Hospital": "AU-NSW-SYD-HOSP-001",
      "Alpha Hospital": "AU-VIC-MEL-HOSP-101",
      "Gamma Hospital": "AU-QLD-BNE-HOSP-201",
      "Beta Hospital": "AU-NSW-NEW-HOSP-301"
    },
    "fieldPatterns": [
      {
        "field": "locationId",
        "matchType": "entityAlias"
      },
      {
        "field": "latency",
        "patterns": [
          {
            "regex": "(?i)latency\\s*(<=|less than or equal to|at most|max(?:imum)? of)\\s*(\\d+)\\s*ms",
            "operator": "<=",
            "valueGroup": 2,
            "unit": "ms"
          }
        ]
      },
      {
        "field": "availability",
        "patterns": [
          {
            "regex": "(?i)availability\\s*(>=|greater than or equal to|at least|min(?:imum)? of)\\s*(\\d+(?:\\.\\d+)?)",
            "operator": ">=",
            "valueGroup": 2,
            "unit": "percent"
          }
        ]
      },
      {
        "field": "sliceType",
        "patterns": [
          {
            "regex": "(?i)surgical connection|surgical slice|surgical urllc",
            "value": "URLLC"
          }
        ]
      },
      {
        "field": "priority",
        "patterns": [
          {
            "regex": "(?i)critical|emergency",
            "value": "CRITICAL"
          },
          {
            "regex": "(?i)high priority|high",
            "value": "HIGH"
          }
        ]
      },
      {
        "field": "semanticTag",
        "patterns": [
          {
            "regex": "(?i)surgical|medical",
            "value": "medical_urllc_critical"
          }
        ]
      }
    ],
    "defaults": {
      "sliceType": "URLLC",
      "priority": "CRITICAL",
      "semanticTag": "medical_urllc_critical"
    },
    "conflictPolicy": {
      "precedence": ["formalExpression", "characteristic", "humanExpression"],
      "onConflict": "reject"
    }
  },

  "behaviour": {
    "latencyOperator": "max",
    "availabilityOperator": "min",
    "onInvalidExpression": "reject",
    "resolveLocationFromHumanExpression": true
  },

  "resolutionOutput": {
    "onSuccess": {
      "semanticStatus": "RESOLVED",
      "includeResolvedLocation": true,
      "includeExecution": true,
      "includeObservability": true,
      "includeOptimisation": true,
      "includeResources": true
    },
    "onFailure": {
      "semanticStatus": "REJECTED",
      "includeRejectionMessage": true
    }
  }
}
```

## KP config refinement decisions

### Locked decisions
- `resourceAttributes.surgicalCapable` is treated as a resource capability
- `orchestrator` remains resource-scoped
- remove `priority` from `services.surgical-connectivity.constraints`
- remove the extra non-delivery resource examples for now
- strengthen the KP example by adding meaningful delivery resources for Alpha and Gamma instead of unrelated resource types

### Intent
Keep the KP example focused on the current hospital slice use case while reducing duplication and improving realism.

## II MS decision flow baseline

### II MS decision stages
1. Consume validated intent
   - input: `IntentValidatedEvent`
   - II MS reads validated request content, referenced `IntentSpecification`, and KP knowledge

2. Semantic interpretation
   - II MS resolves `location`, `sliceType`, `priority`, `semanticTag`, and service meaning from human/formal/characteristic input
   - KP used: `humanExpressionMapping`, `locations`, `services`, `behaviour`

3. Policy evaluation
   - II MS checks whether the resolved request is allowed
   - KP used: `policyRules`
   - fail -> `IntentRejectedEvent`
   - pass -> continue

4. Candidate discovery
   - II MS determines the applicable resource set for the resolved location/service context
   - KP used: `locations.applicableResourceIds`, global `resources`

5. Optimisation decision
   - II MS decides whether optimisation is required
   - KP used: `optimisationProfiles`, `services`, `resolutionOutput`
   - optimisation required -> emit `IntentResolvedEvent`
   - optimisation not required -> emit `IntentNetworkReadyEvent`

6. Rejection path
   - semantic, policy, or candidate-discovery failure -> emit `IntentRejectedEvent`

7. Re-optimisation trigger path
   - later, after `IntentAssuranceEvent`:
     - non-degraded -> no new `IntentResolvedEvent` required
     - degraded without re-decision need -> no action
     - degraded with re-decision need -> emit new `IntentResolvedEvent`

### II MS stage-to-event mapping table
| Stage | Input | KP sections read | Decision | Output |
|---|---|---|---|---|
| Consume validated intent | `IntentValidatedEvent` | none yet beyond references carried in event | accept for II MS processing | continue internal processing |
| Semantic interpretation | validated request content from `IntentValidatedEvent` | `humanExpressionMapping`, `locations`, `services`, `behaviour` | can II MS resolve meaning, location, service context, and structured fields? | continue or reject |
| Policy evaluation | resolved semantic context | `policyRules` | is the resolved request allowed? | continue or `IntentRejectedEvent` |
| Candidate discovery | resolved and policy-valid request | `locations.applicableResourceIds`, `resources` | what is the applicable candidate set? | continue or reject if no valid candidate set |
| Optimisation decision | resolved request + applicable candidates | `optimisationProfiles`, `services`, `resolutionOutput` | is optimisation required? | `IntentResolvedEvent` or `IntentNetworkReadyEvent` |
| Rejection path | failure from semantic/policy/candidate stage | `resolutionOutput` as needed | rejection reason must be emitted | `IntentRejectedEvent` |
| Re-optimisation trigger path | `IntentAssuranceEvent` | `resources`, `locations`, `optimisationProfiles`, `policyRules` as needed | degraded and re-decision needed? | no action or new `IntentResolvedEvent` |

### II MS decision matrix
| Checkpoint | Yes | No |
|---|---|---|
| Can II MS semantically resolve the request? | continue to policy evaluation | emit `IntentRejectedEvent` |
| Does policy allow the resolved request? | continue to candidate discovery | emit `IntentRejectedEvent` |
| Is there a valid applicable candidate set? | continue to optimisation decision | emit `IntentRejectedEvent` |
| Is optimisation required? | emit `IntentResolvedEvent` | emit `IntentNetworkReadyEvent` |
| Is `IntentAssuranceEvent.lifecycleStatus = Degraded`? | evaluate re-decision need | no action |
| Is re-decision needed? | emit new `IntentResolvedEvent` | no action |

### Output rule by stage
- semantic interpretation fails -> `IntentRejectedEvent`
- policy evaluation fails -> `IntentRejectedEvent`
- candidate discovery finds no valid applicable set -> `IntentRejectedEvent`
- optimisation required -> `IntentResolvedEvent`
- optimisation not required -> `IntentNetworkReadyEvent`
- degraded assurance with re-decision needed -> new `IntentResolvedEvent`

### Important locked behaviour
- non-degraded `IntentAssuranceEvent` does not require a new `IntentResolvedEvent`
- degraded `IntentAssuranceEvent` only drives re-decision when needed
- degraded `candidates`, when present, must include current active resources too

## IA MS decision flow baseline

### IA MS role
IA MS owns:
- apply/orchestration handoff to the network
- runtime assurance truth
- assurance/control-loop monitoring
- internal lifecycle input from network/application outcome
- `IntentAssuranceEvent`

IA MS does not own:
- external intent syntax validation
- semantic interpretation
- policy evaluation
- optimisation decision logic
- external TMF event publication

### IA MS inputs
- `IntentNetworkReadyEvent`
- orchestrator/apply result
- live telemetry / assurance data

### IA MS outputs
- internal lifecycle/status input toward IC MS
- `IntentAssuranceEvent`

### IA MS decision stages
1. Consume network-ready intent
   - input: `IntentNetworkReadyEvent`
   - IA MS reads target, configuration, observability, and references

2. Apply/orchestrate
   - IA MS sends the apply-ready configuration to the orchestrator/network target

3. Receive apply result
   - applied/accepted -> continue to assurance
   - rejected/failed -> emit internal lifecycle/status input toward IC MS

4. Start assurance/control loop
   - IA MS activates monitoring for the configured intent/service context

5. Evaluate runtime assurance state
   - IA MS determines current lifecycle-relevant state, current active resources, evaluations, live metrics, and whether degraded state exists

6. Emit assurance truth
   - IA MS emits `IntentAssuranceEvent`

7. Continue or escalate
   - non-degraded -> continue monitoring
   - degraded without re-decision need -> continue monitoring, report truth
   - degraded with re-decision need -> emit degraded assurance truth and let II MS decide next step

### IA MS stage-to-event mapping table
| Stage | Input | Decision | Output |
|---|---|---|---|
| Consume network-ready intent | `IntentNetworkReadyEvent` | accept for IA MS processing | continue internal processing |
| Apply/orchestrate | target + configuration from `IntentNetworkReadyEvent` | can IA MS submit/apply the requested configuration? | continue or lifecycle/status input toward IC MS |
| Receive apply result | orchestrator/network response | was apply accepted / applied / failed / rejected? | continue to assurance or lifecycle/status input toward IC MS |
| Start assurance loop | observability context + telemetry sources | can assurance/control-loop start? | continue monitoring |
| Evaluate runtime assurance state | live telemetry + current applied state | is service non-degraded or degraded? | `IntentAssuranceEvent` |
| Non-degraded monitoring path | non-degraded assurance state | continue monitoring | `IntentAssuranceEvent` non-degraded form |
| Degraded monitoring path | degraded assurance state | is re-decision needed? | `IntentAssuranceEvent` degraded form |
| Re-decision trigger handoff | degraded assurance with re-decision need | include full applicable re-decision set? | degraded `IntentAssuranceEvent` with `candidates` |

### IA MS decision matrix
| Checkpoint | Yes | No |
|---|---|---|
| Can IA MS accept the `IntentNetworkReadyEvent` for processing? | continue to apply/orchestrate | emit internal lifecycle/status input toward IC MS |
| Did apply/orchestration succeed or get accepted? | start assurance/control loop | emit internal lifecycle/status input toward IC MS |
| Can assurance/control loop start? | continue monitoring | emit internal lifecycle/status input toward IC MS |
| Is current runtime state degraded? | evaluate re-decision need | emit non-degraded `IntentAssuranceEvent` |
| Is re-decision needed? | emit degraded `IntentAssuranceEvent` with `candidates` | emit degraded `IntentAssuranceEvent` without `candidates` |

### Output rule by stage
- apply/orchestration rejected or failed -> internal lifecycle/status input toward IC MS
- apply accepted/applied -> start assurance loop
- non-degraded runtime state -> `IntentAssuranceEvent` without `candidates`
- degraded runtime state without re-decision need -> `IntentAssuranceEvent` without `candidates`
- degraded runtime state with re-decision need -> `IntentAssuranceEvent` with `candidates`

### Important IA MS behaviour
- IA MS is the source of runtime assurance truth
- IA MS does not decide optimisation; II MS does
- IA MS may include `candidates` only when re-decision is needed
- when `candidates` is present, it must include current active resources too

## Intent Callback MS request references baseline

### Rule
Do not include `references` in the `POST /intent/callback/v1/submissions` request body.

### Reason
- caller already supplies `intentId`
- ICB MS can construct internal references if needed
- external/orchestrator callback payload should stay lean
- avoid trusting externally supplied canonical resource URLs

### Request shape direction
The callback submission request should carry:
- `callbackType`
- `correlationId`
- `source`
- `intentId`
- `status`

It should not carry:
- `references`

### Internal event direction
If ICB MS publishes an internal event/message after accepting the callback submission, ICB MS may add `references` internally as part of the trusted internal event shape.

## CB vs ICB MS terminology correction baseline

### Rule
CB and ICB MS are different things.

- `CB` = circuit breaker
- `ICB MS` = Intent Callback MS / `intent-callback-ms`

### Correction
Do not use `CB MS` to mean the callback service going forward.

Use:
- **Intent Callback MS** as the display name
- `intent-callback-ms` as the service name
- **ICB MS** as the short name

### ICB MS role
ICB MS is the incoming-only REST wrapper / callback access mediation service for the Intent Domain.

Canonical flow:

`external client / orchestrator -> gateway -> ICB MS -> Kafka/native broker topics`

### Design consequence
Future caching / circuit-breaker discussions should use `CB` for circuit breaker only, and future callback-service interface/docs should use `ICB MS`.

## Intent Enabler sequence diagram baseline

### Baseline files
- `intent-enabler-sequence-part1-baselined.puml`
- `intent-enabler-sequence-part2-baselined.puml`

### Scope
Part 1 covers IntentSpecification definition through initial assurance.  
Part 2 covers runtime assurance and re-decision.

### Key baseline points
- Domain boxes are colour-coded:
  - Intent Consumer
  - Intent Domain
  - Intent Support Domain
  - Other T7 Entities
- Events/message types are colour-coded with a legend.
- Part 1 includes IA MS subscribing to `t7.telemetry` before applying configuration through `t7.orchestrator`.
- Part 2 includes real-time telemetry streaming from `t7.telemetry` to IA MS during runtime assurance.
- Part 2 includes telemetry subscription refresh after re-decision and before applying updated configuration.

## Intent Enabler sequence diagram refinement baseline

### Updated files
- `intent-enabler-sequence-part1-baselined-v2.puml`
- `intent-enabler-sequence-part2-baselined-v2.puml`

### Refinements applied
- Updated `Other T7 Entities` legend to include `t7.telemetry`.
- Renamed Part 1 apply section to include telemetry subscription.
- Changed telemetry subscription wording from active configuration to intended configuration / resource context.
- Changed Part 2 refresh wording to `Prepare / refresh telemetry subscription for updated configuration`.

## Resource roles field baseline:

### Rule:
`roles` is optional.

Include `roles` only when the resource plays a meaningful role in the current intent context. Omit `roles` when there is no meaningful role. Do not include empty arrays such as `"roles": []`.

### Current controlled vocabulary:
`roles` values remain limited to:
- `primary`
- `secondary`

### Interpretation:
For compute, storage, security, or platform resources, include `roles` only if they genuinely act as `primary` or `secondary` in the current intent context. If richer role types such as `inspection`, `backup-storage`, or `control-plane` are needed later, baseline them explicitly before use.

### Baseline file:
- `resource-roles-field-baseline.md`

# Human Expression Mapping Baseline Addendum

## Purpose:

This addendum makes the human-expression support explicit and searchable in the baseline.

## Rule:

Human expression support is baselined in the lightweight II MS KP / Master Knowledge Config as `humanExpressionMapping`.

The incoming `Intent` may carry a `humanExpression`, but the KP stores interpretation rules, not every user sentence.

## Split:

| Where | What it contains |
|---|---|
| `Intent.humanExpression` | The actual user/business sentence submitted in the intent |
| `humanExpressionMapping` in lightweight II MS KP | Rules, aliases, defaults, and conflict policy for interpreting the sentence |
| `t7.knowledge plane` | External network-related knowledge used during resolution and re-decision |

## Baseline JSON section:

```json
{
  "humanExpressionMapping": {
    "enabled": true,
    "entityAliases": {
      "Sydney Hospital": "AU-NSW-SYD-HOSP-001",
      "Alpha Hospital": "AU-VIC-MEL-HOSP-101",
      "Gamma Hospital": "AU-QLD-BNE-HOSP-201",
      "Beta Hospital": "AU-NSW-NEW-HOSP-301"
    },
    "fieldPatterns": [
      {
        "field": "locationId",
        "matchType": "entityAlias"
      },
      {
        "field": "latency",
        "patterns": [
          {
            "regex": "(?i)latency\\s*(<=|less than or equal to|at most|max(?:imum)? of)\\s*(\\d+)\\s*ms",
            "operator": "<=",
            "valueGroup": 2,
            "unit": "ms"
          }
        ]
      },
      {
        "field": "availability",
        "patterns": [
          {
            "regex": "(?i)availability\\s*(>=|greater than or equal to|at least|min(?:imum)? of)\\s*(\\d+(?:\\.\\d+)?)",
            "operator": ">=",
            "valueGroup": 2,
            "unit": "percent"
          }
        ]
      },
      {
        "field": "sliceType",
        "patterns": [
          {
            "regex": "(?i)surgical connection|surgical slice|surgical urllc",
            "value": "URLLC"
          }
        ]
      },
      {
        "field": "priority",
        "patterns": [
          {
            "regex": "(?i)critical|emergency",
            "value": "CRITICAL"
          },
          {
            "regex": "(?i)high priority|high",
            "value": "HIGH"
          }
        ]
      },
      {
        "field": "semanticTag",
        "patterns": [
          {
            "regex": "(?i)surgical|medical",
            "value": "medical_urllc_critical"
          }
        ]
      }
    ],
    "defaults": {
      "sliceType": "URLLC",
      "priority": "CRITICAL",
      "semanticTag": "medical_urllc_critical"
    },
    "conflictPolicy": {
      "precedence": [
        "formalExpression",
        "characteristic",
        "humanExpression"
      ],
      "onConflict": "reject"
    }
  }
}
```

## Interpretation:

`humanExpressionMapping` is part of the lightweight II MS KP. It supports local semantic resolution, while II MS also calls external `t7.knowledge plane` for network-related topology/resource context and broader network intelligence.
