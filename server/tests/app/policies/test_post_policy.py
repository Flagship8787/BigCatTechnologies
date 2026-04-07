import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.token import SessionToken
from app.domains.common.errors import NotAuthorized
from app.models.blog import Blog
from app.models.post import Post
from app.policies.post_policy import PostPolicy
from tests.conftest import create_blog, create_post


def make_policy(sub: str, permissions: list) -> PostPolicy:
    token = SessionToken(sub=sub, permissions=permissions)
    return PostPolicy(token=token)


# --- scope("publish") ---

class TestPostPolicyScopePublish:

    @pytest.mark.asyncio
    async def test_admin_permission_returns_select_post(self, db_session: AsyncSession):
        post = await create_post(db_session)
        policy = make_policy("auth0|admin", ["admin"])
        query = policy.scope("publish").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.id == post.id

    @pytest.mark.asyncio
    async def test_posts_admin_permission_returns_select_post(self, db_session: AsyncSession):
        post = await create_post(db_session)
        policy = make_policy("auth0|editor", ["posts:admin"])
        query = policy.scope("publish").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.id == post.id

    @pytest.mark.asyncio
    async def test_own_permission_returns_own_posts(self, db_session: AsyncSession):
        blog = await create_blog(db_session, owner_id="auth0|user1")
        post = await create_post(db_session, blog=blog)
        policy = make_policy("auth0|user1", ["posts:admin:own"])
        query = policy.scope("publish").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.id == post.id

    @pytest.mark.asyncio
    async def test_own_permission_excludes_other_users_posts(self, db_session: AsyncSession):
        blog = await create_blog(db_session, owner_id="auth0|someone-else")
        post = await create_post(db_session, blog=blog)
        policy = make_policy("auth0|user1", ["posts:admin:own"])
        query = policy.scope("publish").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is None

    @pytest.mark.asyncio
    async def test_no_permissions_raises_not_authorized(self, db_session: AsyncSession):
        policy = make_policy("auth0|user1", [])
        with pytest.raises(NotAuthorized):
            policy.scope("publish")

    @pytest.mark.asyncio
    async def test_unrecognized_permission_raises_not_authorized(self, db_session: AsyncSession):
        policy = make_policy("auth0|user1", ["read:only"])
        with pytest.raises(NotAuthorized):
            policy.scope("publish")

    @pytest.mark.asyncio
    async def test_unrecognized_action_raises_not_authorized(self, db_session: AsyncSession):
        policy = make_policy("auth0|admin", ["admin"])
        with pytest.raises(NotAuthorized):
            policy.scope("delete")

    @pytest.mark.asyncio
    async def test_admin_permission_can_see_all_posts_regardless_of_owner(self, db_session: AsyncSession):
        blog = await create_blog(db_session, owner_id="auth0|someone-else")
        post = await create_post(db_session, blog=blog)
        policy = make_policy("auth0|admin", ["admin"])
        query = policy.scope("publish").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is not None

    @pytest.mark.asyncio
    async def test_own_permission_can_see_multiple_own_posts(self, db_session: AsyncSession):
        blog = await create_blog(db_session, owner_id="auth0|user1")
        post_a = await create_post(db_session, blog=blog)
        post_b = await create_post(db_session, blog=blog)
        policy = make_policy("auth0|user1", ["posts:admin:own"])
        query = policy.scope("publish")
        result = await db_session.execute(query)
        ids = {r.id for r in result.scalars().all()}
        assert post_a.id in ids
        assert post_b.id in ids

    @pytest.mark.asyncio
    async def test_own_permission_does_not_return_other_users_posts_in_full_list(self, db_session: AsyncSession):
        own_blog = await create_blog(db_session, owner_id="auth0|user1")
        other_blog = await create_blog(db_session, owner_id="auth0|someone-else")
        own_post = await create_post(db_session, blog=own_blog)
        other_post = await create_post(db_session, blog=other_blog)
        policy = make_policy("auth0|user1", ["posts:admin:own"])
        query = policy.scope("publish")
        result = await db_session.execute(query)
        ids = {r.id for r in result.scalars().all()}
        assert own_post.id in ids
        assert other_post.id not in ids


# --- scope("update") ---

class TestPostPolicyScopeUpdate:

    @pytest.mark.asyncio
    async def test_admin_permission_returns_select_post(self, db_session: AsyncSession):
        post = await create_post(db_session)
        policy = make_policy("auth0|admin", ["admin"])
        query = policy.scope("update").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.id == post.id

    @pytest.mark.asyncio
    async def test_posts_admin_permission_returns_select_post(self, db_session: AsyncSession):
        post = await create_post(db_session)
        policy = make_policy("auth0|editor", ["posts:admin"])
        query = policy.scope("update").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.id == post.id

    @pytest.mark.asyncio
    async def test_own_permission_scopes_to_own_posts(self, db_session: AsyncSession):
        blog = await create_blog(db_session, owner_id="auth0|user1")
        post = await create_post(db_session, blog=blog)
        policy = make_policy("auth0|user1", ["posts:admin:own"])
        query = policy.scope("update").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.id == post.id

    @pytest.mark.asyncio
    async def test_own_permission_excludes_other_users_posts(self, db_session: AsyncSession):
        blog = await create_blog(db_session, owner_id="auth0|someone-else")
        post = await create_post(db_session, blog=blog)
        policy = make_policy("auth0|user1", ["posts:admin:own"])
        query = policy.scope("update").where(Post.id == post.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is None

    @pytest.mark.asyncio
    async def test_no_permissions_raises_not_authorized(self, db_session: AsyncSession):
        policy = make_policy("auth0|user1", [])
        with pytest.raises(NotAuthorized):
            policy.scope("update")

    @pytest.mark.asyncio
    async def test_unrecognized_action_raises_not_authorized(self, db_session: AsyncSession):
        policy = make_policy("auth0|admin", ["admin"])
        with pytest.raises(NotAuthorized):
            policy.scope("delete")
