import configparser
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from src.core.enums import CompletionState
from src.core.game_state import GameState
from src.core.progress import ProgressCalculator


class VictoryType(Enum):
    NONE = "none"
    PARTIAL = "partial"
    COMPLETE = "complete"
    SECRET = "secret"


@dataclass
class VictoryCondition:
    victory_type: VictoryType
    requirements: list[Callable[[GameState], bool]]
    next_layer: str | None = None


class VictoryDetector:
    def __init__(self, game_state: GameState, progress_calc: ProgressCalculator):
        self.state = game_state
        self.progress = progress_calc
        self.conditions: list[VictoryCondition] = []
        self.current_layer = 0

    def add_condition(self, condition: VictoryCondition) -> None:
        self.conditions.append(condition)

    def check_victory(self) -> VictoryCondition | None:
        for condition in self.conditions:
            if all(req(self.state) for req in condition.requirements):
                return condition
        return None

    def load_from_config(self, config_path: str) -> None:
        parser = configparser.ConfigParser()
        parser.read(config_path)

        for section in parser.sections():
            condition = self._parse_condition(parser[section])
            self.add_condition(condition)

    def _parse_condition(self, section: configparser.SectionProxy) -> VictoryCondition:
        victory_type = VictoryType(section["type"])
        req_strings = section["requirements"].split("&&")
        next_layer = section.get("next_layer", None)
        requirements = [self._parse_requirement(r.strip()) for r in req_strings]
        return VictoryCondition(victory_type, requirements, next_layer)

    def _parse_requirement(self, req_str: str) -> Callable[[GameState], bool]:
        if req_str == "critical_path_complete":
            return lambda state: self.progress.is_victory_condition_met()
        elif req_str.startswith("progress"):
            return self._parse_progress_requirement(req_str)
        elif req_str.startswith("menu:"):
            return self._parse_menu_requirement(req_str)
        elif req_str.startswith("hidden:"):
            return self._parse_hidden_requirement(req_str)
        return lambda state: False

    def _parse_progress_requirement(self, req_str: str) -> Callable[[GameState], bool]:
        parts = req_str.split()
        threshold = float(parts[2])
        return lambda state: self.progress.calculate_overall_progress() >= threshold

    def _parse_menu_requirement(self, req_str: str) -> Callable[[GameState], bool]:
        parts = req_str.split()
        menu_id = parts[0][5:]
        required_state = CompletionState(parts[2])

        def menu_check(state: GameState) -> bool:
            completion = self.progress.calculate_menu_completion(menu_id)
            return completion == required_state

        return menu_check

    def _parse_hidden_requirement(self, req_str: str) -> Callable[[GameState], bool]:
        return lambda state: False
