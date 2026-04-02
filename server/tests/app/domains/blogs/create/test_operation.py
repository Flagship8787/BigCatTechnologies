import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.blogs.create.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.factories.blog import BlogFactory


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"name": "", "author_name": "", "owner_id": "auth0|abc"}
    invalid_fields = ["name", "author_name"]

    @pytest.mark.asyncio
    async def test_do_perform_creates_blog(self, db_session: AsyncSession):
        data = BlogFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            name=data["name"],
            author_name=data["author_name"],
            owner_id=data["owner_id"],
            description=data["description"],
        )

        assert result["name"] == data["name"]
        assert result["author_name"] == data["author_name"]
        assert result["owner_id"] == data["owner_id"]
        assert result["description"] == data["description"]
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result

    @pytest.mark.asyncio
    async def test_do_perform_persists_to_db(self, db_session: AsyncSession):
        from sqlalchemy import select
        from app.models.blog import Blog

        data = BlogFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            name=data["name"],
            author_name=data["author_name"],
            owner_id=data["owner_id"],
        )

        db_result = await db_session.execute(select(Blog).where(Blog.id == result["id"]))
        blog = db_result.scalar_one_or_none()
        assert blog is not None
        assert blog.name == data["name"]
