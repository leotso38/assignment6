# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_repl_history_nonempty.py
# Notes: Ensure REPL prints non-empty history listing.

import builtins
from unittest.mock import patch

from app.calculator_repl import calculator_repl


@patch.object(builtins, "print")
def test_repl_history_nonempty(mock_print):
    # add 2+3, then 'history', then 'exit'
    with patch.object(builtins, "input", side_effect=["add", "2", "3", "history", "exit"]):
        calculator_repl()

    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Calculation History:" in s for s in printed)
    assert any("Addition(2, 3) = 5" in s for s in printed)
    assert any("Goodbye!" in s for s in printed)
