# ML Hackathon — Project Roadmap (Image → Product Comparison App)

**Demo day:** Tuesday, Dec 8, 7pm, Phy 4221. 5 minutes per team.
**Team:** 4 people. Stages are written so they can later be split among people. Workstreams aren't assigned yet.

## Goal
Build a phone-friendly web app that takes a photo, screenshot or image URL, finds the product in it, and pulls matching products from the internet. A model the team trains sorts those results into **Identical**, **Similar**, or **Not a match**, and the app ranks them into **Cheapest**, **Top rated** (adjusted for review count) and **Best value** (price-vs-rating frontier). The finished project includes a trained product-matching model compared against two baselines on held-out data and on a test set of real photos the team labels by hand. A review-helpfulness model and an XGBoost re-ranker are planned extras. A rehearsed 5-minute demo, with cached and video backups, closes it out.

---

## Timeline at a glance

| Dates | Stages | Checkpoint |
|---|---|---|
| Wed 11/25 – Thu 11/26 (Thanksgiving) | 0 Kickoff & setup | — |
| Fri 11/27 – Sat 11/28 | 1 Feasibility tests. Start 2 and 5 | **CP1:** APIs, detector and data confirmed, or a fallback chosen |
| Sat 11/28 – Mon 11/30 | 2 Matching dataset | — |
| Sun 11/29 – Wed 12/2 | 3 Matcher training, 4 Backend, 5 Frontend, 7 Reviews (start) | **CP2 (Wed 12/2):** an end-to-end pipeline that works, however rough |
| Sat 11/28 – Fri 12/4 | 6 Real-photo evaluation (photos early, labeling later) | **CP3 (Fri 12/4):** real-photo evaluation numbers in, stretch goals decided |
| Thu 12/3 – Sat 12/5 | 8 Re-ranker (optional), 9 Integration & polish | — |
| Sat 12/5 – Mon 12/7 | 10 Demo prep | **CP4 (Sun 12/6 evening):** code freeze |
| Tue 12/8 | Demo, 7pm | — |

**Dependency chain:** Stage 0d (API contract) → Stages 4 and 5 can run in parallel. Stage 2 → 3 → 6e. Stage 6a (photos + locked split) → 6b. Stage 1a → 4b → 6b. Stage 6c labels → 6e and 8.

---

## Proposed repo layout (referenced throughout)

```
README.md
.env.example                  # SERPAPI_KEY, DEMO_CACHED, etc.
docs/
  decisions.md                # every locked decision + fallback chosen
  rubric_checklist.md         # rubric line → deliverable → owner
  data_card.md                # dataset counts, splits, known issues
  evaluation.md               # all results, charts, error analysis
ml/
  data/                       # gitignored: raw metadata, images, embeddings
  artifacts/                  # thresholds.json, metrics/*.json, figures/*.png (weights on HF Hub/Drive)
  notebooks/                  # 01_explore … 07_reranker
  src/                        # build_catalog.py, dedupe.py, make_splits.py, make_pairs.py,
                              # embed.py, train_head.py, thresholds.py, eval_offline.py,
                              # eval_live.py, reviews_prepare.py, train_reviews.py, train_reranker.py
labeling/
  queries/                    # real photos (EXIF stripped) + manifest.csv (incl. object_id, query_box)
  lens_cache/                 # raw Lens responses for labeled photos
  lens_cache/images/          # gitignored: local copies of candidate images
  candidates.csv              # one row per Lens candidate; joins labels.csv on photo_id + candidate_pos
  guidelines.md
  prepare_queries.py          # resize, strip EXIF, write manifest rows
  collect_candidates.py       # Lens via serp.py → lens_cache + candidates.csv + images
  label_tool.py               # tiny Streamlit labeler (blind, shuffled)
  labels.csv
backend/
  app/main.py                 # FastAPI app; also serves the built frontend
  app/schemas.py              # request/response models (the API contract)
  app/routes/search.py
  app/services/{detect,serp,matcher,ranking,reviews}.py
  app/cache/                  # disk cache of API responses
  tests/
  requirements.txt
frontend/
  src/{App.tsx, api/client.ts, mocks/search_response.json}
  src/pages/{Home,Results,Camera}.tsx
  src/components/{ImageInput,DetectionOverlay,PipelineAnimation,ProductCard,TopThreeList,ValueScatter}.tsx
demo/
  script.md, objects.md, qa_prep.md, backup_video.mp4
```

