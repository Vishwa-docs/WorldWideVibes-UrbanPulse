"""Property comparison route."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.property import Property, PropertyScore
from app.models.schemas import (
    ComparePropertyItem,
    CompareRequest,
    CompareResponse,
    PropertyResponse,
    ScoreDetail,
)
from app.services.scoring import compute_overall_score

router = APIRouter(prefix="/api/compare", tags=["compare"])


@router.post("", response_model=CompareResponse)
def compare_properties(
    body: CompareRequest,
    session: Session = Depends(get_session),
) -> CompareResponse:
    """Compare up to 3 properties side-by-side."""
    if len(body.property_ids) > 3:
        raise HTTPException(status_code=400, detail="Compare at most 3 properties")

    items: list[ComparePropertyItem] = []
    for pid in body.property_ids:
        prop = session.get(Property, pid)
        if not prop:
            raise HTTPException(status_code=404, detail=f"Property {pid} not found")

        score_obj = session.exec(
            select(PropertyScore).where(
                PropertyScore.property_id == pid,
                PropertyScore.scenario == body.scenario,
            )
        ).first()
        if not score_obj:
            score_obj = compute_overall_score(pid, body.scenario, body.persona, session)

        score_detail = ScoreDetail(
            foot_traffic_score=score_obj.foot_traffic_score,
            competition_score=score_obj.competition_score,
            safety_score=score_obj.safety_score,
            equity_score=score_obj.equity_score,
            activity_index=score_obj.activity_index,
            overall_score=score_obj.overall_score,
            scenario=score_obj.scenario,
            computed_at=score_obj.computed_at,
        )
        prop_resp = PropertyResponse(
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
        items.append(ComparePropertyItem(property=prop_resp, scores=score_detail))

    return CompareResponse(
        items=items,
        scenario=body.scenario,
        persona=body.persona,
    )
