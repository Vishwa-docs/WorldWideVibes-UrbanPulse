"""
Shared test fixtures for UrbanPulse backend tests.

Provides a single in-memory SQLite engine and DB override
so all test modules share the same database connection
and don't interfere with each other.
"""

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app

# Single shared test engine for ALL test modules
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def _test_session_override():
    with Session(TEST_ENGINE) as session:
        yield session


# Apply the override ONCE at import time
app.dependency_overrides[get_session] = _test_session_override


def reset_test_db():
    """Drop and recreate all tables for a clean slate."""
    SQLModel.metadata.drop_all(TEST_ENGINE)
    SQLModel.metadata.create_all(TEST_ENGINE)


def get_test_session():
    """Get a direct session for seeding test data."""
    return Session(TEST_ENGINE)
