"""Score computation and ranking routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.property import Property, PropertyScore
from app.models.schemas import (
    PropertyResponse,
    RankedListResponse,
    RankedPropertyItem,
    ScoreComputeRequest,
    ScoreComputeResponse,
    ScoreDetail,
)
from app.services.scoring import score_all_properties

router = APIRouter(prefix="/api/scores", tags=["scores"])


def _prop_to_resp(prop: Property, score: Optional[PropertyScore]) -> PropertyResponse:
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


@router.post("/compute", response_model=ScoreComputeResponse)
def compute_scores(
    body: ScoreComputeRequest,
    session: Session = Depends(get_session),
) -> ScoreComputeResponse:
    """Recompute scores for all properties."""
    results = score_all_properties(body.scenario, body.persona, session)
    return ScoreComputeResponse(
        computed_count=len(results),
        scenario=body.scenario,
        persona=body.persona,
    )


@router.get("/ranked", response_model=RankedListResponse)
def ranked_list(
    scenario: str = Query("general"),
    persona: str = Query("city_console"),
    limit: int = Query(20, ge=1, le=200),
    min_score: float = Query(0.0, ge=0.0),
    session: Session = Depends(get_session),
) -> RankedListResponse:
    """Return properties ranked by overall score."""
    stmt = (
        select(PropertyScore)
        .where(
            PropertyScore.scenario == scenario,
            PropertyScore.overall_score >= min_score,
        )
        .order_by(PropertyScore.overall_score.desc())  # type: ignore[union-attr]
        .limit(limit)
    )
    scores = session.exec(stmt).all()

    items: list[RankedPropertyItem] = []
    for rank, ps in enumerate(scores, start=1):
        prop = session.get(Property, ps.property_id)
        if not prop:
            continue
        items.append(
            RankedPropertyItem(
                rank=rank,
                property=_prop_to_resp(prop, ps),
                overall_score=ps.overall_score,
            )
        )

    return RankedListResponse(
        items=items,
        scenario=scenario,
        persona=persona,
        total=len(items),
    )
