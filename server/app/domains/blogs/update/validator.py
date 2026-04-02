from app.domains.common.operation.base_validator import BaseValidator


class Validator(BaseValidator):
    """Validates arguments for the UpdateBlog operation."""

    def __init__(self, blog_id: str, name: str | None = None, description: str | None = None, author_name: str | None = None):
        super().__init__()
        self.blog_id = blog_id
        self.name = name
        self.description = description
        self.author_name = author_name

    def validate(self) -> bool:
        if not self.blog_id or not self.blog_id.strip():
            self._add_error("blog_id", "must not be blank")

        if self.name is not None and not self.name.strip():
            self._add_error("name", "must not be blank if provided")

        if self.author_name is not None and not self.author_name.strip():
            self._add_error("author_name", "must not be blank if provided")

        return len(self.errors) == 0
