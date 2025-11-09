import json
from pathlib import Path
from random import choice, randint
from time import sleep


class FourthWallBreaker:
    def __init__(self):
        self.breaks: list[dict] = []
        self.triggered_breaks: set[str] = set()
        self._condition_checkers = self._build_condition_checkers()
        self._action_performers = self._build_action_performers()

    def _build_condition_checkers(self) -> dict[str, callable]:
        return {
            "first_time": lambda c: c.get("is_first", False),
            "frustrated": lambda c: c.get("failed_attempts", 0) > 5,
            "far_in_game": lambda c: c.get("layer_depth", 0) > 3,
        }

    def _build_action_performers(self) -> dict[str, callable]:
        return {
            "cursor_movement": self._perform_cursor_movement,
            "screen_shake": self._perform_screen_shake,
        }

    def load_breaks(self, breaks_file: str | Path):
        with open(breaks_file) as f:
            data = json.load(f)
        self.breaks = data["breaks"]

    def get_break(self, event_type: str, context: dict) -> dict | None:
        eligible = self._find_eligible_breaks(event_type, context)
        if not eligible:
            return None

        selected = choice(eligible)
        if selected.get("show_once", False):
            self.triggered_breaks.add(selected["id"])

        return selected

    def _find_eligible_breaks(self, event_type: str, context: dict) -> list[dict]:
        eligible = []
        for break_data in self.breaks:
            if self._is_break_eligible(break_data, event_type, context):
                eligible.append(break_data)
        return eligible

    def _is_break_eligible(
        self, break_data: dict, event_type: str, context: dict
    ) -> bool:
        if break_data["event"] != event_type:
            return False

        if break_data.get("show_once", False):
            if break_data["id"] in self.triggered_breaks:
                return False

        if "condition" in break_data:
            if not self._check_condition(break_data["condition"], context):
                return False

        return True

    def _check_condition(self, condition: str, context: dict) -> bool:
        checker = self._condition_checkers.get(condition)
        return checker(context) if checker else True

    def display_break(self, break_data: dict):
        print("\n" + "=" * 60)
        print(f"\n{break_data['text']}\n")

        if "action" in break_data:
            self._perform_action(break_data["action"])

        print("=" * 60 + "\n")

        if break_data.get("pause", False):
            input("Press Enter to continue...")

    def _perform_action(self, action: str):
        performer = self._action_performers.get(action)
        if performer:
            performer()

    def _perform_cursor_movement(self):
        for i in range(5):
            print(f"\r{'>' * (i + 1)}", end="", flush=True)
            sleep(0.3)
        print()

    def _perform_screen_shake(self):
        for _ in range(10):
            print("\n" * randint(-2, 2), end="")
            sleep(0.05)
