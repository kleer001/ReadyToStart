import networkx as nx

from ready_to_start.core.config_loader import GenerationConfig
from ready_to_start.generation.graph_analyzer import GraphAnalyzer
from ready_to_start.generation.wfc import WFCGrid

MIN_GRAPH_NODES = 3


class TopologyConverter:
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.graph = nx.DiGraph()
        self.critical_path: list[str] = []

    def grid_to_graph(self, grid: WFCGrid) -> nx.DiGraph:
        self._add_nodes(grid)
        self._add_edges(grid)
        return self.graph

    def validate_graph(self) -> bool:
        if not self.graph.nodes():
            return False
        if len(self.graph.nodes()) < MIN_GRAPH_NODES:
            return False
        if not nx.is_weakly_connected(self.graph):
            return False
        return self._has_valid_critical_path()

    def prune_dead_ends(self) -> None:
        if not self.graph.nodes():
            return

        start_nodes = GraphAnalyzer.get_start_nodes(self.graph)
        if start_nodes:
            self._prune_using_start_nodes(start_nodes)
        else:
            self._prune_using_components()

    def get_critical_path(self) -> list[str]:
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

    def _create_node_id(self, state: str | None, pos: tuple[int, int]) -> str:
        return f"{state}_{pos[0]}_{pos[1]}"

    def _has_valid_critical_path(self) -> bool:
        path = self._find_critical_path()
        return len(path) >= self.config.min_path_length

    def _find_critical_path(self) -> list[str]:
        path = GraphAnalyzer.find_critical_path(self.graph)

        if not path:
            nodes = list(self.graph.nodes())
            if len(nodes) < self.config.min_path_length:
                return []
            return nodes[: self.config.min_path_length]

        return path

    def _prune_using_start_nodes(self, start_nodes: list[str]) -> None:
        max_reachable = set()
        for start in start_nodes:
            reachable = GraphAnalyzer.get_reachable_from(self.graph, start)
            if len(reachable) > len(max_reachable):
                max_reachable = reachable

        unreachable = set(self.graph.nodes()) - max_reachable
        self.graph.remove_nodes_from(unreachable)

    def _prune_using_components(self) -> None:
        components = list(nx.weakly_connected_components(self.graph))
        if len(components) > 1:
            largest = max(components, key=len)
            to_remove = set(self.graph.nodes()) - largest
            self.graph.remove_nodes_from(to_remove)
