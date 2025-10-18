# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: app/operations.py
# Notes: Defines operation strategies and factory for calculator (Strategy + Factory patterns).

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_FLOOR, ROUND_DOWN
from typing import Dict
from app.exceptions import ValidationError


class Operation(ABC):
    """Abstract base class for calculator operations."""

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:  # pragma: no cover
        """Perform the operation."""
        pass

    def validate_operands(self, a: Decimal, b: Decimal) -> None: # pragma: no cover
        """Optional operand validation override."""
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


# ---------- Arithmetic Operations ----------

class Addition(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a + b


class Subtraction(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a - b


class Multiplication(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a * b


class Division(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a / b


class Power(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b < 0:
            raise ValidationError("Negative exponents not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), float(b)))


class Root(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))


class Modulus(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        # Python-style modulo (result sign matches divisor)
        q = (a / b).to_integral_value(rounding=ROUND_FLOOR)
        return a - q * b


class IntegerDivision(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        # Truncate toward zero (discard fractional part)
        return (a / b).to_integral_value(rounding=ROUND_DOWN)


class Percentage(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return (a / b) * Decimal(100)


class AbsoluteDifference(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return (a - b).copy_abs()


# ---------- Operation Factory ----------

class OperationFactory:
    """Factory for creating operation instances from string identifiers."""
    _operations: Dict[str, type] = {
        "add": Addition,
        "subtract": Subtraction,
        "multiply": Multiplication,
        "divide": Division,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "intdiv": IntegerDivision,
        "percentage": Percentage,
        "absdiff": AbsoluteDifference,
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        """Register a new operation at runtime."""
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """Instantiate an operation based on name."""
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()
