# tests/test_calculation_consolidated.py

import logging
import builtins
from decimal import Decimal, InvalidOperation
import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


# -----------------------------
# Success paths & semantics
# -----------------------------

def test_add_sub_mul_div_power_root_success():
    assert Calculation("Addition", Decimal("2"), Decimal("3")).result == Decimal("5")
    assert Calculation("Subtraction", Decimal("5"), Decimal("3")).result == Decimal("2")
    assert Calculation("Multiplication", Decimal("2"), Decimal("3")).result == Decimal("6")
    assert Calculation("Division", Decimal("10"), Decimal("4")).result == Decimal("2.5")
    assert Calculation("Power", Decimal("2"), Decimal("3")).result == Decimal("8")
    # typical roots
    assert Calculation("Root", Decimal("9"), Decimal("2")).result == Decimal("3")
    assert Calculation("Root", Decimal("27"), Decimal("3")).result == Decimal("3")


def test_integer_division_positive_and_negatives():
    # Floor-division semantics (match Python/Decimal)
    assert Calculation("IntegerDivision", Decimal("10"), Decimal("3")).result == Decimal("3")
    assert Calculation("IntegerDivision", Decimal("-10"), Decimal("3")).result == Decimal("-4")
    assert Calculation("IntegerDivision", Decimal("10"), Decimal("-3")).result == Decimal("-4")
    assert Calculation("IntegerDivision", Decimal("-10"), Decimal("-3")).result == Decimal("3")


def test_modulus_with_negatives_matches_python_decimal():
    assert Calculation("Modulus", Decimal("10"), Decimal("3")).result == Decimal("1")
    assert Calculation("Modulus", Decimal("-10"), Decimal("3")).result == Decimal("2")
    assert Calculation("Modulus", Decimal("10"), Decimal("-3")).result == Decimal("-2")
    assert Calculation("Modulus", Decimal("-10"), Decimal("-3")).result == Decimal("-1")


def test_percentage_and_absdiff():
    assert Calculation("Percentage", Decimal("25"), Decimal("100")).result == Decimal("25")
    assert Calculation("AbsoluteDifference", Decimal("7"), Decimal("3")).result == Decimal("4")
    assert Calculation("AbsoluteDifference", Decimal("3"), Decimal("7")).result == Decimal("4")


# -----------------------------
# Error branches
# -----------------------------

def test_division_by_zero_raises():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("Division", Decimal("1"), Decimal("0"))


def test_percentage_by_zero_raises():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("Percentage", Decimal("1"), Decimal("0"))


def test_integer_division_by_zero_raises():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("IntegerDivision", Decimal("1"), Decimal("0"))


def test_modulus_by_zero_raises():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("Modulus", Decimal("1"), Decimal("0"))


def test_negative_exponent_raises():
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation("Power", Decimal("2"), Decimal("-1"))


def test_root_zero_and_negative_base_raise():
    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation("Root", Decimal("9"), Decimal("0"))
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation("Root", Decimal("-9"), Decimal("2"))


def test_unknown_operation_raises():
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation("Nope", Decimal("1"), Decimal("2"))


# This calls the 'generic' else path in _raise_invalid_root directly,
# which normal inputs can't reach via Root().  (exercises the final branch)
def test_raise_invalid_root_generic_branch():
    with pytest.raises(OperationError, match="Invalid root operation"):
        Calculation._raise_invalid_root(Decimal("1"), Decimal("1"))


# -----------------------------
# Logging & formatting helpers
# -----------------------------

def test_from_dict_mismatch_logs_warning(caplog):
    # valid data but with a deliberately wrong saved result to trigger the warning
    data = {
        "operation": "Addition",
        "operand1": "1",
        "operand2": "1",
        "result": "999",  # intentionally wrong
        "timestamp": "2025-01-01T00:00:00",
    }
    caplog.set_level(logging.WARNING)
    calc = Calculation.from_dict(data)
    assert calc.result == Decimal("2")
    assert any("differs from computed result" in rec.message for rec in caplog.records)


def test_format_result_invalid_operation_fallback():
    # Force InvalidOperation inside quantize()
    calc = Calculation("Addition", Decimal("1"), Decimal("1"))
    calc.result = Decimal("NaN")
    assert calc.format_result(precision=5) == "NaN"


def test_calculation_wraps_runtime_error(monkeypatch):
    # Cause pow() to throw to hit the "Calculation failed: ..." wrapper on Power
    original_pow = builtins.pow
    def boom(*args, **kwargs):
        raise ValueError("boom")
    monkeypatch.setattr(builtins, "pow", boom)
    try:
        with pytest.raises(OperationError, match="Calculation failed: boom"):
            Calculation("Power", Decimal("2"), Decimal("3"))
    finally:
        monkeypatch.setattr(builtins, "pow", original_pow)


# -----------------------------
# __str__ / __repr__ / __eq__
# -----------------------------

def test_repr_and_str_and_eq_notimplemented():
    c = Calculation("Addition", Decimal("2"), Decimal("3"))
    s = str(c)
    r = repr(c)
    assert "Addition" in s and "= 5" in s
    assert "Calculation(" in r and "operation='Addition'" in r
    # when comparing against a non-Calculation object, Python's datamodel
    # best-practice is to return NotImplemented so the other side can try.
    assert (c.__eq__(123) is NotImplemented)
