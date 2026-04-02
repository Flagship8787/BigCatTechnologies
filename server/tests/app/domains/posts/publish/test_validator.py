from app.domains.posts.publish.validator import Validator
from app.models.post import PostState
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {"post_id": "some-id", "state": PostState.drafted.value}

    def test_invalid_without_post_id(self):
        v = Validator(post_id="", state=PostState.drafted.value)
        assert v.validate() is False
        assert "post_id" in v.errors

    def test_invalid_when_state_is_published(self):
        v = Validator(post_id="some-id", state=PostState.published.value)
        assert v.validate() is False
        assert "state" in v.errors

    def test_invalid_when_state_is_deleted(self):
        v = Validator(post_id="some-id", state=PostState.deleted.value)
        assert v.validate() is False
        assert "state" in v.errors

    def test_invalid_when_state_is_unknown(self):
        v = Validator(post_id="some-id", state="some_unknown_state")
        assert v.validate() is False
        assert "state" in v.errors

    def test_error_message_mentions_required_state(self):
        v = Validator(post_id="some-id", state=PostState.published.value)
        v.validate()
        assert any(PostState.drafted.value in msg for msg in v.errors["state"])

    def test_collects_multiple_errors(self):
        v = Validator(post_id="", state=PostState.published.value)
        assert v.validate() is False
        assert "post_id" in v.errors
        assert "state" in v.errors
