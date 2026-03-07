"""
Montgomery ArcGIS Open Data integration service.

Fetches free, publicly available data from Montgomery's ArcGIS REST APIs:
- 311 Service Requests
- Most Visited Locations (foot traffic)
- Visitor Origin data
- Business License data

No authentication required — all endpoints are open.
"""

import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── ArcGIS REST Endpoints ───────────────────────────────────────────────────
ARCGIS_311 = (
    "https://mgmgis.montgomeryal.gov/arcgis/rest/services/"
    "HostedDatasets/Received_311_Service_Request/FeatureServer/0/query"
)
ARCGIS_MOST_VISITED = (
    "https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/"
    "Most_Visited_Locations/FeatureServer/0/query"
)
ARCGIS_VISITOR_ORIGIN = (
    "https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/"
    "Visitors_Origin/FeatureServer/0/query"
)
ARCGIS_BUSINESS_LICENSES = (
    "https://mgmgis.montgomeryal.gov/arcgis/rest/services/"
    "HostedDatasets/Business_Licenses/FeatureServer/0/query"
)

# Default query parameters for ArcGIS REST API
DEFAULT_PARAMS = {
    "where": "1=1",
    "outFields": "*",
    "f": "json",
    "returnGeometry": "true",
    "outSR": "4326",  # WGS84 lat/lng
}


async def _query_arcgis(
    url: str,
    extra_params: Optional[dict] = None,
    max_records: int = 500,
) -> list[dict]:
    """Generic ArcGIS feature query. Returns list of feature attributes+geometry."""
    params = {**DEFAULT_PARAMS, "resultRecordCount": str(max_records)}
    if extra_params:
        params.update(extra_params)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        features = data.get("features", [])
        results = []
        for feat in features:
            attrs = feat.get("attributes", {})
            geom = feat.get("geometry", {})
            # ArcGIS may return x/y or latitude/longitude or rings
            if "x" in geom and "y" in geom:
                attrs["longitude"] = geom["x"]
                attrs["latitude"] = geom["y"]
            elif "rings" in geom:
                # Polygon — compute centroid from first ring
                ring = geom["rings"][0] if geom["rings"] else []
                if ring:
                    attrs["longitude"] = sum(p[0] for p in ring) / len(ring)
                    attrs["latitude"] = sum(p[1] for p in ring) / len(ring)
            results.append(attrs)
        return results

    except Exception as e:
        logger.error("ArcGIS query failed for %s: %s", url, e)
        return []


# ── Public API ──────────────────────────────────────────────────────────────


async def fetch_311_requests(
    limit: int = 200,
    category: Optional[str] = None,
) -> list[dict]:
    """Fetch 311 service requests from Montgomery open data."""
    extra = {}
    if category:
        extra["where"] = f"UPPER(CATEGORY) LIKE '%{category.upper()}%'"
    raw = await _query_arcgis(ARCGIS_311, extra_params=extra, max_records=limit)

    return [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "category": r.get("CATEGORY") or r.get("category") or r.get("Category", "Unknown"),
            "description": r.get("DESCRIPTION") or r.get("description") or r.get("Description", ""),
            "status": r.get("STATUS") or r.get("status") or r.get("Status", ""),
            "address": r.get("ADDRESS") or r.get("address") or r.get("Address", ""),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "created_date": r.get("CREATEDATE") or r.get("created_date"),
            "source": "montgomery_arcgis_311",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]


