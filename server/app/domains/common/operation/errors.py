class ValidationError(Exception):
    """Raised when an operation's validator finds errors."""

    def __init__(self, errors: dict[str, list[str]]):
        self.errors = errors
        super().__init__(str(errors))
