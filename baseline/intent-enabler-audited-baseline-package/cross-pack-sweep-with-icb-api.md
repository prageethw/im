# Cross-Pack Sweep Including ICB MS API Contract

## id-ms-baseline-specification-complete-samples-v2.md:
- `slice_type` found:
  - line 484: `"name": "slice_type",`
  - line 653: `"name": "slice_type",`
  - line 855: `"name": "slice_type",`
  - line 1042: `"name": "slice_type",`
  - line 1315: `"name": "slice_type",`

## ic-ms-baseline-specification-complete-samples-v4.md:
- `slice_type` found:
  - line 114: `"name": "slice_type",`
  - line 208: `"name": "slice_type",`
  - line 334: `"name": "slice_type",`
  - line 538: `"name": "slice_type",`
  - line 632: `"name": "slice_type",`
  - line 787: `"name": "slice_type",`
  - line 1337: `"name": "slice_type",`
  - line 1446: `"name": "slice_type",`
- `serviceType` found:
  - line 34: `- `serviceType` is removed from active payloads.`
- `primaryPathId` found:
  - line 28: `- `primaryPathId``
- `secondaryPathId` found:
  - line 29: `- `secondaryPathId``
- `observedOutcome` found:
  - line 31: `- `observedOutcome``
  - line 1047: `- `observedOutcome``
- `expectations` found:
  - line 32: `- `expectations``
  - line 1048: `- `expectations``
- `priority_level` found:
  - line 33: `- `priority_level``

## internal-events-baseline-pack-complete-v3.md:
- `slice_type` found:
  - line 110: `"name": "slice_type",`
  - line 158: `"characteristic[slice_type]",`
  - line 166: `"slice_type",`
- `primaryPathId` found:
  - line 30: `- `primaryPathId``
- `secondaryPathId` found:
  - line 31: `- `secondaryPathId``
- `observedOutcome` found:
  - line 33: `- `observedOutcome``
- `expectations` found:
  - line 34: `- `expectations``
- `priority_level` found:
  - line 35: `- `priority_level``

## ontology-dictionary-baseline-v5.md:
- `serviceType` found:
  - line 265: `- `serviceType``
  - line 279: `- use `service.serviceClass` not `serviceType``
  - line 380: `- `serviceType``
- `primaryPathId` found:
  - line 51: `**Replaces:** `primaryPathId`, `secondaryPathId`, `paths``
  - line 259: `- `primaryPathId``
  - line 274: `- use `resources` not `primaryPathId` / `secondaryPathId` / `paths``
  - line 374: `- `primaryPathId``
- `secondaryPathId` found:
  - line 51: `**Replaces:** `primaryPathId`, `secondaryPathId`, `paths``
  - line 260: `- `secondaryPathId``
  - line 274: `- use `resources` not `primaryPathId` / `secondaryPathId` / `paths``
  - line 375: `- `secondaryPathId``
- `observedOutcome` found:
  - line 262: `- `observedOutcome``
  - line 276: `- use `metrics` not `observedOutcome``
  - line 377: `- `observedOutcome``
- `expectations` found:
  - line 95: `**Replaces:** `expectations``
  - line 263: `- `expectations``
  - line 277: `- use `targets` not `expectations``
  - line 378: `- `expectations``
- `priority_level` found:
  - line 116: `**Replaces:** `priority_level``
  - line 264: `- `priority_level``
  - line 278: `- use `priority` not `priority_level``
  - line 379: `- `priority_level``

## kp-baseline-pack.md:
- No active terminology mismatches found.

## ii-ms-baseline-pack.md:
- No active terminology mismatches found.

## ia-ms-baseline-pack-v2.md:
- No active terminology mismatches found.

## icb-ms-baseline-pack-v2.md:
- `CB MS` found:
  - line 1: `# ICB MS Baseline Pack`
  - line 3: `This document consolidates the currently baselined **ICB MS** role and interface boundary.`
  - line 8: `- ICB MS role and purpose`
  - line 10: `- what ICB MS does and does not own`
  - line 12: `- canonical ICB MS interfaces`
  - line 20: `- `ICB MS` means Intent Callback MS / `intent-callback-ms`.`
  - line 24: `# 1. ICB MS role:`
  - line 26: `ICB MS is the incoming-only REST wrapper / callback access mediation layer for the Intent Domain.`

## end-to-end-platform-flow-pack.md:
- No active terminology mismatches found.

## baseline-pack-index-v9.md:
- `CB MS` found:
  - line 29: `- ICB MS incoming-only REST wrapper / callback access mediation role, interface boundary, and concrete API contract`
  - line 43: `8. ICB MS baseline pack`

## API contract checks:
- PASS — ICB API includes POST submissions
- PASS — ICB API includes health endpoint
- PASS — ICB request omits references
- PASS — ICB health uses intent-callback-ms service name

## Verdict:
Needs fixes.