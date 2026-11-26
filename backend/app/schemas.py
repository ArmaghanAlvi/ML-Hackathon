"""schemas.py: contract C1 (Search API). See docs/contracts.md.

Owner: Shared contract (maintained by Stream C) · Roadmap: Stage 0d
CONTRACT FILE: do not change without team approval. Mirrored in frontend/src/types/api.ts;
the canonical example is shared/mocks/search_response.json.
"""
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
