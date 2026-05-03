# KP Baseline Pack

This document consolidates the currently baselined **Master Knowledge Config / KP** contents in Markdown, including the agreed JSON payloads and naming decisions.

## Scope

This pack includes:
- KP / Master Knowledge Config purpose and boundary
- top-level KP structure
- location model
- global resource model
- policy rules
- optimisation profiles
- human expression mapping
- behaviour
- resolution output
- full hospital-slice KP example

## Notes

- KP is internal II MS knowledge, not an external Intent resource.
- Intent / IntentSpecification remains the external contract side.
- KP provides internal semantic, policy, resource, and optimisation knowledge used by II MS.
- Canonical working format is Markdown.

---

# 1. KP purpose and boundary

## Purpose
Static knowledge-plane config that II MS uses for:
- semantic interpretation
- policy evaluation
- candidate discovery
- optimisation preparation

## KP is not for
- live runtime state
- current assurance truth
- active network measurements
- transient event context

## Separation from intent
- **Intent / IntentSpecification**
  - requester-facing contract and syntax
- **KP / Master Knowledge Config**
  - internal fulfilment knowledge for II MS

---

# 2. KP top-level structure

```json
{
  "version": "1.0",
  "locations": {},
  "services": {},
  "policyRules": {},
  "resources": {},
  "observabilityProfiles": {},
  "optimisationProfiles": {},
  "humanExpressionMapping": {},
  "behaviour": {},
  "resolutionOutput": {}
}
```

## Naming decisions
- use `policyRules`, not `policy`
- use `resources`, not `resourceCatalog`
- use `sliceType` as canonical where the platform controls the contract
- keep prior observability-related naming as drafted for now

---

# 3. KP model decisions

## Locked decisions
- `resourceAttributes.surgicalCapable` is treated as a **resource capability**
- `orchestrator` remains **resource-scoped**
- `resources` stays **global**
- `locations.applicableResourceIds` provides the scoping link
- one location can map to many resource types and classes
- remove `priority` from `services.surgical-connectivity.constraints`
- keep the current KP example focused on the hospital slice use case
- use meaningful delivery resources for Alpha and Gamma rather than unrelated example resource types

---

# 4. Locations model

## Purpose
Static location knowledge for semantic resolution, scoping, and candidate discovery.

## Shape
```json
{
  "locations": {
    "AU-NSW-SYD-HOSP-001": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "name": "Sydney Hospital",
      "locationType": "HOSPITAL",
      "geographicScope": "AU-NSW-SYD",
      "applicableResourceIds": [
        "SYD-PRI-01",
        "SYD-PRI-02",
        "SYD-BAK-01",
        "SYD-BAK-02"
      ],
      "observabilityProfileId": "URLLC_SURGICAL_HIGH_FIDELITY",
      "optimisationProfileIds": [
        "SURGICAL_JOINT",
        "LOWEST_LATENCY"
      ]
    }
  }
}
```

## Meaning
- `locationId` = canonical location identifier
- `locationType` = canonical type for semantic/policy checks
- `geographicScope` = broader area/scope
- `applicableResourceIds` = resource ids scoped to this location

---

# 5. Resources model

## Purpose
Internal candidate resource knowledge used by II MS for discovery and optimisation preparation.

## Shape
```json
{
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
    }
  }
}
```

## Meaning
- `resourceType` = kind of resource
- `resourceClass` = capability/service class
- `roles` = role such as `primary` / `secondary`
- `locationId` = scope/location link
- `metrics` here are **benchmark/static KP metrics**, not live runtime values

---

# 6. Policy rules

## Purpose
Internal rules II MS uses for semantic/policy decisions after syntax validation.

```json
{
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
    }
  }
}
```

---

# 7. Optimisation profiles

## Purpose
Internal optimisation knowledge II MS can reference when preparing or selecting optimisation behaviour.

```json
{
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
  }
}
```

---

# 8. Human expression mapping

