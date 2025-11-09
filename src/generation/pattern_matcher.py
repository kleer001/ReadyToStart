import json
import random
import re
from pathlib import Path
from typing import Any


class DependencyPatternMatcher:
    def __init__(self, patterns_file: str = "data/dependency_patterns.json"):
        self.patterns = []
        self.probabilities = {}
        self.density_modifiers = {}
        self.special_rules = {}
        self._load_patterns(patterns_file)

    def find_applicable_patterns(self, category_info: dict[str, Any]) -> list[dict]:
        applicable = []

        for pattern in self.patterns:
            if self._pattern_applies_to_category(pattern, category_info):
                applicable.append(pattern)

        return applicable

    def select_patterns_for_category(
        self, category_info: dict[str, Any]
    ) -> list[dict]:
        applicable = self.find_applicable_patterns(category_info)
        complexity = category_info["complexity"]
        density = category_info.get("dependency_density", "medium")

        complexity_probs = self.probabilities.get(f"complexity_{complexity}", {})
        density_modifier = self.density_modifiers.get(density, 1.0)

        selected = []
        for pattern in applicable:
            probability = complexity_probs.get(pattern["name"], 0.0)
            adjusted_probability = min(probability * density_modifier, 1.0)

            if random.random() < adjusted_probability:
                selected.append(pattern)

        if category_info["id"] in self.special_rules:
            selected.extend(
                self._apply_special_rules(category_info["id"], applicable)
            )

        return selected

    def apply_pattern(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        pattern_name = pattern["name"]
        handlers = {
            "master_enable": self._apply_master_enable,
            "advanced_gate": self._apply_advanced_gate,
            "value_threshold": self._apply_value_threshold,
            "chain_dependency": self._apply_chain,
            "sequential_unlock": self._apply_sequential,
            "group_requirement": self._apply_group_requirement,
            "cascading_unlock": self._apply_cascading,
            "inverse_dependency": self._apply_inverse,
        }

        handler = handlers.get(pattern_name, self._apply_generic)
        return handler(pattern, settings, category_id)

    def _load_patterns(self, filepath: str) -> None:
        path = Path(filepath)
        if not path.exists():
            return

        with open(path) as f:
            data = json.load(f)

        self.patterns = data.get("patterns", [])
        self.probabilities = data.get("pattern_probabilities", {})
        self.density_modifiers = data.get("density_modifiers", {})
        self.special_rules = data.get("special_category_rules", {})

    def _pattern_applies_to_category(
        self, pattern: dict, category_info: dict[str, Any]
    ) -> bool:
        applies_to = pattern.get("applies_to", [])

        if "all_categories" in applies_to:
            return True

        if category_info["id"] in applies_to:
            return True

        complexity_level = f"complexity_{category_info['complexity']}"
        if complexity_level in applies_to:
            return True

        density_map = {
            "low": "low_complexity",
            "medium": "medium_complexity",
            "high": "high_complexity",
            "very_high": "very_high_complexity",
        }
        density_key = density_map.get(category_info.get("dependency_density", ""))
        if density_key in applies_to:
            return True

        return False

    def _apply_special_rules(
        self, category_id: str, applicable_patterns: list[dict]
    ) -> list[dict]:
        rules = self.special_rules.get(category_id, {})
        always_include = rules.get("always_include", [])

        forced_patterns = []
        for pattern_name in always_include:
            pattern = next(
                (p for p in applicable_patterns if p["name"] == pattern_name), None
            )
            if pattern:
                forced_patterns.append(pattern)

        return forced_patterns

    def _apply_master_enable(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        master_id = f"{category_id}_enable"
        master = self._find_setting_by_id(settings, master_id)

        if not master:
            return []

        dependencies = []
        for setting in settings:
            if setting["id"] != master_id and not setting["id"].endswith(
                "_advanced_mode"
            ):
                dependencies.append(
                    (setting["id"], "simple", master_id, "enabled", "enabled")
                )

        return dependencies

    def _apply_advanced_gate(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        gate_id = f"{category_id}_advanced_mode"
        gate = self._find_setting_by_id(settings, gate_id)

        if not gate:
            return []

        dependencies = []
        for setting in settings:
            if "advanced" in setting["id"].lower() and setting["id"] != gate_id:
                dependencies.append(
                    (setting["id"], "simple", gate_id, "enabled", "enabled")
                )

        return dependencies

    def _apply_value_threshold(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        integer_settings = [s for s in settings if s.get("type") == "integer"]
        if len(integer_settings) < 2:
            return []

        random.shuffle(integer_settings)
        dependencies = []

        for i in range(min(3, len(integer_settings) - 1)):
            prerequisite = integer_settings[i]
            dependent = integer_settings[i + 1]
            threshold = (prerequisite.get("max_value", 100) + prerequisite.get("min_value", 0)) // 2

            dependencies.append(
                (dependent["id"], "value", prerequisite["id"], ">", threshold)
            )

        return dependencies

    def _apply_chain(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        chain_length = random.randint(3, 5)
        if len(settings) < chain_length:
            return []

        chain_settings = random.sample(settings, chain_length)
        dependencies = []

        for i in range(1, len(chain_settings)):
            dependencies.append(
                (
                    chain_settings[i]["id"],
                    "simple",
                    chain_settings[i - 1]["id"],
                    "enabled",
                    "enabled",
                )
            )

        return dependencies

    def _apply_sequential(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        sequence_length = random.randint(2, 4)
        if len(settings) < sequence_length:
            return []

        sequence = random.sample(settings, sequence_length)
        dependencies = []

        for i in range(1, len(sequence)):
            dependencies.append(
                (
                    sequence[i]["id"],
                    "simple",
                    sequence[i - 1]["id"],
                    "enabled",
                    "enabled",
                )
            )

        return dependencies

    def _apply_group_requirement(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        if len(settings) < 4:
            return []

        group_size = random.randint(3, min(5, len(settings) - 1))
        group = random.sample(settings[:-1], group_size)
        dependent = settings[-1]

        dependencies = []
        for group_member in group:
            dependencies.append(
                (
                    dependent["id"],
                    "simple",
                    group_member["id"],
                    "enabled",
                    "enabled",
                )
            )

        return dependencies

    def _apply_cascading(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        if len(settings) < 4:
            return []

        trigger = settings[0]
        unlock_count = random.randint(3, min(7, len(settings) - 1))
        unlocked = random.sample(settings[1:], unlock_count)

        dependencies = []
        for unlocked_setting in unlocked:
            dependencies.append(
                (
                    unlocked_setting["id"],
                    "simple",
                    trigger["id"],
                    "enabled",
                    "enabled",
                )
            )

        return dependencies

    def _apply_inverse(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        boolean_settings = [s for s in settings if s.get("type") == "boolean"]
        if len(boolean_settings) < 2:
            return []

        pair = random.sample(boolean_settings, 2)
        return [
            (pair[1]["id"], "simple_inverse", pair[0]["id"], "disabled", "disabled")
        ]

    def _apply_generic(
        self, pattern: dict, settings: list[dict], category_id: str
    ) -> list[tuple]:
        if len(settings) < 2:
            return []

        pair = random.sample(settings, 2)
        return [(pair[1]["id"], "simple", pair[0]["id"], "enabled", "enabled")]

    def _find_setting_by_id(
        self, settings: list[dict], setting_id: str
    ) -> dict | None:
        return next((s for s in settings if s["id"] == setting_id), None)

    def _matches_pattern(self, setting_id: str, pattern: str, category_id: str) -> bool:
        pattern = pattern.replace("{category}", category_id)
        pattern = pattern.replace("*", ".*")
        return re.match(pattern, setting_id) is not None
