"""Dependency resolution system for settings."""

from typing import TYPE_CHECKING, Protocol

from ready_to_start.core.enums import SettingState

if TYPE_CHECKING:
    from ready_to_start.core.game_state import GameState


class Dependency(Protocol):
    """Protocol for dependency evaluation."""

    def evaluate(self, game_state: "GameState") -> bool:
        """Evaluate if dependency is satisfied.

        Args:
            game_state: Current game state

        Returns:
            True if dependency is satisfied
        """
        ...


class SimpleDependency:
    """A setting requires another setting to be in a specific state."""

    def __init__(self, setting_id: str, required_state: SettingState):
        """Initialize simple dependency.

        Args:
            setting_id: ID of required setting
            required_state: Required state of that setting
        """
        self.setting_id = setting_id
        self.required_state = required_state

    def evaluate(self, game_state: "GameState") -> bool:
        """Check if required setting is in required state."""
        setting = game_state.get_setting(self.setting_id)
        return setting.state == self.required_state if setting else False


class ValueDependency:
    """A setting's value must compare to another setting's value."""

    OPERATORS = {
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
    }

    def __init__(self, setting_a: str, operator: str, setting_b: str):
        """Initialize value dependency.

        Args:
            setting_a: ID of first setting
            operator: Comparison operator (>, <, ==, !=, >=, <=)
            setting_b: ID of second setting
        """
        self.setting_a = setting_a
        self.operator = operator
        self.setting_b = setting_b

        if operator not in self.OPERATORS:
            raise ValueError(f"Invalid operator: {operator}")

    def evaluate(self, game_state: "GameState") -> bool:
        """Check if value comparison is satisfied."""
        setting_a = game_state.get_setting(self.setting_a)
        setting_b = game_state.get_setting(self.setting_b)

        if not setting_a or not setting_b:
            return False

        try:
            op_func = self.OPERATORS[self.operator]
            return op_func(setting_a.value, setting_b.value)
        except (TypeError, ValueError):
            return False


class DependencyResolver:
    """Manages and resolves setting dependencies."""

    def __init__(self):
        """Initialize dependency resolver."""
        self.dependencies: dict[str, list[Dependency]] = {}

    def add_dependency(self, setting_id: str, dependency: Dependency) -> None:
        """Add a dependency for a setting.

        Args:
            setting_id: ID of setting with dependency
            dependency: Dependency to add
        """
        if setting_id not in self.dependencies:
            self.dependencies[setting_id] = []
        self.dependencies[setting_id].append(dependency)

    def can_enable(self, setting_id: str, game_state: "GameState") -> bool:
        """Check if a setting can be enabled.

        Args:
            setting_id: ID of setting to check
            game_state: Current game state

        Returns:
            True if all dependencies are satisfied
        """
        deps = self.dependencies.get(setting_id, [])
        return all(dep.evaluate(game_state) for dep in deps)

    def resolve_all(self, game_state: "GameState") -> dict[str, bool]:
        """Check all settings against their dependencies.

        Args:
            game_state: Current game state

        Returns:
            Dict mapping setting IDs to whether they can be enabled
        """
        results = {}
        for setting_id in self.dependencies:
            results[setting_id] = self.can_enable(setting_id, game_state)
        return results
