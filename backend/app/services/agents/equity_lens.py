"""Equity Lens Agent - analyzes equity and service gap dimensions."""
from app.services.llm_service import get_llm_service

SYSTEM_PROMPT = """You are the Equity Lens Agent for UrbanPulse, a site-selection platform for Montgomery, AL.
Your role is to analyze properties through an equity and social impact lens.
Consider: service gaps, demographics, underserved communities, accessibility, and community benefit.
Be specific, data-driven, and actionable. Reference Montgomery neighborhoods by name when possible.
Keep responses concise (150-200 words)."""

async def analyze_equity(property_data: dict, scores: dict, scenario: str) -> str:
    llm = get_llm_service()
    prompt = f"""Analyze the equity impact of this property for a {scenario} use case:

Property: {property_data.get('address', 'Unknown')}
Neighborhood: {property_data.get('neighborhood', 'Unknown')}
Equity Score: {scores.get('equity_score', 0)}/10
Safety Score: {scores.get('safety_score', 0)}/10
Nearby Services: {property_data.get('nearby_services_count', 'Unknown')}
Is Vacant: {property_data.get('is_vacant', False)}

Provide an equity assessment including:
1. Service gap analysis for this area
2. Community impact potential
3. Equity-specific recommendation"""
    
    return await llm.generate(prompt, SYSTEM_PROMPT, temperature=0.6)
