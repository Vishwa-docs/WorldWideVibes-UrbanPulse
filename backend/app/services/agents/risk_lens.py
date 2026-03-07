"""Risk & Safety Lens Agent - analyzes safety and risk factors."""
from app.services.llm_service import get_llm_service_safe

get_llm_service = get_llm_service_safe

SYSTEM_PROMPT = """You are the Risk & Safety Lens Agent for UrbanPulse, a site-selection platform for Montgomery, AL.
Your role is to assess safety conditions and risk factors for potential business locations.
Consider: incident history, crime patterns, infrastructure condition, and environmental factors.
Be balanced — acknowledge risks but also note positive trends and mitigation options.
Keep responses concise (150-200 words)."""

async def analyze_risk(property_data: dict, scores: dict, incidents_count: int) -> str:
    llm = get_llm_service()
    prompt = f"""Assess the risk and safety profile of this property:

Property: {property_data.get('address', 'Unknown')}
Neighborhood: {property_data.get('neighborhood', 'Unknown')}
Safety Score: {scores.get('safety_score', 0)}/10
Nearby Incidents (0.5km radius): {incidents_count}
Property Type: {property_data.get('property_type', 'Unknown')}

Provide a risk assessment including:
1. Safety overview for this area
2. Key risk factors and caveats
3. Mitigation suggestions"""
    
    return await llm.generate(prompt, SYSTEM_PROMPT, temperature=0.5)
