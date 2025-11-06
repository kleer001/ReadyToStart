import pytest
import networkx as nx
from ready_to_start.generation.dep_generator import DependencyGenerator
from ready_to_start.core.config_loader import GenerationConfig
from ready_to_start.core.dependencies import SimpleDependency
from ready_to_start.core.enums import SettingState


class TestDependencyGenerator:
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
    def simple_graph(self):
        graph = nx.DiGraph()
        graph.add_node("A")
        graph.add_node("B")
        graph.add_node("C")
        graph.add_edge("A", "B")
        graph.add_edge("B", "C")
        return graph

    def test_find_critical_path(self, config, simple_graph):
        gen = DependencyGenerator(simple_graph, config)
        path = gen._find_critical_path()
        assert len(path) == 3
        assert path[0] == "A"
        assert path[-1] == "C"

    def test_generate_dependencies_creates_map(self, config, simple_graph):
        gen = DependencyGenerator(simple_graph, config)
        deps = gen.generate_dependencies()
        assert isinstance(deps, dict)
        assert len(deps) > 0

    def test_critical_path_dependencies(self, config, simple_graph):
        gen = DependencyGenerator(simple_graph, config)
        deps = gen.generate_dependencies()

        assert "B" in deps
        assert len(deps["B"]) > 0
        assert isinstance(deps["B"][0], SimpleDependency)
        assert deps["B"][0].setting_id == "A"
        assert deps["B"][0].required_state == SettingState.ENABLED

    def test_can_add_dependency_same_node(self, config, simple_graph):
        gen = DependencyGenerator(simple_graph, config)
        assert not gen._can_add_dependency("A", "A")

    def test_can_add_dependency_path_exists(self, config, simple_graph):
        gen = DependencyGenerator(simple_graph, config)
        assert not gen._can_add_dependency("A", "B")
        assert not gen._can_add_dependency("B", "A")

    def test_can_add_dependency_valid(self, config):
        graph = nx.DiGraph()
        graph.add_node("A")
        graph.add_node("B")
        gen = DependencyGenerator(graph, config)
        assert gen._can_add_dependency("A", "B")

    def test_get_start_nodes(self, config, simple_graph):
        gen = DependencyGenerator(simple_graph, config)
        start_nodes = gen._get_start_nodes()
        assert start_nodes == ["A"]

    def test_get_end_nodes(self, config, simple_graph):
        gen = DependencyGenerator(simple_graph, config)
        end_nodes = gen._get_end_nodes()
        assert end_nodes == ["C"]

    def test_complex_graph(self, config):
        graph = nx.DiGraph()
        for i in range(5):
            graph.add_node(f"Node_{i}")

        graph.add_edge("Node_0", "Node_1")
        graph.add_edge("Node_1", "Node_2")
        graph.add_edge("Node_2", "Node_3")
        graph.add_edge("Node_3", "Node_4")

        gen = DependencyGenerator(graph, config)
        deps = gen.generate_dependencies()

        assert len(deps) > 0
        for dep_list in deps.values():
            for dep in dep_list:
                assert isinstance(dep, SimpleDependency)

    def test_cross_dependencies_added(self, config):
        graph = nx.DiGraph()
        for i in range(10):
            graph.add_node(f"Node_{i}")

        gen = DependencyGenerator(graph, config)
        deps = gen.generate_dependencies()

        total_deps = sum(len(dep_list) for dep_list in deps.values())
        assert total_deps > 0

    def test_deterministic_with_seed(self, config, simple_graph):
        import random

        random.seed(42)
        gen1 = DependencyGenerator(simple_graph, config)
        deps1 = gen1.generate_dependencies()

        random.seed(42)
        gen2 = DependencyGenerator(simple_graph, config)
        deps2 = gen2.generate_dependencies()

        assert len(deps1) == len(deps2)
        for key in deps1:
            if key in deps2:
                assert len(deps1[key]) == len(deps2[key])
