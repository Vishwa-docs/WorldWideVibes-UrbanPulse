"""
Tests for new services and endpoints: Google Places, Census/Demographics,
Walk Score, and their API routes.

All external API calls (Google Maps, Census Bureau, httpx) are mocked.
"""

import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models.property import Property, PropertyScore
from tests.conftest import TEST_ENGINE, reset_test_db, get_test_session

# ── Test DB setup ─────────────────────────────────────────────────────────────

client = TestClient(app)


def _reset_db():
    reset_test_db()


def _seed():
    """Seed a test property for walk-score and other endpoint tests."""
    _reset_db()
    with Session(TEST_ENGINE) as session:
        p = Property(
            parcel_id="NF-001",
            address="300 Water St",
            latitude=32.3780,
            longitude=-86.3090,
            property_type="commercial",
            zoning="C-2",
            is_vacant=True,
            is_city_owned=False,
            lot_size_sqft=6000.0,
            building_sqft=4000.0,
            assessed_value=175000.0,
            year_built=1990,
            neighborhood="Downtown",
            council_district="1",
        )
        session.add(p)
        session.commit()
        session.refresh(p)
        return p.id


# ── Google Places service tests ───────────────────────────────────────────────


class TestGooglePlacesService:
    """Test GooglePlacesService logic with mocked googlemaps client."""

    def test_raises_without_api_key(self):
        """Without GOOGLE_PLACES_API_KEY, instantiation should raise RuntimeError."""
        from app.services.google_places import GooglePlacesService
        from app.config import Settings

        empty_settings = Settings(google_places_api_key="")
        with patch("app.services.google_places.get_settings", return_value=empty_settings):
            with pytest.raises(RuntimeError, match="Google Places API key is not configured"):
                GooglePlacesService()

    @patch("app.services.google_places.get_settings")
    @patch("app.services.google_places.googlemaps.Client")
    def test_nearby_pois(self, mock_gm_client_cls, mock_settings):
        mock_settings.return_value.google_places_api_key = "test-key"
        mock_gm_instance = MagicMock()
        mock_gm_client_cls.return_value = mock_gm_instance
        mock_gm_instance.places_nearby.return_value = {
            "results": [
                {
                    "place_id": "p1",
                    "name": "Test Store",
                    "vicinity": "123 Main St",
                    "rating": 4.5,
                    "user_ratings_total": 100,
                    "types": ["store"],
                    "geometry": {"location": {"lat": 32.38, "lng": -86.31}},
                    "business_status": "OPERATIONAL",
                },
                {
                    "place_id": "p2",
                    "name": "Test Cafe",
                    "vicinity": "456 Oak Ave",
                    "rating": 3.8,
                    "user_ratings_total": 50,
                    "types": ["cafe"],
                    "geometry": {"location": {"lat": 32.381, "lng": -86.309}},
                    "business_status": "OPERATIONAL",
                },
            ]
        }

        from app.services.google_places import GooglePlacesService

        svc = GooglePlacesService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.nearby_pois(32.38, -86.31)
        )

        assert result["total"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["name"] == "Test Store"
        assert result["results"][0]["rating"] == 4.5

    @patch("app.services.google_places.get_settings")
    @patch("app.services.google_places.googlemaps.Client")
    def test_place_details(self, mock_gm_client_cls, mock_settings):
        mock_settings.return_value.google_places_api_key = "test-key"
        mock_gm_instance = MagicMock()
        mock_gm_client_cls.return_value = mock_gm_instance
        mock_gm_instance.place.return_value = {
            "result": {
                "name": "Dexter Market",
                "formatted_address": "200 Dexter Ave, Montgomery, AL",
                "rating": 4.2,
                "user_ratings_total": 85,
                "price_level": 2,
                "opening_hours": {"open_now": True},
                "types": ["grocery_or_supermarket", "store"],
                "business_status": "OPERATIONAL",
            }
        }

        from app.services.google_places import GooglePlacesService

        svc = GooglePlacesService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.place_details("ChIJ_test123")
        )

        assert result["name"] == "Dexter Market"
        assert result["rating"] == 4.2
        assert result["user_ratings_total"] == 85
        assert result["place_id"] == "ChIJ_test123"

    @patch("app.services.google_places.get_settings")
    @patch("app.services.google_places.googlemaps.Client")
    def test_nearby_competitors(self, mock_gm_client_cls, mock_settings):
        mock_settings.return_value.google_places_api_key = "test-key"
        mock_gm_instance = MagicMock()
        mock_gm_client_cls.return_value = mock_gm_instance
        mock_gm_instance.places_nearby.return_value = {
            "results": [
                {
                    "place_id": "c1",
                    "name": "Piggly Wiggly",
                    "vicinity": "100 Bell St",
                    "rating": 3.9,
                    "user_ratings_total": 200,
                    "geometry": {"location": {"lat": 32.38, "lng": -86.31}},
                },
                {
                    "place_id": "c2",
                    "name": "Dollar General",
                    "vicinity": "200 Perry St",
                    "rating": 4.1,
                    "user_ratings_total": 150,
                    "geometry": {"location": {"lat": 32.382, "lng": -86.312}},
                },
            ]
        }

        from app.services.google_places import GooglePlacesService

        svc = GooglePlacesService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.nearby_competitors(32.38, -86.31, business_type="grocery_or_supermarket")
        )

        assert result["count"] == 2
        assert result["business_type"] == "grocery_or_supermarket"
        assert result["average_rating"] == round((3.9 + 4.1) / 2, 2)
        assert len(result["competitors"]) == 2

    @patch("app.services.google_places.get_settings")
    @patch("app.services.google_places.googlemaps.Client")
    def test_compute_area_activity(self, mock_gm_client_cls, mock_settings):
        mock_settings.return_value.google_places_api_key = "test-key"
        mock_gm_instance = MagicMock()
        mock_gm_client_cls.return_value = mock_gm_instance

        def _fake_places_nearby(location, radius, type):
            fake_data = {
                "restaurant": [
                    {"name": "R1", "rating": 4.0},
                    {"name": "R2", "rating": 3.5},
                ],
                "store": [{"name": "S1", "rating": 4.5}],
                "cafe": [],
                "gym": [{"name": "G1", "rating": 4.0}],
                "bank": [],
                "school": [{"name": "Sch1", "rating": 4.2}],
            }
            return {"results": fake_data.get(type, [])}

        mock_gm_instance.places_nearby.side_effect = _fake_places_nearby

        from app.services.google_places import GooglePlacesService

        svc = GooglePlacesService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.compute_area_activity(32.38, -86.31)
        )

        assert result["total_places"] == 5
        assert result["average_rating"] is not None
        assert "category_breakdown" in result
        assert result["category_breakdown"]["restaurant"] == 2


