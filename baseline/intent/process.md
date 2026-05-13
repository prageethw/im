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
