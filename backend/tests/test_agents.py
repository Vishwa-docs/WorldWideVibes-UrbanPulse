"""
Tests for the multi-agent AI system.

Tests the Azure OpenAI-backed LLM service, orchestrator, story generation,
agent API endpoints, and insights endpoints.
All tests use an in-memory SQLite database and mock the LLM service.
"""

import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models.property import Property, PropertyScore, Incident, ServiceLocation
from app.services.llm_service import BaseLLMService, AzureOpenAIService
from tests.conftest import TEST_ENGINE, reset_test_db, get_test_session

# ── Mock LLM service ─────────────────────────────────────────────────────────


class MockLLMService(BaseLLMService):
    """Deterministic mock LLM for testing without real API calls."""

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        lower = prompt.lower()
        if "equity" in lower:
            return (
                "Equity Analysis: This area in Montgomery shows significant service gaps. "
                "The equity score reflects underserved populations. Community impact potential "
                "is high. Recommendation: prioritize accessible services."
            )
        if "risk" in lower or "safety" in lower:
            return (
                "Risk Assessment: Safety conditions in this Montgomery neighborhood are "
                "moderate. Key risk factors include limited lighting infrastructure. "
                "Mitigation: partner with local community watch programs."
            )
        if "business" in lower or "coach" in lower or "market opportunity" in lower:
            return (
                "Business Coaching: The market opportunity in this area of Montgomery is "
                "strong. Foot traffic supports a viable business. Strategic suggestion: "
                "open during peak hours and establish local partnerships."
            )
        if "city tour" in lower or "narrative" in lower:
            return (
                "Montgomery City Tour: Welcome to a journey through Montgomery's most "
                "promising development sites. Each stop reveals unique opportunities "
                "for investment and community growth."
            )
        if "site report" in lower:
            return (
                "Executive Summary: This property presents a strong opportunity. "
                "Location Analysis: Well-positioned in a growing neighborhood. "
                "Market Opportunity: Scores indicate demand. Risk Assessment: Low risk. "
                "Recommendations: Proceed with due diligence."
            )
        if "market gap" in lower:
            return (
                "Market Gap Analysis: Several Montgomery neighborhoods lack essential "
                "services. Downtown has grocery deserts. Capitol Heights needs clinics. "
                "Investment Priority: grocery stores in underserved tracts."
            )
        if "investment" in lower:
            return (
                "Investment Analysis: This property scores well relative to comparables. "
                "Value Assessment: Below neighborhood average assessed value. "
                "5-Year Outlook: Positive trajectory with planned city projects."
            )
        return (
            "UrbanPulse AI Response: Based on the available property data in Montgomery, "
            "here are the top recommendations with scores and analysis. "
            "Next steps: 1) Visit sites 2) Review zoning 3) Contact city planning."
        )


# ── Patch targets for get_llm_service ────────────────────────────────────────

_LLM_PATCHES = [
    "app.services.agents.orchestrator.get_llm_service",
    "app.services.agents.equity_lens.get_llm_service",
    "app.services.agents.risk_lens.get_llm_service",
    "app.services.agents.bizcoach.get_llm_service",
    "app.routes.insights.get_llm_service",
]


def _apply_llm_patches():
    """Return a list of started patchers for all LLM service call-sites."""
    mock = MockLLMService()
    patchers = []
    for target in _LLM_PATCHES:
        p = patch(target, return_value=mock)
        p.start()
        patchers.append(p)
    return patchers


def _stop_patches(patchers):
    for p in patchers:
        p.stop()


# ── Test DB setup ─────────────────────────────────────────────────────────────

client = TestClient(app)


def _reset_db():
    """Drop and recreate all tables for a clean slate."""
    reset_test_db()


def _seed():
    """Seed test properties, scores, incidents, and service locations."""
    _reset_db()
    with Session(TEST_ENGINE) as session:
        p1 = Property(
            parcel_id="AGT-001",
            address="200 Dexter Ave",
            latitude=32.3792,
            longitude=-86.3077,
            property_type="commercial",
            zoning="C-2",
            is_vacant=True,
            is_city_owned=False,
            lot_size_sqft=5000.0,
            building_sqft=3000.0,
            assessed_value=150000.0,
            year_built=1985,
            neighborhood="Downtown",
            council_district="1",
        )
        p2 = Property(
            parcel_id="AGT-002",
            address="450 Court St",
            latitude=32.3750,
            longitude=-86.3100,
            property_type="commercial",
            zoning="C-1",
            is_vacant=False,
            is_city_owned=True,
            lot_size_sqft=8000.0,
            building_sqft=5000.0,
            assessed_value=220000.0,
            year_built=1970,
            neighborhood="Capitol Heights",
            council_district="2",
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

        # Seed a few incidents for nearby-incident queries
        inc = Incident(
            incident_type="theft",
            latitude=32.3795,
            longitude=-86.3080,
            neighborhood="Downtown",
            severity="low",
        )
        session.add(inc)

        # Seed service locations for market-gap queries
        svc = ServiceLocation(
            name="Corner Grocery",
            service_type="grocery",
            latitude=32.3800,
            longitude=-86.3070,
            neighborhood="Downtown",
        )
        session.add(svc)
        session.commit()

        return p1.id, p2.id


# ── LLM service tests ────────────────────────────────────────────────────────


class TestLLMServiceStructure:
    """Verify the LLM service hierarchy and factory behaviour."""

    def test_azure_openai_service_is_subclass_of_base(self):
        assert issubclass(AzureOpenAIService, BaseLLMService)

    def test_mock_llm_service_conforms_to_base(self):
        svc = MockLLMService()
        assert isinstance(svc, BaseLLMService)

    def test_mock_llm_generates_string(self):
        svc = MockLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("What properties are available?")
        )
        assert isinstance(result, str)
        assert len(result) > 20

    def test_mock_llm_equity_response(self):
        svc = MockLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("Analyze equity for this area")
        )
        assert "Equity" in result

    def test_mock_llm_risk_response(self):
        svc = MockLLMService()
        result = asyncio.get_event_loop().run_until_complete(
            svc.generate("What are the safety risks here?")
        )
        assert "Risk" in result or "Safety" in result

    def test_get_llm_service_raises_without_config(self):
        """Without Azure env vars, get_llm_service should raise RuntimeError."""
        from app.services.llm_service import get_llm_service
        from unittest.mock import patch as _patch
        from app.config import Settings

        empty_settings = Settings(
            azure_openai_endpoint="",
            azure_openai_api_key="",
            azure_openai_deployment="",
            azure_openai_api_version="",
        )
        with _patch("app.config.get_settings", return_value=empty_settings):
            with pytest.raises(RuntimeError, match="Azure OpenAI is not configured"):
                get_llm_service()


