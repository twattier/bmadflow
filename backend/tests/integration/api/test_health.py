"""Integration tests for health check endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test health check endpoint returns 200 OK with correct structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_check_database_field():
    """Test health check includes database connectivity status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    # Database field should exist and indicate status
    assert "database" in data
    assert isinstance(data["database"], str)
    # Accept either "connected" or error message
    assert len(data["database"]) > 0
