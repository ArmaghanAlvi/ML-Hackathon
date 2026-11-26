"""matcher.py: contract C2 (see docs/contracts.md).

Owner: Stream A · Roadmap: Stage 3 (A2 stub by Sat 11/28, A8 real matcher by Wed 12/2)
Purpose: score how well each candidate product image matches the query image, and turn
scores into "identical" / "similar" / "none" labels using thresholds from C5.

STUB: not implemented yet. The scoring below is a placeholder, NOT the real model:
cosine similarity of normalized 8x8x8 RGB colour histograms (Pillow + NumPy only, no torch).
It returns real, deterministic numbers so the backend and evaluation can integrate today.
Stream A will replace the scoring with zero-shot SigLIP 2 by Sat 11/28, then with the
trained projection head by Wed 12/2. Keep the public interface unchanged when doing so.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

DEFAULT_THRESHOLDS_PATH = "ml/artifacts/thresholds.json"
ALLOWED_LABELS = ("identical", "similar", "none")
_BINS = 8


def _histogram(img: Image.Image) -> np.ndarray:
    """L2-normalized 8x8x8 RGB colour histogram (512-dim)."""
    arr = np.asarray(img.convert("RGB").resize((128, 128)), dtype=np.uint8)
    idx = (arr // (256 // _BINS)).reshape(-1, 3).astype(np.int64)
    flat = idx[:, 0] * _BINS * _BINS + idx[:, 1] * _BINS + idx[:, 2]
    hist = np.bincount(flat, minlength=_BINS**3).astype(np.float64)
    norm = np.linalg.norm(hist)
    return hist / norm if norm > 0 else hist


class Matcher:
    """C2 matcher. STUB scoring (colour histogram) until Stream A swaps in SigLIP 2 / trained head."""

    def __init__(self, identical: float, similar: float, weights_dir: str | None = None) -> None:
        if not 0 <= similar <= identical <= 1:
            raise ValueError("thresholds must satisfy 0 <= similar <= identical <= 1")
        self.identical = float(identical)
        self.similar = float(similar)
        self.weights_dir = weights_dir  # unused by the stub

    @classmethod
    def load(cls, weights_dir: str | None = None, thresholds_path: str | None = None) -> "Matcher":
        """Load thresholds from `thresholds_path`, else $THRESHOLDS_PATH, else the default path."""
        path = Path(thresholds_path or os.environ.get("THRESHOLDS_PATH") or DEFAULT_THRESHOLDS_PATH)
        data = json.loads(path.read_text())
        return cls(identical=data["identical"], similar=data["similar"], weights_dir=weights_dir)

    def score(self, query: Image.Image, candidates: list[Image.Image]) -> list[float]:
        """One score in [0, 1] per candidate (higher = more likely the same product)."""
        q = _histogram(query)
        out: list[float] = []
        for cand in candidates:
            sim = float(np.dot(q, _histogram(cand)))
            out.append(float(np.clip(sim, 0.0, 1.0)))
        return out

    def label(self, scores: list[float]) -> list[str]:
        """Map scores to "identical" | "similar" | "none" using the loaded thresholds."""
        labels: list[str] = []
        for s in scores:
            if s >= self.identical:
                labels.append("identical")
            elif s >= self.similar:
                labels.append("similar")
            else:
                labels.append("none")
        return labels

    def heatmap(self, query: Image.Image, candidate: Image.Image) -> np.ndarray:
        """Stretch goal (Stage 9c): patch-similarity heatmap. STUB."""
        raise NotImplementedError("TODO: Stage 9c (Matcher.heatmap)")
