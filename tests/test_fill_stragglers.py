# tests/test_fill_stragglers.py

import pytest
from decimal import Decimal
from app.history import LoggingObserver
from app.operations import Operation

def test_logging_observer_raises_on_none():
    with pytest.raises(AttributeError):
        LoggingObserver().update(None)

class _Dummy(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        # call base no-op validate to mark it covered
        self.validate_operands(a, b)
        return a
def test_base_operation_validate_noop():
    assert _Dummy().execute(Decimal("1"), Decimal("2")) == Decimal("1")
