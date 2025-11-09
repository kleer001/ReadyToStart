from src.meta.achievements import AchievementSystem
from src.meta.statistics import GameStatistics


class EndGameSummary:
    def __init__(self, stats: GameStatistics, achievements: AchievementSystem):
        self.stats = stats
        self.achievements = achievements

    def generate_summary(self) -> str:
        lines = []
        lines.extend(self._generate_header())
        lines.extend(self._generate_statistics_section())
        lines.extend(self._generate_achievements_section())
        lines.extend(self._generate_commentary_section())
        lines.extend(self._generate_footer())
        return "\n".join(lines)

    def _generate_header(self) -> list[str]:
        return [
            "=" * 80,
            "",
            "CONGRATULATIONS (?)".center(80),
            "",
            "You finished Ready to Start.".center(80),
            "A game about settings menus.".center(80),
            "That you actually completed.".center(80),
            "",
            "=" * 80,
            "",
        ]

    def _generate_statistics_section(self) -> list[str]:
        lines = ["YOUR STATISTICS:", ""]
        for key, value in self.stats.get_summary().items():
            lines.append(f"  {key:30s} {value}")
        lines.extend(["", "─" * 80, ""])
        return lines

    def _generate_achievements_section(self) -> list[str]:
        lines = ["ACHIEVEMENTS:", ""]
        unlocked = self.achievements.get_unlocked_achievements()
        total = len(self.achievements.achievements)
        completion = self.achievements.get_completion_percentage()
        lines.append(f"  Unlocked: {len(unlocked)}/{total} ({completion:.1f}%)")
        lines.append("")

        for achievement in unlocked[-5:]:
            stars = "★" * (
                ["common", "uncommon", "rare", "legendary"].index(achievement.rarity)
                + 1
            )
            lines.append(f"  {stars} {achievement.name}")

        lines.extend(["", "─" * 80, ""])
        return lines

    def _generate_commentary_section(self) -> list[str]:
        comments = self._get_personalized_commentary()
        return ["\n".join(f"  • {c}" for c in comments), ""]

    def _generate_footer(self) -> list[str]:
        return [
            "=" * 80,
            "",
            "Thanks for playing (?).".center(80),
            "",
            "=" * 80,
        ]

    def _get_personalized_commentary(self) -> list[str]:
        comments = []
        total_time = self.stats.get_total_time()

        comments.extend(self._get_time_comments(total_time))
        comments.extend(self._get_error_comments())
        comments.extend(self._get_efficiency_comments())
        comments.extend(self._get_secret_comments())
        comments.extend(self._get_quit_comments())
        comments.extend(self._get_layer_comments())

        return comments

    def _get_time_comments(self, total_time: float) -> list[str]:
        if total_time > 7200:
            return [
                "You spent over 2 hours on this. "
                "I'm not sure whether to be impressed or concerned."
            ]
        elif total_time < 600:
            return [
                "You speedran through settings menus. "
                "That's... actually kind of impressive."
            ]
        return []

    def _get_error_comments(self) -> list[str]:
        if self.stats.total_errors == 0:
            return [
                "Zero errors. You're either very skilled or very lucky. "
                "Or you're a robot."
            ]
        elif self.stats.total_errors > 100:
            return [
                "Over 100 errors. But you persisted. "
                "That's dedication, or stubbornness, or both."
            ]
        return []

    def _get_efficiency_comments(self) -> list[str]:
        if self.stats.average_efficiency > 90:
            return [
                "Your efficiency rating is suspiciously high. "
                "Are you sure you're human?"
            ]
        elif self.stats.average_efficiency < 20:
            return [
                "Your efficiency rating is abysmal. "
                "But you made it anyway. Respect."
            ]
        return []

    def _get_secret_comments(self) -> list[str]:
        secret_count = len(self.stats.secrets_found)
        if secret_count > 5:
            return [
                "You found a bunch of secrets. "
                "Your reward is... satisfaction? Sorry."
            ]
        elif secret_count == 0:
            return [
                "You found zero secrets. "
                "Probably for the best, they weren't that great anyway."
            ]
        return []

    def _get_quit_comments(self) -> list[str]:
        if self.stats.quit_attempts > 10:
            return [
                "You tried to quit over 10 times. But here you are. "
                "What does that say about you?"
            ]
        return []

    def _get_layer_comments(self) -> list[str]:
        if self.stats.layers_completed >= 15:
            return [
                "You went through EVERY layer. Every single one. "
                "I admire the commitment to the bit."
            ]
        return []

    def display(self):
        summary = self.generate_summary()
        print("\n" + summary + "\n")
        input("Press Enter to exit...")
