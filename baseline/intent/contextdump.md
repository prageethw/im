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

