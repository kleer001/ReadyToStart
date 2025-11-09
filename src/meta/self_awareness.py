import json
from pathlib import Path
from random import choice, random
from time import time


class SelfAwarenessSystem:
    def __init__(self):
        self.comments: list[dict] = []
        self.triggered_comments: set[str] = set()
        self.awareness_level = 0
        self.last_comment_time = 0.0
        self.comment_cooldown = 30.0
        self._trigger_checkers = self._build_trigger_checkers()

    def _build_trigger_checkers(self) -> dict[str, callable]:
        return {
            "time_spent_excessive": lambda c: c.get("time_spent", 0) > 600,
            "many_failed_attempts": lambda c: c.get("failed_attempts", 0) > 10,
            "circular_dependency_attempt": lambda c: c.get("circular_detected", False),
            "progress_not_real": lambda c: c.get("fake_progress_shown", False),
            "glitch_occurred": lambda c: c.get("glitch_count", 0) > 0,
            "layer_transition": lambda c: c.get("layer_changed", False),
            "deep_layer_reached": lambda c: c.get("layer_depth", 0) >= 5,
            "found_secret": lambda c: c.get("secret_found", False),
            "quit_attempt": lambda c: c.get("tried_to_quit", False),
            "reading_help": lambda c: c.get("viewing_help", False),
        }

    def load_comments(self, comments_file: str | Path):
        with open(comments_file) as f:
            data = json.load(f)
        self.comments = data["comments"]

    def should_trigger_comment(self, context: dict) -> bool:
        if time() - self.last_comment_time < self.comment_cooldown:
            return False

        base_probability = 0.02 + (self.awareness_level * 0.01)
        return random() < base_probability

    def get_contextual_comment(self, context: dict) -> str | None:
        eligible = self._find_eligible_comments(context)
        if not eligible:
            return None

        selected = choice(eligible)
        self.triggered_comments.add(selected["id"])
        self.last_comment_time = time()
        return selected["text"]

    def _find_eligible_comments(self, context: dict) -> list[dict]:
        eligible = []
        for comment_data in self.comments:
            if self._is_comment_eligible(comment_data, context):
                eligible.append(comment_data)
        return eligible

    def _is_comment_eligible(self, comment_data: dict, context: dict) -> bool:
        if comment_data.get("show_once", False):
            if comment_data["id"] in self.triggered_comments:
                return False

        if not self._check_trigger(comment_data["trigger"], context):
            return False

        if self.awareness_level < comment_data.get("min_awareness", 0):
            return False

        return True

    def _check_trigger(self, trigger: str, context: dict) -> bool:
        checker = self._trigger_checkers.get(trigger)
        return checker(context) if checker else False

    def increase_awareness(self, amount: int = 1):
        self.awareness_level = min(10, self.awareness_level + amount)

    def get_awareness_level(self) -> int:
        return self.awareness_level
