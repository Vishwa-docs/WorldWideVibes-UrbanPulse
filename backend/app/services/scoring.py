"""
Scoring engine for UrbanPulse properties.

The scoring system evaluates properties on 5 dimensions (each 0-10):
1. Foot Traffic Score - based on nearby POIs, web signals activity
2. Competition Score - inverse of competitor density (high = less competition = better)
3. Safety Score - based on incident density in the area
4. Equity Score - based on service gaps and underserved area indicators
5. Activity Index - composite of web signals

The Overall Opportunity Score is a weighted average that changes per scenario.
"""

import math
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from app.models.property import (
    Incident,
    Property,
    PropertyScore,
    ServiceLocation,
    WebSignal,
)

# ── Scenario weights ─────────────────────────────────────────────────────────

SCENARIO_WEIGHTS: dict[str, dict[str, float]] = {
    "general": {
        "foot_traffic": 0.25,
        "competition": 0.20,
        "safety": 0.20,
        "equity": 0.20,
        "activity": 0.15,
    },
    "grocery": {
        "foot_traffic": 0.20,
        "competition": 0.25,
        "safety": 0.15,
        "equity": 0.30,
        "activity": 0.10,
    },
    "clinic": {
        "foot_traffic": 0.15,
        "competition": 0.15,
        "safety": 0.20,
        "equity": 0.35,
        "activity": 0.15,
    },
    "daycare": {
        "foot_traffic": 0.20,
        "competition": 0.20,
        "safety": 0.30,
        "equity": 0.20,
        "activity": 0.10,
    },
    "coworking": {
        "foot_traffic": 0.30,
        "competition": 0.20,
        "safety": 0.15,
        "equity": 0.10,
        "activity": 0.25,
    },
}


# ── Haversine helper ─────────────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance in km between two lat/lon points."""
    R = 6371.0  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ── Nearby queries ────────────────────────────────────────────────────────────

def get_nearby_incidents(
    lat: float,
    lng: float,
    radius_km: float,
    session: Session,
) -> list[Incident]:
    """Return incidents within *radius_km* of the given coordinates."""
    incidents = session.exec(select(Incident)).all()
    return [
        i
        for i in incidents
        if haversine_km(lat, lng, i.latitude, i.longitude) <= radius_km
    ]


def get_nearby_services(
    lat: float,
    lng: float,
    radius_km: float,
    session: Session,
) -> list[ServiceLocation]:
    """Return service locations within *radius_km* of the given coordinates."""
    services = session.exec(select(ServiceLocation)).all()
    return [
        s
        for s in services
        if haversine_km(lat, lng, s.latitude, s.longitude) <= radius_km
    ]


# ── Individual score functions ────────────────────────────────────────────────

def compute_foot_traffic_score(
    prop: Property,
    web_signals: list[WebSignal],
    nearby_services: list[ServiceLocation],
) -> float:
    """
    Foot-traffic score (0-10).

    Higher when there are more nearby POIs and web signals indicate activity.
    """
    # Base from nearby services (more nearby services → more foot traffic)
    service_score = min(len(nearby_services) / 5.0, 1.0) * 5.0

    # Bonus from web signals
    if web_signals:
        total_pois = sum(ws.poi_count for ws in web_signals)
        total_reviews = sum(ws.review_count for ws in web_signals)
        poi_score = min(total_pois / 20.0, 1.0) * 3.0
        review_score = min(total_reviews / 100.0, 1.0) * 2.0
    else:
        # No web signals – give a modest baseline from services only
        poi_score = min(len(nearby_services) / 8.0, 1.0) * 3.0
        review_score = 0.0

    return min(round(service_score + poi_score + review_score, 2), 10.0)


def compute_competition_score(
    prop: Property,
    web_signals: list[WebSignal],
    scenario: str,
) -> float:
    """
    Competition score (0-10).

    High score means *less* competition (better opportunity).
    """
    if web_signals:
        total_competitors = sum(ws.competitor_count for ws in web_signals)
    else:
        # Assume moderate competition when data is missing
        total_competitors = 3

    # Inverse: fewer competitors → higher score
    if total_competitors == 0:
        return 10.0
    score = max(10.0 - total_competitors * 1.5, 0.0)
    return round(score, 2)


def compute_safety_score(
    prop: Property,
    nearby_incidents: list[Incident],
) -> float:
    """
    Safety score (0-10).

    Fewer/less-severe incidents → higher score.
    """
    if not nearby_incidents:
        return 10.0

    severity_weight = {"low": 0.5, "medium": 1.0, "high": 2.0}
    weighted_count = sum(
        severity_weight.get(i.severity or "medium", 1.0) for i in nearby_incidents
    )
    score = max(10.0 - weighted_count * 0.8, 0.0)
    return round(score, 2)