# ── Census service tests ─────────────────────────────────────────────────────


class TestCensusService:
    """Test CensusService logic with mocked httpx calls."""

    def test_raises_without_api_key(self):
        from app.services.census_service import CensusService
        from app.config import Settings

        empty_settings = Settings(census_api_key="")
        with patch("app.services.census_service.get_settings", return_value=empty_settings):
            with pytest.raises(RuntimeError, match="Census API key is not configured"):
                CensusService()

    @patch("app.services.census_service.get_settings")
    def test_parse_row_produces_correct_structure(self, mock_settings):
        """Test the _parse_row helper directly."""
        from app.services.census_service import _parse_row

        header = [
            "NAME",
            "B01003_001E",
            "B19013_001E",
            "B25077_001E",
            "B25003_001E",
            "B25003_002E",
            "B25003_003E",
            "B25002_003E",
            "B02001_002E",
            "B02001_003E",
            "B17001_002E",
            "B23025_005E",
            "B23025_002E",
            "B08303_001E",
            "state",
            "county",
            "tract",
        ]
        row = [
            "Census Tract 1, Montgomery County, Alabama",
            "5000",   # total_population
            "45000",  # median_household_income
            "120000", # median_home_value
            "2000",   # total_housing_units
            "1200",   # owner_occupied
            "800",    # renter_occupied
            "100",    # vacant_housing_units
            "2000",   # white_alone
            "2500",   # black_african_american_alone
            "800",    # below_poverty_level
            "200",    # unemployed
            "3000",   # in_labor_force
            "2500",   # total_commuters
            "01",
            "101",
            "000100",
        ]

        result = _parse_row(header, row)

        assert result["total_population"] == 5000
        assert result["median_household_income"] == 45000
        assert result["median_home_value"] == 120000
        assert result["housing"]["total_units"] == 2000
        assert result["housing"]["owner_occupied"] == 1200
        assert result["housing"]["renter_occupied"] == 800
        assert result["housing"]["vacant"] == 100
        assert result["race"]["white_alone"] == 2000
        assert result["race"]["black_african_american_alone"] == 2500
        assert result["economics"]["below_poverty_level"] == 800
        assert result["economics"]["unemployment_rate_pct"] is not None

    def test_pct_helper(self):
        from app.services.census_service import _pct

        assert _pct(50, 200) == 25.0
        assert _pct(None, 200) is None
        assert _pct(50, 0) is None
        assert _pct(0, 100) == 0.0

    def test_safe_int_helper(self):
        from app.services.census_service import _safe_int

        assert _safe_int("100") == 100
        assert _safe_int("-1") is None  # negatives are N/A
        assert _safe_int(None) is None
        assert _safe_int("") is None
        assert _safe_int("abc") is None


