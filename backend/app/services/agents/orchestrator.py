"""
UrbanPulse Orchestrator Agent.

Now backed by role-aware structured recommendations so answers are
query-specific, explainable, and evidence-linked.
"""

from __future__ import annotations

import json

from sqlmodel import Session

from app.services.llm_service import get_llm_service_safe
from app.services.opportunity_engine import normalize_role, query_recommendations

get_llm_service = get_llm_service_safe

ORCHESTRATOR_SYSTEM = """You are UrbanPulse, a workforce and economic opportunity copilot for Montgomery, Alabama.
You must be concise, practical, and evidence-driven.
Always explain why top recommendations were selected and mention confidence.
"""


def _persona_to_role(persona: str) -> str:
    if persona == "city_console":
        return "city"
    if persona == "entrepreneur":
        return "entrepreneur"
    return normalize_role(persona)


async def ask_orchestrator(
    query: str,
    persona: str,
    scenario: str,
    session: Session,
) -> dict:
    """Run structured recommendation pipeline and return copilot response."""
    role = _persona_to_role(persona)
    bundle = await query_recommendations(
        session=session,
        query=query,
        role=role,
        scenario=scenario,
        limit=5,
        refresh_live=False,
    )

    llm = get_llm_service()
    prompt = f"""User query: {query}
Role: {role}
Scenario: {scenario}

Structured recommendations:
{json.dumps(bundle["recommendations"], indent=2, default=str)}

Evidence:
{json.dumps(bundle["sources"][:8], indent=2, default=str)}

Write:
1) A short answer to the user's question
2) Top 3 recommendations with rationale
3) Two concrete next actions"""

    answer = await llm.generate(
        prompt=prompt,
        system_prompt=ORCHESTRATOR_SYSTEM,
        temperature=0.6,
        max_tokens=1200,
    )

    lens_outputs = {
        "equity": "Equity lens prioritizes underserved zones and service gaps.",
        "risk": "Risk lens balances safety history with implementation feasibility.",
        "bizcoach": "BizCoach lens translates scores into go-to-market actions.",
    }

    recommended_properties = [
        item["property"] for item in bundle["recommendations"][:3]
    ]
    return {
        "answer": answer,
        "recommended_properties": recommended_properties,
        "lens_outputs": lens_outputs,
        "recommendation_id": bundle["recommendation_id"],
        "sources": bundle["sources"],
        "confidence": bundle["confidence"],
    }


async def generate_story(
    scenario: str,
    persona: str,
    session: Session,
) -> dict:
    """Generate a judge-friendly narrative from structured recommendations."""
    role = _persona_to_role(persona)
    bundle = await query_recommendations(
        session=session,
        query="What changed this week in Montgomery opportunities?",
        role=role,
        scenario=scenario,
        limit=5,
        refresh_live=False,
    )
    llm = get_llm_service()
    prompt = f"""Create a guided story mode narrative for judges.
Scenario: {scenario}
Role: {role}
Recommendations:
{json.dumps(bundle["recommendations"], indent=2, default=str)}

Narrative requirements:
- Opening in 2-3 lines with challenge alignment
- 5 short stops (one per recommendation)
- Closing with social impact + commercialization note"""
    narrative = await llm.generate(
        prompt=prompt,
        system_prompt="You are a civic-tech demo narrator for a hackathon judging panel.",
        temperature=0.7,
        max_tokens=1400,
    )
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
        "properties": [r["property"] for r in bundle["recommendations"]],
        "recommendation_id": bundle["recommendation_id"],
        "sources": bundle["sources"],
        "confidence": bundle["confidence"],
    }
