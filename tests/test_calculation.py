# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_calculation.py
# Purpose: Consolidated unit tests for Calculation ops, errors, logging, and dunder methods.

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
    """Basic arithmetic, power, and typical roots."""
    assert Calculation("Addition", Decimal("2"), Decimal("3")).result == Decimal("5")
    assert Calculation("Subtraction", Decimal("5"), Decimal("3")).result == Decimal("2")
    assert Calculation("Multiplication", Decimal("2"), Decimal("3")).result == Decimal("6")
    assert Calculation("Division", Decimal("10"), Decimal("4")).result == Decimal("2.5")
    assert Calculation("Power", Decimal("2"), Decimal("3")).result == Decimal("8")
    # typical roots
    assert Calculation("Root", Decimal("9"), Decimal("2")).result == Decimal("3")
    assert Calculation("Root", Decimal("27"), Decimal("3")).result == Decimal("3")


def test_integer_division_positive_and_negatives():
    """Floor-division semantics must match Decimal/Python."""
    assert Calculation("IntegerDivision", Decimal("10"), Decimal("3")).result == Decimal("3")
    assert Calculation("IntegerDivision", Decimal("-10"), Decimal("3")).result == Decimal("-4")
    assert Calculation("IntegerDivision", Decimal("10"), Decimal("-3")).result == Decimal("-4")
    assert Calculation("IntegerDivision", Decimal("-10"), Decimal("-3")).result == Decimal("3")


def test_modulus_with_negatives_matches_python_decimal():
    """Modulo sign behavior mirrors Decimal implementation."""
    assert Calculation("Modulus", Decimal("10"), Decimal("3")).result == Decimal("1")
    assert Calculation("Modulus", Decimal("-10"), Decimal("3")).result == Decimal("2")
    assert Calculation("Modulus", Decimal("10"), Decimal("-3")).result == Decimal("-2")
    assert Calculation("Modulus", Decimal("-10"), Decimal("-3")).result == Decimal("-1")


def test_percentage_and_absdiff():
    """Percentage (a% of b) and absolute difference."""
    assert Calculation("Percentage", Decimal("25"), Decimal("100")).result == Decimal("25")
    assert Calculation("AbsoluteDifference", Decimal("7"), Decimal("3")).result == Decimal("4")
    assert Calculation("AbsoluteDifference", Decimal("3"), Decimal("7")).result == Decimal("4")


# -----------------------------
# Error branches
# -----------------------------

def test_division_by_zero_raises():
    """Division by zero → OperationError."""
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("Division", Decimal("1"), Decimal("0"))


def test_percentage_by_zero_raises():
    """Percentage uses division; zero denominator should error."""
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("Percentage", Decimal("1"), Decimal("0"))


def test_integer_division_by_zero_raises():
    """Integer division by zero must raise."""
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("IntegerDivision", Decimal("1"), Decimal("0"))


def test_modulus_by_zero_raises():
    """Modulo by zero must raise."""
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation("Modulus", Decimal("1"), Decimal("0"))


def test_negative_exponent_raises():
    """Negative exponent is disallowed by spec."""
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation("Power", Decimal("2"), Decimal("-1"))


def test_root_zero_and_negative_base_raise():
    """Invalid roots: zero-degree; even root of negative base."""
    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation("Root", Decimal("9"), Decimal("0"))
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation("Root", Decimal("-9"), Decimal("2"))


def test_unknown_operation_raises():
    """Unsupported operation must raise Unknown operation."""
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation("Nope", Decimal("1"), Decimal("2"))


def test_raise_invalid_root_generic_branch():
    """Force generic invalid-root branch (unreachable via normal inputs)."""
    with pytest.raises(OperationError, match="Invalid root operation"):
        Calculation._raise_invalid_root(Decimal("1"), Decimal("1"))


# -----------------------------
# Logging & formatting helpers
# -----------------------------

def test_from_dict_mismatch_logs_warning(caplog):
    """from_dict warns when stored result ≠ computed."""
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
    """Quantize InvalidOperation → return raw string (e.g., NaN)."""
    calc = Calculation("Addition", Decimal("1"), Decimal("1"))
    calc.result = Decimal("NaN")
    assert calc.format_result(precision=5) == "NaN"


def test_calculation_wraps_runtime_error(monkeypatch):
    """Runtime error inside pow() should be wrapped with OperationError."""
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
    """String forms contain details; eq vs non-Calculation returns NotImplemented."""
    c = Calculation("Addition", Decimal("2"), Decimal("3"))
    s = str(c)
    r = repr(c)
    assert "Addition" in s and "= 5" in s
    assert "Calculation(" in r and "operation='Addition'" in r
    # For non-Calculation comparisons, return NotImplemented (Python data model best practice).
    assert (c.__eq__(123) is NotImplemented)
