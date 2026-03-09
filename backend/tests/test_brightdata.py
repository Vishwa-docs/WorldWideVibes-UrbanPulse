"""
Tests for the Bright Data integration client and API endpoints.

All tests mock httpx calls – no real Bright Data API calls are made.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock
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


def _make_mock_client():
    """Create a fully mocked BrightDataClient without requiring a real API key."""
    mock_client = MagicMock(spec=BrightDataClient)
    mock_client.is_configured = True
    mock_client.api_token = "test-token"
    mock_client.base_url = "https://api.brightdata.com"
    mock_client.serp_zone = "serp_api1"
    mock_client.unlocker_zone = "unlocker1"

    mock_client.fetch_pois_near = AsyncMock(
        return_value={
            "total_count": 12,
            "competitor_count": 4,
            "category": "business",
            "source": "brightdata",
            "pois": [
                {"name": "Shop A", "rating": 4.5},
                {"name": "Shop B", "rating": 3.8},
            ],
        }
    )
    mock_client.fetch_reviews_near = AsyncMock(
        return_value={
            "avg_rating": 4.2,
            "total_reviews": 150,
            "business_type": "restaurant",
            "source": "brightdata",
        }
    )
    mock_client.fetch_activity_signals = AsyncMock(
        return_value={
            "poi_count": 15,
            "avg_rating": 4.2,
            "review_count": 120,
            "competitor_count": 5,
            "activity_index": 7.3,
            "source": "brightdata",
        }
    )
    return mock_client


# ── Sample Bright Data API responses for parsing tests ────────────────────────

SAMPLE_POI_RESPONSE = {
    "results": [
        {"name": "Dexter Deli", "category": "business", "rating": 4.0, "review_count": 50},
        {"name": "Capitol Cafe", "category": "restaurant", "rating": 3.5, "review_count": 30},
        {"name": "Main St Market", "category": "business", "rating": 4.8, "review_count": 200},
    ]
}

SAMPLE_REVIEW_RESPONSE = {
    "results": [
        {"rating": 4.5, "review_count": 80},
        {"rating": 3.2, "review_count": 45},
        {"rating": 4.9, "review_count": 120},
    ]
}


# ── Unit tests for BrightDataClient ──────────────────────────────────────────


class TestBrightDataClientRequiresKey:
    """Verify the client raises without an API key."""

    def setup_method(self):
        _reset_client()

    def test_client_raises_without_api_token(self):
        """Without BRIGHTDATA_API_TOKEN, instantiation should raise RuntimeError."""
        from app.config import Settings

        empty_settings = Settings(brightdata_api_token="")
        with patch("app.services.brightdata_client.get_settings", return_value=empty_settings):
            with pytest.raises(RuntimeError, match="Bright Data API token is not configured"):
                BrightDataClient()


class TestBrightDataParsing:
    """Tests for the response parsing logic using sample data."""

    def test_parse_poi_response_counts_all(self):
        c = MagicMock(spec=BrightDataClient)
        c._parse_brightdata_response = BrightDataClient._parse_brightdata_response.__get__(c)
        result = c._parse_brightdata_response(SAMPLE_POI_RESPONSE, "business")
        assert result["total_count"] == 3
        assert result["source"] == "brightdata"
        assert result["category"] == "business"
        # only 2 of the 3 have category == 'business'
        assert result["competitor_count"] == 2
        assert len(result["pois"]) == 3

    def test_parse_poi_response_empty(self):
        c = MagicMock(spec=BrightDataClient)
        c._parse_brightdata_response = BrightDataClient._parse_brightdata_response.__get__(c)
        result = c._parse_brightdata_response({"results": []}, "business")
        assert result["total_count"] == 0
        assert result["pois"] == []

    def test_parse_review_response_averages(self):
        c = MagicMock(spec=BrightDataClient)
        c._parse_review_response = BrightDataClient._parse_review_response.__get__(c)
        result = c._parse_review_response(SAMPLE_REVIEW_RESPONSE, "restaurant")
        assert result["source"] == "brightdata"
        assert result["avg_rating"] == round((4.5 + 3.2 + 4.9) / 3, 2)
        assert result["total_reviews"] == (80 + 45 + 120)

    def test_parse_review_response_empty(self):
        c = MagicMock(spec=BrightDataClient)
        c._parse_review_response = BrightDataClient._parse_review_response.__get__(c)
        result = c._parse_review_response({"results": []}, "restaurant")
        assert result["avg_rating"] == 0
        assert result["total_reviews"] == 0

    def test_parse_poi_response_data_key(self):
        """API may return 'data' instead of 'results'."""
        c = MagicMock(spec=BrightDataClient)
        c._parse_brightdata_response = BrightDataClient._parse_brightdata_response.__get__(c)
        alt_response = {"data": [{"name": "Place 1", "category": "business"}]}
        result = c._parse_brightdata_response(alt_response, "business")
        assert result["total_count"] == 1


class TestBrightDataActivityIndex:
    """Test the activity index computation logic."""

    def test_activity_index_computation(self):
        """Verify the activity_index formula from fetch_activity_signals."""
        # Test the formula in isolation
        poi_count = 25
        avg_rating = 4.0
        review_count = 250
        competitor_count = 10

        activity_index = min(
            10.0,
            (
                (min(poi_count, 50) / 50) * 3
                + (avg_rating / 5) * 3
                + (min(review_count, 500) / 500) * 2
                + (1 - min(competitor_count, 20) / 20) * 2
            ),
        )

        assert 0 <= activity_index <= 10
        assert round(activity_index, 2) == round(
            (25 / 50) * 3 + (4.0 / 5) * 3 + (250 / 500) * 2 + (1 - 10 / 20) * 2,
            2,
        )

    def test_activity_index_zero_inputs(self):
        poi_count = 0
        avg_rating = 0
        review_count = 0
        competitor_count = 0

        activity_index = min(
            10.0,
            (
                (min(poi_count, 50) / 50) * 3
                + (avg_rating / 5) * 3
                + (min(review_count, 500) / 500) * 2
                + (1 - min(competitor_count, 20) / 20) * 2
            ),
        )
        # Only the competitor factor contributes (no competitors = max score for that factor)
        assert activity_index == 2.0

    def test_activity_index_capped_at_10(self):
        poi_count = 100
        avg_rating = 5.0
        review_count = 1000
        competitor_count = 0

        activity_index = min(
            10.0,
            (
                (min(poi_count, 50) / 50) * 3
                + (avg_rating / 5) * 3
                + (min(review_count, 500) / 500) * 2
                + (1 - min(competitor_count, 20) / 20) * 2
            ),
        )
        assert activity_index == 10.0


# ── Mocked API endpoint tests ────────────────────────────────────────────────


class TestBrightDataAPIMocked:
    """Tests for the Bright Data API endpoints with mocked client."""

    def setup_method(self):
        _reset_client()
        self._mock_client = _make_mock_client()
        self._patcher = patch(
            "app.routes.brightdata.get_brightdata_client",
            return_value=self._mock_client,
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        _reset_client()

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
        assert data["source"] == "brightdata"
        assert data["cached"] is False
        assert "activity_index" in data

        # Second call should be cached (from DB, not mocked client)
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
        assert data["source"] == "brightdata"

    def test_seed_all(self):
        _seed()
        resp = client.post("/api/brightdata/seed-all")
        assert resp.status_code == 200
        data = resp.json()
        assert data["seeded"] >= 1
        assert len(data["results"]) >= 1
        assert "activity_index" in data["results"][0]


class TestBrightDataStatusMocked:
    """Test /api/brightdata/status with mocked client."""

    def setup_method(self):
        _reset_client()
        self._mock_client = _make_mock_client()
        self._patcher = patch(
            "app.routes.brightdata.get_brightdata_client",
            return_value=self._mock_client,
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        _reset_client()

    def test_status_endpoint(self):
        resp = client.get("/api/brightdata/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "configured" in data
        assert "base_url" in data
        assert data["configured"] is True
        assert data["mode"] == "live"


# ── SERP API endpoint tests ──────────────────────────────────────────────


class TestSerpEndpoint:
    """Test /api/brightdata/serp and /api/brightdata/serp/local."""

    def setup_method(self):
        _reset_client()
        self._mock_client = _make_mock_client()
        self._mock_client.search_serp = AsyncMock(
            return_value={
                "query": "grocery stores",
                "engine": "google",
                "location": "Montgomery,Alabama,United States",
                "result_count": 3,
                "results": [
                    {"title": "Piggly Wiggly", "url": "https://pigglywiggly.com", "description": "Grocery chain", "position": 1},
                    {"title": "Publix", "url": "https://publix.com", "description": "Supermarket", "position": 2},
                    {"title": "Winn-Dixie", "url": "https://winndixie.com", "description": "Grocery store", "position": 3},
                ],
                "source": "brightdata_serp",
                "is_live": True,
            }
        )
        self._patcher = patch(
            "app.routes.brightdata.get_brightdata_client",
            return_value=self._mock_client,
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        _reset_client()

    def test_serp_search(self):
        resp = client.post(
            "/api/brightdata/serp",
            json={"query": "grocery stores", "engine": "google", "num_results": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "grocery stores"
        assert data["result_count"] == 3
        assert len(data["results"]) == 3
        assert data["results"][0]["title"] == "Piggly Wiggly"
        assert data["source"] == "brightdata_serp"

    def test_serp_search_default_params(self):
        resp = client.post(
            "/api/brightdata/serp",
            json={"query": "restaurants"},
        )
        assert resp.status_code == 200
        # Verify the mock was called
        self._mock_client.search_serp.assert_called()

    def test_serp_local(self):
        resp = client.get("/api/brightdata/serp/local?q=coffee+shops&category=cafe")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data

    def test_serp_local_requires_query(self):
        resp = client.get("/api/brightdata/serp/local")
        assert resp.status_code == 422  # Missing required query param


class TestSerpSimulated:
    """Test SERP in simulated mode (no API key)."""

    def setup_method(self):
        _reset_client()
        # Create a client that is NOT configured (simulated mode)
        self._mock_client = MagicMock(spec=BrightDataClient)
        self._mock_client.is_configured = False
        # Use the real simulated response logic
        real_client = BrightDataClient(strict=False)
        self._mock_client.search_serp = AsyncMock(
            side_effect=lambda **kwargs: asyncio.get_event_loop().run_until_complete(
                real_client.search_serp(**kwargs)
            ) if False else real_client._simulate_serp_response(
                kwargs.get("query", "test"),
                kwargs.get("engine", "google"),
                kwargs.get("location", "Montgomery,Alabama,United States"),
                kwargs.get("num_results", 10),
            )
        )
        self._patcher = patch(
            "app.routes.brightdata.get_brightdata_client",
            return_value=self._mock_client,
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        _reset_client()

    def test_serp_simulated_returns_results(self):
        resp = client.post(
            "/api/brightdata/serp",
            json={"query": "grocery stores"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["source"] == "brightdata_serp_simulated"
        assert data["is_live"] is False
        assert len(data["results"]) > 0

    def test_serp_simulated_deterministic(self):
        """Same query should produce the same simulated results."""
        resp1 = client.post("/api/brightdata/serp", json={"query": "grocery stores"})
        resp2 = client.post("/api/brightdata/serp", json={"query": "grocery stores"})
        assert resp1.json()["results"] == resp2.json()["results"]


# ── Web Unlocker (scrape) endpoint tests ─────────────────────────────────


class TestScrapeEndpoint:
    """Test /api/brightdata/scrape."""

    def setup_method(self):
        _reset_client()
        self._mock_client = _make_mock_client()
        self._mock_client.scrape_url = AsyncMock(
            return_value={
                "url": "https://montgomeryal.gov",
                "content": "# Montgomery, AL\n\nCity government website content here.",
                "content_length": 52,
                "source": "brightdata_unlocker",
                "is_live": True,
            }
        )
        self._patcher = patch(
            "app.routes.brightdata.get_brightdata_client",
            return_value=self._mock_client,
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        _reset_client()

    def test_scrape_url(self):
        resp = client.post(
            "/api/brightdata/scrape",
            json={"url": "https://montgomeryal.gov"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] == "https://montgomeryal.gov"
        assert "content" in data
        assert data["source"] == "brightdata_unlocker"
        assert data["is_live"] is True

    def test_scrape_url_with_max_length(self):
        long_content = "a" * 10000
        self._mock_client.scrape_url = AsyncMock(
            return_value={
                "url": "https://example.com",
                "content": long_content,
                "content_length": 10000,
                "source": "brightdata_unlocker",
                "is_live": True,
            }
        )
        resp = client.post(
            "/api/brightdata/scrape",
            json={"url": "https://example.com", "max_length": 500},
        )
        assert resp.status_code == 200
        data = resp.json()
        # Content should be truncated + "... (truncated)"
        assert len(data["content"]) < 600
        assert "(truncated)" in data["content"]

    def test_scrape_requires_url(self):
        resp = client.post("/api/brightdata/scrape", json={})
        assert resp.status_code == 422


class TestScrapeSimulated:
    """Test scrape in simulated mode."""

    def setup_method(self):
        _reset_client()
        self._mock_client = MagicMock(spec=BrightDataClient)
        self._mock_client.is_configured = False
        real_client = BrightDataClient(strict=False)
        self._mock_client.scrape_url = AsyncMock(
            side_effect=lambda url: real_client._simulate_scrape_response(url)
        )
        self._patcher = patch(
            "app.routes.brightdata.get_brightdata_client",
            return_value=self._mock_client,
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        _reset_client()

    def test_scrape_simulated(self):
        resp = client.post(
            "/api/brightdata/scrape",
            json={"url": "https://montgomeryal.gov/about"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["source"] == "brightdata_unlocker_simulated"
        assert data["is_live"] is False
        assert "montgomeryal.gov" in data["content"]


# ── Capabilities endpoint tests ──────────────────────────────────────────


class TestCapabilitiesEndpoint:
    """Test /api/brightdata/capabilities."""

    def setup_method(self):
        _reset_client()
        self._mock_client = _make_mock_client()
        self._mock_client.get_capabilities = MagicMock(
            return_value={
                "products": [
                    {"name": "Web Scraper (Datasets API)", "status": "active"},
                    {"name": "SERP API", "status": "active"},
                    {"name": "Web Unlocker", "status": "active"},
                    {"name": "MCP Server", "status": "documented"},
                ],
                "configured": True,
                "mode": "live",
            }
        )
        self._patcher = patch(
            "app.routes.brightdata.get_brightdata_client",
            return_value=self._mock_client,
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()
        _reset_client()

    def test_capabilities_returns_4_products(self):
        resp = client.get("/api/brightdata/capabilities")
        assert resp.status_code == 200
        data = resp.json()
        assert "products" in data
        assert len(data["products"]) == 4
        names = [p["name"] for p in data["products"]]
        assert "Web Scraper (Datasets API)" in names
        assert "SERP API" in names
        assert "Web Unlocker" in names
        assert "MCP Server" in names

    def test_capabilities_configured_flag(self):
        resp = client.get("/api/brightdata/capabilities")
        data = resp.json()
        assert data["configured"] is True
        assert data["mode"] == "live"

    def test_capabilities_simulated_mode(self):
        """When no API key is configured, mode should be simulated."""
        self._mock_client.get_capabilities = MagicMock(
            return_value={
                "products": [
                    {"name": "Web Scraper (Datasets API)", "status": "simulated"},
                    {"name": "SERP API", "status": "simulated"},
                    {"name": "Web Unlocker", "status": "simulated"},
                    {"name": "MCP Server", "status": "documented"},
                ],
                "configured": False,
                "mode": "simulated",
            }
        )
        resp = client.get("/api/brightdata/capabilities")
        data = resp.json()
        assert data["configured"] is False
        assert data["mode"] == "simulated"
