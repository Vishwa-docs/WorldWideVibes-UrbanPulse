"""AI Agent endpoints for UrbanPulse copilot."""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_session
from app.services.agents.orchestrator import ask_orchestrator, generate_story

router = APIRouter(prefix="/api/agent", tags=["agent"])


class AgentQueryRequest(BaseModel):
    query: str
    persona: str = "city_console"
    scenario: str = "general"


class StoryRequest(BaseModel):
    scenario: str = "general"
    persona: str = "city_console"


@router.post("/ask")
async def ask_agent(request: AgentQueryRequest, session: Session = Depends(get_session)):
    """Ask the UrbanPulse AI copilot a question."""
    result = await ask_orchestrator(
        query=request.query,
        persona=request.persona,
        scenario=request.scenario,
        session=session,
    )
    return result


@router.post("/story")
async def get_story(request: StoryRequest, session: Session = Depends(get_session)):
    """Generate a narrative city tour for a scenario."""
    result = await generate_story(
        scenario=request.scenario,
        persona=request.persona,
        session=session,
    )
    return result
