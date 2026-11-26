"""cache.py: contract C4 (see docs/contracts.md).

Owner: Stream C · Roadmap: Stage 4b / 4g
Purpose: disk cache of RAW SerpApi responses at <CACHE_DIR>/<sha256>.json.
Implemented for real (not a stub): tiny, and serp.py + tests rely on it.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from backend.app.config import get_settings


def cache_key(image_bytes: bytes, engine: str, text: str | None) -> str:
    """sha256(image_bytes + engine + (text or "")) as a hex digest."""
    h = hashlib.sha256()
    h.update(image_bytes)
    h.update(engine.encode("utf-8"))
    h.update((text or "").encode("utf-8"))
    return h.hexdigest()


def _path(key: str, cache_dir: str | Path | None = None) -> Path:
    return Path(cache_dir or get_settings().CACHE_DIR) / f"{key}.json"


def load(key: str, cache_dir: str | Path | None = None) -> dict[str, Any] | None:
    """Return the cached raw response for `key`, or None if missing."""
    p = _path(key, cache_dir)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save(key: str, data: dict[str, Any], cache_dir: str | Path | None = None) -> Path:
    """Write the raw response for `key` (atomic replace). Returns the file path."""
    p = _path(key, cache_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data), encoding="utf-8")
    tmp.replace(p)
    return p
