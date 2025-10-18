# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_repl_unexpected_ci.py
# Notes: Hit app.calculator_repl's generic inner-loop exception branch ("Unexpected error: ...").

import builtins
from unittest.mock import patch
from app.calculator_repl import calculator_repl

@patch.object(builtins, "print")
def test_repl_unexpected_exception_branch(mock_print):
    # Make create_operation raise AFTER reading the 'add' command to land in inner 'except Exception as e'
    with patch("app.calculator_repl.OperationFactory.create_operation", side_effect=RuntimeError("boom")):
        with patch.object(builtins, "input", side_effect=["add", "exit"]):
            calculator_repl()

    out = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Unexpected error: boom" in s for s in out)
    assert any("Goodbye!" in s for s in out)
