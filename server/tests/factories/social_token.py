import uuid
from datetime import datetime, timezone, timedelta

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.social_token import SocialToken


def _uuid() -> str:
    return str(uuid.uuid4())


def _future_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=1)


class SocialTokenFactory(SQLAlchemyModelFactory):
    class Meta:
        model = SocialToken
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(_uuid)
    user_id = factory.LazyFunction(_uuid)
    provider = "linkedin"
    access_token = factory.LazyFunction(lambda: f"access_{uuid.uuid4().hex}")
    refresh_token = factory.LazyFunction(lambda: f"refresh_{uuid.uuid4().hex}")
    expires_at = factory.LazyFunction(_future_expiry)
    provider_user_id = factory.LazyFunction(lambda: uuid.uuid4().hex[:10])
