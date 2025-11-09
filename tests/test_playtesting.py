import tempfile
import time
import unittest
from pathlib import Path

from src.testing.playtest_session import PlaytestTracker


class TestPlaytestTracker(unittest.TestCase):
    def test_initialization(self):
        tracker = PlaytestTracker(seed=12345)

        self.assertEqual(tracker.metrics.seed, 12345)
        self.assertIsNotNone(tracker.metrics.session_id)
        self.assertIsNone(tracker.metrics.end_time)
        self.assertFalse(tracker.metrics.completed)

    def test_record_setting_interaction(self):
        tracker = PlaytestTracker()
        tracker.record_setting_interaction("s1", "enable", True, True)

        self.assertEqual(len(tracker.metrics.setting_interactions), 1)
        interaction = tracker.metrics.setting_interactions[0]
        self.assertEqual(interaction.setting_id, "s1")
        self.assertEqual(interaction.action, "enable")
        self.assertEqual(interaction.value, True)
        self.assertTrue(interaction.success)

    def test_record_menu_visit(self):
        tracker = PlaytestTracker()

        tracker.record_menu_visit("menu1")
        time.sleep(0.1)
        tracker.record_menu_visit("menu2")

        self.assertEqual(len(tracker.metrics.menu_visits), 1)
        visit = tracker.metrics.menu_visits[0]
        self.assertEqual(visit.menu_id, "menu1")
        self.assertGreater(visit.duration, 0)

    def test_record_error(self):
        tracker = PlaytestTracker()
        tracker.record_error("Test error message")

        self.assertEqual(len(tracker.metrics.errors), 1)
        self.assertEqual(tracker.metrics.errors[0], "Test error message")

    def test_complete_session(self):
        tracker = PlaytestTracker()
        tracker.record_menu_visit("menu1")
        time.sleep(0.1)
        tracker.complete_session(completed=True)

        self.assertIsNotNone(tracker.metrics.end_time)
        self.assertTrue(tracker.metrics.completed)
        self.assertGreater(tracker.metrics.duration, 0)

    def test_save_and_load(self):
        tracker = PlaytestTracker(seed=42)
        tracker.record_setting_interaction("s1", "enable", True, True)
        tracker.record_menu_visit("menu1")
        tracker.record_error("Test error")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_session.json"
            tracker.save(filepath)

            loaded = PlaytestTracker.load(filepath)

            self.assertEqual(loaded.metrics.seed, tracker.metrics.seed)
            self.assertEqual(
                len(loaded.metrics.setting_interactions),
                len(tracker.metrics.setting_interactions),
            )
            self.assertEqual(len(loaded.metrics.errors), len(tracker.metrics.errors))

    def test_metrics_properties(self):
        tracker = PlaytestTracker()

        tracker.record_setting_interaction("s1", "enable", True, True)
        tracker.record_setting_interaction("s2", "enable", True, False)
        tracker.record_setting_interaction("s1", "update", 42, True)

        self.assertEqual(tracker.metrics.total_interactions, 3)
        self.assertEqual(tracker.metrics.failed_interactions, 1)
        self.assertEqual(tracker.metrics.unique_settings_touched, 2)

    def test_problem_settings_identification(self):
        tracker = PlaytestTracker()

        tracker.record_setting_interaction("s1", "enable", True, False)
        tracker.record_setting_interaction("s1", "enable", True, False)
        tracker.record_setting_interaction("s2", "enable", True, False)

        problems = tracker.metrics.get_problem_settings()

        self.assertEqual(len(problems), 2)
        self.assertEqual(problems[0][0], "s1")
        self.assertEqual(problems[0][1], 2)

    def test_problem_menus_identification(self):
        tracker = PlaytestTracker()

        tracker.record_menu_visit("menu1")
        time.sleep(0.15)
        tracker.record_menu_visit("menu2")
        time.sleep(0.05)
        tracker.complete_session()

        problems = tracker.metrics.get_problem_menus()

        self.assertEqual(len(problems), 2)
        self.assertGreater(problems[0][1], problems[1][1])

    def test_get_summary_format(self):
        tracker = PlaytestTracker(seed=123)
        tracker.record_setting_interaction("s1", "enable", True, True)
        tracker.record_menu_visit("menu1")
        tracker.complete_session(completed=True)

        summary = tracker.get_summary()

        self.assertIn("Playtest Session Summary", summary)
        self.assertIn("Session ID:", summary)
        self.assertIn("Seed: 123", summary)
        self.assertIn("Completed: True", summary)

    def test_stuck_detection(self):
        tracker = PlaytestTracker()
        tracker.STUCK_THRESHOLD = 0.1

        time.sleep(0.15)
        is_stuck = tracker.check_stuck()

        self.assertTrue(is_stuck)
        self.assertEqual(len(tracker.metrics.stuck_events), 1)

    def test_stuck_metrics(self):
        tracker = PlaytestTracker()
        tracker.metrics.stuck_events.append({"timestamp": time.time(), "duration": 30.0})
        tracker.metrics.stuck_events.append({"timestamp": time.time(), "duration": 45.0})

        self.assertEqual(tracker.metrics.total_stuck_time, 75.0)
        self.assertEqual(tracker.metrics.avg_stuck_time, 37.5)

    def test_unique_menus_visited(self):
        tracker = PlaytestTracker()

        tracker.record_menu_visit("menu1")
        tracker.record_menu_visit("menu2")
        tracker.record_menu_visit("menu1")
        tracker.complete_session()

        self.assertEqual(tracker.metrics.unique_menus_visited, 2)


if __name__ == "__main__":
    unittest.main()
