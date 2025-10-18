# Author: Leo Tso
# Date: 2025-10-19
# Class: IS601
# File: tests/test_calculator.py


import builtins
import datetime
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import PropertyMock, patch

import pandas as pd
import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import calculator_repl
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, HistoryObserver, LoggingObserver
from app.operations import Addition, OperationFactory


# ---------- Helpers / fixtures ----------

class _SpyObserver(HistoryObserver):
    """Capture update() notifications."""
    def __init__(self):
        self.seen = []
    def update(self, calculation):
        self.seen.append(str(calculation))


@pytest.fixture
def calc_tmp():
    """Calculator with temp-scoped files (logs/history under a temp dir)."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        cfg = CalculatorConfig(base_dir=temp_path)
        # Force all file paths into the temp area
        with patch.object(CalculatorConfig, "log_dir", new_callable=PropertyMock) as p1, \
             patch.object(CalculatorConfig, "log_file", new_callable=PropertyMock) as p2, \
             patch.object(CalculatorConfig, "history_dir", new_callable=PropertyMock) as p3, \
             patch.object(CalculatorConfig, "history_file", new_callable=PropertyMock) as p4:
            p1.return_value = temp_path / "logs"
            p2.return_value = temp_path / "logs/calculator.log"
            p3.return_value = temp_path / "history"
            p4.return_value = temp_path / "history/calculator_history.csv"
            c = Calculator(config=cfg)
            c.clear_history()
            yield c


def _mk_calc(tmp_path: Path, **overrides) -> Calculator:
    """New Calculator rooted at tmp_path with clean history."""
    cfg = CalculatorConfig(
        base_dir=tmp_path,
        max_history_size=overrides.get("max_history_size", 10),
    )
    c = Calculator(config=cfg)
    c.clear_history()
    return c


# ---------- Core object lifecycle ----------

def test_calculator_initialization(calc_tmp):
    assert calc_tmp.history == []
    assert calc_tmp.undo_stack == []
    assert calc_tmp.redo_stack == []
    assert calc_tmp.operation_strategy is None


@patch("app.calculator.logging.info")
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, "log_dir", new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, "log_file", new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path("/tmp/logs")
        mock_log_file.return_value = Path("/tmp/logs/calculator.log")
        Calculator(CalculatorConfig())  # triggers logging in __init__
        logging_info_mock.assert_any_call("Calculator initialized with configuration")


def test_add_remove_observer(calc_tmp):
    observer = LoggingObserver()
    calc_tmp.add_observer(observer)
    assert observer in calc_tmp.observers
    calc_tmp.remove_observer(observer)
    assert observer not in calc_tmp.observers


def test_set_operation(calc_tmp):
    op = OperationFactory.create_operation("add")
    calc_tmp.set_operation(op)
    assert calc_tmp.operation_strategy == op


# ---------- perform_operation paths ----------

def test_perform_operation_addition(calc_tmp):
    op = OperationFactory.create_operation("add")
    calc_tmp.set_operation(op)
    result = calc_tmp.perform_operation(2, 3)
    assert result == Decimal("5")


def test_perform_operation_validation_error(calc_tmp):
    calc_tmp.set_operation(OperationFactory.create_operation("add"))
    with pytest.raises(ValidationError):
        calc_tmp.perform_operation("invalid", 3)


def test_perform_operation_no_operation_set(calc_tmp):
    with pytest.raises(OperationError, match="No operation set"):
        calc_tmp.perform_operation(2, 3)


def test_perform_operation_wraps_generic_exception(tmp_path):
    """Merged from test_calculator_opwrap.py — exercise generic except -> OperationError."""
    class _BoomOp:
        def __str__(self) -> str:
            return "Addition"  # name is irrelevant for the wrapper
        def execute(self, a: Decimal, b: Decimal):
            raise RuntimeError("boom")

    c = _mk_calc(tmp_path)
    c.set_operation(_BoomOp())
    with pytest.raises(OperationError, match="Operation failed: boom"):
        c.perform_operation("1", "2")


# ---------- History I/O ----------

@patch("app.calculator.pd.DataFrame.to_csv")
def test_save_history_calls_to_csv(mock_to_csv, calc_tmp):
    op = OperationFactory.create_operation("add")
    calc_tmp.set_operation(op)
    calc_tmp.perform_operation(2, 3)
    calc_tmp.save_history()
    mock_to_csv.assert_called_once()


@patch("app.calculator.pd.read_csv")
@patch("app.calculator.Path.exists", return_value=True)
def test_load_history_basic(_mock_exists, mock_read_csv, calc_tmp):
    mock_read_csv.return_value = pd.DataFrame({
        "operation": ["Addition"],
        "operand1": ["2"],
        "operand2": ["3"],
        "result": ["5"],
        "timestamp": [datetime.datetime.now().isoformat()],
    })
    calc_tmp.load_history()
    assert len(calc_tmp.history) == 1
    row = calc_tmp.history[0]
    assert row.operation == "Addition"
    assert row.operand1 == Decimal("2")
    assert row.operand2 == Decimal("3")
    assert row.result == Decimal("5")


def test_save_history_writes_even_when_empty(tmp_path):
    c = _mk_calc(tmp_path)
    c.save_history()
    assert c.config.history_file.exists()
    df = pd.read_csv(c.config.history_file)
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]
    assert df.empty


def test_save_history_wraps_errors(tmp_path, monkeypatch):
    c = _mk_calc(tmp_path)
    c.set_operation(Addition())
    c.perform_operation("5", "6")

    def boom(*_args, **_kwargs):
        raise OSError("disk full")
    monkeypatch.setattr(pd.DataFrame, "to_csv", boom)

    with pytest.raises(OperationError, match="Failed to save history:"):
        c.save_history()


def test_load_history_wraps_errors(tmp_path, monkeypatch):
    c = _mk_calc(tmp_path)
    c.config.history_dir.mkdir(parents=True, exist_ok=True)
    c.config.history_file.write_text("operation,operand1,operand2,result,timestamp\n")

    def kaboom(*_args, **_kwargs):
        raise ValueError("corrupt csv")
    monkeypatch.setattr(pd, "read_csv", kaboom)

    with pytest.raises(OperationError, match="Failed to load history:"):
        c.load_history()


def test_load_history_parses_valid_rows(tmp_path):
    c = _mk_calc(tmp_path)
    c.set_operation(Addition())
    c.perform_operation("2", "8")
    c.save_history()

    c2 = _mk_calc(tmp_path)
    c2.load_history()
    assert c2.history
    assert "Addition(2, 8) = 10" in [str(h) for h in c2.history]


# ---------- History list / undo-redo ----------

def test_get_history_dataframe_and_show_history(tmp_path):
    c = _mk_calc(tmp_path)
    c.set_operation(Addition())
    c.perform_operation("2", "3")

    df = c.get_history_dataframe()
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]
    assert len(df) == 1

    hist_lines = c.show_history()
    assert "Addition(2, 3) = 5" in hist_lines[0]


def test_clear_history(calc_tmp):
    op = OperationFactory.create_operation("add")
    calc_tmp.set_operation(op)
    calc_tmp.perform_operation(2, 3)
    calc_tmp.clear_history()
    assert calc_tmp.history == []
    assert calc_tmp.undo_stack == []
    assert calc_tmp.redo_stack == []


def test_undo_redo_empty_paths(tmp_path):
    c = _mk_calc(tmp_path)
    assert c.undo() is False
    assert c.redo() is False


def test_undo_then_redo_roundtrip(tmp_path):
    c = _mk_calc(tmp_path)
    c.set_operation(Addition())
    c.perform_operation("1", "2")
    c.perform_operation("3", "4")

    assert c.undo() is True
    assert c.redo() is True
    assert len(c.history) == 2
    assert str(c.history[-1]) == "Addition(3, 4) = 7"


# ---------- REPL behavior (via console wrapper) ----------

@patch.object(builtins, "input", side_effect=["exit"])
@patch.object(builtins, "print")
def test_calculator_repl_exit(mock_print, _mock_input):
    with patch("app.calculator.Calculator.save_history") as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")


@patch.object(builtins, "input", side_effect=["help", "exit"])
@patch.object(builtins, "print")
def test_calculator_repl_help(mock_print, _mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")


@patch.object(builtins, "input", side_effect=["add", "2", "3", "exit"])
@patch.object(builtins, "print")
def test_calculator_repl_addition(mock_print, _mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")
