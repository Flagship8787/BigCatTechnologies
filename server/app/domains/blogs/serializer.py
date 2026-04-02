from app.domains.common.serializers.base_serializer import BaseSerializer
from app.domains.posts.serializer import PostSerializer
from app.models.blog import Blog
from app.models.post import PostState


class BlogSerializer(BaseSerializer):
    """Serializes a Blog model instance to a JSON-safe dict.

    Args:
        instance: The Blog model instance to serialize.

    to_json kwargs:
        published_only (bool): If True, only include posts with state=published.
                               Defaults to False (include all posts).
    """

    def __init__(self, instance: Blog):
        super().__init__(instance)

    def to_json(self, published_only: bool = False) -> dict:
        blog = self.instance
        data = {
            "id": blog.id,
            "name": blog.name,
            "description": blog.description,
            "author_name": blog.author_name,
            "owner_id": blog.owner_id,
            "created_at": blog.created_at.isoformat(),
            "updated_at": blog.updated_at.isoformat(),
        }

        if hasattr(blog, "posts"):
            posts = blog.posts
            if published_only:
                posts = [p for p in posts if p.state == PostState.published.value]
            data["posts"] = [PostSerializer(p).to_json() for p in posts]

        return data
