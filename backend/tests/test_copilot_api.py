"""Tests for workforce-first copilot API additions."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models.property import Property, PropertyScore
from tests.conftest import TEST_ENGINE, reset_test_db

client = TestClient(app)


def _seed():
    reset_test_db()
    with Session(TEST_ENGINE) as session:
        p1 = Property(
            parcel_id="COP-001",
            address="101 Commerce St",
            latitude=32.3801,
            longitude=-86.305,
            property_type="commercial",
            is_vacant=True,
            is_city_owned=False,
            neighborhood="Downtown",
        )
        p2 = Property(
            parcel_id="COP-002",
            address="22 Madison Ave",
            latitude=32.374,
            longitude=-86.311,
            property_type="commercial",
            is_vacant=False,
            is_city_owned=True,
            neighborhood="Capitol Heights",
        )
        session.add_all([p1, p2])
        session.commit()
        session.refresh(p1)
        session.refresh(p2)
        session.add_all([
            PropertyScore(
                property_id=p1.id,
                scenario="general",
                overall_score=8.4,
                foot_traffic_score=8.8,
                competition_score=7.4,
                safety_score=7.9,
                equity_score=8.2,
                activity_index=7.3,
            ),
            PropertyScore(
                property_id=p2.id,
                scenario="general",
                overall_score=7.3,
                foot_traffic_score=6.8,
                competition_score=8.3,
                safety_score=6.9,
                equity_score=7.8,
                activity_index=6.1,
            ),
        ])
        session.commit()


def test_opportunities_overview():
    _seed()
    resp = client.get("/api/opportunities/overview", params={"role": "resident", "scenario": "general"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "resident"
    assert data["total_properties"] == 2
    assert len(data["top_recommendations"]) > 0
    assert len(data["sources"]) > 0


def test_recommendation_query_and_evidence():
    _seed()
    query_resp = client.post(
        "/api/recommendations/query",
        json={
            "query": "Best workforce growth opportunities",
            "role": "resident",
            "scenario": "general",
            "limit": 2,
        },
    )
    assert query_resp.status_code == 200
    payload = query_resp.json()
    assert payload["recommendation_id"]
    assert len(payload["recommendations"]) == 2

    first_sources = payload["sources"]
    source_types = {s["source_type"] for s in first_sources}
    assert "montgomery_open_data" in source_types
    assert "bright_data" in source_types

    evidence_resp = client.get(f"/api/evidence/{payload['recommendation_id']}")
    assert evidence_resp.status_code == 200
    evidence = evidence_resp.json()
    assert evidence["recommendation_id"] == payload["recommendation_id"]
    assert len(evidence["evidence"]) >= 2


def test_signal_refresh_and_changes():
    _seed()
    refresh_1 = client.post("/api/signals/refresh", json={"limit": 10, "force_live": False})
    assert refresh_1.status_code == 200
    data_1 = refresh_1.json()
    assert data_1["refreshed_count"] == 2

    refresh_2 = client.post("/api/signals/refresh", json={"limit": 10, "force_live": False})
    assert refresh_2.status_code == 200

    changes_resp = client.get("/api/signals/changes", params={"window_hours": 48})
    assert changes_resp.status_code == 200
    changes_data = changes_resp.json()
    assert changes_data["window_hours"] == 48
    assert len(changes_data["sources"]) == 1
