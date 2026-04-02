from app.domains.blogs.create.validator import Validator
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {
        "name": "My Blog",
        "author_name": "Sam Shapiro",
        "owner_id": "auth0|abc123",
        "description": "A blog about things",
    }

    def test_invalid_without_name(self):
        v = Validator(name="", author_name="Sam", owner_id="auth0|abc")
        assert v.validate() is False
        assert "name" in v.errors

    def test_invalid_without_author_name(self):
        v = Validator(name="My Blog", author_name="", owner_id="auth0|abc")
        assert v.validate() is False
        assert "author_name" in v.errors

    def test_invalid_without_owner_id(self):
        v = Validator(name="My Blog", author_name="Sam", owner_id="")
        assert v.validate() is False
        assert "owner_id" in v.errors

    def test_invalid_with_blank_whitespace_name(self):
        v = Validator(name="   ", author_name="Sam", owner_id="auth0|abc")
        assert v.validate() is False
        assert "name" in v.errors

    def test_description_is_optional(self):
        v = Validator(name="My Blog", author_name="Sam", owner_id="auth0|abc")
        assert v.validate() is True

    def test_collects_multiple_errors(self):
        v = Validator(name="", author_name="", owner_id="")
        assert v.validate() is False
        assert "name" in v.errors
        assert "author_name" in v.errors
        assert "owner_id" in v.errors
