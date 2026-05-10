import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.token import SessionToken
from app.domains.common.errors import NotAuthorized
from app.models.user import User
from app.policies.user_policy import UserPolicy
from tests.conftest import create_user


def make_policy(sub: str, permissions: list) -> UserPolicy:
    token = SessionToken(sub=sub, permissions=permissions)
    return UserPolicy(token=token)


class TestUserPolicyScopeRead:

    @pytest.mark.asyncio
    async def test_admin_permission_returns_select_user(self, db_session: AsyncSession):
        user = await create_user(db_session)
        policy = make_policy("auth0|admin", ["admin"])
        query = policy.scope("read").where(User.id == user.id)
        result = await db_session.execute(query)
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.id == user.id

    @pytest.mark.asyncio
    async def test_admin_permission_returns_all_users(self, db_session: AsyncSession):
        user_one = await create_user(db_session)
        user_two = await create_user(db_session)
        policy = make_policy("auth0|admin", ["admin"])
        query = policy.scope("read")
        result = await db_session.execute(query)
        ids = {r.id for r in result.scalars().all()}
        assert user_one.id in ids
        assert user_two.id in ids

    @pytest.mark.asyncio
    async def test_no_permissions_raises_not_authorized(self, db_session: AsyncSession):
        policy = make_policy("auth0|user1", [])
        with pytest.raises(NotAuthorized):
            policy.scope("read")

    @pytest.mark.asyncio
    async def test_unrecognized_permission_raises_not_authorized(self, db_session: AsyncSession):
        policy = make_policy("auth0|user1", ["blogs:admin:own"])
        with pytest.raises(NotAuthorized):
            policy.scope("read")

    @pytest.mark.asyncio
    async def test_unrecognized_action_raises_not_authorized(self, db_session: AsyncSession):
        policy = make_policy("auth0|admin", ["admin"])
        with pytest.raises(NotAuthorized):
            policy.scope("delete")
