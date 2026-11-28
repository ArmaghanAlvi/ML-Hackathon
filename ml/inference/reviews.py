"""reviews.py: contract C3 (see docs/contracts.md).

Owner: Stream B · Roadmap: Stage 7 (B1 stub by Sat 11/28, B8 real model by Wed 12/2)
Purpose: probability that each review is helpful, in [0, 1].

STUB: not implemented yet. Placeholder heuristic: helpfulness = min(1.0, word_count / 100).
Stream B will replace it with the fine-tuned DistilBERT model (7c). Keep the interface.
"""
from __future__ import annotations


def length_score(texts: list[str]) -> list[float]:
    """Length heuristic: min(1, word_count / 100) per review, same length and order as `texts`.

    Stream B's Stage 4b-i baseline, and the Stage 4e fallback when the trained model can't load.
    `reviews_prepare.py scan` counts words the same way (`len((text or "").split())`).
    """
    return [min(1.0, len((t or "").split()) / 100) for t in texts]


def score_reviews(texts: list[str]) -> list[float]:
    """Return P(helpful) per review, same length and order as `texts`, each in [0, 1]."""
    return length_score(texts)
