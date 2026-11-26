"""Tests for the C3 reviews stub (Stream B)."""
from ml.inference.reviews import score_reviews


def test_length_and_range() -> None:
    texts = ["", "short", "word " * 50, "word " * 500]
    out = score_reviews(texts)
    assert len(out) == len(texts)
    assert all(0.0 <= v <= 1.0 for v in out)


def test_empty_input() -> None:
    assert score_reviews([]) == []
