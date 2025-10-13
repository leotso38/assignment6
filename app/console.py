"""
Console wrapper + tiny color helpers.

- Export `calculator_repl()` that runs the core REPL and then raises SystemExit,
  matching tests that expect a CLI-style exit.
- Color output is enabled only when ALL are true:
    * CALCULATOR_COLOR is set to 1/true/yes
    * colorama is installed
    * running in a real TTY (stdout isatty)
    * NOT running under pytest (PYTEST_CURRENT_TEST unset)
  Otherwise output is plain (so tests comparing raw strings pass).
"""

from __future__ import annotations
import os
import sys

# ---- environment flag (opt-in) ------------------------------------------------
_ENV_WANTS_COLOR = os.getenv("CALCULATOR_COLOR", "0").strip().lower() in {"1", "true", "yes"}

# ---- best-effort import of colorama (graceful fallback) -----------------------
_HAS_COLORAMA = False
try:
    from colorama import init as _cinit, Fore, Style  # type: ignore
    _cinit(autoreset=True)
    _HAS_COLORAMA = True
except Exception:  # pragma: no cover
    class _NoStyle:  # type: ignore
        RESET_ALL = ""
        BRIGHT = ""
    class _NoFore:  # type: ignore
        CYAN = ""
        GREEN = ""
        YELLOW = ""
        RED = ""
        MAGENTA = ""
    Style = _NoStyle()   # type: ignore
    Fore  = _NoFore()    # type: ignore
    _HAS_COLORAMA = False


def _color_enabled() -> bool:
    """Color only if explicitly requested, colorama available, real TTY, and not pytest."""
    if not _ENV_WANTS_COLOR:
        return False
    if not _HAS_COLORAMA:
        return False
    # Avoid coloring under pytest so tests see plain strings
    if "PYTEST_CURRENT_TEST" in os.environ:
        return False
    # Only color when printing to a real terminal
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def fmt(msg: str, kind: str | None = None) -> str:
    """Return colorized string when enabled; otherwise unchanged."""
    if not _color_enabled():
        return msg
    color = {
        "heading":  Fore.MAGENTA,
        "info":     Fore.CYAN,
        "ok":       Fore.GREEN,
        "warn":     Fore.YELLOW,
        "error":    Fore.RED,
        "prompt":   Fore.CYAN,
    }.get(kind or "", "")
    return f"{Style.BRIGHT}{color}{msg}{Style.RESET_ALL}" if color else msg


def prompt_text(text: str) -> str:
    """Build a prompt label (no input yet), colorized if enabled."""
    return fmt(text, "prompt")


def calculator_repl() -> None:
    """
    Console-facing entrypoint used by tests importing from `app.console`.
    Calls the core REPL (which returns) and then raises SystemExit(0).
    """
    from app.calculator_repl import calculator_repl as _core_repl
    _core_repl()
    raise SystemExit(0)


__all__ = ["fmt", "prompt_text", "calculator_repl"]
