import uuid
from datetime import datetime, timezone

import factory
from factory import Faker
from factory.alchemy import SQLAlchemyModelFactory

from app.models.blog import Blog
from app.models.post import Post, PostState


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BlogFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Blog
        sqlalchemy_session = None  # set per-test via BlogFactory._meta.sqlalchemy_session
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(_uuid)
    name = Faker("company")
    description = Faker("sentence")
    author_name = Faker("name")
    owner_id = factory.LazyAttribute(lambda _: f"auth0|{uuid.uuid4().hex[:24]}")
    created_at = factory.LazyFunction(_utcnow)
    updated_at = factory.LazyFunction(_utcnow)


class PostFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Post
        sqlalchemy_session = None  # set per-test via PostFactory._meta.sqlalchemy_session
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(_uuid)
    blog = factory.SubFactory(BlogFactory)
    blog_id = factory.LazyAttribute(lambda o: o.blog.id)
    title = Faker("sentence", nb_words=6)
    body = Faker("paragraph")
    state = PostState.drafted.value
    created_at = factory.LazyFunction(_utcnow)
    updated_at = factory.LazyFunction(_utcnow)
