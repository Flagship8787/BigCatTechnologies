from app.models.post import Post


def serialize(post: Post) -> dict:
    """Serialize a Post model instance to a JSON-safe dict."""
    return {
        "id": post.id,
        "blog_id": post.blog_id,
        "title": post.title,
        "body": post.body,
        "state": post.state,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }
