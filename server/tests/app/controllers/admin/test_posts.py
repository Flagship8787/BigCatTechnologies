import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock, patch

from app.auth.dependencies import require_auth0_token
from app.auth.token import SessionToken
from app.db import get_db
from app.controllers.admin.posts import register as register_admin_posts
from app.models.post import PostState
from tests.conftest import create_blog, create_post


def _make_tweepy_response(tweet_id: str) -> MagicMock:
    response = MagicMock()
    response.data = {"id": tweet_id}
    return response


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


@pytest.fixture
def tweet_full_posts_app(db_session: AsyncSession) -> FastAPI:
    return _make_admin_posts_app(db_session, permissions=["posts:publish:tweet"])


@pytest.fixture
def tweet_own_posts_app(db_session: AsyncSession) -> FastAPI:
    return _make_admin_posts_app(db_session, permissions=["posts:publish:tweet:own"])


# ============================================================
# GET /admin/posts/{post_id}
# ============================================================

# --- Auth / authz ---

@pytest.mark.asyncio
async def test_get_post_returns_401_without_auth_token(unauthed_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=unauthed_posts_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/posts/{post.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_post_returns_404_for_drafted_post_without_valid_scope(no_scope_posts_app: FastAPI, db_session: AsyncSession):
    """Without admin scope, the policy returns only published posts.
    A drafted post is not in scope, so the endpoint returns 404."""
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state="drafted")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/posts/{post.id}")

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_post_returns_published_post_without_valid_scope(no_scope_posts_app: FastAPI, db_session: AsyncSession):
    """Without admin scope, published posts are still readable (public read)."""
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state="published")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/posts/{post.id}")

    assert response.status_code == 200
    assert response.json()["id"] == post.id


# --- Not found ---

