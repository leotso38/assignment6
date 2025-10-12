"""
Author: Leo Tso
Class: Operations
Date: 2025-10-12
"""

class Operations:
    @staticmethod
    def addition(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def subtraction(a: float, b: float) -> float:
        return a - b

    @staticmethod
    def multiplication(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def division(a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
