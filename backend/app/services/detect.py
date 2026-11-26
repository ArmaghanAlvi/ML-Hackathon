"""detect.py

Owner: Stream C · Roadmap: Stage 1b (detector test), 4c (service)
Purpose: return product boxes (normalized, contract C1 Box) for an image, or apply the CP1
fallback (whole image + user-drawn box). Detector choice is recorded in docs/decisions.md.

STUB: not implemented yet. Do not import ultralytics at module level.
"""
from __future__ import annotations

from PIL import Image

from backend.app.schemas import Box


def detect(image: Image.Image) -> list[Box]:
    """Detect products in `image`; boxes sorted by score, highest first."""
    raise NotImplementedError("TODO: Stage 4c (detect)")
