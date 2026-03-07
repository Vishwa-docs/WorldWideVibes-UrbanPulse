"""Recommendation query endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.models.schemas import (
    EvidenceResponse,
    RecommendationQueryRequest,
    RecommendationQueryResponse,
)
from app.services.opportunity_engine import get_evidence, query_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])
evidence_router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.post("/query", response_model=RecommendationQueryResponse)
async def recommendation_query(
    body: RecommendationQueryRequest,
    session: Session = Depends(get_session),
) -> RecommendationQueryResponse:
    """Run a structured recommendation query and return ranked opportunities."""
    payload = await query_recommendations(
        session=session,
        query=body.query,
        role=body.role,
        scenario=body.scenario,
        limit=body.limit,
        refresh_live=body.refresh_live,
        property_ids=body.property_ids,
    )
    return RecommendationQueryResponse(**payload)


@evidence_router.get("/{recommendation_id}", response_model=EvidenceResponse)
async def recommendation_evidence(recommendation_id: str) -> EvidenceResponse:
    """Retrieve stored evidence cards for a recommendation response."""
    evidence = get_evidence(recommendation_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return EvidenceResponse(
        recommendation_id=recommendation_id,
        evidence=evidence,
        generated_at=datetime.now(timezone.utc),
    )
