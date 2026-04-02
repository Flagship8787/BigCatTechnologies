from app.domains.common.serializers.base_serializer import BaseSerializer
from app.models.post import Post


class PostSerializer(BaseSerializer):
    """Serializes a Post model instance to a JSON-safe dict."""

    def __init__(self, instance: Post):
        super().__init__(instance)

    def to_json(self) -> dict:
        post = self.instance
        return {
            "id": post.id,
            "blog_id": post.blog_id,
            "title": post.title,
            "body": post.body,
            "state": post.state,
            "created_at": post.created_at.isoformat(),
            "updated_at": post.updated_at.isoformat(),
        }
