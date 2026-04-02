import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from app.auth.dependencies import require_auth0_token
from app.auth.token import SessionToken
from app.db import get_db
from app.controllers.admin.blogs import register as register_admin_blogs
from app.models.post import PostState
from tests.conftest import create_blog, create_post


def _make_admin_app(db_session: AsyncSession, scope: str) -> FastAPI:
    test_app = FastAPI()
    register_admin_blogs(test_app)

    async def override_get_db():
        yield db_session

    async def override_require_auth0_token():
        return SessionToken(sub="auth0|test123", scope=scope)

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[require_auth0_token] = override_require_auth0_token
    return test_app


@pytest.fixture
def unauthed_admin_app(db_session: AsyncSession) -> FastAPI:
    """Admin app without auth override — used to test 401 responses."""
    test_app = FastAPI()
    register_admin_blogs(test_app)

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
def no_scope_admin_app(db_session: AsyncSession) -> FastAPI:
    """Admin app with a token that has no recognized scopes."""
    return _make_admin_app(db_session, scope="")


@pytest.fixture
def own_scope_admin_app(db_session: AsyncSession) -> FastAPI:
    """Admin app with blogs:admin:own scope — can read all, update only own blogs."""
    return _make_admin_app(db_session, scope="blogs:admin:own")


@pytest.mark.asyncio
async def test_list_blogs_returns_200(admin_app: FastAPI, db_session: AsyncSession):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/blogs")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_blogs_returns_all_blogs(admin_app: FastAPI, db_session: AsyncSession):
    blog_one = await create_blog(db_session)
    blog_two = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/blogs")

    body = response.json()
    assert len(body) == 2
    names = [b["name"] for b in body]
    assert blog_one.name in names
    assert blog_two.name in names


@pytest.mark.asyncio
async def test_list_blogs_includes_blogs_with_no_published_posts(admin_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/blogs")

    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == blog.name


@pytest.mark.asyncio
async def test_get_blog_returns_200(admin_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/blogs/{blog.id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_blog_returns_all_posts(admin_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    published = await create_post(db_session, blog=blog, state=PostState.published.value)
    drafted = await create_post(db_session, blog=blog, state=PostState.drafted.value)
    deleted = await create_post(db_session, blog=blog, state=PostState.deleted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/blogs/{blog.id}")

    body = response.json()
    assert len(body["posts"]) == 3
    post_ids = {p["id"] for p in body["posts"]}
    assert published.id in post_ids
    assert drafted.id in post_ids
    assert deleted.id in post_ids


@pytest.mark.asyncio
async def test_get_blog_returns_404_for_unknown_id(admin_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/blogs/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_blog_returns_200_and_updates(admin_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)

    with patch("app.controllers.admin.blogs.UpdateOperation") as mock_op_class:
        updated_blog = blog
        updated_blog.name = "Updated Name"
        updated_blog.author_name = "Updated Author"
        mock_instance = mock_op_class.return_value
        mock_instance.perform = AsyncMock(return_value=updated_blog)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=admin_app), base_url="http://test"
        ) as client:
            response = await client.patch(
                f"/admin/blogs/{blog.id}",
                json={"name": "Updated Name", "author_name": "Updated Author"},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Name"
    assert body["author_name"] == "Updated Author"


@pytest.mark.asyncio
async def test_patch_blog_returns_422_for_missing_required_fields(admin_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_app), base_url="http://test"
    ) as client:
        response = await client.patch(
            f"/admin/blogs/{blog.id}",
            json={"description": "no name or author"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_blogs_returns_401_without_auth_token(unauthed_admin_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=unauthed_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/blogs")

    assert response.status_code == 401


# --- Policy tests ---


@pytest.mark.asyncio
async def test_list_blogs_returns_403_without_valid_scope(no_scope_admin_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/blogs")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_blog_returns_403_without_valid_scope(no_scope_admin_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_admin_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/blogs/{blog.id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_patch_blog_returns_403_without_valid_scope(no_scope_admin_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session, owner_id="auth0|test123")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_admin_app), base_url="http://test"
    ) as client:
        response = await client.patch(
            f"/admin/blogs/{blog.id}",
            json={"name": "New Name", "author_name": "Author"},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_blogs_returns_200_with_own_scope(own_scope_admin_app: FastAPI, db_session: AsyncSession):
    await create_blog(db_session)
    await create_blog(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/blogs")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_patch_blog_returns_200_for_own_blog_with_own_scope(
    own_scope_admin_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|test123")

    with patch("app.controllers.admin.blogs.UpdateOperation") as mock_op_class:
        mock_instance = mock_op_class.return_value
        mock_instance.perform = AsyncMock(return_value=blog)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=own_scope_admin_app), base_url="http://test"
        ) as client:
            response = await client.patch(
                f"/admin/blogs/{blog.id}",
                json={"name": "New Name", "author_name": "Author"},
            )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_patch_blog_returns_404_for_unowned_blog_with_own_scope(
    own_scope_admin_app: FastAPI, db_session: AsyncSession
):
    # With scoped queries, an own-scope user patching someone else's blog gets a 404
    # (the blog is filtered out of the query) rather than a 403 — this is intentional:
    # we don't reveal the existence of records the user can't touch.
    blog = await create_blog(db_session, owner_id="auth0|someone-else")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_admin_app), base_url="http://test"
    ) as client:
        response = await client.patch(
            f"/admin/blogs/{blog.id}",
            json={"name": "New Name", "author_name": "Author"},
        )

    assert response.status_code == 404
