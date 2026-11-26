"""search.py

Owner: Stream C · Roadmap: Stage 4a (mock), Stage 4 (live pipeline)
Purpose: POST /api/search (contract C1).

STUB: the live pipeline is not implemented yet. With USE_MOCK_RESPONSE=true this returns the
canonical mock shared/mocks/search_response.json, validated as a SearchResponse.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.app.config import get_settings
from backend.app.schemas import SearchRequest, SearchResponse

REPO_ROOT = Path(__file__).resolve().parents[3]
MOCK_PATH = REPO_ROOT / "shared" / "mocks" / "search_response.json"

router = APIRouter(tags=["search"])


def load_mock() -> SearchResponse:
    return SearchResponse.model_validate(json.loads(MOCK_PATH.read_text()))


@router.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    if get_settings().USE_MOCK_RESPONSE:
        return load_mock()
    # TODO (Stage 4): detect -> serp (cached) -> matcher -> ranking -> reviews
    raise HTTPException(status_code=501, detail="live pipeline not implemented (Stream C, Stage 4)")
