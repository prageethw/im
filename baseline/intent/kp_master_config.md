# kp_master_config.md

## KP master config baseline

```json
{
  "knowledgePlaneConfig": {
    "configId": "hospital-surgical-slice-kp-v1",
    "version": "1.0",
    "domain": "intent-enabler",
    "description": "Compact KP master config containing source-of-truth knowledge for location-based service availability, design-time benchmarks, resource inventory, logical optimiser/orchestrator/observer references, and human expression mapping. Location-based services are keyed by canonical locationId for direct lookup.",
    "locationBasedServices": {
      "AU-NSW-SYD-HOSP-001": {
        "displayName": "Sydney-Main-Hospital",
        "locationType": "hospital",
        "geographicScope": "campus",
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold",
        "capabilityStatus": "available",
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
        "resourceRoles": [
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
        ],
        "redundancyAvailable": true
      },
      "AU-VIC-MEL-HOSP-101": {
        "displayName": "Melbourne-Main-Hospital",
        "locationType": "hospital",
        "geographicScope": "campus",
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold",
        "capabilityStatus": "available",
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
        "resourceRoles": [
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
        ],
        "redundancyAvailable": true
      },
      "AU-QLD-BNE-HOSP-201": {
        "displayName": "Brisbane-Main-Hospital",
        "locationType": "hospital",
        "geographicScope": "campus",
        "serviceType": "surgical-connectivity",
        "serviceClass": "critical-gold",
        "capabilityStatus": "unknown",
        "statusReason": "Surgical critical-gold connectivity is not currently confirmed as available at this location.",
        "resourceIds": [],
        "redundancyAvailable": false
      }
    },
    "resources": {
      "SYD-PRI-01": {
        "resourceId": "SYD-PRI-01",
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceRoles": [
          "primary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-b",
        "benchmarks": {
          "expectedLatencyMs": 7,
          "expectedAvailabilityPercent": 99.996,
          "expectedJitterMs": 1.1,
          "expectedPacketLossPercent": 0.004
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceRoles": [
          "primary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-a",
        "benchmarks": {
          "expectedLatencyMs": 8,
          "expectedAvailabilityPercent": 99.995,
          "expectedJitterMs": 1.5,
          "expectedPacketLossPercent": 0.005
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceRoles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-b",
        "benchmarks": {
          "expectedLatencyMs": 10,
          "expectedAvailabilityPercent": 99.994,
          "expectedJitterMs": 1.8,
          "expectedPacketLossPercent": 0.006
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceRoles": [
          "secondary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-a",
        "benchmarks": {
          "expectedLatencyMs": 9,
          "expectedAvailabilityPercent": 99.997,
          "expectedJitterMs": 1.2,
          "expectedPacketLossPercent": 0.003
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceRoles": [
          "primary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-mel-a",
        "benchmarks": {
          "expectedLatencyMs": 9,
          "expectedAvailabilityPercent": 99.995,
          "expectedJitterMs": 1.4,
          "expectedPacketLossPercent": 0.005
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceRoles": [
          "primary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-mel-a",
        "benchmarks": {
          "expectedLatencyMs": 10,
          "expectedAvailabilityPercent": 99.994,
          "expectedJitterMs": 1.6,
          "expectedPacketLossPercent": 0.006
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceRoles": [
          "secondary"
        ],
        "accessTechnology": "5G",
        "provider": "mobile-access-mel-b",
        "benchmarks": {
          "expectedLatencyMs": 12,
          "expectedAvailabilityPercent": 99.993,
          "expectedJitterMs": 1.9,
          "expectedPacketLossPercent": 0.007
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
        "resourceType": "networkPath",
        "resourceClass": "critical-gold-access",
        "resourceRoles": [
          "secondary"
        ],
        "accessTechnology": "fibre",
        "provider": "fixed-access-mel-b",
        "benchmarks": {
          "expectedLatencyMs": 11,
          "expectedAvailabilityPercent": 99.996,
          "expectedJitterMs": 1.3,
          "expectedPacketLossPercent": 0.004
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
          "Melbourne Hospital": "AU-VIC-MEL-HOSP-101",
          "melbourne-hospital": "AU-VIC-MEL-HOSP-101",
          "Brisbane Hospital": "AU-QLD-BNE-HOSP-201",
          "brisbane-hospital": "AU-QLD-BNE-HOSP-201"
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
    }
  }
}
```

## Baseline notes

- KP contains current available knowledge, not optimiser/orchestrator execution logic.
- `locationBasedServices` entries are keyed by canonical `locationId` for direct 1-to-1 lookup.
- `displayName` holds the friendly location/service label.
- `expressionMapping.humanExpressionMapping.entityAliases` maps human names directly to canonical `locationId`.
- `benchmarks` are design-time known capability values.
- `targets` remain runtime/request/event terminology, not KP terminology.
- `resourceIds` identify resources currently known for a location-based service.
- Resource entries do not repeat `locationId`; location-resource association is derived from `locationBasedServices[locationId].resourceIds`.
- `capabilityStatus` uses `available` or `unknown`.
- Logical references such as `optimiserTarget`, `optimiserModel`, `orchestratorTarget`, `orchestratorProfile`, `observerTarget`, and `observerProfile` are names only, not endpoint/payload/credential details.
- KP does not include `semanticProfile`, `assuranceProfiles`, optimiser objective rules, hops, or service attributes by default.
- KP uses `redundancyAvailable` to describe current redundant resource capability. Human/NLP input may map `redundancyRequired`, but II MS validates it against `redundancyAvailable` and `resourceRoles`.