---

## Stage 0 — Kickoff & setup (Wed 11/25 – Thu 11/26)
**Why this stage:** Four people working in parallel need shared decisions, a shared repo, and an agreed API shape. Without those, the first few days go to rework.

- **0a. Lock decisions.** Pick the target user, 3–5 product categories (e.g. Home & Kitchen, Office Products, Electronics accessories, Sports & Outdoors), a shortlist of 8–10 demo objects you own that are easy to find online, and a project name. Record them in `docs/decisions.md`. Also record the evaluation plan (the metrics and split rules in 6d, 6e and 7d) before any results exist.
  *Why:* the categories decide which data you download, and the demo objects decide what you test against all week.
- **0b. Accounts & keys.** Set up SerpApi (decide on the free tier vs. a shared $25 Starter plan), Colab/Kaggle, a GitHub repo, and a Hugging Face account for storing weights. Create `.env.example`. Agree the search budget: about 50 Lens searches for the real-photo set (6b), the rest for development and demo caching, with about 20% in reserve.
  *Why:* every later stage needs these, and quota decisions affect how carefully you cache.
- **0c. Repo skeleton & conventions.** Create the layout above, plus a `.gitignore` covering `ml/data/`, large artifacts and `.env`. Agree on a branch and PR habit and write a README with setup steps.
  *Why:* this avoids merge chaos and keeps large binaries out of git.
- **0d. API contract + mocks.** Define `POST /api/search` in `backend/app/schemas.py`:
  - **Request:** image (base64 or URL), optional text refinement, optional selected box.
  - **Response:** detections, candidates (title, price, rating, review count, adjusted rating, source, link, image, match label, match score) and the three top-3 lists.
  - Put a realistic example in `frontend/src/mocks/search_response.json`.
  *Why:* the frontend can then be built and polished before the backend works. This is the main thing that lets four people work in parallel.
- **0e. Rubric checklist.** In `docs/rubric_checklist.md`, map each rubric line to a concrete deliverable.
  *Why:* it keeps the 55 points for rigor and results visible all week, not just the 10 for the app.

**Done when:** everyone can clone, install and run an empty backend and frontend, and the mock JSON is agreed.

---

## Stage 1 — Feasibility tests (Fri 11/27 – Sat 11/28)
**Why this stage:** Test the three biggest unknowns with throwaway scripts before building on them.

- **1a. SerpApi test.** In `backend/scripts/spike_serp.py`, run Google Lens on 5 demo-object images, using both an image URL and the upload flow (Image API → `image_id`). Then run Google Shopping on the top match's title. Record latency, how often rating and review counts are present, how many results come back, and how many searches one user query costs. Save the raw JSON to the cache.
  *Why:* the product depends on this. It also tells you how many searches each query costs and whether Shopping is needed for ratings.
- **1b. Detector test.** Run YOLO26 (COCO classes) and YOLOE (open-vocabulary, e.g. the prompt "product") on 10 demo photos.
  *Why:* many products aren't in COCO's classes. Choose a detector, or fall back to "whole image + user drags a box."
- **1c. Amazon data test.** Load the metadata for one category from Amazon Reviews 2023 and check images per product, price coverage, and image download speed.
  *Why:* this tells you how big a dataset you can realistically build.
- **1d. Go/no-go (CP1).** Record outcomes and fallbacks in `docs/decisions.md`.
  *Why:* this is the last cheap moment to change direction. Fallbacks: eBay `search_by_image` if SerpApi results are poor, a manual box if the detector is poor, fewer categories if downloads are slow.

