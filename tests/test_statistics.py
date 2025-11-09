from pathlib import Path
import tempfile
import json
from src.meta.statistics import GameStatistics, StatisticsTracker


def test_game_statistics_initialization():
    stats = GameStatistics()
    assert stats.total_actions == 0
    assert stats.settings_enabled == 0
    assert stats.total_errors == 0
    assert len(stats.secrets_found) == 0


def test_statistics_tracker_record_action():
    tracker = StatisticsTracker()

    tracker.record_action("setting_enabled")
    assert tracker.stats.total_actions == 1
    assert tracker.stats.settings_enabled == 1

    tracker.record_action("navigation")
    assert tracker.stats.total_actions == 2
    assert tracker.stats.navigations == 1


def test_statistics_tracker_record_errors():
    tracker = StatisticsTracker()

    tracker.record_action("error_locked")
    assert tracker.stats.total_errors == 1
    assert tracker.stats.locked_attempts == 1

    tracker.record_action("error_dependency")
    assert tracker.stats.total_errors == 2
    assert tracker.stats.dependency_failures == 1


def test_statistics_tracker_layer_completion():
    tracker = StatisticsTracker()

    layer_stats = {"time_spent": 120.5, "efficiency": 85.0, "errors": 0}
    tracker.record_layer_completion("layer1", layer_stats)

    assert tracker.stats.layers_completed == 1
    assert tracker.stats.time_per_layer["layer1"] == 120.5
    assert tracker.stats.best_efficiency == 85.0
    assert tracker.stats.perfect_layers == 1


def test_statistics_tracker_efficiency_tracking():
    tracker = StatisticsTracker()

    tracker.record_layer_completion("layer1", {"efficiency": 80.0, "errors": 1})
    tracker.record_layer_completion("layer2", {"efficiency": 90.0, "errors": 0})

    assert tracker.stats.best_efficiency == 90.0
    assert tracker.stats.worst_efficiency == 80.0
    assert tracker.stats.average_efficiency == 85.0


def test_statistics_tracker_secret_recording():
    tracker = StatisticsTracker()

    tracker.record_secret_found("secret1")
    tracker.record_secret_found("secret2")
    tracker.record_secret_found("secret1")

    assert len(tracker.stats.secrets_found) == 2
    assert "secret1" in tracker.stats.secrets_found
    assert "secret2" in tracker.stats.secrets_found


def test_statistics_tracker_layer_depth():
    tracker = StatisticsTracker()

    tracker.update_layer_depth(3)
    assert tracker.stats.current_layer_depth == 3
    assert tracker.stats.deepest_layer_reached == 3

    tracker.update_layer_depth(2)
    assert tracker.stats.current_layer_depth == 2
    assert tracker.stats.deepest_layer_reached == 3


def test_statistics_save_and_load():
    tracker = StatisticsTracker()
    tracker.record_action("setting_enabled")
    tracker.record_secret_found("secret1")

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "stats.json"
        tracker.save_to_file(filepath)

        assert filepath.exists()

        new_tracker = StatisticsTracker()
        new_tracker.load_from_file(filepath)

        assert new_tracker.stats.settings_enabled == 1
        assert "secret1" in new_tracker.stats.secrets_found


def test_game_statistics_get_summary():
    stats = GameStatistics()
    stats.total_actions = 100
    stats.settings_enabled = 50
    stats.total_errors = 10
    stats.layers_completed = 3

    summary = stats.get_summary()

    assert "Actions Taken" in summary
    assert summary["Actions Taken"] == 100
    assert summary["Settings Enabled"] == 50
    assert summary["Errors Made"] == 10


def test_game_statistics_serialize():
    stats = GameStatistics()
    stats.total_actions = 100
    stats.settings_enabled = 50
    stats.secrets_found = ["secret1", "secret2"]

    serialized = stats.serialize()

    assert serialized["total_actions"] == 100
    assert serialized["settings_enabled"] == 50
    assert len(serialized["secrets_found"]) == 2
