import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.domains.users.find_or_create.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.factories.user import UserFactory


async def create_user(db: AsyncSession, **kwargs) -> User:
    user = UserFactory.build(**kwargs)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"auth0_id": ""}
    invalid_fields = ["auth0_id"]

    @pytest.mark.asyncio
    async def test_do_perform_creates_new_user_when_not_found(self, db_session: AsyncSession):
        result = await Operation()._do_perform(db_session, auth0_id="auth0|newuser123")

        assert isinstance(result, User)
        assert result.auth0_id == "auth0|newuser123"
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_do_perform_persists_new_user_to_db(self, db_session: AsyncSession):
        result = await Operation()._do_perform(db_session, auth0_id="auth0|newuser456")

        db_result = await db_session.execute(select(User).where(User.id == result.id))
        user = db_result.scalar_one_or_none()
        assert user is not None
        assert user.auth0_id == "auth0|newuser456"

    @pytest.mark.asyncio
    async def test_do_perform_returns_existing_user_when_found(self, db_session: AsyncSession):
        existing = await create_user(db_session, auth0_id="auth0|existing789")

        result = await Operation()._do_perform(db_session, auth0_id="auth0|existing789")

        assert isinstance(result, User)
        assert result.id == existing.id
        assert result.auth0_id == "auth0|existing789"

    @pytest.mark.asyncio
    async def test_do_perform_does_not_duplicate_user(self, db_session: AsyncSession):
        await create_user(db_session, auth0_id="auth0|dedup")

        await Operation()._do_perform(db_session, auth0_id="auth0|dedup")

        db_result = await db_session.execute(select(User).where(User.auth0_id == "auth0|dedup"))
        users = db_result.scalars().all()
        assert len(users) == 1
