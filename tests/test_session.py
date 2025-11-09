import json
import tempfile
import time

import pytest

from ready_to_start.core.enums import SettingState, SettingType
from ready_to_start.core.game_state import GameState
from ready_to_start.core.menu import MenuNode
from ready_to_start.core.session import SessionManager, SessionMetrics
from ready_to_start.core.types import Setting


@pytest.fixture
def session_state():
    state = GameState()

    menu = MenuNode(id="menu", category="Test")
    setting = Setting(
        id="s1",
        type=SettingType.BOOLEAN,
        value=False,
        state=SettingState.DISABLED,
        label="S1",
    )
    menu.add_setting(setting)
    state.add_menu(menu)

    return state


def test_session_metrics_creation():
    metrics = SessionMetrics()

    assert metrics.settings_viewed == 0
    assert metrics.settings_modified == 0
    assert metrics.menus_visited == 0
    assert metrics.clicks == 0
    assert metrics.hovers == 0
    assert metrics.start_time > 0


def test_session_metrics_to_dict():
    metrics = SessionMetrics()
    metrics.settings_viewed = 5
    metrics.settings_modified = 3

    data = metrics.to_dict()

    assert data["settings_viewed"] == 5
    assert data["settings_modified"] == 3
    assert "duration" in data


def test_session_manager_creation(session_state):
    manager = SessionManager(session_state)

    assert manager.state is session_state
    assert len(manager.events) == 0


def test_session_record_event(session_state):
    manager = SessionManager(session_state)

    manager.record_event("click", {"button": "left"})

    assert len(manager.events) == 1
    assert manager.events[0]["type"] == "click"
    assert manager.events[0]["data"]["button"] == "left"


def test_session_update_metrics(session_state):
    manager = SessionManager(session_state)

    manager.record_event("setting_viewed")
    manager.record_event("setting_modified")
    manager.record_event("menu_visited")
    manager.record_event("click")
    manager.record_event("hover")

    assert manager.metrics.settings_viewed == 1
    assert manager.metrics.settings_modified == 1
    assert manager.metrics.menus_visited == 1
    assert manager.metrics.clicks == 1
    assert manager.metrics.hovers == 1


def test_session_update_progress(session_state):
    manager = SessionManager(session_state)

    manager.update_progress(75.5)

    assert manager.metrics.progress_percentage == 75.5


def test_session_efficiency_score_zero(session_state):
    manager = SessionManager(session_state)

    score = manager.get_efficiency_score()

    assert score == 0.0


def test_session_efficiency_score_positive(session_state):
    manager = SessionManager(session_state)

    manager.record_event("setting_viewed")
    manager.record_event("setting_modified")

    score = manager.get_efficiency_score()

    assert score > 0.0


def test_session_efficiency_penalties(session_state):
    manager = SessionManager(session_state)

    manager.record_event("setting_viewed")
    manager.record_event("setting_modified")

    score_initial = manager.get_efficiency_score()

    for _ in range(100):
        manager.record_event("click")

    score_after_clicks = manager.get_efficiency_score()

    assert score_after_clicks < score_initial


def test_session_serialize(session_state):
    manager = SessionManager(session_state)

    manager.record_event("click")
    manager.update_progress(50.0)

    data = manager.serialize()

    assert "metrics" in data
    assert "efficiency" in data
    assert "events" in data


def test_session_save_to_file(session_state):
    manager = SessionManager(session_state)

    manager.record_event("click")
    manager.update_progress(50.0)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        filepath = f.name

    manager.save_to_file(filepath)

    with open(filepath) as f:
        data = json.load(f)

    assert "metrics" in data
    assert "efficiency" in data
    assert "events" in data


def test_session_event_limit(session_state):
    manager = SessionManager(session_state)

    for i in range(150):
        manager.record_event("click", {"count": i})

    data = manager.serialize()

    assert len(data["events"]) == 100


def test_session_unknown_event_type(session_state):
    manager = SessionManager(session_state)

    initial_clicks = manager.metrics.clicks

    manager.record_event("unknown_event")

    assert manager.metrics.clicks == initial_clicks
    assert len(manager.events) == 1


def test_session_time_based_efficiency(session_state):
    manager = SessionManager(session_state)

    manager.record_event("setting_viewed")
    manager.record_event("setting_modified")

    score_immediate = manager.get_efficiency_score()

    manager.metrics.start_time = time.time() - 120

    score_after_time = manager.get_efficiency_score()

    assert score_after_time < score_immediate


def test_session_multiple_event_types(session_state):
    manager = SessionManager(session_state)

    manager.record_event("setting_viewed")
    manager.record_event("setting_viewed")
    manager.record_event("setting_modified")
    manager.record_event("menu_visited")

    assert manager.metrics.settings_viewed == 2
    assert manager.metrics.settings_modified == 1
    assert manager.metrics.menus_visited == 1
