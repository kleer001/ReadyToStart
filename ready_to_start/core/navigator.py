"""Menu navigation logic."""


from ready_to_start.core.game_state import GameState


class MenuNavigator:
    """Handle menu navigation logic.

    Provides methods to navigate between menus and query available options.
    """

    def __init__(self, game_state: GameState):
        """Initialize navigator with game state.

        Args:
            game_state: Game state to navigate
        """
        self.state = game_state

    def get_available_options(self) -> list[str]:
        """Get accessible menus from current location.

        Returns:
            List of menu IDs that can be navigated to
        """
        if not self.state.current_menu:
            return []

        current = self.state.get_menu(self.state.current_menu)
        if not current:
            return []

        available = []
        for menu_id in current.connections:
            menu = self.state.get_menu(menu_id)
            if menu and menu.is_accessible(self.state):
                available.append(menu_id)
        return available

    def can_navigate_to(self, menu_id: str) -> bool:
        """Check if navigation to a menu is possible.

        Args:
            menu_id: ID of menu to check

        Returns:
            True if navigation is possible
        """
        return menu_id in self.get_available_options()

    def navigate(self, menu_id: str) -> bool:
        """Navigate to a menu.

        Args:
            menu_id: ID of menu to navigate to

        Returns:
            True if navigation succeeded
        """
        if self.can_navigate_to(menu_id):
            return self.state.navigate_to(menu_id)
        return False
