import os

import tweepy
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.posts.share_x.validator import Validator
from app.models.post import Post


class Operation(BaseOperation):
    """Shares a post to X (Twitter) by posting a tweet with the post title, excerpt, and link."""

    def _validator(self, post: Post) -> BaseValidator:
        return Validator(post=post)

    async def _do_perform(self, db: AsyncSession, post: Post) -> dict:
        tweet_text = (
            f'"{post.title}\n\n{post.body[:200]}\n\n'
            f'https://bigcattechnologies.com/blog/posts/{post.id}"'
        )

        client = tweepy.Client(
            consumer_key=os.environ["X_API_KEY"],
            consumer_secret=os.environ["X_API_KEY_SECRET"],
            access_token=os.environ["X_ACCESS_TOKEN"],
            access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
        )
        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data["id"]

        return {
            "tweet_id": tweet_id,
            "url": f"https://x.com/i/web/status/{tweet_id}",
        }
