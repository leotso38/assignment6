# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_history.py
# Notes: Consolidated observer tests (LoggingObserver, AutoSaveObserver) plus a few
#        quick operation branches to keep CI coverage stable.

import logging
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from app.calculation import Calculation
from app.history import LoggingObserver, AutoSaveObserver
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import Division, Modulus, IntegerDivision


# ---------- LoggingObserver ----------

@patch("logging.info")
def test_logging_observer_logs_calculation(logging_info_mock):
    # concise “happy path” check via patch
    calc = Mock(spec=Calculation)
    calc.operation, calc.operand1, calc.operand2, calc.result = "addition", 5, 3, 8

    LoggingObserver().update(calc)
    logging_info_mock.assert_called_once_with(
        "Calculation performed: addition (5, 3) = 8"
    )


def test_logging_observer_no_calculation():
    # explicit error path
    with pytest.raises(AttributeError):
        LoggingObserver().update(None)


def test_logging_observer_logs_line(monkeypatch, caplog):
    # exercise path without using patch() helper; capture calls directly
    caplog.set_level(logging.INFO)
    captured = []
    monkeypatch.setattr(logging, "info", lambda msg: captured.append(msg))

    calc = Calculation("Addition", Decimal("1"), Decimal("2"))
    LoggingObserver().update(calc)

    assert any("Calculation performed:" in m for m in captured)


# ---------- AutoSaveObserver ----------

def test_autosave_observer_triggers_save():
    # auto_save=True → save_history() is called
    calculator = Mock(spec=Calculator)
    calculator.config = Mock(spec=CalculatorConfig)
    calculator.config.auto_save = True

    AutoSaveObserver(calculator).update(Mock(spec=Calculation))
    calculator.save_history.assert_called_once()


@patch("logging.info")
def test_autosave_observer_logs_autosave(logging_info_mock):
    # logs after successful auto-save
    calculator = Mock(spec=Calculator)
    calculator.config = Mock(spec=CalculatorConfig)
    calculator.config.auto_save = True

    AutoSaveObserver(calculator).update(Mock(spec=Calculation))
    logging_info_mock.assert_called_once_with("History auto-saved")


def test_autosave_observer_does_not_trigger_save_when_disabled():
    # auto_save=False → no save
    calculator = Mock(spec=Calculator)
    calculator.config = Mock(spec=CalculatorConfig)
    calculator.config.auto_save = False

    AutoSaveObserver(calculator).update(Mock(spec=Calculation))
    calculator.save_history.assert_not_called()


def test_autosave_observer_invalid_calculator():
    # ctor validation
    with pytest.raises(TypeError):
        AutoSaveObserver(None)


def test_autosave_observer_no_calculation():
    # update(None) → error path
    calculator = Mock(spec=Calculator)
    calculator.config = Mock(spec=CalculatorConfig)
    calculator.config.auto_save = True

    with pytest.raises(AttributeError):
        AutoSaveObserver(calculator).update(None)


def test_autosave_observer_updates_and_logs(tmp_path):
    # full path: save_history() called and info logged
    calculator = Mock(spec=Calculator)
    calculator.config = Mock(spec=CalculatorConfig)
    calculator.config.auto_save = True

    obs = AutoSaveObserver(calculator)
    with patch("app.history.logging.info") as lg:
        obs.update(Mock(spec=Calculation))

    calculator.save_history.assert_called_once()
    lg.assert_any_call("History auto-saved")


# ---------- Small op-branch nudges (keep CI % healthy) ----------

def test_division_executes_and_hits_validate_branch():
    assert Division().execute(Decimal("6"), Decimal("2")) == Decimal("3")


def test_ops_extra_branches_for_ci():
    assert Modulus().execute(Decimal("-10"), Decimal("3")) == Decimal("2")
    assert IntegerDivision().execute(Decimal("-7"), Decimal("3")) == Decimal("-2")
