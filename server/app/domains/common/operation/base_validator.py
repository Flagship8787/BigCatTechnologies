from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


class BaseValidator(ABC):
    """Base class for all domain validators.

    Subclasses must implement `validate(db)` which populates `self.errors`
    and returns True (valid) or False (invalid).

    Usage:
        validator = MyValidator(arg1, arg2)
        if await validator.validate(db):
            # proceed
        else:
            # inspect validator.errors -> dict[str, list[str]]
            # or check validator.valid -> False
    """

    def __init__(self):
        self.valid: bool = True
        self.errors: dict[str, list[str]] = {}

    @abstractmethod
    async def validate(self, db: AsyncSession) -> bool:
        """Run all validation checks. Returns True if valid, False otherwise."""
        ...

    def _add_error(self, field: str, message: str) -> None:
        """Add a validation error for the given field and mark the validator invalid."""
        self.valid = False
        self.errors.setdefault(field, []).append(message)
