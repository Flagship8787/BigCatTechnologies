import uuid
from datetime import datetime, timezone

import factory
from factory import Faker

from app.models.blog import Blog
from app.models.post import Post, PostState


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BlogFactory(factory.Factory):
    class Meta:
        model = Blog

    id = factory.LazyFunction(_uuid)
    name = Faker("company")
    description = Faker("sentence")
    author_name = Faker("name")
    owner_id = factory.LazyAttribute(lambda _: f"auth0|{uuid.uuid4().hex[:24]}")
    created_at = factory.LazyFunction(_utcnow)
    updated_at = factory.LazyFunction(_utcnow)


class PostFactory(factory.Factory):
    class Meta:
        model = Post

    id = factory.LazyFunction(_uuid)
    blog_id = factory.LazyFunction(_uuid)
    title = Faker("sentence", nb_words=6)
    body = Faker("paragraph")
    state = PostState.drafted.value
    created_at = factory.LazyFunction(_utcnow)
    updated_at = factory.LazyFunction(_utcnow)
