"""Shared fixtures for backend tests. Tests never call the network."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
MOCK_PATH = REPO_ROOT / "shared" / "mocks" / "search_response.json"
VECTORS_PATH = REPO_ROOT / "shared" / "ranking_test_vectors.json"


@pytest.fixture(autouse=True)
def _isolated_settings(monkeypatch, tmp_path):
    """Default (mock) settings regardless of a developer's .env; cache writes go to tmp."""
    from backend.app.config import get_settings

    monkeypatch.setenv("USE_MOCK_RESPONSE", "true")
    monkeypatch.setenv("CACHE_DIR", str(tmp_path / "cache"))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    from backend.app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_json() -> dict:
    return json.loads(MOCK_PATH.read_text())
