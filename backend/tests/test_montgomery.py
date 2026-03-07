"""
Tests for Montgomery open data and workforce routes.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_311_endpoint():
    """Test 311 requests endpoint returns expected structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/311", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_most_visited_endpoint():
    """Test most visited locations endpoint."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/most-visited", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_visitor_origin_endpoint():
    """Test visitor origin endpoint."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/visitor-origin", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_business_licenses_endpoint():
    """Test business licenses endpoint."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/business-licenses", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_vacant_properties_endpoint():
    """Test vacant properties endpoint."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/vacant-properties", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_workforce_endpoint():
    """Test workforce data endpoint returns expected structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/workforce")
    assert resp.status_code == 200
    data = resp.json()
    assert "area" in data
    assert "employment" in data
    assert "industries" in data
    assert "source" in data


@pytest.mark.asyncio
async def test_data_sources_endpoint():
    """Test data sources summary endpoint."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/data-sources")
    assert resp.status_code == 200
    data = resp.json()
    assert "sources" in data
    assert "total_sources" in data
    # Should include brightdata source
    assert "brightdata" in data["sources"]
    assert data["sources"]["brightdata"]["available"] is True


@pytest.mark.asyncio
async def test_311_with_category_filter():
    """Test 311 endpoint with category filter."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/311", params={"limit": 5, "category": "Roads"})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_code_violations_endpoint():
    """Test code violations endpoint returns expected structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/code-violations", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_code_violations_with_type_filter():
    """Test code violations endpoint with violation_type filter."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/code-violations", params={"limit": 5, "violation_type": "Overgrown"})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_opportunity_zones_endpoint():
    """Test opportunity zones endpoint returns expected structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/opportunity-zones", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_city_owned_properties_endpoint():
    """Test city-owned properties endpoint returns expected structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/city-owned-properties", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_building_permits_endpoint():
    """Test building permits endpoint returns expected structure."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/building-permits", params={"limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_building_permits_with_type_filter():
    """Test building permits endpoint with permit_type filter."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/montgomery/building-permits", params={"limit": 5, "permit_type": "New Construction"})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
