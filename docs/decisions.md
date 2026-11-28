# Decisions

Every locked decision and every fallback used. **Contract file:** changes need team approval.

## Product
- **Target user:** TBD
- **Categories (3–5):** TBD
- **Demo objects (8–10):** TBD (details in `demo/objects.md`)
- **Project name:** TBD (working title: "Product Compare")

## Accounts & infrastructure
- **SerpApi plan:** TBD (free tier vs. shared $25 Starter)
  - **Budget:** Stream B about 50 Lens searches for the real-photo candidates (Tue 12/1, through serp.py); Stream C development and demo caching; about 20% reserve. Every call goes through serp.py's quota log.
- **HF matcher repo name:** TBD

## Detection (CP1)
- **Detector choice:** TBD (YOLO26 COCO vs. YOLOE open-vocabulary)
- **Fallback:** TBD (e.g. whole image + user drags a box)
- **Query image for matching:** the matcher scores the crop of the selected box (or the whole image if there's no box), in the app and in every evaluation. Lens searches for evaluation candidates use the same crop. Crop padding: TBD (C, at CP1).

## Ranking parameters (C7)
- **m (prior review count):** TBD (spec default: median review count of the pool, min 1)
- **C (prior mean rating):** TBD (spec default: mean rating of the pool)
- **Default weight w:** TBD (spec default: 0.5)
- **trust_rating (draft; final by Tue 12/1, Stream B proposes, Stream C implements):** for a candidate with fetched reviews i = 1..n, stars rᵢ and helpfulness hᵢ = score_reviews(textᵢ): trust = (Σ hᵢ·rᵢ + k·adjusted_rating) / (Σ hᵢ + k), k = 3. Null when no reviews were fetched.

## Labeling definitions
- **identical / similar / none:** defined in labeling/guidelines.md (v1.1). Identical = same model, any color/size/pack (same parent_asin).
- **Real-photo labels:** identical / similar / none as defined in `labeling/guidelines.md` (Identical = same model, matching the matcher's training positives: same `parent_asin`). Labels judge product identity, not whether the page is a store. File formats: `labeling/SCHEMA.md`.
- **Review helpfulness label (Stage 1a, Fri 11/27):** Amazon Reviews 2023, team categories (all five scanned: Office, Home & Kitchen, Sports, Cell Phones, Electronics); reviews dated 2015-01 … 2021-12 (data ends 2023-09-14; later reviews haven't had time to collect votes). Helpful = ≥3 votes, not helpful = 0, 1–2 dropped. Natural prevalence 6.5%. Chosen from the vote-age curve and counts, not from any model result.

## Evaluation plan (pre-registered Thu 11/26, before any results)
Written before any real-photo or review-model result exists. Any later change is logged at the end of this section with its date and reason.

### Real-photo (live) evaluation (Stream B)
- **Unit:** one test photo. Its candidate pool is the top 20 Lens results for that photo (`labeling/candidates.csv`), minus candidates whose image failed to download (excluded for every method).
- **Methods** (same photos, same query crop, same candidates, same local images): Lens order · ResNet-50 cosine · zero-shot SigLIP 2 cosine · trained matcher (`Matcher.score`). The re-ranker is not in this table (see Re-ranker rule).
- **Primary metric:** NDCG@3 with linear graded gains (identical = 2, similar = 1, none = 0) and a log2 discount, the same definition as `sklearn.metrics.ndcg_score(k=3)`. The ideal ranking comes from that photo's evaluated pool. Reported as the mean over test photos.
- **Photos with no identical or similar candidate** have no defined NDCG. They're excluded from the ranking metrics and reported in the retrieval ceiling.
- **Secondary:** Hit@1 (top result is identical) · Precision@3 for identical · retrieval ceiling (share of test photos with at least one identical candidate in the pool; also with at least one identical-or-similar).
- **Primary comparisons:** matcher vs. Lens order, and matcher vs. zero-shot SigLIP.
- **Classification view:** 3-class confusion matrix, macro-F1, and identical precision/recall for the matcher at (a) the validation cutoffs in `thresholds.json` frozen at CP2 and (b) cutoffs tuned on calibration photos only. Baseline for this view: zero-shot SigLIP with cutoffs tuned on the same calibration photos.
- **Uncertainty:** bootstrap over test **objects** (all photos of a resampled object come along), 1,000 resamples, seed 0, percentile 95% intervals. Comparisons use a **paired** bootstrap of the difference (method − baseline) on the same resamples; a method is reported as better only if the 95% interval of the difference excludes 0.
- **Subgroups (descriptive only, no significance claims):** demo objects, clean vs. hard conditions, category.
- **Split:** by `object_id`, seed 42, stratified by category; every demo object goes to test; about 10–15 photos (5–7 objects) go to calibration. Committed before any Lens candidates are collected.
- **Test discipline:** calibration photos may be used for tuning cutoffs and debugging. Test photos are only scored by frozen models. Every test run is logged in `docs/notes/stream-b.md` (date, model version, reason). No decision is tuned on test numbers.

### Label quality
- 100 candidates double-labeled by two people after a 10-item warm-up (excluded). Report Cohen's kappa, unweighted and linear-weighted (none < similar < identical). Disagreements on the overlap set are settled by discussion; settled labels are used.
  - The two double-labelers are B and D.

### Review-helpfulness model (Stream B)
- **Label:** helpful = at least 3 helpful votes, not helpful = 0 votes, 1–2 dropped, on reviews old enough to have collected votes. The exact threshold and date window come from the Stage 1a data check (Sat 11/28), recorded under Labeling definitions, and are not chosen from any model result.
- **Split:** exact-duplicate texts removed, then split by `parent_asin` 70/15/15; validation and test keep the natural class ratio.
- **Models:** length heuristic (the C3 stub, `length_score`) · TF-IDF + logistic regression · DistilBERT.
- **Primary metric:** PR-AUC (positive = helpful; a random model scores the positive rate). Secondary: macro-F1 at a cutoff chosen on validation, confusion matrix, PR curves. Test set used once, after the models are frozen. 95% intervals by bootstrap over test products.

### Re-ranker rule (Stream A)
The XGBoost re-ranker trains on team labels, so its results are reported **only** from out-of-fold predictions in cross-validation grouped by `object_id`. It never appears as a row in the held-out real-photo table. If it's switched on in the app, the write-up says the live table describes the matcher without the re-ranker.

### Cutoff ownership
Stream A owns `ml/artifacts/thresholds.json`. Stream B may compute cutoffs from calibration photos only and deliver them with evidence in `ml/artifacts/metrics/calibration_thresholds.json`. The team picks which pair ships at CP3 (Fri 12/4) and logs it here. The evaluation reports both pairs on the test photos.

### Change log for this plan
- (none yet)

## Fallbacks used

| Date | Area | Fallback | Why | Decided by |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |
