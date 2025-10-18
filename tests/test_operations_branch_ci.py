# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_operations_branch_ci.py
# Notes: Exercise a validation-guarded execute path deterministically.

from decimal import Decimal
from app.operations import Division

def test_division_executes_and_hits_validate_branch():
    assert Division().execute(Decimal("6"), Decimal("2")) == Decimal("3")
