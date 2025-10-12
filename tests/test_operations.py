import pytest
from app.operations import addition, subtraction, multiplication, division

def test_additioon():
    assert addition(1,1) == 2

def test_subtraction():
    assert subtraction(1,1) == 0

def test_multiplication():
    assert multiplication(1,1) == 1

def test_division_positive():
    assert division(1,1) == 1

def test_division_by_zero():
    """Test division by zero."""
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        division(1, 0)