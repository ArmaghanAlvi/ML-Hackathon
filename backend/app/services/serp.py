"""serp.py

Owner: Stream C · Roadmap: Stage 4b (due Sun 11/29; Stream B needs it Tue 12/1)
Purpose: the ONLY place that calls SerpApi (Google Lens + Google Shopping).

Rules (see CLAUDE.md quota rule):
- Every call goes through cache.py: compute cache_key, return cache.load() on a hit, otherwise
  call SerpApi (httpx, with timeouts), cache.save() the RAW response, and return it.
- Every real call logs quota use (engine, key, timestamp).
- With DEMO_CACHED=true, never call the network: a cache miss is an error.
- Tests must never reach this network path.

STUB: not implemented yet.
"""
from __future__ import annotations

from typing import Any


def lens_search(image_url: str | None = None, image_bytes: bytes | None = None) -> dict[str, Any]:
    """Google Lens visual search by URL or uploaded bytes. Returns the raw SerpApi JSON (cached, C4)."""
    raise NotImplementedError("TODO: Stage 4b (serp.lens_search)")


def shopping_search(query: str) -> dict[str, Any]:
    """Google Shopping search on the top match title (+ text refinement). Raw SerpApi JSON (cached, C4)."""
    raise NotImplementedError("TODO: Stage 4b (serp.shopping_search)")