# ── Walk Score service tests ──────────────────────────────────────────────────


class TestWalkScoreComputation:
    """Test walk score computation with mocked Google Places."""

    def _make_mock_places_service(self):
        mock = MagicMock()
        # Return varied counts for different categories
        async def _nearby_pois(lat, lng, radius_m, place_type):
            counts = {
                "grocery_or_supermarket": 2,
                "restaurant": 5,
                "school": 1,
                "park": 3,
                "pharmacy": 1,
                "cafe": 4,
                "bank": 2,
                "library": 0,
                "hospital": 1,
                "gym": 2,
                "bus_station": 1,
                "transit_station": 0,
            }
            count = counts.get(place_type, 0)
            return {"results": [{"name": f"{place_type}_{i}"} for i in range(count)], "total": count, "count": count}

        mock.nearby_pois = _nearby_pois
        return mock

    @patch("app.services.walkscore.get_google_places_service")
    def test_walk_score_returns_expected_keys(self, mock_get_places):
        mock_get_places.return_value = self._make_mock_places_service()

        from app.services.walkscore import compute_walk_score

        result = asyncio.get_event_loop().run_until_complete(
            compute_walk_score(32.38, -86.31)
        )

        assert "walk_score" in result
        assert "label" in result
        assert "total_amenities_nearby" in result
        assert "category_breakdown" in result
        assert 0 <= result["walk_score"] <= 100

    @patch("app.services.walkscore.get_google_places_service")
    def test_walk_score_label_categories(self, mock_get_places):
        mock_get_places.return_value = self._make_mock_places_service()

        from app.services.walkscore import compute_walk_score

        result = asyncio.get_event_loop().run_until_complete(
            compute_walk_score(32.38, -86.31)
        )

        valid_labels = [
            "Walker's Paradise",
            "Very Walkable",
            "Somewhat Walkable",
            "Car-Dependent",
            "Almost All Errands Require a Car",
        ]
        assert result["label"] in valid_labels

    @patch("app.services.walkscore.get_google_places_service")
    def test_walk_score_zero_amenities(self, mock_get_places):
        mock = MagicMock()

        async def _empty_pois(lat, lng, radius_m, place_type):
            return {"results": [], "total": 0, "count": 0}

        mock.nearby_pois = _empty_pois
        mock_get_places.return_value = mock

        from app.services.walkscore import compute_walk_score

        result = asyncio.get_event_loop().run_until_complete(
            compute_walk_score(32.38, -86.31)
        )

        assert result["walk_score"] == 0
        assert result["total_amenities_nearby"] == 0
        assert result["label"] == "Almost All Errands Require a Car"


# ── Walk Score API endpoint tests ─────────────────────────────────────────────


