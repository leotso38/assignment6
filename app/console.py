"""
Author: Leo Tso
Class: IS601
Date: 2025-10-12
"""

import os
import sys
from typing import Literal

try:
    from colorama import init as colorama_init, Fore, Style
except Exception:  # pragma: no cover
    # Fallback if colorama isn't installed; return plain text
    Fore = Style = type("Dummy", (), {"RESET_ALL": "", "RED": "", "GREEN": "", "YELLOW": "", "CYAN": "", "BRIGHT": ""})()
    def colorama_init(*_args, **_kwargs):  # type: ignore
        pass

# Policy:
# - Default AUTO: enable colors only when stdout is a TTY and not running under pytest.
# - FORCE_ON: force enable (even in non-tty).
# - OFF: disable (always plain text).
ColorMode = Literal["AUTO", "FORCE_ON", "OFF"]

def _detect_mode() -> ColorMode:
    env = os.getenv("CALCULATOR_COLOR", "AUTO").upper()
    if env in {"FORCE_ON", "ON", "TRUE", "1", "YES"}:
        return "FORCE_ON"
    if env in {"OFF", "FALSE", "0", "NO"}:
        return "OFF"
    return "AUTO"

_MODE: ColorMode = _detect_mode()

# Initialize colorama once (safe on Windows; harmless elsewhere)
colorama_init(autoreset=True)

def colors_enabled() -> bool:
    if _MODE == "FORCE_ON":
        return True
    if _MODE == "OFF":
        return False
    # AUTO:
    if os.getenv("PYTEST_CURRENT_TEST"):  # pytest sets this
        return False
    return sys.stdout.isatty()

def _apply(s: str, prefix: str) -> str:
    if not colors_enabled():
        return s
    return f"{prefix}{s}{Style.RESET_ALL}"

def c_info(s: str) -> str:
    """Informational text (cyan)."""
    return _apply(s, f"{Fore.CYAN}")

def c_success(s: str) -> str:
    """Success text (green)."""
    return _apply(s, f"{Fore.GREEN}{Style.BRIGHT}")

def c_warn(s: str) -> str:
    """Warnings (yellow)."""
    return _apply(s, f"{Fore.YELLOW}{Style.BRIGHT}")

def c_error(s: str) -> str:
    """Errors (red)."""
    return _apply(s, f"{Fore.RED}{Style.BRIGHT}")

def c_heading(s: str) -> str:
    """Headings (bright)."""
    return _apply(s, f"{Style.BRIGHT}")

def c_prompt(s: str) -> str:
    """Prompts (cyan, bright)."""
    return _apply(s, f"{Fore.CYAN}{Style.BRIGHT}")
