import random
from typing import TYPE_CHECKING

import networkx as nx

from src.core.dependencies import SimpleDependency
from src.core.enums import SettingState

if TYPE_CHECKING:
    from src.core.game_state import GameState


class BalanceTuner:
    DIFFICULTY_PRESETS = {
        "easy": {
            "max_density": 1.5,
            "max_chain": 3,
            "min_unlocked": 0.4,
            "starter_count": 5,
        },
        "medium": {
            "max_density": 2.5,
            "max_chain": 5,
            "min_unlocked": 0.3,
            "starter_count": 3,
        },
        "hard": {
            "max_density": 3.5,
            "max_chain": 7,
            "min_unlocked": 0.2,
            "starter_count": 2,
        },
        "very_hard": {
            "max_density": 5.0,
            "max_chain": 10,
            "min_unlocked": 0.1,
            "starter_count": 1,
        },
    }

    def __init__(self, game_state: "GameState"):
        self.game_state = game_state

    def apply_preset(self, difficulty: str) -> None:
        if difficulty not in self.DIFFICULTY_PRESETS:
            raise ValueError(f"Unknown difficulty: {difficulty}")

        preset = self.DIFFICULTY_PRESETS[difficulty]

        self._ensure_starter_settings(preset["starter_count"])
        self._reduce_dependency_density(preset["max_density"])
        self._simplify_long_chains(preset["max_chain"])
        self._ensure_minimum_unlocked(preset["min_unlocked"])

    def reduce_density(self, target_density: float) -> int:
        return self._reduce_dependency_density(target_density)

    def unlock_starters(self, count: int) -> int:
        return self._ensure_starter_settings(count)

    def simplify_chains(self, max_length: int) -> int:
        return self._simplify_long_chains(max_length)

    def ensure_unlocked_ratio(self, min_ratio: float) -> int:
        return self._ensure_minimum_unlocked(min_ratio)

    def _ensure_starter_settings(self, count: int) -> int:
        unlocked = [
            s
            for s in self.game_state.settings.values()
            if s.state == SettingState.ENABLED
        ]

        if len(unlocked) >= count:
            return 0

        locked = [
            s for s in self.game_state.settings.values() if s.state == SettingState.LOCKED
        ]

        candidates = [s for s in locked if s.id not in self.game_state.resolver.dependencies]

        if not candidates:
            candidates = sorted(
                locked,
                key=lambda s: len(self.game_state.resolver.dependencies.get(s.id, [])),
            )

        needed = count - len(unlocked)
        to_unlock = candidates[:needed]

        for setting in to_unlock:
            setting.state = SettingState.ENABLED
            if setting.id in self.game_state.resolver.dependencies:
                del self.game_state.resolver.dependencies[setting.id]

        return len(to_unlock)

    def _reduce_dependency_density(self, target_density: float) -> int:
        total_settings = len(self.game_state.settings)
        total_deps = sum(
            len(deps) for deps in self.game_state.resolver.dependencies.values()
        )

        current_density = total_deps / total_settings if total_settings > 0 else 0.0

        if current_density <= target_density:
            return 0

        target_deps = int(target_density * total_settings)
        to_remove = total_deps - target_deps

        graph = self._build_dependency_graph()
        removed = 0

        setting_deps = list(self.game_state.resolver.dependencies.items())
        random.shuffle(setting_deps)

        for setting_id, deps in setting_deps:
            if removed >= to_remove:
                break

            if len(deps) <= 1:
                continue

            temp_graph = graph.copy()
            dep_to_remove = deps[-1]

            if isinstance(dep_to_remove, SimpleDependency):
                if temp_graph.has_edge(dep_to_remove.setting_id, setting_id):
                    temp_graph.remove_edge(dep_to_remove.setting_id, setting_id)

            if nx.is_weakly_connected(temp_graph) or len(
                list(nx.weakly_connected_components(temp_graph))
            ) == len(list(nx.weakly_connected_components(graph))):
                deps.pop()
                removed += 1

                if len(deps) == 0:
                    del self.game_state.resolver.dependencies[setting_id]

        return removed

    def _simplify_long_chains(self, max_length: int) -> int:
        graph = self._build_dependency_graph()
        simplified = 0

        for setting_id in list(self.game_state.settings.keys()):
            try:
                ancestors = nx.ancestors(graph, setting_id)
                if len(ancestors) > max_length:
                    deps = self.game_state.resolver.dependencies.get(setting_id, [])
                    if len(deps) > 1:
                        self.game_state.resolver.dependencies[setting_id] = deps[:1]
                        simplified += 1
                    elif len(deps) == 1:
                        del self.game_state.resolver.dependencies[setting_id]
                        setting = self.game_state.get_setting(setting_id)
                        if setting and setting.state == SettingState.LOCKED:
                            setting.state = SettingState.DISABLED
                        simplified += 1
            except nx.NetworkXError:
                continue

        return simplified

    def _ensure_minimum_unlocked(self, min_ratio: float) -> int:
        total = len(self.game_state.settings)
        target_unlocked = int(total * min_ratio)

        unlockable = self._count_unlockable()

        if unlockable >= target_unlocked:
            return 0

        needed = target_unlocked - unlockable
        return self._unlock_random_locked(needed)

    def _build_dependency_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()

        for setting_id in self.game_state.settings:
            graph.add_node(setting_id)

        for setting_id, deps in self.game_state.resolver.dependencies.items():
            for dep in deps:
                if isinstance(dep, SimpleDependency):
                    graph.add_edge(dep.setting_id, setting_id)

        return graph

    def _count_unlockable(self) -> int:
        unlocked = set()

        for setting_id, setting in self.game_state.settings.items():
            if setting.state == SettingState.ENABLED:
                unlocked.add(setting_id)

        changed = True
        max_iterations = len(self.game_state.settings) * 2
        iteration = 0

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            for setting_id, setting in self.game_state.settings.items():
                if setting_id in unlocked:
                    continue

                if self._can_unlock_with(setting_id, unlocked):
                    unlocked.add(setting_id)
                    changed = True

        return len(unlocked)

    def _can_unlock_with(self, setting_id: str, unlocked: set[str]) -> bool:
        deps = self.game_state.resolver.dependencies.get(setting_id, [])

        for dep in deps:
            if isinstance(dep, SimpleDependency):
                if dep.setting_id not in unlocked:
                    if dep.required_state == SettingState.ENABLED:
                        return False

        return True

    def _unlock_random_locked(self, count: int) -> int:
        locked = [
            s for s in self.game_state.settings.values() if s.state == SettingState.LOCKED
        ]

        to_unlock = locked[:count]
        for setting in to_unlock:
            if setting.id in self.game_state.resolver.dependencies:
                del self.game_state.resolver.dependencies[setting.id]
            setting.state = SettingState.ENABLED

        return len(to_unlock)

    def get_adjustments_summary(self, difficulty: str) -> str:
        if difficulty not in self.DIFFICULTY_PRESETS:
            return f"Unknown difficulty: {difficulty}"

        preset = self.DIFFICULTY_PRESETS[difficulty]

        lines = [
            f"Balance Adjustments for {difficulty.upper()} difficulty:",
            f"",
            f"Target Parameters:",
            f"  Max Dependency Density: {preset['max_density']}",
            f"  Max Chain Length: {preset['max_chain']}",
            f"  Min Unlocked Ratio: {preset['min_unlocked']:.0%}",
            f"  Starter Settings: {preset['starter_count']}",
        ]

        return "\n".join(lines)
