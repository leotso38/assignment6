# tests/test_repl_help_full_menu_ci.py
# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# Notes: Ensure all help lines execute in CI coverage.

import builtins
from unittest.mock import patch
from app.calculator_repl import calculator_repl

@patch.object(builtins, "input", side_effect=["help", "exit"])
def test_repl_help_full_menu(_mock_input, capsys, monkeypatch):
    # Avoid touching disk on save at exit
    monkeypatch.setattr("app.calculator_repl.Calculator.save_history", lambda *a, **k: None, raising=True)
    monkeypatch.setattr("app.calculator_repl.Calculator.load_history", lambda *a, **k: None, raising=True)

    calculator_repl()
    out = capsys.readouterr().out

    # Assert a few individual help lines to ensure those exact lines executed
    assert "\nAvailable commands:" in out
    assert "  add, subtract, multiply, divide, power, root, modulus, intdiv, percentage, absdiff" in out
    assert "  history  - Show calculation history" in out
    assert "  clear    - Clear calculation history" in out
    assert "  undo     - Undo the last calculation" in out
    assert "  redo     - Redo the last undone calculation" in out
    assert "  save     - Save calculation history to file" in out
    assert "  load     - Load calculation history from file" in out
    assert "  exit     - Exit the calculator" in out
