# Stream B notes

## How it works (plain language)
- TBD

## Key decisions
- TBD

## What I'd say if a judge asks…
- *Why is a different color "identical"?* The matcher is trained on same-parent_asin pairs, where color/size variants share a listing, so labels match what it learned. Picking the exact variant is the job of text refinement ("yellow version") and the product cards.




## Log
Dated entries: decisions, data findings, and **every test-set run** (date, model version, reason).

- 2026-11-26: Started Breakdown 1 (Stages 0+1).
- 2026-11-26: Kickoff. X2–X9 treated as approved (written via TICKET-B02, PR <#>); <note any that were only proposed>. Categories: <list | TBD → scanning Office_Products first>. Demo objects: <TBD → placeholders in shot list>. A on Identical = same parent_asin: <confirmed | pending>. A on the similar cutoff: <answer | pending>. Told A about datasets 4.x: <yes | no>.
- 2026-11-26: Evaluation plan choices (before any results): primary real-photo metric NDCG@3 (identical=2, similar=1), Hit@1 and P@3 secondary; demo objects always in test; classification baseline = zero-shot SigLIP with calibration-tuned cutoffs. Checked NDCG example: 0.6013 ✓.
- 2026-11-27: Guidelines v1 written. Reviewed all judgment calls; kept the defaults. Considered color variant = similar and rejected it: matcher positives are same parent_asin (variants mixed in the data), so it would count correct matches as errors and conflict with the size/multipack rules. Sign-off requested from A.