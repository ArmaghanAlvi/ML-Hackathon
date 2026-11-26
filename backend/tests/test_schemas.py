import pytest
from pydantic import ValidationError

from backend.app.schemas import SearchRequest, SearchResponse


def test_canonical_mock_validates(mock_json):
    resp = SearchResponse.model_validate(mock_json)
    ids = {c.id for c in resp.candidates}
    assert len(resp.candidates) == 8
    for field in ("top_cheapest", "top_rated", "best_value", "frontier"):
        assert set(getattr(resp, field)) <= ids, field
    labels = [c.match_label for c in resp.candidates]
    assert labels.count("identical") == 3 and labels.count("similar") == 3 and labels.count("none") == 2
    assert any(c.rating is None for c in resp.candidates)
    assert any(c.review_count is None for c in resp.candidates)
    assert resp.cached is False


def test_request_needs_an_image():
    with pytest.raises(ValidationError):
        SearchRequest()


def test_request_rejects_both_images():
    with pytest.raises(ValidationError):
        SearchRequest(image_url="https://example.com/a.jpg", image_base64="aGVsbG8=")


def test_request_accepts_one_image():
    assert SearchRequest(image_url="https://example.com/a.jpg").image_url
    assert SearchRequest(image_base64="aGVsbG8=").image_base64
