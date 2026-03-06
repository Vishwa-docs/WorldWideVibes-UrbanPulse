"""Bright Data signal endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.property import Property, WebSignal
from app.services.brightdata_client import get_brightdata_client
from datetime import datetime

router = APIRouter(prefix="/api/brightdata", tags=["brightdata"])


@router.get("/signals/{property_id}")
async def get_signals(property_id: int, session: Session = Depends(get_session)):
    """Get or fetch web signals for a property."""
    property = session.get(Property, property_id)
    if not property:
        raise HTTPException(404, "Property not found")

    # Check if we have cached signals
    stmt = select(WebSignal).where(WebSignal.property_id == property_id)
    existing = session.exec(stmt).first()

    if existing:
        return {
            "property_id": property_id,
            "poi_count": existing.poi_count,
            "avg_rating": existing.avg_rating,
            "review_count": existing.review_count,
            "competitor_count": existing.competitor_count,
            "activity_index": existing.poi_count * 0.2,  # simplified
            "source": existing.source,
            "cached": True,
        }

    # Fetch fresh signals
    client = get_brightdata_client()
    signals = await client.fetch_activity_signals(property.latitude, property.longitude)

    # Cache in DB
    web_signal = WebSignal(
        property_id=property_id,
        poi_count=signals["poi_count"],
        avg_rating=signals["avg_rating"],
        review_count=signals["review_count"],
        competitor_count=signals["competitor_count"],
        source=signals["source"],
        fetched_at=datetime.utcnow(),
    )
    session.add(web_signal)
    session.commit()

    return {
        "property_id": property_id,
        **signals,
        "cached": False,
    }


@router.post("/refresh/{property_id}")
async def refresh_signals(property_id: int, session: Session = Depends(get_session)):
    """Force refresh web signals for a property."""
    property = session.get(Property, property_id)
    if not property:
        raise HTTPException(404, "Property not found")

    # Delete old signals
    stmt = select(WebSignal).where(WebSignal.property_id == property_id)
    old_signals = session.exec(stmt).all()
    for sig in old_signals:
        session.delete(sig)
    session.commit()

    # Fetch fresh
    client = get_brightdata_client()
    signals = await client.fetch_activity_signals(property.latitude, property.longitude)

    web_signal = WebSignal(
        property_id=property_id,
        poi_count=signals["poi_count"],
        avg_rating=signals["avg_rating"],
        review_count=signals["review_count"],
        competitor_count=signals["competitor_count"],
        source=signals["source"],
        fetched_at=datetime.utcnow(),
    )
    session.add(web_signal)
    session.commit()

    return {"property_id": property_id, **signals, "refreshed": True}


@router.post("/seed-all")
async def seed_all_signals(session: Session = Depends(get_session)):
    """Fetch and cache web signals for all properties."""
    props = session.exec(select(Property)).all()
    client = get_brightdata_client()
    results = []

    for prop in props:
        signals = await client.fetch_activity_signals(prop.latitude, prop.longitude)

        # Upsert
        stmt = select(WebSignal).where(WebSignal.property_id == prop.id)
        existing = session.exec(stmt).first()
        if existing:
            existing.poi_count = signals["poi_count"]
            existing.avg_rating = signals["avg_rating"]
            existing.review_count = signals["review_count"]
            existing.competitor_count = signals["competitor_count"]
            existing.source = signals["source"]
            existing.fetched_at = datetime.utcnow()
        else:
            web_signal = WebSignal(
                property_id=prop.id,
                poi_count=signals["poi_count"],
                avg_rating=signals["avg_rating"],
                review_count=signals["review_count"],
                competitor_count=signals["competitor_count"],
                source=signals["source"],
                fetched_at=datetime.utcnow(),
            )
            session.add(web_signal)

        results.append(
            {"property_id": prop.id, "activity_index": signals["activity_index"]}
        )

    session.commit()
    return {"seeded": len(results), "results": results}


@router.get("/status")
async def brightdata_status():
    """Check Bright Data configuration status."""
    client = get_brightdata_client()
    return {
        "configured": client.is_configured,
        "base_url": client.base_url,
        "mode": "live" if client.is_configured else "simulated",
    }
