import factory
from factory import Faker
from factory.alchemy import SQLAlchemyModelFactory

from app.models.post import Post, PostState
from tests.factories.blog import BlogFactory, _uuid, _utcnow


class PostFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Post
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(_uuid)
    blog = factory.SubFactory(BlogFactory)
    blog_id = factory.LazyAttribute(lambda o: o.blog.id)
    title = Faker("sentence", nb_words=6)
    body = Faker("paragraph")
    state = PostState.drafted.value
    created_at = factory.LazyFunction(_utcnow)
    updated_at = factory.LazyFunction(_utcnow)
