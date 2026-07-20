import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_health_check(client: AsyncClient):
    """
    Test that the health check endpoint returns 200 and reports correct states.
    """
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    
    payload = response.json()
    assert "api_status" in payload
    assert payload["api_status"] == "ok"
    assert "postgres_status" in payload
    assert "redis_status" in payload