**Done when:** you have saved API responses for 5 objects, a chosen detector approach, and a confirmed data plan.

---

## Stage 2 — Matching dataset (Sat 11/28 – Mon 11/30)
**Why this stage:** The trained model is only as clean as its data, and most leakage risk lives here.

- **2a. Build the catalog.** `ml/src/build_catalog.py` filters the chosen categories to products with at least 2 images and a title, then samples about 5–10k products.
  *Why:* products with several images give you positive pairs (two photos of the same product).
- **2b. Download images.** Resize to about 384px, download in parallel at a polite rate, and make the script able to resume.
  *Why:* this is fast to train on and won't get blocked or lose progress.
- **2c. Remove duplicates and split.** `ml/src/dedupe.py` uses perceptual hashes to find duplicate images across products, and `ml/src/make_splits.py` splits by `parent_asin` into 70/15/15. Duplicate groups must not cross splits.
  *Why:* this is the core no-leakage guarantee. Sellers reuse the same stock photos, which would otherwise leak test answers into training.
- **2d. Pair generation.** `ml/src/make_pairs.py` builds positives (same `parent_asin`, so color variants count as the same product) and random negatives now. Hard negatives get added after 3c.
  *Why:* random negatives are too easy on their own. Hard ones are what teach the model.
- **2e. Data card.** In `docs/data_card.md`, record counts per split and category, how many duplicates were removed, and known issues (studio photos vs. real photos).
  *Why:* rigor evidence, and it gives you something to point to when judges ask about the data.

**Done when:** you have split files, a pairs file, a local image folder and the data card, with a verified zero overlap of products and duplicate groups between splits.

---

## Stage 3 — Baselines & matcher training (Sun 11/29 – Wed 12/2)
**Why this stage:** This is the main model, and it's what the 35 rigor points rest on.

- **3a. Embeddings.** `ml/src/embed.py` computes ResNet-50 and SigLIP 2 embeddings for every image, plus 2–4 augmented versions of each training image (crops, color jitter, blur, busy backgrounds). Save them as `.npy`. Expose an importable `embed_images(images, backbone)` (L2-normalized) so the live evaluation (6e) uses identical preprocessing.
  *Why:* with a frozen backbone, training only touches these vectors, so it takes minutes. The augmentations simulate messy real photos.
- **3b. Baselines.** `ml/notebooks/02_baselines.ipynb` reports Recall@1 and Recall@5 on validation for ResNet-50 and zero-shot SigLIP, saved to `ml/artifacts/metrics/baselines.json`.
  *Why:* these are the numbers your model has to beat.
- **3c. Hard-negative mining.** Use zero-shot SigLIP nearest neighbors within the training split to find similar-looking but different products, and add them to the pairs.
  *Why:* the model learns the fine distinctions that matter for spotting identical items.
- **3d. Train the head.** `ml/src/train_head.py` trains an MLP projection head with InfoNCE or triplet loss, plus an optional pair classifier. Run a small grid search on validation and save the weights (HF Hub or Drive, with the path noted in `docs/decisions.md`).
  *Why:* this is the trained component that's clearly your own work.
- **3e. Cutoffs.** `ml/src/thresholds.py` picks the Identical and Similar score cutoffs on validation and writes them to `ml/artifacts/thresholds.json`.
  *Why:* setting cutoffs on test data would be leakage.
  `thresholds.json` has one owner (Stream A). Stage 6 may propose cutoffs tuned on calibration photos only; the team picks which pair ships at CP3.
- **3f. One-time test evaluation.** `ml/src/eval_offline.py` runs only after the model is frozen. It produces Recall@K bars, a precision-recall curve and ROC-AUC, saved to `ml/artifacts/figures/`.
  *Why:* using the test set once keeps the result honest.

**Done when:** you have a metrics table comparing ResNet, zero-shot SigLIP and your model on the test split, plus saved weights, cutoffs and figures.

---

