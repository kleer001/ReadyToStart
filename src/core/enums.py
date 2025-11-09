"""Enumerations for Ready to Start game system."""

from enum import Enum


class SettingState(Enum):
    """State of a setting in the game."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    HIDDEN = "hidden"
    LOCKED = "locked"
    BLINKING = "blinking"


class SettingType(Enum):
    """Type of value a setting can hold."""

    BOOLEAN = "bool"
    INTEGER = "int"
    FLOAT = "float"
    STRING = "string"


class CompletionState(Enum):
    """Completion state of a menu node."""

    INCOMPLETE = "incomplete"
    PARTIAL = "partial"
    COMPLETE = "complete"
