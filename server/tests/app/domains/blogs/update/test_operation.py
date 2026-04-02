import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blog import Blog
from app.domains.blogs.update.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.conftest import create_blog


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"blog_id": "", "name": "New Name", "author_name": "Author"}
    invalid_fields = ["blog_id"]

    @pytest.mark.asyncio
    async def test_do_perform_returns_blog_instance(self, db_session: AsyncSession):
        blog = await create_blog(db_session)

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            name="Updated Name",
            author_name="Updated Author",
        )

        assert isinstance(result, Blog)
        assert result.id == blog.id

    @pytest.mark.asyncio
    async def test_do_perform_updates_name(self, db_session: AsyncSession):
        blog = await create_blog(db_session)

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            name="Updated Name",
            author_name=blog.author_name,
        )

        assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_do_perform_updates_author_name(self, db_session: AsyncSession):
        blog = await create_blog(db_session)

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            name=blog.name,
            author_name="New Author",
        )

        assert result.author_name == "New Author"

    @pytest.mark.asyncio
    async def test_do_perform_updates_description(self, db_session: AsyncSession):
        blog = await create_blog(db_session)

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            name=blog.name,
            author_name=blog.author_name,
            description="New description",
        )

        assert result.description == "New description"
