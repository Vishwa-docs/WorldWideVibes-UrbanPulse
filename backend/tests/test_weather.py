"""
Tests for Weather API endpoints (Open-Meteo integration).
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_current_weather_endpoint():
    """Test current weather endpoint returns expected structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/weather/current")
    assert resp.status_code == 200
    data = resp.json()
    assert "temperature_f" in data
    assert "humidity_pct" in data
    assert "wind_speed_mph" in data
    assert "weather_description" in data
    assert "source" in data


@pytest.mark.asyncio
async def test_weather_forecast_endpoint():
    """Test weather forecast endpoint returns expected structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/weather/forecast")
    assert resp.status_code == 200
    data = resp.json()
    assert "location" in data
    assert "forecast" in data
    assert isinstance(data["forecast"], list)
    assert "source" in data


@pytest.mark.asyncio
async def test_forecast_has_daily_fields():
    """Test each forecast day has required fields."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/weather/forecast")
    assert resp.status_code == 200
    data = resp.json()
    if data["forecast"]:
        day = data["forecast"][0]
        assert "date" in day
        assert "high_f" in day
        assert "low_f" in day
        assert "weather_description" in day
