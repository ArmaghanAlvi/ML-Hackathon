# Stream B notes

## How it works (plain language)
- **One pass, no download:** `scan` reads each review file straight from the web line by line, unzipping on the fly, so even a 67M-row category never has to fit on disk or in memory.
- **Exact counts:** every good row updates exact counters (rows, date range, helpful-vote and star histograms, per-month counts of 0 / 1 / 2 / 3+ / 5+ / 10+ votes) in `_summary.json`.
- **Thin sample:** every 20th row's numbers (no text) go in `_thin.parquet`, for cheap plots and the length-baseline preview.
- **Reservoir sample:** up to 100k reviews from each group (≥2 votes, 0 votes). Item *i* replaces a random slot with probability cap/(i+1), so every review has the same chance of being kept, without knowing the file length. The groups are capped separately, so Stage 4a rebuilds the natural ratio from the monthly counts.
- **Survives interruptions:** outputs are rewritten safely every few million rows with `completed: false`; a crash leaves usable partial results.

## Key decisions
- Real-photo split by `object_id`; demo objects always in test; primary metric NDCG@3; paired bootstrap over objects (pre-registered in `docs/decisions.md`).
- Labels judge product identity, not buyability; a different color/size/pack of the same model is **identical** (matches the matcher's `parent_asin` positives).
- Review label: helpful = ≥3 votes, not helpful = 0, reviews dated 2015-01 … 2021-12; prevalence 6.5%.
- Length heuristic `length_score` is the stub, the Stage 4 baseline and the fallback (one function).

## What I'd say if a judge asks…
- *Why is a different color "identical"?* The matcher is trained on same-parent_asin pairs, where color/size variants share a listing, so labels match what it learned. Picking the exact variant is the job of text refinement ("yellow version") and the product cards.
- *Why drop reviews after 2021?* Votes accumulate over months; a 2023 review with 0 votes may never have been seen. The vote-vs-date plot (`ml/artifacts/figures/review_votes_by_quarter.png`) shows the drop starting in 2022Q4.
- *Why PR-AUC, not accuracy?* Only 6.5% of reviews are helpful, so "always not helpful" scores 93.5% accuracy. PR-AUC's random floor is 0.065, and length alone reaches 0.33.




## Log
Dated entries: decisions, data findings, and **every test-set run** (date, model version, reason).

- 2026-11-26: Started Breakdown 1 (Stages 0+1).
- 2026-11-26: Kickoff. X2–X9 treated as approved (written via TICKET-B02, PR <#>); <note any that were only proposed>. Categories: <list | TBD → scanning Office_Products first>. Demo objects: <TBD → placeholders in shot list>. A on Identical = same parent_asin: <confirmed | pending>. A on the similar cutoff: <answer | pending>. Told A about datasets 4.x: <yes | no>.
- 2026-11-26: Evaluation plan choices (before any results): primary real-photo metric NDCG@3 (identical=2, similar=1), Hit@1 and P@3 secondary; demo objects always in test; classification baseline = zero-shot SigLIP with calibration-tuned cutoffs. Checked NDCG example: 0.6013 ✓.
- 2026-11-27: Guidelines v1 written. Reviewed all judgment calls; kept the defaults. Considered color variant = similar and rejected it: matcher positives are same parent_asin (variants mixed in the data), so it would count correct matches as errors and conflict with the size/multipack rules. Sign-off requested from A.
- 2026-11-27: Stage 1a done. All five categories scanned with completed=True (Office 12.8M, Home & Kitchen 67.4M, Sports 19.6M, Cell Phones 20.8M, Electronics 43.9M rows; ~36–60k rows/s). Decision: window 2015-01 … 2021-12, threshold ≥3, prevalence 6.5% overall; length AP 0.33 (stub 0.28). Details in notebook 06 "Decision". Scan bugs fixed: EOF crash (B03b), negative votes counted separately.
