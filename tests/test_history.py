# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_history.py
# Notes: Unit tests for LoggingObserver and AutoSaveObserver behavior, including edge cases.

import pytest
from unittest.mock import Mock, patch
from app.calculation import Calculation
from app.history import LoggingObserver, AutoSaveObserver
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig

# ---------- Mock setup ----------
calculation_mock = Mock(spec=Calculation)
calculation_mock.operation = "addition"
calculation_mock.operand1 = 5
calculation_mock.operand2 = 3
calculation_mock.result = 8


# ---------- LoggingObserver ----------

@patch("logging.info")
def test_logging_observer_logs_calculation(logging_info_mock):
    observer = LoggingObserver()
    observer.update(calculation_mock)
    logging_info_mock.assert_called_once_with(
        "Calculation performed: addition (5, 3) = 8"
    )


def test_logging_observer_no_calculation():
    observer = LoggingObserver()
    with pytest.raises(AttributeError):
        observer.update(None)


# ---------- AutoSaveObserver ----------

def test_autosave_observer_triggers_save():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)

    observer.update(calculation_mock)
    calculator_mock.save_history.assert_called_once()


@patch("logging.info")
def test_autosave_observer_logs_autosave(logging_info_mock):
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)

    observer.update(calculation_mock)
    logging_info_mock.assert_called_once_with("History auto-saved")


def test_autosave_observer_does_not_trigger_save_when_disabled():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = False
    observer = AutoSaveObserver(calculator_mock)

    observer.update(calculation_mock)
    calculator_mock.save_history.assert_not_called()


# ---------- Edge / negative cases ----------

def test_autosave_observer_invalid_calculator():
    with pytest.raises(TypeError):
        AutoSaveObserver(None)


def test_autosave_observer_no_calculation():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)

    with pytest.raises(AttributeError):
        observer.update(None)
