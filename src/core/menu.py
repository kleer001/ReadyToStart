"""Menu node structure for Ready to Start game system."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.core.enums import CompletionState, SettingState
from src.core.types import Setting

if TYPE_CHECKING:
    from src.core.game_state import GameState


@dataclass
class MenuNode:
    """A menu node containing settings and connections.

    Attributes:
        id: Unique identifier for the menu node
        category: Category/theme of the menu
        settings: List of settings in this menu
        connections: IDs of connected menu nodes
        requirements: List of requirement dicts for accessibility
        hidden_triggers: List of trigger dicts for hidden features
        visited: Whether this menu has been visited
        completion_state: Current completion state of the menu
        level_id: Level identifier this menu belongs to (optional)
    """

    id: str
    category: str
    settings: list[Setting] = field(default_factory=list)
    connections: list[str] = field(default_factory=list)
    requirements: list[dict] = field(default_factory=list)
    hidden_triggers: list[dict] = field(default_factory=list)
    visited: bool = False
    completion_state: CompletionState = CompletionState.INCOMPLETE
    level_id: str | None = None

    def add_setting(self, setting: Setting) -> None:
        """Add a setting to this menu node."""
        self.settings.append(setting)

    def is_accessible(self, game_state: "GameState") -> bool:
        """Check if this menu is accessible based on requirements.

        Args:
            game_state: Current game state

        Returns:
            True if all requirements are met
        """
        if not self.requirements:
            return True

        for req in self.requirements:
            setting_id = req.get("setting_id")
            required_state = req.get("state")

            if not setting_id or not required_state:
                continue

            setting = game_state.get_setting(setting_id)
            if not setting:
                return False

            # Convert string state to enum if needed
            if isinstance(required_state, str):
                try:
                    required_state = SettingState(required_state)
                except ValueError:
                    return False

            if setting.state != required_state:
                return False

        return True

    def calculate_completion(self) -> CompletionState:
        """Calculate completion state based on settings.

        Returns:
            CompletionState based on setting states
        """
        if not self.settings:
            return CompletionState.COMPLETE

        enabled_count = sum(1 for s in self.settings if s.state == SettingState.ENABLED)
        total_count = len(self.settings)

        if enabled_count == 0:
            return CompletionState.INCOMPLETE
        elif enabled_count == total_count:
            return CompletionState.COMPLETE
        else:
            return CompletionState.PARTIAL
