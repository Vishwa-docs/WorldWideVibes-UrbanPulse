"""
Tests for API endpoints.

Uses an in-memory SQLite database so tests don't touch the real DB.
"""

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app.main import app
from app.models.property import (
    Incident,
    Property,
    PropertyScore,
    ServiceLocation,
    WebSignal,
)
from tests.conftest import TEST_ENGINE, reset_test_db, get_test_session

# ── Test DB setup ─────────────────────────────────────────────────────────────

client = TestClient(app)


# Track seeded IDs so tests use correct references
_seeded_ids: list[int] = []


def _reset_db():
    """Drop and recreate all tables for a clean slate."""
    reset_test_db()
    # Reset autoincrement counters
    with Session(TEST_ENGINE) as session:
        try:
            session.exec(text("DELETE FROM sqlite_sequence"))
            session.commit()
        except Exception:
            pass


def _seed():
    """Seed minimal data for tests."""
    global _seeded_ids
    _reset_db()
    with Session(TEST_ENGINE) as session:
        p1 = Property(
            parcel_id="API-001",
            address="10 Main St",
            latitude=32.38,
            longitude=-86.30,
            property_type="commercial",
            is_vacant=True,
            is_city_owned=False,
            neighborhood="Downtown",
        )
        p2 = Property(
            parcel_id="API-002",
            address="20 Oak Ave",
            latitude=32.39,
            longitude=-86.31,
            property_type="residential",
            is_vacant=False,
            is_city_owned=True,
            neighborhood="Midtown",
        )
        p3 = Property(
            parcel_id="API-003",
            address="30 Elm Rd",
            latitude=32.40,
            longitude=-86.32,
            property_type="commercial",
            is_vacant=True,
            is_city_owned=False,
            neighborhood="Downtown",
        )
        session.add_all([p1, p2, p3])
        session.commit()
        session.refresh(p1)
        session.refresh(p2)
        session.refresh(p3)
        _seeded_ids = [p1.id, p2.id, p3.id]

        # Add incidents
        session.add(
            Incident(
                incident_type="theft",
                latitude=32.381,
                longitude=-86.301,
                severity="low",
            )
        )
        # Add services
        session.add(
            ServiceLocation(
                name="Corner Store",
                service_type="grocery",
                latitude=32.379,
                longitude=-86.299,
            )
        )
        session.commit()


# ── Properties ────────────────────────────────────────────────────────────────


def test_list_properties():
    _seed()
    resp = client.get("/api/properties")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_list_properties_filter_vacant():
    _seed()
    resp = client.get("/api/properties", params={"is_vacant": True})
    assert resp.status_code == 200
    data = resp.json()
    assert all(p["is_vacant"] for p in data)
    assert len(data) == 2


def test_list_properties_filter_neighborhood():
    _seed()
    resp = client.get("/api/properties", params={"neighborhood": "Downtown"})
    assert resp.status_code == 200
    data = resp.json()
    assert all(p["neighborhood"] == "Downtown" for p in data)


def test_list_properties_pagination():
    _seed()
    resp = client.get("/api/properties", params={"skip": 0, "limit": 2})
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    resp2 = client.get("/api/properties", params={"skip": 2, "limit": 2})
    assert resp2.status_code == 200
    assert len(resp2.json()) == 1


def test_get_single_property():
    _seed()
    pid = _seeded_ids[0]
    resp = client.get(f"/api/properties/{pid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["parcel_id"] == "API-001"


def test_get_property_not_found():
    _seed()
    resp = client.get("/api/properties/9999")
    assert resp.status_code == 404


def test_get_scorecard():
    _seed()
    pid = _seeded_ids[0]
    resp = client.get(f"/api/properties/{pid}/scorecard")
    assert resp.status_code == 200
    data = resp.json()
    assert "scores" in data
    assert "nearby_incidents" in data
    assert "nearby_services" in data
    assert "ai_narrative" in data
    assert data["scores"]["overall_score"] >= 0


# ── Scores ────────────────────────────────────────────────────────────────────


def test_compute_scores():
    _seed()
    resp = client.post(
        "/api/scores/compute",
        json={"scenario": "general", "persona": "city_console"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["computed_count"] == 3
    assert data["scenario"] == "general"


def test_ranked_list():
    _seed()
    # First compute scores
    client.post(
        "/api/scores/compute",
        json={"scenario": "general", "persona": "city_console"},
    )
    resp = client.get("/api/scores/ranked", params={"scenario": "general"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    # Ensure descending order
    scores = [item["overall_score"] for item in data["items"]]
    assert scores == sorted(scores, reverse=True)


def test_ranked_list_with_min_score():
    _seed()
    client.post(
        "/api/scores/compute",
        json={"scenario": "general", "persona": "city_console"},
    )
    resp = client.get(
        "/api/scores/ranked", params={"scenario": "general", "min_score": 100}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0  # No property should score >= 100


# ── Compare ───────────────────────────────────────────────────────────────────


def test_compare_properties():
    _seed()
    resp = client.post(
        "/api/compare",
        json={
            "property_ids": _seeded_ids[:2],
            "scenario": "general",
            "persona": "city_console",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["scenario"] == "general"


def test_compare_not_found():
    _seed()
    resp = client.post(
        "/api/compare",
        json={
            "property_ids": [9999],
            "scenario": "general",
            "persona": "city_console",
        },
    )
    assert resp.status_code == 404


# ── Watchlist ─────────────────────────────────────────────────────────────────


def test_watchlist_crud():
    _seed()
    pid = _seeded_ids[0]

    # Add
    resp = client.post(
        "/api/watchlist",
        json={"property_id": pid, "persona": "city_console", "notes": "Looks promising"},
    )
    assert resp.status_code == 201
    wl_id = resp.json()["id"]

    # List
    resp = client.get("/api/watchlist")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1

    # Filter by persona
    resp = client.get("/api/watchlist", params={"persona": "city_console"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # Delete
    resp = client.delete(f"/api/watchlist/{wl_id}")
    assert resp.status_code == 204


def test_watchlist_add_missing_property():
    _seed()
    resp = client.post(
        "/api/watchlist",
        json={"property_id": 9999, "persona": "city_console"},
    )
    assert resp.status_code == 404


def test_watchlist_delete_not_found():
    _seed()
    resp = client.delete("/api/watchlist/9999")
    assert resp.status_code == 404


# ── Export ────────────────────────────────────────────────────────────────────


def test_export_csv():
    _seed()
    # Compute scores first
    client.post(
        "/api/scores/compute",
        json={"scenario": "general", "persona": "city_console"},
    )
    resp = client.get("/api/export/csv", params={"scenario": "general"})
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    lines = resp.text.strip().split("\n")
    assert len(lines) >= 2  # header + at least 1 data row
    assert "overall_score" in lines[0]
