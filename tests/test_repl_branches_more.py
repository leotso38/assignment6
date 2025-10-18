# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_repl_branches_more.py
# Notes: Cover remaining branches in app.calculator_repl (redo none, percentage path, fatal init).

import builtins
from unittest.mock import patch
from decimal import Decimal

import pytest

from app.calculator_repl import calculator_repl


@patch.object(builtins, "print")
def test_repl_redo_nothing(mock_print):
    # redo before any operation
    with patch.object(builtins, "input", side_effect=["redo", "exit"]):
        calculator_repl()
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Nothing to redo" in s for s in printed)


@patch.object(builtins, "print")
def test_repl_percentage_shows_percent(mock_print):
    # percentage 25 of 100 -> "25%"
    with patch.object(builtins, "input", side_effect=["percentage", "25", "100", "exit"]):
        calculator_repl()
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Result: 25%" in s for s in printed)


def test_repl_fatal_error_on_init():
    # Patch Calculator __init__ to raise to hit outermost fatal handler.
    class Boom(Exception):
        pass

    with patch("app.calculator_repl.Calculator", side_effect=Boom("init failed")):
        with patch.object(builtins, "print") as mock_print:
            with pytest.raises(Boom):
                calculator_repl()
            out = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
            assert any("Fatal error: init failed" in s for s in out)
