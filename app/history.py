"""
Author: Leo Tso
Class: IS601
Date: 2025-10-12
"""

from abc import ABC, abstractmethod
import logging
from typing import Any
from app.calculation import Calculation

class HistoryObserver(ABC):
    """Abstract base class for calculator observers."""
    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """Handle new calculation event."""
        pass

class LoggingObserver(HistoryObserver):
    """Observer that logs calculations to a file."""
    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        logging.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = {calculation.result}"
        )

class AutoSaveObserver(HistoryObserver):
    """Observer that automatically saves calculations."""
    def __init__(self, calculator: Any):
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'save_history'):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("History auto-saved")
