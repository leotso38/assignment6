# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: tests/test_misc_low_hanging.py
# Notes: Env path resolution + CalculatorMemento roundtrip coverage.

from decimal import Decimal
from pathlib import Path

from app.calculator_config import CalculatorConfig, _resolve_env_path, get_project_root
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation


def test_resolve_env_path_relative_and_home_expansion(monkeypatch, tmp_path):
    # relative path → project_root / relative
    rel = "rel_logs"
    monkeypatch.setenv("CALCULATOR_LOG_DIR", rel)
    out = _resolve_env_path("CALCULATOR_LOG_DIR", tmp_path / "fallback")
    assert get_project_root() in out.parents or get_project_root() == out.parent

    # home expansion
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(Path.home() / "X_hist"))
    out2 = _resolve_env_path("CALCULATOR_HISTORY_DIR", tmp_path / "fallback2")
    assert str(Path.home()) in str(out2)


def test_config_base_dir_env_and_defaults(monkeypatch, tmp_path):
    # env base dir provided
    monkeypatch.setenv("CALCULATOR_BASE_DIR", str(tmp_path))
    cfg = CalculatorConfig()
    assert cfg.base_dir == tmp_path.resolve()
    assert isinstance(cfg.default_encoding, str)


def test_memento_to_from_dict_roundtrip():
    c1 = Calculation("Addition", Decimal("2"), Decimal("3"))
    c2 = Calculation("Multiplication", Decimal("4"), Decimal("5"))
    mem = CalculatorMemento(history=[c1, c2])
    data = mem.to_dict()
    mem2 = CalculatorMemento.from_dict(data)
    assert len(mem2.history) == 2
    assert str(mem2.history[0]).startswith("Addition(2, 3) = 5")
