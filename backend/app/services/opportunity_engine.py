"""Workforce-first recommendation and overview engine."""

from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Optional
from uuid import uuid4

from sqlmodel import Session, select

from app.models.property import Property, PropertyScore, WebSignal
from app.models.schemas import ScoreDetail
from app.services.scoring import compute_overall_score
from app.services.signals_service import latest_web_signal, refresh_signals

RoleType = str

VALID_ROLES = {"resident", "entrepreneur", "city", "education"}

ROLE_LABELS = {
    "resident": "Resident Career Path",
    "entrepreneur": "Entrepreneur Opportunity",
    "city": "City Operations",
    "education": "Education Partner",
}

_EVIDENCE_STORE: dict[str, list[dict]] = {}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def normalize_role(role: str) -> str:
    """Normalize user-provided role aliases."""
    key = (role or "").strip().lower()
    aliases = {
        "city_staff": "city",
        "city_console": "city",
        "staff": "city",
        "entrepreneur_studio": "entrepreneur",
    }
    normalized = aliases.get(key, key)
    return normalized if normalized in VALID_ROLES else "resident"


def _score_to_detail(score: PropertyScore) -> ScoreDetail:
    return ScoreDetail(
        foot_traffic_score=score.foot_traffic_score,
        competition_score=score.competition_score,
        safety_score=score.safety_score,
        equity_score=score.equity_score,
        activity_index=score.activity_index,
        overall_score=score.overall_score,
        scenario=score.scenario,
        computed_at=score.computed_at,
    )


def _property_to_response(prop: Property, score: Optional[PropertyScore]) -> dict:
    return {
        "id": prop.id,
        "parcel_id": prop.parcel_id,
        "address": prop.address,
        "latitude": prop.latitude,
        "longitude": prop.longitude,
        "property_type": prop.property_type,
        "zoning": prop.zoning,
        "is_vacant": prop.is_vacant,
        "is_city_owned": prop.is_city_owned,
        "lot_size_sqft": prop.lot_size_sqft,
        "building_sqft": prop.building_sqft,
        "assessed_value": prop.assessed_value,
        "year_built": prop.year_built,
        "neighborhood": prop.neighborhood,
        "council_district": prop.council_district,
        "score": _score_to_detail(score).model_dump() if score else None,
    }


def _clamp_score(v: float) -> float:
    return round(max(0.0, min(10.0, v)), 2)


def _compute_role_scores(
    prop: Property,
    score: PropertyScore,
) -> dict[str, float]:
    resident_fit = _clamp_score(
        score.safety_score * 0.35
        + score.equity_score * 0.35
        + score.foot_traffic_score * 0.2
        + score.activity_index * 0.1
    )
    business_opportunity = _clamp_score(
        score.foot_traffic_score * 0.35
        + score.activity_index * 0.25
        + score.competition_score * 0.25
        + (10.0 if prop.is_vacant else 6.0) * 0.15
    )
    city_impact = _clamp_score(
        score.equity_score * 0.35
        + score.safety_score * 0.2
        + (10.0 if prop.is_vacant else 4.5) * 0.25
        + (10.0 if prop.is_city_owned else 5.0) * 0.2
    )
    return {
        "resident_fit_score": resident_fit,
        "business_opportunity_score": business_opportunity,
        "city_impact_score": city_impact,
    }


def _overall_from_role(role: RoleType, role_scores: dict[str, float]) -> float:
    resident = role_scores["resident_fit_score"]
    business = role_scores["business_opportunity_score"]
    city = role_scores["city_impact_score"]

    if role == "resident":
        return _clamp_score(resident * 0.55 + business * 0.2 + city * 0.25)
    if role == "entrepreneur":
        return _clamp_score(business * 0.6 + resident * 0.2 + city * 0.2)
    if role == "city":
        return _clamp_score(city * 0.55 + resident * 0.25 + business * 0.2)
    if role == "education":
        return _clamp_score(resident * 0.45 + city * 0.35 + business * 0.2)
    return _clamp_score((resident + business + city) / 3.0)


def _top_factors(score: PropertyScore, prop: Property) -> list[str]:
    factors = [
        ("Foot Traffic", score.foot_traffic_score),
        ("Competition Gap", score.competition_score),
        ("Safety", score.safety_score),
        ("Equity Need", score.equity_score),
        ("Activity", score.activity_index),
    ]
    ranked = sorted(factors, key=lambda x: x[1], reverse=True)
    labels = [f"{name}: {value:.1f}/10" for name, value in ranked[:3]]
    if prop.is_vacant:
        labels.append("Vacant property can be activated quickly")
    if prop.is_city_owned:
        labels.append("City-owned parcel improves implementation feasibility")
    return labels[:4]


def _build_evidence_for_property(
    recommendation_id: str,
    prop: Property,
    score: PropertyScore,
    web_signal: Optional[WebSignal],
) -> tuple[list[str], list[dict]]:
    montgomery_evidence_id = f"{recommendation_id}-montgomery-{prop.id}"
    brightdata_evidence_id = f"{recommendation_id}-brightdata-{prop.id}"

    montgomery_evidence = {
        "id": montgomery_evidence_id,
        "label": "Montgomery Open Data property context",
        "source_type": "montgomery_open_data",
        "is_live": True,
        "observed_at": score.computed_at,
        "confidence": 0.9,
        "url": "https://opendata.montgomeryal.gov",
        "note": f"{prop.address} in {prop.neighborhood or 'Montgomery'}",
    }
    if web_signal:
        brightdata_evidence = {
            "id": brightdata_evidence_id,
            "label": "Bright Data activity signal",
            "source_type": "bright_data",
            "is_live": "simulated" not in (web_signal.source or "").lower(),
            "observed_at": web_signal.fetched_at,
            "confidence": 0.82 if "simulated" not in (web_signal.source or "").lower() else 0.64,
            "url": "https://docs.brightdata.com/scraping-automation/crawl-api/quick-start",
            "note": (
                f"POI {web_signal.poi_count}, reviews {web_signal.review_count}, "
                f"competitors {web_signal.competitor_count}"
            ),
        }
    else:
        brightdata_evidence = {
            "id": brightdata_evidence_id,
            "label": "Bright Data activity signal (pending refresh)",
            "source_type": "bright_data",
            "is_live": False,
            "observed_at": None,
            "confidence": 0.45,
            "url": "https://docs.brightdata.com/scraping-automation/crawl-api/quick-start",
            "note": "No cached signal yet. Trigger live refresh in the dashboard.",
        }
    return [montgomery_evidence_id, brightdata_evidence_id], [
        montgomery_evidence,
        brightdata_evidence,
    ]


