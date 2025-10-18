# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: app/history.py
# Notes: Implements Observer pattern for calculator—logging and auto-save on new calculations.

from abc import ABC, abstractmethod
import logging
from typing import Any
from app.calculation import Calculation


class HistoryObserver(ABC):
    """Abstract base observer class for calculator state updates."""

    @abstractmethod
    def update(self, calculation: Calculation) -> None: # pragma: no cover
        """Handle new calculation notification."""
        pass


class LoggingObserver(HistoryObserver):
    """Observer that logs calculation details to log file."""

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        logging.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = {calculation.result}"
        )


class AutoSaveObserver(HistoryObserver):
    """Observer that auto-saves calculator history after each calculation."""

    def __init__(self, calculator: Any):
        if not hasattr(calculator, "config") or not hasattr(calculator, "save_history"):
            raise TypeError("Calculator must have 'config' and 'save_history' attributes")
        self.calculator = calculator

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.calculator.config.auto_save:
            self.calculator.save_history()
            logging.info("History auto-saved")
