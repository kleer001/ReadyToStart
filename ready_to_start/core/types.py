"""Core data types for Ready to Start game system."""

from dataclasses import dataclass
from typing import Any

from ready_to_start.core.enums import SettingState, SettingType


@dataclass
class Setting:
    """A single setting in the game menu system.

    Attributes:
        id: Unique identifier for the setting
        type: Type of value (bool, int, float, string)
        value: Current value of the setting
        state: Current state (enabled, disabled, hidden, etc.)
        label: Human-readable label
        min_value: Minimum value for numeric types
        max_value: Maximum value for numeric types
        visit_count: Number of times setting has been modified
        last_modified: Timestamp of last modification
    """

    id: str
    type: SettingType
    value: Any
    state: SettingState
    label: str
    min_value: float | None = None
    max_value: float | None = None
    visit_count: int = 0
    last_modified: float | None = None

    def __post_init__(self):
        """Validate setting attributes."""
        if self.type in (SettingType.INTEGER, SettingType.FLOAT):
            if self.min_value is not None and self.max_value is not None:
                if self.min_value > self.max_value:
                    raise ValueError("min_value cannot be greater than max_value")
