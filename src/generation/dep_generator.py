import random

import networkx as nx

from src.core.config_loader import GenerationConfig
from src.core.dependencies import Dependency, SimpleDependency
from src.core.enums import SettingState
from src.core.menu import MenuNode
from src.generation.graph_analyzer import GraphAnalyzer

CROSS_DEPENDENCY_RATIO = 0.1
MAX_CROSS_DEPENDENCIES = 20


class DependencyGenerator:
    def __init__(
        self, graph: nx.DiGraph, config: GenerationConfig, menus: dict[str, MenuNode]
    ):
        self.graph = graph
        self.config = config
        self.menus = menus
        self.critical_path: list[str] = []

    def generate_dependencies(self) -> dict[str, list[Dependency]]:
        self.critical_path = GraphAnalyzer.find_critical_path(self.graph)
        deps = {}

        self._add_menu_navigation_dependencies(deps)
        self._add_critical_path_dependencies(deps)
        self._add_cross_dependencies(deps)

        return deps

    def _add_menu_navigation_dependencies(
        self, deps: dict[str, list[Dependency]]
    ) -> None:
        for node_id in self.graph.nodes():
            menu = self._get_valid_menu(node_id)
            if not menu:
                continue

            critical_setting = menu.settings[0]

            for successor_id in self.graph.successors(node_id):
                self._add_navigation_dependency(critical_setting.id, successor_id, deps)

    def _get_valid_menu(self, node_id: str) -> MenuNode | None:
        menu = self.menus.get(node_id)
        if menu and menu.settings:
            return menu
        return None

    def _add_navigation_dependency(
        self,
        source_setting_id: str,
        successor_id: str,
        deps: dict[str, list[Dependency]],
    ) -> None:
        successor_menu = self._get_valid_menu(successor_id)
        if not successor_menu:
            return

        target_setting = successor_menu.settings[0]
        if target_setting.id not in deps:
            deps[target_setting.id] = []
        deps[target_setting.id].append(
            SimpleDependency(source_setting_id, SettingState.ENABLED)
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

        num_cross = min(
            int(len(all_settings) * CROSS_DEPENDENCY_RATIO), MAX_CROSS_DEPENDENCIES
        )

        for _ in range(num_cross):
            setting_a = random.choice(all_settings)
            setting_b = random.choice(all_settings)
            if setting_a.id != setting_b.id and not self._would_create_cycle(
                deps, setting_a.id, setting_b.id
            ):
                if setting_b.id not in deps:
                    deps[setting_b.id] = []
                deps[setting_b.id].append(
                    SimpleDependency(setting_a.id, SettingState.ENABLED)
                )

    def _would_create_cycle(
        self, deps: dict[str, list[Dependency]], source_id: str, target_id: str
    ) -> bool:
        dep_graph = self._build_dependency_graph(deps)

        if not (dep_graph.has_node(target_id) and dep_graph.has_node(source_id)):
            return False

        return nx.has_path(dep_graph, target_id, source_id)

    def _build_dependency_graph(self, deps: dict[str, list[Dependency]]) -> nx.DiGraph:
        dep_graph = nx.DiGraph()

        for dependent_id, dep_list in deps.items():
            for dep in dep_list:
                dep_graph.add_edge(dep.setting_id, dependent_id)

        return dep_graph
