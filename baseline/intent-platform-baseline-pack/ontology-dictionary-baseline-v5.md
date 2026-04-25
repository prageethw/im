# Ontology Dictionary — Baseline Terms

_Regenerated against latest running dump: `new-context-working-v29.md`._

This dictionary captures the currently agreed canonical terminology, the intended meaning of each term, where it is used, and any legacy or replaced terms that should not be used as active attribute names.

## Usage rules

- Use **canonical** terms in active payloads, events, and interface examples.
- Use **legacy/replaced** terms only when discussing historical artifacts or explaining a rename.
- Where an external standard or external contract requires a specific field, preserve that field in that external contract only.

---

## 1. Core location and service terms

### `location`
**Meaning:** Generic top-level context for where the intent or event applies.  
**Where used:** Internal events and platform-controlled payloads.  
**Canonical fields:** `location.locationId`  
**Notes:** Preferred common internal term.

### `locationId`
**Meaning:** Stable identifier for the relevant location.  
**Where used:** Internal events, resource attributes, platform-controlled payloads.

### `service`
**Meaning:** Top-level service context block.  
**Where used:** Internal events.  
**Canonical fields:** `service.serviceClass`

### `serviceClass`
**Meaning:** Canonical active service classification used in internal events and platform-controlled payloads.  
**Where used:** Internal events, assurance, optimisation, network-ready payloads.  
**Legacy/replaced:** `serviceType`  
**Rule:** Do not use `serviceType` as an active field unless a real consumer need appears later.

### `geo_location`
**Meaning:** External contract field carrying structured location data in TMF-facing intent payloads.  
**Where used:** External `Intent` / `IntentSpecification` related payloads.  
**Status:** Allowed and preserved where externally appropriate.  
**Notes:** Not an automatic replacement target.

---

## 2. Resource model terms

### `resources`
**Meaning:** Canonical reusable list of selected, current, candidate, configured, or monitored resources.  
**Where used:** Internal events, configuration blocks, observability blocks, assurance blocks.  
**Replaces:** `primaryPathId`, `secondaryPathId`, `paths`

### `roles`
**Meaning:** Role of a resource within a resource set.  
**Where used:** Resource entries.  
**Canonical values:** `primary`, `secondary`

### `resourceId`
**Meaning:** Identifier of a concrete resource.  
**Where used:** Resource entries.

### `resourceType`
**Meaning:** Type/category of resource.  
**Where used:** Resource entries.  
**Typical values used so far:** `deliveryResource`

### `resourceClass`
**Meaning:** Runtime or intended class/profile of the resource.  
**Where used:** Resource entries.

### `resourceAttributes`
**Meaning:** Additional concrete attributes of a resource.  
**Where used:** Resource entries.  
**Examples:** `locationId`, `hops`

### `relationships`
**Meaning:** Explicit resource-to-resource relationships when meaningful.  
**Where used:** Resource entries.  
**Rule:** Omit empty `relationships` arrays.

---

## 3. Measurement and evaluation terms

### `metrics`
**Meaning:** Quantitative measurements or benchmark values associated with a resource.  
**Where used:** Resource entries, reports, assurance events.  
**Notes:** Meaning depends on context:
- in `IntentResolvedEvent`, resource `metrics` are KP benchmark values
- in `IntentAssuranceEvent`, resource `metrics` are live observed values

### `targets`
**Meaning:** Intended/expected values used for comparison or reporting.  
**Where used:** External `IntentReport`  
**Replaces:** `expectations`

### `evaluations`
**Meaning:** Assessment results such as pass/fail or other outcome judgments.  
**Where used:** `IntentAssuranceEvent`, `IntentOptimisedEvent`, external `IntentReport`

### `deviation`
**Meaning:** Signed margin from the relevant target or threshold.  
**Where used:** `IntentAssuranceEvent.evaluations[]`  
**Canonical shape:** `deviation.value`, `deviation.unit`  
**Sign rule:**
- positive value = above target
- negative value = below target

---

## 4. Priority and policy terms

### `priority`
**Meaning:** Canonical priority field.  
**Where used:** External intent payloads, reports, preferences, characteristics.  
**Replaces:** `priority_level`

