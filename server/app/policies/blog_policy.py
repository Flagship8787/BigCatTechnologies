from app.models.blog import Blog
from app.policies.base import BasePolicy, NotAuthorized


class BlogPolicy(BasePolicy):
    FULL_ACCESS = ("admin", "blogs:admin")
    OWN_ACCESS = ("blogs:admin:own",)

    def _can(self, action: str, record: Blog = None) -> bool:
        if action == "read":
            return self.has_scope(*self.FULL_ACCESS, *self.OWN_ACCESS)
        if action == "update":
            if self.has_scope(*self.FULL_ACCESS):
                return True
            if self.has_scope(*self.OWN_ACCESS):
                return record is not None and record.owner_id == self.user_id
        return False

    def scope(self, query):
        if self.has_scope(*self.FULL_ACCESS, *self.OWN_ACCESS):
            return query
        raise NotAuthorized()
