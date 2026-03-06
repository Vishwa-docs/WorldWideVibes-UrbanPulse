"""
Tests for the scoring engine.
"""

import math

from sqlmodel import Session, SQLModel, create_engine

from app.models.property import (
    Incident,
    Property,
    PropertyScore,
    ServiceLocation,
    WebSignal,
)
from app.services.scoring import (
    SCENARIO_WEIGHTS,
    _apply_persona_adjustments,
    compute_activity_index,
    compute_competition_score,
    compute_equity_score,
    compute_foot_traffic_score,
    compute_overall_score,
    compute_safety_score,
    get_nearby_incidents,
    get_nearby_services,
    haversine_km,
    score_all_properties,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


def _seed(session: Session) -> Property:
    """Insert a minimal property + surrounding data and return the property."""
    prop = Property(
        parcel_id="TEST-001",
        address="100 Test St",
        latitude=32.38,
        longitude=-86.30,
        property_type="commercial",
        is_vacant=True,
        neighborhood="Downtown",
    )
    session.add(prop)
    session.commit()
    session.refresh(prop)

    # Web signals
    ws = WebSignal(
        property_id=prop.id,  # type: ignore[arg-type]
        poi_count=10,
        avg_rating=4.2,
        review_count=50,
        competitor_count=2,
        category="restaurant",
    )
    session.add(ws)

    # Incidents nearby (within 1.5 km)
    for sev in ("low", "medium", "high"):
        session.add(
            Incident(
                incident_type="theft",
                latitude=32.381,
                longitude=-86.301,
                severity=sev,
            )
        )

    # Incidents far away (should be excluded by radius)
    session.add(
        Incident(
            incident_type="theft",
            latitude=33.0,
            longitude=-87.0,
            severity="high",
        )
    )

    # Services nearby
    session.add(
        ServiceLocation(
            name="Test Grocery",
            service_type="grocery",
            latitude=32.379,
            longitude=-86.299,
        )
    )
    session.add(
        ServiceLocation(
            name="Test Clinic",
            service_type="clinic",
            latitude=32.382,
            longitude=-86.302,
        )
    )

    # Service far away
    session.add(
        ServiceLocation(
            name="Far Grocery",
            service_type="grocery",
            latitude=33.0,
            longitude=-87.0,
        )
    )

    session.commit()
    return prop


# ── Haversine ─────────────────────────────────────────────────────────────────


def test_haversine_zero_distance():
    assert haversine_km(0, 0, 0, 0) == 0.0


def test_haversine_known_distance():
    # New York to Los Angeles ≈ 3,944 km
    d = haversine_km(40.7128, -74.0060, 34.0522, -118.2437)
    assert 3930 < d < 3960


def test_haversine_short_distance():
    # Two points about 0.11 km apart in Montgomery
    d = haversine_km(32.38, -86.30, 32.381, -86.301)
    assert d < 0.5


# ── Nearby queries ────────────────────────────────────────────────────────────


def test_get_nearby_incidents():
    engine = _make_engine()
    with Session(engine) as session:
        prop = _seed(session)
        incidents = get_nearby_incidents(prop.latitude, prop.longitude, 1.5, session)
        # Should find the 3 nearby ones, not the far one
        assert len(incidents) == 3


def test_get_nearby_services():
    engine = _make_engine()
    with Session(engine) as session:
        prop = _seed(session)
        services = get_nearby_services(prop.latitude, prop.longitude, 2.0, session)
        assert len(services) == 2  # not the far one


# ── Foot-traffic score ────────────────────────────────────────────────────────


def test_foot_traffic_with_signals():
    engine = _make_engine()
    with Session(engine) as session:
        prop = _seed(session)
        ws = list(session.exec(
            __import__("sqlmodel").select(WebSignal).where(
                WebSignal.property_id == prop.id
            )
        ))
        services = get_nearby_services(prop.latitude, prop.longitude, 2.0, session)
        score = compute_foot_traffic_score(prop, ws, services)
        assert 0 <= score <= 10


def test_foot_traffic_no_signals():
    prop = Property(
        parcel_id="X", address="X", latitude=0, longitude=0, property_type="commercial"
    )
    services = [
        ServiceLocation(name="A", service_type="grocery", latitude=0, longitude=0)
    ]
    score = compute_foot_traffic_score(prop, [], services)
    assert 0 <= score <= 10


# ── Competition score ─────────────────────────────────────────────────────────


def test_competition_no_competitors():
    prop = Property(
        parcel_id="X", address="X", latitude=0, longitude=0, property_type="commercial"
    )
    ws = [
        WebSignal(property_id=1, poi_count=5, competitor_count=0, review_count=10)
    ]
    score = compute_competition_score(prop, ws, "general")
    assert score == 10.0


def test_competition_many_competitors():
    prop = Property(
        parcel_id="X", address="X", latitude=0, longitude=0, property_type="commercial"
    )
    ws = [
        WebSignal(property_id=1, poi_count=5, competitor_count=10, review_count=10)
    ]
    score = compute_competition_score(prop, ws, "general")
    assert score == 0.0  # 10 - 10*1.5 clamped to 0


# ── Safety score ──────────────────────────────────────────────────────────────


def test_safety_no_incidents():
    prop = Property(
        parcel_id="X", address="X", latitude=0, longitude=0, property_type="commercial"
    )
    score = compute_safety_score(prop, [])
    assert score == 10.0


def test_safety_with_incidents():
    prop = Property(
        parcel_id="X", address="X", latitude=0, longitude=0, property_type="commercial"
    )
    incidents = [
        Incident(incident_type="theft", latitude=0, longitude=0, severity="high"),
        Incident(incident_type="theft", latitude=0, longitude=0, severity="low"),
    ]
    score = compute_safety_score(prop, incidents)
    # weighted = 2.0 + 0.5 = 2.5  => 10 - 2.5*0.8 = 10 - 2.0 = 8.0
    assert score == 8.0


# ── Equity score ──────────────────────────────────────────────────────────────


def test_equity_no_services():
    prop = Property(
        parcel_id="X", address="X", latitude=0, longitude=0, property_type="commercial"
    )
    score = compute_equity_score(prop, [], service_type="grocery")
    assert score == 10.0


def test_equity_many_services():
    prop = Property(
        parcel_id="X", address="X", latitude=0, longitude=0, property_type="commercial"
    )
    services = [
        ServiceLocation(name=f"S{i}", service_type="grocery", latitude=0, longitude=0)
        for i in range(6)
    ]
    score = compute_equity_score(prop, services, service_type="grocery")
    assert score == 0.0  # 10 - 6*2 clamped to 0


# ── Activity index ────────────────────────────────────────────────────────────


def test_activity_no_signals():
    score = compute_activity_index([])
    assert score == 3.0  # baseline


def test_activity_with_signals():
    ws = [
        WebSignal(
            property_id=1,
            poi_count=15,
            avg_rating=5.0,
            review_count=80,
            competitor_count=0,
        )
    ]
    score = compute_activity_index(ws)
    # poi_part = min(15/15,1)*3 = 3, rating = (5/5)*3 = 3, review = min(80/80,1)*4 = 4 => 10
    assert score == 10.0


# ── Scenario weights ─────────────────────────────────────────────────────────


def test_scenario_weights_sum_to_one():
    for scenario, weights in SCENARIO_WEIGHTS.items():
        total = sum(weights.values())
        assert abs(total - 1.0) < 1e-9, f"{scenario} weights sum to {total}"


def test_grocery_boosts_equity():
    general = SCENARIO_WEIGHTS["general"]
    grocery = SCENARIO_WEIGHTS["grocery"]
    assert grocery["equity"] > general["equity"]


# ── Persona adjustments ──────────────────────────────────────────────────────


def test_city_console_boosts():
    base = dict(SCENARIO_WEIGHTS["general"])
    adjusted = _apply_persona_adjustments(base, "city_console")
    # Check relative boost: equity should be proportionally larger
    orig_ratio = base["equity"] / base["foot_traffic"]
    new_ratio = adjusted["equity"] / adjusted["foot_traffic"]
    assert new_ratio > orig_ratio


def test_entrepreneur_boosts():
    base = dict(SCENARIO_WEIGHTS["general"])
    adjusted = _apply_persona_adjustments(base, "entrepreneur")
    orig_ratio = base["foot_traffic"] / base["equity"]
    new_ratio = adjusted["foot_traffic"] / adjusted["equity"]
    assert new_ratio > orig_ratio


def test_persona_weights_sum_to_one():
    for persona in ("city_console", "entrepreneur"):
        w = _apply_persona_adjustments(dict(SCENARIO_WEIGHTS["general"]), persona)
        total = sum(w.values())
        assert abs(total - 1.0) < 1e-9


# ── Overall score computation ────────────────────────────────────────────────


def test_compute_overall_score():
    engine = _make_engine()
    with Session(engine) as session:
        prop = _seed(session)
        ps = compute_overall_score(prop.id, "general", "city_console", session)  # type: ignore[arg-type]
        assert isinstance(ps, PropertyScore)
        assert 0 <= ps.overall_score <= 10
        assert ps.property_id == prop.id
        assert ps.scenario == "general"


def test_compute_overall_score_upserts():
    engine = _make_engine()
    with Session(engine) as session:
        prop = _seed(session)
        ps1 = compute_overall_score(prop.id, "general", "city_console", session)  # type: ignore[arg-type]
        ps2 = compute_overall_score(prop.id, "general", "city_console", session)  # type: ignore[arg-type]
        assert ps1.id == ps2.id  # same row updated


def test_score_all_properties():
    engine = _make_engine()
    with Session(engine) as session:
        _seed(session)
        # Add a second property
        p2 = Property(
            parcel_id="TEST-002",
            address="200 Test Ave",
            latitude=32.39,
            longitude=-86.31,
            property_type="residential",
        )
        session.add(p2)
        session.commit()

        results = score_all_properties("general", "city_console", session)
        assert len(results) == 2


def test_compute_overall_score_invalid_property():
    engine = _make_engine()
    with Session(engine) as session:
        _seed(session)
        try:
            compute_overall_score(9999, "general", "city_console", session)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