def _fetch_scores_for_scenario(session: Session, scenario: str) -> list[tuple[Property, PropertyScore]]:
    props = session.exec(select(Property)).all()
    rows: list[tuple[Property, PropertyScore]] = []
    for prop in props:
        score = session.exec(
            select(PropertyScore).where(
                PropertyScore.property_id == prop.id,
                PropertyScore.scenario == scenario,
            )
        ).first()
        if not score:
            score = compute_overall_score(
                property_id=prop.id,  # type: ignore[arg-type]
                scenario=scenario,
                persona="city_console",
                session=session,
            )
        rows.append((prop, score))
    return rows


async def query_recommendations(
    session: Session,
    query: str,
    role: str,
    scenario: str,
    limit: int = 5,
    refresh_live: bool = False,
    property_ids: Optional[list[int]] = None,
) -> dict:
    """Return structured role-aware recommendations and evidence."""
    normalized_role = normalize_role(role)

    if refresh_live:
        await refresh_signals(
            session=session,
            property_ids=property_ids,
            limit=min(100, max(limit * 8, 20)),
            force_live=True,
        )

    rows = _fetch_scores_for_scenario(session, scenario)
    if property_ids:
        rows = [row for row in rows if row[0].id in property_ids]

    ranked: list[dict] = []
    for prop, score in rows:
        role_scores = _compute_role_scores(prop, score)
        overall = _overall_from_role(normalized_role, role_scores)
        ranked.append(
            {
                "property": prop,
                "score": score,
                "role_scores": role_scores,
                "overall": overall,
            }
        )
    ranked.sort(key=lambda r: r["overall"], reverse=True)

    recommendation_id = str(uuid4())
    evidence_payload: list[dict] = []
    items: list[dict] = []

    for idx, row in enumerate(ranked[:limit], start=1):
        prop = row["property"]
        score = row["score"]
        web_signal = latest_web_signal(session, prop.id)  # type: ignore[arg-type]
        evidence_ids, evidence = _build_evidence_for_property(
            recommendation_id=recommendation_id,
            prop=prop,
            score=score,
            web_signal=web_signal,
        )
        evidence_payload.extend(evidence)
        scores = {
            **row["role_scores"],
            "overall_score": row["overall"],
        }
        items.append(
            {
                "rank": idx,
                "property": _property_to_response(prop, score),
                "scores": scores,
                "top_factors": _top_factors(score, prop),
                "evidence_ids": evidence_ids,
            }
        )

    _EVIDENCE_STORE[recommendation_id] = evidence_payload
    source_confidences = [float(e["confidence"]) for e in evidence_payload] or [0.5]
    confidence = round(mean(source_confidences), 2)

    query_text = query.strip() or f"Top {ROLE_LABELS[normalized_role]} opportunities"
    summary = (
        f"{ROLE_LABELS[normalized_role]} view surfaced {len(items)} opportunities "
        f"for scenario '{scenario}'. Query context: {query_text}."
    )

    return {
        "recommendation_id": recommendation_id,
        "role": normalized_role,
        "scenario": scenario,
        "query": query_text,
        "summary": summary,
        "recommendations": items,
        "sources": evidence_payload,
        "generated_at": _utcnow(),
        "confidence": confidence,
    }


async def get_overview(
    session: Session,
    role: str,
    scenario: str,
) -> dict:
    """Return role-specific high-level opportunity overview."""
    normalized_role = normalize_role(role)
    recommendation_bundle = await query_recommendations(
        session=session,
        query="",
        role=normalized_role,
        scenario=scenario,
        limit=3,
        refresh_live=False,
    )

    all_scores = [r["scores"]["overall_score"] for r in recommendation_bundle["recommendations"]]
    all_properties = session.exec(select(Property)).all()
    total_properties = len(all_properties)
    city_owned = len([p for p in all_properties if p.is_city_owned])
    vacant = len([p for p in all_properties if p.is_vacant])

    kpis: dict[str, float | int | str] = {
        "avg_top_score": round(mean(all_scores), 2) if all_scores else 0.0,
        "vacant_properties": vacant,
        "city_owned_properties": city_owned,
        "active_role": ROLE_LABELS[normalized_role],
    }
    return {
        "role": normalized_role,
        "scenario": scenario,
        "total_properties": total_properties,
        "role_focus": ROLE_LABELS[normalized_role],
        "kpis": kpis,
        "top_recommendations": recommendation_bundle["recommendations"],
        "sources": recommendation_bundle["sources"],
        "generated_at": recommendation_bundle["generated_at"],
        "confidence": recommendation_bundle["confidence"],
    }


def get_evidence(recommendation_id: str) -> list[dict]:
    """Return stored evidence items for a recommendation id."""
    return _EVIDENCE_STORE.get(recommendation_id, [])
