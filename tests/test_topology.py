import pytest
import networkx as nx
from ready_to_start.generation.topology import TopologyConverter
from ready_to_start.generation.wfc import WFCGrid, WFCCell
from ready_to_start.core.config_loader import GenerationConfig


class TestTopologyConverter:
    @pytest.fixture
    def config(self):
        return GenerationConfig(
            min_path_length=3,
            max_depth=15,
            required_categories=10,
            gate_distribution=0.3,
            critical_ratio=0.25,
            decoy_ratio=0.35,
            noise_ratio=0.40,
        )

    @pytest.fixture
    def simple_grid(self):
        grid = WFCGrid(width=3, height=1)
        grid.cells[(0, 0)].state = "A"
        grid.cells[(0, 0)].collapsed = True
        grid.cells[(1, 0)].state = "B"
        grid.cells[(1, 0)].collapsed = True
        grid.cells[(2, 0)].state = "C"
        grid.cells[(2, 0)].collapsed = True
        return grid

    def test_grid_to_graph_creates_nodes(self, config, simple_grid):
        converter = TopologyConverter(config)
        graph = converter.grid_to_graph(simple_grid)

        assert len(graph.nodes()) == 3
        assert "A_0_0" in graph.nodes()
        assert "B_1_0" in graph.nodes()
        assert "C_2_0" in graph.nodes()

    def test_grid_to_graph_creates_edges(self, config, simple_grid):
        converter = TopologyConverter(config)
        graph = converter.grid_to_graph(simple_grid)

        assert graph.has_edge("A_0_0", "B_1_0")
        assert graph.has_edge("B_1_0", "A_0_0")
        assert graph.has_edge("B_1_0", "C_2_0")
        assert graph.has_edge("C_2_0", "B_1_0")

    def test_grid_to_graph_stores_node_attributes(self, config, simple_grid):
        converter = TopologyConverter(config)
        graph = converter.grid_to_graph(simple_grid)

        assert graph.nodes["A_0_0"]["category"] == "A"
        assert graph.nodes["A_0_0"]["position"] == (0, 0)

    def test_validate_graph_with_connected_graph(self, config, simple_grid):
        converter = TopologyConverter(config)
        converter.grid_to_graph(simple_grid)
        assert converter.validate_graph()

    def test_validate_graph_with_disconnected_graph(self, config):
        converter = TopologyConverter(config)
        converter.graph.add_node("A")
        converter.graph.add_node("B")
        assert not converter.validate_graph()

    def test_get_critical_path(self, config, simple_grid):
        converter = TopologyConverter(config)
        converter.grid_to_graph(simple_grid)
        path = converter.get_critical_path()
        assert len(path) >= 1

    def test_prune_dead_ends(self, config):
        converter = TopologyConverter(config)
        converter.graph.add_node("A")
        converter.graph.add_node("B")
        converter.graph.add_node("C")
        converter.graph.add_edge("A", "B")

        converter.prune_dead_ends()

        assert "C" not in converter.graph.nodes()
        assert "A" in converter.graph.nodes()
        assert "B" in converter.graph.nodes()

    def test_create_node_id(self, config):
        converter = TopologyConverter(config)
        node_id = converter._create_node_id("Audio", (2, 3))
        assert node_id == "Audio_2_3"

    def test_get_start_nodes(self, config):
        converter = TopologyConverter(config)
        converter.graph.add_node("A")
        converter.graph.add_node("B")
        converter.graph.add_edge("A", "B")

        start_nodes = converter._get_start_nodes()
        assert start_nodes == ["A"]

    def test_get_end_nodes(self, config):
        converter = TopologyConverter(config)
        converter.graph.add_node("A")
        converter.graph.add_node("B")
        converter.graph.add_edge("A", "B")

        end_nodes = converter._get_end_nodes()
        assert end_nodes == ["B"]

    def test_grid_with_uncollapsed_cells(self, config):
        grid = WFCGrid(width=2, height=1)
        grid.cells[(0, 0)].state = "A"
        grid.cells[(0, 0)].collapsed = True

        converter = TopologyConverter(config)
        graph = converter.grid_to_graph(grid)

        assert len(graph.nodes()) == 1
        assert "A_0_0" in graph.nodes()
