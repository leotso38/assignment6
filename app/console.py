"""
Console wrapper and tiny color helpers.

- `calculator_repl()` here **calls** the core REPL and then **raises SystemExit(0)**
  so tests that import from `app.console` see a real CLI-style exit.
- Colors are optional: set CALCULATOR_COLOR=1 (or 'true'/'yes') to enable if Colorama
  is installed; otherwise output stays plain (tests compare raw strings).
"""

from __future__ import annotations
import os

# --- Optional Colorama support controlled by env flag ------------------------
_USE_COLOR = os.getenv("CALCULATOR_COLOR", "0").strip().lower() in {"1", "true", "yes"}
_HAS_COLOR = False
try:  # pragma: no cover - availability depends on environment
    from colorama import init as _cinit, Fore, Style  # type: ignore
    _cinit(autoreset=True)
    _HAS_COLOR = True
except Exception:  # pragma: no cover - defensive fallback
    class _NoStyle:
        RESET_ALL = ""
        BRIGHT = ""
    class _NoFore:
        CYAN = ""
        GREEN = ""
        YELLOW = ""
        RED = ""
        MAGENTA = ""
    Style = _NoStyle()      # type: ignore
    Fore = _NoFore()        # type: ignore
    _HAS_COLOR = False


def fmt(msg: str, kind: str | None = None) -> str:
    """Return `msg` colorized if enabled, otherwise unchanged."""
    if not (_USE_COLOR and _HAS_COLOR):
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
    """Build a prompt label (no I/O), colorized if enabled."""
    return fmt(text, "prompt")


def color_status() -> dict:
    """Runtime flags to verify color state without printing control codes."""
    return {"use_color": _USE_COLOR, "has_color": _HAS_COLOR}


def calculator_repl() -> None:
    """
    Console-facing entrypoint used by tests importing from `app.console`.
    Calls the core REPL (which RETURNS) and then raises SystemExit(0).
    """
    from app.calculator_repl import calculator_repl as _core_repl
    _core_repl()
    raise SystemExit(0)


__all__ = ["fmt", "prompt_text", "color_status", "calculator_repl"]
