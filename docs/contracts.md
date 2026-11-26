# Contracts (C1–C7)

These are the interfaces between the four streams. **Changing any of them needs a PR approved by everyone affected**, announced in the team chat. Agents: never edit this file (or the code mirrors listed below) unless the human says the team approved it.

Contract files: `docs/contracts.md`, `backend/app/schemas.py`, `frontend/src/types/api.ts`, `shared/mocks/search_response.json`, `shared/ranking_test_vectors.json`, `docs/decisions.md`.

---

## C1. Search API

`POST /api/search`. Producer: C. Consumer: D.
Code: `backend/app/schemas.py` (source of truth), mirrored in `frontend/src/types/api.ts`. Canonical example: `shared/mocks/search_response.json` (must validate against `SearchResponse`).

```python
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator

MatchLabel = Literal["identical", "similar", "none"]

class Box(BaseModel):
    x: float = Field(ge=0, le=1)  # normalized top-left x
    y: float = Field(ge=0, le=1)
    w: float = Field(gt=0, le=1)
    h: float = Field(gt=0, le=1)
    label: str
    score: float = Field(ge=0, le=1)

class SearchRequest(BaseModel):
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    text: Optional[str] = None           # e.g. "yellow version"
    box: Optional[Box] = None            # user-selected box; None = auto
    @model_validator(mode="after")
    def exactly_one_image(self):
        if (self.image_base64 is None) == (self.image_url is None):
            raise ValueError("provide exactly one of image_base64 or image_url")
        return self

class Candidate(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    rating: Optional[float] = Field(default=None, ge=0, le=5)
    review_count: Optional[int] = Field(default=None, ge=0)
    adjusted_rating: Optional[float] = Field(default=None, ge=0, le=5)  # Bayesian (C7)
    trust_rating: Optional[float] = Field(default=None, ge=0, le=5)     # review-model weighted (Stream B)
    source: str                       # store name
    link: str
    image_url: str
    match_label: MatchLabel
    match_score: float = Field(ge=0, le=1)
    top_reviews: list[str] = []

class SearchResponse(BaseModel):
    query_id: str
    detections: list[Box]
    selected_box: Optional[Box] = None
    candidates: list[Candidate]
    top_cheapest: list[str]           # candidate ids, max 3
    top_rated: list[str]
    best_value: list[str]
    frontier: list[str]               # Pareto-optimal candidate ids
    cached: bool
    timings_ms: dict[str, float] = {}
```

Errors: invalid request body → `422`. Live pipeline not yet implemented (`USE_MOCK_RESPONSE=false`) → `501`.

---

## C2. Matcher interface

`ml/inference/matcher.py`. Producer: A. Consumers: C and B.

```python
class Matcher:
    @classmethod
    def load(cls, weights_dir: str | None = None, thresholds_path: str | None = None) -> "Matcher": ...
    def score(self, query: "PIL.Image.Image", candidates: list["PIL.Image.Image"]) -> list[float]: ...  # each in [0,1]
    def label(self, scores: list[float]) -> list[str]: ...  # "identical" | "similar" | "none"
    def heatmap(self, query, candidate) -> "np.ndarray": ...  # stretch
```

Labeling rule: `score >= identical` → `"identical"`, else `score >= similar` → `"similar"`, else `"none"`, using the thresholds in C5.

---

## C3. Reviews interface

`ml/inference/reviews.py`. Producer: B. Consumer: C.

```python
def score_reviews(texts: list[str]) -> list[float]: ...  # P(helpful) per review, each in [0, 1], same length as input
```

---

## C4. Cache format

Producer: C. Consumers: B and D (cached mode).

- `backend/app/cache/<sha256>.json` holds the **raw** SerpApi response JSON (no reshaping).
- Key: `sha256(image_bytes + engine + (text or ""))`, hex digest (see `backend/app/services/cache.py::cache_key`).
- `labeling/lens_cache/<photo_id>.json` uses the same raw format.

---

## C5. Artifacts

Producers: A and B. Consumers: C, plus D for charts.

- Matcher weights go in an HF Hub repo (name recorded in `docs/decisions.md`, env `HF_MATCHER_REPO`), **never in git**.
- `ml/artifacts/thresholds.json` holds `{"identical": float, "similar": float}` (extra keys starting with `_` are comments and ignored).
- Metrics go in `ml/artifacts/metrics/*.json`; figures in `ml/artifacts/figures/*.png`.

---

## C6. Labels

Producer: B. Consumer: A (re-ranker).

`labeling/labels.csv` columns: `photo_id, candidate_pos, candidate_link, candidate_image, label, labeler`, where `label` is one of `identical | similar | none`.

---

## C7. Ranking spec

Implemented in both `backend/app/services/ranking.py` (C) and `frontend/src/lib/ranking.ts` (D). Both must pass `shared/ranking_test_vectors.json`.

- **Pool:** candidates with `match_label` of `identical` or `similar`, a non-null `price`, and (for rating-based lists) a non-null `rating`.
- **Adjusted rating:** `adj = (v/(v+m))·R + (m/(v+m))·C`, where R = the candidate's rating, v = its review count (null → 0), C = mean rating of the pool, and m = median review count of the pool (minimum 1).
- **Top cheapest:** the 3 lowest prices.
- **Top rated:** the 3 highest `adj`, ties broken by higher v.
- **Frontier:** candidates not dominated by any other. A dominates B if A's price is no higher, A's `adj` is no lower, and at least one is strictly better.
- **Best value:** the top 3 by `w·norm(adj) + (1−w)·(1 − norm(log(price)))`, where `norm` is min-max over the pool (0.5 if all values are equal) and the default `w = 0.5`.
- **Test vector case format:**
  ```json
  {
    "name": "...",
    "input": {"candidates": [{"id": "...", "price": 0.0, "rating": 0.0, "review_count": 0}], "weight": 0.5},
    "expected": {
      "adjusted_rating": {"<id>": 0.0},
      "top_cheapest": ["..."],
      "top_rated": ["..."],
      "frontier": ["..."],
      "best_value": ["..."]
    }
  }
  ```
  Floats are compared at a tolerance of `1e-6`. Test vector candidates are all already in the pool (no `match_label` field).
