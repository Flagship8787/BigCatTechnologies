from abc import ABC, abstractmethod
from typing import Any

from app.db import AsyncSessionLocal
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.common.operation.errors import ValidationError


class BaseOperation(ABC):
    """Base class for all domain operations.

    Subclasses must implement `_validator(*args, **kwargs)` and `_do_perform(db, *args, **kwargs)`.

    Usage:
        result = await SomeOperation().perform(arg1, arg2)

    If validation fails, `ValidationError` is raised with a `.errors` dict
    containing all validation failures before any DB work is done.
    A single DB session is shared between validation and perform.
    """

    async def perform(self, *args, **kwargs) -> Any:
        """Validate, then perform the operation within a single DB session.

        Raises ValidationError if validation fails.
        """
        async with AsyncSessionLocal() as db:
            validator = self._validator(*args, **kwargs)
            if not await validator.validate(db):
                raise ValidationError(validator.errors)
            return await self._do_perform(db, *args, **kwargs)

    async def perform_in(self, db, *args, **kwargs) -> Any:
        """Validate, then perform the operation within a provided DB session.

        Use this when the caller already holds a session (e.g. a controller).
        Raises ValidationError if validation fails.
        """
        validator = self._validator(*args, **kwargs)
        if not await validator.validate(db):
            raise ValidationError(validator.errors)
        return await self._do_perform(db, *args, **kwargs)

    @abstractmethod
    def _validator(self, *args, **kwargs) -> BaseValidator:
        """Return an initialized validator for the given args."""
        ...

    @abstractmethod
    async def _do_perform(self, db, *args, **kwargs) -> Any:
        """Perform the operation logic using the provided DB session."""
        ...
