# Author: Leo Tso
# Date: 2025-10-18
# Class: IS601
# File: app/calculator_memento.py
# Notes: Implements the Memento pattern to capture calculator history for undo/redo.

from dataclasses import dataclass, field
import datetime
from typing import Any, Dict, List
from app.calculation import Calculation


@dataclass
class CalculatorMemento:
    """Preserves calculator state (history + timestamp) for restoration."""
    history: List[Calculation]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize memento into a dictionary format."""
        return {
            "history": [calc.to_dict() for calc in self.history],
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CalculatorMemento":
        """Deserialize memento from dictionary back into object form."""
        return cls(
            history=[Calculation.from_dict(calc) for calc in data["history"]],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
        )
