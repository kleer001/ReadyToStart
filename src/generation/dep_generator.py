import random

import networkx as nx

from src.core.config_loader import DifficultyConfig, GenerationConfig
from src.core.dependencies import Dependency, SimpleDependency
from src.core.enums import SettingState
from src.core.menu import MenuNode
from src.generation.graph_analyzer import GraphAnalyzer


class DependencyGenerator:
    def __init__(
        self, graph: nx.DiGraph, config: GenerationConfig, menus: dict[str, MenuNode]
    ):
        self.graph = graph
        self.config = config
        self.menus = menus
        self.critical_path: list[str] = []
        self.difficulty_config: DifficultyConfig | None = None

    def generate_dependencies(self) -> dict[str, list[Dependency]]:
        """Generate dependencies using Gaussian distribution for dependency counts."""
        self.critical_path = GraphAnalyzer.find_critical_path(self.graph)

        # Calculate difficulty config based on total settings
        total_settings = sum(len(menu.settings) for menu in self.menus.values())
        self.difficulty_config = DifficultyConfig.for_tier(
            self.config.difficulty_tier, total_settings
        )

        deps = {}

        self._add_menu_navigation_dependencies(deps)
        self._add_critical_path_dependencies(deps)
        self._add_gaussian_cross_dependencies(deps)

        return deps

    def _sample_dependency_count(self) -> int:
        """Sample number of dependencies from Gaussian distribution.

        Returns:
            Number of dependencies, clamped to [min, max] range
        """
        if not self.difficulty_config:
            return 1

        # Sample from normal distribution
        sample = random.gauss(
            self.difficulty_config.mean_dependencies,
            self.difficulty_config.std_dev
        )

        # Clamp to min/max and round to integer
        count = int(round(sample))
        count = max(self.difficulty_config.min_dependencies, count)
        count = min(self.difficulty_config.max_dependencies, count)

        return count

    def _add_menu_navigation_dependencies(
        self, deps: dict[str, list[Dependency]]
    ) -> None:
        """Add dependencies for menu navigation."""
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

        # Check if adding this dependency would create a cycle
        if self._would_create_cycle(deps, source_setting_id, target_setting.id):
            return

        if target_setting.id not in deps:
            deps[target_setting.id] = []
        deps[target_setting.id].append(
            SimpleDependency(source_setting_id, SettingState.ENABLED)
        )

    def _add_critical_path_dependencies(
        self, deps: dict[str, list[Dependency]]
    ) -> None:
        """Add dependencies along the critical path."""
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

    def _add_gaussian_cross_dependencies(self, deps: dict[str, list[Dependency]]) -> None:
        """Add cross-dependencies using Gaussian distribution for counts.

        Each setting gets a number of dependencies sampled from Gaussian distribution,
        clamped to the difficulty tier's min/max bounds.
        """
        all_settings = []
        for menu in self.menus.values():
            all_settings.extend(menu.settings)

        if not all_settings:
            return

        # For each setting, add dependencies based on Gaussian sample
        for setting in all_settings:
            # Skip if already has many dependencies
            existing_count = len(deps.get(setting.id, []))

            # Determine target dependency count
            target_count = self._sample_dependency_count()

            # Add dependencies to reach target (avoid over-adding)
            deps_to_add = max(0, target_count - existing_count)

            for _ in range(deps_to_add):
                # Pick random setting as dependency source
                candidate = random.choice(all_settings)

                # Ensure not self-dependent and no cycles
                if candidate.id != setting.id and not self._would_create_cycle(
                    deps, candidate.id, setting.id
                ):
                    if setting.id not in deps:
                        deps[setting.id] = []
                    deps[setting.id].append(
                        SimpleDependency(candidate.id, SettingState.ENABLED)
                    )

    def _would_create_cycle(
        self, deps: dict[str, list[Dependency]], source_id: str, target_id: str
    ) -> bool:
        """Check if adding dependency would create a cycle."""
        dep_graph = self._build_dependency_graph(deps)

        if not (dep_graph.has_node(target_id) and dep_graph.has_node(source_id)):
            return False

        return nx.has_path(dep_graph, target_id, source_id)

    def _build_dependency_graph(self, deps: dict[str, list[Dependency]]) -> nx.DiGraph:
        """Build networkx graph from dependencies for cycle detection."""
        dep_graph = nx.DiGraph()

        for dependent_id, dep_list in deps.items():
            for dep in dep_list:
                if hasattr(dep, 'setting_id'):
                    dep_graph.add_edge(dep.setting_id, dependent_id)

        return dep_graph
