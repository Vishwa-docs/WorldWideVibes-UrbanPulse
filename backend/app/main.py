"""
UrbanPulse API – main application entry-point.

Configures middleware, lifespan events, and route inclusion.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
