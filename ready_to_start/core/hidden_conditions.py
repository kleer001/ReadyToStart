import configparser
from collections.abc import Callable
from dataclasses import dataclass

from ready_to_start.core.game_state import GameState


@dataclass
class HiddenCondition:
    id: str
    description: str
    check: Callable[[GameState], bool]
    triggered: bool = False
    trigger_count: int = 0


class HiddenConditionTracker:
    def __init__(self, game_state: GameState):
        self.state = game_state
        self.conditions: dict[str, HiddenCondition] = {}
        self.counters: dict[str, int] = {}

    def register_condition(self, condition: HiddenCondition) -> None:
        self.conditions[condition.id] = condition

    def increment_counter(self, key: str) -> None:
        self.counters[key] = self.counters.get(key, 0) + 1

    def check_all(self) -> list[str]:
        newly_triggered = []
        for cond_id, condition in self.conditions.items():
            if not condition.triggered and condition.check(self.state):
                condition.triggered = True
                condition.trigger_count += 1
                newly_triggered.append(cond_id)
        return newly_triggered

    def load_from_config(self, config_path: str) -> None:
        parser = configparser.ConfigParser()
        parser.read(config_path)

        for section in parser.sections():
            self.register_condition(self._parse_condition(section, parser[section]))

    def _parse_condition(
        self, cond_id: str, section: configparser.SectionProxy
    ) -> HiddenCondition:
        description = section["description"]
        check_str = section["check"]
        check_func = self._parse_check(check_str)
        return HiddenCondition(cond_id, description, check_func)

    def _parse_check(self, check_str: str) -> Callable[[GameState], bool]:
        if check_str.startswith("counter:"):
            return self._parse_counter_check(check_str[8:])
        elif check_str.startswith("setting:"):
            return self._parse_setting_check(check_str[8:])
        elif check_str.startswith("visited:"):
            return self._parse_visited_check(check_str[8:])
        return lambda state: False

    def _parse_counter_check(self, spec: str) -> Callable[[GameState], bool]:
        parts = spec.split()
        counter_name = parts[0]
        operator = parts[1]
        value = int(parts[2])

        def counter_check(state: GameState) -> bool:
            count = self.counters.get(counter_name, 0)
            return self._compare(count, operator, value)

        return counter_check

    def _parse_setting_check(self, spec: str) -> Callable[[GameState], bool]:
        parts = spec.split()
        setting_id = parts[0]
        operator = parts[1]
        expected_value = parts[2]

        def setting_check(state: GameState) -> bool:
            setting = state.get_setting(setting_id)
            if not setting:
                return False
            expected = self._convert_value(expected_value)
            return self._compare(setting.value, operator, expected)

        return setting_check

    def _parse_visited_check(self, spec: str) -> Callable[[GameState], bool]:
        menus = [m.strip() for m in spec.split(",")]
        return lambda state: all(m in state.visited_menus for m in menus)

    def _compare(self, left, operator: str, right) -> bool:
        ops = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }
        try:
            return ops.get(operator, lambda a, b: False)(left, right)
        except (TypeError, ValueError):
            return False

    def _convert_value(self, value_str: str):
        if value_str.lower() in ("true", "false"):
            return value_str.lower() == "true"
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            return value_str