## Stage 4 — Backend (Sun 11/29 – Thu 12/3)
**Why this stage:** It connects the detector, web search, your model and the ranking math into one endpoint. The product track (10 points) depends on it, and so does the demo.

- **4a. FastAPI skeleton.** `backend/app/main.py` with `/health`, and `/api/search` returning the mock first.
  *Why:* the frontend can connect to a real server from day one.
- **4b. Search client.** `backend/app/services/serp.py` wraps Lens (URL and upload flows) and Shopping (search on the match title plus any text refinement). It caches responses to disk keyed by image hash and text, logs quota use, and has timeouts.
  *Why:* caching protects your quota and powers cached mode on demo day.
- **4c. Detection service.** `backend/app/services/detect.py` returns boxes and the crop for the selected box, or applies the fallback from 1b. The matcher scores this crop (or the whole image if there's no box) in both the app and the real-photo evaluation (6b, 6e). Record the crop padding in `docs/decisions.md` at CP1.
  *Why:* it supplies the boxes the UI draws and gives web search a cleaner query.
- **4d. Matcher service.** `backend/app/services/matcher.py` loads SigLIP, the trained head and the cutoffs once at startup. It fetches candidate images concurrently, preferring Lens's full-size `image` over `thumbnail`, then scores and labels each candidate.
  *Why:* this is where your model runs in the live app. Small thumbnails hurt accuracy.
- **4e. Ranking.** `backend/app/services/ranking.py`:
  - **Price:** parse it from `extracted_price`.
  - **Top rated:** Bayesian average `(v/(v+m))·R + (m/(v+m))·C`, with C = mean rating in the result set and m = median review count. Record those choices in `docs/decisions.md`.
  - **Cheapest:** the lowest prices among Identical and Similar results.
  - **Best value:** the Pareto frontier, and a weighted score `w·norm(adj_rating) + (1−w)·(1 − norm(log price))`.
  - Write unit tests in `backend/tests/test_ranking.py` with small made-up data.
  *Why:* this is the logic behind the three top-3 lists, and the easiest part to get subtly wrong.
- **4f. Text refinement.** Add the user's text to the Shopping query. As a stretch, blend in SigLIP's text embedding when scoring.
  *Why:* this is the "yellow version" feature.
- **4g. Cached mode.** With `DEMO_CACHED=1` (or a request flag), serve only cached responses.
  *Why:* the demo still works if the API or venue Wi-Fi fails.
- **4h. Serving & hosting.** FastAPI serves the built frontend from the same address, and a Cloudflare quick tunnel gives phones HTTPS. Keep a Hugging Face Space as a backup.
  *Why:* one address avoids cross-origin (CORS) and mixed-content problems, and phone cameras require HTTPS.

**Done when:** a curl request with a demo image returns real labeled candidates and the three lists, and a second identical request is served from the cache.

---

## Stage 5 — Frontend (Fri 11/27 – Fri 12/4)
**Why this stage:** This is what judges see. It's built against the mock data first, so it doesn't have to wait for the backend.

- **5a. Scaffold.** React + Vite + TypeScript + Tailwind + a PWA plugin, mobile-first.
  *Why:* one codebase covers phones and laptops.
- **5b. Image input.** `ImageInput.tsx` offers camera capture via `<input type="file" accept="image/*" capture="environment">`, upload, pasting a screenshot (desktop), and an image URL.
  *Why:* the `capture` input opens the phone camera with no live-stream code. Live mode is saved for Stage 9.
- **5c. Detection overlay.** `DetectionOverlay.tsx` draws animated boxes on a canvas and lets the user tap a box to select it.
  *Why:* this is the "draws boxes" visual from your vision.
- **5d. Results.** `Results.tsx`, `ProductCard.tsx` and `TopThreeList.tsx` show Identical and Similar sections, tabs for Cheapest, Top rated and Best value, and both the listed and adjusted rating on each card, with links out to stores.
  *Why:* this is the core product output.
- **5e. Value scatter.** `ValueScatter.tsx` plots price vs. adjusted rating, highlights the frontier, and has a slider. The slider re-ranks on the client using the same formula as 4e.
  *Why:* the result updates instantly, and non-ML viewers grasp it right away.
- **5f. Pipeline animation & states.** `PipelineAnimation.tsx` runs box → crop zoom → "Searching the web…" → non-matches fading out. Also add loading, empty and error states.
  *Why:* it hides the API wait and makes the ML visible.
- **5g. Text refinement + live switch.** Add a text input that triggers a new search, and switch `api/client.ts` from the mocks to the live API (keep a toggle).
  *Why:* this completes the feature set.

**Done when:** you can take a photo on a phone through the tunnel and see boxes, the animation, cards, the three lists and the scatter, using live data.

---

## Stage 6 — Real-photo evaluation (photos Sat 11/28 →, labeling Tue 12/1 – Fri 12/4)
**Why this stage:** This is the strongest evidence you'll have. It measures your model on the kind of data the app actually sees.

- **6a. Capture photos.** Photograph 25–30 distinct items, 1–2 photos each (about 40–50 total), across varied conditions: clean and cluttered backgrounds, low light, odd angles, partly blocked, held in hand. Include every demo object. `labeling/prepare_queries.py` resizes to about 1024px, strips EXIF, renames each file to its `photo_id`, and writes `labeling/queries/manifest.csv` with `photo_id, object_id, filename, description, category, split, query_box, is_demo_object`.
  *Why:* the photos don't depend on the model, so this can start right away. `object_id` ties together every photo of the same physical item, varied conditions make the error analysis meaningful, and stripping EXIF removes GPS location before photos are committed.
- **6b. Collect candidates.** `labeling/collect_candidates.py` runs Lens once per photo through `serp.py`, using the same query crop the app sends (from `query_box`). It saves raw JSON to `labeling/lens_cache/`, writes the top 20 to `labeling/candidates.csv` (`photo_id, candidate_pos, title, link, source, price, rating, review_count, image_url, thumbnail_url, local_image_path, image_kind`), and downloads every candidate image to `labeling/lens_cache/images/` (gitignored, shared as a zip). Budget 30–50 Lens searches.
  *Why:* every model is then compared on exactly the same candidates, and local copies survive store image links breaking before evaluation.
- **6c. Label.** Write `labeling/guidelines.md` defining identical (same model, any color, matching the training positives), similar and no, with edge cases. `labeling/label_tool.py` hides the Lens position and all model scores and shuffles candidate order. Start with a 10-item warm-up everyone labels and discusses (excluded from agreement). Two people label the same 100 items; report Cohen's kappa, unweighted and linear-weighted, and settle disagreements on the overlap set by discussion.
  *Why:* blind labeling keeps the Lens baseline honest, weighted kappa suits ordered labels (none < similar < identical), and agreement is cheap evidence of rigor.
  The two double-labelers are B and D, so A isn't double-labeling on the day the real matcher ships. Labeling can open Tue 12/1 evening once candidates are collected.
- **6d. Calibration vs. test split.** Split by `object_id` with a fixed seed, stratified by category: about 10–15 photos for calibration (optionally re-tuning cutoffs for real photos), the rest as the live test set. Do this right after 6a and lock it before 6b.
  *Why:* the same no-leakage rule applies to your own data. Splitting by photo would let another photo of a test item into calibration.
- **6e. Live evaluation.** `ml/src/eval_live.py` ranks each photo's candidates by Lens order, ResNet, zero-shot SigLIP and your model (same crop, same candidates, same local images). On the test photos it reports NDCG@3 (identical = 2, similar = 1) as the primary metric, plus Precision@3 for Identical and Hit@1, each with bootstrap 95% confidence intervals over test objects. It also reports a 3-class confusion matrix at validation cutoffs and again at cutoffs tuned on calibration photos only, and the retrieval ceiling (share of test photos with at least one identical candidate in Lens's top 20). Write results and 5–10 categorized failures in `docs/evaluation.md`.
  *Why:* this is the headline result and chart for the Results & evidence criterion. With about 30–35 test photos, the intervals show which differences are real, and the ceiling separates Lens misses from matcher misses.

