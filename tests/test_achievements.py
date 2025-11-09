from pathlib import Path
import tempfile
import json
from src.meta.achievements import Achievement, AchievementSystem


def test_achievement_creation():
    achievement = Achievement(
        id="test",
        name="Test Achievement",
        description="A test",
        condition="time_spent",
        threshold=100,
        secret=False,
        rarity="common",
    )

    assert achievement.id == "test"
    assert achievement.unlocked is False
    assert achievement.rarity == "common"


def test_achievement_system_initialization():
    system = AchievementSystem()
    assert len(system.achievements) == 0
    assert system.unlocked_count == 0


def test_achievement_system_load_achievements():
    system = AchievementSystem()

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "achievements.json"
        data = {
            "achievements": [
                {
                    "id": "first",
                    "name": "First",
                    "description": "First achievement",
                    "condition": "settings_enabled",
                    "threshold": 1,
                    "rarity": "common",
                    "secret": False,
                }
            ]
        }

        with open(filepath, "w") as f:
            json.dump(data, f)

        system.load_achievements(filepath)

        assert len(system.achievements) == 1
        assert "first" in system.achievements


def test_achievement_check_conditions():
    system = AchievementSystem()

    achievement = Achievement(
        id="test",
        name="Test",
        description="Test",
        condition="settings_enabled",
        threshold=10,
        secret=False,
    )
    system.achievements["test"] = achievement

    game_state = {"settings_enabled": 5}
    newly_unlocked = system.check_achievements(game_state)
    assert len(newly_unlocked) == 0

    game_state = {"settings_enabled": 10}
    newly_unlocked = system.check_achievements(game_state)
    assert len(newly_unlocked) == 1
    assert newly_unlocked[0].id == "test"
    assert achievement.unlocked is True


def test_achievement_multiple_conditions():
    system = AchievementSystem()

    achievements_data = [
        ("time", "time_spent", 100),
        ("errors", "errors_made", 50),
        ("layers", "layers_completed", 5),
    ]

    for aid, condition, threshold in achievements_data:
        achievement = Achievement(
            id=aid,
            name=aid,
            description=aid,
            condition=condition,
            threshold=threshold,
            secret=False,
        )
        system.achievements[aid] = achievement

    game_state = {"time_spent": 150, "errors_made": 60, "layers_completed": 5}
    newly_unlocked = system.check_achievements(game_state)

    assert len(newly_unlocked) == 3


def test_achievement_efficiency_conditions():
    system = AchievementSystem()

    high = Achievement(
        id="high",
        name="High",
        description="High",
        condition="efficiency_high",
        threshold=90,
        secret=False,
    )
    low = Achievement(
        id="low",
        name="Low",
        description="Low",
        condition="efficiency_low",
        threshold=10,
        secret=False,
    )

    system.achievements["high"] = high
    system.achievements["low"] = low

    game_state = {"efficiency": 95}
    newly_unlocked = system.check_achievements(game_state)
    assert len(newly_unlocked) == 1
    assert newly_unlocked[0].id == "high"


def test_achievement_get_unlocked():
    system = AchievementSystem()

    for i in range(5):
        achievement = Achievement(
            id=f"test{i}",
            name=f"Test {i}",
            description="Test",
            condition="settings_enabled",
            threshold=i,
            secret=False,
            unlocked=(i < 3),
        )
        system.achievements[f"test{i}"] = achievement

    unlocked = system.get_unlocked_achievements()
    assert len(unlocked) == 3


def test_achievement_get_locked_with_secret():
    system = AchievementSystem()

    for i in range(5):
        achievement = Achievement(
            id=f"test{i}",
            name=f"Test {i}",
            description="Test",
            condition="settings_enabled",
            threshold=i,
            secret=(i == 4),
            unlocked=False,
        )
        system.achievements[f"test{i}"] = achievement

    locked = system.get_locked_achievements(include_secret=False)
    assert len(locked) == 4

    locked_with_secret = system.get_locked_achievements(include_secret=True)
    assert len(locked_with_secret) == 5


def test_achievement_completion_percentage():
    system = AchievementSystem()

    for i in range(10):
        achievement = Achievement(
            id=f"test{i}",
            name=f"Test {i}",
            description="Test",
            condition="settings_enabled",
            threshold=i,
            secret=False,
        )
        system.achievements[f"test{i}"] = achievement

    system.unlocked_count = 5
    percentage = system.get_completion_percentage()
    assert percentage == 50.0


def test_achievement_special_conditions():
    system = AchievementSystem()

    final = Achievement(
        id="final",
        name="Final",
        description="Final",
        condition="reached_final_layer",
        threshold=0,
        secret=False,
    )
    system.achievements["final"] = final

    game_state = {"layer_id": "final_layer"}
    newly_unlocked = system.check_achievements(game_state)
    assert len(newly_unlocked) == 1


def test_achievement_perfect_layer():
    system = AchievementSystem()

    perfect = Achievement(
        id="perfect",
        name="Perfect",
        description="Perfect",
        condition="perfect_layer",
        threshold=0,
        secret=False,
    )
    system.achievements["perfect"] = perfect

    game_state = {"errors_in_layer": 0, "layer_completed": True}
    newly_unlocked = system.check_achievements(game_state)
    assert len(newly_unlocked) == 1

    system.achievements["perfect"].unlocked = False
    game_state = {"errors_in_layer": 1, "layer_completed": True}
    newly_unlocked = system.check_achievements(game_state)
    assert len(newly_unlocked) == 0
