from app.domains.common.operation.base_validator import BaseValidator
from app.models.post import PostState


class Validator(BaseValidator):
    """Validates arguments for the PublishPost operation."""

    def __init__(self, post_id: str, state: str):
        super().__init__()
        self.post_id = post_id
        self.state = state

    def validate(self) -> bool:
        if not self.post_id or not self.post_id.strip():
            self._add_error("post_id", "must not be blank")

        if self.state != PostState.drafted.value:
            self._add_error("state", f"must be '{PostState.drafted.value}' to publish (got '{self.state}')")

        return len(self.errors) == 0