**Done when:** you have the comparison table with confidence intervals, the agreement score, figures and error analysis for the live test set (CP3).

---

## Stage 7 — Review-helpfulness model (second model, Mon 11/30 – Fri 12/4; first to cut)
**Why this stage:** A second trained model with its own baseline strengthens the ML core, and it feeds the trust-adjusted rating.

- **7a. Prepare data.** `ml/src/reviews_prepare.py` samples about 50k reviews from your categories that are old enough to have collected votes (pick the cutoff date from the data's timestamp range). Helpful = 3 or more votes, not helpful = 0 votes; drop reviews with 1–2. Remove exact duplicate review texts, then split by product (`parent_asin`) 70/15/15, keeping the natural class ratio in validation and test.
  *Why:* the labels already exist in the dataset, and splitting by product after removing duplicate texts avoids leakage.
- **7b. Baselines.** (i) The length heuristic, which is the C3 stub (`min(1, word_count / 100)`). (ii) TF-IDF + logistic regression (`ml/notebooks/06_review_model.ipynb`), adapted from the course NLP notebook: vectorizer fit on train only, C tuned on validation, balanced class weights.
  *Why:* helpful votes track review length strongly, so the model has to beat a length rule to show it adds anything.
- **7c. Model.** Fine-tune DistilBERT for 1–2 epochs on Colab (T4, max length 256, fp16) with `ml/src/train_reviews.py`, choose the checkpoint by validation PR-AUC, and save it to the HF Hub.
- **7d. Evaluate.** Report PR-AUC (primary), macro-F1 at a cutoff chosen on validation, a confusion matrix, and PR curves for all three models, once on test, in `docs/evaluation.md`. Also check 10–20 Google reviews from the backend cache by eye.
  *Why:* the classes are imbalanced, so accuracy would be misleading. The Google check shows how big the Amazon → Google gap is.
- **7e. Integrate.** `backend/app/services/reviews.py` fetches reviews for the top few products only, scores them, and computes a trust-adjusted rating plus the 2–3 most informative reviews per card. Cache everything. `ml/inference/reviews.py` falls back to the length stub if the weights fail to load.
  *Why:* each product's reviews cost extra searches. Note that Google reviews differ from the Amazon training reviews, and list that as a limitation.
  Stream B writes the trust_rating formula in docs/decisions.md by Tue 12/1 (draft: trust = (Σ hᵢ·rᵢ + k·adjusted_rating) / (Σ hᵢ + k), k = 3, where hᵢ is review helpfulness and rᵢ its stars; null when no reviews were fetched). Stream C implements it.

**Done when:** you have the three-model metrics comparison, and cards show a trust-adjusted rating and top reviews. If DistilBERT is late, TF-IDF + logistic regression ships behind the same interface. If the stage gets cut, the Bayesian average stays as the adjusted rating.

---

## Stage 8 — XGBoost re-ranker (optional, Thu 12/3 – Sat 12/5)
**Why this stage:** It adds a third trained model that uses the rubric's own example (XGBoost), trained on data you labeled yourselves. Only attempt it if Stage 6 reaches about 50 labeled photos.

- **8a. Features.** For each candidate: model score, ResNet score, zero-shot score, Lens position, title-text similarity, and price relative to the median. Candidate metadata comes from `labeling/candidates.csv` and images from `labeling/lens_cache/images/`.
- **8b. Train.** `ml/src/train_reranker.py` uses `rank:pairwise`, with cross-validation grouped by `object_id`.
  *Why:* grouping keeps all results for one photo in the same fold, so the model is never tested on a photo, or another photo of the same item, that it trained on.
- **8c. Evaluate & integrate.** Compare NDCG@3 and precision@3 against Lens order and against your model alone. If it wins, use it behind a flag in `matcher.py`. Re-ranker numbers come only from out-of-fold predictions in grouped cross-validation; it never appears as a row in the 6e held-out table.

**Done when:** you have a grouped cross-validation table, plus a decision on whether to use it in the app.

---

## Stage 9 — Integration, polish & stretch goals (Thu 12/3 – Sat 12/5)
**Why this stage:** Make the full flow reliable on the exact objects you'll demo, then add the visual extras.

- **9a. End-to-end run on every demo object.** Fix failures, and make sure every demo query is cached.
  *Why:* this guarantees cached mode covers the whole demo.
- **9b. Speed.** Warm up the models at startup, fetch images in parallel, and set a latency target (e.g. under 6 seconds with a live API call, under 1 second from cache).
  *Why:* long silent waits hurt a 5-minute demo.
- **9c. Heatmap (stretch).** Use SigLIP patch similarity to show which parts of the image drove the match, as an overlay in the UI.
  *Why:* this is the meaningful version of the "colored grid" idea.
- **9d. Live camera mode (stretch).** `Camera.tsx` uses `getUserMedia` with the MediaPipe Object Detector in the browser. When the box holds steady for about 1 second it locks, sends one request, and a bottom sheet of results slides up.
  *Why:* it's a strong visual moment, but only after the core flow is solid.
- **9e. Visual polish.** Consistent styling, transitions, and a product map (2D projection of embeddings) if time allows.

**Done when:** all demo objects work live and from cache, and the stretch goals are either finished or deliberately dropped.

---

## Stage 10 — Demo prep (Sat 12/5 – Mon 12/7)
**Why this stage:** Demo and communication is worth 10 points, and strong ML is wasted if the 5 minutes go badly.

- **10a. Slides (3–4).** Problem and user, a "how it works" diagram, the evidence charts (live comparison table and Recall@K), and limitations.
  *Why:* the slides support the live demo and don't replace it.
- **10b. Script.** `demo/script.md`: 0:00–0:30 problem, 0:30–2:30 live demo, 2:30–4:00 evidence, 4:00–4:30 limitations, plus about 30 seconds of buffer. Assign who speaks when.
- **10c. Code freeze (CP4, Sun 12/6 evening).** Tag `v1.0`. After that, only demo-breaking bugs get fixed.
- **10d. Backups.** Record `demo/backup_video.mp4`, verify cached mode on the demo laptop, and bring a hotspot and chargers. Test the phone over HTTPS on the hotspot, and visit Phy 4221 beforehand if you can.
- **10e. Q&A prep.** `demo/qa_prep.md` covers likely questions ("why not Lens?", leakage, which parts are pretrained, failure cases). Each person explains their own code out loud.
  *Why:* explaining your own code is part of the rubric.
- **10f. Rehearse at least 3 times with a timer**, including one run in cached mode and one where something "fails."

**Done when:** the team can deliver it in 4:30 or less, both backups have been tested, and everyone has answered practice questions.

---

## Recommended groupings for breakdowns
- **Breakdown 1: Stages 0 + 1.** Setup and feasibility tests are short, need everyone, and should start tonight or tomorrow.
- **Breakdown 2: Stages 2 + 3.** The matching data and training form one continuous ML pipeline.
- **Breakdown 3: Stage 4 alone.** The backend has many moving parts and sits on the critical path.
- **Breakdown 4: Stage 5 + 9c/9d.** All frontend work, including the visual extras and live camera.
- **Breakdown 5: Stages 6 + 8.** Both run on the labeled real-photo data.
- **Breakdown 6: Stage 7 alone.** It's self-contained, and keeping it separate makes it easy to cut.
- **Breakdown 7: Stage 9 (9a, 9b, 9e) + 10.** Integration and demo prep happen together at the end.

These groupings also line up with how four people could split the work later.

---

## Changelog
- **2026-11-26 (TICKET-B01):** Stream B plan sync: object-based photo split, `candidates.csv` and local candidate images, blind labeling, new real-photo metrics with confidence intervals, three-tier review-model baselines. Cross-stream items X1–X9 were approved by the team, so none are marked "Proposed".
