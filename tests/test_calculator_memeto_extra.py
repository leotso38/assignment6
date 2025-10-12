import pytest
from app.exceptions import OperationError
from decimal import Decimal
from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento

def test_memento_empty_history_roundtrip():
    m = CalculatorMemento([])             # empty snapshot is valid
    d = m.to_dict()                       # covers to_dict
    r = CalculatorMemento.from_dict(d)    # covers from_dict
    assert r.history == []
    # timestamp serialized/deserialized
    assert isinstance(r.timestamp.isoformat(), str)

def test_memento_roundtrip_nonempty():
    c1 = Calculation("Addition", Decimal("1"), Decimal("2"))
    c2 = Calculation("Multiplication", Decimal("2"), Decimal("3"))
    m = CalculatorMemento([c1, c2])
    d = m.to_dict()
    r = CalculatorMemento.from_dict(d)
    assert len(r.history) == 2
    assert isinstance(r.timestamp.isoformat(), str)

def test_memento_empty_history_roundtrip():
    m = CalculatorMemento([])
    d = m.to_dict()
    r = CalculatorMemento.from_dict(d)
    assert r.history == []
    assert isinstance(r.timestamp.isoformat(), str)