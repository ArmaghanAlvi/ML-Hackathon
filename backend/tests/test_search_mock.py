from backend.app.config import get_settings
from backend.app.schemas import SearchResponse


def test_search_returns_mock(client):
    r = client.post("/api/search", json={"image_url": "https://example.com/a.jpg"})
    assert r.status_code == 200
    body = SearchResponse.model_validate(r.json())
    assert len(body.candidates) == 8


def test_search_rejects_empty_body(client):
    assert client.post("/api/search", json={}).status_code == 422


def test_search_live_not_implemented(client, monkeypatch):
    monkeypatch.setenv("USE_MOCK_RESPONSE", "false")
    get_settings.cache_clear()
    r = client.post("/api/search", json={"image_url": "https://example.com/a.jpg"})
    assert r.status_code == 501
