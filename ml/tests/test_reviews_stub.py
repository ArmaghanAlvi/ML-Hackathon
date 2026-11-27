"""Tests for the C3 reviews stub (Stream B)."""
from ml.inference.reviews import length_score, score_reviews


def test_length_and_range() -> None:
    texts = ["", "short", "word " * 50, "word " * 500]
    out = score_reviews(texts)
    assert len(out) == len(texts)
    assert all(0.0 <= v <= 1.0 for v in out)


def test_empty_input() -> None:
    assert score_reviews([]) == []


def test_length_score_values() -> None:
    assert length_score(["", "one two three", " ".join(["w"] * 150)]) == [0.0, 0.03, 1.0]


def test_score_reviews_uses_length_score() -> None:
    texts = ["", "one two three", None, " ".join(["w"] * 150)]
    assert score_reviews(texts) == length_score(texts)
    assert score_reviews([]) == []
