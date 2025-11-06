import pytest

from ready_to_start.core.enums import SettingState
from ready_to_start.ui.indicators import StateIndicator


@pytest.fixture
def config_path():
    return "config/indicators.ini"


def test_state_indicator_get_indicator_enabled(config_path):
    indicator = StateIndicator(config_path)
    result = indicator.get_indicator(SettingState.ENABLED)
    assert "[X]" in result


def test_state_indicator_get_indicator_disabled(config_path):
    indicator = StateIndicator(config_path)
    result = indicator.get_indicator(SettingState.DISABLED)
    assert "[ ]" in result


def test_state_indicator_get_indicator_locked(config_path):
    indicator = StateIndicator(config_path)
    result = indicator.get_indicator(SettingState.LOCKED)
    assert "[~]" in result


def test_state_indicator_get_indicator_hidden(config_path):
    indicator = StateIndicator(config_path)
    result = indicator.get_indicator(SettingState.HIDDEN)
    assert result == ""


def test_state_indicator_reset_animation(config_path):
    indicator = StateIndicator(config_path)
    indicator.frame_counter = 5
    indicator.reset_animation()
    assert indicator.frame_counter == 0
