"""Opportunity overview endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.schemas import OpportunitiesOverviewResponse
from app.services.opportunity_engine import get_overview

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.get("/overview", response_model=OpportunitiesOverviewResponse)
async def opportunities_overview(
    role: str = Query("resident"),
    scenario: str = Query("general"),
    session: Session = Depends(get_session),
) -> OpportunitiesOverviewResponse:
    """Return role/scenario overview for the workforce-first dashboard."""
    payload = await get_overview(session=session, role=role, scenario=scenario)
    return OpportunitiesOverviewResponse(**payload)
