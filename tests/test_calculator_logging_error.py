# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_calculator_logging_error.py
# Notes: Hit Calculator._setup_logging exception path (print + raise).

import pytest
from unittest.mock import patch, PropertyMock
from pathlib import Path

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig


def test_setup_logging_error_branch(tmp_path, monkeypatch):
    cfg = CalculatorConfig(base_dir=tmp_path)

    # Keep file paths sane under tmp
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as p1, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as p2:
        p1.return_value = tmp_path / "logs"
        p2.return_value = tmp_path / "logs/calculator.log"

        # Force logging.basicConfig to throw
        with patch("app.calculator.logging.basicConfig", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError, match="boom"):
                Calculator(config=cfg)
