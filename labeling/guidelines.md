# Labeling guidelines (v1.1, Sat 11/28)

## The task
For each (query photo, candidate) pair, decide: is the candidate the same product as the boxed object in the query photo?
You see the query photo with its box, the object's description (brand/model), and the candidate's image and title.
You don't see the Lens position or any model score, and candidates are shuffled.
Labels go in `labeling/labels.csv` (contract C6).

## Labels (keys)
- **1 identical**: the same product model as the query object. A different color, size or pack count of the same model still counts. (This matches the matcher's training positives: same `parent_asin`.)
- **2 similar**: the same product type and purpose, but a different model or brand. Something you'd consider buying instead.
- **3 none**: a different type of product, an accessory or part for it, or no identifiable product.
- **0 unsure**: you can't decide after ~10 seconds. It goes to a review queue that's settled at the end of the session. `unsure` is never written to `labels.csv`: C6 allows only identical, similar and none.

## Judge the product, not the page
Label which product the candidate shows or sells. Whether the page is a store doesn't matter: an identical product on a blog, Pinterest or review page is still **identical**. (Buyability comes from the candidate's price, not from your label.)

## How to decide
1. Read the brand and model in the query description.
2. Read the candidate title. If it names the same model, it's **identical**, even if the image is a lifestyle shot.
3. If the title is vague, compare the image: shape, logo and distinctive features (buttons, ports, pattern, handle). Color alone doesn't matter.
4. Same type and purpose, but something marks a different model (brand, shape, feature): **similar**.
5. Use only the image and title. Don't open links.

## Edge cases
| Case | Label |
|---|---|
| Same model, different color or size | identical |
| Multipack of the same model (e.g. 2-pack) | identical |
| Bundle: label by the main item sold | identical if it's the query model; similar if same type, different model; otherwise none |
| Accessory or part for the product (case, lid, refill, charger) | none |
| Same model, different seller or store | identical |
| Used, refurbished, open box | identical |
| Knockoff or look-alike with a different brand | similar |
| Looks the same, but the title gives no brand and you can't tell | similar |
| Older or newer generation (v2 vs. v3, 2022 vs. 2023 model) | similar |
| Image shows several products (collage, comparison chart) | label by the title; with no usable title, by the most prominent product; if that's impossible, none |
| Non-store page (blog, Pinterest, Reddit, news) | label the product shown, same rules |
| No identifiable product (stock photo, text, broken image) | none |
| Query photo shows several objects | only the boxed object counts |

## Tie-breaks
- Unsure between identical and similar → **similar** (identical needs evidence).
- Unsure between similar and none → would someone shopping for the query object consider buying this instead? Yes → similar, no → none.
- Still stuck → **0 unsure**.

## Agreement
Warm-up: everyone labels the same 10 items, then discusses them (excluded from agreement).
Two labelers (B and D) label the same 100 items for Cohen's kappa (unweighted and linear-weighted), reported in `docs/evaluation.md`. Disagreements on those are settled by discussion, and the settled label is used.

## Calibration vs. test
Each photo is assigned to `calibration` or `test` in `queries/manifest.csv`, split **by `object_id`** so every photo of the same physical item lands in the same split. The split is locked before Lens candidates are collected. Thresholds may only be re-tuned on calibration photos.

## Known limitations
Multipacks count as identical, so price comparisons across pack sizes aren't per unit.

## Changelog
- v1 (Sat 11/28): draft by Stream B; Identical = same `parent_asin`; buyability excluded from the label. Pending confirmation from Stream A.
- v1.1 (Sat 11/28): restored from the pre-v1 file: where labels go (`labels.csv`, C6), the labelers (B and D), kappa reported in `docs/evaluation.md`, and the calibration/test split rules. Added: `unsure` is never written to `labels.csv`.
