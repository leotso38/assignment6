# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_console_isatty_exception.py
# Notes: Cover app.console._color_enabled() exception branch when sys.stdout.isatty() raises.

import sys
import importlib
import types

def _reload_console_with_bad_isatty(monkeypatch):
    # force env flag ON so we actually reach isatty()
    monkeypatch.setenv("CALCULATOR_COLOR", "1")

    # provide a minimal colorama so earlier checks pass
    fake = types.SimpleNamespace(
        init=lambda autoreset=True: None,
        Fore=types.SimpleNamespace(CYAN="C", GREEN="G", YELLOW="Y", RED="R", MAGENTA="M"),
        Style=types.SimpleNamespace(BRIGHT="B", RESET_ALL="X"),
    )
    monkeypatch.setitem(sys.modules, "colorama", fake)

    # make sys.stdout.isatty() raise -> _color_enabled should catch and return False
    class _StdOut:
        def isatty(self):
            raise RuntimeError("tty boom")
    monkeypatch.setattr("sys.stdout", _StdOut(), raising=False)

    if "app.console" in sys.modules:
        del sys.modules["app.console"]
    import app.console as console
    importlib.reload(console)
    return console

def test_fmt_falls_back_when_isatty_raises(monkeypatch):
    console = _reload_console_with_bad_isatty(monkeypatch)
    assert console.fmt("Hello", "ok") == "Hello"
