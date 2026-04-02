import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.blogs.update.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.conftest import create_blog


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"blog_id": "", "name": "New Name"}
    invalid_fields = ["blog_id"]

    @pytest.mark.asyncio
    async def test_do_perform_updates_name(self, db_session: AsyncSession):
        blog = await create_blog(db_session)

        result = await Operation()._do_perform(db_session, blog_id=blog.id, name="Updated Name")

        assert result["id"] == blog.id
        assert result["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_do_perform_updates_description(self, db_session: AsyncSession):
        blog = await create_blog(db_session)

        result = await Operation()._do_perform(db_session, blog_id=blog.id, description="New desc")

        assert result["description"] == "New desc"

    @pytest.mark.asyncio
    async def test_do_perform_updates_author_name(self, db_session: AsyncSession):
        blog = await create_blog(db_session)

        result = await Operation()._do_perform(db_session, blog_id=blog.id, author_name="New Author")

        assert result["author_name"] == "New Author"

    @pytest.mark.asyncio
    async def test_do_perform_does_not_change_unspecified_fields(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        original_name = blog.name

        result = await Operation()._do_perform(db_session, blog_id=blog.id, description="New desc")

        assert result["name"] == original_name

    @pytest.mark.asyncio
    async def test_do_perform_returns_error_for_unknown_blog(self, db_session: AsyncSession):
        result = await Operation()._do_perform(db_session, blog_id="nonexistent-id", name="New Name")

        assert "error" in result
        assert "nonexistent-id" in result["error"]
