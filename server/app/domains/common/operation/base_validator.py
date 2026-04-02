from abc import ABC, abstractmethod


class BaseValidator(ABC):
    """Base class for all domain validators.

    Subclasses must implement `validate()` which populates `self.errors`
    and returns True (valid) or False (invalid).

    Usage:
        validator = MyValidator(arg1, arg2)
        if validator.validate():
            # proceed
        else:
            # inspect validator.errors -> dict[str, list[str]]
    """

    def __init__(self):
        self.errors: dict[str, list[str]] = {}

    @abstractmethod
    def validate(self) -> bool:
        """Run all validation checks. Returns True if valid, False otherwise.

        Implementations should call `self._add_error(field, message)` for each
        validation failure and return `len(self.errors) == 0` at the end.
        """
        raise NotImplementedError("Subclasses must implement validate()")

    def _add_error(self, field: str, message: str) -> None:
        """Add a validation error for the given field."""
        self.errors.setdefault(field, []).append(message)
