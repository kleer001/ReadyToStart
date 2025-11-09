from dataclasses import dataclass
from typing import TYPE_CHECKING

import networkx as nx

from src.core.dependencies import SimpleDependency, ValueDependency
from src.core.enums import SettingState

if TYPE_CHECKING:
    from src.core.game_state import GameState


@dataclass
class DifficultyMetrics:
    dependency_density: float
    max_chain_length: int
    avg_chain_length: float
    locked_setting_ratio: float
    branching_factor: float
    critical_path_length: int
    total_settings: int
    total_dependencies: int


@dataclass
class DifficultyScore:
    overall: int
    metrics: DifficultyMetrics
    rating: str
    suggestions: list[str]


class DifficultyAnalyzer:
    DIFFICULTY_THRESHOLDS = {
        "trivial": 0,
        "easy": 20,
        "medium": 40,
        "hard": 60,
        "very_hard": 80,
    }

    def __init__(self, game_state: "GameState"):
        self.game_state = game_state

    def analyze(self) -> DifficultyScore:
        metrics = self._calculate_metrics()
        score = self._calculate_score(metrics)
        rating = self._determine_rating(score)
        suggestions = self._generate_suggestions(metrics, score)

        return DifficultyScore(
            overall=score, metrics=metrics, rating=rating, suggestions=suggestions
        )

    def _calculate_metrics(self) -> DifficultyMetrics:
        total_settings = len(self.game_state.settings)
        total_dependencies = sum(
            len(deps) for deps in self.game_state.resolver.dependencies.values()
        )

        dependency_density = (
            total_dependencies / total_settings if total_settings > 0 else 0.0
        )

        locked_count = sum(
            1
            for s in self.game_state.settings.values()
            if s.state == SettingState.LOCKED
        )
        locked_ratio = locked_count / total_settings if total_settings > 0 else 0.0

        graph = self._build_dependency_graph()
        max_chain = self._calculate_max_chain_length(graph)
        avg_chain = self._calculate_avg_chain_length(graph)
        branching = self._calculate_branching_factor(graph)
        critical_path = self._calculate_critical_path_length()

        return DifficultyMetrics(
            dependency_density=dependency_density,
            max_chain_length=max_chain,
            avg_chain_length=avg_chain,
            locked_setting_ratio=locked_ratio,
            branching_factor=branching,
            critical_path_length=critical_path,
            total_settings=total_settings,
            total_dependencies=total_dependencies,
        )

    def _calculate_score(self, metrics: DifficultyMetrics) -> int:
        density_score = min(metrics.dependency_density * 20, 30)
        chain_score = min(metrics.max_chain_length * 5, 25)
        locked_score = metrics.locked_setting_ratio * 20
        branching_score = min(metrics.branching_factor * 3, 15)
        critical_score = min(metrics.critical_path_length * 2, 10)

        total = (
            density_score + chain_score + locked_score + branching_score + critical_score
        )

        return min(int(total), 100)

    def _determine_rating(self, score: int) -> str:
        for rating, threshold in reversed(self.DIFFICULTY_THRESHOLDS.items()):
            if score >= threshold:
                return rating
        return "trivial"

    def _generate_suggestions(
        self, metrics: DifficultyMetrics, score: int
    ) -> list[str]:
        suggestions = []

        if metrics.dependency_density > 2.0:
            suggestions.append(
                "High dependency density detected - consider reducing interconnections"
            )

        if metrics.max_chain_length > 5:
            suggestions.append(
                f"Long dependency chains ({metrics.max_chain_length}) may frustrate players"
            )

        if metrics.locked_setting_ratio > 0.7:
            suggestions.append(
                "Too many locked settings - provide more accessible entry points"
            )

        if metrics.locked_setting_ratio < 0.3:
            suggestions.append(
                "Low challenge level - consider adding more dependencies"
            )

        if metrics.branching_factor < 1.5:
            suggestions.append(
                "Limited branching - add more parallel unlocking paths"
            )

        if metrics.critical_path_length < 3:
            suggestions.append("Short critical path - game may feel too simple")

        if score > 80:
            suggestions.append(
                "Overall difficulty very high - may discourage casual players"
            )
        elif score < 20:
            suggestions.append("Overall difficulty low - may bore experienced players")

        return suggestions

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

    def _calculate_max_chain_length(self, graph: nx.DiGraph) -> int:
        if not graph.nodes():
            return 0

        max_length = 0
        for component in nx.weakly_connected_components(graph):
            subgraph = graph.subgraph(component)
            if nx.is_directed_acyclic_graph(subgraph):
                try:
                    length = nx.dag_longest_path_length(subgraph)
                    max_length = max(max_length, length)
                except (nx.NetworkXError, ValueError):
                    pass

        return max_length

    def _calculate_avg_chain_length(self, graph: nx.DiGraph) -> float:
        if not graph.nodes():
            return 0.0

        total_length = 0
        count = 0

        for node in graph.nodes():
            ancestors = nx.ancestors(graph, node)
            total_length += len(ancestors)
            count += 1

        return total_length / count if count > 0 else 0.0

    def _calculate_branching_factor(self, graph: nx.DiGraph) -> float:
        if not graph.nodes():
            return 0.0

        total_successors = sum(graph.out_degree(node) for node in graph.nodes())
        nodes_with_successors = sum(
            1 for node in graph.nodes() if graph.out_degree(node) > 0
        )

        return (
            total_successors / nodes_with_successors if nodes_with_successors > 0 else 0.0
        )

    def _calculate_critical_path_length(self) -> int:
        if not self.game_state.menus:
            return 0

        graph = nx.DiGraph()
        for menu in self.game_state.menus.values():
            graph.add_node(menu.id)
            for connection in menu.connections:
                graph.add_edge(menu.id, connection)

        start_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        end_nodes = [n for n in graph.nodes() if graph.out_degree(n) == 0]

        max_length = 0
        for start in start_nodes:
            for end in end_nodes:
                if nx.has_path(graph, start, end):
                    path = nx.shortest_path(graph, start, end)
                    max_length = max(max_length, len(path) - 1)

        return max_length

    def get_report(self) -> str:
        analysis = self.analyze()
        m = analysis.metrics

        lines = [
            f"Difficulty Analysis Report",
            f"=" * 50,
            f"",
            f"Overall Score: {analysis.overall}/100 ({analysis.rating.upper()})",
            f"",
            f"Metrics:",
            f"  Total Settings: {m.total_settings}",
            f"  Total Dependencies: {m.total_dependencies}",
            f"  Dependency Density: {m.dependency_density:.2f}",
            f"  Max Chain Length: {m.max_chain_length}",
            f"  Avg Chain Length: {m.avg_chain_length:.2f}",
            f"  Locked Ratio: {m.locked_setting_ratio:.1%}",
            f"  Branching Factor: {m.branching_factor:.2f}",
            f"  Critical Path: {m.critical_path_length} menus",
        ]

        if analysis.suggestions:
            lines.append(f"\nSuggestions:")
            for suggestion in analysis.suggestions:
                lines.append(f"  - {suggestion}")

        return "\n".join(lines)
