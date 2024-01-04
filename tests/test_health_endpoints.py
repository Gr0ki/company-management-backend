"""Contains tests for health endpoints."""
import pytest


@pytest.mark.asyncio
async def test_retrive_app_check_health(ac_client):
    """Tests GET on app's health check endpoint with a successful retrieval."""
    response = await ac_client.get("/api/health/app")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}


@pytest.mark.asyncio
async def test_retrive_psql_check_health(ac_client):
    """Tests GET on psql's health check endpoint with a successful retrieval."""
    response = await ac_client.get("/api/health/psql")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}


@pytest.mark.asyncio
async def test_retrive_redis_check_health(ac_client):
    """Tests GET on Redis's health check endpoint with a successful retrieval."""
    response = await ac_client.get("/api/health/redis")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}
