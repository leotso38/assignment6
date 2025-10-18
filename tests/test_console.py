# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_console.py
# Notes: Consolidated console tests: color gating, unknown-kind passthrough,
#        wrapper SystemExit, and isatty() exception fallback.

import sys
import types
import importlib
from unittest.mock import patch
import pytest


def _reload_console(monkeypatch, *, env_color="1", has_colorama=True, is_tty=True, under_pytest=False, isatty_raises: bool = False):
    """Re-import app.console under controlled env to hit all branches."""
    if "app.console" in sys.modules:
        del sys.modules["app.console"]

    # env gating
    monkeypatch.setenv("CALCULATOR_COLOR", env_color)
    if under_pytest:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "x")
    else:
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    # simulate colorama presence/absence
    if has_colorama:
        fake = types.SimpleNamespace(
            init=lambda autoreset=True: None,
            Fore=types.SimpleNamespace(CYAN="CYN", GREEN="GRN", YELLOW="YLW", RED="RED", MAGENTA="MAG"),
            Style=types.SimpleNamespace(BRIGHT="<B>", RESET_ALL="</B>"),
        )
        monkeypatch.setitem(sys.modules, "colorama", fake)
    else:
        class _Dummy:  # import succeeds but lacks symbols -> fallback path
            pass
        monkeypatch.setitem(sys.modules, "colorama", _Dummy())

    # stdout stub
    class _StdOut:
        def isatty(self):
            if isatty_raises:
                raise OSError("tty check failed")
            return is_tty

    monkeypatch.setattr("sys.stdout", _StdOut(), raising=False)

    import app.console as console
    importlib.reload(console)
    return console


# ---------- color gating ----------

def test_color_enabled(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=True, under_pytest=False)
    assert c.fmt("Hello", "ok") != "Hello"

def test_no_color_env_off(monkeypatch):
    c = _reload_console(monkeypatch, env_color="0", has_colorama=True, is_tty=True, under_pytest=False)
    assert c.fmt("Hello", "ok") == "Hello"

def test_no_color_not_tty(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=False, under_pytest=False)
    assert c.fmt("Hello", "ok") == "Hello"

def test_no_color_under_pytest(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=True, under_pytest=True)
    assert c.fmt("Hello", "ok") == "Hello"

def test_no_color_colorama_missing(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=False, is_tty=True, under_pytest=False)
    assert c.fmt("Hello", "ok") == "Hello"

def test_isatty_exception_fallback(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=True, under_pytest=False, isatty_raises=True)
    assert c.fmt("Hello", "ok") == "Hello"

def test_prompt_text(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=True, under_pytest=False)
    out = c.prompt_text("Enter:")
    assert isinstance(out, str) and out


# ---------- unknown kind passthrough ----------

def test_fmt_unknown_kind_passthrough(monkeypatch):
    c = _reload_console(monkeypatch, env_color="1", has_colorama=True, is_tty=True, under_pytest=False)
    assert c.fmt("hello", "not-a-kind") == "hello"


# ---------- wrapper SystemExit (correct patch target) ----------

def test_console_wrapper_raises_systemexit_patch_core(monkeypatch):
    """Patch the *core* REPL and call the wrapper; wrapper must raise SystemExit(0)."""
    import app.console as console
    with patch("app.calculator_repl.calculator_repl", autospec=True) as core:
        core.return_value = None
        with pytest.raises(SystemExit) as exc:
            console.calculator_repl()
        assert exc.value.code == 0
        core.assert_called_once()
