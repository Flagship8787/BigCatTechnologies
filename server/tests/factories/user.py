import uuid
from datetime import datetime, timezone

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.user import User


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(_uuid)
    auth0_id = factory.LazyAttribute(lambda _: f"auth0|{uuid.uuid4().hex[:24]}")
    email = factory.LazyAttribute(lambda obj: f"{uuid.uuid4().hex[:8]}@example.com")
    email_verified = False
    name = factory.LazyAttribute(lambda _: "Test User")
    picture = factory.LazyAttribute(lambda _: "https://example.com/pic.jpg")
    created_at = factory.LazyFunction(_utcnow)
    updated_at = factory.LazyFunction(_utcnow)
