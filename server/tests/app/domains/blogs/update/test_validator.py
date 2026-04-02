from app.domains.blogs.update.validator import Validator
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {"blog_id": "some-id", "name": "New Name"}

    def test_invalid_without_blog_id(self):
        v = Validator(blog_id="", name="New Name")
        assert v.validate() is False
        assert "blog_id" in v.errors

    def test_invalid_with_blank_name_when_provided(self):
        v = Validator(blog_id="some-id", name="")
        assert v.validate() is False
        assert "name" in v.errors

    def test_invalid_with_blank_author_name_when_provided(self):
        v = Validator(blog_id="some-id", author_name="")
        assert v.validate() is False
        assert "author_name" in v.errors

    def test_valid_with_only_blog_id(self):
        """All optional fields can be omitted."""
        v = Validator(blog_id="some-id")
        assert v.validate() is True

    def test_valid_with_none_fields(self):
        """None means 'not updating this field' — not a blank string."""
        v = Validator(blog_id="some-id", name=None, description=None, author_name=None)
        assert v.validate() is True

    def test_valid_updating_description_to_empty_string(self):
        """Description may be set to empty string (clearing it is valid)."""
        v = Validator(blog_id="some-id", description="")
        assert v.validate() is True
