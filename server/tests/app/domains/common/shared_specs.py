"""Shared test specs (mixins) for operation/validator tests.

These mixins provide reusable test cases for common patterns across domain operations.
Subclasses must implement the required class-level attributes documented on each mixin.
"""
import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.errors import ValidationError


class ValidatorBlankFieldSpec:
    """Shared spec for validators that enforce non-blank required fields.

    Subclass must define:
        validator_class: type    — the Validator class under test
        valid_kwargs: dict       — a complete set of valid kwargs

    Example:
        class TestMyValidator(ValidatorBlankFieldSpec):
            validator_class = MyValidator
            valid_kwargs = {"field_a": "value", "field_b": "value"}
    """
    validator_class = None
    valid_kwargs: dict = {}

    @pytest.mark.asyncio
    async def test_valid_starts_true(self, db_session: AsyncSession):
        """valid defaults to True before validate() is called."""
        v = self.validator_class(**self.valid_kwargs)
        assert v.valid is True

    @pytest.mark.asyncio
    async def test_errors_start_empty(self, db_session: AsyncSession):
        """errors defaults to empty dict before validate() is called."""
        v = self.validator_class(**self.valid_kwargs)
        assert v.errors == {}


class OperationValidationGatingSpec:
    """Shared spec verifying that perform() gates on validation.

    Subclass must define:
        operation_class: type    — the Operation class under test
        invalid_kwargs: dict     — kwargs that should fail validation
        invalid_fields: list[str]— field names expected in errors
    """
    operation_class = None
    invalid_kwargs: dict = {}
    invalid_fields: list = []

    @pytest.mark.asyncio
    async def test_perform_raises_validation_error_on_invalid_args(self):
        with pytest.raises(ValidationError) as exc_info:
            await self.operation_class().perform(**self.invalid_kwargs)
        for field in self.invalid_fields:
            assert field in exc_info.value.errors

    @pytest.mark.asyncio
    async def test_perform_does_not_touch_db_when_validation_fails(self):
        op = self.operation_class()
        op._do_perform = AsyncMock()
        with pytest.raises(ValidationError):
            await op.perform(**self.invalid_kwargs)
        op._do_perform.assert_not_called()
