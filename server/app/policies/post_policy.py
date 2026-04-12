from sqlalchemy import select

from app.models.blog import Blog
from app.models.post import Post
from app.policies.base import BasePolicy, NotAuthorized


class PostPolicy(BasePolicy):
    FULL_ACCESS = ("admin", "posts:admin")
    OWN_ACCESS = ("posts:admin:own",)
    TWEET_FULL_ACCESS = ("admin", "posts:admin", "posts:publish:tweet")
    TWEET_OWN_ACCESS = ("posts:publish:tweet:own",)

    def scope(self, action: str):
        if action in ("publish", "get", "update"):
            if self.has_permission(*self.FULL_ACCESS):
                return select(Post)
            if self.has_permission(*self.OWN_ACCESS):
                return select(Post).join(Blog).where(Blog.owner_id == self.user_id)

        if action == "tweet":
            if self.has_permission(*self.TWEET_FULL_ACCESS):
                return select(Post)
            if self.has_permission(*self.TWEET_OWN_ACCESS):
                return select(Post).join(Blog).where(Blog.owner_id == self.user_id)

        raise NotAuthorized()
