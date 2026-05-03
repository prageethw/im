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
