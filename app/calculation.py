# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: app/calculation.py
# Notes: Arithmetic core with safe error mapping and (de)serialization helpers.

from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
import logging
from typing import Any, Dict

from app.exceptions import OperationError


@dataclass
class Calculation:
    operation: str
    operand1: Decimal
    operand2: Decimal
    result: Decimal = field(init=False)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        # Compute once on construction
        self.result = self.calculate()

    # ---------- error helpers ----------

    @staticmethod
    def _raise_div_zero() -> None:
        raise OperationError("Division by zero is not allowed")

    @staticmethod
    def _raise_neg_power() -> None:
        raise OperationError("Negative exponents are not supported")

    @staticmethod
    def _raise_invalid_root(x: Decimal, y: Decimal) -> None:
        # Keep explicit for test coverage
        if y == 0:
            raise OperationError("Zero root is undefined")
        if x < 0:
            raise OperationError("Cannot calculate root of negative number")
        raise OperationError("Invalid root operation")

    # ---------- operation primitives ----------

    @classmethod
    def _div(cls, x: Decimal, y: Decimal) -> Decimal:
        if y == 0:
            cls._raise_div_zero()
        return x / y

    @classmethod
    def _pow(cls, x: Decimal, y: Decimal) -> Decimal:
        if y < 0:
            cls._raise_neg_power()
        # Use float pow for non-integer exponents; convert back to Decimal
        return Decimal(pow(float(x), float(y)))

    @classmethod
    def _root_checked(cls, x: Decimal, y: Decimal) -> Decimal:
        if y == 0 or x < 0:
            cls._raise_invalid_root(x, y)
        return Decimal(pow(float(x), 1.0 / float(y)))

    @classmethod
    def _int_div(cls, x: Decimal, y: Decimal) -> Decimal:
        """Floor-division semantics (matches Python // for negatives)."""
        if y == 0:
            cls._raise_div_zero()
        return (x / y).to_integral_value(rounding=ROUND_FLOOR)

    @classmethod
    def _mod(cls, x: Decimal, y: Decimal) -> Decimal:
        """Remainder: a - b * floor(a/b)."""
        if y == 0:
            cls._raise_div_zero()
        q = (x / y).to_integral_value(rounding=ROUND_FLOOR)
        return x - q * y

    @classmethod
    def _percentage(cls, x: Decimal, y: Decimal) -> Decimal:
        """Compute (x / y) * 100 with zero check."""
        if y == 0:
            cls._raise_div_zero()
        return (x / y) * Decimal(100)

    @staticmethod
    def _absdiff(x: Decimal, y: Decimal) -> Decimal:
        """|x - y|"""
        return (x - y).copy_abs()

    # ---------- dispatcher ----------

    def calculate(self) -> Decimal:
        ops = {
            "Addition":            lambda x, y: x + y,
            "Subtraction":         lambda x, y: x - y,
            "Multiplication":      lambda x, y: x * y,
            "Division":            lambda x, y: self._div(x, y),
            "Power":               lambda x, y: self._pow(x, y),
            "Root":                lambda x, y: self._root_checked(x, y),
            "Modulus":             lambda x, y: self._mod(x, y),
            "IntegerDivision":     lambda x, y: self._int_div(x, y),
            "Percentage":          lambda x, y: self._percentage(x, y),
            "AbsoluteDifference":  lambda x, y: self._absdiff(x, y),
        }
        fn = ops.get(self.operation)
        if not fn:
            raise OperationError(f"Unknown operation: {self.operation}")
        try:
            return fn(self.operand1, self.operand2)
        except (InvalidOperation, ValueError, ArithmeticError) as e:
            # Normalize upstream math/runtime errors
            raise OperationError(f"Calculation failed: {str(e)}")

    # ---------- (de)serialization ----------

    def to_dict(self) -> Dict[str, Any]:
        # Serialize to string-safe forms
        return {
            "operation": self.operation,
            "operand1": str(self.operand1),
            "operand2": str(self.operand2),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Calculation":
        # Strict load with warning on result mismatch
        try:
            calc = Calculation(
                operation=data["operation"],
                operand1=Decimal(data["operand1"]),
                operand2=Decimal(data["operand2"]),
            )
            calc.timestamp = datetime.datetime.fromisoformat(data["timestamp"])
            saved = Decimal(data["result"])
            if calc.result != saved:
                logging.warning(
                    f"Loaded calculation result {saved} differs from computed result {calc.result}"
                )
            return calc
        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {str(e)}")

    # ---------- repr / comparisons / formatting ----------

    def __str__(self) -> str:
        # Human-readable summary
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def __repr__(self) -> str:
        # Debug-focused form
        return (
            "Calculation("
            f"operation='{self.operation}', "
            f"operand1={self.operand1}, "
            f"operand2={self.operand2}, "
            f"result={self.result}, "
            f"timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        # Return NotImplemented to allow symmetric fallback
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation
            and self.operand1 == other.operand1
            and self.operand2 == other.operand2
            and self.result == other.result
        )

    def format_result(self, precision: int = 10) -> str:
        """Format with fixed precision; fall back on InvalidOperation (e.g., NaN)."""
        try:
            q = Decimal("0." + "0" * precision)
            return str(self.result.normalize().quantize(q).normalize())
        except InvalidOperation:
            return str(self.result)
