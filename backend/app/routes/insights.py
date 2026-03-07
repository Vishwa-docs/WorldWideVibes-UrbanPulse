"""AI Insights endpoints - site reports, market gap analysis, investment analysis."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.property import Property, PropertyScore, Incident, ServiceLocation
from app.services.llm_service import get_llm_service_safe
from app.services.scoring import get_nearby_incidents, get_nearby_services, haversine_km
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/api/insights", tags=["insights"])
get_llm_service = get_llm_service_safe


@router.get("/site-report/{property_id}")
async def generate_site_report(
    property_id: int,
    scenario: str = "general",
    persona: str = "city_console",
    session: Session = Depends(get_session),
):
    """Generate a comprehensive AI-powered site report for a property."""
    prop = session.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    
    # Get scores
    score = session.exec(
        select(PropertyScore).where(
            PropertyScore.property_id == property_id,
            PropertyScore.scenario == scenario,
        )
    ).first()
    
    # Get nearby context
    incidents = get_nearby_incidents(prop.latitude, prop.longitude, 1.0, session)
    services = get_nearby_services(prop.latitude, prop.longitude, 2.0, session)
    
    # Build comprehensive prompt
    score_data = {}
    if score:
        score_data = {
            "overall_score": score.overall_score,
            "foot_traffic_score": score.foot_traffic_score,
            "competition_score": score.competition_score,
            "safety_score": score.safety_score,
            "equity_score": score.equity_score,
            "activity_index": score.activity_index,
        }
    
    service_summary = {}
    for s in services:
        stype = s.service_type
        if stype not in service_summary:
            service_summary[stype] = 0
        service_summary[stype] += 1
    
    incident_summary = {}
    for inc in incidents:
        itype = inc.incident_type
        if itype not in incident_summary:
            incident_summary[itype] = 0
        incident_summary[itype] += 1
    
    prompt = f"""Generate a comprehensive site report for this property in Montgomery, AL.

PROPERTY DETAILS:
- Address: {prop.address}
- Neighborhood: {prop.neighborhood}
- Property Type: {prop.property_type}
- Zoning: {prop.zoning}
- Lot Size: {prop.lot_size_sqft} sqft
- Building Size: {prop.building_sqft} sqft
- Assessed Value: {f'${prop.assessed_value:,.2f}' if prop.assessed_value else 'N/A'}
- Year Built: {prop.year_built or 'N/A'}
- Vacant: {prop.is_vacant}
- City-Owned: {prop.is_city_owned}

SCORING ({scenario} scenario, {persona} perspective):
{json.dumps(score_data, indent=2)}

NEARBY SERVICES (within 2km):
{json.dumps(service_summary, indent=2)}

NEARBY INCIDENTS (within 1km):
{json.dumps(incident_summary, indent=2)}
Total incidents: {len(incidents)}

Generate a professional site report with these sections:
1. **Executive Summary** - 2-3 sentence overview
2. **Location Analysis** - Neighborhood context, accessibility, visibility
3. **Market Opportunity** - Based on scores and nearby services/gaps
4. **Risk Assessment** - Safety, environmental, and market risks
5. **Financial Considerations** - Estimated value context, investment potential
6. **Recommendations** - Specific, actionable next steps for {persona}
7. **Score Interpretation** - What the scores mean for this {scenario} use case"""

    system_prompt = """You are an expert commercial real estate analyst and urban planner.