# ── Orchestrator tests ────────────────────────────────────────────────────────


class TestOrchestrator:
    """Tests for the orchestrator agent (with mocked LLM)."""

    def setup_method(self):
        self._ids = _seed()
        self._patchers = _apply_llm_patches()

    def teardown_method(self):
        _stop_patches(self._patchers)

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

    def test_orchestrator_top_property_has_highest_score(self):
        """The first recommended property should have the highest overall score."""
        from app.services.agents.orchestrator import ask_orchestrator

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                ask_orchestrator(
                    query="Rank properties",
                    persona="city_console",
                    scenario="general",
                    session=session,
                )
            )

        props = result["recommended_properties"]
        if len(props) >= 2 and "score" in props[0] and "score" in props[1]:
            assert props[0]["score"]["overall_score"] >= props[1]["score"]["overall_score"]

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

    def test_lens_equity_has_content(self):
        from app.services.agents.orchestrator import ask_orchestrator

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                ask_orchestrator(
                    query="Analyze equity",
                    persona="city_console",
                    scenario="general",
                    session=session,
                )
            )

        equity = result["lens_outputs"]["equity"]
        assert isinstance(equity, str)
        assert len(equity) > 0

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
    """Tests for the story/city-tour generation (with mocked LLM)."""

    def setup_method(self):
        _seed()
        self._patchers = _apply_llm_patches()

    def teardown_method(self):
        _stop_patches(self._patchers)

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

    def test_generate_story_general_title(self):
        from app.services.agents.orchestrator import generate_story

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                generate_story(
                    scenario="general",
                    persona="city_console",
                    session=session,
                )
            )

        assert "Montgomery" in result["title"]

    def test_generate_story_properties_list(self):
        from app.services.agents.orchestrator import generate_story

        with Session(TEST_ENGINE) as session:
            result = asyncio.get_event_loop().run_until_complete(
                generate_story(
                    scenario="general",
                    persona="city_console",
                    session=session,
                )
            )

        assert isinstance(result["properties"], list)
        assert len(result["properties"]) > 0
        assert "address" in result["properties"][0]


# ── API endpoint tests ────────────────────────────────────────────────────────


class TestAgentAPI:
    """Tests for the agent API endpoints (with mocked LLM)."""

    def setup_method(self):
        _seed()
        self._patchers = _apply_llm_patches()

    def teardown_method(self):
        _stop_patches(self._patchers)

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


# ── Insights endpoint tests ──────────────────────────────────────────────────


class TestInsightsAPI:
    """Tests for /api/insights/* endpoints (with mocked LLM)."""

    def setup_method(self):
        self._ids = _seed()
        self._patchers = _apply_llm_patches()

    def teardown_method(self):
        _stop_patches(self._patchers)

    def test_site_report_returns_200(self):
        pid = self._ids[0]
        resp = client.get(f"/api/insights/site-report/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["property_id"] == pid
        assert "report" in data
        assert isinstance(data["report"], str)
        assert len(data["report"]) > 0
        assert "address" in data
        assert "scores" in data
        assert "nearby_services_count" in data
        assert "nearby_incidents_count" in data

    def test_site_report_not_found(self):
        resp = client.get("/api/insights/site-report/99999")
        assert resp.status_code == 404

    def test_market_gaps_returns_200(self):
        resp = client.get("/api/insights/market-gaps")
        assert resp.status_code == 200
        data = resp.json()
        assert "analysis" in data
        assert isinstance(data["analysis"], str)
        assert "service_distribution" in data
        assert "underserved_properties_count" in data

    def test_market_gaps_with_scenario(self):
        resp = client.get("/api/insights/market-gaps?scenario=general")
        assert resp.status_code == 200
        data = resp.json()
        assert data["scenario"] == "general"

    def test_investment_analysis_returns_200(self):
        pid = self._ids[0]
        resp = client.get(f"/api/insights/investment-analysis/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["property_id"] == pid
        assert "analysis" in data
        assert isinstance(data["analysis"], str)
        assert "address" in data
        assert "scores" in data

    def test_investment_analysis_not_found(self):
        resp = client.get("/api/insights/investment-analysis/99999")
        assert resp.status_code == 404

    def test_investment_analysis_includes_comparables(self):
        pid = self._ids[0]
        resp = client.get(f"/api/insights/investment-analysis/{pid}")
        data = resp.json()
        assert "comparables_count" in data
