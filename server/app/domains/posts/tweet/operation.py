import logging
import os
import uuid

import tweepy
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.posts.tweet.errors import TweetCreationError
from app.domains.posts.tweet.validator import Validator
from app.models.post import Post
from app.models.tweet import Tweet

logger = logging.getLogger(__name__)


class Operation(BaseOperation):
    """Shares a post to X (Twitter) by posting a tweet with the post title, excerpt, and link."""

    def _validator(self, post: Post) -> BaseValidator:
        return Validator(post=post)

    async def _do_perform(self, db: AsyncSession, post: Post) -> Tweet:
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
        try:
            response = client.create_tweet(text=tweet_text)
        except tweepy.TweepyException as e:
            logger.error("Failed to create tweet for post %s: %s", post.id, e)
            raise TweetCreationError(f"Failed to create tweet for post {post.id}: {e}") from e

        logger.info("Tweepy response for post %s: %s", post.id, response)
        tweet_id = response.data["id"]
        url = f"https://x.com/i/web/status/{tweet_id}"

        tweet = Tweet(
            id=str(uuid.uuid4()),
            post_id=post.id,
            tweet_id=tweet_id,
            url=url,
        )
        db.add(tweet)
        await db.commit()
        await db.refresh(tweet)

        return tweet
