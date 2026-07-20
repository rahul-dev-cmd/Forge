import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_auth_missing_header(client: AsyncClient):
    """
    Assert requesting protected routes without credentials returns 403 or 401.
    """
    response = await client.get("/api/v1/users/me")
    assert response.status_code in [401, 403]

async def test_auth_mock_token_success(client: AsyncClient):
    """
    Assert requesting with a mock token successfully creates/logs-in the user.
    """
    headers = {"Authorization": "Bearer mock-token-rahuldev"}
    response = await client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    
    payload = response.json()
    assert payload["email"] == "rahuldev@forge.com"
    assert payload["username"] == "rahuldev"
    assert payload["full_name"] == "Rahul Dev"
    assert payload["clerk_id"] == "clerk-mock-rahuldev"

async def test_settings_retrieval_success(client: AsyncClient):
    """
    Assert user settings are initialized and fetched successfully when authenticated.
    """
    headers = {"Authorization": "Bearer mock-token-johndoe"}
    response = await client.get("/api/v1/users/me/settings", headers=headers)
    assert response.status_code == 200
    
    settings_payload = response.json()
    assert settings_payload["theme"] == "system"
    assert settings_payload["language"] == "en"
