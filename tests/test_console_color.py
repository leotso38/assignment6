# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_console_color.py
# Notes: Exercise color gating in app.console (env, colorama present/absent, TTY, pytest guard).

import sys
import types
import importlib
from unittest.mock import patch


def _reload_console(monkeypatch, *, env_color="1", has_colorama=True, is_tty=True, under_pytest=False):
    # fresh import each time
    if "app.console" in sys.modules:
        del sys.modules["app.console"]

    monkeypatch.setenv("CALCULATOR_COLOR", env_color)
    if under_pytest:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "x")
    else:
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    # simulate presence/absence of colorama
    if has_colorama:
        fake = types.SimpleNamespace(
            init=lambda autoreset=True: None,
            Fore=types.SimpleNamespace(CYAN="CYN", GREEN="GRN", YELLOW="YLW", RED="RED", MAGENTA="MAG"),
            Style=types.SimpleNamespace(BRIGHT="<B>", RESET_ALL="</B>"),
        )
        monkeypatch.setitem(sys.modules, "colorama", fake)
    else:
        # ensure "from colorama import ..." fails to import expected attrs -> fallback no-color branch
        class _DummyColoramaModule:
            pass
        monkeypatch.setitem(sys.modules, "colorama", _DummyColoramaModule())

    class _StdOut:
        def isatty(self): return is_tty
    monkeypatch.setattr("sys.stdout", _StdOut(), raising=False)

    import app.console as console
    importlib.reload(console)
    return console


def test_console_color_enabled(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=True, under_pytest=False)
    out = c.fmt("Hello", "ok")
    assert out != "Hello"  # colored


def test_console_no_color_when_env_off(monkeypatch):
    c = _reload_console(monkeypatch, env_color="0", has_colorama=True, is_tty=True, under_pytest=False)
    assert c.fmt("Hello", "ok") == "Hello"


def test_console_no_color_without_tty(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=False, under_pytest=False)
    assert c.fmt("Hello", "ok") == "Hello"


def test_console_no_color_under_pytest(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=True, under_pytest=True)
    assert c.fmt("Hello", "ok") == "Hello"


def test_console_no_color_when_colorama_missing(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=False, is_tty=True, under_pytest=False)
    assert c.fmt("Hello", "ok") == "Hello"


def test_prompt_text(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=True, under_pytest=False)
    out = c.prompt_text("Enter:")
    assert isinstance(out, str) and out
