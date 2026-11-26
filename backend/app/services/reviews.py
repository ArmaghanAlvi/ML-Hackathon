"""reviews.py (service)

Owner: Stream C · Roadmap: Stage 7e
Purpose: wrap ml.inference.reviews.score_reviews (contract C3). Later: fetch reviews for the top
few products only (cached via serp.py/cache.py), compute trust_rating and pick the 2-3 most
informative reviews per card.

STUB: review fetching and trust_rating are not implemented yet; scoring calls the C3 stub.
"""
from __future__ import annotations

from ml.inference.reviews import score_reviews


def score(texts: list[str]) -> list[float]:
    """P(helpful) per review text, in [0, 1]."""
    return score_reviews(texts)


def trust_rating(ratings: list[float], texts: list[str]) -> float | None:
    """Helpfulness-weighted mean rating for one product."""
    raise NotImplementedError("TODO: Stage 7e (trust_rating)")
