import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_blog
from tests.factories import BlogFactory


@pytest.mark.asyncio
async def test_create_blog_returns_201(app: FastAPI):
    payload = BlogFactory.build().__dict__
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/blogs", json={
            "name": payload["name"],
            "description": payload["description"],
            "author_name": payload["author_name"],
            "owner_id": payload["owner_id"],
        })

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_blog_returns_blog_data(app: FastAPI):
    payload = BlogFactory.build().__dict__
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/blogs", json={
            "name": payload["name"],
            "description": payload["description"],
            "author_name": payload["author_name"],
            "owner_id": payload["owner_id"],
        })

    body = response.json()
    assert body["name"] == payload["name"]
    assert body["description"] == payload["description"]
    assert body["author_name"] == payload["author_name"]
    assert body["owner_id"] == payload["owner_id"]
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


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
async def test_get_blog_returns_404_for_unknown_id(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/blogs/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_blog_returns_200(app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/blogs/{blog.id}", json={"name": "New Name"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_blog_changes_name(app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/blogs/{blog.id}", json={"name": "New Name"})

    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_blog_returns_404_for_unknown_id(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch("/blogs/nonexistent-id", json={"name": "New Name"})

    assert response.status_code == 404
