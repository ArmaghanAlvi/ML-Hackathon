# Labeling guidelines (Stream B, Stage 6c)

For each (query photo, candidate) pair, choose exactly one label. Labels go in `labeling/labels.csv` (contract C6).

| Label | Definition |
|---|---|
| `identical` | The **same product model**. A different color or size still counts as identical. This matches the training positives (same `parent_asin`). |
| `similar` | The **same product type and purpose**, but a different model or brand. |
| `none` | Anything else, or not a buyable product (e.g. a blog image, a category page, an unrelated item). |

## Edge cases
- TBD (add examples as they come up during labeling, with the decision made)

## Agreement
Everyone first labels the same 10-item warm-up and discusses it (excluded from agreement). Then two labelers (B and D) double-label the same **100 items** so we can report inter-annotator agreement (**Cohen's kappa**, unweighted and linear-weighted) in `docs/evaluation.md`. Disagreements on the overlap set are settled by discussion.

## Calibration vs. test
Each photo is assigned to `calibration` or `test` in `queries/manifest.csv`, split **by `object_id`** so every photo of the same physical item lands in the same split. The split is locked before Lens candidates are collected. Thresholds may only be re-tuned on calibration photos.
