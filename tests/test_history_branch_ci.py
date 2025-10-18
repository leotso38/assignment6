# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_history_branch_ci.py
# Notes: Force AutoSaveObserver.update to execute the save+log path.

from unittest.mock import Mock, patch
from app.history import AutoSaveObserver
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig

def test_autosave_observer_updates_and_logs(tmp_path):
    calc = Mock(spec=Calculator)
    calc.config = Mock(spec=CalculatorConfig)
    calc.config.auto_save = True

    obs = AutoSaveObserver(calc)
    with patch("app.history.logging.info") as lg:
        obs.update(Mock())  # any Calculation-like obj; not None

    calc.save_history.assert_called_once()
    lg.assert_any_call("History auto-saved")
