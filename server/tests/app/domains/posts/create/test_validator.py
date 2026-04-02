from app.domains.posts.create.validator import Validator
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {"blog_id": "some-id", "title": "My Title", "body": "Some body"}

    def test_invalid_without_blog_id(self):
        v = Validator(blog_id="", title="My Title", body="Some body")
        assert v.validate() is False
        assert "blog_id" in v.errors

    def test_invalid_without_title(self):
        v = Validator(blog_id="some-id", title="", body="Some body")
        assert v.validate() is False
        assert "title" in v.errors

    def test_invalid_without_body(self):
        v = Validator(blog_id="some-id", title="My Title", body="")
        assert v.validate() is False
        assert "body" in v.errors

    def test_invalid_with_blank_whitespace_title(self):
        v = Validator(blog_id="some-id", title="   ", body="Some body")
        assert v.validate() is False
        assert "title" in v.errors

    def test_invalid_with_blank_whitespace_body(self):
        v = Validator(blog_id="some-id", title="My Title", body="   ")
        assert v.validate() is False
        assert "body" in v.errors

    def test_invalid_with_blank_whitespace_blog_id(self):
        v = Validator(blog_id="   ", title="My Title", body="Some body")
        assert v.validate() is False
        assert "blog_id" in v.errors

    def test_collects_multiple_errors(self):
        v = Validator(blog_id="", title="", body="")
        assert v.validate() is False
        assert "blog_id" in v.errors
        assert "title" in v.errors
        assert "body" in v.errors

    def test_errors_contain_messages(self):
        v = Validator(blog_id="", title="", body="Some body")
        v.validate()
        assert len(v.errors["blog_id"]) > 0
        assert len(v.errors["title"]) > 0
