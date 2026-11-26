"""main.py

Owner: Stream C · Roadmap: Stage 4a (skeleton), 4h (serving the built frontend)
Purpose: create the FastAPI app, CORS, /health, the /api routers, and (if built) the SPA.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.config import get_settings
from backend.app.routes import search
from backend.app.services import matcher as matcher_service

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    matcher_service.get_matcher()  # load the matcher once at startup (C2 stub is cheap)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Product Compare API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "mock": get_settings().USE_MOCK_RESPONSE}

    app.include_router(search.router, prefix="/api")

    # Registered AFTER the API routes so /api/* and /health always win.
    if FRONTEND_DIST.is_dir():
        dist = FRONTEND_DIST.resolve()

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa(full_path: str) -> FileResponse:
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404)
            candidate = (dist / full_path).resolve()
            if full_path and candidate.is_file() and candidate.is_relative_to(dist):
                return FileResponse(candidate)
            return FileResponse(dist / "index.html")  # SPA fallback

    return app


app = create_app()