### `statusReason`
**Meaning:** Free-text explanation of current status or status transition.  
**Where used:** Internal assurance and rejection events, reports.

### `reasonCode`
**Meaning:** Structured rejection reason code.  
**Where used:** `IntentRejectedEvent`

---

## 5. Internal event structure terms

### `body`
**Meaning:** Canonical top-level business content wrapper for internal events.  
**Where used:** Internal event payloads.  
**Replaces:** `payload`

### `request`
**Meaning:** Validated incoming intent content passed forward from IC MS.  
**Where used:** `IntentValidatedEvent`

### `inputs`
**Meaning:** Validation or processing context that accompanied the request at that milestone.  
**Where used:** `IntentValidatedEvent`

### `references`
**Meaning:** Canonical reference block for related canonical resources.  
**Where used:** Internal events.  
**Rule:** Keep `references` at the tail of `body`.

### `current`
**Meaning:** Current in-service/applicable operational state.  
**Where used:** `IntentAssuranceEvent`

### `candidates`
**Meaning:** Optional alternative valid or re-decision resource set.  
**Where used:** `IntentResolvedEvent`, `IntentAssuranceEvent`

### `target`
**Meaning:** Where / who the apply-ready configuration should be sent to.  
**Where used:** `IntentNetworkReadyEvent`  
**Replaces:** `applicationTarget`

### `configuration`
**Meaning:** What should be applied.  
**Where used:** `IntentNetworkReadyEvent`  
**Replaces:** `networkConfiguration`

### `observability`
**Meaning:** Monitoring hookup and observability scope for assurance/control loop operation.  
**Where used:** `IntentNetworkReadyEvent`

---

## 6. Internal event-specific business terms

### `resolvedIntent`
**Meaning:** Interpreted semantic and policy-resolved intent ready for optimisation.  
**Where used:** `IntentResolvedEvent`

### `hardConstraints`
**Meaning:** Must-satisfy conditions.  
**Where used:** `IntentResolvedEvent`  
**Notes:** Preferred over generic `constraints`.

### `optimisationObjectives`
**Meaning:** Ranked optimisation goals used once hard constraints are satisfied.  
**Where used:** `IntentResolvedEvent`  
**Notes:** Preferred over generic `objectives`.

### `preferences`
**Meaning:** Softer decision hints that inform selection where appropriate.  
**Where used:** `IntentResolvedEvent`

### `optimisationOutcome`
**Meaning:** Result block returned from optimisation.  
**Where used:** `IntentOptimisedEvent`  
**Allowed `status` values:**
- `Optimised`
- `NotOptimisable`
- `Error`

---

## 7. Lifecycle terms

### `lifecycleStatus`
**Meaning:** Canonical lifecycle state field.  
**Where used:** External intent/report projection and internal assurance/rejection events.

### Baselined lifecycle set
- `Acknowledged`
- `InProgress`
- `Active`
- `Degraded`
- `Paused`
- `Rejected`
- `Failed`
- `Terminated`

### Meanings
- `Acknowledged` = syntactic validation succeeded and request admitted
- `InProgress` = semantic / optimisation / apply workflow underway
- `Active` = network has confirmed the policy is active
- `Degraded` = active but not meeting expected service outcome
- `Paused` = policy exists but is intentionally paused
- `Rejected` = rejected before or after orchestration
- `Failed` = delivery/operation failed irrecoverably
- `Terminated` = ended/removed

---

## 8. External report terms

### `IntentReport`
**Meaning:** IC-MS-owned curated external reporting/projection resource.  
**Where used:** External `/intent/{intentId}/intentReport` interfaces and `IntentReport...Event` family.  
**Notes:** Not raw runtime telemetry.

### `reportType`
**Meaning:** Category/type of the report artifact.  
**Where used:** External `IntentReport`

### `category`
**Meaning:** Reporting domain/category.  
**Where used:** External `IntentReport`

### `summary`
**Meaning:** Human-readable concise summary of the report state.  
**Where used:** External `IntentReport`

### `recommendedAction`
**Meaning:** Human-readable suggested next action.  
**Where used:** External `IntentReport`

---

## 9. Legacy/replaced terms

