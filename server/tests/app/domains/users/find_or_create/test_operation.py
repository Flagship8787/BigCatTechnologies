import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.domains.users.find_or_create.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.factories.user import UserFactory

MOCK_ACCESS_TOKEN = "mock.access.token"

MOCK_PROFILE = {
    "email": "test@example.com",
    "email_verified": True,
    "name": "Test User",
    "picture": "https://example.com/pic.jpg",
}


async def create_user(db: AsyncSession, **kwargs) -> User:
    user = UserFactory.build(**kwargs)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"auth0_id": "", "access_token": MOCK_ACCESS_TOKEN}
    invalid_fields = ["auth0_id"]

    @pytest.mark.asyncio
    async def test_do_perform_creates_new_user_when_not_found(self, db_session: AsyncSession):
        with patch("app.domains.users.find_or_create.operation.AuthService") as MockAuthService:
            MockAuthService.return_value.get_userinfo = AsyncMock(return_value=MOCK_PROFILE)
            result = await Operation()._do_perform(db_session, auth0_id="auth0|newuser123", access_token=MOCK_ACCESS_TOKEN)

        assert isinstance(result, User)
        assert result.auth0_id == "auth0|newuser123"
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_do_perform_persists_new_user_to_db(self, db_session: AsyncSession):
        with patch("app.domains.users.find_or_create.operation.AuthService") as MockAuthService:
            MockAuthService.return_value.get_userinfo = AsyncMock(return_value=MOCK_PROFILE)
            result = await Operation()._do_perform(db_session, auth0_id="auth0|newuser456", access_token=MOCK_ACCESS_TOKEN)

        db_result = await db_session.execute(select(User).where(User.id == result.id))
        user = db_result.scalar_one_or_none()
        assert user is not None
        assert user.auth0_id == "auth0|newuser456"

    @pytest.mark.asyncio
    async def test_do_perform_returns_existing_user_when_found(self, db_session: AsyncSession):
        existing = await create_user(db_session, auth0_id="auth0|existing789")

        with patch("app.domains.users.find_or_create.operation.AuthService") as MockAuthService:
            MockAuthService.return_value.get_userinfo = AsyncMock(return_value=MOCK_PROFILE)
            result = await Operation()._do_perform(db_session, auth0_id="auth0|existing789", access_token=MOCK_ACCESS_TOKEN)

        assert isinstance(result, User)
        assert result.id == existing.id
        assert result.auth0_id == "auth0|existing789"

    @pytest.mark.asyncio
    async def test_do_perform_does_not_duplicate_user(self, db_session: AsyncSession):
        await create_user(db_session, auth0_id="auth0|dedup")

        with patch("app.domains.users.find_or_create.operation.AuthService") as MockAuthService:
            MockAuthService.return_value.get_userinfo = AsyncMock(return_value=MOCK_PROFILE)
            await Operation()._do_perform(db_session, auth0_id="auth0|dedup", access_token=MOCK_ACCESS_TOKEN)

        db_result = await db_session.execute(select(User).where(User.auth0_id == "auth0|dedup"))
        users = db_result.scalars().all()
        assert len(users) == 1

    @pytest.mark.asyncio
    async def test_creates_user_with_profile_fields(self, db_session: AsyncSession):
        with patch("app.domains.users.find_or_create.operation.AuthService") as MockAuthService:
            MockAuthService.return_value.get_userinfo = AsyncMock(return_value=MOCK_PROFILE)
            result = await Operation()._do_perform(db_session, auth0_id="auth0|profiletest", access_token=MOCK_ACCESS_TOKEN)

        assert result.email == "test@example.com"
        assert result.email_verified is True
        assert result.name == "Test User"
        assert result.picture == "https://example.com/pic.jpg"

    @pytest.mark.asyncio
    async def test_updates_profile_on_existing_user(self, db_session: AsyncSession):
        existing = await create_user(
            db_session,
            auth0_id="auth0|updatetest",
            email="old@example.com",
            email_verified=False,
            name="Old Name",
            picture="https://example.com/old.jpg",
        )

        updated_profile = {
            "email": "new@example.com",
            "email_verified": True,
            "name": "New Name",
            "picture": "https://example.com/new.jpg",
        }

        with patch("app.domains.users.find_or_create.operation.AuthService") as MockAuthService:
            MockAuthService.return_value.get_userinfo = AsyncMock(return_value=updated_profile)
            result = await Operation()._do_perform(db_session, auth0_id="auth0|updatetest", access_token=MOCK_ACCESS_TOKEN)

        assert result.id == existing.id
        assert result.email == "new@example.com"
        assert result.email_verified is True
        assert result.name == "New Name"
        assert result.picture == "https://example.com/new.jpg"
