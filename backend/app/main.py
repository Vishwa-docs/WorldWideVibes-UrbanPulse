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
