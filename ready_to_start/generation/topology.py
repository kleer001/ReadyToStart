from typing import List, Optional, Set, Tuple

import networkx as nx

from ready_to_start.core.config_loader import GenerationConfig
from ready_to_start.generation.wfc import WFCGrid


class TopologyConverter:
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.graph = nx.DiGraph()
        self.critical_path: List[str] = []

    def grid_to_graph(self, grid: WFCGrid) -> nx.DiGraph:
        self._add_nodes(grid)
        self._add_edges(grid)
        return self.graph

    def validate_graph(self) -> bool:
        if not nx.is_weakly_connected(self.graph):
            return False
        return self._has_valid_critical_path()

    def prune_dead_ends(self) -> None:
        if not self.graph.nodes():
            return

        start_nodes = self._get_start_nodes()

        if start_nodes:
            max_reachable = set()
            for start in start_nodes:
                reachable = self._get_reachable_from_single_start(start)
                if len(reachable) > len(max_reachable):
                    max_reachable = reachable

            unreachable = set(self.graph.nodes()) - max_reachable
            self.graph.remove_nodes_from(unreachable)
        else:
            components = list(nx.weakly_connected_components(self.graph))
            if len(components) > 1:
                largest = max(components, key=len)
                to_remove = set(self.graph.nodes()) - largest
                self.graph.remove_nodes_from(to_remove)

    def get_critical_path(self) -> List[str]:
        if not self.critical_path:
            self.critical_path = self._find_critical_path()
        return self.critical_path

    def _add_nodes(self, grid: WFCGrid) -> None:
        for pos, cell in grid.cells.items():
            if cell.collapsed:
                node_id = self._create_node_id(cell.state, pos)
                self.graph.add_node(node_id, category=cell.state, position=pos)

    def _add_edges(self, grid: WFCGrid) -> None:
        for pos, cell in grid.cells.items():
            if not cell.collapsed:
                continue

            node_id = self._create_node_id(cell.state, pos)

            for neighbor in grid.get_neighbors(pos):
                if neighbor.collapsed:
                    neighbor_id = self._create_node_id(
                        neighbor.state, neighbor.position
                    )
                    self.graph.add_edge(node_id, neighbor_id)

    def _create_node_id(self, state: Optional[str], pos: Tuple[int, int]) -> str:
        return f"{state}_{pos[0]}_{pos[1]}"

    def _has_valid_critical_path(self) -> bool:
        path = self._find_critical_path()
        return len(path) >= self.config.min_path_length

    def _find_critical_path(self) -> List[str]:
        start_nodes = self._get_start_nodes()
        end_nodes = self._get_end_nodes()

        if not start_nodes or not end_nodes:
            nodes = list(self.graph.nodes())
            if len(nodes) < self.config.min_path_length:
                return []
            return nodes[: self.config.min_path_length]

        longest_path = []
        for start in start_nodes:
            for end in end_nodes:
                if nx.has_path(self.graph, start, end):
                    path = nx.shortest_path(self.graph, start, end)
                    if len(path) > len(longest_path):
                        longest_path = path

        return longest_path

    def _get_start_nodes(self) -> List[str]:
        return [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]

    def _get_end_nodes(self) -> List[str]:
        return [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]

    def _get_reachable_nodes(self, end_nodes: List[str]) -> Set[str]:
        reachable = set()
        for end in end_nodes:
            ancestors = nx.ancestors(self.graph, end)
            reachable.update(ancestors)
            reachable.add(end)
        return reachable

    def _get_reachable_from_starts(self, start_nodes: List[str]) -> Set[str]:
        reachable = set()
        for start in start_nodes:
            descendants = nx.descendants(self.graph, start)
            reachable.update(descendants)
            reachable.add(start)
        return reachable

    def _get_reachable_from_single_start(self, start: str) -> Set[str]:
        descendants = nx.descendants(self.graph, start)
        descendants.add(start)
        return descendants
