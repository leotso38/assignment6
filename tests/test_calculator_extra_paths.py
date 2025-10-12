import pytest
from decimal import Decimal
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.operations import Addition
from app.exceptions import OperationError, ValidationError

@pytest.fixture
def calc(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    return Calculator(config=config)

def test_perform_no_operation_set(calc):
    with pytest.raises(OperationError, match="No operation set"):
        calc.perform_operation("1", "2")

def test_observer_add_remove(calc):
    class DummyObserver:
        def update(self, _): self.updated = True
    o = DummyObserver()
    calc.add_observer(o)
    assert o in calc.observers
    calc.remove_observer(o)
    assert o not in calc.observers

def test_perform_valid(calc):
    calc.set_operation(Addition())
    res = calc.perform_operation("2", "3")
    assert res == Decimal("5")

def test_history_clear(calc):
    calc.set_operation(Addition())
    calc.perform_operation("1", "1")
    calc.clear_history()
    assert calc.history == []
    assert calc.undo_stack == []
    assert calc.redo_stack == []
