from abc import ABC, abstractmethod
from typing import Any, Coroutine

from app.db import AsyncSessionLocal
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.common.operation.errors import ValidationError


class BaseOperation(ABC):
    """Base class for all domain operations.

    Subclasses must implement `_validator(*args, **kwargs)` and `_do_perform(*args, **kwargs)`.

    Usage:
        result = await SomeOperation().perform(arg1, arg2)

    If validation fails, `ValidationError` is raised with a `.errors` dict
    containing all validation failures before any DB work is done.
    """

    def perform(self, *args, **kwargs) -> Coroutine[Any, Any, Any]:
        """Validate synchronously, then return the async perform coroutine.

        Raises ValidationError immediately if validation fails.
        Returns an awaitable coroutine if validation passes.
        """
        validator = self._validator(*args, **kwargs)
        if not validator.validate():
            raise ValidationError(validator.errors)
        return self._run(*args, **kwargs)

    async def _run(self, *args, **kwargs) -> Any:
        """Open a DB session and delegate to _do_perform."""
        async with AsyncSessionLocal() as db:
            return await self._do_perform(db, *args, **kwargs)

    @abstractmethod
    def _validator(self, *args, **kwargs) -> BaseValidator:
        """Return an initialized validator for the given args.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _validator()")

    @abstractmethod
    async def _do_perform(self, db, *args, **kwargs) -> Any:
        """Perform the operation logic using the provided DB session.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _do_perform()")
