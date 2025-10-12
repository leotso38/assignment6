import builtins
import pytest
from app.calculator_repl import calculator_repl

def test_repl_help_exit(monkeypatch, capsys):
    inputs = iter(["help", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    calculator_repl()
    out = capsys.readouterr().out.lower()
    assert "available commands" in out
    assert "goodbye" in out

def test_repl_add(monkeypatch, capsys):
    inputs = iter(["add", "2", "3", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    calculator_repl()
    out = capsys.readouterr().out.lower()
    assert "result" in out
