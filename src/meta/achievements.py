import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    condition: str
    threshold: float
    secret: bool
    rarity: str = "common"
    unlocked: bool = False
    unlock_time: float = 0.0


class AchievementSystem:
    def __init__(self):
        self.achievements: dict[str, Achievement] = {}
        self.unlocked_count = 0
        self._condition_checkers = self._build_condition_checkers()

    def _build_condition_checkers(self) -> dict[str, callable]:
        return {
            "time_spent": lambda a, s: (
                s.get("time_spent", s.get("total_time", 0)) >= a.threshold
            ),
            "settings_enabled": lambda a, s: (
                s.get("settings_enabled", 0) >= a.threshold
            ),
            "layers_completed": lambda a, s: (
                s.get("layers_completed", 0) >= a.threshold
            ),
            "errors_made": lambda a, s: (
                s.get("errors_made", s.get("total_errors", 0)) >= a.threshold
            ),
            "efficiency_high": lambda a, s: s.get("efficiency", 0) >= a.threshold,
            "efficiency_low": lambda a, s: s.get("efficiency", 0) <= a.threshold,
            "secrets_found": lambda a, s: (s.get("secrets_found", 0) >= a.threshold),
            "quit_attempts": lambda a, s: s.get("quit_attempts", 0) >= a.threshold,
            "help_views": lambda a, s: s.get("help_views", 0) >= a.threshold,
            "reached_final_layer": lambda a, s: s.get("layer_id") == "final_layer",
            "found_quantum_layer": lambda a, s: (
                s.get("layer_id") == "quantum_interface"
            ),
            "perfect_layer": lambda a, s: (
                s.get("errors_in_layer", 0) == 0 and s.get("layer_completed", False)
            ),
            "perfect_all_layers": lambda a, s: (
                s.get("perfect_layers", 0) == s.get("layers_completed", 0)
                and s.get("layers_completed", 0) > 0
            ),
        }

    def load_achievements(self, achievements_file: str | Path):
        with open(achievements_file) as f:
            data = json.load(f)

        for ach_data in data["achievements"]:
            achievement = Achievement(
                id=ach_data["id"],
                name=ach_data["name"],
                description=ach_data["description"],
                condition=ach_data["condition"],
                threshold=ach_data.get("threshold", 0),
                secret=ach_data.get("secret", False),
                rarity=ach_data.get("rarity", "common"),
            )
            self.achievements[achievement.id] = achievement

    def check_achievements(self, game_state: dict) -> list[Achievement]:
        newly_unlocked = []

        for achievement in self.achievements.values():
            if not achievement.unlocked and self._check_condition(
                achievement, game_state
            ):
                achievement.unlocked = True
                achievement.unlock_time = game_state.get("time", 0)
                self.unlocked_count += 1
                newly_unlocked.append(achievement)

        return newly_unlocked

    def _check_condition(self, achievement: Achievement, game_state: dict) -> bool:
        checker = self._condition_checkers.get(achievement.condition)
        return checker(achievement, game_state) if checker else False

    def get_unlocked_achievements(self) -> list[Achievement]:
        return [a for a in self.achievements.values() if a.unlocked]

    def get_locked_achievements(
        self, include_secret: bool = False
    ) -> list[Achievement]:
        locked = [a for a in self.achievements.values() if not a.unlocked]
        if not include_secret:
            locked = [a for a in locked if not a.secret]
        return locked

    def get_completion_percentage(self) -> float:
        if not self.achievements:
            return 0.0
        return (self.unlocked_count / len(self.achievements)) * 100

    def display_achievement_unlock(self, achievement: Achievement):
        rarity_symbols = {
            "common": "★",
            "uncommon": "★★",
            "rare": "★★★",
            "legendary": "★★★★",
        }
        symbol = rarity_symbols.get(achievement.rarity, "★")

        lines = [
            "╔" + "═" * 58 + "╗",
            "║" + " " * 58 + "║",
            "║" + f"  🏆 ACHIEVEMENT UNLOCKED! {symbol}".ljust(58) + "║",
            "║" + " " * 58 + "║",
            "║" + f"  {achievement.name}".ljust(58) + "║",
            "║" + f"  {achievement.description}".ljust(58) + "║",
            "║" + " " * 58 + "║",
            "╚" + "═" * 58 + "╝",
        ]

        print("\n" + "\n".join(lines) + "\n")
        input("Press Enter to continue...")
