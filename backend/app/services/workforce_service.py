"""
Workforce data service for Montgomery, AL.

Aggregates employment and workforce data from:
- US Census Bureau API (County Business Patterns, ACS)
- Bureau of Labor Statistics (BLS) public data

Uses the same Census API key already configured for demographics.
"""

import httpx
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)

# Montgomery County, AL FIPS: State=01, County=101
MONTGOMERY_STATE_FIPS = "01"
MONTGOMERY_COUNTY_FIPS = "101"
MONTGOMERY_PLACE_FIPS = "51000"  # Montgomery city


async def fetch_workforce_summary() -> dict:
    """
    Aggregate workforce/employment data for Montgomery from Census ACS.
    Returns employment stats, industry breakdown, and commuting data.
    """
    settings = get_settings()
    api_key = settings.census_api_key

    result = {
        "area": "Montgomery, AL",
        "employment": {},
        "industries": [],
        "education": {},
        "commuting": {},
        "source": "us_census_acs",
    }

    # ── Employment from ACS 5-year ─────────────────────────────────────
    try:
        employment_vars = [
            "B23025_001E",  # Total population 16+
            "B23025_002E",  # In labor force
            "B23025_003E",  # Civilian labor force
            "B23025_004E",  # Employed
            "B23025_005E",  # Unemployed
            "B23025_007E",  # Not in labor force
        ]
        emp_data = await _census_query(
            "acs/acs5",
            employment_vars,
            geo=f"place:{MONTGOMERY_PLACE_FIPS}",
            state=MONTGOMERY_STATE_FIPS,
            api_key=api_key,
        )
        if emp_data:
            pop16 = _safe_int(emp_data.get("B23025_001E"))
            in_lf = _safe_int(emp_data.get("B23025_002E"))
            employed = _safe_int(emp_data.get("B23025_004E"))
            unemployed = _safe_int(emp_data.get("B23025_005E"))
            not_in_lf = _safe_int(emp_data.get("B23025_007E"))

            result["employment"] = {
                "population_16_plus": pop16,
                "in_labor_force": in_lf,
                "employed": employed,
                "unemployed": unemployed,
                "not_in_labor_force": not_in_lf,
                "labor_force_participation_rate": round(in_lf / pop16 * 100, 1) if pop16 else 0,
                "unemployment_rate": round(unemployed / in_lf * 100, 1) if in_lf else 0,
                "employment_rate": round(employed / in_lf * 100, 1) if in_lf else 0,
            }
    except Exception as e:
        logger.error("Census employment query failed: %s", e)

    # ── Industry breakdown from ACS ────────────────────────────────────
    try:
        industry_vars = [
            "C24030_001E",  # Total employed 16+
            "C24030_003E",  # Agriculture
            "C24030_004E",  # Construction
            "C24030_005E",  # Manufacturing
            "C24030_006E",  # Wholesale trade
            "C24030_007E",  # Retail trade
            "C24030_008E",  # Transportation/warehousing
            "C24030_009E",  # Information
            "C24030_010E",  # Finance/insurance/real estate
            "C24030_011E",  # Professional/scientific/management
            "C24030_012E",  # Educational/health/social
            "C24030_013E",  # Arts/entertainment/food
            "C24030_014E",  # Other services
            "C24030_015E",  # Public administration
        ]
        ind_data = await _census_query(
            "acs/acs5",
            industry_vars,
            geo=f"place:{MONTGOMERY_PLACE_FIPS}",
            state=MONTGOMERY_STATE_FIPS,
            api_key=api_key,
        )
        if ind_data:
            total_emp = _safe_int(ind_data.get("C24030_001E"))
            industry_map = {
                "Agriculture/Mining": "C24030_003E",
                "Construction": "C24030_004E",
                "Manufacturing": "C24030_005E",
                "Wholesale Trade": "C24030_006E",
                "Retail Trade": "C24030_007E",
                "Transportation/Warehousing": "C24030_008E",
                "Information": "C24030_009E",
                "Finance/Insurance/Real Estate": "C24030_010E",
                "Professional/Scientific/Management": "C24030_011E",
                "Education/Healthcare/Social": "C24030_012E",
                "Arts/Entertainment/Food Services": "C24030_013E",
                "Other Services": "C24030_014E",
                "Public Administration": "C24030_015E",
            }
            industries = []
            for name, var in industry_map.items():
                count = _safe_int(ind_data.get(var))
                pct = round(count / total_emp * 100, 1) if total_emp else 0
                industries.append({
                    "industry": name,
                    "employed": count,
                    "percentage": pct,
                })
            industries.sort(key=lambda x: x["employed"], reverse=True)
            result["industries"] = industries
    except Exception as e:
        logger.error("Census industry query failed: %s", e)

    # ── Education attainment ───────────────────────────────────────────
    try:
        edu_vars = [
            "B15003_001E",  # Total 25+
            "B15003_017E",  # HS diploma
            "B15003_018E",  # GED
            "B15003_021E",  # Associate's
            "B15003_022E",  # Bachelor's
            "B15003_023E",  # Master's
            "B15003_024E",  # Professional
            "B15003_025E",  # Doctorate
        ]
        edu_data = await _census_query(
            "acs/acs5",
            edu_vars,
            geo=f"place:{MONTGOMERY_PLACE_FIPS}",
            state=MONTGOMERY_STATE_FIPS,
            api_key=api_key,
        )
        if edu_data:
            total_25 = _safe_int(edu_data.get("B15003_001E"))
            hs = _safe_int(edu_data.get("B15003_017E")) + _safe_int(edu_data.get("B15003_018E"))
            assoc = _safe_int(edu_data.get("B15003_021E"))
            bach = _safe_int(edu_data.get("B15003_022E"))
            grad = (
                _safe_int(edu_data.get("B15003_023E"))
                + _safe_int(edu_data.get("B15003_024E"))
                + _safe_int(edu_data.get("B15003_025E"))
            )
            result["education"] = {
                "population_25_plus": total_25,
                "high_school_diploma": hs,
                "associates_degree": assoc,
                "bachelors_degree": bach,
                "graduate_degree": grad,
                "bachelors_or_higher_pct": round((bach + grad) / total_25 * 100, 1) if total_25 else 0,
                "hs_or_higher_pct": round((hs + assoc + bach + grad) / total_25 * 100, 1) if total_25 else 0,
            }
    except Exception as e:
        logger.error("Census education query failed: %s", e)

    # ── Commuting data ─────────────────────────────────────────────────
    try:
        commute_vars = [
            "B08301_001E",  # Total workers 16+
            "B08301_003E",  # Drove alone
            "B08301_004E",  # Carpooled
            "B08301_010E",  # Public transit
            "B08301_019E",  # Walked
            "B08301_021E",  # Worked from home
            "B08303_001E",  # Total commuters
            "B08303_008E",  # 30-34 mins
            "B08303_012E",  # 45-59 mins
            "B08303_013E",  # 60+ mins
        ]
        comm_data = await _census_query(
            "acs/acs5",
            commute_vars,
            geo=f"place:{MONTGOMERY_PLACE_FIPS}",
            state=MONTGOMERY_STATE_FIPS,
            api_key=api_key,
        )
        if comm_data:
            total_workers = _safe_int(comm_data.get("B08301_001E"))
            result["commuting"] = {
                "total_workers": total_workers,
                "drove_alone": _safe_int(comm_data.get("B08301_003E")),
                "carpooled": _safe_int(comm_data.get("B08301_004E")),
                "public_transit": _safe_int(comm_data.get("B08301_010E")),
                "walked": _safe_int(comm_data.get("B08301_019E")),
                "work_from_home": _safe_int(comm_data.get("B08301_021E")),
                "drove_alone_pct": round(
                    _safe_int(comm_data.get("B08301_003E")) / total_workers * 100, 1
                ) if total_workers else 0,
            }
    except Exception as e:
        logger.error("Census commuting query failed: %s", e)

    return result


# ── Helper functions ────────────────────────────────────────────────────────


def _safe_int(val) -> int:
    """Safely convert Census API value to int."""
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


async def _census_query(
    dataset: str,
    variables: list[str],
    geo: str,
    state: str,
    api_key: str,
    year: int = 2022,
) -> Optional[dict]:
    """Query US Census API and return dict of variable -> value."""
    var_str = ",".join(variables)
    url = f"https://api.census.gov/data/{year}/{dataset}"
    params = {
        "get": var_str,
        "for": geo,
        "in": f"state:{state}",
        "key": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if len(data) < 2:
            return None

        headers = data[0]
        values = data[1]
        return dict(zip(headers, values))

    except Exception as e:
        logger.error("Census API query failed (%s): %s", dataset, e)
        return None
