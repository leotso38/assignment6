# tests/test_repl_unexpected_ci.py
# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# Notes: Hit the REPL's generic inner-loop "Unexpected error" branch, without real I/O.

import builtins
from unittest.mock import patch
from app.calculator_repl import calculator_repl

def _noop(*_a, **_k):  # no-op for history methods
    return None

@patch.object(builtins, "print")
def test_repl_unexpected_exception_branch(mock_print, monkeypatch):
    # 1) Avoid filesystem touches that can slow/block CI
    monkeypatch.setattr("app.calculator_repl.Calculator.save_history", _noop, raising=True)
    monkeypatch.setattr("app.calculator_repl.Calculator.load_history", _noop, raising=True)

    # 2) Force an unexpected exception immediately after reading 'add'
    def _boom(*_a, **_k):
        raise RuntimeError("boom")
    monkeypatch.setattr("app.calculator_repl.OperationFactory.create_operation", _boom, raising=True)

    # 3) Provide exactly two inputs: trigger the error, then cleanly exit
    with patch.object(builtins, "input", side_effect=["add", "exit"]):
        calculator_repl()

    # 4) Assert we hit the branch & exited
    out = [str(c.args[0]) for c in mock_print.call_args_list if c.args]
    assert any("Unexpected error: boom" in s for s in out)
    assert any("Goodbye!" in s for s in out)
