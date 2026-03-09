"""Bright Data signal endpoints — Web Scraper, SERP API, and Web Unlocker."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
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
    """Check Bright Data configuration status and capabilities."""
    client = get_brightdata_client()
    return {
        "configured": client.is_configured,
        "base_url": client.base_url,
        "serp_zone": client.serp_zone,
        "unlocker_zone": client.unlocker_zone,
        "mode": "live" if client.is_configured else "simulated",
        "api_token_set": bool(client.api_token),
        "api_token_prefix": client.api_token[:8] + "..." if client.api_token else None,
    }


# ── SERP API ────────────────────────────────────────────────────────────


class SerpRequest(BaseModel):
    query: str
    engine: str = "google"
    location: str = "Montgomery,Alabama,United States"
    num_results: int = 10


@router.post("/serp")
async def search_serp(req: SerpRequest):
    """
    Search via Bright Data SERP API for local business intelligence.

    Returns structured search engine results for Montgomery-related queries.
    Useful for competitive analysis, market research, and local trend discovery.
    """
    client = get_brightdata_client()
    return await client.search_serp(
        query=req.query,
        engine=req.engine,
        location=req.location,
        num_results=req.num_results,
    )


@router.get("/serp/local")
async def search_local(
    q: str = Query(..., description="Search query (e.g., 'grocery stores')"),
    category: str = Query("business", description="Business category"),
):
    """
    Quick local SERP search for Montgomery, AL businesses.

    Shortcut that adds 'Montgomery AL' to the query automatically.
    """
    client = get_brightdata_client()
    full_query = f"{q} {category} Montgomery AL"
    return await client.search_serp(query=full_query, num_results=8)


# ── Web Unlocker ────────────────────────────────────────────────────────


class ScrapeRequest(BaseModel):
    url: str
    max_length: int = 8000


@router.post("/scrape")
async def scrape_url(req: ScrapeRequest):
    """
    Scrape a public webpage via Bright Data's Web Unlocker.

    Returns clean markdown content suitable for AI/LLM consumption.
    Handles anti-bot protection, CAPTCHAs, and dynamic rendering.
    """
    client = get_brightdata_client()
    result = await client.scrape_url(req.url)
    # Respect custom max_length
    if req.max_length and len(result.get("content", "")) > req.max_length:
        result["content"] = result["content"][:req.max_length] + "\n\n... (truncated)"
    return result


# ── Capabilities ────────────────────────────────────────────────────────


@router.get("/capabilities")
async def brightdata_capabilities():
    """
    List all Bright Data products integrated into UrbanPulse.

    Returns details on Web Scraper, SERP API, Web Unlocker, and MCP Server.
    """
    client = get_brightdata_client()
    return client.get_capabilities()
