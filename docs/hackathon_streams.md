# ML Hackathon — 4 Parallel Streams

Companion to `docs/hackathon_roadmap.md`. Stage numbers (e.g. "Stage 3d") refer to that roadmap.

## Goal
Split the roadmap into four streams that four people can work on at the same time, each on its own git branch, in its own folders, with very little waiting on each other. Independence comes from three things: shared contracts locked at kickoff, a stub version of every component on day one, and a few dated handoffs, each with a fallback if it's late. By Dec 8 the streams combine into a single app and a single evaluation story.

---

## How AI tools change the plan
- **Faster with AI help:** writing code (UI, endpoints, scripts, training loops). That frees up time, so the live camera mode (9d), the review model (7) and the re-ranker (8) move from "maybe" to planned.
- **Not faster:** downloading data, training runs, hand labeling, API quota, testing on real phones, debugging integration, and rehearsal. The schedule is built around these.
- **New risks:**
  - **Leakage introduced by AI-written code.** Examples: fitting TF-IDF or a scaler before splitting, splitting by image instead of product, splitting real photos by photo instead of by physical object, or picking cutoffs on test data. The ML owners must check every data and evaluation script themselves.
  - **"Explain your own code."** Each person must read and understand everything AI wrote in their stream. Keep `docs/notes/stream-X.md` with plain-language "how it works" bullets, which become your Q&A prep.
  - **Agents breaking contracts.** Put `docs/contracts.md` in every agent's instructions (e.g. a `CLAUDE.md` or `AGENTS.md` at the repo root that points to it). Agents should never change a contract file without the team agreeing.

---

## The four streams at a glance

| Stream | Member | Mission | Roadmap stages | Main deliverable |
|---|---|---|---|---|
| **A: Vision ML** | Member 1 | Build and evaluate the product matcher | 1c, 2, 3, 8, 9c (model side) | `ml/inference/matcher.py` + weights + offline results |
| **B: Evaluation & Language ML** | Member 2 | Real-photo test set, live evaluation, review model | 6, 7 (7a–7d), evidence charts | `labels.csv`, `docs/evaluation.md`, `ml/inference/reviews.py` |
| **C: Backend & Data Plumbing** | Member 3 | Turn everything into one reliable API | 1a, 1b, 4, 7e, 9a, 9b | `/api/search` on the tunnel, plus cached mode |
| **D: Frontend & Demo Experience** | Member 4 | Everything judges see | 5, 9c (UI side), 9d, 9e, 10a, 10d | The PWA, live camera, slides, backup video |

**Shared by everyone:** Stage 0 (kickoff), labeling (about 1–1.5 hours each, Tue 12/1 evening – Wed 12/2), the code freeze, and rehearsals.

**Suggested fit:** A is for the strongest ML person. B suits someone who's ML-minded and good at analysis and writing. C is for the strongest Python and backend person. D is for the strongest frontend and design person. Two of the four streams are mostly ML, which matches the rubric's 55% weight on ML.

---

## Git & ownership rules
- **Branches:** `stream/a-vision`, `stream/b-eval`, `stream/c-backend`, `stream/d-frontend`. Merge into `main` through small PRs at least every other day. `main` must always run.
- **Folder ownership** (only the owner edits these without asking):

| Path | Owner |
|---|---|
| `ml/src/` (matcher scripts), `ml/inference/matcher.py`, `ml/notebooks/01–04, 07` | A |
| `labeling/`, `ml/src/{eval_live,reviews_prepare,train_reviews}.py`, `ml/inference/reviews.py`, `ml/notebooks/05, 06`, `docs/evaluation.md` | B |
| `backend/`, `shared/ranking_test_vectors.json` | C |
| `frontend/`, `demo/` | D |
| `docs/contracts.md`, `backend/app/schemas.py`, `frontend/src/mocks/search_response.json`, `docs/decisions.md` | **Shared:** changes need a PR approved by everyone affected |

---

## Shared contracts (locked at kickoff in `docs/contracts.md`)
These are what let everyone work independently. Each one has a stub on day one, so nobody waits for the real version.

