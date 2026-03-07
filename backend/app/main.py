"""
UrbanPulse API – main application entry-point.

Configures middleware, lifespan events, and route inclusion.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import create_db_and_tables
from app.routes.health import router as health_router
from app.routes.properties import router as properties_router
from app.routes.scores import router as scores_router
from app.routes.compare import router as compare_router
from app.routes.watchlist import router as watchlist_router
from app.routes.export import router as export_router
from app.routes.brightdata import router as brightdata_router
from app.routes.agent import router as agent_router
from app.routes.demographics import router as demographics_router
from app.routes.walkscore import router as walkscore_router
from app.routes.insights import router as insights_router
from app.routes.montgomery import router as montgomery_router
from app.routes.opportunities import router as opportunities_router
from app.routes.recommendations import (
    router as recommendations_router,
    evidence_router,
)
from app.routes.signals import router as signals_router
from app.routes.weather import router as weather_router


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle hook."""
    # Startup: ensure database tables exist.
    create_db_and_tables()

    # Auto-seed if database is empty (first deploy / fresh container).
    from sqlmodel import Session, select
    from app.models.property import Property
    from app.database import engine as db_engine

    with Session(db_engine) as session:
        count = session.exec(select(Property)).first()
        if count is None:
            import logging
            logging.getLogger("urbanpulse").info("Empty database detected — running auto-seed…")
            from scripts.seed_sample import main as seed_main
            seed_main()

    yield
    # Shutdown: add cleanup logic here if needed.


# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="UrbanPulse API",
    version="1.0.0",
    description="Backend API for the UrbanPulse civic-intelligence platform.",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(health_router)
app.include_router(properties_router)
app.include_router(scores_router)
app.include_router(compare_router)
app.include_router(watchlist_router)
app.include_router(export_router)
app.include_router(brightdata_router)
app.include_router(agent_router)
app.include_router(demographics_router)
app.include_router(walkscore_router)
app.include_router(insights_router)
app.include_router(montgomery_router)
app.include_router(opportunities_router)
app.include_router(recommendations_router)
app.include_router(evidence_router)
app.include_router(signals_router)
app.include_router(weather_router)

# ── Static Frontend (production) ──────────────────────────────────────────────
# In production the Dockerfile builds the React app and copies the output to
# /app/static.  We mount that directory and add a catch-all so that every
# non-API path serves index.html (SPA client-side routing).

_static_dir = Path(__file__).resolve().parent.parent / "static"

if _static_dir.is_dir():
    # Serve assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=_static_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def _spa_fallback(full_path: str):
        """Return the requested file if it exists, otherwise index.html."""
        file = _static_dir / full_path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(_static_dir / "index.html")
