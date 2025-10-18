# tests/test_repl_unexpected_ci.py
# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# Notes: Deterministically hit the REPL's generic inner "Unexpected error" branch on CI.

import builtins
from unittest.mock import patch
from app.calculator_repl import calculator_repl

def _noop(*_a, **_k):
    return None

def _inputs():
    # 1) command
    yield "add"
    # 2) first number
    yield "2"
    # 3) second number
    yield "3"
    # 4) exit cleanly next loop
    yield "exit"
    # After script is done, ALWAYS raise EOFError so the REPL won't hang
    while True:
        raise EOFError()

@patch.object(builtins, "input")
def test_repl_unexpected_exception_branch(mock_input, monkeypatch, capsys):
    # Avoid FS I/O that can slow or block CI
    monkeypatch.setattr("app.calculator_repl.Calculator.save_history", _noop, raising=True)
    monkeypatch.setattr("app.calculator_repl.Calculator.load_history", _noop, raising=True)

    # Raise AFTER both operands are collected → hits inner generic except
    def _boom(*_a, **_k):
        raise RuntimeError("boom")
    monkeypatch.setattr("app.calculator_repl.Calculator.perform_operation", _boom, raising=True)

    # Feed a never-ending input generator that raises EOFError when exhausted
    it = _inputs()
    mock_input.side_effect = lambda _prompt="": next(it)

    calculator_repl()

    out = capsys.readouterr().out  # capture printed output
    assert "Unexpected error: boom" in out
    assert "Goodbye!" in out
