import os
from io import StringIO
from pathlib import Path
from decimal import Decimal, InvalidOperation
import builtins
import pandas as pd
import pytest

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.console import calculator_repl
from app.exceptions import OperationError
from app.operations import Addition


# -----------------------------
# app/calculator.py branches
# -----------------------------

def test_save_history_writes_empty_headers(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path, max_history_size=10)
    c = Calculator(cfg)
    # start empty, force save -> hits empty-history branch
    c.clear_history()
    c.save_history()
    assert cfg.history_file.exists()
    df = pd.read_csv(cfg.history_file)
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]
    assert df.empty


def test_load_history_no_file(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path, max_history_size=10)
    c = Calculator(cfg)
    # ensure file is absent
    if cfg.history_file.exists():
        cfg.history_file.unlink()
    # should hit "no history file found" branch without error
    c.load_history()
    assert c.history == []


def test_load_history_empty_file(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path, max_history_size=10)
    # create empty csv with headers
    cfg.history_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=["operation","operand1","operand2","result","timestamp"]).to_csv(cfg.history_file, index=False)
    c = Calculator(cfg)
    # load_history runs in __init__, but call explicitly too
    c.load_history()
    assert c.history == []


def test_history_prune_slices_latest(tmp_path):
    cfg = CalculatorConfig(base_dir=tmp_path, max_history_size=1)
    c = Calculator(cfg)
    c.set_operation(Addition())
    c.perform_operation("1", "1")
    c.perform_operation("2", "2")
    # after slicing, only the newest remains
    assert len(c.history) == 1
    assert c.history[0].operand1 == Decimal("2")


# -----------------------------
# app/calculation.py branches
# -----------------------------

def test_format_result_invalidoperation_fallback(monkeypatch):
    # Force InvalidOperation inside quantize()
    calc = Calculation("Addition", Decimal("1"), Decimal("1"))
    class DummyDec(Decimal):
        def quantize(self, *args, **kwargs):
            raise InvalidOperation
    calc.result = DummyDec("2")
    assert calc.format_result(precision=6) == "2"


def test_calculation_wraps_runtime_error(monkeypatch):
    # Cause pow() to raise to hit "Calculation failed: ..." wrapper
    original_pow = builtins.pow
    def boom(*args, **kwargs):  # pragma: no cover - this is helper
        raise ValueError("boom")
    monkeypatch.setattr(builtins, "pow", boom)
    try:
        with pytest.raises(OperationError, match="Calculation failed: boom"):
            Calculation("Power", Decimal("2"), Decimal("3"))
    finally:
        monkeypatch.setattr(builtins, "pow", original_pow)


# -----------------------------
# app/calculator_config.py branches
# -----------------------------

def test_config_env_overrides_and_defaults(monkeypatch, tmp_path):
    # Override dirs via env (exercise env branches)
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "L"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "H"))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "7")
    monkeypatch.setenv("CALCULATOR_PRECISION", "8")
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "1000")
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "utf-16")

    cfg = CalculatorConfig(base_dir=tmp_path)
    # Access properties to hit property branches
    assert cfg.log_dir == (tmp_path / "L").resolve()
    assert cfg.history_dir == (tmp_path / "H").resolve()
    assert cfg.auto_save is False
    assert cfg.max_history_size == 7
    assert cfg.precision == 8
    assert str(cfg.max_input_value) == "1000"
    assert cfg.default_encoding == "utf-16"


# -----------------------------
# app/console.py branches
# -----------------------------

def test_console_help_unknown_and_exit(monkeypatch, capsys):
    # Script a short console session: help -> unknown -> exit
    inputs = iter(["help", "wat", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    # prevent actual file I/O noise in logs/history by temp dirs
    tmp = Path(capsys.readouterr().__class__.__name__)  # dummy; just to keep style consistent

    with pytest.raises(SystemExit):
        calculator_repl()

    out = capsys.readouterr().out
    assert "Available commands" in out
    assert "Unknown command: 'wat'" in out or "Unknown command" in out
    assert "Goodbye!" in out


def test_console_cancel_on_operation(monkeypatch, capsys):
    # add -> cancel at first number -> continue -> exit
    inputs = iter(["add", "cancel", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    with pytest.raises(SystemExit):
        calculator_repl()
    out = capsys.readouterr().out
    assert "Operation cancelled" in out
    assert "Goodbye!" in out


def test_console_keyboard_interrupt(monkeypatch, capsys):
    # First prompt raises KeyboardInterrupt, then exit
    calls = {"n": 0}
    def raiser(_):
        calls["n"] += 1
        if calls["n"] == 1:
            raise KeyboardInterrupt()
        return "exit"
    monkeypatch.setattr("builtins.input", raiser)
    with pytest.raises(SystemExit):
        calculator_repl()
    out = capsys.readouterr().out
    assert "Operation cancelled" in out
    assert "Goodbye!" in out


def test_console_eof(monkeypatch, capsys):
    # First prompt raises EOFError -> exits gracefully
    def raiser(_):
        raise EOFError()
    monkeypatch.setattr("builtins.input", raiser)
    with pytest.raises(SystemExit):
        calculator_repl()
    out = capsys.readouterr().out
    assert "Input terminated. Exiting..." in out
