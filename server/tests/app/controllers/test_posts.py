import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_blog, create_post
from tests.factories import PostFactory


@pytest.mark.asyncio
async def test_create_post_returns_201(app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    payload = PostFactory.build().__dict__

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"/blogs/{blog.id}/posts",
            json={"title": payload["title"], "body": payload["body"]}
        )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_post_returns_post_data(app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    payload = PostFactory.build().__dict__

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"/blogs/{blog.id}/posts",
            json={"title": payload["title"], "body": payload["body"]}
        )

    body = response.json()
    assert body["title"] == payload["title"]
    assert body["body"] == payload["body"]
    assert body["blog_id"] == blog.id
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.asyncio
async def test_create_post_returns_404_for_unknown_blog(app: FastAPI):
    payload = PostFactory.build().__dict__

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/blogs/nonexistent-id/posts",
            json={"title": payload["title"], "body": payload["body"]}
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_post_returns_200(app: FastAPI, db_session: AsyncSession):
    post = await create_post(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/posts/{post.id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_post_returns_post_data(app: FastAPI, db_session: AsyncSession):
    post = await create_post(db_session)

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


@pytest.mark.asyncio
async def test_post_appears_in_blog_detail(app: FastAPI, db_session: AsyncSession):
    post = await create_post(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/blogs/{post.blog_id}")

    body = response.json()
    assert len(body["posts"]) == 1
    assert body["posts"][0]["title"] == post.title
