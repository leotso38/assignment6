"""
Author: Leo Tso
Class: IS601
Date: 2025-10-12
"""

from dataclasses import dataclass, field
import datetime
from typing import Any, Dict, List
from app.calculation import Calculation

@dataclass
class CalculatorMemento:
    """Stores calculator state for undo/redo functionality."""
    history: List[Calculation]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert memento to dictionary."""
        return {
            'history': [calc.to_dict() for calc in self.history],
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculatorMemento':
        """Recreate memento from dictionary."""
        return cls(
            history=[Calculation.from_dict(calc) for calc in data['history']],
            timestamp=datetime.datetime.fromisoformat(data['timestamp'])
        )
