"""Watchlist CRUD routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.property import Property, PropertyScore, Watchlist
from app.models.schemas import (
    PropertyResponse,
    ScoreDetail,
    WatchlistItemResponse,
    WatchlistRequest,
    WatchlistResponse,
)

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


def _watchlist_item(
    wl: Watchlist,
    session: Session,
) -> WatchlistItemResponse:
    prop = session.get(Property, wl.property_id)
    prop_resp = None
    if prop:
        score = session.exec(
            select(PropertyScore).where(
                PropertyScore.property_id == prop.id,
                PropertyScore.scenario == "general",
            )
        ).first()
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
    return WatchlistItemResponse(
        id=wl.id,  # type: ignore[arg-type]
        property_id=wl.property_id,
        persona=wl.persona,
        notes=wl.notes,
        created_at=wl.created_at,
        property=prop_resp,
    )


@router.get("", response_model=WatchlistResponse)
def get_watchlist(
    persona: Optional[str] = Query(None),
    session: Session = Depends(get_session),
) -> WatchlistResponse:
    """Get all watchlist items, optionally filtered by persona."""
    stmt = select(Watchlist)
    if persona:
        stmt = stmt.where(Watchlist.persona == persona)
    items = session.exec(stmt).all()
    return WatchlistResponse(
        items=[_watchlist_item(w, session) for w in items],
        total=len(items),
    )


@router.post("", response_model=WatchlistItemResponse, status_code=201)
def add_to_watchlist(
    body: WatchlistRequest,
    session: Session = Depends(get_session),
) -> WatchlistItemResponse:
    """Add a property to the watchlist."""
    prop = session.get(Property, body.property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    wl = Watchlist(
        property_id=body.property_id,
        persona=body.persona,
        notes=body.notes,
    )
    session.add(wl)
    session.commit()
    session.refresh(wl)
    return _watchlist_item(wl, session)


@router.delete("/{watchlist_id}", status_code=204)
def remove_from_watchlist(
    watchlist_id: int,
    session: Session = Depends(get_session),
) -> None:
    """Remove an item from the watchlist."""
    wl = session.get(Watchlist, watchlist_id)
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    session.delete(wl)
    session.commit()
