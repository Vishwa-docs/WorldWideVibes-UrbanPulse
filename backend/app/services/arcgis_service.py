"""
Montgomery ArcGIS Open Data integration service.

Fetches free, publicly available data from Montgomery's ArcGIS REST APIs:
- 311 Service Requests
- Most Visited Locations (foot traffic)
- Visitor Origin data
- Business License data
- Code Violations / Enforcement (crime/blight)
- Opportunity Zones (federal tax incentives)
- City-Owned Properties
- Building / Construction Permits

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
    "HostedDatasets/Business_License/FeatureServer/0/query"
)
ARCGIS_CODE_VIOLATIONS = (
    "https://mgmgis.montgomeryal.gov/arcgis/rest/services/"
    "HostedDatasets/Code_Violations/FeatureServer/0/query"
)
ARCGIS_CITY_OWNED = (
    "https://mgmgis.montgomeryal.gov/arcgis/rest/services/"
    "HostedDatasets/City_Owned_Properities/FeatureServer/0/query"
)
ARCGIS_CONSTRUCTION_PERMITS = (
    "https://mgmgis.montgomeryal.gov/arcgis/rest/services/"
    "HostedDatasets/Construction_Permits/FeatureServer/0/query"
)
ARCGIS_OPPORTUNITY_ZONES = (
    "https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/"
    "Opportunity_Zones/FeatureServer/0/query"
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

    items = [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "category": (
                r.get("Request_Type") or r.get("request_type")
                or r.get("CATEGORY") or r.get("category")
                or r.get("Category", "Unknown")
            ),
            "description": (
                r.get("Department") or r.get("department")
                or r.get("DESCRIPTION") or r.get("description")
                or r.get("Description", "")
            ),
            "status": r.get("STATUS") or r.get("status") or r.get("Status", ""),
            "address": r.get("ADDRESS") or r.get("address") or r.get("Address", ""),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "created_date": r.get("Create_Date") or r.get("CREATEDATE") or r.get("created_date"),
            "source": "montgomery_arcgis_311",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]
    if items:
        return items
    logger.warning("ArcGIS 311 returned 0 geolocated features")
    return []


async def fetch_most_visited_locations(limit: int = 200) -> list[dict]:
    """Fetch most visited locations in Montgomery (foot traffic proxy)."""
    raw = await _query_arcgis(ARCGIS_MOST_VISITED, max_records=limit)

    # Most Visited features store coordinates in attributes (x/y) or geometry
    for r in raw:
        if not r.get("latitude") and r.get("y"):
            r["latitude"] = r["y"]
        if not r.get("longitude") and r.get("x"):
            r["longitude"] = r["x"]

    items = [
        {
            "id": r.get("ObjectId") or r.get("OBJECTID") or r.get("objectid") or r.get("FID"),
            "name": r.get("Name") or r.get("name") or r.get("NAME") or r.get("location_name", "Unknown"),
            "category": (
                r.get("Category_Group") or r.get("Category")
                or r.get("category") or r.get("CATEGORY", "")
            ),
            "visits": (
                r.get("F__of_Visits") or r.get("f__of_visits")
                or r.get("Visits") or r.get("visits")
                or r.get("VISITS") or r.get("raw_visit_counts", 0)
            ),
            "visitors": (
                r.get("Visitors") or r.get("visitors")
                or r.get("VISITORS") or r.get("raw_visitor_counts")
                or max(1, int((r.get("F__of_Visits") or 0) * 0.3))
            ),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_most_visited",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]
    if items:
        return items
    logger.warning("ArcGIS most-visited returned 0 geolocated features")
    return []


async def fetch_visitor_origin(limit: int = 200) -> list[dict]:
    """Fetch visitor origin / foot traffic data."""
    raw = await _query_arcgis(ARCGIS_VISITOR_ORIGIN, max_records=limit)

    items = [
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
    if items:
        return items
    logger.warning("ArcGIS visitor-origin returned 0 geolocated features")
    return []


async def fetch_business_licenses(
    limit: int = 200,
    business_type: Optional[str] = None,
) -> list[dict]:
    """Fetch business license data from Montgomery."""
    extra = {}
    if business_type:
        extra["where"] = f"UPPER(scNAME) LIKE '%{business_type.upper()}%'"
    raw = await _query_arcgis(ARCGIS_BUSINESS_LICENSES, extra_params=extra, max_records=limit)

    items = [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "business_name": (
                r.get("custCOMPANY_NAME") or r.get("paccCOMPANY")
                or r.get("custDBA") or r.get("BUSINESS_NAME")
                or r.get("business_name") or r.get("DBA", "")
            ),
            "business_type": (
                r.get("scNAME") or r.get("pvscDESC")
                or r.get("BUSINESS_TYPE") or r.get("business_type")
                or r.get("NAICS_Description", "")
            ),
            "address": (
                r.get("Full_Address")
                or r.get("ADDRESS") or r.get("address")
                or r.get("Physical_Address", "")
            ),
            "status": "Active" if r.get("pvEXPIRE") else "Unknown",
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_business_licenses",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]
    if items:
        return items
    logger.warning("ArcGIS business-licenses returned 0 geolocated features")
    return []


async def fetch_vacant_properties(limit: int = 200) -> list[dict]:
    """
    Fetch vacant/blighted properties from Montgomery open data.
    Falls back to 311 'Vacant' category if no dedicated endpoint.
    """
    # Try 311 requests that mention vacant/blight
    extra = {
        "where": (
            "UPPER(Request_Type) LIKE '%VACANT%' OR "
            "UPPER(Request_Type) LIKE '%BLIGHT%' OR "
            "UPPER(Request_Type) LIKE '%ABANDON%'"
        )
    }
    raw = await _query_arcgis(ARCGIS_311, extra_params=extra, max_records=limit)

    items = [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "category": (
                r.get("Request_Type") or r.get("request_type")
                or r.get("CATEGORY") or r.get("category", "Vacant")
            ),
            "description": (
                r.get("Department") or r.get("department")
                or r.get("DESCRIPTION") or r.get("description", "")
            ),
            "address": r.get("ADDRESS") or r.get("address", ""),
            "status": r.get("STATUS") or r.get("status", ""),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_311_vacant",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]
    if items:
        return items
    logger.warning("ArcGIS vacant-properties returned 0 geolocated features")
    return []


async def get_data_summary() -> dict:
    """Fetch summary counts from all Montgomery data sources."""
    import asyncio

    results = await asyncio.gather(
        _query_arcgis(ARCGIS_311, max_records=1),
        _query_arcgis(ARCGIS_MOST_VISITED, max_records=1),
        _query_arcgis(ARCGIS_VISITOR_ORIGIN, max_records=1),
        _query_arcgis(ARCGIS_BUSINESS_LICENSES, max_records=1),
        _query_arcgis(ARCGIS_CODE_VIOLATIONS, max_records=1),
        _query_arcgis(ARCGIS_OPPORTUNITY_ZONES, max_records=1),
        _query_arcgis(ARCGIS_CITY_OWNED, max_records=1),
        _query_arcgis(ARCGIS_CONSTRUCTION_PERMITS, max_records=1),
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
            "code_violations": {"available": _count(results[4]) > 0, "source": "Montgomery ArcGIS Open Data"},
            "opportunity_zones": {"available": _count(results[5]) > 0, "source": "Montgomery ArcGIS Open Data"},
            "city_owned_properties": {"available": _count(results[6]) > 0, "source": "Montgomery ArcGIS Open Data"},
            "building_permits": {"available": _count(results[7]) > 0, "source": "Montgomery ArcGIS Open Data"},
        },
        "total_sources": 8,
    }


# ── Code Violations / Enforcement (Crime/Blight) ────────────────────────────


async def fetch_code_violations(
    limit: int = 200,
    violation_type: Optional[str] = None,
) -> list[dict]:
    """Fetch code violation / enforcement reports from Montgomery.
    Serves as a crime/blight proxy — shows areas with enforcement activity."""
    extra = {}
    if violation_type:
        extra["where"] = f"UPPER(VIOLATION_TYPE) LIKE '%{violation_type.upper()}%'"
    raw = await _query_arcgis(ARCGIS_CODE_VIOLATIONS, extra_params=extra, max_records=limit)

    items = [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "violation_type": (
                r.get("CaseType") or r.get("CASE_TYPE") or r.get("case_type")
                or r.get("VIOLATION_TYPE") or r.get("violation_type") or "Unknown"
            ),
            "description": (
                r.get("ComplaintRem") or r.get("DESCRIPTION") or r.get("description")
                or r.get("VIOLATION") or r.get("violation") or ""
            ),
            "status": (
                r.get("CaseStatus") or r.get("CASE_STATUS")
                or r.get("STATUS") or r.get("status", "")
            ),
            "address": (
                r.get("Address1") or r.get("ADDRESS")
                or r.get("address") or r.get("LOCATION", "")
            ),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "created_date": (
                r.get("CaseDate") or r.get("CREATEDATE")
                or r.get("created_date") or r.get("OPENED_DATE")
            ),
            "source": "montgomery_arcgis_code_violations",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]
    if items:
        return items
    logger.warning("ArcGIS code-violations returned 0 geolocated features")
    return []


async def fetch_opportunity_zones(limit: int = 100) -> list[dict]:
    """Fetch federal Opportunity Zone boundaries in Montgomery.
    These are tax-incentive zones that encourage investment in underserved areas."""
    raw = await _query_arcgis(ARCGIS_OPPORTUNITY_ZONES, max_records=limit)

    items = [
        {
            "id": r.get("OBJECTID") or r.get("objectid") or r.get("FID"),
            "name": (
                r.get("NAME") or r.get("name")
                or r.get("NAMELSAD") or r.get("GEOID") or f"OZ-{i}"
            ),
            "tract_id": r.get("GEOID") or r.get("TRACTCE") or r.get("geoid", ""),
            "designation": r.get("DESIGNATION") or r.get("designation") or "Qualified Opportunity Zone",
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_opportunity_zones",
        }
        for i, r in enumerate(raw)
        if r.get("latitude") and r.get("longitude")
    ]
    if items:
        return items
    logger.warning("ArcGIS opportunity-zones returned 0 geolocated features")
    return []


async def fetch_city_owned_properties(limit: int = 200) -> list[dict]:
    """Fetch city-owned properties from Montgomery open data.
    Directly addresses challenge: 'Analyze and improve usage of city-owned properties'."""
    raw = await _query_arcgis(ARCGIS_CITY_OWNED, max_records=limit)

    items = [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "name": (
                r.get("NAME") or r.get("name")
                or r.get("PROPERTY_NAME") or r.get("FACILITY") or ""
            ),
            "property_type": (
                r.get("TYPE") or r.get("type")
                or r.get("PROPERTY_TYPE") or r.get("CATEGORY") or "City Property"
            ),
            "address": r.get("ADDRESS") or r.get("address") or r.get("LOCATION", ""),
            "status": r.get("STATUS") or r.get("status") or "Active",
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_city_owned",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]
    if items:
        return items
    logger.warning("ArcGIS city-owned returned 0 geolocated features")
    return []


async def fetch_building_permits(
    limit: int = 200,
    permit_type: Optional[str] = None,
) -> list[dict]:
    """Fetch building/construction permits from Montgomery.
    Shows where new development is happening — economic growth signal."""
    extra = {}
    if permit_type:
        extra["where"] = f"UPPER(PERMIT_TYPE) LIKE '%{permit_type.upper()}%'"
    raw = await _query_arcgis(ARCGIS_CONSTRUCTION_PERMITS, extra_params=extra, max_records=limit)

    items = [
        {
            "id": r.get("OBJECTID") or r.get("objectid"),
            "permit_type": (
                r.get("PERMIT_TYPE") or r.get("permit_type")
                or r.get("TYPE") or r.get("type") or "Construction"
            ),
            "description": (
                r.get("DESCRIPTION") or r.get("description")
                or r.get("WORK_DESCRIPTION") or ""
            ),
            "address": r.get("ADDRESS") or r.get("address") or r.get("LOCATION", ""),
            "status": r.get("STATUS") or r.get("status") or "Active",
            "issued_date": r.get("ISSUED_DATE") or r.get("issued_date") or r.get("CREATEDATE"),
            "latitude": r.get("latitude", 0),
            "longitude": r.get("longitude", 0),
            "source": "montgomery_arcgis_building_permits",
        }
        for r in raw
        if r.get("latitude") and r.get("longitude")
    ]
    if items:
        return items
    logger.warning("ArcGIS building-permits returned 0 geolocated features")
    return []
