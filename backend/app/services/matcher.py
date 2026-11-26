"""matcher.py (service)

Owner: Stream C · Roadmap: Stage 4d
Purpose: thin wrapper around ml.inference.matcher.Matcher (contract C2). The matcher is loaded
once (at app startup via main.py's lifespan, or on first use) and reused for every request.
Swapping in Stream A's real model must not require changes here.

STUB: candidate image fetching is not implemented yet; scoring calls the C2 stub matcher.
"""
from __future__ import annotations

from functools import lru_cache

from PIL import Image

from backend.app.config import get_settings
from ml.inference.matcher import Matcher


@lru_cache(maxsize=1)
def get_matcher() -> Matcher:
    """Load the matcher once using THRESHOLDS_PATH from settings."""
    return Matcher.load(thresholds_path=get_settings().THRESHOLDS_PATH)


def score_candidates(query: Image.Image, candidates: list[Image.Image]) -> tuple[list[float], list[str]]:
    """Score and label candidate images against the query crop. Returns (scores, labels)."""
    m = get_matcher()
    scores = m.score(query, candidates)
    return scores, m.label(scores)
