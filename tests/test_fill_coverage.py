# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_fill_coverage.py
# Notes: Consolidated coverage tests to hit remaining branches in calculation.py and calculator.py.

import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import Addition
from app.exceptions import OperationError


# ---------- Helpers ----------

def _mk_calc(tmp_path: Path, max_history_size: int | str = 10) -> Calculator:
    cfg = CalculatorConfig(base_dir=tmp_path, max_history_size=10 if isinstance(max_history_size, str) else max_history_size)
    c = Calculator(config=cfg)
    c.clear_history()
    # allow overriding post-init to trigger parse failures later
    c.config.max_history_size = max_history_size
    return c


# ---------- app/calculation.py targets ----------

def test_format_result_quantize_success():
    """Hit the normal quantize path (not the fallback)."""
    c = Calculation("Addition", Decimal("1.234567"), Decimal("0"))
    c.result = Decimal("1.234567")
    assert c.format_result(precision=2) == "1.23"


def test_calculation_equality_true_path():
    """__eq__ true path for identical Calculations."""
    a = Calculation("Addition", Decimal("2"), Decimal("3"))
    b = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert a == b


def test_from_dict_invalid_data_raises():
    """Missing key in dict should raise OperationError via except-block."""
    bad = {
        "operation": "Addition",
        # "operand1" intentionally missing
        "operand2": "1",
        "result": "2",
        "timestamp": "2025-01-01T00:00:00",
    }
    with pytest.raises(OperationError, match="Invalid calculation data:"):
        Calculation.from_dict(bad)


def test_format_result_infinity_fallback():
    """Force InvalidOperation in quantize by using Infinity -> fallback returns raw string."""
    c = Calculation("Addition", Decimal("1"), Decimal("1"))
    c.result = Decimal("Infinity")
    assert c.format_result(precision=3) == "Infinity"


# ---------- app/calculator.py targets ----------

def test_history_trimming_to_max(tmp_path):
    """Ensure trimming keeps only the most recent N entries."""
    c = _mk_calc(tmp_path, max_history_size=1)
    # minimal Addition op object with the required interface
    add_op = type("Add", (), {"execute": lambda _s, a, b: a + b, "__str__": lambda _s: "Addition"})()
    c.set_operation(add_op)

    c.perform_operation("1", "1")   # first entry
    c.perform_operation("2", "2")   # second entry triggers trimming
    assert len(c.history) == 1
    assert str(c.history[0]) == "Addition(2, 2) = 4"


def test_show_history_percentage_appends_percent(tmp_path):
    """Percentage entries in show_history() should render with a % suffix."""
    c = _mk_calc(tmp_path)
    c.history.append(Calculation("Percentage", Decimal("25"), Decimal("100")))
    lines = c.show_history()
    assert lines and lines[0].endswith("%")
    assert "Percentage(25, 100) = 25%" in lines[0]


def test_format_decimal_plain_trims_and_neg_zero(tmp_path):
    """_format_decimal_plain trims trailing zeros and normalizes -0 to 0."""
    s1 = Calculator._format_decimal_plain(Decimal("2.5000"))
    s2 = Calculator._format_decimal_plain(Decimal("-0.0000"))
    assert s1 == "2.5"
    assert s2 == "0"


def test_perform_operation_bad_max_history_size_parse(tmp_path):
    """Set max_history_size to a non-int string to hit ValueError parse path (max_n=0)."""
    calc = _mk_calc(tmp_path, max_history_size="bogus")  # int("bogus") -> ValueError
    calc.set_operation(Addition())
    calc.perform_operation("1", "1")
    # Still records one entry; no trimming since max_n=0 disables it
    assert len(calc.history) == 1
