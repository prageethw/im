# KP Master Config

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Scope | II MS lightweight Knowledge Plane master config example |
| Source of truth after commit | GitHub `baseline/intent/ii-ms/kp_master_config.md` |

The hospital surgical slice content in this file is example Knowledge Plane data only. It does not limit II MS or KP to a single use case, service domain, location model, resource profile, optimiser target, orchestrator target, or observer profile.

## Table of contents:

- [1. KP master config baseline](#1-kp-master-config-baseline)
- [2. Baseline notes](#2-baseline-notes)


## 1. KP master config baseline

The hospital surgical slice in this file is an illustrative Knowledge Plane example use case used to make the II MS lookup and mapping behaviour concrete. It is not the only supported service domain, location model, service class, resource class, expression mapping profile, optimiser target, orchestrator target, observer target, or deployment profile. Other Knowledge Plane configurations may use different targets, constraints, preferences, resources, service types, and governance profiles while following the same mapping and ownership rules.

```json
{
  "knowledgePlaneConfig": {
    "configId": "hospital-surgical-slice-kp-v1",
    "version": "1.0",
    "domain": "intent-enabler",
    "description": "Compact KP master config containing source-of-truth knowledge for service availability, design-time service benchmarks, resource inventory, logical optimiser/orchestrator/observer references, and human expression mapping.",
    "locationBasedServices": {
      "AU-NSW-SYD-HOSP-001": {
        "displayName": "Sydney-Main-Hospital",
        "locationType": "hospital",
        "geographicScope": "campus",
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold",
        "capabilityStatus": "available",
        "redundancyAvailable": true,
        "optimiserTarget": "t7-gurobi-optimiser",
        "optimiserModel": "gurobi-surgical-slice-resource-selection-v1",
        "orchestratorTarget": "t7-network-orchestrator",
        "orchestratorProfile": "hospital-surgical-slice-apply-v1",
        "observerTarget": "t7-observability-platform",
        "observerProfile": "critical-gold-assurance-observation-v1",
        "benchmarks": {
          "maxLatencyMs": 10,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "roles": [
          "primary",
          "secondary"
        ],
        "accessTechnologies": [
          "5G",
          "fibre"
        ],
        "resourceIds": [
          "SYD-PRI-01",
          "SYD-PRI-02",
          "SYD-SEC-01",
          "SYD-SEC-02"
        ]
      },
      "AU-VIC-MEL-HOSP-101": {
        "displayName": "Melbourne-Main-Hospital",
        "locationType": "hospital",
        "geographicScope": "campus",
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold",
        "capabilityStatus": "available",
        "redundancyAvailable": true,
        "optimiserTarget": "t7-gurobi-optimiser",
        "optimiserModel": "gurobi-surgical-slice-resource-selection-v1",
        "orchestratorTarget": "t7-network-orchestrator",
        "orchestratorProfile": "hospital-surgical-slice-apply-v1",
        "observerTarget": "t7-observability-platform",
        "observerProfile": "critical-gold-assurance-observation-v1",
        "benchmarks": {
          "maxLatencyMs": 12,
          "minAvailabilityPercent": 99.99,
          "maxJitterMs": 2,
          "maxPacketLossPercent": 0.01
        },
        "roles": [
          "primary",
          "secondary"
        ],
        "accessTechnologies": [
          "5G",
          "fibre"
        ],
        "resourceIds": [
          "MEL-PRI-01",
          "MEL-PRI-02",
          "MEL-SEC-01",
          "MEL-SEC-02"
        ]
      },
      "AU-QLD-BNE-HOSP-201": {
        "displayName": "Brisbane-Main-Hospital",
        "locationType": "hospital",
        "geographicScope": "campus",
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold",
        "capabilityStatus": "unknown",
        "redundancyAvailable": false,
        "statusReason": "Surgical critical-gold connectivity is not currently confirmed as available at this location.",
        "resourceIds": []
      }
    },
    "resources": {
      "SYD-PRI-01": {
        "resourceId": "SYD-PRI-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-b",
        "metrics": {
          "benchmark": {
            "latencyMs": 7,
            "availabilityPercent": 99.996,
            "jitterMs": 1.1,
            "packetLossPercent": 0.004
          }
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "SYD-SEC-01"
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
        "accessTechnology": "5G",
        "provider": "mobile-access-a",
        "metrics": {
          "benchmark": {
            "latencyMs": 8,
            "availabilityPercent": 99.995,
            "jitterMs": 1.5,
            "packetLossPercent": 0.005
          }
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "SYD-SEC-02"
          }
        ]
      },
      "SYD-SEC-01": {
        "resourceId": "SYD-SEC-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-b",
        "metrics": {
          "benchmark": {
            "latencyMs": 10,
            "availabilityPercent": 99.994,
            "jitterMs": 1.8,
            "packetLossPercent": 0.006
          }
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "SYD-PRI-01"
          }
        ]
      },
      "SYD-SEC-02": {
        "resourceId": "SYD-SEC-02",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-a",
        "metrics": {
          "benchmark": {
            "latencyMs": 9,
            "availabilityPercent": 99.997,
            "jitterMs": 1.2,
            "packetLossPercent": 0.003
          }
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "SYD-PRI-02"
          }
        ]
      },
      "MEL-PRI-01": {
        "resourceId": "MEL-PRI-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-mel-a",
        "metrics": {
          "benchmark": {
            "latencyMs": 9,
            "availabilityPercent": 99.995,
            "jitterMs": 1.4,
            "packetLossPercent": 0.005
          }
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "MEL-SEC-01"
          }
        ]
      },
      "MEL-PRI-02": {
        "resourceId": "MEL-PRI-02",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "primary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-mel-a",
        "metrics": {
          "benchmark": {
            "latencyMs": 10,
            "availabilityPercent": 99.994,
            "jitterMs": 1.6,
            "packetLossPercent": 0.006
          }
        },
        "relationships": [
          {
            "type": "pairedSecondary",
            "resourceId": "MEL-SEC-02"
          }
        ]
      },
      "MEL-SEC-01": {
        "resourceId": "MEL-SEC-01",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-mel-b",
        "metrics": {
          "benchmark": {
            "latencyMs": 12,
            "availabilityPercent": 99.993,
            "jitterMs": 1.9,
            "packetLossPercent": 0.007
          }
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "MEL-PRI-01"
          }
        ]
      },
      "MEL-SEC-02": {
        "resourceId": "MEL-SEC-02",
        "resourceType": "deliveryResource",
        "resourceClass": "critical-gold",
        "roles": [
          "secondary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-mel-b",
        "metrics": {
          "benchmark": {
            "latencyMs": 11,
            "availabilityPercent": 99.996,
            "jitterMs": 1.3,
            "packetLossPercent": 0.004
          }
        },
        "relationships": [
          {
            "type": "protects",
            "resourceId": "MEL-PRI-02"
          }
        ]
      }
    },
    "expressionMapping": {
      "humanExpressionMapping": {
        "enabled": true,
        "entityAliases": {
          "Sydney Hospital": "AU-NSW-SYD-HOSP-001",
          "sydney-hospital": "AU-NSW-SYD-HOSP-001",
          "Sydney-Main-Hospital": "AU-NSW-SYD-HOSP-001",
          "Melbourne Hospital": "AU-VIC-MEL-HOSP-101",
          "melbourne-hospital": "AU-VIC-MEL-HOSP-101",
          "Melbourne-Main-Hospital": "AU-VIC-MEL-HOSP-101",
          "Brisbane Hospital": "AU-QLD-BNE-HOSP-201",
          "brisbane-hospital": "AU-QLD-BNE-HOSP-201",
          "Brisbane-Main-Hospital": "AU-QLD-BNE-HOSP-201"
        },
        "fieldPatterns": [
          {
            "field": "location.locationId",
            "matchType": "entityAlias"
          },
          {
            "field": "maxLatencyMs",
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
            "field": "minAvailabilityPercent",
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
            "field": "maxJitterMs",
            "patterns": [
              {
                "regex": "(?i)jitter\\s*(<=|less than or equal to|at most|max(?:imum)? of)\\s*(\\d+(?:\\.\\d+)?)\\s*ms",
                "operator": "<=",
                "valueGroup": 2,
                "unit": "ms"
              }
            ]
          },
          {
            "field": "maxPacketLossPercent",
            "patterns": [
              {
                "regex": "(?i)(packet loss|packetloss)\\s*(<=|less than or equal to|at most|max(?:imum)? of)\\s*(\\d+(?:\\.\\d+)?)\\s*%?",
                "operator": "<=",
                "valueGroup": 3,
                "unit": "percent"
              }
            ]
          },
          {
            "field": "serviceType",
            "patterns": [
              {
                "regex": "(?i)surgical connection|surgical slice|surgical connectivity",
                "value": "surgical-connectivity"
              }
            ]
          },
          {
            "field": "serviceClass",
            "patterns": [
              {
                "regex": "(?i)critical gold|critical-gold",
                "value": "critical-gold"
              }
            ]
          },
          {
            "field": "priority",
            "patterns": [
              {
                "regex": "(?i)critical|emergency",
                "value": "critical"
              },
              {
                "regex": "(?i)high priority|high",
                "value": "high"
              },
              {
                "regex": "(?i)standard|normal",
                "value": "standard"
              }
            ]
          },
          {
            "field": "redundancyRequired",
            "patterns": [
              {
                "regex": "(?i)redundant|redundancy|required backup|backup path|secondary path",
                "value": true
              }
            ]
          },
          {
            "field": "preferredAccessTechnology",
            "patterns": [
              {
                "regex": "(?i)5g|mobile",
                "value": "5G"
              },
              {
                "regex": "(?i)fibre|fiber|fixed",
                "value": "fibre"
              }
            ]
          }
        ],
        "defaults": {
          "serviceType": "surgical-connectivity",
          "serviceClass": "critical-gold",
          "priority": "critical",
          "redundancyRequired": true
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
    "preResolutionValidationSources": {
      "notes": "Illustrative pre-resolution validation references only. II MS may consult approved T7 services or other governed sources when a use case requires facts beyond KP. These entries are not endpoint, payload, credential, or ownership definitions.",
      "sourceTypes": [
        "knowledgePlane",
        "inventorySystem",
        "policyService",
        "topologyService",
        "capacitySource",
        "serviceCatalogue",
        "fulfilmentSystem",
        "governedDomainSource"
      ]
    }
  }
}
```

## 2. Baseline notes

- The hospital surgical slice KP data is illustrative example data. It shows one compact knowledge profile, not the only supported II MS resolution model. Other intent domains may require II MS to perform additional pre-resolution validation using approved T7 platform services, inventory systems, policy services, topology sources, capacity systems, service catalogues, fulfilment systems, or other governed domain sources to resolve an admitted intent accurately and meet the intent safely.
- `preResolutionValidationSources` contains illustrative logical pre-resolution validation categories only. It does not define endpoints, credentials, payload contracts, ownership transfer, or a mandatory integration chain. II MS remains responsible for curating and normalising pre-resolution validation facts before emitting internal events.

- KP uses shared resource vocabulary where meaning is not lost: resource entries use `resourceType: "deliveryResource"`, `resourceClass: "critical-gold"`, and `roles`. KP-native reference/capability terminology remains valid for resource `metrics.benchmark.*`, location/service `benchmarks.*`, and `optimiserTarget: "t7-gurobi-optimiser"`.

- KP contains current available knowledge, not optimiser/orchestrator execution logic.
- `locationBasedServices` entries are keyed by canonical `locationId` for direct lookup.
- `displayName` holds the friendly location/service label.
- `expressionMapping.humanExpressionMapping.entityAliases` maps human names directly to canonical `locationId`.
- Location/service `benchmarks` are design-time known service capability values.
- Resource performance values use `metrics.benchmark` for KP/design-time values.
- `targets` remain runtime/request/event terminology, not KP terminology.
- `resourceIds` identify resources currently known for a location-based service.
- Resource entries do not repeat `locationId`; location-resource association is derived from `locationBasedServices[locationId].resourceIds`.
- `capabilityStatus` uses `available` or `unknown`.
- KP uses `redundancyAvailable` to describe current redundant resource capability. Human/NLP input may map `redundancyRequired`, but II MS validates it against `redundancyAvailable` and `roles`.
- Logical references such as `optimiserTarget`, `optimiserModel`, `orchestratorTarget`, `orchestratorProfile`, `observerTarget`, and `observerProfile` are names only, not endpoint, payload, or credential details.
- II MS uses observer references when building `IntentNetworkReadyEvent`; optimisation request and outcome payloads do not carry observability configuration by default.
- Events may map these logical references into nested event-specific configuration structures such as `serviceConfiguration.orchestratorConfiguration.target/profile` and `serviceConfiguration.observerConfiguration.target/profile`.
- KP does not include `semanticProfile`, `assuranceProfiles`, optimiser objective rules, hops, or service attributes by default.
