# Labeling file schemas (Stream B)

Owner: Stream B. `labels.csv` follows contract **C6** in `docs/contracts.md`; the other files here are B-owned and not contracts, but A and C read them, so changes are announced in chat first.

## `labeling/queries/shot_list.csv` (photo plan, Stage 1c)
`object_id, description, category, is_demo_object, conditions, owner, status`
- `object_id`: slug for the physical item (e.g. `mug_ember_01`), shared by every photo of it.
- `description`: brand + exact model when known (labelers use it).
- `conditions`: `;`-separated planned shots, from `clean, cluttered, low_light, angle, occluded, in_hand`.

## `labeling/queries/manifest.csv` (one row per prepared photo, Stage 2)
`photo_id, object_id, filename, description, category, split, query_box, is_demo_object`
- `split`: `calibration` or `test`. Assigned by `object_id` (every photo of an item in the same split), seeded, stratified by category; demo objects always `test`. Locked before candidates are collected.
- `query_box`: normalized `x;y;w;h` with top-left origin, the same convention as C1's `Box`. Empty = the whole image.
- `is_demo_object`: `true` / `false`.

## `labeling/candidates.csv` (one row per Lens candidate, Stage 5)
`photo_id, candidate_pos, title, link, source, price, rating, review_count, image_url, thumbnail_url, local_image_path, image_kind`
- `candidate_pos`: 0-based Lens order. **Join key with `labels.csv`: (`photo_id`, `candidate_pos`).**
- `local_image_path`: `labeling/lens_cache/images/<photo_id>/<candidate_pos>.jpg` (gitignored; shared as a zip). Empty if the download failed; such candidates are excluded from evaluation for every method.
- `image_kind`: `image` (full size) or `thumbnail` (fallback).

## `labeling/labels.csv` (contract C6)
`photo_id, candidate_pos, candidate_link, candidate_image, label, labeler`
- `label`: `identical | similar | none`. Definitions in `labeling/guidelines.md`.

## `labeling/lens_cache/<photo_id>.json`
Raw SerpApi Lens response (contract C4 format). Committed.