## Purpose
Internal mapping knowledge II MS uses to convert human phrasing into structured semantic fields.

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
        "field": "sliceType",
        "patterns": [
          {
            "regex": "(?i)surgical connection|surgical slice|surgical urllc",
            "value": "URLLC"
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
  }
}
```

---

# 9. Behaviour and resolution output

## Behaviour
```json
{
  "behaviour": {
    "latencyOperator": "max",
    "availabilityOperator": "min",
    "onInvalidExpression": "reject",
    "resolveLocationFromHumanExpression": true
  }
}
```

## Resolution output
```json
{
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

---

# 10. Full KP baseline example

```json
{
  "version": "1.0",

  "locations": {
    "AU-NSW-SYD-HOSP-001": {
      "locationId": "AU-NSW-SYD-HOSP-001",
      "name": "Sydney Hospital",
      "locationType": "HOSPITAL",
      "geographicScope": "AU-NSW-SYD",
      "applicableResourceIds": [
        "SYD-PRI-01",
        "SYD-PRI-02",
        "SYD-BAK-01",
        "SYD-BAK-02"
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
      "applicableResourceIds": [
        "ALPHA-PRI-01",
        "ALPHA-PRI-03",
        "ALPHA-BAK-01",
        "ALPHA-BAK-03"
      ],
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
      "applicableResourceIds": [
        "GAMMA-PRI-01",
        "GAMMA-PRI-02",
        "GAMMA-BAK-01",
        "GAMMA-BAK-02"
      ],
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
      "applicableResourceIds": []
    }
  },

  "services": {
    "surgical-connectivity": {
      "serviceId": "surgical-connectivity",
      "name": "Surgical Connectivity Service",
      "serviceClass": "critical-gold",
      "locationTypes": ["HOSPITAL"],
      "constraints": {
        "sliceType": "URLLC",
        "trafficClass": "URLLC-Gold",
        "semanticTag": "medical_urllc_critical"
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

    "ALPHA-PRI-01": {
      "resourceId": "ALPHA-PRI-01",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["primary"],
      "locationId": "AU-VIC-MEL-HOSP-101",
      "resourceAttributes": {
        "hops": ["fc00:1:1:701", "fc00:1:1:810"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_SOUTH_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "ALPHA-BAK-01"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 6.2
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.995
        }
      ]
    },
    "ALPHA-PRI-03": {
      "resourceId": "ALPHA-PRI-03",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["primary"],
      "locationId": "AU-VIC-MEL-HOSP-101",
      "resourceAttributes": {
        "hops": ["fc00:1:1:709", "fc00:1:1:830"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_SOUTH_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "ALPHA-BAK-03"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 6.8
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.993
        }
      ]
    },
    "ALPHA-BAK-01": {
      "resourceId": "ALPHA-BAK-01",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["secondary"],
      "locationId": "AU-VIC-MEL-HOSP-101",
      "resourceAttributes": {
        "hops": ["fc00:1:1:702", "fc00:1:1:811"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_SOUTH_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "ALPHA-PRI-01"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 7.8
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.994
        }
      ]
    },
    "ALPHA-BAK-03": {
      "resourceId": "ALPHA-BAK-03",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["secondary"],
      "locationId": "AU-VIC-MEL-HOSP-101",
      "resourceAttributes": {
        "hops": ["fc00:1:1:710", "fc00:1:1:831"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_SOUTH_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "ALPHA-PRI-03"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 8.4
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.992
        }
      ]
    },

    "GAMMA-PRI-01": {
      "resourceId": "GAMMA-PRI-01",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["primary"],
      "locationId": "AU-QLD-BNE-HOSP-201",
      "resourceAttributes": {
        "hops": ["fc00:3:3:101", "fc00:3:3:210"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_NORTH_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "GAMMA-BAK-01"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 5.9
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.996
        }
      ]
    },
    "GAMMA-PRI-02": {
      "resourceId": "GAMMA-PRI-02",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["primary"],
      "locationId": "AU-QLD-BNE-HOSP-201",
      "resourceAttributes": {
        "hops": ["fc00:3:3:105", "fc00:3:3:220"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_NORTH_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "GAMMA-BAK-02"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 9.1
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.992
        }
      ]
    },
    "GAMMA-BAK-01": {
      "resourceId": "GAMMA-BAK-01",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["secondary"],
      "locationId": "AU-QLD-BNE-HOSP-201",
      "resourceAttributes": {
        "hops": ["fc00:3:3:102", "fc00:3:3:211"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_NORTH_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "GAMMA-PRI-01"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 6.5
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.995
        }
      ]
    },
    "GAMMA-BAK-02": {
      "resourceId": "GAMMA-BAK-02",
      "resourceType": "deliveryResource",
      "resourceClass": "critical-gold",
      "roles": ["secondary"],
      "locationId": "AU-QLD-BNE-HOSP-201",
      "resourceAttributes": {
        "hops": ["fc00:3:3:106", "fc00:3:3:221"],
        "surgicalCapable": true,
        "status": "Baseline",
        "orchestrator": "ORCHESTRATOR_NORTH_ZONE"
      },
      "relationships": [
        {
          "type": "disjointFrom",
          "targetResourceId": "GAMMA-PRI-02"
        }
      ],
      "metrics": [
        {
          "name": "latencyBenchmarkMs",
          "value": 9.8
        },
        {
          "name": "reliabilityBenchmarkPercent",
          "value": 99.991
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
            "regex": "(?i)latency\s*(<=|less than or equal to|at most|max(?:imum)? of)\s*(\d+)\s*ms",
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
            "regex": "(?i)availability\s*(>=|greater than or equal to|at least|min(?:imum)? of)\s*(\d+(?:\.\d+)?)",
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

---

# 11. Completion status

This KP baseline currently covers:
- top-level KP structure
- locations
- services
- policy rules
- global resources
- observability profiles
- optimisation profiles
- human expression mapping
- behaviour
- resolution output
- hospital-slice internal KP example
