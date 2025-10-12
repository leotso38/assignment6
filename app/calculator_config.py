"""
Author: Leo Tso
Class: IS601
Date: 2025-10-12
"""

from dataclasses import dataclass
from decimal import Decimal
from numbers import Number
from pathlib import Path
import os
from typing import Optional

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


def get_project_root() -> Path:
    """Return the project root (two levels up from this file)."""
    return Path(__file__).parent.parent.resolve()


def _resolve_env_path(var_name: str, default: Path) -> Path:
    """
    Read a path-like env var, expand ~ and relative paths against project root,
    and return an absolute resolved Path. Falls back to `default` if unset.
    """
    raw = os.getenv(var_name)
    if not raw:
        return default.resolve()
    p = Path(os.path.expanduser(raw))
    if not p.is_absolute():
        p = (get_project_root() / p).resolve()
    return p


# Load .env once, from the project root if present (no override of real env)
# This lets shell-provided env vars win over .env.
load_dotenv(dotenv_path=get_project_root() / ".env", override=False)


@dataclass
class CalculatorConfig:
    """
    Configuration for the calculator. Values can come from:
      1) Explicit constructor args (highest priority)
      2) Environment variables / .env
      3) Code defaults

    Supported env vars:
      - CALCULATOR_BASE_DIR
      - CALCULATOR_LOG_DIR
      - CALCULATOR_HISTORY_DIR
      - CALCULATOR_HISTORY_FILE
      - CALCULATOR_LOG_FILE
      - CALCULATOR_MAX_HISTORY_SIZE
      - CALCULATOR_AUTO_SAVE
      - CALCULATOR_PRECISION
      - CALCULATOR_MAX_INPUT_VALUE
      - CALCULATOR_DEFAULT_ENCODING
    """

    def __init__(
        self,
        base_dir: Optional[Path] = None,
        max_history_size: Optional[int] = None,
        auto_save: Optional[bool] = None,
        precision: Optional[int] = None,
        max_input_value: Optional[Number] = None,
        default_encoding: Optional[str] = None,
    ):
        project_root = get_project_root()

        # Base directory (used only as a fallback if more specific dirs are not provided)
        env_base = os.getenv("CALCULATOR_BASE_DIR")
        if base_dir is not None:
            self.base_dir = Path(base_dir).resolve()
        elif env_base:
            self.base_dir = _resolve_env_path("CALCULATOR_BASE_DIR", project_root)
        else:
            self.base_dir = project_root

        # Number-ish configs
        self.max_history_size = (
            int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000"))
            if max_history_size is None
            else int(max_history_size)
        )

        auto_save_env = os.getenv("CALCULATOR_AUTO_SAVE", "true").strip().lower()
        self.auto_save = (
            (auto_save_env in {"true", "1", "yes", "y"})
            if auto_save is None
            else bool(auto_save)
        )

        self.precision = (
            int(os.getenv("CALCULATOR_PRECISION", "10"))
            if precision is None
            else int(precision)
        )

        self.max_input_value = (
            Decimal(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e999"))
            if max_input_value is None
            else Decimal(max_input_value)
        )

        self.default_encoding = (
            os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")
            if default_encoding is None
            else default_encoding
        )

    # ---- Paths (derived) -------------------------------------------------

    @property
    def log_dir(self) -> Path:
        """
        Directory for log files.
        Env: CALCULATOR_LOG_DIR
        Default: <base_dir>/logs
        """
        fallback = (self.base_dir / "logs").resolve()
        return _resolve_env_path("CALCULATOR_LOG_DIR", fallback)

    @property
    def history_dir(self) -> Path:
        """
        Directory for history files.
        Env: CALCULATOR_HISTORY_DIR
        Default: <base_dir>/history
        """
        fallback = (self.base_dir / "history").resolve()
        return _resolve_env_path("CALCULATOR_HISTORY_DIR", fallback)

    @property
    def history_file(self) -> Path:
        """
        CSV file path for history.
        Env: CALCULATOR_HISTORY_FILE
        Default: <history_dir>/calculator_history.csv
        """
        env_value = os.getenv("CALCULATOR_HISTORY_FILE")
        if env_value:
            return _resolve_env_path("CALCULATOR_HISTORY_FILE", self.history_dir / "calculator_history.csv")
        return (self.history_dir / "calculator_history.csv").resolve()

    @property
    def log_file(self) -> Path:
        """
        Log file path.
        Env: CALCULATOR_LOG_FILE
        Default: <log_dir>/calculator.log
        """
        env_value = os.getenv("CALCULATOR_LOG_FILE")
        if env_value:
            return _resolve_env_path("CALCULATOR_LOG_FILE", self.log_dir / "calculator.log")
        return (self.log_dir / "calculator.log").resolve()

    # ---- Validation ------------------------------------------------------

    def validate(self) -> None:
        if self.max_history_size <= 0:
            raise ConfigurationError("max_history_size must be positive")
        if self.precision <= 0:
            raise ConfigurationError("precision must be positive")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive")
