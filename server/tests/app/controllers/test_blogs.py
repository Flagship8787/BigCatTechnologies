import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import PostState
from tests.conftest import create_blog, create_post


@pytest.mark.asyncio
async def test_list_blogs_returns_200(app: FastAPI, db_session: AsyncSession):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/blogs")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_blogs_returns_created_blogs(app: FastAPI, db_session: AsyncSession):
    blog_one = await create_blog(db_session)
    blog_two = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/blogs")

    body = response.json()
    assert len(body) == 2
    names = [b["name"] for b in body]
    assert blog_one.name in names
    assert blog_two.name in names


@pytest.mark.asyncio
async def test_get_blog_returns_200(app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/blogs/{blog.id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_blog_returns_blog_with_posts(app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/blogs/{blog.id}")

    body = response.json()
    assert body["id"] == blog.id
    assert "posts" in body
    assert isinstance(body["posts"], list)


@pytest.mark.asyncio
async def test_get_blog_only_returns_published_posts(app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    published = await create_post(db_session, blog=blog, state=PostState.published.value)
    await create_post(db_session, blog=blog, state=PostState.drafted.value)
    await create_post(db_session, blog=blog, state=PostState.deleted.value)
    # Expire blog so the handler re-fetches with selectinload
    await db_session.refresh(blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/blogs/{blog.id}")

    body = response.json()
    assert len(body["posts"]) == 1
    assert body["posts"][0]["id"] == published.id


@pytest.mark.asyncio
async def test_get_blog_returns_404_for_unknown_id(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/blogs/nonexistent-id")

    assert response.status_code == 404
