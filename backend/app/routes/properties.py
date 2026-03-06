"""Property listing and detail routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.property import (
    Incident,
    Property,
    PropertyScore,
    ServiceLocation,
    WebSignal,
)
from app.models.schemas import (
    IncidentNearby,
    PropertyResponse,
    ScoreDetail,
    ScorecardResponse,
    ServiceNearby,
)
from app.services.scoring import (
    compute_overall_score,
    get_nearby_incidents,
    get_nearby_services,
    haversine_km,
)

router = APIRouter(prefix="/api/properties", tags=["properties"])


def _property_to_response(
    prop: Property,
    score: Optional[PropertyScore] = None,
) -> PropertyResponse:
    """Map a Property + optional score to an API response."""
    score_detail = None
    if score:
        score_detail = ScoreDetail(
            foot_traffic_score=score.foot_traffic_score,
            competition_score=score.competition_score,
            safety_score=score.safety_score,
            equity_score=score.equity_score,
            activity_index=score.activity_index,
            overall_score=score.overall_score,
            scenario=score.scenario,
            computed_at=score.computed_at,
        )
    return PropertyResponse(
        id=prop.id,  # type: ignore[arg-type]
        parcel_id=prop.parcel_id,
        address=prop.address,
        latitude=prop.latitude,
        longitude=prop.longitude,
        property_type=prop.property_type,
        zoning=prop.zoning,
        is_vacant=prop.is_vacant,
        is_city_owned=prop.is_city_owned,
        lot_size_sqft=prop.lot_size_sqft,
        building_sqft=prop.building_sqft,
        assessed_value=prop.assessed_value,
        year_built=prop.year_built,
        neighborhood=prop.neighborhood,
        council_district=prop.council_district,
        score=score_detail,
    )


@router.get("", response_model=list[PropertyResponse])
def list_properties(
    is_vacant: Optional[bool] = None,
    is_city_owned: Optional[bool] = None,
    neighborhood: Optional[str] = None,
    property_type: Optional[str] = None,
    scenario: str = Query("general"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> list[PropertyResponse]:
    """List properties with optional filters and pagination."""
    stmt = select(Property)
    if is_vacant is not None:
        stmt = stmt.where(Property.is_vacant == is_vacant)
    if is_city_owned is not None:
        stmt = stmt.where(Property.is_city_owned == is_city_owned)
    if neighborhood:
        stmt = stmt.where(Property.neighborhood == neighborhood)
    if property_type:
        stmt = stmt.where(Property.property_type == property_type)

    stmt = stmt.offset(skip).limit(limit)
    props = session.exec(stmt).all()

    results: list[PropertyResponse] = []
    for p in props:
        score = session.exec(
            select(PropertyScore).where(
                PropertyScore.property_id == p.id,
                PropertyScore.scenario == scenario,
            )
        ).first()
        results.append(_property_to_response(p, score))
    return results


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    scenario: str = Query("general"),
    session: Session = Depends(get_session),
) -> PropertyResponse:
    """Get a single property with its latest score."""
    prop = session.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    score = session.exec(
        select(PropertyScore).where(
            PropertyScore.property_id == property_id,
            PropertyScore.scenario == scenario,
        )
    ).first()
    return _property_to_response(prop, score)


@router.get("/{property_id}/scorecard", response_model=ScorecardResponse)
def get_scorecard(
    property_id: int,
    scenario: str = Query("general"),
    persona: str = Query("city_console"),
    session: Session = Depends(get_session),
) -> ScorecardResponse:
    """Return a detailed scorecard for a property."""
    prop = session.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # Ensure scores exist
    score_obj = session.exec(
        select(PropertyScore).where(
            PropertyScore.property_id == property_id,
            PropertyScore.scenario == scenario,
        )
    ).first()
    if not score_obj:
        score_obj = compute_overall_score(property_id, scenario, persona, session)

    prop_resp = _property_to_response(prop, score_obj)
    score_detail = prop_resp.score or ScoreDetail()

    # Nearby data
    incidents = get_nearby_incidents(prop.latitude, prop.longitude, 1.5, session)
    services = get_nearby_services(prop.latitude, prop.longitude, 2.0, session)

    incident_items = [
        IncidentNearby(
            id=i.id,  # type: ignore[arg-type]
            incident_type=i.incident_type,
            latitude=i.latitude,
            longitude=i.longitude,
            severity=i.severity,
            distance_km=round(
                haversine_km(prop.latitude, prop.longitude, i.latitude, i.longitude), 3
            ),
        )
        for i in incidents
    ]

    service_items = [
        ServiceNearby(
            id=s.id,  # type: ignore[arg-type]
            name=s.name,
            service_type=s.service_type,
            latitude=s.latitude,
            longitude=s.longitude,
            distance_km=round(
                haversine_km(prop.latitude, prop.longitude, s.latitude, s.longitude), 3
            ),
        )
        for s in services
    ]

    return ScorecardResponse(
        property=prop_resp,
        scores=score_detail,
        nearby_incidents=incident_items,
        nearby_services=service_items,
    )
