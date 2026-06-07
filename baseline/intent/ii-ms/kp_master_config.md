# KP Master Config

| **Document status** | **Value** |
| --- | --- |
| Status | Current baseline |
| Scope | II MS lightweight Knowledge Plane master config example |
| Source of truth after commit | GitHub `baseline/intent/ii-ms/kp_master_config.md` |

## Table of contents:

- [1. KP master config baseline:](#1-kp-master-config-baseline)
- [2. Baseline notes:](#2-baseline-notes)
- [3. Freshness, cache, and invalidation policy:](#3-freshness-cache-and-invalidation-policy)
- [4. Candidate fact model and degraded lookup support:](#4-candidate-fact-model-and-degraded-lookup-support)
- [5. Fail-closed and audit rules:](#5-fail-closed-and-audit-rules)
- [6. Observability expectations:](#6-observability-expectations)


## 1. KP master config baseline:

The baseline surgical hospital slice in this file is an illustrative Knowledge Plane example used to make the II MS lookup and mapping behaviour concrete. It is not the only supported service domain, location model, service class, resource class, expression mapping profile, optimiser target, orchestrator target, observer target, or deployment profile. Other Knowledge Plane configurations may use different targets, constraints, preferences, resources, service types, and governance profiles while following the same mapping and ownership rules.

```json
{
  "knowledgePlaneConfig": {
    "configId": "hospital-surgical-slice-kp-v1",
    "version": "1.0",
    "domain": "intent-enabler",
    "description": "Compact KP master config containing source-of-truth knowledge for service availability, design-time service benchmarks, resource inventory, logical optimiser and orchestrator/observer references, and human expression mapping.",
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

## 2. Baseline notes:

- The hospital surgical slice KP data is illustrative. It shows one compact knowledge profile, not the only supported II MS resolution model. Other intent domains may require II MS to perform additional pre-resolution validation using approved T7 platform services, inventory systems, policy services, topology sources, capacity systems, service catalogues, fulfilment systems, or other governed domain sources to resolve an admitted intent accurately and meet the intent safely.
- `preResolutionValidationSources` contains illustrative logical pre-resolution validation categories only. It does not define endpoints, credentials, payload contracts, ownership transfer, or a mandatory integration chain. II MS remains responsible for curating and normalising pre-resolution validation facts before emitting internal events.

- KP uses shared resource vocabulary where meaning is not lost: resource entries use `resourceType: "deliveryResource"`, `resourceClass: "critical-gold"`, and `roles`. KP-native reference and capability terminology remains valid for resource `metrics.benchmark.*`, location and service `benchmarks.*`, and `optimiserTarget: "t7-gurobi-optimiser"`.

- KP contains current available knowledge, not optimiser and orchestrator execution logic.
- `locationBasedServices` entries are keyed by canonical `locationId` for direct lookup.
- `displayName` holds the friendly location and service label.
- `expressionMapping.humanExpressionMapping.entityAliases` maps human names directly to canonical `locationId`.
- Location and service `benchmarks` are design-time known service capability values.
- Resource performance values use `metrics.benchmark` for KP and design-time values.
- `targets` remain runtime, request, and event terminology, not KP terminology.
- `resourceIds` identify resources currently known for a location-based service.
- Resource entries do not repeat `locationId`; location-resource association is derived from `locationBasedServices[locationId].resourceIds`.
- `capabilityStatus` uses `available` or `unknown`.
- KP uses `redundancyAvailable` to describe current redundant resource capability. Human and NLP input may map `redundancyRequired`, but II MS validates it against `redundancyAvailable` and `roles`.
- Logical references such as `optimiserTarget`, `optimiserModel`, `orchestratorTarget`, `orchestratorProfile`, `observerTarget`, and `observerProfile` are names only, not endpoint, payload, or credential details.
- Events may map these logical references into nested event-specific configuration structures such as `serviceConfiguration.orchestratorConfiguration.target and profile` and `serviceConfiguration.observerConfiguration.target and profile`.
- KP does not include `semanticProfile`, `assuranceProfiles`, optimiser objective rules, hops, or service attributes by default.

## 3. Freshness, cache, and invalidation policy:

KP master config provides governed reference knowledge for II MS resolution and service-ready preparation. II MS may cache KP facts, but cached facts must remain bounded, version-aware, and safe for runtime use.

Freshness baseline:

| Area | Baseline |
|---|---|
| Config identity | `knowledgePlaneConfig.configId` and `knowledgePlaneConfig.version` identify the governed KP configuration snapshot. |
| Location service facts | Use only when the location service entry is present, enabled by policy, and within the configured freshness window. |
| Resource facts | Use only when every referenced `resourceId` can be resolved to a current resource entry. |
| Candidate set freshness | II MS must evaluate candidate resources against the current KP snapshot before emitting `IntentResolvedEvent` or packaging `IntentNetworkReadyEvent`. |
| Optimisation wait window | If optimisation wait time exceeds the configured freshness threshold, II MS must refresh or re-check the KP snapshot before packaging `IntentNetworkReadyEvent`. |
| Degraded control-loop lookup | For degraded-state handling, II MS must use a fresh or policy-accepted KP snapshot before reselection or re-optimisation. |

Cache baseline:

- KP cache entries must be keyed by config identity, location id, service type, service class, and any other scope field that changes the candidate set.
- Cache entries must retain the KP config version used to produce the cached facts.
- Cache TTL must be bounded and shorter for runtime control-loop use than for low-risk discovery or design-time browsing.
- Client or service logic may bypass cache when a safety-critical decision requires a fresh KP read.
- Cache miss, cache refresh failure, and stale-cache use must be observable.

Invalidation baseline:

- KP config version change invalidates cached location service facts and resource facts for the affected scope.
- Resource availability, resource metric benchmark, role, relationship, or capability changes invalidate the affected resource and candidate-set cache entries.
- Location service capability status changes invalidate the affected location service cache entry.
- Policy changes that affect eligibility, redundancy, target support, or service class support invalidate the affected candidate sets.
- If invalidation cannot be confirmed, II MS must treat the affected safety-critical lookup as stale and follow the fail-closed rules.

## 4. Candidate fact model and degraded lookup support:

II MS uses KP facts to construct the applicable candidate resource set for semantic resolution, service-ready preparation, and degraded-state control-loop evaluation.

Candidate fact baseline:

| Fact | Source in this config | Event-facing treatment |
|---|---|---|
| Location identity | `locationBasedServices` key | Maps to `expression.context.constraints.location.locationId`. |
| Service type | `locationBasedServices[locationId].serviceType` | Maps to `expression.context.constraints.serviceType`. |
| Service class | `locationBasedServices[locationId].serviceClass` | Maps to `expression.context.constraints.serviceClass`. |
| Capability status | `capabilityStatus` | Used by II MS to accept, reject, or fail closed. |
| Redundancy availability | `redundancyAvailable` and resource `roles` | Used to validate `redundancyRequired`. |
| Candidate resources | `resourceIds` plus `resources` entries | Maps to `IntentResolvedEvent.resources[]` and optimiser request candidate resources. |
| Design-time benchmarks | `benchmarks` and `metrics.benchmark` | Maps to neutral metric fields in II-owned events where applicable. |
| Optimiser target | `optimiserTarget` and `optimiserModel` | Used to select the governed optimiser path, not exposed as credentials or endpoint detail. |
| Orchestrator and observer references | `orchestratorTarget`, `orchestratorProfile`, `observerTarget`, `observerProfile` | Maps to `IntentNetworkReadyEvent.serviceConfiguration` target and profile fields. |

Degraded lookup baseline:

- `IntentAssuranceEvent` with `lifecycleStatus: Degraded` may cause II MS degraded-state control-loop handling.
- During degraded-state handling, II MS must correlate `intentId`, `intentVersion`, location, service type, service class, current observed resources, and KP candidate facts.
- II MS must not treat `Failed`, `Terminated`, or `Paused` assurance outcomes as default KP reselection triggers.
- II MS must not resume paused network or service execution.
- II MS may use KP candidate facts to reselect or re-optimise only when degraded-state policy allows it.
- II MS must use the full relevant candidate set known in KP for the applicable location and service context after scope and policy filtering.
- If the degraded resource is no longer present, no longer eligible, or the KP snapshot is stale, II MS must fail closed or route to governed operational handling according to policy.

## 5. Fail-closed and audit rules:

KP lookups that affect safety-critical runtime decisions must fail closed when the governing facts are missing, stale, contradictory, or not trusted.

Fail-closed examples:

- Requested `locationId` cannot be found.
- Location service `capabilityStatus` is `unknown` for the requested service context.
- `redundancyRequired` is true, but `redundancyAvailable` is false or the candidate set lacks suitable primary and secondary roles.
- A referenced resource id is missing from `resources`.
- KP config version cannot be confirmed.
- KP cache is stale and cannot be refreshed within policy.
- KP candidate facts changed while optimisation or service-ready packaging was in progress.
- Degraded-state control-loop handling cannot confirm a fresh applicable candidate set.

Audit baseline:

- Record the KP config id and version used for each semantic decision.
- Record freshness decision, cache hit or miss, and invalidation status where relevant.
- Record location id, service type, service class, and candidate resource ids used for the decision.
- Record fail-closed reasons using intent-domain reason codes such as `KNOWLEDGE_LOOKUP_ERROR`, `SEMANTIC_LOCATION_UNSUPPORTED`, or `SEMANTIC_INTENT_CONTRADICTORY`.
- Do not record credentials, endpoint secrets, raw upstream system payloads, or unrestricted inventory dumps in II-owned events.

## 6. Observability expectations:

KP-related behaviour must be visible enough for II MS operators and platform owners to understand resolution quality, freshness, and control-loop safety.

Recommended signals:

```text
ii_ms_kp_lookup_count
ii_ms_kp_lookup_error_count
ii_ms_kp_cache_hit_count
ii_ms_kp_cache_miss_count
ii_ms_kp_cache_stale_count
ii_ms_kp_refresh_count
ii_ms_kp_refresh_failure_count
ii_ms_kp_invalidation_count
ii_ms_kp_candidate_set_size
ii_ms_kp_fail_closed_count
ii_ms_degraded_kp_lookup_count
ii_ms_degraded_reselection_allowed_count
ii_ms_degraded_reselection_blocked_count
```

Logs and traces should include `correlationId`, `intentId`, `intentVersion`, `configId`, KP config version, location id, service type, service class, and decision outcome where available.

KP observability must not expose credentials, unrestricted raw KP payloads, raw inventory dumps, optimiser internals, or customer-sensitive data outside approved operational identifiers.
