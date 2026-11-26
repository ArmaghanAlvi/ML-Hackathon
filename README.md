# Product Compare (working title)

A phone-friendly web app for comparing products from a single picture. You give it a photo, screenshot or image URL; a detector boxes the product, and web visual search (Google Lens and Google Shopping via SerpApi) fetches candidate products. Our own trained matcher labels each candidate **identical**, **similar** or **none**, and the app ranks the matches into **Cheapest**, **Top rated** (Bayesian average that accounts for review count) and **Best value** (price-vs-rating Pareto frontier plus a weight slider). Built for the ML hackathon, demo day Tue Dec 8.

Scope and plan: [`docs/hackathon_roadmap.md`](docs/hackathon_roadmap.md) and [`docs/hackathon_streams.md`](docs/hackathon_streams.md).
**Interfaces between streams: [`docs/contracts.md`](docs/contracts.md). Read it before changing any interface.**

## Quickstart

Requirements: Python 3.11+, Node 22.12+ (vitest 5 needs it), npm, git. Run everything from the repo root.

| Step | macOS / Linux (`make`) | Plain commands (Windows: use `.venv\Scripts\` instead of `.venv/bin/`) |
|---|---|---|
| Create venv + install | `make install` | `python -m venv .venv` → `.venv/bin/pip install -r backend/requirements.txt` → `cd frontend && npm ci` |
| Run backend (dev) | `make dev-backend` | `.venv/bin/uvicorn backend.app.main:app --reload --port 8000` |
| Run frontend (dev) | `make dev-frontend` | `cd frontend && npm run dev` (opens http://localhost:5173, proxies `/api` to :8000) |
| Run tests | `make test` | `.venv/bin/pytest` → `cd frontend && npm run typecheck && npm test` |
| Build frontend | `make build` | `cd frontend && npm run build` |
| Serve built app | `make serve` | `cd frontend && npm run build`, then `.venv/bin/uvicorn backend.app.main:app --port 8000` and open http://localhost:8000 |

Copy `.env.example` to `.env` (and `frontend/.env.example` to `frontend/.env`) to change settings. With the defaults, the backend returns the canonical mock (`USE_MOCK_RESPONSE=true`) and the frontend uses it directly (`VITE_USE_MOCKS=true`).

ML / notebook dependencies are **not** installed by default: `pip install -r ml/requirements.txt` when you need them.

## Repo map

| Folder | What's in it |
|---|---|
| `docs/` | Contracts, decisions, rubric checklist, data card, evaluation write-up, per-stream notes |
| `shared/` | Files both backend and frontend read: the canonical mock response and ranking test vectors |
| `ml/` | Data/training scripts (`src/`), inference modules (`inference/`), notebooks, artifacts (thresholds, metrics, figures) |
| `labeling/` | Real-photo test set: manifest, cached Lens results, guidelines, Streamlit label tool, `labels.csv` |
| `backend/` | FastAPI app (`app/`), services, SerpApi spike script, tests |
| `frontend/` | Vite + React + TypeScript + Tailwind PWA |
| `demo/` | Demo script, demo objects, Q&A prep |
| `.github/` | CI workflow (pytest + frontend typecheck/test/build) |

## Stream ownership

| Path | Stream |
|---|---|
| `ml/src/` matcher scripts (`build_catalog, dedupe, make_splits, make_pairs, embed, train_head, thresholds, eval_offline, train_reranker`), `ml/inference/matcher.py`, notebooks `01–04`, `07` | A: Vision ML |
| `labeling/`, `ml/src/{eval_live, reviews_prepare, train_reviews}.py`, `ml/inference/reviews.py`, notebooks `05`, `06`, `docs/evaluation.md` | B: Evaluation & Language ML |
| `backend/`, `shared/ranking_test_vectors.json` | C: Backend & Data Plumbing |
| `frontend/`, `demo/` | D: Frontend & Demo |
| Contract files (`docs/contracts.md`, `backend/app/schemas.py`, `frontend/src/types/api.ts`, `shared/mocks/search_response.json`, `shared/ranking_test_vectors.json`, `docs/decisions.md`) | Shared (team approval) |

Branches: `stream/a-vision`, `stream/b-eval`, `stream/c-backend`, `stream/d-frontend`. Merge to `main` via small PRs; `main` must always run.
