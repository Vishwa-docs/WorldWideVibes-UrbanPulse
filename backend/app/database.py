"""
Database engine and session management for UrbanPulse.

Uses SQLModel (SQLAlchemy + Pydantic) with an async-friendly
synchronous SQLite backend.
"""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Import all models so their tables are registered with SQLModel.metadata
from app.models import (  # noqa: F401
    Property, PropertyScore, WebSignal, Incident,
    ServiceLocation, CityProject, Watchlist, SignalSnapshot,
)

# SQLite requires `check_same_thread=False` when used with FastAPI's
# threaded request handling.
connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args=connect_args,
)


def create_db_and_tables() -> None:
    """Create all tables registered with SQLModel.metadata."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session per request."""
    with Session(engine) as session:
        yield session
