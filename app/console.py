# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: app/console.py
# Notes: CLI/console utilities for colorized REPL output and safe SystemExit wrapper.

"""
Console wrapper + color formatting helpers.

- Exports `calculator_repl()` that runs the REPL core then raises SystemExit (for CLI/tests).
- Enables color output only when all are true:
    * CALCULATOR_COLOR = 1/true/yes
    * colorama available
    * stdout is a real TTY
    * not under pytest
"""

from __future__ import annotations
import os
import sys

# ---------- environment flag (opt-in) ----------
_ENV_WANTS_COLOR = os.getenv("CALCULATOR_COLOR", "0").strip().lower() in {"1", "true", "yes"}

# ---------- optional colorama import ----------
_HAS_COLORAMA = False
try:
    from colorama import init as _cinit, Fore, Style  # type: ignore
    _cinit(autoreset=True)
    _HAS_COLORAMA = True
except Exception:  # pragma: no cover
    # graceful fallback when colorama is missing
    class _NoStyle:  # type: ignore
        RESET_ALL = ""
        BRIGHT = ""

    class _NoFore:  # type: ignore
        CYAN = ""
        GREEN = ""
        YELLOW = ""
        RED = ""
        MAGENTA = ""

    Style = _NoStyle()  # type: ignore
    Fore = _NoFore()    # type: ignore
    _HAS_COLORAMA = False


def _color_enabled() -> bool:
    """Enable color only when explicitly requested, colorama present, real TTY, and not pytest."""
    if not _ENV_WANTS_COLOR or not _HAS_COLORAMA:
        return False
    if "PYTEST_CURRENT_TEST" in os.environ:
        return False
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def fmt(msg: str, kind: str | None = None) -> str:
    """Return colorized message string if conditions allow."""
    if not _color_enabled():
        return msg
    color = {
        "heading": Fore.MAGENTA,
        "info": Fore.CYAN,
        "ok": Fore.GREEN,
        "warn": Fore.YELLOW,
        "error": Fore.RED,
        "prompt": Fore.CYAN,
    }.get(kind or "", "")
    return f"{Style.BRIGHT}{color}{msg}{Style.RESET_ALL}" if color else msg


def prompt_text(text: str) -> str:
    """Return colorized prompt label if color enabled."""
    return fmt(text, "prompt")


def calculator_repl() -> None:
    """
    Public entrypoint for REPL from console/CLI.

    Invokes the REPL core function, then exits with SystemExit(0)
    to satisfy test and CLI behavior expectations.
    """
    from app.calculator_repl import calculator_repl as _core_repl
    _core_repl()
    raise SystemExit(0)


__all__ = ["fmt", "prompt_text", "calculator_repl"]
