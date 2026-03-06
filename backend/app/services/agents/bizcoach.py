"""BizCoach Agent - provides business-oriented recommendations."""
from app.services.llm_service import get_llm_service

SYSTEM_PROMPT = """You are the BizCoach Agent for UrbanPulse, a site-selection platform for Montgomery, AL.
Your role is to provide practical, actionable business advice for entrepreneurs considering a location.
Consider: market conditions, competition, customer traffic, operational logistics, and local resources.
Be encouraging but realistic. Reference Montgomery-specific resources when possible.
Keep responses concise (150-200 words)."""

async def coach(property_data: dict, scores: dict, scenario: str, persona: str) -> str:
    llm = get_llm_service()
    prompt = f"""Provide business coaching for this {scenario} opportunity:

Property: {property_data.get('address', 'Unknown')}
Neighborhood: {property_data.get('neighborhood', 'Unknown')}
Overall Score: {scores.get('overall_score', 0)}/10
Foot Traffic: {scores.get('foot_traffic_score', 0)}/10
Competition: {scores.get('competition_score', 0)}/10
Activity Index: {scores.get('activity_index', 0)}/10
Persona: {persona}

Provide business recommendations including:
1. Market opportunity assessment
2. Strategic suggestions (hours, partnerships, marketing)
3. Specific next steps for this scenario"""
    
    return await llm.generate(prompt, SYSTEM_PROMPT, temperature=0.7)
