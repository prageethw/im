# Internal Events Baseline Pack

_Regenerated from latest running dump: `new-context-working-v24.md`._

This document consolidates the currently baselined internal events, including full JSON payloads.

## Scope

This pack includes:
- `IntentValidatedEvent`
- `IntentRejectedEvent`
- `IntentResolvedEvent`
- `IntentOptimisedEvent`
- `IntentNetworkReadyEvent`
- `IntentAssuranceEvent`

## Notes

- Event wrapper uses topic, key, CloudEvents-style headers, and `body`.
- `references` stays at the tail of `body`.
- Canonical terminology direction:
  - `location.locationId`
  - `service.serviceClass`
  - `resources`
  - `metrics`
  - `targets`
  - `evaluations`
  - `priority`
- Do not use as active attribute names unless discussing legacy history:
  - `primaryPathId`
  - `secondaryPathId`
  - `paths`
  - `observedOutcome`
  - `expectations`
  - `priority_level`

---

## IntentValidatedEvent

### Summary
Internal event emitted by IC MS after syntactic validation succeeds on `POST /intentManagement/v5/intent`. It is the handoff from IC MS to II MS for downstream semantic and policy processing.

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

---

## IntentRejectedEvent

### Summary
Internal event emitted by II MS when semantic and/or policy validation fails after consuming `IntentValidatedEvent`.

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

---

## IntentResolvedEvent

### Summary
Internal event emitted by II MS when semantic interpretation and policy validation succeed and the intent needs optimisation.

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

---

## IntentOptimisedEvent

### Summary
Internal event emitted by the optimiser after consuming `IntentResolvedEvent` and successfully completing optimisation.

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

---

## IntentNetworkReadyEvent

### Summary
Internal event emitted by II MS when the intent is ready for application in the network.

```json
{
  "topic": "t7.intent.management.events",
  "key": "INT-HOSP-2026-001",
  "headers": {
    "content-type": "application/json",
    "ce_specversion": "1.0",
    "ce_type": "IntentNetworkReadyEvent",
    "ce_source": "intent-intelligence-ms",
    "ce_id": "EVT-INT-HOSP-2026-001-NET-0001",
    "ce_time": "2026-04-17T10:00:45+10:00",
    "ce_subject": "INT-HOSP-2026-001",
    "ce_datacontenttype": "application/json",
    "ce_correlationid": "INT-HOSP-2026-001-INIT"
  },
  "body": {
    "eventType": "IntentNetworkReadyEvent",
    "eventVersion": "1.0",
    "source": "intent-intelligence-ms",
    "eventTime": "2026-04-17T10:00:45+10:00",
    "correlationId": "INT-HOSP-2026-001-INIT",
    "intentId": "INT-HOSP-2026-001",
    "location": {
      "locationId": "AU-NSW-SYD-HOSP-001"
    },
    "service": {
      "serviceClass": "critical-gold"
    },
    "target": {
      "orchestrator": "ORCHESTRATOR_SYDNEY_ZONE"
    },
    "configuration": {
      "trafficClass": "URLLC-Gold",
      "resources": [
        {
          "roles": ["primary"],
          "resourceId": "PATH-SYD-HOSP-001-A",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "hops": [
              "fc00:2:2:101",
              "fc00:2:2:210"
            ]
          },
          "relationships": [
            {
              "type": "disjointFrom",
              "targetResourceId": "PATH-SYD-HOSP-001-B"
            }
          ]
        },
        {
          "roles": ["secondary"],
          "resourceId": "PATH-SYD-HOSP-001-B",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001",
            "hops": [
              "fc00:2:2:102",
              "fc00:2:2:211"
            ]
          },
          "relationships": [
            {
              "type": "disjointFrom",
              "targetResourceId": "PATH-SYD-HOSP-001-A"
            }
          ]
        }
      ]
    },
    "observability": {
      "telemetrySink": "PROMETHEUS_SYDNEY_CLUSTER",
      "monitoringProfile": "URLLC_SURGICAL_HIGH_FIDELITY",
      "resources": [
        {
          "roles": ["primary"],
          "resourceId": "PATH-SYD-HOSP-001-A",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          }
        },
        {
          "roles": ["secondary"],
          "resourceId": "PATH-SYD-HOSP-001-B",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          }
        },
        {
          "roles": ["secondary"],
          "resourceId": "PATH-SYD-HOSP-001-C",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-silver",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          }
        },
        {
          "roles": ["primary"],
          "resourceId": "PATH-SYD-HOSP-001-D",
          "resourceType": "deliveryResource",
          "resourceClass": "critical-gold",
          "resourceAttributes": {
            "locationId": "AU-NSW-SYD-HOSP-001"
          }
        }
      ]
    },
    "references": {
      "intent": "https://mycsp.com.au/intentManagement/v5/intent/INT-HOSP-2026-001",
      "intentSpecification": "https://mycsp.com.au/intentManagement/v5/intentSpecification/hospital-surgical-slice-spec-v1.19"
    }
  }
}
```

---

## IntentAssuranceEvent

### Summary
Shared internal assurance truth event consumed by both II MS and IC MS.

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