async def fetch_most_visited_locations(limit: int = 200) -> list[dict]:
    """Fetch most visited locations in Montgomery (foot traffic proxy)."""
    raw = await _query_arcgis(ARCGIS_MOST_VISITED, max_records=limit)

    return [
        {
            "id": r.get("OBJECTID") or r.get("objectid") or r.get("FID"),
            "name": r.get("Name") or r.get("name") or r.get("NAME") or r.get("location_name", "Unknown"),
            "category": r.get("Category") or r.get("category") or r.get("CATEGORY", ""),
            "visits": r.get("Visits") or r.get("visits") or r.get("VISITS") or r.get("raw_visit_counts", 0),
            "visitors": r.get("Visitors") or r.get("visitors") or r.get("VISITORS") or r.get("raw_visitor_counts", 0),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_most_visited",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]


async def fetch_visitor_origin(limit: int = 200) -> list[dict]:
    """Fetch visitor origin / foot traffic data."""
    raw = await _query_arcgis(ARCGIS_VISITOR_ORIGIN, max_records=limit)

    return [
        {
            "id": r.get("OBJECTID") or r.get("objectid") or r.get("FID"),
            "origin": r.get("Origin") or r.get("origin") or r.get("ORIGIN") or r.get("poi_cbg", ""),
            "destination": r.get("Destination") or r.get("destination") or "",
            "visitor_count": r.get("Count") or r.get("count") or r.get("visitor_count") or r.get("number_of_visits", 0),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_visitor_origin",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]


async def fetch_business_licenses(
    limit: int = 200,
    business_type: Optional[str] = None,
) -> list[dict]:
    """Fetch business license data from Montgomery."""
    extra = {}
    if business_type:
        extra["where"] = f"UPPER(BUSINESS_TYPE) LIKE '%{business_type.upper()}%'"
    raw = await _query_arcgis(ARCGIS_BUSINESS_LICENSES, extra_params=extra, max_records=limit)

    return [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "business_name": r.get("BUSINESS_NAME") or r.get("business_name") or r.get("DBA", ""),
            "business_type": r.get("BUSINESS_TYPE") or r.get("business_type") or r.get("NAICS_Description", ""),
            "address": r.get("ADDRESS") or r.get("address") or r.get("Physical_Address", ""),
            "status": r.get("STATUS") or r.get("status") or "Active",
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_business_licenses",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]


async def fetch_vacant_properties(limit: int = 200) -> list[dict]:
    """
    Fetch vacant/blighted properties from Montgomery open data.
    Falls back to 311 'Vacant' category if no dedicated endpoint.
    """
    # Try 311 requests that mention vacant/blight
    extra = {
        "where": (
            "UPPER(CATEGORY) LIKE '%VACANT%' OR "
            "UPPER(CATEGORY) LIKE '%BLIGHT%' OR "
            "UPPER(CATEGORY) LIKE '%ABANDON%' OR "
            "UPPER(DESCRIPTION) LIKE '%VACANT%' OR "
            "UPPER(DESCRIPTION) LIKE '%BLIGHT%'"
        )
    }
    raw = await _query_arcgis(ARCGIS_311, extra_params=extra, max_records=limit)

    return [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "category": r.get("CATEGORY") or r.get("category", "Vacant"),
            "description": r.get("DESCRIPTION") or r.get("description", ""),
            "address": r.get("ADDRESS") or r.get("address", ""),
            "status": r.get("STATUS") or r.get("status", ""),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_311_vacant",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]


async def get_data_summary() -> dict:
    """Fetch summary counts from all Montgomery data sources."""
    import asyncio

    results = await asyncio.gather(
        fetch_311_requests(limit=1),
        fetch_most_visited_locations(limit=1),
        fetch_visitor_origin(limit=1),
        fetch_business_licenses(limit=1),
        return_exceptions=True,
    )

    def _count(r):
        if isinstance(r, Exception):
            return 0
        return len(r)

    return {
        "sources": {
            "311_requests": {"available": _count(results[0]) > 0, "source": "Montgomery ArcGIS Open Data"},
            "most_visited": {"available": _count(results[1]) > 0, "source": "Montgomery ArcGIS Open Data"},
            "visitor_origin": {"available": _count(results[2]) > 0, "source": "Montgomery ArcGIS Open Data"},
            "business_licenses": {"available": _count(results[3]) > 0, "source": "Montgomery ArcGIS Open Data"},
        },
        "total_sources": 4,
    }
