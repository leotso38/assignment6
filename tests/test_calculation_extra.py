import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError


def test_str_repr_and_noncalc_eq():
    c = Calculation("Addition", Decimal("2"), Decimal("3"))
    assert "Addition(2, 3) = 5" in str(c)
    assert "Calculation(operation='Addition'" in repr(c)
    assert (c == object()) is False


def test_zero_root_raises():
    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation("Root", Decimal("9"), Decimal("0"))


def test_from_dict_preserves_timestamp():
    ts = datetime(2024, 1, 1, 0, 0)
    d = {
        "operation": "Addition",
        "operand1": "1",
        "operand2": "2",
        "result": "3",
        "timestamp": ts.isoformat(),
    }
    c = Calculation.from_dict(d)
    assert c.timestamp == ts


def test_format_result_edge_case():
    c = Calculation("Addition", Decimal("1"), Decimal("2"))  # 3
    s = c.format_result(precision=5)
    assert s == "3"   # normalize() removes trailing decimals

def test_percentage_in_model_dispatch():
    c = Calculation(operation="Percentage", operand1=Decimal("25"), operand2=Decimal("200"))
    assert c.result == Decimal("12.5")

def test_absolute_difference_calculation():
    calc = Calculation(operation="AbsoluteDifference", operand1=Decimal("10"), operand2=Decimal("3"))
    assert calc.result == Decimal("7")

def test_absolute_difference_symmetric():
    calc = Calculation(operation="AbsoluteDifference", operand1=Decimal("3"), operand2=Decimal("10"))
    assert calc.result == Decimal("7")