Generate detailed, data-driven site reports for properties in Montgomery, Alabama.
Use specific numbers from the data provided. Be professional but accessible.
Your audience is city planners and entrepreneurs evaluating site selection."""

    llm = get_llm_service()
    report = await llm.generate(prompt, system_prompt, temperature=0.6, max_tokens=2000)
    
    now = datetime.now(timezone.utc)
    return {
        "property_id": property_id,
        "property_address": prop.address,
        "address": prop.address,
        "neighborhood": prop.neighborhood,
        "scenario": scenario,
        "persona": persona,
        "report": report,
        "scores": score_data,
        "nearby_services_count": len(services),
        "nearby_incidents_count": len(incidents),
        "generated_at": now.isoformat(),
        "sources": [
            {
                "id": f"site-report-{property_id}-montgomery",
                "label": "Montgomery property and incident datasets",
                "source_type": "montgomery_open_data",
                "is_live": True,
                "observed_at": now.isoformat(),
                "confidence": 0.9,
                "url": "https://opendata.montgomeryal.gov",
            }
        ],
        "timestamps": {"generated_at": now.isoformat()},
        "confidence": 0.83,
    }


@router.get("/market-gaps")
async def analyze_market_gaps(
    scenario: str = "general",
    session: Session = Depends(get_session),
):
    """AI-powered market gap analysis for Montgomery."""
    # Get all services grouped by type
    services = session.exec(select(ServiceLocation)).all()
    service_counts = {}
    for s in services:
        if s.service_type not in service_counts:
            service_counts[s.service_type] = {"count": 0, "neighborhoods": {}}
        service_counts[s.service_type]["count"] += 1
        nbhd = s.neighborhood or "Unknown"
        if nbhd not in service_counts[s.service_type]["neighborhoods"]:
            service_counts[s.service_type]["neighborhoods"][nbhd] = 0
        service_counts[s.service_type]["neighborhoods"][nbhd] += 1
    
    # Get properties with high equity scores (underserved areas)
    high_equity = session.exec(
        select(Property, PropertyScore)
        .join(PropertyScore, Property.id == PropertyScore.property_id)
        .where(PropertyScore.scenario == scenario)
        .where(PropertyScore.equity_score >= 7.0)
        .order_by(PropertyScore.equity_score.desc())
        .limit(10)
    ).all()
    
    underserved_areas = []
    for prop, score in high_equity:
        underserved_areas.append({
            "address": prop.address,
            "neighborhood": prop.neighborhood,
            "equity_score": score.equity_score,
            "property_type": prop.property_type,
            "is_vacant": prop.is_vacant,
        })
    
    prompt = f"""Analyze market gaps in Montgomery, AL for {scenario} businesses.

CURRENT SERVICE DISTRIBUTION:
{json.dumps(service_counts, indent=2)}

UNDERSERVED AREAS (high equity score = few existing services):
{json.dumps(underserved_areas, indent=2)}

Provide a market gap analysis with:
1. **Service Desert Map** - Which neighborhoods lack which services
2. **Top Opportunity Areas** - Where new businesses are most needed
3. **Competitive Landscape** - How saturated each market segment is
4. **Demand Indicators** - Evidence of unmet demand
5. **Investment Priority Ranking** - Ranked list of the best gap-filling opportunities"""

    system_prompt = """You are a market research analyst specializing in urban service gaps.
