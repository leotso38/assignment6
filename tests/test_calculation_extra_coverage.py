# tests/test_calculation_extra_coverage.py

import logging
from decimal import Decimal
import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


# ---------- success paths to exercise inner helpers ---------- #

def test_integer_division_positive_and_negatives():
    assert Calculation("IntegerDivision", Decimal("10"), Decimal("3")).result == Decimal("3")
    # floor division semantics with negatives
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


# ---------- error branches ---------- #

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


# ---------- cover 'generic' invalid-root helper branch ---------- #
# _raise_invalid_root has a final 'Invalid root operation' path that is not reachable
# via the Root implementation. Call it directly to exercise the else-case.
def test_raise_invalid_root_generic_branch():
    with pytest.raises(OperationError, match="Invalid root operation"):
        Calculation._raise_invalid_root(Decimal("1"), Decimal("1"))


# ---------- from_dict mismatch logging branch ---------- #

def test_from_dict_mismatch_logs_warning(monkeypatch, caplog):
    # valid data but with a deliberately wrong saved result to trigger the warning
    data = {
        "operation": "Addition",
        "operand1": "1",
        "operand2": "1",
        "result": "999",  # wrong on purpose
        "timestamp": "2025-01-01T00:00:00",
    }
    caplog.set_level(logging.WARNING)
    calc = Calculation.from_dict(data)
    assert calc.result == Decimal("2")
    # ensure warning was logged
    assert any("differs from computed result" in rec.message for rec in caplog.records)


# ---------- format_result fallback path (InvalidOperation) ---------- #

def test_format_result_invalid_operation_fallback():
    # Build a normal calc, then force a NaN to make quantize raise InvalidOperation.
    calc = Calculation("Addition", Decimal("1"), Decimal("1"))
    calc.result = Decimal("NaN")
    assert calc.format_result(precision=5) == "NaN"
