"""
Author: Leo Tso
Class: IS601
Date: 2025-10-12
"""

class CalculatorError(Exception):
    """Base exception for all calculator-specific errors."""
    pass


class ValidationError(CalculatorError):
    """Raised when input validation fails."""
    pass


class OperationError(CalculatorError):
    """Raised when a calculation operation fails."""
    pass


class ConfigurationError(CalculatorError):
    """Raised when calculator configuration is invalid."""
    pass
