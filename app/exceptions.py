# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: app/exceptions.py
# Notes: Centralized custom exception hierarchy for calculator system.

class CalculatorError(Exception):
    """Base class for all calculator-related exceptions."""
    pass


class ValidationError(CalculatorError):
    """Raised when user input fails validation checks."""
    pass


class OperationError(CalculatorError):
    """Raised when an arithmetic or logical operation fails."""
    pass


class ConfigurationError(CalculatorError):
    """Raised when configuration or environment setup is invalid."""
    pass
