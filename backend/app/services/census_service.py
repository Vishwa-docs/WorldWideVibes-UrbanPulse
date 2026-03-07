"""
US Census Bureau API service.

Fetches real demographic data from the ACS 5-Year (2022) survey
for Montgomery, Alabama (State 01, County 101, City 51000).
"""

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── FIPS codes for Montgomery, AL ─────────────────────────────────────────
STATE_FIPS = "01"
COUNTY_FIPS = "101"
CITY_FIPS = "51000"

# ── ACS 5-Year 2022 base URL ─────────────────────────────────────────────
ACS_BASE = "https://api.census.gov/data/2022/acs/acs5"

# ── Census Geocoder endpoint ─────────────────────────────────────────────
GEOCODER_URL = (
    "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
)

# ── Variables we request ──────────────────────────────────────────────────
VARIABLES = {
    "B01003_001E": "total_population",
    "B19013_001E": "median_household_income",
    "B25077_001E": "median_home_value",
    "B25003_001E": "total_housing_units",
    "B25003_002E": "owner_occupied",
    "B25003_003E": "renter_occupied",
    "B25002_003E": "vacant_housing_units",
    "B02001_002E": "white_alone",
    "B02001_003E": "black_african_american_alone",
    "B17001_002E": "below_poverty_level",
    "B23025_005E": "unemployed",
    "B23025_002E": "in_labor_force",
    "B08303_001E": "total_commuters",
    # Education attainment (25+)
    "B15003_001E": "edu_total_25plus",
    "B15003_017E": "edu_high_school",
    "B15003_021E": "edu_bachelors",
    "B15003_022E": "edu_masters",
    "B15003_025E": "edu_doctorate",
    # Age groups
    "B01001_003E": "age_under_5_male",
    "B01001_027E": "age_under_5_female",
    "B01001_020E": "age_65_66_male",
    "B01001_044E": "age_65_66_female",
    # Median age
    "B01002_001E": "median_age",
    # Means of transportation to work
    "B08301_001E": "commute_total",
    "B08301_003E": "commute_drove_alone",
    "B08301_010E": "commute_public_transit",
    "B08301_019E": "commute_walked",
    "B08301_021E": "commute_work_from_home",
    # Vehicles available
    "B25044_003E": "zero_vehicle_households",
    "B25044_001E": "total_vehicle_households",
}

VARIABLE_LIST = ",".join(VARIABLES.keys())


def _safe_int(value: Any) -> int | None:
    """Convert a Census API value to int, returning None for missing data."""
    if value is None or value == "":
        return None
    try:
        v = int(value)
        return None if v < 0 else v  # Census uses negatives for N/A
    except (ValueError, TypeError):
        return None


