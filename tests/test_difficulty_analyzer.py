import unittest

from src.core.dependencies import SimpleDependency
from src.core.enums import SettingState, SettingType
from src.core.game_state import GameState
from src.core.menu import MenuNode
from src.core.types import Setting
from src.testing.difficulty_analyzer import DifficultyAnalyzer


class TestDifficultyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()

    def test_empty_game_difficulty(self):
        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        self.assertEqual(score.overall, 0)
        self.assertEqual(score.rating, "trivial")

    def test_simple_game_difficulty(self):
        menu = MenuNode(id="menu1", category="test")
        s1 = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=True,
            state=SettingState.ENABLED,
            label="S1",
        )
        s2 = Setting(
            id="s2",
            type=SettingType.BOOLEAN,
            value=False,
            state=SettingState.LOCKED,
            label="S2",
        )
        menu.add_setting(s1)
        menu.add_setting(s2)
        self.game_state.add_menu(menu)

        self.game_state.resolver.add_dependency(
            "s2", SimpleDependency("s1", SettingState.ENABLED)
        )

        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        self.assertGreater(score.overall, 0)
        self.assertIn(score.rating, ["trivial", "easy", "medium"])

    def test_high_density_increases_difficulty(self):
        menu = MenuNode(id="menu1", category="test")
        settings = []
        for i in range(10):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i == 0),
                state=SettingState.ENABLED if i == 0 else SettingState.LOCKED,
                label=f"S{i}",
            )
            settings.append(s)
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        for i in range(1, 10):
            for j in range(max(0, i - 3), i):
                self.game_state.resolver.add_dependency(
                    f"s{i}", SimpleDependency(f"s{j}", SettingState.ENABLED)
                )

        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        self.assertGreater(score.metrics.dependency_density, 2.0)
        self.assertGreater(score.overall, 40)

    def test_long_chains_increase_difficulty(self):
        menu = MenuNode(id="menu1", category="test")
        settings = []
        for i in range(8):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i == 0),
                state=SettingState.ENABLED if i == 0 else SettingState.LOCKED,
                label=f"S{i}",
            )
            settings.append(s)
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        for i in range(1, 8):
            self.game_state.resolver.add_dependency(
                f"s{i}", SimpleDependency(f"s{i-1}", SettingState.ENABLED)
            )

        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        self.assertEqual(score.metrics.max_chain_length, 7)
        self.assertGreater(score.overall, 30)

    def test_locked_ratio_affects_difficulty(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(10):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=False,
                state=SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        self.assertEqual(score.metrics.locked_setting_ratio, 1.0)
        self.assertGreater(score.overall, 15)

    def test_difficulty_rating_thresholds(self):
        analyzer = DifficultyAnalyzer(self.game_state)

        self.assertEqual(analyzer._determine_rating(0), "trivial")
        self.assertEqual(analyzer._determine_rating(15), "trivial")
        self.assertEqual(analyzer._determine_rating(25), "easy")
        self.assertEqual(analyzer._determine_rating(45), "medium")
        self.assertEqual(analyzer._determine_rating(65), "hard")
        self.assertEqual(analyzer._determine_rating(85), "very_hard")

    def test_suggestions_for_high_density(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(6):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i == 0),
                state=SettingState.ENABLED if i == 0 else SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        for i in range(1, 6):
            for j in range(i):
                self.game_state.resolver.add_dependency(
                    f"s{i}", SimpleDependency(f"s{j}", SettingState.ENABLED)
                )

        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        self.assertTrue(
            any("density" in s.lower() for s in score.suggestions),
            "Should suggest reducing density",
        )

    def test_suggestions_for_long_chains(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(10):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i == 0),
                state=SettingState.ENABLED if i == 0 else SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        for i in range(1, 10):
            self.game_state.resolver.add_dependency(
                f"s{i}", SimpleDependency(f"s{i-1}", SettingState.ENABLED)
            )

        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        self.assertTrue(
            any("chain" in s.lower() for s in score.suggestions),
            "Should suggest reducing chain length",
        )

    def test_get_report_format(self):
        menu = MenuNode(id="menu1", category="test")
        s = Setting(
            id="s1",
            type=SettingType.BOOLEAN,
            value=True,
            state=SettingState.ENABLED,
            label="S1",
        )
        menu.add_setting(s)
        self.game_state.add_menu(menu)

        analyzer = DifficultyAnalyzer(self.game_state)
        report = analyzer.get_report()

        self.assertIn("Difficulty Analysis", report)
        self.assertIn("Overall Score", report)
        self.assertIn("Metrics:", report)

    def test_branching_factor_calculation(self):
        menu = MenuNode(id="menu1", category="test")
        for i in range(6):
            s = Setting(
                id=f"s{i}",
                type=SettingType.BOOLEAN,
                value=(i == 0),
                state=SettingState.ENABLED if i == 0 else SettingState.LOCKED,
                label=f"S{i}",
            )
            menu.add_setting(s)

        self.game_state.add_menu(menu)

        self.game_state.resolver.add_dependency(
            "s1", SimpleDependency("s0", SettingState.ENABLED)
        )
        self.game_state.resolver.add_dependency(
            "s2", SimpleDependency("s0", SettingState.ENABLED)
        )
        self.game_state.resolver.add_dependency(
            "s3", SimpleDependency("s0", SettingState.ENABLED)
        )

        analyzer = DifficultyAnalyzer(self.game_state)
        score = analyzer.analyze()

        self.assertGreater(score.metrics.branching_factor, 0)


if __name__ == "__main__":
    unittest.main()
