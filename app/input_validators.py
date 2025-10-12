"""
Author: Leo Tso
Class: IS601
Date: 2025-10-12
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

@dataclass
class InputValidator:
    """Validates and sanitizes calculator inputs."""
    
    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        """Validate and convert input to Decimal."""
        try:
            if isinstance(value, str):
                value = value.strip()
            number = Decimal(str(value))
            if abs(number) > config.max_input_value:
                raise ValidationError(f"Value exceeds maximum allowed: {config.max_input_value}")
            return number.normalize()
        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}") from e
