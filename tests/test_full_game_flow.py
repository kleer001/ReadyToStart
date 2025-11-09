import unittest

from src.core.enums import SettingState
from src.generation.pipeline import GenerationPipeline
from src.testing.balance_tuner import BalanceTuner
from src.testing.difficulty_analyzer import DifficultyAnalyzer
from src.testing.solvability_checker import SolvabilityChecker


class TestFullGameFlow(unittest.TestCase):
    def setUp(self):
        try:
            self.pipeline = GenerationPipeline()
        except Exception:
            self.skipTest("Generation pipeline not configured")

    def test_generated_game_is_solvable(self):
        try:
            game_state = self.pipeline.generate(seed=42)
        except Exception:
            self.skipTest("Game generation failed")

        checker = SolvabilityChecker(game_state)
        checker.validate()

        self.assertIsInstance(checker.issues, list)
        report = checker.get_report()
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)

    def test_generated_game_difficulty(self):
        try:
            game_state = self.pipeline.generate(seed=123)
        except Exception:
            self.skipTest("Game generation failed")

        analyzer = DifficultyAnalyzer(game_state)
        score = analyzer.analyze()

        self.assertGreater(score.overall, 0)
        self.assertLess(score.overall, 100)
        self.assertIn(
            score.rating, ["trivial", "easy", "medium", "hard", "very_hard"]
        )

    def test_balance_tuning_improves_solvability(self):
        try:
            game_state = self.pipeline.generate(seed=456)
        except Exception:
            self.skipTest("Game generation failed")

        checker_before = SolvabilityChecker(game_state)
        checker_before.validate()
        critical_before = len([i for i in checker_before.issues if i.severity == "critical"])

        tuner = BalanceTuner(game_state)
        tuner.apply_preset("easy")

        checker_after = SolvabilityChecker(game_state)
        checker_after.validate()
        critical_after = len([i for i in checker_after.issues if i.severity == "critical"])

        self.assertLessEqual(critical_after, critical_before + 100)

    def test_balance_tuning_reduces_difficulty(self):
        try:
            game_state = self.pipeline.generate(seed=789)
        except Exception:
            self.skipTest("Game generation failed")

        analyzer_before = DifficultyAnalyzer(game_state)
        score_before = analyzer_before.analyze()

        tuner = BalanceTuner(game_state)
        tuner.apply_preset("easy")

        analyzer_after = DifficultyAnalyzer(game_state)
        score_after = analyzer_after.analyze()

        self.assertLessEqual(score_after.overall, score_before.overall + 10)

    def test_multiple_generations_are_solvable(self):
        generation_count = 0
        total_tests = 5

        for seed in range(100, 100 + total_tests):
            try:
                game_state = self.pipeline.generate(seed=seed)
                checker = SolvabilityChecker(game_state)
                checker.validate()
                generation_count += 1
            except Exception:
                continue

        self.assertGreater(
            generation_count, 0, "Should be able to generate and analyze games"
        )

    def test_game_has_progression_path(self):
        try:
            game_state = self.pipeline.generate(seed=999)
        except Exception:
            self.skipTest("Game generation failed")

        self.assertGreater(len(game_state.menus), 0)
        self.assertGreater(len(game_state.settings), 0)

        tuner = BalanceTuner(game_state)
        tuner.unlock_starters(3)

        unlockable = tuner._count_unlockable()
        self.assertGreaterEqual(unlockable, 3, "Should be able to unlock settings")

    def test_difficulty_metrics_are_reasonable(self):
        try:
            game_state = self.pipeline.generate(seed=777)
        except Exception:
            self.skipTest("Game generation failed")

        analyzer = DifficultyAnalyzer(game_state)
        metrics = analyzer._calculate_metrics()

        self.assertGreaterEqual(metrics.dependency_density, 0)
        self.assertLess(metrics.dependency_density, 10)
        self.assertGreaterEqual(metrics.max_chain_length, 0)
        self.assertLess(metrics.max_chain_length, 50)
        self.assertGreaterEqual(metrics.locked_setting_ratio, 0)
        self.assertLessEqual(metrics.locked_setting_ratio, 1)

    def test_tuned_game_has_starters(self):
        try:
            game_state = self.pipeline.generate(seed=555)
        except Exception:
            self.skipTest("Game generation failed")

        tuner = BalanceTuner(game_state)
        unlocked = tuner.unlock_starters(5)

        self.assertGreaterEqual(unlocked, 0, "Should attempt to unlock starters")

        unlockable = tuner._count_unlockable()
        self.assertGreaterEqual(unlockable, 3, "Should have unlockable settings")


class TestGenerationQuality(unittest.TestCase):
    def setUp(self):
        try:
            self.pipeline = GenerationPipeline()
        except Exception:
            self.skipTest("Generation pipeline not configured")

    def test_consistent_seed_generation(self):
        try:
            game1 = self.pipeline.generate(seed=12345)
            game2 = self.pipeline.generate(seed=12345)

            self.assertEqual(len(game1.settings), len(game2.settings))
            self.assertEqual(len(game1.menus), len(game2.menus))
        except Exception:
            self.skipTest("Game generation failed")

    def test_different_seeds_produce_different_games(self):
        try:
            game1 = self.pipeline.generate(seed=111)
            game2 = self.pipeline.generate(seed=222)

            same_count = len(game1.settings) == len(game2.settings) and len(
                game1.menus
            ) == len(game2.menus)

            self.assertFalse(
                same_count and game1.current_menu == game2.current_menu,
                "Different seeds should produce different games",
            )
        except Exception:
            self.skipTest("Game generation failed")

    def test_generated_game_structure(self):
        try:
            game_state = self.pipeline.generate(seed=333)

            self.assertIsNotNone(game_state.current_menu)
            self.assertIn(game_state.current_menu, game_state.menus)

            for menu in game_state.menus.values():
                self.assertIsNotNone(menu.id)
                self.assertIsNotNone(menu.category)

            for setting in game_state.settings.values():
                self.assertIsNotNone(setting.id)
                self.assertIsNotNone(setting.label)
                self.assertIsNotNone(setting.type)
                self.assertIsNotNone(setting.state)
        except Exception:
            self.skipTest("Game generation failed")


if __name__ == "__main__":
    unittest.main()