def _pct(numerator: int | None, denominator: int | None) -> float | None:
    """Calculate percentage, returning None if inputs are unusable."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round((numerator / denominator) * 100, 2)


def _parse_row(header: list[str], row: list[str]) -> dict:
    """Parse a single Census API response row into a labelled dict."""
    raw: dict[str, int | None] = {}
    for col, val in zip(header, row):
        if col in VARIABLES:
            raw[VARIABLES[col]] = _safe_int(val)

    total_pop = raw.get("total_population")
    total_housing = raw.get("total_housing_units")
    labor_force = raw.get("in_labor_force")

    return {
        "total_population": raw.get("total_population"),
        "median_household_income": raw.get("median_household_income"),
        "median_home_value": raw.get("median_home_value"),
        "median_age": raw.get("median_age"),
        "housing": {
            "total_units": total_housing,
            "owner_occupied": raw.get("owner_occupied"),
            "renter_occupied": raw.get("renter_occupied"),
            "vacant": raw.get("vacant_housing_units"),
            "owner_occupied_pct": _pct(raw.get("owner_occupied"), total_housing),
            "renter_occupied_pct": _pct(raw.get("renter_occupied"), total_housing),
            "vacancy_rate_pct": _pct(raw.get("vacant_housing_units"), total_housing),
        },
        "race": {
            "white_alone": raw.get("white_alone"),
            "black_african_american_alone": raw.get("black_african_american_alone"),
            "white_pct": _pct(raw.get("white_alone"), total_pop),
            "black_african_american_pct": _pct(
                raw.get("black_african_american_alone"), total_pop
            ),
        },
        "economics": {
            "below_poverty_level": raw.get("below_poverty_level"),
            "poverty_rate_pct": _pct(raw.get("below_poverty_level"), total_pop),
            "unemployed": raw.get("unemployed"),
            "in_labor_force": labor_force,
            "unemployment_rate_pct": _pct(raw.get("unemployed"), labor_force),
        },
        "education": {
            "total_25plus": raw.get("edu_total_25plus"),
            "high_school": raw.get("edu_high_school"),
            "bachelors": raw.get("edu_bachelors"),
            "masters": raw.get("edu_masters"),
            "doctorate": raw.get("edu_doctorate"),
            "bachelors_plus_pct": _pct(
                (raw.get("edu_bachelors") or 0) + (raw.get("edu_masters") or 0) + (raw.get("edu_doctorate") or 0),
                raw.get("edu_total_25plus"),
            ) if raw.get("edu_total_25plus") else None,
        },
        "commuting": {
            "total": raw.get("total_commuters"),
            "commute_total": raw.get("commute_total"),
            "drove_alone": raw.get("commute_drove_alone"),
            "public_transit": raw.get("commute_public_transit"),
            "walked": raw.get("commute_walked"),
            "work_from_home": raw.get("commute_work_from_home"),
            "drove_alone_pct": _pct(raw.get("commute_drove_alone"), raw.get("commute_total")),
            "public_transit_pct": _pct(raw.get("commute_public_transit"), raw.get("commute_total")),
            "work_from_home_pct": _pct(raw.get("commute_work_from_home"), raw.get("commute_total")),
        },
        "transportation": {
            "zero_vehicle_households": raw.get("zero_vehicle_households"),
            "total_vehicle_households": raw.get("total_vehicle_households"),
            "zero_vehicle_pct": _pct(raw.get("zero_vehicle_households"), raw.get("total_vehicle_households")),
        },
    }


class CensusService:
    """Fetches real demographic data from the US Census Bureau API."""

    def __init__(self) -> None:
        self._api_key = get_settings().census_api_key
        if not self._api_key:
            raise RuntimeError(
                "Census API key is not configured. "
                "Set the CENSUS_API_KEY environment variable."
            )

    # ── Public methods ────────────────────────────────────────────────────

    async def get_tract_demographics(self, lat: float, lng: float) -> dict:
        """Geocode a lat/lng to a census tract, then fetch ACS demographics.

        Args:
            lat: Latitude of the location.
            lng: Longitude of the location.

        Returns:
            Dict with tract GEOID and demographic data.
        """
        tract_info = await self._geocode_to_tract(lat, lng)
        state = tract_info["state"]
        county = tract_info["county"]
        tract = tract_info["tract"]

        logger.info(
            "Fetching demographics for tract %s (state=%s, county=%s)",
            tract, state, county,
        )

        params = {
            "get": f"NAME,{VARIABLE_LIST}",
            "for": f"tract:{tract}",
            "in": f"state:{state} county:{county}",
            "key": self._api_key,
        }

        data = await self._census_get(params)
        header, row = data[0], data[1]

        result = _parse_row(header, row)
        result["geoid"] = f"{state}{county}{tract}"
        result["tract_name"] = row[header.index("NAME")] if "NAME" in header else None
        return result

    async def get_city_overview(self) -> dict:
        """Fetch overall demographics for Montgomery city.

        Returns:
            Dict with city-level demographic data.
        """
        logger.info("Fetching city overview for Montgomery, AL (place %s)", CITY_FIPS)

        params = {
            "get": f"NAME,{VARIABLE_LIST}",
            "for": f"place:{CITY_FIPS}",
            "in": f"state:{STATE_FIPS}",
            "key": self._api_key,
        }

        data = await self._census_get(params)
        header, row = data[0], data[1]

        result = _parse_row(header, row)
        result["place_name"] = row[header.index("NAME")] if "NAME" in header else None
        return result

    async def get_neighborhood_demographics(self, tracts: list[str]) -> dict:
        """Fetch demographics for several census tracts at once.

        Args:
            tracts: List of 6-digit tract codes (e.g. ["000100", "000200"]).

        Returns:
            Dict keyed by tract GEOID with demographic data for each.
        """
        if not tracts:
            return {}

        tract_filter = ",".join(tracts)
        logger.info(
            "Fetching neighborhood demographics for %d tracts in Montgomery County",
            len(tracts),
        )

        params = {
            "get": f"NAME,{VARIABLE_LIST}",
            "for": f"tract:{tract_filter}",
            "in": f"state:{STATE_FIPS} county:{COUNTY_FIPS}",
            "key": self._api_key,
        }

        data = await self._census_get(params)
        header = data[0]

        results: dict[str, dict] = {}
        for row in data[1:]:
            parsed = _parse_row(header, row)
            # Build GEOID from the geography columns
            st = row[header.index("state")] if "state" in header else STATE_FIPS
            co = row[header.index("county")] if "county" in header else COUNTY_FIPS
            tr = row[header.index("tract")] if "tract" in header else ""
            geoid = f"{st}{co}{tr}"
            parsed["geoid"] = geoid
            parsed["tract_name"] = (
                row[header.index("NAME")] if "NAME" in header else None
            )
            results[geoid] = parsed

        return results

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _geocode_to_tract(self, lat: float, lng: float) -> dict:
        """Use the Census Geocoder to resolve lat/lng to a tract.

        Returns:
            Dict with keys: state, county, tract, block, geoid.
        """
        params = {
            "x": str(lng),
            "y": str(lat),
            "benchmark": "Public_AR_Current",
            "vintage": "Current_Current",
            "format": "json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(GEOCODER_URL, params=params)
            resp.raise_for_status()
            payload = resp.json()

        geographies = payload.get("result", {}).get("geographies", {})

        # The tract info lives under "Census Tracts"
        tracts = geographies.get("Census Tracts", [])
        if not tracts:
            raise ValueError(
                f"Census geocoder returned no tract for ({lat}, {lng}). "
                "The location may be outside any census tract."
            )

        tract = tracts[0]
        return {
            "state": tract.get("STATE", ""),
            "county": tract.get("COUNTY", ""),
            "tract": tract.get("TRACT", ""),
            "block": tract.get("BLOCK", ""),
            "geoid": tract.get("GEOID", ""),
        }

    async def _census_get(self, params: dict) -> list[list[str]]:
        """Make a request to the Census ACS API and return the JSON table.

        The Census API returns data as a list-of-lists where the first
        element is the header row.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(ACS_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        if not isinstance(data, list) or len(data) < 2:
            raise ValueError(
                f"Unexpected Census API response shape: {type(data)} "
                f"(expected list with ≥ 2 rows)"
            )
        return data


# ── Factory ───────────────────────────────────────────────────────────────

_instance: CensusService | None = None


def get_census_service() -> CensusService:
    """Return a module-level CensusService singleton.

    Raises RuntimeError if CENSUS_API_KEY is not set.
    """
    global _instance
    if _instance is None:
        _instance = CensusService()
    return _instance