def compute_equity_score(
    prop: Property,
    nearby_services: list[ServiceLocation],
    service_type: Optional[str] = None,
) -> float:
    """
    Equity score (0-10).

    Higher when the area is *underserved* (fewer existing services).
    """
    if service_type:
        relevant = [s for s in nearby_services if s.service_type == service_type]
    else:
        relevant = nearby_services

    count = len(relevant)
    if count == 0:
        return 10.0
    score = max(10.0 - count * 2.0, 0.0)
    return round(score, 2)


def compute_activity_index(web_signals: list[WebSignal]) -> float:
    """
    Activity index (0-10).

    Composite of web-signal volume: POI count, reviews, ratings.
    """
    if not web_signals:
        return 3.0  # default baseline when no data

    total_pois = sum(ws.poi_count for ws in web_signals)
    avg_rating = (
        sum(ws.avg_rating for ws in web_signals if ws.avg_rating) / len(web_signals)
        if any(ws.avg_rating for ws in web_signals)
        else 3.0
    )
    total_reviews = sum(ws.review_count for ws in web_signals)

    poi_part = min(total_pois / 15.0, 1.0) * 3.0
    rating_part = (avg_rating / 5.0) * 3.0
    review_part = min(total_reviews / 80.0, 1.0) * 4.0
    return min(round(poi_part + rating_part + review_part, 2), 10.0)


# ── Persona adjustments ──────────────────────────────────────────────────────

def _apply_persona_adjustments(
    weights: dict[str, float],
    persona: str,
) -> dict[str, float]:
    """Return a *copy* of weights adjusted for the given persona."""
    w = dict(weights)
    if persona == "city_console":
        w["equity"] *= 1.20
        w["safety"] *= 1.10
    elif persona == "entrepreneur":
        w["foot_traffic"] *= 1.20
        w["activity"] *= 1.15

    # Re-normalise so weights sum to 1
    total = sum(w.values())
    if total > 0:
        w = {k: v / total for k, v in w.items()}
    return w


# ── Overall score ─────────────────────────────────────────────────────────────

def compute_overall_score(
    property_id: int,
    scenario: str,
    persona: str,
    session: Session,
) -> PropertyScore:
    """Compute and persist scores for a single property."""
    prop = session.get(Property, property_id)
    if prop is None:
        raise ValueError(f"Property {property_id} not found")

    # Gather context
    web_signals = list(
        session.exec(select(WebSignal).where(WebSignal.property_id == property_id))
    )
    nearby_incidents = get_nearby_incidents(
        prop.latitude, prop.longitude, radius_km=1.5, session=session
    )
    nearby_services = get_nearby_services(
        prop.latitude, prop.longitude, radius_km=2.0, session=session
    )

    # Map scenario to service_type for equity
    scenario_service_map = {
        "grocery": "grocery",
        "clinic": "clinic",
        "daycare": "daycare",
        "coworking": None,
        "general": None,
    }
    service_type = scenario_service_map.get(scenario)

    # Compute sub-scores
    ft = compute_foot_traffic_score(prop, web_signals, nearby_services)
    comp = compute_competition_score(prop, web_signals, scenario)
    safety = compute_safety_score(prop, nearby_incidents)
    equity = compute_equity_score(prop, nearby_services, service_type)
    activity = compute_activity_index(web_signals)

    # Weighted overall
    base_weights = SCENARIO_WEIGHTS.get(scenario, SCENARIO_WEIGHTS["general"])
    weights = _apply_persona_adjustments(base_weights, persona)

    overall = (
        weights["foot_traffic"] * ft
        + weights["competition"] * comp
        + weights["safety"] * safety
        + weights["equity"] * equity
        + weights["activity"] * activity
    )
    overall = round(overall, 2)

    # Upsert
    existing = session.exec(
        select(PropertyScore).where(
            PropertyScore.property_id == property_id,
            PropertyScore.scenario == scenario,
        )
    ).first()

    if existing:
        existing.foot_traffic_score = ft
        existing.competition_score = comp
        existing.safety_score = safety
        existing.equity_score = equity
        existing.activity_index = activity
        existing.overall_score = overall
        existing.computed_at = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    ps = PropertyScore(
        property_id=property_id,
        scenario=scenario,
        foot_traffic_score=ft,
        competition_score=comp,
        safety_score=safety,
        equity_score=equity,
        activity_index=activity,
        overall_score=overall,
        computed_at=datetime.utcnow(),
    )
    session.add(ps)
    session.commit()
    session.refresh(ps)
    return ps


def score_all_properties(
    scenario: str,
    persona: str,
    session: Session,
) -> list[PropertyScore]:
    """Compute and persist scores for every property in the database."""
    props = session.exec(select(Property)).all()
    results: list[PropertyScore] = []
    for prop in props:
        ps = compute_overall_score(prop.id, scenario, persona, session)  # type: ignore[arg-type]
        results.append(ps)
    return results
