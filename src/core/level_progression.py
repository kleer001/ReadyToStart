"""Level progression tracking for Ready to Start.

This module handles tracking which levels have been completed and
determining which level the player should work on next.
"""

from typing import Optional

from src.core.game_state import GameState


class LevelProgressionTracker:
    """Tracks level completion and progression through the game.

    The game uses a hub-and-spoke model where players always return to
    the main menu (Level_0) and must complete levels sequentially to
    eventually start the game.
    """

    def __init__(self):
        """Initialize the progression tracker."""
        self.completed_levels: set[str] = set()
        self.level_game_states: dict[str, GameState] = {}

    def register_level(self, level_id: str, game_state: GameState) -> None:
        """Register a game state for a specific level.

        Args:
            level_id: Level identifier (e.g., "Level_1")
            game_state: The game state for this level
        """
        self.level_game_states[level_id] = game_state

    def is_level_complete(self, level_id: str) -> bool:
        """Check if a level has been completed.

        A level is complete when all its critical path settings are enabled.

        Args:
            level_id: Level identifier to check

        Returns:
            True if level is complete, False otherwise
        """
        if level_id in self.completed_levels:
            return True

        game_state = self.level_game_states.get(level_id)
        if not game_state:
            return False

        # Check if all settings with level_id are enabled (victory condition)
        level_settings = [
            setting
            for menu in game_state.menus.values()
            for setting in menu.settings
            if setting.level_id == level_id
        ]

        if not level_settings:
            return False

        # Check if all critical settings are enabled
        from src.core.enums import SettingState
        all_enabled = all(
            setting.state == SettingState.ENABLED
            for setting in level_settings
        )

        if all_enabled:
            self.completed_levels.add(level_id)
            return True

        return False

    def mark_level_complete(self, level_id: str) -> None:
        """Manually mark a level as complete.

        Args:
            level_id: Level identifier to mark complete
        """
        self.completed_levels.add(level_id)

    def get_next_incomplete_level(self, level_order: list[str]) -> Optional[str]:
        """Get the next incomplete level in sequence.

        Args:
            level_order: Ordered list of level IDs

        Returns:
            Next incomplete level ID, or None if all complete
        """
        for level_id in level_order:
            if level_id == "Level_0":  # Skip hub
                continue
            if not self.is_level_complete(level_id):
                return level_id
        return None

    def get_current_level_number(self, level_order: list[str]) -> int:
        """Get the current level number the player is working on.

        Args:
            level_order: Ordered list of level IDs

        Returns:
            Level number (1-based, 0 for hub)
        """
        next_level = self.get_next_incomplete_level(level_order)
        if not next_level:
            return len(level_order)  # All complete

        try:
            # Extract number from "Level_X"
            return int(next_level.split("_")[1])
        except (IndexError, ValueError):
            return 1

    def can_start_game(self, level_order: list[str]) -> bool:
        """Check if player has completed all levels and can start the game.

        Args:
            level_order: Ordered list of level IDs

        Returns:
            True if all levels are complete
        """
        return self.get_next_incomplete_level(level_order) is None

    def get_completion_stats(self, level_order: list[str]) -> dict:
        """Get statistics about level completion.

        Args:
            level_order: Ordered list of level IDs

        Returns:
            Dict with completion statistics
        """
        total_levels = len([lid for lid in level_order if lid != "Level_0"])
        completed_count = len(self.completed_levels)

        return {
            "total_levels": total_levels,
            "completed_levels": completed_count,
            "completion_percentage": (completed_count / total_levels * 100) if total_levels > 0 else 0,
            "can_start_game": self.can_start_game(level_order)
        }
