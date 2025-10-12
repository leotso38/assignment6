"""
Author: Leo Tso
Class: IS601
Date: 2025-10-12
"""

import pytest
from typing import Union
from app.operations import Operations

Number = Union[int, float]

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 5),
        (0, 0, 0),
        (-1, 1, 0),
        (2.5, 3.5, 6.0),
        (-2.5, 3.5, 1.0),
    ]
)
def test_addition(a: Number, b: Number, expected: Number) -> None:
    result = Operations.addition(a, b)
    assert result == expected

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (5, 3, 2),
        (0, 0, 0),
        (-5, -3, -2),
        (10.5, 5.5, 5.0),
        (-10.5, -5.5, -5.0),
    ]
)
def test_subtraction(a: Number, b: Number, expected: Number) -> None:
    result = Operations.subtraction(a, b)
    assert result == expected

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 6),
        (0, 10, 0),
        (-2, -3, 6),
        (2.5, 4.0, 10.0),
        (-2.5, 4.0, -10.0),
    ]
)
def test_multiplication(a: Number, b: Number, expected: Number) -> None:
    result = Operations.multiplication(a, b)
    assert result == expected

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (6, 3, 2.0),
        (-6, -3, 2.0),
        (6.0, 3.0, 2.0),
        (-6.0, 3.0, -2.0),
        (0, 5, 0.0),
    ]
)
def test_division(a: Number, b: Number, expected: float) -> None:
    result = Operations.division(a, b)
    assert result == expected

@pytest.mark.parametrize(
    "a, b",
    [
        (1, 0),
        (-1, 0),
        (0, 0),
    ]
)
def test_division_by_zero(a: Number, b: Number) -> None:
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        Operations.division(a, b)
