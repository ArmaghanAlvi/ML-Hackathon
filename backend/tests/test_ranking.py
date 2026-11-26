"""C7 ranking tests driven by shared/ranking_test_vectors.json. Skipped while `cases` is empty."""
import json
from pathlib import Path

import pytest

from backend.app.services import ranking

VECTORS_PATH = Path(__file__).resolve().parents[2] / "shared" / "ranking_test_vectors.json"

CASES = json.loads(VECTORS_PATH.read_text())["cases"]
TOL = 1e-6


@pytest.mark.skipif(not CASES, reason="shared/ranking_test_vectors.json has no cases yet (Stream C, Stage 4e)")
@pytest.mark.parametrize("case", CASES, ids=[c.get("name", str(i)) for i, c in enumerate(CASES)])
def test_ranking_vector(case):
    inp, exp = case["input"], case["expected"]
    out = ranking.top_k_lists(inp["candidates"], weight=inp.get("weight", 0.5))
    for cid, val in exp["adjusted_rating"].items():
        assert out["adjusted_rating"][cid] == pytest.approx(val, abs=TOL)
    assert out["top_cheapest"] == exp["top_cheapest"]
    assert out["top_rated"] == exp["top_rated"]
    assert sorted(out["frontier"]) == sorted(exp["frontier"])
    assert out["best_value"] == exp["best_value"]
