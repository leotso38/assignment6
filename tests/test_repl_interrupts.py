# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_repl_interrupts.py
# Notes: Hit KeyboardInterrupt and EOFError branches inside the REPL loop.

import builtins
from unittest.mock import patch

from app.calculator_repl import calculator_repl


@patch.object(builtins, "print")
def test_repl_keyboardinterrupt_then_exit(mock_print):
    # First prompt raises KeyboardInterrupt -> "Operation cancelled", then 'exit'
    with patch.object(builtins, "input", side_effect=[KeyboardInterrupt(), "exit"]):
        calculator_repl()

    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Operation cancelled" in s for s in printed)
    assert any("Goodbye!" in s for s in printed)
    
@patch.object(builtins, "print")
def test_repl_eof_exits_cleanly(mock_print):
    # Direct EOF on first prompt -> "Input terminated. Exiting..." then return
    with patch.object(builtins, "input", side_effect=[EOFError()]):
        calculator_repl()

    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Input terminated. Exiting..." in s for s in printed)
