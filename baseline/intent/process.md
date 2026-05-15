Key process rules we settled on:

* GitHub main/baseline/intent is the source of truth. Do not trust old local/generated copies.
* One file at a time only. Fetch/check one file, patch one file, commit one file, validate one file.
* Always refresh from raw GitHub with cache-busting before validating. If the result looks wrong, refresh again before deciding.
* Do not replace files wholesale. Amend existing GitHub content incrementally and preserve useful structure.
* Generate patches in fresh timestamped folders and include both the stable repo filename plus a unique cache-busting filename where useful.
* Specs first, then design briefs, then diagrams/config.
* After the user commits, validate the committed GitHub file before moving on to the next.
* Allowed stale terms only in “do not use” / explanatory wording. Do not treat those as active model drift.
* Tag clean validated state as baseline-v1.0.

Individual MS solution brief section headings
# <Full MS Name> Solution Brief

Summary
Logical View
Process View
Solution Elaboration
Responsibilities
<MS> does not
Contracts
Request shape/event shape
Field specification
Fields not accepted
Authorisation
Persistence/state/outbox model
Kafka publication
Topics
Event identity
CloudEvents headers
Message shape
Behaviour
Configuration
Consumer contract
Open items
Closed items
MS identity

E2E solution brief section headings

# Intent Management E2E Solution Brief

Business context
Solution summary
Solution elaboration
Use case view
Logical view
Process view

Definition-time capability management
Discover intent specification
Create intent specification
Update intent specification
Activate intent specification
Retire intent specification
Subscribe to intent specification events

Runtime intent management
Discover intent capability
Create intent
Validate intent
Interpret intent
Reject intent
Resolve intent
Prepare network-ready configuration
Apply/orchestrate service configuration
Ingest external callback
Map callback and assurance state
Publish assurance result
Update IntentReport
Terminate intent

Capability matrix
Solution security
Important quality attributes
Risks
Assumptions
Constraints
Appendix

