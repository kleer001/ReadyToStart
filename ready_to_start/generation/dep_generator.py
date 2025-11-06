import random

import networkx as nx

from ready_to_start.core.config_loader import GenerationConfig
from ready_to_start.core.dependencies import Dependency, SimpleDependency
from ready_to_start.core.enums import SettingState
from ready_to_start.core.menu import MenuNode


class DependencyGenerator:
    def __init__(
        self, graph: nx.DiGraph, config: GenerationConfig, menus: dict[str, MenuNode]
    ):
        self.graph = graph
        self.config = config
        self.menus = menus
        self.critical_path: list[str] = []

    def generate_dependencies(self) -> dict[str, list[Dependency]]:
        self.critical_path = self._find_critical_path()
        deps = {}

        self._add_menu_navigation_dependencies(deps)
        self._add_critical_path_dependencies(deps)
        self._add_cross_dependencies(deps)

        return deps

    def _find_critical_path(self) -> list[str]:
        start_nodes = self._get_start_nodes()
        end_nodes = self._get_end_nodes()

        longest_path = []
        for start in start_nodes:
            for end in end_nodes:
                if nx.has_path(self.graph, start, end):
                    path = nx.shortest_path(self.graph, start, end)
                    if len(path) > len(longest_path):
                        longest_path = path

        return longest_path

    def _add_menu_navigation_dependencies(
        self, deps: dict[str, list[Dependency]]
    ) -> None:
        for node_id in self.graph.nodes():
            menu = self.menus.get(node_id)
            if not menu or not menu.settings:
                continue

            critical_setting = menu.settings[0]

            for successor_id in self.graph.successors(node_id):
                successor_menu = self.menus.get(successor_id)
                if successor_menu and successor_menu.settings:
                    target_setting = successor_menu.settings[0]
                    if target_setting.id not in deps:
                        deps[target_setting.id] = []
                    deps[target_setting.id].append(
                        SimpleDependency(critical_setting.id, SettingState.ENABLED)
                    )

    def _add_critical_path_dependencies(
        self, deps: dict[str, list[Dependency]]
    ) -> None:
        for i in range(len(self.critical_path) - 1):
            current_menu = self.menus.get(self.critical_path[i])
            next_menu = self.menus.get(self.critical_path[i + 1])

            if not current_menu or not next_menu:
                continue
            if not current_menu.settings or not next_menu.settings:
                continue

            current_setting = random.choice(current_menu.settings)
            next_setting = random.choice(next_menu.settings)

            if next_setting.id not in deps:
                deps[next_setting.id] = []
            deps[next_setting.id].append(
                SimpleDependency(current_setting.id, SettingState.ENABLED)
            )

    def _add_cross_dependencies(self, deps: dict[str, list[Dependency]]) -> None:
        all_settings = []
        for menu in self.menus.values():
            all_settings.extend(menu.settings)

        if not all_settings:
            return

        num_cross = min(int(len(all_settings) * 0.1), 20)

        for _ in range(num_cross):
            setting_a = random.choice(all_settings)
            setting_b = random.choice(all_settings)
            if setting_a.id != setting_b.id:
                if setting_b.id not in deps:
                    deps[setting_b.id] = []
                deps[setting_b.id].append(
                    SimpleDependency(setting_a.id, SettingState.ENABLED)
                )

    def _get_start_nodes(self) -> list[str]:
        return [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]

    def _get_end_nodes(self) -> list[str]:
        return [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
