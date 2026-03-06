"""
Tests for the multi-agent AI system.

Tests the FallbackLLMService, orchestrator, story generation, and API endpoints.
All tests use an in-memory SQLite database and the fallback (no-API-key) LLM service.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models.property import Property, PropertyScore
from app.services.llm_service import FallbackLLMService, get_llm_service
from tests.conftest import TEST_ENGINE, reset_test_db, get_test_session

# ── Test DB setup ─────────────────────────────────────────────────────────────

client = TestClient(app)


def _reset_db():
    """Drop and recreate all tables for a clean slate."""
    reset_test_db()


def _seed():
    """Seed test properties and scores."""
    _reset_db()
    with Session(TEST_ENGINE) as session:
        p1 = Property(
            parcel_id="AGT-001",
            address="200 Dexter Ave",
            latitude=32.3792,
            longitude=-86.3077,
            property_type="commercial",
            is_vacant=True,
            is_city_owned=False,
            neighborhood="Downtown",
        )
        p2 = Property(
            parcel_id="AGT-002",
            address="450 Court St",
            latitude=32.3750,
            longitude=-86.3100,
            property_type="commercial",
            is_vacant=False,
            is_city_owned=True,
            neighborhood="Capitol Heights",
        )
        session.add(p1)
        session.add(p2)
        session.commit()
        session.refresh(p1)
        session.refresh(p2)

        s1 = PropertyScore(
            property_id=p1.id,
            scenario="general",
            overall_score=8.5,
            foot_traffic_score=9.0,
            competition_score=7.0,
            safety_score=8.0,
            equity_score=9.0,
            activity_index=7.5,
        )
        s2 = PropertyScore(
            property_id=p2.id,
            scenario="general",
            overall_score=7.0,
            foot_traffic_score=6.0,
            competition_score=8.0,
            safety_score=7.0,
            equity_score=8.0,
            activity_index=5.5,
        )
        session.add(s1)
        session.add(s2)
        session.commit()
        return p1.id, p2.id


# ── FallbackLLMService tests ─────────────────────────────────────────────────


class TestFallbackLLMService:
    """Tests for the template-based fallback LLM service."""

    def test_general_response(self):
        svc = FallbackLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("What properties are available?")
        )
        assert isinstance(result, str)
        assert len(result) > 50
        assert "Montgomery" in result

    def test_equity_response(self):
        svc = FallbackLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("Analyze equity for this area")
        )
        assert "Equity" in result
        assert "service" in result.lower()

    def test_risk_response(self):
        svc = FallbackLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("What are the safety risks here?")
        )
        assert "Safety" in result or "Risk" in result

    def test_comparison_response(self):
        svc = FallbackLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("Compare these two properties")
        )
        assert "Comparison" in result or "compare" in result.lower()

    def test_story_response(self):
        svc = FallbackLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("Give me a city tour of Montgomery")
        )
        assert "Tour" in result or "tour" in result.lower()

    def test_bizcoach_response(self):
        svc = FallbackLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("Business coaching for this location")
        )
        assert "Business" in result

    def test_get_llm_service_returns_fallback(self):
        """Without a Gemini API key configured, should return FallbackLLMService."""
        svc = get_llm_service()
        assert isinstance(svc, FallbackLLMService)


# ── Orchestrator tests ────────────────────────────────────────────────────────


class TestOrchestrator:
    """Tests for the orchestrator agent."""

    def setup_method(self):
        _seed()

    def test_ask_orchestrator_returns_expected_keys(self):
        from app.services.agents.orchestrator import ask_orchestrator

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                ask_orchestrator(
                    query="What are the best properties?",
                    persona="city_console",
                    scenario="general",
                    session=session,
                )
            )

        assert isinstance(result, dict)
        assert "answer" in result
        assert "recommended_properties" in result
        assert "lens_outputs" in result
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0

    def test_ask_orchestrator_returns_properties(self):
        from app.services.agents.orchestrator import ask_orchestrator

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                ask_orchestrator(
                    query="Show me commercial properties",
                    persona="entrepreneur",
                    scenario="general",
                    session=session,
                )
            )

        assert len(result["recommended_properties"]) > 0
        prop = result["recommended_properties"][0]
        assert "id" in prop
        assert "address" in prop

    def test_ask_orchestrator_returns_lens_outputs(self):
        from app.services.agents.orchestrator import ask_orchestrator

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                ask_orchestrator(
                    query="Analyze downtown properties",
                    persona="city_console",
                    scenario="general",
                    session=session,
                )
            )

        lens = result["lens_outputs"]
        assert "equity" in lens
        assert "risk" in lens
        assert "bizcoach" in lens

    def test_ask_orchestrator_empty_db(self):
        """Orchestrator should handle empty database gracefully."""
        _reset_db()  # No seed data
        from app.services.agents.orchestrator import ask_orchestrator

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                ask_orchestrator(
                    query="What properties are available?",
                    persona="city_console",
                    scenario="general",
                    session=session,
                )
            )

        assert isinstance(result, dict)
        assert "answer" in result


# ── Story generation tests ────────────────────────────────────────────────────


class TestStoryGeneration:
    """Tests for the story/city-tour generation."""

    def setup_method(self):
        _seed()

    def test_generate_story_returns_expected_keys(self):
        from app.services.agents.orchestrator import generate_story

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                generate_story(
                    scenario="general",
                    persona="city_console",
                    session=session,
                )
            )

        assert isinstance(result, dict)
        assert "title" in result
        assert "narrative" in result
        assert "properties" in result
        assert isinstance(result["title"], str)
        assert isinstance(result["narrative"], str)
        assert len(result["narrative"]) > 0

    def test_generate_story_scenario_title(self):
        from app.services.agents.orchestrator import generate_story

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                generate_story(
                    scenario="grocery",
                    persona="entrepreneur",
                    session=session,
                )
            )

        assert "Grocery" in result["title"] or "grocery" in result["title"].lower()


# ── API endpoint tests ────────────────────────────────────────────────────────


class TestAgentAPI:
    """Tests for the agent API endpoints."""

    def setup_method(self):
        _seed()

    def test_ask_endpoint_returns_200(self):
        response = client.post(
            "/api/agent/ask",
            json={
                "query": "What are the best locations for a grocery store?",
                "persona": "entrepreneur",
                "scenario": "grocery",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "recommended_properties" in data
        assert "lens_outputs" in data

    def test_ask_endpoint_default_params(self):
        response = client.post(
            "/api/agent/ask",
            json={"query": "Show me available properties"},
        )
        assert response.status_code == 200

    def test_story_endpoint_returns_200(self):
        response = client.post(
            "/api/agent/story",
            json={"scenario": "general", "persona": "city_console"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "narrative" in data
        assert "properties" in data

    def test_story_endpoint_default_params(self):
        response = client.post(
            "/api/agent/story",
            json={},
        )
        assert response.status_code == 200
