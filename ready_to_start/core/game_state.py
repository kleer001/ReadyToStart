"""Central game state management."""

import time
from typing import Any

from ready_to_start.core.dependencies import DependencyResolver
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting


class GameState:
    """Central game state management.

    Manages all menus, settings, and tracks navigation state.
    """

    def __init__(self):
        """Initialize game state."""
        self.menus: dict[str, MenuNode] = {}
        self.settings: dict[str, Setting] = {}
        self.current_menu: str | None = None
        self.visited_menus: list[str] = []
        self.resolver = DependencyResolver()

    def add_menu(self, menu: MenuNode) -> None:
        """Add a menu to the game state.

        Args:
            menu: Menu node to add
        """
        self.menus[menu.id] = menu
        for setting in menu.settings:
            self.settings[setting.id] = setting

    def get_setting(self, setting_id: str) -> Setting | None:
        """Get a setting by ID.

        Args:
            setting_id: ID of setting to retrieve

        Returns:
            Setting if found, None otherwise
        """
        return self.settings.get(setting_id)

    def get_menu(self, menu_id: str) -> MenuNode | None:
        """Get a menu by ID.

        Args:
            menu_id: ID of menu to retrieve

        Returns:
            MenuNode if found, None otherwise
        """
        return self.menus.get(menu_id)

    def navigate_to(self, menu_id: str) -> bool:
        """Navigate to a menu.

        Args:
            menu_id: ID of menu to navigate to

        Returns:
            True if navigation succeeded
        """
        menu = self.get_menu(menu_id)
        if menu and menu.is_accessible(self):
            self.current_menu = menu_id
            if menu_id not in self.visited_menus:
                self.visited_menus.append(menu_id)
            menu.visited = True
            return True
        return False

    def update_setting(self, setting_id: str, value: Any) -> bool:
        """Update a setting's value.

        Args:
            setting_id: ID of setting to update
            value: New value

        Returns:
            True if update succeeded
        """
        setting = self.get_setting(setting_id)
        if not setting:
            return False

        # Check dependencies
        if not self.resolver.can_enable(setting_id, self):
            return False

        # Validate value bounds for numeric types
        if setting.min_value is not None and value < setting.min_value:
            return False
        if setting.max_value is not None and value > setting.max_value:
            return False

        setting.value = value
        setting.visit_count += 1
        setting.last_modified = time.time()
        return True

    def propagate_changes(self) -> None:
        """Propagate state changes throughout the game.

        Re-evaluates all dependencies and updates menu completion states
        after a setting has been changed. This ensures the entire game
        state remains consistent.
        """
        # Re-evaluate all dependencies
        dependency_results = self.resolver.resolve_all(self)

        # Update menu completion states
        for menu in self.menus.values():
            menu.completion_state = menu.calculate_completion()

    def get_dependency_hints(self, setting_id: str) -> list[str]:
        """Get human-readable hints about why a setting can't be enabled.

        Args:
            setting_id: ID of setting to check

        Returns:
            List of human-readable dependency descriptions
        """
        hints = []
        deps = self.resolver.dependencies.get(setting_id, [])

        for dep in deps:
            if not dep.evaluate(self):
                # Import here to avoid circular imports
                from ready_to_start.core.dependencies import SimpleDependency, ValueDependency

                if isinstance(dep, SimpleDependency):
                    req_setting = self.get_setting(dep.setting_id)
                    if req_setting:
                        hints.append(
                            f"Requires '{req_setting.label}' to be {dep.required_state.value}"
                        )
                elif isinstance(dep, ValueDependency):
                    setting_a = self.get_setting(dep.setting_a)
                    setting_b = self.get_setting(dep.setting_b)
                    if setting_a and setting_b:
                        hints.append(
                            f"Requires '{setting_a.label}' {dep.operator} '{setting_b.label}'"
                        )

        return hints
