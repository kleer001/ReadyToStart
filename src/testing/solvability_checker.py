from dataclasses import dataclass
from typing import TYPE_CHECKING

import networkx as nx

from src.core.dependencies import SimpleDependency, ValueDependency
from src.core.enums import SettingState

if TYPE_CHECKING:
    from src.core.game_state import GameState


@dataclass
class SolvabilityIssue:
    type: str
    description: str
    affected_items: list[str]
    severity: str


class SolvabilityChecker:
    def __init__(self, game_state: "GameState"):
        self.game_state = game_state
        self.issues: list[SolvabilityIssue] = []

    def validate(self) -> bool:
        self.issues.clear()

        self._check_circular_dependencies()
        self._check_impossible_dependencies()
        self._check_menu_connectivity()
        self._check_unlockable_settings()
        self._check_victory_reachability()

        return len(self.issues) == 0

    def _check_circular_dependencies(self) -> None:
        graph = self._build_dependency_graph()

        # Find strongly connected components (groups of nodes with cycles)
        # Report one issue per component instead of every cycle path
        strongly_connected = list(nx.strongly_connected_components(graph))

        for component in strongly_connected:
            # Only report if component has more than 1 node (actual cycle)
            if len(component) > 1:
                component_list = sorted(list(component))
                # Find a simple cycle within this component to show as example
                subgraph = graph.subgraph(component)
                try:
                    # Get one representative cycle from this component
                    cycles = nx.simple_cycles(subgraph)
                    example_cycle = next(cycles, component_list)
                    self.issues.append(
                        SolvabilityIssue(
                            type="circular_dependency",
                            description=f"Circular dependency group ({len(component)} settings): {' -> '.join(list(example_cycle) + [list(example_cycle)[0]])}",
                            affected_items=component_list,
                            severity="critical",
                        )
                    )
                except (StopIteration, nx.NetworkXNoCycle):
                    # Fallback if we can't find a cycle (shouldn't happen)
                    self.issues.append(
                        SolvabilityIssue(
                            type="circular_dependency",
                            description=f"Circular dependency group detected with {len(component)} settings",
                            affected_items=component_list,
                            severity="critical",
                        )
                    )

    def _check_impossible_dependencies(self) -> None:
        for setting_id, deps in self.game_state.resolver.dependencies.items():
            setting = self.game_state.get_setting(setting_id)
            if not setting:
                continue

            for dep in deps:
                if isinstance(dep, SimpleDependency):
                    target = self.game_state.get_setting(dep.setting_id)
                    if not target:
                        self.issues.append(
                            SolvabilityIssue(
                                type="missing_dependency",
                                description=f"Setting '{setting.label}' depends on non-existent setting '{dep.setting_id}'",
                                affected_items=[setting_id, dep.setting_id],
                                severity="critical",
                            )
                        )
                elif isinstance(dep, ValueDependency):
                    setting_a = self.game_state.get_setting(dep.setting_a)
                    setting_b = self.game_state.get_setting(dep.setting_b)

                    if not setting_a or not setting_b:
                        missing = []
                        if not setting_a:
                            missing.append(dep.setting_a)
                        if not setting_b:
                            missing.append(dep.setting_b)

                        self.issues.append(
                            SolvabilityIssue(
                                type="missing_dependency",
                                description=f"Value dependency references non-existent settings: {missing}",
                                affected_items=[setting_id] + missing,
                                severity="critical",
                            )
                        )

    def _check_menu_connectivity(self) -> None:
        if not self.game_state.menus:
            return

        graph = nx.DiGraph()
        for menu in self.game_state.menus.values():
            graph.add_node(menu.id)
            for connection in menu.connections:
                graph.add_edge(menu.id, connection)

        start_menu = self.game_state.current_menu
        if not start_menu:
            self.issues.append(
                SolvabilityIssue(
                    type="no_start_menu",
                    description="No starting menu defined",
                    affected_items=[],
                    severity="critical",
                )
            )
            return

        reachable = nx.descendants(graph, start_menu)
        reachable.add(start_menu)

        unreachable = set(graph.nodes()) - reachable
        if unreachable:
            self.issues.append(
                SolvabilityIssue(
                    type="unreachable_menus",
                    description=f"Menus unreachable from start: {sorted(unreachable)}",
                    affected_items=sorted(unreachable),
                    severity="warning",
                )
            )

    def _check_unlockable_settings(self) -> None:
        unlockable = self._simulate_unlocking()

        all_settings = set(self.game_state.settings.keys())
        locked_forever = all_settings - unlockable

        if locked_forever:
            for setting_id in locked_forever:
                setting = self.game_state.get_setting(setting_id)
                if setting and setting.state == SettingState.LOCKED:
                    self.issues.append(
                        SolvabilityIssue(
                            type="unlockable_setting",
                            description=f"Setting '{setting.label}' can never be unlocked",
                            affected_items=[setting_id],
                            severity="critical",
                        )
                    )

    def _check_victory_reachability(self) -> None:
        unlockable = self._simulate_unlocking()
        total_settings = len(self.game_state.settings)

        if len(unlockable) < total_settings * 0.5:
            self.issues.append(
                SolvabilityIssue(
                    type="low_completion_rate",
                    description=f"Only {len(unlockable)}/{total_settings} settings can be unlocked",
                    affected_items=[],
                    severity="warning",
                )
            )

    def _build_dependency_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()

        for setting_id in self.game_state.settings:
            graph.add_node(setting_id)

        for setting_id, deps in self.game_state.resolver.dependencies.items():
            for dep in deps:
                if isinstance(dep, SimpleDependency):
                    graph.add_edge(dep.setting_id, setting_id)
                elif isinstance(dep, ValueDependency):
                    graph.add_edge(dep.setting_a, setting_id)
                    graph.add_edge(dep.setting_b, setting_id)

        return graph

    def _simulate_unlocking(self) -> set[str]:
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

        return unlocked

    def _can_unlock_with(self, setting_id: str, unlocked: set[str]) -> bool:
        deps = self.game_state.resolver.dependencies.get(setting_id, [])

        for dep in deps:
            if isinstance(dep, SimpleDependency):
                if dep.setting_id not in unlocked:
                    if dep.required_state == SettingState.ENABLED:
                        return False
            elif isinstance(dep, ValueDependency):
                if dep.setting_a not in unlocked or dep.setting_b not in unlocked:
                    return False

        return True

    def get_report(self) -> str:
        if not self.issues:
            return "✓ Game is solvable - no issues detected"

        critical = [i for i in self.issues if i.severity == "critical"]
        warnings = [i for i in self.issues if i.severity == "warning"]

        lines = [f"Found {len(self.issues)} solvability issues:"]

        if critical:
            lines.append(f"\nCritical Issues ({len(critical)}):")
            for issue in critical:
                lines.append(f"  - {issue.description}")

        if warnings:
            lines.append(f"\nWarnings ({len(warnings)}):")
            for issue in warnings:
                lines.append(f"  - {issue.description}")

        return "\n".join(lines)
