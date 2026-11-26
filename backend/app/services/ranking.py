"""ranking.py: contract C7 (see docs/contracts.md).

Owner: Stream C · Roadmap: Stage 4e
Purpose: adjusted (Bayesian) rating, Pareto frontier, weighted best value, and the top-3 lists.
Must pass shared/ranking_test_vectors.json (same vectors as frontend/src/lib/ranking.ts).

Pool: candidates with match_label in {identical, similar}, non-null price, and (for rating-based
lists) non-null rating.

STUB: not implemented yet.
"""
from __future__ import annotations

from typing import Any

Cand = dict[str, Any]  # needs at least: id, price, rating, review_count


def bayesian_average(candidates: list[Cand]) -> dict[str, float]:
    """adj = (v/(v+m))*R + (m/(v+m))*C per candidate id.

    R = candidate rating, v = review_count (None -> 0), C = mean rating of the pool,
    m = median review count of the pool (minimum 1).
    """
    raise NotImplementedError("TODO: Stage 4e (bayesian_average)")


def pareto_frontier(candidates: list[Cand], adjusted: dict[str, float]) -> list[str]:
    """Ids not dominated by any other. A dominates B if price_A <= price_B and adj_A >= adj_B,
    with at least one strict."""
    raise NotImplementedError("TODO: Stage 4e (pareto_frontier)")


def weighted_value(candidates: list[Cand], adjusted: dict[str, float], weight: float = 0.5) -> dict[str, float]:
    """score = w*norm(adj) + (1-w)*(1 - norm(log(price))); norm = min-max over the pool,
    0.5 if all values are equal. Default w = 0.5."""
    raise NotImplementedError("TODO: Stage 4e (weighted_value)")


def top_k_lists(candidates: list[Cand], weight: float = 0.5, k: int = 3) -> dict[str, Any]:
    """Return {"adjusted_rating", "top_cheapest", "top_rated", "frontier", "best_value"}.

    top_cheapest: k lowest prices. top_rated: k highest adj, ties -> higher review_count.
    best_value: k highest weighted_value.
    """
    raise NotImplementedError("TODO: Stage 4e (top_k_lists)")
