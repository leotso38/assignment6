# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_console_wrapper_and_unknown_kind.py
# Notes: Hit console wrapper's SystemExit and fmt() unknown-kind branch.

import sys
import importlib
from unittest.mock import patch
import types
import builtins
import pytest


def _reload_console_for_color(monkeypatch, *, env_color="1", has_colorama=True, is_tty=True):
    if "app.console" in sys.modules:
        del sys.modules["app.console"]

    monkeypatch.setenv("CALCULATOR_COLOR", env_color)

    if has_colorama:
        fake = types.SimpleNamespace(
            init=lambda autoreset=True: None,
            Fore=types.SimpleNamespace(CYAN="CYN", GREEN="GRN", YELLOW="YLW", RED="RED", MAGENTA="MAG"),
            Style=types.SimpleNamespace(BRIGHT="<B>", RESET_ALL="</B>"),
        )
        monkeypatch.setitem(sys.modules, "colorama", fake)
    else:
        class _Dummy: ...
        monkeypatch.setitem(sys.modules, "colorama", _Dummy())

    class _StdOut:
        def isatty(self): return is_tty
    monkeypatch.setattr("sys.stdout", _StdOut(), raising=False)

    import app.console as console
    importlib.reload(console)
    return console


def test_console_wrapper_raises_systemexit(monkeypatch):
    import app.console as console
    # Patch the core REPL to just return (console wrapper should then raise SystemExit)
    with patch("app.console.calculator_repl", autospec=True) as core:
        core.return_value = None
        with pytest.raises(SystemExit) as exc:
            console.calculator_repl()
        assert exc.value.code == 0


def test_fmt_unknown_kind_returns_original(monkeypatch):
    # Color enabled, but unknown kind -> mapping miss -> returns original string
    console = _reload_console_for_color(monkeypatch, env_color="1", has_colorama=True, is_tty=True)
    out = console.fmt("hello", "not-a-kind")
    assert out == "hello"

def test_console_wrapper_raises_systemexit(monkeypatch):
    import app.console as console
    # Patch the CORE that the wrapper imports inside the function
    with patch("app.calculator_repl.calculator_repl", autospec=True) as core:
        core.return_value = None
        with pytest.raises(SystemExit) as exc:
            console.calculator_repl()
        assert exc.value.code == 0
        core.assert_called_once()