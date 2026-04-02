from app.domains.blogs.update.validator import Validator
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {
        "blog_id": "some-id",
        "name": "New Name",
        "author_name": "New Author",
    }

    def test_invalid_without_blog_id(self):
        v = Validator(blog_id="", name="New Name", author_name="Author")
        assert v.validate() is False
        assert "blog_id" in v.errors

    def test_invalid_without_name(self):
        v = Validator(blog_id="some-id", name="", author_name="Author")
        assert v.validate() is False
        assert "name" in v.errors

    def test_invalid_without_author_name(self):
        v = Validator(blog_id="some-id", name="New Name", author_name="")
        assert v.validate() is False
        assert "author_name" in v.errors

    def test_invalid_with_blank_whitespace_name(self):
        v = Validator(blog_id="some-id", name="   ", author_name="Author")
        assert v.validate() is False
        assert "name" in v.errors

    def test_description_is_optional(self):
        v = Validator(blog_id="some-id", name="Name", author_name="Author")
        assert v.validate() is True

    def test_description_may_be_empty_string(self):
        v = Validator(blog_id="some-id", name="Name", author_name="Author", description="")
        assert v.validate() is True

    def test_collects_multiple_errors(self):
        v = Validator(blog_id="", name="", author_name="")
        assert v.validate() is False
        assert "blog_id" in v.errors
        assert "name" in v.errors
        assert "author_name" in v.errors
