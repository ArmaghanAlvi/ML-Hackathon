"""Tests for the C2 matcher stub (Stream A). No network, no torch."""
import json

import numpy as np
import pytest
from PIL import Image

from ml.inference.matcher import ALLOWED_LABELS, Matcher


def _img(seed: int, color: tuple[int, int, int] | None = None) -> Image.Image:
    if color is not None:
        return Image.new("RGB", (64, 64), color)
    rng = np.random.default_rng(seed)
    return Image.fromarray(rng.integers(0, 256, (64, 64, 3), dtype=np.uint8))


@pytest.fixture
def matcher() -> Matcher:
    return Matcher.load()  # repo default ml/artifacts/thresholds.json


def test_score_one_float_per_candidate_in_range(matcher: Matcher) -> None:
    cands = [_img(1), _img(2), _img(0, (255, 0, 0)), _img(0, (0, 0, 255))]
    scores = matcher.score(_img(0), cands)
    assert len(scores) == len(cands)
    assert all(isinstance(s, float) and 0.0 <= s <= 1.0 for s in scores)


def test_self_similarity(matcher: Matcher) -> None:
    q = _img(7)
    assert matcher.score(q, [q.copy()])[0] >= 0.99


def test_label_values_and_thresholds(matcher: Matcher) -> None:
    scores = [0.0, matcher.similar - 1e-6, matcher.similar, matcher.identical - 1e-6, matcher.identical, 1.0]
    labels = matcher.label(scores)
    assert set(labels) <= set(ALLOWED_LABELS)
    assert labels == ["none", "none", "similar", "similar", "identical", "identical"]


def test_load_custom_thresholds(tmp_path) -> None:
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"identical": 0.9, "similar": 0.5}))
    m = Matcher.load(thresholds_path=str(p))
    assert m.label([0.95, 0.6, 0.1]) == ["identical", "similar", "none"]
