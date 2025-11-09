import configparser
from collections.abc import Callable
from dataclasses import dataclass

from ready_to_start.core.enums import SettingState
from ready_to_start.core.evaluator import DependencyEvaluator
from ready_to_start.core.game_state import GameState
from ready_to_start.core.types import Setting


@dataclass
class PropagationRule:
    trigger_setting: str
    trigger_condition: Callable[[Setting], bool]
    affected_settings: list[str]
    effect: Callable[[Setting], None]


class StatePropagator:
    MAX_DEPTH = 10

    def __init__(self, game_state: GameState, evaluator: DependencyEvaluator):
        self.state = game_state
        self.evaluator = evaluator
        self.rules: list[PropagationRule] = []
        self.propagation_depth = 0

    def add_rule(self, rule: PropagationRule) -> None:
        self.rules.append(rule)

    def propagate(self, changed_setting_id: str) -> list[str]:
        if self.propagation_depth >= self.MAX_DEPTH:
            return []

        self.propagation_depth += 1
        affected = self._apply_rules(changed_setting_id)
        self.propagation_depth -= 1
        return affected

    def load_rules_from_config(self, config_path: str) -> None:
        parser = configparser.ConfigParser()
        parser.read(config_path)

        for section in parser.sections():
            rule = self._parse_rule(parser[section])
            self.add_rule(rule)

    def _apply_rules(self, changed_setting_id: str) -> list[str]:
        setting = self.state.get_setting(changed_setting_id)
        if not setting:
            return []

        affected = []
        for rule in self._matching_rules(changed_setting_id, setting):
            affected.extend(self._apply_single_rule(rule))
        return affected

    def _matching_rules(
        self, setting_id: str, setting: Setting
    ) -> list[PropagationRule]:
        return [
            rule
            for rule in self.rules
            if rule.trigger_setting == setting_id and rule.trigger_condition(setting)
        ]

    def _apply_single_rule(self, rule: PropagationRule) -> list[str]:
        affected = []
        for target_id in rule.affected_settings:
            target = self.state.get_setting(target_id)
            if target:
                rule.effect(target)
                affected.append(target_id)
                self.evaluator.invalidate_cache(target_id)
                affected.extend(self.propagate(target_id))
        return affected

    def _parse_rule(self, section: configparser.SectionProxy) -> PropagationRule:
        trigger = section["trigger_setting"]
        condition = self._parse_condition(section["condition"])
        affected = [s.strip() for s in section["affected"].split(",")]
        effect = self._parse_effect(section["effect"])
        return PropagationRule(trigger, condition, affected, effect)

    def _parse_condition(self, cond_str: str) -> Callable[[Setting], bool]:
        if "==" in cond_str:
            attr, val = [s.strip() for s in cond_str.split("==")]

            def eq_check(s: Setting) -> bool:
                attr_val = getattr(s, attr)
                if isinstance(attr_val, SettingState):
                    return attr_val.value == val
                return str(attr_val) == val

            return eq_check
        elif ">" in cond_str:
            attr, val = [s.strip() for s in cond_str.split(">")]
            return lambda s: float(getattr(s, attr)) > float(val)
        elif "<" in cond_str:
            attr, val = [s.strip() for s in cond_str.split("<")]
            return lambda s: float(getattr(s, attr)) < float(val)
        return lambda s: True

    def _parse_effect(self, effect_str: str) -> Callable[[Setting], None]:
        if "=" not in effect_str:
            return lambda s: None

        attr, val = [s.strip() for s in effect_str.split("=", 1)]

        def apply_effect(s: Setting) -> None:
            current_type = type(getattr(s, attr))
            parsed_value = self._parse_value(val, current_type)
            setattr(s, attr, parsed_value)

        return apply_effect

    def _parse_value(self, val_str: str, target_type: type):
        has_origin = hasattr(target_type, "__origin__")
        is_type_origin = has_origin and target_type.__origin__ is type
        if target_type is SettingState or is_type_origin:
            return SettingState(val_str)
        elif target_type is bool:
            return val_str.lower() == "true"
        elif target_type is int:
            return int(val_str)
        elif target_type is float:
            return float(val_str)
        return val_str
