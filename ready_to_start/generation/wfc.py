import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ready_to_start.core.config_loader import GenerationConfig


@dataclass
class WFCCell:
    position: Tuple[int, int]
    possible_states: Set[str]
    collapsed: bool = False
    state: Optional[str] = None
    entropy: float = float("inf")

    def collapse(self) -> str:
        self.state = random.choice(list(self.possible_states))
        self.collapsed = True
        self.possible_states = {self.state}
        self.entropy = 0
        return self.state

    def constrain(self, allowed: Set[str]) -> None:
        self.possible_states &= allowed
        self.entropy = len(self.possible_states)


@dataclass
class WFCGrid:
    width: int
    height: int
    cells: Dict[Tuple[int, int], WFCCell] = field(default_factory=dict)

    def __post_init__(self):
        for x in range(self.width):
            for y in range(self.height):
                self.cells[(x, y)] = WFCCell(
                    position=(x, y), possible_states=set()
                )

    def get_neighbors(self, pos: Tuple[int, int]) -> List[WFCCell]:
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.cells:
                neighbors.append(self.cells[(nx, ny)])
        return neighbors

    def get_lowest_entropy_cell(self) -> Optional[WFCCell]:
        uncollapsed = [
            cell
            for cell in self.cells.values()
            if not cell.collapsed and cell.entropy > 0
        ]
        if not uncollapsed:
            return None
        return min(uncollapsed, key=lambda c: c.entropy)

    def is_complete(self) -> bool:
        return all(cell.collapsed for cell in self.cells.values())

    def has_contradiction(self) -> bool:
        return any(
            cell.entropy == 0 and not cell.collapsed for cell in self.cells.values()
        )


class WFCGenerator:
    def __init__(self, rules: Dict[str, Dict[str, List[str]]], config: GenerationConfig):
        self.rules = rules
        self.config = config
        self.grid = WFCGrid(width=5, height=5)

    def initialize(self, all_categories: Set[str]) -> None:
        for cell in self.grid.cells.values():
            cell.possible_states = all_categories.copy()
            cell.entropy = len(all_categories)

    def propagate(self, cell: WFCCell) -> None:
        queue = [cell]
        visited = set()

        while queue:
            current = queue.pop(0)
            if current.position in visited:
                continue
            visited.add(current.position)

            if not current.collapsed:
                continue

            valid_neighbors = set(self.rules.get(current.state, {}).get("connections", []))

            for neighbor in self.grid.get_neighbors(current.position):
                if neighbor.collapsed:
                    continue

                old_entropy = neighbor.entropy
                neighbor.constrain(valid_neighbors)

                if neighbor.entropy < old_entropy and neighbor.entropy > 0:
                    queue.append(neighbor)

    def generate(self) -> WFCGrid:
        all_categories = set(self.rules.keys())
        self.initialize(all_categories)

        start_pos = (self.grid.width // 2, self.grid.height // 2)
        start_cell = self.grid.cells[start_pos]
        start_cell.collapse()
        self.propagate(start_cell)

        max_iterations = self.grid.width * self.grid.height * 2
        iterations = 0

        while not self.grid.is_complete() and iterations < max_iterations:
            cell = self.grid.get_lowest_entropy_cell()
            if not cell:
                break

            if self.grid.has_contradiction():
                break

            cell.collapse()
            self.propagate(cell)
            iterations += 1

        return self.grid
