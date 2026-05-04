# Context Dump

## Baseline update — KP Master Config and context dump rule:

Date: 2026-05-04T15:06:45.814425Z

### Files:
- `kp_master_config.md`
- `contextdump.md`

### Baseline:
- The II MS lightweight Master Knowledge Config is now baselined in `kp_master_config.md`.
- `applicableResourceIds` is optional.
- Include `applicableResourceIds` only when the location has known applicable resources in the lightweight II MS KP.
- Omit `applicableResourceIds` when none are currently defined.
- Do not use empty arrays such as `"applicableResourceIds": []` by default.
- Going forward, append new baseline changes to the end of `contextdump.md` as the main context file.

### Knowledge-source rule:
II MS uses the lightweight internal KP for local semantic resolution, mappings, policy hints, and service-specific interpretation. II MS also uses external `t7.knowledge plane` for network-related topology/resource context and broader network intelligence. Neither is exposed as external `Intent` or `IntentSpecification`.

## Baseline update — ID MS Design Brief:

Date: 2026-05-04T15:29:35.255523+00:00

### File:
- `id_ms_design_brief.md`

### Baseline:
ID MS / `intent-definition-ms` owns the design-time `IntentSpecification` API contract and hub subscription APIs under `/intentManagement/v5`.

### API coverage:
- `POST /intentSpecification`
- `GET /intentSpecification`
- `GET /intentSpecification/{id}`
- `PUT /intentSpecification/{id}`
- `PATCH /intentSpecification/{id}`
- `DELETE /intentSpecification/{id}`
- `POST /intentSpecification/hub`
- `GET /intentSpecification/hub/{id}`
- `DELETE /intentSpecification/hub/{id}`

### Lifecycle baseline:
`IntentSpecification` lifecycle values are `DRAFT`, `ACTIVE`, and `RETIRED`. There is no `DELETED` lifecycle state. Delete is an operation/outcome, not a lifecycle status.

### Governance baseline:
- `DRAFT` specs can be edited.
- `ACTIVE` specs are immutable.
- `RETIRED` specs are immutable.
- Meaningful change after activation requires a new versioned `IntentSpecification`.
- `PUT` is preferred for deterministic full updates.
- `PATCH` is supported for compatibility but discouraged.

### Boundary:
ID MS validates syntax/resource shape and enforces specification lifecycle/version governance. It does not validate runtime semantic feasibility, policy fulfilment, network topology, optimisation, assurance, telemetry, or callbacks.

## Baseline update — ID MS lifecycle and versioning rules:

Date: 2026-05-04T15:35:23.666295+00:00

### Updated file:
- `id_ms_design_brief.md`

### Baseline:
The ID MS design brief now includes detailed lifecycle and versioning rules for `IntentSpecification`.

### Lifecycle:
Allowed `IntentSpecification.lifecycleStatus` values are `DRAFT`, `ACTIVE`, and `RETIRED`. `DELETED` is not a lifecycle status.

### Versioning:
Each meaningful change after activation requires a new versioned `IntentSpecification`. New versions start as `DRAFT`. Only one version in the same specification family should be `ACTIVE` for new runtime intent creation. Activating a new version retires the previous active version.

### Runtime compatibility:
IC MS validates new runtime `Intent` creation only against `ACTIVE` specifications. Existing intents referencing retired specifications may continue temporarily where safe, but should be migrated or recreated through controlled flow.

