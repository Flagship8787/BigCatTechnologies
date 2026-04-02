import uuid
from datetime import datetime, timezone

import factory
from factory import Faker
from factory.alchemy import SQLAlchemyModelFactory

from app.models.blog import Blog


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BlogFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Blog
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(_uuid)
    name = Faker("company")
    description = Faker("sentence")
    author_name = Faker("name")
    owner_id = factory.LazyAttribute(lambda _: f"auth0|{uuid.uuid4().hex[:24]}")
    created_at = factory.LazyFunction(_utcnow)
    updated_at = factory.LazyFunction(_utcnow)
