class TweetCreationError(Exception):
    """Raised when the X (Twitter) API fails to create a tweet."""

    def __init__(self, message: str):
        super().__init__(message)
