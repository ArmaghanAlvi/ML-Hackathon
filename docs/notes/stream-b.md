# Stream B notes

## How it works (plain language)
- TBD

## Key decisions
- TBD

## What I'd say if a judge asks…
- TBD




## Log
Dated entries: decisions, data findings, and **every test-set run** (date, model version, reason).

- 2026-11-26: Started Breakdown 1 (Stages 0+1).
- 2026-11-26: Kickoff. X2–X9 treated as approved (written via TICKET-B02, PR <#>); <note any that were only proposed>. Categories: <list | TBD → scanning Office_Products first>. Demo objects: <TBD → placeholders in shot list>. A on Identical = same parent_asin: <confirmed | pending>. A on the similar cutoff: <answer | pending>. Told A about datasets 4.x: <yes | no>.
- 2026-11-26: Evaluation plan choices (before any results): primary real-photo metric NDCG@3 (identical=2, similar=1), Hit@1 and P@3 secondary; demo objects always in test; classification baseline = zero-shot SigLIP with calibration-tuned cutoffs. Checked NDCG example: 0.6013 ✓.