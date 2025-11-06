from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode


class NavigationController:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.current_menu = None
        self.menu_stack = []
        self.command_history = []

    def navigate_to(self, menu_id: str) -> tuple[bool, str]:
        menu = self.game_state.get_menu(menu_id)
        if not menu:
            return False, f"Menu not found: {menu_id}"

        if not menu.is_accessible(self.game_state):
            return False, f"Menu not accessible: {menu_id}"

        if self.current_menu:
            self.menu_stack.append(self.current_menu.id)

        self.current_menu = menu
        menu.visited = True
        return True, ""

    def go_back(self) -> tuple[bool, str]:
        if not self.menu_stack:
            return False, "Already at root menu"

        previous_menu_id = self.menu_stack.pop()
        menu = self.game_state.get_menu(previous_menu_id)

        if not menu:
            return False, f"Previous menu not found: {previous_menu_id}"

        self.current_menu = menu
        return True, ""

    def find_menu_by_name(self, name: str) -> MenuNode | None:
        name_lower = name.lower()
        for menu_id, menu in self.game_state.menus.items():
            if menu.category.lower() == name_lower or menu_id.lower() == name_lower:
                return menu
        return None

    def get_available_menus(self) -> list[MenuNode]:
        if not self.current_menu:
            return []

        available = []
        for connection_id in self.current_menu.connections:
            menu = self.game_state.get_menu(connection_id)
            if menu and menu.is_accessible(self.game_state):
                available.append(menu)

        return available

    def add_command_to_history(self, command: str):
        self.command_history.append(command)

    def get_command_history(self, count: int = 10) -> list[str]:
        return self.command_history[-count:]
