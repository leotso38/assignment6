# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_repl_branches.py
# Notes: Hit hard-to-reach branches in app.calculator_repl (help, unknown, cancel, errors, undo/redo, save/load, signals, unexpected errs).

import builtins
from unittest.mock import patch
import pytest

# Import the REPL CORE directly (not console wrapper)
from app.calculator_repl import calculator_repl


def _run_repl_with_inputs(inputs):
    """Feed a sequence of inputs to the REPL core."""
    with patch.object(builtins, "input", side_effect=inputs):
        calculator_repl()


@patch.object(builtins, "print")
def test_repl_help_unknown_history_exit(mock_print):
    # help -> unknown -> history (empty) -> exit
    _run_repl_with_inputs(["help", "wat", "history", "exit"])
    mock_print.assert_any_call("\nAvailable commands:")
    mock_print.assert_any_call("Unknown command: 'wat'. Type 'help' for available commands.")
    mock_print.assert_any_call("No calculations in history")
    mock_print.assert_any_call("History saved successfully.")
    mock_print.assert_any_call("Goodbye!")


@patch.object(builtins, "print")
def test_repl_add_cancel_paths(mock_print):
    # add, cancel at first; then add, cancel at second; exit
    _run_repl_with_inputs(["add", "cancel", "add", "3", "cancel", "exit"])
    # both cancel paths should be reported
    assert any("Operation cancelled" in c.args[0] for c in mock_print.call_args_list)
    mock_print.assert_any_call("Goodbye!")


@patch.object(builtins, "print")
def test_repl_divide_by_zero_error(mock_print):
    _run_repl_with_inputs(["divide", "1", "0", "exit"])
    assert any("Division by zero is not allowed" in c.args[0] for c in mock_print.call_args_list)


@patch.object(builtins, "print")
def test_repl_undo_redo_clear_history(mock_print):
    _run_repl_with_inputs(["add", "2", "2", "undo", "redo", "clear", "history", "exit"])
    mock_print.assert_any_call("Operation undone")
    mock_print.assert_any_call("Operation redone")
    mock_print.assert_any_call("History cleared")
    mock_print.assert_any_call("No calculations in history")


@patch.object(builtins, "print")
def test_repl_save_load_success_and_failures(mock_print, monkeypatch):
    # First run: normal save/load success
    _run_repl_with_inputs(["save", "load", "exit"])

    # Fail save_history
    from app.calculator import Calculator
    def boom_save(*a, **k): raise RuntimeError("disk full")
    monkeypatch.setattr(Calculator, "save_history", boom_save, raising=True)
    _run_repl_with_inputs(["save", "exit"])
    assert any("Error saving history: disk full" in c.args[0] for c in mock_print.call_args_list)

    # Fail load_history
    def boom_load(*a, **k): raise RuntimeError("corrupt file")
    monkeypatch.setattr(Calculator, "load_history", boom_load, raising=True)
    _run_repl_with_inputs(["load", "exit"])
    assert any("Error loading history: corrupt file" in c.args[0] for c in mock_print.call_args_list)


@patch.object(builtins, "print")
def test_repl_keyboardinterrupt_and_eof(mock_print):
    with patch.object(builtins, "input", side_effect=[KeyboardInterrupt(), EOFError()]):
        calculator_repl()
    mock_print.assert_any_call("Operation cancelled")
    mock_print.assert_any_call("Input terminated. Exiting...")


@patch.object(builtins, "print")
def test_repl_unexpected_exception(mock_print):
    # First input raises; second is 'exit' to terminate
    with patch.object(builtins, "input", side_effect=[RuntimeError("boom"), "exit"]):
        calculator_repl()
    # Accept either "Unexpected error: boom" or "Error: boom"
    printed = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any(("Unexpected error: boom" in s) or ("Error: boom" in s) for s in printed)
    assert any("Goodbye!" in s for s in printed)

