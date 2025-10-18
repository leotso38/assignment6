# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_history_branch_ci.py
# Notes: Force AutoSaveObserver.update to execute the save+log path.

import logging
from decimal import Decimal
from unittest.mock import Mock, patch
from app.history import AutoSaveObserver
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculation import Calculation             
from app.history import LoggingObserver 
from app.operations import Division, Modulus, IntegerDivision    

def test_autosave_observer_updates_and_logs(tmp_path):
    calc = Mock(spec=Calculator)
    calc.config = Mock(spec=CalculatorConfig)
    calc.config.auto_save = True

    obs = AutoSaveObserver(calc)
    with patch("app.history.logging.info") as lg:
        obs.update(Mock())  # any Calculation-like obj; not None

    calc.save_history.assert_called_once()
    lg.assert_any_call("History auto-saved")

def test_logging_observer_logs_line(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    # Patch logger to ensure the info call is recorded (no file I/O)
    logger_calls = []
    monkeypatch.setattr(logging, "info", lambda msg: logger_calls.append(msg))

    calc = Calculation("Addition", Decimal("1"), Decimal("2"))
    LoggingObserver().update(calc)

    assert any("Calculation performed:" in m for m in logger_calls)

  
def test_division_executes_and_hits_validate_branch():
    assert Division().execute(Decimal("6"), Decimal("2")) == Decimal("3")

def test_ops_extra_branches_for_ci():
    assert Modulus().execute(Decimal("-10"), Decimal("3")) == Decimal("2")
    assert IntegerDivision().execute(Decimal("-7"), Decimal("3")) == Decimal("-2")  