- **C1. Search API.** `POST /api/search` request and response shape, as in roadmap 0d. It lives in `backend/app/schemas.py`, with a matching example in `frontend/src/mocks/search_response.json`.
  - Producer: C. Consumer: D.
- **C2. Matcher interface.** `ml/inference/matcher.py` provides:
  - `Matcher.load(weights_dir)`
  - `Matcher.score(query: PIL.Image, candidates: list[PIL.Image]) -> list[float]`
  - `Matcher.label(scores) -> list["identical" | "similar" | "none"]`
  - Stretch: `Matcher.heatmap(query, candidate) -> np.ndarray`
  - **Day-one stub:** zero-shot SigLIP 2 cosine similarity with placeholder cutoffs. That's a real baseline, not a fake.
  - Producer: A. Consumers: C and B.
- **C3. Reviews interface.** `ml/inference/reviews.py` provides `score_reviews(texts: list[str]) -> list[float]`, the probability each review is helpful.
  - **Day-one stub:** a review-length heuristic.
  - Producer: B. Consumer: C.
- **C4. Cache format.** `backend/app/cache/<sha256>.json` holds the raw SerpApi response, keyed by image hash + engine + text. `labeling/lens_cache/<photo_id>.json` uses the same format.
  - Producer: C. Consumers: B and D (cached mode).
- **C5. Artifacts.** Matcher weights go in an HF Hub repo (name it at kickoff). `ml/artifacts/thresholds.json` holds `{"identical": float, "similar": float}`. Metrics go in `ml/artifacts/metrics/*.json`.
  - Producers: A and B. Consumers: C, plus D for charts.
- **C6. Labels.** `labeling/labels.csv` has the columns `photo_id, candidate_pos, candidate_link, candidate_image, label, labeler`.
  - Producer: B. Consumer: A (for the re-ranker).
  - Companion file (B-owned, not a contract): `labeling/candidates.csv` holds candidate metadata and local image paths, and joins on `photo_id, candidate_pos`. Consumer: A (re-ranker features).
- **C7. Ranking spec.** The Bayesian average and weighted value formulas, written in `docs/decisions.md`, plus `shared/ranking_test_vectors.json` (inputs → expected outputs). C implements the backend version and D implements the slider version in `frontend/src/lib/ranking.ts`. Both must pass the same test vectors.

---

## Stream A: Vision ML (Member 1)
**Mission:** build the main model, prove it beats the baselines, and hand C a reliable inference module.

- **A1. Data test & catalog (1c, 2a–2b).** Category check, `build_catalog.py`, image download.
- **A2. Stub matcher by Sat 11/28 (C2).** Zero-shot SigLIP behind the final interface, pushed to `main`.
  *Why:* C and B can integrate on day 3 instead of day 8.