@pytest.mark.asyncio
async def test_get_post_returns_404_for_unknown_post(admin_posts_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/posts/nonexistent-id")

    assert response.status_code == 404


# --- Success cases ---

@pytest.mark.asyncio
async def test_get_post_returns_200_with_admin_permission(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/posts/{post.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == post.id
    assert body["state"] == PostState.drafted.value


@pytest.mark.asyncio
async def test_get_post_returns_200_with_posts_admin_permission(posts_admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=posts_admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/posts/{post.id}")

    assert response.status_code == 200
    assert response.json()["id"] == post.id


@pytest.mark.asyncio
async def test_get_post_returns_200_with_own_permission_for_own_blog(
    own_scope_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|test123")
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/posts/{post.id}")

    assert response.status_code == 200
    assert response.json()["id"] == post.id


@pytest.mark.asyncio
async def test_get_post_returns_404_with_own_permission_for_other_users_blog(
    own_scope_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|someone-else")
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.get(f"/admin/posts/{post.id}")

    assert response.status_code == 404


# ============================================================
# POST /admin/posts/{post_id}/publish
# ============================================================

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


# ============================================================
# POST /admin/posts/{post_id}/unpublish
# ============================================================

# --- Auth tests ---

@pytest.mark.asyncio
async def test_unpublish_post_returns_401_without_auth_token(unauthed_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=unauthed_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/unpublish")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unpublish_post_returns_403_without_valid_scope(no_scope_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/unpublish")

    assert response.status_code == 403


# --- Not found ---

@pytest.mark.asyncio
async def test_unpublish_post_returns_404_for_unknown_post(admin_posts_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post("/admin/posts/nonexistent-id/unpublish")

    assert response.status_code == 404


# --- State validation ---

@pytest.mark.asyncio
async def test_unpublish_post_returns_422_when_already_drafted(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/unpublish")

    assert response.status_code == 422
    assert response.json()["detail"] == "Post must be in published state to unpublish"


@pytest.mark.asyncio
async def test_unpublish_post_returns_422_when_deleted(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.deleted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/unpublish")

    assert response.status_code == 422
    assert response.json()["detail"] == "Post must be in published state to unpublish"


# --- Success cases ---

@pytest.mark.asyncio
async def test_unpublish_post_returns_200_with_admin_permission(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/unpublish")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == post.id
    assert body["state"] == PostState.drafted.value


@pytest.mark.asyncio
async def test_unpublish_post_returns_200_with_posts_admin_permission(posts_admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=posts_admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/unpublish")

    assert response.status_code == 200
    assert response.json()["state"] == PostState.drafted.value


@pytest.mark.asyncio
async def test_unpublish_post_returns_200_with_own_permission_for_own_blog(
    own_scope_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|test123")
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/unpublish")

    assert response.status_code == 200
    assert response.json()["state"] == PostState.drafted.value


@pytest.mark.asyncio
async def test_unpublish_post_returns_404_with_own_permission_for_other_users_blog(
    own_scope_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|someone-else")
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/unpublish")

    assert response.status_code == 404


# ============================================================
# PATCH /admin/posts/{post_id}
# ============================================================

# --- Auth / authz ---

@pytest.mark.asyncio
async def test_update_post_returns_401_without_auth_token(unauthed_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=unauthed_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"title": "New Title"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_post_returns_403_without_valid_scope(no_scope_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"title": "New Title"})

    assert response.status_code == 403


# --- Not found ---

@pytest.mark.asyncio
async def test_update_post_returns_404_for_unknown_post(admin_posts_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch("/admin/posts/nonexistent-id", json={"title": "New Title"})

    assert response.status_code == 404


# --- Validation ---

@pytest.mark.asyncio
async def test_update_post_returns_422_for_invalid_state(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"state": "bogus"})

    assert response.status_code == 422


# --- Success cases ---

@pytest.mark.asyncio
async def test_update_post_updates_title(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"title": "Updated Title"})

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_post_updates_body(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"body": "Updated body text."})

    assert response.status_code == 200
    assert response.json()["body"] == "Updated body text."


@pytest.mark.asyncio
async def test_update_post_updates_state(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"state": PostState.published.value})

    assert response.status_code == 200
    assert response.json()["state"] == PostState.published.value


@pytest.mark.asyncio
async def test_update_post_updates_multiple_fields(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(
            f"/admin/posts/{post.id}",
            json={"title": "New Title", "body": "New body.", "state": PostState.published.value},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New Title"
    assert body["body"] == "New body."
    assert body["state"] == PostState.published.value


@pytest.mark.asyncio
async def test_update_post_with_posts_admin_permission(posts_admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=posts_admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"title": "Posts Admin Update"})

    assert response.status_code == 200
    assert response.json()["title"] == "Posts Admin Update"


@pytest.mark.asyncio
async def test_update_post_with_own_permission_for_own_blog(
    own_scope_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|test123")
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"title": "Own Blog Update"})

    assert response.status_code == 200
    assert response.json()["title"] == "Own Blog Update"


@pytest.mark.asyncio
async def test_update_post_returns_404_with_own_permission_for_other_users_blog(
    own_scope_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|someone-else")
    post = await create_post(db_session, blog=blog)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.patch(f"/admin/posts/{post.id}", json={"title": "Should Fail"})

    assert response.status_code == 404


# ============================================================
# POST /admin/posts/{post_id}/tweet
# ============================================================

_TWEEPY_ENV = {
    "X_API_KEY": "key",
    "X_API_KEY_SECRET": "key_secret",
    "X_ACCESS_TOKEN": "token",
    "X_ACCESS_TOKEN_SECRET": "token_secret",
}

# --- Auth / authz ---

@pytest.mark.asyncio
async def test_tweet_post_returns_401_without_auth_token(unauthed_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=unauthed_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_tweet_post_returns_403_without_valid_scope(no_scope_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_tweet_post_returns_403_with_only_own_admin_scope(own_scope_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session, owner_id="auth0|test123")
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=own_scope_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 403


# --- Not found ---

@pytest.mark.asyncio
async def test_tweet_post_returns_404_for_unknown_post(admin_posts_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post("/admin/posts/nonexistent-id/tweet")

    assert response.status_code == 404


# --- State validation ---

@pytest.mark.asyncio
async def test_tweet_post_returns_422_when_post_is_not_published(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.drafted.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 422
    assert post.id in response.json()["detail"]
    assert PostState.drafted.value in response.json()["detail"]


# --- Success cases ---

@pytest.mark.asyncio
async def test_tweet_post_returns_200_with_admin_permission(admin_posts_app: FastAPI, db_session: AsyncSession):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    mock_client = MagicMock()
    mock_client.create_tweet.return_value = _make_tweepy_response("111")

    with patch("app.domains.posts.tweet.operation.tweepy.Client", return_value=mock_client):
        with patch.dict("os.environ", _TWEEPY_ENV):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
            ) as client:
                response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 200
    body = response.json()
    assert body["tweet_id"] == "111"
    assert "x.com" in body["url"]


@pytest.mark.asyncio
async def test_tweet_post_returns_200_with_posts_publish_tweet_permission(
    tweet_full_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    mock_client = MagicMock()
    mock_client.create_tweet.return_value = _make_tweepy_response("222")

    with patch("app.domains.posts.tweet.operation.tweepy.Client", return_value=mock_client):
        with patch.dict("os.environ", _TWEEPY_ENV):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=tweet_full_posts_app), base_url="http://test"
            ) as client:
                response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 200
    assert response.json()["tweet_id"] == "222"


@pytest.mark.asyncio
async def test_tweet_post_returns_200_with_own_permission_for_own_blog(
    tweet_own_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|test123")
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    mock_client = MagicMock()
    mock_client.create_tweet.return_value = _make_tweepy_response("333")

    with patch("app.domains.posts.tweet.operation.tweepy.Client", return_value=mock_client):
        with patch.dict("os.environ", _TWEEPY_ENV):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=tweet_own_posts_app), base_url="http://test"
            ) as client:
                response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 200
    assert response.json()["tweet_id"] == "333"


@pytest.mark.asyncio
async def test_tweet_post_returns_404_with_own_permission_for_other_users_blog(
    tweet_own_posts_app: FastAPI, db_session: AsyncSession
):
    blog = await create_blog(db_session, owner_id="auth0|someone-else")
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=tweet_own_posts_app), base_url="http://test"
    ) as client:
        response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tweet_post_returns_502_when_tweepy_fails(admin_posts_app: FastAPI, db_session: AsyncSession):
    import tweepy

    blog = await create_blog(db_session)
    post = await create_post(db_session, blog=blog, state=PostState.published.value)

    mock_client = MagicMock()
    mock_client.create_tweet.side_effect = tweepy.TweepyException("API error")

    with patch("app.domains.posts.tweet.operation.tweepy.Client", return_value=mock_client):
        with patch.dict("os.environ", _TWEEPY_ENV):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=admin_posts_app), base_url="http://test"
            ) as client:
                response = await client.post(f"/admin/posts/{post.id}/tweet")

    assert response.status_code == 502
