# tests/test_repl_save_load_errors.py

import builtins
from unittest.mock import patch
from app.calculator_repl import calculator_repl

@patch.object(builtins, "print")
def test_repl_save_error_message(mock_print):
    with patch("app.calculator_repl.Calculator.save_history", side_effect=ValueError("disk full")):
        with patch.object(builtins, "input", side_effect=["save", "exit"]):
            calculator_repl()
    out = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Error saving history: disk full" in s for s in out)

@patch.object(builtins, "print")
def test_repl_load_error_message(mock_print):
    with patch("app.calculator_repl.Calculator.load_history", side_effect=ValueError("corrupt csv")):
        with patch.object(builtins, "input", side_effect=["load", "exit"]):
            calculator_repl()
    out = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Error loading history: corrupt csv" in s for s in out)
