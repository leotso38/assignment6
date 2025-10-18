# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_repl.py
# Notes: Consolidated REPL tests (help, unknown, cancel, errors, undo/redo,
#        save/load, signals, fatal init). Keeps runs finite and deterministic.

import builtins
from unittest.mock import patch
from decimal import Decimal
import pytest

# Import the REPL CORE directly (not console wrapper)
from app.calculator_repl import calculator_repl


# --- helper ------------------------------------------------------------------

def _run_repl_with_inputs(inputs):
    """Feed a finite sequence of inputs to the REPL core."""
    with patch.object(builtins, "input", side_effect=inputs):
        calculator_repl()


# --- basic flows --------------------------------------------------------------

@patch.object(builtins, "print")
def test_help_unknown_history_exit(mock_print):
    # Empty history → deterministic output
    with patch("app.calculator.Calculator.show_history", return_value=[]):
        _run_repl_with_inputs(["help", "wat", "history", "exit"])

    mock_print.assert_any_call("\nAvailable commands:")
    mock_print.assert_any_call("Unknown command: 'wat'. Type 'help' for available commands.")
    mock_print.assert_any_call("No calculations in history")
    mock_print.assert_any_call("History saved successfully.")
    mock_print.assert_any_call("Goodbye!")


@patch.object(builtins, "print")
def test_help_menu_includes_core_commands(mock_print):
    _run_repl_with_inputs(["help", "exit"])
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    # Spot-check a few menu lines so we don't couple to formatting too tightly
    assert any("add, subtract, multiply, divide, power, root, modulus, intdiv, percentage, absdiff" in s for s in printed)
    assert any("history  - Show calculation history" in s for s in printed)
    assert any("exit     - Exit the calculator" in s for s in printed)


@patch.object(builtins, "print")
def test_history_nonempty_lists_entries(mock_print):
    with patch("app.calculator.Calculator.show_history", return_value=["Addition(1, 2) = 3"]):
        _run_repl_with_inputs(["history", "exit"])
    mock_print.assert_any_call("\nCalculation History:")
    mock_print.assert_any_call("1. Addition(1, 2) = 3")


# --- operation and error paths ------------------------------------------------

@patch.object(builtins, "print")
def test_add_cancel_paths(mock_print):
    # add then cancel (first operand), add then cancel (second), exit
    _run_repl_with_inputs(["add", "cancel", "add", "3", "cancel", "exit"])
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Operation cancelled" in s for s in printed)
    assert any("Goodbye!" in s for s in printed)


@patch.object(builtins, "print")
def test_divide_by_zero_error(mock_print):
    _run_repl_with_inputs(["divide", "1", "0", "exit"])
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Division by zero is not allowed" in s for s in printed)


@patch.object(builtins, "print")
def test_percentage_shows_percent(mock_print):
    _run_repl_with_inputs(["percentage", "25", "100", "exit"])
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Result: 25%" in s for s in printed)


# --- undo/redo/clear/save/load ------------------------------------------------

@patch.object(builtins, "print")
def test_undo_redo_clear_history(mock_print):
    _run_repl_with_inputs(["add", "2", "2", "undo", "redo", "clear", "history", "exit"])
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Operation undone" in s for s in printed)
    assert any("Operation redone" in s for s in printed)
    assert any("History cleared" in s for s in printed)
    assert any("No calculations in history" in s for s in printed)


@patch.object(builtins, "print")
def test_redo_nothing_then_exit(mock_print):
    _run_repl_with_inputs(["redo", "exit"])
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Nothing to redo" in s for s in printed)


@patch.object(builtins, "print")
def test_save_load_success_and_failures(mock_print, monkeypatch):
    # Success cases
    _run_repl_with_inputs(["save", "load", "exit"])

    # Fail save_history
    from app.calculator import Calculator
    def boom_save(*_a, **_k): raise RuntimeError("disk full")
    monkeypatch.setattr(Calculator, "save_history", boom_save, raising=True)
    _run_repl_with_inputs(["save", "exit"])

    # Fail load_history
    def boom_load(*_a, **_k): raise RuntimeError("corrupt file")
    monkeypatch.setattr(Calculator, "load_history", boom_load, raising=True)
    _run_repl_with_inputs(["load", "exit"])

    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Error saving history: disk full" in s for s in printed)
    assert any("Error loading history: corrupt file" in s for s in printed)


# --- signals & unexpected paths ----------------------------------------------

@patch.object(builtins, "print")
def test_keyboardinterrupt_and_eof(mock_print):
    # Simulate Ctrl-C then Ctrl-D/EOF
    with patch.object(builtins, "input", side_effect=[KeyboardInterrupt(), EOFError()]):
        calculator_repl()
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Operation cancelled" in s for s in printed)
    assert any("Input terminated. Exiting..." in s for s in printed)


@patch.object(builtins, "print")
def test_unexpected_exception_then_exit(mock_print):
    # First input raises; second is 'exit' to terminate
    with patch.object(builtins, "input", side_effect=[RuntimeError("boom"), "exit"]):
        calculator_repl()
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    # Accept either message variant
    assert any(("Unexpected error: boom" in s) or ("Error: boom" in s) for s in printed)
    assert any("Goodbye!" in s for s in printed)


def test_fatal_error_on_init():
    # Patch Calculator __init__ to raise to hit outermost fatal handler.
    class Boom(Exception):
        pass
    with patch("app.calculator_repl.Calculator", side_effect=Boom("init failed")):
        with patch.object(builtins, "print") as mock_print:
            with pytest.raises(Boom):
                calculator_repl()
            out = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
            assert any("Fatal error: init failed" in s for s in out)
