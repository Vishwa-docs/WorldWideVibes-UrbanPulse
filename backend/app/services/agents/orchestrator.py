"""
UrbanPulse Orchestrator Agent - the main AI copilot.
Coordinates specialist lens agents and produces unified responses.
"""
from typing import Optional
from sqlmodel import Session, select
from app.models.property import Property, PropertyScore, WebSignal, Incident, ServiceLocation
from app.services.llm_service import get_llm_service
from app.services.agents.equity_lens import analyze_equity
from app.services.agents.risk_lens import analyze_risk
from app.services.agents.bizcoach import coach
from app.services.scoring import get_nearby_incidents, get_nearby_services, haversine_km

ORCHESTRATOR_SYSTEM = """You are UrbanPulse, an AI-powered site-selection copilot for Montgomery, Alabama.
You help city planners and entrepreneurs find the best locations for their projects.
You have access to property data, scoring metrics, web activity signals, and specialist analyses.
Be conversational, data-driven, and actionable. When recommending properties, explain why.
Reference specific scores, neighborhoods, and metrics to back up your recommendations.
Format your response with clear headings and bullet points."""


async def ask_orchestrator(
    query: str,
    persona: str,
    scenario: str,
    session: Session,
) -> dict:
    """
    Main entry: accepts a user query, runs scoring + lens agents,
    and produces a unified response.
    """
    llm = get_llm_service()
    
    # 1. Get top-ranked properties for context
    stmt = (
        select(Property, PropertyScore)
        .join(PropertyScore, Property.id == PropertyScore.property_id, isouter=True)
        .where(PropertyScore.scenario == scenario)
        .order_by(PropertyScore.overall_score.desc())
        .limit(5)
    )
    results = session.exec(stmt).all()
    
    if not results:
        # If no scores exist, get any properties
        props = session.exec(select(Property).limit(5)).all()
        results = [(p, None) for p in props]
    
    # 2. Build property context
    properties_context = []
    recommended_properties = []
    for prop, score in results:
        prop_dict = {
            "id": prop.id,
            "address": prop.address,
            "neighborhood": prop.neighborhood,
            "property_type": prop.property_type,
            "is_vacant": prop.is_vacant,
            "is_city_owned": prop.is_city_owned,
        }
        score_dict = {}
        if score:
            score_dict = {
                "overall_score": score.overall_score,
                "foot_traffic_score": score.foot_traffic_score,
                "competition_score": score.competition_score,
                "safety_score": score.safety_score,
                "equity_score": score.equity_score,
                "activity_index": score.activity_index,
            }
        properties_context.append({**prop_dict, "scores": score_dict})
        
        # Build recommended property response objects
        rec_prop = {
            "id": prop.id,
            "parcel_id": prop.parcel_id,
            "address": prop.address,
            "latitude": prop.latitude,
            "longitude": prop.longitude,
            "property_type": prop.property_type,
            "zoning": prop.zoning,
            "is_vacant": prop.is_vacant,
            "is_city_owned": prop.is_city_owned,
            "lot_size_sqft": prop.lot_size_sqft,
            "building_sqft": prop.building_sqft,
            "assessed_value": prop.assessed_value,
            "year_built": prop.year_built,
            "neighborhood": prop.neighborhood,
            "council_district": prop.council_district,
        }
        if score:
            rec_prop["score"] = score_dict
        recommended_properties.append(rec_prop)
    
    # 3. Run specialist lens agents on top property
    lens_outputs = {}
    if properties_context:
        top_prop = properties_context[0]
        top_scores = top_prop.get("scores", {})
        
        # Get incident count for risk lens
        if results and results[0][0]:
            nearby_incidents = get_nearby_incidents(
                results[0][0].latitude, results[0][0].longitude, 0.5, session
            )
            incidents_count = len(nearby_incidents)
        else:
            incidents_count = 0
        
        try:
            equity_output = await analyze_equity(top_prop, top_scores, scenario)
            lens_outputs["equity"] = equity_output
        except Exception:
            lens_outputs["equity"] = "Equity analysis unavailable."
        
        try:
            risk_output = await analyze_risk(top_prop, top_scores, incidents_count)
            lens_outputs["risk"] = risk_output
        except Exception:
            lens_outputs["risk"] = "Risk analysis unavailable."
        
        try:
            biz_output = await coach(top_prop, top_scores, scenario, persona)
            lens_outputs["bizcoach"] = biz_output
        except Exception:
            lens_outputs["bizcoach"] = "Business coaching unavailable."
    
    # 4. Build orchestrator prompt
    import json
    prompt = f"""User Query: {query}
Persona: {persona}
Scenario: {scenario}

Top Ranked Properties:
{json.dumps(properties_context, indent=2)}

Specialist Agent Outputs:
- Equity Lens: {lens_outputs.get('equity', 'N/A')}
- Risk Lens: {lens_outputs.get('risk', 'N/A')}
- BizCoach: {lens_outputs.get('bizcoach', 'N/A')}

Based on the above data and specialist analyses, provide a comprehensive response to the user's query.
Include specific property recommendations with scores and explain your reasoning.
End with 2-3 actionable next steps."""
    
    answer = await llm.generate(prompt, ORCHESTRATOR_SYSTEM, temperature=0.7, max_tokens=1500)
    
    return {
        "answer": answer,
        "recommended_properties": recommended_properties,
        "lens_outputs": lens_outputs,
    }


