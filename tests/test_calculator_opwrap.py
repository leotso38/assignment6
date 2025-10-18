# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_calculator_opwrap.py
# Notes: Exercise perform_operation's generic except -> OperationError path.

from decimal import Decimal
from pathlib import Path

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError


class _BoomOp:
    def __str__(self) -> str:
        return "Addition"  # name doesn't matter for the wrapper
    def execute(self, a: Decimal, b: Decimal):
        raise RuntimeError("boom")  # force generic exception


def _mk_calc(tmp_path: Path) -> Calculator:
    cfg = CalculatorConfig(base_dir=tmp_path)
    c = Calculator(config=cfg)
    c.clear_history()
    return c


def test_perform_operation_wraps_generic_exception(tmp_path):
    c = _mk_calc(tmp_path)
    c.set_operation(_BoomOp())
    with pytest.raises(OperationError, match="Operation failed: boom"):
        c.perform_operation("1", "2")
