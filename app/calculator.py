# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: app/calculator.py
# Notes: Main Calculator orchestration—validation, operation dispatch, history/undo/redo, CSV I/O.

from decimal import Decimal
import logging
import os
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation

Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]


class Calculator:
    def __init__(self, config: Optional[CalculatorConfig] = None):
        """Init with config, logging, dirs; attempt to load prior history."""
        if config is None:
            project_root = Path(__file__).parent.parent
            config = CalculatorConfig(base_dir=project_root)
        self.config = config
        self.config.validate()

        os.makedirs(self.config.log_dir, exist_ok=True)
        self._setup_logging()

        self.history: List[Calculation] = []
        self.operation_strategy: Optional[Operation] = None
        self.observers: List[HistoryObserver] = []
        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []

        self._setup_directories()
        try:
            self.load_history()
        except Exception as e:
            logging.warning(f"Could not load existing history: {e}")

        logging.info("Calculator initialized with configuration")

    def _setup_logging(self) -> None:
        """Configure file logging based on CalculatorConfig.log_file."""
        try:
            os.makedirs(self.config.log_dir, exist_ok=True)
            log_file = self.config.log_file.resolve()
            logging.basicConfig(
                filename=str(log_file),
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                force=True,
            )
            logging.info(f"Logging initialized at: {log_file}")
        except Exception as e:
            print(f"Error setting up logging: {e}")
            raise

    def _setup_directories(self) -> None:
        """Ensure history directory exists."""
        self.config.history_dir.mkdir(parents=True, exist_ok=True)

    def add_observer(self, observer: HistoryObserver) -> None:
        """Register an observer for history updates."""
        self.observers.append(observer)
        logging.info(f"Added observer: {observer.__class__.__name__}")

    def remove_observer(self, observer: HistoryObserver) -> None:
        """Unregister a previously added observer."""
        self.observers.remove(observer)
        logging.info(f"Removed observer: {observer.__class__.__name__}")

    def notify_observers(self, calculation: Calculation) -> None:
        """Notify all observers of a new calculation."""
        for observer in self.observers:
            observer.update(calculation)

    def set_operation(self, operation: Operation) -> None:
        """Set current operation strategy (Factory-produced)."""
        self.operation_strategy = operation
        logging.info(f"Set operation: {operation}")

    def perform_operation(
        self,
        a: Union[str, Number],
        b: Union[str, Number],
    ) -> CalculationResult:
        """Validate inputs, execute operation, push memento, notify observers."""
        if not self.operation_strategy:
            raise OperationError("No operation set")
        try:
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            result = self.operation_strategy.execute(validated_a, validated_b)

            calculation = Calculation(
                operation=str(self.operation_strategy),
                operand1=validated_a,
                operand2=validated_b,
            )

            # Save prior state for undo; clear redo lineage on new op.
            self.undo_stack.append(CalculatorMemento(self.history.copy()))
            self.redo_stack.clear()

            # Append and enforce max history size (keep most recent N).
            self.history.append(calculation)
            try:
                max_n = int(self.config.max_history_size)
            except (TypeError, ValueError):
                max_n = 0
            if max_n > 0 and len(self.history) > max_n:
                self.history = self.history[-max_n:]

            self.notify_observers(calculation)
            return result
        except ValidationError as e:
            logging.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Operation failed: {str(e)}")
            raise OperationError(f"Operation failed: {str(e)}")

    def save_history(self) -> None:
        """Persist history to CSV; create file if empty."""
        try:
            self.config.history_dir.mkdir(parents=True, exist_ok=True)
            rows = [
                {
                    "operation": str(calc.operation),
                    "operand1": str(calc.operand1),
                    "operand2": str(calc.operand2),
                    "result": str(calc.result),
                    "timestamp": calc.timestamp.isoformat(),
                }
                for calc in self.history
            ]
            if rows:
                pd.DataFrame(rows).to_csv(self.config.history_file, index=False)
                logging.info(f"History saved to {self.config.history_file}")
            else:
                pd.DataFrame(
                    columns=["operation", "operand1", "operand2", "result", "timestamp"]
                ).to_csv(self.config.history_file, index=False)
                logging.info("Empty history saved")
        except Exception as e:
            logging.error(f"Failed to save history: {e}")
            raise OperationError(f"Failed to save history: {e}")

    def load_history(self) -> None:
        """Load history from CSV (idempotent if file missing/empty)."""
        try:
            if self.config.history_file.exists():
                df = pd.read_csv(self.config.history_file)
                if not df.empty:
                    self.history = [
                        Calculation.from_dict(
                            {
                                "operation": row["operation"],
                                "operand1": row["operand1"],
                                "operand2": row["operand2"],
                                "result": row["result"],
                                "timestamp": row["timestamp"],
                            }
                        )
                        for _, row in df.iterrows()
                    ]
                    logging.info(f"Loaded {len(self.history)} calculations from history")
                else:
                    logging.info("Loaded empty history file")
            else:
                logging.info("No history file found - starting empty")
        except Exception as e:
            logging.error(f"Failed to load history: {e}")
            raise OperationError(f"Failed to load history: {e}")

    def get_history_dataframe(self) -> pd.DataFrame:
        """Return current history as a DataFrame (for UI/tests)."""
        return pd.DataFrame(
            [
                {
                    "operation": str(c.operation),
                    "operand1": str(c.operand1),
                    "operand2": str(c.operand2),
                    "result": str(c.result),
                    "timestamp": c.timestamp,
                }
                for c in self.history
            ]
        )

    @staticmethod
    def _format_decimal_plain(value: Decimal) -> str:
        """Plain string (no exponent) for Decimal, trims trailing zeros."""
        s = format(value, "f")
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        if s == "-0":
            s = "0"
        return s

    def show_history(self) -> List[str]:
        """Render history lines like 'Op(a, b) = result' (adds % for Percentage)."""
        entries: List[str] = []
        for calc in self.history:
            is_percentage = str(calc.operation).lower() == "percentage"

            a_str = (
                self._format_decimal_plain(calc.operand1)
                if isinstance(calc.operand1, Decimal)
                else str(calc.operand1)
            )
            b_str = (
                self._format_decimal_plain(calc.operand2)
                if isinstance(calc.operand2, Decimal)
                else str(calc.operand2)
            )
            res_str = (
                self._format_decimal_plain(calc.result)
                if isinstance(calc.result, Decimal)
                else str(calc.result)
            )

            if is_percentage:
                res_str = f"{res_str}%"

            entries.append(f"{calc.operation}({a_str}, {b_str}) = {res_str}")
        return entries

    def clear_history(self) -> None:
        """Clear history and all undo/redo stacks."""
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()  # fixed stray 'a' typo
        logging.info("History cleared")

    def undo(self) -> bool:
        """Restore previous history state (push current to redo)."""
        if not self.undo_stack:
            return False
        memento = self.undo_stack.pop()
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True

    def redo(self) -> bool:
        """Re-apply next history state (push current to undo)."""
        if not self.redo_stack:
            return False
        memento = self.redo_stack.pop()
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        return True
