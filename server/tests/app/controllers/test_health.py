import pytest
import httpx
from fastapi import FastAPI

from app.controllers.health import register


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    register(app)
    return app


@pytest.mark.asyncio
async def test_health_returns_200(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_ok_body(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_content_type_is_json(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert "application/json" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_health_disallows_post(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/health")

    assert response.status_code == 405


@pytest.mark.asyncio
async def test_health_status_value_is_string(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    body = response.json()
    assert isinstance(body.get("status"), str)
