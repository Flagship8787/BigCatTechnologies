import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth0_token
from app.auth.token import SessionToken
from app.db import get_db
from app.controllers.admin.posts import register as register_admin_posts
from app.models.post import PostState
from tests.conftest import create_blog, create_post


def _make_admin_posts_app(db_session: AsyncSession, permissions: list) -> FastAPI:
    test_app = FastAPI()
    register_admin_posts(test_app)

    async def override_get_db():
        yield db_session

    async def override_require_auth0_token():
        return SessionToken(sub="auth0|test123", permissions=permissions)

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[require_auth0_token] = override_require_auth0_token
    return test_app


@pytest.fixture
def unauthed_posts_app(db_session: AsyncSession) -> FastAPI:
    test_app = FastAPI()
    register_admin_posts(test_app)

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
def no_scope_posts_app(db_session: AsyncSession) -> FastAPI:
    return _make_admin_posts_app(db_session, permissions=[])


@pytest.fixture
def admin_posts_app(db_session: AsyncSession) -> FastAPI:
    return _make_admin_posts_app(db_session, permissions=["admin"])


@pytest.fixture
def posts_admin_posts_app(db_session: AsyncSession) -> FastAPI:
    return _make_admin_posts_app(db_session, permissions=["posts:admin"])


@pytest.fixture
def own_scope_posts_app(db_session: AsyncSession) -> FastAPI:
    return _make_admin_posts_app(db_session, permissions=["posts:admin:own"])


# --- Auth tests ---

@pytest.mark.asyncio
async def test_publish_post_returns_401_without_auth_token(unauthed_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=unauthed_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/publish")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_publish_post_returns_403_without_valid_scope(no_scope_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/publish")

    assert response.status_code == 403


# --- Not found ---

@pytest.mark.asyncio
async def test_publish_post_returns_404_for_unknown_post(admin_posts_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post("/admin/posts/nonexistent-id/publish")

    assert response.status_code == 404


# --- State validation ---

@pytest.mark.asyncio
async def test_publish_post_returns_422_when_already_published(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/publish")

    assert response.status_code == 422
    assert response.json()["detail"] == "Post must be in drafted state to publish"


@pytest.mark.asyncio
async def test_publish_post_returns_422_when_deleted(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.deleted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/publish")

    assert response.status_code == 422
    assert response.json()["detail"] == "Post must be in drafted state to publish"


# --- Success cases ---

@pytest.mark.asyncio
async def test_publish_post_returns_200_with_admin_permission(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/publish")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == post.id
    assert body["state"] == PostState.published.value


@pytest.mark.asyncio
async def test_publish_post_returns_200_with_posts_admin_permission(posts_admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=posts_admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/publish")

    assert response.status_code == 200
    assert response.json()["state"] == PostState.published.value


@pytest.mark.asyncio
async def test_publish_post_returns_200_with_own_permission_for_own_blog(
    own_scope_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|test123")
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/publish")

    assert response.status_code == 200
    assert response.json()["state"] == PostState.published.value


@pytest.mark.asyncio
async def test_publish_post_returns_404_with_own_permission_for_other_users_blog(
    own_scope_posts_app: FastAPI, db_session: AsyncSession
):
    # With scoped queries, own-permission user cannot see posts on another user's blog.
    # The post is filtered out of the query → 404 (existence is not revealed).
    blog = await create_blog(db_session, owner_id="auth0|someone-else")
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/publish")

    assert response.status_code == 404
