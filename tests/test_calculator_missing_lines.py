import builtins
import json
import logging
import os
import pandas as pd
import pytest
from decimal import Decimal
from pathlib import Path

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import Addition
from app.exceptions import OperationError, ValidationError


# tests/test_calculator_missing_lines.py

def test_ctor_handles_load_history_failure(tmp_path, monkeypatch):
    # Force __init__ → load_history() to raise and ensure ctor does NOT raise
    def boom(self):
        raise RuntimeError("load broke")
    monkeypatch.setattr(Calculator, "load_history", boom, raising=True)

    # If the except-path is executed correctly, this will not raise.
    _ = Calculator(config=CalculatorConfig(base_dir=tmp_path))



# --- 103–106: logging.basicConfig fails during __init__ ---
def test_ctor_logging_setup_failure_raises(tmp_path, monkeypatch):
    def bad_basicConfig(*a, **k): raise RuntimeError("log cfg fail")
    monkeypatch.setattr(logging, "basicConfig", bad_basicConfig)
    with pytest.raises(RuntimeError, match="log cfg fail"):
        Calculator(config=CalculatorConfig(base_dir=tmp_path))


# Utility: a calculator bound to tmp dir, with real Addition op
@pytest.fixture
def calc(tmp_path):
    c = Calculator(config=CalculatorConfig(base_dir=tmp_path))
    c.set_operation(Addition())
    return c


# --- 219: prune when len(history) > max_history_size ---
def test_history_pruned_when_exceeding_max(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path, max_history_size=1)
    c = Calculator(config=cfg)
    c.set_operation(Addition())
    c.perform_operation("1", "1")  # first entry
    c.perform_operation("2", "2")  # triggers prune (line 219)
    # Only the latest remains
    assert len(c.history) == 1
    h = c.history[0]
    assert h.operand1 == Decimal("2") and h.operand2 == Decimal("2")


# --- 230–233: generic Exception from operation -> OperationError path ---
def test_operation_generic_failure_bubbles_as_operationerror(tmp_path):
    from app.operations import Operation
    class BadOp(Operation):
        def execute(self, a, b): raise RuntimeError("boom")
        def __str__(self): return "Addition"  # ensure Calculation() dispatch doesn't fail
    c = Calculator(config=CalculatorConfig(base_dir=tmp_path))
    c.set_operation(BadOp())
    with pytest.raises(OperationError, match="Operation failed: boom"):
        c.perform_operation("1", "2")


# --- 272–275: save_history exception path (to_csv fails) ---
def test_save_history_failure_raises(calc, monkeypatch):
    # Put one entry into history
    calc.perform_operation("3", "4")
    real_to_csv = pd.DataFrame.to_csv
    def bad_to_csv(self, *a, **k): raise IOError("disk full")
    monkeypatch.setattr(pd.DataFrame, "to_csv", bad_to_csv, raising=True)
    with pytest.raises(OperationError, match="Failed to save history: disk full"):
        calc.save_history()
    # restore (just in case later tests need it)
    monkeypatch.setattr(pd.DataFrame, "to_csv", real_to_csv, raising=True)


# --- 309–312: load_history exception path (read_csv fails) ---
def test_load_history_failure_raises(tmp_path, monkeypatch):
    cfg = CalculatorConfig(base_dir=tmp_path)
    c = Calculator(config=cfg)
    # Create a file so the code tries read_csv (instead of taking "no file" branch)
    cfg.history_file.write_text("operation,operand1,operand2,result,timestamp\n")
    real_read_csv = pd.read_csv
    def bad_read_csv(*a, **k): raise ValueError("csv parse")
    monkeypatch.setattr(pd, "read_csv", bad_read_csv, raising=True)
    with pytest.raises(OperationError, match="Failed to load history: csv parse"):
        c.load_history()
    monkeypatch.setattr(pd, "read_csv", real_read_csv, raising=True)


# --- 324–333: get_history_dataframe builds rows and returns df ---
def test_get_history_dataframe_builds_rows(calc):
    calc.perform_operation("2", "3")  # 5
    calc.perform_operation("1", "1")  # 2
    df = calc.get_history_dataframe()
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]
    assert len(df) == 2