These must not be used as active attribute names unless explicitly discussing historical terms:

- `primaryPathId`
- `secondaryPathId`
- `paths`
- `observedOutcome`
- `expectations`
- `priority_level`
- `serviceType`
- `applicationTarget`
- `networkConfiguration`
- `payload`

---

## 10. Quick canonical map

- use `resources` not `primaryPathId` / `secondaryPathId` / `paths`
- use `roles` with `primary` / `secondary`
- use `metrics` not `observedOutcome`
- use `targets` not `expectations`
- use `priority` not `priority_level`
- use `service.serviceClass` not `serviceType`
- use `body` not `payload`
- use `target` not `applicationTarget`
- use `configuration` not `networkConfiguration`

---

## 11. IntentAssuranceEvent form rules

### `IntentAssuranceEvent`
**Meaning:** Shared internal assurance truth event consumed by both II MS and IC MS.

### Two-form rule
Use the same event name, `IntentAssuranceEvent`, with two payload forms:

- **Non-degraded form**
  - includes `current`
  - does not include `candidates`

- **Degraded form**
  - includes `current`
  - may include `candidates` when re-decision is needed

### `current`
**Meaning:** Current in-service operational truth.  
**Where used:** `IntentAssuranceEvent`

### `candidates`
**Meaning:** Full applicable re-decision set when re-decision is needed.  
**Where used:** Degraded form of `IntentAssuranceEvent`  
**Rule:** When present, `candidates` must include the currently active resources too.

### Post-assurance decision rule
- if `lifecycleStatus` is not `Degraded`, II MS does not need to emit another `IntentResolvedEvent`
- if `lifecycleStatus` is `Degraded`, II MS may use the broader applicable monitored set to decide whether re-resolution / re-optimisation is needed

---

## 12. KP and service-pack terminology additions

### `applicableResourceIds`
**Meaning:** Resource ids scoped to a location that II MS can look up in the global `resources` map.  
**Where used:** KP `locations`  
**Rule:** Use this as the location-to-resource scoping link while keeping `resources` global.

### `observabilityProfileId`
**Meaning:** Reference to a reusable observability profile in KP.  
**Where used:** KP `locations`  
**Notes:** Kept as previously drafted to avoid unnecessary terminology churn.

### `optimisationProfileIds`
**Meaning:** Ordered or allowed optimisation profile references for a location or context.  
**Where used:** KP `locations`

### `surgicalCapable`
**Meaning:** Capability flag indicating suitability for the surgical hospital slice context.  
**Where used:** KP `resourceAttributes`  
**Rule:** Treat as a resource capability.

### `orchestrator`
**Meaning:** Resource-scoped orchestrator target or control-plane endpoint for that resource context.  
**Where used:** KP `resourceAttributes`  
**Rule:** Keep resource-scoped.

### `IntentAssuranceEvent`
**Meaning:** Shared internal runtime truth event emitted by IA MS and consumed by both II MS and IC MS.  
**Where used:** Internal event flow  
**Rules:**
- emitted only on status/lifecycle change
- non-degraded form has no `candidates`
- degraded form may include `candidates` when re-decision is needed
- when present, `candidates` must include the current active resources too

### `IntentResolvedEvent`
**Meaning:** Internal II MS output when optimisation is required.  
**Where used:** Internal event flow

### `IntentNetworkReadyEvent`
**Meaning:** Internal apply-ready handoff event consumed by IA MS.  
**Where used:** Internal event flow

### `IntentRejectedEvent`
**Meaning:** Internal II MS rejection event for semantic/policy/candidate failure.  
**Where used:** Internal event flow

### `monitoringProfileId`
**Meaning:** Considered but not adopted in the current baseline.  
**Status:** Not active; keep prior observability-related naming as drafted for now.

---

## 13. Replaced / avoid terms summary

These should not be used as active attribute names unless explicitly discussing history or comparison:

- `primaryPathId`
- `secondaryPathId`
- `paths`
- `observedOutcome`
- `expectations`
- `priority_level`
- `serviceType`
- `applicationTarget`
- `networkConfiguration`
- `payload`
- `slice_type` (legacy/example-only unless an external standard explicitly forces it)

