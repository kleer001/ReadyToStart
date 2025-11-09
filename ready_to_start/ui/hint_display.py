import json
import random
import time
from pathlib import Path
from typing import Any


class HintDisplay:
    def __init__(self, hints_file: str = "data/hints.json"):
        self.hints_database = {}
        self.shown_hints = set()
        self.last_hint_time = {}
        self.tutorial_progress = 0
        self.hint_count = 0
        self._load_hints(hints_file)

    def get_hint(
        self, category: str | None = None, context: dict[str, Any] | None = None
    ) -> str | None:
        if context is None:
            context = {}

        if not self._can_show_hint():
            return None

        tutorial_hint = self._check_tutorial_hints(context)
        if tutorial_hint:
            return tutorial_hint

        contextual_hint = self._check_contextual_hints(context)
        if contextual_hint:
            return contextual_hint

        return self._get_random_category_hint(category)

    def get_helpful_hint(self, category: str | None = None) -> str | None:
        return self._get_category_hint(category, helpful=True)

    def get_misleading_hint(self, category: str | None = None) -> str | None:
        return self._get_category_hint(category, helpful=False)

    def mark_tutorial_completed(self, step: int) -> None:
        self.tutorial_progress = max(self.tutorial_progress, step)

    def reset_tutorial(self) -> None:
        self.tutorial_progress = 0
        self.shown_hints.clear()

    def get_hint_count(self) -> int:
        return self.hint_count

    def reset_hint_count(self) -> None:
        self.hint_count = 0

    def _load_hints(self, filepath: str) -> None:
        path = Path(filepath)
        if not path.exists():
            self.hints_database = self._default_hints()
            return

        with open(path) as f:
            self.hints_database = json.load(f)

    def _can_show_hint(self) -> bool:
        rules = self.hints_database.get("hint_display_rules", {})
        max_hints = rules.get("max_hints_per_session", 50)

        if self.hint_count >= max_hints:
            return False

        min_cooldown = rules.get("min_cooldown_seconds", 30)
        current_time = time.time()

        if self.last_hint_time:
            last_time = max(self.last_hint_time.values())
            if current_time - last_time < min_cooldown:
                return False

        return True

    def _check_tutorial_hints(self, context: dict[str, Any]) -> str | None:
        tutorial = self.hints_database.get("tutorial_sequence", [])

        for hint_spec in tutorial:
            if hint_spec["step"] <= self.tutorial_progress:
                continue

            if self._check_tutorial_trigger(hint_spec, context):
                hint_id = f"tutorial_{hint_spec['step']}"
                if hint_spec.get("show_once", False) and hint_id in self.shown_hints:
                    continue

                self._mark_hint_shown(hint_id)
                self.tutorial_progress = hint_spec["step"]
                return hint_spec["hint"]

        return None

    def _check_contextual_hints(self, context: dict[str, Any]) -> str | None:
        contextual = self.hints_database.get("contextual_hints", [])

        for hint_spec in contextual:
            if self._check_hint_trigger(hint_spec, context):
                hint_id = f"contextual_{hint_spec['trigger']}"

                if hint_spec.get("show_once", False) and hint_id in self.shown_hints:
                    continue

                if not self._check_cooldown(hint_id, hint_spec):
                    continue

                self._mark_hint_shown(hint_id)
                return hint_spec["hint"]

        return None

    def _get_random_category_hint(self, category: str | None) -> str | None:
        rules = self.hints_database.get("hint_display_rules", {})
        helpful_ratio = rules.get("show_helpful_ratio", 0.7)

        is_helpful = random.random() < helpful_ratio
        return self._get_category_hint(category, helpful=is_helpful)

    def _get_category_hint(
        self, category: str | None, helpful: bool
    ) -> str | None:
        categories = self.hints_database.get("hint_categories", {})

        if category and category in categories:
            pool = categories[category]
        else:
            available_categories = list(categories.keys())
            if not available_categories:
                return None
            category = random.choice(available_categories)
            pool = categories[category]

        hint_type = "helpful" if helpful else "misleading"
        hints = pool.get(hint_type, [])

        if not hints:
            hints = pool.get("helpful", []) + pool.get("misleading", [])

        if not hints:
            return None

        hint = random.choice(hints)
        self._mark_hint_shown(f"category_{category}_{hint[:20]}")
        return hint

    def _check_tutorial_trigger(
        self, hint_spec: dict, context: dict[str, Any]
    ) -> bool:
        trigger = hint_spec["trigger"]

        trigger_handlers = {
            "game_start": lambda: context.get("game_just_started", False),
            "first_enable": lambda: context.get("first_setting_enabled", False),
            "first_navigation": lambda: context.get("first_menu_change", False),
            "first_dependency_encountered": lambda: context.get(
                "first_locked_encountered", False
            ),
            "first_dependency_solved": lambda: context.get(
                "first_dependency_solved", False
            ),
            "multiple_menus_visited": lambda: context.get("menus_visited", 0)
            >= hint_spec.get("threshold", 3),
            "first_value_dependency": lambda: context.get(
                "first_value_dep", False
            ),
            "mid_game": lambda: context.get("progress", 0.0)
            >= hint_spec.get("progress_threshold", 0.3),
        }

        handler = trigger_handlers.get(trigger)
        return handler() if handler else False

    def _check_hint_trigger(self, hint_spec: dict, context: dict[str, Any]) -> bool:
        trigger = hint_spec["trigger"]

        trigger_handlers = {
            "stuck_on_menu_for_minutes": lambda: context.get("time_on_menu", 0)
            >= hint_spec.get("threshold", 180),
            "many_failed_attempts": lambda: context.get("failed_attempts", 0)
            >= hint_spec.get("threshold", 5),
            "first_locked_encounter": lambda: context.get(
                "first_locked_encountered", False
            ),
            "rapid_clicking": lambda: context.get("clicks_per_minute", 0)
            >= hint_spec.get("threshold", 10),
            "circular_dependency_suspected": lambda: context.get(
                "circular_suspected", False
            ),
            "value_threshold_confusion": lambda: context.get(
                "value_threshold_attempts", 0
            )
            >= hint_spec.get("threshold", 3),
            "progress_plateau": lambda: context.get("time_since_progress", 0)
            >= hint_spec.get("duration", 600),
            "fake_error_believed": lambda: context.get("fake_error_count", 0) > 2,
            "high_completion_rate": lambda: context.get("completion_rate", 0.0)
            >= hint_spec.get("threshold", 0.75),
            "found_master_enable": lambda: context.get("master_enable_found", False),
            "found_advanced_mode": lambda: context.get("advanced_mode_found", False),
            "cascading_unlock": lambda: context.get("cascading_occurred", False),
        }

        handler = trigger_handlers.get(trigger)
        if not handler:
            return False

        applies_to = hint_spec.get("applies_to", [])
        if applies_to:
            category = context.get("category", "")
            if category not in applies_to:
                return False

        return handler()

    def _check_cooldown(self, hint_id: str, hint_spec: dict) -> bool:
        cooldown = hint_spec.get("cooldown", 0)
        if cooldown == 0:
            return True

        last_shown = self.last_hint_time.get(hint_id, 0)
        current_time = time.time()

        return (current_time - last_shown) >= cooldown

    def _mark_hint_shown(self, hint_id: str) -> None:
        self.shown_hints.add(hint_id)
        self.last_hint_time[hint_id] = time.time()
        self.hint_count += 1

    def _default_hints(self) -> dict:
        return {
            "hint_categories": {
                "navigation": {
                    "helpful": ["Use 'help' to see available commands"],
                    "misleading": ["Try random commands to discover secrets"],
                }
            },
            "hint_display_rules": {
                "max_hints_per_session": 50,
                "min_cooldown_seconds": 30,
            },
        }