- **A3. Remove duplicates, split, pairs (2c–2e).** Includes `docs/data_card.md`.
- **A4. Embeddings & baselines (3a–3b).** ResNet-50 and zero-shot SigLIP, Recall@K on validation. Expose `embed_images(images, backbone)` so B's live evaluation uses the same preprocessing.
- **A5. Hard negatives & training (3c–3d).** Projection head with grid search on validation.
- **A6. Cutoffs & frozen model (3e).** `thresholds.json`, weights on HF Hub.
- **A7. One-time test evaluation (3f).** Figures plus the offline section of `docs/evaluation.md`, sent to B.
- **A8. Real matcher v1 by Wed 12/2.** Same interface, real weights.
- **A9. XGBoost re-ranker (Stage 8).** Starts once labels arrive (Thu 12/3). Cross-validation grouped by `object_id`, reported only from out-of-fold predictions (never in B's held-out table), and integrated behind a flag if it wins.
- **A10. Heatmap function (9c, stretch).** `Matcher.heatmap` using patch similarity.

**Delivers:** stub matcher (Sat 11/28) · real matcher + cutoffs (Wed 12/2) · offline metrics and figures (Thu 12/3) · re-ranker decision (Sat 12/5)
**Depends on:** `labels.csv`, `candidates.csv` and the candidate image zip from B (Thu 12/3), for the re-ranker only. **Fallback:** if labels are late, skip the re-ranker.
**Done when:** C's live endpoint uses the real matcher, and the offline comparison table is in `docs/evaluation.md`.

---

## Stream B: Evaluation & Language ML (Member 2)
**Mission:** own the evidence (the 20 points for Results), build the second model, and run the team labeling session. Detailed plan: Stream B roadmap.

- **B0. Evaluation plan (Thu 11/26).** Write the metrics and split rules into `docs/decisions.md` before any results exist: NDCG@3 primary; Precision@3 for Identical, Hit@1 and the confusion matrix secondary; bootstrap confidence intervals over objects; real photos split by `object_id`, reviews by `parent_asin`.
  *Why:* choosing metrics after seeing results is a quiet form of leakage.
  `docs/decisions.md` is shared, so the plan goes in through a PR approved by everyone.
- **B1. Review data test & stub (by Sat 11/28).** Check the `helpful_vote` distribution and the timestamp range, pick the "old enough" cutoff, and confirm the C3 stub is on `main`.
- **B2. Real-photo set (6a, 6d, from Sat 11/28).** 25–30 distinct objects, 1–2 photos each, varied conditions, every demo object included. `labeling/prepare_queries.py` strips EXIF and writes `manifest.csv` with `object_id`, `query_box` and `is_demo_object`. Lock the calibration/test split by `object_id` before collecting candidates.
  *Why:* every photo of the same item must stay in one split, or re-tuned cutoffs leak.
- **B3. Labeling setup (6c, by Mon 11/30).** `labeling/guidelines.md` (Identical = same `parent_asin`, agreed with A) and `label_tool.py` (Streamlit): blind, shuffled, resumable, with an overlap mode and a kappa helper. Dry run on C's feasibility-test cache.
- **B4. Review model (7a–7d).** `reviews_prepare.py`, then three tiers: the length heuristic, TF-IDF + logistic regression, and DistilBERT fine-tuned on Colab. PR-AUC primary, macro-F1 secondary.
  *Why:* helpfulness tracks length, so the model has to beat a length rule to matter.
- **B5. Collect Lens candidates (6b, Tue 12/1).** `labeling/collect_candidates.py` uses C's `serp.py` with the app's query crop, saves raw JSON to `labeling/lens_cache/`, writes `labeling/candidates.csv`, and downloads every candidate image locally (gitignored, shared as a zip).
  *Why:* image links can break before the evaluation and re-ranker work.
- **B6. Labeling session (Wed 12/2).** A 10-item warm-up, then the work split by object among four people, with 100 items double-labeled for the agreement score.
  B and D double-label the 100 items. Labeling can open Tue 12/1 evening.
- **B7. Live evaluation (6e).** `eval_live.py` comparing Lens order, ResNet, zero-shot SigLIP and A's model on the test photos, with confidence intervals, confusion matrices at validation and calibration cutoffs, the retrieval ceiling, and error analysis.
- **B8. Real reviews model by Wed 12/2.** Same C3 interface, falling back to the stub if weights fail to load. If DistilBERT is late, TF-IDF + logistic regression ships instead.
- **B8b. `trust_rating` formula (Tue 12/1).** Written into `docs/decisions.md` for C to implement.
- **B9. Evidence package (Fri 12/4).** `docs/evaluation.md` finished, plus 2–3 slide-ready charts sent to D.

**Delivers:** reviews stub and locked photo split (Sat 11/28) · labeling tool (Mon 11/30) · `candidates.csv` + candidate images (Tue 12/1) · real reviews model (Wed 12/2) · `labels.csv` (Thu 12/3) · evaluation results and charts (Fri 12/4)
**Depends on:**
- C's detector decision at CP1 (Sat 11/28), to define the query crop. **Fallback:** draw query boxes by hand.
- C's `serp.py` by Tue 12/1. **Fallback:** call SerpApi directly from a notebook using the same cache format.
- A's real matcher by Wed 12/2. **Fallback:** evaluate the stub as "zero-shot SigLIP" and add A's model when it lands.
- A's `embed_images` by Sun 11/29, for the live baselines. **Fallback:** a minimal embedder inside `eval_live.py`.
**Done when:** the live comparison table with confidence intervals, agreement score, review-model metrics and charts are finished and handed to D.

---

## Stream C: Backend & Data Plumbing (Member 3)
**Mission:** make `/api/search` correct, fast, cached, and reachable from a phone.

- **C1. SerpApi + detector tests (1a–1b, Fri 11/27).** Answer the CP1 questions and record them in `docs/decisions.md`.
- **C2. Contract owner (0d).** Keep `schemas.py` and the mock JSON matching.
- **C3. FastAPI skeleton (4a)** that serves the mock on day one.
- **C4. `serp.py` with cache & quota log (4b) by Sun 11/29.** B needs it by Tue 12/1. Budget: about 50 Lens searches for B's real-photo set, with about 20% reserve.
- **C5. `detect.py` (4c).** The detector, or the fallback chosen at CP1. Record the query crop and padding in `docs/decisions.md` at CP1; the app and B's evaluation both score that crop.
- **C6. Matcher integration (4d)** against A's stub, so swapping in the real model is a one-line change.
- **C7. `ranking.py` + test vectors (4e, C7).** Publish `shared/ranking_test_vectors.json` by Mon 11/30 so D can match it.
- **C8. Text refinement (4f) & cached mode (4g).**
- **C9. Reviews integration (7e)** against B's stub. Fetch reviews only for the top few products, and cache them. Implement B's `trust_rating` formula from `docs/decisions.md`.
- **C10. Serving & hosting (4h).** FastAPI serves D's build, a Cloudflare tunnel provides HTTPS, and a Hugging Face Space is the backup.
- **C11. Swap in the real models (Wed 12/2), run every demo object end to end and cache it all (9a), then speed work (9b).**

**Delivers:** test results (Fri 11/27) · `serp.py` (Sun 11/29) · ranking test vectors (Mon 11/30) · live endpoint on the tunnel (Mon 11/30) · real models swapped in (Wed 12/2) · every demo query cached (Fri 12/4)
**Depends on:** A's and B's stubs (Sat 11/28), then their real versions (Wed 12/2). **Fallback:** keep shipping with the stubs. The app works either way.
**Done when:** a phone on the hotspot gets correct results for every demo object, both live and with `DEMO_CACHED=1`.

---

## Stream D: Frontend & Demo Experience (Member 4)
**Mission:** make the ML visible and the demo hard to break.

- **D1. Scaffold (5a).** React + Vite + TypeScript + Tailwind + PWA, built against the C1 mocks.
- **D2. Image input (5b).** `capture` input, upload, pasting a screenshot, and an image URL.
- **D3. Detection overlay (5c)** with tap to select.
- **D4. Results, cards, top-3 tabs (5d).** Show `trust_rating` on each card when it isn't null.
- **D5. Value scatter + slider (5e).** `frontend/src/lib/ranking.ts` must pass C's test vectors.
- **D6. Pipeline animation & loading/empty/error states (5f).**
- **D7. Text refinement + switch to the live API (5g)**, through the tunnel, by Tue 12/1.
- **D8. Live camera mode (9d).** MediaPipe in the browser, lock when the box is steady, and a bottom sheet of results.
- **D9. Heatmap overlay UI (9c).** Shows A's heatmap, if A ships it.
- **D10. Polish (9e)**, plus a cached-mode indicator so the team knows what the demo is using.
- **D11. Demo assets (10a, 10d).** Slide deck (filled with B's charts), the first draft of `demo/script.md`, and the backup video recorded at the freeze.
- **D12. Second labeler (Wed 12/2).** Double-label the 100 overlap items with B (about 10–15 extra minutes).

**Delivers:** UI on the mocks (Sun 11/29) · UI on the live API (Tue 12/1) · live camera (Thu 12/3) · slides draft (Sat 12/5) · backup video (Sun 12/6)
**Depends on:**
- C's live endpoint by Mon 11/30. **Fallback:** keep building on the mocks.
- B's charts by Fri 12/4. **Fallback:** use A's offline figures.
**Done when:** the full demo flow runs on a phone, live and cached, and the slides plus video are ready.

---

## Parallel calendar

| Date | A: Vision ML | B: Eval & Language ML | C: Backend | D: Frontend & Demo |
|---|---|---|---|---|
| **Wed 11/25 – Thu 11/26** | **Everyone: kickoff (Stage 0), contracts C1–C7 locked, branches created** | | | |
| Fri 11/27 | Data test, `build_catalog.py` | Review data test, photo plan | SerpApi + detector tests | Scaffold, image input |
| **Sat 11/28 (CP1)** | Download, dedupe, splits. **Ship stub matcher** | **Ship reviews stub.** Take photos, write guidelines, **lock photo split** | FastAPI skeleton on mocks, start `serp.py` | Overlay, cards, top-3 tabs |
| Sun 11/29 | Embeddings + baselines | `reviews_prepare`, TF-IDF baseline, label tool | **`serp.py` done**, `detect.py`, matcher integration via stub | Scatter + slider, pipeline animation |
| Mon 11/30 | Hard negatives, train head | DistilBERT fine-tune, **labeling tool done** | `ranking.py` + **test vectors**, cached mode, **tunnel live** | Wire up ranking.ts, text refinement |
| Tue 12/1 | Tune, cutoffs, freeze model | **Collect Lens top-20s + download images**, review-model evaluation, trust_rating formula to C | Reviews integration via stub, HF Space backup | **Switch to live API**, phone testing |
| **Wed 12/2 (CP2)** | Test evaluation, **ship real matcher** | **Ship real reviews model.** Run labeling | **Swap in real models** | Live camera begins |
| | **Everyone: about 1–1.5 hours labeling (B and D double-label 100)** | | | |
| Thu 12/3 | Re-ranker features + training | `eval_live.py`, agreement score, send labels + candidates + images to A | Every demo object end to end, cache all | Live camera, heatmap UI |
| **Fri 12/4 (CP3)** | Re-ranker evaluation, heatmap function | **Evaluation package + charts** | Bug fixes, speed | Polish, cached-mode indicator |
| Sat 12/5 | Re-ranker in or out, Q&A notes | Evidence slides with D, Q&A notes | Final caching, check backup host | Slides + script draft |
| **Sun 12/6 (CP4)** | **Everyone: code freeze, tag v1.0, record backup video, rehearsal #1** | | | |
| Mon 12/7 | **Everyone: rehearsals #2–3, teach-backs, venue and hotspot check** | | | |
| **Tue 12/8** | **Demo at 7pm** | | | |

---

## Sync rhythm
- **Daily 10-minute check-in** (async messages are fine). Each person covers what they shipped, what's next, any blocker, and whether a handoff is at risk.
- **Checkpoints:**
  - **CP1 (Sat 11/28):** test outcomes and stubs on `main`.
  - **CP2 (Wed 12/2):** real models swapped in, and an end-to-end run on a phone.
  - **CP3 (Fri 12/4):** evaluation numbers in, decide stretch goals in or out.
  - **CP4 (Sun 12/6):** code freeze.
- **Contract changes:** proposed as a PR to `docs/contracts.md`, approved by everyone affected, and announced in the chat.

---

## Recommended breakdowns
1. **Stage 0 kickoff (everyone, first).** Contracts, repo, branches, decisions. All four streams depend on it.
2. **One breakdown per stream, split into two halves:**
   - **Part 1, through CP2 (Wed 12/2):** stubs, core build, real models swapped in.
   - **Part 2, CP2 → freeze:** evaluation, stretch goals, polish, demo assets.

That makes nine breakdowns in total. Each member can ask for their own stream's parts once Stage 0 is done.

---

## Changelog
- **2026-11-26 (TICKET-B01):** Stream B plan sync: object-based photo split, `candidates.csv` and local candidate images, blind labeling, new real-photo metrics with confidence intervals, three-tier review-model baselines. Cross-stream items X1–X9 were approved by the team, so none are marked "Proposed".
