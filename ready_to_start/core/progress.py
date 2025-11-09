from ready_to_start.core.enums import CompletionState, SettingState
from ready_to_start.core.evaluator import DependencyEvaluator
from ready_to_start.core.game_state import GameState


class ProgressCalculator:
    def __init__(self, game_state: GameState, evaluator: DependencyEvaluator):
        self.state = game_state
        self.evaluator = evaluator

    def calculate_overall_progress(self) -> float:
        total_settings = len(self.state.settings)
        if total_settings == 0:
            return 0.0

        configured = self._count_configured_settings()
        visited_bonus = len(self.state.visited_menus) * 0.5
        raw_progress = (configured + visited_bonus) / total_settings

        return min(99.0, raw_progress * 100)

    def calculate_menu_completion(self, menu_id: str) -> CompletionState:
        menu = self.state.get_menu(menu_id)
        if not menu:
            return CompletionState.INCOMPLETE

        total = len(menu.settings)
        if total == 0:
            return CompletionState.COMPLETE

        enabled = self._count_enabled_settings(menu.settings)

        if enabled == 0:
            return CompletionState.INCOMPLETE
        elif enabled == total:
            return CompletionState.COMPLETE
        else:
            return CompletionState.PARTIAL

    def get_critical_path_progress(self) -> float:
        visited_count = len(self.state.visited_menus)
        total_menus = len(self.state.menus)
        return (visited_count / total_menus) * 100 if total_menus > 0 else 0.0

    def is_victory_condition_met(self) -> bool:
        critical_total = 0
        critical_enabled = 0

        for setting_id, setting in self.state.settings.items():
            if self._is_critical_setting(setting_id):
                critical_total += 1
                if setting.state == SettingState.ENABLED:
                    critical_enabled += 1

        return critical_total > 0 and critical_enabled == critical_total

    def _count_configured_settings(self) -> int:
        return sum(
            1
            for s in self.state.settings.values()
            if s.state in [SettingState.ENABLED, SettingState.LOCKED]
        )

    def _count_enabled_settings(self, settings: list) -> int:
        return sum(1 for s in settings if s.state == SettingState.ENABLED)

    def _is_critical_setting(self, setting_id: str) -> bool:
        return setting_id in self.state.resolver.dependencies
