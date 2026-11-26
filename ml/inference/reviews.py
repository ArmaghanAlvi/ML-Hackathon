"""reviews.py: contract C3 (see docs/contracts.md).

Owner: Stream B · Roadmap: Stage 7 (B1 stub by Sat 11/28, B8 real model by Wed 12/2)
Purpose: probability that each review is helpful, in [0, 1].

STUB: not implemented yet. Placeholder heuristic: helpfulness = min(1.0, word_count / 100).
Stream B will replace it with the fine-tuned DistilBERT model (7c). Keep the interface.
"""
from __future__ import annotations


def score_reviews(texts: list[str]) -> list[float]:
    """Return P(helpful) per review, same length and order as `texts`, each in [0, 1]."""
    return [min(1.0, len((t or "").split()) / 100.0) for t in texts]