async def generate_story(
    scenario: str,
    persona: str,
    session: Session,
) -> dict:
    """Generate a narrative 'city tour' for a scenario."""
    llm = get_llm_service()
    
    # Get top 5 properties for this scenario
    stmt = (
        select(Property, PropertyScore)
        .join(PropertyScore, Property.id == PropertyScore.property_id, isouter=True)
        .where(PropertyScore.scenario == scenario)
        .order_by(PropertyScore.overall_score.desc())
        .limit(5)
    )
    results = session.exec(stmt).all()
    
    if not results:
        props = session.exec(select(Property).limit(5)).all()
        results = [(p, None) for p in props]
    
    properties_data = []
    for prop, score in results:
        p = {
            "id": prop.id,
            "parcel_id": prop.parcel_id,
            "address": prop.address,
            "latitude": prop.latitude,
            "longitude": prop.longitude,
            "property_type": prop.property_type,
            "is_vacant": prop.is_vacant,
            "is_city_owned": prop.is_city_owned,
            "neighborhood": prop.neighborhood,
            "zoning": prop.zoning,
            "lot_size_sqft": prop.lot_size_sqft,
            "assessed_value": prop.assessed_value,
            "year_built": prop.year_built,
        }
        if score:
            p["score"] = {
                "overall_score": score.overall_score,
                "foot_traffic_score": score.foot_traffic_score,
                "competition_score": score.competition_score,
                "safety_score": score.safety_score,
                "equity_score": score.equity_score,
                "activity_index": score.activity_index,
            }
        properties_data.append(p)
    
    import json
    prompt = f"""Create a compelling "City Tour" narrative for Montgomery, AL.
Scenario: {scenario}
Persona: {persona}
Role: {"city planner evaluating development opportunities" if persona == "city_console" else "entrepreneur scouting business locations"}

Properties to feature (in order of score):
{json.dumps(properties_data, indent=2)}

Write a narrative tour that:
1. Opens with a brief introduction about Montgomery and the {scenario} opportunity
2. Visits each property as a "stop" on the tour
3. For each stop, describes the location, its strengths, and the opportunity
4. Closes with a summary recommendation
5. Uses vivid, engaging language that brings each location to life

Format with clear headings for each stop."""
    
    STORY_SYSTEM = """You are a compelling storyteller and urban development expert.
You create engaging narrative tours of cities, highlighting development opportunities.
Your tone is professional but warm, like a knowledgeable local guide.
Use specific details from the data provided to make each location feel real."""
    
    narrative = await llm.generate(prompt, STORY_SYSTEM, temperature=0.8, max_tokens=2000)
    
    scenario_titles = {
        "general": "Montgomery's Hidden Gems",
        "grocery": "Feeding Montgomery: Grocery Store Opportunities",
        "clinic": "Healing Montgomery: Health Clinic Sites",
        "daycare": "Nurturing Montgomery: Daycare Center Locations",
        "coworking": "Connecting Montgomery: Coworking Space Prospects",
    }
    
    return {
        "title": scenario_titles.get(scenario, f"Montgomery {scenario.title()} Opportunities"),
        "narrative": narrative,
        "properties": properties_data,
    }
