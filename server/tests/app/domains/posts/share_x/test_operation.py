import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.posts.share_x.operation import Operation
from app.models.post import Post
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.conftest import create_post


def _make_tweepy_response(tweet_id: str) -> MagicMock:
    response = MagicMock()
    response.data = {"id": tweet_id}
    return response


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"post": None}
    invalid_fields = ["post"]


class TestDoPerform:
    @pytest.mark.asyncio
    async def test_returns_tweet_id_and_url(self, db_session: AsyncSession):
        post = await create_post(db_session, title="Hello World", body="Some body text")

        mock_client = MagicMock()
        mock_client.create_tweet.return_value = _make_tweepy_response("123456")

        with patch("app.domains.posts.share_x.operation.tweepy.Client", return_value=mock_client):
            with patch.dict("os.environ", {
                "X_API_KEY": "key",
                "X_API_KEY_SECRET": "key_secret",
                "X_ACCESS_TOKEN": "token",
                "X_ACCESS_TOKEN_SECRET": "token_secret",
            }):
                result = await Operation()._do_perform(db_session, post=post)

        assert result["tweet_id"] == "123456"
        assert result["url"] == "https://x.com/i/web/status/123456"

    @pytest.mark.asyncio
    async def test_tweet_text_includes_title(self, db_session: AsyncSession):
        post = await create_post(db_session, title="My Post Title", body="Body content")

        mock_client = MagicMock()
        mock_client.create_tweet.return_value = _make_tweepy_response("1")

        with patch("app.domains.posts.share_x.operation.tweepy.Client", return_value=mock_client):
            with patch.dict("os.environ", {
                "X_API_KEY": "key",
                "X_API_KEY_SECRET": "key_secret",
                "X_ACCESS_TOKEN": "token",
                "X_ACCESS_TOKEN_SECRET": "token_secret",
            }):
                await Operation()._do_perform(db_session, post=post)

        tweet_text = mock_client.create_tweet.call_args[1]["text"]
        assert "My Post Title" in tweet_text

    @pytest.mark.asyncio
    async def test_tweet_text_includes_first_200_chars_of_body(self, db_session: AsyncSession):
        long_body = "A" * 300
        post = await create_post(db_session, title="Title", body=long_body)

        mock_client = MagicMock()
        mock_client.create_tweet.return_value = _make_tweepy_response("1")

        with patch("app.domains.posts.share_x.operation.tweepy.Client", return_value=mock_client):
            with patch.dict("os.environ", {
                "X_API_KEY": "key",
                "X_API_KEY_SECRET": "key_secret",
                "X_ACCESS_TOKEN": "token",
                "X_ACCESS_TOKEN_SECRET": "token_secret",
            }):
                await Operation()._do_perform(db_session, post=post)

        tweet_text = mock_client.create_tweet.call_args[1]["text"]
        assert "A" * 200 in tweet_text
        assert "A" * 201 not in tweet_text

    @pytest.mark.asyncio
    async def test_tweet_text_includes_post_url(self, db_session: AsyncSession):
        post = await create_post(db_session, title="Title", body="Body")

        mock_client = MagicMock()
        mock_client.create_tweet.return_value = _make_tweepy_response("1")

        with patch("app.domains.posts.share_x.operation.tweepy.Client", return_value=mock_client):
            with patch.dict("os.environ", {
                "X_API_KEY": "key",
                "X_API_KEY_SECRET": "key_secret",
                "X_ACCESS_TOKEN": "token",
                "X_ACCESS_TOKEN_SECRET": "token_secret",
            }):
                await Operation()._do_perform(db_session, post=post)

        tweet_text = mock_client.create_tweet.call_args[1]["text"]
        assert f"https://bigcattechnologies.com/blog/posts/{post.id}" in tweet_text

    @pytest.mark.asyncio
    async def test_tweet_text_format(self, db_session: AsyncSession):
        post = await create_post(db_session, title="My Title", body="My body text")

        mock_client = MagicMock()
        mock_client.create_tweet.return_value = _make_tweepy_response("1")

        with patch("app.domains.posts.share_x.operation.tweepy.Client", return_value=mock_client):
            with patch.dict("os.environ", {
                "X_API_KEY": "key",
                "X_API_KEY_SECRET": "key_secret",
                "X_ACCESS_TOKEN": "token",
                "X_ACCESS_TOKEN_SECRET": "token_secret",
            }):
                await Operation()._do_perform(db_session, post=post)

        tweet_text = mock_client.create_tweet.call_args[1]["text"]
        expected = (
            f'"My Title\n\nMy body text\n\n'
            f'https://bigcattechnologies.com/blog/posts/{post.id}"'
        )
        assert tweet_text == expected
