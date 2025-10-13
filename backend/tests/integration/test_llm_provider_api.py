"""Integration tests for LLM Provider API endpoints.

Uses httpx AsyncClient with FastAPI dependency override pattern to ensure proper
database session isolation between tests. All tests share the test database
session from conftest.py fixture, which handles automatic cleanup via rollback.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_db
from app.main import app


@pytest.mark.asyncio
class TestLLMProviderAPI:
    """Integration tests for /api/llm-providers endpoints."""

    async def test_create_llm_provider(self, db_session):
        """Test POST /api/llm-providers creates a provider."""
        # Override get_db dependency to use test session
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                payload = {
                    "provider_name": "openai",
                    "model_name": "gpt-4",
                    "is_default": False,
                    "api_config": {"temperature": 0.7, "max_tokens": 500},
                }

                response = await client.post("/api/llm-providers/", json=payload)

                assert response.status_code == 201
                data = response.json()
                assert data["provider_name"] == "openai"
                assert data["model_name"] == "gpt-4"
                assert data["is_default"] is False
                assert data["api_config"] == {"temperature": 0.7, "max_tokens": 500}
                assert "id" in data
                assert "created_at" in data
        finally:
            # Clear dependency override after test
            app.dependency_overrides.clear()

    async def test_list_llm_providers(self, db_session):
        """Test GET /api/llm-providers returns list of providers."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Create two providers
                await client.post(
                    "/api/llm-providers/",
                    json={
                        "provider_name": "ollama",
                        "model_name": "qwen2.5:7b-instruct-q4_K_M",
                        "is_default": True,
                    },
                )
                await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "openai", "model_name": "gpt-4", "is_default": False},
                )

                # List all providers
                response = await client.get("/api/llm-providers/")

                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert len(data) == 2
                # Default should be first
                assert data[0]["is_default"] is True
                assert data[0]["provider_name"] == "ollama"
        finally:
            app.dependency_overrides.clear()

    async def test_get_llm_provider_by_id(self, db_session):
        """Test GET /api/llm-providers/{id} returns specific provider."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Create a provider
                create_response = await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "google", "model_name": "gemini-pro"},
                )
                provider_id = create_response.json()["id"]

                # Get by ID
                response = await client.get(f"/api/llm-providers/{provider_id}")

                assert response.status_code == 200
                data = response.json()
                assert data["id"] == provider_id
                assert data["provider_name"] == "google"
                assert data["model_name"] == "gemini-pro"
        finally:
            app.dependency_overrides.clear()

    async def test_get_llm_provider_not_found(self, db_session):
        """Test GET /api/llm-providers/{id} returns 404 when not found."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                fake_id = "00000000-0000-0000-0000-000000000000"
                response = await client.get(f"/api/llm-providers/{fake_id}")

                assert response.status_code == 404
                assert "not found" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    async def test_update_llm_provider(self, db_session):
        """Test PUT /api/llm-providers/{id} updates provider."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Create a provider
                create_response = await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "ollama", "model_name": "llama3", "is_default": True},
                )
                provider_id = create_response.json()["id"]

                # Update the provider
                update_payload = {
                    "model_name": "qwen2.5:7b-instruct-q4_K_M",
                    "api_config": {"api_base": "http://localhost:11435"},
                }
                response = await client.put(
                    f"/api/llm-providers/{provider_id}", json=update_payload
                )

                assert response.status_code == 200
                data = response.json()
                assert data["model_name"] == "qwen2.5:7b-instruct-q4_K_M"
                assert data["api_config"] == {"api_base": "http://localhost:11435"}
        finally:
            app.dependency_overrides.clear()

    async def test_update_prevents_unsetting_last_default(self, db_session):
        """Test PUT attempting to unset last default returns 400 (AC #6)."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Create a default provider
                create_response = await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "ollama", "model_name": "llama3", "is_default": True},
                )
                provider_id = create_response.json()["id"]

                # Attempt to unset the only default
                response = await client.put(
                    f"/api/llm-providers/{provider_id}", json={"is_default": False}
                )

                assert response.status_code == 400
                assert "cannot unset default" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    async def test_set_default_provider(self, db_session):
        """Test PUT /api/llm-providers/{id}/set-default sets provider as default."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Create two providers
                response1 = await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "ollama", "model_name": "llama3", "is_default": True},
                )
                provider1_id = response1.json()["id"]

                response2 = await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "openai", "model_name": "gpt-4", "is_default": False},
                )
                provider2_id = response2.json()["id"]

                # Set provider2 as default
                response = await client.put(f"/api/llm-providers/{provider2_id}/set-default")

                assert response.status_code == 200
                data = response.json()
                assert data["is_default"] is True

                # Verify provider1 is no longer default
                provider1_response = await client.get(f"/api/llm-providers/{provider1_id}")
                assert provider1_response.json()["is_default"] is False
        finally:
            app.dependency_overrides.clear()

    async def test_delete_non_default_provider(self, db_session):
        """Test DELETE /api/llm-providers/{id} deletes non-default provider."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Create default provider first
                await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "ollama", "model_name": "llama3", "is_default": True},
                )

                # Create non-default provider
                create_response = await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "openai", "model_name": "gpt-4", "is_default": False},
                )
                provider_id = create_response.json()["id"]

                # Delete non-default provider
                response = await client.delete(f"/api/llm-providers/{provider_id}")

                assert response.status_code == 204

                # Verify it's gone
                get_response = await client.get(f"/api/llm-providers/{provider_id}")
                assert get_response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    async def test_delete_default_provider_returns_400(self, db_session):
        """Test DELETE of default provider returns 400 error."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Create default provider
                create_response = await client.post(
                    "/api/llm-providers/",
                    json={"provider_name": "ollama", "model_name": "llama3", "is_default": True},
                )
                provider_id = create_response.json()["id"]

                # Attempt to delete default provider
                response = await client.delete(f"/api/llm-providers/{provider_id}")

                assert response.status_code == 400
                assert "cannot delete default" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    async def test_create_provider_with_duplicate_name_and_model_fails(self, db_session):
        """Test creating duplicate (provider_name, model_name) returns 400."""
        app.dependency_overrides[get_db] = lambda: db_session

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                payload = {"provider_name": "ollama", "model_name": "llama3"}

                # Create first provider
                response1 = await client.post("/api/llm-providers/", json=payload)
                assert response1.status_code == 201

                # Attempt to create duplicate
                response2 = await client.post("/api/llm-providers/", json=payload)
                assert response2.status_code == 400
        finally:
            app.dependency_overrides.clear()
