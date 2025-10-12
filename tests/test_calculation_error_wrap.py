# tests/test_calculation_error_wrap.py
import builtins
import pytest
from decimal import Decimal
from app.calculation import Calculation
from app.exceptions import OperationError

def test_calculation_wraps_runtime_errors(monkeypatch):
    # Force ValueError inside Power lambda to hit the except block
    original_pow = builtins.pow
    def boom(*args, **kwargs): raise ValueError("kaboom")
    monkeypatch.setattr(builtins, "pow", boom)
    try:
        with pytest.raises(OperationError, match="Calculation failed: kaboom"):
            Calculation("Power", Decimal("2"), Decimal("3"))
    finally:
        # restore pow to avoid side-effects in later tests
        monkeypatch.setattr(builtins, "pow", original_pow)
