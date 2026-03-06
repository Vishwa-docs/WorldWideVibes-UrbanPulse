"""
Tests for the Bright Data integration client and API endpoints.

All tests run in simulated (mock) mode – no real Bright Data API calls.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models.property import Property, WebSignal
from app.services.brightdata_client import BrightDataClient, get_brightdata_client
import app.services.brightdata_client as bd_module
from tests.conftest import TEST_ENGINE, reset_test_db, get_test_session

# ── Test DB setup ─────────────────────────────────────────────────────────────

client = TestClient(app)


def _reset_db():
    """Drop and recreate all tables for a clean slate."""
    reset_test_db()


def _seed():
    """Seed a test property."""
    _reset_db()
    with Session(TEST_ENGINE) as session:
        p = Property(
            parcel_id="BD-001",
            address="100 Commerce St",
            latitude=32.38,
            longitude=-86.30,
            property_type="commercial",
            is_vacant=True,
            is_city_owned=False,
            neighborhood="Downtown",
        )
        session.add(p)
        session.commit()
        session.refresh(p)
        return p.id


# ── Reset the singleton client between tests ─────────────────────────────────

def _reset_client():
    bd_module._client = None


# ── Unit tests for BrightDataClient ──────────────────────────────────────────


class TestBrightDataClientMock:
    """Tests for the client in simulated (unconfigured) mode."""

    def setup_method(self):
        _reset_client()

    def test_client_is_not_configured_by_default(self):
        """With no API token set the client should be in simulated mode."""
        c = BrightDataClient()
        assert not c.is_configured

    @pytest.mark.asyncio
    async def test_mock_pois_returns_data(self):
        c = BrightDataClient()
        result = await c.fetch_pois_near(32.38, -86.30)
        assert result["source"] == "simulated"
        assert "total_count" in result
        assert "pois" in result
        assert len(result["pois"]) > 0

    @pytest.mark.asyncio
    async def test_mock_reviews_returns_data(self):
        c = BrightDataClient()
        result = await c.fetch_reviews_near(32.38, -86.30)
        assert result["source"] == "simulated"
        assert "avg_rating" in result
        assert "total_reviews" in result
        assert 0 < result["avg_rating"] <= 5.0

    @pytest.mark.asyncio
    async def test_mock_consistency(self):
        """Same coordinates should produce the same mock data."""
        c = BrightDataClient()
        r1 = await c.fetch_pois_near(32.38, -86.30)
        r2 = await c.fetch_pois_near(32.38, -86.30)
        assert r1["total_count"] == r2["total_count"]
        assert r1["competitor_count"] == r2["competitor_count"]

    @pytest.mark.asyncio
    async def test_activity_signals_aggregation(self):
        c = BrightDataClient()
        signals = await c.fetch_activity_signals(32.38, -86.30)
        assert signals["source"] == "simulated"
        assert "poi_count" in signals
        assert "avg_rating" in signals
        assert "review_count" in signals
        assert "competitor_count" in signals
        assert "activity_index" in signals
        assert 0 <= signals["activity_index"] <= 10

    @pytest.mark.asyncio
    async def test_activity_index_range(self):
        """Activity index must be between 0 and 10 for various coords."""
        c = BrightDataClient()
        for lat, lng in [(32.38, -86.30), (33.0, -85.0), (31.5, -87.0)]:
            signals = await c.fetch_activity_signals(lat, lng)
            assert 0 <= signals["activity_index"] <= 10


# ── API endpoint tests ───────────────────────────────────────────────────────


class TestBrightDataAPI:
    """Tests for the Bright Data API endpoints."""

    def setup_method(self):
        _reset_client()

    def test_status_endpoint(self):
        resp = client.get("/api/brightdata/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "configured" in data
        assert "mode" in data
        assert data["mode"] == "simulated"

    def test_signals_not_found(self):
        _reset_db()
        resp = client.get("/api/brightdata/signals/9999")
        assert resp.status_code == 404

    def test_signals_fetch_and_cache(self):
        pid = _seed()
        resp = client.get(f"/api/brightdata/signals/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["property_id"] == pid
        assert data["source"] == "simulated"
        assert data["cached"] is False
        assert "activity_index" in data

        # Second call should be cached
        resp2 = client.get(f"/api/brightdata/signals/{pid}")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["cached"] is True

    def test_refresh_not_found(self):
        _reset_db()
        resp = client.post("/api/brightdata/refresh/9999")
        assert resp.status_code == 404

    def test_refresh_signals(self):
        pid = _seed()
        # First fetch to cache
        client.get(f"/api/brightdata/signals/{pid}")
        # Refresh
        resp = client.post(f"/api/brightdata/refresh/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["refreshed"] is True
        assert data["source"] == "simulated"

    def test_seed_all(self):
        _seed()
        resp = client.post("/api/brightdata/seed-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["seeded"] >= 1
        assert len(data["results"]) >= 1
        assert "activity_index" in data["results"][0]
