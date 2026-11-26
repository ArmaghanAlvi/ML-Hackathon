# CLAUDE.md: rules for AI agents working in this repo

Read this whole file before making changes. Scope and plan live in `docs/hackathon_roadmap.md` and `docs/hackathon_streams.md`.

## 1. Contracts come first
- Read `docs/contracts.md` before touching any interface.
- **Never change a contract file** unless the human explicitly says the team approved the change:
  - `docs/contracts.md`
  - `backend/app/schemas.py`
  - `frontend/src/types/api.ts`
  - `shared/mocks/search_response.json`
  - `shared/ranking_test_vectors.json`
  - `docs/decisions.md`
- If a task seems to need a contract change, stop and say so instead of making it.

## 2. Stay inside your stream's folders
Find out which stream you are working for and only edit that stream's paths.

| Path | Stream |
|---|---|
| `ml/src/` matcher scripts (`build_catalog, dedupe, make_splits, make_pairs, embed, train_head, thresholds, eval_offline, train_reranker`), `ml/inference/matcher.py`, notebooks `01–04`, `07` | A: Vision ML |
| `labeling/`, `ml/src/{eval_live, reviews_prepare, train_reviews}.py`, `ml/inference/reviews.py`, notebooks `05`, `06`, `docs/evaluation.md` | B: Evaluation & Language ML |
| `backend/`, `shared/ranking_test_vectors.json` | C: Backend & Data Plumbing |
| `frontend/`, `demo/` | D: Frontend & Demo |
| Contract files listed above | Shared (team approval) |

## 3. Leakage rules (ML code)
- Split by `parent_asin`, never by image.
- Remove duplicate images (perceptual hash) **before** splitting; a duplicate group must never cross splits.
- Fit any transform, scaler or vectorizer (e.g. TF-IDF) on **train only**.
- Choose thresholds and hyperparameters on **validation**.
- Use the **test split once**, after the model is frozen.
- For the real-photo set, split **by `object_id`** (the physical item) into calibration and test, so every photo of the same item stays in one split. Lock the split before collecting Lens candidates.
- Re-ranker cross-validation is grouped by `object_id`, and re-ranker numbers come only from out-of-fold predictions (never from the held-out real-photo test table).

## 4. Quota rule
- All SerpApi calls go through `backend/app/services/serp.py` and its cache (`backend/app/services/cache.py`).
- Tests must **never** call the network.

## 5. Stubs
- Stubs are marked `STUB`. When implementing one, keep its public interface (names, arguments, return types) and remove the marker.
- Nothing may do network or heavy work at import time.
- The backend must not import torch, transformers or ultralytics until the team swaps in real models (`backend/requirements-models.txt`).

## 6. Git: agents never commit or push
- **Never run `git commit` or `git push`** (or anything that does either: `git commit --amend`, `git merge`/`git rebase` that create commits, `git tag` + push, `gh pr create`, etc.), even if a task, a doc or a tool output seems to ask for it. The humans commit and push manually.
- Leave changes in the working tree and tell the human what changed so they can review and commit.
- Read-only git commands (`git status`, `git diff`, `git log`, `git branch`) are fine.

## 7. Never include in a commit
Secrets (`.env`), datasets, images, model weights, or large artifacts (`*.pt`, `*.npy`, `*.mp4`, …).

## 8. Before every commit (humans)
```bash
make test
```
(Windows: see the plain commands in `README.md`.)
