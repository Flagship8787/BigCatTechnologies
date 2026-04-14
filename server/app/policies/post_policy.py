from sqlalchemy import select

from app.models.blog import Blog
from app.models.post import Post, PostState
from app.policies.base import BasePolicy, NotAuthorized


class PostPolicy(BasePolicy):
    FULL_ACCESS = ("admin", "posts:admin")
    OWN_ACCESS = ("posts:admin:own",)
    TWEET_FULL_ACCESS = ("admin", "posts:admin", "posts:publish:tweet")
    TWEET_OWN_ACCESS = ("posts:publish:tweet:own",)

    def scope(self, action: str):
        if action in ("publish", "unpublish", "update"):
            if self.has_permission(*self.FULL_ACCESS):
                return select(Post)
            if self.has_permission(*self.OWN_ACCESS):
                return select(Post).join(Blog).where(Blog.owner_id == self.user_id)
            raise NotAuthorized()

        if action == "get":
            if self.has_permission(*self.FULL_ACCESS):
                # Full admin: all posts
                return select(Post)
            if self.has_permission(*self.OWN_ACCESS):
                # Own access: published posts + own drafts
                return select(Post).outerjoin(Blog).where(
                    (Post.state == PostState.published.value) |
                    (Blog.owner_id == self.user_id)
                )
            # No permissions: published posts only (public read)
            return select(Post).where(Post.state == PostState.published.value)

        if action == "tweet":
            if self.has_permission(*self.TWEET_FULL_ACCESS):
                return select(Post)
            if self.has_permission(*self.TWEET_OWN_ACCESS):
                return select(Post).join(Blog).where(Blog.owner_id == self.user_id)
            raise NotAuthorized()

        raise NotAuthorized()
