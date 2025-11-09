import tempfile

import pytest

from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.game_state import GameState
from ready_to_start.core.hidden_conditions import HiddenCondition, HiddenConditionTracker
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.types import Setting


@pytest.fixture
def tracker_state():
    state = GameState()

    audio_menu = MenuNode(id="Audio", category="Audio")
    graphics_menu = MenuNode(id="Graphics", category="Graphics")

    volume_setting = Setting(
        id="audio_volume",
        type=SettingType.INTEGER,
        value=50,
        state=SettingState.ENABLED,
        label="Volume",
        min_value=0,
        max_value=100,
    )
    audio_menu.add_setting(volume_setting)

    state.add_menu(audio_menu)
    state.add_menu(graphics_menu)

    return state


def test_tracker_basic(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    condition = HiddenCondition(
        id="test",
        description="Test condition",
        check=lambda state: True,
    )
    tracker.register_condition(condition)

    newly_triggered = tracker.check_all()

    assert "test" in newly_triggered
    assert condition.triggered is True


def test_tracker_not_triggered(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    condition = HiddenCondition(
        id="test",
        description="Test condition",
        check=lambda state: False,
    )
    tracker.register_condition(condition)

    newly_triggered = tracker.check_all()

    assert "test" not in newly_triggered
    assert condition.triggered is False


def test_tracker_counter(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    tracker.increment_counter("clicks")
    tracker.increment_counter("clicks")
    tracker.increment_counter("clicks")

    assert tracker.counters["clicks"] == 3


def test_tracker_counter_condition(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    condition = HiddenCondition(
        id="many_clicks",
        description="Click 5 times",
        check=tracker._parse_check("counter:clicks > 4"),
    )
    tracker.register_condition(condition)

    for _ in range(5):
        tracker.increment_counter("clicks")

    newly_triggered = tracker.check_all()

    assert "many_clicks" in newly_triggered


def test_tracker_setting_condition(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    condition = HiddenCondition(
        id="magic_number",
        description="Set volume to 42",
        check=tracker._parse_check("setting:audio_volume == 42"),
    )
    tracker.register_condition(condition)

    tracker_state.get_setting("audio_volume").value = 42
    newly_triggered = tracker.check_all()

    assert "magic_number" in newly_triggered


def test_tracker_visited_condition(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    condition = HiddenCondition(
        id="explorer",
        description="Visit Audio and Graphics",
        check=tracker._parse_check("visited:Audio,Graphics"),
    )
    tracker.register_condition(condition)

    tracker_state.visited_menus.append("Audio")
    newly_triggered = tracker.check_all()
    assert "explorer" not in newly_triggered

    tracker_state.visited_menus.append("Graphics")
    newly_triggered = tracker.check_all()
    assert "explorer" in newly_triggered


def test_tracker_only_triggers_once(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    condition = HiddenCondition(
        id="test",
        description="Test condition",
        check=lambda state: True,
    )
    tracker.register_condition(condition)

    first_check = tracker.check_all()
    second_check = tracker.check_all()

    assert "test" in first_check
    assert "test" not in second_check


def test_tracker_config_loading(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    config_content = """[test_condition]
description = Test description
check = counter:test_counter > 5
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(config_content)
        config_path = f.name

    tracker.load_from_config(config_path)

    assert "test_condition" in tracker.conditions
    assert tracker.conditions["test_condition"].description == "Test description"


def test_tracker_compare_operators(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    assert tracker._compare(10, ">", 5) is True
    assert tracker._compare(10, "<", 5) is False
    assert tracker._compare(10, "==", 10) is True
    assert tracker._compare(10, "!=", 5) is True
    assert tracker._compare(10, ">=", 10) is True
    assert tracker._compare(10, "<=", 10) is True


def test_tracker_convert_value(tracker_state):
    tracker = HiddenConditionTracker(tracker_state)

    assert tracker._convert_value("42") == 42
    assert tracker._convert_value("42.5") == 42.5
    assert tracker._convert_value("true") is True
    assert tracker._convert_value("false") is False
    assert tracker._convert_value("text") == "text"
