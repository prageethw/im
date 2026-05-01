# Resource Roles Field Baseline

## Rule:

`roles` is optional.

Include `roles` only when the resource plays a meaningful role in the current intent context.

Omit `roles` when there is no meaningful role.

Do not include empty arrays such as:

```json
"roles": []
```

## Current controlled vocabulary:

For now, the controlled vocabulary for `roles` remains:

```json
["primary", "secondary"]
```

## Interpretation:

- Use `roles: ["primary"]` when the resource is the primary resource for the current intent context.
- Use `roles: ["secondary"]` when the resource is the secondary or backup resource for the current intent context.
- For compute, storage, security, or platform resources, include `roles` only if they genuinely act as `primary` or `secondary` in the current intent context.
- If later we need richer role types such as `inspection`, `backup-storage`, or `control-plane`, baseline them explicitly before using them.

## Example with role:

```json
{
  "resourceId": "SYD-STO-01",
  "resourceType": "storageResource",
  "resourceClass": "critical-gold",
  "roles": ["primary"],
  "locationId": "AU-NSW-SYD-HOSP-001"
}
```

## Example without role:

```json
{
  "resourceId": "SYD-CMP-01",
  "resourceType": "computeResource",
  "resourceClass": "critical-gold",
  "locationId": "AU-NSW-SYD-HOSP-001"
}
```
