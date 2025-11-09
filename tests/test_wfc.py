import pytest
from src.generation.wfc import WFCCell, WFCGrid, WFCGenerator
from src.core.config_loader import GenerationConfig


class TestWFCCell:
    def test_initial_state(self):
        cell = WFCCell(position=(0, 0), possible_states={"A", "B", "C"})
        assert not cell.collapsed
        assert cell.state is None
        assert cell.entropy == float("inf")

    def test_collapse(self):
        cell = WFCCell(position=(0, 0), possible_states={"A", "B", "C"})
        state = cell.collapse()
        assert cell.collapsed
        assert cell.state == state
        assert cell.entropy == 0
        assert cell.possible_states == {state}

    def test_constrain(self):
        cell = WFCCell(position=(0, 0), possible_states={"A", "B", "C"})
        cell.constrain({"A", "C"})
        assert cell.possible_states == {"A", "C"}
        assert cell.entropy == 2

    def test_constrain_to_empty(self):
        cell = WFCCell(position=(0, 0), possible_states={"A", "B", "C"})
        cell.constrain({"D"})
        assert cell.possible_states == set()
        assert cell.entropy == 0


class TestWFCGrid:
    def test_initialization(self):
        grid = WFCGrid(width=3, height=3)
        assert len(grid.cells) == 9
        assert (0, 0) in grid.cells
        assert (2, 2) in grid.cells

    def test_get_neighbors_center(self):
        grid = WFCGrid(width=3, height=3)
        neighbors = grid.get_neighbors((1, 1))
        assert len(neighbors) == 4
        positions = [n.position for n in neighbors]
        assert (1, 2) in positions
        assert (2, 1) in positions
        assert (1, 0) in positions
        assert (0, 1) in positions

    def test_get_neighbors_corner(self):
        grid = WFCGrid(width=3, height=3)
        neighbors = grid.get_neighbors((0, 0))
        assert len(neighbors) == 2

    def test_get_lowest_entropy_cell(self):
        grid = WFCGrid(width=2, height=2)
        for cell in grid.cells.values():
            cell.possible_states = {"A", "B", "C"}
            cell.entropy = 3

        grid.cells[(0, 0)].entropy = 1
        grid.cells[(1, 1)].entropy = 2

        lowest = grid.get_lowest_entropy_cell()
        assert lowest.position == (0, 0)

    def test_is_complete_empty(self):
        grid = WFCGrid(width=2, height=2)
        assert not grid.is_complete()

    def test_is_complete_all_collapsed(self):
        grid = WFCGrid(width=2, height=2)
        for cell in grid.cells.values():
            cell.collapsed = True
        assert grid.is_complete()

    def test_has_contradiction(self):
        grid = WFCGrid(width=2, height=2)
        grid.cells[(0, 0)].entropy = 0
        grid.cells[(0, 0)].collapsed = False
        assert grid.has_contradiction()


class TestWFCGenerator:
    @pytest.fixture
    def simple_rules(self):
        return {
            "A": {"connections": ["B", "C"], "requires": []},
            "B": {"connections": ["A", "C"], "requires": []},
            "C": {"connections": ["A", "B"], "requires": []},
        }

    @pytest.fixture
    def config(self):
        return GenerationConfig(
            min_path_length=5,
            max_depth=15,
            required_categories=10,
            gate_distribution=0.3,
            critical_ratio=0.25,
            decoy_ratio=0.35,
            noise_ratio=0.40,
        )

    def test_initialization(self, simple_rules, config):
        generator = WFCGenerator(simple_rules, config)
        all_categories = {"A", "B", "C"}
        generator.initialize(all_categories)

        for cell in generator.grid.cells.values():
            assert cell.possible_states == all_categories
            assert cell.entropy == 3

    def test_propagate_constraints(self, simple_rules, config):
        generator = WFCGenerator(simple_rules, config)
        all_categories = {"A", "B", "C"}
        generator.initialize(all_categories)

        center_cell = generator.grid.cells[(2, 2)]
        center_cell.possible_states = {"A"}
        center_cell.collapse()

        generator.propagate(center_cell)

        neighbors = generator.grid.get_neighbors((2, 2))
        for neighbor in neighbors:
            if not neighbor.collapsed:
                assert neighbor.possible_states.issubset({"B", "C"})

    def test_generate_produces_grid(self, simple_rules, config):
        generator = WFCGenerator(simple_rules, config)
        grid = generator.generate()

        assert isinstance(grid, WFCGrid)
        collapsed_count = sum(1 for cell in grid.cells.values() if cell.collapsed)
        assert collapsed_count > 0

    def test_generate_deterministic_with_seed(self, simple_rules, config):
        import random

        random.seed(42)
        generator1 = WFCGenerator(simple_rules, config)
        grid1 = generator1.generate()

        random.seed(42)
        generator2 = WFCGenerator(simple_rules, config)
        grid2 = generator2.generate()

        for pos in grid1.cells:
            assert grid1.cells[pos].state == grid2.cells[pos].state
