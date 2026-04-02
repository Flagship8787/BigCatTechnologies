import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import PostState
from tests.conftest import create_post


@pytest.mark.asyncio
async def test_get_post_returns_200_for_published_post(app: FastAPI, db_session: AsyncSession):
    post = await create_post(db_session, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/posts/{post.id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_post_returns_404_for_drafted_post(app: FastAPI, db_session: AsyncSession):
    post = await create_post(db_session, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/posts/{post.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_post_returns_404_for_deleted_post(app: FastAPI, db_session: AsyncSession):
    post = await create_post(db_session, state=PostState.deleted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/posts/{post.id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_post_returns_post_data(app: FastAPI, db_session: AsyncSession):
    post = await create_post(db_session, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/posts/{post.id}")

    body = response.json()
    assert body["id"] == post.id
    assert body["blog_id"] == post.blog_id
    assert body["title"] == post.title
    assert body["body"] == post.body
    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.asyncio
async def test_get_post_returns_404_for_unknown_id(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/posts/nonexistent-post-id")

    assert response.status_code == 404
