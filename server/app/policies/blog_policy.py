from sqlalchemy import select

from app.models.blog import Blog
from app.policies.base import BasePolicy, NotAuthorized


class BlogPolicy(BasePolicy):
    FULL_ACCESS = ("admin", "blogs:admin")
    OWN_ACCESS = ("blogs:admin:own",)

    def scope(self, action: str):
        """Return a scoped SELECT for Blog, or raise NotAuthorized.

        - read:   admin / blogs:admin / blogs:admin:own → see all blogs
        - update: admin / blogs:admin → all blogs
                  blogs:admin:own     → only blogs owned by current user
        """
        if action == "read":
            if self.has_permission(*self.FULL_ACCESS, *self.OWN_ACCESS):
                return select(Blog)
        elif action == "update":
            if self.has_permission(*self.FULL_ACCESS):
                return select(Blog)
            if self.has_permission(*self.OWN_ACCESS):
                return select(Blog).where(Blog.owner_id == self.user_id)

        raise NotAuthorized()
