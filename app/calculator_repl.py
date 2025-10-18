# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: app/calculator_repl.py
# Notes: Text-based REPL for calculator operations with optional color output and full command handling.

"""
Text REPL for the calculator with optional colorized output.

- Uses app.console.fmt() and prompt_text() for styling when CALCULATOR_COLOR=1 and colorama is installed.
- Returns gracefully on exit/EOF; outer wrapper handles SystemExit for CLI/tests.
"""

from __future__ import annotations
from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory
from app.console import fmt, prompt_text


def _print(msg: str, kind: str | None = None) -> None:
    """Helper to print formatted message via console formatter."""
    print(fmt(msg, kind))


def calculator_repl() -> None:
    """Interactive calculator REPL loop."""
    try:
        calc = Calculator()
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        _print("Calculator started. Type 'help' for commands.", "heading")

        while True:
            try:
                command = input(prompt_text("Enter command: ")).lower().strip()

                # ---- Help menu ----
                if command == "help":
                    _print("\nAvailable commands:", "heading")
                    _print("  add, subtract, multiply, divide, power, root, modulus, intdiv, percentage, absdiff", "info") # pragma: no cover
                    _print("  history  - Show calculation history", "info")
                    _print("  clear    - Clear calculation history", "info")
                    _print("  undo     - Undo the last calculation", "info")
                    _print("  redo     - Redo the last undone calculation", "info")
                    _print("  save     - Save calculation history to file", "info")
                    _print("  load     - Load calculation history from file", "info")
                    _print("  exit     - Exit the calculator", "info")
                    continue

                # ---- Exit and save ----
                if command == "exit":
                    try:
                        calc.save_history()
                        _print("History saved successfully.", "ok")
                    except Exception as e:
                        _print(f"Warning: Could not save history: {e}", "warn")
                    _print("Goodbye!", "heading")
                    return  # exit gracefully

                # ---- History management ----
                if command == "history":
                    history = calc.show_history()
                    if not history:
                        _print("No calculations in history", "info")
                    else:
                        _print("\nCalculation History:", "heading")
                        for i, entry in enumerate(history, 1):
                            _print(f"{i}. {entry}", "info")
                    continue

                if command == "clear":
                    calc.clear_history()
                    _print("History cleared", "ok")
                    continue

                if command == "undo":
                    if calc.undo():
                        _print("Operation undone", "ok")
                    else:
                        _print("Nothing to undo", "warn")  # pragma: no cover
                    continue

                if command == "redo":
                    if calc.redo():
                        _print("Operation redone", "ok")
                    else:
                        _print("Nothing to redo", "warn")
                    continue

                if command == "save":
                    try:
                        calc.save_history()
                        _print("History saved successfully", "ok")
                    except Exception as e:
                        _print(f"Error saving history: {e}", "error")
                    continue

                if command == "load":
                    try:
                        calc.load_history()
                        _print("History loaded successfully", "ok")
                    except Exception as e:
                        _print(f"Error loading history: {e}", "error")
                    continue

                # ---- Arithmetic operations ----
                if command in [
                    "add", "subtract", "multiply", "divide",
                    "power", "root", "modulus", "intdiv",
                    "percentage", "absdiff"
                ]:
                    try:
                        _print("\nEnter numbers (or 'cancel' to abort):", "info")
                        a = input(prompt_text("First number: "))
                        if a.lower() == "cancel":
                            _print("Operation cancelled", "warn")
                            continue
                        b = input(prompt_text("Second number: "))
                        if b.lower() == "cancel":
                            _print("Operation cancelled", "warn")
                            continue

                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)
                        result = calc.perform_operation(a, b)

                        result_disp = result.normalize() if isinstance(result, Decimal) else result
                        if str(operation) == "Percentage":
                            result_disp = f"{result_disp}%"

                        _print(f"\nResult: {result_disp}", "ok")
                    except (ValidationError, OperationError) as e:
                        _print(f"Error: {e}", "error")
                    except Exception as e:
                        _print(f"Unexpected error: {e}", "error")
                    continue

                # ---- Unknown command ----
                _print(f"Unknown command: '{command}'. Type 'help' for available commands.", "warn")

            # ---- Interrupts / termination ----
            except KeyboardInterrupt:
                _print("Operation cancelled", "warn")
                continue
            except EOFError:
                _print("Input terminated. Exiting...", "warn")
                return
            except Exception as e:
                _print(f"Error: {e}", "error")
                continue

    except Exception as e:
        _print(f"Fatal error: {e}", "error")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise
