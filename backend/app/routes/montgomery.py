"""
Montgomery open data & workforce routes.

Exposes Montgomery ArcGIS data and workforce statistics via REST API.
All data sources are free and require no authentication.
"""

from fastapi import APIRouter, Query
from typing import Optional
from app.services.arcgis_service import (
    fetch_311_requests,
    fetch_most_visited_locations,
    fetch_visitor_origin,
    fetch_business_licenses,
    fetch_vacant_properties,
    get_data_summary,
)
from app.services.workforce_service import fetch_workforce_summary

router = APIRouter(prefix="/api/montgomery", tags=["montgomery"])


# ── 311 Service Requests ─────────────────────────────────────────────────────


@router.get("/311")
async def get_311_requests(
    limit: int = Query(200, ge=1, le=1000),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """Fetch 311 service requests from Montgomery open data."""
    data = await fetch_311_requests(limit=limit, category=category)
    return {"items": data, "total": len(data), "source": "montgomery_arcgis"}


# ── Most Visited Locations (Foot Traffic) ────────────────────────────────────


@router.get("/most-visited")
async def get_most_visited(
    limit: int = Query(200, ge=1, le=1000),
):
    """Fetch most visited locations in Montgomery (foot traffic data)."""
    data = await fetch_most_visited_locations(limit=limit)
    return {"items": data, "total": len(data), "source": "montgomery_arcgis"}


# ── Visitor Origin ───────────────────────────────────────────────────────────


@router.get("/visitor-origin")
async def get_visitor_origin(
    limit: int = Query(200, ge=1, le=1000),
):
    """Fetch visitor origin / foot traffic patterns."""
    data = await fetch_visitor_origin(limit=limit)
    return {"items": data, "total": len(data), "source": "montgomery_arcgis"}


# ── Business Licenses ────────────────────────────────────────────────────────


@router.get("/business-licenses")
async def get_business_licenses(
    limit: int = Query(200, ge=1, le=1000),
    business_type: Optional[str] = Query(None, description="Filter by business type"),
):
    """Fetch business license data from Montgomery."""
    data = await fetch_business_licenses(limit=limit, business_type=business_type)
    return {"items": data, "total": len(data), "source": "montgomery_arcgis"}


# ── Vacant / Blighted Properties ─────────────────────────────────────────────


@router.get("/vacant-properties")
async def get_vacant_properties(
    limit: int = Query(200, ge=1, le=1000),
):
    """Fetch vacant/blighted property reports from Montgomery 311 data."""
    data = await fetch_vacant_properties(limit=limit)
    return {"items": data, "total": len(data), "source": "montgomery_arcgis"}


# ── Workforce & Employment Data ──────────────────────────────────────────────


@router.get("/workforce")
async def get_workforce_data():
    """
    Comprehensive workforce data for Montgomery, AL.
    Includes employment stats, industry breakdown, education, and commuting.
    Source: US Census ACS 5-year estimates.
    """
    data = await fetch_workforce_summary()
    return data


# ── Data Source Summary ──────────────────────────────────────────────────────


@router.get("/data-sources")
async def get_data_sources():
    """
    Check availability and status of all Montgomery data sources.
    Used by the frontend to show data provenance.
    """
    summary = await get_data_summary()
    summary["sources"]["workforce"] = {
        "available": True,
        "source": "US Census Bureau ACS",
    }
    summary["sources"]["brightdata"] = {
        "available": True,
        "source": "Bright Data Web Scraper API",
    }
    summary["total_sources"] = len(summary["sources"])
    return summary