Provide data-driven analysis of where services are missing in Montgomery, Alabama.
Reference specific neighborhoods and quantify gaps with numbers."""

    llm = get_llm_service()
    analysis = await llm.generate(prompt, system_prompt, temperature=0.5, max_tokens=1500)
    
    now = datetime.now(timezone.utc)
    service_distribution = {
        key: value["count"] for key, value in service_counts.items()
    }
    return {
        "scenario": scenario,
        "analysis": analysis,
        "service_distribution": service_distribution,
        "service_distribution_detail": service_counts,
        "total_properties": len(session.exec(select(Property)).all()),
        "underserved_properties_count": len(underserved_areas),
        "underserved_areas": underserved_areas,
        "generated_at": now.isoformat(),
        "sources": [
            {
                "id": "market-gap-montgomery",
                "label": "Montgomery service location baseline",
                "source_type": "montgomery_open_data",
                "is_live": True,
                "observed_at": now.isoformat(),
                "confidence": 0.88,
                "url": "https://opendata.montgomeryal.gov",
            }
        ],
        "timestamps": {"generated_at": now.isoformat()},
        "confidence": 0.8,
    }


@router.get("/investment-analysis/{property_id}")
async def investment_analysis(
    property_id: int,
    scenario: str = "general",
    session: Session = Depends(get_session),
):
    """AI-powered investment analysis for a specific property."""
    prop = session.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    
    score = session.exec(
        select(PropertyScore).where(
            PropertyScore.property_id == property_id,
            PropertyScore.scenario == scenario,
        )
    ).first()
    
    # Get comparable properties in same neighborhood
    comparables = session.exec(
        select(Property, PropertyScore)
        .join(PropertyScore, Property.id == PropertyScore.property_id)
        .where(Property.neighborhood == prop.neighborhood)
        .where(PropertyScore.scenario == scenario)
        .where(Property.id != property_id)
        .limit(5)
    ).all()
    
    comp_data = []
    for c_prop, c_score in comparables:
        comp_data.append({
            "address": c_prop.address,
            "assessed_value": c_prop.assessed_value,
            "lot_size_sqft": c_prop.lot_size_sqft,
            "overall_score": c_score.overall_score,
        })
    
    prompt = f"""Provide an investment analysis for this Montgomery, AL property:

PROPERTY:
- Address: {prop.address}
- Neighborhood: {prop.neighborhood}
- Type: {prop.property_type}
- Lot Size: {prop.lot_size_sqft} sqft
- Building Size: {prop.building_sqft} sqft
- Assessed Value: {f'${prop.assessed_value:,.2f}' if prop.assessed_value else 'N/A'}
- Year Built: {prop.year_built or 'N/A'}
- Vacant: {prop.is_vacant}

SCORES ({scenario}):
- Overall: {score.overall_score if score else 'N/A'}
- Foot Traffic: {score.foot_traffic_score if score else 'N/A'}
- Competition: {score.competition_score if score else 'N/A'}
- Safety: {score.safety_score if score else 'N/A'}
- Equity: {score.equity_score if score else 'N/A'}

COMPARABLE PROPERTIES IN {prop.neighborhood}:
{json.dumps(comp_data, indent=2)}

Provide:
1. **Investment Summary** - Overall attractiveness rating
2. **Value Assessment** - How it compares to neighborhood comps
3. **Revenue Potential** - Estimated revenue factors for {scenario}
4. **Risk Factors** - What could go wrong
5. **5-Year Outlook** - Expected trajectory
6. **Action Plan** - Step-by-step to maximize return"""

    system_prompt = """You are a commercial real estate investment analyst.
Provide realistic, numbers-based investment analysis for Montgomery, AL properties.
Consider local market conditions, Montgomery's economic development initiatives, and comparable properties."""

    llm = get_llm_service()
    analysis = await llm.generate(prompt, system_prompt, temperature=0.5, max_tokens=1500)
    
    now = datetime.now(timezone.utc)
    return {
        "property_id": property_id,
        "property_address": prop.address,
        "address": prop.address,
        "neighborhood": prop.neighborhood,
        "analysis": analysis,
        "assessed_value": prop.assessed_value,
        "scores": {
            "overall": score.overall_score if score else None,
            "foot_traffic": score.foot_traffic_score if score else None,
            "competition": score.competition_score if score else None,
            "safety": score.safety_score if score else None,
            "equity": score.equity_score if score else None,
        },
        "demographics": None,
        "comparables_count": len(comp_data),
        "generated_at": now.isoformat(),
        "sources": [
            {
                "id": f"investment-{property_id}-montgomery",
                "label": "Montgomery property comparables",
                "source_type": "montgomery_open_data",
                "is_live": True,
                "observed_at": now.isoformat(),
                "confidence": 0.84,
                "url": "https://opendata.montgomeryal.gov",
            }
        ],
        "timestamps": {"generated_at": now.isoformat()},
        "confidence": 0.79,
    }
