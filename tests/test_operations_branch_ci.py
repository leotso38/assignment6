# tests/test_operations_branch_ci.py
# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# Notes: Exercise extra operation branches for CI.

from decimal import Decimal

def test_division_executes_and_hits_validate_branch():
    # local import avoids any ordering/import-path hiccups
    from app.operations import Division
    assert Division().execute(Decimal("6"), Decimal("2")) == Decimal("3")

def test_ops_extra_branches_for_ci():
    from app.operations import Modulus, IntegerDivision
    assert Modulus().execute(Decimal("-10"), Decimal("3")) == Decimal("2")
    assert IntegerDivision().execute(Decimal("-7"), Decimal("3")) == Decimal("-2")
