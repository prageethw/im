# kp_master_config.md

## Purpose:

This file is the baseline lightweight II MS KP / Master Knowledge Config.

II MS uses this lightweight KP for local semantic resolution, mappings, policy hints, and service-specific interpretation.

II MS also uses external `t7.knowledge plane` for network-related topology/resource context and broader network intelligence.

Neither this lightweight KP nor `t7.knowledge plane` is exposed as the external `Intent` or `IntentSpecification`.

## Baseline rules:

- `applicableResourceIds` is optional.
- Include `applicableResourceIds` only when the location has known applicable resources in the lightweight II MS KP.
- Omit `applicableResourceIds` when none are currently defined.
- Do not use empty arrays such as `"applicableResourceIds": []` by default.
- `roles` is optional.
- Include `roles` only when the resource plays a meaningful role in the current intent context.
- Do not use empty arrays such as `"roles": []`.
- Current controlled `roles` values are `primary` and `secondary`.
- `humanExpressionMapping` is explicit under `expressionMapping`.

## Master Knowledge Config:

```json
{
  "knowledgePlaneConfig": {
    "configId": "hospital-surgical-slice-kp-v1",
    "version": "1.0",
    "domain": "intent-enabler",
    "description": "Lightweight II MS KP / Master Knowledge Config for surgical hospital slice intent interpretation.",
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
        }
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
          "semanticTag": "medical_urllc_critical",
          "latencyMs": {
            "operator": "<=",
            "value": 10
          },
          "availabilityPercent": {
            "operator": ">=",
            "value": 99.99
          }
        },
        "policyInputs": {
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
            "value": [
              "CRITICAL",
              "HIGH"
            ]
          }
        ],
        "onFailure": {
          "reasonCode": "POLICY_PRIORITY_NOT_ALLOWED",
          "statusReason": "Requested priority is not allowed for the surgical URLLC profile."
        }
      }
    },
    "resourceCatalogue": {
      "SYD-PRI-01": {
        "resourceId": "SYD-PRI-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
        "locationId": "AU-NSW-SYD-HOSP-001",
        "resourceAttributes": {
          "hops": [
            "fc00:2:2:101",
            "fc00:2:2:210"
          ],
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
        "roles": [
          "primary"
        ],
        "locationId": "AU-NSW-SYD-HOSP-001",
        "resourceAttributes": {
          "hops": [
            "fc00:2:2:105",
            "fc00:2:2:220"
          ],
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
        "roles": [
          "secondary"
        ],
        "locationId": "AU-NSW-SYD-HOSP-001",
        "resourceAttributes": {
          "hops": [
            "fc00:2:2:102",
            "fc00:2:2:211"
          ],
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
        "roles": [
          "secondary"
        ],
        "locationId": "AU-NSW-SYD-HOSP-001",
        "resourceAttributes": {
          "hops": [
            "fc00:2:2:106",
            "fc00:2:2:221"
          ],
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
    "expressionMapping": {
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
                "regex": "(?i)latency\\\\s*(<=|less than or equal to|at most|max(?:imum)? of)\\\\s*(\\\\d+)\\\\s*ms",
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
                "regex": "(?i)availability\\\\s*(>=|greater than or equal to|at least|min(?:imum)? of)\\\\s*(\\\\d+(?:\\\\.\\\\d+)?)",
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
}
```

- Resource performance values use `metrics.benchmark` for KP/design-time values.
