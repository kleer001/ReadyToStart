import random
from typing import Dict, List

import networkx as nx

from ready_to_start.core.config_loader import GenerationConfig
from ready_to_start.core.dependencies import Dependency, SimpleDependency
from ready_to_start.core.enums import SettingState


class DependencyGenerator:
    def __init__(self, graph: nx.DiGraph, config: GenerationConfig):
        self.graph = graph
        self.config = config
        self.critical_path: List[str] = []

    def generate_dependencies(self) -> Dict[str, List[Dependency]]:
        self.critical_path = self._find_critical_path()
        deps = {}

        self._add_critical_path_dependencies(deps)
        self._add_cross_dependencies(deps)

        return deps

    def _find_critical_path(self) -> List[str]:
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

    def _add_critical_path_dependencies(self, deps: Dict[str, List[Dependency]]) -> None:
        for i in range(len(self.critical_path) - 1):
            current = self.critical_path[i]
            next_node = self.critical_path[i + 1]

            if next_node not in deps:
                deps[next_node] = []

            deps[next_node].append(SimpleDependency(current, SettingState.ENABLED))

    def _add_cross_dependencies(self, deps: Dict[str, List[Dependency]]) -> None:
        nodes = list(self.graph.nodes())
        num_cross = int(len(nodes) * 0.2)

        for _ in range(num_cross):
            node_a = random.choice(nodes)
            node_b = random.choice(nodes)

            if self._can_add_dependency(node_a, node_b):
                if node_b not in deps:
                    deps[node_b] = []
                deps[node_b].append(SimpleDependency(node_a, SettingState.ENABLED))

    def _can_add_dependency(self, node_a: str, node_b: str) -> bool:
        if node_a == node_b:
            return False
        if nx.has_path(self.graph, node_a, node_b):
            return False
        if nx.has_path(self.graph, node_b, node_a):
            return False
        return True

    def _get_start_nodes(self) -> List[str]:
        return [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]

    def _get_end_nodes(self) -> List[str]:
        return [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