class TestWalkScoreAPI:
    """Tests for /api/walkscore/* endpoints with mocked Places service."""

    def _make_mock_places_service(self):
        mock = MagicMock()

        async def _nearby_pois(lat, lng, radius_m, place_type):
            return {"results": [{"name": "Place"}], "total": 1, "count": 1}

        mock.nearby_pois = _nearby_pois
        return mock

    def setup_method(self):
        self._pid = _seed()
        self._patcher = patch(
            "app.services.walkscore.get_google_places_service",
            return_value=self._make_mock_places_service(),
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()

    def test_walkscore_by_property_id(self):
        resp = client.get(f"/api/walkscore/{self._pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["property_id"] == self._pid
        assert "walk_score" in data
        assert "label" in data
        assert "address" in data

    def test_walkscore_not_found(self):
        resp = client.get("/api/walkscore/99999")
        assert resp.status_code == 404

    def test_walkscore_by_coordinates(self):
        resp = client.get("/api/walkscore/coordinates/?lat=32.38&lng=-86.31")
        assert resp.status_code == 200
        data = resp.json()
        assert "walk_score" in data
        assert data["latitude"] == 32.38
        assert data["longitude"] == -86.31


# ── Demographics API endpoint tests ──────────────────────────────────────────


class TestDemographicsAPI:
    """Tests for /api/demographics/* endpoints with mocked Census service."""

    def _make_mock_census(self):
        mock = MagicMock()
        mock.get_tract_demographics = AsyncMock(
            return_value={
                "geoid": "0110100100",
                "tract_name": "Census Tract 1, Montgomery County",
                "total_population": 5000,
                "median_household_income": 45000,
                "median_home_value": 120000,
                "housing": {
                    "total_units": 2000,
                    "owner_occupied": 1200,
                    "renter_occupied": 800,
                    "vacant": 100,
                    "owner_occupied_pct": 60.0,
                    "renter_occupied_pct": 40.0,
                    "vacancy_rate_pct": 5.0,
                },
                "race": {
                    "white_alone": 2000,
                    "black_african_american_alone": 2500,
                    "white_pct": 40.0,
                    "black_african_american_pct": 50.0,
                },
                "economics": {
                    "below_poverty_level": 800,
                    "poverty_rate_pct": 16.0,
                    "unemployed": 200,
                    "in_labor_force": 3000,
                    "unemployment_rate_pct": 6.67,
                },
                "commuters": {"total": 2500},
            }
        )
        mock.get_city_overview = AsyncMock(
            return_value={
                "place_name": "Montgomery city, Alabama",
                "total_population": 200000,
                "median_household_income": 42000,
                "median_home_value": 135000,
                "housing": {"total_units": 90000},
                "race": {"white_pct": 32.0, "black_african_american_pct": 60.0},
                "economics": {"poverty_rate_pct": 20.0, "unemployment_rate_pct": 7.0},
                "commuters": {"total": 85000},
            }
        )
        mock.get_neighborhood_demographics = AsyncMock(
            return_value={
                "0110100100": {
                    "geoid": "0110100100",
                    "total_population": 5000,
                    "median_household_income": 45000,
                },
                "0110100200": {
                    "geoid": "0110100200",
                    "total_population": 3000,
                    "median_household_income": 38000,
                },
            }
        )
        return mock

    def setup_method(self):
        _reset_db()
        self._patcher = patch(
            "app.routes.demographics.get_census_service",
            return_value=self._make_mock_census(),
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()

    def test_tract_demographics(self):
        resp = client.get("/api/demographics/tract?lat=32.38&lng=-86.31")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_population"] == 5000
        assert data["median_household_income"] == 45000
        assert "housing" in data
        assert "race" in data
        assert "economics" in data

    def test_city_demographics(self):
        resp = client.get("/api/demographics/city")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_population"] == 200000
        assert "place_name" in data

    def test_neighborhood_demographics(self):
        resp = client.get("/api/demographics/neighborhood?tracts=000100,000200")
        assert resp.status_code == 200
        data = resp.json()
        assert "0110100100" in data
        assert "0110100200" in data

    def test_neighborhood_demographics_no_tracts(self):
        resp = client.get("/api/demographics/neighborhood?tracts=")
        assert resp.status_code == 400


class TestDemographicsServiceUnavailable:
    """Test demographics endpoints when Census service is not configured."""

    def setup_method(self):
        _reset_db()
        self._patcher = patch(
            "app.routes.demographics.get_census_service",
            side_effect=RuntimeError("Census API key is not configured"),
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()

    def test_tract_returns_503(self):
        resp = client.get("/api/demographics/tract?lat=32.38&lng=-86.31")
        assert resp.status_code == 503

    def test_city_returns_503(self):
        resp = client.get("/api/demographics/city")
        assert resp.status_code == 503
