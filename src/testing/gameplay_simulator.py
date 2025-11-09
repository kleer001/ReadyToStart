import time
from typing import TYPE_CHECKING

from src.core.enums import SettingState
from src.testing.playtest_session import PlaytestTracker

if TYPE_CHECKING:
    from src.core.game_state import GameState


class GameplaySimulator:
    def __init__(self, game_state: "GameState", tracker: PlaytestTracker):
        self.game_state = game_state
        self.tracker = tracker
        self.running = False

    def start(self) -> None:
        self.running = True
        if self.game_state.current_menu:
            self.tracker.record_menu_visit(self.game_state.current_menu)

    def stop(self) -> None:
        self.running = False

    def get_current_menu(self):
        if not self.game_state.current_menu:
            return None
        return self.game_state.get_menu(self.game_state.current_menu)

    def get_available_menus(self) -> list:
        current_menu = self.get_current_menu()
        if not current_menu:
            return []

        available = []
        for menu_id in current_menu.connections:
            menu = self.game_state.get_menu(menu_id)
            if menu and menu.is_accessible(self.game_state):
                available.append(menu)

        return available

    def get_available_settings(self) -> list:
        current_menu = self.get_current_menu()
        if not current_menu:
            return []

        return [
            s
            for s in current_menu.settings
            if s.state in (SettingState.ENABLED, SettingState.DISABLED)
        ]

    def navigate_to_menu(self, menu_id: str) -> bool:
        menu = self.game_state.get_menu(menu_id)
        if not menu:
            self.tracker.record_error(f"Menu not found: {menu_id}")
            return False

        if not menu.is_accessible(self.game_state):
            self.tracker.record_error(f"Menu not accessible: {menu_id}")
            return False

        if self.game_state.navigate_to(menu_id):
            self.tracker.record_menu_visit(menu_id)
            return True

        return False

    def toggle_setting(self, setting_id: str) -> bool:
        setting = self.game_state.get_setting(setting_id)
        if not setting:
            self.tracker.record_error(f"Setting not found: {setting_id}")
            return False

        if setting.state == SettingState.LOCKED:
            hints = self.game_state.get_dependency_hints(setting_id)
            self.tracker.record_setting_interaction(
                setting_id, "toggle_locked", None, False
            )
            return False

        if setting.state == SettingState.DISABLED:
            new_state = SettingState.ENABLED
            new_value = True
        else:
            new_state = SettingState.DISABLED
            new_value = False

        setting.state = new_state
        setting.value = new_value
        setting.visit_count += 1
        setting.last_modified = time.time()

        self.game_state.propagate_changes()

        self.tracker.record_setting_interaction(setting_id, "toggle", new_value, True)
        return True

    def get_progress(self) -> dict:
        total_settings = len(self.game_state.settings)
        enabled_settings = sum(
            1
            for s in self.game_state.settings.values()
            if s.state == SettingState.ENABLED
        )

        total_menus = len(self.game_state.menus)
        visited_menus = len(self.game_state.visited_menus)

        return {
            "settings_enabled": enabled_settings,
            "settings_total": total_settings,
            "settings_percent": (
                enabled_settings / total_settings * 100 if total_settings > 0 else 0
            ),
            "menus_visited": visited_menus,
            "menus_total": total_menus,
            "menus_percent": (
                visited_menus / total_menus * 100 if total_menus > 0 else 0
            ),
        }

    def is_victory(self) -> bool:
        progress = self.get_progress()
        return progress["settings_percent"] >= 100

    def get_hints_for_setting(self, setting_id: str) -> list[str]:
        return self.game_state.get_dependency_hints(setting_id)
